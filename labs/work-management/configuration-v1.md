# Конфигурация v1: управление работой

Эта конфигурация собирает рабочий интерфейс `Work Item` штатными средствами Frappe v16. Она не добавляет собственный код, scripts, hooks, API или frontend.

Модель данных описана в [Модели данных v1](data-model-v1.md), права доступа — в [Безопасности v1](security-v1.md).

## Русский интерфейс

Пользовательская часть управления работой настраивается на русском языке. Технические идентификаторы Frappe и нашей модели при этом остаются стабильными:

```text
DocType: Work Item
fieldnames: subject, description, status, priority, due_date, links
priority values: Low, Medium, High
```

Русскими задаются:

- метки полей `Work Item`;
- значения `status`;
- названия Saved Filters;
- Kanban Board и Calendar View;
- Number Cards и Dashboard Charts;
- Workspace и его shortcuts.

Для технического имени `Work Item` и значений приоритета используется штатный DocType `Translation`:

| Source Text | Context | Translated Text |
| --- | --- | --- |
| `Work Item` | — | `Работа` |
| `Low` | `Work Item` | `Низкий` |
| `Medium` | `Work Item` | `Средний` |
| `High` | `Work Item` | `Высокий` |

Контекст `Work Item` у приоритетов нужен, чтобы не менять отображение общих значений `Low / Medium / High` в других DocType. Frappe переводит подписи значений `Select` с контекстом DocType, сохраняя исходное значение поля.

Статусы устроены иначе: их фактические значения сразу русские:

```text
Открыто
Ожидание
Закрыто
Отменено
```

Это требуется для полностью русского штатного Kanban: Frappe использует фактическое значение поля `status` как имя колонки и не хранит для колонки отдельную локализованную подпись.

## Основной сценарий

Базовая работа строится вокруг общей очереди:

```text
Work Item создан
→ виден Work User
→ пользователь берёт его через Assign to me
→ при внешней блокировке переводит в Ожидание
→ после выполнения закрывает назначение и переводит Work Item в Закрыто
```

`Work Item.status` описывает состояние самой работы, а `Assign To / ToDo` — персональную ответственность.

## List View

List View — основной экран очереди.

В рабочем списке используются:

- `subject` с меткой `Название` как Title Field;
- `status` с меткой `Статус`;
- `priority` с меткой `Приоритет`;
- `due_date` с меткой `Срок`;
- системное поле `Assigned To` (`_assign`).

Сортировка по умолчанию:

```text
creation DESC
```

### Общие фильтры

Для команды создаются глобальные Saved Filters:

```text
Активные
status in Открыто, Ожидание

Открытые
status = Открыто

Ожидание
status = Ожидание

Без исполнителя
status = Открыто
Assigned To is not set
```

Для неназначенной работы используется явный фильтр `Assigned To is not set`.

### Мои назначения

Отдельное поле `assignee` не требуется. В стандартном фильтре `Assigned To` пользователь выбирает `Me`; Frappe фильтрует документы по текущему пользователю через системное `_assign`.

## Kanban

Создаётся одна общая доска:

```text
Kanban Board: Работы
Reference DocType: Work Item
Field: status
Private: No
```

Колонки:

```text
Открыто
Ожидание
Закрыто
Отменено
```

Kanban показывает состояние работы. Исполнитель остаётся отдельным фактом `Assign To`, поэтому отдельной колонки «В работе» нет.

Перетаскивание карточки меняет `Work Item.status` штатным сохранением документа. Оно не синхронизирует связанные `ToDo`; закрытие назначений и закрытие Work Item остаются отдельными действиями.

## Calendar

Для сроков создаётся Calendar View:

```text
Name: Работы по сроку
Reference Document Type: Work Item
Subject Field: subject
Start Date Field: due_date
End Date Field: due_date
All Day: Yes
```

Один `due_date` используется как точка срока, а не как интервал выполнения. Работы без `due_date` не отображаются как календарные события.

`Is Calendar and Gantt` у `Work Item` остаётся выключенным. Именованный `Calendar View` открывается отдельным штатным route и не требует включать общий Calendar/Gantt режим DocType. Поэтому дополнительные `start_date`, `end_date`, `duration` и `progress` только ради Calendar или Gantt не добавляются.

Для прямого входа используется route:

```text
/desk/work-item/view/calendar/%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D1%8B%20%D0%BF%D0%BE%20%D1%81%D1%80%D0%BE%D0%BA%D1%83
```

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

При создании очередного Work Item:

- `subject` копируется;
- `description` копируется;
- `priority` копируется;
- `status` не копируется и получает обычный default `Открыто`;
- `due_date` не копируется;
- `links` не копируются.

Автоматическое назначение исполнителя не является частью текущей конфигурации. Повтор создаёт новую работу в общей очереди, после чего пользователь берёт её через `Assign to me`.

`Work User` не получает отдельные права на DocType `Auto Repeat`. Настройка повторений остаётся административной конфигурацией Site, чтобы не открывать пользователю правила повторения других DocType.

Штатный Auto Repeat не вычисляет для этой модели относительный `due_date` нового Work Item. Если повторяющейся работе понадобится правило вроде «создать 1-го числа со сроком 5-го», это отдельное требование.

## Notifications

Обязательных собственных Notification rules в текущей конфигурации нет.

`Assign To` уже создаёт штатное уведомление о назначении, поэтому отдельная Notification на новое назначение не нужна.

При необходимости можно добавить email-напоминание по сроку Work Item:

```text
Document Type: Work Item
Event: Days Before
Reference Date: due_date
Days Before: 1
Channel: Email
Filters: status in Открыто, Ожидание
Send To All Assignees: Yes
```

Это опциональная конфигурация Site, а не обязательная часть модели.

System Notification по `due_date` только текущим исполнителям не настраивается: Work Item намеренно не хранит собственное поле исполнителя, а рассылка по роли отправила бы уведомление всей группе.

`ToDo.date` не используется как замена `Work Item.due_date`: это `Complete By` конкретного назначения, а не срок самой работы.

## Number Cards

Workspace использует пять Number Cards типа `Document Type` с функцией `Count`:

| Card | Filters |
| --- | --- |
| Активные работы | `status in Открыто, Ожидание` |
| Ожидание | `status = Ожидание` |
| Без исполнителя | `status = Открыто`, `Assigned To is not set` |
| Высокий приоритет | `status in Открыто, Ожидание`, `priority = High` |
| Срок сегодня | `status in Открыто, Ожидание`, `due_date Timespan today` |

Для карточек:

```text
Document Type: Work Item
Function: Count
Is Public: Yes
Show Percentage Stats: No
Dynamic Filters: —
```

Percentage Stats выключены: для текущих состояний они не восстанавливают историческое состояние очереди и поэтому не должны интерпретироваться как изменение её размера во времени.

Number Card кликабельна и открывает отфильтрованный список Work Item, поэтому отдельные shortcuts для `Открытые`, `Ожидание` и `Без исполнителя` не нужны.

## Dashboard Charts

### Активные по статусу

```text
Chart Type: Group By
Document Type: Work Item
Group By Based On: status
Group By Type: Count
Filters: status in Открыто, Ожидание
Type: Donut
Is Public: Yes
```

### Активные по приоритету

```text
Chart Type: Group By
Document Type: Work Item
Group By Based On: priority
Group By Type: Count
Filters: status in Открыто, Ожидание
Type: Bar
Is Public: Yes
```

### Новые работы

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

Dynamic Filters с JavaScript expressions не используются.

## Report Builder

Отдельный обязательный Report Builder report не создаётся. Стандартный Report View используется для разового анализа Work Item, например:

- `Count` по `status`;
- `Count` по `priority`;
- `Count` по `owner`.

`owner` означает создателя Work Item, а не исполнителя.

Текущая модель не позволяет корректно считать через обычный Report Builder:

- кто закрыл Work Item;
- сколько Work Item пользователь завершил за период;
- фактическое время выполнения;
- процент выполнения в срок;
- длительность состояния `Ожидание`.

Для этих показателей в модели нет структурированных фактов завершения и периодов состояния. `modified` не используется как подмена даты закрытия.

## Workspace

Создаётся один общий Workspace:

```text
Label: Управление работой
Title: Управление работой
Type: Workspace
Public: Yes
Roles:
  Work User
```

`Public` означает общий Workspace внутри Desk. Роль `Work User` ограничивает его видимость участниками управления работой.

Редактирование общего Workspace остаётся задачей штатного `Workspace Manager`; прикладной роли `Work User` административные права Workspace не выдаются.

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
  URL: /desk/work-item/view/calendar/%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D1%8B%20%D0%BF%D0%BE%20%D1%81%D1%80%D0%BE%D0%BA%D1%83
```

Для site-level Custom DocType `Work Item` вариант `DocType View: Calendar` не используется: список доступных Calendar shortcuts в Workspace привязан к стандартным calendar hooks / Calendar-Gantt режиму DocType, а созданный `Calendar View` является отдельной именованной конфигурацией. URL shortcut остаётся штатным механизмом Workspace и открывает конкретный `Работы по сроку` без включения Gantt. Штатный URL shortcut Frappe открывает такой адрес в новой вкладке.

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
├── СТРУКТУРА ОЧЕРЕДИ
│   ├── Активные по статусу
│   └── Активные по приоритету
│
└── ПОСТУПЛЕНИЕ
    └── Новые работы
```

Quick List не используется: стандартный Quick List показывает только несколько последних документов по `creation desc`, что не является приоритетной рабочей очередью.

Custom HTML Blocks, отдельный Dashboard, Onboarding и служебные shortcuts для `ToDo`, `Auto Repeat` или `Notification` также не требуются.

## Границы конфигурации

Чистая конфигурация на штатных механизмах Frappe сохраняет несколько известных ограничений:

- `Work Item.status` и `ToDo.status` не синхронизируются автоматически;
- Work User с `Write` на общей очереди может редактировать Work Item и снимать назначение другого Work User;
- `Work Item.due_date` и `ToDo.date` независимы;
- Auto Repeat не вычисляет относительный срок Work Item;
- безопасная командная аналитика по всем назначениям Work Item не получается только через стандартные права на `ToDo`, не открыв другие ToDo Site;
- история `closed_at / closed_by` не хранится отдельными полями.

Эти ограничения сами по себе не являются основанием для собственной разработки. Доработка появляется только после подтверждённой пользовательской необходимости.

## Источники Frappe v16

- [Translations](https://docs.frappe.io/framework/user/en/translations)
- [Translation DocType](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/translation/translation.json)
- [Select control](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/controls/select.js)
- [Kanban View](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/views/kanban/kanban_view.js)
- [Calendar View](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/calendar_view/calendar_view.js)
- [List View selector](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/list/list_view_select.js)
- [Workspace](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace/workspace.py)
- [Workspace Shortcut](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json)
- [Workspace Shortcut widget](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/widgets/shortcut_widget.js)
- [Workspace Quick List](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/widgets/quick_list_widget.js)
- [Number Card](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/number_card/number_card.py)
- [Dashboard Chart](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [Assign To](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py)
- [Auto Repeat](https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [Notification](https://github.com/frappe/frappe/blob/version-16/frappe/email/doctype/notification/notification.py)
