# L9. Автоматизация

L9 автоматизирует уже работающий `Service Request`, не меняя его архитектурных границ.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

## Цепочка

```text
новая заявка
→ System Notification Supervisor
→ Assignment Rule создаёт ToDo
→ Status остаётся New
→ Supervisor Accept
→ Technician Start Work / Resolve
→ Supervisor Close
```

Ключевые правила:

```text
Assignment ≠ Workflow
Assignment ≠ authorization
Automation ≠ permission escalation
Target Date = optional
```

---

# 1. Проверить стенд

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps
bench --site facility-ops.localhost scheduler status
bench --site facility-ops.localhost doctor

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
scheduler активен
workers доступны
working tree clean
```

Workflow L7:

```text
New
Accepted
In Progress
Resolved
Closed
```

Actions:

```text
Accept
Start Work
Resolve
Close
```

---

# 2. Permission model не меняется в L9

После L7 продолжает действовать:

```text
Service Request Level 0
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No

Service Request Level 1 content
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
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

`status` остаётся Level 0.

Assignment Rule не должен выдавать Technician Level 1 Write.

---

# 3. Все тестовые Documents соблюдают L4

Каждая создаваемая в L9 заявка содержит:

```text
Subject
Location
Description
Priority
```

`Status` получает default `New`.

`Target Date` заполняем только в тестах, где нужна due/date-based automation.

---

# 4. Создать второго Technician

```text
Email:              technician.two@example.com
First Name:         Technician Two
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Technician
```

Не выдавать System Manager/Administrator.

Проверить у обоих Technician:

```text
нет постоянного Location User Permission
Level 1 Service Request Write = No
```

---

# 5. Почему одинаковый базовый доступ важен Assignment Rule

`Assign To` в `v16.32.0` проверяет, может ли assignee открыть reference document.

Если доступа нет:

```text
sharing включён
→ Frappe может создать DocShare Read

sharing выключен
→ возможен Missing Permission
```

Поэтому оба Technician имеют одинаковый Role-based document access.

Но одинаковый document access **не означает** одинаковое право с Supervisor на Level 1 content.

---

# 6. Notification на новую заявку

Создать Standard Notification:

```text
Name:                 New Service Request
Enabled:              Yes
Is Standard:          Yes
Module:               Facility Operations
Channel:              System Notification
Send Alert On:        New
Document Type:        Service Request
Notification Type:    Alert
Notification Title:   New service request {{ doc.name }}
Notification Message: {{ doc.subject }}
```

Recipient:

```text
Receiver By Role = Facility Supervisor
```

Под Requester создать:

```text
Subject:     Automation notification test
Location:    Room 101
Description: Проверка System Notification на создание заявки
Priority:    Medium
```

Под Supervisor проверить уведомление и `Notification Log`.

---

# 7. Date-based Notification

Создать:

```text
Name:                 Service Request One Day Overdue
Enabled:              Yes
Is Standard:          Yes
Module:               Facility Operations
Channel:              System Notification
Send Alert On:        Days After
Document Type:        Service Request
Reference Date:       Target Date
Days Before or After: 1
Notification Type:    Alert
Notification Title:   Overdue service request {{ doc.name }}
Notification Message: {{ doc.subject }}
```

Filter:

```text
Status != Closed
```

Recipient:

```text
Facility Supervisor
```

Точная семантика:

```text
Target Date = вчера
+
Days After = 1
→ подходит сегодня
```

Это не «любой давно просроченный Document».

---

# 8. Target Date — conditional invariant

```text
Target Date заполнен
→ Assignment Rule ToDo может получить Due Date
→ date-based Notification может быть рассчитана

Target Date пуст
→ Due Date не обещается
→ One Day Overdue неприменима
```

`Target Date` остаётся Optional и находится на Permission Level 1.

Следовательно Technician не получает право менять срок только потому, что он assignee.

---

# 9. Проверить date-based Notification

Создать под Requester или Supervisor:

```text
Subject:     Overdue automation test
Location:    Room 102
Description: Проверка уведомления через один день после Target Date
Priority:    High
Target Date: вчера
```

Оставить незакрытой.

Использовать Preview / Meets Condition / Get Alerts for Today.

Затем:

```bash
bench --site facility-ops.localhost execute \
  frappe.email.doctype.notification.notification.trigger_daily_alerts
```

Проверить `Notification Log`.

---

# 10. Создать Assignment Rule

```text
Name:              Service Request Auto Assignment
Document Type:     Service Request
Due Date Based On: Target Date
Priority:          10
Disabled:          No
Description:       {{ subject }}
```

Assign Condition:

```python
status == "New"
```

Close Condition:

```python
status == "Closed"
```

Unassign Condition: пусто.

Assignment Days: All Days.

---

# 11. Round Robin

```text
Rule = Round Robin
```

Users:

```text
technician.one@example.com
technician.two@example.com
```

Сохранить.

---

# 12. Первая автоматическая заявка

Создать:

```text
Subject:     Auto assignment A
Location:    Room 101
Description: Первая заявка для проверки Round Robin
Priority:    Medium
Target Date: будущая дата
```

Проверить:

```text
Status = New
Assigned To = technician.one@example.com
```

ToDo:

```text
Allocated To    = technician.one@example.com
Reference Type  = Service Request
Reference Name  = номер заявки
Due Date        = Target Date заявки
Assignment Rule = Service Request Auto Assignment
```

Assignment Rule создаёт ответственность, но не Workflow transition и не Level 1 permission.

---

# 13. Вторая и третья заявки

Вторая:

```text
Subject:     Auto assignment B
Location:    Warehouse
Description: Вторая заявка Round Robin
Priority:    Medium
Target Date: будущая дата
```

Третья:

```text
Subject:     Auto assignment C
Location:    Room 102
Description: Третья заявка Round Robin
Priority:    Low
Target Date: будущая дата
```

Ожидаемая последовательность:

```text
One → Two → One
```

Проверить, что оба Technician открывают assigned Documents без auto-Share exceptions.

---

# 14. Assignment не является authorization

```text
ToDo назначен Technician One
```

не означает:

```text
Technician Two лишён Role Permission
```

и не означает:

```text
Technician One получил Level 1 Write
```

Правильная модель:

```text
Role/Permission Level = полномочия
ToDo                  = ответственность
```

---

# 15. Провести заявку через Workflow

```text
Supervisor → Accept
Technician → Start Work
Technician → Resolve
Supervisor → Close
```

Получить:

```text
Status = Closed
```

Assignment Rule Close Condition должен закрыть Rule-owned ToDo.

Это main-site deployment behavior L9, не универсальное свойство Workflow.

---

# 16. Due Date synchronization без permission-размывания

На заявке с заполненным `Target Date` войти **Supervisor**, потому что `Target Date` — Level 1 content, а Technician Level 1 Write не имеет.

Изменить Target Date и сохранить.

Проверить открытый Rule-owned ToDo:

```text
ToDo.date
→ новое Target Date
```

Затем под Technician убедиться, что Target Date остаётся read-only.

Главный вывод:

```text
automation синхронизирует Due Date
≠ Technician получает право менять source Target Date
```

---

# 17. Сравнить ручное и автоматическое назначение

Временно:

```text
Assignment Rule → Disabled = Yes
```

Создать:

```text
Subject:     Manual assignment comparison
Location:    Floor 1
Description: Сравнение ручного Assign To и Assignment Rule
Priority:    Medium
```

Проверить отсутствие auto ToDo.

Под Supervisor:

```text
Assign To → technician.one@example.com
```

После теста снова включить Rule.

---

# 18. Доказать ортогональность Workflow

Создать:

```text
Subject:     Assignment without workflow transition
Location:    Floor 2
Description: Проверка разделения Assignment и Workflow
Priority:    High
```

Сразу после insert:

```text
Assigned To = один из Technician
Status = New
```

Только Supervisor выполняет `Accept`.

После него:

```text
Status = Accepted
```

`Accepted` специально не называется `Assigned`.

---

# 19. Optional: Load Balancing

Временно:

```text
Rule = Load Balancing
```

Создать валидную test request и проверить выбор пользователя с меньшим количеством открытых ToDo.

После проверки обязательно:

```text
Rule = Round Robin
```

---

# 20. Посмотреть служебные Documents

```text
Notification
Notification Log
Assignment Rule
ToDo
```

Не создавать собственных automation log DocType.

---

# 21. Что переносится, а что нет

Standard app-owned:

```text
New Service Request
Service Request One Day Overdue
```

Site-specific:

```text
Service Request Auto Assignment
```

потому что Rule содержит конкретных Users.

---

# 22. Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
find facility_ops/facility_operations -type f | sort | grep -i notification
```

Закоммитить app-owned Notification source.

Не добавлять Users/ToDo/Notification Log/Assignment Rule/runtime Service Request.

---

# 23. Приёмка L9

L9 принят, если:

- `technician.two@example.com` впервые создан здесь;
- оба Technician имеют одинаковый document access и Level 1 Write = No;
- Assignment Rule не создаёт скрытые permission exceptions в нормальном сценарии;
- все test Documents соблюдают Mandatory L4;
- New Notification работает;
- `One Day Overdue` понимается как точка `+1 day`;
- Target Date понимается как Optional Level 1 automation input;
- Round Robin даёт One → Two → One;
- Assignment Rule не меняет `Status = New`;
- Assignment не трактуется как authorization или permission escalation;
- Technician не может менять Target Date только из-за assignment;
- Supervisor меняет Target Date, а Rule-owned ToDo синхронизирует Due Date;
- `Accept` остаётся отдельным Workflow action;
- Closed закрывает Rule-owned ToDo только как site policy L9;
- optional Load Balancing возвращён в Round Robin;
- Assignment Rule остаётся site-specific;
- Git содержит Notifications, но не runtime data.

После L9 переходим к **L10 — Web Form**.
