# L5. Пользователи и права

L5 делает `facility_ops` многопользовательским.

Новых предметных DocType в уроке нет.

Цель: настроить реальные роли и доступ к уже существующим `Facility Location`, `Equipment` и `Service Request`, затем проверить ограничения отдельными входами под обычными пользователями.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

Роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Учебные пользователи:

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
→ читает и редактирует доступные Service Request
→ не создаёт и не удаляет их

Supervisor
→ управляет рабочими данными приложения
→ видит все Service Request
→ имеет расширенные права на отчёт/экспорт
```

В конце урока дополнительно:

- `technician.one@example.com` ограничен через `User Permission` заявками для `Room 101`;
- одна заявка из другого помещения разово открыта этому пользователю через `Share`;
- поле `Equipment.notes` имеет Permission Level 1 и доступно только Supervisor.

Главное различие урока:

```text
Role Permission
= что пользователь в принципе может делать с DocType

If Owner
= те же права только для Documents, которые пользователь создал

User Permission
= какие значения связанных данных пользователь может видеть

Share
= точечное исключение для конкретного Document
```

---

# 1. Проверить состояние после L4

В терминале:

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

В Desk должны существовать:

```text
Facility Location
Equipment
Service Request
```

и несколько Service Request из L4.

---

# 2. Не путать права и назначение

В L5 мы ещё не используем `Assign To`.

Сейчас решаем только вопрос доступа:

```text
кто может открыть DocType
кто может читать Document
кто может создавать
кто может изменять
кто может удалять
какие Documents видны
```

Назначение конкретной заявки конкретному исполнителю будет в L6.

---

# 3. Создать три роли

Через Awesomebar открыть:

```text
Role
```

Создать:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

Дополнительные поля Role без необходимости не менять.

Проверить, что все три роли активны.

---

# 4. Создать четырёх System User

Через Awesomebar открыть:

```text
User
```

Создать четыре пользователя.

## Requester One

```text
Email:              requester.one@example.com
First Name:         Requester One
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Requester
```

## Requester Two

```text
Email:              requester.two@example.com
First Name:         Requester Two
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Requester
```

## Technician One

```text
Email:              technician.one@example.com
First Name:         Technician One
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Technician
```

## Supervisor One

```text
Email:              supervisor.one@example.com
First Name:         Supervisor One
User Type:          System User
Enabled:            Yes
Send Welcome Email: No
Role:               Facility Supervisor
```

Для каждого пользователя задать отдельный учебный пароль через поле/действие установки пароля, доступное на форме User в фактическом v16.32.0.

Пароли в Git не сохранять.

Не выдавать этим пользователям:

```text
System Manager
Administrator
```

иначе проверка прав теряет смысл.

---

# 5. Зафиксировать матрицу до настройки

Используем минимальную матрицу.

## Facility Location

| Role | Read | Write | Create | Delete |
|---|---:|---:|---:|---:|
| Facility Requester | Yes | No | No | No |
| Facility Technician | Yes | No | No | No |
| Facility Supervisor | Yes | Yes | Yes | No |

Удаление узлов дерева Supervisor не выдаём в базовом уроке.

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

`If Owner` включаем только у Requester и только на Permission Level 0.

---

# 6. Настроить Facility Location в Role Permission Manager

Через Awesomebar открыть:

```text
Role Permission Manager
```

Выбрать:

```text
DocType: Facility Location
```

Добавить/настроить роли по матрице:

```text
Facility Requester
Read = Yes

Facility Technician
Read = Yes

Facility Supervisor
Read   = Yes
Write  = Yes
Create = Yes
```

Не включать Delete.

Сохранить изменения.

---

# 7. Настроить Equipment

В Role Permission Manager выбрать:

```text
DocType: Equipment
```

Настроить:

## Facility Requester

```text
Read = Yes
```

## Facility Technician

```text
Read = Yes
```

## Facility Supervisor

```text
Read   = Yes
Write  = Yes
Create = Yes
Import = Yes
Export = Yes
```

Delete не включать.

---

# 8. Настроить Service Request

В Role Permission Manager выбрать:

```text
DocType: Service Request
```

## Facility Requester

Permission Level:

```text
0
```

Включить:

```text
Read            = Yes
Write           = Yes
Create          = Yes
Only If Creator = Yes
```

В интерфейсе `Only If Creator` соответствует `if_owner`.

Не включать:

```text
Delete
Report
Export
```

## Facility Technician

```text
Read  = Yes
Write = Yes
```

Не включать:

```text
Create
Delete
Report
Export
```

## Facility Supervisor

```text
Read   = Yes
Write  = Yes
Create = Yes
Delete = Yes
Report = Yes
Export = Yes
```

`Only If Creator` выключен.

---

# 9. Проверить Requester One

Выйти из `Administrator`.

Войти:

```text
requester.one@example.com
```

Проверить:

1. `Facility Location` открывается для чтения.
2. `Equipment` открывается для чтения.
3. создать новый Equipment нельзя.
4. изменить Equipment нельзя.
5. `Service Request` позволяет создать новую заявку.

Создать заявку:

```text
Subject:     Requester One test
Location:    Room 101
Equipment:   EQ-0001
Description: Проверка If Owner
Priority:    Medium
Status:      New
```

Сохранить.

Запомнить номер созданной заявки.

Проверить, что Requester One может её открыть и изменить Description.

---

# 10. Проверить Requester Two и доказать If Owner

Выйти.

Войти:

```text
requester.two@example.com
```

Создать свою заявку:

```text
Subject:     Requester Two test
Location:    Room 102
Description: Вторая заявка для проверки owner
Priority:    Low
Status:      New
```

Сохранить.

Теперь открыть список `Service Request`.

Requester Two не должен получить обычный доступ к заявке, созданной Requester One.

А Requester One не должен получить обычный доступ к заявке Requester Two.

Это и есть проверка:

```text
If Owner
= owner Document должен совпадать с текущим пользователем
```

Не считать проверкой ситуацию, когда тест выполнен только одним Requester.

---

# 11. Проверить Technician до User Permission

Войти:

```text
technician.one@example.com
```

Проверить:

```text
Facility Location → Read
Equipment         → Read
Service Request   → Read + Write
```

Technician не должен:

```text
создавать Equipment
создавать Service Request
удалять Service Request
```

Проверить изменение существующей заявки:

```text
Description → добавить строку "Technician permission test"
```

Сохранить.

Пока User Permission не создан, Technician должен видеть доступные по Role Permission заявки независимо от их owner.

---

# 12. Проверить Supervisor

Войти:

```text
supervisor.one@example.com
```

Проверить:

- видны все Service Request независимо от owner;
- можно создавать и редактировать Service Request;
- доступно удаление Service Request;
- Equipment можно создавать и изменять;
- Facility Location можно создавать и изменять;
- у Equipment доступны Export/Import в рамках выданных прав.

Удаление реальных учебных данных для проверки не требуется.

Если нужно проверить Delete, создать временную заявку:

```text
Subject:     Delete permission test
Location:    Warehouse
Description: Temporary
Priority:    Low
Status:      New
```

и удалить только её.

---

# 13. Изучить Permission Level без нового поля

Вознуться под `Administrator`.

Используем уже существующее поле:

```text
Equipment.notes
```

Считаем его внутренней технической заметкой.

Открыть Standard DocType `Equipment` и для поля:

```text
Notes
```

установить:

```text
Permission Level = 1
```

Сохранить DocType.

Это изменение metadata приложения.

Теперь в Role Permission Manager для `Equipment` добавить для:

```text
Facility Supervisor
Permission Level = 1
Read  = Yes
Write = Yes
```

Requester и Technician Permission Level 1 не получают.

---

# 14. Проверить Permission Level

Под `supervisor.one@example.com` открыть Equipment с заполненным `Notes`.

Supervisor должен видеть поле и иметь возможность его изменить.

Под:

```text
requester.one@example.com
technician.one@example.com
```

поле `Notes` не должно быть доступно на тех же правах, что обычные поля Permission Level 0.

Главное:

```text
Role Permission Level 0
не даёт автоматически доступ к полям Level 1
```

`If Owner` в этом курсе не используем выше Permission Level 0.

---

# 15. Посмотреть metadata после Permission Level

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff -- \
  facility_ops/facility_operations/doctype/equipment/equipment.json
```

Найти изменение `permlevel` у поля `notes`.

Это попало в Git, потому что изменилось Standard metadata `Equipment`.

Но роли и изменения через Role Permission Manager в текущем уроке являются конфигурационными records конкретного site.

Их переносимость будет разобрана отдельно в L11.

---

# 16. Создать User Permission для Technician

Под `Administrator` через Awesomebar открыть:

```text
User Permission
```

Создать:

```text
User:           technician.one@example.com
Allow:          Facility Location
For Value:      Room 101
Applicable For: Service Request
```

Сохранить.

Если форма показывает настройку descendants, для `Room 101` она не нужна: это конечный узел.

---

# 17. Проверить User Permission

Войти:

```text
technician.one@example.com
```

Открыть `Service Request`.

Пользователь должен получать обычный доступ к заявкам, допустимым значением Location которых является:

```text
Room 101
```

Заявки из:

```text
Room 102
Warehouse
Floor 2
```

не должны попадать в обычную доступную выборку только потому, что Role `Facility Technician` имеет Read.

Итог:

```text
Role Permission
говорит: Service Request читать можно

User Permission
говорит: но только для разрешённого значения Facility Location
```

---

# 18. Разово открыть чужую заявку через Share

Под `Administrator` или пользователем с правом Share открыть одну Service Request с:

```text
Location = Room 102
```

которую `technician.one@example.com` после User Permission обычно не видит.

Использовать стандартное действие:

```text
Share
```

Добавить:

```text
User:  technician.one@example.com
Read:  Yes
Write: No
```

Сохранить Share.

---

# 19. Проверить Share

Снова войти:

```text
technician.one@example.com
```

Проверить два факта одновременно:

1. обычные заявки вне `Room 101` по-прежнему не видны;
2. конкретная shared-заявка из `Room 102` стала доступна для чтения.

Поскольку Share создан без Write, пользователь не должен получать через него право редактирования этой заявки.

Главное:

```text
User Permission
= систематическое ограничение набора данных

Share
= точечное разрешение на один Document
```

После проверки Share можно оставить до конца курса как учебный пример.

---

# 20. Проверить отрицательные сценарии

Нужно получить минимум четыре реальных отказа.

## Requester пытается создать Equipment

Ожидается отказ/отсутствие действия Create.

## Requester пытается открыть заявку другого Requester

Ожидается отсутствие обычного доступа из-за `If Owner`.

## Technician пытается создать Service Request

Ожидается отсутствие Create.

## Technician пытается открыть неразрешённую Room 102 заявку, которая не Shared

Ожидается отсутствие доступа из-за User Permission.

Проверка прав считается выполненной только если есть успешные и отрицательные сценарии.

---

# 21. Не делать Administrator доказательством прав

`Administrator` нужен для настройки.

Он не является тестовым пользователем приложения.

Неверная проверка:

```text
Administrator открыл Service Request
→ значит permissions работают
```

Правильная проверка:

```text
Requester One
Requester Two
Technician One
Supervisor One
→ каждый вошёл отдельно
→ каждый получил именно свой набор разрешений и отказов
```

---

# 22. Зафиксировать metadata L5 в Git

В этом уроке Standard metadata изменилось только осознанно:

```text
Equipment.notes
→ Permission Level 1
```

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

Добавить metadata:

```bash
git add \
  facility_ops/facility_operations/doctype/equipment/equipment.json

git diff --cached
```

Commit:

```bash
git commit -m "Restrict equipment notes by permission level"
git status
```

Ожидается:

```text
working tree clean
```

Не пытаться вручную копировать в Git:

```text
User
Role
User Permission
DocShare
Custom DocPerm
```

В L11 разберём, какие конфигурационные records должны поставляться вместе с app и каким штатным способом.

---

# 23. Самостоятельная работа

Без готовой последовательности выполнить задачу:

> Создать нового System User `technician.two@example.com`, выдать ему только `Facility Technician`, ограничить его Service Request значением `Warehouse` через User Permission и доказать отдельным входом, что Room 101 заявки ему недоступны.

Условия:

- новые предметные DocType не создавать;
- `System Manager` не выдавать;
- `Administrator` не использовать для проверки результата;
- Share не использовать для обхода задания;
- Git после создания пользователя и User Permission должен остаться чистым.

---

# 24. Приёмка L5

L5 принят, если ученик может показать следующее.

## Пользователи

Существуют и работают отдельные входы:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

## Role Permission Manager

Настроены права для:

```text
Facility Location
Equipment
Service Request
```

## If Owner

Requester One и Requester Two видят/изменяют собственные заявки, но не получают обычный доступ к заявкам друг друга.

## Permission Level

```text
Equipment.notes = Permission Level 1
```

и поле доступно Supervisor на соответствующем уровне.

## User Permission

```text
technician.one@example.com
→ Facility Location = Room 101
→ Applicable For = Service Request
```

ограничивает набор заявок.

## Share

Одна заявка из Room 102 разово доступна Technician для чтения, несмотря на обычное ограничение User Permission.

## Отрицательные проверки

Есть реальные примеры запрещённых Create / Read / Write/Delete действий.

## Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое после commit metadata.

## Объяснение

Ученик без подсказки отвечает:

1. Чем Role отличается от User?
2. Что задаёт Role Permission Manager?
3. Что делает `If Owner`?
4. Почему для проверки `If Owner` понадобились два Requester?
5. Чем Permission Level поля отличается от Permission Level роли?
6. Чем User Permission отличается от Role Permission?
7. Чем Share отличается от User Permission?
8. Почему Technician ещё не считается назначенным на заявку, даже если имеет Write?
9. Почему изменение `Equipment.notes.permlevel` попало в Git, а User Permission — нет?
10. Почему проверка под Administrator ничего не доказывает о правах обычных пользователей?

После принятия L5 переходим к **L6 — совместная работа**, где на уже настроенные права накладываются `Assign To`, `ToDo`, Comments, Timeline, Tags и Kanban.