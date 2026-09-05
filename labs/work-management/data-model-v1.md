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

Frappe остаётся ответственным за `DocType`, ORM, Desk, Roles, User Permissions, Assignments/ToDo, Workflow, Notifications, Reports, REST API, background jobs и расширение конкретного `Site`.

Официальные механизмы, на которых основана модель:

- `DocType`: https://docs.frappe.io/framework/user/en/basics/doctypes
- `Link`, `Dynamic Link`, `Table`: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- controllers и lifecycle hooks: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- User Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Workflow: https://docs.frappe.io/framework/user/en/desk/workflow
- naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming

Правила совместимой кастомизации зафиксированы отдельно в [Compatibility Contract](compatibility.md).

## Общие решения

Все три top-level DocType используют внутренний стабильный `name`, не зависящий от пользовательского заголовка:

```text
Work Unit  → WU-00001
Work Type  → WT-00001
Work Item  → WI-2026-00001
```

`unit_name`, `type_name` и `subject` являются `title_field`. Их можно менять без переименования записи и без изменения ссылок.

Для `Work Unit`, `Work Type` и `Work Item` включается `Track Changes`. Это даёт штатную техническую историю изменения полей. Отдельный event log в v1 не вводится.

Core не является submittable-моделью. Жизненный цикл Work Item выражается полем `status`, а процессы согласования конкретной организации при необходимости добавляются штатным Frappe `Workflow`.

## Work Unit

`Work Unit` — организационная очередь или зона ответственности, которой принадлежит работа.

Это не универсальная HR-модель и не обязательное отражение формальной оргструктуры.

`Work Unit` не является обязательной ACL-границей Core. Поле `responsible_unit` хранит операционный факт владения очередью, а не право пользователя читать Work Item.

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

`parent_work_unit` и `is_group` используют штатный Tree/NestedSet механизм Frappe.

### Что не хранится в Work Unit

В Core нет таблицы участников Work Unit.

Членство пользователей, штат, должности и доступ — разные ответственности. В одной установке пользователи могут быть синхронизированы из HRMS, в другой — из внешнего каталога, в третьей Work Unit вообще является сервисной очередью, а не подразделением.

`Work Membership`, если используется, хранит организационный факт принадлежности к рабочей зоне. Он не является ACL.

Базовый доступ к Work Item определяется штатными Roles/DocPerm Frappe. Конкретный Site при необходимости может дополнительно применять User Permissions или другие штатные ограничения, но такая конфигурация не меняет семантику Work Unit как очереди.

## Work Type

`Work Type` классифицирует повторяющийся смысл работы и хранит только простые общие defaults, которые не создают маршрутизацию.

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
| `default_priority` | Select | нет | — | — | приоритет по умолчанию |
| `description` | Small Text | нет | — | — | пояснение назначения вида работы |

`default_priority` использует те же значения, что `Work Item.priority`:

```text
Low
Medium
High
Urgent
```

`Work Type` не определяет ответственную очередь. Связь вида работы с конкретным Work Unit является routing policy конкретного `Site`, а не семантикой классификатора.

Work Type также не содержит source policy, SLA engine, assignment strategy, Workflow или произвольные automation rules.

В `Work Item.work_type` включается `ignore_user_permissions`, потому что Work Type является классификацией, а не измерением доступа к Work Item.

## Work Item

`Work Item` — одна конкретная исполнимая единица работы.

### Настройки DocType

```text
title_field   = subject
autoname      = WI-.YYYY.-.#####
track_changes = 1
```

`allow_auto_repeat` в v1 не включается. Повторяемая работа должна использовать Frappe Auto Repeat только после определения явной семантики копирования полей через штатный `on_recurring`.

### Поля

| Fieldname | Type | Required | Default | Index | Назначение |
| --- | --- | --- | --- | --- | --- |
| `subject` | Data | да | — | нет | краткое название работы |
| `description` | Text Editor | нет | — | нет | подробное описание |
| `work_type` | Link → Work Type | да | — | да | классификация работы |
| `responsible_unit` | Link → Work Unit | да | — | да | текущая очередь/зона ответственности |
| `status` | Select | да | Open | да | текущее каноническое состояние |
| `priority` | Select | да | — | нет | относительная важность |
| `planned_start` | Datetime | нет | — | да | планируемое начало |
| `due_at` | Datetime | нет | — | да | срок завершения |
| `estimated_effort` | Duration | нет | — | нет | ожидаемый объём труда |
| `waiting_reason` | Small Text | нет | — | нет | текущая причина ожидания |
| `waiting_since` | Datetime, Read Only | нет | — | нет | начало текущего ожидания |
| `next_action` | Small Text | нет | — | нет | ближайшее следующее действие |
| `started_at` | Datetime, Read Only | нет | — | нет | первое фактическое начало выполнения |
| `closed_at` | Datetime, Read Only | нет | — | нет | время текущего закрытия lifecycle |
| `sources` | Table → Work Source | нет | — | — | основания возникновения работы |
| `references` | Table → Work Reference | нет | — | — | связанные предметные документы |

`priority` не имеет metadata-default. В `before_validate` сначала используется `Work Type.default_priority`, а если он не задан — `Medium`. Значение копируется в Work Item и дальше является его собственным состоянием.

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

Core фиксирует пять канонических состояний:

```text
Open
In Progress
Waiting
Done
Cancelled
```

Их смысл одинаков для всех установок:

- `Open` — работа существует, но выполнение не начато;
- `In Progress` — работа выполняется;
- `Waiting` — продолжение зависит от внешнего условия или ожидаемого действия;
- `Done` — работа выполнена;
- `Cancelled` — работа прекращена без выполнения.

Core не задаёт обязательный граф переходов. Если организации нужен собственный маршрут согласования, используется Frappe Workflow. Локальные workflow states могут обновлять канонический `status`, но не заменяют его семантику.

### Assignment

Конкретный исполнитель не хранится отдельным полем Work Item.

Для персонального назначения используется штатный Frappe Assignment/ToDo. Core не создаёт собственную параллельную модель `assignee`.

```text
responsible_unit  = текущая очередь работы
Frappe Assignment = персонально назначенный исполнитель
```

Назначение не меняет семантику очереди и не является отдельной ACL-моделью Work Management. Доступ при Assign To остаётся ответственностью штатных permissions и Sharing Frappe.

## Work Source

`Work Source` — child DocType с фиксированной семантикой: **на основании чего возник Work Item**.

```text
source_doctype   Link → DocType
source_name      Dynamic Link, options=source_doctype
```

Core не перечисляет допустимые source DocType и не решает, для каких видов работы source обязателен. Такое требование является policy конкретного процесса или отдельной capability.

## Work Reference

`Work Reference` — child DocType с другой фиксированной семантикой: **к каким предметным документам относится Work Item**.

```text
reference_doctype   Link → DocType
reference_name      Dynamic Link, options=reference_doctype
```

Одна работа может ссылаться на несколько предметных документов. Это не relation engine: произвольные relation types и relation rules в Core отсутствуют.

## Security contract для sources и references

Dynamic Link используется как связь данных, но не как новая граница авторизации.

При добавлении или изменении строки `sources`/`references` пользователь должен иметь `read` на целевой документ. Проверяется только новая или изменённая связь; уже сохранённая историческая связь не должна делать Work Item невалидным после последующего изменения прав на target document.

Пользователь, имеющий право читать Work Item, видит метаданные сохранённой связи (`doctype` и `name`). Сам связанный документ продолжает защищаться собственными permissions.

Если сам факт существования связи чувствителен, такую ссылку нельзя хранить в Work Item, доступном более широкому кругу пользователей.

Для rename/delete Core полагается на штатную обработку Dynamic Link в Frappe и не создаёт собственный механизм ссылочной целостности.

## Серверные инварианты

Собственный Python v1 ограничивается проверками собственного контракта и заполнением текущего lifecycle state.

### Work Item.validate

Проверяются:

1. Если заданы `planned_start` и `due_at`, `due_at` не может быть раньше `planned_start`.
2. `Waiting` требует непустой `waiting_reason`.
3. Внутри `sources` не допускается повтор пары `(source_doctype, source_name)`.
4. Внутри `references` не допускается повтор пары `(reference_doctype, reference_name)`.
5. Новый или изменённый `work_type` должен быть active.
6. Новый или изменённый `responsible_unit` должен быть active.
7. Новая или изменённая source/reference должна указывать на документ, который текущий пользователь может читать.

Frappe сам проверяет существование Link/Dynamic Link документов; Core не дублирует эту инфраструктурную проверку.

### Work Item.before_validate

Если `priority` ещё не задан явно:

- используется `Work Type.default_priority`;
- если он отсутствует, используется `Medium`.

### Временные поля

При первом переходе в `In Progress`:

```text
started_at = now()
```

Повторные входы в `In Progress` не переписывают первое `started_at`.

При входе в `Waiting`:

```text
waiting_since = now()
```

Пока Work Item остаётся в `Waiting`, timestamp не переписывается. При выходе из `Waiting` очищаются текущее `waiting_since` и `waiting_reason`.

При входе в `Done` или `Cancelled`:

```text
closed_at = now()
```

Если Work Item возвращается из terminal state в активное состояние, `closed_at` очищается. Предыдущие значения остаются в штатной истории `Version` благодаря `Track Changes`.

## Queue и доступ

`responsible_unit` хранит текущую организационную очередь Work Item и не является обязательной security boundary продукта.

По умолчанию пользователь, имеющий Role с `read` на Work Item, может читать Work Item независимо от его `responsible_unit`. Аналогично право `write` не превращает смену очереди в изменение ACL.

Если конкретному Site нужна изоляция по Work Unit, он может дополнительно использовать штатные User Permissions, Permission Levels, Workflow или другое допустимое расширение Frappe. Такая политика не является универсальным контрактом Core.

## Work Membership и доступ

`Work Membership`, если capability используется, хранит организационный факт: пользователь относится к Work Unit в определённый период.

Он может использоваться для фильтра выбора исполнителя, аналитики состава команды и валидации локального организационного правила. Он не заменяет Roles/User Permissions и не является вторым permission engine.

```text
Work Membership = organizational fact
Frappe permissions = access control
```

## Permissions v1

Продукт использует два прикладных Role:

```text
Work User
Work Manager
```

Базовая матрица:

| DocType | Work User | Work Manager |
| --- | --- | --- |
| Work Unit | Read | Read, Create, Write |
| Work Type | Read | Read, Create, Write |
| Work Item | Read, Create, Write | Read, Create, Write |
| Work Source | через parent | через parent |
| Work Reference | через parent | через parent |

Delete не выдаётся этим ролям по умолчанию. Устаревшие Work Unit и Work Type отключаются через `active = 0`; Work Item сохраняет историю вместо обычного удаления.

Core не вводит custom `permission_query_conditions`, собственную таблицу ACL или обязательную permission-семантику дерева Work Unit.

`Work Type` не должен становиться дополнительным ACL-измерением Work Item, поэтому его Link исключён из User Permission filtering через metadata `ignore_user_permissions`.

## Auto Repeat

Frappe Auto Repeat остаётся предпочтительным механизмом простой календарной повторяемости, но v1 не включает его для Work Item автоматически.

Причина: Auto Repeat копирует исходный документ. Для Work Item необходимо явно определить, какие поля являются шаблонными, а какие относятся только к конкретному экземпляру работы. В частности нельзя бездумно переносить в следующий экземпляр текущее состояние, timestamps и документальные основания прошлого выполнения.

Перед включением `allow_auto_repeat` отдельный контракт должен определить поведение `on_recurring` как минимум для:

```text
status
waiting_reason
waiting_since
started_at
closed_at
planned_start
due_at
sources
references
```

Assignments/ToDo являются отдельными документами Frappe и не входят в копируемое состояние Work Item.

Собственный scheduler для этого не создаётся.

## Индексы v1

Минимальный набор:

```text
Work Item.work_type
Work Item.responsible_unit
Work Item.status
Work Item.planned_start
Work Item.due_at

Work Source.source_doctype
Work Source.source_name

Work Reference.reference_doctype
Work Reference.reference_name
```

Индексы на timestamps, priority и compound indexes не добавляются заранее. Они появляются под измеренные запросы.

## Обязательные тесты собственного контракта

Минимальный automated test suite должен проверять:

1. `due_at < planned_start` запрещён.
2. `Waiting` без `waiting_reason` запрещён.
3. Duplicate source запрещён.
4. Duplicate reference запрещена.
5. Inactive Work Type нельзя назначить новой или изменяемой Work Item.
6. Inactive Work Unit нельзя назначить новой или изменяемой Work Item.
7. Default priority копируется только в пустое поле и не меняет старые Work Item задним числом.
8. При отсутствии default priority используется `Medium`.
9. Первый вход в `In Progress` заполняет `started_at` один раз.
10. Вход в `Waiting` заполняет `waiting_since`; выход очищает текущие waiting fields.
11. `Done` и `Cancelled` заполняют `closed_at`; reopen очищает его.
12. Новая source/reference на недоступный пользователю документ запрещена.
13. Старая сохранённая source/reference не блокирует редактирование Work Item только из-за последующего изменения permissions target document.
14. В базовой конфигурации `responsible_unit` является очередью, а не ACL: Work User без дополнительных User Permissions видит Work Item разных Work Unit и может менять очередь в пределах своего DocPerm.
15. User Permission на Work Type не превращает классификацию в дополнительную границу доступа к Work Item.
16. Штатный Frappe Assignment создаёт ToDo для Work Item и используется вместо собственного `assignee` field.
17. Включение site Workflow не разрушает каноническую семантику `status`.

Тесты не должны перепроверять ORM, Dynamic Link, NestedSet или Assignments как самостоятельные возможности Framework. Проверяется только то, что приложение действительно опирается на них в собственном data contract.

## Что остаётся вне Data Model v1

Не входят в Core:

```text
Employee
Work Membership
Work Request
Work Project
Work Shift
Basis Document
Tracked Asset
Tracked Asset Movement
Tracked Asset Composition Change
Operational Location
SLA
Work Event
custom workflow engine
assignment engine
scheduler
relation engine
```

Любой из этих объектов может появиться как отдельная capability или обычный DocType и связываться с Work Item через `sources` или `references`.

`Work Event` специально не требуется для первой реализации Core: сначала используются `Track Changes` и lifecycle timestamps. Event-level история добавляется только когда появляется реальная потребность в точной аналитике времени в состояниях, reassignments, reopen или handover.

## Публичный контракт v1

После появления стабильной версии следующие элементы считаются частью публичного data contract продукта:

```text
DocType names
fieldnames
canonical status values
priority values
required relations
semantics of sources
semantics of references
```

Добавление нового поля или capability совместимо. Переименование, удаление или изменение смысла существующего элемента требует миграции и не должно происходить как скрытая внутренняя правка.

## Критерий изменения Core

Core меняется только если новая ответственность одновременно:

1. относится непосредственно к понятию операционной работы;
2. не закрывается штатным механизмом Frappe;
3. повторяется в нескольких независимых предметных областях;
4. не может быть локализована отдельной capability или настройкой Site.

Один частный процесс отдельной организации не является основанием менять Core.
