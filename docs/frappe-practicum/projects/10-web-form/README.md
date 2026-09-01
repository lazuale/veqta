# L10. Web Form

L10 открывает внешний веб-вход в уже существующий `Service Request`.

Новых предметных DocType нет.

Цель урока:

```text
Browser
  ↓
Web Form
  ↓
Service Request
  ↓
Assignment Rule / Workflow
  ↓
Desk
```

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Проверить стенд

В терминале:

```bash
cd ~/frappe/facility-ops-bench

bench version
bench --site facility-ops.localhost list-apps
bench --site facility-ops.localhost scheduler status

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

На site уже должны работать:

```text
Service Request Workflow
Assignment Rule
Notification
```

---

# 2. Не создавать отдельный внешний процесс

Web Form не получает свой DocType.

Используем тот же:

```text
Service Request
```

То есть внешний пользователь создаёт обычный Document, который затем виден в Desk и участвует в тех же механизмах:

```text
Naming
Workflow
Assignment Rule
Notification
Timeline
Permissions
```

Не создаём:

```text
Public Request
External Request
Website Request
Portal Ticket
```

---

# 3. Создать Standard Web Form

Войти под:

```text
Administrator
```

Developer Mode должен быть включён.

Через Awesomebar открыть:

```text
Web Form
```

Создать:

```text
Title:       Report a Facility Issue
Route:       facility-request
Select DocType: Service Request
Module:      Facility Operations
Is Standard: Yes
```

Сохранить.

Standard Web Form в Developer Mode экспортируется в app.

Frappe также создаёт рядом штатные boilerplate-файлы `.js` и `.py` для Web Form.

Их в базовом курсе не редактируем.

---

# 4. Настроить поля формы

Добавить в `Web Form Fields`:

| Field | Настройка |
|---|---|
| Subject | Mandatory |
| Location | Mandatory |
| Equipment | Optional |
| Description | Optional |
| Priority | Mandatory |
| Target Date | Optional |
| Attachment | Optional |

Не добавлять:

```text
Status
Owner
Modified
Assigned To
```

`Status` получает default `New` из `Service Request` и дальше управляется Workflow.

Исполнитель назначается штатным Assignment Rule.

---

# 5. Настроить базовый вид

Для формы задать:

```text
Introduction:
Describe the problem and, if possible, attach a photo or document.

Submit button label:
Create Request

Success title:
Request created

Success message:
Your request has been registered.

Max attachment size:
5 MB
```

Не добавлять Client Script или Custom CSS.

---

# 6. Первый режим: публичный Guest

Сначала проверяем максимально простой внешний сценарий.

Настроить:

```text
Published:            Yes
Anonymous responses:  Yes
Login required:       No
Apply document permissions: No
Allow editing after submit: No
Allow multiple responses:   No
Show list:            No
```

Для публичного теста не раскрываем справочники Equipment и Location.

В `Web Form Fields` временно:

## Location

```text
Hidden:    Yes
Mandatory: Yes
Default:   Main Site
```

## Equipment

временно удалить из Web Form Fields или скрыть без обязательности.

Остальные поля оставить видимыми.

Причина простая:

```text
Guest submission
не должен автоматически превращать внутренние справочники
Location / Equipment в публичный каталог
```

---

# 7. Проверить Guest submission

Выйти из Frappe.

Открыть в браузере:

```text
http://facility-ops.localhost:8000/facility-request
```

Web Form должен открыть страницу создания заявки.

Создать:

```text
Subject:     Guest web form test
Description: Public web form submission
Priority:    High
Target Date: <любая будущая дата>
Attachment:  небольшой тестовый файл
```

Нажать:

```text
Create Request
```

Ожидается success message.

---

# 8. Проверить результат в Desk

Войти под Administrator или Supervisor.

Открыть:

```text
Service Request
```

Найти созданную заявку.

Проверить:

```text
Subject     = Guest web form test
Location    = Main Site
Priority    = High
Status      = New
Attachment  = загружен
```

При `Anonymous responses = Yes` Document должен быть создан как анонимный web-form response.

Главное:

```text
Web Form
не хранит отдельную копию заявки
```

Создан обычный `Service Request`.

---

# 9. Проверить автоматизацию L9

На той же заявке проверить:

```text
Assignment Rule
→ создал ToDo

Target Date
→ попал в Due Date ToDo

Notification
→ отработала по настройкам L9
```

Статус остаётся:

```text
New
```

до отдельного Workflow Action.

То есть:

```text
Web Form = канал создания
Assignment = кто делает
Workflow = состояние процесса
```

---

# 10. Проверить обязательное поле

В Guest Web Form попробовать отправить форму без:

```text
Subject
```

Отправка должна быть заблокирована.

Затем вернуть корректное значение и отправить.

Не включать `Allow incomplete forms` ради обхода Mandatory.

---

# 11. Проверить attachment

Создать ещё одну тестовую заявку с небольшим файлом.

После сохранения проверить в Desk:

```text
Service Request.attachment
```

и наличие File, связанного с Document.

Затем попробовать файл больше установленного ограничения, если это удобно на стенде.

Frappe должен применить лимит Web Form / site.

---

# 12. Перевести форму в финальный режим Login Required

Вернуться под Administrator.

Изменить Web Form:

```text
Anonymous responses: No
Login required:      Yes
Allow multiple responses: Yes
Allow editing after submit: Yes
Show list:           Yes
Apply document permissions: No
Show attachments:   Yes
```

Финальная форма курса требует входа пользователя.

---

# 13. Вернуть Location и Equipment

В Web Form Fields:

## Location

```text
Hidden:    No
Mandatory: Yes
Default:   <пусто>
Allow Read On All Link Options: Yes
```

## Equipment

```text
Hidden:    No
Mandatory: No
Allow Read On All Link Options: Yes
```

Почему включаем `Allow Read On All Link Options`:

при `Login Required` Frappe по умолчанию ограничивает Link options значениями, owner которых совпадает с текущим пользователем.

Для справочников:

```text
Facility Location
Equipment
```

это в нашем учебном приложении не подходит: пользователь не является owner справочника только потому, что создаёт заявку.

Настройка разрешает Web Form читать все options конкретного Link-поля.

Не путать это с полным доступом пользователя к DocType в Desk.

---

# 14. Создать Website User

Через Awesomebar открыть:

```text
User
```

Создать:

```text
Email:      web.requester@example.com
First Name: Web Requester
User Type:  Website User
Enabled:    Yes
Send Welcome Email: No
```

Задать учебный пароль.

Не выдавать:

```text
System Manager
Desk User
Administrator
```

Для основной проверки Web Form отдельная роль не нужна.

---

# 15. Проверить Login Required

Выйти из системы.

Открыть:

```text
http://facility-ops.localhost:8000/facility-request
```

Незалогиненный Guest не должен получить обычную форму создания.

Войти как:

```text
web.requester@example.com
```

После входа открыть тот же route.

Форма должна стать доступной.

---

# 16. Создать заявку как Website User

Создать:

```text
Subject:     Website user request
Location:    Room 101
Equipment:   <любое Equipment из Room 101 или пусто>
Description: Authenticated Web Form test
Priority:    Medium
Target Date: <будущая дата>
Attachment:  тестовый файл
```

Сохранить.

Проверить в Desk:

```text
Owner = web.requester@example.com
Status = New
```

и нормальную работу Assignment Rule.

---

# 17. Проверить Show List

Под `web.requester@example.com` открыть route списка Web Form.

При `Show List = Yes` пользователь должен получить список своих доступных ответов.

Для List Columns оставить минимум:

```text
Subject
Priority
Status
Target Date
```

Не превращать Web Form List в копию Desk List View.

---

# 18. Проверить Allow Edit

Открыть созданную Website User заявку через Web Form.

При:

```text
Allow editing after submit = Yes
Apply document permissions = No
```

owner документа может работать со своим ответом через Web Form.

Изменить:

```text
Description
```

Сохранить.

Проверить то же изменение в Desk.

---

# 19. Доказать owner-границу

Под Administrator заранее создать или найти Service Request другого owner.

Под:

```text
web.requester@example.com
```

попробовать открыть чужой Document через Web Form URL.

Он не должен стать доступным только потому, что пользователь знает его `name`.

При `Apply document permissions = No` базовое правило Web Form для обычного logged-in пользователя:

```text
свой Document
→ доступен

чужой Document
→ не доступен без отдельного website permission
```

---

# 20. Проверить Apply Document Permissions

Теперь временно включить:

```text
Apply document permissions = Yes
```

Под `web.requester@example.com` снова проверить доступ к созданному им Service Request.

Website User не имеет нашей Desk role / DocType permission matrix из L5, поэтому поведение должно измениться согласно обычным permissions `Service Request`.

Это и есть смысл настройки:

```text
OFF
→ Web Form использует собственную owner/website permission модель

ON
→ Web Form проверяет обычные document permissions
```

После проверки вернуть:

```text
Apply document permissions = No
```

Финальный authenticated Web Form курса использует owner-based access.

---

# 21. Проверить System User отдельно

Войти как:

```text
requester.one@example.com
```

Открыть тот же Web Form.

Создать заявку.

Затем временно включить:

```text
Apply document permissions = Yes
```

Проверить, что для `Facility Requester` начинают применяться права L5, включая `If Owner`.

После проверки вернуть финальную настройку:

```text
Apply document permissions = No
```

---

# 22. Не давать Web Form управлять Workflow

В Web Form Fields не должно быть editable поля:

```text
Status
```

Website User не переводит заявку напрямую:

```text
New → Assigned
New → Closed
```

После создания заявка входит в обычный Desk-процесс:

```text
Web Form submission
      ↓
New
      ↓
Supervisor Workflow Action
      ↓
Assigned
      ↓
Technician
```

Web Form не становится вторым Workflow UI.

---

# 23. Проверить Standard Web Form в Git

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Найти exported Web Form:

```bash
find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -i 'web_form\|facility_request'
```

Ожидаются app-owned файлы Standard Web Form.

Frappe может создать рядом boilerplate:

```text
.json
.js
.py
```

В базовом курсе `.js` и `.py` не редактируем.

Их наличие не означает, что мы написали собственную бизнес-логику.

---

# 24. Проверить границу source и data

После L10:

```text
Web Form definition
→ app source
→ Git

Service Request created through Web Form
→ database site
→ не Git

Website User
→ configuration/data site
→ не source приложения автоматически
```

Пользователя не экспортируем как fixture.

---

# 25. Финальная конфигурация Web Form

Оставить:

```text
Title:        Report a Facility Issue
Route:        facility-request
DocType:      Service Request
Published:    Yes
Is Standard:  Yes
Module:       Facility Operations

Anonymous responses: No
Login required:      Yes
Allow multiple responses: Yes
Allow editing after submit: Yes
Show list:           Yes
Apply document permissions: No
Show attachments:   Yes
```

Поля:

```text
Subject
Location
Equipment
Description
Priority
Target Date
Attachment
```

Location и Equipment:

```text
Allow Read On All Link Options = Yes
```

Status в Web Form отсутствует.

---

# 26. Commit L10

Проверить:

```bash
git status
git diff
```

Добавить exported Standard Web Form:

```bash
git add .
git diff --cached
```

Проверить, что staged diff не содержит рабочих Service Request, паролей или пользовательских данных.

Commit:

```bash
git commit -m "Add service request web form"
git status
```

Ожидается:

```text
working tree clean
```

---

# 27. Самостоятельная практика

Без подсказки выполнить три проверки.

## A. Guest

Временно открыть Web Form для Guest, спрятать Location с default `Main Site`, создать заявку и вернуть Login Required.

## B. Website User

Создать второй Service Request и открыть оба через Show List.

## C. Permissions

Переключить `Apply document permissions` и объяснить, почему один и тот же пользователь получает разный результат.

После проверки вернуть финальную конфигурацию из раздела 25.

---

# 28. Приёмка L10

L10 принят, если ученик может показать:

## Web Form

```text
Report a Facility Issue
Route = facility-request
DocType = Service Request
Standard = Yes
Published = Yes
```

## Guest test

```text
Guest смог создать временную публичную заявку
создан обычный Service Request
attachment дошёл до Document
```

## Website User

```text
Login Required работает
Website User создаёт Service Request
Show List показывает доступные ответы
Allow Edit позволяет изменить свой ответ
```

## Permissions

Ученик может объяснить:

```text
Apply document permissions OFF
≠
Apply document permissions ON
```

## Integration

Заявка из Web Form проходит через уже существующие:

```text
Assignment Rule
Notification
Workflow
```

## Архитектура

По-прежнему только три предметных DocType:

```text
Facility Location
Equipment
Service Request
```

---

# Что нужно понять после L10

```text
Web Form
= внешний интерфейс над существующим DocType
```

Он не требует второго backend-процесса.

```text
Guest / Website User / System User
```

— разные контексты доступа к одной и той же форме.

```text
Login Required
```

определяет необходимость аутентификации.

```text
Allow Edit / Show List
```

дают web-пользователю работу с ранее созданными ответами.

```text
Apply Document Permissions
```

определяет, будет ли Web Form опираться на обычные permissions DocType или на собственную web-form access модель.

```text
Web Form submission
→ обычный Document
```

поэтому вся остальная штатная механика Frappe продолжает работать без дублирования.

---

Следующий урок:

```text
L11 — Переносимость приложения
```
