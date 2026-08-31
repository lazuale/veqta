# Лабораторная 09. Single, Tree, Submittable и граница Virtual DocType

## Цель

Увидеть, что специальные режимы меняют семантику DocType, а не просто внешний вид.

## Часть A — Single

Создай:

```text
Training Settings
Module: Training
Is Single: enabled
```

Поля:

```text
Default Priority  Select → Low/Medium/High
Course Note       Small Text
```

Открой `Training Settings`, сохрани значения, закрой и снова открой.

Наблюдение: это одна запись-настройка на Site, а не список из многих Documents.

## Часть B — Tree

Создай:

```text
Training Category
Module: Training
Is Tree: enabled
```

Создай иерархию:

```text
Operations
├── Internal
└── External

Analytics
```

Открой Tree View и перемещай узел.

## Часть C — Submittable

Создай маленький `Approval Record` с `Is Submittable = 1` и полем `Subject`.

Пока только убедись, что у него появляются действия Submit/Cancel. Полный lifecycle — следующая глава.

## Virtual DocType

Не создавай Virtual DocType «для галочки». В этой лабораторной достаточно открыть metadata/документацию и зафиксировать: Virtual нужен, когда backend хранения реализуется кодом и обычной таблицы DocType недостаточно.

## Намеренная ошибка

Попробуй использовать Single как обычный список из нескольких настроек. Увидь, что модель не соответствует такой задаче.

## Проверка себя

Для каждой задачи выбери режим:

- одна конфигурация Site;
- иерархический каталог;
- документ с Submit/Cancel;
- данные из внешнего backend без обычной таблицы.

## Состояние после лабораторной

Оставь `Training Settings`, `Training Category`, `Approval Record`.
