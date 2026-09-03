# S04. Запретить одобрение собственной заявки

После S03 пользователь с ролью `PLT Approver` может выполнить переход `PLT Pending Approval → PLT Approved`.

Теперь появляется отдельное правило:

> Если пользователь сам создал заявку, он не должен одобрять её даже при наличии роли согласующего.

В нашей учебной модели заявитель совпадает с `Document.owner`, поэтому это правило уже умеет выражать сам Workflow.

## 1. Создать пользователя с двумя ролями

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

Поскольку у пользователя есть роль `PLT Approver`, без дополнительного правила он может попытаться выполнить `Approve`.

## 3. Запретить self approval для Approve

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

Новое требование запрещает именно одобрение собственной заявки. Не нужно автоматически распространять его на отправку своей заявки или Reject.

## 4. Проверить настоящий переход Workflow

Оставаясь под `dual@example.test`, попробуйте выполнить `Approve`.

Переход должен быть отклонён.

Это не только ограничение интерфейса. В Frappe v16.33.0 `apply_workflow()` после выбора transition вызывает `has_approval_access()`, где при `allow_self_approval = 0` сравниваются текущий пользователь и `doc.owner`.

Источник:

- [`apply_workflow()` и `has_approval_access()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

Логика Framework по смыслу:

```text
Administrator
или allow_self_approval = true
или current user != doc.owner
→ переход разрешён проверкой self approval
```

Поэтому правило `requester = owner`, принятое на S01, здесь становится важной частью модели.

## 5. Проверить одобрение другим пользователем

Войдите как:

```text
approver@example.test
```

Откройте ту же заявку и выполните `Approve`.

Ожидается:

```text
status = PLT Approved
```

На S04 Document всё ещё остаётся:

```text
docstatus = 0
```

Запрет self approval и Submit — разные правила.

## 6. Проверить через Bench Console

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

Текущая проверка self approval сравнивает пользователя именно с `doc.owner`.

Поэтому она подходит нашему учебному сценарию только при принятом правиле:

```text
requester = owner
```

Если позже секретарь сможет создать заявку за другого сотрудника, то:

```text
requester != owner
```

и требование придётся анализировать заново. Не нужно заранее писать собственный validator для сценария, которого пока нет.

## Результат

После S04:

```text
обычные Role и DocPerm сохраняются
Approve имеет Allow Self Approval = no
owner с ролью Approver не может одобрить свой Document
другой Approver может выполнить Approve
отправка своей заявки и Reject остаются разрешёнными
```

Следующий этап: [`S05_CONDITIONAL_APPROVAL.md`](S05_CONDITIONAL_APPROVAL.md).
