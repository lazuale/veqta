# Frappe Framework 16 — базовый практикум

## Статус

Согласованная базовая траектория практического освоения Frappe Framework 16.

Этот каталог является самостоятельным практикумом и не продолжает старую структуру `docs/frappe16-course`. Старый каталог сохраняется как предыдущая версия материала, но не является источником структуры, требований или последовательности нового практикума.

## Цель

Провести человека без опыта работы с Frappe от чистого стенда до законченной рабочей системы, построенной **штатными средствами Frappe 16 без программирования**.

Практикум строится вокруг одного сквозного проекта — системы управления работой. Каждая следующая работа расширяет уже существующую систему и использует только знания и объекты, введённые ранее.

Главный принцип:

> Не изучаем возможности Frappe по отдельности. Строим одну систему от простого к сложному и вводим новую возможность тогда, когда она естественно нужна проекту.

## Что означает «без программирования»

На базовом уровне ученик не пишет:

- Python;
- JavaScript;
- SQL;
- Server Script;
- Client Script;
- Query Report;
- Script Report;
- собственные API methods;
- hooks;
- Jinja/HTML/CSS как программируемый шаблон;
- произвольные Python/JavaScript-условия и выражения в полях настроек.

Разрешены:

- действия в Desk и других штатных UI Frappe;
- создание и настройка стандартных Frappe-документов;
- Custom DocType и Custom Module;
- Package / Package Release / Package Import;
- терминал только для установки, запуска, диагностики, backup/restore и других штатных административных команд;
- Postman или `curl` для проверки автоматически предоставляемого REST API.

Если штатная возможность существует, но для её практического использования требуется написание Python, JavaScript, SQL, Jinja или иного кода, она относится к следующему уровню — **Frappe 16 Development**.

## Архитектурная граница базового проекта

Базовый практикум **не создаёт собственный Frappe App** через `bench new-app`.

Вместо этого проект собирается штатным no-code механизмом Frappe:

```text
Frappe Site
    ↓
Package: Frappe Practicum
    ↓
Custom Module: Practicum
    ↓
Custom DocTypes / Workspace / Reports / другие no-code объекты
```

Package используется как контейнер переносимой no-code конфигурации проекта. В конце практикума Package Release импортируется на второй Site, чтобы отдельно проверить перенос конфигурации. Backup/Restore затем проверяет восстановление **всего Site вместе с данными и файлами**.

Это два разных навыка:

```text
Package Release / Import
= перенос конфигурации no-code проекта

Backup / Restore
= восстановление полного состояния Site
```

## Сквозной учебный проект

В течение практикума формируется следующая модель:

```text
Package: Frappe Practicum
└── Module: Practicum
    │
    ├── Project
    │
    ├── Work Item
    │   ├── Project
    │   ├── Category
    │   ├── Status
    │   ├── Priority
    │   ├── Responsible
    │   ├── Start Date
    │   ├── Due Date
    │   ├── Location
    │   ├── Description
    │   ├── Checklist
    │   └── Files
    │
    ├── Category [Tree]
    ├── Work Item Step [Child]
    ├── Practicum Settings [Single]
    └── Work Approval [Submittable]
```

`Work Item` остаётся обычным рабочим документом и свободно развивается дальше через Assign, Workflow и совместную работу.

`Work Approval` создаётся специально для изучения штатного lifecycle `Draft → Submit → Cancel → Amend`, `Allow on Submit` и Audit Trail. Мы не делаем `Work Item` submittable только ради демонстрации функции.

## Что входит в базовый уровень

### Платформа и навигация

- установка и базовое администрирование учебного Frappe 16;
- Bench и Site на уровне, необходимом пользователю практикума;
- Desk;
- Desktop и Workspace Sidebar v16;
- Awesome Bar;
- System Settings;
- основные журналы и диагностика.

### No-code контейнер проекта

- Package;
- Custom Module;
- Package Release;
- Package Import;
- проверка переноса no-code конфигурации на второй Site.

### Модель данных

- Custom DocType и Document;
- DocField и базовые штатные типы полей;
- Geolocation;
- naming, title и search;
- Link и Fetch From;
- Dynamic Link;
- Child DocType и Table;
- Single DocType;
- Tree DocType;
- File / Attachments;
- Connections.

### Lifecycle и аудит

- Draft / Submit / Cancel / Amend;
- Allow on Submit;
- Track Changes;
- Version;
- Timeline;
- Audit Trail;
- Track Seen / Track Views.

### Представления и рабочий интерфейс

- List View;
- Report View;
- Kanban;
- Calendar View;
- Gantt там, где доступен штатно для настроенной модели;
- Tree View;
- Map View;
- фильтры, сортировка, теги и массовые действия;
- Workspace;
- Cards, Shortcuts, Quick Lists и Onboarding;
- Number Cards и Charts после их создания на аналитическом этапе;
- DocType Layout без кодовых условий переключения.

### Пользователи и доступ

- User и System User;
- Website User вводится только в Web Form-сценарии;
- Role;
- Role Profile;
- Role Permissions;
- Permission Level;
- If Owner;
- User Permission;
- Share;
- права на Reports, Pages, Print, Import/Export и другие штатные операции.

### Совместная работа и процесс

- Assign;
- ToDo;
- Comments;
- Mentions;
- Tags;
- Following;
- Attachments;
- Assignment Rule без script conditions;
- Workflow без кодовых transition conditions;
- Workflow Actions;
- System Notification без script conditions;
- Auto Repeat.

### Кастомизация, данные и аналитика

- Customize Form;
- Custom Field;
- Property Setter;
- Custom DocPerm;
- Custom Link;
- Route Action без server action;
- Data Import / Data Export;
- Report Builder;
- Number Card;
- Dashboard Chart;
- Dashboard / Workspace analytics.

### Вывод и внешние интерфейсы

- стандартная печать;
- Print Format Builder без ручного HTML/Jinja;
- Letter Head;
- PDF;
- Email Account;
- Communication;
- Email Queue;
- Email Notification только после настройки Email Account;
- Web Form;
- автоматически предоставляемый REST API;
- API Key / Secret;
- backup и restore.

## Что не входит

Базовый уровень сознательно не включает developer-level возможности:

- собственный Frappe App;
- Python controllers;
- Python Document API;
- Database API и Query Builder;
- raw SQL;
- hooks;
- Server Script;
- Client Script;
- JavaScript Form Script;
- custom List/Page/Tree JS;
- Query Report;
- Script Report;
- собственные API methods;
- собственные background jobs и scheduler handlers;
- Custom Desk Page;
- ручной Jinja/HTML/CSS как разработку;
- Virtual DocType / Virtual DocField;
- Data Masking;
- Custom Permission Types;
- Document Queue;
- Data Migration Tool;
- Scanner API;
- custom realtime handlers;
- любые возможности, которые требуют написания кода для воспроизводимой практики.

Это следующий уровень: **Frappe 16 Development**.

## Последовательность

```text
чистая система
    ↓
Frappe Site
    ↓
Package + Custom Module
    ↓
Custom DocType
    ↓
связанная модель данных
    ↓
отдельный submittable-документ и audit
    ↓
штатные views
    ↓
Workspace и навигация
    ↓
пользователи и права
    ↓
совместная работа
    ↓
Workflow и автоматизация
    ↓
кастомизация
    ↓
импорт и отчётность
    ↓
Dashboard
    ↓
печать и Email
    ↓
Web Form
    ↓
штатный REST API
    ↓
Package Release / Import
    ↓
backup / restore
    ↓
законченная рабочая система
```

## Источники истины внутри каталога

Чтобы файлы не расходились между собой:

- [`README.md`](README.md) — **границы, цель и требования уровня**;
- [`MATRIX.md`](MATRIX.md) — **единственный источник состава и нумерации практических работ**;
- [`ROADMAP.md`](ROADMAP.md) — **единственный источник фаз и логики последовательности**;
- [`labs/README.md`](labs/README.md) — **стандарт написания и проверки конкретных практических работ**.

Если меняется номер, состав или результат работы, сначала меняется `MATRIX.md`, затем при необходимости корректируется `ROADMAP.md`. README не должен дублировать подробную матрицу.

## Требование к официальности

Каждая практическая работа должна быть подтверждена для **Frappe Framework 16**, а не просто для ERPNext, HRMS, CRM или другой системы на Frappe.

Приоритет источников:

1. официальная документация Frappe Framework;
2. ветка `version-16` репозитория `frappe/frappe`, если документация неоднозначна или отстаёт;
3. официальные migration notes v16 для изменений, специфичных для версии.

Если UI-документация функции находится в ERPNext-разделе, перед включением в практикум необходимо отдельно подтвердить, что соответствующий DocType или механизм действительно входит в core Frappe 16.

## Критерий завершения базового уровня

После практикума ученик без Python, JavaScript и SQL должен самостоятельно уметь:

1. поднять учебный Site Frappe 16;
2. создать Package и Custom Module;
3. построить модель из нескольких связанных Custom DocTypes;
4. создать отдельный submittable-документ и пройти его lifecycle;
5. использовать штатные views, Workspace и навигацию v16;
6. создать пользователей и роли;
7. разграничить права;
8. организовать Assign/ToDo и совместную работу;
9. построить Workflow;
10. настроить штатные уведомления и Auto Repeat;
11. изменить систему через Customize Form и DocType Layout без кода;
12. импортировать и экспортировать данные;
13. сделать Report Builder и Dashboard;
14. подготовить PDF через Print Format Builder;
15. настроить Email и Email Notification;
16. открыть внешний сценарий через Web Form;
17. работать с теми же документами через штатный REST API;
18. выпустить Package Release и импортировать конфигурацию на другой Site;
19. сделать backup полного Site и восстановить его;
20. пройти полный сквозной сценарий после восстановления.

Если это выполнено, базовый уровень Frappe 16 считается завершённым.
