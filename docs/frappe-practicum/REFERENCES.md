# Источники проверки практикума

Основная версия — **Frappe Framework v16.32.0**.

Этот файл — карта exact-source оснований для архитектуры, уроков и `INVARIANTS.md`.

Приоритет:

1. фактический стенд `v16.32.0`;
2. exact source tag `v16.32.0`;
3. официальная документация;
4. moving `version-16` только для будущих изменений.

---

# 1. Версия и установка

- Release: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Tag: https://github.com/frappe/frappe/tree/v16.32.0
- Installation: https://docs.frappe.io/framework/user/en/installation
- Python requirements: https://github.com/frappe/frappe/blob/v16.32.0/pyproject.toml
- Node requirements: https://github.com/frappe/frappe/blob/v16.32.0/package.json

Exact version:

```text
Python >=3.14,<3.15
Node >=24
```

Стек стенда фиксируется в `projects/00-lab/SETUP_WSL2.md`.

---

# 2. DocType / Document / fields

Документация:

- https://docs.frappe.io/framework/user/en/basics/doctypes
- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype

Exact source:

- DocType: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.json
- DocField: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docfield/docfield.json
- Document lifecycle: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- standard/optional fields: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/__init__.py

`_assign` — штатный optional field Frappe, не бизнес-поле `facility_ops`.

---

# 3. Data Import / Export / List

- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- List View: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list

L3 использует 10 дополнительных Equipment, negative import, filters, Saved Filter, export и Bulk Edit.

---

# 4. Permissions — hard boundary

Документация:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- https://docs.frappe.io/framework/data-masking
- https://docs.frappe.io/framework/permission-types

Exact source:

- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- permissions engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- Permission Manager UI: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.js

## Permission Level

Для `permlevel > 0` Permission Manager предоставляет field-level `read/write/mask`; document operations относятся к level 0.

## If Owner и Create — критический exact-source факт

`get_role_permissions()` при owner-only permission переносит permission type в `if_owner` только когда:

```text
ptype != "create"
```

Следовательно корректна комбинация курса:

```text
Facility Requester
Create = Yes
Read = Yes
Write = No
If Owner = Yes
```

Она означает:

```text
новый Service Request создать можно
после insert читать можно только собственный
post-create Write не выдаётся
```

То есть Requester append-only intake основан на реальном permission engine, а не на Workflow UI.

## Delete policy

`Delete` — обычный DocPerm permission type. L5 временно включает его Supervisor только для отдельного experiment и возвращает `No`.

Финальная app policy:

```text
Requester Delete = No
Technician Delete = No
Supervisor Delete = No
```

Это server permission рабочих ролей, но не попытка ограничить `Administrator`.

---

# 5. Assign To / ToDo — ответственность, не authorization

Документация:

- https://docs.frappe.io/framework/assignments-and-todos

Exact source:

- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.json
- ToDo controller/permissions: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.py

Из `assign_to._add()`:

```text
создаётся ToDo
↓
проверяется доступ assignee к reference document
↓
нет доступа + sharing разрешён
→ может создаться DocShare

нет доступа + sharing запрещён
→ Missing Permission
```

Поэтому:

```text
Assignment
≠ authorization
```

Основные Technician получают совместимый Role-based access заранее; Assignment не должен быть скрытым permission distributor.

`ToDo.update_in_reference()` обновляет штатное `_assign`, но `_assign` не становится доменным полем.

---

# 6. Workflow — server transition vs Desk editability

Документация:

- https://docs.frappe.io/erpnext/workflows
- https://docs.frappe.io/erpnext/workflow-actions
- https://docs.frappe.io/framework/user/en/audit-trail

Exact source:

- Workflow engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py
- client Workflow model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/workflow.js
- Workflow controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/workflow/doctype/workflow/workflow.py
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Workflow Action: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action
- Workflow Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition

## Server transition

`get_transitions()` / `validate_workflow()` используют current state, Allowed Role и Condition для state change.

`apply_workflow()` выбирает Transition по Action и сохраняет новый state.

Поэтому:

```text
Allowed Role / Condition
= server transition enforcement
```

## Only Allow Edit For

Client `frappe.workflow.is_read_only()` использует state `allow_edit` для Desk editability.

Поэтому:

```text
Only Allow Edit For
= Desk state guard
```

а не универсальная ACL любого update path.

## Новый local Document — критический compatibility fact

В exact client source:

```text
if (doc.__islocal) return false
```

в `is_read_only()`.

Следовательно новый Requester Document не становится read-only только потому, что:

```text
New.only_allow_edit_for = Facility Supervisor
```

Server `validate_workflow()` также не рассматривает insert первой state как переход между двумя states.

Это делает совместимой строгую модель:

```text
Requester Create = Yes
New Desk edit role = Supervisor
Requester post-create Write = No
```

---

# 7. Kanban + Workflow

- Kanban Board: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.py
- `frappe.set_value`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/__init__.py
- client set_value: https://github.com/frappe/frappe/blob/v16.32.0/frappe/client.py

Kanban update приходит к обычному save, поэтому Workflow validation не исчезает.

Но Kanban move не является `apply_workflow(Action)`, поэтому Status-Kanban удаляется после L7.

---

# 8. Reports / Cards / Charts / Workspace

- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Report JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/report/report.json
- Number Card: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- Dashboard Chart: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart
- Workspace: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace

L8 создаёт один Report Builder, три Number Cards, один Chart и `Facility Operations Control` Workspace.

---

# 9. Notification / Assignment Rule

- Notification docs: https://docs.frappe.io/framework/notifications
- Notification JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.json
- Notification controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.py
- Assignment Rule JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.json
- Assignment Rule controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.py

Assignment Rule поддерживает Round Robin, Load Balancing, Based on Field, Weighted Distribution.

`do_assignment()` вызывает штатный `assign_to._add(...)`.

`Due Date Based On` передаёт значение field в ToDo `date`; `update_due_date()` обновляет Rule-owned open ToDo.

Close Condition закрывает ToDo только как behavior конкретного Assignment Rule.

```text
Workflow Close
≠ универсально ToDo Close
```

---

# 10. Target Date / date-based Notification

`Days After = 1` означает точку через один день после Reference Date.

Поэтому Notification называется:

```text
Service Request One Day Overdue
```

`Target Date` Optional, значит due/overdue behavior — conditional invariant.

---

# 11. Auto Repeat

- docs: https://docs.frappe.io/erpnext/auto-repeat
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/auto_repeat
- `make_repeatable`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

`Allow Auto Repeat` создаёт служебный `auto_repeat` Custom Field; Lab C его очищает и восстанавливает L9 Assignment Rule.

---

# 12. Web Form — security boundary

Документация:

- https://docs.frappe.io/framework/user/en/web-form
- https://docs.frappe.io/framework/user/en/web-form/settings
- https://docs.frappe.io/framework/user/en/web-form/customization

Exact source:

- Web Form JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- Web Form controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

## Owner update

В `accept()`:

```text
data.name + allow_edit = false
→ update отклоняется
```

Owner/web-form permission при `Apply Document Permissions = No` может сохранить разрешённый update через:

```text
doc.save(ignore_permissions=True)
```

Поэтому финал L10:

```text
Allow Editing After Submit = No
```

## Link options

При login-required форме без `Allow Read On All Link Options` Link options по умолчанию получают owner filter.

С `Allow Read On All Link Options = Yes` общий каталог options доступен через `frappe.get_all`.

Threat model курса:

```text
Website User = trusted internal reporter
```

Public untrusted external catalog — Later.

---

# 13. Fixtures / customizations / install

- Hooks/fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- fixtures: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- customization sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/utils.py
- installer: https://github.com/frappe/frappe/blob/v16.32.0/frappe/installer.py
- standard source sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/sync.py
- import flags: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/import_file.py

`install_app()` выполняет initial sync source/fixtures/customizations/dashboards.

L11 поэтому использует последующий `migrate` как convergence/update test, а не как обязательную вторую половину первоначальной установки.

---

# 14. Customize Form

- https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/customize_form
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/custom_field
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/property_setter

Lab D не учит ложной модели «удалил строку из exported JSON — migrate гарантированно удалил уже синхронизированный Custom Field другого site».

---

# 15. Printing / PDF

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Print Format: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- PDF: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py
- generators: https://github.com/frappe/frappe/tree/v16.32.0/frappe/utils/pdf_generator
- built-in hooks: https://github.com/frappe/frappe/blob/v16.32.0/frappe/hooks.py
- `setup-chrome`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/commands/utils.py

Lab E использует штатный Chromium generator.

---

# 16. Special fields / Calendar / Gantt

- Table MultiSelect: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/table_multiselect.js
- Barcode: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/barcode.js
- Duration: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/duration.js
- Signature: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/signature.js
- Geolocation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/geolocation.js
- Calendar: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/calendar/calendar.js
- Gantt: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/gantt/gantt_view.js
- Event config: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/event/event_calendar.js

Own Calendar/Gantt mapping требует JS configuration и остаётся Later.

---

# 17. Что намеренно Later

```text
Server Script
custom controller validation
custom has_permission / permission_query_conditions
assignee-only authorization
hard state-dependent immutability
public untrusted portal catalog
custom Client Script / JS
arbitrary multi-app integration audit
production hardening
```

Поэтому `INVARIANTS.md` разделяет server guarantees, structural rules, UI guards и site policies.
