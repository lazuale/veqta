# Управление работой v1: сборка на Frappe v16

Этот гайд собирает Work Management Lab как минимальный standard Frappe App и проверяет, что обязательное состояние воспроизводимо переносится на другой Site.

Перед началом:

- [Модель данных v1](data-model-v1.md);
- [Безопасность v1](security-v1.md);
- [Конфигурация v1](configuration-v1.md).

## 0. Development Site

Работайте на отдельном тестовом Site без пользовательских данных.

Из корня `frappe-bench` включите Developer Mode **только для этого Site**:

```bash
bench --site <site> set-config developer_mode 1
bench --site <site> clear-cache
```

Проверьте применённую конфигурацию:

```bash
bench --site <site> show-config
```

Не используйте `-g developer_mode 1`, если нет причины включать Developer Mode для всех Sites bench.

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

Ожидаются как минимум:

```text
frappe
veqta_work_management
```

## 2. Создайте роль `VEQTA Work User`

На development Site создайте:

```text
Role Name: VEQTA Work User
Desk Access: Yes
```

Роль будет указана в permissions standard `Work Item`. При установке App на второй чистый Site отдельно проверяется, что Frappe создаёт отсутствующую Role из standard metadata. Не добавляйте fixture роли заранее, если standard install path уже решает эту задачу.

## 3. Создайте standard DocType `Work Item`

Под `Administrator` откройте `DocType` → `New`.

```text
Name: Work Item
Module: VEQTA Work Management
Custom: No

Naming Rule: Expression
Auto Name: VWM-WI-.#####
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

Источник labels можно оставить английским: русский интерфейс формируется переводами Frappe/App.

Предметные поля:

| Label | Fieldname | Type | Required | Default | No Copy | List | Standard Filter | Global Search | Quick Entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Subject | `subject` | Data | yes | — | no | title | no | yes | required |
| Description | `description` | Text Editor | no | — | no | no | no | yes | yes |
| Status | `status` | Select | yes | `Open` | yes | yes | yes | no | required |
| Priority | `priority` | Select | yes | `Medium` | no | yes | yes | no | required |
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

Добавьте штатные `Section Break` / `Column Break`, не меняя предметную модель:

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

Для трёх параметров используйте Column Breaks, чтобы они стояли в одной строке на широком экране.

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

Не расширяйте permissions стандартного `ToDo` и не удаляйте административный доступ `System Manager`.

## 5. Добавьте lifecycle `Work Item`

После сохранения standard DocType Frappe создаст controller-файл. Используйте созданный Framework путь, а не создавайте альтернативный service layer.

В `work_item.py` добавьте:

```python
import frappe
from frappe import _
from frappe.desk.form import assign_to
from frappe.model.document import Document


class WorkItem(Document):
    def on_update(self):
        if self.status == "Closed":
            assign_to.close_all_assignments(
                self.doctype,
                self.name,
                ignore_permissions=True,
            )
        elif self.status == "Cancelled":
            assign_to.clear(
                self.doctype,
                self.name,
                ignore_permissions=True,
            )


def validate_work_item_todo(doc, method=None):
    if (
        doc.reference_type != "Work Item"
        or doc.status != "Open"
        or not doc.reference_name
    ):
        return

    work_status = frappe.db.get_value("Work Item", doc.reference_name, "status")

    if work_status in {"Closed", "Cancelled"}:
        frappe.throw(
            _("Cannot create or reopen an assignment for a closed or cancelled Work Item.")
        )
```

Первый блок согласует существующие назначения с terminal status Work Item. Второй запрещает создать или повторно открыть активное назначение на terminal Work Item.

Не добавляйте обратную автоматизацию `ToDo → Work Item`: при нескольких исполнителях завершение одного ToDo не означает завершение всей работы.

## 6. Подключите официальный `doc_events` hook

В `veqta_work_management/hooks.py`:

```python
doc_events = {
    "ToDo": {
        "validate": (
            "veqta_work_management.veqta_work_management.doctype.work_item."
            "work_item.validate_work_item_todo"
        )
    }
}
```

Если `hooks.py` уже содержит `doc_events`, добавьте обработчик в существующую структуру, не создавая второй объект с тем же именем.

Hook действует на стандартный `ToDo`, но прикладная проверка сразу выходит для любого `reference_type`, кроме `Work Item`.

## 7. Настройте List View

В созданном Framework файле `work_item_list.js`:

```javascript
frappe.listview_settings["Work Item"] = {
	get_indicator(doc) {
		const colors = {
			Open: "blue",
			Waiting: "orange",
			Closed: "green",
			Cancelled: "gray",
		};

		return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
	},
};
```

Это штатный List View extension Frappe. Отдельный Client Script record не нужен.

Основные пользовательские фильтры создаются через обычный Filter UI:

```text
status in Open, Waiting
status = Open
status = Waiting
Assigned To → Me
```

Не создавайте обязательные global Saved Filters.

## 8. Создайте Kanban

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

В Kanban Settings добавьте на карточку:

```text
priority
due_date
```

Переход в `Closed` / `Cancelled` через drag должен вызвать обычное сохранение Work Item и тот же server lifecycle.

### Поставка Kanban

`Kanban Board` поставляется fixture. В `hooks.py`:

```python
fixtures = [
    {
        "doctype": "Kanban Board",
        "filters": [["name", "=", "VEQTA Work Items"]],
    }
]
```

Затем:

```bash
bench --site <site> export-fixtures
```

Проверьте, что fixture содержит только нужную доску, а не все пользовательские Kanban Boards Site.

## 9. Создайте standard Number Cards

Создайте четыре карточки:

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

Оформление:

| Card | Color | Background Color |
| --- | --- | --- |
| Active | `#1D4ED8` | `#EFF6FF` |
| Waiting | `#B45309` | `#FFF7ED` |
| High Priority | `#B91C1C` | `#FEF2F2` |
| Due Today | `#A16207` | `#FEFCE8` |

Карточку «Без исполнителя» пока не делайте mandatory: сначала отдельно проверьте patch-level поведение фильтра `Assigned To Is Not Set` в Number Card.

## 10. Создайте standard Dashboard Chart

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

График означает поступление новых работ, а не производительность.

## 11. Создайте standard Workspace

```text
Label: VEQTA Work Management
Title: VEQTA Work Management
Type: Workspace
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

Разложите Workspace штатными Header blocks:

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

Не добавляйте Custom HTML/CSS только ради декоративного оформления.

## 12. Локализация v16 через Gettext

Для нового App на Frappe v16 используйте основной Gettext/PO path, а не legacy CSV translations.

После того как metadata и translatable code готовы:

```bash
bench generate-pot-file --app veqta_work_management
bench create-po-file ru --app veqta_work_management
```

Редактируйте:

```text
apps/veqta_work_management/veqta_work_management/locale/ru.po
```

Минимально нужны уникальные строки App, например:

```text
Work Item                         → Работа
VEQTA Work Management             → Управление работой
VEQTA Work User                   → Участник управления работой
VEQTA Work Items                  → Работы
VEQTA Active Work Items           → Активные работы
VEQTA Waiting Work Items          → Ожидание
VEQTA High Priority Work Items    → Высокий приоритет
VEQTA Due Today Work Items        → Срок сегодня
VEQTA New Work Items              → Новые работы
New Work Item                     → Новая работа
Work Item List                    → Список работ
Work Board                        → Доска
```

Не дублируйте в App общие переводы Frappe (`Open`, `Priority`, `Status` и т. п.), если core Russian translation уже даёт подходящее значение.

После изменения translatable strings:

```bash
bench generate-pot-file --app veqta_work_management
bench update-po-files --app veqta_work_management --locale ru
bench compile-po-to-mo --app veqta_work_management --locale ru
bench --site <site> clear-cache
```

## 13. Auto Repeat

Создайте standard Auto Repeat без обязательного Assignee.

Новый Work Item должен получать:

```text
subject      → копируется
description  → копируется
priority     → копируется
status       → Open
due_date     → пусто
links        → пусто
```

Если потребуется относительный срок, первым проверяется `Work Item.on_recurring`. Собственный scheduler для этого не создаётся.

## 14. Добавьте тесты собственных контрактов

Тесты App должны проверять только наше поведение:

1. `Closed` закрывает все активные ToDo этого Work Item.
2. `Cancelled` отменяет все активные ToDo этого Work Item.
3. нельзя создать `ToDo.status = Open` для terminal Work Item.
4. нельзя повторно открыть закрытый ToDo, пока Work Item terminal.
5. закрытие одного ToDo не меняет Work Item.status.
6. Auto Repeat не переносит `status`, `due_date`, `links`.

Запуск:

```bash
bench --site <site> run-tests --app veqta_work_management
```

Не тестируйте заново стандартные возможности Frappe, которые App не изменяет.

## 15. Проверьте состояние App

В каталоге App:

```bash
git status
git diff
```

Ожидаемые группы:

```text
standard metadata / code:
- Work Item
- controller
- list.js
- Workspace
- Number Cards
- Dashboard Chart
- hooks.py
- locale/main.pot
- locale/ru.po

fixture:
- только Kanban Board VEQTA Work Items

не должно попадать:
- Work Item user data
- ToDo user data
- Saved Filters пользователей
- случайные DB exports
```

Затем:

```bash
bench --site <site> migrate
bench build
bench --site <site> clear-cache
```

## 16. Reinstall test на втором чистом Site

Создайте второй test Site и установите App без ручного повторения конфигурации:

```bash
bench --site <second-site> install-app veqta_work_management
bench --site <second-site> migrate
bench --site <second-site> clear-cache
```

Проверьте:

- появился `Work Item` с правильным naming и полями;
- появился `VEQTA Work User`;
- DocPerm совпадает с моделью;
- lifecycle code работает;
- присутствует Kanban fixture;
- появились standard Number Cards / Chart / Workspace;
- русский перевод работает после compile/build;
- пользовательские данные первого Site не приехали.

Если обязательный объект отсутствует, сначала определите его штатный delivery mechanism. Patch не является автоматическим ответом.

## 17. Проверка без Developer Mode

После фиксации App выключите режим на тестовом Site:

```bash
bench --site <site> set-config developer_mode 0
bench --site <site> clear-cache
```

Под обычным `VEQTA Work User` проверьте:

- создание Work Item;
- List View;
- Assign To;
- terminal lifecycle;
- Kanban;
- Number Cards;
- Chart;
- Workspace.

Runtime не должен зависеть от Developer Mode.

## Критерии готовности

1. App создан `bench new-app`, без ручного каркаса.
2. `Work Item` — standard DocType `VEQTA Work Management`.
3. Имя Work Item имеет формат `VWM-WI-00001`.
4. Предметная модель содержит только шесть полей.
5. Назначения работают через standard `ToDo`.
6. Terminal lifecycle защищён на сервере.
7. Calendar/Gantt не включены без interval semantics.
8. Saved Filters не являются обязательным App state.
9. Kanban поставляется узким fixture.
10. Number Cards / Chart / Workspace являются standard metadata.
11. Локализация использует v16 Gettext/PO path.
12. Второй чистый Site устанавливается без ручного повторения обязательной настройки.

## Источники

- [Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Create an App](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Document hooks`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py)
- [`Fixtures`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py)
- [`Gettext commands`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)