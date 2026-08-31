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

Блок D добавляет рабочую штатную permission model поверх уже существующего `Request`. Он не создаёт custom permission hooks и не требует будущего server-side кода.

## Roles

На Site существуют:

```text
Training User
  Desk Access: ✓
  Disabled:    ☐

Training Manager
  Desk Access: ✓
  Disabled:    ☐
```

## Учебные Users

```text
student.user@example.test
  Enabled:   ✓
  User Type: System User
  Roles:
    Training User

student.manager@example.test
  Enabled:   ✓
  User Type: System User
  Roles:
    Training User
    Training Manager
```

Для обоих задан рабочий пароль disposable локального стенда, и оба проверены входом через:

```text
http://learn.localhost:8000/app
```

Контролируемый переход `Training User Desk Access = 0` полностью восстановлен; оба Users финально снова System User.

## `Request` — новые Standard fields

В metadata App постоянно добавлены:

```text
Internal Cost
  internal_cost
  Currency
  Perm Level: 1

Area
  area
  Link → Training Area
  Ignore User Permissions: ☐
```

`Area` размещена в `Main → General` после `Due Date`.

`Internal Cost` размещён в `Details` после `Notes`.

То есть `request.json` изменился из-за собственных Standard DocFields глав 19–20, но **не** из-за Role Permissions Manager.

## `Request` Role Permissions

Runtime rules настроены через Role Permissions Manager и живут как site-level `Custom DocPerm`.

Level 0:

```text
Training User
  Read:    ✓
  Write:   ✓
  Create:  ✓
  Delete:  ☐
  Share:   ☐
  Only if Creator: ☐

Training Manager
  Read:    ✓
  Write:   ✓
  Create:  ✓
  Delete:  ✓
  Share:   ✓
  Only if Creator: ☐
```

Для этих учебных rows ненужные permissions оставлены выключенными:

```text
Select
Print
Email
Report
Import
Export
Mask
```

Level 1:

```text
Training User
  rule отсутствует

Training Manager
  Read:  ✓
  Write: ✓
  Mask:  ☐
```

Временная Level 1 row Training User полностью удалена.

## `Training Area`

Standard DocType:

```text
Name:        Training Area
Module:      Training
Auto Name:   field:area_name
Title Field: area_name
```

Поле:

```text
Area Name
  area_name
  Data
  Mandatory
```

Documents:

```text
North
South
```

Role Permissions Manager:

```text
Training User
→ Training Area Level 0: Read only

Training Manager
→ Training Area Level 0: Read only
```

## User Permission

Для обычного User существует ровно одна учебная Area permission:

```text
User:      student.user@example.test
Allow:     Training Area
For Value: North
Is Default: ✓
Apply To All Document Types: ✓
```

У:

```text
student.manager@example.test
```

User Permission `Training Area` отсутствует.

Глобальный strict-mode ради курса не переключался.

## Фиксированное распределение C12 по Area

```text
North:
  C12-Open-High-1
  C12-Open-Medium
  C12-Progress-High

South:
  C12-Open-High-2
  C12-Progress-Low
  C12-Done-High
```

Поэтому при обычной финальной модели:

```text
student.user@example.test
Subject Like C12-%
→ 3 Documents

student.manager@example.test
Subject Like C12-%
→ 6 Documents
```

`Request.area Ignore User Permissions` после эксперимента снова выключен.

## D18 Documents и owner

Постоянно существуют:

```text
D18-User-Record
  owner:         student.user@example.test
  Area:          North
  Internal Cost: 101

D18-Manager-Record
  owner:         student.manager@example.test
  Area:          North
  Internal Cost: 202
```

Временный:

```text
D18-User-Delete-Probe
```

удалён менеджером в лабораторной 18.

`Only if Creator` проверен на этих двух North-документах и финально снова:

```text
Training User
Only if Creator = ☐
```

То есть owner **не является постоянным ограничением** финального Training User.

## Shared South Request

Постоянно существует:

```text
D21-Shared-South
  owner:         student.manager@example.test
  Area:          South
  Notes:         Read-only shared example
  Internal Cost: 404
```

Для него существует `DocShare`:

```text
User:  student.user@example.test
Read:  ✓
Write: ☐
```

Обычный User получает этот South Request как явное read-only исключение своей `Training Area = North` User Permission.

Временный Share Write полностью снят.

`Internal Cost` через Share обычному User не раскрывается, потому что у него нет Level 1 permission.

Ещё один контрольный South Document:

```text
C12-Open-High-2
  Area:          South
  Internal Cost: 303
  Share:         отсутствует
```

поэтому обычному User финально недоступен.

## Итоговая контрольная матрица Training User

```text
D18-User-Record
  North
  свой owner
  no Share
  Read:  да
  Write: да
  Internal Cost: нет

D18-Manager-Record
  North
  чужой owner
  no Share
  Read:  да
  Write: да
  Internal Cost: нет

C12-Open-High-2
  South
  no Share
  Read:  нет
  Write: нет

D21-Shared-South
  South
  Read Share
  Read:  да
  Write: нет
  Internal Cost: нет
```

Training Manager видит и редактирует все четыре контрольных Request и имеет доступ к `Internal Cost`.

## Sharing settings

Глобально оставлено:

```text
Disable Document Sharing = ☐
```

Это нужно сохранить и для следующего блока, где Assignment может использовать Share как вспомогательный механизм доступа.

## Что ученик уже проверил руками

```text
User vs Role
System User vs Website User
Role Desk Access
реальный вход двух ограниченных Users
Role Permissions Manager
Read / Create / Write / Delete / Share
additive permissions нескольких Roles
Custom DocPerm vs Standard request.json
Permission Level 0 vs 1
field-level Read / Write
User Permission по Link
Is Default
Apply To All Document Types
Ignore User Permissions
owner vs Responsible
Only if Creator
DocShare Read / Write
Share как исключение User Permission/owner restrictions
Permission Level поверх Share
List access vs direct Document access
```

## Контролируемые ошибки блока D

Все восстановлены:

```text
Training User Desk Access снят
→ student.user становится Website User
→ Desk Access возвращён, User снова System User

Training User Write снят
→ существующий Request read-only
→ Write возвращён

Training User получает Level 1 Read, затем лишний Write
→ Internal Cost временно раскрывается и редактируется
→ значение восстановлено, Training User Level 1 row удалена

Request.area Ignore User Permissions = ✓
→ C12-доступ Training User расширяется 3 → 6
→ Ignore User Permissions возвращён в ☐

Training User Only if Creator = ✓
→ чужой North Request исчезает
→ owner restriction возвращён в ☐

D21-Shared-South получает временный Share Write
→ обычный User меняет Notes
→ Notes восстановлены, Share снова Read only

Training User Read временно снят в финальной диагностике
→ обычные Request исчезают, shared Request остаётся
→ Read возвращён
```

## Граница к custom permission code

На стенде после блока D **не создано**:

```text
permission_query_conditions hook
custom has_permission hook
Permission Query Server Script
```

Ученик знает эти extension points только как будущую границу, когда штатной permission model действительно недостаточно.

## Handoff в блок E

До начала главы 23:

```text
оба учебных User Enabled и System User
оба могут войти в /app
Training User имеет рабочий доступ к North Request
Training Manager имеет расширенный доступ
Sharing включён
существует один read-only Share-пример
Assignment / ToDo блок D ещё не создаёт как обязательное состояние
```

Это точное входное состояние главы 23: Assignment впервые изучается уже в блоке E.

---

# После блока E — главы 23–28

Блок E добавляет штатные механизмы выполнения работы и автоматизации поверх permission model блока D. Собственный scheduler code, Server Script и custom Workflow code в блоке E не создаются.

## Ручной Assignment и `ToDo`

Постоянно существует:

```text
E23-Assignment-Manual
  owner:       student.manager@example.test
  Status:      Open
  Priority:    Medium
  Area:        North
  Responsible: пусто
  Notes:       Manual assignment example
```

Его активный Assignment хранится как отдельный `ToDo`:

```text
Allocated To:   student.user@example.test
Reference Type: Request
Reference Name: <name E23-Assignment-Manual>
Status:         Open
Priority:       Medium
Due Date:       2026-09-02
Assigned By:    student.manager@example.test
```

Временный второй Assignment менеджера снят и остаётся только как исторический:

```text
Allocated To: student.manager@example.test
Status:       Cancelled
```

Проверено руками:

```text
Assign → создаёт ToDo
owner не меняется
Responsible не создаёт ToDo
один Request может иметь несколько Assignment
Remove Assignment → ToDo.Cancelled
```

## `Training Request Round Robin`

Assignment Rule существует, но финально отключён:

```text
Name:            Training Request Round Robin
Document Type:   Request
Priority:        10
Assign Condition: status == "Open"
Rule:            Round Robin
Assignment Days: Monday–Sunday
Users:
  1. student.user@example.test
  2. student.manager@example.test
Disabled:        ✓
```

Проверенная последовательность:

```text
E24-RR-1 → student.user@example.test
E24-RR-2 → student.manager@example.test
E24-RR-3 → student.user@example.test
E24-RR-4 → student.manager@example.test
```

Дополнительно:

```text
E24-NoMatch
  Status: Done
  → Assignment отсутствует

E24-Recovered
  Status: Open
  Area: North
  → Assignment = student.user@example.test
```

После recovery финальное поле правила:

```text
Last User = student.user@example.test
```

Для E24-RR-1..4 и E24-Recovered созданные Assignment остаются обычными Open ToDo.

Временный `E24-Permission-Failure` не является сохранённым рабочим Request: попытка была отклонена и восстановлена до продолжения курса.

Глобально восстановлено:

```text
Disable Document Sharing = ☐
```

## Обычный `Status`

Постоянно существует контрольный Request:

```text
E25-Status-Only
  owner:    student.user@example.test
  Status:   Open
  Area:     North
  Due Date: 2026-09-05
  Notes:    Status is still a plain Select
```

На нём доказано, что без Workflow обычный Select позволял прямые переходы:

```text
Open → In Progress → Done
Open → Done
```

После опыта `Status` восстановлен в `Open`.

## `Training Request Workflow`

Для `Request` существует один активный Workflow:

```text
Workflow Name:        Training Request Workflow
Document Type:        Request
Is Active:            ✓
Workflow State Field: workflow_state
Send Email Alert:     ☐
```

Workflow States:

```text
Draft
Review
Approved
Rejected
```

Все четыре состояния имеют:

```text
Doc Status = 0
```

и поэтому `Request.docstatus` в этом процессе остаётся Draft-level системным состоянием.

`Document States`:

```text
Draft
  Only Allow Edit For: Training User

Review
  Only Allow Edit For: Training Manager

Approved
  Only Allow Edit For: Training Manager

Rejected
  Only Allow Edit For: Training User
```

Transitions:

```text
Draft
  --Send for Review--> Review
  Allowed: Training User
  Condition: doc.due_date

Review
  --Approve--> Approved
  Allowed: Training Manager

Review
  --Reject--> Rejected
  Allowed: Training Manager

Rejected
  --Reopen--> Draft
  Allowed: Training User
```

`Allow Self Approval` оставлен включённым для учебных переходов.

Workflow автоматически создал site-level Custom Field:

```text
Workflow State
  fieldname: workflow_state
  Link → Workflow State
  Hidden: ✓
  Allow on Submit: ✓
  No Copy: ✓
```

Поле не добавлялось вручную в Standard `request.json`.

При активации Workflow существующие `Request` с пустым `workflow_state` и `docstatus = 0` получили первое состояние:

```text
Draft
```

если затем не были переведены отдельными Workflow Actions.

Контрольные документы:

```text
E26-Approved
  Status: Done
  Workflow State: Approved
  Area: North
  Due Date: 2026-09-05

E26-Reject-Reopen
  Status: Open
  Workflow State: Draft
  Area: North
  Due Date: 2026-09-06
```

На `E26-Approved` доказано:

```text
Request.status = Done
workflow_state = Approved
```

могут существовать одновременно и означают разные вещи.

## `Training Review Notification`

Notification rule существует, но финально отключён:

```text
Name:          Training Review Notification
Enabled:       ☐
Channel:       System Notification
Document Type: Request
Send Alert On: Value Change
Value Changed: workflow_state
Condition Type: Python
Condition:     doc.workflow_state == "Review"
Receiver By Role: Training Manager
Notification Type: Alert
Notification Title: Request {{ doc.name }} ждёт проверки
Notification Message: {{ doc.subject }}
```

Есть доказанный `Notification Log` для:

```text
E27-Notify-Review
For User = student.manager@example.test
Document Type = Request
Document Name = <name E27-Notify-Review>
```

Контрольные Request после проверки:

```text
E27-Notify-Review
  Workflow State: Approved

E27-Notify-NoHit
  Workflow State: Approved
```

На втором документе проверено, что временное ложное Condition не создаёт Notification Log при переходе в Review.

SMTP и внешний email для этого опыта не использовались.

## `Recurring Note`

Standard DocType:

```text
Name:              Recurring Note
Module:            Training
Allow Auto Repeat: ✓
Auto Name:         RN-.YYYY.-.#####
Title Field:       title
```

Поля:

```text
Title
  title
  Data
  Mandatory

Run Date
  run_date
  Date
  Mandatory
```

Существуют два Documents с одинаковым Title:

```text
Monthly Check Template
```

но разными `Run Date`:

```text
reference: 2026-08-30
generated: 2026-08-31
```

У generated document отдельный system name. На чистом стенде курса это первые два names серии `RN-2026-.....`.

## Auto Repeat

Существует один проверенный Auto Repeat. На чистом стенде курса это:

```text
AUT-AR-00001
```

Финальное состояние:

```text
Reference Document Type: Recurring Note
Reference Document:      <reference Monthly Check Template>
Start Date:              2026-08-31
Frequency:               Daily
End Date:                пусто
Disabled:                ✓
Status:                  Disabled
Next Schedule Date:      пусто
```

В лабораторной штатная функция v16 была выполнена один раз через:

```text
bench --site learn.localhost execute
```

когда `Next Schedule Date = 2026-08-31`.

Она реально создала второй `Recurring Note`, после чего расписание перед отключением сдвинулось на:

```text
2026-09-01
```

Отдельно проверено:

```text
Weekly от Start Date 2026-08-30
→ Next Schedule Date = 2026-09-06
```

После эксперимента Frequency восстановлен в Daily и Auto Repeat отключён, поэтому следующие главы не создают новые Recurring Note сами.

## Контролируемые ошибки блока E

Все восстановлены:

```text
Responsible временно используется как будто это Assignment
→ новый ToDo не появляется
→ Responsible очищен, настоящий Assignment остаётся

Disable Document Sharing = ✓ + следующий Round Robin assignee не имеет доступа к South
→ Missing Permission
→ Sharing возвращён в ☐, контрольное назначение успешно

обычный Status делает прямой Open → Done
→ доказано отсутствие transition graph у Select
→ Status восстановлен в Open

Send for Review при пустом Due Date
→ действие отсутствует из-за doc.due_date
→ Due Date заполнена, переход проходит

Training User пытается получить Approve/Reject
→ действий нет из-за Allowed Role
→ менеджер выполняет переходы штатно

Notification Condition с одним =
→ правило не сохраняется
→ Condition исправлен на ==

Notification Condition временно требует Approved
→ переход в Review не создаёт ожидаемый log
→ Condition восстановлен на Review

Auto Repeat End Date = 2026-08-31
→ End Date cannot be today
→ End Date очищен
```

## Handoff в блок F

До начала главы 29:

```text
permission model блока D восстановлена
Sharing включён
есть реальные ToDo и Assignment history
Assignment Rule существует, но Disabled
Training Request Workflow Active
есть Workflow transitions и Workflow timeline events
Training Review Notification существует, но Disabled
есть Notification Log
Recurring Note и один generated Auto Repeat document существуют
Auto Repeat Disabled
```

Следующий блок может изучать Timeline на уже накопленных реальных событиях, не создавая заново инфраструктуру блока E.

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