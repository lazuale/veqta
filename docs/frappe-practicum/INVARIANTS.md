# Инварианты учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Этот документ задаёт формальную модель гарантий учебного приложения: **что именно гарантируется, каким механизмом, с какого урока и какой силой**.

Главное правило:

```text
не называть hard/security invariant то,
что Frappe обеспечивает только интерфейсом,
site policy или дисциплиной пользователя
```

---

# 1. Уровни силы

## H — hard / server-enforced

Проверяется сервером Frappe при штатной операции.

Примеры:

```text
Mandatory field
Link на существующий Document
Role Permission
Workflow transition Allowed Role / Condition
Web Form Allow Edit = No
```

## S — structural

Следует из metadata/source и архитектуры приложения.

Примеры:

```text
ровно три core DocType
status — единственное поле состояния
Assignment не хранится собственным business field
```

## U — UI/process guard

Помогает работать правильно, но не является самостоятельной server security boundary.

Примеры:

```text
Status Read Only
Workflow Only Allow Edit For
отсутствие Status в Web Form
```

## P — deployment/process policy

Верно только при конкретной конфигурации site или обязательном rollback.

Примеры:

```text
Assignment Rule включён на основном site
временный User Permission удалён после L5
после L11 active site снова facility-ops.localhost
```

## C — conditional invariant

Гарантия действует только при выполнении явно указанного предусловия.

Пример:

```text
Target Date задан
→ может существовать Due Date / overdue automation
```

---

# 2. Фазы жизни

```text
L0–L3  → платформа и справочники
L4–L6  → ручной рабочий документ
L7+     → Workflow-процесс
L9+     → automation на основном site
L10+    → authenticated external intake
L11     → portable app + site-specific deployment
Labs    → временные отклонения с обязательным rollback
```

Фазовое правило:

```text
Status можно менять вручную
```

верно только до L7.

---

# 3. Структурные инварианты

## S-01. Постоянное предметное ядро

**Действует:** L4+

```text
Facility Location
Equipment
Service Request
```

Лабораторные Child/Single/Submittable DocType не становятся core автоматически.

## S-02. Один источник состояния заявки

**Действует:** L4+

```text
Service Request.status
```

После L7 это же поле — `Workflow State Field`.

Не создаются параллельные:

```text
workflow_state
request_state
processing_status
```

## S-03. Assignment не дублируется business field

**Действует:** L6+

```text
Service Request
→ Assign To
→ ToDo
→ User
```

Не создаются собственные:

```text
Assigned Technician
Assignee
Technician User
```

## S-04. Assignment не является авторизацией

**Действует:** L6+

```text
Permission
≠ Assignment
```

`Assign To` отвечает за ответственность и очередь работы. Role Permission отвечает за доступ.

Наличие ToDo не считается доказательством права читать/писать Document.

Assignee-only authorization требует отдельной server-side permission/validation архитектуры и находится в Later.

---

# 4. Инварианты данных

## H-01. Обязательные поля Service Request

**Действует:** L4+

```text
Subject
Location
Description
Priority
```

обязательны на уровне DocType.

Требование действует для:

```text
Desk
Web Form
Auto Repeat
automation test data
clean-site acceptance
Labs
```

## H-02. Equipment необязателен

```text
Service Request.equipment
```

не Mandatory.

## H-03. Допустимые Priority

```text
Low
Medium
High
```

Default:

```text
Medium
```

## H-04. Допустимые Status

```text
New
Accepted
In Progress
Resolved
Closed
```

`Accepted` означает:

```text
Supervisor принял заявку в рабочий процесс
```

и не означает наличие ToDo или assignee.

## H-05. Equipment Category

```text
HVAC
Electrical
IT
Other
```

Новое значение вроде `Pump` нельзя использовать без изменения metadata.

## S-05. Семантика Location

```text
Service Request.location
= историческое место события / проблемы

Equipment.location
= текущее размещение Equipment
```

Hard invariant:

```text
Service Request.location == Equipment.location
```

**не вводится**.

При создании учебных данных значения выбираются логично, но дальнейшее перемещение Equipment не должно переписывать историческую Location заявки.

---

# 5. Permission invariants

## H-06. Role Permission — базовая security boundary

**Действует:** L5+

Финальная server-side permission matrix для `Service Request`:

```text
Requester
→ Create = Yes
→ Read own = Yes через If Owner
→ Write = No
→ Delete = No

Technician
→ Read = Yes
→ Write = Yes
→ Create = No
→ Delete = No

Supervisor
→ Read = Yes
→ Write = Yes
→ Create = Yes
→ Delete = No
→ Report = Yes
→ Export = Yes
```

Ключевой принцип:

```text
Requester intake = append-only после insert
```

Заявитель может подать новую заявку и читать свою, но не переписывать её после сохранения.

## H-06A. If Owner не блокирует Create

В exact `v16.32.0` owner-only свёртка Role Permission специально не применяется к `create`.

Поэтому комбинация:

```text
Requester:
Create = Yes
Read = Yes
Write = No
If Owner = Yes
```

даёт требуемую модель:

```text
создать новый Document можно
после insert читать можно только свой
редактировать после insert нельзя
```

## H-06B. Service Request не удаляется штатной operating policy

После L5 у всех трёх рабочих ролей:

```text
Delete = No
```

Delete изучается только временным experiment L5 и обязательно откатывается.

Цель:

```text
рабочая заявка
→ не исчезает из истории обычным Delete
```

Это не означает, что Frappe глобально запрещает Administrator удалить запись; это permission invariant рабочих ролей курса.

## P-01. User Permission / Share L5 временные

Эксперимент выполняется на:

```text
technician.restricted@example.com
```

До выхода из L5:

```text
Share удалён
User Permission удалён
Restricted Technician отключён
Supervisor Service Request Delete возвращён в No
```

## H-07/P-02. Assignment не должен менять access model скрытым Share

В `v16.32.0` `Assign To` при отсутствии доступа assignee может автоматически создать `DocShare`; при отключённом sharing assignment может завершиться Missing Permission.

Поэтому основные Technician до L9 имеют одинаковый базовый Role-based доступ к `Service Request`.

Цель:

```text
permission architecture задаётся заранее
Assignment не раздаёт скрытые access exceptions
```

## U-01. Only Allow Edit For — не ACL

`Workflow State.only_allow_edit_for` — state-dependent Desk guard.

Правильная модель:

```text
Role Permission
= server access permission

Workflow Allowed Role / Condition
= server transition permission

Only Allow Edit For
= state-dependent Desk editability
```

## U-02. Read Only Status — UI guard

После L7:

```text
status → Read Only = Yes
```

Это убирает свободный Select из Desk. Допустимость state change проверяет Workflow server-side.

---

# 6. Process invariants

## H-08. Workflow state machine

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

Все states:

```text
docstatus = 0
```

## U-03. Desk edit roles после L7

Финальная таблица `Only Allow Edit For`:

| State | Desk edit role |
|---|---|
| New | Facility Supervisor |
| Accepted | Facility Technician |
| In Progress | Facility Technician |
| Resolved | Facility Supervisor |
| Closed | Facility Supervisor |

`New` намеренно принадлежит Supervisor после создания.

При этом Requester всё ещё может **создать** новый Document: exact client Workflow `is_read_only()` возвращает `false` для `doc.__islocal`, а server insert первой Workflow State не является state transition.

После insert настоящий server invariant уже задаёт:

```text
Requester Write = No
```

## H-09. Allowed Role управляет переходом

Workflow transition доступен только роли из `Allowed` и при истинной Condition.

## S-06. Accepted не означает Assigned To

Допустимо:

```text
Status = New
Assigned To = Technician One
```

и технически возможно:

```text
Status = Accepted
Assigned To = пусто
```

Рекомендуемая рабочая последовательность:

```text
Assign To
→ Accept
```

не является hard coupling платформы.

## S-07. Technician role ≠ конкретный assignee

```text
Accepted → In Progress
In Progress → Resolved
```

разрешены роли `Facility Technician`.

Assignment показывает ответственность, Workflow Allowed Role — полномочие роли.

## S-08. Closed — terminal Workflow state, но не абсолютная immutability

У `Closed` нет исходящего transition.

Гарантируется:

```text
Closed
→ штатным Workflow Action назад не перейти
```

Не гарантируется без следующего server-validation слоя:

```text
любое поле Closed Document физически неизменяемо через любой API
```

Удаление рабочими ролями при этом уже запрещено H-06B.

---

# 7. Automation invariants

## P-03. Assignment Rule site-specific

`Service Request Auto Assignment` содержит конкретных Users:

```text
technician.one@example.com
technician.two@example.com
```

Поэтому не является universal fixture.

## H-10. Assignment Rule не меняет Workflow state

После auto assignment:

```text
Assigned To = Technician
Status = New
```

`New → Accepted` выполняется отдельно.

## C-01. Target Date задаёт условную автоматизацию

Если `Target Date` заполнен:

```text
Assignment Rule ToDo.date
→ следует Target Date

Service Request One Day Overdue
→ может сработать через 1 день после Target Date
```

Если пуст:

```text
нет обещания Due Date
нет date-based overdue trigger
```

## P-04. Load Balancing не остаётся финальной конфигурацией

После optional experiment:

```text
Rule = Round Robin
```

---

# 8. Web Form invariants

## H-11. Финальная форма требует login

```text
Login Required = Yes
Anonymous Responses = No
```

Guest mode — временный experiment L10.

## H-12. Финальная Web Form create/read-only

```text
Allow Editing After Submit = No
```

Причина: owner-based Web Form update при `Apply Document Permissions = No` может сохраняться через `doc.save(ignore_permissions=True)`.

Поэтому `Allow Edit` изучается временно и обязательно отключается.

Финальная модель:

```text
Website User
→ создать заявку
→ видеть свои ответы
→ не редактировать созданный Service Request через Web Form
```

## H-13. Web Form не управляет Workflow

В пользовательских Web Form fields отсутствует:

```text
Status
```

После insert:

```text
Status = New
```

за счёт DocType default.

## P-05. Link catalog disclosure — trust decision

`Allow Read On All Link Options = Yes` для Location/Equipment означает осознанное раскрытие имён этих справочников authenticated Website Users.

Threat model:

```text
Website User = trusted internal reporter
```

Публичный untrusted internet intake — Later.

---

# 9. Packaging invariants

## S-09. Четыре слоя

```text
1. Standard source
2. universal app configuration
3. site-specific configuration
4. working data
```

## S-10. Universal app configuration

Через source/fixtures/customizations поставляются:

```text
3 core DocType
Reports/Cards/Chart/Workspace
Notifications
Web Form
Roles
Workflow States
Workflow Action Masters
Workflow
Custom DocPerm
```

## P-06. Неуниверсальная конфигурация не fixture

Не входят в universal fixtures:

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

## H-14. install-app — первоначальная установка

`install_app()` v16.32.0 выполняет первоначальную синхронизацию source, fixtures, customizations и dashboards.

`migrate` после установки в L11 проверяет повторный update/convergence path.

## S-11. Portability scope

L11 доказывает:

```text
clean-site portability
```

но не arbitrary co-installation compatibility с любым набором сторонних apps.

## P-07. После L11 возвращается основной site

```text
bench use facility-ops.localhost
```

обязателен перед Labs.

---

# 10. Lab invariants

## P-08. Lab rollback contract

Каждая лаборатория фиксирует:

```text
Temporary Mutation
Persistent Mutation
Rollback
Final State
```

## S-12. Domain rollback ≠ source rollback

Labs не должны незаметно расширять domain model.

Но presentation configuration может остаться.

Пример:

```text
Lab E
→ Standard Print Format остаётся
→ Letter Head удаляется
→ новых core business entities нет
```

---

# 11. Compatibility matrix

| Механизмы | Совместимость | Условие |
|---|---|---|
| DocType Mandatory ↔ Web Form | жёсткая | Web Form не ослабляет Mandatory |
| Requester Create ↔ post-create immutability | жёсткая | Create Yes + Read own + Write No |
| Requester ↔ Workflow New | совместимы | local new doc editable; после insert Write No |
| Role Permission ↔ Workflow | совместимы | access ≠ transitions |
| Only Allow Edit For ↔ security | не эквивалентны | UI guard, не ACL |
| Assignment ↔ Workflow | ортогональны | assignment не кодирует status |
| Assignment ↔ authorization | не эквивалентны | assignee не permission predicate |
| User Permission ↔ Round Robin | опасная без cleanup | main Technician без Location restriction |
| Assignment Rule ↔ permissions | совместимы | не допускать unexpected auto-Share |
| Target Date ↔ Due Date | условная | только если Target Date задан |
| Workflow ↔ Web Form edit | небезопасная | final Allow Edit = No |
| Workflow ↔ Kanban | допустима для демонстрации | после L7 Kanban удалить |
| Standard source ↔ fixtures | совместимы | fixtures не дублируют Standard DocType |
| Main site ↔ clean site | намеренно различаются | Assignment Rule site-specific |
| Labs ↔ core domain | совместимы | обязательный rollback domain changes |

---

# 12. State contract урока

Каждый execution-аудит использует один шаблон:

```text
PRECONDITIONS
TEMPORARY MUTATIONS
PERSISTENT MUTATIONS
ROLLBACK
OUTPUT STATE
GIT STATE
```

Формальный критерий:

```text
OUTPUT(Ln)
должен удовлетворять
PRECONDITIONS(Ln+1)
```

Если нет — ошибка находится в курсе, а не в ученике.

---

# 13. Что сознательно не обещаем без следующего уровня

В base no-own-code маршруте не обещаем:

```text
редактировать Service Request может только конкретный assignee

Closed физически неизменяем на уровне любого API

Equipment.location всегда равен исторической Service Request.location

Website User безопасно редактирует заявку на любой стадии Workflow

facility_ops бесконфликтно co-installable с любым сторонним app
```

Для этих гарантий нужен отдельный server-side слой: Server Script/custom controller/custom permission logic или другая специально спроектированная validation architecture.

Базовая архитектура должна быть **честно ограниченной, а не псевдобезопасной**.
