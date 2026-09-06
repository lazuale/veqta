# Work Management v1: настройка на Frappe v16

Этот гайд позволяет собрать текущий Work Management prototype на чистом Frappe v16 Site только штатными средствами Framework.

Для Work Management не требуется отдельный App, Python, JavaScript, hooks, scripts, custom API или собственный frontend.

Перед настройкой полезно ознакомиться с:

- [Data Model v1](data-model-v1.md) — модель `Work Item`;
- [Security v1](security-v1.md) — роли и права;
- [Configuration v1](configuration-v1.md) — представления, автоматизация, аналитика и Workspace.

## 1. Создайте роль `Work User`

В Desk откройте `Role` и создайте:

```text
Role Name: Work User
Desk Access: Yes
```

Эта роль даёт пользователю доступ к Work Management. Обычный доступ в Desk сам по себе не должен открывать `Work Item`.

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
| Subject | `subject` | Data | yes | — | no | title | no | yes | required field |
| Description | `description` | Text Editor | no | — | no | no | no | yes | yes |
| Status | `status` | Select | yes | `Open` | yes | yes | yes | no | required field |
| Priority | `priority` | Select | yes | `Medium` | no | yes | yes | no | required field |
| Due Date | `due_date` | Date | no | — | yes | yes | yes | no | yes |
| Links | `links` | Table → `Dynamic Link` | no | — | yes | no | no | no | no |

### Status

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

Отдельный `In Progress` не используется. Активный assignment уже показывает, что открытая работа взята исполнителем.

### Priority

Options:

```text
Low
Medium
High
```

Эти значения совпадают со штатным `ToDo.priority` Frappe.

### Due Date

`due_date` — необязательный общий срок Work Item. Пустое значение означает отсутствие бизнес-срока.

Не путайте его с `ToDo.date`:

```text
Work Item.due_date = срок самой работы
ToDo.date          = Complete By конкретного assignment
```

### Links

Для `links` используйте стандартный child DocType `Dynamic Link`. Отдельный DocType для связей создавать не нужно.

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

Права стандартного `ToDo` не изменяйте. Work Management использует штатную модель доступа Frappe к назначениям.

## 4. Проверьте Assign To

Создайте тестовый Work Item:

```text
Subject: Проверить тестовую работу
Status: Open
Priority: Medium
Due Date: пусто
```

Откройте документ под пользователем с ролью `Work User` и выполните:

```text
Assign To
→ Assign to me
```

Frappe создаст связанный `ToDo`. `Work Item.status` при этом должен остаться `Open`.

Рабочая семантика:

```text
Open + нет assignment = свободная работа
Open + assignment     = работа взята исполнителем
Waiting + assignment  = исполнитель остаётся ответственным, работа ожидает внешнего события
```

## 5. Настройте List View и фильтры

List View остаётся основным экраном очереди.

Используйте:

```text
Subject
Status
Priority
Due Date
Assigned To
```

Сортировка по умолчанию:

```text
creation DESC
```

Создайте глобальные Saved Filters.

### Active

```text
Status In Open, Waiting
```

### Open

```text
Status = Open
```

### Waiting

```text
Status = Waiting
```

### Unassigned

```text
Status = Open
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

Перетаскивание карточки меняет `Work Item.status`. Связанные `ToDo` автоматически не закрываются.

## 7. Создайте Calendar View

Создайте:

```text
Name: Work Items by Due Date
Reference Document Type: Work Item
Subject Field: subject
Start Date Field: due_date
End Date Field: due_date
All Day: Yes
```

Calendar показывает сроки, а не плановую длительность работ. Дополнительные `start_date`, `end_date`, `duration` и `progress` для этого не нужны.

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
| Active Work | `status in Open, Waiting` |
| Waiting | `status = Waiting` |
| Unassigned | `status = Open`, `Assigned To Is Not Set` |
| High Priority | `status in Open, Waiting`, `priority = High` |
| Due Today | `status in Open, Waiting`, `due_date Timespan Today` |

Percentage Stats для текущей очереди выключены: они не восстанавливают историческое состояние `status` и поэтому не показывают корректную динамику backlog.

## 9. Создайте Dashboard Charts

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

`New Work Items` показывает поступление новых работ. Это не показатель производительности или выполненного объёма.

## 10. Создайте Workspace

Общий Workspace настраивайте под `Administrator` или пользователем с ролью `Workspace Manager`.

Создайте:

```text
Name: Work Management
Type: Workspace
Public: Yes
Roles:
  Work User
```

`Public` здесь означает общий Workspace внутри Desk. Он остаётся ограниченным пользователями, которым разрешён этот Workspace и исходные объекты.

### Shortcuts

Добавьте:

```text
New Work Item
  Type: DocType
  Link To: Work Item
  DocType View: New

Work List
  Type: DocType
  Link To: Work Item
  DocType View: List

Board
  Type: DocType
  Link To: Work Item
  DocType View: Kanban
  Kanban Board: Work Items

Calendar
  Type: DocType
  Link To: Work Item
  DocType View: Calendar
```

### Number Cards

Добавьте:

```text
Active Work
Waiting
Unassigned
High Priority
Due Today
```

### Charts

Добавьте:

```text
Active Work by Status
Active Work by Priority
New Work Items
```

Итоговый экран:

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

Quick List в baseline не нужен: стандартный Quick List показывает несколько последних документов по `creation desc`, а не приоритетную рабочую очередь.

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
status       → Open
due_date     → пусто
links        → пусто
assignments  → отсутствуют
```

Новый экземпляр попадает в общую очередь и назначается обычным `Assign to me`.

`Work User` не нужно выдавать права управления DocType `Auto Repeat`; настройка повторений остаётся административной конфигурацией Site.

## 12. Notifications

Обязательные Notification rules для запуска Work Management не нужны. `Assign To` уже создаёт штатное уведомление о назначении.

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
→ Open
→ Assign to me
→ выполнить работу
→ закрыть assignment
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

Assignment при этом можно сохранить.

### Отмена

```text
снять активные assignments
→ Work Item = Cancelled
```

Work Item не удаляется.

### Передача другому исполнителю

```text
добавить контекст передачи в Timeline
→ снять старый assignment
→ назначить нового пользователя
```

## 14. Smoke test

После настройки проверьте основные сценарии.

1. Пользователь с `Work User` создаёт Work Item, второй `Work User` видит его в общей очереди.
2. После `Assign to me` работа исчезает из `Unassigned` и появляется в `Assigned To → Me`.
3. `Open → Waiting` переносит работу в Waiting, assignment остаётся.
4. `Waiting → Open` возвращает работу в активную очередь без потери assignment.
5. Закрытие собственного ToDo не закрывает Work Item автоматически; после завершения Work Item переводится в `Closed` отдельно.
6. При нескольких исполнителях каждый получает отдельный ToDo.
7. Для отмены сначала снимаются assignments, затем Work Item переводится в `Cancelled`.
8. Пользователь без `Work User` не получает доступа к Work Item.
9. `Work User` не может удалить Work Item.
10. Work Item со сроком отображается в Calendar и соответствующих Number Cards.
11. Workspace `Work Management` доступен пользователю с `Work User`.

## 15. Известные ограничения native v1

Текущая конфигурация сознательно оставляет несколько границ штатного Frappe:

- `Work Item.status` и `ToDo.status` не синхронизируются автоматически;
- `Work Item.due_date` и `ToDo.date` имеют разную семантику;
- Work User с `Write` на общей очереди может редактировать Work Item и снимать assignment другого Work User;
- Auto Repeat не вычисляет относительный срок нового Work Item;
- текущая модель не хранит отдельные `closed_at` и `closed_by`;
- безопасная общая аналитика по всем Work Item assignments не строится простым расширением доступа к `ToDo`, не открывая другие ToDo Site.

Эти ограничения не требуют собственной разработки до тех пор, пока реальная эксплуатация не покажет конкретную пользовательскую проблему.

## Источники

Текущий ориентир — Frappe v16.

- [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Frappe v16 source](https://github.com/frappe/frappe/tree/version-16)
- [Assign To](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py)
- [Auto Repeat](https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [Workspace](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace/workspace.py)
