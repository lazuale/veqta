# Дорожная карта второго учебного практикума Frappe

Статус: **проект маршрута, полученный из аудированного dependency graph**.

Продолжает:

- [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md);
- [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md);
- [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md).

Нормативная база:

- [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md);
- [`13_ROLE_PROVISIONING.md`](../frappe-architecture-standard/13_ROLE_PROVISIONING.md).

Этот документ уже является **практическим маршрутом**, но ещё не является точной исполняемой инструкцией. Конкретные имена App/Site, точные поля, LIMIT, fixture hook, команды и контрольные записи фиксируются следующим слоем — executable specification.

---

# 1. Что именно изучает второй практикум

Первый CORE отвечал на вопрос:

> Как правильно построить собственную модель Frappe App?

Второй отвечает на другой вопрос:

> Как обычный Document превращается в управляемый процесс и затем в зафиксированный транзакционный факт, не создавая собственный workflow engine?

Учебная ось:

```text
обычный Document
→ обычное business state
→ доказанная граница обычного status
→ Workflow
→ process policies
→ conditional approval
→ final approval как Submitted fact
→ Cancel
→ Amend
→ App-owned delivery
→ automated contracts
→ clean Site acceptance
```

Практикум не является каталогом функций `Workflow → Notification → Assignment → Print`.

---

# 2. Как из dependency graph получены этапы

Узел графа — архитектурный результат. Этап roadmap — законченный практический кусок работы.

Поэтому соответствие не обязано быть `один Pxx = один урок`.

Принятая группировка:

| Этап | Узлы графа | Основной результат |
|---|---|---|
| `S00` | `P00` | второй App/Site готов к lifecycle-практикуму |
| `S01` | `P01 + P02A + P02B` | минимальный Purchase Request, owner-semantics и plain status |
| `S02` | `P03 + P04` | базовые permissions + доказанная граница обычного status |
| `S03` | `P05 + P06 + P09` | базовый Workflow, Workflow Action и reject/resubmit |
| `S04` | `P08` | self approval policy доказана server-side |
| `S05` | `P07` | условный второй уровень approval |
| `S06` | `P10` | final approval становится Submitted fact |
| `S07A` | `P11` | отдельная политика Cancel |
| `S07B` | `P12` | отдельная ответственность Amend |
| `S08` | `P13` | весь lifecycle имеет App-owned delivery path |
| `S09` | `P14` | server contracts + observed/UI checks |
| `S10` | `P15` | clean Site acceptance |

Почему `S03` объединяет три узла:

```text
P05 = сам базовый Workflow
P06 = штатная рабочая очередь этого Workflow
P09 = завершённый reject/resubmit path
```

Вместе они дают первый законченный простой approval-процесс. Отдельные `S06 Workflow Action` и `S09 Rejected` как самостоятельные «уроки функций» были бы искусственными.

Почему `S04` и `S05` разделены:

```text
self approval
≠
amount-based routing
```

Это две разные ответственности. По dependency graph обе возможны после базового Workflow. Roadmap проходит `S04` раньше `S05` **методически**, чтобы сначала закрыть policy безопасности простого approval, а затем усложнить маршрут. Это не выдаётся за runtime prerequisite: `S04` и `S05` можно поменять местами без нарушения архитектуры.

---

# 3. Полный маршрут

```text
S00  второй App/Site
 ↓
S01  Purchase Request + owner + plain status
 ↓
S02  Role/DocPerm + отрицательный опыт plain status
 ↓
S03  базовый Workflow + Action + Reject/Resubmit
 ↓
S04  self approval policy
 ↓       методический порядок; не runtime dependency
S05  conditional Senior approval
 ↓
S06  Is Submittable + Submit
 ↓
S07A Cancel
 ↓
S07B Amend
 ↓
S08  App-owned lifecycle delivery
 ↓
S09  automated contracts + observed checks
 ↓
S10  clean Site acceptance
```

При строгом чтении dependency graph:

```text
S04 self approval
и
S05 conditional Senior approval
```

являются параллельными расширениями `S03`; обязательным join они становятся только перед `S08`.

---

# 4. S00 — подготовить второй учебный App и Site

**Опорный узел:** `P00`.

## Вход

Ученик уже прошёл первый CORE и понимает:

```text
Bench
Site
App
Module
Standard DocType
developer mode
Git
install-app
migrate
```

## Требование

Второй практикум не должен зависеть от предметной модели `rental_training`.

Нужны отдельные:

```text
training App
training Site
Module
Git source
```

## Ученик делает

1. Создаёт второй нейтральный учебный App.
2. Устанавливает его на отдельный dev/test Site.
3. Проверяет Module и Git.
4. Включает developer mode только там, где он нужен для разработки Standard metadata.
5. Не устанавливает ERPNext или первый учебный App как скрытую зависимость.

## Что здесь НЕ изучается заново

Не повторяется полный OS/Bench bootstrap первого практикума.

Если совместимой среды нет, используется уже принятая инструкция первого CORE; второй практикум не превращается в повторный курс установки Frappe.

## Результат

```text
совместимый Frappe v16 Bench
+
отдельный учебный Site
+
отдельный App
= место для lifecycle-модели
```

## ГОТОВО

Ученик может показать App source и объяснить, почему новый Site не равен новому App.

---

# 5. S01 — создать обычный Purchase Request до Workflow

**Опорные узлы:** `P01 + P02A + P02B`.

**Покрывает:** `R01–R03`.

## Вход

Готов второй App/Site.

## Требование

Сотруднику нужно создать внутреннюю заявку на закупку и понимать её текущее состояние.

Пока нет требования ограничивать переходы по ролям.

## Ученик делает

Создаёт один Standard DocType:

```text
Purchase Request
├── subject
├── description
├── requested_amount
├── needed_by
└── status
```

`status` — обычный Standard `Select`.

Persisted values сразу App-scoped:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
```

Короткие слова:

```text
Draft
Pending Manager
Approved
Rejected
```

используются только как читаемые aliases в схемах и объяснениях.

## Requester semantics

Отдельного поля `requester` нет.

CORE принимает:

```text
requester = Document.owner
```

Это доказывается на реальных Documents, а не просто объявляется текстом.

## Что намеренно отсутствует

```text
Workflow
Workflow State Field workflow_state
Senior Purchase Approver
PR Pending Senior
Is Submittable
Cancelled
Submit / Cancel / Amend
Approval Log
```

## Наблюдаемый результат

Пользователь может создать обычный Purchase Request и вручную выбирать допустимый `status` как значение обычного поля.

## Проверка

Нужно показать:

```text
Purchase Request существует как Standard DocType
status существует в Standard metadata
owner автоматически существует как системное поле Document
нет второго workflow_state field
нет Workflow
```

## Архитектурный вывод

```text
нужно хранить состояние
→ status

наличие нескольких states
≠ автоматически Workflow
```

---

# 6. S02 — настроить базовый доступ и доказать, почему status недостаточно

**Опорные узлы:** `P03 + P04`.

**Покрывает:** `R04–R05`.

## Вход

Есть обычный Purchase Request с обычным `status`.

## Новое требование доступа

Появляются две роли:

```text
Purchase Requester
Purchase Approver
```

На этом шаге они выражают только базовую возможность работать с DocType.

Ещё нет отдельного процессного права `Approve`.

## Ученик делает

1. Создаёт роли на dev-site как setup для настройки Standard DocPerm.
2. Настраивает default `DocType Permissions` Purchase Request.
3. Создаёт Site-local test Users для Requester и Approver.
4. Доказывает фактический Read/Create/Write access.
5. Проверяет Git: default DocPerm находятся в Standard DocType JSON.

## Delivery-модель ролей

Не добавляются:

```text
Role fixture
fixtures/role.json
export-fixtures Role
```

Role names уже находятся в Standard DocPerm; clean-install delivery будет доказан на `S08/S10` через штатный Standard DocType sync.

## Контрольный отрицательный опыт

Под пользователем с обычным `Write` и **без Workflow**:

```text
PR Draft
→ вручную поставить PR Approved
→ обычный Save
```

должен технически пройти, если никакое другое правило этому не мешает.

Эту проверку полезно увидеть и через Desk, и обычным Document path, чтобы не спутать ограничение UI с моделью данных.

После опыта контрольную запись можно удалить/пересоздать как disposable dev data.

## Что доказано

```text
DocPerm
→ может ли роль редактировать Purchase Request вообще

но

DocPerm + Select status
→ не выражают допустимость конкретного process transition
```

## Новая ответственность

Теперь требование уже звучит иначе:

```text
Requester:
Draft → Pending Manager

Approver:
Pending Manager → Approved / Rejected

Requester:
не может Pending Manager → Approved
```

Именно это создаёт основание следующего этапа.

## Архитектурный вывод

Workflow появляется не потому, что «пора его изучить», а потому что доказана responsibility:

```text
role-controlled transition policy
```

---

# 7. S03 — превратить status в управляемый базовый Workflow

**Опорные узлы:** `P05 + P06 + P09`.

**Покрывает:** `R06–R08`, `R11`.

## Вход

Есть доказанная граница plain status.

## Требование

Нужен минимальный рабочий процесс:

```text
Requester:
Draft → Pending Manager

Approver:
Pending Manager → Approved
Pending Manager → Rejected

Requester:
Rejected → исправление → Pending Manager
```

## Ученик делает

### 1. Создаёт App-scoped Workflow State records

Для уже существующих persisted values:

```text
PR Draft
PR Pending Manager
PR Approved
PR Rejected
```

### 2. Создаёт Workflow

Критическое решение:

```text
Workflow State Field = status
```

Существующий Standard:

```text
status : Select
```

остаётся тем же полем.

Не создаётся обязательный:

```text
workflow_state : Link → Workflow State
```

### 3. Задаёт state/edit policy

Для каждого Workflow Document State осознанно выбирается `Only Allow Edit For`.

Эта настройка не объявляется самостоятельной доказанной server ACL.

### 4. Задаёт transitions

Минимум:

```text
PR Draft
→ Submit for Review
→ PR Pending Manager

PR Pending Manager
→ Approve
→ PR Approved

PR Pending Manager
→ Reject
→ PR Rejected

PR Rejected
→ Submit for Review
→ PR Pending Manager
```

Пока все эти states остаются `docstatus 0`.

## Workflow Action

После появления pending action ученик наблюдает штатный `Workflow Action`.

Проверяется:

```text
permitted role видит ожидающее действие
```

но одновременно фиксируется граница:

```text
Workflow Action
≠ окончательная ACL фактического transition
```

## Rejected

На этом этапе `Rejected` окончательно отделяется от системного `Cancelled`:

```text
PR Rejected
→ docstatus 0
→ Requester может исправить draft-state
→ явный resubmit transition
```

## Проверка

Должны работать:

```text
Requester: Draft → Pending Manager
Approver: Pending Manager → Approved
Approver: Pending Manager → Rejected
Requester: Rejected → Pending Manager
```

и не должен появиться второй state field.

## Архитектурный вывод

```text
status
→ хранит текущее business state

Workflow
→ владеет политикой transitions

Workflow Action
→ отображает ожидаемую работу
→ не заменяет server transition validation
```

---

# 8. S04 — запретить self approval штатной политикой Workflow

**Опорный узел:** `P08`.

**Покрывает:** `R10`.

## Вход

Есть базовый Workflow и ранее принято:

```text
requester = owner
```

## Новое требование

Пользователь может одновременно иметь:

```text
Purchase Requester
+
Purchase Approver
```

но не должен одобрять собственную заявку.

## Ученик делает

1. Создаёт/использует dual-role test User.
2. Создаёт Purchase Request именно этим пользователем, чтобы он стал `owner`.
3. Для Approve transition использует штатную self-approval policy Workflow.
4. Не пишет собственный `doc.owner == frappe.session.user` validator.

## Проверка

```text
owner + Approver role
+ allow_self_approval = false
→ фактический apply_workflow Approve отклоняется
```

Другой Approver должен выполнить тот же transition успешно.

Дополнительно можно увидеть role-permitted Workflow Action у dual-role пользователя, если текущий runtime его создаёт. Это специально подчёркивает:

```text
наличие action
≠ разрешение apply_workflow
```

## Архитектурный вывод

Не писать собственную проверку, пока штатный Workflow уже выражает именно эту policy.

---

# 9. S05 — добавить второй уровень approval только для большой суммы

**Опорный узел:** `P07`.

**Покрывает:** `R09`.

## Вход

Работает базовый Workflow.

`S04` уже пройден по выбранному roadmap-порядку, но технически не является prerequisite этого этапа.

## Новое требование

```text
requested_amount <= LIMIT
→ Purchase Approver может завершить approval

requested_amount > LIMIT
→ после Purchase Approver нужен Senior Purchase Approver
```

## Только теперь появляются

```text
Senior Purchase Approver
PR Pending Senior
Workflow Transition Condition
```

## Ученик делает

1. Добавляет `Senior Purchase Approver` в Standard DocPerm Purchase Request.
2. Добавляет `PR Pending Senior` в допустимые persisted values `status`.
3. Создаёт соответствующий Workflow State record.
4. Расширяет Workflow двумя ветками по `requested_amount`.
5. Создаёт Site-local Senior test User.

## Результат

```text
маленькая заявка
Pending Manager
→ Approved

большая заявка
Pending Manager
→ Pending Senior
→ Approved
```

## Что не создаётся

```text
Approval Rule Engine
Approval Matrix DocType
Settings для LIMIT
custom Python router
```

LIMIT пока является фиксированной частью учебного требования.

## Проверка

Нужно создать две реальные заявки по разные стороны LIMIT и доказать, что доступны разные transitions.

## Архитектурный вывод

Workflow Condition используется только после появления настоящей условной ветки процесса.

---

# 10. S06 — сделать final approval зафиксированным Submitted fact

**Опорный узел:** `P10`.

**Покрывает:** `R12`.

## Вход

Работают оба final approval path:

```text
маленький → Approver
большой   → Senior Approver
```

До этого момента `PR Approved` всё ещё был workflow-state с `docstatus 0`.

## Новое требование

После окончательного одобрения:

```text
subject / description / amount / needed_by
```

считаются зафиксированным разрешением и не должны бесследно переписываться обычным Save.

## Ученик делает

1. Включает `Is Submittable` у Standard Purchase Request.
2. Проверяет автоматически появившийся Standard Link `amended_from`.
3. Меняет mapping Workflow State:

```text
PR Approved → Doc Status 1
```

4. Выдаёт `Submit` только ролям, которые реально выполняют final approval:

```text
Purchase Approver        → Submit yes
Senior Purchase Approver → Submit yes
Purchase Requester       → Submit no
```

5. Проверяет оба final path через реальный Workflow.

## Что пока НЕ появляется

```text
PR Cancelled
Cancel permission
Amend permission
```

Техническая capability `amended_from` уже существует, но бизнес ещё не сформулировал обязанность Amend.

## Проверка

```text
small final approval → docstatus 1
large final approval → docstatus 1
Requester            → no Submit
```

После Submitted обычный Save смысловых полей не используется как способ исправления согласованного факта.

## Архитектурный вывод

```text
Approved = docstatus 1
```

не из-за названия `Approved`, а только из нового требования о фиксации факта.

---

# 11. S07A — добавить официальную отмену Submitted approval

**Опорный узел:** `P11`.

**Покрывает:** `R13`.

## Вход

Есть Submitted Purchase Request:

```text
PR Approved
→ docstatus 1
```

## Новое требование

Одобренное разрешение иногда нужно официально отменить, сохранив сам факт его существования.

## Ученик делает

Только теперь добавляет:

```text
PR Cancelled
Workflow State PR Cancelled → docstatus 2
status.Allow on Submit = yes
```

и transition:

```text
PR Approved
→ Cancel
→ PR Cancelled
```

## Permission responsibility

```text
Purchase Approver        → Cancel yes
Senior Purchase Approver → Cancel no
Purchase Requester       → Cancel no
```

Senior роль не получает Cancel просто потому, что умеет final approve дорогую заявку.

На этом шаге state/edit policy `PR Cancelled` соответствует текущей ответственности отмены.

## Проверка

```text
Purchase Approver может Approved → Cancelled
Requester не может Cancel
Senior не получает лишний Cancel
Cancelled → docstatus 2
Draft → Cancelled нельзя
Submitted → Draft нельзя
```

## Архитектурный вывод

Submit и Cancel — разные system operations и разные responsibilities.

---

# 12. S07B — исправить отменённую заявку через Amend

**Опорный узел:** `P12`.

**Покрывает:** `R14`.

**Зависит от:** `S07A`.

## Новое требование

После отмены requester должен создать исправленную версию, не переписывая исходный отменённый факт.

## Ученик делает

Выдаёт отдельный `Amend` DocPerm:

```text
Purchase Requester       → Amend yes
Purchase Approver        → Amend no
Senior Purchase Approver → Amend no
```

У Requester уже есть `Create` из базовой permission-модели.

State/edit policy `PR Cancelled` пересматривается под новую пользовательскую ответственность Requester.

## Важно

`amended_from` **не создаётся вручную**. Оно уже является Standard field, появившимся из `Is Submittable`.

## Реальный Desk scenario обязателен

```text
Approved original
→ Purchase Approver Cancel
→ Cancelled original
→ Purchase Requester Amend
→ новый Draft Document
→ amended_from = original
→ исправление
→ Submit for Review
```

Roadmap не предполагает, что `No Copy` магически сбрасывает workflow-state при Amend. Фактический native path проверяется на принятой версии Frappe.

## Проверка

Нужно показать одновременно:

```text
permission matrix Amend
+
новый Document имеет docstatus 0
+
amended_from ссылается на original
+
новая версия снова входит в Workflow
```

## Архитектурный вывод

```text
Cancel
≠ Amend
```

и наличие технической capability Framework не означает автоматической выдачи бизнес-права.

---

# 13. S08 — доказать App-owned delivery всего lifecycle

**Опорный узел:** `P13`.

**Покрывает:** `R15`.

## Вход

Должны быть закончены все обязательные ветки:

```text
self approval
reject/resubmit
Senior branch
Submit
Cancel
Amend
```

## Требование

Процесс не должен существовать только потому, что его один раз накликали на dev-site.

## Delivery manifest

```text
Purchase Request schema / status / amended_from / DocPerm
→ Standard DocType JSON

Purchase Requester / Purchase Approver / Senior Purchase Approver
→ role names в Standard DocPerm
→ missing Role создаёт Frappe при Standard DocType sync

PR-* Workflow State records
→ filtered Workflow State fixture

Workflow + child states/transitions/conditions/policies
→ filtered Workflow fixture

Workflow Actions
→ runtime Site data

Users/passwords/runtime Purchase Requests
→ Site-local
```

## Ученик делает

1. Проверяет Standard Purchase Request JSON.
2. Доказывает отсутствие необходимости Role fixture.
3. Настраивает filtered fixture только для собственных `PR-* Workflow State`.
4. Настраивает filtered fixture для ровно одного обязательного Workflow.
5. Обеспечивает dependency order:

```text
Workflow State
→ Workflow
```

штатным fixture ordering/prefix механизмом принятой версии Frappe.
6. Выполняет `export-fixtures`.
7. Проверяет содержимое fixture-файлов.
8. Повторяет export и требует объяснимый clean Git.

## Запрещено

```text
fixtures = все Role
fixtures = все Workflow State
fixtures = все Workflow
экспорт Users
экспорт Workflow Actions
ручные post-install клики как скрытая часть продукта
```

## Проверка role delivery

Source role names должен быть виден в Standard DocPerm. Отдельный `role.json` для этих ролей отсутствует.

Полное доказательство появления missing Role переносится в clean-site `S10`.

## Архитектурный вывод

Fixtures используются для database configuration, которой действительно не владеет Standard metadata собственного DocType; они не должны дублировать уже существующий Frappe delivery mechanism.

---

# 14. S09 — превратить lifecycle в автоматические контракты

**Опорный узел:** `P14`.

**Покрывает:** `R16`.

## Вход

Полная mandatory lifecycle-конфигурация уже App-owned.

## Требование

Практикум не может завершаться доказательством «я прокликал Workflow и вроде работает».

## Механизм

Текущий Frappe v16 testing baseline:

```text
IntegrationTestCase
+
Bench test runner
```

## Минимальные server contracts

Автоматически проверяются собственные контракты App:

```text
Requester может Draft → Pending Manager
Requester не может Approve
Approver может Approve / Reject
Rejected = docstatus 0
Rejected можно снова отправить
маленькая сумма не требует Senior
большая сумма требует Pending Senior
Senior завершает большой approval
self approval отклоняется фактическим apply_workflow
Approved после S06 = docstatus 1
Requester не имеет Submit/Cancel
Purchase Approver имеет нужные Submit/Cancel
Senior имеет Submit, но не Cancel
Requester имеет Amend после S07B
Approver/Senior не получают Amend без требования
Draft нельзя сразу Cancel
Purchase Approver может Approved → Cancelled
Cancelled = docstatus 2
Cancelled не получает нелегальный transition
status остаётся одним Standard field
обязательного workflow_state Custom Field нет
mandatory Workflow config существует
Role records соответствуют Standard DocPerm
```

## Что проверяется отдельно как observed/UI behavior

```text
Only Allow Edit For отражается в Desk ожидаемо
Workflow Action отображается для permitted role
Desk Amend создаёт новую draft-запись с amended_from
```

Эти observed checks не выдаются за неподтверждённую самостоятельную server ACL.

## Чего не тестируем

Не пишем tests вида:

```text
Frappe вообще умеет создавать Workflow State
Frappe вообще умеет хранить owner
Frappe вообще умеет делать Link
```

Тестируются наши конфигурационные и lifecycle contracts.

## Результат

```text
изменили mandatory process неправильно
→ test красный
```

а не только «сломалась кнопка в Desk».

---

# 15. S10 — доказать lifecycle на новом чистом Site

**Опорный узел:** `P15`.

**Покрывает:** `R17`.

Это финальный экзамен второго CORE.

## Вход

```text
App source clean/committed
S08 delivery audit пройден
S09 tests green
```

## Новый acceptance Site

Создаётся новый совместимый Frappe Site, где lifecycle никогда не настраивался вручную.

До установки второго App нужно доказать отсутствие:

```text
Purchase Request
Purchase Requester
Purchase Approver
Senior Purchase Approver
PR-* Workflow State
обязательного Workflow
```

## Установка

```text
install-app
→ Standard DocType sync
→ Role из DocPerm
→ fixture Workflow State
→ fixture Workflow
```

Никаких ручных восстановительных действий между этими шагами.

После установки выполняется обычный `migrate` update-path и полный App test suite.

## Что должно существовать без ручной настройки

```text
Standard Purchase Request
status и полный DocPerm
amended_from
три обязательные Role
PR-* Workflow State records
Workflow со states/transitions/conditions/policies
```

## Site-local создаётся только для проверки

```text
Requester test User
Approver test User
Senior test User
runtime Purchase Requests
пароли
local allow_tests
```

## Финальный реальный сценарий

Нужно пройти минимум:

```text
1. Requester создаёт небольшую заявку.
2. Отправляет её Manager/Approver.
3. Approver final approves → docstatus 1.
4. Создаётся большая заявка.
5. Approver переводит её в Pending Senior.
6. Senior final approves → docstatus 1.
7. Dual-role owner не может self approve.
8. Заявка проходит Reject → исправление → resubmit.
9. Purchase Approver отменяет Submitted заявку → docstatus 2.
10. Requester делает Amend.
11. Новая версия имеет amended_from и снова проходит Workflow.
12. Workflow Action наблюдается как штатная рабочая очередь.
```

После runtime данных полный test suite запускается повторно.

## Критерий провала

S10 считается `НЕ ГОТОВО`, если после `install-app` приходится вручную:

```text
создавать обязательные Role
создавать Workflow State
создавать Workflow
добавлять workflow_state Custom Field
добавлять amended_from
восстанавливать DocPerm
править database SQL
```

## Что S10 не доказывает

```text
production deployment
reverse proxy
TLS
backup/restore
HA
CI/CD
отдельный сервер
```

Это acceptance App на чистом Site, а не эксплуатационный production test.

---

# 16. NEXT не входит в обязательный маршрут

После завершения `S10` можно отдельно оценить новые требования.

| Требование | Первый кандидат | Почему не CORE |
|---|---|---|
| после approval назначить закупщика | Assignment / ToDo | операционная работа после lifecycle |
| напомнить до needed_by | Notification | отдельная delivery/scheduler semantics |
| приложить/обсудить/посмотреть историю | File / Comment / Version | спутники Document, не approval engine |
| распечатать утверждённую заявку | Standard Print / Print Format | presentation requirement |

Они не становятся `S11–S14` автоматически.

---

# 17. GATE не активируется без нового требования

## Requester перестал быть owner

Появляется отдельное business field requester и повторно анализируется self approval.

## LIMIT должен менять администратор

Тогда рассматривается `Single DocType` Settings; фиксированное число не превращается в Settings заранее.

## После Submit можно менять отдельное безопасное поле

Только это поле становится кандидатом `Allow on Submit`; смысловые поля согласованного разрешения не открываются массово.

## Approval route стал динамическим

Если маршрут больше не выражается естественно Workflow states/transitions/conditions, выполняется новый fit analysis. Наличие слова `approval` не заставляет бесконечно растягивать Standard Workflow.

## Поддерживается предыдущая production-версия с реальными данными

Тогда изменения lifecycle/metadata получают настоящий migration analysis и при необходимости patch. Disposable учебные записи не создают фиктивную migration responsibility.

---

# 18. Что roadmap намеренно не включает

```text
REST API
custom whitelisted API
Webhook
background jobs
custom scheduler
foreign DocType extension
doc_events
extend_doctype_class
override_doctype_class
Web Form / Portal
custom frontend
Query Report / Script Report
complex User Permission
external integration
concurrency / locking
production deployment
```

Это кандидаты других архитектурных практикумов.

---

# 19. Контроль roadmap перед executable specification

Перед следующим слоем нужно ответить `да`:

```text
1. Ни один этап не появился только ради функции Frappe?
2. S01 заканчивается обычным status без Workflow?
3. S02 реально доказывает границу plain status до включения Workflow?
4. Role names доставляются Standard DocPerm, а не дублирующим fixture?
5. S03 использует один Standard status как Workflow State Field?
6. Rejected остаётся docstatus 0 и имеет явный resubmit path?
7. Workflow Action не выдаётся за server ACL?
8. Self approval и conditional routing остаются разными responsibilities?
9. Порядок S04/S05 явно методический, а не выдуманный runtime edge?
10. Senior role/state появляются только в S05?
11. Approved становится Submitted только в S06?
12. amended_from не создаётся вручную?
13. Cancel появляется только в S07A?
14. Amend permission появляется только в S07B?
15. S08 собирает полный Workflow, включая self approval и resubmit?
16. fixtures не дублируют Role provisioning Standard DocType?
17. S09 разделяет server contracts и observed/UI checks?
18. S10 начинается с действительно чистого Site?
19. S10 не требует ручной обязательной настройки после install-app?
20. NEXT/GATE не превратились в скрытые mandatory stages?
21. API/async/extension/integration не добавлены ради покрытия?
```

Если хотя бы один ответ отрицательный, сначала исправляется roadmap или более ранний архитектурный слой.

Только после прохождения этого gate создаётся точная executable specification второго практикума.
