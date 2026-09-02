# 02. Data Model

## 1. Цель раздела

Задача data modeling во Frappe — не придумать как можно больше DocType, а выразить предметную область через минимальный набор правильных Document structures.

Главный вопрос:

> **Это самостоятельный Document, свойство другого Document или составная часть parent Document?**

Из этого уже выбираются DocType, field, Link, Child Table и другие primitives.

---

## 2. DocType или поле

### Базовая эвристика

Отдельный DocType является естественным кандидатом, если объект:

- существует самостоятельно;
- имеет свой lifecycle;
- должен открываться отдельно;
- имеет собственные permissions;
- используется несколькими другими Documents;
- должен участвовать в independent search/reporting;
- имеет собственную историю;
- должен быть target для Links.

### Поле естественно, если

значение просто описывает Document.

Пример:

```text
Vehicle
    registration_number
    color
    model
```

`Vehicle` — DocType.

`color` — field.

Создавать `Vehicle Color Instance` только ради хранения значения цвета не нужно, если у цвета нет собственной бизнес-семантики.

### Важное исключение

Если список цветов сам является управляемым справочником с дополнительными атрибутами, правилами или ссылками, отдельный DocType может быть оправдан.

---

## 3. Link

`Link` используется, когда один Document содержит живую ссылку на другой самостоятельный Document.

Пример:

```text
Request
    department → Department
```

Здесь `Department` существует независимо от Request.

### Почему Link лучше текста для живой связи

Он сохраняет referential semantics Framework:

- выбор существующего Document;
- поиск;
- link validation;
- navigation;
- User Permissions по связанным данным;
- report/query relationships.

### Но Link не всегда лучше snapshot

Иногда transaction должен хранить значение таким, каким оно было в момент операции.

Пример:

```text
Invoice
    customer → Customer
    customer_name_snapshot
    billing_address_text
```

Если `Customer` позже переименуют, старый Invoice может быть обязан сохранить исторический текст.

Поэтому вопрос не:

> «Link или Data — что более нативно?»

А:

> **Нужна живая ссылка или исторический снимок?**

---

## 4. Dynamic Link

Обычный Link заранее знает target DocType.

Dynamic Link нужен, когда target type определяется значением другого поля.

Классический паттерн:

```text
reference_doctype
reference_name → Dynamic Link(reference_doctype)
```

Это полезно для универсальных ссылок на документы разных типов.

### Красный флаг

Не использовать Dynamic Link вместо нормальной модели только ради универсальности.

Если объект всегда связан, например, только с `Customer`, обычный Link проще и семантически точнее.

---

## 5. Child DocType

Child DocType — строка, являющаяся составной частью parent Document.

Пример:

```text
Purchase Request
    items
        ├── Item A, 10
        ├── Item B, 3
        └── Item C, 1
```

Строка `Purchase Request Item` существует внутри `Purchase Request`.

Framework хранит для child row системные связи с parent:

```text
parent
parenttype
parentfield
idx
```

### Хороший вопрос

> **Является ли эта запись частью документа или самостоятельным business record, просто связанным с документом?**

Если часть документа — Child Table естественна.

---

## 6. Когда Child Table становится плохим выбором

Запись может требовать отдельного DocType, если она:

- должна иметь независимые permissions;
- открывается отдельно;
- является target Link из других Documents;
- участвует в нескольких parents;
- имеет самостоятельный lifecycle;
- должна существовать после удаления/отмены parent;
- является отдельной business event/record.

Пример:

`Shipment Stop` может начинаться как child row маршрута.

Но если stop становится самостоятельной операционной единицей с исполнителем, SLA, status и внешними ссылками, отдельный DocType может стать правильнее.

---

## 7. Table MultiSelect

Когда Document должен содержать несколько ссылок на Documents другого типа, Frappe предоставляет Table MultiSelect.

Это избавляет от самодельного хранения:

```text
"USER-001,USER-002,USER-003"
```

в одном Data field.

Но если связь имеет собственные атрибуты:

```text
member
role
valid_from
valid_to
```

может быть нужен нормальный child/relation DocType.

---

## 8. Отдельный relation DocType

Иногда связь сама является business record.

Пример:

```text
Employee ← Project Membership → Project
```

Если membership содержит:

- роль;
- даты;
- статус;
- allocation;
- историю;

то отдельный DocType связи может быть правильнее простой multi-select таблицы.

Принцип:

> Если у отношения появляются собственные значимые свойства и lifecycle, оно само становится кандидатом в Document.

---

## 9. Single DocType

Single используется, когда в site логически существует один набор настроек.

Примеры:

```text
Application Settings
Integration Settings
Policy Settings
```

Если несколько записей этой сущности не имеют смысла, обычный DocType плюс самодельный запрет второй записи — лишнее усложнение.

### Граница

Если настройки различаются, например, по Company или Region, один глобальный Single может оказаться неправильной моделью.

---

## 10. Virtual DocType

Virtual DocType позволяет представить внешний источник как Frappe Document model.

Это полезно, если данные находятся:

- в external API;
- secondary database;
- файле;
- ином storage;

но должны участвовать во Frappe как Documents.

### Когда использовать

Когда действительно нужна Document-like semantics:

```text
forms
permissions
resource API
links
Frappe views
```

### Когда не использовать

Если App просто вызывает внешний API для получения курса валют, отдельный Virtual DocType может быть избыточным.

Обычный integration service будет проще.

---

## 11. Tree DocType

Если предметная область является иерархией:

```text
Company
 └── Division
      └── Department
```

нужно рассмотреть стандартную tree model Frappe, а не автоматически создавать:

```text
parent_id
level
path
```

с собственными recursive queries.

Но использовать tree semantics нужно только для настоящей иерархии.

---

## 12. Naming — часть архитектуры модели

Каждый Document имеет `name` — primary identifier Framework.

Naming нельзя оставлять полностью «на потом».

Нужно заранее ответить:

> **`name` является техническим ID или бизнес-идентификатором?**

### Вариант A: технический ID

Пользователь видит отдельное бизнес-поле:

```text
request_number
```

а `name` остаётся внутренним identifier.

### Вариант B: бизнес-ID

Например:

```text
REQ-2026-00042
```

становится `name`.

### Почему решение важно

На `name` могут ссылаться другие Documents и external integrations.

Поздняя смена naming strategy может быть значительно дороже раннего решения.

---

## 13. Naming strategies

Frappe предоставляет стандартные способы именования:

- user supplied;
- field-based;
- Naming Series;
- expression;
- random;
- UUID;
- autoname/controller logic;
- Document Naming Rule.

Выбор должен соответствовать бизнес-семантике, а не эстетике номера.

### Красный флаг

Не писать собственный «генератор номеров» без проверки Naming Series / Naming Rule / autoname capabilities.

---

## 14. Business key и mutable data

Не следует автоматически использовать изменяемое бизнес-значение как `name`.

Например, если регистрационный номер Vehicle может измениться, нужно решить:

```text
Vehicle.name = registration_number
```

или

```text
Vehicle.name = immutable ID
Vehicle.registration_number = mutable field
```

Второй вариант часто безопаснее для долгоживущих ссылок.

Но это domain decision, а не универсальное правило Frappe.

---

## 15. Select или отдельный справочник

Простой список:

```text
Low
Medium
High
```

может быть обычным `Select`.

Отдельный DocType нужен не потому, что «справочники должны быть таблицами», а когда значение:

- редактируется пользователем;
- имеет дополнительные поля;
- участвует в permissions;
- используется как самостоятельный record;
- должно расширяться без изменения metadata.

### Пример

Если Priority имеет только три фиксированных значения — Select достаточно.

Если у Priority есть:

```text
label
color
response_time
escalation_rule
```

отдельный DocType становится логичным.

---

## 16. Не создавать DocType «на всякий случай»

Избыточный DocType имеет стоимость:

```text
schema
permissions
naming
views
migration
API surface
maintenance
conceptual complexity
```

Поэтому каждый DocType должен иметь понятную самостоятельную семантику.

---

## 17. Не нормализовать Frappe как чистую реляционную БД

Хорошая relational normalization полезна, но Frappe model не обязана выглядеть как академическая SQL schema.

Child Tables специально существуют как Document composition.

Snapshot fields тоже могут быть правильны.

Metadata и lifecycle имеют значение не меньше нормализации.

### Анти-паттерн

Разбить обычный документ на десять отдельных DocTypes только ради 3NF, хотя пользователь работает с ним как с одной неделимой карточкой.

---

## 18. Не денормализовать без причины

Обратная крайность:

```text
customer_name
customer_phone
customer_company
customer_department
```

в десятках Documents вместо Links к реальным masters.

Это создаёт дублирование и проблемы консистентности.

Денормализация должна иметь причину:

- snapshot;
- performance;
- external contract;
- reporting convenience с понятным ownership.

---

## 19. Attachments

Для обычных прикреплённых файлов Frappe имеет `File` subsystem.

Не нужно создавать:

```text
TaskAttachment
```

только ради хранения файла, если дополнительная domain semantics отсутствует.

### Когда отдельный DocType оправдан

Если «документ» имеет:

- тип;
- обязательность;
- срок действия;
- verification status;
- signatory;
- compliance workflow.

Тогда это уже не просто attachment.

---

## 20. Comments и коммуникации

Обычные комментарии и timeline activity уже являются Framework capability.

Не создавать собственный `Task Comment` только потому, что приложению нужны комментарии.

Но если запись является domain event, например:

```text
Inspection Finding
```

с severity, category и resolution, это самостоятельная модель, а не Comment.

---

## 21. Version/history

Стандартная document version/history подходит для обычного аудита изменений.

Но не нужно путать её с формальным immutable event ledger.

Если требования включают:

- regulatory retention;
- криптографическую целостность;
- юридическую неизменяемость;
- специальные audit events;

может понадобиться отдельная модель.

---

## 22. Проектирование модели: порядок вопросов

Для каждого нового понятия:

```text
1. Что это означает для бизнеса?

2. Может ли оно существовать самостоятельно?

3. Нужен ли отдельный lifecycle?

4. Нужны ли отдельные permissions?

5. Будут ли другие Documents ссылаться на него?

6. Это часть parent Document?

7. Нужна живая ссылка или snapshot?

8. Как оно именуется?

9. Что произойдёт с существующими данными
   при изменении модели?
```

---

## 23. Decision tree

```text
Нужно хранить значение
        │
        ▼
Самостоятельный объект?
   │              │
  нет            да
   │              │
   ▼              ▼
Field          DocType
   │
   ├── фиксированный список → Select
   │
   ├── ссылка на Document → Link
   │
   ├── polymorphic link → Dynamic Link
   │
   └── повторяющиеся составные строки
             → Child Table

Один набор settings на site?
        → Single

External storage должен выглядеть
как Frappe Documents?
        → Virtual DocType

Связь имеет собственные атрибуты/lifecycle?
        → relation DocType
```

---

## 24. Design review checklist

Перед принятием модели проверить:

- [ ] Каждый DocType имеет самостоятельный смысл.
- [ ] Child rows действительно являются частью parent.
- [ ] Links используются для живых отношений.
- [ ] Snapshot fields имеют объяснение.
- [ ] Fixed Select не вынесен в master без причины.
- [ ] Master не заменён произвольным текстом без причины.
- [ ] Naming strategy определена.
- [ ] Mutable business value не стало `name` случайно.
- [ ] Virtual DocType применяется только при необходимости Document semantics.
- [ ] Attachments/comments/history не дублируются без новой семантики.
- [ ] Учтена migration существующих данных.
