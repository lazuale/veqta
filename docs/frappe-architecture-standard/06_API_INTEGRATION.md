# 06. API и Integration — когда использовать встроенный REST, а когда свой контракт

## 1. Frappe автоматически даёт Document REST API

**[FRAPPE DOCS]** Framework генерирует REST API для DocTypes.

Источники:

- https://docs.frappe.io/framework/user/en/api/rest
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api

**[UPSTREAM]** `frappe/api/v2.py` в ветке `version-16` содержит routes для:

```text
GET    /document/<doctype>
POST   /document/<doctype>
GET    /document/<doctype>/<name>
PATCH  /document/<doctype>/<name>
PUT    /document/<doctype>/<name>
DELETE /document/<doctype>/<name>
```

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

Это прямой пруф: обычный CRUD Document уже является ответственностью Framework.

---

## 2. Почему свой CRUD API часто лишний

Типовой anti-pattern:

```text
/api/task/create
/api/task/read
/api/task/update
/api/task/delete
```

где каждый endpoint только вызывает:

```text
frappe.new_doc()
frappe.get_doc()
doc.save()
frappe.delete_doc()
```

**[ARCHITECTURAL INFERENCE]** Такой слой не добавляет новый contract или domain semantics, а лишь переименовывает существующий resource API.

Дополнительная цена:

- ещё один API surface;
- ещё одна документация;
- риск рассинхронизации permissions;
- риск обхода field-level security;
- больше тестов и upgrade responsibility.

---

## 3. Встроенный API проходит через Document model

**[UPSTREAM]** В `frappe/api/v2.py`:

- read выполняет `doc.check_permission("read")`;
- read применяет field-level read permissions;
- create использует `frappe.new_doc(...).insert()`;
- update загружает Document и вызывает `save()`;
- document methods выполняют permission checks.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

Это показывает, почему generic REST API хорошо интегрирован с остальным Framework: он не является отдельной database door.

---

## 4. Когда built-in Document API — хороший default

Подходит, если клиент:

- внутренний;
- понимает Frappe DocType model;
- выполняет обычный CRUD;
- может зависеть от названий DocType/fields;
- не требует отдельного стабильного публичного contract.

Пример:

```text
внутренняя автоматизация создаёт Work Order
и обновляет его обычные поля
```

---

## 5. Когда собственный API оправдан

Встроенный REST не обязан быть внешним контрактом любого продукта.

Свой endpoint разумен, когда нужен:

```text
стабильный публичный contract;
versioning, независимый от DocType schema;
агрегация нескольких DocType;
command semantics;
специальная security boundary;
скрытие внутренней модели;
protocol compatibility;
другая форма payload/response.
```

Пример:

```text
POST /shipment/dispatch
```

внутри может:

- проверить Shipment;
- создать Stock Entry;
- обновить Reservation;
- записать Integration Log;
- поставить background job.

Это уже не «CRUD Shipment».

---

## 6. Resource command vs Document method vs application command

### Обычный CRUD

```text
создать/прочитать/изменить Document
```

→ Document REST API.

### Операция конкретного Document

```text
Order.confirm()
Task.close()
Inspection.complete()
```

→ controller/document method может быть естественным владельцем.

**[UPSTREAM]** REST v2 умеет выполнять whitelisted document methods.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

### Application-level command

```text
generate_monthly_plan()
reconcile_all_open_shipments()
```

→ module/service-level whitelisted method может быть естественнее, потому что операция не принадлежит одному Document.

---

## 7. Whitelisted method — официальный RPC seam

**[FRAPPE DOCS]** REST/RPC API позволяет вызывать whitelisted Python methods.

Источники:

- https://docs.frappe.io/framework/user/en/api/rest
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api

Это не workaround. Это штатный способ expose business operation, которой не соответствует обычный resource CRUD.

Но сам `@frappe.whitelist()` не делает method безопасным автоматически.

Нужно отдельно проверить:

```text
authentication;
authorization;
HTTP method;
input validation;
transaction semantics;
idempotency;
rate/abuse risks при public API.
```

---

## 8. Не использовать внутреннюю реализацию REST как Python API

**[UPSTREAM]** В заголовке `frappe/api/v2.py` есть важное предупреждение: functions файла exposed через routes, но их внутреннюю Python implementation не следует вызывать из application code; location/implementation может меняться без breaking-change guarantee.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

### Универсальное правило

**[ARCHITECTURAL INFERENCE]** Различать:

```text
public/stable API Framework
и
internal implementation Framework
```

Не привязываться к внутреннему модулю только потому, что его можно импортировать.

---

## 9. Webhook — штатный outgoing document event

**[FRAPPE DOCS]** Webhook связывает DocType + Document Event + optional Condition с HTTP callback во внешнюю систему.

Источник:

- https://docs.frappe.io/framework/user/en/guides/integration/webhooks

Подходящий сценарий:

```text
Quotation обновилась
    ↓
POST в внешнюю CRM/шину
```

Webhook может подписывать payload HMAC secret.

### Когда Webhook должен рассматриваться первым

Если требование буквально звучит:

> «Когда с Document произошло X, вызови внешний HTTP endpoint».

---

## 10. Когда Webhook уже недостаточен

Например, нужны:

- гарантированная доставка;
- сложные retries/backoff;
- ordering;
- дедупликация;
- mapping нескольких Documents;
- OAuth token lifecycle;
- rate limits;
- reconciliation;
- dead-letter queue;
- ручной replay.

Тогда это уже отдельная integration responsibility.

**[ARCHITECTURAL INFERENCE]** В таком случае custom integration service/background job не дублирует Webhook, а добавляет недостающую надёжность и orchestration.

---

## 11. Integration service — когда он действительно нужен

Хороший integration service изолирует внешний контракт от Document lifecycle.

Пример:

```text
ExternalTaxService
  authenticate()
  calculate_tax()
  map_error()
  retry_policy()
```

Он решает ответственность, которой Frappe Document не владеет: протокол конкретной внешней системы.

Плохой service:

```text
TaskApiService.create_task(data):
    return frappe.get_doc(data).insert()
```

если это единственная его функция и никакого отдельного контракта нет.

---

## 12. Built-in REST связывает клиента с внутренней schema

Generic endpoint использует имена:

```text
DocType
fieldname
child table fields
```

Для внутренней интеграции это часто удобно и нормально.

Но долгоживущий public API может не хотеть раскрывать внутренние изменения schema наружу.

**[ARCHITECTURAL INFERENCE]** Поэтому выбор такой:

```text
internal Frappe-aware client
    → generic Document API часто достаточно

stable product/external contract
    → dedicated API может быть лучше
```

---

## 13. Incoming integration и permissions

Не решать проблемы интеграции через:

```text
ignore_permissions=True в каждом endpoint
```

Если integration user должен иметь системные права, спроектировать его Role/permissions или отдельную безопасную server-side command boundary.

Подробно: `04_SECURITY.md`.

---

## 14. External side effects и transaction

API call во внешнюю систему — side effect.

Перед вызовом нужно решить:

```text
должен он произойти до commit?
после commit?
в background job?
как обработать duplicate/retry?
```

Подробно: `05_TRANSACTIONS_ASYNC.md`.

---

## 15. API/integration decision track

```text
Нужно обычное CRUD с DocType?
    → Document REST API

Нужно действие конкретного Document?
    → document method

Нужна application/business command?
    → whitelisted service/module method

Нужно сообщить внешний HTTP endpoint о Document event?
    → Webhook

Нужен стабильный внешний contract или aggregation?
    → dedicated API

Нужны retries, reconciliation, mapping, complex auth?
    → integration service + jobs
```

Это не строгая иерархия. Это выбор механизма по ответственности.

---

## 16. Design review API

```text
1. Это CRUD или business command?
2. Клиент может зависеть от DocType schema?
3. Нужен ли отдельный versioned contract?
4. Где происходит authorization?
5. Используются ли Document permission/lifecycle paths?
6. Есть ли ignore_permissions и чем он оправдан?
7. Есть ли external side effects до commit?
8. Нужна ли idempotency?
9. Может ли Webhook решить outbound event без custom code?
10. Не импортируем ли мы internal Frappe API implementation вместо public API?
```
