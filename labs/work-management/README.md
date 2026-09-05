# Work Management: универсальное ядро

Work Management — прототип open-source приложения управления операционной работой на Frappe Framework.

Цель модели — покрывать реальные процессы разных организаций, не превращая приложение в универсальный конструктор бизнес-сущностей и не создавая framework поверх Frappe. Конкретная организация настраивает структуру, виды работ, права, Workflow и собственные предметные объекты на своём `Site`.

## Граница продукта

Frappe остаётся прикладной платформой и отвечает за `DocType`, `Document`, ORM, Desk, permissions, Workflow, Notifications, Reports, REST API, background jobs и штатные механизмы расширения.

Work Management добавляет только семантику операционной работы.

Универсальное ядро состоит из трёх top-level DocType:

```text
Work Unit
Work Type
Work Item
```

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

Core не определяет модель членства сотрудников в Work Unit. Доступ настраивается штатными Roles и User Permissions Frappe; если конкретной организации нужна отдельная модель состава команды, должностей или мощности, она добавляется как самостоятельная capability.

## Work Type

`Work Type` классифицирует работу и хранит только простые общие настройки.

Минимальная семантика:

```text
title
active
default_responsible_unit   optional
default_priority           optional
requires_source            yes/no
```

`Work Type` не является workflow engine, rule engine или системой маршрутизации.

## Work Item

`Work Item` — одна конкретная исполнимая единица работы.

Стабильный контракт:

```text
subject
description

work_type
responsible_unit
assignee

status
priority

planned_start
due_at
estimated_effort

waiting_reason
next_action

started_at
completed_at

sources
references
```

### Sources

`sources` — child table узкой семантики **«на основании чего возникла работа?»**.

Каждая строка содержит:

```text
source_doctype   Link → DocType
source_name      Dynamic Link
```

Так Core не знает, является источником служебная записка, клиентский запрос, monitoring alert, договор, производственное несоответствие или другой документ.

`Work Type.requires_source` может требовать хотя бы один источник для видов работ, которые нельзя выполнять без основания.

### References

`references` — отдельная child table узкой семантики **«к каким предметным документам относится работа?»**.

Каждая строка также использует `DocType` + `Dynamic Link`.

Это позволяет одной Work Item одновременно относиться, например, к Project, сотруднику и оборудованию без добавления этих полей в Core.

`sources` и `references` не являются универсальным relation engine. Их семантика фиксирована самим понятием работы, а произвольные типы и правила отношений не моделируются.

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

## Расширение без изменения Core

Универсальность достигается не новыми meta-сущностями, а обычными механизмами Frappe.

```text
новое подразделение        → новая запись Work Unit
новый вид работы           → новая запись Work Type
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

Реальная установка может требовать больше трёх DocType. Это не делает их частью универсального Core.

### Documentary Records

`Basis Document` может хранить зарегистрированное документальное основание, его метаданные и attachments. Организации, где работа должна быть доказуемо связана со служебным, кадровым, распорядительным или иным документом, используют `Basis Document` как один из `sources` Work Item.

Сам `Basis Document` не входит в Core, потому что в других предметных областях источником может быть уже существующий Ticket, Alert, Contract, Nonconformity или другой DocType.

### Assets

Учёт индивидуально отслеживаемого оборудования может использовать собственные DocType, например:

```text
Asset Type
Tracked Asset
Asset Movement
Asset Composition Change
```

Новый вид оборудования в таком модуле является новой записью `Asset Type`, а не новым полем или новым типом Work Item.

Специфическая функция оборудования, например поверка, добавляется отдельным предметным DocType вроде `Asset Calibration`, не загрязняя Core.

### Reference Data

Конкретная установка может ссылаться на HRMS `Employee`, ERPNext `Asset`, собственные справочники или локальные read-only проекции внешней системы. Core не определяет единую модель сотрудника, техники, клиента или контрагента.

### Planning и Shift Operations

Project, shift journal и handover могут быть самостоятельными capabilities. Work Item связывается с ними через `references`; организация, которой они не нужны, не меняет Core.

## Проверка на разных организациях

Модель проверяется заменой предметной области. Критерий простой: если новый сценарий требует изменить семантику трёх Core DocType, ядро недостаточно универсально. Если отличие выражается данными Site, стандартной настройкой Frappe или отдельным предметным DocType, граница сохраняется.

### Сценарий 1. Промышленная операционная служба

Организация ведёт несколько направлений: диспетчеризацию, контроль документов, учёт, логистику и сменную работу. Значительная часть исправлений выполняется по документальному основанию. Есть сотрудники, производственные площадки, транспорт, измерительное оборудование и составные терминалы; часть объектов перемещается между площадками.

```text
Work Unit    → направления службы
Work Type    → сверка, проверка, исправление, регистрация, перемещение
Work Item    → конкретное действие сотрудника
sources      → Basis Document
references   → сотрудник, площадка, Asset Movement, Project и другие документы
```

Дополнительно используются Documentary Records, reference data, Assets и Shift Operations.

Одна работа может одновременно ссылаться на сотрудника и документ перемещения либо на Project и оборудование. Для этого Core не требует отдельных полей.

Изменение состава терминала или появление нового типа техники не меняет Core.

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

Источниками Work Item являются support ticket, monitoring alert или approved change request. В `references` могут одновременно находиться клиент, сервер, система и Project.

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

В `references` могут одновременно находиться партия, оборудование, производственный заказ и проект улучшения.

Смены, оборудование и будущая поверка подключаются как отдельные capabilities. Core остаётся прежним.

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

Assets и Shift Operations не используются вообще. Для работы достаточно Core и предметных DocType этой организации.

## Результат проверки

| Изменение | Меняется Core | Где выражается |
| --- | --- | --- |
| другая структура компании | нет | `Work Unit` data |
| другой набор операций | нет | `Work Type` data |
| новый этап согласования | нет | Frappe Workflow |
| дополнительное поле конкретной компании | нет | Custom Field |
| новый тип предметного объекта | нет | обычный DocType + `references` |
| новый тип источника работы | нет | обычный DocType + `sources` |
| несколько предметных объектов у одной работы | нет | несколько `references` |
| несколько оснований одной работы | нет | несколько `sources` |
| новая техника | нет | Asset capability / `Asset Type` |
| новый специфический процесс техники | нет | отдельный предметный DocType |
| сменная работа | нет | Shift capability |
| проекты | нет | Planning capability |
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
       │
       ├── Site configuration
       ├── Frappe Workflow / permissions / reports
       ├── first-party capabilities
       └── third-party or company-specific Apps
```

Core не знает о конкретной отрасли, компании, сотрудниках, оборудовании, терминалах, клиентах или внешних системах.

Расширения знают о Core только там, где им действительно нужна связь с выполняемой работой. Core не импортирует их предметную модель.