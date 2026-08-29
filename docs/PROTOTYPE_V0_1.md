# VEQTA — prototype v0.1

Цель: проверить модель из `MODEL_V0_1.md` на живом Frappe и зафиксировать рабочий код приложения в Git.

## 1. Стенд

- использовать baseline из `DEVELOPMENT.md`;
- зафиксировать Frappe tag и commit SHA в Issue #1;
- создать и запушить реальный app scaffold `veqta`;
- установить app на `veqta.localhost` и включить Developer Mode.

## 2. Модель

Создать стандартные DocType:

### Work Type

```text
code          Data        required
title         Data        required
description   Small Text  optional
disabled      Check       optional
```

Тестовые записи:

```text
TASK   / Task
CHECK  / Check
```

### Work Item

```text
title         Data        required
work_type     Link        required -> Work Type
description   Text Editor optional
due_at        Datetime    optional
```

State должен добавляться/управляться штатным Workflow.

## 3. Workflow

Один Workflow для `Work Item`.

```text
TASK:  New → In Progress → Done
CHECK: New → In Progress → Review → Done
```

Все состояния prototype: `Doc Status = 0`.

Разветвление — через Transition Conditions по `work_type`.

Проверить:

- доступные actions соответствуют `Work Type`;
- запрещённый transition блокируется серверно;
- save/API не обходят Workflow;
- конфигурация остаётся поддерживаемой в Desk.

## 4. Assignment

Через штатный `Assign To` проверить:

- одного назначенного;
- двух назначенных;
- снятие одного из двух;
- связанные `ToDo`;
- «назначено мне»;
- получение текущих назначений без разбора `_assign`.

## 5. State history

После нескольких transitions проверить `Version`, Timeline и Workflow comments.

Нужно определить, можно ли структурированно получить:

```text
from_state
to_state
changed_by
changed_at
```

и считать время в состоянии. Если нет — испытать минимальный `Work State Change`.

## 6. Integrity / Kanban

Проверить:

- rename `Work Type.title` при стабильном `code`;
- rename Workflow State и целостность ссылок;
- Kanban по workflow-state;
- drag-and-drop против Workflow rules;
- корректность истории после drag-and-drop.

## 7. Git / reproducibility

После каждого принятого изменения:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

Продуктовая конфигурация должна попасть в app как файлы или штатный экспорт. Тестовые записи стенда не коммитятся без отдельной причины.

Финальная проверка:

```text
чистый Frappe site
+ repository VEQTA
+ install-app / migrate
= принятая конфигурация без ручного повторного накликивания
```

## Результат

Фактические результаты записываются в Issue #1. После этого обновляются `MODEL_V0_1.md` и `DECISIONS.md`.
