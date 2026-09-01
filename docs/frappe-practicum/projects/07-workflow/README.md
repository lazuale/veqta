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

Различать:

```text
Role Permission
= server access permission

Workflow Allowed Role + Condition
= server transition permission

Only Allow Edit For
= state-dependent Desk UI guard
```

`Only Allow Edit For` не является самостоятельной ACL.

От L5 уже действует hard permission:

```text
Requester
→ Create = Yes
→ Read own = Yes
→ Write = No после insert
→ Delete = No
```

Workflow не должен подменять эту server boundary.

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

Проверить L5 output:

```text
Requester saved Service Request → Read own, Write No
Technician → Read/Write, no Create/Delete
Supervisor → Read/Write/Create, Delete No
```

Основной Technician не имеет постоянного Location User Permission.

Kanban L6 `Service Request Status Board` пока существует.

---

# 3. Ещё раз доказать проблему обычного Select

До Workflow под пользователем с Write вручную выполнить на тестовой заявке:

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

Requester для этого теста не использовать: после L5 у него уже нет Write сохранённого Document.

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

---

# 5. Сделать Status Read Only

Для `status`:

```text
Read Only = Yes
Default = New
```

Read Only — UI guard. Server допустимость state change обеспечивает Workflow validation.

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

Почему `New` теперь Supervisor:

```text
Requester
→ только подаёт новую заявку
→ после insert server Write = No

Supervisor
→ принимает и при необходимости корректирует New перед запуском процесса
```

## Почему это не ломает Requester Create

В exact `v16.32.0` client Workflow:

```text
is_read_only()
→ для doc.__islocal возвращает false
```

То есть новый локальный документ не блокируется state edit role.

Server `validate_workflow()` при insert первой state не рассматривает это как переход между двумя states.

Поэтому совместимы одновременно:

```text
Requester Create = Yes
New.only_allow_edit_for = Facility Supervisor
Requester post-create Write = No
```

Это важный negative/positive compatibility test L7.

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
Description: Проверка Create при New state owned Supervisor
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

Ожидается:

```text
Write запрещён Role Permission
```

Главный вывод:

```text
Requester Create
совместим с
post-create immutable-for-requester intake
```

Не приписывать этот hard запрет `Only Allow Edit For`: его обеспечивает L5 Role Permission.

---

# 15. Назначить ответственность отдельно

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

# 16. Supervisor принимает заявку

Выполнить:

```text
Accept
```

Получить:

```text
Status = Accepted
```

`Accepted` не является доказательством ToDo. Мы соблюдаем рекомендуемый порядок `Assign To → Accept`, но это не hard coupling Frappe.

---

# 17. Technician выполняет процесс

Под `technician.one@example.com`:

```text
Start Work
→ Status = In Progress

Resolve
→ Status = Resolved
```

Technician не должен иметь Workflow Action `Close`.

---

# 18. Supervisor закрывает

Под Supervisor:

```text
Close
→ Status = Closed
```

У Closed нет исходящего transition.

Рабочие роли также не имеют Service Request Delete.

Но это не обещание абсолютной API immutability всех полей: для неё нужен отдельный server-validation слой.

---

# 19. Запрещённые переходы

Проверить:

```text
Requester / New
→ Accept недоступен
→ post-create Write запрещён Role Permission

Technician / Accepted
→ Start Work доступен
→ Resolve напрямую недоступен

Supervisor / Resolved
→ Close доступен
→ перехода назад в New нет
```

---

# 20. Временная Condition

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

# 21. Kanban после Workflow

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

# 22. Timeline и audit

Сравнить:

```text
Assignment
Comment
Version / field change
Workflow comment/action
```

Не создавать собственный Workflow History.

---

# 23. Классифицировать enforcement

| Механизм | Роль |
|---|---|
| Role Permission | server access boundary |
| Allowed Role | server transition boundary |
| Workflow Condition | server transition predicate |
| Status Read Only | UI guard |
| Only Allow Edit For | Desk state guard |
| Track Changes | audit, не запрет |

---

# 24. Metadata и configuration

App metadata:

```text
Service Request.status → Read Only
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

Workflow records попадут в portable configuration только в L11.

---

# 26. State contract L7

## Preconditions

```text
L5 final permission matrix действует
L6 assignment/collaboration изучены
Kanban существует
```

## Temporary

```text
Workflow Condition priority == High
```

## Persistent

```text
status Read Only
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
Requester Create still works
Requester saved Document Write = No
Workflow transitions role-gated
Assignment remains separate
```

---

# 27. Приёмка L7

L7 принят, если:

- `status` — единственный Workflow State Field;
- states `New / Accepted / In Progress / Resolved / Closed`;
- actions `Accept / Start Work / Resolve / Close`;
- `New.only_allow_edit_for = Facility Supervisor`;
- Requester после включения Workflow реально создаёт новую заявку;
- после Save тот же Requester не может её переписать;
- hard запрет post-create edit объясняется Role Permission, а не `Only Allow Edit For`;
- Allowed Role реально ограничивает transitions;
- temporary Condition удалена;
- `Accepted` не трактуется как наличие assignee;
- Assignment остаётся ToDo-механизмом;
- `Closed` — terminal state, но не ложное обещание absolute API immutability;
- Kanban удалён;
- metadata закоммичена.

После L7 переходим к **L8 — контроль работы и Workspace**.
