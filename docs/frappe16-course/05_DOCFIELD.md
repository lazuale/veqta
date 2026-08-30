# 05. DocField и свойства полей

Эта глава разбирает **DocField** — описание одного поля внутри DocType.

Если DocType отвечает на вопрос:

> какие документы существуют и как они в целом устроены?

то DocField отвечает:

> какие данные есть внутри документа, как они хранятся, отображаются, проверяются и участвуют в интерфейсе?

Проверено: **2026-08-30**.

---

## 1. Что такое DocField

Поле DocType во Frappe — не просто колонка базы данных.

Оно имеет metadata:

```text
Label
Fieldname
Field Type
Options
Default
Mandatory
Read Only
Hidden
Permissions
Display settings
Search settings
Conditional behavior
и другие свойства
```

Эта metadata используется сразу несколькими частями Framework:

```text
DocType metadata
      │
      ├── форма Desk
      ├── Web Form
      ├── List / Report / Filters
      ├── validation
      ├── permissions
      ├── import/export
      ├── print
      └── schema / storage
```

Поэтому выбор типа поля и его свойств — это уже проектирование приложения.

---

## 2. Три базовых свойства каждого обычного поля

### Label

Человеческое название поля.

Например:

```text
Due Date
```

### Fieldname

Внутреннее имя:

```text
due_date
```

Именно оно используется в Python и JavaScript:

```python
doc.due_date
```

```javascript
frm.doc.due_date
```

### Field Type

Определяет тип данных и UI-компонент:

```text
Date
Link
Select
Check
Table
Text Editor
...
```

---

## 3. Label и Fieldname — не одно и то же

Label можно изменить для пользователя.

Fieldname после начала эксплуатации лучше считать частью технического API модели.

Например:

```text
Label:
Срок выполнения

Fieldname:
due_date
```

Позже Label можно заменить на:

```text
Плановая дата
```

не меняя код, который использует:

```text
due_date
```

---

# Часть I. Типы полей

## 4. Текущий набор Field Types в Frappe

В metadata `DocField` Frappe присутствуют такие типы:

```text
Autocomplete
Attach
Attach Image
Attachment Gallery
Barcode
Button
Check
Code
Color
Column Break
Currency
Data
Date
Datetime
Duration
Dynamic Link
Float
Fold
Geolocation
Heading
HTML
HTML Editor
Icon
Image
Int
JSON
Link
Long Text
Markdown Editor
Password
Percent
Phone
Read Only
Rating
Section Break
Select
Signature
Small Text
Tab Break
Table
Table MultiSelect
Text
Text Editor
Time
```

Не все из них являются обычными колонками данных. Часть — layout/UI элементы.

---

## 5. Data

Самое универсальное короткое текстовое поле.

Примеры:

```text
Название
Артикул
Код
Внешний ID
Email
URL
```

`Options` может включать специальные варианты валидации, например:

```text
Name
Email
Phone
URL
IBAN
```

### Когда использовать

Когда значение является короткой строкой и не требует отдельного специализированного типа.

### Когда не использовать

Не хранить в Data всё подряд только потому, что это проще.

Например дата должна быть `Date`, число — `Int/Float`, связь — `Link`.

---

## 6. Small Text, Text, Long Text

Это текстовые поля разного назначения и размера UI.

Упрощённо:

```text
Small Text
→ короткий многострочный текст

Text
→ обычный многострочный текст

Long Text
→ большой текст
```

Если тексту нужно форматирование, лучше смотреть на `Text Editor`, `Markdown Editor` или `HTML Editor`.

---

## 7. Text Editor

Форматированный rich-text.

Подходит для:

```text
описаний
инструкций
комментариев предметной модели
длинного форматированного контента
```

Не использовать вместо простого Data/Text, если форматирование не требуется.

---

## 8. Markdown Editor и HTML Editor

### Markdown Editor

Поле для редактирования Markdown.

### HTML Editor

Поле для HTML-контента.

Это уже более специализированные варианты.

Не следует хранить HTML без необходимости: он сложнее с точки зрения безопасности и дальнейшего использования данных.

---

## 9. Int

Целое число:

```text
0
1
25
1000
```

Примеры:

```text
Количество
Порядковый номер
Число повторов
```

---

## 10. Float

Число с дробной частью.

Например:

```text
12.5
0.75
```

Для Float можно задавать `Precision`.

---

## 11. Currency

Числовое поле для денежных значений.

Использует денежное форматирование Frappe.

Если значение действительно является деньгами, лучше использовать Currency, а не Float.

---

## 12. Percent

Число, отображаемое как процент.

Например:

```text
75 %
```

Для Float, Currency и Percent Framework поддерживает настройку `Precision`.

---

## 13. Non Negative, Min Value и Max Value

Для числовых полей существуют ограничения значения.

Например:

```text
Quantity

Non Negative = ✓
Min Value = 0
Max Value = 100
```

Это лучше, чем писать простую числовую проверку вручную, если штатного constraint достаточно.

---

## 14. Check

Boolean:

```text
0 / 1
false / true
```

В интерфейсе — флажок.

Пример:

```text
Active
Archived
Requires Review
```

---

## 15. Select

Выбор одного значения из заранее известного списка.

Например Options:

```text
Low
Normal
High
Critical
```

### Важно

Select хорош, если список:

- короткий;
- стабильный;
- не требует отдельной metadata;
- не управляется пользователями как справочник.

Если значения должны иметь свои поля, права, настройки или регулярно меняться — обычно нужен отдельный DocType + Link.

---

## 16. Sort Options

Для `Select` существует свойство:

```text
Sort Options
```

Оно позволяет сортировать варианты.

Не включать его, если порядок Options несёт смысл.

Например:

```text
Low
Normal
High
Critical
```

логический порядок лучше сохранить вручную.

---

## 17. Date

Дата без времени.

Пример:

```text
2026-08-30
```

Использовать, если время суток не имеет значения.

---

## 18. Datetime

Дата и время.

Пример:

```text
2026-08-30 18:30:00
```

Использовать для точек времени:

```text
создано в
закрыто в
начало события
```

---

## 19. Time

Только время суток.

Пример:

```text
08:00:00
```

Это не Duration.

---

## 20. Duration

Продолжительность.

Например:

```text
2 часа 30 минут
```

Для Duration в DocField есть специальные настройки:

```text
Hide Days
Hide Seconds
```

Использовать для длительности, а не для времени суток.

---

## 21. Link

Один из самых важных типов Frappe.

`Link` связывает документ с документом другого DocType.

Например:

```text
Request.department
      │
      ▼
Department
```

В `Options` указывается целевой DocType:

```text
Options = Department
```

Framework даёт lookup/search интерфейс и использует permission model при выборе связанных документов.

### Главное правило

Если значение является ссылкой на самостоятельную сущность, обычно нужен `Link`, а не Data с названием сущности.

---

## 22. Link Filters

Для Link можно задать штатные filters.

Например показывать только:

```text
Department.active = 1
```

В текущем DocField для этого существует свойство `Filters` / `link_filters`.

Не каждый фильтр Link требует Client Script.

---

## 23. Ignore User Permissions

Для Link, Dynamic Link и Table MultiSelect существует настройка:

```text
Ignore User Permissions
```

Она влияет на применение User Permissions к выбору связанного объекта.

Это security-sensitive настройка.

Её нельзя включать просто для того, чтобы «в выпадающем списке всё показывалось».

---

## 24. Remember Last Selected Value

Для Link существует:

```text
Remember Last Selected Value
```

Frappe может запомнить последнее выбранное значение и использовать его в дальнейшем UX.

Полезно для часто повторяемого ввода, но может быть вредно там, где автоматическое повторение значения повышает риск ошибки.

---

## 25. Dynamic Link

`Dynamic Link` нужен, когда целевой DocType определяется другим полем документа.

Концептуально:

```text
Reference Type = Vehicle
Reference      = VEH-001
```

или:

```text
Reference Type = Employee
Reference      = EMP-001
```

То есть один столбец может ссылаться на документы разных DocTypes.

Использовать только если такая полиморфная связь действительно нужна.

---

## 26. Table

`Table` показывает Child Table внутри документа.

`Options` указывает Child DocType.

Например:

```text
Order
└── Items
    ├── Product
    ├── Quantity
    └── Price
```

Это не просто UI-таблица: строки являются child documents.

---

## 27. Allow Bulk Edit

Для Table существует:

```text
Allow Bulk Edit
```

Она разрешает массовое редактирование строк grid.

Полезность зависит от характера данных.

---

## 28. Table MultiSelect

Используется для множественного выбора связанных объектов через child-структуру.

Это более специализированный механизм, чем обычный Link.

Если нужен один объект — Link.

Если требуется полноценный child record с несколькими атрибутами — Table.

Если нужна именно множественная связь — можно рассматривать Table MultiSelect.

---

## 29. Attach

Поле для одного файла.

Использовать, когда файл имеет конкретный смысл:

```text
Signed Contract
Certificate
Main Document
```

Для обычных приложений к документу не обязательно создавать отдельные Attach-поля — у Document уже существует attachment infrastructure.

---

## 30. Attach Image

То же направление, но поле ориентировано на изображение.

Например:

```text
Profile Image
Main Photo
```

---

## 31. Attachment Gallery

Галерея вложений.

Это отдельный UI-oriented field type.

---

## 32. Make Attachment Public

Для attachment-полей есть настройка:

```text
Make Attachment Public (by default)
```

Это влияет на приватность файла.

Нельзя включать её без понимания последствий доступа.

---

## 33. Password

Поле для чувствительного строкового значения с password-style UI.

Сам факт наличия Password field не означает, что туда безопасно складывать любые секреты архитектуры без понимания механизмов хранения и доступа.

Для credentials и интеграционных секретов позже отдельно разберём password/config mechanisms Frappe.

---

## 34. Phone

Специализированное поле для телефонного значения.

Не путать с `Data` + Options = Phone: в текущем Frappe присутствует и отдельный тип `Phone`.

---

## 35. Barcode

Поле с barcode-oriented представлением.

Используется, когда значение должно работать как штрихкод.

---

## 36. Color

Выбор цвета.

Хранит цветовое значение и даёт соответствующий UI.

---

## 37. Rating

Поле рейтинга.

Подходит для сценариев с оценкой.

---

## 38. Signature

Поле для подписи, вводимой через соответствующий интерфейс.

Не следует автоматически считать его юридически значимой электронной подписью: это отдельный вопрос требований и законодательства.

---

## 39. Geolocation

Поле геолокации.

Позволяет работать с географическими данными через штатный компонент.

---

## 40. JSON

Поле для JSON-структуры.

Это мощный, но потенциально опасный escape hatch.

Не следует заменять нормальную модель DocTypes одним большим JSON только потому, что так быстрее.

Использовать, когда данные действительно являются динамической JSON-конфигурацией, а не обычной предметной структурой.

---

## 41. Code

Поле редактирования кода.

`Options` может определять язык/режим редактора.

Используется в настройках, scripts и технических DocTypes.

---

## 42. Read Only

Есть два похожих понятия:

```text
Field Type = Read Only
```

и

```text
свойство Read Only = ✓
```

Практически чаще используется обычный подход:

```text
нормальный Field Type
+
Read Only property
```

когда поле хранит конкретный тип данных, но пользователь не должен его редактировать.

---

## 43. Autocomplete

Текстовый ввод с подсказками/autocomplete поведением.

Это не полноценная связь как Link.

Если нужна referential связь с документом — Link правильнее.

---

# Часть II. Layout-поля

## 44. Section Break

Начинает секцию формы.

Можно использовать для группировки:

```text
Основное
Сроки
Результат
Дополнительно
```

---

## 45. Column Break

Разделяет текущую секцию на колонки.

Например:

```text
Subject       Priority
Department    Due Date
```

---

## 46. Tab Break

Создаёт вкладку формы.

Использовать для действительно крупных логических разделов.

Не превращать форму из пяти полей в десять вкладок.

---

## 47. Heading

Визуальный заголовок внутри layout.

Не хранит предметное значение.

---

## 48. HTML

Позволяет вставлять HTML-контент в форму.

Это UI field, а не обычное пользовательское значение.

---

## 49. Button

Кнопка на форме.

Само наличие Button не реализует действие.

Обычно обработчик задаётся через Client Script или JavaScript приложения.

У Button есть настройка `Button Color`.

---

## 50. Image и Icon

UI-oriented типы для визуального представления.

Их поведение отличается от `Attach Image`, который является файловым полем.

---

## 51. Fold

Layout/UI field type, используемый Framework для организации отображения содержимого.

Это не поле предметных данных.

---

# Часть III. Основные свойства поведения поля

## 52. Mandatory

В metadata поле называется:

```text
reqd
```

В UI:

```text
Mandatory
```

Если включено, документ нельзя корректно сохранить без значения поля.

### Правило

Mandatory должно означать:

> без этого значения документ в данном состоянии не имеет смысла.

Не использовать Mandatory просто для того, чтобы пользователь «заполнял всё аккуратно».

---

## 53. Default

Значение по умолчанию.

Например:

```text
Priority = Normal
Active = 1
```

Default уменьшает ручной ввод, но не заменяет бизнес-логику.

---

## 54. Unique

Требует уникальности значения поля.

Например:

```text
External ID
Employee Number
Serial Number
```

Если уникальность является частью модели, лучше задать её metadata, а не только проверять на форме JavaScript.

---

## 55. Read Only

Запрещает обычное редактирование пользователем в форме.

Хорошо подходит для:

```text
расчётных значений
системно заполненных дат
внешних ID
агрегатов
```

Но Read Only в UI не следует воспринимать как самостоятельную security boundary для любого произвольного server-side сценария.

---

## 56. Hidden

Скрывает поле в обычной форме.

Hidden не означает:

```text
значение не существует
```

или:

```text
данные автоматически защищены от API
```

Это прежде всего свойство представления.

---

## 57. Set Only Once

Свойство:

```text
Set only once
```

означает, что после первоначальной установки значение не должно свободно изменяться.

Полезно для immutable-like атрибутов.

---

## 58. No Copy

При дублировании документа значение поля не переносится в копию.

Примеры:

```text
External ID
Approval Timestamp
Unique Reference
```

То есть:

```text
Duplicate document
```

не обязан означать:

```text
скопировать абсолютно все значения
```

---

## 59. Allow on Submit

Для Submittable DocType после Submit большинство данных блокируется от редактирования.

Поле с:

```text
Allow on Submit
```

можно изменять и после Submit.

Использовать очень осознанно, потому что это исключение из модели зафиксированного документа.

---

## 60. Not Nullable

В текущем DocField есть настройка:

```text
Not Nullable
```

Она относится к ограничению хранения `NULL`.

Это не то же самое, что UX-смысл `Mandatory`.

Упрощённо:

```text
Mandatory
→ значение требуется на уровне документа/формы

Not Nullable
→ ограничение представления значения в storage/schema
```

---

## 61. Length

Для ряда типов можно задавать длину поля.

Не увеличивать её бесконечно «на всякий случай».

Тип и длина должны соответствовать реальным данным.

---

## 62. Precision

Для:

```text
Float
Currency
Percent
```

можно задать количество знаков после десятичного разделителя.

Например:

```text
2
```

для денежных сумм, если это соответствует задаче.

---

## 63. Mask

В текущем DocField присутствует свойство:

```text
Mask
```

для ряда типов.

Оно маскирует отображение значения в интерфейсе.

Не путать masking с полноценным разграничением доступа: пользовательские права всё равно должны быть настроены отдельно.

---

# Часть IV. Автоматическое получение значений

## 64. Fetch From

Одна из самых полезных low-code возможностей поля.

Допустим:

```text
Request.department → Department
```

у Department есть:

```text
manager
```

Можно сделать поле:

```text
Department Manager
```

и задать:

```text
Fetch From = department.manager
```

Тогда Frappe умеет подтягивать значение из связанного документа.

### Почему это важно

Не каждый перенос значения из Link требует Client Script или Python.

---

## 65. Fetch on Save if Empty

В metadata свойство называется:

```text
fetch_if_empty
```

UI:

```text
Fetch on Save if Empty
```

Подсказка Framework поясняет:

- если включено — значение повторно fetch'ится на save только когда поле пустое;
- если выключено — значение может обновляться из источника при сохранении.

Это влияет на то, является поле snapshot-копией или постоянно синхронизируемым отображением связанного значения.

---

# Часть V. Условное поведение без Client Script

## 66. Display Depends On

Metadata:

```text
depends_on
```

UI:

```text
Display Depends On (JS)
```

Например:

```text
eval:doc.status=="Closed"
```

Поле показывается только при выполнении условия.

---

## 67. Mandatory Depends On

Можно сделать поле обязательным только при условии.

Например:

```text
Result
```

обязательно только если:

```text
status == "Closed"
```

Это лучше простого Client Script, если правило укладывается в штатную metadata.

---

## 68. Read Only Depends On

Позволяет условно блокировать редактирование.

Например:

```text
если approved == 1
→ поле становится Read Only
```

---

## 69. Collapsible Depends On

Для collapsible Section Break можно условно управлять сворачиванием секции.

Это UI-механизм layout.

---

## 70. Важная граница Depends On

Эти выражения прежде всего управляют поведением формы.

Не надо делать вывод:

> раз поле скрыто или стало read-only через JS expression, сервер автоматически защищён от любого обхода.

Критичные бизнес-инварианты должны проверяться server-side.

---

# Часть VI. List, Search и Filters

## 71. In List View

Поле показывается в List View.

Выбирать только действительно полезные колонки.

Хороший список обычно отвечает на вопрос:

> могу ли я понять, что это за документ и что с ним происходит, не открывая его?

---

## 72. In List Filter / In Standard Filter

Metadata:

```text
in_standard_filter
```

В текущем UI label:

```text
In List Filter
```

Делает поле удобным стандартным фильтром списка.

Это важная UX-настройка, а не техническая мелочь.

---

## 73. In Filter

Отдельное свойство:

```text
in_filter
```

Оно также относится к использованию поля в filtering-интерфейсах.

Не надо автоматически включать все search/list flags сразу: они имеют разные назначения.

---

## 74. Index

Metadata:

```text
search_index
```

UI:

```text
Index
```

Добавляет индекс для поля, когда это применимо.

Индекс может ускорять запросы, но:

```text
больше индексов
≠ всегда лучше
```

Они занимают место и влияют на запись/обновление данных.

---

## 75. In Global Search

Добавляет поле в глобальный search context Framework для поддерживаемых типов.

Включать для полей, по которым действительно ожидается глобальный поиск.

---

## 76. In Preview

Определяет участие значения в preview представлении документа.

Это UX-настройка.

---

## 77. Sticky

В текущем DocField есть свойство:

```text
Sticky
```

Оно влияет на закреплённое отображение поддерживаемых элементов интерфейса.

---

# Часть VII. Quick Entry

## 78. Allow in Quick Entry

Поле может участвовать в Quick Entry форме.

Если DocType допускает Quick Entry, не обязательно показывать там все его поля.

Выбирать минимальный набор для быстрого создания документа.

---

# Часть VIII. Permissions поля

## 79. Perm Level

У каждого поля может быть:

```text
Perm Level
```

По умолчанию:

```text
0
```

Например:

```text
Public Notes       permlevel 0
Manager Decision   permlevel 1
Salary             permlevel 2
```

Дальше Role Permission Manager может давать ролям доступ к соответствующим уровням.

Это штатная field-level permission model.

---

## 80. Не путать Perm Level с Hidden

```text
Hidden
```

— UI-свойство.

```text
Perm Level
```

— часть permission model.

Если значение действительно нельзя показывать роли, его нужно защищать permissions, а не просто скрывать CSS/UI.

---

# Часть IX. Import, Report и Print

## 81. Include in Import Template

Metadata:

```text
in_import_template
```

Позволяет включать поле в шаблон Data Import.

Полезно для полей, которые пользователь действительно должен загружать массово.

---

## 82. Report Hide

Скрывает поле из обычного report context.

Используется для технических или нерелевантных в отчётах полей.

---

## 83. Print Hide

Поле не выводится в стандартной печати.

Например:

```text
technical_external_id
internal_flag
```

---

## 84. Print Hide If No Value

Для поддерживаемых числовых типов поле можно не показывать в печати, когда значение отсутствует/нулевое согласно поведению Framework.

---

## 85. Print Width и Width

Позволяют управлять размером представления поля в соответствующих UI/print contexts.

Не строить сложный pixel-perfect интерфейс только через Width: это вспомогательная metadata, а не полноценная layout-система CSS.

---

## 86. Columns

Определяет ширину поля в grid/list context в колонках.

В текущем DocField описание напоминает, что суммарное количество колонок должно оставаться в пределах grid layout.

Особенно полезно для Child Table grid.

---

# Часть X. Presentation metadata

## 87. Bold

Выделяет значение визуально.

Не следует использовать Bold как замену приоритету или настоящему статусному UI во всей системе.

---

## 88. Alignment

Для ряда типов доступны:

```text
Left
Center
Right
```

Полезно прежде всего для числовых и табличных представлений.

---

## 89. Description

Пояснение к полю.

Очень полезно для сложных или неоднозначных настроек.

Хорошее Description отвечает:

> что сюда вводить и зачем?

а не повторяет Label другими словами.

---

## 90. Placeholder

Подсказка внутри пустого input.

Не использовать Placeholder вместо постоянного Label: после ввода значения placeholder исчезает.

---

## 91. Documentation URL

У поля может быть ссылка на документацию.

Это полезно для сложных административных настроек.

---

## 92. Show Description on Click

Позволяет показывать Description по запросу пользователя, а не постоянно занимать место на форме.

---

## 93. Translatable

Для поддерживаемых текстовых типов поле можно пометить как переводимое.

Это имеет смысл для metadata/content, который должен участвовать в translation workflow.

Не включать без необходимости для обычных пользовательских данных.

---

# Часть XI. Security-sensitive свойства

## 94. Ignore XSS Filter

В DocField есть:

```text
Ignore XSS Filter
```

Framework прямо предупреждает, что это позволяет сохранять HTML-подобный контент без обычного encoding/filtering поведения.

### Правило

Не включать ради удобства.

Это security-sensitive настройка и должна иметь конкретную причину.

---

## 95. Make Attachment Public

Тоже security-sensitive.

Если attachment должен оставаться private, не включать public-by-default.

---

## 96. Ignore User Permissions

Ещё одна security-sensitive настройка.

Используется только когда модель доступа действительно требует игнорировать User Permissions для конкретной связи.

---

# Часть XII. Virtual field

## 97. Virtual

В текущем DocField присутствует:

```text
Virtual
```

Virtual field может существовать как metadata/вычисляемое представление без обычной физической колонки хранения.

Это developer-oriented механизм и требует понимания того, откуда Framework будет получать значение.

Не путать:

```text
Virtual Field
```

и

```text
Virtual DocType
```

Это разные уровни.

---

# Часть XIII. Что хранится в БД, а что является только UI

## 98. Не все DocFields создают обычную колонку

Например layout/UI элементы:

```text
Section Break
Column Break
Tab Break
Heading
Button
HTML
```

не являются обычными предметными колонками.

А:

```text
Data
Date
Int
Link
Select
Check
```

обычно представляют хранимые значения.

Child Table тоже хранится не как одна колонка JSON в parent: это отдельные child documents.

---

# Часть XIV. Практическая модель выбора типа поля

## 99. Если данные — строка

```text
короткая
→ Data

многострочная
→ Small Text / Text / Long Text

форматированная
→ Text Editor / Markdown Editor / HTML Editor
```

---

## 100. Если данные — число

```text
целое
→ Int

дробное
→ Float

деньги
→ Currency

процент
→ Percent
```

---

## 101. Если данные — дата или время

```text
дата
→ Date

дата + время
→ Datetime

время суток
→ Time

длительность
→ Duration
```

---

## 102. Если данные — выбор

```text
маленький фиксированный набор
→ Select

самостоятельная сущность
→ Link

ссылка на разные типы сущностей
→ Dynamic Link

много связанных значений
→ Table MultiSelect / Child Table — по модели
```

---

## 103. Если это повторяющиеся строки внутри документа

```text
→ Child DocType + Table
```

а не десять полей:

```text
item_1
item_2
item_3
...
```

---

## 104. Если это только layout

```text
Section Break
Column Break
Tab Break
Heading
```

не создаём фиктивное Data-поле ради визуального разделения.

---

# Часть XV. Типичные ошибки

## 105. Всё хранить как Data

Плохо:

```text
status = Data
priority = Data
department = Data
start_date = Data
```

Теряются:

```text
валидация
ссылочная модель
нормальный фильтр
date UI
lookup
permission-aware link behavior
```

---

## 106. Select вместо справочника

Если список Department управляется пользователями и у Department есть свои свойства:

```text
Manager
Active
Code
```

то это уже отдельный DocType.

Не надо помещать все подразделения в Select.

---

## 107. Link вместо текста, который не является сущностью

Обратная ошибка тоже бывает.

Не нужно создавать DocType для каждого простого стабильного значения.

Иногда Select действительно проще и правильнее.

---

## 108. Client Script вместо Depends On

Плохо начинать с:

```javascript
frm.toggle_display(...)
```

если задача решается:

```text
Display Depends On
Mandatory Depends On
Read Only Depends On
```

Сначала metadata.

---

## 109. JavaScript-валидация вместо Mandatory/Unique/constraints

Если Framework уже предоставляет нужное ограничение, оно должно быть описано на уровне модели.

Client Script оставляем для UX и действительно нестандартного поведения.

---

## 110. Hidden вместо permissions

Самая опасная ошибка:

```text
поле скрыто
→ значит защищено
```

Нет.

Для ограничения доступа нужны permission levels и server-side permission model.

---

## 111. JSON вместо нормальной модели

Плохой shortcut:

```text
settings_json = {всё приложение}
```

JSON оправдан для действительно динамической структуры, но не заменяет DocTypes, Links и Child Tables.

---

# Часть XVI. Минимальная последовательность проектирования поля

## 112. Семь вопросов

Перед созданием поля ответить:

```text
1. Какой факт оно хранит?
2. Каков реальный тип этого значения?
3. Это собственное значение или связь с другой сущностью?
4. Нужно ли оно всегда или только при условии?
5. Кто может его читать и изменять?
6. Нужно ли поле в списках, фильтрах, поиске, импорте и печати?
7. Frappe уже умеет нужное поведение metadata-настройкой?
```

Только после этого имеет смысл писать Client Script или Python.

---

# Часть XVII. Итоговая карта DocField

```text
DocField
│
├── DATA TYPE
│   ├── Data / Text
│   ├── Numbers
│   ├── Date / Time
│   ├── Link
│   ├── Table
│   └── Files / special types
│
├── VALIDATION
│   ├── Mandatory
│   ├── Unique
│   ├── Non Negative
│   ├── Min / Max
│   ├── Not Nullable
│   └── Set Only Once
│
├── DEFAULT / FETCH
│   ├── Default
│   ├── Fetch From
│   └── Fetch if Empty
│
├── CONDITIONAL UI
│   ├── Display Depends On
│   ├── Mandatory Depends On
│   └── Read Only Depends On
│
├── SECURITY
│   ├── Perm Level
│   ├── Ignore User Permissions
│   ├── Mask
│   └── attachment privacy
│
├── LIST / SEARCH
│   ├── In List View
│   ├── In List Filter
│   ├── In Global Search
│   ├── Index
│   └── In Preview
│
├── IMPORT / REPORT / PRINT
│   ├── Import Template
│   ├── Report Hide
│   ├── Print Hide
│   └── Width
│
└── LAYOUT
    ├── Section Break
    ├── Column Break
    ├── Tab Break
    ├── Heading
    ├── HTML
    └── Button
```

Именно поэтому `DocField` — не просто определение SQL-колонки, а важная часть поведения приложения.

---

## 113. Контрольные вопросы

После главы нужно уметь ответить:

1. Чем Label отличается от Fieldname?
2. Почему Department обычно лучше хранить Link, а не Data?
3. Когда Select лучше отдельного DocType?
4. Чем Date отличается от Datetime и Duration?
5. Когда использовать Table?
6. Что делает Fetch From?
7. Чем Mandatory Depends On отличается от Display Depends On?
8. Почему Hidden не является permission-механизмом?
9. Для чего нужен Perm Level?
10. Что делает Allow on Submit?
11. Когда нужен No Copy?
12. Для чего используется In List View?
13. Чем Index отличается от In Global Search?
14. Почему Ignore User Permissions требует осторожности?
15. Почему JSON нельзя использовать как универсальную замену модели данных?

Если эти ответы понятны — можно переходить к отдельной теме naming и системного поля `name`.

## Официальные источники

- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [DocField source metadata](https://github.com/frappe/frappe/blob/develop/frappe/core/doctype/docfield/docfield.json)
- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Customize Form](https://docs.frappe.io/framework/user/en/basics/doctypes/customize)

---

Следующая глава: **Naming и системное поле `name`**.