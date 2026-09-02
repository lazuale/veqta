# Источники проверки

Практикум зафиксирован на **Frappe Framework v16.32.0**.

## Правило работы с источниками

1. Ссылка на tag `v16.32.0` доказывает поведение зафиксированной версии.
2. Ссылка на `version-16` или `develop` показывает последующее состояние и не заменяет exact tag.
3. Официальная документация объясняет публичную модель, но спорные permission и export paths дополнительно проверяются по исходникам.
4. ERPNext manual может описывать общий Frappe DocType, например Workflow, но ERPNext не становится зависимостью учебных app.

## Версия и среда

- Release: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Exact tag: https://github.com/frappe/frappe/tree/v16.32.0
- Installation: https://docs.frappe.io/framework/user/en/installation
- Python requirement: https://github.com/frappe/frappe/blob/v16.32.0/pyproject.toml
- Node requirement: https://github.com/frappe/frappe/blob/v16.32.0/package.json
- Migration notes v16: https://github.com/frappe/frappe/wiki/Migrating-to-version-16

Проверено в tag:

```text
Python >=3.14,<3.15
Node >=24
```

## Bench, app, Module и Desk

- Create an App: https://docs.frappe.io/framework/user/en/tutorial/create-an-app
- Create a Site: https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- Apps Page: https://docs.frappe.io/framework/user/en/apps-page
- Desk: https://docs.frappe.io/framework/user/en/desk
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Workspace source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace
- Module Def: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/module_def

Frappe v16 использует Apps Page, постоянный Workspace Sidebar и Workspace. Поэтому UI-проверка app не ограничивается существованием старой workspace page. Для custom app Apps Page настраивается через `add_to_apps_screen` в `hooks.py`.

## DocType и модель данных

- DocType: https://docs.frappe.io/framework/user/en/basics/doctypes
- Field Types: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- Naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- Child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Single DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype
- Tree View: https://docs.frappe.io/framework/user/en/api/tree
- DocType schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.json
- DocField schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docfield/docfield.json
- Document lifecycle: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- BaseDocument: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py
- Global Search: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/global_search.py

Серверная mandatory-проверка не требует истинного значения Check: значение `0`
допустимо. Поэтому явное согласие в P3 выражено обязательным Select без default. Global
Search индексирует child values только у полей, включённых в global search.

## Данные и стандартные views

- Desk views overview: https://docs.frappe.io/framework/user/en/desk
- List View: https://github.com/frappe/frappe/tree/v16.32.0/frappe/public/js/frappe/list
- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Data Import: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_import
- Data Export: https://github.com/frappe/frappe/tree/v16.32.0/frappe/core/doctype/data_export
- Kanban Board: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/kanban_board
- Calendar View schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/calendar_view/calendar_view.json
- Calendar View implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/calendar/calendar.js
- Number Card: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- Dashboard Chart: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart

Kanban меняет поле карточки как обычное значение. В проекте 2 он не используется как альтернативный путь Workflow Action. Calendar View и Kanban Board — записи site без собственного standard/module export path; необходимые общие представления поставляются fixtures.

## Пользователи и права

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Permission Types: https://docs.frappe.io/framework/permission-types
- DocPerm schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Custom DocPerm schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json
- Permission engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py
- Metadata permission helpers: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/meta.py
- Document permission enforcement: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py
- Client permission model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/perm.js

Практикум отдельно проверяет Role Permission, Permission Level, If Owner, User Permission и Share, потому что они ограничивают разные части доступа.

## Workflow и docstatus

- Workflow manual: https://docs.frappe.io/erpnext/user/manual/en/workflows
- Workflow engine: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/workflow.py
- Workflow controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/workflow/doctype/workflow/workflow.py
- Workflow schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/workflow/doctype/workflow/workflow.json
- Workflow State: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- Workflow Transition: https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition
- Client workflow model: https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/model/workflow.js

Workflow schema не имеет собственного `is_standard` или экспорта через Module, поэтому
проект 2 использует fixtures и отдельную проверку на чистом site.

## Assignment, ToDo и уведомления

- Assignments and ToDos: https://docs.frappe.io/framework/assignments-and-todos
- Assign To implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/assign_to.py
- ToDo: https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/todo
- Notification docs: https://docs.frappe.io/framework/notifications
- Notification source: https://github.com/frappe/frappe/tree/v16.32.0/frappe/email/doctype/notification
- Assignment Rule: https://github.com/frappe/frappe/tree/v16.32.0/frappe/automation/doctype/assignment_rule

Assignment Rule schema содержит конкретных Users и не имеет standard export flag. Поэтому rule с людьми текущего site классифицируется как local site configuration.

## Printing

- Printing: https://docs.frappe.io/framework/user/en/desk/printing
- Print Format schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/printing/doctype/print_format/print_format.json
- PDF implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/pdf.py

## Web Form

- Web Form: https://docs.frappe.io/framework/user/en/web-form
- Web Form Settings: https://docs.frappe.io/framework/user/en/web-form/settings
- Web Form Customization: https://docs.frappe.io/framework/user/en/web-form/customization
- Web Form schema: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json
- Web Form controller: https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.py

Exact source facts для архитектуры P3:

- unpublished form блокируется;
- `Login Required` блокирует Guest, но не задаёт role-specific authorization;
- при создании нового target document выполняется `doc.insert(ignore_permissions=True, ...)`;
- `allow_edit` отдельно проверяется для обновления существующего документа;
- `is_standard` и Module позволяют экспортировать Standard Web Form в app.

Поэтому внешняя форма направлена в отдельный `Service Intake`, а не во внутренний `Service Case`.

## REST API

- REST API: https://docs.frappe.io/framework/user/en/api/rest
- Authentication: https://docs.frappe.io/framework/user/en/api/rest#authentication
- Resource endpoints: https://docs.frappe.io/framework/user/en/api/rest#crud-operations

Практикум использует только автоматически созданный DocType API и отдельного пользователя с минимальными правами.

## Поставка app

- Hooks and fixtures: https://docs.frappe.io/framework/user/en/python-api/hooks
- Frappe commands: https://docs.frappe.io/framework/user/en/bench/frappe-commands
- Exporting Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- Fixtures implementation: https://github.com/frappe/frappe/blob/v16.32.0/frappe/utils/fixtures.py
- Module JSON export helpers: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/utils.py
- Standard file export: https://github.com/frappe/frappe/blob/v16.32.0/frappe/modules/export_file.py
- Installer: https://github.com/frappe/frappe/blob/v16.32.0/frappe/installer.py
- Model sync: https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/sync.py

Export Customizations синхронизирует custom fields, property setters и custom permissions целевого DocType. Документация прямо предупреждает, что при синхронизации существующие custom permissions заменяются содержимым exported customization.

## Возможности следующего уровня

- Controllers: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- Form Scripts: https://docs.frappe.io/framework/user/en/api/form
- Server Script: https://docs.frappe.io/framework/user/en/desk/scripting/server-script
- Hooks: https://docs.frappe.io/framework/user/en/python-api/hooks
- Unit Testing: https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing

Server Script с версии 15 отключён по умолчанию. Custom controller, permission hooks и tests относятся к следующему, программному уровню развития app и не скрываются внутри базового no-code маршрута.
