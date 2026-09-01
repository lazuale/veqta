# L11. Переносимость приложения

L11 завершает основной маршрут и доказывает переносимость `facility_ops` на **новый чистый Frappe site**.

Базовая версия: **Frappe Framework v16.32.0**.

Цель:

```text
app source
+ universal configuration
        ↓
clean site
        ↓
install-app
        ↓
рабочее core без старого runtime state
```

L11 доказывает clean-site portability, а не произвольную co-installation совместимость с любым сторонним app.

---

# 1. Четыре слоя

```text
1. Standard source
2. universal app configuration
3. site-specific configuration
4. working data
```

---

# 2. Standard source

В `facility_ops` уже находятся:

```text
Facility Location
Equipment
Service Request

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

Standard objects не дублируются fixtures.

---

# 3. Universal app configuration

Fixtures должны поставить:

```text
Facility Requester
Facility Technician
Facility Supervisor

Workflow States:
New
Accepted
In Progress
Resolved
Closed

Workflow Action Masters:
Accept
Start Work
Resolve
Close

Service Request Workflow
```

Custom Permissions поставляются exported customizations.

---

# 4. Site-specific configuration

Не является universal:

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
```

Main-site L9 Rule:

```text
Service Request Auto Assignment
```

ссылается на локальных Technician One/Two и поэтому не fixture.

---

# 5. Working data

Не переносим старые:

```text
Facility Location Documents
Equipment Documents
Service Request Documents
ToDo
Comments
Tags
Files
Notification Log
Workflow Action records
```

---

# 6. Проверить исходный site

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Ожидается:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

Проверить финальные names:

```text
States:
New / Accepted / In Progress / Resolved / Closed

Actions:
Accept / Start Work / Resolve / Close
```

У Web Form:

```text
Allow Editing After Submit = No
```

У Service Request Role Permissions до экспорта:

```text
Requester → Create + Read own, Write/Delete No
Technician → Read/Write, Create/Delete No
Supervisor → Read/Write/Create, Delete No, Report/Export
```

Если эта матрица не соблюдается — L11 не начинать.

---

# 7. Экспортировать Custom Permissions

Для:

```text
Facility Location
Equipment
Service Request
```

открыть:

```text
Customize Form
→ Actions
→ Export Customizations
```

Параметры:

```text
Module to Export:          Facility Operations
Sync on Migrate:           Yes
Export Custom Permissions: Yes
Apply Module Export Filter: No
```

JSON вручную не редактировать.

---

# 8. Проверить custom JSON

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
find facility_ops/facility_operations/custom \
  -maxdepth 1 -type f -print | sort
```

Проверить:

```text
"sync_on_migrate": 1
"custom_perms"
```

Особенно убедиться, что `service_request.json` отражает финальный hardening, а не временный Delete experiment L5.

Финал должен означать:

```text
Requester Write = 0
Requester Delete = 0
Technician Delete = 0
Supervisor Delete = 0
```

---

# 9. Fixtures в hooks.py

```python
fixtures = [
    {
        "doctype": "Role",
        "filters": [["name", "in", [
            "Facility Requester",
            "Facility Technician",
            "Facility Supervisor",
        ]]],
    },
    {
        "doctype": "Workflow State",
        "filters": [["name", "in", [
            "New",
            "Accepted",
            "In Progress",
            "Resolved",
            "Closed",
        ]]],
    },
    {
        "doctype": "Workflow Action Master",
        "filters": [["name", "in", [
            "Accept",
            "Start Work",
            "Resolve",
            "Close",
        ]]],
    },
    {
        "doctype": "Workflow",
        "filters": [["name", "=", "Service Request Workflow"]],
    },
]

fixture_auto_order = True
```

Порядок зависимостей:

```text
Role
↓
Workflow State / Action Master
↓
Workflow
```

---

# 10. Что не fixture

Не добавлять:

```text
User
User Permission
DocShare
Assignment Rule
working Facility Location
working Equipment
working Service Request
ToDo
File
Notification Log
DocType
Report
Number Card
Dashboard Chart
Workspace
Notification
Web Form
```

---

# 11. Export fixtures

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost export-fixtures --app facility_ops
```

Проверить `facility_ops/fixtures`.

---

# 12. Проверить fixtures на runtime мусор и legacy names

В fixtures не должно быть:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
technician.two@example.com
supervisor.one@example.com
web.requester@example.com
technician.restricted@example.com

SR-00001
EQ-0001
```

Должны быть:

```text
Accepted
Accept
```

Не должно быть legacy process names:

```text
Assigned
Mark Assigned
```

---

# 13. Проверить Workflow configuration перед поставкой

У `Service Request Workflow` проверить:

| State | Only Allow Edit For |
|---|---|
| New | Facility Supervisor |
| Accepted | Facility Technician |
| In Progress | Facility Technician |
| Resolved | Facility Supervisor |
| Closed | Facility Supervisor |

Это должно приехать через fixture Workflow.

Напомнить:

```text
Only Allow Edit For
= Desk guard
```

Hard post-create запрет Requester обеспечивается Custom DocPerm `Write = No`.

---

# 14. Commit поставки

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff

git add \
  facility_ops/hooks.py \
  facility_ops/fixtures \
  facility_ops/facility_operations/custom

git diff --cached
git commit -m "Package facility operations configuration"
git status
```

Не добавлять database dump, passwords или site config.

---

# 15. Создать clean site

```bash
cd ~/frappe/facility-ops-bench

bench new-site facility-ops-clean.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Database старого site не копировать.

---

# 16. install-app и migrate

```bash
bench --site facility-ops-clean.localhost install-app facility_ops
bench --site facility-ops-clean.localhost list-apps
```

В exact `v16.32.0` install flow уже синхронизирует app source, fixtures, customizations и dashboards.

Затем для проверки повторного convergence path:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

Не учить ложной модели `install-app = половина установки`.

---

# 17. Переключиться на clean site

```bash
bench use facility-ops-clean.localhost
```

Открыть:

```text
http://facility-ops-clean.localhost:8000
```

---

# 18. Проверить Standard metadata

Должны существовать:

```text
Facility Location
Equipment
Service Request
```

`Service Request.status`:

```text
New
Accepted
In Progress
Resolved
Closed
```

и:

```text
Read Only = Yes
```

`Equipment.notes`:

```text
Permission Level = 1
```

---

# 19. Проверить fixtures

Роли, Workflow, States и Actions должны существовать.

Transitions:

```text
New → Accept → Accepted
Accepted → Start Work → In Progress
In Progress → Resolve → Resolved
Resolved → Close → Closed
```

`New.only_allow_edit_for` должен быть:

```text
Facility Supervisor
```

---

# 20. Критическая проверка восстановленных permissions

В Role Permission Manager на clean site проверить **точно**:

## Service Request

```text
Facility Requester
Read = Yes
Write = No
Create = Yes
Delete = No
If Owner = Yes

Facility Technician
Read = Yes
Write = Yes
Create = No
Delete = No

Facility Supervisor
Read = Yes
Write = Yes
Create = Yes
Delete = No
Report = Yes
Export = Yes
```

Если Supervisor Delete = Yes или Requester Write = Yes — exported customizations не соответствуют финальной архитектуре, и L11 провален.

---

# 21. Проверить Standard UI/config

Должны существовать:

```text
Workspace:       Facility Operations Control
Report:          Service Requests Overview
Number Card:     Open Requests
Number Card:     High Priority Requests
Number Card:     Closed Requests
Dashboard Chart: Service Requests by Status
Notification:    New Service Request
Notification:    Service Request One Day Overdue
Web Form:        Report a Facility Issue
```

---

# 22. Проверить финальный Web Form

```text
Published = Yes
Login Required = Yes
Anonymous Responses = No
Allow Multiple Responses = Yes
Allow Editing After Submit = No
Show List = Yes
Apply Document Permissions = No
Show Attachments = Yes
```

Fields:

```text
Subject     Mandatory
Location    Mandatory
Equipment   Optional
Description Mandatory
Priority    Mandatory
Target Date Optional
Attachment  Optional
```

`Status` отсутствует.

---

# 23. Доказать отсутствие старого runtime state

Не должно быть старых:

```text
Users курса
User Permission
Share
Service Request Auto Assignment
ToDo
Facility Location data
Equipment data
Service Request data
```

---

# 24. Создать clean-site Users

```text
requester.clean@example.com
→ System User → Facility Requester

technician.clean@example.com
→ System User → Facility Technician

supervisor.clean@example.com
→ System User → Facility Supervisor

web.clean@example.com
→ Website User
```

---

# 25. Создать clean working data

Location:

```text
Main Site
└── Building A
    └── Room 101
```

Equipment:

```text
Equipment Code: EQ-CLEAN-001
Equipment Name: Clean Site Pump
Location:       Room 101
Category:       Other
Status:         Active
```

---

# 26. Критический Requester acceptance

Под:

```text
requester.clean@example.com
```

создать:

```text
Subject:     Clean site request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Description: End-to-end portability and permission test
Priority:    Medium
Target Date: будущая дата или пусто
```

Ожидается:

```text
Create проходит
Status = New
Owner = requester.clean@example.com
```

Сразу после Save попытаться изменить Description.

Ожидается:

```text
Write запрещён
```

Requester при этом должен иметь возможность читать свой Document.

Это главный proof, что packaging восстановил hard intake model, а не только внешний вид Workflow.

---

# 27. Supervisor New-state acceptance

Под Supervisor открыть эту New-заявку.

Проверить:

```text
New state доступен для Desk обработки Supervisor
Requester уже не является editor сохранённой New-заявки
```

Под Supervisor выполнить:

```text
Assign To → technician.clean@example.com
Accept
```

Получить:

```text
Assigned To = technician.clean@example.com
Status = Accepted
```

---

# 28. Technician process

Под Technician:

```text
Start Work
Resolve
```

Получить:

```text
Status = Resolved
```

Technician не должен иметь Create/Delete Service Request.

---

# 29. Manual ToDo boundary на clean site

Main-site Assignment Rule отсутствует.

Поэтому нельзя ожидать:

```text
Workflow Close
→ автоматически закрывает manual ToDo
```

Technician штатно завершает свой ToDo отдельно.

Проверить:

```text
ToDo Status = Closed
Service Request Status = Resolved
```

---

# 30. Закрыть процесс и проверить no-delete

Под Supervisor:

```text
Close
→ Status = Closed
```

Затем проверить, что обычный Supervisor **не может удалить** эту рабочую Service Request.

Это отдельный hard permission proof:

```text
Closed terminal state
+
Supervisor Delete = No
```

не равен абсолютной API immutability, но рабочая роль не может стереть запись штатным Delete.

---

# 31. Проверить Workspace

Под Supervisor открыть `Facility Operations Control` и проверить Cards/Chart/Report на clean data.

---

# 32. Проверить Web Form end-to-end

Под `web.clean@example.com` открыть:

```text
http://facility-ops-clean.localhost:8000/facility-request
```

Создать:

```text
Subject:     Clean site web request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Description: Проверка переносимого Web Form
Priority:    High
Attachment:  небольшой файл
```

Проверить в Desk:

```text
Status = New
```

и отсутствие Web Form update после submit:

```text
Allow Editing After Submit = No
```

---

# 33. Assignment Rule на новом site

После основной acceptance при желании создать локальный Assignment Rule с clean Users.

Это deployment configuration, не часть proof portable core.

---

# 34. Повторный migrate

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops-clean.localhost migrate
```

Должны сохраниться:

```text
app configuration
clean Users
clean working data
```

---

# 35. Git после clean site

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Создание clean Users/Locations/Equipment/Requests/ToDo не должно менять Git.

---

# 36. Карта поставки

```text
facility_ops Git
│
├── Standard source
│   ├── DocTypes
│   ├── Reports/Cards/Chart
│   ├── Workspace
│   ├── Notifications
│   └── Web Form
│
├── fixtures
│   ├── Roles
│   ├── Workflow States
│   ├── Workflow Action Masters
│   └── Workflow
│
└── exported customizations
    └── Custom DocPerm

site database
│
├── Users
├── User Permission
├── Share
├── local Assignment Rule
├── business Documents
└── ToDo / Comments / Files / Logs
```

---

# 37. Portability scope

Доказано:

```text
facility_ops
→ устанавливается на новый clean Frappe site
```

Не доказано автоматически:

```text
facility_ops
→ бесконфликтен с любым сторонним app
```

---

# 38. Вернуть основной site

```bash
cd ~/frappe/facility-ops-bench
bench use facility-ops.localhost
```

Labs A–F продолжают основной накопленный стенд.

---

# 39. State contract L11

## Preconditions

```text
L10 final Allow Edit = No
L5 final permission matrix active
Workflow uses Accepted/Accept
Git clean
```

## Persistent app delivery

```text
Standard source
fixtures
exported Custom DocPerm
```

## Site-specific

```text
clean Users
clean runtime data
optional local Assignment Rule only after acceptance
```

## Output proof

```text
Requester can Create + Read own but cannot Write saved request
Supervisor cannot Delete Service Request
New state Desk owner = Supervisor
Workflow portable
Web Form create/read-only
runtime data not copied
```

---

# 40. Приёмка L11

L11 принят, если доказано:

- Standard source устанавливается на clean site;
- fixtures содержат `Accepted/Accept`, не `Assigned/Mark Assigned`;
- `New.only_allow_edit_for = Facility Supervisor`;
- exported customizations восстанавливают exact final Role Permission matrix;
- Requester clean реально создаёт заявку, читает её и не может переписать после Save;
- Supervisor clean реально не может удалить рабочую Service Request;
- Web Form final `Allow Edit = No`;
- старые Users/Share/User Permission/Assignment Rule/runtime data не приехали;
- manual ToDo не ошибочно связывается с Workflow Close;
- clean Equipment использует допустимую Category;
- Web Form создаёт валидный Service Request;
- повторный migrate сохраняет runtime data;
- работа второго site не меняет Git;
- portability сформулирована как clean-site portability;
- active site возвращён на `facility-ops.localhost`.

Главный вывод:

```text
app
≠ database copy

portable core
≠ site-specific operating policy
```
