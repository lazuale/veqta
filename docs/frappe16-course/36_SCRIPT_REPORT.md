# 36. Script Report

В двух предыдущих главах мы прошли первые два уровня отчётности:

```text
Report Builder
→ собрать отчёт настройками

Query Report
→ описать выборку одним SQL-запросом
```

Но бывают задачи, где одного SQL уже недостаточно или он превращается в плохо читаемую конструкцию.

Например, нужно:

- получить данные несколькими запросами;
- применить к строкам Python-логику;
- собрать результат из разных источников;
- сделать вычисления, которые удобнее выразить функциями;
- подготовить не только таблицу, но и summary;
- вернуть chart вместе с таблицей;
- по-разному строить результат в зависимости от фильтров;
- переиспользовать код собственного App.

Для этого во Frappe есть **Script Report**.

Проверено: **2026-08-31**.

---

## 1. Что такое Script Report простыми словами

Script Report — это отчёт, результат которого готовит **Python-код**.

Упрощённо:

```text
фильтры пользователя
        ↓
      Python
        ↓
columns + data
        ↓
таблица отчёта
```

Но Script Report может вернуть больше:

```text
Python
  ├── columns
  ├── data
  ├── message
  ├── chart
  ├── report_summary
  └── skip_total_row
```

То есть это уже не просто запрос к базе.

Это маленькая серверная программа, задача которой — **подготовить данные отчёта**.

---

## 2. Когда Script Report действительно нужен

Не надо начинать с Python только потому, что Python мощнее.

Для отчётов полезна такая лестница:

```text
Report Builder
      ↓ не хватает
Query Report
      ↓ не хватает
Script Report
```

### Report Builder

Подходит, если нужно:

```text
выбрать поля
отфильтровать записи
отсортировать
сгруппировать
посчитать Count / Sum / Average
```

### Query Report

Подходит, если результат удобно выразить:

```text
одним SELECT
```

с `JOIN`, `CASE`, `GROUP BY`, агрегатами и другими SQL-конструкциями.

### Script Report

Нужен, когда алгоритм естественнее выглядит так:

```text
получить данные A
получить данные B
обработать их Python-кодом
собрать итоговые строки
посчитать summary
подготовить chart
вернуть результат
```

Главная мысль:

> **Script Report нужен не потому, что он «самый продвинутый», а потому, что задача уже стала алгоритмом, а не одной выборкой.**

---

## 3. Маленький пример

Представим DocType `Request`:

```text
name
subject
department
status
priority
amount
creation
```

Нужно получить открытые Requests и дополнительно вычислить категорию суммы:

```text
amount < 10 000
→ Regular

amount >= 10 000
→ Large
```

В SQL это тоже можно сделать через `CASE`.

Но допустим, дальше появятся дополнительные правила, summary и chart.

Тогда Python может быть понятнее:

```python
for row in requests:
    if row.amount >= 10000:
        row.amount_band = "Large"
    else:
        row.amount_band = "Regular"
```

Именно такой код естественно живёт в Script Report.

---

## 4. Script Report всё равно является `Report`

Script Report — не отдельная независимая подсистема.

Он хранится как Document системного DocType:

```text
Report
```

с:

```text
Report Type = Script Report
```

У `Report` в текущем v16 есть, среди прочего:

```text
Report Name
Ref DocType
Module
Is Standard
Report Type
Filters
Columns
Report Script
Javascript
Roles
Prepared Report
Disable Prepared Report Automation
Snapshot Report
```

То есть Python-код — только одна часть объекта Report.

Сам Framework по-прежнему отвечает за:

- экран отчёта;
- фильтры;
- запуск;
- доступ к Report;
- вывод таблицы;
- chart;
- summary;
- export;
- prepared-report механизм.

---

## 5. Самое важное разделение: Standard и non-standard

У Script Report есть два принципиально разных режима.

```text
Script Report
├── Is Standard = Yes
│   └── Python-файл внутри App
│
└── Is Standard = No
    └── Script хранится в самом Report
        и выполняется через safe_exec
```

Это **не просто два способа сохранить один и тот же текст**.

У них разная модель исполнения.

### Standard Script Report

Это обычный код приложения:

```text
App
└── Module
    └── report
        └── request_analysis
            ├── request_analysis.json
            ├── request_analysis.py
            └── request_analysis.js
```

Python выполняется как Python-модуль App.

### Non-standard Script Report

Код хранится в поле:

```text
Report Script
```

самого Document `Report` и запускается через restricted execution:

```text
safe_exec
```

Для стабильной сложной логики эти два режима нельзя считать равнозначными.

---

## 6. Не путай `Is Standard = No` и тип `Custom Report`

В документации иногда встречается выражение:

```text
custom Script Report
```

Обычно под ним имеется в виду:

```text
Report Type = Script Report
Is Standard = No
```

Но у DocType `Report` существует ещё отдельное значение:

```text
Report Type = Custom Report
```

Это **другой тип Report**.

Поэтому в этой главе будем говорить точнее:

```text
Standard Script Report
→ Report Type = Script Report
→ Is Standard = Yes

Non-standard Script Report
→ Report Type = Script Report
→ Is Standard = No
```

Так меньше шансов перепутать два разных механизма.

---

## 7. Standard Script Report — основной вариант для кода App

Официальная документация Frappe описывает именно его как основной способ разработки Script Report.

Чтобы сохранить Standard Report в текущем v16, backend проверяет:

```text
user = Administrator
AND
Developer Mode = enabled
```

Если отчёт пытается сохранить другой пользователь, Framework выдаёт ошибку.

Если Developer Mode выключен, Standard Report тоже нельзя нормально создать как development artifact.

Почему ограничения такие строгие?

Потому что Standard Script Report становится частью файлов приложения:

```text
Git
↓
App
↓
установка на Site
↓
Report
```

Это уже **application code**, а не просто локальная настройка одного Site.

---

## 8. Какие файлы появляются у Standard Script Report

Упрощённо структура выглядит так:

```text
<app>/<module>/report/request_analysis/
├── __init__.py
├── request_analysis.json
├── request_analysis.py
└── request_analysis.js
```

### `.json`

Описывает сам стандартный `Report`:

```text
имя
Ref DocType
Report Type
Roles
и другие metadata
```

### `.py`

Содержит серверный Python-код отчёта.

### `.js`

Содержит клиентские настройки Query Report UI — чаще всего filters и дополнительное поведение интерфейса отчёта.

Главный файл для этой главы:

```text
request_analysis.py
```

---

## 9. Минимальный Standard Script Report

Базовый интерфейс очень маленький:

```python
def execute(filters=None):
    columns = []
    data = []

    return columns, data
```

То есть Framework ожидает функцию:

```text
execute
```

и передаёт ей:

```text
filters
```

На выходе минимум нужны:

```text
columns
+
data
```

---

## 10. `filters` — обычный словарь входных параметров

Пусть пользователь выбрал:

```text
Status = Open
Department = Support
```

В `execute()` придёт структура примерно такого смысла:

```python
{
    "status": "Open",
    "department": "Support",
}
```

Обычно удобно сразу сделать:

```python
filters = frappe._dict(filters or {})
```

Тогда значения можно читать так:

```python
filters.status
filters.department
```

или как обычный dict:

```python
filters.get("status")
filters.get("department")
```

---

## 11. Первый рабочий пример

Допустим, у нас есть учебный DocType `Request`.

```python
import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "fieldname": "request",
            "label": _("Request"),
            "fieldtype": "Link",
            "options": "Request",
            "width": 140,
        },
        {
            "fieldname": "subject",
            "label": _("Subject"),
            "fieldtype": "Data",
            "width": 240,
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 140,
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "amount_band",
            "label": _("Amount Band"),
            "fieldtype": "Data",
            "width": 120,
        },
    ]


def get_data(filters):
    db_filters = {}

    if filters.status:
        db_filters["status"] = filters.status

    if filters.department:
        db_filters["department"] = filters.department

    requests = frappe.get_list(
        "Request",
        filters=db_filters,
        fields=["name", "subject", "department", "amount"],
        order_by="creation desc",
    )

    data = []

    for row in requests:
        data.append(
            {
                "request": row.name,
                "subject": row.subject,
                "department": row.department,
                "amount": row.amount,
                "amount_band": "Large" if (row.amount or 0) >= 10000 else "Regular",
            }
        )

    return data
```

Здесь уже хорошо видна роль Script Report:

```text
получили Documents
        ↓
прогнали Python-логику
        ↓
собрали новую структуру строк
        ↓
вернули таблицу
```

---

## 12. Почему мы разделили `execute`, `get_columns` и `get_data`

Можно написать всё одной функцией.

Например 200 строк внутри:

```python
def execute(filters=None):
    ...
```

Но такой отчёт быстро становится неудобным.

Для небольшого Script Report уже полезно держать структуру:

```text
execute()
├── get_columns()
├── get_data()
├── get_chart_data()
└── get_report_summary()
```

Это не обязательное правило Framework.

Это просто понятная организация кода.

Например текущий стандартный report `Website Analytics` во Frappe использует ровно такую идею: отдельные методы получают data, chart и summary, а `run()` собирает результат.

---

## 13. `data` может быть списком словарей

Удобный вариант:

```python
data = [
    {
        "request": "REQ-0001",
        "department": "Support",
        "amount": 1200,
    },
    {
        "request": "REQ-0002",
        "department": "Sales",
        "amount": 500,
    },
]
```

Тогда значения связываются с columns через:

```text
fieldname
```

Например:

```text
column.fieldname = amount
row["amount"] = 1200
```

Это обычно наиболее читаемый формат.

---

## 14. `data` может быть и списком списков

Также допустимо:

```python
data = [
    ["REQ-0001", "Support", 1200],
    ["REQ-0002", "Sales", 500],
]
```

Тогда порядок значений должен совпасть с порядком columns:

```text
columns
1. request
2. department
3. amount

row
1. REQ-0001
2. Support
3. 1200
```

Текущий v16 при обработке результата умеет нормализовать list/tuple rows в словари по `fieldname` колонок.

Но для сложного отчёта словари обычно проще читать и поддерживать.

---

## 15. Что описывает `columns`

Типичная колонка:

```python
{
    "fieldname": "request",
    "label": _("Request"),
    "fieldtype": "Link",
    "options": "Request",
    "width": 140,
}
```

Основные свойства уже знакомы по DocField:

```text
fieldname
label
fieldtype
options
width
```

Например:

```python
{
    "fieldname": "amount",
    "label": _("Amount"),
    "fieldtype": "Currency",
    "width": 120,
}
```

или:

```python
{
    "fieldname": "department",
    "label": _("Department"),
    "fieldtype": "Link",
    "options": "Department",
}
```

Правильный `fieldtype` нужен не только ради красивой подписи.

Он влияет на форматирование и поведение значения в report UI.

---

## 16. В Report есть и отдельная таблица `Columns`

Текущий DocType `Report` также содержит Child Table:

```text
Columns
```

У её строк есть:

```text
Fieldname
Label
Fieldtype
Options
Width
```

Для **non-standard Script Report** текущая серверная реализация прямо использует эти Columns, если script записал строки в `result`.

Для **Standard Script Report** наиболее прозрачный и source-consistent вариант — вернуть `columns` из `execute()` явно.

Почему здесь стоит быть аккуратным?

Официальная страница документации говорит, что `columns` можно не возвращать, если они заданы в Report. Но текущая ветка `version-16` для standard report вызывает Python-модуль так:

```text
execute(filters)
→ возвращённый результат
→ generate_report_result()
```

и первый элемент этого результата используется как `columns`.

Поэтому в учебном standard report мы **возвращаем columns явно**.

Это делает контракт отчёта очевидным и не зависит от неоднозначности документации.

---

## 17. Filters можно описывать прямо в Report

У `Report` в текущем v16 есть Child Table:

```text
Filters
```

У фильтра есть, среди прочего:

```text
Fieldname
Label
Fieldtype
Mandatory
Options
Default
Wildcard Filter
```

Для простого фильтра этого достаточно.

Например:

```text
Label      = Department
Fieldname  = department
Fieldtype  = Link
Options    = Department
Mandatory  = 0
```

Значение затем попадёт в:

```python
filters.department
```

---

## 18. Для Standard Report остаётся и `.js`

Классический Script Report также может описывать фильтры в файле:

```text
request_analysis.js
```

Например:

```javascript
frappe.query_reports["Request Analysis"] = {
    filters: [
        {
            fieldname: "department",
            label: __("Department"),
            fieldtype: "Link",
            options: "Department",
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: ["Open", "Closed"],
            default: "Open",
        },
    ],
};
```

JS особенно полезен, если фильтру нужна клиентская логика.

Например:

```text
depends_on
динамический default
изменение options
реакция на другой filter
```

Не нужно тащить JS в отчёт, если достаточно простых статичных Filters из metadata.

---

## 19. Что именно возвращает `execute()`

Минимум:

```python
return columns, data
```

Но текущий report pipeline v16 умеет принять до шести значений в строго определённом порядке:

```text
1. columns
2. data
3. message
4. chart
5. report_summary
6. skip_total_row
```

То есть полный вариант:

```python
return (
    columns,
    data,
    message,
    chart,
    report_summary,
    skip_total_row,
)
```

Framework затем раскладывает этот результат примерно так:

```text
columns
result
message
chart
report_summary
skip_total_row
```

Если возвращено только два элемента, остальные становятся пустыми.

---

## 20. `message`

Иногда вместе с таблицей нужно показать дополнительное сообщение.

Например:

```python
message = "Only open requests are included."
```

Тогда можно вернуть:

```python
return columns, data, message
```

Не нужно использовать `message` как замену таблице или строить в нём весь интерфейс.

Это дополнительная информация к результату отчёта.

---

## 21. `chart`

Script Report может сразу вернуть конфигурацию chart.

Упрощённый пример:

```python
chart = {
    "data": {
        "labels": ["Support", "Sales", "Finance"],
        "datasets": [
            {
                "name": "Requests",
                "values": [12, 7, 4],
            }
        ],
    },
    "type": "bar",
}
```

И вернуть:

```python
return columns, data, None, chart
```

Тогда один Script Report может показать:

```text
chart
+
таблицу
```

Подробно chart-механику разберём в следующей главе.

Пока достаточно понять: **chart может быть частью ответа Script Report, его не обязательно строить отдельным Dashboard Chart**.

---

## 22. `report_summary`

`report_summary` — это несколько важных показателей, которые показываются отдельно от основной таблицы.

Например:

```text
Open Requests: 23
Large Requests: 5
Total Amount: 184000
```

Пример структуры:

```python
report_summary = [
    {
        "label": _("Open Requests"),
        "value": 23,
        "datatype": "Int",
    },
    {
        "label": _("Large Requests"),
        "value": 5,
        "datatype": "Int",
    },
]
```

Возвращаем пятым элементом:

```python
return columns, data, None, chart, report_summary
```

Это удобно, когда пользователю нужны одновременно:

```text
несколько KPI сверху
+
детализация снизу
```

---

## 23. Полный небольшой пример с summary

```python
import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})

    rows = frappe.get_list(
        "Request",
        filters={"status": filters.status or "Open"},
        fields=["name", "subject", "department", "amount"],
        order_by="creation desc",
    )

    columns = [
        {
            "fieldname": "request",
            "label": _("Request"),
            "fieldtype": "Link",
            "options": "Request",
        },
        {
            "fieldname": "subject",
            "label": _("Subject"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
        },
        {
            "fieldname": "amount_band",
            "label": _("Amount Band"),
            "fieldtype": "Data",
        },
    ]

    data = []
    large_count = 0

    for row in rows:
        is_large = (row.amount or 0) >= 10000

        if is_large:
            large_count += 1

        data.append(
            {
                "request": row.name,
                "subject": row.subject,
                "amount": row.amount,
                "amount_band": "Large" if is_large else "Regular",
            }
        )

    report_summary = [
        {
            "label": _("Requests"),
            "value": len(data),
            "datatype": "Int",
        },
        {
            "label": _("Large Requests"),
            "value": large_count,
            "datatype": "Int",
        },
    ]

    return columns, data, None, None, report_summary
```

Здесь Python уже делает больше, чем простой SQL-result:

```text
получает rows
→ вычисляет классификацию
→ считает отдельный KPI
→ строит data
→ строит report_summary
```

---

## 24. `Add Total Row` и `skip_total_row`

У `Report` есть флаг:

```text
Add Total Row
```

Если он включён, Framework может добавить итоговую строку к результату.

Но Script Report может вернуть:

```python
skip_total_row = True
```

шестым элементом.

Например:

```python
return columns, data, None, None, report_summary, True
```

Тогда автоматическая total row не добавляется.

Это полезно, если:

- totals уже рассчитаны самим отчётом;
- суммирование строк не имеет смысла;
- в таблице смешаны строки разного уровня;
- итог выводится через `report_summary`.

В текущем backend имя именно:

```text
skip_total_row
```

---

## 25. Script Report не означает «можно забыть про permissions»

Это одна из самых важных частей главы.

При открытии отчёта Frappe всё равно проверяет:

```text
доступ к самому Report
+
Roles отчёта
+
Report permission на Ref DocType
```

После выполнения report pipeline также пытается отфильтровать возвращённые строки с учётом связанного DocType там, где структура результата позволяет это сделать.

Но Python-код Script Report может получать данные разными способами.

И эти способы ведут себя по-разному.

Поэтому безопасность данных нельзя строить на мысли:

> «Раз это Report, Frappe потом сам обязательно вырежет всё запрещённое».

Для произвольных агрегатов, вычисленных строк и сложной структуры результата это особенно опасное предположение.

---

## 26. `frappe.get_list()` и `frappe.get_all()` — не одно и то же

Для текущего v16 официальная Database API формулирует различие прямо.

### `frappe.get_list()`

```python
frappe.get_list("Request", ...)
```

применяет permissions текущего session user к получаемым records.

### `frappe.get_all()`

```python
frappe.get_all("Request", ...)
```

получает records **без применения permissions**.

Упрощённо:

```text
get_list
→ permission-aware выборка

get_all
→ получить все подходящие rows
```

Поэтому в пользовательском отчёте разумный default:

```text
сначала get_list
```

А `get_all` использовать только когда действительно понимаешь, почему permission filtering не нужен или реализован отдельно.

Подробно ORM и Database API будут в главе 52.

---

## 27. Raw SQL тоже не становится permission-aware автоматически

Standard Script Report может выполнить:

```python
frappe.db.sql(...)
```

или использовать Query Builder.

Но сам факт, что код выполняется внутри Script Report, **не добавляет в произвольный SQL автоматически все Frappe permission conditions**.

Например:

```python
rows = frappe.db.sql(
    """
    SELECT name, department, amount
    FROM `tabRequest`
    """,
    as_dict=True,
)
```

не равен по permission-смыслу:

```python
rows = frappe.get_list(
    "Request",
    fields=["name", "department", "amount"],
)
```

Поэтому автор Script Report отвечает не только за правильный расчёт, но и за правильную модель доступа к исходным данным.

---

## 28. Особенно осторожно с агрегатами

Допустим, пользователь имеет право видеть только Department A.

Но report Python сначала получил все Requests и посчитал:

```text
Department A = 100000
Department B = 900000
```

А итоговые строки уже не являются конкретными Documents:

```text
Department | Total Amount
```

Framework не всегда может взять такую агрегированную строку и надёжно восстановить:

> какие исходные Documents пользователь имел право видеть?

Поэтому правильная архитектура:

```text
сначала сформировать permission-correct исходную выборку
        ↓
потом агрегировать
```

а не:

```text
сначала взять вообще всё
        ↓
надеяться, что итоговый report сам очистится
```

---

## 29. Script Report должен быть без побочных эффектов

Standard Script Report — обычный Python-код App.

Технически такой Python обладает большой свободой.

Но отчёт не должен становиться скрытой бизнес-операцией.

Плохая идея:

```python
def execute(filters=None):
    # обновить статусы документов
    # создать записи
    # отправить документы дальше по процессу
    # потом показать таблицу
```

Почему это опасно?

Пользователь может:

```text
открыть report
refresh
сменить filter
снова refresh
экспортировать
запустить prepared report
```

Один и тот же код может выполниться несколько раз просто из-за просмотра отчёта.

Поэтому хороший Script Report:

```text
читает
считает
формирует результат
```

А изменение бизнес-данных лучше делать через:

```text
Document action
whitelisted method
controller
background job
отдельный процесс
```

в зависимости от задачи.

---

## 30. Non-standard Script Report устроен иначе

Теперь вернёмся к:

```text
Report Type = Script Report
Is Standard = No
```

В этом режиме Python-код находится прямо в поле:

```text
Report Script
```

Текущий v16 выполняет его через:

```python
safe_exec(...)
```

То есть это не unrestricted Python-модуль App.

Используется ограниченное script environment.

---

## 31. В non-standard Script Report нет обычного `execute(filters)`

Это важное отличие текущего v16.

Для Standard Report Framework делает примерно:

```text
найти Python module
        ↓
вызвать execute(filters)
```

Для non-standard Report логика другая:

```text
взять текст Report Script
        ↓
safe_exec(script)
        ↓
прочитать variables result / data
```

В текущем source перед выполнением создаются переменные:

```text
filters
data = None
result = None
```

Поэтому простой non-standard script выглядит по смыслу так:

```python
result = frappe.get_list(
    "Request",
    fields=["name", "subject", "status"],
    filters={"status": filters.get("status")},
)
```

А columns можно задать в таблице:

```text
Report → Columns
```

Текущий backend затем возвращает:

```text
self.get_columns()
+
result
```

---

## 32. Почему здесь мы не используем `return ...`

На официальной странице Script Report всё ещё встречается пример для custom report с:

```python
return frappe.db.get_all(...)
```

Но текущий `version-16` source исполняет содержимое `Report Script` напрямую через `safe_exec` и затем читает:

```text
result
или
data
```

Более того, описание самого поля `Report Script` в текущем DocType подсказывает:

```text
result = [result]
```

или legacy-вариант:

```text
data = [columns], [result]
```

Поэтому в этом учебнике для non-standard Script Report используем форму, соответствующую текущему backend:

```python
result = ...
```

а не top-level `return`.

---

## 33. `safe_exec` должен быть разрешён конфигурацией

Текущий `safe_exec.py` проверяет настройку:

```text
server_script_enabled
```

в common site configuration.

Если restricted server-side scripts не разрешены, выполнение прекращается ошибкой:

```text
Server Scripts are disabled
```

Это относится и к non-standard Script Report, потому что его `Report Script` выполняется через тот же `safe_exec` механизм.

То есть:

```text
Is Standard = No
```

не означает:

> можно на любом Site просто сохранить Python и он сразу заработает.

Site должен разрешать safe server scripting.

Подробно эту настройку разберём в главе о Server Script.

---

## 34. Кто может сохранять non-standard Script Report в текущем v16

Здесь тоже есть деталь, которую лучше брать из source.

Для:

```text
Report Type = Script Report
Is Standard = No
```

текущий `Report.validate()` вызывает проверку роли:

```text
Script Manager
```

`Administrator` проходит `frappe.only_for()` как специальный пользователь.

То есть backend ограничивает редактирование такого исполняемого script-кода сильнее, чем обычное редактирование Report metadata.

Это логично: пользователь, который может менять server-side script отчёта, фактически меняет исполняемую серверную логику.

---

## 35. Standard и non-standard — когда какой выбирать

### Non-standard Script Report

Уместен, когда:

- нужно локальное решение на одном Site;
- логика небольшая;
- хватает Script API / safe_exec;
- не нужен полноценный Python package;
- допустима зависимость от `server_script_enabled`.

### Standard Script Report

Уместен, когда:

- отчёт является частью собственного App;
- логика стабильная;
- нужны обычные Python imports;
- код надо тестировать;
- код надо хранить в Git;
- отчёт должен одинаково устанавливаться на другие Sites;
- появляются helper-функции и нормальная структура модуля.

Для серьёзного повторяемого функционала хороший ориентир:

```text
прототип / локальная логика
→ non-standard

стабильная часть продукта
→ Standard Script Report в App
```

Но переходить через промежуточный non-standard вариант необязательно. Если сразу понятно, что отчёт является частью App, его можно сразу делать Standard.

---

## 36. `Prepared Report`

Некоторые Script Reports работают долго.

Например:

```text
миллионы rows
сложные агрегаты
несколько тяжёлых запросов
большой период
```

Если выполнять всё синхронно, пользователь будет ждать открытый browser request.

Для этого есть:

```text
Prepared Report
```

Упрощённо:

```text
обычный report
→ посчитать сейчас
→ вернуть результат

Prepared Report
→ поставить расчёт в background
→ сохранить подготовленный результат
→ открыть его после завершения
```

Официальная документация текущего Framework также описывает notification и повторное открытие готового Prepared Report с теми же filters.

---

## 37. v16 умеет автоматически включить Prepared Report

Это интересное поведение текущего source.

Для Script Report задан threshold:

```text
15 seconds
```

Когда начинается выполнение и:

```text
Prepared Report = 0
AND
Disable Prepared Report Automation = 0
```

Framework запускает timer.

Если report успел закончить быстрее 15 секунд:

```text
timer cancels
```

Если выполнение пересекло 15 секунд:

```text
Prepared Report
→ автоматически устанавливается в 1
```

То есть медленный Script Report может после первого долгого запуска сам перейти на prepared-модель для следующих запусков.

---

## 38. `Disable Prepared Report Automation`

Если автоматическое переключение не нужно, у Script Report есть:

```text
Disable Prepared Report Automation
```

Этот флаг означает:

```text
не включать Prepared Report автоматически
```

Он **не запрещает** вручную включить:

```text
Prepared Report = 1
```

Это разные настройки.

---

## 39. Timeout Prepared Report

Когда `Prepared Report` включён, у Report доступен:

```text
Timeout (In Seconds)
```

Текущее описание поля указывает default timeout:

```text
1500 seconds
```

То есть prepared execution — не бесконечный процесс.

Но если обычный отчёт регулярно требует огромных ресурсов, сначала стоит проверить архитектуру самого отчёта:

```text
лишние запросы?
N+1?
слишком широкий период?
нет нужных индексов?
данные агрегируются в Python вместо базы?
```

Prepared Report помогает с пользовательским ожиданием, но не превращает плохой алгоритм в хороший.

---

## 40. Не делай N+1 без необходимости

Типичная ошибка начинающего:

```python
requests = frappe.get_list("Request", fields=["name", "department"])

for request in requests:
    department = frappe.get_doc("Department", request.department)
```

Если Requests 10 000, можно случайно получить:

```text
1 основной query
+
10 000 дополнительных queries
```

Это называется типичной проблемой N+1.

Если нужное значение можно получить:

- сразу в `get_list`;
- через join/query builder;
- одним дополнительным запросом;
- заранее собранным mapping;

лучше сделать так.

Script Report даёт свободу Python, но свобода легко позволяет написать очень медленный код.

---

## 41. Не переноси всё вычисление в Python

Вторая крайность:

```text
вытащить миллион строк
↓
GROUP BY вручную в Python
↓
SUM вручную в Python
```

если база могла сделать:

```sql
GROUP BY
SUM
COUNT
```

намного раньше.

Хороший Script Report часто сочетает уровни:

```text
DB
→ эффективно отбирает и агрегирует большие данные

Python
→ выполняет бизнес-алгоритм и собирает результат
```

То есть Script Report не отменяет SQL и Query Builder.

Он позволяет использовать их как части более крупного алгоритма.

---

## 42. Когда логика уже не должна жить внутри report-файла

Представим, что `request_analysis.py` разросся до 1500 строк и содержит:

```text
расчёт SLA
определение категории
бизнес-правила стоимости
общие справочники
логику, которая нужна ещё API и background job
```

Тогда проблема уже не в типе отчёта.

Переиспользуемую бизнес-логику лучше вынести в нормальные модули App:

```text
App
├── services
├── utils
├── domain logic
└── report
    └── request_analysis.py
```

А report оставить тонким потребителем:

```text
получить filters
↓
вызвать reusable logic
↓
подготовить columns/data/chart/summary
```

Иначе отчёт превращается в скрытое ядро приложения.

---

## 43. Script Report и отдельная Page — не одно и то же

Script Report уже даёт:

```text
filters
таблицу
chart
summary
export
prepared report
report permissions
```

Поэтому не нужно создавать отдельную Desk Page, если задача всё ещё является отчётом.

Page нужна, когда UI уже выходит за модель report:

```text
нестандартная компоновка
много интерактивных панелей
сложное редактирование
мастер действий
отдельное приложение внутри Desk
```

Для обычного аналитического экрана Script Report часто намного дешевле и правильнее.

---

## 44. Advanced v16: Snapshot Report

В текущем v16 у Script Report есть ещё:

```text
Snapshot Report
```

Это уже продвинутая ветка.

Официальная документация описывает её как работу через синхронизированные аналитические данные и DuckDB.

Для Standard Script Report Framework может вместо:

```python
execute(filters)
```

вызвать:

```python
execute_snapshot_report(filters)
```

если Snapshot Report включён.

Это **не автоматическая кнопка ускорения любого отчёта**.

Обычный report нужно специально переписать под snapshot/OLAP-модель.

На первом проходе курса достаточно знать, что такой механизм в v16 существует.

---

## 45. Report Builder, Query Report и Script Report рядом

| Задача | Инструмент |
|---|---|
| выбрать колонки и фильтры без кода | Report Builder |
| один хорошо выражаемый SQL `SELECT` | Query Report |
| несколько шагов Python-обработки | Script Report |
| вычислить дополнительные поля Python-логикой | Script Report |
| вернуть chart вместе с таблицей | Script Report |
| вернуть report summary | Script Report |
| сложная переиспользуемая бизнес-логика | код App + тонкий Script Report |
| полностью нестандартный интерактивный UI | отдельная Page / frontend |

Удобная карта:

```text
данные уже можно показать штатно?
        │
        ├── да → Report Builder
        │
        └── нет
             ↓
один SQL нормально описывает результат?
        │
        ├── да → Query Report
        │
        └── нет
             ↓
нужен серверный алгоритм?
        │
        ├── да → Script Report
        │
        └── нет → пересмотреть постановку
```

---

## 46. Типичные ошибки

### Ошибка 1. Писать Script Report для обычной фильтрации

Нужно:

```text
Status = Open
Department = Support
```

а пишется 200 строк Python.

Сначала проверь Report Builder.

---

### Ошибка 2. Переписывать нормальный SQL в Python loops

Если база умеет эффективно сделать:

```text
JOIN
GROUP BY
SUM
COUNT
```

необязательно вытаскивать все строки и пересчитывать вручную.

---

### Ошибка 3. Использовать `get_all` по привычке

```python
frappe.get_all(...)
```

не применяет пользовательские permissions.

Для пользовательского отчёта это должно быть осознанным решением.

---

### Ошибка 4. Считать Report UI границей безопасности

Спрятанная колонка или фильтр не исправляет неправильную серверную выборку.

Безопасность начинается с того, **какие данные сервер вообще получил и вернул**.

---

### Ошибка 5. Изменять Documents при просмотре отчёта

Refresh отчёта не должен случайно менять бизнес-состояние системы.

---

### Ошибка 6. Смешать Standard и non-standard механику

Standard:

```text
.py
execute(filters)
обычный App Python
```

Non-standard:

```text
Report Script
safe_exec
result / data
```

Это разные execution paths.

---

### Ошибка 7. Считать Prepared Report лечением любого тормоза

Сначала оптимизируй data path.

Потом решай, нужен ли background execution.

---

## 47. Мини-практика

Сделай учебный Script Report:

```text
Request Analysis
```

Для DocType:

```text
Request
```

Добавь filters:

```text
Status
Department
```

В таблице покажи:

```text
Request
Subject
Department
Amount
Amount Band
```

Правило:

```text
Amount >= 10000
→ Large

иначе
→ Regular
```

Затем добавь:

```text
report_summary
```

с двумя значениями:

```text
Requests
Large Requests
```

После этого проверь отчёт под двумя пользователями с разными User Permissions на `Department`.

Если используешь:

```python
frappe.get_list
```

сравни результат с вариантом:

```python
frappe.get_all
```

и убедись, что понимаешь разницу до того, как использовать второй вариант в реальном report.

---

## 48. Практика на выбор правильного уровня

Определи подходящий механизм.

### A

Нужно показать Open Requests и четыре поля.

Ответ:

```text
Report Builder
```

### B

Нужно одним запросом посчитать сумму Amount по Department с `CASE`.

Ответ:

```text
Query Report
```

### C

Нужно получить Requests, применить несколько Python-правил, сформировать summary и chart.

Ответ:

```text
Script Report
```

### D

Один и тот же расчёт нужен Report, REST API и background job.

Ответ:

```text
вынести расчёт в reusable application code
+
Script Report только вызывает его
```

### E

Нужно при каждом открытии отчёта автоматически менять Status документов.

Ответ:

```text
не делать это в отчёте
```

Для изменения данных нужен отдельный action/process.

---

## 49. Что запомнить

1. **Script Report строит результат серверным Python-кодом.**
2. **Сначала проверяй Report Builder, потом Query Report и только потом Script Report.**
3. **Standard Script Report — часть App и Git.**
4. **Standard Report в текущем v16 сохраняется Administrator-ом в Developer Mode.**
5. **Standard Python вызывается через `execute(filters)`.**
6. **Минимальный результат — `columns, data`.**
7. **Полный pipeline умеет `message`, `chart`, `report_summary`, `skip_total_row`.**
8. **`data` может быть списком dict или списком rows.**
9. **`frappe.get_list` применяет permissions, `frappe.get_all` — нет.**
10. **Raw SQL внутри Script Report не получает Frappe row permissions автоматически.**
11. **Non-standard Script Report выполняется через `safe_exec` и использует `result` / `data`, а не обычный module `execute()`.**
12. **Для non-standard script должен быть разрешён `server_script_enabled`.**
13. **Текущий backend требует `Script Manager` для редактирования non-standard Script Report, кроме Administrator.**
14. **Медленный Script Report в текущем v16 может автоматически получить `Prepared Report = 1` после 15 секунд выполнения.**
15. **Report должен читать и считать, а не тайно менять бизнес-данные.**
16. **Если логика нужна не только отчёту, вынеси её из report-файла в reusable code App.**

---

## Источники

- [Frappe Framework — Script Report](https://docs.frappe.io/framework/user/en/desk/reports/script-report)
- [Frappe Framework — How To Make Script Reports](https://docs.frappe.io/framework/user/en/guides/reports-and-printing/how-to-make-script-reports)
- [Frappe Framework — Database API](https://docs.frappe.io/framework/user/en/api/database)
- [Frappe Framework v16 — `Report` controller](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report/report.py)
- [Frappe Framework v16 — `Report` DocType](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report/report.json)
- [Frappe Framework v16 — Query Report execution pipeline](https://github.com/frappe/frappe/blob/version-16/frappe/desk/query_report.py)
- [Frappe Framework v16 — `safe_exec`](https://github.com/frappe/frappe/blob/version-16/frappe/utils/safe_exec.py)
- [Frappe Framework v16 — `Report Column`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report_column/report_column.json)
- [Frappe Framework v16 — `Report Filter`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report_filter/report_filter.json)
- [Frappe Framework v16 — standard `ToDo` Script Report](https://github.com/frappe/frappe/tree/version-16/frappe/desk/report/todo)
- [Frappe Framework v16 — `Website Analytics` Script Report](https://github.com/frappe/frappe/blob/version-16/frappe/website/report/website_analytics/website_analytics.py)

---

Дальше: **37. Dashboard Chart и Number Card**.