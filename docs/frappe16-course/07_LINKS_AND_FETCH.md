# 07. Link, Dynamic Link и Fetch From на существующем `Request`

До этого все значения `Request` жили внутри самого документа: текст, дата, приоритет, флаг, файл.

Теперь заявке нужен ответственный пользователь. Пользователь уже существует как отдельный Document системного DocType `User`, поэтому копировать его имя обычным `Data` вручную было бы неправильно. Нужна связь между двумя Documents.

В этой главе добавим к `Request` постоянную связь `Responsible → User`, автоматически подтянем `full_name` через `Fetch From` и отдельно проверим, чем обычный `Link` отличается от `Dynamic Link`.

Проверено для **Frappe Framework v16.32.0**. В системном DocType `User` этой версии поле `full_name` действительно существует.

---

## Что уже есть на стенде

`Request` сохраняет модель из лаборатории 06:

```text
subject
description
status
due_date
priority
is_urgent
estimate_hours
notes
reference_file
```

Naming:

```text
Title Field: subject
Auto Name:   REQ-.YYYY.-.#####
```

Есть старые Request Documents и новые Documents серии `REQ-2026-.....`.

---

## Зачем здесь нужен `Link`

Мы хотим добавить поле:

```text
Responsible
```

Ответственный — не произвольная строка. Это один из существующих пользователей Frappe.

Поэтому модель будет такой:

```text
Request.responsible
        │
        └── Link → User
```

В `Options` поля Link указывается DocType цели:

```text
Options = User
```

Теперь Frappe знает, что значение должно ссылаться именно на Document `User`.

---

## Что хранит Link

Обычный Link хранит системный `name` выбранного Document.

Например:

```text
Responsible = Administrator
```

означает:

```text
DocType цели: User
name цели:    Administrator
```

Тип цели известен из metadata поля:

```text
Field Type: Link
Options:    User
```

Поэтому в самом значении достаточно хранить `name`.

---

## Почему не использовать обычный `Data`

Если сделать Responsible строкой, можно получить:

```text
Administrator
administrator
Admin
Аминистратор
```

Frappe не будет знать, какой реальный User имеется в виду.

Link даёт другую модель:

```text
выбираем существующий Document
→ Frappe знает его DocType
→ Frappe проверяет существование ссылки
```

В лабораторной мы намеренно введём несуществующего User и увидим штатный отказ.

---

## `Fetch From`: копируем понятное значение из связанного Document

Системный `User` имеет поле:

```text
full_name
```

К `Request` добавим второе поле:

```text
Responsible Name
Fieldname: responsible_name
Field Type: Data
Read Only: включено
Fetch From: responsible.full_name
```

Последовательность будет такой:

```text
выбрали Responsible = Administrator
        ↓
Frappe открыл связанную запись User
        ↓
взял full_name
        ↓
заполнил Responsible Name
```

Для простой автоподстановки не нужен Client Script.

---

## Link и Fetch From решают разные задачи

После настройки у `Request` будут два значения:

```text
responsible
→ ссылка на конкретный User

responsible_name
→ скопированное значение full_name этого User
```

`responsible` отвечает на вопрос:

> на какой Document мы ссылаемся?

`responsible_name` отвечает:

> какое удобное значение мы скопировали из связанного Document?

Это не одна и та же роль поля.

---

## Fetch From — не живая формула

Важно не ожидать от `responsible_name` поведения постоянного JOIN.

При Fetch From Frappe подставляет значение из связанного Document в поле текущего документа.

Если позже исходный `User.full_name` изменится, уже сохранённый `Request` не нужно воспринимать как автоматически синхронизирующуюся витрину.

Для курса достаточно модели:

```text
Link       → связь
Fetch From → копирование значения по этой связи
```

---

## Что такое `Dynamic Link`

У обычного Link тип цели фиксирован заранее:

```text
Responsible
→ всегда User
```

Иногда тип цели должен определяться другим полем.

Для краткого опыта добавим временную пару:

```text
Reference Type
Field Type: Link
Options: DocType

Reference Name
Field Type: Dynamic Link
Options: reference_type
```

Теперь сначала выбирается тип документа:

```text
Reference Type = User
```

а второе поле уже ссылается на Document этого типа:

```text
Reference Name = Administrator
```

Если поменять:

```text
Reference Type = Request
```

то `Reference Name` начинает выбирать уже Request Documents.

---

## Разница в одной схеме

### Обычный Link

```text
metadata знает тип цели

Responsible
Link → User
value = Administrator
```

### Dynamic Link

```text
тип цели хранится в другом поле

Reference Type = Request
Reference Name = REQ-2026-00001
```

То есть для Dynamic Link нужны две части:

```text
DocType цели
+
name цели
```

---

## Почему Dynamic Link не оставляем в `Request`

Наш `Request` по своей модели уже имеет конкретную связь:

```text
Responsible → User
```

Универсальная пара `Reference Type / Reference Name` дальше курсу не нужна и только размоет модель.

Поэтому в лабораторной Dynamic Link будет **временным экспериментом**:

```text
добавили
→ увидели переключение типа цели
→ удалили оба временных поля
```

Итоговое состояние снова будет однозначным.

---

## Что пока не изучаем

Вокруг Link есть дополнительные механизмы:

```text
фильтрация вариантов
User Permissions
Ignore User Permissions
динамические query из Client Script
Rename связанных Documents
```

Они появятся позже там, где будут нужны практике.

Сейчас задача уже достаточная:

```text
Link
Dynamic Link
Fetch From
проверка существования ссылки
```

---

## Что произойдёт в лабораторной

Ты:

1. добавишь `Responsible → User`;
2. добавишь `Responsible Name` с `Fetch From = responsible.full_name`;
3. выберешь разных Users и увидишь изменение fetched value;
4. намеренно введёшь несуществующего User и получишь отказ Link validation;
5. восстановишь корректную ссылку;
6. временно добавишь Dynamic Link пару;
7. переключишь её между `User` и `Request`;
8. удалишь временную пару;
9. оставишь только постоянные поля `Responsible` и `Responsible Name`.

---

## Что запомнить

1. `Link` ссылается на Document одного заранее известного DocType.
2. В Link хранится `name` целевого Document.
3. `Options` Link определяет DocType цели.
4. `Fetch From` копирует значение из связанного Document.
5. `Dynamic Link` берёт DocType цели из другого поля.
6. Dynamic Link нужен только тогда, когда тип цели действительно должен меняться.
7. Для постоянной модели `Request` оставляем `Responsible → User` и `Responsible Name`.

---

## Официальные источники

- [Field Types — Link and Dynamic Link](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Fetch From guide](https://docs.frappe.io/framework/user/en/guides/app-development/fetch-custom-field-value-from-master-to-all-related-transactions)
- [User DocType — `full_name`, v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/user/user.json)
- [Link validation source — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/base_document.py)

Теперь выполни [**лабораторную 07**](labs/07_LINKS_AND_FETCH_LAB.md).

После неё переходи к [**08. Child Table и Table MultiSelect**](08_CHILD_TABLES.md).