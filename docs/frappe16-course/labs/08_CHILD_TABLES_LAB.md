# Лабораторная 08. Child Table и Table MultiSelect

## Что уже должно быть готово

Лабораторная 07 завершена.

`Request` уже содержит постоянную связь:

```text
Responsible       responsible       Link → User
Responsible Name  responsible_name  Fetch From responsible.full_name
```

и все поля предыдущих лабораторных.

Временные Dynamic Link поля удалены.

---

## Что сейчас получим

Создадим два Child DocType:

```text
Request Item
Request Watcher
```

В `Request` добавим:

```text
Items     items     Table → Request Item
Watchers  watchers  Table MultiSelect → Request Watcher
```

После лабораторной они останутся на стенде.

---

# Часть A. Обычная Child Table

## 1. Создай `Request Item`

В Desk открой:

```text
DocType
→ New
```

Создай:

```text
Name:           Request Item
Module:         Training
Is Child Table: включено
Custom?:        выключено
```

---

## 2. Добавь поля `Request Item`

Создай строки Fields.

### Title

```text
Label:        Title
Fieldname:    title
Field Type:   Data
Mandatory:    включено
In List View: включено
```

### Qty

```text
Label:        Qty
Fieldname:    qty
Field Type:   Float
Default:      1
In List View: включено
```

### Rate

```text
Label:        Rate
Fieldname:    rate
Field Type:   Currency
In List View: включено
```

### Amount

```text
Label:        Amount
Fieldname:    amount
Field Type:   Currency
In List View: включено
```

Сохрани DocType.

Не добавляй формулы или scripts: `Amount` в этой лабораторной заполняется руками. Автоматические вычисления будут позже, когда появится соответствующий механизм.

---

## 3. Добавь `Items` в `Request`

Открой DocType:

```text
Request
```

Добавь поле:

```text
Label:      Items
Fieldname:  items
Field Type: Table
Options:    Request Item
```

Сохрани `Request`.

---

## 4. Создай Request с тремя строками

Создай новый Request:

```text
Subject:      Проверить Child Table
Status:       Open
Priority:     Medium
Due Date:     2026-09-11
Responsible: Administrator
```

В `Items` добавь строки:

| Title | Qty | Rate | Amount |
|---|---:|---:|---:|
| Analysis | 2 | 50 | 100 |
| Review | 1 | 80 | 80 |
| Documentation | 3 | 20 | 60 |

Нажми Save.

Ожидаемый результат:

```text
Request сохранился
+
три строки Items сохранились вместе с ним
```

---

## Проверь принадлежность строк

Вернись в Request List и снова открой этот же Request.

Три строки должны остаться внутри поля `Items`.

Теперь попробуй через глобальный поиск Desk найти `Request Item` как обычный рабочий список для самостоятельного создания записей.

Child DocType предназначен для использования внутри родителя, а не как независимый справочник, который пользователь наполняет отдельными Documents.

Главное наблюдение:

```text
Request Item row
→ существует в контексте Request.items
```

---

## Эксперимент — порядок строк

В `Items` поменяй порядок на:

```text
Documentation
Analysis
Review
```

Сохрани Request.

Обнови страницу или выйди в List View и снова открой документ.

Ожидается тот же порядок:

```text
Documentation
Analysis
Review
```

Так пользователь наблюдает работу порядка child rows без Python console.

---

## Намеренная ошибка — Mandatory внутри child row

Добавь ещё одну строку `Items`:

```text
Title:  оставить пустым
Qty:    1
Rate:   10
Amount: 10
```

Нажми Save у **родительского Request**.

Ожидаемый результат:

```text
Request не сохраняет некорректное состояние
→ Frappe указывает на обязательное поле Title в дочерней строке
```

То есть validation Child Table участвует в сохранении родителя.

---

## Восстановление

В той же строке заполни:

```text
Title: Correction
```

Снова нажми Save.

Теперь Request должен успешно сохраниться уже с четырьмя строками.

---

# Часть B. Table MultiSelect

## 5. Создай `Request Watcher`

Открой:

```text
DocType
→ New
```

Создай:

```text
Name:           Request Watcher
Module:         Training
Is Child Table: включено
Custom?:        выключено
```

Добавь одно поле:

```text
Label:      User
Fieldname:  user
Field Type: Link
Options:    User
Mandatory:  включено
```

Сохрани DocType.

---

## 6. Добавь `Watchers` в `Request`

Открой DocType `Request` и добавь:

```text
Label:      Watchers
Fieldname:  watchers
Field Type: Table MultiSelect
Options:    Request Watcher
```

Сохрани `Request`.

---

## 7. Проверь множественный выбор

Открой Request, который использовался в части A.

В поле `Watchers` последовательно выбери:

```text
Administrator
Guest
```

Сохрани Request.

Ожидаемое поведение:

```text
оба User отображаются компактно как выбранные значения
→ внутри документа Frappe хранит их через child rows Request Watcher
```

---

## Эксперимент — удаление одного значения

Удалить из `Watchers`:

```text
Guest
```

Сохрани Request и снова открой его.

Ожидается:

```text
Administrator остался
Guest отсутствует
```

Затем снова добавь `Guest` и сохрани, чтобы итоговый Request содержал два Watchers.

---

## Проверка себя

Ответь без подсказки.

1. Почему `Request Item` — Child DocType, а `User` — обычный самостоятельный DocType?
2. Что означает `Options = Request Item` у поля `items`?
3. Почему ошибка в Mandatory `Title` блокировала Save родительского Request?
4. Что изменилось после перестановки строк и Save?
5. Чем `Table` отличается от `Table MultiSelect`?
6. Зачем `Request Watcher` содержит Link → User?
7. Какие два новых поля должны остаться в `Request`?

---

## Состояние стенда после лабораторной

Новые Standard Child DocTypes:

```text
Request Item
- title   Data      Mandatory
- qty     Float     Default 1
- rate    Currency
- amount  Currency

Request Watcher
- user    Link → User   Mandatory
```

В `Request` добавлены:

```text
Items
  fieldname: items
  type:      Table
  options:   Request Item

Watchers
  fieldname: watchers
  type:      Table MultiSelect
  options:   Request Watcher
```

Есть минимум один Request с:

```text
4 Request Item rows
Watchers: Administrator, Guest
```

Никакой Python/bench console в этой лабораторной не использовался.

Это точное входное состояние [**главы 09**](../09_SPECIAL_DOCTYPES.md).