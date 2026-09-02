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

Предметное ядро:

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

Практикум намеренно закреплён на `v16.32.0`: инструкции и проверки должны воспроизводиться на одной конкретной версии. Архитектурные принципы курса сверяются с актуальным [архитектурным стандартом Frappe](../frappe-architecture-standard/README.md), а поведение конкретного урока — с исходным кодом `v16.32.0`.

---

# Как мы учимся принимать решения

Курс не должен учить набору кнопок в отрыве от смысла. Для каждого нового требования используется один порядок:

```text
бизнес-задача
    ↓
какая ответственность нужна?
    ↓
кто должен владеть этой ответственностью?
    ↓
какой штатный механизм Frappe совпадает по смыслу?
    ↓
что он реально гарантирует?
    ↓
где заканчивается его ответственность?
    ↓
нужен ли следующий механизм?
```

В уроках это превращается в практический цикл:

```text
задача
→ архитектурный выбор
→ настройка штатного механизма
→ положительная проверка
→ отрицательная проверка
→ граница механизма
→ состояние приложения после урока
→ Git / Site ownership
```

Главный критерий — **совпадение смысла**, а не минимальное количество кликов любой ценой.

## Почему в основном маршруте почти нет собственного кода

В Core собственную бизнес-логику на Python/JavaScript не пишем. Это **методическая граница курса для начинающего**, а не архитектурный запрет Frappe.

`Controller`, hooks, whitelisted methods, сервисные модули, фоновые задачи и собственный API являются штатными средствами Frappe, когда стандартной настройки действительно недостаточно. Они переходят на следующий уровень после того, как ученик руками освоил возможности платформы из коробки.

---

# Service Request

Обязательные поля:

```text
Subject
Location
Description
Priority
```

Необязательные:

```text
Equipment
Target Date
Attachment
```

Состояния:

```text
New
Accepted
In Progress
Resolved
Closed
```

Ключевые различия:

```text
Accepted ≠ Assigned To
```

`Service Request.location` — место события, зафиксированное заявкой.

`Equipment.location` — текущее место оборудования.

---

# Права, состояние и ответственность — разные оси

В `facility_ops` используется следующая **конкретная учебная модель**. Это не универсальный шаблон для любого приложения Frappe.

## Уровень 0 — права на Document

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

## Permission Level 1 — содержательные поля

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

`Permission Level 1` здесь нужен потому, что по требованиям именно этого приложения Technician должен вести процесс, но не переписывать исходное содержание заявки.

## Status до Workflow

До L7 `Status` остаётся обычным полем `Select` на уровне 0.

Это сделано намеренно, чтобы ученик руками доказал:

```text
Select
= допустимые значения

Select
≠ state machine
```

## Workflow после L7

После L7 штатный `Workflow` становится владельцем допустимых переходов:

```text
New → Accepted → In Progress → Resolved → Closed
```

`Status` становится `Read Only` в стандартной форме как защита интерфейса, а допустимость перехода проверяет Workflow на сервере.

## Assignment

```text
Assign To / ToDo
= ответственность конкретного пользователя

Assignment
≠ разрешение на Document
≠ Workflow state
```

Итоговая ментальная модель:

```text
Role Permission    = что можно делать с Document
Permission Level 1 = какие содержательные поля можно менять
Workflow           = какие переходы состояния разрешены
Assignment / ToDo  = кому поручена работа
```

---

# Два канала создания заявки

## Desk

```text
Facility Requester
→ Create
→ Permission Level 1 Write для полей заявки
→ обычный Document insert
→ после создания Document Write = No
```

Это проверка обычной модели прав Frappe.

## Web Form

```text
authenticated Website User
→ Report a Facility Issue
→ Web Form
→ Service Request
```

В `v16.32.0` Web Form создаёт новый целевой `Document` через отдельный серверный путь с `ignore_permissions=True`.

Поэтому:

```text
Desk Create ≠ Web Form Create
```

Web Form не используется как доказательство Role Permission или Permission Level. В финальной конфигурации редактирование после отправки выключено.

---

# Основной маршрут

| Урок | Результат | Главные механизмы |
|---|---|---|
| [L0](projects/00-lab/README.md) | настоящий `facility_ops` | Bench, App, Site, Module, Developer Mode, Desk, Git |
| [L1](projects/01-locations/README.md) | структура мест | Standard DocType, Tree, Naming |
| [L2](projects/02-equipment/README.md) | оборудование | Fields, Link, Form/List, Track Changes |
| [L3](projects/03-data/README.md) | рабочие данные | Filters, Import, Export, Bulk Edit |
| [L4](projects/04-service-request/README.md) | рабочая заявка | модель данных, Status, Attachments, Track Changes |
| [L5](projects/05-users-permissions/README.md) | доступ | Role Permission, Permission Level 1, If Owner, User Permission, Share |
| [L6](projects/06-collaboration/README.md) | ответственность и совместная работа | Assign To, ToDo, Comments, Timeline, Tags, Kanban |
| [L7](projects/07-workflow/README.md) | управляемый процесс | Workflow поверх существующего Status |
| [L8](projects/08-control-workspace/README.md) | контроль | Report Builder, Number Card, Chart, Workspace |
| [L9](projects/09-automation/README.md) | штатная автоматизация | Notification, Assignment Rule, scheduler |
| [L10](projects/10-web-form/README.md) | отдельный канал приёма | Web Form, authentication boundary, create/read-only model |
| [L11](projects/11-portability/README.md) | воспроизводимое приложение | fixtures, exported customizations, clean-site acceptance |

---

# Лаборатории

Лаборатории изучают механизмы, которым не нужно постоянное место в предметной модели:

- [Lab A — Child Table](labs/a-child-table/README.md)
- [Lab B — DocStatus](labs/b-docstatus/README.md)
- [Lab C — Auto Repeat](labs/c-auto-repeat/README.md)
- [Lab D — Customize Form](labs/d-customize-form/README.md)
- [Lab E — Print / PDF](labs/e-print-pdf/README.md)
- [Lab F — специальные возможности и представления](labs/f-special-features/README.md)

Лаборатория не должна незаметно менять предметное ядро или ослаблять финальную модель прав `Service Request`.

---

# Версия и источники

Для воспроизводимого урока приоритет такой:

1. фактический учебный стенд `v16.32.0`;
2. исходный код exact tag `v16.32.0`;
3. официальная документация;
4. ветка `version-16` — для анализа новых возможностей и будущего обновления курса.

Новая patch-версия Frappe не подменяется в инструкциях автоматически. Сначала на ней повторно проходят version-sensitive проверки, затем меняют базовую версию курса.

---

# Какие документы читать ученику

Для первого прохождения достаточно:

1. этот README;
2. L0 → L11 по порядку;
3. нужные Labs после основного маршрута.

Дополнительные документы:

- [ARCHITECTURE.md](ARCHITECTURE.md) — почему учебное приложение устроено именно так;
- [ROADMAP.md](ROADMAP.md) — зависимости между уроками;
- [MATRIX.md](MATRIX.md) — какие возможности где изучаются;
- [SCOPE.md](SCOPE.md) — что относится к Core, Labs и следующему уровню.

Документы для автора курса и технического аудита, а не обязательное чтение новичка:

- [INVARIANTS.md](INVARIANTS.md) — точные гарантии и границы утверждений;
- [REFERENCES.md](REFERENCES.md) — карта официальных источников и исходного кода.

Начало практики: **[L0 — Основа приложения](projects/00-lab/README.md)**.
