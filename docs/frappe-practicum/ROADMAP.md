# Дорожная карта практикума Frappe Framework 16

Базовая версия: **Frappe Framework v16.32.0**.

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Предметное ядро:

```text
Facility Location
Equipment
Service Request
```

---

# 1. Последовательность

```text
L0 платформа
→ L1 Location
→ L2 Equipment
→ L3 данные
→ L4 Service Request
→ L5 permissions
→ L6 collaboration
→ L7 Workflow
→ L8 control
→ L9 standard automation
→ L10 Web Form intake
→ L11 portability
```

Каждый следующий урок использует результат предыдущего:

```text
OUTPUT(Ln) ⊇ PRECONDITIONS(Ln+1)
```

Но курс не пытается добавить в основное приложение каждую возможность Frappe. Механизмы без естественного места в `facility_ops` уходят в Labs или Later.

---

# 2. Методический цикл урока

Новый механизм появляется только после требования:

```text
задача
→ какая ответственность нужна
→ штатный механизм Frappe
→ практическая настройка
→ положительная проверка
→ отрицательная проверка
→ граница механизма
→ итоговое состояние
```

Пример:

```text
нужна иерархия мест
→ Tree DocType

нужно назначить конкретного пользователя
→ Assign To / ToDo

нужно ограничить переходы статуса
→ Workflow
```

---

# 3. Итоговая модель доступа `Service Request`

Это решение конкретного учебного приложения, а не обязательный шаблон Frappe.

## Level 0 — Document

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

## Permission Level 1 — business content

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

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

## Status

До L7:

```text
status = обычный Select на Permission Level 0
```

После L7:

```text
Workflow = transition authority
status Read Only = UI guard
```

## Assignment

```text
Assignment / ToDo = responsibility
```

Итог:

```text
Role Permission    = Document authority
Permission Level 1 = content-field authority
Workflow           = transition authority
Assignment         = responsibility
```

---

# 4. Общие data invariants

Mandatory:

```text
Subject
Location
Description
Priority
```

Status values:

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

Location semantics:

```text
Service Request.location = historical event location
Equipment.location       = current location
```

---

# L0. Основа приложения

Изучаем:

```text
Bench
App
Site
Module
Developer Mode
Desk
Git
Standard DocType metadata
Document data
```

Scheduler/workers только наблюдаются как часть платформы. Собственные фоновые задачи здесь не проектируются.

Ключевой результат:

```text
Standard metadata → app source / Git
Document          → site database
```

---

# L1. Facility Location

Задача: представить иерархию мест.

Выбор:

```text
Tree DocType
```

Не создаём отдельные `Building`, `Floor`, `Room` только потому, что в предметной речи это разные слова.

Изучаем Naming и отрицательный сценарий одинаковых `name`.

---

# L2. Equipment

Добавляем самостоятельный `Equipment` и связываем его с местом через `Link`.

Ключевая граница:

```text
Link
= ссылка на самостоятельный Document
```

Track Changes используется как штатная история изменений, а не создаётся свой history registry.

---

# L3. Data operations

```text
Filters
Sorting
Saved Filters
Data Import
negative import
Export
Bulk Edit
```

Изменяем рабочие Documents, а не схему приложения.

---

# L4. Service Request

Создаём третий и последний постоянный предметный `DocType`.

Ключевые решения:

```text
Location обязательна
Equipment optional
Attach используется для файла
Track Changes используется для истории
Status пока обычный Select
Assignment ещё отсутствует
```

Отдельно доказываем:

```text
Select ≠ state machine
```

До L7 пользователь с обычным `Document Write` может сделать нелогичный переход, например `New → Closed`. Это не баг урока, а подготовка к пониманию Workflow.

---

# L5. Users and Permissions

Создаём роли и пользователей.

`Permission Level 1` вводится **не как универсальная схема**, а чтобы решить конкретное требование:

```text
Technician должен работать с заявкой
но не переписывать исходное содержание
```

Поэтому:

```text
business content → Permission Level 1
status           → Permission Level 0
```

Временно изучаем и откатываем:

```text
Delete
User Permission
Share
```

L5 сознательно **не решает допустимость переходов Status**. Эту ответственность получает Workflow только в L7.

---

# L6. Collaboration

Изучаем:

```text
Assign To
ToDo
Comments
Timeline
Tags
Kanban
```

Главные отрицательные выводы:

```text
Assignment ≠ authorization
Assignment ≠ Status
ToDo Closed ≠ Service Request Closed
Form/List/Kanban ≠ разные permission models
```

До L7 `status` остаётся обычным Select для Technician/Supervisor с `Document Write`.

---

# L7. Workflow

Проблема предыдущего состояния:

```text
Select допускает любые значения
но не описывает допустимые переходы
```

Добавляем Workflow:

```text
New --Accept/Supervisor--> Accepted
Accepted --Start Work/Technician--> In Progress
In Progress --Resolve/Technician--> Resolved
Resolved --Close/Supervisor--> Closed
```

Используем существующее поле:

```text
Workflow State Field = status
```

Не создаём второе `workflow_state` только ради Workflow.

После включения:

```text
Workflow validation
→ server transition boundary

status Read Only
→ UI guard

Only Allow Edit For
→ Desk state guard
```

`Permission Level 1` продолжает отдельно защищать content Technician.

---

# L8. Control

Создаём:

```text
Report Builder
Number Cards
Dashboard Chart
Workspace
```

Главный выбор:

```text
те же Service Request
→ разные представления и агрегаты
```

Не создаём отдельные `Analytics Request`, `Summary Table` или `Dashboard Data` ради простого контроля.

---

# L9. Standard automation

Изучаем штатные декларативные автоматизации:

```text
Notification
Assignment Rule
Round Robin
scheduler-triggered date behavior
```

Создаём второго Technician только здесь, когда он нужен для Round Robin.

Ключевые границы:

```text
Automation ≠ permission escalation
Assignment Rule ≠ Workflow
Target Date remains content field
```

Core не пишет собственную Background Job. `frappe.enqueue`, `enqueue_after_commit` и программная идемпотентность относятся к Later.

---

# L10. Web Form

`Report a Facility Issue` работает поверх того же `Service Request`.

Главная идея:

```text
канал представления/создания
≠ новая бизнес-сущность
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

Различаем:

```text
Desk create
→ ordinary Role Permission path

Web Form create
→ separate Web Form capability
```

`Login Required` означает authentication, а не специальное business permission.

Подробности exact `ignore_permissions=True` нужны для доказательства границы механизма, но ученик прежде всего должен удержать именно эту ментальную модель.

---

# L11. Portability

Разделяем:

```text
Standard source
universal app configuration
site-specific configuration
working data
```

Поставляются:

```text
Standard source
→ DocTypes + field permlevel + Standard UI/config

fixtures
→ Roles + Workflow

exported customizations
→ Custom DocPerm Level 0/1
```

На clean site вручную проверяются:

```text
Requester Desk create/read-own/no-write
Technician Level 1 content read-only + Workflow
Supervisor content/process authority + no Delete
Website User Web Form intake
```

Это проверка воспроизводимости приложения. Automated Frappe tests — Later.

---

# Labs A–F

Labs не должны менять архитектуру только ради покрытия функций.

```text
A → Child Table
B → DocStatus
C → Auto Repeat
D → Customize Form / Custom Field / Property Setter
E → Print / PDF
F → special fields/views, доступные в v16.32.0
```

Если Lab меняет `Service Request`, после rollback сохраняются:

```text
Level 0 matrix
Permission Level 1 matrix
Workflow
```

`DocType Layout` не включён в Lab F: механизм присутствует в более новом коде Frappe v16, но отсутствует в exact `v16.32.0`, на котором исполняется этот курс.

---

# Later

Следующий блок курса может начинаться только после основного маршрута:

```text
Controller / validation
Client Script / Server Script
Permission Types [v16+]
custom permission hooks
REST / whitelisted methods / Webhooks
Background Jobs / enqueue_after_commit
Realtime API
Query / Script Reports
Virtual DocType
automated Frappe tests
```

К version-dependent Later также относится `DocType Layout`: его нужно добавить в практику только после обновления базовой версии и повторной проверки стенда.

Эти механизмы не являются «нештатными». Они просто требуют ответственности или версии, которой в базовом приложении ещё нет.

---

# Финальный gate

Ученик проходит Core, если может на новом требовании объяснить:

```text
1. Какую ответственность нужно реализовать?
2. Какой штатный механизм Frappe соответствует её смыслу?
3. Что этот механизм реально гарантирует?
4. Что он НЕ гарантирует?
5. Принадлежит результат App, Site или working data?
```

Если ученик умеет только воспроизвести настройки `facility_ops`, но не может сделать этот выбор для новой задачи, практикум методически не принят.
