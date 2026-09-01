# Lab C. Auto Repeat

Lab C изучает штатное повторное создание Documents без изменения постоянной доменной модели.

Используем существующий:

```text
Service Request
```

и временно включаем:

```text
Allow Auto Repeat
```

Базовая версия: **Frappe Framework v16.32.0**.

После лаборатории Auto Repeat и служебный Custom Field удаляются, Assignment Rule L9 возвращается в исходное состояние.

---

# 1. Что изучаем

```text
Allow Auto Repeat
Auto Repeat
Reference Document
Frequency
Start / End Date
Next Schedule Date
Assignee
Assign To / ToDo
scheduler
background queue
```

Архитектура:

```text
Reference Service Request
        ↓
Auto Repeat schedule
        ↓
scheduler
        ↓
новый Service Request
        ↓
optional Auto Repeat Assignee
        ↓
ToDo
```

Auto Repeat не является Workflow и не является Assignment Rule.

---

# 2. Preconditions

После L11 active site снова:

```text
facility-ops.localhost
```

Проверить:

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps
bench --site facility-ops.localhost scheduler status
bench --site facility-ops.localhost doctor

cd apps/facility_ops
git status
```

На основном site L9 должен существовать:

```text
Service Request Auto Assignment
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

# 3. Temporary mutation: отключить Assignment Rule

Временно:

```text
Service Request Auto Assignment
Disabled = Yes
```

Причина:

```text
Auto Repeat Assignee
и
Assignment Rule
```

оба используют штатный assignment/ToDo механизм.

Для чистого эксперимента оставляем один источник назначения.

---

# 4. Разрешить Auto Repeat

Под Administrator:

```text
DocType → Service Request
Allow Auto Repeat = Yes
```

Сохранить.

Frappe создаёт служебный Custom Field:

```text
auto_repeat
```

Его не создаём вручную.

---

# 5. Проверить Custom Field

Через `Custom Field` найти:

```text
Document Type = Service Request
Fieldname     = auto_repeat
```

Фиксируем:

```text
Allow Auto Repeat
= metadata capability

auto_repeat
= служебная связь Document → Auto Repeat
```

---

# 6. Создать reference Service Request

```text
Subject:     Periodic inspection template
Location:    Room 101
Equipment:   логично подходящий Equipment или пусто
Description: Template for Auto Repeat laboratory
Priority:    Medium
Target Date: пусто
```

Получить:

```text
Status = New
```

`Target Date` оставляем пустым специально: он Optional и не должен магически становиться датой расписания.

---

# 7. Создать Auto Repeat

```text
Reference Document Type: Service Request
Reference Document:      <reference SR>
Start Date:              сегодня
Frequency:               Daily
Disabled:                No
Submit on Creation:      No
Notify by Email:         No
```

End Date пока пусто.

---

# 8. Проверить единственность связи

Reference `Service Request.auto_repeat` должен ссылаться на созданный Auto Repeat.

Попытаться создать второй Auto Repeat на ту же reference заявку.

Frappe должен запретить дублирующую активную связь.

---

# 9. Next Schedule Date

Проверить рассчитанный:

```text
Next Schedule Date
```

Не вводить его вручную.

Для немедленной лабораторной проверки позже сдвинем Start Date так, чтобы schedule подошёл на сегодня.

---

# 10. Добавить Assignee

```text
Assignee:
technician.one@example.com

Generate Separate Documents For Each Assignee = No
```

При generated Document Frappe использует штатный assignment mechanism:

```text
new Service Request
→ Assign To
→ ToDo
```

Это не создаёт field `Assigned Technician`.

---

# 11. Submit on Creation — отрицательный тест

Попробовать:

```text
Submit on Creation = Yes
```

`Service Request` не Submittable.

Frappe должен отклонить несовместимую настройку.

Вернуть:

```text
Submit on Creation = No
```

---

# 12. Подготовить запуск на сегодня

Изменить schedule так, чтобы:

```text
Next Schedule Date = сегодня
```

Например после уже созданного Auto Repeat сдвинуть Start Date на вчера и проверить пересчёт.

Не править `Next Schedule Date` напрямую.

---

# 13. Запустить штатный scheduler method

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost execute \
  frappe.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry
```

Проверить:

```bash
bench --site facility-ops.localhost show-pending-jobs
bench --site facility-ops.localhost doctor
```

Auto Repeat использует штатную background queue.

---

# 14. Проверить generated Service Request

Найти новую заявку с тем же Subject.

У неё должен быть новый `name`.

Проверить копируемые значения:

```text
Subject
Location
Equipment
Description
Priority
Status = New
```

Это новый обычный Document.

---

# 15. Проверить assignment generated Document

```text
Assigned To = technician.one@example.com
```

Связанный ToDo:

```text
Reference Type = Service Request
Reference Name = generated SR
Allocated To   = technician.one@example.com
```

Assignment Rule L9 сейчас Disabled, поэтому assignment пришёл именно из Auto Repeat.

---

# 16. Assignment остаётся отдельным от Workflow

Generated request после назначения остаётся:

```text
Status = New
```

Под Supervisor выполнить:

```text
Accept
```

Получить:

```text
Status = Accepted
```

Фиксируем:

```text
Auto Repeat
= когда создать Document

Assignment
= кому поручить

Workflow
= состояние процесса
```

`Accepted` не означает «назначен», а assignment не является authorization.

---

# 17. Next Schedule Date после обработки

После успешного запуска проверить переход Next Schedule Date на следующую рассчитанную дату.

Для Daily ожидается следующий день.

---

# 18. End Date

Задать будущую End Date и посмотреть schedule.

Попробовать некорректный вариант по правилам Auto Repeat и получить штатную validation error.

После теста вернуть корректное значение или очистить End Date.

---

# 19. Disabled

Установить:

```text
Disabled = Yes
```

Проверить inactive/disabled состояние и отсутствие следующего активного запуска.

Если нужен следующий тест — временно вернуть No.

---

# 20. Где что хранится

```text
Reference Service Request
→ working data

Auto Repeat
→ schedule configuration Document

Generated Service Request
→ working data

ToDo
→ assignment data

Allow Auto Repeat
→ DocType metadata

auto_repeat
→ служебный Custom Field
```

---

# 21. Git во время эксперимента

`Allow Auto Repeat = Yes` меняет Standard metadata `Service Request`, поэтому source diff возможен.

Runtime:

```text
Auto Repeat
reference/generated Service Request
ToDo
```

не являются app source.

При желании сделать отдельный experiment commit, чтобы потом увидеть rollback.

---

# 22. Rollback: удалить Auto Repeat

Удалить созданный `Auto Repeat` штатно.

Проверить reference document:

```text
auto_repeat = пусто
```

Тестовые generated Documents можно удалить отдельно, если они больше не нужны.

---

# 23. Rollback: Allow Auto Repeat

Вернуть:

```text
DocType → Service Request
Allow Auto Repeat = No
```

Сохранить.

---

# 24. Rollback: служебный Custom Field

Проверить:

```text
Custom Field
Document Type = Service Request
Fieldname = auto_repeat
```

Если запись осталась — удалить штатно.

Затем:

```bash
bench --site facility-ops.localhost clear-cache
```

---

# 25. Rollback: вернуть Assignment Rule

```text
Service Request Auto Assignment
Disabled = No
Rule = Round Robin
```

Сохранить.

После Lab C основной site снова имеет operating policy L9.

---

# 26. Final state

После Lab C:

```text
Service Request.allow_auto_repeat = No
нет Auto Repeat лаборатории
нет Service Request.auto_repeat Custom Field
Assignment Rule включён
Rule = Round Robin
Workflow states не изменены
Status list = New / Accepted / In Progress / Resolved / Closed
```

Core domain снова:

```text
Facility Location
Equipment
Service Request
```

---

# 27. Приёмка

Лаборатория принята, если ученик может выполнить:

```text
disable L9 Assignment Rule
→ enable Allow Auto Repeat
→ create reference request
→ create Daily Auto Repeat
→ add Assignee
→ schedule today
→ run native scheduler method
→ receive new Service Request
→ see ToDo
→ prove Status remains New
→ Supervisor Accept
→ delete Auto Repeat
→ disable Allow Auto Repeat
→ remove technical Custom Field
→ restore Round Robin Assignment Rule
```

И объяснить:

```text
Auto Repeat ≠ Assignment Rule
Assignment ≠ Workflow
Accepted ≠ Assigned To
```
