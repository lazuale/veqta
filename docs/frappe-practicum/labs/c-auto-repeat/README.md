# Lab C. Auto Repeat

Lab C изучает штатное повторное создание Documents без изменения постоянной доменной модели и security baseline.

Используем существующий:

```text
Service Request
```

и временно включаем:

```text
Allow Auto Repeat
```

Базовая версия: **Frappe Framework v16.32.0**.

После лаборатории Auto Repeat и служебный Custom Field удаляются, Assignment Rule L9 возвращается, а Level 0/1 permission model `Service Request` остаётся исходной.

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
new Service Request
        ↓
optional Auto Repeat Assignee
        ↓
ToDo
```

```text
Auto Repeat ≠ Assignment Rule
Assignment ≠ Workflow
Automation ≠ permission escalation
```

---

# 2. Preconditions

После L11 active site:

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

На основном site существует:

```text
Service Request Auto Assignment
```

Workflow:

```text
New
Accepted
In Progress
Resolved
Closed
```

Security baseline:

```text
status → Permission Level 0

subject
location
equipment
description
priority
target_date
attachment
→ Permission Level 1
```

Technician Level 1 Write должен быть `No`.

---

# 3. Temporary mutation: отключить Assignment Rule

Временно:

```text
Service Request Auto Assignment
Disabled = Yes
```

Причина: Auto Repeat Assignee и Assignment Rule оба используют assignment/ToDo. Для чистого эксперимента оставляем один источник назначения.

---

# 4. Разрешить Auto Repeat

Под Administrator:

```text
DocType → Service Request
Allow Auto Repeat = Yes
```

Frappe создаёт служебный Custom Field:

```text
auto_repeat
```

Его не создаём вручную.

Это техническое поле лаборатории, а не новый business-content field core.

---

# 5. Проверить, что core Permission Levels не изменились

После `Allow Auto Repeat = Yes` сразу проверить `Service Request` metadata.

Должны остаться:

```text
status → permlevel 0

subject/location/equipment/description/priority/target_date/attachment
→ permlevel 1
```

Если включение Auto Repeat изменило эти поля вручную из-за ошибочной настройки ученика — лабораторию остановить и восстановить baseline.

---

# 6. Создать reference Service Request

Под Supervisor создать:

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

`Target Date` пуст специально: расписание Auto Repeat не должно путаться с due date заявки.

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

`Service Request.auto_repeat` должен ссылаться на созданный Auto Repeat.

Попытаться создать второй активный Auto Repeat на ту же reference заявку и получить штатный отказ.

---

# 9. Next Schedule Date

Проверить рассчитанный:

```text
Next Schedule Date
```

Не вводить его вручную.

---

# 10. Добавить Assignee

```text
Assignee: technician.one@example.com
Generate Separate Documents For Each Assignee = No
```

Generated Document получит assignment через штатный механизм:

```text
new Service Request
→ Assign To
→ ToDo
```

Это не выдаёт Technician Level 1 Write.

---

# 11. Submit on Creation — negative test

Попробовать:

```text
Submit on Creation = Yes
```

`Service Request` не Submittable, поэтому настройка несовместима.

Вернуть:

```text
Submit on Creation = No
```

---

# 12. Подготовить запуск на сегодня

Настроить schedule так, чтобы:

```text
Next Schedule Date = сегодня
```

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

---

# 14. Проверить generated Service Request

Найти новый Document с новым `name`.

Проверить:

```text
Subject
Location
Equipment
Description
Priority
Status = New
```

Generated request обязана соблюдать H-01 и ту же metadata model, что обычная заявка.

---

# 15. Проверить assignment generated Document

```text
Assigned To = technician.one@example.com
```

ToDo:

```text
Reference Type = Service Request
Reference Name = generated SR
Allocated To   = technician.one@example.com
```

Assignment Rule L9 Disabled, поэтому assignment пришёл из Auto Repeat.

---

# 16. Проверить Technician permissions на generated Document

Под `technician.one@example.com` открыть generated request.

Проверить:

```text
Level 1 content виден
Description/Priority/Target Date не writable
```

Assignment из Auto Repeat не должен менять field authority.

---

# 17. Assignment отдельно от Workflow

Generated request после назначения:

```text
Status = New
```

Под Supervisor:

```text
Accept
→ Status = Accepted
```

```text
Auto Repeat = когда создать
Assignment  = кому поручить
Workflow    = состояние процесса
```

---

# 18. Technician transition

Под Technician:

```text
Start Work
```

Переход должен работать, потому что `status` Level 0 и Technician имеет document-level Write.

Level 1 content при этом остаётся read-only.

После теста можно довести заявку до `Resolved` обычным Workflow.

---

# 19. Next Schedule Date после обработки

После успешного запуска проверить следующую рассчитанную дату.

Для Daily ожидается следующий день.

---

# 20. End Date / Disabled

Проверить корректную End Date и штатную validation на некорректной.

Проверить:

```text
Disabled = Yes
```

и отсутствие следующего активного запуска.

---

# 21. Где что хранится

```text
Reference Service Request
→ working data

Auto Repeat
→ schedule configuration

Generated Service Request
→ working data

ToDo
→ assignment data

Allow Auto Repeat
→ DocType capability metadata

auto_repeat
→ technical Custom Field
```

---

# 22. Git во время эксперимента

`Allow Auto Repeat = Yes` может изменить Standard metadata `Service Request`.

Runtime Auto Repeat/Service Request/ToDo в Git не входят.

При желании experiment можно зафиксировать отдельным commit, но rollback обязателен.

---

# 23. Rollback Auto Repeat

Удалить созданный Auto Repeat штатно.

Проверить:

```text
reference auto_repeat = пусто
```

Тестовые generated Documents удалить, если больше не нужны.

---

# 24. Rollback Allow Auto Repeat

Вернуть:

```text
DocType → Service Request
Allow Auto Repeat = No
```

Сохранить.

---

# 25. Rollback technical Custom Field

Проверить:

```text
Custom Field
Document Type = Service Request
Fieldname = auto_repeat
```

Если остался — удалить штатно.

```bash
bench --site facility-ops.localhost clear-cache
```

---

# 26. Restore Assignment Rule

```text
Service Request Auto Assignment
Disabled = No
Rule = Round Robin
```

---

# 27. Критический post-rollback permission gate

После всех cleanup действий проверить `Service Request` заново.

## Metadata

```text
status → permlevel 0

subject
location
equipment
description
priority
target_date
attachment
→ permlevel 1
```

## Role Permission

```text
Requester Level 0 Write = No
Technician Level 1 Write = No
Supervisor Level 1 Write = Yes
Supervisor Level 0 Delete = No
```

Lab C не принята, если Auto Repeat очищен, но security baseline изменён.

---

# 28. Final state

```text
Service Request.allow_auto_repeat = No
нет lab Auto Repeat
нет Service Request.auto_repeat Custom Field
Assignment Rule enabled
Rule = Round Robin
Workflow unchanged
Level 0/1 permissions unchanged
```

Core domain:

```text
Facility Location
Equipment
Service Request
```

---

# 29. State contract

## Temporary mutation

```text
Assignment Rule Disabled
Allow Auto Repeat Yes
auto_repeat Custom Field
Auto Repeat config
lab runtime Documents
```

## Rollback

```text
Auto Repeat removed
Allow Auto Repeat No
auto_repeat field removed
Assignment Rule enabled / Round Robin
```

## Final state

```text
original domain
original Workflow
original Level 0/1 permission model
Git clean
```

---

# 30. Приёмка

Лаборатория принята, если ученик может:

- disable L9 Assignment Rule;
- enable Allow Auto Repeat;
- создать reference request;
- создать Daily Auto Repeat;
- добавить Assignee;
- запустить native scheduler method;
- получить новый Service Request и ToDo;
- доказать `Status = New` после generation/assignment;
- доказать, что Technician assignment не даёт Level 1 Write;
- выполнить `Accept` и Technician Workflow transition;
- удалить Auto Repeat;
- отключить Allow Auto Repeat;
- удалить technical Custom Field;
- вернуть Round Robin Assignment Rule;
- доказать восстановление исходной Level 0/1 permission model;
- получить clean Git.

Главный вывод:

```text
Auto Repeat ≠ Assignment Rule
Assignment ≠ Workflow
Automation ≠ permission authority
```
