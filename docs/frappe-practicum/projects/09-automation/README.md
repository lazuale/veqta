# L9. Автоматизация

L9 автоматизирует уже работающий процесс `Service Request` штатными механизмами Frappe.

Новых предметных DocType нет.

Цель урока:

```text
новая заявка
→ системное уведомление Supervisor
→ автоматическое назначение Technician
→ ToDo с due date из Target Date
→ закрытие заявки закрывает ToDo
→ просроченная заявка попадает в date-based Notification
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
Git working tree clean
```

Во время практики `bench start` должен быть запущен в отдельном терминале.

---

# 2. Зафиксировать границу урока

До L9 всё уже можно делать вручную:

```text
создать Service Request
→ Assign To
→ Workflow Action
→ ToDo
→ закрыть заявку
```

Теперь автоматизируем только повторяемые действия.

Не создаём:

```text
Automation Log
Request Dispatcher
Notification Queue
Auto Assignment Record
```

Frappe уже имеет необходимые служебные Documents.

---

# 3. Создать второго Technician

Для проверки Round Robin нужен второй исполнитель.

Под `Administrator` открыть:

```text
User
```

Создать:

```text
Email:              technician.two@example.com
First Name:         Technician Two
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Technician
```

Задать учебный пароль.

Не выдавать:

```text
System Manager
Administrator
```

Для проверки автоматического назначения все тестовые заявки создаём в:

```text
Room 101
```

Так `technician.one@example.com` не конфликтует со своим User Permission из L5.

---

# 4. Создать Notification на новую заявку

Через Awesomebar открыть:

```text
Notification
```

Создать:

```text
Name:               New Service Request
Enabled:            Yes
Is Standard:        Yes
Module:             Facility Operations
Channel:            System Notification
Send Alert On:      New
Document Type:      Service Request
Notification Type: Alert
Notification Title: New service request {{ doc.name }}
Notification Message: {{ doc.subject }}
```

Condition не нужен.

В `Recipients` добавить:

```text
Receiver By Role = Facility Supervisor
```

Сохранить.

Собственный Email Account не нужен, потому что используем:

```text
Channel = System Notification
```

---

# 5. Проверить Notification на New

Войти:

```text
requester.one@example.com
```

Создать:

```text
Subject:     Automation notification test
Location:    Room 101
Priority:    Medium
Target Date: любая будущая дата
```

Сохранить.

Затем войти:

```text
supervisor.one@example.com
```

Проверить верхний список уведомлений и `Notification Log`.

Должно появиться уведомление со ссылкой на созданный `Service Request`.

Если его нет, сначала проверить:

```bash
bench --site facility-ops.localhost doctor
bench --site facility-ops.localhost show-pending-jobs
```

а не создавать новый скрипт.

---

# 6. Создать date-based Notification для просрочки

Создать вторую `Notification`:

```text
Name:               Overdue Service Request
Enabled:            Yes
Is Standard:        Yes
Module:             Facility Operations
Channel:            System Notification
Send Alert On:      Days After
Document Type:      Service Request
Reference Date:     Target Date
Days Before or After: 1
Notification Type: Alert
Notification Title: Overdue service request {{ doc.name }}
Notification Message: {{ doc.subject }}
```

Condition Type:

```text
Filters
```

В Filters задать:

```text
Status != Closed
```

Recipient:

```text
Receiver By Role = Facility Supervisor
```

Сохранить.

Смысл настройки:

```text
Target Date = вчера
+
Days After = 1
+
Status != Closed
→ сегодня заявка считается подходящей для уведомления
```

---

# 7. Проверить Preview date-based Notification

На форме `Overdue Service Request` нажать штатный:

```text
Preview
```

Выбрать подходящую заявку.

Проверить:

```text
Meets Condition? = Yes
```

Для `Closed` заявки должно быть:

```text
Meets Condition? = No
```

Затем использовать кнопку date-based Notification:

```text
Get Alerts for Today
```

Она должна показать Documents, которые подходят под текущую дату.

---

# 8. Подготовить тестовую просроченную заявку

Создать под Requester новую заявку:

```text
Subject:     Overdue automation test
Location:    Room 101
Priority:    High
Target Date: вчерашняя дата
```

После сохранения оставить её незакрытой.

Запомнить номер.

---

# 9. Проверить scheduler-job вручную

Date-based Notification запускается scheduler-ом.

Для немедленной проверки не ждём следующего суточного запуска.

Выполнить штатный job вручную:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost execute \
  frappe.email.doctype.notification.notification.trigger_daily_alerts
```

После выполнения войти под:

```text
supervisor.one@example.com
```

Проверить `Notification Log`.

Должно появиться уведомление по просроченной заявке.

Важно различать:

```text
bench execute trigger_daily_alerts
= немедленная проверка конкретного scheduler-job

scheduler status / doctor
= проверка, что scheduler и workers вообще работают
```

---

# 10. Создать Assignment Rule

Вернуться под `Administrator`.

Через Awesomebar открыть:

```text
Assignment Rule
```

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

---

# 11. Настроить Assignment Days

В таблице `Assignment Days` нажать штатную кнопку:

```text
All Days
```

Должны появиться:

```text
Monday
Tuesday
Wednesday
Thursday
Friday
Saturday
Sunday
```

Для учебного стенда правило должно работать независимо от дня прохождения курса.

---

# 12. Настроить Round Robin

В Assignment Rule выбрать:

```text
Rule = Round Robin
```

В `Users` добавить в таком порядке:

```text
technician.one@example.com
technician.two@example.com
```

Сохранить правило.

Frappe Round Robin хранит `Last User` в самом Assignment Rule.

Собственный счётчик распределения не создаём.

---

# 13. Проверить первое автоматическое назначение

Войти:

```text
requester.one@example.com
```

Создать:

```text
Subject:     Auto assignment A
Location:    Room 101
Priority:    Medium
Target Date: будущая дата
```

Сохранить.

Не использовать `Assign To` вручную.

Под Supervisor открыть заявку.

Проверить:

```text
Status = New
Assigned To = technician.one@example.com
```

Открыть созданный `ToDo`.

Проверить:

```text
Reference Type = Service Request
Reference Name = номер заявки
Allocated To   = technician.one@example.com
Due Date       = Target Date заявки
Assignment Rule = Service Request Auto Assignment
```

Главный вывод:

```text
Assignment Rule
→ назначил человека

но Status остался New
```

То есть автоматическое назначение по-прежнему не заменяет Workflow.

---

# 14. Проверить Round Robin второй заявкой

Создать ещё одну:

```text
Subject:     Auto assignment B
Location:    Room 101
Priority:    Medium
Target Date: будущая дата
```

Сохранить.

Проверить:

```text
Assigned To = technician.two@example.com
```

Открыть Assignment Rule и посмотреть:

```text
Last User
```

После двух заявок Round Robin должен последовательно использовать двух пользователей.

---

# 15. Проверить третью заявку

Создать:

```text
Auto assignment C
```

Ожидается возврат к первому пользователю:

```text
technician.one@example.com
```

Получаем цикл:

```text
Technician One
→ Technician Two
→ Technician One
→ ...
```

---

# 16. Проверить Due Date synchronization

Выбрать автоматически назначенную заявку.

Изменить:

```text
Target Date
```

на другую будущую дату и сохранить.

Открыть соответствующий `ToDo`.

Его Due Date должен обновиться вслед за `Service Request.target_date`, потому что Assignment Rule настроен:

```text
Due Date Based On = Target Date
```

Никакая отдельная автоматизация для синхронизации даты не нужна.

---

# 17. Провести автоматически назначенную заявку через Workflow

Под Supervisor выполнить:

```text
Mark Assigned
```

Под назначенным Technician:

```text
Start Work
Resolve
```

Под Supervisor:

```text
Close
```

Проверить:

```text
Service Request.status = Closed
```

Затем открыть связанный `ToDo`.

Ожидается:

```text
Status = Closed
```

Это результат:

```text
Assignment Rule Close Condition
status == "Closed"
```

---

# 18. Сравнить ручное и автоматическое назначение

Временно отключить Assignment Rule:

```text
Disabled = Yes
```

Создать тестовую заявку:

```text
Subject:     Manual assignment comparison
Location:    Room 101
```

Сохранить.

Проверить, что автоматического ToDo нет.

Под Supervisor выполнить:

```text
Assign To
→ technician.one@example.com
```

Сравнить два ToDo:

```text
ручной Assign To
автоматический Assignment Rule
```

В обоих случаях рабочая сущность назначения — штатный:

```text
ToDo
```

После проверки снова включить Assignment Rule.

Тестовую заявку можно удалить, если она больше не нужна.

---

# 19. Проверить, что Assignment Rule не двигает Workflow

Создать новую заявку при включённом Assignment Rule.

Сразу после сохранения должно быть одновременно:

```text
Assigned To = Technician
Status      = New
```

Только Supervisor выполняет:

```text
Mark Assigned
```

после чего:

```text
Status = Assigned
```

Фиксируем окончательно:

```text
Assignment
= кто выполняет

Workflow
= состояние процесса
```

---

# 20. Посмотреть служебные Documents

После практики открыть:

```text
Notification Log
ToDo
Assignment Rule
Notification
```

Убедиться, что автоматизация не создала никаких наших служебных DocType.

Используется штатная цепочка:

```text
Service Request
├── Notification → Notification Log
└── Assignment Rule → ToDo
```

---

# 21. Проверить source и Git

Перейти:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Две Notification созданы как:

```text
Is Standard = Yes
Module      = Facility Operations
```

Поэтому Frappe должен экспортировать их в source app.

Найти файлы:

```bash
find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -i notification
```

Не редактировать экспортированные файлы вручную.

---

# 22. Почему Assignment Rule пока не в Git

`Assignment Rule` не имеет режима `Is Standard` как Notification.

Поэтому созданный:

```text
Service Request Auto Assignment
```

сейчас является configuration Document текущего site.

То же относится к:

```text
technician.two@example.com
```

и другим site configuration records.

В L9 не добавляем их в `hooks.py` наугад.

В L11 определим нужные fixtures и выполним:

```text
bench export-fixtures
```

---

# 23. Commit Standard Notifications

Проверить diff:

```bash
git status
git diff
```

Добавить только осознанно созданные app-owned Notification files:

```bash
git add facility_ops/facility_operations

git diff --cached
```

Убедиться, что в diff нет:

```text
Service Request Documents
User passwords
ToDo
Notification Log
Assignment Rule database record
```

Commit:

```bash
git commit -m "Add service request notifications"
git status
```

Ожидается:

```text
working tree clean
```

---

# 24. Самостоятельная практика

## A. Load Balancing

Временно изменить правило:

```text
Round Robin
→ Load Balancing
```

Создать несколько заявок и посмотреть, как выбирается пользователь с меньшим числом открытых `ToDo` для `Service Request`.

После проверки вернуть:

```text
Round Robin
```

## B. Notification Filter

В `New Service Request` временно добавить Filter:

```text
Priority = High
```

Проверить High и Medium заявки.

После проверки убрать Filter.

## C. Scheduler

Ещё раз выполнить:

```bash
bench --site facility-ops.localhost scheduler status
bench --site facility-ops.localhost doctor
bench --site facility-ops.localhost show-pending-jobs
```

Уметь объяснить назначение каждой команды.

---

# 25. Приёмка L9

L9 принят, если ученик может показать:

## Notification

```text
New Service Request
→ System Notification
→ Event = New
→ Facility Supervisor
```

## Date-based Notification

```text
Overdue Service Request
→ Days After = 1
→ Reference Date = Target Date
→ Status != Closed
```

## Assignment Rule

```text
Service Request Auto Assignment
Rule = Round Robin
Users:
- technician.one@example.com
- technician.two@example.com
Due Date Based On = Target Date
Assign Condition = status == "New"
Close Condition  = status == "Closed"
```

## Результат автоматики

```text
new Service Request
→ Notification Log
→ ToDo
→ due date синхронизирован
→ Workflow остаётся отдельным механизмом
```

## Scheduler

Ученик умеет проверить:

```text
scheduler status
doctor
show-pending-jobs
```

и вручную запустить конкретный штатный daily Notification job для теста.

## Архитектура

По-прежнему только три предметных DocType:

```text
Facility Location
Equipment
Service Request
```

Собственного Python/JS нет.

---

# Что должно остаться после L9

```text
Service Request
│
├── Workflow
├── Assignment Rule
│     └── ToDo
├── New Notification
│     └── Notification Log
└── Overdue Notification
      └── scheduler
```

Следующий урок:

```text
L10 — Web Form
```

В нём откроем внешний вход в тот же `Service Request`, не создавая второй процесс заявок.
