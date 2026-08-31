# 45. Server Script

В предыдущей главе мы разобрали `Client Script`:

```text
JavaScript
→ выполняется в браузере
→ меняет поведение Form / List
→ не является надёжным местом для server-side business rules
```

Теперь переходим на другую сторону Frappe — на сервер.

Главный вопрос этой главы:

```text
как выполнить небольшую Python-логику на сервере
не создавая полноценный App
```

Для этого во Frappe существует `Server Script`.

Проверено: **2026-08-31**.

---

# Часть I. Что такое Server Script простыми словами

## 1. Server Script — Python-код внутри Frappe

`Server Script` — отдельный DocType Framework, в котором можно сохранить небольшой Python-скрипт.

Frappe сам запускает этот код в нужный момент.

Например:

```text
Document сохраняется
        ↓
Before Save
        ↓
Server Script
        ↓
проверка данных
        ↓
Save продолжается или останавливается
```

---

## 2. Главное отличие от Client Script

`Client Script` работает здесь:

```text
Browser
```

`Server Script` работает здесь:

```text
Frappe server
```

Поэтому это два разных уровня системы.

---

## 3. Почему server-side логика важнее для правил данных

Допустим есть правило:

```text
если Status = Closed
→ Result обязательно заполнен
```

Если проверить его только Client Script:

```text
Desk Form
→ проверка сработает
```

Но Document может быть изменён не только через Desk:

```text
REST API
Data Import
другой Python-код
background job
интеграция
```

Эти пути не обязаны выполнять JavaScript браузера.

Server-side проверка находится ближе к данным и может применяться независимо от UI.

---

## 4. Аналогия

Client Script можно представить как правила на панели управления автомобиля:

```text
подсветить предупреждение
спрятать кнопку
показать подсказку
```

Server Script — как правило внутри блока управления:

```text
операцию действительно разрешить
или
операцию действительно запретить
```

---

# Часть II. Server Script в Frappe 16 по умолчанию отключён

## 5. Это сознательное ограничение безопасности

Начиная с Frappe 15 Server Scripts отключены по умолчанию.

Причина проста:

```text
Server Script
→ исполняемый код на сервере
→ существенно опаснее обычной настройки поля
```

Официальная документация прямо указывает, что на shared benches эта возможность отключена по соображениям безопасности.

---

## 6. Для Frappe 16 проверяется bench-level setting

В исходном коде `version-16` функция `is_safe_exec_enabled()` читает:

```text
server_script_enabled
```

из:

```text
common_site_config.json
```

То есть в текущей ветке v16 безопаснее ориентироваться именно на глобальную настройку Bench.

---

## 7. Команда для self-hosted Bench

Из каталога Bench:

```bash
bench set-config -g server_script_enabled 1
```

`-g` означает global config.

Результат появляется в:

```text
sites/common_site_config.json
```

примерно так:

```json
{
  "server_script_enabled": 1
}
```

---

## 8. Почему в документации можно встретить другой вариант

На странице Server Script всё ещё встречается пример site-level команды:

```bash
bench --site site1.local set-config server_script_enabled true
```

Но актуальный код ветки `version-16` проверяет именно `common_site_config.json`.

Поэтому для курса v16 считаем источником истины текущую реализацию Framework:

```bash
bench set-config -g server_script_enabled 1
```

---

## 9. После изменения production-конфигурации

Обычно выполняют:

```bash
bench restart
```

чтобы процессы Bench перечитали конфигурацию.

---

# Часть III. Кто может создавать Server Script

## 10. В v16 есть отдельная роль `Script Manager`

В JSON DocType `Server Script` штатные permissions назначены роли:

```text
Script Manager
```

---

## 11. Controller дополнительно проверяет эту роль

При `validate()` текущий v16 выполняет:

```python
frappe.only_for("Script Manager", True)
```

То есть это не просто подпись в UI.

Frappe реально проверяет роль при сохранении Server Script.

---

## 12. Почему это разумно

Человек с правом создавать Server Scripts может писать код, который:

```text
читает Documents
изменяет Documents
делает запросы к БД через разрешённый API
создаёт HTTP endpoint
вызывает внешние API
выполняется по расписанию
```

Поэтому `Script Manager` — административная и доверенная роль.

---

# Часть IV. Где создать Server Script

## 13. Через Awesome Bar

В Desk можно найти:

```text
Server Script
```

и создать новый Document.

---

## 14. Главное поле — `Script Type`

В актуальном Frappe 16 доступны **пять** типов:

```text
DocType Event
Scheduler Event
Permission Query
API
Workflow Task
```

Это важно: старая документация Server Script подробно описывает в основном Document Event и API, но сам DocType `version-16` уже содержит пять типов.

---

# Часть V. Карта пяти типов

## 15. `DocType Event`

Запустить код при событии Document.

```text
Save / Insert / Submit / Cancel / Delete / ...
→ Server Script
```

---

## 16. `Scheduler Event`

Запустить код автоматически по расписанию.

```text
каждый час
каждый день
cron
→ Server Script
```

---

## 17. `Permission Query`

Добавить дополнительное условие при построении запросов к конкретному DocType.

```text
List / get_list / query
→ дополнительное WHERE-условие
```

---

## 18. `API`

Создать собственный endpoint без Python-файла App.

```text
/api/method/my-method
→ Server Script
```

---

## 19. `Workflow Task`

Использовать Server Script как исполняемую задачу Workflow.

```text
Workflow transition
→ Workflow Task
→ Server Script
```

---

# Часть VI. Тип `DocType Event`

## 20. Это основной тип для server-side Document logic

Настройки выглядят примерно так:

```text
Script Type
    DocType Event

Reference Document Type
    Request

DocType Event
    Before Save
```

---

## 21. Что означает `Reference Document Type`

Это DocType, события которого должен слушать Script.

Например:

```text
Request
Task
Customer
My Custom DocType
```

---

## 22. Что означает `DocType Event`

Это конкретный момент lifecycle Document.

Например:

```text
Before Insert
Before Save
After Save
Before Submit
After Submit
Before Delete
```

---

# Часть VII. События DocType Event в v16

## 23. Список текущего v16

В DocType `Server Script` определены:

```text
Before Insert
Before Validate
Before Save
After Insert
After Save
Before Rename
After Rename
Before Submit
After Submit
Before Cancel
After Cancel
Before Discard
After Discard
Before Delete
After Delete
Before Save (Submitted Document)
After Save (Submitted Document)
Before Print
```

А также специальные payment events:

```text
On Payment Authorization
On Payment Paid
On Payment Failed
On Payment Charge Processed
On Payment Mandate Charge Processed
On Payment Mandate Acquisition Processed
```

---

## 24. Не нужно запоминать весь список сразу

Для первого прохода достаточно хорошо понимать:

```text
Before Insert
After Insert
Before Save
After Save
Before Submit
After Submit
Before Cancel
After Cancel
Before Delete
After Delete
```

Остальные понадобятся по мере реальных задач.

---

# Часть VIII. Insert и Save — не одно и то же

## 25. Insert

`Insert` — первое добавление нового Document в БД.

```text
New Request
→ Save
→ INSERT
```

---

## 26. Save существующего Document

```text
REQ-0001 уже существует
→ поменяли поле
→ Save
→ UPDATE
```

---

## 27. Поэтому `Before Insert` срабатывает только при первом создании

Если нужен код при каждом обычном сохранении, это другой event.

---

# Часть IX. Что такое `doc`

## 28. Для DocType Event Frappe передаёт текущий Document

В Server Script автоматически доступна переменная:

```python
doc
```

---

## 29. Например

Если Script относится к `Request`, можно читать:

```python
doc.name
doc.status
doc.owner
doc.creation
doc.modified
```

и любые обычные поля этого DocType:

```python
doc.priority
doc.due_date
doc.result
```

---

## 30. `doc` — тот Document, событие которого сейчас выполняется

Схема:

```text
REQ-0001 Save
      ↓
Before Save
      ↓
doc = REQ-0001
      ↓
Server Script
```

---

# Часть X. Первый DocType Event Server Script

## 31. Задача

Если Priority не заполнен:

```text
→ поставить Medium
```

---

## 32. Настройки

```text
Script Type:
DocType Event

Reference Document Type:
Request

DocType Event:
Before Save
```

---

## 33. Код

```python
if not doc.priority:
    doc.priority = "Medium"
```

---

## 34. Что происходит

```text
User нажал Save
       ↓
Before Save
       ↓
priority пустой?
       ↓ да
priority = Medium
       ↓
обычный Save продолжается
```

---

## 35. Дополнительный `doc.save()` здесь не нужен

Мы уже находимся внутри сохранения.

Изменение:

```python
doc.priority = "Medium"
```

попадёт в текущую операцию Save.

---

# Часть XI. Server-side validation

## 36. Типичная задача

```text
Closed
требует
Result
```

---

## 37. Script

```python
if doc.status == "Closed" and not doc.result:
    frappe.throw("Укажите результат перед закрытием")
```

---

## 38. `frappe.throw()` останавливает операцию

Упрощённо:

```text
Save
 ↓
Before Save
 ↓
условие нарушено
 ↓
frappe.throw()
 ↓
ошибка пользователю
 ↓
Save не завершается
```

---

## 39. Почему это сильнее Client Script

Эта логика выполняется на сервере при соответствующем lifecycle event.

То есть UI не является единственным местом проверки.

---

# Часть XII. `Before Validate` и `Before Save`

## 40. `Before Validate`

Срабатывает раньше основной `validate` стадии Document.

Подходит, когда нужно подготовить значения до стандартной validation chain.

---

## 41. `Before Save`

Внутри Framework event `validate` сопоставляется Server Script событию:

```text
Before Save
```

Это часто удобное место для:

```text
проверок
нормализации
вычисления значений
```

---

## 42. Не надо воспринимать названия как произвольные callback-и

Frappe имеет внутренний event map.

Например:

```text
validate
→ Before Save

on_update
→ After Save

on_submit
→ After Submit

on_trash
→ Before Delete
```

То есть Server Script подключается к реальному Document lifecycle Framework.

---

# Часть XIII. `Before Save` против `After Save`

## 43. `Before Save`

Хорош для изменения текущего Document:

```python
if not doc.closed_by and doc.status == "Closed":
    doc.closed_by = frappe.session.user
```

---

## 44. `After Save`

Подходит, когда действие логично выполнять уже после успешного сохранения текущего Document.

Например:

```text
создать связанный ToDo
создать журнал
инициировать внешнее действие
```

---

## 45. Опасность повторного Save

Не делай бездумно:

```python
doc.save()
```

в собственном `After Save`.

Можно получить цикл:

```text
Save
→ After Save
→ doc.save()
→ After Save
→ doc.save()
→ ...
```

---

# Часть XIV. Создание другого Document

## 46. Server Script может использовать Document API

Пример:

```python
todo = frappe.get_doc({
    "doctype": "ToDo",
    "description": "Проверить " + doc.name
})

todo.insert()
```

---

## 47. `frappe.get_doc({...})`

Создаёт объект Document из переданных данных.

---

## 48. `.insert()`

Добавляет этот Document в БД через обычный Document lifecycle Frappe.

---

## 49. Это лучше прямого SQL для обычных Documents

Потому что Document API сохраняет ожидаемую механику Framework:

```text
validation
lifecycle
metadata
permissions / flags в зависимости от вызова
hooks
```

---

# Часть XV. Получение существующего Document

## 50. Пример

```python
task = frappe.get_doc("Task", "TASK-0001")
```

После этого доступны поля:

```python
task.subject
task.status
task.owner
```

---

## 51. Script API v16 разрешает `frappe.get_doc`

Официальный Script API прямо указывает, что полученный Document можно сохранять и использовать его exposed methods в рамках safe scripting environment.

---

# Часть XVI. Работа с БД через Script API

## 52. Разрешены database helpers

Например:

```text
frappe.db.get_list
frappe.db.get_all
frappe.db.get_value
frappe.db.get_single_value
frappe.db.set_value
frappe.db.exists
frappe.db.escape
```

Также Script API документирует restricted `SELECT` через:

```text
frappe.db.sql
```

и Query Builder:

```text
frappe.qb
```

---

## 53. `frappe.db.get_value()`

Пример:

```python
full_name = frappe.db.get_value(
    "User",
    doc.owner,
    "full_name"
)
```

---

## 54. `frappe.db.exists()`

```python
if frappe.db.exists("Task", {"subject": doc.subject}):
    frappe.throw("Такая задача уже существует")
```

---

## 55. `frappe.db.set_value()`

```python
frappe.db.set_value(
    "Task",
    "TASK-0001",
    "status",
    "Closed"
)
```

Но это не универсальная замена Document API.

---

## 56. Для текущего `doc` обычно проще менять сам Document

В `Before Save`:

```python
doc.status = "Open"
```

обычно понятнее, чем делать отдельный DB write в ту же запись.

---

# Часть XVII. `get_list` против `get_all`

## 57. `frappe.db.get_list()`

Документация описывает его как запрос с учётом permissions текущего пользователя.

```python
rows = frappe.db.get_list(
    "Task",
    filters={"status": "Open"},
    fields=["name", "subject"]
)
```

---

## 58. `frappe.db.get_all()`

Получает записи без обычной permission-фильтрации списка.

В safe implementation `get_all` выставляет:

```text
ignore_permissions = True
```

---

## 59. Поэтому `get_all()` нельзя использовать автоматически

Если Script работает в пользовательском контексте и не должен раскрывать чужие данные:

```text
get_list
```

обычно безопаснее как исходная точка.

---

# Часть XVIII. Transactions

## 60. Frappe сам управляет транзакцией Document operation

Новичку не нужно после каждого изменения писать:

```python
frappe.db.commit()
```

---

## 61. Более того, для DocType Event commit и rollback запрещены

`execute_doc()` вызывает `safe_exec()` с:

```text
restrict_commit_rollback = True
```

И Frappe удаляет из доступного API:

```text
frappe.db.commit
frappe.db.rollback
frappe.db.add_index
```

---

## 62. Почему

Иначе Server Script мог бы разрушить атомарность обычного Document lifecycle.

Например:

```text
часть изменений commit
→ потом validation error
→ остальная операция rollback
```

и данные остались бы в полусохранённом состоянии.

---

## 63. В Scheduler Script ситуация другая

Script API допускает явные `commit` / `rollback` в server scripts, где это разрешено.

Но это уже продвинутая тема.

Для обычной Document логики правило простое:

```text
не управляй транзакцией вручную
```

---

# Часть XIX. Тип `Scheduler Event`

## 64. Scheduler Event запускается без действия пользователя

Пример:

```text
каждый день
→ найти просроченные записи
→ выполнить действие
```

---

## 65. Доступные частоты v16

```text
All
Hourly
Daily
Weekly
Monthly
Yearly
Hourly Long
Daily Long
Weekly Long
Monthly Long
Cron
```

---

## 66. Пример Daily Script

```python
count = frappe.db.count(
    "Task",
    {"status": "Open"}
)

frappe.log("Open tasks: " + str(count))
```

Настройка:

```text
Script Type:
Scheduler Event

Event Frequency:
Daily
```

---

## 67. Что Frappe делает при сохранении

Controller Server Script синхронизирует отдельный:

```text
Scheduled Job Type
```

для этого Scheduler Event.

---

## 68. Если Server Script отключить

Связанный Scheduled Job Type получает состояние stopped.

---

## 69. Если Server Script удалить

Frappe останавливает связанные Scheduled Job Type и отвязывает их от Server Script.

---

# Часть XX. Что означает `Long`

## 70. Есть обычные и Long frequencies

Например:

```text
Hourly
Hourly Long
```

```text
Daily
Daily Long
```

---

## 71. Long предназначен для более длительных background tasks

Это связано с очередями Frappe.

Подробно background jobs и queues будут разобраны в главе 53.

Пока достаточно понимать:

```text
короткая периодическая операция
→ обычная frequency

более долгая операция
→ Long
```

---

## 72. Но Server Script не должен превращаться в огромный ETL

Если код становится:

```text
длинным
сложно тестируемым
с несколькими этапами
с retry policy
с десятками функций
```

это уже хороший кандидат на App code.

---

# Часть XXI. Cron

## 73. Если стандартной frequency недостаточно

Выбирается:

```text
Event Frequency = Cron
```

После этого появляется поле:

```text
Cron Format
```

---

## 74. Формат

```text
* * * * *
│ │ │ │ │
│ │ │ │ └─ day of week
│ │ │ └─── month
│ │ └───── day of month
│ └─────── hour
└───────── minute
```

---

## 75. Пример

```text
0 8 * * *
```

означает запуск по расписанию каждый день в 08:00.

---

## 76. Cron в Server Script — не отдельный Linux cron

Frappe создаёт Scheduled Job Type и дальше использует свою scheduler/background-job инфраструктуру.

---

# Часть XXII. Тип `API`

## 77. API Server Script создаёт endpoint из Desk

Настройки:

```text
Script Type:
API

API Method:
hello
```

После сохранения endpoint доступен как:

```text
/api/method/hello
```

---

## 78. Самый простой ответ

```python
frappe.response["message"] = "Hello"
```

Ответ Frappe будет содержать:

```json
{
  "message": "Hello"
}
```

---

## 79. API Method — это имя маршрута

Например:

```text
API Method = task-summary
```

даёт:

```text
/api/method/task-summary
```

---

# Часть XXIII. Параметры API

## 80. Request arguments доступны через `frappe.form_dict`

Запрос:

```text
/api/method/hello?name=Alex
```

Script:

```python
name = frappe.form_dict.get("name")
frappe.response["message"] = "Hello " + name
```

---

## 81. Можно вернуть структуру

```python
task_name = frappe.form_dict.get("name")

task = frappe.get_doc("Task", task_name)

frappe.response["message"] = {
    "name": task.name,
    "subject": task.subject,
    "status": task.status
}
```

---

# Часть XXIV. Authentication API Server Script

## 82. По умолчанию Guest не разрешён

Если endpoint вызывает:

```text
Guest
```

а:

```text
Allow Guest = 0
```

Frappe поднимает PermissionError.

---

## 83. `Allow Guest`

Если включить:

```text
Allow Guest = 1
```

endpoint сможет выполняться без authenticated session.

---

## 84. Это security decision

Нельзя ставить `Allow Guest` просто потому, что:

```text
"так заработало"
```

Нужно заранее понимать:

```text
какие данные принимает endpoint
что он возвращает
что он изменяет
какие злоупотребления возможны
```

---

# Часть XXV. Rate Limiting API Server Script

## 85. В v16 есть встроенные поля

```text
Enable Rate Limit
Request Limit
Time Window (Seconds)
```

---

## 86. Пример

```text
Request Limit = 10
Time Window = 60
```

задаёт лимит вызовов в указанном временном окне.

---

## 87. Для API Server Script используется штатный Frappe rate limiter

Controller оборачивает выполнение endpoint в `rate_limit()`.

Это особенно полезно для public / guest endpoint.

---

# Часть XXVI. Вызов API из Client Script

## 88. Client Script может вызвать API Server Script

Например:

```javascript
let r = await frappe.call({
    method: 'task-summary',
    args: {
        name: frm.doc.name
    }
});

console.log(r.message);
```

---

## 89. Получаем цепочку

```text
Client Script
      ↓
frappe.call()
      ↓
/api/method/task-summary
      ↓
API Server Script
      ↓
Python server-side
      ↓
response
      ↓
Browser
```

---

## 90. Это полезно для небольших site-specific actions

Но большой API layer лучше держать в App с normal Python modules, tests и version control.

---

# Часть XXVII. Тип `Permission Query`

## 91. Назначение

`Permission Query` добавляет программное условие к database query конкретного DocType.

Пример идеи:

```text
пользователь видит только записи своего подразделения
```

---

## 92. Настройки

```text
Script Type:
Permission Query

Reference Document Type:
Task
```

---

## 93. В Script доступны специальные locals

```text
user
conditions
active_child_tables
```

---

## 94. `user`

Это пользователь, для которого строится permission query.

---

## 95. `conditions`

Server Script должен сформировать дополнительное SQL condition.

Пример:

```python
conditions = "`tabTask`.`owner` = " + frappe.db.escape(user)
```

---

## 96. Почему нужен `frappe.db.escape()`

Нельзя склеивать непроверенные значения в SQL руками.

`frappe.db.escape()` экранирует значение для database expression.

---

## 97. `active_child_tables`

v16 также передаёт список child tables, которые участвуют в текущем SQL query.

Для новичка это продвинутая возможность; пока достаточно знать, что она существует для сложных permission-query scenarios.

---

# Часть XXVIII. Permission Query не заменяет всю permission model

## 98. Сначала существуют обычные инструменты

```text
Role Permission Manager
Permission Level
User Permission
Owner
Sharing
```

Они уже подробно разобраны в блоке D.

---

## 99. Permission Query нужен, когда стандартной модели недостаточно

То есть правильный порядок:

```text
стандартные permissions
      ↓ не хватает
Permission Query
```

а не наоборот.

---

## 100. Это query-level механизм

Он влияет на условия запросов.

Не нужно автоматически считать его единственной проверкой любой произвольной business operation.

Server methods всё равно должны корректно проверять доступ там, где это требуется.

---

## 101. В текущем v16 map хранит один Permission Query script на DocType

В `server_script_utils.py` значение записывается как:

```text
permission_query[reference_doctype] = script.name
```

То есть не надо проектировать несколько независимых Permission Query Server Scripts для одного и того же DocType и рассчитывать, что Frappe объединит их как список.

---

# Часть XXIX. Тип `Workflow Task`

## 102. Это v16 Server Script type для Workflow task execution

Controller имеет отдельный метод:

```text
execute_workflow_task(doc)
```

который запускает Script и передаёт:

```python
doc
```

---

## 103. Упрощённая схема

```text
Workflow transition
       ↓
Workflow Task
       ↓
Server Script
       ↓
server-side action
```

---

## 104. Пока не нужно строить вокруг этого всю картину

Workflow мы уже знаем как state-transition mechanism.

`Workflow Task` — дополнительный способ привязать исполняемое действие к transition.

Детали конкретной настройки Workflow Transition Tasks имеет смысл изучать тогда, когда такая автоматизация действительно нужна.

---

# Часть XXX. RestrictedPython и `safe_exec`

## 105. Server Script — не обычный `.py` файл

Это критически важно.

Frappe не делает просто:

```python
exec(user_code)
```

в полном Python environment.

---

## 106. Используется RestrictedPython

Frappe компилирует Script через:

```text
RestrictedPython.compile_restricted
```

со своей policy:

```text
FrappeTransformer
```

---

## 107. Затем код выполняется через `safe_exec`

Упрощённо:

```text
Server Script text
      ↓
RestrictedPython compiler
      ↓
safe globals
      ↓
execution
```

---

## 108. Поэтому Server Script — restricted Python

Не надо ожидать, что здесь свободно работают любые:

```text
imports
filesystem operations
OS commands
arbitrary Python packages
private internals Framework
```

---

# Часть XXXI. Что доступно в Script API

## 109. Frappe предоставляет разрешённый набор функций

Например:

```text
frappe.get_doc
frappe.new_doc
frappe.get_last_doc
frappe.get_cached_doc
frappe.get_meta

frappe.db.get_list
frappe.db.get_all
frappe.db.get_value
frappe.db.set_value
frappe.db.exists
frappe.db.escape

frappe.qb

frappe.msgprint
frappe.log_error
frappe.render_template

frappe.make_get_request
frappe.make_post_request
frappe.make_put_request

frappe.sendmail

frappe.utils
```

Точный whitelist может меняться, поэтому для конкретной функции нужно смотреть `Script API` и `safe_exec.py` своей версии.

---

## 110. Доступен `json`

Script API отдельно документирует стандартный модуль:

```python
json
```

в safe scripting environment.

---

## 111. Не нужно заучивать whitelist

Правильная привычка:

```text
хочу использовать функцию X
→ смотрю Script API v16
→ если её нет, не предполагаю, что arbitrary Python import спасёт
```

---

# Часть XXXII. Внешние HTTP API

## 112. Safe Script API разрешает HTTP helpers

Например:

```python
result = frappe.make_get_request(
    "https://example.com/api"
)
```

---

## 113. POST

```python
result = frappe.make_post_request(
    "https://example.com/api",
    data={
        "name": doc.name
    }
)
```

---

## 114. Это позволяет сделать небольшую интеграцию без App

Например:

```text
Document event
→ Server Script
→ external HTTP API
```

---

## 115. Но внешняя интеграция быстро становится сложной

Как только появляются:

```text
authentication refresh
retry
backoff
idempotency
mapping
large payloads
queueing
monitoring
unit tests
```

App code становится значительно удобнее.

---

# Часть XXXIII. Секреты в Server Script

## 116. Server-side лучше Client-side, но hardcode всё равно плохая идея

Не надо писать:

```python
API_KEY = "real-secret-key"
```

прямо в Server Script.

---

## 117. Почему

Server Script — Document в БД.

Люди с административным доступом к Script смогут увидеть код.

Кроме того, секрет сложнее:

```text
менять
ротировать
переносить между environments
аудировать
```

---

## 118. Для секретов нужен нормальный server-side configuration mechanism

Например отдельный Settings DocType с Password field или другой подходящий механизм конфигурации приложения.

Точная схема зависит от интеграции.

---

# Часть XXXIV. Internal Server Script library

## 119. Один Server Script можно вызвать из другого

Script API предоставляет:

```python
run_script()
```

---

## 120. Возврат через `frappe.flags`

Script A:

```python
frappe.flags.result = "Hello"
```

Script B:

```python
result = run_script("Script A").get("result")
```

---

## 121. Это штатная возможность

Она документирована как использование Server Scripts в качестве internal libraries.

---

## 122. Но не строй из этого второй package system

Если получается:

```text
Script A
→ Script B
→ Script C
→ Script D
→ shared helper logic
→ десятки зависимостей
```

обычный App уже намного понятнее.

---

# Часть XXXV. `Disabled`

## 123. Server Script можно временно выключить

Поле:

```text
Disabled
```

есть в DocType v16.

---

## 124. Это полезно для диагностики

```text
подозреваем Server Script
→ Disabled = 1
→ повторяем операцию
→ сравниваем результат
```

---

## 125. Для Scheduler Event disabled также останавливает scheduled job

Controller синхронизирует это состояние со связанным `Scheduled Job Type`.

---

# Часть XXXVI. Track Changes и версии

## 126. Server Script имеет `track_changes = 1`

Поэтому изменения Script отслеживаются через Version mechanism Framework.

---

## 127. Документация также описывает `Compare Versions`

Это позволяет сравнивать изменения кода между версиями Server Script.

---

## 128. Это полезно, но не равно полноценному Git workflow

Version в БД помогает увидеть изменения на Site.

Git даёт другое:

```text
branch
review
commit history
release
merge
CI/tests
```

Именно поэтому большая стабильная логика лучше чувствует себя в App.

---

# Часть XXXVII. Несколько DocType Event Server Scripts

## 129. Для одного DocType + event может существовать несколько Scripts

Текущий v16 строит map примерно так:

```text
Request
  Before Save
    Script A
    Script B
```

и выполняет все найденные scripts.

---

## 130. Но не стоит зависеть от скрытого порядка

Если правильность системы требует:

```text
Script A строго раньше B
B строго раньше C
```

и это критическая business chain, код уже становится трудно сопровождать.

---

## 131. Лучше держать одну логическую ответственность вместе

Например одна маленькая validation может быть отдельным Script.

Но десять Scripts, которые взаимно меняют одно и то же поле, быстро превращаются в неочевидную систему.

---

# Часть XXXVIII. Server Script во время install / migrate

## 132. DocType Event Server Scripts не запускаются во всех внутренних режимах Framework

`run_server_script_for_doc_event()` пропускает выполнение, если Frappe находится в:

```text
install
migrate
```

---

## 133. Почему это важно

Server Script не надо воспринимать как гарантированный hook на абсолютно любое техническое изменение Document во всех режимах Framework.

Для installation/migration logic существуют App mechanisms.

---

# Часть XXXIX. Ошибки Script при сохранении

## 134. Frappe проверяет restricted compilation

При `validate()` Server Script компилируется через RestrictedPython.

Если обнаружена compile error, Frappe показывает:

```text
Compilation warning
```

---

## 135. Это помогает поймать синтаксические проблемы заранее

Но compile success не означает, что логика правильная.

Например:

```python
x = 10 / 0
```

синтаксически валиден, но упадёт во время выполнения.

---

# Часть XL. Runtime errors и диагностика

## 136. Server Script выполняется на сервере

Поэтому browser console — уже не главное место диагностики.

Смотреть нужно:

```text
server traceback
Error Log
bench logs
worker / scheduler logs
HTTP response
```

в зависимости от типа Script.

---

## 137. `frappe.log_error()`

Script API разрешает:

```python
frappe.log_error(
    title="My Script",
    message="Something happened"
)
```

для записи Error Log.

---

## 138. `print()` в safe_exec

Frappe использует собственный `PrintCollector` и отправляет собранный вывод в logging mechanism.

Для временной диагностики это возможно, но production logging лучше делать осмысленно.

---

# Часть XLI. Server Script и permissions

## 139. Server-side не означает автоматически secure

Можно написать плохой Server Script, который сам выдаёт данные без нужной проверки.

Например API Script с:

```python
frappe.db.get_all("Secret DocType")
```

может сознательно обойти list permissions.

---

## 140. Поэтому автор Script отвечает за security semantics

Нужно понимать:

```text
кто запускает Script
что разрешено этому user
какие Documents читаются
какие Documents изменяются
какие данные возвращаются
```

---

## 141. Особенно внимательно с API + Allow Guest

Это уже публичная server attack surface.

Минимально нужно продумать:

```text
input validation
authorization
rate limit
данные ответа
side effects
```

---

# Часть XLII. Server Script против обычных permissions

## 142. Не нужно кодировать в Python то, что уже умеет Framework

Если задача:

```text
роль может Read
роль не может Write
поле скрыто через Permission Level
User Permission ограничивает Company
```

сначала используются штатные permissions.

---

## 143. Server Script нужен для дополнительной логики

Например:

```text
при конкретном business state
→ провести дополнительную server-side проверку
```

---

# Часть XLIII. Server Script против Notification

## 144. Если задача просто отправить уведомление по штатному событию

Сначала посмотри:

```text
Notification
```

Не обязательно писать:

```python
frappe.sendmail(...)
```

в Server Script.

---

## 145. Server Script оправдан, когда logic действительно сложнее штатной Notification

Например перед отправкой нужно:

```text
собрать нестандартные данные
обратиться к внешнему API
создать дополнительные Documents
```

---

# Часть XLIV. Server Script против Assignment Rule

## 146. Автоматическое назначение по стандартным правилам

Сначала:

```text
Assignment Rule
```

---

## 147. Не нужно вручную создавать ToDo на каждое сохранение, если задача уже решается Assignment Rule

Server Script — не замена всем low-code механизмам Framework.

---

# Часть XLV. Server Script против Workflow

## 148. Переходы состояния лучше сначала описывать Workflow

Если задача:

```text
Draft → Review → Approved
```

и нужны роли/transition rules, для этого есть `Workflow`.

---

## 149. Server Script может дополнять Workflow

Например:

```text
transition
→ выполнить дополнительное server-side действие
```

Но не нужно вручную строить целую state machine в одном Python Script, если Workflow уже решает задачу.

---

# Часть XLVI. Server Script против Auto Repeat и Scheduler

## 150. Повторное создание Documents

Если задача именно:

```text
каждый месяц создать копию документа
```

сначала посмотри `Auto Repeat`.

---

## 151. Общая периодическая Python logic

Если задача:

```text
каждый час проверить набор данных
→ выполнить custom logic
```

тогда Scheduler Event Server Script уже подходит лучше.

---

# Часть XLVII. Server Script против Webhook

## 152. Если нужно просто отправить Document data во внешний HTTP endpoint

Сначала проверь штатный:

```text
Webhook
```

---

## 153. Server Script нужен, если интеграция требует дополнительной программной логики

Например:

```text
сформировать нестандартный payload
сделать несколько запросов
прочитать дополнительные Documents
обработать response
```

Но при росте сложности опять появляется граница App.

---

# Часть XLVIII. Server Script против Client Script

## 154. Client Script

```text
Browser
JavaScript
Form / List UI
```

---

## 155. Server Script

```text
Server
restricted Python
Document / Scheduler / API / Permission Query / Workflow Task
```

---

## 156. Типичная хорошая пара

Client Script:

```text
сразу показывает пользователю, что Due Date обязательна
```

Server Script:

```text
реально запрещает Save без Due Date
```

---

# Часть XLIX. Server Script против controller в App

## 157. Controller — обычный Python code приложения

Например:

```text
my_app/
  module/
    doctype/
      request/
        request.py
```

---

## 158. Controller не ограничен ролью Server Script sandbox

Он является частью установленного App и может использовать нормальную структуру Python проекта.

---

## 159. В controller удобно держать authoritative reusable logic

Особенно если нужны:

```text
methods
classes
imports
shared modules
tests
Git
code review
migrations
```

---

## 160. Server Script удобнее для маленькой site-specific логики

Например:

```python
if doc.priority == "High" and not doc.due_date:
    frappe.throw("Укажите Due Date")
```

Создавать ради одной такой проверки большую структуру App не всегда обязательно.

---

# Часть L. Когда Server Script пора переносить в App

## 161. Сигнал 1 — Script стал длинным

Если один Script уже занимает сотни строк, читать и тестировать его неудобно.

---

## 162. Сигнал 2 — нужны helper modules

```text
validation.py
integration.py
services.py
utils.py
```

Server Script не предназначен для нормальной package architecture.

---

## 163. Сигнал 3 — нужны automated tests

Большая production logic без тестов становится рискованной.

---

## 164. Сигнал 4 — feature должна переноситься между Sites

Если нужно воспроизводимо установить одну реализацию на:

```text
dev
test
prod
другой Bench
```

App + Git естественнее.

---

## 165. Сигнал 5 — сложная интеграция

```text
OAuth
retry
idempotency
queues
webhook verification
large mapping
monitoring
```

лучше обслуживается как App code.

---

## 166. Сигнал 6 — несколько Server Scripts стали зависеть друг от друга

Когда никто уже не понимает:

```text
что запускается первым
кто изменил поле
почему произошёл side effect
```

low-code решение переросло свою удобную границу.

---

# Часть LI. Частая ошибка: всё делать через `frappe.db.set_value`

## 167. Пример

```python
frappe.db.set_value(
    doc.doctype,
    doc.name,
    "status",
    "Closed"
)
```

внутри `Before Save` текущего документа.

---

## 168. Почему это часто лишнее

Текущий Document уже находится в lifecycle.

Проще:

```python
doc.status = "Closed"
```

---

## 169. Database API нужен, когда действительно требуется отдельная DB operation

Не превращай его в единственный стиль изменения Documents.

---

# Часть LII. Частая ошибка: дублирование штатной validation

## 170. Если поле всегда mandatory

Не нужен Server Script:

```python
if not doc.title:
    frappe.throw(...)
```

если можно просто поставить:

```text
Reqd = 1
```

в DocField metadata.

---

## 171. Server Script нужен для условной или нестандартной проверки

Например:

```text
Result mandatory только при Status = Closed
```

если это правило нельзя корректно выразить штатной metadata.

---

# Часть LIII. Частая ошибка: внешний API прямо в Before Save

## 172. Представим

```text
Before Save
→ внешний API
→ API отвечает 8 секунд
```

Пользователь ждёт весь этот запрос во время Save.

---

## 173. А если внешний сервис недоступен

Обычная операция Save может начать падать или зависеть от чужой системы.

---

## 174. Поэтому нужно понимать синхронность

Если внешний вызов не обязан завершиться до Save:

```text
background job
Webhook
очередь
```

может быть правильнее.

Подробно фоновые задачи разберём позже.

---

# Часть LIV. Частая ошибка: `Allow Guest` для удобства

## 175. Плохая логика

```text
получаю PermissionError
→ включаю Allow Guest
```

---

## 176. Правильный вопрос

```text
должен ли неизвестный пользователь Интернета
вообще иметь право вызвать этот endpoint?
```

Если ответ нет — проблема решается authentication/authorization, а не Guest access.

---

# Часть LV. Частая ошибка: Permission Query вместо User Permission

## 177. Если задача стандартная

```text
пользователь видит только Company A
```

и связь строится обычными Link fields, сначала проверяется:

```text
User Permission
```

---

## 178. Permission Query — более низкий и сложный уровень

Он нужен только когда стандартной модели реально недостаточно.

---

# Часть LVI. Частая ошибка: считать sandbox полной защитой от плохого Script

## 179. RestrictedPython снижает поверхность доступа

Но Script всё равно может делать серьёзные вещи через разрешённый Frappe API.

Например:

```text
создавать Documents
изменять данные
читать данные
отправлять HTTP requests
```

---

## 180. Поэтому Script Manager остаётся доверенной ролью

Sandbox — не основание раздавать право писать Server Scripts обычным пользователям.

---

# Часть LVII. Мини-практика 1 — server validation

## 181. Задача

Для учебного `Request`:

```text
если Priority = High
→ Due Date обязательно
```

---

## 182. Настройки

```text
Script Type:
DocType Event

Reference Document Type:
Request

DocType Event:
Before Save
```

---

## 183. Script

```python
if doc.priority == "High" and not doc.due_date:
    frappe.throw("Для High Priority укажите Due Date")
```

---

## 184. Проверка

Попробуй сохранить:

```text
Priority = High
Due Date = пусто
```

Ожидаемый результат:

```text
Save запрещён
```

---

## 185. Затем заполни Due Date

Ожидаемый результат:

```text
Save проходит
```

---

# Часть LVIII. Мини-практика 2 — автоматическое поле

## 186. Задача

При переходе в Closed автоматически записать пользователя.

Пусть есть поле:

```text
closed_by
```

---

## 187. Script

```python
if doc.status == "Closed" and not doc.closed_by:
    doc.closed_by = frappe.session.user
```

---

## 188. Почему `Before Save`

Поле меняется внутри текущего Document до записи в БД.

Дополнительный Save не нужен.

---

# Часть LIX. Мини-практика 3 — создание ToDo

## 189. Задача

После первого создания Request автоматически создать ToDo.

---

## 190. Event

Лучше выбрать:

```text
After Insert
```

а не `After Save`, если ToDo нужен ровно один раз после первого создания.

---

## 191. Script

```python
todo = frappe.get_doc({
    "doctype": "ToDo",
    "description": "Проверить Request " + doc.name
})

todo.insert()
```

---

## 192. Почему это лучше `After Save` для этой задачи

`After Save` сработает и при следующих изменениях Request.

Тогда без дополнительной проверки можно создавать новый ToDo на каждый Save.

---

# Часть LX. Мини-практика 4 — API endpoint

## 193. Создай Script

```text
Script Type:
API

API Method:
hello-server-script
```

---

## 194. Script

```python
name = frappe.form_dict.get("name") or "World"

frappe.response["message"] = {
    "hello": name,
    "user": frappe.session.user
}
```

---

## 195. Вызов authenticated user

```text
/api/method/hello-server-script?name=Alex
```

Ожидаемый `message`:

```json
{
  "hello": "Alex",
  "user": "user@example.com"
}
```

---

# Часть LXI. Мини-практика 5 — Scheduler Event

## 196. Задача

Раз в день записывать количество открытых Task в log.

---

## 197. Настройки

```text
Script Type:
Scheduler Event

Event Frequency:
Daily
```

---

## 198. Script

```python
count = frappe.db.count(
    "Task",
    {"status": "Open"}
)

frappe.log("Open tasks: " + str(count))
```

---

## 199. Что проверить

```text
Server Script не Disabled
scheduler Bench работает
workers работают
Scheduled Job Type создан
```

Диагностика Scheduler будет подробно разобрана позже.

---

# Часть LXII. Мини-практика 6 — Permission Query только как демонстрация

## 200. Задача

Для учебного DocType показать в query только Documents, где:

```text
owner = current user
```

---

## 201. Script

```python
conditions = "`tabRequest`.`owner` = " + frappe.db.escape(user)
```

---

## 202. Важно

Это учебный пример механики.

Для реальной системы сначала надо проверить, нельзя ли решить задачу обычными:

```text
Role Permission
If Owner
User Permission
```

---

# Часть LXIII. Как выбирать событие

## 203. Нужно установить значение до сохранения

```text
Before Save
```

---

## 204. Нужно проверить данные перед сохранением

Обычно:

```text
Before Save
```

или более ранний event, если это действительно требуется lifecycle.

---

## 205. Нужно действие один раз после первого создания

```text
After Insert
```

---

## 206. Нужно действие после каждого Save

```text
After Save
```

но нужно продумать idempotency и рекурсию.

---

## 207. Нужно до Submit

```text
Before Submit
```

---

## 208. Нужно после Submit

```text
After Submit
```

---

## 209. Нужно до удаления

```text
Before Delete
```

---

## 210. Нужно после удаления

```text
After Delete
```

---

# Часть LXIV. Decision table

## 211. Какой Server Script type выбрать

| Задача | Тип |
|---|---|
| Проверить Document при Save | `DocType Event` |
| Автозаполнить поле server-side | `DocType Event` |
| Создать связанный Document | `DocType Event` |
| Реагировать на Submit / Cancel / Delete | `DocType Event` |
| Запускать Python по расписанию | `Scheduler Event` |
| Нужен нестандартный cron | `Scheduler Event` + `Cron` |
| Создать маленький endpoint | `API` |
| Разрешить public endpoint | `API` + осознанный `Allow Guest` |
| Ограничить частоту endpoint | `API` + Rate Limit |
| Добавить нестандартное query permission condition | `Permission Query` |
| Выполнить Script как Workflow task | `Workflow Task` |

---

# Часть LXV. Что лучше решить без Server Script

## 212. Static mandatory

```text
DocField Reqd
```

---

## 213. Static read-only / hidden

```text
DocField / Customize Form
```

---

## 214. Простая подстановка из Link

```text
Fetch From
```

---

## 215. UI reaction

```text
Client Script
```

---

## 216. Ролевой доступ

```text
Role Permission Manager
Permission Level
User Permission
Sharing
```

---

## 217. Стандартное уведомление

```text
Notification
```

---

## 218. Стандартное назначение

```text
Assignment Rule
```

---

## 219. Повторное создание Document

```text
Auto Repeat
```

---

## 220. Простой исходящий HTTP event

```text
Webhook
```

если его возможностей достаточно.

---

# Часть LXVI. Архитектурная лестница

## 221. Хороший порядок выбора

```text
можно решить metadata?
→ DocType / Customize Form

есть готовый штатный механизм?
→ Workflow / Notification / Assignment Rule / Auto Repeat / Webhook / ...

нужен только UI behavior?
→ Client Script

нужна маленькая site-specific server logic?
→ Server Script

нужна большая переносимая и тестируемая feature?
→ App code
```

---

# Часть LXVII. Что Server Script не является

## 222. Не является полноценным Python module

```text
нет обычной package architecture
restricted environment
```

---

## 223. Не является заменой App

Он закрывает небольшой слой in-app scripting.

---

## 224. Не является permission system сам по себе

Даже server-side code нужно писать с учётом security model.

---

## 225. Не является background-job framework

Scheduler Event может запускать код по расписанию, но очереди и background jobs — отдельная инфраструктура.

---

## 226. Не является способом обойти Framework

Если есть нормальный DocType API, Workflow, permissions или другой штатный механизм, обычно лучше использовать их, а не низкоуровневые обходы.

---

# Что нужно запомнить

1. `Server Script` — restricted Python-код, который выполняется на сервере Frappe.
2. Server Script не является Client Script: Client Script работает в Browser, Server Script — на сервере.
3. Начиная с v15 Server Scripts по умолчанию отключены.
4. В актуальном коде v16 включение проверяется через `server_script_enabled` в `common_site_config.json`.
5. Для self-hosted Bench используется `bench set-config -g server_script_enabled 1`.
6. Управление Server Script в v16 защищено ролью `Script Manager`.
7. В v16 существует пять Script Type: `DocType Event`, `Scheduler Event`, `Permission Query`, `API`, `Workflow Task`.
8. `DocType Event` выполняется на событиях Document lifecycle.
9. В DocType Event текущий Document доступен как `doc`.
10. `Before Insert` относится к первому созданию Document.
11. `Before Save` подходит для многих server-side validations и изменений текущего Document.
12. `After Insert` полезен для действия, которое должно выполниться один раз после первого создания.
13. `After Save` может выполняться при каждом сохранении, поэтому нужно думать о дублировании и рекурсии.
14. Не нужно вызывать `doc.save()` внутри собственного `After Save` без ясного понимания lifecycle.
15. `frappe.throw()` позволяет остановить operation с server-side validation error.
16. Server Script получает безопасный subset Document API и Database API.
17. `frappe.db.get_list()` учитывает permissions текущего пользователя.
18. `frappe.db.get_all()` работает с `ignore_permissions=True`, поэтому применять его нужно осознанно.
19. Для DocType Event Frappe запрещает явные `commit`, `rollback` и `add_index` в safe context.
20. `Scheduler Event` создаёт/синхронизирует `Scheduled Job Type`.
21. Scheduler frequencies v16 включают обычные, `Long` и `Cron` варианты.
22. API Server Script создаёт endpoint `/api/method/<API Method>`.
23. Request arguments доступны через `frappe.form_dict`.
24. Ответ можно формировать через `frappe.response`.
25. `Allow Guest` открывает API для Guest и является security decision.
26. API Server Script имеет встроенный rate limiting.
27. `Permission Query` добавляет дополнительное query condition и не должен без необходимости заменять обычные permissions.
28. В текущем v16 Server Script map хранит один Permission Query script на Reference DocType.
29. `Workflow Task` запускает Server Script с текущим `doc` как часть Workflow task mechanism.
30. Server Script выполняется через `RestrictedPython` и `safe_exec`.
31. Arbitrary Python и arbitrary imports здесь не гарантированы и намеренно ограничены.
32. Разрешённые функции нужно проверять по Script API своей версии.
33. Script API разрешает Document API, database helpers, Query Builder, HTTP helpers, email и utilities в ограниченном наборе.
34. Один Server Script можно вызвать из другого через `run_script()` и вернуть значения через `frappe.flags`.
35. Server Script поддерживает Track Changes / Version и сравнение версий.
36. `Disabled` позволяет отключить Script без удаления.
37. DocType Event Server Scripts не выполняются во время некоторых внутренних install/migrate режимов.
38. RestrictedPython снижает риск, но не делает любой Server Script автоматически безопасным.
39. `Script Manager` должен оставаться доверенной ролью.
40. Маленькая site-specific server logic — хороший кандидат для Server Script.
41. Большая reusable business logic, сложная интеграция, tests и Git workflow — сигнал переходить в App.

---

# Мини-проверка себя

После этой главы ты должен уметь ответить:

1. Чем Server Script принципиально отличается от Client Script?
2. Почему Server Scripts отключены по умолчанию?
3. Где v16 проверяет `server_script_enabled`?
4. Какая роль управляет Server Script в актуальном v16?
5. Какие пять Script Type существуют?
6. Что такое `doc`?
7. Чем `Before Insert` отличается от `Before Save`?
8. Для чего нужен `After Insert`?
9. Почему `doc.save()` в `After Save` может быть опасен?
10. Как остановить сохранение из server validation?
11. Чем `get_list` отличается от `get_all`?
12. Почему `commit()` недоступен в DocType Event?
13. Как Scheduler Event связан с Scheduled Job Type?
14. Что такое `Cron` frequency?
15. Какой URL получает API Server Script?
16. Для чего нужен `Allow Guest`?
17. Что делает rate limit?
18. Что такое Permission Query?
19. Почему Permission Query не надо использовать вместо обычных permissions без необходимости?
20. Что такое RestrictedPython?
21. Почему Server Script не равен обычному Python module?
22. Когда Server Script уже пора переносить в App?

Если эти ответы понятны, фундамент Server Script усвоен.

---

# Источники

Основные источники именно для Frappe Framework 16:

- [Server Script — Frappe Framework documentation](https://docs.frappe.io/framework/user/en/desk/scripting/server-script)
- [Script API — Frappe Framework documentation](https://docs.frappe.io/framework/user/en/desk/scripting/script-api)
- [`Server Script` DocType — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/server_script/server_script.json)
- [`server_script.py` — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/server_script/server_script.py)
- [`server_script_utils.py` — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/server_script/server_script_utils.py)
- [`safe_exec.py` — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/utils/safe_exec.py)

Для спорных мест этой главы приоритет отдан исходному коду `version-16`, потому что страница Server Script документации местами всё ещё описывает более старую форму интерфейса и не перечисляет все пять Script Type текущего v16.

---

# Следующая глава

**46. Standard vs Custom** — разберём одну из самых важных границ Frappe: что такое standard metadata и code из App, что такое custom records конкретного Site, где физически хранится каждое изменение и что из этого автоматически переносится между окружениями.
