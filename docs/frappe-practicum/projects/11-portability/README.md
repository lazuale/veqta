# L11. Переносимость приложения

L11 завершает основной маршрут практикума.

До этого момента приложение собиралось на одном site. Теперь нужно доказать, что `facility_ops` действительно является приложением, а не набором ручных настроек конкретной базы.

Цель урока:

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

# 1. Проверить исходный site

В терминале:

```bash
cd ~/frappe/facility-ops-bench

bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

На исходном site уже должны существовать:

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

Facility Operations Workspace
Report a Facility Issue Web Form
```

---

# 2. Главный вопрос L11

Не всё, что есть в базе, должно ехать вместе с приложением.

Для каждого объекта задаём один вопрос:

```text
это часть приложения
или данные конкретного site?
```

Используем четыре класса:

```text
1. Standard metadata
2. app configuration
3. site-specific configuration
4. working data
```

---

# 3. Классифицировать всё созданное

## 3.1 Standard metadata

Это уже находится в source app и Git.

Сюда относятся:

```text
Facility Location DocType
Equipment DocType
Service Request DocType

Standard Report
Standard Number Card
Standard Dashboard Chart
Standard Workspace
Standard Notification
Standard Web Form
```

Они не требуют fixtures.

Особенно важно:

```text
DocType
не экспортируем как fixture
```

Standard DocType уже поставляется файлами app.

---

## 3.2 App configuration

Эти records нужны приложению на любом новом site, но сами по себе не являются Standard source-объектами.

Для нашего курса:

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

Их будем поставлять через fixtures.

---

## 3.3 Site-specific configuration

Это настройки, которые зависят от конкретного развёртывания.

В нашем стенде:

```text
Users
User Permission
Share
Assignment Rule
```

Почему `Assignment Rule` не включаем в fixtures:

```text
Service Request Auto Assignment
→ содержит конкретных Users
→ technician.one@example.com
→ technician.two@example.com
```

На другом site исполнители будут другими.

Поэтому правило распределения не является универсальной частью app.

Его создают уже после развёртывания под реальных пользователей конкретного site.

---

## 3.4 Working data

Это никогда не должно приезжать вместе с приложением:

```text
Facility Location Documents
Equipment Documents
Service Request Documents
ToDo
Comments
Files заявок
Notification Log
Workflow Action records
```

На чистом site они должны отсутствовать.

---

# 4. Разобраться с Role Permission Manager

В L5 права были настроены через:

```text
Role Permission Manager
```

Для Standard DocType такие изменения хранятся как:

```text
Custom DocPerm
```

Они не находятся автоматически в JSON наших DocType.

Но права являются частью поведения приложения и должны восстанавливаться на новом site.

Для них используем штатный:

```text
Export Customizations
```

с экспортом Custom Permissions.

---

# 5. Экспортировать permissions Facility Location

В Desk открыть:

```text
Customize Form
```

Выбрать:

```text
Facility Location
```

Открыть:

```text
Actions → Export Customizations
```

В диалоге задать:

```text
Module to Export:          Facility Operations
Sync on Migrate:           Yes
Export Custom Permissions: Yes
Apply Module Export Filter: No
```

Выполнить экспорт.

Даже если у DocType нет Custom Field или Property Setter, нам нужен экспорт его `Custom DocPerm`.

---

# 6. Экспортировать permissions Equipment

Повторить для:

```text
Equipment
```

Настройки те же:

```text
Module to Export:          Facility Operations
Sync on Migrate:           Yes
Export Custom Permissions: Yes
Apply Module Export Filter: No
```

---

# 7. Экспортировать permissions Service Request

Повторить для:

```text
Service Request
```

С теми же параметрами.

Именно здесь должны сохраниться права:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

включая `If Owner`, Report/Export и остальные настройки L5.

---

# 8. Посмотреть exported customizations

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

find facility_ops/facility_operations/custom \
  -maxdepth 1 \
  -type f \
  -print \
  | sort
```

Ожидаются JSON-файлы минимум для:

```text
Facility Location
Equipment
Service Request
```

Открыть их только для чтения:

```bash
sed -n '1,220p' \
  facility_ops/facility_operations/custom/service_request.json
```

Найти:

```text
"sync_on_migrate": 1
"custom_perms"
```

Не исправлять JSON вручную.

Если permissions неправильные — исправить их через Role Permission Manager и повторить Export Customizations.

---

# 9. Подготовить fixtures в hooks.py

Открыть:

```text
apps/facility_ops/facility_ops/hooks.py
```

Добавить конфигурацию fixtures:

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

Это штатная конфигурация Frappe app.

Никакого собственного runtime-кода здесь нет.

---

# 10. Почему fixture_auto_order нужен

Fixtures зависят друг от друга:

```text
Role
↓
Workflow State / Action Master
↓
Workflow
```

При:

```python
fixture_auto_order = True
```

Frappe добавляет к fixture-файлам порядковые префиксы согласно порядку в `hooks.py`.

Это делает порядок импорта явным.

Не пытаться решать зависимости ручным переименованием JSON-файлов.

---

# 11. Что специально НЕ добавляем в fixtures

В `hooks.py` не должно быть:

```text
User
User Permission
DocShare
Facility Location
Equipment
Service Request
ToDo
File
Notification Log
Assignment Rule
```

Также не добавляем:

```text
DocType
```

Standard DocType уже является source приложения.

---

# 12. Экспортировать fixtures

Из bench:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost export-fixtures --app facility_ops
```

Затем:

```bash
cd apps/facility_ops

find facility_ops/fixtures \
  -maxdepth 1 \
  -type f \
  -print \
  | sort
```

Должны появиться fixture JSON для:

```text
Role
Workflow State
Workflow Action Master
Workflow
```

---

# 13. Проверить содержимое fixtures

Посмотреть файлы:

```bash
for f in facility_ops/fixtures/*.json; do
  echo "===== $f ====="
  sed -n '1,220p' "$f"
done
```

Проверить, что там нет:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
technician.two@example.com
supervisor.one@example.com
web.requester@example.com
```

Также не должно быть рабочих номеров:

```text
SR-00001
EQ-0001
```

Fixtures должны содержать конфигурацию, а не содержимое рабочего site.

---

# 14. Проверить source Standard objects

Убедиться, что Standard configuration уже находится в app source:

```bash
find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -E \
    'report|number_card|dashboard_chart|workspace|notification|web_form'
```

Здесь должны быть объекты предыдущих уроков:

```text
Service Requests Overview
Open Requests
High Priority Requests
Closed Requests
Service Requests by Status
Facility Operations Workspace
New Service Request
Overdue Service Request
Report a Facility Issue
```

Они не дублируются fixtures.

---

# 15. Проверить полный Git diff

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

В L11 ожидаются изменения примерно такого типа:

```text
hooks.py
fixtures/*.json
facility_ops/facility_operations/custom/*.json
```

Не должно быть:

```text
дампа database
CSV рабочих данных
паролей
site_config.json
private files
```

---

# 16. Commit поставки приложения

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

Ожидается:

```text
working tree clean
```

---

# 17. Создать второй чистый site

Вознуться в bench:

```bash
cd ~/frappe/facility-ops-bench
```

Создать новый site:

```bash
bench new-site facility-ops-clean.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Задать новый Administrator password для этого site.

Не копировать database исходного `facility-ops.localhost`.

---

# 18. Установить facility_ops на clean site

```bash
bench --site facility-ops-clean.localhost install-app facility_ops
bench --site facility-ops-clean.localhost list-apps
```

Ожидается:

```text
frappe
facility_ops
```

После install выполнить:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

`migrate` штатно синхронизирует:

```text
schema
fixtures
customizations
standard app configuration
```

---

# 19. Переключить bench на clean site

```bash
bench use facility-ops-clean.localhost
```

Если `bench start` уже запущен, обновить страницу браузера.

Открыть:

```text
http://facility-ops-clean.localhost:8000
```

Войти как Administrator нового site.

---

# 20. Проверить Standard metadata

На clean site должны существовать:

```text
Facility Location
Equipment
Service Request
```

Проверить поля и настройки:

```text
Equipment.notes → Permission Level 1
Service Request.status → Read Only
```

Это доказывает перенос Standard DocType metadata.

---

# 21. Проверить Roles

Через `Role` найти:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Они должны существовать без ручного повторного создания.

Это результат fixtures.

---

# 22. Проверить Workflow

Открыть:

```text
Workflow
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

Transitions:

```text
Mark Assigned
Start Work
Resolve
Close
```

Ничего вручную пересобирать не нужно.

---

# 23. Проверить permissions

Открыть:

```text
Role Permission Manager
```

Проверить минимум `Service Request`.

Должны восстановиться права L5 для:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Затем проверить `Equipment` и `Facility Location`.

Это результат Export Customizations с:

```text
Sync on Migrate = Yes
Export Custom Permissions = Yes
```

---

# 24. Проверить Workspace и аналитику

На clean site должны существовать app-owned Standard objects L8:

```text
Facility Operations Workspace
Service Requests Overview
Open Requests
High Priority Requests
Closed Requests
Service Requests by Status
```

Пока рабочих заявок нет, значения Number Card могут быть нулевыми.

Это нормально.

Главное:

```text
интерфейс приехал
данные не приехали
```

---

# 25. Проверить Notifications

Через `Notification` найти:

```text
New Service Request
Overdue Service Request
```

Они должны существовать как Standard Notification из source app.

Fixtures для них не нужны.

---

# 26. Проверить Web Form

Через `Web Form` найти:

```text
Report a Facility Issue
```

Проверить финальную конфигурацию L10:

```text
Route = facility-request
Published = Yes
Login Required = Yes
Allow Multiple Responses = Yes
Allow Editing After Submit = Yes
Show List = Yes
Apply Document Permissions = No
```

Проверить, что `Location` и `Equipment` снова видимы и имеют:

```text
Allow Read On All Link Options = Yes
```

---

# 27. Проверить, чего на clean site НЕТ

Не должно быть старых:

```text
Facility Location Documents
Equipment Documents
Service Request Documents
Users курса
User Permission
Share
ToDo
Assignment Rule Service Request Auto Assignment
```

Особенно важно проверить:

```text
Service Request → List
Equipment → List
Facility Location → Tree
```

Рабочая часть должна быть пустой.

---

# 28. Создать пользователей clean site

Теперь создаём site-specific пользователей заново.

## Requester

```text
requester.clean@example.com
System User
Role: Facility Requester
```

## Technician

```text
technician.clean@example.com
System User
Role: Facility Technician
```

## Supervisor

```text
supervisor.clean@example.com
System User
Role: Facility Supervisor
```

## Website User

```text
web.clean@example.com
Website User
```

У каждого свой учебный пароль.

Эти Users не являются частью app source.

---

# 29. Создать новые рабочие данные

На clean site создать минимальную структуру:

```text
Main Site
└── Building A
    └── Room 101
```

Создать Equipment:

```text
Equipment Code: EQ-CLEAN-001
Equipment Name: Clean Site Pump
Location:       Room 101
Category:       Pump
Status:         Active
```

Это новые Documents именно clean site.

---

# 30. Создать Service Request под Requester

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

Assignment Rule отсутствует, поэтому автоматического назначения быть не должно.

Это ожидаемо.

---

# 31. Проверить ручной Assign To

Войти:

```text
supervisor.clean@example.com
```

Открыть новую заявку.

Выполнить:

```text
Assign To
→ technician.clean@example.com
```

Проверить созданный `ToDo`.

Затем выполнить Workflow Action:

```text
Mark Assigned
```

Получить:

```text
Status = Assigned
```

---

# 32. Проверить Workflow на clean site

Под:

```text
technician.clean@example.com
```

выполнить:

```text
Start Work
Resolve
```

Под:

```text
supervisor.clean@example.com
```

выполнить:

```text
Close
```

Финальное состояние:

```text
Closed
```

Если этот маршрут работает, Workflow действительно приехал вместе с приложением.

---

# 33. Проверить Workspace на новых данных

Войти под:

```text
supervisor.clean@example.com
```

Открыть:

```text
Facility Operations
```

Проверить:

```text
Number Cards
Dashboard Chart
Shortcuts
Report
```

Теперь они должны отображать данные clean site, а не исходного стенда.

---

# 34. Проверить Web Form на clean site

Войти:

```text
web.clean@example.com
```

Открыть:

```text
http://facility-ops-clean.localhost:8000/facility-request
```

Создать новую заявку:

```text
Subject:     Clean site web request
Location:    Room 101
Equipment:   EQ-CLEAN-001
Priority:    High
Attachment:  небольшой файл
```

Сохранить.

Затем под Supervisor найти тот же `Service Request` в Desk.

Получаем цепочку:

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

# 35. Что делать с Assignment Rule на новом site

После доказательства переносимости можно настроить автоматическое назначение уже под пользователей clean site.

Например:

```text
technician.clean@example.com
```

Но это отдельная site deployment-настройка.

Она не является доказательством установки app и не нужна для приёмки L11.

Главное различие:

```text
Workflow
= общий процесс приложения
→ fixtures

Assignment Rule с конкретными Users
= конфигурация конкретного развёртывания
→ настраивается на site
```

---

# 36. Проверить повторный migrate

Выполнить:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops-clean.localhost migrate
```

После migrate проверить:

- Roles остались;
- Workflow остался;
- permissions остались;
- Workspace/Web Form/Notification остались;
- созданные на clean site рабочие Documents не исчезли.

`migrate` синхронизирует приложение, а не очищает рабочую базу.

---

# 37. Проверить Git после второго site

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
```

Создание:

```text
facility-ops-clean.localhost
Users
Facility Locations
Equipment
Service Requests
ToDo
```

не должно создавать новый Git diff приложения.

Если Git изменился — выяснить, какой app-owned объект был изменён через Developer Mode.

---

# 38. Финальная модель поставки

После L11 ученик должен видеть приложение так:

```text
facility_ops Git repository
│
├── Standard DocTypes
│   ├── Facility Location
│   ├── Equipment
│   └── Service Request
│
├── Standard UI/config source
│   ├── Report
│   ├── Number Card
│   ├── Dashboard Chart
│   ├── Workspace
│   ├── Notification
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

# 39. Самостоятельная проверка

Без подсказки ответить для каждого объекта, где он должен жить:

```text
Equipment DocType
EQ-CLEAN-001
Facility Supervisor Role
supervisor.clean@example.com
Service Request Workflow
Service Request Auto Assignment
Facility Operations Workspace
SR-00001
User Permission
Report a Facility Issue Web Form
```

Правильная логика важнее заученного пути к файлу.

---

# 40. Приёмка L11

L11 принят, если ученик может показать два site:

```text
facility-ops.localhost
facility-ops-clean.localhost
```

и доказать следующее.

## App source

На clean site автоматически появились:

```text
Facility Location DocType
Equipment DocType
Service Request DocType
Workspace
Reports / Cards / Chart
Notifications
Web Form
```

## Fixtures

Автоматически появились:

```text
Facility Requester
Facility Technician
Facility Supervisor
Workflow States
Workflow Action Masters
Service Request Workflow
```

## Customizations

Восстановились permissions из Role Permission Manager.

## Не приехали

```text
старые Users
User Permission
Share
Assignment Rule с исходными Users
старые Locations
старые Equipment
старые Service Requests
старые ToDo
```

## End-to-end

На clean site можно:

```text
создать Location
→ создать Equipment
→ создать Service Request
→ Assign To
→ пройти Workflow
→ увидеть данные в Workspace
→ создать новую заявку через Web Form
```

## Git

После создания рабочих данных clean site:

```text
git status
→ working tree clean
```

---

# 41. Что ученик должен унести из базового курса

Не список экранов Frappe, а модель платформы:

```text
DocType
= схема

Document
= рабочая запись

Link
= связь

Role Permission
= что разрешено

User Permission
= какие данные разрешены

Assign To / ToDo
= кому поручена работа

Workflow
= какие переходы допустимы

Report / Card / Chart / Workspace
= представление рабочих данных

Notification / Assignment Rule
= штатная автоматизация

Web Form
= внешний интерфейс к тому же Document

Git
= поставка app-owned source

Fixtures / Export Customizations
= поставка нужной конфигурации

site database
= пользователи, локальная конфигурация и рабочие данные
```

На этом основной маршрут **L0–L11 завершён**.

Дальше идут отдельные лаборатории, которые расширяют знания Frappe, но не меняют минимальную архитектуру приложения.