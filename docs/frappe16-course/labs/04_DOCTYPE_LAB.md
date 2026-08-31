# Лабораторная 04. Создаём первый DocType `Request`

## Что уже должно быть готово

Блок A завершён.

Стенд:

```text
Bench:          ~/frappe/frappe16-course-bench
Frappe:         v16.32.0
Site:           learn.localhost
Apps installed: frappe, training
Module:         Training
Developer Mode: включён
User:           Administrator
Request:        ещё не существует
```

В первом терминале работает:

```bash
cd ~/frappe/frappe16-course-bench
bench start
```

В браузере открыт:

```text
http://learn.localhost:8000/app
```

---

## Что сейчас получим

После лабораторной на стенде впервые появятся:

```text
DocType: Request

Fields:
subject
Description
status
due_date

минимум 4 Request Documents

Standard metadata:
apps/training/training/training/doctype/request/request.json
```

`Request` остаётся на стенде дальше.

---

## Сделай руками

### 1. Открой список DocType

В Desk через поиск открой:

```text
DocType
```

Нажми:

```text
New
```

---

### 2. Создай `Request`

Заполни верхнюю часть DocType:

```text
Name:    Request
Module:  Training
Custom?: выключено
```

Не включай специальные режимы:

```text
Is Child Table
Is Single
Is Tree
Is Submittable
Is Virtual
```

Они будут отдельными темами этого блока.

---

### 3. Добавь четыре поля

В таблице Fields создай строки в таком порядке.

#### Поле 1

```text
Label:      Subject
Fieldname:  subject
Field Type: Data
Mandatory:  включено
```

#### Поле 2

```text
Label:      Description
Fieldname:  description
Field Type: Small Text
```

#### Поле 3

```text
Label:      Status
Fieldname:  status
Field Type: Select
Options:
Open
In Progress
Done
```

Каждое значение `Options` должно находиться на отдельной строке.

#### Поле 4

```text
Label:      Due Date
Fieldname:  due_date
Field Type: Date
```

---

### 4. Задай человекочитаемый заголовок

В `View Settings` укажи:

```text
Title Field: subject
```

Не настраивай `Auto Name` и Naming Series. Они понадобятся в главе 06.

Не включай `Track Changes`: его практическая глава будет позже.

---

### 5. Сохрани DocType

Нажми:

```text
Save
```

После успешного сохранения Frappe должен создать рабочий Standard DocType `Request`.

---

### 6. Открой `Request`

Через поиск Desk введи:

```text
Request
```

Открой список `Request`.

Он пока пустой.

Это уже реальный List View нового DocType.

---

### 7. Создай первый Document

Нажми `Add Request` / `New` и заполни:

```text
Subject:      Проверить отчёт
Description: Первый учебный Request
Status:       Open
Due Date:     2026-09-02
```

Сохрани.

После Save это уже не новая форма, а конкретный Document `Request`.

Посмотри на адрес браузера и заголовок формы.

На этом этапе системный `name` ещё не имеет нашей будущей серии `REQ-...`.

---

### 8. Создай ещё два Documents

Создай:

```text
Subject:      Сверить данные
Description: Второй учебный Request
Status:       In Progress
Due Date:     2026-09-03
```

и:

```text
Subject:      Обновить инструкцию
Description: Третий учебный Request
Status:       Done
Due Date:     2026-09-04
```

В списке теперь должны быть минимум три Documents с разными Status.

---

## Проверь результат на диске

Открой второй терминал Debian.

Перейди в Bench:

```bash
cd ~/frappe/frappe16-course-bench
```

Проверь точный каталог DocType:

```bash
ls -la apps/training/training/training/doctype/request
```

Затем открой начало metadata-файла:

```bash
sed -n '1,180p' apps/training/training/training/doctype/request/request.json
```

Сейчас **не разбирай JSON как язык**.

Найди глазами знакомые значения:

```text
Request
Training
subject
status
due_date
```

Причинная связь:

```text
создали Standard DocType в Desk
→ Frappe экспортировал его metadata в App training
```

---

## Эксперимент

Открой один из созданных Request.

Измени только:

```text
Status: Open → In Progress
```

Нажми Save.

Вернись в List View и снова открой этот Document.

Убедись:

```text
DocType Request не создавался заново
→ изменилось только значение поля конкретного Document
```

---

## Намеренная ошибка

Создай ещё один новый `Request`.

Заполни:

```text
Subject:      оставить пустым
Description: Проверка Mandatory
Status:       Open
Due Date:     2026-09-05
```

Нажми Save.

Ожидаемый результат:

```text
Frappe отказывает в сохранении
→ Subject обязателен
```

Точный текст интерфейса может быть локализован, но причина должна быть однозначной: отсутствует Mandatory-поле `Subject`.

---

## Восстановление

В той же несохранённой форме введи:

```text
Subject: Проверка обязательного поля
```

Нажми Save.

Теперь Document должен сохраниться.

Итого на стенде будет минимум четыре `Request` Documents.

---

## Проверка себя

Ответь без подсказки.

1. Что было создано один раз: `Request` DocType или Request Document?
2. Что создавалось несколько раз?
3. Почему `Request` относится к Module `Training`?
4. Почему `Custom?` оставили выключенным?
5. Что доказало наличие `request.json`?
6. Почему первые Request пока не обязаны называться `REQ-...`?
7. Что именно запретило сохранить пустой `Subject`?

---

## Состояние стенда после лабораторной

Сохраняем:

```text
DocType: Request
Module: Training
Standard: да
Title Field: subject
Auto Name: пока не настроен
Track Changes: выключен
```

Поля:

```text
Subject      subject      Data        Mandatory
Description  description  Small Text
Status       status       Select      Open / In Progress / Done
Due Date     due_date     Date
```

Данные:

```text
минимум 4 Request Documents
как минимум один Open
как минимум один In Progress
как минимум один Done
```

Файл:

```text
apps/training/training/training/doctype/request/request.json
```

Это точное входное состояние [**главы 05**](../05_DOCFIELD.md).