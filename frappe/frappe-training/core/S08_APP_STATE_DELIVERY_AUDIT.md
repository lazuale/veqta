# S08. Доказать, что обязательное состояние принадлежит App

К S08 приложение уже работает, защищает свои инварианты, применяет permissions и имеет автоматические тесты.

```text
модель
+ Controller
+ permissions
+ tests
```

Но пока всё это разрабатывалось на одном `rental.localhost`.

Новое требование:

> Для каждого обязательного элемента CORE нужно знать владельца, source of truth и штатный путь, по которому он попадёт на другой Site.

S08 не добавляет новую функцию. Это проверка архитектуры поставки перед финальной чистой установкой S09.

Связанные документы:

- [`S05D_ROLES_AND_PERMISSIONS.md`](S05D_ROLES_AND_PERMISSIONS.md);
- [`S07_AUTOMATED_CONTRACT_TESTS.md`](S07_AUTOMATED_CONTRACT_TESTS.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations
- https://docs.frappe.io/framework/user/en/bench/reference/migrate
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/installer.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/migrate.py

---

# 1. Что значит «принадлежит App»

Не вся информация на Site должна находиться в Git.

Нужно разделить две категории.

## Обязательное состояние продукта

Без него `rental_training` после установки не соответствует своему контракту.

Примеры CORE:

```text
Module Rental Training
Equipment / Customer / Rental / Rental Item
поля и naming
DocType Permissions
Rental Controller V01/V02/V03
Rental Operator / Rental Manager
автоматические tests
```

Такое состояние должно иметь воспроизводимый источник в App.

## Состояние конкретного Site

Оно существует потому, что на Site реально работают люди и создаются данные.

Примеры:

```text
конкретные Users
конкретные Equipment
конкретные Customer
конкретные Rental
пароли
allow_tests
developer_mode
текущие значения naming counters
```

Эти данные не становятся fixtures только потому, что они есть на dev-site.

Главная формула S08:

```text
обязательное для продукта
→ App-owned

конкретный экземпляр / пользователь / операция
→ Site-owned
```

---

# 2. Delivery manifest CORE

До любых команд зафиксируем ожидаемую карту.

| Элемент | Владелец | Source of truth | Как попадает на Site |
|---|---|---|---|
| App `rental_training` | App | repository / Python package | App доступен Bench, затем `install-app` |
| Module `Rental Training` | App | `rental_training/modules.txt` | `install-app` создаёт/синхронизирует Module Def |
| `Equipment` | App | `equipment.json` | Standard DocType sync при install/migrate |
| `Customer` | App | `customer.json` | Standard DocType sync при install/migrate |
| `Rental Item` | App | `rental_item.json` | Standard DocType sync при install/migrate |
| `Rental` | App | `rental.json` | Standard DocType sync при install/migrate |
| naming / fields / default DocPerm | App | JSON соответствующего Standard DocType | sync metadata/schema |
| V01/V02/V03 | App | `rental.py` | Python source App |
| `Rental Operator` | App | role name в Standard DocPerm | `make_module_and_roles()` создаёт missing Role при sync |
| `Rental Manager` | App | role name в Standard DocPerm | `make_module_and_roles()` создаёт missing Role при sync |
| automated contracts | App | `test_rental.py` | запускаются Frappe test runner |
| test Users | Site/test data | database test environment | создаются test case, не fixture |
| реальные Users | Site | database Site | создаёт администратор Site |
| Equipment/Customer/Rental records | Site | database Site | создают пользователи/интеграции |
| `developer_mode` | Site | site config | локальная настройка dev Site |
| `allow_tests` | Site | site config | локальная настройка test Site |

Это не абстрактная таблица. Дальше каждую строку нужно подтвердить исходниками и фактическим состоянием.

---

# 3. Входная проверка

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Apps текущего Site:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте тесты:

```bash
bench --site rental.localhost run-tests --app rental_training
```

На S08 нельзя начинать проверку поставки с уже сломанным приложением.

Проверьте Git:

```bash
git -C apps/rental_training status --short
```

Рабочее дерево должно быть чистым.

Если оно не чистое, сначала определите владельца каждого изменения и либо зафиксируйте принятое App-owned изменение, либо уберите случайный мусор.

---

# 4. Проверить Module как App-owned state

Откройте:

```bash
cat apps/rental_training/rental_training/modules.txt
```

В CORE ожидается:

```text
Rental Training
```

Это source of truth списка Modules App.

Текущий Frappe при `install_app()` вызывает добавление Module Def из module list App до синхронизации его DocTypes.

Поэтому обязательный Module не должен создаваться отдельным ручным пунктом инструкции установки.

Проверьте runtime Site через console:

```bash
bench --site rental.localhost console
```

```python
frappe.db.exists("Module Def", "Rental Training")
```

Ожидается truthy result.

Завершите console:

```python
exit()
```

---

# 5. Проверить Standard DocTypes и metadata в Git

Из корня App:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
```

Проверьте обязательные JSON:

```bash
for file in \
  rental_training/rental_training/doctype/equipment/equipment.json \
  rental_training/rental_training/doctype/customer/customer.json \
  rental_training/rental_training/doctype/rental_item/rental_item.json \
  rental_training/rental_training/doctype/rental/rental.json
do
  test -f "$file" && echo "OK  $file" || echo "MISSING  $file"
done
```

Все четыре строки должны быть `OK`.

## Что находится в этих JSON

Именно metadata Standard DocType задаёт, в частности:

```text
fields
field types
Link/Table MultiSelect options
naming
Title Field
Is Child Table
required flags
default permissions
```

Не нужно создавать отдельный SQL schema-файл приложения.

Frappe при install/migrate синхронизирует DocTypes из JSON и приводит схему Site к этому metadata-state.

---

# 6. Проверить runtime metadata после sync

Вернитесь в Bench:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Выполните:

```python
core_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]

frappe.get_all(
    "DocType",
    filters={"name": ["in", core_doctypes]},
    fields=["name", "module", "custom", "istable"],
    order_by="name asc",
)
```

Смысл ожидаемого результата:

```text
Equipment   → Module Rental Training, Standard, normal DocType
Customer    → Module Rental Training, Standard, normal DocType
Rental      → Module Rental Training, Standard, normal DocType
Rental Item → Module Rental Training, Standard, Child DocType
```

`custom` не должен показывать, что эти четыре сущности являются случайными Custom DocTypes Site.

---

# 7. Проверить default permissions как часть Standard metadata

В той же console:

```python
roles = {"Rental Operator", "Rental Manager"}

for doctype in ["Equipment", "Customer", "Rental"]:
    print(f"\n{doctype}")
    for perm in frappe.get_meta(doctype).permissions:
        if perm.role in roles:
            print(
                perm.role,
                "read=", perm.read,
                "create=", perm.create,
                "write=", perm.write,
                "delete=", perm.delete,
            )
```

Ожидаемая матрица:

```text
Equipment
Operator → R---
Manager  → CRUD

Customer
Operator → RCU-  (Read/Create/Write, no Delete)
Manager  → CRUD

Rental
Operator → RCU-  (Read/Create/Write, no Delete)
Manager  → CRUD
```

Точная форма вывода Python не является контрактом. Контракт — значения permission rows.

Почему это важно:

```text
default permissions продукта
→ rental_training Standard DocType JSON

не
→ локальный Role Permission Manager override
```

---

# 8. Проверить отсутствие скрытых Site-customizations CORE

Мы создавали собственные Standard DocTypes напрямую в developer mode.

Поэтому обязательные поля и default permissions не должны тайно зависеть от:

```text
Custom Field
Property Setter
Custom DocPerm
```

В console выполните:

```python
targets = ["Equipment", "Customer", "Rental", "Rental Item"]

checks = [
    ("Custom Field", "dt"),
    ("Property Setter", "doc_type"),
    ("Custom DocPerm", "parent"),
]

for doctype, target_field in checks:
    rows = frappe.get_all(
        doctype,
        filters={target_field: ["in", targets]},
        fields=["name", target_field],
    )
    print(doctype, rows)
```

Для принятого CORE ожидается:

```text
Custom Field    []
Property Setter []
Custom DocPerm  []
```

Если здесь есть записи, не удаляйте их вслепую.

Сначала ответьте:

```text
кто их создал?
зачем они нужны?
они относятся к обязательному продукту или к локальному Site?
какой механизм должен быть source of truth?
```

S08 не принимает скрытую обязательную настройку только потому, что «на dev-site всё работает».

Завершите console:

```python
exit()
```

---

# 9. Проверить Controller как source поведения

В App:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

sed -n '1,280p' \
  rental_training/rental_training/doctype/rental/rental.py
```

В Controller должны оставаться три CORE-инварианта:

```text
V01 date range
V02 duplicate Equipment
V03 overlapping Active Rental
```

Проверьте Git tracking:

```bash
git ls-files \
  rental_training/rental_training/doctype/rental/rental.py
```

Файл должен выводиться.

Python behavior не нужно экспортировать fixture или дублировать Server Script.

```text
поведение собственного Standard DocType
→ Controller собственного App
```

---

# 10. Проверить provisioning Role из Standard DocPerm

В S05D имена:

```text
Rental Operator
Rental Manager
```

были добавлены в `permissions[]` собственных Standard DocTypes.

Проверьте source:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

grep -R '"role": "Rental Operator"' \
  rental_training/rental_training/doctype/equipment \
  rental_training/rental_training/doctype/customer \
  rental_training/rental_training/doctype/rental

grep -R '"role": "Rental Manager"' \
  rental_training/rental_training/doctype/equipment \
  rental_training/rental_training/doctype/customer \
  rental_training/rental_training/doctype/rental
```

В Frappe v16.33.0 `make_module_and_roles()` собирает имена ролей из permission rows и создаёт отсутствующие `Role`. Для новой роли Framework задаёт `desk_access = 1`.

При `install-app` сначала выполняется `sync_for()` Standard metadata, а `sync_fixtures()` идёт позже.

Поэтому для текущего CORE source роли выглядит так:

```text
Standard DocType JSON
└── permissions[]
    └── role name
          ↓
      sync_for()
          ↓
make_module_and_roles()
          ↓
missing Role
```

Проверьте, что этот путь не продублирован отдельным fixture:

```bash
grep -n -A20 -B5 'fixtures' rental_training/hooks.py || true

test ! -f rental_training/fixtures/role.json \
  && echo "OK: no redundant role fixture" \
  || echo "CHECK: role fixture exists"
```

Если `role.json` существует, не удаляйте файл вслепую: сначала убедитесь, что он не поставляет самостоятельное состояние Role, которого нет в Standard DocPerm. В текущем CORE такого дополнительного требования нет.

---

# 11. Проверить, что Users не стали App-owned конфигурацией

В App не должно быть source-файла, превращающего учебных Users в обязательную конфигурацию продукта.

Проверьте:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
find rental_training/fixtures -maxdepth 1 -type f -print 2>/dev/null | sort
```

Наличие каталога `fixtures` само по себе нормально, если App использует его для другой оправданной конфигурации.

Но не должно появляться fixture, превращающего в продукт:

```text
operator@example.test
manager@example.test
пароли
любого реального сотрудника
```

Почему:

```text
Role name в Standard DocPerm
→ часть permission model App

User
→ участник конкретного Site
```

---

# 12. Проверить, что business data не экспортированы

CORE runtime data:

```text
Equipment Documents
Customer Documents
Rental Documents
Rental Item rows
```

не являются fixtures продукта.

Поэтому не должно существовать fixture-файлов вроде:

```text
equipment.json
customer.json
rental.json
```

в каталоге `rental_training/fixtures/` только ради того, чтобы новый Site выглядел заполненным.

Не путайте два одинаковых расширения `.json`:

```text
rental_training/.../doctype/equipment/equipment.json
→ metadata Standard DocType
→ App-owned

rental_training/fixtures/equipment.json
→ records Equipment
→ в CORE такого fixture быть не должно
```

Это принципиально разные уровни.

---

# 13. Naming: правило принадлежит App, счётчик — Site

В metadata находится правило именования:

```text
Equipment → EQ-.#####
Customer  → CUST-.#####
Rental    → RENT-.#####
```

Но новый чистый Site **не обязан продолжать номера dev-site**.

Например наличие на dev-site:

```text
EQ-00037
```

не означает, что чистая установка должна начать с:

```text
EQ-00038
```

Текущие business records и runtime sequence state принадлежат конкретному Site.

Контракт App — стратегия naming, а не перенос текущего operational counter.

---

# 14. Site config не является source продукта

Проверьте текущую конфигурацию:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost show-config
```

На учебном Site могут быть:

```text
developer_mode
allow_tests
DB credentials
installed_apps
другие локальные параметры
```

Не копируйте `site_config.json` в repository App как способ «поставить приложение».

В частности:

```text
developer_mode
allow_tests
```

нужны этому dev/test Site, но не являются обязательной бизнес-конфигурацией `rental_training`.

---

# 15. Выполнить migrate как round-trip source → Site

В development Bench `migrate` проверяет доступность необходимых сервисов. Если `bench start` уже работает в отдельном терминале, ничего делать не нужно.

Если процессы Bench не запущены, откройте отдельный терминал и выполните:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Оставьте этот терминал открытым на время migrate и последующих проверок. Это инфраструктура dev-окружения, а не скрытая настройка `rental_training`.

Теперь запускаем штатную синхронизацию уже существующего Site:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost migrate
```

В текущем Frappe v16 migrate включает, среди прочего:

```text
before_migrate hooks
patches
DocType/schema sync
jobs
fixtures
customizations
after_migrate hooks
```

После успешного migrate снова запустите:

```bash
bench --site rental.localhost run-tests --app rental_training
```

И проверьте Git:

```bash
git -C apps/rental_training status --short
```

Ожидается чистое дерево.

Смысл проверки:

```text
Git/App source
   ↓ migrate
текущий Site
   ↓ tests
контракты работают
```

`migrate` не должен требовать ручного SQL или повторного накликивания обязательных полей/permissions.

---

# 16. Нужен ли CORE patch сейчас?

Откройте:

```bash
sed -n '1,240p' \
  apps/rental_training/rental_training/patches.txt
```

В CORE мы **не добавляем patch только ради знакомства с patches**.

Patch нужен, когда существует реальная задача:

```text
старое поддерживаемое состояние данных
        ↓
новая версия App ожидает другое состояние
        ↓
существующие записи надо преобразовать один раз
```

Например в будущем:

```text
старый status = Issued
новая модель = Active
```

и реальные существующие Rentals должны быть преобразованы.

## Почему сейчас patch не нужен

CORE строит первую исходную версию учебного App.

`rental.localhost` — dev/test Site, на котором мы по ходу обучения меняли модель. Он не объявлен поддерживаемой предыдущей production-версией продукта.

Поэтому не нужно писать ретроспективный patch для каждого учебного изменения только потому, что на dev-site уже существовала пара тестовых записей.

Главное доказательство первого baseline будет в S09:

```text
clean Site
+ current App source
→ корректная установка с нуля
```

После появления реально поддерживаемой предыдущей версии миграции данных становятся отдельным обязательным контрактом релиза.

---

# 17. Не использовать ручной SQL как delivery mechanism

В S08 запрещено считать нормальным способом поставки:

```text
install app
→ открыть MariaDB
→ ALTER TABLE ...
→ UPDATE ...
→ вручную вставить permissions
```

Если schema принадлежит Standard DocType, её source — JSON + sync/migrate.

Если обязательная конфигурация действительно требует fixture, её source — fixture JSON.

Если старые данные надо преобразовать — кандидат patch.

Ручной SQL может существовать как осознанный специальный инструмент, но не как скрытая штатная инструкция установки CORE.

---

# 18. Составить собственную карту поставки

Перед S09 ученик должен заполнить таблицу фактическими путями своего App.

| Обязательный элемент | Owner | Source file | Runtime destination | Проверено |
|---|---|---|---|---|
| Rental Training Module | App | `modules.txt` | `Module Def` | [ ] |
| Equipment | App | `equipment.json` | DocType/table/meta | [ ] |
| Customer | App | `customer.json` | DocType/table/meta | [ ] |
| Rental Item | App | `rental_item.json` | Child DocType/table/meta | [ ] |
| Rental | App | `rental.json` | DocType/table/meta | [ ] |
| V01/V02/V03 | App | `rental.py` | Document lifecycle | [ ] |
| Operator/Manager roles | App | role names в Standard DocType JSON | Role records через sync | [ ] |
| CRUD defaults | App | DocType JSON | permission engine | [ ] |
| automated contracts | App | `test_rental.py` | test runner | [ ] |
| Users | Site | database | User | [ ] |
| business records | Site | database | Documents | [ ] |
| developer/test config | Site | site config | Site runtime | [ ] |

Если для обязательной строки нет понятного source of truth, S08 не пройден.

---

# 19. Контрольная последовательность S08

Перед запуском блока ниже `bench start` должен работать в отдельном терминале, если процессы Bench не были запущены ранее.

Из Bench:

```bash
cd ~/frappe/rental-training-bench

printf '\n=== SITE APPS ===\n'
bench --site rental.localhost list-apps -f text

printf '\n=== MODULE SOURCE ===\n'
cat apps/rental_training/rental_training/modules.txt

printf '\n=== APP FILES ===\n'
for file in \
  rental_training/rental_training/doctype/equipment/equipment.json \
  rental_training/rental_training/doctype/customer/customer.json \
  rental_training/rental_training/doctype/rental_item/rental_item.json \
  rental_training/rental_training/doctype/rental/rental.json \
  rental_training/rental_training/doctype/rental/rental.py \
  rental_training/rental_training/doctype/rental/test_rental.py
do
  test -f "apps/rental_training/$file" \
    && echo "OK      $file" \
    || echo "MISSING $file"
done

printf '\n=== ROLE SOURCE ===\n'
grep -R '"role": "Rental Operator"' \
  apps/rental_training/rental_training/rental_training/doctype/{equipment,customer,rental} || true
grep -R '"role": "Rental Manager"' \
  apps/rental_training/rental_training/rental_training/doctype/{equipment,customer,rental} || true

printf '\n=== REDUNDANT ROLE FIXTURE ===\n'
test ! -f apps/rental_training/rental_training/fixtures/role.json \
  && echo "OK: no redundant role fixture" \
  || echo "CHECK: role fixture exists"

printf '\n=== MIGRATE ===\n'
bench --site rental.localhost migrate

printf '\n=== TESTS ===\n'
bench --site rental.localhost run-tests --app rental_training

printf '\n=== FINAL APP GIT ===\n'
git -C apps/rental_training status --short
```

После принятого S08:

```text
все обязательные файлы → OK
role names в DocPerm     → найдены
лишний Role fixture      → отсутствует
migrate                  → success
tests                    → green
final Git                → clean
```

---

# 20. S08 — ГОТОВО

Переход к чистой установке S09 разрешён, если одновременно верно:

```text
[ ] Module имеет source в modules.txt
[ ] четыре Standard DocTypes имеют JSON в App
[ ] naming/fields/default permissions находятся в Standard metadata
[ ] Rental Controller V01/V02/V03 tracked by Git
[ ] Rental Operator/Rental Manager находятся в Standard DocPerm
[ ] отдельный Role fixture не дублирует эти имена
[ ] Users не экспортированы как fixtures
[ ] business data не экспортированы как fixtures
[ ] developer_mode/allow_tests остаются Site-local
[ ] нет скрытых обязательных Custom Field / Property Setter / Custom DocPerm
[ ] Bench services доступны перед migrate
[ ] bench migrate проходит
[ ] tests после migrate проходят
[ ] App Git остаётся clean
[ ] patches.txt не содержит фиктивной миграции «для галочки»
[ ] ученик может объяснить, почему patch сейчас не нужен
```

---

# 21. S08 — НЕ ГОТОВО

Не переходите к S09, если:

- обязательное поле существует только на dev-site;
- обязательная Role после install должна создаваться вручную;
- default permissions держатся только на локальном override;
- добавлен Role fixture только для имён, уже находящихся в Standard DocPerm;
- `fixture` содержит Users или обычные Rentals без продуктового требования;
- runtime records считаются частью source App;
- `site_config.json` копируется как способ установки продукта;
- `migrate` требует ручного SQL;
- tests после migrate падают;
- существует обязательная настройка, для которой нельзя назвать owner/source/delivery path;
- patch написан только для демонстрации механизма.

---

# 22. Что ученик должен понять после S08

Не достаточно сказать:

```text
«у меня всё работает»
```

Нужно уметь показать:

```text
что является продуктом
↓
где это хранится
↓
кто этим владеет
↓
как Framework применяет это к Site
↓
как проверить результат
```

Именно поэтому Frappe App — не просто папка с Python-кодом.

В нашем CORE приложение состоит из нескольких штатных типов source state:

```text
modules.txt
DocType JSON
Python Controller
Frappe-aware tests
```

а Site — из собственного экземплярного состояния:

```text
Users
business Documents
site config
installed app state
runtime naming state
```

S08 доказывает, что мы понимаем эту границу.

S09 останется сделать последнее: взять **новый чистый Site, на котором ничего из CORE раньше не создавалось**, установить текущий App и проверить, что delivery manifest действительно восстанавливает обязательное состояние без скрытых ручных шагов.
