# Матрица покрытия Frappe

Матрица фиксирует **реально выполненную практику**. Она не является каталогом всех функций Frappe и не заставляет добавлять упражнения ради галочки.

Обозначения:

- **Core** — основной маршрут L0–L11;
- **Lab** — отдельная лаборатория A–F;
- **Optional** — самостоятельная проверка внутри урока;
- **Later** — следующий уровень курса.

Базовая версия — **Frappe Framework v16.32.0**.

---

# Основной маршрут

| Код | Тема | Результат |
|---|---|---|
| L0 | платформа | Bench, app, site, Module, Developer Mode, Git |
| L1 | места | Facility Location |
| L2 | оборудование | Equipment |
| L3 | данные | filters, import, export, bulk edit |
| L4 | рабочий документ | Service Request |
| L5 | доступ | Users, Roles, Permissions |
| L6 | совместная работа | Assign To, ToDo, Comments, Tags, Kanban |
| L7 | процесс | Workflow |
| L8 | контроль | Report, Cards, Chart, Workspace |
| L9 | автоматизация | Notification, Assignment Rule, scheduler |
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
| `bench new-site` | L0/L11 | Core |
| `install-app` / `list-apps` | L0/L11 | Core |
| Developer Mode | L0 | Core |
| Module | L0 | Core |
| структура app | L0 | Core |
| `modules.txt` | L0 | Core |
| `hooks.py` | L0/L11 | Core |
| Git status / diff / commit | L0–L11, Labs | Core |
| Desk | L0 | Core |
| Awesomebar | L0+ | Core |
| scheduler / workers | L0/L9 | Core |
| `bench migrate` | L11 | Core |
| второй clean site | L11 | Core |

---

# Модель данных

| Механизм | Где | Статус |
|---|---|---|
| DocType / DocField / Document | L0–L2 | Core |
| `name` | L0–L4 | Core |
| Standard DocType своего app | L0–L4 | Core |
| Tree DocType | L1 | Core |
| Link | L2/L4 | Core |
| Naming by fieldname | L1/L2 | Core |
| naming expression / series | L4 | Core |
| Title Field | L2/L4 | Core |
| Search Fields | L2/L4 | Core |
| Quick Entry | L2 | Core |
| Track Changes | L2/L4 | Core |
| Allow Import | L3 | Core |
| Child DocType / Table | Lab A | Lab |
| Single DocType | Lab F | Lab |
| Dynamic Link | Lab F | Lab |
| Table MultiSelect | Lab F | Lab |
| Custom DocType | — | Later |
| DocType Layout | — | Later |
| Virtual DocType | — | Later |

`Custom DocType` не следует путать с `Custom Field`: Lab D кастомизирует Standard `Equipment`, но не создаёт Custom DocType.

---

# Field Types

| Механизм | Где | Статус |
|---|---|---|
| Data | L2/L4 | Core |
| Small Text / Text | L2/L4 | Core |
| Select | L2/L4 | Core |
| Date | L2/L4 | Core |
| Link | L2/L4 | Core |
| Attach | L4 | Core |
| Attach Image | L2 | Core |
| Section Break | L2 | Core |
| Column Break | L2 | Core |
| Float | Lab A | Lab |
| Currency | Lab A | Lab |
| Check | Lab F | Lab |
| Percent | Lab F | Lab |
| Time | Lab F | Lab |
| Duration | Lab F | Lab |
| Barcode | Lab F | Lab |
| Signature | Lab F | Lab |
| Geolocation | Lab F | Lab |
| Attachment Gallery | Lab F | Lab |
| Markdown Editor | Lab F | Lab |
| собственный HTML field / custom UI | — | Later |

---

# Работа с данными и Desk

| Механизм | Где | Статус |
|---|---|---|
| Form View | L1–L4 | Core |
| List View | L1–L4 | Core |
| Tree View | L1 | Core |
| Filters | L3/L4/L8 | Core |
| Sorting текущего List View | L3 | Core |
| Saved Filters | L3 | Core |
| Search | L2/L3 | Core |
| Data Import | L3 | Core |
| штатный Data Import template | L3 | Core |
| Export | L3 | Core |
| Bulk Edit | L3 | Core |
| Attachments | L2/L4/L10 | Core |
| Comments | L6 | Core |
| Timeline | L2/L6/L7 | Core |
| Tags | L6 | Core |
| Kanban | L6 | Core |
| Calendar | Lab F, штатный Event | Lab |
| Gantt | Lab F, штатный Event | Lab |
| собственная Calendar/Gantt config | — | Later |
| изменение DocType default sort metadata | — | Later |

В `v16.32.0` собственные Calendar/Gantt для нового DocType требуют `frappe.views.calendar[...]`; собственный JavaScript не входит в базовый курс.

---

# Пользователи и права

| Механизм | Где | Статус |
|---|---|---|
| User | L5 | Core |
| System User | L5 | Core |
| Website User | L10 | Core |
| Guest | L10 | Core |
| Role | L5 | Core |
| Role Permission Manager | L5 | Core |
| Read | L5 | Core |
| Write | L5 | Core |
| Create | L5 | Core |
| Delete | L5 | Core |
| Report | L5 | Core |
| Export | L5 | Core |
| Import | L5 | Core |
| If Owner / Only If Creator | L5 | Core |
| Permission Level | L5 | Core |
| User Permission | L5 | Core |
| Share | L5 | Core |
| Print permission | Lab E | Lab |
| Mask / Data Masking | Lab F | Lab |
| Email permission | — | Later |
| Custom Permission Types | — | Later |

Права всегда проверяются под обычными пользователями. `Administrator` используется для настройки, а не как доказательство permissions.

---

# Совместная работа

| Механизм | Где | Статус |
|---|---|---|
| Assign To | L6 | Core |
| ToDo | L6 | Core |
| Due Date | L6/L9 | Core |
| Comments | L6 | Core |
| Timeline | L6 | Core |
| Tags | L6 | Core |
| Kanban | L6 | Core |
| duplicate active assignment | L6 | Core |

Главное различие курса:

```text
Permissions = доступ
Assignment  = конкретная работа
Status      = состояние документа
```

---

# Состояние и Workflow

| Механизм | Где | Статус |
|---|---|---|
| обычный Status | L4 | Core |
| Workflow | L7 | Core |
| Workflow State | L7 | Core |
| Workflow Action Master | L7 | Core |
| Workflow Transition | L7 | Core |
| Allowed Role | L7 | Core |
| Only Allow Edit For | L7 | Core |
| Workflow Action | L7 | Core |
| transition Condition | L7 | Core, минимум |
| существующее поле как Workflow State Field | L7 | Core |
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
| Report filters | L8 | Core |
| Group By | L8 | Core |
| Count | L8 | Core |
| Number Card | L8 | Core |
| Number Card filters | L8 | Core |
| Dashboard Chart | L8 | Core |
| Group By Chart | L8 | Core |
| Workspace | L8 | Core |
| Shortcut | L8 | Core |
| Quick List | L8 | Core |
| Workspace roles/access | L8 | Core |
| Chart roles/access | L8 | Core |
| Sum / Average aggregation | — | Later |
| Query Report | — | Later |
| Script Report | — | Later |

L8 намеренно создаёт один понятный рабочий экран, а не набор отчётов ради количества.

---

# Автоматизация

| Механизм | Где | Статус |
|---|---|---|
| Notification | L9 | Core |
| Standard Notification | L9 | Core |
| System Notification | L9 | Core |
| Notification Filters | L9 | Core |
| date-based Notification | L9 | Core |
| Preview / Alerts for Today | L9 | Core |
| Assignment Rule | L9 | Core |
| Round Robin | L9 | Core |
| Load Balancing | L9, самостоятельная практика | Optional |
| Due Date Based On | L9 | Core |
| Close Condition | L9 | Core |
| штатное expression-поле | L9 | Core, минимум |
| scheduler/background jobs | L9 | Core |
| ручной запуск штатного scheduler job | L9 | Core |
| Allow Auto Repeat | Lab C | Lab |
| Auto Repeat | Lab C | Lab |
| Auto Repeat Assignee | Lab C | Lab |
| Weighted Distribution | — | Later |
| Based on Field assignment | — | Later |

Assignment Rule L9 остаётся site-specific: он содержит конкретных Users и не входит в универсальные fixtures L11.

---

# Web

| Механизм | Где | Статус |
|---|---|---|
| Web Form | L10 | Core |
| Standard Web Form | L10 | Core |
| Route | L10 | Core |
| Published | L10 | Core |
| Anonymous responses | L10 | Core |
| Guest submission | L10 | Core |
| Login Required | L10 | Core |
| Website User | L10 | Core |
| Allow Edit | L10 | Core |
| Show List | L10 | Core |
| Apply Document Permissions | L10 | Core |
| Allow Read On All Link Options | L10 | Core |
| Web Form attachment | L10 | Core |
| собственный Web Form JS/Python | — | Later |
| Web Form Request/key internals | — | Later |
| Portal / Website Pages | — | Later |

---

# Кастомизация и поставка

| Механизм | Где | Статус |
|---|---|---|
| Customize Form | Lab D | Lab |
| Custom Field | Lab D | Lab |
| Property Setter | Lab D | Lab |
| Module for Export | Lab D | Lab |
| Export Customizations | Lab D/L11 | Core для поставки |
| Sync on Migrate | Lab D/L11 | Core для поставки |
| Custom Permissions export | L11 | Core |
| fixtures | L11 | Core |
| `fixture_auto_order` | L11 | Core |
| `bench export-fixtures` | L11 | Core |
| Standard metadata / app config / site config / working data | L11 | Core |
| clean site | L11 | Core |
| повторный `migrate` | L11 | Core |
| DocType Layout | — | Later |

---

# Печать

| Механизм | Где | Статус |
|---|---|---|
| Print View | Lab E | Lab |
| Print Format | Lab E | Lab |
| Print Format Builder | Lab E | Lab |
| Standard Print Format | Lab E | Lab |
| Letter Head | Lab E | Lab |
| Print Settings | Lab E | Lab |
| browser Print | Lab E | Lab |
| PDF | Lab E | Lab |
| Chrome PDF generator | Lab E | Lab |
| Set as Default / default_print_format | Lab E, только граница | Lab |
| ручной Jinja Print Format | — | Later |
| Custom HTML/CSS print logic | — | Later |

---

# Специальные механизмы Lab F

| Механизм | Где | Статус |
|---|---|---|
| Single DocType | Lab F | Lab |
| Dynamic Link | Lab F | Lab |
| Table MultiSelect | Lab F | Lab |
| Barcode | Lab F | Lab |
| Signature | Lab F | Lab |
| Geolocation / GeoJSON | Lab F | Lab |
| Attachment Gallery / File | Lab F | Lab |
| Markdown Editor | Lab F | Lab |
| Data Masking | Lab F | Lab |
| Calendar | Lab F / Event | Lab |
| Gantt | Lab F / Event | Lab |

---

# За пределами базовой программы

| Механизм | Статус |
|---|---|
| Custom DocType | Later |
| DocType Layout | Later |
| собственный Python controller с бизнес-логикой | Later |
| собственные server-side hooks с бизнес-логикой | Later |
| JavaScript / Client Script | Later |
| Server Script | Later |
| whitelisted methods | Later |
| REST API / Webhooks | Later |
| Query Report / Script Report | Later |
| Sum / Average как отдельная аналитическая практика | Later |
| ручные Jinja templates | Later |
| собственные Portal/Website Pages | Later |
| собственная Calendar/Gantt JS configuration | Later |
| Virtual DocType | Later |
| сторонние библиотеки / apps | Later |
| Custom Permission Types с собственным кодом | Later |

---

# Правило матрицы

Если механизм не пройден руками в указанном уроке, он не получает статус Core или Lab.

Если возможность Frappe не нужна трём основным DocType и одному рабочему процессу, она не создаёт новую обязательную сущность.

Сначала исправляется матрица, а не архитектура приложения подгоняется под старый список функций.