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

L11 доказывает clean-site portability, а не произвольную co-installation совместимость.

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

Standard metadata `Service Request` уже содержит:

```text
status → Permission Level 0 + Read Only

subject
location
equipment
description
priority
target_date
attachment
→ Permission Level 1
```

---

# 3. Universal app configuration

Fixtures:

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

Custom Permissions Level 0 и Level 1 поставляются exported customizations.

---

# 4. Site-specific configuration

Не является universal:

```text
Users
User Permission
Share
Assignment Rule с concrete Users
```

Main-site Rule:

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

Process names:

```text
States:  New / Accepted / In Progress / Resolved / Closed
Actions: Accept / Start Work / Resolve / Close
```

Web Form:

```text
Allow Editing After Submit = No
```

---

# 7. Проверить финальную permission model до экспорта

## Service Request Level 0

```text
Requester
Read = Yes
Write = No
Create = Yes
Delete = No
If Owner = Yes

Technician
Read = Yes
Write = Yes
Create = No
Delete = No

Supervisor
Read = Yes
Write = Yes
Create = Yes
Delete = No
Report = Yes
Export = Yes
```

## Service Request Level 1

Для content fields:

```text
subject
location
equipment
description
priority
target_date
attachment
```

проверить:

```text
Requester
Read = Yes
Write = Yes

Technician
Read = Yes
Write = No

Supervisor
Read = Yes
Write = Yes
```

Если Technician Level 1 Write = Yes, Requester Level 0 Write = Yes или Supervisor Delete = Yes — L11 не начинать.

---

# 8. Экспортировать Custom Permissions

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

# 9. Проверить custom JSON

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

`service_request.json` должен содержать **финальную**, а не временную L5 matrix.

Минимальные gates:

```text
Level 0:
Requester Write = 0
Requester Delete = 0
Technician Delete = 0
Supervisor Delete = 0

Level 1:
Requester Read/Write = 1/1
Technician Read/Write = 1/0
Supervisor Read/Write = 1/1
```

Custom Permissions и Standard field `permlevel` — разные части модели:

```text
DocField.permlevel
→ к какому уровню относится field

Custom DocPerm.permlevel
→ какие роли имеют read/write этого уровня
```

---

# 10. Fixtures в hooks.py

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

---

# 11. Что не fixture

Не добавлять:

```text
User
User Permission
DocShare
Assignment Rule
working Facility Location / Equipment / Service Request
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

# 12. Export fixtures

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost export-fixtures --app facility_ops
```

---

# 13. Проверить fixtures

Не должно быть runtime users/data.

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

# 14. Проверить Workflow fixture

| State | Only Allow Edit For |
|---|---|
| New | Facility Supervisor |
| Accepted | Facility Technician |
| In Progress | Facility Technician |
| Resolved | Facility Supervisor |
| Closed | Facility Supervisor |

Напоминание:

```text
Only Allow Edit For
= Desk guard

Level 0 Role Permission
= document authority

Level 1 Permission
= business field authority
```

---

# 15. Commit поставки

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

---

# 16. Создать clean site

```bash
cd ~/frappe/facility-ops-bench

bench new-site facility-ops-clean.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Database старого site не копировать.

---

# 17. install-app и migrate

```bash
bench --site facility-ops-clean.localhost install-app facility_ops
bench --site facility-ops-clean.localhost list-apps
```

Exact `v16.32.0` install flow уже синхронизирует source, fixtures, customizations и dashboards.

Затем:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

Это convergence/update test, не «вторая половина установки».

---

# 18. Переключиться на clean site

```bash
bench use facility-ops-clean.localhost
```

---

# 19. Проверить Standard metadata

Должны существовать три core DocType.

`Service Request.status`:

```text
Options:
New
Accepted
In Progress
Resolved
Closed

Read Only = Yes
Permission Level = 0
```

Content fields:

```text
Subject
Location
Equipment
Description
Priority
Target Date
Attachment
```

должны иметь:

```text
Permission Level = 1
```

Также:

```text
Equipment.notes → Permission Level 1
```

Если field-level metadata не приехала — portability провалена ещё до проверки ролей.

---

# 20. Проверить fixtures

Transitions:

```text
New → Accept → Accepted
Accepted → Start Work → In Progress
In Progress → Resolve → Resolved
Resolved → Close → Closed
```

`New.only_allow_edit_for`:

```text
Facility Supervisor
```

---

# 21. Критическая проверка Custom DocPerm Level 0

На clean site:

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

---

# 22. Критическая проверка Custom DocPerm Level 1

На Permission Level 1 `Service Request`:

```text
Facility Requester
Read = Yes
Write = Yes

Facility Technician
Read = Yes
Write = No

Facility Supervisor
Read = Yes
Write = Yes
```

Это обязательная часть packaging acceptance, а не косметическая настройка формы.

---

# 23. Проверить Standard UI/config

Должны существовать:

```text
Facility Operations Control
Service Requests Overview
Open Requests
High Priority Requests
Closed Requests
Service Requests by Status
New Service Request
Service Request One Day Overdue
Report a Facility Issue
```

---

# 24. Проверить Web Form configuration

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

Поля сохраняют H-01.

Критическая граница:

```text
Web Form new insert
≠ Role Permission Create
≠ Permission Level proof
```

Exact `v16.32.0` Web Form создаёт новый target Document с `ignore_permissions=True`.

Поэтому Level 0/1 portability всегда доказываем отдельно через Desk users.

---

# 25. Доказать отсутствие старого runtime state

Не должно быть старых Users, User Permission, Share, Assignment Rule, ToDo или business Documents.

---

# 26. Создать clean-site Users

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

`web.clean@example.com` специально не получает Facility Requester: Web Form test должен доказать отдельный intake path.

---

# 27. Создать clean working data

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

# 28. Proof A — Requester Desk Create + append-only

Под:

```text
requester.clean@example.com
```

через **Desk** создать:

```text
Subject:     Clean site desk request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Description: Desk Role Permission portability test
Priority:    Medium
```

Ожидается:

```text
Create проходит
Status = New
Owner = requester.clean@example.com
```

Этот positive proof одновременно подтверждает:

```text
Level 0 Create = Yes
Level 1 Write = Yes
```

потому что Mandatory content находится на Level 1.

После Save изменить Description.

Ожидается отказ на повторный document save:

```text
Level 0 Write = No
```

---

# 29. Proof B — Supervisor content authority

Под Supervisor открыть Requester заявку.

Изменить:

```text
Priority
Target Date
```

и сохранить.

Ожидается успех:

```text
Level 0 Write = Yes
Level 1 Write = Yes
```

Затем:

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

# 30. Proof C — Technician Workflow без content Write

Под:

```text
technician.clean@example.com
```

проверить, что Technician видит:

```text
Description
Priority
Target Date
Location
Equipment
```

но Level 1 content не редактируется штатным permission-aware path.

Выполнить:

```text
Start Work
→ In Progress

Resolve
→ Resolved
```

Ожидается успех Workflow.

Ключевой proof:

```text
Technician Level 0 Write + status Level 0
→ transitions работают

Technician Level 1 Write = No
→ business content не становится writeable
```

Если Technician может обычным permission-aware save изменить Description/Priority — packaging acceptance провалена.

---

# 31. Manual ToDo boundary

На clean site Assignment Rule отсутствует.

Поэтому:

```text
Workflow Close
≠ automatic manual ToDo Close
```

Technician завершает manual ToDo отдельно.

---

# 32. Close + no-delete proof

Под Supervisor:

```text
Close
→ Status = Closed
```

После этого Supervisor не должен иметь обычный Delete этой Service Request.

---

# 33. Workspace

Под Supervisor проверить `Facility Operations Control` и L8 artifacts на clean data.

---

# 34. Proof D — Web Form intake capability

Под:

```text
web.clean@example.com
```

открыть:

```text
http://facility-ops-clean.localhost:8000/facility-request
```

Создать:

```text
Subject:     Clean site web request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Description: Web Form intake portability test
Priority:    High
Attachment:  небольшой файл
```

Проверить в Desk:

```text
Owner = web.clean@example.com
Status = New
```

Это proof:

```text
Standard Web Form + authenticated intake
```

Это **не** proof Role Permission или Level 1 permission, потому что Web Form insert использует отдельный `ignore_permissions=True` path.

Проверить:

```text
Allow Editing After Submit = No
→ Web Form не даёт update Level 1 content после создания
```

---

# 35. Сравнить четыре proof

```text
Requester / Desk
→ Level 0 Create + Level 1 intake + post-create no-Write

Supervisor / Desk
→ Level 1 content Write

Technician / Desk + Workflow
→ Level 0 state transition + Level 1 no-Write

Website User / Web Form
→ separate authenticated intake capability
```

Если это описывается как один общий permission mechanism — L11 академически не принят.

---

# 36. Assignment Rule на новом site

После основной acceptance при желании создать локальный Rule с clean Users.

Это site-specific configuration.

---

# 37. Повторный migrate

```bash
bench --site facility-ops-clean.localhost migrate
```

App configuration и clean runtime data должны сохраниться.

Повторно проверить Level 0/1 Custom DocPerm: migrate не должен возвращать временную L5 matrix.

---

# 38. Git после clean site

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Clean Users/Locations/Equipment/Requests/ToDo не должны менять Git.

---

# 39. Portability map

```text
facility_ops Git
│
├── Standard source
│   └── DocField permlevel metadata
├── fixtures
└── exported Custom DocPerm
    ├── Level 0
    └── Level 1

clean site DB
│
├── local Users
├── local runtime data
└── optional local Assignment Rule
```

---

# 40. Вернуть основной site

```bash
cd ~/frappe/facility-ops-bench
bench use facility-ops.localhost
```

---

# 41. State contract L11

## Preconditions

```text
L5 Level 0 + Level 1 permission model
L7 Accepted/Accept workflow
L10 final Allow Edit = No
Git clean
```

## Output proof

```text
Requester Desk create works
Requester post-create save blocked
Supervisor Level 1 content write works
Technician Workflow works without Level 1 content write
Supervisor Delete blocked
Web Form Website User create works as separate intake capability
Web Form update disabled
runtime data not copied
```

---

# 42. Приёмка L11

L11 принят, если:

- Standard source устанавливается на clean site;
- Service Request content fields восстановлены как Permission Level 1;
- `status` восстановлен как Level 0 + Read Only;
- fixtures содержат `Accepted/Accept`, не legacy `Assigned/Mark Assigned`;
- `New.only_allow_edit_for = Facility Supervisor`;
- exported Custom DocPerm восстанавливает exact Level 0 matrix;
- exported Custom DocPerm восстанавливает exact Level 1 matrix;
- Requester clean через Desk создаёт заявку и не может повторно save после insert;
- Supervisor clean может менять Level 1 content, но не Delete Service Request;
- Technician clean выполняет Workflow transitions, но не получает Level 1 content Write;
- Website User clean без Facility Requester создаёт через Web Form;
- Web Form create не называется доказательством Role Permission/Permission Level;
- `Apply Document Permissions` не приписывается к create authorization;
- final Web Form `Allow Edit = No`;
- old runtime state не приехал;
- manual ToDo не смешан с Workflow Close;
- clean Equipment использует допустимую Category;
- repeat migrate сохраняет runtime data и permission configuration;
- работа второго site не меняет Git;
- active site возвращён на `facility-ops.localhost`.

Главный вывод:

```text
app ≠ database copy
Level 0 ≠ Level 1 ≠ Workflow
Desk Create ≠ Web Form Create
portable core ≠ site-specific operating policy
```
