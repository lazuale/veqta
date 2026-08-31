# 27. Notification

Workflow из главы 26 управляет переходами `Request`. Теперь добавим отдельный механизм, который не меняет состояние и не назначает работу, а только сообщает нужным пользователям о событии.

Во Frappe для этого есть системный DocType:

```text
Notification
```

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть

Для `Request` активен:

```text
Training Request Workflow
```

Ключевой переход:

```text
Draft
→ Send for Review
→ Review
```

Роль:

```text
Training Manager
```

получает право Approve/Reject.

Именно менеджеру и будем отправлять внутреннее уведомление, когда Request впервые переходит в `Review`.

---

# 1. Notification — это правило, Notification Log — результат

Нужно различать два системных DocType.

### Notification

Хранит правило:

```text
когда срабатывать
на каком DocType
при каком условии
кому отправить
что показать
```

### Notification Log

Хранит конкретное уведомление конкретного пользователя.

Схема:

```text
Notification rule
        ↓
событие произошло
        ↓
условие истинно
        ↓
Notification Log
        ↓
пользователь видит уведомление в Desk
```

---

# 2. Assignment и Notification — разные механизмы

Assignment отвечает:

```text
кто должен выполнить работу
```

и создаёт `ToDo`.

Notification отвечает:

```text
кого нужно проинформировать
```

и в нашем сценарии создаёт `Notification Log`.

Получить уведомление не означает автоматически стать assignee.

---

# 3. Наше правило

Создадим:

```text
Training Review Notification
```

с настройками:

```text
Channel:       System Notification
Document Type: Request
Send Alert On: Value Change
Value Changed: workflow_state
Condition:     doc.workflow_state == "Review"
```

Получатель:

```text
Receiver By Role = Training Manager
```

В текущем учебном стенде эту роль имеет:

```text
student.manager@example.test
```

---

# 4. Почему именно `Value Change`

Нас интересует не любое сохранение Request, а конкретное изменение поля:

```text
workflow_state
```

Переход:

```text
Draft → Review
```

меняет это поле, поэтому `Value Change` подходит точно.

Если после этого пользователь просто изменит `Notes` и сохранит документ, `workflow_state` не меняется и правило не должно срабатывать повторно.

---

# 5. Зачем ещё Condition

Сам `Value Change` означает только:

```text
поле workflow_state изменилось
```

Но оно может измениться и так:

```text
Review → Approved
Review → Rejected
Rejected → Draft
```

Поэтому добавляем:

```python
doc.workflow_state == "Review"
```

Получаем две проверки одновременно:

```text
workflow_state действительно изменился
+
новое значение равно Review
```

Только тогда создаётся уведомление.

---

# 6. Почему используем System Notification

В `v16.32.0` Channel `Notification` поддерживает:

```text
Email
Slack
System Notification
SMS
```

В этой главе выбираем только:

```text
System Notification
```

Это важно для учебного стенда:

```text
SMTP не нужен
Email Account не нужен
внешний сервис не нужен
```

Результат остаётся полностью внутри Frappe.

Email будет отдельной темой позже.

---

# 7. Текст внутреннего уведомления

Для System Notification есть отдельные поля:

```text
Notification Type
Notification Title
Notification Message
```

В лабораторной используем:

```text
Notification Title:
Request {{ doc.name }} ждёт проверки

Notification Message:
{{ doc.subject }}
```

Jinja-подстановки берут значения из текущего Request.

Например:

```text
Request REQ-2026-00042 ждёт проверки
E27-Notify-Review
```

---

# 8. Получатель по Role

В таблице `Recipients` можно указать:

```text
Receiver By Role
```

Мы выберем:

```text
Training Manager
```

Это не изменение permission model.

Role здесь используется только для поиска получателей Notification.

---

# 9. Что проверить после срабатывания

После перехода Request в `Review` менеджер должен получить внутреннее уведомление.

Его можно увидеть:

```text
в панели уведомлений Desk
```

и как отдельный системный Document:

```text
http://learn.localhost:8000/app/notification-log
```

В `Notification Log` важны поля:

```text
Type
Title
Description
Document Type
Document Name
For User
From User
Read
```

Для нашего опыта ожидается:

```text
For User      = student.manager@example.test
Document Type = Request
Document Name = <name E27 Request>
```

---

# 10. Что произойдёт при обычном Save

Допустим Request уже находится в:

```text
Review
```

Пользователь изменил только:

```text
Notes
```

и сохранил.

Поле:

```text
workflow_state
```

не изменилось.

Значит `Value Change` для него не проходит и новое уведомление по нашему правилу не создаётся.

Это удобнее, чем вешать правило на каждый `Save`.

---

# 11. Гарантированная ошибка в Condition

`Condition` — выражение, которое Frappe проверяет при сохранении самого Notification rule.

Корректно:

```python
doc.workflow_state == "Review"
```

Некорректно:

```python
doc.workflow_state = "Review"
```

Один `=` — присваивание, а не допустимое выражение сравнения.

При сохранении такого Notification v16 отклоняет настройку как invalid condition.

В лабораторной намеренно сделаем эту ошибку и сразу восстановим `==`.

---

# 12. Почему Notification отключим после опыта

Правило будет полностью рабочим, но следующие главы продолжат менять `Request` и Workflow.

Чтобы оно не создавалo лишние уведомления во время других экспериментов, после проверки оставим Document существовать, но установим:

```text
Enabled = ☐
```

Так настройка остаётся доступна для изучения, но больше не вмешивается в курс.

---

## Что запомнить

1. `Notification` — правило, `Notification Log` — конкретный результат.
2. Notification не заменяет Assignment и Workflow.
3. `Value Change` проверяет изменение конкретного поля.
4. Condition уточняет нужное новое значение.
5. `System Notification` работает без SMTP.
6. Получателя можно выбрать по Role.
7. Неверное Python-выражение Condition отклоняется при сохранении правила.
8. После проверки учебное правило можно Disabled, а не удалять.

Теперь выполни [**лабораторную 27**](labs/27_NOTIFICATION_LAB.md).