# S09. Доказать CORE на новом чистом Site

S08 ответил на вопрос, **откуда должен восстанавливаться каждый обязательный элемент приложения**.

S09 больше ничего не проектирует.

Теперь нужно проверить утверждение фактом:

> Новый Site, на котором CORE никогда не создавался вручную, должен получить всю обязательную модель из текущего `rental_training` и пройти те же контракты без скрытых восстановительных действий.

Это финальный экзамен CORE.

Связанные документы:

- [`S08_APP_STATE_DELIVERY_AUDIT.md`](S08_APP_STATE_DELIVERY_AUDIT.md);
- [`S07_AUTOMATED_CONTRACT_TESTS.md`](S07_AUTOMATED_CONTRACT_TESTS.md);
- [`S05D_ROLES_AND_PERMISSIONS.md`](S05D_ROLES_AND_PERMISSIONS.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

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

# 1. Что именно доказывает S09

До S09 всё разрабатывалось на:

```text
rental.localhost
```

Там мы руками создавали DocTypes, меняли metadata и писали Controller.

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
rental-acceptance.localhost
```

Он находится в том же совместимом Bench, но имеет:

```text
свою БД
свою site_config
свой набор installed Apps
свои Users
свои business Documents
```

На нём никогда не создавались `Equipment`, `Customer`, `Rental`, роли или permissions вручную.

## Что S09 НЕ доказывает

S09 не является production deployment test и не проверяет:

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

Это достаточная граница CORE:

```text
совместимый Bench
+ committed App source
+ clean Site
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

Теперь проверьте App repository:

```bash
git -C apps/rental_training status --short
git -C apps/rental_training rev-parse HEAD
```

Первая команда должна ничего не вывести.

Вторая выдаст commit SHA текущего состояния `rental_training`.

Скопируйте SHA в свои заметки как контрольную точку S09.

## Почему это важно

Мы хотим проверить:

```text
конкретное committed состояние App
```

а не:

```text
папку с незакоммиченными локальными правками
```

Если Git не clean, S09 не начинается.

Важно: `rental_training` в этом практикуме имеет собственный Git repository внутри Bench. Именно его commit фиксируется как source приложения; Git repository документации VEQTA не заменяет Git-историю самого учебного App.

---

# 3. Убедиться, что developer mode не протекает на весь Bench

Разработка Standard DocTypes требует developer mode на `rental.localhost`, но acceptance-site не должен зависеть от режима разработки.

Проверьте общий конфиг Bench:

```bash
grep -n 'developer_mode' sites/common_site_config.json || true
```

Для актуальной версии практикума `developer_mode` не должен быть глобальной обязательной настройкой.

Если вы проходили старую версию S00 и там осталось глобальное значение, исправьте окружение:

```bash
bench set-config -g developer_mode None
bench --site rental.localhost set-config developer_mode 1
bench --site rental.localhost clear-cache
```

Проверьте dev-site:

```bash
bench --site rental.localhost show-config | grep developer_mode
```

Ожидается `1`/`true` только для `rental.localhost`.

### Архитектурный смысл

```text
создание Standard metadata
→ developer responsibility
→ dev Site

использование установленного App
→ runtime responsibility
→ developer mode не требуется
```

Если чистая установка требует включить developer mode, граница разработки и поставки сломана.

---

# 4. Создать новый Site без `rental_training`

Сначала убедитесь, что имя ещё не занято:

```bash
test ! -d sites/rental-acceptance.localhost \
  && echo "OK: acceptance Site does not exist yet" \
  || echo "STOP: acceptance Site already exists"
```

Если Site уже существует, **не используйте `--force` и не переустанавливайте его молча**. Финальная проверка должна начинаться с действительно нового экземпляра.

Создайте Site:

```bash
bench new-site rental-acceptance.localhost \
  --db-root-username frappe_admin
```

Bench запросит:

1. пароль MariaDB-пользователя `frappe_admin`;
2. новый пароль Frappe `Administrator` для acceptance-site.

Не используйте пароль MariaDB как пароль Administrator.

Не добавляйте здесь:

```text
--install-app rental_training
--set-default
```

Нам специально нужна промежуточная точка **до установки App**.

---

# 5. Доказать чистое состояние ДО установки

Проверьте installed Apps:

```bash
bench --site rental-acceptance.localhost list-apps -f text
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

## Проверить отсутствие CORE metadata и Role

Откройте console нового Site:

```bash
bench --site rental-acceptance.localhost console
```

Выполните:

```python
core_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]
core_roles = ["Rental Operator", "Rental Manager"]

print("Installed Apps:", frappe.get_installed_apps())

for doctype in core_doctypes:
    print("DocType", doctype, frappe.db.exists("DocType", doctype))

for role in core_roles:
    print("Role", role, frappe.db.exists("Role", role))
```

До установки смысл результата должен быть таким:

```text
Installed Apps: ['frappe']

Equipment   → absent
Customer    → absent
Rental      → absent
Rental Item → absent

Rental Operator → absent
Rental Manager  → absent
```

Завершите:

```python
exit()
```

Если CORE уже существует, Site не является чистой контрольной площадкой.

---

# 6. Проверить, что acceptance-site не использует developer mode

Выполните:

```bash
bench --site rental-acceptance.localhost show-config | grep developer_mode || true
```

При исправленном S00 ожидается отсутствие включённого `developer_mode`.

Если вывод показывает `1`/`true`, не продолжайте установку, пока не выясните источник.

Частая причина — старый глобальный ключ в `common_site_config.json`. Исправление приведено в разделе 3.

Не включайте developer mode на acceptance-site «чтобы точно заработало».

Это уничтожит смысл проверки.

---

# 7. Установить `rental_training`

Теперь выполняем единственное действие, которое должно принести продуктовую модель на Site:

```bash
bench --site rental-acceptance.localhost install-app rental_training
```

Проверьте:

```bash
bench --site rental-acceptance.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

## Что Frappe делает сам

В актуальном Frappe v16 `install_app()` штатно:

```text
добавляет Module Def из module list App
→ синхронизирует Standard metadata App
→ регистрирует App на Site
→ синхронизирует jobs
→ синхронизирует fixtures, если App их использует
→ синхронизирует exported customizations
```

Для CORE нам важны прежде всего:

```text
modules.txt
→ Module Def

DocType JSON
→ DocType/schema/default permissions
→ role names внутри permissions[]
→ missing Role создаются make_module_and_roles()

Python source
→ Controller behavior
```

В Frappe v16.33.0 `install_app()` выполняет `sync_for()` до `sync_fixtures()`. При sync Standard DocType `make_module_and_roles()` собирает роли из permission rows, создаёт отсутствующие `Role` и задаёт им `desk_access = 1`.

Поэтому отдельный `fixtures/role.json` для `Rental Operator` и `Rental Manager` текущему CORE не нужен.

Никаких ручных действий между этими пунктами быть не должно.

---

# 8. Проверить delivery manifest сразу после install-app

Откройте console:

```bash
bench --site rental-acceptance.localhost console
```

## 8.1. Module

```python
frappe.db.exists("Module Def", "Rental Training")
```

Ожидается truthy result.

## 8.2. Standard DocTypes

```python
core_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]

frappe.get_all(
    "DocType",
    filters={"name": ["in", core_doctypes]},
    fields=["name", "module", "custom", "istable"],
    order_by="name asc",
)
```

Должно быть четыре DocTypes.

Смысл:

```text
Equipment   → Rental Training / Standard / normal
Customer    → Rental Training / Standard / normal
Rental      → Rental Training / Standard / normal
Rental Item → Rental Training / Standard / Child
```

## 8.3. Role из Standard DocPerm

```python
for role in ["Rental Operator", "Rental Manager"]:
    print(role, frappe.db.exists("Role", role))
```

Обе Role должны существовать **до того, как мы создадим хоть одного User**.

Они должны появиться как следствие синхронизации Standard DocTypes, в `permissions[]` которых находятся эти role names.

Если приходится открывать `Role` и создавать их вручную, S09 провален.

## 8.4. Default permissions

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

Контракт:

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

## 8.5. Нет скрытых Site-customizations

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

В development Bench `migrate` проверяет доступность необходимых сервисов, включая Redis cache.

Если `bench start` уже работает в отдельном терминале — ничего делать не нужно.

Если не работает, откройте второй терминал и запустите:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Оставьте этот терминал открытым до конца S09.

Это не часть `rental_training` и не скрытая зависимость App:

```text
Bench services
→ инфраструктура dev-окружения

App metadata/Controller
→ продуктовый source
```

Не путайте ошибку вида «Redis service недоступен» с ошибкой архитектуры clean install.

---

# 10. Выполнить migrate как отдельную проверку update-path

`install-app` уже синхронизировал обязательное состояние при первичной установке.

Поэтому следующая команда не нужна как «магический второй install».

Мы запускаем её сознательно, чтобы доказать ещё один контракт:

> Текущее committed состояние App можно безопасно провести через обычный update/migrate path без ручного восстановления модели.

Выполните:

```bash
bench --site rental-acceptance.localhost migrate
```

Ожидается успешное завершение без:

```text
ручного ALTER TABLE
ручного UPDATE
создания Role через Desk
создания Custom Field
правки DocType на acceptance-site
```

После migrate снова проверьте Apps:

```bash
bench --site rental-acceptance.localhost list-apps -f text
```

Должны остаться:

```text
frappe
rental_training
```

---

# 11. Включить только test-настройку и запустить весь suite

На acceptance-site не нужен developer mode.

Для штатного test runner нужна только test-настройка конкретного Site:

```bash
bench --site rental-acceptance.localhost set-config allow_tests 1 --parse
```

Проверьте:

```bash
bench --site rental-acceptance.localhost show-config | grep allow_tests
```

Теперь запустите весь App:

```bash
bench --site rental-acceptance.localhost run-tests --app rental_training
```

Suite должен быть зелёным **на Site, где CORE до установки вообще не существовал**.

Этим одной командой повторно доказываются:

```text
V01 date range
V02 duplicate Equipment
V03 Active overlap
V03 touching boundary
V03 non-overlap
Planned overlap
self-save Active
Operator permissions
Manager permissions
```

Если тесты проходят только на `rental.localhost`, но падают здесь — clean-install contract не выполнен.

---

# 12. Проверить, что tests не изменили source App

```bash
git -C apps/rental_training status --short
```

Ожидается пустой вывод.

Tests могут создавать временные database records в своём test lifecycle, но не должны переписывать committed модель продукта.

---

# 13. Открыть Desk нового Site

`bench start` уже должен работать после раздела 9.

Откройте:

```text
http://rental-acceptance.localhost:8000/app
```

Войдите как:

```text
Administrator
```

с паролем, заданным при создании `rental-acceptance.localhost`.

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
install-app уже привёз metadata
↓
Desk уже умеет Form/List
```

Если для появления полей требуется открыть DocType и нажать Save, S09 провален.

---

# 15. Создать двух Site-local Users

Role уже должны быть на Site после синхронизации Standard DocPerm.

Теперь создаются **только участники этого Site**.

Используйте тот же штатный путь User, что в S05D.

## Operator

```text
Email              : operator.acceptance@example.test
First Name         : Acceptance Operator
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
Email              : manager.acceptance@example.test
First Name         : Acceptance Manager
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

После создания Users проверьте source App:

```bash
git -C apps/rental_training status --short
```

Он должен оставаться clean.

---

# 16. Пройти основной сценарий под Rental Manager

Выйдите из Administrator и войдите как:

```text
manager.acceptance@example.test
```

## 16.1. Создать Equipment №1

```text
Equipment Name : Acceptance Bosch Drill
Equipment Type : Tool
Serial Number  : ACC-TOOL-01
```

Сохраните и запомните сгенерированный `name`.

Не предполагаем заранее, что это обязательно `EQ-00001`: numbering state является состоянием Site.

## 16.2. Создать Equipment №2

```text
Equipment Name : Acceptance Canon Camera
Equipment Type : Camera
Serial Number  : ACC-CAM-01
```

Сохраните.

## 16.3. Создать Customer

```text
Customer Name : Acceptance Customer
Phone         : +31 6 10000901
Email         : acceptance.customer@example.test
```

Сохраните.

## 16.4. Создать первый Active Rental

```text
Customer   : Acceptance Customer
Start Date : 2026-10-10
End Date   : 2026-10-12
Status     : Active
Equipment:
- Acceptance Bosch Drill
- Acceptance Canon Camera
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

Это полноценный вертикальный сценарий на новом Site.

---

# 17. Проверить naming и Link presentation

Откройте сохранённый Rental.

Убедитесь:

1. Customer показывается человекочитаемым title;
2. Equipment показываются человекочитаемыми title;
3. у Customer/Equipment/Rental существуют стабильные системные `name` по заданным naming expressions;
4. UI не хранит копию названия вместо Link.

Не требуйте совпадения конкретных номеров с dev-site.

Правильная гарантия:

```text
strategy воспроизводится
runtime counter локален Site
```

---

# 18. Проверить Operator на реальном Desk

Выйдите и войдите как:

```text
operator.acceptance@example.test
```

## Equipment

Operator должен иметь возможность читать существующие Equipment.

Создавать новый Equipment он не должен.

В Desk это может проявиться как отсутствие `Add/New` либо отказ операции — точная UI-подача вторична.

Серверная гарантия уже повторно проверена S07 suite на этом же acceptance-site.

## Customer

Создайте:

```text
Customer Name : Operator Acceptance Customer
Phone         : +31 6 10000902
Email         : operator.customer@example.test
```

Ожидание: сохраняется.

## Rental

Создайте непересекающийся Rental:

```text
Customer   : Operator Acceptance Customer
Start Date : 2026-10-13
End Date   : 2026-10-14
Status     : Active
Equipment:
- Acceptance Bosch Drill
```

Ожидание: сохраняется, потому что предыдущий Active Rental закончился 12 октября.

Измените:

```text
End Date : 2026-10-15
```

и сохраните.

Ожидание: Write разрешён.

Удалять Rental Operator не должен.

Если Delete action не показывается — это нормальный UI-эффект permission model. Серверный запрет уже проверяется automated test.

---

# 19. Проверить V03 через обычный пользовательский сценарий

Оставаясь под Operator, создайте ещё один Rental:

```text
Customer   : Operator Acceptance Customer
Start Date : 2026-10-11
End Date   : 2026-10-13
Status     : Active
Equipment:
- Acceptance Canon Camera
```

`Acceptance Canon Camera` уже находится в Active Rental Manager за период:

```text
2026-10-10 → 2026-10-12
```

Периоды пересекаются.

Ожидается отказ сохранения с бизнес-ошибкой V03.

Это важно по двум причинам:

```text
правило приехало из rental.py
+
правило работает через обычный Desk Document path
```

Мы не создавали для acceptance-site:

```text
Client Script
Server Script
Workflow
ручной SQL trigger
локальный validator
```

---

# 20. Где проверяются V01 и V02 на финальном Site

Не нужно снова вручную мучить каждое поле только ради количества действий.

На **этом же `rental-acceptance.localhost`** уже выполнился:

```bash
bench --site rental-acceptance.localhost run-tests --app rental_training
```

Он проверил:

```text
V01 invalid date → rejected
V02 duplicate Equipment → rejected
V03 overlap → rejected
```

Ручная проверка V03 в Desk нужна здесь как вертикальное пользовательское доказательство.

Автоматические tests остаются главным повторяемым контрактом всех трёх правил.

---

# 21. Проверить финальное Site-owned состояние

После пользовательского сценария откройте console:

```bash
bench --site rental-acceptance.localhost console
```

Проверьте:

```python
print("Apps", frappe.get_installed_apps())
print("Equipment", frappe.db.count("Equipment"))
print("Customer", frappe.db.count("Customer"))
print("Rental", frappe.db.count("Rental"))

for user in [
    "operator.acceptance@example.test",
    "manager.acceptance@example.test",
]:
    print(user, frappe.db.exists("User", user))
```

Точные counts после test runner не являются архитектурным контрактом.

Здесь важно другое:

```text
business records и Users появились уже ПОСЛЕ установки
→ они принадлежат этому Site
```

Завершите:

```python
exit()
```

---

# 22. Финально проверить source App

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

printf '\n=== ACCEPTANCE APPS ===\n'
bench --site rental-acceptance.localhost list-apps -f text

printf '\n=== ACCEPTANCE CONFIG ===\n'
bench --site rental-acceptance.localhost show-config | \
  grep -E 'developer_mode|allow_tests' || true
```

Ожидаемый смысл:

```text
App commit → тот же committed source, с которого начинали S09
Git        → clean
Apps       → frappe + rental_training
developer_mode → не включён
allow_tests     → 1/true
```

Создание Users, Equipment, Customer и Rental не должно менять repository App.

---

# 23. Финальная автоматическая проверка ещё раз

После ручного пользовательского сценария снова выполните:

```bash
bench --site rental-acceptance.localhost run-tests --app rental_training
```

Suite должен остаться зелёным.

Это ловит ещё один класс ошибки:

```text
tests проходят только на пустой БД
```

Наши тесты должны изолировать собственные данные и не зависеть от того, что пользователь уже создал обычные business Documents.

---

# 24. Контрольная матрица S09

| Проверка | Ожидание |
|---|---|
| Site до install | только `frappe` |
| CORE DocTypes до install | отсутствуют |
| CORE Role до install | отсутствуют |
| developer mode | не нужен acceptance-site |
| `install-app rental_training` | success |
| Module | появился из App |
| 4 Standard DocTypes | появились из JSON |
| Role Operator/Manager | появились из Standard DocPerm при sync |
| default permissions | соответствуют JSON |
| hidden Custom Field/Property Setter/Custom DocPerm | отсутствуют |
| Bench services перед migrate | доступны |
| `migrate` | success без ручного SQL |
| tests | green |
| Manager vertical scenario | проходит |
| Operator read/create/write limits | соответствуют модели |
| V03 в Desk | конфликт блокируется |
| runtime Users/business data | остаются Site-owned |
| App Git после всего | clean |

---

# 25. S09 — ГОТОВО

CORE считается завершённым, если одновременно верно:

```text
[ ] создан новый rental-acceptance.localhost
[ ] до install-app на нём был только frappe
[ ] до install-app CORE DocTypes и Role отсутствовали
[ ] acceptance-site не требует developer_mode
[ ] App repository был clean и его commit SHA зафиксирован
[ ] rental_training установился штатной командой install-app
[ ] Module Rental Training появился без ручного создания
[ ] Equipment появился из App
[ ] Customer появился из App
[ ] Rental Item появился из App
[ ] Rental появился из App
[ ] naming/fields/default permissions соответствуют source metadata
[ ] Rental Operator появился из Standard DocPerm sync
[ ] Rental Manager появился из Standard DocPerm sync
[ ] отдельный Role fixture для этих имён не требуется
[ ] скрытых обязательных Custom Field/Property Setter/Custom DocPerm нет
[ ] Bench services доступны перед migrate
[ ] bench migrate проходит
[ ] tests проходят на acceptance-site
[ ] Site-local Users создаются после установки и не входят в App
[ ] Manager проходит Equipment → Customer → Rental
[ ] Operator видит Equipment, но не может создавать его
[ ] Operator может создавать/изменять Customer и Rental
[ ] Operator не может удалять Rental
[ ] overlapping Active Rental блокируется через Desk
[ ] tests остаются зелёными после обычных business records
[ ] App Git остаётся clean после всех runtime-действий
```

---

# 26. S09 — НЕ ГОТОВО

CORE не принимается, если хотя бы одно обязательное действие звучит так:

```text
«после install откройте DocType и ещё раз Save»
«создайте обязательные Role вручную»
«добавьте missing field через Customize Form»
«поправьте permissions через Role Permission Manager»
«включите developer mode, иначе установленное App не работает»
«выполните этот ALTER TABLE вручную»
«скопируйте Users с dev-site»
«скопируйте старые EQ/CUST/RENT записи как fixtures»
```

Также этап не принят, если:

- tests проходят только на старом `rental.localhost`;
- новый Site требует локальный Server Script для V01/V02/V03;
- роли не восстанавливаются из Standard DocPerm sync;
- добавлен Role fixture только для имён, уже находящихся в Standard DocPerm;
- default permissions зависят от Site override;
- App source меняется от обычной работы пользователей;
- clean install работает только при незакоммиченных файлах разработчика.

---

# 27. Что доказал весь CORE

После S09 у ученика есть не просто маленькая система проката.

Он руками прошёл причинно-следственную цепочку Frappe:

```text
реальное требование
        ↓
ответственность
        ↓
нативный механизм Frappe
        ↓
Standard metadata / Document / permission / Controller
        ↓
Desk scenario
        ↓
server-side contracts
        ↓
automated tests
        ↓
App-owned delivery manifest
        ↓
clean Site install
```

Итоговая модель остаётся маленькой:

```text
Equipment
Customer
Rental
└── Rental Item
```

Но вокруг неё уже доказаны важные свойства настоящего Frappe App:

```text
стабильная identity
живые Link
composition через Child DocType
Table MultiSelect
предметный status
server validation
cross-document invariant
Role + DocType Permissions
migrate
Frappe-aware tests
clean install
```

При этом CORE сознательно не потребовал:

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
custom frontend
```

Потому что ни один из этих механизмов пока не нужен для доказанного требования.

Это и есть финальный архитектурный результат практикума:

> Не перечислить возможности Frappe, а научиться выбирать штатный механизм по ответственности и уметь доказать, что решение воспроизводимо.
