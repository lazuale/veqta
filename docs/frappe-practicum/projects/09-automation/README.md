# L9. Автоматизация

L9 автоматизирует уже работающий процесс `Service Request` штатными механизмами Frappe.

Новых предметных DocType нет.

Цель:

```text
новая заявка
→ System Notification Supervisor
→ автоматическое назначение Technician
→ ToDo с Due Date из Target Date
→ Workflow остаётся отдельным
→ Closed закрывает ToDo
→ date-based Notification проверяет просрочку
```

Базовая версия: **Frappe Framework v16.32.0**.

Все тестовые `Service Request` в этом уроке заполняются согласно metadata L4. Обязательные поля не сокращаем ради примера:

```text
Subject
Location
Description
Priority
Status получает default New
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

Во время практики `bench start` работает в отдельном терминале.

После L5–L7 основной `technician.one@example.com` не имеет постоянного User Permission по Location.

---

# 2. Зафиксировать границу автоматизации

До L9 процесс уже работает вручную:

```text
создать Service Request
→ Assign To
→ Workflow Action
→ ToDo
→ Close
```

Теперь автоматизируем повторяемые операции, не создавая:

```text
Automation Log
Request Dispatcher
Notification Queue
Auto Assignment Record
```

---

# 3. Создать второго Technician

Только теперь создаём второго постоянного исполнителя:

```text
Email:              technician.two@example.com
First Name:         Technician Two
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Technician
```

Задать учебный пароль.

Не выдавать `System Manager` или `Administrator`.

Проверить, что ни у `technician.one@example.com`, ни у `technician.two@example.com` нет постоянного User Permission, ограничивающего `Service Request` одной Location.

Это необходимо для глобального Round Robin: назначенный Technician должен иметь возможность открыть назначенную ему заявку.

---

# 4. Notification на новую заявку

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

Recipients:

```text
Receiver By Role = Facility Supervisor
```

Email Account не нужен: используется `System Notification`.

---

# 5. Проверить New Notification

Войти как `requester.one@example.com` и создать:

```text
Subject:     Automation notification test
Location:    Room 101
Description: Проверка System Notification на создание заявки
Priority:    Medium
Target Date: любая будущая дата
```

Сохранить.

Под `supervisor.one@example.com` проверить верхние уведомления и `Notification Log`.

Если уведомления нет, сначала проверить scheduler/workers, а не писать скрипт.

---

# 6. Date-based Notification

Создать:

```text
Name:                 Overdue Service Request
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
→ уведомление подходит сегодня
```

Это **одноразовый сценарий через один день после Target Date**, а не запрос «все документы, просроченные когда-либо».

---

# 7. Preview date-based Notification

Использовать:

```text
Preview
Meets Condition?
Get Alerts for Today
```

Для подходящей незакрытой заявки ожидать `Meets Condition? = Yes`, для Closed — `No`.

---

# 8. Подготовить просроченную заявку

Под Requester создать:

```text
Subject:     Overdue automation test
Location:    Room 102
Description: Проверка уведомления через один день после Target Date
Priority:    High
Target Date: вчерашняя дата
```

Оставить заявку незакрытой.

---

# 9. Запустить daily handler вручную

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost execute \
  frappe.email.doctype.notification.notification.trigger_daily_alerts
```

Под Supervisor проверить `Notification Log`.

Различать:

```text
bench execute trigger_daily_alerts
= немедленный тест конкретного handler

scheduler status / doctor
= здоровье scheduler и workers
```

---

# 10. Создать Assignment Rule

Создать:

```text
Name:               Service Request Auto Assignment
Document Type:      Service Request
Due Date Based On:  Target Date
Priority:           10
Disabled:           No
Description:        {{ subject }}
```

Assign Condition:

```python
status == "New"
```

Close Condition:

```python
status == "Closed"
```

Unassign Condition оставить пустым.

В Assignment Rule `v16.32.0` expression получает поля документа непосредственно в context, поэтому `status == "New"` — штатная корректная форма для этого механизма.

---

# 11. Assignment Days

Нажать:

```text
All Days
```

Проверить Monday–Sunday. Учебное правило должно работать независимо от дня прохождения курса.

---

# 12. Round Robin

Выбрать:

```text
Rule = Round Robin
```

Users в порядке:

```text
technician.one@example.com
technician.two@example.com
```

Сохранить.

Frappe хранит `Last User` в самом Assignment Rule.

---

# 13. Первая автоматическая заявка

Под Requester создать:

```text
Subject:     Auto assignment A
Location:    Room 101
Description: Первая заявка для проверки Round Robin
Priority:    Medium
Target Date: будущая дата
```

Не использовать Assign To вручную.

Проверить:

```text
Status = New
Assigned To = technician.one@example.com
```

В ToDo:

```text
Reference Type   = Service Request
Reference Name   = номер заявки
Allocated To     = technician.one@example.com
Due Date         = Target Date заявки
Assignment Rule  = Service Request Auto Assignment
```

Assignment Rule назначил человека, но Workflow ещё не двигался.

---

# 14. Вторая и третья заявки

Создать вторую:

```text
Subject:     Auto assignment B
Location:    Warehouse
Description: Вторая заявка для проверки Round Robin
Priority:    Medium
Target Date: будущая дата
```

Ожидается:

```text
Assigned To = technician.two@example.com
```

Создать третью:

```text
Subject:     Auto assignment C
Location:    Room 102
Description: Третья заявка для проверки возврата Round Robin
Priority:    Low
Target Date: будущая дата
```

Ожидается:

```text
Assigned To = technician.one@example.com
```

Проверить `Last User`.

Важная проверка консистентности: оба Technician должны открывать свои автоматически назначенные заявки независимо от Location.

---

# 15. Due Date synchronization

Выбрать автоматически назначенную заявку и под пользователем, которому разрешено её редактировать в текущем Workflow state, изменить:

```text
Target Date
```

Открыть соответствующий ToDo.

Due Date должен обновиться вслед за `Service Request.target_date`.

---

# 16. Провести заявку через Workflow

На одной автоматически назначенной заявке:

```text
Supervisor → Mark Assigned
Technician → Start Work
Technician → Resolve
Supervisor → Close
```

Проверить:

```text
Service Request.status = Closed
ToDo.status = Closed
```

ToDo закрывается по `Close Condition` Assignment Rule.

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
Target Date: будущая дата
```

Проверить отсутствие автоматического ToDo.

Под Supervisor:

```text
Assign To → technician.one@example.com
```

Сравнить ручной и автоматический ToDo.

В обоих случаях рабочая сущность назначения:

```text
ToDo
```

После теста снова включить Assignment Rule.

---

# 18. Доказать, что Assignment Rule не двигает Workflow

Создать ещё одну корректно заполненную заявку:

```text
Subject:     Assignment without workflow transition
Location:    Floor 2
Description: Проверка разделения Assignment и Workflow
Priority:    High
Target Date: будущая дата
```

Сразу после сохранения:

```text
Assigned To = один из Technician
Status = New
```

Только Supervisor выполняет:

```text
Mark Assigned
```

Фиксируем:

```text
Assignment
= кто выполняет

Workflow
= состояние процесса
```

---

# 19. Посмотреть служебные Documents

Открыть:

```text
Notification Log
ToDo
Assignment Rule
Notification
```

Не должно появиться наших служебных DocType.

---

# 20. Проверить Standard Notifications в Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status --short

find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -i notification
```

Две Notification являются Standard app-owned configuration.

Не редактировать экспортированные JSON/boilerplate вручную.

---

# 21. Почему Assignment Rule не входит в app source

`Service Request Auto Assignment` содержит конкретных Users текущего site:

```text
technician.one@example.com
technician.two@example.com
```

Поэтому это site-specific deployment configuration.

В L11 он **намеренно не будет включён в универсальные fixtures** приложения.

Разделение:

```text
Workflow
→ универсальный процесс
→ переносимая app configuration

Assignment Rule с конкретными Users
→ локальное распределение работы
→ site-specific configuration
```

---

# 22. Optional: сравнить Load Balancing

Эта часть не обязательна для приёмки Core, но нужна для покрытия второго штатного алгоритма Assignment Rule.

Перед тестом посмотреть, сколько открытых `ToDo` типа `Service Request` сейчас есть у:

```text
technician.one@example.com
technician.two@example.com
```

Временно изменить правило:

```text
Rule = Load Balancing
```

Users оставить теми же.

Создать корректно заполненную заявку:

```text
Subject:     Load balancing check
Location:    Warehouse
Description: Самостоятельная проверка Load Balancing
Priority:    Medium
Target Date: будущая дата
```

Проверить, что Frappe выбрал пользователя с меньшим числом открытых `ToDo` для `Service Request`.

Если счёт одинаковый, заранее закрыть/открыть тестовые assignments так, чтобы разница была очевидна, а не угадывать результат.

После проверки **обязательно вернуть**:

```text
Rule = Round Robin
```

и сохранить Assignment Rule.

Финальная конфигурация курса остаётся Round Robin.

---

# 23. Commit Standard Notifications

Проверить diff и добавить только source Standard Notifications:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

Закоммитить app-owned Notification files с понятным сообщением, например:

```bash
git commit -m "Add service request notifications"
```

Не добавлять в Git:

```text
User records
ToDo
Notification Log
Assignment Rule database record
рабочие Service Request
пароли
```

---

# 24. Приёмка L9

L9 принят, если:

- создан `technician.two@example.com` и это первый урок, где он появляется;
- оба Technician имеют одинаковую базовую область доступа к Service Request;
- все тестовые заявки проходят Mandatory validation L4;
- New Notification приходит Supervisor;
- date-based Notification проверена как `1 day after Target Date`;
- Round Robin даёт последовательность One → Two → One;
- Due Date ToDo следует за Target Date;
- автоматическое назначение не меняет Workflow State;
- Closed Service Request закрывает Assignment Rule ToDo;
- ручной и автоматический assignment используют штатный ToDo;
- optional Load Balancing либо проверен и возвращён в Round Robin, либо сознательно пропущен как Optional;
- Assignment Rule остаётся site-specific и не попадает в universal fixtures;
- Git содержит Standard Notifications, но не рабочие данные.

После L9 переходим к **L10 — Web Form**.