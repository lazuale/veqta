# 02. Data Model — как выбирать DocType, поля и связи

## 1. Главный вопрос

Frappe — metadata-driven framework, поэтому качество приложения во многом определяется качеством DocType model.

Перед созданием каждого нового DocType нужно спросить:

> Это действительно самостоятельный Document системы или всего лишь свойство/строка/ссылка другого Document?

Это не официальный «тест Frappe», а **[ARCHITECTURAL INFERENCE]**, основанный на том, что Framework предоставляет разные primitives для разных форм данных.

Основные источники:

- https://docs.frappe.io/framework/user/en/basics/doctypes
- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

---

## 2. Когда нужен обычный DocType

**[FRAPPE DOCS]** DocType — core building block и описание типа Document.

Обычный DocType естественен, если запись имеет собственную идентичность и хотя бы несколько из признаков ниже:

```text
имеет самостоятельный lifecycle;
имеет собственные permissions;
на неё ссылаются другие Documents;
её открывают и ищут отдельно;
она может существовать независимо от одного parent;
нужен собственный audit/history;
у неё есть собственные business rules.
```

Пример:

```text
Vehicle
Customer
Contract
Work Order
Inspection
```

### Ошибка новичка

Создавать DocType для каждого существительного:

```text
Task Color
Task Priority Value
Task Comment Row
Task Responsible Row
```

только потому, что «отдельная таблица выглядит чище».

Каждый лишний DocType добавляет собственную модель, права, naming, search/list semantics, ссылки и upgrade surface.

---

## 3. Когда достаточно DocField

**[FRAPPE DOCS]** Frappe предоставляет field types для описания свойств Document: Data, Select, Int, Date, Link, Table и другие.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

Если значение является обычным свойством Document и не имеет самостоятельного поведения, отдельный DocType чаще всего не нужен.

Пример:

```text
Vehicle
  registration_number : Data
  manufacture_year    : Int
  active              : Check
```

### Select или отдельный справочник?

`Select` подходит, когда набор значений:

- мал;
- стабилен;
- не имеет дополнительных атрибутов;
- не требует прав или отдельного управления.

Отдельный DocType лучше, когда элемент списка сам становится управляемым объектом.

Пример:

```text
Priority = Low / Normal / High
```

может быть Select.

Но если у каждой Priority имеются:

```text
name
response_time
color
escalation_rule
active
```

это уже хороший кандидат на отдельный DocType.

---

## 4. Link — живая ссылка на другой Document

**[FRAPPE DOCS]** Field type `Link` ссылается на другой DocType.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

Пример:

```text
Work Order
  vehicle -> Vehicle
```

Если `Vehicle` является самостоятельным master record, Link сохраняет настоящую связь.

### Ошибка

Хранить вместо Link:

```text
vehicle_name = "Shacman A123"
```

когда система должна работать именно с записью Vehicle.

Так теряются ссылочная целостность Frappe, link search и возможность однозначно идентифицировать объект.

---

## 5. Snapshot — важное исключение из правила Link

Не каждое повторение значения является ошибкой.

Иногда transaction должен сохранить состояние данных **на момент операции**.

Пример:

```text
Invoice
  customer -> Customer
  customer_name_snapshot
  billing_address_snapshot
```

Если завтра Customer поменяет адрес, старый Invoice не должен обязательно переписать исторический адрес.

**[ARCHITECTURAL INFERENCE]** Поэтому нужно различать:

```text
Link     = текущая связь с живым master
Snapshot = историческое значение на момент события
```

Решение определяется бизнес-семантикой, а не борьбой с «дублированием данных» как таковым.

---

## 6. Child DocType — составная часть parent Document

**[FRAPPE DOCS]** Child DocType предназначен для records, прикреплённых к parent DocType. Child row содержит `parent`, `parenttype`, `parentfield`, `idx`.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype

Пример:

```text
Purchase Request
  applicant
  date
  items[]
      item
      qty
      uom
```

`Purchase Request Item` не является отдельной заявкой. Это состав документа.

### Лучший вопрос для новичка

Не только:

> «Переживёт ли строка удаление parent?»

а:

> **«Эта запись является частью одного Document или отдельным business record, который просто связан с ним?»**

Если запись требует собственных permissions, используется несколькими parents или на неё должны ссылаться другие документы, отдельный DocType может быть правильнее.

---

## 7. Table MultiSelect

**[FRAPPE DOCS]** `Table MultiSelect` позволяет представить набор ссылок через child-table semantics.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

Это хороший вариант, когда parent должен выбрать несколько records одного типа и сама связь почти не несёт дополнительных бизнес-атрибутов.

Если связь имеет собственные данные:

```text
role
valid_from
valid_to
allocation_percent
```

может понадобиться обычный child row или самостоятельный relation DocType.

---

## 8. Dynamic Link

**[FRAPPE DOCS]** Dynamic Link позволяет одному полю ссылаться на Documents разных DocTypes, а целевой DocType определяется другим полем.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

Пример:

```text
reference_doctype = "Sales Invoice"
reference_name    = "SINV-0001"
```

или тот же объект может ссылаться на Purchase Order, Issue и т.д.

Использовать Dynamic Link только ради «универсальности на будущее» не следует. Обычный Link проще и сильнее выражает модель, если тип связи известен заранее.

---

## 9. Когда нужен отдельный relation DocType

Frappe не запрещает моделировать связь отдельным DocType.

Это естественно, когда отношение само является бизнес-фактом.

Пример:

```text
Employee Project Membership
  employee
  project
  role
  valid_from
  valid_to
  allocation_percent
```

Здесь membership имеет собственный смысл, историю и поля. Он уже не просто «список выбранных сотрудников».

**[ARCHITECTURAL INFERENCE]** Отдельный relation DocType оправдан не потому, что many-to-many «должен иметь join table», а потому что отношение имеет самостоятельную семантику.

---

## 10. Single DocType

**[FRAPPE DOCS]** Single DocType предназначен для данных, где в site имеет смысл только одна запись, например settings.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype

Пример:

```text
My App Settings
  default_priority
  integration_enabled
  api_base_url
```

### Неправильно

Создать обычный DocType `My App Settings`, а потом вручную запрещать вторую запись.

Framework уже имеет тип модели для этого случая.

---

## 11. Virtual DocType

**[FRAPPE DOCS]** Virtual DocType позволяет представить данные, которые физически хранятся не в обычной Frappe table, как Documents Framework.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype

Внешний источник может быть API, другая database и т.п.

### Когда это хорошо

Если внешние данные действительно должны вести себя внутри Frappe как Documents:

- отображаться штатными views;
- участвовать в permissions;
- читаться через resource API;
- иметь Document-like interface.

### Когда не нужно

Если приложение делает два вызова внешнего API для расчёта курса валют, создавать Virtual DocType `External Exchange Rate Record` может быть лишним.

**[ARCHITECTURAL INFERENCE]** Внешний источник сам по себе не означает Virtual DocType. Нужна именно Document semantics.

---

## 12. Tree DocType

Frappe поддерживает tree-структуры DocType для иерархических данных.

Использовать tree нужно, когда предметная область действительно иерархична:

```text
Department
Account
Territory
```

Не нужно превращать любой parent-child relation в tree только ради красивого интерфейса.

Источник для общей модели DocType:

- https://docs.frappe.io/framework/user/en/basics/doctypes

---

## 13. Naming — часть архитектуры, а не косметика

**[FRAPPE DOCS]** Frappe имеет системное поле `name` и несколько naming strategies: field, naming series, expression, UUID, controller `autoname` и другие.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/naming

При проектировании DocType нужно решить:

```text
name = технический ID?
или
name = бизнес-номер, который видит человек?
```

Это важно, потому что `name` участвует в ссылках и URL.

### Пример

Для Vehicle естественным `name` может быть UUID/внутренний ID, если госномер способен измениться.

Для официального документа может быть оправдан бизнес-номер через naming series.

### Red flag

Использовать изменяемое отображаемое название как permanent primary key только потому, что оно сейчас уникально.

---

## 14. Не путать identity и label

У Document есть идентичность `name`, но пользователю часто нужен человекочитаемый title.

**[ARCHITECTURAL INFERENCE]** Если display name может изменяться, а ссылки должны оставаться стабильными, лучше разделить:

```text
name  = стабильный ID
title = изменяемое отображаемое значение
```

Это особенно важно для каталогов и master data.

---

## 15. Data model design review

Перед утверждением нового DocType пройти вопросы:

```text
1. Это самостоятельный Document или свойство другого?
2. Нужен ли собственный lifecycle?
3. Нужны ли собственные permissions?
4. Должны ли другие Documents ссылаться на эту запись?
5. Это состав parent или самостоятельная запись?
6. Link нужен как живая связь или бизнесу нужен snapshot?
7. Нужен ли Single вместо обычного DocType?
8. Нужен ли Dynamic Link или обычный Link точнее?
9. Должны ли внешние данные действительно иметь Document semantics?
10. Что является стабильной identity и как работает naming?
11. Что произойдёт с существующими ссылками при rename?
12. Как модель будет мигрировать после появления production data?
```

Если на эти вопросы нет ответа, DocType ещё рано создавать.
