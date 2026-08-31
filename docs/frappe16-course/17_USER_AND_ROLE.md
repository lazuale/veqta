# 17. User и Role

Блок C закончен: у нас уже есть рабочий `Request`, несколько представлений, Workspace и данные.

До сих пор почти всё проверялось под `Administrator`.

Теперь начинается блок D — **права доступа**.

Первый вопрос здесь не «какую галочку поставить?», а:

> кто вообще входит в систему и какие роли ему назначены?

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

К началу главы существуют:

```text
Site: learn.localhost
App:  training

Request
Training Category
Training Settings
Training Workspace
```

Учебных ролей и отдельных учебных пользователей ещё нет.

Их создаём впервые в этой главе.

---

# User и Role — разные сущности

Самая простая модель:

```text
User
  ↓ получает
Role
  ↓ используется в
DocType permissions
```

Например:

```text
student.user@example.test
└── Training User

student.manager@example.test
├── Training User
└── Training Manager
```

`User` — конкретная учётная запись.

`Role` — именованная системная функция.

Одна Role может быть у многих Users, а один User может иметь несколько Roles.

---

## Role сама по себе ещё не даёт доступ к Request

Создать:

```text
Training User
```

недостаточно.

Пока для этой роли не настроены permissions на `Request`, роль остаётся только именем.

Следующая глава как раз свяжет:

```text
Training User
→ Request
→ Read / Create / Write
```

Поэтому после лабораторной 17 ситуация:

```text
пользователь входит в Desk
но Request ещё может быть недоступен
```

будет правильной.

---

# User

## Что хранит User

`User` — системный DocType Frappe.

Для обычного пользователя его системный `name` совпадает с email.

Например:

```text
Email: student.user@example.test
name:  student.user@example.test
```

Это значение затем используется в Link-полях на `User`, в `owner`, Assignments, Shares и других механизмах Framework.

---

## Enabled

У пользователя есть:

```text
Enabled
```

Отключённый User не должен продолжать обычную работу в системе.

Для реальной системы пользователя, который уже участвовал в документах, обычно логичнее **disable**, чем удалять: старые Documents всё равно могут ссылаться на него через системные поля и журналы.

В учебном стенде оба наших пользователя оставляем включёнными.

---

# System User и Website User

Для текущего курса важны два стандартных типа:

```text
System User
Website User
```

### System User

Это внутренний пользователь Desk.

Канонический путь нашего стенда:

```text
http://learn.localhost:8000/app
```

Именно System User работает с Workspace, List View, Form View и другими Desk-инструментами, если permissions позволяют.

### Website User

Это пользователь website/portal-сценариев без обычного внутреннего Desk-доступа.

До website и portal мы дойдём значительно позже.

---

# Как Role влияет на User Type

У `Role` в `v16.32.0` есть флаг:

```text
Desk Access
```

По умолчанию для новой Role он включён.

Для стандартных типов пользователей Frappe при сохранении User проверяет его роли:

```text
есть хотя бы одна Role с Desk Access?
        ├── да  → System User
        └── нет → Website User
```

Это не просто визуальная договорённость.

Controller `User` в `v16.32.0` устанавливает `user_type` именно на основании Desk Access назначенных ролей.

---

## Что будет, если изменить Desk Access у Role

Controller `Role` в `v16.32.0` делает ещё одну полезную вещь.

Если изменить:

```text
Desk Access
```

Framework повторно вычисляет User Type у пользователей с этой ролью.

Поэтому в лабораторной мы сможем получить настоящую контролируемую поломку:

```text
Training User
Desk Access = 0
```

У пользователя, у которого нет другой Desk-role:

```text
student.user@example.test
→ Website User
```

А менеджер, у которого останется:

```text
Training Manager
Desk Access = 1
```

останется System User.

После этого вернём настройку обратно.

---

# Пароль учебного User

В `User` v16 есть поле:

```text
Set New Password
```

Если при создании отключить:

```text
Send Welcome Email
```

то на локальном учебном Site можно сохранить User, затем задать ему пароль вручную.

Это именно то, что сделаем в лабораторной.

Важно различать:

```text
учебный пароль на disposable learn.localhost
≠
пароль реальной учётной записи
```

Пароль курса не нужно переиспользовать нигде вне этого локального стенда.

---

# Несколько Roles у одного User

Наш менеджер получит:

```text
Training User
Training Manager
```

В permission engine Frappe разрешения подходящих ролей обычно **складываются**.

Если одна роль разрешает действие, отсутствие такой галочки в другой роли не является отдельным `DENY`.

Позже это будет видно на `Request`:

```text
Training User
→ базовая работа

Training Manager
→ дополнительные возможности
```

У менеджера будут возможности обеих ролей.

---

# Автоматические роли

В permission engine `v16.32.0` есть специальные автоматические роли:

```text
Guest
All
Desk User
Administrator
```

Для первого прохода достаточно понимать следующее.

### Guest

Неавторизованный пользователь.

### All

Автоматическая общая роль зарегистрированных пользователей.

### Desk User

Автоматически участвует у System User.

### Administrator

Специальный суперпользователь.

В `frappe.permissions.has_permission()` для него есть прямое правило:

```text
Administrator
→ allow
```

Поэтому проверка:

> под Administrator всё работает

не доказывает правильность обычной permission model.

Начиная с этого блока, ключевые проверки выполняем под учебными Users.

---

# Role Profile — что это такое

Если многим пользователям нужен одинаковый набор ролей, Frappe поддерживает `Role Profile`.

Упрощённо:

```text
Role Profile
├── Role A
├── Role B
└── Role C
```

Это удобная упаковка Roles, а не новый тип permission.

В `v16.32.0` User поддерживает несколько Role Profiles через поле:

```text
role_profiles
```

В этой лабораторной Profile не нужен: у нас всего две роли и два пользователя.

---

# Почему роли лучше называть по функции

Хорошо:

```text
Training User
Training Manager
```

Плохо:

```text
Ivan Role
Anna Role
```

Role должна описывать системную функцию, которую завтра можно назначить другому человеку.

Она не обязана один в один повторять должность из штатного расписания.

---

# Что произойдёт в лабораторной

Ты:

1. создашь `Training User` и `Training Manager`;
2. убедишься, что у обеих включён `Desk Access`;
3. создашь два учебных User;
4. отключишь им welcome email;
5. назначишь роли;
6. задашь локальный учебный пароль;
7. войдёшь каждым пользователем через `/app`;
8. увидишь, что вход в Desk и доступ к `Request` — разные вопросы;
9. временно выключишь Desk Access у `Training User`;
10. увидишь переход одного пользователя в `Website User`;
11. полностью восстановишь обе роли и оба User как System User.

---

# Что запомнить

1. `User` — конкретная учётная запись.
2. `Role` — системная функция, назначаемая Users.
3. User может иметь несколько Roles.
4. Одна Role может быть назначена многим Users.
5. Role с `Desk Access` делает стандартного пользователя кандидатом на `System User`.
6. Role сама по себе ещё не выдаёт доступ к `Request`.
7. `Administrator` нельзя использовать как единственную проверку обычных permissions.
8. Для внутреннего интерфейса курса используем `/app`.

---

## Проверенные исходники v16.32.0

- [Role metadata](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/role/role.json)
- [Role controller](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/role/role.py)
- [User metadata](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/user/user.json)
- [User controller](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/user/user.py)
- [Permission engine](https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py)

Теперь выполни [**лабораторную 17**](labs/17_USER_AND_ROLE_LAB.md).

После неё переходи к [**18. Role Permissions Manager**](18_ROLE_PERMISSION_MANAGER.md).
