# Матрица покрытия Frappe

Матрица фиксирует **реально выполняемую практику**, а не каталог всех возможностей Frappe.

Базовая версия: **Frappe Framework v16.32.0**.

Обозначения:

- **Core** — L0–L11;
- **Lab** — Labs A–F;
- **Optional** — самостоятельная проверка;
- **Later** — следующий уровень.

Формальная сила механизмов: [INVARIANTS.md](INVARIANTS.md).

---

# Основной маршрут

| Код | Тема | Результат |
|---|---|---|
| L0 | платформа | Bench, app, site, Module, Developer Mode, Git |
| L1 | места | Facility Location |
| L2 | оборудование | Equipment |
| L3 | данные | filters, import, export, bulk edit |
| L4 | рабочий документ | Service Request + data semantics |
| L5 | доступ | hardened Role Permission model + temporary access experiments |
| L6 | совместная работа | Assign To, ToDo, Comments, Tags, Kanban |
| L7 | процесс | Workflow + enforcement boundaries |
| L8 | контроль | Report, Cards, Chart, Workspace |
| L9 | automation | Notification, Assignment Rule, scheduler |
| L10 | внешний intake | Web Form; final create/read-only mode |
| L11 | поставка | fixtures, customizations, clean-site portability |

---

# Платформа

| Механизм | Где | Статус |
|---|---|---|
| Bench / App / Site | L0 | Core |
| `bench new-app` / `new-site` | L0/L11 | Core |
| `install-app` / `list-apps` | L0/L11 | Core |
| Developer Mode | L0 | Core |
| Module / app source | L0+ | Core |
| `hooks.py` | L0/L11 | Core |
| Git status/diff/commit | весь курс | Core |
| Desk / Awesomebar | L0+ | Core |
| scheduler / workers | L9/Lab C | Core |
| `bench migrate` | L11 | Core |
| clean site | L11 | Core |

---

# Модель данных

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

Core Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

`Accepted` не является assignment state.

---

# Field Types

| Механизм | Где | Статус |
|---|---|---|
| Data / Text / Small Text | L2/L4 | Core |
| Select | L2/L4 | Core |
| Date | L2/L4 | Core |
| Link | L2/L4 | Core |
| Attach / Attach Image | L2/L4 | Core |
| Section / Column Break | L2/L4 | Core |
| Float / Currency | Lab A | Lab |
| Check / Percent / Time / Duration | Lab F | Lab |
| Barcode / Signature / Geolocation | Lab F | Lab |
| Attachment Gallery / Markdown Editor | Lab F | Lab |

---

# Работа с данными и views

| Механизм | Где | Статус |
|---|---|---|
| Form / List | L1+ | Core |
| Tree View | L1 | Core |
| Filters / Sorting / Saved Filters | L3 | Core |
| Data Import / template / negative test | L3 | Core |
| Export / Bulk Edit | L3 | Core |
| Attachments | L2/L4/L10 | Core |
| Timeline | L6/L7 | Core |
| Tags | L6 | Core |
| Kanban | L6/L7 | Core |
| Calendar / Gantt | Lab F на Event | Lab |
| own Calendar JS mapping | — | Later |

Kanban после L7 удаляется из финальной process configuration.

---

# Permissions

| Механизм | Где | Статус |
|---|---|---|
| User / System User | L5 | Core |
| Website User / Guest | L10 | Core |
| Role | L5 | Core |
| Role Permission Manager | L5 | Core |
| Read / Write / Create | L5 | Core |
| Delete permission | L5 | Core, temporary experiment for Service Request; final Off |
| Report / Export / Import | L5 | Core |
| If Owner | L5 | Core |
| Permission Level | L5 | Core |
| User Permission | L5 | Core, temporary experiment |
| Share | L5 | Core, temporary experiment |
| Mask | Lab F | Lab |
| Custom Permission Types | — | Later |
| custom permission hooks | — | Later |

Final `Service Request` permission outcome:

```text
Requester
→ Create + Read own
→ Write/Delete No

Technician
→ Read/Write
→ Create/Delete No

Supervisor
→ Read/Write/Create
→ Delete No
→ Report/Export
```

Это важно: матрица покрытия фиксирует и изученный механизм, и финальную безопасную конфигурацию.

```text
Role Permission = server access boundary
Assignment      = не permission mechanism
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
Assignment = ответственность
не authorization
```

Assignee-only security — Later.

---

# Workflow

| Механизм | Где | Статус |
|---|---|---|
| обычный Status до Workflow | L4–L6 | Core |
| Workflow / State / Action Master | L7 | Core |
| Transition | L7 | Core |
| Allowed Role | L7 | Core, server transition gate |
| Condition | L7 | Core, server transition predicate |
| Only Allow Edit For | L7 | Core, Desk/UI state guard |
| existing `status` as state field | L7 | Core |
| Read Only status | L7 | Core, UI guard |
| Is Submittable / DocStatus | Lab B | Lab |

Final Desk roles:

```text
New         → Supervisor
Accepted    → Technician
In Progress → Technician
Resolved    → Supervisor
Closed      → Supervisor
```

Requester create остаётся возможным для local new document, а post-create Write блокируется Role Permission.

Closed изучается как terminal Workflow state, не как абсолютная record immutability.

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
| Sum/Average отдельной практикой | — | Later |

---

# Automation

| Механизм | Где | Статус |
|---|---|---|
| Notification | L9 | Core |
| System Notification | L9 | Core |
| filters | L9 | Core |
| Days After | L9 | Core |
| Preview / Alerts for Today | L9 | Core |
| Assignment Rule | L9 | Core |
| Round Robin | L9 | Core |
| Load Balancing | L9 | Optional |
| Due Date Based On | L9 | Core, conditional on Target Date |
| Close Condition | L9 | Core, site policy |
| scheduler/background jobs | L9 | Core |
| manual scheduler handler | L9 | Core |
| Auto Repeat | Lab C | Lab |
| Weighted/Based on Field assignment | — | Later |

Assignment Rule остаётся site-specific.

---

# Web

| Механизм | Где | Статус |
|---|---|---|
| Standard Web Form | L10 | Core |
| Route / Published | L10 | Core |
| Guest submission | L10 | Core, temporary experiment |
| Login Required | L10 | Core, final On |
| Website User | L10 | Core |
| Allow Edit | L10 | Core, temporary experiment; final Off |
| Show List | L10 | Core, final On |
| Apply Document Permissions | L10 | Core, experiment; final Off |
| Allow Read On All Link Options | L10 | Core, trusted-internal policy |
| attachment | L10 | Core |
| own Web Form JS/Python | — | Later |
| public untrusted external catalog | — | Later |

Final Web Form не является parallel editor Workflow Document.

---

# Customization / packaging

| Механизм | Где | Статус |
|---|---|---|
| Customize Form | Lab D | Lab |
| Custom Field / Property Setter | Lab D | Lab |
| Export Customizations | Lab D/L11 | Core для packaging |
| Sync on Migrate | Lab D/L11 | Core |
| Custom Permissions export | L11 | Core |
| fixtures / fixture_auto_order | L11 | Core |
| export-fixtures | L11 | Core |
| Standard vs universal vs site-specific vs data | L11 | Core |
| clean-site portability | L11 | Core |
| arbitrary multi-app compatibility | — | Later |

Clean-site acceptance включает проверку exact final permission matrix.

---

# Print

| Механизм | Где | Статус |
|---|---|---|
| Print View / Print Format Builder | Lab E | Lab |
| Standard Print Format | Lab E | Lab, persistent presentation config |
| Letter Head | Lab E | Lab, temporary site config |
| browser Print / Chrome PDF | Lab E | Lab |
| Jinja/custom HTML print | — | Later |

---

# За пределами Core

| Механизм | Статус |
|---|---|
| Server Script | Later |
| custom Python controller/hooks business logic | Later |
| permission query/custom has_permission | Later |
| state-dependent hard immutability validation | Later |
| assignee-only authorization | Later |
| Client Script / own JS | Later |
| REST/Webhooks отдельным блоком | Later |
| Query/Script Report | Later |
| custom Portal/Website Pages | Later |
| custom Calendar/Gantt JS | Later |
| production hardening | Later |

---

# Правило матрицы

Механизм может быть `Core`, даже если финальная конфигурация его выключает, если ученик реально проверяет его и понимает rollback.

Примеры:

```text
Service Request Delete
→ изучен L5
→ final Off

Web Form Allow Edit
→ изучен L10
→ final Off
```

Coverage не должно подменять architecture quality.
