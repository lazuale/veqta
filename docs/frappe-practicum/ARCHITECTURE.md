# Архитектура учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Формальный реестр гарантий: **[INVARIANTS.md](INVARIANTS.md)**.

Главный принцип:

```text
каждая гарантия должна иметь реальный enforcement layer
```

---

# 1. Цель и core

`facility_ops` изучает Frappe на небольшой модели:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Это не ERP, CMMS или полноценный Service Desk.

---

# 2. Facility Location

Tree структуры мест:

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

`Equipment.location` = текущее размещение.

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

Track Changes включён.

---

# 5. Temporal semantics Location

```text
Service Request.location
= историческое место события

Equipment.location
= текущее размещение Equipment
```

Не вводим вечное hard equality между ними.

---

# 6. Четыре независимые оси

```text
DATA
PERMISSION
ASSIGNMENT
PROCESS
```

Расшифровка:

```text
DATA       → что произошло и где
PERMISSION → кто имеет server access
ASSIGNMENT → кому поручена работа
PROCESS    → в каком state заявка
```

Нельзя выводить одну ось из другой.

---

# 7. Role Permission — hard access boundary Desk

Финальная `Service Request` matrix:

```text
Requester
→ Create Yes
→ Read own Yes / If Owner
→ Write No после insert
→ Delete No

Technician
→ Read/Write Yes
→ Create/Delete No

Supervisor
→ Read/Write/Create Yes
→ Delete No
→ Report/Export Yes
```

Requester Desk intake:

```text
Create
→ Save
→ далее append-only для Requester
```

Delete нормальных Service Request не является operating policy рабочих ролей.

---

# 8. Assignment — ответственность, не ACL

```text
Service Request
→ Assign To / Assignment Rule
→ ToDo
→ User
```

Не создаём собственный `Assigned Technician`.

```text
Assignment ≠ authorization
```

При недостаточном access штатный Assign To способен создать Share; поэтому main Technician получают совместимый Role-based access заранее.

---

# 9. Accepted вместо Assigned

```text
Accepted
= Supervisor принял заявку в процесс
```

Это не гарантия существования ToDo.

Поэтому нормальны независимо:

```text
Assigned To заполнен + Status New
Status Accepted + assignment менялся/отсутствует
```

---

# 10. Workflow

```text
New
 │ Accept / Supervisor
 ▼
Accepted
 │ Start Work / Technician
 ▼
In Progress
 │ Resolve / Technician
 ▼
Resolved
 │ Close / Supervisor
 ▼
Closed
```

Все states `docstatus = 0`.

Workflow State Field:

```text
Service Request.status
```

Desk edit roles:

```text
New         → Supervisor
Accepted    → Technician
In Progress → Technician
Resolved    → Supervisor
Closed      → Supervisor
```

---

# 11. Workflow enforcement layers

```text
Role Permission
= server document access

Allowed Role / Condition
= server transition gate

Only Allow Edit For
= Desk state editability

status Read Only
= UI guard
```

Requester всё ещё может создать новый local `New` Document. Exact client Workflow не делает `doc.__islocal` read-only. После insert его hard boundary — Role Permission `Write = No`.

---

# 12. Closed

Closed — terminal Workflow state.

Рабочие роли также не имеют Delete.

Но absolute field immutability через любой API в base course не обещается: для этого нужен отдельный server validation layer.

---

# 13. Kanban

L6 временно использует `Service Request Status Board`.

После L7 удаляем его как основной process UI:

```text
Kanban save
→ Workflow validation

но

Kanban move
≠ apply_workflow(Action) lifecycle
```

---

# 14. Analytics

```text
Service Requests Overview    → Report Builder
Open Requests                → Number Card
High Priority Requests       → Number Card
Closed Requests              → Number Card
Service Requests by Status   → Dashboard Chart
Facility Operations Control  → Workspace
```

Это представления существующих Documents, не новая data/permission model.

---

# 15. Automation

Notifications:

```text
New Service Request
Service Request One Day Overdue
```

Main-site Assignment Rule:

```text
Service Request Auto Assignment
Rule = Round Robin
```

После assignment:

```text
Assigned To = Technician
Status = New
```

Supervisor отдельно выполняет `Accept`.

`Target Date` остаётся Optional, поэтому due/overdue behavior условный.

Close Condition Rule-owned ToDo — main-site policy, не свойство Workflow.

---

# 16. Два create-channel после L10

Это критически разные пути.

## Desk Requester

```text
Facility Requester
→ Role Permission Create = Yes
→ ordinary Document create
→ после Save Write = No
```

## Web Form

Exact `v16.32.0` новый Web Form Document создаёт через:

```text
doc.insert(ignore_permissions=True, ...)
```

Следовательно:

```text
Web Form submission
≠ Role Permission Create
```

Это сознательная отдельная intake capability Web Form.

---

# 17. Web Form threat model

Final:

```text
Published = Yes
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = No
Apply Document Permissions = No
```

`Login Required` блокирует Guest, но не является role-specific submission authorization.

Поэтому deployment policy:

```text
authenticated website population с доступом к этой форме
= trusted internal reporters
```

Public/untrusted или role-restricted portal intake — Later.

---

# 18. Web Form existing-document access

`Apply Document Permissions` относится к работе с существующим Document:

```text
Off
→ Web Form owner/website permission model

On
→ ordinary document permissions
```

Она не превращает новый Web Form insert в Role Permission `Create` check.

`Allow Edit = No` оставляет форму create/read-only и закрывает parallel edit path поверх Workflow.

---

# 19. Link options

`Allow Read On All Link Options = Yes` для Location/Equipment сознательно раскрывает authenticated internal reporters названия общих справочников.

Это deployment trust decision.

---

# 20. Поставка

Четыре слоя:

```text
1. Standard source
2. universal app configuration
3. site-specific configuration
4. working data
```

Standard source:

```text
3 core DocType
Report/Cards/Chart/Workspace
Notifications
Web Form
```

Universal fixtures:

```text
Roles
Workflow States
Workflow Action Masters
Workflow
```

Exported customizations:

```text
Custom DocPerm
```

Site-specific:

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

---

# 21. Portability

L11 доказывает clean-site portability.

На clean site отдельно доказываются:

```text
Desk Requester Create + Read own + no Write
Supervisor no Delete
Workflow state/edit-role configuration
Website User Web Form submission
```

И эти два create-test не смешиваются:

```text
Desk create
= proof Role Permission

Web Form create
= proof Web Form intake
```

---

# 22. Labs

Labs изучают специальные механизмы с обязательным domain rollback.

Lab E может оставить Standard Print Format как presentation configuration.

---

# 23. Итог

```text
Facility Location
      │
      ├── Equipment
      │
      └── Service Request
              │
              ├── Role Permission / Desk intake
              ├── ToDo / Assignment
              ├── Workflow
              ├── Notifications
              └── Web Form authenticated intake

Service Request
      ↓
Report / Cards / Chart / Workspace
```

«Стальная» архитектура здесь означает не максимум запретов, а **отсутствие ложных связей между механизмами Frappe и точное понимание, какой слой реально обеспечивает каждую гарантию**.
