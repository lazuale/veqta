# 09. Deployment, Migrations и Testing — архитектура должна воспроизводиться

## 1. Архитектура Frappe App существует не только на dev-site

Система считается спроектированной не тогда, когда она работает на одном настроенном site, а когда обязательное состояние можно воспроизвести.

Для source-controlled App целевой принцип:

```text
чистый совместимый Frappe site
+ repository App
+ install-app / migrate
= обязательное состояние приложения
```

Это **[ARCHITECTURAL INFERENCE]**, основанный на официальных механизмах Apps, DocType JSON, fixtures и migrations.

---

## 2. Standard DocType metadata живёт в source tree

**[FRAPPE DOCS]** При изменении Standard DocType в developer mode Frappe сохраняет DocType JSON в source tree App. При install/migrate schema синхронизируется с JSON.

Источник:

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations

Это делает metadata частью version-controlled продукта.

### Следствие

Если новый обязательный field существует только потому, что кто-то вручную добавил его на одном site, продукт ещё не воспроизводим.

---

## 3. `bench migrate` — не только изменение таблиц

**[FRAPPE DOCS]** `bench migrate` выполняет целый deployment pipeline, включая:

- before_migrate hooks;
- application patches;
- schema/background jobs sync;
- fixtures sync;
- dashboards/web pages и другие sync stages;
- after_migrate hooks.

Источник:

- https://docs.frappe.io/framework/user/en/bench/reference/migrate

Это показывает, что App lifecycle во Frappe включает не только Python code.

---

## 4. Schema migration нужно проектировать вместе с моделью

**[FRAPPE DOCS]** Frappe synchronizes DocTypes из JSON и отдельно предупреждает, что reverse schema migrations не поддерживаются.

Источник:

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations

Перед изменением production DocType нужно ответить:

```text
Что произойдёт с существующими records?
Можно ли safely добавить field?
Меняется ли тип данных?
Что делать со старым field?
Как мигрировать значения?
Есть ли rollback strategy на уровне release?
```

### Red flag

Спроектировать новую schema как будто production data ещё не существует.

---

## 5. Fields soft-delete и почему это важно

**[FRAPPE DOCS]** При schema sync удалённые fields обычно soft-deleted на уровне metadata: column может сохраняться, чтобы избежать потери данных и позволить migration logic использовать старые значения.

Источник:

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations

Это не означает, что старые columns можно бесконечно считать частью application model. Для пользователя field уже не существует.

---

## 6. Data patches

**[FRAPPE DOCS]** Для one-off data migrations Frappe использует Python patches, зарегистрированные в `patches.txt`.

Источник:

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations

Пример:

```text
раньше status = "Open"
теперь модель использует status = "New"
```

Если existing records должны быть преобразованы, это migration responsibility App.

### Неправильно

После deploy написать в инструкции:

```text
откройте MariaDB
выполните UPDATE ... вручную
```

если это обязательная часть release.

---

## 7. Patch должен быть повторяемо доставляемым изменением

Patch обычно выполняется один раз на site и Frappe отслеживает его выполнение.

Это позволяет release code и data migration ехать вместе.

### Design review patch

```text
Patch идемпотентен или безопасен при необычном состоянии?
Что если часть данных уже мигрирована?
Есть ли зависимости от schema до/после sync?
Нужны ли commits внутри patch?
Как проверить результат?
```

---

## 8. Fixtures — configuration as code

**[FRAPPE DOCS]** Fixtures — database records, экспортируемые в JSON и синхронизируемые при install/update.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks#fixtures

Примеры подходящих fixtures:

```text
обязательная Role;
configuration record;
Custom Field;
часть справочника, определяемая продуктом.
```

### Не использовать fixtures для transactions

Не нужно экспортировать в Git обычные пользовательские:

```text
Orders
Tasks
Invoices
```

только потому, что механизм технически может экспортировать records.

---

## 9. Export Customizations

**[FRAPPE DOCS]** Custom Fields, Property Setters и связанные customizations можно экспортировать в App и синхронизировать при update/migrate.

Источник:

- https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

Но документация предупреждает о replacement semantics Property Setters/Custom Permissions на target site.

### Архитектурный вопрос

Кто владеет этой configuration:

```text
продукт
или
локальный администратор site?
```

Без этого exported customization может конфликтовать с локальной настройкой.

---

## 10. Install hooks и migrate hooks

Frappe имеет lifecycle hooks App/site installation и migration.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks

Они подходят для специальных действий, которые нельзя выразить metadata/fixtures/patches.

Но hook не должен заменять понятный fixture/patch только потому, что «Python проще написать».

---

## 11. Dependencies App

App может зависеть от других Apps. Extension другого App должен учитывать его наличие и совместимость.

При архитектуре нужно явно фиксировать:

```text
required app;
minimum/compatible version;
ownership extended DocTypes;
hook dependencies.
```

Это особенно важно для Apps, расширяющих ERPNext или HRMS.

---

## 12. Version-sensitive architecture

Стандарт ориентирован на Frappe v16, но отдельные capabilities имеют version boundaries.

Примеры:

```text
extend_doctype_class → v16+
Packages             → v14+
Server Script default restrictions → v15+
```

### Правило

Version-sensitive архитектурное решение должно иметь пометку в documentation и dependency metadata App.

Нельзя рассчитывать на capability v16, заявляя совместимость с v15.

---

## 13. Testing — часть architecture contract

**[FRAPPE DOCS]** Frappe предоставляет test runner, `FrappeTestCase`, test site semantics и команды `bench run-tests`.

Источники:

- https://docs.frappe.io/framework/user/en/testing
- https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing

Frappe может автоматически создавать test records для dependent DocTypes, обнаруженных по Link fields.

---

## 14. Что тестировать

Тестируем не сам факт существования стандартных возможностей Frappe, а **наши contracts поверх них**.

### Document invariants

```text
invalid state нельзя сохранить
```

### Lifecycle

```text
submit создаёт нужный эффект
cancel корректно обращает его
```

### Permissions

```text
Employee не видит restricted Document
Manager видит
```

### Workflow/domain transitions

```text
недопустимый переход отвергается
```

### Services

```text
сложный расчёт даёт ожидаемый результат
```

### API

```text
command проверяет authorization и идемпотентность
```

### Migration

```text
старое состояние данных превращается в новое корректно
```

---

## 15. Что не нужно бессмысленно тестировать

Не требуется писать собственный тест только чтобы доказать:

```text
Frappe Link field работает;
frappe.get_doc умеет загружать Document;
стандартный REST endpoint существует.
```

Это ответственность Framework.

Но если наше App использует capability особым способом и от него зависит critical flow, integration test может быть оправдан.

---

## 16. Tests и transactions

**[FRAPPE DOCS]** `FrappeTestCase` предоставляет Frappe-specific test setup и transaction isolation behaviour.

Источник:

- https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing

Это важно для тестов lifecycle и persistence.

---

## 17. Upgrade test

Для App, который расширяет Frappe/ERPNext, обычных unit tests недостаточно.

Нужны проверки:

```text
чистая установка;
migrate с предыдущей supported version;
совместимость hooks/overrides;
fixtures/customization sync;
критические permissions;
critical user flows.
```

Иначе система может работать на давно настроенном dev-site, но не устанавливаться заново.

---

## 18. Воспроизводимость — обязательный acceptance criterion

Для app-owned состояния нельзя принимать результат, который существует только как набор ручных действий.

Плохая release инструкция:

```text
1. install app
2. откройте Customize Form
3. создайте 14 fields
4. измените permissions
5. создайте Workflow
6. добавьте Notification
```

Если эти элементы обязательны на каждом site, они должны быть доставляемы штатным механизмом App/fixtures/customizations/migrations.

---

## 19. Deployment/test design review

```text
1. Всё обязательное состояние App существует в Git или штатно экспортируется?
2. Можно ли установить App на чистый site без ручного накликивания?
3. Какие fixtures являются частью продукта?
4. Какие customizations принадлежат site, а какие App?
5. Какие schema/data migrations нужны?
6. Есть ли manual production SQL? Почему?
7. Какие version-specific features используются?
8. Какие tests защищают собственные invariants?
9. Проверяется ли clean install?
10. Проверяется ли migrate с предыдущей версии?
```
