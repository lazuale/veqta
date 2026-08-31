# Лабораторная 18. Role Permissions Manager

## Что уже должно быть готово

Лабораторная 17 завершена.

Есть:

```text
Training User
Training Manager
student.user@example.test
student.manager@example.test
```

Оба User — `System User` и умеют входить в `/app`.

Permission rules для `Request` этих ролей ещё не настроены.

---

## Что сейчас получим

Итоговая матрица `Request`, Level 0:

```text
Training User
  Read:    ✓
  Create:  ✓
  Write:   ✓
  Delete:  ☐
  Share:   ☐
  Only if Creator: ☐

Training Manager
  Read:    ✓
  Create:  ✓
  Write:   ✓
  Delete:  ✓
  Share:   ✓
  Only if Creator: ☐
```

Для обеих строк остальные ненужные permissions оставляем выключенными:

```text
Select
Print
Email
Report
Import
Export
Mask
```

Создадим два постоянных Requests:

```text
D18-User-Record
D18-Manager-Record
```

---

# Часть 1. Зафиксируй Standard metadata

Под `Administrator` открой терминал Bench:

```bash
cd ~/frappe/frappe16-course-bench
```

Выполни:

```bash
REQ_JSON="apps/training/training/training/doctype/request/request.json"
sha256sum "$REQ_JSON"
```

Скопируй полученный hash в заметки как:

```text
BEFORE_RPM = ...
```

Мы не пытаемся запомнить конкретный hash курса: он зависит от предыдущих metadata-изменений.

Нужно сравнить **этот же файл до и после** текущей лабораторной.

---

# Часть 2. Настрой `Training User`

## 1. Открой Role Permissions Manager

В Desk:

```text
поиск → Role Permissions Manager
```

Выбери:

```text
Document Type = Request
```

---

## 2. Добавь правило `Training User`

Нажми:

```text
Add A New Rule
```

Укажи:

```text
Document Type:   Request
Role:            Training User
Permission Level: 0
```

После появления строки выставь **точно**:

```text
Read    ✓
Write   ✓
Create  ✓
Delete  ☐
Share   ☐

Only if Creator ☐
```

И явно проверь, что выключены:

```text
Select  ☐
Print   ☐
Email   ☐
Report  ☐
Import  ☐
Export  ☐
Mask    ☐
```

Если какая-то ненужная галочка уже включена после создания строки — выключи её.

---

# Часть 3. Настрой `Training Manager`

## 3. Добавь Level 0 rule

Создай:

```text
Document Type:   Request
Role:            Training Manager
Permission Level: 0
```

Выставь:

```text
Read    ✓
Write   ✓
Create  ✓
Delete  ✓
Share   ✓

Only if Creator ☐
```

Оставь выключенными:

```text
Select  ☐
Print   ☐
Email   ☐
Report  ☐
Import  ☐
Export  ☐
Mask    ☐
```

`Request` не Submittable, поэтому Submit/Cancel/Amend здесь не являются частью проверки.

---

# Часть 4. Убедись, что `request.json` не изменился

Снова выполни:

```bash
cd ~/frappe/frappe16-course-bench
REQ_JSON="apps/training/training/training/doctype/request/request.json"
sha256sum "$REQ_JSON"
```

Сравни с:

```text
BEFORE_RPM
```

Ожидается:

```text
hash одинаковый
```

То есть текущая настройка permissions живёт на Site как `Custom DocPerm`, а Standard metadata `Request` в App от неё не переписалась.

---

# Часть 5. Проверь Training User

Полностью выйди из Administrator и войди:

```text
student.user@example.test
FrappeCourse!2026
```

Открой:

```text
Request
```

Теперь List View должен быть доступен.

---

## 4. Создай постоянный Request

Создай:

```text
Subject:  D18-User-Record
Status:   Open
Priority: Medium
Notes:    Created by Training User
```

Сохрани.

Убедись, что документ получил обычный `REQ-...` name.

Главное для следующих глав:

```text
subject = D18-User-Record
owner   = student.user@example.test
```

---

## 5. Проверь Write

Измени:

```text
Notes: Edited by Training User
```

Сохрани.

Ожидается:

```text
Save успешен
```

---

## 6. Создай delete-probe

Создай ещё один Request:

```text
Subject:  D18-User-Delete-Probe
Status:   Open
Priority: Low
```

Сохрани.

Попробуй удалить его штатным действием формы/меню.

Ожидается одно из нормальных проявлений permission boundary:

```text
Delete action отсутствует
```

или:

```text
Framework отказывает в Delete
```

Документ должен остаться существовать.

Не пытайся обходить UI через будущий API или прямую БД.

---

# Часть 6. Проверь Training Manager

Выйди и войди:

```text
student.manager@example.test
FrappeCourse!2026
```

---

## 7. Создай постоянный Request менеджера

Создай:

```text
Subject:  D18-Manager-Record
Status:   Open
Priority: Medium
Notes:    Created by Training Manager
```

Сохрани.

Теперь:

```text
subject = D18-Manager-Record
owner   = student.manager@example.test
```

---

## 8. Проверь Delete менеджера

Найди:

```text
D18-User-Delete-Probe
```

Удалить его должен суметь `student.manager@example.test`, потому что у него есть Role `Training Manager` с:

```text
Delete = ✓
```

Удали probe.

После этого должны остаться только два постоянных D18-документа:

```text
D18-User-Record
D18-Manager-Record
```

---

# Намеренная поломка — убери Write

Вернись под `Administrator`.

## 9. Сними Write у `Training User`

В Role Permissions Manager:

```text
Document Type = Request
Role = Training User
```

временно установи:

```text
Write = ☐
```

Остальное не меняй.

---

## 10. Проверь под обычным User

Полностью перезайди:

```text
student.user@example.test
```

Открой:

```text
D18-User-Record
```

Ожидается:

```text
Read работает
```

но обычное сохранение изменений существующего документа недоступно или получает permission отказ.

`Create` при этом остаётся отдельным permission и не должен считаться автоматически выключенным только из-за снятого `Write`.

---

# Восстановление

Под `Administrator` верни:

```text
Training User
Write = ✓
```

Проверь всю строку, а не только эту одну галочку.

Финально должно быть:

```text
Training User
Read    ✓
Write   ✓
Create  ✓
Delete  ☐
Share   ☐
Only if Creator ☐

Training Manager
Read    ✓
Write   ✓
Create  ✓
Delete  ✓
Share   ✓
Only if Creator ☐
```

Ненужные permissions обеих строк выключены.

---

## Проверка себя

1. Почему Role сама по себе не давала доступ к Request?
2. Чем `Write` отличается от `Create`?
3. Почему Training User не смог удалить probe?
4. Почему Training Manager смог удалить тот же Document?
5. Почему менеджер сохраняет базовые права Training User?
6. Почему `Administrator` не используется как доказательство работы permission model?
7. Изменился ли `request.json` после Role Permissions Manager?
8. Где живут runtime-правила, созданные этой страницей?

---

## Состояние стенда после лабораторной

Users и Roles из главы 17 сохранены.

`Request`, Level 0:

```text
Training User
  Read:    ✓
  Write:   ✓
  Create:  ✓
  Delete:  ☐
  Share:   ☐
  Only if Creator: ☐

Training Manager
  Read:    ✓
  Write:   ✓
  Create:  ✓
  Delete:  ✓
  Share:   ✓
  Only if Creator: ☐
```

На Site остаются:

```text
D18-User-Record
  owner = student.user@example.test

D18-Manager-Record
  owner = student.manager@example.test
```

`D18-User-Delete-Probe` удалён.

Standard file:

```text
apps/training/training/training/doctype/request/request.json
```

не изменился из-за Role Permissions Manager.

Это точное входное состояние [**главы 19**](../19_PERMISSION_LEVEL.md).
