# Лабораторная 17. User и Role

## Что уже должно быть готово

Блок C завершён.

На стенде уже есть рабочий `Request` и `Training Workspace`, но **ещё нет**:

```text
Training User
Training Manager
student.user@example.test
student.manager@example.test
```

Работаем под `Administrator`, пока отдельно не указано обратное.

---

## Что сейчас получим

Оставим на стенде:

```text
Role: Training User
  Desk Access = ✓

Role: Training Manager
  Desk Access = ✓

User: student.user@example.test
  Role: Training User
  User Type: System User

User: student.manager@example.test
  Roles:
    Training User
    Training Manager
  User Type: System User
```

Оба пользователя получат рабочий пароль для локального учебного Site.

---

# Часть 1. Создай роли

## 1. Создай `Training User`

В Desk найди:

```text
Role
```

Создай:

```text
Role Name:   Training User
Desk Access: ✓
Disabled:    ☐
```

Сохрани.

---

## 2. Создай `Training Manager`

Аналогично:

```text
Role Name:   Training Manager
Desk Access: ✓
Disabled:    ☐
```

Сохрани.

Пока эти Roles **не должны** давать доступ к `Request`: permission rules мы ещё не создавали.

---

# Часть 2. Создай обычного учебного User

## 3. Создай `student.user@example.test`

Открой:

```text
User
→ Add User
```

Заполни:

```text
Email:      student.user@example.test
First Name: Training User
Enabled:    ✓
```

Обязательно отключи:

```text
Send Welcome Email = ☐
```

В Roles назначь:

```text
Training User
```

Сохрани User.

После сохранения проверь:

```text
User Type = System User
```

Причина — у назначенной Role включён `Desk Access`.

---

## 4. Задай пароль

Открой сохранённого User повторно.

В секции смены пароля найди:

```text
Set New Password
```

Для **этого disposable локального стенда** используй:

```text
FrappeCourse!2026
```

Сохрани.

Этот пароль существует только для учебного `learn.localhost`.

Не используй его для реальных аккаунтов.

---

# Часть 3. Создай менеджера

## 5. Создай `student.manager@example.test`

Создай второго User:

```text
Email:      student.manager@example.test
First Name: Training Manager
Enabled:    ✓
Send Welcome Email: ☐
```

Назначь **две** роли:

```text
Training User
Training Manager
```

Сохрани.

Проверь:

```text
User Type = System User
```

Затем задай тот же учебный пароль:

```text
FrappeCourse!2026
```

и снова сохрани.

---

# Часть 4. Проверь реальный вход

## 6. Войди как `student.user@example.test`

Открой приватное/incognito окно браузера.

Перейди:

```text
http://learn.localhost:8000/app
```

Войди:

```text
User:     student.user@example.test
Password: FrappeCourse!2026
```

Ожидается:

```text
login успешен
внутренний Desk открывается
```

Найди через поиск:

```text
Request
```

На этом этапе `Request` может быть недоступен или отсутствовать среди доступных объектов.

Это **нормально**.

Мы доказали только:

```text
User + Desk Role
→ можно войти в Desk
```

Но ещё не настроили:

```text
Role → Request permissions
```

---

## 7. Войди как менеджер

Выйди из первого User или используй второе приватное окно.

Войди:

```text
User:     student.manager@example.test
Password: FrappeCourse!2026
```

Ожидается тот же базовый результат:

```text
System User
→ /app доступен
```

Но наличие `Training Manager` само по себе пока также не должно магически выдавать `Request`.

---

# Намеренная поломка — убери Desk Access

Теперь возвращаемся под `Administrator`.

## 8. Выключи Desk Access только у `Training User`

Открой Role:

```text
Training User
```

временно установи:

```text
Desk Access = ☐
```

Сохрани Role.

---

## 9. Проверь User Types

Открой:

```text
student.user@example.test
```

Ожидается:

```text
User Type = Website User
```

Почему?

У него единственная ручная Role:

```text
Training User
```

и она больше не даёт Desk Access.

Теперь открой:

```text
student.manager@example.test
```

Ожидается:

```text
User Type = System User
```

Потому что у него остаётся:

```text
Training Manager
Desk Access = ✓
```

То есть второй User наглядно показывает: Frappe учитывает **весь набор его Roles**.

---

## 10. Проверь поведение входа

Попробуй снова открыть под первым пользователем:

```text
http://learn.localhost:8000/app
```

Он больше не должен вести себя как обычный внутренний System User.

Сессия также могла быть сброшена при смене User Type — это ожидаемо.

Менеджер при этом должен сохранять Desk-доступ.

---

# Восстановление

## 11. Верни `Training User`

Под `Administrator` открой Role:

```text
Training User
```

верни:

```text
Desk Access = ✓
```

Сохрани.

Проверь обоих Users:

```text
student.user@example.test
→ System User

student.manager@example.test
→ System User
```

Если первый пользователь был разлогинен, войди снова по паролю курса и убедись, что `/app` снова открывается.

---

## Проверка себя

Ответь без подсказки.

1. Чем `User` отличается от `Role`?
2. Может ли один User иметь несколько Roles?
3. Может ли одна Role быть у нескольких Users?
4. Что делает `Desk Access`?
5. Почему после его отключения обычный User стал Website User, а менеджер остался System User?
6. Даёт ли создание `Training User` автоматически `Read` на `Request`?
7. Почему дальше нельзя проверять permissions только под `Administrator`?
8. Какой внутренний route используется в курсе: `/app` или `/desk`?

---

## Состояние стенда после лабораторной

Роли:

```text
Training User
  Desk Access: ✓
  Disabled:    ☐

Training Manager
  Desk Access: ✓
  Disabled:    ☐
```

Users:

```text
student.user@example.test
  Enabled:   ✓
  User Type: System User
  Roles:
    Training User

student.manager@example.test
  Enabled:   ✓
  User Type: System User
  Roles:
    Training User
    Training Manager
```

Оба могут войти в:

```text
http://learn.localhost:8000/app
```

с локальным учебным паролем.

`Request` permissions для этих ролей **ещё не настроены**.

Это точное входное состояние [**главы 18**](../18_ROLE_PERMISSION_MANAGER.md).
