# S09. Проверить приложение на новом чистом Site

S08 показал, откуда должен восстанавливаться каждый обязательный элемент приложения.

Теперь это нужно проверить на новом Site, где `rental_training` раньше не создавался вручную.

> Новый Site должен получить обязательную модель из текущего App и пройти те же проверки без скрытых восстановительных действий.

Связанные документы:

- [`S08_APP_STATE_DELIVERY.md`](S08_APP_STATE_DELIVERY.md);
- [`S07_AUTOMATED_CONTRACT_TESTS.md`](S07_AUTOMATED_CONTRACT_TESTS.md);
- [`S05D_ROLES_AND_PERMISSIONS.md`](S05D_ROLES_AND_PERMISSIONS.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../ROADMAP.md`](../ROADMAP.md);
- [`../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- https://docs.frappe.io/framework/user/en/bench/reference/new-site
- https://docs.frappe.io/framework/user/en/bench/reference/migrate
- https://docs.frappe.io/framework/user/en/testing
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/site.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/installer.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/migrate.py

---

# 1. Что проверяет S09

До S09 всё разрабатывалось на:

```text
rental.localhost
```

Там мы вручную создавали DocTypes, меняли метаданные и писали Controller.

Поэтому факт:

```text
rental.localhost работает
```

ещё не доказывает:

```text
App воспроизводим
```

На S09 создаётся второй Site:

```text
rental-clean.localhost
```

Он находится в том же совместимом Bench, но имеет:

```text
свою БД
свой site_config.json
свой набор установленных Apps
своих Users
свои рабочие Documents
```

На нём никогда не создавались `Equipment`, `Customer`, `Rental`, роли или permissions вручную.

## Что здесь не проверяется

S09 не является проверкой промышленного развёртывания и не охватывает:

```text
reverse proxy
TLS
backup/restore
отдельный сервер
HA
container image
CI pipeline
remote Git hosting
OS bootstrap с нуля
```

S00 уже зафиксировал совместимую среду. S09 проверяет **воспроизводимость Frappe App на чистом Site**.

Граница проверки:

```text
совместимый Bench
+ зафиксированные исходники App
+ чистый Site
→ воспроизводимое обязательное состояние App
```

---

# 2. Зафиксировать исходную версию App

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Framework:

```bash
bench version --format plain
```

Для этого практикума Framework должен оставаться на зафиксированной линии:

```text
16.33.0
```

Теперь проверьте репозиторий App:

```bash
git -C apps/rental_training status --short
git -C apps/rental_training rev-parse HEAD
```

Первая команда должна ничего не вывести.

Вторая выдаст commit SHA текущего состояния `rental_training`.

Скопируйте SHA в свои заметки как контрольную точку S09.

## Почему это важно

Проверяется:

```text
конкретное зафиксированное состояние App
```

а не:

```text
папка с незакоммиченными локальными правками
```

Если Git не чист, сначала разберите изменения.

Важно: `rental_training` в этом практикуме имеет собственный Git-репозиторий внутри Bench. Именно его commit фиксируется как состояние приложения; репозиторий документации VEQTA не заменяет Git-историю самого учебного App.

---

# 3. Убедиться, что developer mode включён только там, где нужен

Разработка Standard DocTypes требует developer mode на `rental.localhost`, но новый контрольный Site не должен зависеть от режима разработки.

Проверьте общий конфиг Bench:

```bash
grep -n 'developer_mode' sites/common_site_config.json || true
```

`developer_mode` не должен быть глобальной обязательной настройкой.

Если вы проходили старую версию S00 и там осталось глобальное значение, исправьте окружение:

```bash
bench set-config -g developer_mode None
bench --site rental.localhost set-config developer_mode 1
bench --site rental.localhost clear-cache
```

Проверьте Site разработки:

```bash
bench --site rental.localhost show-config | grep developer_mode
```

Ожидается `1`/`true` только для `rental.localhost`.

### Архитектурный смысл

```text
создание Standard metadata
→ задача разработки
→ Site разработки

использование установленного App
→ обычная работа Site
→ developer mode не требуется
```

Если чистая установка требует включить developer mode, граница разработки и поставки сломана.

---

# 4. Создать новый Site без `rental_training`

Сначала убедитесь, что имя ещё не занято:

```bash
test ! -d sites/rental-clean.localhost \
  && echo "OK: clean Site does not exist yet" \
  || echo "STOP: clean Site already exists"
```

Если Site уже существует, **не используйте `--force` и не переустанавливайте его молча**. Проверка должна начинаться с действительно нового экземпляра.

Создайте Site:

```bash
bench new-site rental-clean.localhost \
  --db-root-username frappe_admin
```

Bench запросит:

1. пароль MariaDB-пользователя `frappe_admin`;
2. новый пароль Frappe `Administrator` для контрольного Site.

Не используйте пароль MariaDB как пароль Administrator.

Не добавляйте здесь:

```text
--install-app rental_training
--set-default
```

Нам нужна промежуточная точка **до установки App**.

---

# 5. Проверить чистое состояние до установки

Проверьте установленные Apps:

```bash
bench --site rental-clean.localhost list-apps -f text
```

Ожидается ровно:

```text
frappe
```

Наличие `rental_training` в каталоге `apps/` Bench ничего не меняет:

```text
App доступен Bench
≠
App установлен на Site
```

Это та же граница, которую мы впервые увидели в S01, но теперь она проверяется на готовом App.

## Проверить отсутствие DocTypes и Role учебного приложения

Откройте console нового Site:

```bash
bench --site rental-clean.localhost console
```

Выполните:

```python
app_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]
app_roles = ["Rental Operator", "Rental Manager"]

print("Installed Apps:", frappe.get_installed_apps())

for doctype in app_doctypes:
    print("DocType", doctype, frappe.db.exists("DocType", doctype))

for role in app_roles:
    print("Role", role, frappe.db.exists("Role", role))
```

До установки смысл результата должен быть таким:

```text
Installed Apps: ['frappe']

Equipment   → нет
Customer    → нет
Rental      → нет
Rental Item → нет

Rental Operator → нет
Rental Manager  → нет
```

Завершите:

```python
exit()
```

Если эти сущности уже существуют, Site не является чистой контрольной площадкой.

---

# 6. Проверить, что контрольный Site не использует developer mode

Выполните:

```bash
bench --site rental-clean.localhost show-config | grep developer_mode || true
```

При правильной настройке ожидается отсутствие включённого `developer_mode`.

Если вывод показывает `1`/`true`, не продолжайте установку, пока не выясните источник.

Частая причина — старый глобальный ключ в `common_site_config.json`. Исправление приведено в разделе 3.

Не включайте developer mode на контрольном Site «чтобы точно заработало» — это уничтожит смысл проверки.

---

# 7. Установить `rental_training`

Теперь выполняем единственное действие, которое должно принести модель приложения на Site:

```bash
bench --site rental-clean.localhost install-app rental_training
```

Проверьте:

```bash
bench --site rental-clean.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

## Что Frappe делает сам

В актуальном Frappe v16 `install_app()` штатно:

```text
добавляет Module Def из списка Modules App
→ синхронизирует Standard metadata App
→ регистрирует App на Site
→ синхронизирует jobs
→ синхронизирует fixtures, если App их использует
→ синхронизирует exported customizations
```

Для нашего приложения важны прежде всего:

```text
modules.txt
→ Module Def

DocType JSON
→ DocType / schema / default permissions
→ имена Role внутри permissions[]
→ отсутствующие Role создаются make_module_and_roles()

Python-код
→ поведение Controller
```

В Frappe v16.33.0 `install_app()` выполняет `sync_for()` до `sync_fixtures()`. При sync Standard DocType `make_module_and_roles()` собирает роли из permission rows, создаёт отсутствующие `Role` и задаёт им `desk_access = 1`.

Поэтому отдельный `fixtures/role.json` для `Rental Operator` и `Rental Manager` текущему приложению не нужен.

Никаких ручных действий между этими пунктами быть не должно.

---

# 8. Проверить состояние сразу после install-app

Откройте console:

```bash
bench --site rental-clean.localhost console
```

## 8.1. Module

```python
frappe.db.exists("Module Def", "Rental Training")
```

Ожидается непустой результат.

## 8.2. Standard DocTypes

```python
app_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]

frappe.get_all(
    "DocType",
    filters={"name": ["in", app_doctypes]},
    fields=["name", "module", "custom", "istable"],
    order_by="name asc",
)
```

Должно быть четыре DocTypes.

Смысл:

```text
Equipment   → Rental Training / Standard / обычный
Customer    → Rental Training / Standard / обычный
Rental      → Rental Training / Standard / обычный
Rental Item → Rental Training / Standard / Child
```

## 8.3. Role из Standard DocPerm

```python
for role in ["Rental Operator", "Rental Manager"]:
    print(role, frappe.db.exists("Role", role))
```

Обе Role должны существовать **до того, как мы создадим хоть одного User**.

Они должны появиться как следствие синхронизации Standard DocTypes, в `permissions[]` которых находятся эти имена Role.

Если приходится открывать `Role` и создавать их вручную, поставка приложения не воспроизводится.

## 8.4. Permissions по умолчанию

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

Ожидается:

```text
Equipment
Operator → Read only
Manager  → CRUD

Customer
Operator → Read/Create/Write
Manager  → CRUD

Rental
Operator → Read/Create/Write
Manager  → CRUD
```

## 8.5. Нет скрытых локальных настроек

```python
targets = ["Equipment", "Customer", "Rental", "Rental Item"]

for doctype, target_field in [
    ("Custom Field", "dt"),
    ("Property Setter", "doc_type"),
    ("Custom DocPerm", "parent"),
]:
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

Завершите console:

```python
exit()
```

---

# 9. Перед migrate убедиться, что процессы Bench запущены

В учебном Bench `migrate` требует доступности необходимых сервисов, включая Redis cache.

Если `bench start` уже работает в отдельном терминале — ничего делать не нужно.

Если не работает, откройте второй терминал и запустите:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Оставьте этот терминал открытым до конца S09.

Это не часть `rental_training` и не скрытая зависимость App:

```text
сервисы Bench
→ инфраструктура учебного окружения

метаданные и Controller App
→ исходники приложения
```

Не путайте ошибку вида «Redis service недоступен» с ошибкой архитектуры чистой установки.

---

# 10. Выполнить migrate как отдельную проверку пути обновления

`install-app` уже синхронизировал обязательное состояние при первичной установке.

Поэтому следующая команда не является «магическим вторым install».

Мы запускаем её, чтобы проверить ещё одно свойство:

> Текущее зафиксированное состояние App можно безопасно провести через обычный `migrate` без ручного восстановления модели.

Выполните:

```bash
bench --site rental-clean.localhost migrate
```

Ожидается успешное завершение без:

```text
ручного ALTER TABLE
ручного UPDATE
создания Role через Desk
создания Custom Field
правки DocType на контрольном Site
```

После migrate снова проверьте Apps:

```bash
bench --site rental-clean.localhost list-apps -f text
```

Должны остаться:

```text
frappe
rental_training
```

---

# 11. Включить только настройку тестов и запустить весь набор

На контрольном Site не нужен developer mode.

Для штатного test runner нужна только настройка конкретного Site:

```bash
bench --site rental-clean.localhost set-config allow_tests 1 --parse
```

Проверьте:

```bash
bench --site rental-clean.localhost show-config | grep allow_tests
```

Теперь запустите все тесты App:

```bash
bench --site rental-clean.localhost run-tests --app rental_training
```

Тесты должны пройти **на Site, где приложение до установки вообще не существовало**.

Этой командой повторно проверяются:

```text
V01: неверный период
V02: повтор Equipment
V03: пересечение Active Rentals
V03: общая граничная дата
V03: непересекающиеся периоды
пересечение Planned
повторное сохранение Active Rental
permissions Operator
permissions Manager
```

Если тесты проходят только на `rental.localhost`, но падают здесь — чистая установка не воспроизводится.

---

# 12. Проверить, что тесты не изменили исходники App

```bash
git -C apps/rental_training status --short
```

Ожидается пустой вывод.

Тесты могут создавать временные записи БД в своём жизненном цикле, но не должны переписывать зафиксированную модель приложения.

---

# 13. Открыть Desk нового Site

`bench start` уже должен работать после раздела 9.

Откройте:

```text
http://rental-clean.localhost:8000/app
```

Войдите как:

```text
Administrator
```

с паролем, заданным при создании `rental-clean.localhost`.

Не открывайте старый `rental.localhost`: финальный сценарий должен пройти именно на новом Site.

---

# 14. Убедиться, что модель доступна без developer mode

Через Awesomebar найдите:

```text
Equipment
Customer
Rental
```

Откройте List каждого DocType.

Они должны существовать и открываться без создания Workspace, Custom Page или собственного frontend.

Не нужно открывать `DocType` и «досохранять» модель.

Правильное состояние:

```text
install-app уже привёз метаданные
↓
Desk уже умеет Form/List
```

Если для появления полей требуется открыть DocType и нажать Save, чистая установка не воспроизводится.

---

# 15. Создать двух Users этого Site

Role уже должны быть на Site после синхронизации Standard DocPerm.

Теперь создаются **только участники этого Site**.

Используйте тот же штатный путь User, что в S05D.

## Operator

```text
Email              : operator.clean@example.test
First Name         : Rental Operator Test
User Type          : System User
Send Welcome Email : off
Role               : Rental Operator
```

Не назначайте:

```text
Rental Manager
System Manager
```

## Manager

```text
Email              : manager.clean@example.test
First Name         : Rental Manager Test
User Type          : System User
Send Welcome Email : off
Role               : Rental Manager
```

Не назначайте:

```text
Rental Operator
System Manager
```

Для каждого пользователя задайте локальный учебный пароль через штатный механизм User.

Пароли:

- не записываются в App;
- не экспортируются fixture;
- не добавляются в Git.

После создания Users проверьте исходники App:

```bash
git -C apps/rental_training status --short
```

Рабочее дерево должно оставаться чистым.

---

# 16. Пройти основной сценарий под Rental Manager

Выйдите из Administrator и войдите как:

```text
manager.clean@example.test
```

## 16.1. Создать Equipment №1

```text
Equipment Name : Test Bosch Drill
Equipment Type : Tool
Serial Number  : CLEAN-TOOL-01
```

Сохраните и запомните сгенерированный `name`.

Не предполагаем заранее, что это обязательно `EQ-00001`: состояние счётчиков принадлежит Site.

## 16.2. Создать Equipment №2

```text
Equipment Name : Test Canon Camera
Equipment Type : Camera
Serial Number  : CLEAN-CAM-01
```

Сохраните.

## 16.3. Создать Customer

```text
Customer Name : Test Customer
Phone         : +31 6 10000901
Email         : clean.customer@example.test
```

Сохраните.

## 16.4. Создать первый Active Rental

```text
Customer   : Test Customer
Start Date : 2026-10-10
End Date   : 2026-10-12
Status     : Active
Equipment:
- Test Bosch Drill
- Test Canon Camera
```

Сохраните.

Результат:

```text
Manager
→ создаёт Equipment
→ создаёт Customer
→ создаёт Rental
→ выбирает реальные Links
→ сохраняет Active Rental
```

Это полноценный сквозной сценарий на новом Site.

---

# 17. Проверить именование и отображение Links

Откройте сохранённый Rental.

Убедитесь:

1. Customer показывается человекочитаемым title;
2. Equipment показываются человекочитаемыми title;
3. у Customer/Equipment/Rental существуют стабильные системные `name` по заданным naming expressions;
4. UI не хранит копию названия вместо Link.

Не требуйте совпадения конкретных номеров с Site разработки.

Правильная гарантия:

```text
стратегия именования воспроизводится
счётчик остаётся локальным для Site
```

---

# 18. Проверить Operator через Desk

Выйдите и войдите как:

```text
operator.clean@example.test
```

## Equipment

Operator должен иметь возможность читать существующие Equipment.

Создавать новый Equipment он не должен.

В Desk это может проявиться как отсутствие `Add/New` либо отказ операции — точная подача интерфейса вторична.

Серверная гарантия уже повторно проверена автоматическими тестами на этом же Site.

## Customer

Создайте:

```text
Customer Name : Operator Test Customer
Phone         : +31 6 10000902
Email         : operator.customer@example.test
```

Ожидание: сохраняется.

## Rental

Создайте непересекающийся Rental:

```text
Customer   : Operator Test Customer
Start Date : 2026-10-13
End Date   : 2026-10-14
Status     : Active
Equipment:
- Test Bosch Drill
```

Ожидание: сохраняется, потому что предыдущий Active Rental закончился 12 октября.

Измените:

```text
End Date : 2026-10-15
```

и сохраните.

Ожидание: Write разрешён.

Удалять Rental Operator не должен.

Если Delete action не показывается — это нормальный эффект permissions. Серверный запрет уже проверяется автоматическим тестом.

---

# 19. Проверить V03 через обычный пользовательский сценарий

Оставаясь под Operator, создайте ещё один Rental:

```text
Customer   : Operator Test Customer
Start Date : 2026-10-11
End Date   : 2026-10-13
Status     : Active
Equipment:
- Test Canon Camera
```

`Test Canon Camera` уже находится в Active Rental Manager за период:

```text
2026-10-10 → 2026-10-12
```

Периоды пересекаются.

Ожидается отказ сохранения с бизнес-ошибкой V03.

Это показывает сразу две вещи:

```text
правило приехало из rental.py
+
правило работает через обычный путь Document в Desk
```

Для контрольного Site мы не создавали:

```text
Client Script
Server Script
Workflow
ручной SQL trigger
локальный validator
```

---

# 20. Где проверяются V01 и V02

Не нужно снова вручную перебирать каждое поле только ради количества действий.

На **этом же `rental-clean.localhost`** уже выполнялась команда:

```bash
bench --site rental-clean.localhost run-tests --app rental_training
```

Она проверила:

```text
V01: неверная дата → отказ
V02: повтор Equipment → отказ
V03: пересечение → отказ
```

Ручная проверка V03 в Desk нужна здесь как сквозной пользовательский сценарий.

Автоматические тесты остаются главным повторяемым способом проверки всех трёх правил.

---

# 21. Проверить состояние, принадлежащее Site

После пользовательского сценария откройте console:

```bash
bench --site rental-clean.localhost console
```

Проверьте:

```python
print("Apps", frappe.get_installed_apps())
print("Equipment", frappe.db.count("Equipment"))
print("Customer", frappe.db.count("Customer"))
print("Rental", frappe.db.count("Rental"))

for user in [
    "operator.clean@example.test",
    "manager.clean@example.test",
]:
    print(user, frappe.db.exists("User", user))
```

Точные значения после test runner не являются архитектурным контрактом.

Здесь важно другое:

```text
рабочие Documents и Users появились уже после установки
→ они принадлежат этому Site
```

Завершите:

```python
exit()
```

---

# 22. Финально проверить исходники App

Вернитесь в терминал:

```bash
cd ~/frappe/rental-training-bench
```

Выполните:

```bash
printf '\n=== APP COMMIT ===\n'
git -C apps/rental_training rev-parse HEAD

printf '\n=== APP GIT ===\n'
git -C apps/rental_training status --short

printf '\n=== CLEAN SITE APPS ===\n'
bench --site rental-clean.localhost list-apps -f text

printf '\n=== CLEAN SITE CONFIG ===\n'
bench --site rental-clean.localhost show-config | \
  grep -E 'developer_mode|allow_tests' || true
```

Ожидаемый смысл:

```text
commit App       → тот же, с которого начинали S09
Git              → чист
Apps             → frappe + rental_training
developer_mode   → не включён
allow_tests      → 1/true
```

Создание Users, Equipment, Customer и Rental не должно менять репозиторий App.

---

# 23. Ещё раз запустить автоматические тесты

После ручного пользовательского сценария снова выполните:

```bash
bench --site rental-clean.localhost run-tests --app rental_training
```

Тесты должны по-прежнему проходить.

Это ловит ещё один класс ошибки:

```text
тесты проходят только на пустой БД
```

Наши тесты должны изолировать собственные данные и не зависеть от обычных Documents, созданных пользователем.

---

# 24. Итоговая таблица S09

| Проверка | Ожидание |
|---|---|
| Site до install | только `frappe` |
| DocTypes приложения до install | отсутствуют |
| Role приложения до install | отсутствуют |
| developer mode | не нужен контрольному Site |
| `install-app rental_training` | выполняется успешно |
| Module | появляется из App |
| 4 Standard DocTypes | появляются из JSON |
| Role Operator/Manager | появляются из Standard DocPerm при sync |
| permissions по умолчанию | соответствуют JSON |
| скрытые Custom Field/Property Setter/Custom DocPerm | отсутствуют |
| сервисы Bench перед migrate | доступны |
| `migrate` | проходит без ручного SQL |
| тесты | проходят |
| сквозной сценарий Manager | проходит |
| ограничения Operator | соответствуют модели |
| V03 в Desk | конфликт блокируется |
| Users и рабочие данные | остаются на Site |
| Git App после всего | чист |

---

# 25. Итоговая проверка практикума

Практикум завершён, если одновременно верно:

```text
[ ] создан новый rental-clean.localhost
[ ] до install-app на нём был только frappe
[ ] до install-app DocTypes и Role приложения отсутствовали
[ ] контрольный Site не требует developer_mode
[ ] репозиторий App был чистым и его commit SHA зафиксирован
[ ] rental_training установился штатной командой install-app
[ ] Module Rental Training появился без ручного создания
[ ] Equipment появился из App
[ ] Customer появился из App
[ ] Rental Item появился из App
[ ] Rental появился из App
[ ] именование, поля и permissions по умолчанию соответствуют метаданным App
[ ] Rental Operator появился из Standard DocPerm sync
[ ] Rental Manager появился из Standard DocPerm sync
[ ] отдельный Role fixture для этих имён не требуется
[ ] скрытых обязательных Custom Field/Property Setter/Custom DocPerm нет
[ ] сервисы Bench доступны перед migrate
[ ] bench migrate проходит
[ ] тесты проходят на контрольном Site
[ ] Users создаются после установки и не входят в App
[ ] Manager проходит Equipment → Customer → Rental
[ ] Operator видит Equipment, но не может создавать его
[ ] Operator может создавать и изменять Customer и Rental
[ ] Operator не может удалять Rental
[ ] пересекающийся Active Rental блокируется через Desk
[ ] тесты остаются зелёными после создания обычных Documents
[ ] Git App остаётся чистым после всех действий на Site
```

---

# 26. Когда S09 не завершён

Сначала исправьте причину, если обязательный шаг звучит так:

```text
«после install откройте DocType и ещё раз Save»
«создайте обязательные Role вручную»
«добавьте отсутствующее поле через Customize Form»
«поправьте permissions через Role Permission Manager»
«включите developer mode, иначе установленное App не работает»
«выполните этот ALTER TABLE вручную»
«скопируйте Users с Site разработки»
«скопируйте старые EQ/CUST/RENT записи как fixtures»
```

Также этап не завершён, если:

- тесты проходят только на старом `rental.localhost`;
- новый Site требует локальный Server Script для V01/V02/V03;
- роли не восстанавливаются из Standard DocPerm sync;
- добавлен Role fixture только для имён, уже находящихся в Standard DocPerm;
- permissions по умолчанию зависят от локального переопределения Site;
- исходники App меняются от обычной работы пользователей;
- чистая установка работает только при незакоммиченных файлах разработчика.

---

# 27. Что ученик прошёл за весь практикум

После S09 у ученика есть не просто маленькая система проката.

Он руками прошёл причинно-следственную цепочку Frappe:

```text
реальное требование
        ↓
ответственность
        ↓
штатный механизм Frappe
        ↓
Standard metadata / Document / permissions / Controller
        ↓
сквозной сценарий Desk
        ↓
серверные правила
        ↓
автоматические тесты
        ↓
воспроизводимая поставка состояния App
        ↓
установка на чистый Site
```

Итоговая модель остаётся маленькой:

```text
Equipment
Customer
Rental
└── Rental Item
```

Но вокруг неё уже проверены важные свойства настоящего Frappe App:

```text
стабильный системный name
живые Link
композиция через Child DocType
Table MultiSelect
предметный status
серверная валидация
междокументный инвариант
Role + DocType Permissions
migrate
тесты Frappe
чистая установка
```

При этом практикум не потребовал:

```text
Workflow
Submittable/docstatus
Single Settings
Notification
Report
Print Format
Web Form
REST wrapper
Webhook
background jobs
Server Script
собственный frontend
```

Потому что ни один из этих механизмов пока не нужен для поставленных требований.

Главный результат практикума:

> Не перечислить возможности Frappe, а научиться выбирать штатный механизм по ответственности и проверять воспроизводимость решения.