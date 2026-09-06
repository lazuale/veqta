# Work Management: универсальное ядро

Work Management — прототип open-source приложения управления операционной работой на Frappe Framework.

Цель модели — покрывать реальные процессы разных организаций, не превращая приложение в универсальный конструктор бизнес-сущностей и не создавая framework поверх Frappe. Конкретная организация настраивает структуру, виды работ, права, Workflow и собственные предметные объекты на своём `Site`.

Полнота продукта определяется отдельно в [функциональном контракте v1](capabilities.md): наличие DocType или штатного механизма Frappe само по себе не считается готовой пользовательской возможностью без поставляемого интерфейса и рабочего сценария.

## Граница продукта

Frappe остаётся прикладной платформой и отвечает за `DocType`, `Document`, ORM, Desk, permissions, Workflow, Assign To / ToDo, Notifications, Reports, REST API, background jobs и штатные механизмы расширения.

Work Management добавляет только семантику операционной работы.

Универсальное ядро состоит из трёх top-level DocType:

```text
Work Unit
Work Type
Work Item
```

Внутри Work Item используются узкие child DocType для фиксированных отношений, принадлежащих самой работе: `Work Source`, `Work Reference` и `Work Dependency`.

Дополнительные возможности не должны менять эту модель, пока не появляется новая ответственность, общая для самого понятия работы.

Официальные механизмы Frappe, на которых строится граница:

- DocType как основной building block: https://docs.frappe.io/framework/user/en/basics/doctypes
- Link, Dynamic Link и child tables: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- site-specific customization: https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- Modules: https://docs.frappe.io/framework/user/en/basics/doctypes/modules
- hooks и `extend_doctype_class`: https://docs.frappe.io/framework/user/en/python-api/hooks

Точная схема полей, permissions, индексов и серверных инвариантов зафиксирована в [Data Model v1](data-model-v1.md).

## Work Unit

`Work Unit` отвечает только на вопрос: **какая организационная очередь или зона ответственности владеет работой?**

Это не обязательно формальная оргструктура компании. В одном `Site` Work Unit может означать отделы, в другом — команды, направления или сервисные очереди.

Примеры являются данными конкретного `Site`:

```text
Operations
├── Dispatch
├── Document Control
└── Administration
```

У другой организации дерево будет другим без изменения схемы приложения.

Core не определяет модель членства сотрудников в Work Unit и не использует Work Unit как обязательную ACL-границу. Базовый доступ задаётся штатными Roles/DocPerm Frappe. Конкретный Site при необходимости может дополнительно сужать доступ стандартными User Permissions или другими штатными механизмами, но это уже конфигурация установки, а не семантика очереди.

## Work Type

`Work Type` классифицирует повторяющийся смысл работы и не задаёт свойства конкретного Work Item.

Минимальная семантика:

```text
type_name
active
description
```

`Work Type` не является workflow engine, rule engine или системой маршрутизации, не определяет ответственную очередь и не назначает приоритет по умолчанию.

## Work Item

`Work Item` — одна конкретная исполнимая единица работы.

Стабильный контракт:

```text
subject
description

work_type
responsible_unit

status
priority

planned_start
due_at

waiting_reason
waiting_since

started_at
closed_at

parent_work_item
dependencies

sources
references
```

`responsible_unit` отвечает только за текущую очередь Work Item. Персональное выполнение не дублируется отдельным Core field: для назначения одного или нескольких пользователей используется штатный Frappe Assign To / ToDo.

```text
responsible_unit = в какой очереди находится работа
Frappe Assignment = кто назначен на её выполнение
```

Work Item может не иметь активных assignments, иметь один assignment или несколько одновременно. Work Management не вводит собственную кардинальность поверх штатного механизма Frappe.

### Структура работы

`parent_work_item` выражает только отношение **«эта работа является непосредственной частью другой Work Item»**.

У Work Item может быть не более одного непосредственного родителя. Дочерние Work Item остаются самостоятельными исполнимыми документами и могут иметь собственные очередь, исполнителей, status, priority и даты.

Hierarchy не вводит автоматические roll-up правила: закрытие дочерних работ не закрывает родителя, даты не агрегируются автоматически. Если конкретному Site нужно такое процессное правило, оно добавляется отдельно.

### Dependencies

`dependencies` — child table с узкой семантикой **«какая Work Item является prerequisite для текущей работы»**.

```text
Work Item A
    depends on
Work Item B
```

В обратном направлении B блокирует A, но отдельная зеркальная запись не хранится.

Dependency — факт связи, а не workflow rule. Core не запрещает автоматически начинать или закрывать работу при незавершённой зависимости, не переносит даты и не вычисляет critical path. Более строгая policy при необходимости реализуется Workflow или другим допустимым расширением Site.

Self-reference, duplicate dependency и циклы hierarchy/dependencies не допускаются.

### Sources

`sources` — child table узкой семантики **«на основании чего возникла работа?»**.

Каждая строка содержит:

```text
source_doctype   Link → DocType
source_name      Dynamic Link
```

Так Core не знает, является источником служебная записка, клиентский запрос, monitoring alert, договор, производственное несоответствие или другой документ.

Обязательность источника зависит от процесса конкретной организации или отдельной capability и не настраивается универсальным Work Type.

### References

`references` — отдельная child table узкой семантики **«к каким предметным документам относится работа?»**.

Каждая строка также использует `DocType` + `Dynamic Link`.

Это позволяет одной Work Item одновременно относиться, например, к Project, сотруднику и оборудованию без добавления этих полей в Core.

`sources` и `references` не являются универсальным relation engine. Их семантика фиксирована самим понятием работы, а произвольные типы и правила отношений не моделируются. Внутренняя структура Work Item и prerequisite dependency поэтому выражаются отдельными Core relations, а не перегружают `references`.

### Жизненный цикл

Core использует небольшой набор состояний с одинаковым смыслом во всех установках:

```text
Open
In Progress
Waiting
Done
Cancelled
```

Специфические этапы согласования конкретной организации не добавляются в Core. Для них используется штатный Frappe `Workflow` и, при необходимости, отдельное `workflow_state`.

### Повторяемая работа

Для обычной календарной повторяемости используется штатный Frappe Auto Repeat. Work Management определяет только семантику нового экземпляра Work Item через `on_recurring`: новый экземпляр начинается с `Open`, без lifecycle timestamps, текущего Waiting, старых дат, parent/dependencies и `sources` прошлого выполнения.

Классификация, очередь, priority и `references` сохраняются как шаблонный контекст. Assignments остаются штатными `ToDo` и управляются механизмом Auto Repeat, а не копированием поля Work Item.

Техническая ссылка `auto_repeat` нужна для интеграции со штатным механизмом Frappe и не является предметным свойством работы.

Собственный scheduler для повторяемой работы не создаётся.

## Расширение без изменения Core

Универсальность достигается не новыми meta-сущностями, а обычными механизмами Frappe.

```text
новое подразделение        → новая запись Work Unit
новый вид работы           → новая запись Work Type
назначение исполнителей     → Frappe Assign To / ToDo
новое поле компании        → Custom Field / Customize Form
новый процесс согласования → Frappe Workflow
новый предметный объект    → обычный DocType
новый источник работы      → обычный DocType + Work Source
новая связь с объектом     → Work Reference
новая интеграция           → REST / Webhook / hooks / отдельный App
```

Не вводятся `Universal Entity`, `Relation Type`, `Process Definition`, `Rule Engine`, `Plugin Registry` и другие мета-слои. Frappe DocType уже выполняет роль расширяемой модели приложения.

Для Frappe v16 дополнительный App также может расширять поведение существующего DocType через `extend_doctype_class`, не заменяя его controller целиком.

## Дополнительные возможности

Реальная установка может требовать больше трёх DocType. Это не делает их частью универсального Core и не означает, что они автоматически входят в roadmap продукта.

### Documentary Records

`Basis Document` может быть отдельной capability, если продукту действительно понадобится хранить зарегистрированное документальное основание, его метаданные и attachments. В таком случае он может выступать одним из `sources` Work Item.

Сам `Basis Document` не входит в Core, потому что в других предметных областях источником может быть уже существующий Ticket, Alert, Contract, Nonconformity или другой DocType.

### Assets

Учёт индивидуально отслеживаемого оборудования может получить собственную capability только при подтверждении самостоятельной ответственности. Возможная предметная модель не должна добавлять отраслевые поля в Work Item.

Конкретная установка уже сегодня может ссылаться на ERPNext `Asset`, собственный DocType оборудования или другой внешний объект через `references`.

### Reference Data

Конкретная установка может ссылаться на HRMS `Employee`, ERPNext `Asset`, собственные справочники или локальные read-only проекции внешней системы. Core не определяет единую модель сотрудника, техники, клиента или контрагента.

### Planning и Shift Operations

Project, shift journal и handover остаются кандидатами на самостоятельные capabilities, а не частью v1. Они добавляются только после доказательства отдельной ответственности, которой Core, настройка Site или совместимый Frappe App не закрывают.

## Проверка на разных организациях

Модель проверяется заменой предметной области. Критерий простой: если новый сценарий требует изменить семантику трёх Core DocType, ядро недостаточно универсально. Если отличие выражается данными Site, стандартной настройкой Frappe или отдельным предметным DocType, граница сохраняется.

### Сценарий 1. Промышленная операционная служба

Организация ведёт несколько направлений: диспетчеризацию, контроль документов, учёт и логистику.

```text
Work Unit    → направления службы
Work Type    → сверка, проверка, исправление, регистрация, перемещение
Work Item    → конкретное действие сотрудника
sources      → существующий документ-основание
references   → сотрудник, площадка, оборудование и другие предметные документы
```

Сотрудники, площадки, техника и документальные реестры остаются владельцами собственной предметной семантики. Для этого Core не требует отдельных полей.

### Сценарий 2. IT managed services

Компания обслуживает инфраструктуру клиентов.

```text
Work Unit
├── Service Desk
├── Infrastructure
└── Security

Work Type
├── Incident
├── Access Request
├── Change
└── Preventive Maintenance
```

Источниками Work Item являются support ticket, monitoring alert или approved change request. В `references` могут одновременно находиться клиент, сервер и система.

SLA, CMDB или специфический change-management являются отдельными предметными возможностями или настройками Site. Для них не требуется менять Work Unit, Work Type или Work Item.

### Сценарий 3. Производство и контроль качества

Компания использует Work Management для производства, качества и обслуживания оборудования.

```text
Work Unit
├── Production
├── Quality
└── Maintenance

Work Type
├── Inspection
├── Corrective Action
├── Repair
└── Investigation
```

Источники: production order, nonconformity report, maintenance request, customer complaint.

В `references` могут одновременно находиться партия, оборудование и производственный заказ.

### Сценарий 4. Профессиональные услуги

Компания оказывает бухгалтерские, налоговые и юридические услуги.

```text
Work Unit
├── Accounting
├── Tax
└── Legal

Work Type
├── Client Request
├── Review
├── Filing
└── Reconciliation
```

Источниками являются запрос клиента, договор, письмо или уведомление государственного органа. `references` связывают работу с клиентом, договором, делом и отчётным периодом.

Во всех этих сценариях крупная работа может декомпозироваться на Work Item, а порядок выполнения — выражаться prerequisite dependencies без изменения предметной модели.

## Результат проверки

| Изменение | Меняется Core | Где выражается |
| --- | --- | --- |
| другая структура компании | нет | `Work Unit` data |
| другой набор операций | нет | `Work Type` data |
| назначение одного или нескольких исполнителей | нет | Frappe Assign To / ToDo |
| декомпозиция крупной работы | нет | `parent_work_item` |
| prerequisite между работами | нет | `Work Dependency` |
| новый этап согласования | нет | Frappe Workflow |
| дополнительное поле конкретной компании | нет | Custom Field |
| новый тип предметного объекта | нет | обычный DocType + `references` |
| новый тип источника работы | нет | обычный DocType + `sources` |
| несколько предметных объектов у одной работы | нет | несколько `references` |
| несколько оснований одной работы | нет | несколько `sources` |
| интеграция с внешней системой | нет | Frappe integration mechanisms / extension App |

Четыре разные предметные области используют один и тот же контракт Work Unit → Work Type → Work Item. Отличия остаются локальными.

Это не доказывает, что Core никогда не изменится. Изменение Core оправдано только тогда, когда новая ответственность относится к самой семантике операционной работы и повторяется в разных предметных областях. Один специфический процесс отдельной компании для этого недостаточен.

## Публичный репозиторий и данные Site

Исходный репозиторий содержит схему продукта, controllers, reports, tests, документацию и полностью синтетические примеры.

Реальные Work Unit, Work Type, пользователи, документы, файлы, сотрудники, площадки, оборудование и Work Item являются данными конкретного `Site` и не должны экспортироваться в публичный Git.

Особое внимание требуется к Frappe fixtures: fixtures являются записями базы, экспортированными в JSON и синхронизируемыми при установке/обновлении App. В публичные fixtures включаются только данные, являющиеся частью самого продукта, например необходимые Roles. Рабочие данные организации fixtures не являются.

См. https://docs.frappe.io/framework/user/en/python-api/hooks#fixtures

## Архитектурная граница

```text
Frappe Framework
       │
       ▼
Work Management Core
├── Work Unit
├── Work Type
└── Work Item
    ├── parent_work_item
    ├── Work Dependency
    ├── Work Source
    └── Work Reference
       │
       ├── Site configuration
       ├── Frappe Assignments / Workflow / permissions / reports
       ├── optional capabilities after separate validation
       └── third-party or company-specific Apps
```

Core не знает о конкретной отрасли, компании, сотрудниках, оборудовании, терминалах, клиентах или внешних системах.

Расширения знают о Core только там, где им действительно нужна связь с выполняемой работой. Core не импортирует их предметную модель.
