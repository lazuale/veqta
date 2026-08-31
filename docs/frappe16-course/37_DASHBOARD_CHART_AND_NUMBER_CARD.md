# 37. Dashboard Chart и Number Card

В предыдущих главах мы разобрали три способа получить табличный результат:

```text
Report Builder
→ отчёт настройками

Query Report
→ отчёт одним SQL-запросом

Script Report
→ отчёт серверным Python-кодом
```

Но пользователю не всегда нужна таблица.

Иногда на рабочем экране достаточно сразу увидеть:

```text
Открытых заявок: 37

Сумма за месяц: 1 240 000

Requests по Department:
Support  █████████
Sales    █████
Admin    ██
```

Для таких случаев во Frappe есть два отдельных объекта:

```text
Dashboard Chart
Number Card
```

Проверено: **2026-08-31**.

---

## 1. Сначала простая разница

### Dashboard Chart

Показывает **набор значений графически**.

Например:

```text
Jan  12
Feb  18
Mar  31
```

можно вывести как Line или Bar chart.

### Number Card

Показывает **одно главное число**.

Например:

```text
Open Requests
37
```

или:

```text
Total Amount
1.24 M
```

Упрощённо:

```text
нужно увидеть распределение / динамику
→ Dashboard Chart

нужно увидеть один KPI
→ Number Card
```

---

## 2. Это отдельные Documents, а не настройка Workspace

Важно не перепутать несколько уровней.

`Dashboard Chart` — отдельный DocType.

`Number Card` — отдельный DocType.

А Workspace только **размещает уже существующие** Chart и Number Card как блоки.

Схема:

```text
Dashboard Chart
        ↓
     Chart block
        ↓
     Workspace
```

и:

```text
Number Card
      ↓
Number Card block
      ↓
   Workspace
```

То есть Workspace не хранит сам расчёт KPI.

Он хранит расположение блока, который ссылается на соответствующий объект.

Это соответствует штатной модели Workspace v16: в Workspace можно добавлять существующие Dashboard Chart и Number Card.

---

## 3. Есть ещё отдельный Dashboard

Кроме Workspace, во Framework существует отдельная сущность:

```text
Dashboard
```

Dashboard может содержать ссылки на:

```text
Dashboard Chart
Number Card
```

Поэтому один и тот же Chart можно использовать в разных местах.

Например:

```text
Dashboard Chart: Requests by Department
        ├── Workspace A
        └── Dashboard B
```

Не нужно копировать расчёт только потому, что график нужен в двух экранах.

---

# Часть I. Dashboard Chart

## 4. Какие источники данных умеет Dashboard Chart в v16

У актуального `Dashboard Chart.chart_type` есть шесть вариантов:

```text
Count
Sum
Average
Group By
Custom
Report
```

Их удобно разделить на три уровня.

### Уровень 1. Прямо по DocType

```text
Count
Sum
Average
Group By
```

Framework сам строит выборку по Document Type.

### Уровень 2. Из готового Report

```text
Report
```

Chart берёт данные Query/Script Report.

### Уровень 3. Полностью собственный источник

```text
Custom
```

Chart работает через `Dashboard Chart Source` и ваш код.

Главная лестница здесь та же:

```text
штатная агрегация DocType
        ↓ не хватает
готовый Report
        ↓ не хватает
Custom Chart Source
```

---

## 5. Первый пример: Count

Допустим, есть DocType:

```text
Request
```

с документами:

```text
REQ-0001
REQ-0002
REQ-0003
...
```

Хотим увидеть, сколько Requests создавалось по дням.

Dashboard Chart:

```text
Chart Name    = Requests Created
Chart Type    = Count
Document Type = Request
Based On      = creation
Timespan      = Last Month
Time Interval = Daily
Type          = Line
```

Результат по смыслу:

```text
Aug 01 → 4
Aug 02 → 7
Aug 03 → 2
Aug 04 → 9
```

Framework сам получает Documents, группирует их по времени и считает количество.

---

## 6. `Based On` — по какой дате строить динамику

Для Count / Sum / Average используется поле:

```text
Time Series Based On
```

В интерфейсе в него попадают системные даты:

```text
creation
modified
```

и ваши поля типа:

```text
Date
Datetime
```

Например у `Request` есть:

```text
requested_on
closed_at
```

Тогда можно строить разные графики.

### Создание Requests

```text
Based On = creation
```

### Requests по дате заявки

```text
Based On = requested_on
```

### Requests по моменту закрытия

```text
Based On = closed_at
```

Поэтому вопрос перед созданием графика должен звучать не только:

> Что считаем?

но и:

> **По какой дате раскладываем это по времени?**

---

## 7. `Sum`

Теперь предположим, что у `Request` есть числовое поле:

```text
amount
```

Нужно видеть сумму Amount по месяцам.

```text
Chart Type     = Sum
Document Type  = Request
Based On       = creation
Value Based On = amount
Timespan       = Last Year
Time Interval  = Monthly
```

Если данные такие:

```text
January
1000
3000
2000
```

то график покажет:

```text
January → 6000
```

---

## 8. Какие поля можно суммировать

Frontend текущего v16 предлагает для `Value Based On` числовые типы вроде:

```text
Int
Float
Currency
Percent
Duration
```

То есть поле:

```text
subject
```

суммировать бессмысленно и оно не должно предлагаться как обычное numeric source.

А поля:

```text
amount
hours
progress
quantity
```

подходят.

---

## 9. `Average`

`Average` выглядит похоже:

```text
Chart Type     = Average
Document Type  = Request
Based On       = creation
Value Based On = amount
```

Допустим, за день было три Requests:

```text
100
200
600
```

Среднее:

```text
(100 + 200 + 600) / 3 = 300
```

На графике за этот период будет:

```text
300
```

В текущей серверной реализации v16 для временной серии Framework получает одновременно сумму значения и количество Documents, а затем делит сумму на count для `Average`.

---

## 10. Timespan

Для временных графиков в текущем v16 доступны:

```text
Last Year
Last Quarter
Last Month
Last Week
Select Date Range
```

Например:

```text
Timespan = Last Month
```

означает:

> показать выбранную метрику за последний месяц.

Если нужен произвольный период:

```text
Timespan = Select Date Range
```

появляются:

```text
From Date
To Date
```

---

## 11. Time Interval

Timespan отвечает на вопрос:

> какой диапазон берём?

А `Time Interval`:

> на какие куски его делим?

В текущем v16 есть:

```text
Yearly
Quarterly
Monthly
Weekly
Daily
```

Например:

```text
Timespan      = Last Year
Time Interval = Monthly
```

даёт примерно:

```text
Jan
Feb
Mar
...
Dec
```

А:

```text
Timespan      = Last Month
Time Interval = Daily
```

даёт точки по дням.

---

## 12. Пользователь может менять временной масштаб прямо на widget

Chart Widget умеет показывать controls для time-series chart.

Пользователь может переключать:

```text
Daily
Weekly
Monthly
Quarterly
Yearly
```

и Timespan.

Выбранная конфигурация сохраняется в пользовательских Dashboard Settings.

То есть один и тот же Dashboard Chart может быть определён, например, как:

```text
Last Year / Monthly
```

но конкретный пользователь временно переключит себе:

```text
Last Month / Daily
```

Это пользовательское представление, а не изменение бизнес-данных.

---

## 13. Стандартные DocType charts исключают Cancelled

В текущем `Dashboard Chart.get()` перед расчётом добавляется фильтр:

```text
docstatus < 2
```

То есть Documents с:

```text
docstatus = 2
```

не участвуют в обычных DocType Dashboard Charts.

Напомним:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Поэтому обычный Count не означает буквально:

> все строки таблицы без исключения.

Cancelled документы Framework автоматически исключает из этого стандартного пути.

---

## 14. `Group By` — распределение по категории

Теперь хотим ответить на другой вопрос:

> Сколько Requests в каждом Department?

Это уже не time-series.

Настраиваем:

```text
Chart Type        = Group By
Document Type     = Request
Group By Based On = department
Group By Type     = Count
Type              = Bar
```

Допустим:

```text
Support → 18
Sales   → 12
Admin   → 7
```

Chart покажет категории, а не даты.

---

## 15. Что можно использовать для Group By

В интерфейсе текущего v16 для обычного DocType в Group By предлагаются прежде всего:

```text
owner
Link
Select
```

Например:

```text
owner
status
priority
department
category
```

в зависимости от типов полей вашего DocType.

Это разумно: Group By предназначен для категорий.

---

## 16. Group By умеет не только Count

У `Group By Type` сейчас есть:

```text
Count
Sum
Average
```

Например:

```text
Group By Based On            = department
Group By Type                = Sum
Aggregate Function Based On  = amount
```

получим:

```text
Support → сумма amount по Support
Sales   → сумма amount по Sales
Admin   → сумма amount по Admin
```

То есть можно отвечать не только на:

> сколько документов?

но и на:

> какая сумма по каждой категории?

---

## 17. Link label может показываться человеческим названием

Если Group By идёт по Link-полю, backend v16 смотрит metadata связанного DocType.

Если у него есть:

```text
title_field
```

то подпись графика может использовать title, а не технический `name`.

Например Link хранит:

```text
DEP-0007
```

а title связанного Department:

```text
Support
```

На графике логичнее увидеть:

```text
Support
```

И Framework это умеет учитывать.

---

## 18. `Number of Groups` не является SQL LIMIT

У Dashboard Chart есть поле:

```text
Number of Groups
```

Но важно понимать его текущую роль.

Backend Group By получает набор сгруппированных данных.

А Chart Widget передаёт `number_of_groups` в renderer как:

```text
maxSlices
```

Для круговых/категориальных графиков это влияет на визуальное количество slices.

То есть не стоит трактовать поле как гарантированный:

```sql
LIMIT N
```

на уровне исходного запроса.

Это прежде всего настройка отображения chart.

---

## 19. Визуальный `Type`

`Chart Type` отвечает за **способ получения данных**:

```text
Count
Sum
Average
Group By
Report
Custom
```

А поле `Type` отвечает за **способ отрисовки**.

В v16 варианты:

```text
Line
Bar
Percentage
Pie
Donut
Heatmap
```

Это две разные оси.

Например:

```text
Chart Type = Group By
Type       = Bar
```

или:

```text
Chart Type = Group By
Type       = Donut
```

данные могут быть те же, а визуализация разная.

---

## 20. Не любой график подходит любым данным

Технически вариантов много, но выбирать стоит по смыслу.

### Line

Хорошо показывает динамику:

```text
дата → значение
```

### Bar

Удобен для сравнения категорий:

```text
Department → Count
```

### Pie / Donut

Подходит для небольшого числа категорий.

Плохая идея:

```text
83 категории
→ Donut
```

### Percentage

Полезен для частей одного целого.

### Heatmap

Показывает интенсивность по календарным датам.

Форма графика должна помогать увидеть данные, а не просто быть красивой.

---

## 21. Heatmap

Для Heatmap Dashboard Chart использует:

```text
Year
```

и строит значения по отдельным датам года.

По смыслу это удобно для вещей вроде:

```text
активность по дням
события по дням
количество операций по дням
```

Результат не выглядит как обычный:

```text
labels + dataset line
```

а формируется как набор точек календаря.

---

## 22. Важный нюанс v16: Heatmap использует другой data path

Для обычных:

```text
Count
Sum
Average
Group By
```

текущая реализация получает данные через:

```python
frappe.get_list(...)
```

То есть используется permission-aware Database API.

Но текущий `get_heatmap_chart_config()` в ветке `version-16` получает агрегаты через:

```python
frappe.get_all(...)
```

А `get_all` не применяет пользовательские row permissions так же, как `get_list`.

Поэтому практическое правило:

> **не используй стандартный Heatmap для чувствительных данных с row-level ограничениями, пока отдельно не проверил фактический доступ под нужными пользователями.**

Если безопасность зависит от User Permission или другого ограничения строк, лучше явно протестировать Heatmap или построить контролируемый Custom/Report data path.

Это не проблема визуального типа как такового — это особенность текущей серверной реализации v16.

---

## 23. Filters

Dashboard Chart может иметь обычные фильтры.

Например:

```text
Request.status = Open
Request.department = Support
```

Тогда график считает не все Requests, а только подходящие.

Например:

```text
Chart Type = Count
Filter     = status = Open
```

даёт:

> количество только открытых Requests.

---

## 24. Dynamic Filters

В v16 у Dashboard Chart есть также:

```text
Dynamic Filters JSON
```

Они позволяют вычислять часть filter values в клиенте.

Например значение может зависеть от:

```text
user default
сегодняшней даты
другого runtime expression
```

В dashboard utilities текущего v16 такие expressions вычисляются через client-side `eval()`.

Это удобно для динамического представления.

Но запомни:

> **Dynamic Filter — не security rule.**

Пользовательский фильтр отвечает за то, что хочет показать widget.

За реальный доступ к данным отвечает сервер.

Нельзя защищать секретные данные только тем, что Workspace автоматически подставляет нужный Department.

---

## 25. `Is Public`

У Dashboard Chart есть:

```text
Is Public
```

Описание поля говорит, что chart становится доступным для выбора всем пользователям.

Но это не означает:

```text
Is Public = ✓
→ пользователь получил все данные источника
```

В текущем v16 при выборе chart действительно учитываются:

```text
owner
или
is_public = 1
```

Но у Dashboard Chart также есть собственная permission logic, а сами data sources дополнительно выполняют свои permission-aware запросы.

Правильное понимание:

```text
Is Public
→ общий widget можно использовать/выбирать

не

Is Public
→ отключить permissions исходных данных
```

---

## 26. `Roles` у Dashboard Chart

У Chart есть таблица:

```text
Roles
```

Текущее описание прямо говорит:

> если Roles заданы, доступ к chart ограничивается этими ролями; если нет — используются permissions DocType или Report.

Например:

```text
Roles
- Request Manager
```

позволяет ограничить сам chart указанной ролью.

Но это снова **не должно восприниматься как способ выдать скрытые данные**.

Например Report-based Chart всё равно вызывает сам Report, а Report pipeline выполняет собственные проверки.

Для Custom Source ваш server method также должен сам соблюдать нужную модель доступа.

---

## 27. Кто может создавать Dashboard Chart

В metadata v16 у самого DocType `Dashboard Chart` есть полноценные create/write права, в частности, для:

```text
System Manager
Dashboard Manager
```

`Desk User` имеет read-доступ к объектам, которые проходит через дополнительную permission logic.

То есть отдельная роль:

```text
Dashboard Manager
```

предназначена именно для администрирования dashboard-объектов без необходимости раздавать человеку полный System Manager.

---

# Часть II. Chart из Report

## 28. `Chart Type = Report`

Если штатной агрегации DocType уже мало, можно использовать готовый Report.

```text
Chart Type  = Report
Report Name = Request Analysis
```

В интерфейсе текущего v16 Report Builder исключается из списка для такого chart.

То есть этот путь рассчитан прежде всего на Query/Script-подобные отчёты, которые выполняются через query report pipeline.

---

## 29. Вариант 1: использовать chart, который уже вернул Script Report

В главе 36 мы видели, что Script Report может вернуть:

```python
return columns, data, None, chart, report_summary
```

Если Report уже имеет `chart`, Dashboard Chart может включить:

```text
Use Report Chart = ✓
```

Тогда Widget использует:

```text
result.chart.data
```

из результата Report.

Схема:

```text
Script Report
   ├── data
   ├── chart
   └── report_summary
        ↓
Dashboard Chart
        ↓
Workspace
```

Это хороший вариант, когда chart является естественной частью аналитического отчёта.

---

## 30. Вариант 2: построить chart из колонок Report

Можно выключить:

```text
Use Report Chart
```

и выбрать:

```text
X Field
Y Axis
```

Например Report возвращает:

```text
Department | Request Count | Total Amount
```

Настраиваем:

```text
X Field = department
Y Axis:
- request_count
- total_amount
```

Тогда Dashboard Chart сам строит visual dataset из tabular result.

---

## 31. Один Report может стать источником нескольких Chart

Например один Script Report возвращает:

```text
Department
Count
Total Amount
Average Amount
```

Из него можно сделать:

```text
Chart A
X = Department
Y = Count

Chart B
X = Department
Y = Total Amount

Chart C
X = Department
Y = Average Amount
```

Это часто лучше, чем писать три почти одинаковых backend-расчёта.

---

## 32. Report-based Chart наследует сложность Report

Если Report:

- выполняет тяжёлый SQL;
- делает несколько Python queries;
- агрегирует большой объём;

то Dashboard Chart не делает этот расчёт бесплатным.

Chart — только другой способ представить результат.

Поэтому:

```text
медленный Report
→ медленный Report-based Dashboard Chart
```

---

## 33. Prepared Report здесь не спасает автоматически

Это важная особенность текущего v16.

Chart Widget для:

```text
Chart Type = Report
```

вызывает:

```text
frappe.desk.query_report.run
```

с:

```text
ignore_prepared_report = 1
```

То есть widget просит **живой результат Report**, а не подготовленную копию Prepared Report.

Поэтому нельзя рассуждать так:

```text
Report тяжёлый
→ включим Prepared Report
→ Dashboard Chart станет дешёвым
```

Для dashboard widget это не гарантируется.

Если KPI постоянно дорогой, лучше думать об архитектуре данных:

```text
нормальная агрегация в БД
предрасчитанная таблица / DocType
background calculation
отдельный lightweight source
```

а не рассчитывать только на Prepared Report.

---

## 34. `report_summary` тоже может попасть в Chart Widget

Когда Dashboard Chart работает от Report, frontend получает:

```text
report_summary
```

и сохраняет его как summary widget-а.

Для Full-width chart этот summary может отображаться рядом с графиком.

Это позволяет одному Script Report вернуть одновременно:

```text
таблицу
chart
несколько KPI summary
```

а Dashboard Chart использовать тот же расчёт на отдельном экране.

---

# Часть III. Custom Dashboard Chart Source

## 35. Когда нужен `Custom`

`Custom` имеет смысл, когда не подходят:

```text
Count
Sum
Average
Group By
Report
```

Например данные:

- собираются из нескольких сервисов;
- требуют собственного серверного метода;
- имеют нестандартный формат;
- chart имеет собственные filters;
- нужен reusable chart source внутри App.

Тогда:

```text
Chart Type = Custom
Source     = My Chart Source
```

---

## 36. Что такое `Dashboard Chart Source`

Это отдельный системный DocType.

В текущем v16 он содержит минимум:

```text
Source Name
Module
Timeseries
```

Важная архитектурная деталь:

`Dashboard Chart Source` — это уже **developer-level extension point**.

При сохранении source текущий controller требует:

```text
Developer Mode
```

и экспортирует source в файлы App.

То есть это не обычная бизнес-настройка, которую предполагается бесконечно собирать кликами на production Site.

---

## 37. Как Custom Source подключается

Для source существует JavaScript config.

По смыслу он регистрирует объект вида:

```javascript
frappe.dashboards.chart_sources["Request Custom Source"] = {
    method: "training_app.analytics.get_request_chart",
    filters: [
        // filter definitions
    ],
};
```

Chart Widget:

1. загружает config выбранного Dashboard Chart Source;
2. выполняет его;
3. получает settings;
4. вызывает указанный `method`.

Серверный method должен вернуть data, понятные chart widget, например:

```python
{
    "labels": ["A", "B", "C"],
    "datasets": [
        {
            "name": "Requests",
            "values": [10, 20, 15],
        }
    ],
}
```

Конкретная серверная реализация уже является кодом вашего App.

---

## 38. Custom Source не получает безопасность автоматически

Если ваш method делает:

```python
frappe.get_all(...)
```

или raw SQL без ограничений, Dashboard Chart сам не превратит эти данные в permission-aware выборку.

Если method делает:

```python
frappe.get_list(...)
```

и этого достаточно для модели доступа — ситуация лучше.

Главная мысль:

> **Custom Source означает, что разработчик сам отвечает за серверную выборку и permissions.**

Chart Widget — это представление результата, а не ACL firewall.

---

## 39. Custom Options

У Dashboard Chart есть:

```text
Custom Options
```

Это JSON, который frontend объединяет с параметрами Frappe Charts.

Например можно дополнительно задавать параметры визуализации.

Но Custom Options не должны превращаться в место для бизнес-логики.

Разделяй:

```text
как получили данные
→ source / report / DocType query

как их нарисовали
→ chart options
```

---

# Часть IV. Number Card

## 40. Теперь Number Card

Chart отвечает на вопрос:

> как распределяются значения?

Number Card:

> **какое одно число мне важно увидеть сейчас?**

Например:

```text
Open Requests
37
```

```text
Total Amount
1.24 M
```

```text
Average Resolution Time
4.3 h
```

---

## 41. Три источника Number Card в v16

У актуального `Number Card.type` есть:

```text
Document Type
Report
Custom
```

Опять та же лестница.

### Document Type

Простая штатная агрегация.

### Report

Посчитать одно число из результата Query/Script Report.

### Custom

Получить KPI через собственный whitelisted method.

---

## 42. Самый простой Number Card: Count

Хотим показать число открытых Requests.

```text
Label         = Open Requests
Type          = Document Type
Document Type = Request
Function      = Count
Filters       = status = Open
```

Framework выполняет permission-aware aggregate через `frappe.get_list()`.

Результат:

```text
Open Requests
37
```

---

## 43. Функции Document Type Number Card

В текущем v16 есть:

```text
Count
Sum
Average
Minimum
Maximum
```

### Count

```text
сколько Documents
```

### Sum

```text
сумма выбранного numeric field
```

### Average

```text
среднее значение
```

### Minimum

```text
минимальное значение
```

### Maximum

```text
максимальное значение
```

Для всех, кроме Count, нужно указать:

```text
Aggregate Function Based On
```

например:

```text
amount
```

---

## 44. Пример Sum

```text
Label                       = Open Request Amount
Type                        = Document Type
Document Type               = Request
Function                    = Sum
Aggregate Function Based On = amount
Filter                      = status = Open
```

Если открытые Requests имеют:

```text
1000
2500
1500
```

Number Card покажет:

```text
5000
```

---

## 45. Number Card по Child Table

Если выбранный `Document Type` является Child Table, v16 требует:

```text
Parent Document Type
```

Это уже знакомая логика Framework.

Child Table не является независимым верхнеуровневым бизнес-документом, и permission context обычно идёт через parent.

Поэтому поле parent здесь не декоративное.

---

## 46. Filters и Dynamic Filters у Number Card

Как и Dashboard Chart, Number Card поддерживает:

```text
Filters JSON
Dynamic Filters JSON
```

Например:

```text
status = Open
priority = High
```

Dynamic Filters могут подставлять runtime values.

Но правило остаётся тем же:

```text
filter
≠ permission
```

Нельзя делать карточку безопасной только тем, что UI по умолчанию подставил нужный Department.

---

## 47. Percentage Stats

Для `Type = Document Type` у Number Card есть:

```text
Show Percentage Stats
Stats Time Interval
```

Интервалы:

```text
Daily
Weekly
Monthly
Yearly
```

На карточке можно увидеть, например:

```text
37
↑ 12 % since last week
```

Это помогает быстро оценить изменение KPI.

---

## 48. Что именно сравнивает Percentage Stats в текущем v16

Не стоит воспринимать этот механизм как универсальную BI-функцию «сравнить текущий период с предыдущим периодом».

Текущий backend:

1. считает обычный current result;
2. определяет дату `current date - interval`;
3. вызывает тот же aggregate ещё раз с дополнительным условием:

```text
creation < previous_date
```

То есть смысл сравнения зависит от ваших исходных filters.

Например без аккуратного date filter это может быть сравнение:

```text
текущее накопленное значение
против накопленного значения до прошлой недели
```

а не строго:

```text
эта неделя
против предыдущей недели
```

Поэтому для серьёзного KPI сначала проверьте его фактическую математику на тестовых данных.

Если нужна точная бизнес-метрика period-over-period, Report или Custom method может быть понятнее.

---

## 49. Форматирование числа

Number Card умеет сокращать большие значения.

Например:

```text
1 234 567
```

может показываться сокращённо.

В v16 есть флаг:

```text
Show Full Number
```

Если включить его, выводится полное значение вместо сокращённого формата вроде:

```text
1.2 M
```

Также есть:

```text
Currency
Color
Background Color
```

То есть Number Card отвечает не только за calculation, но и за компактное визуальное представление KPI.

---

# Часть V. Number Card из Report

## 50. `Type = Report`

Number Card может взять готовый Report:

```text
Type        = Report
Report Name = Request Analysis
Field       = amount
Function    = Sum
```

Widget запускает Report, получает его rows и извлекает выбранное numeric field.

После этого frontend применяет выбранную aggregate function.

Для report-based Number Card текущий v16 предлагает:

```text
Sum
Average
Minimum
Maximum
```

---

## 51. Это отличается от Document Type Number Card

### Document Type

Агрегация происходит сервером напрямую по DocType:

```text
Request
→ get_list aggregate
→ одно число
```

### Report

Сначала выполняется весь Report:

```text
Report
→ rows
→ взять выбранную numeric column
→ Sum/Average/Min/Max в widget
```

Это принципиально разные пути.

Если для одного числа приходится выполнять огромный Script Report на 50 000 строк, это может быть неоправданно дорого.

---

## 52. Report Number Card тоже игнорирует Prepared Report

Текущий Number Card Widget вызывает:

```text
frappe.desk.query_report.run
```

с:

```text
ignore_prepared_report = 1
```

Поэтому тот же вывод, что и для Dashboard Chart:

> **Prepared Report не является автоматическим кэшем для Number Card на Workspace.**

Если карточка должна отображаться постоянно, source для неё должен быть дешёвым.

---

## 53. Нюанс v16 с нулевыми значениями Report Number Card

Текущий frontend при сборе значений выбранной report column делает проверку по truthy value.

Упрощённо:

```javascript
if (row[field]) {
    values.push(row[field]);
}
```

Значение:

```text
0
```

является falsy и может не попасть в массив.

Для:

```text
Sum
```

это обычно не меняет итог.

Но для:

```text
Average
Minimum
Maximum
```

нули могут быть математически значимы.

Поэтому report-based Number Card с нулевыми значениями нужно обязательно проверять на реальном наборе данных текущей версии.

Это именно нюанс текущего widget v16, а не общее правило математической агрегации.

---

# Часть VI. Custom Number Card

## 54. Когда нужен Custom Number Card

Допустим KPI нельзя выразить одним:

```text
Count
Sum
Average
Min
Max
```

и не хочется запускать тяжёлый Report.

Например:

```text
SLA Compliance = 97.4 %
```

рассчитывается специальным алгоритмом.

Тогда:

```text
Type   = Custom
Method = training_app.api.get_sla_kpi
```

---

## 55. Custom Number Card вызывает whitelisted method

Текущий widget вызывает method, указанный в поле:

```text
Method
```

и передаёт ему:

```text
filters
```

Простой серверный метод может вернуть число.

Но v16 поддерживает и более богатый объект.

В metadata приведён формат по смыслу:

```python
{
    "value": 97.4,
    "fieldtype": "Percent",
    "route_options": {"status": "Open"},
    "route": ["List", "Request"],
}
```

Тогда Number Card знает:

- какое значение показать;
- как его форматировать;
- куда перейти по клику.

---

## 56. Пример Custom method

Например:

```python
import frappe


@frappe.whitelist()
def get_open_request_kpi(filters=None):
    count = frappe.db.count(
        "Request",
        filters={"status": "Open"},
    )

    return {
        "value": count,
        "fieldtype": "Int",
        "route": ["List", "Request"],
        "route_options": {"status": "Open"},
    }
```

Но здесь есть важный вопрос:

> имеет ли текущий пользователь право видеть именно эти данные?

Сам факт `@frappe.whitelist()` не решает этот вопрос.

Custom method должен проектироваться как нормальный server API endpoint.

---

## 57. Custom Number Card и permissions

В текущей permission logic `Number Card` для `Type = Custom` всё равно связан с:

```text
Document Type
```

и обычному пользователю доступ к card проверяется относительно readable DocTypes.

Но это проверка доступа к самому объекту Number Card.

Ваш custom method может внутри:

```python
frappe.get_all(...)
frappe.db.sql(...)
вызвать внешний сервис
```

Поэтому окончательная безопасность данных всё равно остаётся обязанностью server method.

---

# Часть VII. Permissions целиком

## 58. У widget есть два уровня доступа

Очень полезная модель:

```text
можно ли увидеть сам widget?
        ↓
можно ли получить данные source?
```

Это не всегда одно и то же.

Например:

```text
Dashboard Chart доступен по Role
```

но Report, на котором он основан, пользователю недоступен.

Тогда Report endpoint должен отказать.

И наоборот, пользователь может иметь доступ к DocType, но Chart может быть ограничен отдельным Roles.

---

## 59. `Is Public` не превращает данные в public data

Это стоит повторить отдельно для обоих объектов.

Есть:

```text
Dashboard Chart.is_public
Number Card.is_public
```

Эти флаги помогают сделать widget общедоступным для выбора/использования среди пользователей Desk.

Но это не равно:

```text
Guest API
отмена User Permission
отмена Report permissions
отмена server method checks
```

Внутренний widget и публичный интернет-resource — совершенно разные понятия.

---

## 60. Dynamic Filters тоже не security

Плохая архитектура:

```text
Department = текущий Department пользователя
```

задаётся только dynamic filter-ом, а backend реально разрешает читать всё.

Пользовательский filter можно изменить, обойти или вызвать endpoint иначе.

Правильно:

```text
server permissions
→ определяют максимум доступных данных

widget filters
→ выбирают подмножество для отображения
```

---

# Часть VIII. Производительность

## 61. Dashboard открывается часто

Обычный Report пользователь запускает осознанно.

Dashboard/Workspace часто открывается просто при входе в раздел.

Если на странице стоят:

```text
8 Number Cards
6 Dashboard Charts
```

это уже может означать несколько server calls при каждом открытии.

Поэтому dashboard metric должен быть дешевле, чем случайный разовый отчёт.

---

## 62. Не строй Number Card через огромный Report без необходимости

Плохая схема:

```text
Number Card
→ Script Report
→ 100 000 rows
→ Python loops
→ вернуть rows
→ frontend взять одну колонку
→ посчитать Sum
```

если тот же KPI можно получить:

```text
Number Card / Document Type / Sum
```

одним aggregate query.

Сначала выбирай самый дешёвый штатный путь.

---

## 63. Не делай десять одинаковых тяжёлых sources

Допустим нужны карточки:

```text
Requests Today
Open Requests
Overdue Requests
High Priority Requests
```

Если каждая запускает отдельный огромный Python pipeline, dashboard быстро станет дорогим.

В зависимости от объёма данных стоит подумать о:

```text
простых indexed filters
server-side aggregate queries
предрасчёте
отдельной summary model
background update
```

Но не усложняй архитектуру заранее для таблицы из 500 строк.

Сначала измерь.

---

## 64. Что происходит с cache в текущем Dashboard Chart v16

В коде Framework есть decorator:

```python
@cache_source
```

и ключ вида:

```text
chart-data:<chart_name>
```

При изменении Dashboard Chart этот cache key удаляется.

Также хранится:

```text
last_synced_on
```

Но не стоит строить архитектуру приложения на предположении:

> Dashboard Chart — это гарантированная materialized cache таблица.

В текущем v16 Chart Widget при обычном обновлении вызывает source с `refresh = 1`, а cache helper является внутренней implementation detail, которая может меняться.

Кроме того, тяжёлый Report-based chart всё равно запускает report pipeline напрямую.

Поэтому воспринимай Chart прежде всего как **визуализацию**, а не как систему хранения предрасчитанной аналитики.

Если нужен стабильный предрасчёт — проектируй его явно.

---

## 65. `last_synced_on` — не дата актуальности бизнес-источника

Dashboard Chart имеет поле:

```text
Last Synced On
```

Framework обновляет его, когда chart source пересчитывается через штатный path.

Это означает примерно:

> когда Framework последний раз получил данные этого Chart.

Это не обязательно означает:

> все внешние данные гарантированно актуальны на эту секунду.

Особенно для Custom Source, который может читать другой service или предрасчитанную таблицу.

---

# Часть IX. Standard объекты и App

## 66. `Is Standard`

И Dashboard Chart, и Number Card имеют:

```text
Is Standard
Module
```

Когда объект является частью собственного App, его можно хранить как стандартный объект и переносить вместе с кодом.

Для Dashboard Chart текущий controller запрещает редактировать Standard chart вне Developer Mode.

Для стандартных объектов при Developer Mode Framework экспортирует их в файлы App.

Это уже знакомая общая идея:

```text
локальная настройка Site
→ custom object

стабильная часть App
→ standard object + Git
```

Подробно Standard vs Custom и Developer Mode будут в главах 46–47.

---

## 67. Custom Chart Source почти сразу означает App

Обычный:

```text
Count
Sum
Average
Group By
```

можно настроить без собственного backend-кода.

`Dashboard Chart Source` уже требует Developer Mode и живёт как developer artifact.

Поэтому если задача дошла до:

```text
Custom Chart Source
```

мы фактически находимся на уровне:

```text
application code
```

а не обычной настройки рабочего места.

---

# Часть X. Как выбирать механизм

## 68. Нужна одна цифра

Пример:

> Сколько сейчас открытых Requests?

Выбор:

```text
Number Card
Type = Document Type
Function = Count
```

Не нужен Script Report.

---

## 69. Нужна сумма одного поля

> Какова общая сумма открытых Requests?

```text
Number Card
Document Type
Sum(amount)
status = Open
```

---

## 70. Нужна динамика по времени

> Сколько Requests создавалось каждый день?

```text
Dashboard Chart
Count
Based On = creation
Daily
```

---

## 71. Нужно распределение по статусу

> Сколько Requests в каждом Status?

```text
Dashboard Chart
Group By
status
Count
```

---

## 72. Нужен сложный уже существующий расчёт

> Есть Script Report, который считает SLA и возвращает chart.

```text
Dashboard Chart
Type = Report
Use Report Chart = ✓
```

Если нужна только одна числовая колонка из небольшого Report:

```text
Number Card
Type = Report
```

---

## 73. Нужен KPI со специальным алгоритмом

> KPI рассчитывается по нескольким источникам и должен открыть специальный экран по клику.

```text
Custom Number Card
→ whitelisted method
```

---

## 74. Нужен нестандартный график из server logic

```text
Custom Dashboard Chart
→ Dashboard Chart Source
→ App code
```

---

## 75. Нужен полноценный BI dashboard

Представим требования:

```text
20 связанных фильтров
cross-filtering
несколько drill-down уровней
ad-hoc slicing
сотни миллионов аналитических rows
OLAP
сложные интерактивные визуализации
```

Это уже может выходить за назначение встроенных Dashboard Chart и Number Card.

Framework widgets хороши для:

```text
операционных KPI
простых управленческих графиков
быстрой визуализации Documents/Reports
Workspace
```

Но они не обязаны заменять специализированную BI-систему.

Правильный вопрос:

> встроенных widgets достаточно для конкретной задачи или мы уже строим отдельную аналитическую подсистему?

---

# Часть XI. Полный учебный пример

## 76. Данные

Создадим несколько `Request`:

```text
REQ-0001 | Support | Open   | High   | 1200
REQ-0002 | Support | Closed | Low    | 500
REQ-0003 | Sales   | Open   | High   | 3000
REQ-0004 | Sales   | Open   | Medium | 1000
REQ-0005 | Admin   | Open   | Low    | 700
```

---

## 77. Number Card №1 — Open Requests

```text
Label         = Open Requests
Type          = Document Type
Document Type = Request
Function      = Count
Filter        = status = Open
```

Ожидаем:

```text
4
```

---

## 78. Number Card №2 — Open Amount

```text
Label                       = Open Amount
Type                        = Document Type
Document Type               = Request
Function                    = Sum
Aggregate Function Based On = amount
Filter                      = status = Open
```

Ожидаем:

```text
1200 + 3000 + 1000 + 700 = 5900
```

---

## 79. Chart №1 — Requests by Department

```text
Chart Type        = Group By
Document Type     = Request
Group By Based On = department
Group By Type     = Count
Type              = Bar
```

Ожидаем:

```text
Support → 2
Sales   → 2
Admin   → 1
```

---

## 80. Chart №2 — Open Amount by Department

```text
Chart Type                  = Group By
Document Type               = Request
Group By Based On           = department
Group By Type               = Sum
Aggregate Function Based On = amount
Filter                      = status = Open
Type                        = Bar
```

Ожидаем:

```text
Support → 1200
Sales   → 4000
Admin   → 700
```

---

## 81. Размещаем их в Workspace

Теперь Workspace может содержать:

```text
[ Open Requests ] [ Open Amount ]

[ Requests by Department          ]

[ Open Amount by Department       ]
```

Сам Workspace не считает эти значения.

Он только показывает созданные:

```text
Number Card
Dashboard Chart
```

Это важное разделение ответственности.

---

# Часть XII. Типичные ошибки

## 82. Ошибка: делать Script Report ради простого Count

Нужно:

```text
count open Requests
```

а создаётся:

```text
Script Report
Python
Custom chart
```

Лишняя сложность.

Используй Number Card / Count.

---

## 83. Ошибка: путать Chart Type и визуальный Type

```text
Chart Type = Sum
Type       = Bar
```

`Sum` — способ расчёта.

`Bar` — способ рисования.

Это не одно поле в разных переводах.

---

## 84. Ошибка: считать `Is Public` отключением permissions

Нет.

`Is Public` не должен использоваться как security bypass.

---

## 85. Ошибка: защищать данные Dynamic Filter-ом

```text
filter = current user's department
```

не заменяет server permissions.

---

## 86. Ошибка: запускать огромный Script Report ради одной карточки

Если можно получить одно число одним aggregate query, это почти всегда лучше.

---

## 87. Ошибка: считать Prepared Report кэшем Dashboard

Report-based Chart и Number Card текущего v16 вызывают Report с:

```text
ignore_prepared_report = 1
```

Поэтому тяжёлый Report нужно оптимизировать отдельно.

---

## 88. Ошибка: использовать Heatmap для чувствительных row-restricted данных без теста

Текущий heatmap path отличается от обычных charts и использует `get_all`.

Проверь доступ под реальным ограниченным User.

---

## 89. Ошибка: Custom method без проверки permissions

```python
@frappe.whitelist()
def kpi():
    return frappe.get_all(...)
```

может выдать больше данных, чем ожидалось.

Whitelisted означает:

> method можно вызвать через Framework endpoint при соответствующих условиях.

Это не означает:

> Framework автоматически придумал правильные business permissions внутри method.

---

## 90. Ошибка: превращать dashboard в тяжёлую BI-систему

Если Workspace начинает состоять из десятков тяжёлых widgets с многомиллионными raw queries, проблема уже архитектурная.

Chart и Number Card должны быть быстрым пользовательским слоем над разумно подготовленными данными.

---

# Мини-практика

## 91. Создай два Number Card

Для `Request`:

### Open Requests

```text
Type = Document Type
Function = Count
status = Open
```

### Open Request Amount

```text
Type = Document Type
Function = Sum
Based On = amount
status = Open
```

Добавь их в Workspace.

---

## 92. Создай два Dashboard Chart

### Requests Created

```text
Chart Type = Count
Based On = creation
Timespan = Last Month
Time Interval = Daily
Type = Line
```

### Requests by Department

```text
Chart Type = Group By
Group By Based On = department
Group By Type = Count
Type = Bar
```

Добавь оба в Workspace.

---

## 93. Проверь permissions

Создай двух Users с разными User Permissions на `Department`.

Открой Workspace под каждым.

Проверь:

```text
Number Card / Document Type
Dashboard Chart / Count
Dashboard Chart / Group By
```

и сравни результаты.

Затем отдельно создай тестовый Heatmap и проверь, ведёт ли он себя так, как ожидает ваша модель доступа.

Не делай выводы о security только по Administrator.

---

## 94. Сделай Report-based Chart

Возьми Script Report из прошлой главы.

Добавь туда простой `chart`.

Создай:

```text
Dashboard Chart
Chart Type = Report
Report Name = Request Analysis
Use Report Chart = ✓
```

Добавь его в Workspace.

Теперь один Script Report используется:

```text
как Report
+
как Dashboard Chart source
```

---

## 95. Сравни стоимость вариантов

Для одной и той же простой метрики попробуй мысленно оценить:

```text
Number Card / Document Type
vs
Number Card / Report
vs
Custom Number Card
```

Если все три могут решить задачу, обычно выбирай верхний вариант:

```text
Document Type
```

потому что он проще и прозрачнее.

---

# Что запомнить

1. **Dashboard Chart и Number Card — отдельные DocTypes, а Workspace только размещает их как blocks.**
2. **Dashboard Chart показывает распределение или динамику, Number Card — одно KPI-значение.**
3. **Dashboard Chart v16 умеет `Count`, `Sum`, `Average`, `Group By`, `Report`, `Custom`.**
4. **Визуальные типы — `Line`, `Bar`, `Percentage`, `Pie`, `Donut`, `Heatmap`.**
5. **Count/Sum/Average используют Date/Datetime поле для временной серии.**
6. **Group By работает по категориям и умеет Count/Sum/Average.**
7. **Обычный DocType chart автоматически исключает `docstatus = 2`.**
8. **Стандартные Count/Sum/Average/Group By paths текущего v16 используют `frappe.get_list()` и поэтому гораздо ближе к permission-aware выборке.**
9. **Текущий Heatmap path использует `frappe.get_all()`, поэтому row-level permissions для чувствительных данных надо проверять отдельно.**
10. **`Is Public` делает widget общедоступнее в Desk, но не должен восприниматься как отключение permissions источника.**
11. **Dynamic Filters — удобство отображения, а не security.**
12. **Dashboard Chart может использовать готовый Query/Script Report.**
13. **Если Script Report уже возвращает `chart`, Dashboard Chart может включить `Use Report Chart`.**
14. **Report-based Dashboard Chart и Number Card текущего v16 вызывают Report с `ignore_prepared_report = 1`.**
15. **Number Card / Document Type умеет Count/Sum/Average/Minimum/Maximum.**
16. **Number Card / Report агрегирует выбранную numeric column результата Report.**
17. **Current v16 report-card widget может пропустить нулевые значения при сборе column values — это важно для Average/Min/Max.**
18. **Percentage Stats Number Card не является универсальным period-over-period BI engine; проверь точную математику filters.**
19. **Custom Number Card вызывает whitelisted method, а Custom Dashboard Chart использует Dashboard Chart Source.**
20. **Custom source/method означает, что ответственность за data permissions лежит на разработчике.**
21. **Dashboard Chart Source — developer-level extension point и в текущем v16 создаётся/изменяется через Developer Mode/App files.**
22. **Не используй тяжёлый Report для KPI, если тот же результат можно получить одной штатной агрегацией.**
23. **Dashboard widgets — хороший операционный UI, но не обязаны заменять специализированную BI-платформу.**

---

## Источники

- [Frappe Framework — Workspace Blocks](https://docs.frappe.io/framework/user/en/desk/workspace/blocks)
- [Frappe Framework v16 — `Dashboard Chart` controller](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [Frappe Framework v16 — `Dashboard Chart` DocType](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart/dashboard_chart.json)
- [Frappe Framework v16 — Dashboard Chart frontend](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart/dashboard_chart.js)
- [Frappe Framework v16 — `ChartWidget`](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/widgets/chart_widget.js)
- [Frappe Framework v16 — `Dashboard Chart Source`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart_source/dashboard_chart_source.py)
- [Frappe Framework v16 — `Dashboard Chart Source` metadata](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/dashboard_chart_source/dashboard_chart_source.json)
- [Frappe Framework v16 — Dashboard utilities](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/utils/dashboard_utils.js)
- [Frappe Framework v16 — Dashboard cache utilities](https://github.com/frappe/frappe/blob/version-16/frappe/utils/dashboard.py)
- [Frappe Framework v16 — `Number Card` controller](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/number_card/number_card.py)
- [Frappe Framework v16 — `Number Card` DocType](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/number_card/number_card.json)
- [Frappe Framework v16 — `NumberCardWidget`](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/widgets/number_card_widget.js)
- [Frappe Framework — Script Report](https://docs.frappe.io/framework/user/en/desk/reports/script-report)

---

Дальше: **38. Data Import / Export**.