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

Final Desk permissions:

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

Final Web Form:

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

Финальный output:

```text
Requester = append-only after insert
Technician = general Read/Write
Supervisor = manage without Delete
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

Requester Create сохраняется для local new doc; после Save server `Write = No`.

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

Assignment не меняет Status.

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
→ доказательство Role Permission Create

Website User via Web Form
→ доказательство отдельной Web Form intake capability
```

`Login Required` = authentication, не role gate.

`Apply Document Permissions` проверяется только как existing-document permission behavior; create authorization им не доказывается.

Final:

```text
Allow Edit = No
```

---

# L11. Portability

Поставляются:

```text
Standard source
Roles
Workflow States/Actions/Workflow
Custom DocPerm
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
Desk Role Permission create/no-write
Supervisor no-delete
Workflow
Web Form intake
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

Labs не расширяют core domain без отдельного решения.

---

# Финальный gate

```text
L5 permissions
→ не ослаблены позже

L7 workflow
→ не выдаёт UI guard за ACL

L9 assignment
→ не выдаётся за authorization

L10 Web Form
→ create отделён от Role Create
→ final edit disabled

L11
→ оба create-path проверены отдельно
→ portable core отделён от site policy
```

После design-consistency выполняется execution-аудит на чистом `v16.32.0`.
