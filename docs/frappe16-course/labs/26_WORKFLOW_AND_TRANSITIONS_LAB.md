# Лабораторная 26. Workflow и переходы

## Цель

Создать настоящий Workflow и проверить разрешённые/запрещённые переходы разными ролями.

## Подготовка

В `Request` добавь поле для Workflow State, если Frappe не предложит создать/использовать его автоматически:

```text
workflow_state
```

## Создай Workflow States

Например:

```text
Draft
Review
Approved
Rejected
```

## Создай Workflow для Request

Минимальная схема:

```text
Draft --Send for Review--> Review
Review --Approve--> Approved
Review --Reject--> Rejected
Rejected --Reopen--> Draft
```

Роли:

```text
Training User    → Send for Review
Training Manager → Approve / Reject
```

## Проверь

1. Training User создаёт Request и отправляет в Review.
2. Training User пытается Approve — действие не должно быть доступно/разрешено.
3. Training Manager открывает тот же Request и Approve.
4. Создай второй Request и пройди ветку Reject → Reopen.

## Эксперимент

Добавь condition на один transition, например разрешать Approve только при заполненном `Due Date` или другом простом условии. Сравни два документа.

## Намеренная ошибка

Создай состояние/transition, из которого нет выхода, и доведи туда тестовый Request. Увидь проблему модели, затем исправь Workflow.

## Проверка себя

Нарисуй фактический граф transitions и укажи роль на каждой стрелке.

## Состояние после лабораторной

Оставь рабочий Workflow Draft → Review → Approved/Rejected.
