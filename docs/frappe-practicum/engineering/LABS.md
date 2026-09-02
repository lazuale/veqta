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

# E1. Добавить серверный инвариант в Controller

## Задача

В P3 `Service Case.source_intake` уже:

```text
Mandatory
Unique
Set Only Once
Link → Service Intake
```

Этого достаточно, чтобы ссылка существовала, не дублировалась и не менялась после
создания. Но metadata **не выражает** правило:

> `Service Case` можно создать только из `Service Intake` со статусом `Accepted`.

Не переносить это правило в Client Script: оно должно действовать и в Desk, и через API,
и при серверном создании Document.

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

## Добавить `validate`

Привести controller к виду:

```python
import frappe
from frappe.model.document import Document


class ServiceCase(Document):
	def validate(self):
		if not self.source_intake:
			return

		intake = frappe.get_doc("Service Intake", self.source_intake)
		intake.check_permission("read")

		if intake.triage_status != "Accepted":
			frappe.throw("Service Case can only be created from an accepted Service Intake.")
```

Здесь controller не заменяет Link, Unique или Set Only Once. Он добавляет **только тот
инвариант, которого metadata не умеет выразить**.

## Проверить

В Desk под `Service Triage`:

1. создать новый `Service Intake` со статусом `New`;
2. попытаться создать Case со ссылкой на него;
3. получить ошибку controller validation;
4. изменить Intake на `Accepted`;
5. повторить создание Case — сохранение должно пройти.

После проверки удалить созданный Case, чтобы Intake можно было использовать дальше.

## Что доказано

```text
Link
→ target существует

Unique
→ один Case на один Intake

Set Only Once
→ source нельзя перепривязать

Controller.validate
→ source обязан быть Accepted
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

Почему поле Standard: оно принадлежит модели приложения и должно существовать на любом
site с этой версией app.

Почему `Read Only` недостаточно для автоматической гарантии: это UI property. Значение
должен выставлять серверный код приложения.

---

# E3. Сделать семантическую команду `create_case`

## Почему не новый CRUD endpoint

Frappe уже предоставляет CRUD API для Document. Нам нужен не второй `create Service
Case`, а бизнес-действие:

```text
accepted Intake
→ проверить право и инварианты
→ создать связанный Case
→ зафиксировать converted_at
→ оставить запись в Timeline
```

Это команда предметного действия.

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

## Почему именно controller

Команда относится к **одному конкретному `Service Intake`** и использует его состояние.
Отдельный `CaseCreationService`, который только оборачивает этот метод, новой
ответственности не создаст.

Если позже операция начнёт координировать несколько независимых подсистем или внешний
протокол, отдельный module/service можно будет ввести по фактической сложности.

## Permission model

В коде нет:

```text
ignore_permissions=True
```

`self.check_permission("write")` проверяет право на Intake.

`case.insert()` идёт обычным permission-aware Document path и проверяет право Create на
`Service Case`.

Поэтому не нужно вручную копировать Role matrix в Python.

---

# E4. Вызвать Document method через REST API v2

Frappe v16.32.0 имеет отдельный route для whitelisted document method:

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

Создать новый Intake через Desk и вручную перевести его в `Accepted`. Запомнить его
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

- создан ровно один Service Case;
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

В обычном write HTTP request Frappe завершает успешную операцию commit. Необработанное
исключение приводит к rollback.

Поэтому внутри `create_case` **не добавлять**:

```python
frappe.db.commit()
```

Все три изменения:

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

Проверить через Desk или List filter:

```text
Service Case with source_intake = этот Intake
→ отсутствует

converted_at
→ пусто
```

То есть Case успел пройти `insert()` внутри Python-вызова, но request не был успешно
завершён и Framework откатил транзакцию.

**Сразу удалить временный `frappe.throw`** и повторить вызов. Теперь Case должен
создаться.

Проверить diff и убедиться, что probe не остался в исходниках:

```bash
cd ~/frappe/frappe-practicum-bench/apps/service_intake
git diff --check
grep -R "Transaction rollback probe" -n service_intake || true
```

---

# E6. Добавить patch для уже существующих данных

## Почему нужен patch

На site после P3 уже существует минимум один Case, созданный вручную **до появления**
`converted_at`.

Новая схема создаст поле, но сама по себе не заполнит исторические записи.

Это задача data migration, а не controller текущей бизнес-операции.

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

Почему `post_model_sync`: patch зависит от нового поля `converted_at`, поэтому schema
должна быть синхронизирована раньше.

Почему здесь допустим `frappe.db.set_value`: это одноразовая data migration, где
намеренно не нужен обычный lifecycle текущего business document. Такой bypass не надо
копировать в обычные пользовательские операции.

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

Значение не должно дублироваться или изменяться. Patch Log не должен выполнять тот же
patch как новый второй раз.

---

# E7. Добавить integration tests собственного поведения

Тестируем **то, что добавило наше приложение**, а не то, что Link или Mandatory вообще
работают во Frappe.

Открыть или создать:

```text
service_intake/service_intake/doctype/service_case/test_service_case.py
```

Использовать актуальный для v16.32 base class:

```python
import frappe
from frappe.tests import IntegrationTestCase


class TestServiceCase(IntegrationTestCase):
	def make_intake(self, *, status="New", subject="Test intake"):
		return frappe.get_doc(
			{
				"doctype": "Service Intake",
				"reporter_name": "Test Reporter",
				"reporter_email": "test@example.com",
				"topic": "Access",
				"subject": subject,
				"description": "Test description",
				"contact_consent": "I consent to be contacted",
				"triage_status": status,
			}
		).insert(ignore_permissions=True)

	def test_case_requires_accepted_intake(self):
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
```

Для теста category `Access` должна существовать. Если test runner не создаёт рабочие
данные P3, создать Category в `setUpClass`/helper самого теста, а не зависеть от базы
ручного site.

Добавить второй test для accepted Intake и `create_case`, проверяющий:

```text
Case created
source_intake correct
converted_at not empty
second conversion rejected
```

Для проверки permission-aware public command отдельно создать тестового User с нужной
ролью либо оставить permission test на REST acceptance из E4. Не использовать
`ignore_permissions=True` как доказательство прав: в test helper это допустимый способ
подготовить входные данные, но не acceptance security path.

Запустить:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site intake.localhost run-tests --app service_intake
```

Исправить тесты до зелёного результата.

---

# E8. Background Jobs, `after_commit` и Webhook: выбрать, а не внедрить ради галочки

В текущем `create_case` нет долгой операции и нет внешней системы. Поэтому custom
Background Job **не нужен продукту**.

Но ученик обязан знать границу.

## Exact v16.32 behavior

`frappe.enqueue` имеет параметр:

```text
enqueue_after_commit=True
```

При нём постановка job регистрируется в `frappe.db.after_commit` и происходит только
после успешного commit текущей транзакции.

Background worker сам commit-ит успешную job и rollback-ит ошибочную.

### Когда это было бы нужно

Если после создания Case появится требование:

```text
сформировать тяжёлый пакет
обратиться к медленной внешней системе
выполнить большую обработку
```

то основной request должен сохранить собственную бизнес-транзакцию, а работа может
быть поставлена после commit:

```python
frappe.enqueue(
	"service_intake.some_module.process_case",
	case_name=case.name,
	enqueue_after_commit=True,
	job_id=f"service-case:{case.name}",
	deduplicate=True,
)
```

Этот код **не добавлять** в продукт, пока метода `process_case` и реальной ответственности
нет.

## Webhook

Если нужна простая настраиваемая отправка HTTP по DocType event, сначала проверить
штатный `Webhook` Frappe. В v16.32 он умеет DocType events, condition, headers, JSON/form
payload и подпись.

Если нужна сложная orchestration, собственная идемпотентность, несколько систем или
особый протокол, тогда появляется integration module/service и, возможно, Background
Job.

### Приёмка E8

Ученик должен для трёх требований выбрать механизм:

| Требование | Ожидаемый выбор |
|---|---|
| отправить простой HTTP callback при создании Case | Webhook сначала |
| после commit выполнить тяжёлую внутреннюю обработку | Background Job + `enqueue_after_commit` |
| изменить поле Case синхронно как часть его валидности | Controller/lifecycle, не queue |

Здесь намеренно нет фальшивой job в исходниках app.

---

# E9. Финальная поставка: clean install и upgrade — разные проверки

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
Service Case controller → validate
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
bench --site intake.localhost run-tests --app service_intake
```

Проверить старую запись P3 и новый semantic command.

## Clean-install acceptance

Создать новый site:

```bash
bench new-site intake-engineering-clean.localhost --db-root-username frappe_admin
bench --site intake-engineering-clean.localhost install-app service_intake
bench --site intake-engineering-clean.localhost migrate
```

На чистом site:

- поле `converted_at` существует;
- controllers загружаются;
- fixtures P3 присутствуют;
- patch не требует старых рабочих данных;
- tests проходят;
- новых Intake/Case нет до создания test/working data.

## Финальный gate

Ученик должен без подсказки объяснить:

```text
1. Почему Accepted-source rule принадлежит controller, а не Client Script.
2. Почему Link/Unique/Set Only Once не переписаны на Python.
3. Почему create_case — semantic command, а не второй CRUD API.
4. Где проверяются permissions команды.
5. Почему внутри команды нет frappe.db.commit().
6. Что именно доказал rollback probe.
7. Почему backfill сделан patch, а не validate текущего Document.
8. Почему direct DB update допустим в этом patch и не становится обычным CRUD pattern.
9. Что tests проверяют в нашем app и что они не должны заново тестировать во Frappe.
10. Почему Background Job не был добавлен без реальной долгой работы.
```

Engineering Track принят, если ученик умеет не только написать этот код, но и объяснить,
**почему каждый кусок находится именно в своём Frappe-native слое**.
