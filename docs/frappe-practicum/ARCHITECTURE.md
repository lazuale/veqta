# Архитектура учебного приложения

Базовая версия — **Frappe Framework v16.32.0**.

Курс использует одно приложение:

```text
facility_ops
```

Его задача намеренно небольшая:

```text
места
  ↓
оборудование
  ↓
заявки
  ↓
назначение работы
  ↓
управляемый процесс
  ↓
контроль и внешний ввод
```

Это учебное приложение для изучения Frappe, а не ERP, CMMS или полноценный Service Desk.

---

# 1. Постоянное предметное ядро

Только три обязательных DocType:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Смысл:

```text
Facility Location = где
Equipment         = что эксплуатируется
Service Request   = что произошло / что нужно сделать
```

Новая бизнес-сущность не создаётся только ради демонстрации функции Frappe.

---

# 2. Facility Location

Tree DocType.

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

Nested-set поля (`parent`, `lft`, `rgt`, `is_group`) обслуживает Frappe. Ученик не проектирует их вручную.

---

# 3. Equipment

| Поле | Тип | Обязательность |
|---|---|---:|
| Equipment Code | Data | Yes |
| Equipment Name | Data | Yes |
| Location | Link → Facility Location | Yes |
| Category | Select | Yes |
| Status | Select | Yes |
| Serial Number | Data | No |
| Commissioning Date | Date | No |
| Photo | Attach Image | No |
| Notes | Small Text | No |

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

Naming:

```text
field:equipment_code
```

Title Field:

```text
equipment_name
```

`Category` остаётся Select. Значения вроде `Pump` нельзя использовать без изменения metadata: название оборудования и значение Category — разные вещи.

После L5:

```text
Equipment.notes → Permission Level 1
```

и Level 1 выдаётся Facility Supervisor.

---

# 4. Service Request

| Поле | Тип | Обязательность |
|---|---|---:|
| Subject | Data | **Yes** |
| Location | Link → Facility Location | **Yes** |
| Equipment | Link → Equipment | No |
| Description | Text | **Yes** |
| Priority | Select | **Yes** |
| Status | Select | Yes, default New |
| Target Date | Date | No |
| Attachment | Attach | No |

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

Naming:

```text
SR-.#####
```

Title Field:

```text
subject
```

Инвариант курса:

```text
Subject + Location + Description + Priority
```

обязательны во всех каналах создания — Desk, automation test data и Web Form.

`Equipment` остаётся необязательным.

До L7 `status` — обычный Select. В L7 это же поле становится Workflow State Field и Read Only. Второе `workflow_state` не создаётся.

---

# 5. Permissions, Assignment и Status — три разные оси

```text
Permission
= может ли пользователь работать с Document

Assignment
= кому поручена конкретная работа

Status / Workflow
= в каком состоянии находится Service Request
```

Эти понятия не объединяются в одно поле.

В core-модели нет:

```text
Assigned Technician
Technician field
Assignee field
```

Назначение:

```text
Service Request
      ↓ Assign To / Assignment Rule
ToDo
      ↓
User
```

---

# 6. Роли и постоянная модель доступа

Роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Модель:

```text
Requester
→ Read Location / Equipment
→ Create Service Request
→ Read/Write только свои Service Request через If Owner

Technician
→ Read Location / Equipment
→ Read/Write Service Request
→ получает конкретную работу через ToDo

Supervisor
→ управляет рабочими данными
→ видит все Service Request
→ выполняет управляющие Workflow transitions
```

Ключевой архитектурный выбор после consistency-аудита:

```text
основные Technician
не имеют постоянного User Permission по Location
```

`User Permission` и `Share` изучаются в L5 на временном `technician.restricted@example.com`, затем Share/User Permission удаляются, пользователь отключается.

Почему:

```text
глобальный Assignment Rule
не должен назначать человеку Document,
который тот не может открыть
```

`technician.two@example.com` впервые появляется только в L9.

---

# 7. Workflow

Итоговый маршрут:

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

Все states:

```text
docstatus = 0
```

`Service Request` не становится Submittable.

Workflow State Field:

```text
Service Request.status
```

Workflow управляет переходами, но не назначает человека.

Операция Supervisor:

```text
Assign To technician
+
Mark Assigned
```

---

# 8. Kanban

L6 временно создаёт:

```text
Service Request Status Board
```

по `Service Request.status`.

Он показывает те же Documents, что List/Form.

После активации Workflow в L7 доска удаляется из итоговой конфигурации.

Причина:

```text
Kanban field update
→ обычный save и workflow validation

но

Kanban field update
≠ apply_workflow / Workflow Action lifecycle
```

Для одного процесса оставляем один основной интерфейс переходов — Workflow Actions.

---

# 9. Контроль работы

L8 читает те же `Service Request`, не создавая аналитических таблиц:

```text
Service Requests Overview  → Report Builder
Open Requests              → Number Card
High Priority Requests     → Number Card
Closed Requests            → Number Card
Service Requests by Status → Dashboard Chart
Facility Operations        → Workspace
```

```text
рабочие данные
= Service Request Documents

Report/Card/Chart/Workspace
= представления и app configuration
```

---

# 10. Automation

## Notification

```text
Service Request
→ Notification
→ Notification Log
```

Используются System Notification и date-based Notification.

`Overdue Service Request` в курсе означает точный test case:

```text
Days After = 1
→ один день после Target Date
```

## Assignment Rule

```text
Service Request
→ Service Request Auto Assignment
→ Assign To mechanism
→ ToDo
```

Финальный алгоритм:

```text
Round Robin
```

Users:

```text
technician.one@example.com
technician.two@example.com
```

Оба имеют одинаковую базовую область доступа к Service Request.

Load Balancing проверяется опционально и после теста правило возвращается в Round Robin.

Assignment Rule не меняет Workflow state.

Так как правило содержит конкретных Users site, оно является:

```text
site-specific configuration
```

и не входит в universal fixtures L11.

---

# 11. Web Form

L10 не создаёт второй внешний DocType.

```text
Browser
→ Report a Facility Issue
→ Service Request
→ Assignment Rule
→ Workflow
→ Desk
```

Web Form должен сохранять инварианты underlying DocType:

```text
Subject     Mandatory
Location    Mandatory
Equipment   Optional
Description Mandatory
Priority    Mandatory
```

Guest проверяется временно.

Финальный режим:

```text
Login Required = Yes
Anonymous = No
Show List = Yes
Allow Edit = Yes
Apply Document Permissions = No
```

Website User работает со своими ответами через Web Form owner/website permission model. Он не получает роль Facility Requester только ради этого сценария.

Status не выводится как editable поле Web Form.

---

# 12. Поставка приложения

Четыре слоя:

```text
1. Standard source
2. app configuration
3. site-specific configuration
4. working data
```

## Standard source

```text
3 core DocType
Report
Number Cards
Dashboard Chart
Workspace
Notifications
Web Form
```

## Fixtures

```text
Facility Requester / Technician / Supervisor roles
Workflow States
Workflow Action Masters
Service Request Workflow
```

## Exported customizations

```text
Custom DocPerm
```

## Site-specific

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

## Working data

```text
Facility Location Documents
Equipment Documents
Service Request Documents
ToDo
Comments
Files
Logs
```

На clean site `install-app` выполняет первоначальную синхронизацию приложения, включая fixtures/customizations штатного install flow `v16.32.0`.

Последующий `migrate` в L11 проверяет обычный update/convergence путь уже установленного app.

Clean-site тестовые данные обязаны соблюдать ту же модель:

```text
Equipment Category = Other
не Pump

Web Form Service Request
→ Description заполнен
```

После L11 активным site снова становится:

```text
facility-ops.localhost
```

чтобы Labs A–F продолжали основной накопленный стенд.

---

# 13. Лаборатории не расширяют ядро автоматически

```text
Lab A → временный Work Log Child Table → удалить
Lab B → временный Service Report Submittable → удалить
Lab C → временный Auto Repeat → очистить
Lab D → временная Customize Form кастомизация → rollback
Lab E → Standard Print Format остаётся, temporary Letter Head удалить
Lab F → временные special-feature DocType → удалить
```

Правило:

```text
изучили механизм Frappe
≠ обязаны добавить его в постоянную предметную модель
```

---

# 14. Итоговая архитектура

После основного маршрута:

```text
Facility Location
      │
      ├── Equipment
      │
      └── Service Request
              │
              ├── ToDo / Assignment
              ├── Workflow
              ├── Notification
              └── Web Form как внешний канал

Service Request data
      ↓
Report / Cards / Chart / Workspace
```

Переносимое приложение состоит из source + universal configuration. Конкретный site добавляет своих Users, локальное распределение работы и рабочие Documents.