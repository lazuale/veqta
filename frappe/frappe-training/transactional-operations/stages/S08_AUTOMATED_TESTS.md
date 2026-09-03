# S08. Закрепить транзакционные бизнес-контракты тестами

К S08 итоговый App добавил новые собственные правила:

```text
новый Rental стартует только Planned
Planned → Active только через issue()
Active → Returned только через return_equipment()
Issue/Return создают Movement
Movement нельзя создавать прикладной ролью вручную
```

Именно эти контракты нужно тестировать.

Не нужно тестировать сам Frappe на предмет того, умеет ли request handler выполнять rollback при необработанном исключении. Это штатное поведение Framework, которое S03 уже проверил наблюдением.

---

## 1. Сначала обновить старые тестовые helpers

Первый и третий практикумы создавались до появления явных команд Issue/Return.

Поэтому в `test_rental.py` есть тестовые setup-пути вида:

```python
self.make_rental(status="Active").insert()
```

После S06 это уже неверный способ получить Active Rental.

Новый контракт:

```text
создать Planned
→ issue()
→ Active

создать Planned
→ issue()
→ return_equipment()
→ Returned
```

Старые тесты нужно **адаптировать**, а не ослаблять новую validation ради совместимости с тестовым helper.

---

## 2. Добавить helper перехода через реальные команды

В существующий `IntegrationTestRental` добавьте helper:

```python
def insert_rental(self, *, status="Planned", **kwargs):
    rental = self.make_rental(status="Planned", **kwargs).insert()

    if status in {"Active", "Returned"}:
        rental.issue()

    if status == "Returned":
        rental.return_equipment()

    return rental
```

Теперь тест, которому нужен Active Rental, должен использовать:

```python
rental = self.insert_rental(
    status="Active",
    start_date="2027-01-10",
    end_date="2027-01-12",
)
```

а не вставлять `Active` напрямую.

---

## 3. Обновить conflict-тесты первого практикума

### Overlap

Было по смыслу:

```python
active = self.make_rental(status="Active", ...).insert()
conflict = self.make_rental(status="Active", ...)
conflict.insert()
```

Теперь:

```python
self.insert_rental(
    status="Active",
    start_date="2026-11-10",
    end_date="2026-11-12",
)

conflict = self.make_rental(
    start_date="2026-11-11",
    end_date="2026-11-13",
).insert()

with self.assertRaises(frappe.ValidationError):
    conflict.issue()
```

Это даже точнее отражает реальный бизнес-путь: конфликт возникает не при создании Planned Rental, а когда его пытаются сделать Active.

Аналогично обновите:

```text
test_touching_active_periods_are_rejected
test_non_overlapping_active_rental_is_allowed
test_planned_overlap_is_allowed
test_active_rental_does_not_conflict_with_itself
```

Active state в setup теперь получается через `issue()`.

---

## 4. Обновить reporting-тесты

Класс `IntegrationTestRentalReporting` из предыдущего практикума также создаёт Rentals разных состояний для расчёта utilization.

Добавьте в него аналогичный helper:

```python
def insert_rental(self, *, status="Planned", **kwargs):
    rental = self.make_rental(status="Planned", **kwargs).insert()

    if status in {"Active", "Returned"}:
        rental.issue()

    if status == "Returned":
        rental.return_equipment()

    return rental
```

Все setup-места, где тесту нужен persisted `Active` или `Returned`, переведите на этот helper.

Не меняйте сам расчёт utilization: новая транзакционная модель не меняет его контракт.

---

## 5. Добавить отдельный класс transaction-тестов

В тот же `test_rental.py` добавьте новый класс:

```python
class IntegrationTestRentalTransactions(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

        self.customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Transaction Test Customer",
            }
        ).insert()

        self.equipment_a = frappe.get_doc(
            {
                "doctype": "Equipment",
                "equipment_name": "Transaction Equipment A",
                "equipment_type": "Tool",
            }
        ).insert()

        self.equipment_b = frappe.get_doc(
            {
                "doctype": "Equipment",
                "equipment_name": "Transaction Equipment B",
                "equipment_type": "Tool",
            }
        ).insert()

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def make_rental(self, *, equipment=None):
        equipment = equipment or [self.equipment_a.name, self.equipment_b.name]

        return frappe.get_doc(
            {
                "doctype": "Rental",
                "customer": self.customer.name,
                "start_date": "2027-06-01",
                "end_date": "2027-06-03",
                "status": "Planned",
                "items": [{"equipment": name} for name in equipment],
            }
        )
```

Если в файле уже есть общий helper создания Users, переиспользуйте его вместо копирования.

---

## 6. Новый Rental обязан стартовать Planned

Добавьте:

```python
def test_new_rental_cannot_start_active(self):
    rental = self.make_rental()
    rental.status = "Active"

    with self.assertRaises(frappe.ValidationError):
        rental.insert()
```

Это защищает серверную границу, которую UI read-only сам по себе не гарантирует.

---

## 7. Прямой переход через save запрещён

```python
def test_direct_issue_status_change_is_rejected(self):
    rental = self.make_rental().insert()
    rental.status = "Active"

    with self.assertRaises(frappe.ValidationError):
        rental.save()
```

Отдельно для Return:

```python
def test_direct_return_status_change_is_rejected(self):
    rental = self.make_rental().insert()
    rental.issue()
    rental.reload()
    rental.status = "Returned"

    with self.assertRaises(frappe.ValidationError):
        rental.save()
```

---

## 8. Успешный Issue создаёт полный набор Movement

```python
def test_issue_creates_one_movement_per_equipment(self):
    rental = self.make_rental().insert()
    rental.issue()
    rental.reload()

    self.assertEqual(rental.status, "Active")

    movements = frappe.get_all(
        "Equipment Movement",
        filters={
            "rental": rental.name,
            "movement_type": "Issue",
        },
        pluck="equipment",
    )

    self.assertEqual(
        set(movements),
        {self.equipment_a.name, self.equipment_b.name},
    )
```

Проверяется собственный контракт App:

```text
какие Movement должны быть созданы
```

а не внутреннее количество SQL-запросов Framework.

---

## 9. Повторный Issue запрещён

```python
def test_issue_cannot_run_twice(self):
    rental = self.make_rental().insert()
    rental.issue()

    with self.assertRaises(frappe.ValidationError):
        rental.issue()
```

После первого вызова status уже `Active`.

---

## 10. Return создаёт полный набор Movement

```python
def test_return_creates_one_movement_per_equipment(self):
    rental = self.make_rental().insert()
    rental.issue()
    rental.return_equipment()
    rental.reload()

    self.assertEqual(rental.status, "Returned")

    returned = frappe.get_all(
        "Equipment Movement",
        filters={
            "rental": rental.name,
            "movement_type": "Return",
        },
        pluck="equipment",
    )

    self.assertEqual(
        set(returned),
        {self.equipment_a.name, self.equipment_b.name},
    )
```

---

## 11. Повторный Return запрещён

```python
def test_return_cannot_run_twice(self):
    rental = self.make_rental().insert()
    rental.issue()
    rental.return_equipment()

    with self.assertRaises(frappe.ValidationError):
        rental.return_equipment()
```

---

## 12. Проверить permission boundary команды

Используйте существующий helper `make_user("Rental Operator")` или добавьте эквивалентный в текущий test class.

Создайте Rental под operator A:

```python
operator_a = self.make_user("Rental Operator")
operator_b = self.make_user("Rental Operator")

with self.set_user(operator_a):
    rental = self.make_rental().insert()
```

Теперь:

```python
with self.set_user(operator_b):
    with self.assertRaises(frappe.PermissionError):
        rental.issue()
```

После предыдущего практикума `If Owner` является частью metadata Rental, поэтому чужой оператор не получает `write` на этот Document.

---

## 13. Проверить system-generated Movement permissions

Metadata-контракт:

```python
def test_movement_is_not_directly_creatable_by_application_roles(self):
    manager = self.make_user("Rental Manager")

    self.assertTrue(
        frappe.has_permission(
            "Equipment Movement",
            "read",
            user=manager,
        )
    )

    self.assertFalse(
        frappe.has_permission(
            "Equipment Movement",
            "create",
            user=manager,
        )
    )
```

Для оператора ожидается отсутствие и Read, и Create.

Не нужно тестировать сам механизм `ignore_permissions=True`; нужно тестировать публичный контракт приложения:

```text
прикладная роль не создаёт Movement напрямую
но issue()/return_equipment() формируют журнал
```

---

## 14. Почему нет теста «ошибка на втором Movement делает rollback»

S03 уже показал автоматический rollback обычного POST request.

Этот rollback выполняет Frappe request handler, а не `rental_training`.

Чтобы проверить его автоматически, пришлось бы строить тест вокруг HTTP request boundary и по сути тестировать стандартную транзакционную модель Framework.

В текущем App нет собственного transaction manager, который нужно защищать таким тестом.

Поэтому автоматические тесты концентрируются на том, что добавило приложение само:

```text
разрешённые переходы
permission boundary
набор Movement
запрет ручного журнала
```

---

## 15. Запустить Rental tests

```bash
cd ~/frappe/rental-training-bench

bench --site rental.localhost run-tests \
  --doctype Rental \
  --app rental_training
```

Если ваша версия Bench не принимает такое сочетание параметров, используйте проверенный в предыдущих практикумах способ запуска модуля `test_rental.py`.

Важно получить один результат:

```text
старые data/lifecycle/reporting-контракты
+
новые transaction-контракты
→ проходят вместе
```

---

## 16. Проверить отсутствие прямых Active/Returned inserts в тестах

Поиск:

```bash
grep -nE \
  'status=["'"'](Active|Returned)["'"']|"status": ["'"'](Active|Returned)["'"']' \
  apps/rental_training/rental_training/rental_training/doctype/rental/test_rental.py
```

Не каждый найденный текст является ошибкой: часть может находиться в assertions или намеренном negative test.

Но persisted setup данных не должен больше создавать `Active`/`Returned` напрямую в обход команд.

---

## 17. Зафиксировать tests

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short

git diff -- \
  rental_training/rental_training/doctype/rental/test_rental.py
```

После проверки:

```bash
git add \
  rental_training/rental_training/doctype/rental/test_rental.py

git commit -m "test: cover rental transaction contracts"
```

Проверьте чистое дерево.

---

## 18. Контрольная точка S08

Тесты должны защищать:

```text
новый Rental = Planned
прямые transitions запрещены
Issue создаёт полный Issue journal
Return создаёт полный Return journal
повторные команды запрещены
чужой operator не запускает команду
Movement не создаётся вручную прикладной ролью
```

Старые тесты при этом используют новые реальные команды для setup `Active`/`Returned` состояния и не требуют ослаблять Controller.

Следующий этап: [`S09_APP_STATE_DELIVERY.md`](S09_APP_STATE_DELIVERY.md).