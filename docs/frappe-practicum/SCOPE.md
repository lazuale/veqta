# Границы базового практикума

## Цель

Базовый курс показывает **Frappe Framework 16 как платформу приложений через практику**.

Весь маршрут развивается вокруг одного app:

```text
facility_ops
```

и одной минимальной модели:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Собственная бизнес-логика на Python или JavaScript в базовом курсе не требуется.

Это не запрет на штатные expression-поля, `hooks.py`, fixtures и generated files Frappe. Запрет относится к собственной бизнес-логике, которую пришлось бы программировать вместо штатного механизма платформы.

---

# Проверенная версия

Основная версия — **Frappe Framework v16.32.0**.

Приоритет проверки:

1. фактический учебный стенд `v16.32.0`;
2. исходники exact tag `v16.32.0`;
3. официальная документация Frappe;
4. `version-16` только для отслеживания будущих изменений.

Если документация и exact source расходятся, курс не подгоняется под общую формулировку документации.

---

# Учебный стенд

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Базовый стек фиксируется в `projects/00-lab/SETUP_WSL2.md`.

---

# Ядро приложения

Только три обязательных предметных DocType:

```text
Facility Location
Equipment
Service Request
```

Новая бизнес-сущность не создаётся только ради демонстрации возможности Frappe.

В частности, в базовом ядре нет отдельных:

```text
Equipment Type
Equipment Movement
Inspection
Maintenance Work
Department
Team
Technician
Requester
Status
Priority
```

Если специальному механизму нужен временный объект, он создаётся в лаборатории и после упражнения может быть удалён.

---

# Что входит в основной маршрут L0–L11

## Среда и приложение

- WSL2 / Debian учебный стенд;
- Bench;
- Site;
- App;
- Module;
- Developer Mode;
- структура app;
- `modules.txt`;
- `hooks.py`;
- Git;
- Desk;
- Awesomebar;
- scheduler / workers;
- `bench migrate`;
- второй clean site.

## Модель данных

- DocType;
- DocField;
- Document;
- `name`;
- Standard DocType;
- Tree DocType;
- основные Field Types;
- Link;
- Naming;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Form / List / Tree View;
- Allow Import;
- Data Import / Export.

## Работа с данными

- Filters;
- Sorting List View;
- Saved Filters;
- Search;
- Data Import template;
- negative import test;
- Bulk Edit;
- Export;
- Attachments;
- Timeline.

Курс не утверждает, что отдельная настройка metadata `Default Sort` изучена: L3 проверяет обычную сортировку текущего списка.

## Пользователи и права

- User;
- System User;
- Website User;
- Guest;
- Role;
- Role Permission Manager;
- Read / Write / Create / Delete;
- Report / Export / Import там, где они используются;
- If Owner / Only If Creator;
- Permission Level;
- User Permission;
- Share.

Права проверяются отдельным входом под обычными учебными пользователями, а не под Administrator.

## Совместная работа

- Assign To;
- ToDo;
- Due Date;
- Comments;
- Timeline;
- Tags;
- Kanban.

Главное различие:

```text
Permission = что пользователь может делать
Assignment = какая конкретная работа назначена
Status     = состояние рабочего документа
```

## Workflow

- обычный Status до Workflow;
- Workflow;
- Workflow State;
- Workflow Action Master;
- Workflow Transition;
- Allowed Role;
- Only Allow Edit For;
- Workflow Action;
- простая transition Condition;
- использование существующего `Service Request.status` как Workflow State Field.

Workflow появляется только после того, как ученик увидел свободное ручное изменение Status.

## Контроль работы

- один рабочий Report Builder;
- Filters;
- Group By;
- Count;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcut;
- Quick List;
- role-based access к Workspace/Chart.

`Sum / Average` в базовом маршруте не изучаются и не считаются покрытыми.

## Автоматизация

- Standard Notification;
- System Notification;
- Notification Filters;
- date-based Notification;
- Preview / Alerts for Today;
- Assignment Rule;
- Round Robin;
- Due Date Based On;
- Close Condition;
- штатные expression-поля механизма;
- scheduler/background jobs;
- ручной запуск штатного scheduler job для теста.

Load Balancing проверяется как самостоятельное упражнение, а не как второй обязательный алгоритм.

## Web

- Standard Web Form;
- Route;
- Published;
- Anonymous responses;
- Guest;
- Login Required;
- Website User;
- Allow Edit;
- Show List;
- Apply Document Permissions;
- Allow Read On All Link Options;
- attachments.

Web Form работает поверх существующего `Service Request`, а не создаёт второй процесс заявок.

## Поставка приложения

- Standard metadata;
- app configuration;
- site-specific configuration;
- working data;
- fixtures;
- `fixture_auto_order`;
- `bench export-fixtures`;
- Export Customizations;
- Custom Permissions;
- `install-app`;
- `bench migrate`;
- clean site;
- повторная проверка migrate.

Главный результат L11: ученик понимает, что app source, конфигурация site и рабочие Documents — разные слои.

---

# Что изучается лабораториями

Лаборатории не расширяют постоянное ядро приложения.

## Lab A — Child Table

- Child DocType;
- Table;
- Float;
- Currency;
- `parent`;
- `parenttype`;
- `parentfield`;
- `idx`.

Временный `Work Log` после практики удаляется.

## Lab B — DocStatus

- Is Submittable;
- Draft;
- Submit;
- Cancel;
- Amend;
- DocStatus;
- Allow on Submit;
- Audit Trail.

Используется отдельный временный `Service Report`, чтобы не ломать lifecycle Service Request.

## Lab C — Auto Repeat

- Allow Auto Repeat;
- Auto Repeat;
- Assignee;
- scheduler;
- generated Document;
- cleanup служебного `auto_repeat` Custom Field.

## Lab D — Customize Form

- Customize Form;
- Custom Field;
- Property Setter;
- Module for Export;
- Export Customizations;
- Sync on Migrate;
- точечная очистка кастомизации.

Lab D **не** создаёт Custom DocType и **не** изучает DocType Layout.

## Lab E — Print / PDF

- Print View;
- Print Format;
- Print Format Builder;
- Standard Print Format;
- Letter Head;
- Print Settings;
- browser Print;
- PDF;
- Chrome PDF generator;
- Print permission как граница пользовательского доступа.

Полезный Print Format остаётся в приложении; учебный Letter Head удаляется.

## Lab F — специальные возможности

- Single DocType;
- Dynamic Link;
- Table MultiSelect;
- Check;
- Percent;
- Time;
- Duration;
- Barcode;
- Signature;
- Geolocation;
- Attachment Gallery;
- Markdown Editor;
- Data Masking;
- Calendar;
- Gantt.

Calendar/Gantt проверяются на штатном `Event`. Для собственного DocType в `v16.32.0` нужна calendar JavaScript-конфигурация, поэтому собственный Calendar/Gantt остаётся на следующем уровне.

---

# Что остаётся на следующем уровне

- Custom DocType как отдельная практика;
- DocType Layout;
- изменение default sort metadata как отдельная практика;
- Sum / Average и более сложная аналитика;
- Email permission как отдельная проверка;
- собственные Python controllers с бизнес-логикой;
- собственные server-side hooks с бизнес-логикой;
- JavaScript / Client Script;
- собственный calendar JS;
- Server Script;
- whitelisted methods;
- REST API / Webhooks;
- Query Report / Script Report;
- ручные Jinja templates;
- собственные Website / Portal Pages;
- Web Form Request/key internals;
- Virtual DocType;
- сторонние библиотеки и apps;
- Custom Permission Types, требующие собственного кода.

---

# Что считается частью app

## Standard metadata / Standard source object

Создано в Developer Mode внутри Module приложения и хранится в source `facility_ops`.

Примеры курса:

```text
DocType
Standard Report
Standard Number Card
Standard Dashboard Chart
Standard Workspace
Standard Notification
Standard Web Form
Standard Print Format
```

## App configuration

Configuration Documents, которые должны существовать на любом развёртывании приложения, но не являются Standard source-объектами.

В L11 через fixtures поставляются:

```text
Facility Requester
Facility Technician
Facility Supervisor
Workflow State
Workflow Action Master
Service Request Workflow
```

## Site-specific configuration

Зависит от конкретного развёртывания и не должна автоматически ехать на каждый site.

Примеры курса:

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
Letter Head конкретной организации
```

`Service Request Auto Assignment` из L9 намеренно не входит в универсальные fixtures L11.

## Exported customization

Custom Field, Property Setter и Custom Permissions могут быть экспортированы штатным `Export Customizations`.

Экспортированный JSON — механизм синхронизации выбранной кастомизации, а не универсальная команда удаления старых Custom Field/Property Setter на других site.

## Working data

Конкретные:

```text
Facility Location
Equipment
Service Request
ToDo
Comments
Files
Notification Log
```

— рабочие Documents текущего site.

Они не превращаются в fixtures только ради переноса учебного содержимого.

---

# Проверка переносимости

Финальный основной урок создаёт новый чистый site:

```text
clean Frappe site
+ facility_ops
+ install-app
+ migrate
= рабочая конфигурация приложения
```

На новом site должна восстановиться переносимая конфигурация приложения, но не тестовые рабочие данные и не локальное распределение исполнителей.

---

# Правило отбора тем

Тема входит в основной маршрут, если одновременно:

1. это штатная возможность Frappe `v16.32.0`;
2. она нужна трём основным DocType или основному процессу;
3. её можно воспроизвести руками и проверить;
4. ради неё не приходится создавать лишнюю бизнес-сущность;
5. упражнение действительно присутствует в уроке.

Если хотя бы один пункт не выполняется, тема идёт в Lab или Later.

Матрица не является поводом раздувать приложение.

Список источников находится в [REFERENCES.md](REFERENCES.md).