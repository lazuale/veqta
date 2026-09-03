# S09. Закрепить permission и reporting-контракты тестами

К S09 приложение уже добавило несколько собственных контрактов:

```text
Rental Operator → If Owner
Rental Manager  → Report
Query Report    → manager-only
Script Report   → manager-only
Equipment Utilization → включительный календарный расчёт
```

Новое требование:

> Эти правила должны проверяться повторяемо на чистых тестовых данных и падать, если собственное поведение App сломано.

Мы не тестируем Frappe на предмет того, умеет ли Report Builder группировать строки или Recorder показывать SQL. Проверяются только контракты `rental_training`.

Связанные материалы:

- [`S01_OWNER_PERMISSIONS.md`](S01_OWNER_PERMISSIONS.md);
- [`S05_QUERY_REPORT.md`](S05_QUERY_REPORT.md);
- [`S06_SCRIPT_REPORT.md`](S06_SCRIPT_REPORT.md);
- [`S08_QUERY_BUILDER.md`](S08_QUERY_BUILDER.md);
- [`../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

Первичный источник:

- https://docs.frappe.io/framework/user/en/testing

---

## 1. Что именно тестировать

### Permission metadata

```text
Rental Operator → If Owner = yes
Rental Manager  → Report = yes
```

### Runtime permission boundary

```text
operator A не читает Rental operator B
manager читает оба
```

### Standard Reports

```text
Equipment Rental History
Equipment Utilization
```

оба должны:

```text
быть Standard
ссылаться на Rental
разрешать Rental Manager
не разрешать Rental Operator
```

### Utilization

Нужно проверить:

```text
один день считается как 1
from_date > to_date отклоняется
пересечение границы периода обрезается
пересекающиеся интервалы не удваивают день
оптимизированная выборка сохраняет ожидаемый результат
```

Точное число SQL queries не фиксируется тестом.

---

## 2. Использовать существующий `test_rental.py`

Первый практикум уже создал:

```text
rental_training/rental_training/doctype/rental/test_rental.py
```

Не нужно создавать отдельную тестовую инфраструктуру только потому, что появилась отчётность.

Добавьте в этот файл второй `IntegrationTestCase` для reporting-контрактов.

Существующие тесты Rental не удаляйте.

---

## 3. Проверить `allow_tests`

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost show-config | grep allow_tests
```

Если tests выключены:

```bash
bench --site rental.localhost set-config allow_tests 1 --parse
```

Это настройка учебного Site, а не App.

---

## 4. Добавить imports

В `test_rental.py` уже используются `frappe`, `IntegrationTestCase` и `uuid4` из первого практикума.

Добавьте:

```python
from datetime import date

from rental_training.rental_training.report.equipment_utilization.equipment_utilization import (
    _count_occupied_days,
    _validate_period,
    execute as execute_utilization,
)
```

Если `date` уже импортирован, не дублируйте import.

---

## 5. Добавить класс reporting-тестов

После существующего `IntegrationTestRental` добавьте:

```python
class IntegrationTestRentalReporting(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

        self.customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Reporting Test Customer",
            }
        ).insert()

        self.equipment_a = frappe.get_doc(
            {
                "doctype": "Equipment",
                "equipment_name": "Reporting Equipment A",
                "equipment_type": "Tool",
            }
        ).insert()

        self.equipment_b = frappe.get_doc(
            {
                "doctype": "Equipment",
                "equipment_name": "Reporting Equipment B",
                "equipment_type": "Tool",
            }
        ).insert()

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def make_user(self, role):
        self.assertTrue(frappe.db.exists("Role", role))

        email = f"reporting-{frappe.scrub(role)}-{uuid4().hex[:8]}@example.test"
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": f"Reporting {role}",
                "send_welcome_email": 0,
                "user_type": "System User",
            }
        ).insert()

        user.add_roles(role)
        frappe.clear_cache(user=user.name)
        return user.name

    def make_rental(
        self,
        *,
        equipment,
        status="Planned",
        start_date="2026-09-01",
        end_date="2026-09-02",
    ):
        return frappe.get_doc(
            {
                "doctype": "Rental",
                "customer": self.customer.name,
                "start_date": start_date,
                "end_date": end_date,
                "status": status,
                "items": [{"equipment": equipment}],
            }
        )

    def test_reporting_permissions_are_part_of_rental_metadata(self):
        meta = frappe.get_meta("Rental")

        operator = next(
            permission
            for permission in meta.permissions
            if permission.role == "Rental Operator" and permission.permlevel == 0
        )
        manager = next(
            permission
            for permission in meta.permissions
            if permission.role == "Rental Manager" and permission.permlevel == 0
        )

        self.assertEqual(operator.if_owner, 1)
        self.assertEqual(manager.report, 1)

    def test_standard_reports_are_manager_only(self):
        for report_name in (
            "Equipment Rental History",
            "Equipment Utilization",
        ):
            report = frappe.get_doc("Report", report_name)
            roles = {row.role for row in report.roles}

            self.assertEqual(report.is_standard, "Yes")
            self.assertEqual(report.ref_doctype, "Rental")
            self.assertIn("Rental Manager", roles)
            self.assertNotIn("Rental Operator", roles)

    def test_operator_sees_only_owned_rental_and_manager_sees_both(self):
        operator_a = self.make_user("Rental Operator")
        operator_b = self.make_user("Rental Operator")
        manager = self.make_user("Rental Manager")

        with self.set_user(operator_a):
            rental_a = self.make_rental(
                equipment=self.equipment_a.name,
                start_date="2026-10-01",
                end_date="2026-10-02",
            ).insert()

        with self.set_user(operator_b):
            rental_b = self.make_rental(
                equipment=self.equipment_b.name,
                start_date="2026-10-03",
                end_date="2026-10-04",
            ).insert()

        with self.set_user(operator_a):
            rows = frappe.get_list(
                "Rental",
                filters={"name": ["in", [rental_a.name, rental_b.name]]},
                fields=["name"],
            )
            names = {row.name for row in rows}

            self.assertEqual(names, {rental_a.name})

            with self.assertRaises(frappe.PermissionError):
                frappe.get_doc(
                    "Rental",
                    rental_b.name,
                    check_permission="read",
                )

        with self.set_user(manager):
            rows = frappe.get_list(
                "Rental",
                filters={"name": ["in", [rental_a.name, rental_b.name]]},
                fields=["name"],
            )
            names = {row.name for row in rows}

            self.assertEqual(names, {rental_a.name, rental_b.name})

    def test_single_calendar_day_counts_as_one(self):
        occupied = _count_occupied_days(
            [(date(2026, 9, 10), date(2026, 9, 10))]
        )
        self.assertEqual(occupied, 1)

    def test_overlapping_intervals_do_not_double_count_boundary_day(self):
        occupied = _count_occupied_days(
            [
                (date(2026, 9, 1), date(2026, 9, 3)),
                (date(2026, 9, 3), date(2026, 9, 5)),
            ]
        )
        self.assertEqual(occupied, 5)

    def test_invalid_report_period_is_rejected(self):
        with self.assertRaises(frappe.ValidationError):
            _validate_period(
                frappe._dict(
                    from_date="2026-09-11",
                    to_date="2026-09-10",
                )
            )

    def test_utilization_clips_intervals_to_report_period(self):
        manager = self.make_user("Rental Manager")

        frappe.set_user("Administrator")

        self.make_rental(
            equipment=self.equipment_a.name,
            status="Returned",
            start_date="2026-08-30",
            end_date="2026-09-02",
        ).insert()

        self.make_rental(
            equipment=self.equipment_a.name,
            status="Returned",
            start_date="2026-09-02",
            end_date="2026-09-04",
        ).insert()

        with self.set_user(manager):
            _, data = execute_utilization(
                {
                    "from_date": "2026-09-01",
                    "to_date": "2026-09-03",
                }
            )

        row = next(
            item for item in data if item["equipment"] == self.equipment_a.name
        )

        self.assertEqual(row["period_days"], 3)
        self.assertEqual(row["occupied_days"], 3)
        self.assertEqual(row["utilization_percent"], 100.0)
```

---

## 6. Что доказывает permission test

Тест не смотрит на кнопки Desk.

Он выполняет реальные server-side операции:

```text
operator A создаёт свой Rental
operator B создаёт свой Rental
operator A вызывает permission-aware get_list
operator A пытается прочитать чужой Document
manager получает оба Rental
```

Если `If Owner` случайно исчезнет из metadata, тест должен упасть.

---

## 7. Что доказывает report metadata test

Мы не тестируем внутреннюю реализацию `Report.is_permitted()` Frappe.

Наш контракт проще:

```text
обязательный Standard Report существует
его Reference DocType = Rental
его App-owned roles содержат Rental Manager
Rental Operator в них отсутствует
```

Именно это состояние приложение обязано поставлять.

---

## 8. Что доказывает utilization test

Тест создаёт собственные рабочие данные и вызывает итоговую Python-функцию отчёта.

Период:

```text
2026-09-01 → 2026-09-03
```

Rentals Equipment A:

```text
2026-08-30 → 2026-09-02
2026-09-02 → 2026-09-04
```

После clipping и объединения:

```text
2026-09-01 → 2026-09-03
```

Поэтому:

```text
period_days   = 3
occupied_days = 3
utilization   = 100%
```

Этот тест защищает конечный результат после S08. Старую naive-реализацию хранить рядом только ради сравнения не нужно.

---

## 9. Запустить Rental tests

Сначала запустите тесты DocType:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost run-tests --doctype Rental
```

Все старые контракты первого практикума и новые reporting-тесты должны пройти вместе.

Если новый класс не попал в запуск вашего patch-release по `--doctype Rental`, выполните полный App suite:

```bash
bench --site rental.localhost run-tests --app rental_training
```

Полный App suite в любом случае нужен перед завершением этапа.

---

## 10. Не фиксировать exact SQL count тестом

Recorder на S07/S08 нужен для измерения.

Не добавляйте assertion вида:

```python
self.assertEqual(number_of_sql_queries, 7)
```

Служебные запросы Framework могут меняться между patch-release без нарушения нашего бизнес-контракта.

Что должно оставаться стабильным:

```text
нет N+1 по нашей форме запроса
результат расчёта правильный
```

Первое доказывается профилированием, второе — тестами.

---

## 11. Проверить diff

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git diff -- rental_training/rental_training/doctype/rental/test_rental.py
```

Тест не должен содержать зависимостей от ручных A1/B1 или конкретных `EQ-00001` текущего Site.

Тестовые Users и Documents создаются самим test case.

После успешного App suite:

```bash
git add rental_training/rental_training/doctype/rental/test_rental.py
git commit -m "test: cover rental reporting contracts"
```

---

## Результат этапа

К концу S09 автоматизированы собственные контракты:

```text
If Owner
Report permission
manager-only Standard Reports
runtime owner boundary
включительные календарные дни
объединение пересечений
clipping к report period
итоговый utilization после оптимизации
```

На S10 останется проверить последнюю архитектурную границу: что обязательное состояние воспроизводится из App на новом чистом Site без переноса рабочих Users и Rentals.
