# Лабораторная 45. Server Script

## Цель

Увидеть Server Script в трёх режимах и сравнить его с Client Script на одном `Request`.

## Подготовка

Server Scripts должны быть включены на учебном Bench:

```bash
cd ~/frappe/frappe16-course-bench
bench set-config -g server_script_enabled 1
bench restart
```

Проверь `sites/common_site_config.json`.

## Эксперимент 1 — DocType Event validation

В `Request` добавь поле:

```text
Result  Small Text
```

Создай Server Script:

```text
Script Type: DocType Event
Reference Document Type: Request
DocType Event: Before Save
```

Код:

```python
if doc.status == "Done" and not doc.result:
    frappe.throw("Result is required for Done Request")
```

### Проверка через Desk

Попробуй сохранить Done без Result — должен быть отказ.

### Проверка через REST

Отправь update того же типа через API — должен быть тот же server-side отказ.

Это ключевой опыт главы.

## Эксперимент 2 — API Server Script

Создай:

```text
Script Type: API
API Method: training-request-summary
Allow Guest: off
```

Код:

```python
count = frappe.db.count("Request")
frappe.response["message"] = {"request_count": count}
```

Вызови `/api/method/training-request-summary` под authenticated user.

Временно включи Rate Limit с маленьким лимитом и вызови endpoint несколько раз, чтобы увидеть ограничение. Затем верни разумное состояние.

## Эксперимент 3 — Scheduler Event

Создай Scheduler Event, который пишет безопасную диагностическую запись, например Error Log/лог с количеством Request. Для лаборатории используй подходящую frequency или ручной запуск scheduler job согласно v16, не жди реальный день.

Проверь связанный `Scheduled Job Type`.

## Restricted Python

Попробуй выполнить запрещённый arbitrary import/операцию, например `import os`, и посмотри restricted compilation/runtime error. После этого удали запрещённый код.

## Намеренная ошибка

В `After Save` не делай бесконечный `doc.save()`. Если хочешь увидеть принцип рекурсии, разберись на бумаге/в коде без запуска опасного бесконечного цикла.

## Проверка себя

Объясни различие:

```text
Client Script   → browser/UI
DocType Event   → server lifecycle
API Script      → HTTP endpoint
Scheduler Event → scheduled server execution
```

## Состояние после лабораторной

Оставь работающую validation `Done → Result required`. API и Scheduler scripts можно оставить Disabled после проверки, чтобы они не создавали лишнюю поверхность/нагрузку.
