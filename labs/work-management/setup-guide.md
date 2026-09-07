# Управление работой v1: сборка на Frappe v16

Этот гайд собирает текущий Work Management Lab на development Site штатным developer path Frappe v16.

Прототип использует минимальный App `work_management`, standard DocType `Work Item` и стандартные механизмы Framework. Прикладная бизнес-логика и собственный frontend на текущем этапе не требуются. Единственный JS-файл, который появляется в baseline помимо обычного boilerplate DocType, — standard calendar config `Work Item`, создаваемый самим Frappe developer path.

Перед настройкой полезно ознакомиться с:

- [Моделью данных v1](data-model-v1.md) — модель `Work Item`;
- [Безопасностью v1](security-v1.md) — роли и права;
- [Конфигурацией v1](configuration-v1.md) — представления, автоматизация, аналитика и Workspace.

## 0. Подготовьте development Site и App

Работайте на отдельном development Site, а не на рабочем Site с пользовательскими данными.

Из корня `frappe-bench` включите Developer Mode штатной командой Frappe:

```bash
bench set-config -g developer_mode 1
bench --site <site> clear-cache
```

Создайте App штатным Bench:

```bash
bench new-app work_management
```

Для Lab используйте:

```text
App Title: Work Management
App Description: Work Management prototype for VEQTA Labs
App Publisher: VEQTA
App License: MIT
```

Установите App на тестовый Site:

```bash
bench --site <site> install-app work_management
bench --site <site> list-apps
```

В списке должны присутствовать как минимум:

```text
frappe
work_management
```

Не создавайте App-каркас вручную. `bench new-app` является штатным источником структуры App для используемой версии Bench/Frappe.

Developer Mode нужен для проектирования и экспорта standard metadata в App. Обычная пользовательская работа после сборки не должна требовать Developer Mode.

## Русский интерфейс

Интерфейс тестовых пользователей переключите на `Russian (ru)`.

Технические идентификаторы и значения данных не переводятся:

```text
DocType: Work Item
fieldnames: subject, description, status, priority, due_date, links
status values: Open, Waiting, Closed, Cancelled
priority values: Low, Medium, High
```

Русскими задаются пользовательские метки, названия представлений и перевод отображаемых значений.

## 1. Создайте роль `Work User`

Создайте роль:

```text
Role Name: Work User
Desk Access: Yes
```

`Work User` — прикладная роль участников общей очереди. Административные `Administrator` и `System Manager` остаются отдельной границей.

Для текущего live prototype роль можно создать на Site. Если Lab App затем фиксируется как воспроизводимый артефакт, обязательная роль должна доставляться App штатным механизмом, а не ручной инструкцией для каждого Site.

## 2. Создайте standard DocType `Work Item`

Под `Administrator` откройте `DocType` → `New`.

Основные настройки:

```text
Name: Work Item
Module: Work Management
Custom: No

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
Is Calendar and Gantt: Yes
Force Re-route to Default View: No

Sort Field: creation
Sort Order: DESC
```

Ключевая проверка: DocType должен относиться к модулю App и быть standard, а не site-level `Custom DocType`.

В Developer Mode Frappe экспортирует standard DocType в App и создаёт обычный controller-файл. При `Is Calendar and Gantt = Yes` Framework также создаёт standard `<doctype>_calendar.js`. Не добавляйте в Python controller бизнес-логику без отдельного подтверждённого требования.

Добавьте поля в таком порядке:

| Метка | Fieldname | Type | Required | Default | No Copy | List | Standard Filter | Global Search | Quick Entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Название | `subject` | Data | yes | — | no | title | no | yes | required field |
| Описание | `description` | Text Editor | no | — | no | no | no | yes | yes |
| Статус | `status` | Select | yes | `Open` | yes | yes | yes | no | required field |
| Приоритет | `priority` | Select | yes | `Medium` | no | yes | yes | no | required field |
| Срок | `due_date` | Date | no | — | yes | yes | yes | no | yes |
| Связи | `links` | Table → `Dynamic Link` | no | — | yes | no | no | no | no |

### Статус

Options:

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

Отдельного состояния «В работе» нет. `Open` + активное назначение уже означает, что работа взята исполнителем.

### Приоритет

Options:

```text
Low
Medium
High
```

Они совпадают со штатным `ToDo.priority`.

### Срок

```text
Work Item.due_date = срок самой работы
ToDo.date          = Complete By конкретного назначения
```

Не используйте `ToDo.date` как подмену общего срока Work Item.

### Связи

Для `links` используйте стандартный дочерний DocType `Dynamic Link`. Собственный DocType связей не создавайте.

### Переводы

Ожидаемое отображение:

```text
Work Item   → Работа
Open        → Открыто
Waiting     → Ожидание
Closed      → Закрыто
Cancelled   → Отменено
Low         → Низкий
Medium      → Средний
High        → Высокий
```

Не заменяйте technical Options русскими строками. Если конкретная строка не переведена текущим словарём, добавляйте перевод штатным механизмом Frappe.

## 3. Настройте права `Work Item`

Для `Work Item`, permission level `0`, роли `Work User`:

| Permission | Значение |
| --- | --- |
| Read | Yes |
| Create | Yes |
| Write | Yes |
| Report | Yes |
| Delete | No |
| Share | No |
| Import | No |
| Export | No |
| Print | No |
| Email | No |
| Submit | No |
| Cancel | No |
| Amend | No |
| If Owner | No |

Не удаляйте штатный административный доступ `System Manager`.

Права стандартного `ToDo` не расширяйте.

## 4. Проверьте `Assign To`

Создайте тестовый Work Item:

```text
Название: Проверить тестовую работу
Статус: Открыто (Open)
Приоритет: Средний (Medium)
Срок: пусто
```

Выполните:

```text
Assign To
→ Assign to me
```

Ожидается отдельный связанный `ToDo`, при этом `Work Item.status` остаётся `Open`.

Рабочая семантика:

```text
Open + нет назначения = свободная работа
Open + назначение     = работа взята исполнителем
Waiting + назначение  = исполнитель остаётся ответственным, работа ждёт внешнего события
```

## 5. Настройте List View и Saved Filters

Основной рабочий список:

```text
Название
Статус
Приоритет
Срок
Assigned To
```

Сортировка:

```text
creation DESC
```

Глобальные Saved Filters:

```text
Активные
status In Open, Waiting

Открытые
status = Open

Ожидание
status = Waiting

Без исполнителя
status = Open
Assigned To Is Not Set
```

Для личной очереди используйте стандартный фильтр:

```text
Assigned To
→ Me
```

## 6. Создайте Kanban

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

Пользователь должен видеть русские подписи. Перетаскивание меняет `Work Item.status`, но не закрывает связанный `ToDo`.

## 7. Настройте standard Calendar

Отдельный `Calendar View` не создавайте.

После сохранения standard `Work Item` с `Is Calendar and Gantt = Yes` найдите созданный Frappe файл `<doctype>_calendar.js` в каталоге DocType App и задайте штатный calendar config:

```javascript
frappe.views.calendar["Work Item"] = {
	field_map: {
		start: "due_date",
		end: "due_date",
		id: "name",
		title: "subject",
	},
	get_events_method: "frappe.desk.calendar.get_events",
};
```

Calendar показывает `due_date` как точку срока. Использование одного поля одновременно как `start` и `end` является адаптацией к Calendar API, а не новой семантикой интервала.

### Известный Gantt gap

В Frappe v16 тот же `frappe.views.calendar["Work Item"]` делает доступным пункт Gantt. Для текущего `Work Item` Gantt не считается рабочим представлением: модель не содержит `start_date`, `end_date`, `progress` или отдельной длительности.

Это принимается как известный gap. Не добавляйте поля, фиктивные даты, зависимости или progress только ради работоспособности Gantt. Поддерживаемый сценарий сроков — Calendar по `due_date`.

## 8. Создайте Number Cards

Все карточки:

```text
Type: Document Type
Document Type: Work Item
Function: Count
Is Public: Yes
Show Percentage Stats: No
Dynamic Filters: пусто
```

Карточки:

| Card | Filters |
| --- | --- |
| Активные работы | `status in Open, Waiting` |
| Ожидание | `status = Waiting` |
| Без исполнителя | `status = Open`, `Assigned To Is Not Set` |
| Высокий приоритет | `status in Open, Waiting`, `priority = High` |
| Срок сегодня | `status in Open, Waiting`, `due_date Timespan Today` |

### Оформление

Используйте штатные `Color` и `Background Color`:

| Card | Color | Background Color |
| --- | --- | --- |
| Активные работы | `#1D4ED8` | `#EFF6FF` |
| Ожидание | `#B45309` | `#FFF7ED` |
| Без исполнителя | `#475569` | `#F1F5F9` |
| Высокий приоритет | `#B91C1C` | `#FEF2F2` |
| Срок сегодня | `#A16207` | `#FEFCE8` |

Цвет — только визуальная семантика, не новое состояние модели.

## 9. Создайте Dashboard Chart

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

График показывает поступление новых Work Item и не трактуется как производительность.

Простой `Group By` по `status`/`priority` пока не используется из-за отображения technical Select values. Это ограничение выбранной конфигурации, а не всей системы графиков Frappe: при подтверждённой необходимости developer path оставляет доступным `Dashboard Chart Source`.

## 10. Создайте Workspace

Создайте public Workspace:

```text
Label: Управление работой
Title: Управление работой
Type: Workspace
Public: Yes
Module: Work Management
Roles:
  Work User
```

Developer Mode позволяет привязать Workspace к module App и экспортировать public Workspace как standard metadata.

Для Workspace используйте штатные icon/indicator settings. Не отказывайтесь от developer-only полей только ради совместимости с режимом администрирования production Site.

### Shortcuts

```text
Новая работа
  Type: DocType
  Link To: Work Item
  DocType View: New

Список работ
  Type: DocType
  Link To: Work Item
  DocType View: List

Доска
  Type: DocType
  Link To: Work Item
  DocType View: Kanban
  Kanban Board: Работы

Календарь
  Type: DocType
  Link To: Work Item
  DocType View: Calendar
```

Используйте штатный Calendar route DocType. URL на именованный `Calendar View` не нужен.

### Визуальная компоновка

Разделите экран штатными Header blocks:

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

Не добавляйте Custom HTML, собственный CSS или frontend только ради цвета и отступов. Сначала используйте штатные возможности Workspace.

## 11. Auto Repeat

Для конкретной повторяющейся работы создайте стандартный `Auto Repeat` без обязательного Assignee.

Новый Work Item должен получать:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → Open
due_date     → пусто
links        → пусто
назначения   → отсутствуют
```

Если появится требование относительного срока нового экземпляра, не пишите собственный scheduler. Frappe v16 после подготовки повторного документа вызывает `Work Item.on_recurring(...)`; именно эту штатную controller extension point нужно проверить первой.

Пока такого требования нет, controller остаётся без бизнес-логики.

## 12. Notifications

Обязательные собственные Notification rules для запуска не нужны: `Assign To` уже создаёт штатное уведомление о назначении.

Опционально можно настроить email-напоминание по `Work Item.due_date`. Оно не является частью предметной модели.

## 13. Рабочий цикл

### Обычная работа

```text
создать Work Item
→ Open
→ Assign to me
→ выполнить
→ закрыть своё назначение
→ Work Item = Closed
```

### Ожидание

```text
Open
→ добавить комментарий с контекстом
→ Waiting
→ получить ответ / документ / решение
→ Open
```

### Отмена

```text
снять активные назначения
→ Work Item = Cancelled
```

### Передача

```text
добавить контекст в Timeline
→ снять старое назначение
→ назначить нового пользователя
```

## 14. Проверка developer delivery

После сохранения standard `Work Item` и public Workspace проверьте, что изменения действительно попали в App, а не остались только database-state конкретного Site.

Минимально проверьте:

```bash
git status
```

в каталоге App и наличие экспортированных metadata Frappe для `Work Item`/Workspace там, где их создаёт используемая версия Framework.

Отдельно убедитесь, что standard calendar config `Work Item` находится в App рядом с DocType и не зависит от отдельного `Calendar View` database record.

Не придумывайте расположение файлов заранее: эталоном является фактическая структура, созданная Frappe/Bench v16 на стенде.

После этого выполните:

```bash
bench --site <site> migrate
bench --site <site> clear-cache
```

## 15. Проверка пользовательского режима

Основные пользовательские сценарии должны работать независимо от Developer Mode.

После фиксации App можно отдельно проверить Site с `developer_mode = 0`: обычный `Work User` должен пользоваться очередью, формой, Kanban, Calendar и Workspace без developer privileges.

Пункт Gantt может оставаться видимым. Его работоспособность не является частью runtime-контракта текущего Lab и не считается причиной расширять модель.

Developer Mode остаётся режимом разработки, а не обязательным условием эксплуатации.

## 16. Критерии готовности

1. `Work Item` является standard DocType модуля `Work Management`, а не site-level Custom DocType.
2. Предметная модель содержит только `subject`, `description`, `status`, `priority`, `due_date`, `links`.
3. Назначения работают через стандартный `ToDo`.
4. Права соответствуют `security-v1.md`.
5. List/Kanban/Calendar/Number Cards/Chart/Workspace работают без собственного frontend; видимый Gantt принят как неподдерживаемый gap.
6. Workspace визуально разделён и читаем, Number Cards имеют спокойные различимые фоны.
7. Обязательное standard metadata фиксируется через App developer path, включая standard calendar config.
8. Собственная бизнес-логика в controller отсутствует, пока нет подтверждённого поведения, которое Framework не закрывает конфигурацией или официальной точкой расширения.

## Источники

Текущий ориентир — Frappe v16.33.0 и соответствующий Bench v5.

- [Frappe Apps](https://docs.frappe.io/framework/user/en/guides/basics/apps)
- [Create an App](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [Developer Mode](https://docs.frappe.io/framework/user/en/guides/app-development/how-enable-developer-mode-in-frappe)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Site Config](https://docs.frappe.io/framework/user/en/basics/site_config)
- [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [`DocType` controller, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Calendar boilerplate`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/boilerplate/controller_calendar.js)
- [`ToDo Calendar`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo_calendar.js)
- [`List View selector`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/list/list_view_select.js)
- [`Gantt View`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/gantt/gantt_view.js)
- [`Workspace`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
