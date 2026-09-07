# Безопасность v1

Управление работой использует штатные `Role`, `DocPerm` и permission semantics Frappe. Собственный permission model, `permission_query_conditions` и отдельная модель членства в baseline не вводятся.

## Роль `VEQTA Work User`

```text
Role: VEQTA Work User
Desk Access: Yes
```

Русское отображение роли поставляется App через Gettext.

Для обычного System User эта роль определяет доступ к `Work Item`. `Administrator` и `System Manager` остаются штатной административной границей.

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

`Share` для участников очереди выключен. Обычный пользователь не должен получать возможность открывать Work Item произвольным System Users только через назначение.

### Пользователь без доступа

Assign To dialog Frappe показывает enabled System Users, а не пользователей конкретной прикладной роли. Если выбран пользователь без права читать Work Item, штатный Assign To может попытаться обеспечить доступ через `DocShare`; `frappe.share.add()` проверяет право текущего пользователя на `Share`.

Поскольку `VEQTA Work User` не имеет `Share`, такой сценарий проверяется на живом Site и не считается поддерживаемым способом выдачи доступа.

Если позже потребуется ограниченный список назначаемых пользователей, это отдельная UX-ответственность. Ослабление authorization model ради picker не является решением.

## Права на `ToDo`

Work Management не добавляет широкие DocPerm на стандартный `ToDo` и не добавляет hooks, меняющие его lifecycle.

Frappe применяет собственные условия видимости и изменения ToDo. Baseline принимает их как штатную семантику Framework и проверяет на живом Site только те границы, которые важны для общей очереди.

В частности, отдельно проверяется:

- кто может закрыть своё назначение;
- может ли другой `VEQTA Work User` снять чужое назначение при наличии Write на Work Item;
- что происходит при назначении пользователя без доступа к Work Item.

Если эксплуатация потребует более строгого правила, оно проектируется как отдельное server-side требование. UI-запрет сам по себе не считается защитой.

## Независимость `Work Item` и `ToDo`

Baseline не связывает `Work Item.status` и `ToDo.status` собственным кодом.

```text
Work Item.status = состояние общей работы
ToDo.status      = состояние конкретного назначения
```

Изменение одного не используется как authorization rule или автоматический lifecycle другого.

## Почему нет `Work Manager`

Отдельная прикладная роль руководителя в baseline не нужна.

Выдавать ей общий `Read` на весь `ToDo` нельзя только ради аналитики Work Management: такой DocPerm действует на ToDo Site в целом и не выражает условие:

```text
reference_type = Work Item
```

Руководитель может быть обычным `VEQTA Work User` и видеть все Work Item. Если потребуется сводная аналитика назначений, она должна получить собственную узкую authorization boundary.

Отчёт не создаётся заранее.

## `assigned_to` и аналитика

Patch-level механика `assigned_to` / `_assign` не используется как security boundary Work Management.

Она может быть удобна для UI-фильтров после live-проверки, но не заменяет явную проверку прав в будущем App-level отчёте.

## Администрирование

Role и DocPerm принадлежат metadata App. Конечный пользователь не должен вручную собирать security model на каждом Site.

`VEQTA Work User` не является административной ролью и не даёт права менять Roles, DocPerm или Workspace metadata.

`User Group` не используется как замена Role: группировка пользователей и авторизация — разные ответственности.

## Developer Mode

Developer Mode нужен для разработки standard metadata App. Он не является привилегией пользователя и не участвует в authorization logic.

После сборки пользовательские сценарии должны работать с `developer_mode = 0`.

Если появляется новое бизнес-ограничение, порядок решения:

```text
требование
→ DocPerm / User Permission / Share semantics
→ официальный permission/controller hook
→ минимальная серверная проверка
```

Серверный код не добавляется до появления самого требования.

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
        └── стандартная семантика ToDo
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
- [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)
