# 09. Deployment and Testing

## 1. Почему deployment — часть архитектуры

Frappe App — это не только код, который работает на dev-site.

Нормальный продукт должен воспроизводимо пройти путь:

```text
repository
    ↓
clean compatible site
    ↓
install-app / migrate
    ↓
required application state
```

Если после установки обязательная конфигурация существует только в голове разработчика, architecture incomplete.

---

## 2. Standard DocType JSON

Standard DocType metadata живёт в source tree App.

Изменение модели:

- добавление поля;
- изменение field type;
- child table;
- naming;
- is_submittable;

является source-controlled schema/model change.

### Design consequence

Любое изменение модели должно учитывать existing data и upgrade path.

---

## 3. bench migrate

Migration синхронизирует schema/metadata и выполняет migration steps/patches.

Это штатный deployment lifecycle Frappe.

Следовательно, production upgrade не должен требовать секретной последовательности ручных SQL-команд, если изменение является обязательной частью App.

---

## 4. Schema migration ≠ только создание колонок

Пример изменения:

```text
old_status → status
```

Недостаточно просто создать новое поле.

Нужно решить:

```text
как перенести существующие значения?
что делать с неизвестными values?
когда удалить old field?
как rollback/retry?
```

Это уже data migration.

---

## 5. Patches

Patches предназначены для one-off migration logic.

Хорошие примеры:

- преобразовать старые данные;
- заполнить новое обязательное поле;
- изменить historical representation;
- выполнить controlled migration между versions.

### Плохой подход

README:

```text
после обновления зайдите в SQL console
и выполните UPDATE ...
```

для обязательной migration.

---

## 6. Patch должен быть безопасен в upgrade lifecycle

Нужно учитывать:

- порядок;
- повторный запуск/частичный failure;
- transaction semantics;
- большие объёмы данных;
- compatibility со старой schema в момент выполнения.

Patch — production code, а не одноразовый черновик.

---

## 7. Fixtures

Fixtures переносят configuration records как часть App.

Подходят, если record действительно является частью продукта.

Не подходят для пользовательских transactional data.

### Review question

> Этот record описывает продукт или состояние конкретного клиента/site?

---

## 8. Exported customizations

Custom Fields/Property Setters и другие site-created configuration могут быть экспортированы для доставки с App.

Это полезно, когда изменение создавалось low-code способом, но затем стало частью product source.

Нужно внимательно понимать, что будет происходить с customization на target site.

---

## 9. Install hooks

Если App при установке должен создать/настроить специфические данные, можно использовать предусмотренные install hooks.

Но install hook не должен скрывать то, что естественнее выражается DocType JSON/fixtures.

Критерий — responsibility.

---

## 10. Reproducibility test

Обязательный архитектурный тест:

```text
1. создать чистый compatible site
2. установить App
3. выполнить migrate
4. проверить required configuration/model
```

Если приложение не получается воспроизвести без ручной памяти разработчика, deployment contract нарушен.

---

## 11. Site-specific state

Не всё обязано находиться в repository.

Нормально, что конкретный site содержит:

- пользователей;
- customer data;
- local settings;
- secrets;
- optional customization.

Нужно лишь чётко разделить:

```text
product-required state
```

и

```text
site-owned state
```

---

## 12. Secrets

Пароли, API keys и production secrets не должны попадать в fixtures/source repository только потому, что Integration Settings являются DocType.

Deployment architecture должна отделять configuration structure от secret values.

---

## 13. Dependencies

App должен явно понимать зависимости:

- Frappe major version;
- другие Apps;
- Python/Node requirements;
- external services.

Если App расширяет DocType другого App, install/dependency contract должен это отражать.

---

## 14. Version-sensitive mechanisms

Документация стандарта должна маркировать возможности, зависящие от major version.

Например:

```text
extend_doctype_class [v16+]
```

Не нужно привязывать каждую страницу к patch version, если behavior не менялся.

---

## 15. Reverse migrations

Нельзя предполагать, что downgrade автоматически безопасен.

Удаление/изменение schema может быть необратимым без отдельной migration strategy.

Перед destructive migration нужно решить recovery/backup/rollback process.

---

## 16. Destructive changes

Особенно тщательно review:

- удаление fields;
- изменение field type;
- изменение naming;
- разделение DocType;
- слияние DocTypes;
- изменение child ↔ standalone model;
- изменение Link target.

Эти изменения могут ломать existing records и references.

---

## 17. Tests — часть design contract

Тест нужен не для доказательства, что Frappe вообще умеет сохранять Document.

Тест нужен для наших собственных assumptions/contracts.

Пример:

```text
Closed Inspection cannot be edited by Operator
```

Это наш business contract — он должен быть проверяем.

---

## 18. Unit/domain tests

Хорошие кандидаты:

- validation/invariants;
- calculations;
- pure domain functions;
- service behavior;
- state transitions.

Чем меньше dependency на UI, тем проще и быстрее такой тест.

---

## 19. Document lifecycle tests

Проверять:

```text
insert
save
submit
cancel
update-after-submit
```

там, где App добавляет важную behavior.

Особенно если последствия lifecycle создают другие Documents или external events.

---

## 20. Permission tests

Security нельзя считать корректной только потому, что Administrator всё видит.

Нужно тестировать реальные роли:

```text
allowed user
denied user
owner/non-owner
user permission scopes
share
list/direct access
API
```

---

## 21. Workflow tests

Если Workflow является частью critical process, нужно проверять:

- допустимые transitions;
- запрещённые transitions;
- roles;
- conditions;
- обход через API/alternative UI.

---

## 22. API tests

Для custom domain API проверяются:

- authentication;
- authorization;
- validation;
- contract;
- idempotency;
- errors;
- transaction behavior.

Generic REST Framework не нужно тестировать целиком заново, но наши assumptions о нём — можно.

---

## 23. Background job tests

Критические jobs должны проверять:

- repeat execution;
- partial failure;
- idempotency;
- state after success;
- state after exception;
- permission/system context, если важно.

---

## 24. Migration tests

Если patch преобразует production data, это часть критического code path.

Минимум нужно проверить на representative old state:

```text
old schema/data
    ↓
patch/migrate
    ↓
expected new state
```

---

## 25. Fresh install vs upgrade

App должен работать в двух разных сценариях:

```text
fresh install
```

и

```text
upgrade existing site
```

У них разные риски.

Fresh install не доказывает корректность migration старых данных.

---

## 26. Test data

Тестовые данные должны быть минимальными и понятными.

Не нужно копировать production database для каждого unit test.

Но integration/migration testing может требовать realistic fixtures/scenarios.

---

## 27. Manual prototype ≠ deployment

На этапе исследования допустимо накликать Workflow или Custom Field вручную, чтобы проверить гипотезу.

После принятия решения нужно определить, как accepted state попадёт в source/deployment model.

Это важная граница между:

```text
experiment
```

и

```text
product architecture
```

---

## 28. Upgrade compatibility

Extension другого App должен проверяться при major upgrades.

Особенно:

- overrides;
- internal APIs;
- custom JS against Desk internals;
- monkey patches;
- direct DB schema assumptions.

Чем сильнее coupling к internal implementation, тем выше upgrade cost.

---

## 29. Public API dependency

Зависимость от documented/public Framework API обычно стабильнее зависимости от внутренней функции, которая случайно доступна для import.

Это должно учитываться при code review.

---

## 30. Deployment decision track

```text
Standard model change?
        → source DocType metadata

Нужно преобразовать existing data?
        → Patch

Configuration record — часть App?
        → Fixture/export/install setup

Изменение принадлежит только site?
        → site customization

После clean install нужно ручное действие?
        → проверить, действительно ли оно site-owned

Есть destructive schema change?
        → migration/recovery plan
```

---

## 31. Testing decision track

```text
Наш business invariant?
        → automated test

Custom permission policy?
        → permission matrix test

Critical workflow?
        → transition tests

Custom external API?
        → contract/security/idempotency tests

Data patch?
        → migration test

Background operation?
        → retry/idempotency/failure tests
```

---

## 32. Design review checklist

- [ ] Clean install воспроизводит required product state.
- [ ] Upgrade path существующих данных определён.
- [ ] Schema changes не полагаются на ручной SQL.
- [ ] Required configuration доставляется штатным механизмом.
- [ ] Site-specific data не случайно попали в fixtures.
- [ ] Secrets не хранятся в repository.
- [ ] Dependencies объявлены.
- [ ] Destructive migrations имеют recovery plan.
- [ ] Critical domain logic покрыта тестами.
- [ ] Permissions тестируются не под Administrator.
- [ ] Critical Workflow проверяется через альтернативные paths.
- [ ] Migration patches тестируются на old-state scenario.
- [ ] Fresh install и upgrade рассматриваются отдельно.
