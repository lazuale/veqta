# Матрица покрытия Frappe

Базовая версия: **Frappe Framework v16.32.0**.

- **Core** — L0–L11;
- **Lab** — A–F;
- **Optional** — самостоятельная проверка;
- **Later** — следующий уровень.

Формальные гарантии: [INVARIANTS.md](INVARIANTS.md).

---

# Основной маршрут

| Код | Тема | Результат |
|---|---|---|
| L0 | платформа | Bench, app, site, Module, Developer Mode, Git |
| L1 | места | Facility Location |
| L2 | оборудование | Equipment |
| L3 | данные | filters, import, export, bulk edit |
| L4 | документ | Service Request + data invariants |
| L5 | доступ | Level 0 document + Level 1 content + Level 2 state authority |
| L6 | collaboration | Assign To, ToDo, Comments, Tags, Kanban |
| L7 | процесс | Workflow поверх Level 2 state field |
| L8 | контроль | Report, Cards, Chart, Workspace |
| L9 | automation | Notification, Assignment Rule, scheduler |
| L10 | web intake | separate Web Form capability; final update Off |
| L11 | поставка | clean-site portability + Level 0/1/2 acceptance |

---

# Data model

| Механизм | Где | Статус |
|---|---|---|
| Standard DocType | L1/L2/L4 | Core |
| Tree | L1 | Core |
| Link | L2/L4 | Core |
| Naming | L1/L2/L4 | Core |
| Title/Search Fields | L2/L4 | Core |
| Quick Entry | L2 | Core |
| Track Changes | L2/L4 | Core |
| Allow Import | L3 | Core |
| Child DocType / Table | Lab A | Lab |
| Single | Lab F | Lab |
| Dynamic Link | Lab F | Lab |
| Table MultiSelect | Lab F | Lab |
| Virtual DocType | — | Later |

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

---

# Permissions

| Механизм | Где | Статус |
|---|---|---|
| User / System User | L5 | Core |
| Website User / Guest | L10 | Core |
| Role | L5 | Core |
| Role Permission Manager | L5 | Core |
| Read / Write / Create | L5 | Core |
| Delete | L5 | Core, temporary for Service Request; final Off |
| Report / Export / Import | L5 | Core |
| If Owner | L5 | Core |
| Permission Level 1 | L5 | Core, business content authority |
| Permission Level 2 | L5 | Core, process-state authority |
| User Permission | L5 | Core, temporary |
| Share | L5 | Core, temporary |
| Mask | Lab F | Lab |
| custom permission hooks | — | Later |

## Level 0

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

## Level 1 content

```text
subject
location
equipment
description
priority
target_date
attachment
```

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

## Level 2 process state

```text
status
```

```text
Requester   → Read only
Technician  → Read/Write
Supervisor  → Read/Write
```

Ключевой proof:

```text
Technician document Write
≠ content Write
≠ unrestricted state transition
```

---

# Collaboration

| Механизм | Где | Статус |
|---|---|---|
| Assign To | L6 | Core |
| ToDo | L6 | Core |
| Due Date | L6/L9 | Core |
| Comments / Timeline / Tags | L6 | Core |
| Kanban | L6/L7 | Core |

Assignment не расширяет Level 1/2 permissions.

---

# Workflow

| Механизм | Где | Статус |
|---|---|---|
| обычный Status до Workflow | L4–L6 | Core |
| Status Permission Level 2 | L5+ | Core |
| Workflow / State / Action Master | L7 | Core |
| Transition | L7 | Core |
| Allowed Role | L7 | Core, server transition gate |
| Condition | L7 | Core, server predicate |
| Only Allow Edit For | L7 | Core, Desk guard |
| Read Only status | L7 | Core, UI guard |
| Is Submittable / DocStatus | Lab B | Lab |

После L7 state change требует:

```text
Level 0 Write
+ Level 2 Write
+ valid Workflow transition
```

Requester Level 2 Write отсутствует уже с L5.

---

# Analytics

| Механизм | Где | Статус |
|---|---|---|
| Report Builder | L8 | Core |
| Filters / Group By / Count | L8 | Core |
| Number Card | L8 | Core |
| Dashboard Chart | L8 | Core |
| Workspace | L8 | Core |
| Shortcut / Quick List | L8 | Core |
| Query / Script Report | — | Later |

---

# Automation

| Механизм | Где | Статус |
|---|---|---|
| Notification | L9 | Core |
| System Notification | L9 | Core |
| Days After | L9 | Core |
| Assignment Rule | L9 | Core |
| Round Robin | L9 | Core |
| Load Balancing | L9 | Optional |
| Due Date Based On | L9 | Core, conditional |
| Close Condition | L9 | Core, site policy |
| scheduler/background jobs | L9 | Core |
| Auto Repeat | Lab C | Lab |

Automation не расширяет Level 1/2 authority.

---

# Web

| Механизм | Где | Статус |
|---|---|---|
| Standard Web Form | L10 | Core |
| Published / Route | L10 | Core |
| Guest submission | L10 | Core, temporary |
| Login Required | L10 | Core, final On; authentication only |
| Website User | L10 | Core |
| Web Form new insert | L10 | Core, separate capability |
| Allow Edit | L10 | Core, temporary; final Off |
| Show List | L10 | Core, final On |
| Apply Document Permissions | L10 | Core, existing-doc experiment; final Off |
| Allow Read On All Link Options | L10 | Core, trusted-internal policy |
| role-restricted/public portal | — | Later |

```text
Desk Requester Create
→ Level 0/1/2 permission path

Web Form new insert
→ ignore_permissions=True
→ separate intake capability
```

`Status` не входит в Web Form fields.

---

# Packaging

| Механизм | Где | Статус |
|---|---|---|
| Export Customizations | L11/Lab D | Core |
| Custom Permissions Level 0 | L11 | Core |
| Custom Permissions Level 1 | L11 | Core |
| Custom Permissions Level 2 | L11 | Core |
| fixtures / fixture_auto_order | L11 | Core |
| export-fixtures | L11 | Core |
| install-app / migrate | L11 | Core |
| clean-site portability | L11 | Core |
| Desk/Web Form separate acceptance | L11 | Core |
| arbitrary multi-app compatibility | — | Later |

---

# Labs

Labs, затрагивающие `Service Request`, обязаны вернуть Level 0/1/2 baseline.

Lab A temporary `work_logs` = Permission Level 1.

Lab C Auto Repeat не меняет permission authority.

---

# Later

```text
Server Script
custom controller / validation
custom permission logic
assignee-only authorization
absolute Closed immutability
role-restricted/public-untrusted portal intake
Client Script / custom JS
Query/Script Report
production hardening
```

---

# Правило матрицы

Coverage не подменяет architecture quality.

```text
Service Request Delete → изучен → final Off
Web Form Allow Edit     → изучен → final Off
```

И `Write` на Document не означает ни write любого field, ни право на любой process transition.
