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

Assign To dialog Frappe показывает enabled System Users, а не пользователей конкретной прикладной роли. Если выбран пользователь без права читать Work Item, штатный Assign To проверяет доступ assignee к исходному документу и при необходимости пытается выдать `DocShare`, если document sharing не отключён.

Поскольку `VEQTA Work User` не имеет `Share`, такой сценарий не рассматривается как поддерживаемый способ выдачи доступа. Его фактическое поведение проверяется на живом Site текущего patch-release.

Если позже потребуется ограниченный список назначаемых пользователей, это отдельная UX-ответственность. Ослабление authorization model ради picker не является решением.

## Права на `ToDo`

Work Management не добавляет широкие DocPerm на стандартный `ToDo` и не добавляет hooks, меняющие его lifecycle.

Frappe применяет собственные условия видимости и изменения ToDo. В v16.33.0 пользователь без отдельной широкой роли на ToDo видит ToDo, если он является `allocated_to`, `assigned_by` или `owner` этого ToDo.

Baseline принимает эту семантику Framework и не превращает `ToDo` в общую таблицу Work Management.

### Завершение и снятие назначения

Стандартный Assign To различает два действия:

```text
Complete assignment
→ frappe.desk.form.assign_to.close
→ ToDo.status = Closed
→ только сам assignee

Remove assignment
→ frappe.desk.form.assign_to.remove
→ ToDo.status = Cancelled
→ доступно assignee или пользователю с Write на исходный документ
```

Серверный `close` отдельно проверяет, что `assign_to == frappe.session.user`. `remove` проверяет permission на исходный документ и затем меняет связанный ToDo штатным механизмом Frappe.

Следствие для baseline: поскольку каждый `VEQTA Work User` имеет Write на все Work Item, один участник общей очереди может снять назначение другого участника. Это не скрытый дефект permission model, а прямое следствие выбранной доверенной общей очереди и штатной семантики Assign To.

Если эксплуатация потребует правило «чужое назначение снимает только руководитель» или «назначение нельзя снять без отдельного разрешения», это станет самостоятельным server-side требованием. UI-запрет сам по себе защитой не считается.

## Независимость `Work Item` и `ToDo`

Baseline не связывает `Work Item.status` и `ToDo.status` собственным кодом.

```text
Work Item.status = состояние общей работы
ToDo.status      = состояние конкретного назначения
```

Изменение одного не используется как authorization rule или автоматический lifecycle другого.

Активное назначение означает персональную ответственность. Оно не используется как доказательство отдельного состояния `In Progress` и не ограничивает право других участников доверенной очереди изменять Work Item.

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

`_assign` штатно поддерживается Frappe как внутреннее поле reference document и используется стандартными Desk-представлениями. Его можно использовать через штатный UI `Assigned To`, но App не должен строить на строковом содержимом `_assign` собственную authorization logic или публичный контракт.

## Communication и Email

`Communication` может быть связан с Work Item и отображаться в Timeline по штатной семантике Frappe.

При этом `VEQTA Work User` не имеет permission `Email` на Work Item. Поэтому наличие связанного `Communication` не означает, что baseline предоставляет пользователю отдельный workflow отправки почты из Work Item.

Если такой сценарий станет требованием, сначала проверяется штатная email/Communication семантика и только затем необходимость менять permissions или добавлять прикладное поведение.

## Администрирование

Role и DocPerm принадлежат metadata App. Конечный пользователь не должен вручную собирать security model на каждом Site.

При импорте standard DocType Frappe создаёт отсутствующие Role, которые перечислены в его permission rows. Поэтому отдельный fixture только ради `VEQTA Work User` не нужен; воспроизводимость проверяется reinstall-test.

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
        ├── может снять чужое назначение через штатный Assign To remove
        └── завершает своё назначение через штатный Assign To close
```

## Источники Frappe

Текущий проверочный ориентир — Frappe v16.33.0.

- [`ToDo` controller](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`ToDo` metadata](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.json)
- [`Assign To`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Assign To dialog`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [`DocShare`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/share.py)
- [`Role`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/role/role.json)
- [`DocType import`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Permissions`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/permissions.py)
- [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)
