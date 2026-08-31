# Лабораторная 27. Notification

## Цель

Увидеть штатный trigger/condition/template без написания Python.

## Создай Notification

Для `Request` настрой простое событие, например:

```text
Document Event: Value Change / Save
условие: workflow_state == "Review"
```

Получатель — один из учебных пользователей или роль, в зависимости от доступных настроек.

Текст:

```text
Request {{ doc.name }} ожидает проверки.
Subject: {{ doc.subject }}
```

## Проверь trigger

Переведи Request в Review.

Если SMTP не настроен, не делай вывод «Notification не работает» только по отсутствию внешнего письма. Проверь связанные Frappe Records:

```text
Email Queue
Communication
Notification Log
```

в зависимости от выбранного канала.

## Эксперимент

Измени condition так, чтобы Notification не срабатывала, и повтори Save на новом Request. Затем верни condition.

## Намеренная ошибка

Сделай шаблон со ссылкой на несуществующее поле `{{ doc.no_such_field }}`. Посмотри, как проявляется ошибка/пустое значение, затем исправь.

## Проверка себя

Когда достаточно Notification, а когда нужен Server Script? Ответ должен опираться на сложность trigger/action, а не на предпочтение «код удобнее».

## Состояние после лабораторной

Оставь одну понятную Notification, но при необходимости выключи её, чтобы не засорять Email Queue в следующих упражнениях.
