# Лабораторная 23. Assignment и ToDo

## Что уже должно быть готово

Блок D завершён.

На стенде есть:

```text
student.user@example.test
student.manager@example.test
```

Оба — Enabled System User.

Permission model `Request` восстановлена:

```text
Training User
→ Read + Create + Write
→ Training Area = North

Training Manager
→ расширенные права
→ без Training Area User Permission
```

Sharing включён:

```text
Disable Document Sharing = ☐
```

---

## Что сейчас получим

Останется новый Request:

```text
Subject: E23-Assignment-Manual
Status: Open
Priority: Medium
Area: North
Responsible: пусто
```

Его `owner`:

```text
student.manager@example.test
```

На нём останется ровно один активный Assignment:

```text
Allocated To: student.user@example.test
Status: Open
Priority: Medium
```

---

# Часть 1. Создай отдельный Request для Assignment

Полностью войди:

```text
student.manager@example.test
FrappeCourse!2026
```

Создай Request:

```text
Subject:     E23-Assignment-Manual
Status:      Open
Priority:    Medium
Area:        North
Responsible: пусто
Notes:       Manual assignment example
```

Сохрани.

Запомни его системный `name` вида:

```text
REQ-....
```

Проверь:

```text
owner = student.manager@example.test
```

---

# Часть 2. Назначь Request обычному User

На сохранённой форме используй штатное действие:

```text
Assign
```

В диалоге укажи:

```text
Assign To:   student.user@example.test
Complete By: 2026-09-02
Priority:    Medium
Comment:     Check E23 manual assignment
```

Подтверди назначение.

На форме должен появиться активный Assignment на:

```text
student.user@example.test
```

---

# Часть 3. Найди реальный ToDo

Открой:

```text
http://learn.localhost:8000/app/todo
```

Отфильтруй:

```text
Reference Type = Request
Reference Name = <system name E23-Assignment-Manual>
Allocated To   = student.user@example.test
```

Открой найденный ToDo.

Сопоставь:

```text
Allocated To   = student.user@example.test
Reference Type = Request
Reference Name = <system name E23-Assignment-Manual>
Status         = Open
Priority       = Medium
Due Date       = 2026-09-02
Assigned By    = student.manager@example.test
```

Теперь видно, что действие Assign создало отдельный Document.

---

# Часть 4. Проверь назначение под assignee

Полностью перезайди:

```text
student.user@example.test
FrappeCourse!2026
```

Открой тот же Request.

Он должен быть доступен и по обычным permissions, потому что:

```text
Area = North
```

На форме должен быть виден твой активный Assignment.

Также открой:

```text
http://learn.localhost:8000/app/todo
```

и отфильтруй:

```text
Allocated To = student.user@example.test
Status       = Open
Reference Type = Request
```

В списке должен быть ToDo нашего E23 Request.

---

# Эксперимент — два Assignment на одном Request

Снова войди менеджером.

Открой:

```text
E23-Assignment-Manual
```

Через `Assign` добавь второго assignee:

```text
student.manager@example.test
```

Используй:

```text
Complete By: 2026-09-03
Priority:    High
Comment:     Second temporary assignment
```

Теперь на одном Request должны существовать два Open ToDo:

```text
student.user@example.test
student.manager@example.test
```

Проверь это через:

```text
http://learn.localhost:8000/app/todo
```

с фильтром по `Reference Name`.

---

## Удали только временный второй Assignment

Вернись на Request и штатно сними Assignment:

```text
student.manager@example.test
```

Не закрывай Assignment обычного User.

В ToDo проверь:

```text
student.manager@example.test
→ Status = Cancelled

student.user@example.test
→ Status = Open
```

---

# Намеренная ошибка модели — попробуй заменить Assignment полем Responsible

Работай менеджером на том же Request.

До изменения через ToDo List убедись, что активный Open ToDo для этого Request сейчас один:

```text
Allocated To = student.user@example.test
Status = Open
```

Теперь в самом Request установи:

```text
Responsible = student.manager@example.test
```

Сохрани.

Снова открой ToDo List и поставь фильтр:

```text
Reference Type = Request
Reference Name = <system name E23-Assignment-Manual>
Status         = Open
```

Ожидается по-прежнему:

```text
1 Open ToDo
```

Новый ToDo для `student.manager@example.test` не появился.

Это намеренно неправильная попытка использовать обычный Link как Assignment.

---

# Восстановление

Верни в Request:

```text
Responsible = пусто
```

Сохрани.

Финально проверь:

```text
owner = student.manager@example.test
Responsible = пусто
```

и ровно один Open Assignment:

```text
student.user@example.test
```

---

## Проверка себя

Ответь без подсказки.

1. Какой DocType создаётся после Assign?
2. Какими полями ToDo связан с Request?
3. Изменился ли owner после назначения?
4. Почему изменение Responsible не создало Assignment?
5. Может ли один Request иметь несколько Assignment?
6. Чем `Closed` ToDo отличается от `Cancelled`?
7. Кто остался assignee нашего E23 Request?

---

## Состояние стенда после лабораторной

Существует:

```text
E23-Assignment-Manual
  owner:       student.manager@example.test
  Status:      Open
  Priority:    Medium
  Area:        North
  Responsible: пусто
  Notes:       Manual assignment example
```

Для него существует один активный ToDo:

```text
Allocated To:   student.user@example.test
Reference Type: Request
Reference Name: <name E23-Assignment-Manual>
Status:         Open
Priority:       Medium
Due Date:       2026-09-02
Assigned By:    student.manager@example.test
```

Временный Assignment менеджера остаётся только как `Cancelled` ToDo.

Permissions и Sharing не менялись.

Это точное входное состояние [**главы 24**](../24_ASSIGNMENT_RULE.md).