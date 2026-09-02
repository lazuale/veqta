# 12. Evidence Register

## 1. Назначение

Этот файл отделяет первичные факты Frappe от наших архитектурных выводов.

Любое сильное нормативное утверждение стандарта должно иметь понятную доказательную цепочку:

```text
ФАКТ FRAPPE
    ↓
ПЕРВИЧНЫЙ ИСТОЧНИК
    ↓
АРХИТЕКТУРНОЕ СЛЕДСТВИЕ
    ↓
ГРАНИЦА / ИСКЛЮЧЕНИЕ
```

Нельзя выдавать архитектурный вывод за прямое правило мейнтейнеров.

---

## 2. Иерархия источников

Приоритет источников:

```text
1. version-specific upstream source
2. актуальная официальная документация Frappe
3. release / migration notes
4. first-party ERPNext/Frappe Apps как практика
5. community discussion только как дополнительный контекст
```

ERPNext implementation показывает, что подход реально используется first-party проектом, но сам по себе не превращает его в обязательный Framework contract.

---

## E01. Frappe — metadata-driven full-stack framework

### Факт

Frappe позиционирует себя как metadata-driven full-stack low-code framework.

### Источники

- https://docs.frappe.io/framework/user/en/basics
- `frappe/frappe` `version-16/pyproject.toml`

### Архитектурное следствие

Metadata и DocType должны рассматриваться как фундамент application model, а не только как генератор формы.

### Граница

Это не означает запрет custom code или custom frontend.

---

## E02. Configuration over code

### Факт

Официальная философия Frappe предпочитает configuration over code и минимизацию кода там, где generic capability уже существует.

### Источник

- https://docs.frappe.io/framework/user/en/basics/why

### Следствие

Перед собственным generic mechanism проверяется встроенная capability.

### Граница

Если semantics встроенного механизма не соответствует requirement, normal Python code является штатным решением.

---

## E03. DocType — core building block

### Факт

Официальная документация называет DocType core building block приложений Frappe.

### Источник

- https://docs.frappe.io/framework/user/en/basics/doctypes

### Следствие

Data model проектируется прежде всего в терминах Frappe Documents/metadata.

### Граница

DocType не обязан соответствовать только business entity: Framework использует DocTypes также для settings/logs/configuration/system records.

---

## E04. Child DocType имеет parent semantics

### Факт

Child records связаны с parent через `parent`, `parenttype`, `parentfield`, `idx` и предназначены для composition внутри parent Document.

### Источник

- https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype

### Следствие

Повторяющиеся составные строки документа естественно моделировать Child Table.

### Граница

Если row имеет независимые permissions/lifecycle/references, standalone DocType может быть лучше.

---

## E05. Single DocType

### Факт

Single DocType предназначен для единственного settings-like record.

### Источник

- https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype

### Следствие

Не нужно создавать ordinary DocType и вручную запрещать вторую запись, если semantics действительно singleton.

---

## E06. Virtual DocType

### Факт

Virtual DocType позволяет представлять внешний/non-standard storage через Document-like interface.

### Источник

- https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype

### Следствие

Если внешний dataset должен участвовать во Frappe как Documents, Virtual DocType — официальный primitive.

### Граница

Для простого API client отдельный Virtual DocType может быть избыточен.

---

## E07. Document Controller lifecycle

### Факт

Controllers наследуют `frappe.model.document.Document`; Framework предоставляет lifecycle hooks `validate`, `on_update`, `on_submit`, `on_cancel` и другие.

### Источники

- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- `frappe/frappe` `version-16/frappe/model/document.py`

### Upstream confirmation

`Document._save()` выполняет permission checks и `validate` до update, `on_update` после update.

### Следствие

Business invariants собственного DocType естественно защищать server-side lifecycle.

---

## E08. Client Script ограничен browser form

### Факт

Client Script выполняется на client/browser side и его validation не является универсальной server guarantee.

### Источник

- https://docs.frappe.io/framework/user/en/desk/scripting/client-script

### Следствие

Critical data invariant нельзя защищать только Client Script.

---

## E09. docstatus имеет фиксированную semantics

### Факт

Frappe использует:

```text
0 Draft
1 Submitted
2 Cancelled
```

### Источник

- https://docs.frappe.io/framework/doctypes/docstatus

### Следствие

`docstatus` не следует использовать как произвольный business status.

### Граница

Workflow может управлять переходами, связанными с docstatus.

---

## E10. Workflow

### Факт

Workflow моделирует states/transitions/roles/conditions для управляемого процесса.

### Источник

- https://docs.frappe.io/erpnext/workflows

### Следствие

Approval processes сначала проверяются на semantic fit стандартной Workflow model.

### Граница

Сложная dynamic state machine может потребовать domain logic.

---

## E11. Permission engine

### Факт

Frappe имеет централизованную permission system с Role permissions, owner logic, User Permissions, sharing и extension hooks.

### Источники

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- `frappe/frappe` `version-16/frappe/permissions.py`

### Upstream confirmation

`get_doc_permissions()` учитывает controller permission veto, role permissions, owner и User Permissions.

### Следствие

Не создавать параллельный ACL до проверки штатной permission model.

---

## E12. Controller permission hook может veto

### Факт

Upstream `permissions.py` прямо фиксирует, что controller permission logic может deny, но не выдаёт permission, отсутствующую в базовой model.

### Источник

- `frappe/frappe` `version-16/frappe/permissions.py`, `has_controller_permissions`

### Следствие

Custom permission logic — extension базового engine, а не независимый replacement.

---

## E13. Document REST API

### Факт

Frappe предоставляет generic REST CRUD для DocTypes.

### Источники

- https://docs.frappe.io/framework/user/en/api/rest
- `frappe/frappe` `version-16/frappe/api/v2.py`

### Upstream confirmation

API v2 routes содержат document create/read/update/delete; update использует Document `save()`, create — `insert()`.

### Следствие

Для обычного Frappe-aware CRUD не нужно автоматически создавать дублирующие endpoints.

### Граница

Dedicated public/domain contract может быть оправдан.

---

## E14. Public route implementation ≠ public Python API

### Факт

`frappe/api/v2.py` содержит предупреждение, что route handler functions не следует использовать как стабильный Python API.

### Источник

- `frappe/frappe` `version-16/frappe/api/v2.py`

### Следствие

App должен зависеть от public/documented Framework APIs, а не от internal route implementation.

---

## E15. Background Jobs

### Факт

Frappe имеет штатную background queue и `frappe.enqueue`.

### Источники

- https://docs.frappe.io/framework/user/en/api/background_jobs
- `frappe/frappe` `version-16/frappe/utils/background_jobs.py`

### Upstream confirmation

Поддерживаются queues, timeout, callbacks, job ids, deduplication и `enqueue_after_commit`.

### Следствие

Долгая/асинхронная site operation сначала рассматривает штатный job subsystem.

---

## E16. Scheduler

### Факт

Frappe предоставляет scheduler events для периодической application work.

### Источник

- https://docs.frappe.io/framework/user/en/api/background_jobs

### Следствие

Собственный daemon для обычной site-periodic task требует обоснования.

---

## E17. Transactions

### Факт

Frappe управляет transactions для web requests/jobs/patches и предоставляет commit/rollback callbacks.

### Источник

- https://docs.frappe.io/framework/user/en/api/database

### Следствие

Обычный lifecycle не должен быть усеян ручными commits; external side effects должны учитывать commit boundary.

---

## E18. Direct DB update может обходить lifecycle

### Факт

Database APIs вроде direct value update не обязаны вызывать обычные Document validation/events.

### Источник

- https://docs.frappe.io/framework/user/en/api/database

### Следствие

DB bypass применяется намеренно, а не как обычная замена `doc.save()`.

---

## E19. Hooks — официальный extension mechanism

### Факт

Hooks предназначены для расширения/override стандартного поведения Framework/App.

### Источник

- https://docs.frappe.io/framework/user/en/python-api/hooks

### Следствие

Перед patching core нужно проверять официальный extension seam.

---

## E20. extend_doctype_class [v16+]

### Факт

Frappe v16 предоставляет `extend_doctype_class` для добавления поведения существующему Controller без полной замены.

### Источник

- https://docs.frappe.io/framework/user/en/python-api/hooks

### Следствие

На v16+ extension обычно предпочтительнее full override, когда задача именно добавить behavior.

---

## E21. First-party services существуют

### Факт

ERPNext использует service classes/modules для сложной предметной логики, например Stock Ledger, Tax, Asset и другие services.

### Источники

- `frappe/erpnext` `erpnext/stock/services/stock_ledger_service.py`
- `frappe/erpnext` `erpnext/accounts/services/taxes.py`
- другие first-party service modules

### Следствие

Утверждение «Service Layer противоречит Frappe» неверно.

Правильный критерий — наличие самостоятельной responsibility.

---

## E22. Webhook

### Факт

Frappe предоставляет Webhook для отправки HTTP requests по Document events/conditions.

### Источник

- https://docs.frappe.io/framework/user/en/guides/integration/webhooks

### Следствие

Для простого outbound event сначала проверяется Webhook.

### Граница

Надёжная stateful integration может требовать собственного outbox/service.

---

## E23. Notification

### Факт

Frappe имеет configurable Notification mechanism по событиям/условиям/датам.

### Источник

- https://docs.frappe.io/framework/notifications

### Следствие

Простое пользовательское уведомление не требует собственного notification engine.

---

## E24. Assignment

### Факт

Frappe предоставляет Assignment/ToDo и Assignment Rules.

### Источник

- https://docs.frappe.io/framework/assignments-and-todos

### Следствие

Operational assignment сначала проверяет built-in capability.

### Граница

Business field `responsible_user` может иметь другую semantics и не обязан исчезать.

---

## E25. Reports

### Факт

Frappe предоставляет Report Builder, Query Report и Script Report для разных reporting scenarios.

### Источники

- https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- https://docs.frappe.io/framework/user/en/guides/reports-and-printing/how-to-make-query-report
- https://docs.frappe.io/framework/user/en/guides/reports-and-printing/how-to-make-script-reports

### Следствие

Report mechanism выбирается по природе dataset/logic, а не по искусственной лестнице сложности.

---

## E26. Web Form

### Факт

Web Form позволяет external/browser interaction поверх DocType.

### Источник

- https://docs.frappe.io/framework/user/en/web-form

### Следствие

Простая внешняя форма не требует отдельного frontend автоматически.

---

## E27. Migrations and patches

### Факт

`bench migrate` синхронизирует schema/metadata и выполняет patches; Frappe имеет штатный migration lifecycle.

### Источник

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations

### Следствие

Обязательные data/schema migrations должны ехать с App, а не жить в ручной инструкции production SQL.

---

## E28. Exported customizations

### Факт

Frappe поддерживает экспорт Custom Fields/Property Setters/customization в App.

### Источник

- https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

### Следствие

Принятая site customization может быть переведена в воспроизводимый product artifact.

---

## E29. Server Script restrictions

### Факт

Server Script является штатным mechanism, но имеет security/deployment restrictions и может быть disabled в shared environments.

### Источник

- https://docs.frappe.io/framework/user/en/desk/scripting/server-script

### Следствие

Нельзя считать Server Script обязательной промежуточной ступенью перед normal Python App code.

---

## E30. Automated testing

### Факт

Frappe предоставляет testing infrastructure и `bench run-tests`.

### Источник

- https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing

### Следствие

Critical custom contracts должны быть воспроизводимо проверяемыми.

---

# Правило использования реестра

Если новый раздел стандарта говорит:

> «Frappe задумано именно так»

он должен ссылаться на прямой факт/первичный источник.

Если источники подтверждают только capabilities, а recommendation выводим мы, формулировка должна быть:

> **архитектурное следствие / рекомендация стандарта**.

Это принципиальная граница доказательности всего документа.
