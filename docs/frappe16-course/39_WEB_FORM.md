# 39. Web Form

В блоке G мы закончили с данными и аналитикой внутри Frappe.

Теперь начинается блок H — **внешние интерфейсы**.

Первый штатный инструмент здесь — `Web Form`.

Он отвечает на очень практичный вопрос:

```text
как дать человеку форму Frappe
не пуская его в Desk
```

Например:

```text
заявка с сайта
анкета
обращение
регистрация
опрос
форма обратной связи
запрос от подрядчика
ввод данных внешним пользователем
```

При этом результатом остаётся не письмо и не произвольный JSON, а обычный:

```text
Frappe Document
```

в выбранном DocType.

Проверено: **2026-08-31**.

---

# Часть I. Модель Web Form

## 1. Что такое Web Form простыми словами

Представим DocType:

```text
Request
```

с полями:

```text
subject
department
priority
description
```

Обычная форма этого документа живёт в Desk:

```text
Desk
→ Request
→ New
```

Но внешнему человеку Desk может быть вообще не нужен.

Для него можно создать Web Form:

```text
Request Form
```

и получить URL вроде:

```text
/request/new
```

Человек открывает страницу в обычном браузере, заполняет её и нажимает кнопку.

Framework создаёт:

```text
Request REQ-0001
```

То есть схема такая:

```text
Browser
   ↓
Web Form
   ↓
DocType
   ↓
Document
```

---

## 2. Аналогия

`DocType` — это модель и правила документа.

`Desk Form` — внутреннее рабочее окно сотрудника.

`Web Form` — отдельное окно приёма данных для сайта или portal-сценария.

Можно представить офис:

```text
DocType
→ карточка дела внутри организации

Desk Form
→ рабочее место сотрудника

Web Form
→ окно приёма посетителей
```

Посетителю не нужно видеть весь внутренний интерфейс только для того, чтобы передать одну заявку.

---

## 3. Web Form не создаёт второй DocType

Это принципиально.

Если Web Form привязана к:

```text
Request
```

то отправка формы создаёт обычный:

```text
Request
```

а не отдельный объект вроде:

```text
Web Request
Form Response
External Request
```

если только вы сами не спроектировали такую модель.

То есть Web Form — это в первую очередь:

> **другой интерфейс к Document того же DocType.**

---

## 4. Desk Form и Web Form — разные интерфейсы

Не нужно путать:

```text
Desk Form
```

и:

```text
Web Form
```

Они могут работать с одним DocType, но это разные UI-механизмы.

Например:

```text
Request
├── Desk Form → сотрудник работает с полной карточкой
└── Web Form  → внешний пользователь вводит 4 разрешённых поля
```

Web Form не обязана показывать все поля DocType.

Наоборот, обычно она показывает только небольшой безопасный набор.

---

## 5. Главная идея Web Form

Удобная формула:

```text
DocType
+
выбранный набор полей
+
web route
+
правила доступа
+
немного web-настроек
=
Web Form
```

Это не отдельный frontend framework.

Это готовый штатный интерфейс Frappe для довольно стандартного сценария:

```text
показать форму
→ получить данные
→ создать/обновить Document
```

---

# Часть II. Создаём первую Web Form

## 6. Базовое создание

В Desk можно найти:

```text
Web Form
```

или воспользоваться Awesomebar и создать новую Web Form.

Минимально задаём:

```text
Title      = Request Form
Route      = request
Select DocType = Request
```

После выбора DocType можно использовать:

```text
Get Fields
```

чтобы подтянуть поля из модели, либо добавить нужные поля вручную.

После этого Web Form нужно опубликовать.

---

## 7. Пример минимальной формы

Пусть `Request` содержит:

```text
subject      Data
email        Data
priority     Select
description  Text
status       Select
assigned_to  Link
internal_note Text
```

В Web Form можно оставить только:

```text
subject
email
priority
description
```

Тогда внешний пользователь не получает UI для:

```text
status
assigned_to
internal_note
```

Это уже важная граница интерфейса.

---

## 8. Route

Поле:

```text
Route
```

задаёт web-route формы.

Например:

```text
Route = request
```

Основные URL текущего v16 строятся вокруг этого route:

```text
/request
/request/new
/request/list
/request/<document-name>
/request/<document-name>/edit
```

Но конкретно доступные варианты зависят от настроек формы.

Например `list` имеет смысл только при включённом:

```text
Show List
```

а редактирование — при:

```text
Allow editing after submit
```

Если открыть просто:

```text
/request
```

Framework перенаправит пользователя либо на:

```text
/request/new
```

либо на:

```text
/request/list
```

в зависимости от конфигурации.

---

## 9. Published — реальный выключатель Web Form

Web Form должна быть опубликована.

В текущем v16 проверка publication выполняется не только при отрисовке страницы, но и на backend endpoints сохранения/удаления/получения данных.

То есть снятие публикации — это не просто:

```text
спрятать ссылку
```

а штатный способ вывести Web Form из эксплуатации.

---

## 10. Web Form обрабатывается website router

Это уже не Desk route.

Web request идёт через website routing Frappe.

Упрощённо:

```text
HTTP request
→ website router
→ WebformPage
→ Web Form
→ HTML page
```

То есть `/request/new` — обычная web-страница Frappe, а не экран Desk SPA.

Эта разница станет важной в следующей главе про Website / Portal.

---

# Часть III. Поля Web Form

## 11. Web Form выбирает интерфейсный набор полей

В дочерней таблице:

```text
Web Form Fields
```

задаётся, какие поля пользователь увидит.

Для каждого элемента доступны свойства вроде:

```text
Field
Fieldtype
Custom Label
Mandatory
Read Only
Hidden
Options
Description
Default
Placeholder
Max Length
Max Value
Precision
Display Depends On
Mandatory Depends On
Read Only Depends On
Show in filter
```

То есть Web Form может иметь собственное представление поля, не копируя Desk Form один в один.

---

## 12. Какие Field Type поддерживает Web Form v16

В текущем `Web Form Field` штатно перечислены:

```text
Attach
Attach Image
Check
Currency
Color
Data
Date
Datetime
Duration
Float
HTML
Int
Link
Password
Phone
Rating
Select
Signature
Small Text
Text
Text Editor
Table
Time
Section Break
Column Break
Page Break
```

Это уже довольно богатая форма без отдельного frontend-кода.

---

## 13. Layout: Section Break и Column Break

Как и в обычных формах, можно использовать:

```text
Section Break
Column Break
```

Например:

```text
Контактные данные
-----------------
Имя        | Email
Телефон    | Компания

Описание запроса
----------------
Тема
Описание
```

То есть Web Form не обязана быть одной длинной колонкой.

---

## 14. Page Break превращает форму в Multi Step

Если полей много, можно добавить:

```text
Page Break
```

и получить многошаговую форму:

```text
Шаг 1
→ контакты

Шаг 2
→ данные заявки

Шаг 3
→ подтверждение
```

Документация v16 указывает максимум:

```text
9 Page Breaks
→ до 10 страниц
```

Это хороший предел для обычной анкеты.

Если вам уже нужно 25 экранов с ветвящейся навигацией и сложным состоянием, это первый признак, что задача выходит за естественную границу Web Form.

---

## 15. Mandatory в Web Form и Mandatory в DocType — не одно и то же место настройки

У поля Web Form есть свой:

```text
Mandatory
```

Но у исходного DocField тоже может быть:

```text
Reqd
```

Поэтому нужно различать:

```text
обязательность в интерфейсе Web Form
```

и:

```text
обязательность модели Document
```

Если DocType требует поле на уровне модели, просто убрать его из Web Form недостаточно.

Нужно либо:

```text
дать ему default
заполнять его серверной логикой
передать скрытым доверенным способом
```

либо пересмотреть модель.

---

## 16. Hidden mandatory field без Default

Текущий v16 отдельно валидирует опасный случай:

```text
Hidden = 1
Mandatory = 1
Default пустой
```

Если `Allow incomplete forms` не включён, такая конфигурация Web Form считается некорректной.

Логика понятна:

```text
поле обязательно
+
пользователь его не видит
+
значения по умолчанию нет
=
пользователь физически не может заполнить форму
```

---

## 17. Depends On

Web Form Field поддерживает зависимые свойства:

```text
Display Depends On
Mandatory Depends On
Read Only Depends On
```

Например поле:

```text
company_name
```

можно показывать только если:

```text
customer_type = Company
```

Это позволяет закрыть много простых динамических сценариев без отдельного frontend.

---

## 18. Default и Placeholder

Можно отдельно настроить:

```text
Default
Placeholder
```

Например:

```text
Priority
Default = Medium
```

или:

```text
Email
Placeholder = name@example.com
```

Но Default в браузере не нужно использовать как единственную гарантию бизнес-правила.

Если значение критично, его должен проверять и сервер.

---

## 19. Web Form принимает только настроенные поля

Это важный момент реализации v16.

При сохранении backend не делает:

```python
doc.update(all_input_from_browser)
```

Вместо этого он проходит по:

```text
web_form.web_form_fields
```

и берёт значения только для настроенных полей.

Упрощённо:

```python
for field in web_form.web_form_fields:
    doc.set(field.fieldname, submitted_value)
```

Поэтому если злоумышленник руками добавит в HTTP payload:

```text
internal_note = "..."
is_admin = 1
```

сам по себе такой лишний ключ не означает, что Web Form запишет его в Document.

Это одна из важных встроенных границ механизма.

---

# Часть IV. Что происходит при Submit

## 20. Нажатие Submit создаёт обычный Document

Для новой записи текущий backend делает по смыслу:

```python
doc = frappe.new_doc(doctype)
# заполнение разрешённых Web Form fields
doc.insert(...)
```

То есть дальше участвует обычная Document-модель Frappe.

Продолжают иметь значение:

```text
naming
controller lifecycle
validate
before_insert
after_insert
Link validation
custom server logic
hooks
Notification и другие side effects
```

если они настроены на этот Document lifecycle.

---

## 21. `ignore_permissions=True` не означает `ignore_validation=True`

Для создания через Web Form текущий v16 вызывает вставку с:

```text
ignore_permissions = True
```

Это нужно, чтобы публичная форма могла создавать Document даже без обычного Desk-доступа Guest к целевому DocType.

Но это не означает:

```text
отключить controller
отключить validate
отключить naming
отключить Link checks
отключить бизнес-логику
```

Permissions и Document lifecycle — разные слои.

---

## 22. Кнопка Submit Web Form — не `doc.submit()`

Это очень частая путаница терминов.

В Web Form кнопка может называться:

```text
Submit
```

но backend новой Web Form записи выполняет:

```python
doc.insert()
```

а не автоматически:

```python
doc.submit()
```

Поэтому для `Is Submittable` DocType Web Form по умолчанию не означает:

```text
создать сразу Submitted document с docstatus = 1
```

Обычно создаётся обычный Document / Draft, а настоящий Frappe Submit lifecycle — отдельная операция.

---

## 23. `Allow incomplete forms`

Настройка:

```text
Allow incomplete forms
```

разрешает сохранять форму, даже когда standard mandatory fields не заполнены.

Текущий backend выставляет для Document:

```text
ignore_mandatory
```

Но это не должно восприниматься как:

```text
отключить всю серверную валидацию
```

Собственный controller всё равно может отказать в сохранении по своим правилам.

Использовать этот флаг лучше для осознанного сценария:

```text
черновая анкета
неполный intake
поэтапное заполнение
```

а не как способ «починить» плохо спроектированную модель.

---

# Часть V. Три модели доступа

## 24. Web Form может быть публичной

Если:

```text
Login required = 0
Key required   = 0
```

форма доступна Guest.

Сценарий:

```text
любой посетитель
→ /request/new
→ заполнить
→ создать Document
```

Это классическая публичная форма сайта.

---

## 25. Web Form может требовать Login

Если включить:

```text
Login required
```

Guest больше не может отправлять форму.

Пользователь должен иметь Frappe account и активную session.

Такой сценарий уже ближе к личному кабинету:

```text
login
→ мои заявки
→ новая заявка
→ посмотреть предыдущую
→ отредактировать
```

Но Web Form всё ещё остаётся готовым интерфейсом конкретного DocType, а не полноценным приложением.

---

## 26. Web Form может требовать private key

В актуальном v16 есть третий вариант:

```text
Key required
```

Он работает вместе с:

```text
Web Form Request
```

Сценарий:

```text
создали персональный request
→ Framework сгенерировал key
→ отправили private URL человеку
→ человек открыл форму без обычного аккаунта
→ key разрешил именно этот request
```

URL выглядит по смыслу так:

```text
/request/new?web_form_request_key=<key>
```

Это полезно для:

```text
опросов по приглашению
персональной анкеты
customer satisfaction survey
подтверждения данных
формы для конкретного контрагента
```

---

## 27. Login Required и Key Required можно совместить

Если включены оба:

```text
Login required = 1
Key required   = 1
```

нужно одновременно:

```text
быть залогиненным
+
иметь действительный request key
```

То есть это уже двухусловная модель доступа к конкретному web-form flow.

---

## 28. Web Form Request умеет prefill

В `Web Form Request` есть два разных типа значений.

### Web Form Values

Это значения, которые передаются в саму форму и видны пользователю.

Например:

```json
{
  "customer": "CUST-0001"
}
```

Пользователь открывает форму и видит предзаполненный Customer.

### Doc Values

Это значения, которые применяются к создаваемому Document на сервере, но не отправляются пользователю как поля формы.

Например:

```json
{
  "survey_source": "Partner CSAT"
}
```

Так можно безопаснее привязать response к внутреннему контексту.

---

## 29. Hidden Doc Values сильнее обычного browser default

Если критичный контекст выглядит так:

```text
customer = CUST-0001
campaign = 2026-Q3
source = private-invite
```

не всегда правильно отправлять всё это в browser как editable/default fields.

`Web Form Request.Doc Values` позволяет сделать:

```text
private link
→ server-side bound values
→ Document
```

Это значительно лучше, чем надеяться, что пользователь не поменяет hidden HTML input руками.

---

## 30. Request key привязывается к созданным Documents

Для single-response request после успешной отправки key связывается с созданным Document.

Это позволяет позже открыть этот же response для:

```text
просмотра
редактирования
удаления
```

если соответствующие опции Web Form разрешены.

Для:

```text
Allow multiple responses
```

один key может быть связан уже с несколькими responses.

---

# Часть VI. Один response, несколько responses и список

## 31. По умолчанию Login Required Web Form может быть single-response

Если пользователь вошёл и:

```text
Allow multiple responses = 0
```

Framework пытается использовать одну запись пользователя для этой Web Form.

В текущем v16 при открытии формы без конкретного docname он ищет Document этого DocType, где:

```text
owner = current user
```

с учётом `Condition JSON`, если оно настроено.

Если запись найдена, пользователь отправляется к ней вместо создания бесконечных новых responses.

---

## 32. `Allow multiple responses`

Если включить:

```text
Allow multiple responses
```

один пользователь или request key может создавать несколько Documents.

Пример:

```text
один пользователь
├── Request REQ-0001
├── Request REQ-0005
└── Request REQ-0012
```

Это естественный режим для:

```text
заявок
обращений
заказов
регистраций на разные события
```

---

## 33. `Show List`

Настройка:

```text
Show List
```

добавляет Web Form List View.

Например:

```text
/request/list
```

Пользователь может увидеть список responses, доступных ему через Web Form.

Можно настроить:

```text
List Title
List Columns
Show in filter
```

Это уже даёт простейший вариант:

```text
"мои заявки"
```

без разработки отдельной страницы списка.

---

## 34. Web Form List — не Desk List View

Даже если внешне идея похожа:

```text
список документов
```

это другой механизм.

Desk List View предназначен для внутренней работы System Users и имеет гораздо более богатый набор действий.

Web Form List — облегчённый website-интерфейс вокруг responses конкретной Web Form.

Не стоит ожидать от него автоматически:

```text
весь toolbar Desk
mass actions
все saved filters
report views
kanban
workspace navigation
```

---

# Часть VII. Просмотр, редактирование и удаление

## 35. `Allow editing after submit`

Если включить:

```text
Allow editing after submit
```

доступный пользователю response можно открыть в edit mode.

Условно:

```text
/request/REQ-0001/edit
```

При сохранении Web Form загружает существующий Document и делает обычный:

```python
doc.save(...)
```

после заполнения полей формы.

---

## 36. Allow Edit не означает «редактировать любой Document DocType»

Нельзя мыслить так:

```text
Allow edit = 1
→ пользователь может вписать любое name в URL
→ редактировать всё
```

Framework отдельно проверяет, имеет ли пользователь web-form доступ к конкретному Document.

Для Guest произвольный docname без подходящего `Web Form Request` вообще не является допустимым способом открыть чужой response.

---

## 37. `Allow Delete`

При включённом:

```text
Allow Delete
```

доступный response можно удалить из Web Form flow.

В обычном logged-in сценарии endpoint удаления проверяет ownership документа.

В key-based сценарии проверяется связь request key с конкретным Document.

Поэтому это не универсальная кнопка:

```text
frappe.delete_doc(anything)
```

---

# Часть VIII. Permissions — самая важная часть главы

## 38. Web Form permissions не равны Desk permissions

Это место нужно понять особенно хорошо.

У Frappe уже есть:

```text
Role Permission
User Permission
Owner
Sharing
Permission Level
```

Но Web Form добавляет собственный внешний access flow.

Иначе публичная форма была бы бессмысленной:

```text
Guest должен получить Create на весь Request DocType
```

Это было бы слишком грубо.

Вместо этого Web Form сама становится контролируемым каналом создания.

---

## 39. Почему Public Web Form может создать Document без Guest Create permission

В текущем v16 новая запись Web Form вставляется через:

```text
doc.insert(ignore_permissions=True)
```

после того, как Framework уже проверил:

```text
Web Form опубликована
login requirement
key requirement
набор разрешённых Web Form fields
```

Отсюда важный вывод:

> Для публичного intake обычно не нужно выдавать Guest глобальное `Create` на целевой DocType только ради Web Form.

Это одна из причин использовать Web Form вместо самодельного прямого API без ясной модели доступа.

---

## 40. Но backend rules DocType всё равно важны

`ignore_permissions=True` снимает именно permission check операции создания.

Он не превращает Web Form в обход всей модели.

Если controller говорит:

```python
def validate(self):
    if self.amount < 0:
        frappe.throw("Amount cannot be negative")
```

Web Form не должна суметь сохранить отрицательное значение только потому, что это публичная форма.

Поэтому критические business rules должны жить на сервере.

---

## 41. Owner — базовый web-form доступ logged-in пользователя

Когда `Apply document permissions` выключен, текущая Web Form permission model сначала позволяет authenticated пользователю работать со своим Document, если:

```text
owner == frappe.session.user
```

Также Framework может учитывать website-specific permission hooks.

Поэтому типичный сценарий:

```text
пользователь вошёл
→ создал свой response
→ может открыть свой response
```

даже если вы не строите для него полноценный Desk role model.

---

## 42. `Apply document permissions`

Если включить:

```text
Apply document permissions
```

Web Form при доступе к существующему Document переключается на обычную document permission model:

```text
Role Permissions
User Permissions
Share
Owner rules
другие стандартные permission checks
```

Это нужно, когда Web Form должна уважать ту же модель доступа к существующим Documents, что и остальная система.

Удобная логика:

```text
Apply document permissions = 0
→ web-form ownership / website access model

Apply document permissions = 1
→ обычный Document permission check
```

---

## 43. Public create и public read — разные права

Очень важно не делать неправильный вывод:

```text
Guest может отправить Web Form
→ Guest может читать все созданные Request
```

Нет.

В обычной публичной форме без request key Guest направляется к:

```text
/route/new
```

и не получает произвольный доступ к существующим Documents по их `name`.

Создать response и читать базу responses — совершенно разные операции.

---

## 44. Web Form — не способ обойти permissions

Если задача звучит так:

```text
пользователю нельзя видеть документы в Desk,
поэтому сделаем Web Form и покажем ему все документы там
```

нужно остановиться и спроектировать access model.

Web Form — штатный внешний интерфейс, но не loophole для обхода правил безопасности.

Особенно внимательно нужно проектировать:

```text
Link fields
List View
editing
attachments
private files
request keys
custom scripts
```

---

# Часть IX. Link fields

## 45. Link в Web Form обрабатывается отдельно

В текущем v16 сервер преобразует Web Form `Link` field для web-интерфейса в вариант Autocomplete и отдельно получает доступные options.

Это важно, потому что Link может случайно раскрыть справочник.

Например поле:

```text
Customer → Link Customer
```

не должно автоматически означать:

```text
любой Guest может перебрать всех Customers
```

---

## 46. `Allow Read On All Link Options`

Для Link field Web Form существует опция:

```text
Allow Read On All Link Options
```

Она появляется для login-required сценария.

Использовать её нужно осознанно: список Link options сам по себе является данными.

Если справочник содержит чувствительные названия, внутренние объекты или клиентов, нельзя расширять read только ради удобного dropdown.

---

## 47. Особое ограничение Guest + Key Required

В текущем v16 для Web Form, где:

```text
Key required = 1
Login required = 0
```

Link field может ссылаться только на DocType, доступный Guest для чтения.

Framework валидирует это при сохранении Web Form.

Это защита от сценария:

```text
private key к одной анкете
→ неожиданно даёт возможность искать внутренний Link DocType
```

---

# Часть X. Attachments, Comments и Print

## 48. Attach field и Attachment Section — разные вещи

Можно добавить в Web Form поле типа:

```text
Attach
Attach Image
```

Это конкретное поле Document.

Отдельно существует настройка:

```text
Show attachments
```

которая показывает attachment section уже существующего Document.

Не путай:

```text
Attach field
→ значение конкретного поля

Show attachments
→ список File, прикреплённых к Document
```

---

## 49. Max Attachment Size

Есть настройка:

```text
Max attachment size
```

в MB.

Если она не задана, Web Form использует общий maximum file size Site.

Это нужно рассматривать вместе с общей file/security model Frappe, которую мы уже разбирали в главе 31.

---

## 50. `Allow comments`

Для login-required Web Form можно включить:

```text
Allow comments
```

Тогда под response появляется comment section, а комментарии связываются с тем же Document.

Для простого portal-like сценария это уже позволяет получить:

```text
заявка
+
обсуждение по заявке
```

без отдельной системы сообщений.

---

## 51. `Allow print`

Можно включить:

```text
Allow print
```

и при необходимости выбрать:

```text
Print Format
```

Print-кнопка появляется в view mode.

То есть Web Form может не только принимать данные, но и дать пользователю ограниченный способ просмотреть и распечатать свой response.

---

# Часть XI. Настройки списка и фильтрация

## 52. List Columns

Для `Show List` можно явно задать колонки.

Например:

```text
name
subject
status
creation
```

И получить простой внешний список:

```text
REQ-0001 | Printer broken | Open   | 2026-08-31
REQ-0005 | VPN access     | Closed | 2026-08-30
```

Если List Columns не заданы, Framework строит базовый набор из title/status/in-list-view metadata целевого DocType.

---

## 53. `Show in filter`

У Web Form Field есть:

```text
Show in filter
```

что позволяет использовать выбранные fields как фильтры web list.

Это полезно для простого сценария:

```text
My Requests
→ Status = Open
```

Но это всё ещё не Report Builder и не универсальная аналитическая страница.

---

## 54. Condition JSON

В Web Form есть:

```text
Condition JSON
```

Оно особенно важно, если для одного DocType создано несколько Web Forms.

Например:

```text
Employee Feedback 2026
Employee Feedback 2027
```

оба пишут в:

```text
Feedback
```

и имеют поле:

```text
year
```

Тогда условие Web Form помогает Framework отличать response именно этого web-form flow.

Например по смыслу:

```text
year = 2026
```

При single-response login flow это условие участвует в поиске уже существующего документа пользователя.

---

# Часть XII. Что происходит после отправки

## 55. Submit button label

Можно поменять:

```text
Submit button label
```

Например:

```text
Save
Send Request
Register
Submit Survey
```

Это только UI label.

Он не меняет Document lifecycle сам по себе.

---

## 56. Success Title и Success Message

После успешного сохранения можно показать собственные:

```text
Success Title
Success Message
```

Например:

```text
Заявка принята

Мы получили обращение. Номер заявки: ...
```

Это позволяет закрыть простой пользовательский flow без отдельной thank-you page.

---

## 57. Success URL

Можно указать:

```text
Success URL
```

После отправки Framework перенаправит пользователя на заданный URL.

Например:

```text
/thanks
/my-account
/help
```

Это уже позволяет связать Web Form с более широким website flow.

---

# Часть XIII. Внешний вид

## 58. Introduction

Поле:

```text
Introduction
```

показывает вводный текст над формой.

Например:

```text
Заполните обязательные поля.
Ответ придёт на указанный email.
```

Это намного лучше, чем создавать отдельный HTML page только ради двух абзацев перед формой.

---

## 59. Banner Image

Можно задать:

```text
Banner Image
```

для визуального оформления формы.

---

## 60. Navbar, Footer и Sidebar

В v16 у Web Form есть настройки:

```text
Hide navbar
Hide footer
Show sidebar
Website Sidebar
```

То есть форму можно встроить либо в обычное website-окружение, либо сделать более изолированной.

Sidebar позволяет связать несколько web pages / web forms в простой portal-подобный набор разделов.

---

## 61. Meta fields

В актуальной metadata v16 есть:

```text
Meta title
Meta description
Meta image
```

Они управляют метаданными web page.

Для публичной страницы это полезно для:

```text
browser title
link preview
search metadata
```

При этом сама Web Form в текущей реализации не разрешает website search indexing через стандартный Web Form renderer.

---

## 62. Allowed Embedding Domains

В v16 есть:

```text
Allowed embedding domains
```

для контроля origin/domain, которым разрешено встраивать форму.

Если список не задан, metadata описывает поведение как same-origin embedding.

Это важно, если Web Form используется внутри iframe другого сайта.

---

## 63. Custom CSS

В `Customization` можно добавить:

```text
Custom CSS
```

Например изменить отступы, ширину, border или оформление header.

Это хороший уровень, если задача звучит:

```text
форма функционально устраивает,
но нужно немного подправить внешний вид
```

Писать новый frontend только ради пары CSS-правил обычно не нужно.

---

# Часть XIV. Client Script Web Form

## 64. У Web Form свой client scripting API

В Web Form можно написать:

```text
Client script
```

Но это не тот же API, что стандартный Desk Form Script.

Для Web Form используется объект:

```javascript
frappe.web_form
```

а не основной Desk pattern:

```javascript
frappe.ui.form.on(...)
```

---

## 65. Реакция на изменение поля

Базовый API:

```javascript
frappe.web_form.on('priority', (field, value) => {
    // реакция
});
```

Например:

```javascript
frappe.web_form.on('priority', (field, value) => {
    if (value === 'High') {
        frappe.msgprint('Добавьте подробное описание проблемы');
    }
});
```

---

## 66. Получить значение

```javascript
const value = frappe.web_form.get_value('priority');
```

---

## 67. Установить значение

```javascript
frappe.web_form.set_value('priority', 'Medium');
```

---

## 68. Изменить свойство field

```javascript
frappe.web_form.set_df_property('description', 'hidden', 1);
```

Например:

```javascript
frappe.web_form.on('priority', (field, value) => {
    frappe.web_form.set_df_property(
        'reason',
        'hidden',
        value !== 'High'
    );
});
```

---

## 69. `after_load`

Код после загрузки формы:

```javascript
frappe.web_form.after_load = () => {
    frappe.msgprint('Заполните данные внимательно');
};
```

Это подходит для client-side инициализации.

---

## 70. Custom validation

Перед сохранением вызывается:

```javascript
frappe.web_form.validate
```

Можно вернуть:

```text
false
```

и остановить client-side submit.

Например:

```javascript
frappe.web_form.validate = () => {
    const values = frappe.web_form.get_values();

    if (values.priority === 'High' && !values.description) {
        frappe.msgprint('Для высокого приоритета укажите описание');
        return false;
    }
};
```

---

## 71. Client validation — это UX, а не защита

Пользователь контролирует browser.

Он может:

```text
отключить JavaScript
изменить request
вызвать endpoint напрямую
```

Поэтому правило:

```text
приятная подсказка / мгновенная проверка
→ Web Form Client Script

обязательное бизнес-правило
→ server-side validation
```

Это тот же архитектурный принцип, который дальше будет особенно важен в главах Client Script и Server Script.

---

# Часть XV. Standard Web Form

## 72. `Is Standard`

В developer mode у Web Form появляется:

```text
Is Standard
```

Если сделать Web Form standard, она экспортируется в module собственного App.

Framework создаёт файлы Web Form, включая:

```text
.py
.js
```

которые можно хранить в Git вместе с App.

То есть:

```text
site-specific Web Form
→ запись в базе Site

Standard Web Form
→ часть приложения
```

Подробно standard/custom модель разберём отдельно в главе 46.

---

## 73. Python `get_context()` Standard Web Form

Для standard form создаётся Python module с функцией вида:

```python
def get_context(context):
    pass
```

Через неё можно дополнять rendering context серверными данными.

Это уже шаг от чистой настройки к application code.

---

## 74. JS/CSS через App hooks

Для Standard Web Forms Framework поддерживает hooks:

```python
webform_include_js = {
    "ToDo": "public/js/custom_todo.js"
}

webform_include_css = {
    "ToDo": "public/css/custom_todo.css"
}
```

Для Web Form, созданной пользователем, обычный путь проще:

```text
Client script
Custom CSS
```

прямо в самой Web Form.

---

# Часть XVI. Взаимодействие с DocType logic

## 75. Web Form не отменяет controller

Если целевой DocType имеет Python controller:

```python
class Request(Document):
    def validate(self):
        ...
```

Web Form работает с тем же Document.

Поэтому controller остаётся главным местом для правил, которые должны соблюдаться независимо от интерфейса.

Схема:

```text
Desk
REST API
Web Form
Data Import
custom code
     ↓
тот же Document lifecycle
```

Именно поэтому хорошие server-side rules дают согласованную систему.

---

## 76. Web Form и Workflow

Web Form может создавать Document, на котором настроен Workflow.

Но сама Web Form не превращается автоматически в полный Desk Workflow UI с набором workflow actions пользователя.

Нужно различать:

```text
у Document есть workflow_state
```

и:

```text
Web Form предоставляет полноценный интерфейс всех workflow transitions
```

Второе автоматически не следует из первого.

Если внешний пользователь должен выполнять сложный процесс:

```text
Approve
Reject
Return
Escalate
Reassign
```

это уже может потребовать portal page или собственного frontend flow.

---

## 77. Web Form и Submittable DocType

Как уже отмечено:

```text
кнопка Submit Web Form
!=
Document.submit()
```

Поэтому Web Form хорошо подходит для intake Draft, а перевод в настоящий `docstatus = 1` должен быть осознанной частью business flow.

Не строй финансовое или юридически значимое подтверждение на предположении, что надпись кнопки `Submit` автоматически выполняет Frappe Submit.

---

## 78. Child Table

Web Form v16 поддерживает поле:

```text
Table
```

и может показывать child rows.

Например:

```text
Request
└── items
    ├── item
    ├── qty
    └── comment
```

Это полезно для:

```text
позиции заявки
список оборудования
участники
строки заказа
```

Для child table Framework получает её field metadata и рендерит grid-подобный web control.

---

# Часть XVII. Anonymous responses

## 79. `Anonymous responses`

Настройка:

```text
Anonymous responses
```

нужна, когда ответы не должны сохраняться как response конкретного logged-in пользователя.

В текущей реализации при сохранении Framework временно выполняет submit под Guest context.

Практический смысл:

```text
опрос
анонимная обратная связь
голосование без ownership пользователя
```

---

## 80. Anonymous — не обещание абсолютной анонимности инфраструктуры

Нужно различать:

```text
Document ownership / Web Form identity
```

и:

```text
web server logs
reverse proxy logs
security tooling
network metadata
```

Флаг Web Form управляет поведением ответа внутри Frappe, но не является универсальной системой privacy/anonymization всей инфраструктуры.

---

# Часть XVIII. Что Web Form умеет штатно

## 81. Карта возможностей

Без собственного frontend Web Form уже даёт:

```text
public form
login-required form
private key form
single response
multiple responses
list responses
view response
edit response
delete response
print
comments
attachments
child table
multi-step form
conditional fields
custom labels/defaults/placeholders
client-side scripting
custom CSS
success message / redirect
sidebar
meta information
standard-app export
```

Это существенно больше, чем просто HTML `<form>`.

---

# Часть XIX. Где Web Form заканчивается

## 82. Web Form хороша, когда центр интерфейса — один DocType

Прекрасный сценарий:

```text
создать одну заявку
```

или:

```text
показать список моих заявок
→ открыть одну
→ изменить её
```

То есть основной объект понятен:

```text
одна Web Form
→ один target DocType
```

---

## 83. Web Form уже начинает мешать, когда вы строите приложение

Признаки:

```text
10 взаимосвязанных DocTypes на одном экране
сложная навигация
sidebar меняется динамически
несколько dashboard widgets
массовые операции
advanced search
real-time board
drag-and-drop workflow
сложный wizard с ветвлением
client-side state между многими страницами
rich interactive tables
собственная design system
```

В этот момент Web Form перестаёт быть естественным центром архитектуры.

---

## 84. Web Form против Portal / Website Page

Удобная граница:

```text
нужно просто дать форму одного DocType
→ Web Form

нужно собрать собственную страницу из нескольких источников
→ Portal / Website Page
```

Например:

```text
"Отправить заявку"
→ Web Form

"Личный кабинет"
  ├── профиль
  ├── баланс
  ├── мои заявки
  ├── документы
  ├── уведомления
  └── статистика
→ уже Portal / Website pages
```

Web Form может быть частью такого portal, но не обязана быть всем portal целиком.

---

## 85. Web Form против собственного frontend

Если frontend должен быть самостоятельным приложением:

```text
Vue / React / Svelte / mobile app
```

обычно граница выглядит так:

```text
Frappe
→ backend / DocTypes / permissions / API

custom frontend
→ весь UX
```

Тогда Web Form может вообще не использоваться.

Вместо неё frontend работает через:

```text
REST API
RPC / whitelisted methods
```

которые разберём в следующих главах.

---

## 86. Web Form против Desk

Ещё одна полезная граница:

```text
внутренний сотрудник ежедневно обрабатывает сотни документов
→ Desk

внешний / Website User должен выполнить ограниченное действие
→ Web Form / Portal
```

Не нужно вытаскивать весь Desk наружу только потому, что внешнему пользователю нужен один Document.

И наоборот, не нужно заставлять оператора работать через урезанную Web Form, если ему нужен полноценный Desk.

---

# Часть XX. Типичные ошибки

## 87. Ошибка: выдать Guest Create на DocType «потому что форма публичная»

Не делай это автоматически.

Public Web Form уже имеет собственный controlled insert flow.

Сначала проверь, действительно ли Guest нужен прямой доступ к DocType вне Web Form.

Чаще всего ответ:

```text
нет
```

---

## 88. Ошибка: оставить в Web Form внутренние поля

Например:

```text
approved
internal_status
manager_comment
cost_price
security_level
```

Если поле не должен менять внешний пользователь, не нужно добавлять его в Web Form только потому, что оно существует в DocType.

---

## 89. Ошибка: хранить security rule только в Client Script

Плохо:

```javascript
if (amount > 100000) {
    return false;
}
```

и больше нигде.

Правильно:

```text
Client Script
→ удобная ранняя проверка

Server validation
→ обязательное правило
```

---

## 90. Ошибка: считать Hidden field секретным

Поле, которое отправлено в browser, нельзя считать секретным только потому, что UI его не показывает.

Для private request-specific internal values в v16 существует отдельный механизм:

```text
Web Form Request
→ Doc Values
```

---

## 91. Ошибка: пытаться построить полноценный SPA из одной Web Form

Если для каждой новой функции приходится:

```text
вставлять огромный Client Script
перерисовывать весь DOM
подключать десятки API calls
создавать кастомную навигацию
эмулировать routing
```

скорее всего Web Form уже выбрана не на своём уровне.

---

## 92. Ошибка: дублировать DocType validation в Web Form

Плохо:

```text
Desk validation
Web Form validation
API validation
Import validation
```

четырьмя разными реализациями одного правила.

Надёжнее:

```text
server-side Document rule
→ единый источник истины

interface scripts
→ только UX
```

---

# Часть XXI. Практика руками

## 93. Создаём учебный `Request`

Если у тебя уже есть тестовый DocType `Request` из предыдущих глав — используй его.

Для минимального упражнения достаточно полей:

```text
subject      Data       Required
email        Data
priority     Select
             Low
             Medium
             High

description  Text
status       Select
             Open
             Closed
```

Для `status` поставь default:

```text
Open
```

---

## 94. Создаём Web Form

Создай:

```text
Title          = Request Form
Route          = request
Select DocType = Request
```

Добавь в Web Form:

```text
subject
email
priority
description
```

Не добавляй:

```text
status
```

Пусть он заполняется моделью/default, а не внешним пользователем.

---

## 95. Делаем форму Public

Оставь:

```text
Login required = off
Key required   = off
```

Опубликуй Web Form.

Открой в Incognito:

```text
/request/new
```

Заполни:

```text
Subject     = Test public request
Email       = test@example.com
Priority    = High
Description = Public Web Form test
```

Отправь.

---

## 96. Проверяем Document в Desk

Вернись в Desk:

```text
Request List
```

Найди созданный Document.

Проверь:

```text
subject
email
priority
description
status
owner
creation
```

Главная цель упражнения:

> увидеть, что Web Form создаёт реальный Document того же DocType.

---

## 97. Проверяем, что лишнее поле нельзя записать обычной формой

Убедись, что `status` отсутствует в Web Form.

Пользователь не должен получать стандартный UI для его изменения.

Это демонстрирует модель:

```text
DocType fields
≠
Web Form fields
```

---

## 98. Включаем Login Required

Теперь включи:

```text
Login required
```

Открой форму в Incognito.

Guest больше не должен иметь обычный публичный flow отправки.

Войди тестовым Website User и отправь response.

Проверь ownership созданного Document.

---

## 99. Включаем Multiple + List

Включи:

```text
Allow multiple responses
Show List
Allow editing after submit
```

Создай две заявки одним пользователем.

Открой:

```text
/request/list
```

Проверь:

```text
видны обе записи
можно открыть response
можно перейти в edit mode
```

---

## 100. Добавляем простой Client Script

В Web Form добавь:

```javascript
frappe.web_form.on('priority', (field, value) => {
    if (value === 'High') {
        frappe.msgprint('Опишите причину высокого приоритета подробнее');
    }
});
```

Сохрани и обнови страницу.

Поменяй priority на:

```text
High
```

Проверь, что message появляется в browser.

---

## 101. Добавляем client validation

Добавь:

```javascript
frappe.web_form.validate = () => {
    const values = frappe.web_form.get_values();

    if (values.priority === 'High' && !values.description) {
        frappe.msgprint('Для High обязательно описание');
        return false;
    }
};
```

Проверь UX.

После этого зафиксируй главное:

> это всё ещё не замена server-side validation, если правило действительно бизнес-критично.

---

# Часть XXII. Как выбирать решение

## 102. Decision table

| Задача | Инструмент |
|---|---|
| Публично создать один тип Document | Web Form |
| Форма только после login | Web Form + Login Required |
| Персональная форма без account | Web Form + Web Form Request |
| Несколько responses пользователя | Web Form + Allow Multiple |
| Простой список «мои документы» | Web Form + Show List |
| Пользователь должен исправлять свой response | Web Form + Allow Edit |
| Несколько связанных страниц личного кабинета | Website / Portal |
| Полностью свой UX | Custom frontend |
| Внешняя система передаёт данные программно | REST API / RPC |
| Внутренний оператор работает с полной моделью | Desk |

---

## 103. Короткая архитектурная шкала

```text
нужна одна внешняя форма
→ Web Form

нужны несколько связанных web pages
→ Website / Portal

нужен собственный application UX
→ custom frontend

нужен machine-to-machine доступ
→ REST API / RPC
```

Это и есть главная граница этой главы.

---

# Что нужно запомнить

1. `Web Form` — штатный web-интерфейс поверх выбранного DocType.
2. Она создаёт обычные Frappe Documents, а не отдельные «ответы формы» вне модели.
3. Web Form может показывать только выбранный subset полей DocType.
4. Public Web Form может создавать Documents без выдачи Guest обычного `Create` permission на DocType.
5. `ignore_permissions` при Web Form insert не отменяет Document lifecycle и server-side validation.
6. Кнопка `Submit` Web Form не равна `Document.submit()` для Submittable DocType.
7. `Login Required` превращает форму в authenticated flow.
8. `Key Required + Web Form Request` даёт private-link flow, в том числе без user account.
9. `Allow Multiple`, `Show List`, `Allow Edit`, `Allow Delete`, comments, attachments и print позволяют собрать простой portal-like UX без отдельного frontend.
10. `Apply document permissions` переключает доступ к существующим Documents на стандартную permission model.
11. Client Script Web Form работает через `frappe.web_form`, а не Desk `frappe.ui.form.on`.
12. Client-side validation нужна для UX; обязательные правила должны проверяться сервером.
13. Web Form хороша, пока основная задача — один DocType и относительно стандартный create/view/edit flow.
14. Когда нужен полноценный кабинет, сложная навигация или собственный UX, переходят к Portal / Website pages или custom frontend.

---

# Источники

Официальная документация Frappe Framework v16 / current docs:

- [Web Form](https://docs.frappe.io/framework/user/en/web-form)
- [Web Form Settings](https://docs.frappe.io/framework/user/en/web-form/settings)
- [Web Form Customization](https://docs.frappe.io/framework/user/en/web-form/customization)
- [Web Form Request](https://docs.frappe.io/framework/portal-web-form/web-form-request)
- [Portal Pages](https://docs.frappe.io/framework/user/en/portal-pages)
- [Request Lifecycle / Routing and Rendering](https://docs.frappe.io/framework/user/en/python-api/routing-and-rendering)
- [Hooks — Web Form assets](https://docs.frappe.io/framework/user/en/python-api/hooks)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)

Для деталей поведения v16 дополнительно сверено с исходным кодом ветки `version-16`:

- [`frappe/website/doctype/web_form/web_form.py`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/web_form/web_form.py)
- [`frappe/website/doctype/web_form/web_form.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/web_form/web_form.json)
- [`frappe/website/doctype/web_form_field/web_form_field.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/web_form_field/web_form_field.json)

---

Следующая глава: **40. Website / portal-возможности Framework**.
