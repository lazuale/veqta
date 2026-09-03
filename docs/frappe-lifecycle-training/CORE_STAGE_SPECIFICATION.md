# Исполняемая спецификация второго CORE-практикума Frappe

Статус: **проект точной спецификации после аудита roadmap; до executable exercises требуется отдельный аудит этого документа**.

Этот документ превращает архитектурные решения второго практикума в однозначный технический contract.

Обязательные входные документы:

1. [`ARCHITECTURE_CORRECTIONS.md`](ARCHITECTURE_CORRECTIONS.md);
2. [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md);
3. [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md);
4. [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md);
5. [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md);
6. [`ROADMAP_AUDIT.md`](ROADMAP_AUDIT.md).

Нормативная база:

- [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md);
- [`13_ROLE_PROVISIONING.md`](../frappe-architecture-standard/13_ROLE_PROVISIONING.md).

Pinned Framework baseline:

```text
Frappe Framework v16.33.0
```

Если фактический v16.33.0 расходится с этой спецификацией, исправляется спецификация; workaround заранее не придумывается.

---

# 1. Назначение спецификации

После этого документа у исполняемых S00–S10 больше не должно оставаться произвольных решений вида:

```text
«назовите App как-нибудь»
«выберите любую роль»
«укажите какой-нибудь лимит»
«настройте Workflow примерно так»
«проверьте на нескольких заявках»
```

Спецификация фиксирует:

```text
App / Module / Sites
DocType
fields
naming
roles
DocPerm
Workflow State names
Workflow Action Master names
Workflow
states
transitions
conditions
self-policy
LIMIT
docstatus mapping
Cancel / Amend policy
fixtures
control Users
control Documents
test contracts
clean-site acceptance
```

Она не является пошаговым учебным текстом. Это точный contract для будущих executable exercises.

---

# 2. Граница среды

Второй практикум **не повторяет установку Frappe с нуля**.

Используется совместимый Bench из первого CORE. В командах будущих упражнений baseline-путь:

```text
~/frappe/rental-training-bench
```

Имя Bench-папки исторически связано с первым практикумом, но второй App от `rental_training` не зависит.

На dev Site второго практикума должны быть установлены только:

```text
frappe
purchase_lifecycle_training
```

`rental_training` может физически находиться в `apps/` того же Bench, но на этом Site не устанавливается.

Это снова доказывает:

```text
App доступен Bench
≠
App установлен на Site
```

---

# 3. Точные имена App / Module / Sites

## App

```text
App package : purchase_lifecycle_training
App title   : Purchase Lifecycle Training
```

Почему отдельный App:

```text
второй практикум
→ отдельная предметная модель
→ отдельный installable source boundary
```

Он не расширяет `rental_training` и не импортирует его модели.

## Module

```text
Purchase Lifecycle Training
```

Module используется как Frappe grouping внутри App, а не как отдельная архитектурная граница.

## Dev Site

```text
purchase-lifecycle.localhost
```

На нём:

```text
developer_mode = 1
```

Site-local, не global Bench setting.

## Acceptance Site

```text
purchase-lifecycle-acceptance.localhost
```

На нём:

```text
developer_mode не включается
```

`allow_tests` может быть включён Site-local только для test runner.

---

# 4. Namespace продукта

Frappe setup records вроде `Role`, `Workflow State`, `Workflow` и `Workflow Action Master` живут в общей БД Site и не принадлежат namespace Python package автоматически.

Для второго практикума фиксируется короткий продуктовый prefix:

```text
PLT = Purchase Lifecycle Training
```

Он используется там, где запись является App-specific глобальной конфигурацией.

## App-specific Role names

```text
PLT Requester
PLT Approver
PLT Senior Approver
```

## App-specific Workflow State names

```text
PLT Draft
PLT Pending Approval
PLT Rejected
PLT Pending Senior
PLT Approved
PLT Cancelled
```

## Workflow

```text
PLT Purchase Request Approval
```

## App-specific Workflow Action Master

```text
PLT Submit for Review
PLT Cancel Request
```

Frappe-owned standard Action Masters:

```text
Approve
Reject
```

не экспортируются нашим App: они являются базовыми records Frappe v16.33.0.

### Diagram aliases

В поясняющих схемах разрешены короткие aliases:

```text
Draft
Pending Approval
Rejected
Pending Senior
Approved
Cancelled
```

Но persisted values и fixture filters используют только точные `PLT ...` names.

---

# 5. Центральный DocType

```text
DocType      : Purchase Request
Module       : Purchase Lifecycle Training
Standard     : yes
Child        : no
Single       : no
Submittable  : no на S01–S05; yes начиная с S06
Track Changes: не требуется CORE
```

В CORE второго практикума нет дополнительного предметного DocType.

---

# 6. Purchase Request fields

## S01 initial schema

| Label | Fieldname | Type | Required | In List View | Дополнительно |
|---|---|---|---:|---:|---|
| Subject | `subject` | Data | yes | yes | Title Field |
| Description | `description` | Small Text | no | no | — |
| Requested Amount | `requested_amount` | Currency | yes | yes | — |
| Needed By | `needed_by` | Date | yes | yes | — |
| Status | `status` | Select | yes | yes | Default = `PLT Draft` |

На S01 `status` options:

```text
PLT Draft
PLT Pending Approval
PLT Approved
PLT Rejected
```

## Почему Currency

`requested_amount` — денежная сумма, поэтому штатный `Currency` точнее `Float`.

CORE использует числовое значение в валютном контексте Site и не вводит отдельное поле Currency/Price List/Exchange Rate: таких требований нет.

## Почему нет requester field

CORE contract:

```text
requester = Document.owner
```

Поэтому отдельный `requester → Link → User` сейчас был бы вторым источником одного смысла.

Если позже требуется создавать заявку за другого пользователя, это отдельный GATE.

---

# 7. Naming и title

Второй практикум не переучивает naming, но применяет правило первого CORE.

## Naming

```text
PLT-PR-.#####
```

Ожидаемый вид на новом Site:

```text
PLT-PR-00001
PLT-PR-00002
...
```

Текущий counter принадлежит Site и не является App source.

## Title

```text
Title Field = subject
```

Смысл:

```text
name    → стабильная identity
subject → изменяемое человекочитаемое представление
```

---

# 8. Эволюция `status`

`status` остаётся **одним Standard Select** на всём CORE.

Никогда не создаётся обязательный второй:

```text
workflow_state
```

## S01–S02

```text
status : Select
Default = PLT Draft
No Copy = no
Allow on Submit = no
```

Это обычное business state.

## S03 — Workflow появился

Тот же field становится:

```text
Workflow State Field = status
```

И одновременно:

```text
No Copy = yes
Allow on Submit = no
```

Почему `No Copy = yes`:

обычный Duplicate нового Purchase Request не должен переносить process state исходного документа.

Почему `Allow on Submit = no`:

текущий CORE не содержит обычного submitted→submitted update, требующего изменить `status` через `update_after_submit`.

## S05

К options добавляется:

```text
PLT Pending Senior
```

## S07A

К options добавляется:

```text
PLT Cancelled
```

---

# 9. Role + DocPerm evolution

Роли создаются на dev-site как setup для конфигурации, но App source их имён — Standard Purchase Request DocPerm.

`Role fixture` не используется.

## S02 baseline

| Role | Read | Create | Write | Delete | Submit | Cancel | Amend |
|---|---:|---:|---:|---:|---:|---:|---:|
| `PLT Requester` | yes | yes | yes | no | no | no | no |
| `PLT Approver` | yes | no | yes | no | no | no | no |

`If Owner` не включается: CORE не предъявляет требования скрывать от Requester чужие Purchase Requests или ограничивать Write только owner. Это отдельная security responsibility.

## S05 — появляется Senior

| Role | Read | Create | Write | Delete | Submit | Cancel | Amend |
|---|---:|---:|---:|---:|---:|---:|---:|
| `PLT Senior Approver` | yes | no | yes | no | no | no | no |

`Write` нужен, потому что до S06 final transition остаётся draft→draft и `apply_workflow()` сохраняет Document обычным save path.

## S06 — появляется Submit

| Role | Submit |
|---|---:|
| `PLT Requester` | no |
| `PLT Approver` | yes |
| `PLT Senior Approver` | yes |

Остальная матрица не расширяется.

## S07A — появляется Cancel

| Role | Cancel |
|---|---:|
| `PLT Requester` | no |
| `PLT Approver` | yes |
| `PLT Senior Approver` | no |

## S07B — появляется Amend

| Role | Amend |
|---|---:|
| `PLT Requester` | yes |
| `PLT Approver` | no |
| `PLT Senior Approver` | no |

Requester уже имеет `Create = yes`, что требуется native Desk amend copy path.

---

# 10. LIMIT условного согласования

CORE фиксирует:

```text
APPROVAL_LIMIT = 1000
```

Это не Settings и не Python constant приложения.

В CORE LIMIT существует только как фиксированная часть Workflow conditions:

```text
doc.requested_amount <= 1000
doc.requested_amount > 1000
```

Если администратор должен менять LIMIT без изменения Workflow, это отдельный GATE и первый кандидат — App-owned settings mechanism.

---

# 11. Workflow State records

## S03 initial records

Создаются:

```text
PLT Draft
PLT Pending Approval
PLT Rejected
PLT Approved
```

## S05

Добавляется:

```text
PLT Pending Senior
```

## S07A

Добавляется:

```text
PLT Cancelled
```

Все эти records App-owned и в финальном состоянии экспортируются filtered fixture.

Style/icon не являются contract CORE и не задаются ради оформления.

---

# 12. Workflow Action Master records

Frappe v16.33.0 базово создаёт:

```text
Approve
Reject
Review
```

Наш Workflow переиспользует Framework-owned:

```text
Approve
Reject
```

Но вводит два собственных действия:

```text
PLT Submit for Review
PLT Cancel Request
```

Они являются App-owned setup records и в финальном состоянии экспортируются filtered `Workflow Action Master` fixture.

Не создаётся собственный action engine: это только штатные Link-records для `Workflow Transition.action`.

---

# 13. Workflow exact identity

```text
Workflow Name        : PLT Purchase Request Approval
Document Type        : Purchase Request
Workflow State Field : status
Is Active            : yes
Don't Override Status: no
Send Email Alert     : no
Action Confirmation  : no
```

Email не является prerequisite Workflow Action.

---

# 14. Workflow State rows — финальный порядок

Порядок state rows является contract, потому что Frappe использует первый state с соответствующим `docstatus` как default state для local Document.

Финальный order:

| idx | State | Doc Status | Only Allow Edit For |
|---:|---|---:|---|
| 1 | `PLT Draft` | 0 | `PLT Requester` |
| 2 | `PLT Pending Approval` | 0 | `PLT Approver` |
| 3 | `PLT Rejected` | 0 | `PLT Requester` |
| 4 | `PLT Pending Senior` | 0 | `PLT Senior Approver` |
| 5 | `PLT Approved` | 1 | `PLT Approver` |
| 6 | `PLT Cancelled` | 2 | `PLT Requester` |

До S06 `PLT Approved` имеет `Doc Status = 0`.

До S05 row `PLT Pending Senior` отсутствует.

До S07A row `PLT Cancelled` отсутствует.

## Граница allow_edit

`Only Allow Edit For` — Desk/state edit policy.

Он не объявляется самостоятельной server-side гарантией неизменности business fields.

Если нужна server-side state-dependent immutability, это отдельный GATE.

---

# 15. Workflow transitions — финальный contract

## T01 — Requester отправляет заявку

```text
State               : PLT Draft
Action              : PLT Submit for Review
Next State          : PLT Pending Approval
Allowed             : PLT Requester
Allow Self Approval : yes
Condition           : none
```

Почему self=yes:

requester = owner и должен иметь возможность отправить собственный Document.

## T02 — Approver финально одобряет малую заявку

```text
State               : PLT Pending Approval
Action              : Approve
Next State          : PLT Approved
Allowed             : PLT Approver
Allow Self Approval : no
Condition           : doc.requested_amount <= 1000
```

## T03 — Approver отправляет большую заявку Senior

```text
State               : PLT Pending Approval
Action              : Approve
Next State          : PLT Pending Senior
Allowed             : PLT Approver
Allow Self Approval : no
Condition           : doc.requested_amount > 1000
```

`T02` и `T03` используют один action `Approve`; mutually exclusive conditions определяют следующий state.

## T04 — Approver отклоняет

```text
State               : PLT Pending Approval
Action              : Reject
Next State          : PLT Rejected
Allowed             : PLT Approver
Allow Self Approval : yes
Condition           : none
```

Почему self=yes:

CORE запрещает self **approval**, но не вводит отдельного требования запрещать отрицательное решение dual-role owner. Значение зафиксировано явно и не оставлено случайным default.

## T05 — Requester повторно отправляет Rejected

```text
State               : PLT Rejected
Action              : PLT Submit for Review
Next State          : PLT Pending Approval
Allowed             : PLT Requester
Allow Self Approval : yes
Condition           : none
```

## T06 — Senior финально одобряет большую заявку

```text
State               : PLT Pending Senior
Action              : Approve
Next State          : PLT Approved
Allowed             : PLT Senior Approver
Allow Self Approval : no
Condition           : none
```

## T07 — Approver отменяет Submitted approval

Появляется только S07A:

```text
State               : PLT Approved
Action              : PLT Cancel Request
Next State          : PLT Cancelled
Allowed             : PLT Approver
Allow Self Approval : yes
Condition           : none
```

Почему self=yes:

CORE не содержит отдельного требования независимого canceller для dual-role owner. Cancel — отдельная отрицательная responsibility, а не final approval. Значение зафиксировано явно.

---

# 16. Эволюция Workflow по этапам

## S03 — простой approval

До conditional Senior requirement:

States:

```text
PLT Draft              docstatus 0
PLT Pending Approval   docstatus 0
PLT Rejected           docstatus 0
PLT Approved           docstatus 0
```

Transitions:

```text
Draft
→ Submit for Review
→ Pending Approval

Pending Approval
→ Approve
→ Approved

Pending Approval
→ Reject
→ Rejected

Rejected
→ Submit for Review
→ Pending Approval
```

На этом этапе positive Approve transition первоначально может иметь `Allow Self Approval = yes`: запрет self approval ещё не предъявлен как требование.

## S04 — появляется separation of duties

Изменяется только positive approval transition:

```text
Pending Approval → Approved
Allow Self Approval: yes → no
```

Requester transitions остаются self=yes.

Reject остаётся self=yes по принятой CORE semantics.

## S05 — появляется Senior branch

Прямой Approve получает condition `<= 1000`.

Добавляются:

```text
PLT Pending Senior
Pending Approval → Pending Senior condition > 1000
Pending Senior → Approved
```

Обе новые positive approval transitions сразу получают:

```text
Allow Self Approval = no
```

Нельзя оставить default `yes`.

## S06 — final approval становится фактом

Перед изменением mapping очищаются несовместимые disposable dev records — см. раздел 19.

Затем:

```text
Is Submittable = yes
PLT Approved Doc Status: 0 → 1
```

Frappe автоматически добавляет Standard field:

```text
amended_from
```

если его нет.

Добавляются Submit DocPerm final approvers.

`status.Allow on Submit` остаётся `no`.

## S07A — появляется Cancel

Добавляются:

```text
status option PLT Cancelled
Workflow State PLT Cancelled docstatus 2
T07 Approved → Cancelled
PLT Approver Cancel=yes
```

На этом этапе:

```text
Cancelled Only Allow Edit For = PLT Approver
```

## S07B — появляется Amend

Добавляется только:

```text
PLT Requester Amend=yes
```

и state/UI policy эволюционирует:

```text
PLT Cancelled
Only Allow Edit For:
PLT Approver → PLT Requester
```

`amended_from` вручную не создаётся.

---

# 17. `amended_from` contract

После S06 Meta должен содержать Framework-added Standard field:

```text
Label      : Amended From
Fieldname  : amended_from
Fieldtype  : Link
Options    : Purchase Request
Read Only  : yes
No Copy    : yes
```

Сам факт наличия поля не даёт Amend permission.

S07B проверяет native Desk path:

```text
Cancelled original
→ Requester Amend
→ новый local Purchase Request
→ docstatus 0
→ Workflow default state PLT Draft
→ amended_from = original
```

`status.No Copy = yes` не объясняет Amend reset: Frappe `copy_doc(..., from_amend=true)` специально не применяет обычный no_copy filter, а local Form Workflow затем устанавливает default state для `docstatus 0`.

---

# 18. Контрольные Site-local Users

Эти Users нужны для ручных проверок dev/acceptance Sites и не поставляются App.

## U01 Requester

```text
requester@example.test
Roles:
- PLT Requester
```

## U02 Approver

```text
approver@example.test
Roles:
- PLT Approver
```

## U03 Senior

Создаётся только после S05:

```text
senior@example.test
Roles:
- PLT Senior Approver
```

## U04 Dual-role owner

На S04:

```text
dual@example.test
Roles:
- PLT Requester
- PLT Approver
```

После S05 дополнительно:

```text
- PLT Senior Approver
```

U04 нужен именно для self-approval contracts.

Конкретные пароли — Site-local и не документируются в Git.

---

# 19. Disposable dev-data reset перед S06

До S06 `PLT Approved` означал:

```text
docstatus 0
```

После S06 он означает:

```text
docstatus 1
```

Поэтому все старые учебные Purchase Requests со state `PLT Approved` и `docstatus 0` считаются несовместимыми с новой mapping.

## Обязательный S06 preflight

До включения Submittable:

1. перечислить существующие Purchase Requests;
2. выделить созданные только практикумом disposable records;
3. зафиксировать, что они не являются реальными пользовательскими данными;
4. удалить учебные Purchase Requests обычным `frappe.delete_doc()` / Desk Delete под подходящим пользователем или Administrator как dev cleanup;
5. убедиться, что таблица контрольных Purchase Requests готова к созданию заново;
6. только после этого менять `Is Submittable` и Workflow Doc Status mapping.

## Запрещено

```text
UPDATE tabPurchase Request SET docstatus = ...
ручной SQL migration
фиктивный patch только ради учебных данных
ignore_permissions как migration strategy
```

Это disposable development reset, а не production migration.

---

# 20. Контрольные business Documents после S06

После transactional mapping создаётся новый стабильный контрольный набор.

`name` не хардкодится: используется фактически выданный Frappe name с pattern `PLT-PR-#####`.

## C01 Small approval

```text
Owner            : requester@example.test
Subject          : Office chair
Description      : Ergonomic chair for workstation
Requested Amount : 500
Needed By        : 2026-10-15
```

Path:

```text
Draft 0
→ Pending Approval 0
→ Approve by approver
→ Approved 1
```

## C02 Large approval

```text
Owner            : requester@example.test
Subject          : Team laptop
Description      : Shared laptop for project work
Requested Amount : 1500
Needed By        : 2026-10-20
```

Path:

```text
Draft 0
→ Pending Approval 0
→ Approve by approver
→ Pending Senior 0
→ Approve by senior
→ Approved 1
```

## C03 Reject / resubmit

```text
Owner            : requester@example.test
Subject          : Whiteboard
Description      : Meeting room whiteboard
Requested Amount : 300
Needed By        : 2026-10-18
```

Path:

```text
Draft 0
→ Pending Approval 0
→ Reject
→ Rejected 0
→ edit allowed through Desk policy for Requester
→ Submit for Review
→ Pending Approval 0
```

## C04 Self-approval small

```text
Owner            : dual@example.test
Subject          : Dual-role small request
Requested Amount : 400
Needed By        : 2026-10-21
```

External path to Pending Approval:

```text
owner performs PLT Submit for Review
```

Then owner using Approver role attempts `Approve`:

```text
must be rejected by apply_workflow self-policy
```

## C05 Self-approval large

```text
Owner            : dual@example.test
Subject          : Dual-role large request
Requested Amount : 2000
Needed By        : 2026-10-22
```

Checks two boundaries:

```text
owner+Approver cannot first-level Approve → Pending Senior
```

Для отдельной проверки Senior self-policy external `approver@example.test` переводит document в `PLT Pending Senior`, затем owner `dual@example.test` с Senior role пытается final Approve и получает отказ.

## C06 Cancel / Amend

```text
Owner            : requester@example.test
Subject          : External monitor
Requested Amount : 700
Needed By        : 2026-10-25
```

Path:

```text
Requester submits
→ Approver approves
→ Approved 1
→ Approver cancels
→ Cancelled 2
→ Requester Amend
→ new Draft 0
→ amended_from = original
```

---

# 21. Workflow Action runtime contract

После transition в state с доступным следующим действием Frappe создаёт runtime `Workflow Action` с `permitted_roles`.

CORE наблюдает минимум:

```text
C01 Pending Approval
→ action доступна PLT Approver

C02 Pending Senior
→ action доступна PLT Senior Approver
```

Email alerts остаются выключены.

Workflow Action:

```text
runtime queue
≠ fixture
≠ конечная ACL конкретного пользователя
```

Self-policy доказывается фактическим `apply_workflow()`, а не наличием action record.

---

# 22. Fixture delivery — финальный contract S08

## Не fixtures

```text
Role
User
Workflow Action runtime rows
Purchase Request business records
```

Role names находятся в Standard Purchase Request DocPerm, missing Role создаёт Frappe при DocType sync.

## App-owned fixtures

Три типа setup records:

```text
Workflow Action Master
Workflow State
Workflow
```

## `hooks.py`

Финальная форма должна быть семантически эквивалентна:

```python
fixture_auto_order = True

fixtures = [
    {
        "dt": "Workflow Action Master",
        "filters": [
            [
                "workflow_action_name",
                "in",
                ["PLT Submit for Review", "PLT Cancel Request"],
            ]
        ],
    },
    {
        "dt": "Workflow State",
        "filters": [
            [
                "workflow_state_name",
                "in",
                [
                    "PLT Draft",
                    "PLT Pending Approval",
                    "PLT Rejected",
                    "PLT Pending Senior",
                    "PLT Approved",
                    "PLT Cancelled",
                ],
            ]
        ],
    },
    {
        "dt": "Workflow",
        "filters": [["workflow_name", "=", "PLT Purchase Request Approval"]],
    },
]
```

Если `Workflow` filter в текущем v16 export path требует `name` вместо `workflow_name`, executable S08 должен следовать фактической DocType query semantics; смысл fixture остаётся ровно один named Workflow.

## Expected export filenames

При трёх fixtures и `fixture_auto_order = True` текущий v16 exporter добавляет sortable numeric prefixes:

```text
1_workflow_action_master.json
2_workflow_state.json
3_workflow.json
```

Порядок нужен потому что:

```text
Workflow Transition.action
→ Link → Workflow Action Master

Workflow states/transitions
→ Link → Workflow State
```

Следовательно:

```text
Workflow Action Master
→ Workflow State
→ Workflow
```

## Standard metadata раньше fixtures

`install_app()` сначала синхронизирует Standard DocTypes, поэтому до Workflow fixture уже должны существовать:

```text
Purchase Request DocType
PLT Requester Role
PLT Approver Role
PLT Senior Approver Role
```

Роли появляются из DocPerm sync, а не из fixture.

---

# 23. App-owned source manifest

Финальный обязательный source:

```text
purchase_lifecycle_training/
├── purchase_lifecycle_training/
│   ├── hooks.py
│   ├── modules.txt
│   ├── fixtures/
│   │   ├── 1_workflow_action_master.json
│   │   ├── 2_workflow_state.json
│   │   └── 3_workflow.json
│   └── purchase_lifecycle_training/
│       └── doctype/
│           └── purchase_request/
│               ├── purchase_request.json
│               ├── purchase_request.py
│               └── test_purchase_request.py
└── ... generated App files
```

`purchase_request.py` может остаться generated controller без собственной бизнес-логики, если CORE не предъявил отдельного server invariant вне штатного Workflow/docstatus.

Не писать Python только потому, что файл существует.

---

# 24. Автоматические test contracts S09

Используется актуальный для v16:

```python
from frappe.tests import IntegrationTestCase
```

Tests защищают **контракты App**, а не внутренности Frappe ради coverage.

Минимальный обязательный набор logical tests:

```text
test_requester_can_submit_own_request_for_review

test_requester_without_approver_role_cannot_approve

test_small_request_approver_reaches_approved

test_large_request_requires_senior_approval

test_senior_can_final_approve_large_request

test_dual_role_owner_cannot_self_approve_small_request

test_dual_role_owner_cannot_first_level_approve_own_large_request

test_dual_role_owner_cannot_senior_approve_own_large_request

test_rejected_request_stays_docstatus_zero

test_requester_can_resubmit_rejected_request

test_small_final_approval_is_docstatus_one

test_large_final_approval_is_docstatus_one

test_requester_has_no_submit_permission

test_approver_has_submit_permission

test_senior_has_submit_permission

test_only_approver_has_cancel_permission

test_only_requester_has_amend_permission

test_cancelled_request_is_docstatus_two

test_direct_illegal_state_change_is_rejected

test_status_is_single_standard_workflow_state_field

test_status_no_copy_is_enabled

test_status_allow_on_submit_is_disabled

test_required_roles_exist_from_standard_docperm

test_required_workflow_configuration_exists
```

Tests не должны создавать missing required Role/Workflow/State как fallback. Если App-owned delivery сломан, suite должен упасть.

## State transition helper

Для process contracts используется штатный:

```text
frappe.model.workflow.apply_workflow
```

под реальным test user context.

Не симулировать approval простым:

```python
doc.status = "PLT Approved"
doc.save()
```

кроме специального отрицательного test, который доказывает, что illegal direct transition отвергается.

---

# 25. Observed / Desk checks S09

Некоторые contracts нельзя честно выдавать за server unit/integration policy.

Отдельно через Desk проверяются:

```text
Only Allow Edit For делает ожидаемые states read-only/editable в UI
Workflow Action виден роли ожидающего действия
email не нужен для Workflow Action queue
Requester после Cancel видит native Amend action
native Amend создаёт новый Draft
amended_from ссылается на original
```

`Only Allow Edit For` не используется как доказательство server immutability.

---

# 26. Что S09 намеренно НЕ тестирует как собственный contract

Не писать тесты вида:

```text
«Frappe умеет создать Workflow State»
«Currency field хранит число»
«Link field вообще работает»
«docstatus enum имеет 0/1/2»
```

Тестируется наша конфигурация и наша process semantics.

---

# 27. Clean Site acceptance S10

Новый Site:

```text
purchase-lifecycle-acceptance.localhost
```

до установки содержит только:

```text
frappe
```

До install-app должны отсутствовать:

```text
Purchase Request
PLT Requester
PLT Approver
PLT Senior Approver
PLT Draft
PLT Pending Approval
PLT Rejected
PLT Pending Senior
PLT Approved
PLT Cancelled
PLT Purchase Request Approval
PLT Submit for Review
PLT Cancel Request
```

После:

```bash
bench --site purchase-lifecycle-acceptance.localhost install-app purchase_lifecycle_training
```

без developer mode и без ручного setup должны появиться:

```text
Module
Purchase Request Standard DocType
all final DocPerm
three PLT Role records from DocPerm sync
custom Workflow Action Master records
all PLT Workflow State records
PLT Purchase Request Approval Workflow
```

Затем:

```text
migrate
full tests
Site-local test Users
small approval
large approval
reject/resubmit
self-approval negative checks
Cancel
Amend
Workflow Action observation
```

Все проходят без:

```text
ручного создания Role
ручного создания Workflow State
ручного создания Workflow Action Master
ручного создания Workflow
Role Permission Manager как install step
Custom Field workflow_state
ручного amended_from
ручного SQL
patch для disposable training data
```

---

# 28. Acceptance delivery checks

На clean Site доказать source ownership:

```text
Purchase Request schema/DocPerm
→ Standard DocType JSON

PLT Role records
→ created by Standard DocType sync from DocPerm

PLT Submit for Review / PLT Cancel Request
→ ordered Workflow Action Master fixture

PLT Workflow States
→ ordered Workflow State fixture

Workflow
→ ordered Workflow fixture

Users/passwords/business docs
→ Site-local
```

И отсутствие обязательных скрытых:

```text
Custom Field workflow_state
Custom DocPerm
Property Setter
Role fixture
```

---

# 29. CORE stage-to-contract map

| Stage | Точный результат |
|---|---|
| `S00` | `purchase_lifecycle_training` установлен на `purchase-lifecycle.localhost`; dev Site-local developer mode |
| `S01` | Purchase Request schema, naming, title, owner semantics, initial Select status |
| `S02` | PLT Requester/Approver DocPerm + отрицательное доказательство plain status |
| `S03` | базовый Workflow, Workflow States, custom submit action master, `status.No Copy=yes`, Workflow Action, Reject/Resubmit |
| `S04` | positive Approve transition получает `allow_self_approval=no`; dual-role negative proof |
| `S05` | Senior role/DocPerm + Pending Senior + mutually exclusive amount conditions + self=no на новых approval transitions |
| `S06` | dev-data reset, Is Submittable, Approved→1, auto `amended_from`, Submit permissions |
| `S07A` | Cancelled state/action, Approver Cancel, Cancelled→2 |
| `S07B` | Requester Amend + Cancelled allow_edit Requester + native Amend observation |
| `S08` | ordered Action Master → State → Workflow fixtures; Role fixtures absent |
| `S09` | IntegrationTestCase contracts + observed/UI checks |
| `S10` | clean Site reproduces complete lifecycle without hidden setup |

---

# 30. GATE — server-side immutability pending approval

CORE **не** утверждает:

> После Submit for Review Requester не может изменить business fields никаким server/API path.

Текущая модель:

```text
Requester Write=yes
Workflow allow_edit
→ Desk edit policy
```

Если появляется requirement:

```text
Pending Approval / Pending Senior
→ business fields server-immutable для requester независимо от UI/API
```

это новая ответственность.

Тогда отдельно оцениваются штатные permissions/lifecycle extension points и только затем собственная validation/policy logic.

Этот GATE не активируется автоматически во втором CORE.

---

# 31. GATE — production migration

S06 удаляет disposable training data только потому, что это учебный dev Site без поддерживаемой старой версии.

Если бы существовали реальные данные предыдущей поддерживаемой версии:

```text
Approved state = docstatus 0
↓ upgrade
Approved state = docstatus 1
```

это уже настоящая data migration responsibility.

Тогда нужен отдельный migration plan/patch, а не dev-data reset.

---

# 32. GATE — requester != owner

Если появляется сценарий:

```text
секретарь / менеджер создаёт Purchase Request за другого Requester
```

то:

```text
requester ≠ owner
```

и встроенная self-approval проверка по `doc.owner` больше не соответствует бизнес-смыслу requester.

Тогда модель пересматривается до добавления собственного запрета.

---

# 33. GATE — configurable LIMIT

Если LIMIT должен менять администратор без редактирования Workflow:

```text
1000 hardcoded condition
```

перестаёт соответствовать требованию.

Первый кандидат — App-owned Settings, после чего condition читает эту настройку штатным безопасным способом.

В CORE этого требования нет.

---

# 34. NEXT остаётся вне CORE

Не включать в S00–S10 автоматически:

```text
Assignment / ToDo
Notification
File / Comment / Version
Print
Report
Workspace
REST API
Webhook
background jobs
scheduler
foreign DocType extension
custom frontend
external integration
```

Это не «забытые темы», а механизмы без текущей обязательной ответственности.

---

# 35. Критерий готовности спецификации

Перед созданием первого executable exercise отдельный аудит должен ответить `да` на все вопросы:

```text
1. App/Module/Sites названы однозначно?
2. Purchase Request schema минимальна и полна?
3. naming переиспользует принцип первого CORE?
4. requester и owner не задублированы?
5. status один и остаётся Standard?
6. No Copy и Allow on Submit выставлены по реальной семантике?
7. Role names namespaced и permission matrix минимальна?
8. Senior rights появляются только из Senior requirement?
9. LIMIT фиксирован и не маскируется под settings?
10. Workflow State names глобально различимы?
11. State row order обеспечивает Draft default?
12. Каждый transition имеет явный self-policy?
13. Requester self-transitions не блокируются default-логикой?
14. Все positive approval transitions блокируют owner approval?
15. Reject/Cancel self-policy выбран осознанно?
16. Approved→1 появляется только после transactional requirement?
17. Cancel и Amend получают отдельные rights?
18. amended_from не создаётся руками?
19. S06 dev-data reset не выдан за production migration?
20. Role fixture отсутствует без отдельной Role responsibility?
21. custom Action Masters имеют delivery path?
22. fixture ordering отражает реальные Links?
23. tests защищают наши process contracts?
24. allow_edit не выдан за server immutability?
25. clean Site может восстановить всё обязательное без ручного setup?
```

Только после этого спецификация становится основанием для `core/S00...S10`.
