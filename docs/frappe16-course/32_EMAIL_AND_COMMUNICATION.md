# 32. Email / Communication

В прошлых главах мы уже несколько раз встречали письма в Timeline, Notification и Email permission.

Теперь соберём эту механику в одну картину.

Главная мысль простая:

> **во Frappe письмо обычно представлено отдельным Document типа `Communication`.**

Сам `Communication` не равен SMTP-сообщению и не равен строке в Timeline. Это системная запись, которая хранит содержание общения и может быть связана с другим Document.

Проверено: **2026-08-31**.

---

## 1. Самый простой пример

Есть документ:

```text
Request REQ-0001
Subject: Replace printer
```

Пользователь открывает его и отправляет письмо:

```text
To: user@example.com
Subject: Re: Replace printer
Message: Please confirm the model.
```

В упрощённом виде Frappe делает так:

```text
Request REQ-0001
        ↑
        │ reference_doctype = Request
        │ reference_name    = REQ-0001
        │
Communication
├── communication_medium = Email
├── sent_or_received      = Sent
├── sender
├── recipients
├── cc
├── bcc
├── subject
├── content
└── message_id
        ↓
Email Queue / отправка
        ↓
SMTP или другой email backend
```

То есть бизнес-документ и само письмо остаются разными Documents.

---

## 2. `Communication` шире, чем email

Название может ввести в заблуждение.

`Communication` — не DocType исключительно для электронной почты.

В текущем v16 поле `communication_medium` поддерживает:

```text
Email
Chat
Phone
SMS
Event
Meeting
Visit
Other
```

Поэтому правильная модель такая:

```text
Communication
→ запись внешнего или пользовательского общения

Email
→ один из возможных communication_medium
```

Но в этой главе нас в основном интересует именно `communication_medium = Email`.

---

## 3. Основные поля Communication

Для начала достаточно понимать следующие поля:

| Поле | Смысл |
|---|---|
| `subject` | тема |
| `content` | HTML-содержимое сообщения |
| `text_content` | текстовое представление, когда оно есть |
| `sender` | отправитель |
| `recipients` | To |
| `cc` | CC |
| `bcc` | BCC |
| `communication_medium` | Email, Phone и т. д. |
| `sent_or_received` | Sent или Received |
| `communication_date` | дата общения |
| `reference_doctype` | тип связанного документа |
| `reference_name` | конкретный связанный документ |
| `in_reply_to` | предыдущий Communication в цепочке ответа |
| `email_account` | Email Account, через который письмо связано с почтой |
| `message_id` | технический Message-ID email |
| `delivery_status` | состояние отправки |

Для входящей почты дополнительно используются служебные поля вроде `uid`, `imap_folder`, `email_status`, `seen` и `has_attachment`.

Заучивать их сейчас не нужно.

---

## 4. Как Communication связывается с бизнес-документом

У Communication есть пара:

```text
reference_doctype
reference_name
```

Например:

```text
reference_doctype = Request
reference_name    = REQ-0001
```

Это означает:

```text
это письмо относится к Request REQ-0001
```

Именно благодаря такой связи Communication может появляться в Timeline исходного документа.

Сама запись `Request` при этом не обязана содержать поля:

```text
last_email
email_body
email_thread
```

История переписки хранится отдельно.

---

## 5. Одно письмо может появляться и в других Timeline

В v16 у Communication есть Child Table:

```text
Timeline Links
```

Она использует `Communication Link`.

Поэтому кроме основной пары:

```text
reference_doctype
reference_name
```

Communication может иметь дополнительные ссылки на документы.

Это полезно, когда одно письмо относится не к одной-единственной записи.

Но для первого понимания достаточно такой модели:

```text
reference_doctype + reference_name
→ основной документ

Timeline Links
→ дополнительные связанные документы
```

---

## 6. Исходящее письмо из формы

Когда пользователь отправляет письмо в контексте существующего Document, Frappe не начинает сразу с SMTP.

Упрощённая последовательность:

```text
пользователь нажал Email
        ↓
проверить permission
        ↓
создать Communication
        ↓
прикрепить файлы к Communication
        ↓
выбрать outgoing Email Account
        ↓
frappe.sendmail(...)
        ↓
Email Queue
        ↓
фактическая отправка
```

Это важнее, чем кажется.

Письмо сначала становится частью модели данных Frappe, а уже затем отправляется наружу.

---

## 7. Для отправки есть отдельное permission `Email`

В Role Permission Manager мы уже видели право:

```text
Email
```

Теперь становится понятно, зачем оно существует.

Текущий v16 при создании Communication для конкретного документа выполняет проверку примерно такого смысла:

```python
frappe.has_permission(
    doctype,
    doc=name,
    ptype="email",
    throw=True,
)
```

Поэтому:

```text
Read
```

не означает автоматически:

```text
можно отправлять письма от имени этого Document
```

И даже `Write` — это не то же самое, что `Email`.

Это отдельное право модели permissions.

---

## 8. Что создаётся первым: Communication или Email Queue

Сначала создаётся:

```text
Communication
```

В него записываются:

```text
subject
content
sender
recipients
cc
bcc
reference_doctype
reference_name
message_id
...
```

Только после этого, если действительно требуется отправка, вызывается email-механизм Framework.

Поэтому полезно разделять:

```text
Communication
→ логическая запись общения

Email Queue
→ техническая очередь доставки email
```

Один отвечает на вопрос:

```text
что за письмо и к чему оно относится?
```

Другой:

```text
отправлено ли оно почтовым сервером?
```

---

## 9. Email Queue

Обычная отправка во Frappe рассчитана на очередь.

Communication формирует данные для `frappe.sendmail()`, в том числе:

```text
recipients
cc
bcc
sender
subject
content
attachments
reference_doctype
reference_name
communication
send_after
```

В текущем v16 для стандартной Communication-отправки передаётся:

```text
delayed = True
```

То есть нормальная модель — не держать HTTP-запрос открытым, пока внешний SMTP-сервер физически отправляет письмо.

Упрощённо:

```text
Save / Send
    ↓
Email Queue
    ↓
email worker
    ↓
SMTP
```

Позже очередь и background jobs будут разобраны отдельно.

---

## 10. `delivery_status` — не бизнес-статус документа

У Communication есть собственное поле доставки.

В metadata v16 среди возможных значений есть, например:

```text
Scheduled
Sending
Sent
Error
Expired
Bounced
Opened
Rejected
Delayed
Clicked
Read
...
```

Не надо путать его с:

```text
Request.status
workflow_state
docstatus
ToDo.status
Communication.status
```

Например:

```text
Request.status = Open
Communication.delivery_status = Sent
```

означает всего лишь:

```text
заявка остаётся открытой,
а конкретное письмо успешно ушло
```

---

## 11. Как Communication узнаёт состояние Email Queue

Для исходящей Communication v16 смотрит связанные записи `Email Queue`.

Упрощённо:

```text
есть Not Sent / Sending
→ Communication.delivery_status = Sending

есть Error
→ Error

есть Expired
→ Expired

есть Sent
→ Sent
```

То есть `delivery_status` Communication является удобным верхнеуровневым состоянием доставки.

Но сама очередь остаётся отдельной технической сущностью.

---

## 12. Как выбирается Email Account

Для реальной отправки нужен подходящий outgoing `Email Account`.

Frappe может использовать:

- явно связанный `email_account`;
- подходящий outgoing account для отправителя или DocType;
- стандартный outgoing account в рамках штатной логики выбора.

Если подходящего аккаунта нет, Communication создать можно, но стандартная попытка реально отправить email завершится ошибкой о том, что outgoing Email Account не настроен.

Модель:

```text
Communication
        ↓
какой Email Account отправляет?
        ↓
outgoing account
        ↓
SMTP / другой backend
```

---

## 13. Email Account — это настройка почтового подключения

`Email Account` — отдельный системный DocType.

В v16 один аккаунт может иметь:

```text
Enable Incoming
Enable Outgoing
Default Incoming
Default Outgoing
```

и настройки подключения:

```text
IMAP / POP
SMTP
OAuth / password
SSL / TLS
```

Также текущий v16 поддерживает сервис `Frappe Mail` как отдельный вариант backend.

Для новичка главное различие:

```text
Communication
→ одно конкретное сообщение

Email Account
→ настройка почтового ящика / транспорта
```

---

## 14. Входящая почта

Если у Email Account включено:

```text
Enable Incoming
```

Framework может получать письма из почтового ящика.

Для обычной почты используются IMAP или POP, а для поддерживаемого backend возможна другая реализация.

После получения сырого email Framework разбирает:

```text
From
To
CC
BCC
Subject
Message-ID
In-Reply-To
Date
HTML / text body
attachments
```

и создаёт:

```text
Communication
sent_or_received = Received
communication_medium = Email
```

То есть входящее письмо тоже становится обычным Document Frappe.

---

## 15. Как входящий ответ попадает обратно в нужный документ

Вот одна из самых полезных возможностей Framework.

Представим:

```text
Request REQ-0001
        ↓
мы отправили email
        ↓
Communication COMM-1
        ↓
получатель нажал Reply
        ↓
входящий email
```

У обычного email-ответа есть заголовок:

```text
In-Reply-To
```

Frappe пытается по нему найти предыдущее сообщение.

В текущем v16 поиск идёт через `message_id` существующей Communication, а при необходимости — через связанную `Email Queue` и дополнительные fallback-варианты.

Если предыдущая Communication найдена, новая входящая запись получает:

```text
in_reply_to = COMM-1
```

А затем может унаследовать основной бизнес-документ:

```text
reference_doctype = Request
reference_name    = REQ-0001
```

В итоге пользователь видит продолжение переписки в Timeline того же Request.

---

## 16. `message_id` и `in_reply_to` — это разные вещи

У исходящего сообщения есть собственный:

```text
message_id
```

Например условно:

```text
abc123@example
```

В ответном email заголовок `In-Reply-To` ссылается на Message-ID предыдущего сообщения.

После сопоставления Frappe записывает уже внутреннюю ссылку:

```text
Communication.in_reply_to
→ Link на предыдущий Communication
```

Поэтому:

```text
email Message-ID
```

и

```text
Communication.name
```

— не одно и то же.

---

## 17. `Communication.status`

Кроме `delivery_status`, у обычной Communication есть ещё поле:

```text
status
```

В v16 его варианты:

```text
Open
Replied
Closed
Linked
```

Например новая Communication, связанная с бизнес-документом, получает:

```text
Linked
```

А если исходящая Communication является ответом на другую Communication, предыдущая запись может перейти в:

```text
Replied
```

Это состояние самой communication/thread-записи.

Оно не закрывает исходный Request и не выполняет Workflow transition.

---

## 18. Новое входящее письмо не обязано быть ответом

Пусть на почту приходит новое письмо:

```text
From: user@example.com
Subject: Need a new monitor
```

У него нет подходящего `In-Reply-To`.

Тогда возможны разные варианты.

### Вариант 1. Оставить как Communication

Письмо может существовать само по себе без бизнес-документа.

### Вариант 2. Использовать Append To

У incoming Email Account есть механизм `Append To`.

Он позволяет сказать Framework примерно следующее:

```text
новые входящие письма этого ящика
→ связывай с определённым DocType
```

Если подходящий документ уже найден, письмо связывается с ним.

Если его нет, Frappe умеет создать новый reference Document для настроенного `Append To` DocType.

---

## 19. Что требуется от DocType для Append To

Email Account прямо предупреждает, что целевой DocType должен иметь поля для email-настройки, в частности смысловые поля:

```text
Sender
Subject
```

В DocType существуют соответствующие email-настройки metadata, через которые Framework понимает, какие реальные fieldname использовать.

Упрощённо:

```text
входящий email
├── sender  → поле отправителя нового документа
├── subject → поле темы нового документа
└── body    → Communication, связанная с документом
```

Не надо создавать самодельный парсер входящих писем, пока штатный `Append To` закрывает задачу.

---

## 20. IMAP и Append To в v16

Здесь есть деталь актуальной версии.

Для POP Email Account имеет обычный общий:

```text
Append To
```

При IMAP в v16 можно настроить отдельные папки через Child Table `IMAP Folder`, и `append_to` передаётся для конкретной синхронизируемой папки.

Поэтому не стоит воспринимать один `Email Account.append_to` как единственный вариант маршрутизации входящей почты во всех режимах.

---

## 21. Вложения письма

Письмо может иметь attachments.

Но здесь важно вспомнить прошлую главу.

Файл всё равно представлен отдельным:

```text
File
```

Для исходящей Communication стандартный код создаёт или переиспользует File и связывает его так:

```text
attached_to_doctype = Communication
attached_to_name    = <имя Communication>
```

Получается:

```text
Request REQ-0001
        ↑
Communication COMM-1
        ↑
File invoice.pdf
```

То есть attachment email логически может быть прикреплён именно к Communication, а не напрямую к Request.

Timeline при показе письма может затем получить связанные файлы Communication.

---

## 22. Отправить Print Format как attachment

Email-механизм умеет отправлять не только уже существующие File.

В `CommunicationEmailMixin` предусмотрена отправка печатного представления связанного документа.

Упрощённо:

```text
Request REQ-0001
        ↓
Print Format
        ↓
PDF / print attachment
        ↓
email
```

Технические детали Print Format и PDF будут в следующей главе.

---

## 23. `Send After`

У Communication есть:

```text
send_after
```

Если оно заполнено, письмо можно поставить на более позднюю отправку.

При создании такой новой Communication `delivery_status` становится:

```text
Scheduled
```

Это не то же самое, что Auto Repeat.

```text
Send After
→ отложить одно конкретное письмо

Auto Repeat
→ периодически создавать новые Documents
```

---

## 24. Отмена только что отправленного письма

В текущем v16 есть функция `undo_email_send`.

Но это не настоящая отмена письма после его доставки.

Механика работает только пока сообщение ещё стоит в Email Queue со статусом:

```text
Not Sent
```

И только в очень коротком окне — **10 секунд** после создания Communication.

Если worker уже начал отправку, отменить письмо таким способом поздно.

Поэтому правильная модель:

```text
Undo Send
→ попытаться убрать письмо из очереди до фактической отправки
```

а не:

```text
забрать уже доставленное письмо с чужого почтового сервера
```

---

## 25. Read receipt и tracking

Communication содержит поля:

```text
read_receipt
read_by_recipient
read_by_recipient_on
delivery_status
```

А Email Account имеет настройку:

```text
Track Email Status
```

Текущий metadata v16 прямо предупреждает: если письмо отправлено нескольким получателям, открытие хотя бы одним из них может привести к тому, что письмо считается открытым.

Поэтому email tracking нельзя воспринимать как юридически надёжное доказательство, что **каждый** адресат лично прочитал сообщение.

---

## 26. Communication и Timeline

В главе 29 мы уже видели, что Timeline загружает Communications отдельно от Comments.

То есть:

```text
Comment
```

и

```text
Communication
```

— разные Documents.

Timeline просто показывает их вместе в одной визуальной истории.

Пример:

```text
Timeline Request REQ-0001

09:10 Comment
      Need more information

09:20 Communication
      Email sent to user@example.com

10:02 Communication
      Reply received from user@example.com

10:15 Attachment
      photo.jpg added
```

Пользователь видит одну историю.

В базе это несколько разных механизмов.

---

## 27. Communication против Comment

Используй `Comment`, когда это внутреннее обсуждение вокруг документа:

```text
аналитик написал заметку коллеге
```

Используй Communication/email-механику, когда это реальное сообщение с адресатами:

```text
письмо ушло на user@example.com
```

Коротко:

| Задача | Механизм |
|---|---|
| внутренняя реплика в Timeline | Comment |
| исходящий email | Communication |
| входящий email | Communication |
| телефонный контакт как структурированная коммуникация | Communication с другим medium |

---

## 28. Communication против Notification

Это ещё одна частая путаница.

### Notification

Отвечает на вопрос:

```text
когда автоматически кого-то уведомить?
```

Например:

```text
Request.status изменился на Approved
→ автоматически отправить email
```

### Communication

Отвечает на вопрос:

```text
какое конкретное сообщение было отправлено или получено?
```

Notification может породить email.

Но правило Notification и запись Communication — не одно и то же.

У `Communication` в v16 даже есть отдельный тип:

```text
Communication
Automated Message
```

Автоматическое сообщение остаётся конкретной записью общения, а Notification остаётся правилом автоматизации.

---

## 29. Communication против Email Queue

Ещё раз зафиксируем:

```text
Communication
→ сообщение как часть данных системы

Email Queue
→ техническая доставка
```

Если Email Queue временно упала, это не означает, что нужно превращать бизнес-документ в «неотправленное письмо».

Архитектура уже разделяет эти ответственности.

---

## 30. Communication против бизнес-объекта

Не надо пытаться превратить Communication в универсальную заявку, обращение или задачу.

Communication хорошо хранит:

```text
кто
кому
когда
что написал
к чему это относится
```

Но поля вроде:

```text
priority
responsible_user
business_status
department
category
approval_result
```

обычно относятся уже к отдельному бизнес-DocType.

Правильнее:

```text
Request
→ бизнес-состояние

Communication
→ переписка вокруг Request
```

чем создавать десятки бизнес-полей прямо в Communication.

---

## 31. Что видит пользователь

В обычном сценарии пользователь не обязан вручную открывать список `Communication`.

Он работает примерно так:

```text
открыть Request
→ нажать Email
→ заполнить To / Subject / Message
→ отправить
→ увидеть письмо в Timeline
→ получить ответ
→ увидеть ответ там же
```

А системные сущности:

```text
Communication
Email Queue
Email Account
File
```

работают под этим интерфейсом.

Это хороший пример общего принципа Frappe:

> простое действие в Desk часто опирается сразу на несколько связанных DocType.

---

## 32. Когда достаточно штатного email-механизма

Оставайся в стандартных возможностях, если требуется:

- отправлять письма из Document;
- видеть переписку в Timeline;
- принимать ответы обратно;
- хранить email attachments;
- иметь один или несколько Email Account;
- маршрутизировать входящие письма через Append To;
- использовать Notification для автоматических писем;
- отправлять Print Format;
- использовать обычную очередь отправки.

Для таких задач не нужен собственный почтовый клиент.

---

## 33. Когда может понадобиться код

Код становится оправданным, если появляется требование вроде:

```text
по сложному бизнес-правилу определить другой reference Document
```

или:

```text
после входящего письма разобрать специальный формат тела
и создать несколько связанных Documents
```

или:

```text
использовать внешний email provider
с нестандартной логикой доставки
```

Для последнего Framework также имеет hooks вроде:

```text
override_email_send
get_sender_details
```

Но это уже уровень собственного App, а не первый инструмент для обычной отправки письма.

---

## 34. Чего не надо делать

### Ошибка 1. Хранить всю переписку в одном Text field

Например:

```text
email_history = "..."
```

У Frappe уже есть Communication.

### Ошибка 2. Создавать `last_email_body` и постоянно его перезаписывать

Так теряется нормальная история отдельных сообщений.

### Ошибка 3. Считать Timeline физическим хранилищем писем

Timeline — только интерфейс сборки истории.

### Ошибка 4. Путать Notification с Communication

Notification — правило.

Communication — конкретное сообщение.

### Ошибка 5. Путать Communication с Email Queue

Communication — содержание и связь.

Email Queue — доставка.

### Ошибка 6. Давать Email permission только потому, что есть Read

`Email` — отдельное permission.

### Ошибка 7. Писать свой IMAP parser до проверки Append To

Framework уже умеет принимать почту, определять ответы и создавать/связывать reference Documents.

---

## 35. Полная схема

```text
                    Email Account
                    ├── incoming
                    └── outgoing
                         │
                         │
Request REQ-0001         │
        │                │
        │ Email          │
        ▼                │
Communication COMM-1     │
Sent                     │
        │                │
        ├── File         │
        │   attachment   │
        │                │
        ▼                │
    Email Queue ─────────┘
        │
        ▼
      SMTP
        │
        ▼
   external recipient
        │
        │ Reply
        ▼
 incoming mailbox
        │
        ▼
InboundMail parser
        │
        ├── In-Reply-To
        │       ↓
        │ find COMM-1
        │
        ▼
Communication COMM-2
Received
        │
        ├── in_reply_to = COMM-1
        └── reference = Request REQ-0001
```

Если эта схема понятна, большая часть email-механики Frappe уже перестаёт выглядеть магией.

---

## Мини-практика

Возьми учебный DocType `Request`.

### Шаг 1. Проверь permission

Создай роль:

```text
Request Operator
```

Для `Request` включи:

```text
Read
Email
```

Проверь поведение обычным пользователем, не Administrator.

### Шаг 2. Настрой outgoing Email Account

На тестовом Site настрой Email Account с:

```text
Enable Outgoing = 1
```

При необходимости сделай его Default Outgoing.

Не используй рабочую корпоративную почту для экспериментов без необходимости.

### Шаг 3. Отправь письмо из Request

Открой:

```text
Request REQ-0001
```

Отправь тестовое письмо на собственный тестовый адрес.

После этого найди созданный `Communication` и посмотри:

```text
communication_medium
sent_or_received
sender
recipients
subject
reference_doctype
reference_name
message_id
delivery_status
```

### Шаг 4. Посмотри Timeline

Убедись, что Communication отображается в Timeline `REQ-0001`.

### Шаг 5. Добавь attachment

Отправь второе письмо с маленьким тестовым файлом.

Посмотри соответствующие `File` и проверь:

```text
attached_to_doctype = Communication
attached_to_name    = <имя Communication>
```

### Шаг 6. Если есть тестовый incoming account

Ответь на письмо обычной кнопкой Reply во внешнем почтовом клиенте.

После синхронизации найди входящую Communication и проверь:

```text
sent_or_received = Received
in_reply_to
reference_doctype
reference_name
```

Цель упражнения — увидеть не только красивую переписку в Timeline, а реальные Documents под ней.

---

## Что запомнить

1. **`Communication` — отдельный DocType для конкретного сообщения или другого факта общения.**
2. Email — только один из `communication_medium`.
3. Письмо связывается с бизнес-документом через `reference_doctype` и `reference_name`.
4. Исходящее письмо из Document требует отдельного permission `Email`.
5. Сначала создаётся Communication, затем email уходит через механизм отправки и Email Queue.
6. `Email Account` — настройка транспорта, а не письмо.
7. Входящие письма тоже становятся Communication с `sent_or_received = Received`.
8. Ответы связываются с предыдущими письмами через email `In-Reply-To` / `message_id` и внутреннее `Communication.in_reply_to`.
9. `Append To` позволяет маршрутизировать новые входящие письма к бизнес-DocType и при необходимости создавать reference Document.
10. Email attachments остаются Documents типа `File`.
11. `Communication`, `Comment`, `Notification` и `Email Queue` решают разные задачи.
12. Timeline только объединяет их в один удобный интерфейс.

---

## Источники

Официальная документация и API:

- [What is Frappe Framework? — Email](https://docs.frappe.io/framework/user/en/basics)
- [Utility Functions — `frappe.sendmail`](https://docs.frappe.io/framework/user/en/api/utils)
- [Hooks — Email Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)

Текущий исходный код `version-16`:

- [`Communication` metadata](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/communication/communication.json)
- [`Communication` controller](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/communication/communication.py)
- [`Communication` email creation](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/communication/email.py)
- [`CommunicationEmailMixin`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/communication/mixins.py)
- [`Email Account` metadata](https://github.com/frappe/frappe/blob/version-16/frappe/email/doctype/email_account/email_account.json)
- [`Email Account` controller](https://github.com/frappe/frappe/blob/version-16/frappe/email/doctype/email_account/email_account.py)
- [Incoming email parser](https://github.com/frappe/frappe/blob/version-16/frappe/email/receive.py)

Следующая глава: **33. Print Format и PDF**.
