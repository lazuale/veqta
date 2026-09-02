# P3. Внешняя приёмная: лабораторные

P2 должен быть принят после проверки на чистом site. P3 создаёт внешний канал, но остаётся независимым
app без ERPNext, Helpdesk и других business app.

Повторяющиеся команды создания app/site здесь уже служат checklist. Перед выполнением
ученик должен уметь объяснить, зачем нужны отдельный app, отдельный site, Developer Mode
и Module, не возвращаясь к пошаговому объяснению P1.

## P3.1. Создать app, site и роли

```bash
cd ~/frappe/frappe-practicum-bench
bench new-app service_intake
```

Использовать App Title `Service Intake`, описание `Training public intake and internal
case management`, лицензию MIT и не создавать GitHub Workflow.

```bash
bench new-site intake.localhost --db-root-username frappe_admin
bench --site intake.localhost install-app service_intake
bench --site intake.localhost set-config developer_mode 1
bench --site intake.localhost clear-cache
bench --site intake.localhost list-apps
```

Ожидаются только `frappe` и `service_intake`.

В `service_intake/hooks.py` добавить:

```python
add_to_apps_screen = [
	{
		"name": "service_intake",
		"title": "Service Intake",
		"route": "/desk/service-intake",
	}
]
```

Через `Role List` создать:

- `Service Triage`;
- `Service Agent`;
- `Service Manager`;
- `Service API Reader`.

### Состояние после P3.1

- app установлен на отдельный site;
- Developer Mode включён;
- Module `Service Intake` существует;
- созданы четыре роли без Users.

## P3.2. Создать модель и границу доверия

Все три DocType — Standard, Module `Service Intake`.

### Service Category

- Naming: `field:category_name`;
- Title Field: `category_name`.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Category Name | `category_name` | Data | Mandatory, Set Only Once |
| Description | `description` | Small Text | без дополнительных флагов |
| Disabled | `disabled` | Check | Default 0 |

### Service Intake

- Track Changes: Yes;
- Naming: `format:INT-{YYYY}-{#####}`;
- Title Field: `subject`.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Reporter Name | `reporter_name` | Data | Mandatory |
| Reporter Email | `reporter_email` | Data | Mandatory, Options `Email` |
| Topic | `topic` | Select | Mandatory; `Access`, `Equipment`, `Data issue`, `Other` |
| Subject | `subject` | Data | Mandatory, In List View |
| Description | `description` | Text | Mandatory |
| Contact Consent | `contact_consent` | Select | Mandatory; одна option `I consent to be contacted`; без Default |
| Triage Status | `triage_status` | Select | `New`, `Accepted`, `Rejected`; Default `New` |
| Internal Notes | `internal_notes` | Small Text | Permission Level 1 |

`Contact Consent` семантически является булевым согласием. В обычной модели для такого
факта естественнее поле Check. Здесь Select с одной непустой option используется
осознанно как no-code компромисс: основной маршрут запрещает собственную серверную
validation logic, а обязательность Check сама по себе не выражает правило «значение
обязательно должно быть true». Не переносить этот приём на все булевы поля. Если в
реальном приложении допустим код и нужно юридически или бизнесово гарантировать явное
согласие, использовать семантически подходящее поле и проверять требование на серверной
стороне.

`triage_status` не отмечать Read Only. Его не будет во внешней форме, но сотрудник должен
менять значение в Desk.

### Service Case

- Track Changes: Yes;
- Naming: `format:CASE-{YYYY}-{#####}`;
- Title Field: `case_title`.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Case Title | `case_title` | Data | Mandatory, In List View |
| Source Intake | `source_intake` | Link | Mandatory, Unique, Set Only Once, Options `Service Intake` |
| Case Description | `case_description` | Text | Mandatory |
| Category | `category` | Link | Mandatory, Options `Service Category` |
| Priority | `priority` | Select | `Low`, `Normal`, `High`, `Urgent`; Default `Normal` |
| Status | `status` | Select | `Open`, `In Progress`, `Resolved`, `Closed`; Read Only |
| Resolution | `resolution` | Text | без дополнительных флагов |

`Unique` у `source_intake` запрещает два Case для одного Intake. `Set Only Once`
запрещает перепривязать уже созданный Case к другому Intake и тем самым сохраняет
происхождение документа без отдельного controller.

### Permissions

Задать в Standard DocType:

| DocType | Triage | Agent | Manager | API Reader |
|---|---|---|---|---|
| Service Intake | Read/Write | нет доступа | Read/Write | нет доступа |
| Service Case | Read/Create | Read/Write | Read/Write/Create | нет доступа |
| Service Category | Read | Read | Read/Write/Create | Read |

Delete не выдавать. Для Internal Notes создать Level 1 rows с Read/Write только Triage и
Manager. API Reader не получает доступ к Intake и Case.

### Source check

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
find service_intake -type f -path '*doctype*' | sort
git diff --stat
git diff
```

Проверить поля, permission level и permission rows в JSON.

## P3.3. Настроить внутренний Workflow

Создать недостающие Workflow State `Open`, `In Progress`, `Resolved`, `Closed`.

Создать Workflow Action Master `Start Work`, `Resolve`, `Close`, `Reopen`.

Создать Workflow `Service Case Workflow`:

- Document Type: Service Case;
- Is Active: Yes;
- Workflow State Field: `status`.

States:

| State | DocStatus | Only Allow Edit For |
|---|---:|---|
| Open | 0 | Service Agent |
| In Progress | 0 | Service Agent |
| Resolved | 0 | Service Manager |
| Closed | 0 | Service Manager |

Transitions:

| Current | Action | Next | Role | Condition |
|---|---|---|---|---|
| Open | Start Work | In Progress | Service Agent | пусто |
| In Progress | Resolve | Resolved | Service Agent | `doc.resolution` |
| Resolved | Close | Closed | Service Manager | пусто |
| Resolved | Reopen | In Progress | Service Manager | пусто |

Все states имеют `docstatus = 0`: закрытие обращения не требует Submit/Cancel.

## P3.4. Создать публичную Web Form

Создать Categories:

| Category Name | Description |
|---|---|
| Access | Account and access issues |
| Equipment | Equipment issues |
| Data | Data quality issues |
| Other | Other accepted cases |

Через Awesomebar открыть `Web Form List`, создать `Report a Service Issue`:

| Setting | Значение |
|---|---|
| DocType | Service Intake |
| Module | Service Intake |
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

Добавить в форму только поля:

```text
reporter_name
reporter_email
topic
subject
description
contact_consent
```

Не добавлять `triage_status`, `internal_notes`, Case, assignee, workflow state и Link на
Service Category.

Открыть приватное окно браузера:

```text
http://intake.localhost:8000/report-service-issue
```

Первая попытка: оставить Contact Consent пустым. Отправка должна быть заблокирована.

Отправить две записи:

| Поле | Первая запись | Вторая запись |
|---|---|---|
| Reporter Name | Alice Example | Bob Example |
| Reporter Email | alice@example.com | bob@example.com |
| Topic | Access | Other |
| Subject | Cannot sign in | Test message |
| Description | Login is rejected after password entry | Message to reject during triage |
| Contact Consent | I consent to be contacted | I consent to be contacted |

### Проверка границы Guest

- в Desk созданы два `Service Intake` со статусом New;
- Guest не видит Desk и список Intake;
- Guest не может изменить отправленную запись;
- `triage_status` и `internal_notes` не принимались формой;
- `Service Case` автоматически не создан.

Временно включить Login Required, создать Website User и повторить отправку. После
сравнения вернуть Login Required = No. Allow Multiple для финальной Guest-form не
настраивать: эта опция относится к идентифицированным ответам пользователя.

## P3.5. Выполнить триаж и внутреннюю работу

Создать System User:

| Email | Role |
|---|---|
| `triage@example.com` | Service Triage |
| `agent@example.com` | Service Agent |
| `service.manager@example.com` | Service Manager |

Под Triage открыть обращение Alice:

- Triage Status: Accepted;
- создать Service Case;
- Source Intake: принятое обращение;
- Case Title: Cannot sign in;
- вручную перенести только проверенное содержание в Case Description;
- Category: Access по таблице Topic → Category;
- Priority: Normal.

Ручное копирование позволяет убрать персональные или ненужные данные. Если продукту
понадобится точная копия, следующим уровнем можно применить Fetch From, но это будет
другое правило данных.

Обращение Bob отметить Rejected и записать причину в Internal Notes. Попытаться создать
второй Case с тем же Source Intake: Unique должен заблокировать сохранение.

Назначить Case пользователю `agent@example.com`. Под Agent проверить:

- Case доступен;
- исходный Intake недоступен;
- `source_intake` нельзя заменить на другой Intake после создания Case;
- Start Work переводит Case в In Progress;
- Resolve без Resolution запрещён condition;
- после заполнения Resolution переход работает.

Под Manager закрыть Case. На отдельном Case проверить Reopen.

Создать:

- Notification `New Service Intake`, Is Standard Yes, Module app;
- Standard Report Builder `New Intakes`, Module app;
- Standard Report Builder `Open Service Cases`, Module app;
- Number Card `Untriaged Intakes`, Is Standard Yes, Module app;
- Dashboard Chart `Cases by Status`, Is Standard Yes, Module app;
- Public Workspace `Service Intake Control`, Module app.

Отчёты по Intake и Case держать раздельно: внешнее сообщение ещё не является принятым
внутренним кейсом.

## P3.6. Проверить стандартный REST API

Создать System User `api.service@example.com` только с ролью `Service API Reader`.
Сгенерировать API Key и API Secret в User. Secret показывается один раз.

В терминале запросить значения без записи в shell history:

```bash
read -r -p "API key: " PRACTICUM_API_KEY
read -r -s -p "API secret: " PRACTICUM_API_SECRET
echo
```

Разрешённый запрос:

```bash
curl -sS \
  -H "Authorization: token ${PRACTICUM_API_KEY}:${PRACTICUM_API_SECRET}" \
  -H "Accept: application/json" \
  "http://intake.localhost:8000/api/resource/Service%20Category"
```

Запрещённый запрос:

```bash
curl -i -sS \
  -H "Authorization: token ${PRACTICUM_API_KEY}:${PRACTICUM_API_SECRET}" \
  -H "Accept: application/json" \
  "http://intake.localhost:8000/api/resource/Service%20Intake"
```

Первый запрос возвращает категории. Второй должен вернуть ошибку доступа. После опыта:

```bash
unset PRACTICUM_API_KEY PRACTICUM_API_SECRET
```

Не помещать значения в Markdown, screenshots, `hooks.py`, app `.env` или Git.

## P3.7. Экспортировать app и проверить чистый site

В `hooks.py` добавить fixtures:

```python
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", [
			"Service Triage",
			"Service Agent",
			"Service Manager",
			"Service API Reader",
		]]],
	},
	{
		"dt": "Workflow State",
		"filters": [["name", "in", [
			"Open",
			"In Progress",
			"Resolved",
			"Closed",
		]]],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["name", "in", [
			"Start Work",
			"Resolve",
			"Close",
			"Reopen",
		]]],
	},
	{
		"dt": "Workflow",
		"filters": [["name", "=", "Service Case Workflow"]],
	},
]
```

Экспортировать и проверить:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site intake.localhost export-fixtures --app service_intake
bench --site intake.localhost migrate

cd apps/service_intake
git status --short
git diff --check
git diff
```

В diff не должно быть Users, API credentials, SMTP, Intake, Case и File. Затем:

```bash
git add .
git commit -m "Build service intake boundary app"

cd ~/frappe/frappe-practicum-bench
bench new-site intake-clean.localhost --db-root-username frappe_admin
bench --site intake-clean.localhost install-app service_intake
bench --site intake-clean.localhost migrate
bench --site intake-clean.localhost clear-cache
```

На чистом site должны существовать DocType, роли, Workflow, Web Form, Notifications,
Reports, Card, Chart и Workspace. Users, Categories и рабочие обращения создать заново.
Повторить Guest submission, ручной triage и P3 из [ACCEPTANCE.md](../../ACCEPTANCE.md).

P3 принят только после этой проверки. На этом Metadata & Configuration level завершён.
Не переделывать P3 задним числом под Python: его ручная конвертация остаётся доказанной
границей декларативного решения.

Следующий шаг — [Engineering Bridge](../../engineering/LABS.md). Финальный аудит из
[ROADMAP.md](../../ROADMAP.md) выполняется после Engineering Bridge.
