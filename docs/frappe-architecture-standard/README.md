# Frappe Architecture Standard

Универсальный стандарт проектирования приложений на **Frappe Framework 16**.

Этот материал не описывает архитектуру конкретного продукта и не является частью предметной модели VEQTA. Репозиторий используется только как место хранения документации.

## Зачем нужен этот стандарт

Frappe уже задаёт собственную модель приложения: metadata, DocType, Document lifecycle, permissions, REST API, jobs, scheduler, hooks, Desk, migrations и другие подсистемы. Поэтому архитектурное решение на Frappe нельзя оценивать только по общим привычкам из Django, Java, Clean Architecture или DDD.

Основной вопрос design review:

> **Какую ответственность Frappe уже взял на себя, как Framework предлагает её расширять и какую новую ответственность действительно добавляет наше решение?**

Стандарт нужен, чтобы отвечать на этот вопрос одинаково в любом Frappe-приложении.

## Что здесь считается доказательством

Каждое нормативное правило должно быть разобрано в четырёх частях:

1. **Факт Frappe** — что Framework непосредственно предоставляет или гарантирует.
2. **Пруф** — актуальная официальная документация или versioned upstream-код.
3. **Архитектурное следствие** — какой design choice разумно следует из факта.
4. **Граница / исключение** — когда штатного механизма недостаточно или его семантика не совпадает с задачей.

Используются три маркировки:

- **[FRAPPE DOCS]** — прямо подтверждается официальной документацией.
- **[UPSTREAM]** — подтверждается исходным кодом Frappe `version-16`.
- **[ARCHITECTURAL INFERENCE]** — вывод из нескольких фактов; не выдаётся за официальную догму Frappe.

ERPNext используется только как **first-party пример реальной практики**. Наличие решения в ERPNext показывает, что оно реально применяется командой экосистемы, но само по себе не делает решение обязательным контрактом Framework.

## Иерархия источников

При конфликте формулировок используем следующий приоритет:

1. version-specific upstream source `frappe/frappe`, ветка `version-16`;
2. актуальная официальная документация Frappe Framework;
3. release notes и migration notes;
4. first-party приложения, прежде всего ERPNext;
5. community discussions — только как дополнительный контекст.

Проверка стандарта выполнена по ветке **Frappe `version-16`** и актуальному на 2 сентября 2026 года релизу **v16.33.0**.

## Базовый вывод исследования

**[FRAPPE DOCS]** Frappe прямо описывает себя как metadata-driven, full-stack, batteries-included framework. Официальная страница *Why Frappe* говорит, что философия проекта — писать как можно меньше кода и предпочитать configuration over code. Introduction также прямо говорит о monolithic architecture.

Источники:

- https://docs.frappe.io/framework/user/en/basics/why
- https://docs.frappe.io/framework/user/en/introduction
- https://github.com/frappe/frappe/blob/version-16/pyproject.toml

**[ARCHITECTURAL INFERENCE]** Из этого не следует «код плохой» или «всё надо накликать». Следует другое: если Framework уже предоставляет примитив с нужной семантикой, дублировать его собственным механизмом без причины — архитектурный долг.

## Главный Frappe-native принцип

> **Используй существующий primitive Frappe там, где его семантика совпадает с требованием. Если стандартного поведения недостаточно — используй официальный extension seam. Собственную abstraction вводи тогда, когда появляется новая ответственность, которой Framework не владеет.**

Это не цитата из документации. Это итоговый **[ARCHITECTURAL INFERENCE]**, который проверяется во всех следующих разделах.

## Почему здесь нет одной лестницы «metadata → code»

Предыдущая версия исследования пыталась построить одну универсальную последовательность:

```text
metadata → standard mechanisms → controller → hooks → custom code
```

После аудита эта схема признана слишком грубой. Data model, security, lifecycle, async, UI и integration — разные архитектурные оси. Hook не является «следующей ступенью» после Controller, а custom UI не является «более глубоким уровнем», чем background job.

Поэтому стандарт разделён на независимые decision tracks.

## Карта стандарта

1. [01_FOUNDATIONS.md](01_FOUNDATIONS.md) — философия, границы Framework / App / Site, configuration over code.
2. [02_DATA_MODEL.md](02_DATA_MODEL.md) — DocType, Field, Link, Child Table, Single, Virtual, naming, snapshot vs reference.
3. [03_DOCUMENT_LIFECYCLE.md](03_DOCUMENT_LIFECYCLE.md) — Document, Controller, Client/Server Script, status, Workflow, docstatus, services.
4. [04_SECURITY.md](04_SECURITY.md) — реальная модель permissions и безопасная эскалация.
5. [05_TRANSACTIONS_ASYNC.md](05_TRANSACTIONS_ASYNC.md) — transactions, DB API, after_commit, jobs, scheduler, idempotency.
6. [06_API_INTEGRATION.md](06_API_INTEGRATION.md) — REST API, document methods, whitelisted methods, Webhook, внешний контракт.
7. [07_EXTENSION_CUSTOMIZATION.md](07_EXTENSION_CUSTOMIZATION.md) — Custom Field, Property Setter, hooks, doc_events, extend/override, Packages.
8. [08_UI_REPORTING.md](08_UI_REPORTING.md) — Desk, views, Workspace, reports, Web Form, Portal, custom frontend.
9. [09_DEPLOYMENT_TESTING.md](09_DEPLOYMENT_TESTING.md) — JSON metadata, fixtures, patches, migrate, воспроизводимость, tests.
10. [10_DECISION_STANDARD.md](10_DECISION_STANDARD.md) — ответственность-матрица и обязательный design review.
11. [11_EXAMPLES.md](11_EXAMPLES.md) — типовые правильные и неправильные решения понятным языком.
12. [12_EVIDENCE_REGISTER.md](12_EVIDENCE_REGISTER.md) — реестр первичных источников.
13. [13_STATISTICAL_AUDIT.md](13_STATISTICAL_AUDIT.md) — количественный, корреляционный и регрессионный аудит структуры документации.

## Что стандарт запрещает, а что нет

Стандарт **не запрещает**:

- Python Controller;
- service classes;
- domain helpers;
- Query Builder и SQL там, где они оправданы;
- custom API;
- background jobs;
- custom frontend;
- integration layer;
- custom permission logic;
- Virtual DocType;
- собственные технические abstractions.

Красный флаг возникает не из-за названия конструкции, а когда она **пусто дублирует ответственность Framework**.

Например:

```text
TaskRepository.save(task):
    task.save()
```

не получает автоматического оправдания только потому, что называется Repository.

Но отдельный service, который координирует несколько DocType, расчёты и внешнюю интеграцию, вполне может быть естественным решением. В актуальном ERPNext существуют `StockLedgerService`, `TaxService`, `AssetService` и другие service-классы.

Примеры first-party кода:

- https://github.com/frappe/erpnext/blob/develop/erpnext/stock/services/stock_ledger_service.py
- https://github.com/frappe/erpnext/blob/develop/erpnext/accounts/services/taxes.py

## Обязательный вопрос перед любой собственной конструкцией

Перед добавлением ACL engine, repository, scheduler, API layer, event bus или другой abstraction нужно ответить:

```text
1. Какую конкретную ответственность она добавляет?
2. Какой Frappe primitive решает ближайшую по смыслу задачу?
3. Почему его семантика или возможности недостаточны?
4. Есть ли официальный extension seam?
5. Как решение будет устанавливаться, мигрировать, тестироваться и обновляться?
```

Если на вопрос №3 нет конкретного ответа, новая конструкция считается **необоснованной до доказательства обратного**.
