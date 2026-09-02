# 12. Evidence Register — первичные источники и статус доказательств

Этот файл нужен, чтобы архитектурный стандарт не превращался в набор мнений.

Для каждого класса решений здесь зафиксирован источник, тип доказательства и то, **что именно** из него допустимо выводить.

---

## 1. Philosophy / configuration over code

### Источник

https://docs.frappe.io/framework/user/en/basics/why

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- Frappe built to power ERPNext;
- philosophy: write as less code as possible;
- preference for configuration over code;
- generic capabilities помещаются во Framework;
- batteries included;
- extensible architecture through Apps.

### Что НЕ подтверждает

- запрет Python;
- запрет service layers;
- обязательную low-code разработку любого приложения.

---

## 2. Metadata-driven / monolithic architecture

### Источник

https://docs.frappe.io/framework/user/en/introduction

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- metadata treated as data;
- full-stack/batteries-included model;
- explicit belief in monolithic architecture;
- Desk supplies forms, lists, permissions, files and navigation.

### Архитектурное следствие

**[ARCHITECTURAL INFERENCE]** Не дублировать integrated application concerns только ради привычного шаблона другого framework.

---

## 3. Framework package description v16

### Источник

https://github.com/frappe/frappe/blob/version-16/pyproject.toml

### Тип

**[UPSTREAM]**

### Что подтверждает

Project description: metadata driven, full-stack low code web framework.

Также фиксирует version-specific Python dependency range ветки v16.

---

## 4. Current v16 release baseline

### Источник

https://github.com/frappe/frappe/releases/tag/v16.33.0

### Тип

**[UPSTREAM RELEASE]**

### Что подтверждает

Проверенная точка актуальности стандарта: v16.33.0, 1 сентября 2026 года.

Стандарт не должен хардкодить этот номер как вечную «последнюю версию»; он только фиксирует baseline проверки.

---

## 5. DocType as core building block

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- DocType — core building block;
- metadata описывает model/view;
- обычные DocTypes связаны с database schema.

### Что НЕ подтверждает

- «каждое существительное бизнеса обязано быть DocType».

Выбор DocType vs Field/Child — design inference.

---

## 6. Field types / Link / Dynamic Link / Table MultiSelect

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Назначение standard field primitives.

### Архитектурное следствие

Сначала выбирать primitive с соответствующей семантикой, а не создавать отдельный DocType автоматически.

---

## 7. Child DocType

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- Child attached to parent;
- parent/parenttype/parentfield/idx semantics.

### Что НЕ подтверждает

Любая one-to-many relation обязана быть Child Table.

Отдельный business record может требовать обычный DocType.

---

## 8. Single DocType

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Single предназначен для singleton-like settings data.

---

## 9. Virtual DocType

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

External/non-standard storage может быть представлен через Document abstraction.

### Что НЕ подтверждает

Каждая интеграция с внешним API должна быть Virtual DocType.

---

## 10. Naming

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/naming

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

`name` и standard naming strategies являются частью DocType model.

### Архитектурное следствие

Identity нужно выбирать до накопления production references.

---

## 11. Document Controller / lifecycle

### Источники

- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py

### Тип

**[FRAPPE DOCS] + [UPSTREAM]**

### Что подтверждает

- Controllers inherit Document;
- lifecycle hooks;
- save/insert execute permission/validation/lifecycle paths.

### Архитектурное следствие

Critical invariant должен жить в server-side path, а не только в UI.

---

## 12. Client Script limitation

### Источник

https://docs.frappe.io/framework/user/en/desk/scripting/client-script

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Client Script applies in browser/standard form context; его validation не является универсальной server-side guarantee.

---

## 13. Server Script

### Источник

https://docs.frappe.io/framework/user/en/desk/scripting/server-script

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- Server Script supports Document Event/API;
- disabled by default on shared benches starting v15;
- public shared Frappe Cloud benches do not allow it.

### Архитектурное следствие

Server Script не является обязательной ступенью перед Python App code.

---

## 14. DocStatus

### Источник

https://docs.frappe.io/framework/doctypes/docstatus

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

`Draft / Submitted / Cancelled` системная transaction semantics.

### Что НЕ подтверждает

Business status должен совпадать с docstatus.

---

## 15. Workflow

### Источник

https://docs.frappe.io/erpnext/user/manual/en/workflows

### Тип

**[FIRST-PARTY DOCS]**

### Что подтверждает

Workflow states/transitions/roles/conditions и approval semantics.

### Примечание

Workflow является framework/ERPNext ecosystem mechanism; путь документации может находиться в ERPNext manual, но сам механизм является частью Frappe stack.

---

## 16. Permissions overview

### Источник

https://docs.frappe.io/framework/user/en/basics/users-and-permissions

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Role, DocType Permissions, If Owner, Permission Level, User Permissions и другие базовые механизмы.

---

## 17. Permissions runtime

### Источник

https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py

### Тип

**[UPSTREAM]**

### Что подтверждает

- role permission evaluation;
- owner handling;
- User Permission evaluation;
- sharing path;
- controller permission checks;
- explicit comment: controller permissions can deny but cannot grant missing base permission.

### Важно

Наш design escalation не должен выдаваться за буквальный runtime order.

---

## 18. Permission query conditions

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- `permission_query_conditions` modifies list query;
- applies to `frappe.db.get_list`;
- not to `frappe.db.get_all`;
- `has_permission` is a custom document permission hook.

### Архитектурное следствие

Custom row security должна учитывать и list/query, и direct Document access.

---

## 19. Permission-aware query and field security

### Источник

https://docs.frappe.io/framework/get_query

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Permission-aware query includes user permissions, sharing, owner constraints, permission query conditions и field-level security.

---

## 20. Database transaction model

### Источник

https://docs.frappe.io/framework/user/en/api/database

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- implicit commit/rollback rules;
- background/scheduled jobs transactions;
- patches transaction model;
- direct DB APIs;
- `set_value` bypasses ORM triggers;
- transaction callbacks.

### Архитектурное следствие

Manual commit и direct DB lifecycle bypass должны быть осознанными исключениями.

---

## 21. Background jobs

### Источники

- https://docs.frappe.io/framework/user/en/api/background_jobs
- https://github.com/frappe/frappe/blob/version-16/frappe/utils/background_jobs.py

### Тип

**[FRAPPE DOCS] + [UPSTREAM]**

### Что подтверждает

Queues, `frappe.enqueue`, scheduler events, `enqueue_after_commit`, callbacks, job IDs/deduplication в v16 implementation.

---

## 22. REST API

### Источники

- https://docs.frappe.io/framework/user/en/api/rest
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api
- https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

### Тип

**[FRAPPE DOCS] + [UPSTREAM]**

### Что подтверждает

- generic DocType resource API;
- create/read/update/delete;
- document methods;
- permission-aware read/update paths.

### Что НЕ подтверждает

Любой внешний product API обязан использовать generic Document resource contract.

---

## 23. Internal REST implementation warning

### Источник

https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

### Тип

**[UPSTREAM]**

### Что подтверждает

Функции internal route implementation не должны считаться стабильным Python API для application code.

---

## 24. Webhooks

### Источник

https://docs.frappe.io/framework/user/en/guides/integration/webhooks

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Document Event + condition → HTTP callback, включая optional HMAC signature.

### Что НЕ подтверждает

Webhook является guaranteed exactly-once event bus.

---

## 25. Hooks / extension points

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Hooks существуют для extension/override; включают `doc_events`, `extend_doctype_class`, `override_doctype_class`, scheduler events, fixtures, permission hooks и другие seams.

---

## 26. `extend_doctype_class` v16+

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks#extend-doctype-class

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

В v16 extension class рекомендуется для добавления behaviour вместо полного override там, где extension достаточен.

---

## 27. App structure

### Источники

- https://docs.frappe.io/framework/user/en/basics/apps
- https://docs.frappe.io/framework/user/en/tutorial/create-an-app

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Python package, hooks.py, modules.txt, patches.txt, templates/public/source structure.

---

## 28. Packages

### Источник

https://docs.frappe.io/framework/user/en/guides/deployment/packages

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Packages are lightweight app-like bundles for custom Module Defs, available since v14.

---

## 29. Fixtures

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks#fixtures

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Database records can be exported/synced through fixtures.

### Архитектурное следствие

Use for app-owned configuration, not ordinary transactional data.

---

## 30. Export customizations

### Источник

https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

- Custom Fields/Property Setters can be exported;
- synced on update/migrate;
- warning about replacing Property Setters and Custom Permissions.

---

## 31. Migrations and patches

### Источники

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations
- https://docs.frappe.io/framework/user/en/bench/reference/migrate

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

DocType JSON schema sync, patches, fixtures and migrate lifecycle; reverse schema migrations unsupported.

---

## 32. Testing

### Источники

- https://docs.frappe.io/framework/user/en/testing
- https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing

### Тип

**[FRAPPE DOCS]**

### Что подтверждает

Frappe test runner, `FrappeTestCase`, test sites, test records, `bench run-tests`.

---

## 33. First-party Service example

### Источник

https://github.com/frappe/erpnext/blob/develop/erpnext/stock/services/stock_ledger_service.py

### Тип

**[FIRST-PARTY IMPLEMENTATION]**

### Что подтверждает

Service classes are not inherently alien to Frappe ecosystem. Complex logic can be extracted from Controllers into dedicated services.

### Что НЕ подтверждает

Every DocType should have a Service class.

---

# Правило работы с реестром

Если новый нормативный тезис нельзя привязать к одному из источников выше, он должен:

1. получить новый первичный источник;
2. либо явно маркироваться **[ARCHITECTURAL INFERENCE]**;
3. иметь описанную цепочку рассуждения и исключения.

Формулировка «так принято во Frappe» без проверяемого источника в стандарте не допускается.
