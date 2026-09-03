# Матрица требований второго учебного практикума Frappe

Статус: **черновик после архитектурного паспорта и первого злого аудита**.

Этот документ продолжает [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md).

Матрица пока **не является дорожной картой занятий**. Она отвечает на более ранний вопрос: действительно ли каждый механизм второго практикума появляется из нового требования, а не из желания «пройти Workflow» или другую возможность Frappe.

Для каждого требования фиксируется одна и та же цепочка:

```text
требование
    ↓
новая ответственность
    ↓
первый штатный механизм Frappe
    ↓
почему его семантика подходит
    ↓
где проходит граница
    ↓
что должно быть проверено наблюдаемым действием
```

Нормативная база:

- [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md);
- [`03_DOCUMENT_LIFECYCLE.md`](../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md);
- [`04_SECURITY.md`](../frappe-architecture-standard/04_SECURITY.md);
- [`05_TRANSACTIONS_ASYNC.md`](../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md);
- [`09_DEPLOYMENT_TESTING.md`](../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md);
- актуальная документация и исходный код Frappe v16.

---

# 1. Уровни требований

## CORE — обязательный lifecycle-маршрут

```text
R01–R16
```

CORE отвечает только на вопрос:

> Как собственный Frappe Document проходит от обычного рабочего состояния к управляемому согласованию и затем к системно зафиксированному транзакционному факту?

## NEXT — естественные операционные спутники

```text
N01–N04
```

Они не входят в CORE автоматически:

```text
N01 Assignment / ToDo
N02 Notification
N03 File / Comment / Version
N04 Print
```

## GATE — архитектурные развилки

```text
D00–D04
```

Механизм из GATE не включается только ради знакомства.

## За пределами второго практикума

Не входят автоматически:

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

## R01. Внутренняя заявка существует как самостоятельный Document

**Требование:** сотруднику нужен самостоятельный документ внутренней заявки на закупку.

Минимальные данные:

```text
subject
 description
 requested_amount
 needed_by
```

**Ответственность:** хранить одну заявку с собственной identity и lifecycle.

**Первый штатный механизм:** Standard `DocType` `Purchase Request` собственного учебного App.

**Почему подходит:** заявка создаётся, открывается, изменяется, согласуется и позднее может стать Submitted Document.

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

**Граница:** второй практикум не повторяет первый CORE через искусственно большую модель данных.

**Проверка:** создать Purchase Request через обычный Desk Form, найти его через List и повторно открыть.

---

## R02. Requester в CORE равен системному owner

**Требование:** заявку подаёт пользователь, который сам её создаёт.

**Ответственность:** определить, кто является инициатором для правил self approval.

**Первый механизм:** системный `Document.owner`.

CORE-семантика:

```text
requester = owner
```

**Почему подходит:** в обязательном сценарии отдельного предметного requester пока нет, а штатный Workflow Frappe проверяет self approval именно относительно `doc.owner`.

**Не создаётся:**

```text
requester → Link → User
```

только ради дублирования `owner`.

**Граница:** если пользователь должен создавать заявку от имени другого человека, `owner` перестаёт полностью выражать requester — см. `D02`.

**Проверка:** создать Document под конкретным test User и подтвердить, что `owner` равен этому пользователю.

---

# 3. CORE — состояние до Workflow

## R03. Пользователь видит обычное бизнес-состояние заявки

**Требование:** пользователь должен понимать, где находится заявка.

Начальный набор:

```text
Draft
Pending Manager
Approved
Rejected
```

На этом этапе намеренно отсутствуют:

```text
Pending Senior
Cancelled
Workflow
Is Submittable
```

**Ответственность:** хранить предметный смысл текущего рабочего состояния.

**Первый штатный механизм:** Standard поле `status` типа `Select`.

**Почему подходит:** пока требуется только хранение состояния; требований к разрешённым переходам ещё нет.

**Граница:** несколько значений поля сами по себе не являются причиной Workflow.

**Проверка:** создать записи с разными status и фильтровать их в List.

---

## R04. Обычный status не выдаётся за политику переходов

**Требование:** ученик должен увидеть ограничение обычного поля до появления Workflow.

**Ответственность:** отделить хранение state от управления transition.

**Первый механизм:** никакой новый механизм не добавляется; проверяется текущая модель.

**Контрольный отрицательный опыт:** пользователь, который имеет обычное `Write` на Purchase Request, технически может изменить:

```text
Pending Manager → Approved
```

если пока существует только обычный `status`.

**Архитектурный вывод:**

```text
Select/status
= хранит состояние

но не выражает автоматически
= кто имеет право выполнить конкретный переход
```

Это не «дыра Frappe». Это отсутствие соответствующего требования и механизма в нашей модели.

**Проверка:** до появления Workflow показать обычное изменение status и зафиксировать, почему этого уже недостаточно для нового процесса.

---

# 4. CORE — базовая безопасность процесса

## R05. Участники процесса имеют базовый доступ к Purchase Request

**Требование:** Requester и Approvers должны иметь право работать с Purchase Request, но это право не должно автоматически означать право выполнить любой workflow transition.

Обязательные роли:

```text
Purchase Requester
Purchase Approver
Senior Purchase Approver
```

**Ответственность:** базовая авторизация DocType.

**Первый механизм:** `Role` + `DocType Permissions`.

**Почему подходит:** DocPerm отвечает на вопрос, может ли пользователь вообще Read/Create/Write конкретный DocType.

**Граница:** право выполнить `Approve` не кодируется отдельным custom ACL, если им владеет Workflow transition.

**Проверка:** до Workflow подтвердить реальные CRUD-права тестовых пользователей через server-side permission checks и обычные операции Document.

---

# 5. CORE — появление Workflow

## R06. Переходы ограничены ролями

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

**Ответственность:** политика допустимых переходов между состояниями.

**Первый штатный механизм:** `Workflow`.

**Почему подходит:** появились одновременно states, transitions, allowed roles и ограничения действий.

**Не создаются:**

```text
custom approve() только ради обхода Workflow
if role == ... в разных lifecycle hooks
JS-кнопка как единственная защита
Approval Log как собственный workflow engine
```

**Граница:** если будущая логика согласования станет динамической и перестанет естественно выражаться Workflow states/transitions/conditions, решение пересматривается отдельно.

**Проверка:**

```text
Requester может: Draft → Pending Manager
Requester не может: Pending Manager → Approved
Purchase Approver может: Pending Manager → Approved/Rejected
```

Проверяется реальное действие Workflow, а не только наличие строк в настройке.

---

## R07. Состояние имеет один source of truth

**Требование:** после включения Workflow у Purchase Request не должно появиться второе конкурирующее поле состояния.

Запрещённая модель:

```text
status
+
workflow_state
```

если оба означают одно и то же состояние процесса.

**Ответственность:** единое хранение business/workflow state.

**Первый механизм:** существующее Standard поле `status` собственного DocType эволюционирует:

```text
до Workflow:
status = Select

после Workflow:
status = Link → Workflow State
Workflow State Field = status
```

**Почему именно так в этом практикуме:** Frappe v16.33.0 автоматически создаёт `Custom Field → Link → Workflow State`, если указанного Workflow State Field нет в Meta. Для собственного Standard DocType обязательное state field должно принадлежать App, а не появляться скрытым site-local Custom Field.

**Важно:** это архитектурное решение практикума, а не универсальный запрет Frappe на автоматически созданное workflow field для чужих/customized DocTypes.

**Предусловие:** необходимые `Workflow State` records существуют до перехода `status` на Link, а значения совпадают по именам.

**Граница:** реальная миграция поддерживаемых production-данных рассматривается отдельно в `D00`.

**Проверка:**

```text
Meta Purchase Request содержит один status
status = Link → Workflow State
Workflow.workflow_state_field = status
обязательного site-local Custom Field workflow_state нет
```

---

## R08. Ожидающее согласование видно штатным механизмом Workflow

**Требование:** Approver должен видеть, что у него есть ожидающее действие процесса.

**Ответственность:** рабочее представление доступных Workflow actions.

**Первый механизм:** штатный `Workflow Action`.

**Почему подходит:** это часть подсистемы Workflow Frappe; отдельный Approval Inbox для базового approval не нужен.

**Граница:** email не является обязательной предпосылкой CORE. `Send Email Alert` зависит от почтовой конфигурации, но сам Workflow должен быть проверяем и без неё.

**Проверка:** после отправки заявки Approver видит доступное Workflow Action/действие, Requester не получает действие, которого его роль не разрешает.

---

# 6. CORE — условное согласование

## R09. Дорогая заявка требует второго уровня approval

Новое требование:

```text
requested_amount <= LIMIT
→ достаточно Purchase Approver

requested_amount > LIMIT
→ после Purchase Approver нужен Senior Purchase Approver
```

**Ответственность:** условно выбрать допустимый дальнейший transition на основании данных текущего Document.

**Первый механизм:** `Condition` в Workflow Transition.

**Новая state появляется только теперь:**

```text
Pending Senior
```

Смысл:

```text
Draft
→ Pending Manager

небольшая сумма:
Pending Manager → Approved

большая сумма:
Pending Manager → Pending Senior → Approved
```

**Почему подходит:** Frappe Workflow condition вычисляется относительно Document и предназначен для условной применимости transition.

**Граница:** LIMIT пока является зафиксированной частью учебного сценария, а не настраиваемой бизнес-сущностью. Настройки — `D03`.

**Проверка:** две контрольные заявки по разные стороны LIMIT должны получить разные доступные переходы.

---

## R10. Self approval запрещён штатной политикой Workflow

**Требование:** пользователь с ролью Approver не может одобрить Purchase Request, который создал сам.

CORE-политика:

```text
allow_self_approval = false
```

**Ответственность:** запретить self approval конкретного workflow transition.

**Первый механизм:** штатный `Allow Self Approval` / `allow_self_approval` transition.

**Почему подходит:** текущая реализация Frappe проверяет пользователя относительно `doc.owner`, а R02 специально фиксирует requester = owner.

**Не пишется:**

```python
if doc.owner == frappe.session.user:
    frappe.throw(...)
```

пока штатный Workflow уже выражает требование.

**Граница:** если requester перестаёт совпадать с owner, см. `D02`.

**Проверка:** пользователь одновременно с ролью Requester + Approver создаёт заявку сам и не может выполнить собственный Approve; другой Approver может.

---

## R11. Rejected остаётся draft-состоянием процесса

**Требование:** отрицательное решение до окончательного approval не является системной отменой Submitted Document.

CORE-семантика:

```text
Rejected → docstatus 0
```

**Ответственность:** выразить отрицательное решение на рабочей draft-стадии.

**Первый механизм:** Workflow State `Rejected` с `Doc Status = 0`.

**Почему подходит:** документ ещё не был превращён в зафиксированный Submitted факт.

**Не используется:**

```text
Rejected = Cancelled
Rejected = docstatus 2
```

**Граница:** будущая матрица этапов может разрешить `Rejected → Pending Manager` после исправления заявки, но это должно быть отдельным принятым transition, а не неявным редактированием state.

**Проверка:** после Reject:

```text
status = Rejected
docstatus = 0
```

---

# 7. CORE — final approval становится транзакционным фактом

## R12. Окончательно одобренную заявку нельзя бесследно переписать

Новое требование:

> После final approval сумма, назначение и срок считаются согласованным разрешением на закупку. Обычный Save не должен позволять незаметно изменить смысл этого факта.

**Ответственность:** системно зафиксировать подтверждённый Document.

**Первый штатный механизм:** `Is Submittable` + `docstatus`.

Новая семантика:

```text
Draft            → docstatus 0
Pending Manager  → docstatus 0
Pending Senior   → docstatus 0
Rejected         → docstatus 0
Approved         → docstatus 1
Cancelled        → docstatus 2
```

**Почему подходит:** Frappe использует `Draft → Submitted → Cancelled` для транзакционного lifecycle и ограничивает обычное редактирование Submitted/Cancelled Documents.

**Ключевой вывод:**

```text
Approved получает docstatus 1
не потому, что называется Approved,
а потому что появилось отдельное требование зафиксировать этот факт.
```

**Граница:** Approved Purchase Request — это разрешение на закупку, а не сама покупка, платёж или складская операция.

**Проверка:** final approval должен приводить к реальному `submit()` path и `docstatus = 1`.

---

## R13. Workflow полностью владеет submit/cancel transitions

**Требование:** после включения `Is Submittable` lifecycle не должен одновременно управляться и Workflow, и отдельным ручным Save/Submit сценарием.

**Ответственность:** связать workflow states с системным Doc Status.

**Первый механизм:** Workflow States с `Doc Status` + Workflow Transitions.

Frappe должен получить валидный путь:

```text
Draft-state (0)
→ Approved (1)
→ Cancelled (2)
```

и не получить нелегальные переходы:

```text
Draft → Cancelled
Submitted → Draft
Cancelled → другой state
```

**Почему подходит:** активный Workflow для submittable DocType управляет обычным save/submit/cancel flow; текущая реализация `apply_workflow()` вызывает `save()`, `submit()` или `cancel()` согласно Doc Status следующего состояния.

**Граница:** Workflow state и `docstatus` остаются разными понятиями, хотя один transition может менять оба.

**Проверка:**

```text
final Approve → docstatus 1
Draft сразу Cancel → невозможно
Submitted через допустимый Cancel transition → docstatus 2
Cancelled → дальнейший transition невозможен
```

---

## R14. Ошибка после final approval исправляется через Cancel / Amend

**Требование:** после approval обнаружена ошибка в сумме или назначении, меняющая смысл согласованного факта.

**Ответственность:** исправить зафиксированный Document без бесследного переписывания Submitted записи.

**Первый штатный механизм:** `Cancel` → `Amend`.

**Почему подходит:** это штатный lifecycle submittable Documents.

**Не используется как обычное решение:**

```text
вернуть docstatus 1 → 0
разрешить Edit всех полей
ручной SQL
Allow on Submit для смысловых полей
```

**Граница:** безопасное изменение отдельного несмыслового поля после submit — отдельный `D01`.

**Проверка:**

```text
Approved исходный Document → Cancelled
Amend → новый исправленный Document
исходный зафиксированный факт не переписан задним числом
```

---

# 8. CORE — доставка состояния процесса

## R15. Обязательный Workflow принадлежит App, а не dev-site

**Требование:** новый совместимый Site после установки второго App должен получить тот же обязательный процесс без ручной настройки Workflow.

**Ответственность:** воспроизводимая доставка configuration records.

Source of truth:

```text
Purchase Request schema + status field
→ Standard DocType metadata

Purchase Requester
Purchase Approver
Senior Purchase Approver
→ filtered Role fixtures

Workflow State records CORE
→ filtered fixtures

Workflow
+ child states
+ transitions
+ conditions
→ filtered fixture

тестовые Users
→ Site-local data
```

**Первый механизм:** App `fixtures` + Standard DocType source.

**Почему подходит:** Workflow, Workflow State и Role — database records конфигурации, которые должны синхронизироваться вместе с устанавливаемым App.

**Запрещённый результат:** после clean install приходится вручную:

```text
создавать Workflow
создавать Workflow States
создавать Roles
добавлять workflow_state Custom Field
```

**Граница:** точные fixture filters/order должны быть доказаны исполняемой спецификацией; нельзя экспортировать все системные Workflow/Role records Site.

**Проверка:** `export-fixtures → Git clean`, затем clean-site install восстанавливает только обязательные records второго App.

---

# 9. CORE — автоматические контракты

## R16. Lifecycle проверяется автоматическими Frappe-aware tests

**Требование:** критические правила второго практикума не должны зависеть от ручного прокликивания Workflow.

**Ответственность:** повторяемо доказать собственную конфигурацию процесса и её интеграцию с Document lifecycle.

**Первый механизм:** актуальный Frappe v16 `IntegrationTestCase` + Bench test runner.

Минимальный набор будущих контрактов:

```text
Requester может Draft → Pending Manager
Requester не может Approve
Purchase Approver может допустимый Approve/Reject
маленькая сумма не требует Senior
большая сумма требует Pending Senior
Senior может завершить большой approval
self approval запрещён
Rejected остаётся docstatus 0
final Approved становится docstatus 1
Draft нельзя сразу Cancel
Submitted можно Cancel через допустимый transition
Cancelled становится docstatus 2
Cancelled не может перейти дальше
```

Также проверяется delivery contract:

```text
на clean Site
обязательный Workflow существует
обязательные Workflow State существуют
status является Standard field
скрытого обязательного workflow_state Custom Field нет
```

**Не тестируется ради coverage:**

```text
Frappe вообще умеет Workflow
Frappe вообще умеет submit()
```

**Граница:** тестируются наши state/transition/permission/delivery decisions.

---

# 10. Обязательный финальный acceptance

Матрица не вводит отдельный новый механизм, но фиксирует обязательный финальный критерий всего CORE:

```text
чистый совместимый Frappe Site
+ committed второй учебный App
+ install-app / migrate
+ обязательные Role / Workflow State / Workflow
+ Standard status field без скрытого Custom Field
+ automated tests
+ реальный requester/approver scenario
= воспроизводимый lifecycle
```

Site-local остаются:

```text
test Users
runtime Purchase Requests
пароли
local test config
```

Практикум считается архитектурно незавершённым, если процесс работает только на dev-site, где его настроили вручную.

---

# 11. NEXT — операционные спутники

## N01. После approval работу нужно назначить конкретному сотруднику

**Возможное требование:** конкретный сотрудник должен выполнить закупку.

**Первый кандидат:** `Assignment` / `ToDo`.

Смысл:

```text
кто сейчас должен выполнить работу
→ Assignment
```

**Не создавать автоматически:**

```text
executor → Link → User
```

если нужен только текущий рабочий исполнитель.

Assignment уже создаёт `ToDo` и имеет собственное поведение уведомления; отдельная Notification не добавляется для дублирования назначения.

---

## N02. Нужно отдельное напоминание по дате

**Возможное требование:** например, за два дня до `needed_by` напомнить ответственному по актуальной заявке.

**Первый кандидат:** `Notification` с date-based event.

**Граница:** не дублировать:

```text
Workflow Action
Workflow Send Email Alert
Assignment notification
```

Date-based Notification зависит от scheduler infrastructure Frappe. Поэтому её включение должно быть осознанным расширением эксплуатационной границы, а не скрытым «ещё одним полем» CORE.

---

## N03. Нужны файлы, обсуждение и обычная история изменений

Типовые требования:

```text
коммерческое предложение
→ File / Attach

обсуждение заявки
→ Comment / Timeline

кто менял сумму/описание
→ Track Changes / Version
```

**Не создавать автоматически:**

```text
Purchase Request Attachment
Purchase Request Comment
Approval History
```

Если нужен отдельный юридически значимый журнал, это будет другая ответственность.

---

## N04. Одобренную заявку нужно представить как документ

**Возможное требование:** показать/сохранить Approved Purchase Request в печатном виде/PDF.

**Первый шаг:** Standard Print View.

**Следующий кандидат только при недостаточности:** `Print Format`.

Собственный PDF generator не вводится без другого требования.

---

# 12. GATE — архитектурные развилки

## D00. Что делать с данными при эволюции учебной модели

Внутри практикума модель меняется минимум дважды:

```text
status Select
→ status Link → Workflow State

Approved docstatus 0
→ Approved docstatus 1 после появления Submittable-семантики
```

На dev/test Site к этому моменту уже могут существовать контрольные Purchase Requests.

**Правило:** такие данные не объявляются поддерживаемой предыдущей production-версией только потому, что ученик создал их на предыдущем этапе.

Разрешённый учебный путь должен быть явным:

```text
зафиксировать наблюдение предыдущего этапа
→ удалить/пересоздать disposable control data штатным Document-путём
→ применить новую конфигурацию
→ создать новый контрольный набор
```

Без ручного SQL.

Если бы существовала поддерживаемая предыдущая версия App с реальными пользовательскими данными, изменение semantics/type/state потребовало бы отдельного migration plan и при необходимости patch.

**Цель D00:** не приучать ни к фиктивным patches ради учебника, ни к игнорированию реальной data migration.

---

## D01. Безопасное поле можно изменить после Submit

Новое требование, например:

> После approval можно записать внешний номер заказа, но это не меняет согласованную сумму, назначение и срок.

Первый кандидат: `Allow on Submit` только для конкретного поля.

Не использовать его для смысловых полей согласованного факта.

---

## D02. Заявку можно создавать от имени другого сотрудника

Теперь:

```text
requester ≠ всегда owner
```

Потребуется отдельное предметное поле requester и повторный анализ self-approval semantics.

Нельзя продолжать считать штатную owner-based проверку Workflow полной реализацией новой политики.

---

## D03. Лимит approval должен менять администратор как данные системы

Только здесь фиксированный `LIMIT` перестаёт быть частью учебной конфигурации процесса.

Первый кандидат для одного значения уровня Site — `Single DocType` Settings.

После этого Workflow condition должен читать настоящий источник настройки только если такая зависимость остаётся простой и понятной.

---

## D04. Маршрут согласования стал динамическим

Пример нового требования:

```text
approver зависит от подразделения
+ категории расходов
+ организации
+ бюджета
+ внешнего решения
```

Наличие слова «approval» больше не гарантирует, что один статический Workflow остаётся естественной моделью.

Первый шаг — повторный architectural fit analysis:

```text
можно ли честно выразить процесс
Workflow states/transitions/conditions?
```

Если нет, только тогда появляется отдельная предметная ответственность и рассматривается собственный код/модель.

---

# 13. Явные неправильные решения

## Неправильно: Workflow с первого дня

```text
есть четыре status
→ сразу Workflow
```

Почему плохо: ученик не видит, какая новая ответственность потребовала механизм.

Правильно:

```text
status хранит состояние
↓
появилась политика переходов
↓
Workflow
```

---

## Неправильно: два состояния рядом

```text
status
workflow_state
```

при одинаковом смысле.

Почему плохо: два source of truth и скрытая site-local конфигурация.

Правильно: один Standard state field собственного DocType.

---

## Неправильно: Rejected = Cancelled

Почему плохо: отрицательное draft-решение смешано с отменой ранее Submitted Document.

Правильно:

```text
Rejected  → docstatus 0
Cancelled → docstatus 2
```

---

## Неправильно: Approved = Submitted потому что названия похожи

Правильно: docstatus 1 появляется только после отдельного требования о фиксации согласованного факта.

---

## Неправильно: custom approve() поверх обычного status

если штатный Workflow уже выражает роли и transitions.

---

## Неправильно: Workflow role заменяет DocPerm

```text
роль есть в Transition
→ значит пользователь автоматически имеет все права на Document
```

Это разные уровни ответственности.

---

## Неправильно: Notification дублирует всё подряд

Не нужна отдельная Notification только потому, что:

```text
есть Workflow Action
есть Assignment
```

У каждого механизма уже есть собственная notification semantics.

---

# 14. Контроль матрицы перед dependency graph

Перед построением графа нужно ответить `да`:

```text
1. R01–R16 являются реальными требованиями, а не списком функций?
2. Минимальная модель не повторяет первый практикум ради количества DocTypes?
3. Requester = owner явно является границей CORE, а не универсальным утверждением?
4. Обычный status появляется раньше Workflow?
5. Есть отрицательный опыт, показывающий ограничение обычного status?
6. Workflow появляется только из role-controlled transitions?
7. После Workflow остаётся один source of truth состояния?
8. Обязательный state field принадлежит Standard DocType App?
9. Workflow Action используется раньше собственного Approval Inbox?
10. Pending Senior появляется только вместе с amount-based требованием?
11. Self approval использует штатную owner-based семантику только пока R02 истинно?
12. Rejected остаётся docstatus 0?
13. Approved становится docstatus 1 только после требования о фиксации факта?
14. Cancelled появляется только вместе с submittable lifecycle?
15. Workflow описывает реальный submit/cancel path?
16. Cancel / Amend используется для смыслового исправления Submitted факта?
17. Role / Workflow State / Workflow имеют App-owned delivery path?
18. Не экспортируются все системные Roles/Workflow records Site?
19. Lifecycle защищён автоматическими tests?
20. Финал проверяется на clean Site?
21. Эволюция disposable dev data не выдана за production migration?
22. Реальная production migration не объявлена ненужной вообще?
23. Assignment/Notification/File/Comment/Version/Print остаются NEXT?
24. API/async/extension/integration не попали в CORE ради покрытия?
```

Если какой-то ответ отрицательный, сначала исправляется матрица. Dependency graph и roadmap строятся только после этого.