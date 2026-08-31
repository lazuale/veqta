# Матрица базового практикума Frappe Framework 16

Матрица фиксирует обязательную последовательность базового уровня. Единица обучения — не отдельная кнопка или API-метод, а **осмысленный прирост одного сквозного no-code проекта**.

## Условия уровня

- только штатные возможности Frappe Framework 16;
- без Python;
- без JavaScript;
- без SQL;
- без Server Script и Client Script;
- без ручного Jinja/HTML/CSS как разработки;
- без произвольных Python/JavaScript-условий и выражений в настройках;
- без собственного Frappe App;
- проект организуется через Package + Custom Module;
- терминал используется только для установки и штатного администрирования;
- Postman/`curl` используются только для проверки автоматически предоставляемого REST API.

## Практические работы

| № | Практическая работа | Входное состояние | Что добавляем в проект | Штатные возможности | Контрольный результат |
|---:|---|---|---|---|---|
| **00** | **Развернуть чистый Frappe 16** | Чистая Linux-система | Рабочий учебный стенд | официальные зависимости v16, MariaDB, Redis/Valkey, Bench, Site, `bench start`, Desk | Site открывается; Administrator входит в Desk; стенд корректно останавливается и запускается повторно |
| **01** | **Освоиться в Frappe 16** | Пустой Site | Базовая конфигурация и понимание навигации | Desk, Desktop v16, Workspace Sidebar v16, Awesome Bar, System Settings, язык, timezone, форматы, sessions, login/password settings, основные журналы | ученик самостоятельно находит системную настройку, DocType, пользователя, Workspace и журнал |
| **02** | **Создать контейнер no-code проекта** | Настроенный пустой Site | `Package: Frappe Practicum` и `Custom Module: Practicum` | Package, Custom Module / Module Def, связь Module с Package | появляется отдельный штатный контейнер проекта; дальнейшие Custom DocTypes создаются в модуле Practicum |
| **03** | **Создать первый рабочий объект** | Package и Custom Module готовы | `Work Item` | Custom DocType, Document, Form View, List View, стандартные системные поля, CRUD | можно создать, открыть, изменить, скопировать и удалить Work Item; он относится к модулю Practicum |
| **04** | **Построить нормальную карточку Work Item** | Минимальный Work Item | Рабочие поля и форма | базовые Field Types: Data, Text/Small Text/Text Editor, Select, Check, Int/Float/Currency/Percent, Date/Datetime/Time/Duration, Attach, Geolocation; mandatory, default, read-only, unique, hidden; Section/Column/Tab Break; Quick Entry; list/filter properties | форма логична; ограничения работают; у Work Item есть Start Date, Due Date и Location для будущих представлений |
| **05** | **Настроить идентификацию и поиск** | Карточка без удобной идентификации | Удобные имена и поиск | naming, naming series/field naming, Title Field, Search Fields, Allow Rename, list/preview properties | документы имеют понятные идентификаторы и находятся по рабочим данным |
| **06** | **Построить связанную модель данных** | Один самостоятельный DocType | `Project`, `Work Item Step`, `Practicum Settings` и связи | Link, Fetch From, Dynamic Link, Child DocType, Table, Single DocType, File/Attachments, Connections | Work Item связан с Project, содержит checklist, может хранить файлы и использует общие настройки |
| **07** | **Добавить иерархический справочник** | Модель без Category | `Category` сразу как Tree DocType и связь с Work Item | Tree DocType / Is Tree, parent-child hierarchy, Tree View, Link на Tree DocType | категории создаются и просматриваются как дерево; Work Item связывается с выбранной Category |
| **08** | **Освоить lifecycle и аудит документов** | Есть обычные рабочие DocTypes | Отдельный `Work Approval` для подтверждаемого сценария | Is Submittable, Draft, Submit, Cancel, Amend, Allow on Submit, Track Changes, Version, Timeline, Audit Trail | Work Approval проходит полный lifecycle; после amend изменения сравниваются через Audit Trail; Work Item остаётся обычным рабочим документом |
| **09** | **Освоить штатные представления** | Накоплены Work Items с датами, статусами, Location и Category | Несколько способов работы с одними данными | List View, filters, sorting, paging, columns, tags/filter by tags, bulk actions, Report View, Kanban, Calendar View DocType, Calendar, Gantt где доступен штатно, Tree View, Map View | один набор Documents используется через список, доску, календарь, карту и другие доступные штатные views без изменения модели |
| **10** | **Собрать рабочее место пользователя** | Есть DocTypes и views | Единый вход в учебную систему | Workspace, Heading, Text, Cards/Links, Shortcuts, Quick List, Onboarding, public/private Workspace, Workspace Sidebar v16; без Number Card/Chart до аналитической фазы | пользователь получает цельный рабочий экран и навигацию; основные DocTypes и представления доступны из Workspace |
| **11** | **Добавить реальных Desk-пользователей** | Работа только Administrator | Пользователи и роли | User, System User, Role, Role Profile, module access, default Workspace, пользовательские настройки | минимум три обычных Desk User работают под собственными учётными записями и ролями |
| **12** | **Разграничить права** | Пользователи видят систему одинаково | Реальная модель доступа | Role Permission Manager; Read, Write, Create, Delete, Submit, Cancel, Amend, Report, Export, Import, Share, Print, Email; Permission Level; If Owner; User Permission; Share; Page/Report permissions | разные роли реально видят разные Documents, поля и действия; проверка выполняется под обычными пользователями, не Administrator |
| **13** | **Организовать совместную работу** | Documents без рабочего взаимодействия | Поручения, обсуждение и наблюдаемость | Assign, ToDo, priority, due date, Comments, Mentions, Attachments, Timeline, Version, Tags, Following, Track Seen, Track Views, Share | пользователь назначает Work Item другому; исполнитель получает ToDo; обсуждение, просмотры и изменения видны штатными средствами |
| **14** | **Автоматизировать распределение работы** | Назначения выполняются вручную | Автоматическое назначение | Assignment Rule, Round Robin, Load Balancing, Based on Field, Due Date Based On — без script conditions | новые Work Items автоматически распределяются между пользователями без собственного кода |
| **15** | **Построить Workflow** | Есть users, roles, permissions и рабочий Work Item | Управляемый процесс | Workflow State, Workflow, transitions, allowed roles, Workflow Actions — без кодовых transition conditions | Work Item проходит `Новая → В работе → На проверке → Завершена/На доработку`; переходы доступны правильным ролям |
| **16** | **Настроить системные уведомления** | Workflow не информирует участников автоматически | Уведомления внутри Frappe | Notification на штатных Document Event / Value Change / date-based событиях, recipients по пользователям/ролям/полям, System Notification; без script conditions и без Email channel до настройки почты | пользователь получает системное уведомление по событию и напоминание по сроку без собственного кода |
| **17** | **Добавить повторяемую работу** | Work Items создаются вручную | Регулярные документы | Allow Auto Repeat, Auto Repeat, frequency, start/end dates | Frappe самостоятельно создаёт следующий повторяемый Work Item |
| **18** | **Освоить штатную кастомизацию** | Известно создание собственных Custom DocTypes | Изменение уже существующей конфигурации без исходного кода | Customize Form, Custom Field, Property Setter, Custom DocPerm, Custom Link, Route Action без Server Action, DocType Layout без JS condition; привязка Layout к ссылке Workspace | существующая форма и права меняются через customization layer; создаётся альтернативный layout и открывается из Workspace без кода |
| **19** | **Освоить массовую работу с данными** | Данные вводятся в основном вручную | Массовая загрузка и выгрузка | Data Export, Data Import, import template, Insert, Update, child data, validation/import errors, bulk operations где применимо | массив Work Items импортируется, обновляется и экспортируется обратно; ошибки импорта читаются и исправляются |
| **20** | **Построить отчётность без кода** | Накоплены рабочие данные | Пользовательские отчёты | Report Builder, columns, filters, sorting, Group By, Count/Sum/Average, child records, saved reports, print/export actions | пользователь самостоятельно собирает несколько рабочих отчётов без SQL |
| **21** | **Собрать Dashboard и встроить аналитику в Workspace** | Есть данные и Report Builder | Управленческий экран | Number Card, Dashboard Chart, Dashboard/Workspace analytics, filters/aggregates, role access, добавление Number Card/Chart в ранее созданный Workspace | на одном экране видны ключевые показатели: открытые, просроченные, распределение по статусам; аналитика появляется в Workspace только после её создания |
| **22** | **Настроить печать** | Work Item существует только в интерфейсе | Человекочитаемый внешний документ | Standard Print View, Print Format Builder, Letter Head, Print Settings, PDF, default Print Format; без ручного HTML/Jinja | из Work Item получается пригодный PDF штатным визуальным конструктором |
| **23** | **Подключить Email и Email Notification** | System Notification уже работает, почта ещё не настроена | Email как часть документа и автоматизации | Email Account, Send Email из Form, Communication, Email Queue, attachment/PDF, простой Email Template через UI без ручного Jinja; затем Email channel в Notification | письмо отправляется из Work Item и сохраняется в истории; ранее созданное Notification дополнительно отправляет Email |
| **24** | **Создать внешний Web Form** | Работают Desk users и permissions | Внешний пользовательский сценарий | Website User, Web Form, Get Fields, route, publish, Guest/Login Required, list, edit, delete, comments, attachments, print, Apply Document Permission, multi-step | внешний пользователь создаёт Work Item и после авторизации работает со своими документами без Desk |
| **25** | **Проверить автоматический REST API** | Работают Desk и Web Form | Машинный интерфейс к тем же Documents | отдельный API User, API Key/Secret, автоматически предоставляемый REST API, CRUD, fields, filters, pagination, permissions, базовое знакомство с API v1/v2 | через Postman/`curl` API User читает, создаёт и изменяет Work Item строго в рамках своих Role Permissions |
| **26** | **Проверить переносимость no-code проекта** | Проект полностью настроен на первом Site | Второй Site с той же конфигурацией, но без операционных данных первого Site | Package Release, download, Package Import, Activate, сравнение содержимого и границ Package | Package импортирован на второй чистый Site; ученик проверяет, какие DocTypes/настройки проекта перенеслись, и понимает отличие конфигурации от данных Site |
| **27** | **Резервировать и восстанавливать полный Site** | Первый Site полностью настроен и содержит данные/файлы | Восстанавливаемость полного состояния | Bench backup, backup с public/private files, restore, проверка Site data/config | после restore сохраняются Users, no-code конфигурация, Documents, Files, настройки и рабочий процесс |
| **28** | **Пройти финальный сквозной сценарий** | Все базовые механизмы настроены и Site восстановлен | Цельная рабочая система | совместное использование всей базовой функциональности | после restore проходит полный сценарий: Web Form → Work Item → Assignment → Workflow → Notification → Comments/Files → Report Builder → Dashboard → Print/Email → REST API; Package отдельно воспроизводит no-code конфигурацию на втором Site |

---

# Контрольная матрица покрытия базового no-code уровня

| Область Frappe 16 | Практические работы |
|---|---|
| Bench / Site | 00, 27 |
| Desk / System Settings / Awesome Bar | 01 |
| Desktop / Workspace Sidebar v16 | 01, 10 |
| Package / Custom Module | 02 |
| Custom DocType / Document / CRUD | 03 |
| DocField / базовые Field Types / form layout | 04 |
| Geolocation | 04, 09 |
| Naming / title / search | 05 |
| Link / Fetch From / Dynamic Link | 06 |
| Child DocType / Table | 06 |
| Single DocType | 06 |
| File / Attachments | 06, 13, 23, 24 |
| Connections | 06 |
| Tree DocType / Tree View | 07, 09 |
| Submit / Cancel / Amend | 08 |
| Allow on Submit | 08 |
| Track Changes / Version / Timeline | 08, 13 |
| Audit Trail | 08 |
| List View / filters / sorting / paging / bulk actions | 09 |
| Tags / filter by tags | 09, 13 |
| Report View | 09 |
| Kanban | 09 |
| Calendar View / Calendar | 09 |
| Gantt | 09 |
| Map View | 09 |
| Workspace / sidebar / onboarding | 10 |
| User / System User | 11 |
| Role / Role Profile | 11 |
| Role Permissions | 12 |
| Permission Level | 12 |
| If Owner | 12 |
| User Permission | 12 |
| Share | 12, 13 |
| Assign / ToDo | 13 |
| Comments / Mentions | 13 |
| Following / Track Seen / Track Views | 13 |
| Assignment Rule | 14 |
| Workflow / Workflow State | 15 |
| Workflow Actions | 15 |
| System Notification | 16 |
| Auto Repeat | 17 |
| Customize Form | 18 |
| Custom Field | 18 |
| Property Setter | 18 |
| Custom DocPerm | 18 |
| Custom Link | 18 |
| Route Action | 18 |
| DocType Layout | 18 |
| Data Import / Data Export | 19 |
| Report Builder | 20 |
| Number Card / Dashboard Chart | 21 |
| Dashboard / Workspace analytics | 21 |
| Standard Print / Print Format Builder / PDF | 22 |
| Email Account / Communication / Email Queue | 23 |
| Email Notification | 23 |
| Website User | 24 |
| Web Form | 24 |
| Automatically provided REST API | 25 |
| API authentication and permissions | 25 |
| Package Release / Package Import | 26 |
| Backup / Restore | 27 |
| Сквозной итоговый сценарий | 28 |

---

# Явно исключённые границы

Следующие возможности **не считаются пропусками базовой матрицы**, потому что требуют программирования или относятся к следующему уровню:

- Python controller и Document API;
- Database API, Query Builder и SQL;
- Server Script и Client Script;
- любые script conditions/expressions, которые требуют написания Python/JavaScript;
- Query Report и Script Report;
- custom API methods;
- custom background jobs / scheduler;
- custom Desk Page и client-side APIs;
- ручной Jinja/HTML/CSS;
- Virtual DocType / Virtual DocField;
- Document Queue;
- Data Migration Tool;
- Data Masking / Custom Permission Types;
- Scanner API;
- custom realtime;
- developer-level стандартные DocTypes собственного app.

---

# Критерий качества каждой работы

Практическая работа считается завершённой только если ученик:

1. получил ожидаемый результат;
2. проверил его под правильным типом пользователя;
3. изменил или намеренно нарушил одну из безопасных настроек;
4. увидел изменение поведения;
5. объяснил, какая штатная настройка Frappe отвечает за результат;
6. вернул проект в корректное состояние;
7. прошёл контрольный сценарий;
8. не использовал Python, JavaScript, SQL, Server Script, Client Script или собственный app-код;
9. для функции, спорной по принадлежности к core Frappe, подтвердил её по официальной документации Framework или `frappe/frappe version-16`.

Матрица покрывает **базовый штатный no-code уровень Frappe 16**, а не весь Developer API Framework.
