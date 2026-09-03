# S10. Проверить процесс на новом чистом Site

S08 показал, откуда должна восстанавливаться обязательная конфигурация, а S09 закрепил правила процесса автоматическими тестами.

Теперь это нужно проверить на новом Site, где `purchase_lifecycle_training` раньше не настраивался вручную.

> Новый Site должен получить обязательный Workflow из App и пройти те же проверки без скрытых восстановительных действий.

Контрольный Site:

```text
purchase-lifecycle-acceptance.localhost
```

Связанные документы:

- [`S08_APP_STATE_DELIVERY.md`](S08_APP_STATE_DELIVERY.md);
- [`S09_AUTOMATED_TESTS.md`](S09_AUTOMATED_TESTS.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../ROADMAP.md`](../ROADMAP.md);
- [`../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- https://docs.frappe.io/framework/user/en/bench/reference/new-site
- https://docs.frappe.io/framework/user/en/bench/reference/migrate
- https://docs.frappe.io/framework/user/en/testing
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/installer.py
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/migrate.py

---

# 1. Что проверяет S10

До S10 всё разрабатывалось на:

```text
purchase-lifecycle.localhost
```

На нём мы вручную создавали Workflow State, Workflow Action Master и сам Workflow.

Поэтому факт:

```text
процесс работает на dev Site
```

ещё не доказывает:

```text
обязательная конфигурация воспроизводится из App
```

Контрольный Site находится в том же совместимом Bench, но имеет свою БД, свои настройки, своих Users и свои рабочие Documents.

## Что здесь не проверяется

S10 не является проверкой промышленного развёртывания и не охватывает:

```text
reverse proxy
TLS
backup/restore
HA
CI/CD
отдельный production server
```

Здесь проверяется только воспроизводимость Frappe App на чистом Site.

---

# 2. Проверить исходники учебного App

Перед чистой установкой:

```bash
cd ~/frappe/rental-training-bench

git -C apps/purchase_lifecycle_training status --short
```

Рабочее дерево должно быть понятным и зафиксированным.

Убедитесь, что исходники содержат:

```text
Purchase Request Standard metadata
hooks.py с filtered fixtures
fixture files в нужном порядке
автоматические тесты Workflow
```

и не содержат:

```text
User fixtures
Role fixture без отдельной причины
текущие Workflow Action
рабочие Purchase Request
```

---

# 3. Создать новый Site

```bash
bench new-site purchase-lifecycle-acceptance.localhost
```

Не включайте developer mode.

Проверьте Apps до установки:

```bash
bench --site purchase-lifecycle-acceptance.localhost list-apps -f text
```

Ожидается только:

```text
frappe
```

App уже доступен Bench в `apps/`, но ещё не установлен на этот Site.

---

# 4. Проверить состояние до install-app

```bash
bench --site purchase-lifecycle-acceptance.localhost console
```

```python
checks = [
    ("DocType", "Purchase Request"),
    ("Role", "PLT Requester"),
    ("Role", "PLT Approver"),
    ("Role", "PLT Senior Approver"),
    ("Workflow State", "PLT Draft"),
    ("Workflow State", "PLT Pending Approval"),
    ("Workflow State", "PLT Rejected"),
    ("Workflow State", "PLT Pending Senior"),
    ("Workflow State", "PLT Approved"),
    ("Workflow State", "PLT Cancelled"),
    ("Workflow", "PLT Purchase Request Approval"),
    ("Workflow Action Master", "PLT Submit for Review"),
    ("Workflow Action Master", "PLT Cancel Request"),
]

for doctype, name in checks:
    print(doctype, name, bool(frappe.db.exists(doctype, name)))
```

Для записей нашего App ожидается `False`.

Завершите console:

```python
exit()
```

Если эти записи уже существуют, Site не является чистой контрольной площадкой.

---

# 5. Установить App без ручной настройки

```bash
bench --site purchase-lifecycle-acceptance.localhost \
  install-app purchase_lifecycle_training
```

После установки:

```bash
bench --site purchase-lifecycle-acceptance.localhost list-apps -f text
```

Ожидается:

```text
frappe
purchase_lifecycle_training
```

Между `install-app` и проверкой не открывайте Role или Workflow для ручного исправления. Если обязательная конфигурация не появилась из App, это ошибка поставки.

---

# 6. Проверить состояние сразу после install-app

```bash
bench --site purchase-lifecycle-acceptance.localhost console
```

```python
checks = [
    ("DocType", "Purchase Request"),
    ("Role", "PLT Requester"),
    ("Role", "PLT Approver"),
    ("Role", "PLT Senior Approver"),
    ("Workflow State", "PLT Draft"),
    ("Workflow State", "PLT Pending Approval"),
    ("Workflow State", "PLT Rejected"),
    ("Workflow State", "PLT Pending Senior"),
    ("Workflow State", "PLT Approved"),
    ("Workflow State", "PLT Cancelled"),
    ("Workflow", "PLT Purchase Request Approval"),
    ("Workflow Action Master", "PLT Submit for Review"),
    ("Workflow Action Master", "PLT Cancel Request"),
]

for doctype, name in checks:
    print(doctype, name, bool(frappe.db.exists(doctype, name)))
```

Теперь все строки должны быть `True`.

Проверьте поле `status` и `amended_from`:

```python
status = frappe.get_meta("Purchase Request").get_field("status")
print(status.fieldtype)
print(status.no_copy)
print(status.allow_on_submit)
print(frappe.get_meta("Purchase Request").get_field("amended_from"))
```

Ожидается по смыслу:

```text
status = Select
No Copy = 1
Allow on Submit = 0
amended_from существует
```

Завершите console:

```python
exit()
```

---

# 7. Проверить обычный migrate

```bash
bench --site purchase-lifecycle-acceptance.localhost migrate
```

После `migrate` обязательная конфигурация должна остаться той же. App должен воспроизводить своё состояние не только при первой установке, но и через обычный путь обновления Site.

---

# 8. Запустить полный набор тестов App

Разрешите тесты только на контрольном Site:

```bash
bench --site purchase-lifecycle-acceptance.localhost \
  set-config allow_tests 1 --parse
```

Запустите:

```bash
bench --site purchase-lifecycle-acceptance.localhost \
  run-tests --app purchase_lifecycle_training
```

Тесты не должны создавать отсутствующие Workflow, Role или Workflow State. Поэтому успешный запуск на чистом Site одновременно проверяет, что поставка состояния из S08 действительно работает.

---

# 9. Пройти рабочий сценарий через Desk

Автоматические тесты не заменяют пользовательскую проверку интерфейса.

На контрольном Site создайте пользователей:

```text
requester@example.test → PLT Requester
approver@example.test  → PLT Approver
senior@example.test    → PLT Senior Approver
```

Затем пройдите минимум два маршрута.

## Маленькая заявка

```text
Requester создаёт заявку на 500
→ PLT Submit for Review
→ Approver выполняет Approve
→ PLT Approved / docstatus 1
```

## Большая заявка

```text
Requester создаёт заявку на 1500
→ PLT Submit for Review
→ Approver выполняет Approve
→ PLT Pending Senior
→ Senior выполняет Approve
→ PLT Approved / docstatus 1
```

После этого отмените одну Submitted заявку:

```text
Approver
→ PLT Cancel Request
→ PLT Cancelled / docstatus 2
```

и под Requester выполните Amend:

```text
PLT Cancelled
→ Amend
→ новый PLT Draft / docstatus 0
→ amended_from = name исходной заявки
```

---

# 10. Что считается провалом

Чистая установка не пройдена, если после `install-app` требуется вручную:

```text
создать PLT Role
создать Workflow State
создать Workflow Action Master
создать Workflow
добавить workflow_state Custom Field
добавить amended_from
восстановить default DocPerm
править БД через SQL
```

Проверка также не пройдена, если App работает только на dev Site благодаря случайным локальным настройкам, которых нет в исходниках.

---

# Финальный результат

После S10 ученик должен уметь объяснить весь путь:

```text
обычный Purchase Request и status
→ Workflow появляется только для управляемых переходов
→ Submit появляется только когда окончательное решение нужно зафиксировать
→ Cancel отменяет Submitted Document
→ Amend создаёт новый Draft из отменённой заявки
→ обязательная конфигурация воспроизводится из App на чистом Site
```

Практикум завершён.
