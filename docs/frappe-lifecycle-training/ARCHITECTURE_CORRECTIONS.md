# Коррекция архитектуры второго практикума: `Allow on Submit` для Workflow State Field

Статус: **обязательная коррекция текущего lifecycle baseline**.

Этот документ исправляет одну формулировку, появившуюся в `ARCHITECTURE_PASSPORT.md`, `REQUIREMENTS_MATRIX.md`, `STAGE_DEPENDENCY_GRAPH.md` и ранней версии `PRACTICUM_ROADMAP.md`.

Нормативные источники — Frappe v16.33.0:

- `frappe/model/workflow.py::apply_workflow()`;
- `frappe/model/document.py::_cancel()` и save lifecycle;
- `frappe/workflow/doctype/workflow/workflow.py::create_custom_field_for_workflow_state()`.

---

# 1. Что было сформулировано слишком широко

Ранее при появлении transition:

```text
PR Approved   → docstatus 1
PR Cancelled  → docstatus 2
```

было записано:

```text
status.Allow on Submit = yes
```

как будто это обязательная техническая предпосылка Workflow cancel-path.

Для текущего CORE это неверно.

---

# 2. Что реально делает Frappe

`apply_workflow()` сначала устанавливает следующее значение Workflow State Field, а затем выбирает системную Document operation по `Doc Status` следующего Workflow State.

Для текущего cancel-path:

```text
current docstatus = 1
next docstatus    = 2
```

Frappe вызывает:

```text
doc.cancel()
```

`Document._cancel()` устанавливает `docstatus = 2` и вызывает обычный save-path с action `cancel`.

В текущем Document lifecycle проверка `validate_update_after_submit()` выполняется для action:

```text
update_after_submit
```

а не для action:

```text
cancel
```

Следовательно, изменение workflow-state field как часть штатного:

```text
Submitted → Cancelled
```

не требует `allow_on_submit = 1` только ради самого cancel transition.

---

# 3. Почему автоматически создаваемый workflow field всё равно имеет `allow_on_submit = 1`

Если Workflow State Field вообще отсутствует в Meta, Frappe создаёт fallback `Custom Field` с универсальными свойствами, среди которых:

```text
allow_on_submit = 1
no_copy = 1
Link → Workflow State
```

Это общий fallback Framework для разных Workflow-конфигураций.

Из этого не следует правило:

> Любой существующий Standard Workflow State Field любого собственного DocType обязан иметь `Allow on Submit`.

Наш App использует уже существующий Standard:

```text
status : Select
```

и должен включать свойства только из реального требования.

---

# 4. Исправленный CORE contract

Во втором практикуме:

```text
status = Standard Select
Workflow State Field = status
```

Для текущего lifecycle:

```text
Draft 0
→ Pending 0
→ Approved 1
→ Cancelled 2
```

`status.Allow on Submit` **не включается**.

Причина:

```text
в CORE нет transition docstatus 1 → 1,
который должен изменять status через обычный update-after-submit path.
```

---

# 5. Когда `Allow on Submit` станет настоящим кандидатом

Механизм пересматривается только после нового требования.

Например:

```text
Submitted state A
→ Submitted state B
```

при котором Workflow должен изменить state field, сохранив:

```text
docstatus = 1
```

или появляется отдельное безопасное поле, которое пользователь действительно должен менять после Submit.

Тогда проводится новый fit analysis:

```text
какое конкретно поле меняется?
почему это допустимо после Submit?
нужен ли именно allow_on_submit?
```

Не включать `Allow on Submit` заранее «потому что Workflow может когда-нибудь понадобиться».

---

# 6. Что считается отменённым

Если в текущих документах второго практикума встречается утверждение:

```text
PR Approved → PR Cancelled
→ поэтому status.Allow on Submit = yes
```

оно считается заменённым этой коррекцией.

Все остальные решения сохраняются:

```text
PR Cancelled появляется только из отдельного Cancel requirement
Purchase Approver получает Cancel
Requester и Senior не получают Cancel
apply_workflow выполняет реальный cancel-path
Cancelled = docstatus 2
```

---

# 7. Архитектурный вывод

Автоматически создаваемая Framework-конфигурация показывает универсальный capability baseline, но не является требованием копировать все её свойства в собственный Standard metadata.

Правило второго практикума:

> `Allow on Submit` появляется только тогда, когда конкретное поле действительно должно изменяться обычным update-after-submit path. Штатный `docstatus 1 → 2` Workflow cancel-path сам по себе такого требования не создаёт.
