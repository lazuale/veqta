# Engineering Track: нативный программный слой Frappe

Перед началом P3 должен быть полностью принят на рабочем и чистом site.

Рабочий app:

```text
service_intake
```

Рабочий site:

```text
intake.localhost
```

Базовая версия:

```text
Frappe Framework v16.32.0
```

Этот блок впервые добавляет собственный Python. Перед каждой правкой сначала называется
ответственность, которой не хватило в metadata.

---

# E1. Добавить creation invariant в Controller

## Задача

В P3 `Service Case.source_intake` уже имеет:

```text
Mandatory
Unique
Set Only Once
Link → Service Intake
```

Этого достаточно, чтобы ссылка существовала, не дублировалась и не менялась после
создания. Но metadata не выражает правило:

> `Service Case` можно создать только из `Service Intake` со статусом `Accepted`.

Это правило относится именно к **созданию Case**. После создания Agent должен иметь
возможность работать с Case, хотя по модели P3 он не имеет Read на исходный Intake с
контактными данными.

Поэтому правило нельзя бездумно повесить на `validate()`: `validate()` запускается и при
последующих save существующего Case. Такой вариант незаметно связал бы право Agent
редактировать Case с правом читать Intake.

Нужен lifecycle event, совпадающий по смыслу с гарантией: `before_insert`.

## Проверить исходное состояние

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git status --short
git log --oneline -1
```

Working tree должен быть чистым после P3.

Открыть controller:

```text
service_intake/service_intake/doctype/service_case/service_case.py
```

Он должен содержать класс `ServiceCase(Document)`.

## Добавить `before_insert`

Привести controller к виду:

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

Почему `before_insert`, а не Client Script:

```text
Desk create
REST create
server-side Document insert
→ один и тот же creation invariant
```

Почему здесь остаётся `intake.check_permission("read")`: пользователь, который создаёт
внутренний Case из Intake, должен иметь право видеть источник. Но эта проверка не должна
выполняться на каждом последующем save Case.

## Проверить

Под `Service Triage`:

1. создать `Service Intake` со статусом `New`;
2. попытаться создать Case со ссылкой на него;
3. получить ошибку `before_insert`;
4. изменить Intake на `Accepted`;
5. повторить создание Case — сохранение должно пройти;
6. назначить Case `agent@example.com`;
7. под Agent изменить разрешённое рабочее поле Case и сохранить Document.

Последний шаг обязателен. Он доказывает, что creation invariant не превратился в скрытое
требование дать Agent Read на Intake.

После проверки удалить созданный Case, чтобы Intake можно было использовать дальше.

## Что доказано

```text
Link
→ target существует

Unique
→ один Case на один Intake

Set Only Once
→ source нельзя перепривязать

Controller.before_insert
→ при создании source обязан быть Accepted
```

Это четыре разные гарантии. Не переписывать первые три на Python.

---

# E2. Эволюция модели: фиксировать момент конвертации

## Новое требование

После создания внутреннего Case нужно автоматически хранить момент, когда Intake был
конвертирован.

В `Service Intake` добавить Standard field:

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Converted At | `converted_at` | Datetime | Read Only, Permission Level 1 |

Поле не добавлять в Web Form.

Проверить изменение JSON:

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git diff -- service_intake/service_intake/doctype/service_intake/service_intake.json
```

Поле Standard, потому что оно принадлежит модели приложения и должно существовать на
любом site с этой версией app.

`Read Only` не является серверной автоматизацией. Это свойство интерфейса; значение
должен выставлять серверный код приложения.

---

# E3. Сделать семантическую команду `create_case`

## Почему не новый CRUD endpoint

Frappe уже предоставляет CRUD API для Document. Нам нужен не второй способ сделать
`INSERT Service Case`, а предметное действие:

```text
Accepted Intake
→ проверить права и состояние
→ создать связанный Case
→ зафиксировать converted_at
→ оставить запись в Timeline
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

## Почему команда живёт в controller Intake

Команда относится к одному конкретному `Service Intake` и использует его state. Отдельный
`CaseCreationService`, который только переименует `frappe.new_doc()`, `insert()` и
`save()`, самостоятельной ответственности не добавит.

Если позже операция начнёт координировать несколько подсистем, reusable algorithm или
внешний protocol, отдельный module/service можно будет ввести по фактической сложности.

## Permission model

В business command нет:

```text
ignore_permissions=True
```

`self.check_permission("write")` проверяет право на Intake.

`case.insert()` идёт обычным permission-aware Document path и проверяет Create на
`Service Case`.

`ServiceCase.before_insert()` дополнительно требует Read на source Intake и проверяет его
Accepted-state.

Поэтому Role matrix не копируется вручную в Python.

---

# E4. Вызвать Document method через REST API v2

Frappe v16.32.0 имеет route для whitelisted document method:

```text
POST /api/v2/document/<doctype>/<name>/method/<method>/
```

Для проверки создать временный API Key/Secret у `triage@example.com`. Значения не
записывать в файлы и Git.

В shell:

```bash
read -r -p "API key: " TRIAGE_API_KEY
read -r -s -p "API secret: " TRIAGE_API_SECRET
echo
```

Создать новый Intake через Desk и перевести его в `Accepted`. Запомнить фактический
`name`, например:

```text
INT-2026-00003
```

Вызвать команду:

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

Подставить фактический `name` Intake.

Проверить в Desk:

- создан ровно один `Service Case`;
- `source_intake` заполнен;
- `converted_at` заполнен;
- в Timeline Intake появился Info comment.

Повторить тот же POST. Должна прийти ошибка, а второй Case не должен появиться.

Затем создать Intake `New` и вызвать команду для него. Должна прийти ошибка состояния.

После проверки:

```bash
unset TRIAGE_API_KEY TRIAGE_API_SECRET
```

## Что отличать

```text
/api/resource или /api/v2/document
→ generic Document CRUD

/create_case document method
→ semantic command приложения
```

Не создавать `/create_service_case`, `/update_service_case`, `/delete_service_case`, если
они только повторяют штатный CRUD.

---

# E5. Увидеть transaction boundary

## Что Frappe делает сам

Успешный write HTTP request Frappe завершает commit. Необработанное исключение приводит
к rollback.

Поэтому внутри `create_case` не добавлять:

```python
frappe.db.commit()
```

Все изменения:

```text
Service Case insert
Service Intake converted_at update
Timeline Comment
```

должны принадлежать одной request transaction.

## Практический rollback probe

Создать новый Accepted Intake, для которого Case ещё нет.

Временно вставить в `create_case` сразу после:

```python
case.insert()
```

строку:

```python
frappe.throw("Transaction rollback probe")
```

Вызвать REST-команду. Она должна завершиться ошибкой.

Проверить:

```text
Service Case with source_intake = этот Intake
→ отсутствует

converted_at
→ пусто
```

Case успел пройти `insert()` внутри Python-вызова, но request не завершился успешно, и
Framework откатил транзакцию.

Сразу удалить временный `frappe.throw` и повторить вызов. Теперь Case должен создаться.

Проверить diff:

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git diff --check
grep -R "Transaction rollback probe" -n service_intake || true
```

Перед commit вывод `grep` должен быть пустым.

---

# E6. Добавить patch для уже существующих данных

## Почему нужен patch

На site после P3 уже существует минимум один Case, созданный вручную до появления
`converted_at`.

Новая схема создаст поле, но сама по себе не заполнит исторические записи. Это data
migration, а не lifecycle текущей бизнес-операции.

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

В `service_intake/patches.txt` использовать post-model-sync section:

```text
[pre_model_sync]

[post_model_sync]
service_intake.patches.v1_0.backfill_converted_at
```

Patch зависит от нового поля `converted_at`, поэтому schema должна быть синхронизирована
раньше.

`frappe.db.set_value` здесь допустим как deliberate one-off data migration bypass. Это не
образец обычного business CRUD.

## Проверить upgrade

До migrate найти старый Intake из P3, у которого уже есть Case. `converted_at` должен
быть пустым.

Выполнить:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site intake.localhost migrate
```

После migrate старый Intake должен получить `converted_at` из `Service Case.creation`.

Повторить:

```bash
bench --site intake.localhost migrate
```

Значение не должно измениться. В `Patch Log` тот же patch не должен выполняться как новая
одноразовая миграция второй раз.

---

# E7. Добавить integration tests собственного поведения

Тестируем то, что добавило наше приложение, а не то, что Link или Mandatory вообще
работают во Frappe.

## Почему нужен отдельный test site

Не запускать automated suite на рабочем `intake.localhost`. Test runner v16 подготавливает
окружение и может создавать/commit-ить test dependencies. Рабочий учебный site не должен
становиться test database.

Создать отдельный site:

```bash
cd ~/frappe/frappe-practicum-bench
bench new-site intake-test.localhost --db-root-username frappe_admin
bench --site intake-test.localhost install-app service_intake
bench --site intake-test.localhost migrate
```

Working data P3 на этот site не копировать.

## Создать полный test module

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

Третий test защищает важную архитектурную границу: Agent может менять существующий Case
без Read на Intake. Если creation-rule снова случайно перенести в общий `validate()`, этот
test должен упасть.

`ignore_permissions=True` используется только в helpers для подготовки test data. Это не
доказательство security. Permission-aware command отдельно проверен через реального
Triage API user в E4.

Запустить:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site intake-test.localhost run-tests --app service_intake
```

Исправить suite до зелёного результата.

---

# E8. Background Jobs, `after_commit` и Webhook: выбрать, а не внедрить ради галочки

В текущем `create_case` нет долгой операции и нет внешней системы. Поэтому custom
Background Job продукту не нужен.

## Exact v16.32 behavior Background Jobs

`frappe.enqueue` имеет параметры:

```text
enqueue_after_commit
job_id
deduplicate
```

При `enqueue_after_commit=True` постановка job регистрируется через
`frappe.db.after_commit` и происходит только после успешного commit текущей транзакции.

Background worker commit-ит успешную job и rollback-ит ошибочную.

Если после создания Case появится реальное требование выполнить тяжёлую внутреннюю
обработку, возможен такой вариант:

```python
frappe.enqueue(
	"service_intake.some_module.process_case",
	case_name=case.name,
	enqueue_after_commit=True,
	job_id=f"service-case:{case.name}",
	deduplicate=True,
)
```

Этот код не добавлять в продукт, пока метода `process_case` и соответствующей
ответственности нет.

## Exact v16.32 behavior Webhook

Для обычных DocType events штатный Webhook сначала накапливается в transaction-local
queue. Frappe регистрирует flush через `frappe.db.after_commit`, а после успешного commit
ставит фактическую HTTP-отправку в Background Job выбранной очереди.

То есть простой configurable outbound callback уже имеет штатный post-commit path. Не
надо оборачивать обычный Webhook во второй custom job только «для асинхронности».

Webhook подходит, когда достаточно настраиваемого DocType event, condition, headers,
payload и подписи.

Если нужна сложная orchestration, собственная идемпотентность уровня бизнес-протокола,
несколько систем или особый protocol, тогда появляется integration module/service и,
возможно, отдельные jobs.

## Приёмка E8

Для каждого требования выбрать первый естественный owner:

| Требование | Ожидаемый выбор |
|---|---|
| отправить простой HTTP callback при создании Case | Webhook |
| после commit выполнить тяжёлую внутреннюю обработку | Background Job + `enqueue_after_commit` |
| изменить/проверить Case синхронно как часть lifecycle | Controller lifecycle |
| координировать сложный protocol нескольких систем | integration module/service |

Здесь намеренно нет фальшивой job в исходниках app.

---

# E9. Финальная поставка: upgrade, tests и clean install — разные проверки

## Source check

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git status --short
git diff --check
git diff --stat
git diff
```

В исходниках должны появиться только осознанные изменения:

```text
Service Intake JSON → converted_at
Service Intake controller → create_case
Service Case controller → before_insert
a patches.txt + patch module
tests
```

Если в diff буквально появилась строка `a patches.txt`, это опечатка: ожидается обычный
`patches.txt`. Проверить фактические пути перед commit.

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
- `converted_at` старого Intake backfill-нут patch;
- новый semantic command работает;
- Agent по-прежнему работает с Case без Read на Intake.

Automated suite здесь не запускать: рабочий site не используется как test database.

## Test acceptance

На отдельном `intake-test.localhost`:

```bash
bench --site intake-test.localhost migrate
bench --site intake-test.localhost run-tests --app service_intake
```

Suite должен быть зелёным.

## Clean-install acceptance

Создать новый site:

```bash
bench new-site intake-engineering-clean.localhost --db-root-username frappe_admin
bench --site intake-engineering-clean.localhost install-app service_intake
bench --site intake-engineering-clean.localhost migrate
```

До создания любых рабочих данных проверить:

- поле `converted_at` существует;
- controllers загружаются;
- fixtures P3 присутствуют;
- patch безопасен при отсутствии historical Case data;
- новых Intake/Case нет.

Это проверка fresh install. Automated suite уже отдельно доказан на test site и не должен
загрязнять критерий «после чистой установки нет working data».

## Финальный gate

Ученик должен без подсказки объяснить:

```text
1. Почему Accepted-source rule принадлежит before_insert, а не Client Script или общий validate.
2. Почему Link/Unique/Set Only Once не переписаны на Python.
3. Почему create_case — semantic command, а не второй CRUD API.
4. Где проверяются permissions команды.
5. Почему внутри команды нет frappe.db.commit().
6. Что именно доказал rollback probe.
7. Почему backfill сделан patch, а не lifecycle текущего Document.
8. Почему direct DB update допустим в этом patch и не становится обычным CRUD pattern.
9. Что tests проверяют в нашем app и почему для них выделен отдельный site.
10. Почему Background Job не был добавлен без реальной долгой работы.
11. Почему обычный Webhook не нужно вручную оборачивать во второй post-commit job.
```

Engineering Track принят, если ученик умеет не только написать код, но и объяснить,
почему каждый кусок находится именно в своём Frappe-native слое.
