# Инварианты учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Этот документ задаёт формальную модель гарантий: что гарантируется, каким механизмом и с какого этапа курса.

Главное правило:

```text
не называть hard/security invariant то,
что Frappe обеспечивает только UI,
site policy или дисциплиной пользователя
```

---

# 1. Уровни силы

## H — hard / server-enforced

Примеры:

```text
Mandatory
Role Permission
Workflow Allowed Role / Condition
Login Required против Guest
Web Form Allow Edit = No против update
```

## S — structural

Следует из metadata/source и архитектуры.

## U — UI/process guard

Помогает работать правильно, но не является самостоятельной server ACL.

## P — deployment/process policy

Зависит от конфигурации site или обязательного rollback.

## C — conditional invariant

Действует только при указанном предусловии.

---

# 2. Фазы

```text
L0–L3  → платформа и справочники
L4–L6  → ручной рабочий документ
L7+     → Workflow
L9+     → main-site automation
L10+    → authenticated Web Form intake
L11     → portable app + deployment split
Labs    → временные mutations с rollback
```

---

# 3. Структура

## S-01. Постоянное domain core

```text
Facility Location
Equipment
Service Request
```

## S-02. Один state field

```text
Service Request.status
```

После L7 это же поле — Workflow State Field.

Не создаются `workflow_state`, `request_state` и аналоги.

## S-03. Assignment не дублируется полем

```text
Service Request
→ Assign To
→ ToDo
→ User
```

Нет собственного `Assigned Technician`.

## S-04. Assignment не authorization

```text
Permission ≠ Assignment
```

ToDo показывает ответственность, Role Permission — базовый доступ.

Assignee-only authorization — Later.

---

# 4. Data invariants

## H-01. Mandatory Service Request

```text
Subject
Location
Description
Priority
```

Обязательность действует для Desk, Web Form, Auto Repeat, automation tests, clean-site acceptance и Labs.

## H-02. Equipment Optional

`Service Request.equipment` не Mandatory.

## H-03. Priority

```text
Low
Medium
High
```

Default `Medium`.

## H-04. Status

```text
New
Accepted
In Progress
Resolved
Closed
```

`Accepted` = Supervisor принял заявку в процесс.

```text
Accepted ≠ Assigned To
```

## H-05. Equipment Category

```text
HVAC
Electrical
IT
Other
```

## S-05. Temporal semantics Location

```text
Service Request.location
= историческое место события

Equipment.location
= текущее размещение Equipment
```

Вечного hard equality между ними нет.

---

# 5. Permission invariants

## H-06. Финальная Role Permission matrix Service Request

```text
Requester
→ Create Yes
→ Read own Yes / If Owner
→ Write No
→ Delete No

Technician
→ Read/Write Yes
→ Create/Delete No

Supervisor
→ Read/Write/Create Yes
→ Delete No
→ Report/Export Yes
```

Requester intake через Desk становится append-only после insert.

## H-06A. If Owner не блокирует Create

Exact `v16.32.0` не переносит `create` в owner-only restriction.

Поэтому совместимы:

```text
Create Yes
Read own Yes
Write No
If Owner Yes
```

## H-06B. Рабочие роли не удаляют Service Request

У Requester/Technician/Supervisor:

```text
Delete = No
```

Delete изучается только temporary experiment L5 и откатывается.

## P-01. L5 permission experiments очищаются

До выхода из L5:

```text
temporary Share deleted
User Permission deleted
technician.restricted disabled
Supervisor Delete returned to No
```

## H-07/P-02. Assignment не должен скрыто раздавать доступ

`Assign To` может auto-Share document пользователю без access; при disabled sharing может получить Missing Permission.

Поэтому основные Technician имеют совместимый Role-based access до Round Robin.

## U-01. Only Allow Edit For — Desk guard

```text
Role Permission
= server access

Workflow Allowed Role / Condition
= server transition gate

Only Allow Edit For
= Desk state editability
```

## U-02. Status Read Only — UI guard

После L7 `status` Read Only в Desk; server transition validity обеспечивает Workflow.

---

# 6. Process invariants

## H-08. Workflow

```text
New
 ↓ Accept / Facility Supervisor
Accepted
 ↓ Start Work / Facility Technician
In Progress
 ↓ Resolve / Facility Technician
Resolved
 ↓ Close / Facility Supervisor
Closed
```

Все states `docstatus = 0`.

## U-03. Desk edit roles

| State | Only Allow Edit For |
|---|---|
| New | Facility Supervisor |
| Accepted | Facility Technician |
| In Progress | Facility Technician |
| Resolved | Facility Supervisor |
| Closed | Facility Supervisor |

Requester всё ещё может создать новый local Document: client Workflow не делает `doc.__islocal` read-only; после insert настоящий server invariant — `Requester Write = No`.

## H-09. Allowed Role / Condition управляют transition

State change должен соответствовать доступному transition текущего пользователя.

## S-06. Accepted не доказывает assignment

Нормально:

```text
Assigned To заполнен
Status = New
```

Технически возможно:

```text
Status = Accepted
Assigned To пусто
```

Рекомендуется `Assign To → Accept`, но это не hard coupling.

## S-07. Technician role ≠ конкретный assignee

Workflow transition разрешается роли, а не конкретному ToDo assignee.

## S-08. Closed terminal, но не absolute immutable

У Closed нет исходящего Workflow transition, и рабочие роли не имеют Delete.

Абсолютная immutability всех полей через любой API требует отдельной server validation — Later.

---

# 7. Automation invariants

## P-03. Assignment Rule site-specific

`Service Request Auto Assignment` содержит concrete Users и не является universal fixture.

## H-10. Assignment Rule не двигает Workflow

После auto assignment:

```text
Assigned To = Technician
Status = New
```

## C-01. Target Date conditional

Если Target Date задан:

```text
ToDo.date может следовать Target Date
One Day Overdue может сработать +1 day
```

Если пуст — этих гарантий нет.

## P-04. Load Balancing rollback

После optional test финал:

```text
Rule = Round Robin
```

---

# 8. Web Form invariants

## H-11. Login Required — authentication boundary

Финал:

```text
Login Required = Yes
Anonymous Responses = No
```

Это гарантирует:

```text
Guest submit запрещён
```

Но не означает role-specific authorization.

## H/S-11A. Web Form insert — отдельный create capability

Exact `v16.32.0` для нового Web Form Document вызывает:

```text
doc.insert(ignore_permissions=True, ...)
```

Следовательно:

```text
Web Form submit
≠ Role Permission Create check
```

Desk Requester Create и Web Form create — два разных admission path.

`Apply Document Permissions` не превращает Web Form insert в обычный Role Permission Create.

## H-12. Финальная Web Form create/read-only

```text
Allow Editing After Submit = No
```

Owner-based update при разрешённом edit может использовать `doc.save(ignore_permissions=True)`, поэтому edit изучается и обязательно выключается.

## H-13. Web Form не управляет Workflow

`Status` отсутствует в Web Form fields; новый Document получает default `New`.

## H/S-14. Apply Document Permissions относится к existing-document access

```text
Apply Document Permissions = Off
→ Web Form owner/website permission path

Apply Document Permissions = On
→ ordinary document permission path для существующего Document
```

Не использовать эту настройку как доказательство create authorization.

## P-05. Authenticated Web Form population — deployment trust decision

Финальная форма не содержит отдельного role gate `Facility Requester only`.

Поэтому курс принимает policy:

```text
website accounts, которым deployment разрешает доступ к published authenticated form,
= trusted internal reporters
```

Role-restricted/public-untrusted portal intake — Later.

## P-06. Link catalog disclosure — trust decision

`Allow Read On All Link Options = Yes` сознательно раскрывает authenticated reporters названия Location/Equipment options.

---

# 9. Packaging invariants

## S-09. Четыре слоя

```text
Standard source
universal app configuration
site-specific configuration
working data
```

## S-10. Universal delivery

```text
3 core DocType
Reports/Cards/Chart/Workspace
Notifications
Web Form
Roles
Workflow States/Actions/Workflow
Custom DocPerm
```

## P-07. Site-specific не fixture

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

## H-15. install-app — initial installation

`install_app()` v16.32.0 синхронизирует source, fixtures, customizations и dashboards.

Последующий migrate — convergence/update test.

## S-11. Portability scope

L11 доказывает clean-site portability, не arbitrary multi-app compatibility.

## P-08. После L11 active site возвращается main

```text
bench use facility-ops.localhost
```

---

# 10. Lab invariants

## P-09. Lab rollback contract

Каждая Lab фиксирует Temporary / Persistent / Rollback / Final State.

## S-12. Domain rollback ≠ source rollback

Например Lab E оставляет Standard Print Format как presentation configuration, не расширяя domain core.

---

# 11. Compatibility matrix

| Механизмы | Совместимость | Условие |
|---|---|---|
| Mandatory ↔ Web Form | жёсткая | Web Form сохраняет H-01 |
| Requester Desk Create ↔ post-create no-Write | жёсткая | Create Yes + Read own + Write No |
| Requester ↔ Workflow New | совместимы | local doc editable; saved doc Write No |
| Desk Create ↔ Web Form Create | разные пути | не считать Web Form proof Role Create |
| Login Required ↔ role authorization | не эквивалентны | login = authentication only |
| Apply Document Permissions ↔ Web Form insert | не эквивалентны | setting относится к existing-doc path |
| Role Permission ↔ Workflow | совместимы | access ≠ transitions |
| Only Allow Edit For ↔ security | не эквивалентны | UI guard, не ACL |
| Assignment ↔ Workflow | ортогональны | assignment не кодирует status |
| Assignment ↔ authorization | не эквивалентны | assignee не permission predicate |
| User Permission ↔ Round Robin | опасно без cleanup | main Technician без Location restriction |
| Target Date ↔ Due Date | условно | только при Target Date |
| Workflow ↔ Web Form edit | небезопасно | final Allow Edit = No |
| Workflow ↔ Kanban | допустимо для обучения | после L7 Kanban удалить |
| Standard source ↔ fixtures | совместимы | fixtures не дублируют Standard DocType |
| Main site ↔ clean site | намеренно различаются | Assignment Rule site-specific |
| Labs ↔ core domain | совместимы | обязательный rollback |

---

# 12. State contract урока

Каждый execution-аудит использует:

```text
PRECONDITIONS
TEMPORARY MUTATIONS
PERSISTENT MUTATIONS
ROLLBACK
OUTPUT STATE
GIT STATE
```

Критерий:

```text
OUTPUT(Ln) ⊇ PRECONDITIONS(Ln+1)
```

---

# 13. Что base course сознательно не обещает

```text
assignee-only authorization
absolute Closed immutability через любой API
вечное equality Equipment.location и Request.location
role-specific Web Form submission authorization
safe public-untrusted Web Form catalog
arbitrary multi-app co-installation
```

Для этого нужен отдельный server-side/portal architecture layer.

Базовая архитектура должна быть честно ограниченной, а не псевдобезопасной.
