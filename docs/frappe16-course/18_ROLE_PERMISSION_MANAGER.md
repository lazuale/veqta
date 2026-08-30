# 18. Role Permission Manager

В прошлой главе мы разобрали две вещи:

```text
User
└── получает Role
```

Но пока Role — это просто имя.

Чтобы роль действительно что-то разрешала, нужно сказать Frappe:

> что эта роль может делать с конкретным DocType?

Для этого существует **Role Permissions Manager**.

Проверено: **2026-08-31**.

---

## 1. Самый простой пример

Есть DocType:

```text
Request
```

И три роли:

```text
Request Reader
Request Operator
Request Approver
```

Мы хотим получить такую логику:

```text
Request Reader
└── только читать

Request Operator
├── читать
├── создавать
└── редактировать

Request Approver
├── читать
├── отправлять документ в Submit
└── отменять Submitted-документ
```

В Role Permissions Manager это примерно превращается в такую таблицу:

| Role | Read | Write | Create | Submit | Cancel |
|---|---:|---:|---:|---:|---:|
| Request Reader | ✓ |  |  |  |  |
| Request Operator | ✓ | ✓ | ✓ |  |  |
| Request Approver | ✓ |  |  | ✓ | ✓ |

Вот и вся базовая идея.

**Role Permissions Manager связывает Role, DocType и разрешённые действия.**

---

## 2. Где это находится

Самый простой путь:

```text
Awesomebar
→ Role Permissions Manager
```

Внутри можно выбрать:

```text
Document Type
Role
```

Например:

```text
Document Type = Request
Role          = Request Operator
```

После этого видны permission rules для выбранной комбинации.

Доступ к самому Role Permissions Manager штатно предназначен для `System Manager`.

---

## 3. Как читать одну строку permissions

Представим такую строку:

```text
Document Type: Request
Role:          Request Operator
Level:         0

Read    ✓
Write   ✓
Create  ✓
Delete
```

Она означает:

```text
если User имеет Role Request Operator
        ↓
для DocType Request
        ↓
он получает Read + Write + Create
```

Это правило относится не к одному конкретному пользователю, а ко всем пользователям с этой Role.

---

# Часть 1. Основные права

## 4. Read

`Read` разрешает открыть и прочитать документ.

Например:

```text
Request Reader
Read = ✓
```

Пользователь сможет открыть:

```text
REQ-0001
REQ-0002
REQ-0003
```

если никакие другие ограничения не отсекают эти документы.

`Read` не означает право редактировать.

---

## 5. Write

`Write` разрешает изменять существующий документ, к которому у пользователя есть доступ.

Обычный рабочий набор:

```text
Read  ✓
Write ✓
```

Например:

```text
REQ-0001
Subject: Проверить отчёт
```

Пользователь с Write может изменить Subject и сохранить документ, если остальные правила это позволяют.

### Важно

`Write` и `Read` — разные permissions.

Не стоит мыслить так:

```text
Write автоматически включает Read
```

Для обычной роли редактора практически всегда явно дают оба:

```text
Read  ✓
Write ✓
```

---

## 6. Create

`Create` разрешает создать новый документ.

Например:

```text
Request Operator
Create = ✓
```

позволяет нажать:

```text
+ Add Request
```

и создать новую запись.

Но `Create` не означает автоматически, что пользователь сможет потом редактировать все существующие Request.

Для обычного оператора чаще используется:

```text
Read   ✓
Create ✓
Write  ✓
```

---

## 7. Delete

`Delete` разрешает удаление документа там, где lifecycle документа это допускает.

Это отдельное право.

Не нужно выдавать его просто потому, что пользователь умеет редактировать.

Например, можно сделать:

```text
Request Operator
Read   ✓
Create ✓
Write  ✓
Delete
```

Тогда оператор работает с документами, но не может их удалять.

Для рабочих систем это часто разумнее.

---

## 8. Почему права лучше выдавать по необходимости

Плохая привычка:

```text
поставить все галочки
```

только потому, что так быстрее.

Лучше начать с реальных действий пользователя.

Например:

```text
Что должен делать оператор?

1. видеть Request      → Read
2. создавать Request   → Create
3. исправлять Request  → Write
4. удалять Request?    → нет
5. экспортировать?     → только если действительно нужно
```

Так permission model остаётся понятной.

---

# Часть 2. Select

## 9. Select и Read — не одно и то же

`Select` нужен для более узкого сценария: пользователь может **найти и выбрать документ как ссылку**, но не обязательно открыть его полноценную форму.

Представим:

```text
Request
└── Department → Link → Department
```

Пользователю нужно выбрать Department при заполнении Request.

Но ему не обязательно давать полноценный доступ к карточкам Department.

Можно использовать:

```text
Department
Select ✓
Read
```

Тогда Department можно использовать в Link-поиске, не превращая пользователя в обычного читателя всего справочника.

Простая разница:

```text
Select
→ можно найти и выбрать

Read
→ можно открыть и прочитать документ
```

В текущем permission engine v16 есть ещё полезное правило: если отдельного `Select` нет, но есть `Read`, проверка Select может пройти через Read.

То есть практически:

```text
Read ⇒ достаточно и для обычного выбора в Link
```

Но обратное неверно:

```text
Select ⇏ Read
```

---

# Часть 3. Submit, Cancel и Amend

## 10. Эти права появляются только там, где есть смысл

Для обычного DocType:

```text
Is Submittable = 0
```

permissions:

```text
Submit
Cancel
Amend
```

не нужны.

В интерфейсе Role Permissions Manager v16 они не показываются для несубмиттабельного DocType.

Если же:

```text
Is Submittable = 1
```

то появляется lifecycle:

```text
Draft
  ↓ Submit
Submitted
  ↓ Cancel
Cancelled
  ↓ Amend
новый Draft
```

Мы подробно разбирали его в главе 10.

---

## 11. Submit

`Submit` разрешает переход:

```text
docstatus 0
→
docstatus 1
```

То есть пользователь может подтвердить Draft.

Например:

```text
Request Approver
Read   ✓
Submit ✓
```

---

## 12. Cancel

`Cancel` разрешает отменить Submitted-документ:

```text
docstatus 1
→
docstatus 2
```

Обычно это более сильное право, чем обычное редактирование.

Поэтому его не стоит автоматически выдавать всем, кому дали Submit.

---

## 13. Amend

`Amend` разрешает создать исправленную версию отменённого документа.

Это не возвращает старый документ обратно в Draft.

Упрощённо:

```text
REQ-0001
Cancelled
   ↓ Amend
REQ-0001-1
Draft
```

---

# Часть 4. Остальные штатные permissions

## 14. Print

`Print` разрешает печать документа и использование соответствующих возможностей печатного представления/PDF.

Если человеку не нужно выгружать документ в печатном виде, это право необязательно.

---

## 15. Email

`Email` разрешает отправлять документ через штатные email-действия Frappe.

Это не означает «пользователь вообще может пользоваться почтой».

Permission относится к email-действию для данного DocType.

---

## 16. Report

`Report` разрешает использовать отчёты, связанные с DocType, при наличии остальных необходимых прав.

Например:

```text
Request Analyst
Read   ✓
Report ✓
```

может работать с отчётным представлением Request.

`Report` не превращает Frappe в отдельную BI-систему — это permission на штатные report-механизмы.

---

## 17. Export

`Export` разрешает выгружать данные.

Это право часто недооценивают.

Читать записи в интерфейсе и скачать большой набор данных — разные по последствиям действия.

Поэтому `Export` лучше выдавать осознанно.

---

## 18. Import

`Import` разрешает использовать Data Import для данного DocType.

Но одной permission недостаточно.

Сам DocType ещё должен разрешать импорт:

```text
Allow Import = 1
```

То есть:

```text
Import permission = ✓
        +
DocType Allow Import = ✓
        ↓
импорт возможен
```

---

## 19. Share

`Share` разрешает делиться доступом к отдельным документам с другими пользователями.

Например:

```text
REQ-0007
→ Share
→ anna@example.com
```

Sharing разберём отдельно в главе 21.

Также в System Settings можно глобально отключить document sharing; тогда одна галочка `Share` не сможет обойти глобальный запрет.

---

## 20. Mask

В интерфейсе v16 есть permission `Mask`.

Она связана с механизмом маскирования значений полей.

Пример идеи:

```text
81112345678
↓ mask
811XXXXXXX
```

На первом проходе курса достаточно знать, что это **не обычный Read/Write**, а специальный механизм работы с маскируемыми полями.

Не нужно использовать Mask для решения обычной задачи «скрыть поле от роли» — для этого есть Permission Level, который разберём в следующей главе.

---

# Часть 5. Only if Creator

## 21. Самое полезное ограничение внутри Role Permission Manager

Для permission rule уровня 0 можно включить:

```text
Only if Creator
```

В metadata это поле называется:

```text
if_owner
```

Смысл:

> правило применяется к документу, если текущий пользователь является его системным Owner.

Например:

```text
Request Operator

Read  ✓
Write ✓
Only if Creator ✓
```

Анна создала:

```text
REQ-0001
owner = anna@example.com
```

Борис создал:

```text
REQ-0002
owner = boris@example.com
```

Тогда Анна по такому правилу работает со своей:

```text
REQ-0001
```

но не получает те же owner-права на:

```text
REQ-0002
```

---

## 22. Creator здесь — это именно `owner`

Это частая ошибка.

`Only if Creator` не проверяет:

```text
Assigned To
Responsible User
Department
Created By — ваше отдельное поле
Workflow State
```

Он опирается на системное поле:

```text
owner
```

которое Frappe автоматически хранит у документа.

Поэтому такой механизм подходит для логики:

> пользователь работает со своими созданными документами.

Но не подходит для логики:

> пользователь работает со всеми документами, назначенными на него.

Это уже другая задача.

---

## 23. Only if Creator не является отрицательным запретом

Представим, у User две роли.

Первая:

```text
Request Operator
Read ✓
Only if Creator ✓
```

Вторая:

```text
Request Auditor
Read ✓
```

без ограничения по owner.

Итог:

```text
Request Auditor
```

уже даёт обычный `Read` на DocType.

`Only if Creator` из другой роли не сможет превратить его в запрет.

Почему — разберём прямо сейчас.

---

# Часть 6. Права нескольких Roles складываются

## 24. Во Frappe нет обычного правила «Deny победил Allow»

Это одна из самых важных вещей во всём блоке permissions.

Представим User:

```text
anna@example.com
├── Request Reader
└── Request Editor
```

Permissions:

```text
Request Reader
Read ✓
Write

Request Editor
Read
Write ✓
```

Новичок иногда читает это так:

```text
первая роль запрещает Write
вторая роль запрещает Read
```

Но пустая галочка **не является явным запретом**.

Frappe рассматривает подходящие permission rows всех ролей и собирает разрешения.

В этом примере итог будет:

```text
Read  ✓
Write ✓
```

То есть упрощённо:

```text
Role A permissions
        ∪
Role B permissions
        ∪
Role C permissions
        ↓
итоговые role permissions User
```

---

## 25. Практическое правило

Если хоть одна подходящая Role даёт обычный:

```text
Read ✓
```

другая Role с пустым `Read` его не отнимет.

То же относится к другим обычным permission types.

Поэтому нельзя построить такую модель:

```text
Role A → всё разрешает
Role B → должна что-то запретить
```

просто сняв галочку у Role B.

Для ограничений используются другие механизмы:

```text
If Owner
User Permission
Permission Level
controller permission logic
```

в зависимости от задачи.

---

## 26. Почему это удобно

Роли можно собирать как независимые способности.

Например:

```text
Request Operator
→ Read + Create + Write

Request Exporter
→ Export

Request Approver
→ Submit + Cancel
```

Одному человеку назначаем:

```text
Request Operator
```

другому:

```text
Request Operator
Request Exporter
```

третьему:

```text
Request Operator
Request Approver
```

Не нужно создавать три почти одинаковых огромных роли.

---

# Часть 7. Level

## 27. Что означает Level 0

Пока почти все наши permission rules выглядят так:

```text
Level = 0
```

Это основной уровень доступа к самому документу.

Проще говоря:

```text
Level 0
→ может ли роль вообще работать с документом?
```

Если на Level 0 нет нужного базового доступа, permission rules более высоких уровней сами по себе не дают полноценного доступа к документу.

---

## 28. А зачем Level 1, 2, 3…

Они нужны для ограничения отдельных полей.

Например:

```text
Request
├── Subject       Perm Level 0
├── Description   Perm Level 0
└── Internal Cost Perm Level 1
```

Тогда обычная роль может работать с Level 0, а специальная — ещё и с полями Level 1.

В текущем UI Role Permissions Manager для уровней выше 0 используются только права, связанные с доступом к полям:

```text
Read
Write
Mask
```

Это отдельная тема, поэтому полностью разбираем её в следующей главе.

---

# Часть 8. Standard permissions и Custom DocPerm

## 29. Откуда вообще берутся начальные permission rules

У стандартного DocType из App исходные permissions хранятся вместе с metadata приложения.

Упрощённо:

```text
App
└── Request DocType
    └── standard DocPerm rows
```

Это базовая permission model разработчика приложения.

---

## 30. Что происходит, когда мы меняем permissions на Site

Frappe не должен переписывать исходный файл установленного App при каждом клике администратора.

Поэтому для site-level настройки используется:

```text
Custom DocPerm
```

При переходе к кастомным permissions стандартные правила копируются в site-level набор, после чего изменения выполняются уже там.

Упрощённо:

```text
DocPerm из App
      ↓ первая кастомизация
Custom DocPerm на Site
      ↓
изменённые permissions этого Site
```

По смыслу это похоже на идею Customize Form:

```text
стандартное описание App
+
локальная настройка Site
```

Только здесь речь идёт именно о permissions.

---

## 31. Reset Permissions

Role Permissions Manager умеет вернуть стандартные permissions.

Перед сбросом интерфейс показывает стандартный набор правил.

После Reset локальная кастомизация permissions для DocType убирается, и система возвращается к базовым правилам.

Поэтому Reset — это не «снять все галочки».

Это именно:

```text
вернуться к стандартной permission model DocType
```

---

# Часть 9. Child Table

## 32. Почему Child DocType не настраивается здесь отдельно

Child Table не является самостоятельным рабочим документом.

Например:

```text
Request
└── Participants
    ├── row 1
    └── row 2
```

Пользователь получает доступ к child rows через parent `Request`.

Поэтому Role Permissions Manager v16 не предлагает Child DocType (`istable = 1`) в обычном списке Document Type.

Это продолжает правило из главы 08:

```text
Child Table
→ часть parent-документа
→ не отдельный объект доступа
```

---

# Часть 10. Чего Role Permissions Manager НЕ решает

## 33. Он отвечает на вопрос «что можно делать с DocType»

Например:

```text
Request Operator
→ может Read + Create + Write Request
```

Но этого недостаточно, чтобы ответить:

> какие именно Request он должен видеть?

Например:

```text
только Department A
только Site North
только определённого Customer
```

Для этого есть `User Permission` и связанные механизмы.

---

## 34. Три разных вопроса

Полезно сразу разделять:

```text
1. Что пользователь может делать?
   → Role Permission

2. Какие значения/документы ему доступны?
   → User Permission / Owner / Sharing / другие правила

3. Какие поля внутри документа доступны?
   → Permission Level
```

Если держать эти три вопроса раздельно, permission model становится намного понятнее.

---

# Часть 11. Как проверить, почему доступ работает не так

## 35. Не проверяй permissions под Administrator

`Administrator` в permission engine получает специальный обход обычных role permissions.

Поэтому тест:

```text
под Administrator всё открывается
```

ничего не доказывает.

Создай обычного тестового System User и назначь ему именно те роли, которые хочешь проверить.

---

## 36. Permission Inspector

В текущем Frappe v16 есть полезный штатный инструмент:

```text
Permission Inspector
```

Он позволяет указать:

```text
DocType
Document — необязательно
User
Permission Type
```

Например:

```text
DocType         = Request
Document        = REQ-0007
User            = anna@example.com
Permission Type = write
```

После проверки Inspector показывает debug-объяснение решения permission engine.

Это намного полезнее, чем гадать:

```text
почему кнопка пропала?
почему документ не открывается?
почему одна запись видна, а другая нет?
```

Когда permissions становятся сложнее, Permission Inspector стоит проверять одним из первых.

---

# Часть 12. Мини-практика

## 37. Создай две роли

Создай:

```text
Request Reader
Request Operator
```

---

## 38. Настрой Request Reader

В Role Permissions Manager:

```text
Document Type = Request
Role          = Request Reader
Level         = 0

Read ✓
```

Остальное пока не включай.

---

## 39. Настрой Request Operator

```text
Document Type = Request
Role          = Request Operator
Level         = 0

Read   ✓
Write  ✓
Create ✓
```

`Delete` оставь выключенным.

---

## 40. Проверь первым пользователем

Создай обычного тестового User:

```text
reader@example.com
```

Назначь:

```text
Request Reader
```

Проверь:

```text
может открыть Request       → да
может создать новую         → нет
может изменить существующую → нет
```

---

## 41. Проверь вторым пользователем

```text
operator@example.com
```

Role:

```text
Request Operator
```

Проверь:

```text
Read   → да
Create → да
Write  → да
Delete → нет
```

---

## 42. Теперь проверь сложение ролей

Назначь `reader@example.com` ещё одну роль, которая на `Request` даёт только:

```text
Export ✓
```

Ожидаемая идея:

```text
Request Reader → Read
Export Role    → Export

итого          → Read + Export
```

Пустые галочки второй роли не должны «отнять» Read первой.

---

## 43. Проверь Only if Creator

Для тестовой роли настрой:

```text
Read  ✓
Write ✓
Only if Creator ✓
```

Создай одну Request под первым пользователем и вторую — под другим.

Сравни доступ.

Смотри именно на системное поле:

```text
owner
```

а не на Assignment.

---

# Частые ошибки

## 44. «Снял галочку — значит запретил»

Нет.

Пустая permission в одной роли не является отрицательным deny против разрешения другой роли.

Всегда смотри на **все роли User вместе**.

---

## 45. «Write значит и Read»

Не рассчитывай на это.

Для обычного редактора явно выдавай:

```text
Read + Write
```

---

## 46. «Create значит потом можно редактировать»

Тоже нет.

`Create` и `Write` — разные действия.

---

## 47. «Only if Creator — это назначенный исполнитель»

Нет.

Это:

```text
owner == current user
```

Assignment — отдельный механизм.

---

## 48. «Нужно дать оператору доступ только к Department A — настрою Role Permission Manager»

Role Permission Manager отвечает прежде всего на вопрос **что можно делать**.

Ограничение конкретными Department — задача `User Permission`, которую разберём в главе 20.

---

## 49. «Настрою permissions прямо для Child Table»

Обычная Child Table следует доступу parent-документа.

Не нужно строить для неё независимую role model.

---

## 50. «Проверю под Administrator»

Так можно пропустить почти любую ошибку permission model.

Проверяй под обычным User.

---

# Что запомнить

1. **Role Permissions Manager связывает Role с действиями над DocType.**
2. `Read`, `Write`, `Create`, `Delete` — отдельные permissions.
3. `Select` позволяет выбирать документ в ссылках без полноценного Read; Read при этом покрывает Select-проверку.
4. `Submit`, `Cancel`, `Amend` имеют смысл только у Submittable DocType.
5. Права нескольких Roles **складываются как разрешения**.
6. Пустая галочка в одной Role не отменяет разрешение другой Role.
7. `Only if Creator` работает через системное поле `owner`.
8. `Level 0` — базовый document-level доступ; более высокие Levels относятся к полям.
9. Изменённые на Site стандартные permissions хранятся как `Custom DocPerm`, а Reset возвращает стандартные правила.
10. Если результат непонятен, используй обычного тестового User и `Permission Inspector`.

---

# Контрольные вопросы

1. Что связывает Role Permissions Manager?
2. Чем `Read` отличается от `Write`?
3. Даёт ли `Create` автоматически `Write`?
4. Чем `Select` отличается от `Read`?
5. Почему у обычного DocType нет смысла выдавать Submit?
6. Что означает `Only if Creator`?
7. Проверяет ли он Assigned To?
8. Что произойдёт, если одна Role даёт Read, а другая Role Read не даёт?
9. Зачем нужен Level 0?
10. Чем `DocPerm` отличается от `Custom DocPerm`?
11. Почему Child Table не получает отдельную обычную permission model?
12. Каким инструментом удобно диагностировать конкретную проверку доступа?

Если на эти вопросы можно ответить без подсказки, базовая логика Role Permissions уже понятна.

---

# Официальные источники

- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [Role Permissions Manager — source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/page/permission_manager/permission_manager.py)
- [Role Permissions Manager UI — source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/page/permission_manager/permission_manager.js)
- [Permission Manager Help — source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/page/permission_manager/permission_manager_help.html)
- [Permission engine — source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py)
- [DocPerm metadata — source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/docperm/docperm.json)
- [Custom DocPerm metadata — source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/custom_docperm/custom_docperm.json)
- [Permission Inspector — source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/permission_inspector/permission_inspector.py)

Следующая глава: **19. Permission Level**.