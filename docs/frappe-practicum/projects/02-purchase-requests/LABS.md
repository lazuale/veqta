# P2. Заявки на закупку: лабораторные

P1 должен быть принят после проверки на чистом site. P2 создаёт новый app и не использует DocType или
данные реестра оборудования.

## P2.1. Создать app и site

Из корня Bench:

```bash
cd ~/frappe/frappe-practicum-bench
bench new-app purchase_requests
```

Использовать App Title `Purchase Requests`, описание `Training purchase request workflow`,
лицензию MIT и не создавать GitHub Workflow.

```bash
bench new-site purchase.localhost --db-root-username frappe_admin
bench --site purchase.localhost install-app purchase_requests
bench --site purchase.localhost set-config developer_mode 1
bench --site purchase.localhost clear-cache
bench --site purchase.localhost list-apps
```

Ожидаются `frappe` и `purchase_requests`. `equipment_register` на этот site не
устанавливать.

В `purchase_requests/hooks.py` добавить:

```python
add_to_apps_screen = [
	{
		"name": "purchase_requests",
		"title": "Purchase Requests",
		"route": "/desk/purchase-requests",
	}
]
```

Проверить Module `Purchase Requests` через `Module Def`.

### Состояние после P2.1

- существует независимый app и site;
- Developer Mode включён;
- используется Module, созданный Bench;
- `hooks.py` содержит запись Apps Page.

## P2.2. Создать роли и модель

Через `Role List` создать:

- `Purchase Requester`;
- `Department Approver`;
- `Procurement Officer`;
- `Purchase Auditor`.

Все DocType этого проекта создаются Standard в Module `Purchase Requests`.

### Purchase Department

Naming: `field:department_code`. Title Field: `department_name`.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Department Name | `department_name` | Data | Mandatory, Unique, In List View |
| Department Code | `department_code` | Data | Mandatory, Set Only Once |
| Disabled | `disabled` | Check | Default 0 |

### Purchase Request Item

Is Child Table: Yes.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Item Name | `item_name` | Data | Mandatory, In List View |
| Specification | `specification` | Small Text | без дополнительных флагов |
| Quantity | `quantity` | Float | Mandatory, Non Negative, Default 1, In List View |
| UOM | `uom` | Select | Mandatory; `pcs`, `set`, `license`, `month`; In List View |
| Comment | `comment` | Small Text | без дополнительных флагов |

### Purchase Request

- Is Submittable: Yes;
- Track Changes: Yes;
- Naming: `format:PR-{YYYY}-{#####}`;
- Title Field: `title`.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Title | `title` | Data | Mandatory, In List View |
| Department | `department` | Link | Mandatory, Options `Purchase Department`, In List View |
| Required By | `required_by` | Date | Mandatory, In List View |
| Priority | `priority` | Select | `Low`, `Normal`, `High`, `Urgent`; Default `Normal` |
| Justification | `justification` | Text | Mandatory |
| Items | `items` | Table | Mandatory, Options `Purchase Request Item` |
| Department Decision Note | `department_decision_note` | Small Text | Permission Level 1 |
| Procurement Note | `procurement_note` | Small Text | Permission Level 2 |
| Workflow State | `workflow_state` | Link | Options `Workflow State`, Read Only, In List View |
| Attachment | `attachment` | Attach | без дополнительных флагов |

Не создавать `requester`: инициатором остаётся системный `owner`.

### Permissions Standard DocType

В `Purchase Request` задать Level 0:

| Role | If Owner | Read | Write | Create | Submit | Cancel | Amend | Report |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Purchase Requester | Yes | Yes | Yes | Yes | No | No | No | Yes |
| Department Approver | No | Yes | Yes | No | No | No | No | Yes |
| Procurement Officer | No | Yes | Yes | No | Yes | Yes | Yes | Yes |
| Purchase Auditor | No | Yes | No | No | No | No | No | Yes |

Добавить отдельные DocPerm rows для уровней 1 и 2:

| Role | Level 1 | Level 2 |
|---|---|---|
| Purchase Requester | Read | нет доступа |
| Department Approver | Read/Write | Read |
| Procurement Officer | Read | Read/Write |
| Purchase Auditor | Read | Read |

Для `Purchase Department` Procurement Officer получает Read/Write/Create, остальные
роли — только Read.

### Source check

```bash
cd ~/frappe/frappe-practicum-bench/apps/purchase_requests
find purchase_requests -type f -path '*doctype*' | sort
git diff --stat
git diff
```

Проверить `is_submittable`, `workflow_state`, permission levels и permission rows в JSON.

## P2.3. Увидеть обычный lifecycle

До настройки Workflow Administrator должен увидеть базовую механику submittable
document.

Создать Departments:

| Code | Name |
|---|---|
| IT | Information Technology |
| OPS | Operations |

Создать Purchase Request:

| Поле | Значение |
|---|---|
| Title | Laptops for new employees |
| Department | IT |
| Required By | дата через 30 дней |
| Priority | Normal |
| Justification | Equipment for approved workplaces |
| Item | Business laptop, Quantity 2, UOM pcs |

Последовательно выполнить Save, Submit, Cancel и Amend. Записать изменения `docstatus`:

| Состояние | `docstatus` |
|---|---:|
| Draft | 0 |
| Submitted | 1 |
| Cancelled | 2 |
| Amended copy | 0 |

Удалить только незавершённую amended copy. Cancelled тестовый документ можно оставить как
учебное доказательство, но он не должен попасть в fixtures.

## P2.4. Создать пользователей и проверить базовые права

Создать System User:

| Email | Role |
|---|---|
| `requester.it@example.com` | Purchase Requester |
| `approver.it@example.com` | Department Approver |
| `procurement@example.com` | Procurement Officer |
| `purchase.auditor@example.com` | Purchase Auditor |

Для Requester и Approver создать User Permission:

- Allow: Purchase Department;
- For Value: IT;
- Applicable For: Purchase Request.

Под Requester создать Draft. Под Auditor проверить Read и запрет Write. Под Approver
проверить доступ к IT и отсутствие видимости заявки OPS. Под Procurement проверить
уровень 2. Assignment пока не использовать.

Права редактировать в Standard DocType. Role Permission Manager открыть для просмотра,
не сохранять через него Custom DocPerm.

### Состояние после P2.4

- четыре тестовых пользователя работают согласно базовой матрице;
- If Owner ограничивает Requester;
- User Permission ограничивает Department;
- Permission Level разделяет служебные заметки;
- Workflow ещё не включён.

## P2.5. Настроить Workflow

Через Awesomebar открыть `Workflow State List` и создать отсутствующие состояния:

- Draft;
- Pending Department Approval;
- Procurement Review;
- Rejected;
- Approved;
- Cancelled.

Через `Workflow Action Master List` создать действия:

- Submit Request;
- Approve Department;
- Reject;
- Resubmit;
- Approve Purchase;
- Return for Revision;
- Cancel.

Открыть `Workflow List`, создать `Purchase Request Approval`:

- Document Type: Purchase Request;
- Is Active: Yes;
- Workflow State Field: `workflow_state`;
- Don't Override Status: No.

States:

| State | DocStatus | Only Allow Edit For |
|---|---:|---|
| Draft | 0 | Purchase Requester |
| Pending Department Approval | 0 | Department Approver |
| Procurement Review | 0 | Procurement Officer |
| Rejected | 0 | Purchase Requester |
| Approved | 1 | Procurement Officer |
| Cancelled | 2 | Procurement Officer |

Transitions:

| Current | Action | Next | Allowed Role |
|---|---|---|---|
| Draft | Submit Request | Pending Department Approval | Purchase Requester |
| Pending Department Approval | Approve Department | Procurement Review | Department Approver |
| Pending Department Approval | Reject | Rejected | Department Approver |
| Rejected | Resubmit | Pending Department Approval | Purchase Requester |
| Procurement Review | Approve Purchase | Approved | Procurement Officer |
| Procurement Review | Return for Revision | Rejected | Procurement Officer |
| Approved | Cancel | Cancelled | Procurement Officer |

### Проверка маршрута

Создать новую заявку под `requester.it@example.com` и пройти:

```text
Draft
→ Pending Department Approval
→ Procurement Review
→ Approved / docstatus 1
→ Cancelled / docstatus 2
```

Отдельной заявкой проверить Reject и Resubmit. Под Requester убедиться, что нет действий
Approver и Procurement. Под Auditor убедиться, что Workflow Action отсутствуют.

Не менять `workflow_state` через прямую правку, Bulk Edit или Kanban.

## P2.6. Настроить совместную работу и представления

На заявке в Pending Department Approval выполнить Assign To для
`approver.it@example.com`. Проверить ToDo и Timeline. Затем снять assignment и убедиться,
что Workflow State не изменился.

Создать Notification с `Is Standard = Yes` и Module `Purchase Requests`:

- `Purchase Request Pending Approval` при переходе в Pending Department Approval;
- `Purchase Request Approved` при переходе в Approved.

Основной канал — System Notification. Без настроенного SMTP доставка email не входит в
приёмку.

Создать Calendar View `Purchase Requests by Required Date`:

- Reference DocType: Purchase Request;
- Subject Field: title;
- Start Date Field: required_by;
- End Date Field: required_by;
- All Day: Yes.

Создать:

- Standard Report Builder `Purchase Requests Overview`, Module app;
- Number Card `Requests Pending Approval`, Is Standard Yes, Module app;
- Dashboard Chart `Requests by Workflow State`, Is Standard Yes, Module app;
- Public Workspace `Purchase Requests`, Module app;
- Standard Print Format `Approved Purchase Request`, Module app.

Print Format должен показывать `name`, creation, Department, системного Owner,
Justification, Items, Workflow State. Выполнить Print и PDF под Procurement Officer и
Auditor с выданным Print permission.

Assignment Rule можно создать как временный опыт с локальным Approver. После опыта не
включать его в fixtures.

## P2.7. Экспортировать конфигурацию и проверить чистый site

В `hooks.py` добавить fixtures после `add_to_apps_screen`:

```python
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", [
			"Purchase Requester",
			"Department Approver",
			"Procurement Officer",
			"Purchase Auditor",
		]]],
	},
	{
		"dt": "Workflow State",
		"filters": [["name", "in", [
			"Draft",
			"Pending Department Approval",
			"Procurement Review",
			"Rejected",
			"Approved",
			"Cancelled",
		]]],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", [
			"Submit Request",
			"Approve Department",
			"Reject",
			"Resubmit",
			"Approve Purchase",
			"Return for Revision",
			"Cancel",
		]]],
	},
	{
		"dt": "Workflow",
		"filters": [["name", "=", "Purchase Request Approval"]],
	},
	{
		"dt": "Calendar View",
		"filters": [["name", "=", "Purchase Requests by Required Date"]],
	},
]
```

Экспортировать:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site purchase.localhost export-fixtures --app purchase_requests
bench --site purchase.localhost migrate

cd apps/purchase_requests
git status --short
git diff --check
git diff
```

Проверить отсутствие Users, User Permission, Assignment Rule, API keys, заявок и
вложений. Затем:

```bash
git add .
git commit -m "Build purchase request approval app"

cd ~/frappe/frappe-practicum-bench
bench new-site purchase-clean.localhost --db-root-username frappe_admin
bench --site purchase-clean.localhost install-app purchase_requests
bench --site purchase-clean.localhost migrate
bench --site purchase-clean.localhost clear-cache
```

На чистом site должны существовать DocType, роли, Workflow, Calendar View, Report, Number Card,
Chart, Workspace, Notifications и Print Format. Users, Departments и рабочие Request
создать заново. Выполнить P2 из [ACCEPTANCE.md](../../ACCEPTANCE.md).

Следующий проект: [P3 — лабораторные](../03-service-intake/LABS.md).
