# S10. Проверить транзакционный App на новом чистом Site

S09 подтвердил, какие части обязательной модели находятся в исходниках `rental_training`.

Теперь нужно установить тот же App на новый Site и убедиться, что транзакционный сценарий не зависит от скрытого состояния `rental.localhost`.

---

## 1. Проверить зафиксированное состояние App

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
git -C apps/rental_training rev-parse HEAD
```

Рабочее дерево должно быть чистым.

Скопируйте текущий commit SHA App в свои заметки.

Именно это состояние будет проверяться на новом Site.

---

## 2. Создать новый Site

Используем:

```text
rental-transactions-clean.localhost
```

Проверьте, что каталога ещё нет:

```bash
test ! -d sites/rental-transactions-clean.localhost \
  && echo 'clean Site is absent' \
  || echo 'STOP: Site already exists'
```

Создайте Site:

```bash
bench new-site rental-transactions-clean.localhost \
  --db-root-username frappe_admin
```

Не используйте `--force` для повторного использования старого Site.

---

## 3. Проверить состояние до установки App

```bash
bench --site rental-transactions-clean.localhost list-apps -f text
```

Ожидается:

```text
frappe
```

Проверьте отсутствие нового DocType:

```bash
bench --site rental-transactions-clean.localhost console
```

```python
print(frappe.db.exists("DocType", "Equipment Movement"))
print(frappe.db.exists("DocType", "Rental"))
```

До установки `rental_training` ожидается отсутствие обоих учебных DocTypes.

Завершите console.

---

## 4. Установить rental_training

```bash
bench --site rental-transactions-clean.localhost install-app rental_training
```

Проверьте:

```bash
bench --site rental-transactions-clean.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

---

## 5. Проверить Equipment Movement

Откройте console:

```bash
bench --site rental-transactions-clean.localhost console
```

```python
frappe.get_meta("Equipment Movement").as_dict().get("module")
```

Ожидается:

```text
Rental Training
```

Проверьте поля:

```python
meta = frappe.get_meta("Equipment Movement")

for fieldname in [
    "equipment",
    "rental",
    "movement_type",
    "movement_at",
]:
    field = meta.get_field(fieldname)
    print(fieldname, field.fieldtype, field.options)
```

Смысл:

```text
equipment     → Link → Equipment
rental        → Link → Rental
movement_type → Select
movement_at   → Datetime
```

---

## 6. Проверить permissions Movement

```python
for permission in meta.permissions:
    print(
        permission.role,
        "read=", permission.read,
        "create=", permission.create,
        "write=", permission.write,
        "delete=", permission.delete,
    )
```

Ожидается:

```text
Rental Manager
→ Read = 1
→ Create/Write/Delete = 0
```

Проверьте существование роли:

```python
frappe.db.exists("Role", "Rental Manager")
```

Role должна появиться из обязательной metadata App, без ручного создания через Desk.

---

## 7. Проверить Rental metadata

```python
rental_meta = frappe.get_meta("Rental")
status_field = rental_meta.get_field("status")

print("status.read_only =", status_field.read_only)
```

Ожидается:

```text
status.read_only = 1
```

Проверьте permissions, которые накопились к предыдущим маршрутам:

```python
for permission in rental_meta.permissions:
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

Новый практикум не должен случайно потерять контракты предыдущего.

---

## 8. Проверить отсутствие рабочих данных

Сразу после install-app:

```python
for doctype in [
    "Equipment",
    "Customer",
    "Rental",
    "Equipment Movement",
]:
    print(doctype, frappe.db.count(doctype))
```

Не ориентируйтесь на внутренние системные DocTypes Frappe.

Для учебных бизнес-DocTypes ожидается отсутствие рабочих записей:

```text
0
```

Если записи уже есть, Site не является чистой контрольной площадкой.

---

## 9. Создать минимальные данные

Оставаясь Administrator:

```python
customer = frappe.get_doc(
    {
        "doctype": "Customer",
        "customer_name": "Clean Transaction Customer",
    }
).insert()

equipment_a = frappe.get_doc(
    {
        "doctype": "Equipment",
        "equipment_name": "Clean Transaction Equipment A",
        "equipment_type": "Tool",
    }
).insert()

equipment_b = frappe.get_doc(
    {
        "doctype": "Equipment",
        "equipment_name": "Clean Transaction Equipment B",
        "equipment_type": "Tool",
    }
).insert()

rental = frappe.get_doc(
    {
        "doctype": "Rental",
        "customer": customer.name,
        "start_date": "2027-07-01",
        "end_date": "2027-07-03",
        "status": "Planned",
        "items": [
            {"equipment": equipment_a.name},
            {"equipment": equipment_b.name},
        ],
    }
).insert()

print(rental.name)
```

Здесь Administrator используется только для минимальной smoke-проверки App state.

Permission boundary прикладного пользователя уже защищена автоматическими тестами S08.

---

## 10. Проверить серверную защиту status

Попробуйте:

```python
rental.status = "Active"
rental.save()
```

Ожидается ошибка:

```text
Rental status must be changed through the corresponding operation.
```

Перечитайте:

```python
rental.reload()
print(rental.status)
```

Ожидается:

```text
Planned
```

---

## 11. Выполнить Issue

```python
rental.issue()
rental.reload()

print(rental.status)
print(
    frappe.get_all(
        "Equipment Movement",
        filters={"rental": rental.name},
        fields=["equipment", "movement_type"],
        order_by="creation asc",
    )
)
```

Ожидается:

```text
Rental = Active
Issue Movement = 2
```

Поскольку console не является обычным web request, после smoke-проверки явно зафиксируйте текущие учебные данные:

```python
frappe.db.commit()
```

Это **не часть implementation `issue()`**. Мы вручную управляем интерактивной console-сессией.

---

## 12. Выполнить Return

```python
rental.reload()
rental.return_equipment()
rental.reload()

print(rental.status)
print(
    frappe.get_all(
        "Equipment Movement",
        filters={"rental": rental.name},
        fields=["equipment", "movement_type"],
        order_by="creation asc",
    )
)

frappe.db.commit()
```

Ожидается:

```text
Rental = Returned
Issue  × 2
Return × 2
```

Завершите console.

---

## 13. Проверить Form Script на чистом Site

Запустите Bench, если нужно:

```bash
bench start
```

Откройте:

```text
http://rental-transactions-clean.localhost:8000/app
```

Как Administrator откройте созданный Rental.

Для `Returned` кнопок перехода уже быть не должно.

При создании нового Planned Rental стандартная Form должна показывать read-only `Status` и кнопку **Issue** после сохранения.

Это подтверждает, что `rental.js` поставляется App, а не существовал только в browser cache исходного Site.

---

## 14. Запустить tests на чистом Site

Разрешите tests только на контрольном Site:

```bash
bench --site rental-transactions-clean.localhost set-config allow_tests 1 --parse
```

Запустите Rental tests тем же способом, который использовался на S08.

Ожидается совместное прохождение:

```text
первоначальные data invariants
permissions
reporting contracts
transaction contracts
```

---

## 15. Что именно доказал clean install

На новом Site не выполнялись вручную:

```text
создание Equipment Movement DocType
редактирование Rental.status metadata
вставка server methods
создание Form buttons
ручная настройка Movement permissions
```

Но после установки App всё это уже существует.

Следовательно:

```text
обязательная транзакционная модель
→ принадлежит rental_training
```

А конкретные:

```text
Customer
Equipment
Rental
Movement
```

появились только после создания рабочих данных.

---

## 16. Финальная граница практикума

Четвёртый маршрут заканчивается здесь.

Ученик должен уметь объяснить:

```text
одна бизнес-операция
→ может менять несколько Documents

save/insert
→ ещё не отдельный commit

необработанная ошибка request
→ rollback

ручной commit
→ меняет границу операции

пойманная ошибка
→ требует собственного решения о rollback

Document API
→ проходит lifecycle

прямой Database API
→ имеет другую семантику
```

Background jobs, `after_commit`, scheduler и внешние эффекты в этом практикуме намеренно не появлялись.

Следующая самостоятельная задача начнётся тогда, когда после успешной локальной транзакции потребуется долгая или внешняя работа.