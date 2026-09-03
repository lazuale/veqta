# S08. Доказать, что обязательное состояние принадлежит App

К S08 приложение уже работает, защищает свои инварианты, применяет permissions и имеет автоматические тесты.

```text
модель
+ Controller
+ permissions
+ тесты
```

Но пока всё это разрабатывалось на одном `rental.localhost`.

Новое требование:

> Для каждого обязательного элемента приложения нужно знать владельца, основной источник и штатный путь, по которому он попадёт на другой Site.

S08 не добавляет новую функцию. Это проверка архитектуры поставки перед финальной чистой установкой S09.

Связанные документы:

- [`S05D_ROLES_AND_PERMISSIONS.md`](S05D_ROLES_AND_PERMISSIONS.md);
- [`S07_AUTOMATED_CONTRACT_TESTS.md`](S07_AUTOMATED_CONTRACT_TESTS.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../ROADMAP.md`](../ROADMAP.md);
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

## Обязательное состояние приложения

Без него `rental_training` после установки не соответствует своему контракту.

Примеры:

```text
Module Rental Training
Equipment / Customer / Rental / Rental Item
поля и правила именования
DocType Permissions
Rental Controller V01/V02/V03
Rental Operator / Rental Manager
автоматические тесты
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
текущие значения счётчиков имён
```

Эти данные не становятся fixtures только потому, что они есть на Site разработки.

Главная формула S08:

```text
обязательное для приложения
→ принадлежит App

конкретный экземпляр / пользователь / операция
→ принадлежит Site
```

---

# 2. Карта поставки состояния приложения

До любых команд зафиксируем ожидаемую карту.

| Элемент | Владелец | Основной источник | Как попадает на Site |
|---|---|---|---|
| App `rental_training` | App | репозиторий / Python-пакет | App доступен Bench, затем `install-app` |
| Module `Rental Training` | App | `rental_training/modules.txt` | `install-app` создаёт или синхронизирует Module Def |
| `Equipment` | App | `equipment.json` | синхронизация Standard DocType при install/migrate |
| `Customer` | App | `customer.json` | синхронизация Standard DocType при install/migrate |
| `Rental Item` | App | `rental_item.json` | синхронизация Standard DocType при install/migrate |
| `Rental` | App | `rental.json` | синхронизация Standard DocType при install/migrate |
| именование / поля / DocPerm по умолчанию | App | JSON соответствующего Standard DocType | синхронизация метаданных и схемы |
| V01/V02/V03 | App | `rental.py` | Python-код App |
| `Rental Operator` | App | имя Role в Standard DocPerm | `make_module_and_roles()` создаёт отсутствующую Role при sync |
| `Rental Manager` | App | имя Role в Standard DocPerm | `make_module_and_roles()` создаёт отсутствующую Role при sync |
| автоматические проверки | App | `test_rental.py` | запускаются test runner Frappe |
| тестовые Users | Site / тестовые данные | БД тестового окружения | создаются test case, не fixture |
| реальные Users | Site | БД Site | создаёт администратор Site |
| Documents Equipment/Customer/Rental | Site | БД Site | создают пользователи или интеграции |
| `developer_mode` | Site | конфигурация Site | локальная настройка Site разработки |
| `allow_tests` | Site | конфигурация Site | локальная настройка тестового Site |

Дальше каждую строку нужно подтвердить исходниками и фактическим состоянием.

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

Если оно не чистое, сначала определите владельца каждого изменения и либо зафиксируйте принятое изменение App, либо уберите случайный мусор.

---

# 4. Проверить Module как состояние App

Откройте:

```bash
cat apps/rental_training/rental_training/modules.txt
```

Ожидается:

```text
Rental Training
```

Это основной источник списка Modules приложения.

Текущий Frappe при `install_app()` добавляет Module Def из списка Modules App до синхронизации его DocTypes.

Поэтому обязательный Module не должен создаваться отдельным ручным пунктом инструкции установки.

Проверьте состояние Site через console:

```bash
bench --site rental.localhost console
```

```python
frappe.db.exists("Module Def", "Rental Training")
```

Ожидается непустой результат.

Завершите console:

```python
exit()
```

---

# 5. Проверить Standard DocTypes и метаданные в Git

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

Метаданные Standard DocType задают, в частности:

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

Не нужно создавать отдельный SQL-файл схемы приложения.
Frappe при install/migrate синхронизирует DocTypes из JSON и приводит схему Site к состоянию, описанному этими метаданными.

---

# 6. Проверить метаданные Site после синхронизации

Вернитесь в Bench:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Выполните:

```python
app_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]

frappe.get_all(
    "DocType",
    filters={"name": ["in", app_doctypes]},
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

`custom` не должен показывать, что эти четыре сущности являются локальными Custom DocTypes конкретного Site.

---

# 7. Проверить permissions по умолчанию как часть Standard DocType

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
permissions приложения по умолчанию
→ JSON собственного Standard DocType

не
→ локальное переопределение через Role Permission Manager
```

---

# 8. Проверить отсутствие скрытых настроек Site

Мы создавали собственные Standard DocTypes напрямую в developer mode.

Поэтому обязательные поля и permissions по умолчанию не должны тайно зависеть от:

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

Ожидается:

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
они относятся к обязательному состоянию App или к локальному Site?
какой механизм должен быть основным источником?
```

S08 не принимает скрытую обязательную настройку только потому, что «на Site разработки всё работает».

Завершите console:

```python
exit()
```

---

# 9. Проверить Controller как источник поведения

В App:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

sed -n '1,280p' \
  rental_training/rental_training/doctype/rental/rental.py
```

В Controller должны оставаться три инварианта приложения:

```text
V01 date range
V02 duplicate Equipment
V03 overlapping Active Rental
```

Проверьте, что файл отслеживается Git:

```bash
git ls-files \
  rental_training/rental_training/doctype/rental/rental.py
```

Файл должен выводиться.

Python-поведение не нужно экспортировать fixture или дублировать Server Script.

```text
поведение собственного Standard DocType
→ Controller собственного App
```

---

# 10. Проверить создание Role из Standard DocPerm

В S05D имена:

```text
Rental Operator
Rental Manager
```

были добавлены в `permissions[]` собственных Standard DocTypes.

Проверьте исходники:

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

Для учебного приложения путь выглядит так:

```text
Standard DocType JSON
└── permissions[]
    └── имя Role
          ↓
      sync_for()
          ↓
make_module_and_roles()
          ↓
создание отсутствующей Role
```

Проверьте, что этот путь не продублирован отдельным fixture:

```bash
grep -n -A20 -B5 'fixtures' rental_training/hooks.py || true

test ! -f rental_training/fixtures/role.json \
  && echo "OK: no redundant role fixture" \
  || echo "CHECK: role fixture exists"
```

Если `role.json` существует, не удаляйте файл вслепую: сначала убедитесь, что он не поставляет самостоятельное состояние Role, которого нет в Standard DocPerm. В текущем приложении такого дополнительного требования нет.

---

# 11. Проверить, что Users не стали обязательной конфигурацией App

В App не должно быть файла, превращающего учебных Users в обязательную конфигурацию приложения.

Проверьте:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
find rental_training/fixtures -maxdepth 1 -type f -print 2>/dev/null | sort
```

Наличие каталога `fixtures` само по себе нормально, если App использует его для другой оправданной конфигурации.

Но не должно появляться fixture с:

```text
operator@example.test
manager@example.test
паролями
данными реальных сотрудников
```

Почему:

```text
имя Role в Standard DocPerm
→ часть модели permissions App

User
→ участник конкретного Site
```

---

# 12. Проверить, что рабочие данные не экспортированы

Рабочие данные Site:

```text
Equipment Documents
Customer Documents
Rental Documents
Rental Item rows
```

не являются fixtures приложения.

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
→ метаданные Standard DocType
→ принадлежит App

rental_training/fixtures/equipment.json
→ Documents Equipment
→ в текущем приложении такого fixture быть не должно
```

Это принципиально разные уровни.

---

# 13. Именование: правило принадлежит App, счётчик — Site

В метаданных находится правило именования:

```text
Equipment → EQ-.#####
Customer  → CUST-.#####
Rental    → RENT-.#####
```

Но новый чистый Site **не обязан продолжать номера Site разработки**.

Например наличие на Site разработки:

```text
EQ-00037
```

не означает, что чистая установка должна начать с:

```text
EQ-00038
```

Текущие Documents и состояние счётчиков принадлежат конкретному Site.

Контракт App — стратегия именования, а не перенос текущего значения счётчика.

---

# 14. Конфигурация Site не является источником состояния App

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

Не копируйте `site_config.json` в репозиторий App как способ «поставить приложение».

В частности:

```text
developer_mode
allow_tests
```

нужны этому Site разработки и тестирования, но не являются обязательной бизнес-конфигурацией `rental_training`.

---

# 15. Применить состояние App к Site через migrate

В учебном Bench `migrate` требует доступности необходимых сервисов. Если `bench start` уже работает в отдельном терминале, ничего делать не нужно.

Если процессы Bench не запущены, откройте отдельный терминал и выполните:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Оставьте этот терминал открытым на время migrate и последующих проверок. Это инфраструктура учебного окружения, а не скрытая настройка `rental_training`.

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
исходники App
   ↓ migrate
текущий Site
   ↓ tests
контракты работают
```

`migrate` не должен требовать ручного SQL или повторного создания обязательных полей и permissions через интерфейс.

---

# 16. Нужен ли patch сейчас?

Откройте:

```bash
sed -n '1,240p' \
  apps/rental_training/rental_training/patches.txt
```

Мы **не добавляем patch только ради знакомства с patches**.

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

Практикум строит первую исходную версию учебного App.

`rental.localhost` — Site разработки и тестирования, на котором мы по ходу обучения меняли модель. Он не объявлен предыдущей поддерживаемой версией приложения.

Поэтому не нужно писать ретроспективный patch для каждого учебного изменения только потому, что на Site разработки уже существовала пара тестовых записей.

Главная проверка первой версии будет в S09:

```text
чистый Site
+ текущие исходники App
→ корректная установка с нуля
```

После появления реально поддерживаемой предыдущей версии миграции данных становятся отдельным обязательным контрактом релиза.

---

# 17. Не использовать ручной SQL как механизм поставки

Нормальный путь установки не должен выглядеть так:

```text
install app
→ открыть MariaDB
→ ALTER TABLE ...
→ UPDATE ...
→ вручную вставить permissions
```

Если схема принадлежит Standard DocType, её источник — JSON + sync/migrate.

Если обязательная конфигурация действительно требует fixture, её источник — fixture JSON.

Если старые данные надо преобразовать — кандидат patch.

Ручной SQL может существовать как осознанный специальный инструмент, но не как скрытая штатная инструкция установки приложения.

---

# 18. Составить собственную карту поставки

Перед S09 заполните таблицу фактическими путями своего App.

| Обязательный элемент | Владелец | Исходный файл | Куда применяется | Проверено |
|---|---|---|---|---|
| Rental Training Module | App | `modules.txt` | `Module Def` | [ ] |
| Equipment | App | `equipment.json` | DocType / таблица / метаданные | [ ] |
| Customer | App | `customer.json` | DocType / таблица / метаданные | [ ] |
| Rental Item | App | `rental_item.json` | Child DocType / таблица / метаданные | [ ] |
| Rental | App | `rental.json` | DocType / таблица / метаданные | [ ] |
| V01/V02/V03 | App | `rental.py` | жизненный цикл Document | [ ] |
| роли Operator/Manager | App | имена Role в Standard DocType JSON | записи Role через sync | [ ] |
| CRUD по умолчанию | App | DocType JSON | механизм permissions | [ ] |
| автоматические проверки | App | `test_rental.py` | test runner Frappe | [ ] |
| Users | Site | БД | User | [ ] |
| рабочие Documents | Site | БД | Documents | [ ] |
| настройки разработки и тестов | Site | конфигурация Site | состояние Site | [ ] |

Если для обязательной строки нет понятного основного источника, поставка приложения ещё не определена.

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

Ожидаемый результат:

```text
все обязательные файлы → OK
имена Role в DocPerm    → найдены
лишний Role fixture     → отсутствует
migrate                 → выполняется успешно
tests                   → проходят
Git App                 → чистый
```

---

# 20. Проверка перед переходом к S09

Переход к чистой установке S09 возможен, если одновременно верно:

```text
[ ] Module имеет источник в modules.txt
[ ] четыре Standard DocTypes имеют JSON в App
[ ] именование, поля и permissions по умолчанию находятся в Standard metadata
[ ] Rental Controller V01/V02/V03 отслеживается Git
[ ] Rental Operator/Rental Manager находятся в Standard DocPerm
[ ] отдельный Role fixture не дублирует эти имена
[ ] Users не экспортированы как fixtures
[ ] рабочие данные не экспортированы как fixtures
[ ] developer_mode/allow_tests остаются локальными настройками Site
[ ] нет скрытых обязательных Custom Field / Property Setter / Custom DocPerm
[ ] сервисы Bench доступны перед migrate
[ ] bench migrate проходит
[ ] tests после migrate проходят
[ ] Git App остаётся чистым
[ ] patches.txt не содержит фиктивной миграции «для галочки»
[ ] ученик может объяснить, почему patch сейчас не нужен
```

---

# 21. Когда не переходить к S09

Сначала исправьте проблему, если:

- обязательное поле существует только на Site разработки;
- обязательная Role после install должна создаваться вручную;
- permissions по умолчанию держатся только на локальном переопределении;
- добавлен Role fixture только для имён, уже находящихся в Standard DocPerm;
- `fixture` содержит Users или обычные Rentals без требования приложения;
- рабочие Documents считаются частью исходников App;
- `site_config.json` копируется как способ установки приложения;
- `migrate` требует ручного SQL;
- tests после migrate падают;
- существует обязательная настройка, для которой нельзя назвать владельца, источник и путь поставки;
- patch написан только для демонстрации механизма.

---

# 22. Что ученик должен понять после S08

Недостаточно сказать:

```text
«у меня всё работает»
```

Нужно уметь показать:

```text
что принадлежит App
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

В учебном приложении обязательное состояние хранится несколькими штатными способами:

```text
modules.txt
DocType JSON
Python Controller
тесты Frappe
```

а Site хранит собственное экземплярное состояние:

```text
Users
рабочие Documents
site_config.json
список установленных Apps
текущее состояние счётчиков имён
```

S08 проверяет понимание этой границы.

На S09 останется последнее: взять **новый чистый Site, на котором приложение раньше не создавалось вручную**, установить текущий App и проверить, что карта поставки действительно восстанавливает обязательное состояние без скрытых ручных шагов.