# VEQTA — модель v0.1

Этот документ описывает **только модель, которую мы сейчас проверяем на первом стенде**.

Задача v0.1 — понять, можно ли описать разные виды обычной работы одной небольшой моделью и использовать для процесса штатные механизмы Frappe.

## Граница модели

Собственных DocType VEQTA в v0.1 **ровно два**:

```text
Work Type
Work Item
```

Следующие вещи **не являются сущностями VEQTA v0.1** и отдельно нами не разрабатываются:

```text
Workflow / Workflow State  → штатный Frappe
Assign To / ToDo           → штатный Frappe
Version / Timeline         → штатный Frappe
Desk                       → штатный Frappe
Kanban                     → штатный Frappe
```

Мы проверяем их только как готовые механизмы платформы, которые должны работать поверх наших двух DocType.

## Общая схема

```text
VEQTA

Work Type
    ↓
Work Item

Frappe вокруг Work Item

Workflow State       → текущее состояние
Assign To / ToDo     → назначение людей
Version / Timeline   → история изменений
Desk / Kanban        → работа пользователя
```

## Work Type

`Work Type` отвечает на простой вопрос: **что это за вид работы?**

В prototype используются два примера:

```text
TASK   → обычная задача
CHECK  → работа, требующая отдельного этапа Review
```

Поля:

```text
code   Data  required, stable identifier
title  Data  required, display name
```

Почему два поля:

- `code` — стабильная машинная ссылка, например `TASK`;
- `title` — понятное человеку название, которое можно переименовать без изменения машинной ссылки.

На стенде `Work Type` настраивается так:

```text
Autoname    = field:code
Title Field = title
```

Это даёт документу стабильное `name = code`, а человеку оставляет изменяемое отображаемое название.

## Work Item

`Work Item` — **конкретная единица управляемой работы**.

Например:

```text
Подготовить отчёт за смену
Проверить расхождение по путевому листу
Разобрать обращение пользователя
```

Для v0.1 достаточно:

```text
title      Data  required
work_type  Link  required -> Work Type
```

`Title Field` для `Work Item` — `title`.

Смысл полей:

- `title` — что именно нужно сделать;
- `work_type` — к какому виду работы относится запись.

Системные поля Frappe (`name`, `owner`, `creation`, `modified` и т. п.) отдельно не дублируются.

Поле состояния вручную в DocType не добавляется. При сохранении активного Workflow Frappe создаёт собственное Link-поле для Workflow State, если указанного поля ещё нет.

## State / Workflow

Отдельную систему состояний VEQTA в v0.1 не создаём.

Проверяется штатная связка:

```text
Work Item
    ↓
Frappe Workflow
    ↓
Frappe Workflow State
```

На одном `Work Item` проверяются два маршрута:

```text
TASK:  New → In Progress → Done
CHECK: New → In Progress → Review → Done
```

Ключевой вопрос стенда: может ли один Workflow корректно обслуживать оба `Work Type` через Transition Conditions.

## Assignment

Отдельного поля `responsible` или `assigned_to` в `Work Item` на v0.1 нет.

Назначение проверяется через штатный `Assign To`, который создаёт связанные `ToDo`.

Причина проверки: назначение уже является отдельным структурированным фактом Frappe, поэтому сначала нужно убедиться, что его достаточно и нет смысла хранить тот же факт второй раз в `Work Item`.

## State history

Для истории сначала проверяются штатные `Version`, Timeline и Workflow comments.

Нам нужно понять, можно ли из них надёжно получить:

```text
from_state
to_state
changed_by
changed_at
```

То есть не просто увидеть историю глазами в интерфейсе, а получить её в структурированном виде для последующего анализа.
