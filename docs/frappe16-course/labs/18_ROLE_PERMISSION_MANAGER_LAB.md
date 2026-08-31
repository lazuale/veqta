# Лабораторная 18. Role Permission Manager

## Цель

Реально проверить CRUD-права на `Request` под двумя пользователями.

## Настрой permissions

В Role Permission Manager для `Request` задай:

```text
Training User:
Read = yes
Create = yes
Write = yes
Delete = no

Training Manager:
Read = yes
Create = yes
Write = yes
Delete = yes
```

Убедись, что обе роли имеют нужный permission level 0.

## Проверь под Training User

В private окне:

1. открыть список Request;
2. открыть существующий Request;
3. создать новый;
4. изменить его;
5. попытаться удалить.

Последний пункт должен быть запрещён.

## Проверь под Training Manager

Повтори те же шаги. Delete должен быть доступен, если другие ограничения не мешают.

## Эксперимент

Сними `Write` у `Training User`, перезайди и сравни форму. После проверки верни `Write`.

## Намеренная ошибка

Не тестируй permission только под Administrator: Administrator обходит многие обычные ограничения и даёт ложное ощущение, что настройка работает.

## Проверка себя

Составь таблицу фактических действий двух пользователей и сравни её с Role Permission Manager.

## Состояние после лабораторной

Верни базовую матрицу из начала лабораторной.
