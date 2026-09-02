# Границы практикума

## Цель

Научить новичка проектировать, собирать и переносить небольшие приложения на Frappe Framework штатными средствами платформы.

Практикум не готовит администратора, который запомнил расположение кнопок. Он формирует базовую инженерную привычку:

```text
сначала смысл документа и гарантия
→ затем механизм Frappe
→ затем проверка, где эта гарантия реально обеспечивается
```

## Версия и источник истины

Основная версия — `Frappe Framework v16.32.0`.

При конфликте сведений действует следующий порядок:

1. поведение на стенде `v16.32.0`;
2. исходный код tag `v16.32.0`;
3. официальная документация Frappe;
4. ветка `version-16` только как информация о последующих изменениях.

Moving branch не используется для доказательства поведения зафиксированного практикума.

## Допустимые средства

Основной маршрут реально применяет и проверяет:

- Bench, site, app и Module;
- Developer Mode;
- Standard DocType и стандартные типы полей;
- naming, Link, Child Table, Tree и submittable documents;
- Role Permission, Permission Level, If Owner, User Permission и Share;
- Workflow, Workflow State и Workflow Action;
- Assign To, ToDo и Timeline;
- List, Form, Report Builder, Calendar, Kanban и Workspace;
- Number Card и Dashboard Chart;
- Data Import и Data Export там, где они нужны сценарию;
- Notification;
- Print Format и PDF;
- Web Form, Website User и Guest;
- стандартный REST API DocType;
- Standard metadata, fixtures, `migrate` и `install-app`;
- Git для каждого учебного app.

Role Permission Manager, Assignment Rule, Comments, Tags, Saved Filter, exported
customizations и другие штатные механизмы могут использоваться для наблюдения или
сравнения, но не объявляются освоенными без отдельного практического сценария. Точный
статус каждого механизма указан в [MATRIX.md](MATRIX.md).

Штатные Python expressions в Conditions и конфигурация `hooks.py` для fixtures считаются конфигурацией платформы, а не собственной business logic.

Для DocType, принадлежащих учебному app, финальные permissions задаются в таблице
Permissions самого Standard DocType и хранятся в его JSON. Role Permission Manager
используется для просмотра эффективной матрицы и знакомства с инструментом, но не
создаёт второй слой Custom DocPerm для собственных DocType.

## Что не используется в основном маршруте

- ERPNext, CRM, HRMS, Helpdesk и другие Frappe apps;
- custom Python controller;
- Client Script и собственный JavaScript;
- Server Script;
- `has_permission`, `permission_query_conditions` и другие permission hooks;
- custom REST endpoint;
- Query Report и Script Report;
- Jinja-логика сложнее простого Print Format;
- сторонняя интеграция, требующая отдельного сервиса;
- production deployment, reverse proxy, TLS, backups и observability.

Эти темы не объявляются плохими или запрещёнными. Они начинаются после того, как штатная конфигурация перестаёт выражать нужную гарантию. Практикум обязан показать эту границу, но не маскировать код под «ещё одну настройку».

## Предметные границы проектов

### Проект 1: реестр оборудования

Постоянная модель:

```text
Equipment Location (Tree)
Equipment Category
Equipment
Equipment Identifier (Child)
```

В проекте нет заявок, согласований, ремонтов и движения оборудования. Это реестр текущего состояния, а не учёт всех событий жизни объекта.

### Проект 2: заявки на закупку

Постоянная модель:

```text
Purchase Department
Purchase Request
Purchase Request Item (Child)
```

Заявка проходит Workflow и становится submittable document. Проект не заменяет закупочный модуль ERP: нет поставщиков, заказов, складского учёта, бухгалтерских проводок и оплаты.

### Проект 3: внешняя приёмная

Постоянная модель:

```text
Service Intake     ← внешний недоверенный ввод
Service Case       ← внутренний рабочий документ
Service Category
```

Web Form не создаёт внутренний `Service Case` напрямую. Передача из intake в case выполняется сотрудником после проверки. Автоматическое преобразование потребовало бы отдельной business logic и сознательно остаётся за границей базового маршрута.

## Что переносится между site

Переносимые слои:

| Слой | Примеры | Способ |
|---|---|---|
| стандартные метаданные | DocType, Report, Workspace, Web Form, Notification | исходники app |
| конфигурационные записи | Role, Workflow и связанные записи | fixtures или другой явно проверенный штатный экспорт |
| exported customizations | Custom Field, Property Setter, Custom DocPerm | только при расширении DocType другого app |

Не переносятся как часть универсального app:

- Users и пароли;
- API keys и secrets;
- SMTP и site config;
- Assignment Rule, если он ссылается на конкретных локальных Users;
- User Permission и Share, созданные для конкретных пользователей;
- рабочие Equipment, Purchase Request, Service Intake и Service Case;
- тестовые записи и файлы-вложения.

## Обязательные границы безопасности

1. Assignment показывает ответственность, но сам по себе не выдаёт право читать или менять документ.
2. Workflow ограничивает переходы, но не заменяет Role Permission.
3. Read Only и `Only Allow Edit For` — элементы формы и процесса, а не универсальная ACL.
4. Permission Level ограничивает поля, а не строки документов.
5. User Permission сужает доступ по Link-значениям, но не заменяет базовые права DocType.
6. Web Form — отдельный канал доступа. Создание нового target document в `v16.32.0` выполняется с `ignore_permissions=True`.
7. Публичная Web Form не должна принимать внутреннее состояние, исполнителя, закрытые Link-каталоги или другие служебные поля.
8. API user получает отдельную роль и минимальные права; ключи не попадают в Git.
9. Поле Check семантически подходит для булевого согласия, но обязательность Check сама
   по себе не гарантирует значение true. В P3 обязательный Select с одной непустой
   option используется только как осознанный no-code компромисс; при наличии собственной
   business logic такое требование должно проверяться на серверной стороне.

## Критерий завершения программы

Программа завершена, когда все три app:

- работают на исходном site;
- имеют понятную модель и ограниченный scope;
- проходят положительные и отрицательные проверки прав;
- не содержат собственной Python/JavaScript business logic;
- имеют чистую Git-историю;
- устанавливаются на новый site;
- воспроизводят заявленный сценарий после `install-app` и `migrate`;
- явно отделяют переносимые метаданные от локальных пользователей и рабочих данных.
