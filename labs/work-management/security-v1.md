# Безопасность v1

Управление работой использует штатные `Role`, `DocPerm` и permission semantics Frappe. Собственный permission model, `permission_query_conditions` и отдельная модель членства в baseline не вводятся.

## Роль `VEQTA Work User`

Участник общей очереди получает одну прикладную роль:

```text
Role: VEQTA Work User
Desk Access: Yes
```

Русское отображение роли поставляется App через Gettext `locale/ru.po`.

Для обычного System User эта роль определяет доступ к `Work Item`. Наличие общего `Desk User` само по себе не даёт доступа к очереди. `Administrator` и `System Manager` остаются штатной административной границей.

## Права на `Work Item`

Для permission level `0`:

| Permission | VEQTA Work User |
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

Смысл модели:

- все участники видят общую очередь;
- любой участник может зарегистрировать работу;
- все участники могут изменять Work Item;
- ненужная работа переводится в `Cancelled`, а не удаляется;
- доступ не ограничивается владельцем документа.

Это доверенная совместная очередь. Правило «редактировать Work Item может только назначенный пользователь» в baseline не заявляется: обычный DocPerm такого условия не выражает.

## Назначения

Исполнители назначаются штатным `Assign To`, который создаёт связанные `ToDo`.

Если назначаемый пользователь уже имеет доступ к Work Item, `DocShare` не требуется. Обычный случай — назначение между пользователями с ролью `VEQTA Work User`.

`Share` для участников очереди выключен. Это принципиально: обычный пользователь не должен получать возможность открывать Work Item произвольным System Users только через назначение.

### Пользователь без доступа

Assign To dialog Frappe показывает enabled System Users, а не пользователей конкретной прикладной роли. Если выбран пользователь без права читать Work Item, штатный Assign To пытается обеспечить доступ через `DocShare`. `frappe.share.add()` при этом проверяет право текущего пользователя на `Share`.

Поскольку `VEQTA Work User` не имеет `Share`, такое назначение должно завершиться permission error и не является поддерживаемым сценарием. Расширять `Share` только ради более удобного picker нельзя.

Если позже потребуется ограниченный список назначаемых пользователей, это отдельная UX-ответственность и сначала должна анализироваться как официальный extension point, а не как ослабление authorization model.

## Права на `ToDo`

Work Management не добавляет широкие DocPerm на стандартный `ToDo`.

Frappe применяет собственные условия видимости. Обычный пользователь работает прежде всего с ToDo, где он связан с назначением как assignee/assigner/owner, а не получает список всех ToDo Site.

Закрыть назначение штатной кнопкой Done может сам assignee: server method `assign_to.close()` проверяет текущего пользователя.

Снятие назначения устроено иначе. Пользователь с Write на исходный Work Item может оказаться способен отменить чужое назначение. Для доверенной общей очереди это известная граница baseline, которая проверяется на живом Site.

Если эксплуатация потребует запретить это действие, UI-запрет без серверной проверки не считается решением.

## Терминальные Work Item

Lifecycle-инвариант относится к самой модели работы, а не к расширению прав:

```text
Work Item = Closed
→ активных ToDo быть не должно

Work Item = Cancelled
→ активных ToDo быть не должно
```

При `Closed` App закрывает активные назначения. При `Cancelled` App отменяет только активные назначения и не переписывает уже `Closed` ToDo.

Отдельный `doc_events` hook на `ToDo.validate`, ограниченный `reference_type = Work Item`, запрещает создать или повторно открыть `ToDo.status = Open` для уже terminal Work Item.

Этот hook не даёт пользователю дополнительных прав на ToDo и не меняет поведение назначений других DocTypes.

## Почему нет `Work Manager`

Отдельная прикладная роль руководителя в baseline не нужна.

Выдавать ей общий `Read` на весь `ToDo` нельзя только ради аналитики Work Management: такой DocPerm действует на ToDo Site в целом и не выражает условие:

```text
reference_type = Work Item
```

Руководитель может быть обычным `VEQTA Work User` и видеть все Work Item. Если потребуется сводная аналитика назначений, она должна иметь собственную узкую authorization boundary.

Первый вариант для такой ответственности — standard Script Report App, который:

- выбирает только `ToDo.reference_type = Work Item`;
- учитывает permission boundary Work Item;
- не раскрывает посторонние ToDo;
- не требует общего Read на ToDo.

Отчёт не создаётся заранее.

## Почему не используем `assigned_to` group-by как authorization layer

Frappe v16.33.0 имеет специальную агрегацию List View по `assigned_to`, но её запрос связывает `ToDo.reference_name` с разрешёнными именами исходных документов без явного ограничения `reference_type` в этой ветке запроса.

Поэтому такой group-by может быть удобным UI-инструментом после live-проверки, но не считается строгой security/analytics boundary Work Management.

## Администрирование

Роль и DocPerm принадлежат metadata App. Конечный пользователь не должен вручную конструировать security model на каждом Site.

`VEQTA Work User` не является административной ролью и не даёт права изменять Roles, DocPerm или Workspace metadata.

`User Group` не используется как замена Role: группа может быть удобна для выбора пользователей, но authorization остаётся ответственностью Role / DocPerm.

## Developer Mode

Developer Mode нужен для разработки standard metadata и кода App. Он не является привилегией пользователя и не должен участвовать в authorization logic.

После сборки пользовательские сценарии должны работать с `developer_mode = 0`.

Если появляется новое бизнес-ограничение, порядок решения:

```text
требование
→ DocPerm / User Permission / Share semantics
→ официальный permission/controller hook
→ минимальная серверная проверка
```

Клиентская защита не используется как единственный барьер критического правила.

## Граница v1

```text
Пользователь Site
│
├── Administrator / System Manager
│   └── штатный административный доступ
│
└── System User
    │
    ├── без VEQTA Work User
    │   └── Work Item недоступен
    │
    └── VEQTA Work User
        ├── Read всех Work Item
        ├── Create
        ├── Write
        ├── Report
        ├── без Delete
        ├── без Share
        └── стандартная видимость ToDo
```

## Источники Frappe

Текущий проверочный ориентир — Frappe v16.33.0.

- [`ToDo` controller](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`ToDo` metadata](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.json)
- [`Assign To`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Assign To dialog`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [`DocShare`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/share.py)
- [`Role`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/role/role.json)
- [`Permissions`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/permissions.py)
- [`List group-by`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/listview.py)
- [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)