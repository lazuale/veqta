# Второй учебный практикум Frappe — lifecycle

Статус: **архитектурная база и roadmap прошли аудит; executable specification ещё не создана**.

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
6. [`ROADMAP_AUDIT.md`](ROADMAP_AUDIT.md) — обязательный gate после злого аудита roadmap; его точечные corrections имеют приоритет до финальной консолидации документов.

Следующий слой создаётся только из **всех шести** документов выше:

```text
CORE_STAGE_SPECIFICATION
→ executable exercises
→ clean-site acceptance
```

Нельзя начинать executable specification только по roadmap, игнорируя `ROADMAP_AUDIT.md`.

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
