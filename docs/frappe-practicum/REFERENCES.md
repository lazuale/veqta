# Источники для проверки практикумов

Этот файл не является учебником. Здесь собраны официальные материалы, по которым проверяются формулировки и шаги курса.

Основная версия практикумов: **Frappe Framework v16.32.0**.

## Версия и исходники

- Release v16.32.0: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Tag v16.32.0: https://github.com/frappe/frappe/tree/v16.32.0
- Ветка для отслеживания будущих v16.x: https://github.com/frappe/frappe/tree/version-16

При расхождении между текущей веткой и установленным стендом базового курса приоритет имеет tag `v16.32.0` и фактическое поведение стенда.

## App, site и Developer Mode

- Apps: https://docs.frappe.io/framework/user/en/basics/apps
- Create an App: https://docs.frappe.io/framework/user/en/tutorial/create-an-app
- Create a Site / install app: https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- Developer Mode / создание DocType: https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype
- Apps Page: https://docs.frappe.io/framework/user/en/apps-page
- Hooks: https://docs.frappe.io/framework/user/en/python-api/hooks

## DocType и данные

- DocType basics: https://docs.frappe.io/framework/user/en/basics/doctypes
- Field Types: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- Child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Single DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype
- Naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- DocType Layout: https://docs.frappe.io/framework/doctypes/doctype-layout
- Allow on Submit: https://docs.frappe.io/framework/doctypes/allow-on-submit

Ключевой исходник DocType v16.32.0:

- https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.json
- https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py

## Customize Form и переносимость

- Customize Form: https://docs.frappe.io/framework/user/en/basics/doctypes/customize
- Export Customizations: https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- Fixtures: раздел `Fixtures` в https://docs.frappe.io/framework/user/en/python-api/hooks

Ключевые исходники:

- https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/customize_form
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/custom_field
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/custom/doctype/property_setter

## Пользователи и права

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Permission Types v16: https://docs.frappe.io/framework/permission-types

Базовая программа изучает штатные permission flags. Custom Permission Types требуют программной проверки прав в коде и поэтому остаются за пределами обязательного уровня.

## Assignment и ToDo

- Assignments and ToDos: https://docs.frappe.io/framework/assignments-and-todos

Исходники:

- https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/form/assign_to.py
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/todo

## Workflow и жизненный цикл

- Workflow: https://docs.frappe.io/erpnext/workflows
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- Audit Trail: https://docs.frappe.io/framework/user/en/audit-trail

Workflow находится в самом Frappe Framework; страницы ERPNext используются здесь как официальное пользовательское описание механизма.

Исходники v16.32.0:

- https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_state
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_action_master
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/workflow/doctype/workflow_transition

## Reports, Workspace и печать

- Report Builder: https://docs.frappe.io/framework/user/en/desk/reports/report-builder
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Workspace Blocks: https://docs.frappe.io/framework/user/en/desk/workspace/blocks
- Printing: https://docs.frappe.io/framework/user/en/desk/printing

Исходники:

- https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/report/report.json
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/workspace
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/number_card
- https://github.com/frappe/frappe/tree/v16.32.0/frappe/desk/doctype/dashboard_chart

## Автоматизация

- Notification: https://docs.frappe.io/framework/notifications
- Auto Repeat: https://docs.frappe.io/erpnext/auto-repeat

Исходники v16.32.0:

- Assignment Rule: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/assignment_rule/assignment_rule.json
- Auto Repeat: https://github.com/frappe/frappe/blob/v16.32.0/frappe/automation/doctype/auto_repeat/auto_repeat.json
- Notification: https://github.com/frappe/frappe/blob/v16.32.0/frappe/email/doctype/notification/notification.json

Страницы Auto Repeat в ERPNext docs используются как официальное пользовательское описание. Сам механизм находится в Frappe Framework.

## Web Form

- Web Form: https://docs.frappe.io/framework/user/en/web-form
- Web Form Settings: https://docs.frappe.io/framework/user/en/web-form/settings
- Web Form Customization: https://docs.frappe.io/framework/user/en/web-form/customization

Исходник v16.32.0:

- https://github.com/frappe/frappe/blob/v16.32.0/frappe/website/doctype/web_form/web_form.json

Официальная документация Web Form отдельно подтверждает Standard Web Form: в Developer Mode он создаёт файлы внутри Module приложения и поставляется вместе с app.

## Правило обновления курса

При выходе нового v16.x:

1. не менять курс автоматически;
2. сравнить новый release с v16.32.0;
3. проверить затронутые механизмы на отдельном стенде;
4. обновить `REFERENCES.md`, `MATRIX.md` и соответствующий практикум;
5. только после этого менять базовую проверенную версию курса.