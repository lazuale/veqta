# S03. Увидеть автоматический rollback на живой операции

S02 дал рабочую атомарную команду Issue.

Теперь её нужно намеренно оборвать **после первой записи Movement**, но до успешного завершения request.

Цель этапа — увидеть факт:

```text
save() и insert() уже выполнялись
но commit ещё не произошёл
```

---

## 1. Взять отдельный Rental для опыта

Используйте контрольный Rental `rollback` из S00.

Перед экспериментом проверьте:

```bash
bench --site rental.localhost console
```

```python
rental_name = "ВАШ_RENTAL_ROLLBACK"

print(frappe.db.get_value("Rental", rental_name, "status"))
print(
    frappe.db.count(
        "Equipment Movement",
        {"rental": rental_name},
    )
)
```

Ожидается:

```text
Planned
0
```

Завершите console.

---

## 2. Убедиться, что Git чист

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

После S02 вывод должен быть пустым.

Это важно: сейчас мы будем временно портить рабочую реализацию и затем вернём ровно зафиксированное состояние.

---

## 3. Временно добавить ошибку после первого Movement

Откройте `rental.py`.

На время эксперимента измените `create_equipment_movements()` так:

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
            frappe.throw(_("Rollback experiment after first Movement."))
```

Не добавляйте никакой `commit()`.

Не коммитьте этот код в Git.

Проверьте временный diff:

```bash
git -C apps/rental_training diff -- \
  rental_training/rental_training/doctype/rental/rental.py
```

---

## 4. Вызвать Issue через обычную Form

Войдите как:

```text
operator-a@example.test
```

Откройте Rental `rollback`.

Нажмите **Issue**.

Что успеет произойти внутри Python до исключения:

```text
self.status = Active
self.save()

первый Equipment Movement.insert()

frappe.throw(...)
```

В интерфейсе ожидается ошибка request.

---

## 5. Проверить состояние после ошибки

Откройте console под Administrator:

```bash
bench --site rental.localhost console
```

Проверьте Rental:

```python
rental_name = "ВАШ_RENTAL_ROLLBACK"

frappe.db.get_value("Rental", rental_name, "status")
```

Ожидается:

```text
Planned
```

Проверьте Movement:

```python
frappe.get_all(
    "Equipment Movement",
    filters={"rental": rental_name},
    fields=["name", "equipment", "movement_type"],
)
```

Ожидается:

```python
[]
```

Хотя первый `insert()` реально был вызван, запись не пережила rollback транзакции.

Завершите console.

---

## 6. Что сделал Framework

Официальная Database API Frappe описывает для web request:

```text
успешный POST / PUT с DB writes
→ commit в конце request

необработанное исключение
→ rollback транзакции
```

`frm.call()` выполняет POST по умолчанию.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#database-transaction-model

В Frappe v16.33.0 `frappe/app.py` в ветке обработки исключения вызывает:

```python
db.rollback(chain=True)
```

Источник:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/app.py

То есть атомарность здесь не обеспечена нашим собственным transaction manager.

Мы просто **не мешаем** штатной транзакционной модели Framework.

---

## 7. Почему не нужно rollback вручную в issue()

Плохая реакция на этот этап:

```python
try:
    ...
except Exception:
    frappe.db.rollback()
    raise
```

Для обычного request, который должен целиком завершиться ошибкой, Frappe уже владеет транзакционной границей.

Добавлять ручное управление только ради дублирования Framework не нужно.

Явный rollback имеет смысл, когда код намеренно ловит ошибку и продолжает выполнение либо использует отдельную более узкую транзакционную стратегию. В текущем Issue такого требования нет.

---

## 8. Удалить экспериментальную ошибку

Верните `rental.py` к зафиксированной версии S02:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git restore \
  rental_training/rental_training/doctype/rental/rental.py
```

Проверьте:

```bash
git status --short
```

Вывод должен быть пустым.

---

## 9. Повторно выполнить Issue после восстановления кода

Теперь снова войдите как `operator-a@example.test` и нажмите **Issue** на том же Rental `rollback`.

На этот раз ожидается успех:

```text
Rental = Active
Issue Movement = количество Equipment в Rental
```

После проверки этот Rental больше не используется для следующих destructive experiments.

---

## 10. Контрольная точка S03

Ученик должен фактически увидеть:

```text
до ошибки:
  Rental.save() вызван
  Movement.insert() вызван

после необработанной ошибки request:
  Rental снова Planned
  Movement отсутствует
```

И понять причину:

```text
DB write
≠
commit
```

Исходники App снова чистые и рабочие.

Следующий этап покажет, что произойдёт, если вручную разрезать эту транзакцию: [`S04_MANUAL_COMMIT.md`](S04_MANUAL_COMMIT.md).