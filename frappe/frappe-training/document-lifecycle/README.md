# Жизненный цикл Document на Frappe

Этот практикум посвящён не созданию предметной модели с нуля, а следующей задаче: как превратить обычный `Document` в управляемый процесс и затем в зафиксированный транзакционный факт средствами самого Frappe.

Учебная модель — внутренняя заявка на закупку `Purchase Request`.

```text
обычный Document
→ обычный status
→ Workflow
→ правила переходов
→ условное согласование
→ Submit / docstatus
→ Cancel
→ Amend
→ поставка конфигурации App
→ тесты
→ чистый Site
```

Практикум предполагает, что [первое приложение](../first-app/README.md) уже пройдено: Bench, Site, App, Module, Standard DocType, developer mode, permissions, тесты и `migrate` здесь не объясняются заново.

## Что будет построено

Один Standard DocType:

```text
Purchase Request
├── subject
├── description
├── requested_amount
├── needed_by
└── status
```

Процесс развивается по мере появления новых требований. Сначала `status` остаётся обычным `Select`. `Workflow` появляется только тогда, когда возникает правило «кто и из какого состояния имеет право перейти дальше». `Is Submittable` появляется ещё позже — когда окончательное согласование должно стать зафиксированным фактом с `docstatus = 1`.

## Версия

Практикум рассчитан на **Frappe Framework v16**. Версионно-зависимые детали проверены на **v16.33.0**.

Для `Workflow` и `docstatus` опорными являются:

- [официальная документация Workflow](https://docs.frappe.io/erpnext/user/manual/en/workflows);
- [`frappe/model/workflow.py` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py);
- [`frappe/workflow/doctype/workflow/workflow.py` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

## С чего начать

Этапы находятся в [`stages/`](stages/README.md) и проходятся последовательно от `S00` до `S10`.

Справочные материалы:

- [модель учебного приложения](APPLICATION_MODEL.md);
- [требования](REQUIREMENTS.md);
- [маршрут практикума](ROADMAP.md).

Архитектурные объяснения находятся в [архитектурном стандарте Frappe](../../frappe-architecture-standard/README.md), прежде всего в главах о [Document lifecycle](../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md), [security](../../frappe-architecture-standard/04_SECURITY.md), [extension/customization](../../frappe-architecture-standard/08_EXTENSION_CUSTOMIZATION.md) и [delivery/testing](../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).
