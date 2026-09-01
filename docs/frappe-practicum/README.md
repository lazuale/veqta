# Практикум Frappe Framework 16

Курс изучает Frappe через одно небольшое приложение `facility_ops`.

Учебный сценарий:

```text
место
→ оборудование
→ заявка
→ ответственность
→ процесс
→ контроль
```

Ядро ограничено тремя DocType:

```text
Facility Location (Tree)
        │
        ├────────► Equipment
        │              │
        └──────────────┴────────► Service Request
```

`Service Request` может относиться к конкретному Equipment или только к месту.

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

Собственную бизнес-логику на Python/JavaScript в базовом маршруте не пишем.

Поэтому курс принципиально различает:

```text
server-enforced guarantee
structural invariant
UI/process guard
deployment policy
```

Формальная модель: **[INVARIANTS.md](INVARIANTS.md)**.

## Основные DocType

### Facility Location

Tree структуры мест.

### Equipment

Карточка единицы оборудования.

`Equipment.location` означает текущее размещение.

### Service Request

Центральный рабочий Document.

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

`Service Request.location` означает место события. Оно не обязано навсегда совпадать с будущим `Equipment.location`.

Базовый процесс:

```text
New
 ↓
Accepted
 ↓
In Progress
 ↓
Resolved
 ↓
Closed
```

`Accepted` означает, что Supervisor принял заявку в рабочий процесс.

Это **не** синоним `Assigned To`.

## Роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Главное разделение:

```text
Permission = доступ
Assignment = ответственность
Workflow   = состояние процесса
```

Назначение выполняется штатным `Assign To → ToDo`, а не полем исполнителя.

Assignment не считается authorization boundary.

## Основной маршрут

| Урок | Результат | Главные механизмы |
|---|---|---|
| [L0](projects/00-lab/README.md) | настоящий `facility_ops` | Bench, app, site, Module, Developer Mode, Desk, Git |
| [L1](projects/01-locations/README.md) | структура мест | Standard DocType, Tree, Documents, Naming |
| [L2](projects/02-equipment/README.md) | Equipment | Field Types, Link, Form/List, Title/Search, Track Changes |
| [L3](projects/03-data/README.md) | рабочие данные | Filters, Import, Export, Bulk Edit |
| [L4](projects/04-service-request/README.md) | Service Request | Links, data invariants, Status, Attachments |
| [L5](projects/05-users-permissions/README.md) | доступ | User, Role, Role Permission, If Owner, Permission Level, User Permission, Share |
| [L6](projects/06-collaboration/README.md) | ответственность | Assign To, ToDo, Comments, Timeline, Tags, Kanban |
| [L7](projects/07-workflow/README.md) | управляемый процесс | Workflow, Allowed Role, Condition, enforcement границы |
| [L8](projects/08-control-workspace/README.md) | контроль | Report Builder, Number Card, Chart, Workspace |
| [L9](projects/09-automation/README.md) | automation | Notification, Assignment Rule, scheduler |
| [L10](projects/10-web-form/README.md) | authenticated intake | Web Form create/read-only final mode |
| [L11](projects/11-portability/README.md) | clean-site portability | fixtures, customizations, install/migrate, deployment boundary |

## Финальный Web Form

Финальная форма намеренно:

```text
Login Required = Yes
Show List = Yes
Allow Editing After Submit = No
```

`Allow Edit` изучается в L10 временно и отключается, чтобы Web Form не оставался parallel editor поверх Workflow.

## Лаборатории

Отдельно: **[индекс лабораторий](labs/README.md)**.

- [Lab A — Child Table](labs/a-child-table/README.md)
- [Lab B — DocStatus](labs/b-docstatus/README.md)
- [Lab C — Auto Repeat](labs/c-auto-repeat/README.md)
- [Lab D — Customize Form](labs/d-customize-form/README.md)
- [Lab E — Print / PDF](labs/e-print-pdf/README.md)
- [Lab F — специальные возможности](labs/f-special-features/README.md)

Лаборатория не обязана оставлять новый domain object. При этом presentation configuration, например Standard Print Format, может остаться осознанно.

## Версия и источники

Приоритет:

1. фактический стенд `v16.32.0`;
2. exact source tag `v16.32.0`;
3. официальная документация;
4. moving `version-16` только для будущих изменений.

## Документы

- [ARCHITECTURE.md](ARCHITECTURE.md) — итоговая архитектура;
- [INVARIANTS.md](INVARIANTS.md) — формальная модель гарантий и enforcement layers;
- [ROADMAP.md](ROADMAP.md) — последовательность реализации;
- [MATRIX.md](MATRIX.md) — реально покрытые механизмы;
- [SCOPE.md](SCOPE.md) — границы Core/Labs/Later;
- [REFERENCES.md](REFERENCES.md) — exact-source карта.

Начало: **[L0 — Основа приложения](projects/00-lab/README.md)**.
