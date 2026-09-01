# L11. Переносимость приложения

L11 завершает основной маршрут практикума.

До этого `facility_ops` собирался на одном site. Теперь нужно доказать, что это приложение, а не набор ручных настроек одной базы.

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
проверка / migrate
        ↓
рабочая конфигурация без старых рабочих данных
```

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Проверить исходный site

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

На исходном site должны существовать:

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

`Service Request Auto Assignment` существует только на исходном site и содержит конкретных Users L9.

---

# 2. Четыре слоя

Для каждого объекта определяем слой:

```text
1. Standard source
2. app configuration
3. site-specific configuration
4. working data
```

## Standard source

Уже находится в source `facility_ops`:

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

Их не дублируем fixtures.

## App configuration

Нужна на любом site:

```text
Facility Requester
Facility Technician
Facility Supervisor

Workflow State:
New
Assigned
In Progress
Resolved
Closed

Workflow Action Master:
Mark Assigned
Start Work
Resolve
Close

Service Request Workflow
```

Эту часть поставляем fixtures.

## Site-specific configuration

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
```

В частности:

```text
Service Request Auto Assignment
```

ссылается на:

```text
technician.one@example.com
technician.two@example.com
```

На другом site исполнители будут другими. Поэтому Assignment Rule не входит в universal fixtures.

## Working data

На clean site не должны приехать старые:

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

---

# 3. Экспортировать Custom Permissions

L5 менял permissions Standard DocType через Role Permission Manager. Эти настройки хранятся как `Custom DocPerm` и не становятся автоматически частью исходного DocType JSON.

Для каждого:

```text
Facility Location
Equipment
Service Request
```

открыть `Customize Form → Actions → Export Customizations`.

Параметры:

```text
Module to Export:          Facility Operations
Sync on Migrate:           Yes
Export Custom Permissions: Yes
Apply Module Export Filter: No
```

JSON вручную не редактировать.

---

# 4. Проверить exported customizations

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

find facility_ops/facility_operations/custom \
  -maxdepth 1 \
  -type f \
  -print \
  | sort
```

Ожидаются custom JSON для трёх core DocType.

В них должны быть признаки:

```text
"sync_on_migrate": 1
"custom_perms"
```

`Equipment.notes` Permission Level 1 уже находится в Standard DocType metadata, а соответствующий Role permission Level 1 приходит через exported custom permissions.

---

# 5. Добавить fixtures в hooks.py

В `apps/facility_ops/facility_ops/hooks.py` добавить:

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

Это штатная конфигурация fixtures, а не runtime business logic.

---

# 6. Почему fixture_auto_order нужен

Зависимости:

```text
Role
↓
Workflow State / Workflow Action Master
↓
Workflow
```

В `v16.32.0` `fixture_auto_order = True` создаёт порядок fixture-файлов согласно hooks.

Не переименовывать JSON вручную.

---

# 7. Что не включать в fixtures

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

Причины:

```text
Standard source objects
→ уже в app source

site-specific configuration
→ зависит от развёртывания

working data
→ содержимое конкретного site
```

---

# 8. Экспортировать fixtures

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

# 9. Проверить fixtures на мусор

```bash
for f in facility_ops/fixtures/*.json; do
  echo "===== $f ====="
  sed -n '1,260p' "$f"
done
```

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

Fixtures содержат конфигурацию, а не учебные Documents.

---

# 10. Проверить Standard source objects

```bash
find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -E \
    'report|number_card|dashboard_chart|workspace|notification|web_form'
```

Объекты L8–L10 должны находиться в app source.

---

# 11. Зафиксировать поставку в Git

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

Добавить только нужное и закоммитить, например:

```bash
git add \
  facility_ops/hooks.py \
  facility_ops/fixtures \
  facility_ops/facility_operations/custom

git diff --cached
git commit -m "Package facility operations configuration"
git status
```

Working tree должен быть clean.

---

# 12. Создать clean site

```bash
cd ~/frappe/facility-ops-bench

bench new-site facility-ops-clean.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Задать новый пароль `Administrator`.

Не копировать database исходного site.

---

# 13. Установить app

```bash
bench --site facility-ops-clean.localhost install-app facility_ops
bench --site facility-ops-clean.localhost list-apps
```

Ожидается:

```text
frappe
facility_ops
```

Важно правильно понимать `v16.32.0`:

```text
install-app
```

уже выполняет первоначальную синхронизацию app: Standard source, fixtures, exported customizations и dashboards входят в штатный install flow.

Поэтому следующий `migrate` — **не обязательный второй этап, без которого установка якобы неполна**. Мы запускаем его как явную проверку обычного update/convergence пути уже установленного приложения:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

Фиксируем различие:

```text
install-app
= первоначальная установка приложения на site

migrate
= штатная синхронизация уже установленного приложения при изменениях/обновлении
```

---

# 14. Открыть clean site

```bash
bench use facility-ops-clean.localhost
```

Открыть:

```text
http://facility-ops-clean.localhost:8000
```

Войти под Administrator нового site.

---

# 15. Проверить Standard metadata

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

---

# 16. Проверить fixtures

Найти роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Найти:

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

# 17. Проверить permissions

В Role Permission Manager проверить права L5 для:

```text
Facility Location
Equipment
Service Request
```

Особенно:

```text
Requester → Only If Creator
Supervisor → Report / Export
Equipment.notes → Level 1 только Supervisor
```

---

# 18. Проверить Standard UI/config

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

Пока рабочих данных нет, карты могут показывать `0`.

```text
интерфейс приехал
данные не приехали
```

---

# 19. Проверить финальный Web Form

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

Для Location/Equipment:

```text
Allow Read On All Link Options = Yes
```

`Status` не является пользовательским полем Web Form.

---

# 20. Доказать отсутствие старых данных

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

Рабочая база clean site пустая.

---

# 21. Создать site-specific пользователей заново

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

Задать отдельные учебные пароли.

Эти Users не являются app source.

---

# 22. Создать новые рабочие данные

Создать дерево:

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
Category:       Other
Status:         Active
```

`Category = Other`, потому что базовый `Equipment.category` допускает только:

```text
HVAC
Electrical
IT
Other
```

Не придумывать `Pump` как новое Select value только ради названия оборудования.

---

# 23. Создать заявку под Requester

Войти как:

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

Проверить:

```text
Status = New
```

Автоматического назначения нет: Assignment Rule специально не переносился.

---

# 24. Assign To + Workflow на clean site

Под Supervisor:

```text
Assign To → technician.clean@example.com
Mark Assigned
```

Под Technician:

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

Проверить связанный ToDo.

---

# 25. Проверить Workspace

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

Они должны работать уже по новым данным clean site.

---

# 26. Проверить Web Form end-to-end

Войти как:

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
Description: Проверка переносимого Web Form на чистом site
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

Assignment Rule здесь отсутствует намеренно.

---

# 27. Assignment Rule на новом site

При желании после основной приёмки создать новый Assignment Rule уже под Users clean site.

Это deployment-настройка конкретного site:

```text
Workflow
→ universal app configuration

Assignment Rule с конкретными Users
→ site-specific configuration
```

Он не нужен для доказательства переносимости core приложения.

---

# 28. Повторить migrate

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops-clean.localhost migrate
```

После migrate должны сохраниться:

```text
Roles
Workflow
permissions
Workspace
Report / Cards / Chart
Notifications
Web Form
новые Users и рабочие Documents clean site
```

`migrate` синхронизирует приложение и не очищает рабочие данные.

---

# 29. Проверить Git после работы на втором site

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

---

# 30. Финальная карта поставки

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

# 31. Вернуть основной site активным

Это обязательный финальный шаг, потому что последующие Labs A–F продолжают накопленный основной учебный стенд.

Выполнить:

```bash
cd ~/frappe/facility-ops-bench
bench use facility-ops.localhost
```

Проверить:

```bash
bench --site facility-ops.localhost list-apps
```

Clean site остаётся рядом только как контрольный стенд переносимости.

После L11 активным снова должен быть:

```text
facility-ops.localhost
```

---

# 32. Финальная приёмка L11

L11 принят, если ученик может показать два site:

```text
facility-ops.localhost
facility-ops-clean.localhost
```

и доказать:

- Standard metadata приехала из app source;
- Roles и Workflow приехали через fixtures;
- Custom Permissions восстановились через exported customizations;
- Standard Workspace/Report/Cards/Chart/Notifications/Web Form установились вместе с app;
- `install-app` корректно понимается как первоначальная установка, а не только копирование schema;
- последующий `migrate` является проверкой штатной повторной синхронизации;
- старые Users, User Permission, Share, Assignment Rule и рабочие Documents не приехали;
- clean-site Equipment использует допустимое значение Category;
- Web Form на clean site заполняет обязательный Description;
- Assign To + Workflow работают без Assignment Rule;
- повторный migrate не уничтожает рабочие данные;
- работа на втором site не меняет Git;
- после проверки активным site снова выбран `facility-ops.localhost`.

Главный результат:

```text
app
≠
копия database
```

Приложение поставляет структуру и универсальную конфигурацию. Site хранит своих пользователей, локальное распределение работы и рабочие данные.