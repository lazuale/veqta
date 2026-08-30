# 20. User Permission

В прошлых главах мы настроили два уровня доступа:

```text
Role Permission
→ что пользователь может делать с DocType

Permission Level
→ какие поля внутри документа он может видеть и менять
```

Теперь нужен третий вопрос:

> какие именно записи этого DocType пользователь может видеть?

Например, два сотрудника имеют одну и ту же роль `Request Operator`.

Оба умеют читать и редактировать `Request`, но:

```text
Анна  → должна работать только с Department A
Борис → только с Department B
```

Создавать отдельный DocType или отдельную роль для каждого отдела не нужно.

Для таких ограничений во Frappe есть **User Permission**.

Проверено: **2026-08-31**.

---

## 1. Сначала простая картинка

Есть DocType:

```text
Request
```

У него есть поле:

```text
department
Field Type = Link
Options = Department
```

Есть документы:

```text
REQ-001 → Department A
REQ-002 → Department B
REQ-003 → Department A
REQ-004 → Department C
```

У Анны есть роль:

```text
Request Operator
├── Read
├── Create
└── Write
```

Без дополнительных ограничений эта роль позволяет ей работать со всеми доступными `Request`.

Теперь создаём User Permission:

```text
User      = anna@example.com
Allow     = Department
For Value = Department A
```

После применения ограничения картина становится такой:

```text
REQ-001 → Department A → доступен
REQ-002 → Department B → не доступен
REQ-003 → Department A → доступен
REQ-004 → Department C → не доступен
```

То есть User Permission не отвечает на вопрос **«можно ли читать Request?»**.

На него уже ответила Role Permission.

User Permission отвечает:

> какие `Request` из разрешённого DocType подходят этому конкретному пользователю?

---

## 2. Role Permission и User Permission работают вместе

Это одна из самых важных вещей всей permission model Frappe.

Не так:

```text
User Permission
→ даёт доступ к Request
```

А так:

```text
Role Permission
→ разрешает Read на Request

User Permission
→ сужает набор Request
```

Пример:

```text
Анна
│
├── Role: Request Operator
│   └── Request: Read + Create + Write
│
└── User Permission
    └── Department = Department A
```

Результат:

```text
может работать с Request
        ↓
но только с теми,
которые проходят User Permission
```

Если у роли вообще нет `Read` на `Request`, User Permission не выдаст его сама.

---

## 3. User Permission обычно работает через Link

User Permission особенно полезна, когда документы связаны со справочниками через `Link`.

Например:

```text
Request
├── department → Link → Department
├── project    → Link → Project
└── region     → Link → Region
```

Тогда можно ограничивать пользователя разрешёнными значениями:

```text
Department A
Project Alpha
Region North
```

Frappe учитывает эти связи при формировании доступных документов.

Поэтому User Permission — это не универсальный конструктор произвольных условий вроде:

```text
status = "Open"
due_date < today
amount > 100000
```

Для таких бизнес-условий нужны другие механизмы.

User Permission в первую очередь построена вокруг **разрешённых связанных документов**.

---

## 4. Поля User Permission

В `User Permission` v16 основные поля такие:

```text
User
Allow
For Value
Is Default
Apply To All Document Types
Applicable For
Hide Descendants
```

Разберём каждое на одном примере.

---

# Часть 1. User, Allow и For Value

## 5. User

`User` — кому назначается ограничение.

Например:

```text
User = anna@example.com
```

То есть правило относится не к Role, а к конкретному User.

Именно поэтому механизм называется **User Permission**.

Если десяти пользователям нужен одинаковый базовый набор действий, это задача Roles.

Если каждому из них разрешены разные подразделения, проекты или регионы — здесь уже полезны User Permissions.

---

## 6. Allow

`Allow` отвечает на вопрос:

> документы какого DocType мы разрешаем этому пользователю?

Например:

```text
Allow = Department
```

Это ещё не конкретный отдел.

Мы только сказали, что правило относится к значениям DocType `Department`.

---

## 7. For Value

`For Value` — конкретный разрешённый документ из `Allow`.

Например:

```text
Allow     = Department
For Value = Department A
```

Поле `For Value` является `Dynamic Link`.

Поэтому его целевой DocType определяется значением `Allow`.

Простая схема:

```text
Allow = Department
        ↓
For Value показывает Department
        ↓
выбираем Department A
```

Если изменить:

```text
Allow = Project
```

то `For Value` уже будет выбирать документ `Project`.

---

## 8. Можно разрешить несколько значений

Допустим, Анне нужны сразу два отдела:

```text
Department A
Department B
```

Создаём две User Permission:

```text
1.
User      = anna@example.com
Allow     = Department
For Value = Department A

2.
User      = anna@example.com
Allow     = Department
For Value = Department B
```

Теперь для Department разрешён набор:

```text
{Department A, Department B}
```

То есть несколько записей одного `Allow` работают как список разрешённых значений.

---

# Часть 2. Как ограничивается Request

## 9. Откуда Frappe понимает связь

Вернёмся к `Request`:

```text
Request.department
Field Type = Link
Options    = Department
```

У Анны разрешено:

```text
Department A
```

Frappe видит, что `Request` содержит Link на `Department`, и может учитывать User Permission при выборке документов.

Упрощённо:

```text
User Permission
Department = Department A
        ↓
Request.department
        ↓
показывать подходящие Request
```

Это отражается не только на форме.

Permission-aware механизмы Frappe используют User Permissions и при получении списков документов.

Поэтому это намного надёжнее, чем просто спрятать строки JavaScript-кодом в интерфейсе.

---

## 10. User Permission влияет и на Link-подбор

Допустим, Анна создаёт новый `Request`.

Поле:

```text
department
```

должно предлагать ей значения, разрешённые permission model.

Если ей разрешены:

```text
Department A
Department B
```

обычный Link должен учитывать эти ограничения.

Так permission model помогает не только скрывать чужие документы, но и не давать пользователю случайно выбирать запрещённые связанные значения.

---

# Часть 3. Apply To All Document Types

## 11. Что значит Apply To All Document Types

По умолчанию User Permission имеет:

```text
Apply To All Document Types = 1
```

Название может сначала запутать.

Оно не означает:

> запретить вообще все DocType системы.

Смысл такой:

> применять эту User Permission ко всем подходящим связанным DocType, где она участвует в permission checking.

Например, `Department` может использоваться в нескольких документах:

```text
Request.department
Meeting.department
Budget.department
```

Если ограничение Department применяется ко всем связанным DocType, оно может влиять на каждый из этих сценариев.

---

## 12. Когда это удобно

Например пользователь действительно относится только к:

```text
Department A
```

и во всей системе должен работать только с данными этого отдела.

Тогда логично оставить:

```text
Apply To All Document Types = 1
```

Это единое ограничение на разрешённое значение Department.

---

# Часть 4. Applicable For

## 13. Иногда ограничение нужно только в одном месте

Представим:

```text
Department A
```

должен ограничивать Анну только при работе с `Request`.

Но в другом DocType она должна иметь более широкий доступ.

Тогда снимаем:

```text
Apply To All Document Types
```

и задаём:

```text
Applicable For = Request
```

Получается:

```text
User      = anna@example.com
Allow     = Department
For Value = Department A
Applicable For = Request
```

Теперь эта конкретная User Permission применяется в контексте `Request`, а не везде, где встречается Department.

---

## 14. Простая разница

```text
Apply To All Document Types = 1
        ↓
ограничение используется во всех подходящих связанных местах
```

```text
Apply To All Document Types = 0
Applicable For = Request
        ↓
ограничение применяется только для Request
```

Если сомневаешься, сначала сформулируй правило обычными словами.

Например:

> Анна вообще может работать только с Department A.

Тогда логичен широкий вариант.

Или:

> Department A ограничивает Анну только внутри Request.

Тогда нужен `Applicable For`.

---

# Часть 5. Is Default

## 15. Что делает Is Default

Допустим, Анне разрешены:

```text
Department A
Department B
```

Но чаще всего она создаёт документы для:

```text
Department A
```

Одну User Permission можно отметить:

```text
Is Default = 1
```

Например:

```text
Department A → Is Default
Department B → обычное разрешённое значение
```

Frappe может использовать default permission как значение по умолчанию для соответствующего Link-поля при создании нового документа.

В тестах самой ветки v16 это поведение проверяется на новом документе: значение из default User Permission подставляется в Link-поле.

---

## 16. Default не означает «разрешён только он»

Это частая ошибка.

Если есть:

```text
Department A → Is Default
Department B → разрешён
```

это не превращается в:

```text
доступен только Department A
```

Правильнее понимать так:

```text
A → разрешён и предпочтителен по умолчанию
B → тоже разрешён
```

`Is Default` влияет на удобство ввода, а не заменяет сам список разрешённых значений.

---

## 17. Для одного Allow нельзя бездумно назначать несколько defaults

Controller `User Permission` v16 проверяет пересечение default rules.

Если для одного пользователя и одного `Allow` уже существует подходящий default, Frappe не даст просто создать конфликтующий второй default в том же контексте.

Это логично: система должна понимать, какое значение считать основным.

---

# Часть 6. Tree и Hide Descendants

## 18. User Permission понимает иерархические DocType

Представим Tree DocType:

```text
Department

Company
├── Department A
│   ├── Department A1
│   └── Department A2
└── Department B
```

И User Permission:

```text
Allow     = Department
For Value = Department A
```

Для Tree DocType Frappe по умолчанию может добавить к разрешённому узлу его потомков.

То есть доступ получится примерно такой:

```text
Department A
Department A1
Department A2
```

Это поведение прямо реализовано в `get_user_permissions()` ветки v16.

---

## 19. Hide Descendants

Если дочерние узлы выдавать не нужно, используется:

```text
Hide Descendants = 1
```

Тогда:

```text
Department A  → разрешён
Department A1 → не добавляется автоматически
Department A2 → не добавляется автоматически
```

В тестах v16 отдельно проверяется этот сценарий: без `Hide Descendants` дочерний Tree-документ доступен, с флагом — уже нет.

Для обычного неиерархического DocType этот параметр смысла не имеет.

---

# Часть 7. Strict User Permissions

## 20. Что делать с документом, где Link вообще пустой

Представим:

```text
REQ-001 → Department A
REQ-002 → Department B
REQ-003 → department пустой
```

У Анны есть User Permission:

```text
Department A
```

С первыми двумя всё понятно.

Но что делать с:

```text
REQ-003
```

где Department не указан вообще?

Для этого в `System Settings` есть:

```text
Apply Strict User Permissions
```

---

## 21. Что меняет strict mode

В metadata v16 описание настройки сформулировано прямо:

если включён `Apply Strict User Permissions` и для пользователя определена User Permission на соответствующий DocType, документы с **пустым значением Link** не показываются этому пользователю.

Упрощённо:

```text
Strict OFF
→ пустая ссылка может не попадать под это ограничение так строго

Strict ON
→ если User Permission существует,
  пустое связанное значение тоже не считается разрешённым
```

Пример при strict mode:

```text
REQ-001 → Department A → да
REQ-002 → Department B → нет
REQ-003 → пусто         → нет
```

Это глобальная системная настройка, поэтому включать её нужно осознанно и проверять уже существующие документы с пустыми Link-полями.

---

# Часть 8. Ignore User Permissions

## 22. Иногда конкретный Link не должен участвовать в этих ограничениях

У `DocField` типов вроде `Link` есть свойство:

```text
Ignore User Permissions
```

Оно означает, что для этого конкретного поля User Permission не должна применяться обычным способом.

Например, в одном документе есть два Link на `Department`:

```text
working_department
reference_department
```

Первое поле реально определяет область доступа.

Второе используется только как справочная ссылка и по требованиям не должно ограничивать документ.

Тогда для второго поля иногда оправдано:

```text
Ignore User Permissions = 1
```

---

## 23. Не ставь Ignore User Permissions, чтобы «починить доступ»

Это опасный анти-паттерн.

Плохой сценарий:

```text
пользователь не видит документ
        ↓
не разбираемся почему
        ↓
ставим Ignore User Permissions
        ↓
«заработало»
```

Так можно случайно убрать настоящее ограничение доступа.

Сначала нужно понять:

```text
Role Permission?
User Permission?
Applicable For?
Strict mode?
Permission Level?
Sharing?
```

И только потом осознанно исключать конкретный Link из User Permission checking.

---

# Часть 9. Несколько разных ограничений

## 24. Один пользователь может иметь User Permissions разных типов

Например:

```text
Department = Department A
Region     = North
Project    = Project Alpha
```

Если `Request` содержит соответствующие Link-поля, permission engine может учитывать эти ограничения вместе.

То есть реальные доступные документы могут стать уже, чем при одном Department.

Именно поэтому большое количество User Permissions нужно проектировать как систему, а не добавлять случайными заплатками.

---

## 25. User Permission — это ограничение по пользователю, а не замена модели данных

Плохая идея:

```text
создать десятки User Permission,
чтобы компенсировать отсутствие нормальных Link-полей
```

Сначала документ должен иметь нормальную модель данных:

```text
Request.department → Department
Request.project    → Project
```

И уже поверх этих связей удобно строить User Permissions.

Если в документе всё хранится текстом:

```text
department = "Отдел А"
```

User Permission не сможет использовать такую связь так же естественно, как настоящий `Link`.

---

# Часть 10. Что User Permission НЕ делает

## 26. Она не выдаёт права на DocType

Если:

```text
Request Operator
→ нет Read на Request
```

то запись:

```text
User Permission
Department = Department A
```

не превратит это в Read.

Сначала Role Permissions.

Потом ограничения.

---

## 27. Она не заменяет Permission Level

Вопрос:

> может ли Анна видеть поле `internal_cost`?

Это задача:

```text
Permission Level
```

А вопрос:

> может ли Анна видеть REQ-001?

может решаться:

```text
User Permission
```

Это разные уровни.

---

## 28. Она не заменяет If Owner

Если правило звучит:

> пользователь работает только с документами, которые сам создал

сначала стоит проверить:

```text
Only if Creator / If Owner
```

Не нужно искусственно создавать User Permission только ради системного `owner`.

---

## 29. Она не является произвольным фильтром

Требование:

```text
показывать только Request со status = Open
```

не является типичной задачей User Permission.

`status` обычно `Select`, а не разрешённый связанный master-document.

То же самое:

```text
amount < 100000
creation > 2026-01-01
priority = High
```

Если доступ зависит от произвольной бизнес-логики, нужно рассматривать controller permission logic и другие серверные механизмы.

Это будет разобрано отдельно в главе о границах штатных permissions.

---

# Часть 11. Что происходит под капотом

## 30. User Permissions собираются по Allow

В `version-16` Frappe загружает User Permission пользователя и группирует их примерно так:

```text
Department
├── Department A
└── Department B

Project
└── Project Alpha
```

То есть для permission engine получается набор разрешённых документов каждого типа.

Для Tree DocType при необходимости туда же добавляются descendants.

Результат кэшируется для пользователя и сбрасывается после изменения User Permission.

Новичку это не нужно запоминать, но полезно понимать: это реальный серверный механизм, а не просто фильтр, нарисованный List View.

---

## 31. Permission-aware запросы учитывают User Permissions

В актуальной документации Query Builder v16 это сформулировано явно: когда запрос выполняется с permission checking, Frappe учитывает:

```text
Role Permissions
+
User Permissions
```

Поэтому правильный серверный код должен пользоваться permission-aware API там, где результат предназначен обычному пользователю.

Сырые SQL-запросы сами по себе не получают всю permission model магически.

Эта тема подробно появится позже в главах про ORM и Database API.

---

# Часть 12. Практика

## 32. Создадим простой пример

Нужны два DocType:

```text
Department
Request
```

В `Request` добавь:

```text
subject
Field Type = Data

 department
Field Type = Link
Options = Department
```

Создай отделы:

```text
Department A
Department B
Department C
```

И несколько Request:

```text
REQ-001 → Department A
REQ-002 → Department B
REQ-003 → Department A
REQ-004 → Department C
```

---

## 33. Создай тестового пользователя

Например:

```text
anna@example.com
```

Дай ему роль, которая имеет как минимум:

```text
Request
├── Read
├── Create
└── Write

Department
└── Read
```

Сначала войди под этим пользователем **без User Permission**.

Убедись, что он видит обычный набор `Request`.

Это важно: мы сначала проверяем базовые Role Permissions.

---

## 34. Добавь User Permission

Создай:

```text
User Permission

User      = anna@example.com
Allow     = Department
For Value = Department A
```

Сохрани.

Зайди под Анной снова и проверь список `Request`.

Ожидаемая идея:

```text
Department A → доступен
остальные     → отфильтрованы permission model
```

Также открой Link `department` в новом `Request` и посмотри, какие значения предлагает система.

---

## 35. Разреши второй Department

Добавь ещё одну User Permission:

```text
User      = anna@example.com
Allow     = Department
For Value = Department B
```

Теперь проверь:

```text
Department A
Department B
```

Оба должны входить в разрешённый набор.

---

## 36. Проверь Is Default

Одну из User Permission отметь:

```text
Is Default = 1
```

Создай новый `Request`.

Посмотри, подставляет ли Frappe это значение в подходящее Link-поле по умолчанию.

После этого всё равно проверь, что второе разрешённое значение остаётся доступным для выбора.

---

## 37. Проверь Applicable For

Если у тебя есть второй DocType с Link на `Department`, можно увидеть разницу между:

```text
Apply To All Document Types = 1
```

и:

```text
Apply To All Document Types = 0
Applicable For = Request
```

Это лучший способ понять настройку — один раз увидеть разницу руками.

---

# Часть 13. Типичные ошибки

## 38. Создать роль на каждый отдел

Плохо:

```text
Department A Operator
Department B Operator
Department C Operator
```

только ради того, чтобы разделить одни и те же `Request` по Department.

Если действия одинаковые, обычно лучше:

```text
Role → что можно делать
User Permission → с какими Department
```

---

## 39. Думать, что User Permission даёт доступ

```text
User Permission = Department A
```

не означает автоматически:

```text
Read Request
```

Без Role Permission пользователь всё равно может не иметь доступа к DocType.

---

## 40. Перепутать default с единственным разрешённым значением

```text
Is Default
```

не означает:

```text
Only This Value
```

Это только предпочтительное разрешённое значение.

---

## 41. Включить strict mode и не проверить старые документы

Если часть документов имеет:

```text
department = пусто
```

включение:

```text
Apply Strict User Permissions
```

может изменить их видимость.

Перед включением такой глобальной настройки нужно проверить данные.

---

## 42. Лечить проблему через Ignore User Permissions

Если доступ построен неправильно, флаг:

```text
Ignore User Permissions
```

может просто скрыть архитектурную ошибку.

Используй его только когда конкретная Link-связь **по смыслу действительно не должна ограничивать документ**.

---

## 43. Пытаться User Permission заменить произвольную бизнес-логику

User Permission отлично подходит для:

```text
Department
Project
Region
Branch
другой master DocType
```

Но требование вроде:

```text
видеть документы дешевле 100 000
```

уже относится к другому классу permission logic.

Не пытайся заставить один инструмент решать все задачи доступа.

---

# Часть 14. Как выбирать механизм

## 44. Простая шпаргалка

```text
Нужно решить, ЧТО пользователь может делать?
→ Role Permission

Нужно ограничить отдельные ПОЛЯ?
→ Permission Level

Нужно ограничить КОНКРЕТНЫЕ ДОКУМЕНТЫ
по связанному Department / Project / Region?
→ User Permission

Нужно только документы, созданные самим пользователем?
→ If Owner

Нужно разово дать доступ к одному документу?
→ Sharing

Нужно сложное условие доступа по бизнес-логике?
→ серверная permission logic
```

Последние два механизма подробнее разберём в следующих главах.

---

## 45. Что запомнить

1. `User Permission` **сужает** доступ конкретного User к связанным документам.
2. Она не заменяет Role Permission и сама не выдаёт `Read` или `Write` на DocType.
3. Базовая запись состоит из `User + Allow + For Value`.
4. Несколько `For Value` одного `Allow` образуют набор разрешённых значений.
5. `Applicable For` ограничивает область применения конкретным DocType.
6. `Is Default` выбирает предпочтительное значение, но не делает его единственным разрешённым.
7. Для Tree DocType потомки разрешённого узла обычно тоже включаются; `Hide Descendants` отключает это расширение.
8. `Apply Strict User Permissions` особенно важен для документов с пустыми Link-полями.
9. `Ignore User Permissions` — исключение для конкретной Link-связи, а не универсальная кнопка «починить права».
10. User Permission лучше всего работает поверх нормальной модели данных с настоящими `Link`.

---

## 46. Контрольные вопросы

1. Чем Role Permission отличается от User Permission?
2. Что означает `Allow`?
3. Что хранится в `For Value`?
4. Почему User Permission обычно связана с Link-полями?
5. Что произойдёт, если разрешить одному User два Department?
6. Может ли User Permission сама выдать `Read` на `Request`?
7. Для чего нужен `Applicable For`?
8. Чем `Is Default` отличается от единственного разрешённого значения?
9. Как ведут себя descendants Tree DocType?
10. Что делает `Hide Descendants`?
11. Для чего нужен `Apply Strict User Permissions`?
12. Чем опасно бездумное `Ignore User Permissions`?
13. Подходит ли User Permission для условия `amount > 100000`?
14. Чем User Permission отличается от Permission Level?

Если на эти вопросы можно ответить без подсказки, базовая модель User Permissions уже понятна.

---

## Источники

- [Frappe Framework — Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [Frappe Framework — Query permissions](https://docs.frappe.io/framework/get_query)
- [`User Permission` metadata — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user_permission/user_permission.json)
- [`User Permission` controller — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user_permission/user_permission.py)
- [`User Permission` tests — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user_permission/test_user_permission.py)
- [`permissions.py` — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py)
- [`System Settings` metadata — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/system_settings/system_settings.json)
- [`DocField` metadata — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/docfield/docfield.json)

---

Следующая глава: **21. Owner и Sharing**.
