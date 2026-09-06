# Work Management: Configuration v1

Эта конфигурация собирает рабочий интерфейс `Work Item` штатными средствами Frappe v16. Она не добавляет собственный код, scripts, hooks, API или frontend.

Модель данных описана в [Data Model v1](data-model-v1.md), права доступа — в [Security v1](security-v1.md).

## Основной сценарий

Базовая работа строится вокруг общей очереди:

```text
Work Item создан
→ виден Work User
→ пользователь берёт его через Assign to me
→ при внешней блокировке переводит в Waiting
→ после выполнения закрывает assignment и Work Item
```

`Work Item.status` описывает состояние самой работы, а `Assign To / ToDo` — персональную ответственность.

## List View

List View — основной экран очереди.

В рабочем списке используются:

- `subject` как Title Field;
- `status`;
- `priority`;
- `due_date`;
- системное поле `Assigned To` (`_assign`).

Сортировка по умолчанию:

```text
creation DESC
```

### Общие фильтры

Для команды полезны глобальные Saved Filters:

```text
Active
status in Open, Waiting

Open
status = Open

Waiting
status = Waiting

Unassigned
status = Open
Assigned To is not set
```

Для неназначенной работы используется явный фильтр `Assigned To is not set`.

### Мои назначения

Отдельное поле `assignee` не требуется. В стандартном фильтре `Assigned To` пользователь выбирает `Me`; Frappe фильтрует документы по текущему пользователю через системное `_assign`.

## Kanban

Создаётся одна общая доска:

```text
Kanban Board: Work Items
Reference DocType: Work Item
Field: status
Private: No
```

Колонки:

```text
Open
Waiting
Closed
Cancelled
```

Kanban показывает состояние работы. Исполнитель остаётся отдельным фактом Assign To, поэтому отдельной колонки `In Progress` нет.

Перетаскивание карточки меняет `Work Item.status` штатным сохранением документа. Оно не синхронизирует связанные `ToDo`; закрытие assignments и закрытие Work Item остаются отдельными действиями.

## Calendar

Для сроков создаётся Calendar View:

```text
Name: Work Items by Due Date
Reference Document Type: Work Item
Subject Field: subject
Start Date Field: due_date
End Date Field: due_date
All Day: Yes
```

Один `due_date` используется как точка срока, а не как интервал выполнения. Работы без `due_date` не отображаются как календарные события.

Дополнительные `start_date`, `end_date`, `duration` и `progress` только ради Calendar или Gantt не добавляются.

## Auto Repeat

`Work Item` разрешает штатный Auto Repeat.

Типовая конфигурация повторения:

```text
Reference Document Type: Work Item
Reference Document: нужный Work Item
Submit on Creation: No
Generate Separate Documents For Each Assignee: No
Assignee: —
Notify by Email: No
```

Доступные штатные частоты Frappe:

```text
Daily
Weekly
Fortnightly
Monthly
Quarterly
Half-yearly
Yearly
```

При создании очередного Work Item:

- `subject` копируется;
- `description` копируется;
- `priority` копируется;
- `status` не копируется и получает обычный default `Open`;
- `due_date` не копируется;
- `links` не копируются.

Автоматическое назначение исполнителя не является частью baseline. Повтор создаёт новую работу в общей очереди, после чего пользователь берёт её через `Assign to me`.

`Work User` не получает отдельные права на DocType `Auto Repeat`. Настройка повторений остаётся административной конфигурацией Site, чтобы не открывать пользователю правила повторения других DocType.

Штатный Auto Repeat не вычисляет для этой модели относительный `due_date` нового Work Item. Если повторяющейся работе понадобится правило вроде «создать 1-го числа со сроком 5-го», это отдельное требование.

## Notifications

Обязательных собственных Notification rules в baseline нет.

`Assign To` уже создаёт штатное уведомление о назначении, поэтому отдельная Notification на новое назначение не нужна.

При необходимости можно добавить email-напоминание по сроку Work Item:

```text
Document Type: Work Item
Event: Days Before
Reference Date: due_date
Days Before: 1
Channel: Email
Filters: status in Open, Waiting
Send To All Assignees: Yes
```

Это опциональная Site-конфигурация, а не обязательная часть модели.

System Notification по `due_date` только текущим assignees в baseline не настраивается: Work Item намеренно не хранит собственное поле исполнителя, а рассылка по роли отправила бы уведомление всей группе.

`ToDo.date` не используется как замена `Work Item.due_date`: это `Complete By` конкретного assignment, а не срок самой работы.

## Number Cards

Workspace использует пять Number Cards типа `Document Type` с функцией `Count`:

| Card | Filters |
| --- | --- |
| Active Work | `status in Open, Waiting` |
| Waiting | `status = Waiting` |
| Unassigned | `status = Open`, `Assigned To is not set` |
| High Priority | `status in Open, Waiting`, `priority = High` |
| Due Today | `status in Open, Waiting`, `due_date = today` |

Для карточек:

```text
Document Type: Work Item
Function: Count
Is Public: Yes
Show Percentage Stats: No
Dynamic Filters: —
```

Percentage Stats выключены: для текущих состояний `Open` и `Waiting` они не восстанавливают историческое состояние очереди и поэтому не должны интерпретироваться как изменение backlog во времени.

Number Card кликабельна и открывает отфильтрованный список Work Item, поэтому отдельные shortcuts `Open`, `Waiting` и `Unassigned` не нужны.

## Dashboard Charts

### Active Work by Status

```text
Chart Type: Group By
Document Type: Work Item
Group By Based On: status
Group By Type: Count
Filters: status in Open, Waiting
Type: Donut
Is Public: Yes
```

### Active Work by Priority

```text
Chart Type: Group By
Document Type: Work Item
Group By Based On: priority
Group By Type: Count
Filters: status in Open, Waiting
Type: Bar
Is Public: Yes
```

### New Work Items

```text
Chart Type: Count
Document Type: Work Item
Time Series: Yes
Time Series Based On: creation
Timespan: Last Month
Time Interval: Daily
Type: Line
Is Public: Yes
```

Этот график показывает только поступление новых Work Item. Он не является показателем производительности или объёма выполненной работы.

Dynamic Filters с JavaScript expressions в baseline не используются.

## Report Builder

Отдельный обязательный Report Builder report не создаётся. Стандартный Report View используется для разового анализа Work Item, например:

- count по `status`;
- count по `priority`;
- count по `owner`.

`owner` означает создателя Work Item, а не исполнителя.

Текущая модель не позволяет корректно считать через обычный Report Builder:

- кто закрыл Work Item;
- сколько Work Item пользователь завершил за период;
- фактическое время выполнения;
- процент выполнения в срок;
- длительность состояния Waiting.

Для этих показателей в модели нет структурированных фактов завершения и периодов состояния. `modified` не используется как подмена даты закрытия.

## Workspace

Создаётся один общий Workspace:

```text
Name: Work Management
Type: Workspace
Public: Yes
Roles:
  Work User
```

`Public` означает общий Workspace внутри Desk. Роль `Work User` ограничивает его видимость участниками Work Management.

Редактирование общего Workspace остаётся задачей штатного `Workspace Manager`; прикладной роли `Work User` административные права Workspace не выдаются.

### Shortcuts

```text
New Work Item
  Type: DocType
  Link To: Work Item
  View: New

Work List
  Type: DocType
  Link To: Work Item
  View: List

Board
  Type: DocType
  Link To: Work Item
  View: Kanban
  Kanban Board: Work Items

Calendar
  Type: DocType
  Link To: Work Item
  View: Calendar
```

### Состав экрана

```text
WORK MANAGEMENT
│
├── ACTIONS
│   ├── New Work Item
│   ├── Work List
│   ├── Board
│   └── Calendar
│
├── CURRENT STATE
│   ├── Active Work
│   ├── Waiting
│   ├── Unassigned
│   ├── High Priority
│   └── Due Today
│
├── QUEUE STRUCTURE
│   ├── Active Work by Status
│   └── Active Work by Priority
│
└── INTAKE
    └── New Work Items
```

Quick List в baseline не используется: стандартный Quick List показывает только несколько последних документов по `creation desc`, что не является приоритетной рабочей очередью.

Custom HTML Blocks, отдельный Dashboard, Onboarding и служебные shortcuts для `ToDo`, `Auto Repeat` или `Notification` также не требуются.

## Границы конфигурации

Чистая native-first конфигурация сохраняет несколько известных ограничений:

- `Work Item.status` и `ToDo.status` не синхронизируются автоматически;
- Work User с `Write` на общей очереди может редактировать Work Item и снимать assignment другого Work User;
- `Work Item.due_date` и `ToDo.date` независимы;
- автоматический Auto Repeat не вычисляет относительный срок Work Item;
- безопасная командная аналитика по всем Work Item assignments не получается только через стандартные права на `ToDo`, не открыв другие ToDo Site;
- история `closed_at / closed_by` не хранится отдельными полями.

Эти ограничения сами по себе не являются основанием для собственной разработки. Доработка появляется только после подтверждённой пользовательской необходимости.

## Источники Frappe v16

- [Workspace](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace/workspace.py)
- [Workspace Shortcut](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json)
- [Workspace Quick List](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/widgets/quick_list_widget.js)
- [Number Card](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/number_card/number_card.py)
- [Dashboard Chart](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [Assign To](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py)
- [Auto Repeat](https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [Notification](https://github.com/frappe/frappe/blob/version-16/frappe/email/doctype/notification/notification.py)
