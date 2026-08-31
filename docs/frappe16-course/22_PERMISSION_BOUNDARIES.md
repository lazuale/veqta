# 22. Границы штатных permissions

За главы 17–21 мы собрали рабочую permission model не по отдельным теориям, а на одном живом `Request`.

Теперь нужно научиться делать самое важное для реальной эксплуатации:

> диагностировать доступ по слоям и понимать, когда штатных механизмов уже действительно не хватает.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

### Users и Roles

```text
student.user@example.test
└── Training User

student.manager@example.test
├── Training User
└── Training Manager
```

Оба — System User.

### Request Role Permissions

```text
Training User
→ Read + Create + Write
→ no Delete
→ no Share
→ Only if Creator = off

Training Manager
→ Read + Create + Write + Delete + Share
```

### Field permission

```text
Internal Cost
Perm Level = 1

Training Manager
→ Level 1 Read + Write

Training User
→ Level 1 rule отсутствует
```

### User Permission

```text
student.user@example.test
→ Training Area = North
```

### Share

```text
D21-Shared-South
Area = South
→ shared to student.user@example.test
→ Read only
```

То есть у нас уже достаточно слоёв, чтобы увидеть реальную permission evaluation.

---

# Не ищи одну «главную галочку»

Когда пользователь говорит:

> я не вижу документ

плохой подход:

```text
открыть настройки
поставить несколько галочек
перезайти
надеяться
```

Правильный подход — пройти уровни по порядку.

---

# Слой 1. Может ли User вообще работать в Desk

Сначала:

```text
Enabled?
User Type = System User?
есть Role с Desk Access?
```

Если User стал Website User, обсуждать `Request Write` рано.

Это мы уже видели в лабораторной 17.

---

# Слой 2. Есть ли базовый Role Permission на DocType

Следующий вопрос:

```text
какие Roles есть у User?
```

и затем:

```text
какие Level 0 permissions эти Roles дают на Request?
```

Например:

```text
Training User
Read = ✓
```

даёт базовый read-кандидат.

Если обычного Role Read нет, User Permission не создаёт его из воздуха.

Но отдельный Share конкретного Document может стать дополнительным каналом доступа — это проверим ещё раз в лабораторной.

---

# Слой 3. Ограничен ли конкретный Document

После базовой Role permission появляются document-level constraints.

В нашем курсе это:

```text
User Permission
Only if Creator
```

### User Permission

```text
Area = North
```

может убрать South Request из обычной доступной выборки.

### Only if Creator

```text
owner == current_user
```

может ограничить permission row только собственными Documents.

Это разные условия.

---

# Слой 4. Есть ли Share-исключение

Если обычные constraints документ не пропускают, permission engine дополнительно учитывает Sharing.

В `database/query.py` `v16.32.0` логика описана очень явно:

```text
shared documents trump all other restrictions
```

Поэтому:

```text
D21-Shared-South
Area = South
```

всё равно доступен North-only User на Read.

Это не значит, что User Permission выключен.

Значит только:

```text
для этого одного Document существует явное исключение
```

---

# Слой 5. Какие поля доступны

Даже когда сам Document уже разрешён, остаётся field-level permission.

Например:

```text
D21-Shared-South
→ Document Read есть через Share
```

но:

```text
Internal Cost
Perm Level = 1
```

обычному Training User не раскрывается.

То есть:

```text
доступ к Document
≠ автоматически доступ ко всем полям
```

---

# Разрешения нескольких Roles складываются

У менеджера:

```text
Training User
Training Manager
```

Frappe собирает подходящие permission rows всех Roles.

Поэтому если:

```text
Training User Delete = 0
Training Manager Delete = 1
```

это не означает конфликт `0 против 1`.

Обычная модель разрешений работает как набор разрешающих правил.

`Training Manager` даёт менеджеру Delete.

---

# Почему во Frappe нет простой универсальной кнопки DENY

Если бы каждая Role одновременно могла давать `ALLOW` и абсолютный `DENY`, несколько ролей быстро превращались бы в трудно объяснимую таблицу конфликтов.

Frappe в базовой модели идёт другим путём:

```text
Roles
→ дают разрешения

User Permission / owner / Share / field level
→ уточняют область конкретного доступа
```

Это не означает, что модель решает абсолютно любое правило без кода.

Но сначала нужно использовать её по назначению.

---

# List View и прямое открытие должны быть согласованы

Проверяем два разных пути:

```text
1. попадает ли Document в permission-aware List
2. разрешается ли открыть конкретный name
```

Если результаты неожиданно расходятся, нельзя сразу говорить:

```text
permissions сломаны
```

Нужно проверить:

```text
Role Permission
User Permission
Only if Creator
Share
custom permission code, если он уже есть
```

В нашем курсе до главы 22 custom permission code ещё нет.

---

# UI-фильтр не является security boundary

Например:

```text
List Filter: Area = North
```

только просит интерфейс показать North среди уже доступных документов.

Это не замена:

```text
User Permission
```

Пользователь может убрать List Filter.

Server-side User Permission от этого не исчезает.

---

# Hidden не является Role Permission

Аналогично:

```text
Hidden = 1
```

не заменяет:

```text
Perm Level
```

Если поле чувствительное, security model должна описывать **право на поле**, а не только его внешний вид.

Мы уже доказали это на `Internal Cost`.

---

# Как диагностировать доступ по шагам

Практический порядок для обычного Document:

```text
1. User enabled и System User?
2. Какие Roles реально назначены?
3. Есть ли у них Read/Write/Create/... на DocType Level 0?
4. Включён ли Only if Creator?
5. Есть ли User Permissions на сам DocType или его Link fields?
6. Не стоит ли Ignore User Permissions на Link?
7. Есть ли DocShare на конкретный Document?
8. Какой Permission Level у нужного поля?
9. Проверяется List или конкретный Document?
10. После изменения permissions пользователь полностью перезашёл/кэш обновился?
```

Не обязательно каждый раз менять все настройки.

Напротив: **меняем один слой и повторяем тот же тест**.

---

# Что покажет финальная лаборатория блока

Мы возьмём четыре фиксированных Request:

```text
D18-User-Record
D18-Manager-Record
C12-Open-High-2
D21-Shared-South
```

И построим фактическую матрицу:

```text
Owner
Area
Shared?
Read?
Write?
Internal Cost?
```

Так permissions перестанут быть набором абстрактных терминов.

---

# Контролируемый опыт 1: убрать Role Read

У `Training User` временно снимем:

```text
Read
```

Обычные North Requests исчезнут.

Но `D21-Shared-South` имеет явный:

```text
DocShare Read
```

В текущем `v16.32.0` permission-aware query умеет в ситуации без role Read показать именно shared Documents этого DocType.

Это важный урок:

```text
Share
→ отдельный канал доступа к конкретной записи
```

После опыта Read сразу восстановим.

---

# Контролируемый опыт 2: включить owner constraint

Затем, уже при восстановленном Read, временно включим:

```text
Only if Creator
```

Получим:

```text
D18-User-Record
→ свой North
→ доступен

D18-Manager-Record
→ чужой North
→ обычным путём недоступен

D21-Shared-South
→ чужой South
→ всё ещё доступен на Read через Share
```

После этого owner restriction снова будет выключен.

---

# Где заканчиваются штатные permissions

Стандартная модель хорошо выражает требования вроде:

```text
разные действия разных Roles
поля разных уровней доступа
ограничение по связанному Area / Company / Department
только свои Documents
разовое исключение для одной записи
```

Но представим правило:

```text
пользователь может читать Request,
если
owner == current_user
ИЛИ
reviewer == current_user
ИЛИ
он указан в одной из строк Review Team
```

Это уже не естественная комбинация наших простых штатных настроек.

Здесь появляется нормальная причина расширять permission model серверным кодом App.

---

# Два extension point, которые нужно знать по имени

В Frappe существуют, в частности:

```text
permission_query_conditions
has_permission
```

На этом этапе **не пишем их**.

Важно понять границу.

### `permission_query_conditions`

Дополняет permission-aware условия выборок списка.

### `has_permission`

Участвует в проверке конкретного Document.

В текущем `v16.32.0` controller `has_permission` имеет важную границу:

```text
может дополнительно DENY
но не должен магически GRANT право,
которого не было в базовой permission model
```

Этого знания пока достаточно.

Практика серверного кода будет позже, когда уже будут изучены нужные инструменты разработки.

---

# Почему не пишем permission code сейчас

Потому что блок D должен сначала научить уверенно использовать штатную модель.

Если сразу добавить Python:

```text
непонятный List
+ непонятный has_permission
+ User Permission
+ Share
+ owner
```

новичок не сможет определить источник результата.

Поэтому итог блока D должен быть:

```text
штатные permissions понятны руками
граница к custom server logic понятна концептуально
custom permission code ещё отсутствует
```

---

# Что произойдёт в лабораторной

Ты:

1. заполнишь `Internal Cost` у четырёх контрольных Requests;
2. построишь базовую permission matrix Training User;
3. сравнишь её с Training Manager;
4. временно снимешь Role Read и увидишь, что остаётся только shared Request;
5. восстановишь Read;
6. временно включишь Only if Creator;
7. увидишь собственный North и shared South как два разных канала доступа;
8. восстановишь owner rule;
9. проверишь финальное состояние всего блока D;
10. не создашь ни одного permission hook или Server Script.

---

# Что запомнить

1. Диагностика permissions идёт по слоям.
2. Role Permission даёт базовые действия.
3. User Permission и owner ограничивают обычный document access.
4. Share является явным document-level исключением.
5. Permission Level отдельно ограничивает поля.
6. List filter и Hidden не являются security model.
7. Менять несколько permission layers одновременно — плохой способ диагностики.
8. Штатных механизмов хватает до тех пор, пока правило естественно ими выражается.
9. Сложная собственная логика доступа должна быть server-side.
10. `permission_query_conditions` и `has_permission` — extension points на будущее, а не обязательный код блока D.

---

## Проверенные исходники v16.32.0

- [Permission engine](https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py)
- [Permission-aware query engine](https://github.com/frappe/frappe/blob/v16.32.0/frappe/database/query.py)
- [Sharing backend](https://github.com/frappe/frappe/blob/v16.32.0/frappe/share.py)
- [User Permission](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/user_permission/user_permission.py)

Теперь выполни [**лабораторную 22**](labs/22_PERMISSION_BOUNDARIES_LAB.md).

После неё блок D закончен. Следующий блок начинается с [**23. Assignment и ToDo**](23_ASSIGNMENT_AND_TODO.md).
