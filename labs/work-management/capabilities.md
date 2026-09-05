# Work Management: продуктовые возможности

Work Management строится как готовый open-source продукт управления операционной работой на Frappe Framework.

У продукта есть жёстко зафиксированное ядро данных и набор first-party возможностей вокруг него. Конкретная организация настраивает процессы через данные `Site` и штатные механизмы Frappe, но не конструирует заново смысл `Work Unit`, `Work Type` и `Work Item`.

## Граница

Ядро остаётся неизменным:

```text
Work Unit
Work Type
Work Item
```

Дополнительная возможность входит в продукт только тогда, когда у неё есть самостоятельная и достаточно распространённая ответственность. Она не должна добавлять отраслевые поля в `Work Item` и не должна превращать приложение в собственный framework поверх Frappe.

На текущем этапе продукт остаётся одним Frappe App. Возможности группируются обычными Frappe Modules и DocType. Отдельная система плагинов, feature engine или динамическая загрузка модулей не требуется.

## Что уже даёт Frappe

Часть пользовательских возможностей Work Management не требует собственной предметной модели. Frappe уже предоставляет их как штатные механизмы.

| Потребность | Механизм Frappe | Решение Work Management |
| --- | --- | --- |
| роли и доступ | Roles, Role Permissions, User Permissions | использовать штатно |
| назначение исполнителей | Assign To / ToDo | использовать штатно, без собственного `assignee` |
| этапы согласования | Workflow | не создавать собственный workflow engine |
| уведомления и напоминания | Notification | настраивать по событиям и датам |
| повторяющаяся работа | Auto Repeat | разрешить повторение Work Item для простых календарных схем |
| вход через веб | Web Form | использовать для Work Request или другого подходящего DocType |
| вход через API | REST API | использовать автоматически генерируемый CRUD API DocType |
| вход из почты | Email Account / Email Append To | использовать для подходящего входного DocType, а не писать собственный mail processor |
| комментарии и обсуждение | Form Timeline / Comments / Communication | использовать штатно |
| вложения | File / Attachments | использовать штатно |
| список и фильтры | List View | настроить рабочие представления |
| Kanban | Kanban View | использовать `status` или другой подходящий Select |
| календарь и Gantt | Calendar / Gantt View | использовать `planned_start` и `due_at` |
| дерево ответственности | Tree View / Nested Set | использовать для Work Unit |
| простые отчёты | Report Builder | предоставлять готовые и пользовательские отчёты |
| сложные отчёты | Script Report | добавлять только там, где Report Builder недостаточен |
| рабочая навигация | Workspace | поставлять нейтральные Workspace продукта |
| дополнительные поля Site | Customize Form / Custom Fields | не раздувать upstream-схему ради одной организации |
| исходящие интеграции | Webhook, hooks | не создавать собственный integration framework |

Официальная документация:

- Desk и стандартные Views: https://docs.frappe.io/framework/user/en/desk
- User Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Notifications: https://docs.frappe.io/framework/notifications
- Web Form: https://docs.frappe.io/framework/user/en/web-form
- REST API: https://docs.frappe.io/framework/user/en/api/rest
- Webhooks: https://docs.frappe.io/framework/user/en/guides/integration/webhooks
- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Script Report: https://docs.frappe.io/framework/user/en/desk/reports/script-report
- Actions and Links: https://docs.frappe.io/framework/user/en/basics/doctypes/actions-and-links
- hooks: https://docs.frappe.io/framework/user/en/python-api/hooks
- Auto Repeat: https://docs.frappe.io/erpnext/auto-repeat

Таким образом, наличие назначений, Kanban, Gantt, уведомлений, входных каналов или повторяемости не является основанием добавлять собственные движки в Work Management.

## First-party возможности

### Состав рабочих команд

Ответственность: хранить факт того, какие пользователи относятся к какой рабочей зоне ответственности и в какой период.

```text
Work Membership
- user -> User
- work_unit -> Work Unit
- valid_from
- valid_to
- is_primary
```

Это не HR-модель. Здесь нет зарплаты, кадрового статуса, табеля, должностного штатного расписания или персональных данных сотрудника.

`Work Membership` нужен для рабочих представлений, фильтра выбора пользователей при штатном Assign To, аналитики состава команды и, если конкретная установка этого требует, проверки назначения пользователя в свою рабочую зону.

Сам `Work Unit` остаётся частью Core и не получает таблицу сотрудников.

### Входящие запросы и первичная обработка

Ответственность: зарегистрировать входящий запрос до того, как он будет классифицирован как конкретная работа или отклонён.

```text
Work Request
- subject
- description
- requester
- received_at
- channel
- status
```

`Work Request` нужен там, где входящий поток нельзя сразу считать готовым `Work Item`: письмо, обращение через Web Form, звонок, API-запрос или внутреннее поручение сначала может потребовать просмотра, классификации и определения ответственной зоны.

После принятия запроса из него создаётся один или несколько Work Item, а сам `Work Request` становится их `source`.

Каналы приёма не реализуются собственными движками: Web Form, REST API и Email Append To предоставляет Frappe.

`Work Request` не является Helpdesk или CRM. Он не вводит customer SLA, полноценный ticket lifecycle, омниканальность, базу знаний или клиентский портал. Если такая предметная система уже существует, её Ticket/Request может напрямую выступать `Work Source`, а `Work Request` не используется.

### Документальные основания

Ответственность: хранить канонический документ, на основании которого возникли действия или изменения.

```text
Basis Document
- document_type
- document_number
- document_date
- subject
- issuer
- received_at
- attachments
```

`Basis Document` используется как `Work Source`, но не является обязательным источником для всех организаций. В другой предметной области источником может быть Work Request, Ticket, Alert, Contract, Nonconformity или другой DocType.

Эта возможность не должна превращаться в полноценную ECM/СЭД: электронная подпись, юридическое долговременное хранение, OCR и сложные маршруты делопроизводства относятся к отдельной ответственности.

### Операционные локации

Ответственность: дать нейтральную модель места, в котором выполняется работа или находится отслеживаемый объект.

```text
Operational Location
- location_name
- parent_location
- is_group
- active
- description
```

В одной установке это могут быть производственные площадки, в другой — филиалы, офисы, сервисные центры или иные реальные места работы.

`Operational Location` не является складской системой, GIS или адресным справочником. При необходимости он может ссылаться на штатный `Address` или расширяться на конкретном Site.

### Отслеживаемые физические объекты

Ответственность: учитывать конкретный физический объект, его тип, текущее местонахождение, историю перемещений и изменяемый состав.

Имена DocType не должны конфликтовать с ERPNext `Asset` и `Asset Movement`, поэтому модель Work Management использует собственные предметные имена:

```text
Tracked Asset Type
Tracked Asset
Tracked Asset Movement
Tracked Asset Composition Change
```

Базовая семантика:

```text
Tracked Asset Type
    classifies
Tracked Asset

Tracked Asset Movement
    moves
Tracked Asset
    between Operational Location

Tracked Asset Composition Change
    changes parent/component relation
```

Типами могут быть транспорт, измерительное оборудование, терминал, принтер, датчик, ноутбук, генератор или другой индивидуально отслеживаемый физический объект.

Новый вид оборудования является новой записью `Tracked Asset Type`, а не новым DocType и не новым полем `Work Item`.

Специфическая функция конкретного оборудования, например поверка или техническое обслуживание, получает отдельный предметный DocType только при наличии самостоятельной ответственности.

`Tracked Assets` не должен становиться полноценным EAM/CMMS, складом, бухгалтерским учётом основных средств или PLM.

### Проекты и ограниченные результаты

Ответственность: объединять Work Item вокруг ограниченного результата с целью и плановыми датами.

Чтобы не конфликтовать с ERPNext `Project`, используется самостоятельное имя:

```text
Work Project
- title
- objective
- owning_unit
- owner_user
- status
- planned_start
- planned_end
```

Work Item связывается с `Work Project` через `references`.

Эта возможность покрывает лёгкое проектное управление, но не пытается заменить полноценные PPM, Agile или Critical Path системы. Зависимости, бюджеты, портфели и сложное ресурсное планирование добавляются только при отдельной доказанной потребности.

### Сменная работа и передача

Ответственность: фиксировать фактически состоявшуюся смену и передачу незавершённой работы между сменами.

```text
Work Shift
- work_unit
- starts_at
- ends_at
- status
- members
- summary
- handover_items
```

`handover_items` ссылаются на существующие `Work Item` и фиксируют, что необходимо продолжить следующей смене.

Это не workforce scheduler. Work Management не строит графики 2/2, не рассчитывает нормы рабочего времени, отпуска и замены. Если организации нужна полноценная система планирования персонала, это отдельная ответственность или интеграция с HR-системой.

### Учёт фактического времени

Ответственность: при необходимости фиксировать фактический труд, затраченный пользователем на Work Item.

```text
Work Time Entry
- work_item
- user
- started_at
- ended_at
- duration
- note
```

Эта возможность не обязательна для всех установок. Она полезна сервисным, проектным и профессиональным командам, где важно сравнивать `estimated_effort` с фактическим временем.

Если на Site уже используется подходящий Timesheet из другого Frappe App, Work Management не должен заставлять дублировать данные: Work Item может ссылаться на существующие документы через `references`.

### Семантическая история работы

Frappe `Track Changes`, `Version` и штатные `ToDo` остаются базовой технической историей. Для продвинутой операционной аналитики может использоваться отдельная узкая история значимых событий Work Item:

```text
Work Event
- work_item
- event_time
- event_type
- actor
- work_unit
- from_status
- to_status
```

`Work Event` фиксирует только события с бизнес-смыслом: начало, изменение состояния, передача между очередями, переоткрытие, завершение. Он не является общим event bus и не заменяет `Version` или `ToDo`.

Если в будущем потребуется отдельная стабильная история назначений для аналитики, сначала проверяется, достаточно ли штатных данных `ToDo`; поля назначения не добавляются в Work Item ради отчётности.

## Представления и отчётность продукта

Рабочая система должна быть полезной сразу после настройки, поэтому продукт поставляет стандартные представления и отчёты поверх своей модели, не создавая для них новую предметную модель.

Минимальный набор:

```text
My Work
Unit Queue
Incoming Requests
Open / In Progress / Waiting
Due Soon / Overdue
Unassigned Work
Work by Type
Work by Unit
Work by Assigned User
Completed Work
Throughput by Period
Lead / Cycle Time where timestamps allow it
Project Progress
Shift Handover
Asset Location / Movement History
```

`My Work`, `Unassigned Work` и `Work by Assigned User` используют штатные Assignment/ToDo records, а не поле Work Item.

Простые варианты строятся Report Builder и сохранёнными List View. Междокументные и расчётные отчёты оформляются как permission-aware Script Reports.

Query Report с сырым SQL не должен использоваться как способ обходить модель прав доступа.

## Повторяющаяся работа

Для обычных календарных схем Work Management использует Frappe Auto Repeat, а не собственный scheduler:

```text
daily
weekly
monthly
quarterly
half-yearly
yearly
```

Если бизнес-правило требует, например, «первый рабочий день месяца после закрытия предыдущего периода», это уже отдельная ответственность. Такой механизм не добавляется в продукт до появления реального распространённого сценария, который Auto Repeat не выражает.

## Что остаётся данными или расширением конкретной организации

Work Management не создаёт универсальные справочники для любой предметной области.

Примеры того, что может принадлежать конкретному Site или другому App:

```text
Employee / HR data
Customer
Supplier
Contractor
Contract
Vehicle-specific corporate fields
1C identifiers and sync metadata
CMDB objects
production orders
quality records
service tickets
legal cases
accounting dimensions
industry-specific registers
```

Work Item связывается с такими объектами через `sources` и `references`.

Интеграция с 1С, ERP, HRMS, CRM, CMDB или другой внешней системой также не является частью Core. Она реализуется через штатный REST/Webhook/hooks или отдельный integration App.

## Проверка на разных организациях

Набор возможностей должен позволять организациям использовать одну модель Core, но включать только реально нужную предметную часть.

| Возможность | Промышленная операционная служба | IT-сервис | Производство | Профессиональные услуги |
| --- | --- | --- | --- | --- |
| Core Work | нужна | нужна | нужна | нужна |
| Work Membership | нужна | нужна | нужна | нужна |
| Work Request | нужна | нужна или заменяется Helpdesk | иногда | нужна |
| Basis Document | нужна | иногда | нужна | нужна |
| Operational Location | нужна | иногда | нужна | редко |
| Tracked Assets | нужна | иногда / CMDB | нужна | обычно нет |
| Work Project | нужна | нужна | иногда | нужна |
| Work Shift | нужна | иногда для NOC | нужна | обычно нет |
| Work Time Entry | необязательно | часто нужна | необязательно | часто нужна |
| Work Event / flow analytics | полезна | полезна | полезна | полезна |

Предметные различия не меняют `Work Unit`, `Work Type` и `Work Item`.

Для промышленной эксплуатации дополнительно может использоваться интеграция с корпоративной учётной системой и локальные read-only справочники сотрудников. Для IT — Helpdesk/CMDB, для производства — ERP/MES/Quality, для профессиональных услуг — CRM/Contract/Case. Эти системы подключаются к Work Management, а не переписываются внутри него.

## Зависимости

Главное правило остаётся односторонним:

```text
capability -> Core
Core       -X-> capability
```

Допустимые зависимости между возможностями должны быть очевидными и предметными. Например:

```text
Tracked Assets  -> Operational Location
Work Shift      -> Work Item
Work Time Entry -> Work Item
Work Event      -> Work Item
```

`Work Request`, `Basis Document` и `Work Project` не требуют добавлять специальные поля в Work Item: связь уже выражается через `sources` и `references`.

## Чего продукт не строит

Work Management не должен превращаться в:

- универсальный BPMN/process builder;
- собственный workflow engine;
- собственный assignment engine;
- собственный permission engine;
- HR/payroll систему;
- CRM;
- бухгалтерию;
- складской учёт;
- универсальную ECM/СЭД;
- полноценный EAM/CMMS;
- универсальную CMDB;
- PPM/Agile suite;
- workforce scheduling engine;
- полноценный Helpdesk;
- integration bus;
- meta-framework с Entity/Relation/Rule/Plugin.

Если одна из этих задач становится самостоятельным продуктом, она должна решаться соответствующим Frappe App или интеграцией, а не раздуванием Work Management.

## Итоговая структура продукта

```text
Frappe Framework
│
├── permissions / Assign To / Workflow / Notifications
├── Desk / Views / Reports / Workspace
├── Auto Repeat / File / Comments / Communication
├── Web Form / REST / Email intake / Webhooks
│
└── Work Management
    │
    ├── Core Work
    │   ├── Work Unit
    │   ├── Work Type
    │   └── Work Item
    │
    ├── Work Membership
    ├── Work Intake
    ├── Documentary Records
    ├── Operational Locations
    ├── Tracked Assets
    ├── Work Projects
    ├── Shift Operations
    ├── Time Tracking
    └── Work History & Analytics
```

Это один готовый продукт с устойчивым Core. Организация использует нужные ей возможности и собирает свой типовой процесс через Frappe, не меняя фундаментальную модель данных.
