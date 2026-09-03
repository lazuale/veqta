# S03. Превратить status в базовый Workflow

S02 показал конкретную проблему: обычный `Write` позволяет пользователю записать любое значение обычного `status`, а нам теперь нужен управляемый маршрут.

Требование изменилось:

```text
Requester:
PLT Draft → PLT Pending Approval

Approver:
PLT Pending Approval → PLT Approved
PLT Pending Approval → PLT Rejected

Requester:
PLT Rejected → PLT Pending Approval
```

Это уже штатная ответственность `Workflow`.

---

# 1. Не создавать второе поле состояния

У нас уже есть поле Standard DocType:

```text
status : Select
```

Оно и станет:

```text
Workflow State Field = status
```

Не создавайте отдельный:

```text
workflow_state
```

Frappe умеет автоматически создать Custom Field, если указанного Workflow State Field нет в Meta. В нашем случае поле уже существует, поэтому второй источник состояния не нужен.

Источник: [`Workflow.create_custom_field_for_workflow_state()` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

---

# 2. Не копировать состояние процесса при Duplicate

Откройте Standard DocType `Purchase Request`, найдите поле `status` и включите:

```text
No Copy : yes
```

Оставьте:

```text
Allow on Submit : no
```

`No Copy` нужен потому, что обычная копия Purchase Request не должна наследовать состояние процесса исходного документа.

`Allow on Submit` сейчас не нужен: все состояния Workflow на S03 имеют `docstatus = 0`.

---

# 3. Создать Workflow State

Через Desk откройте `Workflow State` и создайте:

```text
PLT Draft
PLT Pending Approval
PLT Rejected
PLT Approved
```

Префикс `PLT` нужен потому, что `Workflow State` — отдельные записи настройки Site. Их имена не изолируются автоматически именем Python package.

Style и icon для практикума не важны.

---

# 4. Создать собственное действие отправки

Frappe уже создаёт базовые `Workflow Action Master`:

```text
Approve
Reject
Review
```

Это стандартные записи Framework, их не нужно дублировать под своими именами.

Для действия заявителя создайте новый `Workflow Action Master`:

```text
PLT Submit for Review
```

Стандартные `Approve` и `Reject` используем как есть.

Frappe устанавливает базовые Action Masters при setup; см. [`frappe/utils/install.py`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/install.py).

---

# 5. Создать Workflow

Откройте `Workflow` и создайте:

```text
Workflow Name        : PLT Purchase Request Approval
Document Type        : Purchase Request
Is Active            : yes
Workflow State Field : status
Send Email Alert     : no
```

Email не является условием существования самого Workflow или серверного перехода.

---

# 6. Добавить состояния

На S03 все состояния соответствуют `docstatus = 0`:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| `PLT Draft` | 0 | `PLT Requester` |
| `PLT Pending Approval` | 0 | `PLT Approver` |
| `PLT Rejected` | 0 | `PLT Requester` |
| `PLT Approved` | 0 | `PLT Approver` |

Порядок важен: если у нового Document Workflow State ещё не установлен, `validate_workflow()` использует первую строку `states` как начальное состояние. Поэтому `PLT Draft` должен быть первой строкой Workflow.

Источник: [`validate_workflow()` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

На этом этапе `PLT Approved` ещё не переводит Document в Submitted:

```text
status    = PLT Approved
docstatus = 0
```

Требования фиксировать окончательное согласование через Submit пока нет.

`Only Allow Edit For` задаёт, какая роль может редактировать Document в конкретном состоянии Workflow. Не используйте эту настройку как доказательство отдельной универсальной серверной защиты всех полей.

---

# 7. Добавить переходы

## Draft → Pending Approval

```text
State               : PLT Draft
Action              : PLT Submit for Review
Next State          : PLT Pending Approval
Allowed             : PLT Requester
Allow Self Approval : yes
Condition           : пусто
```

`yes` здесь обязателен по смыслу: owner должен уметь отправить собственную заявку.

## Pending Approval → Approved

```text
State               : PLT Pending Approval
Action              : Approve
Next State          : PLT Approved
Allowed             : PLT Approver
Allow Self Approval : yes
Condition           : пусто
```

На S03 self approval ещё не запрещён отдельным требованием. Мы намеренно оставляем его разрешённым, чтобы на S04 добавить новое правило отдельно.

## Pending Approval → Rejected

```text
State               : PLT Pending Approval
Action              : Reject
Next State          : PLT Rejected
Allowed             : PLT Approver
Allow Self Approval : yes
Condition           : пусто
```

## Rejected → Pending Approval

```text
State               : PLT Rejected
Action              : PLT Submit for Review
Next State          : PLT Pending Approval
Allowed             : PLT Requester
Allow Self Approval : yes
Condition           : пусто
```

Сохраните Workflow.

---

# 8. Проверить нормальный маршрут

Создайте новую заявку под `requester@example.test`:

```text
Subject          : Whiteboard
Requested Amount : 300
Needed By        : будущая дата
```

После сохранения ожидается:

```text
status    = PLT Draft
docstatus = 0
```

Выполните `PLT Submit for Review`.

Ожидается:

```text
status    = PLT Pending Approval
docstatus = 0
```

Переключитесь на `approver@example.test` и выполните `Reject`.

Ожидается:

```text
status    = PLT Rejected
docstatus = 0
```

Вернитесь под Requester, исправьте заявку и снова выполните `PLT Submit for Review`.

После повторной отправки Approver выполните `Approve`.

Ожидается:

```text
status    = PLT Approved
docstatus = 0
```

---

# 9. Проверить запрет прямого перехода

Создайте ещё одну Draft-заявку под Requester и через Bench Console попробуйте сразу записать `PLT Approved`:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
frappe.set_user("requester@example.test")
name = frappe.get_all(
    "Purchase Request",
    filters={"status": "PLT Draft"},
    pluck="name",
    limit=1,
)[0]

doc = frappe.get_doc("Purchase Request", name)
doc.status = "PLT Approved"
doc.save()
```

С активным Workflow такой прямой переход не должен считаться допустимым переходом Workflow. Frappe проверяет изменение состояния относительно доступных transitions.

Источник: [`validate_workflow()` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

После проверки верните пользователя:

```python
frappe.set_user("Administrator")
exit()
```

---

# 10. Посмотреть Workflow Action

Когда заявка находится в `PLT Pending Approval`, откройте Desk под Approver и посмотрите ожидающие Workflow Actions.

Нужно увидеть практический смысл:

```text
Workflow Transition
→ задаёт допустимое действие

Workflow Action
→ показывает ожидающую работу
```

Это разные части механизма. На следующем этапе пользователь будет иметь подходящую роль, но серверная проверка `Allow Self Approval` всё равно запретит одобрение собственной заявки.

---

# Результат

После S03:

```text
status остаётся одним полем Standard DocType
Workflow State Field = status
No Copy = yes
Allow on Submit = no
есть Draft / Pending Approval / Rejected / Approved
Rejected можно исправить и отправить повторно
Approved пока остаётся docstatus 0
Workflow Action показывает ожидающее действие
```

Следующий этап: [`S04_SELF_APPROVAL.md`](S04_SELF_APPROVAL.md).
