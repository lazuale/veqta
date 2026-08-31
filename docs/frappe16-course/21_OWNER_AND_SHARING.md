# 21. Owner и Sharing

У нас уже есть четыре разных элемента permission model:

```text
User / Role
Role Permission
Permission Level
User Permission
```

Теперь разберём ещё два механизма, которые часто путают с бизнес-полями вроде `Responsible`:

```text
owner
Sharing
```

Они решают разные задачи.

Проверено для **Frappe Framework v16.32.0**.

---

# `owner` — системный создатель Document

У обычного Document Frappe есть системное поле:

```text
owner
```

Если пользователь сам создаёт Request, Framework записывает его User туда автоматически.

Из главы 18 у нас уже есть два хороших примера:

```text
D18-User-Record
owner = student.user@example.test

D18-Manager-Record
owner = student.manager@example.test
```

Оба имеют:

```text
Area = North
```

Поэтому они идеально подходят для чистого owner-эксперимента: Area одинаковая, отличается только создатель.

---

# owner ≠ Responsible

У нашего `Request` уже есть:

```text
Responsible
Link → User
```

Это бизнес-поле самого DocType.

Если менеджер создал Request и указал:

```text
Responsible = student.user@example.test
```

системный owner всё равно будет:

```text
student.manager@example.test
```

То есть:

```text
owner
→ кто создал Document

responsible
→ кого модель Request считает ответственным
```

Framework не считает эти значения взаимозаменяемыми.

---

# Only if Creator

В Role Permissions Manager у Level 0 rule есть:

```text
Only if Creator
```

В metadata permission rule это:

```text
if_owner
```

Если включить его у `Training User`, права этой строки начинают зависеть от:

```text
doc.owner == current_user
```

Именно это проверим в лабораторной.

---

## Что произойдёт с нашим Training User

Сейчас финальная row главы 20:

```text
Training User
Read   ✓
Create ✓
Write  ✓
Only if Creator ☐
```

Временно сделаем:

```text
Only if Creator ✓
```

Тогда для двух North-документов:

```text
D18-User-Record
owner = student.user@example.test
→ owner condition проходит

D18-Manager-Record
owner = student.manager@example.test
→ owner condition не проходит
```

После опыта обязательно вернём:

```text
Only if Creator ☐
```

чтобы дальнейший курс не превратился в модель «только свои Requests».

---

## Почему не строим две одинаковые строки одной Role

Иногда хочется выразить:

```text
все документы Read
свои документы Write
```

и попытаться создать две Level 0 rows одной и той же Role:

```text
Training User + Level 0 + normal
Training User + Level 0 + if_owner
```

Для первого практического маршрута так делать не будем.

В текущем Role Permissions Manager `Only if Creator` является свойством конкретной row `Role + Permission Level`, а backend обновления custom permissions ориентируется на эту комбинацию.

Поэтому в лаборатории owner-поведение проверяем как **одну временную конфигурацию**, а не учим сомнительной схеме дублирования строк.

---

# Sharing — другое

Теперь представим другой сценарий.

У обычного User есть:

```text
User Permission
Training Area = North
```

Поэтому South Request ему недоступен.

Но один конкретный South Request нужно показать ему как исключение.

Для этого существует:

```text
Share
```

---

# Что такое Share

Sharing выдаёт конкретному User доступ к **конкретному Document**.

Например:

```text
D21-Shared-South
Area = South
        ↓
Share
        ↓
student.user@example.test
Read only
```

Это не меняет:

```text
Training User Role
User Permission North
owner документа
```

Просто появляется явное document-level исключение.

---

# Где хранится Share

Framework использует системный DocType:

```text
DocShare
```

Запись содержит, среди прочего:

```text
user
share_doctype
share_name
read
write
submit
share
```

То есть Sharing — серверная запись permission model, а не локальная настройка браузера.

---

# Read при Share

В `frappe.share.add_docshare()` текущего `v16.32.0` есть прямое правило:

```text
при создании Share
Read добавляется всегда
```

Потом можно дополнительно разрешить:

```text
Write
Submit
Share
```

если пользователь, который делится документом, сам имеет соответствующие права.

---

# Нельзя раздать право, которого нет у тебя

Перед созданием Share Framework проверяет:

```text
имеет ли текущий User право Share на документ
```

А если он пытается выдать, например:

```text
Write
```

проверяется и его собственный `Write` на этот Document.

Именно поэтому в нашей модели:

```text
Training Manager
Share = ✓
Write = ✓
```

а:

```text
Training User
Share = ☐
```

Менеджер сможет создать учебный Share без Administrator.

---

# Share может быть исключением из других ограничений

Это особенно важная деталь `v16.32.0`.

В permission-aware list query Framework строит обычные ограничения, например:

```text
owner
User Permission
permission query conditions
```

а затем, если есть shared Documents, добавляет их как отдельное разрешённое множество.

В исходнике это сформулировано прямо:

```text
shared documents trump all other restrictions
```

Поэтому наш будущий:

```text
D21-Shared-South
Area = South
```

сможет появиться у пользователя, которому обычно разрешён только North.

Это не «сломанный User Permission».

Это явное исключение через Share.

---

# Share Read не означает Write

Если South Document расшарен только с:

```text
Read
```

то обычный User сможет его открыть.

Но `Write` через его обычную Role всё равно упирается в User Permission по Area.

А Share не содержит Write.

Поэтому ожидаемый итог:

```text
D21-Shared-South
→ виден
→ открывается
→ read-only
```

Затем лаборатория временно добавит Share Write, даст изменить `Notes` и снова вернёт Share в read-only состояние.

---

# Permission Level остаётся отдельным слоем

Даже если Document расшарен с Read или Write, это не означает автоматический доступ к:

```text
Internal Cost
Perm Level = 1
```

У `Training User` по-прежнему нет Level 1 rule.

Поэтому на Shared Request:

```text
обычные поля могут быть доступны
Internal Cost остаётся недоступен
```

Это очень хороший пример того, как permission layers складываются, а не заменяют друг друга.

---

# Share не меняет owner

Если:

```text
D21-Shared-South
owner = student.manager@example.test
```

и менеджер делится им с обычным User, после Share:

```text
owner
```

остаётся прежним.

Sharing не передаёт ownership.

---

# Sharing ≠ User Permission

```text
User Permission North
→ системное ограничение по связанному Training Area

Share D21-Shared-South
→ исключение для одной конкретной записи
```

Механизмы работают на разных уровнях.

---

# Sharing ≠ Assignment

В следующем блоке появится:

```text
Assignment / ToDo
```

Его вопрос:

> кому нужно выполнить работу?

Sharing отвечает на другой вопрос:

> кому разрешено открыть/изменить конкретный Document?

Не путай:

```text
доступ
≠
рабочее назначение
```

---

# Disable Document Sharing

В System Settings есть глобальная настройка:

```text
Disable Document Sharing
```

Если она включена, стандартная permission check не разрешает обычный Sharing.

В учебном стенде она должна оставаться выключенной:

```text
Disable Document Sharing = ☐
```

Это также важно для следующей главы про Assignment: стандартный Assign умеет использовать Share как вспомогательный механизм, если назначаемому User не хватает Read.

---

# Что произойдёт в лабораторной

Ты:

1. временно включишь `Only if Creator` у Training User;
2. сравнишь два North Requests с разными owners;
3. полностью вернёшь owner restriction в исходное состояние;
4. под Training Manager создашь `D21-Shared-South`;
5. убедишься, что Student User не видит его из-за Area = South;
6. расшаришь документ Student User только на Read;
7. увидишь Share как явное исключение User Permission;
8. временно добавишь Share Write;
9. изменишь обычное поле;
10. вернёшь Share в read-only состояние;
11. убедишься, что owner не изменился и Internal Cost не раскрылся.

---

# Что запомнить

1. `owner` — системный создатель Document.
2. `owner` не равен `Responsible`.
3. `Only if Creator` проверяет именно owner.
4. Share хранится как `DocShare` для конкретного Document.
5. Share всегда добавляет Read, а дополнительные права выдаются отдельно.
6. Нельзя штатно расшарить право, которого нет у самого sharer.
7. Shared Document может быть явным исключением owner/User Permission restrictions.
8. Share не отменяет Permission Level.
9. Share не меняет owner.
10. Sharing и Assignment — разные механизмы.

---

## Проверенные исходники v16.32.0

- [Permission engine](https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py)
- [Permission-aware query conditions](https://github.com/frappe/frappe/blob/v16.32.0/frappe/database/query.py)
- [Sharing backend](https://github.com/frappe/frappe/blob/v16.32.0/frappe/share.py)
- [Role Permissions Manager](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.py)

Теперь выполни [**лабораторную 21**](labs/21_OWNER_AND_SHARING_LAB.md).

После неё переходи к [**22. Границы штатных permissions**](22_PERMISSION_BOUNDARIES.md).
