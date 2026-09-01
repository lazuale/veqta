# Источники проверки практикума

Основная версия — **Frappe Framework v16.32.0**.

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

---

# 2. DocType / Document

- DocTypes: https://docs.frappe.io/framework/user/en/basics/doctypes
- Field Types: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- Naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- Child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Single: https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype
- DocType source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.json
- DocField: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docfield/docfield.json
- Document lifecycle: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- model standard/optional fields: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/__init__.py

`_assign` — штатное optional field Frappe, не business field `facility_ops`.

---

# 3. Data Import / Export

- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- List View: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list

---

# 4. Permissions

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Permission Types: https://docs.frappe.io/framework/permission-types
- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- permission engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- Permission Manager: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.js

## If Owner / Create

Exact `get_role_permissions()` owner-only folding исключает:

```text
ptype == "create"
```

Поэтому работает финальная Desk policy:

```text
Requester
Create = Yes
Read = Yes
Write = No
If Owner = Yes
```

то есть Create возможен, owner read остаётся, post-create Write не выдаётся.

## Delete

Delete — обычный DocPerm permission type. В финале `Service Request Delete = No` у всех рабочих ролей; L5 включает его Supervisor только временно.

---

# 5. Assign To / ToDo

- docs: https://docs.frappe.io/framework/assignments-and-todos
- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.json
- ToDo controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.py

`assign_to._add()` создаёт ToDo и проверяет access assignee. При недостаточном access штатный механизм может создать DocShare; при disabled sharing возможен Missing Permission.

Поэтому:

```text
Assignment ≠ authorization
```

---

# 6. Workflow

- docs: https://docs.frappe.io/erpnext/workflows
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py
- client model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/workflow.js
- Workflow source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Workflow Action: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action
- Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition

Server transition проверяет state/role/condition.

```text
Allowed Role / Condition
= server transition gate
```

Client `is_read_only()` использует state `allow_edit`:

```text
Only Allow Edit For
= Desk guard
```

Критический exact-source факт:

```text
if (doc.__islocal) return false
```

поэтому New state с edit role Supervisor не мешает Requester заполнить новый local Document. После insert Role Permission `Write = No` становится настоящей boundary.

---

# 7. Kanban

- Kanban Board: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.py
- `frappe.set_value`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/__init__.py
- client set_value: https://github.com/frappe/frappe/blob/v16.32.0/frappe/client.py

Kanban update идёт через обычный save, но не является `apply_workflow(Action)` lifecycle.

---

# 8. Reports / Workspace

- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Number Card: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- Dashboard Chart: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart
- Workspace source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace

---

# 9. Notification / Assignment Rule

- Notification: https://docs.frappe.io/framework/notifications
- Notification source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.py
- Assignment Rule JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.json
- Assignment Rule controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.py

`do_assignment()` использует штатный Assign To.

Close Condition Rule-owned ToDo — behavior конкретного Assignment Rule, не универсальное свойство Workflow.

Target Date Optional, поэтому due/overdue behavior conditional.

---

# 10. Auto Repeat

- docs: https://docs.frappe.io/erpnext/auto-repeat
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/auto_repeat
- `make_repeatable`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

---

# 11. Web Form — ключевая permission граница

Документация:

- https://docs.frappe.io/framework/user/en/web-form
- https://docs.frappe.io/framework/user/en/web-form/settings
- https://docs.frappe.io/framework/user/en/web-form/customization

Exact source:

- Web Form JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- Web Form controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

## Published

`raise_if_unpublished()` блокирует direct API use непубликованной формы.

## Login Required

`accept()` блокирует Guest при `login_required = true`.

Это authentication boundary, не role-specific authorization.

## New insert

Критический exact-source факт:

```text
new target Document
→ doc.insert(ignore_permissions=True, ...)
```

Следовательно:

```text
Web Form submit
≠ Role Permission Create check
```

`Apply Document Permissions` не меняет это поведение нового insert.

Поэтому L10/L11 разделяют:

```text
Desk Requester create
→ proof Role Permission Create

Website User Web Form create
→ proof Web Form intake capability
```

## Existing document

Для existing Document:

```text
Apply Document Permissions = Off
→ owner / website permission model

Apply Document Permissions = On
→ ordinary document permission model
```

При разрешённом owner edit update может сохраняться через:

```text
doc.save(ignore_permissions=True)
```

поэтому final:

```text
Allow Editing After Submit = No
```

## Link options

Login-required Link options без `Allow Read On All Link Options` получают owner filter. Включение этой настройки сознательно раскрывает authenticated reporters общий каталог имён.

---

# 12. Fixtures / customizations / install

- Hooks/fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- fixtures implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- customization sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/utils.py
- installer: https://github.com/frappe/frappe/blob/v16.32.0/frappe/installer.py
- source sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/sync.py

`install_app()` выполняет initial source/fixtures/customizations/dashboard sync. Последующий migrate в L11 — convergence test.

---

# 13. Customize Form

- docs: https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/customize_form
- Custom Field: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/custom_field
- Property Setter: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/property_setter

---

# 14. Printing / PDF

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Print Format: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- PDF: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py
- generators: https://github.com/frappe/frappe/tree/v16.32.0/frappe/utils/pdf_generator
- `setup-chrome`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/commands/utils.py

---

# 15. Special fields / Calendar / Gantt

- Table MultiSelect: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/table_multiselect.js
- Barcode: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/barcode.js
- Duration: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/duration.js
- Signature: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/signature.js
- Geolocation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/geolocation.js
- Calendar: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/calendar/calendar.js
- Gantt: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/gantt/gantt_view.js

---

# 16. Later

```text
Server Script
custom controller validation
custom has_permission / permission_query_conditions
assignee-only authorization
hard Closed immutability
role-restricted/public-untrusted portal intake
custom Client Script / JS
arbitrary multi-app integration audit
production hardening
```

Именно поэтому `INVARIANTS.md` разделяет hard guarantees, structure, UI guards, conditional behavior и deployment policies.
