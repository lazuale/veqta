# Лабораторная 05. DocField и свойства полей

## Что уже должно быть готово

Лабораторная 04 завершена.

`Request` существует как Standard DocType в Module `Training`.

Поля:

```text
subject      Data        Mandatory
description  Small Text
status       Select      Open / In Progress / Done
due_date     Date
```

Есть минимум четыре Request Documents.

---

## Что сейчас получим

К `Request` добавятся:

```text
priority
is_urgent
estimate_hours
notes
reference_file
```

И будет проверено руками:

```text
Default
In List View
Read Only
Hidden
Mandatory
Description
```

После восстановления конфликтных тестовых настроек не останется.

---

## Сделай руками

### 1. Открой DocType `Request`

Через поиск Desk открой:

```text
DocType
```

Найди:

```text
Request
```

Открой его для редактирования.

---

### 2. Добавь `Priority`

Добавь поле:

```text
Label:      Priority
Fieldname:  priority
Field Type: Select
Options:
Low
Medium
High
Default:    Medium
In List View: включено
```

---

### 3. Добавь `Is Urgent`

```text
Label:      Is Urgent
Fieldname:  is_urgent
Field Type: Check
Default:    0
```

---

### 4. Добавь `Estimate Hours`

```text
Label:      Estimate Hours
Fieldname:  estimate_hours
Field Type: Int
Description: Оценка трудозатрат целым числом часов
```

---

### 5. Добавь `Notes`

```text
Label:      Notes
Fieldname:  notes
Field Type: Text Editor
```

---

### 6. Добавь `Reference File`

```text
Label:      Reference File
Fieldname:  reference_file
Field Type: Attach
```

---

### 7. Добавь поля списка

У существующих полей включи:

```text
Status   → In List View
Due Date → In List View
```

Для `Priority` это уже включено.

Нажми Save у DocType.

---

## Проверь новую форму

Открой один существующий Request.

Ты должен увидеть новые поля:

```text
Priority
Is Urgent
Estimate Hours
Notes
Reference File
```

У старого сохранённого Request поле `Priority` не обязано стать `Medium` только из-за нового Default.

Заполни у этого существующего документа:

```text
Priority:       High
Is Urgent:      включено
Estimate Hours: 3
```

Сохрани.

---

## Эксперимент 1 — Default

Создай **новый** Request.

Сразу после открытия новой формы посмотри на:

```text
Priority
```

Ожидается:

```text
Medium
```

Заполни:

```text
Subject:      Проверить Default Priority
Status:       Open
Due Date:     2026-09-06
```

Сохрани.

Теперь сравни:

```text
старый Request
→ его Priority не был массово переписан

новый Request
→ получил Medium при создании
```

---

## Эксперимент 2 — In List View

Вернись в `Request` List View.

В списке должны быть видны короткие рабочие поля, включая:

```text
Status
Priority
Due Date
```

Если ширины окна мало, Frappe может сжать отображение, но поля помечены metadata как предназначенные для List View.

Главное наблюдение:

```text
изменили свойство DocField
→ изменилось представление списка
```

---

## Эксперимент 3 — Read Only

Вернись в DocType `Request`.

Для поля:

```text
Estimate Hours
```

временно включи:

```text
Read Only
```

Сохрани DocType и обнови форму существующего Request.

Ожидаемый результат:

```text
Estimate Hours видно
→ обычное редактирование через форму недоступно
```

После наблюдения вернись в DocType, выключи `Read Only` и снова сохрани.

Проверь, что поле снова редактируется.

---

## Эксперимент 4 — Hidden

Для:

```text
Reference File
```

временно включи:

```text
Hidden
```

Сохрани DocType и обнови Request Form.

Ожидается:

```text
Reference File исчез из обычной формы
```

Затем снова выключи `Hidden`, сохрани DocType и убедись, что поле вернулось.

---

## Намеренная ошибка — Mandatory

Теперь проверим свойство, которое влияет на сохранение.

В DocType `Request` у поля:

```text
Due Date
```

временно включи:

```text
Mandatory
```

Сохрани DocType.

Создай новый Request:

```text
Subject:  Проверка Mandatory Due Date
Status:   Open
Priority: Medium
Due Date: оставить пустым
```

Нажми Save.

Ожидаемый результат:

```text
Frappe не сохраняет Document
→ обязательное поле Due Date не заполнено
```

Это контролируемая ошибка metadata, а не случайный сбой.

---

## Восстановление

Не сохраняй некорректный тестовый Document.

Вернись в DocType `Request` и у `Due Date` выключи:

```text
Mandatory
```

Сохрани DocType.

Теперь создай **новый** Request:

```text
Subject:  Проверка восстановленного Due Date
Status:   Open
Priority: Medium
Due Date: оставить пустым
```

Нажми Save.

Ожидаемый результат:

```text
Document успешно сохранён
→ Due Date снова необязателен
```

Этот восстановительный Request оставь на стенде.

---

## Проверка себя

Для каждого утверждения определи: это **metadata DocField** или **значение Document**.

```text
Priority имеет Field Type Select
Priority = High у конкретного Request
Priority имеет Default = Medium
Due Date = 2026-09-06 у конкретного Request
Estimate Hours имеет Description
Reference File имеет Field Type Attach
```

Ответь также:

1. Почему `Default = Medium` не означает массовое обновление старых Requests?
2. Чем `Hidden` отличается от permission-механизма?
3. Почему `fieldname` важнее сохранить стабильным, чем Label?
4. Что именно вызвало отказ при пустом Mandatory `Due Date`?

---

## Состояние стенда после лабораторной

`Request` содержит:

```text
Subject         subject         Data        Mandatory
Description     description     Small Text
Status          status          Select      Open / In Progress / Done
Due Date        due_date        Date
Priority        priority        Select      Low / Medium / High, Default Medium
Is Urgent       is_urgent       Check
Estimate Hours  estimate_hours  Int
Notes           notes           Text Editor
Reference File  reference_file  Attach
```

Итоговые свойства:

```text
Status    → In List View
Priority  → In List View
Due Date  → In List View
Estimate Hours → Read Only выключено
Reference File → Hidden выключено
Due Date → Mandatory выключено
```

`Subject` остаётся Mandatory.

Существующие Request Documents сохранены.

Дополнительно обязательно существует восстановительный Document:

```text
Subject:  Проверка восстановленного Due Date
Status:   Open
Priority: Medium
Due Date: пусто
```

Это точное входное состояние [**главы 06**](../06_NAMING.md).