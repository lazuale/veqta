# Безопасность v1

Управление работой использует штатные `Role`, `DocPerm` и семантику прав Frappe. Собственный механизм прав, hook `permission_query_conditions` и отдельная модель членства на текущем этапе не вводятся.

Наличие минимального App и Developer Mode не меняет прикладную модель доступа автоматически. Они только оставляют доступными официальные extension points Frappe, если чистых DocPerm действительно окажется недостаточно для подтверждённого требования.

## Роль `Work User`

Участник управления работой получает одну прикладную роль:

```text
Role: Work User
Desk Access: Yes
```

Для обычного прикладного System User роль определяет границу доступа к `Work Item` на Site: наличие обычного `Desk User` само по себе не даёт доступа к рабочей очереди. Штатный административный доступ `System Manager` и `Administrator` рассматривается отдельно и этой прикладной границей не отменяется.

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
- все участники могут изменять доступные им `Work Item`;
- ненужная работа переводится в `Cancelled`, а не удаляется;
- доступ не ограничивается владельцем документа, потому что очередь общая.

Текущий вариант является доверенной совместной очередью. Штатные DocPerm сами по себе не выражают правило «изменять Work Item может только назначенный пользователь», поэтому такое ограничение не заявляется.

## Назначения

Исполнители назначаются штатным `Assign To`, который создаёт связанные `ToDo`.

Если назначаемый пользователь уже имеет доступ к `Work Item`, дополнительный `DocShare` не требуется. Это обычный случай для назначения между пользователями с ролью `Work User`.

`Share` для `Work User` намеренно выключен. Если пользователь без доступа к `Work Item` назначается исполнителем, Frappe может использовать `DocShare`; обычный `Work User` не должен получать возможность открывать Work Item произвольным пользователям Site через назначение.

## Права на `ToDo`

Управление работой не добавляет собственные DocPerm к стандартному `ToDo`.

Frappe применяет к `ToDo` собственные условия доступа. Обычный пользователь видит ToDo, если он:

```text
allocated_to = current user
или
assigned_by = current user
или
owner = current user
```

Поэтому `Work User` работает со своими назначениями и назначениями, созданными им, не получая общего доступа ко всем `ToDo` Site.

Закрыть назначение как выполненное может сам назначенный пользователь: штатный метод Frappe проверяет соответствие назначенного пользователя текущему пользователю.

Снятие назначения имеет другую серверную границу. В штатном пути Frappe перед отменой `ToDo` проверяется доступ к исходному Document; отдельного правила «снимать может только assignee» эта модель не добавляет.

Следовательно, в общей очереди один `Work User` может оказаться способен снять назначение другого. Это принимается как ограничение доверенной совместной модели v1 и обязательно проверяется на живом Site.

Если реальная эксплуатация потребует запретить такое действие, сначала анализируется официальный extension path App. UI-запрет без серверной защиты не считается решением.

## Почему нет `Work Manager`

Отдельная прикладная роль `Work Manager` в текущей модели не создаётся.

Причина — не в том, что руководителю не нужна аналитика, а в границе стандартного `ToDo`: широкий DocPerm на `ToDo` действует на записи всего Site, а не только на:

```text
reference_type = Work Item
```

Обычный DocPerm не выражает условие по `reference_type`. Поэтому выдавать руководителю общий `Read` на все `ToDo` Site только ради аналитики Work Management нельзя.

Руководитель может быть обычным `Work User` и видеть все `Work Item`, но общая аналитика загрузки по назначениям всей команды не считается закрытой простым расширением прав `ToDo`.

Если такая аналитика станет обязательной, первый developer path — не новый permission model и не расширение `ToDo` DocPerm, а отдельный standard Query/Script Report или другой штатный App-механизм, который:

- выбирает только назначения `Work Item`;
- применяет явную требуемую границу авторизации;
- не раскрывает посторонние `ToDo` Site.

Только если этого недостаточно, рассматриваются permission hooks или другой официальный extension point.

## Администрирование

Настройку Roles и DocPerm выполняет системный администратор штатными средствами Frappe. `Work User` не является административной ролью и не даёт права изменять модель безопасности.

Standard `Work Item` принадлежит App, но это не отменяет стандартную роль `System Manager` и доступ `Administrator`.

`User Group` не используется как замена Role: группы предназначены для группировки пользователей и назначения, а авторизация остаётся ответственностью `Role` / `DocPerm`.

## Developer Mode и безопасность

Developer Mode — режим разработки metadata и кода App, а не привилегия конечного пользователя.

Он не должен использоваться как условие доступа к Work Item или как обход permission model.

После сборки основные пользовательские сценарии должны проходить с выключенным Developer Mode. Если требуемое бизнес-правило нельзя надёжно защитить чистыми DocPerm, порядок решения такой:

```text
требование
→ проверить штатные DocPerm / User Permission / Share semantics
→ проверить официальный permission/report/controller extension point
→ добавить минимальную серверную проверку
```

Не добавляется клиентская защита как единственный барьер критического правила.

## Граница v1

```text
Пользователь Site
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
        ├── Read всех Work Item
        ├── Create
        ├── Write
        ├── Report
        ├── без Delete
        ├── без Share
        └── стандартная видимость ToDo
            ├── назначенные мне
            ├── назначенные мной
            └── созданные мной
```

## Источники Frappe

Текущий ориентир — Frappe v16.33.0.

- [`ToDo` controller, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`ToDo` metadata, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.json)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`DocShare`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/share.py)
- [`Role`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/role/role.json)
- [`DocPerm`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/docperm/docperm.json)
- [`Permissions`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/permissions.py)
- [`Report`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/report/report.py)
- [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)
