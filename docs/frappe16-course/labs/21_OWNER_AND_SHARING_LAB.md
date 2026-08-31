# Лабораторная 21. Owner и Sharing

## Что уже должно быть готово

Лабораторная 20 завершена.

Есть:

```text
D18-User-Record
  owner = student.user@example.test
  Area  = North

D18-Manager-Record
  owner = student.manager@example.test
  Area  = North
```

Обычный User имеет:

```text
User Permission
Training Area = North
```

Менеджер такого ограничения не имеет.

`Training Manager` имеет `Share = ✓` на Request.

---

## Что сейчас получим

Временный owner-эксперимент будет полностью восстановлен.

На стенде останется новый Request:

```text
D21-Shared-South
  owner = student.manager@example.test
  Area = South
  Notes = Read-only shared example
  Internal Cost = 2100
```

Он будет расшарен:

```text
student.user@example.test
Read = ✓
Write = ☐
```

`Training User` финально снова будет иметь:

```text
Only if Creator = ☐
```

---

# Часть 1. Проверь исходный owner

Войди под `Administrator` или открой документы по очереди под тем User, который их создавал.

Проверь системный owner двух D18 Requests:

```text
D18-User-Record
→ student.user@example.test

D18-Manager-Record
→ student.manager@example.test
```

Не путай owner с полем:

```text
Responsible
```

В этой лабораторной значение `Responsible` вообще не участвует в owner-check.

---

# Часть 2. Временно включи Only if Creator

Работай под `Administrator`.

## 1. Открой Role Permissions Manager

Выбери:

```text
Document Type = Request
Role = Training User
Level = 0
```

У существующей row временно включи:

```text
Only if Creator = ✓
```

Остальные финальные права не меняй:

```text
Read   ✓
Create ✓
Write  ✓
Delete ☐
Share  ☐
```

---

## 2. Проверь обычного User

Полностью перезайди:

```text
student.user@example.test
```

В Request List отфильтруй:

```text
Subject Like D18-%
```

Ожидается:

```text
D18-User-Record
→ доступен

D18-Manager-Record
→ не доступен обычным путём
```

Оба имеют:

```text
Area = North
```

Значит разницу создал не User Permission, а именно owner condition.

---

## 3. Проверь прямое открытие

Открой свой:

```text
D18-User-Record
```

Ожидается:

```text
Read:  да
Write: да
```

Теперь попробуй открыть известный name:

```text
D18-Manager-Record
```

Ожидается permission denial.

---

## 4. Сравни менеджера

Войди:

```text
student.manager@example.test
```

У него есть дополнительная Role:

```text
Training Manager
```

с отдельной unrestricted Level 0 row.

Поэтому менеджер должен продолжать видеть оба D18 Requests.

Так мы на практике проверили сложение разрешений нескольких Roles.

---

# Восстанови owner restriction сразу

Вернись под `Administrator`.

У:

```text
Request
Training User
Level 0
```

верни:

```text
Only if Creator = ☐
```

Полностью перезайди обычным User и проверь:

```text
D18-User-Record
D18-Manager-Record
```

Оба снова доступны, потому что:

```text
Area = North
```

а owner restriction снят.

**Не продолжай к Sharing, пока это состояние не восстановлено.**

---

# Часть 3. Подготовь South Request для Share

Теперь работай именно под:

```text
student.manager@example.test
```

## 5. Создай Request

Создай:

```text
Subject:  D21-Shared-South
Status:   Open
Priority: Medium
Area:     South
Notes:    Before share
```

Сохрани.

Установи:

```text
Internal Cost = 2100
```

и снова сохрани.

Проверь:

```text
owner = student.manager@example.test
```

---

# Часть 4. Проверь отказ до Share

Выйди и войди:

```text
student.user@example.test
```

Поставь в Request List:

```text
Subject Like D21-%
```

Ожидается:

```text
0 Documents
```

Потому что:

```text
D21-Shared-South
Area = South
```

а User Permission разрешает только:

```text
North
```

Попробуй прямое открытие известного name этого Request.

Ожидается permission denial.

---

# Часть 5. Создай read-only Share

Снова войди:

```text
student.manager@example.test
```

Открой:

```text
D21-Shared-South
```

Используй штатное действие:

```text
Share
```

Добавь:

```text
User:  student.user@example.test
Read:  ✓
Write: ☐
```

Если интерфейс отдельно показывает дополнительные permissions, не включай их.

Сохрани Share.

Менеджер должен суметь это сделать без Administrator, потому что его `Training Manager` role имеет:

```text
Share = ✓
```

---

# Часть 6. Проверь Share как исключение

Полностью перезайди:

```text
student.user@example.test
```

Снова поставь:

```text
Subject Like D21-%
```

Теперь ожидается:

```text
1 Document
D21-Shared-South
```

Несмотря на:

```text
Area = South
```

он появился как явный shared Document.

---

## 6. Открой Shared Request

Ожидается:

```text
Read: да
```

Но обычное изменение существующего Request не должно быть разрешено только этим Share:

```text
Share Write = ☐
```

Убедись, что `Internal Cost` также не открылся обычному User.

Permission Level 1 продолжает действовать отдельно.

---

# Намеренная поломка — временно выдай Share Write

Вернись менеджером к Share этого документа.

Временно включи:

```text
Write = ✓
```

Сохрани.

---

## 7. Проверь под Training User

Полностью перезайди:

```text
student.user@example.test
```

Открой:

```text
D21-Shared-South
```

Измени обычное Level 0 поле:

```text
Notes = Changed through temporary Write Share
```

Сохрани.

Ожидается:

```text
Save успешен
```

South User Permission не дала обычный Write, но явный DocShare теперь содержит `Write`.

При этом:

```text
Internal Cost
```

по-прежнему не должен стать доступен: у Training User нет Request Level 1 rule.

---

# Восстановление Share

Войди менеджером.

## 8. Верни Notes

Установи:

```text
Notes = Read-only shared example
```

Сохрани.

---

## 9. Верни Share в read-only

В Share для:

```text
student.user@example.test
```

оставь:

```text
Read  ✓
Write ☐
```

Сохрани.

---

## 10. Проверь owner

На том же Request убедись:

```text
owner = student.manager@example.test
```

Share не должен был изменить owner.

---

# Часть 7. Посмотри серверную запись Share

Работай под `Administrator`.

## 11. Открой DocShare List

Перейди напрямую:

```text
http://learn.localhost:8000/app/docshare
```

`DocShare` — системный DocType Frappe, в котором хранится document sharing.

Отфильтруй список:

```text
Document Type = Request
Document Name = <system name D21-Shared-South>
User          = student.user@example.test
```

Ожидается Share-запись для документа, который мы только что оставили в read-only состоянии.

Открой её и сопоставь поля:

```text
User          = student.user@example.test
Document Type = Request
Document Name = <system name D21-Shared-South>
Read          = 1
Write         = 0
```

Ничего в `DocShare` вручную не редактируй. Состоянием Share управляй штатным Share dialog исходного `Request`.

---

## Проверка себя

1. Кто owner `D18-User-Record`?
2. Почему при `Only if Creator = ✓` пропал `D18-Manager-Record`, хотя он North?
3. Почему после восстановления owner restriction он вернулся?
4. Чем Share отличается от User Permission?
5. Почему `D21-Shared-South` появился у North-only User после Share?
6. Почему read-only Share не дал обычный Write?
7. Почему временный Share Write разрешил изменить Notes?
8. Почему Internal Cost при этом не открылся?
9. Изменился ли owner после Share?
10. Чем Sharing будет отличаться от Assignment следующей главы?

---

## Состояние стенда после лабораторной

`Training User` Request Level 0 восстановлен:

```text
Read   ✓
Create ✓
Write  ✓
Delete ☐
Share  ☐
Only if Creator ☐
```

User Permission остаётся:

```text
student.user@example.test
→ Training Area = North
```

Существует:

```text
D21-Shared-South
  owner:         student.manager@example.test
  Area:          South
  Notes:         Read-only shared example
  Internal Cost: 2100
```

Для него существует Share:

```text
student.user@example.test
  Read:  ✓
  Write: ☐
```

Глобально:

```text
Disable Document Sharing = ☐
```

Это точное входное состояние [**главы 22**](../22_PERMISSION_BOUNDARIES.md).
