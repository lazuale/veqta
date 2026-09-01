# Матрица покрытия Frappe

Матрица контролирует полноту курса. Она не диктует архитектуру приложения.

Обозначения:

- **Core** — основной маршрут L0–L11;
- **Lab** — отдельная лаборатория;
- **Later** — следующий уровень курса.

## Основной маршрут

| Код | Тема | Результат |
|---|---|---|
| L0 | платформа | Bench, app, site, Module, Developer Mode, Git |
| L1 | места | Facility Location |
| L2 | оборудование | Equipment |
| L3 | данные | импорт, фильтры, экспорт |
| L4 | рабочий документ | Service Request |
| L5 | доступ | Users, Roles, Permissions |
| L6 | совместная работа | Assign To, ToDo, Comments, Kanban |
| L7 | процесс | Workflow |
| L8 | контроль | Reports, Cards, Charts, Workspace |
| L9 | автоматизация | Notification, Assignment Rule |
| L10 | внешний ввод | Web Form |
| L11 | поставка | fixtures, customizations, clean site |

---

# Среда и приложение

| Механизм | Где | Статус |
|---|---|---|
| Bench | L0 | Core |
| App | L0 | Core |
| Site | L0 | Core |
| `bench new-app` | L0 | Core |
| `install-app` / `list-apps` | L0/L11 | Core |
| Developer Mode | L0 | Core |
| Module | L0 | Core |
| структура app | L0 | Core |
| `hooks.py` | L0/L11 | Core |
| Git diff / commit | L0–L11 | Core |
| Desk v16 | L0 | Core |
| Apps Page / Workspace Sidebar | L0 | Core |
| Awesomebar / command palette | L0 | Core |
| scheduler / workers | L0/L9 | Core |
| `bench migrate` | L11 | Core |
| второй clean site | L11 | Core |

---

# Модель данных

| Механизм | Где | Статус |
|---|---|---|
| DocType / DocField / Document / `name` | L0–L2 | Core |
| Standard DocType своего app | L0–L4 | Core |
| Tree DocType | L1 | Core |
| Link | L2/L4 | Core |
| Naming | L1/L2/L4 | Core |
| By fieldname / подходящий штатный Naming | L1/L2 | Core |
| Title Field | L2 | Core |
| Search Fields | L2 | Core |
| Quick Entry | L2 | Core |
| Track Changes | L2/L4 | Core |
| Allow Import | L3 | Core |
| Default Sort | L3 | Core |
| Child DocType / Table | Lab A | Lab |
| Single DocType | Lab F | Lab |
| Dynamic Link | Lab F | Lab |
| Custom DocType | Lab D | Lab |
| Table MultiSelect | Lab F | Lab |
| DocType Layout | Lab D | Lab |

---

# Field Types

| Механизм | Где | Статус |
|---|---|---|
| Data | L2/L4 | Core |
| Small Text / Text | L2/L4 | Core |
| Select | L2/L4 | Core |
| Check | L2 или короткое упражнение | Core |
| Date | L2/L4 | Core |
| Link | L2/L4 | Core |
| Attach | L4 | Core |
| Attach Image | L2 | Core |
| Section / Column / Tab Break | L2 | Core |
| Float / Currency | Lab A | Lab |
| Percent | Lab F | Lab |
| Time / Duration | Lab F | Lab |
| Barcode | Lab F | Lab |
| Signature | Lab F | Lab |
| Geolocation | Lab F | Lab |
| Attachment Gallery | Lab F | Lab |
| Markdown/Text Editor | Lab F | Lab |

---

# Работа с данными и Desk

| Механизм | Где | Статус |
|---|---|---|
| Form View | L1–L4 | Core |
| List View | L1–L4 | Core |
| Tree View | L1 | Core |
| Filters | L3/L4 | Core |
| Sorting | L3 | Core |
| Saved Filters | L3 | Core |
| Search | L2/L3 | Core |
| Data Import | L3 | Core |
| Export | L3 | Core |
| Mass actions | L3 | Core |
| Attachments | L2/L4 | Core |
| Comments | L6 | Core |
| Timeline | L2/L6 | Core |
| Tags | L6 | Core |
| Kanban | L6 | Core |
| Calendar | Lab F | Lab |
| Gantt | Lab F | Lab |

---

# Пользователи и права

| Механизм | Где | Статус |
|---|---|---|
| User | L5 | Core |
| System User | L5 | Core |
| Website User | L10 | Core |
| Guest | L10 | Core |
| Administrator / Desk User / All | L5 | Core |
| Role | L5 | Core |
| Role Permission Manager | L5 | Core |
| Read / Write / Create / Delete | L5 | Core |
| If Owner | L5 | Core |
| Permission Level | L5 | Core |
| User Permission | L5 | Core |
| Share | L5 | Core |
| Report / Export / Import permissions | L5 | Core |
| Print / Email permission | L5 / Lab E | Core/Lab |
| Mask / Data Masking | Lab F | Lab |

---

# Совместная работа

| Механизм | Где | Статус |
|---|---|---|
| Assign To | L6 | Core |
| ToDo | L6 | Core |
| Due Date | L6 | Core |
| Comments | L6 | Core |
| Timeline | L6 | Core |
| Tags | L6 | Core |
| Kanban | L6 | Core |

Главное различие курса:

```text
Permissions = доступ
Assignment  = конкретная работа
```

---

# Состояние и Workflow

| Механизм | Где | Статус |
|---|---|---|
| обычный Status | L4 | Core |
| Workflow | L7 | Core |
| Workflow State | L7 | Core |
| Workflow Transition | L7 | Core |
| Allowed Role | L7 | Core |
| Workflow Action | L7 | Core |
| transition condition | L7 | Core, минимум |
| Is Submittable | Lab B | Lab |
| Draft / Submit / Cancel / Amend | Lab B | Lab |
| DocStatus | Lab B | Lab |
| Allow on Submit | Lab B | Lab |
| Audit Trail | Lab B | Lab |

Workflow и DocStatus намеренно изучаются отдельно.

---

# Аналитика и Workspace

| Механизм | Где | Статус |
|---|---|---|
| Report Builder | L8 | Core |
| Filters | L8 | Core |
| Group By | L8 | Core |
| Count | L8 | Core |
| Sum / Average | L8 или Lab A data | Core |
| Number Card | L8 | Core |
| Dashboard Chart | L8 | Core |
| Workspace | L8 | Core |
| Shortcut | L8 | Core |
| Quick List | L8 | Core |
| Workspace roles/access | L8 | Core |
| Calendar | Lab F | Lab |

---

# Автоматизация

| Механизм | Где | Статус |
|---|---|---|
| Notification | L9 | Core |
| System Notification | L9 | Core |
| Notification Filters | L9 | Core |
| date-based Notification | L9 | Core |
| Assignment Rule | L9 | Core |
| Round Robin или Load Balancing | L9 | Core |
| остальные Assignment Rule modes | L9 | Lab/обзор |
| PythonExpression штатного механизма | L9 | Core, минимум |
| scheduler/background jobs | L9 | Core |
| Allow Auto Repeat | Lab C | Lab |
| Auto Repeat | Lab C | Lab |
| Auto Repeat Assignee | Lab C | Lab |

---

# Web

| Механизм | Где | Статус |
|---|---|---|
| Web Form | L10 | Core |
| Route | L10 | Core |
| Anonymous responses | L10 | Core |
| Login Required | L10 | Core |
| Guest | L10 | Core |
| Website User | L10 | Core |
| Apply document permissions | L10 | Core |
| attachments | L10 | Core |
| Show List | L10 | Core |
| editing existing document | L10 | Core, если подходит сценарию |
| Standard Web Form | L10 | Core |
| Web Form Request / key | L10 | Lab/обзор |

---

# Кастомизация и поставка

| Механизм | Где | Статус |
|---|---|---|
| Customize Form | Lab D | Lab |
| Custom Field | Lab D | Lab |
| Property Setter | Lab D | Lab |
| DocType Layout | Lab D | Lab |
| Export Customizations | Lab D/L11 | Core для понимания поставки |
| fixtures | L11 | Core |
| `bench export-fixtures` | L11 | Core |
| Standard / Customized / configuration record / working data | L11 | Core |
| clean site | L11 | Core |

---

# Печать

| Механизм | Где | Статус |
|---|---|---|
| Print View | Lab E | Lab |
| Print Format Builder | Lab E | Lab |
| Letter Head | Lab E | Lab |
| PDF | Lab E | Lab |

---

# За пределами базовой программы

| Механизм | Статус |
|---|---|
| собственный Python controller | Later |
| собственная бизнес-логика hooks | Later |
| JavaScript / Client Script | Later |
| Server Script | Later |
| whitelisted methods | Later |
| REST API / Webhooks | Later |
| Query Report / Script Report | Later |
| ручные Jinja templates | Later |
| собственные Portal/Website Pages | Later |
| Virtual DocType | Later |
| сторонние библиотеки / apps | Later |
| Custom Permission Types с собственным кодом | Later |

---

# Правило матрицы

Если возможность Frappe не нужна трём основным DocType и одному рабочему процессу, она не создаёт новую обязательную сущность.

Она либо:

1. изучается в лаборатории;
2. остаётся на следующем уровне курса.
