# 33. Print Format и PDF

В прошлых главах мы разобрали сам Document, его Timeline, вложения и письма.

Теперь разберём ещё один встроенный слой Frappe — **представление документа для печати**.

Главная мысль здесь простая:

> **Print Format не меняет сам Document. Он описывает, как данные Document должны выглядеть на печати.**

Проверено: **2026-08-31**.

---

## 1. Самый простой пример

Есть документ:

```text
Request REQ-0001

Subject: Replace printer
Department: Support
Priority: High
```

В форме Desk он может выглядеть как обычный набор полей.

Но на бумаге хочется получить:

```text
REQUEST REQ-0001

Subject: Replace printer
Department: Support
Priority: High

____________________
Signature
```

Данные те же.

Меняется только представление:

```text
Document
   ↓
Print Format
   ↓
HTML для печати
   ↓
браузерная печать или PDF
```

Поэтому Print Format — это не второй Document и не копия данных.

---

## 2. Что пользователь видит в интерфейсе

У обычного документа в Form View есть действие печати.

Оно открывает **Print View**.

В Print View пользователь обычно может:

- выбрать Print Format;
- выбрать Letter Head;
- посмотреть предварительный результат;
- распечатать его;
- скачать PDF.

То есть Print View — это место использования формата, а `Print Format` — описание самого макета.

---

## 3. У каждого DocType уже есть Standard

Создавать Print Format с нуля нужно далеко не всегда.

Frappe умеет автоматически построить стандартное печатное представление DocType.

Оно называется:

```text
Standard
```

Упрощённо:

```text
DocType layout
      ↓
Standard Print Format
      ↓
готовая печатная форма
```

Например, если `Request` имеет поля:

```text
subject
department
priority
description
```

стандартный формат может вывести их без написания собственного HTML.

Поэтому первое правило очень простое:

> **сначала посмотри Standard. Возможно, отдельный Print Format вообще не нужен.**

---

## 4. Print Format — отдельный DocType

Если Standard уже недостаточно, можно создать отдельный Document типа:

```text
Print Format
```

В актуальном v16 у него есть, среди прочего:

```text
DocType
Standard
Custom Format
Print Format Type
HTML
Custom CSS
Margin Top
Margin Bottom
Margin Left
Margin Right
Page Number
PDF Generator
```

То есть один бизнес-DocType может иметь несколько вариантов печати.

Например:

```text
Request
├── Standard
├── Internal Request
└── External Request
```

Один и тот же `REQ-0001` можно представить по-разному без дублирования данных.

---

## 5. Три уровня сложности

Для начала удобно держать в голове три уровня.

### Уровень 1 — Standard

Ничего специально не строим.

```text
DocType
→ Standard
```

Подходит, если нужна просто читаемая распечатка полей.

### Уровень 2 — Print Format Builder

Создаём собственный Print Format и собираем его визуально.

```text
DocType
→ Print Format Builder
→ свой layout
```

Подходит для большинства обычных форм.

### Уровень 3 — Custom HTML + Jinja

Полностью задаём структуру сами.

```text
DocType
→ HTML + Jinja + CSS
→ точный layout
```

Подходит, когда нужен нестандартный документ: акт, заявление, сложная таблица, точное расположение реквизитов и т. п.

Правильная последовательность:

```text
Standard
   ↓ не хватает
Print Format Builder
   ↓ не хватает
Custom HTML + Jinja
```

Не стоит начинать с большого HTML-шаблона, если Builder уже решает задачу.

---

## 6. Print Format Builder

Официальная документация рекомендует для обычной настройки создать копию стандартного формата и редактировать её через **Print Format Builder**.

Builder позволяет визуально собрать печатную форму из полей DocType.

Упрощённый пример:

```text
[ Request ]

[ Subject        ]
[ Department     ]

[ Description    ]

[ Items table    ]
```

Для обычного пользователя это существенно проще, чем писать:

```html
<div>...</div>
<table>...</table>
```

вручную.

---

## 7. Custom HTML внутри Builder

Builder не ограничивается только полями.

В Print Format можно добавлять **Custom HTML**.

Например:

```html
<h3>Additional information</h3>
<p>This document was generated automatically.</p>
```

Причём внутри Custom HTML можно использовать Jinja.

Например:

```html
{% if doc.priority == "High" %}
  <strong>HIGH PRIORITY</strong>
{% endif %}
```

Это уже позволяет делать небольшие динамические блоки, не переписывая всю форму с нуля.

---

## 8. Custom CSS

За внешний вид отвечает CSS.

Например:

```css
.request-title {
    font-size: 18px;
    font-weight: bold;
    text-align: center;
}
```

А в HTML:

```html
<div class="request-title">
    Request {{ doc.name }}
</div>
```

Таким способом можно менять:

- размеры текста;
- отступы;
- границы;
- выравнивание;
- ширину таблиц;
- отображение отдельных блоков.

Но важно разделять две вещи:

```text
Jinja
→ какие данные и блоки выводить

CSS
→ как они выглядят
```

---

## 9. Когда нужен полностью Custom Format

Если Builder начинает мешать, можно создать Print Format с:

```text
Custom Format = ✓
Print Format Type = Jinja
```

и написать HTML самостоятельно.

Например:

```html
<h2>Request {{ doc.name }}</h2>

<p>
  <strong>Subject:</strong>
  {{ doc.subject }}
</p>

<p>
  <strong>Department:</strong>
  {{ doc.department }}
</p>
```

В актуальном v16 такой HTML валидируется как Jinja template при сохранении Print Format.

---

## 10. Что такое Jinja

Jinja — шаблонный язык.

Его задача — вставлять данные в текст или HTML.

Самая простая конструкция:

```jinja
{{ doc.subject }}
```

означает:

> выведи значение поля `subject` текущего документа.

Если:

```text
subject = Replace printer
```

результатом станет:

```text
Replace printer
```

---

## 11. `doc` — текущий Document

В Print Format главная переменная:

```text
doc
```

Это текущий печатаемый Document.

Например:

```jinja
{{ doc.name }}
{{ doc.subject }}
{{ doc.department }}
{{ doc.priority }}
```

Для `REQ-0001` это может дать:

```text
REQ-0001
Replace printer
Support
High
```

То есть никакого отдельного API для чтения собственных полей документа здесь не нужно.

---

## 12. Условия

Jinja умеет включать блок только при определённом условии.

Например:

```jinja
{% if doc.priority == "High" %}
  <p><strong>High priority request</strong></p>
{% endif %}
```

Если `priority = High`, блок появится.

Если нет — не появится.

Это удобно для небольших различий печати.

Но не надо превращать Print Format в бизнес-движок.

Правильная граница:

```text
решить, как показать уже существующие данные
→ Print Format

вычислить бизнес-решение или изменить Document
→ серверная логика
```

---

## 13. Child Table в Jinja

Есть:

```text
Order
└── items → Order Item
```

В печати нужно вывести все строки.

Это делается обычным циклом:

```jinja
<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Item</th>
      <th>Qty</th>
    </tr>
  </thead>
  <tbody>
    {% for row in doc.items %}
      <tr>
        <td>{{ row.idx }}</td>
        <td>{{ row.item }}</td>
        <td>{{ row.qty }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
```

Если у документа три строки, цикл выполнится три раза.

Модель:

```text
doc
└── items
    ├── row 1
    ├── row 2
    └── row 3
```

Именно поэтому Child Table хорошо ложится на печатные таблицы.

---

## 14. Не форматируй Date и Currency вручную без причины

В базе дата, число или Currency могут храниться в техническом виде.

Но в печати обычно нужен человекочитаемый формат.

У Document есть:

```jinja
{{ doc.get_formatted("request_date") }}
```

Для строки Child Table можно использовать:

```jinja
{{ row.get_formatted("amount", doc) }}
```

Это лучше, чем самостоятельно собирать формат даты или валюты строковыми операциями.

В Jinja API также доступны разрешённые helpers Framework, например:

```jinja
{{ frappe.format_date(doc.request_date) }}
```

Главный принцип:

> если Framework уже знает тип поля, сначала используй его штатное форматирование.

---

## 15. Можно ли читать другие Documents

Да.

Jinja API разрешает, например:

```jinja
{% set department = frappe.get_doc("Department", doc.department) %}

{{ department.description }}
```

Но использовать это нужно аккуратно.

Если ради одной распечатки шаблон начинает делать много дополнительных запросов:

```text
row 1 → get_doc()
row 2 → get_doc()
row 3 → get_doc()
...
row 200 → get_doc()
```

печать становится тяжёлой и архитектура расползается.

Практическое правило:

```text
простое получение одного связанного значения
→ допустимо

сложные расчёты и десятки запросов
→ лучше подготовить данные раньше
```

Print Format должен в первую очередь **представлять данные**, а не заменять controller и серверную модель.

---

## 16. `Print Hide`

Не каждое поле формы должно попадать на бумагу.

У `DocField` есть свойство:

```text
Print Hide
```

Например:

```text
internal_note
Print Hide = ✓
```

Тогда стандартная печать не должна выводить это поле.

Это штатный способ сказать:

> поле нужно в интерфейсе, но в обычной печатной форме его показывать не надо.

В v16 у числовых полей также есть:

```text
Print Hide If No Value
```

а для управления шириной присутствует:

```text
Print Width
```

То есть часть печати настраивается прямо на уровне DocField и не требует отдельного шаблона.

---

## 17. `Hidden` и `Print Hide` — разные свойства

Не путай:

```text
Hidden
→ поведение поля в интерфейсе

Print Hide
→ поведение поля в стандартной печати
```

Поле может быть полезно в Form View, но не нужно в PDF.

И наоборот, собственный Jinja Print Format вообще может явно вывести нужное значение независимо от того, как был собран стандартный layout.

Поэтому печатное представление лучше проектировать отдельно от формы, когда требования действительно различаются.

---

## 18. Letter Head

Шапку организации не нужно копировать в каждый Print Format.

Для этого есть отдельный DocType:

```text
Letter Head
```

В актуальном v16 шапка может строиться на основе:

```text
Image
или
HTML
```

Footer также может быть:

```text
Image
или
HTML
```

Например:

```text
Letter Head: Main

Header
├── logo
├── organization name
└── contacts

Footer
└── address / website / registration data
```

А Print Format отвечает уже за тело документа.

Так получается правильное разделение:

```text
Letter Head
→ общая фирменная шапка и footer

Print Format
→ структура конкретного типа документа
```

---

## 19. Как Frappe выбирает Letter Head

Упрощённый порядок текущего v16:

```text
явно выбранный Letter Head
        ↓ если нет
поле letter_head текущего Document
        ↓ если нет
Default Letter Head
```

Если печать вызвана с `no_letterhead`, шапка вообще не добавляется.

Это позволяет иметь, например:

```text
Main Letter Head
Branch A Letter Head
Branch B Letter Head
```

без копирования самих Print Format.

---

## 20. Print Settings

Помимо конкретных Print Format есть глобальная настройка:

```text
Print Settings
```

Это **Single DocType**.

В текущем v16 среди его настроек есть:

```text
Send Print as PDF
Repeat Header and Footer
PDF Generator
PDF Page Size
Print with letterhead
Allow Print for Draft
Always add "Draft" Heading
Allow Page Break Inside Tables
Allow Print for Cancelled
Print Style
Font
Font Size
```

Поэтому часть поведения задаётся не в каждом формате отдельно, а глобально для Site.

---

## 21. Draft и Cancelled

Для Submittable DocType печать зависит не только от Print Format.

В `Print Settings` есть:

```text
Allow Print for Draft
Allow Print for Cancelled
```

В текущем v16 при классическом print rendering Framework проверяет их перед построением шаблона.

Например:

```text
Request is Submittable
DocStatus = Draft
Allow Print for Draft = 0
```

→ печать Draft будет запрещена.

Также можно включить автоматическое обозначение:

```text
Draft
```

для печатаемых черновиков.

Это уже политика печати всего Site, а не логика конкретного Jinja-шаблона.

---

## 22. HTML сначала, PDF потом

Одна из самых важных вещей всей главы:

> **Print Format по своей сути формирует HTML-представление. PDF — следующий этап.**

Упрощённо:

```text
Document
   ↓
Print Format + Jinja
   ↓
HTML + CSS
   ↓
PDF generator
   ↓
PDF bytes
```

Поэтому ситуация:

```text
в браузерном Print View всё выглядит хорошо,
а PDF ломает таблицу
```

не обязательно означает ошибку Jinja.

Проблема может быть именно на этапе HTML → PDF.

---

## 23. PDF Generator в v16

В старых установках Frappe обычно ассоциировали с:

```text
wkhtmltopdf
```

В актуальном v16 в metadata Framework уже есть два варианта:

```text
wkhtmltopdf
chrome
```

Такое поле есть и в `Print Format`, и в `Print Settings`.

В серверном коде `get_print(..., as_pdf=True)` также принимает:

```python
pdf_generator="wkhtmltopdf"
```

или:

```python
pdf_generator="chrome"
```

При этом выбор `chrome` использует отдельный PDF-generator hook/path, а классический fallback остаётся через wkhtmltopdf.

Для новичка отсюда нужно вынести только одно:

> **PDF generator — отдельная часть печатного конвейера, а не сам Print Format.**

---

## 24. Размер страницы

Глобальный `Print Settings` в v16 содержит:

```text
PDF Page Size
```

Например:

```text
A4
A5
Letter
Legal
...
Custom
```

Для `Custom` доступны:

```text
PDF Page Height (mm)
PDF Page Width (mm)
```

Это значит, что для обычной задачи вроде:

> весь Site печатает документы на A4

не нужно вписывать размер страницы вручную во все Jinja-шаблоны.

---

## 25. Поля Print Format самого v16

У конкретного Print Format сейчас есть собственные параметры:

```text
Margin Top
Margin Bottom
Margin Left
Margin Right
Page Number
PDF Generator
```

`Page Number` поддерживает варианты:

```text
Hide
Top Left
Top Center
Top Right
Bottom Left
Bottom Center
Bottom Right
```

То есть многие требования к странице уже являются данными настройки, а не поводом писать сложный CSS.

---

## 26. Page Break и длинные таблицы

Проблемы с PDF часто начинаются на длинных Child Table.

Например:

```text
Order
└── 150 строк items
```

Таблица должна продолжиться на следующей странице.

В `Print Settings` есть:

```text
Allow Page Break Inside Tables
```

Кроме того, header/footer могут повторяться в PDF в зависимости от соответствующей настройки и rendering path.

Поэтому прежде чем бороться с многостраничной таблицей десятками CSS-хаков, проверь штатные Print Settings.

---

## 27. Print Format Builder Beta

В актуальном `Print Format` v16 присутствует отдельный флаг:

```text
Print Format Builder Beta
```

Он не является просто другим названием старого Builder.

Текущий исходный код отправляет такой формат по отдельному rendering path через `frappe.utils.weasyprint`.

Для курса важно не смешивать две реализации в одну картину.

Пока разумно считать:

```text
классический Standard / Builder / Jinja
→ основная модель, которую нужно понять

Builder Beta
→ отдельная развивающаяся реализация v16
```

Когда работаешь с конкретным Site, проверяй выбранный тип Builder и не переноси автоматически ограничения одного renderer на другой.

---

## 28. Raw Printing — это не PDF

В `Print Format` v16 есть:

```text
Raw Printing
Raw Commands
```

А в `Print Settings`:

```text
Enable Raw Printing
```

Raw Printing нужен для принтеров, которые принимают собственный язык команд.

Упрощённо:

```text
Document
   ↓
Jinja
   ↓
команды языка принтера
   ↓
printer
```

Это отдельный режим.

Не надо путать его с:

```text
HTML
→ PDF
```

Для обычных офисных актов, заявок и документов Raw Printing обычно вообще не требуется.

---

## 29. Standard и Custom в репозитории

Здесь снова появляется знакомое разделение:

```text
локальная настройка Site
против
части собственного App
```

У `Print Format` есть поле:

```text
Standard = No / Yes
```

Текущий controller v16 запрещает обычное изменение `Standard = Yes`, если не включён Developer Mode.

А при сохранении Standard Print Format он экспортируется в module JSON приложения.

Поэтому смысл примерно такой:

```text
Standard = No
→ локальный настраиваемый Print Format Site

Standard = Yes
→ стандартная часть App, которая должна жить в кодовой базе
```

Это тот же архитектурный принцип, который позже будет подробно разобран в главах про Standard vs Custom и Developer Mode.

---

## 30. Default Print Format

Если у `Request` есть несколько форматов:

```text
Internal Request
External Request
```

один можно сделать default.

В текущем v16 Framework записывает это как `default_print_format` DocType.

Для Custom DocType значение может быть сохранено непосредственно в DocType.

Для стандартного DocType Framework использует `Property Setter`, чтобы не переписывать исходный DocType приложения.

Это хороший пример общей модели Frappe:

```text
стандартная metadata приложения
        +
локальная customization Site
```

---

## 31. Print permission

В Role Permission Manager уже встречалось право:

```text
Print
```

Официальная модель Framework описывает его как право распечатывать Document и генерировать PDF.

Поэтому Print Format не является обходом security.

То, что мы умеем написать:

```jinja
{{ doc.internal_cost }}
```

не означает, что надо проектировать печать как способ показать пользователю данные, к которым он не должен иметь доступа.

Security сначала должна быть корректно построена на уровне данных и permissions.

А Print Format должен заниматься представлением уже разрешённого сценария.

---

## 32. Print Format не является местом бизнес-логики

Плохой шаблон:

```text
получить 12 связанных Documents
↓
пересчитать сложную скидку
↓
решить, можно ли утверждать Request
↓
изменить состояние
↓
вывести результат
```

Здесь смешано всё.

Лучше:

```text
server-side business logic
        ↓
готовые данные Document
        ↓
Print Format
        ↓
представление
```

Jinja хорошо подходит для:

```text
if
for
простого форматирования
небольшого выбора блоков
```

Но не должен становиться скрытым controller.

---

## 33. Print Format не хранит отдельную версию бизнес-данных

Допустим, сегодня распечатали:

```text
REQ-0001
Priority = High
```

А завтра пользователь поменял:

```text
Priority = Medium
```

Если снова открыть Print View, формат будет строиться уже из текущего Document.

Сам факт того, что вчера существовал PDF с `High`, не превращает Print Format в архив этого состояния.

Если бизнесу нужно юридически или операционно хранить **зафиксированный экземпляр сформированного документа**, это уже отдельное требование к модели:

```text
сохранённый File/PDF
отдельный immutable record
версия документа
или другая архивная модель
```

Print Format сам по себе — шаблон, а не архив снимков.

---

## 34. Не путай четыре сущности

После этой главы полезно окончательно разделить:

```text
Document
→ сами бизнес-данные

Print Format
→ как представить эти данные

Letter Head
→ общая шапка / footer

PDF
→ конкретный результат рендеринга
```

Например:

```text
Request REQ-0001
        ↓
External Request Print Format
        +
Main Letter Head
        ↓
request-REQ-0001.pdf
```

Это четыре разных уровня.

---

## 35. Когда достаточно Standard

Требование:

> нужно просто распечатать Request со всеми основными полями.

Начинай с:

```text
Standard
```

Не создавай отдельный шаблон только ради самого факта печати.

---

## 36. Когда нужен Builder

Требование:

> поля нужны те же, но расположение и структура должны быть аккуратнее.

Например:

```text
заголовок
↓
две колонки реквизитов
↓
описание
↓
таблица
```

Это хороший кандидат для:

```text
Print Format Builder
```

---

## 37. Когда нужен Jinja

Требование:

> если тип Request = External, нужен один блок; если Internal — другой; Child Table надо вывести в нестандартной таблице; внизу должны быть отдельные подписи.

Это уже нормальный кандидат для:

```text
Custom HTML + Jinja
```

---

## 38. Когда одного Print Format уже мало

Требование:

> нужно собрать PDF из нескольких разных Documents, выполнить сложные расчёты, подписать файл, сохранить неизменяемую копию и отправить во внешнюю систему.

Это уже не просто задача макета.

Архитектура может выглядеть так:

```text
App code
   ↓
подготовить данные
   ↓
отрендерить Print Format
   ↓
создать PDF
   ↓
сохранить File
   ↓
выполнить дальнейшую бизнес-операцию
```

Print Format остаётся частью решения, но уже не является всем решением.

---

## 39. Мини-практика

Создай простой DocType:

```text
Request
```

Поля:

```text
subject       Data
request_date  Date
department    Link → Department
priority      Select
internal_note Small Text
items         Table → Request Item
```

В `Request Item`:

```text
item_name  Data
qty        Float
```

### Шаг 1

Создай несколько `Request` и посмотри их через:

```text
Print → Standard
```

Не создавай свой формат заранее.

### Шаг 2

Для `internal_note` включи:

```text
Print Hide = ✓
```

Снова посмотри Standard.

### Шаг 3

Создай собственный Print Format через Builder.

Выведи:

```text
name
subject
request_date
department
priority
items
```

### Шаг 4

Добавь Custom HTML:

```jinja
{% if doc.priority == "High" %}
  <p><strong>HIGH PRIORITY</strong></p>
{% endif %}
```

Проверь Request с разными Priority.

### Шаг 5

Создай отдельный Custom Format на Jinja и вручную выведи Child Table через цикл:

```jinja
{% for row in doc.items %}
  {{ row.idx }}. {{ row.item_name }} — {{ row.qty }}
{% endfor %}
```

### Шаг 6

Создай Letter Head и сравни:

```text
Print with letterhead
Print without letterhead
```

### Шаг 7

Открой `Print Settings` и найди:

```text
PDF Page Size
Allow Print for Draft
Allow Print for Cancelled
PDF Generator
```

Пока ничего сложного не настраивай. Задача — понять, какой уровень за что отвечает.

---

## 40. Что запомнить

1. `Print Format` описывает **представление Document**, а не его данные.
2. У DocType уже есть автоматически формируемый `Standard`.
3. Сначала пробуй `Standard`, затем Builder, затем Custom HTML + Jinja.
4. В Jinja текущий документ доступен как `doc`.
5. Child Table можно перебирать обычным `{% for %}`.
6. Для дат, валют и других typed values лучше использовать штатное форматирование.
7. `Print Hide` — отдельное свойство DocField для печати.
8. `Letter Head` хранит общую шапку/footer отдельно от Print Format.
9. `Print Settings` задаёт глобальные правила Site: page size, Draft/Cancelled, letterhead, fonts и другие параметры.
10. HTML-rendering и PDF-generation — два разных этапа.
11. В текущем v16 среди PDF generators есть `wkhtmltopdf` и `chrome`.
12. `Print Format Builder Beta` существует как отдельный rendering path и не должен автоматически смешиваться с классическим Builder.
13. `Standard = Yes` относится к стандартной части App и требует Developer Mode для обычного редактирования.
14. Print Format не является архивом уже сформированных PDF и не должен становиться скрытым бизнес-controller.

---

## Источники

Официальная документация:

- [Printing](https://docs.frappe.io/framework/user/en/desk/printing)
- [Jinja API](https://docs.frappe.io/framework/user/en/api/jinja)
- [Getting Information From Another Document In Print Format](https://docs.frappe.io/framework/user/en/guides/reports-and-printing/getting-information-from-another-document-in-print-format)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)

Исходный код Frappe Framework `version-16`:

- [`Print Format` metadata](https://github.com/frappe/frappe/blob/version-16/frappe/printing/doctype/print_format/print_format.json)
- [`Print Format` controller](https://github.com/frappe/frappe/blob/version-16/frappe/printing/doctype/print_format/print_format.py)
- [`printview.py`](https://github.com/frappe/frappe/blob/version-16/frappe/www/printview.py)
- [`Print Settings` metadata](https://github.com/frappe/frappe/blob/version-16/frappe/printing/doctype/print_settings/print_settings.json)
- [`Letter Head` metadata](https://github.com/frappe/frappe/blob/version-16/frappe/printing/doctype/letter_head/letter_head.json)
- [`print_utils.py`](https://github.com/frappe/frappe/blob/version-16/frappe/utils/print_utils.py)
- [`pdf.py`](https://github.com/frappe/frappe/blob/version-16/frappe/utils/pdf.py)
- [`DocField` metadata](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/docfield/docfield.json)

---

Дальше: **34. Report Builder**.
