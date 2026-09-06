# Security v1

Work Management использует штатные `Role`, `DocPerm` и permission semantics Frappe. Собственный permission engine, `permission_query_conditions` hook и отдельная модель членства не вводятся.

## Роль `Work User`

Участник Work Management получает одну прикладную роль:

```text
Role: Work User
Desk Access: Yes
```

Для обычного прикладного System User роль определяет границу Work Management на `Site`: наличие обычного `Desk User` само по себе не даёт доступа к `Work Item`. Штатный административный доступ `System Manager` и `Administrator` рассматривается отдельно и этой прикладной границей не отменяется.

## Права на `Work Item`

Для `Work Item`, permission level `0`:

| Permission | Work User |
| --- | --- |
| Read | yes |
| Create | yes |
| Write | yes |
| Report | yes |
| Delete | no |
| Share | no |
| Export | no |
| Import | no |
| Print | no |
| Email | no |
| Submit | no |
| Cancel | no |
| Amend | no |
| If Owner | no |

Смысл этой модели:

- все `Work User` видят общую очередь;
- любой `Work User` может зарегистрировать новую работу;
- все участники могут изменять открытые им `Work Item`;
- ненужная работа переводится в `Cancelled`, а не удаляется;
- доступ не ограничивается владельцем документа, потому что очередь общая.

Текущий вариант является доверенной совместной очередью. Штатные DocPerm не выражают правило «изменять Work Item может только назначенный пользователь», поэтому такое ограничение не заявляется.

## Назначения

Исполнители назначаются штатным `Assign To`, который создаёт связанные `ToDo`.

Если назначаемый пользователь уже имеет доступ к `Work Item`, дополнительный `DocShare` не требуется. Это обычный случай для назначения между пользователями с ролью `Work User`.

`Share` для `Work User` намеренно выключен. Если пользователь без доступа к `Work Item` назначается исполнителем, Frappe пытается предоставить ему доступ через `DocShare`; создание такого share требует соответствующего permission у назначающего пользователя. Таким образом, обычный `Work User` не может использовать assignment как способ открыть Work Item произвольному пользователю Site.

## Права на `ToDo`

Work Management не добавляет собственные DocPerm к стандартному `ToDo`.

Frappe применяет к `ToDo` собственные permission conditions. Обычный пользователь видит ToDo, если он:

```text
allocated_to = current user
или
assigned_by = current user
или
owner = current user
```

Поэтому `Work User` работает со своими назначениями и назначениями, созданными им, не получая общего доступа ко всем `ToDo` Site.

Закрыть assignment как выполненный может сам assignee: штатный endpoint Frappe проверяет, что `assign_to` совпадает с текущим пользователем.

При этом пользователь с `Write` на исходный `Work Item` может снять assignment другого пользователя. В native-first модели это принимается как часть доверенной совместной очереди.

## Почему нет `Work Manager`

Отдельная роль `Work Manager` в baseline не создаётся.

Причина в семантике стандартного `ToDo`: если пользователь имеет неавтоматическую роль с доступом к `ToDo`, Frappe снимает обычное персональное ограничение выборки. Такое разрешение действует на `ToDo` всего Site, а не только на записи с:

```text
reference_type = Work Item
```

Обычный `DocPerm` не умеет ограничить `Read` условием по `reference_type`. Поэтому выдавать менеджеру общий `Read` на `ToDo` только ради аналитики Work Management слишком широко.

В текущем baseline руководитель может быть обычным `Work User` и анализировать все `Work Item`, но общая аналитика по assignment load всей команды не считается безопасно закрытой чистой конфигурацией Frappe.

Если такая аналитика станет обязательной, потребуется отдельное решение с сохранением permission boundary; расширять доступ ко всем `ToDo` Site ради этого нельзя.

## Администрирование

Настройку Roles и DocPerm выполняет системный администратор штатными средствами Frappe. `Work User` не является административной ролью и не даёт права изменять модель безопасности.

При создании нового DocType Frappe добавляет permission row для `System Manager`. Эта строка относится к штатному администрированию DocType и не заменяется прикладной ролью `Work User`. `Administrator` также сохраняет штатный административный доступ.

`User Group` не используется как замена Role: группы предназначены для группировки пользователей и назначения, а authorization остаётся ответственностью `Role` / `DocPerm`.

## Граница v1

```text
Site user
│
├── Administrator / System Manager
│   └── штатный административный доступ
│
└── обычный System User
    │
    ├── без Work User
    │   └── Work Item недоступен
    │
    └── Work User
        ├── Read all Work Items
        ├── Create
        ├── Write
        ├── Report
        ├── no Delete
        ├── no Share
        └── стандартная видимость ToDo
            ├── назначенные мне
            ├── назначенные мной
            └── созданные мной
```

## Источники Frappe

Текущий ориентир — Frappe v16.

- [`ToDo` controller, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/todo/todo.py)
- [`ToDo` metadata, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/todo/todo.json)
- [`Assign To`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py)
- [`DocShare`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/share.py)
- [`Role`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/role/role.json)
- [`DocPerm`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/docperm/docperm.json)
- [`DocType` form, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/doctype/doctype.js)
- [`Permissions`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py)
