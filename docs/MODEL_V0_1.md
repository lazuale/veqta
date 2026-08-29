# VEQTA — модель v0.1

Модель ниже проверяется на первом prototype и пока не является стабильным API.

## Work Type

```text
code         Data        required, stable identifier
title        Data        required, display name
description  Small Text  optional
disabled     Check       optional
```

Проверяем `code` как `name` документа и изменение `title` без нарушения ссылок.

## Work Item

```text
title           Data        required
work_type       Link        required -> Work Type
description     Text Editor optional
due_at           Datetime    optional
workflow_state  Link        managed by Frappe Workflow
```

Системные поля Frappe не дублируются.

## State

На v0.1 используется Frappe Workflow / Workflow State. Проверяем один Workflow для разных `Work Type` через Transition Conditions.

## Assignment

Отдельного `responsible` / `assigned_to` в `Work Item` нет. Проверяется штатный `Assign To` и связанные `ToDo`.

## State history

Сначала проверяются `Version`, Timeline и Workflow comments.

Если из них нельзя надёжно получить:

```text
work_item
from_state
to_state
changed_by
changed_at
```

проверяется минимальный `Work State Change`.

## Инварианты

- один бизнес-факт — один источник истины;
- ключевые данные структурированы;
- производные показатели вычисляются из первичных фактов;
- штатный механизм Frappe не дублируется без необходимости.
