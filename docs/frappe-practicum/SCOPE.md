# Границы базового практикума

Базовая версия: **Frappe Framework v16.32.0**.

Практикум изучает Frappe через `facility_ops`.

Предметное ядро:

```text
Facility Location
Equipment
Service Request
```

Архитектурная основа: [../frappe-architecture-standard/README.md](../frappe-architecture-standard/README.md).

Точные технические гарантии курса: [INVARIANTS.md](INVARIANTS.md).

---

# 1. Главная граница Core

Основной маршрут сначала изучает штатные возможности Frappe без собственной бизнес-логики на Python/JavaScript.

Допустимы:

```text
metadata
Role Permission
Permission Level
Workflow
Assignment Rule
Notification
Web Form
Report / Workspace
fixtures
Export Customizations
штатные expressions/conditions
```

Это **педагогическое ограничение**, а не правило архитектуры Frappe.

На следующем уровне совершенно допустимы:

```text
Controller
hooks
Server Script
Client Script
whitelisted methods
service modules
Background Jobs
Realtime API
custom API
```

если задача действительно требует программной ответственности.

---

# 2. Как определяется scope механизма

Механизм попадает в Core или Lab не потому, что «надо покрыть всё», а если ученик может увидеть его самостоятельный смысл на живом приложении.

```text
Core
→ нужен для развития одного рабочего facility_ops

Lab
→ важный штатный механизм, но его постоянное добавление исказило бы предметную модель

Later
→ требует собственного программного слоя, более сложной интеграции или отдельного продвинутого курса
```

---

# 3. Источники и версия

Для инструкций курса приоритет:

1. фактический стенд `v16.32.0`;
2. exact tag `v16.32.0`;
3. официальная документация;
4. `version-16` — для будущих изменений курса.

Практикум не переключается на новую patch-версию только потому, что она вышла. Version-sensitive сценарии сначала повторно проверяются.

---

# 4. Core data

`Service Request`:

Обязательные:

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

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

Семантика:

```text
Service Request.location = место события
Equipment.location       = текущее место оборудования
```

Поэтому вечного equality между ними нет.

---

# 5. Что не входит в постоянное предметное ядро

Без доказанной необходимости не создаём:

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
Task Comment
Task History
Attachment Registry
```

Часть этих задач уже выражается штатными механизмами Frappe. Остальные могут стать нормальными `DocType` в другом приложении, если получат самостоятельную ответственность.

---

# 6. Permissions scope

Core изучает:

```text
User / System User / Website User / Guest
Role
Role Permission Manager
Read / Write / Create / Delete
Report / Export / Import
If Owner
Permission Level
User Permission
Share
```

## Level 0 — Document authority

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

## Permission Level 1 — business content

```text
subject
location
equipment
description
priority
target_date
attachment
```

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

Это **case-specific решение facility_ops**. Оно выражает требование «Technician ведёт процесс, но не переписывает исходную заявку».

## Status

До L7:

```text
status → Permission Level 0
```

и является обычным `Select` для пользователей с `Document Write`.

После L7:

```text
status → тот же field
Workflow → server transition authority
Read Only → UI guard
```

Отдельный Permission Level для состояния в Core не вводится.

## Что остаётся Later в permissions

```text
Permission Types [v16+] для собственных действий
custom has_permission
permission_query_conditions
assignee-only authorization
сложная динамическая policy model
```

`Permission Type` штатный, но требует программного действия, которое курс Core пока не пишет.

---

# 7. Collaboration scope

Core:

```text
Assign To
ToDo
Due Date
Comments
Timeline
Tags
Kanban
Track Changes / Version
Attachments
```

Ключевая граница:

```text
Assignment = responsibility
Assignment ≠ authorization
Assignment ≠ Workflow state
```

Assignee-only authorization — Later.

---

# 8. Workflow scope

Core:

```text
обычный Status до Workflow
Workflow
Workflow State
Workflow Action Master
Transition
Allowed Role
Condition
Only Allow Edit For
существующий status как Workflow State Field
```

Процесс:

```text
New → Accepted → In Progress → Resolved → Closed
```

После L7:

```text
status = Read Only в стандартной Form
Workflow = server transition gate
```

`Only Allow Edit For` остаётся Desk guard, а не отдельной ACL.

`Closed` — terminal Workflow state, но абсолютная неизменяемость через любой возможный серверный путь — Later.

`Is Submittable / DocStatus` не навязывается этой заявке и изучается отдельно в Lab B.

---

# 9. Analytics scope

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
role access to presentation objects
```

Курс не создаёт отдельную аналитическую предметную модель ради простого контроля.

Later:

```text
Query Report
Script Report
внешний BI/OLAP слой
```

---

# 10. Automation scope

Core:

```text
Notification
System Notification
Days After
Assignment Rule
Round Robin
Due Date Based On
Close Condition
scheduler-triggered standard automation
```

Optional:

```text
Load Balancing
```

Core **не учит созданию собственной Background Job**.

Later:

```text
frappe.enqueue
Background Jobs
enqueue_after_commit
собственные scheduled_events
идемпотентность программных задач
```

Automation не выдаёт дополнительные права и не заменяет Workflow.

---

# 11. Web scope

Core:

```text
Standard Web Form
Published
Route
временный Guest experiment
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
Published = Yes
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

Главные выводы:

```text
Login Required
= authentication boundary
≠ role-specific business authorization

Web Form create
= отдельный intake path
≠ доказательство Desk Role Permission
```

Role-restricted/public-untrusted portal architecture — Later.

---

# 12. Packaging scope

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

Universal application state:

```text
3 core DocType
field permlevel 1
Reports / Cards / Chart / Workspace
Notifications
Web Form
Roles
Workflow
Custom DocPerm Level 0/1
```

Site-specific:

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

Core заканчивается ручной clean-site acceptance.

Later:

```text
FrappeTestCase
bench run-tests
automated lifecycle / permission / migration tests
```

Автоматизированные тесты появляются тогда, когда у приложения появляется собственная логика, которую действительно нужно защищать, а не ради повторного тестирования самого Framework.

---

# 13. Labs

```text
A Child Table
B DocStatus
C Auto Repeat
D Customize Form
E Print/PDF
F special fields/views + DocType Layout [v16+]
```

Lab, меняющая `Service Request`, обязана вернуть:

```text
Level 0 document matrix
Level 1 content matrix
Workflow
```

Лаборатория изучает механизм и затем убирает временную предметную сущность, если она не нужна приложению.

---

# 14. Later

Следующий уровень курса:

```text
Server Script
custom Python Controller
Client Script / custom JS
Permission Types [v16+]
custom has_permission / permission_query_conditions
assignee-only authorization
hard state immutability
role-restricted/public-untrusted Web Form/Portal
REST / whitelisted methods / Webhooks
Background Jobs / enqueue_after_commit
Realtime API
Query / Script Reports
Virtual DocType
automated Frappe tests
complex multi-app integration
production hardening
```

Эти темы не считаются «менее нативными». Они требуют программного или эксплуатационного контекста, которого в базовом no-code маршруте ещё нет.

---

# 15. Exit criterion

Ученик должен уметь различить:

```text
Document
Field / Link / Child
Role Permission
Permission Level
Workflow
Assignment / ToDo
Web Form
App-owned configuration
Site-specific configuration
working data
```

И главное — на новом требовании отвечать не «какую таблицу или скрипт написать», а:

> **какой штатный механизм Frappe уже владеет этой ответственностью и где проходит его граница?**
