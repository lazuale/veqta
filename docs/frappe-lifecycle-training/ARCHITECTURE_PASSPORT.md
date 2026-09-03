# Архитектурный паспорт второго учебного практикума Frappe

Статус: **черновик архитектуры после первого аудита**.

Этот практикум является второй отдельной ступенью после принятого [`docs/frappe-training`](../frappe-training/ARCHITECTURE_PASSPORT.md), но не продолжает его предметную область и не зависит от `rental_training`.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md). Если учебное решение конфликтует со стандартом или актуальным Frappe v16, исправляется практикум.

Следующий формализованный слой — [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md). Граф зависимостей и roadmap до принятия матрицы не создаются.

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
рабочее бизнес-состояние
        ↓
ограничения переходов по ролям
        ↓
Workflow
        ↓
условные уровни согласования
        ↓
self-approval policy
        ↓
момент фиксации факта
        ↓
Is Submittable / docstatus
        ↓
Cancel / Amend
        ↓
автоматические контракты
        ↓
чистая воспроизводимая установка
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

Второй практикум создаёт отдельный учебный App и отдельную предметную модель. Создание App, Site и Git остаётся технической предпосылкой, а не новой учебной темой.

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

`submit` здесь фиксирует факт организационного разрешения потратить согласованную сумму на согласованную цель. Это и создаёт реальную причину изучать `docstatus`, а не использовать Submitted как декоративный финальный статус.

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

Второй практикум изучает lifecycle и процесс. Новые сущности не создаются ради большей «реалистичности», пока без них можно честно выразить учебные требования.

---

# 5. Requester = Document.owner

В обязательном сценарии requester — пользователь, который создал Document:

```text
requester = Document.owner
```

Отдельного поля `requester → User` в lifecycle CORE нет.

Это не универсальная модель закупок. Это граница учебного сценария, важная для self approval: штатная реализация Workflow Frappe сравнивает пользователя именно с `doc.owner`.

Если позже появится требование создавать заявку от имени другого сотрудника, `owner` перестанет полностью выражать requester и self-approval policy придётся пересмотреть.

---

# 6. Сначала — обычное бизнес-состояние

Первое требование:

> Пользователь должен понимать, где находится заявка.

Для этого сначала достаточно обычного предметного поля состояния.

Начальный набор:

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

`Pending Senior` появится только после требования о втором уровне согласования. `Cancelled` — только после появления транзакционной семантики `docstatus = 2`.

Наличие нескольких значений само по себе не доказывает необходимость Workflow:

```text
нужно только хранить состояние?
→ обычное поле

нужно ограничить переходы по ролям/условиям?
→ кандидат Workflow
```

---

# 7. Один source of truth состояния

Это обязательное архитектурное решение второго практикума.

Нельзя получить два поля:

```text
status
+
workflow_state
```

если оба выражают один и тот же процесс.

Frappe v16.33.0 при сохранении Workflow проверяет поле, указанное как `workflow_state_field`. Если такого поля нет в Meta целевого DocType, Framework автоматически создаёт на Site `Custom Field` типа `Link → Workflow State`.

Для Site-customized или чужого DocType это штатно допустимо. Для нашего собственного Standard `Purchase Request` обязательное поле состояния должно принадлежать App.

Baseline практикума:

```text
до Workflow
status = Standard Select

после появления Workflow
тот же fieldname status
→ остаётся единственным state field
→ Standard field меняется на Link → Workflow State
→ Workflow State Field = status
```

Это **архитектурный вывод практикума**, а не универсальное требование Frappe. Его цель — сохранить один source of truth и не получить скрытый обязательный `Custom Field` на dev-site.

Workflow State records создаются до смены типа поля, а используемые значения `status` должны иметь соответствующие записи Workflow State. Если бы это была поддерживаемая production-версия с реальными данными, изменение поля потребовало бы отдельного migration analysis; dev/test данные практикума за такую production migration не выдаются.

---

# 8. Появилась политика переходов → Workflow

Следующее требование:

```text
Purchase Requester:
Draft → Pending Manager

Purchase Approver:
Pending Manager → Approved
Pending Manager → Rejected

Purchase Requester:
не может Pending Manager → Approved
```

Появились состояния, переходы, роли и правила допустимого действия. Первый штатный кандидат — `Workflow`.

Не создаются собственные:

```text
approve() только ради обхода Workflow
if "Purchase Approver" in frappe.get_roles() в разных местах
JS-кнопки как единственная защита
Approval Log как движок процесса
```

Workflow становится владельцем политики переходов.

---

# 9. Workflow Action — часть штатного Workflow

После включения Workflow пользователь должен увидеть не только действие на Form, но и штатную модель ожидающих действий через `Workflow Action`.

Отдельный собственный `Approval Inbox` не создаётся.

Email для Workflow Actions не является обязательной предпосылкой lifecycle CORE: он зависит от настройки исходящей почты и `Send Email Alert`. Сам Workflow должен быть проверяем без отдельной email-инфраструктуры.

---

# 10. Появилось условное согласование → Condition

Новое требование:

```text
requested_amount <= лимит
→ достаточно Purchase Approver

requested_amount > лимит
→ после Purchase Approver нужен Senior Purchase Approver
```

Только теперь появляются:

```text
Senior Purchase Approver
Pending Senior
```

и реальная причина использовать `Condition` перехода Workflow.

```text
Draft
  ↓ Requester
Pending Manager
  ↓ Purchase Approver + небольшая сумма
Approved

Pending Manager
  ↓ Purchase Approver + большая сумма
Pending Senior
  ↓ Senior Purchase Approver
Approved
```

Лимит пока является частью зафиксированного учебного сценария. `Single DocType` настроек не создаётся ради демонстрации. Если администратор должен менять лимит как данные системы, это станет отдельным требованием.

---

# 11. Self approval — отдельная политика

Следующий вопрос процесса:

> Может ли пользователь с ролью Approver одобрить Document, который сам создал?

В обязательном сценарии:

```text
нет
```

Первым используется штатный `allow_self_approval` перехода Workflow.

Собственная проверка `doc.owner == frappe.session.user` не пишется, пока стандартный Workflow уже выражает эту ответственность.

Граница уже задана разделом 5: штатная проверка сравнивает пользователя с `doc.owner`. Если requester позднее перестанет совпадать с owner, это будет новая архитектурная задача.

---

# 12. Rejected не равен Cancelled

В этом практикуме `Rejected` означает отрицательное решение на draft-стадии согласования.

Поэтому:

```text
Rejected → docstatus 0
```

`Rejected` не означает `docstatus 2`, потому что Frappe `Cancelled` — состояние ранее Submitted Document.

Если процесс допускает исправление Rejected и повторную отправку, это должно быть явным Workflow transition.

---

# 13. Final approval становится зафиксированным фактом

Новое требование:

> После окончательного одобрения сумма, назначение и срок заявки считаются согласованными. Их нельзя незаметно переписать обычным Save.

Теперь `Approved` — не просто workflow state.

Появляется транзакционная семантика:

```text
до final approval
→ Document рабочий и изменяемый

после final approval
→ Document фиксирует разрешённый факт
```

Первый штатный кандидат — `Is Submittable` / `docstatus`.

После этого mapping:

```text
Draft            → docstatus 0
Pending Manager  → docstatus 0
Pending Senior   → docstatus 0
Rejected         → docstatus 0
Approved         → docstatus 1
Cancelled        → docstatus 2
```

`Cancelled` вводится только здесь.

`Approved` получает `docstatus 1` не из-за названия, а из-за отдельного требования зафиксировать разрешение как факт.

---

# 14. Workflow должен полностью описывать submit/cancel path

После появления `Is Submittable` активный Workflow управляет переходами, связанными с `save()`, `submit()` и `cancel()`.

Workflow должен содержать допустимые переходы к:

```text
Approved  → docstatus 1
Cancelled → docstatus 2
```

и не должен моделировать нелегальные для Frappe переходы:

```text
Draft → Cancelled
Submitted → Draft
Cancelled → другой state
```

Будущая матрица и tests должны доказать эти границы действиями, а не только конфигурацией строк Workflow.

---

# 15. Cancel / Amend вместо бесследного переписывания

Если после final approval обнаружена смысловая ошибка в сумме или назначении, первый штатный путь:

```text
Cancel
→ Amend
→ новый исправленный Document
```

Практикум должен показать разницу между обычным изменением Draft и исправлением уже зафиксированного Submitted факта.

`Allow on Submit` не используется как способ вернуть Submitted Document в обычное редактирование.

---

# 16. Allow on Submit — GATE

Механизм появляется только под отдельное безопасное требование.

Пример:

> После approval можно записать внешний номер заказа, не меняя согласованную сумму, назначение и срок.

Только тогда конкретное поле может рассматриваться как `Allow on Submit`.

---

# 17. DocType Permissions и Workflow roles — разные уровни

Базовая безопасность:

```text
Role + DocType Permissions
→ может ли пользователь вообще работать с Purchase Request

Workflow transition roles
→ какое процессное действие доступно в текущем state
```

Обязательные роли появляются по мере требований:

```text
R05:
Purchase Requester
Purchase Approver

R09:
Senior Purchase Approver
```

`Permission Type [v16+]` не нужен автоматически для Approve: разрешение transition уже принадлежит Workflow.

---

# 18. Workflow должен быть App-owned

Обязательный процесс не может существовать только потому, что его один раз настроили на dev-site.

Source of truth:

```text
Purchase Request schema + status field
→ Standard DocType metadata

обязательные Roles
→ filtered fixtures

Workflow State records
→ filtered fixtures

Workflow + states + transitions + conditions
→ filtered fixture

test Users
→ Site-local data
```

После clean install не должно требоваться вручную создавать Workflow, Workflow States, Roles или скрытый `workflow_state` Custom Field.

Точные fixture filters и порядок экспорта фиксируются будущей исполняемой спецификацией.

---

# 19. Автоматические контракты обязательны

Второй практикум не заканчивается «покликали Workflow — работает».

Минимальный класс контрактов:

```text
Requester может отправить Draft
Requester не может Approve
Purchase Approver может допустимый Approve/Reject
маленькая сумма не требует Senior
большая сумма требует Senior
self approval запрещён
Rejected остаётся docstatus 0
final Approved становится docstatus 1
Draft нельзя сразу Cancel
Submitted можно Cancel через допустимый Workflow transition
Cancelled становится docstatus 2
Cancelled не переходит дальше
```

Проверяется и delivery contract обязательного Workflow на clean Site.

---

# 20. Clean Site acceptance — финальный gate

Финал должен доказать:

```text
чистый совместимый Frappe Site
+ второй App из committed source
+ install-app / migrate
+ mandatory Workflow configuration
+ tests
+ реальный requester/approver scenario
= воспроизводимый lifecycle
```

На новом Site нельзя вручную создавать обязательные Workflow/State/Role/state-field.

Site-local test Users и runtime Purchase Requests создаются после установки App.

---

# 21. Что после аудита НЕ входит в обязательный lifecycle CORE

Первоначальная идея включала в одну обязательную цепочку:

```text
Assignment
Notification
File / Comment / Version
Print
```

После аудита это признано слишком широкой границей.

Обязательный маршрут заканчивается на:

```text
Workflow
→ conditions
→ self approval
→ docstatus
→ Cancel / Amend
→ tests
→ clean delivery
```

Операционные спутники остаются `NEXT`.

---

# 22. NEXT-A — Assignment / ToDo

Возможное требование:

> После approval конкретный сотрудник должен выполнить закупку.

Первый механизм: `Assignment / ToDo`.

Если нужен только текущий рабочий исполнитель, не создаётся автоматически `executor → Link → User`.

Assignment имеет собственное уведомление о назначении/снятии назначения; отдельная Notification для дублирования этого события не нужна.

---

# 23. NEXT-B — Notification

Notification не дублирует:

```text
Workflow Action
Workflow Send Email Alert
Assignment notification
```

Для неё нужен отдельный смысл, например напоминание относительно `needed_by`.

Date-based Notification использует scheduler infrastructure Frappe, поэтому эта зависимость не должна незаметно попадать в lifecycle CORE.

---

# 24. NEXT-C — File / Comment / Version

```text
приложить коммерческое предложение
→ File / Attach

обсудить заявку
→ Comment / Timeline

увидеть обычную историю изменений
→ Track Changes / Version
```

Не создаются автоматически `Purchase Request Attachment`, `Purchase Request Comment`, `Approval History`.

---

# 25. NEXT-D — Print

Если Approved Purchase Request нужно представить как печатный документ/PDF, сначала проверяется штатный Print View.

Только если его недостаточно — `Print Format`.

---

# 26. За пределами обязательного маршрута

```text
REST API
custom whitelisted API
Webhook
background jobs
custom scheduler code
foreign DocType customization
doc_events
extend_doctype_class
override_doctype_class
Web Form / Portal
custom frontend
Query Report / Script Report
complex User Permission model
Permission Type без отдельной команды
concurrency / locking
external integration
production deployment
```

---

# 27. Архитектурная карта после аудита

Обязательный lifecycle CORE:

```text
Purchase Request
        ↓
обычный status
        ↓
role-controlled transitions
        ↓
единый state field + Workflow
        ↓
amount-based branching
        ↓
Senior role + Pending Senior + Conditions
        ↓
self approval policy
        ↓
final approval = фиксированный факт
        ↓
Is Submittable / docstatus
        ↓
Cancelled = docstatus 2
        ↓
Cancel / Amend
        ↓
automated contracts
        ↓
clean Site acceptance
```

Необязательный операционный контур:

```text
Assignment / ToDo
Notification
File / Comment / Version
Print
```

---

# 28. Источники

**[ДОКУМЕНТАЦИЯ FRAPPE]** `docstatus`:

- https://docs.frappe.io/framework/doctypes/docstatus

**[ОФИЦИАЛЬНАЯ ДОКУМЕНТАЦИЯ ЭКОСИСТЕМЫ]** Workflow:

- https://docs.frappe.io/erpnext/workflows
- https://docs.frappe.io/erpnext/workflow-actions

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** автоматическое создание Workflow state Custom Field:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** transitions, conditions, `apply_workflow()` и self approval:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py

**[ДОКУМЕНТАЦИЯ FRAPPE]** fixtures:

- https://docs.frappe.io/framework/user/en/python-api/hooks

**[ВНУТРЕННИЙ АРХИТЕКТУРНЫЙ СТАНДАРТ]**:

- [`03_DOCUMENT_LIFECYCLE.md`](../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md)
- [`04_SECURITY.md`](../frappe-architecture-standard/04_SECURITY.md)
- [`05_TRANSACTIONS_ASYNC.md`](../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md)
- [`09_DEPLOYMENT_TESTING.md`](../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md)
- [`10_DECISION_STANDARD.md`](../frappe-architecture-standard/10_DECISION_STANDARD.md)

---

# 29. Критерий принятия паспорта

Перед dependency graph матрица должна подтвердить все ключевые решения паспорта. Если матрица выявляет противоречие, сначала исправляется паспорт/матрица, а не строится удобная последовательность уроков.