# Лабораторная 12. List View, фильтры и сортировка

## Что уже должно быть готово

Лабораторная 11 завершена.

`Request` имеет рабочий двухвкладочный Form View.

Поля `Status`, `Priority` и `Due Date` уже включены в `In List View`.

---

## Что сейчас получим

Оставим на стенде:

```text
Status   → In List Filter
Priority → In List Filter
```

И создадим ровно шесть учебных Requests:

```text
C12-Open-High-1
C12-Open-High-2
C12-Open-Medium
C12-Progress-High
C12-Progress-Low
C12-Done-High
```

По ним результаты фильтров заранее известны.

---

## Часть 1. Подготовь metadata списка

### 1. Открой DocType `Request`

В Desk:

```text
поиск → DocType → Request
```

У поля `Status` включи:

```text
In List Filter = ✓
```

У поля `Priority` включи:

```text
In List Filter = ✓
```

Сохрани DocType.

Убедись, что итоговые свойства остаются:

```text
Status
→ In List View = ✓
→ In List Filter = ✓

Priority
→ In List View = ✓
→ In List Filter = ✓

Due Date
→ In List View = ✓
```

---

## Часть 2. Создай фиксированный набор данных

Создай следующие шесть `Request` Documents.

У всех оставляй остальные поля по умолчанию, если они не указаны.

### Request 1

```text
Subject:     C12-Open-High-1
Status:      Open
Priority:    High
Due Date:    2026-09-01
Responsible: Administrator
```

### Request 2

```text
Subject:     C12-Open-High-2
Status:      Open
Priority:    High
Due Date:    2026-09-05
Responsible: Administrator
```

### Request 3

```text
Subject:     C12-Open-Medium
Status:      Open
Priority:    Medium
Due Date:    2026-09-03
Responsible: Guest
```

### Request 4

```text
Subject:     C12-Progress-High
Status:      In Progress
Priority:    High
Due Date:    2026-09-02
Responsible: Administrator
```

### Request 5

```text
Subject:     C12-Progress-Low
Status:      In Progress
Priority:    Low
Due Date:    2026-09-04
Responsible: Guest
```

### Request 6

```text
Subject:     C12-Done-High
Status:      Done
Priority:    High
Due Date:    2026-09-06
Responsible: Administrator
```

Все шесть сохрани.

---

## Часть 3. Открой List View

Через поиск Desk открой:

```text
Request
```

Перейди именно в List View.

Убедись, что в строках видны как минимум:

```text
Status
Priority
Due Date
```

Точный порядок колонок может зависеть от ширины окна, но эти поля должны участвовать в List View metadata.

---

## Часть 4. Отдели учебные записи от старых

Добавь фильтр:

```text
Subject
Like
C12-%
```

`%` — wildcard оператора `Like`. В интерфейсе фильтров v16.32.0 для `Like` прямо показана подсказка `use % as wildcard`.

Теперь список должен содержать шесть созданных в этой лабораторной Documents.

Посчитай строки:

```text
6
```

---

## Часть 5. Проверь `AND`

К уже действующему `Subject Like C12-%` добавь:

```text
Status = Open
```

Ожидается:

```text
3 Documents
```

Добавь ещё:

```text
Priority = High
```

Теперь ожидается ровно:

```text
2 Documents
```

Это:

```text
C12-Open-High-1
C12-Open-High-2
```

---

## Часть 6. Проверь другой фильтр

Очисти фильтры и снова поставь:

```text
Subject Like C12-%
Status != Done
```

Ожидается:

```text
5 Documents
```

Единственная исключённая запись:

```text
C12-Done-High
```

---

## Часть 7. Сортировка

Оставь только:

```text
Subject Like C12-%
```

Отсортируй список:

```text
Due Date ASC
```

Порядок учебных записей по сроку должен быть:

```text
2026-09-01 → C12-Open-High-1
2026-09-02 → C12-Progress-High
2026-09-03 → C12-Open-Medium
2026-09-04 → C12-Progress-Low
2026-09-05 → C12-Open-High-2
2026-09-06 → C12-Done-High
```

Проверь: сортировка изменила порядок строк, но не значения `Due Date` в самих Documents.

---

## Часть 8. Выбор нескольких строк

Оставь фильтр:

```text
Subject Like C12-%
```

Выбери флажками любые две строки.

Посмотри, какие массовые действия показывает List View для `Administrator`.

Ничего разрушительного выполнять не нужно.

Цель:

```text
List View умеет работать не только с одной строкой
```

Permissions массовых действий подробно будут изучаться позже.

---

## Намеренная ошибка — пустая выборка

Очисти фильтры и установи:

```text
Subject Like C12-%
Status = Done
Priority = Low
```

По нашему фиксированному набору такой комбинации нет.

Ожидаемый результат:

```text
0 Documents
```

Это нормальный ответ фильтра.

Проверь через поиск/очистку условий: данные не удалены.

---

## Восстановление

Удалить все активные фильтры.

Верни сортировку к обычному состоянию списка либо оставь пользовательскую сортировку — она не является частью общей metadata.

Главное итоговое состояние:

```text
никаких активных фильтров не требуется
все 6 C12 Documents сохранены
Status и Priority остаются In List Filter
```

---

## Проверка себя

Ответь без подсказки.

1. Чем `In List View` отличается от `In List Filter`?
2. Что означает `%` в условии `Subject Like C12-%`?
3. Сколько C12-записей имеют `Status = Open`?
4. Сколько одновременно `Open` и `High`?
5. Почему `Status = Done AND Priority = Low` вернул 0 строк?
6. Изменяет ли сортировка `Due Date` в Documents?
7. Является ли Filter механизмом permissions?

---

## Состояние стенда после лабораторной

`Request` сохраняет layout лабораторной 11.

Metadata списка:

```text
Status
  In List View:   ✓
  In List Filter: ✓

Priority
  In List View:   ✓
  In List Filter: ✓

Due Date
  In List View:   ✓
```

На Site существуют ровно шесть учебных записей главы 12 с Subjects:

```text
C12-Open-High-1
C12-Open-High-2
C12-Open-Medium
C12-Progress-High
C12-Progress-Low
C12-Done-High
```

Они не удаляются и будут использованы в главе 13.

Это точное входное состояние [**главы 13**](../13_KANBAN_CALENDAR_GANTT_TREE.md).
