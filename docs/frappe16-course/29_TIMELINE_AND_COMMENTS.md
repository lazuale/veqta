# 29. Timeline и Comments

Внизу обычной Form View во Frappe есть **Timeline**.

Новичок легко принимает его за «список комментариев».

Но Timeline устроен гораздо шире.

Он показывает историю активности вокруг документа:

```text
создание документа
изменения
комментарии
email и другие Communication
назначения
вложения
Workflow
Sharing
просмотры
и другие события
```

Главное, что нужно понять сразу:

> **Timeline — это экран, который собирает события из нескольких разных источников. Это не одна таблица в базе.**

Проверено: **2026-08-31**.

---

## 1. Самый простой пример

Есть документ:

```text
Request REQ-0001
```

С ним произошло несколько действий:

```text
09:00  Анна создала Request
09:10  Анна написала комментарий
09:20  Борису назначили Request
10:00  изменили Priority
10:30  прикрепили файл
11:00  отправили email
```

Пользователь может увидеть всё это в одном Timeline.

Визуально выглядит так, будто перед нами одна история.

Но физически данные могут лежать в разных местах:

```text
Request
Comment
ToDo
Version
File
Communication
...
```

Timeline просто собирает их вместе и сортирует по времени.

---

# Что такое Timeline

## 2. Timeline находится внизу Form View

Официальная документация Desk описывает Form Timeline как историю:

```text
emails
comments
edits
other events
```

То есть это встроенная часть стандартной Form View.

Для обычного внутреннего DocType не нужно самостоятельно создавать отдельный журнал событий только ради того, чтобы пользователь видел историю работы с документом.

---

## 3. Timeline не является бизнес-данными документа

Допустим, у `Request` есть поля:

```text
subject
priority
status
```

Timeline не превращается в ещё одно поле:

```text
timeline
```

и обычно не хранится внутри `Request` как Child Table.

Правильнее представить так:

```text
Request
   │
   ├── собственные поля
   │
   └── связанные системные события
            ↓
         Timeline
```

То есть Timeline — **представление истории**, а не часть прикладной схемы DocType.

---

## 4. Из чего v16 собирает Timeline

В текущем Frappe v16 Form Timeline собирает, среди прочего:

| Что видно | Основной источник |
|---|---|
| кто создал документ | системные `owner` и `creation` |
| кто последний раз менял | `modified_by` и `modified` |
| обычный комментарий | `Comment` |
| email / звонок / встреча | `Communication` |
| автоматическое сообщение | `Communication` типа `Automated Message` |
| изменение полей | `Version`, если включён Track Changes |
| просмотр документа | `View Log`, если включён Track Views |
| назначение | служебный `Comment` + сам Assignment хранится через `ToDo` |
| добавление/удаление вложения | служебный `Comment`; сам файл хранится в `File` |
| Share / Unshare | служебный `Comment`; текущее состояние доступа хранится отдельно |
| Workflow-событие | служебный `Comment` |
| Like | служебный `Comment` |
| Milestone | `Milestone` |
| пользовательский элемент Timeline | hook `additional_timeline_content` |

Это одна из самых полезных карт всей главы.

---

# Comment

## 5. Обычный комментарий — отдельный Document

Когда пользователь внизу формы пишет:

```text
Проверил данные, можно продолжать.
```

Frappe создаёт отдельный документ DocType:

```text
Comment
```

У него есть ссылка обратно на исходный документ:

```text
reference_doctype = Request
reference_name    = REQ-0001
```

Поэтому комментарий не нужно хранить в поле `Request.comment` или в собственной Child Table.

---

## 6. У Comment есть собственные поля

Среди основных полей текущего v16:

```text
comment_type
comment_email
comment_by
published
reference_doctype
reference_name
content
```

То есть Comment сам является нормальным Frappe Document.

Условно:

```text
Comment
├── comment_type = Comment
├── reference_doctype = Request
├── reference_name = REQ-0001
├── comment_email = anna@example.com
└── content = Проверил данные
```

---

## 7. `comment_type` важнее, чем кажется

DocType `Comment` используется не только для обычного текста пользователя.

В v16 список типов включает, например:

```text
Comment
Like
Info
Label
Workflow
Assigned
Assignment Completed
Attachment
Attachment Removed
Shared
Unshared
Edit
```

и ещё несколько системных типов.

Поэтому слово `Comment` во Frappe может означать две разные вещи:

```text
Comment
→ системный DocType

comment_type = Comment
→ именно обычный человеческий комментарий
```

Это полезно не путать.

---

## 8. Assignment в Timeline не означает, что Assignment хранится в Comment

В главе 23 мы уже разобрали:

```text
Assignment
→ ToDo
```

Когда пользователь назначает документ Борису, Frappe может дополнительно создать служебную Timeline-запись типа:

```text
comment_type = Assigned
```

Но это **журнал события**, а не сама модель назначения.

Правильная картина:

```text
ToDo
→ текущее назначение

Comment(type=Assigned)
→ запись о том, что назначение произошло
```

Нельзя восстанавливать текущего исполнителя только по тексту Timeline.

---

## 9. То же самое относится к вложениям

Пользователь прикрепил:

```text
report.pdf
```

Сам файл представлен DocType:

```text
File
```

А Timeline может получить служебную запись:

```text
Comment
comment_type = Attachment
content = report.pdf
```

При удалении:

```text
comment_type = Attachment Removed
```

Следовательно:

```text
File
→ текущее вложение

Comment
→ история действия
```

---

## 10. Sharing работает по той же логике

Текущее правило доступа не хранится в тексте Timeline.

Timeline лишь может показать событие:

```text
Shared
Unshared
```

через соответствующие Comment-записи.

Сам механизм Sharing мы разбирали в главе 21.

---

# Как создаётся обычный комментарий

## 11. Comment box встроен в Form Footer

Внизу сохранённого документа Frappe создаёт стандартное поле ввода комментария.

При отправке Desk вызывает серверный метод добавления комментария, передавая примерно:

```text
reference_doctype
reference_name
content
comment_email
comment_by
```

После этого новый Comment появляется в Timeline.

Для нового, ещё не сохранённого документа footer скрыт: сначала Document должен получить собственное `name`.

---

## 12. Комментарии поддерживают mentions

В стандартном поле комментария включены mentions.

Например пользователь пишет:

```text
@boris@example.com проверь этот документ
```

После вставки Comment его controller вызывает механизм уведомления упомянутых пользователей.

То есть для простого общения вокруг документа не нужно сначала писать собственную систему `@mentions`.

---

## 13. HTML комментария очищается на сервере

Comment хранит форматированный content, но перед сохранением Frappe выполняет sanitization HTML.

Например опасные элементы вроде:

```html
<form>
<input>
<button>
```

явно запрещены текущим controller Comment.

Это ещё одна причина пользоваться штатным Comment вместо собственного поля с сырым HTML без необходимости.

---

# Где хранится Comment

## 14. Источник истины — документ `Comment`

Важно не перепутать его со служебным полем:

```text
_comments
```

В обычном родительском Document Frappe может поддерживать `_comments` как JSON-кэш последних комментариев.

Но это не означает, что комментарии перестали быть отдельными Documents.

Правильная модель:

```text
Comment documents
→ источник комментариев

parent._comments
→ вспомогательный кэш/краткая информация
```

В текущем v16 в `_comments` сохраняется максимум последние 100 элементов.

Поэтому строить собственную аналитику комментариев по `_comments` не следует.

---

# Communication

## 15. Email в Timeline — не Comment

Если из формы отправили email, в Timeline появляется карточка сообщения.

Но она основана уже на другом DocType:

```text
Communication
```

Например:

```text
Communication
├── communication_medium = Email
├── sender
├── recipients
├── subject
├── content
├── reference_doctype = Request
└── reference_name = REQ-0001
```

То есть:

```text
Comment
→ обсуждение внутри документа

Communication
→ коммуникация: email, phone, meeting и т.п.
```

Подробно `Communication` будет разобран в главе 32.

---

## 16. В Timeline поддерживаются разные Communication medium

Текущий frontend v16 различает, например:

```text
Email
Phone
Meeting
Other
```

и показывает для них разные иконки.

Также отдельно обрабатываются:

```text
communication_type = Automated Message
```

То есть автоматическое письмо Notification тоже может оставить нормальный Communication trail.

---

## 17. Communications загружаются порциями

Timeline долгоживущего документа может содержать сотни писем.

Поэтому Frappe не обязан сразу загружать их все.

В v16 начальная загрузка берёт ограниченную порцию Communications, а интерфейс при необходимости показывает:

```text
Load More Communications
```

Это полезная деталь: Timeline — не попытка выгрузить всю историю системы одним огромным запросом.

---

# Version и изменения документа

## 18. Изменение поля может появиться в Timeline через Version

Допустим:

```text
Priority: Medium → High
```

Если у DocType включён:

```text
Track Changes
```

Frappe создаёт записи `Version`.

Timeline умеет преобразовывать их в понятные человеку строки об изменениях.

Но сам `Version` — отдельный DocType, а не Comment.

Эту механику подробно разберём в следующей главе.

---

## 19. Без Track Changes полной истории значений не будет

Timeline сам по себе не превращает любой Save в детальный audit diff.

В текущем backend v16:

```text
if not doc.meta.track_changes:
    versions = []
```

То есть для истории изменений полей нужен именно `Track Changes`.

Начальная загрузка Timeline сейчас берёт последние 10 Version-записей.

---

# View Log

## 20. Просмотры тоже могут появляться в Timeline

Если у DocType включён:

```text
Track Views
```

при открытии документа Framework может создавать `View Log`.

После этого Timeline умеет показывать:

```text
Boris viewed this
```

Если Track Views выключен, эта история не собирается.

Поэтому обычный Timeline не означает автоматического полного аудита каждого просмотра всех документов.

---

# Creation и Modified

## 21. «Создал документ» не обязательно является Comment

В Timeline всегда полезно видеть начало истории:

```text
Anna created this
```

Но frontend может сформировать эту строку напрямую из системных полей документа:

```text
owner
creation
```

А строку:

```text
Boris last edited this
```

из:

```text
modified_by
modified
```

Поэтому снова:

> визуальная строка Timeline не обязана иметь отдельную строку в `tabComment`.

---

# Workflow, Share, Like и другие события

## 22. Многие служебные события действительно используют Comment

Backend `get_docinfo()` получает все связанные Comment-записи и раскладывает их по группам.

Например:

```text
Comment
→ обычные комментарии

Shared / Unshared
→ share logs

Assigned / Assignment Completed
→ assignment logs

Attachment / Attachment Removed
→ attachment logs

Info / Edit / Label
→ info logs

Like
→ like logs

Workflow
→ workflow logs
```

Frontend затем отображает каждую группу по-своему.

Именно поэтому один системный DocType `Comment` используется как лёгкий журнал нескольких типов событий.

---

## 23. Но не все значения `comment_type` обязательно рисуются одинаково

В metadata Comment список типов довольно большой.

Однако текущий `get_docinfo()` специально распределяет только нужные ему группы.

Поэтому не стоит рассуждать так:

```text
я создам любой Comment с любым comment_type
→ Frappe обязательно красиво покажет его в Timeline
```

Если нужен собственный тип события приложения, для этого есть более явный механизм `additional_timeline_content`.

---

# Milestone

## 24. Milestone — ещё один отдельный источник Timeline

В актуальном v16 Timeline умеет показывать `Milestone`.

Условно:

```text
Anna changed Stage to Done
```

При этом backend загружает отдельные записи DocType:

```text
Milestone
```

с полями вроде:

```text
reference_type
reference_name
track_field
value
```

То есть даже внутри одного Timeline Framework может использовать специализированные источники событий.

---

# Show all activity

## 25. Timeline можно визуально упростить

Когда у документа есть Comments или Communications, текущий v16 показывает переключатель:

```text
Show all activity
```

При сокращённом режиме основной акцент остаётся на общении, а часть технической активности скрывается.

При полном режиме добавляются, например:

```text
views
versions
sharing
workflow
likes
assignments
attachments
milestones
custom timeline content
```

Это только фильтрация отображения.

Сами события из базы от этого не удаляются.

---

# Действия прямо из Timeline

## 26. Timeline — не только чтение истории

В стандартном Form Timeline могут появляться действия.

Например:

```text
New Email
New Event
Reply
Reply All
Edit Comment
Delete Comment
Publish / Unpublish Comment
```

Набор зависит от permissions и настроек DocType.

То есть Timeline одновременно является:

```text
историей
+
точкой взаимодействия
```

---

## 27. Обычный Comment можно редактировать

В текущем Desk v16 кнопка Edit показывается:

```text
Administrator
или
owner самого Comment
```

То есть автор может исправить собственный комментарий через стандартный интерфейс.

Удаление дополнительно зависит от permission `Delete` для DocType `Comment`.

UI разрешает соответствующее действие владельцу комментария или System Manager при выполнении permission-проверки.

---

## 28. Comment можно Publish / Unpublish

У `Comment` есть поле:

```text
published
```

Штатный Timeline позволяет авторизованному пользователю переключать публикацию комментария.

Интерфейс прямо предупреждает, что опубликованный Comment может стать видимым website/portal users.

Поэтому:

```text
внутренний Comment
```

и

```text
публичный Comment
```

не всегда одно и то же с точки зрения доступа.

---

# Comments и realtime

## 29. Новый комментарий может появиться без полной перезагрузки формы

Comment controller v16 для нескольких типов событий публикует realtime-событие:

```text
docinfo_update
```

Например для:

```text
Comment
Like
Assigned
Assignment Completed
Attachment
Attachment Removed
```

Это позволяет уже открытой Form View обновлять часть docinfo без необходимости вручную строить собственный WebSocket-механизм для базовых сценариев.

Realtime подробно будет разобран позже, в главе 55.

---

# Программное добавление Comment

## 30. У Document есть штатный `add_comment()`

На сервере можно добавить Timeline-комментарий через Document API:

```python
request = frappe.get_doc("Request", "REQ-0001")
request.add_comment("Comment", text="Проверено автоматически")
```

Официальная документация Document API прямо указывает, что такой Comment появится в Form Timeline.

Можно создавать и служебные типы:

```python
request.add_comment("Edit", "Значения изменены")
```

Но не стоит использовать произвольные служебные comment types как замену собственной модели данных.

---

# Custom Timeline content

## 31. App может добавить собственное событие без создания Comment

Если стандартных источников недостаточно, Frappe предоставляет hook:

```python
additional_timeline_content = {
    "Request": "training_app.timeline.get_request_timeline"
}
```

Серверный метод может вернуть дополнительные элементы для Timeline.

Это полезно, например, если внешний сервис хранит собственные события:

```text
External check completed
```

и их нужно показать рядом с обычной историей Frappe.

---

## 32. Custom Timeline content не нужно использовать для обычных комментариев

Плохая идея:

```text
нужны комментарии пользователей
→ пишем additional_timeline_content
```

Для этого уже есть стандартный `Comment`.

Hook нужен, когда событие действительно приходит из другого источника или имеет нестандартную природу.

---

# Timeline не заменяет бизнес-журнал

## 33. Audit trail и бизнес-сущность — разные задачи

Представим, что нужно хранить официальный результат проверки:

```text
дата проверки
проверяющий
результат
значение до
значение после
основание
подпись
```

Не следует автоматически решать:

```text
будем писать всё текстом в Comment
```

Если данные нужно:

```text
фильтровать
проверять
агрегировать
использовать в отчётах
связывать с другими Documents
```

они заслуживают нормальных структурированных полей или отдельного DocType.

Timeline подходит для истории взаимодействия, но не заменяет корректную модель данных.

---

## 34. Comment — тоже не универсальная задача

Плохая модель:

```text
Comment:
"Проверь документ завтра"
```

если на самом деле требуется:

```text
назначить Борису
срок 02.09
отслеживать Open/Closed
```

Для этого есть:

```text
Assignment / ToDo
```

А Comment может лишь дополнять назначение человеческим контекстом.

---

# Карта выбора

## 35. Что использовать для какой задачи

| Нужно | Штатный механизм |
|---|---|
| оставить заметку человеку | Comment |
| назначить работу | Assignment / ToDo |
| отправить/получить email | Communication |
| видеть изменение полей | Version + Track Changes |
| хранить файл | File |
| выдать доступ | Sharing / DocShare |
| управлять согласованием | Workflow |
| показать историю этих действий | Timeline |
| добавить нестандартное внешнее событие в Timeline | `additional_timeline_content` |

Эта таблица убирает большую часть архитектурной путаницы.

---

# Что происходит при открытии Form

## 36. Упрощённая техническая картина

При загрузке существующего Document Framework получает сам документ и дополнительную информацию `docinfo`.

Упрощённо:

```text
GET Form
   ↓
Document
+
docinfo
   ├── comments
   ├── communications
   ├── automated_messages
   ├── versions
   ├── views
   ├── assignments
   ├── attachment logs
   ├── workflow logs
   ├── share logs
   ├── milestones
   └── additional timeline content
        ↓
FormTimeline
        ↓
единая лента Activity
```

Frontend не обязан знать одну универсальную таблицу событий — он получает несколько наборов и объединяет их по времени.

---

## 37. Timeline сортирует события как одну историю

В результате пользователь видит последовательность вроде:

```text
11:20  Boris attached report.pdf
11:10  Anna changed Priority from Medium to High
10:55  Boris commented: Проверено
10:30  Request assigned to Boris
09:00  Anna created this
```

Хотя каждая строка могла прийти из своего механизма.

Именно это делает Timeline удобным: пользователю не нужно открывать пять технических списков.

---

# Типичные ошибки

## 38. Ошибка: сделать собственный Child Table `Comments`

Если нужен обычный разговор вокруг документа, это дублирует штатный `Comment`.

Ты потеряешь или придётся повторно реализовывать:

```text
mentions
Timeline UI
realtime updates
publish/unpublish
permissions
стандартные APIs
```

Сначала используй Comment.

---

## 39. Ошибка: считать Timeline полноценным неизменяемым аудитом

Timeline полезен как activity trail.

Но некоторые его элементы можно редактировать или удалять при наличии прав.

Например обычный Comment может быть изменён автором.

Если нормативное требование звучит:

> запись должна быть юридически неизменяемой и храниться N лет

нельзя просто сказать:

```text
у нас же есть Timeline
```

Это уже отдельное требование к аудиту, permissions, retention и модели хранения.

---

## 40. Ошибка: читать текущую систему по историческим сообщениям

Например Timeline говорит:

```text
Assigned to Boris
```

Это не гарантирует, что Борис назначен сейчас.

Позже его могли снять с Assignment.

Для текущего состояния смотри текущие данные:

```text
ToDo
DocShare
File
workflow_state
```

а Timeline используй как историю.

---

## 41. Ошибка: превращать Comment в структурированную базу данных

Не стоит писать:

```text
"Сумма: 125000; категория: A; участок: 3"
```

и потом парсить эту строку в отчётах.

Если значение нужно системе — оно должно быть полем или отдельным Document.

Comment предназначен прежде всего для человеческого контекста.

---

# Мини-практика

## 42. Подготовь тестовый Request

Возьми существующий `Request` или другой учебный DocType.

Создай один документ:

```text
REQ-0001
```

и сохрани его.

---

## 43. Добавь обычный Comment

Внизу Form напиши:

```text
Первый тестовый комментарий
```

Отправь его.

Проверь:

```text
Timeline
→ появилась карточка комментария
```

Если есть доступ к списку Comment, найди созданную запись и посмотри:

```text
reference_doctype
reference_name
comment_type
content
```

---

## 44. Сделай Assignment

Назначь документ другому пользователю.

Теперь сравни:

```text
ToDo
```

и

```text
Timeline
```

Нужно увидеть разницу:

```text
ToDo
→ текущее назначение

Timeline entry
→ история факта назначения
```

---

## 45. Прикрепи файл

Добавь небольшой файл.

Проверь одновременно:

```text
Attachments
→ сам File

Timeline
→ событие Attachment
```

После этого удали файл и посмотри событие `Attachment Removed`.

---

## 46. Включи Track Changes

Для учебного DocType включи:

```text
Track Changes
```

Измени одно простое поле, например:

```text
Priority: Medium → High
```

Сохрани документ.

Посмотри, как изменение появляется в Timeline уже не как обычный человеческий Comment.

---

## 47. Сравни обычный и полный Timeline

Если появился переключатель:

```text
Show all activity
```

выключи и включи его.

Посмотри, какие технические события исчезают и возвращаются.

Это хорошо закрепляет мысль:

> Timeline — собранное представление разных типов activity.

---

# Что запомнить

1. **Timeline — это представление истории, а не одна таблица.**
2. **Обычный комментарий хранится отдельным Document `Comment`.**
3. **`Comment` DocType используется также для нескольких типов служебных событий.**
4. **Assignment хранится через ToDo, File — через File, email — через Communication, даже если всё это видно в одном Timeline.**
5. **Изменения полей появляются через Version только при Track Changes.**
6. **Просмотры требуют Track Views.**
7. **`_comments` у родительского документа — вспомогательный кэш, а не замена DocType Comment.**
8. **Для нестандартных событий App может использовать `additional_timeline_content`.**
9. **Timeline не заменяет структурированную бизнес-модель и не следует считать его неизменяемым нормативным аудитом без отдельной проверки требований.**

---

## Источники

- [Frappe Framework — Desk](https://docs.frappe.io/framework/user/en/desk)
- [Frappe Framework — Document API: `doc.add_comment`](https://docs.frappe.io/framework/user/en/api/document)
- [Frappe Framework — Hooks: Form Timeline](https://docs.frappe.io/framework/user/en/python-api/hooks)
- [`version-16`: `frappe/public/js/frappe/form/footer/form_timeline.js`](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/footer/form_timeline.js)
- [`version-16`: `frappe/public/js/frappe/form/footer/footer.js`](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/footer/footer.js)
- [`version-16`: `frappe/desk/form/load.py`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/load.py)
- [`version-16`: `frappe/core/doctype/comment/comment.json`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/comment/comment.json)
- [`version-16`: `frappe/core/doctype/comment/comment.py`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/comment/comment.py)

---

Предыдущая глава: **28. Auto Repeat**  
Следующая глава: **30. Version и Track Changes**
