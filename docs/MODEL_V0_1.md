# VEQTA — модель v0.1

Эта модель проверяется на первом prototype и пока не является стабильным API.

## Work Type

```text
code   Data  required, stable identifier
title  Data  required, display name
```

Проверяется `code` как `name` документа и изменение `title` без нарушения ссылок.

## Work Item

```text
title           Data  required
work_type       Link  required -> Work Type
workflow_state  Link  managed by Frappe Workflow
```

Системные поля Frappe не дублируются.

## State

Проверяется Frappe Workflow / Workflow State: один Workflow для разных `Work Type` через Transition Conditions.

## Assignment

Проверяется штатный `Assign To` и связанные `ToDo`. Отдельного `responsible` / `assigned_to` в `Work Item` на v0.1 нет.

## State history

Проверяются `Version`, Timeline и Workflow comments на возможность получить состояние, пользователя и время перехода в структурированном виде.
