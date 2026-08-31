# Сквозное состояние практического курса Frappe 16

Этот файл не заменяет лабораторные. Он фиксирует, **что должно существовать на стенде после каждого блока**, чтобы следующая практика была воспроизводимой.

Основной стенд: [00_LAB_SETUP.md](00_LAB_SETUP.md).

Полный индекс лабораторных: [labs/README.md](labs/README.md).

---

# После главы 0

```text
Bench:  ~/frappe/frappe16-course-bench
Site:   learn.localhost
Frappe: v16.32.0
Apps:   frappe, training
Module: Training
```

Site должен открываться по:

```text
http://learn.localhost:8000
```

---

# После блока A — главы 1–3

Новых business objects нет.

Ученик умеет найти на диске и в Desk:

```text
Bench
Site
App
Module
DocType
Document
Workspace
List/Form
```

И понимает, что чистый Framework работает без ERPNext.

---

# После блока B — главы 4–10

Должны существовать:

```text
Request
Request Item
Training Settings
Training Category
Approval Record
```

`Request` содержит минимум:

```text
Subject
Description
Status
Priority
Due Date
Responsible
Responsible Name
Is Urgent
Estimate Hours
Notes
Reference File
Items → Request Item
```

Naming новых Request — стабильная учебная series вида:

```text
REQ-.YYYY.-.#####
```

Есть несколько Request Documents и примеры `Approval Record` в разных docstatus.

---

# После блока C — главы 11–16

`Request` имеет аккуратную Form layout.

Есть:

```text
List data
Kanban по Status
Calendar по Due Date
при необходимости Start/End Date для Gantt
Training Category Tree
Training Workspace
custom_local_note через Customize Form
```

Ученик различает Standard metadata и site customization, но глубокий перенос ещё не изучает.

---

# После блока D — главы 17–22

Есть:

```text
Roles:
Training User
Training Manager

Users:
student.user@example.test
student.manager@example.test

DocType:
Training Area

Areas:
North
South
```

В `Request` добавлены:

```text
Area → Training Area
Internal Cost → Permission Level 1
```

Рабочая модель доступа:

```text
Training User
→ работает с разрешёнными Request
→ ограничен User Permission по North
→ не видит Internal Cost

Training Manager
→ имеет расширенные права
→ видит Internal Cost
```

Есть один учебный пример Share.

---

# После блока E — главы 23–28

Есть минимум один активный Assignment/ToDo.

Assignment Rule проверен и может быть оставлен Disabled.

У `Request` работает Workflow:

```text
Draft
→ Review
→ Approved
→ Rejected
→ Reopen/Draft
```

Переходы разделены между `Training User` и `Training Manager`.

Notification проверена и может быть Disabled.

Auto Repeat проверен на отдельном учебном DocType и может быть Disabled.

---

# После блока F — главы 29–33

На одном Request есть:

```text
Comments
Timeline events
Version history
public File
private File
Communication
```

Для `Request` существует рабочий Print Format.

Email используется только через безопасную тестовую конфигурацию.

---

# После блока G — главы 34–38

В `Request` должно быть минимум 40–50 учебных Documents.

Есть:

```text
Report Builder report
Query Report
Script Report
Number Card
Dashboard Chart
```

Card/Chart размещены в Training Workspace.

Data Import проверен как для create, так и для update, включая обработку ошибочной строки.

---

# После блока H — главы 39–43

Есть:

```text
Web Form для Request
простая Training Portal page
REST CRUD опыт
training.api.ping_training whitelisted RPC method
training.api@example.test integration user
```

API key/secret не должны лежать в Git.

Guest creation в Web Form должен быть выключен, если он не нужен дальше.

---

# После главы 44

Есть Client Script Request, который демонстрирует минимум:

```text
conditional mandatory
show/hide
custom UI action
Child Table calculation
```

Ученик уже проверил через REST, что Client Script не является server-side validation.

---

# После главы 45

Server Scripts включены на учебном Bench.

Есть рабочая server-side validation:

```text
Request Status = Done
→ Result обязателен
```

Она проверена как минимум через:

```text
Desk
REST API
```

API Server Script и Scheduler Event проверены; после опыта их можно оставить `Disabled`.

---

# Правило восстановления

Если лабораторная ломает стенд сильнее, чем ожидается:

1. не продолжать следующую главу вслепую;
2. проверить последние изменённые metadata/permissions/scripts;
3. использовать Version/Git/backup-механизм, соответствующий уже изученному уровню;
4. вернуть состояние, описанное для предыдущего блока;
5. только после этого продолжать.

Курс специально допускает ошибки. Но каждая ошибка должна закончиться пониманием причины и восстановлением воспроизводимого состояния.
