# Лабораторная 22. Границы штатных permissions

## Что уже должно быть готово

Лабораторная 21 завершена.

Финальная модель перед диагностикой:

```text
Training User
Request Level 0:
  Read   ✓
  Create ✓
  Write  ✓
  Delete ☐
  Share  ☐
  Only if Creator ☐

Training Manager
Request Level 0:
  Read   ✓
  Create ✓
  Write  ✓
  Delete ✓
  Share  ✓

Training Manager
Request Level 1:
  Read  ✓
  Write ✓
```

User Permission:

```text
student.user@example.test
→ Training Area = North
```

Share:

```text
D21-Shared-South
→ student.user@example.test
→ Read only
```

---

## Что сейчас получим

Новых permission-механизмов в финальном состоянии не появится.

Главный результат — точная контрольная матрица четырёх Requests и понимание, какой слой объясняет каждый результат.

После всех опытов модель должна быть полностью восстановлена.

---

# Часть 1. Подготовь четыре контрольных документа

Работай под:

```text
student.manager@example.test
```

Менеджер имеет Level 1 Read + Write и может заполнить `Internal Cost`.

Установи:

```text
D18-User-Record
  Area: North
  Internal Cost: 101

D18-Manager-Record
  Area: North
  Internal Cost: 202

C12-Open-High-2
  Area: South
  Internal Cost: 303

D21-Shared-South
  Area: South
  Internal Cost: 404
  Notes: Read-only shared example
```

Все четыре сохрани.

Убедись, что owners остаются:

```text
D18-User-Record
→ student.user@example.test

D18-Manager-Record
→ student.manager@example.test

C12-Open-High-2
→ owner, созданный в предыдущих главах курса

D21-Shared-South
→ student.manager@example.test
```

Owner `C12-Open-High-2` не нужно менять.

---

# Часть 2. Построй базовую матрицу Training User

Полностью перезайди:

```text
student.user@example.test
FrappeCourse!2026
```

Для каждого документа проверь:

```text
виден ли в permission-aware Request List
открывается ли по прямому name
можно ли менять обычное Level 0 поле Notes
виден ли Internal Cost
```

Не меняй permissions во время этой части.

---

## Ожидаемая матрица

| Document | Area | Owner относительно User | Share | Read | Write | Internal Cost |
|---|---|---|---|---|---|---|
| `D18-User-Record` | North | свой | нет | да | да | нет |
| `D18-Manager-Record` | North | чужой | нет | да | да | нет |
| `C12-Open-High-2` | South | чужой | нет | нет | нет | недоступен |
| `D21-Shared-South` | South | чужой | Read | да | нет | нет |

Разбери каждую строку.

### `D18-User-Record`

```text
Role Read/Write
+
Area North разрешена
+
Only if Creator выключен
→ Read + Write
```

### `D18-Manager-Record`

Он чужой по owner, но:

```text
Only if Creator = ☐
```

поэтому owner сейчас не ограничивает доступ.

`Area = North`, значит обычный User также получает Read + Write.

### `C12-Open-High-2`

```text
Area = South
нет Share
→ User Permission отсекает Document
```

### `D21-Shared-South`

```text
Area = South
НО
есть explicit DocShare Read
→ Document доступен на Read
```

Write не разрешён, потому что Share остаётся read-only.

Во всех разрешённых документах:

```text
Internal Cost
```

обычному User не доступен из-за отсутствия Level 1 rule.

---

# Часть 3. Сравни Training Manager

Перезайди:

```text
student.manager@example.test
```

Проверь те же четыре Documents.

Ожидается:

```text
все 4 доступны
все 4 можно Write
Internal Cost виден во всех 4
```

Почему:

```text
Training Manager
→ базовые Request rights
→ нет Training Area User Permission
→ Level 1 Read + Write
```

Share на `D21-Shared-South` для менеджера не является причиной его собственного доступа: он и без Share имеет обычные permissions.

---

# Намеренная поломка 1 — убери Role Read

Теперь проверим, что произойдёт, если сломать **только один слой**.

Работай под `Administrator`.

## 1. Временно сними Read у Training User

В Role Permissions Manager:

```text
Document Type = Request
Role = Training User
Level = 0
```

установи:

```text
Read = ☐
```

Не меняй:

```text
Write
Create
User Permission
Share
Only if Creator
```

---

## 2. Перезайди Student User

Ожидаемый результат для обычных Request:

```text
D18-User-Record
→ обычного Read больше нет

D18-Manager-Record
→ обычного Read больше нет
```

Но проверь:

```text
D21-Shared-South
```

Он должен оставаться доступным на Read через explicit Share.

В permission-aware List при отсутствии role Read/Select для `Request` Framework может оставить именно shared Documents этого DocType.

То есть ожидаемая идея:

```text
обычный канал Role Permission сломан
но отдельный Share всё ещё существует
```

`C12-Open-High-2` по-прежнему не должен внезапно появиться: у него Share нет.

---

# Восстановление 1

Сразу верни под `Administrator`:

```text
Training User
Read = ✓
```

Полностью перезайди Student User.

Проверь:

```text
D18-User-Record
D18-Manager-Record
```

снова доступны.

**Не переходи к следующему опыту, пока Read не восстановлен.**

---

# Намеренная поломка 2 — включи owner constraint

Теперь меняем только:

```text
Only if Creator
```

## 3. Временно включи

Под `Administrator`:

```text
Request
Training User
Level 0
Only if Creator = ✓
```

Остальные права оставь как были.

---

## 4. Перезайди Student User

Проверь три ключевых Request.

### Свой North

```text
D18-User-Record
```

Ожидается:

```text
доступен
Write доступен
```

### Чужой North

```text
D18-Manager-Record
```

Ожидается:

```text
обычным путём недоступен
```

Хотя:

```text
Area = North
```

owner constraint стал дополнительным ограничением permission row.

### Чужой South, но Shared

```text
D21-Shared-South
```

Ожидается:

```text
по-прежнему доступен на Read
```

Это самый важный результат опыта.

Документ одновременно:

```text
не owner
Area = South
```

но explicit Share остаётся отдельным исключением.

Write по-прежнему не должно появиться, потому что Share read-only.

---

# Восстановление 2

Под `Administrator` верни:

```text
Only if Creator = ☐
```

Полностью перезайди Student User.

Убедись:

```text
D18-User-Record
→ Read + Write

D18-Manager-Record
→ Read + Write

C12-Open-High-2
→ denied

D21-Shared-South
→ Read only
```

---

# Часть 4. Финальный аудит блока D

Под `Administrator` проверь настройки по очереди.

## Users

```text
student.user@example.test
  Enabled: ✓
  User Type: System User
  Roles:
    Training User

student.manager@example.test
  Enabled: ✓
  User Type: System User
  Roles:
    Training User
    Training Manager
```

---

## Roles

```text
Training User
  Desk Access: ✓

Training Manager
  Desk Access: ✓
```

---

## Request Level 0

```text
Training User
  Read   ✓
  Create ✓
  Write  ✓
  Delete ☐
  Share  ☐
  Only if Creator ☐

Training Manager
  Read   ✓
  Create ✓
  Write  ✓
  Delete ✓
  Share  ✓
  Only if Creator ☐
```

Ненужные Select/Print/Email/Report/Import/Export/Mask выключены, как в лабораторной 18.

---

## Request Level 1

```text
Training User
→ rule отсутствует

Training Manager
→ Read + Write
```

---

## Training Area

```text
North
South
```

Role permissions:

```text
Training User    → Read
Training Manager → Read
```

---

## Request.area

```text
Link → Training Area
Ignore User Permissions = ☐
```

---

## User Permission

Ровно одна учебная Area permission для обычного User:

```text
User:      student.user@example.test
Allow:     Training Area
For Value: North
Is Default: ✓
Apply To All Document Types: ✓
```

У менеджера такой User Permission нет.

---

## Share

На:

```text
D21-Shared-South
```

остаётся:

```text
student.user@example.test
Read  ✓
Write ☐
```

---

## Global sharing

```text
Disable Document Sharing = ☐
```

---

## Custom permission code

На этом этапе курса **не должно быть создано**:

```text
permission_query_conditions hook
custom has_permission hook
Permission Query Server Script
```

Блок D изучает штатную permission model и только обозначает границу к будущему server-side расширению.

---

## Проверка себя

Ответь без подсказки.

1. Какой слой объясняет Read/Write/Create/Delete всего Request?
2. Какой слой объясняет отсутствие Internal Cost у Training User?
3. Какой слой убирает обычные South Requests?
4. Что делает Only if Creator?
5. Почему D21-Shared-South виден несмотря на South?
6. Почему он read-only?
7. Почему снятие Role Read не уничтожило существующий Share?
8. Почему несколько Roles менеджера складывают возможности?
9. Почему List filter не заменяет User Permission?
10. Когда появляется причина для custom server-side permission logic?
11. Нужно ли уже сейчас писать `permission_query_conditions` или `has_permission`?

---

## Состояние стенда после лабораторной

Все временные поломки восстановлены.

Контрольные значения:

```text
D18-User-Record
  Area: North
  Internal Cost: 101

D18-Manager-Record
  Area: North
  Internal Cost: 202

C12-Open-High-2
  Area: South
  Internal Cost: 303

D21-Shared-South
  Area: South
  Internal Cost: 404
  Notes: Read-only shared example
  Share to student.user@example.test: Read only
```

`Training User` снова имеет обычный:

```text
Read + Create + Write
Only if Creator = ☐
```

и User Permission:

```text
Training Area = North
```

`Training Manager` имеет расширенные права и Level 1 Read + Write.

Оба учебных Users остаются Enabled System Users с рабочим локальным паролем.

Это точное входное состояние следующего блока: [**23. Assignment и ToDo**](../23_ASSIGNMENT_AND_TODO.md).
