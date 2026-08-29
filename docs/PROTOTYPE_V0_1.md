# VEQTA — prototype v0.1

Статус: **следующий практический этап проверки архитектуры**.

Цель прототипа — не получить полноценный продукт, а проверить минимальную модель VEQTA на актуальном стабильном Frappe без создания собственного framework поверх Framework.

## 1. Technical baseline

На дату подготовки: 2026-08-29.

Целевая линия Frappe:

- `version-16`;
- последняя проверенная стабильная версия: `v16.32.0`.

Перед фактическим развёртыванием версия проверяется повторно согласно `FRAPPE_BASELINE.md`.

Проверенные официальные исходники Frappe v16, влияющие на прототип:

- `frappe/model/workflow.py` — выбор активного Workflow, Conditions, применение transitions;
- `frappe/workflow/doctype/workflow/workflow.py` — один активный Workflow на DocType и автоматическое создание workflow-state поля;
- `frappe/workflow/doctype/workflow_state/workflow_state.json` — структура штатного Workflow State;
- `frappe/desk/form/assign_to.py` — Assignment/ToDo backend;
- `frappe/public/js/frappe/form/sidebar/assign_to.js` — стандартный Desk UI Assign To;
- `frappe/desk/doctype/todo/todo.json` — реляционная модель ToDo.

## 2. Принцип прототипа

Сначала используется только штатная конфигурация Frappe.

Собственный код добавляется только если конкретный тест показывает, что без него нельзя сохранить обязательное свойство VEQTA.

Прототип не должен заранее содержать:

- собственный workflow engine;
- собственный assignment engine;
- собственный form builder;
- собственный permission engine;
- SLA;
- Handoff;
- Workstream;
- Project/Sprint;
- универсальный Event Store.

## 3. Минимальные сущности VEQTA

### Work Type

Кандидат:

```text
code          required
label         required
description   optional
disabled      optional
```

Для прототипа создаются два типа:

```text
TASK   — Простая задача
CHECK  — Проверка
```

Задача теста: подтвердить, что один `Work Item` нормально обслуживает разные процессы через `work_type`.

### Work Item

Минимальный кандидат:

```text
title          required
work_type      required
workflow state required / managed by Frappe Workflow

description    optional
due_at          optional
```

Поля назначения пользователя в Work Item на первом проходе не создаются.

Assignment проверяется штатным Frappe `Assign To` / `ToDo`.

## 4. Workflow test

Используется **один штатный Workflow Frappe** для `Work Item`.

Workflow State:

```text
New
In Progress
Review
Done
```

### Work Type TASK

```text
New
  └─ Start → In Progress

In Progress
  └─ Complete → Done
```

Transition Conditions:

```python
doc.work_type == "TASK"
```

### Work Type CHECK

```text
New
  └─ Start → In Progress

In Progress
  └─ Send to Review → Review

Review
  └─ Complete → Done
```

Transition Conditions:

```python
doc.work_type == "CHECK"
```

## 5. Что должен доказать Workflow test

1. На одном DocType одновременно живут разные процессы по Work Type.
2. Пользователь видит только допустимые действия для своего Work Item.
3. Нельзя сохранить недопустимый переход обычным редактированием workflow-state поля.
4. Kanban/List корректно работают по общему state-полю.
5. Workflow остаётся понятным администратору в Desk.
6. Различия процессов задаются конфигурацией, а не кодом VEQTA.

Если этот тест проходит — свой lifecycle engine не создаётся.

Если не проходит — фиксируется конкретное ограничение Frappe и ищется минимальное расширение.

## 6. Assignment test

Не создавать `responsible` и `assigned_to` на Work Item.

Через штатный Desk `Assign To` проверить:

### Case A — один назначенный

- назначить User A;
- убедиться, что создан открытый `ToDo`;
- проверить `allocated_to`, `reference_type`, `reference_name`, `assigned_by`;
- проверить UI Work Item и уведомление;
- закрыть assignment.

### Case B — несколько назначенных

- назначить User A и User B;
- убедиться, что существуют две отдельные открытые записи `ToDo`;
- проверить штатный UI списка назначенных;
- закрыть только назначение User A;
- убедиться, что назначение User B продолжает существовать.

### Case C — аналитический доступ

Проверить возможность штатно получить:

- все Work Item, назначенные User A;
- всех текущих назначенных для конкретного Work Item;
- открытые и закрытые назначения;
- дату создания assignment;
- назначившего пользователя.

Если `ToDo` достаточен — VEQTA не дублирует assignment в своей модели.

Если продукту позднее потребуется именно один `accountable owner`, это рассматривается отдельным требованием, а не выводится автоматически из Assignment Frappe.

## 7. State history test — этап A без собственного кода

Провести несколько transitions и проверить:

- `Version`;
- Timeline;
- Workflow comments;
- workflow-state field Work Item.

Ответить на вопросы:

1. можно ли однозначно получить последовательность переходов;
2. можно ли надёжно получить `from_state`, `to_state`, `changed_by`, `changed_at`;
3. можно ли считать время в состоянии без парсинга сериализованного audit data или текста комментариев.

Ожидаемая гипотеза: для пользовательского audit trail штатных механизмов достаточно, для аналитической истории lifecycle — нет.

Но это должно быть подтверждено прототипом.

## 8. State history test — этап B только при подтверждённой необходимости

Если этап A подтверждает недостаточность технического audit для аналитики, добавить **минимальный** VEQTA DocType:

```text
Work State Change
-----------------
work_item
from_state
to_state
changed_by
changed_at
```

И минимальный server-side hook, который создаёт эту запись только при фактическом изменении workflow-state.

Требования:

- запись структурирована;
- никаких JSON payload;
- никакого универсального Event Bus;
- никакого Event Sourcing;
- Work Item продолжает хранить текущее состояние напрямую;
- событие создаётся в той же транзакции изменения документа.

## 9. Rename / data integrity test

Проверить штатное поведение Frappe при изменении пользовательских названий:

### Work Type

- изменить `label` без изменения стабильного `code`;
- убедиться, что существующие Work Item не меняют классификацию.

### Workflow State

- проверить допустимое штатное переименование Workflow State;
- проверить, как обновляются ссылки в существующих Work Item;
- проверить влияние на Workflow и историю;
- определить, нужен ли VEQTA стабильный машинный code для State или штатной модели Frappe достаточно.

До этого теста собственный `Work State` не создаётся.

## 10. UI test

Минимально проверить штатный Desk:

- создание Work Item;
- Quick Entry, если применимо;
- Form View;
- List View;
- Kanban по workflow-state;
- стандартные filters;
- Assign To;
- Timeline.

Задача не в дизайне final UI, а в проверке принципа:

> **можно ли получить рабочий VEQTA v0.1 в основном настройкой штатного Desk.**

## 11. Критерии успеха прототипа

Prototype v0.1 успешен, если:

1. два Work Type используют разные lifecycle без собственного workflow engine;
2. Work Item остаётся одним универсальным DocType;
3. стандартный Assignment Frappe не требует дублирования факта назначения;
4. обычная эксплуатация возможна через штатный Desk;
5. данные остаются структурированными;
6. для аналитики не требуется парсить произвольный текст;
7. объём необходимого собственного кода VEQTA точно известен и минимален.

## 12. Что будет решено после прототипа

После практической проверки можно закрыть следующие вопросы `DECISIONS.md`:

- Q-001 — минимальный состав Work Item;
- Q-002 — State и Frappe Workflow;
- Q-003 — структурированная State history;
- Q-006 — Assignment / ответственность;
- Q-007 — Work Type.

Только после этого проектируется следующая функциональность.
