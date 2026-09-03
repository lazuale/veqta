# Модель учебного приложения

Практикум использует один предметный объект — внутреннюю заявку на закупку `Purchase Request`. Модель намеренно небольшая: цель не в количестве DocTypes, а в том, чтобы на одном понятном Document увидеть разницу между предметным состоянием, `Workflow` и системным `docstatus`.

## Purchase Request

```text
Purchase Request
├── subject            Data
├── description        Small Text
├── requested_amount   Currency
├── needed_by          Date
└── status             Select
```

Системное имя строится по выражению:

```text
PLT-PR-.#####
```

Примеры:

```text
PLT-PR-00001
PLT-PR-00002
```

`subject` используется как `Title Field`: системный `name` остаётся стабильным идентификатором, а заголовок можно исправлять без переименования Document.

## Кто является заявителем

Отдельного поля `requester` в практикуме нет.

Для учебного сценария принято:

```text
requester = Document.owner
```

Этого достаточно, пока пользователь создаёт заявку только от собственного имени. Если позже появится сценарий «создать за другого сотрудника», модель потребует отдельного анализа: `owner` и бизнес-понятие requester перестанут совпадать.

## Состояния

Практикум использует одно поле Standard DocType:

```text
status : Select
```

Финальный набор значений:

```text
PLT Draft
PLT Pending Approval
PLT Rejected
PLT Pending Senior
PLT Approved
PLT Cancelled
```

В начале практикума это обычный предметный `Select`. Позже то же поле становится `Workflow State Field`.

Отдельный обязательный `workflow_state` не создаётся: Frappe позволяет использовать уже существующее поле, если оно указано в Workflow. Если подходящего поля нет, Framework умеет создать `Custom Field` автоматически, но в нашем App второй источник состояния не нужен. См. [`Workflow.create_custom_field_for_workflow_state()` в v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

## Роли

Используются три прикладные роли:

```text
PLT Requester
PLT Approver
PLT Senior Approver
```

Они определяют возможности работы с `Purchase Request` через обычные DocType Permissions. Право выполнить конкретный переход процесса задаётся отдельно в `Workflow Transition`.

К концу практикума модель прав выглядит так:

| Role | Read | Create | Write | Submit | Cancel | Amend |
|---|---:|---:|---:|---:|---:|---:|
| `PLT Requester` | yes | yes | yes | no | no | yes |
| `PLT Approver` | yes | no | yes | yes | yes | no |
| `PLT Senior Approver` | yes | no | yes | yes | no | no |

Эта матрица развивается по этапам; лишние права не выдаются заранее.

## Маршрут согласования

Итоговый процесс:

```text
PLT Draft
   │
   └─ Submit for Review
        ↓
PLT Pending Approval
   ├─ Reject
   │    ↓
   │  PLT Rejected
   │    └─ Submit for Review → PLT Pending Approval
   │
   └─ Approve
        ├─ requested_amount <= 1000
        │      ↓
        │   PLT Approved
        │
        └─ requested_amount > 1000
               ↓
          PLT Pending Senior
               └─ Approve → PLT Approved
```

После появления требования фиксировать окончательное решение через Submit:

```text
PLT Approved  → docstatus 1
PLT Cancelled → docstatus 2
```

До этого `PLT Approved` остаётся обычным состоянием Workflow с `docstatus = 0`.

Название `Approved` само по себе не переводит Document в `docstatus = 1`.

## Одобрение собственной заявки

Пользователь может одновременно иметь `PLT Requester` и `PLT Approver`, но не должен одобрять собственную заявку.

Frappe предоставляет настройку `Allow Self Approval` на уровне перехода. В v16.33.0 серверная проверка сравнивает текущего пользователя с `doc.owner`; поэтому штатный механизм подходит нашей модели, где requester совпадает с owner. См. [`has_approval_access()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

Собственный validator для этого правила не нужен.

## Cancel и Amend

После того как окончательное согласование фиксируется через Submit:

```text
Approved → Cancelled
```

переход выполняется штатным `doc.cancel()` через Workflow. `apply_workflow()` выбирает операцию Document по `docstatus` следующего Workflow State, поэтому переход `1 → 2` является Cancel, а не обычным изменением Submitted Document. Источник: [`apply_workflow()` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

После Cancel заявитель получает отдельное право `Amend` и создаёт новый Draft с `amended_from`, не переписывая отменённый Document.

## Что хранится в App

В финальном состоянии App должен воспроизводимо поставлять:

```text
метаданные Standard DocType Purchase Request
DocType Permissions
собственные Workflow Action Master
Workflow State
Workflow с его states, transitions и conditions
автоматические тесты
```

Пользователи, их пароли и созданные Purchase Requests остаются данными конкретного Site.

Отдельный Role fixture для трёх ролей не нужен, пока роли существуют только как имена в Standard DocPerm собственного DocType: Frappe создаёт отсутствующие Role при синхронизации metadata. Тот же принцип уже используется в первом практикуме.

Последовательность развития модели описана в [`ROADMAP.md`](ROADMAP.md).
