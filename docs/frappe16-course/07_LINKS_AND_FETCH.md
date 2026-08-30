# 07. Link, Dynamic Link и Fetch From

Эта глава разбирает штатные механизмы связей между документами во **Frappe Framework 16**.

Цель — понять:

- что реально хранит поле `Link`;
- чем `Link` отличается от SQL foreign key;
- как Frappe проверяет существование связанного документа;
- как работает поиск в Link-поле;
- зачем нужен `Dynamic Link`;
- что хранит `Dynamic Link` и откуда он узнаёт тип документа;
- как работает `Fetch From`;
- почему `Fetch From` — это копирование значения, а не live-связь;
- когда использовать обычный Link, Dynamic Link или отдельную сущность связи.

Проверено: **2026-08-30**.

---

## 1. Связи во Frappe начинаются с `name`

В предыдущей главе мы разобрали, что каждый обычный документ Frappe имеет системный идентификатор:

```text
name
```

Именно `name` используется как значение ссылки на документ.

Пример:

```text
Department
name = ANALYTICS
```

В другом DocType создаём поле:

```text
Department
Field Type: Link
Options: Department
```

Если пользователь выбрал документ `ANALYTICS`, в поле сохраняется:

```text
ANALYTICS
```

То есть Link хранит **`name` целевого документа**.

---

## 2. `Link` — штатная ссылка на конкретный DocType

Обычный `Link` всегда знает тип документа заранее.

Например:

```text
Request.department
```

настраиваем так:

```text
Field Type: Link
Options: Department
```

Схема:

```text
Request
   │
   │ department = "ANALYTICS"
   ▼
Department
name = "ANALYTICS"
```

`Options` для Link содержит **название целевого DocType**.

Это главный признак обычного Link:

```text
тип цели фиксирован metadata поля
```

---

## 3. Что хранится в базе данных

Для MariaDB в текущем Frappe типы `Link` и `Dynamic Link` отображаются в обычный `varchar`.

То есть концептуально в таблице находится не объект и не JSON:

```text
department = "ANALYTICS"
```

Это важно для понимания архитектуры Frappe:

> Link — это **application-level reference**, а не обязательно физический SQL `FOREIGN KEY` constraint.

Framework знает, что поле является ссылкой, потому что его DocField metadata говорит:

```text
fieldtype = Link
options   = Department
```

---

## 4. Но Link — не просто строка

Хотя физически поле хранит значение `name`, Framework добавляет вокруг него поведение:

```text
поиск документа
autocomplete
permissions
User Permissions
проверку существования цели
переход к связанному документу
rename-aware обновление ссылок
metadata связанного DocType
```

Поэтому заменять Link обычным `Data` только потому, что «там всё равно строка», обычно неправильно.

---

## 5. Frappe проверяет ссылки при сохранении

При обычном `insert` или `save` Document выполняется link validation.

Если поле указывает на несуществующий документ, Framework может выбросить:

```text
frappe.LinkValidationError
```

Пример:

```text
Request.department = "DOES-NOT-EXIST"
```

при условии:

```text
Field Type = Link
Options    = Department
```

не считается нормальной ссылкой.

Это проверяется на уровне Document lifecycle.

### Важная деталь

Поскольку это проверка Framework, а не SQL foreign key, низкоуровневый код при необходимости может явно обходить link validation через специальные флаги вроде `ignore_links`.

Следовательно:

```text
Link validation
≠
неизбежный DB foreign key constraint
```

---

## 6. Что происходит при Rename целевого документа

Поскольку Frappe понимает metadata Link-полей, штатный механизм Rename умеет искать поля:

```text
Field Type: Link
Options: переименовываемый DocType
```

и обновлять ссылки со старого `name` на новый.

Например:

```text
Department
ANALYTICS
```

переименовали в:

```text
DATA-ANALYTICS
```

ссылочные значения в документах должны быть обработаны штатным механизмом Rename, а не оставлены как сломанные строки.

Это ещё одна причина не заменять настоящую связь обычным `Data`.

---

# Часть I. Link в интерфейсе

## 7. Что пользователь видит в Desk

Поле Link рендерится как control с поиском связанных документов.

Пользователь не должен вручную помнить `name` каждой записи.

Условно:

```text
Department
[ Analyt...          ]

Suggestions:
Analytics
Analytics Support
Data Analytics
```

Framework выполняет link search и возвращает подходящие документы.

---

## 8. `name` и отображаемый title — не одно и то же

Целевой документ может иметь:

```text
name  = DEP-00017
title = Analytics
```

Ссылка всё равно хранит:

```text
DEP-00017
```

а интерфейс может дополнительно показывать пользователю title/описание документа.

Поэтому правильная модель:

```text
Link storage
→ стабильный name

Human UI
→ name + title / search fields
```

Не стоит менять Naming strategy только ради того, чтобы Link выглядел красиво.

---

## 9. Search Fields целевого DocType

Возможность найти документ через Link зависит не только от его `name`.

DocType может определять дополнительные:

```text
Search Fields
```

Например Department имеет:

```text
name
Department Name
Code
```

Тогда link search можно сделать удобнее для пользователя.

Это лучше, чем пытаться копировать все поисковые поля в исходный документ.

---

## 10. Link и permissions

Link search интегрирован с permission model Frappe.

На доступный набор значений могут влиять:

```text
Role Permissions
User Permissions
query filters
DocType access
```

Поэтому ситуация:

```text
документ существует в БД
```

не всегда означает:

```text
пользователь увидит его в Link dropdown
```

Это нормальное следствие security model.

---

## 11. `Ignore User Permissions`

У Link и Dynamic Link есть metadata-флаг:

```text
Ignore User Permissions
```

Он нужен для специальных случаев, когда Link search не должен ограничиваться User Permissions обычным образом.

Использовать его автоматически на всех ссылках нельзя: это ослабляет один из уровней ограничения данных.

Сначала нужно понимать, **почему конкретная ссылка должна игнорировать User Permissions**.

---

## 12. Статические Link Filters

В DocField существует свойство:

```text
link_filters
```

Оно позволяет задавать дополнительные фильтры Link-поля через metadata.

Например логически:

```text
Department
active = 1
```

Тогда пользователь выбирает только активные подразделения.

Это хороший вариант, если условие:

```text
стабильное
не зависит от текущего документа сложным образом
```

---

## 13. Динамические фильтры Link

Если фильтр зависит от текущего документа, обычно используется Form API и `set_query`.

Концептуально:

```javascript
frm.set_query("department", () => {
    return {
        filters: {
            active: 1
        }
    };
});
```

Более сложный пример:

```text
выбран Company A
        ↓
Department Link показывает
только Department этой Company
```

То есть:

```text
статическая связь
→ Link metadata

динамический поиск
→ query/filter logic
```

---

# Часть II. Dynamic Link

## 14. Ограничение обычного Link

Обычный Link всегда указывает на один заранее заданный DocType.

Например:

```text
Link → Department
```

Но иногда нужно поле:

```text
Reference
```

которое может ссылаться на:

```text
Customer
Supplier
Employee
Project
любой другой разрешённый тип
```

Обычного Link здесь недостаточно.

---

## 15. Что такое Dynamic Link

`Dynamic Link` — ссылка, у которой целевой DocType определяется **значением другого поля текущего документа**.

Типичная пара:

```text
Reference Type
Field Type: Link
Options: DocType

Reference
Field Type: Dynamic Link
Options: reference_type
```

Например пользователь выбирает:

```text
Reference Type = Department
```

после этого поле `Reference` ищет документы именно DocType:

```text
Department
```

Если выбрать:

```text
Reference Type = User
```

то то же Dynamic Link поле начинает ссылаться на:

```text
User
```

---

## 16. Что означает `Options` у Dynamic Link

У обычного Link:

```text
Options = название DocType
```

Например:

```text
Options = Department
```

У Dynamic Link:

```text
Options = fieldname другого поля
```

Например:

```text
Options = reference_type
```

Это принципиальное различие.

### Обычный Link

```text
options
   ↓
Department
```

### Dynamic Link

```text
options
   ↓
reference_type
   ↓
значение этого поля
   ↓
Department / User / Project / ...
```

---

## 17. Что хранит Dynamic Link

Само Dynamic Link поле также хранит `name` выбранного документа.

Например:

```text
reference_type = "Department"
reference      = "ANALYTICS"
```

Полную ссылку можно понимать как пару:

```text
(doctype, name)
```

то есть:

```text
("Department", "ANALYTICS")
```

Это полиморфная ссылка.

---

## 18. Где Dynamic Link особенно полезен

Типовые случаи:

```text
универсальный Reference
связь Communication с разными документами
журнал событий разных сущностей
универсальные attachments/relations
generic activity/reference model
```

Но использовать Dynamic Link просто «на всякий случай» не стоит.

Если поле всегда связано только с Department, обычный:

```text
Link → Department
```

проще, понятнее и легче анализируется.

---

## 19. Когда Dynamic Link начинает вредить модели

Плохой признак:

```text
reference_type
reference_name
```

появляются почти в каждой бизнес-сущности только для того, чтобы избежать нормальных связей.

Это приводит к:

```text
слабой типизации модели
сложным отчётам
сложным permission rules
трудному анализу зависимостей
неочевидным пользовательским формам
```

Dynamic Link — мощный инструмент для **реально полиморфной связи**, а не универсальная замена всем Link.

---

# Часть III. Fetch From

## 20. Задача Fetch From

Представим два DocType.

### Department

```text
name
manager
email
```

### Request

```text
subject
department
department_manager
```

Поле:

```text
Request.department
```

— Link на Department.

Мы хотим автоматически записывать manager выбранного Department в:

```text
Request.department_manager
```

Для этого существует:

```text
Fetch From
```

---

## 21. Синтаксис Fetch From

Формат:

```text
link_field.source_field
```

Например:

```text
department.manager
```

То есть:

```text
текущее поле Request.department
        ↓
открыть связанный Department
        ↓
взять Department.manager
        ↓
записать в текущее поле
```

---

## 22. Пример настройки

В Request:

```text
Department
Field Type: Link
Options: Department
fieldname: department
```

и:

```text
Department Manager
Field Type: Link
Options: User
fieldname: department_manager
Fetch From: department.manager
Read Only: ✓
```

Пользователь выбирает:

```text
Department = Analytics
```

Frappe получает:

```text
Analytics.manager
```

и записывает его в:

```text
Request.department_manager
```

---

## 23. `Fetch From` хранит копию значения

Это самое важное правило главы.

`Fetch From` не создаёт live SQL join.

Он **записывает полученное значение в поле текущего документа**.

Например:

```text
Department.manager = user_a
```

Request сохранился:

```text
Request.department_manager = user_a
```

Потом Department изменили:

```text
Department.manager = user_b
```

это не означает, что во всех уже существующих Request мгновенно физически изменилось поле `department_manager`.

`Fetch From` следует понимать как:

```text
fetch
+
copy into current document
```

а не как:

```text
live relation / computed join
```

---

## 24. Зачем тогда вообще копировать данные

Это полезно, когда значение должно стать частью конкретного документа.

Например:

```text
адрес на момент операции
контакт на момент создания
налоговый номер
ответственный, зафиксированный в записи
наименование для печати
```

То есть иногда денормализация является сознательной частью модели.

---

## 25. Когда Fetch From использовать не надо

Если бизнес-смысл такой:

> всегда показывать **текущее** значение поля связанного документа,

то физическая копия может создать два источника истины.

Например:

```text
Request.department
```

уже позволяет найти актуальный Department.

Если дополнительно без необходимости хранить:

```text
Request.department_name
Request.department_manager
Request.department_email
Request.department_phone
```

можно получить устаревающие дубли.

Перед Fetch From задаём вопрос:

> значение должно быть снимком в текущем документе или всегда должно читаться из master?

---

## 26. Обычный режим Fetch From

Официальный guide описывает режим, в котором fetched value обновляется при сохранении документа и может перезаписывать пользовательский ввод.

Обычно такой target field делают:

```text
Read Only
```

если пользователь не должен изменять автоматически полученное значение.

---

## 27. `Fetch If Empty`

У DocField существует флаг:

```text
Fetch If Empty
```

Его смысл:

```text
если target field пуст
→ получить значение

если target field уже заполнен
→ не затирать его
```

Это полезно для сценария:

```text
попробовать взять default из master
        ↓
если значения нет или его нужно изменить
        ↓
разрешить пользователю собственное значение
```

---

## 28. Два разных бизнес-смысла Fetch From

### Сценарий A — автоматически поддерживаемая копия

```text
Fetch From: department.manager
Read Only: ✓
```

Смысл:

> это поле определяется связанной записью.

### Сценарий B — начальное значение

```text
Fetch From: department.manager
Fetch If Empty: ✓
```

Смысл:

> взять значение как default, но затем разрешить локальное значение.

Эти сценарии нельзя путать.

---

## 29. Fetch From и permissions

Получение значения связано с доступом к source document.

В Desk permission restrictions могут влиять на клиентский fetch.

На текущих релизах v16 есть известный нюанс: `ignore_user_permissions` имеет смысл для Link/Dynamic Link, но установка этого флага на обычном Data/Read Only target field сама по себе не гарантирует обход permission checks клиентского `fetch_from`.

Практическое правило:

> Fetch From обязательно тестируем под реальной ролью и реальными User Permissions, а не только под Administrator.

---

# Часть IV. Что выбирать

## 30. Link или Fetch From

Это не альтернативы.

### Link

Хранит:

```text
какой документ связан
```

### Fetch From

Хранит:

```text
какое значение мы скопировали из связанного документа
```

Например:

```text
department
→ Link

department_manager
→ Fetch From department.manager
```

---

## 31. Link или Dynamic Link

Используем обычный Link, если тип цели известен:

```text
Department
Employee
Project
User
```

Используем Dynamic Link, если тип цели является частью данных:

```text
reference_doctype
+
reference_name
```

Упрощённо:

```text
Цель всегда одного DocType?
        │
        ├── да → Link
        │
        └── нет
             │
             └── связь действительно полиморфная?
                    │
                    ├── да → Dynamic Link
                    └── нет → пересмотреть модель
```

---

## 32. Когда нужна отдельная сущность связи

Иногда одного Link уже мало.

Например отношение само имеет свойства:

```text
Person
   │
   │ participates in
   ▼
Project
```

но нам ещё нужно хранить:

```text
role
start_date
end_date
allocation_percent
status
```

Тогда связь сама становится данными.

Нужен отдельный DocType вроде:

```text
Project Member
```

а не несколько разрозненных Link-полей.

Принцип:

> если у отношения появились собственные атрибуты и lifecycle, отношение может быть самостоятельной сущностью.

---

## 33. Link против Child Table

Если нужно выбрать **один самостоятельный документ**:

```text
Link
```

Если внутри текущего документа существует набор дочерних строк:

```text
Table / Child DocType
```

Если нужны несколько самостоятельных связанных документов с отношением many-to-many — модель требует отдельного анализа; автоматически заменять её Child Table нельзя.

Child Tables подробно разбираются в следующей главе.

---

# Часть V. Практические ошибки

## 34. Ошибка: использовать Data вместо Link

Плохо:

```text
department
Field Type: Data
```

если значение на самом деле должно ссылаться на Department.

Теряем:

```text
link search
validation
permissions integration
Rename awareness
metadata relationship
нормальный UX выбора
```

---

## 35. Ошибка: хранить title вместо `name`

Допустим:

```text
Department.name = DEP-00012
Department.title = Analytics
```

Link должен ссылаться на:

```text
DEP-00012
```

а не пытаться самостоятельно хранить:

```text
Analytics
```

как неформальную ссылку.

Человекочитаемое отображение и идентификатор — разные задачи.

---

## 36. Ошибка: Dynamic Link везде

Плохо:

```text
reference_type
reference
```

для любой связи.

Если тип известен заранее, обычный Link:

```text
проще
понятнее
лучше документирует schema
удобнее для reports
удобнее для permissions
```

---

## 37. Ошибка: Fetch From как синхронизация master data

`Fetch From` не является универсальным механизмом двусторонней синхронизации.

Он не означает:

```text
изменилось source
→ мгновенно изменились миллионы target documents
```

Если требуется такая семантика, надо либо читать source напрямую, либо проектировать отдельную серверную синхронизацию.

---

## 38. Ошибка: копировать всё из linked document

Если у Request есть:

```text
department → Department
```

не нужно автоматически добавлять:

```text
department_name
department_code
department_manager
department_email
department_phone
department_address
```

только потому, что `Fetch From` это позволяет.

Каждая копия должна иметь доказанный смысл:

```text
snapshot
печать
поиск
историческая фиксация
performance
отдельное бизнес-значение
```

---

# Часть VI. Итоговая модель

## 39. Обычный Link

```text
DocType A
   │
   │ Link
   │ options = DocType B
   │ value   = B.name
   ▼
DocType B
```

---

## 40. Dynamic Link

```text
DocType A

reference_type = "DocType B"
        │
        └──────────────┐
                       ▼
reference
Dynamic Link
options = reference_type
value   = B.name
```

Полная ссылка:

```text
(reference_type, reference)
```

---

## 41. Fetch From

```text
Request.department
       │
       │ Link
       ▼
Department.manager
       │
       │ Fetch From
       ▼
Request.department_manager
```

Это:

```text
получить значение
+
записать значение в текущий Document
```

а не live join.

---

## 42. Что нужно уметь после главы

Нужно без подсказки объяснить:

1. Что физически хранит обычное Link-поле?
2. Где указан целевой DocType обычного Link?
3. Почему Link не равен SQL foreign key?
4. Что Frappe проверяет при сохранении Link?
5. Почему `Data` не является полноценной заменой Link?
6. Что находится в `Options` у Dynamic Link?
7. Из каких двух значений концептуально состоит Dynamic Link reference?
8. В чём разница между Link и Dynamic Link?
9. Что означает `department.manager` в Fetch From?
10. Является ли Fetch From live join?
11. Чем обычный Fetch From отличается от `Fetch If Empty`?
12. Когда отношение между двумя сущностями стоит вынести в отдельный DocType?

Если ответы ясны — можно переходить к Child Tables.

## Официальные источники

- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Controls API](https://docs.frappe.io/framework/user/en/api/controls)
- [Fetch a Field Value from a Document into a Transaction](https://docs.frappe.io/framework/user/en/guides/app-development/fetch-custom-field-value-from-master-to-all-related-transactions)
- [Form Scripts / `frm.set_query`](https://docs.frappe.io/framework/user/en/api/form)
- [DocField source](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/docfield/docfield.py)
- [MariaDB field type map](https://github.com/frappe/frappe/blob/version-16/frappe/database/mariadb/mysqlclient.py)
- [Document lifecycle and link validation](https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py)
- [Rename implementation](https://github.com/frappe/frappe/blob/version-16/frappe/model/rename_doc.py)

---

Следующая глава: **08. Child Table и Table MultiSelect**.