# S06. Добавить атомарную команду Return

После S03–S05 правильная транзакционная модель Issue уже понятна:

```text
один request
→ Rental save
→ Movement inserts
→ один commit в конце
```

Теперь добавляем вторую реальную бизнес-операцию без новой инфраструктуры.

Требование:

> Возвратить Active Rental: перевести его в `Returned` и создать `Return` Movement для каждого Equipment одной транзакцией.

---

## 1. Расширить серверную защиту переходов

Откройте `rental.py`.

`validate_status_transition()` после S02 разрешает только:

```text
Planned → Active внутри issue()
```

Добавьте второй разрешённый переход:

```python
def validate_status_transition(self):
    if self.is_new():
        if self.status != "Planned":
            frappe.throw(_("A new Rental must start as Planned."))
        return

    previous = self.get_doc_before_save()

    if not previous or previous.status == self.status:
        return

    transition = (previous.status, self.status)

    allowed_operations = {
        ("Planned", "Active"): "issue",
        ("Active", "Returned"): "return",
    }

    if allowed_operations.get(transition) == self.flags.rental_operation:
        return

    frappe.throw(
        _("Rental status must be changed through the corresponding operation.")
    )
```

Итоговая защита:

```text
новый Rental
→ только Planned

Planned → Active
→ только issue()

Active → Returned
→ только return_equipment()
```

Старые test helpers, которые создавали `Active` или `Returned` напрямую через `insert()`, на S08 будут приведены к новому бизнес-контракту.

---

## 2. Добавить return_equipment()

Добавьте в Controller:

```python
@frappe.whitelist(methods=["POST"])
def return_equipment(self):
    self.reload()
    self.check_permission("write")

    if self.status != "Active":
        frappe.throw(_("Only an Active Rental can be returned."))

    self.flags.rental_operation = "return"
    self.status = "Returned"
    self.save()

    self.create_equipment_movements("Return")

    return {"status": self.status}
```

Как и `issue()`, команда:

```text
POST-only
перечитывает persisted Rental
проверяет write уже по сохранённому Document
```

Структура намеренно почти совпадает с `issue()`.

Пока не создавайте отдельный Service или command framework только ради двух коротких методов.

Общая часть уже вынесена там, где появилась настоящая общая ответственность:

```text
create_equipment_movements()
```

---

## 3. Почему Return снова не требует commit

Операция выполняет несколько writes:

```text
Rental.save()
Return Movement.insert() × N
```

Но транзакционная граница остаётся той же:

```text
успешный POST request
→ commit

необработанная ошибка
→ rollback
```

Ничего нового для Return изобретать не нужно.

---

## 4. Обновить Form Script

Приведите `rental.js` к виду:

```javascript
frappe.ui.form.on("Rental", {
    refresh(frm) {
        if (frm.is_new()) {
            return;
        }

        if (frm.doc.status === "Planned") {
            frm.add_custom_button(__("Issue"), () => {
                if (frm.is_dirty()) {
                    frappe.msgprint(__("Save Rental before issuing it."));
                    return;
                }

                frm.call("issue").then(() => frm.reload_doc());
            });
        }

        if (frm.doc.status === "Active") {
            frm.add_custom_button(__("Return"), () => {
                if (frm.is_dirty()) {
                    frappe.msgprint(__("Save Rental before returning it."));
                    return;
                }

                frm.call("return_equipment").then(() => frm.reload_doc());
            });
        }
    },
});
```

UI отражает предметное состояние:

```text
Planned  → Issue
Active   → Return
Returned → нет transition button
```

Но серверные методы сами проверяют состояние и permissions.

---

## 5. Проверить прямой Active → Returned

Возьмите Active Rental `success` из S02.

В console:

```python
rental = frappe.get_doc("Rental", "ВАШ_RENTAL_SUCCESS")
rental.status = "Returned"
rental.save()
```

Ожидается ошибка:

```text
Rental status must be changed through the corresponding operation.
```

Persisted state должен оставаться:

```text
Active
```

Проверьте:

```python
frappe.db.get_value("Rental", rental.name, "status")
```

---

## 6. Выполнить Return через Form

Войдите пользователем, который имеет `write` на этот Rental.

Для `success`, созданного `operator-a@example.test`, используйте этого оператора.

Откройте Form.

Ожидается:

```text
Status = Active
кнопка Return доступна
```

Нажмите **Return**.

После успешного request:

```text
Status = Returned
```

---

## 7. Проверить полный журнал

Под `manager@example.test` или Administrator проверьте:

```python
rental_name = "ВАШ_RENTAL_SUCCESS"

frappe.get_all(
    "Equipment Movement",
    filters={"rental": rental_name},
    fields=["equipment", "movement_type", "movement_at"],
    order_by="creation asc",
)
```

Для Rental с двумя Equipment ожидается:

```text
Issue  × 2
Return × 2
```

Для каждого Equipment история имеет пару:

```text
Issue
Return
```

---

## 8. Проверить повторный Return

После успешного возврата Form уже не показывает кнопку Return.

Серверный вызов также должен отказать из-за:

```text
status = Returned
```

UI и сервер согласованы, но сервер остаётся настоящей защитой.

---

## 9. Проверить повторный Issue

На том же Returned Rental вызов `issue()` должен быть запрещён:

```text
Only a Planned Rental can be issued.
```

Для текущего сценария этого достаточно, чтобы повторный request не создавал второй набор Issue Movement после завершённой операции.

Отдельная deduplication infrastructure сейчас не нужна.

---

## 10. Повторно проверить неправильное начальное состояние

Откройте console под Administrator и попробуйте создать новый Rental сразу как `Active`:

```python
frappe.get_doc(
    {
        "doctype": "Rental",
        "customer": "ВАШ_CUSTOMER",
        "start_date": "2026-11-01",
        "end_date": "2026-11-02",
        "status": "Active",
        "items": [{"equipment": "ВАШ_EQUIPMENT"}],
    }
).insert()
```

Ожидается:

```text
A new Rental must start as Planned.
```

Это подтверждает финальный серверный контракт и после добавления Return.

---

## 11. Проверить Git diff

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Ожидаются изменения:

```text
rental.py
rental.js
```

Посмотрите diff и убедитесь, что:

```text
Active → Returned разрешён только через return
return_equipment() POST-only
return_equipment() проверяет write на persisted Rental
return_equipment() не делает commit
кнопка Return не содержит бизнес-логики
```

---

## 12. Зафиксировать Return

```bash
git add \
  rental_training/rental_training/doctype/rental/rental.py \
  rental_training/rental_training/doctype/rental/rental.js

git commit -m "feat: add atomic rental return operation"
```

Проверьте:

```bash
git status --short
```

---

## 13. Контрольная точка S06

Рабочий контракт Rental:

```text
новый Rental = Planned

issue() [POST]
Planned → Active
+ Issue Movement × Equipment

return_equipment() [POST]
Active → Returned
+ Return Movement × Equipment
```

Обе операции используют одну транзакцию request и не управляют commit вручную.

Следующий этап покажет, почему прямой Database API способен обойти этот Controller: [`S07_DOCUMENT_VS_DB.md`](S07_DOCUMENT_VS_DB.md).