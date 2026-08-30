# 03. Что входит в Framework, а что является отдельным App

Перед тем как изучать возможности Frappe, нужно научиться отличать **сам Framework** от приложений, которые на нём работают.

Иначе легко увидеть функцию в ERPNext или CRM и решить, что она есть в чистом Frappe. Это одна из самых частых ошибок новичка.

Проверено: **2026-08-30**.

## 1. Самая простая модель

```text
Frappe Framework
├── общая техническая платформа
├── DocType / Document
├── Desk
├── permissions
├── Workflow
├── API
└── другие универсальные механизмы

Отдельные Apps
├── ERPNext
├── CRM
├── Helpdesk
├── HRMS
└── свои приложения
```

Framework даёт **инструменты**.

App добавляет **конкретные сущности и сценарии**.

Например:

```text
Workflow                           → Framework
«Согласование коммерческого счёта» → логика конкретного App
```

## 2. Пример на форме

Допустим, в ERPNext есть документ `Sales Order`.

Что здесь от Framework:

- форма;
- сохранение Document;
- Link-поля;
- permissions;
- Timeline;
- attachments;
- REST API;
- Workflow-механизм.

Что добавляет ERPNext:

- сам DocType `Sales Order`;
- его поля;
- бизнес-правила продаж;
- расчёты;
- связи с другими ERP-сущностями.

То есть Frappe умеет **обслуживать документ**, но не знает из коробки, что такое заказ клиента в конкретной ERP-модели.

## 3. Что точно относится к чистому Framework

Ниже не полный API-справочник, а полезная карта возможностей.

### Данные

- `DocType` и `DocField`;
- `Document` API;
- `Link`, `Dynamic Link`, Child Tables;
- Single, Tree, Submittable, Virtual DocTypes;
- ORM и Database API.

### Интерфейс

- Desk;
- Form View;
- List View;
- Workspaces;
- Reports;
- Kanban, Calendar, Gantt, Tree View там, где они применимы.

### Доступ

- `User`;
- `Role`;
- Role Permission Manager;
- Permission Level;
- User Permission;
- Sharing;
- owner-based permissions.

### Процессы

- Assignment и ToDo;
- Assignment Rule;
- Workflow;
- Notification;
- Auto Repeat.

### Возможности вокруг документа

- Comments и Timeline;
- Version / Track Changes;
- File и attachments;
- email / Communication;
- Print Format и PDF;
- Data Import / Export.

### Для интеграций и разработки

- REST API;
- whitelisted methods;
- Client Script;
- Server Script;
- hooks;
- background jobs;
- scheduler;
- realtime.

Все эти механизмы могут использовать разные Apps.

## 4. Что не стоит автоматически считать частью Framework

Примеры отдельных продуктов экосистемы:

```text
ERPNext
Frappe CRM
Frappe Helpdesk
Frappe HR / HRMS
Frappe Learning
Frappe Insights
Frappe Builder
Frappe Wiki
Frappe Drive
```

Они могут выглядеть очень «родными», потому что построены на Frappe, но это отдельные Apps.

### Несколько наглядных пар

| В Framework есть | Но это не значит, что в Framework есть |
|---|---|
| `File` и attachments | полноценный Frappe Drive |
| Reports и Charts | Frappe Insights |
| Web Forms | Frappe Builder |
| email / Communication | готовый Newsletter-продукт |
| ToDo и Assignment | готовый проектный менеджер |

Это важная граница: **базовый механизм не равен готовому предметному продукту**.

## 5. Особенность v16: часть старого core вынесли в отдельные Apps

В Frappe 16 некоторые возможности, которые раньше жили внутри `frappe`, вынесены отдельно. В migration guide упоминаются, в частности:

- Energy Points;
- Newsletter;
- Backup Integrations;
- Blog.

Поэтому статья или видео по старой версии может говорить «это есть в Frappe», а на чистом v16 соответствующего модуля уже не будет.

Это не ошибка установки — состав Framework изменился.

## 6. Как самому проверить спорную функцию

Если встретил незнакомую возможность, можно пройти короткую проверку.

### Шаг 1. Есть ли она на чистом Site только с `frappe`?

Если функция появляется только после установки другого App, ответ уже понятен.

### Шаг 2. Где находится DocType или код?

Если объект живёт в репозитории `frappe/frappe`, это сильный признак core Framework.

Если он находится, например, в `frappe/erpnext` или другом репозитории — это отдельное App.

### Шаг 3. Что говорит документация?

Смотри именно документацию **Framework**, а не документацию конкретного продукта.

## 7. Простой пример классификации

Попробуем разложить несколько вещей:

| Возможность | Framework или отдельное App? |
|---|---|
| создать свой DocType | Framework |
| настроить Workflow | Framework |
| назначить документ пользователю | Framework |
| открыть Kanban для подходящего DocType | Framework |
| вести бухгалтерский план счетов ERPNext | ERPNext |
| использовать готовый CRM pipeline Frappe CRM | CRM App |
| хранить вложение у документа | Framework |
| получить полноценный файловый диск с UI Drive | Frappe Drive |

Если такое разделение стало интуитивным, дальше будет намного проще читать документацию.

## 8. Зачем вообще знать эту границу

Есть две противоположные ошибки.

### Ошибка 1. Писать то, что уже есть

Например, делать собственную систему ролей, не изучив Role Permission Manager.

### Ошибка 2. Ждать от Framework готовый бизнес-продукт

Например, считать, что раз в Framework есть Assignment и Kanban, то он уже является полноценной системой управления проектами.

Правильный подход находится посередине: сначала понять штатные строительные блоки, затем уже собирать из них нужное приложение.

## Мини-практика

Попробуй классифицировать без подсказки:

1. `DocType` — **Framework**.
2. `Sales Invoice` — **не core Framework; предметный DocType ERPNext**.
3. `User Permission` — **Framework**.
4. Frappe Insights — **отдельное App**.
5. REST API для своего DocType — **Framework**.

## Что запомнить

- Frappe Framework — **платформа**, а не ERP/CRM/Helpdesk сразу.
- Наличие функции в одном Frappe-приложении не доказывает её наличие в core.
- Framework даёт универсальные механизмы; Apps добавляют предметную модель.
- Для v16 старые материалы нужно проверять: часть прежнего core вынесена в отдельные Apps.

## Официальные источники

- [Frappe Framework — Introduction](https://docs.frappe.io/framework/user/en/introduction)
- [Frappe Framework documentation](https://docs.frappe.io/framework/user/en)
- [Migrating to Version 16](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)
- [Frappe Framework source](https://github.com/frappe/frappe/tree/version-16)

Следующая глава: [**04. DocType от А до Я**](04_DOCTYPE.md).