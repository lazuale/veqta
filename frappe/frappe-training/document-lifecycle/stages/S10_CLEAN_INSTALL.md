# S10. Доказать lifecycle на новом чистом Site

Финальная проверка практикума — не ещё один сценарий на dev Site, а установка App там, где его lifecycle никогда не настраивали вручную.

Новый acceptance Site:

```text
purchase-lifecycle-acceptance.localhost
```

Он должен получить обязательное состояние только из App source и штатных механизмов Frappe.

## 1. Проверить Git учебного App

Перед чистой установкой:

```bash
cd ~/frappe/rental-training-bench

git -C apps/purchase_lifecycle_training status --short
```

Рабочее дерево должно быть понятным и зафиксированным.

Убедитесь, что source содержит:

```text
Purchase Request Standard metadata
hooks.py с filtered fixtures
ordered fixture files
workflow tests
```

и не содержит:

```text
User fixtures
Role fixture без отдельной причины
runtime Workflow Action
Purchase Request business data
```

## 2. Создать новый Site

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

## 3. Проверить отсутствие обязательного состояния до install-app

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

Для App-specific записей ожидается `False`.

Завершите console:

```python
exit()
```

## 4. Установить App без ручного setup

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

Не открывайте между install и проверкой Role/Workflow редакторы, чтобы «докликать» отсутствующее состояние. Если что-то не приехало из App, это ошибка delivery.

## 5. Проверить, что обязательная конфигурация появилась

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

Проверьте state field:

```python
status = frappe.get_meta("Purchase Request").get_field("status")
print(status.fieldtype)
print(status.no_copy)
print(status.allow_on_submit)
print(frappe.get_meta("Purchase Request").get_field("amended_from"))
```

Ожидается по смыслу:

```text
status = Standard Select
No Copy = 1
Allow on Submit = 0
amended_from существует
```

Завершите console:

```python
exit()
```

## 6. Проверить обычный migrate path

```bash
bench --site purchase-lifecycle-acceptance.localhost migrate
```

После `migrate` обязательная конфигурация должна остаться той же. Это важно: App должен работать не только в момент первого install, но и через обычный update path Frappe.

## 7. Запустить полный test suite App

Разрешите tests только на acceptance Site:

```bash
bench --site purchase-lifecycle-acceptance.localhost \
  set-config allow_tests 1 --parse
```

Запустите:

```bash
bench --site purchase-lifecycle-acceptance.localhost \
  run-tests --app purchase_lifecycle_training
```

Tests не должны создавать missing Workflow/Role как fallback. Поэтому зелёный результат на чистом Site одновременно проверяет, что S08 delivery действительно сработал.

## 8. Пройти один реальный Desk scenario

Tests не заменяют пользовательскую проверку интерфейса.

На acceptance Site создайте Site-local пользователей:

```text
requester@example.test → PLT Requester
approver@example.test  → PLT Approver
senior@example.test    → PLT Senior Approver
```

Затем пройдите минимум два маршрута.

### Маленькая заявка

```text
Requester creates 500
→ PLT Submit for Review
→ Approver Approve
→ PLT Approved / docstatus 1
```

### Большая заявка

```text
Requester creates 1500
→ PLT Submit for Review
→ Approver Approve
→ PLT Pending Senior
→ Senior Approve
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
Cancelled original
→ Amend
→ new PLT Draft / docstatus 0
→ amended_from = original
```

## 9. Что считается провалом

Чистая установка не пройдена, если после `install-app` требуется вручную:

```text
создать PLT Role
создать Workflow State
создать Workflow Action Master
создать Workflow
добавить workflow_state Custom Field
добавить amended_from
восстановить default DocPerm
править database SQL
```

Также провал, если App работает только на dev Site благодаря случайным локальным настройкам, отсутствующим в source.

## 10. Что эта проверка не доказывает

S10 — acceptance приложения на чистом Site, а не production deployment.

Здесь не проверяются:

```text
reverse proxy
TLS
backup/restore
HA
CI/CD
отдельный production server
```

Это другие эксплуатационные ответственности.

## Финальный результат

После S10 ученик должен уметь объяснить весь путь одним предложением:

> Мы начали с обычного `Document` и `status`, добавили `Workflow` только для политики переходов, подключили `docstatus` только когда approval стал зафиксированным фактом, использовали штатные Cancel/Amend и затем доказали, что весь обязательный lifecycle воспроизводится из App на чистом Site.

Практикум завершён.
