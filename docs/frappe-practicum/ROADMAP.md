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

```text
OUTPUT(Ln) ⊇ PRECONDITIONS(Ln+1)
```

---

# Финальная security model

## Level 0 — Document

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

## Level 1 — Business content

Fields:

```text
subject
location
equipment
description
priority
target_date
attachment
```

Permissions:

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

## Level 2 — Process state

Field:

```text
status
```

Permissions:

```text
Requester   → Read only
Technician  → Read/Write
Supervisor  → Read/Write
```

## После L7

```text
Workflow Allowed Role / Condition
→ дополнительный server transition gate
```

Итог:

```text
Level 0 = document authority
Level 1 = business-content authority
Level 2 = process-state field authority
Workflow = concrete transition authority
Assignment = responsibility only
```

---

# Общие data invariants

Mandatory:

```text
Subject
Location
Description
Priority
```

Status values:

```text
New
Accepted
In Progress
Resolved
Closed
```

```text
Accepted ≠ Assigned To
```

Location:

```text
Service Request.location = historical event location
Equipment.location       = current location
```

---

# L0. Основа

Bench, app, site, Module, Developer Mode, Desk, Git.

---

# L1. Facility Location

Tree структуры мест.

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

---

# L3. Data operations

Filters, Sorting, Saved Filters, Data Import, negative import, Export, Bulk Edit.

Импортировать 10 дополнительных Equipment.

---

# L4. Service Request

Создать третий core DocType.

До L5 fields ещё на baseline metadata permission level; permission architecture вводится следующим уроком.

До L7 Status — обычный Select.

---

# L5. Permissions

Создать роли и основных Users.

Перестроить `Service Request`:

```text
business fields → Permission Level 1
status          → Permission Level 2
```

Создать exact Level 0/1/2 Role Permission rows.

Ключевые proofs:

```text
Requester
→ заполняет новый Level1 content
→ Status видит как New, но не выбирает произвольный Level2 state
→ после insert не save existing Document

Technician
→ Level0 document Write
→ Level1 content read-only
→ Level2 status Write

Supervisor
→ Level1 + Level2 Write
→ no Delete
```

Temporary:

```text
Supervisor Delete Yes → test → No
Restricted Technician
User Permission
Share
```

Все откатываются до L6.

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

До Workflow:

```text
Technician/Supervisor
→ могут менять Level2 Status как обычный Select

Requester
→ Level2 Write не имеет
```

Так доказательство `Select ≠ state machine` не требует давать Requester state authority.

Assignment не меняет Level 1/2 permissions.

---

# L7. Workflow

```text
New --Accept/Supervisor--> Accepted
Accepted --Start Work/Technician--> In Progress
In Progress --Resolve/Technician--> Resolved
Resolved --Close/Supervisor--> Closed
```

`status` остаётся Level 2 и становится Read Only в Desk.

Теперь для смены state нужны одновременно:

```text
Level 0 Write
Level 2 Write
valid Workflow transition
```

Technician при этом Level 1 Write не получает.

Desk edit roles:

```text
New         → Supervisor
Accepted    → Technician
In Progress → Technician
Resolved    → Supervisor
Closed      → Supervisor
```

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

Analytics не создаёт permission exceptions.

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

Automation не расширяет Level 1/2 authority.

Target Date = Level 1 conditional input.

Assignment Rule site-specific.

---

# L10. Web Form

`Report a Facility Issue`.

Final:

```text
Published = Yes
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

Desk create и Web Form insert — разные paths.

Web Form new insert использует `ignore_permissions=True`, поэтому не является proof Level 0/1/2 permissions.

`Status` в Web Form отсутствует; новый Document получает default `New`.

Final `Allow Edit = No` закрывает bypass update path поверх Level 1/2 protection.

---

# L11. Portability

Поставляются:

```text
Standard source
→ field permlevels 1/2

fixtures
→ Roles + Workflow

exported Custom DocPerm
→ Level 0 + Level 1 + Level 2
```

Clean-site proofs:

```text
Requester Desk
→ Level0 Create + Level1 input + Level2 New/read-only + no post-save Write

Technician
→ Level1 read-only + Level2 Write + Workflow works

Supervisor
→ Level1/2 Write + no Delete

Website User
→ separate Web Form intake
```

После проверки:

```bash
bench use facility-ops.localhost
```

---

# Labs A–F

Labs не должны ослаблять:

```text
Level 0 matrix
Level 1 matrix
Level 2 matrix
Workflow
```

Временный business-content field/table получает явный Permission Level и rollback.

---

# Финальный gate

```text
L5
→ exact Level0/1/2 model

L6
→ assignment не меняет authority
→ Requester не получает Status Write

L7
→ Level2 field authority + Workflow transition authority разделены
→ Technician state transitions работают без Level1 content Write

L9
→ automation не повышает permissions

L10
→ Web Form bypass create отделён от Desk permissions
→ final update Off

L11
→ Level0/1/2 metadata + Custom DocPerm восстановлены на clean site
```

После design consistency выполняется execution-аудит на фактическом `v16.32.0` стенде.
