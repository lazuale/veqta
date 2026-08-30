# 13. Kanban, Calendar, Gantt и Tree View

Во Frappe один и тот же набор документов можно смотреть по-разному.

Иногда нужен обычный список. Иногда удобнее доска по статусам. Иногда важны даты. Иногда — иерархия.

Но здесь есть важная граница:

- **Kanban, Calendar и Gantt** в основном показывают те же документы под другим углом;
- **Tree View** требует, чтобы сам DocType был иерархическим.

То есть Tree — это уже не просто «ещё один красивый экран».

Проверено: **2026-08-30**.

## 1. Сначала один простой пример

Представим DocType `Activity`:

```text
Activity
├── Subject
├── Stage
├── Starts On
└── Ends On
```

`Stage` — поле `Select`:

```text
New
In Progress
Done
```

А даты выглядят так:

```text
ACT-0001   Проверить отчёт     New          01.09 → 02.09
ACT-0002   Подготовить акт     In Progress  01.09 → 05.09
ACT-0003   Закрыть сверку      Done         28.08 → 30.08
```

В List View это обычные строки.

Но эти же данные можно показать иначе.

## 2. Четыре представления — четыре разных вопроса

| View | На какой вопрос отвечает |
|---|---|
| **Kanban** | На каком этапе находится документ? |
| **Calendar** | На какую дату он приходится? |
| **Gantt** | Сколько длится работа и как она расположена на шкале времени? |
| **Tree** | Кто чей родитель и как устроена иерархия? |

Это хороший способ выбирать представление: не по внешнему виду, а по вопросу, на который оно должно отвечать.

---

# Часть 1. Kanban

## 3. Что такое Kanban во Frappe

Kanban показывает документы карточками, разложенными по колонкам.

Для нашего `Activity`:

```text
New              In Progress          Done

ACT-0001         ACT-0002             ACT-0003
Проверить отчёт  Подготовить акт      Закрыть сверку
```

Самое важное: колонка — это не отдельная сущность.

Она соответствует значению выбранного поля документа.

Например:

```text
Stage = New
```

значит карточка находится в колонке `New`.

## 4. Что нужно для Kanban

В обычном сценарии нужен хотя бы один `Select` field.

Например:

```text
Field Type: Select
Label: Stage
Fieldname: stage
Options:
New
In Progress
Done
```

При создании Kanban Board Frappe спрашивает:

```text
Columns based on: Stage
```

И превращает options этого `Select` в колонки.

```text
Stage options
     ↓
New | In Progress | Done
     ↓
Kanban columns
```

## 5. Что происходит при перетаскивании карточки

Допустим:

```text
ACT-0001
Stage = New
```

Пользователь перетащил карточку:

```text
New → In Progress
```

Frappe меняет значение поля документа:

```text
Stage = In Progress
```

Это не только визуальное перемещение карточки.

Значение сохраняется в самом Document.

В серверном коде v16 Kanban при переносе между колонками вызывает обновление поля, выбранного как `field_name` доски.

## 6. Kanban Board — отдельная настройка

Один DocType может иметь несколько досок.

Например:

```text
Activity
├── Все работы
├── Только срочные
└── Работы отдела A
```

У каждой доски могут быть свои:

- имя;
- filters;
- поле колонок;
- набор полей на карточке;
- порядок карточек;
- private/public режим.

То есть:

```text
Activity documents
        ↓
несколько Kanban Board
        ↓
разные способы смотреть те же данные
```

## 7. Kanban и Workflow — не одно и то же

Это очень легко перепутать.

Kanban отвечает за представление документов по значению поля.

Workflow отвечает за разрешённые переходы, роли и правила процесса.

Например:

```text
Kanban:
Stage = New / In Progress / Done
```

не означает автоматически:

```text
New можно перевести только в In Progress
Done может поставить только Manager
```

Такие правила относятся уже к Workflow или другой бизнес-логике.

Поэтому не следует считать Kanban полноценным workflow engine только потому, что карточки можно таскать между колонками.

## 8. Когда Kanban удобен

Kanban хорошо подходит, если:

- документов много;
- у них есть понятное дискретное состояние;
- важно видеть распределение по этапам;
- карточку удобно двигать между этими этапами.

Примеры:

```text
Заявки по статусу
Кандидаты по этапу отбора
Обращения по стадии обработки
Материалы по состоянию проверки
```

## 9. Когда Kanban не нужен

Если основная задача — сравнивать десяток колонок, суммы, даты и реквизиты, обычный List или Report часто удобнее.

Kanban особенно хорош для **состояния**, но не обязан заменять таблицу.

---

# Часть 2. Calendar

## 10. Что такое Calendar View

Calendar раскладывает документы по датам.

Наши `Activity` могут выглядеть так:

```text
September 2026

1 Sep
├── Проверить отчёт
└── Подготовить акт

2 Sep
└── Проверить отчёт

...

5 Sep
└── Подготовить акт
```

Calendar отвечает прежде всего на вопрос:

> когда это происходит?

## 11. Одних Date-полей недостаточно

Frappe должен понимать:

```text
какое поле = начало
какое поле = конец
какое поле = заголовок события
```

Для `Activity` это может быть:

```text
Subject  → title
Starts On → start
Ends On   → end
```

Это называется `field_map` — сопоставление полей документа с тем, что ожидает Calendar.

## 12. Флаг Is Calendar and Gantt

В metadata DocType v16 есть штатный флаг:

```text
Is Calendar and Gantt
```

Его описание прямо говорит:

```text
Enables Calendar and Gantt views.
```

Он сообщает Frappe, что для этого DocType предполагаются такие представления.

Но сам по себе флаг не объясняет, **какие именно поля являются start/end/title**.

Для этого всё равно нужна конфигурация отображения.

## 13. Calendar View как настройка

В Framework есть отдельный системный DocType:

```text
Calendar View
```

Он содержит простую настройку:

```text
Reference Document Type
Subject Field
Start Date Field
End Date Field
All Day
```

Например:

```text
Reference Document Type: Activity
Subject Field: subject
Start Date Field: starts_on
End Date Field: ends_on
All Day: 0
```

Для новичка это самый понятный способ увидеть саму идею mapping:

```text
Activity.subject   → текст события
Activity.starts_on → начало
Activity.ends_on   → конец
```

Frappe при выборе полей Start/End предлагает поля типов `Date` и `Datetime`.

## 14. Standard Calendar configuration

Для стандартного DocType внутри собственного App calendar-конфигурация обычно задаётся в файле вида:

```text
activity_calendar.js
```

Смысл выглядит примерно так:

```javascript
frappe.views.calendar["Activity"] = {
    field_map: {
        start: "starts_on",
        end: "ends_on",
        id: "name",
        title: "subject"
    }
};
```

Пока этот код не нужно запоминать.

Важно понять идею:

```text
Calendar не угадывает смысл полей.
Ему указывают mapping.
```

К calendar JS мы вернёмся в блоке про разработку.

## 15. Что можно делать в Calendar

В стандартном Calendar v16 пользователь может:

- открыть документ кликом;
- смотреть месяц, неделю и день;
- создавать документ через выбранный временной диапазон;
- при наличии write permission переносить событие;
- изменять его длительность растягиванием.

При переносе Frappe обновляет поля start/end документа.

То есть Calendar тоже может быть не только чтением.

---

# Часть 3. Gantt

## 16. Что такое Gantt View

Gantt показывает документы как полосы на временной шкале.

Например:

```text
             1 Sep   2 Sep   3 Sep   4 Sep   5 Sep

Проверить отчёт
             ████████

Подготовить акт
             ████████████████████████████████
```

Calendar отвечает:

> что происходит в конкретный день?

Gantt отвечает:

> сколько длится работа и как разные работы расположены во времени?

## 17. Gantt использует те же даты начала и конца

В Frappe v16 Gantt берёт `field_map` из calendar configuration.

Минимально ему нужны:

```text
start
end
```

Например:

```text
starts_on
ends_on
```

Поэтому Calendar и Gantt во Frappe связаны между собой сильнее, чем может показаться по интерфейсу.

## 18. Progress

Дополнительно можно указать поле прогресса.

Например:

```text
Progress = 40
```

На Gantt-полосе это может выглядеть как выполнение 40% работы.

Conceptually:

```text
Start Date + End Date + Progress
              ↓
          Gantt bar
```

## 19. Изменение дат прямо на Gantt

В реализации v16 при наличии write permission изменение положения или длины Gantt bar обновляет start/end поля документа.

То есть можно изменить:

```text
01.09 → 05.09
```

на:

```text
02.09 → 06.09
```

не открывая Form View.

Если настроено обычное поле progress, его изменение на диаграмме также может сохраниться в документ.

## 20. Дополнительные возможности Gantt

Текущая реализация v16 также знает некоторые специальные данные:

```text
progress
color
is_milestone
depends_on_tasks
```

Но новичку не нужно строить вокруг них модель только ради того, чтобы «использовать всё».

Начинать лучше с простого:

```text
Subject
Start
End
```

а дополнительные поля добавлять только если они действительно нужны предметной области.

## 21. Когда Gantt полезен

Он хорош для работ, где имеет значение **интервал времени**:

```text
Подготовка документа   01.09 → 03.09
Проверка               03.09 → 05.09
Согласование           05.09 → 08.09
```

Если у документа есть только одна дата вроде:

```text
Deadline = 05.09
```

Calendar часто будет естественнее.

---

# Часть 4. Tree View

## 22. Tree отличается от остальных

Возьмём уже другой DocType — `Category`.

Нам нужна структура:

```text
Все категории
├── Оборудование
│   ├── Компьютеры
│   └── Принтеры
└── Материалы
    ├── Бумага
    └── Картриджи
```

Это не просто способ нарисовать обычные независимые записи.

Каждая категория действительно имеет место в иерархии.

## 23. Is Tree

Чтобы DocType был иерархическим, включается:

```text
Is Tree = ✓
```

Frappe использует Nested Set model.

У записи появляется родитель, например:

```text
Принтеры
Parent Category = Оборудование
```

И Framework поддерживает служебные `lft/rgt` значения для работы с деревом.

Эту механику мы уже разбирали в главе 09.

## 24. Tree View строится из реальной структуры данных

Для обычного списка:

```text
Оборудование
Компьютеры
Принтеры
Материалы
Бумага
```

непонятно, кто кому подчиняется.

Tree показывает настоящую структуру:

```text
Оборудование
├── Компьютеры
└── Принтеры
```

То есть:

```text
Tree View
   ↑
parent-child hierarchy
   ↑
Is Tree DocType
```

## 25. Tree нельзя включать «просто для красоты»

Если документы по смыслу независимы:

```text
Request A
Request B
Request C
```

не нужно делать DocType Tree только потому, что дерево выглядит удобно.

Tree оправдан, когда сама предметная область иерархична:

```text
категории
подразделения
места хранения
структура меню
классификатор
```

Это архитектурное решение о модели данных, а не настройка внешнего вида.

## 26. Настройка Tree View кодом

Если стандартного Tree View недостаточно, для standard DocType можно использовать файл:

```text
{doctype}_tree.js
```

Там можно настроить, например:

- title;
- breadcrumbs;
- filters;
- получение дочерних узлов;
- добавление узлов;
- дополнительные действия.

Но само дерево работает благодаря `Is Tree`; писать собственный tree UI с нуля для базового сценария не требуется.

---

# Часть 5. Что Frappe меняет на самом деле

## 27. Сравним четыре View

| View | Нужна специальная модель? | Основная опора |
|---|---|---|
| Kanban | нет | `Select` field + Kanban Board |
| Calendar | нет | Date/Datetime fields + mapping |
| Gantt | нет | start/end mapping, обычно calendar config |
| Tree | **да** | `Is Tree` + parent hierarchy |

Это главное различие всей главы.

## 28. Один Document — несколько View

Для обычного `Activity` одна запись может одновременно существовать как:

```text
ACT-0001
```

и быть показана:

```text
List      → строка
Form      → карточка документа
Kanban    → карточка в колонке New
Calendar  → событие 1–2 сентября
Gantt     → полоса 1–2 сентября
```

Это всё **один и тот же Document**.

Не пять копий данных.

Поэтому изменение значения через один View видно в остальных после обновления данных.

## 29. View не должен определять модель

Плохая последовательность:

```text
Хочу красивый Gantt
        ↓
добавлю десять искусственных полей
        ↓
сломаю модель данных
```

Лучше наоборот:

```text
Какие данные реально существуют?
        ↓
Какой вопрос нужно задать этим данным?
        ↓
Какой View лучше отвечает на этот вопрос?
```

Например:

- есть стадия → Kanban может быть полезен;
- есть начало и конец → Gantt может быть полезен;
- есть дата события → Calendar может быть полезен;
- есть настоящая иерархия → Tree может быть полезен.

---

# Часть 6. Где настройка, а где код

## 30. Kanban

Базовый Kanban в значительной степени штатный:

```text
Select field
    ↓
Create Kanban Board
    ↓
выбрать Columns based on
```

Для обычной доски отдельный frontend не нужен.

## 31. Calendar

Есть два уровня:

```text
Calendar View record
```

для mapping полей и:

```text
{doctype}_calendar.js
```

для стандартной/расширенной calendar-конфигурации App.

Второй вариант уже относится к коду приложения.

## 32. Gantt

Gantt v16 использует calendar settings DocType и его `field_map`.

Поэтому полноценная standard-конфигурация Gantt обычно появляется на уровне App calendar JS.

Это хороший пример границы:

```text
Framework умеет Gantt штатно
```

не означает:

```text
Frappe может сам угадать, какие поля любого DocType означают Start и End.
```

## 33. Tree

Базовая иерархия задаётся metadata:

```text
Is Tree
Parent Field
```

Дополнительное поведение Tree — уже `{doctype}_tree.js`.

---

# Часть 7. Простая практика

## 34. Практика с Kanban

Создай учебный DocType `Activity` с полями:

```text
Subject   Data
Stage     Select
Starts On Date
Ends On   Date
```

Для `Stage`:

```text
New
In Progress
Done
```

Создай 4–5 документов.

Открой List View и переключись на Kanban.

Создай доску по полю `Stage`.

Перетащи одну карточку:

```text
New → In Progress
```

После этого открой Form View этой записи и проверь значение `Stage`.

Цель упражнения — увидеть, что Kanban меняет данные документа, а не только картинку.

## 35. Практика с Calendar

В `Activity` уже есть:

```text
Starts On
Ends On
```

Найди системный DocType `Calendar View` и посмотри его поля:

```text
Reference Document Type
Subject Field
Start Date Field
End Date Field
All Day
```

Создай учебную настройку для `Activity` и сопоставь:

```text
Subject Field    = subject
Start Date Field = starts_on
End Date Field   = ends_on
```

Открой календарь через `Show Calendar`.

Задача здесь не в том, чтобы настроить production-calendar, а в том, чтобы руками понять mapping.

## 36. Практика с Tree

Создай отдельный учебный DocType `Category`.

Включи `Is Tree` и создай структуру:

```text
Root
├── Hardware
│   ├── Computers
│   └── Printers
└── Supplies
```

Сравни List View и Tree View.

После этого различие между обычным DocType и Tree DocType становится намного понятнее, чем из определения Nested Set.

---

# 37. Что запомнить

1. **View — это способ посмотреть на документы, а не новая копия данных.**
2. **Kanban обычно строится по `Select` field.** Перетаскивание между колонками меняет значение этого поля.
3. **Kanban не равен Workflow.** Доска сама по себе не задаёт роли и допустимые переходы процесса.
4. **Calendar требует mapping:** title, start, end.
5. **Gantt использует start/end и связан с calendar configuration.**
6. **Tree — особый случай:** он требует `Is Tree` и реальной parent-child модели.
7. Не меняй модель данных только ради красивого View. Сначала данные и смысл, потом представление.

## Источники

- [Frappe Framework — Desk](https://docs.frappe.io/framework/user/en/desk)
- [Frappe Framework — Tree API](https://docs.frappe.io/framework/user/en/api/tree)
- [Frappe v16 — DocType metadata](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/doctype/doctype.json)
- [Frappe v16 — List view selector](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/list/list_view_select.js)
- [Frappe v16 — Calendar](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/views/calendar/calendar.js)
- [Frappe v16 — Calendar View](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/calendar_view/calendar_view.json)
- [Frappe v16 — Gantt View](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/views/gantt/gantt_view.js)
- [Frappe v16 — Kanban View](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/views/kanban/kanban_view.js)
- [Frappe v16 — Kanban Board server logic](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/kanban_board/kanban_board.py)

Следующая глава: **14. Workspace, Shortcut, Quick List, Number Card и Chart**.
