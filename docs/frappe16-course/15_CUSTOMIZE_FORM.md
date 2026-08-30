# 15. Customize Form

До этого мы создавали свои DocType и настраивали их поля.

Но в реальной системе часто возникает другая задача:

> DocType уже существует, он пришёл из установленного App, а нам нужно немного изменить его под свой Site.

Например, есть стандартный DocType `Request`, а на конкретном Site хочется:

- добавить поле `Department`;
- скрыть ненужное поле;
- поменять подпись поля;
- вынести `Priority` выше;
- добавить поле в List View;
- изменить стандартную сортировку.

Для этого во Frappe есть **Customize Form**.

Проверено: **2026-08-30**.

---

## 1. Самая важная мысль

`Customize Form` не переписывает исходный DocType установленного App.

Вместо этого Frappe создаёт поверх него отдельные настройки.

Упрощённо:

```text
стандартный DocType из App
        Request
          ↓
   Customize Form
          ↓
Custom Field + Property Setter
          ↓
итоговая metadata на этом Site
```

Поэтому App можно обновлять, не редактируя вручную его исходный JSON.

Это одна из ключевых идей Frappe.

---

## 2. Простой пример

Допустим, стандартная форма выглядит так:

```text
Request

Subject
Priority
Status
Description
```

На нашем Site нужно добавить подразделение.

В `Customize Form` добавляем:

```text
Department
Field Type: Link
Options: Department
```

После сохранения пользователь увидит:

```text
Request

Subject
Department
Priority
Status
Description
```

Исходный файл DocType внутри установленного App при этом не менялся.

Появился отдельный **Custom Field**.

---

# Часть 1. Где нужен Customize Form

## 3. Standard DocType и Custom DocType — не одно и то же

Это место легко запутать.

### Standard DocType

Это DocType, который поставляется приложением.

Например:

```text
some_app/
└── some_module/
    └── doctype/
        └── request/
            └── request.json
```

Если нужно сделать **локальное изменение именно для этого Site**, используется `Customize Form`.

### Custom DocType

Это DocType, созданный пользователем прямо на Site как `Custom`.

Его можно менять непосредственно через сам DocType/Form Builder.

Поэтому правило простое:

```text
свой Custom DocType
        ↓
меняем сам DocType

стандартный DocType из App
        ↓
Customize Form
```

В v16 сам `Customize Form` серверно не разрешает выбирать Custom DocType, Single DocType и системные core DocTypes.

---

## 4. Зачем вообще нужен такой слой

Представим два Site с одним и тем же App:

```text
App
└── Request

Site A
└── нужен Department

Site B
└── нужен Customer Code
```

Если оба Site начнут менять исходный `request.json`, приложение перестанет быть единым.

Customize Form позволяет оставить базовый App одинаковым:

```text
один App
   ↓
один стандартный DocType
   ↓
разные site-specific customizations
```

Именно для этого механизм и существует.

---

# Часть 2. Что находится под капотом

## 5. Custom Field

`Custom Field` — отдельный DocType Frappe, который описывает добавленное поле стандартного DocType.

Например, мы добавили:

```text
Label: Department
Fieldname: department
Field Type: Link
Options: Department
```

Frappe создаёт запись примерно такого смысла:

```text
Custom Field
├── DocType: Request
├── Fieldname: department
├── Field Type: Link
├── Options: Department
└── Insert After: subject
```

После этого поле входит в итоговую metadata `Request`.

Для обычного хранимого поля Frappe также обновляет схему таблицы DocType.

---

## 6. Property Setter

А теперь другой случай.

Поле `Priority` уже существует в стандартном DocType.

Мы не хотим создавать новое поле. Нужно только изменить его свойство:

```text
было:
Priority
Mandatory: No

стало:
Priority
Mandatory: Yes
```

Для этого Frappe создаёт **Property Setter**.

Упрощённо:

```text
стандартный DocField
Priority
Mandatory = 0

        +

Property Setter
Priority
Mandatory = 1

        ↓

итоговая metadata
Priority
Mandatory = 1
```

То есть Property Setter — это **переопределение свойства**, а не копия всего DocType.

---

## 7. Custom Field и Property Setter — главное различие

| Что делаем | Что создаётся |
|---|---|
| добавляем новое поле | `Custom Field` |
| меняем свойство стандартного поля | `Property Setter` |
| меняем свойство DocType | `Property Setter` |
| переставляем стандартные поля | Property Setter для layout/order |

Запоминать внутренние DocType необязательно.

Достаточно понимать модель:

```text
новое → Custom Field

изменение существующего → Property Setter
```

---

## 8. Почему не стоит редактировать Property Setter вручную

Технически `Property Setter` существует как обычный DocType.

Но даже его собственная форма предупреждает, что напрямую менять записи опасно и для нормальной работы следует использовать `Customize Form` и `Custom Field`.

То есть обычный путь такой:

```text
Customize Form
      ↓
Frappe сам создаёт нужные Property Setter
```

А не:

```text
ищем Property Setter
      ↓
вручную ковыряем metadata
```

---

# Часть 3. Что можно менять

## 9. Добавление поля

Самый частый сценарий.

Например:

```text
Request
└── Department
```

В Form Builder добавляем строку и задаём:

```text
Label      Department
Field Type Link
Options    Department
```

При необходимости можно настроить те же свойства, которые уже знакомы по главе про DocField:

```text
Mandatory
Read Only
Hidden
Default
Fetch From
In List View
In List Filter
Depends On
Permission Level
и т. д.
```

Для нового поля это будет `Custom Field`.

---

## 10. Перестановка полей

Допустим, было:

```text
Subject
Description
Priority
Status
```

А пользователю удобнее:

```text
Subject
Priority
Status
Description
```

В Form Builder поле можно переместить.

Frappe сохраняет изменённый порядок как customization.

Исходный порядок стандартного DocType остаётся в App.

---

## 11. Section Break, Column Break и Tab Break

Через Customize Form можно не только менять сами данные, но и переделывать layout формы.

Например:

```text
Request

[Основное]
Subject        Priority
Department    Status

[Описание]
Description
```

Для этого используются знакомые layout fields:

```text
Section Break
Column Break
Tab Break
```

Если layout стандартной формы неудобен, для его перестройки не нужен Client Script.

Сначала стоит проверить Customize Form.

---

## 12. Изменение подписи поля

Например, стандартное поле называется:

```text
Subject
```

А пользователям понятнее:

```text
Краткое описание
```

Изменяем Label через Customize Form.

Frappe создаст Property Setter для этого свойства.

Сам `fieldname` при этом остаётся прежним.

Это важно:

```text
Label может измениться
fieldname остаётся техническим идентификатором
```

---

## 13. Hidden

Если стандартное поле не нужно пользователю, его часто можно просто скрыть:

```text
Hidden = Yes
```

Это особенно важно потому, что **стандартное поле удалить через Customize Form нельзя**.

Если поле поставляется App, Frappe предлагает скрыть его, а не удалить из стандартной модели.

---

## 14. Mandatory

Для нового Custom Field можно включить:

```text
Mandatory = Yes
```

Для стандартного поля действуют ограничения.

Например, если App уже объявил поле обязательным, Customize Form не позволяет просто снять эту обязательность.

Почему это разумно?

Потому что код стандартного App может рассчитывать на существование этого значения.

---

## 15. Read Only

Та же логика применяется к стандартным полям.

Если поле в исходном DocType является `Read Only`, Customize Form не позволяет просто сделать его редактируемым.

Иначе UI мог бы позволить пользователю менять данные, которые приложение считает системными.

---

## 16. Allow on Submit

Для стандартного поля нельзя произвольно включить `Allow on Submit`, если исходный DocType этого не разрешал.

Это связано с lifecycle, который мы разбирали раньше:

```text
Draft
  ↓ Submit
Submitted
```

После Submit правила изменения документа являются частью контракта DocType.

Customize Form не должен тихо ломать этот контракт.

---

## 17. Изменение Field Type

Некоторые совместимые изменения Frappe разрешает.

Но нельзя считать, что любое поле можно безопасно превратить во что угодно:

```text
Data → Date → Link → Table
```

Так делать бездумно нельзя.

Frappe проверяет допустимость изменения типа и в некоторых случаях также данные, которые уже лежат в таблице.

Для новичка хорошее правило:

> Если изменение типа поля меняет смысл уже существующих данных, сначала остановись и подумай о миграции данных.

---

## 18. Изменение Options

`Options` тоже нельзя безусловно менять для любого стандартного поля.

Например, у разных Field Type `Options` имеет разный смысл:

```text
Link   → целевой DocType
Select → список вариантов
Table  → Child DocType
```

Поэтому Customize Form проверяет, допустимо ли такое изменение.

---

# Часть 4. Свойства самого DocType

## 19. Customize Form меняет не только поля

Через него можно переопределять и часть настроек самого DocType.

Например:

```text
Title Field
Search Fields
Default Sort Field
Default Sort Order
Quick Entry
Track Changes
Default View
Is Calendar and Gantt
Allow Import
Max Attachments
и другие поддерживаемые свойства
```

Механика та же:

```text
стандартное значение DocType
        +
Property Setter
        ↓
итоговое значение на Site
```

---

## 20. Пример с сортировкой

Допустим, `Request` по умолчанию открывается так:

```text
creation DESC
```

То есть новые документы сверху.

Если нужно сортировать по `priority`, можно изменить:

```text
Default Sort Field = priority
Default Sort Order = ASC
```

Это изменение metadata, а не отдельный List Script.

---

## 21. Default View

Если DocType поддерживает несколько представлений, можно настроить его Default View.

Например:

```text
List
Kanban
Calendar
Tree
```

Набор доступных вариантов зависит от возможностей самого DocType.

Например, Calendar/Gantt включаются только для DocType, где эта возможность настроена, а Tree требует иерархической модели.

---

# Часть 5. Child Table

## 22. Дочернюю таблицу тоже можно кастомизировать

Представим:

```text
Order
└── Items
    ├── Product
    └── Qty
```

`Items` — Child Table.

Нужно добавить:

```text
Comment
```

В Customize Form v16 для Table/Table MultiSelect есть переход **Customize Child Table**.

То есть можно перейти к целевому Child DocType и добавить поле уже туда.

Результат:

```text
Order
└── Items
    ├── Product
    ├── Qty
    └── Comment
```

Это всё ещё штатная customization, а не отдельный frontend.

---

# Часть 6. Actions и Links

## 23. Можно добавлять Links и Actions

Customize Form умеет добавлять пользовательские `Links` и `Actions` к стандартному DocType.

Это не то же самое, что Client Script.

Упрощённо:

```text
Customize Form
├── Fields
├── Links
└── Actions
```

Frappe хранит такие элементы как соответствующие metadata-записи с признаком custom.

Для новичка пока достаточно знать, что простую дополнительную навигацию не всегда нужно писать JavaScript-кнопкой.

---

# Часть 7. Права доступа

## 24. Customize Form — не Role Permission Manager

В интерфейсе есть кнопка `Set Permissions`, но она переводит в отдельный механизм управления правами.

Не стоит смешивать:

```text
Customize Form
→ форма и metadata

Role Permission Manager
→ доступ пользователей и ролей
```

Права подробно разбираются в отдельном блоке курса.

---

# Часть 8. Reset

## 25. Reset Layout

Представим, что мы долго таскали поля по форме и получили хаос.

`Reset Layout` возвращает стандартный порядок/layout.

То есть он предназначен именно для layout-настроек.

Он не означает:

```text
удалить вообще все Custom Fields
```

Это более узкая операция.

---

## 26. Reset All Customizations

Это уже гораздо более серьёзная команда.

Она удаляет обычные site-specific Custom Fields и Property Setters для выбранного DocType, за исключением защищённых/системно созданных настроек.

После неё итоговая metadata снова становится максимально близкой к стандартной.

Перед такой операцией нужно понимать, какие поля и настройки были добавлены именно на этом Site.

---

# Часть 9. Удаление Custom Field и база данных

## 27. Удалили поле из metadata — не значит сразу удалили колонку из БД

Это важная техническая деталь.

Допустим, мы когда-то добавили:

```text
department
```

Затем удалили Custom Field.

Frappe специально не обязан сразу физически удалять старую колонку из таблицы.

Причина очевидна: автоматический `DROP COLUMN` может уничтожить данные без возможности восстановления.

Поэтому может получиться:

```text
metadata:
department уже нет

database table:
старая колонка department ещё существует
```

Такая колонка называется orphaned column — осиротевшая колонка.

---

## 28. Trim Table

В Customize Form v16 есть действие `Trim Table`.

Оно ищет database columns, которых больше нет в DocType metadata, и позволяет физически удалить их.

Но интерфейс прямо предупреждает:

```text
DATA LOSS
операция необратима
```

Поэтому для новичка правило простое:

> Не используй Trim Table просто для «наведения порядка». Это операция над схемой БД с реальным удалением данных.

Сначала backup и понимание того, что именно удаляется.

---

# Часть 10. Export Customizations

## 29. Site-specific хорошо, пока Site один

Customize Form отлично подходит для локальной настройки.

Но представим, что мы разработали набор полезных изменений:

```text
Request
├── Department
├── Category
├── изменённый layout
└── несколько Property Setter
```

И теперь хотим получить точно такую же настройку на пяти Site.

Ручное повторение уже плохой вариант.

---

## 30. Export Customizations

В Developer Mode v16 в Customize Form появляется действие:

```text
Export Customizations
```

Оно позволяет сохранить customizations в собственный App.

Упрощённо:

```text
Site customization
      ↓ export
собственный App
      ↓ install / migrate
другой Site
```

Это переход от локальной настройки к воспроизводимой конфигурации в кодовой базе приложения.

---

## 31. Sync on Migrate

При экспорте можно включить:

```text
Sync on Migrate
```

Тогда customizations из App будут синхронизироваться при миграции Site.

Это удобно, когда App должен гарантированно приносить с собой эти изменения.

Но здесь появляется важная ответственность:

```text
то, что лежит в App
становится источником истины
```

Если потом вручную менять те же customizations на Site, при синхронизации они могут быть перезаписаны.

Особенно осторожно нужно обращаться с экспортом custom permissions: интерфейс v16 прямо предупреждает, что они могут принудительно синхронизироваться при migrate.

---

# Часть 11. Где заканчивается Customize Form

## 32. Не всякое поведение является customization metadata

Представим требования:

### Требование A

Добавить поле `Department`.

```text
→ Customize Form
```

### Требование B

Скрывать поле `Reason`, если `Status != Rejected`.

Во многих случаях это можно сделать через:

```text
Depends On
```

То есть всё ещё metadata.

### Требование C

При выборе Department динамически запрашивать сервер и сложным образом менять несколько полей.

```text
→ возможно Client Script
```

### Требование D

При сохранении проверять сложное правило, которое обязательно должно работать и через API.

```text
→ серверная логика
```

### Требование E

Изменение должно поставляться как часть собственного App и быть одинаковым на всех Site.

```text
→ export customization или реализация в App
```

---

## 33. Правильный порядок выбора

Для изменения существующего стандартного DocType полезно идти так:

```text
Можно просто изменить metadata через Customize Form?
        ↓ нет

Хватает Depends On / Fetch From / других свойств?
        ↓ нет

Нужен Client Script?
        ↓ нет

Нужна серверная логика?
        ↓ нет

Нужно расширение собственного App?
```

Не стоит начинать с JavaScript только ради того, чтобы сделать поле обязательным или переместить его выше.

---

# Часть 12. Практика

## 34. Мини-практика

Возьми любой **стандартный не-Single DocType**, который можно безопасно использовать на учебном Site.

Открой:

```text
Awesomebar
→ Customize Form
```

Выбери этот DocType.

Сделай четыре изменения:

### Шаг 1. Добавь Custom Field

```text
Label: Training Note
Field Type: Small Text
```

### Шаг 2. Перемести его

Поставь после одного из основных полей формы.

### Шаг 3. Добавь в List View

Включи:

```text
In List View
```

Если выбранный тип/раскладка это допускает.

### Шаг 4. Измени Label существующего стандартного поля

Например:

```text
старый Label → новый понятный Label
```

Сохрани customization и открой обычную форму документа.

Проверь, что изменения появились.

---

## 35. Вторая практика: понять, что сохранилось

Через Awesomebar найди:

```text
Custom Field
```

Найди созданное поле.

Затем найди:

```text
Property Setter
```

Посмотри, появился ли Property Setter для изменённого Label или порядка.

Ничего там вручную не редактируй.

Цель упражнения — просто увидеть, что Customize Form является удобным интерфейсом над этими механизмами.

---

## 36. Что не делать в учебной практике

Пока не нужно:

```text
Trim Table
Reset All Customizations
Export Custom Permissions
```

Это уже операции с более широкими последствиями.

Для понимания Customize Form достаточно безопасных изменений формы.

---

# Что запомнить

1. **Customize Form предназначен для site-specific изменения стандартного DocType.**
2. Новое поле сохраняется как **Custom Field**.
3. Изменение свойства существующего DocType/DocField обычно сохраняется как **Property Setter**.
4. Исходный JSON стандартного DocType при этом не переписывается.
5. Стандартное поле нельзя просто удалить — его обычно скрывают.
6. Некоторые свойства стандартных полей специально нельзя ослабить или произвольно изменить.
7. `Reset Layout` и `Reset All Customizations` — разные операции.
8. Удаление Custom Field не означает автоматический `DROP COLUMN`; для физической очистки существует опасный `Trim Table`.
9. В Developer Mode customizations можно экспортировать в App для воспроизводимого развёртывания.
10. Если задача решается Customize Form, писать Client Script или Python обычно ещё рано.

---

## Контрольные вопросы

1. Зачем нужен Customize Form, если DocType уже можно открыть и редактировать?
2. Чем Standard DocType отличается от Custom DocType в контексте customization?
3. Что создаётся при добавлении нового поля?
4. Что создаётся при изменении свойства стандартного поля?
5. Меняется ли исходный JSON стандартного DocType?
6. Почему стандартное поле нельзя просто удалить?
7. Чем `Reset Layout` отличается от `Reset All Customizations`?
8. Почему удаление Custom Field не обязательно удаляет колонку из БД?
9. Почему `Trim Table` опасен?
10. Когда имеет смысл Export Customizations?

Если ответы понятны без подглядывания, механизм Customize Form уже уложился правильно.

---

## Официальные источники

- [Customizing DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/customize)
- [Exporting Customizations to your App](https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations)
- [`customize_form.py`, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/custom/doctype/customize_form/customize_form.py)
- [`customize_form.js`, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/custom/doctype/customize_form/customize_form.js)
- [`custom_field.json`, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/custom/doctype/custom_field/custom_field.json)
- [`property_setter.json`, branch `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/custom/doctype/property_setter/property_setter.json)

Следующая глава: **Desk Page и границы штатного интерфейса**.