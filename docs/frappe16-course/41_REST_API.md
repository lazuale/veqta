# 41. REST API

В предыдущих главах мы разобрали внешние интерфейсы для человека:

```text
Web Form
Website
Portal
```

Теперь переходим к интерфейсу для программ.

Главный вопрос этой главы:

```text
как внешняя программа
может читать и изменять Frappe Documents
по HTTP
```

Для этого Frappe автоматически предоставляет HTTP API для DocTypes.

Проверено: **2026-08-31**.

---

# Часть I. Что такое REST API простыми словами

## 1. Обычный пользователь работает через Form

В Desk человек делает:

```text
Request
→ открыть
→ изменить Priority
→ Save
```

Browser вызывает внутренние механизмы Frappe, а Framework сохраняет Document.

---

## 2. Внешняя программа не обязана открывать Desk

Например есть:

```text
Python script
mobile app
другая информационная система
integration service
Power Automate
n8n
```

Ей нужен не HTML-интерфейс, а данные.

Она может отправить HTTP request:

```http
GET /api/resource/Request/REQ-0001
```

и получить JSON.

Упрощённо:

```text
External program
      ↓ HTTP
Frappe REST API
      ↓
Document API / permissions
      ↓
Database
```

---

## 3. REST API Frappe создаётся автоматически для DocTypes

Если существует DocType:

```text
Request
```

не нужно вручную писать endpoint только для базовых CRUD-операций.

Framework уже умеет:

```text
Create
Read
Update
Delete
List
```

для Documents этого DocType.

Это одна из ключевых возможностей Frappe как application framework.

---

## 4. API работает с теми же Documents

REST API не создаёт отдельную интеграционную таблицу.

Если API создаёт:

```text
Request REQ-0007
```

то сотрудник увидит этот же Document в Desk.

Схема:

```text
Desk
Web Form
REST API
Data Import
Python code
   ↓
Request Document
```

---

# Часть II. В v16 есть API v1 и API v2

## 5. Старый привычный API — v1

Классические маршруты:

```text
/api/resource/Request
/api/resource/Request/REQ-0001
/api/method/...
```

В v16 это API v1.

Его можно вызывать двумя способами:

```text
/api/...
/api/v1/...
```

То есть:

```text
/api/resource/Request
```

и:

```text
/api/v1/resource/Request
```

маршрутизируются в один v1 API.

---

## 6. API v2 тоже штатно существует в v16

Начиная с Frappe v15 Framework содержит API v2.

В v16 routes выглядят иначе:

```text
/api/v2/document/Request
/api/v2/document/Request/REQ-0001/
/api/v2/doctype/Request/count
/api/v2/doctype/Request/meta
```

API v2 не отменяет v1.

Оба механизма существуют параллельно.

---

## 7. Не путай версии API и версию Frappe

Например:

```text
Frappe Framework v16
```

может обслуживать:

```text
API v1
API v2
```

Это разные понятия.

---

## 8. В этой главе сначала разбираем v1

Причина практическая:

```text
/api/resource
```

до сих пор очень распространён и хорошо показывает базовую модель.

После этого отдельно сравним v2.

---

# Часть III. Базовый URL

## 9. Base URL

Пусть Site доступен по адресу:

```text
https://frappe.example.com
```

Тогда endpoint:

```text
/api/resource/Request
```

означает полный URL:

```text
https://frappe.example.com/api/resource/Request
```

---

## 10. API — часть того же Site

REST API не требует отдельного сервера.

Обычно:

```text
https://frappe.example.com
├── /desk
├── /request
├── /api/resource/Request
└── /api/v2/document/Request
```

обслуживаются одним Frappe Site.

---

# Часть IV. Authentication пока только на уровне идеи

## 11. API request выполняется от имени пользователя

Frappe должен понимать:

```text
кто делает request
```

Потому что от этого зависят permissions.

Обычно API работает через:

```text
API Key + API Secret
session login
OAuth access token
```

Подробно authentication разберём в главе 43.

---

## 12. Authorization не превращает пользователя в Administrator

Если API token принадлежит пользователю:

```text
integration@example.com
```

request выполняется с permissions этого пользователя.

То есть API не означает:

```text
есть API key
→ можно читать всю базу
```

---

## 13. Без authentication request идёт как Guest

Это не значит, что REST API автоматически становится публичным.

Guest сможет сделать только то, что Framework реально разрешает Guest-контексту.

Важно сравнить с предыдущей главой:

```text
Public Web Form
→ имеет специальный controlled insert flow

REST resource API
→ обычный Document permission flow
```

Поэтому публичная Web Form и публичный REST Create — совсем не одно и то же.

---

# Часть V. v1: List Documents

## 14. Получить список Documents

Для DocType:

```text
Request
```

выполняем:

```http
GET /api/resource/Request
```

Ответ имеет вид:

```json
{
  "data": [
    {"name": "REQ-0001"},
    {"name": "REQ-0002"}
  ]
}
```

---

## 15. По умолчанию возвращается только `name`

Это правильное поведение для list endpoint.

Framework не отправляет автоматически все поля всех Documents.

По умолчанию:

```text
fields = name
```

---

## 16. `fields`

Чтобы получить конкретные поля:

```http
GET /api/resource/Request?fields=["name","subject","status"]
```

Параметр `fields` передаётся как JSON array.

Ответ:

```json
{
  "data": [
    {
      "name": "REQ-0001",
      "subject": "Printer broken",
      "status": "Open"
    }
  ]
}
```

---

## 17. Не запрашивай `*` автоматически

Даже если Framework позволяет более широкий field selection, интеграция обычно должна запрашивать только нужные поля.

Лучше:

```text
name
status
modified
```

чем:

```text
все 80 полей
```

Причины:

```text
меньше traffic
меньше лишних данных
проще контракт
меньше риск случайно раскрыть ненужные поля
```

---

# Часть VI. Filters

## 18. `filters`

Нужно получить только открытые заявки:

```http
GET /api/resource/Request?filters=[["status","=","Open"]]
```

Можно передать несколько условий:

```text
status = Open
priority = High
```

По смыслу:

```json
[
  ["status", "=", "Open"],
  ["priority", "=", "High"]
]
```

---

## 19. Несколько обычных filters соединяются через AND

То есть:

```text
status = Open
AND
priority = High
```

---

## 20. `or_filters`

Если нужна логика OR, v1 `frappe.client.get_list` поддерживает:

```text
or_filters
```

Например по смыслу:

```text
priority = High
OR
priority = Urgent
```

---

## 21. Filter — не permission bypass

Если пользователь имеет право видеть только часть Request Documents, filter не может расширить этот доступ.

Смысл правильный:

```text
permissions
→ определяют доступную область

filters
→ сужают результат внутри неё
```

а не наоборот.

---

# Часть VII. Sorting и pagination

## 22. `order_by`

Например:

```http
GET /api/resource/Request?order_by=modified%20desc
```

По смыслу:

```text
ORDER BY modified DESC
```

---

## 23. List endpoint пагинируется

По умолчанию v1 устанавливает:

```text
limit_page_length = 20
```

То есть один request не должен автоматически выгружать всю таблицу.

---

## 24. `limit_start`

Начальная позиция:

```text
limit_start = 0
```

Следующая страница при размере 20:

```text
limit_start = 20
```

---

## 25. `limit_page_length`

Размер страницы:

```http
GET /api/resource/Request?limit_start=0&limit_page_length=100
```

---

## 26. `limit` — alias в v1

Текущий v1 route делает:

```text
limit
→ limit_page_length
```

если `limit_page_length` явно не задан.

Поэтому можно встретить:

```http
?limit=100
```

---

## 27. Интеграция должна уметь ходить по страницам

Плохая модель:

```text
GET 100000 records одним request
```

Лучше:

```text
page 1
page 2
page 3
...
```

Особенно если данные постоянно растут.

---

# Часть VIII. Получить один Document

## 28. Read by name

```http
GET /api/resource/Request/REQ-0001
```

Framework делает по смыслу:

```python
doc = frappe.get_doc("Request", "REQ-0001")
doc.check_permission("read")
```

---

## 29. Field-level permissions тоже применяются

После read permission текущий v1 вызывает:

```text
apply_fieldlevel_read_permissions()
```

Это продолжение главы 19.

Permission Level — не только UI hiding в Desk.

API response тоже должен учитывать разрешённые поля.

---

## 30. `expand_links`

В актуальном v1 можно запросить:

```http
GET /api/resource/Request/REQ-0001?expand_links=True
```

Тогда Link / Dynamic Link values могут быть развёрнуты в связанные документы, причём Framework отдельно проверяет read permission связанных Documents.

Это удобно, но может сильно увеличить payload и количество работы.

Использовать нужно осознанно.

---

# Часть IX. Create

## 31. Создать Document

```http
POST /api/resource/Request
Content-Type: application/json
```

Body:

```json
{
  "subject": "Printer broken",
  "priority": "High",
  "description": "Floor 2"
}
```

---

## 32. Framework создаёт настоящий Document

Текущий v1 делает по смыслу:

```python
frappe.new_doc("Request", **data).insert()
```

Поэтому это не SQL INSERT напрямую.

---

## 33. Document lifecycle продолжает работать

При REST Create продолжают иметь значение:

```text
naming
mandatory fields
Link validation
controller before_insert
controller validate
after_insert
hooks
notifications
versioning
и другая Document logic
```

в соответствии с обычным lifecycle.

---

## 34. Create permission тоже проверяется

В отличие от Public Web Form, стандартный REST resource endpoint не вызывает:

```text
insert(ignore_permissions=True)
```

Текущий v1 вызывает обычный:

```text
insert()
```

Поэтому authenticated API user должен реально иметь право создавать этот DocType.

---

## 35. API не должен требовать Administrator для обычной интеграции

Правильнее создать отдельного integration user с минимальными нужными правами.

Например:

```text
Request
Read   = yes
Create = yes
Write  = yes
Delete = no
```

Если интеграции Delete не нужен, его не надо выдавать.

Принцип:

> API user должен иметь минимально достаточные permissions.

---

# Часть X. Update

## 36. v1 Update

```http
PUT /api/resource/Request/REQ-0001
Content-Type: application/json
```

Body:

```json
{
  "priority": "Low"
}
```

---

## 37. Не нужно отправлять весь Document

Хотя HTTP method называется:

```text
PUT
```

v1 ведёт себя практически как partial update.

Framework загружает существующий Document:

```python
doc = frappe.get_doc(doctype, name, for_update=True)
```

затем:

```python
doc.update(data)
doc.save()
```

Поэтому можно отправить только изменяемые fields.

---

## 38. Write permission проверяется обычным `save()`

REST Update не является отдельным каналом обхода write access.

Если user не может сохранить Document обычной permission model, API тоже не должен дать это сделать.

---

## 39. Controller validation работает и при Update

Если controller запрещает:

```text
Closed → Open
```

при определённом условии, API Update должен получить ту же validation error.

Это ещё одна причина хранить business rules на сервере, а не только в Desk Client Script.

---

# Часть XI. Delete

## 40. Удалить Document

```http
DELETE /api/resource/Request/REQ-0001
```

v1 вызывает:

```python
frappe.delete_doc(...)
```

---

## 41. Delete требует соответствующее permission

API key сам по себе Delete не даёт.

Если у пользователя нет Delete permission, операция должна завершиться ошибкой доступа.

---

## 42. Удаление может быть запрещено ссылками

Даже при Delete permission Document может участвовать в ссылочной целостности.

Например:

```text
другой Document Link → REQ-0001
```

и Framework может не позволить удалить его обычным способом.

REST API не отменяет link integrity.

---

## 43. DELETE v1 возвращает HTTP 202

Текущая реализация v1 после успешного удаления устанавливает:

```text
HTTP 202
```

и возвращает:

```text
ok
```

Это полезно учитывать клиенту, который ошибочно считает успешным только `200`.

---

# Часть XII. Child Tables

## 44. Document JSON может содержать Child Table

Если `Request` содержит:

```text
items → Table / Request Item
```

API response одного Document может включать:

```json
{
  "name": "REQ-0001",
  "items": [
    {
      "item": "Monitor",
      "qty": 2
    }
  ]
}
```

---

## 45. Child row остаётся частью Parent Document

Общая модель не меняется:

```text
Parent
└── Child rows
```

Поэтому безопаснее мыслить REST update так же, как Form save:

```text
изменяем структуру Document
→ сохраняем Parent lifecycle
```

---

## 46. Update Child Table требует аккуратности

Если отправить новый массив child rows, нужно точно понимать, что должно произойти с существующими rows.

Для сложного merge/reconcile лучше не строить логику на догадке клиента.

Часто правильнее сделать отдельный server-side method с явной бизнес-семантикой.

Это уже мост к главе 42.

---

# Часть XIII. Response format

## 47. Resource API v1 возвращает данные под `data`

Например:

```json
{
  "data": {
    "name": "REQ-0001",
    "subject": "Printer broken"
  }
}
```

или list:

```json
{
  "data": [
    {"name": "REQ-0001"},
    {"name": "REQ-0002"}
  ]
}
```

---

## 48. Не путай `data` и `message`

В Frappe часто встречаются оба response keys.

Упрощённо:

```text
REST resource endpoint
→ обычно data

RPC / whitelisted method
→ часто message
```

RPC подробно разберём в следующей главе.

---

## 49. Клиент должен проверять HTTP status, а не только JSON body

Плохой код:

```text
если JSON пришёл → успех
```

Правильнее:

```text
HTTP status
+
response body
```

Потому что API может вернуть:

```text
401 / 403
404
409-подобную business conflict logic
417/422-style framework errors в зависимости от exception path
429
500
```

Клиент должен быть готов к ошибочным HTTP responses.

---

# Часть XIV. Ошибки Frappe

## 50. Validation error — нормальный API outcome

Например внешний клиент отправил:

```json
{
  "priority": "SUPER_HIGH"
}
```

а Select field такого значения не допускает.

Это не повод обходить validation.

Клиент должен получить ошибку, исправить payload или бизнес-логику.

---

## 51. PermissionError — отдельный класс проблемы

Если request корректен структурно, но пользователь не имеет доступа, это не validation problem.

Нужно различать:

```text
неверные данные
нет permission
Document не существует
конфликт состояния
server error
```

---

## 52. Не показывай raw traceback конечному пользователю

API client может логировать технические details для диагностики, но UI внешней системы не должен бездумно показывать пользователю весь stack trace.

Для production integration нужны:

```text
нормальный error mapping
короткое пользовательское сообщение
technical log отдельно
```

---

# Часть XV. `debug=True`

## 53. v1 list поддерживает debug

Можно передать:

```http
GET /api/resource/Request?debug=True
```

Тогда response может содержать debug information о выполненном query и времени.

Это удобно для разработки.

---

## 54. Debug не должен быть основой production-клиента

Использовать:

```text
для диагностики
```

а не:

```text
в каждом production request
```

---

# Часть XVI. `as_dict`

## 55. По умолчанию list возвращает объекты

```json
[
  {"name": "REQ-0001"}
]
```

---

## 56. `as_dict=False`

v1 list поддерживает:

```http
?as_dict=False
```

и может вернуть rows как arrays.

Например:

```json
[
  ["REQ-0001", "Open"],
  ["REQ-0002", "Closed"]
]
```

Для большинства интеграций dict/object format понятнее и устойчивее к чтению.

---

# Часть XVII. Expand в list

## 57. `expand`

Актуальный v1 `frappe.client.get_list` поддерживает:

```text
expand
```

для разворачивания выбранных Link fields в list response.

Параметр передаётся JSON array.

---

## 58. Expand увеличивает связность API response

Это удобно:

```text
Request.department
→ сразу получить данные Department
```

но интеграционный контракт становится тяжелее.

Иногда проще сделать два понятных request-а, чем возвращать большое дерево связанных объектов.

---

# Часть XVIII. API v2

## 59. v2 использует `/document/`, а не `/resource/`

Вместо:

```text
/api/resource/Request
```

v2 использует:

```text
/api/v2/document/Request
```

---

## 60. v2 List

```http
GET /api/v2/document/Request
```

Поддерживаются параметры вроде:

```text
fields
filters
order_by
start
limit
group_by
as_dict
debug
```

---

## 61. v2 pagination использует `start` и `limit`

Например:

```http
GET /api/v2/document/Request?start=0&limit=20
```

Это отличается от привычного v1:

```text
limit_start
limit_page_length
```

---

## 62. v2 сообщает `has_next_page`

Текущий v2 получает:

```text
limit + 1
```

records и по этому признаку устанавливает:

```json
{
  "has_next_page": true
}
```

Это удобнее для клиента, чем самостоятельно угадывать наличие следующей страницы.

---

## 63. v2 Read

```http
GET /api/v2/document/Request/REQ-0001/
```

Текущая реализация явно выполняет:

```text
read permission
field-level read permissions
```

перед возвратом dict.

---

## 64. v2 Create

```http
POST /api/v2/document/Request
```

Body:

```json
{
  "subject": "Printer broken",
  "priority": "High"
}
```

Внутри используется обычный:

```text
new_doc → insert()
```

---

## 65. v2 Update поддерживает PATCH и PUT

```http
PATCH /api/v2/document/Request/REQ-0001/
```

или:

```http
PUT /api/v2/document/Request/REQ-0001/
```

Body может содержать изменяемые fields.

Это более естественная HTTP-модель, чем v1, где partial update исторически выполняется через PUT.

---

## 66. v2 Delete

```http
DELETE /api/v2/document/Request/REQ-0001/
```

Использует штатный delete flow Frappe.

---

# Часть XIX. Дополнительные возможности v2

## 67. Copy Document

v2 имеет endpoint:

```http
GET /api/v2/document/Request/REQ-0001/copy
```

Он возвращает чистую копию Document, пригодную как основа для создания нового.

При этом исходный Document сначала проверяется на:

```text
read permission
```

---

## 68. Count

```http
GET /api/v2/doctype/Request/count
```

Позволяет получить count records с учётом поддерживаемого count flow.

Это удобнее, чем скачивать list только ради количества.

---

## 69. Meta

```http
GET /api/v2/doctype/Request/meta
```

возвращает metadata DocType через v2 API.

Это полезно для generic clients, которые строят интерфейс или validation на основе metadata.

Но не нужно тащить meta в каждую простую интеграцию, если контракт полей уже известен.

---

## 70. Document methods в v2

v2 содержит route:

```text
/api/v2/document/<doctype>/<name>/method/<method>/
```

для whitelisted document methods.

Например framework-level actions вроде:

```text
submit
cancel
```

могут выполняться как document method flow.

Это уже не обычный CRUD, поэтому подробно будет в главе 42.

---

# Часть XX. v1 против v2

## 71. Сравнение

| Возможность | v1 | v2 |
|---|---|---|
| Base prefix | `/api` или `/api/v1` | `/api/v2` |
| List | `/resource/<doctype>` | `/document/<doctype>` |
| Read one | `/resource/<doctype>/<name>` | `/document/<doctype>/<name>/` |
| Create | POST | POST |
| Partial update | PUT | PATCH или PUT |
| Delete | DELETE | DELETE |
| Count endpoint | не отдельный resource route | `/doctype/<doctype>/count` |
| Meta endpoint | не основной resource route | `/doctype/<doctype>/meta` |
| Copy | нет отдельного route | есть |
| `has_next_page` | нет штатного флага list route | есть |
| Document method route | legacy resource POST / RPC patterns | отдельный `/method/<method>/` |

---

## 72. v1 не объявлен «нерабочим» только потому, что есть v2

В v16:

```text
/api
```

по-прежнему специально маршрутизируется в v1.

Поэтому существующие интеграции на `/api/resource` не нужно переписывать только ради номера версии без причины.

---

## 73. Для нового клиента версию нужно выбрать явно

Хорошо зафиксировать в integration contract:

```text
Frappe API v1
```

или:

```text
Frappe API v2
```

а не писать абстрактно:

```text
"ходим в API Frappe"
```

потому что route и pagination semantics отличаются.

---

# Часть XXI. Permissions в REST API

## 74. API не имеет отдельной магической permission model

Основная идея:

```text
request authenticated as User X
→ операции выполняются в контексте User X
```

Поэтому продолжают иметь значение:

```text
Role Permission
User Permission
Owner
Share
Permission Level
custom permission hooks
```

в зависимости от конкретной операции.

---

## 75. List v1 использует `frappe.get_list()`

Текущий v1 вызывает:

```python
frappe.client.get_list(...)
```

а тот использует:

```python
frappe.get_list(...)
```

То есть list retrieval является permission-aware.

---

## 76. v2 list тоже не игнорирует permissions

Текущий v2 создаёт query через:

```text
ignore_permissions = False
```

Поэтому v2 collection endpoint также не является unrestricted database query.

---

## 77. Read one проверяет Document permission

И v1, и v2 явно вызывают:

```text
check_permission("read")
```

для single-document read.

---

## 78. Field Level Permissions тоже важны

После read Framework применяет field-level read permissions.

Это значит:

```text
API user видит Document
```

ещё не обязательно означает:

```text
API user видит каждое его поле
```

---

## 79. Integration user — обычный security principal

Относись к нему как к отдельному пользователю системы.

Нужно определить:

```text
какие DocTypes читает
какие создаёт
какие изменяет
какие удаляет
какие records видит
какие поля видит
```

---

# Часть XXII. API и lifecycle

## 80. REST API не равно direct DB access

Это один из главных выводов главы.

Схема:

```text
REST payload
→ Document
→ permission check
→ validation
→ lifecycle
→ database
```

а не:

```text
REST payload
→ SQL table напрямую
```

---

## 81. Это хорошо для согласованности

Если правило живёт в controller:

```python
def validate(self):
    ...
```

оно применяется независимо от того, кто меняет Document:

```text
Desk
REST API
Web Form
Data Import
Python code
```

с учётом особенностей каждого flow.

---

## 82. Но custom controller может сделать API дорогим

Если каждый `save()` делает:

```text
10 тяжёлых queries
3 внешних HTTP calls
большой пересчёт
```

массовая REST integration будет медленной.

Проблема тогда не обязательно в HTTP.

Проблема может быть в стоимости lifecycle одного Document.

---

# Часть XXIII. REST CRUD против business command

## 83. Не каждое действие является «изменить поле»

Например бизнес-команда:

```text
Approve Request
```

может требовать:

```text
проверить состояние
проверить роль
создать связанные Documents
записать комментарий
отправить notification
```

Пытаться представить это как:

```http
PUT {"status":"Approved"}
```

может быть слишком примитивно.

---

## 84. CRUD хорош для data-oriented операций

Например:

```text
создать справочник
прочитать заявку
изменить description
получить список records
```

---

## 85. RPC хорош для command-oriented операций

Например:

```text
approve_request()
generate_invoice()
recalculate_totals()
close_period()
```

То есть удобная граница:

```text
работаем с ресурсом
→ REST

вызываем бизнес-команду
→ RPC / whitelisted method
```

Следующая глава будет именно об этом.

---

# Часть XXIV. File Upload

## 86. Файл не нужно запихивать в JSON Document вручную

Frappe имеет специальный upload endpoint.

В v1:

```text
/api/method/upload_file
```

В v2:

```text
/api/v2/method/upload_file
```

---

## 87. Пример curl

```bash
curl -X POST \
  https://frappe.example.com/api/method/upload_file \
  -H 'Accept: application/json' \
  -H 'Authorization: token API_KEY:API_SECRET' \
  -F file=@./document.pdf
```

Authentication подробно разберём позже.

---

## 88. Attachment к Document требует контекста

При upload можно передавать параметры, связывающие File с Document.

Нужно различать:

```text
просто загрузить File
```

и:

```text
прикрепить File к Request REQ-0001
```

Общая модель `File` уже разобрана в главе 31.

---

# Часть XXV. HTTP headers

## 89. Для JSON requests задавай Content-Type

Обычный набор:

```http
Accept: application/json
Content-Type: application/json
```

---

## 90. Authorization header

Для token authentication используется header вида:

```http
Authorization: token API_KEY:API_SECRET
```

Не вставляй секреты:

```text
в URL
в Git
в frontend source code
в публичный лог
```

Подробно — глава 43.

---

# Часть XXVI. URL encoding

## 91. JSON query parameters нужно корректно кодировать

Например:

```text
fields=["name","subject"]
filters=[["status","=","Open"]]
```

в реальном HTTP client должны быть корректно URL-encoded.

Не собирай production URL огромной строковой конкатенацией, если библиотека умеет передавать query params отдельно.

---

## 92. Лучше пользоваться HTTP client library

Например Python:

```python
requests.get(
    url,
    params={
        "fields": '["name","subject"]',
        "filters": '[["status","=","Open"]]',
    },
)
```

чем вручную экранировать каждый символ URL.

---

# Часть XXVII. Rate limiting

## 93. Frappe имеет общий rate limiter

Site configuration может задавать:

```text
rate_limit
```

с параметрами:

```text
limit
window
```

---

## 94. Глобальный limiter учитывает не просто количество requests

Текущая реализация глобального rate limiter накапливает затраченное request execution time внутри window.

При превышении лимита Framework может вернуть:

```text
HTTP 429 Too Many Requests
```

и headers вроде:

```text
X-RateLimit-Limit
X-RateLimit-Remaining
X-RateLimit-Reset
Retry-After
```

---

## 95. Отдельные endpoints могут иметь собственный decorator rate limit

В Framework также существует:

```python
@rate_limit(...)
```

для ограничения конкретных endpoints.

Поэтому клиент должен быть готов к `429`, а не бесконечно долбить сервер повторными запросами.

---

## 96. Retry должен иметь backoff

Плохо:

```text
429
→ мгновенно повторить 1000 раз
```

Правильнее:

```text
учесть Retry-After
подождать
повторить ограниченное число раз
```

---

# Часть XXVIII. API Request Log

## 97. Frappe умеет логировать API requests

В текущем API entry point есть проверка System Setting:

```text
log_api_requests
```

Если она включена, создаётся:

```text
API Request Log
```

с данными вроде:

```text
path
user
HTTP method
```

---

## 98. API log не нужно путать с вечным audit archive

Operational log полезен для диагностики, но политика хранения и его юридическая значимость — отдельный вопрос.

Не проектируй критичный audit только на предположении:

```text
API Request Log всегда хранится навсегда
```

---

# Часть XXIX. Performance

## 99. Не делай N+1 requests без необходимости

Плохо:

```text
GET 1000 Request names
→ для каждого ещё GET /Request/<name>
```

если нужные поля можно сразу получить list endpoint:

```text
fields=["name","status","priority"]
```

---

## 100. Но не превращай один response в огромный graph

Другая крайность:

```text
expand всё
все child tables
все links
100000 rows
```

Нужен баланс.

---

## 101. Для incremental sync используй стабильный cursor strategy

Типичный вариант:

```text
modified > last_sync_timestamp
```

с сортировкой:

```text
modified asc
```

Но нужно продумать границы timestamp, одинаковые значения modified, retries и idempotency.

Это уже интеграционная архитектура, а не только syntax REST API.

---

## 102. Массовая интеграция и Data Import — разные инструменты

```text
одноразово загрузить готовую таблицу
→ Data Import

регулярно синхронизировать системы
→ API / integration code
```

Не нужно каждую синхронизацию превращать в ручную загрузку Excel.

---

# Часть XXX. Idempotency и дубли

## 103. POST Create по природе может создать новый Document повторно

Если client не получил response из-за сетевой ошибки:

```text
request дошёл до Frappe
Document создался
response потерялся
```

клиент может повторить POST и получить второй Document.

---

## 104. Для критичных интеграций нужен внешний ключ

Например поле:

```text
external_id
```

с уникальностью.

Flow:

```text
external system ID
→ найти existing
→ update или create
```

или отдельный idempotent server-side method.

---

## 105. Naming series не является integration idempotency key

```text
REQ-0001
REQ-0002
```

генерируется уже внутри Frappe.

Внешней системе часто нужен свой устойчивый identifier.

---

# Часть XXXI. Concurrency

## 106. Два клиента могут менять один Document одновременно

Сценарий:

```text
Client A прочитал version 1
Client B прочитал version 1
Client A сохранил version 2
Client B пытается сохранить старые данные
```

Document lifecycle Frappe имеет механизмы проверки актуальности документа, но интеграцию всё равно нужно проектировать с пониманием конкуренции.

---

## 107. Не делай blind overwrite без причины

Особенно опасно:

```text
GET весь Document
изменить одно поле
через минуту PUT вернуть весь старый JSON
```

Можно затереть изменения другого пользователя.

Для partial update отправляй только действительно изменяемые fields.

---

# Часть XXXII. Security

## 108. Никогда не давай API user лишние права «чтобы точно работало»

Плохой подход:

```text
System Manager
все DocTypes
Read/Write/Create/Delete
```

для интеграции, которой нужен один справочник.

---

## 109. Ограничивай не только DocType, но и данные

Если интеграция должна видеть только:

```text
Company = A
```

нужно продумать:

```text
User Permissions
custom permission query
owner/share model
отдельный integration DocType
```

в зависимости от задачи.

Filter в URL сам по себе security boundary не создаёт.

---

## 110. Не доверяй payload

REST client может отправить любые поля, которые знает.

Поэтому важные ограничения должны быть на сервере:

```text
field permissions
Document permissions
controller validation
whitelisted command validation
```

---

## 111. Не выдавай API Secret frontend-приложению

Если JavaScript выполняется в browser конечного пользователя, любой встроенный secret можно извлечь.

Схема:

```text
browser JS
+ permanent API Secret
```

обычно неправильна.

Для browser/mobile auth используются user/session/OAuth-подходы, а не один серверный integration secret на всех.

---

# Часть XXXIII. REST API против прямого SQL

## 112. REST сохраняет application boundary

Преимущества:

```text
permissions
validation
Document lifecycle
version compatibility на уровне публичного API
HTTP separation
```

---

## 113. Direct SQL быстрее только в очень узком смысле

Если внешняя программа напрямую пишет:

```text
tabRequest
```

она может обойти:

```text
controller
naming
links
permissions
hooks
business invariants
```

Поэтому внешний integration client не должен получать доступ к базе только ради того, чтобы «API медленнее».

---

## 114. Для аналитики может быть другой сценарий

Read-only BI replica / warehouse может читать данные напрямую по специально спроектированному pipeline.

Но это уже аналитическая архитектура, а не CRUD integration с бизнес-системой.

---

# Часть XXXIV. Практика через curl

## 115. Подготовим переменные

Для примеров:

```bash
BASE_URL="https://frappe.example.com"
API_KEY="your_api_key"
API_SECRET="your_api_secret"
```

Никогда не коммить реальные secrets в Git.

---

## 116. Получить текущего пользователя

Это уже RPC endpoint, но удобно проверить authentication:

```bash
curl "$BASE_URL/api/method/frappe.auth.get_logged_user" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json"
```

---

## 117. List Request

```bash
curl "$BASE_URL/api/resource/Request?fields=%5B%22name%22%2C%22subject%22%2C%22status%22%5D&limit_page_length=20" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json"
```

---

## 118. Read one

```bash
curl "$BASE_URL/api/resource/Request/REQ-0001" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json"
```

---

## 119. Create

```bash
curl -X POST "$BASE_URL/api/resource/Request" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "API test",
    "priority": "Medium",
    "description": "Created from REST API"
  }'
```

---

## 120. Update

```bash
curl -X PUT "$BASE_URL/api/resource/Request/REQ-0001" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "High"
  }'
```

---

## 121. Delete

Только на тестовом Document:

```bash
curl -X DELETE "$BASE_URL/api/resource/Request/REQ-TEST" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json"
```

---

# Часть XXXV. Практика v2

## 122. List v2

```bash
curl "$BASE_URL/api/v2/document/Request?limit=20" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json"
```

---

## 123. Read v2

```bash
curl "$BASE_URL/api/v2/document/Request/REQ-0001/" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json"
```

---

## 124. PATCH v2

```bash
curl -X PATCH "$BASE_URL/api/v2/document/Request/REQ-0001/" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "Low"
  }'
```

---

## 125. Count v2

```bash
curl "$BASE_URL/api/v2/doctype/Request/count" \
  -H "Authorization: token $API_KEY:$API_SECRET" \
  -H "Accept: application/json"
```

---

# Часть XXXVI. Практика через Python

## 126. Простой GET

```python
import requests

base_url = "https://frappe.example.com"
api_key = "..."
api_secret = "..."

headers = {
    "Authorization": f"token {api_key}:{api_secret}",
    "Accept": "application/json",
}

response = requests.get(
    f"{base_url}/api/resource/Request",
    headers=headers,
    params={
        "fields": '["name","subject","status"]',
        "filters": '[["status","=","Open"]]',
        "limit_page_length": 20,
    },
    timeout=30,
)

response.raise_for_status()
rows = response.json()["data"]

for row in rows:
    print(row)
```

---

## 127. Всегда ставь timeout

Плохо:

```python
requests.get(url)
```

без timeout в production integration.

Сетевой вызов может зависнуть намного дольше, чем ожидается.

---

## 128. Проверяй status

```python
response.raise_for_status()
```

или собственная явная обработка:

```text
2xx
401/403
404
429
5xx
```

---

## 129. Логируй correlation context

Для серьёзной интеграции полезно логировать:

```text
operation
DocType
external_id
Frappe document name
HTTP status
attempt
```

но не секреты.

---

# Часть XXXVII. Типичные ошибки

## 130. Ошибка: использовать Administrator token везде

Так интеграция работает быстрее только до первого security incident.

Создавай отдельного user и выдавай минимальные permissions.

---

## 131. Ошибка: считать API отдельной моделью данных

Не нужно создавать duplicate fields только потому, что данные приходят по REST.

API работает с тем же DocType.

---

## 132. Ошибка: bypass lifecycle через прямую БД

Если интеграция должна создавать бизнес-Documents, она обычно должна проходить через Frappe application layer.

---

## 133. Ошибка: выгружать всю таблицу каждый час

Плохо:

```text
500000 records
× 24 раза в сутки
```

если изменилось 200 records.

Нужен incremental sync.

---

## 134. Ошибка: игнорировать pagination

Если сегодня таблица содержит 15 records, это не значит, что через год их не станет 150000.

Клиент должен быть готов к pages с самого начала.

---

## 135. Ошибка: retries без idempotency

Повторный POST после timeout может создать дубль.

Нужны:

```text
external_id
unique constraint
или idempotent command
```

---

## 136. Ошибка: использовать PUT как бизнес-команду

```text
{"status":"Approved"}
```

не всегда эквивалентно:

```text
Approve
```

Если действие имеет бизнес-семантику, оформляй её server-side method.

---

## 137. Ошибка: считать URL filter security rule

```text
?company=ACME
```

не запрещает клиенту убрать filter.

Security должна контролироваться Framework/server code.

---

# Часть XXXVIII. Как выбирать между инструментами

## 138. Decision table

| Задача | Инструмент |
|---|---|
| Внешняя программа читает Documents | REST API |
| Внешняя программа создаёт обычный Document | REST API POST |
| Частично изменить поля Document | REST PUT/PATCH |
| Получить список с filters | REST collection endpoint |
| Выполнить бизнес-команду | RPC / whitelisted method |
| Человек заполняет публичную форму | Web Form |
| Массово один раз загрузить Excel | Data Import |
| Постоянная синхронизация систем | REST/RPC + integration code |
| Аналитическая выгрузка миллионов строк | отдельный ETL/warehouse подход |

---

# Часть XXXIX. Архитектурная граница

## 139. REST API — data interface

Модель:

```text
Client
→ resource URL
→ CRUD
→ Document
```

---

## 140. RPC — command interface

Модель:

```text
Client
→ named method
→ business operation
→ Documents / side effects
```

---

## 141. Хорошая система обычно использует оба подхода

Например:

```text
GET /api/v2/document/Request/REQ-0001/
→ прочитать Request

PATCH /api/v2/document/Request/REQ-0001/
→ изменить description

POST /api/v2/method/my_app.api.approve_request
→ выполнить бизнес-команду Approve
```

Не нужно пытаться все задачи втиснуть только в REST или только в RPC.

---

# Что нужно запомнить

1. Frappe автоматически создаёт REST API для DocTypes.
2. REST API работает с теми же Documents, что Desk, Web Form и Python code.
3. В Frappe v16 одновременно существуют API v1 и API v2.
4. `/api/...` и `/api/v1/...` ведут в v1.
5. v1 CRUD использует `/api/resource/<doctype>`.
6. v2 CRUD использует `/api/v2/document/<doctype>`.
7. List endpoint по умолчанию возвращает ограниченную страницу records, а не всю таблицу.
8. `fields`, `filters`, `or_filters`, sorting и pagination нужно использовать осознанно.
9. REST API не обходит permissions authenticated пользователя.
10. Single-document read применяет read permission и field-level read permissions.
11. REST Create проходит обычный `insert()` и требует Create permission; это отличается от специального Public Web Form flow.
12. REST Update проходит обычный `save()` и Document validation.
13. REST Delete проходит штатный delete flow и link integrity.
14. v1 PUT работает как partial update.
15. v2 поддерживает PATCH и PUT.
16. v2 дополнительно имеет `count`, `meta`, `copy` и `has_next_page`.
17. API user лучше делать отдельным пользователем с минимальными permissions.
18. Filter в URL — не security boundary.
19. Permanent API secrets нельзя хранить во frontend code или Git.
20. Для регулярной синхронизации нужны pagination, retry strategy, idempotency и incremental sync.
21. Повторный POST после timeout может создать дубль, если не спроектирован внешний idempotency key.
22. Массовая интеграция не должна автоматически читать всю таблицу на каждом запуске.
23. CRUD по ресурсам и бизнес-команды — разные задачи.
24. Data-oriented операции естественно делать через REST, command-oriented операции — через RPC / whitelisted methods.
25. Следующая глава посвящена именно RPC и whitelisted methods.

---

# Источники

Официальная документация Frappe Framework:

- [REST API](https://docs.frappe.io/framework/user/en/api/rest)
- [REST API — Introduction](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [Listing Documents](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/listing_documents)
- [Manipulating DocTypes](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/manipulating_documents)
- [Authentication](https://docs.frappe.io/framework/user/en/api/rest#authentication)

Для поведения v16 дополнительно сверено с исходным кодом ветки `version-16`:

- [`frappe/api/__init__.py`](https://github.com/frappe/frappe/blob/version-16/frappe/api/__init__.py)
- [`frappe/api/v1.py`](https://github.com/frappe/frappe/blob/version-16/frappe/api/v1.py)
- [`frappe/api/v2.py`](https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py)
- [`frappe/client.py`](https://github.com/frappe/frappe/blob/version-16/frappe/client.py)
- [`frappe/rate_limiter.py`](https://github.com/frappe/frappe/blob/version-16/frappe/rate_limiter.py)

---

Следующая глава: **42. RPC и whitelisted methods**.
