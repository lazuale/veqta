# Матрица покрытия Frappe

Матрица фиксирует реально выполняемую практику на **Frappe Framework v16.32.0**.

Статусы:

- **Core** — L0–L11;
- **Lab** — A–F;
- **Optional** — самостоятельная проверка;
- **Later** — следующий уровень.

Формальная сила: [INVARIANTS.md](INVARIANTS.md).

---

# Основной маршрут

| Код | Тема | Результат |
|---|---|---|
| L0 | платформа | Bench, app, site, Module, Developer Mode, Git |
| L1 | места | Facility Location |
| L2 | оборудование | Equipment |
| L3 | данные | filters, import, export, bulk edit |
| L4 | документ | Service Request + data invariants |
| L5 | доступ | hardened Role Permission model |
| L6 | collaboration | Assign To, ToDo, Comments, Tags, Kanban |
| L7 | процесс | Workflow + enforcement boundaries |
| L8 | контроль | Report, Cards, Chart, Workspace |
| L9 | automation | Notification, Assignment Rule, scheduler |
| L10 | web intake | Web Form create/read-only final mode |
| L11 | поставка | clean-site portability + dual create proof |

---

# Data model

| Механизм | Где | Статус |
|---|---|---|
| Standard DocType | L1/L2/L4 | Core |
| Tree | L1 | Core |
| Link | L2/L4 | Core |
| Naming by field | L1/L2 | Core |
| naming series/expression | L4 | Core |
| Title/Search Fields | L2/L4 | Core |
| Quick Entry | L2 | Core |
| Track Changes | L2/L4 | Core |
| Allow Import | L3 | Core |
| Child DocType / Table | Lab A | Lab |
| Single | Lab F | Lab |
| Dynamic Link | Lab F | Lab |
| Table MultiSelect | Lab F | Lab |
| Custom DocType | — | Later |
| Virtual DocType | — | Later |

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

`Accepted ≠ Assigned To`.

---

# Views / data operations

| Механизм | Где | Статус |
|---|---|---|
| Form / List / Tree | L1+ | Core |
| Filters / Sorting / Saved Filters | L3 | Core |
| Data Import / template / negative test | L3 | Core |
| Export / Bulk Edit | L3 | Core |
| Attachments | L2/L4/L10 | Core |
| Timeline | L6/L7 | Core |
| Tags | L6 | Core |
| Kanban | L6/L7 | Core |
| Calendar / Gantt | Lab F | Lab |
| own Calendar JS mapping | — | Later |

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
| Permission Level | L5 | Core |
| User Permission | L5 | Core, temporary |
| Share | L5 | Core, temporary |
| Mask | Lab F | Lab |
| custom permission hooks | — | Later |

Final Desk outcome:

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

---

# Collaboration

| Механизм | Где | Статус |
|---|---|---|
| Assign To | L6 | Core |
| ToDo | L6 | Core |
| Due Date | L6/L9 | Core |
| duplicate assignment behavior | L6 | Core |
| Comments / Timeline / Tags | L6 | Core |

```text
Assignment = responsibility, not authorization
```

---

# Workflow

| Механизм | Где | Статус |
|---|---|---|
| обычный Status | L4–L6 | Core |
| Workflow / State / Action Master | L7 | Core |
| Transition | L7 | Core |
| Allowed Role | L7 | Core, server gate |
| Condition | L7 | Core, server predicate |
| Only Allow Edit For | L7 | Core, Desk guard |
| existing `status` as state field | L7 | Core |
| Read Only status | L7 | Core, UI guard |
| Is Submittable / DocStatus | Lab B | Lab |

Final Desk states:

```text
New         → Supervisor
Accepted    → Technician
In Progress → Technician
Resolved    → Supervisor
Closed      → Supervisor
```

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
| role access | L8 | Core |
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

---

# Web

| Механизм | Где | Статус |
|---|---|---|
| Standard Web Form | L10 | Core |
| Route / Published | L10 | Core |
| Guest submission | L10 | Core, temporary |
| Login Required | L10 | Core, final On; authentication only |
| Website User | L10 | Core |
| Web Form new insert | L10 | Core, separate intake capability |
| Allow Edit | L10 | Core, temporary; final Off |
| Show List | L10 | Core, final On |
| Apply Document Permissions | L10 | Core, existing-doc experiment; final Off |
| Allow Read On All Link Options | L10 | Core, trusted-internal policy |
| attachment | L10 | Core |
| role-restricted portal admission | — | Later |
| public-untrusted catalog | — | Later |

Ключевая классификация:

```text
Desk Requester Create
→ Role Permission mechanism

Web Form new insert
→ Web Form capability
→ insert(ignore_permissions=True)

Apply Document Permissions
→ existing-document permission behavior
→ не create authorization
```

---

# Packaging

| Механизм | Где | Статус |
|---|---|---|
| Export Customizations | L11/Lab D | Core |
| Custom Permissions export | L11 | Core |
| fixtures / fixture_auto_order | L11 | Core |
| export-fixtures | L11 | Core |
| install-app / migrate | L11 | Core |
| clean-site portability | L11 | Core |
| dual Desk/Web Form create acceptance | L11 | Core |
| arbitrary multi-app compatibility | — | Later |

---

# Print / special labs

| Механизм | Где | Статус |
|---|---|---|
| Print View / Builder | Lab E | Lab |
| Standard Print Format | Lab E | Lab, persistent presentation config |
| Letter Head | Lab E | Lab, temporary |
| browser Print / Chrome PDF | Lab E | Lab |
| Percent / Time / Duration | Lab F | Lab |
| Barcode / Signature / Geolocation | Lab F | Lab |
| Attachment Gallery / Markdown | Lab F | Lab |

---

# Later

```text
Server Script
custom controller / validation
custom permission logic
assignee-only authorization
absolute Closed immutability
role-restricted Web Form/portal admission
public-untrusted external intake
Client Script / custom JS
Query/Script Report
production hardening
```

---

# Правило матрицы

Механизм может быть Core и при этом финально выключаться, если он реально изучен и rollback является частью lesson contract.

```text
Service Request Delete → studied → final Off
Web Form Allow Edit     → studied → final Off
```

Coverage не подменяет architecture quality.
