# Лабораторная 17. User и Role

## Цель

Создать отдельные учебные личности и роли, чтобы все следующие главы permissions проверять не под Administrator.

## Создай роли

```text
Training User
Training Manager
```

## Создай пользователей

Используй учебные адреса, не реальные рабочие:

```text
student.user@example.test
student.manager@example.test
```

Назначь:

```text
student.user@example.test    → Training User
student.manager@example.test → Training User + Training Manager
```

Если Frappe требует email-доставку при создании, отключи отправку welcome email для учебных Users.

## Проверь

Открой private/incognito окно и войди поочерёдно под каждым пользователем.

Посмотри:

```text
какие Workspaces видны
какие DocTypes находятся через Awesome Bar
какие действия доступны
```

Пока `Request` может быть недоступен — это нормально: permission мы ещё не дали.

## Эксперимент

Временно сними `Training Manager` со второго пользователя, перезайди и сравни `frappe.get_roles()` через browser console или доступный UI контекст. Затем верни роль.

## Намеренная ошибка

Попробуй считать `User` и `Role` одним и тем же. Назначь одну роль двум Users и убедись: роль — набор полномочий, User — конкретная учётная запись.

## Проверка себя

Ответь:

- может ли User иметь несколько Roles;
- может ли одна Role быть у многих Users;
- даёт ли создание Role автоматически доступ к Request.

## Состояние после лабораторной

Оба учебных User и обе Role оставить.
