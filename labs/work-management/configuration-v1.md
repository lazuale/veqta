# Конфигурация v1: управление работой

Эта конфигурация собирает рабочий интерфейс `Work Item` штатными средствами Frappe v16 внутри App `veqta_work_management`.

Модель данных описана в [Модели данных v1](data-model-v1.md), права доступа — в [Безопасности v1](security-v1.md).

## Русский интерфейс

Технические идентификаторы App остаются стабильными:

```text
App / Module: VEQTA Work Management
DocType: Work Item
Role: VEQTA Work User
status: Open, Waiting, Closed, Cancelled
priority: Low, Medium, High
```

Для нового App на Frappe v16 русская локализация поставляется через Gettext:

```text
veqta_work_management/locale/main.pot
veqta_work_management/locale/ru.po
```

Уникальные строки App переводятся в `ru.po`, например:

```text
Work Item                      → Работа
VEQTA Work Management          → Управление работой
VEQTA Work User                → Участник управления работой
VEQTA Work Items               → Работы
VEQTA Active Work Items        → Активные работы
VEQTA Waiting Work Items       → Ожидание
VEQTA High Priority Work Items → Высокий приоритет
VEQTA Due Today Work Items     → Срок сегодня
VEQTA New Work Items           → Новые работы
```

Общие строки Frappe (`Open`, `Status`, `Priority` и т. п.) не переопределяются App без необходимости, если core Russian translation уже подходит.

## Основной сценарий

```text
Work Item создан
→ Open
→ пользователь берёт его через Assign to me
→ при внешней блокировке переводит в Waiting
→ после завершения всей работы переводит Work Item в Closed
→ App закрывает оставшиеся активные назначения
```

При `Cancelled` App отменяет только активные назначения. Закрытие одного `ToDo` не закрывает Work Item автоматически.

## List View

List View — основной экран очереди.

Показываются:

- `subject`;
- `status`;
- `priority`;
- `due_date`;
- штатное отображение назначенных пользователей Frappe.

Сортировка:

```text
creation DESC
```

### Индикатор состояния

Для standard DocType используется штатная точка расширения `<doctype>_list.js`:

```javascript
frappe.listview_settings["Work Item"] = {
	get_indicator(doc) {
		const colors = {
			Open: "blue",
			Waiting: "orange",
			Closed: "green",
			Cancelled: "gray",
		};

		return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
	},
};
```

Это standard List View extension Frappe, а не собственный frontend.

### Фильтры

Базовые фильтры строятся обычным Filter UI:

```text
Активные: status in Open, Waiting
Открытые: status = Open
Ожидание: status = Waiting
Мои работы: Assigned To → Me
```

Они не поставляются App как глобальные `List Filter` fixtures. Saved Filter является пользовательской настройкой Site, если конкретный пользователь хочет сохранить такой выбор.

Внутреннее `_assign` не используется как собственное поле модели. Фильтры или показатели, завязанные на него, не становятся обязательным App-контрактом без проверки на конкретном patch-release.

## Kanban

Обязательная доска:

```text
Kanban Board Name: VEQTA Work Items
Reference DocType: Work Item
Field: status
Private: No
```

В русском интерфейсе имя отображается как `Работы`.

Колонки используют технические значения:

```text
Open
Waiting
Closed
Cancelled
```

Renderer Frappe переводит их через `__()`, поэтому русские значения данных не нужны.

Через штатный Kanban Settings на карточке дополнительно показываются:

```text
priority
due_date
```

Назначенные пользователи, теги и служебные элементы Kanban получает штатно.

Перетаскивание карточки меняет `Work Item.status` обычным сохранением документа. Поэтому переход в `Closed` или `Cancelled` проходит тот же серверный lifecycle Work Item и не требует отдельного Kanban-кода.

`Kanban Board` не является file-backed standard metadata, поэтому именно для этой обязательной DB-записи используется fixture.

## Calendar и Gantt

Calendar/Gantt не входят в baseline.

Причина не в отсутствии UI во Frappe, а в семантике данных: текущая модель имеет одну дату `due_date`, а Calendar/Gantt работают с интервалом. Не создаются:

```text
start_date
end_date
progress
фиктивный end = due_date
```

Когда появится реальная ответственность планового интервала, представления проектируются заново.

## Auto Repeat

`Work Item` разрешает штатный Auto Repeat.

При повторении:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → default Open
due_date     → пусто
links        → пусто
назначения   → отсутствуют, если их явно не задаёт Auto Repeat
```

Относительный `due_date` не вычисляется без реального правила. Если такое правило появится, первым используется `Work Item.on_recurring`; собственный scheduler не нужен.

## Assignment Rule

`Assignment Rule` не входит в baseline.

Базовая модель — общая очередь + ручное `Assign to me`. Assignment Rule добавляется только когда появляется самостоятельное правило автоматического распределения: round-robin, load balancing, based on field или weighted distribution.

Не используется Assignment Rule только ради синхронизации сроков или terminal status: это не его ответственность.

## Notifications

Собственных обязательных Notification rules нет. `Assign To` уже создаёт стандартное уведомление о назначении.

Email-напоминание по `Work Item.due_date` может появиться как отдельная конфигурация, если оно реально потребуется пользователю.

## Number Cards

Baseline содержит четыре Number Cards типа `Document Type`, `Function = Count`:

| Техническое имя | Русское отображение | Filters |
| --- | --- | --- |
| `VEQTA Active Work Items` | Активные работы | `status in Open, Waiting` |
| `VEQTA Waiting Work Items` | Ожидание | `status = Waiting` |
| `VEQTA High Priority Work Items` | Высокий приоритет | `status in Open, Waiting`, `priority = High` |
| `VEQTA Due Today Work Items` | Срок сегодня | `status in Open, Waiting`, `due_date Timespan Today` |

Для каждой карточки:

```text
Is Standard: Yes
Module: VEQTA Work Management
Is Public: Yes
Show Percentage Stats: No
```

Percentage Stats выключены: они сравнивают выборки по времени, но не восстанавливают историческое состояние очереди.

### Почему нет обязательной карточки «Без исполнителя»

Назначения Frappe отображаются через системное `_assign`/`ToDo`. В exact v16.33.0 это поведение нельзя считать одинаковым для всех путей List/Number Card без live-проверки. Поэтому «Без исполнителя» сначала проверяется на живом Site и только после подтверждения может стать standard card.

Не добавляется собственный `assignee` только ради счётчика.

### Оформление

Используются штатные `Color` и `Background Color` Number Card:

| Card | Color | Background Color |
| --- | --- | --- |
| Активные работы | `#1D4ED8` | `#EFF6FF` |
| Ожидание | `#B45309` | `#FFF7ED` |
| Высокий приоритет | `#B91C1C` | `#FEF2F2` |
| Срок сегодня | `#A16207` | `#FEFCE8` |

Цвет является только визуальной семантикой.

## Dashboard Chart

Baseline использует один standard chart:

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

В русском интерфейсе: `Новые работы`.

График показывает входящий поток Work Item и не трактуется как производительность.

## Report Builder и аналитика назначений

Report Builder остаётся первым выбором для анализа полей самого Work Item:

- Count по `status`;
- Count по `priority`;
- Count по `owner`.

`owner` — создатель Work Item, а не исполнитель.

Для общей аналитики по исполнителям нельзя выдавать широкий `Read` на все `ToDo` Site.

Кроме того, специальная агрегация List View `assigned_to` в Frappe v16.33.0 сопоставляет разрешённые имена документов с `ToDo.reference_name`, не добавляя в этот запрос ограничение `reference_type = Work Item`. Поэтому она не используется как строгий источник управленческой аналитики Lab.

Если такая аналитика станет обязательной, первый App-level вариант — отдельный permission-aware Script Report, который явно ограничивает:

```text
ToDo.reference_type = Work Item
```

и проверяет прикладную авторизацию. Собственный отчёт не создаётся заранее.

## Workspace

Создаётся один общий standard public Workspace:

```text
Label: VEQTA Work Management
Title: VEQTA Work Management
Type: Workspace
Public: Yes
Module: VEQTA Work Management
Roles:
  VEQTA Work User
```

В русском интерфейсе он отображается как `Управление работой`.

### Shortcuts

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

Русские подписи: `Новая работа`, `Список работ`, `Доска`.

### Компоновка

```text
УПРАВЛЕНИЕ РАБОТОЙ
│
├── ДЕЙСТВИЯ
│   ├── Новая работа
│   ├── Список работ
│   └── Доска
│
├── ТЕКУЩЕЕ СОСТОЯНИЕ
│   ├── Активные работы
│   ├── Ожидание
│   ├── Высокий приоритет
│   └── Срок сегодня
│
└── ПОСТУПЛЕНИЕ
    └── Новые работы
```

Используются штатные Header blocks, Number Cards, Chart и shortcuts. Custom HTML/CSS не добавляется только ради декоративного оформления.

## Поставка обязательного состояния

Приоритет доставки:

1. standard file-backed metadata Frappe;
2. fixture только для обязательной DB-записи, которая не имеет standard file-backed механизма;
3. patch только для миграции уже существующего состояния;
4. ручная настройка — только этап live experiment.

В baseline:

```text
standard metadata / App files:
- Work Item
- Work Item controller
- Work Item list.js
- Workspace
- Number Cards
- Dashboard Chart
- locale/main.pot
- locale/ru.po
- hooks.py

fixture:
- Kanban Board VEQTA Work Items

не поставляется:
- пользовательские Saved Filters
- пользовательские данные Work Item/ToDo
```

Точный экспорт проверяется reinstall-test на втором чистом Site, а не предполагается по имени UI-объекта.

## Источники Frappe v16.33.0

- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Gettext commands`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)
- [`List View settings`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/activity_log/activity_log_list.js)
- [`Kanban View`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/kanban/kanban_view.js)
- [`Kanban Settings`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/kanban/kanban_settings.js)
- [`Number Card`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/number_card/number_card.py)
- [`Dashboard Chart`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [`Workspace`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [`Workspace Shortcut`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json)
- [`List group-by`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/listview.py)
- [`Fixtures`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py)