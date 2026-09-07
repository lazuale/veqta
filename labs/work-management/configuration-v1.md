# Конфигурация v1: управление работой

Эта конфигурация собирает рабочий интерфейс `Work Item` штатными средствами Frappe v16 внутри минимального App `work_management`.

Developer Mode используется для разработки и экспорта standard metadata в App. Это не означает, что прототип должен содержать собственный frontend, API, scheduler или прикладной Python-код: сначала используются готовые механизмы Frappe, затем официальные extension points и только потом минимальный собственный код для подтверждённого пробела.

Модель данных описана в [Модели данных v1](data-model-v1.md), права доступа — в [Безопасности v1](security-v1.md).

## Русский интерфейс

Пользовательская часть управления работой настраивается на русском языке. Технические идентификаторы и хранимые значения остаются стабильными:

```text
DocType: Work Item
fieldnames: subject, description, status, priority, due_date, links
status values: Open, Waiting, Closed, Cancelled
priority values: Low, Medium, High
```

Русскими задаются метки полей, названия Saved Filters, Kanban Board, Calendar View, Number Cards, Dashboard Charts, Workspace и shortcuts.

`Work Item` отображается как `Работа` через штатный механизм переводов Frappe. Технические значения `status` и `priority` не заменяются русскими строками.

```text
Open      → Открыто
Waiting   → Ожидание
Closed    → Закрыто
Cancelled → Отменено

Low       → Низкий
Medium    → Средний
High      → Высокий
```

Если конкретная строка не переведена текущим русским словарём Site, добавляется перевод, а не новое значение модели.

## Основной сценарий

```text
Work Item создан
→ виден Work User
→ пользователь берёт его через Assign to me
→ при внешней блокировке переводит в Waiting
→ после выполнения закрывает своё назначение
→ переводит Work Item в Closed
```

`Work Item.status` описывает состояние самой работы, а `Assign To / ToDo` — персональную ответственность.

## List View

List View — основной экран очереди.

Используются:

- `subject` — `Название`;
- `status` — `Статус`;
- `priority` — `Приоритет`;
- `due_date` — `Срок`;
- системное `Assigned To` (`_assign`).

Сортировка:

```text
creation DESC
```

### Общие фильтры

```text
Активные
status in Open, Waiting

Открытые
status = Open

Ожидание
status = Waiting

Без исполнителя
status = Open
Assigned To is not set
```

Для личной очереди отдельное поле `assignee` не требуется: используется стандартный фильтр `Assigned To → Me`.

## Kanban

```text
Kanban Board: Работы
Reference DocType: Work Item
Field: status
Private: No
```

Технические колонки:

```text
Open
Waiting
Closed
Cancelled
```

Kanban показывает состояние работы. Исполнитель остаётся отдельным фактом `Assign To`, поэтому отдельной колонки «В работе» нет.

Перетаскивание карточки меняет `Work Item.status` штатным сохранением документа. Оно не синхронизирует связанные `ToDo`.

## Calendar

```text
Name: Работы по сроку
Reference Document Type: Work Item
Subject Field: subject
Start Date Field: due_date
End Date Field: due_date
All Day: Yes
```

`due_date` используется как точка срока, а не интервал выполнения. Поля `start_date`, `end_date`, `duration`, `progress` только ради Calendar/Gantt не добавляются.

## Auto Repeat

`Work Item` разрешает штатный Auto Repeat.

Базовая конфигурация повторения не назначает исполнителя автоматически. Новый экземпляр попадает в общую очередь.

При копировании:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → не копируется, default Open
due_date     → не копируется
links        → не копируются
```

Чистая конфигурация Auto Repeat не рассчитывает относительный `due_date`. Это ограничение конфигурации, а не всего Frappe: v16 после подготовки нового документа вызывает controller method `on_recurring`.

Поэтому если появится правило вроде «создать 1-го числа со сроком 5-го», сначала рассматривается `Work Item.on_recurring(...)`. Собственный scheduler для этого не нужен.

Пока такого требования нет, controller остаётся без прикладной логики.

## Notifications

Обязательных собственных Notification rules нет.

`Assign To` уже создаёт штатное уведомление о назначении. При необходимости можно добавить email-напоминание по `Work Item.due_date`; это конфигурация, а не новое поле модели.

## Number Cards

Workspace использует пять Number Cards типа `Document Type` с функцией `Count`:

| Card | Filters |
| --- | --- |
| Активные работы | `status in Open, Waiting` |
| Ожидание | `status = Waiting` |
| Без исполнителя | `status = Open`, `Assigned To is not set` |
| Высокий приоритет | `status in Open, Waiting`, `priority = High` |
| Срок сегодня | `status in Open, Waiting`, `due_date Timespan today` |

Для карточек:

```text
Document Type: Work Item
Function: Count
Is Public: Yes
Show Percentage Stats: No
Dynamic Filters: —
```

Percentage Stats выключены: они не восстанавливают историческое состояние очереди.

### Оформление

Используются штатные `Color` и `Background Color`:

| Card | Color | Background Color |
| --- | --- | --- |
| Активные работы | `#1D4ED8` | `#EFF6FF` |
| Ожидание | `#B45309` | `#FFF7ED` |
| Без исполнителя | `#475569` | `#F1F5F9` |
| Высокий приоритет | `#B91C1C` | `#FEF2F2` |
| Срок сегодня | `#A16207` | `#FEFCE8` |

Developer Mode оставляет доступными standard/module-настройки карточек, если они нужны для воспроизводимой доставки App.

## Dashboard Charts

Базовая конфигурация использует один временной график:

```text
Chart Name: Новые работы
Chart Type: Count
Document Type: Work Item
Time Series: Yes
Time Series Based On: creation
Timespan: Last Month
Time Interval: Daily
Type: Line
Is Public: Yes
```

График показывает поступление новых Work Item и не является показателем производительности.

Простой `Group By` по `status`/`priority` пока не используется, если он показывает technical Select values без перевода.

Это не считается общей границей Frappe: Developer Mode открывает standard `Dashboard Chart` и `Dashboard Chart Source`. Собственный источник графика добавляется только при реальной необходимости, а не ради демонстрации возможностей.

## Report Builder и расширенная отчётность

Report Builder остаётся первым выбором для простого анализа одного DocType.

Примеры:

- `Count` по `status`;
- `Count` по `priority`;
- `Count` по `owner`.

`owner` означает создателя Work Item, а не исполнителя.

Текущая предметная модель не хранит структурированные факты `closed_at`, `closed_by`, длительность `Waiting` или фактическое время выполнения, поэтому такие показатели нельзя честно выводить из `modified`.

Отдельно нужно различать невозможность конкретного Report Builder-запроса и отсутствие возможностей Framework. Если появится обязательная безопасная аналитика по назначениям, App оставляет штатный путь через standard Query/Script Report с явной семантикой и проверкой прав. Выдавать руководителю широкий `Read` на все `ToDo` Site ради отчётности по-прежнему нельзя.

## Workspace

Создаётся один общий public Workspace:

```text
Label: Управление работой
Title: Управление работой
Type: Workspace
Public: Yes
Module: Work Management
Roles:
  Work User
```

Developer Mode важен здесь не для runtime, а для разработки: public Workspace с module может быть экспортирован в App как standard metadata.

Используйте штатные `icon` и `indicator_color` Workspace. Не ограничивайте дизайн только теми полями, которые видны обычному администратору production Site.

### Shortcuts

```text
Новая работа
  Type: DocType
  Link To: Work Item
  View: New

Список работ
  Type: DocType
  Link To: Work Item
  View: List

Доска
  Type: DocType
  Link To: Work Item
  View: Kanban
  Kanban Board: Работы

Календарь
  Type: URL
  URL: route именованного Calendar View Работы по сроку
```

`Workspace Shortcut.color` не рассматривается как способ перекрасить всю плитку: в штатном v16 он главным образом участвует в indicator/count-представлении. Основная визуальная структура достигается компоновкой Workspace и оформлением Number Cards.

### Состав экрана

```text
УПРАВЛЕНИЕ РАБОТОЙ
│
├── ДЕЙСТВИЯ
│   ├── Новая работа
│   ├── Список работ
│   ├── Доска
│   └── Календарь
│
├── ТЕКУЩЕЕ СОСТОЯНИЕ
│   ├── Активные работы
│   ├── Ожидание
│   ├── Без исполнителя
│   ├── Высокий приоритет
│   └── Срок сегодня
│
└── ПОСТУПЛЕНИЕ
    └── Новые работы
```

Workspace делится штатными Header blocks. Custom HTML, собственный CSS и frontend только ради декоративного оформления не добавляются.

## Поставка обязательного состояния

Обязательное состояние Lab должно быть воспроизводимым.

Приоритет поставки:

1. standard metadata, которое Frappe экспортирует в module App;
2. штатные fixtures для обязательных database records, если конкретный тип документа не является file-backed standard metadata;
3. patch только если требуется миграция уже существующего состояния;
4. ручная настройка — только временный шаг live experiment, а не конечный способ доставки.

Точный набор exported metadata и fixtures фиксируется после живой сборки на используемой версии Frappe. Не нужно заранее придумывать механизм для каждого объекта без проверки фактического поведения Framework.

## Границы текущей конфигурации

На текущем этапе остаются следующие наблюдаемые границы:

- `Work Item.status` и `ToDo.status` не синхронизируются автоматически;
- `Work Item.due_date` и `ToDo.date` имеют разную семантику;
- чистый DocPerm не выражает правило «редактировать Work Item может только назначенный пользователь»;
- простой Report Builder не закрывает безопасную общую аналитику по всем назначениям;
- базовый Auto Repeat не вычисляет относительный `due_date`;
- простой `Dashboard Chart Group By` может быть недостаточен для локализованного категориального графика.

Эти пункты не объявляются фундаментальными ограничениями Frappe. При подтверждённой необходимости сначала проверяется официальный developer extension point.

## Источники Frappe v16

- [Frappe Apps](https://docs.frappe.io/framework/user/en/guides/basics/apps)
- [Developer Mode](https://docs.frappe.io/framework/user/en/guides/app-development/how-enable-developer-mode-in-frappe)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Workspace](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [Workspace form](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.js)
- [Workspace Shortcut](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json)
- [Workspace Shortcut widget](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/widgets/shortcut_widget.js)
- [Number Card](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/number_card/number_card.json)
- [Number Card widget](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/widgets/number_card_widget.js)
- [Dashboard Chart](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [Dashboard Chart Source](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart_source/dashboard_chart_source.py)
- [Report](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/report/report.py)
- [Assign To](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [Auto Repeat](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
