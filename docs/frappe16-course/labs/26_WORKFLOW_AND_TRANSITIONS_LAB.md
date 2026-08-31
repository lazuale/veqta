# Лабораторная 26. Workflow и переходы

## Что уже должно быть готово

Лабораторная 25 завершена.

Есть обычный Request:

```text
E25-Status-Only
Status = Open
```

`Training Request Round Robin` существует, но:

```text
Disabled = ✓
```

Активного Workflow для `Request` ещё нет.

---

## Что сейчас получим

Останется активный Workflow:

```text
Training Request Workflow
```

Граф:

```text
Draft
  └── Send for Review → Review
                          ├── Approve → Approved
                          └── Reject  → Rejected
                                           └── Reopen → Draft
```

Финальные контрольные Request:

```text
E26-Approved
  workflow_state = Approved
  status = Done

E26-Reject-Reopen
  workflow_state = Draft
  status = Open
```

---

# Часть 1. Создай Workflow States

Работай под `Administrator`.

Открой:

```text
http://learn.localhost:8000/app/workflow-state
```

Создай четыре записи:

```text
Draft
Review
Approved
Rejected
```

Для визуального Style можно использовать:

```text
Draft    → Primary
Review   → Warning
Approved → Success
Rejected → Danger
```

Сохрани каждую запись.

---

# Часть 2. Создай Workflow Actions

Открой:

```text
http://learn.localhost:8000/app/workflow-action-master
```

Создай четыре действия:

```text
Send for Review
Approve
Reject
Reopen
```

---

# Часть 3. Создай Workflow

Открой:

```text
http://learn.localhost:8000/app/workflow
```

Создай:

```text
Workflow Name:        Training Request Workflow
Document Type:        Request
Is Active:            ✓
Don't Override Status: ☐
Send Email Alert:     ☐
Workflow State Field: workflow_state
```

---

## 1. Document States

Добавь строки строго в таком порядке:

| № | State | Doc Status | Only Allow Edit For |
|---:|---|---:|---|
| 1 | Draft | 0 | Training User |
| 2 | Review | 0 | Training Manager |
| 3 | Approved | 0 | Training Manager |
| 4 | Rejected | 0 | Training User |

Не заполняй:

```text
Update Field
Update Value
```

Во всех строках оставь:

```text
Doc Status = 0
```

---

## 2. Transitions

Добавь четыре строки:

### Строка 1

```text
State:      Draft
Action:     Send for Review
Next State: Review
Allowed:    Training User
Allow Self Approval: ✓
Condition:  doc.due_date
```

### Строка 2

```text
State:      Review
Action:     Approve
Next State: Approved
Allowed:    Training Manager
Allow Self Approval: ✓
Condition:  пусто
```

### Строка 3

```text
State:      Review
Action:     Reject
Next State: Rejected
Allowed:    Training Manager
Allow Self Approval: ✓
Condition:  пусто
```

### Строка 4

```text
State:      Rejected
Action:     Reopen
Next State: Draft
Allowed:    Training User
Allow Self Approval: ✓
Condition:  пусто
```

Сохрани Workflow.

Ожидается сообщение о создании Custom Field:

```text
workflow_state
```

для `Request`.

---

# Часть 4. Проверь созданное поле

Открой `Customize Form` для:

```text
Request
```

Найди:

```text
Workflow State
fieldname: workflow_state
Field Type: Link
Options: Workflow State
Hidden: ✓
```

Не меняй это поле вручную.

Закрой Customize Form без изменений.

---

# Намеренная поломка — отправка без Due Date

Войди:

```text
student.user@example.test
FrappeCourse!2026
```

Создай Request:

```text
Subject:  E26-Approved
Status:   Open
Priority: Medium
Area:     North
Due Date: пусто
Notes:    Workflow condition probe
```

Сохрани.

После Save документ должен находиться в:

```text
Workflow State = Draft
```

Проверь доступные Workflow Actions.

Ожидается:

```text
Send for Review отсутствует
```

Причина:

```python
doc.due_date
```

возвращает пустое значение.

---

# Восстановление условия

Заполни:

```text
Due Date = 2026-09-05
```

Сохрани.

Теперь действие:

```text
Send for Review
```

должно стать доступно.

Выполни его.

Ожидается:

```text
Workflow State = Review
```

---

# Часть 5. Проверь границу Training User

Оставаясь под:

```text
student.user@example.test
```

посмотри Workflow Actions на `E26-Approved`.

Ожидается, что действий:

```text
Approve
Reject
```

нет.

Они разрешены только роли:

```text
Training Manager
```

---

# Часть 6. Approve менеджером

Полностью войди:

```text
student.manager@example.test
FrappeCourse!2026
```

Открой:

```text
E26-Approved
```

Ожидаются действия:

```text
Approve
Reject
```

Выбери:

```text
Approve
```

После перехода:

```text
Workflow State = Approved
```

При этом обычный Status должен остаться:

```text
Open
```

потому что мы не настроили `Update Field`.

---

# Эксперимент — Status и Workflow State независимы

На том же Approved Request установи:

```text
Status = Done
```

Сохрани.

Ожидается:

```text
Status         = Done
Workflow State = Approved
```

То есть изменение обычного бизнес-поля не откатило Workflow.

---

# Часть 7. Пройди ветку Reject → Reopen

Войди обычным User.

Создай второй Request:

```text
Subject:  E26-Reject-Reopen
Status:   Open
Priority: Medium
Area:     North
Due Date: 2026-09-06
Notes:    Reject and reopen example
```

Сохрани.

Ожидается:

```text
Workflow State = Draft
```

Выполни:

```text
Send for Review
```

Получаем:

```text
Workflow State = Review
```

---

## Reject менеджером

Войди менеджером и открой тот же Request.

Выполни:

```text
Reject
```

Ожидается:

```text
Workflow State = Rejected
```

---

## Reopen обычным User

Снова войди:

```text
student.user@example.test
```

Открой:

```text
E26-Reject-Reopen
```

Должно быть доступно действие:

```text
Reopen
```

Выполни его.

Ожидается:

```text
Workflow State = Draft
Status         = Open
```

---

# Часть 8. Финальная проверка Workflow

Под `Administrator` открой:

```text
Training Request Workflow
```

Проверь:

```text
Is Active = ✓
```

States идут в порядке:

```text
Draft
Review
Approved
Rejected
```

Transitions:

```text
Draft    --Send for Review--> Review      [Training User, doc.due_date]
Review   --Approve---------> Approved    [Training Manager]
Review   --Reject----------> Rejected    [Training Manager]
Rejected --Reopen----------> Draft       [Training User]
```

---

## Проверка себя

1. Почему `workflow_state` не создавали вручную?
2. Какой State должен быть первым?
3. Почему без Due Date не было `Send for Review`?
4. Почему обычный User не получил Approve?
5. Какая Role выполняет Reject?
6. Кто выполняет Reopen?
7. Изменился ли `docstatus` при Approved?
8. Почему `Status = Done` и `Workflow State = Approved` могут существовать одновременно?
9. Есть ли переход из Approved обратно?

---

## Состояние стенда после лабораторной

Активен:

```text
Training Request Workflow
```

Workflow State Field:

```text
workflow_state
Link → Workflow State
Custom Field
Hidden = ✓
```

Граф:

```text
Draft
→ Review
→ Approved
→ Rejected
→ Reopen to Draft
```

Контрольные документы:

```text
E26-Approved
  Status: Done
  Workflow State: Approved
  Area: North
  Due Date: 2026-09-05

E26-Reject-Reopen
  Status: Open
  Workflow State: Draft
  Area: North
  Due Date: 2026-09-06
```

Assignment Rule остаётся Disabled.

Это точное входное состояние [**главы 27**](../27_NOTIFICATION.md).