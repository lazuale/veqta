# S05D. Настроить базовые роли и доказать права серверными операциями

К S05D приложение уже умеет:

```text
Equipment
Customer
Rental
└── Rental Item

Rental.validate()
├── end_date >= start_date
└── Equipment не повторяется внутри одного Rental
```

Но до сих пор почти все проверки выполнялись под `Administrator`.

Это означает, что мы ещё **не доказали безопасность приложения**.

Новое требование:

> Оператор проката должен работать с клиентами и прокатами, но не должен управлять справочником Equipment и не должен удалять бизнес-записи. Менеджер должен иметь полный CRUD-доступ к CORE-модели.

Для этого CORE использует только штатную базовую модель Frappe:

```text
User
Role
DocType Permissions
```

На этом этапе намеренно **не используются**:

```text
Permission Level
Permission Type
If Owner
User Permission
Share
permission_query_conditions
has_permission hook
собственная ACL-таблица
скрытие кнопок через JavaScript как защита
ignore_permissions=True
```

Причина простая: текущее требование полностью выражается обычными ролями и правами на DocType.

Связанные документы:

- [`S05C_RENTAL_LOCAL_INVARIANTS.md`](S05C_RENTAL_LOCAL_INVARIANTS.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md);
- [`../REQUIREMENTS_MATRIX.md`](../REQUIREMENTS_MATRIX.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/04_SECURITY.md`](../../frappe-architecture-standard/04_SECURITY.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/installer.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/permissions.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/delete_doc.py

---

# 1. Сначала сформулировать permission matrix

До кликов нужно знать, что именно разрешено.

## Rental Operator

| DocType | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Equipment | yes | no | no | no |
| Customer | yes | yes | yes | no |
| Rental | yes | yes | yes | no |

Смысл роли:

```text
Equipment
→ оператор выбирает существующее оборудование
→ но не управляет самим справочником

Customer
→ оператор ведёт клиентов
→ но не удаляет их

Rental
→ оператор создаёт и редактирует прокаты
→ но не удаляет их
```

## Rental Manager

| DocType | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Equipment | yes | yes | yes | yes |
| Customer | yes | yes | yes | yes |
| Rental | yes | yes | yes | yes |

Менеджер имеет полный CRUD-доступ к текущему CORE.

## Чего в матрице нет

```text
Submit
Cancel
Amend
```

потому что `Rental` не является `Is Submittable`.

Также пока не нужны:

```text
Report
Export
Import
Share
Print
Email
```

Они не включаются просто потому, что такие колонки существуют в Frappe.

---

# 2. Почему не делать собственную ACL

Требование сейчас выглядит так:

```text
роль
→ набор CRUD-действий
→ конкретный DocType
```

Это буквально ответственность `Role + DocType Permissions` Frappe.

Собственная таблица вида:

```text
Rental ACL
├── user
├── doctype
├── can_read
├── can_write
└── ...
```

создала бы второй движок прав рядом со штатным.

Тогда пришлось бы отдельно согласовывать:

```text
Desk
REST API
Document.save()
List
Reports
custom endpoints
```

с нашей самодельной системой.

На S05D для этого нет никакого основания.

---

# 3. Понять, что принадлежит App, а что Site

Это центральная архитектурная часть этапа.

## App-owned

Приложение **требует**, чтобы после чистой установки существовали роли:

```text
Rental Operator
Rental Manager
```

и чтобы Standard DocTypes имели определённые default permissions.

Для текущего CORE источник этой модели один:

```text
DocType Permissions
→ часть metadata Standard DocType
→ equipment.json / customer.json / rental.json

role name внутри DocPerm
→ часть той же metadata
→ при sync Frappe создаёт отсутствующий Role
```

В Frappe v16.33.0 `make_module_and_roles()` собирает имена ролей из permission rows Standard DocType и создаёт отсутствующие `Role`. Для созданной роли Framework устанавливает `desk_access = 1`.

При установке App `install_app()` выполняет `sync_for()` до `sync_fixtures()`. Поэтому отдельный `Role` fixture только ради двух имён, уже присутствующих в Standard DocPerm собственного App, дублировал бы штатный механизм Frappe.

## Site-owned

Конкретные пользователи:

```text
operator@example.test
manager@example.test
```

нужны только для учебной проверки на этом Site.

Это не часть продукта.

Следовательно:

```text
User accounts
→ runtime/config data конкретного Site
→ не fixtures практикума
→ пароли не Git
```

Главная формула:

```text
роль нужна приложению
≠
конкретный человек нужен приложению
```

---

# 4. Входная проверка

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Apps:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте Git App:

```bash
git -C apps/rental_training status --short
```

После принятого S05C рабочее дерево должно быть чистым.

Проверьте, что Controller S05C уже находится в Git:

```bash
git -C apps/rental_training log -1 --oneline -- \
  rental_training/rental_training/doctype/rental/rental.py
```

---

# 5. Создать две Role через Desk

Если dev server не работает:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте:

```text
http://rental.localhost:8000/app
```

Войдите как `Administrator`.

Через Awesomebar откройте:

```text
Role
```

Создайте первую роль:

```text
Role Name   : Rental Operator
Desk Access : yes
Disabled    : no
```

Сохраните.

Создайте вторую:

```text
Role Name   : Rental Manager
Desk Access : yes
Disabled    : no
```

Сохраните.

### Почему Desk Access = yes

Обе роли предназначены для внутренних System Users, работающих в Desk.

В актуальном `Role` DocType Frappe поле `desk_access` является штатной частью роли и по умолчанию включено.

---

# 6. Пока изменения существуют только на Site

После создания двух Role проверьте Git:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Сам факт создания Role в БД Site не обязан автоматически создать source-файл в нашем App.

Это полезное наблюдение:

```text
Role создана на Site
≠
роль уже описана обязательной metadata нашего App
```

Дальше мы добавим эти имена в default permissions Standard DocTypes. Именно эти permission rows станут воспроизводимым source: при синхронизации Frappe создаст отсутствующие Role на другом Site.

---

# 7. Настроить Equipment permissions в самом Standard DocType

Через Awesomebar откройте:

```text
DocType
```

Найдите:

```text
Equipment
```

Откройте таблицу `Permissions`.

Добавьте/настройте строки уровня `0`.

## Rental Operator

```text
Role   : Rental Operator
Level  : 0
Read   : yes
Create : no
Write  : no
Delete : no
```

Не включайте `If Owner`.

Остальные дополнительные permission-флаги оставьте выключенными, если они не требуются этапом.

## Rental Manager

```text
Role   : Rental Manager
Level  : 0
Read   : yes
Create : yes
Write  : yes
Delete : yes
```

Сохраните `Equipment`.

### Что произошло

Мы изменили **default permissions Standard DocType собственного App**.

Поэтому developer mode должен записать изменение в:

```text
apps/rental_training/
└── rental_training/
    └── rental_training/
        └── doctype/
            └── equipment/
                └── equipment.json
```

---

# 8. Настроить Customer permissions

Откройте Standard DocType:

```text
Customer
```

## Rental Operator

```text
Role   : Rental Operator
Level  : 0
Read   : yes
Create : yes
Write  : yes
Delete : no
```

## Rental Manager

```text
Role   : Rental Manager
Level  : 0
Read   : yes
Create : yes
Write  : yes
Delete : yes
```

`If Owner` не включать.

Сохраните.

Ожидаемое source-изменение:

```text
customer/customer.json
```

---

# 9. Настроить Rental permissions

Откройте Standard DocType:

```text
Rental
```

## Rental Operator

```text
Role   : Rental Operator
Level  : 0
Read   : yes
Create : yes
Write  : yes
Delete : no
```

## Rental Manager

```text
Role   : Rental Manager
Level  : 0
Read   : yes
Create : yes
Write  : yes
Delete : yes
```

Не включайте:

```text
Submit
Cancel
Amend
If Owner
```

Сохраните.

---

# 10. Почему Rental Item не получает самостоятельную CRUD-матрицу

`Rental Item` — Child DocType.

Пользователь не должен работать с ним как с независимым реестром.

Его строки принадлежат `Rental`:

```text
Rental
└── items
    └── Rental Item
```

В текущем исходнике Frappe permission handling для child document учитывает `parenttype` при проверке прав.

Поэтому S05D не придумывает отдельную роль:

```text
Rental Item Operator
```

и не строит самостоятельный CRUD-процесс для строк.

Право пользователя редактировать набор Equipment проверяется в контексте возможности изменять родительский `Rental`.

---

# 11. Проверить изменения metadata через Git

Вернитесь в терминал:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
```

Проверьте:

```bash
git status --short
```

На этом месте должны быть изменены как минимум JSON трёх Standard DocTypes:

```text
rental_training/rental_training/doctype/equipment/equipment.json
rental_training/rental_training/doctype/customer/customer.json
rental_training/rental_training/doctype/rental/rental.json
```

Посмотрите diff:

```bash
git diff -- \
  rental_training/rental_training/doctype/equipment/equipment.json \
  rental_training/rental_training/doctype/customer/customer.json \
  rental_training/rental_training/doctype/rental/rental.json
```

Ищите `permissions` с ролями:

```text
Rental Operator
Rental Manager
```

и соответствующими CRUD-флагами.

Точный порядок JSON-ключей не является контрактом.

Контракт:

```text
обязательные default permissions
→ находятся в metadata Standard DocType
→ видны Git
```

---

# 12. Не использовать Role Permission Manager как источник обязательных defaults

Frappe предоставляет `Role Permission Manager` — это нормальный штатный административный инструмент.

Но он способен создавать **Site-level overrides** относительно default permissions DocType.

Для S05D нам нужна другая гарантия:

> После установки App на чистый Site базовая permission model уже существует без ручной донастройки.

Поэтому обязательные defaults мы редактировали в `Permissions` самих Standard DocTypes своего App.

Правило этапа:

```text
default permission model продукта
→ Standard DocType metadata

локальное изменение конкретного Site
→ Role Permission Manager может быть уместен
```

Мы не запрещаем Role Permission Manager. Мы просто не делаем локальный override скрытым обязательным шагом установки продукта.

---

# 13. Почему отдельный Role fixture здесь не нужен

После разделов 7–9 оба имени роли уже находятся в `permissions[]` Standard DocTypes нашего App.

В Frappe v16.33.0 штатный sync Standard DocType вызывает `make_module_and_roles()`:

```text
permissions[]
→ собрать role names
→ проверить наличие Role
→ создать отсутствующую Role
→ desk_access = 1
```

При `install-app` этот sync происходит до `sync_fixtures()`.

Следовательно, схема:

```text
Standard DocPerm
+
Role fixture с тем же role_name
```

создала бы два механизма поставки одной ответственности.

Для CORE используем более простой путь:

```text
Standard DocPerm
→ source of truth role name
→ штатный sync Frappe создаёт missing Role
```

Отдельный Role fixture был бы оправдан только при дополнительном App-owned состоянии самой Role, которое не выражается Standard DocPerm. В текущем требовании такого состояния нет.

---

# 14. Проверить, что лишний fixture не появился

Проверьте `hooks.py`:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

grep -n -A20 -B5 'fixtures' rental_training/hooks.py || true
```

Если `fixtures` уже используются для другой самостоятельной конфигурации App, не удаляйте их.

Но текущие две роли не должны добавляться отдельной записью вида:

```python
{
    "dt": "Role",
    "filters": [["role_name", "in", ["Rental Operator", "Rental Manager"]]],
}
```

и для них не требуется:

```text
rental_training/fixtures/role.json
```

Также не запускайте `export-fixtures` только ради этих двух Role: их воспроизводимость будет проверена на чистом Site в S09.

---

# 15. Проверить Git ownership permission model

Теперь:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Ожидаемый класс изменений:

```text
equipment.json
customer.json
rental.json
```

Архитектурная картина:

```text
Role names
+
Role → CRUD on DocType
→ Standard DocType JSON permissions[]

missing Role на новом Site
→ создаёт Frappe при sync Standard metadata

конкретные User accounts
→ только Site
```

---

# 16. Создать двух учебных Users только на Site

Вернитесь в Desk под Administrator.

Через Awesomebar откройте:

```text
User
```

Создайте первого пользователя.

## Operator User

```text
Email              : operator@example.test
First Name         : Rental Operator User
User Type          : System User
Send Welcome Email : off
```

В Roles назначьте:

```text
Rental Operator
```

Не назначайте:

```text
Rental Manager
System Manager
```

Установите локальный учебный пароль через штатный механизм User.

Пароль:

- не записывается в этот документ;
- не добавляется в Git;
- используется только на локальном учебном Site.

Создайте второго пользователя.

## Manager User

```text
Email              : manager@example.test
First Name         : Rental Manager User
User Type          : System User
Send Welcome Email : off
```

В Roles назначьте:

```text
Rental Manager
```

Не назначайте `System Manager`.

### Почему System User

Оба пользователя должны работать в Desk.

Frappe автоматически предоставляет System Users роль `Desk User`; это инфраструктурная роль Framework, а не замена нашим предметным ролям.

---

# 17. Проверить, что Users не попали в Git

После создания Users:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Создание:

```text
operator@example.test
manager@example.test
```

не должно создавать новые source-файлы пользователей.

Это правильно: `User` остаётся состоянием конкретного Site и не входит в обязательную metadata CORE.

---

# 18. Проверить реальные роли пользователей

Откройте Bench console:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Выполните:

```python
operator = "operator@example.test"
manager = "manager@example.test"

print(frappe.get_roles(operator))
print(frappe.get_roles(manager))
```

У Operator должна присутствовать:

```text
Rental Operator
```

и не должны присутствовать:

```text
Rental Manager
System Manager
```

У Manager должна присутствовать:

```text
Rental Manager
```

и не должен присутствовать `System Manager`.

Автоматические роли вроде `All` и `Desk User` являются нормальными.

---

# 19. Посмотреть effective CRUD-права программно

В том же console используйте функцию:

```python
def show_crud(user, doctype):
    frappe.set_user(user)
    result = {
        ptype: frappe.has_permission(doctype, ptype)
        for ptype in ("read", "create", "write", "delete")
    }
    print(user, doctype, result)
```

## Operator

```python
for dt in ("Equipment", "Customer", "Rental"):
    show_crud(operator, dt)
```

Ожидаемый смысл:

```text
Equipment
read=True
create=False
write=False
delete=False

Customer
read=True
create=True
write=True
delete=False

Rental
read=True
create=True
write=True
delete=False
```

## Manager

```python
for dt in ("Equipment", "Customer", "Rental"):
    show_crud(manager, dt)
```

Ожидается:

```text
read=True
create=True
write=True
delete=True
```

для всех трёх DocTypes.

Верните контекст:

```python
frappe.set_user("Administrator")
```

### Почему одной таблицы `has_permission()` недостаточно

Она хорошо показывает effective permission model, но S05D должен доказать, что реальные Document operations действительно блокируются/разрешаются.

Поэтому дальше выполняются несколько настоящих CRUD-проверок.

---

# 20. Доказать: Operator не может создать Equipment

В console:

```python
frappe.set_user(operator)

try:
    frappe.get_doc(
        {
            "doctype": "Equipment",
            "equipment_name": "Forbidden Operator Equipment",
            "equipment_type": "Tool",
            "serial_number": "S05D-DENIED-001",
        }
    ).insert()
except frappe.PermissionError as exc:
    print("BLOCKED operator create Equipment:", exc)
    frappe.db.rollback()
```

Ожидается:

```text
BLOCKED operator create Equipment
```

Это серверная проверка.

Мы не проверяем только отсутствие кнопки `New`.

В актуальном `Document.insert()` Frappe выполняет permission check `create` до вставки Document.

---

# 21. Доказать: Operator может читать Equipment

Оставаясь Operator:

```python
rows = frappe.get_list(
    "Equipment",
    fields=["name", "equipment_name"],
    limit_page_length=5,
)

print(rows)
```

Запрос должен выполняться без `PermissionError` и возвращать доступные Equipment.

Здесь намеренно используется:

```text
get_list
```

а не `get_all`, потому что мы проверяем путь с учётом пользовательских permissions.

---

# 22. Доказать: Operator может создать Customer

```python
frappe.set_user(operator)

operator_customer = frappe.get_doc(
    {
        "doctype": "Customer",
        "customer_name": "S05D Operator Customer",
        "email": "s05d-operator-customer@example.test",
    }
)

operator_customer.insert()
print("ALLOWED operator create Customer:", operator_customer.name)
```

Ожидается успешная вставка.

Для чистоты учебного Site откатите эту **console-транзакцию**:

```python
frappe.db.rollback()
```

### Почему rollback здесь допустим

Это интерактивная диагностическая console-сессия, а не код Controller приложения.

Мы сознательно создаём временный Document для проверки и возвращаем БД к исходному состоянию.

В обычном web request ручное управление транзакцией не добавляется «на всякий случай».

---

# 23. Доказать: Operator может создать Rental

Найдите существующие Customer и Equipment, которые доступны Operator:

```python
frappe.set_user(operator)

customer = frappe.get_list(
    "Customer",
    fields=["name"],
    limit_page_length=1,
)[0].name

equipment = frappe.get_list(
    "Equipment",
    fields=["name"],
    limit_page_length=1,
)[0].name
```

Создайте Planned Rental с корректными локальными инвариантами:

```python
operator_rental = frappe.get_doc(
    {
        "doctype": "Rental",
        "customer": customer,
        "start_date": "2026-11-10",
        "end_date": "2026-11-11",
        "status": "Planned",
        "items": [{"equipment": equipment}],
    }
)

operator_rental.insert()
print("ALLOWED operator create Rental:", operator_rental.name)
```

Ожидается успешная вставка.

После проверки:

```python
frappe.db.rollback()
```

Это одновременно подтверждает, что permission model и Controller S05C работают в одном обычном Document path.

---

# 24. Доказать: Operator может Write, но не Delete Rental

Найдите существующий Rental, например контрольный S05B:

```python
frappe.set_user(operator)

rental_name = frappe.get_list(
    "Rental",
    fields=["name"],
    limit_page_length=1,
)[0].name

rental = frappe.get_doc("Rental", rental_name)
```

## Write разрешён

Сохраним допустимое изменение, которое не ломает S05C-инварианты.

Например временно сменим status:

```python
old_status = rental.status
rental.status = "Planned"
rental.save()
print("ALLOWED operator write Rental:", rental.name)
frappe.db.rollback()
```

После rollback runtime-запись вернётся к исходному состоянию.

## Delete запрещён

Снова установите пользователя:

```python
frappe.set_user(operator)
```

Попробуйте:

```python
try:
    frappe.delete_doc("Rental", rental_name)
except frappe.PermissionError as exc:
    print("BLOCKED operator delete Rental:", exc)
    frappe.db.rollback()
```

Ожидается permission error.

В актуальном Frappe `delete_doc()` документирует и выполняет delete-permission check, если `ignore_permissions=False`.

---

# 25. Доказать полный CRUD Manager на временном Equipment

Теперь:

```python
frappe.set_user(manager)
```

Создайте временную запись:

```python
manager_equipment = frappe.get_doc(
    {
        "doctype": "Equipment",
        "equipment_name": "S05D Manager Equipment",
        "equipment_type": "Tool",
        "serial_number": "S05D-MANAGER-001",
    }
)

manager_equipment.insert()
print("CREATE OK:", manager_equipment.name)
```

Прочитайте:

```python
loaded = frappe.get_doc("Equipment", manager_equipment.name)
loaded.check_permission("read")
print("READ OK:", loaded.name)
```

Измените:

```python
loaded.equipment_name = "S05D Manager Equipment Updated"
loaded.save()
print("WRITE OK:", loaded.name)
```

Удалите:

```python
frappe.delete_doc("Equipment", loaded.name)
print("DELETE OK:", loaded.name)
```

Теперь откатите всю временную console-транзакцию:

```python
frappe.db.rollback()
```

Верните Administrator:

```python
frappe.set_user("Administrator")
```

Выйдите:

```python
exit()
```

---

# 26. Проверить то же поведение через Desk

Теперь выполните короткую UI-проверку.

## Под Operator

Выйдите из Administrator и войдите как:

```text
operator@example.test
```

Проверьте:

```text
Equipment
✓ открыть List
✓ открыть существующее Equipment
✗ создать новое
✗ редактировать существующее
✗ удалить

Customer
✓ открыть
✓ создать
✓ изменить
✗ удалить

Rental
✓ открыть
✓ создать
✓ изменить
✗ удалить
```

Не оценивайте безопасность только по наличию/отсутствию кнопок. Серверные проверки уже выполнены предыдущими разделами.

## Под Manager

Войдите как:

```text
manager@example.test
```

Проверьте, что обычный CRUD всех трёх CORE DocTypes доступен.

---

# 27. Почему UI hiding не считается защитой

Допустим, кто-то сделал:

```javascript
frm.remove_custom_button("Delete")
```

или спрятал поле/кнопку CSS.

Это не меняет permission engine.

Пользователь может обращаться к данным другим путём:

```text
REST
Document API
другая форма
серверный метод
```

S05D принят только потому, что запрет находится в штатной серверной permission model.

Формула:

```text
кнопки отражают право

но

кнопки не создают право
```

---

# 28. Почему не `If Owner`

Требование S05D не говорит:

> Operator может изменять только Rental, которые создал сам.

Оно говорит:

> Operator может изменять Rental.

Поэтому `If Owner` был бы **новым бизнес-правилом**, которого у нас нет.

Кроме того, системный `owner` Frappe означает создателя Document и не обязан совпадать с бизнес-понятиями вроде:

```text
ответственный
менеджер клиента
исполнитель
```

---

# 29. Почему не User Permission

У нас нет требования:

```text
Operator A работает только с Customer X
Operator B видит только Equipment участка Y
```

Поэтому User Permission пока не нужен.

Если такое требование появится, это будет отдельная архитектурная ветка.

---

# 30. Почему не Permission Level

Все текущие поля Rental доступны тому, кто имеет read/write на Rental.

Нет чувствительного поля вида:

```text
internal_cost
manager_comment
salary
secret_rate
```

которое одна роль должна видеть, а другая — нет.

Поэтому `permlevel > 0` сейчас был бы механизмом без требования.

---

# 31. Почему не Permission Type

В S05D проверяются стандартные операции:

```text
read
create
write
delete
```

Нам пока не нужна отдельная предметная операция:

```text
approve
issue
force_return
```

которая требует собственного permission type.

Следовательно, стандартных типов прав достаточно.

---

# 32. Почему не permission hooks

Нет строковой политики вроде:

```text
пользователь видит только Rentals своего Department
```

или динамической логики:

```text
доступ зависит от договора + суммы + организации
```

Поэтому не нужны:

```text
permission_query_conditions
has_permission
```

Сначала используются декларативные `Role + DocPerm`.

---

# 33. Проверить, что в коде не появился обход прав

Из App repo:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
```

Поищите опасные обходы:

```bash
grep -RIn \
  -e 'ignore_permissions=True' \
  -e 'ignore_permissions = True' \
  rental_training || true
```

Для текущего CORE собственный код не должен содержать такой обход.

Также S05D не требует собственной проверки:

```python
if "Rental Manager" in frappe.get_roles():
    ...
```

для обычного CRUD.

CRUD уже принадлежит permission engine.

---

# 34. Зафиксировать permission model в Git

Проверьте итоговый diff:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short

git diff -- \
  rental_training/rental_training/doctype/equipment/equipment.json \
  rental_training/rental_training/doctype/customer/customer.json \
  rental_training/rental_training/doctype/rental/rental.json
```

Добавьте согласованный набор:

```bash
git add \
  rental_training/rental_training/doctype/equipment/equipment.json \
  rental_training/rental_training/doctype/customer/customer.json \
  rental_training/rental_training/doctype/rental/rental.json
```

Проверьте staged diff:

```bash
git diff --cached
```

Убедитесь, что в Git попали только default permissions Standard DocTypes и нет случайных Users, паролей или Role fixture.

Зафиксируйте:

```bash
git commit -m "feat: add rental permissions"
```

Проверьте:

```bash
git status --short
```

Ожидается:

```text
<пусто>
```

---

# 35. Нужно ли выполнять `bench migrate` на текущем Site

На текущем учебном Site:

- Role уже созданы в БД;
- permissions уже сохранены через DocType UI;
- Users уже существуют локально.

Поэтому S05D не требует выполнять `bench migrate` просто ради ритуала.

Но для **другого Site** смысл source-файлов другой:

```text
Standard DocType JSON
        ↓
install / migrate sync
        ↓
DocPerm синхронизируются
        ↓
missing Role создаются Frappe
```

Это будет доказано не предположением, а clean-install проверкой на S08/S09.

---

# 36. Что не является частью Git после S05D

В репозитории не должны появиться:

```text
operator@example.test User record
manager@example.test User record
их пароли
sessions
конкретные runtime Rentals
конкретные runtime Customers
конкретные runtime Equipment
```

В Git появляется обязательная permission model:

```text
Standard DocType JSON
└── permissions[]
    ├── Rental Operator
    └── Rental Manager
```

Отдельный Role fixture для этих двух имён текущему CORE не нужен.

---

# 37. Типовые неправильные решения

## Ошибка 1. Проверить всё под Administrator

```text
Administrator может создать Rental
→ значит permissions работают
```

Нет.

Administrator является специальным системным пользователем и не доказывает поведение предметных ролей.

## Ошибка 2. Спрятать кнопку вместо запрета

```text
Operator не должен удалять Rental
→ скрыли Delete в JS
```

Это UI, а не authorization.

Правильная ответственность:

```text
DocPerm.delete = 0
```

## Ошибка 3. Настроить всё только Role Permission Manager и забыть delivery

На dev-site всё выглядит правильно, но после clean install default permissions приходится восстанавливать вручную.

Это значит, что обязательное состояние продукта не принадлежит Standard metadata App.

## Ошибка 4. Добавить Role fixture для имени, которое уже находится в Standard DocPerm

Так App начинает поставлять одну и ту же ответственность двумя путями:

```text
Standard DocPerm sync
+
Role fixture sync
```

Для текущего CORE это лишнее дублирование.

## Ошибка 5. Экспортировать Users

Учебный аккаунт конкретного человека — не обязательная конфигурация продукта.

## Ошибка 6. Добавить `ignore_permissions=True`, чтобы тест прошёл

Это уничтожает сам смысл проверки authorization.

---

# 38. Три правильных решения

## Правильно 1. CRUD policy через DocPerm

Требование совпадает со стандартными permission types — значит используем их напрямую.

## Правильно 2. Default permissions в Standard DocType metadata

Они принадлежат нашему App и воспроизводятся вместе с моделью.

## Правильно 3. Role name поставляется тем же Standard DocPerm

Frappe создаёт отсутствующий `Role` при sync Standard DocType. Отдельный fixture появляется только при самостоятельном App-owned состоянии Role, которого текущий CORE не требует.

---

# 39. Контрольная карта S05D

```text
[ ] создана Role Rental Operator на dev-site
[ ] создана Role Rental Manager на dev-site
[ ] обе Role имеют Desk Access
[ ] Equipment DocPerm соответствует матрице
[ ] Customer DocPerm соответствует матрице
[ ] Rental DocPerm соответствует матрице
[ ] If Owner не включён без требования
[ ] Submit/Cancel/Amend не включены
[ ] Rental Item не превращён в самостоятельный CRUD
[ ] имена Rental Operator/Rental Manager находятся в Standard DocPerm
[ ] отдельный Role fixture для этих имён не добавлен
[ ] operator@example.test создан только на Site
[ ] manager@example.test создан только на Site
[ ] Operator не имеет System Manager/Rental Manager
[ ] Manager не имеет System Manager
[ ] Operator server-side не может create Equipment
[ ] Operator server-side может read Equipment
[ ] Operator server-side может create Customer
[ ] Operator server-side может create/write Rental
[ ] Operator server-side не может delete Rental
[ ] Manager server-side имеет полный CRUD
[ ] Desk отражает те же права
[ ] собственный код не использует ignore_permissions=True
[ ] обязательная permission model видна в Git
[ ] runtime Users не попали в Git
[ ] Git working tree после commit чистый
```

---

# 40. ГОТОВО

S05D принят, если одновременно выполнены четыре уровня проверки.

## 1. Модель

```text
Rental Operator
Rental Manager
```

существуют как предметные Role.

DocPerm трёх обычных CORE DocTypes соответствует утверждённой CRUD-матрице.

## 2. Server authorization

Реальными server-side операциями доказано:

```text
Operator
✓ read Equipment
✗ create Equipment
✓ create Customer
✓ create/write Rental
✗ delete Rental

Manager
✓ CRUD Equipment
✓ CRUD Customer
✓ CRUD Rental
```

## 3. Delivery

```text
Role names + DocPerm
→ Standard DocType JSON
→ sync Standard metadata
→ missing Role создаёт Frappe

Users
→ Site only
```

После clean install не должно требоваться вручную создавать две обязательные Role или заново настраивать default CRUD matrix.

## 4. Архитектурная граница

Не добавлены без требования:

```text
Permission Level
Permission Type
If Owner
User Permission
Share
permission hooks
custom ACL
JS-security
ignore_permissions=True
Role fixture, дублирующий Standard DocPerm
```

---

# 41. НЕ ГОТОВО

S05D не принят, если:

- права проверены только визуально;
- тесты выполнялись только под Administrator;
- Operator фактически может создать Equipment или удалить Rental;
- Manager не получает заявленный CRUD;
- `If Owner` включён без предметного требования;
- права существуют только как локальный override Site;
- обязательные Role не воспроизводятся из Standard metadata App;
- добавлен Role fixture только для имён, уже находящихся в Standard DocPerm;
- Users/пароли попали в Git;
- собственный код обходит permission engine через `ignore_permissions=True`;
- JavaScript используется как единственная защита.

---

# 42. Что должно остаться после S05D

Предметная модель данных не изменилась.

Появилась отдельная authorization model:

```text
User
  ↓ roles
Rental Operator / Rental Manager
  ↓ DocPerm
Equipment / Customer / Rental
```

И теперь мы умеем различать две независимые гарантии:

```text
S05C
какие данные допустимы
→ Controller.validate()

S05D
кто может выполнить операцию
→ Role + DocType Permissions
```

Следующий этап — S06.

На нём появится третий собственный бизнес-инвариант:

```text
одно Equipment
не может находиться
в двух пересекающихся Active Rentals
```

Это уже правило **между несколькими Documents**, поэтому впервые понадобится запрос к другим Rentals, а не только проверка текущего `self`.
