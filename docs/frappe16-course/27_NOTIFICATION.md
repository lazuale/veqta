# 27. Notification

В предыдущих главах мы уже разобрали несколько похожих по ощущениям механизмов:

```text
Assignment
Workflow
Workflow Action
```

Теперь добавим ещё один:

```text
Notification
```

Notification отвечает не за назначение работы и не за изменение состояния документа.

Его задача проще:

> когда произошло нужное событие и выполнено условие — отправить нужным получателям сообщение.

Проверено: **2026-08-31**.

---

## 1. Самый простой пример

Есть DocType:

```text
Request
├── subject
├── status
├── due_date
└── owner
```

Нам нужно правило:

> когда создаётся новый Request, показать его создателю системное уведомление.

Вместо собственного Python можно создать `Notification`:

```text
Document Type: Request
Send Alert On: New
Channel: System Notification
Receiver: owner
```

После создания `REQ-0001` Framework сам проверит правило и создаст уведомление.

Удобно запомнить так:

```text
событие
   ↓
Notification
   ↓
условие
   ↓
получатели
   ↓
сообщение
```

---

## 2. Notification — отдельный системный DocType

Настройка уведомления сама является Document:

```text
Notification
```

В ней хранятся:

```text
Enabled
Channel
Document Type
Send Alert On
Condition
Recipients
Subject / Message
Attachment Settings
```

То есть обычное уведомление можно собрать через Desk без написания собственного обработчика событий.

---

# Сначала не путаем четыре разных механизма

## 3. Notification ≠ Assignment

Assignment отвечает на вопрос:

```text
кто должен выполнить работу?
```

Он создаёт `ToDo`.

Notification отвечает:

```text
кого надо проинформировать?
```

Он не делает пользователя исполнителем.

Например:

```text
Assign Boris
→ у Бориса появился ToDo

Notification to Boris
→ Борис получил сообщение
```

Это разные действия.

---

## 4. Notification ≠ Workflow

Workflow отвечает:

```text
какие переходы состояния разрешены
и кто может их выполнить?
```

Notification отвечает:

```text
когда и кому отправить сообщение?
```

Можно использовать их вместе.

Например:

```text
Workflow:
Review → Approved

Notification:
при изменении status на Approved
→ сообщить автору
```

Но Notification сам по себе не является машиной состояний.

---

## 5. Notification ≠ Workflow Action

`Workflow Action` — это системная запись о том, что пользователю с подходящей Role доступно действие Workflow.

`Notification` — универсальное правило оповещения.

Не нужно создавать Notification только для того, чтобы вручную имитировать Workflow Action.

У Workflow уже есть собственная механика действий и email-оповещений.

---

## 6. Notification ≠ Notification Log

Названия очень похожи.

### `Notification`

Это **правило**:

```text
когда
при каком условии
кому
что отправить
```

### `Notification Log`

Это уже **конкретное системное уведомление пользователя**, которое может появиться в интерфейсе Desk.

То есть упрощённо:

```text
Notification rule
        ↓ сработало
Notification Log
        ↓
пользователь видит уведомление
```

---

# Каналы

## 7. В текущем Frappe v16 есть четыре штатных Channel

В `Notification` доступны:

```text
Email
Slack
System Notification
SMS
```

Каждый канал решает немного разную задачу.

---

## 8. Email

Самый обычный вариант:

```text
Channel: Email
```

Нужно настроить исходящую почту через `Email Account`.

Для письма можно задавать:

```text
Sender
Subject
Message
Recipients
CC
BCC
Attachments
```

Например:

```text
Subject:
Request {{ doc.name }} is overdue
```

и тело письма:

```html
<p>Request {{ doc.name }} requires attention.</p>
<p>Status: {{ doc.status }}</p>
```

---

## 9. Slack

Для:

```text
Channel: Slack
```

используется заранее настроенный:

```text
Slack Webhook URL
```

Notification рендерит сообщение и отправляет его через выбранный webhook.

Это удобно для общего канала команды, но Slack не превращается от этого в систему Assignment или Workflow.

---

## 10. System Notification

Это уведомление внутри Desk.

Для него в текущем v16 есть отдельные настройки:

```text
Notification Type
Notification Title
Notification Message
```

Например:

```text
Notification Title:
New request {{ doc.name }}

Notification Message:
{{ doc.subject }}
```

Такое уведомление попадает в систему внутренних уведомлений Frappe.

---

## 11. Можно добавить System Notification к другому каналу

В v16 есть отдельная галочка:

```text
Send System Notification
```

Например, основным каналом можно оставить:

```text
Email
```

но дополнительно создать и внутреннее уведомление Desk.

Получается:

```text
Email
+
System Notification
```

без второго отдельного Notification rule.

---

## 12. SMS

Для:

```text
Channel: SMS
```

нужны настроенные `SMS Settings`.

Получатель должен определяться через подходящее поле телефона, User, Customer или Role.

Для первого учебного проекта SMS обычно не нужен, но важно знать, что это штатный канал Framework.

---

# Когда Notification срабатывает

## 13. `Send Alert On`

В текущем v16 доступны события:

```text
New
Save
Submit
Cancel
Days After
Days Before
Minutes After
Minutes Before
Value Change
Method
Custom
```

Это гораздо важнее, чем просто выбрать канал.

Сначала определяем:

```text
КОГДА должно срабатывать правило?
```

и только потом:

```text
ЧТО отправлять?
```

---

## 14. `New`

`New` означает создание нового Document.

Внутри текущего v16 этот Notification event связан с lifecycle-событием:

```text
after_insert
```

То есть пример:

```text
создан новый Request
→ New Notification
→ отправить сообщение
```

---

## 15. `Save`

`Save` привязан к:

```text
on_update
```

То есть правило может проверяться при сохранении документа.

Например:

```text
Send Alert On: Save
Condition: doc.priority == "High"
```

Но здесь нужно быть осторожным.

Если документ сохраняют десять раз и условие всё время остаётся истинным, уведомление может оказаться слишком шумным.

Если нас интересует именно **изменение конкретного поля**, обычно лучше использовать:

```text
Value Change
```

---

## 16. `Submit`

Для Submittable DocType можно использовать:

```text
Send Alert On: Submit
```

Это соответствует:

```text
on_submit
```

Например:

```text
Document submitted
→ уведомить контролёра
```

---

## 17. `Cancel`

`Cancel` связан с:

```text
on_cancel
```

Например:

```text
Document cancelled
→ сообщить владельцу процесса
```

---

# Value Change

## 18. `Value Change` следит за одним конкретным полем

Предположим:

```text
status = Open
```

Потом пользователь меняет:

```text
status = Closed
```

Можно настроить:

```text
Send Alert On: Value Change
Value Changed: status
```

Тогда Notification проверит именно изменение этого поля.

---

## 19. `Value Change` означает «значение поменялось», а не «стало равным X»

Если настроить только:

```text
Value Changed: status
```

правило может сработать и на:

```text
Open → In Progress
```

и на:

```text
In Progress → Closed
```

Если нужно только закрытие, добавляем Condition:

```python
doc.status == "Closed"
```

Получается:

```text
поле status изменилось
        +
новое значение == Closed
        ↓
отправить Notification
```

---

## 20. На создании документа Value Change не используется

Текущий v16 отдельно исключает `Value Change` для первоначальной вставки документа.

То есть:

```text
новый Document
```

не считается обычным переходом старого значения поля в новое.

Для создания используется:

```text
New
```

---

# Date-based события

## 21. `Days Before` и `Days After`

Допустим, есть поле:

```text
due_date
Date
```

Нам нужно предупредить за два дня.

Настройка:

```text
Send Alert On: Days Before
Reference Date: due_date
Days Before or After: 2
```

Тогда правило ищет документы, дата которых подходит под сегодняшнюю проверку.

---

## 22. Это не таймер внутри каждого Document

Frappe не запускает отдельный процесс ожидания для каждой записи.

Date-based Notifications проверяются scheduler-ом.

Упрощённо:

```text
scheduler
   ↓
найти активные Days Before / Days After rules
   ↓
найти документы на нужную дату
   ↓
проверить Condition
   ↓
отправить
```

Поэтому для таких уведомлений важна работа scheduler.

---

## 23. В v16 Date Notification можно использовать и с Child DocType

Это отдельное текущее поведение v16.

Обычные Notification events для Child DocType запрещены.

Но для child table разрешены:

```text
Days Before
Days After
```

То есть можно реагировать на дату, которая хранится в строках дочерней таблицы.

Это не означает, что любой Notification event теперь можно навесить на Child DocType.

---

# Datetime-based события v16

## 24. `Minutes Before` и `Minutes After`

В актуальном v16 есть ещё два события:

```text
Minutes Before
Minutes After
```

Они работают уже с полем:

```text
Datetime
```

Например:

```text
meeting_at = 2026-09-01 14:00
```

и правило:

```text
Minutes Before: 30
```

может использоваться для напоминания незадолго до события.

---

## 25. Минутная точность здесь не абсолютная

В текущем v16 scheduler проверяет такие правила примерно раз в 5 минут.

Поэтому интерфейс прямо предупреждает:

```text
actual sending may be delayed by up to 5 minutes
```

Кроме того, backend требует:

```text
Minutes Offset >= 10
```

Поэтому Notification не стоит использовать как механизм жёсткого real-time SLA вида:

```text
отправить строго в 14:00:00
```

Это плановое scheduler-based уведомление.

---

# Method

## 26. `Method` привязывает Notification к Document method

Можно выбрать:

```text
Send Alert On: Method
Trigger Method: before_insert
```

или другой lifecycle method, реально вызываемый выбранным DocType.

Внутренний механизм v16 сравнивает:

```text
method == alert.method
```

и тогда запускает Notification.

---

## 27. Method полезен, но не надо начинать с него

Если задача звучит:

```text
при создании
при сохранении
при Submit
при Cancel
при изменении поля
за N дней
```

для этого уже есть специальные события.

`Method` нужен, когда требуется привязаться именно к конкретному Document method.

Не стоит выбирать его просто потому, что название звучит «более технически».

---

# Custom

## 28. `Custom` означает явный запуск из кода

Иногда Notification надо отправить не из стандартного lifecycle-события, а из собственного серверного сценария.

Для этого есть:

```text
Send Alert On: Custom
```

В текущем v16 рекомендуемый серверный путь — получить Notification и поставить отправку в очередь:

```python
notification = frappe.get_doc("Notification", "Request Escalated")
notification.queue_send(doc)
```

Это уже граница:

```text
настройка Notification
+
явный вызов из App / Server Script
```

---

# Условия

## 29. Notification не обязан срабатывать на каждый подходящий event

Для этого существует Condition.

Простейший пример:

```python
doc.status == "Open"
```

Или:

```python
doc.priority == "High"
```

Или:

```python
doc.due_date == nowdate()
```

Схема:

```text
Event совпал
   ↓
Condition == True?
   ↓ да
send
```

---

## 30. В v16 есть два типа условий

В текущем Notification есть:

```text
Condition Type:
Python
Filters
```

Это важное отличие от старых инструкций, где обычно показывали только Python expression.

---

## 31. `Python` Condition

Например:

```python
doc.status == "Open" and doc.priority == "High"
```

Выражение выполняется через безопасный evaluation-контекст Frappe.

Основной объект:

```text
doc
```

То есть текущий Document.

Также доступны ограниченные безопасные функции, включая `nowdate()` и часть `frappe` safe globals.

---

## 32. `Filters` — более простой вариант без выражения Python

В v16 можно выбрать:

```text
Condition Type: Filters
```

и собрать условия через стандартный Filter UI.

Например логически:

```text
status = Open
priority = High
```

Для новичка это хороший первый выбор, если условие нормально выражается обычными фильтрами.

Иерархия простая:

```text
обычные Filters
        ↓ не хватает
Python Condition
        ↓ не хватает
собственная серверная логика
```

---

## 33. Не путай Condition Notification с permissions

Condition отвечает:

```text
отправлять сообщение или нет?
```

Permissions отвечают:

```text
может ли пользователь работать с Document?
```

Notification Condition не является защитой данных.

---

# Получатели

## 34. Получатели задаются отдельно от события

Для Email, System Notification и SMS используется таблица:

```text
Recipients
```

В строке получателя есть основные варианты:

```text
Receiver By Document Field
Receiver By Role
CC
BCC
Condition
```

---

## 35. Receiver By Document Field

Предположим, у `Request` есть:

```text
requested_by
Link → User
```

Можно выбрать это поле получателем.

Тогда для каждого конкретного Request адресат определяется по самому документу.

Например:

```text
REQ-0001.requested_by = anna@example.com
```

значит сообщение уйдёт Анне.

---

## 36. Можно использовать `owner`

В интерфейсе Notification среди вариантов получателя есть:

```text
owner
```

То есть можно отправлять уведомление создателю документа без отдельного поля `requested_by`.

Но помним главу 21:

```text
owner = создатель Document
```

а не текущий исполнитель.

---

## 37. Получатель может находиться в Child Table

Текущий интерфейс v16 умеет подхватывать подходящие recipient-поля и из Child Table.

В выборе они отображаются как путь примерно вида:

```text
child_table > email
```

После этого Frappe проходит по строкам таблицы и собирает получателей.

Это удобно, когда адресаты уже являются частью нормальной модели документа.

---

## 38. Receiver By Role

Можно выбрать:

```text
Receiver By Role: Request Manager
```

Тогда Frappe получает пользователей с этой Role и добавляет их в список адресатов.

Это подходит для правил вида:

> сообщить всем пользователям роли контролёра.

Но если в Role 30 человек, уведомление действительно может уйти многим людям.

Role здесь не означает «выбрать одного ответственного».

---

## 39. Recipient Condition

У каждой строки получателя есть собственное поле:

```text
Condition
```

Это позволяет сделать, например:

```text
менеджеру отправлять всегда

финансовому контролёру
→ только если сумма > 100000
```

То есть есть два уровня условий:

```text
Notification Condition
→ срабатывать ли правилу вообще

Recipient Condition
→ включать ли конкретного получателя
```

---

## 40. `Send To All Assignees`

Для Email в v16 есть штатная галочка:

```text
Send To All Assignees
```

Frappe находит активные `ToDo`:

```text
status = Open
reference_type = текущий DocType
reference_name = текущий Document
```

и добавляет их `allocated_to` в получателей.

Вот здесь главы 23 и 27 соединяются:

```text
Assignment
→ кто назначен

Notification
→ отправить сообщение всем назначенным
```

---

# Subject и Message

## 41. Notification использует Jinja

В Subject и Message можно подставлять данные документа.

Например:

```text
Request {{ doc.name }} requires review
```

или:

```html
<h3>{{ doc.subject }}</h3>
<p>Status: {{ doc.status }}</p>
```

Главный объект:

```text
doc
```

---

## 42. В Message можно использовать comments

Notification context также может содержать комментарии документа.

Например:

```jinja2
{% if comments %}
Last comment: {{ comments[-1].comment }}
{% endif %}
```

Это удобно для информативного письма, но не нужно превращать каждое уведомление в полный дамп Timeline.

---

## 43. Есть Preview

Текущий v16 добавляет на Notification кнопку:

```text
Preview
```

Для выбранного документа можно проверить:

```text
Meets Condition?
Subject
Message
```

Это намного лучше, чем сохранять правило и потом гадать, что отрендерит Jinja.

---

# Вложения

## 44. `Attach Print`

Для Notification можно включить:

```text
Attach Print
```

и выбрать:

```text
Print Format
```

Тогда к письму прикладывается печатная форма документа.

Здесь действуют обычные Print Settings.

Например, если печать Draft запрещена, нельзя рассчитывать, что Notification магически обойдёт это ограничение.

---

## 45. `Attach Files`

В текущем v16 есть:

```text
Attach Files:
From Field
All
```

### From Field

Берётся файл из конкретного поля:

```text
Attach
или
Attach Image
```

### All

Берутся все `File`, прикреплённые к текущему документу.

Это уже знакомая нам стандартная файловая модель Frappe.

---

# Изменить поле после отправки

## 46. `Set Property After Alert`

Notification умеет не только отправить сообщение, но и после этого записать значение в поле документа.

Например:

```text
Set Property After Alert: reminder_sent
Value To Be Set: 1
```

Тогда после успешного прохождения Notification logic Frappe может обновить документ.

---

## 47. С этой функцией нужно быть осторожнее

Потому что Notification внезапно перестаёт быть чисто информационным механизмом.

Получается:

```text
событие
→ Notification
→ отправка
→ изменение Document
```

Для Submitted Document поле должно позволять изменение после Submit:

```text
Allow on Submit
```

Иначе Frappe не должен менять его обычным способом.

Для простого флага вроде:

```text
reminder_sent
```

это может быть удобно.

Но сложную бизнес-логику лучше не прятать в Notification.

---

# Плановые проверки

## 48. `Get Alerts for Today`

Для `Days Before / Days After` текущий интерфейс v16 добавляет кнопку:

```text
Get Alerts for Today
```

Она помогает проверить, какие документы правило считает подходящими сегодня.

Это хороший первый инструмент диагностики date-based Notification.

---

## 49. Для плановых Notification должен работать scheduler

Если:

```text
New
Save
Value Change
```

работают,

а:

```text
Days Before
Minutes Before
```

не работают,

нужно проверять не только само правило, но и scheduler.

Эту серверную часть курса мы подробно разберём позже.

Пока достаточно понимать зависимость:

```text
scheduled Notification
→ требует scheduler
```

---

# Standard Notification

## 50. Notification может быть частью App

В Developer Mode доступна настройка:

```text
Is Standard
```

Для Standard Notification задаётся Module, а данные и template могут экспортироваться в App.

Это уже путь от site-level настройки к версии, хранимой вместе с кодом приложения.

---

## 51. Standard Notification нельзя спокойно править на production-site

В текущем v16 включённый Standard Notification нельзя редактировать вне Developer Mode обычным способом.

Идея такая же, как у других standard-объектов:

```text
источник истины
→ App / Git

конкретный Site
→ получает стандартную конфигурацию
```

Если на Site нужна собственная версия правила, стандартную конфигурацию обычно не стоит тайно менять в обход App.

---

# Notification и UI-колокольчик — не одно и то же

## 52. У Desk есть ещё общий Notification dropdown

В Frappe существует и более общий механизм конфигурации элементов notification dropdown через hook:

```python
notification_config
```

Это другой уровень Framework.

Он управляет тем, какие элементы и счётчики отображаются в Desk notification area.

Не надо путать его с DocType:

```text
Notification
```

который мы изучаем в этой главе.

---

# Как выбрать механизм

## 53. Простая карта

| Требование | Механизм |
|---|---|
| Назначить человеку работу | Assignment / ToDo |
| Автоматически выбрать исполнителя | Assignment Rule |
| Ограничить переходы состояний | Workflow |
| Показать пользователю доступное согласование | Workflow Action |
| Отправить сообщение при событии | Notification |
| Выполнить внешний HTTP callback | Webhook |
| Сделать произвольную серверную операцию | App code / Server Script |

Эта таблица экономит огромное количество лишнего кода.

---

## 54. Notification не является общей системой автоматизации

Плохая идея — складывать в Notification всё подряд:

```text
изменить пять полей
создать три документа
назначить исполнителя
перестроить workflow
вызвать внешнюю систему
```

Технически некоторые цепочки можно построить косвенно.

Но Notification создан прежде всего для:

```text
оповещения
```

а не как универсальный workflow engine.

---

# Где заканчивается штатная настройка

## 55. Сначала используем стандартный Notification

Если требование выглядит так:

```text
при событии X
если условие Y
сообщить Z
```

обычно сначала проверяем Notification.

Например:

```text
за 2 дня до due_date
→ всем assignees
→ отправить email
```

Это штатный сценарий.

---

## 56. Код нужен, когда событие само по себе нестандартное

Например:

> отправить уведомление только после успешного расчёта сложного алгоритма собственного App.

Тогда уже может быть естественная схема:

```text
App code
   ↓
сложная бизнес-операция завершена
   ↓
Custom Notification.queue_send(doc)
```

В таком случае Notification всё ещё полезен как конфигурация:

```text
кому
какой текст
каким каналом
```

а решение **когда именно** вызвать его остаётся в коде приложения.

---

# Полный пример

## 57. Напоминание об открытой заявке

Есть:

```text
Request
├── subject
├── status
├── due_date
└── owner
```

Требование:

> за один день до срока, если Request ещё не Closed, отправить Email всем текущим исполнителям.

Notification:

```text
Enabled: Yes
Channel: Email
Document Type: Request
Send Alert On: Days Before
Reference Date: due_date
Days Before or After: 1
Send To All Assignees: Yes
```

Condition:

```python
doc.status != "Closed"
```

Subject:

```jinja2
Request {{ doc.name }} is due tomorrow
```

Message:

```jinja2
<p>{{ doc.subject }}</p>
<p>Due date: {{ doc.due_date }}</p>
```

Получаем:

```text
scheduler
   ↓
завтра due_date?
   ↓ да
status != Closed?
   ↓ да
найти Open ToDo
   ↓
получить assignees
   ↓
отправить Email
```

Ни собственного cron, ни собственного списка получателей для такого сценария писать не требуется.

---

# Мини-практика

## 58. Практика 1 — System Notification на новый Request

Создай Notification:

```text
Name: New Request Created
Enabled: Yes
Channel: System Notification
Document Type: Request
Send Alert On: New
```

Получатель:

```text
Receiver By Document Field: owner
```

Заголовок:

```jinja2
Request {{ doc.name }} created
```

Сообщение:

```jinja2
{{ doc.subject }}
```

Создай новый Request.

Проверь внутреннее уведомление пользователя.

---

## 59. Практика 2 — Value Change

Создай второе правило:

```text
Document Type: Request
Send Alert On: Value Change
Value Changed: status
```

Condition:

```python
doc.status == "Closed"
```

Теперь проверь два изменения:

```text
Open → In Progress
```

и:

```text
In Progress → Closed
```

Уведомление должно соответствовать не просто сохранению документа, а выбранному изменению поля плюс Condition.

---

## 60. Практика 3 — Filters вместо Python

Возьми правило, которое должно срабатывать при:

```text
status = Open
priority = High
```

Вместо Python Condition выбери:

```text
Condition Type: Filters
```

и собери два фильтра через UI.

Цель практики — увидеть, что для простых условий код выражения уже не обязателен.

---

## 61. Практика 4 — Days Before

Если у `Request` есть:

```text
due_date
Date
```

создай:

```text
Send Alert On: Days Before
Reference Date: due_date
Days Before or After: 1
```

Сохрани правило и используй:

```text
Get Alerts for Today
```

чтобы проверить выборку без ожидания реального следующего дня.

---

# Что запомнить

## 62. Семь основных мыслей

### 1.

Notification — это правило:

```text
event + condition + recipients + message
```

### 2.

Notification не заменяет:

```text
Assignment
Workflow
permissions
```

### 3.

В v16 штатные каналы:

```text
Email
Slack
System Notification
SMS
```

### 4.

Основные события включают не только lifecycle, но и:

```text
Value Change
Days Before / After
Minutes Before / After
Method
Custom
```

### 5.

Для простых условий в v16 можно использовать:

```text
Filters
```

а не сразу Python expression.

### 6.

Получатели могут определяться через:

```text
поле Document
Role
assignees
```

### 7.

Если логика звучит как:

```text
при X сообщить Y
```

сначала проверяй Notification.

Если она звучит как:

```text
выполнить сложную бизнес-операцию
```

скорее всего нужен уже другой механизм.

---

# Источники

- Frappe Framework — Notifications: https://docs.frappe.io/framework/notifications
- Frappe Framework — Controllers: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
- Frappe Framework `version-16` — `frappe/email/doctype/notification/notification.json`
- Frappe Framework `version-16` — `frappe/email/doctype/notification/notification.py`
- Frappe Framework `version-16` — `frappe/email/doctype/notification/notification.js`
- Frappe Framework `version-16` — `frappe/email/doctype/notification_recipient/notification_recipient.json`
- Frappe Framework `version-16` — `frappe/model/document.py`

---

Предыдущая глава: **26. Workflow и переходы**.

Следующая глава: **28. Auto Repeat**.
