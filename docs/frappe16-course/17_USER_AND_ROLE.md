# 17. User и Role

До этого мы почти не думали о том, **кто именно** работает с системой.

Теперь начинается блок про права доступа.

Во Frappe база очень простая:

```text
User
  ↓ получает
Role
  ↓ участвует в
Permissions DocType
```

То есть пользователь сам по себе не получает доступ к данным просто потому, что он создан.

И роль сама по себе тоже не означает «можно всё».

Проверено: **2026-08-30**.

---

## 1. Начнём с обычного примера

Представим DocType `Request`.

Есть три человека:

```text
Анна   → только смотрит Request
Борис  → создаёт и редактирует Request
Ирина  → управляет настройками системы
```

Можно было бы вручную выдавать права каждому человеку отдельно.

Но это быстро превратилось бы в хаос.

Вместо этого создаём роли:

```text
Request Reader
Request Operator
System Manager
```

А пользователям назначаем нужные роли:

```text
Анна
└── Request Reader

Борис
└── Request Operator

Ирина
└── System Manager
```

Дальше уже для каждой роли задаются права на DocType.

Например:

```text
Request Reader
└── Request: Read

Request Operator
└── Request: Read + Create + Write
```

Вот это и есть базовая модель доступа Frappe.

---

# Часть 1. User

## 2. Что такое User

`User` — это учётная запись человека или технического пользователя, который может войти в систему и выполнять разрешённые действия.

У обычного пользователя есть, например:

```text
Email
First Name
Last Name
Language
Time Zone
User Type
Roles
Password / Login settings
Default Workspace
```

Для обычных пользователей Frappe использует email как системное `name` документа User.

Например:

```text
email = anna@example.com
name  = anna@example.com
```

Это важно, потому что в Link-полях на `User` обычно хранится именно это значение.

---

## 3. Enabled

У пользователя есть флаг:

```text
Enabled
```

Если пользователь отключён, он больше не должен использовать учётную запись для нормальной работы в системе.

Это правильнее, чем удалять пользователя, который уже участвовал в документах.

Почему?

Потому что старые документы могут содержать:

```text
owner
modified_by
Assigned To
Comments
Shares
```

ссылки на этого User.

Поэтому бывшего сотрудника обычно **отключают**, а не стирают из истории.

---

## 4. System User и Website User

В стандартной модели Frappe есть два особенно важных типа пользователя:

```text
System User
Website User
```

### System User

Это пользователь Desk.

То есть он работает во внутреннем интерфейсе Frappe:

```text
/desk
```

и может видеть Workspaces, Lists, Forms и другие Desk views, если права это разрешают.

### Website User

Это пользователь, которому не нужен обычный Desk.

Он предназначен прежде всего для website / portal-сценариев.

Простая картинка:

```text
System User
└── внутренний Desk

Website User
└── website / portal
```

Website User — это не просто «System User с меньшими правами».

Это другой режим использования интерфейса.

---

## 5. Откуда берётся System User

Здесь в v16 есть полезная деталь.

У Role есть флаг:

```text
Desk Access
```

Для обычных стандартных типов пользователя Frappe проверяет назначенные роли.

Если хотя бы одна из них имеет `Desk Access`, пользователь становится `System User`.

Если таких ролей нет — `Website User`.

Упрощённо:

```text
User
└── имеет Role с Desk Access?
        ├── да  → System User
        └── нет → Website User
```

Поэтому роль влияет не только на permissions DocType, но и на то, нужен ли пользователю Desk.

---

# Часть 2. Role

## 6. Что такое Role

`Role` — это именованная роль пользователя в системе.

Например:

```text
Request Reader
Request Operator
Request Manager
```

Самое главное:

> Role не содержит магического готового доступа ко всему.

Role становится полезной, когда на неё ссылаются permission rules DocType.

Например:

```text
Role: Request Operator

Request permissions:
├── Read
├── Create
└── Write
```

То есть логика выглядит так:

```text
User
  ↓
Role
  ↓
DocType Permission
  ↓
разрешённое действие
```

---

## 7. Одна роль может работать с разными DocType

Например роль:

```text
Request Operator
```

может иметь:

```text
Request
├── Read
├── Create
└── Write

Department
└── Read
```

Это нормально.

Роль описывает рабочую функцию, а не один конкретный DocType.

---

## 8. У пользователя может быть несколько ролей

Например:

```text
Борис
├── Request Operator
└── Report Viewer
```

Тогда при вычислении role permissions Frappe учитывает подходящие permission rows всех его ролей.

На базовом уровне это можно воспринимать как объединение разрешений.

Например:

```text
Request Operator → Read + Write
Report Viewer    → Report

итого           → Read + Write + Report
```

Позже увидим, что сверху могут накладываться дополнительные ограничения:

```text
Permission Level
User Permission
If Owner
Sharing
controller permission logic
```

Но пока достаточно помнить базу: **User может иметь несколько Roles**.

---

## 9. Где назначаются роли

Открой:

```text
User
```

и раздел с ролями.

Там можно назначить пользователю нужные роли.

Например:

```text
anna@example.com

Roles
☑ Request Reader
☐ Request Operator
☐ System Manager
```

После сохранения Frappe будет использовать эти роли при проверках доступа.

---

## 10. Не создавай роль на каждого человека

Плохой вариант:

```text
Anna Role
Boris Role
Irina Role
```

Если роли повторяют имена людей, значит модель доступа почти наверняка построена неудачно.

Лучше описывать функцию:

```text
Request Reader
Request Operator
Request Manager
Auditor
```

Почему это удобнее?

Потому что человек меняется, а рабочая функция остаётся.

Сегодня:

```text
Борис → Request Operator
```

завтра:

```text
Олег → Request Operator
```

а permission model менять не пришлось.

---

## 11. Role не равна должности

Иногда они совпадают, но это не обязательное правило.

Например должность человека:

```text
Analyst
```

а в системе ему могут понадобиться роли:

```text
Request Operator
Report Viewer
Document Exporter
```

Поэтому лучше мыслить так:

```text
должность
→ организационная реальность

Role
→ набор системных возможностей
```

Не нужно пытаться один в один копировать штатное расписание в Roles.

---

## 12. Desk Access у Role

В `Role` есть флаг:

```text
Desk Access
```

Если роль предназначена для внутреннего Desk-пользователя, обычно он включён.

Пример:

```text
Request Operator
Desk Access = 1
```

Если такая роль назначена пользователю, Frappe считает, что ему нужен системный Desk-доступ.

Для чисто portal-роли Desk Access обычно не требуется.

---

## 13. Disabled Role

У Role есть:

```text
Disabled
```

В metadata v16 прямо указано: если роль отключить, она удаляется у пользователей.

То есть это не просто визуальная галочка.

Если роль больше не должна использоваться, её можно отключить.

Но перед этим нужно понимать последствия для доступа пользователей.

---

# Часть 3. Автоматические роли

## 14. Есть роли, которые Frappe добавляет сам

Не все роли нужно вручную назначать пользователю.

В v16 есть специальные автоматические роли:

```text
Guest
All
Desk User
Administrator
```

Разберём их без лишней магии.

---

## 15. Guest

`Guest` используется для неавторизованного пользователя.

То есть человек открыл сайт, но не вошёл в систему.

Упрощённо:

```text
не вошёл
→ Guest
```

Permissions для Guest нужно выдавать очень осторожно, потому что это фактически публичный доступ.

---

## 16. All

`All` применяется к зарегистрированным пользователям.

В том числе к Website User.

Она удобна, если доступ должен быть у любого вошедшего пользователя.

Но это широкая роль, поэтому использовать её для чувствительных данных бездумно не стоит.

---

## 17. Desk User

`Desk User` автоматически получает `System User`.

То есть вручную назначать каждому внутреннему пользователю отдельную роль `Desk User` обычно не требуется.

Логика:

```text
System User
→ автоматически имеет Desk User
```

---

## 18. Administrator

`Administrator` — специальный системный пользователь Frappe.

Он не является обычным пользователем с просто очень большим набором Role.

В permission engine для него есть специальное правило:

```text
user == Administrator
→ разрешить всё
```

Поэтому Administrator нельзя использовать как образец нормальной permission model.

Если под Administrator всё работает, это ещё ничего не доказывает.

Всегда проверяй доступ под обычным тестовым пользователем.

---

# Часть 4. Role Profile

## 19. Что делать, если одинаковый набор ролей нужен многим людям

Допустим, каждому оператору нужны:

```text
Request Operator
Report Viewer
Department Reader
```

Можно вручную ставить три галочки каждому User.

Но если операторов много, удобнее создать:

```text
Role Profile: Request Operator Profile
```

и положить в него эти роли.

Получается:

```text
Role Profile
├── Request Operator
├── Report Viewer
└── Department Reader
```

А уже Role Profile назначается пользователям.

---

## 20. Role Profile не заменяет Role

Это важная граница.

`Role Profile` — просто удобная упаковка нескольких ролей.

Permission rules всё равно работают с обычными Roles.

```text
Role Profile
      ↓ разворачивается в
Roles
      ↓
DocType Permissions
```

В v16 User поддерживает несколько Role Profile через поле `role_profiles`.

Старое одиночное поле `role_profile_name` в коде v16 уже помечено как deprecated.

Новичку достаточно использовать текущий интерфейс и не строить решения вокруг старого поля.

---

# Часть 5. Что Role ещё НЕ решает

## 21. Role не отвечает на вопрос «какие именно документы?»

Допустим:

```text
Request Operator
→ Read Request
```

Это пока означает право читать DocType `Request` в целом.

Но может понадобиться:

```text
Анна видит Request только Department A
Борис видит Request только Department B
```

Это уже задача следующего уровня — `User Permission` и других механизмов ограничения конкретных документов.

---

## 22. Role не ограничивает отдельные поля сама по себе

Например:

```text
Request
├── Subject
├── Department
└── Internal Cost
```

Если нужно:

```text
Operator видит Subject и Department
Manager дополнительно видит Internal Cost
```

для этого понадобится `Permission Level`.

Он будет отдельной главой.

---

## 23. Role не равна Assignment

Если документ назначен Борису через `Assign To`, это не означает автоматически:

```text
Борис получил Read / Write
```

Assignment отвечает на вопрос:

> Кто должен этим заняться?

Permissions отвечают на другой вопрос:

> Имеет ли этот пользователь право работать с таким документом?

Это два разных механизма.

---

## 24. Role не равна видимости Workspace

Можно скрыть Workspace или Module из навигации.

Но скрытый пункт меню — это ещё не защита данных.

Настоящий доступ должен контролироваться permission system.

Никогда не рассчитывай на логику:

```text
не видно кнопки
→ значит доступа нет
```

Это неверно.

---

# Часть 6. Как Frappe думает о доступе

## 25. Упрощённая цепочка

Когда пользователь пытается открыть документ:

```text
User
  ↓
какие у него Roles?
  ↓
есть ли у этих Roles нужное право на DocType?
  ↓
есть ли дополнительные ограничения?
  ↓
можно / нельзя
```

Позже эта схема станет подробнее:

```text
User
  ↓
Roles
  ↓
Role Permissions
  ↓
Permission Level
  ↓
User Permissions
  ↓
Owner / Sharing
  ↓
server-side permission logic
  ↓
итоговый доступ
```

Не пытайся запомнить всё сейчас.

Нам важно двигаться по слоям.

---

## 26. Какие действия вообще можно разрешать

В permission system Frappe есть стандартные действия вроде:

```text
Select
Read
Write
Create
Delete
Submit
Cancel
Amend
Print
Email
Report
Import
Export
Share
```

В этой главе их подробно не разбираем.

Следующая глава будет именно про `Role Permission Manager`.

---

# Часть 7. Хорошая модель ролей

## 27. Начинай с рабочих возможностей

Пусть есть `Request`.

Разумный старт:

```text
Request Reader
Request Operator
Request Manager
```

А не:

```text
Role 1
Role 2
Department A User
Anna Access
Super Request Worker
```

Хорошее имя роли должно без объяснений примерно отвечать на вопрос:

> Что этот пользователь делает в системе?

---

## 28. Не плодить роли заранее

Не нужно сразу делать:

```text
Request Reader Level 1
Request Reader Level 2
Request Reader Department A
Request Reader Department B
Request Reader Temporary
```

Сначала проверь, нельзя ли различия выразить другими штатными механизмами:

```text
Role
Permission Level
User Permission
Owner
Sharing
```

Иначе через полгода никто не поймёт, зачем существуют 60 почти одинаковых ролей.

---

## 29. Пример нормальной начальной схемы

```text
User: anna@example.com
└── Role: Request Reader

User: boris@example.com
├── Role: Request Operator
└── Role: Report Viewer

User: irina@example.com
└── Role: Request Manager
```

А permissions:

```text
Request Reader
└── Request: Read

Request Operator
└── Request: Read + Create + Write

Request Manager
└── Request: Read + Create + Write + Delete

Report Viewer
└── Request: Report
```

Это уже понятная система.

---

# Часть 8. Мини-практика

## 30. Создай три роли

Через Awesomebar открой:

```text
Role
```

Создай:

```text
Training Reader
Training Operator
Training Manager
```

Для внутренних ролей оставь `Desk Access` включённым.

---

## 31. Создай тестового User

Создай обычного тестового пользователя, например:

```text
trainee@example.com
```

Назначь ему:

```text
Training Reader
```

Посмотри, что пользователь стал System User и может войти в Desk.

Но пока не удивляйся, если он почти ничего полезного там не видит.

Мы ещё не выдали роли permission rules на наши DocType.

Именно это будет следующим шагом.

---

## 32. Добавь вторую роль

Назначь пользователю ещё:

```text
Training Operator
```

Пока визуально это может почти ничего не изменить.

И это полезный урок:

> Название Role само по себе не создаёт доступ.

Нужно ещё связать Role с permissions конкретного DocType.

---

# Что запомнить

1. **User** — учётная запись пользователя.
2. Для обычного User системный `name` — его email.
3. **System User** работает в Desk; **Website User** предназначен для website/portal-сценария.
4. Роль с `Desk Access` делает обычного пользователя System User.
5. **Role** — не готовое право, а участник permission model.
6. У одного User может быть несколько Roles.
7. `Role Profile` — удобная группа ролей, а не отдельный механизм permissions.
8. `Guest`, `All`, `Desk User`, `Administrator` — специальные автоматические роли.
9. Administrator обходит обычную role permission проверку, поэтому тестировать права под ним бессмысленно.
10. Скрытая кнопка или Workspace не заменяют настоящих permissions.

---

# Контрольные вопросы

1. Чем User отличается от Role?
2. Может ли User иметь несколько Roles?
3. Даёт ли новая пустая Role какой-либо доступ сама по себе?
4. Чем System User отличается от Website User?
5. Что делает флаг `Desk Access` у Role?
6. Нужно ли вручную выдавать каждому System User роль `Desk User`?
7. Для чего нужен Role Profile?
8. Почему Role Profile не заменяет обычные Roles?
9. Почему нельзя проверять permission model только под Administrator?
10. Почему Assignment и Permissions — разные вещи?

---

# Официальные источники

- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [Frappe v16 — User metadata](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user/user.json)
- [Frappe v16 — User controller](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user/user.py)
- [Frappe v16 — Role metadata](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/role/role.json)
- [Frappe v16 — Permission engine](https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py)
- [Frappe v16 — Role Profile](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/role_profile/role_profile.json)

Следующая глава: **Role Permission Manager**.
