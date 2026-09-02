# 12. Реестр доказательств — первичные источники и статус утверждений

Этот файл нужен, чтобы архитектурный стандарт не превращался в набор мнений.

Для каждого класса решений здесь зафиксирован источник, тип доказательства и то, **что именно** из него допустимо выводить.

---

## 1. Философия / configuration over code

### Источник

https://docs.frappe.io/framework/user/en/basics/why

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- Frappe создавался как основа ERPNext;
- философия: писать как можно меньше кода;
- предпочтение configuration over code, то есть настройки вместо программирования там, где этого достаточно;
- универсальные возможности помещаются во Framework;
- основные возможности поставляются из коробки;
- Apps являются штатным механизмом расширения.

### Что НЕ подтверждает

- запрет Python;
- запрет сервисных слоёв;
- обязательную low-code разработку любого приложения.

---

## 2. Метаданные и монолитная архитектура

### Источник

https://docs.frappe.io/framework/user/en/introduction

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- метаданные рассматриваются как данные;
- полнофункциональную модель с возможностями из коробки;
- прямо заявленную монолитную архитектуру;
- Desk предоставляет формы, списки, права, файлы и навигацию.

### Архитектурное следствие

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Не дублировать согласованные прикладные механизмы только ради привычного шаблона другого фреймворка.

---

## 3. Описание пакета Framework v16

### Источник

https://github.com/frappe/frappe/blob/version-16/pyproject.toml

### Тип

**[ИСХОДНЫЙ КОД]**

### Что подтверждает

Описание проекта: metadata driven, full-stack low code web framework.

Также фиксирует требования ветки v16 к версии Python.

---

## 4. Контрольная точка версии v16

### Источник

https://github.com/frappe/frappe/releases/tag/v16.33.0

### Тип

**[РЕЛИЗ FRAPPE]**

### Что подтверждает

Проверенная точка актуальности стандарта: v16.33.0, 1 сентября 2026 года.

Стандарт не должен хранить этот номер как вечную «последнюю версию»; он только фиксирует базовую точку проверки.

---

## 5. DocType как основной строительный блок

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- `DocType` — основной строительный блок;
- метаданные описывают модель и представление;
- обычные `DocType` связаны со схемой базы данных.

### Что НЕ подтверждает

- «каждое существительное бизнеса обязано быть DocType».

Выбор `DocType` или поля/Child — архитектурный вывод.

---

## 6. Типы полей / Link / Dynamic Link / Table MultiSelect

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Назначение стандартных типов полей и связей.

### Архитектурное следствие

Сначала выбирать механизм с соответствующим смыслом, а не создавать отдельный `DocType` автоматически.

---

## 7. Child DocType

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- Child-запись прикреплена к родителю;
- смысл `parent`/`parenttype`/`parentfield`/`idx`.

### Что НЕ подтверждает

Любая связь one-to-many обязана быть Child Table.

Самостоятельная бизнес-запись может требовать обычный `DocType`.

---

## 8. Single DocType

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

`Single` предназначен для данных, существующих в одном экземпляре, например настроек.

---

## 9. Virtual DocType

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Данные во внешнем или нестандартном хранилище могут быть представлены через абстракцию `Document`.

### Что НЕ подтверждает

Каждая интеграция с внешним API должна быть `Virtual DocType`.

---

## 10. Naming

### Источник

https://docs.frappe.io/framework/user/en/basics/doctypes/naming

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

`name` и стандартные стратегии именования являются частью модели `DocType`.

### Архитектурное следствие

Идентификатор нужно выбирать до накопления производственных ссылок.

---

## 11. Document Controller / жизненный цикл

### Источники

- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE] + [ИСХОДНЫЙ КОД]**

### Что подтверждает

- Controllers наследуются от `Document`;
- методы жизненного цикла;
- `save`/`insert` выполняют проверки прав, данных и событий жизненного цикла.

### Архитектурное следствие

Критичный инвариант должен жить в серверном пути, а не только в интерфейсе.

---

## 12. Ограничение Client Script

### Источник

https://docs.frappe.io/framework/user/en/desk/scripting/client-script

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

`Client Script` работает в браузерном контексте стандартной формы; его проверка не является универсальной серверной гарантией.

---

## 13. Server Script

### Источник

https://docs.frappe.io/framework/user/en/desk/scripting/server-script

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- `Server Script` поддерживает `Document Event` и API;
- начиная с v15 отключён по умолчанию на shared benches;
- публичные shared benches Frappe Cloud его не разрешают.

### Архитектурное следствие

`Server Script` не является обязательной ступенью перед Python-кодом App.

---

## 14. DocStatus

### Источник

https://docs.frappe.io/framework/doctypes/docstatus

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

`Draft / Submitted / Cancelled` — системная транзакционная семантика.

### Что НЕ подтверждает

Бизнес-статус должен совпадать с `docstatus`.

---

## 15. Workflow

### Источник

https://docs.frappe.io/erpnext/user/manual/en/workflows

### Тип

**[ОФИЦИАЛЬНАЯ ДОКУМЕНТАЦИЯ ЭКОСИСТЕМЫ]**

### Что подтверждает

Состояния, переходы, роли, условия и смысл согласований в `Workflow`.

### Примечание

`Workflow` является механизмом Frappe/ERPNext; страница документации может находиться в руководстве ERPNext, но сам механизм входит в стек Frappe.

---

## 16. Общая модель прав доступа

### Источник

https://docs.frappe.io/framework/user/en/basics/users-and-permissions

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

`Role`, `DocType Permissions`, `If Owner`, `Permission Level`, `User Permissions` и другие базовые механизмы.

---

## 17. Права доступа во время выполнения

### Источник

https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py

### Тип

**[ИСХОДНЫЙ КОД]**

### Что подтверждает

- вычисление прав ролей;
- обработку владельца;
- `User Permission`;
- путь `Share`;
- проверки Controller;
- прямой комментарий: Controller может запретить право, но не выдать отсутствующее базовое право.

### Важно

Наш рекомендуемый порядок проектирования не должен выдаваться за буквальный порядок выполнения Framework.

---

## 18. permission_query_conditions

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- `permission_query_conditions` изменяет запрос списка;
- применяется к `frappe.db.get_list`;
- не применяется к `frappe.db.get_all`;
- `has_permission` — собственный hook проверки документа.

### Архитектурное следствие

Собственная политика доступа к строкам должна учитывать и список/запрос, и прямой доступ к `Document`.

---

## 19. Запросы с учётом прав и права на поля

### Источник

https://docs.frappe.io/framework/get_query

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Запрос с учётом прав включает `User Permission`, sharing, ограничения владельца, `permission_query_conditions` и права на поля.

---

## 20. Модель транзакций базы данных

### Источник

https://docs.frappe.io/framework/user/en/api/database

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- неявные правила `commit`/`rollback`;
- транзакции фоновых и плановых задач;
- модель транзакций patches;
- прямой Database API;
- `set_value` обходит ORM-события;
- callbacks транзакций.

### Архитектурное следствие

Ручной `commit` и прямой обход жизненного цикла БД должны быть осознанными исключениями.

---

## 21. Background Jobs

### Источники

- https://docs.frappe.io/framework/user/en/api/background_jobs
- https://github.com/frappe/frappe/blob/version-16/frappe/utils/background_jobs.py

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE] + [ИСХОДНЫЙ КОД]**

### Что подтверждает

Очереди, `frappe.enqueue`, `scheduler_events`, `enqueue_after_commit`, callbacks, идентификаторы задач и дедупликацию в реализации v16.

---

## 22. REST API

### Источники

- https://docs.frappe.io/framework/user/en/api/rest
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api
- https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE] + [ИСХОДНЫЙ КОД]**

### Что подтверждает

- стандартный ресурсный API `DocType`;
- создание, чтение, изменение и удаление;
- методы `Document`;
- учёт прав при чтении и обновлении.

### Что НЕ подтверждает

Любой внешний продуктовый API обязан использовать стандартный контракт `Document`.

---

## 23. Предупреждение о внутренней реализации REST

### Источник

https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

### Тип

**[ИСХОДНЫЙ КОД]**

### Что подтверждает

Функции внутренней реализации маршрутов не должны считаться стабильным Python API для кода приложения.

---

## 24. Webhooks

### Источник

https://docs.frappe.io/framework/user/en/guides/integration/webhooks

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

`Document Event` + условие → HTTP-вызов, включая необязательную HMAC-подпись.

### Что НЕ подтверждает

`Webhook` является гарантированной шиной событий с exactly-once доставкой.

---

## 25. Hooks / точки расширения

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Hooks существуют для расширения и переопределения; включают `doc_events`, `extend_doctype_class`, `override_doctype_class`, `scheduler_events`, fixtures, permission hooks и другие точки.

---

## 26. extend_doctype_class v16+

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks#extend-doctype-class

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

В v16 расширение класса рекомендуется для добавления поведения вместо полного override там, где расширения достаточно.

---

## 27. Структура App

### Источники

- https://docs.frappe.io/framework/user/en/basics/apps
- https://docs.frappe.io/framework/user/en/tutorial/create-an-app

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Python-пакет, `hooks.py`, `modules.txt`, `patches.txt`, templates/public и другие части структуры приложения.

---

## 28. Packages

### Источник

https://docs.frappe.io/framework/user/en/guides/deployment/packages

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

`Packages` — облегчённые пакеты для пользовательских `Module Def`, доступные с v14.

---

## 29. Fixtures

### Источник

https://docs.frappe.io/framework/user/en/python-api/hooks#fixtures

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Записи базы данных можно экспортировать и синхронизировать через fixtures.

### Архитектурное следствие

Использовать для конфигурации, принадлежащей App, а не для обычных транзакционных данных.

---

## 30. Export customizations

### Источник

https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- `Custom Fields`/`Property Setters` можно экспортировать;
- они синхронизируются при обновлении или `migrate`;
- есть предупреждение о замене `Property Setters` и `Custom Permissions`.

---

## 31. Миграции и patches

### Источники

- https://docs.frappe.io/framework/user/en/guides/deployment/migrations
- https://docs.frappe.io/framework/user/en/bench/reference/migrate

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Синхронизацию схемы из JSON `DocType`, patches, fixtures и жизненный цикл `migrate`; обратные миграции схемы не поддерживаются.

---

## 32. Тестирование

### Источники

- https://docs.frappe.io/framework/user/en/testing
- https://docs.frappe.io/framework/user/en/guides/automated-testing/unit-testing

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

Test runner Frappe, `FrappeTestCase`, тестовые сайты, тестовые записи и `bench run-tests`.

---

## 33. Пример Service из официального приложения

### Источник

https://github.com/frappe/erpnext/blob/develop/erpnext/stock/services/stock_ledger_service.py

### Тип

**[ОФИЦИАЛЬНАЯ РЕАЛИЗАЦИЯ]**

### Что подтверждает

Классы `Service` не являются чуждыми экосистеме Frappe. Сложную логику можно выносить из Controllers в отдельные сервисы.

### Что НЕ подтверждает

Каждый `DocType` должен иметь свой `Service`.

---

## 34. Аутентификация REST API

### Источники

- https://docs.frappe.io/framework/user/en/api/rest
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api/oauth-2

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- REST API поддерживает token-based и password/session authentication;
- OAuth access token поддерживается как Bearer token;
- API Key/API Secret связаны с конкретным `User`;
- запросы с таким токеном выполняются с проверкой ролей этого пользователя.

### Архитектурное следствие

Аутентификацию интеграции нужно проектировать отдельно от её permissions; технический пользователь не должен автоматически быть Administrator.

---

## 35. File и вложения

### Источник

https://docs.frappe.io/framework/user/en/desk/attachments

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- файлы можно прикреплять к `Document`;
- пользователь с `Read` на исходный документ получает доступ к прикреплённым файлам;
- Frappe имеет собственный File Manager и модель вложений.

### Архитектурное следствие

Для обычного вложения сначала использовать `File`/Attach; собственный attachment-`DocType` требует дополнительной бизнес-семантики.

---

## 36. Comment и Version

### Источники

- https://docs.frappe.io/framework/user/en/api/document
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api
- https://docs.frappe.io/erpnext/document-versioning

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE] + [ОФИЦИАЛЬНАЯ ДОКУМЕНТАЦИЯ ЭКОСИСТЕМЫ]**

### Что подтверждает

- `Document` поддерживает добавление комментариев;
- REST API v2 предоставляет стандартный `add_comment`;
- при `Track Changes` ведётся журнал версий с изменёнными полями, временем и пользователем.

### Что НЕ подтверждает

`Version` является юридически неизменяемым compliance-журналом для любых регуляторных требований.

---

## 37. Realtime API

### Источник

https://docs.frappe.io/framework/user/en/api/realtime

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- Frappe поставляет realtime API на базе Socket.IO;
- клиент может подписываться через `frappe.realtime.on`;
- сервер публикует события через `frappe.publish_realtime`;
- `frappe.publish_progress` предназначен для отображения прогресса.

### Важно

Custom realtime handlers, отмеченные документацией как nightly/experimental, не считаются стабильным контрактом Frappe v16 без отдельной проверки.

---

## 38. Permission Types [v16+]

### Источник

https://docs.frappe.io/framework/permission-types

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- механизм доступен начиная с v16;
- можно создавать типы прав сверх встроенных `read`, `write`, `create`, `delete`, `submit` и других;
- `Permission Type` привязывается к `DocType` и поставляется с App как fixture;
- проверка выполняется через `frappe.has_permission()`;
- назначение права ролям выполняется через `Role Permission Manager`.

### Архитектурное следствие

Для отдельного действия вроде `approve`, которое должно управляться ролями, сначала проверить `Permission Type`, а не создавать параллельную ACL-модель или разбрасывать ручные проверки ролей по коду.

### Что НЕ подтверждает

`Permission Type` заменяет `Workflow` или любую сложную политику доступа. Он отвечает за возможность выполнить действие, а не за последовательность бизнес-переходов.

---

## 39. DocType Layout [v16+]

### Источник

https://docs.frappe.io/framework/doctypes/doctype-layout

### Тип

**[ДОКУМЕНТАЦИЯ FRAPPE]**

### Что подтверждает

- один `DocType` может иметь несколько layouts;
- layout может наследоваться от другого layout через `Based On`;
- ссылки `DocType` в `Workspace` могут открывать конкретную раскладку;
- стандартные layouts экспортируются в App как JSON и поставляются через `bench migrate`.

### Архитектурное следствие

Разные формы для разных рабочих контекстов не являются сами по себе основанием создавать дублирующие `DocType`, если данные, идентичность и жизненный цикл остаются общими.

### Что НЕ подтверждает

Различие интерфейса отменяет модель прав доступа или позволяет объединять действительно разные бизнес-объекты в один `DocType`.

---

# Правило работы с реестром

Если новый нормативный тезис нельзя привязать к одному из источников выше, он должен:

1. получить новый первичный источник;
2. либо явно маркироваться **[АРХИТЕКТУРНЫЙ ВЫВОД]**;
3. иметь описанную цепочку рассуждения и исключения.

Формулировка «так принято во Frappe» без проверяемого источника в стандарте не допускается.
