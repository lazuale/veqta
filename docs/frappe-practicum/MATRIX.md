# Матрица покрытия Frappe

Базовая версия: **Frappe Framework v16.32.0**.

Обозначения:

- **Core** — L0–L11, один развивающийся `facility_ops`;
- **Lab** — отдельный практический эксперимент без обязательного изменения постоянной предметной модели;
- **Optional** — дополнительная проверка внутри Core/Lab;
- **Later** — следующий уровень, обычно с собственным программным слоем или другой проверенной базовой версией.

Матрица показывает **coverage**, но не задаёт архитектуру автоматически. Для каждого применения механизм всё равно выбирается по смыслу требования.

---

# Основной маршрут

| Код | Тема | Результат |
|---|---|---|
| L0 | платформа | Bench, App, Site, Module, Developer Mode, Git |
| L1 | места | `Facility Location` как Tree DocType |
| L2 | оборудование | `Equipment`, поля, Link, Form/List, Track Changes |
| L3 | данные | filters, import, export, bulk edit |
| L4 | заявка | `Service Request`, Status, Attach, Track Changes |
| L5 | доступ | Role Permission + Permission Level 1 + If Owner + User Permission + Share |
| L6 | совместная работа | Assign To, ToDo, Comments, Timeline, Tags, Kanban |
| L7 | процесс | Workflow поверх существующего `status` |
| L8 | контроль | Report Builder, Number Cards, Chart, Workspace |
| L9 | штатная автоматизация | Notification, Assignment Rule, scheduler |
| L10 | web intake | Web Form как отдельный канал создания |
| L11 | поставка | fixtures, customizations, clean-site acceptance |

---

# Модель данных

| Механизм | Где | Статус |
|---|---|---|
| Standard DocType | L1/L2/L4 | Core |
| Tree | L1 | Core |
| Link | L2/L4 | Core |
| Naming | L1/L2/L4 | Core |
| Title/Search Fields | L2/L4 | Core |
| Quick Entry | L2 | Core |
| Track Changes / Version | L2/L4/L6 | Core |
| Attach / File | L2/L4/L10 | Core |
| Allow Import | L3 | Core |
| Child DocType / Table | Lab A | Lab |
| Single | Lab F | Lab |
| Dynamic Link | Lab F | Lab |
| Table MultiSelect | Lab F | Lab |
| Virtual DocType | — | Later |

Постоянное предметное ядро не расширяется только ради покрытия механизма.

---

# Permissions

| Механизм | Где | Статус |
|---|---|---|
| User / System User | L5 | Core |
| Website User / Guest | L10 | Core |
| Role | L5 | Core |
| Role Permission Manager | L5 | Core |
| Read / Write / Create | L5 | Core |
| Delete | L5 | Core, временный эксперимент; финально Off |
| Report / Export / Import | L5 | Core |
| If Owner | L5 | Core |
| Permission Level 1 | L5+ | Core, защита содержательных полей `Service Request` |
| User Permission | L5 | Core, временный эксперимент |
| Share | L5 | Core, временный эксперимент |
| Mask / Data Masking | Lab F | Lab |
| Permission Type [v16+] | — | Later |
| custom `has_permission` / query conditions | — | Later |

## Конкретная модель `Service Request`

### Level 0 — Document

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No; Report/Export
```

### Permission Level 1 — business content

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

### Status

```text
до L7
→ обычный Select, Permission Level 0

после L7
→ тот же field + Workflow transition validation
```

Отдельный Permission Level для status в Core не используется.

`Permission Type [v16+]` оставлен на Later, потому что его практический смысл проявляется при собственном программном действии, которое должно проверять дополнительное право.

---

# Совместная работа и история

| Механизм | Где | Статус |
|---|---|---|
| Assign To | L6 | Core |
| ToDo | L6/L9 | Core |
| Due Date | L6/L9 | Core |
| Comments | L6 | Core |
| Timeline | L4/L6/L7 | Core |
| Track Changes / Version | L4/L6/L7 | Core |
| Tags | L6 | Core |
| Kanban | L6/L7 | Core |

```text
Assignment = responsibility
Assignment ≠ authorization
Assignment ≠ Workflow state
```

---

# Состояние и Workflow

| Механизм | Где | Статус |
|---|---|---|
| обычный Status Select | L4–L6 | Core |
| Workflow / State / Action Master | L7 | Core |
| Transition | L7 | Core |
| Allowed Role | L7 | Core, server transition gate |
| Condition | L7 | Core, временный эксперимент |
| Only Allow Edit For | L7 | Core, Desk guard |
| Read Only status | L7 | Core, UI guard |
| Is Submittable / DocStatus | Lab B | Lab |
| Allow on Submit | Lab B | Lab |

Главный учебный переход:

```text
до Workflow:
Select = значения, переходы не ограничены моделью процесса

после Workflow:
Workflow = допустимые переходы
```

---

# Интерфейс и представления

| Механизм | Где | Статус |
|---|---|---|
| Form | L0–L7 | Core |
| List | L0–L8 | Core |
| Tree | L1 | Core |
| Kanban | L6/L7 | Core |
| Workspace | L8 | Core |
| Calendar / Gantt | Lab F | Lab |
| DocType Layout | — | Later: отсутствует в закреплённом `v16.32.0` |
| собственный frontend | — | Later |

`DocType Layout` архитектурно полезен для задачи «одни и те же Documents нужно показывать по-разному», но текущий практикум не объявляет его изученным: прямой путь к этому DocType отсутствует в exact tag `v16.32.0`. Механизм попадёт в исполняемый курс после обновления и повторной проверки базовой версии.

---

# Аналитика

| Механизм | Где | Статус |
|---|---|---|
| Report Builder | L8 | Core |
| Filters / Group By / Count | L8 | Core |
| Number Card | L8 | Core |
| Dashboard Chart | L8 | Core |
| Workspace | L8 | Core |
| Shortcut / Quick List | L8 | Core |
| Query Report | — | Later |
| Script Report | — | Later |
| внешний BI/OLAP | — | Later |

Core не создаёт аналитический `DocType` ради данных, которые уже читаются из `Service Request`.

---

# Автоматизация

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
| scheduler / scheduled standard automation | L0/L9 | Core |
| Auto Repeat | Lab C | Lab |
| Background Jobs / `frappe.enqueue` | — | Later |
| `enqueue_after_commit` | — | Later |
| custom scheduled events | — | Later |

L0 только показывает наличие scheduler/workers. L9 изучает штатные декларативные автоматизации. Собственную фоновую задачу Core не проектирует.

---

# Web

| Механизм | Где | Статус |
|---|---|---|
| Standard Web Form | L10 | Core |
| Published / Route | L10 | Core |
| Guest submission | L10 | Core, временный эксперимент |
| Login Required | L10 | Core, финально On |
| Website User | L10 | Core |
| Web Form create path | L10 | Core |
| Allow Edit | L10 | Core, временно; финально Off |
| Show List | L10 | Core, финально On |
| Apply Document Permissions | L10 | Core, experiment for existing docs; финально Off |
| Allow Read On All Link Options | L10 | Core, trusted-internal policy |
| role-restricted/public portal | — | Later |

```text
Desk Create
→ Role Permission + Permission Level path

Web Form Create
→ отдельная capability
```

`Login Required` изучается как authentication boundary, а не как role-specific authorization.

---

# Расширение и кастомизация

| Механизм | Где | Статус |
|---|---|---|
| Standard DocType source | L0–L4 | Core |
| Customize Form | Lab D | Lab |
| Custom Field | Lab D | Lab |
| Property Setter | Lab D | Lab |
| Export Customizations | L11/Lab D | Core/Lab |
| Server Script | — | Later |
| Client Script / custom JS | — | Later |
| `doc_events` / hooks | — | Later |
| `extend_doctype_class` | — | Later |
| override/fork | — | Later |

Core сначала осваивает метаданные и стандартную настройку; программные точки расширения не считаются запрещёнными.

---

# Packaging / deployment / verification

| Механизм | Где | Статус |
|---|---|---|
| Standard source in Git | L0+ | Core |
| fixtures / fixture_auto_order | L11 | Core |
| export-fixtures | L11 | Core |
| exported Custom DocPerm | L11 | Core |
| install-app | L0/L11 | Core |
| migrate | L11/Lab D | Core/Lab |
| clean-site acceptance | L11 | Core |
| patches | — | Later |
| automated `FrappeTestCase` / `bench run-tests` | — | Later |
| migration tests | — | Later |

Core доказывает воспроизводимость вручную на чистом Site. Автоматизированные tests вводятся позже вместе с собственным программным поведением.

---

# Realtime / API / интеграции

| Механизм | Где | Статус |
|---|---|---|
| built-in Document REST API | — | Later |
| whitelisted methods / RPC | — | Later |
| Webhook | — | Later |
| Realtime API / `publish_realtime` | — | Later |
| custom integration service | — | Later |

Эти механизмы архитектурно нативны, но требуют отдельного программного/интеграционного блока и не добавляются в Core ради формального покрытия.

---

# Labs

Labs, затрагивающие `Service Request`, обязаны вернуть:

```text
Level 0 document matrix
Permission Level 1 content matrix
Workflow
```

Lab A временный `work_logs` получает Permission Level 1, потому что в учебной модели это содержательные данные заявки.

Lab B доказывает различие Status / Workflow / DocStatus.

Lab C доказывает Auto Repeat как отдельную штатную автоматизацию.

Lab D различает Standard source и site/app customization.

Lab F покрывает специальные Field Types и доступные в `v16.32.0` представления, не превращая полигон в постоянную предметную модель.

---

# Правило матрицы

```text
механизм изучен
≠ механизм обязан использоваться в реальном приложении
```

И наоборот:

```text
механизм находится в Later
≠ он не-Frappe-native
```

Курс принят архитектурно, если ученик умеет объяснить **почему механизм выбран по смыслу и какую ответственность он не решает**.
