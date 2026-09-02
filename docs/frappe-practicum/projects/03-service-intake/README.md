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
bench new-site intake.localhost --db-root-username frappe_admin
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
| Category Name | `category_name` | Data | Mandatory, Set Only Once |
| Description | `description` | Small Text | Optional |
| Disabled | `disabled` | Check | Default 0 |

Naming: `field:category_name`.

### `Service Intake`

Standard DocType, Track Changes включён.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Reporter Name | `reporter_name` | Data | Mandatory |
| Reporter Email | `reporter_email` | Data | Mandatory, Options: Email |
| Topic | `topic` | Select | Mandatory; `Access`, `Equipment`, `Data issue`, `Other`; публичный список без Link |
| Subject | `subject` | Data | Mandatory, In List View |
| Description | `description` | Text | Mandatory |
| Contact Consent | `contact_consent` | Select | Mandatory; единственная option `I consent to be contacted`; без default |
| Triage Status | `triage_status` | Select | `New`, `Accepted`, `Rejected`; Default `New`; не Read Only в DocType |
| Internal Notes | `internal_notes` | Small Text | Permission Level 1 |

Naming: `format:INT-{YYYY}-{#####}`. Title Field: `subject`.

Публичная версия не принимает Attachment. Добавление upload меняет abuse, storage и privacy model и должно проходить отдельную security-проверку.

Значение `reporter_email` — сообщённый гостем контакт, а не подтверждённая личность. Оно не используется для авторизации или автоматической выдачи доступа.

`Contact Consent` семантически является булевым согласием, но обязательность Check сама
по себе не гарантирует значение true. Поэтому в no-code маршруте используется обязательный
Select без default. Это осознанный компромисс практикума, а не универсальный паттерн для
булевых полей; при наличии собственной business logic явное согласие следует проверять
на серверной стороне.

Публичная и внутренняя классификации связаны явным правилом:

| Public Topic | Service Category |
|---|---|
| Access | Access |
| Equipment | Equipment |
| Data issue | Data |
| Other | Other |

Triage выбирает внутреннюю Category по этой таблице. Автоматического преобразования нет.

### `Service Case`

Standard DocType, Track Changes включён.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Case Title | `case_title` | Data | Mandatory, In List View |
| Source Intake | `source_intake` | Link | Mandatory, Unique, Set Only Once, Options: Service Intake |
| Case Description | `case_description` | Text | Mandatory; проверенное содержание для внутренней работы |
| Category | `category` | Link | Mandatory, Options: Service Category |
| Priority | `priority` | Select | `Low`, `Normal`, `High`, `Urgent` |
| Status | `status` | Select | `Open`, `In Progress`, `Resolved`, `Closed`; Read Only после включения Workflow |
| Resolution | `resolution` | Text | Optional, Mandatory by process before Resolve |

Naming: `format:CASE-{YYYY}-{#####}`. Title Field: `case_title`.

`Unique` на `source_intake` выражает правило «одно принятое внешнее обращение — не более
одного внутреннего Case». `Set Only Once` защищает происхождение уже созданного Case:
Agent или другой пользователь с Write не может перепривязать его к другому Intake.

## 4. Роли и внутренний процесс

Создать:

- `Service Triage`;
- `Service Agent`;
- `Service Manager`;
- `Service API Reader`.

| DocType | Triage | Agent | Manager |
|---|---|---|---|
| Service Intake | Read/Write, no Create/Delete | No access | Read/Write, no Create/Delete |
| Service Case | Read/Create | Read/Write | Read/Write/Create, no Delete |
| Service Category | Read | Read | Manage |

`Service API Reader` получает только Read на `Service Category`. API user не получает
доступ к Intake или Case.

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
Сам `triage_status` не делается Read Only в DocType: иначе сотрудник Triage не сможет его
изменить. Внешний запрет обеспечивается отсутствием поля в Web Form.

## 6. Проверить границу Web Form

Открыть route в приватном окне браузера и отправить две записи.

Проверить:

1. Guest submission создаёт `Service Intake`.
2. Guest не получает Desk access.
3. После отправки нельзя открыть список всех Intake.
4. Отправленный Intake нельзя редактировать или удалить через Web Form.
5. В запросе нельзя штатно задать поля, отсутствующие в списке полей Web Form.
6. `Service Case` не создаётся автоматически.

Затем временно включить `Login Required`, создать Website User и повторить отправку.
Зафиксировать различие аутентификации, после чего вернуть финальную публичную форму в
режим Guest.

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

После сохранения Case попытаться под Agent заменить `source_intake` на другой Intake.
Изменение должно быть заблокировано `Set Only Once`; иначе трассируемость источника не
считается доказанной.

Автоматической кнопки «Преобразовать» нет. Она потребовала бы custom Client/Python logic.
В Metadata & Configuration level ручной шаг является честной границей возможностей
декларативной конфигурации.

Agent работает с `case_description` и не получает Read на исходный Intake с контактными данными. Link на источник сохраняет трассируемость для Triage/Manager, но не используется как способ расширить доступ Agent.

## 8. Внутренняя работа и контроль

Назначить Accepted Case конкретному Agent через Assign To. Проверить ToDo и отсутствие повышения прав.

Создать:

- Notification `New Service Intake` для Triage;
- Report `New Intakes`;
- Report `Open Service Cases`;
- Number Card `Untriaged Intakes`;
- Dashboard Chart `Cases by Status`;
- Workspace `Service Intake Control`.

Отчётность по Intake и Case разделена: количество внешних сообщений не равно количеству принятых кейсов.

## 9. Стандартный REST API

Создать отдельного System User `api.service@example.com` и выдать только роль
`Service API Reader`. Не использовать Administrator token.

Сгенерировать API Key/Secret в User и выполнить два запроса по официальному REST API:

- разрешённый Read `Service Category`;
- запрещённый Read `Service Intake` без выданного права.

Authorization header имеет форму:

```text
Authorization: token <api_key>:<api_secret>
```

Secret хранится только на время опыта. Не помещать его в Markdown, `hooks.py`, `.env` внутри app, screenshots, shell history или Git. Custom API method не создаётся.

## 10. Поставка и чистый site

Standard Web Form и Notification должны экспортироваться в app при Developer Mode и `Is Standard`.

Number Card и Dashboard Chart сохраняются с `Is Standard = Yes` и Module app. Workspace
должен быть Public и принадлежать Module app. В `hooks.py` добавляется
`add_to_apps_screen` для навигации Frappe v16.

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
bench new-site intake-clean.localhost --db-root-username frappe_admin
bench --site intake-clean.localhost install-app service_intake
bench --site intake-clean.localhost migrate
bench --site intake-clean.localhost clear-cache
```

На чистом site проверить маршрут `/report-service-issue`, отправку Guest, отсутствие
списка и редактирования, ручной триаж и создание Case. API user создаётся заново: его
учётные данные не входят в app.

## 11. Готовность проекта

Выполнить P3 из [ACCEPTANCE.md](../../ACCEPTANCE.md) и объяснить:

- почему внешний Intake и внутренний Case — разные DocType;
- почему `source_intake` нельзя менять после создания Case;
- почему Login Required не равен role authorization;
- почему `Apply Document Permissions` не превращает new Web Form insert в обычный Desk Create;
- почему закрытые Link options не публикуются;
- почему автоматическое преобразование не вошло в Metadata Track без программной ответственности;
- почему API keys относятся к site secrets, а не к app source.

После принятого P3 базовый Metadata & Configuration level завершён. Его не нужно
ретроспективно переделывать под Python.

Следующий шаг — [Engineering Bridge](../../engineering/LABS.md). Там тот же
`service_intake` получает новое требование и показывает, когда Controller, transaction,
patch и tests становятся нативным продолжением приложения.

Финальный аудит [ROADMAP.md](../../ROADMAP.md) выполняется после Engineering Bridge.

Пошаговое выполнение P3: [LABS.md](LABS.md).
