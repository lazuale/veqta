# Граф зависимостей второго учебного практикума Frappe

Статус: **черновик dependency graph после принятой REQUIREMENTS_MATRIX**.

Этот документ построен из [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md) и не является дорожной картой занятий.

Его задача — отделить:

```text
что должно существовать раньше технически
```

от:

```text
что нам просто удобно показать раньше методически
```

В граф попадает только реальная зависимость результата. Если два механизма можно доказать независимо после общего основания, они остаются параллельными ветками.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md) и решения `R01–R17` из матрицы.

---

# 1. Техническое предусловие

## P00. Второй учебный App установлен на dev/test Site

Это не новая тема второго практикума.

Ученик уже умеет из первого CORE:

```text
Bench
Site
App
Module
install-app
migrate
Git
```

Для второго практикума нужен отдельный учебный App и совместимый Frappe v16 Site.

`P00` не доказывает lifecycle. Он только создаёт место, где дальше появляется `Purchase Request`.

---

# 2. Узлы CORE

## P01. Минимальный Purchase Request существует как Standard DocType

Покрывает главным образом `R01`.

Результат:

```text
Purchase Request
├── subject
├── description
├── requested_amount
└── needed_by
```

Пока нет Workflow, Senior approval, Submit/Cancel и NEXT-механизмов.

---

## P02. Requester semantics и обычный business status доказаны

Покрывает `R02–R03`.

Результат:

```text
requester = Document.owner

status = Standard Select
Draft
Pending Manager
Approved
Rejected
```

Это ещё только хранение состояния.

---

## P03. Базовый DocType access выражен Role + DocPerm

Покрывает `R05` до появления Senior approval.

Роли:

```text
Purchase Requester
Purchase Approver
```

Результат:

```text
DocPerm
→ может ли пользователь вообще работать с Purchase Request
```

Здесь ещё нет процессного права `Approve` как Workflow transition.

---

## P04. Ограничение обычного status доказано отрицательным опытом

Покрывает `R04`.

Предусловия:

```text
P02 status
+
P03 пользователь с обычным Write
```

Наблюдение:

```text
обычный status
не выражает сам по себе
кто имеет право выполнить конкретный переход
```

Пользователь с подходящим Write технически способен поставить другое допустимое значение `status`.

Это и создаёт причину следующего узла.

---

## P05. Базовый Workflow владеет role-controlled transitions

Покрывает `R06–R07`.

Появляется только после `P04`.

Результат:

```text
status остаётся Standard Select
Workflow State Field = status

Purchase Requester:
Draft → Pending Manager

Purchase Approver:
Pending Manager → Approved
Pending Manager → Rejected
```

Также для каждого Workflow Document State принимается осознанный `Only Allow Edit For` (`allow_edit`).

Важно:

```text
status
→ один source of truth

Workflow
→ политика transitions
```

Обязательный site-local `workflow_state` Custom Field не создаётся.

---

## P06. Workflow Action наблюдаем как штатная очередь действий

Покрывает `R08`.

Требует работающий `P05`, но не является основанием безопасности самого Workflow.

Результат:

```text
Workflow transition
↓
Workflow Action runtime records
↓
permitted_roles
```

Проверяется граница:

```text
Workflow Action
≠ окончательная ACL конкретного пользователя
```

Self approval проверяется отдельным узлом `P08`.

---

## P07. Условный второй уровень approval выражен штатным Workflow

Покрывает `R09`.

Требует `P05`.

Только теперь появляются:

```text
Senior Purchase Approver
Pending Senior
Workflow Transition Condition
```

Результат:

```text
requested_amount <= LIMIT
→ Purchase Approver может завершить approval

requested_amount > LIMIT
→ Pending Senior
→ Senior Purchase Approver
→ Approved
```

До этого узла Senior role/state не существуют.

---

## P08. Self approval policy доказана реальным apply_workflow

Покрывает `R10`.

Требует одновременно:

```text
P02 requester = owner
+
P05 Workflow transitions
```

Результат:

```text
owner + Approver role
+ allow_self_approval = false
→ собственный Approve отклонён
```

`P06 Workflow Action` не является prerequisite этого правила: наличие role-scoped action не заменяет серверную проверку `apply_workflow()`.

---

## P09. Rejected остаётся draft-state и имеет явный resubmit path

Покрывает `R11`.

Требует `P05`.

Результат:

```text
Rejected
→ docstatus 0
→ Purchase Requester исправляет допустимые данные
→ Submit for Review
→ Pending Manager
```

`Rejected` не смешивается с системным `Cancelled`.

---

## P10. Final Approved становится Submitted fact

Покрывает `R12`.

Требует, чтобы final approval уже имел определённый маршрут. Поэтому минимальное основание:

```text
P05 базовый Workflow
+
P07 оба final approval path
```

Теперь появляется новая ответственность:

```text
окончательно согласованный Document
нельзя бесследно переписать обычным Save
```

Результат:

```text
Is Submittable = yes

Approved  → docstatus 1
Cancelled → docstatus 2
```

Одновременно меняется DocPerm:

```text
Purchase Approver        → Submit yes / Cancel yes
Senior Purchase Approver → Submit yes / Cancel yes
Purchase Requester       → Submit no  / Cancel no
```

Для `status` как workflow-state field включается необходимая after-submit semantics, но это не превращает status в обход Workflow transitions.

---

## P11. Workflow полностью управляет submit/cancel path

Покрывает `R13`.

Требует `P10`.

Результат:

```text
Draft-state 0
→ Approved 1
→ Cancelled 2
```

и отрицательные границы:

```text
Draft → Cancelled        нельзя
Submitted → Draft        нельзя
Cancelled → другой state нельзя
```

Здесь уже проверяется реальное поведение `apply_workflow()` через `save()/submit()/cancel()` semantics Frappe.

---

## P12. Ошибка Submitted fact исправляется через Cancel / Amend

Покрывает `R14`.

Требует рабочий `P11`, потому что исходный Document сначала должен корректно стать `Cancelled`.

Ожидаемый native path:

```text
Approved original
→ Workflow Cancel
→ Cancelled original
→ Amend
→ новый Draft Document
→ amended_from = original
```

Критическая граница:

```text
Amend runtime behaviour
не предполагается по документации курса
а наблюдается на принятой версии Frappe
```

Если фактический v16 path расходится с ожиданием, сначала фиксируется реальное поведение Framework; workaround заранее не проектируется.

---

## P13. Обязательный lifecycle имеет App-owned delivery path

Покрывает `R15`.

Этот узел требует уже сформированной обязательной конфигурации процесса:

```text
P03 base Roles
+
P07 Senior Role / Pending Senior
+
P11 final Workflow states/transitions/docstatus mapping
```

Source of truth:

```text
Purchase Request schema/status/permissions
→ Standard DocType metadata

Role records
→ filtered fixtures

Workflow State records
→ filtered fixtures

Workflow + child states/transitions/conditions
→ filtered fixture

Workflow Actions
→ runtime Site data, НЕ fixture

Users/passwords/runtime Purchase Requests
→ Site-local
```

Delivery dependency:

```text
Role
→ Workflow State
→ Workflow
```

потому что Frappe импортирует fixture files по сортированным именам.

Исполняемая спецификация должна доказать штатный ordering/prefix mechanism, а не полагаться на случайный filesystem order.

Также здесь принимается сознательное решение по namespace глобальных `Workflow State` records:

```text
App-scoped names
или
явно доказанное shared-state reuse
```

---

## P14. Lifecycle защищён automated contracts

Покрывает `R16`.

Автотесты появляются только после того, как весь обязательный server contract определён.

Зависимости:

```text
P05 base Workflow
P07 conditional approval
P08 self approval
P09 reject/resubmit
P11 submit/cancel
P13 App-owned mandatory configuration
```

Server contracts проверяют:

```text
Requester submit-for-review
role transitions
amount branching
Senior approval
self approval
Rejected docstatus 0 + resubmit
Approved docstatus 1
Submit/Cancel DocPerm
Cancelled docstatus 2
illegal transitions
single Standard status field
mandatory configuration presence
```

Observed/UI checks не маскируются под server contracts:

```text
Only Allow Edit For presentation
Workflow Action presentation
Amend Desk path
```

`P12` поэтому не обязан блокировать написание всех server tests, но его observed acceptance должен быть завершён до финального clean-site gate.

---

## P15. Clean Site acceptance доказывает воспроизводимость lifecycle

Покрывает `R17`.

Это финальный узел CORE.

Требует:

```text
P12 native Cancel / Amend scenario verified
+
P13 App-owned delivery
+
P14 automated contracts green
```

Финал:

```text
чистый совместимый Frappe Site
+ committed lifecycle App
+ install-app / migrate
+ Standard Purchase Request metadata
+ ordered mandatory Role / Workflow State / Workflow config
+ tests
+ реальный requester/approver/senior scenario
+ Cancel / Amend observed path
= воспроизводимый lifecycle CORE
```

На clean Site запрещено вручную достраивать обязательный Workflow, Roles, Workflow States или второе state field.

Это не production deployment test.

---

# 3. Граф зависимостей

Сжатый граф:

```text
P00 App/Site prerequisite
  ↓
P01 Purchase Request
  ├──────────────→ P03 base Roles + DocPerm
  ↓
P02 owner + status
  │                 │
  └──────┬──────────┘
         ↓
P04 prove plain status limitation
         ↓
P05 base Workflow + one Standard state field
  ├────────→ P06 Workflow Action
  ├────────→ P09 Rejected + resubmit
  ├───┐
  │   └──── P02 ───→ P08 self approval
  │
  └────────→ P07 conditional Senior approval
                  ↓
             P10 Is Submittable + Submit/Cancel DocPerm
                  ↓
             P11 Workflow submit/cancel path
                  ↓
             P12 Cancel / Amend observation

P03 ───────┐
P07 ───────┼────→ P13 App-owned ordered delivery
P11 ───────┘

P05 ───────┐
P07 ───────┤
P08 ───────┤
P09 ───────┼────→ P14 automated contracts
P11 ───────┤
P13 ───────┘

P12 ───────┐
P13 ───────┼────→ P15 clean Site acceptance
P14 ───────┘
```

---

# 4. Таблица рёбер

| Откуда | Куда | Почему зависимость реальная |
|---|---|---|
| P00 | P01 | Нужен App/Site, чтобы создать Standard DocType |
| P01 | P02 | owner/status относятся к существующему Purchase Request |
| P01 | P03 | DocPerm настраивается для существующего DocType |
| P02 | P04 | Нужно обычное state field |
| P03 | P04 | Нужен реальный пользователь с Write для отрицательного опыта |
| P04 | P05 | Именно ограничение plain status обосновывает Workflow |
| P05 | P06 | Workflow Action возникает из работающего Workflow |
| P05 | P07 | Condition/Senior branch расширяют существующий Workflow |
| P02 | P08 | Self approval привязан к принятой semantics requester = owner |
| P05 | P08 | Нужен реальный Workflow transition |
| P05 | P09 | Rejected/resubmit — часть Workflow state machine |
| P05 | P10 | Final approval должен быть workflow state |
| P07 | P10 | Должны существовать оба маршрута final approval |
| P10 | P11 | Submit/cancel path появляется только у Submittable DocType |
| P11 | P12 | Amend требует корректно Cancelled original |
| P03 | P13 | Base Role records входят в delivery |
| P07 | P13 | Senior Role/State входят в final mandatory config |
| P11 | P13 | Финальный Workflow/docstatus mapping должен быть уже определён |
| P05 | P14 | Tests проверяют базовый Workflow |
| P07 | P14 | Tests проверяют amount branching |
| P08 | P14 | Tests проверяют self approval |
| P09 | P14 | Tests проверяют reject/resubmit |
| P11 | P14 | Tests проверяют submit/cancel semantics |
| P13 | P14 | Tests должны работать на App-owned mandatory config |
| P12 | P15 | Финальная приёмка включает native Amend observation |
| P13 | P15 | Clean Site должен воспроизвести config из App |
| P14 | P15 | Перед финальной приёмкой automated contracts должны быть green |

---

# 5. Что намеренно НЕ является зависимостью

## Workflow Action не блокирует self approval

Неверно:

```text
P06 Workflow Action
→ P08 self approval
```

Почему: self approval проверяет серверный Workflow transition; Workflow Action — отдельный runtime presentation/queue mechanism.

Правильно:

```text
P02 requester = owner
+
P05 Workflow
→ P08
```

---

## Rejected/resubmit не нужен для появления Submittable

`P09` полезен для полного процесса, но системная возможность final Approved стать Submitted не зависит технически от reject branch.

Поэтому нет искусственного ребра:

```text
P09 → P10
```

---

## Cancel/Amend не блокирует саму delivery-конфигурацию

`P13` может фиксировать Role/Workflow/Workflow State source раньше финального observed Amend scenario.

Поэтому нет ребра:

```text
P12 → P13
```

Но `P12` обязателен перед `P15`, потому что clean acceptance должен проверить весь заявленный CORE lifecycle.

---

## NEXT не блокирует CORE

Нет зависимостей:

```text
Assignment
Notification
File / Comment / Version
Print
→ P15
```

Они остаются NEXT и не имеют права стать скрытым условием успешного второго практикума.

---

# 6. Архитектурные развилки вне основного графа

`D00–D04` из матрицы не превращаются в последовательные этапы автоматически.

Они включаются только новым требованием:

```text
D00 поддерживаемая старая версия + реальные данные
→ migration plan / patch analysis

D01 безопасное post-submit поле
→ field-specific Allow on Submit

D02 requester != owner
→ отдельный requester field + новый self-approval analysis

D03 LIMIT становится админ-настройкой
→ Settings candidate

D04 динамический approval route
→ повторный fit analysis Workflow
```

Ни одна ветка GATE не включена в `P00–P15` по умолчанию.

---

# 7. Gate перед roadmap

Перед построением `PRACTICUM_ROADMAP.md` нужно подтвердить:

```text
1. Каждый P-узел производит наблюдаемый результат, а не просто знакомит с функцией?
2. P04 действительно предшествует Workflow и объясняет его появление?
3. P05 не создаёт второго state field?
4. P06 не используется как ACL?
5. P07 впервые вводит Senior role/state?
6. P08 зависит от requester=owner, а не от Workflow Action?
7. P09 не смешивает Rejected и Cancelled?
8. P10 вводит Is Submittable вместе с Submit/Cancel DocPerm?
9. P11 проверяет реальный save/submit/cancel path?
10. P12 не предполагает Amend semantics без наблюдения?
11. P13 учитывает fixture dependency order и глобальность Workflow State names?
12. P14 разделяет server contracts и UI/observed checks?
13. P15 зависит только от обязательного CORE, а не от NEXT?
14. Ни один GATE не превратился в обязательный этап без нового требования?
15. Граф описывает зависимости результатов, а не желаемый порядок лекций?
```

Если любой ответ отрицательный, сначала исправляется граф. Roadmap строится только после этого gate.
