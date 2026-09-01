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

Все состояния имеют `docstatus = 0`.

---

# 1. Enforcement model

После L5 уже существуют два permission layer:

```text
Permission Level 0
= document-level authority

Permission Level 1
= business-content authority
```

L7 добавляет третий слой:

```text
Workflow Allowed Role + Condition
= server transition authority
```

И отдельно остаётся UI guard:

```text
Only Allow Edit For
= state-dependent Desk behavior
```

Итоговая схема:

```text
Level 0 Role Permission
→ можно ли save/create/delete Document

Level 1 Permission
→ какие business fields можно менять

Workflow
→ какой state transition разрешён

Only Allow Edit For
→ как Desk ведёт себя в текущем state
```

`Only Allow Edit For` не является самостоятельной ACL.

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

Проверить L5 output.

## Level 0

```text
Requester
→ Create + Read own
→ Write/Delete No

Technician
→ Read/Write
→ Create/Delete No

Supervisor
→ Read/Write/Create
→ Delete No
```

## Level 1 Service Request content

```text
subject
location
equipment
description
priority
target_date
attachment
```

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

`status` остаётся Level 0.

Основной Technician не имеет постоянного Location User Permission.

Kanban L6 `Service Request Status Board` пока существует.

---

# 3. Ещё раз доказать проблему обычного Select

До Workflow под Supervisor вручную выполнить на тестовой заявке:

```text
New → Closed
```

Сохранить и вернуть логичное состояние.

```text
Select
= набор значений

Select
≠ допустимые переходы
```

Requester для этого теста не использовать: после L5 у него уже нет document Write сохранённого Document.

---

# 4. Использовать существующий Status

`Service Request.status`:

```text
New
Accepted
In Progress
Resolved
Closed
```

Настроить:

```text
Workflow State Field = status
```

Не создавать:

```text
workflow_state
request_state
workflow_status
```

`status` остаётся Permission Level 0 именно потому, что Workflow должен менять его независимо от Level 1 business content.

---

# 5. Сделать Status Read Only

Для `status`:

```text
Read Only = Yes
Default = New
Permission Level = 0
```

Read Only — UI guard.

Server допустимость state change обеспечивает Workflow validation.

Проверить diff Standard metadata.

---

# 6. Создать Workflow State

```text
New
Accepted
In Progress
Resolved
Closed
```

Названия точно совпадают с Select options.

---

# 7. Создать Workflow Action Master

```text
Accept
Start Work
Resolve
Close
```

```text
Accept
= Supervisor принимает заявку в процесс

Assign To
= конкретному User создаётся ToDo
```

---

# 8. Создать Workflow

```text
Workflow Name:        Service Request Workflow
Document Type:        Service Request
Workflow State Field: status
Is Active:            No
```

---

# 9. Document States

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| New | 0 | **Facility Supervisor** |
| Accepted | 0 | Facility Technician |
| In Progress | 0 | Facility Technician |
| Resolved | 0 | Facility Supervisor |
| Closed | 0 | Facility Supervisor |

Почему `New` принадлежит Supervisor в Desk:

```text
Requester
→ подаёт новую заявку
→ после insert Level 0 Write = No

Supervisor
→ принимает и при необходимости корректирует New
```

## Почему это не ломает Requester Create

В exact `v16.32.0` client Workflow:

```text
is_read_only()
→ для doc.__islocal возвращает false
```

Server insert первой state не является переходом между двумя сохранёнными states.

Requester при этом имеет Level 1 Write, поэтому high-permlevel Mandatory content нового Document не сбрасывается.

Совместимы одновременно:

```text
Requester Level 0 Create = Yes
Requester Level 1 Write = Yes
New.only_allow_edit_for = Facility Supervisor
Requester post-create Level 0 Write = No
```

---

# 10. Transitions

| State | Action | Next State | Allowed |
|---|---|---|---|
| New | Accept | Accepted | Facility Supervisor |
| Accepted | Start Work | In Progress | Facility Technician |
| In Progress | Resolve | Resolved | Facility Technician |
| Resolved | Close | Closed | Facility Supervisor |

Conditions в финале пустые.

---

# 11. Workflow не проверяет assignee

Не обещаем hard rule:

```text
Start Work может только User из ToDo
```

```text
Facility Technician role
→ полномочие роли на transition

ToDo
→ ответственность конкретного User
```

Assignee-only transition policy — Later server-side architecture.

---

# 12. Активировать Workflow

Проверить states/transitions и включить:

```text
Is Active = Yes
```

Затем:

```bash
bench --site facility-ops.localhost clear-cache
```

---

# 13. Нормализовать старые учебные данные

Если старый стенд содержит legacy:

```text
Assigned
```

до финальной проверки перевести такие тестовые records в:

```text
Accepted
```

Не возвращать старый state в Workflow.

---

# 14. Критический тест Requester после включения Workflow

Войти:

```text
requester.one@example.com
```

Создать новый Document:

```text
Subject:     Workflow requester create test
Location:    Room 102
Description: Проверка Create при Level 1 content и New state Supervisor
Priority:    Medium
```

До первого Save форма должна позволять заполнить новый local Document.

Сохранить.

Получить:

```text
Status = New
Owner = requester.one@example.com
```

После Save попытаться изменить `Description`.

Ожидается отказ на document save:

```text
Level 0 Write = No
```

Главный вывод:

```text
Requester Level 1 Write
нужен для создания

но

Requester Level 0 Write No
делает intake append-only после insert
```

---

# 15. Supervisor может корректировать New content

Под Supervisor открыть созданную Requester заявку.

Проверить, что Supervisor может изменить, например:

```text
Priority
Target Date
```

и сохранить.

Это ожидаемо:

```text
Supervisor Level 0 Write = Yes
Supervisor Level 1 Write = Yes
New Desk edit role = Supervisor
```

После проверки оставить логичные значения.

---

# 16. Назначить ответственность отдельно

Под Supervisor:

```text
Assign To
→ technician.one@example.com
```

Проверить ToDo.

После Assign To:

```text
Assigned To = technician.one@example.com
Status = New
```

---

# 17. Supervisor принимает заявку

Выполнить:

```text
Accept
```

Получить:

```text
Status = Accepted
```

`Accepted` не является доказательством ToDo.

Мы соблюдаем рекомендуемый порядок `Assign To → Accept`, но это не hard coupling Frappe.

---

# 18. Критический тест Technician: Workflow без content Write

Войти:

```text
technician.one@example.com
```

Открыть Accepted заявку.

Проверить Level 1 поля:

```text
Description
Priority
Target Date
Location
Equipment
```

Technician должен их видеть, но не иметь штатного field Write.

Теперь выполнить:

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

Это главный compatibility proof L7:

```text
Technician Level 0 Write
+
status Level 0
→ Workflow transitions работают

Technician Level 1 Write = No
→ business content не становится редактируемым
```

---

# 19. Server negative test high Permission Level

Если Desk уже делает Level 1 поля read-only, этого недостаточно как единственного доказательства.

На отдельной тестовой заявке выполнить permission-aware save path, который пытается передать изменённый Level 1 field под Technician, и затем перечитать Document.

Проверяем факт exact `v16.32.0`:

```text
validate_higher_perm_levels()
→ недопустимое Level 1 изменение сбрасывается к исходному значению
```

Не использовать для этого:

```text
ignore_permissions=True
frappe.db.set_value
raw SQL
```

потому что лаборатория проверяет именно ordinary Document permission path.

Если на конкретном стенде штатный UI не позволяет удобно сформировать такой запрос, достаточно зафиксировать серверный source behavior и обязательный Desk negative test; собственный тестовый Python-код ради курса не пишем.

---

# 20. Supervisor закрывает

Под Supervisor:

```text
Close
→ Status = Closed
```

У Closed нет исходящего transition.

Рабочие роли также не имеют Service Request Delete.

Но это не обещание абсолютной API immutability всех полей: для неё нужен отдельный server-validation слой.

---

# 21. Запрещённые переходы и записи

Проверить:

```text
Requester / New
→ Accept недоступен
→ post-create save запрещён Level 0 Role Permission

Technician / Accepted
→ Start Work доступен
→ Resolve напрямую недоступен
→ Level 1 content write отсутствует

Supervisor / Resolved
→ Close доступен
→ перехода назад в New нет
```

---

# 22. Временная Condition

У:

```text
New → Accept → Accepted
```

временно задать:

```python
doc.priority == "High"
```

Проверить High/Medium и затем **обязательно удалить Condition**.

Condition — server transition predicate, но не permanent бизнес-правило курса.

---

# 23. Kanban после Workflow

L6 Kanban использует те же state values.

В `v16.32.0` Kanban update приходит к обычному save, где Workflow validation проверяет state change.

Но:

```text
Kanban move
≠ Workflow Action lifecycle
```

После сравнения удалить:

```text
Service Request Status Board
```

---

# 24. Timeline и audit

Сравнить:

```text
Assignment
Comment
Version / field change
Workflow comment/action
```

Не создавать собственный Workflow History.

---

# 25. Классифицировать enforcement

| Механизм | Роль |
|---|---|
| Level 0 Role Permission | server document access/save boundary |
| Level 1 Permission | server business-field write/read boundary on ordinary Document path |
| Allowed Role | server transition boundary |
| Workflow Condition | server transition predicate |
| Status Read Only | UI guard |
| Only Allow Edit For | Desk state guard |
| Track Changes | audit, не запрет |
| Assignment | responsibility, не ACL |

---

# 26. Metadata и configuration

App metadata:

```text
Service Request.status → Read Only + permlevel 0
Service Request business content → permlevel 1
```

Site configuration до L11:

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

New.allow_edit = Facility Supervisor
```

---

# 27. Commit metadata

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

Workflow records попадут в portable configuration только в L11.

---

# 28. State contract L7

## Preconditions

```text
L5 Level 0 + Level 1 permission matrix действует
L6 assignment/collaboration изучены
Kanban существует
```

## Temporary

```text
Workflow Condition priority == High
```

## Persistent

```text
status Read Only + Level 0
Service Request content remains Level 1
Service Request Workflow active
New edit role = Supervisor
Accepted/In Progress edit role = Technician
Resolved/Closed edit role = Supervisor
```

## Rollback

```text
temporary Condition removed
Kanban removed
```

## Output

```text
Requester Create works
Requester saved Document Write = No
Technician Workflow transitions work
Technician Level 1 content Write = No
Supervisor content Write works
Workflow transitions role-gated
Assignment remains separate
```

---

# 29. Приёмка L7

L7 принят, если:

- `status` — единственный Workflow State Field;
- states `New / Accepted / In Progress / Resolved / Closed`;
- actions `Accept / Start Work / Resolve / Close`;
- `status` остаётся Permission Level 0;
- business content остаётся Permission Level 1;
- `New.only_allow_edit_for = Facility Supervisor`;
- Requester после включения Workflow реально создаёт новую заявку;
- после Save Requester не может её переписать;
- Supervisor может корректировать Level 1 content;
- Technician выполняет `Start Work / Resolve`;
- Technician не получает Level 1 content Write;
- hard post-create Requester restriction объясняется Role Permission, а не `Only Allow Edit For`;
- field protection объясняется Permission Level, а не только read-only UI;
- Allowed Role реально ограничивает transitions;
- temporary Condition удалена;
- `Accepted` не трактуется как наличие assignee;
- Assignment остаётся ToDo-механизмом;
- `Closed` — terminal state, но не ложное обещание absolute API immutability;
- Kanban удалён;
- metadata закоммичена.

После L7 переходим к **L8 — контроль работы и Workspace**.
