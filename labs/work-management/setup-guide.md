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

Роль будет указана в permissions standard `Work Item`. Отдельный fixture роли заранее не добавляется; её доставка проверяется reinstall-test.

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

## 5. Не добавляйте lifecycle-код

Generated controller `Work Item` оставьте без прикладной логики.

Baseline не добавляет:

```text
Work Item.on_update → ToDo
ToDo.validate hook
синхронизацию Work Item.status ↔ ToDo.status
запрет Assign To по статусу Work Item
```

`Work Item` и `ToDo` используют штатную семантику Frappe. Собственный lifecycle появляется только после подтверждённого бизнес-требования.

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

## 12. Auto Repeat

Создайте Auto Repeat без обязательного Assignee и проверьте ожидаемую metadata-семантику:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → Open
due_date     → пусто
links        → пусто
```

Отдельный scheduler не создаётся.

## 13. Проверьте состояние App

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

fixture:
- только Kanban Board VEQTA Work Items

не должно попадать:
- пользовательские Work Item / ToDo
- global Saved Filters
- custom List JS
- ToDo hooks
- случайные DB exports
```

Затем:

```bash
bench --site <site> migrate
bench build
bench --site <site> clear-cache
```

## 14. Reinstall test на втором чистом Site

```bash
bench --site <second-site> install-app veqta_work_management
bench --site <second-site> migrate
bench --site <second-site> clear-cache
```

Без ручного повторения настройки должны появиться:

- standard `Work Item`;
- naming `WI-.#####`;
- Role и DocPerm;
- Kanban fixture;
- Number Cards;
- Dashboard Chart;
- Workspace;
- Gettext localization.

Пользовательские данные первого Site переноситься не должны.

Если обязательный объект отсутствует, сначала определите его штатный delivery mechanism. Patch не добавляется автоматически.

## 15. Runtime без Developer Mode

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
6. Work Item и ToDo не связаны синтетическим lifecycle-кодом.
7. Calendar/Gantt не включены без interval semantics.
8. Saved Filters не являются обязательным App state.
9. Kanban поставляется узким fixture.
10. Number Cards / Chart / Workspace являются standard metadata.
11. Локализация использует Gettext.
12. Второй чистый Site устанавливается без ручного повторения обязательной настройки.

## Источники

- [Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Create an App](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Fixtures`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py)
- [`Gettext commands`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)
