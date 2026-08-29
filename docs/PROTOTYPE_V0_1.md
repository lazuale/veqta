# VEQTA — prototype v0.1

Статус: **текущий практический этап проекта**.

Цель — проверить минимальную модель VEQTA на живом актуальном Frappe и получить первый реальный код приложения без преждевременных собственных подсистем.

Модель, которую проверяем: `MODEL_V0_1.md`.

Правила разработки: `DEVELOPMENT.md`.

## 1. Baseline

Перед началом стенда повторно проверить актуальный stable Frappe согласно `DEVELOPMENT.md` и зафиксировать точный tag/commit в Issue #1.

На дату подготовки документа (2026-08-29) последняя проверенная версия линии v16 — `v16.32.0`.

## 2. Что должно существовать в коде prototype

### Work Type

Стандартный DocType приложения VEQTA:

```text
code          Data        required, unique candidate
title         Data        required
description   Small Text  optional
disabled      Check       optional
```

Prototype records:

```text
TASK   / Task
CHECK  / Check
```

### Work Item

Стандартный DocType приложения VEQTA:

```text
title         Data        required
work_type     Link        required -> Work Type
description   Text Editor optional
due_at        Datetime    optional
```

Не добавлять на первом проходе `responsible`, `assigned_to`, Workstream, Outcome, Priority, SLA, Handoff и другие неподтверждённые поля.

Текущее State сначала предоставляет Frappe Workflow.

## 3. Workflow experiment

Создать **один штатный Workflow** для `Work Item`.

States:

```text
New
In Progress
Review
Done
```

Все состояния prototype оставить `Doc Status = 0`, чтобы не смешивать lifecycle test с submit/cancel semantics.

Проверяем два процесса.

### TASK

```text
New → In Progress → Done
```

### CHECK

```text
New → In Progress → Review → Done
```

Различия ограничить Transition Conditions по `work_type`.

Проверить:

- пользователь видит только допустимые actions;
- недопустимый transition блокируется серверно;
- обычный save/API не обходят Workflow;
- конфигурация остаётся понятной в Desk;
- один Workflow не превращается в неприемлемую кашу уже на двух типах.

Если эксперимент проходит, собственный lifecycle engine не создаётся.

## 4. Assignment experiment

Не создавать отдельное поле ответственного.

Штатным `Assign To` проверить:

1. одного назначенного;
2. двух назначенных;
3. снятие одного assignment при сохранении второго;
4. связанные `ToDo` и поля `allocated_to`, `reference_type`, `reference_name`, `status`, `assigned_by`;
5. «назначено мне»;
6. получение текущих назначений через штатный Report/API/SQL без разбора `_assign`.

После теста решить, достаточно ли Frappe Assignment или продукту действительно нужен отдельный accountable owner.

## 5. State history experiment

### Этап A — только Frappe

Выполнить реальные transitions и проверить:

- Timeline;
- Workflow comments;
- Version;
- возможность структурированно получить `from_state`, `to_state`, `changed_by`, `changed_at`;
- расчёт времени в State без парсинга текста/serialized audit.

### Этап B — только при подтверждённой недостаточности

Добавить минимальный DocType `Work State Change` и минимальный server-side hook.

Не создавать Event Store/Event Bus/Event Sourcing.

## 6. Rename / integrity experiment

Проверить:

- изменение `Work Type.title` при стабильном `code`;
- сохранность ссылок существующих Work Item;
- штатное переименование Workflow State;
- влияние rename на Work Item, Workflow и историю;
- нужна ли VEQTA собственная стабильная машинная семантика State.

## 7. Kanban experiment

Kanban не считается заранее решённой частью архитектуры.

Проверить:

- можно ли создать корректный board по workflow-state field;
- нужно ли вручную создавать columns;
- проходит ли drag-and-drop через Workflow validation;
- нельзя ли drag-and-drop выполнить запрещённый transition;
- остаётся ли история переходов корректной.

При несовместимости сначала фиксируется конкретное ограничение Frappe; новый framework не создаётся автоматически.

## 8. Click → Git / reproducibility experiment

Каждый согласованный объект, созданный через Desk, должен попасть в `apps/veqta` как исходник или штатно экспортированная продуктовая конфигурация.

После каждого этапа:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

Prototype не считается завершённым, пока не пройден контрольный тест:

```text
новый чистый site
+ текущий repository VEQTA
+ install-app / migrate
= Work Type + Work Item + принятая продуктовая конфигурация без повторного ручного накликивания
```

Тестовые записи `TASK`, `CHECK` и Work Item не обязаны быть частью production fixtures, если они нужны только для испытания. В Git должна попасть **модель и продуктовая конфигурация**, а не мусорные данные стенда.

## 9. UI sanity check

Минимально проверить штатный Desk:

- Form;
- List;
- filters;
- Assign To;
- Timeline;
- Kanban как отдельный compatibility test.

Цель — не финальный дизайн, а проверка возможности получить рабочий v0.1 преимущественно штатным Frappe.

## 10. Результат prototype

Prototype завершается только фактическим отчётом в Issue #1 и обновлением `DECISIONS.md`.

Должны быть закрыты или переформулированы вопросы:

- Work Item;
- Work Type;
- State / Workflow;
- Assignment;
- State history;
- Kanban;
- rename/integrity;
- reproducibility из Git.

До этого новые Core-сущности не проектируются.
