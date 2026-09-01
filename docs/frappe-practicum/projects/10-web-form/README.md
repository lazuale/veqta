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

# 1. Preconditions: Desk security уже построена

После L5/L7 обычный Desk path защищён так:

```text
Level 0
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No

Level 1 business content
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write

status      → Level 0 + Workflow
```

На Level 1 находятся:

```text
subject
location
equipment
description
priority
target_date
attachment
```

L10 не имеет права незаметно разрушить эту модель.

---

# 2. Два разных create-path

## Desk create

```text
requester.one@example.com
→ Level 0 Create = Yes
→ Level 1 Write позволяет заполнить content
→ ordinary Document insert
```

Здесь Role Permission и Permission Level являются частью enforcement.

## Web Form create

В exact `v16.32.0` новый target Document Web Form вставляется так:

```text
doc.insert(ignore_permissions=True, ...)
```

Поэтому:

```text
Web Form submit
≠ proof Role Permission Create
≠ proof Permission Level enforcement
```

`Apply Document Permissions` не превращает новый Web Form insert в обычный Desk create-path.

---

# 3. Threat model финального intake

Финальная форма:

```text
Published = Yes
Login Required = Yes
Anonymous Responses = No
```

`Login Required` означает:

```text
Guest submit запрещён
```

но это не отдельный role gate вида:

```text
только Facility Requester может submit
```

Deployment policy курса:

```text
authenticated website accounts,
которым доступна эта опубликованная форма,
считаются доверенными внутренними заявителями
```

Role-restricted/public-untrusted intake — Later.

---

# 4. Почему final Allow Edit обязательно выключен

В `v16.32.0` разрешённый Web Form update может сохраняться через:

```text
doc.save(ignore_permissions=True)
```

Это принципиально сильнее обычного Desk path:

```text
ignore_permissions=True
→ нельзя считать Level 0/Level 1 Role Permission enforcement
```

Поэтому Web Form нельзя оставлять parallel editor рабочего `Service Request`.

Финал:

```text
Allow Editing After Submit = No
```

Это защищает не только Workflow semantics, но и Level 1 content boundary.

---

# 5. Проверить стенд

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
New Service Request
```

---

# 6. Web Form не создаёт второй бизнес-процесс

Работаем с тем же:

```text
Service Request
```

Не создаём `Public Request`, `Portal Ticket` и другие дубли.

Web Form — канал создания, а не новая бизнес-сущность.

---

# 7. Создать Standard Web Form

```text
Title:          Report a Facility Issue
Route:          facility-request
Select DocType: Service Request
Module:         Facility Operations
Is Standard:    Yes
```

Generated `.json/.js/.py` boilerplate не редактируем.

---

# 8. Поля Web Form

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

Web Form обязана создавать Document, совместимый с H-01 L4, даже несмотря на `ignore_permissions=True` create path.

---

# 9. Базовый вид

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

# 10. Временный Guest experiment

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

# 11. Guest submission

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

Проверить:

```text
Location = Main Site
Status = New
Description заполнен
```

Этот тест показывает отдельную capability Web Form, а не Guest Role Permission.

После теста Guest mode обязательно выключить.

---

# 12. Mandatory tests

Получить отказ минимум:

```text
без Subject
без Description
```

Не включать `Allow incomplete forms`.

---

# 13. Перейти к authenticated mode

Вернуть:

```text
Anonymous responses: No
Login required:      Yes
Allow multiple:      Yes
Show list:           Yes
Show attachments:    Yes
Allow Edit:          No
```

---

# 14. Вернуть Location и Equipment

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

`Description` остаётся Mandatory.

---

# 15. Link options и trust boundary

Без `Allow Read On All Link Options` login-required Web Form по exact source по умолчанию owner-фильтрует Link options.

Для общих Location/Equipment включаем:

```text
Allow Read On All Link Options = Yes
```

Это сознательно раскрывает authenticated Website Users названия этих справочников.

Допустимо только в threat model:

```text
trusted internal reporter
```

---

# 16. Создать Website User

```text
Email:              web.requester@example.com
First Name:         Web Requester
User Type:          Website User
Enabled:            Yes
Send Welcome Email: No
```

Не выдавать `Facility Requester` только ради Web Form.

Это позволяет доказать:

```text
Web Form submission
≠ Desk Role Permission Create
```

---

# 17. Проверить Login Required

Guest больше не должен submit final form.

Войти `web.requester@example.com` — форма должна открыться.

---

# 18. Создать authenticated заявку

```text
Subject:     Website user request
Location:    Warehouse
Equipment:   логично подходящий Equipment или пусто
Description: Authenticated Web Form intake test
Priority:    Medium
Target Date: будущая дата или пусто
Attachment:  тестовый файл
```

Проверить:

```text
Owner = web.requester@example.com
Status = New
```

Website User не имеет `Facility Requester`, но insert проходит через Web Form capability. Это ожидаемое штатное поведение.

Assignment Rule может создать ToDo, но Status остаётся New.

---

# 19. Show List как read-path

Под Website User открыть список responses.

Рекомендуемые columns:

```text
Subject
Priority
Status
Target Date
```

Show List сам по себе не даёт edit.

---

# 20. Временно изучить Allow Edit

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
Web Form update
может идти отдельно от Desk Role Permission
и Level 1 field protection
```

Это именно причина не оставлять его включённым.

---

# 21. Обязательный rollback Allow Edit

Сразу вернуть:

```text
Allow editing after submit = No
```

После этого owner может иметь read-path, но Web Form update должен быть запрещён.

---

# 22. Owner boundary

Website User не должен получить чужой response только потому, что знает `name`.

Проверить другой owner через Web Form route.

---

# 23. Apply Document Permissions

Временно включить:

```text
Apply document permissions = Yes
```

Проверять нужно **existing-document access**, не creation.

Фиксируем:

```text
OFF
→ Web Form owner/website permission model

ON
→ ordinary document permission model для existing doc
```

Но new insert всё равно не становится ordinary Role Permission Create.

После теста вернуть:

```text
Apply document permissions = No
Allow editing after submit = No
```

---

# 24. Сравнить System User Desk Create и Web Form Create

Под `requester.one@example.com` сделать два теста.

## A. Desk

Создать новую заявку через Desk.

Это proof:

```text
Level 0 Create = Yes
Level 1 Write позволяет заполнить content
```

После Save:

```text
Level 0 Write = No
```

## B. Web Form

Создать вторую заявку через `/facility-request`.

Это proof только:

```text
authenticated Web Form intake работает
```

Не смешивать два результата.

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

```text
Role Permission Level 0/1
→ ordinary Desk path

Web Form Published/Login Required
→ Web Form admission boundary

Web Form new insert
→ ignore_permissions=True
→ separate capability

Allow Edit = No
→ closes Web Form update path

Workflow
→ process after creation
```

Нельзя выдавать Web Form authentication за role authorization или Web Form insert за proof Permission Level enforcement.

---

# 28. Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
find facility_ops/facility_operations -type f | sort | grep -i 'web_form\|facility_request'
```

Standard Web Form входит в app source.

Runtime Users/Requests/Files — нет.

---

# 29. State contract L10

## Preconditions

```text
L5 Level 0 + Level 1 permission model
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

## Output

```text
Desk security model remains intact
Web Form create is separate authenticated intake path
final Web Form is create/read-only
no persistent ignore_permissions update path
```

---

# 30. Приёмка L10

L10 принят, если:

- ученик различает Desk Create и Web Form insert;
- Website User без `Facility Requester` создаёт Service Request через Web Form;
- это не называется доказательством Role Permission или Permission Level;
- Guest experiment выполнен и выключен;
- final `Login Required = Yes`;
- Login Required не трактуется как role-specific authorization;
- Mandatory L4 сохранены;
- Link catalog disclosure объяснено;
- Show List работает как read-path;
- `Allow Edit` изучен и возвращён в `No`;
- объяснено, что `ignore_permissions=True` Web Form update обходил бы обычную Level 1 protection;
- `Apply Document Permissions` проверен только как existing-document mechanism и возвращён в `No`;
- `Status` не управляется из Web Form;
- процесс использует `Accept`;
- Git содержит Standard Web Form, но не runtime data.

После L10 переходим к **L11 — переносимость**.
