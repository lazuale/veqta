# S08. Доказать, что обязательное состояние принадлежит App

К S08 CORE уже имеет модель, Controller, permissions и automated contracts. Теперь нужно доказать для каждого обязательного элемента:

```text
владелец
→ source of truth
→ штатный delivery path
→ проверка на текущем Site
```

S08 не добавляет новую бизнес-функцию. Это аудит поставки перед clean-site acceptance S09.

Нормативные документы:

- [`../BASELINE_CORRECTIONS.md`](../BASELINE_CORRECTIONS.md);
- [`../../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md`](../../frappe-architecture-standard/09_DEPLOYMENT_TESTING.md);
- [`../../frappe-architecture-standard/13_ROLE_PROVISIONING.md`](../../frappe-architecture-standard/13_ROLE_PROVISIONING.md).

Первичные источники Frappe v16.33.0:

- `frappe/installer.py::install_app()`;
- `frappe/core/doctype/doctype/doctype.py::make_module_and_roles()`;
- `frappe/migrate.py`;
- официальная документация `bench migrate`.

---

# 1. App-owned и Site-owned — не одно и то же

## App-owned CORE

```text
Module Rental Training
Equipment / Customer / Rental Item / Rental
fields / naming / default DocPerm
Rental Controller V01/V02/V03
role names, необходимые default DocPerm
Automated contracts
```

## Site-owned

```text
конкретные Users
пароли
runtime Equipment / Customer / Rental
local developer_mode
local allow_tests
naming counters
```

Главное правило:

```text
обязательное для продукта
→ должно воспроизводиться из App source штатным путём

конкретный пользователь/операция
→ остаётся Site data
```

---

# 2. Исправленный delivery manifest

| Элемент | Source of truth | Delivery |
|---|---|---|
| App | Git/Python package | App доступен Bench, затем `install-app` |
| Module | `modules.txt` | install/sync Module Def |
| Equipment | `equipment.json` | Standard DocType sync |
| Customer | `customer.json` | Standard DocType sync |
| Rental Item | `rental_item.json` | Standard DocType sync |
| Rental | `rental.json` | Standard DocType sync |
| fields / naming / default DocPerm | Standard DocType JSON | metadata/schema sync |
| `Rental Operator` / `Rental Manager` | role names в Standard DocPerm | `make_module_and_roles()` создаёт missing Role при sync |
| V01/V02/V03 | `rental.py` | Python source App |
| automated contracts | `test_rental.py` | Frappe test runner |
| Users/passwords/runtime data | Site DB/config | Site-local |

Для текущего CORE отсутствует строка:

```text
Role → fixtures/role.json
```

потому что она дублировала уже существующий source — Standard DocPerm.

---

# 3. Входная проверка

```bash
cd ~/frappe/rental-training-bench

bench --site rental.localhost list-apps -f text
bench --site rental.localhost run-tests --app rental_training
git -C apps/rental_training status --short
```

Ожидается:

```text
frappe
rental_training

tests green
Git clean
```

Если tests красные или Git содержит необъяснённые изменения, delivery audit не начинается.

---

# 4. Проверить Module source

```bash
cat apps/rental_training/rental_training/modules.txt
```

Ожидается:

```text
Rental Training
```

Runtime:

```bash
bench --site rental.localhost console
```

```python
print(frappe.db.exists("Module Def", "Rental Training"))
```

Module не должен требовать ручного создания после `install-app`.

---

# 5. Проверить Standard DocType source

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

for file in \
  rental_training/rental_training/doctype/equipment/equipment.json \
  rental_training/rental_training/doctype/customer/customer.json \
  rental_training/rental_training/doctype/rental_item/rental_item.json \
  rental_training/rental_training/doctype/rental/rental.json
do
  test -f "$file" && echo "OK  $file" || echo "MISSING  $file"
done
```

В этих JSON находятся обязательные:

```text
fields
field types
Links/Table MultiSelect
naming
title/view flags
Child metadata
default permissions
```

Отдельный SQL schema-файл для обычного Standard DocType не нужен.

---

# 6. Проверить runtime DocTypes и default permissions

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

```python
core_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]

print(
    frappe.get_all(
        "DocType",
        filters={"name": ["in", core_doctypes]},
        fields=["name", "module", "custom", "istable"],
        order_by="name asc",
    )
)
```

Должны существовать четыре Standard DocType нужного Module.

Теперь permissions:

```python
roles = {"Rental Operator", "Rental Manager"}

for doctype in ["Equipment", "Customer", "Rental"]:
    print("\n", doctype)
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
Operator → read only
Manager  → CRUD

Customer
Operator → read/create/write, no delete
Manager  → CRUD

Rental
Operator → read/create/write, no delete
Manager  → CRUD
```

---

# 7. Проверить role provisioning через Standard DocPerm

На текущем Site:

```python
for role in ["Rental Operator", "Rental Manager"]:
    print(role, frappe.db.exists("Role", role))
```

Обе Role должны существовать.

Но source-аудит теперь другой.

Проверьте App:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

find rental_training/fixtures -maxdepth 1 -type f -print 2>/dev/null | sort

grep -n "fixtures" rental_training/hooks.py || true
```

Для текущего CORE не должно требоваться:

```text
fixtures/role.json
filtered Role fixture
```

## Почему это воспроизводимо

Frappe v16.33.0 `make_module_and_roles()` при Standard DocType sync:

```text
читает doc.permissions
→ собирает role names
→ создаёт отсутствующие Role
→ desk_access = 1
```

А `install_app()` выполняет:

```text
sync_for(app)
→ Standard metadata + roles из DocPerm

потом

sync_fixtures(app)
```

Следовательно, Role fixture для этих двух имён не только не нужен — он был бы вторым механизмом доставки одной ответственности.

---

# 8. Проверить отсутствие скрытых Site overrides

В console:

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

Для принятого CORE ожидается:

```text
Custom Field    []
Property Setter []
Custom DocPerm  []
```

Если записи есть, сначала выясняется их ответственность. Их нельзя молча считать частью продукта только потому, что dev-site работает.

---

# 9. Проверить Controller и tests как App source

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git ls-files \
  rental_training/rental_training/doctype/rental/rental.py \
  rental_training/rental_training/doctype/rental/test_rental.py
```

Оба файла должны выводиться.

`rental.py` владеет V01/V02/V03.

`test_rental.py` владеет automated contracts нашего App.

Они не экспортируются fixtures и не заменяются Server Script без требования.

---

# 10. Проверить, что runtime Users не поставляются App

В source не должно быть product fixture, создающего:

```text
operator@example.test
manager@example.test
пароли
```

Конкретные Users принадлежат Site/test environment.

Формула:

```text
Role name + default capability
→ Standard DocPerm App

конкретный User + assignment Role
→ Site
```

---

# 11. `migrate` — update path, не магия

Перед migrate в dev Bench должны быть доступны необходимые services. Если `bench start` не работает, запустите его в отдельном терминале.

Затем:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost migrate
bench --site rental.localhost run-tests --app rental_training
git -C apps/rental_training status --short
```

Ожидается:

```text
migrate success
tests green
Git clean
```

`migrate` синхронизирует App state; он не является способом генерировать отсутствующий source после релиза.

---

# 12. Почему patch всё ещё не нужен

CORE остаётся первой поддерживаемой baseline-версией учебного App. Нет старой production-версии, данные которой требуется одноразово преобразовать.

Поэтому не создаём patch ради демонстрации механизма.

Patch станет обоснованным, когда появится:

```text
поддерживаемая старая версия
+
существующие данные
+
новая модель
+
необходимое одноразовое преобразование
```

---

# 13. Итоговый manifest S08

```text
Module
→ modules.txt

Standard DocTypes / fields / naming / DocPerm
→ Standard JSON

Rental Operator / Rental Manager
→ role names в Standard DocPerm
→ missing Role создаёт Frappe при sync

V01/V02/V03
→ rental.py

automated contracts
→ test_rental.py

Users / passwords / business Documents / local config
→ Site
```

---

# 14. ГОТОВО / НЕ ГОТОВО

## ГОТОВО

```text
✓ каждый обязательный элемент имеет owner/source/delivery
✓ default permissions находятся в Standard metadata
✓ роли воспроизводимы из DocPerm sync
✓ Role fixture не дублирует эту ответственность
✓ нет скрытых Custom Field/Property Setter/Custom DocPerm
✓ Users/runtime data не экспортированы как продукт
✓ migrate проходит
✓ tests green
✓ Git clean
✓ patch не создан без реальной data migration
```

## НЕ ГОТОВО

Если clean install всё ещё требует:

```text
создать Role вручную
экспортировать role.json
настроить default permissions через local override
добавить скрытый Custom Field
выполнить ручной SQL
```

S09 начинать нельзя.
