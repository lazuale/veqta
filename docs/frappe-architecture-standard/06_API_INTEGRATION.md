# 06. API and Integration

## 1. Главная граница

Нужно различать три вещи:

```text
обычный CRUD Document
business command
integration contract
```

Они могут использовать разные механизмы Frappe.

---

## 2. Document REST API

Frappe автоматически предоставляет REST API для DocTypes.

Это сильный default для обычных операций:

```text
create
read
update
delete
```

### Архитектурное следствие

Если внутреннему Frappe-aware клиенту нужно просто работать с Document, не следует автоматически писать четыре собственных endpoints, которые лишь повторяют стандартный CRUD.

### Граница

Generic Document API раскрывает внутреннюю модель DocType: имена полей, child tables и структуру Documents. Для долгоживущего публичного API это может быть нежелательно.

---

## 3. Whitelisted methods

Когда операция является не CRUD, а бизнес-командой, custom method естественен.

Примеры:

```text
approve_request
close_period
generate_statement
dispatch_shipment
```

Команда может затронуть несколько Documents и выполнить orchestration.

---

## 4. Document method или module-level command

Если операция естественно принадлежит конкретному Document:

```text
Order.submit_to_supplier()
```

она может быть controller/document method.

Если операция шире одного Document:

```text
generate_monthly_plan()
```

она может жить в service/module command.

Критерий — ownership ответственности.

---

## 5. Custom CRUD API

Собственный CRUD API не является запрещённым.

Он оправдан, если нужен:

- стабильный внешний contract;
- versioning;
- aggregation нескольких DocTypes;
- специальная security boundary;
- скрытие внутренней Frappe model;
- compatibility с внешним протоколом.

Анти-паттерн — не custom API сам по себе, а бессмысленный дубль generic Document API.

---

## 6. Public contract и internal model

Если внешний клиент зависит от:

```text
/api/v2/document/Work Item
```

он знает внутреннее имя DocType и полей.

При refactoring model это может стать breaking change для интеграции.

Поэтому для публичных/долгоживущих интеграций полезно отдельно решить:

> Может ли внешний contract совпадать с внутренней Document model?

Если да — generic REST отлично подходит.

Если нет — нужен domain API.

---

## 7. Webhook

Когда Frappe должен сообщить внешней системе о событии Document, сначала рассматривается стандартный Webhook.

Пример:

```text
Sales Order submitted
    ↓
HTTP request to external service
```

Webhook подходит для простых event-driven integrations.

---

## 8. Когда Webhook недостаточен

Если нужны:

- сложные retries;
- гарантированная доставка;
- дедупликация;
- transformation pipeline;
- orchestration нескольких systems;
- stateful integration;

может понадобиться custom integration service/background job.

Webhook не нужно превращать в полноценный message broker.

---

## 9. Integration service

Отдельный integration module/service нормален, если он владеет реальной интеграционной ответственностью:

```text
authentication
rate limits
mapping
retry policy
provider errors
versioning
idempotency
```

Такую логику не следует размазывать по нескольким Controllers.

---

## 10. External API client

Хорошая граница:

```text
Document Controller
    → вызывает domain/integration service

Integration Service
    → знает протокол внешней системы
```

Controller не обязан знать URL, OAuth flow и retry semantics стороннего сервиса.

---

## 11. Authentication ≠ Authorization

Custom endpoint может быть authenticated, но всё равно неправильно применять права.

Например:

```python
@frappe.whitelist()
def get_secret_documents():
    return frappe.get_all("Secret Document")
```

Authentication сама по себе не делает этот method безопасным.

Нужно отдельно определить authorization business action.

---

## 12. Permission-aware API

Для Document CRUD стандартный REST использует permission model Framework.

Custom methods должны явно соблюдать требуемую security semantics.

Вопрос review:

> От имени какого principal выполняется операция и какие permissions должны применяться?

---

## 13. API method не должен зависеть от internal REST implementation

Внутренние функции `frappe/api/v2.py` не являются обязательным public Python API.

Нужно использовать документированные Framework APIs (`frappe.get_doc`, Document methods и т. п.), а не импортировать route handlers ради повторного использования кода.

---

## 14. Idempotency integration commands

Команда:

```text
POST /dispatch
```

может быть отправлена повторно из-за network retry.

Следовательно, критические integration commands должны решать:

```text
как определить duplicate?
можно ли выполнить повторно?
что является idempotency key?
```

Особенно для платежей, отгрузок и создания внешних records.

---

## 15. Sync vs async integration

### Синхронно

Подходит, когда:

- ответ нужен пользователю сразу;
- операция быстрая;
- внешний сервис достаточно надёжен;
- transaction semantics понятна.

### Асинхронно

Подходит, когда:

- внешний API медленный;
- нужны retries;
- результат можно получить позже;
- нельзя блокировать web request.

В Frappe естественный механизм — Background Job.

---

## 16. Transaction boundary

Нельзя бездумно отправлять внешний request до commit local transaction.

Для действий, которые должны происходить только после успешного сохранения, рассмотреть:

```text
after_commit
enqueue_after_commit
```

Подробно — `05_TRANSACTIONS_ASYNC.md`.

---

## 17. Mapping

External model не обязана совпадать с DocType 1:1.

Нормально иметь mapping layer:

```text
External Shipment
    ↕ mapping
Delivery Note + Package + Tracking
```

Это не «второй framework». Это реальная integration responsibility.

---

## 18. Web Form как integration surface

Если человеку вне Desk нужно просто создать/редактировать Document через browser, Web Form может быть проще отдельного frontend/API.

Но Web Form не является заменой полноценного public application UX, если требования значительно сложнее.

---

## 19. Uploads/files

Если integration передаёт файлы, использовать стандартный File model/API там, где semantics обычного attachment подходит.

Не хранить base64-файлы в Data/Text fields без отдельной причины.

---

## 20. Versioning public API

Generic Frappe REST versioned вместе с Framework/application model.

Если продукт обещает независимый стабильный внешний contract, его versioning должен проектироваться отдельно.

Например:

```text
/api/my_product/v1/...
```

может быть оправдан, даже если внутри используется Frappe Documents.

---

## 21. Errors

Integration boundary должна преобразовывать internal exceptions в понятный внешний contract там, где API является публичным.

Не следует раскрывать caller'у произвольный traceback как часть бизнес-протокола.

---

## 22. Integration ownership

Перед проектированием определить:

```text
кто system of record?
кто инициирует изменение?
кто имеет authoritative state?
как разрешаются конфликты?
```

Frappe API mechanics не решают эти business questions автоматически.

---

## 23. Polling

Polling не является автоматически костылём.

Он оправдан, если external system не предоставляет webhook/events.

Но не нужно polling'ом имитировать события собственного Frappe Document, для которых уже есть lifecycle/hooks.

---

## 24. Outbox/reliable delivery

Если integration требует гарантированной доставки и replay, обычного Webhook может быть недостаточно.

Тогда отдельный integration event/outbox mechanism может быть оправдан как новая responsibility.

Важно: это уже не дублирование Notification/Webhook, а другой reliability contract.

---

## 25. API decision track

```text
Обычный CRUD Frappe Document?
        → Document REST API

Команда конкретного Document?
        → whitelisted document method

Application/domain command?
        → whitelisted service/module method

Нужен стабильный внешний contract?
        → dedicated domain API

Нужно отправить простой Document event наружу?
        → Webhook

Нужна сложная/reliable integration?
        → integration service + jobs/state
```

---

## 26. Design review checklist

- [ ] Определено, является endpoint CRUD или command.
- [ ] Custom CRUD не дублирует generic API без причины.
- [ ] Public contract осознанно связан или не связан с DocType schema.
- [ ] Custom method применяет authorization.
- [ ] External side effects согласованы с commit.
- [ ] Idempotency рассмотрена.
- [ ] Sync/async модель выбрана осознанно.
- [ ] Webhook рассмотрен для простого outbound event.
- [ ] Complex integration выделена в самостоятельную responsibility.
- [ ] Internal route implementation не используется как public Python API.
- [ ] Определён system of record.
