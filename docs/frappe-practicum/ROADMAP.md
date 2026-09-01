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

Архитектурные гарантии формально описаны в **[INVARIANTS.md](INVARIANTS.md)**.

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

Каждый следующий урок должен использовать выход предыдущего без ручного исправления противоречий.

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

Equipment Category:

```text
HVAC
Electrical
IT
Other
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

Жёсткого вечного равенства между ними нет.

## Security

```text
Role Permission
= базовый server access

Assignment
= ответственность, не ACL

Workflow Allowed Role / Condition
= server transition gate

Only Allow Edit For
= Desk state guard, не самостоятельная ACL
```

## Web

Финальная форма:

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

Создать настоящий Bench/site/app в Developer Mode.

Изучаем:

- Bench;
- `bench new-app`;
- `bench new-site`;
- `install-app`;
- Module;
- Desk / Awesomebar;
- Developer Mode;
- app source;
- Git.

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

Создать Tree DocType:

```text
Facility Location
```

Пример:

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

Изучаем Standard DocType, Tree, Naming, generated metadata и Git.

---

# L2. Equipment

Создать:

```text
Equipment
```

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

Category строго:

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

Импортировать 10 дополнительных Equipment и доказать разницу source vs working Documents.

---

# L4. Service Request

Создать третий core DocType.

Поля:

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

Ключевая семантика:

```text
Accepted
≠ Assigned To
```

и:

```text
Service Request.location
≠ обязано навсегда совпадать с Equipment.location
```

До L7 Status остаётся обычным Select.

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

Изучаем:

```text
Role Permission Manager
If Owner
Permission Level
User Permission
Share
```

`User Permission + Share` проверяются на временном:

```text
technician.restricted@example.com
```

После эксперимента:

```text
Share удалить
User Permission удалить
Restricted Technician отключить
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

Главная модель:

```text
Permission = доступ
Assignment = ответственность
Status = процесс
```

Assignment не считается authorization.

После Assign To нормально:

```text
Assigned To = Technician
Status = New
```

Kanban:

```text
Service Request Status Board
```

колонки:

```text
New
Accepted
In Progress
Resolved
Closed
```

---

# L7. Workflow

Использовать существующий:

```text
Service Request.status
```

как единственный Workflow State Field.

Процесс:

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

Изучаем:

```text
Workflow State
Workflow Action Master
Transition
Allowed Role
Only Allow Edit For
Condition
```

Академическая граница:

```text
Allowed Role / Condition
= server transition enforcement

Only Allow Edit For
= Desk guard
```

Closed — terminal state, но абсолютную API immutability базовый курс не обещает.

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

Module остаётся `Facility Operations`.

Никаких SQL/Python reports в Core.

---

# L9. Automation

Создать второго Technician:

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

Supervisor отдельно выполняет:

```text
Accept
```

Target Date — conditional input:

```text
задан
→ Due Date / overdue automation возможны

пуст
→ этих гарантий нет
```

Assignment Rule содержит конкретных Users и остаётся site-specific.

---

# L10. Web Form

Standard:

```text
Report a Facility Issue
Route: facility-request
DocType: Service Request
```

Guest mode — временный experiment с закрытыми внутренними Link catalogs.

Финальный trust model:

```text
Website User = доверенный внутренний заявитель
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

`Allow Edit` временно изучается и затем обязательно выключается.

Причина: Web Form не должен оставаться parallel editor рабочего Workflow Document.

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

На clean site ручной ToDo **не обязан закрываться Workflow Close**, потому что L9 Assignment Rule отсутствует.

После проверки:

```bash
bench use facility-ops.localhost
```

---

# Labs A–F

Лаборатории изучают специальные механизмы, не расширяя core domain автоматически.

```text
A → Child Table
B → DocStatus/Submittable
C → Auto Repeat
D → Customize Form
E → Print/PDF
F → special fields/views
```

Каждая Lab должна иметь:

```text
Temporary Mutation
Persistent Mutation
Rollback
Final State
```

Lab E может оставить Standard Print Format как presentation configuration — это не новый domain entity.

---

# Финальная проверка последовательности

```text
OUTPUT(Ln)
→ должен удовлетворять PRECONDITIONS(Ln+1)
```

Критические gates:

```text
L4
→ Accepted вместо Assigned
→ Mandatory не ослабляются дальше

L5
→ temporary permission experiment очищен

L6
→ Assignment не превращён в ACL

L7
→ Workflow enforcement классифицирован точно

L9
→ Assignment Rule не создаёт скрытые permission exceptions
→ Target Date conditional

L10
→ final Allow Edit = No

L11
→ portable core отделён от site policy
→ active site возвращён main
```

После этого выполняется execution-аудит на чистом `v16.32.0`.
