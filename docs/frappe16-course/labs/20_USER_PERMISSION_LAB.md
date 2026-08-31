# Лабораторная 20. User Permission

## Цель

Ограничить пользователя не всем DocType целиком, а конкретным значением связанного Link.

## Подготовка

Создай Standard DocType:

```text
Training Area
```

Поле:

```text
Area Name  Data Mandatory
```

Дай `Training User` и `Training Manager` как минимум `Read` на `Training Area`, иначе Link сам по себе не будет доступен учебным пользователям.

Создай Documents:

```text
North
South
```

В `Request` добавь:

```text
Area  Link → Training Area
```

Распредели существующие Request между `North` и `South`.

## Настрой User Permission

Для:

```text
student.user@example.test
```

создай:

```text
Allow: Training Area
For Value: North
```

У Link `Area` не должен быть включён `Ignore User Permissions`.

## Проверь

Полностью перезайди под `student.user@example.test`.

Проверь:

1. какие Request видны в List View;
2. какие значения предлагает Link `Area`;
3. открывается ли напрямую Request из `South`.

Затем войди под `student.manager@example.test` без такого User Permission и сравни.

## Эксперимент

Поменяй User Permission с `North` на `South`, перезайди и повтори те же три проверки.

После опыта верни `North`.

## Намеренная поломка

Временно включи у поля `Area`:

```text
Ignore User Permissions = 1
```

и сравни варианты Link.

Важно: этот флаг относится к применению User Permissions для данного Link; он не превращает пользователя в администратора и не отменяет всю permission model.

После опыта выключи флаг.

## Проверка себя

Объясни разницу:

```text
Role Permission
→ что Role вообще может делать с DocType

User Permission
→ какими связанными значениями ограничен конкретный User
```

## Состояние после лабораторной

```text
Training User → User Permission Training Area = North
Training Manager → без такого ограничения
Area → Ignore User Permissions выключен
```
