# Второй учебный практикум Frappe — lifecycle

Статус: **архитектурная база и roadmap прошли аудит; CORE specification создана и ожидает отдельного аудита; executable exercises ещё не начаты**.

Практикум изучает управляемый lifecycle собственного `Purchase Request`:

```text
plain Document
→ plain status
→ Workflow
→ process policies
→ conditional approval
→ docstatus / Submit
→ Cancel
→ Amend
→ delivery
→ tests
→ clean Site acceptance
```

Он является отдельной второй ступенью после [`docs/frappe-training`](../frappe-training/README.md) и не зависит от предметной модели `rental_training`.

## Читать в таком порядке

1. [`ARCHITECTURE_CORRECTIONS.md`](ARCHITECTURE_CORRECTIONS.md) — обязательная архитектурная коррекция; имеет приоритет над отменённой формулировкой про `status.Allow on Submit` в ранних слоях.
2. [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md) — предметная и архитектурная граница практикума.
3. [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md) — требования `R01–R17`, NEXT и GATE.
4. [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md) — реальные зависимости `P00–P15`.
5. [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md) — практический маршрут `S00–S10`.
6. [`ROADMAP_AUDIT.md`](ROADMAP_AUDIT.md) — обязательный gate после злого аудита roadmap.
7. [`CORE_STAGE_SPECIFICATION.md`](CORE_STAGE_SPECIFICATION.md) — точные App/Site/Module names, schema, naming, roles/DocPerm, Workflow, LIMIT, transitions, fixtures, control data, tests и clean-site contract.

Roadmap gate пройден. Stage map `S00–S10` сохранён.

CORE specification уже фиксирует, в частности:

```text
App = purchase_lifecycle_training
Module = Purchase Lifecycle Training
Dev Site = purchase-lifecycle.localhost
Acceptance Site = purchase-lifecycle-acceptance.localhost
Namespace = PLT
Naming = PLT-PR-.#####
APPROVAL_LIMIT = 1000
```

а также:

```text
transition-level Allow Self Approval policy
status.No Copy = yes после включения Workflow
status.Allow on Submit = no для текущего CORE
минимальный Senior DocPerm
reset несовместимых disposable Approved/docstatus0 records перед S06
Only Allow Edit For = Desk policy, не server immutability
Role provisioning из Standard DocPerm
ordered Workflow Action Master → Workflow State → Workflow fixtures
source-backed native Amend expectation
```

Следующий gate:

```text
злой аудит CORE_STAGE_SPECIFICATION
↓
только после него
executable exercises S00–S10
```

Executable exercises нельзя начинать по одной specification без её отдельного аудита.

## Нормативная база

- [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md);
- [`13_ROLE_PROVISIONING.md`](../frappe-architecture-standard/13_ROLE_PROVISIONING.md).

Если текст практикума конфликтует с нормативной базой, текущими corrections или фактическим поведением принятой версии Frappe, исправляется практикум.

## Что не входит во второй CORE автоматически

```text
Assignment / ToDo
Notification
File / Comment / Version
Print
REST API
Webhook
background jobs
scheduler
foreign DocType extension
custom frontend
reports
external integrations
production deployment
```

Эти механизмы появляются только из новых требований и могут стать материалом отдельных последующих практикумов.
