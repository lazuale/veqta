# Дорожная карта практикума

Курс развивается последовательно на одном app — `facility_ops`.

Основная модель неизменна:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Ядро не расширяется ради отдельных функций Frappe. Всё, чему не нужно постоянное место в этой модели, изучается в лабораториях.

Базовая версия курса — **Frappe Framework v16.32.0**.

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
2. Проверить точную версию Frappe и зависимости стенда.
3. Создать `facility_ops`.
4. Создать site и установить app.
5. Включить Developer Mode.
6. Найти Module, `modules.txt`, `hooks.py` и структуру app.
7. Пройти базовую навигацию Desk.
8. Проверить scheduler и workers.
9. Создать временный Standard DocType `Lab Note`.
10. Создать обычный Document.
11. Посмотреть generated files и Git diff.
12. Удалить `Lab Note` штатно.
13. Оставить чистый app перед L1.

## После урока ученик различает

```text
Bench
Site
App
Module
DocType
Document
metadata
working data
Git
```

---

# L1. Места эксплуатации

## Создаём

```text
Facility Location
```

Тип: Tree DocType.

Пример:

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
- Tree / List / Form View;
- group и leaf;
- nested-set infrastructure Frappe;
- metadata и Documents;
- Git.

## Приёмка

Ученик понимает, почему дерево — это структура мест, а не обычный справочник со случайным `Parent`.

---

# L2. Реестр оборудования

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
- Mandatory;
- Naming `field:equipment_code`;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Section / Column Break;
- Form / List View;
- Link на Tree DocType.

## Практика

Создать рабочий набор Equipment вручную, проверить Quick Entry, поиск, отрицательный duplicate и связь с Location.

---

# L3. Работа с данными

Новых DocType нет.

## Изучаем

- List View;
- Filters;
- Sorting текущей выборки;
- Saved Filters;
- Search;
- Allow Import;
- Data Import;
- Export;
- Bulk Edit;
- metadata против рабочих данных.

## Практика

1. Включить `Allow Import` у Equipment.
2. Скачать **штатный шаблон Frappe** из Data Import.
3. Подготовить **10 новых Equipment** `EQ-0010` … `EQ-0019`.
4. Импортировать их через `Insert New Records`.
5. Отдельно проверить ошибочный импорт со ссылкой на несуществующий Location.
6. Создать полезные фильтры и персональный Saved Filter.
7. Проверить сортировку List View.
8. Экспортировать отфильтрованную выборку.
9. Выполнить безопасный Bulk Edit двух записей и вернуть исходное состояние.
10. Зафиксировать в Git только изменение `Equipment.allow_import`.

## Приёмка

Ученик умеет загрузить, найти, отфильтровать, массово изменить и выгрузить Documents и не путает это с поставкой приложения.

---

# L4. Service Request

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
- обязательную и необязательную Link-связь;
- Priority;
- Status как обычный Select до Workflow;
- Attach;
- Track Changes;
- naming `SR-.#####`;
- фильтры рабочего списка.

## Практика

Создать рабочий набор заявок для следующих уроков и вручную провести несколько из них через Status.

---

# L5. Пользователи и права

## Роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

## Базовые учебные пользователи

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

Все четыре — System User без System Manager.

## Изучаем

- User;
- System User;
- Role;
- Role Permission Manager;
- Read / Write / Create / Delete;
- Report / Export / Import там, где они реально нужны;
- If Owner;
- Permission Level;
- User Permission;
- Share.

## Практика

1. Настроить права на три core DocType.
2. Проверить каждую роль отдельным входом.
3. Доказать `If Owner` двумя Requester.
4. Перевести `Equipment.notes` на Permission Level 1 и дать доступ Supervisor.
5. Ограничить `technician.one@example.com` через User Permission на `Room 101` для Service Request.
6. Открыть один чужой документ точечно через Share.
7. Проверить отрицательные сценарии.

Главное:

```text
Permission = что разрешено
Assignment = какая конкретная работа назначена
```

---

# L6. Совместная работа

Новых предметных DocType нет.

## Изучаем

- Assign To;
- ToDo;
- Due Date;
- Comments;
- Timeline;
- Tags;
- Kanban.

## Практика

1. Supervisor назначает Service Request Technician через Assign To.
2. Найти созданный ToDo и проверить reference на заявку.
3. Проверить очередь Technician.
4. Сравнить Assignment и `Service Request.status`.
5. Добавить Comment и посмотреть Timeline.
6. Закрыть assignment и убедиться, что это не закрывает Service Request автоматически.
7. Проверить duplicate active assignment.
8. Добавить полезные Tags.
9. Создать Kanban по `Status` и убедиться, что карточки — те же Service Request Documents.

Kanban здесь учебный. После появления Workflow в L7 Status-Kanban удаляется, чтобы процесс имел один понятный интерфейс переходов.

---

# L7. Workflow

## Процесс

```text
New
 │ Mark Assigned / Facility Supervisor
 ▼
Assigned
 │ Start Work / Facility Technician
 ▼
In Progress
 │ Resolve / Facility Technician
 ▼
Resolved
 │ Close / Facility Supervisor
 ▼
Closed
```

## Принцип

Используется существующее поле:

```text
Service Request.status
```

как единственный `Workflow State Field`.

Второй `workflow_state` не создаётся.

Все состояния имеют `docstatus = 0`: Service Request не становится Submittable.

## Изучаем

- Workflow;
- Workflow State;
- Workflow Action Master;
- Workflow Transition;
- Allowed Role;
- Only Allow Edit For;
- Workflow Action;
- простую Condition.

## Практика

1. Сделать `status` Read Only.
2. Создать пять Workflow State.
3. Создать четыре Action Master.
4. Создать и активировать `Service Request Workflow`.
5. Проверить переходы под Requester, Technician и Supervisor.
6. Проверить запрещённые переходы.
7. Коротко проверить Condition по Priority и вернуть линейную схему.
8. Проверить Timeline и Workflow Action records.
9. Удалить Status-Kanban из L6.

## Граница Kanban

В `v16.32.0` Kanban меняет выбранное поле через `frappe.set_value`, который приводит к обычному `doc.save()` и workflow validation. Но это не тот же путь, что штатный `apply_workflow`: Workflow Action остаётся единственным учебным способом выполнять переход процесса.

---

# L8. Контроль работы

Новых предметных DocType нет.

## Результат

Создаём **один** рабочий набор контроля:

### Report Builder

```text
Service Requests Overview
```

Поля заявки + `Group By = Status` + `Count`.

### Number Cards

```text
Open Requests
High Priority Requests
Closed Requests
```

### Dashboard Chart

```text
Service Requests by Status
```

### Workspace

```text
Facility Operations
```

Workspace предназначен `Facility Supervisor` и содержит:

- три Number Card;
- один Dashboard Chart;
- Shortcuts на Service Request, Equipment, Facility Location и Report;
- одну Quick List Service Request.

## Изучаем

- Report Builder;
- Filters;
- Group By;
- Count;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcut;
- Quick List;
- Workspace / Chart roles.

SQL, отдельные таблицы статистики и собственная BI-логика не нужны.

---

# L9. Автоматизация

Новых предметных DocType нет.

## Изучаем

- Notification;
- System Notification;
- Filters;
- date-based Notification;
- Assignment Rule;
- Round Robin;
- Due Date Based On;
- Close Condition;
- scheduler/background jobs;
- штатные Python expressions внутри механизмов Frappe.

## Практика

1. Создать Standard Notification `New Service Request`.
2. Создать date-based `Overdue Service Request`.
3. Проверить Preview / Alerts for Today.
4. Запустить штатный daily notification job вручную для немедленного теста.
5. Создать второго Technician.
6. Создать Assignment Rule `Service Request Auto Assignment`.
7. Настроить Round Robin между двумя Technician.
8. Связать Due Date ToDo с `Target Date`.
9. Проверить `Close Condition = status == "Closed"`.
10. Сравнить ручной Assign To и Assignment Rule.
11. Убедиться, что Assignment Rule не двигает Workflow.
12. В самостоятельной практике кратко проверить Load Balancing и вернуть Round Robin.

Assignment Rule остаётся configuration record текущего site, потому что содержит конкретных Users. В L11 это решение подтверждается: правило не входит в универсальные fixtures приложения.

---

# L10. Web Form

## Задача

Открыть внешний вход в **тот же** Service Request.

```text
Browser
  ↓
Web Form
  ↓
Service Request
  ↓
Assignment / Notification / Workflow
  ↓
Desk
```

## Изучаем

- Standard Web Form;
- Route;
- Anonymous responses;
- Guest;
- Login Required;
- Website User;
- Allow Edit;
- Show List;
- Apply Document Permissions;
- Link options;
- attachments.

## Практика

1. Создать `Report a Facility Issue`, route `facility-request`.
2. Временно проверить Guest submission без публикации внутренних справочников.
3. Проверить attachment.
4. Перевести форму в финальный `Login Required`.
5. Создать Website User.
6. Проверить создание и редактирование своих ответов.
7. Проверить owner-границу.
8. Переключить `Apply Document Permissions` и сравнить поведение.
9. Оставить финальную форму без editable `Status`.

Web Form не создаёт второй backend-процесс.

---

# L11. Переносимость приложения

## Цель

Доказать, что `facility_ops` восстанавливается на чистом site без копирования старой базы.

## Классификация

### Standard source app

Уже поставляются исходниками и **не требуют fixtures**:

```text
Facility Location / Equipment / Service Request DocType
Standard Report
Standard Number Card
Standard Dashboard Chart
Standard Workspace
Standard Notification
Standard Web Form
```

### Универсальная app configuration

Поставляется fixtures:

```text
Facility Requester
Facility Technician
Facility Supervisor
Workflow State
Workflow Action Master
Service Request Workflow
```

### Site-specific configuration

Не поставляется универсальными fixtures:

```text
Users
User Permission
Share
Service Request Auto Assignment
```

Assignment Rule здесь site-specific, потому что его Users зависят от конкретного развёртывания.

### Working data

Не входит в поставку app:

```text
Facility Location Documents
Equipment Documents
Service Request Documents
ToDo
Comments
Files
Notification Log
Workflow Action records
```

## Практика

1. Экспортировать Custom Permissions трёх core DocType через Export Customizations.
2. Добавить точные fixtures в `hooks.py`.
3. Выполнить `bench export-fixtures`.
4. Проверить fixture JSON на отсутствие Users и рабочих Documents.
5. Создать `facility-ops-clean.localhost`.
6. Установить `facility_ops`.
7. Выполнить `migrate`.
8. Проверить Standard metadata, Roles, Workflow, permissions, Workspace, Notifications и Web Form.
9. Убедиться, что рабочие данные и Assignment Rule не приехали.
10. Создать новых site-specific пользователей и минимальные рабочие данные.
11. Вручную настроить локальное назначение и пройти end-to-end.
12. Повторить `migrate` и убедиться в идемпотентности поставки.

---

# Лаборатории

Лаборатории изучают возможности Frappe, которым не нужно постоянное место в core-модели.

## Lab A. Child Table

Временно добавить `Work Log` в Service Request:

```text
Description
Hours
Cost
```

Изучить Child DocType, Table, `parent / parenttype / parentfield / idx`, затем удалить эксперимент.

## Lab B. DocStatus

Временно создать `Service Report` и пройти:

```text
Draft → Submit → Cancel → Amend
```

Изучить Is Submittable, DocStatus, Allow on Submit и Audit Trail. После лаборатории удалить Service Report.

## Lab C. Auto Repeat

Временно включить Auto Repeat для Service Request:

- Allow Auto Repeat;
- Auto Repeat;
- Assignee;
- scheduler;
- generated Document;
- cleanup служебного Custom Field `auto_repeat`.

## Lab D. Customize Form

На Equipment изучить:

- Customize Form;
- Custom Field;
- Property Setter;
- Module for Export;
- Export Customizations;
- Sync on Migrate;
- точечный rollback.

`Custom DocType` и `DocType Layout` в эту лабораторию не входят.

## Lab E. Print / PDF

На Service Request изучить:

- Print View;
- Print Format Builder;
- Standard Print Format;
- Letter Head;
- Print Settings;
- browser Print;
- PDF;
- Chrome PDF generator.

`Service Request Summary` остаётся app-owned Print Format. Учебный Letter Head удаляется.

## Lab F. Специальные возможности

На временном полигоне проверить:

- Single DocType;
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
- Data Masking.

Calendar и Gantt проверяются на штатном `Event` Frappe.

Для собственного DocType в `v16.32.0` эти views требуют calendar JavaScript-конфигурацию `frappe.views.calendar[...]`; собственный JS остаётся за пределами базового курса.

После лаборатории временные DocType удаляются.

---

# Правило перехода между уроками

Следующий урок начинается, когда одновременно выполнено четыре условия:

1. текущий результат работает на фактическом стенде `v16.32.0`;
2. ученик может объяснить использованные механизмы без заученных формулировок;
3. понятно, что изменилось в metadata, configuration, working data и Git;
4. Git clean либо все изменения осознанно зафиксированы.

Если ROADMAP расходится с подробным уроком или фактическим поведением `v16.32.0`, исправляется ROADMAP, а не рабочий урок подгоняется под старую формулировку.