# L7. Workflow

L7 переводит `Service Request` с ручного Select Status на управляемый Workflow.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

## Результат

```text
New
 │ Accept / Facility Supervisor
 ▼
Accepted
 │ Start Work / Facility Technician
 ▼
In Progress
 │ Resolve / Facility Technician
 ▼
Resolved
 │ Close / Facility Supervisor
 ▼
Closed
```

Поле состояния остаётся одно:

```text
Service Request.status
```

Второй `workflow_state` не создаём.

Все состояния:

```text
docstatus = 0
```

`Service Request` остаётся обычным, не Submittable Document.

---

# 1. Главная академическая граница

В L7 нужно различать три разных слоя.

```text
Role Permission
= серверное право работать с DocType/Document

Workflow Allowed Role + Condition
= серверное право выполнить конкретный state transition

Only Allow Edit For
= state-dependent поведение стандартного Desk UI
```

`Only Allow Edit For` **не считаем самостоятельной security boundary**.

В `v16.32.0` server-side `validate_workflow()` надёжно проверяет допустимость смены Workflow State, но не следует преподавать `Only Allow Edit For` как универсальный запрет любого возможного изменения полей через любой API/path.

Это важный инвариант всего курса.

---

# 2. Проверить состояние после L6

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно получить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

Должны существовать роли и основные пользователи L5.

Основной Technician не имеет постоянного Location User Permission.

Kanban L6:

```text
Service Request Status Board
```

пока существует для сравнения.

---

# 3. Ещё раз доказать проблему обычного Select

До Workflow открыть тестовую заявку и вручную выполнить:

```text
New → Closed
```

Сохранить и вернуть логичное состояние.

Фиксируем:

```text
Select
= набор допустимых значений

Select
≠ допустимые переходы
```

---

# 4. Использовать существующий Status

`Service Request.status` уже содержит:

```text
New
Accepted
In Progress
Resolved
Closed
```

Используем:

```text
Workflow State Field = status
```

В `v16.32.0` Frappe создаёт скрытый Custom Field для workflow state только если указанного поля нет.

У нас оно есть, поэтому не создаём:

```text
workflow_state
request_state
workflow_status
```

---

# 5. Сделать Status Read Only

Для:

```text
Status
fieldname: status
```

включить:

```text
Read Only = Yes
```

Оставить:

```text
Default = New
```

и прежние Options.

`Read Only` здесь нужен как UI guard: обычный пользователь не должен видеть `status` как свободный Select после включения Workflow.

Server-side допустимость state change обеспечивает Workflow validation.

Проверить diff:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

---

# 6. Создать Workflow State

Создать:

```text
New
Accepted
In Progress
Resolved
Closed
```

Названия точно совпадают со значениями `Service Request.status`.

---

# 7. Создать Workflow Action Master

Создать:

```text
Accept
Start Work
Resolve
Close
```

Почему `Accept`, а не `Mark Assigned`:

```text
Accept
= Supervisor принимает заявку в процесс

Assign To
= конкретному User создаётся ToDo
```

Workflow и Assignment остаются ортогональны.

---

# 8. Создать Workflow

```text
Workflow Name:        Service Request Workflow
Document Type:        Service Request
Workflow State Field: status
Is Active:            No
```

Дополнительные email/tasks пока не включать.

---

# 9. Document States

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| New | 0 | Facility Requester |
| Accepted | 0 | Facility Technician |
| In Progress | 0 | Facility Technician |
| Resolved | 0 | Facility Supervisor |
| Closed | 0 | Facility Supervisor |

У всех:

```text
Doc Status = 0
```

Не использовать Submitted/Cancelled.

## Как правильно читать Only Allow Edit For

Например:

```text
Accepted → Facility Technician
```

означает, что стандартный Desk делает этот state рабочим для Technician.

Но server-side security всё равно начинается с Role Permission.

Не делать вывод:

```text
Only Allow Edit For
= отдельная ACL, которая физически запрещает любое изменение через API
```

Это было бы академически неверно для `v16.32.0`.

---

# 10. Transitions

| State | Action | Next State | Allowed |
|---|---|---|---|
| New | Accept | Accepted | Facility Supervisor |
| Accepted | Start Work | In Progress | Facility Technician |
| In Progress | Resolve | Resolved | Facility Technician |
| Resolved | Close | Closed | Facility Supervisor |

Conditions оставить пустыми в финальной базовой конфигурации.

`Allow Self Approval` оставить со штатным значением.

---

# 11. Почему Workflow не проверяет assignee

Не добавляем скрытую бизнес-гарантию:

```text
Start Work может только User из ToDo
```

Базовая архитектура Frappe разделяет:

```text
Facility Technician role
→ полномочие роли на transition

ToDo
→ ответственность конкретного User
```

Assignment не является permission predicate.

Если продукту понадобится hard rule:

```text
transition выполняет только конкретный assignee
```

это уже отдельная server-side validation/permission архитектура следующего уровня, а не честный no-code invariant.

---

# 12. Активировать Workflow

Проверить:

```text
Document Type = Service Request
Workflow State Field = status
States = New / Accepted / In Progress / Resolved / Closed
```

Включить:

```text
Is Active = Yes
```

Сохранить и очистить cache:

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost clear-cache
```

---

# 13. Проверить существующие заявки

Открыть записи L4–L6.

Все должны иметь допустимые state values.

Если старый стенд до архитектурной правки содержит:

```text
Assigned
```

до активации финального Workflow вручную перевести такие учебные записи в:

```text
Accepted
```

Не добавлять `Assigned` обратно в новый Workflow ради старых тестовых данных.

---

# 14. Создать новую заявку под Requester

```text
Subject:     Workflow test request
Location:    Room 102
Description: Проверка управляемого процесса
Priority:    Medium
```

Сохранить.

Получить:

```text
Status = New
```

Requester не должен видеть действие:

```text
Accept
```

потому что transition Allowed = Facility Supervisor.

---

# 15. Назначить ответственность отдельно

Под Supervisor сначала:

```text
Assign To
→ technician.one@example.com
```

Проверить ToDo.

После Assign To всё ещё допустимо:

```text
Assigned To = technician.one@example.com
Status = New
```

Это намеренно.

---

# 16. Supervisor принимает заявку

Выполнить:

```text
Accept
```

Получить:

```text
Status = Accepted
```

Важно:

```text
Accepted
= состояние процесса

не

доказательство существования ToDo
```

Мы соблюдаем рекомендуемый порядок `Assign To → Accept`, но не выдаём его за hard coupling платформы.

---

# 17. Technician выполняет процесс

Под:

```text
technician.one@example.com
```

выполнить:

```text
Start Work
```

Получить:

```text
Status = In Progress
```

Затем:

```text
Resolve
```

Получить:

```text
Status = Resolved
```

Technician не должен иметь Workflow Action `Close`.

---

# 18. Supervisor закрывает

Под Supervisor:

```text
Close
```

Получить:

```text
Status = Closed
```

У `Closed` нет исходящего transition.

## Точная семантика Closed

```text
Closed
= terminal Workflow state
```

Это не означает:

```text
Document физически неизменяем любым пользователем через любой API
```

Track Changes остаётся аудитом допустимых исправлений.

Hard immutability потребовала бы отдельной server-side validation policy, которая находится за границей базового курса.

---

# 19. Запрещённые переходы

Проверить:

```text
Requester / New
→ Accept недоступен

Technician / Accepted
→ Start Work доступен
→ Resolve напрямую недоступен

Supervisor / Resolved
→ Close доступен
→ перехода назад в New нет
```

Server-side transition model:

```text
Current State
+
Allowed Role
+
Condition
=
допустимый transition
```

---

# 20. Временная Condition

У перехода:

```text
New → Accept → Accepted
```

временно задать:

```python
doc.priority == "High"
```

Проверить:

```text
High   → Accept доступен
Medium → Accept недоступен
```

После теста **обязательно удалить Condition**.

Почему не оставляем её:

```text
Priority не должна случайно превращаться
в permanent gate принятия любой заявки
```

Condition изучается как штатный server-side transition predicate, а не как повод усложнить модель.

---

# 21. Kanban после Workflow

Доска L6:

```text
Service Request Status Board
```

после появления Workflow больше не является основным интерфейсом переходов.

В `v16.32.0` Kanban field update приходит к обычному save, а Workflow validation проверяет допустимость state change.

Но:

```text
Kanban move
≠ Workflow Action lifecycle
```

Поэтому после проверки удалить Kanban Board.

Основной процесс управляется:

```text
Workflow Actions
```

---

# 22. Timeline и Workflow Action

На заявке полного маршрута сравнить:

```text
Assignment
Comment
Version/field change
Workflow comment/action
```

Не создавать собственный Workflow History.

---

# 23. Что является hard, а что UI guard

После L7 ученик должен уметь классифицировать:

| Механизм | Роль |
|---|---|
| Role Permission | server access boundary |
| Allowed Role transition | server transition boundary |
| Workflow Condition | server transition predicate |
| Status Read Only | UI guard |
| Only Allow Edit For | state-dependent Desk editability |
| Track Changes | audit, не запрет |

Это один из главных академических результатов L7.

---

# 24. Metadata и configuration

## App metadata

```text
Service Request.status
→ Read Only
```

## Site configuration до L11

```text
Workflow State
Workflow Action Master
Workflow
```

Имена финальной конфигурации:

```text
States:
New
Accepted
In Progress
Resolved
Closed

Actions:
Accept
Start Work
Resolve
Close
```

---

# 25. Commit metadata

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff

git add \
  facility_ops/facility_operations/doctype/service_request/service_request.json

git diff --cached
git commit -m "Make service request status workflow controlled"
git status
```

Workflow records вручную в source не копировать; их переносимость разбирается в L11.

---

# 26. Приёмка L7

L7 принят, если:

- `status` — единственный Workflow State Field;
- `status` Read Only в Desk;
- существуют состояния `New / Accepted / In Progress / Resolved / Closed`;
- существуют действия `Accept / Start Work / Resolve / Close`;
- активен `Service Request Workflow`;
- Allowed Role реально ограничивает transitions;
- временная Condition проверена и удалена;
- ученик не называет `Only Allow Edit For` полноценной ACL;
- `Accepted` не трактуется как наличие конкретного assignee;
- Assignment остаётся отдельным ToDo-механизмом;
- `Closed` понимается как terminal workflow state, а не обещание абсолютной immutability;
- Kanban удалён после сравнения;
- metadata закоммичена.

После L7 переходим к **L8 — контроль работы и Workspace**.