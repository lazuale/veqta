# S04. Запретить self approval штатной политикой Workflow

После S03 пользователь с ролью `PLT Approver` может выполнить переход `PLT Pending Approval → PLT Approved`.

Теперь появляется отдельное правило:

> Если пользователь сам создал заявку, он не должен одобрять её даже при наличии роли согласующего.

В нашей учебной модели заявитель совпадает с `Document.owner`, поэтому это правило уже умеет выражать сам Workflow.

## 1. Создать dual-role пользователя

Через Desk создайте пользователя, например:

```text
dual@example.test
```

Назначьте ему обе роли:

```text
PLT Requester
PLT Approver
```

## 2. Создать заявку именно этим пользователем

Войдите как `dual@example.test` и создайте новую заявку:

```text
Subject          : Dual-role request
Requested Amount : 400
Needed By        : будущая дата
```

Сохраните и выполните:

```text
PLT Submit for Review
```

Теперь:

```text
owner  = dual@example.test
status = PLT Pending Approval
```

Поскольку у пользователя есть роль `PLT Approver`, без дополнительной policy он является кандидатом на `Approve`.

## 3. Изменить только positive approval transition

Откройте Workflow `PLT Purchase Request Approval`.

Для перехода:

```text
PLT Pending Approval
→ Approve
→ PLT Approved
```

установите:

```text
Allow Self Approval : no
```

Остальные transitions не меняйте:

```text
Draft → Submit for Review        self yes
Pending Approval → Reject       self yes
Rejected → Submit for Review    self yes
```

Почему: новое требование запрещает именно одобрение собственной заявки. Мы не расширяем его автоматически на отправку своей заявки или отрицательное решение.

## 4. Проверить через реальный Workflow path

Оставаясь под `dual@example.test`, попробуйте выполнить `Approve`.

Переход должен быть отклонён.

Это не UI-фильтр. В Frappe v16.33.0 `apply_workflow()` после выбора transition вызывает `has_approval_access()`, где при `allow_self_approval = 0` сравниваются текущий пользователь и `doc.owner`.

Источник:

- [`apply_workflow()` и `has_approval_access()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

Текущая логика Framework по смыслу:

```text
Administrator
или allow_self_approval = true
или current user != doc.owner
→ transition разрешён по self-policy
```

Поэтому наш выбор `requester = owner` на S01 здесь становится важной частью модели.

## 5. Проверить успешный approval другим пользователем

Войдите как:

```text
approver@example.test
```

Откройте ту же заявку и выполните `Approve`.

Ожидается:

```text
status = PLT Approved
```

На S04 документ всё ещё остаётся:

```text
docstatus = 0
```

Self-approval policy и Submit — разные ответственности.

## 6. Проверить server path напрямую

Для отрицательной проверки можно использовать Bench Console:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
from frappe.model.workflow import apply_workflow

frappe.set_user("dual@example.test")
name = frappe.get_all(
    "Purchase Request",
    filters={"owner": "dual@example.test", "status": "PLT Pending Approval"},
    pluck="name",
    limit=1,
)[0]

doc = frappe.get_doc("Purchase Request", name)
apply_workflow(doc, "Approve")
```

Ожидается ошибка self approval.

После проверки:

```python
frappe.set_user("Administrator")
exit()
```

## 7. Граница штатного механизма

Текущая self-policy сравнивает пользователя именно с `doc.owner`.

Поэтому она подходит нашему CORE только при принятом правиле:

```text
requester = owner
```

Если позже секретарь сможет создать заявку за другого сотрудника, то:

```text
business requester != owner
```

и это требование придётся анализировать заново. Не нужно заранее писать собственный validator для сценария, которого пока нет.

## Результат

После S04:

```text
обычный role access сохранён
positive approval имеет Allow Self Approval = no
owner с Approver role не может одобрить свой Document
другой Approver может
Requester self-transitions остаются рабочими
```

Следующий этап: [`S05_CONDITIONAL_APPROVAL.md`](S05_CONDITIONAL_APPROVAL.md).
