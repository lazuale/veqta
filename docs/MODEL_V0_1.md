# VEQTA — модель v0.1

Статус: **рабочая гипотеза для prototype v0.1, не стабильный контракт**.

Цель документа — в одном месте зафиксировать минимальную предметную модель, которую должен проверить живой стенд Frappe.

## 1. Work Item

`Work Item` — единица управляемой работы.

Минимальный кандидат:

```text
Work Item
---------
title          required
work_type      required
workflow_state required / managed by Frappe Workflow

description    optional
due_at          optional
```

Системные поля Frappe (`name`, `owner`, `creation`, `modified`, `modified_by`) не дублируются без отдельного бизнес-смысла.

`Work Item` хранит текущее состояние работы. Он не должен одновременно быть журналом истории, отчётом и универсальным контейнером предметных данных.

## 2. Work Type

`Work Type` — собственный master DocType VEQTA для классификации разных видов работы без создания отдельного DocType на каждый сценарий.

Кандидатная модель prototype:

```text
Work Type
---------
code            required, stable machine identifier
title           required, user-facing name
description     optional
disabled        optional
```

Предполагается проверить:

- `code` как стабильный идентификатор/name;
- `title` как отображаемое название;
- переименование `title` без нарушения ссылок существующих Work Item;
- отказ от удаления исторически использованных типов в пользу `disabled`, если это оправдано практикой.

Поля и naming rule пока не считаются замороженным публичным API.

## 3. State

Отдельный `Work State` VEQTA в prototype не создаётся.

Сначала проверяется штатная модель:

```text
Work Item
    ↓
Frappe Workflow
    ↓
Frappe Workflow State
```

Frappe создаёт workflow-state поле целевого DocType и управляет допустимыми transitions.

Гипотеза: один Workflow `Work Item` может обслуживать разные Work Type через Transition Conditions по `work_type`.

Если реальный тест это подтверждает, VEQTA не создаёт собственный lifecycle engine.

## 4. Assignment

В prototype `Work Item` не получает `responsible` или `assigned_to`.

Сначала используется штатный Frappe `Assign To`, который создаёт структурированные `ToDo` со связью на исходный документ.

Проверяется, достаточно ли этого механизма для:

- одного назначенного;
- нескольких назначенных;
- «назначено мне»;
- получения текущих назначений через Report/API/SQL;
- снятия одного assignment без нарушения остальных.

`_assign` не рассматривается как аналитический источник; предмет проверки — связанные записи `ToDo`.

Если VEQTA позднее действительно понадобится ровно один accountable owner, это будет отдельное требование, а не предположение ядра.

## 5. История State

Сначала используется только штатный audit Frappe: Workflow comments, Timeline и Version.

Прототип должен ответить, можно ли без парсинга текста/serialized audit надёжно получить:

```text
work_item
from_state
to_state
changed_by
changed_at
```

Если нет, минимальный кандидат на собственный бизнес-факт:

```text
Work State Change
-----------------
work_item
from_state
to_state
changed_by
changed_at
```

Он допускается только после подтверждения необходимости и не превращается в Event Store/Event Sourcing.

## 6. Due date

`due_at` необязателен. VEQTA не должна требовать искусственный deadline для каждой работы.

Производные признаки вроде `is_overdue`, `age_days`, `days_open`, `cycle_time` не хранятся как первичные факты без отдельной необходимости.

## 7. Что сознательно отсутствует в v0.1

До доказанной необходимости не добавляются:

- `responsible` / `assigned_to` в Work Item;
- Priority как обязательная семантика Core;
- Workstream/Context;
- Outcome;
- Project/Sprint/Epic;
- SLA;
- Handoff;
- Approval subsystem;
- Dependencies;
- Parent/Child hierarchy;
- Recurrence;
- Team Ownership/RACI;
- универсальный Event Bus/Event Store;
- аналитические агрегаты в OLTP-модели.

## 8. Инварианты, которые уже считаются принципами

1. Один бизнес-факт — один источник истины.
2. Ключевые данные структурированы, а не спрятаны в произвольном JSON/тексте.
3. Производные показатели вычисляются из первичных фактов.
4. Новая сущность Core появляется только после доказанной универсальной необходимости.
5. Если штатный Frappe корректно решает задачу, VEQTA не создаёт второй механизм.

## 9. Что должен решить prototype v0.1

После живого теста должны быть закрыты вопросы:

- финальный минимальный набор полей Work Item;
- достаточность Work Type-модели;
- пригодность одного Frappe Workflow для разных типов работы;
- пригодность штатного Assignment/ToDo;
- необходимость структурированной State history;
- совместимость Workflow State с List/Kanban;
- поведение rename и целостность ссылок.

До этого документ остаётся рабочей гипотезой.
