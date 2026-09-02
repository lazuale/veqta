# Frappe Architecture Standard

> Внутренний архитектурный стандарт проектирования приложений на Frappe Framework 16.

Этот раздел отвечает на один вопрос: **как принимать архитектурные решения, исходя из устройства самого Frappe, а не из привычек команды или шаблонов другого фреймворка**.

Стандарт не является официальным документом Frappe Technologies. Он собран из официальной документации Frappe, актуального upstream-кода и first-party практики ERPNext. Там, где правило является нашим архитектурным выводом, это должно быть указано прямо.

## Базовый принцип

Frappe — metadata-driven, full-stack, low-code framework. Его стандартная модель уже включает DocType/Document, permissions, lifecycle, UI, REST API, jobs, scheduler, notifications, reports и extension hooks.

Поэтому нативное решение строится так:

```text
требование
    ↓
какая ответственность нужна?
    ↓
какой Frappe primitive уже владеет этой ответственностью?
    ↓
совпадает ли его семантика с задачей?
    ↓
ДА → используем primitive
НЕТ → ищем официальный extension seam
    ↓
только при отсутствии подходящего механизма
вводим собственную abstraction
```

Важно: это **не означает «никакого кода»**. Python Controller, service module, custom API, background job или собственный frontend могут быть совершенно нативными. Красный флаг — не наличие собственного кода, а **дублирование уже существующей ответственности Framework без причины**.

## Как читать стандарт

1. **[01_FOUNDATIONS.md](01_FOUNDATIONS.md)** — философия Frappe, ownership и границы Framework/App/Site.
2. **[02_DATA_MODEL.md](02_DATA_MODEL.md)** — DocType, поля, Link, Child Table, Single, Virtual, Naming.
3. **[03_DOCUMENT_LIFECYCLE.md](03_DOCUMENT_LIFECYCLE.md)** — Document, Controller, Client/Server Script, services и state model.
4. **[04_SECURITY.md](04_SECURITY.md)** — permissions runtime и design escalation.
5. **[05_TRANSACTIONS_ASYNC.md](05_TRANSACTIONS_ASYNC.md)** — transactions, DB API, background jobs, scheduler.
6. **[06_API_INTEGRATION.md](06_API_INTEGRATION.md)** — REST, methods, Webhooks и integration contracts.
7. **[07_EXTENSION_CUSTOMIZATION.md](07_EXTENSION_CUSTOMIZATION.md)** — Custom Field, hooks, extension/override, site customization.
8. **[08_UI_REPORTING.md](08_UI_REPORTING.md)** — Desk, views, reports, Web Forms и custom UI.
9. **[09_DEPLOYMENT_TESTING.md](09_DEPLOYMENT_TESTING.md)** — migrations, patches, fixtures, воспроизводимость и tests.
10. **[10_DECISION_STANDARD.md](10_DECISION_STANDARD.md)** — итоговый design-review protocol и responsibility matrix.
11. **[11_EXAMPLES.md](11_EXAMPLES.md)** — типовые правильные и неправильные решения понятным языком.
12. **[12_EVIDENCE_REGISTER.md](12_EVIDENCE_REGISTER.md)** — реестр первичных источников и статусов доказательств.

## Как маркируются утверждения

Каждое существенное нормативное правило должно быть разложено на четыре части:

```text
ФАКТ FRAPPE
что Framework действительно предоставляет или гарантирует

ПРУФ
официальная документация / versioned upstream / first-party implementation

АРХИТЕКТУРНОЕ СЛЕДСТВИЕ
какое решение из этого разумно следует

ГРАНИЦА / ИСКЛЮЧЕНИЕ
когда это решение перестаёт быть лучшим вариантом
```

Это не позволяет превращать мнение автора в «так задумал Frappe».

## Версионная база

Стандарт ориентирован на **Frappe v16** и проверен по ветке `version-16`. Версионно зависимые возможности должны быть отмечены рядом с правилом.

Особенно это относится к:

- `extend_doctype_class` — v16+;
- ограничениям Server Script;
- REST API v2;
- naming changes/deprecations;
- Python/Node runtime requirements.

Не следует переписывать весь стандарт при каждом patch-релизе. Проверяется major-line и только те места, где поведение реально изменилось.

## Что стандарт не делает

Он не проектирует конкретное приложение.

Он не говорит:

```text
всегда делай Workflow
всегда делай Child Table
никогда не делай Service
никогда не делай custom API
```

Он требует другой дисциплины:

> **перед созданием собственного механизма уметь назвать существующий Frappe primitive, объяснить его семантику и показать, почему её недостаточно для конкретной задачи.**

Именно это является основой Frappe-native design review.
