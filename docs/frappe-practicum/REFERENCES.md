# Источники для проверки практикума

Этот файл — карта официальных источников для L0–L11 и Lab A–F, а не отдельный учебник.

Основная версия — **Frappe Framework v16.32.0**.

## Приоритет

1. фактический стенд `v16.32.0`;
2. exact tag `v16.32.0`;
3. официальная документация Frappe;
4. `version-16` только для отслеживания изменений.

Если current docs описывают более новую реализацию, для курса приоритетнее exact source.

---

# Версия и установка

- Release: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Tag: https://github.com/frappe/frappe/tree/v16.32.0
- Version 16 branch: https://github.com/frappe/frappe/tree/version-16
- Installation: https://docs.frappe.io/framework/user/en/installation
- Python requirements: https://github.com/frappe/frappe/blob/v16.32.0/pyproject.toml
- Node requirements: https://github.com/frappe/frappe/blob/v16.32.0/package.json

Exact `v16.32.0` требует:

```text
Python >=3.14,<3.15
Node >=24
```

Стек L0:

```text
Debian 13 / Trixie
MariaDB 11.8.x
NVM 0.40.3
Node 24.20.0 LTS
Yarn Classic 1.22.22
uv 0.12.7
Python 3.14.7
Frappe Bench 5.31.0
Frappe Framework v16.32.0
```

Дополнительные источники:

- WSL: https://learn.microsoft.com/windows/wsl/install
- Debian 13: https://www.debian.org/releases/trixie/
- MariaDB in Trixie: https://packages.debian.org/trixie/mariadb-server
- NVM 0.40.3: https://github.com/nvm-sh/nvm/releases/tag/v0.40.3
- Node 24.20.0: https://nodejs.org/en/download/archive/v24.20.0
- Yarn 1.22.22: https://github.com/yarnpkg/yarn/releases/tag/v1.22.22
- uv 0.12.7: https://github.com/astral-sh/uv/releases/tag/0.12.7
- Python 3.14.7: https://www.python.org/downloads/release/python-3147/
- Bench 5.31.0: https://pypi.org/project/frappe-bench/5.31.0/

---

# App, Site, Developer Mode

- Apps: https://docs.frappe.io/framework/user/en/basics/apps
- Create an App: https://docs.frappe.io/framework/user/en/tutorial/create-an-app
- Create a Site: https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- Create a DocType / Developer Mode: https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype
- Apps Page: https://docs.frappe.io/framework/user/en/apps-page
- Hooks: https://docs.frappe.io/framework/user/en/python-api/hooks
- branch detection: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/change_log.py

На Bench, созданном непосредственно на tag, Frappe находится в detached HEAD, поэтому L0 явно задаёт `main` для нового учебного app.

---

# DocType и Documents

Документация:

- DocType: https://docs.frappe.io/framework/user/en/basics/doctypes
- Field Types: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- Child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Single DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype
- Naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- Allow on Submit: https://docs.frappe.io/framework/doctypes/allow-on-submit

Exact source:

- DocType JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.json
- DocType controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py
- Document lifecycle: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- DocField: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docfield/docfield.json
- deletion: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/delete_doc.py

`DocType Layout` существует, но текущим практикумом не покрывается:

- https://docs.frappe.io/framework/doctypes/doctype-layout

---

# Data Import / Export / List

- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- List View source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list

L3 реально использует штатный import template, 10 новых Equipment, отрицательный импорт, filters, Saved Filter, export и Bulk Edit.

---

# Permissions

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Data Masking: https://docs.frappe.io/framework/data-masking
- Permission Types: https://docs.frappe.io/framework/permission-types
- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- permissions.py: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- masking tests: https://github.com/frappe/frappe/blob/v16.32.0/frappe/tests/test_mask_fields.py

L5 проверяет Read / Write / Create / Delete, Report / Export / Import, If Owner, Permission Level, User Permission и Share.

Print permission проверяется в Lab E. Email permission и Custom Permission Types — Later.

---

# Assign To / ToDo

- docs: https://docs.frappe.io/framework/assignments-and-todos
- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/todo

`Assign To` создаёт ToDo. В `facility_ops` нет отдельного поля исполнителя.

---

# Kanban и Workflow

Kanban:

- https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.py
- `frappe.set_value`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/__init__.py
- client `set_value`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/client.py

Workflow:

- docs: https://docs.frappe.io/erpnext/workflows
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- Audit Trail: https://docs.frappe.io/framework/user/en/audit-trail
- Workflow: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Workflow Action: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action
- Action Master: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action_master
- Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition
- validation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py

Kanban `v16.32.0` приходит через `frappe.set_value` к `doc.save()`, поэтому workflow validation выполняется. Но это не `apply_workflow`, поэтому после L7 Status-Kanban не используется как интерфейс процесса.

---

# Reports / Cards / Charts / Workspace

- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Workspace Blocks: https://docs.frappe.io/framework/user/en/desk/workspace/blocks
- Report JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/report/report.json
- Number Card: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- Dashboard Chart: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart
- Workspace: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace

L8 реально создаёт один Report Builder, Group By + Count, три Number Card, один Chart и один Workspace. `Sum / Average` не считаются покрытыми.

---

# Notification / Assignment Rule

- Notification docs: https://docs.frappe.io/framework/notifications
- Notification JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.json
- Notification controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.py
- Assignment Rule JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.json
- Assignment Rule controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.py

Для `Days After = 1` exact source ищет Documents с reference date = вчера. Это соответствует L9.

Core L9 использует Round Robin. Load Balancing — самостоятельная практика.

---

# Auto Repeat

- docs: https://docs.frappe.io/erpnext/auto-repeat
- source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/auto_repeat
- `make_repeatable`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

При `Allow Auto Repeat` Frappe создаёт служебный `auto_repeat` Custom Field; Lab C поэтому явно очищает его.

---

# Web Form

- Web Form: https://docs.frappe.io/framework/user/en/web-form
- Settings: https://docs.frappe.io/framework/user/en/web-form/settings
- Customization: https://docs.frappe.io/framework/user/en/web-form/customization
- JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

Standard Web Form в Developer Mode входит в source приложения. Web Form Request/key internals — Later.

---

# Customize Form / Export Customizations

- Customize Form: https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- Fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Customize Form source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/customize_form
- Custom Field: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/custom_field
- Property Setter: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/property_setter

Lab D работает поверх Standard Equipment. Custom DocType и DocType Layout не считаются покрытыми.

Удаление строки из exported customization JSON не гарантирует удаления уже синхронизированной кастомизации на другом site.

---

# Печать и PDF

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Installation: https://docs.frappe.io/framework/user/en/installation
- Print Format JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- Print utilities: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/print_utils.py
- PDF: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py
- PDF generators: https://github.com/frappe/frappe/tree/v16.32.0/frappe/utils/pdf_generator
- built-in pdf hook: https://github.com/frappe/frappe/blob/v16.32.0/frappe/hooks.py
- `setup-chrome` command: https://github.com/frappe/frappe/blob/v16.32.0/frappe/commands/utils.py

Print Format `v16.32.0` поддерживает:

```text
wkhtmltopdf
chrome
```

Default поля — wkhtmltopdf. Lab E явно выбирает `chrome`.

Frappe имеет штатную команду:

```bash
bench setup-chrome
```

и `find_or_download_chromium_executable()`, который скачивает headless Chromium на bench при отсутствии executable.

Официальная Installation page продолжает перечислять `wkhtmltopdf 0.12.6` patched Qt для wkhtmltopdf-сценария. Это не противоречит Lab E: лаборатория выбирает другой штатно поддерживаемый generator exact версии.

---

# Специальные Field Types

- Table MultiSelect: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/table_multiselect.js
- Barcode: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/barcode.js
- Duration: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/duration.js
- Signature: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/signature.js
- Geolocation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/geolocation.js
- Attachment Gallery: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/attachment_gallery.js

Table MultiSelect использует Child Table с Link field.

Attachment Gallery показывает обычные File текущего Document.

Signature — визуальное поле Frappe, а не квалифицированная электронная подпись.

Geolocation работает с GeoJSON.

---

# Calendar / Gantt

- List view selector: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/list/list_view_select.js
- Calendar: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/calendar/calendar.js
- Gantt: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/gantt/gantt_view.js
- Event calendar config: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/event/event_calendar.js
- Event: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/event/event.json

Для собственного DocType в `v16.32.0` Calendar/Gantt опираются на `frappe.views.calendar[doctype]`. Собственный JS не входит в base course, поэтому Lab F использует встроенный Event.

---

# Fixtures и migrate

- Fixtures source: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- Migrate: https://github.com/frappe/frappe/blob/v16.32.0/frappe/migrate.py
- Modules: https://github.com/frappe/frappe/tree/v16.32.0/frappe/modules

Exact fixtures source подтверждает `fixture_auto_order`.

L11 разделяет:

```text
Standard source
app configuration
site-specific configuration
working data
```

В универсальные fixtures входят Roles и Workflow configuration.

Не входят Users, User Permission, Share, Assignment Rule с конкретными Users и рабочие Documents.

---

# Обновление baseline

При переходе на другой release:

1. сравнить release с `v16.32.0`;
2. проверить затронутые механизмы на отдельном стенде;
3. исправить конкретные уроки;
4. синхронно обновить `ROADMAP.md`, `MATRIX.md`, `SCOPE.md`, `ARCHITECTURE.md` и этот файл;
5. только после этого менять baseline курса.

Матрица не должна обещать механизм, который ученик фактически не проходит руками.