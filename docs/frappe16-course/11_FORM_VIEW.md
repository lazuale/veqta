# 11. Form View

`Form View` — это экран одного документа во Frappe.

Если List View отвечает на вопрос **«какие записи у нас есть?»**, то Form View — **«что находится внутри одной конкретной записи?»**.

В этой главе разберём форму сначала глазами обычного пользователя, а затем посмотрим, откуда берутся её поля, кнопки и дополнительное поведение.

Проверено: **2026-08-30**.

## 1. Самый простой пример

Есть DocType `Request`:

```text
Request
├── Subject
├── Department
├── Priority
├── Due Date
└── Description
```

И есть один Document:

```text
REQ-0001
```

Когда мы открываем `REQ-0001`, Frappe показывает Form View примерно такого смысла:

```text
Request
REQ-0001

Subject      Проверить отчёт
Department   Analytics
Priority     High
Due Date     2026-09-01
Description  Проверить расхождение за август

                         [Save]
```

Это и есть форма документа.

## 2. Форму не нужно писать с нуля

Это одна из главных особенностей Frappe.

Мы уже описали поля в DocType, поэтому Framework знает:

- какие поля показать;
- какого они типа;
- какие обязательные;
- какие read-only;
- какие являются Link;
- как расположены секции, колонки и вкладки.

Упрощённо:

```text
DocType + DocField metadata
           ↓
        Form View
```

Для обычного внутреннего приложения это означает: базовый экран просмотра и редактирования записи уже есть.

Не требуется начинать с HTML, Vue или React только ради формы с полями.

## 3. Новая форма и существующий документ

Один и тот же Form View используется в двух ситуациях.

### Создание

Пользователь нажал `New`:

```text
Request
New Request

Subject      [              ]
Department   [              ]
Priority     [              ]
```

Документ ещё не сохранён.

### Редактирование

Пользователь открыл уже существующий документ:

```text
Request
REQ-0001

Subject      Проверить отчёт
Department   Analytics
Priority     High
```

После Save запись уже существует в базе.

Для пользователя это один и тот же тип экрана, но состояние документа разное.

## 4. Что значит `Not Saved`

Допустим, открыли `REQ-0001` и поменяли:

```text
Priority: Medium → High
```

Но Save ещё не нажали.

Форма становится **dirty** — в ней есть несохранённые изменения.

Frappe показывает состояние вроде:

```text
Not Saved
```

Простыми словами:

> значение уже изменилось в браузере, но ещё не записано на сервер.

Если попытаться уйти со страницы с несохранёнными изменениями, Form View умеет предупреждать об этом.

## 5. Save — это не просто запись полей в SQL

Когда пользователь нажимает Save, Frappe запускает Document lifecycle.

Упрощённо:

```text
изменили форму
     ↓
    Save
     ↓
client-side проверки
     ↓
запрос на сервер
     ↓
server-side permissions и validation
     ↓
сохранение Document
     ↓
обновление формы
```

Поэтому Form View — пользовательский интерфейс над Document API, а не отдельная система хранения данных.

Server-side lifecycle подробно разберём позже в главе про controller.

## 6. Откуда берётся порядок полей

Базовый порядок формы следует metadata DocType.

Например:

```text
1. Subject
2. Department
3. Priority
4. Due Date
5. Description
```

В форме они будут идти в этой логике, если layout-элементы не задают другое расположение.

Для структуры используются уже знакомые типы полей:

```text
Section Break
Column Break
Tab Break
```

Пример:

```text
[Основное]
Subject        Priority
Department     Due Date

[Описание]
Description
```

Для такого макета не нужен собственный frontend.

## 7. Вкладки

`Tab Break` позволяет разделить длинную форму на вкладки.

Например:

```text
[Основное] [Детали] [Служебное]
```

Это полезно, когда полей уже много и одна длинная страница становится неудобной.

Но не стоит делать десять вкладок для формы из восьми полей. Layout должен упрощать работу, а не демонстрировать все возможности конструктора.

## 8. Section Break и Column Break

Два самых простых элемента разметки.

### Section Break

Начинает новый смысловой блок:

```text
Основная информация
-------------------
Subject
Department
```

### Column Break

Делит текущую секцию на колонки:

```text
Subject          Priority
Department       Due Date
```

Это layout metadata. Отдельного CSS для обычной формы не требуется.

## 9. Mandatory, Read Only и Hidden прямо влияют на форму

Свойства DocField из главы 05 становятся реальным поведением Form View.

### Mandatory

```text
Subject *
```

Без значения документ нельзя нормально сохранить.

### Read Only

Поле видно, но пользователь не может его обычным способом изменить.

Например:

```text
Calculated Total: 1500
```

### Hidden

Поле не показывается в обычной форме.

То есть свойства DocField — это не абстрактные флаги где-то в metadata. Пользователь ощущает их прямо в форме.

## 10. Условия тоже меняют форму

У поля могут быть:

```text
Display Depends On
Mandatory Depends On
Read Only Depends On
```

Простой пример.

Есть:

```text
Requires Review   Check
Reviewer          Link → User
```

Хотим показывать `Reviewer` только когда включено:

```text
Requires Review = ✓
```

Тогда форма может вести себя так:

```text
Requires Review [ ]
```

и поле Reviewer скрыто.

После включения:

```text
Requires Review [✓]
Reviewer         [             ]
```

Для такого простого поведения часто вообще не нужен Client Script.

## 11. Link-поле в форме

Пусть:

```text
Department
Field Type = Link
Options = Department
```

В Form View пользователь получает поле с поиском существующих Departments.

Он не обязан вручную вводить внутренний `name`.

Например:

```text
Department
[ Analyt... ]

Analytics
Analytics Support
Data Analytics
```

После выбора в документ сохраняется ссылка на конкретный Department.

Сам механизм Link мы уже подробно разобрали в главе 07.

## 12. Child Table внутри формы

Если у документа есть поле `Table`, Form View показывает grid.

Например:

```text
Order

Items
------------------------------------------------
Product              Qty      Price
Keyboard              2       50
Mouse                 1       20
------------------------------------------------
```

Для пользователя это таблица внутри формы.

Для Framework — список Child Documents, принадлежащих родителю.

Grid можно редактировать прямо внутри Form View; набор видимых колонок зависит от metadata дочернего DocType.

## 13. Quick Entry

Иногда полная форма слишком велика для создания простой записи.

Например, чтобы быстро добавить Department, достаточно:

```text
Department Name
Manager
```

Если для DocType включён `Quick Entry`, при создании Frappe может сначала открыть небольшой диалог вместо полной формы.

Упрощённо:

```text
+ New Department

Department Name  [          ]
Manager          [          ]

                [Save]
```

Это удобно для короткого создания связанной записи прямо во время работы.

Quick Entry — не отдельный DocType и не отдельная модель данных. Это просто сокращённый интерфейс создания того же Document.

## 14. Заголовок формы и `name`

Допустим:

```text
name = REQ-0001
subject = Проверить отчёт
```

Если `subject` назначен как `Title Field`, интерфейс может использовать его как человекочитаемый заголовок.

Техническая идентичность документа остаётся:

```text
REQ-0001
```

То есть Form View помогает пользователю видеть понятное название, не заставляя делать primary key красивым текстом.

## 15. Права меняют доступные действия

Form View учитывает permissions пользователя.

Один пользователь может иметь:

```text
Read ✓
Write ✓
Create ✓
Delete ✗
```

Другой:

```text
Read ✓
Write ✗
```

Первый сможет редактировать документ, второй увидит его в read-only режиме.

Для Submittable DocType отдельно существуют действия и permissions вроде:

```text
Submit
Cancel
Amend
```

То есть кнопки формы зависят не только от состояния Document, но и от прав текущего пользователя.

## 16. Form Sidebar

У формы есть не только поля.

Штатный Form Sidebar позволяет работать с сервисами вокруг документа.

К ним относятся, в частности:

```text
Assignments
Sharing
Attachments
Tags
```

Пример: у `REQ-0001` можно прикрепить файл без создания собственного поля `file_1`:

```text
REQ-0001
└── Attachments
    ├── report.xlsx
    └── screenshot.png
```

Attachments — отдельный штатный механизм Frappe. Подробно он будет разобран позже.

## 17. Assignment не является полем `assigned_to`

Это полезно увидеть именно на форме.

Можно назначить документ пользователю через штатный Assign-механизм, даже если в самом DocType нет поля:

```text
assigned_to
```

То есть есть два разных подхода:

```text
поле Link → User
```

и:

```text
штатный Assignment / ToDo
```

Они решают разные задачи. Assignment подробно разберём в отдельной главе.

## 18. Share

Документ можно штатно поделить с другим пользователем через механизм Sharing.

Это тоже не требует добавлять в каждый DocType собственную таблицу вроде:

```text
users_with_access
```

Форма даёт пользовательскую точку входа в этот механизм, а реальные правила доступа обслуживает Framework.

## 19. Attachments

К Document можно прикреплять файлы.

Frappe поддерживает несколько способов, включая загрузку файла и drag-and-drop.

Практический пример:

```text
Request REQ-0001

Attachments:
- source.xlsx
- photo.jpg
```

Пользователи с Read-доступом к документу получают доступ к связанным с ним вложениям согласно штатной модели Frappe.

Отдельные поля `Attach` и общий список Attachments — связанные, но не одинаковые механизмы. Это подробно разберём в главе про File и Attachments.

## 20. Timeline

Внизу Form View есть timeline документа.

Он показывает историю связанных событий в обратном хронологическом порядке.

Например:

```text
30 Aug 18:40  Ivan changed Priority: Medium → High
30 Aug 18:15  Anna added a comment
30 Aug 17:50  Email sent
```

В timeline могут попадать:

```text
comments
emails
edits / version information
assignment/share events
другие события документа
```

Это сильно отличается от обычного текстового поля `Comments`.

Timeline — системная история вокруг конкретного Document.

## 21. Комментарий не нужно моделировать как Child Table по умолчанию

Представим желание добавить к Request обсуждение:

```text
Request Comment
├── author
├── text
└── date
```

и потом сделать Child Table комментариев.

Для обычного обсуждения документа это часто лишнее: Frappe уже имеет штатные Comments и Timeline.

Собственный DocType комментариев нужен только если у предметной области действительно другая сущность с отдельной логикой.

## 22. Print прямо из формы

Для Document Frappe имеет штатный Print View.

Для обычного DocType Framework может сформировать стандартное печатное представление на основе layout.

Из Form View пользователь может перейти к печати и PDF.

Поэтому задача:

> «нужно распечатать документ»

сама по себе ещё не означает:

> «нужно писать генератор PDF».

Print Format подробно разберём позже.

## 23. Email из формы

Form API содержит штатный механизм открытия Email dialog для текущего документа.

То есть Form View может быть точкой, откуда пользователь отправляет связанное с документом письмо.

Это связано с системными `Communication` и email-механизмами Frappe, которые будут отдельной темой курса.

## 24. Form Dashboard

У формы может быть dashboard с дополнительной информацией о связанных объектах и показателях.

Простая идея:

```text
Customer CUST-001

Orders: 12
Invoices: 8
```

Сам Customer при этом остаётся одним Document. Dashboard просто помогает перейти к связанным данным или увидеть их количество.

Не нужно добавлять в Customer двенадцать полей `order_1`, `order_2` и так далее.

## 25. Когда формы из metadata уже достаточно

Допустим, нужна внутренняя карточка заявки:

```text
Subject
Department
Priority
Due Date
Description
Attachments
Comments
Assigned User
```

Очень большая часть этого уже закрывается штатно:

| Требование | Что использовать |
|---|---|
| обычные поля | DocField |
| расположение | Section / Column / Tab Break |
| связанный отдел | Link |
| вложения | Attachments |
| обсуждение | Comments / Timeline |
| назначение | Assignment |
| доступ | Permissions / Sharing |
| печать | Print View / Print Format |

Перед созданием собственного Form frontend стоит сначала собрать такой вариант и проверить, чего реально не хватает.

## 26. Customize Form

Если DocType уже существует, его форму можно изменять через штатный `Customize Form`.

Там можно, например:

```text
добавить Custom Field
переставить поля
изменить label
скрыть поле
сделать его read-only
настроить часть view-свойств
```

Это site-level customization.

В отдельной главе разберём, что именно Customize Form сохраняет и чем это отличается от изменения Standard DocType в App.

## 27. Когда появляются Form Scripts

Metadata умеет много, но не всё.

Допустим, при нажатии кнопки нужно создать другой Document или выполнить динамическую реакцию на изменение поля.

Тогда появляется Form Script.

Простой пример из документации Frappe:

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        frm.add_custom_button('Create Review', () => {
            frappe.new_doc('Review', {
                request: frm.doc.name
            });
        });
    }
});
```

После этого в форме появляется пользовательская кнопка.

Но важно соблюдать порядок:

```text
сначала DocType / DocField / стандартные настройки
        ↓
если не хватает
Client Script / standard Form Script
```

Не писать JS для того, что уже умеет `Mandatory`, `Depends On`, `Fetch From` или permissions.

## 28. `frm`

В Form Script текущая форма обычно доступна как объект:

```javascript
frm
```

А текущий документ:

```javascript
frm.doc
```

Например:

```javascript
frm.doc.subject
frm.doc.priority
frm.doc.name
```

Изменить значение штатным способом можно через:

```javascript
frm.set_value('priority', 'High');
```

Этот вызов обновляет значение в форме и запускает соответствующее field change event.

На данном этапе этого достаточно. Полный Form API будет нужен, когда дойдём до Client Script.

## 29. Основные события формы

Form Script работает через события.

Для первого знакомства достаточно знать несколько:

```text
setup
onload
refresh
validate
before_save
after_save
before_submit
on_submit
before_cancel
```

Пример:

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        // форма уже показана пользователю
    }
});
```

Не нужно сейчас заучивать весь список. Важно понять принцип:

> Form Script не работает «сам по себе» — код привязывается к событию формы или поля.

## 30. Client-side validation не заменяет server-side validation

Это принципиальный момент.

Можно написать в Form Script:

```javascript
validate(frm) {
    // проверить значение
}
```

Но этот код выполняется в браузерной Form View.

Документ может быть создан и другим путём, например через API или server-side код.

Поэтому правило, которое обязано соблюдаться **всегда**, нельзя защищать только Client Script.

Упрощённо:

```text
удобство интерфейса
→ Client Script подходит

целостность бизнес-данных
→ нужна server-side проверка
```

Подробно эту границу разберём в главах про Client Script, Server Script и controller.

## 31. DocType Layout в актуальном Frappe

В текущем Frappe есть также механизм `DocType Layout`, который позволяет создавать альтернативные layout формы одного DocType с переопределением части свойств полей и условным выбором layout.

Например, один и тот же документ можно показывать компактнее в одном состоянии и подробнее в другом.

Это более продвинутая возможность. Для первого знакомства достаточно помнить:

```text
обычный случай
→ layout основного DocType

нужны разные варианты формы одного DocType
→ изучить DocType Layout
```

Не следует начинать проектирование простой формы с нескольких layouts без реальной необходимости.

## 32. Что Form View не делает сам

Form View очень мощный, но он не угадывает предметную логику.

Он не знает сам, что:

```text
Priority должна стать High при условии X

нужно создать второй документ после события Y

поле A должно рассчитываться по сложной формуле

нужно обратиться к внешнему API
```

Такое поведение добавляется настройками, scripting или кодом App — в зависимости от задачи.

Главное не путать:

```text
Form View
= готовая оболочка работы с Document

бизнес-логика
= отдельные правила поверх этой оболочки
```

## 33. Простая карта Form View

После этой главы форму удобно представлять так:

```text
┌───────────────────────────────────────┐
│ Request: REQ-0001                     │
│                          [Save] [...] │
├───────────────────────────────────────┤
│                                       │
│  поля из DocType / DocField metadata  │
│                                       │
│  Subject      ...                     │
│  Department   ...                     │
│  Priority     ...                     │
│                                       │
│  Child Table / Grid при необходимости │
│                                       │
├───────────────────────────────────────┤
│ Timeline                              │
│ comments / emails / edits / events    │
└───────────────────────────────────────┘

справа / вокруг формы:
Assignments / Sharing / Attachments / Tags
```

Поверх этого могут работать:

```text
Permissions
Workflow
Form Script
Print
Email
и другие механизмы Framework
```

## 34. Мини-практика

Возьми любой простой учебный DocType, например `Request`.

Сделай поля:

```text
Subject       Data        Mandatory
Department    Link        → Department
Priority      Select      Low / Medium / High
Due Date      Date
Description   Small Text
```

Затем:

1. создай новый Request;
2. посмотри, как metadata превратилась в Form View;
3. измени Priority и обрати внимание на `Not Saved`;
4. сохрани документ;
5. добавь attachment;
6. добавь comment;
7. посмотри timeline;
8. если доступны права — попробуй Assign и Share;
9. открой Print View;
10. вернись в DocType и переставь поля через Section/Column Break, затем снова открой форму.

После этого Form View перестаёт выглядеть «магическим»: становится видно, какие части пришли из metadata, а какие являются отдельными сервисами Framework.

## Что запомнить

1. `Form View` — штатный экран одного Document.
2. Базовая форма строится из metadata DocType и DocField.
3. Section, Column и Tab Break управляют layout без собственного frontend.
4. Permissions влияют не только на данные, но и на доступные действия формы.
5. Assignments, Sharing, Attachments, Tags и Timeline — штатные сервисы вокруг Document.
6. Quick Entry — сокращённое создание того же Document, а не отдельная сущность.
7. Form Script нужен для динамического поведения, которого уже не дают metadata и настройки.
8. Client-side validation не должна быть единственной защитой обязательного бизнес-правила.

## Официальные источники

- [Desk — Form View](https://docs.frappe.io/framework/user/en/desk)
- [Form Scripts / Form API](https://docs.frappe.io/framework/user/en/api/form)
- [Form Scripts Tutorial](https://docs.frappe.io/framework/user/en/tutorial/form-scripts)
- [Create a DocType — Form Layout](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Form & View Settings](https://docs.frappe.io/framework/user/en/basics/doctypes/form_%26_view_settings)
- [Attachments](https://docs.frappe.io/framework/user/en/desk/attachments)
- [Printing](https://docs.frappe.io/framework/user/en/desk/printing)
- [Dialog API — Quick Entry behaviour](https://docs.frappe.io/framework/user/en/api/dialog)
- [DocType Layout](https://docs.frappe.io/framework/doctypes/doctype-layout)
- [Frappe v16 source: form.js](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/form.js)

---

Предыдущая глава: [**10. `docstatus`, Submit, Cancel и Amendment**](10_DOCSTATUS_LIFECYCLE.md)

Следующая глава: **12. List View и фильтры**.