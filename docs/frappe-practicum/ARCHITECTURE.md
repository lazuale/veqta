# Архитектура учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Формальные гарантии: [INVARIANTS.md](INVARIANTS.md).

Главный принцип:

```text
каждая гарантия должна иметь реальный enforcement layer
```

---

# 1. Core domain

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Только три постоянных business DocType.

---

# 2. Facility Location

Tree структуры мест.

---

# 3. Equipment

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

Status:

```text
Active
Out of Service
Retired
```

`Equipment.location` = текущее размещение.

`Equipment.notes` после L5 — Permission Level 1, доступен для write Supervisor.

---

# 4. Service Request

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

`Service Request.location` = historical event location.

---

# 5. Temporal semantics

```text
Service Request.location
≠ обязана навсегда совпадать
Equipment.location
```

Исторический факт заявки не переписывается из-за будущего перемещения Equipment.

---

# 6. Независимые оси

```text
DATA
PERMISSION
FIELD ACCESS
ASSIGNMENT
PROCESS
```

```text
Permission  → можно ли работать с Document
Field Access→ какие business fields можно менять
Assignment  → кто отвечает
Process     → какой Workflow state
```

---

# 7. Level 0 document permission

Final Service Request:

```text
Requester
→ Create Yes
→ Read own Yes
→ Write/Delete No

Technician
→ Read/Write Yes
→ Create/Delete No

Supervisor
→ Read/Write/Create Yes
→ Delete No
→ Report/Export Yes
```

Requester Desk intake = append-only after insert.

---

# 8. Level 1 business content protection

После L5 поля:

```text
subject
location
equipment
description
priority
target_date
attachment
```

имеют:

```text
Permission Level = 1
```

`status` остаётся Level 0.

Role matrix Level 1:

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

Почему это работает:

```text
Requester Level 0 Create
+ Requester Level 1 Write
→ может заполнить новый Document

Requester Level 0 Write No
→ после insert не может повторно save

Technician Level 0 Write
+ Technician Level 1 Write No
→ может участвовать в Workflow
→ не сохраняет изменения business content через permission-aware save
```

Exact `Document.validate_higher_perm_levels()` сбрасывает high-permlevel values, для которых у текущего пользователя нет write access, перед DB write.

Это server-side permission layer штатного save/insert.

---

# 9. Граница Permission Level

Если операция явно выполняется с:

```text
ignore_permissions=True
```

Permission Level enforcement пропускается.

Поэтому architecture не утверждает, что Permission Level защищает от доверенного server code, который сознательно bypass permissions.

Это особенно важно для Web Form insert.

---

# 10. Assignment

```text
Service Request
→ Assign To / Assignment Rule
→ ToDo
→ User
```

```text
Assignment ≠ authorization
```

Основные Technician имеют совместимый base access, чтобы assignment не создавал неожиданные DocShare exceptions.

---

# 11. Accepted

```text
Accepted
= Supervisor принял заявку в процесс
```

Не является синонимом assignment.

---

# 12. Workflow

```text
New
 │ Accept / Supervisor
 ▼
Accepted
 │ Start Work / Technician
 ▼
In Progress
 │ Resolve / Technician
 ▼
Resolved
 │ Close / Supervisor
 ▼
Closed
```

Все states `docstatus = 0`.

Desk edit roles:

```text
New         → Supervisor
Accepted    → Technician
In Progress → Technician
Resolved    → Supervisor
Closed      → Supervisor
```

Technician state form может быть Workflow-editable, но Level 1 business fields остаются read-only для его роли.

---

# 13. Enforcement stack

```text
Level 0 Role Permission
→ document create/read/write/delete

Permission Level 1
→ business field read/write

Workflow Allowed Role / Condition
→ server state transition

Only Allow Edit For
→ Desk state guard

Status Read Only
→ UI guard
```

Это не пять названий одного механизма, а разные уровни.

---

# 14. Closed

Closed terminal в Workflow; рабочие роли no-delete.

Absolute immutability через любой API — Later.

---

# 15. Analytics

Report/Cards/Chart/Workspace читают существующий Service Request и не создают новую data/permission model.

---

# 16. Automation

Assignment Rule создаёт ToDo и не меняет status.

Target Date — conditional input.

Rule-owned ToDo close — main-site policy, не Workflow invariant.

---

# 17. Desk create vs Web Form create

## Desk

```text
Requester
→ Level 0 Create
→ Level 1 Write заполняет business fields
→ after insert Level 0 Write No
```

## Web Form

Exact `v16.32.0`:

```text
new target doc
→ insert(ignore_permissions=True)
```

Следовательно Web Form insert обходит Role Permission и high Permission Level validation.

Это отдельная trusted intake capability.

Поэтому Web Form field list — explicit allow-list безопасных intake fields.

---

# 18. Web Form final

```text
Published = Yes
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

`Login Required` = authentication, not role authorization.

`Allow Edit = No` критичен, потому что owner update иначе также способен использовать `ignore_permissions=True` и обойти field-level hardening.

---

# 19. Threat model

Website accounts с доступом к published authenticated form = trusted internal reporters.

Public-untrusted или role-restricted portal admission — Later.

---

# 20. Packaging

```text
Standard source
→ DocTypes + UI/config

fixtures
→ Roles + Workflow

exported customizations
→ Custom DocPerm Level 0 + Level 1

site-specific
→ Users / Share / User Permission / Assignment Rule
```

L11 обязан восстановить и проверить обе permission layers.

---

# 21. Clean-site proof

Отдельно:

```text
Desk Requester
→ Role Create + Level1 field input + post-save no Write

Technician
→ Workflow works + Level1 content stays protected

Supervisor
→ Level1 content edit + no Delete

Website User
→ separate Web Form intake
```

---

# 22. Итог

```text
Facility Location
      │
      ├── Equipment
      │
      └── Service Request
              │
              ├── Level0 document permissions
              ├── Level1 business-field permissions
              ├── ToDo / Assignment
              ├── Workflow
              ├── Notifications
              └── Web Form intake
```

Стальная архитектура = **минимальная модель + наименьшие необходимые права + точное разделение native enforcement layers**.
