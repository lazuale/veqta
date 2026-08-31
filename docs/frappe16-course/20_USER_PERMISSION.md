# 20. User Permission

К этому моменту мы уже умеем отвечать на два разных вопроса:

```text
Role Permission
→ что пользователь может делать с Request

Permission Level
→ какие поля внутри Request ему доступны
```

Теперь третий вопрос:

> какие именно Requests из всего DocType доступны конкретному User?

Для ограничений по связанным значениям Frappe использует **User Permission**.

Проверено для **Frappe Framework v16.32.0**.

---

## Сценарий курса

Создадим справочник:

```text
Training Area
├── North
└── South
```

И добавим в `Request`:

```text
Area
Link → Training Area
```

Обычному User разрешим:

```text
Training Area = North
```

Менеджеру такого ограничения не дадим.

Получим:

```text
Training User
→ может работать с Request
→ но обычный доступ ограничен Area = North

Training Manager
→ работает и с North, и с South
```

---

# User Permission не выдаёт базовый Read

Это критически важно.

Неправильно:

```text
User Permission North
→ автоматически даёт Read на Request
```

Правильно:

```text
Role Permission
→ Training User имеет Read на Request

User Permission
→ из этих Request оставляет допустимые связанные значения
```

То есть User Permission **сужает** уже существующую permission model.

---

# Почему нужен Link

User Permission естественно работает с связанными Documents.

Например:

```text
Request.area
→ Link → Training Area
```

У пользователя разрешено:

```text
Training Area = North
```

Framework видит связь и может построить ограничение:

```text
Request.area
→ North
```

Это не универсальный конструктор любого бизнес-условия вроде:

```text
Status = Open
AND Priority = High
```

Для таких правил существуют другие механизмы.

---

# Основные поля User Permission

Metadata `User Permission` в `v16.32.0` содержит:

```text
User
Allow
For Value
Is Default
Apply To All Document Types
Applicable For
Hide Descendants
```

Для нашей базовой практики нужны первые пять.

---

## User

Кому назначается правило:

```text
student.user@example.test
```

Это ограничение конкретного User, а не Role.

---

## Allow

DocType разрешённого значения:

```text
Training Area
```

---

## For Value

Конкретный разрешённый Document:

```text
North
```

`For Value` — Dynamic Link, чей целевой DocType определяется `Allow`.

Получается:

```text
Allow = Training Area
        ↓
For Value = North
```

---

# Apply To All Document Types

По умолчанию:

```text
Apply To All Document Types = 1
```

Это означает: разрешённое значение может учитываться во всех подходящих связанных местах permission engine.

Для курса оставим именно так.

Это удобно, потому что User Permission будет участвовать и в:

```text
Request.area
```

и в обычном Link-подборе самих `Training Area`.

---

# Applicable For

Если снять:

```text
Apply To All Document Types
```

можно указать:

```text
Applicable For = Request
```

Тогда конкретная permission применяется только в соответствующем контексте.

В нашей лабораторной это не нужно: `Training Area = North` является общей учебной границей этого User.

---

# Is Default

User Permission можно отметить:

```text
Is Default = 1
```

Тогда разрешённое значение может использоваться Framework как default для соответствующего Link при создании нового Document.

Мы отметим:

```text
North
→ Is Default = ✓
```

Это не означает, что default и permission — одно и то же.

`North` одновременно:

```text
разрешён
и
предпочтителен как default
```

---

# Несколько разрешённых значений

Если пользователю нужны:

```text
North
South
```

создаются две User Permissions одного `Allow`.

Тогда разрешённым набором будут оба значения.

В курсе оставляем только:

```text
North
```

чтобы результат был однозначным.

---

# Как User Permission влияет на List View

Permission-aware query engine `v16.32.0` строит conditions по Link fields.

Упрощённо:

```text
User Permission
Training Area = North
        ↓
Request.area
        ↓
List View получает разрешённые Request
```

Это server-side permission condition, а не пользовательский фильтр списка.

Поэтому:

```text
List Filter
≠ User Permission
```

Первый меняет рабочую выборку среди доступных данных.

Второй участвует в определении того, какие данные пользователю вообще разрешены.

---

# Прямое открытие Document тоже проверяется

Ограничение не должно работать только в списке.

Если User знает name South Request и пытается открыть его напрямую, permission engine проверяет Link fields конкретного Document.

Поэтому лаборатория обязательно сравнит:

```text
виден ли South Request в List
и
открывается ли он напрямую
```

Оба результата должны соответствовать одной permission model.

---

# Ignore User Permissions у Link-поля

У Link DocField есть настройка:

```text
Ignore User Permissions
```

Если она включена, permission engine пропускает User Permission для **этой Link-связи**.

Для нашего:

```text
Request.area
```

это означает: Area перестанет ограничивать Request через User Permission.

Но это не означает:

```text
пользователь стал Administrator
```

и не отключает всю систему permissions.

В лабораторной временно включим этот флаг и увидим расширение C12-списка с трёх до шести Requests, затем обязательно вернём его в `0`.

---

# Важный нюанс: пустое Link-поле

В `v16.32.0` есть системная настройка:

```text
Apply Strict User Permissions
```

Если strict mode не включён, query engine для связанного поля обычно допускает:

```text
Area пусто
OR
Area входит в разрешённые значения
```

Это значит, что на обычном Site нельзя честно сказать:

> любой Request без Area точно исчезнет у пользователя.

Именно поэтому лаборатория не считает случайные старые записи.

Мы заполним `Area` у **всех документов фиксированного набора**, по которому считаем результат.

Это важный приём воспроизводимой проверки permissions.

---

# Фиксированный набор C12

Шесть Requests из главы 12 получат точное распределение.

### North

```text
C12-Open-High-1
C12-Open-Medium
C12-Progress-High
```

### South

```text
C12-Open-High-2
C12-Progress-Low
C12-Done-High
```

Поэтому под Training User фильтр:

```text
Subject Like C12-%
```

после User Permission должен вернуть ровно:

```text
3
```

А Training Manager — ровно:

```text
6
```

---

# Почему Training Area тоже нужны permissions

`Area` — Link на отдельный DocType:

```text
Training Area
```

Обычным учебным Users нужен как минимум `Read` на этот справочник, иначе они не смогут нормально работать с Link.

Поэтому Role Permissions Manager получит простые read-only rules:

```text
Training User
→ Training Area Read

Training Manager
→ Training Area Read
```

Управлять самим справочником в этой главе они не будут.

---

# Что произойдёт в лабораторной

Ты:

1. создашь Standard DocType `Training Area`;
2. создашь `North` и `South`;
3. дашь обеим учебным Roles `Read` на `Training Area`;
4. добавишь Standard Link `Request.area`;
5. распределишь фиксированные C12 и D18 документы по Area;
6. создашь User Permission `Training Area = North`;
7. сделаешь North default;
8. проверишь 3 North против 6 total C12;
9. проверишь прямой отказ на South Request;
10. временно включишь `Ignore User Permissions` у `Request.area`;
11. увидишь расширение доступа;
12. полностью восстановишь Link и User Permission.

---

# Что запомнить

1. Role Permission определяет действия над DocType.
2. User Permission ограничивает конкретного User разрешёнными связанными Documents.
3. User Permission особенно естественна для Link-полей.
4. `Apply To All Document Types` и `Applicable For` управляют областью применения.
5. `Is Default` не заменяет сам permission.
6. `Ignore User Permissions` относится к конкретной Link-связи, а не ко всей security model.
7. Пустые Link values могут вести себя иначе при strict и non-strict режиме — поэтому тестовые данные должны быть заполнены явно.
8. List View и прямое открытие должны согласовываться с одной серверной permission model.

---

## Проверенные исходники v16.32.0

- [User Permission metadata](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/user_permission/user_permission.json)
- [User Permission controller](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/user_permission/user_permission.py)
- [Permission engine](https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py)
- [Query permission conditions](https://github.com/frappe/frappe/blob/v16.32.0/frappe/database/query.py)

Теперь выполни [**лабораторную 20**](labs/20_USER_PERMISSION_LAB.md).

После неё переходи к [**21. Owner и Sharing**](21_OWNER_AND_SHARING.md).
