# Лабораторная 16. Выбираем минимальный штатный UI

## Что уже должно быть готово

Лабораторная 15 завершена.

На стенде существуют рабочие:

```text
Request Form
Request List
Request Status Kanban
Request Calendar
Request Gantt
Training Category Tree
Training Workspace
Training Settings
```

Также остаются:

```text
Request-custom_local_note
Request-estimate_hours-description
```

В этой лабораторной **не создаём Desk Page и не пишем JavaScript**.

---

## Что сейчас получим

После лабораторной стенд должен остаться в том же функциональном состоянии.

Главный результат — ты должен уметь для требования выбрать:

```text
Form
List
Kanban
Calendar
Gantt
Tree
Workspace
Single Form
Page
```

и не создавать Page раньше необходимости.

---

# Часть 1. Пройди реальные экраны

## 1. Form View

Открой один существующий Request.

Зафиксируй:

```text
Экран: Form View
Объект: один Request Document
Назначение: просмотр и редактирование одной записи
```

---

## 2. List View

Перейди в Request List.

Зафиксируй:

```text
Экран: List View
Объект: много Request Documents
Назначение: поиск, фильтрация, сортировка, выбор строк
```

---

## 3. Kanban

Открой:

```text
Request Status
```

Зафиксируй:

```text
Экран: Kanban
Объект: те же Request Documents
Поле колонок: status
```

---

## 4. Calendar

Открой Request Calendar.

Зафиксируй:

```text
Экран: Calendar
Поля времени: start_date / end_date
Заголовок: subject
```

---

## 5. Gantt

Открой Request Gantt.

Зафиксируй:

```text
Экран: Gantt
Объект: те же Request Documents
Интервал: start_date → end_date
```

---

## 6. Tree

Открой:

```text
Training Category
```

в Tree View.

Зафиксируй:

```text
Экран: Tree
Модель: реальная parent-child иерархия Training Category
```

---

## 7. Workspace

Открой:

```text
Training
```

Зафиксируй:

```text
Экран: Workspace
Содержит: Shortcuts / Quick List / Number Card / Chart
Назначение: рабочая точка входа
```

---

## 8. Single Form

Открой:

```text
Training Settings
```

Зафиксируй:

```text
Экран: Form View Single DocType
Экземпляров: один на Site
Назначение: глобальная учебная настройка
```

---

# Часть 2. Выбери UI для конкретных требований

Для каждого требования сначала ответь сам, затем сравни с ответом ниже.

### Требование A

```text
Открыть один Request, поменять Priority и Responsible.
```

Ответ:

```text
Form View
```

### Требование B

```text
Найти все Open Requests с Priority = High.
```

Ответ:

```text
List View + filters
```

### Требование C

```text
Видеть Requests по Status и переносить их Open → In Progress → Done.
```

Ответ:

```text
Kanban
```

### Требование D

```text
Посмотреть, какие Requests приходятся на даты сентября.
```

Ответ:

```text
Calendar
```

### Требование E

```text
Сравнить длительность нескольких Requests на общей временной шкале.
```

Ответ:

```text
Gantt
```

### Требование F

```text
Работать с иерархией категорий.
```

Ответ:

```text
Tree
```

### Требование G

```text
На одном стартовом экране дать ссылки на Request, короткий список, счётчик и график.
```

Ответ:

```text
Workspace
```

### Требование H

```text
Хранить одну общую настройку курса для всего Site.
```

Ответ:

```text
Single DocType + Form View
```

### Требование I

```text
Сделать отдельный операторский экран:
- собственная панель фильтров;
- две независимые интерактивные таблицы;
- несколько несвязанных источников данных;
- собственные действия над выбранными строками;
- взаимное обновление разных областей экрана.
```

Ответ:

```text
кандидат на Desk Page
```

Page сейчас не создаём: для осмысленной реализации ещё не изучены нужные инструменты разработки.

---

# Часть 3. Реши простую UI-задачу без Page

## 9. Требование

Представим временное требование:

```text
Due Date нужно показывать только пока Request не Done.
```

Это относится к одному полю одного Document.

Значит первым механизмом должен быть:

```text
DocField → Display Depends On
```

а не Page.

---

## 10. Намеренно задай условие наоборот

Открой:

```text
DocType → Request
```

У поля:

```text
Due Date
fieldname = due_date
```

временно задай:

```text
Display Depends On: eval:doc.status=="Done"
```

Сохрани DocType.

---

## 11. Увидь неправильное поведение

Открой:

```text
C12-Open-High-1
```

У него:

```text
Status = Open
```

При ошибочном условии `Due Date` скрыта.

Теперь открой:

```text
C12-Done-High
```

У него:

```text
Status = Done
```

`Due Date` видна.

Получилось ровно **наоборот** относительно требования.

Framework выполнил metadata правильно — ошибку допустили мы в условии.

---

## 12. Исправь условие

Вернись в `DocType → Request`.

Исправь на:

```text
Display Depends On: eval:doc.status!="Done"
```

Сохрани.

Проверь снова:

```text
C12-Open-High-1
→ Due Date видна

C12-Done-High
→ Due Date скрыта
```

Теперь требование реализовано правильно без Page и без Client Script.

---

# Часть 4. Полностью восстанови каноническую модель

Это условие было только учебным опытом. В дальнейших главах `Due Date` должно оставаться обычным полем независимо от Status.

Вернись в:

```text
DocType → Request
```

У `Due Date` полностью очисти:

```text
Display Depends On
```

Сохрани.

Открой оба документа:

```text
C12-Open-High-1
C12-Done-High
```

В обоих `Due Date` снова должна быть видна.

---

## Проверка себя

Ответь без подсказки.

1. Какой экран первым проверяешь для редактирования одного Document?
2. Какой — для фильтрации множества Documents?
3. В чём отличие Workspace от Page?
4. Почему Tree нельзя включать только ради красивого вида обычного списка?
5. Почему требование про `Due Date` не требовало Page?
6. Кто допустил ошибку при условии `status == Done`: Framework или автор metadata?
7. Для какого требования из части 2 Page действительно выглядит оправданным?
8. Создавали ли мы Page в блоке C?

---

## Состояние стенда после лабораторной

Новых Page не создано.

Экспериментальное условие полностью удалено:

```text
Request.due_date
Display Depends On: пусто
```

Сохраняется всё состояние предыдущих лабораторных блока C:

```text
Request двухвкладочный Form layout
Status / Priority In List Filter
6 C12 Requests
Start Date / End Date
Kanban Board Request Status
Calendar View Request Course Calendar
request_calendar.js
Is Calendar and Gantt = ✓
Training Category Tree
Public Workspace Training
Number Card Open Requests
Dashboard Chart Requests by Status
Custom Field Request-custom_local_note
Property Setter Request-estimate_hours-description
```

Это точное входное состояние следующего блока: [**17. User, System User, Website User и Role**](../17_USERS_AND_ROLES.md).
