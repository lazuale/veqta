# Граф зависимостей второго учебного практикума Frappe

Статус: **аудированный dependency graph; основание для roadmap**.

Этот документ построен из [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md) и не является дорожной картой занятий.

Его задача — отделить:

```text
что действительно зависит от предыдущего результата
```

от:

```text
что нам просто удобно показать раньше методически
```

В граф попадает только реальная зависимость результата или архитектурная причинность требования. Тип зависимости фиксируется отдельно, чтобы не выдавать учебную аргументацию за runtime prerequisite.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md) и решения `R01–R17` из матрицы.

---

# 1. Типы зависимостей

Граф различает несколько причин появления ребра.

```text
STRUCTURAL
→ без предыдущего объекта следующий технически не существует

ARCHITECTURAL_CAUSE
→ предыдущее наблюдение создаёт новую ответственность и обосновывает механизм

PROCESS
→ следующий кусок процесса расширяет уже существующую state machine

TRANSACTIONAL
→ следующий lifecycle step возможен только из предыдущего docstatus

DELIVERY
→ source должен уже содержать полный обязательный contract

VERIFICATION
→ проверка собирает несколько ранее определённых результатов

ACCEPTANCE
→ финальная чистая установка проверяет готовый source/contract
```

Это важно, например:

```text
P04 → P05
```

не означает, что Frappe технически запрещает создать Workflow раньше. Это означает:

```text
мы не имеем архитектурного основания включать Workflow,
пока не доказана новая responsibility transition policy
```

---

# 2. Техническое предусловие

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

# 3. Узлы CORE

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

Пока нет Workflow, Senior approval, Submit/Cancel/Amend и NEXT-механизмов.

---

## P02A. Requester semantics доказана независимо от status

Покрывает `R02`.

Результат:

```text
requester = Document.owner
```

Это отдельная ветка модели.

Она потребуется self-approval policy, но **не является prerequisite обычного status или самого факта существования Workflow**.

Если потом появится `requester != owner`, меняется именно эта ветка.

---

## P02B. Обычный business status существует до Workflow

Покрывает `R03`.

Результат:

```text
status = Standard Select
```

Physical values сразу App-scoped, потому что будущие `Workflow State` records глобально уникальны на Site:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
```

В схемах используются короткие aliases `Draft / Pending Manager / Approved / Rejected`.

Это ещё только хранение состояния.

---

## P03. Базовый DocType access выражен Role + DocPerm

Покрывает `R05` до появления Senior approval и transactional lifecycle.

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

Здесь ещё нет процессного права `Approve` как Workflow transition и нет `Submit/Cancel/Amend` permissions без соответствующего требования.

На dev-site роли могут быть созданы вручную для настройки DocPerm, но их финальная delivery semantics будет проверена позднее: Standard DocType sync умеет создавать missing Role из DocPerm.

---

## P04. Ограничение обычного status доказано отрицательным опытом

Покрывает `R04`.

Предусловия:

```text
P02B обычный status
+
P03 пользователь с обычным Write
```

`P02A requester=owner` здесь не нужен.

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

Появляется только после архитектурной причины `P04`.

До создания Workflow уже существуют App-scoped `Workflow State` records для текущих persisted values:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
```

То есть namespace global Workflow State не откладывается до delivery-аудита.

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

Для каждого Workflow Document State принимается осознанный `Only Allow Edit For` (`allow_edit`).

Важно:

```text
status
→ один source of truth

Workflow
→ политика transitions
```

Обязательный site-local `workflow_state` Custom Field не создаётся.

---

## P06. Workflow Action наблюдаем как штатную очередь действий

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
PR Pending Senior
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
P02A requester = owner
+
P05 Workflow transitions
```

Результат:

```text
owner + Approver role
+ allow_self_approval = false
→ собственный Approve отклонён
```

`P02B status` уже входит в `P05` через другую ветку, но requester semantics остаётся отдельным prerequisite.

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

Этот resubmit transition входит в финальную обязательную Workflow-конфигурацию и поэтому позже должен попасть в delivery join `P13`.

---

## P10. Final Approved становится Submitted fact

Покрывает `R12`.

Требует:

```text
P05 базовый Workflow
+
P07 оба final approval path
```

Почему `P07` здесь реальный prerequisite выбранной модели:

```text
к моменту перехода к Submitted
мы уже обязались поддерживать
маленький и большой final approval path
```

Это не универсальное ограничение Frappe, а зависимость накопленного requirement set практикума.

Новая ответственность:

```text
окончательно согласованный Document
нельзя бесследно переписать обычным Save
```

Результат:

```text
Is Submittable = yes
Approved → docstatus 1
```

Одновременно появляется только необходимый `Submit` DocPerm:

```text
Purchase Approver        → Submit yes
Senior Purchase Approver → Submit yes
Purchase Requester       → Submit no
```

`Cancel` и `Amend` ещё не выдаются: соответствующих обязанностей пока нет.

### Автоматическое следствие Frappe: amended_from

При сохранении Standard DocType с `Is Submittable` текущий Frappe вызывает `DocType.make_amendable()` и сам добавляет Standard Link:

```text
amended_from → Purchase Request
```

если такого field ещё нет.

Это часть Framework capability и App metadata после сохранения DocType.

Но:

```text
поле amended_from существует
≠
Amend уже разрешён бизнесом
≠
кому-то уже выдан Amend DocPerm
```

Amend responsibility появится только в `P12`.

---

## P11. Отмена Submitted approval становится отдельным Workflow responsibility

Покрывает `R13`.

Требует `P10`, потому что отменить можно только уже Submitted факт.

Новое требование:

```text
Approved разрешение нужно официально отменить
без удаления и без возврата в Draft
```

CORE policy:

```text
Purchase Approver
→ владеет Cancel approved request

Senior Purchase Approver
→ только final approval дорогой заявки

Purchase Requester
→ не Cancel
```

Результат:

```text
status += PR Cancelled
PR Cancelled → docstatus 2
status.Allow on Submit = yes

Purchase Approver        → Cancel yes
Senior Purchase Approver → Cancel no
Purchase Requester       → Cancel no
```

На этом шаге `Only Allow Edit For` нового Cancelled state соответствует текущей ответственности:

```text
Cancelled → Purchase Approver
```

Полный system path:

```text
Draft-state 0
→ Approved 1
→ Cancelled 2
```

Отрицательные границы:

```text
Draft → Cancelled        нельзя
Submitted → Draft        нельзя
Cancelled → другой state нельзя
```

Здесь проверяется реальное поведение `apply_workflow()` через `submit()/cancel()` semantics Frappe.

---

## P12. Исправленная версия создаётся через Amend

Покрывает `R14`.

Требует рабочий `P11`, потому что исходный Document сначала должен корректно стать `Cancelled`.

Новое требование:

```text
после Cancel requester должен создать исправленную версию
сохранив связь с исходным фактом
```

Ответственности разделены:

```text
Purchase Approver
→ Cancel original

Purchase Requester
→ Amend cancelled original
→ исправляет новый Draft
→ снова отправляет по Workflow
```

Только здесь появляется отдельный `Amend` DocPerm:

```text
Purchase Requester       → Amend yes
Purchase Approver        → Amend no
Senior Purchase Approver → Amend no
```

У Requester уже есть `Create = yes` из `P03`.

`amended_from` вручную не создаётся: оно уже появилось как штатное следствие `Is Submittable` в `P10`.

Одновременно state/edit policy эволюционирует вместе с новой ответственностью:

```text
Cancelled → Purchase Requester
```

`Amend` является стандартным permission type Frappe и в Desk описан как право создать amended copy cancelled Document. Но CORE не выдаёт сам permission bit за полное доказательство серверной невозможности вручную сконструировать иной Document path.

Поэтому доказательство разделяется:

```text
permission contract
→ frappe.has_permission(..., "amend") / role permissions

native user scenario
→ реальный Desk Amend
```

Ожидаемый native path:

```text
Approved original
→ Workflow Cancel
→ Cancelled original
→ Requester Amend
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

## P13. Весь обязательный lifecycle имеет один App-owned delivery path

Покрывает `R15`.

Это **join полного mandatory configuration**, а не только основной happy path.

К этому моменту должны быть определены:

```text
P08 self-approval policy
+
P09 reject/resubmit branch
+
P12 полный transactional path
```

Через `P12` транзитивно уже существуют базовые DocPerm, базовый Workflow, Senior branch, Submit, Cancel и Amend policy.

Source of truth:

```text
Purchase Request schema/status/amended_from/DocPerm
→ Standard DocType metadata

Role records из Purchase Request DocPerm
→ missing records создаются Framework при Standard DocType sync
→ Role fixtures не нужны текущему CORE

PR-* Workflow State records
→ filtered Workflow State fixture

Workflow + child states/transitions/conditions/self-approval/resubmit
→ filtered Workflow fixture

Workflow Actions
→ runtime Site data, НЕ fixture

Users/passwords/runtime Purchase Requests
→ Site-local
```

### Delivery dependency

После удаления лишнего Role fixture обязательный fixture order:

```text
Workflow State
→ Workflow
```

потому что Workflow ссылается на уже существующие Workflow State records.

Исполняемая спецификация должна доказать штатный ordering/prefix mechanism, а не полагаться на случайный filesystem order.

Первый кандидат:

```text
fixture_auto_order = True
+
fixtures hook в порядке:
1. Workflow State
2. Workflow
```

### Role delivery не дублируется

Текущий Frappe `DocType.make_module_and_roles()` во время Standard DocType sync создаёт отсутствующие Role из его permissions с `desk_access=1`.

Пока роль не несёт дополнительных App-owned свойств, отдельный Role fixture был бы вторым механизмом доставки одной ответственности.

### Workflow State namespace к P13 уже выбран

P13 не принимает naming decision заново. Он экспортирует ровно App-scoped records, существующие с предыдущих узлов:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
PR Pending Senior
PR Cancelled
```

---

## P14. Verification gate собирает server contracts и observed behavior

Покрывает `R16`.

`P14` не является ещё одним механизмом продукта. Это join проверки уже определённого lifecycle.

Требует:

```text
P06 Workflow Action runtime branch
+
P13 полный App-owned mandatory configuration
```

Через `P13` уже включены self-approval, reject/resubmit и transactional path.

Server contracts проверяют:

```text
Requester submit-for-review
role transitions
amount branching
Senior approval
self approval
Rejected docstatus 0 + resubmit
Approved docstatus 1
Submit DocPerm
Cancel DocPerm
Amend permission matrix
least-privilege split между Requester / Approver / Senior
Cancelled docstatus 2
illegal transitions
single Standard status field
mandatory configuration presence
Role records из Standard DocPerm
```

Observed/UI checks отдельно:

```text
Only Allow Edit For presentation
Workflow Action presentation
Requester Amend Desk path
```

`amended_from` не тестируется как внутренний механизм Frappe ради coverage, но его наличие проверяется как acceptance dependency нашего Amend scenario.

---

## P15. Clean Site acceptance доказывает воспроизводимость lifecycle

Покрывает `R17`.

Это финальный узел CORE.

Требует:

```text
P13 App-owned delivery
+
P14 verification gate пройден
```

Прямое ребро `P12 → P15` удалено после аудита: предварительное наблюдение Amend на dev-site — полезный учебный шаг, но не отдельный технический prerequisite clean install. На чистом Site acceptance сам повторяет native Amend path.

Финал:

```text
чистый совместимый Frappe Site
+ committed lifecycle App
+ install-app / migrate
+ Standard Purchase Request metadata/DocPerm/amended_from
+ missing Role records созданы Standard DocType sync
+ ordered PR-* Workflow State / Workflow fixtures
+ tests
+ requester/approver/senior scenario
+ Workflow Action observation
+ Cancel / Amend observed path
= воспроизводимый lifecycle CORE
```

На clean Site запрещено вручную достраивать обязательный Workflow, Roles, Workflow States, permissions, второе state field или `amended_from`.

Это не production deployment test.

---

# 4. Граф зависимостей

```text
P00 App/Site prerequisite
  ↓
P01 Purchase Request
  ├────────→ P02A requester = owner
  ├────────→ P02B plain namespaced status
  └────────→ P03 base Roles + DocPerm

P02B ──────┐
P03 ───────┴──→ P04 prove plain status limitation
                  ↓
             P05 base Workflow + one Standard state field
               ├────────→ P06 Workflow Action
               ├────────→ P07 conditional Senior approval
               └────────→ P09 Rejected + resubmit

P02A ──────┐
P05 ───────┴──→ P08 self approval

P05 ───────┐
P07 ───────┴──→ P10 Is Submittable + Submit + amended_from capability
                  ↓
             P11 Cancelled + Cancel
                  ↓
             P12 Amend responsibility + Amend

P08 ───────┐
P09 ───────┼──→ P13 complete App-owned delivery
P12 ───────┘

P06 ───────┐
P13 ───────┴──→ P14 verification gate
                  ↓
             P15 clean Site acceptance
```

Главное отличие от предыдущей версии: owner/self-approval и ordinary-status ветки больше не склеены искусственно.

---

# 5. Таблица рёбер

| Откуда | Куда | Тип | Почему зависимость реальная |
|---|---|---|---|
| P00 | P01 | STRUCTURAL | Нужен App/Site, чтобы создать Standard DocType |
| P01 | P02A | STRUCTURAL | owner semantics относится к существующему Purchase Request |
| P01 | P02B | STRUCTURAL | status относится к существующему Purchase Request |
| P01 | P03 | STRUCTURAL | DocPerm настраивается для существующего DocType |
| P02B | P04 | VERIFICATION | Нужен обычный state field для отрицательного опыта |
| P03 | P04 | VERIFICATION | Нужен реальный пользователь с Write |
| P04 | P05 | ARCHITECTURAL_CAUSE | Именно ограничение plain status создаёт ответственность transition policy |
| P05 | P06 | PROCESS | Workflow Action возникает из работающего Workflow |
| P05 | P07 | PROCESS | Condition/Senior branch расширяют существующий Workflow |
| P02A | P08 | PROCESS | Self approval привязан к requester = owner |
| P05 | P08 | PROCESS | Нужен реальный Workflow transition |
| P05 | P09 | PROCESS | Rejected/resubmit — ветка Workflow state machine |
| P05 | P10 | TRANSACTIONAL | Final approval должен быть Workflow state |
| P07 | P10 | PROCESS | При переходе к Submitted уже обязаны сохраниться оба final approval path |
| P10 | P11 | TRANSACTIONAL | Cancel policy имеет смысл только после Submitted fact |
| P11 | P12 | TRANSACTIONAL | Amend требует Cancelled original |
| P08 | P13 | DELIVERY | Self-approval policy входит в финальный Workflow source |
| P09 | P13 | DELIVERY | Resubmit transition входит в финальный Workflow source |
| P12 | P13 | DELIVERY | Через полный transactional path собраны финальные metadata/permissions/states |
| P06 | P14 | VERIFICATION | Verification gate включает штатный Workflow Action runtime branch |
| P13 | P14 | VERIFICATION | Contracts проверяются на полном обязательном App-owned config |
| P13 | P15 | ACCEPTANCE | Clean Site должен воспроизвести source из App |
| P14 | P15 | ACCEPTANCE | Перед финальной приёмкой contracts/observed checks должны быть пройдены |

---

# 6. Что намеренно НЕ является зависимостью

## Requester semantics не блокирует появление ordinary status

Неверно склеивать:

```text
requester = owner
+
status
→ один обязательный P02
```

Почему: это две независимые ответственности.

Правильно:

```text
P02A requester = owner
→ нужен P08 self approval

P02B status
→ нужен P04/P05
```

---

## Workflow Action не блокирует self approval

Неверно:

```text
P06 Workflow Action
→ P08 self approval
```

Почему: self approval проверяет серверный Workflow transition; Workflow Action — отдельный runtime presentation/queue mechanism.

Правильно:

```text
P02A requester = owner
+
P05 Workflow
→ P08
```

---

## Rejected/resubmit не нужен для появления Submittable

`P09` обязателен для полного процесса, но системная возможность final Approved стать Submitted не зависит технически от reject branch.

Поэтому нет искусственного ребра:

```text
P09 → P10
```

При этом `P09 → P13` обязательно: resubmit должен попасть в финальную поставляемую Workflow-конфигурацию.

---

## Self approval не блокирует появление Submit

`P08` является обязательным contract процесса, но техническая возможность сделать final state Submitted зависит от Workflow route и DocPerm, а не от self-approval ветки.

Поэтому нет искусственного ребра:

```text
P08 → P10
```

Но `P08 → P13` есть, потому что self-approval flags входят в финальный source Workflow.

---

## Dev-site Amend observation не является отдельным prerequisite clean install

После аудита удалено прямое ребро:

```text
P12 → P15
```

Почему: `P13` уже содержит финальный Amend policy/source, `P14` проверяет обязательный contract, а clean acceptance `P15` само повторяет native Amend scenario на новом Site.

Предварительное наблюдение в P12 полезно методически, но это не независимая delivery dependency.

---

## Role fixture не является prerequisite delivery

В текущем CORE нет ребра:

```text
Role fixture
→ P13
```

Роли уже перечислены в Standard Purchase Request DocPerm, а текущий Frappe создаёт отсутствующие Role при DocType sync.

Отдельный Role fixture появится только если у Role возникнет новая App-owned responsibility, которую DocPerm sync не выражает.

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

# 7. Архитектурные развилки вне основного графа

`D00–D04` из матрицы не превращаются в последовательные этапы автоматически.

Они включаются только новым требованием:

```text
D00 поддерживаемая старая версия + реальные данные
→ migration plan / patch analysis

D01 безопасное post-submit business field
→ field-specific Allow on Submit

D02 requester != owner
→ отдельный requester field + новый self-approval analysis

D03 LIMIT становится админ-настройкой
→ Settings candidate

D04 динамический approval route
→ повторный fit analysis Workflow
```

Ни одна ветка GATE не включена в основной граф по умолчанию.

---

# 8. Результаты злого аудита графа

Аудит нашёл и исправил следующие реальные дефекты:

```text
1. P02 ложно склеивал requester=owner и status
   → разделено на P02A / P02B

2. Workflow State namespace решался слишком поздно в delivery
   → App-scoped physical values фиксируются до базового Workflow

3. P13 не зависел от self-approval и resubmit веток
   → добавлены P08 → P13 и P09 → P13

4. P12 → P15 было методическим повтором, а не реальной dependency
   → прямое ребро удалено

5. Role fixtures дублировали Standard DocPerm delivery
   → Role fixture удалён из CORE delivery model

6. Is Submittable скрыто приносил amended_from
   → capability зафиксирована в P10, вручную field не создаётся

7. Cancelled allow_edit был заранее прибит к роли
   → P11 вводит текущую cancel-policy, P12 меняет её только из нового Amend requirement
```

Циклов после исправлений нет.

---

# 9. Gate перед roadmap

Перед построением `PRACTICUM_ROADMAP.md` нужно подтвердить:

```text
1. Каждый P-узел производит наблюдаемый результат, а не просто знакомит с функцией?
2. P02A requester semantics независима от P02B status?
3. P02B использует App-scoped physical state values до Workflow?
4. P04 действительно предшествует Workflow и объясняет его появление?
5. P05 не создаёт второго state field и не откладывает namespace decision до delivery?
6. P06 не используется как ACL?
7. P07 впервые вводит Senior role/state?
8. P08 зависит от requester=owner, а не от Workflow Action?
9. P09 не смешивает Rejected и Cancelled и входит в final delivery?
10. P10 вводит только Is Submittable/Submit responsibility, без преждевременного Cancel/Amend?
11. P10 признаёт auto-added amended_from, но не считает его бизнес-разрешением Amend?
12. P11 впервые вводит Cancelled и только необходимый Cancel DocPerm?
13. Senior не получает Cancel без требования?
14. P12 впервые вводит Amend responsibility и Amend DocPerm Requester?
15. Cancelled allow_edit меняется только вместе с новой Amend responsibility?
16. Amend permission bit не выдаётся за более сильную гарантию, чем доказано Frappe?
17. Cancel и Amend принадлежат разным явно принятым обязанностям?
18. P13 собирает self-approval + resubmit + полный transactional path?
19. P13 не использует Role fixture без дополнительной ответственности?
20. P13 имеет fixture dependency order Workflow State → Workflow?
21. P14 разделяет server contracts и UI/observed checks?
22. P15 не зависит от предварительного dev-наблюдения только ради порядка занятий?
23. P15 зависит только от обязательного CORE, а не от NEXT?
24. Ни один GATE не превратился в обязательный этап без нового требования?
25. Граф не содержит циклов?
26. Рёбра различают structural/runtime dependency и architectural cause?
27. Граф описывает зависимости результатов, а не желаемый порядок лекций?
```

После текущего аудита все ответы — `да`.

Граф считается **готовым основанием для PRACTICUM_ROADMAP**, но сам roadmap ещё не создан.