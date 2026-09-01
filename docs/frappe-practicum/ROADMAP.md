# Дорожная карта

Практикум идёт последовательно. Переход к следующему проекту разрешён только после clean-site gate текущего.

## Этап 0. Подготовить платформу

Результат:

- установлен Frappe `v16.32.0`;
- версии Python и Node соответствуют exact tag;
- bench запускается;
- можно создать site и войти в Desk;
- понятна разница между Bench, site и app.

Маршрут установки: [SETUP_WSL2.md](SETUP_WSL2.md).

Контроль:

```bash
bench version
python --version
node --version
```

## Этап 1. Реестр оборудования

Подробный сценарий: [projects/01-equipment-register/README.md](projects/01-equipment-register/README.md).

### P1.1. Контейнер продукта

- создать `equipment_register`;
- создать `equipment.localhost`;
- установить app;
- включить Developer Mode;
- проверить Module и исходную Git-структуру.

### P1.2. Модель до интерфейса

- зафиксировать границы реестра;
- создать `Equipment Location`, `Equipment Category`, `Equipment Identifier`, `Equipment`;
- настроить naming, Mandatory, Unique, Link и Child Table;
- проверить Tree и системные поля Document.

### P1.3. Рабочие данные

- создать минимальный набор вручную;
- импортировать второй набор;
- проверить ошибки обязательности, уникальности и Link;
- сравнить Data Export с source app.

### P1.4. Доступ

- создать роли Operator, Manager, Viewer;
- проверить Read/Write/Create/Delete;
- провести опыт с If Owner и User Permission;
- вернуть финальную permission matrix.

### P1.5. Рабочее место

- настроить Form/List;
- создать Kanban по обычному `status`;
- собрать Report Builder report, Number Card и Workspace;
- проверить видимость по ролям.

### P1.6. Поставка

- найти standard metadata в app;
- выполнить `migrate`;
- очистить случайные site-only настройки;
- сделать Git commit;
- установить app на `equipment-clean.localhost`;
- пройти приёмку без копирования Equipment records.

Gate P1: реестр работает как самостоятельный продукт и переносится на чистый site.

## Этап 2. Заявки на закупку

Подробный сценарий: [projects/02-purchase-requests/README.md](projects/02-purchase-requests/README.md).

### P2.1. Новый независимый app

- создать `purchase_requests` и `purchase.localhost`;
- не копировать DocType и роли из P1;
- зафиксировать business scenario и state machine.

### P2.2. Транзакционный документ

- создать `Purchase Department`;
- создать Child DocType `Purchase Request Item`;
- создать submittable `Purchase Request`;
- настроить naming series/format;
- проверить Draft, Submit, Cancel и Amend без Workflow.

### P2.3. Права

- создать четыре роли;
- разделить Create/Read/Write и Submit/Cancel/Amend;
- применить If Owner и Permission Level только к обоснованным полям;
- проверить каждую роль отдельным пользователем.

### P2.4. Workflow

- создать states и transitions;
- связать Approved с `docstatus = 1`, Cancelled — с `docstatus = 2`;
- запретить прямое утверждение Requester;
- проверить возврат на доработку и повторную подачу;
- не использовать Kanban drag для workflow state.

### P2.5. Совместная работа

- назначить конкретного согласующего через Assign To;
- проверить созданный ToDo;
- добавить Comments и Notification;
- провести локальный опыт с Assignment Rule;
- доказать, что назначение не расширило права.

### P2.6. Результат и контроль

- собрать Calendar по `required_by`;
- создать reports, chart и Workspace;
- сделать Print Format для Approved;
- получить PDF под ролью с Print permission.

### P2.7. Поставка

- классифицировать standard metadata, fixtures и site-specific records;
- экспортировать только переносимую конфигурацию;
- установить app на `purchase-clean.localhost`;
- повторить полный Workflow всеми ролями.

Gate P2: state machine и docstatus воспроизводятся на чистом site, а обходной переход запрещён.

## Этап 3. Внешняя приёмная

Подробный сценарий: [projects/03-service-intake/README.md](projects/03-service-intake/README.md).

### P3.1. Спроектировать trust boundary

- создать `service_intake` и `intake.localhost`;
- разделить недоверенный `Service Intake` и внутренний `Service Case`;
- определить минимальный публичный payload;
- запретить внешнему каналу служебные поля и закрытые Link-каталоги.

### P3.2. Внутреннее ядро

- создать `Service Category`, `Service Intake`, `Service Case`;
- настроить роли Triage, Agent, Manager;
- настроить простой внутренний Workflow case;
- проверить связь Case с исходным Intake.

### P3.3. Web Form

- создать Standard Web Form для `Service Intake`;
- проверить Guest create;
- проверить режим Website User;
- доказать финальные запреты list/edit/delete;
- убедиться, что Web Form не создаёт `Service Case`.

### P3.4. Триаж и работа

- принять одно обращение, отклонить другое;
- вручную создать Case из проверенного Intake;
- назначить Agent;
- настроить Notification и контроль очереди;
- собрать reports/cards/chart/Workspace.

### P3.5. Стандартный REST API

- создать отдельного API user;
- выдать минимальную роль;
- сгенерировать token локально;
- выполнить разрешённый read/create по стандартному API;
- доказать запрещённый доступ;
- не сохранять secret в shell history, документах или Git.

### P3.6. Поставка

- проверить, что Standard Web Form находится в app;
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

Финальная работа принимается только при наличии трёх независимых Git-репозиториев app и трёх clean-site протоколов.
