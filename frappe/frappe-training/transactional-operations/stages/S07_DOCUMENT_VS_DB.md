# S07. Сравнить Document API и прямое изменение БД

К S06 Controller Rental уже защищает жизненно важный контракт:

```text
Planned → Active
только через issue()

Active → Returned
только через return_equipment()
```

Теперь нужно увидеть, что прямой Database API имеет другую семантику и способен эту защиту обойти.

---

## 1. Взять отдельный контрольный Rental

Используйте Rental `direct_db` из S00.

Он принадлежит:

```text
operator-b@example.test
```

и должен всё ещё иметь:

```text
status = Planned
Equipment Movement = 0
```

Проверьте:

```bash
bench --site rental.localhost console
```

```python
rental_name = "ВАШ_RENTAL_DIRECT_DB"

print(frappe.db.get_value("Rental", rental_name, "status"))
print(frappe.db.count("Equipment Movement", {"rental": rental_name}))
```

---

## 2. Попробовать обычный Document API

Под Administrator загрузите Rental:

```python
rental = frappe.get_doc("Rental", rental_name)
rental.status = "Active"
rental.save()
```

Ожидается ошибка Controller:

```text
Rental status must be changed through the corresponding operation.
```

Почему:

```text
Document.save()
→ validate()
→ validate_status_transition()
→ переход без issue() отклонён
```

Проверьте persisted state:

```python
frappe.db.get_value("Rental", rental_name, "status")
```

Остаётся:

```text
Planned
```

---

## 3. Выполнить прямой set_value

Теперь выполните технический эксперимент:

```python
frappe.db.set_value(
    "Rental",
    rental_name,
    "status",
    "Active",
)

frappe.db.commit()
```

Перечитайте:

```python
print(frappe.db.get_value("Rental", rental_name, "status"))
print(frappe.db.count("Equipment Movement", {"rental": rental_name}))
```

Ожидается противоречивое состояние:

```text
Rental = Active
Equipment Movement = 0
```

Controller не остановил изменение.

---

## 4. Почему validate не сработал

Официальная Database API определяет `frappe.db.set_value()` как прямое изменение поля в БД и отдельно предупреждает:

```text
validate
on_update
```

обычные ORM triggers не вызываются.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#frappedbset_value

Это принципиально другая семантика по сравнению с:

```python
doc.save()
```

который выполняет permission checks и Document lifecycle.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/document#docsave

---

## 5. Это не делает set_value запрещённым API

Неправильный вывод:

```text
frappe.db.set_value использовать нельзя
```

Правильный вопрос:

```text
нужно ли в этой операции пройти Document lifecycle?
```

Для текущего изменения Rental ответ:

```text
да
```

потому что переход состояния связан с:

```text
permission boundary
transition validation
созданием Equipment Movement
```

Поэтому обычный бизнес-путь — `issue()` / `return_equipment()`.

Прямой Database API подходит для технических изменений, где обход lifecycle является осознанной частью задачи.

---

## 6. Performance не оправдывает обход контракта

Нельзя заменять:

```python
rental.save()
```

на:

```python
frappe.db.set_value(...)
```

только потому, что второй вызов выглядит проще или потенциально дешевле.

Если производительность действительно является проблемой:

```text
сначала измерить
→ понять стоимость
→ сохранить необходимую семантику
→ только затем менять реализацию
```

Это продолжает принцип из предыдущего практикума Data Access & Reporting.

---

## 7. Восстановить контрольный Rental

Текущая запись была намеренно повреждена низкоуровневым экспериментом.

Восстановите её тем же техническим путём:

```python
frappe.db.set_value(
    "Rental",
    rental_name,
    "status",
    "Planned",
)
frappe.db.commit()
```

Проверьте:

```python
print(frappe.db.get_value("Rental", rental_name, "status"))
print(frappe.db.count("Equipment Movement", {"rental": rental_name}))
```

Ожидается:

```text
Planned
0
```

Завершите console.

---

## 8. Пройти правильный путь

Войдите как:

```text
operator-b@example.test
```

Откройте Rental `direct_db`.

Нажмите **Issue**.

Теперь ожидается:

```text
Rental = Active
Issue Movement = полный набор
```

Затем нажмите **Return**:

```text
Rental = Returned
Issue Movement = полный набор
Return Movement = полный набор
```

То есть один и тот же итоговый `status` имеет смысл только вместе с операцией, которая его создала.

---

## 9. Проверить исходники

S07 не требует изменения App.

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Вывод должен быть пустым.

Все действия этапа выполнялись только над Site-owned контрольными данными.

---

## 10. Контрольная точка S07

Ученик должен различать:

```text
Document API
→ permissions
→ validate / on_update
→ бизнес-lifecycle

Database API direct update
→ техническое изменение БД
→ обычные ORM triggers не вызываются
```

И понимать, почему текущий Rental меняется через controller commands, а не прямой `set_value`.

Следующий этап закрепит итоговые контракты автоматическими проверками: [`S08_AUTOMATED_TESTS.md`](S08_AUTOMATED_TESTS.md).