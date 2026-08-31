# Лабораторная 14. Workspace и dashboard blocks

## Что уже должно быть готово

Лабораторная 13 завершена.

Существуют:

```text
Request
Kanban Board: Request Status
Calendar View: Request Course Calendar
Training Category Tree
```

У Request есть данные со статусами:

```text
Open
In Progress
Done
```

Работаем как:

```text
Administrator
```

---

## Что сейчас получим

Создадим и оставим:

```text
Workspace: Training
Public: yes
```

Внутри него обязательны:

```text
Shortcut → Request List
Shortcut → Request Kanban / Request Status
Shortcut → Training Category Tree
Quick List → Request
Number Card → Open Requests
Chart → Requests by Status
```

---

# Часть 1. Создай Public Workspace

## 1. Открой создание Workspace

Через Desktop/Workspace navigation создай новый Workspace.

В диалоге задай:

```text
Title / Name: Training
Public:       ✓
```

После создания открой Workspace `Training`.

Если он ещё не показан на Desktop/Sidebar автоматически, открой его запись `Workspace` и используй штатное действие:

```text
Add to Desktop
```

Для Public Workspace редактирование выполняем как `Administrator` с системными ролями.

---

## 2. Перейди в Edit Mode

На странице `Training` включи:

```text
Edit
```

Дальнейшие блоки добавляй через редактор Workspace.

---

# Часть 2. Добавь Shortcuts

## 3. Shortcut `Requests`

Добавь Shortcut:

```text
Label:        Requests
Type:         DocType
Link To:      Request
DocType View: List
```

---

## 4. Shortcut `Request Kanban`

Добавь:

```text
Label:        Request Kanban
Type:         DocType
Link To:      Request
DocType View: Kanban
Kanban Board: Request Status
```

---

## 5. Shortcut `Training Categories`

Добавь:

```text
Label:        Training Categories
Type:         DocType
Link To:      Training Category
DocType View: Tree
```

Сохрани Workspace.

Проверь каждый Shortcut:

```text
Requests            → Request List
Request Kanban      → Kanban Board Request Status
Training Categories → Training Category Tree
```

Вернись в `Training`.

---

# Часть 3. Quick List

## 6. Добавь `Recent Requests`

В Edit Mode добавь Quick List:

```text
Label:   Recent Requests
DocType: Request
```

Фильтр оставь пустым.

Сохрани Workspace.

Ожидаемый результат:

```text
на странице виден короткий список Request Documents
```

Quick List не обязан показывать все Requests — это компактный блок.

---

# Часть 4. Number Card

## 7. Создай `Open Requests`

Через поиск Desk открой:

```text
Number Card
```

Создай новый документ:

```text
Label:                 Open Requests
Type:                  Document Type
Document Type:         Request
Function:              Count
Is Public:             ✓
Show Percentage Stats: выключено
```

### Сначала намеренно задай неверный фильтр

В Filters задай:

```text
Request
name
=
__NO_SUCH_REQUEST__
```

Сохрани Number Card.

Открой/обнови его preview, если он показан на форме.

Ожидаемый результат:

```text
0
```

Причина однозначна: Request с таким системным `name` не существует.

---

## 8. Восстанови правильный фильтр

Удалить фильтр по `name`.

Добавь:

```text
Request
status
=
Open
```

Сохрани.

Теперь Number Card должен показывать фактическое количество всех Requests со статусом `Open` на текущем Site.

Число может быть больше трёх, потому что в предыдущих главах уже создавались другие Requests. Это нормально: здесь мы специально считаем весь DocType, а не только C12-набор.

---

## 9. Добавь Card на Workspace

Вернись в:

```text
Training → Edit
```

Добавь блок `Number Card` и выбери:

```text
Open Requests
```

Сохрани.

На Workspace должно появиться одно число.

---

# Часть 5. Dashboard Chart

## 10. Создай `Requests by Status`

Через поиск Desk открой:

```text
Dashboard Chart
```

Создай:

```text
Chart Name:        Requests by Status
Chart Type:        Group By
Document Type:     Request
Group By Based On: status
Group By Type:     Count
Number of Groups:  10
Type:              Bar
Is Public:         ✓
```

Filters оставь без ограничений. Если форма показывает `Filters JSON`, итоговое значение пустого набора фильтров должно быть:

```json
[]
```

Сохрани Dashboard Chart.

Ожидаемый смысл результата:

```text
Open        → count
In Progress → count
Done        → count
```

Конкретные числа зависят от всех Request Documents, накопленных в курсе.

---

## 11. Добавь Chart на Workspace

Вернись в:

```text
Training → Edit
```

Добавь Chart block:

```text
Requests by Status
```

Сохрани.

---

# Часть 6. Приведи Workspace к финальному виду

Расположи блоки в понятном порядке:

```text
Shortcuts
→ Requests
→ Request Kanban
→ Training Categories

Open Requests

Recent Requests

Requests by Status
```

Точная ширина блоков не является частью модели курса. Важно, чтобы все шесть элементов существовали и были видимы.

Выйди из Edit Mode.

---

## Проверь весь маршрут

На `Training` последовательно:

1. нажми `Requests` → получи List View;
2. вернись;
3. нажми `Request Kanban` → получи доску `Request Status`;
4. вернись;
5. нажми `Training Categories` → получи Tree;
6. вернись;
7. открой один Request из `Recent Requests`;
8. вернись;
9. сравни `Open Requests` с фильтром `Status = Open` в Request List;
10. убедись, что Chart содержит группы по `Status`.

---

## Проверка себя

Ответь без подсказки.

1. Что делает Shortcut?
2. Чем Quick List отличается от полноценного List View?
3. Где рассчитывается число `Open Requests`?
4. Что делает Workspace с Number Card?
5. По какому полю группируется `Requests by Status`?
6. Почему первый Number Card показал 0?
7. Даёт ли наличие Shortcut право читать любой Request?

---

## Состояние стенда после лабораторной

Существует Public Workspace:

```text
Training
```

Он содержит:

```text
Shortcut: Requests
  Type: DocType
  Link To: Request
  View: List

Shortcut: Request Kanban
  Type: DocType
  Link To: Request
  View: Kanban
  Board: Request Status

Shortcut: Training Categories
  Type: DocType
  Link To: Training Category
  View: Tree

Quick List: Recent Requests
  DocType: Request

Number Card: Open Requests
  Type: Document Type
  Document Type: Request
  Function: Count
  Filter: status = Open
  Is Public: ✓

Dashboard Chart: Requests by Status
  Chart Type: Group By
  Document Type: Request
  Group By Based On: status
  Group By Type: Count
  Visual Type: Bar
  Is Public: ✓
```

Неверный фильтр `name = __NO_SUCH_REQUEST__` полностью удалён.

Это точное входное состояние [**главы 15**](../15_CUSTOMIZE_FORM.md).
