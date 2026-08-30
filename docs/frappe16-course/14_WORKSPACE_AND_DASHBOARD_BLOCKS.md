# 14. Workspace, Shortcut, Quick List, Number Card и Chart

До этого мы работали с отдельными экранами:

- Form View — одна запись;
- List View — много записей;
- Kanban — карточки по этапам;
- Calendar и Gantt — данные по времени;
- Tree — иерархия.

Но обычному пользователю неудобно каждый раз искать нужный DocType через Awesomebar.

Для этого во Frappe есть **Workspace** — рабочая страница, на которой можно собрать ссылки, быстрые списки, показатели и графики в одном месте.

Проверено: **2026-08-30**.

## 1. Самый простой пример

Представим, что пользователь каждый день работает с DocType `Request`.

Ему нужны:

```text
1. быстро создать новую Request;
2. открыть список всех Request;
3. увидеть последние изменённые Request;
4. увидеть количество открытых Request;
5. увидеть график Request по статусам.
```

Можно каждый раз искать всё вручную.

А можно собрать Workspace:

```text
Requests

[ + New Request ]   [ All Requests ]

Open Requests
     27

Recent Requests
-----------------------------
REQ-0042  Проверить данные
REQ-0041  Подготовить акт
REQ-0040  Исправить отчёт

Requests by Status
██████████ Open        27
██████     In Progress 15
██         Closed       5
```

Это и есть основная идея Workspace.

Он не создаёт новую бизнес-логику.

Он собирает уже существующие части Frappe на одной странице.

---

# Часть 1. Workspace

## 2. Что такое Workspace

`Workspace` — рабочая страница внутри Desk.

Проще всего представить её как **главный экран раздела**.

Например:

```text
Desk
└── Requests Workspace
    ├── shortcuts
    ├── quick lists
    ├── number cards
    ├── charts
    └── links
```

Workspace отвечает на вопрос:

> Что пользователю нужно видеть сразу после входа в этот раздел?

Это не отдельная база данных и не отдельное приложение.

Это компоновка интерфейса.

## 3. Где пользователь видит Workspace

В Frappe 16 Workspaces находятся в постоянной боковой панели Desk.

Упрощённо:

```text
Desk

Sidebar
├── Home
├── Requests
├── Reports
└── Settings

          выбран Workspace Requests
                    ↓
          содержимое рабочей страницы
```

При входе пользователь попадает в Desk и открывает нужный Workspace из sidebar.

Workspace также может быть назначен пользователю как `Default Workspace`.

Если явный default не задан, Frappe может возвращать пользователя к последнему открытому Workspace.

## 4. Public и Private Workspace

Есть два базовых варианта.

### Public Workspace

Общий Workspace.

Он предназначен для группы пользователей.

Например:

```text
Requests
```

может быть общей рабочей страницей для всех пользователей с нужным доступом.

В интерфейсе такие Workspace находятся в секции `PUBLIC`.

### Private Workspace

Личный Workspace конкретного пользователя.

Например, пользователь может собрать себе:

```text
My Daily Work
├── мои открытые записи
├── мои отчёты
└── нужные мне shortcuts
```

Он будет виден владельцу в `MY WORKSPACES`.

Простая аналогия:

```text
Public Workspace  = общая доска в отделе
Private Workspace = личный рабочий стол
```

## 5. Кто может менять Public Workspace

Для публичных Workspace используется роль `Workspace Manager`.

Обычный пользователь может иметь свои личные Workspace, но управление общей структурой интерфейса лучше не раздавать всем подряд.

Иначе каждый начнёт перестраивать общий Desk под себя.

## 6. Parent и Child Workspace

Workspace могут образовывать иерархию.

Например:

```text
Operations
├── Requests
├── Documents
└── Reports
```

Здесь `Operations` — родительский Workspace, остальные — дочерние.

Это помогает организовать sidebar, когда разделов становится много.

## 7. Edit Mode

У Workspace есть обычный режим просмотра и режим редактирования.

В Edit Mode можно:

- добавить блок;
- удалить блок;
- переместить блок;
- изменить размер блока;
- перестроить страницу.

То есть Workspace во Frappe можно собирать визуально.

Для базового рабочего экрана писать HTML или JavaScript не требуется.

---

# Часть 2. Из чего состоит Workspace

## 8. Блоки Workspace

Workspace строится из блоков.

Основные штатные варианты включают:

- Header;
- Text;
- Card / Links;
- Shortcut;
- Quick List;
- Number Card;
- Chart;
- Spacer;
- Onboarding.

В этой главе нас интересуют пять самых полезных для повседневной работы:

```text
Shortcut
Quick List
Number Card
Chart
Link/Card
```

Их легко спутать, поэтому разберём по одному.

---

# Часть 3. Shortcut

## 9. Shortcut — большая кнопка быстрого перехода

`Shortcut` нужен, когда пользователь часто открывает одно и то же место.

Например:

```text
[ All Requests ]
[ New Request ]
[ Requests Report ]
```

Shortcut может вести на:

- DocType;
- Report;
- Page;
- Dashboard;
- URL.

Для DocType можно выбрать конкретный View.

Например:

```text
Request → List
Request → Report Builder
Request → Dashboard
Request → Tree
Request → New
Request → Calendar
Request → Kanban
Request → Image
```

То есть два Shortcut могут вести в один DocType, но в разные представления.

## 10. Пример двух Shortcut

Создадим:

```text
Shortcut 1
Label: All Requests
Type: DocType
Link To: Request
DocType View: List
```

и:

```text
Shortcut 2
Label: New Request
Type: DocType
Link To: Request
DocType View: New
```

Пользователь увидит две разные кнопки:

```text
[ All Requests ]    [ New Request ]
```

При этом отдельной страницы мы не программировали.

## 11. Shortcut с фильтром и счётчиком

Shortcut может иметь `Count Filter`.

Например, нам нужна кнопка только для открытых Request:

```text
Status = Open
```

Тогда Shortcut может показывать число подходящих документов:

```text
[ Open Requests   27 ]
```

Получается полезная комбинация:

```text
кнопка + фильтр + количество
```

Но Shortcut всё равно остаётся прежде всего **переходом куда-то**.

---

# Часть 4. Quick List

## 12. Quick List — маленький список прямо на Workspace

Shortcut показывает кнопку.

Quick List показывает сами документы.

Например:

```text
Recent Requests

REQ-0042  Проверить данные
REQ-0041  Подготовить акт
REQ-0040  Исправить отчёт
```

Это удобно, когда пользователю нужно быстро увидеть последние записи, не открывая полный List View.

## 13. Что задаётся для Quick List

У блока есть основные настройки:

```text
DocType
Label
Filter
```

Например:

```text
DocType: Request
Label: Open Requests
Filter: status = Open
```

Workspace покажет только подходящие документы.

## 14. Quick List не заменяет List View

Это важно.

Quick List — короткий обзор.

List View — полноценный рабочий экран.

Сравнение:

| | Quick List | List View |
|---|---|---|
| Показать несколько записей | да | да |
| Быстро увидеть свежие документы | удобно | можно |
| Сложные фильтры | ограниченно | удобно |
| Массовые действия | нет как основной сценарий | да |
| Полноценная работа со списком | нет | да |

Правило простое:

> Quick List показывает, List View позволяет полноценно работать.

---

# Часть 5. Number Card

## 15. Number Card — один показатель

`Number Card` показывает одно число.

Например:

```text
Open Requests

27
```

или:

```text
Average Processing Time

3.4 days
```

Это самый простой элемент дашборда.

## 16. Workspace не считает Number Card сам

Здесь есть важная техническая граница.

Workspace содержит ссылку на уже существующий документ `Number Card`.

То есть схема выглядит так:

```text
Request documents
       ↓
 Number Card
       ↓
Workspace block
```

Workspace только размещает показатель на странице.

Логика расчёта находится в самом `Number Card`.

## 17. Самый простой Number Card

Предположим, нужно число открытых Request.

Логика:

```text
DocType: Request
Function: Count
Filter: Status = Open
```

Результат:

```text
Open Requests
27
```

Никакой Python для такого показателя не нужен.

## 18. Что умеет Number Card по DocType

Для типа `Document Type` доступны агрегаты:

```text
Count
Sum
Average
Minimum
Maximum
```

Примеры:

```text
Count   → сколько документов
Sum     → сумма Amount
Average → среднее Duration
Minimum → минимальная сумма
Maximum → максимальная сумма
```

Для `Sum`, `Average`, `Minimum` и `Maximum` нужно указать поле, по которому считать.

## 19. Другие источники Number Card

В v16 Number Card может быть типа:

```text
Document Type
Report
Custom
```

### Document Type

Самый простой вариант.

Расчёт идёт по DocType.

### Report

Показатель берётся из отчёта.

### Custom

Используется whitelisted Python method.

Это уже вариант, когда штатного Count/Sum/Average недостаточно.

Для новичка правильный порядок такой:

```text
сначала Document Type
       ↓ если не хватает
Report
       ↓ если не хватает
Custom method
```

## 20. Percentage Stats

Number Card может показывать не только текущее число, но и изменение относительно прошлого периода.

Например:

```text
Open Requests
27
+12% за неделю
```

Интервал может быть:

- Daily;
- Weekly;
- Monthly;
- Yearly.

Это уже небольшой аналитический показатель, но всё ещё штатный механизм Frappe.

---

# Часть 6. Dashboard Chart

## 21. Chart — график на Workspace

Если Number Card отвечает:

> Сколько?

то Chart отвечает:

> Как эти данные распределены или менялись?

Например:

```text
Requests by Status

Open         ███████████ 27
In Progress  ██████      15
Closed       ██           5
```

или временной ряд:

```text
Requests per Week

30 ┤       ╭──╮
20 ┤   ╭───╯  ╰╮
10 ┤───╯       ╰──
   └──────────────
```

## 22. Workspace использует Dashboard Chart

Как и с Number Card, Workspace не создаёт расчёт сам.

Он размещает существующий `Dashboard Chart`.

```text
Request documents
       ↓
Dashboard Chart
       ↓
Workspace Chart block
```

Поэтому есть два разных понятия:

```text
Dashboard Chart = описание и расчёт графика
Chart block      = место этого графика на Workspace
```

## 23. Источники данных Dashboard Chart

В v16 `Dashboard Chart` поддерживает такие варианты расчёта:

```text
Count
Sum
Average
Group By
Custom
Report
```

Для простого случая можно построить всё напрямую по DocType.

Например:

```text
Document Type: Request
Chart Type: Group By
Group By Based On: status
Group By Type: Count
```

Получим количество документов по статусам.

## 24. Визуальный тип графика

Отдельно выбирается, **как показать результат**.

Доступны:

```text
Line
Bar
Percentage
Pie
Donut
Heatmap
```

Это важное различие.

Например:

```text
Chart Type: Group By
```

говорит **как получить данные**,

а:

```text
Type: Pie
```

говорит **как их нарисовать**.

Не путай эти два поля.

## 25. Time Series

Для `Count`, `Sum` и `Average` Dashboard Chart может строить временной ряд.

Например:

```text
Request
Based On: creation
Timespan: Last Month
Time Interval: Daily
```

Получим количество созданных Request по дням.

То есть обычное поле `creation`, которое есть у всех документов, уже позволяет построить простую динамику.

---

# Часть 7. Link / Card

## 26. Когда не нужна большая Shortcut-кнопка

Workspace также может содержать группы обычных ссылок.

Например:

```text
Master Data
├── Departments
├── Categories
└── Users
```

Такие группы удобны для вещей, которые нужны регулярно, но не настолько часто, чтобы занимать большие Shortcut-блоки.

Практическая логика:

```text
очень частое действие     → Shortcut
нужен небольшой список    → Quick List
нужен один показатель     → Number Card
нужен график              → Chart
нужна компактная навигация→ Link/Card
```

---

# Часть 8. Как собрать простой рабочий Workspace

## 27. Учебный пример

Возьмём DocType `Request` с полями:

```text
subject
status
priority
creation
```

Хотим рабочую страницу:

```text
Requests

[ New Request ] [ All Requests ] [ Open Requests 27 ]

Open Requests
27

Recent Requests
REQ-0042 ...
REQ-0041 ...
REQ-0040 ...

Requests by Status
[ chart ]
```

Для этого понадобится:

1. Workspace `Requests`;
2. Shortcut `New Request`;
3. Shortcut `All Requests`;
4. Shortcut с фильтром `Open Requests`;
5. Quick List `Recent Requests`;
6. Number Card `Open Requests`;
7. Dashboard Chart `Requests by Status`;
8. Chart block, который размещает этот Dashboard Chart.

Обрати внимание: один и тот же показатель можно показать по-разному.

Например `Open Requests = 27` можно вывести:

- числом на Shortcut;
- отдельной Number Card;
- частью Chart.

Не нужно использовать всё сразу только потому, что Frappe это позволяет.

## 28. Хороший Workspace не должен быть свалкой

Плохой вариант:

```text
25 shortcuts
12 number cards
9 charts
8 quick lists
```

Пользователь снова ничего не найдёт.

Лучше задать простой вопрос:

> Что человеку действительно нужно видеть в первые 10 секунд после открытия раздела?

Например:

```text
2–5 основных действий
1–3 важных показателя
1 короткий список
1–2 действительно полезных графика
```

Это не ограничение Frappe, а здравый смысл интерфейса.

---

# Часть 9. Workspace и права

## 29. Видимый блок не отменяет permissions

Если пользователь видит ссылку на `Request`, это ещё не означает, что он внезапно получил доступ ко всем Request.

Работает обычная система permissions.

Упрощённо:

```text
Workspace показывает вход
        ↓
permissions решают, что пользователь реально может открыть
```

То же касается Number Card и Dashboard Chart: доступ к данным не должен восприниматься как отдельная система безопасности.

## 30. Ограничение самого Workspace

Workspace можно ограничивать:

- по Module;
- по Role.

Это позволяет, например, показать один Workspace только определённой группе пользователей.

Но ещё раз:

> скрыть Workspace и запретить доступ к данным — не одно и то же.

Безопасность данных должна задаваться permissions DocType и связанных механизмов.

---

# Часть 10. Что делать без кода, а где код уже нужен

## 31. Штатно без кода

Без собственного JavaScript/Python можно:

- создать Workspace;
- сделать его Public или Private;
- создать Parent/Child структуру;
- переставлять блоки;
- создавать Shortcut;
- применять фильтр к Shortcut;
- показывать счётчик;
- добавлять Quick List;
- создавать простые Number Card;
- считать Count/Sum/Average/Min/Max;
- создавать Dashboard Chart;
- строить простые группировки и временные ряды;
- размещать Number Card и Chart на Workspace.

Для большого числа внутренних рабочих экранов этого уже достаточно.

## 32. Когда может понадобиться код

Код становится оправдан, если, например:

```text
показатель нельзя выразить обычным агрегатом;
данные нужно собирать из нескольких нестандартных источников;
нужна сложная вычисляемая метрика;
нужен полностью собственный интерактивный блок;
штатного Workspace layout уже недостаточно.
```

Тогда возможны:

```text
Custom Number Card method
Custom Dashboard Chart Source
Custom Block
Desk Page
собственный frontend
```

Но это следующий уровень сложности.

Для начала нужно убедиться, что задачу действительно нельзя решить обычными Workspace blocks.

---

# Мини-практика

## 33. Собери Workspace руками

Если у тебя есть учебный DocType `Request`, сделай следующее.

### Шаг 1

Создай Workspace:

```text
Title: Requests
```

Для первого опыта можно сделать Private.

### Шаг 2

Добавь Shortcut:

```text
Label: All Requests
Type: DocType
Link To: Request
View: List
```

### Шаг 3

Добавь второй Shortcut:

```text
Label: New Request
Type: DocType
Link To: Request
View: New
```

### Шаг 4

Добавь Quick List:

```text
DocType: Request
Label: Recent Requests
```

### Шаг 5

Создай Number Card:

```text
Label: Open Requests
Type: Document Type
Document Type: Request
Function: Count
Filter: status = Open
```

Добавь её на Workspace.

### Шаг 6

Создай Dashboard Chart:

```text
Name: Requests by Status
Chart Type: Group By
Document Type: Request
Group By Based On: status
Group By Type: Count
Type: Bar
```

Добавь этот Chart на Workspace.

### Шаг 7

Открой Workspace как обычный пользователь и проверь:

- работают ли ссылки;
- виден ли Quick List;
- правильно ли считается Number Card;
- строится ли Chart;
- не показывает ли экран лишнее.

---

# Что запомнить

## 34. Короткая схема

```text
Workspace
│
├── Shortcut    → быстро перейти
├── Quick List  → быстро увидеть несколько документов
├── Number Card → увидеть одно число
├── Chart       → увидеть распределение или динамику
└── Link/Card   → компактно сгруппировать навигацию
```

И главное:

```text
Workspace ≠ бизнес-логика
Workspace ≠ отдельная база данных
Workspace ≠ BI-система

Workspace = компоновщик рабочего экрана Desk
```

## 35. Пять контрольных вопросов

После этой главы ты должен уметь ответить:

1. Чем Workspace отличается от DocType?
2. Чем Shortcut отличается от Quick List?
3. Где считается значение Number Card?
4. Чем Dashboard Chart отличается от Chart block внутри Workspace?
5. Почему видимость Workspace не заменяет permissions на данные?

Если на эти вопросы отвечаешь уверенно — достаточно.

---

# Источники

- [Workspace](https://docs.frappe.io/framework/user/en/desk/workspace)
- [Workspace Blocks](https://docs.frappe.io/framework/user/en/desk/workspace/blocks)
- [Workspace Customization](https://docs.frappe.io/framework/user/en/desk/workspace/customization)
- [Workspace Access](https://docs.frappe.io/framework/user/en/desk/workspace/access)
- [Workspace metadata — `workspace.json`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace/workspace.json)
- [Workspace Shortcut metadata](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace_shortcut/workspace_shortcut.json)
- [Workspace Quick List metadata](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace_quick_list/workspace_quick_list.json)
- [Number Card metadata](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/number_card/number_card.json)
- [Dashboard Chart metadata](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart/dashboard_chart.json)

Следующая глава: **15. Customize Form — как менять существующий DocType без редактирования его исходного определения**.
