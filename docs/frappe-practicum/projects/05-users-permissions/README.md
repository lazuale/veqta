# L5. Пользователи и права

L5 делает `facility_ops` многопользовательским и вводит **базовую server-side permission model** приложения.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

Главный результат урока:

```text
Role Permission
= базовая граница доступа

If Owner
= ограничение permission владельцем Document

Permission Level
= field-level access

User Permission
= дополнительное ограничение набора Documents/Link values

Share
= точечное исключение для конкретного Document
```

Assignment появится в L6 и **не будет считаться permission mechanism**.

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

Существуют:

```text
Facility Location
Equipment
Service Request
```

и валидные Documents L4.

---

# 2. Создать роли

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Роль — набор полномочий. User может иметь одну или несколько ролей.

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

`technician.two@example.com` здесь не создаём. Он появится только в L9 для Round Robin.

---

# 4. Базовая permission matrix

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
| Facility Requester | Yes | Yes | Yes | No | No | No | Yes |
| Facility Technician | Yes | Yes | No | No | No | No | No |
| Facility Supervisor | Yes | Yes | Yes | Yes | Yes | Yes | No |

`If Owner` используется только для Requester на Permission Level 0.

Это базовая server permission model. Позже Workflow добавит transition rules, но не заменит эту матрицу.

---

# 5. Настроить Role Permission Manager

Последовательно настроить:

```text
Facility Location
Equipment
Service Request
```

строго по таблицам выше.

Для Requester у Service Request:

```text
Read = Yes
Write = Yes
Create = Yes
Only If Creator = Yes
```

Для Technician:

```text
Read = Yes
Write = Yes
```

Для Supervisor:

```text
Read = Yes
Write = Yes
Create = Yes
Delete = Yes
Report = Yes
Export = Yes
```

---

# 6. Проверить Requester One

Войти:

```text
requester.one@example.com
```

Проверить:

```text
Facility Location → Read
Equipment → Read
Equipment Create/Write → запрещены
```

Создать:

```text
Subject:     Requester One test
Location:    Room 101
Equipment:   EQ-0001 или пусто
Description: Проверка If Owner
Priority:    Medium
```

Status получает default:

```text
New
```

Requester One должен открыть и изменить собственную заявку.

---

# 7. Проверить Requester Two и If Owner

Войти:

```text
requester.two@example.com
```

Создать:

```text
Subject:     Requester Two test
Location:    Room 102
Description: Вторая заявка для проверки owner
Priority:    Low
```

Requester Two не получает обычный доступ к заявке Requester One, и наоборот.

Фиксируем:

```text
If Owner
→ permission row применяется только к Document своего owner
```

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

Изменить `Description` существующей заявки и сохранить.

На этом этапе Workflow ещё нет, поэтому Role Permission является основной границей редактирования.

---

# 9. Проверить Supervisor

Войти:

```text
supervisor.one@example.com
```

Проверить:

- все Service Request независимо от owner;
- Create / Write / Delete Service Request;
- Create / Write Facility Location и Equipment;
- Import / Export Equipment.

Для Delete создать отдельную временную заявку:

```text
Subject:     Delete permission test
Location:    Warehouse
Description: Temporary delete permission test
Priority:    Low
```

Удалить только её.

---

# 10. Permission Level

Под Administrator у:

```text
Equipment.notes
```

установить:

```text
Permission Level = 1
```

В Role Permission Manager добавить:

```text
Role: Facility Supervisor
Permission Level: 1
Read: Yes
Write: Yes
```

Requester/Technician Level 1 не получают.

Проверить под реальными пользователями.

Фиксируем:

```text
Permission Level
= field-level permission layer
```

Он не создаёт отдельную роль и не заменяет Level 0 document permissions.

---

# 11. Проверить metadata в Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/equipment/equipment.json
```

Изменение:

```text
Equipment.notes.permlevel = 1
```

является Standard metadata и попадает в source app.

Role Permission Manager configuration пока живёт в site DB; перенос будет собран L11 через Export Customizations.

---

# 12. Создать временного Restricted Technician

Для изолированной проверки дополнительных permission mechanisms создать:

```text
technician.restricted@example.com
First Name: Restricted Technician
User Type: System User
Enabled: Yes
Role: Facility Technician
Send Welcome Email: No
```

Этот User **не является частью финальной operating model**.

---

# 13. User Permission experiment

Создать:

```text
User:           technician.restricted@example.com
Allow:          Facility Location
For Value:      Room 101
Applicable For: Service Request
```

Под Restricted Technician проверить:

```text
Room 101 Service Request
→ обычный доступ есть

Room 102 / Warehouse / Floor 2
→ обычного доступа нет
```

Модель:

```text
Role Permission
→ DocType в принципе доступен

User Permission
→ дополнительно сужает допустимые связанные значения / Documents
```

---

# 14. Share experiment

Под Administrator открыть одну Service Request:

```text
Location = Room 102
```

Создать Share:

```text
User:  technician.restricted@example.com
Read:  Yes
Write: No
```

Под Restricted Technician проверить:

```text
обычные Room 102 заявки
→ недоступны

конкретная shared заявка
→ доступна для чтения
```

Фиксируем:

```text
User Permission
= систематическое ограничение

Share
= точечное исключение Document
```

---

# 15. Почему experiment обязательно очищается

В `v16.32.0` штатный `Assign To` после создания ToDo проверяет доступ assignee к reference document.

Если assignee не имеет доступа:

```text
document sharing разрешён
→ Frappe может автоматически создать DocShare Read

sharing запрещён
→ assignment может завершиться Missing Permission
```

Следовательно опасная модель:

```text
основной Technician ограничен Location User Permission
+
глобальный Round Robin
```

может привести не просто к «невидимой задаче», а к тому, что Assignment **начнёт сам менять access model через auto-Share** или падать при отключённом sharing.

Так не строим.

Основной принцип:

```text
Permission architecture
задаётся заранее

Assignment
не должен раздавать скрытые permission exceptions
```

---

# 16. Обязательный rollback L5

Под Administrator:

1. удалить лабораторный Share;
2. удалить User Permission `technician.restricted@example.com`;
3. установить Restricted Technician:

```text
Enabled = No
```

Затем под:

```text
technician.one@example.com
```

проверить обычный Role-based доступ к Service Request независимо от Location.

Это обязательный OUTPUT STATE L5.

---

# 17. Отрицательные проверки

Получить реальные отказы:

```text
Requester → Create Equipment запрещён
Requester → чужая Service Request запрещена
Technician → Create Service Request запрещён
Restricted Technician до rollback → обычная Room 102 заявка запрещена
```

Administrator не является доказательством permission model.

---

# 18. Зафиксировать metadata L5

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

# 19. State contract L5

## Preconditions

```text
3 core DocType
valid working data L4
```

## Persistent mutations

```text
3 Roles
4 main System Users
Role Permission configuration
Equipment.notes Permission Level 1
```

## Temporary mutations

```text
technician.restricted@example.com enabled
User Permission Room 101
one explicit Share Room 102
```

## Rollback

```text
Share deleted
User Permission deleted
Restricted Technician disabled
```

## Output state

```text
technician.one@example.com
→ no Location User Permission

technician.two@example.com
→ does not exist yet
```

## Git state

```text
Equipment metadata committed
working tree clean
```

---

# 20. Приёмка L5

L5 принят, если:

- существуют три роли;
- четыре основных пользователя работают отдельными входами;
- Requester ограничен `If Owner`;
- Technician имеет общий Role-based Read/Write Service Request;
- Supervisor имеет расширенные права;
- `Equipment.notes = Permission Level 1`, Level 1 выдан Supervisor;
- User Permission и Share проверены на temporary user;
- Share и User Permission удалены;
- Restricted Technician отключён;
- `technician.two@example.com` ещё не существует;
- ученик объясняет, почему Assignment не должен использовать auto-Share как штатную permission policy;
- Git clean.

После L5 переходим к **L6 — совместная работа**, где Assignment будет введён как отдельная ось ответственности.
