# L6. Совместная работа

L6 не добавляет новые предметные DocType и не добавляет поле исполнителя в `Service Request`.

Цель — изучить штатные `Assign To`, `ToDo`, Comments, Timeline, Tags и Kanban, не разрушая permission model L5.

Базовая версия: **Frappe Framework v16.32.0**.

Главная схема:

```text
Level 0 Permission
= document authority

Level 1 Permission
= business-field authority

Assignment
= ответственность / рабочая очередь

Status
= состояние процесса
```

`Assignment` не является authorization и не расширяет Permission Level.

---

# 1. Проверить состояние после L5

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Ожидается:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

Основные роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

## Level 0 Service Request

```text
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No
```

## Level 1 content

```text
subject
location
equipment
description
priority
target_date
attachment
```

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

`status` остаётся Level 0.

После cleanup L5 у основного Technician нет постоянного Location User Permission.

---

# 2. Выбрать New-заявку

Под Supervisor открыть:

```text
Status = New
Assigned To = пусто
```

---

# 3. Назначить через Assign To

```text
Assign To
→ technician.one@example.com
```

Описание:

```text
Проверить заявку и зафиксировать результат.
```

При необходимости указать Due Date.

Не создавать поле `Assigned Technician`.

---

# 4. Проверить ToDo

Найти ToDo:

```text
Allocated To   = technician.one@example.com
Reference Type = Service Request
Reference Name = выбранный SR-.....
Status         = Open
```

```text
Assign To
→ создаёт ToDo
→ обновляет штатное assignment-представление
→ не создаёт наше business field
```

---

# 5. Assignment не меняет Status и permissions

После Assign To:

```text
Assigned To = technician.one@example.com
Status = New
```

И одновременно:

```text
Technician Level 1 Write = No
```

Assignment не должен превращать assignee в редактора `Description`, `Priority`, `Target Date` и других Level 1 fields.

До L7 Supervisor вручную меняет:

```text
New → Accepted
```

`Accepted` означает принятие заявки в процесс, а не доказательство конкретного assignee.

---

# 6. Проверить Technician

Войти:

```text
technician.one@example.com
```

Открыть ToDo и Service Request.

Проверить:

```text
assignment виден
reference открывается
Level 1 content читается
Level 1 content не редактируется
```

Минимум проверить:

```text
Description
Priority
Target Date
```

До L7 `status` ещё обычный Level 0 Select, поэтому вручную изменить:

```text
Accepted → In Progress
```

и сохранить.

Ключевой вывод:

```text
Technician document Write
позволяет сохранить Level 0 status

но

не означает Level 1 content Write
```

---

# 7. Assignment не является ACL

Под Supervisor назначить другую заявку Technician One.

Если второго Technician ещё нет, полноценную cross-technician проверку повторить в L9 после создания `technician.two@example.com`.

Нельзя выводить:

```text
не назначен
→ сервер обязан запретить Document
```

ToDo не является record-level permission rule.

---

# 8. Comments и Timeline

Добавить Comment:

```text
Проверка начата. Требуется дополнительный осмотр оборудования.
```

Сравнить:

```text
Timeline
Track Changes / Version
Comment
Assignment
```

Не создавать собственный журнал комментариев.

---

# 9. Закрыть ToDo и сравнить со Status

Закрыть assignment.

Получить:

```text
ToDo Status = Closed
```

Service Request не обязан стать Closed.

Если Status был `In Progress`, Technician может до L7 вручную изменить Level 0 `status`:

```text
In Progress → Resolved
```

```text
ToDo Closed
≠ Service Request Closed
```

---

# 10. Duplicate assignment

На другой заявке снова назначить того же Technician.

На уже назначенной заявке повторить Assign To тому же User и зафиксировать фактическое штатное поведение Frappe для duplicate active ToDo.

Не создавать собственный assignment registry.

---

# 11. Tags

Добавить лёгкие метки:

```text
hvac
urgent-check
network
```

Не дублировать структурированные:

```text
Priority
Status
Location
Equipment
```

---

# 12. Создать Kanban

```text
Board Name:        Service Request Status Board
Reference DocType: Service Request
Field:             Status
```

Колонки:

```text
New
Accepted
In Progress
Resolved
Closed
```

---

# 13. Kanban — те же Documents

Сравнить одну запись в List/Form/Kanban.

Переместить:

```text
Accepted → In Progress
```

Проверить:

```text
Status = In Progress
```

До Workflow это обычное изменение Level 0 Select.

Kanban не даёт отдельное право менять Level 1 content.

---

# 14. Permissions через views

Requester видит только свои Service Request из-за `If Owner`.

Technician имеет одинаковую document permission-area в List/Form/Kanban и одинаковый Level 1 read-only content.

```text
List / Form / Kanban
→ разные views
→ не разные permission models
```

---

# 15. Не путать четыре оси

Нормально:

```text
Assigned To = technician.one@example.com
Status = In Progress
```

Но нельзя выводить:

```text
Accepted → обязательно существует ToDo
Assigned To → только assignee имеет access
Assigned To → assignee получил Level 1 Write
```

---

# 16. Auto-Share boundary Assign To

`Assign To` в `v16.32.0` проверяет access assignee к reference document.

Если доступа нет:

```text
sharing разрешён
→ возможен DocShare

sharing запрещён
→ возможен Missing Permission
```

Поэтому основные Technician имеют совместимый базовый document access.

Это не повод расширять Level 1 Write.

---

# 17. Git

L6 работает в основном с site data/configuration:

```text
ToDo
Comment
Tag
Kanban Board
```

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Standard Service Request metadata в L6 не меняем.

---

# 18. State contract L6

## Preconditions

```text
L5 Level 0 + Level 1 matrix
permission experiments cleaned
```

## Persistent

```text
none in Standard metadata
```

## Output

```text
Assignment demonstrated
ToDo demonstrated
Technician Level 1 content still read-only
manual Level 0 Status still works before Workflow
Kanban exists for L7 comparison
```

---

# 19. Приёмка L6

L6 принят, если:

- Assign To создаёт ToDo;
- `Assignment ≠ Status`;
- `Assignment ≠ authorization`;
- assignment не меняет Level 1 permissions;
- Technician видит business content, но не редактирует Level 1 fields;
- Technician до L7 может менять обычный Level 0 Status;
- Comment и Timeline проверены;
- `ToDo Closed ≠ Service Request Closed`;
- Tags проверены;
- Kanban использует `New / Accepted / In Progress / Resolved / Closed`;
- List/Form/Kanban не создают разные permission models;
- основной Technician не имеет Location User Permission;
- unexpected DocShare не используется как нормальная архитектура assignment;
- Git clean.

После L6 переходим к **L7 — Workflow**. Kanban пока оставляем только для сравнения, затем удаляем.
