# Источники для проверки практикумов

Этот файл не является учебником. Здесь собраны официальные материалы, по которым проверяются формулировки и шаги курса.

Основная версия практикумов: **Frappe Framework v16.32.0**.

## Версия, установка и исходники

- Release v16.32.0: https://github.com/frappe/frappe/releases/tag/v16.32.0
- Tag v16.32.0: https://github.com/frappe/frappe/tree/v16.32.0
- Ветка для отслеживания будущих v16.x: https://github.com/frappe/frappe/tree/version-16
- Installation: https://docs.frappe.io/framework/user/en/installation

При расхождении между текущей веткой и установленным стендом базового курса приоритет имеет tag `v16.32.0` и фактическое поведение стенда.

Официальная установка перечисляет `wkhtmltopdf 0.12.6` с patched Qt как зависимость для PDF. В программе PDF впервые требуется в P5, поэтому P0 не блокируется отсутствием PDF-зависимости. Перед P5 способ установки и работоспособность PDF отдельно проверяются на фактическом учебном стенде.

## App, site и Developer Mode

- Apps: https://docs.frappe.io/framework/user/en/basics/apps
- Create an App: https://docs.frappe.io/framework/user/en/tutorial/create-an-app
- Create a Site / install app: https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- Developer Mode / создание DocType: https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype
- Apps Page: https://docs.frappe.io/framework/user/en/apps-page
- Hooks: https://docs.frappe.io/framework/user/en/python-api/hooks

Официальный Create an App показывает модуль, создаваемый `bench new-app`, как `Default Module bootstrapped with app`; отдельно создавать первый Module после `new-app` не требуется.

## DocType и данные

- DocType basics: https://docs.frappe.io/framework/user/en/basics/doctypes
- Field Types: https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- Child DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- Single DocType: https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype
- Naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- DocType Layout: https://docs.frappe.io/framework/doctypes/doctype-layout
- Allow on Submit: https://docs.frappe.io/framework/doctypes/allow-on-submit

Ключевые исходники DocType v16.32.0:

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
- Data Masking: https://docs.frappe.io/framework/data-masking
- Custom Permission Types v16: https://docs.frappe.io/framework/permission-types
- `DocPerm` v16.32.0: https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docperm/docperm.json
- Permission constants and automatic roles: https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py

Для курса набор permission-флагов сверяется прежде всего с `DocPerm` тега v16.32.0. В нём есть:

- Select;
- Read;
- Write;
- Create;
- Delete;
- Submit;
- Cancel;
- Amend;
- Mask;
- Report;
- Export;
- Import;
- Share;
- Print;
- Email.

В `frappe/permissions.py` тега v16.32.0 `Guest`, `All`, `Desk User` и `Administrator` входят в `AUTOMATIC_ROLES`, поэтому именно так они рассматриваются в P3.

На момент проверки страница Users and Permissions всё ещё перечисляет `Set User Permissions` как permission-флаг, однако в `DocPerm` v16.32.0 такого поля нет. Поэтому курс не выдаёт его за отдельную галку Role Permission Manager. User Permission при этом остаётся отдельным обязательным механизмом ограничения данных.

Data Masking присутствует в v16.32.0 через поле `Mask`, но официальная документация помечает саму функцию как экспериментальную, поэтому она остаётся дополнительным упражнением.

Custom Permission Types требуют проверки нового permission type в собственном коде. Они относятся к следующему уровню курса.

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