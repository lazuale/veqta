# L10. Web Form

L10 добавляет authenticated Web Form как **отдельный intake-channel** поверх существующего `Service Request`.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

## Итоговая архитектура

```text
trusted authenticated Website User
        ↓
Report a Facility Issue
        ↓ Web Form insert
Service Request / Status = New
        ↓
Assignment Rule / Desk Workflow
```

Финальная Web Form:

```text
создаёт новые Service Request
показывает собственные responses
не редактирует Service Request после submit
```

---

# 1. Два разных create-path

После L10 в приложении существуют два штатных способа создать `Service Request`.

## Desk create

```text
requester.one@example.com
→ Role Permission Create = Yes
→ обычный Document insert
```

Здесь `Create` контролируется Role Permission.

## Web Form create

В exact `v16.32.0` новый Web Form Document вставляется так:

```text
doc.insert(ignore_permissions=True, ...)
```

То есть Web Form insert **не является доказательством DocType Create permission**.

Его admission boundary задают настройки самой Web Form, в частности:

```text
Published
Login Required
Web Form route
```

Это фундаментальная академическая граница L10:

```text
Desk Create permission
≠ Web Form submission permission
```

`Apply Document Permissions` не превращает новый Web Form insert в обычный Role Permission `Create` check.

---

# 2. Threat model финального intake

Финальная форма курса:

```text
Published = Yes
Login Required = Yes
Anonymous Responses = No
```

`Login Required` означает:

```text
Guest submit запрещён
```

но это **не отдельный role gate** вида:

```text
только Facility Requester может submit
```

В базовом Web Form курса такого утверждения нет.

Поэтому deployment policy:

```text
аккаунты, которым разрешён authenticated website access,
считаются доверенными внутренними заявителями
```

Если нужен отдельный список ролей/групп, которым разрешено именно создание через внешний канал, это требует иной специально спроектированной portal/permission архитектуры и относится к Later.

---

# 3. Почему final Allow Edit выключен

В `v16.32.0` Web Form при owner-based доступе и:

```text
Apply Document Permissions = No
```

может сохранить разрешённый update через:

```text
doc.save(ignore_permissions=True)
```

Поэтому Web Form нельзя оставлять параллельным редактором рабочего Workflow Document.

Финал:

```text
Allow Editing After Submit = No
```

`Only Allow Edit For` Workflow не используется как оправдание: это Desk guard, не универсальная server ACL такого update path.

---

# 4. Проверить стенд

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps
bench --site facility-ops.localhost scheduler status

cd apps/facility_ops
git status
```

Должны работать:

```text
Service Request Workflow
Service Request Auto Assignment
New Service Request Notification
```

Workflow states:

```text
New
Accepted
In Progress
Resolved
Closed
```

---

# 5. Web Form не создаёт второй бизнес-процесс

Работаем с тем же:

```text
Service Request
```

Не создаём:

```text
Public Request
External Request
Portal Ticket
Website Request
```

Web Form — новый **канал создания**, а не новая бизнес-сущность.

---

# 6. Создать Standard Web Form

```text
Title:          Report a Facility Issue
Route:          facility-request
Select DocType: Service Request
Module:         Facility Operations
Is Standard:    Yes
```

Standard Web Form экспортируется в app source.

Generated `.json/.js/.py` boilerplate не редактируем.

---

# 7. Поля Web Form

| Field | Настройка |
|---|---|
| Subject | Mandatory |
| Location | Mandatory |
| Equipment | Optional |
| Description | Mandatory |
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

Web Form должна создавать Document, совместимый с H-01 L4.

---

# 8. Базовый вид

```text
Introduction:
Describe the problem and, if possible, attach a photo or document.

Submit button:
Create Request

Success title:
Request created

Success message:
Your request has been registered.

Max attachment size:
5 MB
```

Не добавлять Client Script / Custom CSS.

---

# 9. Временный Guest experiment

Только для изучения механизма временно:

```text
Published:                  Yes
Anonymous responses:        Yes
Login required:             No
Apply document permissions: No
Allow editing after submit: No
Allow multiple responses:   No
Show list:                  No
```

Чтобы Guest не получил внутренние Link catalogs:

## Location

```text
Hidden:    Yes
Mandatory: Yes
Default:   Main Site
```

## Equipment

```text
скрыть / временно убрать
```

---

# 10. Guest submission

Незалогиненным открыть:

```text
http://facility-ops.localhost:8000/facility-request
```

Создать:

```text
Subject:     Guest web form test
Description: Public Web Form creation test
Priority:    High
Target Date: будущая дата или пусто
Attachment:  небольшой тестовый файл
```

Проверить в Desk:

```text
Location = Main Site
Status = New
Description заполнен
```

Важно понять: этот тест специально демонстрирует, что опубликованная Web Form может быть самостоятельным create-channel, даже когда Guest не имеет обычной Desk Role Permission на `Service Request`.

После теста Guest mode обязательно выключаем.

---

# 11. Mandatory tests

Получить отказ минимум:

```text
без Subject
без Description
```

Не включать `Allow incomplete forms`.

---

# 12. Перейти к authenticated mode

Вернуть:

```text
Anonymous responses: No
Login required:      Yes
Allow multiple:      Yes
Show list:           Yes
Show attachments:    Yes
```

`Allow Edit` пока остаётся `No`.

---

# 13. Вернуть Location и Equipment

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

Description:

```text
Mandatory = Yes
```

---

# 14. Link options и trust boundary

При login-required Web Form без `Allow Read On All Link Options` exact source по умолчанию фильтрует Link options по:

```text
owner = current user
```

Для общих `Facility Location` / `Equipment` это неудобно, поэтому включаем:

```text
Allow Read On All Link Options = Yes
```

Тем самым сознательно раскрываем authenticated Website Users названия этих справочников.

Это допустимо только в принятом threat model:

```text
trusted internal reporter
```

---

# 15. Создать Website User

```text
Email:              web.requester@example.com
First Name:         Web Requester
User Type:          Website User
Enabled:            Yes
Send Welcome Email: No
```

Не выдавать ему `Facility Requester` только ради Web Form.

Именно это позволяет доказать:

```text
Web Form submission
≠ Role Permission Create
```

---

# 16. Проверить Login Required

Guest больше не должен получать возможность submit authenticated final form.

Войти:

```text
web.requester@example.com
```

Форма должна открыться.

---

# 17. Создать authenticated заявку

```text
Subject:     Website user request
Location:    Warehouse
Equipment:   логично подходящий Equipment или пусто
Description: Authenticated Web Form intake test
Priority:    Medium
Target Date: будущая дата или пусто
Attachment:  тестовый файл
```

Проверить в Desk:

```text
Owner = web.requester@example.com
Status = New
```

Website User не имеет `Facility Requester`, но insert проходит через Web Form intake path. Это ожидаемое, а не обходное поведение.

Assignment Rule может создать ToDo, но Status остаётся `New`.

---

# 18. Show List как read-path

Под Website User открыть список responses.

Рекомендуемые columns:

```text
Subject
Priority
Status
Target Date
```

Show List не даёт право edit сам по себе.

---

# 19. Временно изучить Allow Edit

На отдельной новой заявке временно:

```text
Allow editing after submit = Yes
Apply document permissions = No
```

Под owner изменить:

```text
Description
```

Проверить изменение в Desk.

Фиксируем:

```text
Web Form owner permission
может разрешать update отдельно от Desk Role Permission
```

---

# 20. Обязательный rollback Allow Edit

Сразу вернуть:

```text
Allow editing after submit = No
```

Причина:

```text
Web Form
не должен оставаться вторым editor path
после Accept / Start Work / Resolve
```

---

# 21. Проверить final update rejection

Под Website User открыть собственный response.

Read может работать через Show List/view route, но update после:

```text
Allow editing after submit = No
```

должен быть запрещён.

---

# 22. Owner boundary

Website User не должен получить чужой response только потому, что знает `name`.

Проверить попытку открыть Document другого owner через Web Form route.

---

# 23. Что реально делает Apply Document Permissions

Временно включить:

```text
Apply document permissions = Yes
```

Проверять нужно **доступ к уже существующему Document**, а не создание нового.

У `web.requester@example.com` нет Desk Role Permission на `Service Request`, поэтому owner-based Web Form read convenience при этом меняется на обычную document permission model.

Фиксируем:

```text
Apply Document Permissions
→ влияет на existing-document permission path

Apply Document Permissions
≠ включить Role Permission Create для Web Form insert
```

После теста вернуть:

```text
Apply document permissions = No
Allow editing after submit = No
```

---

# 24. Сравнить System User Desk Create и Web Form Create

Под:

```text
requester.one@example.com
```

сделать два разных теста.

## A. Desk

Создать новую заявку через Desk.

Это proof:

```text
Facility Requester Create = Yes
```

После Save Requester не должен иметь Write по L5.

## B. Web Form

Создать вторую корректную заявку через `/facility-request`.

Это proof:

```text
authenticated Web Form intake работает
```

Но **не** повторное доказательство Role Permission Create, потому что Web Form insert использует собственный permission-bypassing create path.

Не смешивать эти два результата.

---

# 25. Web Form не управляет Workflow

После любого Web Form insert:

```text
Status = New
```

Дальше:

```text
Assignment Rule → ToDo
Supervisor → Accept
Technician → Start Work
Technician → Resolve
Supervisor → Close
```

`Status` отсутствует как editable Web Form field.

---

# 26. Final configuration

Оставить:

```text
Title:        Report a Facility Issue
Route:        facility-request
DocType:      Service Request
Published:    Yes
Is Standard:  Yes
Module:       Facility Operations

Anonymous responses:         No
Login required:              Yes
Allow multiple responses:    Yes
Allow editing after submit:  No
Show list:                   Yes
Apply document permissions:  No
Show attachments:            Yes
```

Fields:

```text
Subject     Mandatory
Location    Mandatory + Allow Read On All Link Options
Equipment   Optional  + Allow Read On All Link Options
Description Mandatory
Priority    Mandatory
Target Date Optional
Attachment  Optional
```

`Status` отсутствует.

---

# 27. Enforcement map L10

## Hard

```text
Published required for live Web Form API/page
Login Required blocks Guest in final mode
Mandatory validation
Allow Edit = No rejects update
```

## Separate intake capability

```text
new Web Form insert
→ doc.insert(ignore_permissions=True)
→ не является Role Permission Create check
```

## Existing-document permission path

```text
Apply Document Permissions = Off
→ Web Form owner/website permission model

Apply Document Permissions = On
→ ordinary document permission model
```

## Deployment policy

```text
authenticated website accounts with access to this published form
= trusted internal intake population
```

Не называть authentication role-based authorization.

---

# 28. Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -i 'web_form\|facility_request'
```

Standard Web Form входит в app source.

Runtime Users/Requests/Files — нет.

---

# 29. State contract L10

## Preconditions

```text
L5 hardened Role Permission model
L7 Workflow Accepted/Accept
L9 Assignment Rule active on main site
```

## Temporary

```text
Guest mode
Allow Edit = Yes
Apply Document Permissions = Yes
```

## Rollback

```text
Anonymous = No
Login Required = Yes
Allow Edit = No
Apply Document Permissions = No
```

## Persistent

```text
Standard Web Form
Website User site record
trusted-internal intake policy
```

## Output

```text
Desk Requester create remains Role Permission path
Web Form create is separate authenticated intake path
final Web Form is create/read-only
```

---

# 30. Приёмка L10

L10 принят, если:

- ученик различает Desk Create и Web Form insert;
- доказано, что Website User без `Facility Requester` создаёт Service Request через Web Form;
- это не называется доказательством Role Permission Create;
- Guest experiment выполнен и выключен;
- final `Login Required = Yes`;
- Login Required не трактуется как role-specific authorization;
- Website User понимается как trusted internal reporter;
- Mandatory L4 сохранены;
- Link catalog disclosure объяснено;
- Show List работает как read-path;
- `Allow Edit` изучен и возвращён в `No`;
- `Apply Document Permissions` проверен на existing-document access и возвращён в `No`;
- `Apply Document Permissions` не приписывается к create authorization;
- `Status` не управляется из Web Form;
- процесс использует `Accept`;
- Git содержит Standard Web Form, но не runtime data.

После L10 переходим к **L11 — переносимость**.
