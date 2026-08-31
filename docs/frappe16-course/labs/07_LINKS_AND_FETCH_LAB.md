# Лабораторная 07. Link, Dynamic Link и Fetch From

## Что уже должно быть готово

Лабораторная 06 завершена.

`Request` содержит:

```text
subject
description
status
due_date
priority
is_urgent
estimate_hours
notes
reference_file
```

Naming:

```text
Title Field: subject
Auto Name:   REQ-.YYYY.-.#####
```

Есть минимум один новый Request вида:

```text
REQ-2026-.....
```

---

## Что сейчас получим

Постоянно добавим к `Request`:

```text
Responsible       responsible       Link → User
Responsible Name  responsible_name  Data
                                  Read Only
                                  Fetch From = responsible.full_name
```

Временно добавим и затем удалим:

```text
Reference Type  reference_type  Link → DocType
Reference Name  reference_name  Dynamic Link → reference_type
```

---

## Сделай руками

### 1. Открой DocType `Request`

Через поиск Desk:

```text
DocType
→ Request
```

---

### 2. Добавь `Responsible`

Создай поле:

```text
Label:      Responsible
Fieldname:  responsible
Field Type: Link
Options:    User
```

Сохрани DocType.

---

### 3. Добавь `Responsible Name`

Создай следующее поле:

```text
Label:      Responsible Name
Fieldname:  responsible_name
Field Type: Data
Read Only:  включено
Fetch From: responsible.full_name
```

Снова сохрани DocType.

---

## Проверь обычный Link и Fetch From

### 4. Открой существующий Request

Открой любой Request серии:

```text
REQ-2026-.....
```

В поле:

```text
Responsible
```

выбери:

```text
Administrator
```

После выбора проверь:

```text
Responsible
→ содержит ссылку на User Administrator

Responsible Name
→ заполняется значением full_name связанного User
```

Сохрани Request.

---

### 5. Поменяй связанный User

В том же Request выбери в `Responsible` другого существующего пользователя, например:

```text
Guest
```

если он доступен для выбора на твоём чистом Site.

Наблюдай:

```text
изменился Link
→ Frappe снова выполнил Fetch From
→ Responsible Name изменился вслед за выбранным User
```

После опыта верни:

```text
Responsible = Administrator
```

и сохрани.

Если `Guest` не предлагается Link-полем в интерфейсе, используй любой другой существующий `User` из списка `User`, но итоговое значение снова верни на `Administrator`.

---

## Намеренная ошибка — битая Link-ссылка

В новом или существующем Request очисти `Responsible`.

Введи заведомо несуществующее значение:

```text
not-a-real-user@example.test
```

Попробуй сохранить Document.

Ожидаемое поведение:

```text
Frappe не принимает ссылку на отсутствующий User
→ сохранение блокируется или Link control сообщает, что значение не существует
```

Смысл ошибки однозначен:

```text
Link → User
```

не должен содержать имя Document, которого нет в `User`.

---

## Восстановление

Выбери через штатный список Link:

```text
Responsible = Administrator
```

Убедись, что `Responsible Name` снова заполнился.

Сохрани Request.

---

## Эксперимент — Dynamic Link

Теперь временно расширим **тот же** `Request`.

### 6. Добавь `Reference Type`

В DocType `Request` создай:

```text
Label:      Reference Type
Fieldname:  reference_type
Field Type: Link
Options:    DocType
```

### 7. Добавь `Reference Name`

Следом создай:

```text
Label:      Reference Name
Fieldname:  reference_name
Field Type: Dynamic Link
Options:    reference_type
```

Сохрани DocType.

---

### 8. Проверь ссылку на `User`

Открой Request.

Выбери:

```text
Reference Type = User
```

После этого в:

```text
Reference Name
```

выбери:

```text
Administrator
```

Сейчас пара означает:

```text
(User, Administrator)
```

---

### 9. Переключи тип цели

Измени:

```text
Reference Type = Request
```

Теперь `Reference Name` должен работать уже с Documents DocType `Request`.

Выбери существующий Request серии:

```text
REQ-2026-.....
```

Теперь пара означает:

```text
(Request, REQ-2026-.....)
```

Сравни с постоянным полем:

```text
Responsible
→ всегда User

Reference Name
→ тип цели определяется Reference Type
```

---

## Восстановление после Dynamic Link

Dynamic Link был только учебным опытом и дальше модели `Request` не нужен.

Вернись в DocType `Request` и удали обе временные строки Fields:

```text
Reference Type  reference_type
Reference Name  reference_name
```

Сохрани DocType.

Обнови Request Form.

Проверь:

```text
Responsible       остался
Responsible Name  остался
Reference Type    отсутствует
Reference Name    отсутствует
```

---

## Проверка себя

Ответь без подсказки.

1. На какой DocType всегда ссылается `Responsible`?
2. Что хранит Link: Label пользователя или его системный `name`?
3. Откуда берётся `Responsible Name`?
4. Почему `not-a-real-user@example.test` нельзя сохранить как корректный Link → User?
5. Откуда Dynamic Link узнаёт DocType цели?
6. Чем `(User, Administrator)` отличается от обычного `Responsible = Administrator`?
7. Какие поля должны остаться после удаления временного Dynamic Link опыта?

---

## Состояние стенда после лабораторной

`Request` сохраняет предыдущие поля и получает:

```text
Responsible
  fieldname: responsible
  type:      Link
  options:   User

Responsible Name
  fieldname: responsible_name
  type:      Data
  Read Only: включено
  Fetch From: responsible.full_name
```

Минимум один Request сохранён с:

```text
Responsible = Administrator
```

Временные поля полностью удалены из metadata:

```text
reference_type
reference_name
```

Это точное входное состояние [**главы 08**](../08_CHILD_TABLES.md).