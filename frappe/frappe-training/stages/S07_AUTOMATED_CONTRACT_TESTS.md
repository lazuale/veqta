# S07. Закрепить правила приложения автоматическими тестами

К S07 приложение уже умеет работать через Desk, защищает три бизнес-инварианта и имеет базовую модель permissions:

```text
Rental.validate()
├── V01  end_date >= start_date
├── V02  Equipment не повторяется внутри Rental
└── V03  Equipment не пересекается в Active Rentals

Rental Operator / Rental Manager
└── Role + DocType Permissions
```

До сих пор эти требования проверялись вручную через Desk и `bench console`.

Новое требование:

> Критические правила приложения должны проверяться повторяемо одной командой и должны явно падать, если собственное поведение приложения сломано.

S07 **не добавляет новую бизнес-функцию**. Он превращает уже существующие требования в исполняемые проверки.

Связанные документы:

- [`S05C_RENTAL_LOCAL_INVARIANTS.md`](S05C_RENTAL_LOCAL_INVARIANTS.md);
- [`S05D_ROLES_AND_PERMISSIONS.md`](S05D_ROLES_AND_PERMISSIONS.md);
- [`S06_ACTIVE_RENTAL_CONFLICT.md`](S06_ACTIVE_RENTAL_CONFLICT.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../REQUIREMENTS.md`](../REQUIREMENTS.md);
- [`../ROADMAP.md`](../ROADMAP.md);
- [`../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/testing
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/boilerplate/test_controller._py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/tests/classes/integration_test_case.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/tests/classes/context_managers.py
- https://github.com/frappe/frappe/wiki/Migrating-to-version-16#tests

---

# 1. Что именно мы тестируем

Не нужно писать тесты на всё, что видит пользователь.

Frappe сам отвечает за то, что:

```text
Document вообще умеет insert/save
Link вообще существует
Form вообще открывается
List вообще умеет показывать записи
```

Наш App добавил собственные правила. Вот их и нужно защищать.

## Данные

```text
V01  неправильный период запрещён
V02  дубль Equipment в одном Rental запрещён
V03  пересечение Active Rentals запрещено
```

## Точная семантика V03

```text
Planned  → не блокирует
Active   → блокирует
Returned → не блокирует
```

Периоды включительны:

```text
10–12 + 12–14 → конфликт
10–12 + 13–14 → допустимо
```

Повторное сохранение самого Active Rental не должно создавать конфликт с собой.

## Permissions

```text
Rental Operator
Equipment → Read
Customer  → Read/Create/Write
Rental    → Read/Create/Write

Rental Manager
Equipment → CRUD
Customer  → CRUD
Rental    → CRUD
```

Тесты должны выполнять реальные серверные операции, а не проверять наличие кнопки в Desk.

---

# 2. Почему `IntegrationTestCase`, а не старый `FrappeTestCase`

Rental-тесты:

```text
создают Documents
пишут в БД
читают другие Documents
переключают пользователей
проверяют permissions
```

Это интеграционные тесты.

В актуальном Frappe v16 используется:

```python
from frappe.tests import IntegrationTestCase
```

и:

```python
class IntegrationTestRental(IntegrationTestCase):
    ...
```

Текущая заготовка Standard DocType v16.33.0 генерирует именно такую основу.

Старый путь:

```python
from frappe.tests.utils import FrappeTestCase
```

не используем: в v16 он помечен как устаревший и готовится к удалению в v17.

Отдельный `UnitTestCase` здесь тоже был бы неправильным выбором: он предназначен для логики без взаимодействия с БД, а наши проверки специально проходят реальный путь Document и permissions.

---

# 3. Что уже создал Frappe

При создании Standard DocType `Rental` в developer mode Frappe уже создал заготовку теста рядом с Controller:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── rental/
                ├── rental.json
                ├── rental.py
                └── test_rental.py
```

Проверьте:

```bash
cd ~/frappe/rental-training-bench

sed -n '1,220p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/test_rental.py
```

В актуальном v16 ожидается основа со смыслом:

```python
from frappe.tests import IntegrationTestCase


class IntegrationTestRental(IntegrationTestCase):
    pass
```

Также заготовка содержит:

```python
EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []
```

На S07 их не заполняем без причины.

Наши Customer и Equipment для каждого теста создаются явно, поэтому тест понятен без скрытого набора заранее подготовленных рабочих записей.

---

# 4. Разрешить запуск tests на учебном Site

`allow_tests` — настройка **учебного Site**, а не обязательная конфигурация приложения.

Проверьте текущее значение:

```bash
bench --site rental.localhost show-config | grep allow_tests
```

Если параметр отсутствует или выключен:

```bash
bench --site rental.localhost set-config allow_tests 1 --parse
```

Проверьте:

```bash
bench --site rental.localhost show-config | grep allow_tests
```

Ожидаемый смысл:

```text
allow_tests = 1
```

После этого:

```bash
git -C apps/rental_training status --short
```

не должен показывать изменение App.

Почему:

```text
allow_tests
→ свойство конкретного Site разработки и тестирования
→ sites/rental.localhost/site_config.json
→ не исходники приложения
```

Не экспортируйте `allow_tests` как fixture.

---

# 5. Тестовые данные не должны зависеть от ручных данных S02–S06

Плохой тест:

```python
frappe.get_doc("Equipment", "EQ-00001")
```

Почему плохо:

```text
тест пройдёт только если
кто-то до него вручную создал EQ-00001
```

Автоматическая проверка должна сама подготовить минимальные данные, необходимые конкретному тесту.

Поэтому каждый test method получает собственные:

```text
Customer
Equipment
```

созданные в `setUp()`.

Названия `CUST-...` и `EQ-...` заранее не угадываются: тест использует `doc.name`, который вернул Frappe.

---

# 6. Записать `test_rental.py`

Откройте:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── rental/
                └── test_rental.py
```

Сохраните существующий copyright/license header, затем приведите содержательную часть к следующему виду:

```python
from uuid import uuid4

import frappe
from frappe.tests import IntegrationTestCase


EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestRental(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

        self.customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Automated Test Customer",
            }
        ).insert()

        self.equipment = frappe.get_doc(
            {
                "doctype": "Equipment",
                "equipment_name": "Automated Test Equipment",
                "equipment_type": "Tool",
            }
        ).insert()

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def make_rental(
        self,
        *,
        status="Planned",
        start_date="2026-10-10",
        end_date="2026-10-12",
        equipment=None,
        customer=None,
    ):
        equipment = equipment or [self.equipment.name]

        return frappe.get_doc(
            {
                "doctype": "Rental",
                "customer": customer or self.customer.name,
                "start_date": start_date,
                "end_date": end_date,
                "status": status,
                "items": [{"equipment": name} for name in equipment],
            }
        )

    def make_user(self, role):
        self.assertTrue(
            frappe.db.exists("Role", role),
            msg=f"Required App role is missing: {role}",
        )

        email = f"rental-{frappe.scrub(role)}-{uuid4().hex[:8]}@example.test"

        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": f"Test {role}",
                "send_welcome_email": 0,
                "user_type": "System User",
            }
        ).insert()

        user.add_roles(role)
        frappe.clear_cache(user=user.name)
        return user.name

    def test_valid_rental_can_be_saved(self):
        rental = self.make_rental().insert()
        self.assertTrue(rental.name)

    def test_end_date_before_start_date_is_rejected(self):
        rental = self.make_rental(
            start_date="2026-10-12",
            end_date="2026-10-10",
        )

        with self.assertRaises(frappe.ValidationError):
            rental.insert()

    def test_duplicate_equipment_in_same_rental_is_rejected(self):
        rental = self.make_rental(
            equipment=[self.equipment.name, self.equipment.name],
        )

        with self.assertRaises(frappe.ValidationError):
            rental.insert()

    def test_overlapping_active_rental_is_rejected(self):
        self.make_rental(
            status="Active",
            start_date="2026-11-10",
            end_date="2026-11-12",
        ).insert()

        conflict = self.make_rental(
            status="Active",
            start_date="2026-11-11",
            end_date="2026-11-13",
        )

        with self.assertRaises(frappe.ValidationError):
            conflict.insert()

    def test_touching_active_periods_are_rejected(self):
        self.make_rental(
            status="Active",
            start_date="2026-12-10",
            end_date="2026-12-12",
        ).insert()

        touching = self.make_rental(
            status="Active",
            start_date="2026-12-12",
            end_date="2026-12-14",
        )

        with self.assertRaises(frappe.ValidationError):
            touching.insert()

    def test_non_overlapping_active_rental_is_allowed(self):
        self.make_rental(
            status="Active",
            start_date="2027-01-10",
            end_date="2027-01-12",
        ).insert()

        rental = self.make_rental(
            status="Active",
            start_date="2027-01-13",
            end_date="2027-01-14",
        ).insert()

        self.assertTrue(rental.name)

    def test_planned_overlap_is_allowed(self):
        self.make_rental(
            status="Active",
            start_date="2027-02-10",
            end_date="2027-02-12",
        ).insert()

        planned = self.make_rental(
            status="Planned",
            start_date="2027-02-11",
            end_date="2027-02-13",
        ).insert()

        self.assertTrue(planned.name)

    def test_active_rental_does_not_conflict_with_itself(self):
        rental = self.make_rental(
            status="Active",
            start_date="2027-03-10",
            end_date="2027-03-12",
        ).insert()

        rental.reload()
        rental.save()

        self.assertEqual(rental.status, "Active")

    def test_operator_cannot_create_equipment(self):
        operator = self.make_user("Rental Operator")

        with self.set_user(operator):
            equipment = frappe.get_doc(
                {
                    "doctype": "Equipment",
                    "equipment_name": "Forbidden Equipment",
                    "equipment_type": "Tool",
                }
            )

            with self.assertRaises(frappe.PermissionError):
                equipment.insert()

    def test_operator_can_create_and_update_rental_but_cannot_delete_it(self):
        operator = self.make_user("Rental Operator")

        with self.set_user(operator):
            rental = self.make_rental(
                start_date="2027-04-10",
                end_date="2027-04-12",
            ).insert()

            rental.end_date = "2027-04-13"
            rental.save()

            with self.assertRaises(frappe.PermissionError):
                frappe.delete_doc("Rental", rental.name)

    def test_manager_can_manage_equipment(self):
        manager = self.make_user("Rental Manager")

        with self.set_user(manager):
            equipment = frappe.get_doc(
                {
                    "doctype": "Equipment",
                    "equipment_name": "Manager Test Equipment",
                    "equipment_type": "Tool",
                }
            ).insert()

            equipment.equipment_name = "Manager Updated Equipment"
            equipment.save()

            frappe.delete_doc("Equipment", equipment.name)

            self.assertFalse(frappe.db.exists("Equipment", equipment.name))
```

---

# 7. Разобрать структуру теста

## `setUp()`

```python
self.customer = ...insert()
self.equipment = ...insert()
```

Каждый test method получает собственные реальные Documents.

Это важно:

```text
test A не должен зависеть от того,
запускался ли раньше test B
```

Мы специально не используем `EQ-00001`, `CUST-00001` или данные, созданные вручную на предыдущих этапах.

## `make_rental()`

Это вспомогательная функция **только тестового кода**.

Она не является новым Service приложения.

Её ответственность очень узкая:

```text
собрать одинаковый тестовый Rental
и убрать повторение из test methods
```

Не переносите эту функцию в рабочий код ради «чистой архитектуры».

## `make_user()`

Тестовый User создаётся внутри теста и получает существующую Role приложения.

Ключевой момент:

```python
self.assertTrue(frappe.db.exists("Role", role))
```

Тест **не создаёт отсутствующую Role автоматически**.

Если `Rental Operator` или `Rental Manager` исчезли, тест должен сообщить о нарушенном требовании, а не тайно починить приложение.

Конкретный тестовый User остаётся тестовыми данными и не становится fixture App.

---

# 8. Почему используется `self.set_user()`

Текущий `IntegrationTestCase` предоставляет контекстный менеджер:

```python
with self.set_user(operator):
    ...
```

Он временно переключает `frappe.session.user`, а после блока восстанавливает предыдущего пользователя.

Это безопаснее шаблона:

```python
frappe.set_user(operator)
# ...
# забыли вернуть Administrator
```

который может загрязнить следующие проверки.

В `tearDown()` всё равно явно возвращаем `Administrator` как дополнительную понятную границу теста.

---

# 9. Почему здесь нет ручного `commit()` / `rollback()`

В S05C/S06 `bench console` требовал отдельно понимать границу интерактивной транзакции.

Автоматический test runner — другой контекст.

`IntegrationTestCase` предоставляет подготовку и очистку тестовой БД и управляет транзакционной инфраструктурой тестов.

Поэтому внутри обычных tests не добавляем:

```python
frappe.db.commit()
frappe.db.rollback()
```

только ради очистки данных.

Особенно нельзя встраивать `commit()` в Controller, чтобы «тест видел запись».

Если тест начинает требовать такие действия без отдельной причины, сначала нужно проверить устройство самого теста.

---

# 10. Запустить только Rental tests

Из корня Bench:

```bash
cd ~/frappe/rental-training-bench
```

Запустите test module:

```bash
bench --site rental.localhost run-tests \
  --app rental_training \
  --module rental_training.rental_training.doctype.rental.test_rental
```

Ожидается итог со смыслом:

```text
Ran ... tests

OK
```

Точное время и количество служебных строк могут отличаться.

Критерий — код завершения 0 и `OK` для нашего test module.

---

# 11. Запустить один конкретный test

При разработке быстрее запускать только сломанную проверку.

Например V01:

```bash
bench --site rental.localhost run-tests \
  --app rental_training \
  --module rental_training.rental_training.doctype.rental.test_rental \
  --test test_end_date_before_start_date_is_rejected
```

Для V03:

```bash
bench --site rental.localhost run-tests \
  --app rental_training \
  --module rental_training.rental_training.doctype.rental.test_rental \
  --test test_overlapping_active_rental_is_rejected
```

Это не другой механизм тестирования. Это тот же штатный runner с более узким набором проверок.

---

# 12. Запустить весь App

После прохождения Rental module:

```bash
bench --site rental.localhost run-tests --app rental_training
```

Это основной повторяемый набор тестов текущего учебного App.

На маленьком приложении он должен проходить полностью.

Не заменяйте эту команду запуском только одного «любимого» test method перед финальной проверкой.

---

# 13. Доказать, что тест действительно что-то защищает

Зелёный набор тестов сам по себе ещё не доказывает, что тест чувствителен к поломке.

Сделайте контролируемую временную ошибку.

Например в `rental.py` временно закомментируйте вызов:

```python
self.validate_date_range()
```

Запустите:

```bash
bench --site rental.localhost run-tests \
  --app rental_training \
  --module rental_training.rental_training.doctype.rental.test_rental \
  --test test_end_date_before_start_date_is_rejected
```

Теперь тест обязан стать красным:

```text
FAIL
```

Потому что ожидался `frappe.ValidationError`, но Rental сохранился.

После этого **обязательно восстановите Controller** и повторите команду.

Финальное состояние:

```text
правило исправно
→ test зелёный

правило намеренно сломано
→ test красный

правило восстановлено
→ test снова зелёный
```

Не коммитьте намеренно сломанный Controller.

---

# 14. Что именно доказывают тесты permissions

## Operator

Тест выполняет реальный:

```python
Equipment.insert()
```

и ожидает:

```text
frappe.PermissionError
```

Затем другой test под той же Role выполняет:

```text
Rental.insert() → разрешено
Rental.save()   → разрешено
Rental delete   → запрещено
```

То есть проверяется не UI, а фактический путь Document и delete.

## Manager

Менеджер реально выполняет:

```text
Equipment.insert()
Equipment.save()
Equipment delete
```

Это проверяет противоположную сторону матрицы permissions на том же DocType.

Мы не пишем тест «кнопка Delete видна менеджеру». Это следствие UI, а не граница безопасности.

---

# 15. Что S07 намеренно не тестирует

Не добавляйте тесты только ради количества:

```text
Frappe Form вообще существует
Frappe List вообще существует
Naming Series вообще умеет выдавать следующий номер
Link вообще хранит name
Table MultiSelect вообще умеет отображаться
frappe.throw вообще бросает exception
```

Это ответственность Framework.

Также S07 не добавляет:

```text
автоматизацию браузера и UI
Playwright
REST integration tests
тесты background workers
сложную инфраструктуру mock
CI pipeline
целевой процент coverage
performance/load tests
тест конкурентной гонки
```

Каждый такой уровень требует отдельного основания.

Особенно важно последнее:

```text
S06 честно не обещает защиту от race condition
→ S07 не должен писать test,
  который делает вид, что такая гарантия уже существует
```

---

# 16. Test records: почему не создаём отдельный учебный каталог fixtures

Frappe умеет автоматически загружать test records зависимых DocTypes, а актуальная заготовка предоставляет:

```python
EXTRA_TEST_RECORD_DEPENDENCIES
IGNORE_TEST_RECORD_DEPENDENCIES
```

Но наш набор очень мал и предметно важен.

Явный `setUp()` здесь полезнее:

```text
вижу Customer
вижу Equipment
вижу, кто их создал
вижу, какой Rental использует их
```

Не нужно заводить `test_records.json` только потому, что механизм существует.

Если позже десятки test modules начнут переиспользовать большой стабильный набор зависимостей, решение можно пересмотреть.

---

# 17. Зафиксировать тесты в Git

Посмотрите изменение:

```bash
git -C apps/rental_training diff -- \
  rental_training/rental_training/doctype/rental/test_rental.py
```

В рабочем Controller после контрольной намеренной поломки не должно остаться временной ошибки:

```bash
git -C apps/rental_training diff -- \
  rental_training/rental_training/doctype/rental/rental.py
```

Если `rental.py` отличается только из-за временного эксперимента — восстановите его до рабочего варианта.

Затем:

```bash
git -C apps/rental_training add \
  rental_training/rental_training/doctype/rental/test_rental.py

git -C apps/rental_training commit \
  -m "test: cover rental rules"
```

Проверьте:

```bash
git -C apps/rental_training status --short
```

Ожидается пустой вывод.

`allow_tests` в конфигурации Site в этот commit не входит.

---

# 18. Финальный запуск S07

После commit ещё раз:

```bash
bench --site rental.localhost run-tests --app rental_training
```

Этап не считается пройденным по старому выводу терминала до последней правки.

Финальный запуск тестов выполняется на том состоянии App, которое находится в Git.

---

# 19. Типовые ошибки новичка

## Ошибка 1. Тест использует `EQ-00001`

Проблема:

```text
автоматический test зависит от ручной истории Site
```

Правильно: создать собственный Equipment и использовать возвращённый `name`.

## Ошибка 2. Использовать старый `FrappeTestCase`

Проблема: это устаревший API текущей ветки v16.

Правильно для Document/DB tests:

```python
from frappe.tests import IntegrationTestCase
```

## Ошибка 3. Проверять только `has_permission()`

`has_permission()` полезен, но наше требование сформулировано как реальные операции.

Проверяем:

```text
insert
save
delete
```

## Ошибка 4. Создать Role внутри теста, если её нет

Тогда тест сам чинит нарушение требований App.

Правильно: обязательная Role должна уже поставляться App; её отсутствие — ошибка теста.

## Ошибка 5. Коммитить test Users как fixtures

Test User нужен запуску теста, а не установленному приложению.

## Ошибка 6. Делать `frappe.db.commit()` после каждого test insert

Это ломает нормальную изоляцию тестов и обычно не требуется.

## Ошибка 7. Один огромный `test_everything`

Если он падает, непонятно какой контракт нарушен.

Лучше один test method = один ясный результат.

## Ошибка 8. Тестировать Framework ради coverage

Количество тестов не является целью.

Цель:

```text
если наше правило сломано
→ соответствующий test обязан это обнаружить
```

---

# 20. Проверка перед S08

Перед переходом дальше одновременно должно быть верно:

```text
[ ] test_rental.py использует IntegrationTestCase
[ ] тесты не зависят от вручную созданных EQ/CUST/RENT
[ ] valid Rental сохраняется
[ ] V01 автоматически блокируется
[ ] V02 автоматически блокируется
[ ] V03 overlap автоматически блокируется
[ ] общая граничная дата автоматически считается конфликтом
[ ] непересекающийся Active Rental разрешён
[ ] Planned overlap разрешён
[ ] Active Rental не конфликтует сам с собой при save
[ ] Rental Operator не может создать Equipment
[ ] Rental Operator может insert/save Rental
[ ] Rental Operator не может удалить Rental
[ ] Rental Manager может create/write/delete Equipment
[ ] один test намеренно становился красным при поломке правила
[ ] после восстановления весь test module снова зелёный
[ ] bench --site rental.localhost run-tests --app rental_training проходит
[ ] test file находится в Git
[ ] рабочее дерево App чистое
```

Ученик должен уметь объяснить:

```text
почему эти tests используют IntegrationTestCase
почему мы тестируем собственные правила App, а не Frappe вообще
почему тест сам создаёт рабочие данные
почему Role должна существовать до permission test
почему test User не fixture
почему self.set_user лучше ручного незакрытого frappe.set_user
почему в tests нет ручных commit/rollback
почему S07 не доказывает защиту от конкурентной гонки, которой нет в S06
```

---

# 21. Когда не переходить к S08

Сначала исправьте проблему, если:

```text
тесты проходят только при наличии ручных данных Site разработки;
используется устаревший FrappeTestCase без причины;
permissions проверены только через UI;
тест сам создаёт отсутствующие обязательные Roles;
намеренная поломка V01/V02/V03 не делает соответствующий test красным;
тесты требуют ручного commit в рабочем Controller;
запускается только один test, а весь набор App падает;
в Git попали пароли Site или test Users как fixtures;
S07 заявляет защиту от конкурентной гонки, которой приложение ещё не реализует.
```

Следующий этап — **S08: проверить поставку обязательного состояния App**.

Там вопрос изменится:

```text
не «работает ли правило?»
а
«откуда на чистом Site появится каждый обязательный элемент?»
```