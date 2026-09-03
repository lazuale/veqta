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

> Оператор проката должен работать с клиентами и прокатами, но не должен управлять справочником Equipment и не должен удалять рабочие записи. Менеджер должен иметь полный CRUD-доступ к модели практикума.

Для этого используются только штатные механизмы Frappe:

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
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../REQUIREMENTS.md`](../REQUIREMENTS.md);
- [`../ROADMAP.md`](../ROADMAP.md);
- [`../../../frappe-architecture-standard/04_SECURITY.md`](../../../frappe-architecture-standard/04_SECURITY.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/installer.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/permissions.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/delete_doc.py

---

# 1. Сначала сформулировать матрицу прав

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

Менеджер имеет полный CRUD-доступ к текущей модели.

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

создала бы второй механизм прав рядом со штатным.

Тогда пришлось бы отдельно согласовывать с ним:

```text
Desk
REST API
Document.save()
List
Reports
собственные endpoints
```

На S05D для этого нет никакого основания.

---

# 3. Понять, что принадлежит App, а что Site

Это центральная архитектурная часть этапа.

## Состояние App

Приложение **требует**, чтобы после чистой установки существовали роли:

```text
Rental Operator
Rental Manager
```

и чтобы Standard DocTypes имели определённые permissions по умолчанию.

Для текущего приложения источник этой модели один:

```text
DocType Permissions
→ часть метаданных Standard DocType
→ equipment.json / customer.json / rental.json

имя Role внутри DocPerm
→ часть тех же метаданных
→ при sync Frappe создаёт отсутствующую Role
```

В Frappe v16.33.0 `make_module_and_roles()` собирает имена ролей из permission rows Standard DocType и создаёт отсутствующие `Role`. Для созданной роли Framework устанавливает `desk_access = 1`.

При установке App `install_app()` выполняет `sync_for()` до `sync_fixtures()`. Поэтому отдельный `Role` fixture только ради двух имён, уже присутствующих в Standard DocPerm собственного App, дублировал бы штатный механизм Frappe.

## Состояние Site

Конкретные пользователи:

```text
operator@example.test
manager@example.test
```

нужны только для учебной проверки на этом Site.

Они не являются обязательной частью App.

Следовательно:

```text
User accounts
→ данные конкретного Site
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

После S05C рабочее дерево должно быть чистым.

Проверьте, что Controller S05C уже находится в Git:

```bash
git -C apps/rental_training log -1 --oneline -- \
  rental_training/rental_training/doctype/rental/rental.py
```

---

# 5. Создать две Role через Desk

Если сервер разработки не работает:

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

Сам факт создания Role в БД Site не обязан автоматически создать файл в нашем App.

Это полезное наблюдение:

```text
Role создана на Site
≠
имя Role уже записано в обязательных метаданных App
```

Дальше мы добавим эти имена в permissions по умолчанию Standard DocTypes. Именно эти permission rows станут воспроизводимым источником: при синхронизации Frappe создаст отсутствующие Role на другом Site.

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

Добавьте или настройте строки уровня `0`.

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

Мы изменили **permissions по умолчанию Standard DocType собственного App**.

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

Ожидается изменение:

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

В текущем исходнике Frappe проверка permissions для child document учитывает `parenttype`.

Поэтому S05D не придумывает отдельную роль:

```text
Rental Item Operator
```

и не строит самостоятельный CRUD-процесс для строк.

Право пользователя редактировать набор Equipment проверяется в контексте возможности изменять родительский `Rental`.

---

# 11. Проверить изменения метаданных через Git

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

Важно другое:

```text
обязательные permissions по умолчанию
→ находятся в метаданных Standard DocType
→ видны Git
```

---

# 12. Не использовать Role Permission Manager как источник обязательных permissions

Frappe предоставляет `Role Permission Manager` — это нормальный штатный административный инструмент.

Но он способен создавать локальные переопределения Site относительно permissions DocType по умолчанию.

Для S05D нам нужна другая гарантия:

> После установки App на чистый Site базовая модель permissions уже существует без ручной донастройки.

Поэтому обязательные permissions мы редактировали в `Permissions` самих Standard DocTypes своего App.

Правило этапа:

```text
permissions приложения по умолчанию
→ метаданные Standard DocType

локальное изменение конкретного Site
→ Role Permission Manager может быть уместен
```

Мы не запрещаем Role Permission Manager. Мы просто не делаем локальное переопределение скрытым обязательным шагом установки приложения.

---

# 13. Почему отдельный Role fixture здесь не нужен

После разделов 7–9 оба имени Role уже находятся в `permissions[]` Standard DocTypes нашего App.

В Frappe v16.33.0 штатная синхронизация Standard DocType вызывает `make_module_and_roles()`:

```text
permissions[]
→ собрать имена Role
→ проверить наличие Role
→ создать отсутствующую Role
→ desk_access = 1
```

При `install-app` эта синхронизация происходит до `sync_fixtures()`.

Следовательно, схема:

```text
Standard DocPerm
+
Role fixture с тем же role_name
```

создала бы два механизма поставки одной ответственности.

Для учебного приложения используем более простой путь:

```text
Standard DocPerm
→ источник имени Role
→ штатная синхронизация Frappe создаёт отсутствующую Role
```

Отдельный Role fixture был бы оправдан только при дополнительном состоянии самой Role, которое требуется App и не выражается Standard DocPerm. В текущем требовании такого состояния нет.

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

# 15. Проверить, где хранится модель permissions

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
имена Role
+
Role → CRUD on DocType
→ permissions[] Standard DocType JSON

отсутствующую Role на новом Site
→ создаёт Frappe при синхронизации Standard metadata

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

Frappe автоматически предоставляет System Users роль `Desk User`; это инфраструктурная роль Framework, а не замена нашим прикладным ролям.

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

не должно создавать новые файлы пользователей в исходниках App.

Это правильно: `User` остаётся состоянием конкретного Site и не входит в обязательные метаданные приложения.

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

# 19. Посмотреть фактические CRUD-права программно

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

Она хорошо показывает итоговые permissions, но S05D должен проверить, что реальные операции Document действительно блокируются или разрешаются.

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

В актуальном `Document.insert()` Frappe выполняет проверку permission `create` до вставки Document.

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

Для чистоты учебного Site откатите эту **транзакцию console**:

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

Это одновременно подтверждает, что permissions и Controller S05C работают в одном обычном пути Document.

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

После rollback запись вернётся к исходному состоянию.

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

Ожидается `PermissionError`.

В актуальном Frappe `delete_doc()` документирует и выполняет проверку delete-permission, если `ignore_permissions=False`.

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

Теперь откатите всю временную транзакцию console:

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

Теперь выполните короткую проверку интерфейса.

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

Не оценивайте безопасность только по наличию или отсутствию кнопок. Серверные проверки уже выполнены предыдущими разделами.

## Под Manager

Войдите как:

```text
manager@example.test
```

Проверьте, что обычный CRUD всех трёх DocTypes доступен.

---

# 27. Почему скрытие UI не считается защитой

Допустим, кто-то сделал:

```javascript
frm.remove_custom_button("Delete")
```

или спрятал поле или кнопку CSS.

Это не меняет permission engine.

Пользователь может обращаться к данным другим путём:

```text
REST
Document API
другая форма
серверный метод
```

S05D считается пройденным только потому, что запрет находится в штатной серверной модели permissions.

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

Если такое требование появится, его нужно будет рассматривать отдельно.

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

Из репозитория App:

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

Для текущего приложения собственный код не должен содержать такой обход.

Также S05D не требует собственной проверки:

```python
if "Rental Manager" in frappe.get_roles():
    ...
```

для обычного CRUD.

CRUD уже принадлежит permission engine.

---

# 34. Зафиксировать модель permissions в Git

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

Проверьте подготовленный diff:

```bash
git diff --cached
```

Убедитесь, что в Git попали только permissions по умолчанию Standard DocTypes и нет случайных Users, паролей или Role fixture.

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

Но для **другого Site** смысл файлов App другой:

```text
Standard DocType JSON
        ↓
install / migrate sync
        ↓
DocPerm синхронизируются
        ↓
отсутствующие Role создаются Frappe
```

Это будет проверено на чистом Site в S08/S09.

---

# 36. Что не является частью Git после S05D

В репозитории не должны появиться:

```text
operator@example.test User record
manager@example.test User record
их пароли
sessions
конкретные Rentals
конкретные Customers
конкретные Equipment
```

В Git появляется обязательная модель permissions:

```text
Standard DocType JSON
└── permissions[]
    ├── Rental Operator
    └── Rental Manager
```

Отдельный Role fixture для этих двух имён текущему приложению не нужен.

---

# 37. Типовые неправильные решения

## Ошибка 1. Проверить всё под Administrator

```text
Administrator может создать Rental
→ значит permissions работают
```

Нет.

Administrator является специальным системным пользователем и не доказывает поведение прикладных ролей.

## Ошибка 2. Спрятать кнопку вместо запрета

```text
Operator не должен удалять Rental
→ скрыли Delete в JS
```

Это UI, а не авторизация.

Правильная ответственность:

```text
DocPerm.delete = 0
```

## Ошибка 3. Настроить всё только Role Permission Manager и забыть про воспроизводимость

На Site разработки всё выглядит правильно, но после чистой установки permissions по умолчанию приходится восстанавливать вручную.

Это значит, что обязательное состояние приложения не находится в Standard metadata App.

## Ошибка 4. Добавить Role fixture для имени, которое уже находится в Standard DocPerm

Так App начинает поставлять одну и ту же ответственность двумя путями:

```text
Standard DocPerm sync
+
Role fixture sync
```

Для текущего приложения это лишнее дублирование.

## Ошибка 5. Экспортировать Users

Учебный аккаунт конкретного человека — не обязательная конфигурация приложения.

## Ошибка 6. Добавить `ignore_permissions=True`, чтобы тест прошёл

Это уничтожает сам смысл проверки авторизации.

---

# 38. Три правильных решения

## Правильно 1. CRUD через DocPerm

Требование совпадает со стандартными permission types — значит используем их напрямую.

## Правильно 2. Permissions по умолчанию в Standard DocType metadata

Они принадлежат нашему App и воспроизводятся вместе с моделью.

## Правильно 3. Имя Role поставляется тем же Standard DocPerm

Frappe создаёт отсутствующую `Role` при синхронизации Standard DocType. Отдельный fixture появляется только при самостоятельном состоянии Role, которое требуется App и которого текущая модель не содержит.

---

# 39. Контрольная карта S05D

```text
[ ] создана Role Rental Operator на Site разработки
[ ] создана Role Rental Manager на Site разработки
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
[ ] Operator на сервере не может create Equipment
[ ] Operator на сервере может read Equipment
[ ] Operator на сервере может create Customer
[ ] Operator на сервере может create/write Rental
[ ] Operator на сервере не может delete Rental
[ ] Manager на сервере имеет полный CRUD
[ ] Desk отражает те же права
[ ] собственный код не использует ignore_permissions=True
[ ] обязательная модель permissions видна в Git
[ ] Users не попали в Git
[ ] рабочее дерево Git после commit чистое
```

---

# 40. Проверка перед S06

Перед переходом дальше должны быть проверены четыре уровня.

## 1. Модель

```text
Rental Operator
Rental Manager
```

существуют как прикладные Role.

DocPerm трёх обычных DocTypes соответствует утверждённой CRUD-матрице.

## 2. Серверная авторизация

Реальными серверными операциями проверено:

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

## 3. Воспроизводимость

```text
имена Role + DocPerm
→ Standard DocType JSON
→ синхронизация Standard metadata
→ отсутствующие Role создаёт Frappe

Users
→ только Site
```

После чистой установки не должно требоваться вручную создавать две обязательные Role или заново настраивать базовую CRUD-матрицу.

## 4. Архитектурная граница

Не добавлены без требования:

```text
Permission Level
Permission Type
If Owner
User Permission
Share
permission hooks
собственная ACL
JS-security
ignore_permissions=True
Role fixture, дублирующий Standard DocPerm
```

---

# 41. Когда не переходить к S06

Сначала исправьте проблему, если:

- права проверены только визуально;
- проверки выполнялись только под Administrator;
- Operator фактически может создать Equipment или удалить Rental;
- Manager не получает заявленный CRUD;
- `If Owner` включён без предметного требования;
- права существуют только как локальное переопределение Site;
- обязательные Role не воспроизводятся из Standard metadata App;
- добавлен Role fixture только для имён, уже находящихся в Standard DocPerm;
- Users или пароли попали в Git;
- собственный код обходит permission engine через `ignore_permissions=True`;
- JavaScript используется как единственная защита.

---

# 42. Что должно остаться после S05D

Предметная модель данных не изменилась.

Появилась отдельная модель авторизации:

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