# S07A. Добавить официальный Cancel path

После S06 окончательное согласование стало Submitted fact:

```text
PLT Approved
docstatus = 1
```

Теперь появляется отдельное требование:

> Уже согласованную заявку иногда нужно официально отменить, сохранив сам факт её существования.

Для этого Frappe уже имеет системную операцию Cancel и `docstatus = 2`.

## 1. Добавить Cancelled в status

В Standard field `status` добавьте option:

```text
PLT Cancelled
```

Финальный набор values теперь:

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

## 2. Создать отдельное действие Cancel

Создайте `Workflow Action Master`:

```text
PLT Cancel Request
```

Мы не переиспользуем `Reject`: отклонение draft-заявки и отмена уже Submitted fact имеют разную семантику.

## 3. Добавить Cancelled state в Workflow

В `PLT Purchase Request Approval` добавьте:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| `PLT Cancelled` | 2 | `PLT Approver` |

`Only Allow Edit For` является обязательным полем state row. Для `docstatus = 2` оно не превращает отменённый Document обратно в редактируемый факт и не выдаёт право Amend. Право Amend появится отдельно на S07B.

## 4. Добавить transition Approved → Cancelled

```text
State               : PLT Approved
Action              : PLT Cancel Request
Next State          : PLT Cancelled
Allowed             : PLT Approver
Allow Self Approval : yes
Condition           : пусто
```

Почему здесь `Allow Self Approval = yes`: текущая бизнес-политика запрещает self **approval**, но не требует отдельного независимого canceller. Мы не переносим правило одного действия на другое без требования.

## 5. Выдать отдельный Cancel permission

В Standard DocPerm:

```text
PLT Requester        Cancel no
PLT Approver         Cancel yes
PLT Senior Approver  Cancel no
```

Senior умеет final approve большие заявки, но из этого не следует право отменять любые Submitted Purchase Requests.

## 6. Проверить реальный cancel transition

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

## 7. Почему status.Allow on Submit всё ещё не нужен

Оставьте:

```text
status.Allow on Submit = no
```

`Approved → Cancelled` — не обычное редактирование уже Submitted документа. Это системный Cancel path с переходом `docstatus 1 → 2`.

Автоматически создаваемый Frappe workflow Custom Field действительно получает `allow_on_submit = 1`, но это универсальный fallback для поля, которого не было в Meta. Наш Standard `status` уже существует, и мы включаем только свойства, которые нужны конкретному контракту.

Источник: [`Workflow.create_custom_field_for_workflow_state()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

## 8. Проверить отрицательные случаи

Под Requester не должно быть права Cancel.

Под Senior не должно быть права Cancel.

Draft-заявка не должна переходить прямо в Cancelled: Workflow Frappe не допускает `docstatus 0 → 2`.

Источник: [`Workflow.validate_docstatus()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

## Результат

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
