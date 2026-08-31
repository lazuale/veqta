# Лабораторная 11. Form View

## Цель

Собрать форму Request из metadata и увидеть, что UI генерируется из структуры DocType.

## Сделай руками

Перестрой поля `Request`:

```text
Tab: Main
  Section: General
    Subject | Priority
    Status  | Due Date

  Section: Responsibility
    Responsible | Responsible Name

Tab: Details
  Description
  Notes
  Items
```

Используй `Tab Break`, `Section Break`, `Column Break`.

Добавь Description нескольким полям.

## Ожидаемый результат

Form View меняется без собственного HTML/React/Vue-кода.

## Эксперимент

Сделай одну Section collapsible и одну вкладку/секцию условно видимой через штатное `Depends On`, например на `is_urgent`.

Поменяй `Is Urgent` и наблюдай форму.

## Намеренная ошибка

Создай неудобную раскладку: слишком много Column Break или пустую Section. Посмотри результат и верни форму в понятное состояние.

Цель — понять, что metadata даёт свободу, но не проектирует UX за тебя.

## Проверка себя

Укажи, что отвечает за:

- новый таб;
- новую строку смыслового блока;
- две колонки;
- условную видимость;
- постоянную read-only характеристику.

## Состояние после лабораторной

Оставь аккуратную двухвкладочную форму `Request`.
