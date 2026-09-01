# Архитектура учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Формальный реестр гарантий: **[INVARIANTS.md](INVARIANTS.md)**.

Главный принцип:

```text
лучше честная ограниченная гарантия,
чем удобная формулировка,
которую Frappe серверно не обеспечивает
```

---

# 1. Цель приложения

`facility_ops` — небольшое учебное приложение:

```text
места
→ оборудование
→ заявки
→ ответственность
→ процесс
→ контроль
→ внешний intake
```

Это не ERP, CMMS или полноценный Service Desk.

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

Nested-set infrastructure обслуживает Frappe.

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

# 5. Семантика Location

```text
Service Request.location
= историческое место события / проблемы

Equipment.location
= текущее размещение Equipment
```

Не вводится hard invariant:

```text
Service Request.location == Equipment.location
```

Причина — время: Equipment может быть позже перемещён, а историческая Location заявки должна остаться прежней.

---

# 6. Четыре независимые оси

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

# 7. Permission — основная server security boundary

Роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Финальная permission policy для `Service Request`:

```text
Requester
→ Create = Yes
→ Read own = Yes через If Owner
→ Write = No после создания
→ Delete = No

Technician
→ Read = Yes
→ Write = Yes
→ Create/Delete = No

Supervisor
→ Read/Write/Create = Yes
→ Delete = No
→ Report/Export = Yes
```

Главное усиление:

```text
Requester intake
= append-only после insert
```

Заявитель не должен тихо переписывать уже поданную рабочую запись.

Удаление нормальных `Service Request` также не является штатной operating policy рабочих ролей. Delete изучается временно в L5 и затем откатывается.

`User Permission` и `Share` изучаются отдельно и временно.

---

# 8. Почему Requester всё ещё может создавать после L7

Workflow state `New` после L7 имеет:

```text
Only Allow Edit For = Facility Supervisor
```

Это не ломает создание Requester.

В exact `v16.32.0` client Workflow `is_read_only()` возвращает `false` для нового `doc.__islocal`, а server insert первой Workflow State не считается state transition.

Поэтому:

```text
Requester Create = Yes
→ новый Service Request создаётся

после insert
→ Role Permission Write = No
→ Requester больше не редактирует его
```

Это сильнее и точнее, чем полагаться на `Only Allow Edit For` как на ACL.

---

# 9. Assignment — ответственность, а не ACL

```text
Service Request
→ Assign To / Assignment Rule
→ ToDo
→ User
```

Не создаётся поле:

```text
Assigned Technician
```

Ключевой инвариант:

```text
Assignment
≠ authorization
```

Наличие ToDo показывает ответственность. Role Permission определяет базовый доступ.

Assignee-only authorization находится в Later.

---

# 10. Почему state `Accepted`

Состояние `Assigned` было семантически опасным, потому что выглядело как гарантия существования конкретного assignment.

Поэтому:

```text
Accepted
= Supervisor принял заявку в рабочий процесс
```

и только это.

Assignment остаётся отдельной осью.

---

# 11. Workflow

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

Desk edit roles:

| State | Only Allow Edit For |
|---|---|
| New | Facility Supervisor |
| Accepted | Facility Technician |
| In Progress | Facility Technician |
| Resolved | Facility Supervisor |
| Closed | Facility Supervisor |

Это UX/state guard, а не самостоятельная ACL.

---

# 12. Три уровня Workflow enforcement

```text
Role Permission
= server access boundary

Transition Allowed Role / Condition
= server transition boundary

Only Allow Edit For
= state-dependent Desk editability
```

Также:

```text
status → Read Only
```

является UI guard. Server-side допустимость смены состояния проверяет Workflow validation.

---

# 13. Closed

```text
Closed
= terminal Workflow state
```

У него нет следующего transition.

Рабочие роли также не имеют Delete.

Но базовый курс не обещает абсолютную физическую immutability всех полей Closed Document через любой API. Для этого потребовалась бы отдельная server validation policy.

---

# 14. Kanban

L6 временно использует:

```text
Service Request Status Board
```

После L7 доска удаляется.

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

# 15. Контроль работы

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
= рабочие данные

Report/Card/Chart/Workspace
= способы чтения и навигации
```

Они не создают отдельную permission boundary и не хранят копию данных.

---

# 16. Automation

Standard Notifications:

```text
New Service Request
Service Request One Day Overdue
```

Main-site Assignment Rule:

```text
Service Request Auto Assignment
Rule = Round Robin
Users = Technician One / Technician Two
```

После auto assignment:

```text
Assigned To = Technician
Status = New
```

Supervisor отдельно выполняет:

```text
Accept
```

---

# 17. Почему основные Technician имеют одинаковый базовый доступ

`Assign To` v16.32.0 при отсутствии доступа assignee может автоматически создать `DocShare`; при отключённом sharing — завершиться Missing Permission.

Поэтому:

```text
основные Technician
→ одинаковый Role-based Service Request access
```

Assignment не должен незаметно перестраивать access model.

---

# 18. Target Date — conditional automation input

Если `Target Date` заполнен:

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

---

# 19. Main-site Close Condition

На основном site L9:

```text
Assignment Rule Close Condition
= status == "Closed"
```

может закрывать Rule-managed ToDo.

Это site operating policy, а не свойство Workflow.

На clean site L11 без Assignment Rule manual ToDo живёт своим lifecycle.

---

# 20. Web Form — intake, а не parallel editor

Standard Web Form:

```text
Report a Facility Issue
```

Финал:

```text
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

```text
Website User
→ создаёт Service Request
→ видит свои ответы
→ не редактирует рабочий Document после submit
```

`Allow Edit` изучается временно и обязательно отключается.

---

# 21. Web trust model

Authenticated Website User курса — доверенный внутренний заявитель.

`Allow Read On All Link Options = Yes` для Location/Equipment означает осознанное раскрытие названий этих справочников этому классу пользователей.

Public untrusted intake — Later.

---

# 22. Четыре слоя поставки

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

# 23. Portability scope

L11 доказывает:

```text
clean-site portability
```

а не arbitrary co-installation compatibility с любым набором сторонних apps.

---

# 24. install-app и migrate

В `v16.32.0` install flow выполняет первоначальную синхронизацию source/fixtures/customizations/dashboards.

Последующий:

```text
bench migrate
```

проверяет повторную синхронизацию уже установленного app.

---

# 25. Лаборатории

```text
Lab A → временный Child Table → удалить
Lab B → временный Submittable DocType → удалить
Lab C → Auto Repeat → cleanup → Assignment Rule вернуть
Lab D → customization experiment → rollback
Lab E → Print Format остаётся presentation config; Letter Head удалить
Lab F → временные special-feature DocType → удалить
```

```text
domain rollback
≠ обязательно byte-identical Git rollback
```

---

# 26. Итоговая архитектура

```text
Facility Location
      │
      ├── Equipment
      │
      └── Service Request
              │
              ├── Role Permission
              ├── ToDo / Assignment
              ├── Workflow
              ├── Notifications
              └── Web Form create/read path

Service Request
      ↓
Report / Cards / Chart / Facility Operations Control
```

Архитектура считается «стальной» не потому, что запрещает всё, а потому что **каждая гарантия имеет честный enforcement layer и не зависит от выдуманной связи между механизмами Frappe**.
