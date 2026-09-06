# Work Item v1

`Work Item` — основной документ текущего Work Management prototype. Он представляет сам факт работы. Назначения, комментарии, файлы, теги, коммуникации, повторение, представления и отчётность не дублируются собственными сущностями и полями, если соответствующую ответственность уже закрывает Frappe.

## DocType

```text
Name: Work Item
Module: Custom
Custom: Yes

Naming Rule: Autoincrement
Auto Name: autoincrement
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

Остальные настройки остаются штатными значениями Frappe, если отдельная ответственность не требует их изменить.

Техническое имя Work Item — последовательный идентификатор:

```text
1
2
3
...
```

Пользовательское название документа — `subject`.

## Поля

| Label | Fieldname | Type | Required | Default | No Copy | List | Filter | Global Search | Quick Entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Subject | `subject` | Data | yes | — | no | title | no | yes | yes, как required |
| Description | `description` | Text Editor | no | — | no | no | no | yes | yes |
| Status | `status` | Select | yes | `Open` | yes | yes | yes | no | yes, как required |
| Priority | `priority` | Select | yes | `Medium` | no | yes | yes | no | yes, как required |
| Due Date | `due_date` | Date | no | — | yes | yes | yes | no | yes |
| Links | `links` | Table → `Dynamic Link` | no | — | yes | no | no | no | no |

### `subject`

Краткое человеческое название работы.

Пример:

```text
Проверить путевые листы за август
```

Поле является `Title Field`, поэтому именно оно используется как основное название Work Item в пользовательском интерфейсе.

### `description`

Подробности и условия выполнения работы.

Пример:

```text
Проверить расхождения между выгрузкой 1С и журналом контроля.
Результат указать в комментарии.
```

Структурированные состояния, исполнители и классификация в `description` не кодируются.

### `status`

```text
Open
Waiting
Closed
Cancelled
```

Семантика:

- `Open` — работа актуальна и может выполняться;
- `Waiting` — работа актуальна, но продолжение зависит от внешнего события;
- `Closed` — работа полностью завершена;
- `Cancelled` — работа больше не требуется.

Типичные причины `Waiting`: ожидается ответ, согласование, документ или решение. Само назначение исполнителя не меняет `status`.

```text
Open + нет assignment
= свободная работа

Open + assignment
= открытая работа взята исполнителем

Waiting + assignment
= исполнитель остаётся ответственным, но продолжение сейчас невозможно
```

`In Progress` не используется: наличие активного assignment уже хранит факт персональной ответственности, а `status` не дублирует эту ось.

`status` имеет `No Copy = Yes`, чтобы новый экземпляр работы не наследовал `Waiting`, `Closed` или `Cancelled` от исходного документа.

### `priority`

```text
Low
Medium
High
```

Значения совпадают со стандартным `ToDo.priority` и ручным `Assign To` Frappe.

`priority` характеризует важность самой работы и копируется при обычном копировании/повторении как часть содержательного контекста.

### `due_date`

Необязательный общий срок самой работы.

Пустое значение означает, что общий срок не установлен.

`Work Item.due_date` не равен `ToDo.date`:

```text
Work Item.due_date = общий срок работы
ToDo.date          = Complete By конкретного assignment
```

Поле имеет `No Copy = Yes`, чтобы новый экземпляр не наследовал абсолютный срок старой работы.

### `links`

Необязательная таблица на стандартном child DocType `Dynamic Link`.

Она связывает Work Item с произвольными документами Frappe без собственного relation DocType.

Пример:

```text
Links

Purchase Order    PO-00015
Customer          ACME
Some Document     DOC-0042
```

`links` имеет `No Copy = Yes`: связь относится к конкретному экземпляру работы и не переносится автоматически в новую повторяющуюся работу.

## Assignment

Исполнитель не хранится собственным полем `Work Item`.

Используется штатный Frappe:

```text
Work Item
    ↓ Assign To
ToDo
```

Один Work Item может иметь ноль, один или несколько активных assignments.

```text
Work Item.status = состояние работы
ToDo             = назначение работы конкретному пользователю
```

Закрытие собственного `ToDo` не закрывает `Work Item`. Изменение `Work Item.status` также не закрывает связанные `ToDo` автоматически.

Это две независимые штатные модели состояния, и текущий native-first вариант не добавляет между ними собственную синхронизацию.

## Waiting

`Waiting` является полноценным состоянием Work Item, а не тегом.

Обычный цикл может выглядеть так:

```text
Open
↓ отправлен запрос
Waiting
↓ получен ответ
Open
↓ работа завершена
Closed
```

Отдельные поля `waiting_reason`, `waiting_since` и `waiting_until` пока не входят в модель. Конкретный контекст ожидания фиксируется в Timeline/Comments.

## Auto Repeat

Для календарного повторения используется штатный `Auto Repeat` Frappe. Собственный scheduler не создаётся.

Текущая схема специально не копирует:

```text
status
 due_date
links
```

Содержательный контекст, который может повторяться, остаётся в:

```text
subject
description
priority
```

Assignments Auto Repeat не являются обязательной частью модели: базовый сценарий оставляет новый Work Item в общей очереди.

## Communication

Письма не хранятся в собственных `source_email` или `source` полях Work Item.

Стандартный `Communication` Frappe может ссылаться на Work Item и отображаться в Timeline документа. Поэтому происхождение письма остаётся ответственностью `Communication`.

## Намеренно отсутствующие поля и сущности

В текущую модель не входят:

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

Они не добавляются ради потенциальной будущей функциональности. Новая сущность или поле появляются только при самостоятельной ответственности, которую нельзя корректно закрыть текущей моделью или штатным механизмом Frappe.

## Штатные механизмы вокруг Work Item

Текущая модель рассчитана на использование следующих возможностей Frappe без собственного frontend или движков:

```text
Assign To / ToDo
Comments / Timeline
Attachments
Tags
Communication
Auto Repeat
Assignment Rule (optional)
Notification
Roles / DocPerm
List View
Kanban
Calendar View
Report Builder
Number Card
Dashboard Chart
Workspace
```

## Текущие ограничения native-first варианта

1. `Work Item.status` и `ToDo.status` не синхронизируются автоматически.
2. `Work Item.due_date` и `ToDo.date` имеют разную семантику и не считаются одним сроком.
3. Стандартные DocPerm сами по себе не выражают правило «редактировать Work Item может только назначенный пользователь».
4. Более строгие инварианты не реализуются кодом до появления подтверждённой необходимости.

## Источники Frappe

Текущий ориентир — Frappe v16.

- [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [`Assign To` source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py)
- [`ToDo` source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/todo/todo.py)
- [`Auto Repeat` source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.py)
