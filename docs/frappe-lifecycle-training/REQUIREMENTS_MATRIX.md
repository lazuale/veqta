# Матрица требований второго учебного практикума Frappe

Статус: **аудированная матрица-кандидат перед dependency graph**.

Этот документ продолжает [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md).

Матрица не является roadmap. Она проверяет причинность архитектуры:

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

Начальная семантика:

```text
Draft
Pending Manager
Approved
Rejected
```

На этом этапе нет:

```text
Pending Senior
Cancelled
Workflow
Is Submittable
```

**Ответственность:** хранить текущий business state.

**Первый механизм:** Standard `status : Select`.

**Граница:** несколько значений не являются доказательством необходимости Workflow.

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

Submit/Cancel ещё не используются, потому что Purchase Request пока не Submittable.

**Граница:** Workflow transition role не заменяет DocPerm.

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

### Обязательная state edit policy

`Workflow Document State.allow_edit` (`Only Allow Edit For`) является обязательной частью конфигурации Workflow. Его нельзя заполнять случайно.

Baseline:

```text
Draft           → Purchase Requester
Pending Manager → Purchase Approver
Rejected        → Purchase Requester
```

Позднее:

```text
Pending Senior → Senior Purchase Approver
Approved       → Purchase Approver
Cancelled      → Purchase Approver
```

**Граница:** `allow_edit`, DocPerm и transition role — разные уровни.

**Проверка:**

```text
Requester может Draft → Pending Manager
Requester не может Approve
Approver может Approve/Reject
Requester не может обычным edit менять Pending Manager при принятой state policy
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

**Ключевая коррекция после аудита:** менять `status` с Select на `Link → Workflow State` **не требуется**.

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

После появления Submittable-семантики в R12 дополнительно включается:

```text
Allow on Submit = yes
```

для workflow-state field. Это не разрешает обходить transitions: серверный Workflow всё равно проверяет переход.

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

`status` Select получает новое допустимое значение `Pending Senior`; создаётся соответствующий Workflow State record.

Схема:

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

**Первый механизм:** Workflow State `Rejected` с `Doc Status = 0` + явный transition:

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

Теперь появляется:

```text
Cancelled
```

и mapping:

```text
Draft            → docstatus 0
Pending Manager  → docstatus 0
Pending Senior   → docstatus 0
Rejected         → docstatus 0
Approved         → docstatus 1
Cancelled        → docstatus 2
```

`status` остаётся тем же Standard Select; добавляется значение `Cancelled`, а самому field включается `Allow on Submit = yes` как workflow-state field.

### DocPerm тоже меняется

Workflow transition role не выдаёт системное право `submit()`/`cancel()`.

Поэтому вместе с Submittable-семантикой роли Approver получают:

| Role | Submit | Cancel |
|---|---:|---:|
| Purchase Approver | yes | yes |
| Senior Purchase Approver | yes | yes |
| Purchase Requester | no | no |

**Почему:** final Approve реально вызывает `submit()`, а Cancel transition — `cancel()`.

**Ключевой вывод:**

```text
Approved = docstatus 1
не из-за слова Approved,
а из-за требования зафиксировать факт.
```

---

## R13. Workflow полностью описывает submit/cancel path

**Требование:** после `Is Submittable` не должно существовать параллельной неуправляемой модели lifecycle.

**Ответственность:** связать Workflow State с системным Doc Status.

**Первый механизм:** Workflow State `Doc Status` + Workflow Transitions.

Допустимый путь:

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

**Граница:** Workflow state и docstatus остаются разными понятиями.

**Проверка:** final Approve реально приводит к `docstatus 1`; Cancel transition — к `docstatus 2`; незаконные переходы отклоняются.

---

## R14. Смысловая ошибка после approval исправляется через Cancel / Amend

**Требование:** после final approval обнаружена ошибка, меняющая смысл согласованного факта.

**Ответственность:** исправить факт без переписывания Submitted записи.

**Первый механизм:** `Cancel → Amend`.

**Не используется:**

```text
вернуть 1 → 0
редактировать все Submitted fields
ручной SQL
Allow on Submit для смысловых полей
```

### Amend не принимается на веру

Desk Frappe копирует cancelled Document через отдельный `from_amend` path, а workflow UI для local Document устанавливает default state его текущего docstatus.

Поэтому CORE ожидает:

```text
Cancelled original
→ Amend
→ new docstatus 0
→ initial Draft workflow-state
→ amended_from = original
```

Но это поведение обязательно проверяется на принятой версии Frappe реальным Desk scenario. `No Copy` не выдаётся за механизм сброса state при Amend: `from_amend` имеет отдельную copy semantics.

**Граница:** если фактический v16 runtime расходится с ожидаемым native path, сначала фиксируется поведение Framework; workaround не проектируется заранее.

---

# 8. CORE — App-owned delivery

## R15. Roles и Workflow конфигурация воспроизводятся из App source

**Требование:** новый Site после установки App получает тот же обязательный процесс без ручной донастройки.

Source of truth:

```text
Purchase Request schema + status
→ Standard DocType metadata

Purchase Requester / Purchase Approver / Senior Purchase Approver
→ filtered Role fixtures

нужные Workflow State records
→ filtered Workflow State fixtures

Workflow + child states/transitions/conditions
→ filtered Workflow fixture

test Users
→ Site-local

Workflow Actions
→ runtime Site data, НЕ fixture
```

**Первый механизм:** Standard metadata + filtered App fixtures.

### Fixture dependency order обязателен

Frappe v16 импортирует fixture files в сортированном порядке имён. Без явной последовательности стандартные файлы дали бы:

```text
role.json
workflow.json
workflow_state.json
```

что ставит `Workflow` раньше `Workflow State`.

Поэтому delivery contract обязан обеспечить:

```text
Role
→ Workflow State
→ Workflow
```

штатным ordering/prefix-механизмом. Первый кандидат v16:

```text
fixture_auto_order = True
+
fixtures hook в dependency order
```

Точный код фиксируется исполняемой спецификацией и проверяется clean install.

### Глобальная граница Workflow State

`Workflow State.workflow_state_name` уникален на весь Site.

Следовательно, будущая спецификация обязана решить naming сознательно:

```text
либо App-scoped state names
либо явно доказанное переиспользование общих state records
```

Случайно экспортировать/перезаписывать глобальную запись другого App нельзя.

### Запрещено

```text
fixtures = все Role
fixtures = все Workflow
fixtures = все Workflow State
```

**Проверка:** `export-fixtures → Git clean`, clean install восстанавливает только обязательную конфигурацию в правильном порядке.

---

# 9. CORE — automated contracts

## R16. Lifecycle защищён автоматическими Frappe-aware tests

**Требование:** критические правила не зависят от ручного прокликивания.

**Первый механизм:** Frappe v16 `IntegrationTestCase` + Bench test runner.

Минимальные контракты:

```text
Requester может Draft → Pending Manager
Requester не может Approve
Approver может Approve/Reject
Requester не может обычным Edit менять Pending Manager при принятой state policy
маленькая сумма не требует Senior
большая сумма требует Pending Senior
Senior завершает большой approval
self approval отклоняется фактическим apply_workflow
Rejected остаётся docstatus 0
Rejected можно исправить и снова отправить
Approved после R12 становится docstatus 1
Requester не имеет submit/cancel permission
Approver roles имеют submit/cancel permission
Draft нельзя сразу Cancel
Submitted можно Cancel через допустимый transition
Cancelled = docstatus 2
Cancelled не переходит дальше
обязательного Custom Field workflow_state нет
status остаётся Standard Select
```

Amend дополнительно проверяется manual acceptance и, где возможно без имитации browser semantics, server contract.

Не тестируется Frappe «вообще» ради coverage.

---

## R17. Lifecycle воспроизводится на чистом Site

**Требование:** доказать, что процесс принадлежит App, а не истории dev-site.

**Первый механизм:** `install-app + migrate + tests + реальный scenario`.

Финальный критерий:

```text
clean compatible Frappe Site
+ committed App
+ Standard Purchase Request metadata
+ ordered filtered fixtures
+ mandatory Roles / Workflow States / Workflow
+ automated contracts
+ requester/approver lifecycle
= reproducible lifecycle
```

На новом Site нельзя вручную:

```text
создавать Roles
создавать Workflow State
создавать Workflow
добавлять workflow_state Custom Field
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

После аудита **нет** обязательной смены:

```text
status Select → Link
```

Поэтому этот искусственный migration step удалён.

Модель всё равно эволюционирует:

```text
добавляется Pending Senior
добавляется Cancelled
Approved получает новую docstatus-семантику 1
```

Disposable dev/test records можно явно пересоздать штатным Document-путём.

Это не означает, что production migration «не нужна вообще»: поддерживаемая предыдущая версия с реальными данными потребовала бы отдельного migration plan/patch по фактическому изменению.

---

## D01. Отдельное business field можно менять после Submit

Например внешний номер заказа, который не меняет согласованный смысл.

Первый кандидат — `Allow on Submit` только для этого field.

Не путать с техническим `Allow on Submit` workflow-state field `status`.

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

## Senior role заранее

Неправильно: role и Pending Senior появляются только вместе с R09.

---

## `status + workflow_state`

Неправильно при одинаковом смысле: два source of truth.

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

## Workflow transition role заменяет Submit/Cancel DocPerm

Неправильно: `submit()`/`cancel()` остаются системными Document operations со своими permissions.

---

## Fixtures без dependency order

Неправильно: clean install должен доказать порядок Role → Workflow State → Workflow.

---

## Notification дублирует Workflow/Assignment

Неправильно без отдельного notification requirement.

---

# 13. Контроль перед dependency graph

Перед построением графа нужно ответить `да`:

```text
1. R01–R17 — реальные требования, а не список функций?
2. Requester = owner явно ограничен CORE?
3. status появляется раньше Workflow?
4. отрицательный опыт R04 показывает реальную границу status?
5. до R09 нет Senior role/state?
6. Workflow появляется только из role-controlled transitions?
7. allow_edit policy задана осознанно?
8. после Workflow остаётся один Standard status?
9. status не меняет тип без необходимости?
10. обязательный site-local workflow_state Custom Field не появляется?
11. Workflow Action не выдаётся за окончательную authorization check?
12. self approval проверяется на apply_workflow?
13. Rejected = docstatus 0 и имеет явный resubmit path?
14. Approved становится docstatus 1 только после отдельного требования?
15. Submit/Cancel DocPerm учтены отдельно от transition roles?
16. Cancelled появляется только вместе с Submittable lifecycle?
17. Workflow описывает реальный submit/cancel path?
18. Amend проверяется фактически, а не объясняется выдуманным no_copy поведением?
19. fixtures имеют доказанный dependency order?
20. глобальная уникальность Workflow State не игнорируется?
21. lifecycle защищён automated contracts?
22. финал — отдельный clean Site acceptance?
23. disposable dev data не выдана за production migration?
24. production migration не объявлена ненужной вообще?
25. NEXT остаётся вне lifecycle CORE?
26. API/async/extension/integration не добавлены ради покрытия?
```

Если хотя бы один ответ отрицательный, сначала исправляется матрица. Dependency graph строится только после этого.
