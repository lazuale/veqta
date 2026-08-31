# Лабораторная 20. User Permission

## Цель

Ограничить пользователя не всем DocType целиком, а значением Link.

## Подготовка

Создай простой DocType:

```text
Training Area
```

Поле:

```text
Area Name  Data Mandatory
```

Создай Documents:

```text
North
South
```

В `Request` добавь:

```text
Area  Link → Training Area
```

Распредели существующие Request между North и South.

## Настрой User Permission

Для `student.user@example.test` создай User Permission:

```text
Allow: Training Area
For Value: North
```

Убедись, что Link field `Area` участвует в permission chain и не отключён флагами Ignore User Permissions.

## Проверь

Под Training User открой Request List и сравни доступные записи/варианты Area.

Под Training Manager без такого ограничения должны быть доступны обе Area при достаточных role permissions.

## Эксперимент

Поменяй User Permission с North на South и перезайди. Набор доступных данных должен измениться.

## Намеренная ошибка

Включи `Ignore User Permissions` у Link `Area` или другой релевантной настройки только на время эксперимента и посмотри, как меняется поведение выбора. После этого верни безопасное состояние.

## Проверка себя

Почему Role Permission отвечает на вопрос «что можно делать с DocType», а User Permission — «какие связанные значения/документы доступны конкретному User»?

## Состояние после лабораторной

Верни Training User ограничение на `North`.
