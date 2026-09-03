# S04. Увидеть, как ручной commit ломает атомарность

S03 показал штатное поведение Frappe:

```text
необработанная ошибка
→ rollback всей незавершённой транзакции request
```

Теперь временно добавим `frappe.db.commit()` посередине той же операции и посмотрим, что именно изменится.

Это **контролируемый антипример**. Такой код не останется в App.

---

## 1. Взять отдельный Rental

Используйте контрольный Rental `manual_commit` из S00.

Проверьте:

```bash
bench --site rental.localhost console
```

```python
rental_name = "ВАШ_RENTAL_MANUAL_COMMIT"

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

## 2. Убедиться, что рабочий код чист

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Вывод должен быть пустым.

---

## 3. Временно разрезать транзакцию

Откройте `rental.py` и на время эксперимента измените `create_equipment_movements()`:

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
            frappe.db.commit()
            frappe.throw(_("Manual commit experiment."))
```

Порядок специально такой:

```text
Rental.save()
↓
первый Movement.insert()
↓
COMMIT
↓
исключение
```

Не коммитьте этот код в Git.

---

## 4. Выполнить Issue

Войдите как:

```text
operator-a@example.test
```

Откройте Rental `manual_commit` и нажмите **Issue**.

Request завершится ошибкой:

```text
Manual commit experiment.
```

На первый взгляд это похоже на S03.

Но состояние БД теперь принципиально другое.

---

## 5. Проверить Rental после ошибки

Откройте console:

```bash
bench --site rental.localhost console
```

```python
rental_name = "ВАШ_RENTAL_MANUAL_COMMIT"

frappe.db.get_value("Rental", rental_name, "status")
```

Ожидается:

```text
Active
```

Почему:

```text
self.save()
произошёл до ручного commit
```

и его изменение уже вошло в зафиксированную часть транзакции.

---

## 6. Проверить частичный журнал

```python
frappe.get_all(
    "Equipment Movement",
    filters={"rental": rental_name},
    fields=["name", "equipment", "movement_type", "movement_at"],
    order_by="name asc",
)
```

Для Rental с двумя Equipment ожидается одна строка:

```text
Issue Movement = 1 из 2
```

Получилось состояние, которое бизнес-контракт запрещал:

```text
Rental = Active
но Movement создан не для каждого Equipment
```

---

## 7. Почему последующий rollback не помогает

После исключения Frappe всё ещё выполняет rollback текущей транзакции request.

Но ручной:

```python
frappe.db.commit()
```

уже завершил предыдущую транзакцию.

Rollback не может «отмотать» изменения через ранее выполненный commit.

Официальная Database API прямо определяет `frappe.db.commit()` как SQL `COMMIT` и отдельно отмечает, что в большинстве обычных случаев ручной commit не нужен.

Источник:

- https://docs.frappe.io/framework/user/en/api/database#frappedbcommit

---

## 8. Удалить сломанный код

Сначала верните исходник к версии S02:

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

Теперь App снова корректен, но Site-owned контрольные данные всё ещё намеренно повреждены.

---

## 9. Восстановить только контрольные данные

Для учебного восстановления используем Administrator и прямой Database API.

Это не обычная бизнес-операция, а техническая очистка после специально созданного partial commit.

Откройте console:

```bash
bench --site rental.localhost console
```

```python
frappe.set_user("Administrator")
rental_name = "ВАШ_RENTAL_MANUAL_COMMIT"

frappe.db.delete(
    "Equipment Movement",
    {"rental": rental_name},
)

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

### Почему здесь допустим прямой DB update

Мы не реализуем бизнес-команду Rental.

Мы вручную ремонтируем **только учебные данные**, которые сами намеренно сломали низкоуровневым экспериментом.

На S07 прямой DB update будет разобран отдельно как механизм с другой семантикой.

---

## 10. Снова выполнить Issue нормальным кодом

После восстановления исходников и данных вызовите Issue для этого Rental ещё раз.

Ожидается нормальный контракт:

```text
Rental = Active
Issue Movement = 2 из 2
```

---

## 11. Что именно доказал эксперимент

Сравните два этапа.

### S03

```text
save
insert
throw
↓
rollback
↓
ничего не осталось
```

### S04

```text
save
insert
COMMIT
throw
↓
rollback
↓
зафиксированная часть осталась
```

То есть ручной commit — не «усиление надёжности».

Он **меняет границу бизнес-операции**.

---

## 12. Контрольная точка S04

Готово, если ученик увидел реальное состояние:

```text
ошибка request была
но Rental и первый Movement сохранились из-за commit
```

После завершения этапа:

```text
в исходниках нет frappe.db.commit()
временного frappe.throw нет
Git App чист
контрольный Rental восстановлен и затем корректно выдан
```

Следующий этап покажет другой способ лишить Framework возможности автоматически выбрать rollback: [`S05_CAUGHT_EXCEPTION.md`](S05_CAUGHT_EXCEPTION.md).