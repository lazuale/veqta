# 35. Query Report

В прошлой главе мы разобрали **Report Builder** — штатный способ собрать табличный отчёт без SQL и Python.

Но у Report Builder есть граница. Иногда нужно:

- соединить несколько таблиц через `JOIN`;
- посчитать выражение, которого нет как отдельного поля;
- сделать сложный `CASE`;
- сгруппировать данные не так, как позволяет обычный Report Builder;
- вернуть ровно тот набор строк, который проще описать одним SQL-запросом.

Для таких задач во Frappe есть **Query Report**.

Проверено: **2026-08-31**.

---

## 1. Что такое Query Report простыми словами

Query Report — это отчёт, данные которого возвращает **один SQL-запрос**.

Схема выглядит так:

```text
фильтры пользователя
        ↓
    SQL query
        ↓
строки + колонки
        ↓
интерфейс Query Report
```

Например, есть `Request`:

```text
REQ-0001 | Support | Open   | 1200
REQ-0002 | Sales   | Open   | 500
REQ-0003 | Support | Closed | 700
```

Самый простой Query Report может выполнить:

```sql
SELECT
    name,
    department,
    status,
    amount
FROM `tabRequest`
WHERE status = 'Open'
ORDER BY creation DESC
```

и показать:

```text
REQ-0001 | Support | Open | 1200
REQ-0002 | Sales   | Open | 500
```

Здесь уже не интерфейс Frappe решает, какие строки выбрать.

Их выбирает SQL.

---

## 2. Когда сначала всё-таки нужен Report Builder

Query Report не должен становиться первым инструментом просто потому, что SQL знакомее.

Правильная последовательность:

```text
Report Builder
      ↓ не хватает
Query Report
      ↓ не хватает
Script Report
```

Если задача звучит так:

> покажи Open Requests, добавь Department и Amount, отсортируй по Amount

Report Builder обычно достаточно.

Если задача звучит так:

> соедини Request с Department, посчитай несколько агрегатов и выведи вычисляемую категорию через CASE

Query Report уже может быть логичнее.

Главная причина переходить к SQL — **необходимость выразить выборку**, а не желание написать код ради кода.

---

## 3. Где Query Report находится в модели Frappe

`Query Report` — один из типов системного DocType:

```text
Report
```

В актуальном v16 у `Report.report_type` есть варианты:

```text
Report Builder
Query Report
Script Report
Custom Report
```

У Query Report нас будут особенно интересовать:

```text
Report Name
Ref DocType
Module
Is Standard
Report Type
Query
Filters
Columns
Roles
Prepared Report
```

То есть SQL — только одна часть объекта Report.

Сам Report ещё задаёт интерфейс, колонки, фильтры и доступ.

---

## 4. Что такое `Ref DocType`

При создании Report нужно указать:

```text
Ref DocType
```

Например:

```text
Ref DocType = Request
```

Очень важно правильно понять смысл этого поля.

Оно **не означает**:

> SQL разрешено читать только таблицу Request.

Query Report вполне может сделать:

```sql
FROM `tabRequest` r
LEFT JOIN `tabDepartment` d
    ON d.name = r.department
```

`Ref DocType` нужен как основной контекст отчёта, в том числе для permissions.

Упрощённо:

```text
Ref DocType
→ к какому бизнес-объекту относится Report
→ на каком DocType проверяется право Report
→ какой контекст получает отчёт
```

Но **SQL-границей** это поле не является.

---

## 5. Почему таблица называется `tabRequest`

В обычном пользовательском интерфейсе мы говорим:

```text
DocType = Request
```

В базе стандартная таблица такого DocType обычно называется:

```text
tabRequest
```

Поэтому SQL выглядит так:

```sql
SELECT name
FROM `tabRequest`
```

Для `Department`:

```text
DocType: Department
DB table: tabDepartment
```

Для `Order Item`:

```text
DocType: Order Item
DB table: tabOrder Item
```

Не нужно самостоятельно создавать эти таблицы для обычных DocType — ими управляет schema/migration механизм Frappe.

---

## 6. Первый полноценный Query Report

Допустим, у `Request` есть:

```text
name
subject
department
priority
status
amount
creation
```

Хотим получить открытые Requests.

SQL:

```sql
SELECT
    r.name AS request,
    r.subject,
    r.department,
    r.priority,
    r.amount
FROM `tabRequest` r
WHERE r.status = 'Open'
ORDER BY r.creation DESC
```

Теперь одна строка результата означает примерно:

```text
один Request
```

Это важно помнить так же, как в Report Builder: прежде чем считать суммы, нужно понимать **гранулярность строки**.

---

## 7. Query Report предназначен для чтения

Query Report — не место для `UPDATE`, `DELETE` или `INSERT`.

Перед выполнением текущий v16 вызывает проверку:

```python
check_safe_sql_query(self.query)
```

После этого запрос выполняется примерно так:

```python
frappe.db.sql(self.query, filters)
```

Текущая проверка допускает read-only начало запроса:

```text
SELECT
EXPLAIN
```

Также в текущей реализации отдельно допускается `WITH` для MariaDB.

При этом блокируются опасные конструкции вроде:

```text
INTO OUTFILE
INTO DUMPFILE
```

Главная мысль для новичка:

> **Query Report — SQL для получения данных, а не для изменения базы.**

Если задача должна что-то изменить в Documents, это уже не отчёт.

---

## 8. Filters — пользовательские параметры SQL

Постоянно писать отдельный Report для каждого Department бессмысленно.

Лучше сделать фильтр.

Например, в `Filters` создаём:

```text
Label      = Department
Fieldname  = department
Fieldtype  = Link
Options    = Department
```

А SQL меняем на:

```sql
SELECT
    r.name AS request,
    r.subject,
    r.department,
    r.amount
FROM `tabRequest` r
WHERE r.department = %(department)s
ORDER BY r.creation DESC
```

Теперь пользователь выбирает Department в интерфейсе, а значение попадает в параметр:

```text
%(department)s
```

---

## 9. Не собирай SQL строковой склейкой

Правильный вариант:

```sql
WHERE r.department = %(department)s
```

Именно параметры передаются Frappe в `frappe.db.sql(self.query, filters)`.

Не нужно пытаться собирать что-то вроде:

```text
"... WHERE department = '" + value + "'"
```

У Query Report уже есть штатный механизм параметров.

Он и понятнее, и безопаснее ручной строковой подстановки.

---

## 10. Mandatory Filter

Если без значения SQL не имеет смысла, фильтр можно сделать обязательным.

Например:

```text
Department
Mandatory = ✓
```

Тогда пользователь сначала должен выбрать Department.

Это полезно не только для удобства.

Иногда обязательный фильтр защищает от случайного запуска очень тяжёлой выборки на всей таблице.

Например:

```text
From Date = обязательный
To Date   = обязательный
```

может быть гораздо разумнее, чем каждый раз считать отчёт за несколько лет.

---

## 11. Типы фильтров

В текущем v16 `Report Filter` поддерживает привычные типы, среди них:

```text
Check
Currency
Data
Date
Datetime
Dynamic Link
Float
Int
Link
Select
Time
```

Выбирай тип по смыслу данных.

Например:

```text
Department
→ Link / Department

Status
→ Select

From Date
→ Date

Minimum Amount
→ Currency
```

Это даёт пользователю нормальный Frappe-control вместо текстового поля для всего подряд.

---

## 12. Wildcard Filter

Допустим, пользователь должен искать Requests по части Subject.

Filter:

```text
Fieldname = subject
Fieldtype = Data
Wildcard Filter = ✓
```

SQL:

```sql
WHERE r.subject LIKE %(subject)s
```

В текущем frontend v16 для такого фильтра значение оборачивается в `%`.

Например пользователь ввёл:

```text
printer
```

в запрос уйдёт значение примерно:

```text
%printer%
```

То есть получится поиск по вхождению.

---

## 13. Columns — это не просто подписи

SQL вернул данные, но Frappe ещё должен понимать, **что означает каждая колонка**.

Для этого у Query Report есть таблица `Columns`.

Например:

| Fieldname | Label | Fieldtype | Options |
|---|---|---|---|
| `request` | Request | Link | Request |
| `department` | Department | Link | Department |
| `priority` | Priority | Data | |
| `amount` | Amount | Currency | |

Зачем указывать тип?

Потому что тогда Frappe понимает, например:

```text
request
→ это Link на Request

amount
→ это денежное число
```

От этого зависят форматирование, ссылки и часть последующей permission-обработки результата.

Поэтому в новых отчётах лучше задавать Columns явно, особенно для `Link`.

---

## 14. Старый синтаксис alias тоже существует

Исторически метаданные колонки можно было кодировать прямо в SQL alias.

Например:

```sql
SELECT
    r.name AS "Request:Link/Request:160"
FROM `tabRequest` r
```

Смысл примерно такой:

```text
Label     = Request
Fieldtype = Link
Options   = Request
Width     = 160
```

Текущий Frappe сохраняет совместимость с таким форматом.

Но для нового отчёта обычно понятнее держать:

```text
SQL
+
Columns metadata
```

раздельно.

---

## 15. JOIN — одна из главных причин использовать Query Report

Пусть `Request.department` ссылается на `Department`.

А в `Department` есть:

```text
manager
```

Report Builder уже может быть неудобен, если хочется собрать точную SQL-выборку.

Query Report:

```sql
SELECT
    r.name AS request,
    r.department,
    d.manager,
    r.priority,
    r.amount
FROM `tabRequest` r
LEFT JOIN `tabDepartment` d
    ON d.name = r.department
WHERE r.status = %(status)s
ORDER BY r.creation DESC
```

Теперь пользователь видит и Request, и данные связанного Department.

Это один SQL-запрос, а не цикл из сотен `get_doc()`.

---

## 16. GROUP BY и агрегаты

Можно сделать отчёт не по отдельным Requests, а по Department.

Например:

```sql
SELECT
    r.department,
    COUNT(*) AS request_count,
    SUM(r.amount) AS total_amount,
    AVG(r.amount) AS average_amount
FROM `tabRequest` r
WHERE r.status = %(status)s
GROUP BY r.department
ORDER BY request_count DESC
```

Результат:

```text
Support | 42 | 125000 | 2976.19
Sales   | 31 |  87000 | 2806.45
```

Здесь гранулярность уже другая:

```text
одна строка
=
один Department
```

Именно такие произвольные SQL-агрегации — сильная сторона Query Report.

---

## 17. Вычисляемые колонки

Query Report не ограничен существующими DocFields.

Например:

```sql
SELECT
    r.name AS request,
    r.amount,
    CASE
        WHEN r.amount >= 100000 THEN 'Large'
        WHEN r.amount >= 10000 THEN 'Medium'
        ELSE 'Small'
    END AS amount_group
FROM `tabRequest` r
```

`amount_group` не обязан существовать в `Request`.

Это вычисляемый результат отчёта.

Именно здесь Query Report начинает заметно отличаться от простого просмотра Documents.

---

## 18. Но Query Report — не `frappe.get_list()`

Это одна из самых важных вещей всей главы.

В Report Builder сервер получает данные через permission-aware механизмы Framework.

В Query Report сначала выполняется сам SQL:

```text
raw SQL
   ↓
результат
```

А затем Frappe выполняет дополнительную обработку результата с учётом permissions там, где может связать полученные колонки с DocTypes.

Упрощённо текущая схема v16 выглядит так:

```text
проверить доступ к Report
        ↓
проверить Report permission на Ref DocType
        ↓
выполнить SQL
        ↓
нормализовать строки
        ↓
постфильтровать результат по доступным связям
        ↓
показать пользователю
```

Поэтому нельзя думать:

> раз это Frappe Report, любой мой SQL автоматически получает абсолютно те же ограничения, что `frappe.get_list()`.

Это неверная модель.

---

## 19. Какие права проверяются до запуска

При открытии Query Report текущий v16 проверяет несколько вещей.

Во-первых, разрешён ли сам Report пользователю по его `Roles`.

Во-вторых, есть ли у пользователя permission:

```text
Report
```

на `Ref DocType`.

Например:

```text
Report: Open Requests
Ref DocType: Request
```

пользователю нужен `Report` permission на `Request`.

Если Report отключён через `Disabled`, он тоже не выполняется.

То есть Query Report — это не свободный SQL console для любого Desk User.

---

## 20. `Roles` самого Report

У `Report` есть собственная таблица:

```text
Roles
```

Например, можно разрешить отчёт только роли:

```text
Request Manager
```

Это дополнительный барьер:

```text
роль разрешена для Report?
        ↓ да
есть Report permission на Ref DocType?
        ↓ да
можно запускать Report
```

`Roles` отчёта не заменяет обычные permissions DocType.

Это ещё один слой поверх них.

---

## 21. Что происходит с User Permission после SQL

Текущий `query_report.py` не просто отдаёт raw результат браузеру.

После выполнения Report Frappe вызывает фильтрацию результата и анализирует связанные DocTypes, которые может определить по колонкам.

Например, колонка описана как:

```text
Fieldtype = Link
Options   = Department
```

Тогда Framework понимает:

> значение этой колонки является Department.

И может учитывать ограничения пользователя для этого DocType.

Поэтому корректное описание Link-колонок важно не только для красивого клика по значению.

---

## 22. Почему сложный агрегат нужно проверять особенно внимательно

Рассмотрим простой построчный отчёт:

```text
request  = REQ-0001
owner    = anna@example.com
department = Support
```

Здесь системе проще понять, к какому Document относится строка.

А теперь агрегат:

```text
Support | 42 | 125000
```

Что это за Document?

Никакой.

Это результат сразу 42 Documents.

Значит, обычные document-level идеи вроде:

```text
Only if Creator
```

уже нельзя механически переносить на одну агрегированную строку.

Если отчёт содержит чувствительные данные и сложные агрегаты, его нужно тестировать именно под ограниченным пользователем, а не только под Administrator.

---

## 23. Permission Level — особенно важная граница

В главе про Permission Level мы видели:

```text
internal_cost
Perm Level = 1
```

и, например:

```text
Manager
→ Read level 1

Operator
→ нет Read level 1
```

Для обычного permission-aware чтения это защищает поле.

Но Query Report выполняет **написанный автором raw SQL**.

В текущем `query_report.py` нет обычного механизма `get_permitted_fields()`, который автоматически вырезал бы из произвольного SQL все поля недоступного Permission Level.

Поэтому опасно написать:

```sql
SELECT
    r.name,
    r.internal_cost
FROM `tabRequest` r
```

и считать:

> Frappe сам уберёт `internal_cost` у Operator.

Так проектировать Query Report нельзя.

Если поле чувствительное, безопаснее:

- вообще не выбирать его в общем Report;
- или создать отдельный Report только для нужных Roles;
- или перейти к серверной реализации, где permission-логика явно контролируется.

---

## 24. Masking и Permission Level — не одно и то же

Текущий Query Report pipeline умеет применять masking к соответствующим колонкам Ref DocType.

Но это не означает:

```text
Mask
=
полноценная автоматическая защита любого raw SQL
```

И тем более Masking не заменяет Permission Level.

Запомни две разные задачи:

```text
Mask
→ скрыть часть отображаемого значения

Permission Level
→ разрешить или запретить доступ к группе полей
```

В Query Report автор отчёта обязан отдельно думать, какие данные он вообще возвращает SQL-запросом.

---

## 25. Хорошая модель безопасности Query Report

Думай о нём так:

```text
SQL определяет данные

Report Roles
→ кто вообще может открыть этот Report

Ref DocType permissions
→ есть ли право запускать отчёты этого типа

Query Report post-filter
→ дополнительная защита известных связей
```

Но последний слой не должен становиться оправданием для небезопасного SQL.

Лучшее правило:

> **не возвращай SQL-запросом данные, которые аудитория отчёта не должна видеть.**

---

## 26. Тестируй не только под Administrator

Очень частая ошибка:

```text
создали Query Report
→ открыли Administrator
→ всё работает
→ готово
```

Administrator имеет особый доступ и совершенно не показывает реальное поведение обычных пользователей.

Для отчёта с permissions нужен минимум такой тест:

```text
Administrator
Manager
обычный Operator
пользователь с User Permission
пользователь без доступа к части данных
```

Особенно проверяй:

- строки;
- Link-поля;
- чувствительные колонки;
- агрегаты;
- Export.

---

## 27. Export — отдельное право

То, что пользователь может открыть Query Report, ещё не обязательно означает, что он может его выгрузить.

Текущий export Query Report вызывает проверку `can_export()` для `Ref DocType`.

То есть для выгрузки нужен соответствующий `Export` permission.

Это хорошо продолжает модель из Role Permission Manager:

```text
Report
→ можно запускать отчёт

Export
→ можно выгружать данные
```

Не путай эти действия.

---

## 28. Кто может создавать Query Report в текущем v16

Здесь есть полезное расхождение между документацией и текущим backend.

Официальная документация Query Report описывает создание через System Manager.

Но в актуальном `version-16` у `Report.validate()` для нестандартных Reports есть дополнительная проверка:

```python
if self.is_standard == "No":
    if self.report_type not in ("Report Builder", "Custom Report"):
        frappe.only_for("Script Manager", True)
```

То есть для текущего нестандартного:

```text
Query Report
```

сервер явно требует `Script Manager` сверх обычной возможности работать с Report.

Это как раз тот случай, когда документация отстаёт от текущего исходного кода v16.

---

## 29. `Is Standard = No`

Такой Report хранится как обычная запись текущего Site.

Упрощённо:

```text
Report
Is Standard = No
        ↓
запись в базе Site
```

Это удобно для локального отчёта или быстрого прототипа.

Но если отчёт стал частью стабильной функциональности App, хранить важный SQL только как случайную локальную запись уже неудобно.

---

## 30. `Is Standard = Yes`

Standard Report предназначен для поставки вместе с App.

Текущий v16 при обычном интерактивном сохранении Standard Report требует:

```text
Administrator
+
Developer Mode
```

А при сохранении в Developer Mode Report экспортируется в файлы приложения.

Модель:

```text
локальный эксперимент
→ Is Standard = No

стабильная часть собственного App
→ Is Standard = Yes
→ Developer Mode
→ Git
```

К теме Standard vs Custom мы ещё вернёмся отдельно в главе 46.

---

## 31. Query Report и разные СУБД

Query Report передаёт SQL непосредственно базе.

Поэтому SQL-диалект имеет значение.

Например, часть старых примеров Frappe написана с расчётом на MariaDB.

Но современный Framework может работать не только с ней.

Следствие:

> raw SQL обычно менее переносим между СУБД, чем высокоуровневые API Framework.

Если App должен поддерживать разные database backends, Query Report нужно проектировать с этим ограничением в голове.

Не стоит автоматически считать любой MariaDB-specific SQL универсальным Frappe SQL.

---

## 32. Prepared Report

Некоторые отчёты могут быть тяжёлыми.

У `Report` есть:

```text
Prepared Report
```

При таком режиме результат может готовиться отдельно и затем использоваться как подготовленный результат вместо постоянного ожидания тяжёлого запроса в обычном web request.

Для первого Query Report это не нужно.

Правильная последовательность:

```text
сначала сделать корректный запрос
→ проверить permissions
→ проверить индексы и объём данных
→ только потом решать проблему тяжёлого выполнения
```

`Prepared Report` не исправляет плохой SQL автоматически.

---

## 33. Query Report не должен менять бизнес-логику

Допустим, нужно:

> если сумма больше 100000 — автоматически назначить Manager и перевести Request в Review.

Это не Query Report.

SQL отчёта может **показать**, какие записи подходят:

```sql
SELECT name, amount
FROM `tabRequest`
WHERE amount > 100000
```

Но сам Report не должен превращаться в механизм изменения Documents.

Разделяй:

```text
прочитать / проанализировать данные
→ Report

изменить состояние системы
→ document logic / automation / App code
```

---

## 34. Где Query Report заканчивается

Query Report идеален, если задача решается примерно так:

```text
один SQL
→ строки
→ колонки
```

Но иногда нужно:

- несколько последовательных запросов;
- Python-расчёт;
- сложная логика permissions;
- данные из внешнего API;
- динамически менять колонки;
- вернуть `chart`;
- вернуть `report_summary`;
- построить tree-структуру;
- сделать сложную серверную обработку результата.

Тогда SQL начинает превращаться в монстра.

Следующий уровень:

```text
Script Report
```

---

## 35. Как выбрать между тремя типами

| Задача | Инструмент |
|---|---|
| выбрать поля, фильтры, сортировку | Report Builder |
| простая группировка Count/Sum/Average | Report Builder |
| точный JOIN нескольких таблиц | Query Report |
| CASE и SQL-вычисления | Query Report |
| нестандартная SQL-агрегация | Query Report |
| несколько этапов серверного расчёта | Script Report |
| Python нужен для результата | Script Report |
| внешний API участвует в отчёте | Script Report или отдельная интеграция |

Не переходи к Script Report просто потому, что он мощнее.

Сначала используй самый простой уровень, который действительно закрывает задачу.

---

## 36. Мини-практика

Сделаем отчёт:

```text
Open Requests by Department
```

### Шаг 1. Создай Report

Укажи:

```text
Report Type = Query Report
Ref DocType = Request
Is Standard = No
```

Для текущего v16 учти серверную проверку роли `Script Manager` для такого нестандартного Query Report.

### Шаг 2. Добавь Filters

Создай:

```text
status
Fieldtype = Select
Mandatory = ✓
```

и:

```text
department
Fieldtype = Link
Options = Department
```

### Шаг 3. Напиши SQL

Для простоты сделай Department обязательным тоже:

```sql
SELECT
    r.name AS request,
    r.department,
    r.priority,
    r.amount,
    r.owner
FROM `tabRequest` r
WHERE r.status = %(status)s
  AND r.department = %(department)s
ORDER BY r.creation DESC
```

### Шаг 4. Опиши Columns

Минимум:

```text
request
Label = Request
Fieldtype = Link
Options = Request


department
Label = Department
Fieldtype = Link
Options = Department

priority
Label = Priority
Fieldtype = Data

amount
Label = Amount
Fieldtype = Currency

owner
Label = Owner
Fieldtype = Link
Options = User
```

### Шаг 5. Проверь обычного пользователя

Не Administrator.

Проверь пользователя, которому через User Permission разрешён только один Department.

Сравни результат.

### Шаг 6. Проверь чувствительное поле

Если у `Request` есть:

```text
internal_cost
Perm Level = 1
```

не добавляй его в общий Query Report для Operators.

Отдельно убедись, что ты не рассчитываешь на автоматическое вырезание такого raw SQL-поля.

### Шаг 7. Проверь Export

Убери у тестового пользователя `Export` permission и посмотри разницу между:

```text
открыть Report
```

и:

```text
выгрузить Report
```

После этой практики должно быть понятно не только **как написать SQL**, но и почему Query Report требует более внимательного отношения к безопасности, чем Report Builder.

---

## Что запомнить

1. **Query Report = один read-only SQL-запрос + интерфейс Frappe Report.**
2. Не переходи на SQL, если Report Builder уже решает задачу.
3. `Ref DocType` — основной контекст permissions, а не ограничение SQL одной таблицей.
4. Фильтры передаются как параметры вида `%(fieldname)s`.
5. Для Link-колонок лучше явно задавать `Fieldtype = Link` и `Options`.
6. Query Report удобен для `JOIN`, `CASE`, вычисляемых колонок и произвольных SQL-агрегаций.
7. SQL выполняется напрямую через `frappe.db.sql()` после проверки read-only запроса.
8. **Raw SQL не равен `frappe.get_list()` по модели permissions.**
9. Frappe постфильтрует результат по известным связям, User Permissions, owner/share-механике там, где может это определить, но отчёт всё равно нужно проектировать безопасно.
10. **Не рассчитывай, что Permission Level автоматически вырежет чувствительную колонку из произвольного Query Report.**
11. `Roles` самого Report — дополнительный слой доступа.
12. Для запуска нужен `Report` permission на `Ref DocType`.
13. Для выгрузки отдельно проверяется `Export` permission.
14. В текущем v16 нестандартный Query Report при сохранении проходит явную проверку `Script Manager`, хотя официальная документация всё ещё описывает System Manager.
15. Standard Report — уже артефакт App: Administrator + Developer Mode + файлы приложения.
16. Если одного SQL уже недостаточно, следующий инструмент — **Script Report**.

---

## Источники

- [Frappe Framework — Query Report](https://docs.frappe.io/framework/user/en/desk/reports/query-report)
- [Frappe Framework — Script Report](https://docs.frappe.io/framework/user/en/desk/reports/script-report)
- [`Report` controller, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report/report.py)
- [`Report` metadata, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report/report.json)
- [`Query Report` runtime, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/query_report.py)
- [`Report Filter` metadata, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report_filter/report_filter.json)
- [`Report Column` metadata, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/report_column/report_column.json)
- [`check_safe_sql_query`, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/utils/safe_exec.py)

Дальше: **36. Script Report**.
