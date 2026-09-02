# Engineering Track: нативный программный слой Frappe

Перед началом P3 должен быть принят на рабочем и чистом site.

```text
App:    service_intake
Site:   intake.localhost
Frappe: v16.32.0
```

Здесь впервые появляется собственный Python. Перед каждой правкой сначала назвать
ответственность, которой не хватило в metadata.

---

# E1. Creation invariant в Controller

## Требование

В P3 `Service Case.source_intake` уже имеет:

```text
Mandatory
Unique
Set Only Once
Link → Service Intake
```

Но metadata не выражает правило:

> `Service Case` можно создать только из `Service Intake` со статусом `Accepted`.

Это правило **создания**, а не любого последующего save. Agent после создания Case должен
работать с ним без Read на исходный Intake.

Поэтому owner — `before_insert`, а не общий `validate()`.

## Исходное состояние

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git status --short
git log --oneline -1
```

Working tree должен быть чистым после P3.

Открыть:

```text
service_intake/service_intake/doctype/service_case/service_case.py
```

и привести controller к виду:

```python
import frappe
from frappe.model.document import Document


class ServiceCase(Document):
	def before_insert(self):
		if not self.source_intake:
			return

		intake = frappe.get_doc("Service Intake", self.source_intake)
		intake.check_permission("read")

		if intake.triage_status != "Accepted":
			frappe.throw("Service Case can only be created from an accepted Service Intake.")
```

`before_insert` действует для server-side Document insert независимо от того, пришёл он
из Desk, REST или другого Python-кода.

`intake.check_permission("read")` нужен только на create path: пользователь, который
создаёт Case из Intake, должен иметь право видеть источник.

## Проверка

Под `Service Triage`:

1. создать Intake со статусом `New`;
2. попытаться создать связанный Case — получить ошибку;
3. изменить Intake на `Accepted`;
4. создать Case — сохранение проходит;
5. назначить Case `agent@example.com`;
6. под Agent изменить разрешённое поле Case и сохранить.

Последний шаг доказывает, что creation invariant не превратился в скрытое требование
выдать Agent Read на Intake.

После проверки удалить созданный Case.

## Граница

```text
Link
→ source существует

Unique
→ один Case на Intake

Set Only Once
→ source нельзя перепривязать

before_insert
→ при создании source обязан быть Accepted
```

Первые три гарантии не переписывать на Python.

---

# E2. Эволюция модели

После создания Case нужно хранить момент конвертации Intake.

В `Service Intake` добавить Standard field:

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Converted At | `converted_at` | Datetime | Read Only, Permission Level 1 |

Поле не добавлять в Web Form.

Проверить JSON:

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git diff -- service_intake/service_intake/doctype/service_intake/service_intake.json
```

`Read Only` — UI property. Автоматическое заполнение должен делать серверный код.

---

# E3. Семантическая команда `create_case`

Frappe уже даёт generic CRUD для Document. Нужен не второй CRUD endpoint, а предметное
действие:

```text
Accepted Intake
→ проверить права и состояние
→ создать связанный Case
→ записать converted_at
→ оставить Timeline comment
```

Открыть:

```text
service_intake/service_intake/doctype/service_intake/service_intake.py
```

и привести controller к виду:

```python
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ServiceIntake(Document):
	@frappe.whitelist(methods=["POST"])
	def create_case(
		self,
		case_title: str,
		case_description: str,
		category: str,
		priority: str = "Normal",
	):
		self.check_permission("write")

		if self.triage_status != "Accepted":
			frappe.throw("Only an accepted Service Intake can be converted to a Service Case.")

		if frappe.db.exists("Service Case", {"source_intake": self.name}):
			frappe.throw("A Service Case already exists for this Service Intake.")

		case = frappe.new_doc("Service Case")
		case.case_title = case_title
		case.source_intake = self.name
		case.case_description = case_description
		case.category = category
		case.priority = priority
		case.insert()

		self.converted_at = now_datetime()
		self.save()

		self.add_comment("Info", text=f"Created Service Case {case.name}")

		return {"case": case.name}
```

## Почему controller Intake

Команда относится к одному конкретному Intake и использует его state. Отдельный
`CaseCreationService`, который только переименует `frappe.new_doc()`, `insert()` и
`save()`, новой ответственности не создаёт.

Service/module имеет смысл позже, если появится реальная cross-document orchestration,
reusable algorithm или внешний protocol.

## Permissions

В business command нет:

```text
ignore_permissions=True
```

- `self.check_permission("write")` проверяет Intake;
- `case.insert()` проверяет Create на Case;
- `ServiceCase.before_insert()` проверяет Read на source Intake и Accepted-state.

Role matrix не копируется в Python.

---

# E4. Вызвать Document method через REST API v2

Exact `v16.32.0` имеет route:

```text
POST /api/v2/document/<doctype>/<name>/method/<method>/
```

Создать временный API Key/Secret у `triage@example.com`.

```bash
read -r -p "API key: " TRIAGE_API_KEY
read -r -s -p "API secret: " TRIAGE_API_SECRET
echo
```

Через Desk создать новый Accepted Intake и запомнить его фактический `name`, например
`INT-2026-00003`.

```bash
curl -sS -X POST \
  -H "Authorization: token ${TRIAGE_API_KEY}:${TRIAGE_API_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "case_title": "API conversion test",
    "case_description": "Reviewed content for the internal case",
    "category": "Access",
    "priority": "Normal"
  }' \
  "http://intake.localhost:8000/api/v2/document/Service%20Intake/INT-2026-00003/method/create_case/"
```

Подставить реальный `name`.

Проверить:

- создан ровно один Case;
- `source_intake` заполнен;
- `converted_at` заполнен;
- в Timeline Intake появился Info comment.

Повторить POST — второй Case не появляется. Затем вызвать команду для Intake `New` —
получить ошибку состояния.

```bash
unset TRIAGE_API_KEY TRIAGE_API_SECRET
```

Различать:

```text
/api/resource или /api/v2/document
→ generic Document CRUD

/create_case
→ semantic command приложения
```

Не создавать `/create_service_case`, `/update_service_case`, `/delete_service_case`, если
они лишь повторяют штатный CRUD.

---

# E5. Transaction boundary

Успешный write HTTP request Frappe завершает commit. Uncaught exception приводит к
rollback.

Поэтому в `create_case` не добавлять:

```python
frappe.db.commit()
```

Одна business operation:

```text
Case insert
Intake converted_at update
Timeline Comment
```

## Rollback probe

Создать новый Accepted Intake без Case.

Временно вставить сразу после:

```python
case.insert()
```

строку:

```python
frappe.throw("Transaction rollback probe")
```

Вызвать REST-команду. Ожидается ошибка.

Проверить:

```text
Case with this source_intake
→ отсутствует

converted_at
→ пусто
```

Удалить probe и повторить вызов — Case создаётся.

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git diff --check
grep -R "Transaction rollback probe" -n service_intake || true
```

Перед commit вывод `grep` должен быть пустым.

---

# E6. Patch для существующих данных

После P3 уже есть минимум один Case, созданный вручную до появления `converted_at`.
Schema добавит field, но не заполнит исторические записи.

Создать:

```text
service_intake/patches/v1_0/__init__.py
service_intake/patches/v1_0/backfill_converted_at.py
```

`backfill_converted_at.py`:

```python
import frappe


def execute():
	cases = frappe.get_all(
		"Service Case",
		fields=["source_intake", "creation"],
		filters={"source_intake": ["is", "set"]},
	)

	for case in cases:
		if not frappe.db.get_value("Service Intake", case.source_intake, "converted_at"):
			frappe.db.set_value(
				"Service Intake",
				case.source_intake,
				"converted_at",
				case.creation,
				update_modified=False,
			)
```

В `service_intake/patches.txt`:

```text
[pre_model_sync]

[post_model_sync]
service_intake.patches.v1_0.backfill_converted_at
```

Patch зависит от нового field, поэтому идёт после model sync.

`frappe.db.set_value` здесь — deliberate one-off migration bypass, а не образец business
CRUD.

## Upgrade proof

До migrate у старого Intake из P3 `converted_at` пустой.

```bash
cd ~/frappe/frappe-practicum-bench
bench --site intake.localhost migrate
```

После migrate поле получает `Service Case.creation`.

Повторить migrate. Значение не меняется, тот же patch не выполняется как новая
одноразовая миграция.

---

# E7. Integration tests собственного поведения

Не запускать suite на рабочем `intake.localhost`. Test runner подготавливает test
dependencies; рабочий учебный site не должен становиться test database.

Создать отдельный site:

```bash
cd ~/frappe/frappe-practicum-bench
bench new-site intake-test.localhost --db-root-username frappe_admin
bench --site intake-test.localhost install-app service_intake
bench --site intake-test.localhost migrate
```

Working data P3 не копировать.

Открыть или создать:

```text
service_intake/service_intake/doctype/service_case/test_service_case.py
```

Содержимое:

```python
import frappe
from frappe.tests import IntegrationTestCase


CONSENT = "I consent to be contacted"


class TestServiceCase(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		if not frappe.db.exists("Service Category", "Access"):
			frappe.get_doc(
				{
					"doctype": "Service Category",
					"category_name": "Access",
				}
			).insert(ignore_permissions=True)

	def make_intake(self, *, status="New", subject="Test intake"):
		return frappe.get_doc(
			{
				"doctype": "Service Intake",
				"reporter_name": "Test Reporter",
				"reporter_email": "test@example.com",
				"topic": "Access",
				"subject": subject,
				"description": "Test description",
				"contact_consent": CONSENT,
				"triage_status": status,
			}
		).insert(ignore_permissions=True)

	def make_agent(self):
		return frappe.get_doc(
			{
				"doctype": "User",
				"email": "engineering.agent@example.com",
				"first_name": "Engineering Agent",
				"enabled": 1,
				"send_welcome_email": 0,
				"roles": [{"role": "Service Agent"}],
			}
		).insert(ignore_permissions=True)

	def test_case_requires_accepted_intake_on_insert(self):
		intake = self.make_intake(status="New")

		case = frappe.get_doc(
			{
				"doctype": "Service Case",
				"case_title": "Should fail",
				"source_intake": intake.name,
				"case_description": "Test",
				"category": "Access",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			case.insert(ignore_permissions=True)

	def test_create_case_converts_accepted_intake_once(self):
		intake = self.make_intake(status="Accepted", subject="Accepted intake")

		result = intake.create_case(
			case_title="Created from command",
			case_description="Reviewed content",
			category="Access",
			priority="Normal",
		)

		case = frappe.get_doc("Service Case", result["case"])
		self.assertEqual(case.source_intake, intake.name)

		intake.reload()
		self.assertTrue(intake.converted_at)

		with self.assertRaises(frappe.ValidationError):
			intake.create_case(
				case_title="Duplicate",
				case_description="Should not be created",
				category="Access",
			)

	def test_agent_can_update_existing_case_without_intake_read(self):
		intake = self.make_intake(status="Accepted", subject="Agent boundary")
		result = intake.create_case(
			case_title="Agent case",
			case_description="Reviewed content",
			category="Access",
		)
		agent = self.make_agent()

		self.assertFalse(frappe.has_permission("Service Intake", "read", user=agent.name))

		try:
			frappe.set_user(agent.name)
			case = frappe.get_doc("Service Case", result["case"])
			case.priority = "High"
			case.save()
		finally:
			frappe.set_user("Administrator")
```

Третий test защищает архитектурную границу: Agent может менять существующий Case без Read
на Intake. Если creation-rule вернуть в общий `validate()`, test должен упасть.

`ignore_permissions=True` используется только в helpers для подготовки test data. Это не
security acceptance. Permission-aware command проверен реальным Triage API user в E4.

Запустить:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site intake-test.localhost run-tests --app service_intake
```

Исправить suite до зелёного результата.

---

# E8. Background Jobs, `after_commit` и Webhook

В текущем `create_case` нет долгой операции и внешней системы. Custom Background Job
продукту не нужен.

## Background Jobs

Exact `v16.32.0` `frappe.enqueue` имеет:

```text
enqueue_after_commit
job_id
deduplicate
```

При `enqueue_after_commit=True` job ставится в очередь только после успешного commit.
Worker commit-ит успешную job и rollback-ит ошибочную.

Если позже появится тяжёлая внутренняя обработка:

```python
frappe.enqueue(
	"service_intake.some_module.process_case",
	case_name=case.name,
	enqueue_after_commit=True,
	job_id=f"service-case:{case.name}",
	deduplicate=True,
)
```

Этот код не добавлять, пока нет реального `process_case`.

## Webhook

Для ordinary DocType events exact v16.32 Webhook накапливается в transaction-local
queue. Frappe регистрирует flush через `frappe.db.after_commit`; после успешного commit
фактическая HTTP-отправка ставится в Background Job выбранной очереди.

Поэтому простой outbound callback сначала выражается штатным Webhook, а не Webhook плюс
ещё один custom job.

Webhook подходит, когда достаточно настраиваемого event, condition, headers, payload и
подписи.

Сложная orchestration, собственная protocol-level idempotency или несколько внешних
систем могут потребовать integration module/service и jobs.

## Приёмка E8

| Требование | Первый кандидат |
|---|---|
| простой HTTP callback при создании Case | Webhook |
| тяжёлая внутренняя работа после commit | Background Job + `enqueue_after_commit` |
| synchronous invariant/mutation Document | подходящий Controller lifecycle event |
| сложный protocol нескольких систем | integration module/service |

Фальшивой job в app нет.

---

# E9. Финальная поставка

Upgrade, automated tests и fresh install — три разные проверки.

## Source check

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git status --short
git diff --check
git diff --stat
git diff
```

Ожидаемые изменения:

```text
Service Intake JSON → converted_at
Service Intake controller → create_case
Service Case controller → before_insert
patches.txt + patch module
tests
```

Не должно быть:

```text
Users
API keys/secrets
working Intake/Case data
transaction probe
manual DB dump
```

Создать commit:

```bash
git add .
git commit -m "Add native service intake business logic"
```

## Upgrade acceptance

На существующем `intake.localhost`:

```bash
bench --site intake.localhost migrate
```

Проверить:

- старый Case/Intake из P3 сохранился;
- `converted_at` старого Intake заполнен patch;
- новый semantic command работает;
- Agent по-прежнему работает с Case без Read на Intake.

Automated suite здесь не запускать.

## Test acceptance

```bash
bench --site intake-test.localhost migrate
bench --site intake-test.localhost run-tests --app service_intake
```

Suite должен быть зелёным.

## Fresh-install acceptance

```bash
bench new-site intake-engineering-clean.localhost --db-root-username frappe_admin
bench --site intake-engineering-clean.localhost install-app service_intake
bench --site intake-engineering-clean.localhost migrate
```

До создания рабочих данных проверить:

- `converted_at` существует;
- controllers загружаются;
- fixtures P3 присутствуют;
- patch безопасен без historical Case data;
- Intake/Case отсутствуют.

Automated suite уже доказан на test site и не загрязняет критерий «fresh install без
working data».

## Финальный gate

Ученик без подсказки объясняет:

```text
1. Почему Accepted-source rule принадлежит before_insert, а не Client Script или общему validate.
2. Почему Link/Unique/Set Only Once не переписаны на Python.
3. Почему create_case — semantic command, а не второй CRUD API.
4. Где проверяются permissions команды.
5. Почему внутри команды нет frappe.db.commit().
6. Что доказал rollback probe.
7. Почему backfill сделан patch, а не lifecycle текущего Document.
8. Почему direct DB update допустим в patch и не становится обычным CRUD pattern.
9. Что tests проверяют в app и почему для них выделен отдельный site.
10. Почему Background Job не добавлен без реальной долгой работы.
11. Почему ordinary Webhook не нужно оборачивать во второй post-commit job.
```

Engineering Track принят, если ученик умеет не только написать код, но и объяснить,
почему каждый кусок находится именно в своём Frappe-native слое.
