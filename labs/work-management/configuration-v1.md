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

## Основной сценарий

```text
Work Item создан
→ Open
→ пользователь берёт его через Assign to me
→ при внешней блокировке переводит Work Item в Waiting
→ после продолжения возвращает в Open
→ при завершении переводит Work Item в Closed
```

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

`Kanban Board` является обязательной DB-конфигурацией, поэтому для его поставки используется fixture.

## Calendar и Gantt

Calendar/Gantt не входят в baseline.

Текущая модель имеет одну дату `due_date`, а стандартные Calendar/Gantt Frappe работают с интервалом. Ради представления не создаются фиктивные:

```text
start_date
end_date
progress
```

Если появится реальная ответственность планового интервала, представления проектируются из неё.

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

Относительный `due_date` без отдельного правила не вычисляется. Если такое правило появится, первым проверяется `Work Item.on_recurring`.

## Assignment Rule

`Assignment Rule` не входит в baseline.

Базовый сценарий — общая очередь + ручное `Assign to me`. Assignment Rule нужен только при реальном автоматическом распределении.

## Notifications

Собственных обязательных Notification rules нет. `Assign To` уже использует штатные уведомления Frappe.

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

## Поставка обязательного состояния

Порядок:

1. standard file-backed metadata Frappe;
2. fixture только для обязательной DB-записи без standard file-backed механизма;
3. patch только для миграции существующего состояния;
4. ручная настройка — только этап эксперимента.

Baseline:

```text
standard metadata / App files:
- Work Item
- Workspace
- Number Cards
- Dashboard Chart
- locale/main.pot
- locale/ru.po
- hooks.py с fixture declaration

fixture:
- Kanban Board VEQTA Work Items

не поставляется:
- global Saved Filters
- пользовательские Work Item / ToDo
- custom List JS
- lifecycle hooks для ToDo
```

Фактическая поставка проверяется reinstall-test на втором чистом Site.

## Источники Frappe v16.33.0

- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Gettext commands`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)
- [`Kanban View`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/kanban/kanban_view.js)
- [`Kanban Settings`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/kanban/kanban_settings.js)
- [`Number Card`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/number_card/number_card.py)
- [`Dashboard Chart`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [`Workspace`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [`Fixtures`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py)
