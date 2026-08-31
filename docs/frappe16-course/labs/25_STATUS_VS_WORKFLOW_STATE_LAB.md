# Лабораторная 25. `Status` против `Workflow State`

## Что уже должно быть готово

Лабораторная 24 завершена.

`Training Request Round Robin` существует, но отключён:

```text
Disabled = ✓
```

Поэтому новые Request в этой и следующих главах не будут получать автоматические Assignment.

У `Request` по-прежнему есть обычное поле:

```text
Status
Open / In Progress / Done
```

Настоящий Workflow ещё не создан.

---

## Что сейчас получим

Останется Request:

```text
Subject: E25-Status-Only
Status: Open
Area: North
Due Date: 2026-09-05
```

Никакого `workflow_state` мы вручную не создаём.

---

# Часть 1. Создай обычный Request

Войди:

```text
student.user@example.test
FrappeCourse!2026
```

Создай:

```text
Subject:  E25-Status-Only
Status:   Open
Priority: Medium
Area:     North
Due Date: 2026-09-05
Notes:    Status is still a plain Select
```

Сохрани.

Проверь, что на форме нет Workflow Actions:

```text
Send for Review
Approve
Reject
Reopen
```

Их ещё не существует.

---

# Часть 2. Измени Status напрямую

В том же Request установи:

```text
Status = In Progress
```

Сохрани.

Затем сразу:

```text
Status = Done
```

и снова сохрани.

Ожидается:

```text
оба Save успешны
```

Framework не потребовал отдельного действия перехода и не проверял промежуточный граф состояний.

---

# Эксперимент — измени другие поля независимо от Status

При:

```text
Status = Done
```

измени:

```text
Notes = Done is still editable by normal field permissions
```

Сохрани.

Ожидается обычный Save.

Причина: само значение `Done` не включает отдельный механизм блокировки или согласования.

---

# Намеренно неправильный процессный переход

Верни:

```text
Status = Open
```

Сохрани.

Теперь одним действием снова установи:

```text
Status = Done
```

и сохрани.

С точки зрения будущего процесса это намеренный «прыжок» через промежуточные стадии.

Ожидается:

```text
Save успешен
```

Это не ошибка Framework. Мы пока используем всего лишь обычный Select.

---

# Восстановление

Верни:

```text
Status = Open
Notes  = Status is still a plain Select
```

Сохрани.

---

# Часть 3. Посмотри системные объекты будущего Workflow

Работай под `Administrator`.

Открой по очереди:

```text
http://learn.localhost:8000/app/workflow-state
http://learn.localhost:8000/app/workflow
```

Сейчас ничего для `Request` не создавай.

Задача только увидеть, что:

```text
Workflow State
```

и:

```text
Workflow
```

— отдельные системные DocType, а не options нашего поля `Status`.

---

## Проверка себя

1. Почему `Open → Done` сейчас разрешён одним Save?
2. Создал ли обычный Status Workflow Action?
3. Является ли `Done` значением `docstatus`?
4. Чем `ToDo.status` отличается от `Request.status`?
5. Нужно ли вручную добавлять `workflow_state` перед следующей главой?
6. Почему обычный Status оставляем в `Request`, даже когда добавим Workflow?

---

## Состояние стенда после лабораторной

Существует:

```text
E25-Status-Only
  owner:    student.user@example.test
  Status:   Open
  Area:     North
  Due Date: 2026-09-05
  Notes:    Status is still a plain Select
```

`Training Request Round Robin` остаётся:

```text
Disabled = ✓
```

Для `Request` ещё нет активного Workflow.

Поле `workflow_state` вручную не создавалось.

Это точное входное состояние [**главы 26**](../26_WORKFLOW_AND_TRANSITIONS.md).