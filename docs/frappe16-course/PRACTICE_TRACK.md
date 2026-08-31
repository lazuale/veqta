# Сквозное состояние практического курса Frappe 16

Этот файл не заменяет лабораторные. Он фиксирует, **что должно существовать на стенде после каждого блока**, чтобы следующая практика была воспроизводимой.

Основной стенд: [00_LAB_SETUP.md](00_LAB_SETUP.md).

Полный индекс лабораторных: [labs/README.md](labs/README.md).

---

# После главы 0

```text
Bench:  ~/frappe/frappe16-course-bench
Site:   learn.localhost
Frappe: v16.32.0
Apps:   frappe, training
Module: Training
```

Site должен открываться по:

```text
http://learn.localhost:8000
```

Developer Mode включён как инструмент учебного стенда.

`Request` ещё не создан.

---

# После блока A — главы 1–3

Стенд по сравнению с главой 0 **не изменён**.

Фактическое состояние:

```text
Bench:          ~/frappe/frappe16-course-bench
Frappe:         v16.32.0
Site:           learn.localhost
Apps in Bench:  frappe, training
Apps installed: frappe, training
Module:         Training
Developer Mode: включён
User:           Administrator
ERPNext:        отсутствует
Request:        ещё не создан
```

Новых бизнес-объектов, Documents, ролей, Workspaces и настроек блок A не создаёт.

Ученик уже руками проверил:

```text
apps/ и sites/ — соседние части Bench
training существует как код App и установлен на learn.localhost
Module Training зафиксирован в apps/training/training/modules.txt
User — системный DocType
Administrator — конкретный Document User
Desk / Sidebar / Desktop / Workspace
List View и Form View
границу между чистым Framework и отдельными Apps
```

Контролируемые ошибки блока A не меняют состояние стенда:

```text
несуществующий Site
несуществующий Desk route
попытка install-app erpnext при отсутствии кода erpnext в Bench
```

После восстановления должны по-прежнему открываться Desk и `User`, а команда:

```bash
bench --site learn.localhost list-apps
```

должна показывать `frappe` и `training`.

Это точное входное состояние блока B: **первый собственный DocType `Request` создаётся только в лабораторной 04**.

---

# После блока B — главы 4–10

Блок B впервые создаёт и затем последовательно расширяет собственную модель данных курса.

## `Request`

Standard DocType:

```text
Name:        Request
Module:      Training
Title Field: subject
Auto Name:   REQ-.YYYY.-.#####
```

Поля:

```text
Subject
  subject
  Data
  Mandatory

Description
  description
  Small Text

Status
  status
  Select: Open / In Progress / Done
  In List View

Due Date
  due_date
  Date
  In List View

Priority
  priority
  Select: Low / Medium / High
  Default: Medium
  In List View

Is Urgent
  is_urgent
  Check

Estimate Hours
  estimate_hours
  Int

Notes
  notes
  Text Editor

Reference File
  reference_file
  Attach

Responsible
  responsible
  Link → User

Responsible Name
  responsible_name
  Data
  Read Only
  Fetch From: responsible.full_name

Items
  items
  Table → Request Item

Watchers
  watchers
  Table MultiSelect → Request Watcher
```

Итоговая metadata не должна содержать временные поля лабораторной 07:

```text
reference_type
reference_name
```

Они создавались только для опыта Dynamic Link и затем удалены.

Есть несколько Request Documents:

```text
часть создана до настройки Auto Name и сохраняет исходные names
часть имеет names серии REQ-2026-.....
```

Минимум один Request содержит:

```text
Responsible = Administrator
4 строки Items
Watchers = Administrator, Guest
```

## `Request Item`

Standard Child DocType:

```text
Request Item
Is Child Table: 1
```

Поля:

```text
title   Data      Mandatory
qty     Float     Default 1
rate    Currency
amount  Currency
```

Он используется только через:

```text
Request.items
```

## `Request Watcher`

Standard Child DocType:

```text
Request Watcher
Is Child Table: 1
```

Поле:

```text
user  Link → User  Mandatory
```

Он используется через:

```text
Request.watchers
```

как backing Child DocType для `Table MultiSelect`.

## `Training Settings`

Standard Single DocType:

```text
Is Single: 1
```

Поля и сохранённые значения:

```text
Default Priority  default_priority  Select Low/Medium/High = Medium
Course Note       course_note       Small Text = Block B settings
```

Это одна форма настроек Site, а не список множества Documents.

## `Training Category`

Standard Tree DocType:

```text
Is Tree:     1
Auto Name:   field:category_name
Title Field: category_name
```

Основное поле:

```text
Category Name  category_name  Data  Mandatory
```

Tree-служебные поля добавлены Framework, включая:

```text
parent_training_category
is_group
lft
rgt
old_parent
```

Итоговая иерархия после эксперимента:

```text
Operations
└── Internal

Analytics
└── External
```

То есть:

```text
Internal.parent_training_category = Operations
External.parent_training_category = Analytics
```

## `Approval Record`

Standard Submittable DocType:

```text
Is Submittable: 1
Auto Name:      APR-.YYYY.-.#####
Title Field:    subject
```

Поля:

```text
Subject
  subject
  Data
  Mandatory

Comment
  comment
  Small Text
  Allow on Submit = 0

Internal Note
  internal_note
  Small Text
  Allow on Submit = 1

Amended From
  amended_from
  Link → Approval Record
  добавлено Framework
```

На стенде оставлены минимум четыре смысловых состояния:

```text
1 Draft
1 Submitted
1 Cancelled
1 Amended Draft с заполненным amended_from
```

Ученик уже руками проверил:

```text
DocType vs Document
Standard DocType → metadata-файл App
DocField types и свойства
Mandatory / Default / Read Only / Hidden / In List View
name vs Title Field
Naming Series REQ-.YYYY.-.#####
Link → User
Fetch From
Dynamic Link как временный опыт
Child Table
Table MultiSelect
Single
Tree
Submittable
docstatus 0 / 1 / 2
Allow on Submit
Cancel
Amend / amended_from
границу Virtual DocType без преждевременного controller-кода
```

Контролируемые ошибки блока B после восстановления не оставляют сломанного состояния:

```text
пустой Mandatory Subject
временный Mandatory Due Date
невалидная naming series REQ-#####
несуществующий Link → User
пустой Mandatory Title в Request Item
запрещённый Custom Virtual DocType
попытка обычного редактирования Submitted поля без Allow on Submit
```

Это точное входное состояние блока C. Глава 11 получает уже существующий `Request` со всеми полями, которые нужны для построения Form View, включая:

```text
Subject
Priority
Status
Due Date
Responsible
Responsible Name
Description
Notes
Items
```

---

# После блока C — главы 11–16

Блок C не создаёт новую предметную модель. Он превращает накопленные Documents и metadata блока B в рабочий интерфейс Desk и добавляет один явный слой site customization.

## `Request` — итоговая Form View

Standard layout:

```text
Main
├── General
│   ├── Subject | Priority
│   ├── Status  | Due Date
│   └── Is Urgent
├── Responsibility
│   ├── Responsible | Responsible Name
│   └── Watchers
└── Urgent Details
    ├── Display Depends On: eval:doc.is_urgent
    └── Estimate Hours

Details
├── Description
│   ├── Description
│   └── Notes
├── Files
│   └── Reference File
└── Items
    └── Items
```

У `General` нет `Display Depends On`.

Экспериментальное условие лабораторной 16 полностью удалено:

```text
Request.due_date
Display Depends On: пусто
```

## List View metadata

Постоянно включено:

```text
Status
  In List View:   ✓
  In List Filter: ✓

Priority
  In List View:   ✓
  In List Filter: ✓

Due Date
  In List View:   ✓
```

## Фиксированный набор главы 12

На Site остаются шесть Requests:

```text
C12-Open-High-1
C12-Open-High-2
C12-Open-Medium
C12-Progress-High
C12-Progress-Low
C12-Done-High
```

Их канонические значения:

```text
C12-Open-High-1
  Status: Open
  Priority: High
  Due Date: 2026-09-01
  Responsible: Administrator
  Start Date: 2026-08-31
  End Date:   2026-09-01

C12-Open-High-2
  Status: Open
  Priority: High
  Due Date: 2026-09-05
  Responsible: Administrator
  Start Date: 2026-09-03
  End Date:   2026-09-05

C12-Open-Medium
  Status: Open
  Priority: Medium
  Due Date: 2026-09-03
  Responsible: Guest
  Start Date: 2026-09-02
  End Date:   2026-09-03

C12-Progress-High
  Status: In Progress
  Priority: High
  Due Date: 2026-09-02
  Responsible: Administrator
  Start Date: 2026-09-01
  End Date:   2026-09-02

C12-Progress-Low
  Status: In Progress
  Priority: Low
  Due Date: 2026-09-04
  Responsible: Guest
  Start Date: 2026-09-03
  End Date:   2026-09-04

C12-Done-High
  Status: Done
  Priority: High
  Due Date: 2026-09-06
  Responsible: Administrator
  Start Date: 2026-09-05
  End Date:   2026-09-06
```

## Calendar / Gantt fields

`Request` постоянно содержит:

```text
Start Date  start_date  Date
End Date    end_date    Date
```

DocType setting:

```text
Is Calendar and Gantt = ✓
```

Существует named Calendar View:

```text
Request Course Calendar
  Reference Document Type: Request
  Subject Field: subject
  Start Date Field: start_date
  End Date Field: end_date
  All Day: ✓
```

Standard calendar mapping для Calendar/Gantt существует в App:

```text
apps/training/training/training/doctype/request/request_calendar.js
```

Содержит mapping:

```text
start → start_date
end   → end_date
id    → name
title → subject
allDay → 1
```

## Kanban

Существует:

```text
Kanban Board: Request Status
Reference Document Type: Request
Field Name: status
```

Итоговые C12 Status после эксперимента восстановлены; в частности:

```text
C12-Open-Medium → Open
```

## Tree

`Training Category` после эксперимента восстановлен:

```text
Operations
└── Internal

Analytics
└── External
```

## Public Workspace `Training`

Существует и используется дальше курса.

Обязательные блоки:

```text
Shortcut: Requests
  DocType → Request
  View → List

Shortcut: Request Kanban
  DocType → Request
  View → Kanban
  Board → Request Status

Shortcut: Training Categories
  DocType → Training Category
  View → Tree

Quick List: Recent Requests
  DocType → Request

Number Card: Open Requests
  Type → Document Type
  Document Type → Request
  Function → Count
  Filter → status = Open
  Is Public → ✓

Dashboard Chart: Requests by Status
  Chart Type → Group By
  Document Type → Request
  Group By Based On → status
  Group By Type → Count
  Visual Type → Bar
  Is Public → ✓
```

## Site-level customization `Request`

Постоянно остаётся Custom Field:

```text
Name:       Request-custom_local_note
DocType:    Request
Fieldname:  custom_local_note
Field Type: Small Text
```

Минимум один Request содержит:

```text
custom_local_note = Local value from chapter 15
```

Постоянно остаётся Property Setter:

```text
Name:       Request-estimate_hours-description
Doc Type:   Request
Field Name: estimate_hours
Property:   description
Value:      Local customization from chapter 15
```

Временный Custom Field полностью удалён:

```text
Request-custom_ch15_required_test
```

Лабораторная 15 доказала через SHA-256 конкретного файла, что Customize Form не изменил:

```text
apps/training/training/training/doctype/request/request.json
```

между началом и концом самой лабораторной.

## Desk Page

В блоке C **не создано ни одного нового Page**.

Ученик только установил границу:

```text
один Document              → Form
много Documents            → List
статусы                     → Kanban
даты                        → Calendar
интервалы                   → Gantt
реальная иерархия           → Tree
рабочая стартовая страница  → Workspace
одна глобальная настройка   → Single Form
собственный сложный UI      → кандидат на Page
```

## Контролируемые ошибки блока C

После восстановления не оставляют сломанного состояния:

```text
General Section скрыта через ошибочный Display Depends On
→ условие полностью удалено

фильтр C12 + Done + Low даёт 0 строк
→ фильтры очищены

End Date временно создан как Data и недоступен Calendar View
→ Field Type исправлен на Date до заполнения данных

Number Card фильтруется по name = __NO_SUCH_REQUEST__ и показывает 0
→ фильтр заменён на status = Open

временный Mandatory Custom Field блокирует Save
→ Custom Field удалён

Due Date получает условие status == Done вместо обратного
→ условие исправлено, проверено и затем полностью очищено
```

Это точное входное состояние блока D. Глава 17 должна начинаться с уже готового интерфейса и модели `Request`, но **без учебных ролей и отдельных учебных Users**: они впервые создаются в блоке D.

---

# После блока D — главы 17–22

Есть:

```text
Roles:
Training User
Training Manager

Users:
student.user@example.test
student.manager@example.test

DocType:
Training Area

Areas:
North
South
```

В `Request` добавлены:

```text
Area → Training Area
Internal Cost → Permission Level 1
```

Рабочая модель доступа:

```text
Training User
→ работает с разрешёнными Request
→ ограничен User Permission по North
→ не видит Internal Cost

Training Manager
→ имеет расширенные права
→ видит Internal Cost
```

Есть один учебный пример Share.

---

# После блока E — главы 23–28

Есть минимум один активный Assignment/ToDo.

Assignment Rule проверен и может быть оставлен Disabled.

У `Request` работает Workflow:

```text
Draft
→ Review
→ Approved
→ Rejected
→ Reopen/Draft
```

Переходы разделены между `Training User` и `Training Manager`.

Notification проверена и может быть Disabled.

Auto Repeat проверен на отдельном учебном DocType и может быть Disabled.

---

# После блока F — главы 29–33

На одном Request есть:

```text
Comments
Timeline events
Version history
public File
private File
Communication
```

Для `Request` существует рабочий Print Format.

Email используется только через безопасную тестовую конфигурацию.

---

# После блока G — главы 34–38

В `Request` должно быть минимум 40–50 учебных Documents.

Есть:

```text
Report Builder report
Query Report
Script Report
Number Card
Dashboard Chart
```

Card/Chart размещены в Training Workspace.

Data Import проверен как для create, так и для update, включая обработку ошибочной строки.

---

# После блока H — главы 39–43

Есть:

```text
Web Form для Request
простая Training Portal page
REST CRUD опыт
training.api.ping_training whitelisted RPC method
training.api@example.test integration user
```

API key/secret не должны лежать в Git.

Guest creation в Web Form должен быть выключен, если он не нужен дальше.

---

# После главы 44

Есть Client Script Request, который демонстрирует минимум:

```text
conditional mandatory
show/hide
custom UI action
Child Table calculation
```

Ученик уже проверил через REST, что Client Script не является server-side validation.

---

# После главы 45

Server Scripts включены на учебном Bench.

Есть рабочая server-side validation:

```text
Request Status = Done
→ Result обязателен
```

Она проверена как минимум через:

```text
Desk
REST API
```

API Server Script и Scheduler Event проверены; после опыта их можно оставить `Disabled`.

---

# Правило восстановления

Если лабораторная ломает стенд сильнее, чем ожидается:

1. не продолжать следующую главу вслепую;
2. проверить последние изменённые metadata/permissions/scripts;
3. использовать Version/Git/backup-механизм, соответствующий уже изученному уровню;
4. вернуть состояние, описанное для предыдущего блока;
5. только после этого продолжать.

Курс специально допускает ошибки. Но каждая ошибка должна закончиться пониманием причины и восстановлением воспроизводимого состояния.
