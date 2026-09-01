# L11. Переносимость приложения

L11 завершает основной маршрут практикума.

До этого момента `facility_ops` собирался на одном site. Теперь нужно доказать, что это действительно приложение, а не набор ручных настроек одной базы.

Цель:

```text
app source
+ fixtures
+ exported customizations
        ↓
clean site
        ↓
install-app
        ↓
migrate
        ↓
рабочая конфигурация без старых рабочих данных
```

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Проверить исходный стенд

В терминале:

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

На исходном site к этому моменту должны существовать:

```text
Facility Location
Equipment
Service Request

Facility Requester
Facility Technician
Facility Supervisor

Service Request Workflow

New Service Request
Overdue Service Request

Service Request Auto Assignment

Facility Operations
Service Requests Overview
Open Requests
High Priority Requests
Closed Requests
Service Requests by Status

Report a Facility Issue
```

`Facility Operations` здесь — **Title Workspace**, созданного в L8.

---

# 2. Четыре класса объектов

Для каждого объекта задаём вопрос:

```text
это часть приложения
или содержимое конкретного site?
```

Используем четыре класса:

```text
1. Standard source
2. app configuration
3. site-specific configuration
4. working data
```

---

# 3. Standard source

Уже находится в source `facility_ops` и Git:

```text
Facility Location DocType
Equipment DocType
Service Request DocType

Service Requests Overview Report
Open Requests Number Card
High Priority Requests Number Card
Closed Requests Number Card
Service Requests by Status Dashboard Chart
Facility Operations Workspace

New Service Request Notification
Overdue Service Request Notification

Report a Facility Issue Web Form
```

Эти объекты **не экспортируем fixtures**.

Особенно:

```text
Standard DocType
≠ fixture
```

Standard metadata уже поставляется файлами app.

---

# 4. App configuration

Нужна на любом новом site, но не является Standard source-объектами:

```text
Facility Requester
Facility Technician
Facility Supervisor

Workflow State:
- New
- Assigned
- In Progress
- Resolved
- Closed

Workflow Action Master:
- Mark Assigned
- Start Work
- Resolve
- Close

Service Request Workflow
```

Эту конфигурацию поставляем fixtures.

---

# 5. Site-specific configuration

Зависит от конкретного развёртывания:

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
```

`Service Request Auto Assignment` из L9 содержит:

```text
technician.one@example.com
technician.two@example.com
```

На другом site исполнители будут другими.

Поэтому Assignment Rule **не входит** в универсальные fixtures приложения.

---

# 6. Working data

Не должны приехать на clean site:

```text
Facility Location Documents
Equipment Documents
Service Request Documents
ToDo
Comments
Files
Notification Log
Workflow Action records
```

Clean site должен получить структуру и универсальную конфигурацию, а не копию учебной базы.

---

# 7. Почему permissions нужно экспортировать отдельно

В L5 Role Permission Manager изменил права Standard DocType.

Эти изменения хранятся как:

```text
Custom DocPerm
```

Они не становятся автоматически частью исходного DocType JSON.

Поэтому права трёх core DocType экспортируем штатным:

```text
Export Customizations
```

с:

```text
Export Custom Permissions = Yes
Sync on Migrate = Yes
```

---

# 8. Экспортировать permissions трёх DocType

Под `Administrator` открыть:

```text
Customize Form
```

Последовательно выбрать:

```text
Facility Location
Equipment
Service Request
```

Для каждого выполнить:

```text
Actions → Export Customizations
```

Параметры:

```text
Module to Export:          Facility Operations
Sync on Migrate:           Yes
Export Custom Permissions: Yes
Apply Module Export Filter: No
```

После каждого экспорта не редактировать JSON вручную.

---

# 9. Проверить exported customizations

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

find facility_ops/facility_operations/custom \
  -maxdepth 1 \
  -type f \
  -print \
  | sort
```

Ожидаются файлы для:

```text
facility_location
equipment
service_request
```

Проверить один из них:

```bash
sed -n '1,260p' \
  facility_ops/facility_operations/custom/service_request.json
```

Найти:

```text
"sync_on_migrate": 1
"custom_perms"
```

Если permissions неверные, исправить их через Role Permission Manager и повторить Export Customizations.

---

# 10. Добавить fixtures в hooks.py

Открыть:

```text
apps/facility_ops/facility_ops/hooks.py
```

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
                    "Assigned",
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
                    "Mark Assigned",
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

Это конфигурация штатного механизма fixtures, а не собственная runtime-логика.

---

# 11. Почему fixture_auto_order нужен

Fixtures зависят друг от друга:

```text
Role
↓
Workflow State / Workflow Action Master
↓
Workflow
```

В `v16.32.0` `fixture_auto_order = True` добавляет fixture-файлам порядковые префиксы в соответствии с порядком hooks.

Не переименовывать fixture JSON вручную.

---

# 12. Что не включать в fixtures

Не добавлять:

```text
User
User Permission
DocShare
Assignment Rule
Facility Location
Equipment
Service Request
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

Причины разные:

```text
Standard source objects
→ уже находятся в app source

site-specific configuration
→ зависит от развёртывания

working data
→ содержимое конкретного site
```

---

# 13. Экспортировать fixtures

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost export-fixtures --app facility_ops
```

Проверить:

```bash
cd apps/facility_ops

find facility_ops/fixtures \
  -maxdepth 1 \
  -type f \
  -print \
  | sort
```

Должны быть fixture-файлы для:

```text
Role
Workflow State
Workflow Action Master
Workflow
```

---

# 14. Проверить fixtures на мусор

```bash
for f in facility_ops/fixtures/*.json; do
  echo "===== $f ====="
  sed -n '1,260p' "$f"
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

SR-00001
EQ-0001
```

Fixtures содержат конфигурацию, а не учебные Documents.

---

# 15. Проверить Standard source objects

```bash
find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -E \
    'report|number_card|dashboard_chart|workspace|notification|web_form'
```

Нужно увидеть source объектов L8–L10.

Их не дублируем fixtures.

---

# 16. Зафиксировать поставку в Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

Ожидаемые изменения L11:

```text
facility_ops/hooks.py
facility_ops/fixtures/*.json
facility_ops/facility_operations/custom/*.json
```

Не должно быть:

```text
database dump
CSV рабочих данных
паролей
site_config.json
private files
```

Добавить только нужное:

```bash
git add \
  facility_ops/hooks.py \
  facility_ops/fixtures \
  facility_ops/facility_operations/custom

git diff --cached
```

После проверки:

```bash
git commit -m "Package facility operations configuration"
git status
```

Нужно получить:

```text
working tree clean
```

---

# 17. Создать clean site

Вернуться в bench:

```bash
cd ~/frappe/facility-ops-bench
```

Создать новый site:

```bash
bench new-site facility-ops-clean.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Задать новый пароль Frappe `Administrator`.

Не копировать database `facility-ops.localhost`.

---

# 18. Установить app и выполнить migrate

```bash
bench --site facility-ops-clean.localhost install-app facility_ops
bench --site facility-ops-clean.localhost list-apps
```

Ожидается:

```text
frappe
facility_ops
```

Затем:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

В `v16.32.0` migrate синхронизирует schema, fixtures, exported customizations и Standard app configuration.

---

# 19. Открыть clean site

```bash
bench use facility-ops-clean.localhost
```

Открыть:

```text
http://facility-ops-clean.localhost:8000
```

Войти под `Administrator` нового site.

---

# 20. Проверить Standard metadata

Должны существовать:

```text
Facility Location
Equipment
Service Request
```

Проверить минимум:

```text
Equipment.notes → Permission Level 1
Service Request.status → Read Only
```

Это source metadata приложения.

---

# 21. Проверить fixtures

Через `Role` найти:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Через `Workflow` найти:

```text
Service Request Workflow
```

Проверить:

```text
Workflow State Field = status
Is Active = Yes
```

States:

```text
New
Assigned
In Progress
Resolved
Closed
```

Actions:

```text
Mark Assigned
Start Work
Resolve
Close
```

---

# 22. Проверить permissions

Открыть Role Permission Manager для:

```text
Facility Location
Equipment
Service Request
```

Права L5 должны восстановиться из exported customizations.

Особенно проверить:

```text
Requester → Only If Creator
Supervisor → Report / Export
Equipment.notes → Level 1 только Supervisor
```

---

# 23. Проверить Standard UI/config

На clean site должны существовать:

```text
Workspace:       Facility Operations
Report:          Service Requests Overview
Number Card:     Open Requests
Number Card:     High Priority Requests
Number Card:     Closed Requests
Dashboard Chart: Service Requests by Status
Notification:    New Service Request
Notification:    Overdue Service Request
Web Form:        Report a Facility Issue
```

Пока Service Request нет, карты могут показывать `0`.

Правильный результат:

```text
интерфейс приехал
данные не приехали
```

---

# 24. Проверить финальный Web Form

У `Report a Facility Issue` проверить:

```text
Route = facility-request
Published = Yes
Login Required = Yes
Allow Multiple Responses = Yes
Allow Editing After Submit = Yes
Show List = Yes
Apply Document Permissions = No
```

У полей:

```text
Location
Equipment
```

проверить:

```text
Allow Read On All Link Options = Yes
```

`Status` не должен быть пользовательским полем Web Form.

---

# 25. Доказать, что рабочие данные не перенеслись

На clean site не должно быть старых:

```text
Users курса
User Permission
Share
Service Request Auto Assignment
ToDo
Facility Location Documents
Equipment Documents
Service Request Documents
```

Проверить:

```text
Facility Location → Tree
Equipment → List
Service Request → List
```

Рабочая часть clean site должна быть пустой.

---

# 26. Создать site-specific пользователей заново

Создать:

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

У каждого свой учебный пароль.

Эти Users не являются app source.

---

# 27. Создать новые рабочие данные

Под подходящим пользователем создать:

```text
Main Site
└── Building A
    └── Room 101
```

Затем Equipment:

```text
Equipment Code: EQ-CLEAN-001
Equipment Name: Clean Site Pump
Location:       Room 101
Category:       Pump
Status:         Active
```

Это новые Documents clean site.

---

# 28. Создать заявку под Requester

Войти:

```text
requester.clean@example.com
```

Создать:

```text
Subject:     Clean site request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Description: End-to-end portability test
Priority:    Medium
Target Date: будущая дата
```

Сохранить.

Ожидается:

```text
Status = New
```

Автоматического назначения быть не должно, потому что Assignment Rule намеренно не переносился.

---

# 29. Проверить Assign To и Workflow

Под:

```text
supervisor.clean@example.com
```

выполнить:

```text
Assign To → technician.clean@example.com
Mark Assigned
```

Проверить созданный ToDo и:

```text
Status = Assigned
```

Под Technician выполнить:

```text
Start Work
Resolve
```

Под Supervisor:

```text
Close
```

Финал:

```text
Status = Closed
```

---

# 30. Проверить Workspace на новых данных

Под Supervisor открыть:

```text
Facility Operations
```

Проверить:

```text
Number Cards
Dashboard Chart
Shortcuts
Service Requests Overview
```

Они должны показывать данные clean site.

---

# 31. Проверить Web Form end-to-end

Войти:

```text
web.clean@example.com
```

Открыть:

```text
http://facility-ops-clean.localhost:8000/facility-request
```

Создать:

```text
Subject:     Clean site web request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Priority:    High
Attachment:  небольшой файл
```

Сохранить.

Под Supervisor найти тот же Service Request в Desk.

Доказанная цепочка:

```text
Web Form
↓
Service Request
↓
Desk
↓
Assign To
↓
Workflow
```

---

# 32. Assignment Rule на новом site

После приёмки L11 при желании создать новый Assignment Rule уже под Users clean site.

Это deployment-настройка конкретного site, а не обязательная часть установки `facility_ops`.

```text
Workflow
→ универсальный процесс приложения
→ fixture

Assignment Rule с конкретными Users
→ локальное распределение работы
→ site-specific configuration
```

---

# 33. Повторить migrate

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops-clean.localhost migrate
```

После повторного migrate должны сохраниться:

```text
Roles
Workflow
permissions
Workspace
Report / Cards / Chart
Notifications
Web Form
новые рабочие Documents clean site
```

`migrate` синхронизирует приложение, а не очищает рабочие данные.

---

# 34. Проверить Git после работы на втором site

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Создание на clean site:

```text
Users
Locations
Equipment
Service Requests
ToDo
```

не должно менять Git приложения.

Если Git изменился, выяснить, какой app-owned metadata/config object был изменён через Developer Mode.

---

# 35. Финальная карта поставки

```text
facility_ops Git repository
│
├── Standard source
│   ├── DocTypes
│   ├── Report
│   ├── Number Cards
│   ├── Dashboard Chart
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
├── Assignment Rule tied to local Users
├── Facility Location Documents
├── Equipment Documents
├── Service Request Documents
└── ToDo / Comments / Files / Logs
```

---

# 36. Самостоятельная классификация

Без подсказки определить слой для каждого объекта:

```text
Equipment DocType
EQ-CLEAN-001
Facility Supervisor Role
supervisor.clean@example.com
Service Request Workflow
Service Request Auto Assignment
Facility Operations Workspace
Service Request Document
User Permission
Report a Facility Issue Web Form
```

Правильная логика важнее пути к конкретному JSON.

---

# 37. Приёмка L11

L11 принят, если ученик может показать два site:

```text
facility-ops.localhost
facility-ops-clean.localhost
```

и доказать:

- Standard metadata приехала из app source;
- Roles и Workflow приехали через fixtures;
- Custom Permissions восстановились через exported customizations;
- `Facility Operations` Workspace, Report, Cards, Chart, Notifications и Web Form приехали как Standard source objects;
- старые Users, Assignment Rule и рабочие Documents не приехали;
- на clean site можно создать новых пользователей и данные;
- Assign To + Workflow работают;
- Web Form создаёт обычный Service Request;
- повторный migrate не уничтожает рабочие данные;
- создание рабочих Documents на втором site не меняет Git.

Главный результат:

```text
app
≠
копия database
```

Приложение поставляет структуру и универсальное поведение. Site хранит своих пользователей, локальные правила распределения и рабочие данные.