# Инварианты учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Этот файл — **технический контракт курса для автора, методиста и аудита**. Новичку не нужно читать его перед практикой.

Главное правило:

```text
каждая заявленная гарантия
должна иметь названный реальный механизм Frappe
```

Курс не должен обещать более сильную гарантию, чем реально даёт выбранный механизм.

---

# 1. Уровни силы утверждений

## H — hard / server-enforced

Сервер Frappe проверяет операцию штатным permissions, validation или Workflow.

## S — structural

Следует из metadata/source и структуры модели.

## U — UI/process guard

Ограничивает или направляет стандартный интерфейс, но не является самостоятельной серверной ACL.

## P — deployment/process policy

Зависит от конфигурации Site, обязательного cleanup/rollback или принятой политики курса.

## C — conditional

Гарантия действует только при названном предусловии.

---

# 2. Core structure

## S-01. Постоянное предметное ядро

```text
Facility Location
Equipment
Service Request
```

## S-02. Один process-state field

```text
Service Request.status
```

После L7 это же поле используется как `Workflow State Field`.

Параллельный `workflow_state` не создаётся.

## S-03. Assignment не дублируется полем

```text
Service Request → Assign To → ToDo → User
```

Отдельный `assigned_technician` в Core отсутствует.

## S-04. Assignment ≠ authorization

```text
ToDo = responsibility
permissions = authority
```

Assignee-only authorization не обещается в Core.

---

# 3. Data invariants

## H-01. Mandatory fields

```text
Subject
Location
Description
Priority
```

## H-02. Equipment optional

`equipment` не Mandatory.

## H-03. Priority values

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

## S-05. Accepted ≠ Assigned To

`Accepted` означает принятие заявки в процесс и не доказывает наличие конкретного `ToDo`.

## S-06. Location semantics

```text
Service Request.location = место события, зафиксированное заявкой
Equipment.location       = текущее место оборудования
```

Вечного equality между ними нет.

---

# 4. Permission architecture курса

После L5 `Service Request` использует **два**, а не три слоя permissions:

```text
Role Permission / Level 0
→ document authority

Permission Level 1
→ business-content field authority
```

После L7 добавляется независимая ответственность:

```text
Workflow
→ transition authority
```

Это важно: Workflow не называется «Permission Level 2», а Permission Level не выдаётся за state machine.

---

# 5. Level 0 — document authority

## H-05. Final Service Request matrix

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

Requester Desk intake после insert является append-only по обычному Role Permission path.

## H-05A. If Owner не блокирует Create

На закреплённой версии `v16.32.0` owner-only folding не применяется к `create`, поэтому сочетание:

```text
Create = Yes
Read = Yes + If Owner
Write = No
```

совместимо с созданием нового Document и последующим запретом обычного save.

## H-05B. Working roles no-delete

После временного эксперимента L5:

```text
Service Request Delete = No
```

для всех трёх рабочих ролей.

---

# 6. Permission Level 1 — business content authority

## S/H-06. Content fields = Permission Level 1

```text
subject
location
equipment
description
priority
target_date
attachment
```

## H-06A. Level 1 matrix

```text
Requester
→ Read Yes / Write Yes

Technician
→ Read Yes / Write No

Supervisor
→ Read Yes / Write Yes
```

## H-06B. Почему Requester Level 1 Write не означает post-create Write

На новом Document Requester имеет:

```text
Level 0 Create = Yes
Level 1 Write = Yes
```

поэтому может заполнить содержательные поля.

После insert:

```text
Level 0 Write = No
```

и обычный повторный save запрещён целиком.

## H-06C. Technician Document Write ≠ content Write

На обычном permission-aware `Document` path Frappe проверяет high-permlevel fields.

Следовательно модель:

```text
Technician Level 0 Write = Yes
Technician Level 1 Write = No
```

не даёт штатного права переписывать содержательные Level 1 поля.

Гарантия **не распространяется** на доверенный server code, который сознательно использует `ignore_permissions=True`, прямой DB API или иной bypass.

---

# 7. Status до Workflow

## S/H-07. Status остаётся Level 0

В L4–L6:

```text
Service Request.status
→ Permission Level 0
→ обычный Select
```

Requester после сохранения не может менять его из-за отсутствия Document Write.

Technician и Supervisor имеют Document Write и могут менять `status` как обычное поле.

## H/S-07A. До L7 переходы не защищены state machine

До включения Workflow пользователь с Write может, например, сохранить:

```text
New → Closed
```

если значение входит в Select options.

Это **намеренный отрицательный результат курса**:

```text
Select values
≠ transition model
```

Не называем это дефектом permissions и не строим отдельный Level 2 только для сокрытия этого учебного факта.

---

# 8. Workflow invariants после L7

## H-08. Workflow state machine

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

Все состояния:

```text
docstatus = 0
```

## H-08A. Первое состояние

При активном Workflow новый Document получает первое состояние Workflow, если state field не установлен.

Прямая попытка создать новый Document сразу в другом состоянии не считается допустимым сохранённым переходом Workflow.

## H-08B. Saved transition validation

Для сохранённого Document изменение workflow state должно соответствовать доступному transition текущего пользователя.

Allowed transition зависит от:

```text
current state
Allowed Role
Condition
```

## H-08C. Workflow использует тот же status

```text
Workflow State Field = status
```

Второе поле состояния не требуется.

## U-01. Status Read Only

После L7:

```text
status → Read Only = Yes
```

Это UI guard. Серверную допустимость перехода обеспечивает Workflow.

## U-02. Only Allow Edit For

```text
Only Allow Edit For
= Desk state editability
≠ самостоятельная ACL
```

## S-07. Closed terminal, не absolute immutable

У `Closed` нет исходящего transition, рабочие роли не имеют Delete.

Но Core не обещает абсолютную неизменяемость через любой возможный server/bypass path.

---

# 9. Assignment / collaboration invariants

## H/S-09. Assignment не меняет status

После назначения:

```text
ToDo exists
Status remains current value
```

## H/S-09A. Assignment не повышает Permission Level 1

Назначение Technician не выдаёт ему право менять:

```text
Description
Priority
Target Date
Location
Equipment
```

если такого права не было у роли.

## S-08. ToDo Closed ≠ Service Request Closed

Закрытие поручения и завершение предметного процесса — разные состояния разных Documents.

## P-01. Auto-Share не является нормальной моделью Core

Основные Technician имеют совместимый Role-based document access, чтобы Assignment не строил скрытую архитектуру на случайных `DocShare`.

---

# 10. Temporary permission experiments

## P-02. L5 cleanup

До выхода из L5:

```text
Supervisor Delete = No
Share removed
User Permission removed
technician.restricted disabled
```

Временный эксперимент считается законченным только после восстановления финальной модели.

---

# 11. Automation invariants

## P-03. Assignment Rule site-specific

Rule с конкретными Users не является универсальной fixture приложения.

## H/S-10. Assignment Rule не меняет Workflow state

```text
Assigned To = Technician
Status = New
```

до отдельного Workflow Action.

## H/S-10A. Automation не расширяет authority

Assignment Rule и Auto Repeat Assignee не выдают Technician Permission Level 1 Write.

## C-01. Target Date

Date-based поведение существует только при заполненном `Target Date`.

## P-04. Load Balancing rollback

Финальный L9 возвращается в:

```text
Round Robin
```

## S-09. Core не обещает собственную Background Job

L9 использует стандартные механизмы `Notification` и `Assignment Rule`, работающие с scheduler infrastructure.

Курс не утверждает, что ученик уже освоил `frappe.enqueue`, retries или `enqueue_after_commit`.

---

# 12. Web Form invariants

## H-11. Login Required = authentication boundary

Финал:

```text
Login Required = Yes
Anonymous = No
```

Guest submit запрещён.

Это не означает role-specific business authorization.

## H/S-11A. Web Form new insert = separate capability

На exact `v16.32.0` Web Form создаёт новый target Document отдельным путём с `ignore_permissions=True`.

Следовательно Web Form insert **не является доказательством** обычного Role Permission / Permission Level path Desk.

## S-10. Status не входит в Web Form fields

Новая заявка использует начальное значение процесса, а пользователь Web Form не получает отдельное поле управления Workflow.

## H-12. Final Web Form update disabled

```text
Allow Editing After Submit = No
```

Курс не оставляет Web Form как параллельный редактор рабочего `Service Request`.

## H/S-13. Apply Document Permissions

Эксперимент относится к existing-document behavior и не превращает Web Form create в обычный Desk Create.

## P-05. Trust policy

Authenticated Website Users финальной формы считаются trusted internal reporters в рамках учебной модели.

Безопасный public-untrusted intake и role-restricted portal — Later.

---

# 13. Packaging invariants

## S-11. Четыре слоя

```text
Standard source
universal app configuration
site-specific configuration
working data
```

## S-12. Universal delivery

На чистый Site приложение должно доставлять:

```text
core DocTypes
field permlevel metadata
Standard reports/cards/chart/workspace
Notifications
Web Form
Roles
Workflow
Custom DocPerm Level 0/1
```

## P-06. Site-specific state

```text
Users
User Permission
Share
Assignment Rule tied to Users
```

не объявляется универсальным состоянием App.

## H/P-14. Clean-site acceptance

L11 вручную проверяет на новом Site:

```text
Requester Desk create/read-own/no-write
Technician Level 1 content protection + Workflow
Supervisor content/process authority + no Delete
Website User Web Form intake
```

## S-13. Core testing boundary

Clean-site acceptance — обязательная проверка Core.

Автоматизированные `FrappeTestCase` / `bench run-tests` не объявляются пройденными до появления собственного программного поведения, которое действительно должно иметь тестовый контракт.

---

# 14. Lab invariants

## P-07. Каждая Lab имеет rollback contract

```text
PRECONDITIONS
TEMPORARY MUTATION
PERSISTENT MUTATION
ROLLBACK
FINAL STATE
GIT STATE
```

## H/S/P-07A. Service Request baseline переживает Labs

После Lab, затрагивающей `Service Request`, сохраняются:

```text
Level 0
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No

Permission Level 1
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write

Workflow
New → Accepted → In Progress → Resolved → Closed
```

## P-07B. Временный content field/table получает Permission Level 1

Если временное поле Lab имеет тот же смысл, что и бизнес-содержание заявки, оно получает Level 1, чтобы лаборатория не создала случайный обход существующей модели.

## S-14. Domain rollback ≠ byte-identical source rollback

Лаборатория может оставить явно заявленный presentation artifact, если это часть результата Lab и не меняет предметную/security model.

---

# 15. Compatibility matrix

| Механизмы | Вердикт |
|---|---|
| Requester Create + Level0 Write No | совместимы |
| Requester Level1 Write + Level0 Write No | new content yes, later ordinary save no |
| Technician Level0 Write + Level1 Write No | workflow/document save yes, content protected |
| Status Level0 до L7 | обычный Select, transitions ещё не защищены |
| Status + Workflow после L7 | transition validation принадлежит Workflow |
| Permission Level + ignore_permissions | не enforcement при сознательном bypass |
| Desk Create + Web Form Create | разные admission paths |
| Assignment + authorization | не эквивалентны |
| Assignment + content authority | не эквивалентны |
| Workflow + Only Allow Edit For | server transition vs Desk guard |
| Workflow + Web Form edit | финально edit Off |
| Main Assignment Rule + clean site | intentionally different site-specific state |
| Labs + permissions | compatible only with explicit rollback |

---

# 16. Execution contract

Каждый Core-урок фиксирует:

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
= Level 0 + Permission Level 1 + Workflow baseline
```

---

# 17. Что Core не обещает

```text
assignee-only authorization
absolute Closed immutability
role-specific Web Form admission
safe public-untrusted portal
protection from explicit trusted ignore_permissions code
custom Permission Types behavior
custom Background Job reliability
Realtime integration
automated tests for custom business code
arbitrary multi-app compatibility
```

Финальный критерий технической честности курса:

> **максимум реальных штатных гарантий без присваивания механизму ответственности, которой Frappe ему не даёт.**
