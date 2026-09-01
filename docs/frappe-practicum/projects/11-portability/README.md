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
working core without old runtime data
```

Важно: L11 доказывает **clean-site portability**, а не автоматическую бесконфликтную co-installation совместимость с любым сторонним app.

---

# 1. Четыре слоя

```text
1. Standard source
2. universal app configuration
3. site-specific configuration
4. working data
```

Эти слои не смешиваем.

---

# 2. Standard source

Уже находится в `facility_ops`:

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

Standard DocType/Report/Card/Chart/Workspace/Notification/Web Form не дублируются fixtures.

---

# 3. Universal app configuration

На любом clean site должны появиться:

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

Это поставляем fixtures.

---

# 4. Site-specific configuration

Не является universal app behavior:

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
```

На основном site L9 существует:

```text
Service Request Auto Assignment
```

с:

```text
technician.one@example.com
technician.two@example.com
```

На clean site таких Users нет, поэтому Rule не fixture.

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

Приложение переносит структуру и конфигурацию, а не копию database.

---

# 6. Проверить исходный site

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно получить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

На исходном site должны существовать финальные имена:

```text
Service Request Workflow
New / Accepted / In Progress / Resolved / Closed
Accept / Start Work / Resolve / Close

Facility Operations Control
New Service Request
Service Request One Day Overdue
Report a Facility Issue
```

У Web Form:

```text
Allow Editing After Submit = No
```

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

`Equipment.notes` Permission Level 1 находится в Standard metadata, а соответствующие Role permissions приходят через exported custom permissions.

---

# 9. Fixtures в hooks.py

Добавить:

```python
fixtures = [
    {
        "doctype": "Role",
        "filters": [
            [
                "name",
                "in",
                [
                    "Facility Requester",
                    "Facility Technician",
                    "Facility Supervisor",
                ],
            ]
        ],
    },
    {
        "doctype": "Workflow State",
        "filters": [
            [
                "name",
                "in",
                [
                    "New",
                    "Accepted",
                    "In Progress",
                    "Resolved",
                    "Closed",
                ],
            ]
        ],
    },
    {
        "doctype": "Workflow Action Master",
        "filters": [
            [
                "name",
                "in",
                [
                    "Accept",
                    "Start Work",
                    "Resolve",
                    "Close",
                ],
            ]
        ],
    },
    {
        "doctype": "Workflow",
        "filters": [["name", "=", "Service Request Workflow"]],
    },
]

fixture_auto_order = True
```

Зависимости:

```text
Role
↓
Workflow State / Action Master
↓
Workflow
```

`fixture_auto_order` использует hooks order для fixture filenames.

---

# 10. Что не fixture

Не добавлять:

```text
User
User Permission
DocShare
Assignment Rule
Facility Location working Documents
Equipment working Documents
Service Request working Documents
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

Standard source уже поставляется source-механизмом, runtime/site-specific data не должны становиться fixtures.

---

# 11. Export fixtures

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost export-fixtures --app facility_ops
```

Проверить каталог:

```bash
cd apps/facility_ops
find facility_ops/fixtures -maxdepth 1 -type f -print | sort
```

Ожидаются:

```text
Role
Workflow State
Workflow Action Master
Workflow
```

---

# 12. Проверить fixtures на runtime мусор

```bash
for f in facility_ops/fixtures/*.json; do
  echo "===== $f ====="
  sed -n '1,280p' "$f"
done
```

Не должно быть:

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

Должны быть новые universal Workflow names:

```text
Accepted
Accept
```

и не должно остаться старых:

```text
Assigned
Mark Assigned
```

---

# 13. Проверить Standard source

```bash
find facility_ops/facility_operations \
  -type f | sort \
  | grep -E 'report|number_card|dashboard_chart|workspace|notification|web_form'
```

L8–L10 находятся в app source.

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

Новый пароль Administrator задаётся отдельно.

Database старого site не копировать.

---

# 16. install-app и migrate — точная семантика

```bash
bench --site facility-ops-clean.localhost install-app facility_ops
bench --site facility-ops-clean.localhost list-apps
```

В `v16.32.0` `install_app()` уже выполняет первоначальный install flow, включая:

```text
sync source
sync fixtures
sync customizations
sync dashboards
```

Поэтому последующий:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

используется как проверка обычного update/convergence path уже установленного приложения.

Не учим ложной модели:

```text
install-app = половина установки
migrate = обязательная вторая половина
```

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

Проверить:

```text
Service Request.status
Options:
New
Accepted
In Progress
Resolved
Closed

Read Only = Yes
```

и:

```text
Equipment.notes → Permission Level 1
```

---

# 19. Проверить fixtures

Роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Workflow:

```text
Service Request Workflow
```

States:

```text
New
Accepted
In Progress
Resolved
Closed
```

Actions:

```text
Accept
Start Work
Resolve
Close
```

Проверить transitions:

```text
New → Accept → Accepted
Accepted → Start Work → In Progress
In Progress → Resolve → Resolved
Resolved → Close → Closed
```

---

# 20. Проверить permission semantics

Role Permission Manager должен восстановить L5 configuration.

При этом помнить:

```text
Role Permission
= server access boundary

Only Allow Edit For
= state-dependent Desk behavior
```

Не использовать clean-site проверку UI как доказательство более сильной ACL, чем реально настроено.

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

Для Location/Equipment `Allow Read On All Link Options = Yes` рассматривается как trust decision для внутренних authenticated Website Users.

---

# 23. Доказать отсутствие старого runtime состояния

На clean site не должно быть старых:

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
System User
Role: Facility Requester

technician.clean@example.com
System User
Role: Facility Technician

supervisor.clean@example.com
System User
Role: Facility Supervisor

web.clean@example.com
Website User
```

Это site data, не app source.

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

`Pump` — название объекта, не новое значение Category.

---

# 26. Создать Service Request

Под Requester:

```text
Subject:     Clean site request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Description: End-to-end portability test
Priority:    Medium
Target Date: будущая дата или пусто
```

Получить:

```text
Status = New
```

Assignment Rule отсутствует, поэтому auto assignment не ожидается.

---

# 27. Manual Assignment + Workflow

Под Supervisor:

```text
Assign To → technician.clean@example.com
Accept
```

Получить:

```text
Assigned To = technician.clean@example.com
Status = Accepted
```

Под Technician:

```text
Start Work
Resolve
```

Получить:

```text
Status = Resolved
```

---

# 28. Важная граница ToDo на clean site

На основном site L9 Assignment Rule имеет:

```text
Close Condition: status == "Closed"
```

и поэтому закрывает Rule-managed ToDo.

На clean site Assignment Rule **намеренно отсутствует**.

Следовательно нельзя ожидать:

```text
Workflow Close
→ автоматически закроет ручной ToDo
```

Перед финальным Close Technician может штатно завершить своё ToDo вручную.

Проверить:

```text
ToDo Status = Closed
Service Request Status = Resolved
```

Это снова доказывает:

```text
ToDo lifecycle
≠ Workflow lifecycle
```

---

# 29. Закрыть процесс

Под Supervisor:

```text
Close
```

Получить:

```text
Status = Closed
```

Closed — terminal Workflow state.

Не объявлять его абсолютной физической immutability record без отдельной server validation policy.

---

# 30. Проверить Workspace

Под Supervisor открыть:

```text
Facility Operations Control
```

Проверить Cards, Chart, Shortcuts, Quick List и Report на новых clean-site данных.

---

# 31. Проверить Web Form end-to-end

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
Description: Проверка переносимого Web Form
Priority:    High
Attachment:  небольшой файл
```

Под Supervisor найти тот же Service Request.

Проверить:

```text
Status = New
```

и отсутствие Web Form edit после submit:

```text
Allow Editing After Submit = No
```

---

# 32. Assignment Rule на новом site

После основной acceptance при желании создать новый локальный Assignment Rule уже с clean Users.

Это deployment configuration, а не доказательство переносимости core.

После его добавления поведение ToDo может отличаться от чистого manual-assignment сценария — именно поэтому Rule не fixture.

---

# 33. Повторный migrate

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

`migrate` не является очисткой runtime data.

---

# 34. Git после clean site

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Создание clean:

```text
Users
Locations
Equipment
Service Requests
ToDo
```

не должно менять app Git.

---

# 35. Карта поставки

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

# 36. Scope portability

L11 доказывает:

```text
facility_ops
→ устанавливается на новый clean Frappe site
```

L11 не доказывает:

```text
facility_ops
→ гарантированно не конфликтует
с любым произвольным сторонним app
на уже насыщенном site
```

Глобальные имена DocType/Workflow State/Action Master требуют отдельного integration audit при co-installation.

---

# 37. Вернуть основной site

Обязательный финальный шаг:

```bash
cd ~/frappe/facility-ops-bench
bench use facility-ops.localhost
```

Проверить:

```bash
bench --site facility-ops.localhost list-apps
```

Labs A–F продолжают основной накопленный стенд.

---

# 38. Приёмка L11

L11 принят, если доказано:

- Standard source устанавливается на clean site;
- fixtures содержат `Accepted` и `Accept`, а не старые `Assigned/Mark Assigned`;
- permissions восстановлены exported customizations;
- Web Form финально `Allow Edit = No`;
- старые Users/Share/User Permission/Assignment Rule/runtime data не приехали;
- manual ToDo на clean site не ошибочно связывается с Workflow Close;
- main-site auto-close ToDo понимается как L9 Assignment Rule policy;
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
