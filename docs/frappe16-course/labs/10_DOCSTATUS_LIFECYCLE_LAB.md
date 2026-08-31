# Лабораторная 10. `docstatus`, Submit, Cancel и Amendment

## Что уже должно быть готово

Лабораторная 09 завершена.

`Approval Record` существует как Standard Submittable DocType:

```text
Module:         Training
Is Submittable: включено
Auto Name:      APR-.YYYY.-.#####
Title Field:    subject
```

Поля:

```text
subject       Data   Mandatory
amended_from  Link → Approval Record   добавлено Framework
```

Есть минимум один Draft:

```text
APR-2026-00001
Subject = Первый черновик Approval Record
```

Он остаётся Draft и понадобится как контрольный пример.

---

## Что сейчас получим

К `Approval Record` добавим:

```text
Comment
  fieldname: comment
  Small Text
  Allow on Submit: выключено

Internal Note
  fieldname: internal_note
  Small Text
  Allow on Submit: включено
```

После лабораторной должны существовать примеры:

```text
Draft
Submitted
Cancelled
Amended Draft
```

---

## Подготовка DocType

### 1. Открой `Approval Record`

Через поиск Desk:

```text
DocType
→ Approval Record
```

---

### 2. Добавь `Comment`

```text
Label:      Comment
Fieldname:  comment
Field Type: Small Text
Allow on Submit: выключено
```

---

### 3. Добавь `Internal Note`

```text
Label:      Internal Note
Fieldname:  internal_note
Field Type: Small Text
Allow on Submit: включено
```

Сохрани DocType.

---

# Часть A. Draft → Submitted

## 4. Создай отдельный lifecycle Document

Не используй контрольный Draft `APR-2026-00001`.

Создай новый `Approval Record`:

```text
Subject: Lifecycle example
Comment: Черновик до Submit
Internal Note: оставить пустым
```

Нажми Save.

Зафиксируй его `name`.

На свежем стенде это будет следующий номер серии, например:

```text
APR-2026-00002
```

В интерфейсе документ должен быть Draft.

---

## 5. Проверь обычное редактирование Draft

Пока документ Draft, измени:

```text
Comment:
Черновик до Submit
→
Черновик проверен перед Submit
```

Нажми Save.

Изменение должно сохраниться обычным образом.

---

## 6. Выполни Submit

На этом же документе нажми:

```text
Submit
```

Подтверди действие, если Frappe показывает диалог подтверждения.

Ожидаемый результат:

```text
Document перестал быть Draft
→ состояние Submitted
```

Он по-прежнему существует под тем же `name`.

---

# Часть B. `Allow on Submit`

## Эксперимент — разрешённое изменение

После Submit найди поле:

```text
Internal Note
```

Введи:

```text
Добавлено после Submit
```

Выполни доступное действие сохранения/обновления Submitted Document (`Update`).

Ожидаемый результат:

```text
Internal Note изменился
→ Document остаётся Submitted
```

Причина:

```text
Internal Note
Allow on Submit = включено
```

---

## Намеренная неправильная попытка — обычное поле после Submit

Теперь попробуй изменить:

```text
Comment
```

Например, попытайся заменить текст на:

```text
Попытка изменить обычное поле после Submit
```

Ожидаемое поведение Form View:

```text
обычное поле после Submit недоступно для свободного редактирования
```

Если интерфейс не даёт поставить курсор и изменить значение — это и есть ожидаемая блокировка.

Не ищи обход через console, API или developer tools. Они ещё не изучались и разрушили бы смысл опыта.

---

## Восстановление после неправильной попытки

Никаких данных обычного поля измениться не должно.

Проверь:

```text
Comment = Черновик проверен перед Submit
Internal Note = Добавлено после Submit
состояние = Submitted
```

Если так, документ находится в корректном состоянии.

---

# Часть C. Submitted → Cancelled

## 7. Выполни Cancel

На lifecycle Document нажми:

```text
Cancel
```

Подтверди действие.

Ожидаемый результат:

```text
Submitted
→ Cancelled
```

Запись не исчезла из системы.

Зафиксируй её `name`: он понадобится для проверки Amendment.

---

## 8. Убедись, что Cancel не равен Delete

Вернись в список `Approval Record`.

Найди только что отменённый документ.

Он должен по-прежнему существовать и быть отмечен как Cancelled.

Наблюдение:

```text
Cancel
→ сохраняет запись и её историю
```

---

# Часть D. Cancelled → Amend → новый Draft

## 9. Открой Cancelled Document

Открой отменённый lifecycle Document.

Используй действие:

```text
Amend
```

Frappe создаст **новый** Approval Record в Draft.

Не ожидай конкретный суффикс нового `name`: для курса гарантированной связью является поле `Amended From`.

---

## 10. Проверь `Amended From`

В новом Draft найди:

```text
Amended From
```

Оно должно ссылаться на `name` отменённого lifecycle Document.

То есть должно выполняться:

```text
новый Draft.amended_from
=
name старого Cancelled Document
```

Это главное доказательство Amendment.

---

## 11. Измени исправленную версию

В новом Draft измени:

```text
Subject:
Lifecycle example
→
Lifecycle example amended
```

и:

```text
Comment:
Исправленная версия
```

Нажми Save.

**Не Submit этот amended Document.**

Он должен остаться Draft для сравнения в следующих главах.

---

# Часть E. Оставляем отдельный Submitted пример

## 12. Создай ещё один Approval Record

Создай:

```text
Subject: Submitted example
Comment: Этот документ остаётся Submitted
```

Сохрани, затем нажми:

```text
Submit
```

Его не Cancel и не Amend.

Он должен остаться Submitted.

---

## Проверь четыре состояния

В итоге у тебя должны быть минимум четыре смысловых примера.

### Draft

Контрольный документ из лабораторной 09:

```text
Subject = Первый черновик Approval Record
state = Draft
```

### Submitted

```text
Subject = Submitted example
state = Submitted
```

### Cancelled

Исходный lifecycle Document:

```text
Subject = Lifecycle example
state = Cancelled
```

### Amended Draft

Новая версия после Amend:

```text
Subject = Lifecycle example amended
state = Draft
Amended From = Cancelled lifecycle Document
```

---

## Эксперимент — сравни Form View состояний

По очереди открой:

```text
контрольный Draft
Submitted example
Cancelled lifecycle Document
Amended Draft
```

Сравни доступные действия и редактирование полей.

Задача не запомнить расположение кнопок, а увидеть:

```text
один DocType
+
разный docstatus
→ разное разрешённое поведение Form View
```

---

## Проверка себя

Ответь без подсказки.

1. Какое системное состояние имеет новый сохранённый Submittable Document?
2. Что делает Submit с `docstatus`?
3. Почему `Internal Note` можно было изменить после Submit?
4. Почему `Comment` был заблокирован?
5. Удалил ли Cancel Document?
6. Что создал Amend: изменение старой записи или новый Document?
7. На что указывает `Amended From`?
8. Чем `Request.status` отличается от `Approval Record.docstatus`?
9. Какие четыре примера должны остаться на стенде?

---

## Состояние стенда после лабораторной

`Approval Record`:

```text
Is Submittable: 1
Auto Name: APR-.YYYY.-.#####
Title Field: subject
```

Поля:

```text
Subject
  subject
  Data
  Mandatory

Comment
  comment
  Small Text
  Allow on Submit = 0

Internal Note
  internal_note
  Small Text
  Allow on Submit = 1

Amended From
  amended_from
  Link → Approval Record
  добавлено Framework
```

Данные:

```text
минимум 1 Draft
минимум 1 Submitted
минимум 1 Cancelled
минимум 1 Amended Draft с заполненным amended_from
```

Основной `Request` и все его поля/данные не менялись в этой лабораторной.

Это финальное состояние **блока B** и вход [**главы 11 — Form View**](../11_FORM_VIEW.md).