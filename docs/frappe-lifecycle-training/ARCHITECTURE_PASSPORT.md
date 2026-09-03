# Архитектурный паспорт второго учебного практикума Frappe

Статус: **черновик после аудита матрицы требований**.

Этот практикум является второй отдельной ступенью после принятого [`docs/frappe-training`](../frappe-training/ARCHITECTURE_PASSPORT.md), но не продолжает его предметную область и не зависит от `rental_training`.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md). Если учебное решение конфликтует со стандартом или актуальным Frappe v16, исправляется практикум.

Формализованный слой требований — [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md).

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
Cancel / Amend
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

---

# 6. Сначала — обычное business state

Первое требование:

> Пользователь должен понимать, где находится заявка.

Для этого сначала достаточно обычного Standard поля:

```text
status : Select
```

Начальная семантика:

```text
Draft
Pending Manager
Approved
Rejected
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

`Workflow State` records всё равно нужны самому Workflow; значения `status` должны соответствовать принятым состояниям процесса.

Когда Workflow становится владельцем процесса, для `status` дополнительно фиксируется `No Copy = yes`, чтобы обычное дублирование документа не переносило текущий workflow-state как новый стартовый state.

Когда Purchase Request позднее становится Submittable, для этого же state field отдельно проверяется/включается `Allow on Submit`, поскольку workflow-state должен корректно участвовать в Submitted lifecycle. Это не разрешает пользователю обходить Workflow: допустимость перехода по-прежнему проверяет Workflow.

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

## Only Allow Edit For — не случайная колонка

Каждая строка `Workflow Document State` в текущем Frappe требует `Only Allow Edit For` (`allow_edit`). Поэтому будущая спецификация обязана выбрать эту роль осознанно.

Baseline:

```text
Draft           → Purchase Requester
Pending Manager → Purchase Approver
Rejected        → Purchase Requester
Pending Senior  → Senior Purchase Approver   # появляется позднее
Approved        → Purchase Approver
Cancelled       → Purchase Approver
```

`allow_edit` не заменяет DocType Permissions и не заменяет transition role. Это отдельная часть state policy.

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
Pending Senior
```

и реальная причина использовать `Condition` перехода Workflow.

Смысл:

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
Rejected → docstatus 0
```

В CORE Rejected-заявку можно исправить и снова направить:

```text
Rejected
→ Purchase Requester edits
→ Submit for Review
→ Pending Manager
```

Это явно заданный Workflow transition, а не ручная запись произвольного status.

`Cancelled` появляется только после того, как Document уже имеет Submitted-семантику.

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
Cancelled        → docstatus 2
```

`Cancelled` добавляется в набор состояний только здесь.

Одновременно меняется базовая permission-модель: Workflow transition role сам по себе не выдаёт право `submit` или `cancel`.

Поэтому роли, которые выполняют final Approve, получают необходимый `Submit` DocPerm, а роли, которые выполняют Cancel, получают необходимый `Cancel` DocPerm.

В учебном baseline эти права получают:

```text
Purchase Approver
Senior Purchase Approver
```

Requester их не получает.

Это специально показывает два уровня:

```text
DocPerm
→ можно ли выполнить системную Document operation

Workflow transition
→ допустимо ли это процессное действие из текущего state
```

---

# 14. Workflow полностью описывает submit/cancel path

После `Is Submittable` нельзя одновременно считать владельцами процесса и Workflow, и произвольные ручные кнопки Submit/Cancel.

Workflow должен иметь допустимые transitions, которые реально приводят к:

```text
Approved  → docstatus 1
Cancelled → docstatus 2
```

Текущий Frappe `apply_workflow()` в зависимости от `Doc Status` следующего Workflow State вызывает обычные:

```text
save()
submit()
cancel()
```

Нелегальные переходы не проектируются:

```text
Draft → Cancelled
Submitted → Draft
Cancelled → другой state
```

`Workflow State` и `docstatus` остаются разными понятиями, хотя один transition может изменить оба.

---

# 15. Ошибка после submit → Cancel / Amend

Если после final approval обнаружена ошибка, меняющая смысл согласованного разрешения, обычный Edit не подходит.

Первый штатный путь:

```text
Cancel
→ Amend
→ новый исправленный Document
```

Практикум обязан фактически проверить Amend при активном Workflow, а не предположить его поведение.

В Desk Frappe создаёт amendment как новый local Document с `docstatus = 0`; workflow UI для local Documents устанавливает default state текущего docstatus. Поэтому ожидаемый пользовательский результат:

```text
Cancelled original
→ Amend
→ новый Draft-state Document
→ amended_from указывает на исходный
```

Важно: `No Copy` не выдаётся за механизм сброса state при Amend — Desk copy path при `from_amend` имеет собственную семантику. Если реальное поведение версии отличается, практикум фиксирует наблюдение и пересматривает решение, а не добавляет магический workaround заранее.

---

# 16. Workflow — App-owned configuration

Обязательный процесс не может существовать только потому, что его один раз настроили на dev-site.

Source of truth:

```text
Purchase Request schema + status field
→ Standard DocType metadata

Roles
→ filtered Role fixtures

Workflow State records
→ filtered fixtures

Workflow + child states/transitions/conditions
→ filtered Workflow fixture

test Users
→ Site-local data

runtime Workflow Actions
→ Site runtime data, не fixture
```

## Порядок fixtures — часть delivery contract

Frappe v16 импортирует fixture files в сортированном порядке имён файлов. Обычные имена дали бы:

```text
role.json
workflow.json
workflow_state.json
```

то есть Workflow мог бы импортироваться раньше Workflow State, на которые он ссылается.

Поэтому будущая исполняемая спецификация обязана зафиксировать штатный порядок:

```text
Role
→ Workflow State
→ Workflow
```

через поддерживаемый механизм fixture ordering/prefix. В v16 для этого доступен `fixture_auto_order` и порядок записей hook `fixtures`.

Нельзя экспортировать все системные Role/Workflow/Workflow State текущего Site.

Отдельная граница: `Workflow State.workflow_state_name` уникален на весь Site. Точные имена состояний в спецификации должны либо быть безопасно namespaced для учебного App, либо их намеренное совместное использование должно быть явно доказано. Случайно «захватывать» глобальную запись другого App нельзя.

---

# 17. Автоматические контракты обязательны

Второй практикум не завершается фразой «покликали Workflow — работает».

Минимальные контракты:

```text
Requester может Draft → Pending Manager
Requester не может Approve
Approver может Approve/Reject
Requester не может обычным Edit менять Pending Manager, если state policy этого не разрешает
маленькая сумма не требует Senior
большая сумма идёт в Pending Senior
Senior завершает большой approval
self approval блокируется на apply_workflow
Rejected остаётся docstatus 0
Rejected можно исправить и повторно отправить
final Approved становится docstatus 1
Requester не имеет submit/cancel permission
Approver roles имеют нужный submit/cancel permission
Draft нельзя сразу Cancel
Submitted можно Cancel только допустимым Workflow transition
Cancelled становится docstatus 2
Cancelled не переходит дальше
Amend создаёт новую draft-запись, связанную через amended_from
```

Тестируется собственная конфигурация процесса и её интеграция с Frappe lifecycle, а не внутренности Framework ради coverage.

---

# 18. Clean Site acceptance — финальный gate CORE

Финал должен доказать:

```text
чистый совместимый Frappe Site
+ второй App из committed source
+ install-app / migrate
+ ordered filtered fixtures
+ mandatory Workflow configuration
+ automated tests
+ реальный requester/approver scenario
= воспроизводимый lifecycle
```

На новом Site нельзя вручную:

```text
создавать обязательные Roles
создавать Workflow States
создавать Workflow
добавлять workflow_state Custom Field
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

После аудита обязательной смены типа `status Select → Link` больше нет.

Учебная модель всё равно эволюционирует:

```text
добавляется Pending Senior
добавляется Cancelled
Approved меняет процессную семантику с draft-state на docstatus 1
```

Disposable control records dev/test Site можно явно пересоздать штатным Document-путём. Это не повод писать фиктивный patch.

Поддерживаемая production-версия с реальными данными потребовала бы отдельного migration analysis.

## D01. Allow on Submit для отдельного business field

Только если появляется безопасное пост-фактическое поле, например внешний номер заказа.

Это не относится к `status`, которому `Allow on Submit` может быть нужен технически как workflow-state field.

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

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** `apply_workflow()` и self approval:

- `frappe/model/workflow.py`

`apply_workflow()` вызывает `save()`, `submit()` или `cancel()` согласно `Doc Status` следующего Workflow State; self approval сравнивается с `doc.owner`.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Workflow Action:

- `frappe/workflow/doctype/workflow_action/workflow_action.py`

Workflow Action хранит permitted roles; фактический transition дополнительно проверяется серверным Workflow.

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

Перед dependency graph должны быть подтверждены все пункты:

```text
1. Purchase Request создаёт реальную lifecycle-задачу.
2. Requester = owner явно ограничен CORE.
3. status появляется раньше Workflow.
4. Workflow не появляется только из-за количества status values.
5. После Workflow остаётся один Standard state field.
6. status не меняет тип без реальной необходимости.
7. Workflow не создаёт обязательный site-local workflow_state Custom Field.
8. Only Allow Edit For задан осознанно для каждого state.
9. Workflow Action не выдаётся за окончательную ACL.
10. Senior role/state появляются только из amount-based requirement.
11. self approval использует штатную owner-based семантику.
12. Rejected остаётся docstatus 0 и имеет явный путь повторной отправки.
13. Approved становится docstatus 1 только после требования о фиксации факта.
14. Submit/Cancel DocPerm не смешаны с transition roles.
15. Workflow полностью описывает submit/cancel path.
16. Amend проверяется фактически при активном Workflow.
17. App-owned fixtures имеют доказанный dependency order.
18. Workflow State global namespace не игнорируется.
19. Lifecycle contracts автоматизированы.
20. Clean Site acceptance не требует ручной настройки процесса.
21. NEXT не перегружает обязательный lifecycle CORE.
22. API/async/extension/integration не добавлены ради покрытия.
```

Если какой-то пункт не подтверждён, сначала исправляется архитектура. Dependency graph строится только после этого.
