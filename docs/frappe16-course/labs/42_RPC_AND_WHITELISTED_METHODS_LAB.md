# Лабораторная 42. RPC и whitelisted methods

## Цель

Вызвать серверную Python-функцию как command и сравнить это с resource REST API.

## Шаг 1. Создай Python module

В терминале:

```bash
cd ~/frappe/frappe16-course-bench
```

Найди корневой Python package учебного App:

```bash
find apps/training -maxdepth 3 -name hooks.py -print
```

Рядом с `hooks.py` должен находиться package `training`.

Создай/открой файл `api.py` в этом package и добавь:

```python
import frappe


@frappe.whitelist()
def ping_training(name=None):
    return {
        "message": "pong",
        "name": name,
        "user": frappe.session.user,
    }
```

Не создавай второй случайный package, если `training/api.py` уже существует.

## Шаг 2. Убедись, что dev server видит изменение

Если `bench start` не подхватил новый Python module, останови его `Ctrl+C` и снова запусти:

```bash
bench start
```

## Шаг 3. Используй session из лабораторной 41

Проверь:

```bash
test -f /tmp/frappe-course.cookies && echo "cookie jar exists"
```

Если файла нет, повтори login-шаг из лабораторной 41.

## Шаг 4. Вызови method через curl

```bash
curl -sS \
  -b /tmp/frappe-course.cookies \
  -G \
  --data-urlencode 'name=terminal' \
  http://learn.localhost:8000/api/method/training.api.ping_training
```

Ожидается response с:

```text
pong
terminal
Administrator
```

## Шаг 5. Вызови method из Desk

Открой Browser DevTools → Console на странице Desk:

```javascript
frappe.call({
    method: 'training.api.ping_training',
    args: {name: 'browser'}
}).then(r => console.log(r.message));
```

## Эксперимент

Убери decorator:

```python
@frappe.whitelist()
```

перезапусти dev server при необходимости и повтори HTTP-вызов.

Ожидается отказ: наличие Python function не делает её RPC endpoint автоматически.

Верни decorator.

## Намеренная ошибка мышления

Сравни две задачи:

```text
изменить Priority Request
→ REST resource update подходит

Approve Request с permissions, conditions и side effects
→ отдельная server command часто понятнее
```

Не реализуй Approve в этой лабораторной — цель увидеть границу.

## Проверка себя

Объясни:

```text
/api/resource/... → CRUD над Document
/api/method/...   → RPC вызов whitelisted server method
```

## Состояние после лабораторной

Оставь:

```text
training.api.ping_training
```

Удалить временную session cookie можно после проверки:

```bash
rm -f /tmp/frappe-course.cookies
```
