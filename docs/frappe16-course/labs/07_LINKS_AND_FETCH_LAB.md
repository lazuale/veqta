# Лабораторная 07. Link, Dynamic Link и Fetch From

## Цель

Связать `Request` с реальными Documents другого DocType и увидеть автоматическую подстановку.

## Сделай руками

В `Request` добавь:

```text
Responsible       Link → User
Responsible Name  Data
```

Для `Responsible Name` настрой:

```text
Fetch From = responsible.full_name
Read Only = 1
```

Создай/открой Request и выбери разных Users в `Responsible`.

## Ожидаемый результат

При смене Link Frappe подтягивает `full_name` связанного User в `Responsible Name`.

## Эксперимент

Очисти `Responsible`, затем выбери другого User. Проверь, как меняется fetched value.

## Намеренная поломка

Временно измени `Fetch From` на несуществующее поле, например:

```text
responsible.not_a_real_field
```

Обнови форму и посмотри, что автоматическая подстановка перестала работать/вызывает проблему конфигурации. После этого верни:

```text
responsible.full_name
```

## Дополнительный опыт

Добавь временную пару:

```text
Reference Type  Link → DocType
Reference Name  Dynamic Link → Reference Type
```

Выбери `User`, затем конкретного пользователя. После эксперимента можешь оставить поля для будущих глав или удалить, если они мешают.

## Проверка себя

Объясни различие:

```text
Link       → всегда указывает на один заранее известный DocType
Dynamic Link → тип связанного Document определяется другим полем
Fetch From → копирует значение из Link-связанного Document
```

## Состояние после лабораторной

`Responsible` и `Responsible Name` оставить.
