# Управление работой

Управление работой — прототип управления операционной работой на Frappe Framework в рамках VEQTA Labs.

Текущая модель начинается со штатных возможностей Frappe v16. Собственный код появляется только после подтверждённого пробела, который нельзя закрыть конфигурацией Framework или официальной точкой расширения.

## Как устроен Lab

Живой прототип собирается на отдельном development Site с включённым `developer_mode` и минимальным Frappe App.

App здесь — не Product и не отдельная архитектурная надстройка. Это штатная единица разработки Frappe, которая позволяет:

- хранить standard DocType и другие обязательные metadata в коде;
- воспроизводимо переносить состояние между Site;
- использовать официальные controller methods, reports, hooks и другие extension points только там, где они реально понадобятся;
- проверять полный developer path Framework, а не только возможности site-level Customization.

Пользовательская эксплуатация прототипа не должна зависеть от включённого `developer_mode`. Режим разработчика нужен для проектирования и экспорта состояния App.

На текущем этапе App остаётся минимальным: он не вводит собственный API, scheduler, frontend, service layer или дополнительные предметные сущности.

Точная схема `Work Item` описана в [Модели данных v1](data-model-v1.md). Права доступа и их границы — в [Безопасности v1](security-v1.md). Рабочие представления, автоматизация, аналитика и Workspace — в [Конфигурации v1](configuration-v1.md). Сборка development Site описана в [Руководстве по настройке](setup-guide.md), а фактическая проверка — в [Руководстве по проверке](live-test-guide.md).

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

Технические значения состояния:

```text
Open
Waiting
Closed
Cancelled
```

В русском интерфейсе они отображаются как:

```text
Открыто
Ожидание
Закрыто
Отменено
```

`status` описывает состояние самой работы. Персональная ответственность хранится отдельно штатным механизмом `Assign To / ToDo`.

```text
Work Item.status = состояние работы
Assign To / ToDo = кто отвечает за выполнение
```

Поэтому отдельного состояния «В работе» нет. `Open` с активным назначением означает, что открытая работа уже взята исполнителем. `Waiting` используется, когда работа остаётся актуальной, но продолжение зависит от внешнего события: ответа, согласования, документа или решения.

## Русский интерфейс

Документация и пользовательская часть прототипа ориентированы на русский язык. При этом технические идентификаторы и значения модели остаются стабильными:

```text
DocType: Work Item
fieldnames: subject, description, status, priority, due_date, links
status values: Open, Waiting, Closed, Cancelled
priority values: Low, Medium, High
```

Русификация относится к отображению: меткам полей, переводимым значениям, названиям фильтров, доски, календаря, карточек, графиков и Workspace. Она не требует менять хранимые значения `status` или `priority`.

Для собственного имени `Work Item` используется штатный механизм перевода. Общие значения `status` и `priority` выводятся через переводы Frappe; недостающие строки при необходимости добавляются штатным способом, не меняя технические значения.

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
| расширенная отчётность при подтверждённой необходимости | standard Query / Script Report |
| показатели | Number Card / Dashboard Chart |
| расширяемый источник графика при подтверждённой необходимости | Dashboard Chart Source |
| единая точка входа | Workspace |
| доступ | Roles / DocPerm |
| прикладные серверные extension points | controller methods / hooks |

`Assignment Rule` не является обязательной частью модели: базовый сценарий — общая очередь, из которой пользователь берёт работу через `Assign to me`.

Наличие developer path не означает, что перечисленные точки расширения нужно использовать заранее. Они рассматриваются только после появления конкретной ответственности.

## Связи и источники

Для связи Work Item с другими документами используется таблица `links` на стандартном дочернем DocType `Dynamic Link`.

Письмо не копируется в собственное поле Work Item: стандартный `Communication` может быть связан с `Work Item` и отображаться в Timeline документа.

Отдельных `Work Source`, `Work Reference` и собственного механизма связей в текущей модели нет.

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

Эти сущности и поля не добавляются заранее. Developer mode не является основанием расширять предметную модель. Новый элемент появляется только при самостоятельной ответственности, которую нельзя корректно выразить уже существующей моделью или штатным механизмом Frappe.

## Текущие границы

Нужно различать два типа границ.

### Границы текущей конфигурации

- `Work Item.status` и связанные `ToDo.status` не синхронизируются автоматически;
- `Work Item.due_date` и `ToDo.date` имеют разную семантику;
- чистые DocPerm не выражают правило «редактировать Work Item может только назначенный пользователь»;
- простого Report Builder недостаточно для безопасной общей аналитики по назначениям всей команды;
- стандартная конфигурация Auto Repeat сама по себе не вычисляет относительный `due_date` нового Work Item.

### Что это не означает

Эти пункты не являются доказательством отсутствия возможностей во Frappe. Если соответствующее требование станет обязательным, сначала проверяется официальный developer extension point: controller method, permission hook, standard Report, Dashboard Chart Source или другой штатный механизм.

Например, Auto Repeat v16 вызывает `on_recurring` у создаваемого документа. Поэтому правило относительного срока при реальной необходимости должно сначала рассматриваться как controller extension, а не как повод писать собственный scheduler.

## Версия Frappe

Текущий ориентир — Frappe v16. Версионно-зависимое поведение проверяется по официальной документации и исходному коду конкретной версии.

Основные источники:

- [Frappe Apps](https://docs.frappe.io/framework/user/en/guides/basics/apps)
- [Developer Mode](https://docs.frappe.io/framework/user/en/guides/app-development/how-enable-developer-mode-in-frappe)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Translations](https://docs.frappe.io/framework/user/en/translations)
- [Frappe v16 source](https://github.com/frappe/frappe/tree/version-16)
