# Архитектура практикума

## 1. Базовый закон курса

Практикум не строится от списка функций Frappe.

```text
реальная задача
→ ответственность
→ минимальная модель продукта
→ Frappe primitive с подходящей семантикой
→ официальный extension point, если primitive уже недостаточен
→ custom abstraction только при новой самостоятельной ответственности
```

Отсюда два одинаково важных запрета:

```text
не изобретать второй Framework поверх Frappe
не объявлять любой Python «ненативным»
```

Нативность определяется владельцем ответственности, а не количеством строк кода.

---

# 2. Почему три приложения, а не один учебный комбайн

Один app, в который ради coverage последовательно добавляют Tree, Workflow, Web Form,
Auto Repeat и специальные поля, быстро перестаёт быть продуктом. Его domain model
начинает обслуживать учебную матрицу.

Поэтому Metadata Track состоит из трёх самостоятельных приложений:

```text
P1 equipment_register
→ data model / registry

P2 purchase_requests
→ lifecycle / approval

P3 service_intake
→ trust boundary / web intake
```

Функция Framework появляется только тогда, когда естественно нужна одному из продуктов.

---

# 3. Физическая архитектура стенда

```text
Frappe Bench
├── equipment_register ──► equipment.localhost
├── purchase_requests  ──► purchase.localhost
└── service_intake     ──► intake.localhost
```

Clean-site acceptance:

```text
equipment-clean.localhost
purchase-clean.localhost
intake-clean.localhost
```

Ни один учебный app не зависит от другого.

Engineering Bridge продолжает `service_intake` после принятого P3 и дополнительно
проверяет:

```text
upgrade existing intake.localhost
+
clean install new version
```

Это разные deployment scenarios.

---

# 4. Единица обучения

Единица обучения — законченный инженерный шаг:

```text
проблема
→ кто владеет гарантией
→ решение
→ действие
→ positive test
→ negative test
→ граница механизма
→ source/site/deployment check
```

Например, Link изучается не как пункт меню. Сначала появляется Equipment, которому нужен
существующий Category; затем Link; затем negative Link test; затем проверка metadata в
source.

Controller появляется так же: сначала обнаруживается cross-document правило, которого
нет в metadata, и только после этого пишется `validate`.

---

# 5. P1 — `equipment_register`

## Модель

```text
Equipment Location (Tree) ◄──── Equipment ────► Equipment Category
                                      │
                                      └──── Equipment Identifier (Child)
```

## Ownership решений

- `Equipment Location` → Tree, потому что location имеет hierarchy.
- `Equipment Category` → normal DocType, потому что значение переиспользуется и имеет собственную identity/integrity.
- `Equipment Identifier` → Child Table, потому что строка не имеет самостоятельного lifecycle/permissions/workspace.
- `asset_code` → naming source; отдельный duplicate identity layer не создаётся.
- `status` → Select, потому что это состояние объекта без approval transition model.
- Kanban → presentation/edit surface обычного status, не альтернативный permission model.
- Track Changes → штатная история изменений вместо custom history registry.

Workflow в P1 не нужен. Его отсутствие — архитектурное решение, а не пробел курса.

---

# 6. P2 — `purchase_requests`

## Модель

```text
Purchase Department ◄──── Purchase Request
                               │
                               └──── Purchase Request Item (Child)
```

## Lifecycle

```text
Draft
  └─ Submit Request ─► Pending Department Approval
                         ├─ Approve ─► Procurement Review
                         └─ Reject  ─► Rejected

Rejected ── Resubmit ─► Pending Department Approval

Procurement Review
  ├─ Approve Purchase ─► Approved (docstatus 1)
  └─ Return           ─► Rejected

Approved ── Cancel ─► Cancelled (docstatus 2)
```

## Ownership решений

- `Purchase Request` → submittable, потому что Approved становится зафиксированным деловым документом.
- Workflow → допустимые business transitions и связанный docstatus.
- DocPerm → базовый access независимо от Workflow.
- Permission Level → field-level authority для decision/procurement notes.
- User Permission → ограничение по Department, а не новый ACL framework.
- Assign To / ToDo → конкретный ответственный, не authorization.
- Print Format → представление Approved document, не отдельная модель.

```text
business state
Workflow transition
docstatus
permission
assignment
```

в P2 изучаются как разные семантики, даже когда участвуют в одном процессе.

---

# 7. P3 — `service_intake`

## Trust model

```text
Internet / Website User
        │
        ▼
Web Form
        │
        ▼
Service Intake        untrusted input
        │ manual triage
        ▼
Service Case          internal document
        │
        └────► Service Category
```

## Почему два DocType

В `v16.32.0` Web Form создаёт новый target Document специальным path с
`ignore_permissions=True`.

Направить публичную форму сразу в `Service Case` означало бы связать untrusted channel с
внутренними fields, permissions и lifecycle.

Разделение оправдано разными ответственностями:

```text
Service Intake
→ принимает минимальный непроверенный ввод

Service Case
→ живёт во внутреннем permission/workflow контуре
```

Это не дублирование одного объекта двумя таблицами, а настоящая trust/lifecycle boundary.

P3 намеренно заканчивается **ручным** созданием Case после триажа. Пока курс запрещает
business Python, это честная граница возможностей metadata.

---

# 8. Engineering Bridge — где code становится нативным решением

После P3 появляется новое требование:

```text
Accepted Intake
→ создать Case одной server command
→ гарантировать Accepted source
→ записать converted_at
→ не оставить частичное изменение при ошибке
```

Разбор ownership:

| Требование | Владелец |
|---|---|
| source существует | Link |
| один Case на Intake | Unique |
| source нельзя перепривязать | Set Only Once |
| source обязан быть Accepted | `ServiceCase.validate` |
| действие «convert Intake to Case» | whitelisted `ServiceIntake` Document method |
| Create permission на Case | permission-aware `case.insert()` |
| атомарность Case + Intake + Comment | request transaction Frappe |
| новое поле на всех installations | Standard DocType JSON |
| backfill старых records | patch |
| защита custom behavior от regression | integration tests |

Ни одна строка Python не должна повторять гарантию, которой уже владеет metadata.

---

# 9. Почему semantic command живёт в Controller

`create_case` относится к одному конкретному `Service Intake` и использует его state.
Поэтому controller — естественный владелец.

Не создаётся:

```text
CaseRepository
CaseFactoryService
ServiceIntakeManager
```

если они лишь переименуют `frappe.new_doc`, `insert` и `save`.

Отдельный service/module становится оправданным, если появляется реальная
cross-document orchestration, сложный reusable algorithm или external protocol, а не
потому, что «business logic должна жить в services».

---

# 10. Transaction architecture

В write HTTP request Framework управляет transaction boundary:

```text
successful request
→ commit

uncaught exception
→ rollback
```

Поэтому `create_case` не делает manual `frappe.db.commit()`.

```text
Case insert
Intake converted_at update
Timeline Comment
```

составляют одну business operation.

Engineering Lab временно бросает exception после `case.insert()` и доказывает отсутствие
частичного Case после rollback.

External/slow side effect не надо выполнять до уверенности, что business transaction
зафиксирована. Для будущей background work существует `enqueue_after_commit=True`.

---

# 11. Migration architecture

Schema evolution и data migration разделены:

```text
DocType JSON
→ поле converted_at существует в новой модели

post_model_sync patch
→ старые Intakes получают значение из уже существующих Cases
```

В patch допустим deliberate direct DB update, потому что это one-off migration, где
обычный current-document lifecycle не является целью.

Это не превращает `frappe.db.set_value` в рекомендуемый business CRUD path.

---

# 12. Async and integration boundary

Current `service_intake` не имеет реальной долгой операции, поэтому custom Background
Job в продукт не добавляется.

Решение выбирается по требованию:

```text
simple configurable outbound HTTP event
→ Webhook first

slow/heavy internal work after successful write
→ Background Job + enqueue_after_commit

synchronous invariant/current Document mutation
→ Controller lifecycle

complex multi-system protocol/orchestration
→ integration module/service when responsibility appears
```

Умение **не создать queue без задачи** является частью архитектурной приёмки.

---

# 13. Extension of other apps

Три учебных app в основном владеют своими DocType, поэтому собственное поведение живёт в
controllers.

Для чужого DocType архитектурный выбор был бы другим:

```text
react to document event
→ doc_events

add behavior without taking full ownership
→ extension seam such as extend_doctype_class when supported by pinned version

complete override
→ только при доказанной необходимости и с пониманием composition conflicts
```

Эти механизмы не внедряются искусственно в текущие продукты и остаются следующим
практическим блоком.

---

# 14. Модель поставки

Четыре слоя:

```text
1. Standard source
   DocType JSON, controllers, Workspace, Report, Web Form, Notification

2. portable configuration
   Roles, Workflow, shared view/config records

3. local site configuration
   Users, Assignment Rule with Users, User Permission, SMTP, API keys

4. working data
   Equipment, Purchase Request, Service Intake, Service Case, Files
```

Engineering Bridge добавляет:

```text
5. evolution path
   patches + tests for upgrade
```

Git содержит product source и осознанно выбранную portable configuration. Working data и
secrets не выдаются за product source.

---

# 15. Что сознательно не моделируется

Не создаются универсальные `Status`, `Priority`, `Person`, `Team`, `Attachment` и другие
справочники «на будущее».

Dynamic Link не используется там, где target известен.

Не создаются service/repository/background job/custom API только ради архитектурного
coverage.

Принцип:

```text
механизм известен
≠ механизм обязан быть использован
```

---

# 16. Финальный критерий

Для каждого элемента курса должны существовать ответы:

1. Какую реальную ответственность он решает?
2. Почему именно этот Frappe layer ей владеет?
3. Какая проверка доказывает гарантию?
4. Где заканчивается семантика этого механизма?
5. Что произойдёт при clean install и при upgrade?

Если ответа нет, элемент не должен оставаться в архитектуре курса.
