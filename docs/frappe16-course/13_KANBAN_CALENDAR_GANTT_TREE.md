# 13. Kanban, Calendar, Gantt и Tree View

Один и тот же набор Documents можно показывать разными способами.

В этой главе мы не создаём четыре разных модели данных. Мы проверяем, **какие данные и какая metadata нужны каждому View**.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

После лабораторной 12 есть шесть фиксированных Requests:

```text
C12-Open-High-1
C12-Open-High-2
C12-Open-Medium
C12-Progress-High
C12-Progress-Low
C12-Done-High
```

У `Request` уже есть:

```text
Status   Select → Open / In Progress / Done
Due Date Date
```

Также существует настоящий Tree DocType:

```text
Training Category
```

с иерархией:

```text
Operations
└── Internal

Analytics
└── External
```

---

## Четыре View отвечают на разные вопросы

```text
Kanban
→ в каком состоянии находится Document?

Calendar
→ на какие даты он приходится?

Gantt
→ какой интервал времени занимает работа?

Tree
→ как Documents связаны отношением parent → child?
```

`Kanban`, `Calendar` и `Gantt` могут показывать обычные Requests.

`Tree` требует, чтобы сам DocType имел иерархическую модель (`Is Tree`).

---

# Kanban

## Что нужно Kanban

Kanban Board группирует Documents по значениям выбранного поля.

Для курса используем уже существующий:

```text
Request.status
```

Options:

```text
Open
In Progress
Done
```

Колонки доски будут соответствовать этим значениям.

То есть:

```text
Open        In Progress        Done
```

не являются отдельными DocTypes.

Это значения поля `Status` одного `Request`.

---

## Что происходит при переносе карточки

Если Request имеет:

```text
Status = Open
```

и карточку перетащили в:

```text
In Progress
```

Frappe меняет поле самого Document:

```text
Status = In Progress
```

Поэтому после переноса можно открыть Form View и увидеть новое значение.

Kanban здесь — другой интерфейс работы с теми же данными.

---

## Kanban не является Workflow

Перетаскивание между колонками само по себе не задаёт:

```text
кто имеет право на переход
какие переходы запрещены
кто должен согласовать
```

Это будет задачей Workflow и permissions в следующих блоках.

Сейчас Kanban только визуализирует и меняет значение `Status`.

---

# Calendar

## Почему одного `Due Date` недостаточно для полноценного интервала

`Due Date` отвечает на вопрос:

```text
к какому сроку выполнить Request?
```

Но Calendar и особенно Gantt удобнее на данных:

```text
Start Date
End Date
```

Поэтому в лабораторной 13 мы постоянно добавим:

```text
Start Date  start_date  Date
End Date    end_date    Date
```

`Due Date` при этом остаётся отдельным бизнес-полем срока.

---

## Named `Calendar View` в v16.32.0

В Framework есть системный DocType:

```text
Calendar View
```

У него в `v16.32.0` обязательны:

```text
Reference Document Type
Subject Field
Start Date Field
End Date Field
```

и есть:

```text
All Day
```

Для нашего курса создадим:

```text
Name:                    Request Course Calendar
Reference Document Type: Request
Subject Field:           subject
Start Date Field:        start_date
End Date Field:          end_date
All Day:                 enabled
```

Исходный код формы Calendar View предлагает для Start/End только поля типов:

```text
Date
Datetime
```

Это даст нам воспроизводимый опыт с неправильным типом `End Date` в лабораторной.

---

## Что Calendar View делает с mapping

Сопоставление будет таким:

```text
Request.subject    → заголовок события
Request.start_date → начало
Request.end_date   → конец
Request.name       → ID Document
```

Named Calendar хранит эту настройку как отдельный Document `Calendar View`.

После сохранения его кнопка `Show Calendar` открывает Calendar именно с этим mapping.

---

# Gantt

## Важный нюанс v16.32.0

Здесь нельзя притворяться, будто named `Calendar View` автоматически настраивает Gantt.

В исходном коде `v16.32.0` Gantt берёт mapping из:

```text
frappe.views.calendar["Request"]
```

то есть из стандартной calendar-конфигурации DocType.

Для Standard DocType Frappe загружает такую конфигурацию из файла:

```text
<doctype>_calendar.js
```

Для нашего `Request` точный путь:

```text
apps/training/training/training/doctype/request/request_calendar.js
```

Это подтверждается `FormMeta.add_code()` в исходниках v16.32.0.

---

## Почему в этой главе появится маленький JS-файл

Мы пока **не изучаем JavaScript**.

Здесь файл используется только как декларативное сопоставление полей представления — аналогично тому, как в Desk мы выбрали Subject/Start/End у `Calendar View`.

В лабораторной нужно скопировать ровно этот код:

```javascript
frappe.views.calendar["Request"] = {
    field_map: {
        start: "start_date",
        end: "end_date",
        id: "name",
        title: "subject",
        allDay: 1,
    },
};
```

Не нужно уметь его писать самостоятельно.

Смысл только такой:

```text
start_date → start
end_date   → end
subject    → title
name       → id
```

К полноценному Client Script мы придём только в главе 44.

---

## Что Gantt делает с этими полями

Исходный `gantt_view.js` v16.32.0 строит каждую полосу из:

```text
start = item[field_map.start]
end   = item[field_map.end]
```

При наличии Write permission изменение полосы на Gantt записывает новые значения обратно в эти поля Document.

Поэтому Gantt — не статичная картинка.

---

## `Is Calendar and Gantt`

У DocType есть флаг:

```text
Is Calendar and Gantt
```

Он включает соответствующие View в набор стандартных представлений DocType.

В лабораторной включим его для `Request`.

Но один флаг не определяет, какое поле является start/end. Mapping всё равно должен существовать.

---

# Tree

## Почему `Request` не превращаем в Tree

Tree — это не ещё один способ показать произвольные Requests.

Tree DocType должен иметь настоящую иерархию.

У нас уже есть правильный учебный объект:

```text
Training Category
```

Framework обслуживает у него:

```text
parent_training_category
is_group
lft
rgt
old_parent
```

В лабораторной мы просто снова откроем этот же Tree View и изменим положение одного узла.

Никакой второй Tree DocType не нужен.

---

## Каноническое состояние после главы

После лабораторной `Request` получит два новых постоянных поля:

```text
Start Date  start_date  Date
End Date    end_date    Date
```

Будут существовать:

```text
Kanban Board: Request Status
Calendar View: Request Course Calendar
Standard calendar config: request_calendar.js
```

И `Request` будет иметь:

```text
Is Calendar and Gantt = enabled
```

Этого достаточно, чтобы дальше Workspace мог ссылаться на готовые Views.

---

## Что произойдёт в лабораторной

Ты:

1. создашь Kanban Board по `Status`;
2. проверишь перенос карточки и изменение Request;
3. намеренно создашь `End Date` неверного типа `Data` и увидишь, что Calendar View не предлагает его как Date field;
4. исправишь `End Date` на `Date`;
5. создашь named `Calendar View` с точным mapping;
6. добавишь точный `request_calendar.js` для Standard Calendar/Gantt;
7. включишь `Is Calendar and Gantt`;
8. задашь интервалы трём C12 Requests;
9. откроешь Calendar и Gantt;
10. проверишь существующий Tree `Training Category`.

---

## Что запомнить

1. Kanban группирует Documents по значению поля; это не Workflow.
2. Calendar требует явного сопоставления title/start/end.
3. Named `Calendar View` и Standard calendar config — разные механизмы.
4. В v16.32.0 Gantt использует Standard `frappe.views.calendar[doctype]` mapping.
5. Gantt нужен интервал `start + end`, а не только один deadline.
6. Tree View требует настоящего Tree DocType.

---

## Официальные источники и исходный код v16.32.0

- [Calendar View DocType](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/calendar_view/calendar_view.json)
- [Calendar View form logic](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/calendar_view/calendar_view.js)
- [Calendar implementation](https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/calendar/calendar.js)
- [Gantt implementation](https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/views/gantt/gantt_view.js)
- [Form metadata asset loading](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/form/meta.py)
- [Kanban Board DocType](https://github.com/frappe/frappe/blob/v16.32.0/frappe/desk/doctype/kanban_board/kanban_board.json)

Теперь выполни [**лабораторную 13**](labs/13_KANBAN_CALENDAR_GANTT_TREE_LAB.md).

После неё переходи к [**14. Workspace и dashboard blocks**](14_WORKSPACE_AND_DASHBOARD_BLOCKS.md).
