# 05. Transactions, Background Jobs и Scheduler

## 1. Транзакции — часть архитектуры Frappe

Предыдущая версия стандарта почти не учитывала transactions. Для production-приложения это критический пробел.

**[FRAPPE DOCS]** Database API описывает transaction model Frappe:

- успешный write web request commit'ится в конце;
- uncaught exception вызывает rollback;
- background/scheduled job commit'ится после успеха;
- uncaught exception в job вызывает rollback;
- patches также выполняются в transaction model.

Источник:

- https://docs.frappe.io/framework/user/en/api/database

Главный вывод для новичка:

> Обычно не нужно вручную управлять commit для каждой операции. Framework уже определяет границу транзакции.

---

## 2. Почему ручной `frappe.db.commit()` — red flag

Если обычная business operation выполняется внутри request:

```text
создать документ A
обновить документ B
создать документ C
```

Framework способен закоммитить изменения вместе после успешного завершения.

Если разработчик делает commit посередине:

```text
создали A
COMMIT
обновили B
ошибка при C
```

rollback уже не сможет вернуть A.

**[ARCHITECTURAL INFERENCE]** Поэтому manual commit внутри обычной application flow требует конкретного обоснования.

Это не абсолютный запрет: существуют migration, tooling или специальные long-running сценарии. Но «на всякий случай закоммитим» — неправильный мотив.

---

## 3. Исключение, которое поймали сами — отвечаем за rollback

**[FRAPPE DOCS]** Документация Database API отдельно предупреждает: если код сам ловит exception, database abstraction уже не знает, что операция должна считаться failed; разработчик отвечает за корректное transaction behaviour.

Источник:

- https://docs.frappe.io/framework/user/en/api/database

Пример риска:

```python
try:
    dangerous_operation()
except Exception:
    frappe.log_error()
    return "ok"
```

Если `dangerous_operation()` частично изменила DB, а exception проглочен, стандартный rollback path может не сработать так, как ожидает разработчик.

---

## 4. Direct DB update обходит часть Document lifecycle

**[FRAPPE DOCS]** `frappe.db.set_value()` обновляет database value и не вызывает ORM triggers вроде `validate` и `on_update`.

Источник:

- https://docs.frappe.io/framework/user/en/api/database

Поэтому:

```text
Document API
    → обычная business mutation,
      где нужны validation/lifecycle

Direct DB API
    → намеренный обход lifecycle
```

### Типовая ошибка

Использовать `db_set`/`set_value` вместо `save()` просто потому, что так короче или быстрее.

Если бизнес-инварианты находятся в Controller, такой update может их обойти.

---

## 5. Когда direct DB access нормален

Он может быть оправдан, если:

- обновляется техническое/derived поле;
- migration намеренно обходит lifecycle;
- bulk operation требует другого performance profile;
- разработчик сознательно управляет последствиями;
- нужно выполнить служебное internal update.

Ключевое слово — **намеренно**.

---

## 6. External side effects и commit

Один из самых опасных классов ошибок:

```text
1. сохранить Frappe Document
2. отправить данные во внешнюю систему
3. позже в request возникает exception
4. Frappe делает rollback
```

Получается:

```text
внешняя система считает операцию выполненной
Frappe считает, что операции не было
```

Frappe предоставляет transaction callbacks и `enqueue_after_commit`.

Источники:

- https://docs.frappe.io/framework/user/en/api/database
- https://docs.frappe.io/framework/user/en/api/background_jobs
- https://github.com/frappe/frappe/blob/version-16/frappe/utils/background_jobs.py

**[ARCHITECTURAL INFERENCE]** Side effect, который должен происходить только после успешной фиксации данных, нужно привязывать к successful commit path.

---

## 7. `after_commit`

Database API предоставляет callbacks:

```text
before_commit
after_commit
before_rollback
after_rollback
```

Источник:

- https://docs.frappe.io/framework/user/en/api/database

Это полезно, когда работа с внешним ресурсом должна соответствовать результату DB transaction.

Но callback не отменяет необходимости думать об idempotency: процесс может упасть после внешнего side effect, network response может потеряться и т.д.

---

## 8. Background Jobs — штатная инфраструктура

**[FRAPPE DOCS]** Frappe поставляется с background job system и `frappe.enqueue`.

Источник:

- https://docs.frappe.io/framework/user/en/api/background_jobs

**[UPSTREAM]** В `version-16` implementation есть:

- queues;
- timeout;
- `enqueue_after_commit`;
- success/failure callbacks;
- job id;
- deduplication;
- transaction commit/rollback worker path.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/utils/background_jobs.py

### Когда Job — естественный выбор

```text
долгий расчёт;
массовая обработка;
внешняя интеграция, которую не нужно держать в HTTP request;
работа, которая может выполняться асинхронно.
```

---

## 9. Job не означает «можно забыть о надёжности»

Перед enqueue нужно ответить:

```text
1. Можно ли безопасно выполнить job повторно?
2. Что будет, если worker упадёт посередине?
3. Нужен ли job_id/deduplicate?
4. Должна ли задача запускаться только после commit?
5. Как пользователь узнает результат?
6. Как обрабатывается failure?
7. Какой timeout действительно нужен?
```

### Idempotency

На бытовом языке:

> Если одну и ту же кнопку случайно нажали дважды или job запустился повторно, система не должна создать двойную оплату, двойную накладную или повторный внешний запрос без контроля.

---

## 10. `enqueue_after_commit`

**[FRAPPE DOCS + UPSTREAM]** `frappe.enqueue` поддерживает `enqueue_after_commit=True`.

Источники:

- https://docs.frappe.io/framework/user/en/api/background_jobs
- https://github.com/frappe/frappe/blob/version-16/frappe/utils/background_jobs.py

Это важно для сценария:

```text
создали документ
    ↓
после успешного commit
    ↓
запустили тяжёлую обработку этого документа
```

Иначе worker теоретически может начать работать с состоянием, которое ещё не зафиксировано или позже будет откатано.

---

## 11. Scheduler Events

**[FRAPPE DOCS]** Периодические задачи подключаются через `scheduler_events` hook.

Источник:

- https://docs.frappe.io/framework/user/en/api/background_jobs

Пример:

```text
каждый час проверить просроченные записи
каждую ночь пересчитать агрегаты
раз в неделю выполнить cleanup
```

Для site-level application jobs Scheduler — native default.

---

## 12. Когда внешний scheduler нормален

Внешний cron/enterprise orchestrator не является автоматически костылём.

Он может быть правильным, если процесс:

- управляет несколькими независимыми системами;
- является инфраструктурным;
- должен существовать даже без доступного Frappe site;
- централизованно управляется отдельной orchestration platform.

**[ARCHITECTURAL INFERENCE]** Red flag — не внешний scheduler сам по себе, а параллельный scheduler без отдельной ответственности.

---

## 13. Notification — штатный механизм пользовательских уведомлений

Frappe имеет Notification subsystem для событий Documents, условий и date-based notification.

Источник:

- https://docs.frappe.io/framework/notifications

Подходящий сценарий:

```text
за 3 дня до срока отправить уведомление ответственному
после изменения status уведомить руководителя
```

### Не превращать Notification в integration event bus

Notification не нужно автоматически использовать для:

```text
guaranteed domain event delivery;
exactly-once external processing;
сложных retries;
external event store.
```

Если требуется надёжная integration orchestration, это другая ответственность.

---

## 14. Assignment / ToDo

Frappe имеет встроенный assignment mechanism через Assign To / ToDo.

Источник:

- https://docs.frappe.io/framework/assignments-and-todos

Он подходит, когда смысл требования:

> назначить пользователю работу по конкретному Document.

Но это не означает, что любое domain field `account_manager`, `owner_employee` или `responsible_department` нужно заменить Assignment.

**[ARCHITECTURAL INFERENCE]** Отличаем operational assignment от устойчивого business property.

---

## 15. Типовой неправильный сценарий

Задача:

> После submit документа отправить его в API, построить PDF и обновить 20 000 строк.

Плохой вариант:

```text
on_submit
  ├─ HTTP API call
  ├─ PDF generation
  └─ цикл 20 000 updates
```

всё синхронно в request.

Риски:

- большой response time;
- timeout;
- длинные locks;
- внешний API уже принял данные, а transaction затем откатилась;
- пользователь не понимает, завершилась ли операция.

Более устойчивый вариант:

```text
submit transaction
      ↓
commit
      ↓
enqueue_after_commit
      ↓
background orchestration
```

Конкретная реализация зависит от требований к надёжности.

---

## 16. Transaction/async design review

```text
1. Где начинается и заканчивается transaction?
2. Есть ли manual commit/rollback? Зачем?
3. Есть ли direct DB writes, обходящие Document lifecycle?
4. Есть ли external side effects до commit?
5. Нужен ли after_commit/enqueue_after_commit?
6. Должна ли операция быть background job?
7. Идемпотентна ли job?
8. Как обрабатываются retry/failure?
9. Нужен ли deduplication?
10. Scheduler — site-level responsibility или внешняя orchestration?
```

Без ответов на эти вопросы сложную business operation нельзя считать архитектурно завершённой.
