# Управление работой v1: настройка на Frappe v16

Этот гайд позволяет собрать текущий прототип управления работой на чистом Frappe v16 Site только штатными средствами Framework.

Для него не требуется отдельный App, Python, JavaScript, hooks, scripts, custom API или собственный frontend.

Перед настройкой полезно ознакомиться с:

- [Моделью данных v1](data-model-v1.md) — модель `Work Item`;
- [Безопасностью v1](security-v1.md) — роли и права;
- [Конфигурацией v1](configuration-v1.md) — представления, автоматизация, аналитика и Workspace.

## Русский интерфейс

Рабочий интерфейс прототипа настраивается на русском языке. Пользователь или Site должен использовать язык `Russian (ru)`.

Технические идентификаторы и значения данных не переводятся:

```text
DocType: Work Item
fieldnames: subject, description, status, priority, due_date, links
status values: Open, Waiting, Closed, Cancelled
priority values: Low, Medium, High
```

Русскими будут метки полей, названия рабочих представлений и отображение переводимых значений.

## 1. Создайте роль `Work User`

В Desk откройте `Role` и создайте:

```text
Role Name: Work User
Desk Access: Yes
```

Эта роль даёт обычному прикладному пользователю доступ к управлению работой. Обычный доступ в Desk сам по себе не должен открывать `Work Item`; штатный административный доступ `System Manager` и `Administrator` сохраняется отдельно.

## 2. Создайте `Work Item`

Откройте `DocType` → `New`.

Основные настройки:

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

В русском интерфейсе ожидаемое отображение:

```text
Open      → Открыто
Waiting   → Ожидание
Closed    → Закрыто
Cancelled → Отменено
```

Отдельное состояние «В работе» не используется. Активное назначение уже показывает, что открытая работа взята исполнителем.

### Приоритет

Options остаются техническими значениями Frappe:

```text
Low
Medium
High
```

Они совпадают со штатным `ToDo.priority` и не переименовываются.

В русском интерфейсе ожидаемое отображение:

```text
Low    → Низкий
Medium → Средний
High   → Высокий
```

### Срок

`due_date` — необязательный общий срок Work Item. Пустое значение означает отсутствие бизнес-срока.

```text
Work Item.due_date = срок самой работы
ToDo.date          = Complete By конкретного назначения
```

При ручном `Assign To` пустой `Complete By` не означает пустой `ToDo.date`: в v16.33.0 серверная логика `Assign To` подставляет текущую дату. Поэтому `ToDo.date` нельзя использовать как источник общего срока Work Item и нельзя интерпретировать его значение «сегодня» как автоматически установленный бизнес-срок самой работы.

### Связи

Для `links` используйте стандартный дочерний DocType `Dynamic Link`. Отдельный DocType для связей создавать не нужно.

### Переводы

Для собственного DocType создайте запись `Translation`:

| Language | Source Text | Context | Translated Text |
| --- | --- | --- | --- |
| `Russian` | `Work Item` | пусто | `Работа` |

Поле `Language` у `Translation` обязательное; одной пары `Source Text / Translated Text` недостаточно.

Общие значения `Open / Waiting / Closed / Cancelled` и `Low / Medium / High` сначала проверьте под языком `Russian (ru)`: Frappe выводит значения `Select`, List View и заголовки Kanban через механизм перевода. Если конкретная строка остаётся английской, добавьте её штатной записью `Translation`, не меняя фактическое значение поля.

Не заменяйте Options на русские строки ради локализации. В данных должны остаться `Open / Waiting / Closed / Cancelled` и `Low / Medium / High`.

## 3. Настройте права `Work Item`

Откройте `Role Permission Manager`.

Для `Work Item`, permission level `0`, роли `Work User` задайте:

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

При создании DocType Frappe добавляет строку прав для `System Manager`. Не удаляйте её: это штатный административный доступ, а `Work User` — отдельная прикладная роль.

Права стандартного `ToDo` не изменяйте.

## 4. Проверьте Assign To

Создайте тестовый Work Item:

```text
Название: Проверить тестовую работу
Статус: Открыто (Open)
Приоритет: Средний (Medium)
Срок: пусто
```

В данных должны остаться `status = Open` и `priority = Medium`.

Откройте документ под пользователем с ролью `Work User` и выполните:

```text
Assign To
→ Assign to me
```

Frappe создаст связанный `ToDo`. `Work Item.status` при этом должен остаться `Open`.

Рабочая семантика:

```text
Open + нет назначения    = свободная работа
Open + назначение        = работа взята исполнителем
Waiting + назначение     = исполнитель остаётся ответственным, работа ожидает внешнего события
```

## 5. Настройте List View и фильтры

List View остаётся основным экраном очереди.

Используйте:

```text
Название
Статус
Приоритет
Срок
Assigned To
```

Сортировка по умолчанию:

```text
creation DESC
```

Создайте глобальные Saved Filters.

### Активные

```text
status In Open, Waiting
```

### Открытые

```text
status = Open
```

### Ожидание

```text
status = Waiting
```

### Без исполнителя

```text
status = Open
Assigned To Is Not Set
```

Названия Saved Filters русские; условия используют технические значения.

Для личной очереди отдельный глобальный фильтр не нужен. Пользователь выбирает:

```text
Assigned To
→ Me
```

## 6. Создайте Kanban

Создайте общую доску:

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

Под русским языком их заголовки должны отображаться как:

```text
Открыто
Ожидание
Закрыто
Отменено
```

Kanban Frappe переводит заголовок колонки через `__()`, поэтому менять фактические значения `status` не нужно.

Перетаскивание карточки меняет `Work Item.status`. Связанные `ToDo` автоматически не закрываются.

## 7. Создайте Calendar View

Создайте:

```text
Name: Работы по сроку
Reference Document Type: Work Item
Subject Field: subject
Start Date Field: due_date
End Date Field: due_date
All Day: Yes
```

Calendar показывает сроки, а не плановую длительность работ. `Is Calendar and Gantt` у `Work Item` оставьте выключенным.

Именованный Calendar View открывается по route:

```text
/desk/work-item/view/calendar/%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D1%8B%20%D0%BF%D0%BE%20%D1%81%D1%80%D0%BE%D0%BA%D1%83
```

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

Создайте пять карточек:

| Card | Filters |
| --- | --- |
| Активные работы | `status in Open, Waiting` |
| Ожидание | `status = Waiting` |
| Без исполнителя | `status = Open`, `Assigned To Is Not Set` |
| Высокий приоритет | `status in Open, Waiting`, `priority = High` |
| Срок сегодня | `status in Open, Waiting`, `due_date Timespan Today` |

Percentage Stats для текущей очереди выключены: они не восстанавливают историческое состояние `status`.

### Оформление карточек

Frappe v16 штатно поддерживает `Color` и `Background Color` у `Number Card`; Workspace применяет `Background Color` к фону всей карточки, а `Color` — к числовому значению.

Для текущего прототипа используйте спокойную семантическую палитру:

| Card | Color | Background Color |
| --- | --- | --- |
| Активные работы | `#1D4ED8` | `#EFF6FF` |
| Ожидание | `#B45309` | `#FFF7ED` |
| Без исполнителя | `#475569` | `#F1F5F9` |
| Высокий приоритет | `#B91C1C` | `#FEF2F2` |
| Срок сегодня | `#A16207` | `#FEFCE8` |

Цвет здесь помогает быстро различать смысл показателей и убирает ощущение сплошного белого полотна. Он не кодирует новые состояния модели и не заменяет текст карточки.

Если на реальном Desk выбранная тема даёт плохой контраст, меняйте только оттенок оформления; фильтры и смысл Number Card остаются прежними.

## 9. Создайте Dashboard Chart

Создайте один график:

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

`Новые работы` показывает поступление новых работ. Это не показатель производительности или выполненного объёма.

Категориальные графики `Group By` по `status` и `priority` не создавайте: Frappe v16 отдаёт фактические значения `Select` как подписи групп без перевода, поэтому такие графики были бы полурусскими.

## 10. Создайте Workspace

Общий Workspace настраивайте под `Administrator` или пользователем с ролью `Workspace Manager`.

Создайте:

```text
Label: Управление работой
Title: Управление работой
Type: Workspace
Public: Yes
Roles:
  Work User
```

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
  Type: URL
  URL: /desk/work-item/view/calendar/%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D1%8B%20%D0%BF%D0%BE%20%D1%81%D1%80%D0%BE%D0%BA%D1%83
```

Для Calendar не выбирайте `DocType View: Calendar`: у site-level Custom DocType этот вариант не появляется только из-за отдельно созданного `Calendar View`. URL shortcut открывает именно `Работы по сроку` без включения Gantt.

`Color` у Workspace Shortcut не используйте как основной декоративный механизм: в штатном v16 он влияет прежде всего на count-indicator у подходящих DocType shortcuts, а не перекрашивает всю плитку.

### Number Cards

```text
Активные работы
Ожидание
Без исполнителя
Высокий приоритет
Срок сегодня
```

### Charts

```text
Новые работы
```

### Визуальная компоновка

Откройте Workspace в режиме редактирования и разделите экран штатными `Header` blocks. Не складывайте shortcuts, показатели и график в один непрерывный ряд.

Итоговая структура:

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

Практически это означает:

1. Header `Действия` → ряд из четырёх shortcuts.
2. Header `Текущее состояние` → пять Number Cards с заданными выше фонами.
3. Header `Поступление` → график `Новые работы` на отдельной строке.

Не добавляйте декоративные Custom HTML Blocks, собственный CSS или frontend только ради цвета и отступов. Сначала используйте штатную компоновку Workspace и оформление Number Cards.

Quick List не нужен: стандартный Quick List показывает несколько последних документов по `creation desc`, а не приоритетную рабочую очередь.

## 11. Auto Repeat

Auto Repeat создавайте только для конкретной повторяющейся работы.

```text
Reference Document Type: Work Item
Reference Document: нужный Work Item
Submit on Creation: No
Assignee: пусто
Generate Separate Documents For Each Assignee: No
Notify by Email: No
```

Новый Work Item получает:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → Open
due_date     → пусто
links        → пусто
назначения   → отсутствуют
```

Новый экземпляр попадает в общую очередь и назначается обычным `Assign to me`.

`Work User` не нужно выдавать права управления DocType `Auto Repeat`; настройка повторений остаётся административной конфигурацией Site.

## 12. Notifications

Обязательные Notification rules для запуска управления работой не нужны. `Assign To` уже создаёт штатное уведомление о назначении.

При необходимости можно добавить email-напоминание за день до общего срока:

```text
Document Type: Work Item
Event: Days Before
Reference Date: due_date
Days Before: 1
Channel: Email
Filters: status in Open, Waiting
Send To All Assignees: Yes
```

## 13. Рабочий цикл

### Обычная работа

```text
создать Work Item
→ Open (Открыто)
→ Assign to me
→ выполнить работу
→ закрыть назначение
→ Work Item = Closed (Закрыто)
```

### Ожидание

```text
Open (Открыто)
→ добавить комментарий с контекстом
→ Waiting (Ожидание)
→ получить ответ / документ / решение
→ Open (Открыто)
```

Назначение при этом можно сохранить.

### Отмена

```text
снять активные назначения
→ Work Item = Cancelled (Отменено)
```

Work Item не удаляется.

### Передача другому исполнителю

```text
добавить контекст передачи в Timeline
→ снять старое назначение
→ назначить нового пользователя
```

## 14. Проверка после настройки

После настройки проверьте основные сценарии.

1. Пользователь с `Work User` создаёт Work Item, второй `Work User` видит его в общей очереди.
2. После `Assign to me` работа исчезает из `Без исполнителя` и появляется в `Assigned To → Me`.
3. `Open → Waiting` отображается пользователю как `Открыто → Ожидание`, назначение остаётся.
4. `Waiting → Open` возвращает работу в активную очередь без потери назначения.
5. Закрытие собственного ToDo не закрывает Work Item автоматически; Work Item переводится в `Closed` отдельно.
6. При нескольких исполнителях каждый получает отдельный ToDo.
7. Для отмены сначала снимаются назначения, затем Work Item переводится в `Cancelled`.
8. Обычный System User без `Work User` и без административной роли не получает доступа к Work Item.
9. `Work User` не может удалить Work Item.
10. Work Item со сроком отображается в `Работы по сроку` и соответствующих Number Cards.
11. Workspace `Управление работой` доступен пользователю с `Work User`.
12. В русском интерфейсе `Work Item` отображается как `Работа`, статусы и приоритеты — по-русски, при этом их технические значения не изменены.
13. Kanban показывает русские заголовки колонок при технических значениях `Open / Waiting / Closed / Cancelled`.
14. Workspace визуально разделён на `Действия`, `Текущее состояние` и `Поступление`; Number Cards имеют различимые спокойные фоны, текст и числа читаются без потери контраста.

## 15. Известные ограничения штатной версии v1

- `Work Item.status` и `ToDo.status` не синхронизируются автоматически;
- `Work Item.due_date` и `ToDo.date` имеют разную семантику; при ручном Assign To без `Complete By` Frappe задаёт `ToDo.date` текущей датой;
- все `Work User` имеют `Read` общей очереди, а штатное снятие назначения проверяет `Read` исходного `Work Item`, поэтому один `Work User` может снять назначение другого;
- Auto Repeat не вычисляет относительный срок нового Work Item;
- Dashboard Chart `Group By` не переводит значения `Select`, поэтому категориальные графики по `status` и `priority` не входят в русскую конфигурацию;
- текущая модель не хранит отдельные `closed_at` и `closed_by`;
- безопасная общая аналитика по всем назначениям Work Item не строится простым расширением доступа к `ToDo`, не открывая другие ToDo Site.

Эти ограничения не требуют собственной разработки до тех пор, пока реальная эксплуатация не покажет конкретную пользовательскую проблему.

## Источники

Текущий ориентир — Frappe v16.33.0.

- [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Translations](https://docs.frappe.io/framework/user/en/translations)
- [Translation metadata](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/translation/translation.json)
- [Select control](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/controls/select.js)
- [Kanban column template](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/kanban/kanban_column.html)
- [Kanban Board](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/kanban_board/kanban_board.py)
- [Dashboard Chart](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [DocType form](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.js)
- [Permissions](https://github.com/frappe/frappe/blob/v16.33.0/frappe/permissions.py)
- [Assign To](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [Auto Repeat](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [Calendar View](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/calendar_view/calendar_view.js)
- [Workspace Shortcut](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json)
- [Workspace Shortcut widget](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/widgets/shortcut_widget.js)
- [Number Card](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/number_card/number_card.json)
- [Number Card widget](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/widgets/number_card_widget.js)
- [Workspace](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [Workspace editor](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/views/workspace/workspace.js)