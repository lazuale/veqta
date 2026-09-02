# Дорожная карта

Практикум идёт последовательно. Следующий этап начинается после приёмки предыдущего.

```text
Platform
→ P1 Data Model
→ P2 Lifecycle
→ P3 Trust Boundary
→ Engineering Bridge
→ Final Architecture Audit
```

P1–P3 образуют законченный metadata/configuration уровень. Engineering Bridge — второй
уровень того же курса, а не четвёртый независимый продукт.

---

# Этап 0. Подготовить платформу

Результат:

- Frappe `v16.32.0` установлен;
- Python/Node соответствуют exact tag;
- Bench запускается;
- site создаётся и Desk открывается;
- ученик различает Bench, site, app, Module, DocType и Document.

Маршрут:

1. [SETUP_WSL2.md](SETUP_WSL2.md)
2. [FOUNDATIONS.md](FOUNDATIONS.md)

Контроль:

```bash
bench version
python --version
node --version
```

---

# Этап 1. P1 — Реестр оборудования

Маршрут: [projects/01-equipment-register/LABS.md](projects/01-equipment-register/LABS.md).

## P1.1. Контейнер продукта

- `equipment_register`;
- `equipment.localhost`;
- Developer Mode;
- Module;
- Git/source layout.

## P1.2. Модель

```text
Equipment Location → Tree
Equipment Category → independent DocType
Equipment Identifier → Child Table
Equipment → main Document
```

Проверяются naming, Set Only Once, Mandatory, Link и source permissions.

## P1.3. Working data

- ручные Documents;
- Data Import / Export;
- negative mandatory/naming/Link checks;
- global search по child identifier.

## P1.4. Permissions

- Operator / Manager / Viewer;
- Read/Write/Create/Delete отдельными Users;
- временные If Owner, User Permission, Share;
- возврат к final DocPerm.

## P1.5. Рабочее место

- List;
- Kanban по обычному `status`;
- Timeline/Track Changes;
- Report Builder;
- Number Card;
- Workspace.

Ключевой вывод:

```text
status field существует
≠ Workflow нужен автоматически
```

## P1.6. Поставка

- Standard metadata;
- fixtures только для portable records;
- Git commit;
- `equipment-clean.localhost`;
- acceptance без копирования Equipment data.

**Gate P1:** модель естественна для реестра, а app воспроизводится на clean site.

---

# Этап 2. P2 — Заявки на закупку

Маршрут: [projects/02-purchase-requests/LABS.md](projects/02-purchase-requests/LABS.md).

## P2.1. Новый app/site

- `purchase_requests`;
- `purchase.localhost`;
- без зависимости от P1 app.

## P2.2. Транзакционная модель

```text
Purchase Department
Purchase Request Item (Child)
Purchase Request (Submittable)
```

Создаются роли, Permission Levels и базовый DocPerm.

## P2.3. Document lifecycle до Workflow

Практически пройти:

```text
Save → Submit → Cancel → Amend
```

и записать `docstatus`.

Цель — сначала понять нативный Document lifecycle, затем добавлять Workflow.

## P2.4. Users и access

- Requester / Approver / Procurement / Auditor;
- If Owner;
- User Permission по Department;
- Permission Level;
- Assignment ещё не участвует в authorization.

## P2.5. Workflow

```text
Draft
→ Pending Department Approval
→ Procurement Review
→ Approved / docstatus 1
→ Cancelled / docstatus 2
```

Отдельно проверить Reject/Resubmit и невозможность чужих Workflow Action.

Ключевой вывод:

```text
Role Permission
Workflow
DocStatus
Assignment
```

решают разные задачи.

## P2.6. Collaboration/presentation

- Assign To / ToDo;
- Timeline;
- System Notification;
- Calendar;
- Report / Card / Chart / Workspace;
- Print Format / PDF.

## P2.7. Поставка

- portable Workflow/configuration;
- local Users/User Permission/Assignment Rule не экспортируются;
- `purchase-clean.localhost`;
- полный Workflow повторяется новыми Users.

**Gate P2:** lifecycle и state machine воспроизводятся без ручного восстановления
configuration на clean site.

---

# Этап 3. P3 — Внешняя приёмная

Маршрут: [projects/03-service-intake/LABS.md](projects/03-service-intake/LABS.md).

## P3.1. App/site/roles

- `service_intake`;
- `intake.localhost`;
- Triage / Agent / Manager / API Reader.

## P3.2. Trust model

```text
Service Intake → untrusted external input
Service Case   → internal work
Service Category
```

Проверяются public/internal fields и Permission Level.

## P3.3. Internal Workflow

```text
Open → In Progress → Resolved → Closed
```

Все states `docstatus = 0`; Resolution требуется перед Resolve.

## P3.4. Web Form

- Guest create;
- Website User comparison;
- no list/edit/delete;
- no internal fields;
- no direct `Service Case` creation.

Ключевой вывод:

```text
Web Form access path
≠ Desk permission path
```

## P3.5. Manual triage

- Accepted Intake;
- ручное создание Case только после проверки;
- Unique / Set Only Once source link;
- Assign To;
- Workflow;
- separate Intake/Case reporting.

Ручная конвертация здесь не недостаток курса. Это специально достигнутая граница:
metadata уже не выражает следующую атомарную business operation.

## P3.6. Built-in REST

- отдельный API User;
- allowed Read `Service Category`;
- denied Read `Service Intake`;
- secrets outside Git.

## P3.7. Поставка

- Standard Web Form source;
- portable Workflow/roles;
- no Users/keys/working data;
- `intake-clean.localhost`;
- Guest submission + internal triage повторяются.

**Gate P3:** metadata/configuration уровень курса завершён. Следующий шаг —
[Engineering Bridge](engineering/LABS.md).

---

# Этап 4. Engineering Bridge

Маршрут: [engineering/LABS.md](engineering/LABS.md).

Используется тот же `service_intake`, потому что именно он дошёл до естественной границы
configuration-only решения.

## E1. Creation invariant в Controller

Новое правило:

```text
при создании Service Case
source_intake must reference Accepted Service Intake
```

Metadata продолжает владеть Link/Unique/Set Only Once. Controller `before_insert`
добавляет только creation-time cross-document state invariant.

Проверка обязательно включает Agent-save существующего Case без Read на Intake. Так
доказывается, что правило не повешено на слишком широкий `validate()`.

## E2. Schema evolution

В `Service Intake` появляется Standard field:

```text
converted_at
```

Он принадлежит source-модели app, а не site customization.

## E3. Semantic Document command

`ServiceIntake.create_case`:

```text
check Intake write
→ require Accepted
→ reject duplicate conversion
→ permission-aware Case insert
→ set converted_at
→ add Timeline comment
```

Команда whitelisted только для POST.

Ключевой вывод:

```text
business command
≠ duplicate CRUD endpoint
```

## E4. REST document method

Через exact v16 API v2 route выполняется whitelisted method конкретного Intake.

Проверяются success, duplicate rejection, state rejection, permissions и secret hygiene.

## E5. Transaction rollback

Временный controlled failure после `case.insert()` доказывает:

```text
uncaught request exception
→ no partial Case
→ no converted_at
```

Probe удаляется до commit. Manual `frappe.db.commit()` в business command отсутствует.

## E6. Patch/migrate

Новая схема сама не backfill-ит старые data.

```text
post_model_sync patch
→ existing P3 Intake gets converted_at from old Case
```

Patch повторно через migrate не выполняется как новый.

## E7. Integration tests

Создаётся отдельный:

```text
intake-test.localhost
```

На нём тестируется собственное поведение app:

- non-Accepted source rejected on insert;
- accepted conversion works;
- duplicate conversion rejected;
- converted_at written;
- Agent сохраняет существующий Case без Read на Intake.

Рабочий `intake.localhost` не используется как test database.

## E8. Async/integration decision lab

Разобрать границы:

```text
Webhook
Background Job + enqueue_after_commit
Controller lifecycle
integration module/service
```

В exact v16.32 обычный Webhook для DocType event сам проходит через after-commit flush и
background queue. Custom Job вокруг него только ради «асинхронности» не нужен.

Custom Job в app не добавлять, потому что текущая модель не имеет реальной долгой
операции.

## E9. Deployment acceptance

Проверяются три разных сценария:

```text
upgrade intake.localhost

automated tests intake-test.localhost

clean install intake-engineering-clean.localhost
```

**Gate Engineering:** code находится в нативных extension points и правильных lifecycle
phases, migration проходит, tests зелёные, искусственных abstractions/jobs нет.

---

# Финальный аудит

После полного курса ученик без подсказки объясняет:

1. где Framework заканчивается и начинается ответственность app;
2. почему DocType — Document model, а не просто таблица;
3. когда нужны Link, Child Table, Tree, Select и submittable document;
4. чем Role Permission отличается от Permission Level, User Permission и Share;
5. почему Assignment не authorization;
6. почему Workflow не заменяет permissions и docstatus;
7. почему Web Form — отдельный trust/access path;
8. когда invariant должен перейти в Controller и как выбрать lifecycle phase;
9. почему semantic command не дублирует CRUD REST;
10. где проходит transaction boundary и почему manual commit опасен;
11. чем schema migration отличается от data patch;
12. что должны тестировать tests приложения и почему им нужен отдельный site;
13. когда Background Job/Webhook действительно оправданы;
14. как отдельно доказать upgrade и clean install.

Финальная работа принимается, когда три app имеют воспроизводимые Git-состояния, а
`service_intake` дополнительно проходит Engineering acceptance.
