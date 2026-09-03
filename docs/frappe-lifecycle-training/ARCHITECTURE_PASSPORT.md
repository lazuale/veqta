# Архитектурный паспорт второго учебного практикума Frappe

Статус: **черновик архитектуры после первого аудита**.

Этот практикум является второй отдельной ступенью после принятого [`docs/frappe-training`](../frappe-training/ARCHITECTURE_PASSPORT.md), но не продолжает его предметную область и не зависит от `rental_training`.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md). Если учебное решение конфликтует со стандартом или актуальным Frappe v16, исправляется практикум.

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
Requester:
Draft → Pending Manager

Purchase Approver:
Pending Manager → Approved
Pending Manager → Rejected

Requester:
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

Только теперь появляется состояние:

```text
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

Вопрос:

> Может ли Approver одобрить Document, который сам создал?

Для обязательного сценария:

```text
нет
```

Первым используется штатный `allow_self_approval` перехода Workflow. Собственная проверка `doc.owner == frappe.session.user` не пишется, пока Workflow уже владеет этой ответственностью.

Граница: Frappe сравнивает пользователя с `doc.owner`, поэтому этот механизм правильно соответствует только принятой здесь модели `requester = owner`.

---

# 12. Rejected ≠ Cancelled

`Rejected` здесь означает отрицательное решение на draft-стадии согласования:

```text
Rejected → docstatus 0
```

Это не `docstatus 2`. Заявка может быть исправлена и снова отправлена на согласование, если матрица требований примет такой переход.

`Cancelled` в Frappe относится к ранее Submitted Document. Если бизнес позже потребует терминальный неизменяемый отказ с другой семантикой, это будет отдельное решение, а не автоматическая подмена rejection системным cancel.

---

# 13. Final approval стал фактом → Is Submittable / docstatus

Новое требование:

> После окончательного одобрения сумма, назначение и срок считаются согласованными. Их нельзя незаметно переписать обычным Save.

Теперь `Approved` — не просто workflow label:

```text
до final approval
→ Document рабочий

после final approval
→ Document фиксирует разрешённый факт
```

Первый штатный кандидат — `Is Submittable / docstatus`.

После включения submittable-семантики:

```text
Draft            → docstatus 0
Pending Manager  → docstatus 0
Pending Senior   → docstatus 0
Rejected         → docstatus 0
Approved         → docstatus 1
Cancelled        → docstatus 2
```

`Cancelled` вводится только теперь.

```text
business state = предметный смысл
Workflow       = политика переходов
docstatus      = системный транзакционный lifecycle
```

---

# 14. Workflow должен описать submit/cancel путь

Для submittable DocType активный Workflow заменяет обычный Save/Submit flow.

Значит после появления `Is Submittable` нельзя считать, что Submit/Cancel «останутся сами». Workflow обязан иметь допустимые переходы, которые реально приводят к:

```text
Approved  → docstatus 1
Cancelled → docstatus 2
```

Frappe v16.33.0 не разрешает переходы:

```text
Draft      → Cancelled
Submitted  → Draft
из уже Cancelled state
```

Матрица должна проверить эти границы реальными действиями.

---

# 15. Ошибка после submit → Cancel / Amend

Если после approval обнаружена ошибка, меняющая смысл согласованной заявки, обычный Edit не подходит.

Первый штатный путь:

```text
Cancel
→ Amend
→ новый исправленный Document
```

Практикум должен показать разницу:

```text
изменить Draft
≠
исправить Submitted факт
```

`Allow on Submit` не используется как способ вернуть обычное редактирование.

---

# 16. Allow on Submit — GATE

Он рассматривается только если появляется поле, которое действительно может измениться после approval без изменения смысла согласованной заявки.

Пример отдельного требования:

> После approval нужно записать внешний номер заказа; это не меняет сумму, назначение и решение согласования.

Только тогда проверяется `Allow on Submit`. Без такого требования он вне обязательного маршрута.

---

# 17. Workflow не заменяет DocType Permissions

Безопасность остаётся двухуровневой:

```text
Role + DocType Permissions
→ может ли пользователь вообще работать с Purchase Request

Workflow transition roles / state edit policy
→ какое действие процесса допустимо в текущем state
```

Роль в Workflow transition не является автоматической выдачей всех прав на Document.

Обязательные роли-кандидаты:

```text
Purchase Requester
Purchase Approver
Senior Purchase Approver
```

`Permission Type [v16+]` не включается автоматически для approve: право выполнить переход уже выражает Workflow. Он станет кандидатом только для отдельного действия вне Workflow.

---

# 18. Workflow — App-owned configuration

Обязательный процесс не может существовать только потому, что его один раз настроили на dev-site.

Source of truth:

```text
Purchase Request schema + status field
→ Standard DocType metadata

обязательные Roles
→ fixtures

нужные Workflow State records
→ fixtures

Workflow + child states/transitions/conditions
→ fixtures

test Users
→ Site-local data
```

Точные fixture filters и порядок экспорта фиксируются после принятия матрицы.

Критический отрицательный критерий:

```text
после clean install
не требуется вручную создавать Workflow
не требуется вручную добавлять Workflow States
не появляется случайный обязательный site-local workflow_state Custom Field
```

---

# 19. Автоматические контракты обязательны

Второй практикум не заканчивается «покликали Workflow — работает».

Минимальный класс контрактов:

```text
Requester может Draft → Pending Manager
Requester не может Approve
Purchase Approver может выполнить допустимый approval
маленькая сумма не требует Senior
большая сумма идёт в Pending Senior
self approval блокируется
Rejected остаётся docstatus 0
final Approved становится docstatus 1
Draft нельзя сразу Cancel
Submitted можно Cancel только допустимым transition
Cancelled становится docstatus 2
```

Точная test matrix появится позже. Тестируется собственный процесс приложения, а не внутренности Frappe ради coverage.

---

# 20. Clean Site acceptance — финальный gate lifecycle CORE

Финал должен доказать:

```text
чистый совместимый Frappe Site
+ второй App из committed source
+ install-app / migrate
+ mandatory Workflow configuration
+ tests
= воспроизводимый lifecycle
```

На новом Site нельзя вручную создавать обязательный Workflow, Roles, Workflow States или state Custom Field.

Test Users и runtime Purchase Requests остаются Site-local.

---

# 21. Что после аудита исключено из обязательного lifecycle CORE

Первоначальный паспорт продолжал обязательную цепочку через:

```text
Assignment
Notification
File / Comment / Version
Print
```

Это признано слишком широкой границей.

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

Операционные спутники остаются ветками `NEXT`. Их присутствие в паспорте не означает, что они обязаны попасть в матрицу второго практикума.

---

# 22. NEXT-A — Assignment / ToDo

Возможное требование:

> После approval конкретный сотрудник должен выполнить закупку.

Первый механизм:

```text
Assignment / ToDo
```

```text
кто сейчас должен сделать работу
→ Assignment
```

Если нужен только текущий рабочий исполнитель, поле `executor → User` не создаётся автоматически. Если исполнитель должен стать неизменяемым бизнес-фактом, это уже другая ответственность.

Assignment сам создаёт `ToDo` и штатно уведомляет пользователя о назначении/снятии назначения. Отдельная Notification для дублирования этого события не нужна.

---

# 23. NEXT-B — Notification

Notification не должна дублировать:

```text
Workflow Action
Workflow Send Email Alert
Assignment notification
```

Пример отдельного смысла:

> За два дня до `needed_by` по всё ещё актуальной заявке напомнить ответственному.

Первый кандидат — date-based `Notification`.

Но у этой возможности есть скрытая эксплуатационная зависимость: time/date-based Notifications запускаются scheduler infrastructure Frappe. Поэтому она не должна незаметно попадать в lifecycle CORE, который пока не изучает scheduler/background jobs как отдельную архитектурную тему.

---

# 24. NEXT-C — File / Comment / Version

Типовые требования:

```text
приложить коммерческое предложение
→ File / Attach

обсудить заявку
→ Comment / Timeline

увидеть обычную историю изменений
→ Track Changes / Version
```

Не создаются автоматически `Purchase Request Attachment`, `Purchase Request Comment` или `Approval History`.

Если нужен отдельный юридически значимый журнал с другой семантикой, модель пересматривается отдельно.

---

# 25. NEXT-D — Print

Возможное требование:

> Одобренную заявку нужно представить как печатный документ/PDF.

Первый шаг — штатный Print View. Если его недостаточно, кандидат — `Print Format`.

Собственный PDF generator или frontend не вводится без другой ответственности. Печатный контур может потребовать дополнительные зависимости среды; они появляются только после принятия ветки.

---

# 26. Вне второго lifecycle CORE

Не входят автоматически:

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

NEXT-A/B/C/D также не становятся обязательными только потому, что перечислены здесь.

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
Condition + Pending Senior
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

# 28. Первичные источники

**[ДОКУМЕНТАЦИЯ FRAPPE]** `docstatus`:

- https://docs.frappe.io/framework/doctypes/docstatus

**[ОФИЦИАЛЬНАЯ ДОКУМЕНТАЦИЯ ЭКОСИСТЕМЫ]** Workflow / Workflow Actions:

- https://docs.frappe.io/erpnext/workflows
- https://docs.frappe.io/erpnext/workflow-actions

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Workflow создаёт state Custom Field только если указанного поля нет в Meta:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** transitions, conditions, `apply_workflow()` и self approval:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py

`has_approval_access()` сравнивает пользователя с `doc.owner`; `apply_workflow()` вызывает `save()`, `submit()` или `cancel()` в зависимости от Doc Status следующего state.

**[ДОКУМЕНТАЦИЯ FRAPPE]** fixtures:

- https://docs.frappe.io/framework/user/en/python-api/hooks

**[ДОКУМЕНТАЦИЯ FRAPPE]** Assignment / ToDo:

- https://docs.frappe.io/framework/assignments-and-todos

**[ДОКУМЕНТАЦИЯ FRAPPE]** Notification:

- https://docs.frappe.io/framework/notifications

**[ИСХОДНЫЙ КОД FRAPPE]** scheduler вызывает ежедневные/offset Notification checks:

- https://github.com/frappe/frappe/blob/version-16/frappe/hooks.py

**[ДОКУМЕНТАЦИЯ FRAPPE]** Printing:

- https://docs.frappe.io/framework/user/en/desk/printing

**[ДОКУМЕНТАЦИЯ FRAPPE]** `Allow on Submit`:

- https://docs.frappe.io/framework/doctypes/allow-on-submit

**[ВНУТРЕННИЙ СТАНДАРТ]**:

- [`03_DOCUMENT_LIFECYCLE.md`](../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md)
- [`04_SECURITY.md`](../frappe-architecture-standard/04_SECURITY.md)
- [`05_TRANSACTIONS_ASYNC.md`](../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md)
- [`08_UI_REPORTING.md`](../frappe-architecture-standard/08_UI_REPORTING.md)
- [`09_DEPLOYMENT_TESTING.md`](../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md)
- [`10_DECISION_STANDARD.md`](../frappe-architecture-standard/10_DECISION_STANDARD.md)

---

# 29. Gate перед матрицей требований

На все вопросы нужен ответ `да`:

```text
1. Purchase Request создаёт реальную lifecycle-задачу?
2. Requester в CORE явно равен Document.owner?
3. Обычный status появляется раньше Workflow?
4. Pending Senior не существует до второго approval level?
5. Cancelled не существует до docstatus?
6. После Workflow остаётся один source of truth состояния?
7. Mandatory state field принадлежит Standard DocType, а не случайному Custom Field?
8. Workflow появляется только после role-controlled transitions?
9. Condition появляется из amount-based approval?
10. Self approval соответствует принятой owner-семантике?
11. Rejected не перепутан с Cancelled?
12. Approved получает docstatus 1 только после требования о фиксации разрешения?
13. Workflow полностью описывает submit/cancel path после Is Submittable?
14. Cancel / Amend используется для изменения смысла Submitted факта?
15. Allow on Submit остаётся GATE?
16. DocType Permissions и Workflow roles не смешаны?
17. Workflow/Role configuration имеет App-owned delivery path?
18. Lifecycle contracts проверяются автоматически?
19. Финал проверяется на чистом Site?
20. Assignment/Notification/File/Comment/Version/Print не перегружают обязательный CORE?
21. Notification не дублирует Workflow/Assignment и не скрывает scheduler dependency?
22. API/async/extension/integration не попали в CORE ради покрытия?
23. Первый и второй практикумы учат разным архитектурным классам задач?
```

Если хотя бы один ответ отрицательный, сначала исправляется паспорт. Матрица, граф и roadmap до этого не создаются.
