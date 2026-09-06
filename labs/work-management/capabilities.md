# Work Management: функциональный контракт v1

Work Management развивается в VEQTA Labs как прототип будущего самостоятельного open-source продукта управления операционной работой на Frappe Framework.

Готовность продукта определяется не количеством DocType, а тем, может ли пользователь пройти полный рабочий цикл после установки и обычной настройки `Site` без разработки собственного приложения.

`DocType`, controller, report или Workspace появляются только там, где они нужны для конкретной пользовательской возможности.

## Критерий готовности

Work Management v1 должен позволять организации:

```text
настроить структуру и доступ
↓
создать работу
↓
классифицировать и поместить её в очередь
↓
назначить исполнителей
↓
разбить крупную работу и выразить зависимости
↓
задать сроки и приоритет
↓
выполнять работу и взаимодействовать по ней
↓
видеть свою работу и очереди в готовых представлениях
↓
получать уведомления и контролировать просрочку
↓
завершить или переоткрыть работу
↓
восстановить историю
↓
получить операционную и управленческую отчётность
```

Это должно работать на одной стабильной модели Work Management и штатных механизмах Frappe без обязательного форка Core под конкретную компанию.

## Frappe как платформа продукта

Наличие механизма во Frappe ещё не означает, что возможность готова в Work Management.

Например, Frappe уже предоставляет `Kanban View`, но продукт считается имеющим Kanban только тогда, когда пользователь после установки Work Management получает понятный путь к доске, корректное поле колонок и пригодное рабочее представление.

Поэтому граница выглядит так:

```text
Frappe предоставляет механизм
+
Work Management поставляет модель, конфигурацию и UX
=
готовая возможность продукта
```

Work Management не создаёт свои workflow, assignment, permission, notification, reporting или integration engines там, где соответствующую ответственность уже закрывает Frappe.

## Функциональный контур v1

| Возможность | Что получает пользователь | Основа Frappe | Что обязан поставить Work Management |
| --- | --- | --- | --- |
| установка | приложение устанавливается на совместимый Frappe Site | App, Bench, `install-app`, `migrate` | воспроизводимую установку, зависимости, миграции и начальную конфигурацию |
| доступ | пользователи видят и изменяют только разрешённые данные | Users, Roles, DocPerm, User Permissions, sharing | стандартные роли продукта и проверенный permission contract |
| рабочие очереди | можно распределять работу по устойчивым зонам ответственности | Tree/NestedSet, Link | `Work Unit`, дерево очередей и готовые queue views |
| прямое создание | пользователь может сразу создать конкретную работу | Form View, REST API | полноценную форму `Work Item` и корректные validation |
| классификация | работу можно отнести к устойчивому виду | Link, standard DocType | `Work Type` без маршрутизации и отраслевой семантики |
| ручные назначения | одной работе можно назначить 0, 1 или несколько пользователей | Assign To / ToDo | использовать штатный assignment UX без собственного `assignee` |
| автоматические назначения | типовые документы можно распределять по пользователям автоматически | Assignment Rule | совместимость Work Item с Assignment Rule; не создавать свой routing engine |
| декомпозиция | крупную работу можно разбить на более мелкие исполнимые работы | Link / отдельная узкая модель | явную семантику parent/child между Work Item; `references` для этого не переиспользуются |
| зависимости | пользователь видит, какая работа зависит от другой или блокируется ею | Link / отдельная узкая модель | явную семантику work dependency без универсального relation engine |
| жизненный цикл | работа проходит общие состояния Open/In Progress/Waiting/Done/Cancelled | Select, controller | канонический `status`, timestamps и серверные инварианты |
| локальный процесс | организация может добавить собственные этапы и правила переходов | Workflow | совместимость канонического lifecycle с Site Workflow |
| приоритет и сроки | есть приоритет, планируемое начало и срок | стандартные поля DocType | единый контракт `priority`, `planned_start`, `due_at` |
| ожидание | видно, почему работа стоит и с какого момента | Form/List | `waiting_reason`, `waiting_since` и соответствующие views |
| повторяемая работа | календарно повторяющуюся работу не нужно создавать вручную | Auto Repeat | безопасный контракт копирования Work Item и очистки instance-specific состояния |
| взаимодействие | участники могут обсуждать работу и прикладывать материалы | Timeline, Comments, Communication, File | использовать штатную Form Timeline и attachments, не дублируя их |
| слежение | пользователь может получать изменения по интересующей работе | Document Follow, Notification | понятную конфигурацию follow/notifications и готовые типовые уведомления продукта |
| поиск и фильтрация | работа быстро находится по состоянию, типу, очереди, сроку и тегам | List View, filters, tags, Awesomebar | стандартные List settings и продуктовые точки входа |
| моя работа | пользователь сразу видит назначенные ему активные Work Item | ToDo, List/Report | готовое представление `My Work` |
| очередь | команда видит всю активную работу выбранной зоны | List/Report | готовое представление `Unit Queue` |
| неназначенная работа | видно, что находится в очереди без активного исполнителя | ToDo + Work Item | готовое представление `Unassigned Work` |
| контроль сроков | видно, что скоро просрочится и что уже просрочено | List, Report, Notification | `Due Soon`, `Overdue` и типовые уведомления |
| Kanban | работу можно вести визуально по состояниям | Kanban View | готовую доску по каноническому `status` |
| календарь | работу с датами можно видеть во времени | Calendar View | calendar configuration для Work Item |
| история | можно понять, что происходило с работой и когда | Track Changes, Version, Timeline, ToDo | достаточный стабильный контракт истории для пользовательского просмотра и аналитики |
| простые отчёты | администратор может строить выборки без кода | Report Builder | корректно доступные поля и нейтральные сохранённые отчёты там, где они полезны |
| междокументная аналитика | руководство получает показатели потока работы | Script Report | permission-aware стандартные отчёты продукта |
| API | внешняя система может создавать, читать и изменять документы по правам пользователя | REST API / RPC | стабильную документированную модель и отдельные business methods только там, где обычного CRUD недостаточно |
| исходящие события | Work Management можно связать с внешними системами | Webhook, hooks | не создавать integration bus; документировать поддерживаемые события и контракты |
| локальная настройка | компания может добавить поля, Workflow, Notifications и представления | Customize Form, Custom Fields, Workflow, Workspace | сохранять стабильную семантику Core и не требовать форка для типовых изменений Site |
| массовая работа с данными | администратор может переносить или загружать большие наборы записей | Data Import / Bench data-import | не создавать собственный импортёр без отдельной необходимости |
| обновление | новая версия App корректно обновляет существующий Site | `bench migrate`, patches | миграции для breaking schema/data changes и проверку upgrade path |
| проверяемость | критические контракты продукта воспроизводимо тестируются | Frappe test runner | automated tests для собственных инвариантов, permissions, views/contracts и миграций |

Отдельная модель intake, membership, time tracking, project management или SLA не является условием готовности Core v1. Такая модель появляется только после подтверждения самостоятельной ответственности, которую текущий контракт и штатные механизмы Frappe не закрывают.

## Обязательные интерфейсы продукта

Work Management v1 не должен после установки выглядеть как набор технических DocType в Awesomebar.

### Workspace

Продукт поставляет нейтральный Workspace как основную точку входа.

Минимальная структура:

```text
Work Management
├── My Work
├── Unit Queues
├── Unassigned Work
├── Due Soon
├── Overdue
├── Waiting
├── All Work
├── Work Types
├── Work Units
├── Reports
└── Administration
```

First-party capabilities добавляют свои входы только при наличии самостоятельной пользовательской задачи. Workspace не должен превращаться в меню всех внутренних DocType.

### Work Item Form

Форма Work Item должна поддерживать полный рабочий цикл без собственного frontend:

```text
subject / description
classification
queue
status / priority
planned_start / due_at
waiting_reason
sources / references
work structure / dependencies

Frappe Form sidebar
→ Assign To
→ Share
→ Follow
→ Attachments

Frappe Timeline
→ comments
→ communications
→ edits / history
```

Work Management не дублирует элементы Frappe отдельными полями и панелями только ради собственного UI.

### Рабочие представления

Из коробки должны быть доступны как минимум:

```text
My Work
Unit Queue
Unassigned Work
Open Work
In Progress
Waiting
Due Soon
Overdue
Recently Updated
Completed Work
```

Для визуальной работы v1 использует штатные представления Frappe:

```text
List
Kanban
Calendar
```

Gantt не является критерием готовности v1. Он может появиться позже, если будет подтверждена самостоятельная задача временного планирования, для которой обычных дат и Calendar недостаточно.

Если штатное представление не выражает конкретную продуктовую задачу, сначала определяется недостающая ответственность. Отдельный frontend не создаётся только ради другого внешнего вида.

## Управленческая отчётность v1

Готовый продукт должен отвечать не только на вопрос «какие записи есть», но и на типовые вопросы управления потоком работы.

Минимальный набор отчётных возможностей:

```text
Work by Unit
Work by Type
Work by Assigned User
Open / In Progress / Waiting
Due Soon / Overdue
Unassigned Work
Completed Work
Created vs Completed by Period
Throughput by Period
Current Workload by Unit
Current Workload by Assigned User
```

Если подтверждённая история позволяет корректно вычислять показатели времени, продукт также может поставлять:

```text
Lead Time
Cycle Time
Time in Waiting
Reopen Count
Queue Transfers
```

Эти показатели не вычисляются из случайных технических diff, если Framework не гарантирует для них устойчивую семантику. При необходимости Work Management хранит собственные узкие бизнес-события, но не создаёт универсальный event bus.

## Стандартная настройка организации

После установки администратор должен иметь возможность собрать типовой рабочий контур без разработки:

```text
структура ответственности  → Work Unit data
виды работ                 → Work Type data
доступ                     → Roles / User Permissions
этапы процесса             → Workflow
ручные назначения          → Assign To
автоматические назначения  → Assignment Rule
уведомления                → Notification
дополнительные поля        → Customize Form / Custom Fields
дополнительные views       → стандартные Desk Views
входная web-форма          → Web Form, если она создаёт подходящий DocType
интеграции                 → REST / Webhook
```

Work Management не обещает выразить без кода любой уникальный процесс. Если штатных механизмов Frappe и функциональности продукта объективно недостаточно, специфическая ответственность реализуется обычным DocType, hook или extension App.

## Собственная модель появляется только из пользовательской возможности

Новый DocType или поле не являются самостоятельной целью.

Порядок решения:

```text
какую возможность должен получить пользователь?
↓
какая ответственность за ней стоит?
↓
есть ли уже штатный механизм Frappe?
├── да → продукт поставляет правильную конфигурацию и UX
└── нет
    ↓
достаточно ли Custom Field / Workflow / hook?
├── да → используем extension point
└── нет
    ↓
добавляем минимальную собственную модель
```

Поэтому:

- Assign To / ToDo закрывает персональные назначения — собственного `assignee` нет;
- Workflow закрывает локальные этапы — собственного workflow engine нет;
- Frappe Tags закрывают произвольные пользовательские метки — `Work Label` не нужен;
- `sources` и `references` закрывают связь работы с предметными документами, но не подменяют семантику parent/child и dependencies между Work Item;
- Report Builder закрывает простые отчёты, а Script Report используется только для расчётной или междокументной аналитики.

## Возможные first-party capabilities за пределами v1

Полноценность Work Management не означает, что продукт должен одновременно быть HR, Helpdesk, ECM, EAM, CRM и PPM.

Дополнительная first-party capability оправдана только когда она закрывает распространённую самостоятельную задачу и может не использоваться организациями, которым она не нужна.

Кандидатами для отдельной проверки могут быть:

```text
team membership
intake / request triage
documentary records
shift operations
operational locations
tracked assets
SLA / service operations
project planning
time tracking
```

Этот список не является roadmap и не обещает соответствующие DocType. Для каждого кандидата сначала доказывается отдельная ответственность и проверяется, не закрывает ли её уже Frappe или другой совместимый App.

Внешние предметные системы также могут оставаться владельцами своих данных:

```text
HRMS / Employee
CRM / Customer
ERP / Supplier / Contract
Helpdesk / Ticket
CMDB
production orders
quality records
legal cases
accounting dimensions
```

Work Management связывается с ними через `sources`, `references`, REST, Webhook или extension App.

## Граница v1

Work Management v1 считается функционально полным, когда новый Site после установки и настройки способен пройти нейтральный end-to-end сценарий:

```text
создание Work Item
→ классификация
→ очередь
→ назначение
→ декомпозиция / зависимости при необходимости
→ сроки и приоритет
→ выполнение и взаимодействие
→ Waiting при внешней зависимости
→ контроль сроков
→ Done / Cancelled / reopen
→ история
→ отчётность
```

При этом:

- типовой сценарий не требует собственного кода компании;
- пользователь получает готовые Workspace, формы, views и reports, а не только схему данных;
- Core не зависит от конкретной отрасли или оргструктуры;
- стандартные возможности Frappe используются вместо параллельных движков;
- permissions работают одинаково из Form, List, Report и API;
- обязательное состояние App воспроизводимо устанавливается и мигрирует;
- собственные критичные контракты покрыты automated tests;
- Site может расширять процесс без переопределения смысла базовых сущностей.

## Механизмы Frappe, на которых строится контракт

- Desk и стандартные Views: https://docs.frappe.io/framework/user/en/desk
- List View: https://docs.frappe.io/framework/user/en/api/list
- Workspace: https://docs.frappe.io/framework/user/en/desk/workspace
- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- Assign To / ToDo implementation v16: https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py
- Assignment Rule implementation v16: https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/assignment_rule/assignment_rule.py
- Notifications: https://docs.frappe.io/framework/notifications
- Web Form: https://docs.frappe.io/framework/user/en/web-form
- REST API: https://docs.frappe.io/framework/user/en/api/rest
- Webhooks: https://docs.frappe.io/framework/user/en/guides/integration/webhooks
- Script Report: https://docs.frappe.io/framework/user/en/desk/reports/script-report
- Auto Repeat: https://docs.frappe.io/erpnext/auto-repeat
- Document Follow: https://docs.frappe.io/erpnext/document-follow
- Migrations: https://docs.frappe.io/framework/user/en/guides/deployment/migrations
- Bench data import: https://docs.frappe.io/framework/user/en/guides/data/import-large-csv-file

Этот документ задаёт функциональную границу продукта. Точная схема Core фиксируется отдельно в [Data Model v1](data-model-v1.md). Новая capability получает собственный контракт только после подтверждения её ответственности.
