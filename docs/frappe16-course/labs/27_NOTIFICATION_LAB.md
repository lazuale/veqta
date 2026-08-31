# Лабораторная 27. Notification

## Что уже должно быть готово

Лабораторная 26 завершена.

Активен:

```text
Training Request Workflow
```

Переходы:

```text
Draft --Send for Review--> Review       [Training User]
Review --Approve---------> Approved     [Training Manager]
Review --Reject----------> Rejected     [Training Manager]
Rejected --Reopen--------> Draft        [Training User]
```

Для `Send for Review` действует Condition:

```python
doc.due_date
```

`Training Request Round Robin` остаётся Disabled.

---

## Что сейчас получим

Останется Notification:

```text
Training Review Notification
Enabled = ☐
```

Перед отключением будет доказано, что переход:

```text
Draft → Review
```

создаёт System Notification для:

```text
student.manager@example.test
```

---

# Часть 1. Создай Notification rule

Работай под `Administrator`.

Открой:

```text
http://learn.localhost:8000/app/notification
```

Создай новый `Notification`.

Заполни:

```text
Enabled:       ✓
Channel:       System Notification
Document Type: Request
Send Alert On: Value Change
Value Changed: workflow_state
Condition Type: Python
```

В `Recipients` добавь одну строку:

```text
Receiver By Role: Training Manager
```

Для внутреннего уведомления укажи:

```text
Notification Title:
Request {{ doc.name }} ждёт проверки

Notification Message:
{{ doc.subject }}
```

`Notification Type` оставь со штатным значением:

```text
Alert
```

---

# Намеренная ошибка — неверный Condition

Сначала введи неправильное выражение:

```python
doc.workflow_state = "Review"
```

Попробуй сохранить Notification.

Когда Frappe запросит имя нового правила, введи:

```text
Training Review Notification
```

Ожидается отказ сохранения: Condition недопустим.

Причина:

```text
=
```

не является оператором сравнения в выражении.

---

# Восстановление

Исправь Condition на:

```python
doc.workflow_state == "Review"
```

Сохрани снова.

Ожидается успешное сохранение:

```text
Training Review Notification
Enabled = ✓
```

---

# Часть 2. Создай Request, который должен дать уведомление

Полностью войди:

```text
student.user@example.test
FrappeCourse!2026
```

Создай:

```text
Subject:  E27-Notify-Review
Status:   Open
Priority: Medium
Area:     North
Due Date: 2026-09-07
Notes:    System notification positive case
```

Сохрани.

Ожидается:

```text
Workflow State = Draft
```

На самом первом Save Notification не должен сработать как `Value Change`.

---

## Выполни Workflow Action

Выбери:

```text
Send for Review
```

После перехода:

```text
Workflow State = Review
```

Теперь одновременно выполнены условия:

```text
workflow_state изменился
+
новое значение = Review
```

---

# Часть 3. Проверь Notification под менеджером

Полностью войди:

```text
student.manager@example.test
FrappeCourse!2026
```

Открой панель уведомлений Desk.

Найди уведомление с заголовком вида:

```text
Request <system name E27-Notify-Review> ждёт проверки
```

и текстом:

```text
E27-Notify-Review
```

---

## Проверь системный Notification Log

Открой:

```text
http://learn.localhost:8000/app/notification-log
```

Отфильтруй:

```text
For User      = student.manager@example.test
Document Type = Request
Document Name = <system name E27-Notify-Review>
```

Открой найденную запись.

Сопоставь:

```text
For User      = student.manager@example.test
Document Type = Request
Document Name = <system name E27-Notify-Review>
Title         = Request <name> ждёт проверки
Description   = E27-Notify-Review
```

Это конкретный `Notification Log`, созданный нашим правилом.

---

# Эксперимент 1 — обычный Save не является Value Change workflow_state

Оставаясь менеджером, на том же Request измени только:

```text
Notes = Review note changed without state transition
```

Сохрани.

Снова открой `Notification Log` с теми же фильтрами.

Ожидается:

```text
новая запись от этого Save не появилась
```

Потому что:

```text
workflow_state = Review
```

не изменился.

---

# Часть 4. Заверши первый Request

На `E27-Notify-Review` выполни:

```text
Approve
```

Ожидается:

```text
Workflow State = Approved
```

Нового уведомления по нашему правилу быть не должно, потому что Condition требует именно:

```text
Review
```

---

# Эксперимент 2 — временно сделай Condition ложным для Review

Под `Administrator` открой:

```text
Training Review Notification
```

Временно установи:

```python
doc.workflow_state == "Approved"
```

Сохрани.

---

## Создай второй Request

Войди обычным User и создай:

```text
Subject:  E27-Notify-NoHit
Status:   Open
Priority: Medium
Area:     North
Due Date: 2026-09-08
Notes:    Condition negative case
```

Сохрани и выполни:

```text
Send for Review
```

Получаем:

```text
Workflow State = Review
```

---

## Проверь отсутствие уведомления

Войди менеджером.

Открой:

```text
http://learn.localhost:8000/app/notification-log
```

Отфильтруй:

```text
For User      = student.manager@example.test
Document Type = Request
Document Name = <system name E27-Notify-NoHit>
```

Ожидается:

```text
0 записей от Training Review Notification
```

Причина:

```python
doc.workflow_state == "Approved"
```

для перехода в `Review` ложно.

---

# Восстановление Notification

Под `Administrator` верни Condition:

```python
doc.workflow_state == "Review"
```

Сохрани.

---

## Заверши второй Request без нового Review notification

Войди менеджером и открой:

```text
E27-Notify-NoHit
```

Выполни:

```text
Approve
```

Ожидается:

```text
Workflow State = Approved
```

Condition снова требует `Review`, поэтому переход `Review → Approved` не создаёт наше уведомление.

---

# Часть 5. Отключи правило перед следующей главой

Под `Administrator` открой:

```text
Training Review Notification
```

Установи:

```text
Enabled = ☐
```

Сохрани.

Правило не удаляй.

---

## Проверка себя

1. Чем `Notification` отличается от `Notification Log`?
2. Почему первый Save нового Request не дал Value Change notification?
3. Какое поле отслеживалось?
4. Почему изменение Notes не создало новую запись?
5. Зачем кроме Value Change был нужен Condition?
6. Кто был получателем и как он выбирался?
7. Нужен ли SMTP для этого опыта?
8. Почему выражение с одним `=` не сохранилось?
9. Почему правило оставлено Disabled?

---

## Состояние стенда после лабораторной

Существует:

```text
Training Review Notification
  Channel: System Notification
  Document Type: Request
  Send Alert On: Value Change
  Value Changed: workflow_state
  Condition: doc.workflow_state == "Review"
  Receiver By Role: Training Manager
  Notification Type: Alert
  Notification Title: Request {{ doc.name }} ждёт проверки
  Notification Message: {{ doc.subject }}
  Enabled: ☐
```

Есть доказанный Notification Log для:

```text
E27-Notify-Review
→ For User = student.manager@example.test
```

Контрольные Request:

```text
E27-Notify-Review
  Workflow State: Approved

E27-Notify-NoHit
  Workflow State: Approved
```

Workflow остаётся Active.

Assignment Rule остаётся Disabled.

Это точное входное состояние [**главы 28**](../28_AUTO_REPEAT.md).