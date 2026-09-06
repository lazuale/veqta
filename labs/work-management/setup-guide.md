# Управление работой v1: настройка на Frappe v16

Этот гайд позволяет собрать текущий прототип управления работой на чистом Frappe v16 Site только штатными средствами Framework.

Для него не требуется отдельный App, Python, JavaScript, hooks, scripts, custom API или собственный frontend.

Перед настройкой полезно ознакомиться с:

- [Моделью данных v1](data-model-v1.md) — модель `Work Item`;
- [Безопасностью v1](security-v1.md) — роли и права;
- [Конфигурацией v1](configuration-v1.md) — представления, автоматизация, аналитика и Workspace.

## Русский интерфейс

Рабочий интерфейс прототипа настраивается на русском языке. Пользователь или Site должен использовать язык `Russian (ru)`.

Технические идентификаторы не переводятся:

```text
DocType: Work Item
fieldnames: subject, description, status, priority, due_date, links
priority values: Low, Medium, High
```

Русскими будут метки полей, статусы и имена рабочих представлений. Для имени `Work Item` и значений приоритета используются штатные записи `Translation`.

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

| Label | Fieldname | Type | Required | Default | No Copy | List | Standard Filter | Global Search | Quick Entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Название | `subject` | Data | yes | — | no | title | no | yes | required field |
| Описание | `description` | Text Editor | no | — | no | no | no | yes | yes |
| Статус | `status` | Select | yes | `Открыто` | yes | yes | yes | no | required field |
| Приоритет | `priority` | Select | yes | `Medium` | no | yes | yes | no | required field |
| Срок | `due_date` | Date | no | — | yes | yes | yes | no | yes |
| Связи | `links` | Table → `Dynamic Link` | no | — | yes | no | no | no | no |

### Статус

Options:

```text
Открыто
Ожидание
Закрыто
Отменено
```

Семантика:

- `Открыто` — работа актуальна и может выполняться;
- `Ожидание` — работа актуальна, но продолжение зависит от внешнего события;
- `Закрыто` — работа завершена;
- `Отменено` — работа больше не требуется.

Отдельное состояние «В работе» не используется. Активное назначение уже показывает, что открытая работа взята исполнителем.

### Приоритет

Options остаются техническими значениями Frappe:

```text
Low
Medium
High
```

Они совпадают со штатным `ToDo.priority` и не переименовываются.

### Срок

`due_date` — необязательный общий срок Work Item. Пустое значение означает отсутствие бизнес-срока.

Не путайте его с `ToDo.date`:

```text
Work Item.due_date = срок самой работы
ToDo.date          = Complete By конкретного назначения
```

### Связи

Для `links` используйте стандартный дочерний DocType `Dynamic Link`. Отдельный DocType для связей создавать не нужно.

### Переводы

Откройте `Translation` и создайте четыре записи для языка `Russian`:

| Source Text | Context | Translated Text |
| --- | --- | --- |
| `Work Item` | пусто | `Работа` |
| `Low` | `Work Item` | `Низкий` |
| `Medium` | `Work Item` | `Средний` |
| `High` | `Work Item` | `Высокий` |

Контекст `Work Item` у приоритетов обязателен: он ограничивает перевод нашей моделью и не меняет `Low / Medium / High` во всех остальных DocType.

Для статусов отдельные Translation не создавайте. Их реальные значения уже русские, потому что стандартный Kanban использует значение поля как имя колонки.

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

Права стандартного `ToDo` не изменяйте. Управление работой использует штатную модель доступа Frappe к назначениям.

## 4. Проверьте Assign To

Создайте тестовый Work Item:

```text
Название: Проверить тестовую работу
Статус: Открыто
Приоритет: Средний
Срок: пусто
```

В базе значение приоритета останется `Medium`, хотя в русском интерфейсе должно отображаться `Средний`.

Откройте документ под пользователем с ролью `Work User` и выполните:

```text
Assign To
→ Assign to me
```

Frappe создаст связанный `ToDo`. `Work Item.status` при этом должен остаться `Открыто`.

Рабочая семантика:

```text
Открыто + нет назначения = свободная работа
Открыто + назначение     = работа взята исполнителем
Ожидание + назначение    = исполнитель остаётся ответственным, работа ожидает внешнего события
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
Статус In Открыто, Ожидание
```

### Открытые

```text
Статус = Открыто
```

### Ожидание

```text
Статус = Ожидание
```

### Без исполнителя

```text
Статус = Открыто
Assigned To Is Not Set
```

Для неназначенной очереди используйте обычный Filter UI с `Assigned To Is Not Set`.

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

Колонки:

```text
Открыто
Ожидание
Закрыто
Отменено
```

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

Calendar показывает сроки, а не плановую длительность работ. `Is Calendar and Gantt` у `Work Item` оставьте выключенным; дополнительные `start_date`, `end_date`, `duration` и `progress` для этого не нужны.

Именованный Calendar View открывается по штатному route:

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
| Активные работы | `status in Открыто, Ожидание` |
| Ожидание | `status = Ожидание` |
| Без исполнителя | `status = Открыто`, `Assigned To Is Not Set` |
| Высокий приоритет | `status in Открыто, Ожидание`, `priority = High` |
| Срок сегодня | `status in Открыто, Ожидание`, `due_date Timespan Today` |

Percentage Stats для текущей очереди выключены: они не восстанавливают историческое состояние `status` и поэтому не показывают корректную динамику очереди.

## 9. Создайте Dashboard Charts

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

`Новые работы` показывает поступление новых работ. Это не показатель производительности или выполненного объёма.

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

`Public` здесь означает общий Workspace внутри Desk. Он остаётся ограниченным пользователями, которым разрешён этот Workspace и исходные объекты.

### Shortcuts

Добавьте:

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

Для Calendar не выбирайте `DocType View: Calendar`: у site-level Custom DocType этот вариант не появляется только из-за отдельно созданного `Calendar View`. URL shortcut — штатный механизм Workspace и открывает именно `Работы по сроку` без включения Gantt. Штатный URL shortcut Frappe открывает адрес в новой вкладке.

### Number Cards

Добавьте:

```text
Активные работы
Ожидание
Без исполнителя
Высокий приоритет
Срок сегодня
```

### Charts

Добавьте:

```text
Активные по статусу
Активные по приоритету
Новые работы
```

Итоговый экран:

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

Quick List не нужен: стандартный Quick List показывает несколько последних документов по `creation desc`, а не приоритетную рабочую очередь.

## 11. Auto Repeat

Auto Repeat создавайте только для конкретной повторяющейся работы.

Типовая конфигурация:

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
status       → Открыто
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
Filters: status in Открыто, Ожидание
Send To All Assignees: Yes
```

## 13. Рабочий цикл

### Обычная работа

```text
создать Work Item
→ Открыто
→ Assign to me
→ выполнить работу
→ закрыть назначение
→ Work Item = Закрыто
```

### Ожидание

```text
Открыто
→ добавить комментарий с контекстом
→ Ожидание
→ получить ответ / документ / решение
→ Открыто
```

Назначение при этом можно сохранить.

### Отмена

```text
снять активные назначения
→ Work Item = Отменено
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
3. `Открыто → Ожидание` переносит работу в ожидание, назначение остаётся.
4. `Ожидание → Открыто` возвращает работу в активную очередь без потери назначения.
5. Закрытие собственного ToDo не закрывает Work Item автоматически; после завершения Work Item переводится в `Закрыто` отдельно.
6. При нескольких исполнителях каждый получает отдельный ToDo.
7. Для отмены сначала снимаются назначения, затем Work Item переводится в `Отменено`.
8. Обычный System User без `Work User` и без административной роли не получает доступа к Work Item.
9. `Work User` не может удалить Work Item.
10. Work Item со сроком отображается в `Работы по сроку` и соответствующих Number Cards.
11. Workspace `Управление работой` доступен пользователю с `Work User`.
12. В русском интерфейсе имя DocType отображается как `Работа`, а приоритеты — `Низкий / Средний / Высокий`.

## 15. Известные ограничения штатной версии v1

Текущая конфигурация сознательно оставляет несколько границ штатного Frappe:

- `Work Item.status` и `ToDo.status` не синхронизируются автоматически;
- `Work Item.due_date` и `ToDo.date` имеют разную семантику;
- Work User с `Write` на общей очереди может редактировать Work Item и снимать назначение другого Work User;
- Auto Repeat не вычисляет относительный срок нового Work Item;
- текущая модель не хранит отдельные `closed_at` и `closed_by`;
- безопасная общая аналитика по всем назначениям Work Item не строится простым расширением доступа к `ToDo`, не открывая другие ToDo Site.

Эти ограничения не требуют собственной разработки до тех пор, пока реальная эксплуатация не покажет конкретную пользовательскую проблему.

## Источники

Текущий ориентир — Frappe v16.

- [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Translations](https://docs.frappe.io/framework/user/en/translations)
- [Translation DocType](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/translation/translation.json)
- [Select control](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/controls/select.js)
- [Kanban View](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/views/kanban/kanban_view.js)
- [DocType form](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/doctype/doctype.js)
- [Permissions](https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py)
- [Assign To](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py)
- [Auto Repeat](https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [Calendar View](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/calendar_view/calendar_view.js)
- [Workspace Shortcut widget](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/widgets/shortcut_widget.js)
- [Workspace](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace/workspace.py)
