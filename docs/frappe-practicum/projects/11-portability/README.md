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

Custom Permissions поставляются exported customizations.

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

Проверить process names:

```text
States:  New / Accepted / In Progress / Resolved / Closed
Actions: Accept / Start Work / Resolve / Close
```

Web Form:

```text
Allow Editing After Submit = No
```

Service Request Role Permissions:

```text
Requester → Create + Read own, Write/Delete No
Technician → Read/Write, Create/Delete No
Supervisor → Read/Write/Create, Delete No, Report/Export
```

Если это не так — L11 не начинать.

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

`service_request.json` должен отражать **финальную**, а не временную L5 matrix:

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

---

# 10. Что не fixture

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

# 11. Export fixtures

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost export-fixtures --app facility_ops
```

---

# 12. Проверить fixtures

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

# 13. Проверить Workflow fixture

| State | Only Allow Edit For |
|---|---|
| New | Facility Supervisor |
| Accepted | Facility Technician |
| In Progress | Facility Technician |
| Resolved | Facility Supervisor |
| Closed | Facility Supervisor |

Напоминание:

```text
Only Allow Edit For = Desk guard
Requester post-create Write No = Role Permission hard boundary
```

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

Exact `v16.32.0` install flow уже синхронизирует source, fixtures, customizations и dashboards.

Затем:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

Это convergence/update test, не «вторая половина установки».

---

# 17. Переключиться на clean site

```bash
bench use facility-ops-clean.localhost
```

---

# 18. Проверить Standard metadata

Должны существовать три core DocType.

`Service Request.status`:

```text
New
Accepted
In Progress
Resolved
Closed
```

и `Read Only = Yes`.

`Equipment.notes`:

```text
Permission Level = 1
```

---

# 19. Проверить fixtures

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

# 20. Критическая проверка Role Permissions

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

Requester Write Yes или Supervisor Delete Yes = провал packaging acceptance.

---

# 21. Проверить Standard UI/config

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

# 22. Проверить Web Form configuration

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
```

Exact `v16.32.0` Web Form создаёт новый target Document с `ignore_permissions=True`.

`Apply Document Permissions` относится к existing-document permission path, а не превращает insert в обычный Role Create check.

---

# 23. Доказать отсутствие старого runtime state

Не должно быть старых Users, User Permission, Share, Assignment Rule, ToDo или business Documents.

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

`web.clean@example.com` специально **не получает Facility Requester**: Web Form test должен доказывать отдельный intake path, а не дублировать Desk permission test.

---

# 25. Создать clean working data

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

# 26. Proof A — Desk Role Permission Create

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

После Save изменить Description.

Ожидается отказ:

```text
Write = No
```

Это proof именно:

```text
exported Custom DocPerm / Role Permission
```

---

# 27. Supervisor New-state handling

Под Supervisor открыть Desk-заявку.

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

```text
Start Work
Resolve
```

Получить `Status = Resolved`.

Technician не имеет Create/Delete.

---

# 29. Manual ToDo boundary

На clean site Assignment Rule отсутствует.

Поэтому:

```text
Workflow Close
≠ automatic manual ToDo Close
```

Technician завершает manual ToDo отдельно.

---

# 30. Close + no-delete proof

Под Supervisor:

```text
Close
→ Status = Closed
```

После этого Supervisor не должен иметь обычный Delete этой Service Request.

---

# 31. Workspace

Под Supervisor проверить `Facility Operations Control` и L8 artifacts на clean data.

---

# 32. Proof B — Web Form intake capability

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
Standard Web Form + authenticated intake работает после установки app
```

Это **не** proof Role Permission `Create`, потому что Website User не имеет Facility Requester и Web Form insert использует отдельный create path.

Проверить также:

```text
Allow Editing After Submit = No
→ Web Form не даёт update
```

---

# 33. Сравнить два proof

```text
requester.clean через Desk
→ доказывает Role Permission Create + post-create Write No

web.clean через Web Form
→ доказывает отдельную authenticated Web Form intake capability
```

Если эти тесты описываются как один и тот же permission mechanism — L11 академически не принят.

---

# 34. Assignment Rule на новом site

После основной acceptance при желании создать локальный Rule с clean Users.

Это site-specific configuration.

---

# 35. Повторный migrate

```bash
bench --site facility-ops-clean.localhost migrate
```

App configuration и clean runtime data должны сохраниться.

---

# 36. Git после clean site

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Clean Users/Locations/Equipment/Requests/ToDo не должны менять Git.

---

# 37. Portability map

```text
facility_ops Git
│
├── Standard source
├── fixtures
└── exported Custom DocPerm

clean site DB
│
├── local Users
├── local runtime data
└── optional local Assignment Rule
```

---

# 38. Вернуть основной site

```bash
cd ~/frappe/facility-ops-bench
bench use facility-ops.localhost
```

---

# 39. State contract L11

## Preconditions

```text
L5 hardened Role Permission matrix
L7 Accepted/Accept workflow
L10 final Allow Edit = No
Git clean
```

## Output proof

```text
Desk Requester create works by Role Permission
Requester saved request Write = No
Supervisor Delete = No
Workflow portable
Web Form Website User create works as separate intake capability
Web Form update disabled
runtime data not copied
```

---

# 40. Приёмка L11

L11 принят, если:

- Standard source устанавливается на clean site;
- fixtures содержат `Accepted/Accept`, не legacy `Assigned/Mark Assigned`;
- `New.only_allow_edit_for = Facility Supervisor`;
- exported Custom DocPerm восстанавливает exact final Role Permission matrix;
- Requester clean через Desk создаёт заявку, читает свою и не может переписать после Save;
- Supervisor clean не может удалить Service Request;
- Website User clean без Facility Requester создаёт через Web Form;
- Web Form create не называется доказательством Role Permission Create;
- `Apply Document Permissions` не приписывается к create authorization;
- final Web Form `Allow Edit = No`;
- old runtime state не приехал;
- manual ToDo не смешан с Workflow Close;
- clean Equipment использует допустимую Category;
- repeat migrate сохраняет runtime data;
- работа второго site не меняет Git;
- active site возвращён на `facility-ops.localhost`.

Главный вывод:

```text
app ≠ database copy
Desk Create ≠ Web Form Create
portable core ≠ site-specific operating policy
```
