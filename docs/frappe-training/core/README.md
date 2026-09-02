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
| [`S04`](S04_RENTAL_COMPOSITION.md) | `Rental` + `Rental Item` + Link + Table MultiSelect | написан |
| [`S05A`](S05A_RENTAL_STATUS.md) | предметный `status` без Workflow/docstatus | написан |
| [`S05B`](S05B_DESK_VERTICAL_SCENARIO.md) | полный сценарий через стандартный Desk | написан |
| [`S05C`](S05C_RENTAL_LOCAL_INVARIANTS.md) | серверные инварианты одного Rental | написан |
| [`S05D`](S05D_ROLES_AND_PERMISSIONS.md) | `Rental Operator` / `Rental Manager` через Role + DocType Permissions | написан |
| [`S06`](S06_ACTIVE_RENTAL_CONFLICT.md) | междокументный инвариант пересекающихся Active Rentals | написан |
| S07 | автоматические тесты контрактов | следующий |
| S08 | аудит App-owned состояния и миграций | запланирован |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После S06 CORE имеет три бизнес-инварианта и базовую authorization model.

```text
Rental.validate()
├── V01 local
│   └── end_date >= start_date
├── V02 local
│   └── Equipment не повторяется внутри Rental
└── V03 cross-document
    └── одно Equipment не может находиться
        в пересекающихся Active Rentals

User
  ↓ roles
Rental Operator / Rental Manager
  ↓ DocType Permissions
Equipment / Customer / Rental
```

Для V03 зафиксирована включительная семантика дат:

```text
10–12 + 12–14 → конфликт
10–12 + 13–14 → допустимо
```

и предметная семантика статусов:

```text
Planned  → не блокирует
Active   → блокирует
Returned → не блокирует
```

Внутренний validator использует `frappe.get_all()` намеренно, потому что целостность данных не должна зависеть от того, какие другие Rentals текущий пользователь видит в List. Пользовательские выборки при этом продолжают использовать permission-aware путь.

S06 отдельно фиксирует границу:

```text
последовательная validate-проверка
≠
полная concurrency/locking strategy
```

SQL-locks, reservation service и другие production-механизмы не добавляются без отдельного требования.

Следующий этап — S07. На нём ручные проверки S05C, S05D и S06 должны превратиться в повторяемые автоматические контракты Frappe test runner:

```text
valid Rental
invalid dates
duplicate Equipment
overlapping Active Rental
non-overlapping Active Rental
permissions
```
