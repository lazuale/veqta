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

Поэтому курс различает:

```text
server-enforced guarantee
structural invariant
UI/process guard
conditional behavior
deployment policy
```

Формальная модель: **[INVARIANTS.md](INVARIANTS.md)**.

---

# Основные DocType

## Facility Location

Tree структуры мест.

## Equipment

Карточка единицы оборудования.

`Equipment.location` = текущее размещение.

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

`Service Request.location` = историческое место события.

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

`Accepted` = заявка принята Supervisor в рабочий процесс.

```text
Accepted ≠ Assigned To
```

---

# Роли и доступ

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Final Desk policy:

```text
Requester
→ Create + Read own
→ Write/Delete No after insert

Technician
→ Read/Write
→ Create/Delete No

Supervisor
→ Read/Write/Create
→ Delete No
→ Report/Export
```

Главное разделение:

```text
Permission = access
Assignment = responsibility
Workflow   = process state
```

Assignment выполняется штатным `Assign To → ToDo` и не является authorization boundary.

---

# Два intake-channel

После L10 существуют два разных create path.

## Desk

```text
Facility Requester
→ Role Permission Create
→ после Save Write = No
```

## Web Form

```text
trusted authenticated Website User
→ Report a Facility Issue
→ Web Form insert
```

Exact `v16.32.0` новый Web Form target Document создаётся через `insert(ignore_permissions=True)`.

Поэтому:

```text
Desk Create ≠ Web Form Create
```

Web Form submission не является доказательством Role Permission Create.

Final Web Form:

```text
Published = Yes
Login Required = Yes
Show List = Yes
Allow Editing After Submit = No
```

`Login Required` — authentication, не role-specific authorization.

---

# Основной маршрут

| Урок | Результат | Главные механизмы |
|---|---|---|
| [L0](projects/00-lab/README.md) | настоящий `facility_ops` | Bench, app, site, Module, Developer Mode, Desk, Git |
| [L1](projects/01-locations/README.md) | структура мест | Standard DocType, Tree, Naming |
| [L2](projects/02-equipment/README.md) | Equipment | Fields, Link, Form/List, Track Changes |
| [L3](projects/03-data/README.md) | рабочие данные | Filters, Import, Export, Bulk Edit |
| [L4](projects/04-service-request/README.md) | Service Request | data invariants, Status, Attachments |
| [L5](projects/05-users-permissions/README.md) | hardened Desk access | Role Permission, If Owner, Permission Level, User Permission, Share |
| [L6](projects/06-collaboration/README.md) | ответственность | Assign To, ToDo, Comments, Tags, Kanban |
| [L7](projects/07-workflow/README.md) | процесс | Workflow, Allowed Role, Condition, enforcement layers |
| [L8](projects/08-control-workspace/README.md) | контроль | Report, Cards, Chart, Workspace |
| [L9](projects/09-automation/README.md) | automation | Notification, Assignment Rule, scheduler |
| [L10](projects/10-web-form/README.md) | authenticated intake | Web Form create/read-only; separate create capability |
| [L11](projects/11-portability/README.md) | portability | fixtures, Custom DocPerm, clean-site dual acceptance |

---

# Лаборатории

- [Lab A — Child Table](labs/a-child-table/README.md)
- [Lab B — DocStatus](labs/b-docstatus/README.md)
- [Lab C — Auto Repeat](labs/c-auto-repeat/README.md)
- [Lab D — Customize Form](labs/d-customize-form/README.md)
- [Lab E — Print / PDF](labs/e-print-pdf/README.md)
- [Lab F — специальные возможности](labs/f-special-features/README.md)

Lab не обязана оставлять новый domain object. Presentation configuration может остаться осознанно.

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
