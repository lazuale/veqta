# S05. Добавить второй уровень согласования по сумме

До этого все заявки проходили одинаковый маршрут. Теперь появляется новое требование:

```text
requested_amount <= 1000
→ достаточно PLT Approver

requested_amount > 1000
→ после PLT Approver нужен PLT Senior Approver
```

Это первая условная ветка Workflow.

## 1. Не создавать собственную систему согласования

Требование пока очень простое:

```text
одно числовое условие
→ два предсказуемых маршрута
```

Поэтому сначала используем штатный `Workflow Transition.condition`.

Не создавайте:

```text
Approval Matrix DocType
Approval Rule DocType
Python router
Settings для лимита
```

Значение `1000` является частью текущего учебного требования. Настраиваемым параметром оно станет только после отдельного требования администратора менять лимит без редактирования Workflow.

## 2. Добавить роль второго согласующего

Через Desk создайте:

```text
PLT Senior Approver
```

Откройте Standard DocType `Purchase Request` и добавьте permission row:

```text
Read    yes
Create  no
Write   yes
Delete  no
Submit  no
Cancel  no
Amend   no
```

`Write` сейчас нужен потому, что до S06 все состояния остаются с `docstatus = 0`, а окончательный переход заканчивается обычным Save.

## 3. Добавить новое состояние в status

В поле `status` добавьте option:

```text
PLT Pending Senior
```

Порядок options на этом этапе:

```text
PLT Draft
PLT Pending Approval
PLT Rejected
PLT Pending Senior
PLT Approved
```

Создайте отдельный `Workflow State`:

```text
PLT Pending Senior
```

## 4. Добавить состояние в Workflow

В `PLT Purchase Request Approval` добавьте:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| `PLT Pending Senior` | 0 | `PLT Senior Approver` |

Все остальные состояния пока остаются с прежним `docstatus = 0`.

## 5. Разделить Approve на две ветки

Существующий переход:

```text
PLT Pending Approval
→ Approve
→ PLT Approved
```

получает condition:

```python
doc.requested_amount <= 1000
```

И сохраняет:

```text
Allowed             : PLT Approver
Allow Self Approval : no
```

Добавьте второй переход с тем же action:

```text
State               : PLT Pending Approval
Action              : Approve
Next State          : PLT Pending Senior
Allowed             : PLT Approver
Allow Self Approval : no
Condition           : doc.requested_amount > 1000
```

Условия специально не пересекаются:

```text
<= 1000
> 1000
```

Для конкретной суммы должен оставаться ровно один подходящий переход `Approve`.

## 6. Добавить окончательное согласование Senior

Добавьте:

```text
State               : PLT Pending Senior
Action              : Approve
Next State          : PLT Approved
Allowed             : PLT Senior Approver
Allow Self Approval : no
Condition           : пусто
```

Self approval запрещён сразу. Второй уровень согласования не должен случайно получить более слабое правило, чем первый.

## 7. Создать пользователя для проверки

Через Desk создайте, например:

```text
senior@example.test
```

Назначьте:

```text
PLT Senior Approver
```

Для отдельной проверки self approval можно также добавить `PLT Senior Approver` пользователю `dual@example.test`.

## 8. Проверить малую заявку

Под Requester создайте:

```text
Subject          : Office chair
Requested Amount : 500
```

Маршрут:

```text
PLT Draft
→ PLT Pending Approval
→ Approve by PLT Approver
→ PLT Approved
```

`PLT Pending Senior` появляться не должен.

На этом этапе результат всё ещё:

```text
docstatus = 0
```

## 9. Проверить большую заявку

Создайте:

```text
Subject          : Team laptop
Requested Amount : 1500
```

Маршрут:

```text
PLT Draft
→ PLT Pending Approval
→ Approve by PLT Approver
→ PLT Pending Senior
→ Approve by PLT Senior Approver
→ PLT Approved
```

До действия Senior заявка не должна попадать в `PLT Approved`.

## 10. Проверить границу лимита

Создайте две заявки:

```text
1000
1000.01
```

Ожидается:

```text
1000    → PLT Approved
1000.01 → PLT Pending Senior
```

Это полезнее проверки только на `500` и `1500`: так мы проверяем точную границу условия.

## 11. Проверить self approval на втором уровне

Если `dual@example.test` имеет все три роли, создайте большую заявку именно этим пользователем.

Другой `PLT Approver` должен перевести её до:

```text
PLT Pending Senior
```

После этого `dual@example.test` не должен суметь выполнить `Approve`, потому что он остаётся owner исходного Document и переход Senior имеет:

```text
Allow Self Approval = no
```

## Результат

После S05:

```text
PLT Senior Approver появился только из реального требования
PLT Pending Senior появился только из реального маршрута
<= 1000 и > 1000 используют разные переходы
оба перехода Approve запрещают self approval
Approved пока остаётся docstatus 0
```

Следующий этап: [`S06_SUBMITTABLE.md`](S06_SUBMITTABLE.md).
