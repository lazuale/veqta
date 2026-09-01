# L10. Web Form

L10 открывает внешний веб-вход в уже существующий `Service Request`.

Новых предметных DocType нет.

Цель:

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

Главное правило урока:

```text
Web Form
не ослабляет модель Service Request
```

Если поле Mandatory в основном DocType, оно остаётся обязательным и во внешней форме. В L4 обязательны:

```text
Subject
Location
Description
Priority
```

`Status` получает default `New` и пользователю Web Form не показывается как управляющее поле.

---

# 1. Проверить стенд

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

На site уже работают:

```text
Service Request Workflow
Service Request Auto Assignment
New Service Request Notification
```

Оба Technician из L9 имеют обычный доступ к Service Request независимо от Location.

---

# 2. Не создавать второй внешний процесс

Web Form работает с тем же:

```text
Service Request
```

Не создаём:

```text
Public Request
External Request
Website Request
Portal Ticket
```

Обычный Document, созданный из браузера, должен участвовать в тех же:

```text
Naming
Workflow
Assignment Rule
Notification
Timeline
Permissions
```

---

# 3. Создать Standard Web Form

Под Administrator, при включённом Developer Mode, открыть `Web Form` и создать:

```text
Title:          Report a Facility Issue
Route:          facility-request
Select DocType: Service Request
Module:         Facility Operations
Is Standard:    Yes
```

Сохранить.

Standard Web Form экспортируется в source app. Frappe может создать рядом штатные `.json`, `.js` и `.py` boilerplate-файлы. В базовом курсе `.js` и `.py` не редактируем.

---

# 4. Настроить поля

В `Web Form Fields` добавить:

| Field | Настройка |
|---|---|
| Subject | Mandatory |
| Location | Mandatory |
| Equipment | Optional |
| Description | **Mandatory** |
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

Критично:

```text
Service Request.description = Mandatory
→ Web Form Description тоже Mandatory
```

Нельзя делать UI «Optional», если backend-модель требует значение.

---

# 5. Базовый вид

Настроить:

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

# 6. Первый режим: Guest

Временно настроить:

```text
Published:                   Yes
Anonymous responses:         Yes
Login required:              No
Apply document permissions:  No
Allow editing after submit:  No
Allow multiple responses:    No
Show list:                   No
```

Для публичного Guest-теста не раскрываем внутренние справочники.

Временно у `Location`:

```text
Hidden:    Yes
Mandatory: Yes
Default:   Main Site
```

`Equipment` удалить из Web Form Fields или скрыть без обязательности.

`Subject`, `Description` и `Priority` остаются видимыми и Mandatory.

---

# 7. Проверить Guest submission

Выйти из системы и открыть:

```text
http://facility-ops.localhost:8000/facility-request
```

Создать:

```text
Subject:     Guest web form test
Description: Public web form submission with required description
Priority:    High
Target Date: будущая дата
Attachment:  небольшой тестовый файл
```

Location должна подставиться как `Main Site`.

Нажать:

```text
Create Request
```

---

# 8. Проверить результат в Desk

Под Administrator или Supervisor найти созданный `Service Request`.

Проверить:

```text
Subject     = Guest web form test
Location    = Main Site
Description = заполнено
Priority    = High
Status      = New
Attachment  = загружен
```

Web Form не хранит отдельную копию заявки.

---

# 9. Проверить автоматизацию L9

На Guest-заявке проверить:

```text
Assignment Rule
→ создал ToDo

Notification
→ отработала для Supervisor

Status
→ остался New
```

Назначенный Technician должен иметь возможность открыть заявку независимо от Location.

Фиксируем:

```text
Web Form = канал создания
Assignment = кто делает
Workflow = состояние процесса
```

---

# 10. Проверить Mandatory в Web Form

Сделать два отрицательных теста.

## Без Subject

Попробовать отправить форму без `Subject`.

Отправка должна быть заблокирована.

## Без Description

Попробовать отправить форму без `Description`.

Отправка также должна быть заблокирована.

Не включать:

```text
Allow incomplete forms
```

ради обхода metadata.

---

# 11. Проверить attachment

Создать ещё одну корректно заполненную Guest-заявку с небольшим файлом.

Проверить:

```text
Service Request.attachment
```

и связанный `File`.

При желании проверить файл больше `Max attachment size`.

---

# 12. Перевести Web Form в финальный Login Required режим

Вернуться под Administrator и установить:

```text
Anonymous responses:         No
Login required:              Yes
Allow multiple responses:    Yes
Allow editing after submit:  Yes
Show list:                   Yes
Apply document permissions:  No
Show attachments:            Yes
```

Это финальный режим формы курса.

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

`Description` остаётся:

```text
Mandatory = Yes
```

`Allow Read On All Link Options` нужен, чтобы Website User мог выбрать справочные значения Web Form, не становясь owner этих справочников.

Это не равно полноценному Desk permission на DocType.

---

# 14. Создать Website User

Создать:

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
System Manager
Administrator
```

Для основной проверки при `Apply document permissions = No` отдельная Desk role не нужна.

---

# 15. Проверить Login Required

Незалогиненный Guest не должен получить обычную форму создания по route:

```text
/facility-request
```

Войти как:

```text
web.requester@example.com
```

и открыть тот же route.

Форма должна стать доступной.

---

# 16. Создать заявку как Website User

Создать:

```text
Subject:     Website user request
Location:    Warehouse
Equipment:   любое Equipment из Warehouse или пусто
Description: Authenticated Web Form test
Priority:    Medium
Target Date: будущая дата
Attachment:  тестовый файл
```

Проверить в Desk:

```text
Owner = web.requester@example.com
Status = New
```

и работу Assignment Rule.

Назначенный Technician должен открывать документ независимо от выбранной Location.

---

# 17. Show List

Под Website User открыть список ответов Web Form.

При `Show List = Yes` пользователь должен видеть свои доступные ответы.

List Columns оставить минимум:

```text
Subject
Priority
Status
Target Date
```

Не превращать Web Form List в копию Desk List View.

---

# 18. Allow Edit

Открыть собственную заявку через Web Form.

При:

```text
Allow editing after submit = Yes
Apply document permissions = No
```

owner может изменить свой ответ.

Изменить `Description`, сохранить и проверить то же значение в Desk.

---

# 19. Доказать owner-границу

Под Administrator найти Service Request другого owner.

Под `web.requester@example.com` попытаться открыть чужой Document через Web Form URL.

При `Apply document permissions = No` обычный logged-in пользователь не должен получить чужой ответ только потому, что знает его `name`.

---

# 20. Apply Document Permissions

Временно включить:

```text
Apply document permissions = Yes
```

Под Website User снова проверить свою заявку.

Website User не имеет нашей Desk role matrix L5, поэтому теперь Web Form должен опираться на обычные document permissions.

Смысл переключателя:

```text
OFF
→ Web Form owner/website access model

ON
→ обычные document permissions
```

После проверки вернуть:

```text
Apply document permissions = No
```

---

# 21. Проверить System User отдельно

Войти как:

```text
requester.one@example.com
```

Создать через Web Form корректную заявку:

```text
Subject:     System user web form test
Location:    Room 101
Description: Проверка Web Form под Facility Requester
Priority:    Low
```

Временно включить `Apply document permissions = Yes` и проверить влияние L5 `If Owner`.

После теста вернуть `Apply document permissions = No`.

---

# 22. Web Form не управляет Workflow

`Status` не должен быть editable полем Web Form.

Website User не выполняет:

```text
New → Assigned
New → Closed
```

После создания:

```text
Web Form submission
→ New
→ Assignment Rule назначает Technician
→ Supervisor Mark Assigned
→ Technician Start Work / Resolve
→ Supervisor Close
```

Один процесс, один underlying Document.

---

# 23. Проверить Standard Web Form в Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -i 'web_form\|facility_request'
```

Frappe может создать `.json`, `.js`, `.py` boilerplate.

В базовом курсе кодовые файлы не редактируем.

---

# 24. Source против data

```text
Web Form definition
→ app source / Git

Service Request, созданный через Web Form
→ working data site

web.requester@example.com
→ site data/configuration
```

Website User не экспортируем fixture.

---

# 25. Финальная конфигурация

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
Allow editing after submit:  Yes
Show list:                   Yes
Apply document permissions:  No
Show attachments:            Yes
```

Fields:

```text
Subject     Mandatory
Location    Mandatory + Allow Read On All Link Options
Equipment   Optional + Allow Read On All Link Options
Description Mandatory
Priority    Mandatory
Target Date Optional
Attachment  Optional
```

`Status` отсутствует в пользовательском наборе полей.

---

# 26. Commit L10

Проверить app-owned Web Form files и закоммитить их без рабочих данных и Users.

Пример сообщения:

```bash
git commit -m "Add service request web form"
```

---

# 27. Приёмка L10

L10 принят, если:

- Web Form создаёт обычный `Service Request`;
- Guest-сценарий проверен и затем выключен;
- `Description` нигде не становится Optional;
- отсутствие Subject/Description реально блокирует отправку;
- attachment работает;
- финальный режим требует Login;
- Website User может создать, увидеть в Show List и изменить собственный ответ;
- чужой ответ не открывается через знание name;
- `Apply document permissions` проверен и возвращён в `No`;
- Location/Equipment options работают в authenticated форме;
- Web Form не управляет Workflow State;
- Assignment Rule может назначить заявку из любой выбранной Location доступному Technician;
- Standard Web Form находится в source app, рабочие заявки и Website User — нет.

После L10 переходим к **L11 — переносимость и clean site**.