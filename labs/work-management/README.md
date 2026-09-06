# Work Management

Work Management — прототип управления операционной работой на Frappe Framework в рамках VEQTA Labs.

Текущая модель строится **native-first**: сначала используются штатные возможности Frappe v16, а собственный код появляется только после подтверждённого пробела, который нельзя закрыть конфигурацией Framework.

На этом этапе Work Management не является отдельным `App`. Прототип собирается на Site вокруг одного `Custom DocType` — `Work Item` — и штатных механизмов Frappe.

Точная схема `Work Item` описана в [Data Model v1](data-model-v1.md). Права доступа и граница штатных permissions описаны в [Security v1](security-v1.md). Рабочие представления, автоматизация, аналитика и Workspace собраны в [Configuration v1](configuration-v1.md). Пошаговая настройка на чистом Frappe v16 Site описана в [Setup Guide](setup-guide.md), а проверка фактического поведения на живом Site — в [Live Test Guide](live-test-guide.md).

## Граница текущей модели

```text
Work Item
├── subject
├── description
├── status
├── priority
├── due_date
└── links → Dynamic Link
```

Состояния работы:

```text
Open
Waiting
Closed
Cancelled
```

`status` описывает состояние самой работы. Персональная ответственность хранится отдельно штатным механизмом `Assign To / ToDo`.

```text
Work Item.status = состояние работы
Assign To / ToDo = кто отвечает за выполнение
```

Поэтому отдельного состояния `In Progress` нет. `Open` с активным assignment означает, что открытая работа уже взята исполнителем. `Waiting` используется, когда работа остаётся актуальной, но продолжение зависит от внешнего события: ответа, согласования, документа или решения.

## Что предоставляет Frappe

Текущая модель не дублирует возможности Framework собственными сущностями.

| Ответственность | Штатный механизм Frappe |
| --- | --- |
| назначение исполнителей | `Assign To` / `ToDo` |
| комментарии и история обсуждения | Timeline / Comments |
| файлы | Attachments |
| свободная классификация | Tags |
| письма и коммуникации | `Communication` |
| связи с произвольными документами | `Dynamic Link` |
| повторяющаяся работа | `Auto Repeat` |
| автоматическое распределение при необходимости | `Assignment Rule` |
| уведомления | `Notification` |
| очередь | List View |
| состояние потока | Kanban |
| сроки | Calendar View |
| простая отчётность | Report Builder |
| показатели | Number Card / Dashboard Chart |
| единая точка входа | Workspace |
| доступ | Roles / DocPerm |

`Assignment Rule` не является обязательной частью модели: базовый сценарий — общая очередь, из которой пользователь берёт работу через `Assign to me`.

## Связи и источники

Для связи Work Item с другими документами используется таблица `links` на стандартном child DocType `Dynamic Link`.

Письмо не копируется в собственное поле Work Item: стандартный `Communication` может быть связан с `Work Item` и отображаться в Timeline документа.

Отдельных `Work Source`, `Work Reference` и собственного relation engine в текущей модели нет.

## Что намеренно не входит в модель

В текущем ядре нет:

```text
Work Unit
Work Type
Work Source
Work Reference
Work Dependency
assignee
responsible_unit
parent_work_item
started_at
closed_at
closed_by
waiting_reason
waiting_since
planned_start
estimated_effort
SLA
progress
```

Эти сущности и поля не добавляются заранее. Они появятся только при самостоятельной ответственности, которую нельзя корректно выразить уже существующей моделью или штатным механизмом Frappe.

## Ограничения чистой конфигурации

Текущий прототип сознательно сохраняет границы нативного Frappe:

- `Work Item.status` и связанные `ToDo.status` независимы: закрытие или отмена Work Item само по себе не закрывает assignments;
- `Work Item.due_date` — срок самой работы, а `ToDo.date` — `Complete By` конкретного назначения; это разные даты;
- штатные DocPerm не выражают правило «может редактировать Work Item только назначенный пользователь» без дополнительного механизма;
- более строгие серверные инварианты не добавляются, пока реальная эксплуатация не покажет, что они необходимы.

Это не скрытые автоматизации продукта, а явные границы текущего native-first прототипа.

## Версия Frappe

Текущий ориентир — Frappe v16. Версионно-зависимое поведение проверяется по официальной документации и исходному коду ветки `version-16`.

Основные источники:

- [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Frappe v16 source](https://github.com/frappe/frappe/tree/version-16)
