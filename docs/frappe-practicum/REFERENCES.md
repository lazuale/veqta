# Источники проверки практикума

Основная версия — **Frappe Framework v16.32.0**.

Этот файл — карта источников для проверки архитектуры, уроков и `INVARIANTS.md`.

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

Exact version требует:

```text
Python >=3.14,<3.15
Node >=24
```

Стек L0 зафиксирован в `projects/00-lab/SETUP_WSL2.md`.

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

`_assign` является штатным optional field Frappe, а не нашим бизнес-полем.

---

# 3. Data Import / Export / List

- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- List View source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list

L3 использует 10 дополнительных Equipment, отрицательный импорт, filters, Saved Filter, export и Bulk Edit.

---

# 4. Permissions и Permission Level

Документация:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- https://docs.frappe.io/framework/data-masking
- https://docs.frappe.io/framework/permission-types

Exact source:

- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- permissions engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- Permission Manager UI: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.js

Для `permlevel > 0` Permission Manager предоставляет прежде всего field-level `read/write/mask`; document-level operations рассматриваются на level 0.

В архитектуре курса Role Permission считается базовой server security boundary.

---

# 5. Assign To / ToDo — критическая граница

Документация:

- https://docs.frappe.io/framework/assignments-and-todos

Exact source:

- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.json
- ToDo permissions/query conditions: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/todo/todo.py

Из `assign_to._add()` следует:

```text
создаётся ToDo
↓
проверяется доступ assignee к reference document
↓
если доступа нет и sharing разрешён
→ frappe.share.add(...) создаёт Share

если sharing отключён
→ Missing Permission
```

Поэтому курс **не использует Assignment как authorization** и не оставляет основных Technician с несовместимыми Location User Permission.

`ToDo.update_in_reference()` обновляет штатное `_assign` reference document, но `_assign` не становится нашим доменным полем.

---

# 6. Workflow — server transition vs Desk editability

Документация:

- Workflow: https://docs.frappe.io/erpnext/workflows
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- Audit Trail: https://docs.frappe.io/framework/user/en/audit-trail

Exact source:

- Workflow controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/workflow/doctype/workflow/workflow.py
- Workflow engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py
- client workflow model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/workflow.js
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Workflow Action: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action
- Workflow Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition

## Что exact source подтверждает

`get_transitions()` проверяет:

```text
current state
transition.allowed ∈ user roles
Condition
```

`apply_workflow()` выбирает transition по Action, меняет state и сохраняет Document.

`validate_workflow()` при изменении state проверяет, что переход существует для текущего пользователя.

Client `frappe.workflow.is_read_only()` использует Workflow State `allow_edit` / `Only Allow Edit For`, чтобы управлять Desk editability.

Поэтому курс классифицирует:

```text
Allowed Role / Condition
= server transition enforcement

Only Allow Edit For
= state-dependent Desk guard
```

и **не выдаёт Only Allow Edit For за универсальную ACL любого update path**.

---

# 7. Kanban + Workflow

- Kanban Board: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.py
- `frappe.set_value`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/__init__.py
- client set_value: https://github.com/frappe/frappe/blob/v16.32.0/frappe/client.py

Kanban update приходит к обычному save, поэтому Workflow state validation не исчезает.

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

Assignment Rule exact source подтверждает:

```text
Round Robin
Load Balancing
Based on Field
Weighted Distribution
```

`do_assignment()` вызывает штатный `assign_to._add(...)`.

`Due Date Based On` передаёт значение field в ToDo `date`.

`update_due_date()` обновляет открытые Rule-owned ToDo при изменении configured field.

Close Condition закрывает ToDo только как поведение конкретного Assignment Rule.

Поэтому:

```text
Workflow Close
≠ универсально ToDo Close
```

На clean site L11 без Rule manual ToDo остаётся отдельным lifecycle.

---

# 10. Target Date / date-based Notification

Notification `Days After = 1` для reference date означает точку через один день после даты.

Курс поэтому использует точное имя:

```text
Service Request One Day Overdue
```

`Target Date` Optional, поэтому due/overdue behavior считается conditional invariant.

---

# 11. Auto Repeat

- docs: https://docs.frappe.io/erpnext/auto-repeat
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/auto_repeat
- `make_repeatable`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

`Allow Auto Repeat` создаёт служебный `auto_repeat` Custom Field; Lab C явно очищает его и возвращает L9 Assignment Rule.

---

# 12. Web Form — критическая security граница

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
если data.name и allow_edit = false
→ update отклоняется
```

Если owner/web-form permission разрешает write при `Apply Document Permissions = No`, update выполняется через:

```text
doc.save(ignore_permissions=True)
```

Поэтому финальная архитектура L10:

```text
Allow Editing After Submit = No
```

`Allow Edit` изучается временно, но не остаётся parallel editor рабочего Workflow document.

## Link options

`get_link_options()` при:

```text
login_required = true
allow_read_on_all_link_options = false
```

по умолчанию добавляет:

```text
owner = current user
```

При `Allow Read On All Link Options = Yes` общий каталог Link options возвращается без owner-фильтра через `frappe.get_all`.

Поэтому курс явно фиксирует threat model:

```text
Website User = trusted internal reporter
```

а публичный untrusted external catalog оставляет Later.

---

# 13. Fixtures / customizations / install

- Hooks/fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- fixture implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- customization sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/utils.py
- installer: https://github.com/frappe/frappe/blob/v16.32.0/frappe/installer.py
- standard source sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/sync.py
- import flags: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/import_file.py

`install_app()` exact source выполняет:

```text
sync_for(app)
sync_fixtures(app)
sync_customizations(app)
sync_dashboards(app)
```

Поэтому L11 не трактует `migrate` как обязательную вторую половину первоначальной установки.

Standard source import выполняется с import flags, включая `ignore_links`, что позволяет app source и fixtures синхронизироваться в штатном install flow.

---

# 14. Customize Form

- Customize Form: https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/customize_form
- Custom Field: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/custom_field
- Property Setter: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/property_setter

Lab D не учит ложной модели «удалил строку из exported JSON — migrate гарантированно удалит старую кастомизацию другого site».

---

# 15. Printing / PDF

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Print Format: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- PDF: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py
- PDF generators: https://github.com/frappe/frappe/tree/v16.32.0/frappe/utils/pdf_generator
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

Собственный Calendar/Gantt mapping требует JS configuration и остаётся Later.

---

# 17. Что намеренно Later

Критичные усиления, которые не притворяемся no-code возможностями:

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

Именно поэтому `INVARIANTS.md` различает hard guarantees и UI/site policies.
