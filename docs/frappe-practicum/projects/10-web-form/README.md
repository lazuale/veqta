# L10. Web Form

L10 открывает внешний authenticated-вход в существующий `Service Request`.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

## Итоговая архитектура

```text
Trusted internal Website User
        ↓
Report a Facility Issue
        ↓ create
Service Request / Status = New
        ↓
Assignment Rule / Desk Workflow
```

Финальная Web Form **не является редактором рабочего Service Request после создания**.

```text
Allow Editing After Submit = No
```

Это сознательная security boundary курса.

---

# 1. Почему final Allow Edit выключен

В `v16.32.0` Web Form при owner-based доступе и:

```text
Apply Document Permissions = No
```

может считать owner достаточным web-form permission и сохранить update через:

```text
doc.save(ignore_permissions=True)
```

Поэтому модель:

```text
Website User
→ может редактировать заявку на любой стадии Workflow
```

не является безопасной no-code архитектурой.

`Only Allow Edit For` Workflow не используем как оправдание: это не отдельная универсальная server ACL для такого update path.

В L10 `Allow Edit` будет **временно изучен**, затем обязательно выключен до финальной приёмки.

---

# 2. Проверить стенд

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

Workflow states:

```text
New
Accepted
In Progress
Resolved
Closed
```

---

# 3. Web Form не создаёт второй процесс

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

Один Document участвует в тех же Naming, Assignment, Workflow, Timeline и Reporting.

---

# 4. Создать Standard Web Form

```text
Title:          Report a Facility Issue
Route:          facility-request
Select DocType: Service Request
Module:         Facility Operations
Is Standard:    Yes
```

Standard Web Form экспортируется в source app. Generated `.json/.js/.py` boilerplate не редактируем.

---

# 5. Поля Web Form

Добавить:

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

Web Form не ослабляет Mandatory metadata L4.

---

# 6. Базовый вид

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

# 7. Временный Guest experiment

Для изучения Guest creation временно:

```text
Published:                  Yes
Anonymous responses:        Yes
Login required:             No
Apply document permissions: No
Allow editing after submit: No
Allow multiple responses:   No
Show list:                  No
```

Чтобы не раскрывать внутренние Link-каталоги публичному Guest:

## Location

```text
Hidden:    Yes
Mandatory: Yes
Default:   Main Site
```

## Equipment

```text
скрыть / временно убрать из Web Form
```

Это security experiment, а не финальная конфигурация.

---

# 8. Guest submission

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

и работу L9 automation.

Guest не должен увидеть списки Location/Equipment.

---

# 9. Mandatory tests

Отдельно получить отказ:

```text
без Subject
без Description
```

Не включать `Allow incomplete forms` ради обхода основной модели.

---

# 10. Перейти к финальному authenticated trust model

Вернуть:

```text
Anonymous responses: No
Login required:      Yes
Allow multiple:      Yes
Show list:           Yes
Show attachments:    Yes
```

Пока для короткого эксперимента edit можно временно включить позже, но **финальное значение будет No**.

---

# 11. Вернуть Location и Equipment

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

# 12. Threat model Link options

`Allow Read On All Link Options = Yes` в `v16.32.0` позволяет Web Form получить общие Link options без owner-фильтра.

Поэтому финальная модель курса предполагает:

```text
Website User
= доверенный внутренний заявитель
```

Он может видеть имена/названия доступных Web Form Link options `Facility Location` и `Equipment`.

Не выдаём эту конфигурацию за безопасную публичную internet-форму для неизвестных пользователей.

Для внешнего недоверенного intake потребовался бы отдельно спроектированный safe catalog/permission layer — это Later.

---

# 13. Создать Website User

```text
Email:              web.requester@example.com
First Name:         Web Requester
User Type:          Website User
Enabled:            Yes
Send Welcome Email: No
```

Задать учебный пароль.

Не выдавать:

```text
Administrator
System Manager
```

---

# 14. Проверить Login Required

Guest больше не должен получать рабочую форму `/facility-request`.

Войти:

```text
web.requester@example.com
```

Форма должна открыться.

---

# 15. Создать authenticated заявку

```text
Subject:     Website user request
Location:    Warehouse
Equipment:   логично подходящий Equipment или пусто
Description: Authenticated Web Form test
Priority:    Medium
Target Date: будущая дата или пусто
Attachment:  тестовый файл
```

Проверить в Desk:

```text
Owner = web.requester@example.com
Status = New
```

Assignment Rule может создать ToDo, но Status остаётся `New`.

---

# 16. Show List как безопасный read-path

Под Website User открыть список ответов.

`Show List = Yes` используется для просмотра собственных доступных Web Form responses.

Рекомендуемые columns:

```text
Subject
Priority
Status
Target Date
```

Просмотр ответа не означает право его редактировать.

---

# 17. Временно изучить Allow Edit

Только на отдельной новой заявке, пока она ещё `Status = New`, временно установить:

```text
Allow editing after submit = Yes
Apply document permissions = No
```

Под owner `web.requester@example.com` изменить:

```text
Description
```

Проверить изменение в Desk.

Фиксируем факт механизма:

```text
owner-based Web Form permission
может разрешить update отдельно от Role Permission
```

---

# 18. Почему этот режим не оставляем

После временного теста представить ситуацию:

```text
Supervisor → Accept
Technician → Start Work
Status = In Progress
```

Если Web Form всё ещё разрешает owner edit, внешний owner остаётся отдельным update path к тому же рабочему документу.

Это противоречит строгой архитектуре процесса.

Поэтому сразу вернуть:

```text
Allow editing after submit = No
```

и сохранить.

Это **обязательный rollback L10**.

---

# 19. Проверить финальный запрет update

Под Website User открыть собственную ранее созданную заявку.

Она может быть доступна для просмотра через Show List, но не должна предоставлять штатный Web Form update после:

```text
Allow editing after submit = No
```

Попытка отправить update должна быть отклонена Web Form.

---

# 20. Owner boundary

Website User не должен получить чужой ответ только потому, что знает его `name`.

Проверить попытку открыть Service Request другого owner через Web Form route.

---

# 21. Apply Document Permissions

Временно включить:

```text
Apply document permissions = Yes
```

и проверить read-доступ Website User к своему Document.

Website User не имеет нашей Desk Role matrix, поэтому теперь поведение опирается на обычные document permissions.

Смысл:

```text
OFF
→ Web Form owner/website permission model

ON
→ обычные document permissions
```

После теста вернуть:

```text
Apply document permissions = No
```

`Allow Edit` при этом остаётся:

```text
No
```

---

# 22. Проверить System User через Web Form

Под:

```text
requester.one@example.com
```

создать корректную заявку через Web Form.

Поля должны соблюдать L4.

При необходимости временно включить `Apply Document Permissions = Yes`, чтобы увидеть влияние L5 `If Owner`, затем вернуть `No`.

Не возвращать `Allow Edit = Yes`.

---

# 23. Web Form не управляет Workflow

После создания:

```text
Web Form
→ Status = New
```

Дальнейший процесс:

```text
Assignment Rule → ToDo
Supervisor → Accept
Technician → Start Work
Technician → Resolve
Supervisor → Close
```

`Status` не присутствует как editable Web Form field.

---

# 24. Final configuration

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

# 25. Что именно гарантируется

## Hard / server-side

```text
Login Required
Mandatory Web Form fields
Allow Edit = No для update
owner/read permission checks Web Form
```

## Structural/UI

```text
Status не выведен в форму
Web Form является intake channel
```

## Deployment trust policy

```text
Website Users считаются доверенными внутренними заявителями
и могут видеть Link option names
```

Не смешивать эти уровни.

---

# 26. Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -i 'web_form\|facility_request'
```

Standard Web Form source попадает в app/Git.

Не экспортировать:

```text
Website User
Service Request runtime data
Files
```

---

# 27. Приёмка L10

L10 принят, если:

- Web Form создаёт обычный `Service Request`;
- Guest experiment выполнен с закрытыми Link catalogs и затем выключен;
- финальный режим Login Required;
- Website User понимается как trusted internal reporter;
- `Description` остаётся Mandatory;
- Location/Equipment disclosure через Link options объяснено явно;
- Show List работает как read-path;
- `Allow Edit` временно изучен;
- после эксперимента `Allow Edit = No`;
- собственный Web Form update в финале запрещён;
- `Apply Document Permissions` проверен и возвращён в `No`;
- `Status` не управляется из Web Form;
- процесс использует `Accept`, а не старое `Mark Assigned`;
- app source содержит Web Form, runtime users/data — нет.

После L10 переходим к **L11 — переносимость**.