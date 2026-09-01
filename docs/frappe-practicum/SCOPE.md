# Границы базового практикума

Базовая версия: **Frappe Framework v16.32.0**.

Практикум изучает Frappe через `facility_ops`.

Core domain:

```text
Facility Location
Equipment
Service Request
```

Формальные гарантии: [INVARIANTS.md](INVARIANTS.md).

---

# 1. Базовое правило

Собственную Python/JavaScript business logic в основном маршруте не пишем.

Допустимы штатные expressions, Workflow/Assignment Rule Conditions, fixtures/hooks configuration, generated files и exported customizations.

Server Script, custom controller, custom permission hooks и Client Script — Later.

---

# 2. Source of truth

1. фактический стенд `v16.32.0`;
2. exact tag `v16.32.0`;
3. официальная документация;
4. moving `version-16` только для future changes.

---

# 3. Core data

Service Request Mandatory:

```text
Subject
Location
Description
Priority
```

Optional:

```text
Equipment
Target Date
Attachment
```

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

`Service Request.location` = historical event location.

`Equipment.location` = current location.

---

# 4. Не входит в core domain

```text
Equipment Type
Equipment Movement
Inspection
Maintenance Work
Department
Team
Technician business entity
Requester business entity
Status/Priority references
Assigned Technician field
```

---

# 5. Permission scope

Core изучает:

```text
User / System User / Website User / Guest
Role
Role Permission Manager
Read/Write/Create/Delete
Report/Export/Import
If Owner
Permission Level 1
Permission Level 2
User Permission
Share
```

## Level 0 — document authority

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

## Level 1 — business content

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

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

## Level 2 — process state

```text
status → Permission Level 2
```

```text
Requester   → Read only
Technician  → Read/Write
Supervisor  → Read/Write
```

Это позволяет дать Technician process-state authority без content authority и не выдавать Requester state write на create path.

Exact `v16.32.0` high Permission Level validation участвует в ordinary insert/save; explicit `ignore_permissions=True` является bypass.

Delete, User Permission и Share частично изучаются temporary и откатываются.

---

# 6. Collaboration scope

```text
Assign To
ToDo
Due Date
Comments
Timeline
Tags
Kanban
```

```text
Assignment = responsibility
не document/content/state authority
```

Assignee-only authorization — Later.

---

# 7. Workflow scope

Core:

```text
Workflow
Workflow State
Workflow Action Master
Transition
Allowed Role
Only Allow Edit For
Condition
existing status field
```

Process:

```text
New → Accepted → In Progress → Resolved → Closed
```

После L7:

```text
status = Permission Level 2 + Read Only UI
```

Enforcement stack:

```text
Level 0 Role Permission
→ document save/access

Level 1 Permission
→ business fields

Level 2 Permission
→ status field authority

Allowed Role / Condition
→ server transition gate

Only Allow Edit For
→ Desk guard
```

Closed terminal, но absolute API immutability — Later.

---

# 8. Analytics scope

Core:

```text
Report Builder
Filters
Group By
Count
Number Card
Dashboard Chart
Workspace
Shortcut
Quick List
role access
```

Query/Script Reports и BI layer — Later.

---

# 9. Automation scope

Core:

```text
Notification
System Notification
Days After
Assignment Rule
Round Robin
Due Date Based On
Close Condition
scheduler
```

Load Balancing — Optional.

Target Date = Level 1 Optional/conditional input.

Automation не меняет Level 1/2 authority.

Assignment Rule с concrete Users site-specific.

---

# 10. Web scope

Core:

```text
Standard Web Form
Published
Route
Guest experiment
Login Required
Website User
Allow Edit
Show List
Apply Document Permissions
Allow Read On All Link Options
attachments
```

Final:

```text
Published = Yes
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

Desk:

```text
Role Permission Level 0/1/2
```

Web Form new insert:

```text
insert(ignore_permissions=True)
```

Поэтому Web Form Create не является Role Permission proof.

`Status` не входит в Web Form allow-list.

Final `Allow Edit = No` закрывает bypass update path, который иначе мог бы обходить Level 1/2 protections.

Website User = trusted internal reporter.

Role-restricted/public-untrusted admission — Later.

---

# 11. Packaging scope

Core:

```text
Standard source
universal app configuration
site-specific configuration
working data
fixtures
fixture_auto_order
export-fixtures
Export Customizations
Custom DocPerm
install-app
migrate
clean site
```

Universal:

```text
3 core DocType
field permlevels 1/2
Reports/Cards/Chart/Workspace
Notifications
Web Form
Roles
Workflow
Custom DocPerm Level 0/1/2
```

Site-specific:

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

L11 отдельно проверяет Level 0/1/2 и Web Form capability.

---

# 12. Labs

```text
A Child Table
B DocStatus
C Auto Repeat
D Customize Form
E Print/PDF
F special fields/views
```

Lab, меняющая `Service Request`, должна вернуть:

```text
Level 0 matrix
Level 1 matrix
Level 2 matrix
Workflow
```

Временный business-content field/table получает explicit Permission Level.

---

# 13. Later

```text
Server Script
custom Python controller
custom has_permission / permission query
assignee-only authorization
hard state immutability
role-restricted Web Form/portal admission
public-untrusted catalog architecture
Client Script / custom JS
REST/Webhooks separate block
Query/Script Reports
arbitrary multi-app integration audit
production hardening
```

---

# 14. Exit criterion

Ученик должен различать:

```text
Level 0 document authority
Level 1 business-content authority
Level 2 process-state authority
Workflow transition authority
Assignment responsibility
Web Form intake capability
```

Если это всё называется просто «права», практикум академически не принят.
