# 18. Role Permissions Manager

В главе 17 мы создали:

```text
Training User
Training Manager
```

и двух реальных System Users.

Они уже могут войти в Desk, но Role пока не отвечает на вопрос:

> что именно пользователь может делать с `Request`?

Для этого во Frappe есть **Role Permissions Manager**.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

```text
student.user@example.test
└── Training User

student.manager@example.test
├── Training User
└── Training Manager
```

Оба — `System User`.

Для `Request` ещё нет учебных permission rules этих ролей.

---

# Главная модель

```text
User
  ↓ имеет
Role
  ↓ получает правило на
DocType
  ↓ разрешённые действия
```

Например:

```text
Training User
→ Request
→ Read + Create + Write
```

А менеджер дополнительно:

```text
Training Manager
→ Request
→ Delete + Share
```

Так одна Role применяется ко всем Users, которым она назначена.

---

# Где находится Role Permissions Manager

В Desk найди:

```text
Role Permissions Manager
```

Его route в текущем Desk:

```text
/app/permission-manager
```

Страница штатно предназначена для `System Manager`.

В лаборатории настройку выполняет `Administrator`, а результат проверяется под обычными учебными Users.

---

# Permission rule

Одна строка связывает:

```text
Document Type
Role
Permission Level
```

Для базового доступа к документу используется:

```text
Permission Level = 0
```

Например:

```text
Request
Training User
Level 0
```

и на этой строке включаются нужные права.

---

# Основные права этой лабораторной

## Read

Разрешает читать доступный Document.

```text
Read = ✓
```

не означает Write.

---

## Create

Разрешает создать новый Document.

```text
Create = ✓
```

не означает Delete.

---

## Write

Разрешает изменять существующий доступный Document.

Для обычного оператора курса получаем:

```text
Read   ✓
Create ✓
Write  ✓
```

---

## Delete

Отдельное право удаления.

В нашем сценарии:

```text
Training User
Delete = ☐

Training Manager
Delete = ✓
```

Так ученик руками увидит разницу между редактированием и удалением.

---

## Share

Разрешает штатно делиться конкретным Document с другим User.

Пока просто оставим:

```text
Training User
Share = ☐

Training Manager
Share = ✓
```

Сам механизм Sharing подробно проверим в главе 21.

---

# Select и Read

`Select` — более узкое permission для выбора Document в Link-поиске.

В текущем permission engine `v16.32.0`:

```text
Read
→ может удовлетворить проверку Select
```

Но обратное неверно:

```text
Select
≠ полноценный Read
```

В нашей матрице отдельный `Select` не нужен: обе роли получают обычный `Read` на `Request`.

---

# Остальные permissions

Role Permissions Manager показывает и другие права:

```text
Print
Email
Report
Import
Export
Mask
```

Для Submittable DocType также имеют смысл:

```text
Submit
Cancel
Amend
```

`Request` в текущем курсе не Submittable, поэтому Submit/Cancel/Amend здесь не являются нашей задачей.

Главное правило лабораторной:

> не ставить все галочки «на всякий случай».

Мы оставим только реально нужные действия.

---

## Почему отдельно проверяем Export

Metadata `Custom DocPerm` в `v16.32.0` содержит собственные значения по умолчанию для permission fields.

Поэтому после добавления новой строки нельзя полагаться на мысль:

> я включил три галочки — значит остальные точно выключены.

Нужно глазами проверить **всю строку**.

В лабораторной `Export`, `Import`, `Print`, `Email`, `Report` и другие ненужные права явно оставляем выключенными.

---

# Несколько ролей складываются

Менеджер имеет:

```text
Training User
Training Manager
```

Permission engine собирает разрешения всех подходящих Roles.

Поэтому менеджеру не нужно отнимать базовые возможности `Training User`.

Можно мыслить так:

```text
Training User
→ Read + Create + Write

Training Manager
→ Read + Create + Write + Delete + Share
```

Итог менеджера — более широкий набор разрешённых действий.

Пустая галочка в одной Role не является отдельным запретом, который отменяет разрешение другой Role.

---

# Administrator — специальный случай

В `frappe.permissions.has_permission()` для:

```text
Administrator
```

есть прямой shortcut:

```text
return True
```

Поэтому все важные проверки этой главы выполняем под:

```text
student.user@example.test
student.manager@example.test
```

---

# Где сохраняются изменения Role Permissions Manager

Это особенно важно после главы 15.

Наш `Request` — Standard DocType собственного App.

Его каноническая metadata лежит в:

```text
apps/training/training/training/doctype/request/request.json
```

Но Role Permissions Manager для runtime-настройки использует:

```text
Custom DocPerm
```

Если custom permissions для DocType ещё не созданы, Framework сначала копирует стандартные `DocPerm`, а затем изменяет site-level `Custom DocPerm`.

То есть:

```text
Request JSON
→ стандартная metadata App

Role Permissions Manager
→ site-level Custom DocPerm
```

В лабораторной мы проверим SHA-256 `request.json` до и после настройки.

Он не должен измениться.

---

# Only if Creator пока не включаем

На Level 0 есть ещё флаг:

```text
Only if Creator
```

В metadata он называется:

```text
if_owner
```

Он ограничивает permission rule документами, где текущий User является системным `owner`.

В этой главе оставляем:

```text
Only if Creator = ☐
```

Подробный owner-эксперимент будет в главе 21, когда у нас уже появятся стабильные Documents разных владельцев.

Важно: на первом проходе курса не строим фиктивную схему с двумя одинаковыми строками одной Role и одного Level. В текущем UI `Only if Creator` — свойство конкретной permission row.

---

# Почему нужен фиксированный набор документов

Если тестировать Delete на случайном старом Request, результат может зависеть от данных предыдущих глав.

Поэтому лабораторная создаст точно два постоянных документа:

```text
D18-User-Record
D18-Manager-Record
```

И один временный delete-probe, который в конце удаляется.

У этих документов будет известный `owner`, что пригодится в главе 21.

---

# Что произойдёт в лабораторной

Ты:

1. снимешь SHA-256 `request.json`;
2. создашь точные Level 0 rules для `Training User` и `Training Manager`;
3. явно выключишь ненужные permissions;
4. проверишь, что `request.json` не изменился;
5. под Training User создашь `D18-User-Record`;
6. под Training Manager создашь `D18-Manager-Record`;
7. проверишь разницу Delete;
8. временно снимешь `Write` у Training User;
9. увидишь read-only поведение;
10. восстановишь точную permission matrix.

---

# Что запомнить

1. Role сама по себе не даёт доступ к DocType.
2. Level 0 — базовые document permissions.
3. Read, Create, Write и Delete — разные права.
4. Share — отдельное право.
5. Несколько Roles пользователя складывают разрешения.
6. Administrator не подходит для проверки обычной permission model.
7. Role Permissions Manager в этом сценарии пишет `Custom DocPerm`, а не `request.json`.
8. После добавления rule нужно проверить всю строку, а не только поставленные вручную галочки.

---

## Проверенные исходники v16.32.0

- [Role Permissions Manager backend](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.py)
- [Role Permissions Manager UI](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.js)
- [Custom DocPerm metadata](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json)
- [Permission engine](https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py)

Теперь выполни [**лабораторную 18**](labs/18_ROLE_PERMISSION_MANAGER_LAB.md).

После неё переходи к [**19. Permission Level**](19_PERMISSION_LEVEL.md).
