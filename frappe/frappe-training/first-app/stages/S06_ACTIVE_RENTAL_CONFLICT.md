# S06. Запретить пересекающиеся Active Rentals одного Equipment

К S06 приложение уже умеет хранить Rental, защищать его локальные инварианты и применять базовые роли.

```text
Rental.validate()
├── V01: end_date >= start_date
└── V02: Equipment не повторяется внутри Rental

Rental Operator / Rental Manager
└── Role + DocType Permissions
```

Теперь появляется новый класс требования:

> Одна единица Equipment не может одновременно находиться в двух Rentals со статусом `Active`, если их периоды пересекаются.

Это уже не проверка только текущего Document. Решение требует прочитать другие Rental Documents и их дочерние строки.

Связанные документы:

- [`S05C_RENTAL_LOCAL_INVARIANTS.md`](S05C_RENTAL_LOCAL_INVARIANTS.md);
- [`S05D_ROLES_AND_PERMISSIONS.md`](S05D_ROLES_AND_PERMISSIONS.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../REQUIREMENTS.md`](../REQUIREMENTS.md);
- [`../ROADMAP.md`](../ROADMAP.md);
- [`../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md`](../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md);
- [`../../frappe-architecture-standard/06_TRANSACTIONS_ASYNC.md`](../../frappe-architecture-standard/06_TRANSACTIONS_ASYNC.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/api/database
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/__init__.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py

---

# 1. Сначала зафиксировать бизнес-семантику

В учебном приложении Equipment считается занятым только когда:

```text
status = Active
```

То есть:

```text
Planned  → не блокирует
Active   → блокирует
Returned → не блокирует
```

Это решение предметной модели практикума, а не встроенное свойство Frappe.

Если позже требования изменятся и `Planned` начнёт резервировать Equipment, изменится правило участвующих статусов. Для этого не нужно автоматически вводить Workflow, новый DocType или отдельный механизм резервирования.

---

# 2. Формула пересечения дат

`start_date` и `end_date` — поля `Date`, а границы периода в практикуме включительны.

Два периода конфликтуют, если:

```text
existing.start_date <= current.end_date
AND
existing.end_date >= current.start_date
```

Проверим смысл до кода.

```text
10–12 и 11–13 → конфликт
10–12 и 12–14 → конфликт
10–12 и 13–14 → нет конфликта
```

Общая дата 12 сентября принадлежит обоим периодам, поэтому второй пример конфликтует.

---

# 3. Кто владеет V03

V03 читает другие Documents, но отвечает на тот же вопрос:

> Допустимо ли сохранить текущий Rental в его текущем состоянии?

Поэтому правило остаётся в `Rental Controller` и вызывается из `validate()`.

Пока не нужны:

```text
RentalService
ReservationService
Availability Engine
Booking Rule DocType
Server Script
собственный API
```

Отдельный Service станет кандидатом только после появления действительно самостоятельной ответственности, а не из-за того, что один validator сделал запрос к другим Documents.

---

# 4. `get_list` и `get_all` здесь имеют разный смысл

Frappe различает:

```text
frappe.get_list(...)
→ учитывает permissions текущего пользователя

frappe.get_all(...)
→ не применяет обычную фильтрацию по permissions
```

Для пользовательских списков нормальный выбор — путь с учётом permissions.

Но V03 — внутренний инвариант данных. Если конфликт уже существует в базе, текущий Rental нельзя разрешать только потому, что пользователь не видит конфликтующую запись в своём List.

Поэтому **внутри V03 `get_all()` используется намеренно**.

Это не означает «если права мешают — всегда используйте get_all». На S05D уже зафиксировано противоположное правило: обход permissions должен иметь конкретную системную причину.

Также внутренний запрос не должен без необходимости раскрывать пользователю данные скрытого Rental. Поэтому ошибка сообщает о занятости Equipment, но не обязана показывать имя конфликтующего Rental, его Customer или owner.

---

# 5. Алгоритм без ручного SQL

Текущий Rental содержит Equipment через `Rental Item`.

Сначала находим дочерние строки с теми же Equipment:

```text
current.items
→ имена Equipment
→ строки Rental Item
→ имена родительских Rental
```

Затем среди найденных родителей ищем:

```text
status = Active
AND start_date <= current.end_date
AND end_date >= current.start_date
```

Получается два обычных запроса через Database API Frappe. Ручной SQL текущему требованию не нужен.

---

# 6. Дополнить `rental.py`

Откройте:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── rental/
                └── rental.py
```

После S06 содержательная часть Controller должна выглядеть так:

```python
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class Rental(Document):
    def validate(self):
        self.validate_date_range()
        self.validate_duplicate_equipment()
        self.validate_active_equipment_conflicts()

    def validate_date_range(self):
        if self.start_date and self.end_date and getdate(self.end_date) < getdate(self.start_date):
            frappe.throw(_("End Date cannot be before Start Date."))

    def validate_duplicate_equipment(self):
        equipment = [row.equipment for row in self.items if row.equipment]

        if len(equipment) != len(set(equipment)):
            frappe.throw(_("The same Equipment cannot be selected more than once in one Rental."))

    def validate_active_equipment_conflicts(self):
        if self.status != "Active" or not self.start_date or not self.end_date:
            return

        equipment = [row.equipment for row in self.items if row.equipment]
        if not equipment:
            return

        matching_items = frappe.get_all(
            "Rental Item",
            filters=[
                ["equipment", "in", equipment],
                ["parenttype", "=", "Rental"],
                ["parentfield", "=", "items"],
            ],
            fields=["parent", "equipment"],
        )

        candidate_rentals = sorted(
            {row.parent for row in matching_items if row.parent != self.name}
        )
        if not candidate_rentals:
            return

        overlapping_rentals = set(
            frappe.get_all(
                "Rental",
                filters=[
                    ["name", "in", candidate_rentals],
                    ["status", "=", "Active"],
                    ["start_date", "<=", self.end_date],
                    ["end_date", ">=", self.start_date],
                ],
                pluck="name",
            )
        )

        if not overlapping_rentals:
            return

        conflicting_equipment = sorted(
            {
                row.equipment
                for row in matching_items
                if row.parent in overlapping_rentals
            }
        )

        frappe.throw(
            _(
                "Equipment {0} is already used in another Active Rental for the selected period."
            ).format(", ".join(conflicting_equipment))
        )
```

Существующий copyright/license header App сохраняйте.

---

# 7. Разобрать критические места

## Только `Active`

```python
if self.status != "Active":
    return
```

Поэтому `Planned` и `Returned` не участвуют в V03.

## Пустые даты

```python
not self.start_date or not self.end_date
```

не заменяют `Mandatory` metadata. Ранний `return` только не позволяет междокументному запросу работать с неполным периодом раньше штатной проверки обязательных полей.

## Дочерние строки

`Rental Item` имеет системные поля:

```text
parent
parenttype
parentfield
```

Поэтому из него можно найти родительский Rental. Условия

```text
parenttype = Rental
parentfield = items
```

явно фиксируют нужную связь и не опираются на предположение, что `Rental Item` никогда больше нигде не будет использован.

---

# 8. Не забыть исключить текущий Rental

При редактировании существующего Rental его старые дочерние строки уже находятся в БД.

Если не выполнить:

```python
row.parent != self.name
```

Active Rental сможет найти самого себя и объявить собственное состояние конфликтом.

Исключение текущего Document — часть корректности V03, а не оптимизация.

---

# 9. Проверить основной конфликт через Desk

Под `Rental Manager` или `Administrator` создайте Active Rental A:

```text
Customer   : любой существующий Customer
Start Date : 2026-09-10
End Date   : 2026-09-12
Status     : Active
Equipment  : EQ-00001
```

Если этот Equipment свободен, Rental A сохраняется.

Теперь создайте Active Rental E:

```text
Start Date : 2026-09-11
End Date   : 2026-09-13
Status     : Active
Equipment  : тот же EQ-00001
```

Ожидается отказ со смыслом:

```text
Equipment EQ-00001 is already used in another Active Rental for the selected period.
```

---

# 10. Проверить границу периода

После Active Rental A `10–12`:

```text
Active 12–14 → запрещён
Active 13–14 → разрешён
```

Так проверяется именно включительная формула интервала, а не только один очевидный случай из середины периода.

---

# 11. Проверить семантику `Planned`

Создайте:

```text
Start Date : 2026-09-11
End Date   : 2026-09-13
Status     : Planned
Equipment  : EQ-00001
```

Несмотря на пересечение с Active Rental A, Planned Rental должен сохраниться.

Теперь измените:

```text
Planned → Active
```

и сохраните.

Ожидается конфликт.

Это показывает, что обычный `save()` повторно проверяет текущее состояние Document. Отдельный endpoint `activate_rental` для текущего требования не нужен.

---

# 12. Проверить `Returned`

`Returned` Rental по текущей семантике не блокирует Equipment.

Создайте пересекающийся `Returned` Rental либо переведите контрольный Rental в `Returned`, затем убедитесь, что новый `Active` Rental не блокируется только из-за этой Returned-записи.

---

# 13. Проверить отсутствие конфликта с самим собой

Откройте валидный Active Rental A и сохраните его повторно без изменения периода либо измените Customer.

Ожидается успешное сохранение.

Если Rental блокирует сам себя, V03 реализован неверно.

---

# 14. Проверить V03 серверным `Document.insert()`

Откройте Bench console:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Переключитесь на пользователя с правом Create Rental:

```python
frappe.set_user("operator@example.test")
```

Здесь мы выбираем тестовые данные **с учётом permissions**:

```python
customer = frappe.get_list("Customer", pluck="name", limit_page_length=1)[0]
equipment = frappe.get_list("Equipment", pluck="name", limit_page_length=1)[0]
```

Это важно: `get_all()` нужен внутри системного инварианта V03, но не нужен оператору просто для выбора доступных ему Documents.

Создайте контрольную запись на свободном периоде:

```python
baseline = frappe.get_doc(
    {
        "doctype": "Rental",
        "customer": customer,
        "start_date": "2026-11-10",
        "end_date": "2026-11-12",
        "status": "Active",
        "items": [{"equipment": equipment}],
    }
).insert()
```

В интерактивном console можно явно зафиксировать успешную контрольную запись:

```python
frappe.db.commit()
```

Этот `commit()` относится только к ручной console-сессии. Его не должно быть в Controller: обычной транзакционной границей web request или job управляет Frappe.

Теперь конфликтующий Document:

```python
conflict = frappe.get_doc(
    {
        "doctype": "Rental",
        "customer": customer,
        "start_date": "2026-11-11",
        "end_date": "2026-11-13",
        "status": "Active",
        "items": [{"equipment": equipment}],
    }
)

try:
    conflict.insert()
except frappe.ValidationError as exc:
    print("BLOCKED V03:", exc)
    frappe.db.rollback()
```

Ожидается сообщение `BLOCKED V03`.

Ключевой вывод:

```text
Form не участвовал
Client Script не участвовал
V03 всё равно сработал
```

---

# 15. Что эта проверка не гарантирует при конкурентных запросах

Обычная `validate()`-проверка не исключает сценарий:

```text
T1 проверяет → конфликта ещё нет
T2 проверяет → конфликта ещё нет
T1 записывает Rental
T2 записывает Rental
```

S06 доказывает только:

```text
при последовательном сохранении
существующий конфликт обнаруживается
```

Он не доказывает строгую сериализацию параллельных бронирований.

Реальная задача с конкурентными запросами может потребовать отдельной доказанной стратегии:

```text
транзакции и блокировки
модель резервирования
сериализованный критический участок
другая схема конкурентного доступа
```

Какой именно механизм нужен, определяется реальной нагрузкой и требованием. В практикуме не добавляем SQL locks или Reservation Service ради демонстрации возможностей.

---

# 16. Что не нужно делать

Не добавляйте ради V03:

```text
ручной commit в Controller
Client Script как единственную защиту
ручной SQL без необходимости
Reservation DocType без нового требования
Rule Engine
permission-aware get_list внутри инварианта,
если из-за будущих ограничений он сможет пропустить реальный конфликт
```

Также не следует возвращать пользователю скрытые детали конфликтующего Rental только потому, что внутренний validator их увидел.

---

# 17. Зафиксировать изменение в Git

Проверьте изменение:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training diff -- \
  rental_training/rental_training/doctype/rental/rental.py
```

Зафиксируйте Controller:

```bash
git -C apps/rental_training add \
  rental_training/rental_training/doctype/rental/rental.py

git -C apps/rental_training commit \
  -m "feat: prevent overlapping active rentals"
```

Проверка:

```bash
git -C apps/rental_training status --short
```

Ожидается пустой вывод.

Как и на S05C, схема не менялась, поэтому `bench migrate` не выполняется просто из-за изменения Python Controller.

---

# 18. Проверка перед S07

Перед переходом дальше должно быть проверено:

```text
Active 10–12 + Active 11–13, same Equipment → запрещено
Active 10–12 + Active 12–14, same Equipment → запрещено
Active 10–12 + Active 13–14, same Equipment → разрешено
Planned overlap                         → разрешён
Planned → Active при конфликте          → запрещено
Returned overlap                        → не блокирует
повторный save самого Active Rental     → разрешён
```

Конфликт также должен блокироваться обычным `Document.insert()` без Form/Client Script.

Ученик должен объяснить:

```text
почему V03 читает другие Documents
почему внутренний инвариант использует get_all
почему пользовательский поиск от этого не становится get_all
почему обычная validate-проверка не гарантирует защиту от конкурентных запросов
```

`rental.py` находится в Git, рабочее дерево App чистое.

---

# 19. Когда не переходить к S07

Сначала исправьте проблему, если:

- конфликт проверяется только JavaScript-кодом формы;
- текущий Rental конфликтует сам с собой;
- общая граничная дата ошибочно считается непересечением;
- `Planned` или `Returned` блокируют Equipment вопреки принятой семантике;
- реальный конфликт может исчезнуть из-за фильтрации permissions пользовательского List;
- в Controller появился ручной `frappe.db.commit()`;
- заявлено, что обычная `validate()` полностью решает конкурентное бронирование;
- появился отдельный слой резервирования, Service или Rule Engine без нового требования;
- изменение Controller не находится в Git.

---

# 20. Что должно остаться после S06

```text
Rental.validate()
├── V01 local: date range
├── V02 local: duplicate Equipment
└── V03 cross-document: overlapping Active Rental
```

На этом все три согласованных бизнес-инварианта учебного приложения реализованы.

Следующий этап — S07: ручные проверки S05C/S05D/S06 превращаются в повторяемые автоматические проверки Frappe test runner.