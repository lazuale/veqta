# S06. Запретить пересекающиеся Active Rentals одного Equipment

К S06 приложение уже умеет:

```text
Rental
├── customer
├── start_date
├── end_date
├── status
└── items
      ↓
Controller.validate()
├── V01: end_date >= start_date
└── V02: Equipment не повторяется внутри Rental
```

и имеет базовую permission model:

```text
Rental Operator
Rental Manager
```

Теперь появляется новый класс требования:

> Одна и та же единица Equipment не может одновременно находиться в двух Rentals со статусом `Active`, если их периоды пересекаются.

Это уже не локальная проверка одного Document. Чтобы принять решение, Rental должен посмотреть на **другие** Rental Documents и их child rows.

Связанные документы:

- [`S05C_RENTAL_LOCAL_INVARIANTS.md`](S05C_RENTAL_LOCAL_INVARIANTS.md);
- [`S05D_ROLES_AND_PERMISSIONS.md`](S05D_ROLES_AND_PERMISSIONS.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md);
- [`../REQUIREMENTS_MATRIX.md`](../REQUIREMENTS_MATRIX.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md`](../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md);
- [`../../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md`](../../frappe-architecture-standard/05_TRANSACTIONS_ASYNC.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/api/database
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/__init__.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py

---

# 1. Сначала определить точную бизнес-семантику

В CORE занятость Equipment определяется так:

```text
status = Active
```

Только `Active` блокирует оборудование.

```text
Planned  → не блокирует
Active   → блокирует
Returned → не блокирует
```

Это **не универсальное правило проката**. Это конкретное требование текущего учебного продукта.

Если позже бизнес скажет:

> Подтверждённый Planned Rental тоже резервирует Equipment.

изменится предметное правило, например:

```text
blocking statuses = Planned + Active
```

Но это не означает, что нужно менять архитектуру на Workflow, новый DocType или отдельный reservation framework.

---

# 2. Определить пересечение периодов

Поля `start_date` и `end_date` имеют тип `Date`.

В CORE границы периода включительны.

Rental A:

```text
10 сентября — 12 сентября
```

занимает Equipment и 10-го, и 12-го.

Поэтому два периода пересекаются, если:

```text
existing.start_date <= current.end_date
AND
existing.end_date >= current.start_date
```

Примеры.

## Пересечение

```text
A: 10–12
B: 11–13
```

Результат:

```text
конфликт
```

## Общая граничная дата

```text
A: 10–12
B: 12–14
```

Результат:

```text
конфликт
```

потому что 12 сентября принадлежит обоим периодам.

## Нет пересечения

```text
A: 10–12
B: 13–14
```

Результат:

```text
допустимо
```

Эту семантику нужно определить **до написания запроса**. Иначе два разработчика легко реализуют разные представления о границах интервала.

---

# 3. Почему правило остаётся в Rental Controller

V03 использует другие Documents, но по смыслу всё ещё отвечает на вопрос:

> Можно ли сохранить текущий Rental в его текущем состоянии?

Поэтому для CORE естественная точка остаётся:

```text
Rental.validate()
```

Мы пока не создаём:

```text
RentalService
ReservationService
Availability Engine
Booking Rule DocType
Server Script
custom API
```

Отдельный service может стать оправдан, если появится самостоятельная ответственность: сложное резервирование, несколько типов ресурсов, отдельная транзакционная команда, внешняя интеграция и т. п.

Сейчас этого требования нет.

---

# 4. Почему внутренний запрос использует `frappe.get_all()`

Frappe различает два близких пути чтения:

```text
frappe.get_list(...)
→ учитывает permissions текущего пользователя

frappe.get_all(...)
→ не применяет обычную permission filtering
```

Для пользовательского списка это важное различие: обычно нельзя заменять `get_list` на `get_all`, чтобы «починить» права.

Но V03 — не пользовательский поиск.

Это **внутренний инвариант данных**:

```text
если конфликт существует в базе
→ сохранение должно быть запрещено
```

Он не должен зависеть от того, видит ли текущий пользователь конфликтующий Rental в List.

Поэтому здесь `get_all()` используется намеренно.

Это не даёт пользователю право изменять или удалять чужой Document. Мы только читаем необходимые данные внутри серверной проверки и не возвращаем скрытый Rental наружу.

По этой же причине сообщение ошибки не должно без необходимости раскрывать имя конфликтующего Rental.

---

# 5. Алгоритм без SQL

Текущий Rental содержит Equipment через child rows `Rental Item`.

Задачу удобно разделить на два штатных запроса.

## Шаг 1. Найти другие Rentals с тем же Equipment

```text
current.items
→ Equipment names
→ Rental Item rows в БД
→ parent Rental names
```

## Шаг 2. Среди этих Rentals найти Active с пересекающимися датами

```text
candidate Rentals
+
status = Active
+
start_date <= current.end_date
+
end_date >= current.start_date
```

Это остаётся обычным Database API Frappe.

Ручной SQL для такого требования не нужен.

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

# 7. Разобрать код по смыслу

## Проверять только Active

```python
if self.status != "Active":
    return
```

Из этого автоматически следует:

```text
Planned с пересечением → допустим
Returned с пересечением → допустим
```

Это бизнес-семантика CORE, а не техническое ограничение Frappe.

## Почему проверяются даты на наличие

```python
not self.start_date or not self.end_date
```

`Mandatory` metadata всё равно защищает обязательность полей.

Здесь ранний `return` нужен лишь затем, чтобы междокументный запрос не пытался работать с пустой границей периода раньше штатной mandatory validation.

## Почему сначала `Rental Item`

Нужно найти другие Rentals, где присутствует хотя бы одно Equipment текущего Rental.

Child rows имеют системные поля:

```text
parent
parenttype
parentfield
```

поэтому из `Rental Item` можно получить родительские Rental names.

## Почему явно проверяются `parenttype` и `parentfield`

Сегодня `Rental Item` используется только в `Rental.items`.

Но явное условие фиксирует именно нужную связь:

```text
parenttype = Rental
parentfield = items
```

Код не опирается на случайное предположение, что этот Child DocType никогда больше нигде не будет применён.

---

# 8. Обязательно исключить текущий Rental

При редактировании существующего Active Rental его старые child rows уже находятся в БД.

Если не исключить:

```python
row.parent != self.name
```

Rental найдёт самого себя и объявит собственное состояние конфликтом.

Поэтому self-exclusion — часть корректности правила, а не оптимизация.

Нужно проверить это отдельным сценарием.

---

# 9. Не раскрывать лишние данные в ошибке

Внутренняя проверка может видеть больше записей, чем пользовательский List.

Поэтому сообщение:

```text
Equipment EQ-00001 is already used in another Active Rental...
```

достаточно для текущего требования.

Не требуется сообщать:

```text
конфликтующий RENT-00042
его Customer
его даты
его owner
```

если это не является отдельным UX-требованием и не проверено с точки зрения доступа.

Это полезная граница:

```text
внутренняя проверка может знать
≠
пользователь автоматически должен увидеть
```

---

# 10. Проверить базовый конфликт через Desk

Под `Rental Manager` или `Administrator` создайте контрольный Active Rental A:

```text
Customer   : любой существующий Customer
Start Date : 2026-09-10
End Date   : 2026-09-12
Status     : Active
Equipment  : EQ-00001
```

Он должен сохраниться, если на эти даты ещё нет другого Active Rental с этим Equipment.

Теперь создайте Rental E:

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

Rental E не должен сохраниться.

---

# 11. Проверить включительную границу дат

Попробуйте Active Rental:

```text
A: 2026-09-10 — 2026-09-12
B: 2026-09-12 — 2026-09-14
```

Ожидается конфликт.

Затем:

```text
A: 2026-09-10 — 2026-09-12
C: 2026-09-13 — 2026-09-14
```

Ожидается успешное сохранение C.

Так ученик проверяет именно формулу интервала, а не один случай из середины периода.

---

# 12. Проверить, что Planned не резервирует Equipment

Создайте:

```text
Rental P
Start Date : 2026-09-11
End Date   : 2026-09-13
Status     : Planned
Equipment  : EQ-00001
```

Несмотря на существующий Active Rental A на 10–12 сентября, Planned Rental должен сохраниться.

Теперь у Rental P измените:

```text
Planned → Active
```

и нажмите Save.

Ожидается конфликт.

Это важная проверка lifecycle:

```text
создание Planned допустимо
↓
изменение состояния на Active
↓
validate() повторно проверяет реальное текущее состояние
```

Не нужен отдельный custom endpoint `activate_rental` только ради этой проверки.

---

# 13. Проверить Returned

Создайте или переведите контрольный Rental в:

```text
Returned
```

Такой Rental не должен блокировать другое Active бронирование по текущей семантике CORE.

Ещё раз:

```text
Returned не блокирует
```

— это наше предметное решение, а не свойство статуса Frappe.

---

# 14. Проверить отсутствие self-conflict

Откройте существующий валидный Active Rental A.

Измените поле, которое не создаёт нового конфликта, например Customer, либо оставьте тот же период и просто сохраните Document повторно.

Ожидается успешное сохранение.

Если Rental блокирует сам себя, реализация V03 неверна.

---

# 15. Проверить серверный путь без Form

На S05C уже доказано, что Controller вызывается обычным `Document.insert()`.

Для V03 повторим ключевую проверку.

Откройте:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Используйте пользователя, который имеет Create Rental, например:

```python
frappe.set_user("operator@example.test")
```

Найдите один существующий Customer и Equipment:

```python
customer = frappe.get_all("Customer", pluck="name", limit_page_length=1)[0]
equipment = frappe.get_all("Equipment", pluck="name", limit_page_length=1)[0]
```

Создайте контрольный Active Rental на свободном периоде, например:

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

В интерактивном console успешную контрольную запись можно явно зафиксировать:

```python
frappe.db.commit()
```

Этот `commit()` относится **только к ручной работе в console**. Его не должно быть в Rental Controller: обычным web request/job transaction boundary управляет Frappe.

Теперь попробуйте конфликт:

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

Ожидается:

```text
BLOCKED V03: ...already used in another Active Rental...
```

Критический вывод:

```text
Form не участвовал
Client Script не участвовал
правило всё равно сработало
```

---

# 16. Почему это ещё НЕ защита от гонки

Рассмотрим две параллельные транзакции:

```text
T1 проверяет конфликты → ничего нет
T2 проверяет конфликты → ничего нет
T1 сохраняет Active Rental
T2 сохраняет Active Rental
```

Обычный запрос в `validate()` сам по себе не доказывает, что такой сценарий невозможен.

Поэтому S06 гарантирует только:

```text
последовательное сохранение
→ уже существующий конфликт обнаруживается
```

Он **не заявляет**:

```text
строгая сериализация конкурентных бронирований
```

Для production-системы с реальной параллельной выдачей может понадобиться отдельное решение:

```text
transaction/locking strategy
reservation model
serializable critical section
другая доказанная схема конкурентного доступа
```

Выбор зависит от реального требования и профиля нагрузки.

В CORE не добавляем SQL locks или reservation service только для демонстрации этих механизмов.

---

# 17. Что нельзя делать для «усиления» V03

## Не делать ручной `commit()` в Controller

Это не решает гонку и ломает обычную transaction boundary Frappe.

## Не использовать Client Script как единственную проверку

Другой server path обойдёт browser logic.

## Не проверять только Rentals, которые видит пользователь

Инвариант базы не должен исчезать из-за permission filtering.

## Не писать ручной SQL без необходимости

Текущее условие выражается штатным Database API.

## Не создавать `Equipment Reservation` заранее

Отдельный reservation Document может быть правильной production-моделью при другом требовании, но сейчас это новая сущность без доказанной необходимости.

---

# 18. Git checkpoint

После изменения Controller:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training diff -- \
  rental_training/rental_training/doctype/rental/rental.py
```

Проверьте, что изменился только ожидаемый business behavior.

Затем:

```bash
git -C apps/rental_training add \
  rental_training/rental_training/doctype/rental/rental.py

git -C apps/rental_training commit \
  -m "feat: prevent overlapping active rentals"
```

После commit:

```bash
git -C apps/rental_training status --short
```

Ожидается пустой вывод.

Как и на S05C, schema не менялась. `bench migrate` не нужен просто из-за изменения Python Controller.

---

# 19. ГОТОВО

S06 принят, если одновременно доказано следующее.

## Бизнес-правило

```text
одно Equipment
+
два пересекающихся периода
+
оба Rental = Active
→ второй save запрещён
```

## Граница интервала

```text
10–12 и 12–14 → конфликт
10–12 и 13–14 → допустимо
```

## Состояние

```text
Planned overlapping → допустимо
Planned → Active при конфликте → запрещено
Returned overlapping → не блокирует
```

## Редактирование

Существующий Active Rental не конфликтует сам с собой.

## Серверный путь

Конфликт блокируется обычным `Document.insert()` без Form/Client Script.

## Архитектура

Ученик объясняет:

```text
почему V03 читает другие Documents
почему get_all здесь выбран намеренно
почему пользовательский List всё равно не следует строить через get_all
почему validate-check ≠ concurrency guarantee
```

## Source

`rental.py` находится в Git, рабочее дерево App чистое.

---

# 20. НЕ ГОТОВО

S06 не принят, если:

- конфликт проверяется только JavaScript-кодом формы;
- текущий Rental конфликтует сам с собой;
- общая граничная дата ошибочно считается непересечением;
- Planned или Returned блокируют Equipment вопреки зафиксированной CORE-семантике;
- проверка зависит от того, видит ли пользователь другой Rental в List;
- в Controller появился ручной `frappe.db.commit()`;
- заявлено, что обычная `validate()` полностью решает конкурентное бронирование;
- ради одного запроса появился отдельный Rule Engine/Reservation Service без нового требования;
- изменение Controller не находится в Git.

---

# 21. Что изменилось после S06

До S06 Rental защищал только своё внутреннее состояние:

```text
V01 dates
V02 duplicate Equipment
```

После S06:

```text
Rental.validate()
├── V01 local
├── V02 local
└── V03 cross-document
```

Теперь CORE имеет все три согласованных бизнес-инварианта.

Следующий этап — S07.

На нём ручные проверки S05C/S05D/S06 превращаются в повторяемые автоматические контракты Frappe test runner:

```text
valid Rental
invalid dates
duplicate Equipment
overlapping Active Rental
non-overlapping Active Rental
permissions
```
