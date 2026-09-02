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
| S03 | `Customer` как самостоятельный Document | следующий |
| S04 | `Rental` + `Rental Item` + Link/Table | запланирован |
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

После успешного S02 приложение уже содержит первый App-owned Standard DocType:

```text
rental_training [App]
└── Rental Training [Module]
    └── Equipment [DocType]
        ├── equipment_name
        ├── equipment_type
        └── serial_number
```

Ученик должен уже уметь показать две стороны одной модели:

```text
Desk
├── Equipment Form
└── Equipment List

Git repository apps/rental_training
└── rental_training/rental_training/doctype/equipment/
    ├── equipment.json
    ├── equipment.py
    ├── equipment.js
    └── test_equipment.py
```

И объяснить:

```text
Equipment = самостоятельный Document
Equipment Type = пока Select
name = стабильная identity
Title Field = человекочитаемое представление
Standard DocType = App-owned metadata в Git
```

После этого можно переходить к S03 и создать второй независимый Document — `Customer`.
