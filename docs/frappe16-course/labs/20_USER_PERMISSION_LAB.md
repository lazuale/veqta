# Лабораторная 20. User Permission

## Что уже должно быть готово

Лабораторная 19 завершена.

Есть:

```text
Training User
Training Manager
student.user@example.test
student.manager@example.test
```

`Request` уже имеет field-level защиту:

```text
Internal Cost
Perm Level = 1
```

Также существуют:

```text
6 C12 Requests
D18-User-Record
D18-Manager-Record
```

---

## Что сейчас получим

Оставим на стенде Standard DocType:

```text
Training Area
├── North
└── South
```

В `Request` останется:

```text
Area
fieldname: area
Link → Training Area
Ignore User Permissions = ☐
```

User Permission:

```text
User:      student.user@example.test
Allow:     Training Area
For Value: North
Is Default: ✓
Apply To All Document Types: ✓
```

Training Manager такого User Permission не имеет.

---

# Часть 1. Создай `Training Area`

Работай под `Administrator`.

## 1. Создай Standard DocType

В Desk:

```text
DocType
→ New
```

Создай:

```text
Name:       Training Area
Module:     Training
Custom:     ☐
```

Добавь поле:

```text
Label:      Area Name
Fieldname:  area_name
Field Type: Data
Mandatory:  ✓
```

Настрой:

```text
Title Field: area_name
Auto Name:   field:area_name
```

Сохрани DocType.

---

## 2. Создай два Documents

Создай:

```text
North
South
```

Проверь, что их системные names именно:

```text
North
South
```

---

# Часть 2. Дай учебным ролям Read на справочник

Открой:

```text
Role Permissions Manager
Document Type = Training Area
```

Создай Level 0 rule для:

```text
Training User
```

оставив только:

```text
Read = ✓
```

Все остальные ненужные permissions выключи.

Создай такую же read-only row для:

```text
Training Manager
```

Итог:

```text
Training User    → Training Area: Read
Training Manager → Training Area: Read
```

Создавать или удалять Areas учебные Users в этом сценарии не должны.

---

# Часть 3. Добавь Area в Request

## 3. Открой `DocType → Request`

Добавь Standard field:

```text
Label:      Area
Fieldname:  area
Field Type: Link
Options:    Training Area
```

Размести его в `Main → General` сразу после:

```text
Due Date
```

Убедись:

```text
Ignore User Permissions = ☐
```

Сохрани DocType.

---

# Часть 4. Заполни фиксированные данные

Мы будем считать только документы с заранее известными Subjects.

## 4. Назначь North

Установи:

```text
C12-Open-High-1     → North
C12-Open-Medium     → North
C12-Progress-High   → North
D18-User-Record     → North
D18-Manager-Record  → North
```

---

## 5. Назначь South

Установи:

```text
C12-Open-High-2   → South
C12-Progress-Low  → South
C12-Done-High     → South
```

Все перечисленные Documents сохрани.

Теперь у каждого C12 Request, участвующего в подсчёте, `Area` заполнена явно.

---

# Часть 5. Создай User Permission

## 6. Открой `User Permission`

Создай:

```text
User:      student.user@example.test
Allow:     Training Area
For Value: North
```

Выставь:

```text
Is Default:                  ✓
Apply To All Document Types: ✓
```

Сохрани.

У `student.manager@example.test` такую User Permission **не создавай**.

---

# Часть 6. Проверь обычного User

Полностью перезайди:

```text
student.user@example.test
FrappeCourse!2026
```

Открой `Request` List View.

## 7. Отфильтруй только C12

Поставь:

```text
Subject Like C12-%
```

Ожидается ровно:

```text
3 Documents
```

Это:

```text
C12-Open-High-1
C12-Open-Medium
C12-Progress-High
```

Все они:

```text
Area = North
```

South C12 Documents в обычной permission-aware выборке появиться не должны.

---

## 8. Проверь прямое открытие South

Под `Administrator` или менеджером заранее скопируй системный `name` документа с Subject:

```text
C12-Open-High-2
```

Он имеет:

```text
Area = South
```

Попробуй открыть именно этот Document под:

```text
student.user@example.test
```

Ожидается permission denial.

То есть ограничение работает не только как визуальный List filter.

---

## 9. Создай новый Request и проверь default

Нажми:

```text
New Request
```

Посмотри поле:

```text
Area
```

Ожидаемый default:

```text
North
```

Проверь Link-подбор: обычный User не должен получать нормальный выбор `South` как разрешённого Training Area.

Сам тестовый Request сохранять не обязательно. Закрой его без сохранения.

---

# Часть 7. Сравни менеджера

Полностью перезайди:

```text
student.manager@example.test
```

В `Request` List View поставь:

```text
Subject Like C12-%
```

Ожидается:

```text
6 Documents
```

Менеджер не имеет User Permission по `Training Area`, поэтому видит и North, и South C12 Requests.

В новом Request Link `Area` должен позволять выбрать:

```text
North
South
```

---

# Намеренная поломка — Ignore User Permissions

Возвращаемся под `Administrator`.

## 10. Временно выключи связь Area с User Permission

Открой:

```text
DocType → Request
→ Area
```

включи:

```text
Ignore User Permissions = ✓
```

Сохрани DocType.

---

## 11. Проверь Student User снова

Полностью перезайди:

```text
student.user@example.test
```

В List View поставь:

```text
Subject Like C12-%
```

Ожидается теперь:

```text
6 Documents
```

Почему?

Мы сказали permission engine:

```text
не применять User Permission через Request.area
```

Попробуй снова открыть South Request:

```text
C12-Open-High-2
```

Теперь Area не должна отсеивать этот Request.

Это не сделало User администратором: базовые Role Permissions и Permission Level продолжают действовать.

В частности `Internal Cost` обычному User по-прежнему не должен стать доступен.

---

# Восстановление

## 12. Верни поле Area

Под `Administrator` установи:

```text
Request.area
Ignore User Permissions = ☐
```

Сохрани.

Полностью перезайди обычным User.

Снова:

```text
Subject Like C12-%
→ 3 Documents
```

И прямое открытие:

```text
C12-Open-High-2
→ permission denial
```

---

## Не меняй strict mode ради этой лабораторной

Мы сознательно **не переключаем** глобальную настройку:

```text
Apply Strict User Permissions
```

Потому что это изменило бы поведение всего Site.

Все точные подсчёты сделаны на C12-наборе, где `Area` заполнена у каждой записи.

---

## Проверка себя

1. Даёт ли User Permission сама по себе Read на Request?
2. Почему Training User видит 3 C12, а Training Manager 6?
3. Почему South Request не открывался напрямую?
4. Что делает `Is Default`?
5. Что означает `Apply To All Document Types`?
6. Что произошло после `Ignore User Permissions = ✓` у `Request.area`?
7. Отключило ли это все Role Permissions?
8. Почему мы не используем случайные Requests с пустой Area для точного подсчёта?

---

## Состояние стенда после лабораторной

Standard DocType:

```text
Training Area
  Module: Training
  Auto Name: field:area_name
  Title Field: area_name

Area Name
  area_name
  Data
  Mandatory
```

Documents:

```text
North
South
```

Role permissions `Training Area`:

```text
Training User    → Read
Training Manager → Read
```

В Standard `Request`:

```text
Area
  area
  Link → Training Area
  Ignore User Permissions: ☐
```

C12 mapping:

```text
North:
  C12-Open-High-1
  C12-Open-Medium
  C12-Progress-High

South:
  C12-Open-High-2
  C12-Progress-Low
  C12-Done-High
```

D18 mapping:

```text
D18-User-Record    → North
D18-Manager-Record → North
```

User Permission:

```text
student.user@example.test
  Allow: Training Area
  For Value: North
  Is Default: ✓
  Apply To All Document Types: ✓
```

`student.manager@example.test` не имеет User Permission `Training Area`.

Это точное входное состояние [**главы 21**](../21_OWNER_AND_SHARING.md).
