# Жизненный цикл Document на Frappe

Практикум продолжает [первое приложение](../first-app/README.md) и показывает, как обычный Frappe `Document` превращается в управляемый процесс с `Workflow`, `Submit`, `Cancel` и `Amend`.

Вместо обзора возможностей Workflow здесь сначала появляется новое требование к внутренней заявке `Purchase Request`, затем выбирается штатный механизм Frappe и только после этого выполняется реализация.

## Что будет построено

```text
Purchase Request
├── subject
├── description
├── requested_amount
├── needed_by
└── status
```

По ходу практикума обычный `status : Select` становится полем состояния Workflow, появляется запрет одобрения собственной заявки, условный второй уровень согласования и системный жизненный цикл Document:

```text
Draft
→ Pending Approval
→ Rejected / Resubmit
→ Pending Senior при необходимости
→ Approved / docstatus 1
→ Cancelled / docstatus 2
→ Amend → новый Draft
```

Обязательная конфигурация Workflow затем переносится в App, закрепляется автоматическими тестами и проверяется установкой на новый чистый Site.

Практикум предполагает, что Bench, Site, App, Module, Standard DocType, developer mode, permissions, тесты и `migrate` уже знакомы по первому маршруту.

## Версия

Практикум подготовлен для **Frappe Framework v16**. Версионно-зависимые детали текущего маршрута проверены на **v16.33.0**.

## С чего начать

Практические этапы находятся в [`stages/`](stages/README.md) и проходятся последовательно от `S00` до `S10`.

Справочные материалы:

- [модель учебного приложения](APPLICATION_MODEL.md);
- [требования учебного приложения](REQUIREMENTS.md);
- [маршрут практикума](ROADMAP.md).

Архитектурные объяснения, на которые опираются задания, находятся в соседнем [архитектурном стандарте Frappe](../../frappe-architecture-standard/README.md).
