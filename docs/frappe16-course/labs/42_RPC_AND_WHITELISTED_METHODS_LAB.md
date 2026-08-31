# Лабораторная 42. RPC и whitelisted methods

## Цель

Вызвать серверную функцию как command и сравнить это с CRUD resource API.

## Создай method в App training

В подходящем Python module, например `training/api.py`, добавь минимальный method:

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

После изменения перезапусти dev server при необходимости.

## Вызови через curl

```bash
curl -s 'http://learn.localhost:8000/api/method/training.api.ping_training?name=test'
```

с нужной authentication.

## Вызови из browser console

```javascript
frappe.call({
  method: 'training.api.ping_training',
  args: {name: 'browser'}
}).then(r => console.log(r.message));
```

## Эксперимент

Убери `@frappe.whitelist()` и повтори вызов. Посмотри отказ. Затем верни decorator.

## Намеренная ошибка

Попытайся решить команду «Approve Request» через generic `PUT status=Approved`, хотя бизнес-действие требует проверок. Зафиксируй, почему RPC command может быть правильнее resource update для сложной операции.

## Проверка себя

Объясни:

```text
REST resource API → CRUD над Documents
RPC method        → вызов server function/command
```

## Состояние после лабораторной

Оставь `training.api.ping_training` как тестовый method.
