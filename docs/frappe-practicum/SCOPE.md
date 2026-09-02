# Границы практикума

## Цель

Научить новичка проектировать, собирать, расширять и переносить небольшие приложения на
Frappe Framework, используя минимальный механизм, чья семантика совпадает с задачей.

Базовая привычка курса:

```text
сначала смысл и требуемая гарантия
→ затем владелец ответственности
→ затем штатный primitive / extension point Frappe
→ затем правильная lifecycle phase
→ затем проверка реального enforcement layer
```

## Версия и источник истины

Основная версия — **Frappe Framework v16.32.0**.

При конфликте сведений:

1. фактическое поведение на стенде `v16.32.0`;
2. exact source tag `v16.32.0`;
3. официальная документация;
4. moving `version-16` только как информация для будущего обновления курса.

Moving branch не доказывает поведение закреплённой версии.

---

# 1. Два уровня

## Уровень A — Metadata & Configuration

P1–P3 выполняются без собственной Python/JavaScript business logic.

Практически применяются:

- Bench, site, app, Module, Developer Mode;
- Standard DocType и стандартные Field Types;
- naming, Link, Child Table, Tree, submittable document;
- Role Permission, Permission Level, If Owner, User Permission, Share;
- Workflow / Workflow State / Workflow Action;
- Assign To / ToDo / Timeline;
- Form, List, Kanban, Calendar, Report Builder, Workspace;
- Number Card, Dashboard Chart;
- Data Import / Export там, где они нужны продукту;
- Notification;
- Print Format / PDF;
- Web Form, Website User, Guest;
- built-in Document REST API;
- Standard metadata, fixtures, `migrate`, `install-app`;
- Git и clean-site acceptance.

`hooks.py` для fixtures/Apps Page здесь считается конфигурацией app, а не собственной
business logic.

## Уровень B — Engineering Bridge

После принятого P3 разрешён минимальный Python, потому что появляется ответственность,
которую metadata уже не выражает.

Практически применяются:

- собственный DocType Controller;
- `before_insert` как creation-only server invariant;
- различие `before_insert` и общего `validate` по lifecycle semantics;
- permission-aware `Document` API;
- `@frappe.whitelist(methods=["POST"])` на Document method;
- REST API v2 для semantic document method;
- request transaction и rollback;
- отсутствие manual `frappe.db.commit()` в обычной команде;
- schema evolution через Standard metadata;
- `patches.txt`, post-model-sync patch, `bench migrate`;
- deliberate direct DB update внутри one-off data migration;
- `IntegrationTestCase` и `bench run-tests` на отдельном test site;
- `enqueue_after_commit`, Background Jobs и Webhook как decision boundary.

Background Job не добавляется в `service_intake`, пока в продукте нет реальной долгой
или внешней операции. Курс учит и применять механизм, и не применять его без задачи.

---

# 2. Что не делаем автоматически

Даже на Engineering level не вводятся по умолчанию:

- Repository, дублирующий `frappe.get_doc` / `doc.save()`;
- Service class без самостоятельной ответственности;
- собственный transaction manager;
- собственная queue/daemon;
- duplicate CRUD API;
- raw SQL для обычного business CRUD;
- `ignore_permissions=True` как shortcut;
- Client Script как единственная server/business гарантия;
- слишком широкий lifecycle hook, если правило относится только к insert/submit/cancel;
- core patch/fork;
- custom frontend без отдельной UX-причины.

Service/domain module, custom API, Background Job, hooks или custom frontend могут быть
полностью Frappe-native, когда появляется соответствующая ответственность.

---

# 3. Предметные границы проектов

## P1 — `equipment_register`

```text
Equipment Location (Tree)
Equipment Category
Equipment
Equipment Identifier (Child)
```

Это реестр текущего состояния. В нём нет заявок, согласований, ремонтов и event ledger.

`status` остаётся обычным Select: процесс согласования отсутствует, поэтому Workflow не
нужен.

## P2 — `purchase_requests`

```text
Purchase Department
Purchase Request
Purchase Request Item (Child)
```

`Purchase Request` — submittable document с Workflow. Проект не заменяет ERP purchasing:
нет Supplier, Purchase Order, warehouse/accounting/payment logic.

## P3 — `service_intake`

```text
Service Intake   ← внешний недоверенный ввод
Service Case     ← внутренний рабочий документ
Service Category
```

Web Form не создаёт внутренний Case напрямую. P3 заканчивается ручной конвертацией после
триажа — это сознательная граница metadata/configuration уровня.

## Engineering Bridge

Тот же `service_intake` получает новое требование:

```text
Accepted Intake
→ permission-aware semantic command
→ exactly one Case
→ converted_at
→ one request transaction
```

Creation rule принадлежит `ServiceCase.before_insert`: Agent после создания Case не
должен получать Read на Intake только ради последующих save.

Здесь код появляется не ради «продвинутого уровня», а потому что metadata уже не
выражает cross-document creation invariant и атомарное business action.

---

# 4. Ownership основных механизмов

| Ответственность | Владелец в курсе |
|---|---|
| структура Document | DocType metadata |
| ссылка на самостоятельный объект | Link |
| зависимые строки без своего lifecycle | Child Table |
| hierarchy | Tree DocType |
| простое значение состояния | Select |
| допустимые process transitions | Workflow |
| transaction finality | docstatus / submit-cancel, когда семантика подходит |
| базовый доступ к DocType | Role/DocPerm |
| доступ к полям | Permission Level |
| ограничение по linked values | User Permission |
| ad-hoc document grant | Share |
| конкретный исполнитель | Assign To / ToDo |
| внешний простой intake | Web Form |
| generic CRUD integration | built-in REST |
| creation invariant собственного Document | Controller `before_insert` |
| invariant каждого save | Controller `validate`, только когда семантика действительно такая |
| предметное действие одного Document | whitelisted Document method |
| request atomicity | Framework transaction boundary |
| эволюция существующих данных | patch |
| собственное поведение app | integration tests |
| тяжёлая post-commit работа | Background Job, только при реальной необходимости |
| простой outbound HTTP event | Webhook сначала |

---

# 5. Поставка app и проверочные site

Различаются четыре слоя:

| Слой | Примеры | Способ |
|---|---|---|
| Standard source | DocType, controller, Workspace, standard Report, Web Form, Notification | app source |
| переносимая конфигурация | Role, Workflow, общие view-records | fixtures/штатный export |
| local site configuration | Users, User Permission, Assignment Rule с Users, SMTP, API keys | site only |
| working data | Equipment, Requests, Intake, Case, Files | database/site |

Для DocType, принадлежащих учебному app, permissions задаются в Standard DocType JSON.
Export Customizations не используется как второй permission layer для своих DocType.

Engineering Bridge разделяет три эксплуатационные проверки:

```text
intake.localhost
→ upgrade existing working data

intake-test.localhost
→ automated integration tests

intake-engineering-clean.localhost
→ fresh install without historical working data
```

Рабочий site не используется как test database.

Schema JSON отвечает за структуру, patch — за одноразовую миграцию существующих данных.

---

# 6. Обязательные security boundaries

1. Assignment = responsibility, не authorization.
2. Workflow = transition policy, не замена Role Permission.
3. Read Only / Only Allow Edit For = UI/process guards, не универсальная ACL.
4. Permission Level ограничивает fields, не rows.
5. User Permission сужает linked values, но не выдаёт базовый DocType access.
6. Web Form — отдельный access path; в `v16.32.0` new target insert использует `ignore_permissions=True`.
7. Public Web Form не принимает internal state, assignee, internal notes и закрытые catalogs.
8. API user получает отдельную минимальную роль; secrets не попадают в Git.
9. `case.insert()` в semantic command остаётся permission-aware; custom command не получает `ignore_permissions=True`.
10. Uncaught exception в write request должна приводить к rollback; manual commit не дробит business operation.
11. Agent не получает Read на Intake только для обслуживания слишком широкого controller hook.

---

# 7. Что остаётся после практикума

Следующий отдельный уровень, не маскируемый под базовый курс:

- Client Script и полноценный Form UX scripting;
- Server Script как site/runtime customization;
- `doc_events`, `extend_doctype_class`, override mechanics для чужих DocType;
- complex service/domain modules;
- custom permission hooks и Permission Types;
- Query / Script Reports;
- Virtual DocType;
- Realtime;
- сложная внешняя интеграция и custom protocol/API versioning;
- production deployment, TLS, backup, monitoring/observability;
- performance engineering и масштабирование.

Эти механизмы не считаются «менее нативными». Они требуют отдельной задачи и контекста.

---

# 8. Критерий завершения

После P3 ученик должен уметь построить небольшой metadata-driven Frappe app без
искусственных сущностей и обходов Framework.

После Engineering Bridge он дополнительно должен уметь ответить:

```text
почему metadata перестало хватать?
какой lifecycle/extension point владеет новой гарантией?
почему выбрана именно эта lifecycle phase?
где проходит transaction boundary?
как существующий site получает новую модель данных?
почему tests выполняются на отдельном site?
что именно должно быть покрыто tests?
```

Если ответ сводится к «так принято писать код», инженерный уровень не принят.
