# Модель данных v1: `Work Item`

`Work Item` — основной документ прототипа управления работой. Он представляет сам факт работы. Всё, что уже имеет собственную сущность или механизм во Frappe, не дублируется в предметной модели.

## Поставка модели

```text
App package: veqta_work_management
App Title: VEQTA Work Management
Module: VEQTA Work Management
DocType: Work Item
Custom: No
```

`Work Item` — standard DocType App. App нужен для штатной разработки и воспроизводимой поставки metadata, а не для введения дополнительных архитектурных слоёв.

## DocType

```text
Name: Work Item
Module: VEQTA Work Management
Custom: No

Naming Rule: Expression
Auto Name: WI-.#####
Title Field: subject
Show Title Field in Link: Yes
Search Fields: subject
Allow Rename: No

Is Submittable: No
Is Single: No
Is Tree: No

Quick Entry: Yes
Track Changes: Yes
Track Seen: No
Track Views: No

Allow Auto Repeat: Yes

Default View: List
Is Calendar and Gantt: No
Force Re-route to Default View: No

Sort Field: creation
Sort Order: DESC
```

Технические имена документов:

```text
WI-00001
WI-00002
WI-00003
```

Пользовательским названием остаётся `subject`. Префикс нужен только как короткий читаемый идентификатор документа.

## Предметные поля

Предметная модель содержит шесть полей:

| Source label | Fieldname | Type | Required | Default | No Copy | List | Standard Filter | Global Search | Quick Entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Subject | `subject` | Data | yes | — | no | title | no | yes | yes |
| Description | `description` | Text Editor | no | — | no | no | no | yes | yes |
| Status | `status` | Select | yes | `Open` | yes | yes | yes | no | yes |
| Priority | `priority` | Select | yes | `Medium` | no | yes | yes | no | yes |
| Due Date | `due_date` | Date | no | — | yes | yes | yes | no | yes |
| Links | `links` | Table → `Dynamic Link` | no | — | yes | no | no | no | no |

`Section Break` и `Column Break` относятся к layout metadata и не являются предметными полями.

Технические `fieldname` и значения `Select` остаются английскими. Русское отображение App поставляется через Gettext.

## Компоновка формы

```text
РАБОТА
Название
Описание

ПАРАМЕТРЫ
Статус | Приоритет | Срок работы

СВЯЗИ
Связи
```

Для такой компоновки достаточно штатных `Section Break` / `Column Break`; собственный CSS не нужен.

## `subject`

Краткое человеческое название работы. Поле является `Title Field`.

Пример:

```text
Проверить путевые листы за август
```

## `description`

Подробности и условия выполнения работы.

Исполнители, статусы и структурированные связи в текст не кодируются.

## `status`

Технические значения:

```text
Open
Waiting
Closed
Cancelled
```

Семантика:

- `Open` — работа актуальна и может выполняться;
- `Waiting` — работа актуальна, но продолжение зависит от внешнего события;
- `Closed` — работа завершена;
- `Cancelled` — работа больше не требуется.

```text
Open + нет назначения = свободная работа
Open + назначение     = работа с персонально ответственным пользователем
Waiting + назначение  = исполнитель остаётся ответственным
```

Отдельное `In Progress` не используется. Активный `ToDo` хранит факт персональной ответственности, но сам по себе не является сохранённым фактом начала выполнения. В базовом pull-сценарии `Assign to me` означает, что пользователь принимает Work Item на себя. Если потребуется отдельно различать «назначено» и «фактически начато», это будет новая ответственность модели, а не вывод из `_assign` или `ToDo`.

`status` имеет `No Copy = Yes`, чтобы новый экземпляр не наследовал состояние исходного документа.

### Связь с `ToDo`

`Work Item.status` и `ToDo.status` — независимые состояния разных сущностей.

```text
Work Item.status = состояние общей работы
ToDo.status      = состояние конкретного назначения
```

Baseline не добавляет автоматическую синхронизацию между ними:

- закрытие `ToDo` не меняет `Work Item.status`;
- `Closed` или `Cancelled` у Work Item не закрывает и не отменяет связанные `ToDo` автоматически;
- App не запрещает штатному `Assign To` создавать назначения по собственной семантике Frappe.

Если живой прототип покажет, что между этими состояниями нужен обязательный инвариант, он проектируется отдельно на основании реального сценария.

## `priority`

Технические значения:

```text
Low
Medium
High
```

Они совпадают со стандартным `ToDo.priority`. В Frappe v16.33.0 стандартный Assign To dialog использует `doc.priority` как default, если значение входит в `Low / Medium / High`, поэтому преобразование не требуется. Это удобный default UI, а не синхронизация: пользователь может выбрать другой приоритет назначения.

`priority` копируется при повторении как часть содержательного контекста работы.

## `due_date`

Необязательный общий срок работы. В русском интерфейсе это «Срок работы».

```text
Work Item.due_date = общий срок работы
ToDo.date          = Complete By конкретного назначения
```

Это разные данные и они не синхронизируются автоматически.

В стандартном Assign To dialog `Complete By` можно оставить пустым, но серверный `frappe.desk.form.assign_to` в этом случае создаёт `ToDo.date` с текущей датой. Следовательно:

```text
пустой Work Item.due_date ≠ пустой ToDo.date
Work Item.due_date        ≠ default для ToDo.date
```

Если появится требование автоматически передавать общий срок работы в назначение, сначала проверяется штатный `Assignment Rule.due_date_based_on`. Ручную синхронизацию Work Item → ToDo не следует вводить раньше такого требования.

`due_date` имеет `No Copy = Yes`, чтобы новый экземпляр не наследовал абсолютную дату старой работы.

### Почему нет Calendar/Gantt

`due_date` — одна точка, а стандартный Calendar/Gantt Frappe работают с интервалом. Baseline не вводит фиктивные `start_date`, `end_date`, `progress` или `end = due_date` только ради представления.

Если появится реальная ответственность планового интервала, модель и представления пересматриваются из этого требования.

## `links`

`links` — необязательная таблица на стандартном дочернем DocType `Dynamic Link`.

Пример:

```text
Purchase Order    PO-00015
Customer          ACME
Some Document     DOC-0042
```

Отдельный DocType связей не создаётся. `links` имеет `No Copy = Yes`, потому что связь относится к конкретному экземпляру работы.

## Назначения

Исполнитель не хранится собственным полем `Work Item`:

```text
Work Item
    ↓ Assign To
ToDo
```

Один Work Item может иметь ноль, одно или несколько назначений. Системное `_assign` остаётся внутренним механизмом Frappe и не становится нашим предметным API-полем.

Стандартный Assign To различает завершение и снятие назначения:

- `close` завершает ToDo и разрешён только самому assignee;
- `remove` переводит назначение в `Cancelled`; пользователь с Write на исходный Work Item может снять чужое назначение штатным UI.

Для доверенной общей очереди это принимается как штатная семантика Frappe. Если потребуется запретить снятие чужих назначений, это станет отдельным server-side правилом.

## Ожидание

`Waiting` является состоянием Work Item, а не отдельной сущностью:

```text
Open
↓ отправлен запрос
Waiting
↓ получен ответ
Open
↓ работа завершена
Closed
```

Поля `waiting_reason`, `waiting_since` и `waiting_until` пока не нужны. Контекст ожидания фиксируется в Timeline/Comments.

## Auto Repeat

Используется штатный `Auto Repeat`. Собственный scheduler не создаётся.

При `Allow Auto Repeat = Yes` Frappe сам добавляет служебный `auto_repeat`; это framework field, а не седьмое предметное поле.

При повторении:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → default Open
due_date     → не копируется
links        → не копируются
назначения   → не являются полями Work Item
```

Для назначения повторяющихся экземпляров сначала используются нативные возможности по ответственности:

- фиксированный assignee — `Auto Repeat.assignee`;
- автоматический выбор пользователя — `Assignment Rule`;
- относительный `Work Item.due_date` или другая логика самого нового документа — `Work Item.on_recurring`.

`Auto Repeat` уже вызывает `on_recurring` после подготовки нового документа, поэтому отдельный scheduler для такой логики не нужен.

## Communication

`Communication` может быть связан с Work Item и отображаться в Timeline. Письма не копируются в собственные `source_email` или `source` поля.

При этом baseline не выдаёт `VEQTA Work User` право `Email` на Work Item и не заявляет отдельный почтовый workflow. Наличие `Communication` как штатной связанной сущности и право пользователя отправлять письмо из формы — разные ответственности.

## Намеренно отсутствующие поля и сущности

```text
Work Unit
Work Type
Work Source
Work Reference
Work Dependency
assignee
assigned_to
responsible_unit
parent_work_item
started_at
closed_at
closed_by
waiting_reason
waiting_since
waiting_until
planned_start
estimated_effort
SLA
progress
start_date
end_date
```

Новая сущность или поле появляются только при самостоятельной ответственности, которую нельзя корректно закрыть текущей моделью или штатным механизмом Frappe.

## Что проверять на живом Site

Проверяется именно граница нашей конфигурации:

1. `Work Item` создаётся как standard DocType App.
2. Назначения работают через штатный `Assign To / ToDo` без собственного поля исполнителя.
3. `Work Item.status` и `ToDo.status` фактически остаются независимыми.
4. `priority` корректно подхватывается стандартным Assign To dialog как default.
5. При пустом `Complete By` фактический `ToDo.date` соответствует штатному default текущей версии.
6. Пользователь с Write на Work Item может снять чужое назначение, а завершить его через `close` может только assignee.
7. Auto Repeat соблюдает `No Copy` metadata текущей модели и штатную семантику assignee.

## Источники Frappe

Текущий проверочный ориентир — Frappe v16.33.0.

- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Naming`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/naming.py)
- [`DocType`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Assign To dialog`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [`ToDo`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Assignment Rule`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/assignment_rule/assignment_rule.py)
