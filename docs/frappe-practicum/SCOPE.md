# Границы базового практикума

Базовая версия: **Frappe Framework v16.32.0**.

Практикум изучает Frappe через одно приложение:

```text
facility_ops
```

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

Допустимы штатные expression fields, Workflow/Assignment Rule Conditions, fixtures/hooks configuration, generated files и exported customizations.

Server Script, custom controller, custom permission hooks и Client Script — Later.

Поэтому base course не обещает гарантий, которые без отдельного server layer нельзя честно обеспечить.

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
User
System User
Website User
Guest
Role
Role Permission Manager
Read/Write/Create/Delete
Report/Export/Import
If Owner
Permission Level
User Permission
Share
```

## Level 0 — document authority

Final Desk Service Request policy:

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

## Level 1 — business content authority

На Permission Level 1 находятся:

```text
subject
location
equipment
description
priority
target_date
attachment
```

`status` остаётся Level 0.

Level 1 role policy:

```text
Requester
→ Read/Write

Technician
→ Read only

Supervisor
→ Read/Write
```

Это не противоречит Requester `Write = No` на Level 0:

```text
new Document
→ Create Level 0 + Write Level 1
→ можно заполнить Mandatory business fields

saved Document
→ Level 0 Write = No
→ повторный save запрещён
```

Для Technician:

```text
Level 0 Write = Yes
→ Workflow/document save возможен

Level 1 Write = No
→ business content не должен изменяться ordinary permission-aware save
```

Exact `v16.32.0` server `validate_higher_perm_levels()` участвует в insert/save и сбрасывает недопустимые high-permlevel изменения.

Гарантия не распространяется на explicit `ignore_permissions=True` path.

Delete, User Permission и Share частично изучаются temporary и откатываются к безопасному baseline.

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
Permission = access
Assignment = responsibility
Status = process
```

Assignment не расширяет Level 1 content permission.

Assignee-only authorization — Later.

---

# 7. Workflow scope

```text
Workflow
Workflow State
Workflow Action Master
Transition
Allowed Role
Only Allow Edit For
Condition
existing status state field
```

Process:

```text
New → Accepted → In Progress → Resolved → Closed
```

Enforcement:

```text
Level 0 Role Permission      = document save/access authority
Level 1 Permission           = business field authority
Allowed Role / Condition     = server transition gate
Only Allow Edit For          = Desk guard
Status Read Only             = UI guard
```

Requester can create local New doc; after insert Level 0 `Write = No` is the hard boundary.

Technician может выполнять разрешённые Workflow transitions, не получая Level 1 Write на исходные реквизиты.

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

Query/Script Reports and separate BI layer — Later.

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

Target Date Optional, поэтому due/overdue behavior conditional.

Assignment Rule с concrete Users остаётся site-specific.

Automation не является поводом выдавать Technician Level 1 Write.

---

# 10. Web scope

Core изучает:

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

## Final mode

```text
Published = Yes
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

## Критическая граница create

Desk:

```text
System User
→ ordinary Role Permission Create
→ Permission Level validation
```

Web Form:

```text
new target Document
→ insert(ignore_permissions=True)
```

Поэтому:

```text
Web Form Create
≠ Role Permission Create
```

и Web Form insert не доказывает Level 0/Level 1 Role Permission enforcement.

`Apply Document Permissions` относится к existing-document access и не превращает new insert в ordinary Create check.

`Login Required` — authentication boundary, не role-specific authorization.

Final `Allow Edit = No` закрывает parallel Web Form update path, который иначе мог бы работать с `ignore_permissions=True` и обходить обычную Level 1 protection.

Final threat model:

```text
published authenticated Web Form
→ trusted internal website population
```

Role-restricted/public-untrusted portal intake — Later.

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
Reports/Cards/Chart/Workspace
Notifications
Web Form
Roles
Workflow
Custom DocPerm Level 0 + Level 1
```

Site-specific:

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

L11 must test separately:

```text
Desk Requester create/no-write
Technician Workflow with Level 1 content read-only
Supervisor Level 1 write + no Delete
Web Form Website User create
```

These are different permission/capability paths.

---

# 12. Main vs clean site

Main site may have Assignment Rule Close Condition.

Clean site intentionally has no Assignment Rule during portability acceptance; manual ToDo lifecycle remains separate.

---

# 13. Labs

```text
A Child Table
B DocStatus
C Auto Repeat
D Customize Form
E Print/PDF
F special fields/views
```

Domain rollback is mandatory.

Lab не должна оставлять ослабленную Service Request permission model, если это не её явно заявленный temporary experiment с rollback.

Presentation configuration может остаться сознательно.

---

# 14. Later

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

# 15. Exit criterion

Ученик должен уметь назвать для каждого механизма:

```text
server guarantee
structural rule
UI guard
conditional behavior
deployment policy
```

И отдельно различать:

```text
Level 0 document authority
Level 1 field authority
Workflow transition authority
Assignment responsibility
Web Form intake capability
```

Если эти слои смешаны в одну абстрактную «permission», практикум академически не принят.
