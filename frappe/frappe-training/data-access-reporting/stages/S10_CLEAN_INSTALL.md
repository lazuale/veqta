# S10. Проверить итоговый App на новом чистом Site

На `rental.localhost` мы вручную меняли permissions, создавали Reports и писали код. Сам факт, что этот Site работает, ещё не доказывает воспроизводимость App.

Финальное требование:

> Новый Site должен получить обязательные permissions, Standard Reports и код расчёта из `rental_training`, но не получить учебных Users, Rentals и персональный Report Builder текущего Site.

Связанные материалы:

- [`S09_AUTOMATED_TESTS.md`](S09_AUTOMATED_TESTS.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

---

## 1. Зафиксировать состояние App, которое проверяется

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Framework и Apps:

```bash
bench version --format plain
```

Используйте ту же совместимую линию Frappe v16, на которой проходились предыдущие этапы.

Проверьте Git учебного App:

```bash
git -C apps/rental_training status --short
git -C apps/rental_training rev-parse HEAD
```

Рабочее дерево должно быть чистым.

Clean install проверяет зафиксированное состояние App, а не локальные незакоммиченные изменения.

---

## 2. Что должно прийти из App

После установки обязаны существовать:

```text
Equipment
Customer
Rental
Rental Item

Rental Operator
Rental Manager
```

Для `Rental`:

```text
Rental Operator → If Owner = yes
Rental Manager  → Report = yes
```

Standard Reports:

```text
Equipment Rental History
Equipment Utilization
```

Оба должны быть manager-only.

Также App должен содержать Python/JS исходники `Equipment Utilization` и автоматические тесты.

---

## 3. Что не должно переноситься

Новый Site не должен получить рабочие данные старого Site:

```text
operator-a@example.test
operator-b@example.test
manager@example.test

Equipment records
Customer records
Rental records
Rental Item rows
```

Также не должен автоматически появиться сохранённый на S03 Custom Report Builder:

```text
Rental Count by Status
```

Это Site-owned состояние, а не обязательная конфигурация App.

---

## 4. Создать действительно новый Site

Используем имя:

```text
rental-reporting-clean.localhost
```

Сначала проверьте, что каталога ещё нет:

```bash
test ! -d sites/rental-reporting-clean.localhost \
  && echo "OK: clean Site does not exist" \
  || echo "STOP: Site already exists"
```

Если Site уже существует, не называйте его «чистым» и не продолжайте проверку поверх старого состояния.

Создайте новый Site обычным способом, принятым в вашей Bench-среде:

```bash
bench new-site rental-reporting-clean.localhost
```

Bench запросит необходимые локальные пароли БД/Administrator в соответствии с вашей установкой.

Не записывайте их в Git или документацию.

---

## 5. Проверить состояние до установки App

```bash
bench --site rental-reporting-clean.localhost list-apps -f text
```

До установки ожидается:

```text
frappe
```

Откройте console:

```bash
bench --site rental-reporting-clean.localhost console
```

Проверьте:

```python
for doctype in ["Equipment", "Customer", "Rental", "Rental Item"]:
    print(doctype, frappe.db.exists("DocType", doctype))

for role in ["Rental Operator", "Rental Manager"]:
    print(role, frappe.db.exists("Role", role))

for report in ["Equipment Rental History", "Equipment Utilization"]:
    print(report, frappe.db.exists("Report", report))
```

Все элементы `rental_training` должны отсутствовать.

Завершите:

```python
exit()
```

---

## 6. Не включать developer mode ради установки

На Site разработки developer mode был нужен для создания Standard metadata.

На чистом Site готовый App должен устанавливаться без него.

Проверьте:

```bash
bench --site rental-reporting-clean.localhost show-config \
  | grep developer_mode || true
```

Не включайте developer mode «чтобы Reports появились».

Если готовому App для установки требуется developer mode, поставка состояния спроектирована неправильно.

---

## 7. Установить `rental_training`

```bash
bench --site rental-reporting-clean.localhost install-app rental_training
```

Проверьте:

```bash
bench --site rental-reporting-clean.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Никаких ручных действий вида:

```text
создать Role
поставить If Owner
поставить Report permission
создать Query Report
создать Script Report
скопировать Python вручную
```

между `install-app` и проверкой быть не должно.

---

## 8. Проверить Standard DocType Permissions

Откройте console нового Site:

```bash
bench --site rental-reporting-clean.localhost console
```

Выполните:

```python
meta = frappe.get_meta("Rental")

for permission in meta.permissions:
    if permission.role in {"Rental Operator", "Rental Manager"}:
        print(
            permission.role,
            "read=", permission.read,
            "create=", permission.create,
            "write=", permission.write,
            "delete=", permission.delete,
            "if_owner=", permission.if_owner,
            "report=", permission.report,
        )
```

Ожидаемый смысл:

```text
Rental Operator
→ Read/Create/Write
→ If Owner = 1
→ Delete = 0

Rental Manager
→ CRUD
→ If Owner = 0
→ Report = 1
```

Отдельный Role fixture только ради этих имён не требуется: роли являются частью permission rows Standard DocType и должны появиться при штатной синхронизации App.

---

## 9. Проверить Standard Reports

В той же console:

```python
for report_name in [
    "Equipment Rental History",
    "Equipment Utilization",
]:
    report = frappe.get_doc("Report", report_name)
    print(
        report.name,
        report.report_type,
        report.is_standard,
        report.ref_doctype,
        [row.role for row in report.roles],
    )
```

Ожидается:

```text
Equipment Rental History
→ Query Report
→ Standard
→ Rental
→ Rental Manager

Equipment Utilization
→ Script Report
→ Standard
→ Rental
→ Rental Manager
```

`Rental Operator` не должен находиться в allowed roles этих Reports.

---

## 10. Проверить отсутствие Site-owned данных

В той же console:

```python
for email in [
    "operator-a@example.test",
    "operator-b@example.test",
    "manager@example.test",
]:
    print(email, frappe.db.exists("User", email))

for doctype in ["Equipment", "Customer", "Rental", "Rental Item"]:
    print(doctype, frappe.db.count(doctype))

print(
    "Rental Count by Status",
    frappe.db.exists("Report", "Rental Count by Status"),
)
```

Ожидается:

```text
учебных Users → нет
рабочих Documents → 0
Custom Report Builder → нет
```

Системные данные самого Frappe в других DocTypes, конечно, присутствуют.

Завершите console:

```python
exit()
```

---

## 11. Выполнить `migrate`

После установки выполните обычный миграционный путь:

```bash
bench --site rental-reporting-clean.localhost migrate
```

После `migrate` обязательное состояние должно остаться тем же.

Повторите короткую проверку Reports и Rental permissions, если хотите убедиться, что синхронизация не создаёт расхождений.

---

## 12. Запустить App tests на чистом Site

Для test Site локально разрешите tests:

```bash
bench --site rental-reporting-clean.localhost \
  set-config allow_tests 1 --parse
```

Запустите:

```bash
bench --site rental-reporting-clean.localhost \
  run-tests --app rental_training
```

Tests должны сами создать необходимые временные Users и Documents.

Они не должны требовать ручного восстановления контрольных данных S00.

---

## 13. Проверить App Git ещё раз

Возвращаемся к исходникам:

```bash
git -C apps/rental_training status --short
```

Clean install, `migrate` и запуск tests на другом Site не должны изменять исходники App.

---

## 14. Что доказано

После S10 граница выглядит так:

```text
App-owned
├── Standard DocTypes
├── Standard DocType Permissions
│   ├── Rental Operator → If Owner
│   └── Rental Manager → Report
├── Standard Query Report
├── Standard Script Report
├── Python/JS Report source
└── automated tests

Site-owned
├── Users/passwords
├── Equipment
├── Customer
├── Rental / Rental Item
├── control data
└── saved custom Report Builder
```

Это и есть финальный результат практикума.

---

## Результат практикума

После S00–S10 ученик прошёл один связный путь:

```text
готовая предметная модель
→ реальная permission boundary
→ List View
→ Report Builder
→ get_list / get_all / get_doc
→ Query Report
→ Script Report
→ Recorder
→ frappe.qb.get_query
→ automated contracts
→ clean Site
```

Главный навык — не запомнить список API, а выбирать способ чтения и представления данных по ответственности задачи и проверять границы доступа и производительности фактически.
