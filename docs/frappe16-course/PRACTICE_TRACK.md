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
Is Tree:    1
Auto Name:  field:category_name
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

`Request` имеет аккуратную Form layout.

Есть:

```text
List data
Kanban по Status
Calendar по Due Date
при необходимости Start/End Date для Gantt
Training Category Tree
Training Workspace
custom_local_note через Customize Form
```

Ученик различает Standard metadata и site customization, но глубокий перенос ещё не изучает.

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