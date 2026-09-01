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
Assignment
≠ Workflow

Assignment
≠ authorization

Target Date
= optional
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

Workflow L7 использует:

```text
New
Accepted
In Progress
Resolved
Closed
```

и действия:

```text
Accept
Start Work
Resolve
Close
```

---

# 2. Все тестовые Documents соблюдают L4

Каждая создаваемая в L9 заявка содержит:

```text
Subject
Location
Description
Priority
```

`Status` получает default `New`.

`Target Date` заполняем только в тестах, где нужна due/date-based automation.

Не сокращать примеры так, чтобы они нарушали Mandatory metadata.

---

# 3. Создать второго Technician

Только теперь создаём:

```text
Email:              technician.two@example.com
First Name:         Technician Two
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Technician
```

Не выдавать:

```text
System Manager
Administrator
```

Проверить у обоих:

```text
technician.one@example.com
technician.two@example.com
```

отсутствие постоянного Location User Permission.

---

# 4. Почему это важно для Assignment Rule

В `v16.32.0` штатный `Assign To` после создания ToDo проверяет, может ли assignee открыть reference document.

Если доступа нет:

```text
document sharing включён
→ Frappe может автоматически создать DocShare Read

document sharing отключён
→ операция может завершиться Missing Permission
```

Поэтому основной deployment курса устроен так:

```text
оба Facility Technician
→ имеют одинаковый базовый Role Permission на Service Request
```

Assignment не должен незаметно превращаться в механизм выдачи permission exceptions.

Это более точная причина cleanup User Permission в L5.

---

# 5. Notification на новую заявку

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

---

# 6. Проверить New Notification

Под Requester создать:

```text
Subject:     Automation notification test
Location:    Room 101
Description: Проверка System Notification на создание заявки
Priority:    Medium
```

`Target Date` можно оставить пустым: для Notification Event `New` он не нужен.

Под Supervisor проверить верхнее уведомление и `Notification Log`.

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

Condition Type:

```text
Filters
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

Это не «все документы, которые когда-либо просрочены».

---

# 8. Target Date — условный инвариант

`Target Date` остаётся Optional.

Поэтому нельзя обещать каждой заявке Due Date.

Правильная модель:

```text
Target Date заполнен
→ ToDo Assignment Rule может получить эту Due Date
→ date-based Notification может быть рассчитана

Target Date пуст
→ Due Date не обещается
→ One Day Overdue к такой записи неприменима
```

---

# 9. Проверить date-based Notification

Создать:

```text
Subject:     Overdue automation test
Location:    Room 102
Description: Проверка уведомления через один день после Target Date
Priority:    High
Target Date: вчера
```

Оставить незакрытой.

Использовать Preview / Meets Condition / Get Alerts for Today.

Затем выполнить:

```bash
cd ~/frappe/facility-ops-bench

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

Unassign Condition:

```text
пусто
```

Assignment Days:

```text
All Days
```

В `Assignment Rule v16.32.0` поля документа передаются непосредственно в expression context, поэтому форма `status == "New"` корректна именно для этого механизма.

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

`Last User` хранится в Assignment Rule.

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

Главный вывод:

```text
Assignment Rule создал ответственность
но не выполнил Workflow transition
```

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

Ожидается Technician Two.

Третья:

```text
Subject:     Auto assignment C
Location:    Room 102
Description: Третья заявка Round Robin
Priority:    Low
Target Date: будущая дата
```

Ожидается Technician One.

Последовательность:

```text
One → Two → One
```

Проверить, что оба Technician открывают свои assigned Documents без автоматических DocShare exceptions.

---

# 14. Assignment не является authorization

После появления второго Technician доказать отдельно:

```text
ToDo назначен Technician One
```

не означает:

```text
Technician Two автоматически лишён Role Permission на этот Service Request
```

В базовой архитектуре:

```text
Role = полномочие
ToDo = ответственность
```

Это сознательная модель, а не недостаток, который маскируем учебным текстом.

Если будущему продукту понадобится `assignee-only write`, потребуется отдельная server-side permission architecture следующего уровня.

---

# 15. Провести заявку через Workflow

На автоматически назначенной заявке:

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

Assignment Rule Close Condition должен закрыть связанный ToDo.

На основном site это deployment behavior L9.

Это **не универсальное свойство Workflow** и не будет автоматически существовать на clean site L11 без Assignment Rule.

---

# 16. Due Date synchronization

На заявке с заполненным `Target Date` изменить его под пользователем, которому разрешено изменение документа в текущем сценарии.

Проверить соответствующий открытый ToDo:

```text
ToDo.date
→ новое Target Date
```

Не распространять этот вывод на заявки с пустым Target Date.

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

Сравнить ручной и автоматический ToDo.

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

Только Supervisor выполняет:

```text
Accept
```

После него:

```text
Status = Accepted
```

`Accepted` специально не называется `Assigned`.

---

# 19. Optional: Load Balancing

Перед тестом посмотреть открытые ToDo `Service Request` обоих Technician.

Временно:

```text
Rule = Load Balancing
```

Создать:

```text
Subject:     Load balancing check
Location:    Warehouse
Description: Проверка второго штатного алгоритма
Priority:    Medium
```

Проверить выбор пользователя с меньшим количеством открытых ToDo.

Если counts одинаковы, подготовить очевидную разницу.

После проверки обязательно:

```text
Rule = Round Robin
```

---

# 20. Посмотреть служебные Documents

Открыть:

```text
Notification
Notification Log
Assignment Rule
ToDo
```

Не создавать своих automation log/dispatcher DocType.

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

Эта граница будет проверена в L11.

---

# 22. Git

Проверить Standard Notification files:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -i notification
```

Закоммитить app-owned Notification source.

Не добавлять:

```text
Users
ToDo
Notification Log
Assignment Rule database record
Service Request working data
```

---

# 23. Приёмка L9

L9 принят, если:

- `technician.two@example.com` впервые создан здесь;
- оба Technician имеют одинаковую базовую Service Request permission-area;
- ученик объясняет automatic Share boundary `Assign To`;
- все тестовые Documents соблюдают Mandatory L4;
- New Notification работает;
- `Service Request One Day Overdue` понимается как точка `+1 day`;
- Target Date понимается как Optional/conditional automation input;
- Round Robin даёт One → Two → One;
- Assignment Rule не меняет `Status = New`;
- Supervisor выполняет `Accept`, не `Mark Assigned`;
- `Accepted` не означает наличие конкретного assignee;
- Assignment не трактуется как authorization;
- Closed закрывает Rule-owned ToDo только как site policy L9;
- optional Load Balancing возвращён в Round Robin;
- Assignment Rule остаётся site-specific;
- Git содержит Notifications, но не runtime data.

После L9 переходим к **L10 — Web Form**.