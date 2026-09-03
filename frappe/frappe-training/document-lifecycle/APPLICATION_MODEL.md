# Модель учебного приложения

Практикум использует один предметный объект — внутреннюю заявку на закупку `Purchase Request`. Модель намеренно маленькая: цель не в количестве DocTypes, а в том, чтобы на одном понятном Document увидеть разницу между предметным состоянием, `Workflow` и системным `docstatus`.

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

`subject` используется как `Title Field`: системный `name` остаётся стабильной identity, а заголовок можно исправлять без переименования Document.

## Кто является заявителем

Отдельного поля `requester` в практикуме нет.

Для учебного сценария принято:

```text
requester = Document.owner
```

Этого достаточно, пока пользователь создаёт заявку только от собственного имени. Если позже появится сценарий «создать за другого сотрудника», модель потребует отдельного анализа: `owner` и бизнес-понятие requester перестанут совпадать.

## Состояния

Практикум использует один Standard field:

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

В начале практикума это обычный предметный `Select`. Позже тот же field становится `Workflow State Field`.

Отдельный обязательный `workflow_state` не создаётся: Frappe позволяет использовать уже существующее поле, если оно указано в Workflow. Если подходящего поля нет, Framework умеет создать `Custom Field` автоматически, но в нашем App такой второй источник состояния не нужен. См. [`Workflow.create_custom_field_for_workflow_state()` в v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/workflow.py).

## Роли

Используются три прикладные роли:

```text
PLT Requester
PLT Approver
PLT Senior Approver
```

Они отвечают за возможности работать с `Purchase Request` через обычные DocType Permissions. Право выполнить конкретный процессный переход задаётся отдельно в `Workflow Transition`.

К концу практикума permission-модель выглядит так:

| Role | Read | Create | Write | Submit | Cancel | Amend |
|---|---:|---:|---:|---:|---:|---:|
| `PLT Requester` | yes | yes | yes | no | no | yes |
| `PLT Approver` | yes | no | yes | yes | yes | no |
| `PLT Senior Approver` | yes | no | yes | yes | no | no |

Эта матрица развивается по этапам; лишние права не выдаются заранее.

## Маршрут согласования

Финальный процесс:

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

После появления транзакционного требования:

```text
PLT Approved  → docstatus 1
PLT Cancelled → docstatus 2
```

До этого `PLT Approved` остаётся обычным workflow-state с `docstatus 0`.

Это принципиально: название `Approved` само по себе не делает Document Submitted.

## Self approval

Пользователь может одновременно иметь `PLT Requester` и `PLT Approver`, но не должен одобрять собственную заявку.

Frappe уже предоставляет transition-level настройку `Allow Self Approval`. В v16.33.0 серверная проверка сравнивает текущего пользователя с `doc.owner`; поэтому она подходит именно потому, что в учебной модели requester совпадает с owner. См. [`has_approval_access()`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

Собственный validator для этого правила не нужен.

## Cancel и Amend

После того как окончательное согласование становится Submitted fact:

```text
Approved → Cancelled
```

идёт штатным `doc.cancel()` через Workflow, потому что `apply_workflow()` выбирает Document operation по `docstatus` следующего Workflow State. Переход `1 → 2` обрабатывается как Cancel, а не как обычный update-after-submit. Источник: [`apply_workflow()` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

После Cancel заявитель получает отдельное право `Amend` и создаёт новую draft-версию с `amended_from`, не переписывая отменённый факт.

## Что принадлежит App

В финальном состоянии App должен воспроизводимо поставлять:

```text
Purchase Request Standard metadata
DocType Permissions
Workflow Action Master для собственных действий
Workflow State records
Workflow с states/transitions/conditions
автоматические tests
```

Пользователи, их пароли и созданные Purchase Requests остаются данными конкретного Site.

Role fixture для трёх ролей не нужен, пока роль существует только как имя в Standard DocPerm собственного DocType: Frappe создаёт отсутствующие Role при синхронизации metadata. Это тот же принцип, который уже используется в первом практикуме.

Последовательность развития модели описана в [`ROADMAP.md`](ROADMAP.md).
