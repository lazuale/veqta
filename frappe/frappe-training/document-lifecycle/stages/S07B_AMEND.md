# S07B. Создать новую версию отменённой заявки через Amend

После S07A отменённая заявка сохраняется как исторический факт:

```text
PLT Cancelled
docstatus = 2
```

Теперь появляется новое требование:

> Заявитель должен уметь создать новую версию отменённой заявки, не переписывая исходный Document.

Для этого используется штатный Amend Frappe.

---

# 1. Выдать отдельный Amend permission

В Standard DocPerm `Purchase Request` измените только Amend:

```text
PLT Requester        Amend yes
PLT Approver         Amend no
PLT Senior Approver  Amend no
```

У `PLT Requester` уже есть:

```text
Create yes
```

Это соответствует смыслу Amend: создаётся новый Document, а не редактируется отменённый.

---

# 2. Не создавать amended_from вручную

После включения `Is Submittable` Frappe уже добавил поле:

```text
amended_from
```

Никакой отдельный Custom Field для ссылки на исходную версию не нужен.

Проверьте Meta через console:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
field = frappe.get_meta("Purchase Request").get_field("amended_from")
print(field.fieldname, field.fieldtype, field.options, field.read_only, field.no_copy)
exit()
```

Ожидаемый смысл:

```text
amended_from
Link → Purchase Request
read only
no copy
```

---

# 3. Не связывать Amend с Only Allow Edit For

На S07A `PLT Cancelled` получил `Only Allow Edit For = PLT Approver`, потому что это обязательное поле строки состояния Workflow.

Для появления Amend **не нужно** менять эту настройку на Requester.

Почему:

```text
Only Allow Edit For
→ определяет редактирование Document в текущем состоянии Workflow

Amend permission
→ разрешает создать новый Document из отменённого
```

Это разные обязанности.

В Desk v16.33.0 условие `can_amend()` проверяет `docstatus == 2` и `frm.perm[0].amend`; `Only Allow Edit For` в это условие не входит.

Источник: [`frappe/public/js/frappe/form/toolbar.js` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/toolbar.js).

Поэтому на этом этапе меняется DocPerm `Amend`, а не настройка редактирования состояния Workflow.

---

# 4. Пройти сценарий через Desk

Используйте заявку, которая уже прошла:

```text
PLT Approved  docstatus 1
→ PLT Cancel Request
→ PLT Cancelled docstatus 2
```

Войдите как `requester@example.test` и откройте отменённую заявку.

Выполните штатное действие **Amend**.

Frappe должен создать новый Draft Document.

Проверьте до сохранения:

```text
docstatus = 0
amended_from = name исходной отменённой заявки
```

Workflow для нового Draft должен начать процесс снова с:

```text
PLT Draft
```

Исправьте нужные поля и сохраните новую версию.

---

# 5. Проверить связь версий

Через console:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
rows = frappe.get_all(
    "Purchase Request",
    fields=["name", "status", "docstatus", "amended_from"],
    order_by="creation desc",
    limit=5,
)
for row in rows:
    print(row)
exit()
```

Должна быть видна пара по смыслу:

```text
исходная заявка
status = PLT Cancelled
docstatus = 2
amended_from = пусто

новая версия
status = PLT Draft
docstatus = 0
amended_from = name исходной заявки
```

---

# 6. Повторно отправить новую версию

Новая версия должна снова пройти обычный Workflow:

```text
PLT Draft
→ PLT Pending Approval
→ ...
```

Amend не создаёт отдельный процесс согласования. Он создаёт новый Draft, который снова проходит уже существующий маршрут.

---

# 7. Проверить отрицательные роли

`PLT Approver` и `PLT Senior Approver` не должны получать Amend только потому, что участвуют в согласовании.

Это отдельное право заявителя.

---

# Результат

После S07B полный пользовательский маршрут уже собран:

```text
Draft
→ Pending Approval
→ Rejected → Resubmit
или
→ Pending Senior
→ Approved (docstatus 1)
→ Cancelled (docstatus 2)
→ Amend
→ новый Draft с amended_from
```

Следующий этап: [`S08_APP_STATE_DELIVERY.md`](S08_APP_STATE_DELIVERY.md).
