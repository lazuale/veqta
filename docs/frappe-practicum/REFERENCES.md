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
- Python: https://github.com/frappe/frappe/blob/v16.32.0/pyproject.toml
- Node: https://github.com/frappe/frappe/blob/v16.32.0/package.json

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
- Document: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- BaseDocument: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py

`_assign` — штатное optional field Frappe, не business field `facility_ops`.

---

# 3. Data Import / Export

- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- List View: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list

---

# 4. Permissions — exact basis hardened architecture

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Permission Types: https://docs.frappe.io/framework/permission-types
- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- server permissions: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- metadata permission helpers: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/meta.py
- Document permission enforcement: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- high-permlevel reset: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py
- client permission model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/perm.js
- Form permission/actions: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/form.js
- Permission Manager: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.js

## If Owner / Create

Owner-only folding server-side не применяется к `create`.

Поэтому Level 0:

```text
Requester
Create = Yes
Read = Yes
Write = No
If Owner = Yes
```

совместим с созданием нового Document и запретом последующего save.

## Local form + permlevel

Client `frappe.perm.get_perm()` для local doc использует doctype role permissions.

`get_field_display_status()` вычисляет field access через:

```text
df.permlevel
→ perm[df.permlevel]
→ p.write / p.read
```

Это exact основание трёхуровневой модели.

### Level 1

```text
subject/location/equipment/description/priority/target_date/attachment
```

Requester имеет Level 1 Write, поэтому может заполнить эти поля нового Document.

### Level 2

```text
status
```

Requester имеет Level 2 Read, но не Write, поэтому Status не является его writable intake field.

Technician/Supervisor имеют Level 2 Write.

## Server insert/save

`Document.insert()` выполняет:

```text
check_permission("create")
validate_higher_perm_levels()
```

`Document._save()` выполняет:

```text
check_permission("write")
validate_higher_perm_levels()
```

`validate_higher_perm_levels()` для high-permlevel fields без write access вызывает reset к original/default values.

Отсюда:

```text
Requester
→ Level0 Create
→ Level1 Write
→ Level2 Write No
→ new content accepted
→ status stays permitted default New
→ after insert Level0 Write No

Technician
→ Level0 Write
→ Level1 Write No
→ Level2 Write
→ document/state save possible
→ content change not ordinary permission authority
```

Explicit `ignore_permissions=True` bypasses этот слой.

## Почему status Level 2 лучше Level 0

Если `status` оставить Level 0, `Create=Yes` сам по себе не является field-level state restriction на insert до Workflow.

Перенос `status` на Level 2 даёт штатную field authority уже с L5:

```text
Requester → state read-only
Technician/Supervisor → state write
```

После L7 Workflow накладывает transition validation поверх Level 2.

---

# 5. Assign To / ToDo

- docs: https://docs.frappe.io/framework/assignments-and-todos
- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.json
- ToDo controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.py

`assign_to._add()` создаёт ToDo и проверяет access assignee. При недостаточном access возможен DocShare или Missing Permission.

```text
Assignment ≠ authorization
Assignment ≠ Level1/Level2 escalation
```

---

# 6. Workflow

- Workflow docs: https://docs.frappe.io/erpnext/workflows
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py
- client workflow: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/workflow.js
- Workflow source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition

`validate_workflow()` проверяет допустимость state transition.

`get_transitions()` учитывает current state, Allowed role и Condition.

Никакого требования `workflow_state_field.permlevel == 0` в exact engine нет.

Поэтому `status` может оставаться Level 2 при условии, что роли, выполняющие transitions, имеют Level 2 Write.

Client `is_read_only()` возвращает false для `doc.__islocal`; Workflow edit role не блокирует форму нового Document.

После L7:

```text
Level2 Write
+ valid Workflow transition
```

нужны для process-state change.

---

# 7. Kanban

- Kanban: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.py
- client set_value: https://github.com/frappe/frappe/blob/v16.32.0/frappe/client.py

Kanban update приходит к ordinary save и Workflow validation, но не является `apply_workflow(Action)` lifecycle.

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
- Notification controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.py
- Assignment Rule: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.py

Assignment Rule использует штатный Assign To.

Target Date = Level 1 input.

Rule не расширяет Level 1/2 permissions.

Close Condition Rule-owned ToDo — site policy, не universal Workflow behavior.

---

# 10. Auto Repeat

- docs: https://docs.frappe.io/erpnext/auto-repeat
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/auto_repeat
- `make_repeatable`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

Auto Repeat assignment не меняет Level 1/2 role authority.

---

# 11. Web Form

- docs: https://docs.frappe.io/framework/user/en/web-form
- settings: https://docs.frappe.io/framework/user/en/web-form/settings
- JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

## New insert

Exact:

```text
new target Document
→ doc.insert(ignore_permissions=True, ...)
```

Поэтому Web Form insert не доказывает Level 0/1/2 permissions.

`Status` не включается в Web Form fields; default `New` остаётся structural intake rule.

## Existing update

Разрешённый owner update может использовать:

```text
doc.save(ignore_permissions=True)
```

Поэтому final:

```text
Allow Editing After Submit = No
```

Это закрывает bypass update path поверх Level 1/2 authority.

`Apply Document Permissions` относится к existing-document behavior и не превращает new insert в ordinary Create.

`Login Required` = authentication boundary, не role-specific authorization.

---

# 12. Fixtures / customizations / install

- Hooks/fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- fixtures: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- customization sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/utils.py
- installer: https://github.com/frappe/frappe/blob/v16.32.0/frappe/installer.py
- source sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/sync.py

`install_app()` выполняет initial sync.

L11 exported `Custom DocPerm` должен содержать exact Level 0/1/2 rows.

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

# 15. Special fields / views

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
