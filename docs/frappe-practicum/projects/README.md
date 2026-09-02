# Проекты практикума

Проекты выполняются по порядку. Для работы использовать LABS, а README проекта — как
архитектурную спецификацию:

1. [Реестр оборудования](01-equipment-register/LABS.md) — данные и metadata.
2. [Заявки на закупку](02-purchase-requests/LABS.md) — Document lifecycle и процесс.
3. [Внешняя приёмная](03-service-intake/LABS.md) — trust boundary и web-контур.

Каждый проект создаёт собственный app и site. Переиспользуются общий Frappe Bench и
приобретённые навыки, но не DocType и рабочие данные предыдущего продукта.

После принятого P3 отдельный четвёртый продукт не создаётся. Следующий уровень продолжает
тот же `service_intake`, потому что именно там появляется естественная программная
ответственность:

[Engineering Bridge](../engineering/LABS.md)

```text
P1–P3
→ выбрать правильный native metadata/configuration mechanism

Engineering Bridge
→ выбрать правильный native programmatic extension point и lifecycle phase
```

Так курс не превращает программирование в отдельный искусственный app ради coverage.
