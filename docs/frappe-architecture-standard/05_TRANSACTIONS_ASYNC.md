# 05. Transactions and Async

## 1. Почему этот раздел обязателен

Без понимания transaction model легко получить систему, где:

- часть данных сохранилась, часть нет;
- внешняя система получила событие до commit;
- background job стартовал раньше сохранения Document;
- ручной `commit()` разрушил atomic operation;
- direct DB update обошёл validation.

Frappe уже имеет собственную transaction semantics. Архитектура приложения должна её учитывать.

---

## 2. Базовая transaction model

Обычный write request выполняется внутри transaction.

Упрощённо:

```text
request
    ↓
Document operations
    ↓
успех
    ↓
commit
```

Если uncaught exception прерывает операцию:

```text
rollback
```

### Архитектурное следствие

Не нужно вручную делать `frappe.db.commit()` после каждого `doc.save()`.

Framework уже управляет нормальной request transaction.

---

## 3. Atomic business operation

Допустим, операция должна:

```text
1. создать Order
2. создать Reservation
3. обновить Inventory State
```

Бизнес ожидает:

```text
либо всё выполнено
либо ничего
```

Это естественная transaction boundary.

### Плохое решение

```text
save Order
COMMIT
save Reservation
ошибка
```

Теперь состояние частично применено.

### Правильный принцип

Не разделять одну atomic business operation ручными commits без необходимости.

---

## 4. Когда ручной commit может быть оправдан

Например:

- отдельная административная batch operation;
- специальная migration logic;
- операция сознательно разбита на checkpoints;
- long-running process с явной recovery model.

Но это уже отдельный design decision.

В обычном Document lifecycle ручной commit — красный флаг для review.

---

## 5. Rollback

Если операция падает до commit, Framework откатывает database changes текущей transaction.

Но rollback базы данных **не может откатить внешний мир**.

Например:

```text
Frappe DB write
HTTP request to external system
email
file write
external payment
```

могут иметь разную transaction semantics.

Это приводит к ключевой проблеме side effects.

---

## 6. External side effect до commit

Пример:

```text
on_update:
    send order to external ERP
```

Последовательность:

```text
Document saved
    ↓
external ERP receives order
    ↓
позже request падает
    ↓
Frappe rollback
```

Результат:

```text
Frappe: Order не существует
External ERP: Order существует
```

### Вывод

External side effects должны проектироваться относительно transaction commit.

---

## 7. after_commit

Frappe предоставляет transaction callbacks, включая действия после успешного commit.

Это полезно для side effects, которые нельзя запускать до того, как database state гарантированно зафиксирован.

Пример conceptual flow:

```text
save Document
    ↓
commit succeeds
    ↓
after_commit callback
    ↓
external side effect
```

---

## 8. enqueue_after_commit

Background job может быть поставлен в очередь после успешного commit.

Это особенно полезно:

```text
Document сохранён
    ↓
после commit
    ↓
job отправляет данные во внешнюю систему
```

Так worker не увидит состояние, которое ещё может rollback.

### Design question

> Job должен существовать, если текущая transaction не commit'нулась?

Если нет — рассмотреть `enqueue_after_commit`.

---

## 9. before_commit / after_commit

Эти callbacks дают явную точку синхронизации с transaction lifecycle.

Но ими не следует заменять нормальную Document logic.

Использовать нужно тогда, когда **момент transaction boundary действительно важен**.

---

## 10. before_rollback / after_rollback

Они полезны для cleanup/compensation локальных side effects, если операция откатывается.

Но внешний irreversible effect часто невозможно просто отменить.

Поэтому лучше не запускать его до commit, чем потом пытаться компенсировать.

---

## 11. Document API и DB API — разные уровни

```python
doc.save()
```

проходит Document lifecycle.

```python
frappe.db.set_value(...)
```

может обновить DB напрямую без обычных Document triggers.

### Следствие

Для обычной business operation, где invariants должны соблюдаться, Document API является естественным default.

Direct DB API используется, когда обход lifecycle **намерен**.

---

## 12. `db_set`

`doc.db_set()` также является более прямым update path и имеет другую event semantics, чем полноценный `save()`.

Его удобно использовать для служебных полей, прогресса или технических updates.

Но не следует применять его для обхода бизнес-validation только потому, что `save()` «мешает» неправильным данным.

---

## 13. Raw SQL

Raw SQL не запрещён.

Он оправдан для:

- сложных bulk operations;
- migrations;
- performance-sensitive internal queries;
- операций, плохо выражаемых ORM/query builder.

Но он сильнее связывает код со схемой и легче обходит Framework behavior.

### Review questions

```text
Нужны ли permissions?
Нужен ли lifecycle?
Нужна ли portability?
Можно ли решить Query Builder/DB API?
```

---

## 14. Background Job

Frappe имеет штатный job subsystem.

Долгая операция не должна удерживать web request без необходимости.

Пример:

```text
пользователь запускает пересчёт 100 000 строк
```

Вместо:

```text
browser waits 5 minutes
```

естественнее:

```text
enqueue job
user continues work
worker processes task
```

---

## 15. Job не только про timeout

Background job также даёт operational separation:

- отдельный worker;
- queue;
- timeout;
- failure handling;
- retries/design around retry;
- job id;
- deduplication;
- post-commit scheduling.

Поэтому job полезен не только для операций «дольше 30 секунд».

---

## 16. Idempotency background jobs

Worker может упасть.

Операция может быть retry.

Пользователь может нажать кнопку дважды.

Следовательно, для критических jobs нужно решить:

> Что произойдёт при повторном запуске?

### Плохой job

```text
каждый запуск безусловно создаёт новую Invoice
```

### Более безопасный подход

Использовать business key/job id/check existing state, если операция должна быть уникальной.

---

## 17. Deduplication

Frappe job API поддерживает job identifiers/deduplication capabilities.

Если одна и та же тяжёлая работа не должна одновременно находиться в queue несколько раз, использовать штатный механизм предпочтительнее собственной таблицы `Running Jobs` без причины.

---

## 18. Job user/security context

Background process может выполняться с user context.

Это нужно учитывать:

```text
job выполняет пользовательскую операцию?
или системную?
```

Не нужно случайно обходить permissions только потому, что код ушёл в background worker.

---

## 19. Queue selection

Frappe имеет разные queues/timeouts.

Короткая interactive работа и тяжёлый import — разные workloads.

Не отправлять всё автоматически в одну long queue только потому, что она существует.

Выбор queue является operational design decision.

---

## 20. Scheduler

Frappe Scheduler предназначен для периодических задач App/site.

Примеры:

```text
каждый час проверить сроки;
раз в день выполнить агрегирование;
еженедельно очистить временные данные.
```

Для такого класса задач отдельный `while True` daemon обычно не нужен.

---

## 21. Scheduler и business event — не одно и то же

Плохой паттерн:

```text
каждую минуту искать Documents,
которые только что изменились
```

если Framework уже имеет lifecycle hooks/Webhook/events для реакции на изменение.

Polling нужен, когда event-driven вариант недоступен или внешняя система не умеет иного.

---

## 22. Когда внешний scheduler нормален

Например:

- enterprise orchestration;
- процесс управляет несколькими системами;
- infrastructure maintenance;
- задача должна существовать независимо от Frappe site.

Нативность не означает, что всё в мире обязано запускаться Scheduler Frappe.

---

## 23. Notification

Для пользовательских уведомлений по условиям/событиям сначала рассматривается стандартный Notification.

Он подходит, когда задача действительно является notification:

```text
при событии X
при условии Y
уведомить Z
```

### Не использовать Notification как

- reliable domain event bus;
- exactly-once integration mechanism;
- complex message broker.

---

## 24. Assignment

Assignment/ToDo — стандартный operational work-assignment mechanism.

Если требование:

> назначить конкретному пользователю работу по Document

сначала рассматривается Assignment.

Но domain field:

```text
account_manager
responsible_engineer
owner_company
```

не обязательно нужно заменять Assignment.

Это могут быть постоянные свойства бизнес-объекта.

---

## 25. Assignment Rule

Если назначения выполняются автоматически по правилам, следует проверить штатные Assignment Rule capabilities до создания собственного round-robin engine.

Но если распределение требует сложной optimization/ML/external planning logic, custom service может быть оправдан.

---

## 26. Event-driven или scheduled

Decision:

```text
Действие должно произойти сразу
после Document event?
        → lifecycle / hook / webhook / enqueue

Действие происходит по времени?
        → Scheduler / Notification date event

Действие тяжёлое?
        → Background Job

Внешняя система не умеет events?
        → controlled polling может быть нормальным
```

---

## 27. Long transaction

Не следует удерживать одну огромную DB transaction без необходимости при обработке миллионов rows.

Для bulk operations иногда нужна batch strategy с checkpoint semantics.

Но это должно проектироваться явно:

```text
что является atomic unit?
как возобновить после failure?
как избежать partial inconsistency?
```

---

## 28. Migration и transaction

Patches также имеют transaction semantics.

Data migration должна быть повторяемой/безопасной относительно upgrade process.

Не проектировать production migration как набор ручных SQL-команд, запускаемых «если предыдущая не упала».

Подробнее — `09_DEPLOYMENT_TESTING.md`.

---

## 29. File system side effects

Database rollback не обязательно удалит вручную созданный внешний файл.

Если операция пишет файлы вне normal File lifecycle, нужно предусмотреть transaction cleanup/recovery.

То же относится к:

- S3/external storage;
- remote API;
- message broker;
- payment provider.

---

## 30. Transaction decision track

```text
Обычная Document business operation?
        → позволить Frappe управлять transaction

Нужен direct DB update?
        → явно подтвердить обход lifecycle

External side effect зависит от успешного save?
        → after_commit / enqueue_after_commit

Долгая работа?
        → Background Job

Периодическая работа?
        → Scheduler

Работа может быть повторена?
        → спроектировать idempotency

Несколько steps должны быть атомарны?
        → не делать промежуточный commit без причины
```

---

## 31. Design review checklist

- [ ] Определена atomic unit бизнес-операции.
- [ ] Нет случайных ручных `commit()` внутри обычного lifecycle.
- [ ] Direct DB updates имеют обоснование.
- [ ] External side effects не происходят преждевременно.
- [ ] Рассмотрены `after_commit` / `enqueue_after_commit`.
- [ ] Background jobs имеют idempotency strategy.
- [ ] Дубликаты jobs рассмотрены.
- [ ] Queue/timeout соответствуют workload.
- [ ] Scheduler используется для site-periodic work, а не как универсальный event poller.
- [ ] Permission context background operation определён.
- [ ] File/external-system side effects учитывают rollback boundary.
