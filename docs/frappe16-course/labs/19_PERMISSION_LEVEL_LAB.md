# Лабораторная 19. Permission Level

## Что уже должно быть готово

Лабораторная 18 завершена.

Есть два постоянных Request:

```text
D18-User-Record
  owner = student.user@example.test

D18-Manager-Record
  owner = student.manager@example.test
```

`Training User` и `Training Manager` имеют рабочие Level 0 permissions на `Request`.

---

## Что сейчас получим

В Standard metadata `Request` останется поле:

```text
Internal Cost
fieldname: internal_cost
Field Type: Currency
Perm Level: 1
```

Финальный доступ:

```text
Training User
→ Level 1 rule отсутствует
→ Internal Cost не доступен

Training Manager
→ Level 1 Read + Write
→ Internal Cost виден и редактируется
```

В `D18-Manager-Record` итоговое значение:

```text
Internal Cost = 1250
```

---

# Часть 1. Добавь поле в Standard DocType

Работай под `Administrator`.

## 1. Открой `DocType → Request`

Добавь поле:

```text
Label:      Internal Cost
Fieldname:  internal_cost
Field Type: Currency
Perm Level: 1
```

Размести его в `Details` после поля:

```text
Notes
```

Не включай:

```text
Hidden
Read Only
```

Нам нужен чистый опыт Permission Level без дополнительных UI-ограничений.

Сохрани DocType.

---

## 2. Проверь metadata-файл

В терминале:

```bash
cd ~/frappe/frappe16-course-bench

grep -n 'internal_cost' \
  apps/training/training/training/doctype/request/request.json
```

Ожидается строка с новым fieldname.

При желании посмотри diff собственного App:

```bash
cd ~/frappe/frappe16-course-bench/apps/training

git diff -- training/training/doctype/request/request.json
```

На этот раз изменение **должно** существовать: мы меняли Standard metadata собственного DocType.

---

# Часть 2. Дай Level 1 менеджеру

## 3. Открой Role Permissions Manager

Выбери:

```text
Document Type = Request
```

Добавь новую rule:

```text
Role:             Training Manager
Permission Level: 1
```

Для неё выставь:

```text
Read  ✓
Write ✓
Mask  ☐
```

На Level 1 других document-level permissions в UI быть не должно.

---

## 4. Training User Level 1 пока не создавай

Итог до эксперимента:

```text
Training User
Level 1: нет rule

Training Manager
Level 1: Read + Write
```

---

# Часть 3. Запиши внутреннюю стоимость как менеджер

Полностью войди:

```text
student.manager@example.test
FrappeCourse!2026
```

Открой Request с Subject:

```text
D18-Manager-Record
```

Поле должно быть видно:

```text
Internal Cost
```

Запиши:

```text
1250
```

Сохрани.

Ожидается:

```text
значение сохраняется
```

---

# Часть 4. Сравни обычного User

Перезайди:

```text
student.user@example.test
```

Открой **тот же**:

```text
D18-Manager-Record
```

Ожидается:

```text
Request открывается
обычные Level 0 поля доступны по текущим rights
Internal Cost не получает обычного доступа
```

Для этой проверки достаточно сравнить одну и ту же Form View под двумя реальными Users.

---

# Часть 5. Временно дай только Read

Вернись под `Administrator`.

## 5. Добавь Training User Level 1

В Role Permissions Manager создай:

```text
Role:             Training User
Permission Level: 1
```

Выставь:

```text
Read  ✓
Write ☐
Mask  ☐
```

---

## 6. Проверь под Training User

Полностью перезайди обычным User и снова открой:

```text
D18-Manager-Record
```

Теперь ожидается:

```text
Internal Cost виден
значение = 1250
поле read-only
```

Попытка обычного редактирования поля не должна быть доступна.

Так мы получили три разных уровня:

```text
Level 0 Write на Request
+
Level 1 только Read
→ обычные поля редактируются,
  Internal Cost только читается
```

---

# Намеренная ошибка — выдай лишний Write

Под `Administrator` в той же Level 1 row `Training User` временно включи:

```text
Write = ✓
```

Перезайди:

```text
student.user@example.test
```

Открой:

```text
D18-Manager-Record
```

Измени:

```text
Internal Cost: 9999
```

Сохрани.

Ожидается:

```text
изменение разрешено
```

Это **не баг Framework**.

Мы сами выдали обычному User лишний field-level permission.

Именно поэтому Permission Level — часть реальной security model, а не декоративная галочка формы.

---

# Восстановление

## 7. Верни каноническое значение

Войди менеджером и верни:

```text
Internal Cost = 1250
```

Сохрани.

---

## 8. Удали Training User Level 1 rule полностью

Под `Administrator` открой Role Permissions Manager и удали строку:

```text
Request
Training User
Level 1
```

Не оставляй её с пустыми галочками.

Финально должно быть:

```text
Training User
Level 0: Read + Create + Write
Level 1: отсутствует

Training Manager
Level 0: Read + Create + Write + Delete + Share
Level 1: Read + Write
```

---

## 9. Финальная проверка

Под `student.user@example.test`:

```text
D18-Manager-Record
→ открывается
→ Internal Cost не доступен
```

Под `student.manager@example.test`:

```text
D18-Manager-Record
→ открывается
→ Internal Cost виден
→ значение = 1250
→ можно редактировать
```

---

## Проверка себя

1. Что означает `Perm Level = 0`?
2. Зачем существует Level 1+?
3. Какие permission types показывает Role Permissions Manager для Level 1?
4. Почему Training User сначала не видел Internal Cost?
5. Почему после временного `Read` увидел его только для чтения?
6. Почему после временного `Write` смог изменить значение?
7. Чем `Hidden` отличается от Permission Level?
8. Почему в этой лабораторной `request.json` должен измениться, а в лабораторной 18 — нет?

---

## Состояние стенда после лабораторной

В Standard `Request` постоянно существует:

```text
Internal Cost
  internal_cost
  Currency
  Perm Level: 1
```

Permission rules:

```text
Training User
  Request Level 0: Read + Create + Write
  Request Level 1: нет

Training Manager
  Request Level 0: Read + Create + Write + Delete + Share
  Request Level 1: Read + Write
```

`D18-Manager-Record`:

```text
Internal Cost = 1250
```

Временная Training User Level 1 row удалена.

Это точное входное состояние [**главы 20**](../20_USER_PERMISSION.md).
