# 09. Single, Tree, Submittable и Virtual DocType

Эта глава разбирает четыре специальных режима **Frappe Framework 16**, которые существенно меняют поведение обычного DocType:

```text
Single
Tree
Submittable
Virtual
```

Цель — понять не только, где поставить соответствующую галочку, но и **что после этого меняется в хранении данных, интерфейсе и lifecycle документа**.

Проверено: **2026-08-30**.

---

## 1. Сначала сравнение

Обычный DocType можно представить так:

```text
DocType
   ↓
собственная таблица tab<DocType>
   ↓
много Documents
   ↓
обычный Form/List lifecycle
```

Специальные режимы меняют эту модель.

| Режим | Главное отличие |
|---|---|
| `Single` | существует только один экземпляр; значения лежат в `tabSingles` |
| `Tree` | документы образуют иерархию и обслуживаются Nested Set Model |
| `Submittable` | появляется lifecycle Draft → Submitted → Cancelled |
| `Virtual` | собственной таблицы данных нет; источник данных реализует controller |

Важно:

> Это не четыре варианта одной и той же задачи.

Каждый режим решает совершенно разную проблему.

---

# Часть I. Single DocType

## 2. Что такое Single DocType

Обычный DocType предполагает множество документов:

```text
Customer
├── CUST-0001
├── CUST-0002
└── CUST-0003
```

Но некоторые данные существуют в системе только в одном экземпляре.

Например:

```text
Application Settings
System Settings
Integration Settings
```

Создавать для них список записей бессмысленно.

Для этого во Frappe существует:

```text
Is Single
```

Официальная документация определяет Single DocType как DocType, имеющий **только один экземпляр**.

---

## 3. Типичный пример Single

Допустим, приложению нужны настройки:

```text
Application Settings
├── Default Language
├── Default Timezone
├── Enable Notifications
└── Retention Days
```

Нам не нужны документы:

```text
SETTINGS-001
SETTINGS-002
SETTINGS-003
```

Нужен один экран:

```text
Application Settings
────────────────────────
Default Language: English
Default Timezone: Europe/Amsterdam
Enable Notifications: ✓
Retention Days: 90
```

Это классический случай `Single`.

---

## 4. У Single нет обычной таблицы DocType

Это принципиальное отличие.

Обычный DocType:

```text
Customer
    ↓
tabCustomer
```

Single DocType:

```text
Application Settings
    ↓
tabSingles
```

Отдельная таблица:

```text
tabApplication Settings
```

для хранения его единственного документа не создаётся.

Официальная документация прямо указывает, что значения Single DocTypes хранятся в общей таблице:

```text
tabSingles
```

---

## 5. Схема `tabSingles`

Основная идея:

```text
doctype | field | value
```

Например логически:

```text
Application Settings | default_language     | en
Application Settings | enable_notifications | 1
Application Settings | retention_days       | 90
```

То есть Single хранится не как одна обычная строка документа, а как набор значений его полей.

---

## 6. Получение Single через Document API

Для обычного документа:

```python
frappe.get_doc("Customer", "CUST-0001")
```

Нужны:

```text
DocType + name
```

Для Single:

```python
settings = frappe.get_doc("Application Settings")
```

`name` указывать не требуется.

Официальный Document API отдельно поддерживает такой вызов для Single DocType.

---

## 7. Когда Single подходит

Хорошие кандидаты:

```text
общесистемные настройки приложения
единственная конфигурация интеграции
настройки поведения модуля
глобальные значения по умолчанию
```

Ключевой вопрос:

> Может ли существовать более одного независимого экземпляра этих данных?

Если ответ уверенно:

```text
нет
```

— Single может быть подходящим вариантом.

---

## 8. Когда Single НЕ подходит

Плохие кандидаты:

```text
Department
Customer
Project
Warehouse
Device
Contract
```

если таких сущностей может быть несколько.

Также опасная ошибка:

> «Сейчас запись одна, поэтому сделаем Single».

Нужно смотреть на **смысл модели**, а не на текущее количество строк.

Например сегодня организация использует одного поставщика, но сущность `Supplier` от этого не становится Single.

---

## 9. Single — это не справочник из одной записи

Это важное различие.

Если сущность концептуально множественная:

```text
Currency
Department
Location
```

но сейчас создана одна запись — используется обычный DocType.

Single означает:

```text
сам тип данных по определению singleton
```

---

## 10. Single и интерфейс

Для Single нет смысла в обычном List View вида:

```text
Application Settings List
```

потому что список всегда содержал бы одну запись.

Практически пользователь открывает сразу единственную форму настроек.

Это одна из причин, почему Single удобен для configuration screens.

---

# Часть II. Tree DocType

## 11. Что такое Tree DocType

Иногда документы одного DocType образуют иерархию:

```text
Company
└── Division
    ├── Department A
    └── Department B
```

или:

```text
Category
├── Hardware
│   ├── Computers
│   └── Monitors
└── Software
```

Для таких моделей во Frappe существует:

```text
Is Tree
```

Frappe создаёт для такого DocType Tree View и использует **Nested Set Model** для хранения иерархии.

---

## 12. Tree — не просто красивый View

Ошибочно думать:

```text
Is Tree
=
показывать список лесенкой
```

На самом деле меняется модель работы документа.

Tree DocType использует структуру Nested Set.

В ней важны поля:

```text
parent field
old_parent
lft
rgt
```

Иерархия поддерживается Framework при добавлении и перемещении узлов.

---

## 13. Parent field

Дерево должно знать непосредственного родителя узла.

Условно:

```text
Category
name = Computers
parent_category = Hardware
```

В v16 nested-set код по умолчанию использует convention:

```text
parent_<scrubbed_doctype>
```

Например для:

```text
Item Group
```

логическое имя parent-поля будет строиться вокруг имени DocType.

При необходимости controller может определить собственное:

```python
nsm_parent_field
```

---

## 14. `old_parent`

Nested Set должен понимать, поменялся ли родитель документа.

Для этого используется значение старого parent:

```text
old_parent
```

Если узел перенесли:

```text
Hardware
└── Computers
```

в:

```text
Equipment
└── Computers
```

Framework должен перестроить соответствующие nested-set границы.

---

## 15. `lft` и `rgt`

Nested Set Model использует числовые границы:

```text
lft
rgt
```

Упрощённый пример:

```text
Root           1 ---------------- 10
Hardware       2 ------- 7
Computers      3 -- 4
Monitors       5 -- 6
Software       8 -- 9
```

У предка диапазон содержит диапазоны потомков.

Это позволяет эффективно получать:

```text
ancestors
 descendants
subtree
```

без рекурсивного обхода parent-ссылок для каждого уровня.

---

## 16. Что происходит при перемещении узла

Если узел меняет parent, недостаточно изменить одно поле:

```text
parent_category
```

Framework также должен пересчитать nested-set индексы.

Код `version-16/frappe/utils/nestedset.py` выполняет операции над `lft/rgt` при:

```text
добавлении узла
перемещении узла
удалении
перестроении дерева
```

Поэтому прямое ручное обновление tree-таблицы через SQL особенно опасно.

---

## 17. Tree View

Для DocType с `Is Tree` Framework предоставляет Tree View.

Пользователь видит структуру примерно так:

```text
▼ Root
   ▼ Hardware
      Computers
      Monitors
   ▼ Software
      Operating Systems
```

Это отдельное представление тех же документов.

Tree View можно дополнительно настраивать через:

```text
<doctype>_tree.js
```

для Standard DocType приложения.

---

## 18. NestedSet controller

В Framework существует класс:

```python
frappe.utils.nestedset.NestedSet
```

Он расширяет обычный `Document` поведением дерева.

Среди доступных возможностей:

```python
doc.get_parent()
doc.get_children()
doc.get_ancestors()
```

а также Framework-level функции получения descendants/ancestors и rebuild tree.

В исходном коде v16 Custom DocType с `is_tree` автоматически получает `NestedSet` как controller base.

Для Standard DocType приложения tree-поведение должно быть согласовано с его controller.

---

## 19. Когда Tree подходит

Хороший критерий:

> Объекты одного типа действительно могут быть родителями и детьми объектов того же типа?

Примеры:

```text
категории
организационные подразделения
иерархические справочники
папки
дерево счетов
```

---

## 20. Когда Tree НЕ подходит

Не надо включать `Is Tree`, если нужна просто связь:

```text
Project → Tasks
```

Это не дерево одного DocType.

Также не каждое отношение parent/child означает Nested Set.

Например:

```text
Order
└── Order Items
```

— это Child Table, а не Tree.

---

## 21. Tree vs Child Table

Сравним.

### Child Table

```text
Order
└── Order Item
```

разные DocTypes, child принадлежит parent.

### Tree

```text
Category
└── Category
    └── Category
```

один и тот же DocType образует иерархию.

Кратко:

```text
Child Table = composition
Tree        = hierarchy внутри одного типа
```

---

# Часть III. Submittable DocType

## 22. Что означает `Is Submittable`

Обычный документ можно создавать и изменять обычным `save()`.

Но для некоторых документов нужен формальный lifecycle:

```text
Draft
   ↓
Submitted
   ↓
Cancelled
```

Для этого в DocType включается:

```text
Is Submittable
```

---

## 23. Системное поле `docstatus`

Frappe хранит состояние transaction lifecycle в системном поле:

```text
docstatus
```

Возможны три значения:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Это **не обычное пользовательское поле Status**.

---

## 24. Не Submittable документ

Если DocType не является Submittable:

```text
docstatus = 0
```

и обычный документ остаётся в Draft lifecycle.

При этом у него совершенно спокойно может быть собственное поле:

```text
status = Open / Closed
```

То есть:

```text
status
≠
docstatus
```

---

## 25. Submittable document lifecycle

Для Submittable документа:

```text
Draft (0)
   │ submit
   ▼
Submitted (1)
   │ cancel
   ▼
Cancelled (2)
```

Это системная модель Framework.

---

## 26. Что меняется после Submit

Submitted document считается зафиксированным.

В обычной ситуации его нельзя свободно редактировать как Draft.

Это и есть основная причина существования Submit:

```text
Save
=
редактируемая рабочая версия

Submit
=
формально зафиксированный документ
```

---

## 27. `Allow on Submit`

Иногда отдельное поле всё-таки должно оставаться изменяемым после Submit.

Для DocField существует настройка:

```text
Allow on Submit
```

Она разрешает изменение именно этого поля у Submitted document.

Это исключение, а не способ сделать весь submitted документ снова обычной редактируемой записью.

---

## 28. Отдельные permissions

У Frappe существуют отдельные permission types для операций:

```text
Submit
Cancel
Amend
```

Поэтому право:

```text
Write
```

не означает автоматически право Submit или Cancel.

Эту модель подробно разберём в разделе permissions.

---

## 29. Server API

На сервере Document предоставляет операции:

```python
doc.submit()
doc.cancel()
```

Они меняют lifecycle через штатный Document flow, а не просто присваивают число `docstatus`.

Не следует делать так:

```python
doc.docstatus = 1
```

как замену штатному Submit lifecycle.

---

## 30. Когда Submittable подходит

Использовать его стоит, когда существует реальная семантика:

```text
черновик
→
официально зафиксирован
→
при необходимости отменён
```

Типичные классы документов:

```text
транзакционные документы
утверждённые записи
официальные операции
документы, после фиксации которых данные нельзя тихо переписать
```

---

## 31. Когда Submittable не нужен

Плохая причина:

> «У нас есть статус Done».

Если сущность просто проходит рабочие состояния:

```text
New
In Progress
Waiting
Done
```

это ещё не означает необходимость `docstatus`.

Рабочий lifecycle часто лучше выражается:

```text
Status
Workflow
```

а Submit нужен именно для **неизменяемой фиксации transaction record**.

---

## 32. Submittable vs Workflow

Это разные механизмы.

### Submittable

```text
Draft → Submitted → Cancelled
```

системный transaction lifecycle.

### Workflow

```text
New → Review → Approved → Closed
```

настраиваемые бизнес-состояния и переходы.

Workflow может использовать `docstatus` в своих состояниях, но одно не является синонимом другого.

Подробно это разберём позже в главе Workflow.

---

## 33. Amendment

Для Cancelled Submittable document Frappe поддерживает модель Amendment.

Упрощённо:

```text
Original
Submitted
   ↓
Cancelled
   ↓
Amended document
```

При amendment сохраняется связь с исходным документом через:

```text
amended_from
```

Эта тема вместе с точными правилами изменения `docstatus` будет подробно разобрана в следующей главе.

---

# Часть IV. Virtual DocType

## 34. Что такое Virtual DocType

Virtual DocType — самый необычный режим из этой четвёрки.

Обычная схема:

```text
DocType
   ↓
таблица Site DB
   ↓
Document
```

Virtual:

```text
DocType metadata
   ↓
Frappe UI / permissions / API
   ↓
Custom controller
   ↓
внешний или иной источник данных
```

Главное:

> Для данных Virtual DocType Frappe не создаёт обычную таблицу в Site database.

---

## 35. Зачем нужен Virtual DocType

Он позволяет использовать Frappe как UI/application layer над данными, которые живут не в стандартной таблице Frappe.

Официальная документация приводит варианты:

```text
external API
secondary database
JSON file
CSV file
другой backend
```

---

## 36. Что сохраняется от обычного DocType

Несмотря на внешний data source, Frappe может продолжать предоставлять:

```text
Form UI
List UI
resource API
roles
permissions
metadata
```

Для конечного пользователя Virtual DocType может выглядеть почти как обычный.

---

## 37. Что исчезает

Исчезает главное автоматическое предположение:

```text
Document data
=
строка tab<DocType> в Site DB
```

Поэтому обычный database CRUD должен быть заменён controller-реализацией.

---

## 38. Controller Virtual DocType

Официальный пример Virtual DocType реализует методы вроде:

```python
db_insert()
load_from_db()
db_update()
delete()
get_list()
get_count()
get_stats()
```

Точный набор зависит от того, какие операции должен поддерживать Virtual DocType и его источник данных.

То есть поставить галочку:

```text
Is Virtual
```

недостаточно, если не реализован соответствующий data access layer.

---

## 39. Пример архитектуры Virtual DocType

Допустим, данные находятся во внешней системе:

```text
External API
   │
   ├── EXT-001
   ├── EXT-002
   └── EXT-003
```

Создаём:

```text
External Record
Is Virtual = ✓
```

Controller:

```text
get_list()
    ↓
GET external API

load_from_db()
    ↓
GET external API /<id>

db_update()
    ↓
PUT external API /<id>
```

Для пользователя:

```text
Frappe List View
Frappe Form View
```

но источник истины находится снаружи.

---

## 40. `frappe.db.*` и Virtual DocType

Это критически важно.

Официальная документация отдельно предупреждает:

```text
frappe.db.*
```

работает с **database connection текущего Site**.

Если Virtual DocType хранится во внешней PostgreSQL, API или файле, обычный:

```python
frappe.db.get_value(...)
```

не превращается автоматически в запрос к этому внешнему источнику.

Доступ к data source реализует сам controller.

---

## 41. REST API Virtual DocType

Одна из сильных сторон механизма: стандартные resource API Frappe совместимы с Virtual DocTypes при корректно реализованном controller.

Концептуально:

```text
GET /api/resource/External Record
```

может выглядеть для клиента так же, как запрос обычного DocType,

хотя данные реально приходят из другого backend.

---

## 42. Virtual — не способ избежать проектирования базы

Плохая причина:

> «Не хочется создавать таблицу».

Если данные являются нормальной частью приложения и должны жить в Site database, обычный DocType почти всегда проще.

Virtual добавляет ответственность:

```text
CRUD implementation
ошибки внешнего источника
latency
pagination
filtering
permissions interaction
transaction consistency
availability
```

Поэтому он нужен, когда внешний data source — **реальное требование**, а не попытка обойти ORM.

---

## 43. Virtual и производительность

Обычный List View ожидает операции вроде:

```text
filter
sort
pagination
count
```

Если Virtual DocType тянет данные из медленного API, controller должен разумно реализовать эти операции.

Иначе внешне обычный Frappe List может оказаться очень медленным.

То есть Virtual переносит часть ответственности Framework на разработчика data adapter.

---

# Часть V. Сравниваем четыре режима

## 44. Где физически находятся данные

### Normal

```text
tabMy DocType
```

### Single

```text
tabSingles
```

### Tree

```text
tabMy Tree DocType
+
lft/rgt/parent structure
```

### Submittable

```text
tabMy DocType
+
docstatus lifecycle
```

### Virtual

```text
не в обычной tabMy DocType
↓
controller-defined source
```

---

## 45. Что именно меняется

| Режим | Storage | UI | Lifecycle |
|---|---|---|---|
| Normal | собственная таблица | List/Form | обычный Save |
| Single | `tabSingles` | одна Form | обычный Save |
| Tree | собственная таблица + Nested Set | List/Form/Tree | tree maintenance |
| Submittable | собственная таблица | List/Form | Draft/Submit/Cancel |
| Virtual | внешний/custom source | Frappe views | controller-defined persistence |

---

## 46. Эти режимы отвечают на разные вопросы

### Single

```text
Сколько экземпляров сущности существует?
```

Ответ:

```text
ровно один
```

### Tree

```text
Есть ли иерархия между документами одного типа?
```

### Submittable

```text
Нужна ли формальная неизменяемая фиксация документа?
```

### Virtual

```text
Должны ли данные жить не в обычной таблице Frappe?
```

---

## 47. Поэтому режимы нельзя выбирать по внешнему виду

Неправильная логика:

```text
хочу дерево в интерфейсе
→ Tree
```

Сначала нужно убедиться, что сама модель действительно иерархическая.

Неправильно:

```text
хочу кнопку подтверждения
→ Submittable
```

Сначала определить, нужен ли transaction lifecycle или достаточно Workflow action.

Неправильно:

```text
настройка сейчас одна
→ Single
```

Нужно понять, может ли экземпляров быть несколько концептуально.

Неправильно:

```text
данные сложные
→ Virtual
```

Virtual связан с источником хранения, а не со сложностью модели.

---

# Часть VI. Практический выбор

## 48. Алгоритм выбора

Начинаем с обычного DocType.

```text
Нужен ровно один экземпляр?
        │
        ├── да → Single
        │
        └── нет
             ↓
Документы одного типа образуют иерархию?
        │
        ├── да → Tree
        │
        └── нет
             ↓
Нужен формальный Draft → Submitted → Cancelled?
        │
        ├── да → Submittable
        │
        └── нет
             ↓
Данные должны жить во внешнем/custom source?
        │
        ├── да → Virtual
        │
        └── нет → Normal DocType
```

Это упрощённая схема: некоторые возможности технически могут пересекаться, но выбирать режим следует по главной семантической потребности.

---

## 49. Примеры

### Настройки приложения

```text
Application Settings
```

→ `Single`.

### Иерархия категорий

```text
Category
```

→ `Tree`.

### Официально фиксируемая заявка/операция

если после утверждения запись должна стать transaction-like immutable document:

→ `Submittable`.

### Объекты внешней системы

```text
External Device
```

если источник истины — внешний API и данные не должны копироваться в локальную таблицу:

→ `Virtual`.

### Обычный справочник

```text
Department
```

→ Normal DocType.

---

# Часть VII. Типичные ошибки

## 50. Single вместо нормальной сущности

Проблема:

```text
"Пока запись одна"
```

не означает singleton-модель.

Проектировать нужно по смыслу данных.

---

## 51. Tree вместо связи разных сущностей

Плохая модель:

```text
Project
└── Task
```

как Tree одного DocType.

Если это разные типы объектов, обычно нужны разные DocTypes и Link/Child relation.

---

## 52. Submittable для любого статуса

Плохая логика:

```text
есть Open/Done
→ включаем Submit
```

`docstatus` — не универсальный workflow status.

---

## 53. Virtual как premature abstraction

Плохая логика:

```text
"Вдруг потом будет другая база"
```

→ сразу Virtual.

Это добавляет много кода и operational complexity без текущей необходимости.

---

## 54. Прямое SQL-редактирование Tree

Tree хранит не только parent field, но и nested-set индексы.

Ручное:

```sql
UPDATE ... SET parent_category = ...
```

без обновления `lft/rgt` может разрушить структуру дерева.

Работать следует через Document/NestedSet mechanisms.

---

## 55. Прямое изменение `docstatus`

Плохой подход:

```python
doc.docstatus = 1
doc.db_update()
```

как замена Submit.

Так можно обойти lifecycle events, validations и permissions.

Используется:

```python
doc.submit()
```

---

# Часть VIII. Что запомнить

## 56. Минимальная карта

```text
NORMAL
много обычных документов

SINGLE
один документ, tabSingles

TREE
иерархия документов одного типа, Nested Set

SUBMITTABLE
Draft → Submitted → Cancelled

VIRTUAL
Frappe metadata/UI/API над custom data source
```

---

## 57. Контрольные вопросы

После этой главы нужно уметь ответить:

1. Почему Single DocType не имеет обычной `tab<DocType>` таблицы данных?
2. Где хранятся значения Single?
3. Почему `frappe.get_doc()` для Single не требует `name`?
4. Чем Tree отличается от Child Table?
5. Для чего Tree нужны `lft` и `rgt`?
6. Почему нельзя бездумно менять parent Tree через SQL?
7. Какие значения принимает `docstatus`?
8. Чем `status` отличается от `docstatus`?
9. Почему `Write` не равно `Submit`?
10. Для чего существует `Allow on Submit`?
11. Почему Virtual DocType не создаёт обычную data table?
12. Какие методы приходится реализовывать controller Virtual DocType?
13. Почему `frappe.db.*` не начинает автоматически работать с внешним backend Virtual DocType?
14. Как понять, что нужен Virtual, а не обычный DocType?

Если ответы понятны, можно подробно разбирать transaction lifecycle.

---

## Официальные источники

- [Single DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype)
- [Single Type Doctype](https://docs.frappe.io/framework/user/en/guides/app-development/single-type-doctype)
- [Types of DocType](https://docs.frappe.io/framework/user/en/tutorial/types-of-doctype)
- [Tree API](https://docs.frappe.io/framework/user/en/api/tree)
- [Desk — Tree View](https://docs.frappe.io/framework/user/en/desk)
- [Docstatus or Document Status](https://docs.frappe.io/framework/doctypes/docstatus)
- [Document API](https://docs.frappe.io/framework/user/en/api/document)
- [Virtual DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype)
- [Nested Set implementation — Frappe v16](https://github.com/frappe/frappe/blob/version-16/frappe/utils/nestedset.py)
- [Document/controller loading — Frappe v16](https://github.com/frappe/frappe/blob/version-16/frappe/model/base_document.py)

---

Следующая глава: **`docstatus`, Submit, Cancel и Amendment**.