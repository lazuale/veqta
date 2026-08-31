# 26. Workflow и переходы

В главе 25 мы доказали, что обычный `Status` можно менять напрямую.

Теперь добавим процесс, где пользователь уже не выбирает состояние вручную. Он выполняет разрешённое **Workflow Action**, а Frappe сам переводит `Request` в следующее `Workflow State`.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть

У `Request` есть обычный:

```text
Status
Open / In Progress / Done
```

Но активного Workflow пока нет.

Роли уже созданы:

```text
Training User
Training Manager
```

`student.manager@example.test` имеет обе роли, а обычный User — только `Training User`.

---

# 1. Канонический Workflow курса

Создадим один процесс:

```text
Draft
  │
  └── Send for Review
          ↓
        Review
        ├── Approve → Approved
        └── Reject  → Rejected
                         │
                         └── Reopen → Draft
```

Роли:

```text
Training User
→ Send for Review
→ Reopen

Training Manager
→ Approve
→ Reject
```

Это состояние согласования. Обычный `Request.status` остаётся отдельным полем.

---

# 2. Почему все состояния будут `Doc Status = 0`

`Request` в нашем курсе не Submittable.

Поэтому не нужно смешивать Workflow с Submit/Cancel.

У всех четырёх состояний зададим:

```text
Doc Status = 0
```

То есть:

```text
workflow_state меняется
но
docstatus остаётся 0
```

Так мы изучаем именно переходы и роли.

---

# 3. Workflow State

Создадим четыре записи системного DocType:

```text
Draft
Review
Approved
Rejected
```

Они являются значениями поля состояния Workflow.

Само поле `workflow_state` заранее в `Request` не добавляем.

Когда сохраним Workflow, v16 увидит, что поля нет, и создаст скрытый Custom Field:

```text
Workflow State
fieldname: workflow_state
Link → Workflow State
Hidden = ✓
Allow on Submit = ✓
No Copy = ✓
```

---

# 4. Workflow Action Master

Отдельно создадим названия действий:

```text
Send for Review
Approve
Reject
Reopen
```

Это не состояния.

Сравнение:

```text
State  = где находится документ
Action = что пользователь делает
```

Например:

```text
State: Draft
Action: Send for Review
Next State: Review
```

---

# 5. Document States

В самом Workflow таблица `Document States` будет такой:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| Draft | 0 | Training User |
| Review | 0 | Training Manager |
| Approved | 0 | Training Manager |
| Rejected | 0 | Training User |

`Only Allow Edit For` не заменяет Role Permission Manager.

Базовый доступ к `Request` уже должен существовать. Workflow дополнительно ограничивает редактирование в конкретном состоянии.

---

# 6. Transitions

Создадим четыре строки:

| State | Action | Next State | Allowed |
|---|---|---|---|
| Draft | Send for Review | Review | Training User |
| Review | Approve | Approved | Training Manager |
| Review | Reject | Rejected | Training Manager |
| Rejected | Reopen | Draft | Training User |

Frappe показывает пользователю только те переходы, для которых одновременно выполняются:

```text
текущий State совпадает
роль пользователя подходит
Condition истинно
```

---

# 7. Condition на отправку в Review

Чтобы увидеть реальную проверку условия, переход:

```text
Draft → Send for Review → Review
```

получит:

```python
doc.due_date
```

Смысл:

```text
Due Date заполнена
→ действие Send for Review доступно

Due Date пустая
→ действие не предлагается
```

Это простое выражение, а не отдельный Python-скрипт.

---

# 8. Первый State действительно важен

При сохранении документа без установленного Workflow State Frappe использует первую строку `Document States`.

Поэтому первой должна быть:

```text
Draft
```

После активации Workflow существующие `Request` без `workflow_state` также получат первое состояние, соответствующее их `docstatus`.

Поскольку у нас все состояния имеют `Doc Status = 0`, первой строкой должен оставаться именно `Draft`.

---

# 9. Что увидит Training User

Новый Request после Save будет иметь:

```text
Workflow State = Draft
```

Если `Due Date` заполнена, обычный User увидит действие:

```text
Send for Review
```

После него:

```text
Workflow State = Review
```

У обычного User нет роли `Training Manager`, поэтому действий:

```text
Approve
Reject
```

у него не будет.

---

# 10. Что увидит Training Manager

На документе в `Review` менеджер имеет нужную роль и получает:

```text
Approve
Reject
```

После `Approve`:

```text
workflow_state = Approved
```

После `Reject`:

```text
workflow_state = Rejected
```

---

# 11. Reopen возвращает только Rejected

Для учебного процесса обратный путь есть только из:

```text
Rejected
```

и выглядит так:

```text
Rejected
→ Reopen
→ Draft
```

`Approved` в этом Workflow является конечным состоянием.

Это осознанное правило, а не случайно забытая стрелка.

---

# 12. Status не синхронизируем автоматически

В `Document States` есть возможности:

```text
Update Field
Update Value
```

Но в обязательной схеме мы их оставим пустыми.

Поэтому переход:

```text
Review → Approved
```

изменит:

```text
workflow_state
```

но не обязан менять:

```text
status
```

После Approval мы отдельно изменим `Status` и увидим, что Workflow State останется прежним.

---

# 13. Почему нельзя просто записать `workflow_state = Approved`

Когда Workflow активен, Frappe проверяет переходы.

Если пользователь пытается перейти из текущего состояния в значение, для которого нет разрешённого Transition, Framework отклоняет изменение как недопустимый Workflow State transition.

Поэтому правильный рабочий путь:

```text
пользователь выбирает Action
→ Frappe находит Transition
→ проверяет Role и Condition
→ устанавливает Next State
→ сохраняет Document
```

---

# 14. Self Approval в нашем первом Workflow

В `Workflow Transition` есть:

```text
Allow Self Approval
```

Для курса оставим его включённым по умолчанию.

Мы сейчас изучаем разделение ролей, а не запрет согласования собственного документа.

Отдельное усложнение self-approval в эту лабораторную не добавляем.

---

# 15. Что останется после лабораторной

Активный Workflow:

```text
Training Request Workflow
```

с четырьмя состояниями и четырьмя переходами.

Будут два контрольных Request:

```text
E26-Approved
→ workflow_state = Approved
→ status = Done

E26-Reject-Reopen
→ workflow_state = Draft
→ status = Open
```

Первый покажет независимость `status` и `workflow_state`, второй — обратную ветку Rejected → Reopen → Draft.

---

## Что запомнить

1. Workflow состоит из состояний, действий и переходов.
2. Первое состояние нашего Workflow — `Draft`.
3. `Training User` отправляет в Review и делает Reopen.
4. `Training Manager` Approve/Reject.
5. `Condition` может скрыть недоступный переход.
6. `workflow_state` создаст сам Workflow.
7. Все состояния курса имеют `Doc Status = 0`.
8. Обычный `Status` не синхронизируется автоматически.
9. `Approved` — конечное состояние, `Rejected` имеет Reopen.

Теперь выполни [**лабораторную 26**](labs/26_WORKFLOW_AND_TRANSITIONS_LAB.md).