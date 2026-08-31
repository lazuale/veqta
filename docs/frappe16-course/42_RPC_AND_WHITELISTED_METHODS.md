# 42. RPC и whitelisted methods

В главе 41 мы разобрали REST API как интерфейс работы с данными:

```text
Create Document
Read Document
Update Document
Delete Document
List Documents
```

Но не каждая операция является обычным CRUD.

Иногда внешнему клиенту нужно сказать системе не:

```text
измени поле status
```

а:

```text
approve_request()
recalculate_total()
close_period()
send_invitation()
```

Для таких задач во Frappe есть RPC — вызов серверных Python-методов по HTTP.

Главный вопрос этой главы:

```text
как безопасно превратить Python-функцию
в вызываемую HTTP-команду
```

Проверено: **2026-08-31**.

---

# Часть I. RPC простыми словами

## 1. REST работает с ресурсом

REST-мышление:

```text
GET Request REQ-0001
PATCH Request REQ-0001
DELETE Request REQ-0001
```

То есть клиент работает прежде всего с состоянием Document.

---

## 2. RPC вызывает действие

RPC-мышление:

```text
approve_request("REQ-0001")
```

или:

```text
rebuild_summary("2026-08")
```

Клиент обращается не к таблице напрямую, а к именованной серверной операции.

---

## 3. Аналогия

REST можно представить как:

> «Дай мне карточку документа и измени в ней эти поля».

RPC — как:

> «Выполни команду, смысл которой уже определён на сервере».

---

## 4. RPC особенно полезен для бизнес-команд

Например операция:

```text
Approve Request
```

может означать одновременно:

```text
проверить права
проверить текущий статус
проверить обязательные данные
изменить состояние
создать связанные записи
отправить Notification
записать аудит
```

Это уже не просто изменение одного поля.

Такую операцию естественнее держать в одном server-side method.

---

# Часть II. Обычная Python-функция ещё не API

## 5. Допустим, в App есть функция

Файл:

```text
my_app/api.py
```

Код:

```python
def hello(name):
    return f"Hello, {name}"
```

Из другого Python-кода App её можно вызвать обычным способом.

Но HTTP-клиент вызвать её не может.

---

## 6. Frappe не публикует все Python-функции автоматически

Это критично.

Иначе любой импортируемый метод App мог бы случайно стать удалённо вызываемым.

Для HTTP-доступа функция должна быть явно разрешена.

---

## 7. Для этого нужен `@frappe.whitelist()`

```python
import frappe

@frappe.whitelist()
def hello(name):
    return f"Hello, {name}"
```

Теперь функция включена в набор whitelisted methods.

---

## 8. Что означает whitelist

В этом контексте:

```text
whitelisted
=
разрешено вызывать через HTTP RPC-механизм Frappe
```

Это не означает:

```text
разрешено любому пользователю
```

и не означает:

```text
permissions больше не нужны
```

Это только первый шлюз.

---

# Часть III. Dotted path

## 9. RPC вызывает функцию по Python path

Если функция находится здесь:

```text
my_app/api.py
```

и называется:

```python
hello
```

её dotted path будет:

```text
my_app.api.hello
```

---

## 10. В API v1 вызов выглядит так

```http
GET /api/method/my_app.api.hello?name=Alex
```

или явно через v1:

```http
GET /api/v1/method/my_app.api.hello?name=Alex
```

---

## 11. В API v2

```http
GET /api/v2/method/my_app.api.hello?name=Alex
```

RPC есть и в v1, и в v2.

---

## 12. Функция должна быть импортируема

Нельзя придумать произвольный URL вроде:

```text
/api/method/approve
```

если Frappe не может разрешить соответствующий Python method.

Обычно используется полный путь:

```text
app.module.function
```

---

## 13. Короткие shorthand-вызовы — не основа для нового кода

В `version-16` handler уже содержит deprecation warning для RPC shorthand без полного dotted path и указывает на удаление такого поведения в v17.

Поэтому в новом коде используй полный путь:

```text
my_app.api.some_method
```

а не рассчитывай на короткое имя.

---

# Часть IV. Самый маленький рабочий пример

## 14. Server-side method

```python
import frappe

@frappe.whitelist()
def add(a: int, b: int):
    return a + b
```

---

## 15. Вызов через curl

```bash
curl "https://example.com/api/method/my_app.api.add?a=2&b=3"
```

Для метода без `allow_guest=True` запрос должен быть аутентифицирован.

Способы аутентификации разберём в следующей главе.

---

## 16. Возвращаемое значение становится JSON

Для v1 типичный успешный ответ:

```json
{
  "message": 5
}
```

Frappe помещает return value whitelisted method в `message`.

---

## 17. В API v2 оболочка отличается

Маршруты v2 проходят через общий v2 API dispatcher, поэтому return value попадает в:

```json
{
  "data": 5
}
```

Это маленькое, но важное различие клиента v1 и v2.

Не хардкодь один response shape для всех API versions.

---

# Часть V. GET и POST — не просто стиль

## 18. GET используем для чтения

Например:

```python
@frappe.whitelist(methods=["GET"])
def get_open_request_count():
    ...
```

Смысл:

```text
получить данные
не изменяя состояние системы
```

---

## 19. POST используем для команды, которая что-то меняет

```python
@frappe.whitelist(methods=["POST"])
def approve_request(name):
    ...
```

Например она может:

```text
изменить Document
создать запись
отправить Communication
запустить дальнейший процесс
```

---

## 20. Это связано и с транзакциями

В v16 после успешного HTTP request Frappe смотрит на HTTP method.

Для unsafe methods изменения БД коммитятся.

Для безопасных read-oriented requests транзакция в конце запроса откатывается, если код специально не запросил commit.

Практическое правило:

> Не делай database mutation через GET.

---

## 21. Официальная документация формулирует правило проще

```text
если method только возвращает данные → GET
если method изменяет database state → POST
```

Этого правила достаточно почти всегда.

---

# Часть VI. `methods=` в `@frappe.whitelist()`

## 22. HTTP methods можно ограничить явно

```python
@frappe.whitelist(methods=["POST"])
def approve_request(name):
    ...
```

Теперь GET-вызов будет отклонён.

---

## 23. Для read method

```python
@frappe.whitelist(methods=["GET"])
def get_summary():
    ...
```

---

## 24. Можно разрешить несколько методов

```python
@frappe.whitelist(methods=["GET", "POST"])
def some_method():
    ...
```

Но делать это без причины не стоит.

Чем уже контракт, тем понятнее API.

---

## 25. Важная деталь v16

Если `methods=` не передан, текущая реализация `frappe.whitelist()` регистрирует:

```text
GET
POST
PUT
DELETE
```

Поэтому просто:

```python
@frappe.whitelist()
```

технически шире, чем обычно нужно.

Для application API лучше явно указывать ожидаемый HTTP method.

---

## 26. Framework реально проверяет HTTP method

Перед вызовом handler сравнивает:

```text
frappe.request.method
```

с набором методов, зарегистрированных для конкретной whitelisted function.

То есть `methods=["POST"]` — не документация для человека, а реальное ограничение.

---

# Часть VII. `allow_guest=True`

## 27. Обычный whitelisted method требует вошедшего пользователя

```python
@frappe.whitelist()
def my_method():
    ...
```

`Guest` такой метод вызвать не может.

---

## 28. Чтобы разрешить анонимный вызов

```python
@frappe.whitelist(allow_guest=True)
def public_method():
    ...
```

Теперь endpoint доступен без login.

---

## 29. `allow_guest=True` — это серьёзное решение

После этого Internet client потенциально может вызывать метод без User account.

Нужно сразу думать про:

```text
input validation
rate limiting
spam
enumeration
abuse
sensitive data
side effects
```

---

## 30. Не используй `allow_guest=True` для исправления PermissionError

Плохая логика:

```text
метод не вызывается
→ поставим allow_guest=True
```

Это не «ослабить одну проверку».

Это сделать endpoint публичным.

---

## 31. Guest method не должен доверять входным данным

Например:

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_request(customer, amount):
    ...
```

нельзя считать `customer` доказательством личности отправителя.

Пользователь сам формирует HTTP request.

---

# Часть VIII. Guest input sanitation и `xss_safe`

## 32. v16 дополнительно обрабатывает параметры Guest RPC

В `is_whitelisted()` Framework проверяет:

```text
session.user == "Guest"
```

и для обычного guest method sanitizes строковые значения в `frappe.form_dict`.

Это снижает риск простого HTML/XSS payload в публичных параметрах.

---

## 33. Есть флаг `xss_safe=True`

Технически можно написать:

```python
@frappe.whitelist(allow_guest=True, xss_safe=True)
def public_html_method(html):
    ...
```

Для такого метода стандартная guest sanitization не применяется тем же способом.

---

## 34. Для новичка правило простое

> Не ставь `xss_safe=True`, пока точно не понимаешь, зачем нужен несanitized input.

Это advanced security switch, а не настройка производительности.

---

# Часть IX. Whitelist не равен authorization

## 35. Это самая важная мысль главы

```text
@frappe.whitelist()
```

означает:

```text
HTTP может дойти до функции
```

но не означает:

```text
текущий пользователь имеет право выполнить бизнес-действие
```

---

## 36. Пример опасного метода

```python
@frappe.whitelist(methods=["POST"])
def delete_anything(doctype, name):
    frappe.db.delete(doctype, {"name": name})
```

Сам факт whitelist не добавит правильную authorization logic.

Такой метод может стать обходом обычной permission model.

---

## 37. Whitelisted method выполняется в контексте текущего пользователя

Полезная точка:

```python
frappe.session.user
```

Она показывает пользователя текущего request.

Но метод должен использовать этот контекст правильно.

---

# Часть X. Проверка Role

## 38. Для role-based business command есть `frappe.only_for()`

Пример:

```python
@frappe.whitelist(methods=["POST"])
def close_period(period):
    frappe.only_for("Accounts Manager")
    ...
```

Если у пользователя нет разрешённой роли, Frappe бросит PermissionError.

---

## 39. Можно разрешить несколько ролей

```python
frappe.only_for(["Operations Manager", "System Manager"])
```

Достаточно одной из них.

---

## 40. Но Role не всегда достаточно

Пользователь может иметь роль:

```text
Project Manager
```

но иметь право только на конкретные Projects.

Тогда нужен ещё data-level permission check.

---

# Часть XI. Проверка Document permission

## 41. Если команда работает с конкретным Document

Нужно проверять права на него.

Например:

```python
@frappe.whitelist(methods=["POST"])
def approve_request(name):
    doc = frappe.get_doc("Request", name)
    doc.check_permission("write")
    ...
```

---

## 42. Для read-команды

```python
doc.check_permission("read")
```

---

## 43. Можно использовать permission-aware retrieval

Например:

```python
frappe.get_list(...)
```

работает с permission model.

А прямые database-level shortcuts нужно использовать сознательно.

---

## 44. `frappe.get_all()` — не permission boundary

Как и в предыдущих главах:

```python
frappe.get_all(...)
```

не следует воспринимать как безопасный способ выдавать portal/API данные текущему пользователю.

Для RPC endpoint особенно важно не сделать собственный data leak.

---

# Часть XII. Document methods

## 45. Whitelisted method может быть методом controller класса

Например DocType:

```text
Request
```

Controller:

```python
import frappe
from frappe.model.document import Document

class Request(Document):

    @frappe.whitelist(methods=["POST"])
    def approve(self):
        ...
```

Это instance method конкретного Document.

---

## 46. Отличие от module-level function

Module-level:

```python
@frappe.whitelist()
def get_statistics():
    ...
```

работает как самостоятельная функция.

Document method:

```python
def approve(self):
```

работает вокруг конкретного `self` Document.

---

## 47. Document method удобен, когда команда принадлежит объекту

Например:

```text
Request.approve()
Invoice.recalculate()
Contract.close()
```

Логика естественно живёт рядом с controller этого DocType.

---

# Часть XIII. Document method в API v2

## 48. v2 имеет отдельный красивый route

```http
POST /api/v2/document/Request/REQ-0001/method/approve/
```

Framework:

```text
загрузит Request REQ-0001
проверит whitelisted method
проверит допустимый HTTP method
проверит document permission
вызовет doc.run_method(...)
```

---

## 49. Для GET document method

v2 проверяет:

```text
read permission
```

---

## 50. Для POST document method

v2 проверяет:

```text
write permission
```

до выполнения метода.

Это полезная встроенная защита instance-method route.

---

## 51. После выполнения v2 снова применяет field-level read permissions

То есть отправляемый обратно Document проходит field-level filtering.

---

# Часть XIV. v1 document method

## 52. В v1 механизм старее

`/api/resource/<doctype>/<name>/` с POST может использоваться для запуска whitelisted Document method через параметр:

```text
run_method
```

Это backward-compatible route.

---

## 53. Для нового integration code v2 route понятнее

```text
/api/v2/document/<doctype>/<name>/method/<method>/
```

лучше выражает смысл операции.

Но v1 остаётся частью Frappe 16 и встречается в существующем коде.

---

# Часть XV. v2 controller-level RPC

## 54. API v2 имеет ещё один route

```text
/api/v2/method/<doctype>/<method>
```

Например концептуально:

```text
/api/v2/method/Request/get_statistics
```

---

## 55. Что делает Framework

v2 загружает Python module controller указанного DocType и разворачивает method в реальный dotted path.

Это вызов whitelisted function из controller module.

---

## 56. Не путай его с instance method

Есть две разные идеи:

```text
controller module function
```

и:

```text
method конкретного Document
```

Для второго существует:

```text
/api/v2/document/<doctype>/<name>/method/<method>/
```

---

# Часть XVI. `run_doc_method` в v2

## 57. В v2 есть специальный endpoint

```text
/api/v2/method/run_doc_method
```

Он умеет запускать whitelisted controller method на переданном Document representation.

---

## 58. Для чего это нужно

Это полезно клиентам, которые держат Document state у себя и хотят передать его server-side controller method для обработки/валидации.

Например UI может иметь ещё не сохранённое состояние документа.

---

## 59. Это advanced mechanism

Для обычной внешней интеграции чаще достаточно:

```text
REST CRUD
+
обычные whitelisted API functions
+
instance document method
```

`run_doc_method` не нужно использовать только потому, что он существует.

---

# Часть XVII. Аргументы RPC

## 60. Параметры запроса превращаются в аргументы функции

Функция:

```python
@frappe.whitelist(methods=["GET"])
def greet(name, title=None):
    return f"Hello {title or ''} {name}"
```

может быть вызвана с параметрами request.

---

## 61. GET query parameters

```http
GET /api/method/my_app.api.greet?name=Alex&title=Mr
```

---

## 62. JSON body

Для POST удобно передавать JSON:

```json
{
  "name": "REQ-0001",
  "comment": "Approved"
}
```

Frappe разбирает JSON object в request arguments.

---

## 63. Form data тоже поддерживается

Обычный form-encoded request также попадает в `frappe.form_dict`.

Это важно, например, для file upload и browser forms.

---

## 64. Но API contract лучше держать простым

Плохой метод:

```python
def do_everything(data, flags, options, mode, type, action, force, extra):
```

Лучше несколько ясных операций с понятными параметрами.

---

# Часть XVIII. Type hints

## 65. Whitelist v16 оборачивает функцию type validation механизмом

При регистрации method Framework использует argument type validation для вызовов в request/test context.

Поэтому такие сигнатуры полезны:

```python
@frappe.whitelist(methods=["POST"])
def set_priority(name: str, priority: int):
    ...
```

---

## 66. Type hint не заменяет business validation

Даже если:

```text
priority: int
```

нужно отдельно проверить допустимый диапазон:

```python
if priority not in (1, 2, 3):
    frappe.throw("Invalid priority")
```

---

## 67. Проверяем смысл, а не только тип

Например:

```text
amount = -100
```

может быть корректным числом, но некорректным бизнес-значением.

---

# Часть XIX. Возвращаемые значения

## 68. Можно вернуть простое значение

```python
return 42
```

---

## 69. Можно вернуть dict

```python
return {
    "status": "ok",
    "name": doc.name,
}
```

Это обычно самый удобный контракт.

---

## 70. Можно вернуть list

```python
return [
    {"name": "REQ-0001"},
    {"name": "REQ-0002"},
]
```

---

## 71. Возвращаемое значение должно сериализоваться в JSON

Не нужно возвращать произвольные Python objects, которые JSON encoder не понимает.

Document обычно можно преобразовать:

```python
doc.as_dict()
```

---

## 72. Не возвращай больше данных, чем нужно

Плохой API:

```python
return frappe.get_all("User", fields=["*"])
```

если клиенту нужны только:

```text
name
full_name
```

Минимальный response легче поддерживать и безопаснее.

---

# Часть XX. Ошибки

## 73. Для ожидаемой business error используй Frappe exception flow

Например:

```python
if doc.status != "Draft":
    frappe.throw("Only Draft requests can be approved")
```

---

## 74. Permission errors должны быть именно permission errors

Например:

```python
doc.check_permission("write")
```

или:

```python
frappe.throw_permission_error()
```

---

## 75. Не превращай ошибки в `{"success": false}` без причины

Плохой шаблон:

```python
try:
    ...
except Exception as e:
    return {"success": False, "error": str(e)}
```

Так ты скрываешь нормальный HTTP/error flow Frappe.

Пусть реальные ошибки становятся ошибками request.

---

## 76. Client должен различать success и failure по HTTP/API response

Не только по текстовому полю внутри JSON.

---

# Часть XXI. Транзакция RPC

## 77. Один request обычно является одной transaction boundary

Упрощённо:

```text
HTTP request
→ method
→ DB changes
→ success
→ commit
```

для state-changing HTTP method.

---

## 78. Если внутри метода возникает exception

Frappe request pipeline выполняет rollback.

Поэтому не нужно вручную пытаться откатывать каждое изменение обычного request.

---

## 79. Не разбрасывай `frappe.db.commit()` внутри business method без необходимости

Если сделать ранний commit:

```text
изменение A → commit
изменение B → exception
```

A уже нельзя автоматически откатить вместе с B.

Обычная request transaction как раз защищает от такого полусостояния.

---

# Часть XXII. REST field update против RPC command

## 80. Плохая модель approval

Client делает:

```http
PATCH /Request/REQ-0001
```

```json
{
  "status": "Approved"
}
```

и вся business logic живёт в клиенте.

---

## 81. Лучше

```http
POST /api/method/my_app.api.approve_request
```

```json
{
  "name": "REQ-0001"
}
```

А сервер сам решает:

```text
можно ли approve
что проверить
какое состояние выставить
какие side effects выполнить
```

---

## 82. Почему это устойчивее

Если завтра правила изменятся, не придётся обновлять каждый внешний клиент.

Server-side command остаётся единым источником business behavior.

---

# Часть XXIII. Не дублируй Document lifecycle

## 83. Если операция уже существует у Document

Например:

```text
submit
cancel
```

не нужно вручную менять:

```text
docstatus
```

через SQL или прямой field update.

Используй штатную Document operation.

---

## 84. RPC должен вызывать доменную операцию, а не ломать её

Например:

```python
doc.submit()
```

а не:

```python
frappe.db.set_value("Request", name, "docstatus", 1)
```

---

# Часть XXIV. Server-side validation остаётся главным

## 85. RPC client нельзя считать доверенным

Даже если это собственный frontend.

Любой request можно воспроизвести отдельно через:

```text
curl
Postman
Python
browser devtools
```

---

## 86. Client-side validation — UX

Например JavaScript проверяет:

```text
amount > 0
```

Это удобно пользователю.

Но server method должен проверить то же бизнес-условие там, где оно действительно критично.

---

# Часть XXV. `frappe.call()` из Desk

## 87. RPC нужен не только внешним системам

Frappe JavaScript API имеет:

```javascript
frappe.call(...)
```

Он вызывает whitelisted Python method с browser side.

---

## 88. Простой пример

```javascript
frappe.call({
    method: "my_app.api.get_summary",
    args: {
        project: "PROJ-0001"
    }
}).then(r => {
    console.log(r.message);
});
```

---

## 89. Server side

```python
@frappe.whitelist(methods=["GET"])
def get_summary(project: str):
    ...
```

---

## 90. Это тот же security boundary

Неважно, что вызов пришёл из собственного Desk JS.

Whitelisted method всё равно нельзя считать доверенным только потому, что кнопку нарисовали вы.

---

# Часть XXVI. `frappe.call()` и REST — не конкуренты

## 91. `frappe.call()` — client helper

Он удобен внутри Frappe browser environment.

---

## 92. HTTP API — внешний контракт

Другой сервис обычно использует:

```text
HTTP library
curl
requests
fetch
axios
```

и вызывает тот же RPC endpoint напрямую.

---

## 93. Server method при этом может быть одним и тем же

```text
Desk JS
      ┐
      ├→ my_app.api.approve_request
External integration
      ┘
```

если permissions и API contract подходят обоим клиентам.

---

# Часть XXVII. Rate limiting для чувствительных RPC

## 94. Публичный или дорогой endpoint может требовать отдельного limit

В Framework есть decorator:

```python
from frappe.rate_limiter import rate_limit
```

для ограничения частоты конкретного endpoint.

---

## 95. Это особенно актуально для

```text
OTP
password reset-like flows
public search
expensive calculation
public form actions
external callbacks
```

---

## 96. Rate limit не заменяет permissions

Это разные задачи:

```text
authorization
→ имеет ли право

rate limit
→ как часто можно
```

Нужны обе, если сценарий этого требует.

---

# Часть XXVIII. Идемпотентность business commands

## 97. POST может быть повторён клиентом

Например:

```text
request отправлен
server выполнил команду
response потерялся
client повторил POST
```

---

## 98. Опасная команда

```text
charge_customer()
create_invoice()
issue_bonus()
```

может сработать дважды.

---

## 99. Для критичных commands нужна защита от duplicate execution

Например:

```text
external_request_id
idempotency key
unique integration reference
проверка текущего state
```

---

## 100. Хорошая state transition сама часто частично защищает

Например:

```text
Draft → Approved
```

и повторный `approve()` на уже Approved Document должен быть явно отклонён или безопасно обработан.

---

# Часть XXIX. Long-running RPC

## 101. Не каждый процесс должен выполняться прямо внутри HTTP request

Например:

```text
пересчитать 2 миллиона строк
сформировать огромный экспорт
обработать сотни файлов
```

может занять слишком долго.

---

## 102. Тогда RPC может только поставить job

Упрощённо:

```text
POST command
→ validate request
→ enqueue background job
→ быстро вернуть job/reference
```

Background Jobs подробно разберём в главе 53.

---

## 103. Не держи browser request открытым без необходимости

Долгий synchronous endpoint сложнее:

```text
retry
monitor
масштабировать
защищать от timeout
```

---

# Часть XXX. Где хранить API methods в App

## 104. Для небольшого App нормально иметь

```text
my_app/api.py
```

Например:

```text
my_app/
└── api.py
```

---

## 105. При росте можно разделить по областям

```text
my_app/api/
├── requests.py
├── projects.py
└── integrations.py
```

Тогда dotted path остаётся понятным:

```text
my_app.api.requests.approve
```

---

## 106. Не делай одну гигантскую `api.py`

Если там сотни unrelated methods, API layer превращается в свалку.

Группируй команды по бизнес-смыслу.

---

# Часть XXXI. API layer не обязан содержать всю логику

## 107. Хороший whitelisted method часто тонкий

Например:

```python
@frappe.whitelist(methods=["POST"])
def approve_request(name: str):
    doc = frappe.get_doc("Request", name)
    doc.check_permission("write")
    return doc.approve()
```

---

## 108. Основная business logic может жить в controller/service

Это полезно, чтобы ту же операцию можно было вызвать из:

```text
RPC
background job
hook
test
internal Python code
```

без имитации HTTP request.

---

## 109. Whitelist — transport boundary

Удобная архитектура:

```text
HTTP RPC layer
→ authorization / input parsing
→ domain/service/controller method
→ database
```

---

# Часть XXXII. Ошибка: whitelist внутренних helpers

## 110. Не каждая функция должна быть endpoint

Если функция нужна только внутри Python:

```python
def calculate_internal_score(doc):
    ...
```

оставь её обычной функцией.

---

## 111. Чем меньше public API surface, тем лучше

Каждый whitelisted method — это контракт, который нужно:

```text
защищать
тестировать
документировать
поддерживать
```

---

# Часть XXXIII. Ошибка: универсальный `execute(action, payload)`

## 112. Соблазнительный API

```python
@frappe.whitelist(methods=["POST"])
def execute(action, payload):
    ...
```

а внутри:

```text
if action == approve
if action == delete
if action == export
if action == recalc
```

---

## 113. Почему это плохо

Теряется ясность:

```text
permissions
HTTP contract
логирование
тестирование
идемпотентность
```

---

## 114. Лучше отдельные методы

```text
approve_request
cancel_request
recalculate_request
```

с собственной проверкой входа и прав.

---

# Часть XXXIV. `override_whitelisted_methods`

## 115. App может переопределить стандартный whitelisted method

Для этого у Frappe есть hook:

```python
override_whitelisted_methods = {
    "some.original.method": "my_app.api.replacement"
}
```

---

## 116. Handler применяет override перед вызовом

То есть клиент может обращаться к старому dotted path, а Framework перенаправит выполнение на override.

---

## 117. Это extension point, а не первый способ кастомизации

Используй его, когда действительно нужно заменить поведение существующего public method.

Hooks подробно разберём позже.

---

# Часть XXXV. API Server Script

## 118. Handler v16 умеет маршрутизировать API Server Scripts

Перед обычным Python method Frappe проверяет map Server Scripts типа API.

Это low-code способ создать server endpoint.

---

## 119. Но граница та же

API Server Script всё равно является externally callable server logic.

Нужно так же думать про:

```text
permissions
input validation
side effects
public exposure
```

Server Script отдельно разберём в главе 45.

---

# Часть XXXVI. Вызов метода не должен обходить permission model случайно

## 120. Опасные low-level операции

Внутри whitelisted method можно написать код, который напрямую меняет данные:

```text
frappe.db.sql
frappe.db.set_value
frappe.db.delete
```

Некоторые такие операции не воспроизводят полный Document permission/lifecycle flow.

---

## 121. Поэтому RPC требует большей дисциплины, чем стандартный REST CRUD

REST route Framework уже знает, что нужно проверить для Document operation.

В custom method часть authorization responsibility переходит разработчику.

---

## 122. Предпочитай Document API, когда работаешь с Document behavior

```python
doc = frappe.get_doc("Request", name)
doc.check_permission("write")
doc.status = "Approved"
doc.save()
```

лучше, чем скрытый SQL update, если нужно сохранить обычный lifecycle.

---

# Часть XXXVII. Audit и observability

## 123. Хорошая business command должна оставлять понятный след

В зависимости от процесса это может быть:

```text
Version
Comment
Communication
custom audit DocType
status history
integration log
```

---

## 124. Не рассчитывай только на HTTP access log

Access log показывает, что endpoint вызвали.

Он не всегда объясняет business meaning результата.

---

## 125. Для интеграций полезен correlation/reference id

Например:

```text
external_request_id
source_system
source_event_id
```

Это сильно упрощает расследование повторов и ошибок.

---

# Часть XXXVIII. Практический пример: `approve_request`

## 126. Плохая версия

```python
@frappe.whitelist(allow_guest=True)
def approve_request(name):
    frappe.db.set_value("Request", name, "status", "Approved")
```

Проблемы:

```text
Guest access
не ограничен HTTP method
нет permission check
нет state validation
обход обычного Document behavior
```

---

## 127. Намного лучше

```python
import frappe

@frappe.whitelist(methods=["POST"])
def approve_request(name: str):
    doc = frappe.get_doc("Request", name)
    doc.check_permission("write")

    if doc.status != "Draft":
        frappe.throw("Only Draft requests can be approved")

    doc.status = "Approved"
    doc.save()

    return {
        "name": doc.name,
        "status": doc.status,
    }
```

---

## 128. Ещё лучше, если approval является частью domain controller

Controller:

```python
class Request(Document):

    def approve(self):
        if self.status != "Draft":
            frappe.throw("Only Draft requests can be approved")

        self.status = "Approved"
        self.save()
        return self
```

API layer:

```python
@frappe.whitelist(methods=["POST"])
def approve_request(name: str):
    doc = frappe.get_doc("Request", name)
    doc.check_permission("write")
    doc.approve()

    return {
        "name": doc.name,
        "status": doc.status,
    }
```

Теперь business operation можно переиспользовать без HTTP.

---

# Часть XXXIX. Пример instance method v2

## 129. Controller

```python
class Request(Document):

    @frappe.whitelist(methods=["POST"])
    def approve(self):
        if self.status != "Draft":
            frappe.throw("Only Draft requests can be approved")

        self.status = "Approved"
        self.save()

        return {
            "name": self.name,
            "status": self.status,
        }
```

---

## 130. HTTP call

```bash
curl -X POST \
  "https://example.com/api/v2/document/Request/REQ-0001/method/approve/" \
  -H "Authorization: token API_KEY:API_SECRET"
```

v2 сам требует write permission на этот Document перед вызовом POST instance method.

---

# Часть XL. Пример read RPC

## 131. Method

```python
@frappe.whitelist(methods=["GET"])
def get_my_open_requests():
    return frappe.get_list(
        "Request",
        filters={"status": "Open"},
        fields=["name", "subject", "modified"],
        order_by="modified desc",
        limit_page_length=20,
    )
```

---

## 132. Почему `get_list()` здесь важен

Он вписывается в permission-aware query flow.

Не нужно делать:

```python
frappe.get_all("Request", fields=["*"])
```

только потому, что это короче.

---

# Часть XLI. Пример public RPC

## 133. Публичный read endpoint

```python
@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_public_status(reference: str):
    ...
```

---

## 134. Что нужно проверить дополнительно

Даже если endpoint read-only:

```text
можно ли перебрать reference
не раскрывает ли он существование чужих объектов
не отдаёт ли персональные данные
нужен ли rate limit
достаточно ли непредсказуем reference
```

Public read API тоже может утекать данные.

---

# Часть XLII. RPC и auth

## 135. Whitelist отвечает на вопрос

```text
можно ли эту Python-функцию вызывать через HTTP вообще
```

---

## 136. Authentication отвечает на другой вопрос

```text
кто делает request
```

---

## 137. Authorization отвечает на третий вопрос

```text
имеет ли этот пользователь право выполнить действие
```

Схема:

```text
HTTP request
→ Authentication
→ Whitelist gate
→ HTTP method gate
→ Authorization / business checks
→ Method
```

Эти уровни нельзя смешивать.

---

# Часть XLIII. Decision table

## 138. Что выбирать

| Задача | Инструмент |
|---|---|
| Получить Document | REST GET |
| Изменить обычные поля Document | REST PATCH/PUT |
| Создать Document | REST POST |
| Удалить Document | REST DELETE |
| Выполнить бизнес-команду | Whitelisted RPC method |
| Команда относится к одному Document | Whitelisted instance method |
| Read-only helper для Desk JS | `frappe.call()` + GET whitelisted method |
| Публичный API без login | `allow_guest=True` только при явной необходимости |
| Долгая операция | RPC → enqueue background job |
| Заменить существующий public method App | `override_whitelisted_methods` |
| Простая low-code API endpoint | API Server Script, если сценарий подходит |

---

# Часть XLIV. Архитектурная лестница

## 139. Не начинай с RPC, если хватает штатного REST

```text
нужно прочитать Document
→ REST

нужно изменить обычное поле
→ REST

нужно выполнить осмысленную business command
→ RPC
```

---

## 140. Не начинай с public RPC

```text
нужен authenticated method
→ @frappe.whitelist()

реально нужен anonymous endpoint
→ allow_guest=True
```

---

## 141. Не начинай с low-level DB API внутри RPC

```text
можно выполнить через Document lifecycle
→ Document API

нужна осознанная low-level операция
→ database API с явным пониманием permissions/lifecycle
```

---

# Мини-практика

## 142. Создай read method

В собственном App:

```python
import frappe

@frappe.whitelist(methods=["GET"])
def who_am_i():
    return {
        "user": frappe.session.user,
        "roles": frappe.get_roles(),
    }
```

Вызови его под аутентифицированным пользователем.

---

## 143. Создай POST command

```python
@frappe.whitelist(methods=["POST"])
def set_request_priority(name: str, priority: str):
    doc = frappe.get_doc("Request", name)
    doc.check_permission("write")

    if priority not in ("Low", "Medium", "High"):
        frappe.throw("Invalid priority")

    doc.priority = priority
    doc.save()

    return {
        "name": doc.name,
        "priority": doc.priority,
    }
```

---

## 144. Проверь неправильный GET

Попробуй вызвать POST-only method через GET.

Ожидаемый смысл результата:

```text
HTTP method не разрешён
```

---

## 145. Проверь пользователя без Write permission

Endpoint должен отказать на:

```python
doc.check_permission("write")
```

а не успешно изменить запись только потому, что function whitelisted.

---

# Что нужно запомнить

1. RPC нужен для вызова именованных server-side операций, а REST — прежде всего для работы с ресурсами/Documents.
2. Обычная Python-функция не доступна по HTTP автоматически.
3. `@frappe.whitelist()` делает функцию вызываемой через RPC.
4. Whitelist не означает, что метод разрешён любому пользователю.
5. `allow_guest=True` отдельно разрешает вызов без login и расширяет публичную attack surface.
6. Для нового RPC используй полный Python dotted path.
7. v1 RPC доступен через `/api/method/...` и `/api/v1/method/...`.
8. v2 RPC доступен через `/api/v2/method/...`.
9. v1 обычно возвращает return value в `message`, v2 — в `data`.
10. Read-only method естественно вызывать GET, state-changing command — POST.
11. В `@frappe.whitelist(methods=[...])` лучше явно ограничивать допустимые HTTP methods.
12. В текущем v16 без `methods=` whitelist по умолчанию регистрирует GET, POST, PUT и DELETE.
13. Framework действительно проверяет HTTP method перед вызовом.
14. Guest parameters по умолчанию проходят дополнительную sanitization; `xss_safe=True` — advanced security option.
15. Whitelist — это exposure gate, а не authorization policy.
16. Для role checks можно использовать `frappe.only_for()`.
17. Для операции над конкретным Document проверяй его permission.
18. `frappe.get_list()` предпочтительнее permission-bypassing query pattern для user-facing RPC.
19. `frappe.get_all()` нельзя считать permission boundary.
20. Whitelisted method может быть обычной module-level function или Document controller method.
21. v2 имеет явный route `/api/v2/document/<doctype>/<name>/method/<method>/` для instance methods.
22. GET instance method v2 требует read permission, POST — write permission.
23. v1 document method route остаётся для backward compatibility.
24. Type hints полезны, но не заменяют business validation.
25. Возвращай минимальный и стабильный JSON contract.
26. Не скрывай реальные exceptions в самодельном `success: false`, если нормальный error flow Frappe подходит.
27. Не изменяй database state через GET.
28. Не ставь ручной `commit()` посреди обычной business transaction без доказанной необходимости.
29. Для approval/close/recalculate и подобных команд server-side RPC обычно лучше прямого изменения status полем из клиента.
30. Критичные POST commands должны учитывать retries и idempotency.
31. Долгую работу лучше запускать через background job, а не держать HTTP request открытым.
32. Не whitelist внутренние helper functions без необходимости.
33. `override_whitelisted_methods` позволяет App переопределять существующие whitelisted methods.
34. API Server Script — альтернативный low-code endpoint, но имеет те же требования к безопасности.
35. Authentication, whitelist и authorization — три разных уровня.
36. Следующая глава посвящена Authentication для интеграций.

---

# Источники

Официальная документация Frappe Framework:

- [REST API — RPC](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [REST API — Remote Method Calls](https://docs.frappe.io/framework/user/en/api/rest)
- [Server Calls (`frappe.call`)](https://docs.frappe.io/framework/user/en/api/server-calls)
- [Frappe Ajax Call](https://docs.frappe.io/framework/user/en/guides/basics/frappe_ajax_call)
- [Hooks — Override Whitelisted Methods](https://docs.frappe.io/framework/user/en/python-api/hooks)

Для поведения v16 дополнительно сверено с исходным кодом ветки `version-16`:

- [`frappe/__init__.py`](https://github.com/frappe/frappe/blob/version-16/frappe/__init__.py) — `whitelist()`, `is_whitelisted()`, guest methods, allowed HTTP methods, `only_for()`.
- [`frappe/handler.py`](https://github.com/frappe/frappe/blob/version-16/frappe/handler.py) — RPC dispatch, HTTP method validation, document method execution.
- [`frappe/api/__init__.py`](https://github.com/frappe/frappe/blob/version-16/frappe/api/__init__.py) — routing API v1/v2.
- [`frappe/api/v1.py`](https://github.com/frappe/frappe/blob/version-16/frappe/api/v1.py) — RPC v1 и backward-compatible document methods.
- [`frappe/api/v2.py`](https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py) — RPC v2, controller/document method routes, permission mapping.
- [`frappe/app.py`](https://github.com/frappe/frappe/blob/version-16/frappe/app.py) — request transaction, commit/rollback, request parsing.
- [`frappe/rate_limiter.py`](https://github.com/frappe/frappe/blob/version-16/frappe/rate_limiter.py) — endpoint rate limiting.

---

Следующая глава: **43. Authentication для интеграций**.
