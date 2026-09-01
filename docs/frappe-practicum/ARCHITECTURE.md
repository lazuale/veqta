# Архитектура учебного приложения

## 1. Что строим

Курс использует одно приложение — `facility_ops`.

Его задача:

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

Это учебное приложение, а не попытка построить полноценную систему эксплуатации.

Поэтому ядро ограничено тремя DocType.

---

# 2. Техническая основа

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
Frappe: v16.32.0
```

Один app используется на всём курсе.

---

# 3. Предметная модель

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

`Service Request` всегда связан с `Facility Location`.

Связь с `Equipment` необязательна.

Это позволяет одинаково обрабатывать:

```text
сломалось конкретное оборудование
```

и

```text
проблема относится только к помещению или месту
```

---

# 4. Facility Location

Назначение — структура мест эксплуатации.

Тип:

```text
Tree DocType
```

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

Минимальная предметная информация:

```text
Location Name
```

На этом объекте изучаются:

- Standard DocType;
- Tree DocType;
- Naming;
- Tree View;
- Form View;
- List View;
- связь metadata с app и Git.

---

# 5. Equipment

Назначение — реестр конкретных единиц оборудования.

Минимальные поля:

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

`Category` остаётся `Select`.

Отдельный `Equipment Type` не создаётся, пока у категории нет собственной модели данных.

На Equipment изучаются:

- основные Field Types;
- Link;
- Select;
- required/default;
- Naming;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Form layout;
- List View;
- Filters / Sorting;
- Data Import / Export.

---

# 6. Service Request

Центральный рабочий документ приложения.

Минимальные поля:

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

`Location` обязателен.

`Equipment` необязателен.

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

Не создаём собственное поле исполнителя.

Ответственный хранится штатной связкой:

```text
Assign To
   ↓
ToDo
```

Не создаём собственные сущности комментариев и истории.

Используются штатные:

```text
Comments
Timeline
Track Changes / Version
```

---

# 7. Пользователи и роли

Минимально:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

## Facility Requester

Создаёт заявки и работает только с разрешёнными ему данными.

## Facility Technician

Работает с доступными и назначенными ему заявками.

## Facility Supervisor

Контролирует очередь, распределение, отчёты и настройки рабочего процесса.

`Administrator` используется только для настройки и диагностики.

Проверка обычных permissions под `Administrator` не считается.

---

# 8. Основной процесс

Сначала Status работает как обычное поле:

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

После того как ручной процесс понятен, на него накладывается Workflow.

Учебная последовательность:

```text
ручной Status
      ↓
понятна проблема свободного изменения
      ↓
Workflow
```

Workflow не вводится раньше рабочего документа.

---

# 9. Что не входит в ядро

Не создаём отдельные обязательные DocType только ради демонстрации возможностей Frappe:

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

Если специальному механизму нужен отдельный объект, он создаётся внутри лаборатории.

После лаборатории объект может быть удалён.

---

# 10. Что изучается на ядре

## Модель данных

```text
DocType
DocField
Document
name
Standard DocType
Tree
Link
Field Types
Naming
Title/Search
Forms
Lists
Data Import
```

## Работа пользователей

```text
User
Role
Permissions
User Permission
Share
Assign To
ToDo
Comments
Timeline
Tags
Kanban
Workflow
```

## Представление и контроль

```text
Report Builder
Number Card
Dashboard Chart
Workspace
```

## Автоматизация и внешний вход

```text
Notification
Assignment Rule
Web Form
```

## Поставка приложения

```text
Git
Standard metadata
fixtures
Export Customizations
install-app
migrate
clean site
```

---

# 11. Лаборатории

## Lab A — Child Table

Временная таблица выполненных работ внутри Service Request:

```text
Work Log
├── Description
├── Hours
└── Cost
```

Изучаются Child DocType и Table.

## Lab B — DocStatus

Отдельный маленький `Service Report`:

```text
Draft
Submit
Cancel
Amend
```

Изучаются:

- Is Submittable;
- DocStatus;
- Allow on Submit;
- Audit Trail.

## Lab C — Auto Repeat

Создать повторяющуюся профилактическую заявку и изучить Auto Repeat.

## Lab D — Customize Form

Добавить локальное поле в Equipment и изучить:

- Customize Form;
- Custom Field;
- Property Setter;
- Export Customizations.

## Lab E — Print / PDF

Печатная форма Service Request.

## Lab F — специальные возможности

Короткие упражнения:

- Single DocType;
- Dynamic Link;
- Table MultiSelect;
- Duration;
- Percent;
- Barcode;
- Signature;
- Geolocation;
- Attachment Gallery;
- Gantt.

Ни одна из этих тем не должна раздувать основную предметную модель.

---

# 12. Как устроено обучение

```text
L0  платформа и app
 ↓
L1  места
 ↓
L2  оборудование
 ↓
L3  данные
 ↓
L4  заявка
 ↓
L5  права
 ↓
L6  совместная работа
 ↓
L7  Workflow
 ↓
L8  аналитика и Workspace
 ↓
L9  автоматизация
 ↓
L10 Web Form
 ↓
L11 переносимость
```

Лаборатории подключаются после того, как базовый объект, на котором они выполняются, уже знаком.

---

# 13. Архитектурные правила курса

1. Ядро — три DocType.
2. Один app развивается весь курс.
3. Новая сущность появляется только по необходимости предметной модели.
4. Механизм Frappe не должен диктовать новую бизнес-сущность.
5. Права и Assignment — разные вещи.
6. Workflow появляется после ручного процесса.
7. Автоматизация появляется после ручного действия.
8. Рабочие данные не экспортируются как конфигурация приложения.
9. Редкая возможность изучается лабораторией, а не усложнением ядра.
10. Если v16.32.0 работает иначе, исправляется курс.
