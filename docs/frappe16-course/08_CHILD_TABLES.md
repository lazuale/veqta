# 08. Child Table и Table MultiSelect

Иногда одному документу нужно хранить несколько однотипных строк.

Например, в заказе несколько позиций, а в акте замера — несколько измерений. Для этого во Frappe есть `Child Table`.

Проверено: **2026-08-30**.

## 1. Самый понятный пример

Есть `Order`:

```text
Order ORD-0001

Items:
- Laptop      × 2
- Mouse       × 5
- Keyboard    × 3
```

Сам `Order` — обычный Document.

Каждая строка `Items` — тоже Document, но **дочерний**: отдельно от Order она не имеет самостоятельного смысла.

Вот для таких случаев нужен Child DocType.

## 2. Как это собирается

Сначала создаём дочерний DocType:

```text
DocType: Order Item
Is Child Table = ✓

Fields:
product   Link
qty       Float
price     Currency
```

Потом в `Order` добавляем поле:

```text
Label: Items
Fieldname: items
Field Type: Table
Options: Order Item
```

Теперь Frappe знает:

```text
Order.items
→ список Documents типа Order Item
```

## 3. Child DocType — не JSON-мешок

Дочерняя строка — нормальный Document своего DocType.

У неё есть:

- свои DocFields;
- свой `name`;
- системные поля связи с родителем;
- validation и controller behavior в рамках lifecycle родителя.

То есть строка таблицы структурирована так же строго, как обычный документ, просто **принадлежит parent Document**.

## 4. Четыре поля, которые связывают child с parent

У дочерней строки есть специальные системные свойства:

| Поле | Что означает |
|---|---|
| `parent` | `name` родительского Document |
| `parenttype` | DocType родителя |
| `parentfield` | fieldname Table-поля в родителе |
| `idx` | порядок строки в таблице |

Посмотрим на строку товара:

```text
parent      = ORD-0001
parenttype  = Order
parentfield = items
idx         = 2
```

Этого достаточно, чтобы Frappe понял:

> Это вторая строка поля `items` документа `Order ORD-0001`.

## 5. Зачем нужен `parentfield`

У одного родителя может быть больше одной таблицы.

Например:

```text
Inspection
├── measurements
└── defects
```

Тогда одного `parent = INS-0001` мало. Frappe ещё должен знать, к какому Table-полю относится строка.

Для этого и нужен `parentfield`.

## 6. Зачем нужен `idx`

`idx` хранит порядок:

```text
1 → Laptop
2 → Mouse
3 → Keyboard
```

Если пользователь переставит строки местами, Framework обновит порядок.

Не стоит использовать `idx` как важный неизменяемый бизнес-ID. Это прежде всего позиция строки.

## 7. Как child rows выглядят в Python

Получаем Order:

```python
order = frappe.get_doc("Order", "ORD-0001")
```

И работаем с дочерними строками как со списком:

```python
for row in order.items:
    print(row.product, row.qty)
```

Добавить строку можно через parent:

```python
order.append("items", {
    "product": "Laptop",
    "qty": 2
})

order.save()
```

Для новичка тут важна не команда, а модель:

> дочерние строки загружаются и сохраняются **вместе с родителем**.

## 8. Что происходит при Save

Допустим, в Order было три строки.

Пользователь:

- изменил количество в первой;
- удалил вторую;
- добавил четвёртую.

При сохранении parent Frappe синхронизирует дочернюю таблицу с текущим состоянием Document.

Не нужно отдельно нажимать Save у каждой строки.

Это и есть главное отличие от набора самостоятельных Documents.

## 9. Почему Child Table подходит не всегда

Child Table хороша, когда строка **принадлежит родителю**.

Хорошие примеры:

```text
Order → Order Items
Inspection → Measurements
Questionnaire → Answers
```

Плохой кандидат:

```text
Project → Employees
```

если сотрудник должен иметь собственные права, ссылки, отчёты, lifecycle и использоваться независимо от конкретного Project.

Тогда `Employee` — обычный самостоятельный DocType, а не child row.

## 10. Простой тест: child или обычный DocType?

Спроси:

> Если удалить родительский документ, имеет ли эта строка самостоятельный смысл?

Если ответ «нет» — Child Table выглядит логично.

Если ответ «да, это полноценный объект системы» — скорее нужен обычный DocType и Link.

Это не абсолютное математическое правило, но для проектирования помогает очень хорошо.

## 11. Child Table нельзя вкладывать бесконечно

В Frappe child tables не предназначены для создания дерева «таблица внутри строки таблицы внутри ещё одной таблицы».

Child DocType не должен содержать обычную вложенную child table как ещё один уровень композиции.

Если модель требует глубокую иерархию самостоятельных объектов, лучше пересмотреть структуру данных.

## 12. Editable Grid

В Form View обычная Child Table часто отображается как grid.

Пользователь может редактировать часть полей прямо в строках:

```text
Product      Qty      Price
Laptop       2        1200
Mouse        5        30
```

Какие колонки видны и как ведёт себя grid, зависит от metadata полей и настроек DocType.

Для небольших таблиц это очень удобно.

## 13. Что делать с очень большими таблицами

Если один Document начинает содержать тысячи child rows, работать с ним становится тяжелее и для UI, и для lifecycle сохранения.

В v16 есть настройки grid/search, которые помогают с крупными таблицами, но они не отменяют архитектурный вопрос:

> действительно ли эти тысячи записей являются частью одного документа?

Иногда правильнее сделать самостоятельный DocType и List View, а не гигантскую Child Table.

## 14. Table MultiSelect

`Table MultiSelect` решает более узкую задачу: **выбрать несколько связанных значений**.

Пример:

```text
Request
Allowed Departments:
[Analytics] [Finance] [Operations]
```

Под капотом для этого тоже используется Child DocType.

Например:

```text
DocType: Request Department
Is Child Table = ✓

Field:
department  Link → Department
```

А в Request:

```text
Field Type: Table MultiSelect
Options: Request Department
```

Пользователь получает удобный множественный выбор вместо полноценной табличной формы.

## 15. Table и Table MultiSelect — в чём разница

### Table

Нужна, когда каждая строка содержит **несколько значимых полей**.

Пример:

```text
Product | Qty | Price | Discount
```

### Table MultiSelect

Нужна, когда основная задача — **выбрать несколько ссылок**.

Пример:

```text
Department
- Analytics
- Finance
- Operations
```

Если для каждой выбранной записи внезапно нужны `Role`, `Start Date`, `Percent`, `Comment` — это уже не простой MultiSelect. Возможно, нужна обычная Table или отдельный DocType связи.

## 16. Почему для Table MultiSelect тоже нужен Child DocType

Frappe не хранит список ссылок просто строкой:

```text
"Analytics,Finance,Operations"
```

Вместо этого каждая выбранная связь имеет структурированную child row.

Это лучше для целостности и работы Framework.

## 17. Уникальность выбора

Для Table MultiSelect смысл обычно в том, чтобы один и тот же связанный Document не выбирать много раз.

Например:

```text
Analytics
Analytics
Analytics
```

не несёт пользы как «список разрешённых отделов».

Framework учитывает специфику этого field type и работает с ним не как с обычной свободной таблицей.

## 18. Когда лучше отдельный DocType связи

Допустим, между `Project` и `Employee` нужно хранить:

```text
Project
Employee
Role
Start Date
End Date
Allocation %
```

Это уже почти самостоятельная сущность:

```text
Project Member
```

У неё могут появиться свои permissions, Reports и ссылки из других документов.

В таком случае отдельный обычный DocType часто понятнее, чем прятать всё внутри parent.

## 19. Child Table и Link — разные отношения

Полезно запомнить две модели:

```text
Link
→ «этот документ ссылается на другой самостоятельный документ»

Child Table
→ «эти строки принадлежат этому документу»
```

Слова «ссылка» и «принадлежность» хорошо помогают выбрать правильный механизм.

## Мини-практика

Определи подходящий вариант:

1. `Order` содержит товары, количество и цену → **Table / Child DocType**.
2. `Request` должен выбрать несколько разрешённых Departments без дополнительных данных → **Table MultiSelect**.
3. `Request` относится к одному Department → **Link**, не Child Table.
4. Участие Employee в Project имеет роль, даты и процент загрузки → скорее **отдельный DocType связи**.

## Что запомнить

- Child Table означает **владение/композицию**, а не просто любую связь.
- Child row знает `parent`, `parenttype`, `parentfield`, `idx`.
- Child rows сохраняются вместе с parent Document.
- `Table` — полноценные строки с несколькими полями.
- `Table MultiSelect` — удобный множественный выбор через child rows.
- Если строка становится самостоятельным объектом, пора подумать об обычном DocType.

## Официальные источники

- [Child / Table DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [BaseDocument child handling, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/model/base_document.py)

Следующая глава: [**09. Single, Tree, Submittable и Virtual DocType**](09_SPECIAL_DOCTYPES.md).