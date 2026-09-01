# Границы базового практикума

Базовая версия — **Frappe Framework v16.32.0**.

Практикум показывает Frappe как платформу приложений через один app:

```text
facility_ops
```

и одну минимальную модель:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Собственную бизнес-логику на Python или JavaScript в базовом курсе не пишем.

Это не запрет на:

```text
штатные expression-поля
hooks.py для fixtures/config
Frappe-generated files
exported customizations
```

Запрет относится к собственной логике, которая дублировала бы штатный механизм платформы.

---

# Проверенная версия и источники

Приоритет:

1. фактический стенд `v16.32.0`;
2. exact source tag `v16.32.0`;
3. официальная документация Frappe;
4. moving `version-16` только для будущих изменений.

Если общая документация расходится с exact source, базовый курс следует exact source.

---

# Учебный стенд

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Стек стенда фиксируется в:

```text
projects/00-lab/SETUP_WSL2.md
```

---

# Постоянное ядро

Только:

```text
Facility Location
Equipment
Service Request
```

В базовом ядре нет отдельных:

```text
Equipment Type
Equipment Movement
Inspection
Maintenance Work
Department
Team
Technician business entity
Requester business entity
Status reference
Priority reference
```

Специальному механизму разрешён временный объект в Lab, но это не делает его частью итоговой модели.

---

# Инварианты модели

## Equipment

Category:

```text
HVAC
Electrical
IT
Other
```

Status:

```text
Active
Out of Service
Retired
```

`Equipment.notes` после L5 имеет Permission Level 1.

## Service Request

Mandatory:

```text
Subject
Location
Description
Priority
```

Optional:

```text
Equipment
Target Date
Attachment
```

Status:

```text
New
Assigned
In Progress
Resolved
Closed
```

До L7 это Select, после L7 — то же поле `status` как Workflow State Field.

Любой канал создания `Service Request`, включая Web Form и automation test data, обязан соблюдать Mandatory-модель.

---

# Что входит в Core L0–L11

## Платформа

- WSL2 / Debian стенд;
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
- `install-app`;
- `bench migrate`;
- второй clean site.

`install-app` и `migrate` не считаются двумя обязательными половинами первоначальной установки. В `v16.32.0` install flow уже синхронизирует app source, fixtures/customizations; L11 использует последующий migrate как проверку штатной повторной синхронизации.

## Модель данных

- DocType / DocField / Document;
- `name`;
- Standard DocType своего app;
- Tree;
- основные Field Types;
- Link;
- Naming;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Form / List / Tree;
- Allow Import;
- Data Import / Export.

## Работа с данными

- Filters;
- Sorting текущего List View;
- Saved Filters;
- Search;
- Data Import template;
- negative import test;
- Bulk Edit;
- Export;
- Attachments;
- Timeline.

Отдельная metadata-настройка `Default Sort` не считается изученной.

## Пользователи и права

- User;
- System User;
- Website User;
- Guest;
- Role;
- Role Permission Manager;
- Read / Write / Create / Delete;
- Report / Export / Import;
- If Owner / Only If Creator;
- Permission Level;
- User Permission;
- Share.

`User Permission` и `Share` входят в Core как **временный изолированный эксперимент L5**. Они не остаются ограничением основных Technician после завершения урока.

Постоянные основные пользователи после L5:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

`technician.two@example.com` создаётся только в L9.

## Совместная работа

- Assign To;
- ToDo;
- Due Date;
- Comments;
- Timeline;
- Tags;
- Kanban.

Ключевое различие:

```text
Permission = доступ
Assignment = конкретная работа
Status     = состояние документа
```

## Workflow

- обычный Status до L7;
- Workflow;
- Workflow State;
- Workflow Action Master;
- Workflow Transition;
- Allowed Role;
- Only Allow Edit For;
- Workflow Action;
- простая Condition;
- существующий `Service Request.status` как state field.

Workflow не назначает человека.

## Контроль

- один Report Builder;
- Filters;
- Group By;
- Count;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcut;
- Quick List;
- role-based access к Workspace/Chart.

`Sum / Average` не считаются покрытыми Core.

## Automation

- Standard Notification;
- System Notification;
- Notification Filters;
- date-based Notification;
- Preview / Get Alerts for Today;
- Assignment Rule;
- Round Robin;
- Due Date Based On;
- Close Condition;
- штатные expression-поля;
- scheduler/background jobs;
- manual execution штатного scheduler handler.

Load Balancing — Optional внутри L9. После проверки Assignment Rule возвращается в Round Robin.

Глобальный Assignment Rule L9 допустим только потому, что оба основных Technician не имеют постоянного Location User Permission.

Assignment Rule с конкретными Users остаётся site-specific configuration.

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

Web Form работает поверх `Service Request` и сохраняет его Mandatory-модель. В частности:

```text
Description = Mandatory
```

Status не редактируется как поле внешней формы.

## Поставка

- Standard source;
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

После L11 активным site снова становится:

```text
facility-ops.localhost
```

Clean site остаётся только контрольным стендом.

---

# Что входит в Labs

## Lab A — Child Table

- Child DocType;
- Table;
- Float;
- Currency;
- `parent` / `parenttype` / `parentfield` / `idx`.

Временный `Work Log` удаляется.

## Lab B — DocStatus

- Is Submittable;
- Draft;
- Submit;
- Cancel;
- Amend;
- DocStatus;
- Allow on Submit;
- Audit Trail.

Используется временный `Service Report`; `Service Request` не делаем Submittable.

## Lab C — Auto Repeat

- Allow Auto Repeat;
- Auto Repeat;
- Assignee;
- scheduler;
- generated Document;
- cleanup `auto_repeat` Custom Field.

L9 Assignment Rule временно отключается для чистого теста и возвращается после лаборатории.

## Lab D — Customize Form

- Customize Form;
- Custom Field;
- Property Setter;
- Module for Export;
- Export Customizations;
- Sync on Migrate;
- точечный rollback.

Lab D не создаёт Custom DocType и не изучает DocType Layout.

## Lab E — Print / PDF

- Print View;
- Print Format;
- Print Format Builder;
- Standard Print Format;
- Letter Head;
- Print Settings;
- browser Print;
- PDF через chrome.

Standard Print Format остаётся app-owned, временный Letter Head удаляется.

## Lab F — специальные возможности

- Single;
- Dynamic Link;
- Table MultiSelect;
- Percent;
- Time;
- Duration;
- Barcode;
- Signature;
- Geolocation;
- Attachment Gallery;
- Markdown Editor;
- Data Masking;
- Calendar/Gantt на штатном Event.

Собственная Calendar/Gantt JS config — Later.

---

# Что сознательно Later

- Custom DocType как пользовательская runtime-сущность;
- DocType Layout;
- Virtual DocType;
- Query Report;
- Script Report;
- собственные Python controllers/hooks business logic;
- собственный Client Script / JS business logic;
- custom HTML/Jinja Print Format как обязательная практика;
- собственный Calendar/Gantt JS config;
- Sum/Average analytics;
- Email permission;
- Custom Permission Types;
- внешние интеграции/API как отдельный блок;
- полноценный portal/frontend;
- production deployment/hardening.

---

# Критерий выхода из базового курса

Ученик должен уметь объяснить и показать на живом стенде:

```text
DocType / Document / metadata
app source / site config / working data
permissions / assignment / workflow
Desk / Web Form
reports / automation
fixtures / customizations / clean site
```

и пройти L0 → L11 без ручного исправления противоречий между уроками.