# S02. Собрать атомарную команду Issue

S01 дал нам журнал `Equipment Movement`, но пока он пуст.

Теперь появляется сама бизнес-операция:

> Выдать Rental: перевести его из `Planned` в `Active` и создать `Issue` Movement для каждого Equipment.

Эта операция должна быть серверной и атомарной.

---

## 1. Почему обычного изменения status уже недостаточно

До появления Movement пользователь мог изменить:

```text
Planned → Active
```

как обычное поле Rental.

Теперь такой переход без журнала создаёт противоречие:

```text
Rental = Active
но факта выдачи Equipment нет
```

Поэтому после S02:

```text
Planned → Active
```

становится не просто новым значением поля, а командой:

```text
Issue Rental
```

---

## 2. Почему команда остаётся в Rental Controller

Операция относится к конкретному Rental и использует его данные:

```text
status
items
permissions
```

Пока нет отдельной ответственности, которая требовала бы создавать `RentalService` или собственный command bus.

Поэтому используем обычный controller method:

```python
Rental.issue()
```

Frappe Form умеет вызывать whitelisted controller method через `frm.call()`.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/form#frmcall

В Frappe v16.33.0 серверный `run_doc_method` также проверяет write permission для POST-вызова Document method и проверяет, что метод whitelisted.

Исходный код:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/api/v2.py

Мы всё равно оставим явный `self.check_permission("write")` внутри команды, потому что permission boundary является частью самой бизнес-команды, а не только особенностью конкретного транспорта вызова.

---

## 3. Сделать status read-only для обычной Form

Откройте Desk → `DocType` → `Rental`.

Найдите поле:

```text
Status
fieldname = status
```

Включите:

```text
Read Only = yes
```

Сохраните DocType.

Это убирает обычный пользовательский путь редактирования состояния.

Но это **не единственная защита**. На сервере будет отдельная validation перехода.

---

## 4. Добавить серверную защиту перехода

Откройте:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── rental/
                └── rental.py
```

В существующий `validate()` добавьте новую проверку:

```python
def validate(self):
    self.validate_date_range()
    self.validate_duplicate_equipment()
    self.validate_status_transition()
    self.validate_active_equipment_conflicts()
```

Добавьте метод:

```python
def validate_status_transition(self):
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

### Что делает эта проверка

```text
создание нового Planned Rental
→ разрешено

обычное сохранение без изменения status
→ разрешено

Planned → Active внутри issue()
→ разрешено

прямой Planned → Active через обычный save
→ запрещён

любой другой прямой переход
→ пока запрещён
```

`Active → Returned` будет разрешён на S06, когда появится реальная команда Return.

---

## 5. Добавить helper создания Movement

В imports добавьте:

```python
from frappe.utils import getdate, now_datetime
```

Если `getdate` уже импортирован, просто дополните существующий import.

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

Почему `ignore_permissions=True` здесь осознанный:

```text
Equipment Movement
→ system-generated journal
→ пользователям Create не выдан

Rental.issue()
→ сначала проверит write на Rental
→ только после этого создаст внутренние Movement
```

Не переносите `ignore_permissions=True` на `self.save()` самого Rental.

Пользовательская команда обязана сохранить обычную permission boundary Rental.

---

## 6. Добавить issue()

Добавьте:

```python
@frappe.whitelist()
def issue(self):
    self.check_permission("write")
    self.reload()

    if self.status != "Planned":
        frappe.throw(_("Only a Planned Rental can be issued."))

    self.flags.rental_operation = "issue"
    self.status = "Active"
    self.save()

    self.create_equipment_movements("Issue")

    return {"status": self.status}
```

### Почему `self.reload()`

`frm.call()` вызывает controller method для текущего Document.

Перед бизнес-командой нам нужен именно последний сохранённый Rental из БД, а не случайные незаписанные изменения клиента.

Поэтому после permission check команда перечитывает persisted state.

UI дополнительно не будет запускать Issue на dirty Form, но серверная команда не должна зависеть только от UI.

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

в БД уже выполнены SQL writes, но транзакция request ещё не обязана быть зафиксирована.

Frappe Database API описывает модель так:

```text
успешный POST/PUT
→ commit в конце request

необработанное исключение
→ rollback request
```

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#database-transaction-model

В исходном коде v16.33.0 request handler при исключении вызывает `db.rollback(...)`, а успешный путь проходит `sync_database()`.

Источник:

- https://github.com/frappe/frappe/blob/v16.33.0/frappe/app.py

Поэтому в `issue()` **не добавляйте**:

```python
frappe.db.commit()
```

---

## 8. Добавить кнопку Issue в rental.js

Откройте:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── rental/
                └── rental.js
```

Добавьте:

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

Кнопка — только способ вызвать серверную команду.

Она не содержит:

```text
изменения status
создания Movement
permission logic
transaction logic
```

---

## 9. Проверить итоговый Controller

Смысловая структура после S02:

```python
class Rental(Document):
    def validate(self):
        self.validate_date_range()
        self.validate_duplicate_equipment()
        self.validate_status_transition()
        self.validate_active_equipment_conflicts()

    ... существующие validators ...

    def validate_status_transition(self):
        previous = self.get_doc_before_save()

        if not previous or previous.status == self.status:
            return

        transition = (previous.status, self.status)

        if transition == ("Planned", "Active") and self.flags.rental_operation == "issue":
            return

        frappe.throw(
            _("Rental status must be changed through the corresponding operation.")
        )

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

    @frappe.whitelist()
    def issue(self):
        self.check_permission("write")
        self.reload()

        if self.status != "Planned":
            frappe.throw(_("Only a Planned Rental can be issued."))

        self.flags.rental_operation = "issue"
        self.status = "Active"
        self.save()
        self.create_equipment_movements("Issue")

        return {"status": self.status}
```

Не переписывайте существующие validators, если для нового требования это не требуется.

---

## 10. Проверить прямое изменение status через Document API

До успешной Issue полезно проверить серверную границу.

Откройте console:

```bash
bench --site rental.localhost console
```

Возьмите контрольный Rental `success` из S00:

```python
rental = frappe.get_doc("Rental", "ВАШ_RENTAL_SUCCESS")
rental.status = "Active"
rental.save()
```

Ожидается ошибка:

```text
Rental status must be changed through the corresponding operation.
```

Проверьте:

```python
frappe.db.get_value("Rental", rental.name, "status")
```

Ожидается:

```text
Planned
```

Завершите console.

---

## 11. Выполнить успешный Issue через Form

Войдите как:

```text
operator-a@example.test
```

Откройте контрольный Rental `success`.

Form должна показывать:

```text
Status = Planned
Status нельзя редактировать вручную
кнопка Issue доступна
```

Нажмите **Issue**.

После успешного ответа Form должна перезагрузиться:

```text
Status = Active
```

---

## 12. Проверить Movement под менеджером

Войдите как:

```text
manager@example.test
```

Откройте `Equipment Movement` List.

Для контрольного Rental должны появиться две строки:

```text
Issue → Equipment 1 → Rental success
Issue → Equipment 2 → Rental success
```

Обе должны иметь одинаковый `movement_at`, потому что это одна операция выдачи.

Проверьте через console при необходимости:

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

Количество строк должно совпадать с количеством `Rental Item`.

---

## 13. Проверить operator permission boundary

Под `operator-a@example.test` попытайтесь открыть `Equipment Movement` через поиск Desk.

Оператор не должен получать обычный прямой доступ к журналу.

При этом Issue собственного Rental уже успешно создал Movement.

Именно это подтверждает границу:

```text
нет Create на Equipment Movement
≠
команда не может создать внутреннюю запись
```

Авторизация команды находится на Rental.

---

## 14. Проверить Git diff

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Ожидаются изменения как минимум в:

```text
rental.json
rental.py
rental.js
```

Посмотрите diff:

```bash
git diff -- \
  rental_training/rental_training/doctype/rental/rental.json \
  rental_training/rental_training/doctype/rental/rental.py \
  rental_training/rental_training/doctype/rental/rental.js
```

Проверьте:

```text
status стал read_only
validate_status_transition добавлен
issue() добавлен
Movement создаётся через Document API
ручного commit нет
кнопка только вызывает серверный method
```

---

## 15. Зафиксировать рабочую Issue-команду

```bash
git add \
  rental_training/rental_training/doctype/rental/rental.json \
  rental_training/rental_training/doctype/rental/rental.py \
  rental_training/rental_training/doctype/rental/rental.js

git commit -m "feat: add atomic rental issue operation"
```

Проверьте:

```bash
git status --short
```

Должно быть чисто.

---

## 16. Контрольная точка S02

Готово, если:

```text
Rental.status read-only в Form
прямой Planned → Active через save запрещён
issue() whitelisted
issue() проверяет write permission
issue() не делает ручной commit
успешный Issue переводит Rental в Active
создаётся Movement для каждого Equipment
оператор не получает прямой Create на Movement
Git App чист
```

Следующий этап намеренно сломает эту команду и проверит настоящий rollback: [`S03_ROLLBACK.md`](S03_ROLLBACK.md).