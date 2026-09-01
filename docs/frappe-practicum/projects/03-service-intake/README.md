# Проект 3. Внешняя приёмная

## Результат

App `service_intake` безопасно принимает сообщения через Web Form, хранит их в отдельной очереди триажа и позволяет сотруднику создать внутренний `Service Case`. Внешний пользователь не получает доступ к внутренней модели процесса.

## 1. Сценарий и граница доверия

```text
Guest / Website User
→ Web Form
→ Service Intake
→ ручная проверка Triage
→ Service Case
→ Agent
→ Manager
```

Внешний ввод считается недоверенным. Web Form не должна принимать:

- `triage_status`;
- internal notes;
- category из закрытого Link-справочника;
- assignee;
- workflow state;
- ссылку на внутренний Case.

## 2. Создать app и site

```bash
bench new-app service_intake
bench new-site intake.localhost
bench --site intake.localhost install-app service_intake
bench --site intake.localhost set-config developer_mode 1
bench --site intake.localhost clear-cache
bench --site intake.localhost list-apps
```

Не устанавливать P1/P2. Внешняя приёмная должна доказать свою модель самостоятельно.

## 3. Внутренняя модель

### `Service Category`

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Category Name | `category_name` | Data | Mandatory, Unique |
| Description | `description` | Small Text | Optional |
| Disabled | `disabled` | Check | Default 0 |

Naming: `field:category_name`.

### `Service Intake`

Standard DocType, Track Changes включён.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Reporter Name | `reporter_name` | Data | Mandatory |
| Reporter Email | `reporter_email` | Data | Mandatory, Options: Email |
| Topic | `topic` | Select | Mandatory; короткий публичный список без Link |
| Subject | `subject` | Data | Mandatory, In List View |
| Description | `description` | Text | Mandatory |
| Contact Consent | `contact_consent` | Check | Mandatory |
| Triage Status | `triage_status` | Select | `New`, `Accepted`, `Rejected`; Default `New`, Read Only для внешней формы |
| Internal Notes | `internal_notes` | Small Text | Permission Level 1 |

Naming: `format:INT-{YYYY}-{#####}`. Title Field: `subject`.

Публичная версия не принимает Attachment. Добавление upload меняет abuse, storage и privacy model и должно проходить отдельную security-проверку.

Значение `reporter_email` — сообщённый гостем контакт, а не подтверждённая личность. Оно не используется для авторизации или автоматической выдачи доступа.

### `Service Case`

Standard DocType, Track Changes включён.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Case Title | `case_title` | Data | Mandatory, In List View |
| Source Intake | `source_intake` | Link | Mandatory, Unique, Options: Service Intake |
| Case Description | `case_description` | Text | Mandatory; проверенное содержание для внутренней работы |
| Category | `category` | Link | Mandatory, Options: Service Category |
| Priority | `priority` | Select | `Low`, `Normal`, `High`, `Urgent` |
| Status | `status` | Select | `Open`, `In Progress`, `Resolved`, `Closed`; Read Only после включения Workflow |
| Resolution | `resolution` | Text | Optional, Mandatory by process before Resolve |

Naming: `format:CASE-{YYYY}-{#####}`. Title Field: `case_title`.

Unique на `source_intake` выражает правило «одно принятое внешнее обращение — не более одного внутреннего Case» без custom controller.

## 4. Роли и внутренний процесс

Создать:

- `Service Triage`;
- `Service Agent`;
- `Service Manager`.

| DocType | Triage | Agent | Manager |
|---|---|---|---|
| Service Intake | Read/Write/Create, no Delete | No access | Read/Write, no Delete |
| Service Case | Read/Create | Read/Write | Read/Write/Create, no Delete |
| Service Category | Read | Read | Manage |

Level 1 Internal Notes читают/меняют только Triage и Manager. Website User и Guest не получают Desk role.

Для `Service Case` настроить Workflow:

```text
Open --Start Work/Agent--> In Progress
In Progress --Resolve/Agent, condition `doc.resolution`--> Resolved
Resolved --Close/Manager--> Closed
Resolved --Reopen/Manager--> In Progress
```

Все states остаются `docstatus = 0`: здесь закрытие кейса — состояние работы, а не бухгалтерская фиксация submittable document.

## 5. Standard Web Form

Создать Web Form `Report a Service Issue`:

| Setting | Финальное значение |
|---|---|
| DocType | Service Intake |
| Module | модуль app |
| Is Standard | Yes |
| Published | Yes |
| Route | `report-service-issue` |
| Login Required | No |
| Anonymous | No |
| Allow Multiple | Yes |
| Allow Editing After Submit | No |
| Allow Delete | No |
| Show List | No |
| Apply Document Permissions | No |
| Allow Read On All Link Options | No |

Поля формы — только:

```text
reporter_name
reporter_email
topic
subject
description
contact_consent
```

`triage_status` получает default `New` из DocType. `internal_notes` отсутствует в form allow-list.

## 6. Доказать Web Form boundary

Открыть route в приватном окне браузера и отправить две записи.

Проверить:

1. Guest submission создаёт `Service Intake`.
2. Guest не получает Desk access.
3. После отправки нельзя открыть список всех Intake.
4. Отправленный Intake нельзя редактировать или удалить через Web Form.
5. В запросе нельзя штатно задать поля, отсутствующие в Web Form fields.
6. `Service Case` не создаётся автоматически.

Затем временно включить `Login Required`, создать Website User и повторить отправку. Зафиксировать различие authentication boundary, после чего вернуть принятую финальную настройку Guest form.

Критическая модель `v16.32.0`:

```text
Web Form new document
→ target insert(ignore_permissions=True)
```

Поэтому успешный submit не доказывает Role Permission Create на `Service Intake`. Безопасность достигается отдельным target DocType и узким списком полей.

## 7. Ручной триаж

Под `Service Triage`:

- первое обращение отметить `Accepted`;
- создать `Service Case`, связав его через `source_intake` и вручную перенеся проверенное содержание в `case_description`;
- второе обращение отметить `Rejected` и записать причину в Internal Notes;
- попытаться создать второй Case по тому же Intake и получить Unique violation.

Автоматической кнопки «Преобразовать» нет. Она потребовала бы custom Client/Python logic. В базовом app ручной шаг является честной границей возможностей конфигурации.

Agent работает с `case_description` и не получает Read на исходный Intake с контактными данными. Link на источник сохраняет трассируемость для Triage/Manager, но не используется как способ расширить доступ Agent.

## 8. Внутренняя работа и контроль

Назначить Accepted Case конкретному Agent через Assign To. Проверить ToDo и отсутствие повышения прав.

Создать:

- Notification `New Service Intake` для Triage;
- Notification `Service Case Assigned` или системное назначение;
- Report `New Intakes`;
- Report `Open Service Cases`;
- Number Card `Untriaged Intakes`;
- Dashboard Chart `Cases by Status`;
- Workspace `Service Intake Control`.

Отчётность по Intake и Case разделена: количество внешних сообщений не равно количеству принятых кейсов.

## 9. Стандартный REST API

Создать отдельного System User `api.service@example.com` и роль с минимальным Read/Create только на заранее выбранный DocType. Не использовать Administrator token.

Сгенерировать API Key/Secret в User и выполнить два запроса по официальному REST API:

- разрешённый запрос к выбранному DocType;
- запрещённый запрос к внутреннему DocType без Read.

Authorization header имеет форму:

```text
Authorization: token <api_key>:<api_secret>
```

Secret хранится только на время опыта. Не помещать его в Markdown, `hooks.py`, `.env` внутри app, screenshots, shell history или Git. Custom API method не создаётся.

## 10. Поставка и clean site

Standard Web Form и Notification должны экспортироваться в app при Developer Mode и `Is Standard`.

Workflow и Roles экспортируются узкими fixtures по точным именам. В фильтры также входят используемые `Workflow State` и `Workflow Action Master`. Users, Website Users, API credentials, Assignment Rule с конкретными Users, SMTP и рабочие Intake/Case не экспортируются.

```bash
bench --site intake.localhost export-fixtures --app service_intake
bench --site intake.localhost migrate

cd apps/service_intake
git status --short
git diff --check
git diff
git add .
git commit -m "Build service intake boundary app"

cd ../..
bench new-site intake-clean.localhost
bench --site intake-clean.localhost install-app service_intake
bench --site intake-clean.localhost migrate
bench --site intake-clean.localhost clear-cache
```

На clean site проверить route `/report-service-issue`, Guest submission, отсутствие list/edit, ручной triage и создание Case. API user создаётся заново: credentials не должны приезжать с app.

## 11. Готовность проекта

Выполнить P3 из [ACCEPTANCE.md](../../ACCEPTANCE.md) и объяснить:

- почему внешний Intake и внутренний Case — разные DocType;
- почему Login Required не равен role authorization;
- почему `Apply Document Permissions` не превращает new Web Form insert в обычный Desk Create;
- почему закрытые Link options не публикуются;
- почему автоматическое преобразование осталось за границей no-code core;
- почему API keys относятся к site secrets, а не к app source.

После этого выполнить финальный аудит из [ROADMAP.md](../../ROADMAP.md).
