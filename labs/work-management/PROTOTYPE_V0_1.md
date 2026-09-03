# VEQTA — prototype v0.1

Цель: на живом Frappe проверить минимальную модель VEQTA и получить первый воспроизводимый код приложения.

Главное разделение:

```text
СОЗДАЁМ САМИ
├── Work Type
└── Work Item

НЕ СОЗДАЁМ, А ПРОВЕРЯЕМ У FRAPPE
├── Workflow / Workflow State
├── Assign To / ToDo
├── Version / Timeline / Workflow comments
├── Desk
└── Kanban
```

То есть объём предметной модели v0.1 — **два наших DocType**. Остальные шаги нужны только для ответа на вопрос: можно ли использовать готовые механизмы Frappe поверх этих двух DocType или какой-то из них имеет конкретное ограничение.

## Как вести испытание

Каждый этап заканчивается одним результатом:

```text
PASS — штатный механизм подходит для текущей модели
FAIL — зафиксировано конкретное воспроизводимое ограничение
```

В Issue #2 для каждого этапа записываются:

```text
Результат: PASS / FAIL
Что сделали:
Что получили:
Доказательство: имя записи / вывод команды / конкретное сообщение об ошибке
```

При `FAIL` в этом же шаге **не проектируется замена**. Сначала фиксируется факт.

---

## 0. Стенд

Поднять окружение строго по `START_HERE_WSL2.md`.

Зафиксировать в Issue #2:

```bash
cd ~/frappe/veqta-bench/apps/frappe
git describe --tags --always
git rev-parse HEAD
```

### PASS

- `veqta.localhost` открывается;
- app `veqta` установлен;
- Developer Mode включён;
- реальный scaffold `apps/veqta` уже запушен в `lazuale/veqta`.

Без PASS этого этапа дальше не идти.

---

## 1. Создать два DocType VEQTA

Это единственные собственные сущности prototype v0.1.

### 1.1 Work Type

В Desk открыть `DocType` и создать стандартный DocType `Work Type` в модуле приложения VEQTA.

Поля:

```text
code   Data  required
title  Data  required
```

Настройки DocType:

```text
Autoname    = field:code
Title Field = title
```

Создать две записи:

```text
code=TASK   title=Task
code=CHECK  title=Check
```

Ожидается:

```text
name TASK  → title Task
name CHECK → title Check
```

### 1.2 Work Item

Создать стандартный DocType `Work Item`.

Поля:

```text
title      Data  required
work_type  Link  required -> Work Type
```

Настройка:

```text
Title Field = title
```

**Не добавлять вручную** `workflow_state`, `responsible`, `assigned_to` или другие поля.

Создать две записи:

```text
TASK test   → work_type=TASK
CHECK test  → work_type=CHECK
```

После создания DocType проверить исходники:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

### PASS

- существуют только два собственных DocType VEQTA;
- `Work Item.work_type` хранит ссылку на `Work Type`;
- DocType metadata появились в `apps/veqta`;
- изменение `Work Type.title` не требует изменения `code`.

---

## 2. Workflow

### Зачем

Проверить, может ли **один штатный Workflow Frappe** управлять двумя типами `Work Item` с разными маршрутами.

### 2.1 Подготовить штатные записи Frappe

Создать Workflow State:

```text
New
In Progress
Review
Done
```

Для всех четырёх состояний:

```text
Doc Status = 0
Only Allow Edit For = System Manager
```

Создать Workflow Action Master:

```text
Start
Send to Review
Complete
```

### 2.2 Создать один Workflow

```text
Workflow Name        = Work Item Workflow
Document Type        = Work Item
Is Active            = 1
Workflow State Field = workflow_state
```

Transitions:

| From | Action | To | Allowed | Condition |
|---|---|---|---|---|
| New | Start | In Progress | System Manager | — |
| In Progress | Complete | Done | System Manager | `doc.work_type == "TASK"` |
| In Progress | Send to Review | Review | System Manager | `doc.work_type == "CHECK"` |
| Review | Complete | Done | System Manager | `doc.work_type == "CHECK"` |

После сохранения Workflow проверить `Work Item`: Frappe должен сам создать Link-поле `workflow_state`, если его не было.

### 2.3 Проверить TASK

Открыть `TASK test`.

Ожидаемый маршрут:

```text
New
↓ Start
In Progress
↓ Complete
Done
```

В `In Progress` действие `Send to Review` для TASK появляться не должно.

### 2.4 Проверить CHECK

Открыть `CHECK test`.

Ожидаемый маршрут:

```text
New
↓ Start
In Progress
↓ Send to Review
Review
↓ Complete
Done
```

В `In Progress` действие `Complete` для CHECK появляться не должно.

### 2.5 Проверить серверный запрет обхода

Создать ещё один `Work Item` типа `CHECK`, провести его штатным действием до `In Progress` и скопировать его `name`.

В Ubuntu:

```bash
cd ~/frappe/veqta-bench
bench --site veqta.localhost console
```

В console:

```python
doc = frappe.get_doc("Work Item", "<CHECK_NAME>")
doc.workflow_state = "Done"
doc.save()
```

Ожидается ошибка вида:

```text
Workflow State transition not allowed from In Progress to Done
```

После выхода из console документ должен остаться в `In Progress`.

### PASS

- TASK проходит только `New → In Progress → Done`;
- CHECK проходит только `New → In Progress → Review → Done`;
- лишние actions не предлагаются;
- прямой `doc.save()` не позволяет запрещённый переход.

### FAIL

Любой способ изменить состояние в обход разрешённых переходов или невозможность поддерживать оба типа одним понятным Workflow.

---

## 3. Assignment / ToDo

### Зачем

Понять, достаточно ли штатного Assignment, чтобы **не добавлять в Work Item своё поле ответственного**.

Если на чистом site есть только `Administrator`, создать через Desk одного временного тестового System User. Специальную модель пользователей VEQTA для этого не создавать.

Создать `Work Item`:

```text
Assignment test
work_type=TASK
```

### 3.1 Одно назначение

Через `Assign To` назначить документ на `Administrator`.

Открыть список `ToDo` и найти запись по:

```text
Reference Type = Work Item
Reference Name = <имя Assignment test>
```

Проверить:

```text
allocated_to
reference_type
reference_name
status
assigned_by
```

### 3.2 Два назначения

Тем же `Assign To` добавить второго пользователя.

Ожидается две открытые записи `ToDo`, обе с одной ссылкой на тот же `Work Item`.

### 3.3 Снять одно назначение

Убрать второго пользователя из назначенных.

Ожидается:

```text
ToDo второго пользователя → Cancelled
ToDo Administrator        → Open
```

Для машинной проверки можно выполнить:

```bash
cd ~/frappe/veqta-bench
bench --site veqta.localhost console
```

```python
frappe.get_all(
    "ToDo",
    filters={
        "reference_type": "Work Item",
        "reference_name": "<WORK_ITEM_NAME>",
    },
    fields=[
        "allocated_to",
        "reference_type",
        "reference_name",
        "status",
        "assigned_by",
    ],
    order_by="creation asc",
)
```

### PASS

- одно назначение = одна связанная `ToDo`;
- два назначения = две независимые `ToDo`;
- снятие одного не уничтожает второе;
- текущие назначения можно получить из структурированных `ToDo` без разбора `_assign`;
- своего `responsible` / `assigned_to` в `Work Item` не требуется для этих операций.

---

## 4. State history

### Зачем

Понять, даёт ли штатный audit Frappe машинно читаемую историю lifecycle, а не только красивую Timeline для человека.

Использовать `CHECK test`, который уже прошёл:

```text
New → In Progress → Review → Done
```

### 4.1 Проверить глазами

На форме `Work Item` открыть Timeline и убедиться, что переходы видны пользователю.

### 4.2 Проверить данные

В console:

```python
frappe.get_all(
    "Comment",
    filters={
        "reference_doctype": "Work Item",
        "reference_name": "<CHECK_NAME>",
        "comment_type": "Workflow",
    },
    fields=["content", "comment_by", "creation"],
    order_by="creation asc",
)
```

И отдельно:

```python
frappe.get_all(
    "Version",
    filters={
        "ref_doctype": "Work Item",
        "docname": "<CHECK_NAME>",
    },
    fields=["owner", "creation", "data"],
    order_by="creation asc",
)
```

Нужно ответить на один конкретный вопрос:

> Можно ли без разбора текста и без парсинга сериализованного audit получить отдельными структурированными полями `from_state`, `to_state`, `changed_by`, `changed_at` и рассчитать время в состоянии?

### PASS

Да — показать, из каких именно штатных полей это получается.

### FAIL

Нет — записать в Issue #2, чего именно не хватает. **Никакую замену на этом шаге не проектировать.**

---

## 5. Rename / integrity

### Зачем

Проверить, не ломаются ли уже созданные данные при изменении человекочитаемых названий.

### 5.1 Work Type title

Изменить:

```text
TASK.title: Task → Task renamed
```

Проверить существующий `Work Item` типа TASK.

Ожидается:

```text
work_type продолжает ссылаться на name=TASK
```

После проверки вернуть `title=Task`.

### 5.2 Workflow State

После завершения остальных workflow-тестов переименовать `Review` штатным Rename в `Review Renamed`.

Проверить:

- ссылки в Workflow;
- существующий `Work Item`, если он находится в этом State;
- Timeline / Version.

После фиксации результата вернуть название `Review`.

### PASS / FAIL

Записать фактическое поведение ссылок и истории. Здесь не предполагается заранее, что State rename обязательно безопасен.

---

## 6. Kanban

### Зачем

Проверить, не становится ли drag-and-drop обходным способом менять `workflow_state` мимо правил Workflow.

Создать Kanban Board для:

```text
Reference DocType = Work Item
Field             = workflow_state
```

Если Frappe не создаст колонки состояний автоматически, вручную добавить:

```text
New
In Progress
Review
Done
```

Сам факт необходимости ручных колонок записать в Issue #2, но не считать ошибкой сам по себе.

### 6.1 Запрещённый drag-and-drop

Создать новый CHECK и штатным Workflow довести до `In Progress`.

Попытаться перетащить карточку сразу:

```text
In Progress → Done
```

### PASS

- перенос отвергнут;
- `workflow_state` остаётся `In Progress`;
- данные и история не повреждены.

### FAIL

Карточка реально получает `Done` в обход разрешённого маршрута.

### 6.2 Разрешённый drag-and-drop

Попытаться:

```text
In Progress → Review
```

Проверить:

- изменилось ли состояние;
- не появилась ли ошибка;
- что записалось в Timeline / Version / Workflow comments.

Записать фактическое отличие drag-and-drop от обычного Workflow action, если оно есть.

---

## 7. Desk

Отдельного большого теста Desk нет: он уже используется во всех предыдущих шагах.

В процессе достаточно подтвердить, что для `Work Item` нормально работают:

```text
Form
List
filters
Assign To
Timeline
Kanban
```

Если базовая операция требует собственного UI уже на этих двух DocType — это фиксируется как конкретное ограничение.

---

## 8. Git / reproducibility

### Зачем

Доказать, что VEQTA существует не только в БД текущего стенда.

После каждого принятого изменения:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

Стандартные DocType должны появляться в исходном дереве приложения благодаря Developer Mode.

Для принятой конфигурации, которая остаётся только в БД, сначала определить **какие именно штатные записи Frappe требуется экспортировать**, затем использовать официальный механизм fixtures/export. Не создавать exporter VEQTA.

Тестовые `Work Type`, `Work Item` и временные User не коммитятся как production data только ради прохождения испытаний.

После фиксации принятой конфигурации в Git создать контрольный чистый site:

```bash
cd ~/frappe/veqta-bench
bench new-site veqta-restore.localhost --db-type mariadb
bench --site veqta-restore.localhost install-app veqta
bench --site veqta-restore.localhost migrate
```

Проверить, что без повторного ручного создания продуктовой конфигурации восстановлены все **принятые** части v0.1.

### PASS

```text
чистый site
+ repository VEQTA
+ install-app / migrate
= принятое состояние VEQTA
```

### FAIL

Что-либо принято как часть продукта, но существует только на исходном dev-site и требует повторного ручного накликивания.

---

## Когда prototype v0.1 закончен

В Issue #2 должны быть результаты:

```text
0 Stand                PASS
1 Two VEQTA DocTypes   PASS / FAIL
2 Workflow             PASS / FAIL
3 Assignment / ToDo    PASS / FAIL
4 State history        PASS / FAIL
5 Rename / integrity   PASS / FAIL
6 Kanban               PASS / FAIL
7 Desk                 PASS / FAIL
8 Reproducibility      PASS / FAIL
```

После этого `MODEL_V0_1.md` и `DECISIONS.md` обновляются **только фактическими выводами стенда**.
