# Лабораторная 21. Owner и Sharing

## Цель

Увидеть два разных механизма: ownership и явный Share.

## Подготовка

Настрой для `Training User` на Request режим `If Owner` для Write или Read/Write в зависимости от сценария главы.

Создай один Request под `student.user@example.test`, второй — под `student.manager@example.test`.

## Проверь owner restriction

Под Training User:

- свой документ доступен по правилам owner;
- чужой документ ограничен.

## Share

Под пользователем с правом Share или Administrator открой чужой Request и поделись им с `student.user@example.test`.

Выдай только `Read`, затем проверь.

После этого добавь `Write` и сравни.

## Unshare

Удали Share и снова проверь доступ.

## Эксперимент

В списке `DocShare` найди созданную запись Share и сопоставь её с тем, что видел пользователь.

## Намеренная ошибка

Не считай, что смена `owner` и Share — одно и то же. Сравни metadata документа до и после Share: owner остаётся прежним.

## Проверка себя

Ответь:

- кто является owner;
- что добавляет Share;
- исчезает ли ownership после Share;
- можно ли Share дать только Read.

## Состояние после лабораторной

Оставь один пример Shared Request для следующей главы диагностики permissions.
