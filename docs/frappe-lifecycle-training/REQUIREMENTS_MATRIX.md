# Матрица требований второго учебного практикума Frappe

Статус: **аудированная матрица; основание для dependency graph**.

Этот документ продолжает [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md).

Следующий слой — [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md). Матрица сама не является roadmap: она проверяет причинность архитектуры.

```text
требование
    ↓
новая ответственность
    ↓
первый штатный механизм Frappe
    ↓
почему его семантика подходит
    ↓
где граница
    ↓
что можно наблюдаемо доказать
```

Нормативная база:

- [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md);
- [`03_DOCUMENT_LIFECYCLE.md`](../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md);
- [`04_SECURITY.md`](../frappe-architecture-standard/04_SECURITY.md);
- [`05_TRANSACTIONS_ASYNC.md`](../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md);
- [`09_DEPLOYMENT_TESTING.md`](../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md);
- актуальная документация и исходный код Frappe v16.33.0.

---

# 1. Уровни требований

## CORE

```text
R01–R17
```

CORE отвечает на один вопрос:

> Как собственный Frappe Document проходит от обычного рабочего состояния к управляемому согласованию и затем к системно зафиксированному факту?

## NEXT

```text
N01 Assignment / ToDo
N02 Notification
N03 File / Comment / Version
N04 Print
```

NEXT не становится обязательным только потому, что механизм существует во Frappe.

## GATE

```text
D00–D04
```

GATE включается только после нового требования.

## Вне второго практикума

```text
REST API
custom whitelisted API
Webhook
background jobs
custom scheduler code
foreign DocType extension
doc_events
extend_doctype_class
override_doctype_class
Web Form / Portal
custom frontend
Query Report / Script Report
complex User Permission model
Permission Type без отдельной команды
external integration
concurrency / locking
production deployment
```

---

# 2. CORE — минимальный Document

## R01. Purchase Request — самостоятельный Document

**Требование:** сотруднику нужен самостоятельный документ внутренней заявки на закупку.

Минимальные данные:

```text
subject
description
requested_amount
needed_by
```

**Ответственность:** хранить одну заявку с собственной identity и lifecycle.

**Первый механизм:** Standard `DocType` `Purchase Request` собственного учебного App.

**Не создаются заранее:**

```text
Purchase Request Item
Supplier
Department
Budget
Cost Center
Approval Log
Approver
Executor
Purchase Request Status DocType
```

**Граница:** второй практикум не повторяет первый через искусственно большую модель данных.

**Проверка:** создать Purchase Request через Desk, найти через List, открыть повторно.

---

## R02. Requester в CORE равен `Document.owner`

**Требование:** заявку подаёт пользователь, который сам её создаёт.

**Ответственность:** определить инициатора для self-approval policy.

**Первый механизм:** системный `owner`.

```text
requester = owner
```

**Почему подходит:** Frappe Workflow проверяет self approval именно относительно `doc.owner`.

**Не создаётся:** `requester → Link → User` только ради дублирования owner.

**Граница:** создание от имени другого сотрудника — `D02`.

**Проверка:** документ, созданный test User, имеет этого пользователя в `owner`.

---

# 3. CORE — состояние до Workflow

## R03. Обычное business state существует раньше Workflow

**Требование:** пользователь должен понимать, где находится заявка.

**Ответственность:** хранить текущий business state.

**Первый механизм:** Standard `status : Select`.

### Глобальная граница будущего Workflow State учитывается сразу

`Workflow State.workflow_state_name` уникален на весь Site. Поэтому persisted значения `status`, которые позднее станут Workflow State, не должны случайно захватывать общие записи другого App.

Для этого практикума physical state values с самого начала App-scoped:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
```

Default:

```text
PR Draft
```

В схемах и объяснениях ниже ради читаемости используются короткие aliases:

```text
Draft           = PR Draft
Pending Manager = PR Pending Manager
Approved        = PR Approved
Rejected        = PR Rejected
```

Позднее по требованиям появятся:

```text
Pending Senior = PR Pending Senior
Cancelled      = PR Cancelled
```

На этом этапе ещё нет:

```text
Pending Senior
Cancelled
Workflow
Is Submittable
```

**Граница:** несколько значений не являются доказательством необходимости Workflow. Namespacing — это защита глобального setup namespace, а не причина включать Workflow раньше времени.

**Проверка:** создать записи с разными status и отфильтровать в List.

---

## R04. Обычный status не выдаётся за transition policy

**Требование:** показать ограничение простой модели до появления нового механизма.

**Ответственность:** отделить хранение state от разрешения transition.

**Новый механизм:** не добавляется.

**Отрицательный опыт:** пользователь с обычным Write может технически изменить:

```text
Pending Manager → Approved
```

если существует только обычный Select.

**Вывод:**

```text
status
= хранит state

но сам по себе не выражает
= кто может выполнить конкретный transition
```

Это не «дыра Frappe», а отсутствующая ответственность модели.

---

# 4. CORE — базовые права

## R05. Requester и первый Approver имеют базовый доступ к DocType

**Требование:** участники могут работать с Purchase Request, но базовый доступ не означает право любого transition.

На этом этапе существуют только:

```text
Purchase Requester
Purchase Approver
```

`Senior Purchase Approver` пока не создаётся.

**Ответственность:** базовая авторизация Document operations.

**Первый механизм:** `Role + DocType Permissions`.

Baseline до Submittable:

| Role | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Purchase Requester | yes | yes | yes | no |
| Purchase Approver | yes | no | yes | no |

`Submit`, `Cancel` и `Amend` пока не используются: соответствующих требований ещё нет.

### Dev-site и delivery — не одно и то же

На dev-site Role records можно создать через Desk, чтобы выбрать их в Standard DocType Permissions и позже в Workflow.

Но **это ещё не означает, что Role обязан стать fixture**.

В текущем Frappe v16.33.0 `DocType.make_module_and_roles()` при sync Standard DocType создаёт отсутствующие `Role`, перечисленные в его DocPerm, и включает `desk_access=1`.

Следовательно, пока нашим ролям не нужны дополнительные нестандартные свойства:

```text
Standard Purchase Request DocPerm
→ source of truth permission model
→ при install/sync Framework создаёт missing Role records
```

Отдельный Role fixture для тех же имён был бы дублированием одной ответственности двумя механизмами.

**Граница:** если позже Role понадобится дополнительная App-owned конфигурация, которую Standard DocPerm sync не выражает, fixture снова оценивается по реальному требованию.

**Проверка:** реальные server-side create/read/write/delete operations под test Users.

---

# 5. CORE — появление Workflow

## R06. Role-controlled transitions требуют Workflow

Новое требование:

```text
Purchase Requester:
Draft → Pending Manager

Purchase Approver:
Pending Manager → Approved
Pending Manager → Rejected

Purchase Requester:
не может Pending Manager → Approved
```

**Ответственность:** политика допустимых переходов.

**Первый механизм:** `Workflow`.

**Почему подходит:** появились одновременно states, transitions, roles и правила допустимого действия.

**Не создаются:**

```text
custom approve()
if role == ... в разных hooks
JS-кнопка как единственная защита
Approval Log как собственный workflow engine
```

### Workflow State namespace уже определён R03

До создания Workflow создаются только App-scoped Workflow State records, соответствующие уже существующим persisted значениям `status`:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
```

То есть решение о глобальных именах не откладывается до delivery-аудита: без этих records базовый Workflow вообще нельзя честно собрать.

### Обязательная state edit policy

`Workflow Document State.allow_edit` (`Only Allow Edit For`) является обязательной частью конфигурации Workflow. Его нельзя заполнять случайно.

Baseline:

```text
Draft           → Purchase Requester
Pending Manager → Purchase Approver
Rejected        → Purchase Requester
Approved        → Purchase Approver
```

Позднее по требованиям появится:

```text
Pending Senior → Senior Purchase Approver
```

`Cancelled` ещё не существует и его edit-policy заранее не выбирается.

**Граница:** `allow_edit`, DocPerm и transition role — разные уровни.

По результатам аудита `allow_edit` не используется как единственное доказательство серверного запрета изменения полей. В CORE это state/edit policy стандартного Workflow, проверяемая через Desk/observed behavior. Серверная безопасность процесса доказывается transitions, DocPerm, self-approval check и docstatus.

**Проверка:**

```text
Requester может Draft → Pending Manager
Requester не может Approve
Approver может Approve/Reject
Desk отражает принятую Only Allow Edit For policy
```

---

## R07. У состояния остаётся один Standard source of truth

**Требование:** включение Workflow не должно создавать второе обязательное поле состояния.

Запрещённая модель:

```text
status
+
workflow_state
```

если оба означают одно и то же.

**Ответственность:** единое хранение state.

**Первый механизм:** использовать уже существующее Standard поле:

```text
status = Select
Workflow State Field = status
```

**Ключевая коррекция после аудита:** менять `status` с Select на `Link → Workflow State` не требуется.

**Почему:** в Frappe v16.33.0 `Workflow.create_custom_field_for_workflow_state()` создаёт Link field только когда указанного field вообще нет в Meta. Существующее Standard поле может быть Workflow State Field без лишней смены типа.

Следовательно:

```text
никакой обязательной Select → Link migration
никакого site-local workflow_state Custom Field
один Standard field в App source
```

После появления Workflow для `status` фиксируется:

```text
No Copy = yes
```

чтобы обычное Duplicate не переносило текущий workflow-state как старт нового документа.

`Allow on Submit` пока не нужен: он появится только тогда, когда Workflow должен менять state уже Submitted Document — см. `R13`.

**Проверка:**

```text
Purchase Request Meta содержит один status
status остаётся Standard Select
Workflow.workflow_state_field = status
обязательного Custom Field workflow_state нет
```

---

## R08. Workflow Action используется как штатная очередь действий

**Требование:** Approver должен видеть ожидающее процессное действие без собственного Approval Inbox.

**Ответственность:** представить ожидающие Workflow actions.

**Первый механизм:** `Workflow Action`.

**Важная граница текущего Frappe:** Workflow Action создаётся с `permitted_roles`. Это role-scoped runtime record, а не отдельная окончательная ACL конкретного пользователя.

Поэтому проверка разделяется:

```text
чистый Requester без Approver role
→ не видит Approver Workflow Action

Approver role
→ видит role-permitted Workflow Action

owner + Approver role + allow_self_approval=false
→ наличие role-permitted action не отменяет
  серверный запрет фактического apply_workflow()
```

Нельзя использовать только присутствие/отсутствие Workflow Action как доказательство self-approval security.

Email не обязателен для CORE.

---

# 6. CORE — условное согласование

## R09. Большая сумма создаёт второй уровень approval

Новое требование:

```text
requested_amount <= LIMIT
→ достаточно Purchase Approver

requested_amount > LIMIT
→ нужен Senior Purchase Approver
```

Только теперь появляются:

```text
Senior Purchase Approver
Pending Senior
```

**Ответственность:** условно выбрать дальнейший transition и дать второму уровню свою роль.

**Первый механизм:**

```text
Role + базовый DocPerm
+
Workflow Transition Condition
```

Senior baseline до Submittable:

| Role | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Senior Purchase Approver | yes | no | yes | no |

`status` Select получает новое persisted значение:

```text
PR Pending Senior
```

и создаётся соответствующий Workflow State record.

Схема (короткие aliases):

```text
Draft
→ Pending Manager

маленькая сумма:
Pending Manager → Approved

большая сумма:
Pending Manager → Pending Senior → Approved
```

**Граница:** LIMIT пока является фиксированной частью учебного сценария. Настраиваемый LIMIT — `D03`.

**Проверка:** две заявки по разные стороны LIMIT получают разные доступные transitions.

---

## R10. Self approval запрещён штатной политикой Workflow

**Требование:** Approver не может одобрить документ, который создал сам.

```text
allow_self_approval = false
```

**Ответственность:** запретить self approval transition.

**Первый механизм:** штатный `Allow Self Approval` transition.

**Не пишется:** собственная `doc.owner == frappe.session.user` проверка.

**Граница:** корректно только пока R02 (`requester = owner`) истинно.

**Проверка:** dual-role owner не может фактически выполнить `apply_workflow()` Approve; другой Approver может.

---

## R11. Rejected остаётся draft-state и может быть переотправлен

**Требование:** отрицательное решение до final approval не является системной отменой Submitted Document.

```text
Rejected → docstatus 0
```

**Ответственность:** выразить отрицательное решение на draft-стадии и дать понятный путь исправления.

**Первый механизм:** Workflow State `PR Rejected` с `Doc Status = 0` + явный transition:

```text
Rejected
→ Purchase Requester edits
→ Submit for Review
→ Pending Manager
```

**Не используется:** `Rejected = Cancelled`.

**Проверка:** после Reject документ имеет `docstatus 0`, Requester может исправить его и повторно отправить только разрешённым Workflow transition.

---

# 7. CORE — final approval становится системным фактом

## R12. Final Approved становится Submitted только после отдельного требования

Новое требование:

> После final approval сумма, назначение и срок считаются зафиксированным разрешением и не должны бесследно переписываться обычным Save.

**Ответственность:** системно зафиксировать подтверждённый Document.

**Первый механизм:** `Is Submittable + docstatus`.

На этом шаге mapping ещё минимален:

```text
Draft            → docstatus 0
Pending Manager  → docstatus 0
Pending Senior   → docstatus 0
Rejected         → docstatus 0
Approved         → docstatus 1
```

`Cancelled` пока не добавляется: сама возможность зафиксировать факт ещё не создаёт требования отменять его.

### Frappe сам добавляет amended_from как часть Submittable capability

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** при сохранении `Is Submittable` метод `DocType.make_amendable()` автоматически добавляет Standard field:

```text
Amended From
fieldname  = amended_from
fieldtype  = Link
options    = Purchase Request
read_only  = yes
no_copy    = yes
```

если такого field ещё нет.

Поэтому практикум **не создаёт amended_from вручную**.

При этом наличие поля ещё не означает, что бизнес уже разрешил Amend:

```text
Framework capability
≠
выданное право Amend
≠
принятая ответственность исправлять документ
```

`Amend` появится отдельным требованием только в `R14`.

### Submit DocPerm появляется только теперь

Workflow transition role не выдаёт системное право `submit()`.

Оба возможных final approver должны уметь реально выполнить submit-path:

| Role | Submit |
|---|---:|
| Purchase Approver | yes |
| Senior Purchase Approver | yes |
| Purchase Requester | no |

**Почему:** маленькую заявку финально одобряет `Purchase Approver`, большую — `Senior Purchase Approver`; оба transitions должны уметь привести Document к `docstatus = 1`.

`Cancel` и `Amend` права пока не выдаются.

**Ключевой вывод:**

```text
Approved = docstatus 1
не из-за слова Approved,
а из-за требования зафиксировать факт.
```

---

## R13. Появилась отдельная политика отмены Submitted approval

Новое требование:

> Уже одобренное разрешение иногда нужно официально отменить, не удаляя и не возвращая его в Draft.

CORE-политика ответственности:

```text
Purchase Approver
→ владеет отменой Approved Purchase Request

Senior Purchase Approver
→ только второй уровень final approval для дорогих заявок

Purchase Requester
→ не отменяет Submitted approval
```

**Ответственность:** перевести ранее Submitted факт в системное Cancelled состояние.

**Первый механизм:** Workflow transition `Approved → Cancelled` + `docstatus 2` + стандартный `Cancel` DocPerm.

Только здесь появляются:

```text
status option = PR Cancelled
Workflow State PR Cancelled → Doc Status 2
status.Allow on Submit = yes
```

и права:

| Role | Cancel |
|---|---:|
| Purchase Approver | yes |
| Senior Purchase Approver | no |
| Purchase Requester | no |

На этом шаге `Only Allow Edit For` для нового Cancelled state временно соответствует текущей ответственности отмены:

```text
Cancelled → Purchase Approver
```

Если позже появляется обязанность Requester создавать исправленную версию, state/edit policy меняется вместе с новым требованием — см. `R14`.

**Почему `Allow on Submit` у status появляется здесь:** Workflow должен изменить state field у уже Submitted Document при системном cancel-path. Это техническое свойство workflow-state field и не разрешение редактировать остальные Submitted поля.

Допустимый lifecycle теперь:

```text
Draft-state 0
→ Approved 1
→ Cancelled 2
```

Не проектируются:

```text
Draft → Cancelled
Submitted → Draft
Cancelled → другой state
```

**Почему:** Frappe `apply_workflow()` вызывает `save()`, `submit()` или `cancel()` в зависимости от Doc Status следующего state.

**Проверка:**

```text
final Approve → docstatus 1
Purchase Approver может Approved → Cancelled
Senior Purchase Approver не получает лишнее Cancel право
Requester не может Cancel
Cancelled → docstatus 2
illegal transitions отклоняются
```

---

## R14. Смысловая ошибка после Cancel исправляется через Amend

Новое требование:

> После отмены согласованной заявки requester должен создать исправленную версию, сохранив связь с исходным фактом.

**Ответственность:** исправить факт без переписывания отменённой записи.

**Первый механизм:** штатный `Amend` cancelled Document.

CORE-политика:

```text
Purchase Approver
→ Cancel original

Purchase Requester
→ Amend cancelled original
→ исправляет новый Draft
→ снова отправляет его по Workflow
```

### Amend DocPerm появляется только теперь

`Amend` — отдельный стандартный permission type Frappe. Он не следует автоматически из Write/Create/Cancel.

| Role | Amend |
|---|---:|
| Purchase Requester | yes |
| Purchase Approver | no |
| Senior Purchase Approver | no |

У Requester уже есть `Create = yes` из R05, что соответствует созданию нового amended Document.

Одновременно `Only Allow Edit For` для `PR Cancelled` меняется на роль, которая теперь владеет следующей пользовательской операцией:

```text
Cancelled → Purchase Requester
```

Это эволюция state/edit policy из нового требования, а не настройка «на будущее» в R13.

**Не используется:**

```text
вернуть docstatus 1 → 0
редактировать исходный Submitted/Cancelled факт
ручной SQL
Allow on Submit для смысловых полей
```

### Amend не принимается на веру

`amended_from` уже присутствует как Standard field, автоматически добавленный Framework при `Is Submittable` в R12.

Desk Frappe использует отдельный `from_amend` copy path, а workflow UI для нового local Document устанавливает default state его текущего docstatus.

CORE ожидает:

```text
Cancelled original
→ Requester Amend
→ new docstatus 0
→ initial Draft workflow-state
→ amended_from = original
```

Но этот native path обязательно проверяется на принятой версии Frappe реальным Desk scenario. `No Copy` не выдаётся за механизм сброса state при Amend: у `from_amend` собственная copy semantics.

**Граница:** если фактический v16 runtime расходится с ожидаемым native path, сначала фиксируется поведение Framework; workaround заранее не проектируется.

---

# 8. CORE — App-owned delivery

## R15. Обязательная lifecycle-конфигурация воспроизводится из App source

**Требование:** новый Site после установки App получает тот же обязательный процесс без ручной донастройки.

Source of truth:

```text
Purchase Request schema + status + amended_from + DocPerm
→ Standard DocType metadata

Purchase Requester / Purchase Approver / Senior Purchase Approver
→ missing Role records создаются Framework из Standard DocPerm при DocType sync
→ отдельный Role fixture в CORE не нужен

нужные PR-* Workflow State records
→ filtered Workflow State fixture

Workflow + child states/transitions/conditions
→ filtered Workflow fixture

test Users
→ Site-local

Workflow Actions
→ runtime Site data, НЕ fixture
```

**Первый механизм:** Standard metadata + минимальные filtered App fixtures только там, где metadata самого Standard DocType не владеет записью.

### Почему Role fixture удалён после аудита

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** `DocType.make_module_and_roles()` при install/sync проходит роли из `permissions` Standard DocType и создаёт отсутствующие `Role` с `desk_access=1`.

В нашем CORE все обязательные роли уже присутствуют в Purchase Request DocPerm и дополнительных свойств Role не требуют.

Следовательно:

```text
DocPerm JSON
→ источник обязательных role names
→ Framework создаёт Role при sync
```

и второй source:

```text
Role fixture с теми же именами
```

не нужен.

### Fixture dependency order остаётся обязательным, но становится проще

Frappe v16 импортирует fixture files в сортированном порядке имён.

Lifecycle fixtures должны идти:

```text
Workflow State
→ Workflow
```

потому что Workflow ссылается на уже существующие Workflow State records.

Первый кандидат v16:

```text
fixture_auto_order = True
+
fixtures hook:
1. Workflow State
2. Workflow
```

Точный код фиксируется исполняемой спецификацией и проверяется clean install.

### Workflow State namespace уже не принимается здесь

Решение о namespace принято в R03/R06 до создания базового Workflow:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
PR Pending Senior
PR Cancelled
```

R15 лишь экспортирует **ровно эти App-scoped records**.

### Запрещено

```text
fixtures = все Role
fixtures = все Workflow
fixtures = все Workflow State
Role fixture, дублирующий роли из Standard DocPerm без дополнительной ответственности
```

**Проверка:**

```text
export-fixtures
→ Git clean после повторного export

clean install
→ Standard DocType sync создаёт missing Role
→ ordered fixtures создают только PR-* Workflow State и Workflow
→ ручная донастройка не нужна
```

---

# 9. CORE — automated contracts

## R16. Lifecycle защищён автоматическими Frappe-aware tests

**Требование:** критические правила не зависят от ручного прокликивания.

**Первый механизм:** Frappe v16 `IntegrationTestCase` + Bench test runner.

Минимальные server contracts:

```text
Requester может Draft → Pending Manager
Requester не может Approve
Approver может Approve/Reject
маленькая сумма не требует Senior
большая сумма требует Pending Senior
Senior завершает большой approval
self approval отклоняется фактическим apply_workflow
Rejected остаётся docstatus 0
Rejected можно исправить и снова отправить
Approved после R12 становится docstatus 1
Requester не имеет submit/cancel permission
Purchase Approver имеет submit/cancel permission
Senior Purchase Approver имеет submit, но не cancel
Purchase Requester имеет amend permission после R14
Approver roles не получают amend без требования
Draft нельзя сразу Cancel
Purchase Approver может Approved → Cancelled
Cancelled = docstatus 2
Cancelled не переходит дальше
обязательного Custom Field workflow_state нет
status остаётся Standard Select
обязательные Role records существуют после sync Standard DocType
```

Отдельные observed/UI checks:

```text
Only Allow Edit For отражается в Desk ожидаемым образом
Workflow Action отображается согласно permitted roles
Requester Amend создаёт новую draft-запись, связанную через amended_from
```

Так state/UI policy не выдаётся за неподтверждённую server ACL.

Не тестируется Frappe «вообще» ради coverage. Автоматическое добавление `amended_from` не превращается в бессмысленный unit-test Framework, но его наличие проверяется как часть App acceptance, потому что R14 зависит от этого metadata.

---

## R17. Lifecycle воспроизводится на чистом Site

**Требование:** доказать, что процесс принадлежит App, а не истории dev-site.

**Первый механизм:** `install-app + migrate + tests + реальный scenario`.

Финальный критерий:

```text
clean compatible Frappe Site
+ committed App
+ Standard Purchase Request metadata/DocPerm/amended_from
+ Role records, восстановленные штатным DocType sync
+ ordered filtered Workflow State / Workflow fixtures
+ automated contracts
+ requester/approver/senior lifecycle
+ Cancel / Amend scenario
= reproducible lifecycle
```

На новом Site нельзя вручную:

```text
создавать обязательные Roles
создавать Workflow State
создавать Workflow
добавлять workflow_state Custom Field
добавлять amended_from вручную
```

Site-local:

```text
test Users
runtime Purchase Requests
runtime Workflow Actions
пароли
local test config
```

Это App acceptance, а не production deployment.

---

# 10. NEXT

## N01. Assignment / ToDo

Если после approval конкретный сотрудник должен выполнить закупку, первый кандидат — Assignment.

Не создавать `executor → User`, если нужен только текущий рабочий исполнитель.

---

## N02. Notification

Если нужно отдельное date-based reminder, первый кандидат — Notification.

Не дублировать:

```text
Workflow Action
Workflow email alert
Assignment notification
```

Date-based Notification имеет scheduler dependency и поэтому не прячется внутри lifecycle CORE.

---

## N03. File / Comment / Version

```text
приложить файл
→ File / Attach

обсудить
→ Comment / Timeline

обычная история изменений
→ Track Changes / Version
```

Не создавать автоматически собственные Attachment/Comment/Approval History DocTypes.

---

## N04. Print

Сначала Standard Print View. `Print Format` — только при реальной недостаточности.

---

# 11. GATE

## D00. Эволюция dev/test данных

После аудита нет обязательной смены:

```text
status Select → Link
```

и нет позднего переименования generic Workflow States в App-scoped records: namespace выбран с R03.

Модель всё равно эволюционирует:

```text
добавляется PR Pending Senior
Approved получает новую docstatus-семантику 1
Frappe добавляет amended_from при Is Submittable
позднее добавляется PR Cancelled
```

Disposable dev/test records можно явно пересоздать штатным Document-путём.

Это не означает, что production migration «не нужна вообще»: поддерживаемая предыдущая версия с реальными данными потребовала бы отдельного migration plan/patch по фактическому изменению.

---

## D01. Отдельное business field можно менять после Submit

Например внешний номер заказа, который не меняет согласованный смысл.

Первый кандидат — `Allow on Submit` только для этого field.

Не путать с техническим `Allow on Submit` workflow-state field `status`, которое появляется в R13 для workflow cancel-path.

---

## D02. Requester перестал совпадать с owner

Появляется отдельное предметное requester field и повторно анализируется self approval.

---

## D03. LIMIT должен быть данными системы

Если администратор должен менять LIMIT без редактирования Workflow, первый кандидат для одного Site-level значения — `Single DocType` Settings.

---

## D04. Approval route стал динамическим

Если маршрут зависит от подразделения, категории, организации, бюджета, внешнего решения и перестаёт естественно выражаться Workflow states/transitions/conditions, выполняется новый fit analysis.

Наличие слова approval не обязывает бесконечно растягивать Standard Workflow.

---

# 12. Явно неправильные решения

## Workflow с первого дня

```text
есть status values
→ сразу Workflow
```

Неправильно: механизм появляется до новой ответственности.

---

## Лишняя смена state field типа

```text
status Select
→ Workflow появился
→ обязательно Link → Workflow State
```

Неправильно для нашего собственного Standard DocType: Framework умеет использовать уже существующий field как Workflow State Field.

---

## Generic Workflow State names без решения global namespace

Неправильно считать `Draft`, `Approved`, `Rejected` автоматически «своими» records: `Workflow State.workflow_state_name` уникален на весь Site.

В этом практикуме persisted values namespaced заранее (`PR ...`), а короткие названия используются только как aliases в схемах.

---

## Senior role заранее

Неправильно: role и Pending Senior появляются только вместе с R09.

---

## `status + workflow_state`

Неправильно при одинаковом смысле: два source of truth.

---

## `Only Allow Edit For` = доказанная server ACL

Неправильно без отдельного доказательства server enforcement. В этом практикуме это обязательная Workflow state/edit policy, а критическая server authorization проверяется другими штатными слоями.

---

## Workflow Action = окончательная ACL

Неправильно: это role-scoped runtime action; фактический transition дополнительно проверяет Workflow, включая self approval.

---

## Rejected = Cancelled

```text
Rejected  → docstatus 0
Cancelled → docstatus 2
```

---

## Approved = Submitted только из-за названия

Неправильно: docstatus 1 появляется только из требования зафиксировать факт.

---

## Workflow transition role заменяет Document permissions

Неправильно:

```text
роль указана в transition
→ значит автоматически есть Submit / Cancel / Amend
```

Это разные права и разные ответственности.

---

## Выдать Cancel/Amend всем Approver-ролям «на всякий случай»

Неправильно: право появляется только вместе с конкретной ответственностью.

CORE:

```text
Purchase Approver        → Cancel approved request
Purchase Requester       → Amend cancelled request
Senior Purchase Approver → ни Cancel, ни Amend без отдельного требования
```

---

## Role fixture дублирует Standard DocPerm без новой ответственности

Если роль нужна только потому, что она уже перечислена в permissions собственного Standard DocType и стандартные свойства Role нас устраивают, Frappe сам создаёт missing Role во время sync.

Отдельный fixture тех же Role records без дополнительного требования создаёт второй source доставки.

---

## Fixtures без dependency order

Неправильно: clean install должен доказать порядок:

```text
Workflow State
→ Workflow
```

Role здесь уже не fixture текущего CORE.

---

## amended_from создавать вручную после Is Submittable

Неправильно для Standard DocType этого практикума: текущий Frappe добавляет этот Standard Link через `DocType.make_amendable()` при включении `Is Submittable`.

---

## Notification дублирует Workflow/Assignment

Неправильно без отдельного notification requirement.

---

# 13. Контроль перед dependency graph

Перед построением/принятием графа нужно ответить `да`:

```text
1. R01–R17 — реальные требования, а не список функций?
2. Requester = owner явно ограничен CORE?
3. requester semantics и status не склеены ложной зависимостью?
4. status появляется раньше Workflow?
5. physical state values namespaced до создания Workflow State records?
6. отрицательный опыт R04 показывает реальную границу status?
7. до R09 нет Senior role/state?
8. Workflow появляется только из role-controlled transitions?
9. allow_edit policy задана осознанно и не выдана за неподтверждённую server ACL?
10. после Workflow остаётся один Standard status?
11. status не меняет тип без необходимости?
12. обязательный site-local workflow_state Custom Field не появляется?
13. Workflow Action не выдаётся за окончательную authorization check?
14. self approval проверяется на apply_workflow?
15. Rejected = docstatus 0 и имеет явный resubmit path?
16. Approved становится docstatus 1 только после отдельного требования?
17. Is Submittable автоматически добавляет amended_from, но это не считается разрешением Amend?
18. Submit право появляется только вместе с final submit responsibility?
19. Cancelled и Cancel право появляются только после отдельного R13?
20. Senior не получает Cancel без требования?
21. Amend permission появляется только вместе с R14 и принадлежит Requester?
22. Cancel и Amend выполняют разные роли ответственности?
23. Cancelled allow_edit policy меняется только когда появляется Amend responsibility?
24. Workflow описывает реальный submit/cancel path?
25. Amend проверяется фактически, а не объясняется выдуманным no_copy поведением?
26. обязательные Role records не дублируются fixtures без причины?
27. fixtures имеют доказанный порядок Workflow State → Workflow?
28. server lifecycle защищён automated contracts?
29. state/UI policies проверяются отдельно?
30. финал — отдельный clean Site acceptance?
31. disposable dev data не выдана за production migration?
32. production migration не объявлена ненужной вообще?
33. NEXT остаётся вне lifecycle CORE?
34. API/async/extension/integration не добавлены ради покрытия?
```

Если хотя бы один ответ отрицательный, сначала исправляется матрица или граф. Roadmap строится только после прохождения этого gate.