# Источники проверки

Практикум зафиксирован на **Frappe Framework v16.32.0**.

## Правило источников

1. Фактический стенд `v16.32.0` — execution proof курса.
2. Exact source tag `v16.32.0` — главный источник version-sensitive runtime behavior.
3. Официальная документация — публичная модель и назначение механизма.
4. `version-16`/`develop` — только последующее состояние, не доказательство pinned курса.
5. ERPNext может служить first-party примером использования Framework mechanism, но не становится зависимостью учебных app.

---

# Версия и среда

- Release: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Exact tag: https://github.com/frappe/frappe/tree/v16.32.0
- Installation: https://docs.frappe.io/framework/user/en/installation
- Python: https://github.com/frappe/frappe/blob/v16.32.0/pyproject.toml
- Node: https://github.com/frappe/frappe/blob/v16.32.0/package.json
- Migration notes v16: https://github.com/frappe/frappe/wiki/Migrating-to-version-16

```text
Python >=3.14,<3.15
Node >=24
```

---

# Bench / app / Module / Desk

- Create an App: https://docs.frappe.io/framework/user/en/tutorial/create-an-app
- Create a Site: https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- Apps Page: https://docs.frappe.io/framework/user/en/apps-page
- Desk: https://docs.frappe.io/framework/user/en/desk
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Workspace source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace
- Module Def: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/module_def

Frappe v16 использует Apps Page, Workspace Sidebar и Workspace. Custom app регистрируется
на Apps Page через `add_to_apps_screen`.

---

# DocType / Document / data model

- DocType: https://docs.frappe.io/framework/user/en/basics/doctypes
- Field Types: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- Naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- Child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Single DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype
- Tree API: https://docs.frappe.io/framework/user/en/api/tree
- Controllers: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- DocType schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.json
- DocField schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docfield/docfield.json
- Document implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- BaseDocument: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py
- NestedSet: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/nestedset.py

P1–P3 используют metadata guarantees там, где они совпадают с требованием. Engineering
E1 добавляет Controller только для creation invariant, которого Link/Unique/Set Only Once
не выражают.

---

# Document lifecycle / Controller

Exact source:

- Document: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- Controller docs: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers

`Document.insert()` в exact `v16.32.0` отдельно выполняет `before_insert`, затем обычные
before-save methods, включая `validate`, и после этого DB insert / post-insert lifecycle.

Это важно для E1. Требование звучит:

```text
при СОЗДАНИИ Service Case
source Intake должен быть Accepted
```

Поэтому владелец — `ServiceCase.before_insert`, а не общий `validate()`.

Причина не стилистическая: Agent по модели P3 имеет Write на `Service Case`, но не имеет
Read на `Service Intake`. Если controller загружает Intake при каждом `validate()`,
последующий Agent-save существующего Case ломается либо вынуждает выдать лишний доступ.

```text
creation-only invariant
→ before_insert

invariant каждого save
→ validate / другая matching lifecycle phase
```

`Document.run_method()` также запускает controller method вместе с Framework hooks,
notifications, webhooks и server-script document events.

---

# Data operations / views / reports

- List View source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list
- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- Kanban Board: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/kanban_board
- Calendar View schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/calendar_view/calendar_view.json
- Number Card: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- Dashboard Chart: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart

Kanban используется в P1 только для ordinary Select state. P2 Workflow state не получает
альтернативный drag-path.

---

# Permissions

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Permission Types: https://docs.frappe.io/framework/permission-types
- Permission engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- Meta permission helpers: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/meta.py
- Document enforcement: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- Client permission model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/perm.js

Engineering command не использует `ignore_permissions=True`: source Intake проверяет
Write, `case.insert()` идёт обычным permission-aware Document path, а
`ServiceCase.before_insert` проверяет право читать выбранный source Intake только на
creation path.

---

# Workflow / docstatus

- Workflow manual: https://docs.frappe.io/erpnext/user/manual/en/workflows
- Workflow engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py
- Workflow controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/workflow/doctype/workflow/workflow.py
- Workflow schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/workflow/doctype/workflow/workflow.json
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Workflow Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition

P2 отделяет ordinary submit/cancel/amend lifecycle от Workflow до их объединения.
P3 показывает business state с `docstatus=0`, когда submit/cancel семантически не нужны.

Exact workflow source также показывает, что новый Document получает первый Workflow state,
если state field ещё пуст. Это совместимо с созданием нового `Service Case` в initial
`Open` state без отдельного перехода из несуществующего состояния.

---

# Assignment / Notification / history

- Assignments and ToDos: https://docs.frappe.io/framework/assignments-and-todos
- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/todo
- Notification: https://docs.frappe.io/framework/notifications
- Notification source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/email/doctype/notification
- Assignment Rule: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/assignment_rule
- Document API/comments: https://docs.frappe.io/framework/user/en/api/document

Assignment остаётся responsibility mechanism, не ACL.

---

# Web Form

- Web Form: https://docs.frappe.io/framework/user/en/web-form
- Settings: https://docs.frappe.io/framework/user/en/web-form/settings
- Customization: https://docs.frappe.io/framework/user/en/web-form/customization
- Schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- Controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

Exact `v16.32.0` facts used by P3:

- unpublished form is blocked;
- Login Required separates Guest/authenticated access but is not role-specific ACL;
- new target Document is inserted by Web Form path with `ignore_permissions=True`;
- edit existing target has its own `allow_edit` boundary;
- Standard Web Form can live in app source.

Поэтому public Web Form targets `Service Intake`, а не internal `Service Case`.

---

# REST / semantic API

Official REST:

- REST API: https://docs.frappe.io/framework/user/en/api/rest
- Authentication: https://docs.frappe.io/framework/user/en/api/rest#authentication

Exact REST API v2 implementation:

- https://github.com/frappe/frappe/blob/v16.32.0/frappe/api/v2.py

В exact source есть:

```text
GET/POST/PATCH/DELETE Document routes
POST /api/v2/document/<doctype>/<name>/method/<method>/
```

Document method route проверяет whitelisting, HTTP method и permission на Document, затем
запускает controller method через `doc.run_method()`.

Engineering E3/E4 поэтому различает:

```text
Document CRUD API
vs
semantic document command
```

Внутренние функции `frappe/api/v2.py` не используются как Python API приложения: сам
source предупреждает, что route implementations не являются стабильным internal-call
contract.

Whitelisting decorator implementation:

- https://github.com/frappe/frappe/blob/v16.32.0/frappe/__init__.py

`@frappe.whitelist(methods=["POST"])` ограничивает semantic command write-методом.

---

# Request transactions

Official database API:

- https://docs.frappe.io/framework/user/en/api/database

Exact source:

- request application: https://github.com/frappe/frappe/blob/v16.32.0/frappe/app.py
- database transaction callbacks: https://github.com/frappe/frappe/blob/v16.32.0/frappe/database/database.py

В `app.py` write/unsafe request при успешном завершении commit-ится через Framework.
Exception path выполняет rollback.

`database.py` имеет callback managers:

```text
before_commit
after_commit
before_rollback
after_rollback
```

Engineering E5 намеренно проверяет rollback после уже выполненного `case.insert()` и не
добавляет manual `frappe.db.commit()` в command.

---

# Background Jobs / after commit

- Docs: https://docs.frappe.io/framework/user/en/api/background_jobs
- Exact source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/background_jobs.py

В `v16.32.0` `frappe.enqueue` имеет:

```text
enqueue_after_commit
job_id
deduplicate
```

При `enqueue_after_commit=True` enqueue регистрируется через
`frappe.db.after_commit.add(...)`.

Worker execution commit-ит успешную job и rollback-ит exception path.

E8 не добавляет fake job в `service_intake`: механизм выбирается только если появляется
реальная heavy/slow responsibility.

---

# Webhook

- Docs: https://docs.frappe.io/framework/user/en/guides/integration/webhooks
- Queue/after-commit source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/integrations/doctype/webhook/__init__.py
- Webhook implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/integrations/doctype/webhook/webhook.py

Exact Webhook поддерживает DocType event, condition, headers, JSON/form payload, secret
signature и request log.

Для ordinary DocType events `run_webhooks()` сначала складывает webhook execution в
transaction-local queue. Framework регистрирует `flush_webhook_execution_queue` через
`frappe.db.after_commit`; после успешного commit flush ставит фактическую webhook
execution в Background Job выбранной/default очереди.

Следствие для E8:

```text
simple configurable outbound event
→ штатный Webhook уже имеет post-commit/background path
```

Не нужно вручную создавать второй custom job вокруг обычного Webhook только ради
асинхронности.

---

# Migrate / patches / fixtures

- Migration guide: https://docs.frappe.io/framework/user/en/guides/deployment/migrations
- Bench migrate: https://docs.frappe.io/framework/user/en/bench/reference/migrate
- Hooks/fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Fixtures source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- Migrate source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/migrate.py
- Patch handler: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/patch_handler.py

Exact `migrate.py` выполняет patches вокруг schema sync, затем fixtures/customizations и
другие post-schema tasks.

Exact `patch_handler.py` поддерживает:

```text
[pre_model_sync]
[post_model_sync]
```

Data patch, зависящий от нового `converted_at`, помещается в `post_model_sync`.

Direct `frappe.db.set_value` в E6 — deliberate one-off migration bypass. Это не общий
pattern для business CRUD.

---

# Automated tests

- Unit/integration testing guide: https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing
- Test command source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/commands/testing.py
- Test environment: https://github.com/frappe/frappe/blob/v16.32.0/frappe/testing/environment.py
- IntegrationTestCase: https://github.com/frappe/frappe/blob/v16.32.0/frappe/tests/classes/integration_test_case.py
- Test exports: https://github.com/frappe/frappe/blob/v16.32.0/frappe/tests/__init__.py

Exact v16.32 exposes `IntegrationTestCase` through `frappe.tests` and `run-tests` accepts
an app selector.

Test environment и `IntegrationTestCase` подготавливают dependencies для suite; setup
может commit-ить test dependencies. Поэтому Engineering E7 использует отдельный
`intake-test.localhost`, а не рабочий `intake.localhost`.

Tests проверяют application-owned behavior, включая regression boundary:

```text
Agent has no Intake Read
but can save existing Case
```

Это защищает `before_insert` от случайного возврата к слишком широкому `validate()`.

---

# Printing

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Print Format: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- PDF: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py

---

# Extension mechanisms следующего блока

Эти механизмы архитектурно нативны, но текущим трём продуктам не нужна искусственная
реализация:

- Client Script / Form API: https://docs.frappe.io/framework/user/en/api/form
- Server Script: https://docs.frappe.io/framework/user/en/desk/scripting/server-script
- Hooks / `doc_events`: https://docs.frappe.io/framework/user/en/python-api/hooks
- custom permission hooks: https://docs.frappe.io/framework/user/en/python-api/hooks
- Query/Script Reports: https://docs.frappe.io/framework/user/en/desk/reports
- Virtual DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype

Server Script с v15 disabled by default in shared-bench contexts. Он не используется как
замена source-controlled controller собственного app.

Курс не делает moving-version feature исполняемым только потому, что он появился в
более новой v16 документации: сначала механизм проверяется по exact `v16.32.0`.
