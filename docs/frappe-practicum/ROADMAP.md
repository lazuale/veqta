# Дорожная карта

Практикум идёт последовательно. Переход к следующему проекту разрешён только после
проверки текущего app на чистом site.

## Этап 0. Подготовить платформу

Результат:

- установлен Frappe `v16.32.0`;
- версии Python и Node соответствуют exact tag;
- bench запускается;
- можно создать site и войти в Desk;
- понятна разница между Bench, site и app.

Маршрут установки: [SETUP_WSL2.md](SETUP_WSL2.md).

После установки выполнить [FOUNDATIONS.md](FOUNDATIONS.md). Переход к P1 разрешён,
когда ученик может объяснить Bench, site, app, Module, DocType и Document и умеет
находить объекты через Awesomebar.

Контроль:

```bash
bench version
python --version
node --version
```

## Этап 1. Реестр оборудования

Пошаговый маршрут: [projects/01-equipment-register/LABS.md](projects/01-equipment-register/LABS.md).

### P1.1. Контейнер продукта

- создать `equipment_register`;
- создать `equipment.localhost`;
- установить app;
- включить Developer Mode;
- проверить Module и исходную Git-структуру.

### P1.2. Модель до интерфейса

- создать `Equipment Location`, `Equipment Category`, `Equipment Identifier`, `Equipment`;
- настроить naming, Set Only Once, Mandatory, Link и Child Table;
- проверить Tree и системные поля Document;
- задать базовые Permissions в Standard DocType.

### P1.3. Рабочие данные

- создать минимальный набор вручную;
- импортировать второй набор;
- проверить ошибки обязательности, naming и Link;
- проверить глобальный поиск по дочернему идентификатору;
- сравнить Data Export с исходниками app.

### P1.4. Доступ

- создать роли Operator, Manager, Viewer;
- проверить Read/Write/Create/Delete отдельными пользователями;
- провести временные опыты с If Owner, User Permission и Share;
- вернуть финальную permission matrix.

### P1.5. Рабочее место

- настроить List View;
- создать Kanban по обычному `status`;
- проверить Timeline после изменения состояния;
- собрать Report Builder report, Number Card и Workspace;
- проверить видимость по ролям.

### P1.6. Поставка

- найти Standard metadata в app;
- экспортировать только необходимые fixtures;
- выполнить `migrate`;
- сделать Git commit;
- установить app на `equipment-clean.localhost`;
- пройти приёмку без копирования записей Equipment.

Gate P1: реестр работает как самостоятельный продукт и переносится на чистый site.

## Этап 2. Заявки на закупку

Пошаговый маршрут: [projects/02-purchase-requests/LABS.md](projects/02-purchase-requests/LABS.md).

### P2.1. Новый независимый app и site

- создать `purchase_requests` и `purchase.localhost`;
- не устанавливать `equipment_register` на этот site;
- включить Developer Mode;
- проверить Module и Apps Page.

### P2.2. Роли и транзакционная модель

- создать четыре роли проекта;
- создать `Purchase Department`;
- создать Child DocType `Purchase Request Item`;
- создать submittable `Purchase Request`;
- настроить naming format, Permission Level и базовые DocPerm.

### P2.3. Обычный lifecycle до Workflow

- создать тестовую заявку;
- выполнить Save, Submit, Cancel и Amend;
- записать фактические значения `docstatus`;
- отделить механику submittable document от будущего Workflow.

### P2.4. Пользователи и базовые права

- создать Requester, Approver, Procurement Officer и Auditor;
- проверить If Owner;
- ограничить Requester и Approver через User Permission по Department;
- проверить Permission Level;
- не использовать Assignment как замену авторизации.

### P2.5. Workflow

- создать Workflow State и Workflow Action Master;
- создать `Purchase Request Approval`;
- связать Approved с `docstatus = 1`, Cancelled — с `docstatus = 2`;
- проверить возврат на доработку и повторную подачу;
- доказать, что прямое изменение workflow state не является допустимым переходом.

### P2.6. Совместная работа и представления

- назначить согласующего через Assign To;
- проверить ToDo и Timeline;
- настроить System Notification;
- создать Calendar по `required_by`;
- собрать Report Builder report, Number Card, Dashboard Chart и Workspace;
- сделать Print Format и получить PDF под рабочей ролью;
- Assignment Rule оставить только временным опытом, если он нужен для сравнения.

### P2.7. Поставка

- классифицировать Standard metadata, fixtures и локальные записи site;
- экспортировать только переносимую конфигурацию;
- не переносить Users, User Permission, Assignment Rule, заявки и вложения;
- установить app на `purchase-clean.localhost`;
- повторить полный Workflow новыми тестовыми Users.

Gate P2: state machine и docstatus воспроизводятся на чистом site, а обходной переход запрещён.

## Этап 3. Внешняя приёмная

Пошаговый маршрут: [projects/03-service-intake/LABS.md](projects/03-service-intake/LABS.md).

### P3.1. Новый app, site и роли

- создать `service_intake` и `intake.localhost`;
- включить Developer Mode;
- проверить Module;
- создать роли Triage, Agent, Manager и API Reader.

### P3.2. Модель и граница доверия

- создать `Service Category`, `Service Intake`, `Service Case`;
- отделить недоверенный Intake от внутреннего Case;
- дать публичному документу только необходимые поля;
- разделить служебные поля через Permission Level;
- запретить API Reader доступ к Intake и Case.

### P3.3. Внутренний Workflow

- создать состояния Open, In Progress, Resolved и Closed;
- создать действия Start Work, Resolve, Close и Reopen;
- оставить все состояния с `docstatus = 0`;
- требовать Resolution перед Resolve.

### P3.4. Web Form

- создать Standard Web Form для `Service Intake`;
- проверить Guest create;
- проверить обязательное явное согласие на контакт;
- сравнить Guest и Website User режимы;
- доказать финальные запреты list/edit/delete;
- убедиться, что форма не принимает служебные поля и не создаёт `Service Case`.

### P3.5. Триаж и внутренняя работа

- принять одно обращение, отклонить другое;
- вручную создать Case только из проверенных данных;
- проверить Unique на связи Intake → Case;
- назначить Agent и пройти Workflow;
- настроить Notification;
- собрать раздельные отчёты по Intake и Case, Number Card, Dashboard Chart и Workspace.

### P3.6. Стандартный REST API

- создать отдельного API user;
- выдать минимальную роль;
- сгенерировать key/secret локально;
- выполнить разрешённый Read по `Service Category`;
- доказать запрещённый доступ к `Service Intake`;
- удалить секреты из переменных shell после проверки и не сохранять их в Git.

### P3.7. Поставка

- проверить, что Standard Web Form находится в app;
- экспортировать только роли и Workflow-конфигурацию, которой действительно нужны fixtures;
- не экспортировать Users, keys, SMTP и рабочие обращения;
- установить app на `intake-clean.localhost`;
- повторить Guest submission и внутренний triage.

Gate P3: внешний канал работает, но не пересекает внутреннюю границу полномочий.

## Финальный аудит

После P3 ученик без подсказки объясняет:

1. где заканчивается framework и начинается app;
2. почему DocType — это модель документа, а не просто таблица;
3. когда нужен Link, Child Table, Tree и submittable document;
4. чем Role Permission отличается от Permission Level, User Permission и Share;
5. почему Assignment не является авторизацией;
6. почему Workflow не заменяет базовые права;
7. почему Web Form нельзя считать обычной Desk-формой;
8. какие объекты app переносятся source-файлами, fixtures и customizations;
9. почему Data Export не является поставкой app;
10. как доказать переносимость на чистом site.

Финальная работа принимается только при наличии трёх независимых Git-репозиториев app и
трёх протоколов проверки на чистом site.
