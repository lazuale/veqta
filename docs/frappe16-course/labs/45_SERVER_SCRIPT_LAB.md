# Лабораторная 45. Server Script

## Цель

Увидеть Server Script в нескольких режимах и сравнить его с Client Script на одном `Request`.

## Шаг 1. Включи Server Scripts

Во втором терминале:

```bash
cd ~/frappe/frappe16-course-bench
bench set-config -g server_script_enabled 1
```

Проверь:

```bash
grep -n 'server_script_enabled' sites/common_site_config.json
```

На учебном стенде процессы запущены через `bench start`, поэтому **не используй `bench restart` как production-команду**.

Перейди в первый терминал, останови dev stack:

```text
Ctrl+C
```

и снова запусти:

```bash
cd ~/frappe/frappe16-course-bench
bench start
```

## Эксперимент 1 — DocType Event validation

В `Request` добавь поле, если его ещё нет:

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

Попробуй сохранить:

```text
Status = Done
Result = пусто
```

Ожидается отказ.

Заполни `Result` и сохрани успешно.

### Проверка через REST

Используй token authentication из главы 43 либо снова создай временную session как в лабораторной 41.

Попробуй REST update:

```text
Status = Done
Result = пусто
```

Должен быть **тот же server-side отказ**.

Это ключевой опыт главы:

```text
Client Script может не выполниться
Server Script validation выполняется на сервере
```

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
frappe.response["message"] = {
    "request_count": count
}
```

Вызови:

```text
/api/method/training-request-summary
```

под authenticated user.

Затем включи небольшой Rate Limit, например 3 запроса за 60 секунд, и быстро вызови endpoint несколько раз.

Увидь rate-limit response, после чего выключи экспериментальный маленький лимит или верни разумное значение.

## Эксперимент 3 — Scheduler Event

Создай Scheduler Event, который выполняет безопасное наблюдаемое действие, например:

```python
frappe.log("Training Request count: " + str(frappe.db.count("Request")))
```

Выбери подходящую учебную frequency и проверь созданный связанный `Scheduled Job Type`.

Чтобы не ждать реальный день, используй штатные scheduler/bench инструменты, описанные в главе, для ручной проверки job на dev Site. Не создавай отдельный Linux cron.

## Restricted Python

Создай отдельный временный Server Script и попробуй запрещённый arbitrary import:

```python
import os
```

Посмотри `Compilation warning`/restricted execution error.

После эксперимента удали запрещённый код или отключи этот Script.

## Намеренная опасная идея, которую не запускаем

Не запускай в `After Save`:

```python
doc.save()
```

для того же документа без контроля.

Разбери цепочку на бумаге:

```text
Save
→ After Save
→ doc.save()
→ Save
→ After Save
→ ...
```

Здесь задача — понять рекурсию, а не повесить dev worker.

## Проверка себя

Объясни:

```text
Client Script   → browser/UI
DocType Event   → server Document lifecycle
API Script      → HTTP endpoint
Scheduler Event → scheduled server execution
```

и почему Server Script всё равно не равен произвольному Python-файлу App.

## Состояние после лабораторной

Оставь рабочую validation:

```text
Done → Result required
```

API и Scheduler Server Scripts после проверки можно оставить:

```text
Disabled = 1
```

чтобы они не создавали лишнюю поверхность и шум.
