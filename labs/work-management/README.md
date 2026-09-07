# Управление работой

Управление работой — прототип управления операционной работой на Frappe Framework в рамках VEQTA Labs.

Lab проверяет, насколько далеко можно зайти на штатных механизмах Frappe, не создавая параллельную систему задач.

Базовый порядок:

```text
требование
→ ответственность
→ штатный механизм Frappe
→ проверка семантики
→ официальный extension point
→ собственный код только для недостающего поведения
```

## Как устроен Lab

Прототип собирается на отдельном development Site как минимальный standard Frappe App:

```text
App package: veqta_work_management
App / Module: VEQTA Work Management
DocType: Work Item
Role: VEQTA Work User
```

App здесь не Product. Он нужен для штатной разработки Frappe и воспроизводимой поставки metadata на другой Site. Обычная работа пользователя не должна зависеть от `developer_mode`.

Документы Lab:

- [Модель данных v1](data-model-v1.md) — `Work Item` и границы модели;
- [Безопасность v1](security-v1.md) — Role, DocPerm и штатная семантика `ToDo`;
- [Конфигурация v1](configuration-v1.md) — List, Kanban, Number Cards, Chart и Workspace;
- [Руководство по настройке](setup-guide.md) — сборка App;
- [Руководство по проверке](live-test-guide.md) — проверка поведения и воспроизводимой поставки.

## Ядро модели

```text
Work Item
├── subject
├── description
├── status
├── priority
├── due_date
└── links → Dynamic Link
```

Технические состояния:

```text
Open
Waiting
Closed
Cancelled
```

`Work Item.status` описывает состояние самой работы. Персональная ответственность хранится отдельно штатным `Assign To / ToDo`.

```text
Work Item.status = состояние работы
Assign To / ToDo = персональное назначение
```

Эти две оси не синхронизируются собственным кодом Lab. Закрытие `ToDo` не закрывает Work Item; изменение `Work Item.status` само по себе не изменяет связанные `ToDo`. Если живой прототип покажет, что здесь нужен отдельный бизнес-инвариант, он будет проектироваться как самостоятельное требование.

Отдельного `In Progress` нет: `Open` с активным назначением уже означает, что работа взята исполнителем. `Waiting` используется, когда работа остаётся актуальной, но продолжение зависит от внешнего события.

## Идентификаторы и русский интерфейс

Технические идентификаторы не зависят от языка интерфейса:

```text
DocType: Work Item
Work Item name: WI-00001, WI-00002, ...
fieldnames: subject, description, status, priority, due_date, links
status: Open, Waiting, Closed, Cancelled
priority: Low, Medium, High
```

Русская локализация App поставляется через Gettext `locale/*.po`. Пользовательским названием документа остаётся `subject`.

## Что предоставляет Frappe

| Ответственность | Механизм |
| --- | --- |
| персональные назначения | `Assign To` / `ToDo` |
| комментарии и история | Timeline / Comments |
| файлы | Attachments |
| свободная классификация | Tags |
| письма | `Communication` |
| связи с другими документами | `Dynamic Link` |
| повторение | `Auto Repeat` |
| автоматическое распределение при необходимости | `Assignment Rule` |
| очередь | List View |
| состояние потока | Kanban |
| простая аналитика Work Item | Report Builder |
| показатели | Number Card / Dashboard Chart |
| единая точка входа | Workspace |
| авторизация | Role / DocPerm |
| локализация App | Gettext |

Baseline не добавляет собственный API, scheduler, service/repository layer, frontend, permission model или lifecycle-синхронизацию поверх `ToDo`.

## Сроки

```text
Work Item.due_date = общий срок работы
ToDo.date          = Complete By конкретного назначения
```

Это разные данные и они не синхронизируются автоматически.

Calendar/Gantt не входят в baseline: текущая модель содержит одну точку `due_date`, а стандартные представления Frappe работают с интервалом `start/end`. Фиктивные `start_date`, `end_date` и `progress` ради UI не добавляются.

## Что намеренно отсутствует

```text
Work Unit
Work Type
Work Source
Work Reference
Work Dependency
assignee
responsible_unit
parent_work_item
started_at
closed_at
closed_by
waiting_reason
waiting_since
planned_start
estimated_effort
SLA
progress
start_date
end_date
```

Новый элемент появляется только при самостоятельной ответственности, которую нельзя корректно выразить текущей моделью или штатным механизмом Frappe.

## Границы baseline

- DocPerm описывает доверенную общую очередь; правило «редактировать может только assignee» не заявляется.
- `Assign To` и `Work Item.status` остаются независимыми штатными механизмами.
- Фильтрация и аналитика по внутреннему `_assign` не становятся App-контрактом без live-проверки конкретной версии.
- Общая аналитика по исполнителям не строится выдачей широкого `Read` на все `ToDo` Site.
- Auto Repeat не вычисляет относительный `due_date` без отдельного правила; при появлении такого требования сначала проверяется `Work Item.on_recurring`.

## Версия Frappe

Текущий проверочный ориентир — Frappe v16.33.0. Версионно-зависимые детали перепроверяются на используемом patch-release.

Основные источники:

- [Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Create an App](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`ToDo`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Gettext commands`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)
