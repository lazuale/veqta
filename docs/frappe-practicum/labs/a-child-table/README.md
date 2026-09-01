# Lab A. Child Table

Lab A изучает вложенные строки документа и после rollback возвращает приложение к трём core DocType.

Временный эксперимент:

```text
Service Request
    │
    └── Work Logs
          ├── Description
          ├── Hours
          └── Cost
```

Базовая версия: **Frappe Framework v16.32.0**.

Собственный Python/JavaScript не пишем.

---

# 1. Что изучаем

```text
Child DocType
Table field
Editable Grid
parent
parenttype
parentfield
idx
parent permission context
Permission Level на Table field
metadata vs working data
rollback
```

Критическое правило лаборатории:

```text
новый Table field
не должен случайно пробить
финальную Level 1 protection Service Request
```

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

cd apps/facility_ops
git status
```

Ожидается:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

Core domain:

```text
Facility Location
Equipment
Service Request
```

Service Request baseline:

```text
Level 0
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No

Level 1 content
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

---

# 3. Child Table vs самостоятельный Document

Обычный DocType:

```text
Equipment
Service Request
```

представляет самостоятельные Documents.

Child DocType представляет строки внутри parent Document.

Пример:

```text
Service Request SR-00042

Work Logs
1. Inspect equipment    0.50 h
2. Replace bearing     2.00 h
3. Test after repair   0.50 h
```

`Replace bearing` не должен жить как отдельный business Document.

---

# 4. Создать временный Child DocType

Под Administrator:

```text
Name:           Work Log
Module:         Facility Operations
Is Child Table: Yes
```

Если `Editable Grid` доступен — оставить включённым.

Не включать:

```text
Is Single
Is Tree
Is Submittable
Allow Import
```

Для Child DocType отдельную обычную permission matrix не создаём.

---

# 5. Поля Work Log

| Label | Fieldname | Type | Mandatory | In List View |
|---|---|---|---:|---:|
| Description | `description` | Data | Yes | Yes |
| Hours | `hours` | Float | Yes | Yes |
| Cost | `cost` | Currency | No | Yes |

Для Hours можно задать Precision 2.

---

# 6. Системная модель Child DocType

Для `istable = 1` Frappe не проектирует Child DocType как самостоятельный реестр с отдельной пользовательской permission matrix.

Child rows связаны с parent через:

```text
parent
parenttype
parentfield
idx
```

Эти поля не добавляем вручную.

---

# 7. Добавить Table field в Service Request

Открыть Standard DocType `Service Request`.

Добавить Section Break:

```text
Work
```

Добавить:

```text
Label:            Work Logs
Fieldname:        work_logs
Field Type:       Table
Options:          Work Log
Permission Level: 1
```

**Permission Level 1 обязателен.**

Почему:

```text
Service Request business content
→ уже защищён Level 1

Work Logs
→ тоже business content parent Document
→ не должен оказаться на Level 0
```

Если оставить `work_logs` на Level 0, Technician с document-level Write сможет получить дополнительную writable область, которой не было в базовой архитектуре.

---

# 8. Permission semantics Child Table

Child row не получает самостоятельную permission architecture.

В parent context важен в том числе Permission Level Table field:

```text
Service Request.work_logs → permlevel 1
```

Поэтому в нашей лаборатории:

```text
Supervisor
→ Level 1 Write
→ редактирует Work Logs

Technician
→ Level 1 Read only
→ видит Work Logs
→ не должен редактировать их штатным permission-aware path
```

Это сохраняет hardened baseline L5/L11.

---

# 9. Создать лабораторную Service Request

Под Supervisor создать отдельную заявку:

```text
Subject:     Child table lab
Location:    Room 101
Description: Temporary document for Lab A
Priority:    Medium
Target Date: любая будущая дата
```

Не использовать рабочую заявку, которую жалко испортить.

---

# 10. Добавить строки под Supervisor

В `Work Logs` добавить:

```text
Description: Inspect equipment
Hours:       0.50
Cost:        0
```

```text
Description: Replace bearing
Hours:       2.00
Cost:        120
```

```text
Description: Test after repair
Hours:       0.50
Cost:        0
```

Сохранить parent `Service Request`.

Главный факт:

```text
3 child rows
1 parent Service Request
```

Save выполняется у parent Document.

---

# 11. Editable Grid

Под Supervisor изменить inline:

```text
Replace bearing
Hours: 2.00 → 2.50
```

Затем через row editor:

```text
Cost: 120 → 135
```

Сохранить parent.

Оба способа изменяют ту же child row.

---

# 12. Проверить Technician read-only boundary

Войти:

```text
technician.one@example.com
```

Открыть лабораторную Service Request.

Technician должен видеть Work Logs, но не иметь штатного write на Table field Level 1.

Проверить, что нельзя обычным UI изменить:

```text
Hours
Cost
Description row
```

или добавить/удалить строку.

Фиксируем:

```text
parent document Write
≠ write child table любого Permission Level
```

Не использовать `ignore_permissions`, raw SQL или собственный script для обхода этого теста.

---

# 13. Порядок строк и idx

Под Supervisor переставить строки, если Grid позволяет штатный reorder.

Например:

```text
1. Inspect equipment
2. Test after repair
3. Replace bearing
```

Сохранить и обновить страницу.

Позиция child row хранится через:

```text
idx
```

Если drag/reorder в конкретном UI недоступен — не писать обходной код.

---

# 14. Удалить строку

Под Supervisor удалить:

```text
Test after repair
```

Сохранить parent.

```text
удалить child row
≠ удалить Service Request
```

---

# 15. Mandatory child fields

Добавить пустую строку и получить validation error при отсутствии:

```text
Description
```

или:

```text
Hours
```

После теста заполнить строку либо удалить её.

Mandatory не отключать.

---

# 16. Техническая связь строк

Смысл системных полей:

```text
parent      = SR-00042
parenttype  = Service Request
parentfield = work_logs
idx         = номер строки
```

Frappe управляет ими автоматически.

---

# 17. Table vs Link

```text
Link
→ ссылка на другой самостоятельный Document

Table
→ дочерние строки текущего Document
```

`Facility Location` может использоваться множеством Documents.

`Work Log` row принадлежит своему parent Service Request.

---

# 18. Metadata в Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
find facility_ops/facility_operations -type f | sort | grep -E 'work_log|service_request'
```

В diff `Service Request` проверить:

```text
fieldtype = Table
fieldname = work_logs
options   = Work Log
permlevel = 1
```

В `Work Log`:

```text
istable = 1
```

Конкретные строки Work Log в Git не попадают.

---

# 19. Optional experiment commit

```bash
git add .
git diff --cached
git commit -m "Add temporary work log child table lab"
git status
```

Commit сохраняет историю эксперимента, но не превращает Work Log в core entity.

---

# 20. Почему Work Log не остаётся

```text
механизм изучен
≠
сущность доказала необходимость в постоянной модели
```

В базовом `facility_ops` Work Log не нужен для core scenario.

---

# 21. Rollback working data без ослабления Delete policy

Под Supervisor удалить все `Work Logs` из лабораторной заявки и сохранить parent Document.

Саму лабораторную `Service Request` **не удалять под Supervisor**: финальная permission policy специально имеет:

```text
Supervisor Delete = No
```

Если тестовый Document нужно убрать полностью, есть два корректных варианта:

```text
1. оставить/закрыть его как учебный runtime Document;

2. удалить под Administrator как административный cleanup,
   не меняя Role Permission Manager.
```

Запрещено ради cleanup временно включать Supervisor `Delete = Yes`: этот механизм уже изучен и откатан в L5.

---

# 22. Rollback metadata parent

Под Administrator удалить из `Service Request`:

```text
Work Logs / work_logs
```

и пустой Section Break `Work`, если он больше не нужен.

Не удалять JSON вручную.

---

# 23. Rollback Child DocType

Штатно удалить:

```text
Work Log
```

Если Frappe сообщает о ссылке — сначала проверить, что parent Table field действительно удалён.

---

# 24. Проверить возврат permission model

После cleanup `Service Request` снова должен содержать только исходные business fields Level 1:

```text
subject
location
equipment
description
priority
target_date
attachment
```

`work_logs` отсутствует.

Проверить Role Permission Manager:

```text
Requester Level 0 Write = No
Technician Level 1 Write = No
Supervisor Delete = No
```

Лаборатория не должна менять Custom DocPerm.

---

# 25. Git после rollback

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

Если делался experiment commit:

```bash
git add -A
git diff --cached
git commit -m "Remove temporary work log child table lab"
git status
```

Финально working tree clean.

---

# 26. Самостоятельная практика

Временно создать:

```text
Checklist Item
```

Поля:

```text
Item      Data
Completed Check
```

Добавить его как Table в Service Request **на Permission Level 1**, создать 3 строки под Supervisor, проверить read-only под Technician и полностью удалить эксперимент.

---

# 27. State contract

## Temporary mutation

```text
Work Log Child DocType
Service Request.work_logs Table permlevel 1
lab Service Request + rows
```

## Persistent mutation

```text
none in metadata/security
```

Лабораторную Service Request можно оставить как runtime data либо удалить Administrator без изменения ролей.

## Rollback

```text
rows removed
work_logs removed
Work Log removed
Supervisor Delete remains No
```

## Final state

```text
3 core DocType
original Service Request Level 0/1 model
Git clean
```

---

# 28. Приёмка Lab A

Лаборатория принята, если ученик показывает:

- Child DocType и Table field;
- `parent / parenttype / parentfield / idx`;
- Editable Grid и row editor;
- Mandatory внутри child row;
- `work_logs` находится на Permission Level 1;
- Supervisor редактирует строки;
- Technician видит, но не редактирует Table через штатный permission-aware path;
- конкретные rows остаются site data;
- после rollback нет Work Log/work_logs;
- Supervisor Delete ради cleanup не включался;
- финальная Service Request permission model не ослаблена;
- Git clean.

Главный вывод:

```text
Child Table
= вложенные данные parent Document

и

permission parent field
остаётся частью архитектуры доступа
```
