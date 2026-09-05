# Work Management: Data Model v1

Этот документ фиксирует минимальную модель универсального ядра Work Management после проверки на нескольких предметных областях.

Цель v1 — дать точный контракт для реализации `Work Unit`, `Work Type`, `Work Item` и двух child DocType, не добавляя в Core сотрудников, проекты, смены, оборудование, документооборот или другие предметные подсистемы.

## Принцип

Core отвечает только за операционную работу:

```text
Work Unit
    owns
Work Item

Work Type
    classifies
Work Item

Work Item
    may have
sources and references
```

Frappe остаётся ответственным за `DocType`, ORM, Desk, Roles, User Permissions, Workflow, Notifications, Reports, REST API, background jobs и расширение конкретного `Site`.

Официальные механизмы, на которых основана модель:

- `DocType`: https://docs.frappe.io/framework/user/en/basics/doctypes
- `Link`, `Dynamic Link`, `Table`: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- controllers и lifecycle hooks: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- User Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming

## Общие решения

Все три top-level DocType используют внутренний стабильный `name`, не зависящий от пользовательского заголовка:

```text
Work Unit  → WU-00001
Work Type  → WT-00001
Work Item  → WI-2026-00001
```

Для этого используются стандартные naming expressions Frappe.

`unit_name`, `type_name` и `subject` являются `title_field`. Их можно менять без переименования записи и без изменения ссылок.

Для `Work Unit`, `Work Type` и `Work Item` включается `Track Changes`. Это даёт штатную техническую историю изменения полей. Отдельный event log в v1 не вводится.

Core не является submittable-моделью. Жизненный цикл Work Item выражается полем `status`, а процессы согласования конкретной организации при необходимости добавляются штатным Frappe `Workflow`.

## Work Unit

`Work Unit` — организационная очередь или зона ответственности, которой принадлежит работа.

Это не универсальная HR-модель и не обязательное отражение формальной оргструктуры.

### Настройки DocType

```text
is_tree       = 1
title_field   = unit_name
autoname      = WU-.#####
track_changes = 1
```

### Поля

| Fieldname | Type | Required | Default | Назначение |
| --- | --- | --- | --- | --- |
| `unit_name` | Data | да | — | отображаемое имя Work Unit |
| `parent_work_unit` | Link → Work Unit | нет | — | родитель в дереве |
| `is_group` | Check | да | 0 | может ли узел содержать дочерние Work Unit |
| `active` | Check | да | 1 | доступен ли Work Unit для новой работы |
| `description` | Small Text | нет | — | краткое пояснение ответственности |

`parent_work_unit` и `is_group` используются штатным Tree/NestedSet механизмом Frappe.

### Что не хранится в Work Unit

В Core нет таблицы участников Work Unit.

Причина: членство сотрудников, штат, должности и доступ — разные ответственности. В одной установке пользователи могут быть синхронизированы из HRMS, в другой — из внешнего каталога, в третьей Work Unit вообще является сервисной очередью, а не подразделением.

Доступ к Work Item ограничивается штатными Roles и User Permissions по `responsible_unit`. Если конкретной организации нужна отдельная модель членства или мощности команды, она добавляется как самостоятельная capability, а не в Core.

## Work Type

`Work Type` классифицирует повторяющийся смысл работы и хранит только простые defaults.

### Настройки DocType

```text
title_field   = type_name
autoname      = WT-.#####
track_changes = 1
```

### Поля

| Fieldname | Type | Required | Default | Дополнительно | Назначение |
| --- | --- | --- | --- | --- | --- |
| `type_name` | Data | да | — | Unique | отображаемое имя вида работы |
| `active` | Check | да | 1 | — | можно ли выбирать тип для новой работы |
| `default_responsible_unit` | Link → Work Unit | нет | — | — | подразделение по умолчанию |
| `default_priority` | Select | нет | — | — | приоритет по умолчанию |
| `description` | Small Text | нет | — | — | пояснение назначения вида работы |

`default_priority` использует те же значения, что `Work Item.priority`:

```text
Low
Medium
High
Urgent
```

Если `default_responsible_unit` задаётся или меняется, он должен быть active. Уже существующий Work Type не становится невалидным только потому, что его прежний default позднее отключили.

Work Type не содержит source policy, routing rules, SLA engine, assignment strategy, Workflow или произвольные automation rules.

## Work Item

`Work Item` — одна конкретная исполнимая единица работы.

### Настройки DocType

```text
title_field   = subject
autoname      = WI-.YYYY.-.#####
track_changes = 1
```

### Поля

| Fieldname | Type | Required | Default | Index | Назначение |
| --- | --- | --- | --- | --- | --- |
| `subject` | Data | да | — | нет | краткое название работы |
| `description` | Text Editor | нет | — | нет | подробное описание |
| `work_type` | Link → Work Type | да | — | да | классификация работы |
| `responsible_unit` | Link → Work Unit | да | — | да | владелец очереди/ответственности |
| `assignee` | Link → User | нет | — | да | текущий исполнитель |
| `status` | Select | да | Open | да | текущее состояние |
| `priority` | Select | да | — | нет | относительная важность |
| `planned_start` | Datetime | нет | — | да | планируемое начало |
| `due_at` | Datetime | нет | — | да | срок завершения |
| `estimated_effort` | Duration | нет | — | нет | ожидаемый объём труда |
| `waiting_reason` | Small Text | нет | — | нет | текущая причина ожидания |
| `next_action` | Small Text | нет | — | нет | ближайшее следующее действие |
| `started_at` | Datetime, Read Only | нет | — | нет | первое фактическое начало работы |
| `completed_at` | Datetime, Read Only | нет | — | нет | текущее время завершения |
| `sources` | Table → Work Source | нет | — | — | основания возникновения работы |
| `references` | Table → Work Reference | нет | — | — | связанные предметные документы |

`priority` не имеет metadata-default. В `before_validate` сначала используется `Work Type.default_priority`, а если он не задан — `Medium`. Так default Work Type действительно может работать и при этом сохранённый Work Item не зависит от будущего изменения Work Type.

Индексы задаются через стандартное свойство DocField `search_index`. Frappe при синхронизации схемы создаёт для таких полей обычные индексы БД:
https://github.com/frappe/frappe/blob/version-16/frappe/database/schema.py

Дополнительные compound indexes в v1 не вводятся: они должны появляться только после измерения реальных запросов.

### Priority

```text
Low
Medium
High
Urgent
```

Priority — только относительная важность работы. Он не заменяет срок, SLA или Workflow.

### Status

Core фиксирует только пять состояний:

```text
Open
In Progress
Waiting
Done
Cancelled
```

Их смысл одинаков для всех установок:

- `Open` — работа существует, но исполнение не начато;
- `In Progress` — работа выполняется;
- `Waiting` — продолжение зависит от внешнего условия или ожидаемого действия;
- `Done` — работа выполнена;
- `Cancelled` — работа прекращена без выполнения.

Core не задаёт допустимый граф переходов между статусами. Если организации нужен обязательный маршрут согласования, используется Frappe Workflow.

## Work Source

`Work Source` — child DocType с одной фиксированной семантикой: **на основании чего возник Work Item**.

### Настройки DocType

```text
is_child_table = 1
```

### Поля

| Fieldname | Type | Required | Index | Назначение |
| --- | --- | --- | --- | --- |
| `source_doctype` | Link → DocType | да | да | тип документа-источника |
| `source_name` | Dynamic Link, options=`source_doctype` | да | да | конкретный документ-источник |

Примеры источников в разных установках:

```text
Basis Document
Support Ticket
Monitoring Alert
Contract
Nonconformity
Customer Request
```

Core не перечисляет допустимые source DocType, не создаёт их универсальные аналоги и не решает, для каких видов работы source обязателен. Такое требование является policy конкретного процесса или отдельной capability.

## Work Reference

`Work Reference` — child DocType с другой фиксированной семантикой: **к каким предметным документам относится Work Item**.

### Настройки DocType

```text
is_child_table = 1
```

### Поля

| Fieldname | Type | Required | Index | Назначение |
| --- | --- | --- | --- | --- |
| `reference_doctype` | Link → DocType | да | да | тип связанного документа |
| `reference_name` | Dynamic Link, options=`reference_doctype` | да | да | конкретный связанный документ |

Одна работа может одновременно ссылаться, например, на Project, Employee и Tracked Asset. Это не превращает `references` в relation engine: типы отношений и произвольные relation rules в Core отсутствуют.

## Серверные инварианты

Собственный Python v1 ограничивается понятными проверками и автоматическим заполнением текущего состояния.

### Work Type.validate

Если `default_responsible_unit` задаётся или меняется, он должен ссылаться на active Work Unit.

### Work Item.validate

Проверяются только собственные контракты Work Item:

1. Если заданы `planned_start` и `due_at`, `due_at` не может быть раньше `planned_start`.
2. `Waiting` требует непустой `waiting_reason`.
3. Внутри `sources` не допускается повтор одной пары `(source_doctype, source_name)`.
4. Внутри `references` не допускается повтор одной пары `(reference_doctype, reference_name)`.
5. Новый или изменённый `work_type` должен быть active.
6. Новый или изменённый `responsible_unit` должен быть active.
7. Новый или изменённый `assignee` должен ссылаться на enabled Frappe User.

Frappe сам проверяет существование Link/Dynamic Link документов; Core не дублирует эту инфраструктурную проверку.

### Work Item.before_validate

Если значение ещё не задано явно:

- `responsible_unit` копируется из `Work Type.default_responsible_unit`;
- `priority` копируется из `Work Type.default_priority`;
- если default priority у Work Type отсутствует, используется `Medium`.

Defaults копируются в Work Item и дальше являются его собственным состоянием. Последующее изменение Work Type не переписывает уже созданные Work Item.

### Временные поля

При первом переходе в `In Progress`:

```text
started_at = now()
```

Повторные входы в `In Progress` не переписывают первое `started_at`.

При переходе в `Done`:

```text
completed_at = now()
```

Если Work Item уходит из `Done`, `completed_at` очищается, потому что документ снова не завершён. Предыдущий факт изменения остаётся в штатном `Version` благодаря `Track Changes`.

При выходе из `Waiting` текущее `waiting_reason` очищается. История старого значения остаётся в `Version`.

`Cancelled` не считается завершённой работой и не получает `completed_at`.

## Что Core намеренно не проверяет

### Принадлежность assignee к Work Unit

Core не вводит собственную модель членства и не делает `assignee` зависимым от HR-модели конкретной организации.

Штатная безопасность строится по `responsible_unit` через Frappe User Permissions. Организация может дополнительно потребовать правило «исполнитель должен иметь доступ к Work Unit» или «исполнитель должен состоять в подразделении», но это site policy или extension capability, а не универсальный контракт Work Item.

Так Core не привязывается к одной модели штатного расписания и не создаёт собственный permission engine.

### Обязательность source

Core хранит основания, но не определяет, когда они обязательны. Для одной компании источником любого исправления должен быть зарегистрированный документ, для другой Incident может возникнуть непосредственно из monitoring alert, а часть внутренних задач вообще не имеет внешнего основания.

Если процесс требует обязательного source, это правило добавляется Documentary Records capability, site-specific Server Script или extension App. Для такого требования не нужен новый механизм Core.

### SLA, routing и автоматическое распределение

Эти правила не входят в Work Type или Work Item. Используются стандартные Frappe механизмы либо отдельное предметное расширение, когда появляется реальная ответственность.

## Permissions v1

Продукт использует два прикладных Role:

```text
Work User
Work Manager
```

Консервативная базовая матрица:

| DocType | Work User | Work Manager |
| --- | --- | --- |
| Work Unit | Read | Read, Create, Write |
| Work Type | Read | Read, Create, Write |
| Work Item | Read, Create, Write | Read, Create, Write |
| Work Source | через parent | через parent |
| Work Reference | через parent | через parent |

Delete не выдаётся этим ролям по умолчанию. Устаревшие Work Unit и Work Type отключаются через `active = 0`; Work Item сохраняет историю вместо обычного удаления.

Доступ к Work Item ограничивается стандартными User Permissions по `Work Unit`. Поскольку `Work Unit` является Tree DocType, Frappe v16 распространяет User Permission родительского узла на descendants, если `hide_descendants` не включён:
https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user_permission/user_permission.py

Пример:

```text
Operations
├── Dispatch
└── Document Control
```

User Permission на `Operations` для менеджера даёт доступ к дочерним Work Unit через штатную семантику NestedSet/User Permission. Пользователю отдельного направления можно выдать permission только на его Work Unit.

Custom `permission_query_conditions` и собственная таблица ACL в v1 не используются.

## Индексы v1

Минимальный набор индексов ориентирован на основные рабочие выборки:

```text
Work Item.work_type
Work Item.responsible_unit
Work Item.assignee
Work Item.status
Work Item.planned_start
Work Item.due_at

Work Source.source_doctype
Work Source.source_name

Work Reference.reference_doctype
Work Reference.reference_name
```

Индексы на `started_at`, `completed_at`, `priority` и compound indexes не добавляются заранее. Если реальные отчёты покажут узкое место, индекс добавляется под измеренный запрос.

## Обязательные тесты собственного контракта

Минимальный automated test suite должен проверять:

1. Work Item нельзя сохранить с `due_at < planned_start`.
2. `Waiting` нельзя сохранить без `waiting_reason`.
3. Повтор одного source в одном Work Item запрещён.
4. Повтор одной reference в одном Work Item запрещён.
5. Inactive Work Type нельзя назначить новой или изменяемой Work Item.
6. Inactive Work Unit нельзя назначить новой или изменяемой Work Item.
7. Disabled User нельзя назначить новой или изменяемой Work Item.
8. Inactive Work Unit нельзя назначить новым или изменённым `default_responsible_unit` Work Type.
9. Defaults Work Type копируются только в пустые поля Work Item и не меняют исторические Work Item задним числом.
10. Если Work Type не задаёт priority, новый Work Item получает `Medium`.
11. Первый переход в `In Progress` заполняет `started_at` один раз.
12. `Done` заполняет `completed_at`, reopen очищает его.
13. User Permission на Work Unit ограничивает доступ к Work Item через `responsible_unit`.
14. User Permission на родительский Work Unit даёт менеджеру доступ к дочерним узлам в соответствии со штатной NestedSet-семантикой Frappe.

Тесты не должны перепроверять ORM, Dynamic Link или NestedSet как самостоятельные возможности Framework. Проверяется только то, что приложение действительно опирается на них в собственном security/data contract.

## Что остаётся вне Data Model v1

Не входят в Core и не должны добавляться в Work Item без отдельного доказанного основания:

```text
Employee
Work Membership
Project
Shift Log
Basis Document
Tracked Asset
Asset Movement
Asset Composition
Operational Location
Contractor
SLA
Work Event
custom workflow engine
assignment engine
scheduler
relation engine
```

Любой из этих объектов может появиться как отдельная capability или обычный DocType и связываться с Work Item через `sources` или `references`.

## Критерий изменения Core

Нового поля или DocType недостаточно обосновать фразой «может пригодиться».

Core меняется только если новая ответственность одновременно:

1. относится непосредственно к понятию операционной работы;
2. не закрывается штатным механизмом Frappe;
3. повторяется в нескольких независимых предметных областях;
4. не может быть локально выражена отдельным DocType/capability без изменения Work Item.

Пока эти условия не выполнены, Data Model v1 остаётся стабильным контрактом.