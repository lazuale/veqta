# 34. Report Builder

В предыдущих главах мы работали в основном с одним Document: открывали его форму, смотрели Timeline, отправляли письма и печатали.

Теперь переключимся на **много документов сразу**.

Представим, что в `Request` уже накопились сотни записей:

```text
REQ-0001 | Support | High   | Open   | 1200
REQ-0002 | Sales   | Normal | Open   | 500
REQ-0003 | Support | High   | Closed | 700
...
```

Нужно быстро ответить на вопросы:

- какие Requests ещё открыты;
- какие колонки показать;
- как отсортировать их по сумме;
- сколько Requests приходится на каждый Department;
- какова сумма `amount` по Department.

Для этого не обязательно писать SQL или Python.

Во Frappe есть **Report Builder**.

Проверено: **2026-08-31**.

---

## 1. Что такое Report Builder простыми словами

Report Builder — это штатный табличный отчёт над данными одного основного DocType.

Упрощённая схема:

```text
DocType
   ↓
Report View
   ↓
колонки + фильтры + сортировка + группировка
   ↓
табличный отчёт
```

Например:

```text
Request
   ↓
Status = Open
   ↓
показать:
name
subject
department
priority
amount
   ↓
сортировать amount DESC
```

Получаем нужную выборку без отдельного кода отчёта.

Главная мысль:

> **Report Builder не создаёт новые бизнес-данные. Он по-другому выбирает и показывает уже существующие Documents.**

---

## 2. Report View уже есть у DocType

Для обычного DocType не нужно сначала программировать специальную страницу отчёта.

Framework предоставляет **Report View** как один из способов просмотра записей DocType.

То есть у `Request` могут существовать разные представления одних и тех же данных:

```text
Request
├── List View
├── Kanban
├── Calendar
└── Report View
```

Набор доступных представлений зависит от метаданных DocType и настроек интерфейса, но сам Report View — штатная возможность Framework.

Внутри текущего v16 класс `ReportView` даже наследуется от `ListView`:

```text
ReportView extends ListView
```

Это хорошо объясняет их близость: оба работают с набором Documents, но Report View заточен именно под табличное представление и анализ.

---

## 3. List View и Report Builder — не одно и то же

На первый взгляд они похожи: и там, и там строки документов и фильтры.

Но назначение разное.

| List View | Report Builder |
|---|---|
| рабочая очередь документов | табличный анализ данных |
| быстро открыть запись | выбрать нужные колонки |
| статусы, индикаторы, массовые действия | группировки и агрегаты |
| компактное ежедневное представление | более широкая таблица |
| поля обычно задаются настройками List View | пользователь может перестраивать набор колонок |
| подходит для оперативной работы | подходит для анализа и выгрузок |

Например, оператору удобно жить в List View:

```text
REQ-0001   Open
REQ-0002   Review
REQ-0003   Closed
```

А для анализа удобнее Report Builder:

```text
Name      Department   Priority   Amount   Owner
REQ-0001  Support      High       1200     anna@example.com
REQ-0002  Sales        Normal      500     boris@example.com
```

Это одни и те же Documents.

---

## 4. Что пользователь может менять в Report View

В актуальном v16 Report View хранит и применяет, среди прочего:

```text
filters
fields
order_by
add_totals_row
page_length
column_widths
group_by
chart_args
```

Для новичка это можно перевести так:

```text
что отобрать
что показать
как отсортировать
нужна ли итоговая строка
сколько строк показывать
какая ширина колонок
как сгруппировать
как построить небольшой chart
```

Chart пока подробно не разбираем — этому посвящена отдельная глава.

---

## 5. Колонки

Допустим, `Request` содержит:

```text
subject
department
priority
status
amount
description
owner
creation
modified
```

Для конкретного отчёта нужны только:

```text
name
department
priority
amount
```

В Report View можно собрать именно такой набор колонок.

Упрощённо:

```text
все поля Request
        ↓
выбираем нужные
        ↓
Name | Department | Priority | Amount
```

Можно также:

- добавлять колонку;
- убирать колонку;
- менять порядок;
- изменять ширину.

Поэтому не нужно добавлять отдельное поле в DocType только потому, что хочется переставить колонки в одном отчёте.

---

## 6. Поля Child Table тоже можно использовать

Пусть есть:

```text
Request
└── items → Request Item
```

А внутри `Request Item`:

```text
item
qty
amount
```

Report View текущего v16 умеет предлагать поля Child Table как дополнительные колонки.

Например:

```text
Name      Department   Item      Qty
REQ-0001  Support      Laptop    1
REQ-0001  Support      Mouse     2
```

Это полезно, но здесь появляется очень важный эффект.

---

## 7. Почему один родитель может появиться несколько раз

Есть один Request:

```text
REQ-0001
```

В нём две строки Child Table:

```text
items
├── Laptop | 1
└── Mouse  | 2
```

Если отчёт показывает только поля самого Request, логично получить одну строку:

```text
REQ-0001 | Support
```

Но если добавить поле из Child Table:

```text
Request Item.item
```

результат может стать таким:

```text
REQ-0001 | Support | Laptop
REQ-0001 | Support | Mouse
```

Это **не обязательно дубль или ошибка**.

Причина простая:

```text
1 Parent
   ↓
2 Child rows
   ↓
2 строки результата
```

Текущий DatabaseQuery Frappe действительно строит join с Child Table, и тесты v16 отдельно проверяют, что родитель с двумя дочерними строками даёт две строки результата при выборе child-поля.

Поэтому перед подсчётами всегда надо понимать **гранулярность строки отчёта**.

---

## 8. Гранулярность — очень полезное слово

Пусть отчёт состоит только из полей `Request`.

Тогда одна строка примерно означает:

```text
один Request
```

Добавили `Request Item.item`.

Теперь строка может означать:

```text
один Request × одна строка Request Item
```

Это особенно важно при суммах и подсчётах.

Например, если у `REQ-0001`:

```text
Request.amount = 1000
```

и у него три child-строки, отчёт с child-полями может визуально повторить `1000` три раза.

Это ещё не означает, что сумма Request стала `3000`.

Нужно сначала понять, **что представляет одна строка результата**.

---

## 9. Фильтры

Report Builder использует обычную систему фильтрации Frappe.

Например:

```text
Status = Open
```

или:

```text
Department = Support
Priority = High
```

Получаем:

```text
все Request
     ↓
Status = Open
AND Department = Support
AND Priority = High
     ↓
только подходящие записи
```

Тип доступного значения зависит от типа поля.

Например:

```text
Select
→ выбрать значение

Link
→ выбрать связанную запись

Date
→ выбрать дату или диапазон

Currency / Int / Float
→ сравнивать числа
```

Это тот же общий принцип фильтров, который мы уже видели в List View.

---

## 10. Можно фильтровать и по Child Table

Пусть:

```text
Request
└── items
    └── item
```

Можно строить выборку с учётом дочерних строк.

Например, найти Requests, где есть:

```text
item = Laptop
```

Но снова помним про структуру результата:

> как только запрос начинает использовать Child Table, количество возвращаемых строк может определяться не только количеством Parent Documents.

Это нормальное следствие relational query, а не странность интерфейса.

---

## 11. Сортировка

Допустим, нужны самые крупные Requests сверху.

Задаём:

```text
Amount
Descending
```

Получаем примерно:

```text
REQ-0031 | 9800
REQ-0014 | 7200
REQ-0042 | 5100
REQ-0001 | 1200
```

Сохранённый Report Builder хранит сортировку в настройках отчёта.

Если явная сортировка не задана, серверная логика сохранённого Report Builder использует обычный fallback по `creation desc`.

---

## 12. Самое полезное: Group By

Представим 100 Requests.

Смотреть все строки не нужно.

Нужно узнать:

> сколько Requests приходится на каждый Department?

Выбираем:

```text
Group By = Department
Aggregate = Count
```

Получаем:

```text
Support | 42
Sales   | 31
Finance | 27
```

Вместо 100 документов теперь видим три агрегированные строки.

---

## 13. В v16 доступны три штатные агрегатные функции

В текущем интерфейсе Group By есть:

```text
Count
Sum
Average
```

На уровне backend разрешены те же функции:

```text
count
sum
avg
```

### Count

Сколько записей в группе:

```text
Department = Support
Count = 42
```

### Sum

Сумма числового поля:

```text
Department = Support
Sum of Amount = 125000
```

### Average

Среднее числового поля:

```text
Priority = High
Average of Amount = 3200
```

Для `Sum` и `Average` интерфейс предлагает именно числовые поля.

---

## 14. Пример Count

Есть:

```text
REQ-0001 | Support
REQ-0002 | Support
REQ-0003 | Sales
REQ-0004 | Support
REQ-0005 | Sales
```

Group By:

```text
Department
Count
```

Результат:

```text
Support | 3
Sales   | 2
```

То есть Report Builder фактически отвечает на вопрос:

> сколько строк попало в каждую группу?

---

## 15. Пример Sum

Есть:

```text
REQ-0001 | Support | 100
REQ-0002 | Support | 250
REQ-0003 | Sales   | 400
```

Настраиваем:

```text
Group By = Department
Function = Sum
Field = Amount
```

Получаем:

```text
Support | 350
Sales   | 400
```

Никакой отдельный Python-код для такой задачи не нужен.

---

## 16. Пример Average

Есть:

```text
High   | 100
High   | 300
Normal | 150
```

Настраиваем:

```text
Group By = Priority
Function = Average
Field = Amount
```

Получаем:

```text
High   | 200
Normal | 150
```

Для простой аналитики этого часто достаточно.

---

## 17. Group By — не универсальный SQL-конструктор

Можно подумать:

> если есть Group By, значит через Report Builder можно собрать вообще любой запрос.

Нет.

У него специально ограниченная модель.

Например, текущий v16 прямо запрещает некоторые комбинации группировки между Parent и разными Child Table и показывает сообщение:

```text
Parent-to-child or child-to-different-child grouping is not allowed.
```

Это хорошая граница продукта.

Report Builder предназначен для понятных отчётов вокруг одного основного DocType и его дочерних данных, а не для произвольной реляционной аналитики всей базы.

---

## 18. Group By и Show Totals — разные вещи

Не путай два режима.

### Group By

Меняет структуру результата:

```text
много отдельных Requests
        ↓
по одному результату на группу
```

Например:

```text
Support | 42
Sales   | 31
```

### Show Totals

Добавляет итоговую строку к обычной таблице, где это применимо.

То есть логика другая:

```text
обычные строки
+ итоговая строка снизу
```

Если задача звучит:

> «сделай отдельную строку на каждый Department»

это Group By.

Если:

> «оставь обычные строки, но покажи итог»

это Show Totals.

---

## 19. Report Builder может показать небольшой Chart

В текущем v16 у Report View есть встроенная область charts и настройки `chart_args`.

То есть табличный отчёт можно дополнить простой визуализацией.

Но пока достаточно помнить:

```text
Report Builder
→ прежде всего таблица

Chart
→ дополнительное представление результата
```

Полноценные Dashboard Chart и Number Card разберём отдельно в главе 37.

---

## 20. Несохранённый Report View уже запоминает настройки пользователя

Есть важное различие.

Пользователь открыл Report View для `Request` и поменял:

```text
columns
filters
sort
group_by
chart
```

При этом он ещё **не создавал отдельный Report Document**.

В таком случае v16 умеет сохранить часть текущих настроек как пользовательские настройки представления.

Схематично:

```text
User
  ↓
Report View Request
  ↓
его личные настройки вида
```

Это удобно для повседневной работы.

---

## 21. А Save / Save As создаёт настоящий `Report`

Если конфигурацию нужно сохранить как именованный отчёт, создаётся отдельный Document:

```text
Report
```

Например:

```text
Report Name = Open Requests by Department
Ref DocType = Request
Report Type = Report Builder
```

Внутри сохраняется JSON конфигурации.

Упрощённо:

```json
{
  "filters": ["..."],
  "fields": ["..."],
  "order_by": "...",
  "page_length": 20,
  "column_widths": {},
  "group_by": {},
  "chart_args": {}
}
```

Точный JSON не нужно писать руками.

Интерфейс собирает его сам.

---

## 22. Сохранённый Report не хранит копию результата

Это один из главных моментов главы.

Представим, сегодня отчёт показывает:

```text
42 Open Requests
```

Мы сохранили его как:

```text
Open Requests
```

Завтра часть Requests закрыли и появились новые.

Открываем тот же Report и можем увидеть:

```text
38 Open Requests
```

Почему?

Потому что сохранилась не таблица из 42 строк, а **правило построения таблицы**:

```text
какие поля
какие фильтры
какая сортировка
какая группировка
```

Схема:

```text
Report Document
      ↓
сохранённая конфигурация
      ↓
новый запрос к актуальным данным
      ↓
актуальный результат
```

Report Builder — не snapshot.

---

## 23. Report Builder не выдаёт дополнительные права на данные

Допустим, сохранён общий отчёт:

```text
All Requests
```

Анна по своим permissions может читать только Department A.

Борис — только Department B.

Они открывают один и тот же Report.

Правильная модель:

```text
Report configuration
        ↓
permission-aware query
        ↓
Anna  → разрешённые ей Documents
Boris → разрешённые ему Documents
```

Текущий v16 исполняет сохранённый Report Builder через `frappe.get_list(...)`/DatabaseQuery, а не через безусловный `get_all()`.

Поэтому:

> **Report Builder меняет представление данных, но не является способом обойти permissions.**

---

## 24. Permission Level тоже учитывается

В `Request` есть:

```text
subject        Perm Level = 0
internal_cost  Perm Level = 1
```

Пользователь имеет доступ к Request, но не имеет права читать уровень 1.

Он не должен получить `internal_cost` просто потому, что открыл Report View.

В текущем `reportview.py` поля с повышенным `permlevel` удаляются из запроса, если у пользователя нет доступа к этому Permission Level.

То есть логика главы 19 продолжает действовать и здесь.

---

## 25. `Report Hide`

У DocField есть свойство:

```text
Report Hide
```

Если оно включено, текущий backend Report View удаляет это поле из набора запрашиваемых полей.

Например:

```text
technical_note
Report Hide = ✓
```

Тогда поле не предназначено для обычного Report View.

Но не делай из этого замену permissions.

Разница:

```text
Report Hide
→ не показывать поле в Report View

Permission Level
→ реальное ограничение доступа к полю
```

Если значение действительно секретное, решать это нужно permissions, а не только визуальным флагом отчёта.

---

## 26. Кто может сохранить именованный Report

Здесь есть два разных права:

```text
право пользоваться Report View
        ≠
право создавать Report Documents
```

Backend v16 при создании сохранённого Report Builder проверяет:

```text
Create на Report
+
Read на исходный DocType
```

В стандартных permissions текущего v16 `Create / Write / Delete` на `Report` есть у:

```text
Administrator
System Manager
Report Manager
```

У обычного `Desk User` стандартно есть чтение/запуск/печать Report, но нет `Create`.

Это не жёсткий закон системы — permissions можно изменить.

Но из коробки полезно ожидать именно такое разделение.

---

## 27. Roles самого Report и права на данные — тоже разные уровни

У `Report` есть таблица `Roles`.

Она отвечает на вопрос:

> кому доступен сам этот отчёт как объект интерфейса?

При создании нестандартного Report текущий controller может заполнить Roles на основании level-0 ролей исходного DocType.

Но даже если пользователь имеет доступ к самому Report:

```text
Open Requests by Department
```

это всё ещё не означает:

```text
можно читать каждый Request
```

Всегда разделяем:

```text
доступ к Report
        +
доступ к данным Ref DocType
```

---

## 28. Inline editing не отменяет правила документа

Report View v16 построен на DataTable и имеет механизм редактора ячеек.

То есть совместимые поля можно редактировать прямо из таблицы, когда интерфейс и permissions это позволяют.

Но это не означает:

```text
Report Builder = обойти Form View
```

По-прежнему имеют значение:

```text
Write permission
Read Only
Permission Level
docstatus
Workflow
серверные validate
другие ограничения Document lifecycle
```

Если сервер не разрешает изменение, наличие редактируемой таблицы не должно это отменить.

---

## 29. Экспорт

Report Builder удобно использовать как подготовленную таблицу для выгрузки.

Текущий v16 имеет отдельный backend экспорта Report View.

Для крупной выгрузки Framework может отправить экспорт в background job и затем выслать пользователю ссылку на готовый файл по email.

И здесь действует тот же принцип:

```text
экспортируется результат разрешённого запроса
```

а не произвольный дамп таблицы базы.

---

## 30. Один основной DocType — важная граница

Допустим, нужно:

```text
Request
+ Department
+ Request Item
```

Если `Department` связан Link-полем, а `Request Item` является Child Table, Report Builder часто вполне достаточен.

Но теперь задача:

> взять Request, произвольно соединить его с Budget, несколькими журналами, исторической таблицей и вычислить несколько сложных SQL-выражений.

Это уже не нормальная задача Report Builder.

Удобная граница:

```text
один основной DocType
+ его штатные поля
+ связанные/дочерние данные, которые умеет Report View
+ простая фильтрация
+ Count / Sum / Average
→ Report Builder
```

Если требуется произвольный запрос к структуре базы — дальше смотрим на **Query Report**.

---

## 31. Когда уже нужен Query Report

Report Builder перестаёт быть удобным, когда требование звучит примерно так:

```text
соединить несколько таблиц по своей логике
```

или:

```text
сделать сложный SQL-расчёт
```

или:

```text
нужны CASE, сложные агрегаты, несколько JOIN
```

Тогда следующий уровень:

```text
Report Builder
      ↓ не хватает
Query Report
```

Query Report разбирается в следующей главе.

---

## 32. Когда Query Report тоже не подходит

Допустим, результат требует:

- нескольких этапов вычислений;
- Python-логики;
- обращения к внешнему API;
- сложного алгоритма;
- формирования данных, которые неудобно получить одним SQL-запросом.

Тогда может понадобиться:

```text
Script Report
```

или уже код собственного App.

Получается понятная лестница:

```text
Report Builder
      ↓ недостаточно
Query Report
      ↓ недостаточно
Script Report / App code
```

Не начинай с Python, если `Group By → Sum` уже полностью решает задачу.

---

## 33. Report Builder — не BI-система

Он очень удобен для оперативной аналитики внутри Frappe:

```text
фильтр
таблица
группировка
простая агрегация
быстрая выгрузка
```

Но не надо пытаться превратить каждый Report Builder в огромный аналитический слой.

Если задача требует:

- десятков источников;
- тяжёлой исторической аналитики;
- сложной модели показателей;
- больших витрин;
- множества взаимосвязанных визуализаций;

нужно уже отдельно проектировать аналитический слой.

Report Builder хорош именно потому, что остаётся простым.

---

## 34. Маленькая практическая модель выбора

Есть требования:

| Требование | Что выбрать |
|---|---|
| показать Open Requests | Report Builder |
| оставить только несколько колонок | Report Builder |
| сортировать по Amount | Report Builder |
| Count по Department | Report Builder |
| Sum Amount по Department | Report Builder |
| добавить поля Child Table | Report Builder |
| произвольный SQL JOIN нескольких сущностей | Query Report |
| сложный Python-расчёт | Script Report |
| KPI на Workspace | Dashboard Chart / Number Card |

Это и есть правильный порядок усложнения.

---

## 35. Частая ошибка: сохранять отдельный Report на каждый мелкий фильтр

Представим:

```text
My Open Requests
My High Requests
My Support Requests
My Open Support Requests
My High Open Support Requests
```

Очень быстро появляется свалка из десятков почти одинаковых Reports.

Если конфигурация нужна только одному пользователю для повседневного просмотра, часто достаточно его настроек Report View.

Отдельный именованный Report имеет смысл, когда это действительно повторно используемое представление:

```text
Open Requests by Department
Monthly Request Summary
Requests with Items
```

То есть не надо превращать `Report` в каталог каждого клика пользователя.

---

## 36. Частая ошибка: считать повторённый Parent дублем данных

Увидели:

```text
REQ-0001 | Laptop
REQ-0001 | Mouse
```

и сразу решили:

> в базе два REQ-0001.

Нет.

Сначала проверь, есть ли в отчёте поля Child Table.

Может быть:

```text
Parent REQ-0001
└── две child-строки
```

и Report Builder совершенно корректно показывает две строки результата.

---

## 37. Частая ошибка: считать Report способом выдать доступ

Неправильная модель:

```text
дал пользователю Report
→ теперь он видит все данные отчёта
```

Правильная:

```text
дал доступ к Report
        ↓
пользователь может открыть конфигурацию отчёта
        ↓
данные всё равно проходят обычные permission checks
```

Если пользователю не хватает прав на `Request`, чинить это нужно в модели permissions, а не в Report Builder.

---

## 38. Частая ошибка: сразу писать SQL

Требование:

> показать количество Requests по Department.

Можно написать Query Report с:

```sql
SELECT department, COUNT(*) ...
```

Но в Report Builder уже есть:

```text
Group By = Department
Count
```

Если штатный механизм полностью закрывает задачу, SQL здесь только добавит поддержку собственного кода без выгоды.

---

# Мини-практика

Для учебного DocType `Request` создай или используй поля:

```text
subject      Data
department   Link → Department
priority     Select
status       Select
amount       Currency
items        Table → Request Item
```

В `Request Item`:

```text
item         Data
qty          Float
```

Создай несколько Requests в разных Departments и с разными Amount.

### Задание 1

Открой Report View и оставь колонки:

```text
Name
Department
Priority
Amount
```

### Задание 2

Добавь фильтр:

```text
Status = Open
```

### Задание 3

Отсортируй:

```text
Amount DESC
```

### Задание 4

Сделай:

```text
Group By = Department
Count
```

Посмотри, сколько Requests приходится на каждый Department.

### Задание 5

Измени агрегат:

```text
Group By = Department
Sum = Amount
```

### Задание 6

Убери группировку и добавь колонку `Request Item.item`.

Создай Request с двумя child-строками и посмотри, почему один Request появляется в результате несколько раз.

### Задание 7

Попробуй сохранить конфигурацию как именованный Report.

Если кнопка или операция недоступна обычному пользователю, проверь permissions на системный DocType `Report` и сравни их с правами `Report Manager`.

### Задание 8

Определи подходящий механизм:

```text
A. Open Requests за этот месяц
B. Count Requests по Department
C. Sum Amount по Department
D. Request + произвольный JOIN с независимым Budget
E. сложный показатель, вычисляемый Python-алгоритмом
```

Ответ:

```text
A → Report Builder
B → Report Builder
C → Report Builder
D → Query Report
E → Script Report / App code
```

---

# Что запомнить

1. **Report Builder — штатный no-code табличный отчёт над одним основным DocType.**
2. **Report View близок к List View, но предназначен для выбора колонок, анализа и группировок.**
3. **Можно использовать поля Child Table, но тогда один Parent может дать несколько строк результата.**
4. **Group By в актуальном v16 поддерживает Count, Sum и Average.**
5. **Sum и Average работают с числовыми полями.**
6. **Сохранённый Report Builder хранит конфигурацию отчёта, а не копию его строк.**
7. **Один и тот же сохранённый Report может показывать разным пользователям разные строки из-за permissions.**
8. **Permission Level продолжает ограничивать доступные поля.**
9. **`Report Hide` управляет участием поля в Report View, но не заменяет security permissions.**
10. **Для сохранения именованного Report нужны права на системный DocType `Report`; в стандартном v16 Create есть у Report Manager, System Manager и Administrator.**
11. **Report Builder — не произвольный SQL-конструктор.**
12. **Если его возможностей не хватает, следующий уровень — Query Report, а потом Script Report.**

---

## Источники

- [Frappe Framework — Report Builder](https://docs.frappe.io/framework/user/en/desk/reports/report-builder)
- [Frappe Framework — Desk](https://docs.frappe.io/framework/user/en/desk)
- [`frappe/desk/reportview.py`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/desk/reportview.py)
- [`frappe/public/js/frappe/views/reports/report_view.js`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/views/reports/report_view.js)
- [`frappe/public/js/frappe/ui/group_by/group_by.js`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/ui/group_by/group_by.js)
- [`frappe/core/doctype/report/report.py`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report/report.py)
- [`frappe/core/doctype/report/report.json`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report/report.json)
- [`frappe/tests/test_db_query.py`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/tests/test_db_query.py)

Дальше: **35. Query Report**.
