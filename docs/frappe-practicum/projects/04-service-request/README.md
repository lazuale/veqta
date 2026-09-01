# L4. Заявка на обслуживание

L4 добавляет третий и последний основной DocType приложения — `Service Request`.

Цель урока: собрать первый настоящий рабочий документ `facility_ops`, связать его с местом и, при необходимости, с оборудованием, но **не смешивать состояние процесса с назначением исполнителя**.

Базовая версия: **Frappe Framework v16.32.0**.

## Итоговая модель

```text
Facility Location
      │
      ├────────► Equipment
      │              │
      └──────────────┴────────► Service Request
```

`Service Request` всегда имеет `Location`.

`Equipment` необязателен:

```text
сломался кондиционер
→ Location + Equipment

протекает потолок
→ только Location
```

Поля:

| Label | Fieldname | Type | Mandatory | Default |
|---|---|---|---:|---|
| Subject | `subject` | Data | Yes | |
| Location | `location` | Link → Facility Location | Yes | |
| Equipment | `equipment` | Link → Equipment | No | |
| Description | `description` | Text | Yes | |
| Priority | `priority` | Select | Yes | Medium |
| Status | `status` | Select | Yes | New |
| Target Date | `target_date` | Date | No | |
| Attachment | `attachment` | Attach | No | |

Priority:

```text
Low
Medium
High
```

Status:

```text
New
Accepted
In Progress
Resolved
Closed
```

Критическое изменение архитектуры:

```text
Accepted
= Supervisor принял заявку в рабочий процесс

Accepted
≠ назначен конкретный Technician
```

Конкретное поручение появится в L6 через `Assign To → ToDo` и останется отдельной осью.

Naming:

```text
Naming Rule: Expression
Auto Name:   SR-.#####
```

Title Field:

```text
subject
```

Track Changes:

```text
Yes
```

---

# 1. Проверить состояние после L3

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
Git working tree clean
```

Минимально существуют:

```text
Room 101
Room 102
Floor 1
Floor 2
Warehouse
```

и несколько `Equipment` из L2/L3.

Если L3 не принят — L4 не начинаем.

---

# 2. Зафиксировать семантику Location

До создания DocType важно определить смысл двух похожих полей.

```text
Equipment.location
= текущее размещение Equipment

Service Request.location
= место события / проблемы, зафиксированное заявкой
```

Поэтому курс **не вводит** правило:

```text
Service Request.location == Equipment.location навсегда
```

Почему это было бы плохим инвариантом:

```text
сегодня Equipment находится в Room 101
→ там создаётся заявка

через месяц Equipment переместили в Warehouse
→ Equipment.location изменился
→ историческая заявка всё равно должна помнить Room 101
```

При создании заявки выбираем Equipment, который **сейчас логично относится к выбранной Location**, но это контроль качества исходных данных, а не серверная синхронизация.

Не пишем код автоподстановки и не связываем два поля жёстко.

---

# 3. Зафиксировать тип документа

`Service Request` — обычный Standard DocType.

Он не является:

```text
Tree
Child Table
Single
Submittable
```

Каждый Document — отдельная рабочая заявка.

`Draft / Submit / Cancel / Amend` изучаются отдельно в Lab B и не навязываются рабочей заявке.

---

# 4. Создать Standard DocType

Через Awesomebar открыть `DocType` и создать:

```text
Name:   Service Request
Module: Facility Operations
Custom: No
```

Не включать:

```text
Is Tree
Is Child Table
Is Single
Is Submittable
```

---

# 5. Добавить поля

## Subject

```text
Label:     Subject
Fieldname: subject
Type:      Data
Mandatory: Yes
```

## Location

```text
Label:     Location
Fieldname: location
Type:      Link
Options:   Facility Location
Mandatory: Yes
```

## Equipment

```text
Label:     Equipment
Fieldname: equipment
Type:      Link
Options:   Equipment
Mandatory: No
```

Добавить `Section Break`:

```text
Details
```

## Description

```text
Label:     Description
Fieldname: description
Type:      Text
Mandatory: Yes
```

Добавить `Section Break`:

```text
Processing
```

## Priority

```text
Label:     Priority
Fieldname: priority
Type:      Select
Mandatory: Yes
Default:   Medium
Options:
Low
Medium
High
```

## Status

```text
Label:     Status
Fieldname: status
Type:      Select
Mandatory: Yes
Default:   New
Options:
New
Accepted
In Progress
Resolved
Closed
```

Добавить `Column Break`.

## Target Date

```text
Label:     Target Date
Fieldname: target_date
Type:      Date
Mandatory: No
```

## Attachment

```text
Label:     Attachment
Fieldname: attachment
Type:      Attach
Mandatory: No
```

Не добавлять:

```text
Assigned Technician
Requester business entity
Department
Status reference
Priority reference
даты каждого перехода
свой журнал комментариев
```

---

# 6. Почему статус называется Accepted, а не Assigned

`Assigned` создаёт опасное ложное ожидание:

```text
Status = Assigned
→ обязательно существует конкретный assignee
```

Штатный Frappe этого не гарантирует.

`Assign To` хранит поручение через `ToDo`, а Workflow/Status — состояние процесса.

Поэтому используем:

```text
New
→ заявка поступила

Accepted
→ Supervisor принял её в рабочую очередь

In Progress
→ работа выполняется

Resolved
→ Technician считает проблему решённой

Closed
→ Supervisor завершил процесс
```

Так модель остаётся корректной даже если Assignment меняется, закрывается или отсутствует.

---

# 7. Настроить Naming

```text
Naming Rule: Expression
Auto Name:   SR-.#####
```

Например:

```text
SR-00001
SR-00002
```

`Subject` — бизнес-заголовок, `name` — системный идентификатор.

---

# 8. Title Field и Search Fields

```text
Title Field: subject
Search Fields: location,equipment,priority,status
```

---

# 9. Track Changes

Включить:

```text
Track Changes = Yes
```

Рабочий Document будет меняться по ходу процесса. Для аудита используем штатный `Version/Timeline`, а не свой History DocType.

---

# 10. Проверить metadata

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

sed -n '1,380p' \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

Найти:

```text
"autoname": "SR-.#####"
"title_field": "subject"
"track_changes": 1
```

и поля:

```text
subject
location
equipment
description
priority
status
target_date
attachment
```

JSON вручную не редактировать.

---

# 11. Создать заявку с Equipment

```text
Subject:     Не охлаждает кондиционер
Location:    Room 101
Equipment:   EQ-0001
Description: Кондиционер включается, но температура в помещении не снижается.
Priority:    High
Status:      New
Target Date: ближайшая будущая дата
```

Перед сохранением убедиться, что выбранное `EQ-0001` действительно сейчас относится к `Room 101` в учебных данных.

Сохранить и проверить имя `SR-.....`.

---

# 12. Создать заявку без Equipment

```text
Subject:     Не работает освещение
Location:    Floor 1
Equipment:   пусто
Description: В коридоре первого этажа не работает часть светильников.
Priority:    Medium
Status:      New
```

Заявка должна сохраниться.

Не создавать фиктивный Equipment `General` ради заполнения Link.

---

# 13. Проверить Mandatory

Отдельно получить отказ без каждого из ключевых обязательных значений:

```text
Subject
Location
Description
Priority
```

Минимум обязательно проверить отсутствие `Location` и `Description`.

Итог:

```text
Web Form/Automation следующих уроков
не имеют права ослаблять эту модель
```

---

# 14. Проверить Link

Попробовать указать:

```text
Equipment = EQ-NOT-EXISTS
```

Обычный Link должен ссылаться на существующий `Equipment` Document.

---

# 15. Создать рабочий набор заявок

Создать минимум 8 записей.

Пример:

| Subject | Location | Equipment | Priority | Status |
|---|---|---|---|---|
| Не охлаждает кондиционер | Room 101 | EQ-0001 | High | New |
| Не работает освещение | Floor 1 | — | Medium | New |
| Нет сети у коммутатора | Room 101 | EQ-0004 | High | In Progress |
| Проверить ИБП | Warehouse | EQ-0006 | Low | Accepted |
| Шум от кондиционера | Room 102 | EQ-0002 | Medium | New |
| Повреждена розетка | Room 102 | — | High | Resolved |
| Убрать старое оборудование | Floor 2 | EQ-0008 | Low | Closed |
| Слабый сигнал Wi-Fi | Room 102 | EQ-0005 | Medium | In Progress |

В L4 статусы пока вводятся вручную специально для подготовки данных.

---

# 16. Проверить обычный Select до Workflow

Открыть заявку `New` и вручную изменить:

```text
New → Closed
```

Сохранить.

Frappe должен позволить это, потому что пока:

```text
Select
= набор допустимых значений

Select
≠ state machine
```

Вернуть заявке логичное состояние.

---

# 17. Проверить Track Changes

Изменить у тестовой заявки `Priority` или `Description` и посмотреть Timeline/Version.

Зафиксировать:

```text
Track Changes
= аудит изменений

но

Track Changes
≠ запрет изменений
```

---

# 18. List View и Filters

Проверить фильтры минимум по:

```text
Status
Priority
Location
Equipment
```

Сохранить один полезный фильтр, например:

```text
Status != Closed
Priority = High
```

---

# 19. Что изменилось в архитектуре

После L4 существуют три разные сущности/оси:

```text
Location / Equipment
= предметные данные

Service Request.status
= состояние рабочего процесса

Assignment
= ещё отсутствует и появится отдельно в L6
```

Это разделение нельзя ломать в следующих уроках.

---

# 20. Commit L4

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff

git add facility_ops/facility_operations/doctype/service_request

git diff --cached
git commit -m "Add service request doctype"
git status
```

Рабочие `SR-...` Documents в Git не попадают.

---

# 21. Приёмка L4

L4 принят, если:

- создан Standard `Service Request`;
- `Subject`, `Location`, `Description`, `Priority` Mandatory;
- `Equipment` Optional;
- `Priority` имеет `Low / Medium / High`, default `Medium`;
- `Status` имеет `New / Accepted / In Progress / Resolved / Closed`;
- ученик объясняет, почему `Accepted ≠ Assigned To`;
- ученик объясняет разницу `Service Request.location` и `Equipment.location`;
- не заявляется ложный hard invariant равенства этих Location;
- naming `SR-.#####` работает;
- Track Changes работает;
- создан рабочий набор заявок;
- доказано, что обычный Select до L7 не ограничивает переходы;
- metadata находится в app source, рабочие Documents — только на site;
- Git чист после commit.

После L4 переходим к **L5 — пользователи и права**.