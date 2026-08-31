# Лабораторная 24. Assignment Rule

## Что уже должно быть готово

Лабораторная 23 завершена.

Есть ручной Request:

```text
E23-Assignment-Manual
```

с одним активным Assignment:

```text
student.user@example.test
```

Sharing включён:

```text
Disable Document Sharing = ☐
```

Assignment Rule ещё не создан.

---

## Что сейчас получим

Останется правило:

```text
Training Request Round Robin
Disabled = ✓
```

Оно будет проверено на последовательности:

```text
E24-RR-1 → student.user@example.test
E24-RR-2 → student.manager@example.test
E24-RR-3 → student.user@example.test
E24-RR-4 → student.manager@example.test
```

Также останется один no-match Request без Assignment:

```text
E24-NoMatch
Status = Done
```

---

# Часть 1. Создай правило

Работай под `Administrator`.

Открой:

```text
http://learn.localhost:8000/app/assignment-rule
```

Создай новый `Assignment Rule`.

Имя:

```text
Training Request Round Robin
```

Заполни:

```text
Document Type: Request
Priority:      10
Disabled:      ☐
Description:   Auto assignment: {{ subject }}
```

В `Assign Condition`:

```python
status == "Open"
```

`Unassign Condition` и `Close Condition` оставь пустыми.

В `Assignment Days` нажми:

```text
All Days
```

Убедись, что появились все семь дней недели.

В `Rule` выбери:

```text
Round Robin
```

В `Users` добавь строго в таком порядке:

```text
1. student.user@example.test
2. student.manager@example.test
```

Сохрани.

Проверь:

```text
Last User = пусто
```

---

# Часть 2. Проверь Round Robin

Полностью войди:

```text
student.manager@example.test
FrappeCourse!2026
```

Создай четыре Request по очереди.

Для каждого используй:

```text
Status:   Open
Priority: Medium
Area:     North
Due Date: 2026-09-05
```

Subject меняй:

```text
E24-RR-1
E24-RR-2
E24-RR-3
E24-RR-4
```

После каждого `Save` посмотри активный Assignment на форме.

Ожидается строго:

```text
E24-RR-1 → student.user@example.test
E24-RR-2 → student.manager@example.test
E24-RR-3 → student.user@example.test
E24-RR-4 → student.manager@example.test
```

---

## Проверь через ToDo

Открой:

```text
http://learn.localhost:8000/app/todo
```

Фильтруй по:

```text
Reference Type = Request
Status         = Open
```

Для четырёх E24 Request проверь поле:

```text
Assignment Rule = Training Request Round Robin
```

Вернись к самому Assignment Rule и проверь:

```text
Last User = student.manager@example.test
```

---

# Эксперимент — condition не выполняется

Создай Request:

```text
Subject:  E24-NoMatch
Status:   Done
Priority: Medium
Area:     North
Due Date: 2026-09-05
```

Сохрани.

Ожидается:

```text
Assignment отсутствует
```

Через ToDo List проверь, что для `E24-NoMatch` не создан Open ToDo с нашим Assignment Rule.

Причина одна:

```python
status == "Open"
```

для этого документа ложно.

---

# Намеренная поломка — assignee без доступа и Sharing выключен

После `E24-RR-4` поле `Last User` равно менеджеру.

Значит следующий подходящий Request Round Robin попытается назначить:

```text
student.user@example.test
```

## 1. Временно отключи document sharing

Под `Administrator` открой `System Settings`.

Установи:

```text
Disable Document Sharing = ✓
```

Сохрани.

---

## 2. Попробуй создать South Request

Снова войди менеджером.

Создай:

```text
Subject:  E24-Permission-Failure
Status:   Open
Priority: Medium
Area:     South
Due Date: 2026-09-05
```

Нажми `Save`.

Ожидается отказ с заголовком:

```text
Missing Permission
```

Смысл сообщения:

```text
student.user@example.test
не имеет доступа к этому документу
и document sharing отключён
```

Не пытайся обходить ошибку изменением User Permission.

---

# Восстановление

Под `Administrator` верни:

```text
Disable Document Sharing = ☐
```

Сохрани.

Теперь снова войди менеджером и создай контрольный Request:

```text
Subject:  E24-Recovered
Status:   Open
Priority: Medium
Area:     North
Due Date: 2026-09-05
```

Сохрани.

Ожидается:

```text
Save успешен
Assignment → student.user@example.test
```

Это подтверждает, что после восстановления правило снова работает.

---

# Часть 3. Отключи правило перед следующей главой

Под `Administrator` открой:

```text
Training Request Round Robin
```

Установи:

```text
Disabled = ✓
```

Сохрани.

Проверь:

```text
Status правила больше не влияет на новые Request
```

Само правило не удаляй.

---

## Проверка себя

1. Что создаёт Assignment Rule после успешного срабатывания?
2. Почему `E24-NoMatch` не получил Assignment?
3. В каком порядке Round Robin использовал двух Users?
4. Для чего нужен `Last User`?
5. Почему South Request дал `Missing Permission` только после отключения Sharing?
6. Заменяет ли Assignment Rule Role Permission или User Permission?
7. Почему правило оставлено Disabled?

---

## Состояние стенда после лабораторной

Существует:

```text
Training Request Round Robin
  Document Type: Request
  Assign Condition: status == "Open"
  Rule: Round Robin
  Users:
    student.user@example.test
    student.manager@example.test
  Assignment Days: All Days
  Disabled: ✓
```

Проверены и остаются документы:

```text
E24-RR-1
E24-RR-2
E24-RR-3
E24-RR-4
E24-NoMatch
E24-Recovered
```

`E24-Permission-Failure` не должен считаться сохранённым рабочим документом после отказа.

Глобально снова:

```text
Disable Document Sharing = ☐
```

Это точное входное состояние [**главы 25**](../25_STATUS_VS_WORKFLOW_STATE.md).