# Архитектура учебного приложения

## 1. Что строим

Курс использует одно приложение — `facility_ops`.

Его задача намеренно небольшая:

```text
хранить места
      ↓
хранить оборудование
      ↓
принимать заявки
      ↓
назначать работу
      ↓
вести заявку до закрытия
```

Это учебное приложение для изучения Frappe Framework, а не попытка построить ERP, CMMS или Service Desk.

Базовая версия — **Frappe Framework v16.32.0**.

---

# 2. Постоянное ядро

В приложении только три обязательных предметных DocType:

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Смысл модели:

```text
Facility Location = где
Equipment         = что эксплуатируется
Service Request   = что произошло / что нужно сделать
```

`Service Request.location` обязателен.

`Service Request.equipment` необязателен: проблема может относиться к помещению или территории без конкретной единицы Equipment.

---

# 3. Facility Location

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

Tree используется потому, что местам нужна настоящая иерархия.

Технические nested-set поля (`parent`, `lft`, `rgt`, `is_group`) создаёт и обслуживает Frappe. Ученик не проектирует их вручную.

---

# 4. Equipment

Основные поля:

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

Naming:

```text
field:equipment_code
```

Title Field:

```text
equipment_name
```

`Category` остаётся Select. Отдельный `Equipment Type` не создаётся, пока реальная задача не докажет необходимость справочника.

После L5 `notes` имеет Permission Level 1 и используется как учебный пример field-level permissions.

---

# 5. Service Request

Основные поля:

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

Naming:

```text
SR-.#####
```

Title Field:

```text
subject
```

До L7 `status` — обычный Select. В L7 то же поле становится Workflow State Field и Read Only для обычной работы.

Второе поле `workflow_state` не вводится.

---

# 6. Assignment не является полем Service Request

В core-модели нет:

```text
Assigned Technician
Technician
Assignee
```

Назначение выполняется штатно:

```text
Service Request
      ↓ Assign To / Assignment Rule
ToDo
      ↓
User
```

Поэтому:

```text
Permission = что пользователь может делать
Assignment = какая конкретная работа ему назначена
Status     = состояние Service Request
```

Эти три понятия не объединяются в одно поле.

---

# 7. Роли и доступ

Учебные роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Модель:

```text
Requester
→ читает Location / Equipment
→ создаёт свои Service Request
→ работает только со своими заявками через If Owner

Technician
→ читает Location / Equipment
→ читает и изменяет разрешённые Service Request
→ получает конкретную работу через ToDo

Supervisor
→ управляет рабочими данными
→ видит все заявки
→ выполняет управляющие Workflow transitions
```

Дополнительно курс отдельно показывает:

- Permission Level;
- User Permission;
- Share;
- Data Masking в Lab F.

Data Masking не заменяет Permission Level: это другой механизм.

---

# 8. Workflow

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

Все состояния:

```text
docstatus = 0
```

`Service Request` не становится Submittable.

Workflow управляет переходами, но не назначает человека.

Поэтому реальная операция Supervisor выглядит так:

```text
Assign To technician
+
Mark Assigned
```

---

# 9. Kanban и Workflow

В L6 Kanban по `Service Request.status` нужен, чтобы показать альтернативное представление одних и тех же Documents.

В L7 он удаляется из итоговой конфигурации.

Причина не в том, что Kanban полностью обходит save validation: в `v16.32.0` его `frappe.set_value` приходит к обычному `doc.save()` и workflow validation.

Проблема другая:

```text
Kanban field update
≠
apply_workflow / Workflow Action
```

Для учебного процесса оставляется один однозначный интерфейс переходов — Workflow Action.

---

# 10. Контроль работы

L8 не создаёт аналитические таблицы.

Используются штатные представления над `Service Request`:

```text
Service Requests Overview        → Report Builder
Open Requests                    → Number Card
High Priority Requests           → Number Card
Closed Requests                  → Number Card
Service Requests by Status       → Dashboard Chart
Facility Operations              → Workspace
```

Главный принцип:

```text
рабочие данные остаются в Service Request
отчёт и Workspace только читают их
```

---

# 11. Автоматизация

L9 добавляет два независимых механизма.

## Notification

```text
Service Request
      ↓
Notification
      ↓
Notification Log
```

Используются System Notification и date-based scheduler.

## Assignment Rule

```text
Service Request
      ↓
Assignment Rule
      ↓
Assign To mechanism
      ↓
ToDo
```

Основной алгоритм курса — Round Robin.

Assignment Rule не двигает Workflow state.

`Service Request Auto Assignment` содержит конкретных учебных Users, поэтому считается site-specific configuration и не входит в универсальные fixtures L11.

---

# 12. Web Form

L10 не создаёт внешний дубль заявки.

```text
Browser
  ↓
Report a Facility Issue
  ↓
Service Request
  ↓
Notification / Assignment / Workflow
  ↓
Desk
```

Финальный Web Form:

- Login Required;
- Website User;
- Show List;
- Allow Edit;
- Apply Document Permissions = No;
- Location и Equipment доступны как Link options;
- Status не редактируется через Web Form.

Guest-сценарий нужен как временная проверка и после неё форма возвращается в Login Required.

---

# 13. Поставка приложения

Курс разделяет четыре слоя.

## 13.1 Standard source

Хранится в `facility_ops` и Git:

```text
Standard DocType
Standard Report
Standard Number Card
Standard Dashboard Chart
Standard Workspace
Standard Notification
Standard Web Form
Standard Print Format
```

## 13.2 Универсальная app configuration

Нужна на любом site, но экспортируется fixtures:

```text
Facility Requester
Facility Technician
Facility Supervisor
Workflow State
Workflow Action Master
Service Request Workflow
```

## 13.3 Site-specific configuration

Не переносится автоматически на любой site:

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
Letter Head конкретного развёртывания
```

## 13.4 Working data

```text
Facility Location Documents
Equipment Documents
Service Request Documents
ToDo
Comments
Files
Notification Log
```

Это содержимое site, а не приложение.

---

# 14. Customize Form

Lab D специально показывает второй путь изменения metadata.

```text
Standard DocType editor
→ изменение исходного определения нашего app

Customize Form
→ Custom Field / Property Setter поверх существующего DocType
```

Экспортированная кастомизация может поставляться через `Export Customizations` и `migrate`.

Но удаление записи из exported JSON не является декларативной командой удалить уже синхронизированный Custom Field/Property Setter на другом site.

---

# 15. Печать

Lab E добавляет переносимый:

```text
Service Request Summary
```

как Standard Print Format.

Отдельно временно создаётся Letter Head учебного site.

```text
Print Format
→ app source

Letter Head
→ site-specific configuration

PDF
→ результат вывода
```

Для лаборатории явно выбирается Chrome PDF generator `v16.32.0`.

---

# 16. Лабораторные объекты

Лаборатории могут временно создавать metadata, но не расширяют core.

## Lab A

```text
Work Log — Child DocType
```

После упражнения удаляется.

## Lab B

```text
Service Report — Submittable DocType
```

После упражнения удаляется.

## Lab C

Временно включает Auto Repeat для Service Request и затем убирает служебную кастомизацию.

## Lab D

Работает поверх существующего Equipment через Customize Form. Custom DocType не создаётся.

## Lab E

Оставляет полезный Standard Print Format, но не создаёт новый business DocType.

## Lab F

Временно создаёт:

```text
Lab Feature Settings — Single
Lab Equipment Link   — Child
Lab Feature Record   — обычный Standard DocType-полигон
```

и проверяет:

```text
Dynamic Link
Table MultiSelect
Check
Percent
Time
Duration
Barcode
Signature
Geolocation
Attachment Gallery
Markdown Editor
Data Masking
```

Calendar и Gantt проверяются на встроенном `Event` Frappe.

Для собственного DocType в `v16.32.0` эти views требуют `frappe.views.calendar[...]`, то есть собственного JavaScript-конфига. Это уже следующий уровень курса.

После Lab F временные DocType удаляются.

---

# 17. Что намеренно не является архитектурой base course

Не вводим без доказанной необходимости:

```text
Equipment Type
Department
Team
Technician
Requester
Status DocType
Priority DocType
Automation Log
Workflow History
Notification Queue
Public Request
```

Не используем в базовом маршруте:

```text
Custom DocType как отдельную практику
DocType Layout
Client Script
Server Script
собственный Python controller
собственные hooks с бизнес-логикой
REST API
Query Report
Script Report
ручной Jinja Print Format
собственные Portal Pages
Virtual DocType
собственный calendar JS
```

---

# 18. Главный архитектурный тест

Любое новое учебное решение должно проходить простой вопрос:

```text
эта сущность нужна рабочей модели
или только демонстрирует функцию Frappe?
```

Если только демонстрирует функцию — ей место в Lab, а не в core.

Итоговый `facility_ops` после всего практикума по-прежнему строится вокруг трёх предметных DocType.