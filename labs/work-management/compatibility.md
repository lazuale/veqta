# Work Management: compatibility contract

Work Management рассчитан на глубокую настройку конкретного `Site`, но стабильность продукта зависит от того, что Core сохраняет одинаковый смысл во всех установках.

Главный принцип:

> Site может расширять модель и настраивать процесс, но не должен переопределять семантику Core.

## Что считается совместимой настройкой

Организация может без форка продукта использовать штатные механизмы Frappe:

```text
Work Unit data
Work Type data
Roles / User Permissions
Assign To / ToDo
Assignment Rule
Workflow
Notifications
Custom Fields
Reports
Workspace
Client Script
Server Script
дополнительные DocType
extension Apps
REST / Webhook / hooks
```

Такая настройка может радикально менять конкретный бизнес-процесс, интерфейс и предметную область, пока базовый контракт `Work Unit`, `Work Type` и `Work Item` остаётся прежним.

## Что считается частью Core contract

К стабильной семантике Work Item относятся не только обычные поля состояния, но и четыре разных типа отношений:

```text
parent_work_item = часть другой Work Item
dependencies     = prerequisite Work Item
sources          = на основании чего возникла работа
references       = к каким предметным документам относится работа
```

Эти отношения не взаимозаменяемы и не должны переиспользоваться друг вместо друга.

## Что нельзя переопределять без потери совместимости

Технически Frappe позволяет менять metadata стандартных DocType через Customize Form и Property Setter. Work Management не запрещает сам механизм, но не считает совместимой конфигурацию, которая меняет фундаментальный контракт продукта.

К несовместимым изменениям относятся:

- изменение `fieldtype` Core field;
- использование Core field для другого смысла;
- удаление обязательного Core field;
- превращение обязательной фундаментальной связи в необязательную;
- удаление или переопределение канонических значений `status`;
- изменение смысла канонических значений `status` или `priority`;
- изменение семантики `parent_work_item`, `dependencies`, `sources` или `references`;
- использование `references` как замены hierarchy/dependencies;
- создание второй независимой модели ACL для Work Item;
- подмена `responsible_unit` другой сущностью, не означающей очередь или зону ответственности;
- добавление собственной параллельной модели исполнителей вместо штатного Frappe Assign To / ToDo без отдельной доказанной ответственности.

Если организации нужна дополнительная информация, добавляется Custom Field. Если нужна новая самостоятельная сущность — обычный DocType или capability. Существующее Core field не переиспользуется.

## Канонический status и локальный Workflow

Core использует стабильные состояния:

```text
Open
In Progress
Waiting
Done
Cancelled
```

Организация может иметь любое количество собственных workflow states:

```text
На проверке
На согласовании
Ожидает клиента
У руководителя
Готово к выпуску
```

Эти состояния относятся к локальному бизнес-процессу. При необходимости Workflow обновляет канонический `status`, чтобы общая семантика и отчётность продукта оставались стабильными.

Таким образом, Work Management не навязывает этапы конкретной организации и одновременно не теряет общий operational lifecycle.

## Queue, assignments и permissions

`responsible_unit` отвечает на вопрос, в какой организационной очереди или зоне ответственности находится Work Item.

Персональное выполнение выражается штатными Frappe Assignments / `ToDo`. Один Work Item может иметь ноль, один или несколько активных assignments.

```text
responsible_unit = queue ownership
Frappe Assignment = execution responsibility
```

`Work Unit` не является обязательной ACL-границей Core. Базовый доступ к Work Item задаётся Roles/DocPerm. Конкретный Site при необходимости может дополнительно применять User Permissions, Permission Levels, Workflow или другие штатные механизмы Frappe.

Если Site использует User Permission на `Work Unit`, это дополнительная политика ограничения данных конкретной установки. Она не меняет смысл `responsible_unit` и не превращает дерево Work Unit в отдельный permission engine продукта.

Assignment сам по себе не является альтернативной ACL-моделью Work Management. Доступ к Work Item остаётся ответственностью штатных permissions и sharing Frappe.

## Hierarchy и dependencies

`parent_work_item` означает только непосредственного родителя в декомпозиции работы. `dependencies` означает prerequisite: текущая Work Item зависит от указанной Work Item.

Эти связи не являются скрытым процессным движком:

- parent не наследует автоматически status, queue, assignments или dates от child;
- завершение child не закрывает parent;
- dependency не запрещает автоматически начать или завершить Work Item;
- dependency не переносит даты;
- Core не вычисляет critical path или scheduling.

Site может добавить более строгие правила через Workflow, Server Script или extension App, если они не меняют смысл самих Core relations.

Self-reference, duplicate dependency и циклы hierarchy/dependencies являются нарушением Core contract и не считаются допустимой Site customization.

Новая parent/dependency связь должна указывать на Work Item, доступную пользователю для чтения. Сама связь не выдаёт доступ к другой Work Item и не является ACL.

## Auto Repeat

Work Item использует штатный Frappe Auto Repeat для простой календарной повторяемости.

Новый экземпляр считается новой операционной работой, поэтому не наследует instance-specific состояние прошлого выполнения:

```text
status          → Open
waiting fields  → cleared
next_action     → cleared
started_at      → cleared
closed_at       → cleared
planned_start   → cleared
due_at          → cleared
parent_work_item → cleared
dependencies    → cleared
sources         → cleared
```

При этом сохраняются шаблонные свойства:

```text
subject / description
work_type
responsible_unit
priority
estimated_effort
references
```

Assignments не копируются как поле Work Item: для повторяемых назначений используется штатная конфигурация Auto Repeat / ToDo.

Site может расширять recurring behavior, но совместимая настройка не должна превращать старый экземпляр Work Item в источник lifecycle state нового экземпляра.

## Work Membership и permissions

`Work Membership` хранит организационный факт принадлежности пользователя к Work Unit и может использоваться для:

- фильтра выбора пользователей при назначении;
- отображения состава команды;
- аналитики;
- локальной проверки принадлежности назначаемого пользователя к рабочей зоне.

Он не заменяет Roles/User Permissions и не является источником прав доступа.

```text
Work Membership = organizational fact
Frappe permissions = access control
```

Это исключает две конфликтующие модели безопасности.

## Sources и references

`sources` и `references` являются частью Work Item и потому видимы пользователям, которым доступен сам Work Item.

Они не дают автоматического права читать target document. Каждый связанный документ продолжает защищаться собственными permissions.

При создании или изменении ссылки пользователь должен иметь право читать target document. Если сам факт связи является чувствительной информацией, такую ссылку нельзя хранить в Work Item с более широким доступом.

`sources` и `references` не используются для внутренней структуры Work Item: parent/child и prerequisite dependency имеют собственную фиксированную семантику.

## Site customization и обновления

Upstream Work Management гарантирует миграции для собственного стабильного контракта. Site-specific Custom Fields, Scripts, Workflows и Property Setters остаются ответственностью владельца Site.

При обновлении продукта совместимая Site-конфигурация должна продолжать работать без форка приложения. Если Site сознательно изменил семантику Core metadata, такая конфигурация выходит за поддерживаемый compatibility contract.

## Публичный API модели

Даже без отдельного SDK модель становится API для:

```text
Workflow
Reports
REST integrations
Server Scripts
Custom Fields
extension Apps
```

Поэтому после стабильного v1 следующие элементы нельзя менять незаметно:

- имена Core DocType;
- fieldnames;
- смысл полей;
- канонические значения status и priority;
- обязательные отношения;
- семантику `parent_work_item` и `dependencies`;
- семантику `sources` и `references`.

Breaking change требует явной миграции и причины, а не внутренней переработки ради удобства реализации.

## Критерий

Совместимая организация должна иметь возможность полностью настроить собственный типовой процесс, не меняя смысл Core.

Если для поддержки нового сценария приходится переименовывать или переосмысливать `Work Unit`, `Work Type`, `Work Item`, `status`, `parent_work_item`, `dependencies`, `sources` или `references`, сначала нужно проверить архитектуру: либо найден реальный недостаток Core, либо предметная ответственность ошибочно пытается попасть в универсальную модель.
