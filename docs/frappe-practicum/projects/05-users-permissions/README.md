# L5. Пользователи и права

L5 делает `facility_ops` многопользовательским.

Новых предметных DocType в уроке нет.

Цель: настроить роли и права на уже существующие `Facility Location`, `Equipment` и `Service Request`, проверить `If Owner`, Permission Level, User Permission и Share под реальными пользователями, а затем вернуть стенд в состояние, пригодное для следующих уроков.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

Постоянные учебные роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Постоянные учебные пользователи после L5:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

Все четыре — `System User`.

Основная модель доступа:

```text
Requester
→ читает места и оборудование
→ создаёт Service Request
→ видит и редактирует только свои Service Request

Technician
→ читает места и оборудование
→ читает и редактирует Service Request
→ не создаёт и не удаляет их

Supervisor
→ управляет рабочими данными приложения
→ видит все Service Request
→ имеет расширенные права на отчёт/экспорт
```

Дополнительно в середине урока создаётся временный пользователь:

```text
technician.restricted@example.com
```

Он нужен только для изолированной проверки `User Permission` и `Share`. После проверки ограничения удаляются, а пользователь отключается. Это важно: следующие уроки не должны наследовать случайное ограничение Technician по одному помещению.

Главные различия:

```text
Role Permission
= что роль в принципе может делать с DocType

If Owner
= разрешение действует только для Documents текущего owner

Permission Level
= доступ к отдельным полям

User Permission
= систематически ограничивает допустимые связанные значения

Share
= точечно открывает конкретный Document
```

---

# 1. Проверить состояние после L4

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

В Desk уже существуют:

```text
Facility Location
Equipment
Service Request
```

и несколько заявок из L4.

---

# 2. Создать три роли

Через Awesomebar открыть `Role` и создать:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Проверить, что все роли активны.

---

# 3. Создать четырёх постоянных System User

Через `User` создать:

```text
requester.one@example.com
First Name: Requester One
Role: Facility Requester

requester.two@example.com
First Name: Requester Two
Role: Facility Requester

technician.one@example.com
First Name: Technician One
Role: Facility Technician

supervisor.one@example.com
First Name: Supervisor One
Role: Facility Supervisor
```

Для каждого:

```text
User Type: System User
Enabled: Yes
Send Welcome Email: No
```

Задать отдельный учебный пароль.

Не выдавать:

```text
System Manager
Administrator
```

`technician.two@example.com` здесь **не создаём**. Этот пользователь появится только в L9, когда действительно понадобится второй исполнитель для Round Robin.

---

# 4. Зафиксировать матрицу прав

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

`If Owner` используем только для Requester на Permission Level 0.

---

# 5. Настроить Role Permission Manager

Через `Role Permission Manager` последовательно настроить:

```text
Facility Location
Equipment
Service Request
```

строго по матрицам выше.

Для Requester у `Service Request` включить:

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

Войти как:

```text
requester.one@example.com
```

Проверить чтение `Facility Location` и `Equipment`, отсутствие создания/редактирования Equipment.

Создать заявку:

```text
Subject:     Requester One test
Location:    Room 101
Equipment:   EQ-0001
Description: Проверка If Owner
Priority:    Medium
Status:      New
```

Сохранить и запомнить номер.

Requester One должен иметь возможность открыть и изменить собственную заявку.

---

# 7. Проверить Requester Two и If Owner

Войти как:

```text
requester.two@example.com
```

Создать:

```text
Subject:     Requester Two test
Location:    Room 102
Description: Вторая заявка для проверки owner
Priority:    Low
Status:      New
```

Requester Two не должен получать обычный доступ к заявке Requester One, а Requester One — к заявке Requester Two.

Фиксируем:

```text
If Owner
= owner Document должен совпадать с текущим пользователем
```

---

# 8. Проверить Technician до дополнительных ограничений

Войти как:

```text
technician.one@example.com
```

Проверить:

```text
Facility Location → Read
Equipment         → Read
Service Request   → Read + Write
```

Technician не должен создавать или удалять `Service Request`.

Изменить Description существующей заявки и сохранить.

Важно: `technician.one@example.com` остаётся обычным универсальным Technician. На него не накладываем постоянный `User Permission` по Location.

---

# 9. Проверить Supervisor

Войти как:

```text
supervisor.one@example.com
```

Проверить:

- все Service Request независимо от owner;
- Create / Write / Delete для Service Request;
- Create / Write для Facility Location и Equipment;
- Import / Export для Equipment.

Для Delete создать отдельную временную заявку:

```text
Subject:     Delete permission test
Location:    Warehouse
Description: Temporary
Priority:    Low
Status:      New
```

и удалить только её.

---

# 10. Permission Level без нового поля

Вернуться под Administrator.

У существующего поля:

```text
Equipment.notes
```

установить:

```text
Permission Level = 1
```

В Role Permission Manager для `Equipment` добавить:

```text
Role: Facility Supervisor
Permission Level: 1
Read: Yes
Write: Yes
```

Requester и Technician Level 1 не получают.

Проверить под Supervisor и под обычными пользователями.

Главный вывод:

```text
Permission Level 0
не даёт автоматически доступ к полям Level 1
```

---

# 11. Проверить metadata в Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/equipment/equipment.json
```

Изменение `Equipment.notes.permlevel` относится к Standard metadata приложения.

Роли и Role Permission Manager пока являются site configuration. Их переносимость разберём в L11.

---

# 12. Создать временного Restricted Technician

Теперь отдельно изучаем `User Permission` и `Share`, не меняя постоянного Technician.

Создать:

```text
Email:              technician.restricted@example.com
First Name:         Restricted Technician
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Technician
```

Задать учебный пароль.

---

# 13. User Permission как временный эксперимент

Создать `User Permission`:

```text
User:           technician.restricted@example.com
Allow:          Facility Location
For Value:      Room 101
Applicable For: Service Request
```

Войти под этим пользователем.

Он должен получать обычный доступ к Service Request для:

```text
Room 101
```

и не получать обычный доступ к заявкам для:

```text
Room 102
Warehouse
Floor 2
```

Это демонстрирует:

```text
Role Permission
→ DocType доступен

User Permission
→ набор Documents дополнительно ограничен связанным значением
```

---

# 14. Share как точечное исключение

Под Administrator открыть одну заявку:

```text
Location = Room 102
```

Использовать `Share`:

```text
User:  technician.restricted@example.com
Read:  Yes
Write: No
```

Снова войти под Restricted Technician.

Проверить одновременно:

```text
обычные Room 102 заявки
→ недоступны

конкретная shared Room 102 заявка
→ доступна для чтения
```

Share не должен давать Write, если его не включали.

---

# 15. Обязательная очистка эксперимента

Этот шаг является частью L5, а не необязательной уборкой.

Под Administrator:

1. удалить созданный `Share`;
2. удалить `User Permission` для `technician.restricted@example.com`;
3. открыть временного пользователя и установить:

```text
Enabled = No
```

После очистки проверить под:

```text
technician.one@example.com
```

что обычный Technician снова видит все Service Request, разрешённые его Role Permission, независимо от Location.

Причина очистки:

```text
User Permission / Share
= изученный механизм

но

не часть итоговой модели доступа facility_ops
```

Если оставить Location-ограничение жить дальше, L9 Round Robin сможет назначить человеку заявку, которую тот сам не может открыть.

---

# 16. Отрицательные проверки

Получить реальные отказы:

```text
Requester → Create Equipment запрещён
Requester → чужая Service Request запрещена
Technician → Create Service Request запрещён
Restricted Technician до cleanup → обычная Room 102 заявка запрещена
```

Administrator не использовать как доказательство пользовательских прав.

---

# 17. Зафиксировать metadata L5 в Git

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

Не добавлять вручную в Git:

```text
User
Role
User Permission
DocShare
Custom DocPerm
```

---

# 18. Самостоятельная проверка

Без готовой последовательности:

> Временно снова включить `technician.restricted@example.com`, создать для него User Permission на `Warehouse`, доказать отдельным входом, что `Room 101` недоступен, затем удалить User Permission и снова отключить пользователя.

Условия:

- `technician.two@example.com` не создавать;
- `System Manager` не выдавать;
- Share для обхода задания не использовать;
- после упражнения Restricted Technician снова отключён;
- Git остаётся чистым.

---

# 19. Приёмка L5

L5 принят, если:

- существуют три роли;
- четыре постоянных пользователя работают отдельными входами;
- Requester ограничен `If Owner`;
- Technician имеет общий Read/Write на Service Request без постоянного Location-фильтра;
- Supervisor имеет расширенные права;
- `Equipment.notes = Permission Level 1` и Level 1 доступен Supervisor;
- User Permission и Share реально проверены на временном пользователе;
- после проверки Share и User Permission удалены, Restricted Technician отключён;
- `technician.two@example.com` ещё не существует;
- Git чист после commit metadata.

Ученик должен объяснить:

1. чем Role отличается от User;
2. что задаёт Role Permission Manager;
3. что делает `If Owner`;
4. чем Permission Level отличается от обычного DocType permission;
5. чем User Permission отличается от Role Permission;
6. чем Share отличается от User Permission;
7. почему User Permission нельзя бездумно оставлять перед глобальным Assignment Rule;
8. почему изменение `Equipment.notes.permlevel` попало в Git, а User Permission — нет.

После L5 переходим к **L6 — совместная работа**. Стенд входит в L6 без постоянных User Permission/Share ограничений на основных Technician.