# Управление работой

Управление работой — прототип управления операционной работой на Frappe Framework в рамках VEQTA Labs.

Lab проверяет, насколько далеко можно зайти на штатной модели Frappe, не создавая параллельную систему задач. Базовый порядок тот же, что и для других решений VEQTA:

```text
требование
→ ответственность
→ штатный механизм Frappe
→ проверка семантики
→ официальный extension point
→ собственный код только для недостающего поведения
```

## Как устроен Lab

Живой прототип собирается на отдельном development Site как минимальный standard Frappe App:

```text
App package: veqta_work_management
App / Module: VEQTA Work Management
DocType: Work Item
Role: VEQTA Work User
```

App здесь не является отдельным Product. Он нужен как штатная единица разработки Frappe: standard metadata и код должны воспроизводимо устанавливаться на другой Site, а пользовательская работа не должна зависеть от `developer_mode`.

Документы Lab разделены по ответственности:

- [Модель данных v1](data-model-v1.md) — `Work Item` и его lifecycle;
- [Безопасность v1](security-v1.md) — Role, DocPerm и границы `ToDo`;
- [Конфигурация v1](configuration-v1.md) — List, Kanban, Number Cards, Chart и Workspace;
- [Руководство по настройке](setup-guide.md) — сборка App на development Site;
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

`status` описывает состояние самой работы. Персональная ответственность хранится отдельно штатным `Assign To / ToDo`:

```text
Work Item.status = состояние работы
Assign To / ToDo = персональное назначение
```

Поэтому отдельного состояния `In Progress` нет. `Open` с активным назначением означает, что работа уже взята исполнителем. `Waiting` означает, что работа остаётся актуальной, но продолжение зависит от внешнего события.

`Closed` и `Cancelled` являются терминальными состояниями. При переходе Work Item в `Closed` активные назначения закрываются; при переходе в `Cancelled` — отменяются. Новое назначение на терминальный Work Item не допускается серверным контрактом App. Обратной автоматизации нет: закрытие одного `ToDo` само по себе не закрывает Work Item, потому что у документа может быть несколько исполнителей.

## Идентификаторы и русский интерфейс

Технические идентификаторы остаются стабильными и не зависят от языка интерфейса:

```text
DocType: Work Item
Work Item name: VWM-WI-00001, VWM-WI-00002, ...
fieldnames: subject, description, status, priority, due_date, links
status: Open, Waiting, Closed, Cancelled
priority: Low, Medium, High
```

Русские подписи поставляются App через `translations/ru.csv`. Пользователь видит `Работа`, `Открыто`, `Ожидание`, `Закрыто`, `Отменено`, но в данных остаются исходные технические значения.

Префикс имени Work Item нужен не для интерфейса, а для устойчивой идентификации документа в ссылках, логах и интеграциях. Пользовательским названием документа остаётся `subject`.

## Что предоставляет Frappe

| Ответственность | Механизм |
| --- | --- |
| персональные назначения | `Assign To` / `ToDo` |
| комментарии и история обсуждения | Timeline / Comments |
| файлы | Attachments |
| свободная классификация | Tags |
| письма | `Communication` |
| связи с другими документами | `Dynamic Link` |
| повторение | `Auto Repeat` |
| автоматическое распределение при реальной необходимости | `Assignment Rule` |
| очередь | List View |
| состояние потока | Kanban |
| простая аналитика Work Item | Report Builder |
| показатели | Number Card / Dashboard Chart |
| единая точка входа | Workspace |
| авторизация | Role / DocPerm |
| локализация App | `translations/*.csv` |

Собственный код baseline ограничен контрактом самого `Work Item`: терминальные состояния должны согласованно завершать активные назначения и не позволять создавать новые назначения на завершённую или отменённую работу. Для отображения состояния List View использует штатный `<doctype>_list.js` extension point.

## Сроки

`due_date` — одна дата срока всей работы:

```text
Work Item.due_date = общий срок работы
ToDo.date          = Complete By конкретного назначения
```

Эти поля не синхронизируются автоматически: у них разная ответственность.

Calendar/Gantt не входят в baseline. Стандартный Calendar Frappe моделирует start/end и позволяет изменять их через интерфейс, а текущий Work Item имеет только одну точку `due_date`. Добавлять фиктивные `start_date`, `end_date` или `progress` только ради представления нельзя. Если в предметной модели появится реальный плановый интервал, Calendar/Gantt проектируются заново уже из этой ответственности.

## Что намеренно отсутствует

В текущем ядре нет:

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

Не создаются также собственные API, scheduler, service/repository layers, frontend или отдельная модель членства. Новый элемент появляется только при самостоятельной ответственности, которую нельзя корректно выразить уже существующей моделью или штатным механизмом Frappe.

## Границы baseline

- DocPerm описывает доверенную общую очередь; правило «редактировать может только assignee» не заявляется.
- `Assign To` показывает enabled System Users, а право открыть Work Item определяется отдельно; назначение пользователя без доступа должно завершаться штатной проверкой permissions, а не расширением `Share` для участников очереди.
- Фильтрация и аналитика по внутреннему `_assign` не считаются обязательным App-контрактом без проверки на конкретной версии Frappe.
- Общая аналитика по исполнителям не должна строиться выдачей широкого `Read` на все `ToDo` Site. Если она станет обязательной, нужен отдельный permission-aware App report, явно ограниченный `reference_type = Work Item`.
- Auto Repeat не вычисляет относительный `due_date` без отдельного правила. При появлении такого требования первым рассматривается `Work Item.on_recurring`, а не собственный scheduler.

## Версия Frappe

Текущий проверочный ориентир — Frappe v16.33.0. Версионно-зависимые детали перепроверяются на используемом patch-release.

Основные источники:

- [Frappe Apps](https://docs.frappe.io/framework/user/en/guides/basics/apps)
- [Create an App](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Translations](https://docs.frappe.io/framework/user/en/translations)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`ToDo`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Workspace`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)