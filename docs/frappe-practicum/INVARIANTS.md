# Инварианты учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Главное правило:

```text
каждая заявленная гарантия
должна иметь названный enforcement layer
```

---

# 1. Уровни силы

## H — hard / server-enforced

Сервер Frappe проверяет или нормализует операцию штатным permissions/validation/workflow.

## S — structural

Следует из metadata/source и модели.

## U — UI/process guard

Помогает стандартному UX, но не является отдельной server ACL.

## P — deployment/process policy

Зависит от конфигурации site или обязательного rollback.

## C — conditional

Действует только при выполнении предусловия.

---

# 2. Core structure

## S-01. Domain core

```text
Facility Location
Equipment
Service Request
```

## S-02. Единственный process state

```text
Service Request.status
```

После L7 это же поле — Workflow State Field.

Параллельный `workflow_state` не создаётся.

## S-03. Assignment не дублируется business field

```text
Service Request → Assign To → ToDo → User
```

## S-04. Assignment ≠ authorization

ToDo = responsibility.

Permissions = authority.

Assignee-only authorization — Later.

---

# 3. Data invariants

## H-01. Mandatory

```text
Subject
Location
Description
Priority
```

## H-02. Equipment Optional

`equipment` не Mandatory.

## H-03. Priority

```text
Low
Medium
High
```

## H-04. Status values

```text
New
Accepted
In Progress
Resolved
Closed
```

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

## S-05. Location semantics

```text
Service Request.location = historical event location
Equipment.location       = current equipment location
```

Вечного equality нет.

---

# 4. Трёхуровневая permission architecture

После L5 `Service Request` разделён на три permission layer.

```text
Permission Level 0
→ document authority

Permission Level 1
→ business content authority

Permission Level 2
→ process-state field authority
```

Workflow после L7 добавляет четвёртый слой:

```text
Workflow Allowed Role / Condition
→ transition authority
```

---

# 5. Level 0 — document authority

## H-06. Final Level 0 matrix

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

Requester Desk intake = append-only after insert.

## H-06A. If Owner не блокирует Create

Exact `v16.32.0` owner-only folding не применяется к `create`.

## H-06B. Working roles no-delete

`Service Request Delete = No` у всех трёх рабочих ролей после temporary L5 experiment.

---

# 6. Level 1 — business content authority

## S/H-07. Business content = Permission Level 1

```text
subject
location
equipment
description
priority
target_date
attachment
```

имеют:

```text
Permission Level = 1
```

## H-07A. Level 1 matrix

```text
Requester
→ Read Yes / Write Yes

Technician
→ Read Yes / Write No

Supervisor
→ Read Yes / Write Yes
```

## H-07B. Почему Requester Level 1 Write безопасен

Client `perm.js` для local Document проверяет `write` именно на `df.permlevel`.

Поэтому Requester может заполнить Level 1 intake fields нового Document.

Server insert при этом проверяет:

```text
Create
```

После insert:

```text
Level 0 Write = No
```

блокирует повторный ordinary save целиком.

## H-07C. Technician document Write ≠ content Write

Exact `Document.insert()` / `_save()` вызывают:

```text
validate_higher_perm_levels()
```

Если у пользователя нет write конкретного high Permission Level, Frappe сбрасывает такие значения к разрешённым original/default перед DB write.

Следовательно ordinary permission-aware save Technician не должен сохранять изменения Level 1 content.

---

# 7. Level 2 — process-state authority

## S/H-08. Status = Permission Level 2

После L5:

```text
Service Request.status
→ Permission Level = 2
```

Level 2 matrix:

```text
Requester
→ Read Yes / Write No

Technician
→ Read Yes / Write Yes

Supervisor
→ Read Yes / Write Yes
```

Это разделяет:

```text
business content
≠ process state
```

## H-08A. Requester не задаёт произвольный state на insert

Requester не имеет Level 2 Write.

На ordinary permission-aware insert high-permlevel validation нормализует недоступное Level 2 field к разрешённому default/original значению.

Для нового `Service Request`:

```text
status default = New
```

Поэтому даже **до L7** Requester не получает штатного права выбрать `Accepted / In Progress / Resolved / Closed`.

Это сильнее модели, где `status` оставался Level 0.

## H-08B. Technician/Supervisor могут менять state до Workflow

В L5–L6 Technician и Supervisor имеют Level 2 Write, поэтому до Workflow `status` остаётся обычным Select для этих ролей.

Это позволяет доказать:

```text
Select values
≠ state machine
```

не раздавая state write Requester.

## H-08C. Workflow совместим с Level 2

После L7 Technician/Supervisor сохраняют Level 2 Write, необходимый для своих state changes.

Но теперь допустимость перехода дополнительно проверяет Workflow.

```text
Level 2 Write
= право изменять process-state field

Workflow transition
= право выполнить конкретный переход
```

Оба условия нужны одновременно.

---

# 8. Ограничение Permission Level

`ignore_permissions=True` отключает high-permlevel enforcement.

Поэтому Level 1/2 guarantees формулируются для:

```text
permission-aware Document insert/save
```

а не для доверенного server code, который сознательно bypass permissions.

Это одна из причин, почему final Web Form update выключен.

---

# 9. Temporary permission experiments

## P-01. L5 cleanup

До выхода из L5:

```text
Supervisor Delete = No
Share removed
User Permission removed
technician.restricted disabled
```

## H/P-02. Assignment не раздаёт скрытые permissions

Основные Technician имеют совместимый Role-based document access, чтобы Assign To не создавал неожиданные DocShare exceptions.

Assignment не меняет Level 1/2 matrices.

---

# 10. UI guards

## U-01. Only Allow Edit For ≠ ACL

```text
Level 0 Role Permission
= document authority

Permission Level 1
= business-content authority

Permission Level 2
= process-state field authority

Workflow Allowed Role / Condition
= transition authority

Only Allow Edit For
= Desk state editability
```

## U-02. Status Read Only после L7

После Workflow:

```text
status → Read Only = Yes
```

Это UI guard. Server state validity проверяет Workflow.

---

# 11. Workflow invariants

## H-09. State machine

```text
New
 ↓ Accept / Supervisor
Accepted
 ↓ Start Work / Technician
In Progress
 ↓ Resolve / Technician
Resolved
 ↓ Close / Supervisor
Closed
```

Все states `docstatus = 0`.

## U-03. Desk edit roles

```text
New         → Supervisor
Accepted    → Technician
In Progress → Technician
Resolved    → Supervisor
Closed      → Supervisor
```

Requester local create остаётся возможным, потому что intake fields находятся на Level 1, а status получает default New на Level 2.

## H-09A. Allowed Role / Condition

Workflow state change должен соответствовать допустимому transition текущего пользователя.

## S-06. Accepted не доказывает assignment

`Assign To → Accept` — рекомендуемый порядок, не hard coupling.

## S-07. Technician role ≠ конкретный assignee

Workflow transition разрешается роли, а не ToDo assignee.

## S-08. Closed terminal, не absolute immutable

Нет исходящего transition; working roles no-delete.

Absolute API immutability — Later.

---

# 12. Automation invariants

## P-03. Assignment Rule site-specific

Rule с concrete Users не universal fixture.

## H-10. Assignment Rule не меняет Workflow state

```text
Assigned To = Technician
Status = New
```

## H/S-10A. Automation не расширяет authority

Assignment Rule, Auto Repeat Assignee и ToDo не выдают Technician:

```text
Level 1 Write
или дополнительные Level 2 transitions
```

`Target Date` остаётся Level 1 content; его меняет Supervisor, а Assignment Rule синхронизирует Due Date ToDo.

## C-01. Target Date

Due/overdue behavior существует только при заполненном Target Date.

## P-04. Load Balancing rollback

Финал L9:

```text
Round Robin
```

---

# 13. Web Form invariants

## H-11. Login Required = authentication boundary

Final:

```text
Login Required = Yes
Anonymous = No
```

Guest submit запрещён, но role-specific authorization не обещается.

## H/S-11A. Web Form new insert = separate capability

Exact target insert:

```text
doc.insert(ignore_permissions=True, ...)
```

Следовательно Web Form insert не доказывает Level 0/1/2 Role Permission enforcement.

Web Form field allow-list **не содержит Status**.

Новый Request получает:

```text
Status = New
```

из metadata default.

## H-12. Final Web Form update disabled

```text
Allow Editing After Submit = No
```

Owner update иначе способен использовать `save(ignore_permissions=True)` и обходить Level 1/2 protection.

## H/S-13. Apply Document Permissions = existing-document behavior

Не является create authorization.

## P-05. Web Form population trust policy

Authenticated website accounts с доступом к published form считаются trusted internal reporters.

Role-restricted/public-untrusted intake — Later.

## P-06. Link catalog disclosure

`Allow Read On All Link Options = Yes` — осознанная disclosure policy для trusted reporters.

---

# 14. Packaging invariants

## S-09. Layers

```text
Standard source
universal config
site-specific config
working data
```

## S-10. Universal delivery

```text
core DocTypes
UI/analytics Standard objects
Notifications
Web Form
Roles
Workflow
Custom DocPerm Level 0 + Level 1 + Level 2
```

## P-07. Site-specific

```text
Users
User Permission
Share
Assignment Rule tied to Users
```

## H-15. install-app

Initial app install синхронизирует source/fixtures/customizations/dashboards; migrate — convergence test.

## S-11. Portability scope

Clean-site portability, не arbitrary multi-app compatibility.

## P-08. Active site restore

После L11:

```text
bench use facility-ops.localhost
```

---

# 15. Lab invariants

## P-09. Каждая Lab имеет rollback contract

```text
PRECONDITIONS
TEMPORARY MUTATION
PERSISTENT MUTATION
ROLLBACK
FINAL STATE
GIT STATE
```

Domain rollback обязателен; presentation config может остаться только когда это прямо заявлено.

## H/S/P-09A. Service Request security baseline переживает Labs

После Lab, затрагивающей `Service Request`, обязаны сохраниться:

```text
Level 0 document matrix
Level 1 business-content matrix
Level 2 status matrix
Workflow
```

Точная baseline:

```text
Level 0
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No

Level 1
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write

Level 2
Requester   → Read only
Technician  → Read/Write
Supervisor  → Read/Write
```

Лаборатория не принята, если functional cleanup выполнен, но permission baseline ослаблен.

## P-09B. Временный business-content field/table получает explicit Permission Level

Например Lab A:

```text
work_logs → Permission Level 1
```

После rollback временное поле удаляется полностью.

## S-12. Domain rollback ≠ byte-identical source rollback

Lab E может оставить Standard Print Format, не меняя domain/security model.

---

# 16. Compatibility matrix

| Механизмы | Вердикт |
|---|---|
| Requester Create + Level0 Write No | совместимы |
| Requester Level1 Write + Level0 Write No | new content yes, later save no |
| Requester Level2 Write No + status default New | state spoof через ordinary insert не является разрешённой моделью |
| Technician Level0 Write + Level1 Write No | document/workflow yes, content protected |
| Technician Level2 Write + Workflow | field authority + transition gate |
| Permission Level + ignore_permissions | не enforcement при bypass |
| Desk Create + Web Form Create | разные admission paths |
| Assignment + authorization | не эквивалентны |
| Assignment + Level1/2 authority | не эквивалентны |
| Workflow + Only Allow Edit For | server transition vs Desk guard |
| Workflow + Web Form edit | unsafe; final edit Off |
| Main Assignment Rule + clean site | intentionally different |
| Labs + hardened permissions | compatible only with explicit permlevel + rollback |

---

# 17. Execution contract

Каждый урок:

```text
PRECONDITIONS
TEMPORARY MUTATIONS
PERSISTENT MUTATIONS
ROLLBACK
OUTPUT STATE
GIT STATE
```

```text
OUTPUT(Ln) ⊇ PRECONDITIONS(Ln+1)
```

Для Labs:

```text
FINAL_SECURITY(Lab)
= Level 0 + Level 1 + Level 2 hardened baseline
```

---

# 18. Не обещаем в Core

```text
assignee-only authorization
absolute Closed immutability
role-specific Web Form admission
safe public-untrusted portal
protection from explicit ignore_permissions code paths
arbitrary multi-app compatibility
```

Steel architecture = **максимум реальных штатных гарантий без выдумывания тех, которых платформа не даёт**.
