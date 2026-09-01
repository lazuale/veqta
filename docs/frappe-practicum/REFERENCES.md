# Источники для проверки практикума

Этот файл не является учебником. Здесь собраны официальные материалы и exact-source файлы, по которым проверяются формулировки L0–L11 и Lab A–F.

Основная версия практикума — **Frappe Framework v16.32.0**.

## Правило источников

Приоритет:

1. фактический учебный стенд `v16.32.0`;
2. exact tag `v16.32.0`;
3. официальная документация Frappe;
4. `version-16` только для отслеживания будущих изменений.

Если текущая документация описывает более новую реализацию, она не заменяет exact-source курса.

---

# Версия и установка

- Release v16.32.0: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Tag v16.32.0: https://github.com/frappe/frappe/tree/v16.32.0
- Version 16 branch: https://github.com/frappe/frappe/tree/version-16
- Installation: https://docs.frappe.io/framework/user/en/installation

Exact source требований runtime:

- Python: https://github.com/frappe/frappe/blob/v16.32.0/pyproject.toml
- Node.js: https://github.com/frappe/frappe/blob/v16.32.0/package.json

В `v16.32.0`:

```text
Python >=3.14,<3.15
Node >=24
```

Учебный стенд фиксирует конкретные patch-версии внутри этих требований.

---

# Учебный стек L0

`projects/00-lab/SETUP_WSL2.md` использует:

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

Источники:

- WSL: https://learn.microsoft.com/windows/wsl/install
- Debian 13: https://www.debian.org/releases/trixie/
- MariaDB package in Trixie: https://packages.debian.org/trixie/mariadb-server
- NVM 0.40.3: https://github.com/nvm-sh/nvm/releases/tag/v0.40.3
- Node 24.20.0: https://nodejs.org/en/download/archive/v24.20.0
- Yarn 1.22.22: https://github.com/yarnpkg/yarn/releases/tag/v1.22.22
- uv 0.12.7: https://github.com/astral-sh/uv/releases/tag/0.12.7
- Python 3.14.7: https://www.python.org/downloads/release/python-3147/
- Bench 5.31.0: https://pypi.org/project/frappe-bench/5.31.0/

Точное сочетание — baseline курса, а не обещание использовать навсегда последние версии каждого компонента.

---

# App, site и Developer Mode

Документация:

- Apps: https://docs.frappe.io/framework/user/en/basics/apps
- Create an App: https://docs.frappe.io/framework/user/en/tutorial/create-an-app
- Create a Site: https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- Create a DocType / Developer Mode: https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype
- Apps Page: https://docs.frappe.io/framework/user/en/apps-page
- Hooks: https://docs.frappe.io/framework/user/en/python-api/hooks

Exact source для default branch `bench new-app`:

- https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/change_log.py

На Bench, созданном прямо на tag `v16.32.0`, репозиторий Frappe находится в detached HEAD, поэтому L0 явно задаёт branch `main` для учебного app.

---

# DocType, Naming и данные

Документация:

- DocType basics: https://docs.frappe.io/framework/user/en/basics/doctypes
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

Standard DocType, созданный в Developer Mode внутри app, экспортируется в source приложения. Временные Standard DocType лабораторий удаляются штатно, а не вычищаются вручную из БД.

`DocType Layout` существует в Frappe, но после аудита не считается покрытым базовым практикумом:

- https://docs.frappe.io/framework/doctypes/doctype-layout

---

# Data Import / Export

- Data Import source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- List View: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list

L3 использует скачанный из Frappe import template, 10 новых Equipment, отдельный отрицательный импорт, filters, Saved Filter, export и Bulk Edit.

---

# Пользователи и права

Документация:

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Data Masking: https://docs.frappe.io/framework/data-masking
- Permission Types: https://docs.frappe.io/framework/permission-types

Exact source:

- DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- Permissions: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- masking tests: https://github.com/frappe/frappe/blob/v16.32.0/frappe/tests/test_mask_fields.py

L5 реально проверяет:

```text
Read / Write / Create / Delete
Report / Export / Import
If Owner
Permission Level
User Permission
Share
```

Print permission проверяется в Lab E. Email permission и Custom Permission Types не считаются покрытыми базовым курсом.

Data Masking проверяется в Lab F и остаётся отдельным механизмом от Permission Level.

---

# Assign To и ToDo

Документация:

- Assignments and ToDos: https://docs.frappe.io/framework/assignments-and-todos

Exact source:

- Assign To: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/todo

`Assign To` создаёт обычный `ToDo`. Если в целевом DocType нет поля `assigned_to`, назначение не становится новым бизнес-полем документа.

В `facility_ops` такого поля нет.

---

# Kanban

Exact source:

- Kanban Board: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.py
- `frappe.set_value`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/__init__.py
- client `set_value`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/client.py
- Document validation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py

В `v16.32.0` перенос Kanban-карточки вызывает `frappe.set_value`. Он приходит к `frappe.client.set_value`, затем к `doc.save()`, поэтому обычная workflow validation выполняется.

Но это не тот же путь, что `apply_workflow`, поэтому после L7 Status-Kanban удаляется и основным интерфейсом переходов остаются Workflow Actions.

---

# Workflow и DocStatus

Документация:

- Workflow: https://docs.frappe.io/erpnext/workflows
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- Audit Trail: https://docs.frappe.io/framework/user/en/audit-trail

Exact source:

- Workflow: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Workflow Action: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action
- Workflow Action Master: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action_master
- Workflow Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition
- workflow validation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py

L7 использует существующее поле `Service Request.status` как Workflow State Field и не создаёт дублирующий `workflow_state`.

Lab B отдельно изучает DocStatus через временный Submittable DocType.

---

# Reports, Cards, Charts и Workspace

Документация:

- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Workspace Blocks: https://docs.frappe.io/framework/user/en/desk/workspace/blocks

Exact source:

- Report: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/report/report.json
- Number Card: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- Dashboard Chart: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart
- Workspace: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace

L8 реально использует один Report Builder, Group By + Count, три Number Card, один Dashboard Chart и один Workspace.

`Sum / Average` после аудита не считаются покрытыми.

---

# Notification и Assignment Rule

Документация:

- Notification: https://docs.frappe.io/framework/notifications

Exact source:

- Notification: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.json
- Assignment Rule JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.json
- Assignment Rule controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.py

Assignment Rule `v16.32.0` использует штатный Assign To mechanism, хранит `last_user` для Round Robin, умеет считать Load Balancing по открытым ToDo, синхронизировать Due Date и закрывать assignments по Condition.

Core L9 использует Round Robin. Load Balancing — самостоятельная проверка.

---

# Auto Repeat

Документация:

- Auto Repeat: https://docs.frappe.io/erpnext/auto-repeat

Exact source:

- Auto Repeat: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/auto_repeat
- DocType `make_repeatable`: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

При `Allow Auto Repeat` Frappe добавляет служебный `auto_repeat` Custom Field, поэтому Lab C проверяет и его очистку.

---

# Web Form

Документация:

- Web Form: https://docs.frappe.io/framework/user/en/web-form
- Settings: https://docs.frappe.io/framework/user/en/web-form/settings
- Customization: https://docs.frappe.io/framework/user/en/web-form/customization

Exact source:

- Web Form JSON: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- Web Form controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

Standard Web Form в Developer Mode экспортируется в Module приложения. Generated `.js/.py` не означают, что базовый курс написал собственную бизнес-логику.

Web Form Request/key internals в текущем практикуме не изучаются и отнесены к Later.

---

# Customize Form и Export Customizations

Документация:

- Customize Form: https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- Fixtures: раздел Fixtures в https://docs.frappe.io/framework/user/en/python-api/hooks

Exact source:

- Customize Form: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/customize_form
- Custom Field: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/custom_field
- Property Setter: https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/property_setter

Lab D показывает Custom Field + Property Setter поверх Standard `Equipment`.

`Custom DocType` и `DocType Layout` в Lab D не изучаются.

Важно: удаление Custom Field/Property Setter из exported customization JSON не гарантирует удаление уже синхронизированной записи на другом site. Lab D поэтому содержит явный rollback.

---

# Печать и PDF

Документация:

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Installation: https://docs.frappe.io/framework/user/en/installation

Exact source `v16.32.0`:

- Print Format: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- print utilities: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/print_utils.py
- PDF: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py
- Chrome PDF generator: https://github.com/frappe/frappe/tree/v16.32.0/frappe/utils/pdf_generator

В Print Format `v16.32.0` доступны:

```text
wkhtmltopdf
chrome
```

Default Print Format value — `wkhtmltopdf`, но Lab E **явно выбирает `chrome`**.

Exact `print_utils.py` умеет найти или автоматически скачать headless Chromium на bench. Поэтому L0 не блокируется отдельной установкой PDF-движка: первая реальная проверка PDF выполняется в Lab E на выбранном Chrome generator.

Официальная Installation page при этом продолжает перечислять `wkhtmltopdf 0.12.6` patched Qt для сценариев, использующих wkhtmltopdf. Это не противоречит Lab E: курс выбирает другой штатно поддерживаемый generator exact версии.

---

# Специальные Field Types Lab F

Exact source:

- Table MultiSelect: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/table_multiselect.js
- Barcode: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/barcode.js
- Duration: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/duration.js
- Signature: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/signature.js
- Geolocation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/geolocation.js
- Attachment Gallery: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/attachment_gallery.js
- masking tests: https://github.com/frappe/frappe/blob/v16.32.0/frappe/tests/test_mask_fields.py

Table MultiSelect использует Child Table, в которой должен существовать Link field.

Attachment Gallery показывает обычные `File`, прикреплённые к Document, а не создаёт отдельное файловое хранилище.

Signature — визуальная подпись Frappe, а не квалифицированная электронная подпись.

Geolocation хранит геоданные и отображает их штатной картой.

---

# Calendar и Gantt Lab F

Exact source:

- List view selector: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/list/list_view_select.js
- Calendar view: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/calendar/calendar.js
- Gantt view: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/gantt/gantt_view.js
- Event calendar config: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/event/event_calendar.js
- Event DocType: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/event/event.json

Для собственного DocType в `v16.32.0` одного metadata-флага недостаточно для полного штатного Calendar/Gantt сценария: интерфейс опирается на `frappe.views.calendar[doctype]`.

Поскольку собственный JavaScript не входит в base course, Lab F использует встроенный `Event`, для которого Frappe уже поставляет calendar mapping.

---

# Поставка и migrate

Документация:

- Fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

Exact source для миграции и fixtures проверяется в:

- https://github.com/frappe/frappe/tree/v16.32.0/frappe/migrate.py
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/modules

L11 разделяет:

```text
Standard source
app configuration
site-specific configuration
working data
```

В fixtures входят только универсальные Roles и Workflow configuration.

Не входят:

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
рабочие Location / Equipment / Service Request
ToDo / Files / Notification Log
```

---

# Правило обновления курса

При переходе на новый v16.x или новую major version:

1. не менять документацию курса автоматически;
2. сравнить новый release с `v16.32.0`;
3. проверить затронутые механизмы на отдельном стенде;
4. сначала исправить конкретные уроки;
5. затем синхронно обновить `ROADMAP.md`, `MATRIX.md`, `SCOPE.md`, `ARCHITECTURE.md` и этот файл;
6. только после этого менять baseline версии.

Матрица не должна обещать механизм, который ученик фактически не проходит руками.