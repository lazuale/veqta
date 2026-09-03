# S05D. Настроить базовые роли и доказать права серверными операциями

К S05D приложение уже имеет рабочую CORE-модель и серверные инварианты, но почти всё проверялось под `Administrator`.

Новое требование:

> `Rental Operator` должен работать с Customer и Rental, но только читать Equipment и не удалять бизнес-записи. `Rental Manager` должен иметь полный CRUD текущего CORE.

Используем только штатную модель:

```text
User
Role
DocType Permissions
```

Нормативные документы:

- [`../BASELINE_CORRECTIONS.md`](../BASELINE_CORRECTIONS.md);
- [`../../frappe-architecture-standard/04_SECURITY.md`](../../frappe-architecture-standard/04_SECURITY.md);
- [`../../frappe-architecture-standard/13_ROLE_PROVISIONING.md`](../../frappe-architecture-standard/13_ROLE_PROVISIONING.md).

Первичные источники Frappe v16.33.0:

- `frappe/permissions.py`;
- `frappe/model/document.py`;
- `frappe/model/delete_doc.py`;
- `frappe/core/doctype/doctype/doctype.py::make_module_and_roles()`.

---

# 1. Permission matrix сначала, клики потом

## Rental Operator

| DocType | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Equipment | yes | no | no | no |
| Customer | yes | yes | yes | no |
| Rental | yes | yes | yes | no |

## Rental Manager

| DocType | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Equipment | yes | yes | yes | yes |
| Customer | yes | yes | yes | yes |
| Rental | yes | yes | yes | yes |

Не включаем без требования:

```text
Submit
Cancel
Amend
If Owner
Permission Level
User Permission
Share
custom ACL
ignore_permissions=True
```

`Rental` не является Submittable, поэтому `Submit/Cancel/Amend` здесь не имеют предметной ответственности.

---

# 2. Что принадлежит App, а что Site

Ключевая коррекция baseline:

```text
default permission matrix
→ Standard DocType JSON

role names, используемые этой matrix
→ те же DocPerm rows
→ missing Role создаёт Frappe при Standard DocType sync
```

В текущем Frappe `DocType.make_module_and_roles()` при install/sync собирает роли из `permissions` Standard DocType и создаёт отсутствующие `Role` с `desk_access=1`.

Поэтому для текущего CORE **не нужны**:

```text
Role fixture
hooks.py fixtures = Role
fixtures/role.json
export-fixtures Role
```

Это не значит, что Role не App-owned по смыслу. Это значит, что её необходимое имя уже доставляется более нативным механизмом — Standard DocPerm.

Site-owned остаются:

```text
operator@example.test
manager@example.test
пароли
назначение Role конкретным Users
```

---

# 3. Создать роли на dev-site только как setup для настройки

Чтобы выбрать роли в Link-полях таблицы Permissions через Desk, на текущем dev-site удобно сначала создать:

```text
Rental Operator
Rental Manager
```

Через Awesomebar откройте `Role` и создайте обе записи:

```text
Role Name   : Rental Operator
Desk Access : yes
Disabled    : no

Role Name   : Rental Manager
Desk Access : yes
Disabled    : no
```

Важно:

```text
ручное создание Role на dev-site
= удобство разработки текущего Site

НЕ
= обязательный install step продукта
```

Чистая установка S09 должна воспроизвести эти Role без такого ручного шага.

---

# 4. Настроить default permissions в Standard DocTypes

Работайте под `Administrator` на `rental.localhost` в developer mode.

## Equipment

`Rental Operator`:

```text
Read   yes
Create no
Write  no
Delete no
```

`Rental Manager`:

```text
Read   yes
Create yes
Write  yes
Delete yes
```

## Customer

`Rental Operator`:

```text
Read   yes
Create yes
Write  yes
Delete no
```

`Rental Manager`:

```text
Read   yes
Create yes
Write  yes
Delete yes
```

## Rental

`Rental Operator`:

```text
Read   yes
Create yes
Write  yes
Delete no
```

`Rental Manager`:

```text
Read   yes
Create yes
Write  yes
Delete yes
```

Не включайте `If Owner` и дополнительные permission-флаги без отдельного требования.

`Rental Item` не получает самостоятельную CRUD-матрицу: это Child DocType, работающий в контексте родительского `Rental`.

---

# 5. Доказать source of truth через Git

Перейдите в App:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
```

Проверьте:

```bash
git status --short
```

Ожидаемые App-owned изменения:

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

В JSON должны быть permission rows с:

```text
Rental Operator
Rental Manager
```

и нужными CRUD-флагами.

## Чего не должно появиться

```text
rental_training/fixtures/role.json
новый fixtures hook только ради Role
экспорт всех Role Site
```

Если после S05D вы видите `role.json`, остановитесь и разберите, какая отдельная ответственность Role требует fixture. Для принятого CORE такой ответственности нет.

---

# 6. Создать Site-local test Users

Создайте через Desk два System User:

```text
operator@example.test
manager@example.test
```

`Send Welcome Email` для учебного Site можно выключить.

Назначьте:

```text
operator@example.test → Rental Operator
manager@example.test  → Rental Manager
```

Не назначайте `System Manager`.

Пароли не записываются в Git и документацию.

Frappe может автоматически добавлять системные роли вроде `All`/`Desk User`; это не отменяет проверку наших предметных Role.

---

# 7. Проверить effective roles

Откройте console:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

```python
operator = "operator@example.test"
manager = "manager@example.test"

print(frappe.get_roles(operator))
print(frappe.get_roles(manager))
```

Ожидается присутствие соответственно:

```text
Rental Operator
Rental Manager
```

---

# 8. Проверить CRUD через permission engine

```python
def show_crud(user, doctype):
    frappe.set_user(user)
    print(
        user,
        doctype,
        {
            ptype: frappe.has_permission(doctype, ptype)
            for ptype in ("read", "create", "write", "delete")
        },
    )

for user in (operator, manager):
    for doctype in ("Equipment", "Customer", "Rental"):
        show_crud(user, doctype)

frappe.set_user("Administrator")
```

Контракт:

```text
Operator
Equipment R---
Customer  RCW-
Rental    RCW-

Manager
Equipment RCWD
Customer  RCWD
Rental    RCWD
```

Буквенная форма здесь только памятка; контракт — реальные boolean permissions.

---

# 9. Доказать права реальными Document operations

## Operator не может создать Equipment

```python
frappe.set_user(operator)

try:
    frappe.get_doc({
        "doctype": "Equipment",
        "equipment_name": "Forbidden Operator Equipment",
        "equipment_type": "Tool",
        "serial_number": "S05D-DENIED-001",
    }).insert()
except frappe.PermissionError as exc:
    print("BLOCKED operator create Equipment:", exc)
    frappe.db.rollback()
```

## Operator может читать Equipment

```python
rows = frappe.get_list(
    "Equipment",
    fields=["name", "equipment_name"],
    limit_page_length=5,
)
print(rows)
```

Для user-visible проверки используется `get_list`, а не permission-bypassing `get_all`.

## Operator может создать Customer

```python
customer = frappe.get_doc({
    "doctype": "Customer",
    "customer_name": "S05D Operator Customer",
    "email": "s05d-operator-customer@example.test",
})
customer.insert()
print(customer.name)
frappe.db.rollback()
```

## Operator может создать Rental

Возьмите существующие Customer и Equipment через `frappe.get_list()`, затем создайте валидный Planned Rental обычным `insert()`.

После успешной диагностической проверки вызовите `frappe.db.rollback()`, чтобы не загрязнять учебные данные.

## Operator не может удалить Rental

```python
frappe.set_user(operator)

rental_name = frappe.get_list("Rental", pluck="name", limit_page_length=1)[0]

try:
    frappe.delete_doc("Rental", rental_name)
except frappe.PermissionError as exc:
    print("BLOCKED operator delete Rental:", exc)
    frappe.db.rollback()
```

## Manager имеет полный CRUD

Под `manager` создайте временный Equipment, прочитайте его, измените через `.save()` и удалите через `frappe.delete_doc()`.

После проверки:

```python
frappe.db.rollback()
frappe.set_user("Administrator")
```

---

# 10. UI — только отражение server permissions

Войдите через Desk под обоими test Users.

Operator должен наблюдать:

```text
Equipment → read only
Customer  → create/edit, без delete
Rental    → create/edit, без delete
```

Manager:

```text
Equipment → full CRUD
Customer  → full CRUD
Rental    → full CRUD
```

Но отсутствие кнопки не считается доказательством безопасности. Доказательство уже выполнено server-side операциями.

---

# 11. Delivery contract S05D

После этапа source должен выглядеть концептуально так:

```text
Standard DocType JSON
├── Equipment permissions
├── Customer permissions
└── Rental permissions
       ↓
role names
Rental Operator / Rental Manager
       ↓
на clean install Frappe sync создаёт missing Role
```

Не так:

```text
DocPerm JSON
+
Role fixture с теми же именами
```

Если Role когда-нибудь получит отдельное App-owned состояние, которого нет в обычном `make_module_and_roles()` baseline, тогда fixture будет рассмотрен заново из нового требования.

---

# 12. Git checkpoint

На этом этапе App Git должен содержать изменения permission metadata и **не требовать** Role fixture.

Проверьте:

```bash
git status --short
```

После проверки изменений:

```bash
git add \
  rental_training/rental_training/doctype/equipment/equipment.json \
  rental_training/rental_training/doctype/customer/customer.json \
  rental_training/rental_training/doctype/rental/rental.json

git diff --cached

git commit -m "feat: add rental permissions"
```

Не добавляйте runtime Users.

---

# 13. ГОТОВО / НЕ ГОТОВО

## ГОТОВО

```text
✓ permission matrix определена до настройки
✓ Operator/Manager permissions находятся в Standard DocType JSON
✓ роли присутствуют на dev-site и назначены test Users
✓ реальные server operations подтверждают ограничения
✓ нет JS-security вместо server permissions
✓ нет ignore_permissions=True как фикса модели
✓ нет Role fixture без дополнительной ответственности
✓ ученик объясняет, что clean install создаст missing Role из DocPerm sync
```

## НЕ ГОТОВО

Если:

```text
права доказаны только Administrator/UI;
mandatory defaults живут только в Role Permission Manager overrides;
Role fixture добавлен просто ради двух role_name;
Users/пароли попали в Git;
оператор получил лишний CRUD;
permission bypass используется вместо исправления модели.
```

Следующий этап не должен считать permission model принятой, пока эти условия не выполнены.
