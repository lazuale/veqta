# 19. Permission Level

В прошлой главе мы настроили права роли на DocType целиком.

Например:

```text
Request Operator
├── Read
├── Create
└── Write
```

Но теперь возникает другой вопрос:

> а если пользователь должен видеть документ, но не все его поля?

Например, обычный оператор может работать с `Request`, но не должен видеть внутреннюю стоимость.

Или должен видеть её, но не менять.

Для этого во Frappe есть **Permission Level**, сокращённо `Perm Level`.

Проверено: **2026-08-31**.

---

## 1. Главная идея

У каждого обычного поля DocType есть свойство:

```text
Perm Level
```

По умолчанию оно равно:

```text
0
```

Это означает, что поле использует базовый уровень permissions документа.

Например:

```text
Request
├── subject         Perm Level = 0
├── description     Perm Level = 0
├── department      Perm Level = 0
└── internal_cost   Perm Level = 1
```

Теперь можно отдельно определить:

```text
кто имеет Read на Level 1
кто имеет Write на Level 1
```

Получается двухступенчатая модель:

```text
сначала доступ к документу
        ↓
Level 0
        ↓
потом доступ к отдельным группам полей
        ↓
Level 1 / Level 2 / ...
```

---

## 2. Самое важное правило

**Level 0 — базовый доступ к документу.**

Если у пользователя нет доступа на Level 0, права на Level 1, 2 и выше сами по себе бесполезны.

Например:

```text
Request Manager
Level 1 → Read + Write
```

но на Level 0 у этой роли нет `Read`.

Это не означает:

```text
пользователь откроет Request и увидит только поля Level 1
```

Нет.

Сначала пользователь должен вообще иметь доступ к `Request`.

Упрощённо:

```text
есть Read на Level 0?
        ├── нет → документа для нормальной работы нет
        └── да
             ↓
        проверяем уровень конкретного поля
```

Именно поэтому Level 1+ нельзя воспринимать как самостоятельные «мини-роли» внутри документа.

---

## 3. Один практический пример

Создадим три роли:

```text
Request Reader
Request Operator
Request Manager
```

И DocType:

```text
Request
```

с полями:

```text
subject
status
department
internal_cost
```

Первые три поля оставим на Level 0:

```text
subject       → 0
status        → 0
department    → 0
```

А поле:

```text
internal_cost
```

переведём на:

```text
Perm Level = 1
```

Теперь зададим permissions.

### Request Reader

```text
Level 0
└── Read
```

Level 1 для него не создаём.

Результат:

```text
Request Reader
├── видит Request
├── видит subject
├── видит status
├── видит department
└── internal_cost не получает Read через Level 1
```

### Request Operator

```text
Level 0
├── Read
├── Create
└── Write

Level 1
└── Read
```

Результат:

```text
Request Operator
├── редактирует обычные поля
└── internal_cost видит, но не редактирует
```

### Request Manager

```text
Level 0
├── Read
├── Create
└── Write

Level 1
├── Read
└── Write
```

Результат:

```text
Request Manager
└── internal_cost видит и редактирует
```

Вот основной сценарий Permission Level.

---

# Часть 1. Где задаётся Perm Level поля

## 4. Через DocType или Customize Form

У DocField есть свойство:

```text
Perm Level
```

В v16 это обычное целочисленное поле metadata.

По умолчанию:

```text
0
```

Для стандартного DocType обычно удобнее менять его через:

```text
Customize Form
```

Для своего Standard DocType в собственном App уровень можно задавать в metadata самого DocType.

Логика одинакова:

```text
DocField
└── permlevel = 1
```

---

## 5. Не нужно создавать отдельный уровень для каждого поля

Permission Level предназначен для **группировки полей с одинаковой политикой доступа**.

Плохой вариант:

```text
field_a → Level 1
field_b → Level 2
field_c → Level 3
field_d → Level 4
```

если на самом деле всё это одна группа «внутренние данные».

Лучше:

```text
internal_cost       → Level 1
internal_comment    → Level 1
internal_rating     → Level 1
```

и один набор правил:

```text
Level 1
├── Request Operator → Read
└── Request Manager  → Read + Write
```

Так модель остаётся понятной.

---

# Часть 2. Где задаются права уровня

## 6. Role Permissions Manager

Открой:

```text
Role Permissions Manager
```

выбери:

```text
Document Type = Request
```

На Level 0 находятся обычные права DocType.

Например:

```text
Request Operator | Level 0 | Read Write Create
```

Для поля с `Perm Level = 1` добавляется отдельное правило:

```text
Request Operator | Level 1 | Read
Request Manager  | Level 1 | Read Write
```

В интерфейсе v16 для уровней выше 0 доступны только права, относящиеся к полям:

```text
Read
Write
Mask
```

Такие действия, как:

```text
Create
Delete
Submit
Cancel
Amend
Report
Import
Export
Print
Email
Share
```

относятся к документу, а не к отдельному полю, поэтому на Level 1+ Role Permissions Manager их не показывает.

---

## 7. Почему Create не бывает «для поля»

Допустим:

```text
internal_cost → Level 1
```

Нельзя осмысленно сказать:

```text
Create internal_cost
```

Создаётся весь документ `Request`.

Поэтому:

```text
Create → Level 0
```

А поле уже получает:

```text
Read / Write
```

согласно своему `Perm Level`.

---

# Часть 3. Как Frappe решает, что делать с полем

## 8. У каждого поля выбирается permission row его уровня

Упрощённо Frappe делает так:

```text
поле internal_cost
        ↓
permlevel = 1
        ↓
смотрим permissions пользователя на Level 1
```

Дальше в Desk возможны три базовых результата:

```text
Write
Read
None
```

### Write

Если на этом уровне есть `Write`, поле может быть редактируемым.

### Read

Если `Write` нет, но есть `Read`, поле отображается только для чтения.

### None

Если нет и `Read`, и `Write`, поле не получает обычного доступа через permissions этого уровня.

Упрощённая схема:

```text
Level N имеет Write?
        ├── да  → Write
        └── нет
             ↓
        имеет Read?
        ├── да  → Read
        └── нет → None
```

---

## 9. Write не отменяет свойства самого поля

Permission Level — не единственный механизм, влияющий на редактирование.

Допустим:

```text
internal_cost
Perm Level = 1
Read Only = 1
```

а роль имеет:

```text
Level 1 → Read + Write
```

Поле всё равно останется read-only, потому что metadata поля дополнительно ограничивает редактирование.

То же касается других механизмов, например:

```text
Hidden
Read Only
Set Only Once
Virtual field
docstatus
Allow on Submit
Workflow
Depends On
```

Поэтому правильная логика такая:

```text
permission разрешает максимум
        ↓
свойства поля и состояние документа
могут дополнительно ограничить
```

Но поле не должно становиться доступнее, чем разрешают permissions.

---

## 10. Hidden и Permission Level — не одно и то же

Иногда хочется просто поставить:

```text
Hidden = 1
```

и считать, что поле защищено.

Это ошибка в модели доступа.

`Hidden` — свойство интерфейса поля.

`Perm Level` — часть permission model.

Если поле содержит данные, которые разные роли действительно не должны читать или изменять, используй permissions, а не только визуальное скрытие.

Простое правило:

```text
хочу убрать поле из формы для всех
→ Hidden

хочу разный доступ для разных ролей
→ Perm Level
```

---

# Часть 4. Permission Level и сервер

## 11. Это не только фронтенд

В v16 permission-aware механизмы Frappe получают список разрешённых полей через metadata и permissions пользователя.

У Framework есть серверная функция, которая строит permitted fields для DocType.

Поэтому Permission Level используется не только для того, чтобы JavaScript формы спрятал контрол.

Он участвует и в серверной модели разрешённых полей для стандартных permission-aware путей Framework.

Это принципиально важно:

```text
Perm Level
≠ CSS
≠ декоративное скрытие
```

Это часть системы доступа.

---

## 12. Но низкоуровневый код может обойти permissions

При этом Frappe — framework, а не магическая песочница.

Разработчик собственного App может намеренно использовать низкоуровневые механизмы или флаги вроде обхода permission checks.

Например, опасно считать:

```text
раз поле защищено Perm Level,
любой Python-код автоматически никогда его не прочитает
```

Это неверная гарантия.

Правильнее так:

```text
обычные permission-aware механизмы Frappe
→ учитывают permissions

код, который намеренно обходит permissions
→ ответственность разработчика
```

Позже это станет особенно важно в главах про API, controllers и Database API.

---

# Часть 5. Несколько ролей

## 13. Права складываются и внутри Permission Level

Это продолжение правила из прошлой главы.

Пользователь имеет:

```text
Role A
Role B
```

Для Level 1:

```text
Role A → Read
Role B → Write
```

Frappe собирает разрешения подходящих ролей на этом уровне.

Поэтому итог будет включать разрешённые права обеих ролей.

То есть Permission Level не превращает систему в `grant/deny`.

Пустая галочка в одной роли не отменяет разрешение другой роли.

Упрощённо:

```text
Role A Level 1 → Read
Role B Level 1 → Write

итог Level 1    → Read + Write
```

Поэтому при проектировании доступа всегда проверяй **весь набор ролей пользователя**, а не одну выбранную роль.

---

# Часть 6. Level 0 и Level 1 работают вместе

## 14. Очень частая ошибка

Допустим роль имеет:

```text
Level 0
└── Read

Level 1
└── Write
```

Новичок может ожидать:

```text
обычные поля → только чтение
internal_cost → редактирование
```

Но нужно помнить, что возможность сохранить изменения документа всё равно существует в общей permission model и жизненном цикле документа.

Практически, если пользователю действительно нужно редактировать отдельные поля существующего документа, его базовая модель обычно должна быть согласована с `Write` на документ и отдельными ограничениями полей.

Не стоит строить схему, где Level 0 и верхние уровни противоречат друг другу по смыслу.

Хорошая модель:

```text
Operator
Level 0 → Read + Write
Level 1 → Read

Manager
Level 0 → Read + Write
Level 1 → Read + Write
```

Она читается однозначно.

---

## 15. Permission Level не является Workflow

Допустим нужно:

```text
до согласования поле editable
после согласования read-only
```

Это не обязательно задача Permission Level.

Permission Level отвечает в первую очередь на вопрос:

> какая роль имеет доступ к какой группе полей?

А вопрос:

> что можно менять в конкретном состоянии процесса?

чаще относится к:

```text
Workflow
Read Only
Depends On
Allow on Submit
Client Script
или application logic
```

Не нужно пытаться кодировать все состояния процесса через десятки Permission Levels.

---

# Часть 7. Submitted документы

## 16. Permission Level не отменяет docstatus

Если DocType submittable и документ уже:

```text
docstatus = 1
```

обычное поле становится read-only, даже если роль имеет `Write` на его Permission Level.

Чтобы отдельное поле разрешалось менять после Submit, у поля должен быть соответствующий штатный механизм:

```text
Allow on Submit
```

и пользователь всё равно должен иметь подходящее `Write`.

Упрощённо:

```text
Level 1 Write
        ↓
документ Submitted?
        ├── нет → поле может быть Write
        └── да
             ↓
        Allow on Submit?
        ├── да  → может остаться Write
        └── нет → Read
```

То есть Permission Level работает внутри общей lifecycle-модели документа, а не вместо неё.

---

# Часть 8. Child Table

## 17. Поля строки Child Table тоже имеют Perm Level

Child DocType не получает самостоятельную обычную permission table как независимый DocType.

Но его DocFields имеют metadata, включая `permlevel`.

Поэтому при проектировании child table нужно думать о двух слоях:

```text
доступ к parent document
        ↓
доступ к полям child row
```

Не нужно пытаться назначать отдельные обычные Role Permissions самому Child DocType как независимому master-документу.

Это продолжение модели, разобранной в главе про Child Table.

---

# Часть 9. Практическая настройка

## 18. Задача

Нужно получить:

```text
Request Reader
→ видит обычные поля
→ не видит Internal Cost

Request Operator
→ редактирует обычные поля
→ Internal Cost только читает

Request Manager
→ редактирует всё
```

---

## 19. Шаг 1. Поля Request

Создай или используй:

```text
subject
status
department
internal_cost
```

Для первых трёх:

```text
Perm Level = 0
```

Для `internal_cost`:

```text
Perm Level = 1
```

---

## 20. Шаг 2. Level 0 permissions

В Role Permissions Manager:

```text
Request Reader
Level 0
Read = 1
```

```text
Request Operator
Level 0
Read   = 1
Write  = 1
Create = 1
```

```text
Request Manager
Level 0
Read   = 1
Write  = 1
Create = 1
```

---

## 21. Шаг 3. Level 1 permissions

Добавь:

```text
Request Operator
Level 1
Read = 1
```

и:

```text
Request Manager
Level 1
Read  = 1
Write = 1
```

Для `Request Reader` Level 1 не добавляй.

---

## 22. Шаг 4. Проверка под реальными тестовыми пользователями

Создай трёх обычных тестовых пользователей и назначь им только нужные роли.

Не проверяй эту модель под `Administrator`.

Проверь:

| Роль | Обычные поля | Internal Cost |
|---|---|---|
| Request Reader | Read | нет обычного Read на Level 1 |
| Request Operator | Write | Read |
| Request Manager | Write | Write |

После этого добавь вторую роль одному из пользователей и посмотри, как права объединяются.

Это лучший способ руками понять модель.

---

# Часть 10. Что Permission Level не решает

## 23. Он не выбирает конкретные документы

Permission Level отвечает на вопрос:

```text
какие поля доступны роли?
```

Но не отвечает на вопрос:

```text
какие именно Request доступны этому пользователю?
```

Для ограничения набора документов используются другие механизмы, прежде всего:

```text
User Permission
Owner
Sharing
```

которые будут разобраны дальше.

---

## 24. Он не заменяет User Permission

Пример:

```text
Анна должна видеть Request только Department A
Борис — только Department B
```

Это не Permission Level.

Поля у обоих могут быть одинаковыми.

Различается **набор документов**.

Значит нужен другой слой permission model.

---

## 25. Он не заменяет отдельный DocType

Если «секретные поля» фактически являются отдельной сущностью со своим жизненным циклом, владельцем, историей, Workflow и связями, не надо прятать половину огромного документа за Level 7.

Иногда правильнее сделать:

```text
Request
        ↓ Link
Request Internal Review
```

чем строить:

```text
Request
├── Level 0
├── Level 1
├── Level 2
├── Level 3
├── Level 4
└── Level 5
```

Permission Level полезен для нескольких групп полей.

Он не должен превращаться в замену нормальной модели данных.

---

# Часть 11. Типичные ошибки

## 26. Ошибка: считать Level 1 более «главным», чем Level 0

Неверно:

```text
Level 1 > Level 0
```

Это не иерархия полномочий.

Правильнее:

```text
Level 0 → поля группы 0
Level 1 → поля группы 1
Level 2 → поля группы 2
```

Число — идентификатор группы permission level, а не ранг сотрудника.

---

## 27. Ошибка: использовать Perm Level вместо Role

Плохо:

```text
Level 1 = оператор
Level 2 = начальник
Level 3 = директор
```

Потому что смысл уровня должен задаваться через **поля**, а доступ — через **Roles**.

Лучше:

```text
Level 0 → обычные поля
Level 1 → внутренние финансовые поля
Level 2 → служебные поля контроля
```

и уже роли получают нужные права на эти уровни.

---

## 28. Ошибка: надеяться только на Hidden

Если поле действительно чувствительное:

```text
Hidden
```

не является заменой permission design.

Используй Permission Level.

---

## 29. Ошибка: делать десятки уровней

Если permission matrix выглядит так:

```text
0
1
2
3
4
5
6
7
8
9
```

и никто уже не понимает, почему конкретное поле находится на Level 6, модель стала слишком сложной.

Сначала проверь:

```text
можно ли упростить роли?
можно ли сгруппировать поля?
не является ли часть данных отдельным DocType?
не пытаемся ли мы через permissions реализовать Workflow?
```

---

## 30. Ошибка: проверять только форму

Нужно проверить не только:

```text
видно поле или нет
```

но и:

```text
можно ли его изменить
что происходит после Submit
что происходит с дополнительной Role
как ведут себя List / Report / API сценарии
```

Permission model должна быть проверена как система, а не как внешний вид формы.

---

# Часть 12. Decision tree

## 31. Как понять, нужен ли Permission Level

```text
Нужно ограничить весь DocType?
        ↓ да
Role Permission Manager, Level 0

Нужно ограничить конкретные документы?
        ↓ да
User Permission / Owner / Sharing

Нужно дать разным ролям разный доступ к группе полей?
        ↓ да
Permission Level

Нужно менять доступ в зависимости от состояния процесса?
        ↓ да
Workflow / lifecycle / conditional logic

Данные фактически имеют отдельный жизненный цикл?
        ↓ да
отдельный DocType
```

---

# Часть 13. Граница stock / low-code / code

## 32. Что здесь умеет чистый Frappe

**Штатно Frappe:**

```text
DocField Perm Level
Role Permissions Manager
Read / Write на уровнях 1+
полевая проверка в Desk
permission-aware permitted fields
работа вместе с docstatus и Allow on Submit
```

Для обычной задачи:

> «оператор видит поле, менеджер может его редактировать»

Python не нужен.

---

## 33. Когда low-code пока не нужен

Не пиши Client Script вроде:

```javascript
frm.set_df_property("internal_cost", "hidden", true)
```

только для реализации обычного role-based field access.

Сначала проверь Permission Level.

Client Script может менять интерфейс, но он не должен быть первым инструментом для security model.

---

## 34. Когда может понадобиться код

Код может понадобиться, если правило существенно сложнее штатной модели.

Например:

```text
поле можно менять только автору в течение 30 минут
```

или:

```text
доступ зависит от вычисляемой доменной логики нескольких связанных документов
```

Но даже тогда базовые Role Permissions и Permission Level остаются фундаментом, а custom logic должна дополнять их, а не хаотично заменять.

---

# Что нужно запомнить

1. У каждого обычного DocField есть `Perm Level`.
2. По умолчанию поля находятся на Level 0.
3. Level 0 отвечает за базовый доступ к документу и его обычным полям.
4. Level 1+ используют для групп полей с отдельной политикой доступа.
5. Без доступа к документу на Level 0 верхние уровни сами по себе бесполезны.
6. На Level 1+ Role Permissions Manager показывает полевые права `Read`, `Write` и `Mask`.
7. В Desk поле получает состояние `Write`, `Read` или `None` согласно своему уровню и дополнительным ограничениям metadata/lifecycle.
8. Права нескольких ролей складываются и на одном Permission Level.
9. `Hidden` не заменяет Permission Level.
10. Permission Level не заменяет User Permission, Workflow или отдельный DocType.
11. Permission Level участвует не только в отображении формы, но и в permission-aware модели разрешённых полей Framework.
12. Проверять permissions нужно под обычными тестовыми пользователями, а не под Administrator.

---

# Контрольные вопросы

1. Что означает `Perm Level = 0` у DocField?
2. Может ли Level 1 самостоятельно дать пользователю доступ к документу без Level 0?
3. Чем `Read` на Level 1 отличается от `Write` на Level 1?
4. Что произойдёт с полем Level 1, если у пользователя нет прав на этот уровень?
5. Почему `Create` не имеет смысла на Level 1?
6. Почему `Hidden` не является заменой Permission Level?
7. Что произойдёт, если одна Role даёт Level 1 Read, а другая Level 1 Write?
8. Может ли `Read Only = 1` дополнительно ограничить поле, даже если Level 1 даёт Write?
9. Как `docstatus = 1` влияет на редактирование поля?
10. Для чего нужен `Allow on Submit`?
11. Чем Permission Level отличается от User Permission?
12. Почему десяток Permission Levels обычно является плохим признаком?
13. Когда вместо очередного Permission Level стоит создать отдельный DocType?
14. Почему permissions нужно проверять не только визуально в форме?
15. Почему тестирование под Administrator не показывает реальную картину доступа?

---

# Официальные источники

- Users and Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- DocField metadata, `permlevel`: https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/docfield/docfield.json
- Role Permissions Manager UI: https://github.com/frappe/frappe/blob/version-16/frappe/core/page/permission_manager/permission_manager.js
- Client-side permission resolution: https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/model/perm.js
- Server-side permission engine: https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py
- Server-side permitted fields: https://github.com/frappe/frappe/blob/version-16/frappe/model/__init__.py

---

Следующая глава: **20. User Permission**.
