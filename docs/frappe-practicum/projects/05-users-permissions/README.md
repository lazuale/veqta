# L5. Пользователи и права

L5 вводит **базовую server-side permission model** `facility_ops`.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

Финальная политика после L5:

```text
Requester
→ Create Service Request
→ Read только свои
→ после создания не Write
→ не Delete

Technician
→ Read/Write Service Request
→ не Create
→ не Delete

Supervisor
→ Read/Write/Create Service Request
→ не Delete в финальной политике
→ Report/Export
```

Причина жёсткости:

```text
заявитель отправил заявку
→ дальше это рабочая запись системы
→ он не должен тихо переписывать её после создания

рабочие Service Request
→ не удаляем как штатную операцию
→ сохраняем audit trail
```

Assignment появится в L6 и **не является permission mechanism**.

---

# 1. Preconditions

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

Существуют три core DocType и валидные Documents L4.

---

# 2. Создать роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Role — набор полномочий. User и Role не являются одной сущностью.

---

# 3. Создать постоянных System User

```text
requester.one@example.com
→ Facility Requester

requester.two@example.com
→ Facility Requester

technician.one@example.com
→ Facility Technician

supervisor.one@example.com
→ Facility Supervisor
```

Для каждого:

```text
User Type = System User
Enabled = Yes
Send Welcome Email = No
```

Не выдавать:

```text
Administrator
System Manager
```

`technician.two@example.com` появится только в L9.

---

# 4. Финальная permission matrix

## Facility Location

| Role | Read | Write | Create | Delete |
|---|---:|---:|---:|---:|
| Facility Requester | Yes | No | No | No |
| Facility Technician | Yes | No | No | No |
| Facility Supervisor | Yes | Yes | Yes | No |

## Equipment

| Role | Read | Write | Create | Delete | Import | Export |
|---|---:|---:|---:|---:|---:|---:|
| Facility Requester | Yes | No | No | No | No | No |
| Facility Technician | Yes | No | No | No | No | No |
| Facility Supervisor | Yes | Yes | Yes | No | Yes | Yes |

## Service Request

| Role | Read | Write | Create | Delete | Report | Export | If Owner |
|---|---:|---:|---:|---:|---:|---:|---:|
| Facility Requester | Yes | **No** | Yes | No | No | No | Yes |
| Facility Technician | Yes | Yes | No | No | No | No | No |
| Facility Supervisor | Yes | Yes | Yes | **No** | Yes | Yes | No |

Ключевой exact-source факт `v16.32.0`:

```text
If Owner
не превращает Create в owner-only запрет
```

Permission engine отдельно исключает `create` из owner-only свёртки.

Поэтому Requester может:

```text
создать новый Service Request
```

но после insert:

```text
Read own = Yes
Write = No
```

Это и есть безопасная модель intake.

---

# 5. Настроить Role Permission Manager

Для Requester `Service Request`:

```text
Read = Yes
Write = No
Create = Yes
Delete = No
Only If Creator = Yes
```

Для Technician:

```text
Read = Yes
Write = Yes
Create = No
Delete = No
```

Для Supervisor:

```text
Read = Yes
Write = Yes
Create = Yes
Delete = No
Report = Yes
Export = Yes
```

Остальные core DocType настроить по матрицам выше.

---

# 6. Проверить Requester One: create + read own

Войти:

```text
requester.one@example.com
```

Создать:

```text
Subject:     Requester One test
Location:    Room 101
Equipment:   EQ-0001 или пусто
Description: Проверка безопасного intake и If Owner
Priority:    Medium
```

Status получает default:

```text
New
```

После сохранения Requester One должен:

```text
видеть собственную заявку
не иметь штатного Write после создания
```

Попытка изменить `Description` и сохранить должна быть запрещена permission model.

Это важнее, чем надеяться на будущий Workflow UI.

---

# 7. Requester Two и If Owner

Под:

```text
requester.two@example.com
```

создать:

```text
Subject:     Requester Two test
Location:    Room 102
Description: Проверка owner visibility
Priority:    Low
```

Проверить:

```text
Requester Two
→ видит свой Document
→ не видит обычным способом Requester One Document

Requester One
→ не видит обычным способом Requester Two Document
```

`If Owner` здесь используется как **read boundary**, а не как разрешение переписывать собственную заявку после отправки.

---

# 8. Проверить Technician

Войти:

```text
technician.one@example.com
```

Проверить:

```text
Facility Location → Read
Equipment → Read
Service Request → Read + Write
Service Request Create/Delete → запрещены
```

Изменить `Description` отдельной тестовой Service Request и сохранить.

Это показывает базовый document Write Technician до появления Workflow.

После L7 Workflow добавит state-dependent Desk behavior и transition gates, но Role Permission останется server access boundary.

---

# 9. Проверить Supervisor без Delete

Под:

```text
supervisor.one@example.com
```

проверить:

```text
Service Request Read/Write/Create = Yes
Service Request Delete = No
Equipment Import/Export = Yes
Facility Location / Equipment management = по матрице
```

Рабочие заявки не должны исчезать обычным Delete из финальной operating policy.

Ошибочную/неактуальную заявку можно довести до terminal process state и оставить историю, а не стирать её.

---

# 10. Временно изучить Delete permission

Чтобы механизм Delete не остался только теорией, временно у Supervisor для `Service Request` включить:

```text
Delete = Yes
```

Создать только лабораторную заявку:

```text
Subject:     Delete permission experiment
Location:    Warehouse
Description: Temporary record created only to test Delete permission
Priority:    Low
```

Удалить её под Supervisor.

Сразу после проверки вернуть:

```text
Delete = No
```

Это **обязательный rollback**, а не рекомендация.

Фиксируем:

```text
Delete capability изучена
≠ Delete оставлен нормальной рабочей политикой
```

---

# 11. Permission Level

Под Administrator у:

```text
Equipment.notes
```

установить:

```text
Permission Level = 1
```

Для Supervisor добавить Level 1:

```text
Read = Yes
Write = Yes
```

Requester/Technician Level 1 не получают.

Проверить под реальными пользователями.

Фиксируем:

```text
Permission Level
= field-level permission layer
```

Он не заменяет Level 0 document permissions.

---

# 12. Metadata в Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/equipment/equipment.json
```

`Equipment.notes.permlevel = 1` — Standard metadata.

Role Permission configuration пока site-specific; L11 экспортирует Custom DocPerm через Export Customizations.

---

# 13. Создать временного Restricted Technician

```text
technician.restricted@example.com
First Name: Restricted Technician
User Type: System User
Enabled: Yes
Role: Facility Technician
Send Welcome Email: No
```

Он существует только внутри permission experiment.

---

# 14. User Permission experiment

Создать:

```text
User:           technician.restricted@example.com
Allow:          Facility Location
For Value:      Room 101
Applicable For: Service Request
```

Проверить:

```text
Room 101 → обычный доступ
Room 102 / Warehouse / Floor 2 → обычного доступа нет
```

Модель:

```text
Role Permission
→ базовый доступ к DocType

User Permission
→ дополнительное сужение допустимых Documents/Link values
```

---

# 15. Share experiment

Одну `Room 102` заявку поделить:

```text
User:  technician.restricted@example.com
Read:  Yes
Write: No
```

Проверить:

```text
обычные Room 102 → недоступны
конкретная shared Room 102 → доступна Read
```

```text
User Permission
≠ Share
```

---

# 16. Почему experiment обязательно очищается

В `v16.32.0` штатный `Assign To` после создания ToDo проверяет access assignee.

Если access нет:

```text
sharing разрешён
→ Frappe может автоматически создать DocShare Read

sharing запрещён
→ assignment может завершиться Missing Permission
```

Поэтому опасная комбинация:

```text
глобальный Round Robin
+
основные Technician с разными Location User Permission
```

может заставить Assignment менять permission model или падать.

Финальный принцип:

```text
permission architecture задаётся заранее
Assignment не раздаёт скрытые access exceptions
```

---

# 17. Обязательный rollback permission experiment

Под Administrator:

1. удалить explicit Share;
2. удалить User Permission Restricted Technician;
3. установить:

```text
technician.restricted@example.com
Enabled = No
```

Проверить под `technician.one@example.com` обычный Role-based доступ независимо от Location.

---

# 18. Финальный повторный permission check

Проверить именно **после всех временных экспериментов**:

```text
Requester:
Create own request = Yes
Read own = Yes
Write after creation = No
Delete = No

Technician:
Read/Write = Yes
Create/Delete = No

Supervisor:
Read/Write/Create = Yes
Delete = No
Report/Export = Yes
```

Если Supervisor Delete всё ещё Yes — L5 не принят.

---

# 19. Отрицательные проверки

Получить реальные отказы:

```text
Requester → edit saved own Service Request запрещён
Requester → чужая Service Request запрещена
Requester → Create Equipment запрещён
Technician → Create Service Request запрещён
Supervisor → Delete обычной Service Request запрещён после rollback
Restricted Technician до cleanup → обычная Room 102 запрещена
```

Administrator не используется как доказательство.

---

# 20. Commit metadata

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff

git add \
  facility_ops/facility_operations/doctype/equipment/equipment.json

git diff --cached
git commit -m "Restrict equipment notes by permission level"
git status
```

Не добавлять вручную:

```text
User
Role
User Permission
DocShare
Custom DocPerm
```

---

# 21. State contract L5

## Persistent

```text
3 Roles
4 main System Users
final Role Permission matrix
Equipment.notes permlevel 1
```

## Temporary

```text
Supervisor Service Request Delete = Yes
Restricted Technician enabled
User Permission Room 101
one explicit Share
```

## Rollback

```text
Supervisor Delete = No
Share deleted
User Permission deleted
Restricted Technician disabled
```

## Output

```text
Requester = create + read-own, no post-create write
main Technician = no Location User Permission
technician.two = does not exist yet
no core Service Request Delete permission
```

## Git

```text
Equipment metadata committed
working tree clean
```

---

# 22. Приёмка L5

L5 принят, если:

- Requester создаёт заявку, читает свою, но не может переписать её после сохранения;
- If Owner ограничивает visibility собственными Documents;
- Technician имеет общий Read/Write, но не Create/Delete;
- Supervisor не имеет финального Delete Service Request;
- Delete permission реально проверен временно и откатан;
- `Equipment.notes` Level 1 доступен Supervisor;
- User Permission и Share реально проверены;
- permission experiment полностью очищен;
- `technician.two@example.com` ещё не существует;
- ученик объясняет automatic Share boundary Assign To;
- Git clean.

После L5 переходим к **L6 — совместная работа**.
