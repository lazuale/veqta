# Источники проверки практикума

Основная исполняемая версия курса — **Frappe Framework v16.32.0**.

Этот файл предназначен прежде всего для автора курса и технического аудита. Ученик не обязан читать исходники Framework до выполнения практических заданий.

Приоритет для version-sensitive утверждений:

1. фактический стенд `v16.32.0`;
2. exact source tag `v16.32.0`;
3. официальная документация;
4. moving `version-16` — только для анализа будущих изменений.

Архитектурные решения сверяются также с [общим стандартом](../frappe-architecture-standard/README.md), но инструкция конкретного урока не меняет закреплённую версию без повторной execution-проверки.

---

# 1. Версия и установка

- Release: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Tag: https://github.com/frappe/frappe/tree/v16.32.0
- Installation: https://docs.frappe.io/framework/user/en/installation
- Python requirements: https://github.com/frappe/frappe/blob/v16.32.0/pyproject.toml
- Node requirements: https://github.com/frappe/frappe/blob/v16.32.0/package.json

```text
Python >=3.14,<3.15
Node >=24
```

---

# 2. DocType / Document / data model

- DocTypes: https://docs.frappe.io/framework/user/en/basics/doctypes
- Field Types: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- Naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- Child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Single: https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype
- Virtual DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype
- DocType source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.json
- DocField: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docfield/docfield.json
- Document: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- BaseDocument: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py
- NestedSet: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/nestedset.py

Ключевой архитектурный вывод курса:

```text
DocType / Link / Child / Tree
выбираются по смыслу данных,
а не по желанию создать отдельную таблицу для каждого существительного
```

---

# 3. File / Comment / Version

- Attachments: https://docs.frappe.io/framework/user/en/desk/attachments
- Document API / comments: https://docs.frappe.io/framework/user/en/api/document
- Document Versioning: https://docs.frappe.io/erpnext/document-versioning

Используются в L4/L6 вместо собственных:

```text
Attachment Registry
Task Comment
Task History
```

`Version` в курсе означает штатную историю изменений и не объявляется юридически неизменяемым audit ledger.

---

# 4. Data Import / Export

- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- List View: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list

---

# 5. Permissions — Document и Permission Level 1

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- server permissions: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- metadata permission helpers: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/meta.py
- Document permission enforcement: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- high-permlevel handling: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py
- client permission model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/perm.js
- Form permission/actions: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/form.js
- Permission Manager: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.js

## If Owner / Create

На закреплённой версии owner-only folding server-side не применяется к `create`.

Поэтому модель:

```text
Requester
Create = Yes
Read = Yes + If Owner
Write = No
```

совместима с созданием нового Document и запретом обычного последующего save.

## Permission Level 1

В `facility_ops` на Level 1 находятся:

```text
subject
location
equipment
description
priority
target_date
attachment
```

Причина не универсальная, а предметная:

```text
Technician должен работать с Service Request
но не должен переписывать исходное содержание
```

Requester имеет Level 1 Write для заполнения нового Document. После insert отсутствие Level 0 Write блокирует обычный post-create save.

Technician имеет:

```text
Document Write = Yes
Permission Level 1 Write = No
```

и поэтому на обычном permission-aware Document path не получает права на содержательные Level 1 поля.

Explicit `ignore_permissions=True` не является частью этой гарантии.

## Почему отдельного Level 2 в курсе нет

`status` намеренно остаётся Permission Level 0.

До L7 это позволяет показать:

```text
Select values
≠ transition model
```

После L7 допустимость перехода становится ответственностью Workflow. Отдельный Permission Level для того же state field не нужен для учебной задачи.

---

# 6. Permission Types [v16+]

- Docs: https://docs.frappe.io/framework/permission-types

`Permission Type` — штатный механизм для дополнительного действия вроде `approve`, которое код приложения проверяет через `frappe.has_permission()`.

В базовом Core механизм **не практикуется**, потому что курс пока не создаёт собственное программное action, для которого такое право было бы естественным.

Статус:

```text
Later
```

Это не означает, что механизм не-Frappe-native.

---

# 7. Assign To / ToDo

- Docs: https://docs.frappe.io/framework/assignments-and-todos
- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.json
- ToDo controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.py

`Assign To` создаёт `ToDo` и работает с доступом к reference Document.

Главная граница курса:

```text
Assignment = responsibility
Assignment ≠ authorization
Assignment ≠ business status
```

---

# 8. Workflow — владелец переходов состояния после L7

- Workflow docs: https://docs.frappe.io/erpnext/workflows
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py
- client workflow: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/workflow.js
- Workflow source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition

Exact `v16.32.0` подтверждает:

- `validate_workflow()` проверяет допустимость state transition;
- `get_transitions()` учитывает current state, Allowed Role и Condition;
- новый Document без state получает первое состояние Workflow;
- попытка нового Document сразу оказаться в другом state не является допустимым transition;
- `apply_workflow()` меняет state field и сохраняет Document штатным lifecycle.

Поэтому в курсе:

```text
до L7
status = ordinary Select

после L7
Workflow = server transition boundary
```

`status Read Only` и `Only Allow Edit For` не выдаются за отдельную серверную ACL.

---

# 9. DocStatus / Submittable

- DocStatus: https://docs.frappe.io/framework/doctypes/docstatus
- Allow on Submit: https://docs.frappe.io/framework/doctypes/allow-on-submit

Lab B отделяет:

```text
business status
Workflow transitions
DocStatus Draft / Submitted / Cancelled
```

`Service Request` не становится Submittable только потому, что имеет terminal state `Closed`.

---

# 10. Kanban / views

- Kanban: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.py
- client set_value: https://github.com/frappe/frappe/blob/v16.32.0/frappe/client.py

Разные views не создают разные permission models.

В курсе Kanban сначала показывает обычное изменение Status, а после Workflow используется для сравнения с управляемым process lifecycle.

---

# 11. DocType Layout — версионная граница текущего курса

- Current docs: https://docs.frappe.io/framework/doctypes/doctype-layout
- Current repository path: https://github.com/frappe/frappe/tree/develop/frappe/core/doctype/doctype_layout

Архитектурный смысл механизма:

```text
один business object
+ одна identity/lifecycle model
+ разные формы для разных рабочих сценариев
→ сначала проверить DocType Layout
```

Не создавать второй `DocType` только ради другой компоновки формы.

Но в exact tag `v16.32.0` путь:

```text
frappe/core/doctype/doctype_layout/doctype_layout.json
```

отсутствует. Прямое чтение raw-файла возвращает `404`, поэтому текущий исполняемый курс **не объявляет DocType Layout изученным** и не включает его в Lab F.

Статус:

```text
Later / future baseline
```

После обновления базовой версии нужно отдельно повторить практическую проверку и только затем добавить лабораторию.

---

# 12. Reports / Workspace

- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Number Card: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- Dashboard Chart: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart
- Workspace source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace

L8 использует существующие `Service Request` как source data и не создаёт отдельный аналитический `DocType`.

---

# 13. Notification / Assignment Rule

- Notification: https://docs.frappe.io/framework/notifications
- Notification controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.py
- Assignment Rule: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.py

Assignment Rule использует штатный assignment mechanism.

```text
Automation ≠ Workflow
Automation ≠ permission escalation
```

Target Date остаётся содержательным Level 1 полем.

---

# 14. Scheduler vs Background Jobs

- Background Jobs docs: https://docs.frappe.io/framework/user/en/api/background_jobs
- source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/background_jobs.py

Core:

```text
наблюдает scheduler/workers в L0
использует scheduler-dependent Notification/Assignment Rule behavior в L9
```

Core **не создаёт собственную Background Job**.

Следующий уровень:

```text
frappe.enqueue
enqueue_after_commit
queues/timeouts
idempotency/retry reasoning
```

---

# 15. Auto Repeat

- Docs: https://docs.frappe.io/erpnext/auto-repeat
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/auto_repeat
- `make_repeatable`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

Lab C рассматривает Auto Repeat как отдельный штатный механизм повторного создания Documents.

---

# 16. Web Form

- Docs: https://docs.frappe.io/framework/user/en/web-form
- Settings: https://docs.frappe.io/framework/user/en/web-form/settings
- JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- Controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

## New insert

На exact `v16.32.0` новый target Document создаётся Web Form отдельным путём с `ignore_permissions=True`.

Следовательно:

```text
Web Form create
≠ proof ordinary Desk Role Permission
```

## Existing update

Разрешённый Web Form update может использовать permission-bypass path.

Поэтому финал курса:

```text
Allow Editing After Submit = No
```

## Authentication boundary

```text
Login Required
= user must authenticate
≠ role-specific authorization
```

---

# 17. Fixtures / customizations / install

- Hooks/fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- fixtures source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- customization sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/utils.py
- installer: https://github.com/frappe/frappe/blob/v16.32.0/frappe/installer.py
- source sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/sync.py

L11 поставляет:

```text
Standard source
fixtures: Roles + Workflow
exported Custom DocPerm: Level 0/1
```

и отдельно проверяет clean-site behavior.

---

# 18. Customize Form

- Docs: https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/customize_form
- Custom Field: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/custom_field
- Property Setter: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/property_setter

Lab D отделяет:

```text
изменение Standard source своего App
от
site/app customization поверх Standard DocType
```

---

# 19. Printing / PDF

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Print Format: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- PDF: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py
- generators: https://github.com/frappe/frappe/tree/v16.32.0/frappe/utils/pdf_generator
- `setup-chrome`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/commands/utils.py

---

# 20. Special fields / views

- Table MultiSelect: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/table_multiselect.js
- Barcode: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/barcode.js
- Duration: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/duration.js
- Signature: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/signature.js
- Geolocation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/geolocation.js
- Calendar: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/calendar/calendar.js
- Gantt: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/gantt/gantt_view.js

---

# 21. Realtime / REST / programming extensions — Later

- REST API: https://docs.frappe.io/framework/user/en/api/rest
- Realtime API: https://docs.frappe.io/framework/user/en/api/realtime
- Hooks: https://docs.frappe.io/framework/user/en/python-api/hooks
- Controllers: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- Server Script: https://docs.frappe.io/framework/user/en/desk/scripting/server-script
- Client Script: https://docs.frappe.io/framework/user/en/desk/scripting/client-script

Они остаются вне базового no-code маршрута не потому, что менее нативны, а потому что требуют отдельного программного контекста.

---

# 22. Automated testing — Later

- Testing: https://docs.frappe.io/framework/user/en/testing
- Unit Testing: https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing

Core заканчивается ручной clean-site acceptance.

`FrappeTestCase` и `bench run-tests` вводятся вместе с собственным программным поведением, а не для бессмысленного доказательства того, что стандартный `Link` или `get_doc` работает.
