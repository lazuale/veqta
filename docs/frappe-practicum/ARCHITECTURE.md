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

# 2. Service Request

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

`Equipment.location` = current equipment location.

Жёсткого вечного equality нет.

---

# 3. Независимые оси

```text
DATA
DOCUMENT AUTHORITY
CONTENT AUTHORITY
STATE-FIELD AUTHORITY
ASSIGNMENT
WORKFLOW TRANSITIONS
```

Ни одна ось не выводится автоматически из другой.

---

# 4. Level 0 — document authority

Final `Service Request`:

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

# 5. Level 1 — business content authority

Поля:

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

Role matrix:

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

Requester Level 1 Write нужен для заполнения нового Document.

После insert Level 0 Write No блокирует повторный save.

Technician Level 0 Write не означает право переписывать content.

Exact `validate_higher_perm_levels()` защищает high-permlevel fields на ordinary permission-aware insert/save.

---

# 6. Level 2 — process-state field authority

```text
Service Request.status
→ Permission Level = 2
```

Role matrix:

```text
Requester   → Read only
Technician  → Read/Write
Supervisor  → Read/Write
```

Зачем отдельный уровень:

```text
business content
≠ process state
```

Requester не должен выбирать process state даже при создании заявки.

Default:

```text
status = New
```

На ordinary permission-aware insert отсутствие Requester Level 2 Write не даёт ему штатной authority установить другое process-state value.

До L7 Technician/Supervisor могут менять Status как обычный Select, что позволяет доказать отсутствие state machine.

После L7 Level 2 Write остаётся необходимой field authority, а Workflow добавляет transition authority.

---

# 7. Почему четыре слоя не избыточны

```text
Level 0
→ можно ли вообще сохранить Document

Level 1
→ можно ли менять исходные/рабочие реквизиты

Level 2
→ можно ли менять поле состояния

Workflow
→ разрешён ли именно этот переход состояния
```

Пример Technician после L7:

```text
Level 0 Write = Yes
Level 1 Write = No
Level 2 Write = Yes
Allowed Workflow transition = Yes/No по state/action/role
```

Поэтому Technician может вести процесс, но не переписывает заявку.

---

# 8. Assignment

```text
Service Request
→ Assign To / Assignment Rule
→ ToDo
→ User
```

```text
Assignment ≠ authorization
Assignment ≠ Level 1/2 permission
```

ToDo показывает ответственность.

---

# 9. Accepted

```text
Accepted
= Supervisor принял заявку в рабочий процесс
```

Не означает наличие конкретного ToDo.

---

# 10. Workflow

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

`status` после L7 также:

```text
Read Only = Yes
```

как UI guard.

---

# 11. Enforcement stack

```text
Level 0 Role Permission
→ document create/read/write/delete

Permission Level 1
→ business content read/write

Permission Level 2
→ status field read/write

Workflow Allowed Role / Condition
→ server transition validation

Only Allow Edit For
→ Desk state guard

Status Read Only
→ UI guard
```

---

# 12. Closed

Closed — terminal Workflow state.

Рабочие роли не имеют Delete.

Absolute immutability через любой API — Later.

---

# 13. Automation

Assignment Rule создаёт ToDo, не меняет status и не расширяет Level 1/2 authority.

Target Date = Level 1 conditional automation input.

Rule-owned ToDo close = main-site policy, не Workflow invariant.

---

# 14. Desk create vs Web Form create

## Desk Requester

```text
Level 0 Create
+ Level 1 Write
+ Level 2 Read only / default New
→ корректный новый Service Request
```

После insert:

```text
Level 0 Write No
```

## Web Form

Exact `v16.32.0`:

```text
new target doc
→ insert(ignore_permissions=True)
```

Поэтому Web Form insert — отдельная trusted intake capability и не является proof Level 0/1/2 permissions.

`Status` не включён в Web Form fields, поэтому используется default `New`.

---

# 15. Web Form final

```text
Published = Yes
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

`Login Required` = authentication, not role authorization.

`Allow Edit = No` закрывает bypass update path, который иначе мог бы использовать `ignore_permissions=True` и обходить Level 1/2 protection.

---

# 16. Packaging

```text
Standard source
→ DocTypes + field permlevels + Standard UI/config

fixtures
→ Roles + Workflow

exported customizations
→ Custom DocPerm Level 0 + Level 1 + Level 2

site-specific
→ Users / Share / User Permission / Assignment Rule
```

---

# 17. Clean-site proof

Отдельно доказываются:

```text
Requester Desk
→ Create + Level1 input + status New + no post-save Write

Technician
→ content read-only + Level2 state authority + Workflow transitions

Supervisor
→ content/state authority + no Delete

Website User
→ separate Web Form intake capability
```

---

# 18. Labs

Лаборатории не должны ослаблять:

```text
Level 0 document matrix
Level 1 content matrix
Level 2 status matrix
Workflow
```

Временный business-content field/table получает явный Permission Level и удаляется при rollback.

---

# 19. Итог

```text
Facility Location
      │
      ├── Equipment
      │
      └── Service Request
              │
              ├── Level 0 document authority
              ├── Level 1 content authority
              ├── Level 2 status authority
              ├── ToDo / Assignment
              ├── Workflow transition authority
              ├── Notifications
              └── Web Form intake
```

Стальная архитектура = **минимальная модель + least privilege + точное разделение native enforcement layers**.
