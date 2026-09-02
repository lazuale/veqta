# CORE-практикум Frappe — исполняемые этапы

Эта папка содержит уже не архитектурные документы, а **пошаговые практические задания**.

Нормативные документы находятся уровнем выше:

- [`../ARCHITECTURE_PASSPORT.md`](../ARCHITECTURE_PASSPORT.md);
- [`../REQUIREMENTS_MATRIX.md`](../REQUIREMENTS_MATRIX.md);
- [`../STAGE_DEPENDENCY_GRAPH.md`](../STAGE_DEPENDENCY_GRAPH.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md).

## Правило прохождения

Каждый файл заканчивается критерием `ГОТОВО / НЕ ГОТОВО`.

Следующий зависимый этап начинается только после прохождения контрольной точки предыдущего.

Практикум не требует запоминать меню или команды ради самих команд. В каждом этапе сначала есть рабочая задача, затем штатный механизм Frappe, затем проверяемый результат.

## Этапы

| Код | Результат | Статус |
|---|---|---|
| [`S00`](S00_ENVIRONMENT.md) | чистый Frappe v16 Bench + `rental.localhost` | написан |
| [`S01`](S01_APP_AND_SITE.md) | создан и установлен `rental_training` | написан |
| [`S02`](S02_EQUIPMENT_DOCTYPE.md) | `Equipment` как самостоятельный Standard DocType | написан |
| [`S03`](S03_CUSTOMER_DOCTYPE.md) | `Customer` как второй самостоятельный Document | написан |
| S04 | `Rental` + `Rental Item` + Link/Table | следующий |
| S05A | предметный status | запланирован |
| S05B | полный сценарий через Desk | запланирован |
| S05C | серверные инварианты одного Rental | запланирован |
| S05D | Roles / DocType Permissions | запланирован |
| S06 | правило пересекающихся Active Rentals | запланирован |
| S07 | автоматические тесты контрактов | запланирован |
| S08 | аудит App-owned состояния и миграций | запланирован |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После успешного S03 приложение содержит две независимые предметные сущности:

```text
rental_training [App]
└── Rental Training [Module]
    ├── Equipment [DocType]
    └── Customer [DocType]
```

Обе имеют собственную стабильную identity и человекочитаемый title:

```text
Equipment
name  = EQ-#####
title = equipment_name

Customer
name  = CUST-#####
title = customer_name
```

Для Customer дополнительно проверена штатная типизация текстовых значений:

```text
phone : Data + Options=Phone
email : Data + Options=Email
```

Ученик должен уметь объяснить:

```text
почему Equipment и Customer существуют независимо
почему их display-поля не используются как identity
почему обычная Email validation не требует своей regex
почему эти два Documents пока не нужно связывать напрямую
```

Следующий реальный вопрос предметной области:

> кто взял, на какой период и какое оборудование?

Он приводит к S04, где впервые появляется сама операция `Rental` и естественно используются:

```text
Link
Child DocType
Table
```

Не как отдельные учебные функции, а как следствие модели операции проката.
