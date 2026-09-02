# S05C. Защитить инварианты одного Rental на серверном пути

До S05C приложение уже умеет хранить Rental и работать с ним через стандартный Desk:

```text
Rental
├── customer   → Link → Customer
├── start_date → Date
├── end_date   → Date
├── status     → Select
└── items      → Table MultiSelect → Rental Item
                                     └── equipment → Link → Equipment
```

Но сама структура полей ещё не гарантирует два предметных правила:

```text
V01  end_date >= start_date
V02  одно Equipment не повторяется внутри одного Rental
```

Это первая точка CORE, где появляется собственный Python-код.

Он появляется **не потому, что закончились low-code возможности**, а потому, что возникла новая ответственность:

> Некорректный Rental нельзя сохранить независимо от того, через какой интерфейс он создаётся.

Для поведения собственного DocType штатный первый механизм Frappe — его `Document Controller`, а естественная lifecycle-точка для проверки инвариантов — `validate()`.

Связанные документы:

- [`S04_RENTAL_COMPOSITION.md`](S04_RENTAL_COMPOSITION.md);
- [`S05B_DESK_VERTICAL_SCENARIO.md`](S05B_DESK_VERTICAL_SCENARIO.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md`](../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md).

Первичные источники:

- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py

---

# 1. Что именно должен гарантировать Controller

## V01. Корректный период

Допустимо:

```text
Start Date = 2026-09-20
End Date   = 2026-09-20
```

и:

```text
Start Date = 2026-09-20
End Date   = 2026-09-22
```

Недопустимо:

```text
Start Date = 2026-09-20
End Date   = 2026-09-18
```

Формула:

```text
end_date >= start_date
```

## V02. Equipment не повторяется внутри Rental

Допустимо:

```text
EQ-00001
EQ-00002
```

Недопустимо:

```text
EQ-00003
EQ-00003
```

`Table MultiSelect` может помогать пользователю выбирать набор значений, но серверная целостность приложения не должна зависеть от поведения конкретного browser control.

---

# 2. Почему `validate()`

Frappe `Document` проходит controller lifecycle при обычных `insert()` и `save()`.

В актуальном исходнике v16.33.0 `Document.insert()` прямо описывает, что выполняет `validate`, а `Document.save()` также выполняет `validate` перед обновлением.

Поэтому требование:

```text
неправильный Rental нельзя сохранить
```

естественно выражается:

```text
Rental Controller
└── validate()
```

Это отличается от Client Script:

```text
Client Script
= ранняя подсказка/удобство конкретной Form

Controller.validate()
= серверная гарантия обычного Document-пути
```

На S05C Client Script не нужен.

---

# 3. Входная проверка

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Site:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте Git:

```bash
git -C apps/rental_training status --short
```

После принятого S05B рабочее дерево App должно быть чистым.

Проверьте Controller Rental:

```bash
test -f \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.py \
  && echo 'Rental controller: OK'
```

Ожидается:

```text
Rental controller: OK
```

Посмотрите текущий файл:

```bash
sed -n '1,220p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.py
```

После создания Standard DocType там уже должен существовать класс `Rental`, наследующий `Document`. До S05C собственного поведения в нём быть не должно.

---

# 4. Не создавать новый слой ради двух правил

Нам сейчас не нужны:

```text
RentalService
RentalValidator
Rule Engine
Validation Registry
Server Script
Hook на собственный Rental
отдельный Validation DocType
```

Почему:

```text
правила относятся к состоянию одного Rental
Rental принадлежит нашему App
Frappe уже дал Rental собственный Controller
```

Значит первый владелец ответственности — сам Controller Rental.

Service станет кандидатом только если появится действительно отдельная сложная ответственность, например координация многих типов Documents.

---

# 5. Отредактировать `rental.py`

Откройте файл:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── rental/
                └── rental.py
```

Приведите содержательную часть Controller к следующему виду:

```python
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class Rental(Document):
    def validate(self):
        self.validate_date_range()
        self.validate_duplicate_equipment()

    def validate_date_range(self):
        if self.start_date and self.end_date and getdate(self.end_date) < getdate(self.start_date):
            frappe.throw(_("End Date cannot be before Start Date."))

    def validate_duplicate_equipment(self):
        equipment = [row.equipment for row in self.items if row.equipment]

        if len(equipment) != len(set(equipment)):
            frappe.throw(_("The same Equipment cannot be selected more than once in one Rental."))
```

Существующий copyright/license header, который сгенерировал ваш App, сохраняйте.

---

# 6. Разобрать код по ответственности

## `validate()`

```python
def validate(self):
    self.validate_date_range()
    self.validate_duplicate_equipment()
```

`validate()` здесь остаётся короткой точкой lifecycle и перечисляет инварианты текущего Document.

Мы не превращаем её в одну длинную функцию на десятки правил.

## Проверка периода

```python
if self.start_date and self.end_date and getdate(self.end_date) < getdate(self.start_date):
```

Почему используется `getdate()`:

- правило сравнивает именно даты;
- код не должен опираться на случайное строковое представление значения;
- `getdate` — штатная утилита Frappe для получения date-value.

Проверка `if self.start_date and self.end_date` не заменяет Mandatory metadata. Она только не заставляет наш инвариант падать на пустом значении раньше штатной проверки обязательных полей.

## Проверка дублей

```python
equipment = [row.equipment for row in self.items if row.equipment]
```

`self.items` — дочерние строки Rental Item, даже несмотря на то что пользователь работает с ними через `Table MultiSelect`.

Затем сравниваются:

```text
количество выбранных Equipment
```

и:

```text
количество уникальных Equipment
```

Если числа различаются, внутри одного Rental есть повтор.

---

# 7. Почему сообщения идут через `frappe.throw()`

Нужно не просто вычислить `False`, а прервать сохранение Document понятной ошибкой.

Используется штатный механизм:

```python
frappe.throw(...)
```

Он поднимает validation exception и останавливает обычный save/insert path.

Строки обёрнуты в `_()` как пользовательские сообщения, которые могут участвовать в механизме переводов Frappe.

На S05C не создаётся собственный класс исключения: для двух обычных ошибок валидации это не добавляет новой ответственности.

---

# 8. Что намеренно отсутствует в Controller

В `validate()` не должно появиться:

```text
frappe.db.commit()
ignore_permissions=True
ручной SQL UPDATE
создание другого Rental
отправка HTTP-запроса
Notification
Workflow logic
проверка пересечений других Rentals
```

Последний пункт особенно важен.

S05C содержит только локальные инварианты одного Rental.

Проверка других Rentals — другой класс ответственности и отдельный этап S06.

---

# 9. Нужно ли выполнять `bench migrate`

На S05C мы **не меняли DocType metadata или схему БД**.

Изменился только Python Controller:

```text
rental.py
```

Поэтому не нужно выполнять `bench migrate` как ритуальный шаг после каждого изменения Python.

В dev-среде процесс должен загрузить новую версию Python-кода. Если запущенный web process не подхватил изменение автоматически, перезапустите `bench start`/dev processes обычным способом.

Главная граница:

```text
изменили schema/metadata
→ migrate имеет смысл для синхронизации состояния Site

изменили только Python behavior
→ схема не изменилась
```

---

# 10. Проверить V01 через Desk

Откройте существующий валидный Rental или создайте новый Planned Rental.

Задайте:

```text
Start Date : 2026-09-20
End Date   : 2026-09-18
```

Нажмите **Save**.

Ожидается ошибка со смыслом:

```text
End Date cannot be before Start Date.
```

Document не должен сохраниться с неправильным периодом.

Исправьте:

```text
End Date : 2026-09-22
```

и сохраните.

Ожидается успешное сохранение.

Так мы видим happy path и ошибку через Form, но этого ещё недостаточно, чтобы доказать серверную гарантию.

---

# 11. Проверить V02 через Desk — если control позволяет сформировать дубль

Попробуйте выбрать одно Equipment дважды в одном Rental.

Например:

```text
Lenovo ThinkPad E14
Lenovo ThinkPad E14
```

Возможны два нормальных результата:

1. `Table MultiSelect` сам не даёт сформировать одинаковый выбор в UI;
2. UI позволяет сформировать его, но серверный `validate()` блокирует Save.

Первый результат **не отменяет серверное правило**.

Browser control — не единственный путь создания Document.

Поэтому обязательная доказательная проверка V02 выполняется следующим разделом через серверный API `Document.insert()`.

---

# 12. Проверить оба инварианта без Form

Откройте отдельный Bench console:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Для этой проверки используем Administrator: здесь проверяется controller invariant, а не permissions.

```python
frappe.set_user("Administrator")
```

Найдите существующие ссылки для контрольных Documents:

```python
customer = frappe.db.get_value(
    "Customer",
    {"customer_name": "Mark de Vries"},
    "name",
)

equipment = frappe.db.get_value(
    "Equipment",
    {"equipment_name": "Lenovo ThinkPad E14"},
    "name",
)

print(customer, equipment)
```

Оба значения должны быть непустыми.

Если вы сознательно переименовали эти runtime-записи на предыдущих этапах, выберите любой существующий Customer/Equipment через `frappe.get_all()` и используйте их реальные `name`.

---

# 13. Server check V01 — неправильный период

В том же console:

```python
bad_dates = frappe.get_doc(
    {
        "doctype": "Rental",
        "customer": customer,
        "start_date": "2026-10-05",
        "end_date": "2026-10-04",
        "status": "Planned",
        "items": [{"equipment": equipment}],
    }
)
```

Попробуйте обычный `insert()`:

```python
try:
    bad_dates.insert()
except frappe.ValidationError as exc:
    print("BLOCKED V01:", exc)
    frappe.db.rollback()
```

Ожидается ошибка периода.

Критический факт:

```text
мы не открывали Form
мы не запускали Client Script
Document.insert() всё равно заблокирован
```

Значит правило действительно живёт на серверном Document path.

---

# 14. Server check V02 — повтор Equipment

Создайте второй несохранённый Document:

```python
duplicate_equipment = frappe.get_doc(
    {
        "doctype": "Rental",
        "customer": customer,
        "start_date": "2026-10-05",
        "end_date": "2026-10-06",
        "status": "Planned",
        "items": [
            {"equipment": equipment},
            {"equipment": equipment},
        ],
    }
)
```

Попробуйте:

```python
try:
    duplicate_equipment.insert()
except frappe.ValidationError as exc:
    print("BLOCKED V02:", exc)
    frappe.db.rollback()
```

Ожидается сообщение со смыслом:

```text
The same Equipment cannot be selected more than once in one Rental.
```

Здесь мы намеренно сформировали Document программно, не полагаясь на ограничения Table MultiSelect UI.

---

# 15. Почему после exception вызывается rollback в console

Обычный web request управляет транзакцией на уровне Framework: успешный write request коммитится в конце, а необработанное исключение приводит к rollback.

Но в интерактивном console мы сами ловим exception через `try/except`.

После этого исключение уже не является необработанным для внешнего runner, поэтому учебный код явно возвращает текущую console-транзакцию в чистое состояние:

```python
frappe.db.rollback()
```

Это **не** означает, что controller должен делать rollback самостоятельно.

В Controller нет:

```python
frappe.db.rollback()
frappe.db.commit()
```

Транзакционная ответственность остаётся у внешнего request/job/test path.

---

# 16. Выйти из console

После двух проверок:

```python
exit()
```

Ни `bad_dates`, ни `duplicate_equipment` не должны появиться в Rental List как сохранённые Documents.

---

# 17. Проверить изменение Git

Теперь source App **должен** измениться, в отличие от S05B.

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Ожидается изменение:

```text
rental_training/rental_training/doctype/rental/rental.py
```

Посмотрите diff:

```bash
git -C apps/rental_training diff -- \
  rental_training/rental_training/doctype/rental/rental.py
```

На S05C это правильно:

```text
новое обязательное поведение Rental
→ App-owned Controller source
→ Git diff
```

При этом `rental.json` не обязан меняться, потому что схема на этом этапе не изменялась.

---

# 18. Зафиксировать Controller в Git

Перейдите в App:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
```

Добавьте только изменение Controller:

```bash
git add \
  rental_training/rental_training/doctype/rental/rental.py
```

Проверьте staged diff:

```bash
git diff --cached
```

Зафиксируйте:

```bash
git commit -m "feat: validate rental invariants"
```

Проверьте:

```bash
git status --short
```

Ожидается чистое рабочее дерево.

---

# 19. Три типовые ошибки

## Ошибка 1. Проверять даты только Client Script

```text
Form не даёт выбрать неправильную дату
```

но `Document.insert()` принимает её.

Это UI-защита, а не инвариант модели.

## Ошибка 2. Писать отдельный Rule Engine

Для двух локальных правил одного собственного DocType вводится новая абстракция, хотя Controller уже является штатным владельцем lifecycle Rental.

## Ошибка 3. Использовать `frappe.db.commit()` внутри `validate()`

`validate()` должен проверить Document, а не частично фиксировать транзакцию.

Ручной commit разрушил бы нормальную возможность внешнего request/job path откатить операцию целиком при последующей ошибке.

---

# 20. Три правильных решения

## Правильно 1. Инвариант принадлежит серверному пути

```text
end_date >= start_date
→ Rental.validate()
```

## Правильно 2. Использовать child rows как часть Document

```text
self.items
→ Rental Item Documents
→ row.equipment
```

Не нужен отдельный запрос к child table только для проверки дублей внутри уже загруженного Rental.

## Правильно 3. Отделить локальное правило от междокументного

```text
S05C
текущий Rental
→ даты + свои items

S06
текущий Rental + другие Rentals
→ конфликт периодов
```

Не смешивать весь будущий booking subsystem в первый `validate()`.

---

# 21. Контрольная карта S05C

```text
[ ] rental.py найден в App source
[ ] validate() добавлен в Controller Rental
[ ] V01 проверяет end_date >= start_date
[ ] V02 проверяет уникальность row.equipment внутри self.items
[ ] неправильная дата блокируется через Form
[ ] валидная дата сохраняется
[ ] V01 блокируется через Document.insert()
[ ] V02 блокируется через Document.insert()
[ ] Client Script не является единственной защитой
[ ] нет Service/Rule Engine без новой ответственности
[ ] нет ручного commit/SQL в Controller
[ ] rental.py виден в Git diff
[ ] controller зафиксирован commit'ом
```

---

# 22. ГОТОВО

S05C принят, если одновременно выполнено всё ниже.

## Инварианты

Нельзя сохранить Rental с:

```text
end_date < start_date
```

и нельзя сохранить Rental с одним Equipment дважды.

## Серверная гарантия

Оба правила доказаны через обычный серверный:

```python
Document.insert()
```

без Form и Client Script.

## Архитектурный владелец

Ученик объясняет:

```text
собственный DocType
+ локальный invariant его состояния
→ Controller.validate()
```

## Delivery

Обязательное поведение находится в:

```text
rental_training/.../doctype/rental/rental.py
```

и зафиксировано в Git.

---

# 23. НЕ ГОТОВО

S05C не принят, если:

- неправильную дату блокирует только браузер;
- программный `Document.insert()` обходит V01 или V02;
- проверка дублей зависит только от Table MultiSelect control;
- ради двух правил создан собственный validation framework;
- `validate()` выполняет ручной `commit`;
- правило записано только как Site-local Server Script;
- Controller изменён локально, но не зафиксирован в Git;
- в S05C уже протащено междокументное правило S06.

---

# 24. Что изменилось после S05C

Схема данных осталась прежней:

```text
Equipment
Customer
Rental
└── Rental Item
```

Но Rental впервые получил собственное обязательное поведение:

```text
Rental Document
    ↓
Controller.validate()
    ├── validate_date_range()
    └── validate_duplicate_equipment()
```

Это первая точка практикума, где собственный Python действительно оправдан предметной ответственностью.

Следующий независимый этап в исполняемом маршруте — S05D:

```text
Rental Operator
Rental Manager
      ↓
Role + DocType Permissions
```

После S05D появятся две защищённые стороны модели:

```text
что является допустимым Document → S05C
кто имеет право выполнять операции → S05D
```

И только после этого S06 добавит первый инвариант, который читает **другие Rentals**.