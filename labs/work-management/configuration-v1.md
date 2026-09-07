# Конфигурация v1: управление работой

Эта конфигурация собирает рабочий интерфейс `Work Item` штатными средствами Frappe v16 внутри App `veqta_work_management`.

Модель данных описана в [Модели данных v1](data-model-v1.md), права — в [Безопасности v1](security-v1.md).

## Русский интерфейс

Технические идентификаторы остаются стабильными:

```text
App / Module: VEQTA Work Management
DocType: Work Item
Role: VEQTA Work User
status: Open, Waiting, Closed, Cancelled
priority: Low, Medium, High
```

Для нового App используется Gettext:

```text
veqta_work_management/locale/main.pot
veqta_work_management/locale/ru.po
```

Уникальные строки App переводятся в `ru.po`. Общие строки Frappe не дублируются, если core Russian translation уже подходит.

`Work Item.due_date` по смыслу является общим сроком Work Item. Это отличается от `Complete By` конкретного назначения, но не требует отдельного переопределения общей строки Frappe `Due Date`.

## Основной сценарий

```text
Work Item создан
→ Open
→ пользователь принимает ответственность через Assign to me
→ при внешней блокировке переводит Work Item в Waiting
→ после продолжения возвращает в Open
→ при завершении переводит Work Item в Closed
```

`Assign to me` создаёт персональное назначение, но baseline не хранит отдельный факт начала выполнения и не выводит состояние `In Progress` из самого наличия ToDo.

Состояние Work Item и состояние назначения `ToDo` остаются независимыми. Baseline не добавляет автоматическую синхронизацию между ними.

## List View

List View — основной экран очереди.

Показываются штатными средствами Frappe:

- `subject`;
- `status`;
- `priority`;
- `due_date`;
- назначенные пользователи, если стандартный List View текущего patch-release их показывает.

Сортировка:

```text
creation DESC
```

Базовые фильтры создаются обычным Filter UI:

```text
status in Open, Waiting
status = Open
status = Waiting
Assigned To → Me
```

`Assigned To` использует штатную assignment-механику Frappe. Внутренний `_assign` не становится полем предметной модели или App API.

Global Saved Filters не являются обязательным состоянием App. Пользователь при необходимости сохраняет собственный фильтр.

Собственный `work_item_list.js` в baseline не добавляется. Сначала проверяется стандартный List View на живом Site; визуальный extension появляется только при подтверждённом UX-пробеле.

## Kanban

Обязательная доска:

```text
Kanban Board Name: VEQTA Work Items
Reference DocType: Work Item
Field: status
Private: No
```

В русском интерфейсе: `Работы`.

Колонки:

```text
Open
Waiting
Closed
Cancelled
```

Через штатный Kanban Settings на карточке показываются:

```text
priority
due_date
```

Назначенные пользователи, теги и служебные элементы Kanban использует штатно.

Перетаскивание карточки меняет только `Work Item.status`. Связанные `ToDo` App не синхронизирует.

`Kanban Board` является обязательной DB-конфигурацией, поэтому для его поставки используется узкий fixture. Patch или собственный setup-код для создания одной обязательной доски не нужны.

## Calendar и Gantt

Calendar/Gantt не входят в baseline.

Текущая модель имеет одну дату `due_date`, а стандартные Calendar/Gantt Frappe работают с интервалом. Ради представления не создаются фиктивные:

```text
start_date
end_date
progress
```

Если появится реальная ответственность планового интервала, представления проектируются из неё.

## Срок Work Item и Complete By

```text
Work Item.due_date = общий срок работы
ToDo.date          = Complete By конкретного назначения
```

Стандартный Assign To не копирует `Work Item.due_date` в `ToDo.date`. Если пользователь оставляет `Complete By` пустым, standard dialog не отправляет null-поле `date`, и backend Frappe создаёт ToDo с текущей датой.

Если появится требование автоматически передавать срок Work Item в назначения, сначала проверяется штатный `Assignment Rule.due_date_based_on`, включая его стандартное обновление сроков открытых ToDo, созданных этим Assignment Rule. Собственная lifecycle-синхронизация не является первым вариантом.

## Auto Repeat

`Work Item` использует штатный Auto Repeat.

При повторении ожидается поведение metadata модели:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → default Open
due_date     → пусто
links        → пусто
```

Нативный механизм выбирается по конкретной ответственности:

- обычное повторение — `Auto Repeat`;
- фиксированный исполнитель нового экземпляра — `Auto Repeat.assignee`;
- автоматический выбор исполнителя — `Assignment Rule`;
- относительный `Work Item.due_date` или другая логика нового документа — `Work Item.on_recurring`.

Отдельный scheduler для этих сценариев не создаётся.

## Assignment Rule

`Assignment Rule` не входит в baseline как обязательная конфигурация.

Базовый сценарий — общая очередь + ручное `Assign to me`. Assignment Rule нужен только при реальном автоматическом распределении или при требовании штатно связывать срок назначения с полем исходного документа.

При появлении автоматического распределения сначала рассматриваются нативные стратегии Frappe:

```text
Round Robin
Load Balancing
Based on Field
Weighted Distribution
```

Собственная логика распределения не добавляется до появления требования, которое эти стратегии не выражают.

## Notifications

Собственных обязательных Notification rules нет. `Assign To` уже использует штатные notification mechanisms Frappe.

`Communication` может быть связан с Work Item и отображаться в Timeline, но baseline не выдаёт `VEQTA Work User` permission `Email` и не заявляет отдельный почтовый workflow.

## Number Cards

Baseline содержит четыре standard Number Cards типа `Document Type`, `Function = Count`:

| Техническое имя | Русское отображение | Filters |
| --- | --- | --- |
| `VEQTA Active Work Items` | Активные работы | `status in Open, Waiting` |
| `VEQTA Waiting Work Items` | Ожидание | `status = Waiting` |
| `VEQTA High Priority Work Items` | Высокий приоритет | `status in Open, Waiting`, `priority = High` |
| `VEQTA Due Today Work Items` | Срок сегодня | `status in Open, Waiting`, `due_date Timespan Today` |

Для каждой:

```text
Is Standard: Yes
Module: VEQTA Work Management
Is Public: Yes
Show Percentage Stats: No
```

В Developer Mode standard Number Card экспортируется Frappe в module files. Для загрузки этих файлов из downstream App требуется `importable_doctypes`, описанный ниже.

Карточка «Без исполнителя» не входит в baseline: фильтрация через внутренний assignment-механизм сначала проверяется на живом patch-release. Собственное поле `assignee` ради счётчика не добавляется.

Для визуального разделения можно использовать штатные `Color` / `Background Color` Number Card. Это оформление, а не модель данных.

## Dashboard Chart

Один standard chart:

```text
Chart Name: VEQTA New Work Items
Chart Type: Count
Document Type: Work Item
Time Series: Yes
Time Series Based On: creation
Timespan: Last Month
Time Interval: Daily
Type: Line
Is Public: Yes
Is Standard: Yes
Module: VEQTA Work Management
```

В русском интерфейсе: `Новые работы`. График показывает входящий поток Work Item и не трактуется как производительность.

В Developer Mode standard Dashboard Chart экспортируется Frappe в module files. Для загрузки этих файлов из downstream App также требуется `importable_doctypes`.

## Report Builder

Для полей самого Work Item используется штатный Report Builder, например Count по `status`, `priority` или `owner`.

`owner` — создатель Work Item, не исполнитель.

Широкий `Read` на все `ToDo` Site ради аналитики назначений не добавляется. Специальный отчёт по исполнителям создаётся только после отдельного требования и проверки authorization boundary.

## Workspace

Один standard public Workspace:

```text
Label: VEQTA Work Management
Title: VEQTA Work Management
Public: Yes
Module: VEQTA Work Management
Roles:
  VEQTA Work User
```

Shortcuts:

```text
New Work Item
  Type: DocType
  Link To: Work Item
  View: New

Work Item List
  Type: DocType
  Link To: Work Item
  View: List

Work Board
  Type: DocType
  Link To: Work Item
  View: Kanban
  Kanban Board: VEQTA Work Items
```

Компоновка:

```text
ДЕЙСТВИЯ
├── Новая работа
├── Список работ
└── Доска

ТЕКУЩЕЕ СОСТОЯНИЕ
├── Активные работы
├── Ожидание
├── Высокий приоритет
└── Срок сегодня

ПОСТУПЛЕНИЕ
└── Новые работы
```

Используются штатные Header blocks, shortcuts, Number Cards и Chart. Custom HTML/CSS ради декоративного оформления не добавляется.

Отдельный `Workspace Sidebar` не является обязательным состоянием baseline: Frappe v16 умеет строить навигацию модуля из его standard metadata. Собственный standard Sidebar нужен только если появится самостоятельное требование управлять структурой навигации, которую автоматическая module navigation не выражает.

## Поставка обязательного состояния

Порядок:

1. standard file-backed metadata Frappe;
2. официальный sync hook для standard DocTypes, которые downstream App не сканирует по умолчанию;
3. fixture только для обязательной DB-записи без standard file-backed механизма;
4. patch только для миграции существующего состояния;
5. ручная настройка — только этап эксперимента.

### `hooks.py`

Для Number Card и Dashboard Chart нужен официальный hook:

```python
importable_doctypes = [
    "Number Card",
    "Dashboard Chart",
]

fixtures = [
    {
        "doctype": "Kanban Board",
        "filters": [["name", "=", "VEQTA Work Items"]],
    }
]
```

Почему именно так:

- `Number Card` и `Dashboard Chart` имеют собственный standard file export и должны оставаться standard metadata;
- `frappe.model.sync.get_doc_files()` сканирует downstream App только по встроенному `IMPORTABLE_DOCTYPES` плюс hook `importable_doctypes`;
- `Number Card` и `Dashboard Chart` не входят во встроенный список Frappe v16.33.0;
- fixture для них дублировал бы уже существующую standard file semantics;
- `Kanban Board`, напротив, не имеет такого standard file-backed механизма, поэтому узкий fixture остаётся правильным выбором.

Baseline:

```text
standard metadata / App files:
- Work Item
- Workspace
- Number Cards
- Dashboard Chart
- locale/main.pot
- locale/ru.po

hooks.py:
- importable_doctypes: Number Card, Dashboard Chart
- fixture declaration: только Kanban Board VEQTA Work Items

не поставляется:
- fixture для Number Card / Dashboard Chart
- отдельный fixture Role только ради VEQTA Work User
- global Saved Filters
- пользовательские Work Item / ToDo
- custom List JS
- lifecycle hooks для ToDo
- Workspace Sidebar без отдельного навигационного требования
```

Role, указанные в permission rows standard DocType, создаются штатной импортной механикой Frappe; это проверяется reinstall-test вместе с DocPerm.

Фактическая поставка проверяется reinstall-test на втором чистом Site.

## Источники Frappe v16.33.0

- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Gettext commands`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)
- [`Assign To`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Assign To dialog`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [`FieldGroup.get_values`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/ui/field_group.js)
- [`Assignment Rule`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/assignment_rule/assignment_rule.py)
- [`Auto Repeat`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Kanban View`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/kanban/kanban_view.js)
- [`Kanban Board`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/kanban_board/kanban_board.py)
- [`Kanban Settings`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/kanban/kanban_settings.js)
- [`Number Card`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/number_card/number_card.py)
- [`Dashboard Chart`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [`Workspace`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [`Workspace Sidebar`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace_sidebar/workspace_sidebar.py)
- [`DocType import`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Model sync`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/sync.py)
- [`Fixtures`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py)
