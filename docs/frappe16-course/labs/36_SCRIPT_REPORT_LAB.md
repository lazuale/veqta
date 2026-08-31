# Лабораторная 36. Script Report

## Цель

Сравнить SQL-only Query Report с Python-driven Script Report.

## Сделай руками

Создай Standard Script Report в App `training` для `Request` согласно структуре файлов текущего v16.

Минимальный результат должен вернуть:

```text
columns
data
```

Например сгруппируй Request по Status:

```text
Open        12
In Progress 8
Done        15
```

Используй Frappe Database API или Query Builder вместо сырого SQL там, где это логично.

## Проверь на диске

```bash
find apps/training -type f | grep -i 'report' | sort
```

Открой Python/JS/JSON файлы созданного report.

## Эксперимент

Добавь filter `Area` и пересчитай результат только для выбранной Area.

## Намеренная ошибка

Верни data с неправильной структурой/несовпадающими columns и посмотри, как ломается rendering. Затем восстанови правильный контракт.

## Проверка себя

Объясни:

```text
Report Builder → metadata/no code
Query Report   → SQL
Script Report  → Python + произвольная report logic
```

## Состояние после лабораторной

Оставь Script Report `Request Status Summary`.
