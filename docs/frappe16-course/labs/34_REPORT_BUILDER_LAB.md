# Лабораторная 34. Report Builder

## Цель

Получить полезный отчёт без SQL и Python.

## Подготовка

В Request должно быть минимум 30 учебных записей с разными Status, Priority, Area, Responsible и Due Date.

## Сделай руками

Создай Report Builder для `Request`.

Добавь колонки:

```text
Name
Subject
Status
Priority
Area
Responsible
Due Date
```

Применяй фильтры:

```text
Status != Done
Priority = High
Area = North
```

Попробуй сортировку и grouping, если они доступны для выбранного Report type.

## Ожидаемый результат

Отчёт должен отвечать на конкретный вопрос, например:

> Какие High Priority Requests в North ещё не Done?

## Эксперимент

Убери один фильтр и сравни количество строк. Затем добавь фильтр по Due Date.

## Намеренная ошибка

Попробуй получить сложный вычисляемый показатель, которого нет в полях и который требует join/вычисления. Зафиксируй границу Report Builder вместо попытки «додавить» его бессмысленными настройками.

## Проверка себя

Когда Report Builder достаточно, а когда нужен Query Report или Script Report?

## Состояние после лабораторной

Оставь один сохранённый отчёт `Open Requests by Area`.
