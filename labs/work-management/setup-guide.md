# Управление работой v1: сборка на Frappe v16

Этот гайд собирает Work Management Lab как минимальный standard Frappe App и проверяет воспроизводимую поставку обязательного состояния.

Перед началом:

- [Модель данных v1](data-model-v1.md);
- [Безопасность v1](security-v1.md);
- [Конфигурация v1](configuration-v1.md).

## 0. Development Site

Работайте на отдельном тестовом Site без пользовательских данных.

Включите Developer Mode только для этого Site:

```bash
bench --site <site> set-config developer_mode 1
bench --site <site> clear-cache
bench --site <site> show-config
```

Не используйте глобальный `-g developer_mode 1`, если нет причины включать режим для всех Sites bench.

## 1. Создайте App штатным Bench

```bash
bench new-app veqta_work_management
```

Используйте:

```text
App Title: VEQTA Work Management
App Description: Work Management prototype for VEQTA Labs
App Publisher: VEQTA
App License: MIT
```

Не создавайте App-каркас вручную. Эталонная структура — результат `bench new-app` используемой версии Bench/Frappe.

Установите App:

```bash
bench --site <site> install-app veqta_work_management
bench --site <site> list-apps
```

## 2. Создайте роль `VEQTA Work User`

```text
Role Name: VEQTA Work User
Desk Access: Yes
```

Роль будет указана в permissions standard `Work Item`. Отдельный fixture роли не добавляется: при импорте standard DocType Frappe создаёт отсутствующие Role из permission rows. Это всё равно проверяется reinstall-test на чистом Site.

## 3. Создайте standard DocType `Work Item`

```text
Name: Work Item
Module: VEQTA Work Management
Custom: No

Naming Rule: Expression
Auto Name: WI-.#####
Title Field: subject
Show Title Field in Link: Yes
Search Fields: subject
Allow Rename: No

Is Submittable: No
Is Single: No
Is Tree: No

Quick Entry: Yes
Track Changes: Yes
Track Seen: No
Track Views: No

Allow Auto Repeat: Yes

Default View: List
Is Calendar and Gantt: No
Force Re-route to Default View: No

Sort Field: creation
Sort Order: DESC
```

Ключевая проверка: это standard DocType App, а не site-level Custom DocType.

### Поля

| Label | Fieldname | Type | Required | Default | No Copy | List | Standard Filter | Global Search | Quick Entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Subject | `subject` | Data | yes | — | no | title | no | yes | yes |
| Description | `description` | Text Editor | no | — | no | no | no | yes | yes |
| Status | `status` | Select | yes | `Open` | yes | yes | yes | no | yes |
| Priority | `priority` | Select | yes | `Medium` | no | yes | yes | no | yes |
| Due Date | `due_date` | Date | no | — | yes | yes | yes | no | yes |
| Links | `links` | Table → `Dynamic Link` | no | — | yes | no | no | no | no |

`status` Options:

```text
Open
Waiting
Closed
Cancelled
```

`priority` Options:

```text
Low
Medium
High
```

`due_date` означает общий срок Work Item. Не переопределяйте общий перевод строки `Due Date` только ради этой семантики; различие с `Complete By` назначения объясняется моделью и проверяется отдельно.

### Layout формы

Используйте штатные `Section Break` / `Column Break`:

```text
Work
├── Subject
└── Description

Parameters
├── Status
├── Priority
└── Due Date

Links
└── Links
```

Собственный CSS не нужен.

## 4. Настройте DocPerm

Для `VEQTA Work User`, permission level `0`:

| Permission | Value |
| --- | --- |
| Read | Yes |
| Create | Yes |
| Write | Yes |
| Report | Yes |
| Delete | No |
| Share | No |
| Import | No |
| Export | No |
| Print | No |
| Email | No |
| Submit | No |
| Cancel | No |
| Amend | No |
| If Owner | No |

Не расширяйте permissions стандартного `ToDo` и не меняйте административную границу `System Manager`.

Эта модель является доверенной общей очередью. Поэтому любой `VEQTA Work User` имеет Write на Work Item и по штатной семантике Assign To может снять чужое назначение через `remove`. Завершить назначение через `close` может только сам assignee.

## 5. Не добавляйте lifecycle-код

Generated controller `Work Item` оставьте без прикладной логики.

Baseline не добавляет:

```text
Work Item.on_update → ToDo
ToDo.validate hook
синхронизацию Work Item.status ↔ ToDo.status
запрет Assign To по статусу Work Item
```

`Work Item` и `ToDo` используют штатную семантику Frappe. Активное назначение означает персональную ответственность, но не создаёт отдельного сохранённого состояния `In Progress`.

Собственный lifecycle появляется только после подтверждённого бизнес-требования.

## 6. List View

Не добавляйте обязательный `work_item_list.js`.

Проверьте стандартный List View с полями:

```text
subject
status
priority
due_date
```

Пользовательские фильтры:

```text
status in Open, Waiting
status = Open
status = Waiting
Assigned To → Me
```

`Assigned To` использует штатную assignment-механику Frappe. Не добавляйте собственный `assignee` только ради фильтра.

Global Saved Filters не создаются как App state.

## 7. Создайте Kanban

```text
Kanban Board Name: VEQTA Work Items
Reference DocType: Work Item
Field: status
Private: No
```

Колонки:

```text
Open
Waiting
Closed
Cancelled
```

В Kanban Settings добавьте:

```text
priority
due_date
```

Перетаскивание меняет только `Work Item.status`; App не синхронизирует связанные ToDo.

### Поставка Kanban

В `hooks.py` добавьте только fixture declaration:

```python
fixtures = [
    {
        "doctype": "Kanban Board",
        "filters": [["name", "=", "VEQTA Work Items"]],
    }
]
```

Экспорт:

```bash
bench --site <site> export-fixtures
```

Проверьте, что fixture содержит только нужную доску.

Kanban Board не имеет standard file-backed канала, поэтому узкий fixture здесь уместен. Patch и собственный setup-код не нужны.

## 8. Создайте standard Number Cards

| Name | Filters |
| --- | --- |
| `VEQTA Active Work Items` | `status in Open, Waiting` |
| `VEQTA Waiting Work Items` | `status = Waiting` |
| `VEQTA High Priority Work Items` | `status in Open, Waiting`, `priority = High` |
| `VEQTA Due Today Work Items` | `status in Open, Waiting`, `due_date Timespan Today` |

Общие настройки:

```text
Type: Document Type
Document Type: Work Item
Function: Count
Is Public: Yes
Is Standard: Yes
Module: VEQTA Work Management
Show Percentage Stats: No
```

Для визуального разделения используйте штатные `Color` / `Background Color`.

В Developer Mode после сохранения проверьте, что Number Cards появились как standard files в каталоге `number card` модуля App. На install/migrate Frappe загрузит их через штатный `sync_dashboards()`.

Карточку «Без исполнителя» пока не создавайте как обязательную: сначала проверьте фактическое поведение assignment-фильтра на используемом patch-release.

## 9. Создайте standard Dashboard Chart

```text
Chart Name: VEQTA New Work Items
Chart Type: Count
Document Type: Work Item
Time Series: Yes
Time Series Based On: creation
Timespan: Last Month
Time Interval: Daily
Type: Line
Is Public: Yes
Is Standard: Yes
Module: VEQTA Work Management
```

График показывает поступление Work Item, а не производительность.

После сохранения в Developer Mode проверьте standard file в каталоге `dashboard chart` модуля App. При install/migrate Frappe загрузит его через тот же `sync_dashboards()`.

Не добавляйте для Number Card / Dashboard Chart fixtures или `importable_doctypes`: для них уже есть специализированный штатный sync.

## 10. Создайте standard Workspace

```text
Label: VEQTA Work Management
Title: VEQTA Work Management
Public: Yes
Module: VEQTA Work Management
Roles:
  VEQTA Work User
```

Shortcuts:

```text
New Work Item
  Type: DocType
  Link To: Work Item
  DocType View: New

Work Item List
  Type: DocType
  Link To: Work Item
  DocType View: List

Work Board
  Type: DocType
  Link To: Work Item
  DocType View: Kanban
  Kanban Board: VEQTA Work Items
```

Компоновка:

```text
Actions
├── New Work Item
├── Work Item List
└── Work Board

Current State
├── VEQTA Active Work Items
├── VEQTA Waiting Work Items
├── VEQTA High Priority Work Items
└── VEQTA Due Today Work Items

Intake
└── VEQTA New Work Items
```

Не добавляйте Custom HTML/CSS только ради декора.

Отдельный standard `Workspace Sidebar` в baseline не создавайте. Frappe v16 умеет автоматически собирать module navigation; собственный Sidebar нужен только при реальном требовании к структуре навигации, которое автоматическая сборка не закрывает.

## 11. Локализация через Gettext

```bash
bench generate-pot-file --app veqta_work_management
bench create-po-file ru --app veqta_work_management
```

Редактируйте:

```text
apps/veqta_work_management/veqta_work_management/locale/ru.po
```

Добавляйте только уникальные строки App. Общие переводы Frappe не дублируйте без необходимости.

После изменений:

```bash
bench generate-pot-file --app veqta_work_management
bench update-po-files --app veqta_work_management --locale ru
bench compile-po-to-mo --app veqta_work_management --locale ru
bench --site <site> clear-cache
```

## 12. Assign To и сроки

Создайте Work Item с `due_date` и выполните ручной Assign To.

Проверьте два независимых значения:

```text
Work Item.due_date = срок общей работы
ToDo.date          = Complete By назначения
```

Стандартный Assign To dialog не использует `Work Item.due_date` как default для Complete By. Если Complete By не заполнить, dialog не отправляет пустое поле `date`, а backend Frappe создаёт ToDo с текущей датой.

Не добавляйте собственную синхронизацию сроков. Если появится требование автоматически передавать срок Work Item в ToDo, сначала проверьте `Assignment Rule.due_date_based_on`.

## 13. Auto Repeat

Создайте Auto Repeat без обязательного Assignee и проверьте ожидаемую metadata-семантику:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → Open
due_date     → пусто
links        → пусто
```

После этого отдельно проверьте нативные варианты только если они нужны сценарию:

```text
фиксированный исполнитель
→ Auto Repeat.assignee

автоматический выбор исполнителя
→ Assignment Rule

относительный due_date нового Work Item
→ Work Item.on_recurring
```

Отдельный scheduler не создаётся.

## 14. Проверьте состояние App

В каталоге App:

```bash
git status
git diff
```

Ожидаемые группы:

```text
standard metadata:
- Work Item
- Workspace
- Number Cards
- Dashboard Chart
- locale/main.pot
- locale/ru.po

штатная синхронизация:
- Work Item / Workspace → model sync
- Number Cards / Dashboard Chart → sync_dashboards()

hooks.py:
- fixture declaration только для Kanban Board VEQTA Work Items

fixture:
- только Kanban Board VEQTA Work Items

не должно попадать:
- fixture для Number Card / Dashboard Chart
- importable_doctypes для Number Card / Dashboard Chart
- отдельный fixture Role только ради VEQTA Work User
- пользовательские Work Item / ToDo
- global Saved Filters
- custom List JS
- ToDo hooks
- Workspace Sidebar без отдельного требования
- случайные DB exports
```

Затем:

```bash
bench --site <site> migrate
bench build
bench --site <site> clear-cache
```

## 15. Reinstall test на втором чистом Site

```bash
bench --site <second-site> install-app veqta_work_management
bench --site <second-site> migrate
bench --site <second-site> clear-cache
```

Без ручного повторения настройки должны появиться:

- standard `Work Item`;
- naming `WI-.#####`;
- Role `VEQTA Work User` и DocPerm;
- Kanban fixture;
- Number Cards из standard files через `sync_dashboards()`;
- Dashboard Chart из standard file через `sync_dashboards()`;
- Workspace;
- Gettext localization.

Пользовательские данные первого Site переноситься не должны.

Если обязательный объект отсутствует, сначала определите его штатный delivery mechanism. Patch не добавляется автоматически.

## 16. Runtime без Developer Mode

```bash
bench --site <site> set-config developer_mode 0
bench --site <site> clear-cache
```

Под обычным `VEQTA Work User` повторите основные сценарии: создание, List, Assign To, статусы, Kanban, Number Cards, Chart и Workspace.

Runtime не должен зависеть от Developer Mode.

## Критерии готовности

1. App создан `bench new-app`, без ручного каркаса.
2. `Work Item` — standard DocType App.
3. Имя Work Item имеет формат `WI-00001`.
4. Предметная модель содержит только шесть полей.
5. Назначения работают через standard `Assign To / ToDo`.
6. Активное назначение выражает персональную ответственность и не подменяется синтетическим `In Progress`.
7. Work Item и ToDo не связаны собственным lifecycle-кодом.
8. Общий `due_date` и `ToDo.date` трактуются как разные сроки.
9. Calendar/Gantt не включены без interval semantics.
10. Saved Filters не являются обязательным App state.
11. Kanban поставляется узким fixture.
12. Number Cards / Dashboard Chart поставляются standard files через штатный `sync_dashboards()`, а не fixtures.
13. Workspace является standard metadata.
14. Локализация использует Gettext.
15. Второй чистый Site устанавливается без ручного повторения обязательной настройки.

## Источники

- [Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Create an App](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`DocType`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Assign To dialog`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [`FieldGroup.get_values`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/ui/field_group.js)
- [`Assignment Rule`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/assignment_rule/assignment_rule.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Number Card`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/number_card/number_card.py)
- [`Dashboard Chart`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart/dashboard_chart.py)
- [`Dashboard sync`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/dashboard.py)
- [`Kanban Board`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/kanban_board/kanban_board.py)
- [`Workspace Sidebar`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace_sidebar/workspace_sidebar.py)
- [`Fixtures`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py)
- [`Gettext commands`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)
