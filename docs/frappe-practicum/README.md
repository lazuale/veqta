# Практикум Frappe Framework 16

Курс изучает Frappe через одно небольшое приложение `facility_ops`.

Учебный сценарий простой:

```text
место
  ↓
оборудование
  ↓
заявка
  ↓
исполнитель
  ↓
выполнение
  ↓
закрытие
```

Мы не строим ERP, CMMS или полноценный Service Desk. Ядро приложения намеренно ограничено тремя DocType:

```text
Facility Location (Tree)
        │
        ├────────► Equipment
        │              │
        └──────────────┴────────► Service Request
```

`Service Request` может относиться к конкретному оборудованию или только к месту.

## Учебный стенд

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
Frappe: v16.32.0
```

Один app развивается весь курс.

## Принцип курса

Каждый урок делает приложение полезнее и вводит только те механизмы Frappe, которые нужны для следующего рабочего шага.

```text
задача
  ↓
модель
  ↓
сборка в Frappe
  ↓
проверка
  ↓
что изменилось в app / site / Git
```

Собственную бизнес-логику на Python или JavaScript в базовой программе не пишем.

Редкие механизмы, которым нет естественного места в основном приложении, изучаются отдельными лабораториями и не усложняют ядро.

## Основные DocType

### Facility Location

Tree DocType для структуры мест:

```text
Main Site
├── Building A
│   ├── Floor 1
│   └── Floor 2
└── Warehouse
```

### Equipment

Конкретная единица оборудования.

Основные данные:

- Equipment Code;
- Equipment Name;
- Location;
- Category;
- Status;
- Serial Number;
- Commissioning Date;
- Photo;
- Notes.

### Service Request

Центральный рабочий документ.

Основные данные:

- Subject;
- Location;
- Equipment — необязательно;
- Description;
- Priority;
- Status;
- Target Date;
- Attachment.

Базовый процесс:

```text
New
 ↓
Assigned
 ↓
In Progress
 ↓
Resolved
 ↓
Closed
```

## Учебные роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Назначение конкретной работы выполняется штатным `Assign To` / `ToDo`, а не отдельным полем исполнителя.

## Основной маршрут

| Урок | Результат | Главные механизмы |
|---|---|---|
| [L0](projects/00-lab/README.md) | настоящий `facility_ops` | Bench, app, site, Module, Developer Mode, Desk, Git |
| [L1](projects/01-locations/README.md) | структура мест | Standard DocType, Tree, Documents, Naming |
| [L2](projects/02-equipment/README.md) | реестр оборудования | Field Types, Link, Form, List, Title/Search, Track Changes |
| [L3](projects/03-data/README.md) | рабочие данные | Filters, Sorting, Saved Filters, Data Import, Export, Bulk Edit |
| [L4](projects/04-service-request/README.md) | Service Request | рабочий DocType, Links, Status, Priority, Attachments |
| [L5](projects/05-users-permissions/README.md) | пользователи и доступ | User, Role, Permissions, If Owner, Permission Level, User Permission, Share |
| [L6](projects/06-collaboration/README.md) | совместная работа | Assign To, ToDo, Comments, Timeline, Tags, Kanban |
| [L7](projects/07-workflow/README.md) | управляемый процесс | Workflow, Workflow State, Transition, Workflow Action |
| [L8](projects/08-control-workspace/README.md) | контроль работы | Report Builder, Number Card, Dashboard Chart, Workspace |
| [L9](projects/09-automation/README.md) | автоматизация | Notification, Assignment Rule, scheduler |
| [L10](projects/10-web-form/README.md) | внешний ввод | Web Form, Guest, Website User, permissions, attachments |
| [L11](projects/11-portability/README.md) | переносимость | metadata, fixtures, customizations, clean site, migrate |

## Лаборатории

Отдельно от ядра: **[индекс лабораторий](labs/README.md)**.

- **[Lab A — Child Table](labs/a-child-table/README.md)**;
- **[Lab B — Draft / Submit / Cancel / Amend / DocStatus](labs/b-docstatus/README.md)**;
- **[Lab C — Auto Repeat](labs/c-auto-repeat/README.md)**;
- **[Lab D — Customize Form / Custom Field / Property Setter / Export Customizations](labs/d-customize-form/README.md)**;
- **[Lab E — Print / Print Format / Letter Head / PDF](labs/e-print-pdf/README.md)**;
- **[Lab F — специальные Field Types и представления](labs/f-special-features/README.md)**.

Лаборатория не обязана оставлять новую сущность в итоговом приложении.

## Версия и источники

Базовая версия курса — **Frappe Framework v16.32.0**.

Приоритет проверки:

1. фактический стенд v16.32.0;
2. исходники тега `v16.32.0`;
3. официальная документация Frappe;
4. `version-16` только для отслеживания будущих изменений.

## Документы

- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура приложения;
- [ROADMAP.md](ROADMAP.md) — реализация по урокам;
- [MATRIX.md](MATRIX.md) — покрытие механизмов Frappe;
- [SCOPE.md](SCOPE.md) — границы базового курса;
- [REFERENCES.md](REFERENCES.md) — источники проверки.

Начало курса: **[L0 — Основа приложения](projects/00-lab/README.md)**.
