# Матрица базового практикума Frappe Framework 16

Матрица фиксирует обязательную последовательность базового уровня. Единица обучения — **осмысленный прирост одного сквозного продукта**, а не отдельная кнопка, API-метод или синтаксическая конструкция.

## Условия уровня

- основа — штатные возможности Frappe Framework 16;
- собственный App создаётся нативно через `bench new-app`;
- продукт живёт в собственном App и Module;
- сначала используется декларативный штатный механизм Frappe;
- встроенный low-code применяется только как естественное расширение штатной функции;
- допустимы Client Script, Server Script, Query Report, custom Script Report, expressions, Jinja, Webhook и другие встроенные scripting-поверхности;
- не используется полноценная файловая разработка собственной бизнес-логики на Python/JS;
- не используются controllers, hooks, patches, overrides, custom frontend и другие developer-level расширения App;
- терминал используется для штатной работы Bench/App/Site;
- Git используется как нормальный способ хранения и переноса собственного App.

## Практические работы

| № | Практическая работа | Входное состояние | Что добавляем | Штатные возможности Frappe | Контрольный результат |
|---:|---|---|---|---|---|
| **00** | **Развернуть чистый Frappe 16** | Чистая Linux-система | Рабочий учебный стенд | официальные зависимости v16, MariaDB, Redis/Valkey, Bench, Site, `bench start`, Desk | Site открывается; Administrator входит в Desk; стенд корректно перезапускается |
| **01** | **Освоиться в Frappe 16** | Пустой Site | Базовая конфигурация и понимание платформы | Desk, Desktop v16, Workspace Sidebar, Awesome Bar, System Settings, timezone, форматы, sessions, основные журналы | ученик ориентируется в Site и понимает назначение Bench, Site, App, Module, DocType и Document |
| **02** | **Создать собственный App** | Рабочий Site | `frappe_practicum` и Module `Practicum` | `bench new-app`, структура App, Module, `install-app`, `list-apps`, Git, `bench migrate` | App создан, установлен на Site, находится в Git; дальнейшие стандартные объекты принадлежат Practicum |
| **03** | **Создать первый DocType** | Пустой Practicum App | `Work Item` | DocType, DocField, Document, Form View, List View, стандартные системные поля, CRUD | можно создать, открыть, изменить, скопировать и удалить Work Item |
| **04** | **Построить рабочую карточку** | Минимальный Work Item | Рабочие поля и структура формы | основные Field Types, Geolocation, Attach, mandatory/default/read-only/unique/hidden, Section/Column/Tab Break, Quick Entry, list/filter properties | Work Item имеет статус, приоритет, даты, описание, Location и пригодную форму |
| **05** | **Настроить идентификацию и поиск** | Рабочая карточка | Удобные имена и поиск | naming, naming series/field naming, Title Field, Search Fields, Allow Rename, list/preview properties | документы получают понятные идентификаторы и находятся по рабочим данным |
| **06** | **Построить связанную модель** | Один самостоятельный DocType | `Project`, `Work Item Step`, `Practicum Settings` и связи | Link, Fetch From, Dynamic Link, Child DocType, Table, Single DocType, Files, Connections | Work Item связан с Project, содержит checklist, файлы и использует общие настройки |
| **07** | **Добавить иерархический справочник** | Модель без Category | `Category` как Tree DocType | Tree DocType, parent-child hierarchy, Tree View, Link на Tree DocType | Category работает как дерево и используется в Work Item |
| **08** | **Освоить lifecycle и аудит** | Есть обычные рабочие DocTypes | `Work Approval` [Submittable] | Draft, Submit, Cancel, Amend, Allow on Submit, Track Changes, Version, Timeline, Audit Trail | Work Approval проходит полный lifecycle; Work Item остаётся обычным рабочим документом |
| **09** | **Освоить штатные представления** | Накоплены Work Items | Несколько способов работы с одними данными | List View, filters, sorting, tags, bulk actions, Report View, Kanban, Calendar View, Calendar, Gantt где доступен, Tree View, Map View | один набор Documents используется через несколько штатных views |
| **10** | **Собрать Workspace** | Есть модель и views | Рабочее место пользователя | Workspace, Cards/Links, Shortcuts, Quick List, Onboarding, public/private Workspace, Sidebar v16 | пользователь получает единый рабочий вход в Practicum |
| **11** | **Добавить пользователей и роли** | Работа только Administrator | Несколько реальных пользователей | User, System User, Role, Role Profile, module access, default Workspace | минимум три Desk User работают под собственными ролями |
| **12** | **Настроить штатные permissions** | Пользователи видят одинаково | Базовая модель доступа | Role Permission Manager; CRUD; Submit/Cancel/Amend; Report/Export/Import/Share/Print/Email; Permission Level; If Owner; User Permission; Share; Page/Report permissions | роли реально получают разные Documents, поля и действия; проверка выполняется не Administrator |
| **13** | **Организовать совместную работу** | Documents без рабочего взаимодействия | Поручения и коммуникация | Assign, ToDo, priority, due date, Comments, Mentions, Tags, Following, Attachments, Timeline, Track Seen/Views, Share | Work Item назначается исполнителю и становится центром совместной работы |
| **14** | **Автоматизировать назначения** | Assign выполняется вручную | Assignment Rule | Round Robin, Load Balancing, Based on Field, Due Date Based On, штатные conditions | новые Work Items распределяются автоматически; простое условие ограничивает применение правила |
| **15** | **Построить Workflow** | Есть users, roles и permissions | Управляемый процесс Work Item | Workflow State, Workflow, transitions, allowed roles, штатные transition conditions, Workflow Actions | Work Item проходит `Новая → В работе → На проверке → Завершена/На доработку` |
| **16** | **Настроить Notifications** | Workflow не информирует участников | Событийные и срочные уведомления | Notification, Document Event, Value Change, date-based event, recipients, штатные conditions, System Notification | пользователи получают системные уведомления только при нужных условиях |
| **17** | **Добавить повторяемую работу** | Work Items создаются вручную | Регулярные документы | Allow Auto Repeat, Auto Repeat, frequency, start/end dates | Frappe самостоятельно создаёт повторяемые Work Items |
| **18** | **Освоить штатную кастомизацию** | Известны собственные DocTypes | Изменение существующей конфигурации без правки core | Customize Form, Custom Field, Property Setter, Custom DocPerm, Custom Link, Route Action, DocType Layout | форма, links/actions, права и layout меняются штатным customization layer |
| **19** | **Добавить клиентское поведение** | Декларативные возможности формы уже понятны | Минимальный Client Script | Client Script для Form/List, field events, `frm.set_value`, field properties, buttons, filters; граница client-side validation | Work Item получает полезное интерактивное поведение, которое нельзя было выразить проще metadata-настройкой |
| **20** | **Добавить серверные правила без controller-кода** | Client-side граница понятна | Server Script: DocType Event | Script Manager, restricted Python, DocType Event, server-side validation/автозаполнение, обработка ошибок | правило работает и через Desk, и при обходе браузерного Client Script |
| **21** | **Освоить встроенную серверную автоматизацию** | Server Script уже знаком | Scheduler Event и Permission Query | Server Script Scheduler Event, frequency/Cron на базовом уровне, Permission Query; журналы выполнения | периодическая автоматизация выполняется без hooks; дополнительное permission-ограничение действует на сервере |
| **22** | **Освоить массовую работу с данными** | Есть стабильная модель | Массовая загрузка и выгрузка | Data Export, Data Import, template, Insert, Update, child data, validation/import errors, bulk operations | массив Work Items импортируется, обновляется и экспортируется обратно |
| **23** | **Построить отчётность штатной лестницей** | Накоплены данные | Три уровня отчётности | Report Builder → Query Report → Custom Script Report; filters, grouping, aggregates, SQL внутри Query Report, restricted script внутри custom Report | ученик понимает, когда достаточно builder, когда нужен SQL, а когда нужен встроенный script report, не создавая файловый Standard Script Report |
| **24** | **Собрать Dashboard и аналитику Workspace** | Есть отчёты | Управленческий экран | Number Card, Dashboard Chart, Dashboard/Workspace analytics, filters/aggregates, role access | ключевые показатели встроены в ранее созданный Workspace |
| **25** | **Настроить печать от Builder до Jinja** | Work Item существует в интерфейсе | Человекочитаемый документ | Standard Print, Print Format Builder, Letter Head, Print Settings, PDF, custom Print Format с Jinja и минимальным HTML/CSS | один документ выводится стандартно, через builder и через Jinja-шаблон; понятна граница каждого уровня |
| **26** | **Подключить Email** | System Notification уже работает | Email как часть Document history | Email Account, Send Email, Communication, Email Queue, Email Template, attachments/PDF, Email Notification | письмо отправляется из Work Item, сохраняется в истории, Notification умеет отправлять Email |
| **27** | **Создать штатную Website-страницу** | Продукт пока существует только в Desk | Внешняя информационная страница | Website Settings, Web Page/Page Builder и штатные website-настройки без файлового portal-кода | у Practicum появляется публичная страница, созданная штатными средствами Frappe |
| **28** | **Создать Web Form** | Website уже знаком | Внешний пользовательский сценарий | Website User, Web Form, layout, multi-step, permissions, list/edit/comments/attachments/print, встроенные CSS/Client Script/validation | внешний пользователь создаёт и обслуживает свои Work Items без Desk |
| **29** | **Освоить штатный REST API и low-code API** | Desk и Web Form работают | Два уровня API | API User, API Key/Secret, автоматический REST CRUD v1/v2, filters/pagination/permissions; Server Script API, Allow Guest и встроенный rate limiting | внешний клиент использует стандартный CRUD и отдельный low-code endpoint без файлового Python method |
| **30** | **Настроить исходящую интеграцию** | API-модель понятна | Webhook | DocType Event, condition, URL, method, headers, fields/JSON, Jinja payload, secret/HMAC, журнал ошибок | изменение Work Item отправляет контролируемый запрос во внешний тестовый endpoint |
| **31** | **Связать Workflow с действиями v16** | Workflow, Server Script и Webhook уже изучены | Workflow Transition Tasks | Workflow Transition Task, Server Script/Webhook action, sync/async поведение | переход Workflow запускает штатное действие; ученик видит границу между transition и side effect |
| **32** | **Разобрать Package как отдельный stock-механизм** | Есть обычный App-проект | Lightweight/UI-created packaging | Package, Custom Module, Package Release/Import, сравнение с обычным Frappe App | ученик понимает, когда Package уместен и почему основной учебный продукт всё равно живёт в обычном App |
| **33** | **Воспроизвести App на втором Site** | App полностью собран | Чистая установка продукта | Git clone/get-app в подходящем учебном сценарии, install-app, migrate, проверка стандартных объектов | второй Site получает Practicum App штатным способом; конфигурация воспроизводится из репозитория |
| **34** | **Резервировать и восстанавливать Site** | Первый Site содержит конфигурацию, данные и файлы | Восстанавливаемость | Bench backup, public/private files, restore, проверка Site data/config | после restore сохраняются Users, Documents, Files, настройки и рабочий процесс |
| **35** | **Пройти финальный сквозной сценарий** | Все механизмы настроены | Цельный рабочий продукт | совместное использование всех основных возможностей практикума | после restore проходит полный сценарий от Web Form до Workflow, Notifications, reports, print/email, API/Webhook; второй Site воспроизводит App из Git |

---

# Контрольная матрица покрытия базового native-first уровня

| Область | Работы |
|---|---|
| Bench / Site | 00, 34 |
| Desk / Desktop / Sidebar / Awesome Bar | 01, 10 |
| `bench new-app` / App / Module / install-app / Git | 02, 33 |
| DocType / Document / CRUD | 03 |
| DocField / Field Types / form layout / Geolocation | 04 |
| Naming / title / search | 05 |
| Link / Fetch / Dynamic Link / Child / Single / Files / Connections | 06 |
| Tree DocType / Tree View | 07, 09 |
| Submit / Cancel / Amend / Allow on Submit / Audit Trail | 08 |
| List / Report View / Kanban / Calendar / Gantt / Map | 09 |
| Workspace / Onboarding | 10, 24 |
| User / Role / Role Profile | 11 |
| Role Permissions / Permission Level / User Permission / Share | 12 |
| Assign / ToDo / Comments / Mentions / Tags / Following | 13 |
| Assignment Rule + conditions | 14 |
| Workflow + conditions / Workflow Actions | 15 |
| Notification + conditions | 16, 26 |
| Auto Repeat | 17 |
| Customize Form / Property Setter / Custom Field / Actions / Links / DocType Layout | 18 |
| Client Script | 19, 28 |
| Server Script: DocType Event | 20 |
| Server Script: Scheduler / Permission Query | 21 |
| Data Import / Export | 22 |
| Report Builder | 23 |
| Query Report | 23 |
| Custom Script Report | 23 |
| Number Card / Dashboard Chart / Workspace analytics | 24 |
| Print Builder / Jinja / PDF / Letter Head | 25 |
| Email / Communication / Email Queue / Email Template | 26 |
| Website Settings / Web Page | 27 |
| Web Form / Website User / Web Form scripting | 28 |
| REST API v1/v2 | 29 |
| Server Script API / rate limiting | 29 |
| Webhook | 30 |
| Workflow Transition Tasks v16 | 31 |
| Package / Package Release / Import | 32 |
| Git-based App reproduction / migrate | 33 |
| Backup / Restore | 34 |
| Сквозной итоговый сценарий | 35 |

---

# Критерий native-first для каждой работы

Перед использованием low-code работа обязана показать, почему более простой механизм уже недостаточен.

Правильная последовательность решения:

```text
metadata / настройка
        ↓
готовый штатный DocType-механизм
        ↓
встроенный expression
        ↓
Client Script / Server Script / Query / Jinja
        ↓
[граница базового уровня]
        ↓
файловый app-код
```

Практическая работа считается завершённой только если ученик:

1. получил ожидаемый рабочий результат;
2. понимает, почему выбран именно этот штатный механизм;
3. проверил permissions правильным пользователем;
4. намеренно изменил одну настройку и увидел последствия;
5. вернул проект в корректное состояние;
6. может назвать более простой и более сложный слой решения;
7. не заменил штатную возможность ненужным script-кодом.