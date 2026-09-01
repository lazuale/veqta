# Дорожная карта практикума

Курс развивается последовательно на одном app — `facility_ops`.

Основная модель:

```text
Facility Location
      │
      ├────────► Equipment
      │             │
      └─────────────┴────────► Service Request
```

Ядро не расширяется ради отдельных функций Frappe. Специальные механизмы идут в лаборатории.

---

# L0. Основа приложения

## Результат

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
Frappe: v16.32.0
```

## Практика

1. Поднять стенд по `projects/00-lab/SETUP_WSL2.md`.
2. Проверить точную версию Frappe.
3. Создать `facility_ops`.
4. Создать site и установить app.
5. Включить Developer Mode.
6. Найти Module, `modules.txt`, `hooks.py`, структуру app.
7. Пройти базовую навигацию Desk.
8. Проверить scheduler/workers.
9. Создать временный Standard DocType `Lab Note`.
10. Создать обычный Document.
11. Посмотреть generated files и Git diff.
12. Удалить `Lab Note` штатно.
13. Оставить чистый app перед L1.

## Ученик должен объяснить

- Bench / site / app / Module;
- DocType / Document;
- metadata / рабочие данные;
- Developer Mode;
- что хранит Git.

---

# L1. Места эксплуатации

## Задача

Создать структуру мест.

## Создаём

```text
Facility Location
```

Тип: Tree DocType.

Пример данных:

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

## Изучаем

- Standard DocType;
- Tree DocType;
- Naming;
- Tree View;
- Form View;
- List View;
- Documents;
- metadata и Git.

## Практика

1. Создать `Facility Location` в Module `Facility Operations`.
2. Настроить понятное имя документа.
3. Построить иерархию минимум из двух уровней.
4. Открыть те же записи через Tree, List и Form.
5. Найти JSON DocType в app.
6. Посмотреть Git diff.
7. Commit.

## Приёмка

Ученик может объяснить, когда нужен Tree, а когда обычный DocType.

---

# L2. Реестр оборудования

## Задача

Создать реестр оборудования и связать его с местами.

## Создаём

```text
Equipment
```

Поля:

| Поле | Тип |
|---|---|
| Equipment Code | Data |
| Equipment Name | Data |
| Location | Link → Facility Location |
| Category | Select |
| Status | Select |
| Serial Number | Data |
| Commissioning Date | Date |
| Photo | Attach Image |
| Notes | Small Text |

Status:

```text
Active
Out of Service
Retired
```

## Изучаем

- Data / Select / Date / Link / Attach Image / Small Text;
- Mandatory / Default;
- Naming;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Section / Column / Tab Break;
- Form View;
- List View.

## Практика

1. Создать `Equipment`.
2. Разложить поля по понятной форме.
3. Настроить Naming.
4. Настроить Title Field и Search Fields.
5. Включить Track Changes.
6. Проверить Quick Entry там, где он удобен.
7. Создать 5–10 записей вручную.
8. Изменить одну запись и посмотреть Timeline/Version.
9. Посмотреть JSON и Git diff.
10. Commit.

## Приёмка

Ученик различает:

- Link и Select;
- `name` и Title Field;
- metadata и Document.

---

# L3. Работа с данными

## Задача

Научиться работать с реестром как с данными, а не только проектировать форму.

Новых DocType нет.

## Изучаем

- List View;
- Filters;
- Sorting;
- Saved Filters;
- Search;
- Data Import;
- Export;
- массовые действия;
- attachments;
- Timeline.

## Практика

1. Подготовить CSV минимум на 30 единиц оборудования.
2. Включить Allow Import для Equipment.
3. Импортировать данные через Data Import.
4. Проверить ошибки импорта на намеренно неправильной строке.
5. Создать фильтры по Location, Status и Category.
6. Сохранить полезный filter.
7. Отсортировать список.
8. Выполнить одну безопасную массовую операцию.
9. Экспортировать отфильтрованную выборку.

## Приёмка

Ученик умеет загрузить, найти, отфильтровать и выгрузить данные штатными средствами.

---

# L4. Заявка

## Задача

Добавить основной рабочий процесс приложения.

## Создаём

```text
Service Request
```

Поля:

| Поле | Тип |
|---|---|
| Subject | Data |
| Location | Link → Facility Location |
| Equipment | Link → Equipment |
| Description | Text |
| Priority | Select |
| Status | Select |
| Target Date | Date |
| Attachment | Attach |

Priority:

```text
Low
Medium
High
```

Status:

```text
New
Assigned
In Progress
Resolved
Closed
```

`Location` обязателен. `Equipment` необязателен.

## Изучаем

- рабочий DocType;
- несколько Link;
- обязательные/необязательные связи;
- Status как обычное поле;
- Priority;
- Attach;
- Track Changes;
- фильтры рабочего списка.

## Практика

Создать минимум пять сценариев:

1. проблема конкретного Equipment;
2. проблема Location без Equipment;
3. High Priority;
4. заявка с Target Date;
5. заявка с attachment.

Затем вручную провести несколько заявок через Status.

## Приёмка

Приложение уже решает минимальную задачу без пользователей, Workflow и автоматизации.

---

# L5. Пользователи и права

## Задача

Сделать приложение многопользовательским.

## Роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

## Изучаем

- User;
- System User;
- Role;
- Role Permission Manager;
- Read / Write / Create / Delete;
- If Owner;
- Permission Level;
- User Permission;
- Share;
- Report / Export / Import permissions на базовом уровне.

## Практика

1. Создать минимум трёх учебных пользователей.
2. Создать роли.
3. Настроить права для Facility Location, Equipment и Service Request.
4. Проверить каждую роль отдельным входом.
5. Проверить If Owner.
6. Ограничить данные через User Permission.
7. Разово открыть документ через Share.
8. Проверить отрицательные сценарии.

## Приёмка

Ученик понимает:

```text
Permission = что разрешено
Assignment = какая конкретная работа назначена
```

---

# L6. Совместная работа

## Задача

Организовать работу исполнителей без новых предметных сущностей.

## Изучаем

- Assign To;
- ToDo;
- Due Date;
- Comments;
- Timeline;
- Tags;
- Kanban.

## Практика

1. Supervisor назначает Service Request технику через Assign To.
2. Найти созданный ToDo.
3. Проверить личную очередь техника.
4. Добавить комментарий.
5. Проверить Timeline.
6. Добавить Tags.
7. Создать Kanban по Status.
8. Пройти несколько заявок вручную.

## Приёмка

Ученик не создаёт поле `Assigned Technician`, потому что штатное назначение уже решает эту задачу.

---

# L7. Workflow

## Задача

Ограничить допустимые переходы Service Request.

До урока Status меняется вручную.

## Процесс

```text
New
 ↓
Assigned
 ↓
In Progress
 ↓
Resolved
 ↓
Closed
```

## Изучаем

- Workflow;
- Workflow State;
- Workflow Transition;
- Allowed Role;
- Workflow Action;
- условия переходов на базовом уровне.

## Практика

1. Зафиксировать, что обычный Select не контролирует маршрут.
2. Создать Workflow для Service Request.
3. Использовать существующее поле Status/согласованное workflow state field без дублирования смысла.
4. Назначить роли переходам.
5. Проверить правильные переходы.
6. Проверить запрещённые переходы.
7. Посмотреть Workflow Action.

## Приёмка

Ученик объясняет разницу между полем состояния и правилами переходов.

---

# L8. Контроль работы

## Задача

Собрать рабочий интерфейс руководителя на накопленных данных.

## Изучаем

- Report Builder;
- Filters;
- Group By;
- Count / Sum / Average там, где применимо;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcuts;
- Quick Lists;
- Workspace access.

## Практика

Создать:

### Reports

- Service Requests by Status;
- Service Requests by Priority;
- Service Requests by Location;
- Service Requests by Equipment.

### Number Cards

- Open Requests;
- Overdue Requests;
- High Priority Requests.

### Dashboard Chart

- Requests by Status.

### Workspace

```text
Facility Operations

[Open Requests] [Overdue] [High Priority]

New Request
Equipment
Locations

Requests by Status
```

## Приёмка

Workspace отвечает на рабочие вопросы, а не демонстрирует все блоки Frappe.

---

# L9. Автоматизация

## Задача

Автоматизировать то, что уже умеем делать вручную.

## Изучаем

- Notification;
- System Notification;
- Notification Filters;
- date-based Notification;
- Assignment Rule;
- Round Robin или Load Balancing;
- PythonExpression только в штатном поле механизма;
- scheduler/background jobs.

## Практика

1. Notification на новую Service Request.
2. Notification на просроченную Service Request.
3. Assignment Rule для автоматического назначения техников.
4. Сравнить автоматическое назначение с ручным Assign To.
5. Проверить scheduler и фоновые задания.

## Приёмка

Никакого собственного Python/JS для этих сценариев.

---

# L10. Web Form

## Задача

Открыть внешний вход в существующий Service Request.

## Изучаем

- Web Form;
- Route;
- Anonymous responses;
- Login Required;
- Website User;
- Guest;
- Apply document permissions;
- attachments;
- Show List / editing на подходящем сценарии;
- Standard Web Form.

## Практика

1. Создать Web Form для Service Request.
2. Проверить создание документа из браузера.
3. Проверить Guest-сценарий.
4. Проверить Login Required.
5. Проверить Website User.
6. Проверить attachment.
7. Убедиться, что созданный документ появляется в обычном Desk-процессе.

Цепочка:

```text
Web Form
   ↓
Service Request
   ↓
Assignment / Workflow
   ↓
Desk
```

---

# L11. Переносимость приложения

## Задача

Понять, что является приложением и как оно восстанавливается на чистом site.

## Классификация

Каждый созданный объект отнести к одному типу:

```text
Standard metadata
site-specific customization
configuration record
working data
```

## Изучаем

- Git как поставку app metadata;
- fixtures;
- `bench export-fixtures`;
- Export Customizations;
- `install-app`;
- `bench migrate`;
- clean site.

## Практика

1. Проверить Git app.
2. Определить, какие Roles, Workflow, Workspace, Notification, Assignment Rule и Web Form должны поставляться с app.
3. Добавить fixtures только для реально нужных конфигурационных записей.
4. Если Lab D оставил нужную кастомизацию — экспортировать её.
5. Создать новый чистый site.
6. Установить `facility_ops`.
7. Выполнить migrate.
8. Проверить конфигурацию.
9. Убедиться, что рабочие Equipment и Service Request не приехали как fixtures.

## Финальная приёмка

На чистом site можно заново пройти путь:

```text
создать Location
создать Equipment
создать Service Request
назначить
провести Workflow
увидеть в Workspace
создать через Web Form
```

---

# Лаборатории

## Lab A. Child Table

Временная таблица `Work Log` внутри Service Request:

| Поле | Тип |
|---|---|
| Description | Data / Small Text |
| Hours | Float |
| Cost | Currency |

Изучить Child DocType / Table и затем решить, оставлять ли таблицу.

---

## Lab B. Draft / Submit / Cancel / Amend

Создать маленький `Service Report` только для изучения:

- Is Submittable;
- Draft;
- Submit;
- Cancel;
- Amend;
- DocStatus;
- Allow on Submit;
- Audit Trail.

Не переносить этот lifecycle на Service Request только ради урока.

---

## Lab C. Auto Repeat

Создать повторяющуюся профилактическую Service Request.

Изучить:

- Allow Auto Repeat;
- Auto Repeat;
- Assignee;
- scheduler.

---

## Lab D. Customize Form

На конкретном site добавить в Equipment локальное поле.

Изучить:

- Customize Form;
- Custom Field;
- Property Setter;
- DocType Layout при необходимости;
- Export Customizations.

После лаборатории оставить изменение только если оно действительно нужно итоговому приложению.

---

## Lab E. Print / PDF

На Service Request изучить:

- Print View;
- Print Format Builder;
- Letter Head;
- PDF.

---

## Lab F. Специальные возможности

Коротко проверить без изменения ядра:

- Single DocType;
- Dynamic Link;
- Table MultiSelect;
- Percent;
- Time / Duration;
- Barcode;
- Signature;
- Geolocation;
- Attachment Gallery;
- Gantt.

---

# Правило перехода между уроками

Следующий урок начинается, когда:

1. текущий результат работает;
2. ученик может объяснить использованные механизмы;
3. понятна разница между metadata, configuration и working data;
4. Git чистый или изменения осознанно зафиксированы.
