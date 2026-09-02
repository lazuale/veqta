# Проект 2. Заявки на закупку

## Результат

App `purchase_requests` ведёт внутренние заявки со строками позиций, многошаговым согласованием, ответственными, уведомлениями, печатью и отчётностью. Approved заявка становится submitted document, а не просто записью со словом «Одобрено».

## 1. Сценарий продукта

```text
инициатор создаёт заявку
→ руководитель подразделения согласует или возвращает
→ закупщик проверяет и утверждает
→ утверждённая заявка фиксируется
→ при необходимости закупщик отменяет её штатным Cancel
```

Не входят: поставщики, заказы поставщикам, склад, платежи, налоги и бухгалтерские проводки.

## 2. Создать независимый app

Из общего bench:

```bash
bench new-app purchase_requests
bench new-site purchase.localhost
bench --site purchase.localhost install-app purchase_requests
bench --site purchase.localhost set-config developer_mode 1
bench --site purchase.localhost clear-cache
bench --site purchase.localhost list-apps
```

P1 не устанавливать на этот site. Совпадение общих понятий не создаёт зависимости между app.

## 3. Модель данных

```text
Purchase Department ◄──── Purchase Request
                               │
                               └──── Purchase Request Item (Child)
```

### `Purchase Department`

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Department Name | `department_name` | Data | Mandatory, Unique, In List View |
| Department Code | `department_code` | Data | Mandatory, Set Only Once |
| Disabled | `disabled` | Check | Default 0 |

Naming: `field:department_code`. Title Field: `department_name`.

### `Purchase Request Item`

Child DocType.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Item Name | `item_name` | Data | Mandatory, In List View |
| Specification | `specification` | Small Text | Optional |
| Quantity | `quantity` | Float | Mandatory, Default 1, In List View |
| UOM | `uom` | Select | Mandatory; `pcs`, `set`, `license`, `month`; In List View |
| Comment | `comment` | Small Text | Optional |

Стоимость и автоматический итог не добавляются: без отдельной расчётной логики приложение не должно обещать финансовую точность.

### `Purchase Request`

Standard DocType, `Is Submittable = Yes`, Track Changes включён.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Title | `title` | Data | Mandatory, In List View |
| Department | `department` | Link | Mandatory, Options: Purchase Department, In List View |
| Required By | `required_by` | Date | Mandatory, In List View |
| Priority | `priority` | Select | `Low`, `Normal`, `High`, `Urgent`; Default `Normal` |
| Justification | `justification` | Text | Mandatory |
| Items | `items` | Table | Mandatory, Options: Purchase Request Item |
| Department Decision Note | `department_decision_note` | Small Text | Permission Level 1 |
| Procurement Note | `procurement_note` | Small Text | Permission Level 2 |
| Workflow State | `workflow_state` | Link | Options: Workflow State, Read Only, In List View |
| Attachment | `attachment` | Attach | Optional |

Naming: `format:PR-{YYYY}-{#####}`. Title Field: `title`.

Инициатор заявки — системное поле `owner`. Отдельный изменяемый Link `requester` не создаётся: без server-side validation пользователь мог бы указать в нём другого человека, а интерфейс создавал бы ложное ощущение гарантии.

Перед Workflow вручную проверить обычный lifecycle submittable document на тестовой записи: Draft → Submit → Cancel → Amend. После этого удалить тестовую запись или явно оставить её как учебную.

Начальные `Purchase Department` загрузить через Data Import. Purchase Request импортировать только как отдельный контролируемый опыт: импорт не должен использоваться для обхода Workflow или создания фиктивно Approved документов.

## 4. Роли и базовые права

Создать:

- `Purchase Requester`;
- `Department Approver`;
- `Procurement Officer`;
- `Purchase Auditor`.

Финальная базовая матрица `Purchase Request`:

| Роль | Read | Write | Create | Submit | Cancel | Amend | Report |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Requester | own | own | Yes | No* | No | No | own |
| Department Approver | Yes | Yes | No | No* | No | No | Yes |
| Procurement Officer | Yes | Yes | No | Yes | Yes | Yes | Yes |
| Auditor | Yes | No | No | No | No | No | Yes |

`*` Финальная подача выполняется Workflow Action. Не считать колонку Submit единственным условием перехода: одновременно действуют Role Permission, Workflow state/transition и `docstatus` следующего состояния.

Permission Level:

| Роль | Level 0 | Level 1 | Level 2 |
|---|---|---|---|
| Requester | Read/Write own | Read | no access |
| Department Approver | Read/Write | Read/Write | Read |
| Procurement Officer | Read/Write | Read | Read/Write |
| Auditor | Read | Read | Read |

Эта схема нужна не ради трёх уровней. Она выражает реальную границу: заметка руководителя и внутренняя заметка закупщика имеют разных авторов.

Создать по одному System User на роль. User Permission на Department применить к Requester и Department Approver, затем проверить видимость заявок другого подразделения.

## 5. Workflow

Создать Workflow `Purchase Request Approval` для `Purchase Request`, state field `workflow_state`.

### States

| State | DocStatus | Only Allow Edit For |
|---|---:|---|
| Draft | 0 | Purchase Requester |
| Pending Department Approval | 0 | Department Approver |
| Procurement Review | 0 | Procurement Officer |
| Rejected | 0 | Purchase Requester |
| Approved | 1 | Procurement Officer |
| Cancelled | 2 | Procurement Officer |

### Transitions

| Current | Action | Next | Allowed Role |
|---|---|---|---|
| Draft | Submit Request | Pending Department Approval | Purchase Requester |
| Pending Department Approval | Approve Department | Procurement Review | Department Approver |
| Pending Department Approval | Reject | Rejected | Department Approver |
| Rejected | Resubmit | Pending Department Approval | Purchase Requester |
| Procurement Review | Approve Purchase | Approved | Procurement Officer |
| Procurement Review | Return for Revision | Rejected | Procurement Officer |
| Approved | Cancel | Cancelled | Procurement Officer |

Проверить каждый переход целевой ролью и минимум три запрета:

- Requester не видит/не выполняет `Approve Department`;
- Department Approver не выполняет `Approve Purchase`;
- Auditor не меняет state.

Не создавать Kanban по `workflow_state` для перемещения карточек. Workflow state меняется Workflow Action, иначе интерфейс предлагает неверную модель процесса.

## 6. Assignment и совместная работа

На `Pending Department Approval` вручную назначить документ конкретному Approver через Assign To.

Проверить:

- создан ToDo с reference на Purchase Request;
- Due Date соответствует принятой политике;
- Comment виден в Timeline;
- снятие assignment не меняет Workflow State;
- назначение пользователя без базового доступа не превращает его автоматически в Approver.

Создать Notification:

- `Purchase Request Pending Approval` — при входе в `Pending Department Approval`;
- `Purchase Request Approved` — при входе в `Approved`.

Использовать System Notification как основной воспроизводимый канал. Email проверять только при настроенном исходящем аккаунте site.

Assignment Rule допустимо настроить как опыт на рабочем site. Если rule содержит конкретных Users, он относится к local site configuration и не включается в универсальный app без отдельной стратегии параметризации.

## 7. Представление результата

Создать:

- Calendar View по `required_by`;
- Standard Report Builder report `Purchase Requests Overview`;
- Number Card `Requests Pending Approval`;
- Dashboard Chart `Requests by Workflow State`;
- Workspace `Purchase Requests`;
- Standard Print Format `Approved Purchase Request`.

Calendar View — переносимая конфигурация продукта, поэтому он входит в fixtures по
точному имени. Number Card и Dashboard Chart сохраняются с `Is Standard = Yes` и Module
app. Workspace должен быть Public и принадлежать Module app. Для Apps Page в `hooks.py`
добавляется `add_to_apps_screen`.

Print Format должен показывать номер, дату, подразделение, системного Owner как инициатора, justification, items и состояние. PDF проверить под Procurement Officer и Auditor, если их Print permission различается — под каждой ролью.

## 8. Поставка Workflow и ролей

Standard DocType, standard Report, Workspace, Notification и Print Format должны
находиться в исходниках app.

Workflow и Role — конфигурационные записи. Зафиксировать их как fixtures с узкими
фильтрами по точным именам. Вместе с Workflow включить используемые `Workflow State` и
`Workflow Action Master`, иначе чистый site получит ссылки на отсутствующие записи. Не
экспортировать все роли, состояния, действия или Workflow site.

После настройки fixtures:

```bash
bench --site purchase.localhost export-fixtures --app purchase_requests
bench --site purchase.localhost migrate
```

Проверить fixture JSON вручную: в нём нет Users, email, паролей, API keys, Assignment Rule с локальными людьми и рабочих Purchase Request.

Финальные permissions собственных Standard DocType настроить в таблице Permissions
самого DocType. Они должны находиться в JSON DocType. Не создавать Custom DocPerm и не
использовать Export Customizations для DocType этого app.

## 9. Git и чистый site

```bash
cd apps/purchase_requests
git status --short
git diff --check
git diff
git add .
git commit -m "Build purchase request approval app"

cd ../..
bench new-site purchase-clean.localhost
bench --site purchase-clean.localhost install-app purchase_requests
bench --site purchase-clean.localhost migrate
bench --site purchase-clean.localhost clear-cache
```

На чистом site заново создать тестовых Users и Departments. Затем пройти:

```text
Draft
→ Pending Department Approval
→ Procurement Review
→ Approved / docstatus 1
→ Cancelled / docstatus 2
```

Не принимать проект, если Workflow пришлось собрать вручную после `install-app`.

## 10. Готовность проекта

Выполнить P2 из [ACCEPTANCE.md](../../ACCEPTANCE.md) и объяснить:

- чем `docstatus` отличается от текста в поле состояния;
- почему Workflow не заменяет Role Permission;
- почему Assign To не делает пользователя согласующим;
- зачем Decision Note и Procurement Note имеют разные Permission Level;
- почему fixtures фильтруются по точным именам;
- почему рабочие заявки не входят в поставку app.

Дальше: [проект 3 — «Внешняя приёмная»](../03-service-intake/README.md).

Пошаговое выполнение: [LABS.md](LABS.md).
