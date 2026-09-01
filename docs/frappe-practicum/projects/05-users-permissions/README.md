# L5. Пользователи и права

L5 делает `facility_ops` многопользовательским и задаёт **финальную базовую security model** для следующих уроков.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Цель hardening

После L5 нужно разделить:

```text
право создать заявку
право читать заявку
право сохранять Document
право менять содержательные поля
право удалить Document
```

Финальная модель:

```text
Requester
→ создаёт заявку
→ читает свою
→ после insert не сохраняет её повторно

Technician
→ читает заявки
→ имеет document Write для Workflow
→ не переписывает исходные реквизиты заявки

Supervisor
→ управляет содержанием и процессом
→ не удаляет нормальные Service Request
```

---

# 2. Создать роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

---

# 3. Создать постоянных Users

```text
requester.one@example.com     → Facility Requester
requester.two@example.com     → Facility Requester
technician.one@example.com    → Facility Technician
supervisor.one@example.com    → Facility Supervisor
```

Все — `System User`, Enabled, без Welcome Email.

Не выдавать `System Manager`.

`technician.two@example.com` появится только в L9.

---

# 4. Facility Location permissions

| Role | Read | Write | Create | Delete |
|---|---:|---:|---:|---:|
| Requester | Yes | No | No | No |
| Technician | Yes | No | No | No |
| Supervisor | Yes | Yes | Yes | No |

---

# 5. Equipment permissions

| Role | Read | Write | Create | Delete | Import | Export |
|---|---:|---:|---:|---:|---:|---:|
| Requester | Yes | No | No | No | No | No |
| Technician | Yes | No | No | No | No | No |
| Supervisor | Yes | Yes | Yes | No | Yes | Yes |

Для:

```text
Equipment.notes
```

установить:

```text
Permission Level = 1
```

Level 1:

```text
Supervisor → Read Yes / Write Yes
Requester  → No
Technician → No
```

Это первый простой пример field-level permission.

---

# 6. Service Request: document-level permissions

На Permission Level 0 настроить:

| Role | Read | Write | Create | Delete | Report | Export | If Owner |
|---|---:|---:|---:|---:|---:|---:|---:|
| Requester | Yes | **No** | Yes | No | No | No | Yes |
| Technician | Yes | Yes | No | No | No | No | No |
| Supervisor | Yes | Yes | Yes | **No** | Yes | Yes | No |

Ключевой результат:

```text
Requester
Create = Yes
Read own = Yes
Write = No
```

Exact permission engine `v16.32.0` не сворачивает `create` в If Owner restriction, поэтому новый Document создать можно, а сохранённый повторно редактировать нельзя.

---

# 7. Service Request: защитить содержательные поля Level 1

Перевести следующие поля Standard DocType на:

```text
Permission Level = 1
```

Поля:

```text
subject
location
equipment
description
priority
target_date
attachment
```

Оставить на Level 0:

```text
status
```

и системные поля Frappe.

Почему:

```text
status
→ должен участвовать в Workflow

business content
→ не должен свободно переписываться Technician
```

---

# 8. Service Request Level 1 role matrix

В Role Permission Manager добавить Level 1 rows:

| Role | Level | Read | Write |
|---|---:|---:|---:|
| Facility Requester | 1 | Yes | **Yes** |
| Facility Technician | 1 | Yes | **No** |
| Facility Supervisor | 1 | Yes | Yes |

На Level 1 не настраивать document operations вроде Create/Delete — это level-0 responsibility.

## Почему Requester получает Level 1 Write

Это не возвращает ему post-create document Write.

При insert:

```text
Level 0 Create = Yes
+
Level 1 Write = Yes
→ Requester может заполнить high-permlevel fields нового Document
```

После insert:

```text
Level 0 Write = No
→ обычный повторный save запрещён целиком
```

То есть Level 1 Write у Requester нужен **для intake**, а не для дальнейшего редактирования.

---

# 9. Почему Level 1 — реальная server защита

В exact `v16.32.0` `Document.insert()` и `Document.save()` вызывают:

```text
validate_higher_perm_levels()
```

до записи в БД.

Если пользователь не имеет `write` на высокий Permission Level, Frappe сбрасывает такие поля к исходным/default values перед сохранением.

Следовательно для Technician:

```text
Document Write = Yes
Level 1 Read = Yes
Level 1 Write = No
```

означает:

```text
может сохранять разрешённые Level 0 изменения / Workflow
не может через обычный permission-aware save переписать Level 1 content
```

Это сильнее, чем просто сделать поля Read Only в форме.

Не распространять гарантию на explicit `ignore_permissions=True` paths — поэтому L10 Web Form update финально выключен.

---

# 10. Проверить Requester One create

Под:

```text
requester.one@example.com
```

создать через Desk:

```text
Subject:     Requester One test
Location:    Room 101
Equipment:   EQ-0001 или пусто
Description: Проверка append-only intake
Priority:    Medium
```

Save должен пройти.

Проверить owner и Status New.

---

# 11. Проверить Requester post-create no-Write

На только что сохранённой заявке попробовать изменить:

```text
Description
Priority
```

Ожидается отсутствие обычного Write.

Requester может читать свою заявку, но не переписывать её после insert.

---

# 12. Проверить If Owner вторым Requester

Под `requester.two@example.com` создать свою заявку.

Проверить:

```text
Requester Two → читает свою
Requester Two → не читает обычным путём заявку Requester One
```

и наоборот.

---

# 13. Проверить Technician field protection

Под:

```text
technician.one@example.com
```

открыть Service Request.

Technician должен видеть Level 1 content:

```text
Subject
Location
Equipment
Description
Priority
Target Date
Attachment
```

но не иметь штатного field Write для них.

Проверить минимум:

```text
Description → read-only
Priority    → read-only
Target Date → read-only
```

При этом document-level `Write = Yes` сохраняется — он понадобится Workflow L7.

Главный вывод:

```text
Document Write
не означает write каждого Permission Level
```

---

# 14. Проверить Supervisor

Под Supervisor:

- читать все Service Request;
- создавать новую заявку;
- изменять Level 1 content;
- Report/Export доступны;
- обычный Delete в финале недоступен.

---

# 15. Временно изучить Delete

Чтобы механизм `Delete` реально был пройден, временно включить Supervisor:

```text
Service Request
Permission Level 0
Delete = Yes
```

Создать отдельную заявку:

```text
Subject:     Delete permission experiment
Location:    Warehouse
Description: Temporary L5 delete test
Priority:    Low
```

Удалить **только её** под Supervisor.

Сразу после теста вернуть:

```text
Delete = No
```

и перепроверить Role Permission Manager.

Финальная operating policy не разрешает рабочим ролям удалять Service Request.

---

# 16. Временный Restricted Technician

Создать:

```text
technician.restricted@example.com
→ System User
→ Facility Technician
```

Он нужен только для User Permission / Share experiment.

---

# 17. User Permission experiment

Создать:

```text
User:           technician.restricted@example.com
Allow:          Facility Location
For Value:      Room 101
Applicable For: Service Request
```

Проверить:

```text
Room 101 → ordinary access
Room 102 / Warehouse → ordinary access отсутствует
```

---

# 18. Share experiment

Одну Room 102 заявку Share:

```text
User:  technician.restricted@example.com
Read:  Yes
Write: No
```

Проверить точечный read exception.

---

# 19. Почему experiment обязательно очистить

Штатный `Assign To` при insufficient access assignee может автоматически создать `DocShare`; при disabled sharing — получить Missing Permission.

Если оставить Location User Permission на основных Technician, Assignment начнёт неожиданно менять access model.

Поэтому до выхода из L5:

```text
Share удалить
User Permission удалить
technician.restricted отключить
Supervisor Delete = No
```

Основной `technician.one` остаётся без Location User Permission.

---

# 20. Проверить Standard metadata diff

В L5 меняется Standard metadata:

```text
Equipment.notes → permlevel 1

Service Request:
subject      → permlevel 1
location     → permlevel 1
equipment    → permlevel 1
description  → permlevel 1
priority     → permlevel 1
target_date  → permlevel 1
attachment   → permlevel 1
status       → permlevel 0
```

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/equipment/equipment.json \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

Role Permission rows пока site configuration; L11 экспортирует `Custom DocPerm`.

---

# 21. Отрицательные проверки

Получить реальные ограничения:

```text
Requester → Create Equipment запрещён
Requester → чужая Service Request запрещена
Requester → own saved Service Request Write запрещён
Technician → Create Service Request запрещён
Technician → Level 1 content Write отсутствует
Supervisor → Service Request Delete после rollback запрещён
Restricted Technician → non-permitted Location закрыта до cleanup
```

Administrator не использовать как доказательство.

---

# 22. Commit metadata

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff

git add \
  facility_ops/facility_operations/doctype/equipment/equipment.json \
  facility_ops/facility_operations/doctype/service_request/service_request.json

git diff --cached
git commit -m "Harden facility operations field permissions"
git status
```

Не добавлять в Git Users/Share/User Permission/Custom DocPerm вручную.

---

# 23. State contract L5

## Persistent

```text
3 roles
4 main System Users
Equipment.notes permlevel 1
Service Request business content permlevel 1
final Role Permission matrix
```

## Temporary

```text
Supervisor Delete Yes
technician.restricted
Location User Permission
one Share
```

## Rollback

```text
Supervisor Delete No
Share removed
User Permission removed
restricted user disabled
```

## Output

```text
Requester = create/read-own/no-write
Technician = document write + content read-only
Supervisor = content write + no delete
```

---

# 24. Приёмка L5

L5 принят, если:

- существуют три роли и четыре main users;
- Requester через Desk создаёт валидный Service Request;
- после Save Requester читает свой Document, но не имеет Write;
- второй Requester доказывает If Owner isolation;
- Service Request content fields находятся на Permission Level 1;
- Requester Level 1 Read/Write позволяет заполнить новый Document, но level-0 Write остаётся No;
- Technician Level 1 Read Yes / Write No;
- Technician видит content, но не редактирует его штатным permission-aware path;
- Technician сохраняет document-level Write для будущего Workflow;
- Supervisor Level 1 Read/Write;
- Delete реально изучен и возвращён в No;
- User Permission и Share проверены временно и очищены;
- main Technician не ограничен Location User Permission;
- metadata закоммичена;
- Git clean.

После L5 переходим к **L6 — совместная работа**.
