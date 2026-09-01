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

Сервер Frappe проверяет/нормализует операцию штатным механизмом permissions, validation или workflow.

## S — structural

Следует из metadata/source и модели.

## U — UI/process guard

Помогает правильному поведению, но не является отдельной server ACL.

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

После L7 — Workflow State Field.

## S-03. Assignment не дублируется business field

```text
Service Request → Assign To → ToDo → User
```

## S-04. Assignment ≠ authorization

ToDo = responsibility.

Role Permission = base access.

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

## H-04. Status

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

# 4. Document permission invariants

## H-06. Final Service Request Level 0 matrix

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

`Service Request Delete = No` для всех трёх рабочих ролей после temporary L5 experiment.

---

# 5. Field permission invariants

## S/H-07. Service Request business content = Permission Level 1

После L5:

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

`status` остаётся Level 0.

## H-07A. Level 1 role matrix

```text
Requester
→ Level 1 Read Yes / Write Yes

Technician
→ Level 1 Read Yes / Write No

Supervisor
→ Level 1 Read Yes / Write Yes
```

## H-07B. Почему Requester Level 1 Write безопасен

Requester Level 1 Write нужен для заполнения high-permlevel fields нового Document.

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

При отсутствии write-доступа к high Permission Level значения таких полей сбрасываются к разрешённым original/default values перед DB write.

Следовательно штатный permission-aware save Technician не должен сохранять изменения Level 1 content.

При этом Level 0 document Write остаётся для Workflow/state operations.

## Ограничение H-07C

`ignore_permissions=True` отключает этот слой.

Поэтому гарантия формулируется как:

```text
permission-aware Document insert/save
```

а не «никакой код никогда не изменит поле».

Именно поэтому финальный Web Form update выключен.

---

# 6. Temporary permission experiments

## P-01. L5 cleanup

До выхода из L5:

```text
Supervisor Delete = No
Share removed
User Permission removed
technician.restricted disabled
```

## H/P-02. Assignment не раздаёт скрытые permissions

Основные Technician имеют совместимый Role-based access, чтобы Assign To не создавал неожиданные DocShare exceptions.

---

# 7. UI guards

## U-01. Only Allow Edit For ≠ ACL

```text
Role Permission
= server document access

Permission Level
= server field-level write/read control для permission-aware paths

Workflow Allowed Role / Condition
= server state-transition gate

Only Allow Edit For
= Desk state editability
```

## U-02. Status Read Only

После L7 Status Read Only в Desk; server state validity проверяет Workflow.

---

# 8. Workflow invariants

## H-08. State machine

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

Requester local create остаётся возможным; после insert Role Permission Write No — hard boundary.

## H-09. Allowed Role / Condition

Workflow state change должен соответствовать допустимому transition пользователя.

## S-06. Accepted не доказывает assignment

`Assign To → Accept` — рекомендуемый process order, но не hard coupling.

## S-07. Technician role ≠ конкретный assignee

Workflow transition разрешается роли, а не ToDo assignee.

## S-08. Closed terminal, не absolute immutable

Нет исходящего transition; working roles no-delete.

Absolute API immutability — Later.

---

# 9. Automation invariants

## P-03. Assignment Rule site-specific

Rule с concrete Users не universal fixture.

## H-10. Assignment Rule не меняет Workflow state

```text
Assigned To = Technician
Status = New
```

## C-01. Target Date

Due/overdue behavior существует только при заполненном Target Date.

## P-04. Load Balancing rollback

Финал L9:

```text
Round Robin
```

---

# 10. Web Form invariants

## H-11. Login Required = authentication boundary

Final:

```text
Login Required = Yes
Anonymous = No
```

Guest submit запрещён, но role-specific authorization не обещается.

## H/S-11A. Web Form new insert = separate capability

Exact new target insert:

```text
doc.insert(ignore_permissions=True, ...)
```

Следовательно Web Form insert обходит и Level 0 Role Create, и high Permission Level validation path.

Это сознательная intake capability самой Web Form.

Web Form fields поэтому должны быть **явным allow-list только безопасных intake fields**.

## H-12. Final Web Form update disabled

```text
Allow Editing After Submit = No
```

Owner update иначе способен использовать `save(ignore_permissions=True)`.

## H-13. Web Form не управляет Workflow

`Status` не входит в form field allow-list; новый Request получает default New.

## H/S-14. Apply Document Permissions = existing-document behavior

Не является create authorization.

## P-05. Web Form population trust policy

Authenticated website accounts с доступом к published form считаются trusted internal reporters.

Role-restricted/public-untrusted intake — Later.

## P-06. Link catalog disclosure

`Allow Read On All Link Options = Yes` — осознанная disclosure policy для trusted reporters.

---

# 11. Packaging invariants

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
Custom DocPerm
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

# 12. Lab invariants

Labs имеют Temporary / Persistent / Rollback / Final State.

Domain rollback обязателен; presentation config может остаться осознанно.

---

# 13. Compatibility matrix

| Механизмы | Вердикт |
|---|---|
| Requester Create + no post-write | совместимы |
| Requester Level1 Write + Level0 Write No | совместимы: insert fields yes, later save no |
| Technician Level0 Write + Level1 Write No | совместимы: Workflow yes, business content protected |
| Permission Level + ignore_permissions | **не enforcement** при ignore_permissions |
| Desk Create + Web Form Create | разные admission paths |
| Login Required + role authorization | не эквивалентны |
| Apply Document Permissions + Web insert | не эквивалентны |
| Assignment + authorization | не эквивалентны |
| Workflow + Only Allow Edit For | server transition vs Desk guard |
| Workflow + Web Form edit | unsafe; final edit Off |
| Main Assignment Rule + clean site | intentionally different |

---

# 14. Execution contract

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

---

# 15. Не обещаем в Core

```text
assignee-only authorization
absolute Closed immutability
role-specific Web Form admission
safe public-untrusted portal
protection from explicit ignore_permissions code paths
arbitrary multi-app compatibility
```

Steel architecture = **максимум реальных штатных гарантий без выдумывания тех, которых платформа не даёт**.
