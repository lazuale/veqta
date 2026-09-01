# L7. Workflow

L7 переводит `Service Request` с ручного `Status` на управляемый Workflow.

Новых предметных DocType нет.

Цель: оставить уже знакомые состояния заявки, но передать переходы между ними штатному Workflow Frappe.

Базовая версия: **Frappe Framework v16.32.0**.

## Результат

```text
New
 │ Mark Assigned / Facility Supervisor
 ▼
Assigned
 │ Start Work / Facility Technician
 ▼
In Progress
 │ Resolve / Facility Technician
 ▼
Resolved
 │ Close / Facility Supervisor
 ▼
Closed
```

Поле состояния остаётся одно:

```text
Service Request.status
```

Никакого второго `workflow_state` не создаём.

Все состояния имеют:

```text
docstatus = 0
```

`Service Request` остаётся обычным, не Submittable Document.

---

# 1. Проверить состояние после L6

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно получить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

Должны существовать роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

и минимум пользователи:

```text
requester.one@example.com
technician.one@example.com
supervisor.one@example.com
```

Для тестов Technician используем заявки `Room 101`, потому что после L5 у него действует соответствующий `User Permission`.

---

# 2. Ещё раз увидеть проблему обычного Select

До создания Workflow открыть тестовую заявку под пользователем с `Write`.

Временно изменить:

```text
New → Closed
```

Сохранить и затем вернуть нормальное состояние.

До Workflow поле `Status` всего лишь ограничивает набор значений:

```text
Select
= допустимые значения

Select
≠ допустимые переходы
```

---

# 3. Передать существующий Status под управление Workflow

В `Service Request` уже есть:

```text
status
```

со значениями:

```text
New
Assigned
In Progress
Resolved
Closed
```

Именно его используем как:

```text
Workflow State Field = status
```

Frappe v16.32.0 создаёт скрытый Custom Field только если указанного Workflow State Field в DocType нет.

Поэтому не создаём:

```text
workflow_state
request_state
workflow_status
```

---

# 4. Сделать Status Read Only

Открыть Standard DocType:

```text
Service Request
```

Для поля:

```text
Status
fieldname: status
```

включить:

```text
Read Only = Yes
```

Оставить:

```text
Default = New
```

и прежние Options.

Теперь нормальный пользователь видит состояние, а перевод выполняет Workflow.

Это единственное изменение metadata приложения в L7.

Проверить diff:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

Пока не commit.

---

# 5. Создать Workflow State

Через Awesomebar открыть:

```text
Workflow State
```

Создать пять записей:

```text
New
Assigned
In Progress
Resolved
Closed
```

Названия должны точно совпадать со значениями `Service Request.status`.

`Workflow State` — штатная конфигурация Frappe, а не новый предметный справочник приложения.

---

# 6. Создать Workflow Action Master

Создать четыре действия:

```text
Mark Assigned
Start Work
Resolve
Close
```

Первое специально называется `Mark Assigned`.

Нужно различать:

```text
Assign To
→ создаёт ToDo и назначает работу человеку

Mark Assigned
→ переводит Service Request в состояние Assigned
```

Workflow не заменяет Assignment.

---

# 7. Создать Service Request Workflow

Создать новый `Workflow`:

```text
Workflow Name:        Service Request Workflow
Document Type:        Service Request
Is Active:            No
Workflow State Field: status
```

Пока оставить выключенными:

```text
Send Email Alert
Enable Action Confirmation
```

---

# 8. Настроить Document States

Добавить:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| New | 0 | Facility Requester |
| Assigned | 0 | Facility Technician |
| In Progress | 0 | Facility Technician |
| Resolved | 0 | Facility Supervisor |
| Closed | 0 | Facility Supervisor |

У всех строк:

```text
Doc Status = 0
```

Не использовать `1 = Submitted` и `2 = Cancelled`.

`Only Allow Edit For` — дополнительное ограничение текущего состояния. Оно не заменяет Role Permission Manager.

```text
Role Permission
+
Workflow State Allow Edit
=
фактический режим работы документа
```

---

# 9. Настроить Transitions

Добавить четыре перехода:

| State | Action | Next State | Allowed |
|---|---|---|---|
| New | Mark Assigned | Assigned | Facility Supervisor |
| Assigned | Start Work | In Progress | Facility Technician |
| In Progress | Resolve | Resolved | Facility Technician |
| Resolved | Close | Closed | Facility Supervisor |

Conditions пока пустые.

`Allow Self Approval` оставить со штатным значением — отдельную модель самоутверждения в базовом уроке не строим.

---

# 10. Активировать Workflow

Перед активацией проверить:

```text
Document Type = Service Request
Workflow State Field = status
```

States:

```text
New
Assigned
In Progress
Resolved
Closed
```

Transitions:

```text
New → Assigned
Assigned → In Progress
In Progress → Resolved
Resolved → Closed
```

После проверки:

```text
Is Active = Yes
```

Сохранить.

Очистить cache:

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost clear-cache
```

Обновить Desk.

---

# 11. Проверить существующие заявки

Открыть несколько Service Request из L4–L6.

Их `status` уже содержит допустимые Workflow State, поэтому отдельное поле или миграция не нужны.

Если найдена тестовая запись с другим значением, исправить именно плохие тестовые данные.

Не расширять Workflow ради ошибочной записи.

---

# 12. Создать новую заявку под Requester

Войти:

```text
requester.one@example.com
```

Создать заявку:

```text
Subject:     Workflow test request
Location:    Room 101
Description: Проверка управляемого процесса
Priority:    Medium
```

Сохранить.

Проверить:

```text
Status = New
```

Requester не должен видеть Workflow Action:

```text
Mark Assigned
```

потому что переход разрешён только `Facility Supervisor`.

---

# 13. Назначить и перевести в Assigned

Войти:

```text
supervisor.one@example.com
```

Открыть заявку.

Сначала выполнить уже знакомое:

```text
Assign To
→ technician.one@example.com
```

Проверить созданный `ToDo`.

Затем выполнить Workflow Action:

```text
Mark Assigned
```

Результат:

```text
Status = Assigned
```

То есть:

```text
Assign To
→ кто делает

Workflow
→ в каком состоянии процесс
```

---

# 14. Провести работу под Technician

Войти:

```text
technician.one@example.com
```

Открыть назначенную заявку `Room 101`.

В состоянии `Assigned` выполнить:

```text
Start Work
```

Проверить:

```text
Status = In Progress
```

Затем выполнить:

```text
Resolve
```

Проверить:

```text
Status = Resolved
```

Technician не должен видеть действие:

```text
Close
```

---

# 15. Закрыть под Supervisor

Вернуться под:

```text
supervisor.one@example.com
```

Для `Resolved` заявки выполнить:

```text
Close
```

Получить:

```text
Status = Closed
```

В нашей линейной схеме у `Closed` следующего перехода нет.

---

# 16. Проверить запрещённые переходы

Обязательно проверить минимум три случая.

## Requester

На `New` заявке нет:

```text
Mark Assigned
```

## Technician

На `Assigned` заявке есть только следующий допустимый рабочий переход:

```text
Start Work
```

Нельзя сразу перескочить в `Resolved`.

## Supervisor

На `Resolved` заявке есть:

```text
Close
```

Нет перехода напрямую назад в `New` или `Assigned`.

Итог:

```text
Current State
+
Allowed Role
+
Condition
=
доступные Workflow Actions
```

---

# 17. Проверить Status

Открыть Service Request под обычным пользователем.

`Status` должен отображать текущее состояние и не использоваться как ручной переключатель процесса.

Если поле редактируется напрямую, проверить в Standard DocType:

```text
status → Read Only = Yes
```

Client Script для блокировки не нужен.

---

# 18. Посмотреть Timeline

На заявке, прошедшей полный маршрут, проверить Timeline:

```text
New
→ Assigned
→ In Progress
→ Resolved
→ Closed
```

Сравнить в одной истории:

```text
Document change
Assignment
Comment
Workflow
```

При `apply_workflow` Frappe добавляет Workflow comment для нового состояния.

Собственный `Workflow History` DocType не нужен.

---

# 19. Посмотреть Workflow Action

Под пользователем, у которого ожидается следующий переход, открыть:

```text
Workflow Action
```

Найти действие для тестовой заявки.

Проверить:

```text
Reference Document Type = Service Request
Reference Name          = SR-.....
Status                  = Open / Completed
Permitted Roles         = роль следующего перехода
```

Frappe создаёт и закрывает эти записи штатно.

Собственная таблица ожидающих действий не нужна.

---

# 20. Короткая практика Condition

Это временный эксперимент.

У перехода:

```text
New → Mark Assigned → Assigned
```

временно задать:

```python
doc.priority == "High"
```

Проверить две `New` заявки под Supervisor:

```text
Priority = High
→ Mark Assigned доступен

Priority = Medium
→ Mark Assigned недоступен
```

После проверки удалить Condition и сохранить Workflow.

Финальный маршрут снова должен принимать любой Priority.

Здесь используется штатное выражение Workflow, а не собственный Python-модуль.

---

# 21. Разобраться с Kanban из L6

В L6 был создан Kanban:

```text
Service Requests by Status
```

После появления Workflow **не используем drag-and-drop Kanban как основной способ выполнять переходы**.

Причина в реализации v16.32.0:

```text
Kanban move
→ frappe.set_value(...)
→ frappe.client.set_value(...)
→ doc.save()
```

Поэтому workflow validation состояния, роли и Condition выполняется, но это не тот же путь, что:

```text
frappe.model.workflow.apply_workflow(...)
```

`apply_workflow` дополнительно обрабатывает Workflow Action и штатные действия перехода.

Для нашего учебного приложения один процесс должен иметь один понятный способ управления:

```text
Workflow Action
```

Поэтому Kanban `Service Requests by Status`, созданный для изучения механизма в L6, **удалить после проверки L7**.

Сам Kanban как возможность Frappe уже изучен; в итоговом приложении он не нужен ценой двусмысленного управления Workflow State.

---

# 22. Разделить metadata и configuration

После L7 появились два типа изменений.

## Metadata app

Изменён Standard DocType:

```text
Service Request.status
→ Read Only
```

Это видно в Git.

## Configuration Documents site

Созданы:

```text
Workflow State
Workflow Action Master
Workflow
```

Они живут в database текущего site.

В L7 не пытаемся вручную копировать их в source.

Их переносимость будет разобрана в L11 через штатные механизмы Frappe.

---

# 23. Commit metadata L7

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

В осознанном metadata diff должен быть переход `status` в Read Only.

Добавить:

```bash
git add \
  facility_ops/facility_operations/doctype/service_request/service_request.json

git diff --cached
```

Commit:

```bash
git commit -m "Make service request status workflow controlled"
git status
```

Ожидается:

```text
working tree clean
```

Workflow configuration в этот commit сама по себе не попадает.

---

# 24. Самостоятельная практика

С нуля провести одну новую заявку до `Closed`.

Порядок должен получиться без подсказки:

```text
Requester
→ создаёт

Supervisor
→ Assign To Technician
→ Mark Assigned

Technician
→ Start Work
→ Resolve

Supervisor
→ Close
```

Условия:

- Status вручную не редактируется;
- Assignment существует как ToDo;
- переходы выполняются правильными ролями;
- Timeline показывает процесс;
- Workflow Action можно найти;
- Status-Kanban из L6 больше не используется.

---

# 25. Приёмка L7

L7 принят, если выполнено всё ниже.

## Workflow

```text
Name:                 Service Request Workflow
Document Type:        Service Request
Workflow State Field: status
Is Active:            Yes
```

Нового `workflow_state` поля нет.

## States

```text
New
Assigned
In Progress
Resolved
Closed
```

У всех:

```text
Doc Status = 0
```

## Transitions

```text
New         --Mark Assigned / Supervisor--> Assigned
Assigned    --Start Work / Technician-----> In Progress
In Progress --Resolve / Technician--------> Resolved
Resolved    --Close / Supervisor----------> Closed
```

## Negative tests

- Requester не выполняет `Mark Assigned`;
- Technician не выполняет `Close`;
- состояния нельзя перескакивать;
- Status не используется как ручной переключатель.

## Понимание

Ученик объясняет:

```text
Permission
= можно ли работать с документом

Assign To / ToDo
= кому поручена работа

Status
= текущее состояние

Workflow
= какие переходы разрешены

Workflow Action
= конкретное доступное действие перехода
```

## Переносимость

Ученик различает:

```text
service_request.json
= metadata app

Workflow / Workflow State / Workflow Action Master
= configuration Documents site
```

## Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое.

---

# Итог L7

До урока:

```text
пользователь меняет Status
```

После урока:

```text
пользователь выбирает разрешённое Workflow Action
        ↓
Frappe проверяет State + Role + Condition
        ↓
Workflow меняет status
        ↓
процесс продолжается
```

Следующий урок — **L8. Контроль работы**: Report Builder, Number Card, Dashboard Chart и Workspace на накопленных `Service Request`.
