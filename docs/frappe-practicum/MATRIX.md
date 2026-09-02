# Матрица покрытия Frappe

Матрица проверяет уже спроектированный курс, а не генерирует предметную модель.

Обозначения:

- **●** — механизм впервые выполняется и проверяется;
- **↺** — снова применяется в более сложном контексте;
- **○** — рассматривается/сравнивается как граница, но не внедряется в продукт;
- **—** — в текущем маршруте не нужен.

```text
mechanism known
≠ mechanism must be used
```

---

# 1. Platform / app / deployment

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| Bench / site | ● | ↺ | ↺ | ↺ | P1.1, P2.1, P3.1, E7/E9 |
| `bench new-app` | ● | ↺ | ↺ | — | P1.1, P2.1, P3.1 |
| Module | ● | ↺ | ↺ | ↺ | project setup/source |
| Developer Mode | ● | ↺ | ↺ | ↺ | P1.1, P2.1, P3.1 |
| Apps Page / Workspace Sidebar | ● | ↺ | ↺ | — | project workspace labs |
| Git | ● | ↺ | ↺ | ↺ | every delivery gate |
| clean `install-app` | ● | ↺ | ↺ | ↺ | P1.6, P2.7, P3.7, E7/E9 |
| upgrade existing site | — | — | — | ● | E6/E9 |
| dedicated test site | — | — | — | ● | E7/E9 |
| `bench migrate` | ● | ↺ | ↺ | ↺ | delivery + E6/E9 |
| fixtures | ● | ↺ | ↺ | ↺ | P1.6, P2.7, P3.7 |
| exported customizations | ○ | — | — | — | область применения, не нужна своим Standard DocType |
| `patches.txt` / data patch | — | — | — | ● | E6 |

---

# 2. Data model

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| Standard DocType | ● | ↺ | ↺ | ↺ | P1.2, P2.2, P3.2, E2 |
| Document/system fields | ● | ↺ | ↺ | ↺ | all projects |
| Data / Select / Date / Text / Check | ● | ↺ | ↺ | ↺ | project models |
| Link | ● | ↺ | ↺ | ↺ | project models/E1 |
| Child Table | ● | ↺ | — | — | P1.2, P2.2 |
| Tree DocType | ● | — | — | — | P1.2 |
| naming by field / Set Only Once | ● | — | ↺ | ↺ | P1/P3 |
| naming format | — | ● | ↺ | ↺ | P2/P3 |
| Mandatory / Unique | ● | ↺ | ↺ | ↺ | project models/E1–E3 |
| Track Changes / Timeline history | ● | ↺ | ↺ | ↺ | P1/P2/P3/E3 |
| submittable / docstatus | — | ● | — | — | P2.2–P2.5 |
| Single DocType | ○ | — | ○ | — | model comparison only |
| Dynamic Link | ○ | — | — | — | ordinary Link preferred when target known |
| Virtual DocType | — | — | ○ | — | next integration level |

Architecture gate:

```text
DocType / Link / Child / Tree
chosen by identity/lifecycle/reference semantics
not by noun counting
```

---

# 3. Views / data operations / reporting

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| Form | ● | ↺ | ↺ | ↺ | all projects |
| List / filters / sorting | ● | ↺ | ↺ | ↺ | working scenarios |
| Data Import | ● | — | — | — | P1.3 |
| Data Export | ● | — | — | — | P1.3 |
| Kanban | ● | — | — | — | P1.5; not Workflow bypass |
| Calendar | — | ● | — | — | P2.6 |
| Report Builder | ● | ↺ | ↺ | — | P1.5, P2.6, P3.5 |
| Number Card | ● | ↺ | ↺ | — | P1.5, P2.6, P3.5 |
| Dashboard Chart | — | ● | ↺ | — | P2.6, P3.5 |
| Workspace | ● | ↺ | ↺ | — | all project workplace labs |
| Print Format / PDF | — | ● | — | — | P2.6 |
| Query Report | — | — | ○ | — | later when Report Builder semantics are insufficient |
| Script Report | — | — | ○ | — | later procedural reporting |

---

# 4. Permissions

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| User / System User | ● | ↺ | ↺ | ↺ | permission labs/API test |
| Website User / Guest | — | — | ● | — | P3.4 |
| Standard DocType permissions | ● | ↺ | ↺ | ↺ | P1.2/P2.2/P3.2 |
| Role Permission Manager | ○ | ○ | — | — | effective matrix observation |
| Read/Write/Create/Delete | ● | ↺ | ↺ | ↺ | P1.4/P2.4/P3/E1–E4 |
| Submit/Cancel/Amend | — | ● | — | — | P2.3–P2.5 |
| If Owner | ● | ↺ | — | — | P1/P2 |
| Permission Level | — | ● | ↺ | ↺ | P2/P3/E2 |
| User Permission | ● | ↺ | — | — | P1/P2 |
| Share | ● | — | — | — | P1.4 temporary |
| `doc.check_permission` | — | — | — | ● | E1/E3 |
| permission-aware `insert/save` | ○ | ○ | ○ | ● | E3/E4 |
| `ignore_permissions=True` boundary | ○ | ○ | ● Web Form fact | ↺ test helpers only | P3/E7 |
| custom permission hooks | — | — | — | ○ | next level, no product need |
| Permission Types | — | — | — | ○ | next action-specific permission scenario |

Important:

```text
permission-aware Document API
≠ ignore_permissions bypass
```

Engineering command intentionally keeps ordinary permission enforcement.

---

# 5. Lifecycle / state / collaboration

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| ordinary Select state | ● | ○ | — | — | P1 status |
| Document save/submit/cancel/amend | ○ | ● | ○ | ↺ | P2.3/E1–E3 |
| `before_insert` creation invariant | — | — | — | ● | E1 |
| `validate` as broader save-time lifecycle | ○ | ○ | ○ | ○ | compared in E1; deliberately not owner of creation-only rule |
| Workflow | — | ● | ↺ | — | P2.5/P3.3 |
| Workflow Action | — | ● | ↺ | — | P2/P3 |
| Workflow + docstatus | — | ● | — | — | P2.5 |
| Assign To / ToDo | — | ● | ↺ | — | P2.6/P3.5 |
| Comments / Timeline | ○ | ↺ | ↺ | ● via `add_comment` | E3 |
| Notification | — | ● | ↺ | — | P2.6/P3.5 |
| Assignment Rule | — | ○ | — | — | comparison only |
| whitelisted Document method | — | — | — | ● | E3/E4 |

Lifecycle gate:

```text
creation-only invariant
→ before_insert

rule that must hold on every save
→ validate or another matching lifecycle phase
```

Правильный Controller с неправильной lifecycle phase не принимается.

---

# 6. Web / API / integration

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| Web Form | — | — | ● | — | P3.4 |
| Guest/public route | — | — | ● | — | P3.4 |
| Login Required comparison | — | — | ● | — | P3.4 |
| Web Form create-path boundary | — | — | ● | ↺ | P3 architecture/E reasoning |
| built-in Document REST CRUD | — | — | ● read | ↺ | P3.6/E4 comparison |
| REST API v2 document method | — | — | — | ● | E4 |
| custom semantic command | — | — | — | ● | E3/E4 |
| duplicate CRUD endpoint | — | — | — | rejected | E3 architecture |
| Webhook | — | — | ○ | ○ | E8 decision lab |
| Webhook post-commit queue path | — | — | — | ○ | E8 exact-v16 source reading |
| custom integration service | — | — | — | ○ | only when orchestration/protocol appears |

---

# 7. Transactions / async

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| Framework request transaction | ○ | ○ | ○ | ● | E5 |
| uncaught exception rollback | — | — | — | ● | E5 rollback probe |
| manual `frappe.db.commit()` | — | — | — | rejected | E5 |
| `frappe.db.after_commit` concept | — | — | — | ○ | E8 |
| `frappe.enqueue` | — | — | — | ○ | E8 |
| `enqueue_after_commit=True` | — | — | — | ○ | E8 |
| job id / deduplicate | — | — | — | ○ | E8 |
| custom Background Job in product | — | — | — | — | no real long-running responsibility |

Not using a job is intentional architecture, not missing knowledge.

---

# 8. Migrations / tests

| Возможность | P1 | P2 | P3 | Engineering | Где |
|---|:---:|:---:|:---:|:---:|---|
| schema sync from DocType JSON | ● | ↺ | ↺ | ↺ | delivery/E2/E6 |
| `patches.txt` | — | — | — | ● | E6 |
| pre/post model sync distinction | — | — | — | ● | E6 |
| one-off direct DB migration | — | — | — | ● | E6 |
| Patch Log / one-time execution | — | — | — | ● | E6 |
| `IntegrationTestCase` | — | — | — | ● | E7 |
| `bench run-tests --app` | — | — | — | ● | E7/E9 |
| dedicated `intake-test.localhost` | — | — | — | ● | E7/E9 |
| permission acceptance outside test helper | ● | ↺ | ↺ | ↺ | P1–P3/E4 |
| regression: Agent save without Intake Read | — | — | — | ● | E1/E7 |
| clean install test | ● | ↺ | ↺ | ↺ | project gates/E9 |
| upgrade test | — | — | — | ● | E6/E9 |

Tests cover application-owned behavior. They do not re-prove that Frappe Link or
Mandatory generally work, and working site is not used as the automated-test database.

---

# 9. Extension mechanisms deliberately not forced into these products

| Механизм | Решение курса |
|---|---|
| Client Script | next UX-specific requirement; never sole server guarantee |
| Server Script | site/runtime customization boundary; not source-owned app logic here |
| `doc_events` | use when reacting to another DocType/app; current own DocType uses controller |
| `extend_doctype_class` | extension seam for another app when exact pinned version/scenario requires it |
| full controller override | exceptional, composition/conflict cost must be justified |
| service/domain module | valid only for real cross-document/reusable/integration complexity |
| Virtual DocType | next external-data-as-Document scenario |
| Realtime | next live-update scenario |
| Query/Script Report | next reporting requirement beyond Report Builder |
| Auto Repeat | not imposed on equipment/requests merely for exercise |
| Gantt | only with real start/end planning semantics |
| specialized fields | Geolocation/Signature/Barcode only when product requires them |

---

# Итог

Полный маршрут закрывает две разные способности:

```text
A. выбрать и собрать правильный metadata-driven Frappe solution
B. распознать момент, когда требуется native programmatic extension
```

Курс принят архитектурно, если ученик умеет объяснить не только как применить механизм,
но и почему соседний механизм или другая lifecycle phase здесь не являются владельцем
ответственности.
