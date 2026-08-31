# Лабораторная 19. Permission Level

## Цель

Увидеть field-level permission, а не путать его с Hidden/Read Only в UI.

## Подготовка

В `Request` добавь поле:

```text
Internal Cost  Currency
Permission Level = 1
```

В Role Permission Manager добавь для `Training Manager` отдельную строку permission level 1 с `Read` и `Write`.

Для `Training User` level 1 не выдавай.

## Проверь

Под `Training Manager`:

- поле видно;
- значение можно записать.

Под `Training User`:

- сравни Form View;
- попробуй получить Request через REST позже или через доступный browser request/форму;
- убедись, что это именно permission boundary, а не просто скрытие CSS.

## Эксперимент

Временно добавь level 1 Read для `Training User`, но не Write. Проверь разницу между чтением и изменением. Затем убери.

## Намеренная ошибка

Сделай копию поля `Fake Secret` с level 0 и просто `Hidden = 1`. Подумай, почему Hidden не равно защите данных. После эксперимента удали `Fake Secret`.

## Проверка себя

Объясни:

```text
Hidden       → UI metadata
Read Only    → UI/field behavior
Perm Level   → слой permission model
```

## Состояние после лабораторной

`Internal Cost` оставить на permission level 1; доступ только Training Manager.
