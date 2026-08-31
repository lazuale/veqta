# 11. Form View: как metadata превращается в рабочую форму

В блоке B мы постепенно собрали реальный `Request`: добавили обычные поля, Link, Fetch From, Child Table, Table MultiSelect и naming.

Теперь впервые смотрим на этот объект не как на набор metadata, а как на **рабочую форму пользователя**.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

После лабораторной 10 `Request` уже существует и содержит:

```text
Subject
Description
Status
Due Date
Priority
Is Urgent
Estimate Hours
Notes
Reference File
Responsible
Responsible Name
Items
Watchers
```

Naming новых документов:

```text
REQ-.YYYY.-.#####
```

Также уже есть:

```text
Request Item
Request Watcher
Training Settings
Training Category
Approval Record
```

В этой главе новый бизнес-объект не создаём. Работаем с тем же `Request`.

---

## Что такое Form View

`Form View` — штатный экран одного Document.

Когда ты открываешь конкретный Request:

```text
REQ-2026-00001
```

Frappe получает metadata DocType `Request`, данные этого Document и строит форму.

Связь выглядит так:

```text
DocType Request
+ DocField metadata
+ Request Document
        ↓
     Form View
```

Поэтому обычную внутреннюю форму Frappe не нужно начинать с собственного HTML, React или Vue.

---

## Форма уже знает тип каждого поля

Мы ранее задали:

```text
Priority         Select
Due Date         Date
Is Urgent        Check
Responsible      Link → User
Responsible Name Data + Read Only + Fetch From
Items            Table → Request Item
Watchers         Table MultiSelect → Request Watcher
```

Form View использует эти сведения напрямую.

Поэтому пользователь получает не одинаковые текстовые поля, а подходящие элементы интерфейса:

```text
Select            → список вариантов
Date              → ввод даты
Check             → флаг
Link              → поиск существующего User
Table             → дочерний grid
Table MultiSelect → множественный выбор
```

Это видимое следствие metadata, которое мы настраивали в блоке B.

---

## `name` и Title Field на форме

У Request есть два разных значения:

```text
name    = REQ-2026-00001
subject = Проверить отчёт
```

`name` остаётся системным идентификатором Document.

`subject` назначен как `Title Field`, поэтому интерфейс может показывать человеку понятный заголовок.

Изменение `Subject` не создаёт новый Request и не обязано менять `name`.

---

## Новая форма и сохранённый Document

Один и тот же Form View используется в двух состояниях.

### Новый Document

После `New` существует форма нового Request, но записи в базе ещё нет.

После заполнения и Save Frappe создаёт Document и назначает ему `name`.

### Существующий Document

Когда открываем `REQ-2026-00001`, форма уже загружает сохранённые значения.

После изменения поля форма становится несохранённой, пока пользователь снова не нажмёт Save.

Главное различие:

```text
форма может показывать новый или существующий Document
```

но тип данных остаётся один — `Request`.

---

## Почему длинная плоская форма неудобна

Сейчас поля `Request` уже решают разные задачи:

```text
идентификация
статус и сроки
ответственный
срочность
описание
файл
дочерние строки
наблюдатели
```

Если оставить их одной длинной колонкой, Framework всё отобразит, но пользователю придётся самому угадывать структуру.

Frappe позволяет задать layout той же metadata.

Для этого используются:

```text
Tab Break
Section Break
Column Break
```

Они не создают новые бизнес-данные. Они организуют существующие поля.

---

## Tab Break

`Tab Break` начинает новую вкладку формы.

Для нашего Request в лабораторной будет две вкладки:

```text
Main
Details
```

`Main` содержит то, что нужно для ежедневной работы.

`Details` — описание, файл и дочерние данные.

---

## Section Break

`Section Break` начинает смысловой блок внутри вкладки.

Например:

```text
General
Responsibility
Urgent Details
Description
Files
Items
```

Секция помогает читать форму как последовательность рабочих частей, а не как перечень технических полей.

---

## Column Break

`Column Break` делит текущую секцию на колонки.

Например:

```text
Subject        Priority
Status         Due Date
```

Здесь по-прежнему четыре обычных DocField. Изменилась только раскладка.

---

## Канонический layout курса

В лабораторной 11 мы оставим `Request` в таком состоянии:

```text
Tab: Main

  Section: General
    Subject      | Priority
    Status       | Due Date
    Is Urgent

  Section: Responsibility
    Responsible  | Responsible Name
    Watchers

  Section: Urgent Details
    Display Depends On: eval:doc.is_urgent
    Estimate Hours

Tab: Details

  Section: Description
    Description
    Notes

  Section: Files
    Reference File

  Section: Items
    Items
```

Так последующие главы работают с одной и той же формой.

---

## Условная видимость без Client Script

У `DocField` и layout-полей есть `Display Depends On`.

Для секции `Urgent Details` мы зададим:

```text
eval:doc.is_urgent
```

Результат:

```text
Is Urgent = 0
→ секция Urgent Details скрыта

Is Urgent = 1
→ секция появляется
```

Это важная граница: для простой реакции формы на значения Document отдельный Client Script не нужен.

Client Script будет изучаться значительно позже, в главе 44.

---

## Mandatory, Read Only и Fetch From продолжают работать после перестройки

Layout не отменяет свойства полей.

После переноса `Subject` в другую секцию он всё ещё:

```text
Mandatory
```

`Responsible Name` всё ещё:

```text
Read Only
Fetch From = responsible.full_name
```

`Items` всё ещё:

```text
Table → Request Item
```

То есть layout отвечает за расположение, а свойства DocField — за смысл и поведение конкретного поля.

---

## Child Table в Form View

Поле:

```text
Items → Table → Request Item
```

отображается внутри формы как grid.

Пользователь добавляет строки внутри Request, потому что `Request Item` принадлежит родительскому Document.

Перестройка вкладок не меняет эту модель владения.

---

## Table MultiSelect в Form View

Поле:

```text
Watchers → Table MultiSelect → Request Watcher
```

показывает выбранных Users как множественные значения.

Под капотом остаются child rows `Request Watcher`, но пользователь работает с более компактным контролом.

---

## Поля интерфейса и сервисы вокруг формы — не одно и то же

Form View содержит не только поля DocType. Вокруг Document Frappe предоставляет другие механизмы, например:

```text
Attachments
Comments / Timeline
Assignments
Sharing
Tags
```

В этом блоке мы их подробно не изучаем.

Важно только не путать:

```text
Reference File
→ конкретный DocField Attach внутри Request

Attachments
→ общий сервис вложений вокруг Document
```

Аналогично `Responsible Link → User` не равен штатному механизму Assignment. Assignment будет отдельной главой позже.

---

## Что сейчас не нужно писать

Для текущего `Request` нам не нужен собственный frontend.

Также в этой главе не пишем:

```text
JavaScript Form Script
Python controller
REST API
собственный Page
```

Ученик должен сначала увидеть пределы metadata на живой форме.

---

## Что произойдёт в лабораторной

Ты:

1. перестроишь существующий `Request` в две вкладки;
2. разложишь поля по точным Section/Column Break;
3. сделаешь `Urgent Details` условной секцией;
4. проверишь поведение на обычном Request;
5. намеренно скроешь секцию с Mandatory `Subject` неправильным условием и получишь воспроизводимый отказ Save;
6. вернёшь правильный layout.

После лабораторной данные Request сохранятся, а изменится только Standard metadata формы.

---

## Что запомнить

1. Form View — штатный экран одного Document.
2. Базовая форма строится из DocType и DocField metadata.
3. `Tab Break`, `Section Break`, `Column Break` меняют layout, а не модель данных.
4. `Display Depends On` закрывает простые условные сценарии без Client Script.
5. Свойства `Mandatory`, `Read Only`, `Fetch From`, `Table` продолжают работать независимо от расположения поля.
6. Сначала нужно использовать штатную форму; собственный UI появляется только при доказанной необходимости.

---

## Официальные источники

- [Create a DocType — Form Layout](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Form API](https://docs.frappe.io/framework/user/en/api/form)
- [DocField source — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/docfield/docfield.json)

Теперь выполни [**лабораторную 11**](labs/11_FORM_VIEW_LAB.md).

После неё переходи к [**12. List View и фильтры**](12_LIST_VIEW_AND_FILTERS.md).
