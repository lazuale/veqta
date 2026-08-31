# Лабораторная 11. Собираем рабочую Form View `Request`

## Что уже должно быть готово

Блок B завершён.

Стенд:

```text
Bench:          ~/frappe/frappe16-course-bench
Site:           learn.localhost
Apps installed: frappe, training
Module:         Training
Developer Mode: включён
User:           Administrator
```

`Request` уже содержит:

```text
Subject
Description
Status
Due Date
Priority
Is Urgent
Estimate Hours
Notes
Reference File
Responsible
Responsible Name
Items
Watchers
```

Новые Request получают `name` вида:

```text
REQ-2026-.....
```

---

## Что сейчас получим

После лабораторной `Request` будет иметь один точный layout:

```text
Tab: Main

  Section: General
    Subject      | Priority
    Status       | Due Date
    Is Urgent

  Section: Responsibility
    Responsible  | Responsible Name
    Watchers

  Section: Urgent Details
    Display Depends On: eval:doc.is_urgent
    Estimate Hours

Tab: Details

  Section: Description
    Description
    Notes

  Section: Files
    Reference File

  Section: Items
    Items
```

Никакой JavaScript или Python не нужен.

---

## Сделай руками

### 1. Открой Standard DocType `Request`

В Desk:

```text
поиск → DocType → Request
```

Работаем именно с Standard metadata `Request`, а не с `Customize Form`.

---

### 2. Добавь первый Tab Break

В начало набора Fields добавь layout-поле:

```text
Label:      Main
Field Type: Tab Break
```

Fieldname Frappe может сформировать автоматически.

---

### 3. Создай Section `General`

Сразу после `Main` добавь:

```text
Label:      General
Field Type: Section Break
```

Перемести поля так, чтобы внутри секции сначала шли:

```text
Subject
Status
Is Urgent
```

Затем добавь `Column Break` после `Is Urgent` не нужно — нам нужен точный двухколоночный порядок, поэтому расположи строки так:

```text
General Section
├── Subject
├── Status
├── Is Urgent
├── Column Break
├── Priority
└── Due Date
```

В Form View это даст две колонки:

```text
Subject      | Priority
Status       | Due Date
Is Urgent    |
```

---

### 4. Создай Section `Responsibility`

После `Due Date` добавь:

```text
Label:      Responsibility
Field Type: Section Break
```

В первой колонке размести:

```text
Responsible
Watchers
```

Затем `Column Break`, после него:

```text
Responsible Name
```

Итог:

```text
Responsible  | Responsible Name
Watchers     |
```

---

### 5. Создай условную Section `Urgent Details`

После блока Responsibility добавь:

```text
Label:      Urgent Details
Field Type: Section Break
Display Depends On: eval:doc.is_urgent
```

Внутри неё оставь:

```text
Estimate Hours
```

Смысл:

```text
Is Urgent = выключено
→ Urgent Details скрыта

Is Urgent = включено
→ Urgent Details появляется
```

---

### 6. Создай вкладку `Details`

После `Estimate Hours` добавь:

```text
Label:      Details
Field Type: Tab Break
```

---

### 7. Разложи оставшиеся поля

В `Details` создай:

```text
Section Break: Description
```

Внутри:

```text
Description
Notes
```

Затем:

```text
Section Break: Files
Reference File
```

Затем:

```text
Section Break: Items
Items
```

Сохрани DocType.

---

## Проверь рабочую форму

Открой любой существующий Request серии:

```text
REQ-2026-.....
```

Проверь наличие вкладок:

```text
Main
Details
```

На `Main` должны быть:

```text
General
Responsibility
```

При выключенном `Is Urgent` секция:

```text
Urgent Details
```

не должна отображаться.

Включи:

```text
Is Urgent = ✓
```

Секция должна появиться, а внутри неё:

```text
Estimate Hours
```

Выключи `Is Urgent` обратно и убедись, что секция снова исчезает.

---

## Проверь, что layout не сломал поведение полей

В том же Request:

1. выбери `Responsible = Administrator`;
2. проверь, что `Responsible Name` автоматически заполняется;
3. открой `Details`;
4. убедись, что `Items` по-прежнему отображается как Child Table;
5. убедись, что `Watchers` по-прежнему работает как Table MultiSelect.

То есть:

```text
переставили поля
≠ изменили их тип или смысл
```

---

## Намеренная ошибка — спрячем Mandatory `Subject`

Сейчас сделаем гарантированно плохую конфигурацию и сразу её исправим.

В DocType `Request` у Section Break `General` временно установи:

```text
Display Depends On: eval:doc.is_urgent
```

Сохрани DocType.

Создай новый Request.

По умолчанию:

```text
Is Urgent = 0
```

Поэтому вся Section `General`, включая Mandatory-поле `Subject`, скрыта.

Попробуй сохранить новый Request.

Ожидаемый результат:

```text
Frappe не сохраняет Document
→ обязательный Subject пуст
```

Это не «поломка Frappe». Мы сами сделали обязательное поле недоступным пользователю неправильным layout-условием.

---

## Восстановление

Вернись в DocType `Request`.

У Section `General` полностью очисти:

```text
Display Depends On
```

У Section `Urgent Details` оставь правильное условие:

```text
eval:doc.is_urgent
```

Сохрани DocType.

Вернись к новой форме Request.

Теперь `Subject` снова виден независимо от `Is Urgent`.

Заполни:

```text
Subject: Проверка восстановленной формы
Status:  Open
```

Сохрани Document.

---

## Проверка себя

Ответь без подсказки.

1. Что создаёт новую вкладку формы?
2. Что создаёт новый смысловой блок?
3. Что делит секцию на колонки?
4. Какое условие показывает `Urgent Details`?
5. Почему неправильное условие на `General` заблокировало Save?
6. Изменился ли тип `Responsible` после переноса в другую секцию?
7. Изменился ли способ хранения `Items` после переноса во вкладку `Details`?

---

## Состояние стенда после лабораторной

Модель данных блока B сохранена.

`Request` имеет точный Standard layout:

```text
Main
├── General
│   ├── Subject | Priority
│   ├── Status  | Due Date
│   └── Is Urgent
├── Responsibility
│   ├── Responsible | Responsible Name
│   └── Watchers
└── Urgent Details
    ├── Display Depends On: eval:doc.is_urgent
    └── Estimate Hours

Details
├── Description
│   ├── Description
│   └── Notes
├── Files
│   └── Reference File
└── Items
    └── Items
```

У `General` нет `Display Depends On`.

Новый проверочный Request сохранён.

Это точное входное состояние [**главы 12**](../12_LIST_VIEW_AND_FILTERS.md).
