# 08. Child Table и Table MultiSelect на `Request`

У `Request` уже есть обычные поля и ссылка на ответственного. Следующая задача другая: одной заявке нужно хранить **несколько однотипных строк**, которые не имеют самостоятельного смысла без родителя.

Для этого во Frappe используется Child DocType и поле `Table`.

В этой главе добавим к `Request` строки `Request Item`, а затем отдельно увидим `Table MultiSelect` — более компактный вариант множественного выбора, который тоже хранит данные через child rows.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

`Request` содержит накопленную модель, включая:

```text
subject
status
priority
due_date
responsible
responsible_name
```

и остальные поля предыдущих лабораторных.

Новых Child DocTypes пока нет.

---

## Когда нужен Child Table

Представим Request с несколькими строками работ:

```text
Request REQ-2026-00005

Items:
1. Analysis       Qty 2   Rate 50   Amount 100
2. Review         Qty 1   Rate 80   Amount 80
3. Documentation  Qty 3   Rate 20   Amount 60
```

Каждая строка нужна только внутри конкретного Request.

Если удалить сам Request, отдельная строка `Analysis × 2` не является самостоятельным объектом системы.

Это хороший случай для Child Table.

---

## Как собирается Child Table

Нужны две части.

### 1. Child DocType

Создадим:

```text
Request Item
Is Child Table = включено
```

Поля строки:

```text
title
qty
rate
amount
```

### 2. Поле в родительском `Request`

```text
Label:      Items
Fieldname:  items
Field Type: Table
Options:    Request Item
```

После этого Frappe понимает:

```text
Request.items
→ набор child rows типа Request Item
```

---

## Child row — структурированный Document

Строка таблицы — не произвольный JSON и не текстовая ячейка.

У неё есть metadata `Request Item` и системная связь с родителем.

Внутри Frappe для child row важны поля:

```text
parent
parenttype
parentfield
idx
```

Их смысл:

| Поле | Что означает |
|---|---|
| `parent` | `name` родительского Request |
| `parenttype` | DocType родителя, здесь `Request` |
| `parentfield` | поле родителя, здесь `items` |
| `idx` | порядок строки |

В этой главе мы **не открываем Python console**, чтобы посмотреть эти поля напрямую: Python ещё не изучался.

Сейчас достаточно увидеть поведение, которое из них следует:

```text
строки создаются внутри Request
сохраняются вместе с Request
порядок строк сохраняется
валидация строки блокирует Save родителя
```

Позже, когда появится код, к внутренней структуре можно будет вернуться уже осознанно.

---

## Почему child row не создаём как обычный самостоятельный Document

`Request Item` не должен иметь отдельный рабочий список, в котором пользователь создаёт строки независимо от Request.

Модель здесь именно такая:

```text
Request
└── owns → Request Item rows
```

А обычный Link из предыдущей главы означал другое:

```text
Request
└── references → User
```

Полезно различать два слова:

```text
Link        → ссылка
Child Table → принадлежность
```

---

## `idx` и порядок строк

Frappe хранит порядок child rows через `idx`.

Пользователь может переставить строки в grid:

```text
Analysis
Review
Documentation
```

на:

```text
Documentation
Analysis
Review
```

После Save и повторного открытия порядок должен сохраниться.

`idx` — технический порядок строки, а не постоянный бизнес-номер. Не стоит строить предметную идентичность на `idx`.

---

## Валидация child rows идёт вместе с родителем

Сделаем `Request Item.title` обязательным.

Если добавить строку:

```text
Title:  пусто
Qty:    1
Rate:   10
Amount: 10
```

и сохранить Request, Frappe должен остановить сохранение из-за Mandatory-поля дочерней строки.

Это хорошо показывает границу lifecycle:

```text
Save Request
→ Frappe проверяет и его child rows
→ только затем сохраняет согласованное состояние документа
```

---

## Что такое Table MultiSelect

Иногда полная grid-таблица из четырёх колонок не нужна.

Нужно просто выбрать несколько Documents одного типа, например пользователей-наблюдателей:

```text
Watchers:
[Administrator] [Guest]
```

Для этого есть `Table MultiSelect`.

Он тоже использует Child DocType, но показывает выбранные Link-значения компактно.

---

## Почему Table MultiSelect тоже требует Child DocType

В `v16.32.0` control `Table MultiSelect` берёт metadata указанного Child DocType и ищет в нём Link-поле.

Поэтому создадим отдельный Child DocType:

```text
Request Watcher
Is Child Table = включено

User
  fieldname: user
  type: Link
  options: User
```

А в `Request` добавим:

```text
Watchers
Fieldname: watchers
Field Type: Table MultiSelect
Options: Request Watcher
```

Frappe хранит выбранных пользователей как child rows, а показывает их пользователю как компактный набор значений.

---

## Table и Table MultiSelect — разные задачи

### `Table`

Используем, когда одна строка содержит несколько важных значений:

```text
Title | Qty | Rate | Amount
```

### `Table MultiSelect`

Используем, когда основная задача — выбрать несколько связанных Documents:

```text
Administrator
Guest
```

Если у наблюдателя позже понадобятся:

```text
Role
Start Date
Comment
Notification Level
```

простого MultiSelect уже будет мало: понадобится полноценная Table или самостоятельная сущность связи.

---

## Почему оба Child DocType останутся на стенде

`Request Item` нужен дальше как часть основной учебной формы.

`Request Watcher` нужен, чтобы Table MultiSelect был не только теорией, а реально пройденным механизмом.

После этой главы оба объекта оставляем. Они созданы не «для галочки», а потому что два разных field type требуют двух разных форм строк:

```text
Request Item
→ полноценная строка с несколькими полями

Request Watcher
→ одна Link-ссылка для множественного выбора
```

---

## Что произойдёт в лабораторной

Ты:

1. создашь Child DocType `Request Item`;
2. добавишь `Items → Table → Request Item` в существующий Request;
3. создашь Request с несколькими строками;
4. поменяешь порядок строк и увидишь сохранение порядка;
5. добавишь строку без Mandatory `Title` и получишь отказ Save родителя;
6. исправишь строку и сохранишь Request;
7. создашь Child DocType `Request Watcher`;
8. добавишь `Watchers → Table MultiSelect`;
9. выберешь нескольких Users и увидишь компактный множественный выбор.

---

## Что запомнить

1. Child Table означает принадлежность строк родительскому Document.
2. `Table` в родителе указывает через `Options` на Child DocType.
3. Child rows сохраняются и валидируются вместе с родителем.
4. Порядок строк поддерживается Framework.
5. `parent`, `parenttype`, `parentfield`, `idx` объясняют внутреннюю связь, но Python для их изучения пока не нужен.
6. `Table MultiSelect` — компактный множественный Link-выбор поверх child rows.
7. `Table` и `Table MultiSelect` не взаимозаменяемы: выбор зависит от структуры одной строки.

---

## Официальные источники

- [Child / Table DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Table MultiSelect control — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/public/js/frappe/form/controls/table_multiselect.js)
- [Child table handling — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py)

Теперь выполни [**лабораторную 08**](labs/08_CHILD_TABLES_LAB.md).

После неё переходи к [**09. Single, Tree, Submittable и Virtual DocType**](09_SPECIAL_DOCTYPES.md).