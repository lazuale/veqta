# 07. Link, Dynamic Link и Fetch From

Во Frappe документы редко живут изолированно. Заявка может ссылаться на отдел, сотрудника, проект или другой документ.

Для этого есть несколько разных механизмов. Самые важные на старте — `Link`, `Dynamic Link` и `Fetch From`.

Проверено: **2026-08-30**.

## 1. Link — ссылка на другой DocType

Допустим, есть справочник:

```text
DocType: Department

Documents:
ANALYTICS
FINANCE
OPERATIONS
```

В `Request` добавим поле:

```text
Label: Department
Fieldname: department
Field Type: Link
Options: Department
```

Теперь пользователь не печатает название отдела вручную, а выбирает существующий Document.

Если выбран `ANALYTICS`, в поле сохраняется:

```text
department = "ANALYTICS"
```

То есть обычный Link хранит **`name` целевого документа**.

## 2. Что означает Options у Link

Для Link:

```text
Options = Department
```

означает:

> это поле может ссылаться на Documents DocType `Department`.

Тип цели известен заранее.

Схема:

```text
Request.department
        │
        └── Link → Department
                     │
                     └── name = ANALYTICS
```

## 3. Почему не сделать Department обычным Data

Можно было бы создать:

```text
Department
Field Type: Data
```

и писать руками:

```text
Analytics
analytics
ANALYTICS
Аналитика
```

Через месяц получим несколько написаний одного и того же отдела.

Link решает эту проблему: значение выбирается из существующих Documents.

Кроме того, Frappe понимает, что это связь, и добавляет вокруг неё поиск, permissions, переход к записи и link validation.

## 4. Link хранится как значение, но ведёт себя как ссылка

На уровне БД Link обычно хранится как строковое значение `name`, а не как вложенный объект.

Например:

```text
ANALYTICS
```

Но metadata поля говорит Frappe:

```text
fieldtype = Link
options = Department
```

Поэтому Framework знает, что `ANALYTICS` нужно искать именно среди Documents `Department`.

Это **application-level reference**. Его не стоит путать с обычным SQL foreign key constraint.

## 5. Проверка существования ссылки

При нормальном `insert`/`save` Frappe проверяет Link-поля.

Если написать:

```text
department = DOES-NOT-EXIST
```

а такого Department нет, сохранение обычно завершится `LinkValidationError`.

Это полезная защита от битых ссылок.

Технически низкоуровневый код может обходить некоторые проверки специальными флагами, но в обычной разработке этого без причины делать не нужно.

## 6. Что пользователь видит в Link-поле

В Desk Link выглядит как поле с поиском и подсказками.

Пользователь начинает печатать:

```text
ana...
```

и получает варианты.

Поиск может учитывать не только `name`, но и title/search fields целевого DocType.

Например:

```text
name = DEP-0017
title = Analytics
```

Пользователь может видеть понятное `Analytics`, хотя в ссылке хранится `DEP-0017`.

## 7. Permissions тоже влияют на Link

Пользователь обычно не должен выбирать документы, к которым у него нет доступа.

Поэтому Link search связан с permission engine и User Permissions.

Пример:

```text
Пользователь имеет доступ только к Department = ANALYTICS
```

Тогда список доступных значений Link может быть ограничен этим отделом.

Свойство `Ignore User Permissions` существует, но применять его нужно осознанно: оно отключает часть стандартного ограничения.

## 8. Как ограничить варианты Link

Иногда из всех Departments нужны только активные.

Идея фильтра:

```text
is_active = 1
```

Для простых случаев используются штатные link filters. Для динамических условий на форме можно настраивать query через Client Script, например `frm.set_query`.

Пример задачи:

```text
Сначала пользователь выбрал Company
        ↓
в поле Department показать только отделы этой Company
```

Это уже динамический фильтр Link.

## 9. Что происходит при Rename

Допустим:

```text
Department.name = ANALYTICS
```

переименовали в:

```text
DATA-ANALYTICS
```

Штатный Rename Frappe умеет обновлять известные Link references.

Именно поэтому нельзя безопасно заменить Rename ручным SQL вроде:

```sql
UPDATE tabDepartment SET name = ...
```

Frappe должен знать об операции, чтобы обработать связи.

## 10. Dynamic Link — когда тип цели заранее неизвестен

Обычный Link всегда знает DocType цели.

Но иногда один документ должен ссылаться на **разные типы документов**.

Пример: `Activity` может относиться либо к `Request`, либо к `Department`.

Тогда можно хранить два поля:

```text
Reference Type
Field Type: Link
Options: DocType

Reference Name
Field Type: Dynamic Link
Options: reference_type
```

Если:

```text
reference_type = Request
reference_name = REQ-0042
```

ссылка ведёт на Request.

Если:

```text
reference_type = Department
reference_name = ANALYTICS
```

то уже на Department.

## 11. Как мыслить о Dynamic Link

Обычный Link хранит одну часть:

```text
name
```

а тип цели известен из metadata.

Dynamic Link требует две части:

```text
doctype + name
```

То есть фактически:

```text
(Request, REQ-0042)
```

или:

```text
(Department, ANALYTICS)
```

## 12. Когда Dynamic Link действительно нужен

Хороший случай:

```text
универсальный журнал, комментарий или интеграционная запись,
которая по смыслу может относиться к разным DocTypes
```

Плохой случай:

```text
«Я пока не знаю модель, поэтому пусть поле ссылается на что угодно»
```

Dynamic Link делает модель гибче, но одновременно слабее: тип связи уже нельзя понять только по одному fieldname.

Если связь по смыслу всегда ведёт на `Department`, обычный Link лучше.

## 13. Fetch From — взять значение из связанного документа

Допустим, в `Department` есть:

```text
manager_name = Иван Петров
```

А в `Request` есть:

```text
department   Link → Department
manager_name Data
```

Для `manager_name` можно настроить:

```text
Fetch From = department.manager_name
```

Пользователь выбирает Department, и Frappe подставляет имя руководителя.

Пример:

```text
Department = ANALYTICS
        ↓
Fetch From
        ↓
Manager Name = Иван Петров
```

Для такой простой автоподстановки Client Script не нужен.

## 14. Fetch From — это копия, а не живая формула

Это один из самых важных моментов.

Допустим, сегодня:

```text
ANALYTICS.manager_name = Иван Петров
```

Создали Request, и туда скопировалось:

```text
manager_name = Иван Петров
```

Завтра в Department поменяли руководителя:

```text
manager_name = Анна Смирнова
```

Старый Request не обязан автоматически превратиться в `Анна Смирнова` только потому, что использовался Fetch From.

Fetch From — это **денормализованная копия значения в документ**.

## 15. Зачем тогда вообще копировать данные

Иногда это именно то, что нужно.

Например, документ должен сохранить историческое состояние:

```text
кто был руководителем отдела на момент создания заявки
```

Тогда копия полезна.

А если всегда нужно показывать **текущее** значение из Department, возможно, отдельное сохранённое поле вообще не нужно — достаточно читать связанный Document в нужном месте.

## 16. Fetch If Empty

У режима fetch есть вариант не перезаписывать уже заполненное значение.

Сценарий:

```text
Frappe автоматически подставил адрес
        ↓
пользователь вручную уточнил его для конкретного документа
        ↓
повторный fetch не должен затереть исправление
```

Тогда полезен режим `Fetch If Empty`.

## 17. Когда нужна отдельная сущность связи

Представь связь «Сотрудник участвует в Проекте».

Если нужно хранить только факт выбора нескольких сотрудников, иногда хватит простой структуры.

Но если у самой связи есть данные:

```text
Employee
Project
Role in Project
Start Date
End Date
Allocation %
```

это уже самостоятельный объект предметной области.

Лучше сделать отдельный DocType вроде `Project Member`, а не пытаться спрятать всю модель в Dynamic Link или MultiSelect.

## Мини-практика

Представь два DocType:

```text
Department
- department_name
- manager_name

Request
- subject
- department
- manager_name
```

Настрой мысленно:

```text
Request.department
→ Link → Department

Request.manager_name
→ Fetch From → department.manager_name
```

Теперь ответь:

1. Что хранится в `department`? **`name` выбранного Department.**
2. Если Department переименовали штатным Rename, понимает ли Frappe эту связь? **Да, Link metadata известна Framework.**
3. Если изменился `manager_name` в Department, обновится ли автоматически каждый старый Request? **Не обязательно; Fetch From хранит копию.**
4. Когда нужен Dynamic Link? **Когда один field по смыслу может ссылаться на документы разных DocTypes.**

## Что запомнить

- `Link` → один заранее известный DocType.
- Link хранит `name` целевого Document.
- `Dynamic Link` → тип цели берётся из другого поля.
- `Fetch From` → копирует значение из связанного документа.
- Если у самой связи появляются собственные важные поля и lifecycle, подумай об отдельном DocType.

## Официальные источники

- [Field Types — Link and Dynamic Link](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Fetch From guide](https://docs.frappe.io/framework/user/en/guides/app-development/fetch-custom-field-value-from-master-to-all-related-transactions)
- [Document link validation, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/model/base_document.py)
- [Rename implementation, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/model/rename_doc.py)

Следующая глава: [**08. Child Table и Table MultiSelect**](08_CHILD_TABLES.md).