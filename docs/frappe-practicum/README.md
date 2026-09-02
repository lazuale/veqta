# Практикум Frappe Framework 16

Курс изучает Frappe через одно небольшое приложение `facility_ops`.

```text
место
→ оборудование
→ заявка
→ ответственность
→ процесс
→ контроль
```

Core domain:

```text
Facility Location (Tree)
        │
        ├────────► Equipment
        │              │
        └──────────────┴────────► Service Request
```

## Учебный стенд

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
Frappe: v16.32.0
```

## Принцип курса

```text
задача
→ модель
→ штатный механизм Frappe
→ проверка
→ настоящий enforcement layer
→ Git/site boundary
```

Собственную business logic на Python/JavaScript в базовом маршруте не пишем.

Формальная модель: **[INVARIANTS.md](INVARIANTS.md)**.

---

# Service Request

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

```text
Accepted ≠ Assigned To
```

`Service Request.location` = historical event location.

`Equipment.location` = current location.

---

# Роли и hardened permissions

```text
Facility Requester
Facility Technician
Facility Supervisor
```

## Level 0 — document authority

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

## Level 1 — business content

```text
Subject
Location
Equipment
Description
Priority
Target Date
Attachment
```

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

## Level 2 — process state

```text
Status
```

```text
Requester   → Read only
Technician  → Read/Write
Supervisor  → Read/Write
```

После L7 Workflow добавляет transition gate поверх Level 2.

Итог:

```text
Level 0 Permission = document authority
Level 1 Permission = content authority
Level 2 Permission = state-field authority
Workflow           = transition authority
Assignment         = responsibility
```

Requester может заполнить новый Level 1 Document, но не менять Status и не save заявку после insert.

Technician может вести process state, но не переписывать business content.

---

# Два intake-channel

## Desk

```text
Facility Requester
→ Level 0 Create
→ Level 1 Write для intake fields
→ Level 2 Status read-only / default New
→ after insert Level 0 Write No
```

## Web Form

```text
trusted authenticated Website User
→ Report a Facility Issue
→ Web Form insert
```

Exact `v16.32.0` Web Form new target Document создаётся через:

```text
insert(ignore_permissions=True)
```

Поэтому:

```text
Desk Create ≠ Web Form Create
```

Web Form submit не является доказательством Level 0/1/2 permissions.

Final Web Form:

```text
Published = Yes
Login Required = Yes
Show List = Yes
Allow Editing After Submit = No
```

`Status` в Web Form отсутствует.

Final `Allow Edit = No` не оставляет bypass update path поверх Level 1/2 protection.

---

# Основной маршрут

| Урок | Результат | Главные механизмы |
|---|---|---|
| [L0](projects/00-lab/README.md) | настоящий `facility_ops` | Bench, app, site, Module, Developer Mode, Desk, Git |
| [L1](projects/01-locations/README.md) | структура мест | Standard DocType, Tree, Naming |
| [L2](projects/02-equipment/README.md) | Equipment | Fields, Link, Form/List, Track Changes |
| [L3](projects/03-data/README.md) | рабочие данные | Filters, Import, Export, Bulk Edit |
| [L4](projects/04-service-request/README.md) | Service Request | data invariants, Status, Attachments |
| [L5](projects/05-users-permissions/README.md) | hardened access | Level 0/1/2, If Owner, User Permission, Share |
| [L6](projects/06-collaboration/README.md) | ответственность | Assign To, ToDo, Comments, Tags, Kanban |
| [L7](projects/07-workflow/README.md) | процесс | Workflow поверх Level 2 Status |
| [L8](projects/08-control-workspace/README.md) | контроль | Report, Cards, Chart, Workspace |
| [L9](projects/09-automation/README.md) | automation | Notification, Assignment Rule, scheduler |
| [L10](projects/10-web-form/README.md) | authenticated intake | separate Web Form capability; final update disabled |
| [L11](projects/11-portability/README.md) | portability | fixtures, Custom DocPerm Level 0/1/2, clean-site acceptance |

---

# Лаборатории

- [Lab A — Child Table](labs/a-child-table/README.md)
- [Lab B — DocStatus](labs/b-docstatus/README.md)
- [Lab C — Auto Repeat](labs/c-auto-repeat/README.md)
- [Lab D — Customize Form](labs/d-customize-form/README.md)
- [Lab E — Print / PDF](labs/e-print-pdf/README.md)
- [Lab F — специальные возможности](labs/f-special-features/README.md)

Lab не должна незаметно ослаблять Level 0/1/2 permission baseline.

---

# Версия и источники

Приоритет:

1. фактический стенд `v16.32.0`;
2. exact source tag `v16.32.0`;
3. официальная документация;
4. moving `version-16` только для future changes.

---

# Документы

- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура;
- [INVARIANTS.md](INVARIANTS.md) — formal guarantees;
- [ROADMAP.md](ROADMAP.md) — последовательность;
- [MATRIX.md](MATRIX.md) — coverage;
- [SCOPE.md](SCOPE.md) — Core/Labs/Later;
- [REFERENCES.md](REFERENCES.md) — exact-source map.

Начало: **[L0 — Основа приложения](projects/00-lab/README.md)**.
