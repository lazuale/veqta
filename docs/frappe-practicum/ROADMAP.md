# Дорожная карта практикума Frappe Framework 16

Базовая версия: **Frappe Framework v16.32.0**.

Учебное приложение:

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Постоянное ядро:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Формальные гарантии: **[INVARIANTS.md](INVARIANTS.md)**.

---

# 1. Принцип последовательности

```text
платформа
→ модель
→ данные
→ рабочий документ
→ permissions
→ collaboration
→ Workflow
→ observability
→ automation
→ external intake
→ portability
```

Критерий:

```text
OUTPUT(Ln)
должен удовлетворять
PRECONDITIONS(Ln+1)
```

---

# 2. Главные инварианты

## Данные

```text
Service Request mandatory:
Subject
Location
Description
Priority
```

```text
Equipment = optional
Target Date = optional
```

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

`Accepted` означает принятие заявки Supervisor, а не наличие assignee.

## Location

```text
Service Request.location = место события
Equipment.location       = текущее размещение Equipment
```

Вечного hard equality между ними нет.

## Security

```text
Requester
→ Create
→ Read own
→ no post-create Write
→ no Delete

Technician
→ Read/Write
→ no Create/Delete

Supervisor
→ Read/Write/Create
→ no Delete
→ Report/Export
```

```text
Role Permission
= server access boundary

Assignment
= ответственность, не ACL

Workflow Allowed Role / Condition
= server transition gate

Only Allow Edit For
= Desk state guard
```

## Web

```text
Login Required = Yes
Show List = Yes
Allow Edit = No
```

## Deployment

Assignment Rule с конкретными Users остаётся site-specific.

L11 доказывает clean-site portability.

---

# L0. Основа приложения

Создать Bench/site/app в Developer Mode.

Изучаем Bench, app, site, Module, Desk, Developer Mode, source и Git.

Приёмка:

```text
facility-ops-bench
facility_ops
facility-ops.localhost
Facility Operations
Frappe v16.32.0
```

---

# L1. Facility Location

Создать Tree DocType `Facility Location`.

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

---

# L2. Equipment

Создать `Equipment`.

Поля:

```text
Equipment Code
Equipment Name
Location
Category
Status
Serial Number
Commissioning Date
Photo
Notes
```

Category:

```text
HVAC
Electrical
IT
Other
```

Naming:

```text
field:equipment_code
```

---

# L3. Работа с данными

Изучаем:

```text
Filters
Sorting
Saved Filters
Search
Allow Import
Data Import
negative import
Export
Bulk Edit
```

Импортировать 10 дополнительных Equipment.

---

# L4. Service Request

Создать третий core DocType.

| Поле | Mandatory |
|---|---:|
| Subject | Yes |
| Location | Yes |
| Equipment | No |
| Description | Yes |
| Priority | Yes |
| Status | Yes |
| Target Date | No |
| Attachment | No |

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

```text
Accepted
≠ Assigned To
```

До L7 Status — обычный Select.

---

# L5. Пользователи и permissions

Роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Основные Users:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

Финальная `Service Request` policy:

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
→ Report/Export
```

Delete permission изучается временно под Supervisor на отдельной тестовой заявке и затем обязательно возвращается в `No`.

`User Permission + Share` проверяются на временном:

```text
technician.restricted@example.com
```

После эксперимента:

```text
Share удалить
User Permission удалить
Restricted Technician отключить
Supervisor Delete = No
```

Основные Technician остаются без Location restriction.

---

# L6. Collaboration

Изучаем:

```text
Assign To
ToDo
Comments
Timeline
Tags
Kanban
```

```text
Permission = доступ
Assignment = ответственность
Status = процесс
```

Assignment не является authorization.

После Assign To нормально:

```text
Assigned To = Technician
Status = New
```

Kanban:

```text
New
Accepted
In Progress
Resolved
Closed
```

---

# L7. Workflow

`Service Request.status` становится единственным Workflow State Field.

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

Desk edit roles:

```text
New         → Facility Supervisor
Accepted    → Facility Technician
In Progress → Facility Technician
Resolved    → Facility Supervisor
Closed      → Facility Supervisor
```

Requester всё ещё может создать новый локальный Document. После insert его настоящий server boundary:

```text
Write = No
```

Академическая граница:

```text
Allowed Role / Condition
= server transition enforcement

Only Allow Edit For
= Desk guard
```

Kanban после сравнения удалить.

---

# L8. Контроль

Создать:

```text
Report:          Service Requests Overview
Cards:           Open / High Priority / Closed Requests
Chart:           Service Requests by Status
Workspace:       Facility Operations Control
```

Аналитические представления читают доступные пользователю Documents, но сами не являются новой permission boundary.

---

# L9. Automation

Создать:

```text
technician.two@example.com
```

Notifications:

```text
New Service Request
Service Request One Day Overdue
```

Assignment Rule:

```text
Service Request Auto Assignment
Round Robin
Technician One / Technician Two
```

После assignment:

```text
Assigned To = Technician
Status = New
```

Supervisor отдельно выполняет `Accept`.

Target Date — conditional input.

Assignment Rule остаётся site-specific.

---

# L10. Web Form

```text
Report a Facility Issue
Route: facility-request
DocType: Service Request
```

Guest mode — временный experiment.

Финал:

```text
Website User = trusted internal reporter
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

`Allow Edit` изучается и обязательно выключается.

Desk Requester и Website User сходятся в одном принципе:

```text
intake
≠ право бессрочно переписывать рабочую заявку
```

---

# L11. Portability

Четыре слоя:

```text
Standard source
universal app configuration
site-specific configuration
working data
```

Fixtures:

```text
Roles
Workflow States:
  New
  Accepted
  In Progress
  Resolved
  Closed

Workflow Actions:
  Accept
  Start Work
  Resolve
  Close

Service Request Workflow
```

Не fixtures:

```text
Users
User Permission
Share
Assignment Rule tied to concrete Users
working data
```

Clean-site permission acceptance обязательно проверяет:

```text
Requester = Create + Read own, Write/Delete No
Technician = Read/Write, Create/Delete No
Supervisor = Read/Write/Create, Delete No, Report/Export
```

На clean site manual ToDo не обязан закрываться Workflow Close, потому что L9 Assignment Rule отсутствует.

После проверки:

```bash
bench use facility-ops.localhost
```

---

# Labs A–F

```text
A → Child Table
B → DocStatus/Submittable
C → Auto Repeat
D → Customize Form
E → Print/PDF
F → special fields/views
```

Каждая Lab должна иметь Temporary Mutation / Persistent Mutation / Rollback / Final State.

---

# Финальная проверка последовательности

Критические gates:

```text
L4
→ Accepted вместо Assigned
→ Mandatory сохраняются

L5
→ Requester append-only после insert
→ Service Request Delete выключен у рабочих ролей
→ temporary permission experiments очищены

L6
→ Assignment не превращён в ACL

L7
→ New обслуживает Supervisor
→ Requester Create сохраняется, post-create Write запрещён Role Permission
→ Workflow enforcement классифицирован точно

L9
→ Assignment Rule не создаёт hidden access exceptions
→ Target Date conditional

L10
→ final Allow Edit = No

L11
→ exact permission matrix восстановлена на clean site
→ portable core отделён от site policy
→ active site возвращён main
```

После этого выполняется execution-аудит на чистом `v16.32.0`.
