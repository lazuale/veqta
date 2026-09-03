# S07A. Добавить штатную отмену через Cancel

После S06 окончательно согласованная заявка становится Submitted Document:

```text
PLT Approved
docstatus = 1
```

Теперь появляется отдельное требование:

> Уже согласованную заявку иногда нужно официально отменить, сохранив сам факт её существования.

Для этого Frappe уже имеет системную операцию Cancel и `docstatus = 2`.

---

# 1. Добавить Cancelled в status

В поле `status` добавьте option:

```text
PLT Cancelled
```

Итоговый набор значений теперь:

```text
PLT Draft
PLT Pending Approval
PLT Rejected
PLT Pending Senior
PLT Approved
PLT Cancelled
```

Создайте `Workflow State`:

```text
PLT Cancelled
```

---

# 2. Создать отдельное действие Cancel

Создайте `Workflow Action Master`:

```text
PLT Cancel Request
```

Мы не переиспользуем `Reject`: отклонение Draft-заявки и отмена уже Submitted Document имеют разный смысл.

---

# 3. Добавить состояние Cancelled в Workflow

В `PLT Purchase Request Approval` добавьте:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| `PLT Cancelled` | 2 | `PLT Approver` |

`Only Allow Edit For` является обязательным полем строки состояния Workflow. Для `docstatus = 2` оно не делает отменённый Document снова редактируемым и не выдаёт право Amend. Право Amend появится отдельно на S07B.

---

# 4. Добавить переход Approved → Cancelled

```text
State               : PLT Approved
Action              : PLT Cancel Request
Next State          : PLT Cancelled
Allowed             : PLT Approver
Allow Self Approval : yes
Condition           : пусто
```

Здесь `Allow Self Approval = yes`, потому что текущее правило запрещает одобрять собственную заявку, но не запрещает отменять её после согласования. Не переносим ограничение одного действия на другое без отдельного требования.

---

# 5. Выдать отдельный Cancel permission

В Standard DocPerm:

```text
PLT Requester        Cancel no
PLT Approver         Cancel yes
PLT Senior Approver  Cancel no
```

Senior может окончательно согласовать большую заявку, но из этого не следует право отменять любые Submitted Purchase Requests.

---

# 6. Проверить настоящий Cancel

Возьмите любую Submitted заявку:

```text
status    = PLT Approved
docstatus = 1
```

Войдите как `approver@example.test` и выполните:

```text
PLT Cancel Request
```

Ожидается:

```text
status    = PLT Cancelled
docstatus = 2
```

В v16.33.0 `apply_workflow()` для перехода:

```text
current docstatus = 1
next docstatus    = 2
```

вызывает `doc.cancel()`.

Источник: [`apply_workflow()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

---

# 7. Почему status.Allow on Submit всё ещё не нужен

Оставьте:

```text
status.Allow on Submit = no
```

`Approved → Cancelled` — не обычное редактирование Submitted Document. Это системный Cancel с переходом `docstatus 1 → 2`.

Автоматически создаваемый Frappe workflow Custom Field действительно получает `allow_on_submit = 1`, но это общее поведение для поля, которого не было в Meta. Наш Standard `status` уже существует, и мы включаем только свойства, которые нужны текущему требованию.

Источник: [`Workflow.create_custom_field_for_workflow_state()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

---

# 8. Проверить отрицательные случаи

Под Requester не должно быть права Cancel.

Под Senior не должно быть права Cancel.

Draft-заявка не должна переходить прямо в Cancelled: Workflow Frappe не допускает `docstatus 0 → 2`.

Источник: [`Workflow.validate_docstatus()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

---

# Результат

После S07A:

```text
PLT Approved  = docstatus 1
PLT Cancelled = docstatus 2
Cancel выполняет только PLT Approver
Reject и Cancel остаются разными действиями
status.Allow on Submit остаётся no
Amend ещё никому не выдан
```

Следующий этап: [`S07B_AMEND.md`](S07B_AMEND.md).
