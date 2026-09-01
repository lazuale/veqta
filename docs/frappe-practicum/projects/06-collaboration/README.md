# L6. Совместная работа

L6 не добавляет новые предметные DocType и не добавляет поле исполнителя в `Service Request`.

Цель: изучить штатные `Assign To`, `ToDo`, Comments, Timeline, Tags и Kanban и зафиксировать академически точную границу:

```text
Permission
= право доступа

Assignment
= ответственность / рабочая очередь

Status
= состояние процесса
```

**Assignment не является механизмом авторизации.** Наличие ToDo не заменяет Role Permission и не означает, что только assignee имеет право работать с Document.

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Проверить состояние после L5

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно подтвердить:

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

Пользователи:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

После cleanup L5 у основного Technician нет постоянного Location User Permission.

---

# 2. Выбрать New-заявку

Под Supervisor открыть незакрытую:

```text
Status = New
```

До назначения:

```text
Assigned To = пусто
Status = New
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

Через Awesomebar открыть `ToDo` и найти запись:

```text
Allocated To   = technician.one@example.com
Reference Type = Service Request
Reference Name = выбранный SR-.....
Status         = Open
```

Фиксируем:

```text
Assign To
→ создаёт ToDo
→ обновляет штатное представление assignment
→ не создаёт наше бизнес-поле исполнителя
```

---

# 5. Assignment не меняет Status

Вернуться в Service Request.

После Assign To:

```text
Assigned To = technician.one@example.com
Status = New
```

Это **нормальное состояние**, а не ошибка.

Теперь вручную изменить:

```text
New → Accepted
```

Сохранить.

`Accepted` означает:

```text
заявка принята в рабочий процесс
```

а не:

```text
Frappe доказал наличие конкретного assignee
```

---

# 6. Проверить Technician

Войти:

```text
technician.one@example.com
```

Открыть свою очередь / ToDo и перейти к заявке.

Проверить:

- заявка открывается;
- assignment виден;
- ToDo ссылается на нужный Service Request.

Вручную изменить:

```text
Accepted → In Progress
```

Сохранить.

До L7 `Status` ещё обычный Select.

---

# 7. Важная проверка: Assignment не является ACL

Под Supervisor назначить другую заявку `technician.one@example.com`.

Затем войти другим пользователем с ролью `Facility Technician`, если такой пользователь уже существует на стенде. Если второго Technician ещё нет, эту проверку повторим в L9.

Смысл проверки:

```text
ToDo
не является record-level permission rule
```

В базовой архитектуре Technician получает доступ к Service Request через Role Permission, а ToDo отвечает только за ответственность.

Не строить вывод:

```text
не назначен
→ значит сервер обязан запретить Document
```

Штатный Frappe так не устроен.

---

# 8. Comments и Timeline

Добавить Comment:

```text
Проверка начата. Требуется дополнительный осмотр оборудования.
```

Посмотреть Timeline.

Различать:

```text
Timeline
= общий интерфейс активности

Track Changes / Version
= аудит изменений полей

Comment
= пользовательская запись

Assignment
= отдельное поручение
```

Не создавать собственный журнал комментариев.

---

# 9. Закрыть ToDo и сравнить со Status

Закрыть назначение штатным действием.

Проверить:

```text
ToDo Status = Closed
```

Service Request не обязан стать Closed.

Если Status был `In Progress`, вручную перевести:

```text
In Progress → Resolved
```

Фиксируем:

```text
закрыть ToDo
≠ закрыть Service Request
```

И обратное тоже не является универсальным правилом без отдельной automation policy.

---

# 10. Повторное и duplicate assignment

На другой заявке снова назначить того же Technician.

Проверить отдельные ToDo по разным `reference_name`.

На уже назначенной заявке повторить Assign To тому же пользователю и зафиксировать фактическое штатное поведение Frappe для duplicate active ToDo.

Не писать обходной registry.

---

# 11. Tags

Добавить лёгкие метки:

```text
hvac
urgent-check
network
```

Не дублировать структурированные поля:

```text
Priority
Status
Location
Equipment
```

---

# 12. Создать Kanban

Создать:

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

Сравнить одну запись в:

```text
List View
Form View
Kanban
```

Переместить:

```text
Accepted → In Progress
```

Проверить в Form View:

```text
Status = In Progress
```

До Workflow это обычное изменение Select field.

---

# 14. Permissions через Kanban

Requester должен видеть только свои Service Request из-за `If Owner` L5.

Technician работает в своей Role-based области доступа.

```text
List / Form / Kanban
→ не создают разные permissions
```

Если основного Technician всё ещё ограничивает Location User Permission, это ошибка cleanup L5.

---

# 15. Не путать три оси

Нормальная комбинация:

```text
Assigned To = technician.one@example.com
Status = In Progress
```

Но из этого нельзя вывести:

```text
Status = Accepted
→ обязательно Assigned To заполнен
```

и нельзя вывести:

```text
Assigned To = Technician One
→ только Technician One имеет security permission
```

Это фундаментальная граница дальнейшей архитектуры.

---

# 16. Проверить auto-Share как границу Assign To

Штатный `Assign To` в `v16.32.0` проверяет доступ assignee к reference document.

Если доступа нет и document sharing разрешён, Frappe способен создать `DocShare`; если sharing отключён — получить Missing Permission.

В нашем основном deployment Technician уже имеет нормальный Role Permission, поэтому assignment **не должен тихо менять access model через Share**.

Именно поэтому временные Location User Permission из L5 не оставляются на основных Technician.

---

# 17. Git

L6 работает с site data/configuration:

```text
ToDo
Comment
Tag
Kanban Board
```

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Если Standard metadata не менялась, working tree остаётся clean.

---

# 18. Приёмка L6

L6 принят, если ученик может показать:

- Assign To и соответствующий ToDo;
- `Assignment ≠ Status`;
- `Assignment ≠ authorization`;
- нормальное состояние `Assigned To заполнен + Status New`;
- Comment и Timeline;
- `ToDo Closed ≠ Service Request Closed`;
- Tags;
- Kanban `Service Request Status Board` с колонкой `Accepted`;
- одинаковую permission-модель List/Form/Kanban;
- отсутствие постоянного Location User Permission у основного Technician;
- отсутствие неожиданных DocShare как нормального механизма назначения;
- чистый Git.

После L6 переходим к **L7 — Workflow**. Kanban пока оставляем только для сравнения, затем удаляем.