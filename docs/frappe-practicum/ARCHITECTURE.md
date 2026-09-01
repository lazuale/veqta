# Архитектура учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Этот документ описывает итоговую архитектуру приложения после анализа инвариантов.

Формальный реестр гарантий: **[INVARIANTS.md](INVARIANTS.md)**.

Главный принцип:

```text
лучше честная ограниченная гарантия,
чем удобная формулировка,
которую Frappe серверно не обеспечивает
```

---

# 1. Цель приложения

`facility_ops` — маленькое учебное приложение:

```text
места
→ оборудование
→ заявки
→ ответственность
→ процесс
→ контроль
→ внешний intake
```

Это не ERP, CMMS или Service Desk.

Постоянное предметное ядро:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Только эти три DocType обязательны для доменной модели.

---

# 2. Facility Location

Tree DocType.

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

`location_name` определяет понятное имя узла.

Nested-set infrastructure поддерживает Frappe.

---

# 3. Equipment

| Поле | Тип | Mandatory |
|---|---|---:|
| Equipment Code | Data | Yes |
| Equipment Name | Data | Yes |
| Location | Link → Facility Location | Yes |
| Category | Select | Yes |
| Status | Select | Yes |
| Serial Number | Data | No |
| Commissioning Date | Date | No |
| Photo | Attach Image | No |
| Notes | Small Text | No |

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

Naming:

```text
field:equipment_code
```

`Equipment.location` означает **текущее размещение Equipment**.

---

# 4. Service Request

| Поле | Тип | Mandatory | Default |
|---|---|---:|---|
| Subject | Data | Yes | |
| Location | Link → Facility Location | Yes | |
| Equipment | Link → Equipment | No | |
| Description | Text | Yes | |
| Priority | Select | Yes | Medium |
| Status | Select | Yes | New |
| Target Date | Date | No | |
| Attachment | Attach | No | |

Priority:

```text
Low
Medium
High
```

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

Naming:

```text
SR-.#####
```

Title:

```text
subject
```

Track Changes включён.

---

# 5. Семантика Location без ложной связанности

```text
Service Request.location
= место события / проблемы

Equipment.location
= текущее размещение Equipment
```

Не вводим hard invariant:

```text
Service Request.location == Equipment.location
```

Причина — время.

```text
заявка создана в Room 101
↓
оборудование позже перемещено в Warehouse
↓
историческое место заявки должно остаться Room 101
```

Учебные данные при создании делаем логичными, но не строим ложную вечную зависимость.

---

# 6. Четыре независимые оси

Архитектура намеренно разделяет:

```text
DATA
→ Location / Equipment / Description / Priority

PERMISSION
→ кто имеет право работать с Document

ASSIGNMENT
→ кому поручена конкретная работа

PROCESS
→ в каком состоянии Service Request
```

Нельзя выводить одну ось из другой.

---

# 7. Permission — security boundary

Основные роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Role Permission Manager задаёт серверный базовый доступ.

Учебная модель:

```text
Requester
→ Read Location / Equipment
→ Create Service Request
→ Read/Write own Service Request через If Owner

Technician
→ Read Location / Equipment
→ Read/Write Service Request

Supervisor
→ управляет рабочими данными
→ Report / Export / Import где предусмотрено
```

`User Permission` и `Share` изучаются временно в L5 и не остаются ограничением основных Technician.

---

# 8. Assignment — ответственность, а не ACL

Штатная модель:

```text
Service Request
→ Assign To / Assignment Rule
→ ToDo
→ User
```

Не создаём поле:

```text
Assigned Technician
```

Ключевой инвариант:

```text
Assignment
≠ authorization
```

Наличие ToDo показывает ответственность и рабочую очередь.

Role Permission определяет базовое право работать с Document.

Если будущий продукт потребует:

```text
редактировать может только конкретный assignee
```

это требует отдельной server-side permission/validation архитектуры следующего уровня.

В базовом no-own-code курсе такую гарантию не имитируем.

---

# 9. Почему state Accepted

Старое имя `Assigned` было семантически опасным:

```text
Status = Assigned
```

выглядело как гарантия:

```text
существует конкретный ToDo / assignee
```

Frappe не создаёт такого hard coupling.

Поэтому state называется:

```text
Accepted
```

и означает только:

```text
Supervisor принял заявку в рабочий процесс
```

Assignment остаётся отдельным механизмом.

---

# 10. Workflow

```text
New
 │ Accept / Facility Supervisor
 ▼
Accepted
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

Все states:

```text
docstatus = 0
```

Workflow State Field:

```text
Service Request.status
```

Второго state field нет.

---

# 11. Три уровня Workflow enforcement

## Role Permission

```text
server access boundary
```

## Transition Allowed Role / Condition

```text
server transition boundary
```

`get_transitions()` и `validate_workflow()` проверяют допустимость state change.

## Only Allow Edit For

```text
state-dependent Desk editability
```

Не считаем его самостоятельной ACL.

То же относится к:

```text
status → Read Only
```

Это хороший UI guard, но server state transition защищает сам Workflow.

---

# 12. Closed

```text
Closed
= terminal Workflow state
```

У него нет следующего transition.

Но базовый курс **не обещает**:

```text
Closed Document физически неизменяем любым API
```

Для абсолютной state-dependent immutability нужна отдельная server validation policy.

Track Changes нужен для аудита допустимых коррекций.

---

# 13. Kanban

L6 временно использует:

```text
Service Request Status Board
```

После L7 доска удаляется.

Причина:

```text
Kanban field update
→ обычный save
→ Workflow validation
```

но:

```text
Kanban move
≠ Workflow Action lifecycle
```

Финальный процесс управляется Workflow Actions.

---

# 14. Контроль работы

L8 создаёт представления над теми же Documents:

```text
Service Requests Overview    → Report Builder
Open Requests                → Number Card
High Priority Requests       → Number Card
Closed Requests              → Number Card
Service Requests by Status   → Dashboard Chart
Facility Operations Control  → Workspace
```

```text
Service Request
= данные

Report/Card/Chart/Workspace
= способы чтения и навигации
```

---

# 15. Automation

Standard Notifications:

```text
New Service Request
Service Request One Day Overdue
```

Assignment Rule основного site:

```text
Service Request Auto Assignment
Rule = Round Robin
Users = Technician One / Technician Two
```

После auto assignment нормальное состояние:

```text
Assigned To = Technician
Status = New
```

Supervisor отдельно выполняет:

```text
Accept
```

---

# 16. Почему основные Technician имеют одинаковый базовый доступ

`Assign To` в `v16.32.0` при отсутствии доступа assignee может:

```text
создать DocShare
```

а при отключённом sharing — завершиться Missing Permission.

Чтобы Assignment не менял access model скрытыми исключениями:

```text
оба основных Technician
→ имеют одинаковый Role-based Service Request access
```

Поэтому Location User Permission L5 остаётся временным experiment.

---

# 17. Target Date — conditional automation input

`Target Date` Optional.

Если заполнен:

```text
Assignment Rule ToDo.date
→ следует Target Date

One Day Overdue
→ может сработать через +1 day
```

Если пуст:

```text
Due Date не обещается
Overdue trigger неприменим
```

Это условный, а не глобальный инвариант.

---

# 18. Main-site Close Condition

На основном site L9:

```text
Assignment Rule Close Condition
= status == "Closed"
```

может закрывать Rule-owned ToDo.

Но это:

```text
site operating policy
```

а не свойство Workflow.

На clean site L11 без Assignment Rule ручной ToDo живёт своим lifecycle и при необходимости закрывается отдельно.

---

# 19. Web Form как intake, а не parallel editor

Standard Web Form:

```text
Report a Facility Issue
```

Финальная конфигурация:

```text
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

Смысл:

```text
Website User
→ создаёт Service Request
→ видит свои ответы
→ не продолжает редактировать рабочий Document через Web Form
```

Это устраняет параллельный owner-based update path поверх Workflow.

`Allow Edit` изучается временно в L10 и обязательно отключается.

---

# 20. Web trust model

Authenticated Website User курса — **доверенный внутренний заявитель**.

`Allow Read On All Link Options = Yes` для Location/Equipment означает осознанное раскрытие имён этих справочников такому пользователю.

Для публичного internet intake неизвестных людей эта модель не считается достаточной.

Нужен отдельный safe external catalog/permission design — Later.

---

# 21. Четыре слоя поставки

```text
1. Standard source
2. universal app configuration
3. site-specific configuration
4. working data
```

## Standard source

```text
3 core DocType
Report/Cards/Chart/Workspace
Notifications
Web Form
```

## Universal fixtures

```text
Roles
Workflow States
Workflow Action Masters
Workflow
```

## Exported customizations

```text
Custom DocPerm
```

## Site-specific

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

## Working data

```text
Locations
Equipment
Service Requests
ToDo
Comments
Files
Logs
```

---

# 22. Portability scope

L11 доказывает:

```text
clean-site portability
```

То есть `facility_ops` устанавливается на новый чистый Frappe site.

Он не доказывает автоматически:

```text
arbitrary co-installation compatibility
```

с любым набором сторонних apps и глобальных имён.

Это отдельная integration-задача.

---

# 23. install-app и migrate

В `v16.32.0` install flow выполняет первоначальную синхронизацию source/fixtures/customizations/dashboards.

Последующий:

```text
bench migrate
```

в L11 проверяет штатную повторную синхронизацию уже установленного app.

---

# 24. Лаборатории

Лаборатория может временно менять metadata, но не должна незаметно расширять core domain.

```text
Lab A → временный Child Table → удалить
Lab B → временный Submittable DocType → удалить
Lab C → Auto Repeat → cleanup → Assignment Rule вернуть
Lab D → customization experiment → rollback
Lab E → Print Format остаётся presentation config; Letter Head удалить
Lab F → временные special-feature DocType → удалить
```

Важно:

```text
domain rollback
≠ обязательно byte-identical Git rollback
```

Lab E сознательно оставляет Standard Print Format, не добавляя новую бизнес-сущность.

---

# 25. Уровни гарантий

Полная классификация находится в `INVARIANTS.md`.

Коротко:

```text
H = server-enforced
S = structural
U = UI/process guard
P = deployment/process policy
```

Нельзя повышать U/P до H только потому, что интерфейс выглядит убедительно.

---

# 26. Итоговая архитектура

```text
Facility Location
      │
      ├── Equipment
      │
      └── Service Request
              │
              ├── Permission / Roles
              ├── ToDo / Assignment
              ├── Workflow
              ├── Notifications
              └── Web Form create/read path

Service Request
      ↓
Report / Cards / Chart / Facility Operations Control
```

Архитектура считается «стальной» не потому, что запрещает всё, а потому что **каждая гарантия имеет честный enforcement layer и не зависит от выдуманной связи между механизмами Frappe**.
