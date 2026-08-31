# Матрица базового практикума Frappe Framework 16

Матрица фиксирует обязательную последовательность базового уровня. Единица обучения — не отдельная кнопка или API-метод, а **осмысленный прирост одного сквозного проекта**.

Условия уровня:

- только штатные возможности Frappe 16;
- без Python;
- без JavaScript;
- без SQL;
- без ручной разработки собственного Frappe App;
- терминал используется только для установки и штатного администрирования стенда.

## Практические работы

| № | Практическая работа | Входное состояние | Что добавляем в проект | Штатные возможности | Контрольный результат |
|---:|---|---|---|---|---|
| **00** | **Развернуть чистый Frappe 16** | Чистая Linux-система | Рабочий учебный стенд | системные зависимости, MariaDB, Redis/Valkey, Bench, Site, `bench start`, Desk | Site открывается; Administrator входит в Desk; стенд повторно запускается после остановки |
| **01** | **Освоиться в Frappe** | Пустой Site | Базовая конфигурация среды | Desk, Awesome Bar, System Settings, язык, timezone, форматы, sessions, login/password settings, основные журналы | ученик самостоятельно находит настройку, DocType, пользователя и журнал событий |
| **02** | **Создать первый рабочий объект** | Пустой настроенный Site | `Work Item` | Custom DocType, Document, Form View, List View, стандартные системные поля, CRUD | можно создать, открыть, изменить, скопировать и удалить Work Item |
| **03** | **Построить нормальную карточку** | Минимальный Work Item | Рабочие поля и структура формы | основные Field Types; mandatory, default, read-only, unique, hidden; Section/Column/Tab Break; Quick Entry; свойства отображения | форма логична, обязательные ограничения реально работают |
| **04** | **Настроить идентификацию и поиск** | Карточка без удобной идентификации | Удобные имена и поиск | naming, naming series/field naming, Title Field, Search Fields, Allow Rename, list/preview properties | документы имеют понятные идентификаторы и находятся по рабочим данным |
| **05** | **Построить связанную модель данных** | Один самостоятельный DocType | `Project`, `Category`, `Work Item Step`, `Practicum Settings` и связи | Link, Fetch From, Dynamic Link, Child DocType, Table, Single DocType, File/Attachments, Connections | Work Item связан с Project/Category, содержит checklist и использует общие настройки |
| **06** | **Добавить иерархический справочник** | Плоская Category | Иерархия категорий | Tree DocType / Is Tree, parent-child hierarchy, Tree View | категории создаются, перемещаются и просматриваются как дерево |
| **07** | **Освоить жизненный цикл документа** | Обычные редактируемые документы | Контролируемый документ и аудит изменений | Is Submittable, Draft, Submit, Cancel, Amend, Allow on Submit, Track Changes, Version, Timeline | ученик проходит полный lifecycle и видит последствия каждого состояния |
| **08** | **Освоить штатные представления** | Достаточный массив Work Items | Несколько способов ежедневной работы с теми же данными | List View, filters, sorting, columns, standard filters, bulk actions, Report View, Kanban, Calendar, Gantt/Tree там, где модель применима | один набор Documents используется через разные представления без изменения модели |
| **09** | **Собрать рабочее место пользователя** | Набор DocTypes и views | Единый вход в учебную систему | Workspace, Heading, Text, Card, Shortcut, Quick List, Number Card, Chart, Onboarding, public/private Workspace, sidebar | пользователь получает цельный рабочий экран и навигацию |
| **10** | **Добавить реальных пользователей** | Работа только Administrator | Пользователи и роли | User, System User, Website User, Role, Role Profile, module access, default Workspace, пользовательские настройки | минимум три разных пользователя работают под собственными учётными записями |
| **11** | **Разграничить права** | Пользователи видят систему одинаково | Реальная модель доступа | Role Permission Manager; Read, Write, Create, Delete, Submit, Cancel, Amend, Report, Export, Import, Share, Print, Email; Permission Level; If Owner; User Permission; Share; Page/Report permissions | разные роли реально видят разные Documents, поля и действия; проверка выполняется не Administrator |
| **12** | **Организовать совместную работу** | Documents без исполнителей | Поручение и взаимодействие внутри карточки | Assign, ToDo, priority, due date, Comments, Mentions, Attachments, Timeline, Version, Share | один пользователь назначает работу другому; исполнитель получает ToDo и ведёт работу в Work Item |
| **13** | **Автоматизировать распределение работы** | Назначения выполняются вручную | Автоматическое назначение | Assignment Rule, Round Robin, Load Balancing, Based on Field, Due Date Based On — без script conditions | новые Work Items распределяются штатным Assignment Rule без собственного кода |
| **14** | **Построить Workflow** | Есть роли и permissions | Управляемый процесс | Workflow State, Workflow, transitions, allowed roles, Workflow Actions | Work Item проходит `Новая → В работе → На проверке → Завершена/На доработку`; действия доступны правильным ролям |
| **15** | **Настроить штатные уведомления** | Workflow не информирует людей автоматически | Событийные и срочные уведомления | Notification, Document Event, Value Change, date-based event, recipients по roles/document fields, System Notification, Email Notification | исполнитель получает событие и напоминание по сроку без собственного кода |
| **16** | **Добавить повторяемую работу** | Work Items создаются вручную | Регулярные документы | Allow Auto Repeat, Auto Repeat, frequency, start/end dates | Frappe самостоятельно создаёт следующий повторяемый Work Item |
| **17** | **Освоить штатную кастомизацию** | Известно создание собственных Custom DocTypes | Изменение уже существующей модели без исходного кода | Customize Form, Custom Field, Property Setter, Custom DocPerm, Custom Link | существующая форма и её права изменены через штатный customization layer |
| **18** | **Освоить массовую работу с данными** | Данные вводятся в основном вручную | Массовая загрузка и выгрузка | Data Export, Data Import, import template, Insert, Update, child data, validation/import errors, bulk operations где применимо | массив Work Items импортируется, обновляется и экспортируется обратно |
| **19** | **Построить отчётность без кода** | Накоплены рабочие данные | Пользовательские отчёты | Report Builder, columns, filters, sorting, Group By, Count/Sum/Average, child records, saved reports, print/export actions | пользователь самостоятельно собирает несколько рабочих отчётов без SQL |
| **20** | **Собрать Dashboard** | Есть рабочие отчёты | Управленческий экран | Number Card, Dashboard Chart, Dashboard/Workspace analytics, filters/aggregates, role access | на одном экране видны ключевые показатели: открытые, просроченные и распределение по статусам |
| **21** | **Настроить печать** | Work Item существует только в интерфейсе | Человекочитаемый внешний документ | Standard Print View, Print Format Builder, Letter Head, Print Settings, PDF, default Print Format | из Work Item получается пригодный PDF без ручного HTML/Jinja-кода |
| **22** | **Подключить Email** | Коммуникация живёт отдельно от документа | Email как часть истории Work Item | Email Account, Send Email из Form, Communication, Email Queue, attachment/PDF, Email Template через UI | письмо отправляется из Work Item и сохраняется в его истории |
| **23** | **Создать внешний Web Form** | Работать с системой могут только Desk Users | Внешний сценарий создания/просмотра Work Item | Web Form, Get Fields, route, publish, Guest/Login Required, Website User, list, edit, delete, comments, attachments, print, Apply Document Permission, multi-step | внешний пользователь создаёт заявку и при авторизации работает со своими документами без Desk |
| **24** | **Проверить автоматический REST API** | Работают Desk и Web Form | Машинный интерфейс к тем же Documents | API Key/Secret, автоматически предоставляемый REST API, CRUD, fields, filters, pagination, permissions; базовое знакомство с API v1/v2 | через Postman/curl отдельный API User читает, создаёт и изменяет Work Item строго в рамках своих permissions |
| **25** | **Резервировать и восстанавливать Site** | Полностью настроенный учебный Site | Восстанавливаемость | Bench backup, backup с public/private files, restore, проверка Site data/config | после restore сохраняются Users, DocTypes, Documents, Files, настройки и рабочий процесс |
| **26** | **Пройти финальный сквозной сценарий** | Все базовые механизмы настроены | Цельная рабочая система | совместное использование всей базовой функциональности | полный сценарий проходит после восстановления: Web Form → Work Item → Assignment → Workflow → Notification → работа с файлами/комментариями → отчёт → Dashboard → Print/Email → REST API |

---

# Контрольная матрица покрытия

| Область Frappe 16 | Практические работы |
|---|---|
| Bench / Site | 00, 25 |
| Desk / System Settings / Awesome Bar | 01 |
| Custom DocType / Document / CRUD | 02 |
| DocField / основные Field Types / layout | 03 |
| Naming / title / search | 04 |
| Link / Fetch From / Dynamic Link | 05 |
| Child DocType / Table | 05 |
| Single DocType | 05 |
| File / Attachments | 05, 12, 22, 23 |
| Connections | 05 |
| Tree DocType / Tree View | 06, 08 |
| Submit / Cancel / Amend | 07 |
| Allow on Submit | 07 |
| Track Changes / Version / Timeline | 07, 12 |
| List View / filters / bulk actions | 08 |
| Report View | 08 |
| Kanban | 08 |
| Calendar / Gantt | 08 |
| Workspace / sidebar / onboarding | 09 |
| User / System User / Website User | 10, 23 |
| Role / Role Profile | 10 |
| Role Permissions | 11 |
| Permission Level | 11 |
| If Owner | 11 |
| User Permission | 11 |
| Share | 11, 12 |
| Assign / ToDo | 12 |
| Comments / Mentions | 12 |
| Assignment Rule | 13 |
| Workflow / Workflow State | 14 |
| Workflow Actions | 14 |
| Notification | 15 |
| Auto Repeat | 16 |
| Customize Form | 17 |
| Custom Field | 17 |
| Property Setter | 17 |
| Custom DocPerm | 17 |
| Custom Link | 17 |
| Data Import / Data Export | 18 |
| Report Builder | 19 |
| Number Card / Dashboard Chart | 20 |
| Dashboard / Workspace analytics | 20 |
| Standard Print / Print Format Builder / PDF | 21 |
| Email Account / Communication / Email Queue | 22 |
| Web Form | 23 |
| автоматически предоставляемый REST API | 24 |
| API authentication и permissions | 24 |
| Backup / Restore | 25 |
| Сквозной итоговый сценарий | 26 |

---

# Критерий качества каждой работы

Практическая работа считается завершённой только если ученик:

1. получил ожидаемый результат;
2. проверил его под правильным типом пользователя;
3. изменил или намеренно нарушил одну из настроек;
4. увидел изменение поведения;
5. объяснил, какая штатная настройка Frappe отвечает за результат;
6. вернул проект в корректное состояние;
7. прошёл контрольный сценарий работы.

Матрица не должна расширяться developer-level возможностями только ради формального покрытия Framework. Всё, что требует Python, JavaScript, SQL или собственного приложения, относится к следующему уровню обучения.
