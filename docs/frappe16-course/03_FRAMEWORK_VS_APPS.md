# 03. Что входит в чистый Frappe Framework 16, а что является отдельным App

Эта глава проводит одну из самых важных границ во всём курсе: **Frappe Framework — это платформа, а не набор всех продуктов экосистемы Frappe**.

Цель главы — научиться смотреть на любую возможность и правильно отвечать:

```text
это механизм самого Framework?
или
это функциональность отдельного приложения?
```

Проверено: **2026-08-30**.

---

## 1. Почему эта граница вообще нужна

Вокруг Frappe существует много приложений:

```text
ERPNext
Frappe CRM
Frappe Helpdesk
Frappe HR
Frappe Learning
Frappe Insights
Frappe Builder
Frappe Wiki
Frappe Drive
и другие
```

Все они могут быть построены на Frappe Framework и использовать его механизмы.

Из этого легко сделать неправильный вывод:

> если функция есть в одном из этих продуктов, значит она входит в Frappe Framework.

Это неверно.

Правильная модель:

```text
                 Frappe Framework
                       │
        ┌──────────────┼──────────────┐
        │              │              │
     ERPNext        CRM App       Helpdesk App
        │              │              │
   свои DocTypes   свои DocTypes   свои DocTypes
   своя логика     своя логика     своя логика
        │              │              │
        └──────────────┼──────────────┘
                       │
              используют Framework
```

Framework предоставляет общие технические механизмы.

App добавляет предметную функциональность.

---

## 2. Как сам Frappe описывает Framework

Официальная документация называет Frappe **full-stack, batteries-included web framework**.

Это значит, что Framework уже содержит очень много универсальной инфраструктуры для database-driven приложений:

```text
модели данных
UI
permissions
authentication
API
reports
printing
email
background jobs
realtime
и другие общие механизмы
```

Но `batteries included` не означает:

```text
готовая бухгалтерия
готовый склад
готовый CRM
готовый helpdesk
готовый HRM
```

Это уже предметные приложения.

---

# Часть I. Что относится к Framework

## 3. Metadata и модель данных

В чистый Framework входит базовая модель:

```text
DocType
DocField
Document
Meta
```

А также типы связей и специальные варианты DocType, которые будем разбирать отдельно:

```text
Link
Dynamic Link
Child Table
Single
Tree
Submittable
Virtual DocType
```

Это фундамент Frappe.

Любое Frappe-приложение строит свои сущности поверх этой модели.

---

## 4. Хранение данных и ORM

Framework предоставляет серверную модель работы с Documents и БД.

Например:

```python
frappe.get_doc(...)
frappe.get_list(...)
frappe.get_all(...)
frappe.db.get_value(...)
```

Поэтому App обычно не пишет собственный общий ORM для каждой сущности.

Предметное приложение добавляет **какие данные хранить**, а Framework предоставляет **как с Documents работать**.

---

## 5. Desk

В чистый Framework входит Desk — основной интерфейс системного пользователя.

Framework предоставляет основу для:

```text
Form View
List View
Report View
Workspace
Kanban
Calendar
Gantt
Tree View
```

Конкретное приложение добавляет свои DocTypes, Reports, Workspaces и другие объекты, которые Desk затем показывает.

То есть:

```text
Desk
= Framework

конкретный экран "Sales Order"
= ERPNext
```

---

## 6. Пользователи и authentication

Framework содержит универсальную систему пользователей и аутентификации.

К этому уровню относятся, среди прочего:

```text
User
login
sessions
roles
password/auth mechanisms
API authentication mechanisms
```

Отдельное приложение может использовать этих пользователей, но ему не требуется создавать собственную базовую систему login только потому, что оно является новым App.

---

## 7. Roles и Permissions

В Framework входят общие механизмы доступа:

```text
Role
Role Permission Manager
DocType permissions
Permission Level
User Permission
Owner-based permissions
Sharing
```

Приложение определяет:

```text
какие роли нужны его предметной области
какие permissions назначить его DocTypes
```

Но сам permission engine — часть Framework.

---

## 8. Workflow

`Workflow` и связанные механизмы являются универсальной возможностью Framework.

Приложение может использовать Workflow для собственных Documents.

Например, Framework умеет проверять состояния, переходы, роли и условия, но он сам не знает, что в конкретном приложении означает:

```text
Approved
Rejected
Paid
Closed
```

Это уже предметный смысл приложения.

---

## 9. Assignment и ToDo

В Frappe имеются штатные механизмы:

```text
ToDo
Assign To
Assignment Rule
```

Они могут использоваться любыми DocTypes.

Но наличие `ToDo` не означает, что Frappe является готовой системой управления проектами или helpdesk.

Это универсальный строительный блок.

---

## 10. Notifications

Framework предоставляет generic-механизм `Notification`.

Он позволяет реагировать на события и условия Documents и отправлять уведомления через поддерживаемые каналы.

Но это не то же самое, что полноценный предметный notification center конкретного специализированного продукта.

---

## 11. Auto Repeat

Framework содержит generic-механизм повторного создания Documents.

Он может применяться к подходящим DocTypes.

Сам механизм — инфраструктурный.

То, **что именно повторяется**, определяет приложение.

---

## 12. Timeline, Comments и Version

В Framework есть общая document-инфраструктура для:

```text
comments
timeline
versioning / track changes
activity around documents
```

Это не означает, что Framework содержит предметный журнал аудита любой бизнес-операции.

Он предоставляет общую техническую основу истории Document.

---

## 13. Files и Attachments

Framework умеет работать с `File` и вложениями Documents.

То есть возможность:

> приложить файл к записи

— не требует установки отдельной системы хранения документов.

Но это не значит, что чистый Framework является аналогом Frappe Drive.

Разница:

```text
File / Attachments
= базовый механизм Framework

Drive
= отдельное приложение для полноценной работы с файлами и совместным хранилищем
```

---

## 14. Email

Frappe Framework имеет встроенную email-инфраструктуру.

Она используется для отправки и получения почты, Communications и связи сообщений с Documents.

Но важно различать:

```text
email infrastructure
= Framework

Newsletter
= отдельный функциональный модуль/App в v16
```

В Frappe 16 Newsletter больше не следует считать частью чистого Framework.

---

## 15. Printing и PDF

Framework предоставляет:

```text
Print Format
Print Format Builder
Jinja templates
PDF generation infrastructure
```

Поэтому прикладной App может иметь печатные формы, не создавая собственный универсальный print engine.

Содержание конкретного документа — предмет приложения.

Print infrastructure — Framework.

---

## 16. Reports

Framework предоставляет несколько уровней отчётности:

```text
Report Builder
Query Report
Script Report
Dashboard Chart
Number Card
```

Это универсальная reporting infrastructure.

Но:

```text
Frappe Reports
≠ Frappe Insights
```

`Frappe Insights` — отдельный аналитический продукт.

Встроенные отчёты Framework подходят для прикладной отчётности внутри Frappe Apps, но не превращают чистый Framework в отдельную BI-платформу.

---

## 17. Import и Export

Framework содержит generic-механизмы импорта и экспорта данных для DocTypes.

Поэтому простая задача:

```text
загрузить Documents из CSV/Excel-подобного шаблона
```

не означает автоматически необходимость писать отдельный импортёр.

Специализированный ETL, сложное сопоставление внешних схем или потоковая интеграция — уже другая задача.

---

## 18. REST API

REST API для DocTypes — штатная возможность Framework.

Приложение, создавая DocType, получает базовую HTTP-инфраструктуру работы с Documents.

Это принципиальная особенность Frappe:

```text
модель приложения
      ↓
Framework API
```

а не необходимость вручную писать CRUD endpoint для каждой сущности.

---

## 19. RPC и whitelisted methods

Framework предоставляет механизм вызова whitelisted Python methods через HTTP.

Это generic RPC-инфраструктура.

Сам метод и его предметная логика уже принадлежат приложению.

---

## 20. Web Forms и website-механизмы

В Framework существуют web-возможности, включая Web Forms и инфраструктуру website/portal-разработки.

Поэтому простой внешний ввод данных может быть реализован без отдельного SPA.

Но наличие web infrastructure не означает, что в чистом Framework входит каждый специализированный website-продукт Frappe.

Например визуальный website builder — отдельный продукт.

---

## 21. Background Jobs

Framework предоставляет фоновые очереди и API для постановки jobs.

Например:

```python
frappe.enqueue(...)
```

Сам Framework решает инфраструктурную задачу:

```text
поставить работу в очередь
выполнить worker-ом
```

Приложение определяет, **какую работу выполнить**.

---

## 22. Scheduler

Framework имеет scheduler и scheduler events.

То есть приложение может регистрировать периодические задачи без написания собственного общего cron engine.

Но конкретная периодическая бизнес-операция принадлежит App.

---

## 23. Realtime

Frappe содержит realtime-инфраструктуру.

Приложение может публиковать события и обновлять интерфейс без постоянного polling.

Это generic Framework capability.

---

## 24. Bench

Bench относится к инфраструктуре экосистемы Frappe и используется для управления:

```text
Apps
Sites
migrations
processes
backup
configuration
```

Bench не является предметным приложением для конечного пользователя.

---

## 25. App system и hooks

В Framework входит сама модель расширения платформы:

```text
App
hooks.py
controllers
fixtures
patches
migrations
extensions
```

Именно поэтому поверх Frappe можно создавать отдельные приложения без форка Framework.

---

# Часть II. Что НЕ следует считать частью чистого Framework

## 26. ERPNext

ERPNext — отдельное приложение/набор бизнес-модулей на Frappe.

Такие понятия, как:

```text
Customer
Supplier
Sales Order
Purchase Order
Invoice
Stock Entry
Warehouse
BOM
Accounting Ledger
```

не являются универсальными сущностями чистого Framework.

Они приходят из ERPNext.

Даже если их интерфейс выглядит как обычный Frappe Desk, это не делает их частью Framework.

---

## 27. Frappe CRM

Frappe CRM — отдельное приложение.

Следовательно, специализированные сущности и UX CRM нельзя автоматически относить к Framework.

Framework даёт строительные блоки, на которых CRM реализована.

CRM App добавляет предметную модель customer relationship management.

---

## 28. Frappe Helpdesk

Helpdesk — отдельное приложение.

Ticketing, SLA-модель, агентский интерфейс и другие специализированные helpdesk-сценарии не следует принимать за возможности чистого Framework.

При этом Helpdesk сам использует базовые возможности Frappe.

---

## 29. Frappe HR / HRMS

HR и payroll — предметная область отдельного приложения.

Такие сущности, как:

```text
Employee
Leave
Attendance
Payroll
Shift
```

не надо считать базовыми сущностями Framework только потому, что они существуют в Frappe-экосистеме.

---

## 30. Frappe Learning

LMS-функциональность — отдельный продукт.

Курсы, уроки, обучение и специализированный учебный UX не являются generic-возможностями Framework.

---

## 31. Frappe Insights

Insights — отдельный аналитический продукт.

Нужно различать:

```text
встроенные Reports / Charts
= Framework

полноценное специализированное BI-приложение
= Insights
```

---

## 32. Frappe Builder

Builder — отдельное приложение для визуального построения сайтов.

Наличие website и Web Form infrastructure в Framework не означает, что весь Builder встроен в Framework.

---

## 33. Frappe Wiki

Wiki — отдельное приложение.

Framework сам по себе не становится готовой wiki-системой только потому, что умеет хранить Documents и рендерить web-страницы.

---

## 34. Frappe Drive

Drive — отдельное приложение.

Framework имеет `File` и attachments, но специализированное файловое рабочее пространство и совместная работа с файлами — другая функциональность.

---

# Часть III. Особенно важные изменения v16

## 35. Некоторые модули были вынесены из `frappe`

В migration guide Frappe 16 отдельно указано, что из core были вынесены дополнительные модули:

```text
Energy Points
Newsletter
Backup Integrations
Blog
```

Это важно при чтении старых гайдов.

Если в старом материале говорится:

> Frappe имеет встроенный Blog

для v16 это уже нельзя принимать как корректное описание чистого Framework.

---

## 36. Почему модули вообще выносят из core

Это помогает лучше понять архитектурную границу.

Условно существуют два типа возможностей:

### Generic infrastructure

Полезна почти любому database-driven приложению:

```text
DocType
permissions
Desk
API
jobs
printing
```

Ей логично находиться в Framework.

### Domain/product functionality

Нужна только определённому типу продукта:

```text
newsletter campaign
blog
CRM pipeline
helpdesk SLA
payroll
accounting
```

Её логичнее держать в отдельном App.

Граница не абсолютно неподвижна — состав Framework меняется между версиями.

Именно поэтому курс фиксируется на **v16**, а не на абстрактном «Frappe вообще».

---

# Часть IV. Главные пары, которые нельзя путать

## 37. Desk ≠ ERPNext UI

```text
Desk
= Framework shell/interface

ERPNext screens
= предметные Documents и Workspaces внутри этого интерфейса
```

---

## 38. File ≠ Drive

```text
File / Attachments
= Framework

Drive
= отдельное App
```

---

## 39. Reports ≠ Insights

```text
Report Builder / Query Report / Script Report
= Framework

Insights
= отдельное App
```

---

## 40. Web Forms ≠ Builder

```text
Web Form / website infrastructure
= Framework

visual website builder
= отдельное App
```

---

## 41. Email ≠ Newsletter

```text
email / Communication infrastructure
= Framework

Newsletter в v16
= вынесенный функциональный модуль/App
```

---

## 42. ToDo / Assignment ≠ Project Management App

```text
ToDo / Assign To
= generic Framework capability

полноценная проектная модель
= предметное приложение
```

---

## 43. Workflow ≠ готовый бизнес-процесс

```text
Workflow engine
= Framework

конкретные состояния, роли и правила процесса
= App configuration / business model
```

---

## 44. User ≠ Employee

Это особенно частая путаница.

```text
User
= техническая учётная запись Framework

Employee
= предметная HR-сущность отдельного приложения
```

Один пользователь Framework не обязан автоматически означать сотрудника HR-системы.

---

# Часть V. Как определять границу самостоятельно

## 45. Проверка №1 — документация

Сначала смотрим, в каком разделе документации находится функция.

Если URL и navigation относятся к:

```text
/framework/
```

это сильный признак Framework functionality.

Если документация относится к:

```text
/erpnext/
/crm/
/helpdesk/
...
```

это уже документация отдельного продукта.

Но одной структуры сайта недостаточно для сложных случаев — при необходимости проверяем исходный код.

---

## 46. Проверка №2 — установлен ли отдельный App

Очень практичный вопрос:

> будет ли эта сущность существовать на чистом Site, где установлен только `frappe`?

Если нет — скорее всего это не часть Framework.

Например:

```text
User       → да
DocType    → да
ToDo       → да
Workflow   → да

Sales Order → нет без ERPNext
Ticket      → не означает Helpdesk ticket без Helpdesk App
Employee    → не следует считать базовой HR-сущностью Framework
```

---

## 47. Проверка №3 — исходный код

Если документация не даёт уверенного ответа, смотрим репозиторий `frappe/frappe`.

Если DocType, API или механизм находится непосредственно в Framework codebase — это подтверждает его принадлежность core.

Если он находится в репозитории отдельного приложения — это App functionality.

---

## 48. Проверка №4 — generic или domain-specific

Хороший эвристический вопрос:

> эта возможность нужна почти любому web-приложению или только конкретной предметной области?

Например:

```text
permissions
→ generic

accounts receivable
→ domain-specific

REST API
→ generic

sales pipeline
→ domain-specific
```

Это не заменяет проверку документации, но помогает быстро ориентироваться.

---

# Часть VI. Карта чистого Frappe Framework 16

## 49. Упрощённая функциональная карта

Для стартового понимания чистый Framework можно представить так:

```text
FRAPPE FRAMEWORK 16
│
├── DATA MODEL
│   ├── DocType
│   ├── DocField
│   ├── Document
│   ├── Links
│   └── Child Tables
│
├── DESK / UI
│   ├── Workspace
│   ├── Form
│   ├── List
│   ├── Report
│   ├── Kanban
│   ├── Calendar
│   ├── Gantt
│   └── Tree
│
├── SECURITY
│   ├── User
│   ├── Role
│   ├── Permissions
│   ├── User Permission
│   └── Sharing
│
├── PROCESS MECHANICS
│   ├── Workflow
│   ├── ToDo / Assignment
│   ├── Assignment Rule
│   ├── Notification
│   └── Auto Repeat
│
├── DOCUMENT SERVICES
│   ├── Timeline
│   ├── Comments
│   ├── Version
│   ├── File / Attachments
│   ├── Communication / Email
│   └── Printing
│
├── DATA ACCESS
│   ├── ORM
│   ├── Database API
│   ├── Import / Export
│   ├── REST API
│   └── RPC
│
├── REPORTING
│   ├── Report Builder
│   ├── Query Report
│   ├── Script Report
│   ├── Charts
│   └── Number Cards
│
├── WEB
│   ├── Web Forms
│   └── website / portal infrastructure
│
├── SERVER RUNTIME
│   ├── Background Jobs
│   ├── Scheduler
│   ├── Realtime
│   └── Cache / supporting services
│
└── APP DEVELOPMENT
    ├── Controllers
    ├── Hooks
    ├── Fixtures
    ├── Patches
    ├── Migrations
    └── Tests
```

Это пока не полный справочник каждого внутреннего модуля Frappe.

Это **карта функциональных возможностей**, которой достаточно, чтобы понимать границу платформы.

---

# Часть VII. Что должен вынести новичок

## 50. Главное правило

Нельзя делать вывод о возможностях Framework по интерфейсу установленного Frappe-продукта.

Нужно всегда мысленно разделять:

```text
FRAMEWORK
универсальные механизмы

APP
предметные сущности и процессы
```

---

## 51. Пример разбора

Допустим, в какой-то системе на Frappe мы видим:

```text
Ticket
Assignee
Status
SLA
Comments
Attachments
Email
```

Не всё это обязательно реализовано одним уровнем.

Возможная структура:

```text
Ticket
SLA
часть status-модели
→ Helpdesk App

User
Assignment / ToDo
Comments
Attachments
Email infrastructure
→ Frappe Framework
```

Вот именно так дальше нужно анализировать любое Frappe-приложение.

---

## 52. Контрольные вопросы

После этой главы нужно уметь ответить:

1. Почему ERPNext не равен Frappe Framework?
2. Является ли `User` сущностью Framework?
3. Является ли `Employee` универсальной сущностью Framework?
4. Чем `File` отличается от Frappe Drive?
5. Чем встроенные Reports отличаются от Frappe Insights?
6. Почему наличие ToDo не делает Frappe готовым task tracker?
7. Является ли Workflow готовым бизнес-процессом?
8. Какие четыре модуля были вынесены из `frappe` в v16?
9. Как проверить принадлежность спорной функции к Framework?
10. Почему старый гайд по Frappe может ошибочно описывать состав v16?

Если эти ответы ясны, можно переходить к центральной теме всего Framework — **DocType**.

---

## Официальные источники

- [Frappe Framework — Introduction](https://docs.frappe.io/framework/user/en/introduction)
- [What is Frappe Framework?](https://docs.frappe.io/framework/user/en/basics)
- [Why Frappe Framework?](https://docs.frappe.io/framework/user/en/basics/why)
- [Frappe Framework Guides](https://docs.frappe.io/framework/user/en/guides)
- [Frappe Apps Documentation](https://docs.frappe.io/)
- [Migrating to Version 16](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)

---

Следующая глава: **04. DocType от А до Я: центральная модель Frappe**.