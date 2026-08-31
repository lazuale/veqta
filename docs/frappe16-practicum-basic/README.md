# Frappe Framework 16 — базовый практикум

## Статус

Согласованная базовая траектория практического освоения Frappe Framework 16.

Этот каталог является самостоятельным практикумом и не продолжает старую структуру `docs/frappe16-course`. Старый каталог сохраняется как предыдущая версия материала, но не является источником структуры, требований или последовательности нового практикума.

## Цель

Провести человека без опыта работы с Frappe от чистого стенда до законченного рабочего продукта, собранного **максимально нативно из штатных возможностей Frappe Framework 16**.

Практикум строится вокруг одного сквозного проекта — системы управления работой. Каждая следующая работа расширяет уже существующую систему и использует только знания и объекты, введённые ранее.

Главный принцип:

> Сначала используем штатный декларативный механизм Frappe. Встроенный low-code применяем только там, где он является естественным продолжением штатной функции. Полноценную файловую разработку собственного поведения откладываем на следующий уровень.

## Что означает native-first

При решении каждой задачи действует такой порядок выбора:

1. **Штатная настройка / metadata** — DocType, поля, permissions, Workflow, Assignment Rule, Notification, Workspace, Web Form, Report Builder и другие готовые механизмы.
2. **Штатный low-code Frappe** — expressions, Client Script, Server Script, Query Report, custom Script Report, Jinja в Print Format, Webhook и другие встроенные scripting-поверхности.
3. **Файловая разработка собственного app-кода** — только если первые два слоя не решают задачу; этот слой в базовый практикум не входит.

Практикум не должен использовать Client Script или Server Script там, где тот же результат штатно решается настройкой поля, Workflow, Notification, Assignment Rule, permissions или другим более нативным механизмом.

## Архитектурная граница базового проекта

В базовом практикуме создаётся **обычное собственное Frappe App штатной командой `bench new-app`**.

Это контейнер продукта, а не повод сразу писать Python-логику.

```text
Bench
  ↓
Site
  ↓
App: frappe_practicum
  ↓
Module: Practicum
  ↓
DocTypes / Workspace / Reports / Scripts / Web / Integrations
```

App создаётся, устанавливается на Site и хранится в Git. Внутри базового уровня продукт максимально собирается штатными механизмами Frappe.

## Что входит в базовый уровень

### Платформа и App

- установка и базовое администрирование Frappe 16;
- Bench и Site;
- `bench new-app`;
- структура App на уровне понимания контейнера проекта;
- Module;
- `bench --site ... install-app`;
- `bench migrate` на уровне эксплуатации;
- Git для хранения собственного App;
- Desk, Desktop, Workspace Sidebar v16, Awesome Bar, System Settings и основные журналы.

### Модель данных

- DocType и Document;
- DocField и штатные типы полей;
- naming, title и search;
- Link, Fetch From, Dynamic Link;
- Child DocType / Table;
- Single DocType;
- Tree DocType;
- Files / Attachments;
- Connections и Actions;
- Geolocation.

### Lifecycle и аудит

- Draft / Submit / Cancel / Amend;
- Allow on Submit;
- Track Changes;
- Version;
- Timeline;
- Audit Trail;
- Track Seen / Track Views.

### Views и рабочий интерфейс

- Form View;
- List View;
- Report View;
- Kanban;
- Calendar View;
- Gantt там, где доступен штатно;
- Tree View;
- Map View;
- Workspace;
- Cards, Shortcuts, Quick Lists, Onboarding;
- Number Cards и Dashboard Charts;
- DocType Layout.

### Пользователи и доступ

- User / System User / Website User;
- Role / Role Profile;
- Role Permission Manager;
- Permission Level;
- If Owner;
- User Permission;
- Share;
- Page / Report / Import / Export / Print / Email permissions;
- штатные permission conditions;
- Server Script Permission Query как встроенный low-code механизм после освоения обычных permissions.

### Совместная работа и процесс

- Assign / ToDo;
- Comments / Mentions / Tags / Following;
- Attachments;
- Assignment Rule;
- Workflow / Workflow State / Workflow Actions;
- штатные conditions в Assignment Rule, Workflow и Notification;
- Notification;
- Auto Repeat;
- Workflow Transition Tasks v16 в той части, где используются штатные Server Script/Webhook actions.

### Встроенный low-code

- простые expressions в штатных настройках;
- Client Script для Form/List там, где декларативных настроек недостаточно;
- Server Script:
  - DocType Event;
  - Scheduler Event;
  - Permission Query;
  - API;
  - Workflow Task;
- restricted scripting как встроенный механизм Frappe;
- понимание границы между Client Script и серверной логикой.

### Данные, отчётность и аналитика

- Data Import / Data Export;
- Report Builder;
- Query Report;
- Custom Script Report, если script хранится в самом Report и не требует файлов собственного app;
- Number Card;
- Dashboard Chart;
- Dashboard / Workspace analytics.

### Печать и коммуникации

- Standard Print;
- Print Format Builder;
- Jinja в штатном Print Format;
- HTML/CSS внутри Print Format в объёме, необходимом для штатной печати;
- Letter Head;
- PDF;
- Email Account;
- Communication;
- Email Queue;
- Email Template;
- Email Notification.

### Website и внешние интерфейсы

- Website Settings на базовом уровне;
- Web Page / Page Builder там, где доступны штатно;
- Web Form;
- Web Form layout, CSS и встроенный Client Script;
- Website User;
- автоматически предоставляемый REST API;
- API Key / Secret;
- Server Script API;
- Webhook;
- штатные условия, headers и payload templates.

### Переносимость и эксплуатация

- Package как отдельная штатная возможность Frappe для UI-created/lightweight конфигураций — изучается для понимания, но не является основным контейнером учебного проекта;
- backup / restore;
- перенос App через Git;
- установка App на чистый второй Site;
- `bench migrate`;
- проверка воспроизводимости продукта.

## Что не входит

Базовый уровень не переходит в полноценную файловую разработку поведения приложения:

- собственные Python controllers в DocType `.py`;
- собственная бизнес-логика в Python-модулях App;
- `hooks.py` как extension architecture;
- override/extend стандартных классов и методов;
- собственные whitelisted Python methods в файловом коде;
- собственные background jobs в Python-коде App;
- собственные scheduler handlers через hooks;
- файловые Form/List/Page JS-скрипты App;
- asset bundling, Vue, TypeScript и custom frontend;
- Standard Script Report с файловыми `.py/.js`;
- custom Page с файловой разработкой;
- patches и data migrations собственного App;
- Virtual DocType / Virtual DocField, если требуется controller-код;
- custom Jinja methods через hooks;
- полноценные automated tests собственного app-кода;
- production-hardening как отдельный DevOps-курс.

Это следующий уровень: **Frappe 16 Development**.

## Сквозной учебный проект

```text
App: frappe_practicum
└── Module: Practicum
    │
    ├── Project
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

`Work Item` остаётся обычным рабочим документом и используется в Assign, Workflow, Notifications, reports, Web Form и API.

`Work Approval` используется для естественного изучения `Draft → Submit → Cancel → Amend`, `Allow on Submit` и Audit Trail.

## Методическое правило выбора решения

Перед добавлением любой логики в практикум задаются четыре вопроса:

1. Есть ли для задачи готовая штатная настройка Frappe?
2. Есть ли более естественный стандартный DocType/механизм, чем script?
3. Если нужен script, существует ли для этого встроенная low-code поверхность Frappe?
4. Требует ли решение изменения файлов Python/JS собственного App?

Если ответ на пункт 4 — да, тема переносится в Development-уровень, если только файл не является автоматически создаваемым стандартным артефактом самого App без добавления собственной логики.

## Последовательность

```text
чистая система
    ↓
Bench / Site
    ↓
bench new-app / Module / install-app / Git
    ↓
DocTypes и модель данных
    ↓
Document lifecycle и audit
    ↓
штатные views / Workspace
    ↓
Users / Roles / Permissions
    ↓
Collaboration / Assignment Rule
    ↓
Workflow / Notification / Auto Repeat
    ↓
встроенный Client Script / Server Script там, где это естественно
    ↓
Import / Reports / Analytics
    ↓
Print / Jinja / Email
    ↓
Web Page / Web Form
    ↓
REST API / Server Script API / Webhook
    ↓
Workflow Transition Tasks
    ↓
Package как отдельный stock-механизм
    ↓
Git deployment на второй Site / migrate
    ↓
backup / restore
    ↓
финальный рабочий продукт
```

## Источники истины внутри каталога

- [`README.md`](README.md) — границы, цель и требования уровня;
- [`MATRIX.md`](MATRIX.md) — единственный источник состава и нумерации практических работ;
- [`ROADMAP.md`](ROADMAP.md) — единственный источник фаз и логики последовательности;
- [`labs/README.md`](labs/README.md) — стандарт написания и проверки конкретных практических работ.

## Требование к официальности

Каждая практическая работа должна быть подтверждена для **Frappe Framework 16**.

Приоритет источников:

1. официальная документация Frappe Framework;
2. ветка `version-16` репозитория `frappe/frappe`;
3. официальные migration notes v16.

Документация ERPNext, HRMS, CRM и других приложений может использоваться как UI-справка только после подтверждения, что соответствующий механизм действительно входит в core Frappe 16.

## Критерий завершения базового уровня

После практикума ученик должен уметь самостоятельно:

1. развернуть учебный Frappe 16;
2. создать собственный App штатной командой Bench и установить его на Site;
3. построить связанную модель DocTypes;
4. настроить lifecycle и audit;
5. использовать штатные views и Workspace;
6. создать пользователей, роли и permissions;
7. организовать collaboration, Assignment Rule и Workflow;
8. настроить Notifications и Auto Repeat;
9. использовать встроенные expressions, Client Script и Server Script без ухода в файловую разработку;
10. импортировать данные и строить Report Builder / Query Report / Custom Script Report;
11. собрать Dashboard;
12. настроить Print Format Builder и Jinja-печать;
13. настроить Email;
14. создать Web Page и Web Form;
15. использовать штатный REST API, Server Script API и Webhook;
16. использовать Workflow Transition Tasks там, где это уместно;
17. понимать назначение Package и его отличие от обычного App;
18. установить свой App из Git на второй Site и выполнить migrate;
19. сделать backup и restore;
20. пройти полный сквозной сценарий после восстановления.

Если это выполнено, базовый уровень считается завершённым.