# Границы базового практикума

Базовая версия: **Frappe Framework v16.32.0**.

Практикум изучает Frappe через одно приложение:

```text
facility_ops
```

Постоянное ядро:

```text
Facility Location
Equipment
Service Request
```

Формальные гарантии и enforcement level: **[INVARIANTS.md](INVARIANTS.md)**.

---

# 1. Базовое правило курса

Собственную Python/JavaScript business logic в основном маршруте не пишем.

Допустимы штатные:

```text
expression fields
Workflow Conditions
Assignment Rule Conditions
hooks.py для fixtures/config
Frappe-generated files
exported customizations
```

Server Script, custom controller, custom permission hooks и Client Script остаются Later.

Поэтому курс не обещает гарантий, которые без отдельного server-side слоя невозможно честно обеспечить.

---

# 2. Источники истины

1. фактический стенд `v16.32.0`;
2. exact source tag `v16.32.0`;
3. официальная документация;
4. moving `version-16` только для будущих изменений.

---

# 3. Core domain

## Facility Location

Tree структуры мест.

## Equipment

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

`Equipment.location` — текущее размещение.

## Service Request

Mandatory:

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

`Service Request.location` — историческое место события.

Вечное hard equality с текущим `Equipment.location` не вводится.

---

# 4. Что не входит в core domain

Нет обязательных:

```text
Equipment Type
Equipment Movement
Inspection
Maintenance Work
Department
Team
Technician business entity
Requester business entity
Status reference
Priority reference
Assigned Technician field
```

Assignment использует штатный ToDo.

---

# 5. Permission scope

Core включает:

```text
User
System User
Website User
Guest
Role
Role Permission Manager
Read / Write / Create / Delete
Report / Export / Import
If Owner
Permission Level
User Permission
Share
```

Финальная `Service Request` policy:

```text
Requester
→ Create
→ Read own
→ Write No после insert
→ Delete No

Technician
→ Read/Write
→ Create/Delete No

Supervisor
→ Read/Write/Create
→ Delete No
→ Report/Export
```

Requester intake — append-only после создания.

Delete permission входит в Core как **временный L5 experiment**, но не остаётся финальной working policy.

Академическая граница:

```text
Role Permission
= server access boundary

User Permission / Share
= дополнительные access mechanisms

Assignment
= не access mechanism
```

User Permission/Share L5 временные и не остаются ограничением основных Technician.

---

# 6. Collaboration scope

Core:

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
Permission = доступ
Assignment = ответственность
Status = процесс
```

Assignee-only authorization — Later.

---

# 7. Workflow scope

Core:

```text
Status before Workflow
Workflow
Workflow State
Workflow Action Master
Transition
Allowed Role
Only Allow Edit For
Workflow Action
Condition
existing status as Workflow State Field
```

Процесс:

```text
New
→ Accept
→ Accepted
→ Start Work
→ In Progress
→ Resolve
→ Resolved
→ Close
→ Closed
```

Desk edit roles:

```text
New         → Facility Supervisor
Accepted    → Facility Technician
In Progress → Facility Technician
Resolved    → Facility Supervisor
Closed      → Facility Supervisor
```

Requester может создать новый `__islocal` Document, но после insert server `Write = No` запрещает дальнейшее редактирование.

Разделение enforcement:

```text
Allowed Role / Condition
= server transition enforcement

Only Allow Edit For
= state-dependent Desk guard

Status Read Only
= UI guard
```

Closed — terminal workflow state, но абсолютная API immutability не заявляется.

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

Не Core:

```text
Query Report
Script Report
Sum/Average как отдельная практика
BI layer
```

---

# 9. Automation scope

Core:

```text
Notification
System Notification
Notification Filters
Days After
Preview / Alerts for Today
Assignment Rule
Round Robin
Due Date Based On
Close Condition
scheduler/background jobs
manual scheduler handler test
```

Optional:

```text
Load Balancing
```

Target Date остаётся Optional, поэтому Due Date/overdue behavior — conditional invariant.

Main-site Assignment Rule содержит concrete Users и остаётся site-specific.

Основные Technician имеют одинаковый base permission, чтобы Assign To не создавал неожиданные DocShare exceptions.

---

# 10. Web scope

Core изучает:

```text
Standard Web Form
Route
Published
Guest creation experiment
Login Required
Website User
Allow Edit
Show List
Apply Document Permissions
Allow Read On All Link Options
attachments
```

Финал:

```text
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

`Allow Edit` изучается временно и выключается.

Threat model:

```text
Website User = trusted internal reporter
```

Public untrusted internet intake — Later.

---

# 11. Packaging scope

Core включает:

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
Workflow States
Workflow Actions
Workflow
Custom DocPerm
```

Site-specific:

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

L11 clean-site acceptance обязана проверить восстановление финальной permission matrix, включая:

```text
Requester post-create Write = No
все рабочие роли Service Request Delete = No
```

L11 доказывает clean-site portability, не arbitrary co-installation compatibility.

---

# 12. Main site и clean site

Main site после L9:

```text
Assignment Rule Close Condition
→ Rule-managed ToDo может закрываться при Status Closed
```

Clean site L11:

```text
Assignment Rule отсутствует
→ manual ToDo lifecycle остаётся отдельным
```

Это deployment difference, а не inconsistency core.

---

# 13. Labs

```text
Lab A → Child Table
Lab B → Submittable / DocStatus
Lab C → Auto Repeat
Lab D → Customize Form
Lab E → Print / PDF
Lab F → special field types / Event views
```

Правило:

```text
не оставлять новую domain entity без осознанного решения
```

Presentation configuration вроде Standard Print Format может остаться.

---

# 14. Later

```text
Server Script
custom Python controller
permission_query_conditions / custom has_permission
server-side state immutability validation
assignee-only authorization
Client Script / custom JS
REST/Webhooks отдельным блоком
Query/Script Reports
custom Portal/Website Pages
public external catalog architecture
custom Calendar/Gantt JS
Virtual DocType
arbitrary multi-app integration audit
production hardening
```

---

# 15. Критерий выхода

Ученик должен уметь назвать настоящий enforcement layer:

```text
что сервер гарантирует
что гарантирует metadata
что является UI guard
что является site policy
что держится обязательным rollback
```

Базовый курс корректен только если UI/policy договорённость не выдаётся за hard security invariant.
