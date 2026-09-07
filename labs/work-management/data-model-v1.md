# Модель данных v1: `Work Item`

`Work Item` — основной документ текущего прототипа управления работой. Он представляет сам факт работы. Назначения, комментарии, файлы, теги, коммуникации, повторение и представления не дублируются собственными сущностями, если соответствующую ответственность уже закрывает Frappe.

## Поставка модели

`Work Item` проектируется как standard DocType минимального Frappe App:

```text
App package: veqta_work_management
App Title: VEQTA Work Management
Module: VEQTA Work Management
DocType: Work Item
Custom: No
```

App нужен для штатной разработки и воспроизводимой доставки metadata и небольшого прикладного контракта `Work Item`. Он не добавляет отдельный service/repository layer.

## DocType

```text
Name: Work Item
Module: VEQTA Work Management
Custom: No

Naming Rule: Expression
Auto Name: VWM-WI-.#####
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
VWM-WI-00001
VWM-WI-00002
VWM-WI-00003
```

Пользовательским названием остаётся `subject`. Префикс нужен для устойчивой идентификации в ссылках, логах и интеграциях; он не заменяет человеческое название.

`Autoincrement` не используется: после начала эксплуатации Frappe ограничивает смену такого naming mode, а голые числовые имена хуже различимы за пределами конкретного DocType.

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

`Section Break` и `Column Break`, используемые для компоновки формы, являются layout metadata и не считаются предметными полями.

Технические `fieldname` и значения `Select` остаются английскими. Русское отображение App поставляется через Gettext `locale/main.pot` и `locale/ru.po`; общие переводы Frappe не дублируются без необходимости.

## Компоновка формы

Форма разделяется штатными layout fields Frappe:

```text
РАБОТА
Название
Описание

ПАРАМЕТРЫ
Статус | Приоритет | Срок

СВЯЗИ
Связи
```

Собственный CSS или frontend для этой компоновки не нужен.

## `subject`

Краткое человеческое название работы. Поле является `Title Field`.

Пример:

```text
Проверить путевые листы за август
```

## `description`

Подробности и условия выполнения работы.

Пример:

```text
Проверить расхождения между выгрузкой 1С и журналом контроля.
Результат указать в комментарии.
```

Исполнители и состояния в `description` не кодируются.

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
- `Closed` — работа полностью завершена;
- `Cancelled` — работа больше не требуется.

```text
Open + нет назначения = свободная работа
Open + назначение     = работа взята исполнителем
Waiting + назначение  = исполнитель остаётся ответственным
```

Отдельное `In Progress` не используется: оно дублировало бы факт активного назначения.

`status` имеет `No Copy = Yes`, чтобы новый экземпляр не наследовал `Waiting`, `Closed` или `Cancelled`.

### Терминальные состояния

`Closed` и `Cancelled` создают собственный прикладной контракт, которого нет в стандартном `Assign To` автоматически:

```text
Work Item → Closed
→ все активные связанные ToDo становятся Closed

Work Item → Cancelled
→ все активные связанные ToDo становятся Cancelled
→ уже Closed ToDo остаются Closed
```

Обратной автоматизации нет:

```text
ToDo → Closed
≠
Work Item → Closed
```

Один Work Item может иметь несколько назначений, поэтому завершение одного назначения не доказывает завершение всей работы.

Нельзя также создавать или повторно открывать активный `ToDo`, если его `reference_type = Work Item`, а связанный Work Item уже `Closed` или `Cancelled`. Это серверный инвариант App, а не UI-ограничение.

Для реализации используются официальные extension points Frappe:

- controller `Work Item.on_update`;
- `doc_events` для `ToDo.validate`, ограниченный только `reference_type = Work Item`;
- `assign_to.close_all_assignments()` для `Closed`;
- `assign_to.set_status()` только для активных ToDo при `Cancelled`.

`assign_to.clear()` здесь не используется: он отменяет все ToDo, связанные с документом, и тем самым может переписать уже закрытую историю назначения.

## `priority`

Технические значения:

```text
Low
Medium
High
```

Они совпадают со стандартным `ToDo.priority`. В Assign To dialog Frappe v16.33.0 использует `doc.priority` как default, если значение входит в `Low / Medium / High`, поэтому отдельное преобразование не нужно.

`priority` копируется при повторении как часть содержательного контекста работы.

## `due_date`

Необязательный общий срок самой работы.

```text
Work Item.due_date = общий срок работы
ToDo.date          = Complete By конкретного назначения
```

Это разные данные. Assign To не обязан автоматически копировать `due_date` в `ToDo.date`; пользователь может задать срок конкретного назначения отдельно.

`due_date` имеет `No Copy = Yes`, чтобы новый экземпляр не наследовал абсолютную дату старой работы.

### Почему нет Calendar/Gantt

`due_date` — одна точка, а стандартный Calendar Frappe работает с `start/end` и позволяет менять даты через интерфейс. Использование одного `due_date` одновременно как `start` и `end` создаёт неоднозначную запись обратно в документ.

Поэтому baseline не включает Calendar/Gantt и не добавляет ради них фиктивные `start_date`, `end_date`, `progress` или длительность. Если в предметной модели появится реальный плановый интервал, представления проектируются уже из этой новой ответственности.

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

Один Work Item может иметь ноль, одно или несколько активных назначений.

```text
Work Item.status = состояние общей работы
ToDo             = назначение конкретному пользователю
```

Системное `_assign` используется самим Frappe для отображения назначений, но не становится нашим предметным API-полем.

## Ожидание

`Waiting` является состоянием Work Item, а не тегом:

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

Для календарного повторения используется штатный `Auto Repeat`. Собственный scheduler не создаётся.

При `Allow Auto Repeat = Yes` Frappe сам добавляет служебный `auto_repeat`; это framework field, а не седьмое предметное поле.

При повторении:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → default Open
due_date     → не копируется
links        → не копируются
назначения   → не являются обязательной частью baseline
```

Если появится правило относительного срока, первым extension point является `Work Item.on_recurring`, который вызывается Auto Repeat. Отдельный scheduler для этого не нужен.

## Communication

Письма не копируются в собственные `source_email` или `source` поля. Стандартный `Communication` может быть связан с Work Item и отображаться в Timeline.

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

## Что нужно тестировать в App

Тестируются наши контракты, а не стандартный Frappe:

1. `Closed` закрывает все активные `ToDo` этого Work Item.
2. `Cancelled` отменяет активные `ToDo`, не переписывая уже `Closed` назначения.
3. активный `ToDo` нельзя создать или повторно открыть для terminal Work Item.
4. закрытие одного `ToDo` не меняет `Work Item.status`.
5. повторение не переносит `status`, `due_date` и `links`.

## Источники Frappe

Текущий проверочный ориентир — Frappe v16.33.0.

- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Naming`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/naming.py)
- [`DocType`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`ToDo`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Document hooks`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py)
- [`Gettext commands`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)