# Work Management: Data Model v1

Этот документ фиксирует минимальную модель универсального ядра Work Management после проверки на нескольких предметных областях.

Цель v1 — дать точный контракт для реализации `Work Unit`, `Work Type`, `Work Item` и трёх child DocType, не добавляя в Core сотрудников, проекты, смены, оборудование, документооборот или другие предметные подсистемы.

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
    may be part of
another Work Item

Work Item
    may depend on
another Work Item

Work Item
    may have
sources and references
```

Frappe остаётся ответственным за `DocType`, ORM, Desk, Roles, User Permissions, Assign To / ToDo, Assignment Rule, Workflow, Notifications, Reports, Auto Repeat, REST API, background jobs и расширение конкретного `Site`.

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

Для `Work Unit`, `Work Type` и `Work Item` включается `Track Changes`. Это даёт штатную техническую историю изменения полей. Отдельный event log в Core v1 не вводится.

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

Базовый доступ к Work Item определяется штатными Roles/DocPerm Frappe. Конкретный Site при необходимости может дополнительно применять User Permissions или другие штатные ограничения, но такая конфигурация не меняет семантику Work Unit как очереди.

## Work Type

`Work Type` классифицирует повторяющийся смысл работы. Он не определяет маршрутизацию, приоритет или другие свойства конкретного Work Item.

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
| `description` | Small Text | нет | — | — | пояснение назначения вида работы |

`Work Type` не определяет ответственную очередь. Связь вида работы с конкретным Work Unit является routing policy конкретного `Site`, а не семантикой классификатора.

Work Type также не содержит source policy, SLA engine, assignment strategy, Workflow или произвольные automation rules.

В `Work Item.work_type` включается `ignore_user_permissions`, потому что Work Type является классификацией, а не измерением доступа к Work Item.

## Work Item

`Work Item` — одна конкретная исполнимая единица работы.

### Настройки DocType

```text
title_field       = subject
autoname          = WI-.YYYY.-.#####
track_changes     = 1
allow_auto_repeat = 1
```

Повторяемая работа использует штатный Frappe Auto Repeat. Work Item реализует только собственную семантику нового экземпляра через `on_recurring`.

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
| `waiting_reason` | Small Text | нет | — | нет | текущая причина ожидания |
| `waiting_since` | Datetime, Read Only | нет | — | нет | начало текущего ожидания |
| `started_at` | Datetime, Read Only | нет | — | нет | первое фактическое начало выполнения |
| `closed_at` | Datetime, Read Only | нет | — | нет | время текущего закрытия lifecycle |
| `parent_work_item` | Link → Work Item | нет | — | да | непосредственный родитель в декомпозиции работы |
| `dependencies` | Table → Work Dependency | нет | — | — | prerequisite Work Item |
| `sources` | Table → Work Source | нет | — | — | основания возникновения работы |
| `references` | Table → Work Reference | нет | — | — | связанные предметные документы |
| `auto_repeat` | Link → Auto Repeat, hidden | нет | — | нет | техническая ссылка штатного Auto Repeat |

`priority` является состоянием конкретного Work Item. Work Type не подставляет его автоматически, поэтому изменение классификатора не несёт скрытой policy приоритета.

`auto_repeat` — техническое поле интеграции со штатным Frappe Auto Repeat, а не предметное свойство работы.

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

Core не задаёт обязательный граф переходов. Если организации нужен собственный маршрут согласования, используется Frappe Workflow. Локальные workflow states могут обновлять канонический `status`, но не заменяют его семантику. Для такого сопоставления Workflow State использует `update_field = status` и `update_value` из канонического набора Work Management.

### Исполнители

Core не хранит собственного `assignee`.

Персональное выполнение выражается штатным Frappe Assign To / `ToDo`. Один Work Item может иметь:

```text
0 assignments
1 assignment
N assignments
```

Work Management не создаёт собственный assignment engine, не синхронизирует второе поле исполнителя с `ToDo` и не накладывает ограничение «только один исполнитель» поверх Framework.

### Hierarchy

`parent_work_item` выражает только непосредственное отношение **«текущая Work Item является частью другой Work Item»**.

Один Work Item может иметь не более одного непосредственного родителя. Дочерние Work Item являются самостоятельными документами и не наследуют автоматически:

```text
responsible_unit
assignments
status
priority
planned_start / due_at
```

Core не выполняет roll-up status или dates и не закрывает родителя автоматически после завершения дочерних работ.

Self-parent и циклы hierarchy запрещены.

### Dependencies

`Work Dependency` — child DocType с фиксированной семантикой prerequisite:

```text
Work Dependency
- depends_on -> Work Item
```

Строка находится внутри текущей Work Item и означает:

```text
current Work Item depends on depends_on
```

Обратное отношение `blocks` вычисляется из этих записей и отдельно не хранится.

Dependency не является workflow или scheduling rule. Core не блокирует lifecycle автоматически, не переносит даты и не вычисляет critical path.

Для одной Work Item запрещены:

- dependency на себя;
- duplicate `depends_on`;
- dependency cycle.

Универсальный `Relation Type` или relation engine не вводится.

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

`references` не используется для parent/child или prerequisite relation между Work Item.

## Security contract для связей

Связи Work Item не являются новой границей авторизации.

При добавлении или изменении `parent_work_item` или строки `dependencies` пользователь должен иметь `read` на целевую Work Item.

При добавлении или изменении строки `sources`/`references` пользователь должен иметь `read` на целевой документ. Проверяется новая или изменённая связь; собственный controller не перепроверяет старую связь только из-за последующего изменения permissions target document.

Пользователь, имеющий право читать Work Item, видит сохранённые relationship metadata. Сам target document продолжает защищаться собственными permissions.

Если сам факт существования связи чувствителен, такую связь нельзя хранить в Work Item, доступном более широкому кругу пользователей.

Для существования Link/Dynamic Link target Core полагается на штатную link validation Frappe и не создаёт собственный механизм ссылочной целостности.

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
7. `parent_work_item` не может ссылаться на сам Work Item и создавать hierarchy cycle.
8. `dependencies` не допускают self-reference, duplicates и dependency cycles.
9. Новая или изменённая parent/dependency связь требует `read` на target Work Item.
10. Новая или изменённая source/reference требует `read` на target document.

Frappe сам проверяет существование Link/Dynamic Link документов; Core не дублирует эту инфраструктурную проверку.

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

## Queue, assignments и доступ

`responsible_unit` хранит текущую организационную очередь Work Item и не является обязательной security boundary продукта.

По умолчанию пользователь, имеющий Role с `read` на Work Item, может читать Work Item независимо от его `responsible_unit`. Аналогично право `write` не превращает смену очереди в изменение ACL.

Assignments не являются отдельной ACL-моделью Work Management. Frappe сам управляет назначениями, `ToDo`, sharing и связанными permission checks.

Если конкретному Site нужна изоляция по Work Unit или дополнительные ограничения назначения, он может использовать штатные User Permissions, Permission Levels, Workflow или другое допустимое расширение Frappe. Такая политика не является универсальным контрактом Core.

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
| Work Dependency | через parent | через parent |
| Work Source | через parent | через parent |
| Work Reference | через parent | через parent |

Delete не выдаётся этим ролям по умолчанию. Устаревшие Work Unit и Work Type отключаются через `active = 0`; Work Item сохраняет историю вместо обычного удаления.

Core не вводит custom `permission_query_conditions`, собственную таблицу ACL или обязательную permission-семантику дерева Work Unit.

`Work Type` не должен становиться дополнительным ACL-измерением Work Item, поэтому его Link исключён из User Permission filtering через metadata `ignore_user_permissions`.

## Auto Repeat

Frappe Auto Repeat используется как штатный механизм простой календарной повторяемости. Work Management не создаёт собственный scheduler.

Frappe копирует reference document и вызывает `on_recurring`; Work Item использует этот hook для очистки instance-specific состояния.

Новый экземпляр получает:

```text
status = Open
waiting_reason = empty
waiting_since = empty
started_at = empty
closed_at = empty
planned_start = empty
due_at = empty
parent_work_item = empty
dependencies = empty
sources = empty
```

Сохраняются шаблонные данные:

```text
subject
description
work_type
responsible_unit
priority
references
```

`references` сохраняются как предметный контекст шаблона; `sources` очищаются, потому что они описывают происхождение конкретного экземпляра работы.

Assignments являются отдельными штатными `ToDo` и не копируются как поле Work Item. При необходимости Auto Repeat использует собственную штатную конфигурацию назначения пользователей.

## Индексы v1

Минимальный набор:

```text
Work Item.work_type
Work Item.responsible_unit
Work Item.status
Work Item.planned_start
Work Item.due_at
Work Item.parent_work_item

Work Dependency.depends_on

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
7. Первый вход в `In Progress` заполняет `started_at` один раз.
8. Вход в `Waiting` заполняет `waiting_since`; выход очищает текущие waiting fields.
9. `Done` и `Cancelled` заполняют `closed_at`; reopen очищает его.
10. `parent_work_item` допускает нормальную декомпозицию, но запрещает self-reference и hierarchy cycle.
11. `dependencies` запрещают duplicate, self-reference и dependency cycle.
12. Новая parent/dependency связь на недоступную пользователю Work Item запрещена.
13. Старая сохранённая parent/dependency связь не должна запускать собственную повторную read-проверку controller при несвязанном редактировании.
14. Новая source/reference на недоступный пользователю документ запрещена.
15. Старая сохранённая source/reference не блокирует редактирование Work Item только из-за последующего изменения permissions target document.
16. В базовой конфигурации `responsible_unit` является очередью, а не ACL: Work User без дополнительных User Permissions видит Work Item разных Work Unit и может менять очередь в пределах своего DocPerm.
17. User Permission на Work Type не превращает классификацию в дополнительную границу доступа к Work Item.
18. Work Item использует штатные Frappe Assignments и допускает несколько активных assignments одновременно.
19. Auto Repeat создаёт новый operational instance с очищенным lifecycle, dates, sources и Work Item structure при сохранении шаблонного контекста.
20. Site Workflow может обновлять канонический `status`, а lifecycle timestamps Work Item остаются корректными.

Тесты не должны перепроверять ORM, Dynamic Link, NestedSet, Workflow, Auto Repeat или ToDo как самостоятельные возможности Framework. Проверяется только то, что приложение действительно опирается на них в собственном data contract.

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
universal relation engine
```

Эти объекты не являются частью v1. Добавление каждого из них требует отдельной подтверждённой ответственности; распространённость похожего объекта в других task/project системах сама по себе недостаточна.

`Work Event` специально не требуется для первой реализации Core: сначала используются `Track Changes`, lifecycle timestamps и штатные Assignment/ToDo records. Event-level история добавляется только когда появляется реальная потребность в точной аналитике времени в состояниях, reassignments, reopen или handover.

## Публичный контракт v1

После появления стабильной версии следующие элементы считаются частью публичного data contract продукта:

```text
DocType names
fieldnames
canonical status values
priority values
required relations
semantics of parent_work_item
semantics of dependencies
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
