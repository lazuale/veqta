# S05. Увидеть границу пойманного исключения

S04 показал явный способ разрезать транзакцию — ручной `commit()`.

Есть менее очевидная ошибка:

```text
внутри операции что-то сломалось
но код поймал исключение
и вернул обычный успешный response
```

Для Framework такой request уже не выглядит неуспешным.

---

## 1. Взять отдельный Rental

Используйте контрольный Rental `caught_exception` из S00.

Проверьте исходное состояние:

```bash
bench --site rental.localhost console
```

```python
rental_name = "ВАШ_RENTAL_CAUGHT_EXCEPTION"

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

## 2. Убедиться, что App чист

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Вывод должен быть пустым.

---

## 3. Временно создать ошибку внутри Movement

Снова измените `create_equipment_movements()` только для эксперимента:

```python
def create_equipment_movements(self, movement_type):
    movement_at = now_datetime()

    for index, row in enumerate(self.items, start=1):
        frappe.get_doc(
            {
                "doctype": "Equipment Movement",
                "equipment": row.equipment,
                "rental": self.name,
                "movement_type": movement_type,
                "movement_at": movement_at,
            }
        ).insert(ignore_permissions=True)

        if movement_type == "Issue" and index == 1:
            frappe.throw(_("Caught exception experiment."))
```

Пока это тот же тип ошибки, что в S03.

Но теперь изменим сам `issue()`.

---

## 4. Временно проглотить исключение

На время эксперимента замените конец `issue()`:

```python
@frappe.whitelist(methods=["POST"])
def issue(self):
    self.reload()
    self.check_permission("write")

    if self.status != "Planned":
        frappe.throw(_("Only a Planned Rental can be issued."))

    self.flags.rental_operation = "issue"
    self.status = "Active"
    self.save()

    try:
        self.create_equipment_movements("Issue")
    except Exception:
        return {"ok": False}

    return {"ok": True, "status": self.status}
```

Ключевое отличие от S03:

```text
исключение больше не выходит из controller method
```

Логирование здесь специально не добавляется: оно не относится к проверяемой транзакционной границе.

Не добавляйте `rollback()`.

Не коммитьте экспериментальный код.

---

## 5. Вызвать Issue через Form

Войдите как:

```text
operator-a@example.test
```

Откройте Rental `caught_exception` и нажмите **Issue**.

Серверный method вернёт:

```python
{"ok": False}
```

Но request как Python-выполнение завершился без необработанного исключения.

UI текущего минимального button code не интерпретирует бизнес-смысл `ok=False`; promise считается успешно завершённым и Form перезагрузится.

Это отдельный полезный сигнал:

```text
transport success
≠
business success
```

---

## 6. Проверить БД

Откройте console:

```bash
bench --site rental.localhost console
```

```python
rental_name = "ВАШ_RENTAL_CAUGHT_EXCEPTION"

print(frappe.db.get_value("Rental", rental_name, "status"))
print(
    frappe.get_all(
        "Equipment Movement",
        filters={"rental": rental_name},
        fields=["name", "equipment", "movement_type"],
        order_by="name asc",
    )
)
```

Ожидается повреждённый смысл:

```text
Rental = Active
Issue Movement = 1 из 2
```

Ручного commit в нашем коде не было.

Почему данные всё равно сохранились:

```text
request завершился успешно
→ Frappe выполнил обычный commit в конце request
```

---

## 7. Что говорит Database API

Официальная документация предупреждает: если приложение само ловит исключение, database abstraction больше не знает, что операция должна считаться неуспешной; ответственность за rollback переходит к коду приложения.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#database-transaction-model

Для текущего Issue нам не нужно продолжать request после ошибки.

Поэтому правильная модель проще:

```text
ошибка отменяет Issue
→ не скрывать её
→ exception выходит наружу
→ Frappe rollback request
```

---

## 8. Почему не добавляем except + rollback без требования

Можно написать:

```python
try:
    ...
except Exception:
    frappe.db.rollback()
    raise
```

Но если исключение всё равно будет повторно выброшено и request завершится ошибкой, обычный handler Framework уже сделает rollback.

Такой код лишь дублирует транзакционную границу.

Явный rollback нужен, когда приложение действительно:

```text
ловит ошибку
и
продолжает request по осмысленному сценарию
```

Такого требования у Rental Issue нет.

---

## 9. Вернуть правильный код

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git restore \
  rental_training/rental_training/doctype/rental/rental.py
```

Проверьте:

```bash
git status --short
```

Должно быть чисто.

---

## 10. Восстановить только контрольные данные

Поскольку успешный request уже закоммитил повреждённый набор, восстановите учебную запись технически:

```bash
bench --site rental.localhost console
```

```python
frappe.set_user("Administrator")
rental_name = "ВАШ_RENTAL_CAUGHT_EXCEPTION"

frappe.db.delete("Equipment Movement", {"rental": rental_name})
frappe.db.set_value("Rental", rental_name, "status", "Planned")
frappe.db.commit()

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

## 11. Повторить Issue с правильным кодом

Теперь выполните обычную Issue-команду.

Ожидается:

```text
Rental = Active
Issue Movement = полный набор
```

---

## 12. Сравнить три сценария

### Штатный rollback

```text
write
write
exception наружу
→ rollback
```

### Ручной commit

```text
write
COMMIT
exception наружу
→ уже зафиксированная часть остаётся
```

### Пойманное исключение

```text
write
write
exception пойман
обычный return
→ request success
→ commit
```

Это три разных причины результата, хотя во всех случаях «внутри кода была ошибка».

---

## 13. Контрольная точка S05

Готово, если:

```text
ученик видел partial state без ручного commit
понимает, почему request считался успешным
в итоговом issue() нет except, скрывающего ошибку
в итоговом issue() нет ручного rollback
временный код удалён
контрольный Rental восстановлен и корректно выдан
Git App чист
```

Следующий этап больше ничего намеренно не ломает. Мы добавим вторую реальную бизнес-команду на той же транзакционной модели: [`S06_RETURN_COMMAND.md`](S06_RETURN_COMMAND.md).