# S00. Проверить исходное состояние и подготовить контрольные Rentals

Практикум не создаёт новый Bench, App или предметную модель. Он продолжает текущее `rental_training` после предыдущих маршрутов VEQTA Learn.

На S00 нужно получить две вещи:

```text
1. подтверждённое состояние App
2. отдельные рабочие данные, которые можно безопасно ломать в экспериментах
```

Контрольные Users и Documents остаются данными Site и не попадают в App.

---

## 1. Проверить Bench и версию Framework

Перейдите в существующий Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте версии:

```bash
bench version --format plain
```

Контрольная линия практикума:

```text
frappe 16.33.0
```

`rental_training` должен работать на той же версии, на которой завершён предыдущий маршрут.

Если Framework уже обновлён на другой patch v16, не откатывайте его автоматически. Сначала нужно отдельно перепроверить версионно-зависимые места практикума.

---

## 2. Проверить установленные Apps

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается как минимум:

```text
frappe
rental_training
```

Проверьте, что исходная модель уже принадлежит App:

```bash
test -f apps/rental_training/rental_training/rental_training/doctype/equipment/equipment.json \
  && echo 'Equipment: OK'

test -f apps/rental_training/rental_training/rental_training/doctype/customer/customer.json \
  && echo 'Customer: OK'

test -f apps/rental_training/rental_training/rental_training/doctype/rental/rental.json \
  && echo 'Rental: OK'

test -f apps/rental_training/rental_training/rental_training/doctype/rental_item/rental_item.json \
  && echo 'Rental Item: OK'
```

На S00 `Equipment Movement` ещё не должен существовать:

```bash
test ! -d \
  apps/rental_training/rental_training/rental_training/doctype/equipment_movement \
  && echo 'Equipment Movement: not created yet'
```

---

## 3. Проверить Git App

```bash
git -C apps/rental_training status --short
```

Перед новым практикумом рабочее дерево должно быть чистым.

Зафиксируйте текущую точку:

```bash
git -C apps/rental_training rev-parse HEAD
```

Это baseline учебного App до транзакционных изменений.

---

## 4. Проверить существующие правила Rental

Откройте Controller:

```bash
sed -n '1,320p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.py
```

В нём уже должны существовать правила первого практикума:

```text
end_date >= start_date
Equipment не повторяется внутри Rental
Equipment не пересекается в Active Rentals
```

Новый маршрут их не заменяет.

Транзакционная операция будет строиться **поверх существующего Controller**.

---

## 5. Проверить permission boundary из предыдущего практикума

Откройте console:

```bash
bench --site rental.localhost console
```

Выполните:

```python
meta = frappe.get_meta("Rental")

for permission in meta.permissions:
    if permission.role in {"Rental Operator", "Rental Manager"}:
        print(
            permission.role,
            "read=", permission.read,
            "write=", permission.write,
            "create=", permission.create,
            "if_owner=", permission.if_owner,
            "report=", permission.report,
        )
```

Для последовательного прохождения Learn ожидается смысл:

```text
Rental Operator
→ Read/Create/Write
→ If Owner = yes

Rental Manager
→ Read/Create/Write/Delete
→ Report = yes
```

Текущий практикум не переучивает `If Owner`. Он использует уже существующую границу, чтобы команда `issue()` могла проверяться на собственном и чужом Rental.

Завершите console:

```python
exit()
```

---

## 6. Проверить учебных Users

Для маршрута нужны:

```text
operator-a@example.test
operator-b@example.test
manager@example.test
```

Они уже использовались в предыдущем практикуме.

Проверьте:

```bash
bench --site rental.localhost console
```

```python
for user in [
    "operator-a@example.test",
    "operator-b@example.test",
    "manager@example.test",
]:
    print(user, bool(frappe.db.exists("User", user)))
```

Все три результата должны быть `True`.

Если Users отсутствуют, завершите подготовительный этап предыдущего практикума вместо создания второй параллельной схемы учебных пользователей.

---

## 7. Создать отдельный Customer для транзакционных опытов

Оставаясь в console:

```python
frappe.set_user("Administrator")

customer = frappe.get_doc(
    {
        "doctype": "Customer",
        "customer_name": "Transactional Test Customer",
        "email": "transactions@example.test",
    }
).insert()

print("Customer:", customer.name)
```

Сохраните фактический `name` из вывода.

Не рассчитывайте, что это обязательно будет `CUST-00003` или другой конкретный номер.

---

## 8. Создать девять отдельных Equipment

Выполните:

```python
equipment = []

for number in range(1, 10):
    doc = frappe.get_doc(
        {
            "doctype": "Equipment",
            "equipment_name": f"Transaction Equipment {number:02d}",
            "equipment_type": "Tool",
            "serial_number": f"TX-{number:03d}",
        }
    ).insert()
    equipment.append(doc.name)

print(equipment)
```

Нам нужны разные Equipment, чтобы активные Rentals из одного эксперимента не создавали ложные конфликты в другом.

---

## 9. Создать контрольные Rentals

Используем пять отдельных Rental:

```text
A → обычная успешная Issue + будущий Return
B → rollback experiment
C → manual commit experiment
D → caught exception experiment
E → direct DB update experiment
```

Создайте helper в console:

```python
def make_rental(user, equipment_names, start_date, end_date):
    frappe.set_user(user)
    doc = frappe.get_doc(
        {
            "doctype": "Rental",
            "customer": customer.name,
            "start_date": start_date,
            "end_date": end_date,
            "status": "Planned",
            "items": [{"equipment": name} for name in equipment_names],
        }
    ).insert()
    return doc.name
```

Создайте Rentals:

```python
rentals = {
    "success": make_rental(
        "operator-a@example.test",
        equipment[0:2],
        "2026-10-01",
        "2026-10-03",
    ),
    "rollback": make_rental(
        "operator-a@example.test",
        equipment[2:4],
        "2026-10-05",
        "2026-10-07",
    ),
    "manual_commit": make_rental(
        "operator-a@example.test",
        equipment[4:6],
        "2026-10-09",
        "2026-10-11",
    ),
    "caught_exception": make_rental(
        "operator-a@example.test",
        equipment[6:8],
        "2026-10-13",
        "2026-10-15",
    ),
    "direct_db": make_rental(
        "operator-b@example.test",
        equipment[8:9],
        "2026-10-17",
        "2026-10-18",
    ),
}

frappe.set_user("Administrator")
print(rentals)
```

Запишите фактические имена.

Они понадобятся в S02–S07.

---

## 10. Проверить owner и status

```python
frappe.get_all(
    "Rental",
    filters={"name": ["in", list(rentals.values())]},
    fields=["name", "owner", "status", "start_date", "end_date"],
    order_by="start_date asc",
)
```

Ожидаемый смысл:

```text
success / rollback / manual_commit / caught_exception
→ owner = operator-a@example.test
→ status = Planned

direct_db
→ owner = operator-b@example.test
→ status = Planned
```

Завершите console:

```python
exit()
```

---

## 11. Почему эти данные не fixtures

Customer, Equipment и Rental здесь существуют только для прохождения конкретного Site.

Они не являются обязательной конфигурацией приложения.

Проверьте Git:

```bash
git -C apps/rental_training status --short
```

После создания рабочих Documents вывод должен оставаться пустым.

Это снова подтверждает границу:

```text
исходники App
≠
рабочие данные Site
```

---

## 12. Контрольная точка S00

Перед S01 должно выполняться:

```text
Frappe v16.33.0 проверен
rental_training установлен
Git App чист
предыдущие Rental validations на месте
If Owner для Rental Operator на месте
созданы 5 отдельных контрольных Rentals
все контрольные Rentals = Planned
Equipment Movement ещё не существует
```

Следующий этап: [`S01_EQUIPMENT_MOVEMENT.md`](S01_EQUIPMENT_MOVEMENT.md).