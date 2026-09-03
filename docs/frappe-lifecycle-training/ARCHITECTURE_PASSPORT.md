# Архитектурный паспорт второго учебного практикума Frappe

Статус: **черновик после аудита dependency graph**.

Этот практикум является второй отдельной ступенью после принятого [`docs/frappe-training`](../frappe-training/ARCHITECTURE_PASSPORT.md), но не продолжает его предметную область и не зависит от `rental_training`.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md). Если учебное решение конфликтует со стандартом или актуальным Frappe v16, исправляется практикум.

Формализованные слои:

- [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md);
- [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md).

---

# 1. Назначение

Первый практикум отвечает на вопрос:

> **Как правильно построить собственную модель Frappe App?**

Второй отвечает на другой вопрос:

> **Как обычный Document превращается в управляемый бизнес-процесс и зафиксированный транзакционный факт, не изобретая собственный workflow engine?**

Обязательная учебная ось:

```text
обычный предметный Document
        ↓
обычное business state
        ↓
появилась политика переходов
        ↓
Workflow
        ↓
условный второй уровень approval
        ↓
self-approval policy
        ↓
final approval стал фиксированным фактом
        ↓
Is Submittable / docstatus
        ↓
отдельная ответственность Cancel
        ↓
отдельная ответственность Amend
        ↓
automated contracts
        ↓
clean Site acceptance
```

Практикум не строится как каталог `Workflow → Assignment → Notification → Print`. Каждый механизм появляется только после требования, которое создаёт новую ответственность.

---

# 2. Входные знания

Второй практикум не повторяет с нуля:

```text
Bench / Site / App / Module
Standard DocType
DocField
name / Title Field
Controller
Role / DocType Permissions
Desk Form / List
fixtures
migrate
tests
clean install
```

Это вход из первого CORE-практикума.

Создание второго App, Site и Git остаётся технической предпосылкой, а не новой учебной темой.

---

# 3. Предметная область

Предметная задача — **внутренняя заявка на закупку**.

Сотруднику нужно приобрести товар или услугу для работы. Он создаёт заявку. Заявку рассматривают уполномоченные сотрудники. После окончательного одобрения заявка становится **зафиксированным разрешением на закупку**.

Важно:

```text
Approved Purchase Request
≠ сама покупка
≠ платёж
≠ складская операция
```

`submit` здесь фиксирует факт организационного разрешения потратить согласованную сумму на согласованную цель. Поэтому `docstatus` появляется из предметной семантики, а не как декоративный финальный статус.

---

# 4. Минимальная модель

Стартовая модель намеренно мала:

```text
Purchase Request
├── subject
├── description
├── requested_amount
└── needed_by
```

На старте нет:

```text
Purchase Request Item
Supplier
Department
Budget
Cost Center
Purchase Category
Approval Log
Approver
Executor
Purchase Request Status DocType
Purchase Request Comment
Purchase Request Attachment
```

Второй практикум изучает lifecycle и процесс. Новые сущности не создаются ради большей «реалистичности», пока без них можно честно выразить требования.

---

# 5. Requester = Document.owner

В обязательном сценарии requester — пользователь, который создал Document:

```text
requester = Document.owner
```

Отдельного поля `requester → User` в lifecycle CORE нет.

Это не универсальная модель закупок. Это граница учебного сценария, важная для self approval: штатная реализация Workflow Frappe сравнивает пользователя именно с `doc.owner`.

Если позднее появится требование создавать заявку от имени другого сотрудника, `owner` перестанет полностью выражать requester и self-approval policy придётся пересмотреть.

Важно для dependency graph: эта семантика не является prerequisite обычного business status. Она нужна своей отдельной ветке self approval.

---

# 6. Сначала — обычное business state

Первое требование:

> Пользователь должен понимать, где находится заявка.

Для этого сначала достаточно обычного Standard поля:

```text
status : Select
```

## Physical values namespaced с первого дня

`Workflow State.workflow_state_name` уникален на весь Site. Поэтому значения, которые позднее станут Workflow State records, не должны случайно претендовать на generic setup records другого App.

Persisted values текущего App:

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

Для читаемости в схемах дальше используются короткие aliases:

```text
Draft           = PR Draft
Pending Manager = PR Pending Manager
Approved        = PR Approved
Rejected        = PR Rejected
```

Позднее из новых требований появятся:

```text
Pending Senior = PR Pending Senior
Cancelled      = PR Cancelled
```

На этом этапе намеренно нет:

```text
Pending Senior
Cancelled
Workflow
Is Submittable
```

Наличие нескольких значений само по себе не доказывает необходимость Workflow.

Контрольная мысль:

```text
нужно только хранить состояние?
→ обычное поле

нужно ограничить допустимые переходы по ролям/условиям?
→ появляется кандидат Workflow
```

---

# 7. Один Standard state field — без лишней смены типа

Это обязательное архитектурное решение второго практикума.

Нельзя получить два конкурирующих поля:

```text
status
+
workflow_state
```

если оба выражают один и тот же процесс.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** при сохранении Workflow Framework создаёт `Custom Field → Link → Workflow State` только если указанного `workflow_state_field` вообще нет в Meta целевого DocType.

Следовательно, для собственного Standard `Purchase Request` нет необходимости сначала иметь `status : Select`, а потом менять его тип только потому, что появился Workflow.

Baseline второго практикума:

```text
до Workflow
status = Standard Select

после Workflow
status = тот же Standard Select
Workflow State Field = status
```

То есть:

```text
один fieldname
один source of truth
никакого обязательного site-local workflow_state Custom Field
никакой искусственной Select → Link migration
```

`Workflow State` records всё равно нужны самому Workflow; они создаются с теми же App-scoped physical values, которые `status` использует с R03.

Когда Workflow становится владельцем процесса, для `status` дополнительно фиксируется `No Copy = yes`, чтобы обычное дублирование документа не переносило текущий workflow-state как новый стартовый state.

`Allow on Submit` появляется позднее только тогда, когда Workflow должен менять этот state field у уже Submitted Document в cancel-path.

Это решение основано на семантике текущего Frappe, а не на догме «workflow field всегда обязан быть Link».

---

# 8. Появилась политика переходов → Workflow

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

Появились одновременно:

```text
states
transitions
roles
условия допустимого действия
```

Первый штатный механизм — `Workflow`.

Не создаются собственные:

```text
custom approve() только ради обхода Workflow
if role == ... в lifecycle hooks
JS-кнопки как единственная защита
Approval Log как собственный workflow engine
```

Workflow становится владельцем политики переходов.

## Workflow State namespace выбирается не на delivery-этапе

К моменту создания Workflow уже должны существовать App-scoped records:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
```

Это обязательное prerequisite базового Workflow, а не поздняя косметика экспорта fixtures.

## Only Allow Edit For — обязательная state policy

Каждая строка `Workflow Document State` в текущем Frappe требует `Only Allow Edit For` (`allow_edit`). Поэтому спецификация обязана выбрать эту роль осознанно.

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

`allow_edit` не заменяет DocType Permissions и не заменяет transition role.

По результатам аудита ему также **не приписывается неподтверждённая серверная гарантия**. В CORE он рассматривается как обязательная state/edit policy стандартного Workflow и проверяется через Desk/observed behavior. Критическая серверная авторизация процесса доказывается отдельно через DocPerm, допустимые transitions, self-approval check и docstatus.

---

# 9. Workflow Action — рабочая очередь, но не самостоятельная ACL

После включения Workflow штатный `Workflow Action` используется раньше собственного `Approval Inbox`.

Но важно не приписывать ему лишнюю семантику.

В Frappe v16 `Workflow Action` создаётся для **permitted roles** следующего шага и сам по себе не является доказательством, что конкретный пользователь имеет право выполнить transition в любой ситуации.

Особенно важен dual-role сценарий:

```text
user = owner документа
+
user имеет Approver role
+
allow_self_approval = false
```

Такой пользователь может соответствовать роли Workflow Action, но фактический `apply_workflow()` всё равно обязан отклонить self approval.

Следовательно:

```text
Workflow Action visibility
≠ окончательная серверная авторизация transition
```

Email для Workflow Actions не является обязательной предпосылкой lifecycle CORE: сам Workflow проверяется без отдельной почтовой инфраструктуры.

---

# 10. Условное согласование → Condition

Новое требование:

```text
requested_amount <= LIMIT
→ достаточно Purchase Approver

requested_amount > LIMIT
→ после Purchase Approver нужен Senior Purchase Approver
```

Только теперь появляются:

```text
Senior Purchase Approver
PR Pending Senior
```

и реальная причина использовать `Condition` перехода Workflow.

Смысл (короткие aliases):

```text
Draft
→ Pending Manager

небольшая сумма:
Pending Manager → Approved

большая сумма:
Pending Manager → Pending Senior → Approved
```

Лимит пока является частью фиксированного учебного сценария. `Single DocType` настроек не создаётся ради демонстрации.

---

# 11. Self approval — отдельная политика

Вопрос:

> Может ли пользователь с Approver role одобрить Document, который сам создал?

CORE-ответ:

```text
нет
```

Используется штатный `allow_self_approval = false` конкретного Workflow Transition.

Собственная проверка:

```python
if doc.owner == frappe.session.user:
    ...
```

не пишется, пока штатный Workflow уже выражает требование.

Граница: эта семантика корректна именно потому, что CORE заранее зафиксировал `requester = owner`.

---

# 12. Rejected не равен Cancelled

`Rejected` означает отрицательное решение на draft-стадии:

```text
PR Rejected → docstatus 0
```

В CORE Rejected-заявку можно исправить и снова направить:

```text
Rejected
→ Purchase Requester edits
→ Submit for Review
→ Pending Manager
```

Это явно заданный Workflow transition, а не ручная запись произвольного status.

`Cancelled` появляется только после отдельного требования отмены ранее Submitted факта.

---

# 13. Final approval становится зафиксированным фактом

Новое требование:

> После окончательного approval сумма, назначение и срок считаются согласованным разрешением. Их нельзя незаметно переписать обычным Save.

Теперь `Approved` — не просто workflow-state.

Появляется:

```text
Is Submittable
```

и mapping:

```text
Draft            → docstatus 0
Pending Manager  → docstatus 0
Pending Senior   → docstatus 0
Rejected         → docstatus 0
Approved         → docstatus 1
```

`Cancelled` здесь ещё не добавляется: способность зафиксировать факт не создаёт автоматически обязанность его отменять.

## Submittable автоматически приносит amended_from

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** `DocType.validate()` вызывает `make_amendable()`. Если `is_submittable=1`, Framework сам добавляет Standard field:

```text
Amended From
fieldname = amended_from
fieldtype = Link
options   = Purchase Request
read_only = yes
no_copy   = yes
```

если такого field ещё нет.

Практикум не создаёт `amended_from` вручную.

Но важно различать:

```text
Framework добавил capability metadata
≠
бизнес уже потребовал Amend
≠
роль уже получила Amend permission
```

Amend responsibility появится только отдельным требованием позже.

## Submit permission появляется только вместе с submit responsibility

Workflow transition role сам по себе не выдаёт системное право `submit()`.

Маленькую заявку финально одобряет `Purchase Approver`, большую — `Senior Purchase Approver`, поэтому:

```text
Purchase Approver        → Submit yes
Senior Purchase Approver → Submit yes
Purchase Requester       → Submit no
```

`Cancel` и `Amend` ещё не выдаются.

Это показывает два уровня:

```text
DocPerm
→ можно ли выполнить системную Document operation

Workflow transition
→ допустимо ли это процессное действие из текущего state
```

---

# 14. Отмена Submitted факта — отдельное требование

Новое требование:

> Уже одобренное разрешение иногда нужно официально отменить, не удаляя и не возвращая его в Draft.

Теперь появляется:

```text
PR Cancelled → docstatus 2
Approved → Cancelled Workflow transition
```

и только необходимый `Cancel` DocPerm:

```text
Purchase Approver        → Cancel yes
Senior Purchase Approver → Cancel no
Purchase Requester       → Cancel no
```

Почему именно так:

```text
Purchase Approver
→ владеет отменой Approved разрешения

Senior Purchase Approver
→ отвечает только за дополнительный final approval дорогой заявки
```

Для нового Cancelled state на этом шаге `Only Allow Edit For` соответствует текущей ответственности:

```text
Cancelled → Purchase Approver
```

Также именно здесь `status` получает `Allow on Submit = yes`, потому что Workflow должен изменить state field при переходе уже Submitted документа в Cancelled.

Нелегальные переходы не проектируются:

```text
Draft → Cancelled
Submitted → Draft
Cancelled → другой state
```

Текущий Frappe `apply_workflow()` в зависимости от `Doc Status` следующего Workflow State вызывает обычные:

```text
save()
submit()
cancel()
```

---

# 15. Ошибка после Cancel → отдельная Amend responsibility

Следующее требование:

> После отмены requester должен создать исправленную версию, сохранив связь с исходным фактом.

Первый штатный путь:

```text
Cancel original
→ Amend
→ новый исправленный Document
```

Ответственности разделены:

```text
Purchase Approver
→ Cancel original

Purchase Requester
→ Amend cancelled original
→ исправляет новый Draft
→ снова отправляет его по Workflow
```

Только здесь появляется:

```text
Purchase Requester       → Amend yes
Purchase Approver        → Amend no
Senior Purchase Approver → Amend no
```

У Requester уже есть `Create=yes`, необходимый для нового amended Document.

Одновременно state/edit policy эволюционирует из нового требования:

```text
Cancelled → Purchase Requester
```

а не назначается Requester заранее в момент появления Cancelled.

`amended_from` уже присутствует в Standard metadata как штатное следствие `Is Submittable`.

Практикум обязан фактически проверить Amend при активном Workflow, а не предположить его поведение.

В Desk Frappe создаёт amendment как новый local Document с `docstatus = 0`; workflow UI для local Documents устанавливает default state текущего docstatus. Поэтому ожидаемый пользовательский результат:

```text
Cancelled original
→ Requester Amend
→ новый Draft-state Document
→ amended_from указывает на исходный
```

Важно: `No Copy` не выдаётся за механизм сброса state при Amend — Desk copy path при `from_amend` имеет собственную семантику. Если реальное поведение версии отличается, практикум фиксирует наблюдение и пересматривает решение, а не добавляет магический workaround заранее.

---

# 16. Workflow — App-owned configuration

Обязательный процесс не может существовать только потому, что его один раз настроили на dev-site.

Source of truth:

```text
Purchase Request schema + status + amended_from + DocPerm
→ Standard DocType metadata

обязательные Role records из этих DocPerm
→ создаются Frappe при Standard DocType sync
→ Role fixtures текущему CORE не нужны

PR-* Workflow State records
→ filtered Workflow State fixture

Workflow + child states/transitions/conditions
→ filtered Workflow fixture

test Users
→ Site-local data

runtime Workflow Actions
→ Site runtime data, не fixture
```

## Почему не Role fixture

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** `DocType.make_module_and_roles()` при install/sync берёт роли из Standard DocType permissions и создаёт отсутствующие Role records с `desk_access=1`.

В этом практикуме все три обязательные роли уже принадлежат Purchase Request DocPerm и не требуют дополнительных нестандартных свойств.

Поэтому:

```text
DocPerm metadata
→ один source обязательных role names
→ Framework создаёт Role
```

Отдельный fixture тех же ролей создавал бы дублирующий delivery mechanism без новой ответственности.

Если позже появится необходимость поставлять дополнительные свойства Role, fixture анализируется заново.

## Порядок fixtures — часть delivery contract

После удаления лишнего Role fixture порядок проще:

```text
Workflow State
→ Workflow
```

Frappe v16 импортирует fixture files в сортированном порядке имён, поэтому будущая исполняемая спецификация обязана обеспечить этот порядок штатным ordering/prefix mechanism. Первый кандидат:

```text
fixture_auto_order = True
+
fixtures hook:
1. Workflow State
2. Workflow
```

Нельзя экспортировать все системные Workflow/Workflow State текущего Site.

## Workflow State namespace к delivery уже выбран

Точные App-owned records определены раньше, до создания базового Workflow:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
PR Pending Senior
PR Cancelled
```

Delivery не принимает это решение заново, а только воспроизводит уже принятую обязательную конфигурацию.

---

# 17. Автоматические контракты обязательны

Второй практикум не завершается фразой «покликали Workflow — работает».

Минимальные серверные контракты:

```text
Requester может Draft → Pending Manager
Requester не может Approve
Approver может Approve/Reject
маленькая сумма не требует Senior
большая сумма идёт в Pending Senior
Senior завершает большой approval
self approval блокируется на apply_workflow
Rejected остаётся docstatus 0
Rejected можно исправить и повторно отправить
final Approved становится docstatus 1
Requester не имеет Submit/Cancel
Purchase Approver имеет Submit/Cancel
Senior Purchase Approver имеет Submit, но не Cancel
Requester имеет Amend после появления Amend responsibility
Approver/Senior не получают Amend без требования
Draft нельзя сразу Cancel
Purchase Approver может Approved → Cancelled
Cancelled становится docstatus 2
Cancelled не переходит дальше
status остаётся одним Standard Select
обязательные Role records существуют после Standard DocType sync
```

Отдельные observed/UI checks:

```text
Only Allow Edit For отражается в Desk ожидаемым образом
Workflow Action отображается согласно permitted roles
Requester Amend создаёт новую draft-запись, связанную через amended_from
```

Так мы не выдаём UI/state policy за неподтверждённую серверную ACL.

`amended_from` не тестируется как внутренний unit-test Frappe, но его наличие проверяется на delivery/acceptance границе, потому что наш native Amend scenario от него зависит.

---

# 18. Clean Site acceptance — финальный gate CORE

Финал должен доказать:

```text
чистый совместимый Frappe Site
+ второй App из committed source
+ install-app / migrate
+ Standard Purchase Request metadata/DocPerm/amended_from
+ missing Role records созданы штатным DocType sync
+ ordered filtered Workflow State / Workflow fixtures
+ mandatory Workflow configuration
+ automated tests
+ реальный requester/approver/senior scenario
+ Cancel / Amend observed path
= воспроизводимый lifecycle
```

На новом Site нельзя вручную:

```text
создавать обязательные Roles
создавать Workflow States
создавать Workflow
добавлять workflow_state Custom Field
добавлять amended_from вручную
```

Site-local остаются:

```text
test Users
runtime Purchase Requests
runtime Workflow Actions
пароли
local test config
```

Это acceptance Frappe App, а не production deployment test.

---

# 19. NEXT — операционные спутники

Они не входят в обязательный lifecycle CORE автоматически.

## NEXT-A — Assignment / ToDo

Требование-кандидат:

> После approval конкретный сотрудник должен выполнить закупку.

Первый механизм — `Assignment / ToDo`.

## NEXT-B — Notification

Требование-кандидат:

> За два дня до `needed_by` нужно напомнить ответственному.

Первый механизм — date-based `Notification`, но с явной scheduler dependency.

Notification не дублирует Workflow Action/Workflow email или Assignment notification.

## NEXT-C — File / Comment / Version

```text
приложить документ
→ File / Attach

обсудить
→ Comment / Timeline

увидеть обычную историю изменений
→ Track Changes / Version
```

## NEXT-D — Print

Сначала проверяется Standard Print View, затем при реальной недостаточности — `Print Format`.

---

# 20. GATE — только после нового требования

## D00. Эволюция dev/test данных

После аудита обязательной смены типа `status Select → Link` нет и поздней миграции generic state names в App-scoped names тоже нет: namespace выбран с первого status.

Учебная модель всё равно эволюционирует:

```text
добавляется PR Pending Senior
Approved меняет процессную семантику с draft-state на docstatus 1
Frappe добавляет amended_from при Is Submittable
добавляется PR Cancelled
```

Disposable control records dev/test Site можно явно пересоздать штатным Document-путём. Это не повод писать фиктивный patch.

Поддерживаемая production-версия с реальными данными потребовала бы отдельного migration analysis.

## D01. Allow on Submit для отдельного business field

Только если появляется безопасное пост-фактическое поле, например внешний номер заказа.

Это не относится к `status`, которому `Allow on Submit` нужен технически для workflow cancel-path.

## D02. Requester перестал совпадать с owner

Появляется отдельное предметное поле requester и заново анализируется self-approval policy.

## D03. LIMIT должен менять администратор

Первый кандидат для одного Site-level значения — `Single DocType` Settings.

## D04. Approval route стал динамическим

Если маршрут зависит от множества документов/организаций/внешних решений и перестаёт естественно выражаться Workflow states/transitions/conditions, выполняется новый architectural fit analysis. Только тогда рассматривается отдельная предметная модель/код.

---

# 21. Что намеренно вне второго CORE

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

# 22. Доказательная база текущей версии

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Workflow создаёт Custom Field состояния только если указанного field нет в Meta:

- `frappe/workflow/doctype/workflow/workflow.py`

Автоматически создаваемое поле имеет `Link → Workflow State`, `allow_on_submit=1` и `no_copy=1`. Это показывает fallback Framework, но не означает, что существующее Standard state field обязано менять тип на Link.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** `Workflow Document State`:

- `frappe/workflow/doctype/workflow_document_state/workflow_document_state.json`

`allow_edit` является обязательным полем конфигурации state. В этом практикуме оно рассматривается как штатная state/edit policy, но не используется как единственная доказанная серверная защита критического инварианта.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** `apply_workflow()` и self approval:

- `frappe/model/workflow.py`

`apply_workflow()` вызывает `save()`, `submit()` или `cancel()` согласно `Doc Status` следующего Workflow State; self approval сравнивается с `doc.owner`.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Workflow Action:

- `frappe/workflow/doctype/workflow_action/workflow_action.py`

Workflow Action хранит permitted roles; фактический transition дополнительно проверяется серверным Workflow.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Standard DocType Role provisioning и Amend metadata:

- `frappe/core/doctype/doctype/doctype.py`

`make_module_and_roles()` создаёт отсутствующие Role из Standard DocType permissions; `make_amendable()` добавляет `amended_from` при `Is Submittable`.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** fixtures:

- `frappe/utils/fixtures.py`

Fixture files импортируются в сортированном порядке; `fixture_auto_order` позволяет экспортировать их с последовательными префиксами по порядку hook `fixtures`.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Workflow state UI и Amend copy:

- `frappe/public/js/frappe/form/workflow.js`
- `frappe/public/js/frappe/model/create_new.js`
- `frappe/public/js/frappe/form/form.js`

Local Document получает default Workflow state по своему docstatus; Amend использует отдельный `from_amend` copy path, поэтому его поведение проверяется явно.

Внутренний стандарт:

- [`03_DOCUMENT_LIFECYCLE.md`](../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md)
- [`04_SECURITY.md`](../frappe-architecture-standard/04_SECURITY.md)
- [`05_TRANSACTIONS_ASYNC.md`](../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md)
- [`09_DEPLOYMENT_TESTING.md`](../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md)
- [`10_DECISION_STANDARD.md`](../frappe-architecture-standard/10_DECISION_STANDARD.md)

---

# 23. Критерий принятия паспорта

Перед roadmap должны быть подтверждены все пункты:

```text
1. Purchase Request создаёт реальную lifecycle-задачу.
2. Requester = owner явно ограничен CORE и не связан ложной зависимостью с status.
3. status появляется раньше Workflow.
4. physical state values App-scoped до создания Workflow State records.
5. Workflow не появляется только из-за количества status values.
6. после Workflow остаётся один Standard state field.
7. status не меняет тип без реальной необходимости.
8. Workflow не создаёт обязательный site-local workflow_state Custom Field.
9. Only Allow Edit For задан осознанно и не выдан за неподтверждённую server ACL.
10. Workflow Action не выдаётся за окончательную ACL.
11. Senior role/state появляются только из amount-based requirement.
12. self approval использует штатную owner-based семантику.
13. Rejected остаётся docstatus 0 и имеет явный путь повторной отправки.
14. Approved становится docstatus 1 только после требования о фиксации факта.
15. Is Submittable автоматически добавляет amended_from, но не выдаёт Amend responsibility.
16. Submit, Cancel и Amend появляются из трёх разных обязанностей.
17. Senior не получает Cancel/Amend «на всякий случай».
18. Cancelled edit-policy меняется только при появлении Requester Amend responsibility.
19. Workflow полностью описывает submit/cancel path.
20. Amend проверяется фактически при активном Workflow.
21. Role fixtures не дублируют роли, которые Framework уже создаёт из Standard DocPerm.
22. Workflow State / Workflow fixtures имеют доказанный dependency order.
23. server lifecycle contracts автоматизированы.
24. UI/state policies проверяются отдельно от server security contracts.
25. Clean Site acceptance не требует ручной настройки процесса.
26. NEXT не перегружает обязательный lifecycle CORE.
27. API/async/extension/integration не добавлены ради покрытия.
```

Если какой-то пункт не подтверждён, сначала исправляется архитектура. Roadmap строится только после прохождения dependency graph gate.