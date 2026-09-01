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

Эти правила не должны нарушаться ни одним последующим уроком:

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
10. После L11 активным site снова становится `facility-ops.localhost`, чтобы Labs продолжали основной стенд.

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

## Создаём

Tree DocType:

```text
Facility Location
```

Пример дерева:

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

## Изучаем

- Standard DocType своего app;
- Tree;
- Documents;
- Naming;
- generated metadata;
- Git.

---

# L2. Equipment

## Создаём

```text
Equipment
```

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

## Изучаем

- Link;
- Form/List;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- naming `field:equipment_code`.

---

# L3. Работа с данными

## Изучаем

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

## Практика

Импортировать 10 дополнительных Equipment (`EQ-0010`–`EQ-0019`), проверить связанные Location/Select values и доказать, что Documents не являются source app.

---

# L4. Service Request

## Создаём

```text
Service Request
```

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

## Изучаем

- рабочий Document;
- mandatory/optional Link;
- Attach;
- naming `SR-.#####`;
- Track Changes;
- обычный Select Status до Workflow.

Все дальнейшие примеры создания Service Request обязаны соблюдать эти Mandatory fields.

---

# L5. Пользователи и права

## Постоянные роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

## Постоянные пользователи

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

`technician.two@example.com` в L5 не создаётся.

## Изучаем

- User / System User;
- Role;
- Role Permission Manager;
- Read / Write / Create / Delete;
- Report / Export / Import;
- If Owner;
- Permission Level;
- User Permission;
- Share.

## Практика

1. Настроить права на три core DocType.
2. Доказать `If Owner` двумя Requester.
3. `Equipment.notes` перевести на Permission Level 1 и дать Level 1 Supervisor.
4. Создать **временного** `technician.restricted@example.com`.
5. На нём проверить User Permission `Room 101` для Service Request.
6. Одну Room 102 заявку точечно открыть через Share.
7. Удалить Share и User Permission.
8. Отключить temporary Restricted Technician.
9. Доказать, что `technician.one@example.com` после L5 снова имеет обычную Role-based область Service Request без Location-фильтра.

## Причина cleanup

```text
User Permission / Share
= изучаем механизм

но не оставляем случайное ограничение
в рабочей модели следующих уроков
```

Иначе глобальный Assignment Rule L9 способен назначить Technician документ, который он не может открыть.

---

# L6. Совместная работа

## Изучаем

- Assign To;
- ToDo;
- Due Date;
- Comments;
- Timeline;
- Tags;
- Kanban.

## Практика

1. Supervisor назначает Service Request `technician.one@example.com`.
2. Найти созданный ToDo.
3. Доказать `Assignment ≠ Status`.
4. Добавить Comment и посмотреть Timeline.
5. Закрыть ToDo и доказать, что Service Request не закрывается автоматически.
6. Проверить повторное/duplicate assignment поведение.
7. Добавить полезные Tags.
8. Создать Kanban:

```text
Service Request Status Board
```

по полю `status`.
9. Проверить одинаковые permissions в List/Form/Kanban.

Основной Technician не ограничен конкретной Location.

---

# L7. Workflow

## Используем существующее поле

```text
Service Request.status
```

как единственный:

```text
Workflow State Field
```

`workflow_state` не создаётся.

## Процесс

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

## Практика

- `status → Read Only`;
- 5 Workflow State;
- 4 Workflow Action Master;
- `Service Request Workflow`;
- Role/state restrictions;
- temporary condition `doc.priority == "High"` и обязательный rollback;
- сравнение Kanban field update с `apply_workflow`;
- удаление `Service Request Status Board` после сравнения.

Workflow управляет состоянием, Assignment продолжает отвечать за человека.

---

# L8. Контроль работы

## Создаём

```text
Report Builder:   Service Requests Overview
Number Card:      Open Requests
Number Card:      High Priority Requests
Number Card:      Closed Requests
Dashboard Chart:  Service Requests by Status
Workspace:        Facility Operations
```

## Изучаем

- Report Builder;
- Filters;
- Group By / Count;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcut;
- Quick List;
- role access.

Никаких SQL/Python reports в базовом маршруте.

---

# L9. Автоматизация

## Создаём второго постоянного Technician

```text
technician.two@example.com
```

Это **первый** урок, где появляется данный User.

Перед Round Robin у обоих Technician должна быть одинаковая базовая область доступа к Service Request без постоянного Location User Permission.

## Notification

```text
New Service Request
Overdue Service Request
```

`Overdue Service Request` проверяется как точный сценарий:

```text
Days After = 1
→ один день после Target Date
```

а не как «все когда-либо просроченные».

## Assignment Rule

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

## Практика

- One → Two → One;
- ToDo Due Date из Target Date;
- Due Date synchronization;
- Assignment Rule не двигает Workflow;
- Closed закрывает связанный ToDo;
- сравнение автоматического и ручного Assign To;
- scheduler / manual handler test.

Все тестовые Service Request содержат Mandatory `Description`.

Assignment Rule остаётся site-specific и в L11 не экспортируется universal fixture.

---

# L10. Web Form

## Создаём

Standard Web Form:

```text
Report a Facility Issue
Route: facility-request
DocType: Service Request
```

## Поля

```text
Subject     Mandatory
Location    Mandatory
Equipment   Optional
Description Mandatory
Priority    Mandatory
Target Date Optional
Attachment  Optional
```

Web Form не может объявлять `Description` Optional, потому что underlying DocType требует его.

## Практика

1. Guest mode с временно фиксированным `Main Site`.
2. Mandatory test без Subject.
3. Mandatory test без Description.
4. Attachment.
5. Финальный `Login Required`.
6. Website User.
7. Show List / Allow Edit.
8. Owner boundary.
9. `Apply Document Permissions` ON/OFF.
10. Link options Location/Equipment.
11. Проверка Web Form → Assignment Rule → Workflow → Desk.

Финальный режим: authenticated, `Apply Document Permissions = No`, Status не редактируется из Web Form.

---

# L11. Переносимость

## Четыре слоя

```text
Standard source
app configuration
site-specific configuration
working data
```

## Standard source

- 3 core DocType;
- Report/Cards/Chart/Workspace;
- Notifications;
- Web Form.

## Fixtures

- Roles;
- Workflow State;
- Workflow Action Master;
- Workflow.

## Exported customizations

- Custom DocPerm для core DocType.

## Не переносим

```text
Users
User Permission
Share
Assignment Rule tied to concrete Users
working Documents
ToDo / Files / Logs
```

## Clean site

Создать:

```text
facility-ops-clean.localhost
```

Проверить `install-app`.

В `v16.32.0` `install-app` уже выполняет первоначальную синхронизацию Standard source, fixtures, customizations и dashboards.

Последующий:

```text
bench migrate
```

используется как явная проверка обычного update/convergence пути уже установленного app, а не как «обязательное продолжение неполной установки».

## Новые clean-site данные

Equipment:

```text
Equipment Code: EQ-CLEAN-001
Equipment Name: Clean Site Pump
Category: Other
```

Не использовать `Pump` как новое Select value.

Web Form request на clean site обязательно содержит `Description`.

После финальной проверки выполнить:

```bash
bench use facility-ops.localhost
```

Чтобы Labs A–F продолжили основной накопленный стенд.

---

# Лаборатории

Лаборатории изучают специальные механизмы и не обязаны менять постоянное ядро.

## Lab A — Child Table

Временный:

```text
Work Log
```

Изучаем Child DocType, Table, Editable Grid, `parent/parenttype/parentfield/idx`, затем полностью удаляем эксперимент.

## Lab B — DocStatus

Временный:

```text
Service Report
```

Изучаем Draft / Submit / Cancel / Amend / DocStatus / Allow on Submit. `Service Request` не делаем Submittable.

## Lab C — Auto Repeat

Временно включаем Auto Repeat для `Service Request`, отключаем L9 Assignment Rule на время чистого теста, проверяем scheduler/assignee, затем полностью очищаем Auto Repeat и служебный `auto_repeat` Custom Field. После лаборатории L9 Assignment Rule снова включён.

## Lab D — Customize Form

Изучаем Custom Field, Property Setter, Export Customizations и `Sync on Migrate` на `Equipment`, затем точечно возвращаем baseline. Удаление записи из exported JSON само по себе не считается гарантированным удалением уже синхронизированной кастомизации на другом site.

## Lab E — Print / PDF

Создаём Standard Print Format `Service Request Summary`, временный site-specific Letter Head, проверяем Print/PDF через chrome. Print Format остаётся в app, Letter Head после лаборатории удаляется.

## Lab F — специальные возможности

Временный полигон для редких Field Types / Single / Dynamic Link / Table MultiSelect. Calendar/Gantt проверяются на штатном `Event`, потому что собственный Calendar/Gantt в `v16.32.0` требует calendar JS configuration и не входит в no-own-JS базовый курс.

---

# Финальная приёмка всего маршрута

Практикум считается последовательным, если ученик может пройти L0 → L11 без ручного «угадывания», а входное состояние каждого урока является выходным состоянием предыдущего.

Ключевые проверки:

```text
L4 Mandatory fields
→ не нарушаются L9/L10/L11

L5 temporary User Permission
→ очищен до L6

technician.two
→ впервые создаётся L9

L9 global Round Robin
→ не назначает недоступные Technician документы

L10 Web Form
→ создаёт валидный Service Request

L11 clean site
→ использует допустимые Select values
→ после теста возвращает active site на facility-ops.localhost
```

Только после этого имеет смысл выполнять полный execution-аудит на заново поднятом стенде.