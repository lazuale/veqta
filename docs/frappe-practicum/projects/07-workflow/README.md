# L7. Workflow

L7 переводит `Service Request` с ручного `Status` на управляемый Workflow.

Новых предметных DocType в уроке нет.

Цель: сохранить уже знакомые состояния заявки, но запретить произвольные переходы между ними и передать управление полем `status` штатному Workflow Frappe.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

До L7:

```text
Status = обычный Select

New
Assigned
In Progress
Resolved
Closed

пользователь с Write может менять поле вручную
```

После L7:

```text
Service Request.status
        ▲
        │
     Workflow
        │
        ├── Mark Assigned → Facility Supervisor
        ├── Start Work    → Facility Technician
        ├── Resolve       → Facility Technician
        └── Close         → Facility Supervisor
```

Итоговый маршрут:

```text
New
 │
 │ Mark Assigned
 │ Facility Supervisor
 ▼
Assigned
 │
 │ Start Work
 │ Facility Technician
 ▼
In Progress
 │
 │ Resolve
 │ Facility Technician
 ▼
Resolved
 │
 │ Close
 │ Facility Supervisor
 ▼
Closed
```

Все состояния имеют:

```text
docstatus = 0
```

`Service Request` остаётся обычным несабмиттабельным Document.

`Draft / Submit / Cancel / Amend` здесь не смешиваем с Workflow — они изучаются отдельно в Lab B.

---

# 1. Проверить состояние после L6

В терминале:

```bash
cd ~/frappe/facility-ops-bench

bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
Git working tree clean
```

В Desk должны существовать:

```text
Facility Location
Equipment
Service Request
```

Роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Пользователи минимум:

```text
requester.one@example.com
technician.one@example.com
supervisor.one@example.com
```

После L6 уже должны быть понятны:

```text
Permission
Assignment
Status
```

Если L6 не принят — L7 не начинаем.

---

# 2. Ещё раз увидеть проблему ручного Status

До создания Workflow открыть любую тестовую заявку под пользователем, который имеет `Write`.

Например временно изменить:

```text
New → Closed
```

Сохранить.

Если обычные permissions позволяют изменение, Frappe сохранит его: `Status` пока просто `Select`.

Вернуть заявке исходное логичное состояние.

Зафиксировать:

```text
Select
= список допустимых значений

Select
≠ правила переходов между значениями
```

Именно эту проблему решает Workflow.

---

# 3. Не создавать второе поле состояния

В `Service Request` уже существует:

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

Это же поле используем как:

```text
Workflow State Field = status
```

Не создаём:

```text
workflow_state
request_state
workflow_status
```

и не дублируем смысл.

В Frappe v16.32.0 Workflow создаёт скрытый Custom Field только тогда, когда указанного `workflow_state_field` нет в DocType.

У нас `status` уже существует, поэтому новый Custom Field не нужен.

---

# 4. Сделать Status пользовательски Read Only

Теперь состояние должно меняться Workflow, а не ручным редактированием поля.

Открыть Standard DocType:

```text
Service Request
```

Для поля:

```text
Status
fieldname: status
```

включить:

```text
Read Only = Yes
```

Default оставить:

```text
New
```

Options не менять:

```text
New
Assigned
In Progress
Resolved
Closed
```

Сохранить DocType.

Это единственное изменение metadata приложения в L7.

Смысл:

```text
status
= хранит состояние

Workflow Action
= меняет состояние

пользователь
≠ редактирует status напрямую
```

---

# 5. Проверить metadata после Read Only

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff -- \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

В diff должно появиться изменение поля `status`, соответствующее Read Only.

Другие поля Service Request без причины не менять.

Пока commit не делать.

---

# 6. Создать Workflow State

Через Awesomebar открыть:

```text
Workflow State
```

Создать пять записей:

```text
New
Assigned
In Progress
Resolved
Closed
```

Использовать ровно те же строки, что находятся в `Service Request.status`.

Не создавать отдельные предметные справочники статусов.

`Workflow State` здесь — штатная конфигурационная сущность Frappe.

---

# 7. Создать Workflow Action Master

Через Awesomebar открыть:

```text
Workflow Action Master
```

Создать четыре действия:

```text
Mark Assigned
Start Work
Resolve
Close
```

Почему первое действие называется `Mark Assigned`, а не просто `Assign`:

```text
Assign To
= создаёт ToDo и назначает работу человеку

Mark Assigned
= переводит Service Request в состояние Assigned
```

Это разные механизмы.

Workflow сам по себе не заменяет `Assign To`.

---

# 8. Создать Workflow

Через Awesomebar открыть:

```text
Workflow
```

Создать:

```text
Workflow Name:        Service Request Workflow
Document Type:        Service Request
Is Active:            выключено пока
Workflow State Field: status
```

Оставить выключенными:

```text
Send Email Alert
Enable Action Confirmation
```

Email и автоматические уведомления будут изучаться позже.

Не включать опции только ради демонстрации.

---

# 9. Настроить состояния Workflow

В таблице `Document States` добавить:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| New | 0 | Facility Requester |
| Assigned | 0 | Facility Technician |
| In Progress | 0 | Facility Technician |
| Resolved | 0 | Facility Supervisor |
| Closed | 0 | Facility Supervisor |

Для всех строк:

```text
Doc Status = 0
```

Не использовать:

```text
1 = Submitted
2 = Cancelled
```

потому что `Service Request` не является Submittable DocType.

`Only Allow Edit For` отвечает за редактирование обычных полей документа в конкретном состоянии.

Он не заменяет Role Permission Manager.

То есть действуют оба слоя:

```text
Role Permission
      +
Workflow State Allow Edit
      ↓
фактическая возможность редактирования
```

---

# 10. Настроить переходы

В таблице `Transitions` создать четыре строки:

| State | Action | Next State | Allowed |
|---|---|---|---|
| New | Mark Assigned | Assigned | Facility Supervisor |
| Assigned | Start Work | In Progress | Facility Technician |
| In Progress | Resolve | Resolved | Facility Technician |
| Resolved | Close | Closed | Facility Supervisor |

`Allow Self Approval` оставить в штатном состоянии.

В базовом уроке не строим отдельную схему самоутверждения.

Conditions пока оставить пустыми.

Получается:

```text
New
  --Mark Assigned / Supervisor-->
Assigned
  --Start Work / Technician-->
In Progress
  --Resolve / Technician-->
Resolved
  --Close / Supervisor-->
Closed
```

---

# 11. Проверить Workflow до активации

Перед включением ещё раз проверить:

```text
Document Type = Service Request
Workflow State Field = status
```

States:

```text
New
Assigned
In Progress
Resolved
Closed
```

Transitions:

```text
New → Assigned
Assigned → In Progress
In Progress → Resolved
Resolved → Closed
```

Все `Doc Status`:

```text
0
```

После этого включить:

```text
Is Active = Yes
```

Сохранить Workflow.

---

# 12. Очистить cache и открыть Service Request заново

В терминале:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost clear-cache
```

Обновить браузер.

Не продолжать тест на старой уже открытой форме, если она была загружена до активации Workflow.

---

# 13. Проверить существующие заявки

Открыть несколько Service Request, созданных до L7.

Их значения `status` уже должны совпадать с Workflow State:

```text
New
Assigned
In Progress
Resolved
Closed
```

Отдельная миграция рабочего поля не нужна.

Если на site существует заявка со значением Status, которого нет среди Workflow States, сначала исправить тестовые данные.

Не добавлять странный Workflow State только ради старой ошибочной записи.

---

# 14. Создать новую заявку под Requester

Войти:

```text
requester.one@example.com
```

Создать новую заявку в разрешённом ему Location.

Например:

```text
Subject:     Workflow test request
Location:    Room 101
Description: Проверка нового управляемого процесса
Priority:    Medium
```

Сохранить.

Проверить:

```text
Status = New
```

Requester не должен получать действие:

```text
Mark Assigned
```

потому что этот transition разрешён роли:

```text
Facility Supervisor
```

Requester в состоянии `New` при этом может редактировать обычные поля в рамках своих Role Permissions и `If Owner`.

---

# 15. Назначить заявку технику

Войти:

```text
supervisor.one@example.com
```

Открыть созданную заявку.

Сначала использовать уже изученный механизм:

```text
Assign To
→ technician.one@example.com
```

Проверить созданный `ToDo`.

После этого выполнить Workflow Action:

```text
Mark Assigned
```

Проверить результат:

```text
Status = Assigned
```

Важно:

```text
Assign To
→ создал ToDo

Mark Assigned
→ изменил Workflow State / status
```

Один механизм не подменяет другой.

---

# 16. Проверить Workflow под Technician

Войти:

```text
technician.one@example.com
```

Использовать заявку для `Room 101`, чтобы не конфликтовать с User Permission из L5.

Открыть назначенный Service Request.

В состоянии:

```text
Assigned
```

должно быть доступно действие:

```text
Start Work
```

Выполнить.

Проверить:

```text
Status = In Progress
```

Затем выполнить:

```text
Resolve
```

Проверить:

```text
Status = Resolved
```

Technician не должен получать действие:

```text
Close
```

потому что оно разрешено только:

```text
Facility Supervisor
```

---

# 17. Закрыть заявку под Supervisor

Вернуться под:

```text
supervisor.one@example.com
```

Открыть ту же заявку.

При состоянии:

```text
Resolved
```

должно быть доступно:

```text
Close
```

Выполнить.

Проверить:

```text
Status = Closed
```

После `Closed` в нашей линейной схеме нет следующего перехода.

---

# 18. Проверить запрещённые переходы

Нужны минимум три отрицательные проверки.

## Проверка A — Requester

Requester открывает `New` заявку.

Он не должен иметь Workflow Action:

```text
Mark Assigned
```

## Проверка B — Technician

Technician открывает `Assigned` заявку.

У него должно быть:

```text
Start Work
```

но не должно быть:

```text
Resolve
```

до перехода в `In Progress`.

## Проверка C — Supervisor

Supervisor открывает `Resolved` заявку.

У него должно быть:

```text
Close
```

но не должно быть перехода напрямую из `Resolved` в `New` или `Assigned`.

Главное:

```text
Workflow State
+
Allowed Role
+
текущий State
=
набор доступных Workflow Actions
```

---

# 19. Проверить, что Status больше не рабочая кнопка процесса

Открыть Service Request под обычным пользователем.

Поле:

```text
Status
```

должно отображать текущее состояние, но не использоваться как ручной способ провести заявку по процессу.

Все нормальные переходы выполняются через Workflow Action.

Если Status всё ещё редактируется напрямую — вернуться к Standard DocType и проверить:

```text
status → Read Only = Yes
```

Не добавлять Client Script для блокировки поля.

---

# 20. Посмотреть Timeline

Открыть заявку, которая прошла полный маршрут:

```text
New
→ Assigned
→ In Progress
→ Resolved
→ Closed
```

Посмотреть Timeline.

Frappe добавляет записи Workflow при применении переходов.

Сравнить в одной истории:

```text
обычное изменение Document
Assignment
Comment
Workflow transition
```

Не создавать собственный `Workflow History` DocType.

---

# 21. Посмотреть Workflow Action

Под пользователем с ожидающим действием открыть через Awesomebar:

```text
Workflow Action
```

Найти открытое действие, связанное с тестовым `Service Request`.

Проверить минимум:

```text
Reference Document Type = Service Request
Reference Name          = SR-.....
Workflow State          = текущее состояние
Status                  = Open / Completed
```

После выполнения допустимого перехода соответствующее Workflow Action должно быть обработано штатным механизмом Frappe.

Не создавать собственную таблицу «ожидающих согласований».

---

# 22. Коротко проверить Condition

Это временный эксперимент, а не финальное бизнес-правило.

Открыть `Service Request Workflow`.

У перехода:

```text
New
→ Mark Assigned
→ Assigned
```

временно указать Condition:

```python
doc.priority == "High"
```

Сохранить Workflow и обновить формы.

Проверить две новые заявки:

```text
Priority = High
→ Supervisor видит Mark Assigned

Priority = Medium
→ Supervisor не видит Mark Assigned
```

После проверки **удалить Condition** и сохранить Workflow.

Финальный процесс должен снова принимать заявки любого Priority.

Что нужно понять:

```text
Condition
= дополнительное условие появления/допуска transition
```

Это штатное выражение Workflow.

Собственный Python-модуль не пишется.

---

# 23. Проверить Kanban после Workflow

Открыть созданный в L6 Kanban:

```text
Service Requests by Status
```

Колонки остаются:

```text
New
Assigned
In Progress
Resolved
Closed
```

Теперь Workflow уже управляет допустимыми переходами процесса.

Не использовать drag-and-drop Kanban как способ обходить Workflow.

Проверить фактическое поведение на стенде v16.32.0 под Technician и Supervisor.

Если Frappe блокирует недопустимый переход — это ожидаемо.

Если интерфейс предлагает действие, которое сервер затем отклоняет, зафиксировать фактическое поведение и не обходить проверку.

---

# 24. Понять, что попало в app, а что осталось в database

После L7 есть два разных типа изменений.

## Metadata app

Изменён Standard DocType `Service Request`:

```text
status.read_only = 1
```

Это должно быть видно в Git.

## Configuration Documents site

Созданы:

```text
Workflow State
Workflow Action Master
Workflow
```

Это обычные configuration Documents в database текущего site.

Они сами по себе не обязаны появиться как source-файлы `facility_ops`.

Это сознательно оставляем до L11, где будем разбирать fixtures и переносимость.

---

# 25. Зафиксировать metadata L7 в Git

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

Ожидаемый осознанный diff:

```text
Service Request.status
→ Read Only
```

Добавить:

```bash
git add \
  facility_ops/facility_operations/doctype/service_request/service_request.json

git diff --cached
```

Commit:

```bash
git commit -m "Make service request status workflow controlled"
git status
```

Ожидается:

```text
working tree clean
```

Workflow configuration пока живёт в database site.

---

# 26. Самостоятельная практика

Без готовой пошаговой инструкции выполнить следующее.

Создать новую Service Request под Requester и провести её до `Closed` правильными пользователями.

Условия:

1. Requester создаёт заявку.
2. Supervisor назначает её Technician через `Assign To`.
3. Supervisor выполняет `Mark Assigned`.
4. Technician выполняет `Start Work`.
5. Technician выполняет `Resolve`.
6. Supervisor выполняет `Close`.
7. Никто не редактирует Status вручную.
8. В Timeline видна история процесса.
9. Ученик может найти связанные Workflow Action / ToDo.

---

# 27. Приёмка L7

L7 принят, если ученик может показать следующее.

## Workflow

Существует активный:

```text
Service Request Workflow
```

с:

```text
Document Type = Service Request
Workflow State Field = status
```

Нового `workflow_state` поля нет.

## States

```text
New
Assigned
In Progress
Resolved
Closed
```

У всех:

```text
Doc Status = 0
```

## Transitions

```text
New        → Assigned    → Facility Supervisor
Assigned   → In Progress → Facility Technician
In Progress→ Resolved    → Facility Technician
Resolved   → Closed      → Facility Supervisor
```

## Process

Заявка проходит:

```text
New
→ Assigned
→ In Progress
→ Resolved
→ Closed
```

только через допустимые Workflow Actions.

## Negative tests

- Requester не выполняет `Mark Assigned`;
- Technician не выполняет `Close`;
- переходы нельзя перескакивать;
- `Status` не используется как ручной переключатель процесса.

## Collaboration

Ученик различает:

```text
Assign To / ToDo
= кому поручено

Workflow
= какой переход разрешён

Status
= текущее состояние
```

## Configuration

Ученик понимает, что:

```text
Service Request JSON
= metadata app

Workflow / Workflow State / Workflow Action Master
= configuration Documents текущего site
```

и знает, что вопрос их переноса будет решаться в L11.

## Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое после commit.

---

# Итог L7

До L7:

```text
пользователь меняет Status
```

После L7:

```text
пользователь выбирает разрешённое Action
        ↓
Workflow проверяет State + Role + Condition
        ↓
Frappe меняет status
        ↓
появляется история Workflow
```

Следующий урок — **L8. Контроль работы**: Report Builder, Number Card, Dashboard Chart и Workspace на уже накопленных `Service Request`.
