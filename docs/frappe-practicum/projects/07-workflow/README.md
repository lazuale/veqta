# L7. Workflow

L7 переводит `Service Request` с ручного `Status` на управляемый Workflow.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

## Результат

```text
New
 │ Mark Assigned / Facility Supervisor
 ▼
Assigned
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

Никакого второго `workflow_state` не создаём.

Все состояния имеют:

```text
docstatus = 0
```

`Service Request` остаётся обычным, не Submittable Document.

---

# 1. Проверить состояние после L6

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

Должны существовать:

```text
Facility Requester
Facility Technician
Facility Supervisor

requester.one@example.com
technician.one@example.com
supervisor.one@example.com
```

После очистки L5 у `technician.one@example.com` нет постоянного User Permission по Location. Поэтому Workflow проверяем на обычных заявках, не подстраивая сценарий под `Room 101`.

---

# 2. Ещё раз увидеть проблему обычного Select

До Workflow открыть тестовую заявку под пользователем с Write.

Временно изменить:

```text
New → Closed
```

Сохранить и вернуть нормальное состояние.

До Workflow:

```text
Select
= допустимые значения

Select
≠ допустимые переходы
```

---

# 3. Использовать существующий Status как Workflow State Field

В `Service Request` уже есть:

```text
status
```

со значениями:

```text
New
Assigned
In Progress
Resolved
Closed
```

Используем:

```text
Workflow State Field = status
```

В `v16.32.0` Frappe создаёт скрытый Custom Field только если указанного state field в DocType нет. У нас поле уже есть, поэтому не создаём:

```text
workflow_state
request_state
workflow_status
```

---

# 4. Сделать Status Read Only

Открыть Standard DocType `Service Request`.

Для поля:

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

Проверить diff:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

Это единственное Standard metadata-изменение L7.

---

# 5. Создать Workflow State

Через `Workflow State` создать:

```text
New
Assigned
In Progress
Resolved
Closed
```

Названия должны точно совпадать со значениями `Service Request.status`.

---

# 6. Создать Workflow Action Master

Создать:

```text
Mark Assigned
Start Work
Resolve
Close
```

Различать:

```text
Assign To
→ кто выполняет работу

Mark Assigned
→ перевод состояния New → Assigned
```

Workflow не заменяет Assignment.

---

# 7. Создать Workflow

Создать:

```text
Workflow Name:        Service Request Workflow
Document Type:        Service Request
Workflow State Field: status
Is Active:            No
```

Пока оставить выключенными дополнительные email/action-confirmation настройки.

---

# 8. Настроить Document States

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| New | 0 | Facility Requester |
| Assigned | 0 | Facility Technician |
| In Progress | 0 | Facility Technician |
| Resolved | 0 | Facility Supervisor |
| Closed | 0 | Facility Supervisor |

У всех:

```text
Doc Status = 0
```

Не использовать Submitted/Cancelled здесь.

`Only Allow Edit For` дополняет Role Permission Manager, а не заменяет его.

---

# 9. Настроить Transitions

| State | Action | Next State | Allowed |
|---|---|---|---|
| New | Mark Assigned | Assigned | Facility Supervisor |
| Assigned | Start Work | In Progress | Facility Technician |
| In Progress | Resolve | Resolved | Facility Technician |
| Resolved | Close | Closed | Facility Supervisor |

Conditions оставить пустыми.

`Allow Self Approval` оставить со штатным значением. Отдельную модель самоутверждения в базовом уроке не строим.

---

# 10. Активировать Workflow

Проверить:

```text
Document Type = Service Request
Workflow State Field = status
```

States и Transitions должны соответствовать таблицам выше.

Затем:

```text
Is Active = Yes
```

Сохранить.

Очистить cache:

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost clear-cache
```

---

# 11. Проверить существующие заявки

Открыть несколько Service Request из L4–L6.

Их `status` уже содержит допустимые значения Workflow State. Отдельное поле или миграция не нужны.

Если встречается тестовая запись с неправильным значением, исправить данные, а не расширять Workflow ради ошибки.

---

# 12. Создать новую заявку под Requester

Войти:

```text
requester.one@example.com
```

Создать:

```text
Subject:     Workflow test request
Location:    Room 102
Description: Проверка управляемого процесса
Priority:    Medium
```

Сохранить.

Проверить:

```text
Status = New
```

Requester не должен видеть:

```text
Mark Assigned
```

потому что переход разрешён Supervisor.

---

# 13. Назначить и перевести в Assigned

Войти как:

```text
supervisor.one@example.com
```

На заявке сначала выполнить:

```text
Assign To
→ technician.one@example.com
```

Проверить ToDo.

Затем выполнить Workflow Action:

```text
Mark Assigned
```

Получить:

```text
Status = Assigned
```

---

# 14. Провести работу под Technician

Войти:

```text
technician.one@example.com
```

Открыть назначенную заявку независимо от её Location.

Выполнить:

```text
Start Work
```

Проверить:

```text
Status = In Progress
```

Затем:

```text
Resolve
```

Проверить:

```text
Status = Resolved
```

Technician не должен видеть `Close`.

---

# 15. Закрыть под Supervisor

Вернуться под Supervisor и выполнить:

```text
Close
```

Получить:

```text
Status = Closed
```

У `Closed` следующего перехода нет.

---

# 16. Проверить запрещённые переходы

Обязательно получить реальные ограничения:

```text
Requester / New
→ Mark Assigned недоступен

Technician / Assigned
→ Start Work доступен
→ Resolve напрямую недоступен

Supervisor / Resolved
→ Close доступен
→ перехода назад в New нет
```

Итог:

```text
Current State
+
Allowed Role
+
Condition
=
доступные Workflow Actions
```

---

# 17. Проверить Read Only Status

Под обычным пользователем `Status` должен отображать текущее состояние, но не быть ручным переключателем.

Если поле редактируется напрямую, проверить Standard DocType:

```text
status → Read Only = Yes
```

Client Script не нужен.

---

# 18. Timeline и Workflow Action records

На заявке, прошедшей полный маршрут, посмотреть Timeline.

Сравнить:

```text
Document change
Assignment
Comment
Workflow
```

При `apply_workflow` Frappe добавляет Workflow comment для нового состояния.

Через `Workflow Action` посмотреть служебные записи по тестовой заявке и их статус.

Не создавать собственный `Workflow History` DocType.

---

# 19. Временная Condition

У перехода:

```text
New → Mark Assigned → Assigned
```

временно задать:

```python
doc.priority == "High"
```

Проверить:

```text
Priority = High
→ действие доступно

Priority = Medium
→ действие недоступно
```

После теста Condition удалить.

Это штатное expression-поле Workflow, а не собственный Python-модуль.

---

# 20. Что происходит с Kanban из L6

В L6 создана доска:

```text
Service Request Status Board
```

После появления Workflow не используем drag-and-drop как основной способ переходов.

В `v16.32.0` цепочка Kanban идёт через запись нового значения поля и обычный `doc.save()`:

```text
Kanban move
→ frappe.set_value(...)
→ frappe.client.set_value(...)
→ doc.save()
```

Workflow validation при таком save выполняется: недопустимый переход или роль не должны обходиться Kanban.

Но это не тот же action-path, что:

```text
frappe.model.workflow.apply_workflow(...)
```

`apply_workflow` выбирает Transition по Action и дополнительно ведёт штатный workflow-action/comment lifecycle.

Для одного понятного процесса оставляем один основной способ управления:

```text
Workflow Action
```

После проверки удалить Kanban Board:

```text
Service Request Status Board
```

Сам механизм Kanban уже изучен в L6.

---

# 21. Metadata и configuration

После L7 есть два слоя.

## App metadata

```text
Service Request.status
→ Read Only
```

Это source app и Git.

## Site configuration

```text
Workflow State
Workflow Action Master
Workflow
```

Пока они живут в database текущего site. Их переносимость будет собрана в L11 через fixtures.

---

# 22. Commit metadata

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

Workflow records вручную в source не копировать.

---

# 23. Приёмка L7

L7 принят, если:

- `Service Request.status` используется как единственный Workflow State Field;
- `status` Read Only;
- существуют 5 Workflow State и 4 Workflow Action Master;
- активен `Service Request Workflow`;
- Requester, Technician и Supervisor видят только свои допустимые Actions;
- Assignment остаётся отдельным от Workflow;
- Technician может обработать назначенную заявку независимо от Location;
- временная Condition проверена и удалена;
- Kanban `Service Request Status Board` удалён после сравнения;
- metadata закоммичена, Workflow configuration остаётся на site до L11.

После L7 переходим к **L8 — контроль работы и Workspace**.