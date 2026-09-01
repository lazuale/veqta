# Дорожная карта практикума Frappe Framework 16

Базовая версия: **Frappe Framework v16.32.0**.

Практикум развивается вокруг одного учебного приложения:

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Постоянное предметное ядро:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Курс не строит ERP/CMMS/Service Desk и не добавляет сущности только ради демонстрации возможностей Frappe.

Основной принцип:

```text
сначала рабочая модель
→ потом permissions
→ потом collaboration
→ потом Workflow
→ потом аналитика
→ потом automation
→ потом web-вход
→ потом переносимость
```

Собственную бизнес-логику на Python/JavaScript в базовом маршруте не пишем. Штатные expression-поля, generated files, `hooks.py`, fixtures и exported customizations допустимы как нативные механизмы Frappe.

---

# Инварианты всего курса

1. `Service Request.location` — Mandatory.
2. `Service Request.description` — Mandatory.
3. `Service Request.equipment` — Optional.
4. `Equipment.category` допускает только:

```text
HVAC
Electrical
IT
Other
```

5. Assignment не хранится собственным полем в `Service Request`.
6. После L7 `Service Request.status` управляется Workflow и остаётся единственным state field.
7. Основные Technician после L5 не имеют постоянного Location User Permission.
8. `technician.two@example.com` впервые создаётся только в L9.
9. Assignment Rule с конкретными Users — site-specific configuration, не universal fixture.
10. Module и основной Workspace имеют разные имена:

```text
Module    = Facility Operations
Workspace = Facility Operations Control
```

11. Date-based Notification `Days After = 1` называется:

```text
Service Request One Day Overdue
```

12. После L11 активным site снова становится `facility-ops.localhost`.

---

# L0. Основа приложения

## Результат

Настоящий Bench, site и app в Developer Mode.

## Изучаем

- Bench;
- `bench new-app`;
- `bench new-site`;
- `install-app`;
- Module;
- Developer Mode;
- Desk / Awesomebar;
- структура app;
- Git.

## Приёмка

```text
facility-ops-bench
facility_ops
facility-ops.localhost
Facility Operations
Frappe v16.32.0
```

работают, app находится под Git.

---

# L1. Facility Location

Tree DocType:

```text
Facility Location
```

Пример:

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

Изучаем Standard DocType, Tree, Documents, Naming, generated metadata и Git.

---

# L2. Equipment

Поля:

| Поле | Тип |
|---|---|
| Equipment Code | Data |
| Equipment Name | Data |
| Location | Link → Facility Location |
| Category | Select |
| Status | Select |
| Serial Number | Data |
| Commissioning Date | Date |
| Photo | Attach Image |
| Notes | Small Text |

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

Изучаем Link, Form/List, Title Field, Search Fields, Quick Entry, Track Changes и naming `field:equipment_code`.

---

# L3. Работа с данными

Изучаем:

- Filters;
- Sorting текущего List View;
- Saved Filters;
- Search;
- Allow Import;
- Data Import;
- штатный template;
- negative import test;
- Export;
- Bulk Edit.

Импортировать 10 дополнительных Equipment (`EQ-0010`–`EQ-0019`) и доказать, что Documents не являются source app.

---

# L4. Service Request

| Поле | Тип | Mandatory |
|---|---|---:|
| Subject | Data | Yes |
| Location | Link → Facility Location | Yes |
| Equipment | Link → Equipment | No |
| Description | Text | **Yes** |
| Priority | Select | Yes |
| Status | Select | Yes, default New |
| Target Date | Date | No |
| Attachment | Attach | No |

Priority:

```text
Low
Medium
High
```

Status:

```text
New
Assigned
In Progress
Resolved
Closed
```

Все дальнейшие примеры создания Service Request обязаны соблюдать Mandatory fields L4.

---

# L5. Пользователи и права

Постоянные роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Постоянные пользователи:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

`technician.two@example.com` в L5 не создаётся.

Изучаем User, Role, Role Permission Manager, If Owner, Permission Level, User Permission и Share.

Практика:

1. Настроить права на три core DocType.
2. Доказать `If Owner` двумя Requester.
3. `Equipment.notes` → Permission Level 1 для Supervisor.
4. Создать временного `technician.restricted@example.com`.
5. Проверить User Permission `Room 101`.
6. Одну Room 102 заявку открыть через Share.
7. Удалить Share и User Permission.
8. Отключить Restricted Technician.
9. Доказать, что основной `technician.one@example.com` не ограничен Location.

---

# L6. Совместная работа

Изучаем Assign To, ToDo, Due Date, Comments, Timeline, Tags, Kanban.

Создаём временную доску:

```text
Service Request Status Board
```

по полю `status`.

Проверяем:

```text
Assignment ≠ Status
ToDo close ≠ Service Request close
Kanban = другое представление тех же Documents
```

Основной Technician не ограничен конкретной Location.

---

# L7. Workflow

Используется существующее поле:

```text
Service Request.status
```

как единственный Workflow State Field.

Процесс:

```text
New
 │ Mark Assigned / Facility Supervisor
 ▼
Assigned
 │ Start Work / Facility Technician
 ▼
In Progress
 │ Resolve / Facility Technician
 ▼
Resolved
 │ Close / Facility Supervisor
 ▼
Closed
```

Все states имеют `docstatus = 0`.

Практика: Read Only status, Workflow State, Workflow Action Master, Transitions, temporary Condition, сравнение Kanban-save с `apply_workflow`, затем удаление `Service Request Status Board`.

---

# L8. Контроль работы

Создаём:

```text
Report Builder:   Service Requests Overview
Number Card:      Open Requests
Number Card:      High Priority Requests
Number Card:      Closed Requests
Dashboard Chart:  Service Requests by Status
Workspace:        Facility Operations Control
```

Module остаётся:

```text
Facility Operations
```

Workspace специально имеет другое имя, чтобы не смешивать Module и рабочий экран.

Изучаем Report Builder, Filters, Group By/Count, Number Card, Dashboard Chart, Workspace, Shortcut, Quick List и role access.

---

# L9. Автоматизация

Создаём второго постоянного Technician:

```text
technician.two@example.com
```

Это первый урок, где появляется этот User.

Standard Notifications:

```text
New Service Request
Service Request One Day Overdue
```

Второе имя точно отражает:

```text
Days After = 1
```

Assignment Rule:

```text
Service Request Auto Assignment
Rule: Round Robin
Users:
  technician.one@example.com
  technician.two@example.com
```

Assign Condition:

```python
status == "New"
```

Close Condition:

```python
status == "Closed"
```

Практика: One → Two → One, Due Date synchronization, Workflow остаётся отдельным, Closed закрывает ToDo, ручной Assign To сравнивается с Assignment Rule.

Load Balancing — Optional; после теста Rule обязательно возвращается в Round Robin.

Все тестовые Service Request содержат Mandatory `Description`.

Assignment Rule остаётся site-specific и в L11 не экспортируется universal fixture.

---

# L10. Web Form

Standard Web Form:

```text
Report a Facility Issue
Route: facility-request
DocType: Service Request
```

Поля:

```text
Subject     Mandatory
Location    Mandatory
Equipment   Optional
Description Mandatory
Priority    Mandatory
Target Date Optional
Attachment  Optional
```

Практика: Guest, обязательность Subject/Description, attachment, Login Required, Website User, Show List, Allow Edit, owner boundary, Apply Document Permissions, Link options, Web Form → Assignment Rule → Workflow → Desk.

Финальный режим authenticated, Status из Web Form не управляется.

---

# L11. Переносимость

Четыре слоя:

```text
Standard source
app configuration
site-specific configuration
working data
```

Standard source:

```text
3 core DocType
Service Requests Overview
Open Requests
High Priority Requests
Closed Requests
Service Requests by Status
Facility Operations Control
New Service Request
Service Request One Day Overdue
Report a Facility Issue
```

Fixtures:

```text
Roles
Workflow State
Workflow Action Master
Workflow
```

Exported customizations:

```text
Custom DocPerm
```

Не переносим:

```text
Users
User Permission
Share
Assignment Rule tied to concrete Users
working Documents
ToDo / Files / Logs
```

На clean site `install-app` выполняет первоначальную синхронизацию; последующий `migrate` используется как проверка обычного update/convergence пути уже установленного app.

Clean-site Equipment:

```text
Equipment Code: EQ-CLEAN-001
Equipment Name: Clean Site Pump
Category: Other
```

Web Form request на clean site обязательно содержит `Description`.

После проверки:

```bash
bench use facility-ops.localhost
```

---

# Лаборатории

## Lab A — Child Table

Временный `Work Log`, Child DocType/Table/Editable Grid/parent fields, затем полный cleanup.

## Lab B — DocStatus

Временный `Service Report`; Draft/Submit/Cancel/Amend/Allow on Submit. `Service Request` не делаем Submittable.

## Lab C — Auto Repeat

Временно включаем Auto Repeat для `Service Request`, отключаем L9 Assignment Rule на время чистого теста, затем полностью очищаем Auto Repeat и возвращаем Assignment Rule.

## Lab D — Customize Form

Custom Field, Property Setter, Export Customizations, Sync on Migrate и точечный rollback.

## Lab E — Print / PDF

Standard Print Format `Service Request Summary` остаётся в app, временный Letter Head удаляется.

## Lab F — специальные возможности

Временный metadata-полигон. Calendar/Gantt проверяются на штатном Event; собственный JS calendar config — Later.

---

# Финальная приёмка последовательности

Курс считается консистентным, если:

```text
L4 Mandatory fields
→ не нарушаются L9/L10/L11

L5 temporary permissions
→ очищены до L6

technician.two
→ впервые появляется L9

L6 Kanban
→ Service Request Status Board
→ удаляется L7

L8 Workspace
→ Facility Operations Control
→ не путается с Module Facility Operations

L9 date Notification
→ Service Request One Day Overdue
→ точно соответствует Days After = 1

L9 global Round Robin
→ не назначает недоступные документы

L10 Web Form
→ создаёт валидный Service Request

L11 clean site
→ использует допустимые Select values
→ возвращает active site на facility-ops.localhost
```

После этого выполняется отдельный execution-аудит на чистом стенде.