# 25. `Status` против `Workflow State`

До этой главы у `Request` уже есть обычное поле:

```text
Status
Open / In Progress / Done
```

В следующей главе мы добавим настоящий Workflow. Перед этим нужно чётко развести три разных состояния документа.

Проверено для **Frappe Framework v16.32.0**.

---

# 1. Обычный `Status`

Поле:

```text
status
```

в нашем `Request` — обычный `Select`.

Framework хранит выбранное значение:

```text
Open
In Progress
Done
```

Если permissions разрешают редактирование, пользователь может поменять:

```text
Open → Done
```

и сохранить документ напрямую.

Само наличие списка вариантов не создаёт процесс согласования.

---

# 2. Почему Select не является Workflow

Для настоящего процесса обычно нужны правила вида:

```text
из какого состояния можно перейти
какое действие пользователь нажимает
в какое состояние попадёт документ
какая Role может выполнить действие
при каком условии действие доступно
```

У обычного `Select` этого нет.

Он отвечает только на вопрос:

```text
какое значение сейчас хранится в поле
```

Поэтому обычный `Status` хорошо подходит для прикладного состояния работы, если строгий граф переходов не нужен.

---

# 3. `Workflow State`

Настоящий Workflow хранит своё текущее состояние в отдельном поле.

По умолчанию его fieldname:

```text
workflow_state
```

Например:

```text
Draft
Review
Approved
Rejected
```

Но это значение уже меняется не обычным выбором из Select, а через разрешённые Workflow Actions.

---

# 4. Поле `workflow_state` не нужно создавать заранее

В `Workflow` есть настройка:

```text
Workflow State Field = workflow_state
```

Если такого поля в целевом DocType ещё нет, Frappe v16 сам создаёт скрытый `Custom Field` типа:

```text
Link → Workflow State
```

Поэтому в лабораторной 26 мы не будем вручную добавлять `workflow_state` в Standard metadata `Request`.

Workflow создаст нужное поле сам.

---

# 5. `docstatus` — третья отдельная вещь

У каждого Document есть системный:

```text
docstatus
```

Его значения фиксированы:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Это технический lifecycle документа, который мы уже изучали в главе 10.

Наш `Request` не Submittable, поэтому в блоке E он останется:

```text
docstatus = 0
```

даже когда Workflow State станет:

```text
Approved
```

---

# 6. У одного Request могут одновременно быть разные значения

После следующей главы нормальна такая комбинация:

```text
status         = Done
workflow_state = Approved
docstatus      = 0
```

Здесь нет конфликта, если смысл полей разный.

В нашем учебном процессе:

```text
status
→ обычное рабочее состояние Request

workflow_state
→ состояние согласования

docstatus
→ системный lifecycle Framework
```

---

# 7. ToDo.status — ещё одно независимое состояние

После глав 23–24 существуют связанные `ToDo`.

У них своё поле:

```text
ToDo.status
Open / Closed / Cancelled
```

Поэтому на одном экране могут существовать сразу четыре значения:

```text
Request.status
Request.workflow_state
Request.docstatus
ToDo.status
```

Они отвечают на разные вопросы.

---

# 8. Что изменится после включения Workflow

До Workflow пользователь может сделать обычному `Status`:

```text
Open → Done
```

прямо в поле.

После создания Workflow для состояния согласования пользователь будет выбирать действия вроде:

```text
Send for Review
Approve
Reject
Reopen
```

И уже действие будет переводить:

```text
Draft → Review → Approved / Rejected
```

Это главное визуальное отличие, которое мы проверим руками.

---

# 9. Не нужно дублировать один смысл двумя полями

Плохой вариант:

```text
status:
Draft / Review / Approved / Rejected

workflow_state:
Draft / Review / Approved / Rejected
```

если оба поля означают одно и то же.

Тогда легко получить противоречие:

```text
status = Review
workflow_state = Approved
```

В нашем курсе значения специально разные:

```text
Status:
Open / In Progress / Done

Workflow State:
Draft / Review / Approved / Rejected
```

Так видно, что это две разные оси.

---

# 10. Что сделаем в лабораторной

До создания Workflow мы возьмём обычный Request и намеренно совершим «плохой процессный переход»:

```text
Status: Open → Done
```

одним сохранением.

Framework разрешит его, потому что `Status` — обычный Select и никакого Workflow для него нет.

После этого вернём:

```text
Status = Open
```

и только в следующей главе создадим реальный граф согласования.

---

## Что запомнить

1. `status` — обычное поле нашего DocType.
2. `workflow_state` — состояние активного Workflow.
3. `docstatus` — системные 0/1/2.
4. `ToDo.status` относится к Assignment, а не к Request.
5. Список вариантов Select не создаёт разрешённые переходы.
6. Frappe может сам создать `workflow_state` при сохранении Workflow.
7. В нашем курсе Workflow и обычный Status будут иметь разный смысл.

Теперь выполни [**лабораторную 25**](labs/25_STATUS_VS_WORKFLOW_STATE_LAB.md).