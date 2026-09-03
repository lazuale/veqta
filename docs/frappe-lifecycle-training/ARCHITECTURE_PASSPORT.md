# Архитектурный паспорт второго учебного практикума Frappe

Статус: **черновик архитектуры после первого аудита**.

Этот практикум является второй отдельной ступенью после принятого [`docs/frappe-training`](../frappe-training/ARCHITECTURE_PASSPORT.md), но не продолжает его предметную область и не зависит от `rental_training`.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md). Если учебное решение конфликтует со стандартом или актуальным Frappe v16, исправляется практикум.

---

# 1. Назначение второго практикума

Первый практикум отвечает на вопрос:

> **Как правильно построить собственную модель Frappe App?**

Второй отвечает на другой вопрос:

> **Как обычный Document превращается в управляемый бизнес-процесс и зафиксированный транзакционный факт, не изобретая собственный workflow engine?**

Обязательная учебная ось второго практикума:

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
воспроизводимая установка на чистый Site
```

Практикум не строится как каталог:

```text
Workflow → Assignment → Notification → Print → ...
```

Каждый механизм появляется только после требования, которое создаёт новую ответственность.

---

# 2. Что ученик уже должен понимать

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

Эти знания являются входом из первого CORE-практикума.

Второй практикум создаёт отдельный учебный App и отдельную предметную модель, чтобы lifecycle-решения не зависели от Rental.

Создание App, Site и Git остаётся технической предпосылкой, а не новой учебной темой.

---

# 3. Нейтральная предметная область

Предметная задача — **внутренняя заявка на закупку**.

Сотруднику нужно приобрести товар или услугу для работы. Он создаёт заявку. Заявку рассматривают уполномоченные сотрудники. После окончательного одобрения заявка становится **зафиксированным разрешением на закупку**.

Важно:

```text
Approved Purchase Request
≠
сама покупка
≠
платёж
≠
складская операция
```

`submit` в этом практикуме фиксирует именно факт организационного разрешения потратить согласованную сумму на согласованную цель.

Это и создаёт реальную причину изучать `docstatus`, а не использовать Submitted как декоративный финальный статус.

---

# 4. Минимальная предметная модель

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

Причина: второй практикум изучает lifecycle и процесс. Новые сущности не создаются ради большей «реалистичности», пока без них можно честно выразить учебные требования.

Если позднее появится реальное требование к строкам закупки, поставщику, бюджету или другому самостоятельному объекту, модель пересматривается обычным способом из первого практикума.

---

# 5. Кто является requester

В обязательном сценарии requester — пользователь, который создал Document.

То есть:

```text
requester
=
Document.owner
```

Отдельного поля `requester → User` в CORE второго практикума нет.

Это не универсальная модель закупок. Это важная граница учебного сценария.

Причина особенно существенна для self approval: штатная реализация Workflow Frappe проверяет собственную заявку именно через `doc.owner`.

Если появится требование:

> сотрудник может создавать заявку от имени другого сотрудника,

то `owner` перестанет полностью выражать requester и модель self-approval придётся пересмотреть отдельно.

---

# 6. Первый шаг — обычное бизнес-состояние

Первое требование:

> Пользователь должен понимать, где находится заявка.

Для этого сначала достаточно обычного предметного поля состояния.

Начальный набор смыслов:

```text
Draft
Pending Manager
Approved
Rejected
```

На этом этапе **нет**:

```text
Pending Senior
Cancelled
Workflow
Is Submittable
```

Это принципиально.

`Pending Senior` появится только после требования о втором уровне согласования.

`Cancelled` появится только после появления транзакционной семантики `docstatus = 2`.

Наличие четырёх значений само по себе не доказывает необходимость Workflow.

Архитектурная проверка:

```text
нужно только хранить состояние?
→ обычное поле

нужно ограничить допустимые переходы по ролям и условиям?
→ появляется кандидат Workflow
```

---

# 7. Единственный source of truth состояния

Это обязательное архитектурное решение второго практикума.

Нельзя получить:

```text
status
+
workflow_state
```

если оба поля выражают один и тот же смысл процесса.

В Frappe v16.33.0 при сохранении Workflow Framework проверяет поле, указанное как `workflow_state_field`. Если такого поля нет в Meta целевого DocType, Frappe автоматически создаёт **Custom Field** типа `Link → Workflow State` на Site.

Для чужого или Site-customized DocType это может быть нормальным штатным поведением.

Для нашего собственного Standard `Purchase Request` обязательное состояние должно принадлежать App, а не возникать скрытым ручным Custom Field на dev-site.

Поэтому baseline второго практикума:

```text
до Workflow
status = обычный Standard DocField

после появления Workflow
тот же fieldname status
→ остаётся единственным source of truth состояния
→ становится Standard Link → Workflow State
→ Workflow State Field = status
```

То есть мы **эволюционируем существующее поле**, а не создаём второе состояние рядом.

Workflow State records должны существовать до того, как существующие значения `status` начинают интерпретироваться как Links. В учебном сценарии названия состояний сохраняются совместимыми.

Если бы это была поддерживаемая предыдущая production-версия с реальными данными, изменение типа поля и существующих значений потребовало бы отдельного migration analysis. Второй практикум не выдаёт dev/test записи за такую production migration.

---

# 8. Вторая граница — политика переходов

Следующее требование:

```text
Requester
может:
Draft → Pending Manager

Purchase Approver
может:
Pending Manager → Approved
Pending Manager → Rejected

Requester
не может:
Pending Manager → Approved
```

Появились одновременно:

```text
состояния
+
переходы
+
роли
+
правила допустимого действия
```

Первый штатный кандидат — `Workflow`.

Не создаются собственные:

```text
approve() только ради обхода Workflow
if "Purchase Approver" in frappe.get_roles() в разных местах
JS-кнопки как единственная защита перехода
Approval Log как движок процесса
```

Workflow становится владельцем политики переходов.

---

# 9. Workflow Action — часть штатного Workflow, не отдельная подсистема

После включения Workflow пользователь должен увидеть не только кнопку на Form, но и штатную модель ожидающих действий через `Workflow Action`.

Это часть доказательства, что мы используем реальную подсистему Workflow Frappe, а не только меняем поле состояния.

Отдельный собственный `Approval Inbox` не создаётся.

Email для Workflow Actions не является обязательной предпосылкой CORE: он зависит от настройки исходящей почты и включённого `Send Email Alert`. Сам Workflow проверяется без требования поднимать отдельную email-инфраструктуру.

---

# 10. Третья граница — условный уровень согласования

Следующее требование:

```text
requested_amount <= лимит
→ достаточно Purchase Approver

requested_amount > лимит
→ после Purchase Approver нужен Senior Purchase Approver
```

Только теперь появляется новое состояние:

```text
Pending Senior
```

и первая реальная причина использовать `Condition` перехода Workflow.

Смысловая схема:

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

Лимит на этом этапе остаётся частью зафиксированного учебного сценария.

Отдельный Settings DocType не создаётся ради демонстрации `Single DocType`.

Если появится самостоятельное требование:

> администратор должен менять лимит без изменения Workflow,

тогда настройки рассматриваются отдельно.

---

# 11. Self approval — отдельная политика

Следующий вопрос процесса:

> Может ли пользователь, имеющий роль Approver, одобрить Document, который сам создал?

В обязательном сценарии ответ:

```text
нет
```

Первым используется штатный `allow_self_approval` перехода Workflow.

Собственная проверка:

```python
if doc.owner == frappe.session.user:
    ...
```

не пишется, пока стандартный Workflow уже выражает эту ответственность.

Граница уже зафиксирована разделом 5:

```text
self approval Frappe
сравнивает пользователя с doc.owner
```

Если business requester позднее перестанет совпадать с owner, это будет новая архитектурная задача.

---

# 12. Rejected не равен Cancelled

В этом практикуме `Rejected` означает отрицательное решение на draft-стадии согласования.

Поэтому:

```text
Rejected
→ docstatus 0
```

и заявка может быть исправлена и снова отправлена на рассмотрение, если будущая матрица выберет такой переход.

`Rejected` не означает:

```text
docstatus 2
```

Потому что Frappe `Cancelled` — состояние ранее **Submitted** Document.

Если бизнес позже потребует терминальный неизменяемый отказ с другой юридической семантикой, это будет отдельное требование, а не причина автоматически подменить rejection системным cancel.

---

# 13. Четвёртая граница — окончательное одобрение как зафиксированный факт

Следующее требование меняет архитектуру сильнее:

> После окончательного одобрения сумма, назначение и срок заявки считаются согласованными. Их нельзя незаметно переписать обычным Save.

Теперь `Approved` — не просто значение workflow state.

Появилась транзакционная семантика:

```text
до final approval
→ Document рабочий и изменяемый

после final approval
→ Document фиксирует разрешённый факт
```

Первый штатный кандидат — `Is Submittable` / `docstatus`.

После включения submittable-семантики mapping становится:

```text
Draft            → docstatus 0
Pending Manager  → docstatus 0
Pending Senior   → docstatus 0
Rejected         → docstatus 0
Approved         → docstatus 1
Cancelled        → docstatus 2
```

`Cancelled` вводится **только на этом этапе**.

`Workflow` и `docstatus` используются вместе, но отвечают на разные вопросы:

```text
business state
= предметный смысл состояния

Workflow
= кто и при каких условиях может выполнить переход

docstatus
= системный транзакционный lifecycle
```

---

# 14. Workflow должен полностью описать submit/cancel путь

Для submittable DocType активный Workflow заменяет обычный Save/Submit flow.

Поэтому после появления `Is Submittable` нельзя считать, что кнопки Submit/Cancel «как-нибудь останутся сами».

Workflow обязан содержать допустимые переходы, которые реально приводят к:

```text
Approved  → docstatus 1
Cancelled → docstatus 2
```

Frappe не разрешает:

```text
Draft      → Cancelled
Submitted  → Draft
переход из уже Cancelled state
```

Будущая матрица должна проверить эти границы реальными действиями, а не только конфигурацией таблицы Workflow.

---

# 15. Cancel / Amend вместо бесследного переписывания

После `Submitted` появляется требование:

> Что делать, если после approval обнаружена ошибка в сумме или назначении?

Если изменение меняет смысл согласованного факта, обычный Edit не подходит.

Первый штатный путь:

```text
Cancel
→ Amend
→ новый исправленный Document
```

Практикум должен показать разницу между:

```text
изменить Draft
```

и:

```text
исправить уже зафиксированный Submitted факт
```

`Allow on Submit` не используется как способ вернуть Submitted Document в режим обычного редактирования.

---

# 16. Allow on Submit — GATE, а не обязательный механизм

Он рассматривается только если появляется поле, которое действительно может измениться после approval без изменения смысла согласованной заявки.

Пример отдельного требования:

> После approval исполнитель записывает внешний номер заказа; это не меняет сумму, назначение и решение согласования.

Только тогда можно проверить `Allow on Submit`.

Без такого требования механизм остаётся вне обязательного маршрута.

---

# 17. Безопасность Workflow не заменяет DocType Permissions

Базовая безопасность остаётся двухуровневой:

```text
Role + DocType Permissions
→ может ли пользователь вообще работать с Purchase Request

Workflow transition roles / state edit policy
→ какое действие процесса доступно в текущем state
```

Наличие роли в Workflow transition не должно восприниматься как автоматическая выдача всех прав на Document.

Предполагаемые обязательные роли:

```text
Purchase Requester
Purchase Approver
Senior Purchase Approver
```

`Permission Type [v16+]` не включается автоматически для approve: само право выполнить переход уже принадлежит Workflow.

Он станет кандидатом только для отдельного нестандартного действия вне Workflow.

---

# 18. Воспроизводимость Workflow — часть архитектуры App

Обязательный процесс не может существовать только потому, что его один раз настроили на dev-site.

Для собственного App source of truth разделяется так:

```text
Purchase Request schema
включая status field
→ Standard DocType metadata

обязательные Roles
→ App configuration / fixtures

Workflow State records, которых требует процесс
→ App configuration / fixtures

Workflow + transitions + conditions
→ App configuration / fixtures

test Users
→ Site-local data
```

Точные fixture filters и порядок экспорта фиксируются будущей спецификацией после принятия матрицы.

Критический отрицательный тест:

```text
после clean install
не должно требоваться вручную создавать Workflow
или появившийся случайно site-local Custom Field workflow_state
```

---

# 19. Автоматические контракты обязательны и во втором практикуме

Второй практикум не должен завершаться фразой «покликали Workflow — работает».

Минимальный класс контрактов:

```text
Requester может отправить Draft на согласование
Requester не может выполнить Approve
Purchase Approver может одобрить допустимый переход
большая сумма идёт в Pending Senior
маленькая сумма не требует Senior
self approval блокируется
Rejected остаётся docstatus 0
final Approved становится docstatus 1
Draft нельзя сразу Cancel
Submitted можно Cancel только через допустимый Workflow transition
Cancelled становится docstatus 2
```

Точная test matrix появится позже.

Тестируется собственная конфигурация процесса и её интеграция с Frappe lifecycle, а не внутренности Framework ради coverage.

---

# 20. Clean Site acceptance остаётся финальным gate

Финал второго практикума должен доказать:

```text
чистый совместимый Frappe Site
+ второй учебный App из committed source
+ install-app / migrate
+ mandatory Workflow configuration
+ tests
= воспроизводимый lifecycle
```

На новом Site нельзя вручную:

```text
создавать Workflow
добавлять обязательные Workflow States
донастраивать Roles
создавать workflow_state Custom Field
```

Site-local test Users и runtime Purchase Requests создаются уже после установки App.

---

# 21. Что после аудита НЕ входит в обязательный lifecycle CORE

Первоначальный паспорт пытался продолжить обязательную цепочку через:

```text
Assignment
Notification
File / Comment / Version
Print
```

После аудита это признано слишком широкой границей.

Эти механизмы полезны, но отвечают уже не на главный вопрос lifecycle CORE.

Поэтому обязательный маршрут заканчивается на:

```text
Workflow
→ conditions
→ self approval
→ docstatus
→ Cancel / Amend
→ tests
→ clean delivery
```

Операционные спутники остаются естественными ветками `NEXT` и будут включены только если будущая матрица докажет необходимость именно во втором практикуме.

---

# 22. NEXT-A — Assignment / ToDo

Возможное следующее требование:

> После approval конкретный сотрудник должен выполнить закупку.

Первый механизм:

```text
Assignment / ToDo
```

Смысл:

```text
кто сейчас должен сделать работу
→ Assignment
```

Если нужен только текущий рабочий исполнитель, не создаётся автоматически:

```text
executor → Link → User
```

Если позднее исполнитель должен стать неизменяемым бизнес-фактом, это уже другая ответственность.

Assignment сам создаёт ToDo и штатно уведомляет пользователя о назначении/снятии назначения. Отдельная Notification для дублирования этого события не нужна.

---

# 23. NEXT-B — Notification

Notification не дублирует:

```text
Workflow Action
Workflow Send Email Alert
Assignment notification
```

Для неё нужен отдельный смысл.

Пример:

> За два дня до `needed_by` по всё ещё актуальной заявке нужно напомнить ответственному.

Первый кандидат — штатная `Notification` с date-based event.

Но это уже расширяет эксплуатационную границу: date-based Notifications выполняются через scheduler infrastructure Frappe.

Поэтому такая ветка не должна незаметно попадать в lifecycle CORE, который пока сознательно не обучает scheduler/background jobs как отдельной архитектурной теме.

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

Не создаются автоматически:

```text
Purchase Request Attachment
Purchase Request Comment
Approval History
```

Если позднее нужен отдельный юридически значимый журнал с другой семантикой, модель пересматривается отдельно.

---

# 25. NEXT-D — Print

Возможное требование:

> Одобренную заявку нужно представить как печатный документ/PDF.

Первый шаг — проверить штатный Print View.

Если его недостаточно, следующий кандидат — `Print Format`.

Собственный PDF generator или отдельный frontend не вводится без другой ответственности.

Печатный контур может потребовать дополнительные зависимости среды; они добавляются только когда эта ветка действительно принимается.

---

# 26. Что второй практикум намеренно не покрывает

В обязательный маршрут не входят:

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
Web Form
Portal
custom frontend
Query Report
Script Report
complex User Permission model
Permission Type без отдельной команды
concurrency / locking
external integration
production deployment
```

NEXT-A/B/C/D также не становятся обязательными только потому, что паспорт их перечисляет.

---

# 27. Архитектурная карта после аудита

Обязательный lifecycle CORE:

```text
Purchase Request
        ↓
обычный status
        ↓
появились role-controlled transitions
        ↓
единый state field + Workflow
        ↓
появилось amount-based ветвление
        ↓
conditional transitions + Pending Senior
        ↓
self approval policy
        ↓
final approval стал фиксированным фактом
        ↓
Is Submittable / docstatus
        ↓
Cancelled появляется как docstatus 2
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

Эти две цепочки больше не смешиваются в одну только ради количества функций.

---

# 28. Источники

**[ДОКУМЕНТАЦИЯ FRAPPE]** `docstatus`:

- https://docs.frappe.io/framework/doctypes/docstatus

**[ОФИЦИАЛЬНАЯ ДОКУМЕНТАЦИЯ ЭКОСИСТЕМЫ]** Workflow:

- https://docs.frappe.io/erpnext/workflows
- https://docs.frappe.io/erpnext/workflow-actions

Workflow задаёт состояния, переходы, роли, условия и `Doc Status`; для submittable DocType активный Workflow заменяет обычный Save/Submit flow.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Workflow создаёт Custom Field состояния только если указанного поля нет в Meta:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py

Это основание не допускать скрытый site-local `workflow_state` для собственного Standard DocType.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** Workflow transitions, conditions, `apply_workflow()` и self approval:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py

`has_approval_access()` сравнивает пользователя с `doc.owner`, а `apply_workflow()` вызывает обычные `save()`, `submit()` и `cancel()` в зависимости от Doc Status следующего Workflow State.

**[ДОКУМЕНТАЦИЯ FRAPPE]** fixtures:

- https://docs.frappe.io/framework/user/en/python-api/hooks

**[ДОКУМЕНТАЦИЯ FRAPPE]** Assignment / ToDo:

- https://docs.frappe.io/framework/assignments-and-todos

**[ДОКУМЕНТАЦИЯ FRAPPE]** Notification:

- https://docs.frappe.io/framework/notifications

**[ДОКУМЕНТАЦИЯ FRAPPE]** Printing:

- https://docs.frappe.io/framework/user/en/desk/printing

**[ДОКУМЕНТАЦИЯ FRAPPE]** `Allow on Submit`:

- https://docs.frappe.io/framework/doctypes/allow-on-submit

**[ВНУТРЕННИЙ АРХИТЕКТУРНЫЙ СТАНДАРТ]**:

- [`03_DOCUMENT_LIFECYCLE.md`](../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md)
- [`04_SECURITY.md`](../frappe-architecture-standard/04_SECURITY.md)
- [`05_TRANSACTIONS_ASYNC.md`](../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md)
- [`08_UI_REPORTING.md`](../frappe-architecture-standard/08_UI_REPORTING.md)
- [`09_DEPLOYMENT_TESTING.md`](../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md)
- [`10_DECISION_STANDARD.md`](../frappe-architecture-standard/10_DECISION_STANDARD.md)

---

# 29. Критерий принятия паспорта после аудита

Перед созданием матрицы требований нужно ответить `да` на все вопросы:

```text
1. Purchase Request действительно создаёт реальную lifecycle-задачу?
2. Requester в обязательном сценарии явно равен Document.owner?
3. Обычный status появляется раньше Workflow?
4. Pending Senior не существует до требования второго approval level?
5. Cancelled не существует как обычный business state до docstatus?
6. После включения Workflow остаётся один source of truth состояния?
7. Workflow не создаёт скрытый обязательный Custom Field на dev-site?
8. Workflow появляется только после role-controlled transitions?
9. Conditional Workflow появляется из amount-based approval?
10. Self approval использует штатную семантику owner и явно ограничен этой моделью?
11. Rejected не перепутан с Cancelled?
12. Approved получает docstatus 1 только после отдельного требования о фиксации разрешения?
13. Workflow полностью описывает submit/cancel transitions после Is Submittable?
14. Cancel / Amend используется для изменения смысла зафиксированного факта?
15. Allow on Submit остаётся отдельным GATE?
16. DocType Permissions и Workflow roles не смешаны?
17. Workflow/Role configuration имеет App-owned delivery path?
18. Lifecycle contracts проверяются автоматически?
19. Финал проверяется на чистом Site?
20. Assignment/Notification/File/Comment/Version/Print не перегружают обязательный lifecycle CORE?
21. Notification не дублирует Workflow/Assignment и не скрывает scheduler dependency?
22. API/async/extension/integration не попали в CORE ради покрытия?
23. Первый и второй практикумы учат разным архитектурным классам задач?
```

Если хотя бы один ответ отрицательный, сначала исправляется паспорт. Матрица, граф и roadmap до этого не создаются.
