# 08. Child Table и Table MultiSelect

Эта глава разбирает два штатных механизма Frappe Framework 16 для хранения нескольких связанных значений внутри одного документа:

- `Table` + Child DocType;
- `Table MultiSelect`.

Цель — понять:

- чем Child DocType отличается от обычного DocType;
- что реально хранится в дочерней строке;
- как Frappe связывает child-row с родителем;
- как сохраняются и удаляются дочерние строки;
- зачем нужен `idx`;
- чем `Table` отличается от `Table MultiSelect`;
- когда Child Table подходит идеально;
- когда Child Table уже начинает ломать модель и нужна отдельная самостоятельная сущность.

Проверено: **2026-08-30**.

---

## 1. Зачем вообще нужны Child Tables

Обычный DocType хранит одно значение каждого поля:

```text
Request
├── subject
├── status
└── priority
```

Но иногда одному документу нужно принадлежать несколько однотипных строк.

Например:

```text
Order
└── Items
    ├── Product A × 2
    ├── Product B × 5
    └── Product C × 1
```

Или:

```text
Inspection
└── Measurements
    ├── Length = 10.2
    ├── Width  = 3.4
    └── Height = 2.8
```

Для этого Frappe использует Child DocType.

Официальная документация описывает Child DocType как DocType, который может существовать только в привязке к родительскому документу.

Концептуально:

```text
Parent Document
      │
      └── Table field
             │
             ▼
       Child Documents[]
```

---

## 2. Child DocType — это всё ещё DocType

Важно не воспринимать Child Table как массив произвольных словарей.

У дочерней строки есть собственный DocType со своими полями.

Например:

```text
DocType: Order Item
Is Child Table = ✓

Fields:
├── product   Link
├── qty       Float
├── price     Currency
└── amount    Currency
```

А в родительском `Order`:

```text
Field Type: Table
Fieldname: items
Options: Order Item
```

В результате форма `Order` получает таблицу строк `Order Item`.

---

## 3. Как создать Child DocType

При создании DocType включается:

```text
Is Child Table
```

В metadata это свойство соответствует:

```text
istable = 1
```

После этого DocType становится дочерним.

Типичный пример:

```text
Measurement Row
Is Child Table ✓

Fields:
parameter
value
unit
```

Затем в родительском DocType:

```text
Measurements
Field Type: Table
Options: Measurement Row
```

---

## 4. Поле `Table`

Поле типа:

```text
Table
```

не хранит весь массив дочерних данных в одной JSON-ячейке родителя.

В `Options` указывается имя Child DocType:

```text
Field Type: Table
Options: Order Item
```

Frappe понимает:

```text
Order.items
    ↓
child doctype = Order Item
```

При загрузке Document Framework отдельно получает child rows и собирает их в список `items`.

Для Python-кода это выглядит естественно:

```python
order = frappe.get_doc("Order", "ORD-0001")

for row in order.items:
    print(row.product, row.qty)
```

---

## 5. Что реально хранится в child-row

У Child Document есть специальные системные свойства:

```text
parent
parenttype
parentfield
idx
```

Они являются фундаментом связи с родителем.

Официальная документация перечисляет именно эти четыре свойства.

Разберём каждое.

---

## 6. `parent`

`parent` содержит `name` конкретного родительского документа.

Например:

```text
parent = ORD-0001
```

Это отвечает на вопрос:

> к какому конкретному документу принадлежит эта строка?

---

## 7. `parenttype`

`parenttype` содержит имя DocType родителя.

Например:

```text
parenttype = Order
```

Это отвечает на вопрос:

> документ какого типа является родителем?

---

## 8. `parentfield`

`parentfield` содержит `fieldname` поля `Table` в родительском DocType.

Например:

```text
parentfield = items
```

Это необходимо потому, что один и тот же Parent DocType теоретически может иметь несколько Table-полей.

Например:

```text
Order
├── items       → Order Line
└── bonuses     → Order Line
```

В таком случае `parentfield` позволяет Framework различить, в какой именно таблице находится конкретная строка.

---

## 9. `idx`

`idx` хранит порядок строки внутри таблицы.

Например:

```text
idx = 1
idx = 2
idx = 3
```

Это не просто косметический номер строки.

При загрузке Child Table Frappe сортирует дочерние записи по `idx`.

Если строки переставляются drag-and-drop, `idx` отражает новый порядок.

В текущем коде Framework при изменении списка дочерних документов индекс строк перенумеровывается начиная с 1.

---

## 10. Полная идентификация child-row

Связь можно представить так:

```text
Child Row
├── parent     = ORD-0001
├── parenttype = Order
├── parentfield= items
└── idx        = 3
```

То есть Frappe хранит достаточно информации, чтобы понять:

```text
какому документу
какого DocType
в каком Table-поле
и на какой позиции
```

принадлежит строка.

---

## 11. У Child Document есть и собственный `name`

У дочерней записи есть собственный технический `name`.

Но смысл этого `name` обычно отличается от идентификатора самостоятельного бизнес-документа.

Для пользователя child-row чаще воспринимается как часть родителя:

```text
Order ORD-0001
└── row 3
```

а не как отдельный объект, который нужно искать и открывать самостоятельно.

Поэтому не стоит проектировать Child Table как самостоятельный registry только потому, что технически у каждой строки существует `name`.

---

## 12. Child Documents загружаются вместе с родителем

Если загрузить:

```python
order = frappe.get_doc("Order", "ORD-0001")
```

Frappe получает родительскую запись и её дочерние таблицы.

Результат концептуально:

```python
{
    "doctype": "Order",
    "name": "ORD-0001",
    "items": [
        {
            "product": "A",
            "qty": 2
        },
        {
            "product": "B",
            "qty": 5
        }
    ]
}
```

То есть на уровне Document API таблица выглядит как обычный вложенный список документов.

---

## 13. Как Frappe загружает child rows из БД

Текущий код `Document` фильтрует строки Child DocType по тройке:

```text
parent
parenttype
parentfield
```

и сортирует:

```text
ORDER BY idx ASC
```

Концептуально запрос выглядит так:

```sql
SELECT *
FROM child_table
WHERE parent = 'ORD-0001'
  AND parenttype = 'Order'
  AND parentfield = 'items'
ORDER BY idx ASC
```

Это полезно понимать при диагностике данных и написании сложных запросов.

Но в прикладном коде предпочтительнее работать через Document API, а не вручную собирать child rows SQL-запросами.

---

## 14. Добавление строки через Python

Штатный способ:

```python
row = order.append("items", {
    "product": "Product A",
    "qty": 2,
})
```

Framework автоматически знает Child DocType из metadata Table-поля.

При создании child-row он выставляет:

```text
parent
parenttype
parentfield
```

а `idx` формируется по позиции строки.

Поэтому вручную заполнять эти системные поля в нормальной работе не требуется.

---

## 15. Добавление нескольких строк

Например:

```python
order.append("items", {
    "product": "A",
    "qty": 2,
})

order.append("items", {
    "product": "B",
    "qty": 5,
})

order.save()
```

В родительском Document:

```text
items[0]
items[1]
```

будут полноценными Child Documents.

---

## 16. Сохранение parent сохраняет и children

Это ключевое поведение.

Child Table является частью состояния родительского Document.

При вставке нового parent Frappe:

```text
1. сохраняет parent
2. вставляет child rows
```

При последующем `save()` Framework синхронизирует дочерние таблицы с текущим содержимым parent document.

Это означает:

> Child Table не нужно отдельно «сохранять» после обычного изменения родителя.

---

## 17. Что происходит при удалении строки из списка

Представим, в БД есть:

```text
row A
row B
row C
```

а в Document перед `save()` осталось:

```text
row A
row C
```

Текущий алгоритм `update_child_table()` определяет строки, которых больше нет в Document, и удаляет их из child table.

После этого оставшиеся строки обновляются или вставляются.

То есть parent document является источником актуального состава Child Table при обычном сохранении.

---

## 18. Child Table — часть lifecycle родителя

Это очень важное архитектурное свойство.

Если данные должны жить и изменяться именно вместе с родителем, Child Table подходит хорошо.

Например:

```text
Invoice
└── Invoice Items
```

или:

```text
Checklist
└── Checklist Rows
```

Но если строки должны иметь собственный lifecycle, отдельную очередь, permissions, assignment или ссылки из многих других сущностей — Child Table может быть неправильной моделью.

---

## 19. Простой критерий выбора

Хороший вопрос:

> существует ли эта строка сама по себе без родителя?

Если ответ:

```text
нет
```

Child Table — сильный кандидат.

Если ответ:

```text
да
```

скорее нужен обычный самостоятельный DocType.

---

## 20. Хорошие кандидаты на Child Table

Типичные примеры:

```text
строки документа
позиции заказа
измерения внутри акта
элементы конфигурации
контакты внутри конкретной сущности
локальные параметры
история значений, если она принадлежит только одному parent
```

Общее свойство:

```text
child имеет смысл только как часть parent
```

---

## 21. Плохие кандидаты на Child Table

Осторожно с сущностями вроде:

```text
Task
Employee
Contract
Vehicle
Customer
Project
Approval Request
```

если им нужны:

```text
собственный URL
собственная карточка
независимые permissions
собственный lifecycle
assignment
workflow
отчётность между разными parents
массовая работа
независимые ссылки из других DocTypes
```

В таком случае обычный DocType обычно правильнее.

---

## 22. Child Table не заменяет нормальную many-to-many модель

Представим:

```text
Project
↔
User
```

Если нам просто нужен небольшой список выбранных пользователей без дополнительных данных — может подойти Table MultiSelect.

Но если связь имеет собственные атрибуты:

```text
role
start_date
end_date
allocation
status
```

то сама связь уже становится сущностью.

Например:

```text
Project Member
├── project
├── user
├── role
├── allocation
└── start_date
```

Это может быть отдельный обычный DocType, если запись должна быть самостоятельной.

---

# Часть II. Table MultiSelect

## 23. Что такое `Table MultiSelect`

`Table MultiSelect` — штатный Field Type Frappe, который объединяет идею:

```text
Link
+
несколько значений
+
child table storage
```

В интерфейсе пользователь видит не полноценную grid-таблицу с `Add Row`, а поле, где можно выбрать несколько документов.

Например:

```text
Reviewers
[alice@example.com] [bob@example.com] [carol@example.com]
```

---

## 24. Но внутри это всё равно Child Table

Это критически важно.

`Table MultiSelect` не хранит строку типа:

```text
"Alice,Bob,Carol"
```

и не хранит JSON-массив в одном поле parent.

В `Options` Table MultiSelect указывается **Child DocType**.

Например:

```text
User Selection
Is Child Table ✓

Fields:
user → Link / User
```

В parent:

```text
reviewers
Field Type: Table MultiSelect
Options: User Selection
```

Фактическое хранение остаётся child rows.

---

## 25. Минимальная структура Table MultiSelect

Child DocType:

```text
Selected User
Is Child Table ✓

user
Field Type: Link
Options: User
Mandatory ✓
In List View ✓
```

Parent:

```text
Reviewers
Field Type: Table MultiSelect
Options: Selected User
```

Пользователь выбирает несколько `User`, а Framework создаёт соответствующие child rows.

---

## 26. Почему Link-поле child table должно быть явно определено

В текущем коде `DocField.get_link_doctype()` для `Table MultiSelect` ищет Link-поле внутри указанного Child DocType.

В частности Framework ориентируется на Link-поле, отмеченное для отображения в list view.

Поэтому child table для MultiSelect должна быть спроектирована однозначно.

Практически:

```text
Selected User
└── user
    Field Type = Link
    In List View = ✓
```

---

## 27. Table MultiSelect запрещает повтор одного значения

Штатный UI рассчитан на набор уникально выбранных документов.

То есть:

```text
Alice
Bob
Alice
```

не является нормальным сценарием Table MultiSelect.

Если одинаковый объект должен встречаться несколько раз с разными параметрами, нужна обычная Child Table.

---

## 28. Когда Table MultiSelect удобнее обычной Table

Если каждая строка содержит фактически только одну ссылку:

```text
User
Tag
Category
Region
Department
```

полноценная grid-таблица создаёт лишний UI.

Вместо:

```text
+ Add Row
----------------
User A
User B
User C
```

получаем компактный selector:

```text
[User A] [User B] [User C]
```

---

## 29. Когда Table MultiSelect НЕ подходит

Если у строки есть дополнительные значимые поля:

```text
User
Role
Allocation
Start Date
```

то Table MultiSelect скрывает важную структуру.

Правильнее обычная Table:

```text
Members
┌─────────┬──────────┬────────────┐
│ User    │ Role     │ Allocation │
├─────────┼──────────┼────────────┤
│ Alice   │ Reviewer │ 30%        │
│ Bob     │ Owner    │ 100%       │
└─────────┴──────────┴────────────┘
```

---

## 30. Table vs Table MultiSelect

| Требование | Table | Table MultiSelect |
|---|---:|---:|
| несколько строк | ✓ | ✓ |
| несколько полей в строке | ✓ | неудобно |
| одно Link-значение на строку | ✓ | ✓, оптимально |
| компактный selector | ✗ | ✓ |
| drag-and-drop строк | ✓ | не основной UX |
| визуальная grid-таблица | ✓ | ✗ |
| уникальный набор выбранных документов | вручную/правило | штатный сценарий |

---

## 31. Table MultiSelect нельзя воспринимать как Select

Обычный `Select` хранит одно значение из фиксированного списка:

```text
Low
Medium
High
```

`Table MultiSelect` хранит ссылки на реальные Documents.

То есть:

```text
Select
→ enum-подобное значение

Table MultiSelect
→ набор связей с Documents
```

---

## 32. Table MultiSelect vs несколько Link-полей

Плохая модель:

```text
reviewer_1
reviewer_2
reviewer_3
reviewer_4
```

Проблемы:

```text
фиксированное число участников
неудобные фильтры
дублирование metadata
сложная валидация
```

Если количество ссылок переменное, Table MultiSelect обычно чище.

---

# Часть III. UI и grid

## 33. Editable Grid

Child Table может отображаться как grid внутри формы.

Если включён Editable Grid, часть полей можно редактировать прямо в строках таблицы без открытия отдельной mini-form каждой строки.

Пример:

```text
Items
┌────────────┬─────┬────────┐
│ Product    │ Qty │ Price  │
├────────────┼─────┼────────┤
│ A          │  2  │ 100.00 │
│ B          │  5  │  30.00 │
└────────────┴─────┴────────┘
```

Какие поля видны в grid, зависит от metadata Child DocType, в частности `In List View` и layout-параметров.

---

## 34. Не все поля надо показывать в grid

Child DocType может иметь много полей, но grid должен оставаться читаемым.

Например:

```text
Product
Qty
Price
Amount
```

видим прямо в таблице.

А:

```text
Long Description
Internal Note
Additional Metadata
```

можно оставить внутри формы строки.

Это тот же принцип, что и List View обычного DocType.

---

## 35. Grid Page Length

DocType имеет настройку:

```text
Grid Page Length
```

Она влияет на отображение больших дочерних таблиц.

Если child rows десятки или сотни, UX таблицы уже становится отдельной задачей.

Большое количество строк — один из сигналов проверить, не превращаем ли мы независимый dataset в Child Table только ради удобства формы.

---

## 36. Rows Threshold for Grid Search

В Frappe 16 также существует настройка порога, после которого grid использует поиск по строкам.

Это полезно для больших дочерних таблиц.

Но техническая возможность работать с большой grid не означает, что любая огромная сущность должна быть Child Table.

---

# Часть IV. Client Script события

## 37. События строк Child Table

Form Scripts умеют реагировать на события дочерних таблиц.

Например:

```javascript
frappe.ui.form.on("Order Item", {
    items_add(frm, cdt, cdn) {
        // строка добавлена
    },

    items_remove(frm, cdt, cdn) {
        // строка удалена
    },

    items_move(frm, cdt, cdn) {
        // строка переставлена
    }
});
```

Также существует:

```text
before_{fieldname}_remove
form_render
```

---

## 38. Что такое `cdt` и `cdn`

В child event handlers часто встречаются:

```text
cdt
cdn
```

### `cdt`

Child DocType.

### `cdn`

`name` конкретной child row.

Например:

```javascript
const row = frappe.get_doc(cdt, cdn);
```

Так можно получить строку, вызвавшую событие.

---

## 39. Новое для v16: события Table MultiSelect

Официальная документация Form Scripts отдельно отмечает, что начиная с **Version 16** события:

```text
before_{fieldname}_remove
{fieldname}_add
{fieldname}_remove
```

работают также для `Table MultiSelect`.

Это хороший пример изменения, которое может отсутствовать в старых гайдах по v14/v15.

---

# Часть V. Server-side работа

## 40. Перебор children

Обычный код:

```python
for row in doc.items:
    validate_row(row)
```

Child rows доступны как объекты Document.

Можно обращаться:

```python
row.product
row.qty
row.idx
row.parent
```

---

## 41. `get_all_children()`

Framework умеет получить все child documents родителя через внутреннюю Document API.

Это используется самим Frappe для общих операций над дочерними строками.

Для прикладной логики чаще проще работать с конкретным table field:

```python
for row in doc.items:
    ...
```

потому что так код явно показывает, с какой таблицей он работает.

---

## 42. Child Table и validation

Если бизнес-правило относится ко всему документу, удобнее валидировать его на parent.

Например:

```python
def validate(self):
    if not self.items:
        frappe.throw("At least one item is required")

    total = sum(row.amount for row in self.items)
```

Это подчёркивает модель:

```text
parent + children
=
один агрегат
```

---

## 43. Не полагаться только на client-side validation

Как и для обычных полей, критическое правило должно проверяться server-side.

Например:

> один Product не должен встречаться дважды.

Можно показывать ошибку сразу в браузере, но окончательная гарантия должна жить на сервере, если правило действительно обязательно.

---

# Часть VI. Что происходит под капотом

## 44. Вставка нового документа

Упрощённо:

```text
parent.insert()
    │
    ├── db_insert(parent)
    │
    └── db_insert(child 1)
        db_insert(child 2)
        db_insert(child 3)
```

Framework сначала получает `name` родителя, затем child rows могут ссылаться на него через `parent`.

---

## 45. Последующий `save()`

Упрощённо:

```text
parent.save()
    │
    ├── update parent
    │
    └── update_children()
            │
            ├── удалить отсутствующие rows
            ├── обновить существующие
            └── вставить новые
```

Текущий код Frappe делает эту синхронизацию отдельно для каждого Table field.

---

## 46. Почему это важно

Это означает, что опасно делать параллельную произвольную запись в child table, не учитывая состояние parent Document.

Если затем родитель будет сохранён со своим текущим списком children, Framework синхронизирует БД с этим списком.

Нормальный путь:

```text
получить parent
→ изменить child list через Document API
→ сохранить parent
```

---

## 47. Rename parent обновляет `parent` у children

При переименовании документа Frappe обновляет ссылки дочерних строк на новый `name` родителя.

То есть:

```text
ORD-0001
→ rename → ORD-2026-0001
```

и child rows должны получить:

```text
parent = ORD-2026-0001
```

Framework имеет отдельную обработку child documents для Rename.

---

# Часть VII. Архитектурный выбор

## 48. Child Table как composition

Наиболее полезная mental model:

```text
Parent
◆──── Child
```

То есть Child является частью состава Parent.

Без parent он обычно не имеет самостоятельного бизнес-смысла.

Это ближе к composition, чем к обычной слабой ссылке.

---

## 49. Link как reference, Child Table как ownership

Сравним.

### Link

```text
Order ─────→ Customer
```

Customer существует самостоятельно.

Удаление/изменение Order не означает, что Customer должен исчезнуть.

### Child Table

```text
Order
└── Order Item
```

Order Item принадлежит этому Order.

Это принципиально разные отношения.

---

## 50. Главный вопрос перед созданием Child Table

Спросить:

> эта запись является самостоятельным объектом или частью состояния другого объекта?

### Если самостоятельный объект

```text
обычный DocType + Link
```

### Если часть состояния parent

```text
Child DocType + Table
```

### Если это просто множество ссылок

```text
Table MultiSelect
```

---

## 51. Сигналы, что Child Table стала слишком тяжёлой

Стоит пересмотреть модель, если child rows требуют:

```text
собственной карточки
собственного поиска
собственного workflow
assignment
permission rules
индивидуальных notifications
отдельного dashboard
независимого REST lifecycle
массовой обработки между parents
множества внешних Link на child row
```

Это не абсолютный технический запрет.

Но архитектурно такие требования показывают, что child-row превратилась в самостоятельную сущность.

---

## 52. Сигналы, что отдельный DocType избыточен

Обратная ошибка — создавать отдельный DocType для каждой мелкой строки.

Например:

```text
Inspection Measurement
```

если строка:

```text
не открывается отдельно
не имеет lifecycle
не используется другими документами
не нужна вне Inspection
```

то отдельная самостоятельная сущность только усложнит модель.

Child Table здесь естественнее.

---

## 53. Практическая матрица выбора

| Вопрос | Child Table | Обычный DocType |
|---|---:|---:|
| существует без parent | плохо | хорошо |
| нужен отдельный URL | плохо | хорошо |
| нужна собственная очередь | плохо | хорошо |
| меняется только вместе с parent | хорошо | возможно, но тяжелее |
| несколько простых строк в форме | отлично | избыточно |
| нужны собственные permissions | неудобно | хорошо |
| нужны независимые links | неудобно | хорошо |
| нужен grid внутри parent | отлично | требует другого UX |

---

## 54. Выбор между Table и Table MultiSelect

Используем:

```text
нужно несколько структурированных строк
→ Table
```

```text
нужно просто выбрать несколько Documents
→ Table MultiSelect
```

```text
отношение само имеет lifecycle/атрибуты и существует независимо
→ отдельный обычный DocType
```

---

## 55. Типичная ошибка №1: хранить массив в Text/JSON без причины

Плохой вариант:

```json
[
  {"product":"A","qty":2},
  {"product":"B","qty":5}
]
```

в `Long Text` или `JSON`, если это обычные структурированные дочерние строки.

Потери:

```text
нет нормального grid UI
нет metadata полей
сложнее validation
сложнее import/reporting
сложнее scripting
```

Если структура стандартная и принадлежит parent, Child Table обычно лучше.

---

## 56. Когда JSON всё же разумен

JSON может быть правильнее, если данные:

```text
слабо структурированы
приходят как внешний payload
динамичны по schema
не нужны как обычные пользовательские rows
```

То есть выбор зависит не от возможности хранения, а от семантики данных.

---

## 57. Типичная ошибка №2: использовать Child Table как справочник

Например:

```text
Department
└── Employees[]
```

если Employee — самостоятельный объект всей системы.

Это плохая ownership-модель.

Правильнее:

```text
Employee.department → Link / Department
```

или отдельная membership-сущность, если отношение сложнее.

---

## 58. Типичная ошибка №3: Table MultiSelect для сложной связи

Если через месяц выясняется, что выбранному User нужно добавить:

```text
role
weight
status
comment
```

Table MultiSelect перестаёт быть естественным UI.

Лучше сразу использовать обычную Table, если дополнительные атрибуты связи уже известны.

---

## 59. Типичная ошибка №4: дублировать одну связь двумя способами

Плохо:

```text
reviewers → Table MultiSelect
```

и одновременно:

```text
Reviewer Assignment → отдельный DocType
```

если оба механизма описывают один и тот же факт.

Это создаёт два источника истины.

Нужно выбрать одну authoritative модель.

---

## 60. Что нужно запомнить

### Child Table

```text
структурированные строки,
принадлежащие parent
```

### Table MultiSelect

```text
компактный набор Link-значений,
внутри реализованный через child rows
```

### Ordinary DocType

```text
самостоятельная сущность
с собственным lifecycle
```

---

## 61. Итоговая схема

```text
Нужно хранить несколько значений
        │
        ▼
Есть ли у каждой строки самостоятельный смысл?
        │
   ┌────┴────┐
  да         нет
   │          │
   ▼          ▼
Обычный     Это просто
DocType     набор Links?
+ Links        │
          ┌────┴────┐
         да         нет
          │          │
          ▼          ▼
   Table MultiSelect Table
```

---

## 62. Контрольные вопросы

После этой главы нужно уметь ответить:

1. Чем Child DocType отличается от обычного DocType?
2. Что хранится в `parent`?
3. Что хранится в `parenttype`?
4. Для чего нужен `parentfield`?
5. Для чего нужен `idx`?
6. Как Frappe понимает, какие child rows относятся к конкретному Table field?
7. Почему Child Table является частью lifecycle родителя?
8. Что происходит с удалённой из Document дочерней строкой после `save()`?
9. Что реально хранит Table MultiSelect?
10. Почему Table MultiSelect всё равно требует Child DocType?
11. Когда лучше использовать обычную Table?
12. Когда нужно отказаться от Child Table в пользу самостоятельного DocType?
13. Чем Link-отношение концептуально отличается от Child Table?

Если ответы ясны — базовая модель отношений «parent owns children» во Frappe понятна.

---

## Официальные источники

- [Child / Table DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype)
- [Field Types — Table и Table MultiSelect](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Form Scripts — Child Table events](https://docs.frappe.io/framework/user/en/api/form)
- [Frappe source: `base_document.py`](https://github.com/frappe/frappe/blob/version-16/frappe/model/base_document.py)
- [Frappe source: `document.py`](https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py)
- [Frappe source: `docfield.py`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/docfield/docfield.py)
- [Frappe source: `rename_doc.py`](https://github.com/frappe/frappe/blob/version-16/frappe/model/rename_doc.py)

---

Следующая глава: **Single, Tree, Submittable и Virtual DocType**.