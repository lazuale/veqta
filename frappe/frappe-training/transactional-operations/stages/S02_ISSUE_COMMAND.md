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
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/handler.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py

Поскольку команда изменяет данные, она будет whitelisted только для POST:

```python
@frappe.whitelist(methods=["POST"])
```

Здесь важно не приписывать HTTP-методу лишнюю семантику. Для legacy-вызова через `frm.call()` Frappe `run_doc_method()` загружает Document с `check_permission=True`; в `Document` это означает обычную проверку `read`, если конкретный тип permission не указан. Ограничение `methods=["POST"]` проверяет допустимый HTTP method, но само по себе не превращается в `write`-permission check.

Поэтому настоящая permission boundary изменяющей бизнес-команды должна быть явной:

```python
rental.check_permission("write")
```

REST API v2 имеет собственную семантику HTTP-методов и не должен смешиваться с legacy `frm.call()` при объяснении этой проверки.

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
    self.lock_active_equipment()
    self.validate_active_equipment_conflicts()
```

`lock_active_equipment()` уже появился на S06 предыдущего практикума: перед проверкой V03 он берёт row lock для выбранных Equipment в стабильном порядке. Это не отдельная транзакционная инфраструктура, а часть гарантии междокументного инварианта при конкурентных запросах.

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
    rental = frappe.get_doc("Rental", self.name, for_update=True)
    rental.check_permission("write")

    if rental.status != "Planned":
        frappe.throw(_("Only a Planned Rental can be issued."))

    rental.flags.rental_operation = "issue"
    rental.status = "Active"
    rental.save()

    rental.create_equipment_movements("Issue")

    return {"status": rental.status}
```

### Почему команда заново получает Rental с `for_update=True`

Whitelisted method вызывается на Document, который пришёл через RPC-путь, но изменяющая команда должна работать с актуальным persisted состоянием.

```python
frappe.get_doc("Rental", self.name, for_update=True)
```

делает две вещи:

```text
загружает текущий Rental из БД
+ удерживает row lock до конца транзакции
```

Это важно не только для свежих данных. Без блокировки два одновременных `issue()` одного `Planned` Rental могут оба успеть прочитать старое состояние и попытаться создать два набора `Issue Movement`.

С row lock второй request ждёт завершения первого, затем читает уже `Active` и останавливается на проверке:

```text
Only a Planned Rental can be issued.
```

После блокировки явная проверка:

```python
rental.check_permission("write")
```

проверяет право на тот же persisted Document, который команда собирается изменять.

### Как это связано с V03

Row lock Rental и row locks Equipment решают разные задачи:

```text
Rental FOR UPDATE
→ сериализует команды над одним Rental

Equipment FOR UPDATE внутри V03
→ сериализует разные Rentals, конкурирующие за одно Equipment
```

Один lock не заменяет другой.

---

## 7. Почему здесь нет commit

После:

```python
rental.save()
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

Row locks также не требуют отдельного commit: они живут внутри той же request-транзакции и освобождаются при её завершении.

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
issue() заново получает persisted Rental с for_update=True
issue() явно проверяет write на locked Rental
V03 блокирует Equipment перед проверкой пересечений
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
issue() блокирует persisted Rental через for_update=True
issue() явно проверяет write на locked Rental
V03 сериализует конкурирующие Rentals через Equipment row locks
issue() не делает ручной commit
успешный Issue переводит Rental в Active
создаётся Movement для каждого Equipment
оператор не получает прямой Create на Movement
Git App чист
```

Следующий этап намеренно оборвёт эту рабочую команду и проверит настоящий rollback: [`S03_ROLLBACK.md`](S03_ROLLBACK.md).