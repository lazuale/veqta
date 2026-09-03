# S09. Доказать CORE на новом чистом Site

S09 — финальный acceptance первого CORE. Он ничего не проектирует заново.

Требование:

> Новый Site должен получить всю обязательную модель `rental_training` из committed App source без скрытого ручного восстановления.

Нормативные документы:

- [`S08_APP_STATE_DELIVERY_AUDIT.md`](S08_APP_STATE_DELIVERY_AUDIT.md);
- [`../BASELINE_CORRECTIONS.md`](../BASELINE_CORRECTIONS.md);
- [`../../frappe-architecture-standard/13_ROLE_PROVISIONING.md`](../../frappe-architecture-standard/13_ROLE_PROVISIONING.md).

S09 проверяет воспроизводимость Frappe App в совместимом Bench. Это **не** production deployment test.

---

# 1. Зафиксировать source App

```bash
cd ~/frappe/rental-training-bench

bench version --format plain
git -C apps/rental_training status --short
git -C apps/rental_training rev-parse HEAD
```

Для принятого baseline Framework:

```text
Frappe 16.33.0
```

Git App должен быть clean. Зафиксируйте commit SHA.

Проверяем именно committed `rental_training`, а не незакоммиченную папку dev-site.

---

# 2. Acceptance Site не должен зависеть от developer mode

Проверьте общий config:

```bash
grep -n 'developer_mode' sites/common_site_config.json || true
```

В актуальном практикуме developer mode не является обязательной глобальной настройкой Bench.

Dev-site:

```bash
bench --site rental.localhost show-config | grep developer_mode
```

Acceptance-site будет работать без developer mode.

---

# 3. Создать новый Site без App

Убедитесь, что Site ещё не существует:

```bash
test ! -d sites/rental-acceptance.localhost \
  && echo "OK: new acceptance site" \
  || echo "STOP: site already exists"
```

Создайте:

```bash
bench new-site rental-acceptance.localhost \
  --db-root-username frappe_admin
```

Не используйте здесь:

```text
--install-app rental_training
--force поверх старого acceptance Site
```

Нам нужна контрольная точка **до установки**.

---

# 4. Доказать чистое состояние ДО install-app

```bash
bench --site rental-acceptance.localhost list-apps -f text
```

Ожидается:

```text
frappe
```

Откройте console:

```bash
bench --site rental-acceptance.localhost console
```

```python
core_doctypes = ["Equipment", "Customer", "Rental", "Rental Item"]
core_roles = ["Rental Operator", "Rental Manager"]

print("apps", frappe.get_installed_apps())

for doctype in core_doctypes:
    print("doctype", doctype, frappe.db.exists("DocType", doctype))

for role in core_roles:
    print("role", role, frappe.db.exists("Role", role))
```

До установки:

```text
Equipment   absent
Customer    absent
Rental      absent
Rental Item absent

Rental Operator absent
Rental Manager  absent
```

Если CORE уже существует, Site не является чистой контрольной площадкой.

```python
exit()
```

---

# 5. Проверить отсутствие Role fixture в App

До установки App проверьте source:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

find rental_training/fixtures -maxdepth 1 -type f -print 2>/dev/null | sort

test ! -f rental_training/fixtures/role.json \
  && echo "OK: no Role fixture" \
  || echo "STOP: unexpected role.json"
```

Для принятого CORE `Rental Operator` и `Rental Manager` не должны доставляться `role.json`.

Их source — role names в Standard DocPerm.

---

# 6. Установить App

```bash
cd ~/frappe/rental-training-bench
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

## Что именно должен сделать Frappe

Для этого acceptance важен порядок Frappe v16.33.0:

```text
install_app()
↓
add Module Def
↓
sync_for(rental_training)
↓
Standard DocType JSON / DocPerm
↓
make_module_and_roles()
↓
missing Rental Operator / Rental Manager создаются
↓
App регистрируется
↓
sync_jobs()
↓
sync_fixtures()
```

То есть обе Role должны появиться **до и независимо от Role fixtures**, которых в CORE нет.

---

# 7. Доказать delivery сразу после install-app

```bash
bench --site rental-acceptance.localhost console
```

## Module

```python
print(frappe.db.exists("Module Def", "Rental Training"))
```

## Standard DocTypes

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

Должно быть четыре Standard DocType.

## Roles — главный corrected acceptance

```python
for role in ["Rental Operator", "Rental Manager"]:
    print(role, frappe.db.exists("Role", role))
```

Ожидается truthy для обеих Role.

При этом:

```text
мы их не создавали вручную на acceptance Site
role.json отсутствует
```

Если Role не появились, acceptance провален и архитектурная гипотеза должна быть пересмотрена.

## Default permissions

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
Operator → Read only
Manager  → CRUD

Customer
Operator → Read/Create/Write
Manager  → CRUD

Rental
Operator → Read/Create/Write
Manager  → CRUD
```

## Нет скрытых Site-customizations

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

```python
exit()
```

---

# 8. Запустить migrate как обычный update path

В development Bench перед migrate должны работать необходимые services. При необходимости в отдельном терминале:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Затем:

```bash
bench --site rental-acceptance.localhost migrate
```

После migrate снова проверьте Role и permissions. Они не должны исчезнуть или требовать ручного восстановления.

---

# 9. Включить tests только на acceptance Site

```bash
bench --site rental-acceptance.localhost set-config allow_tests 1 --parse
bench --site rental-acceptance.localhost run-tests --app rental_training
```

Ожидается полный green suite.

`allow_tests` — Site-local test config, не App fixture.

---

# 10. Создать Site-local Users

Только после того как App уже доставил Role, создайте на acceptance Site:

```text
operator@example.test
manager@example.test
```

Назначьте:

```text
operator@example.test → Rental Operator
manager@example.test  → Rental Manager
```

Не создавайте Role вручную.

Это принципиальная последовательность:

```text
App install
→ capability model уже существует
→ Site admin назначает capability конкретным Users
```

---

# 11. Проверить permissions реальными операциями

Под Operator:

```text
Equipment read             ✓
Equipment create           ✗
Customer create/write      ✓
Rental create/write        ✓
Rental delete              ✗
```

Под Manager:

```text
Equipment CRUD ✓
Customer CRUD  ✓
Rental CRUD    ✓
```

Проверяйте не только кнопки Desk, но и server-side операции так же, как в S05D/S07.

---

# 12. Пройти реальный вертикальный сценарий

Под Manager создайте на acceptance Site:

```text
Equipment A
Equipment B
Customer A
Rental A = Active
```

Период Rental A, например:

```text
2026-09-10 .. 2026-09-12
```

с Equipment A.

Убедитесь, что запись сохраняется.

Под Operator создайте обычный допустимый Planned Rental и убедитесь, что права работают как ожидается.

---

# 13. Проверить V01/V02/V03 на новом Site

Новый Site должен доказать не только metadata, но и Python behavior.

## V01

```text
end_date < start_date
→ reject
```

## V02

Обычным Document path программно сформируйте duplicate Equipment rows:

```text
same Equipment twice
→ reject
```

## V03

После Active Rental A:

```text
same Equipment
Active
2026-09-11 .. 2026-09-13
→ reject
```

А:

```text
same Equipment
Active
2026-09-13 .. 2026-09-14
→ allow
```

Это доказывает, что Controller source приехал вместе с App, а не жил в runtime customization старого Site.

---

# 14. Повторить tests после обычных runtime данных

```bash
bench --site rental-acceptance.localhost run-tests --app rental_training
```

Suite должен оставаться green.

Runtime business Documents не должны делать tests зависимыми от «идеально пустого» Site.

---

# 15. Проверить source App после acceptance

```bash
git -C apps/rental_training status --short
git -C apps/rental_training rev-parse HEAD
```

Ожидается:

```text
Git clean
commit SHA тот же
```

Создание Site, Users и business Documents не должно менять source App.

Особенно не должно внезапно появиться:

```text
fixtures/role.json
```

---

# 16. Что запрещено делать ради зелёного S09

```text
создать Role вручную на acceptance Site
добавить role.json после неудачной установки без анализа причины
включить developer_mode на acceptance Site
создать Custom Field вручную
исправить permission через local Role Permission Manager override
использовать ignore_permissions=True
выполнить ручной SQL для mandatory state
```

Если без такого действия App не проходит acceptance, проблема должна быть исправлена в source architecture.

---

# 17. Финальный контракт CORE

```text
clean compatible Frappe Site
+
committed rental_training
+
install-app
+
Standard DocType metadata / DocPerm
+
native Role provisioning from DocPerm
+
Controller V01/V02/V03
+
migrate
+
automated tests
+
Site-local Users
+
real Desk/server scenario
=
reproducible CORE App
```

---

# 18. ГОТОВО / НЕ ГОТОВО

## ГОТОВО

```text
✓ до install-app CORE DocTypes и Role отсутствовали
✓ acceptance Site не требовал developer_mode
✓ install-app создал Module и Standard DocTypes
✓ Rental Operator/Manager появились из DocPerm sync без Role fixture
✓ default permissions совпадают с matrix
✓ нет обязательных Custom Field/Property Setter/Custom DocPerm
✓ migrate success
✓ tests green
✓ Site-local Users назначены уже существующим Role
✓ permissions доказаны реальными operations
✓ V01/V02/V03 работают
✓ повторный test suite green
✓ App Git clean и commit не изменился
✓ никаких ручных восстановительных действий не потребовалось
```

## НЕ ГОТОВО

Если роль, permission, DocType или behavior пришлось восстановить вручную после `install-app`, CORE не считается воспроизводимым.
