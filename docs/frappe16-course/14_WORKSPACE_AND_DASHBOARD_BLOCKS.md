# 14. Workspace, Shortcut, Quick List, Number Card и Chart

К этому моменту у `Request` уже есть рабочие Form, List, Kanban, Calendar и Gantt. `Training Category` имеет Tree View.

Теперь соберём из этих готовых экранов **одну рабочую точку входа** — Workspace `Training`.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

После лабораторной 13:

```text
Request Form View
Request List View
Kanban Board: Request Status
Calendar View: Request Course Calendar
Request Calendar/Gantt mapping
Training Category Tree
```

Есть шесть фиксированных C12 Requests и другие документы, накопленные раньше.

---

## Что такое Workspace

`Workspace` — страница внутри Desk, которая собирает уже существующие объекты и показатели.

Она не создаёт отдельную базу данных и не заменяет DocType.

Для курса итоговая страница будет выглядеть по смыслу так:

```text
Training

Shortcuts
[ Requests ] [ Request Kanban ] [ Training Categories ]

Open Requests
<число>

Recent Requests
<короткий список>

Requests by Status
<график Open / In Progress / Done>
```

Каждый блок использует существующие данные `Request`.

---

## Public Workspace

Workspace может быть личным или общим.

Нам нужен общий учебный Workspace, потому что в следующем блоке появятся отдельные пользователи и мы будем проверять, что интерфейс и permissions — разные вещи.

Поэтому создаём:

```text
Training
Public = yes
Module = Training
```

В v16 публичный Workspace редактирует пользователь с ролью `Workspace Manager`.

На чистом учебном Site `Administrator` получает системные роли и подходит для этой настройки.

---

## Shortcut

`Shortcut` — быстрый переход.

Для DocType у него можно задать View.

Например:

```text
Type: DocType
Link To: Request
DocType View: List
```

или:

```text
Type: DocType
Link To: Request
DocType View: Kanban
Kanban Board: Request Status
```

То есть Workspace не дублирует List/Kanban. Он даёт удобную кнопку к уже готовому экрану.

---

## Quick List

`Quick List` показывает небольшой список Documents прямо на Workspace.

Для курса используем:

```text
Label: Recent Requests
DocType: Request
```

Это обзор, а не полноценная замена List View.

Если нужно глубоко фильтровать, сортировать и массово работать со строками, пользователь переходит в List View.

---

## Number Card

`Number Card` показывает одно вычисленное число.

В `v16.32.0` для типа `Document Type` доступны штатные функции:

```text
Count
Sum
Average
Minimum
Maximum
```

Нам нужен самый простой вариант:

```text
Label:         Open Requests
Type:          Document Type
Document Type: Request
Function:      Count
Filter:        status = Open
```

Количество вычисляется по Documents `Request`.

Workspace только размещает уже созданный `Number Card`.

---

## Dashboard Chart

`Dashboard Chart` описывает расчёт и визуализацию графика.

Для курса создадим:

```text
Chart Name:          Requests by Status
Chart Type:          Group By
Document Type:       Request
Group By Based On:   status
Group By Type:       Count
Visual Type:         Bar
```

Получим группы:

```text
Open
In Progress
Done
```

и количество Requests в каждой.

Опять же:

```text
Dashboard Chart
→ считает и готовит данные

Workspace Chart block
→ размещает этот график на странице
```

---

## Почему Card и Chart обязательны уже здесь

Старый вариант курса откладывал их «если получится» до аналитики.

Для базовых `Count` и `Group By` это не нужно. Frappe v16.32.0 уже имеет эти режимы без Python и без Report.

Поэтому лабораторная проверяет весь базовый путь:

```text
Documents
→ Number Card / Dashboard Chart
→ Workspace
```

Позже аналитический блок покажет более сложные источники и Reports.

---

## Workspace не является permissions

Если на Workspace есть Shortcut к `Request`, это ещё не означает, что любой пользователь сможет открыть любой Request.

Слой выглядит так:

```text
Workspace
→ показывает точку входа

Permissions
→ решают, разрешена ли операция с данными
```

В этой главе мы не создаём искусственную permission-ошибку «на будущее». Реальные ограниченные пользователи появятся в блоке D, и там доступ будет проверяться непосредственно.

---

## Изменение layout Workspace

В Edit Mode блоки можно:

```text
добавлять
удалять
перемещать
менять размер
```

Это настройка рабочей страницы, а не изменение `Request`.

Если переставить Chart выше Quick List, Documents не изменятся.

---

## Канонический Workspace курса

После лабораторной оставляем один Workspace:

```text
Training
```

В нём обязательны:

```text
Shortcut: Requests
Shortcut: Request Kanban
Shortcut: Training Categories
Quick List: Recent Requests
Number Card: Open Requests
Chart: Requests by Status
```

Именно эта страница будет использоваться дальше.

---

## Намеренная ошибка в лабораторной

Чтобы ошибка была воспроизводимой, не будем придумывать будущую роль без permissions.

Вместо этого создадим `Number Card` с невозможным фильтром:

```text
status = DOES-NOT-EXIST
```

Он штатно покажет:

```text
0
```

После этого исправим фильтр на:

```text
status = Open
```

Так видно, что показатель зависит от настроенного запроса, а не «угадывает» нужное число.

---

## Что произойдёт в лабораторной

Ты:

1. создашь Public Workspace `Training`;
2. добавишь три точных Shortcut;
3. добавишь Quick List;
4. создашь `Open Requests` Number Card;
5. намеренно получишь 0 из-за неправильного фильтра и исправишь его;
6. создашь `Requests by Status` Dashboard Chart;
7. разместишь Card и Chart на Workspace;
8. проверишь переходы в List, Kanban и Tree.

---

## Что запомнить

1. Workspace собирает готовые части Desk на одной странице.
2. Shortcut — переход, Quick List — короткий список.
3. Number Card показывает один агрегат.
4. Dashboard Chart показывает распределение или динамику.
5. Workspace ссылается на Number Card и Dashboard Chart, а не заменяет их расчёт.
6. Workspace не является permission layer.

---

## Официальные источники и исходный код v16.32.0

- [Workspace](https://docs.frappe.io/framework/user/en/desk/workspace)
- [Workspace DocType](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/workspace/workspace.json)
- [Workspace controller](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/workspace/workspace.py)
- [Workspace Shortcut](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json)
- [Workspace Quick List](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/workspace_quick_list/workspace_quick_list.json)
- [Number Card](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/number_card/number_card.json)
- [Dashboard Chart](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/dashboard_chart/dashboard_chart.json)

Теперь выполни [**лабораторную 14**](labs/14_WORKSPACE_AND_DASHBOARD_BLOCKS_LAB.md).

После неё переходи к [**15. Customize Form**](15_CUSTOMIZE_FORM.md).
