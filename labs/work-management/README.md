# Work Management: историческое состояние

## Вопрос

Можно ли штатными данными Frappe восстановить состояние работы и ответственного на произвольный момент в прошлом — без собственного event log и snapshots?

Проверяем на **Frappe Framework v16.33.0**.

Frappe хранит эти данные разными механизмами:

- `Track Changes` создаёт `Version` с изменёнными полями, старым и новым значением;
- `Assign To` создаёт `ToDo`, связанный с исходным Document;
- снятие или закрытие назначения меняет `status` этого `ToDo`;
- у `ToDo` включён `Track Changes`.

Источники:

- https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/version/version.py
- https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py
- https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/todo/todo.json

Документация и код описывают эти механизмы по отдельности. Эксперимент проверяет, образуют ли они вместе достаточную историческую модель.

## Стенд

Нужен отдельный Site с простым Standard DocType:

```text
Work Item
├── title      Data, required
├── status     Select, required
└── due_date   Date
```

`status`:

```text
New
In Progress
Done
```

Для `Work Item` включить `Track Changes`.

Поле ответственного в `Work Item` не добавлять. Назначения выполняются штатным `Assign To`.

Нужны два обычных пользователя. Ни Workflow, ни собственный код, ни hooks для этого эксперимента не нужны.

Перед началом записать:

```text
Frappe version:
Site:
Work Item name:
User A:
User B:
```

## Сценарий

Создать один `Work Item` и выполнить действия строго по порядку. После каждого действия записывать фактическое время из системы.

| Шаг | Действие | Время |
| --- | --- | --- |
| S0 | создать Work Item со `status = New` и `due_date = D1` | |
| S1 | назначить User A через `Assign To` | |
| S2 | изменить `status`: `New → In Progress` | |
| S3 | изменить `due_date`: `D1 → D2` | |
| S4 | снять назначение User A | |
| S5 | назначить User B | |
| S6 | изменить `status`: `In Progress → Done` | |
| S7 | изменить `status`: `Done → In Progress` | |
| S8 | изменить `status`: `In Progress → Done` | |

Не редактировать записи `Version` и `ToDo` вручную.

## Что посмотреть после сценария

### Work Item

Зафиксировать текущее состояние Document:

```text
status:
due_date:
modified:
modified_by:
```

### Version для Work Item

В `bench console` получить версии исследуемого Work Item:

```python
frappe.get_all(
    "Version",
    filters={"ref_doctype": "Work Item", "docname": "WORK_ITEM_NAME"},
    fields=["name", "owner", "creation", "data"],
    order_by="creation asc",
)
```

Для каждой записи проверить:

- время;
- пользователя;
- какие поля изменились;
- есть ли старое и новое значение.

### ToDo

Получить все назначения исследуемого Work Item:

```python
frappe.get_all(
    "ToDo",
    filters={"reference_type": "Work Item", "reference_name": "WORK_ITEM_NAME"},
    fields=[
        "name",
        "allocated_to",
        "assigned_by",
        "status",
        "creation",
        "modified",
    ],
    order_by="creation asc",
)
```

Записать `name` найденных `ToDo`.

### Version для ToDo

Для каждого найденного `ToDo` получить его `Version`:

```python
frappe.get_all(
    "Version",
    filters={"ref_doctype": "ToDo", "docname": "TODO_NAME"},
    fields=["name", "owner", "creation", "data"],
    order_by="creation asc",
)
```

## Проверка восстановления

Не смотреть на таблицу действий выше. Используя только сохранённые данные Frappe, попытаться восстановить ответы.

| Вопрос | Ответ | Откуда получен факт |
| --- | --- | --- |
| Какой `status` был после S2 и до S6? | | |
| Какой `due_date` действовал до S3? | | |
| Кто был ответственным после S1 и до S4? | | |
| Был ли промежуток без ответственного между S4 и S5? | | |
| Кто был ответственным после S5? | | |
| Сколько раз работа переходила в `Done`? | | |
| Можно ли определить время каждого перехода `status`? | | |
| Можно ли определить время начала и окончания каждого назначения? | | |
| Можно ли восстановить состояние Work Item на произвольный момент между S0 и S8? | | |

Отдельно проверить начальное состояние после S0: достаточно ли сохранённых исторических данных, чтобы узнать исходный `status` и `due_date`, не опираясь на память о создании записи и текущие defaults DocType.

## Результат

После прогона заполнить таблицу.

| Факт | Восстанавливается | Источник | Ограничение |
| --- | --- | --- | --- |
| текущее состояние | | | |
| история `status` | | | |
| история `due_date` | | | |
| история ответственного | | | |
| повторное завершение | | | |
| состояние на момент T | | | |

## Вывод

Если состояние и ответственность на момент T восстанавливаются однозначно из штатных данных, отдельный исторический слой для этой задачи не нужен.

Если какой-то факт восстановить нельзя или для него приходится делать предположение, нужно зафиксировать **конкретно недостающий факт**. Только после этого имеет смысл проверять дополнительную модель: событие, snapshot или аналитическую витрину.
