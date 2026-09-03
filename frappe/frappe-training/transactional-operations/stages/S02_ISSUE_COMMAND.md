# S02. Собрать атомарную команду Issue

S01 дал нам журнал `Equipment Movement`, но пока он пуст.

Теперь появляется бизнес-операция:

> Выдать Rental: перевести его из `Planned` в `Active` и создать `Issue` Movement для каждого Equipment.

Операция должна быть серверной и атомарной.

---

## 1. Почему обычного изменения status уже недостаточно

После появления Movement состояние:

```text
Rental = Active
```

без журнала выдачи становится противоречивым.

Поэтому:

```text
новый Rental
→ только Planned

Planned → Active
→ только Issue Rental
```

Нельзя защитить только редактирование существующего Document и оставить возможность вставить новый Rental сразу как `Active`.

---

## 2. Почему команда остаётся в Rental Controller

Операция относится к конкретному Rental и использует его:

```text
status
items
permissions
```

Отдельный `RentalService` или command bus текущему требованию не нужен.

Используем controller method:

```python
Rental.issue()
```

Frappe Form вызывает whitelisted controller method через `frm.call()`.

Первичные источники:

- https://docs.frappe.io/framework/user/en/api/form#frmcall
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/api/v2.py

Поскольку команда изменяет данные, она будет whitelisted только для POST:

```python
@frappe.whitelist(methods=["POST"])
```

В v16.33.0 Document method, вызванный POST-запросом, также проходит штатную write-permission проверку транспорта. В самой команде мы всё равно оставляем явный `self.check_permission("write")`, чтобы permission boundary принадлежала самой бизнес-операции.

---

## 3. Сделать status read-only в Form

Откройте Desk → `DocType` → `Rental`.

У поля:

```text
Status
fieldname = status
```

включите:

```text
Read Only = yes
```

Сохраните DocType.

Это убирает обычный UI-путь редактирования состояния, но серверная защита всё равно обязательна.

---

## 4. Добавить серверный контракт status

Откройте:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── rental/
                └── rental.py
```

В существующий `validate()` добавьте:

```python
def validate(self):
    self.validate_date_range()
    self.validate_duplicate_equipment()
    self.validate_status_transition()
    self.validate_active_equipment_conflicts()
```

Добавьте:

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

    if transition == ("Planned", "Active") and self.flags.rental_operation == "issue":
        return

    frappe.throw(
        _("Rental status must be changed through the corresponding operation.")
    )
```

На S02 это даёт:

```text
new Rental / Planned
→ разрешён

new Rental / Active или Returned
→ запрещён

обычное сохранение без изменения status
→ разрешено

Planned → Active внутри issue()
→ разрешено

прямой Planned → Active через save()
→ запрещён

прочие прямые переходы
→ пока запрещены
```

`Active → Returned` появится на S06 вместе с реальной командой Return.

---

## 5. Добавить helper создания Movement

В imports добавьте `now_datetime`:

```python
from frappe.utils import getdate, now_datetime
```

Добавьте в `Rental`:

```python
def create_equipment_movements(self, movement_type):
    movement_at = now_datetime()

    for row in self.items:
        frappe.get_doc(
            {
                "doctype": "Equipment Movement",
                "equipment": row.equipment,
                "rental": self.name,
                "movement_type": movement_type,
                "movement_at": movement_at,
            }
        ).insert(ignore_permissions=True)
```

Почему здесь осознанно используется `ignore_permissions=True`:

```text
Movement = system-generated journal
→ прикладным ролям Create не выдан

issue()
→ авторизует изменение на persisted Rental
→ затем внутренне создаёт Movement
```

Не переносите `ignore_permissions=True` на `self.save()` самого Rental.

---

## 6. Добавить issue()

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

    self.create_equipment_movements("Issue")

    return {"status": self.status}
```

### Почему сначала `reload()`, потом permission check

Для команды нужен именно persisted Rental из БД.

После `self.reload()` явная проверка:

```python
self.check_permission("write")
```

оценивает permission boundary по сохранённому Document, включая реальный `owner` и `If Owner`, а не по присланному клиентом состоянию Form.

UI дополнительно не будет запускать Issue на dirty Form, но сервер не должен зависеть только от UI.

---

## 7. Почему здесь нет commit

После:

```python
self.save()
```

и каждого:

```python
movement.insert(...)
```

SQL writes уже выполнены, но request-транзакция ещё не обязана быть зафиксирована.

Frappe Database API описывает:

```text
успешный POST/PUT
→ commit в конце request

необработанное исключение
→ rollback request
```

Источники:

- https://docs.frappe.io/framework/user/en/api/database#database-transaction-model
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/app.py

Поэтому внутри `issue()` не добавляйте:

```python
frappe.db.commit()
```

---

## 8. Добавить кнопку Issue

Откройте `rental.js` и добавьте:

```javascript
frappe.ui.form.on("Rental", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.status === "Planned") {
            frm.add_custom_button(__("Issue"), () => {
                if (frm.is_dirty()) {
                    frappe.msgprint(__("Save Rental before issuing it."));
                    return;
                }

                frm.call("issue").then(() => frm.reload_doc());
            });
        }
    },
});
```

Кнопка не содержит бизнес-логики. Она только вызывает серверную команду.

---

## 9. Проверить начальное состояние на сервере

В console под Administrator попробуйте создать новый Rental сразу как `Active`:

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

Это доказывает, что read-only Form не является единственной защитой.

---

## 10. Проверить прямой Planned → Active

Возьмите контрольный Rental `success` из S00:

```python
rental = frappe.get_doc("Rental", "ВАШ_RENTAL_SUCCESS")
rental.status = "Active"
rental.save()
```

Ожидается:

```text
Rental status must be changed through the corresponding operation.
```

Проверьте persisted state:

```python
frappe.db.get_value("Rental", rental.name, "status")
```

Остаётся:

```text
Planned
```

---

## 11. Выполнить успешный Issue через Form

Войдите как:

```text
operator-a@example.test
```

Откройте Rental `success`.

Ожидается:

```text
Status = Planned
Status read-only
кнопка Issue доступна
```

Нажмите **Issue**.

После успешного ответа:

```text
Status = Active
```

---

## 12. Проверить полный журнал

Под `manager@example.test` откройте `Equipment Movement` List.

Для Rental `success` с двумя Equipment должны существовать две строки `Issue`.

При необходимости через console:

```python
frappe.get_all(
    "Equipment Movement",
    filters={
        "rental": "ВАШ_RENTAL_SUCCESS",
        "movement_type": "Issue",
    },
    fields=["name", "equipment", "movement_type", "movement_at", "owner"],
    order_by="name asc",
)
```

Количество Movement должно совпадать с количеством `Rental Item`.

Одинаковый `movement_at` показывает, что timestamp был сформирован один раз для всей команды.

---

## 13. Проверить operator boundary

Под `operator-a@example.test` прямой доступ к `Equipment Movement` не должен появляться.

При этом Issue собственного Rental уже создал Movement.

Граница:

```text
нет Create на Movement
≠
серверная команда не может создать внутренний журнал
```

Авторизация находится на Rental.

---

## 14. Проверить diff

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short

git diff -- \
  rental_training/rental_training/doctype/rental/rental.json \
  rental_training/rental_training/doctype/rental/rental.py \
  rental_training/rental_training/doctype/rental/rental.js
```

Проверьте:

```text
status read_only
new Rental обязан стартовать Planned
validate_status_transition добавлен
issue() POST-only
issue() перечитывает persisted Rental до явной permission check
Movement создаётся через Document API
ручного commit нет
JS только вызывает серверный method
```

---

## 15. Зафиксировать Issue-команду

```bash
git add \
  rental_training/rental_training/doctype/rental/rental.json \
  rental_training/rental_training/doctype/rental/rental.py \
  rental_training/rental_training/doctype/rental/rental.js

git commit -m "feat: add atomic rental issue operation"
```

Проверьте чистое дерево.

---

## 16. Контрольная точка S02

Готово, если:

```text
новый Rental может стартовать только Planned
Rental.status read-only в Form
прямой Planned → Active через save запрещён
issue() POST-only и whitelisted
issue() проверяет write на persisted Rental
issue() не делает ручной commit
успешный Issue переводит Rental в Active
создаётся Movement для каждого Equipment
оператор не получает прямой Create на Movement
Git App чист
```

Следующий этап намеренно оборвёт эту рабочую команду и проверит настоящий rollback: [`S03_ROLLBACK.md`](S03_ROLLBACK.md).