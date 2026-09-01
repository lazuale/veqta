# Дорожная карта практикума Frappe Framework 16

Базовая версия: **Frappe Framework v16.32.0**.

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Core:

```text
Facility Location
Equipment
Service Request
```

Формальные гарантии: [INVARIANTS.md](INVARIANTS.md).

---

# Последовательность

```text
L0 платформа
→ L1 Location
→ L2 Equipment
→ L3 данные
→ L4 Service Request
→ L5 permissions
→ L6 collaboration
→ L7 Workflow
→ L8 control
→ L9 automation
→ L10 Web Form intake
→ L11 portability
```

Критерий:

```text
OUTPUT(Ln) ⊇ PRECONDITIONS(Ln+1)
```

---

# Глобальные инварианты

Service Request Mandatory:

```text
Subject
Location
Description
Priority
```

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

```text
Accepted ≠ Assigned To
Permission ≠ Assignment ≠ Workflow
```

Location semantics:

```text
Service Request.location = historical event location
Equipment.location       = current equipment location
```

## Финальная Desk security model

Permission Level 0 управляет document-level operations:

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

Содержательные поля `Service Request` находятся на Permission Level 1:

```text
subject
location
equipment
description
priority
target_date
attachment
```

Level 1:

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

`status` остаётся Level 0.

Итоговая модель:

```text
Level 0 Role Permission
→ право создать/читать/save/delete Document

Level 1 Permission
→ право читать/изменять business content

Workflow
→ право менять process state
```

Requester Level 1 Write нужен для заполнения нового Document; после insert Level 0 `Write = No` запрещает повторный save.

Technician Level 0 Write нужен для Workflow; Level 1 `Write = No` не даёт штатным permission-aware save переписывать исходные реквизиты заявки.

## Финальный Web Form

```text
Published = Yes
Login Required = Yes
Allow Edit = No
Show List = Yes
Apply Document Permissions = No
```

Критическая граница:

```text
Desk Create
= Role Permission path

Web Form create
= separate Web Form intake path
= new doc insert with ignore_permissions
```

Поэтому финальный запрет Web Form update обязателен: `ignore_permissions=True` не должен оставаться параллельным редактором рабочего Document.

---

# L0. Основа

Bench, site, app, Module, Developer Mode, Desk, Git.

---

# L1. Facility Location

Tree:

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

Category:

```text
HVAC
Electrical
IT
Other
```

Status:

```text
Active
Out of Service
Retired
```

Naming `field:equipment_code`.

---

# L3. Data operations

Filters, Sorting, Saved Filters, Data Import, negative import, Export, Bulk Edit.

Импортировать 10 дополнительных Equipment.

---

# L4. Service Request

Создать третий core DocType.

```text
New
Accepted
In Progress
Resolved
Closed
```

До L7 Status — обычный Select.

---

# L5. Permissions

Создать роли и основных Users.

Построить двухуровневую permission model:

```text
Level 0
→ document authority

Level 1
→ Service Request content authority
```

Финальный output:

```text
Requester
→ create/read-own
→ no post-create save

Technician
→ document Write для Workflow
→ business content read-only

Supervisor
→ business content write
→ no Service Request Delete
```

Temporary experiments:

```text
Supervisor Delete = Yes → test → No
Restricted Technician
User Permission
Share
```

Все временные ограничения очищаются до L6.

---

# L6. Collaboration

```text
Assign To
ToDo
Comments
Timeline
Tags
Kanban
```

Assignment = responsibility, not authorization.

L6 не ослабляет Level 1 protection Service Request content.

---

# L7. Workflow

```text
New --Accept/Supervisor--> Accepted
Accepted --Start Work/Technician--> In Progress
In Progress --Resolve/Technician--> Resolved
Resolved --Close/Supervisor--> Closed
```

Desk edit roles:

```text
New         → Supervisor
Accepted    → Technician
In Progress → Technician
Resolved    → Supervisor
Closed      → Supervisor
```

Requester Create сохраняется для local new doc; после Save server Level 0 `Write = No`.

Критический proof для Technician:

```text
Start Work / Resolve проходят
но
Description / Priority / Target Date
не становятся Technician-writeable
```

То есть Workflow не требует отдавать Technician право переписывать business content.

Kanban после сравнения удалить.

---

# L8. Control

```text
Service Requests Overview
Open Requests
High Priority Requests
Closed Requests
Service Requests by Status
Facility Operations Control
```

Reports/Cards/Chart читают существующие Documents и не создают новую permission model.

---

# L9. Automation

Создать `technician.two@example.com`.

Notifications:

```text
New Service Request
Service Request One Day Overdue
```

Assignment Rule:

```text
Round Robin
Technician One / Technician Two
```

Assignment не меняет Status и не расширяет Level 1 permissions.

Target Date — conditional automation input.

Assignment Rule site-specific.

---

# L10. Web Form

```text
Report a Facility Issue
```

Изучить Guest временно, затем final authenticated mode.

Два create proof:

```text
Requester via Desk
→ доказательство Role Permission Create + Level 1 intake fields

Website User via Web Form
→ доказательство отдельной Web Form intake capability
```

`Login Required` = authentication, не role gate.

`Apply Document Permissions` проверяется как existing-document permission behavior; create authorization им не доказывается.

Final:

```text
Allow Edit = No
```

Это также не позволяет Web Form `ignore_permissions` update обходить Level 1 content protection.

---

# L11. Portability

Поставляются:

```text
Standard source
Roles
Workflow States/Actions/Workflow
Custom DocPerm Level 0 + Level 1
```

Не поставляются universal fixtures:

```text
Users
User Permission
Share
Assignment Rule tied to users
working data
```

Clean-site acceptance отдельно доказывает:

```text
Requester Desk create + no post-create Write
Technician Workflow + no Level 1 content Write
Supervisor content Write + no Delete
Workflow
Web Form separate intake
```

После проверки:

```bash
bench use facility-ops.localhost
```

---

# Labs A–F

```text
A Child Table
B DocStatus
C Auto Repeat
D Customize Form
E Print/PDF
F special fields/views
```

Labs не расширяют core domain и не ослабляют финальную permission model без явного temporary mutation/rollback.

---

# Финальный gate

```text
L5
→ Level 0 + Level 1 permissions не ослаблены позже

L7
→ Technician может вести state machine
→ Technician не получает content write
→ UI guard не выдаётся за ACL

L9
→ assignment не выдаётся за authorization

L10
→ Web Form create отделён от Role Create
→ final edit disabled
→ ignore_permissions update path закрыт

L11
→ Level 0/1 Custom DocPerm восстановлены на clean site
→ Desk и Web Form create-path проверены отдельно
→ portable core отделён от site policy
```

После design-consistency выполняется execution-аудит на чистом `v16.32.0`.
