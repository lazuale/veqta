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
| [`S07`](S07_AUTOMATED_CONTRACT_TESTS.md) | автоматические Frappe-aware tests собственных контрактов | написан |
| S08 | аудит App-owned состояния и миграций | следующий |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После S07 CORE уже не зависит от ручного повторения проверок S05C/S05D/S06.

```text
Rental.validate()
├── V01  date range
├── V02  duplicate Equipment
└── V03  overlapping Active Rental

Role + DocType Permissions
├── Rental Operator
└── Rental Manager

        ↓
IntegrationTestRental
        ↓
bench --site rental.localhost run-tests --app rental_training
```

S07 использует актуальный для Frappe v16 путь:

```python
from frappe.tests import IntegrationTestCase
```

а не deprecated `FrappeTestCase`.

Тесты сами создают необходимые Customer/Equipment и test Users. Они не зависят от `EQ-00001`, `CUST-00001`, вручную созданных Rentals или паролей dev-site.

Автоматически фиксируются не только базовые V01/V02/V03, но и точная семантика V03:

```text
общая граничная дата → конфликт
следующий день        → допустимо
Planned overlap       → допустимо
self-save Active      → допустимо
```

Permission tests выполняют реальные `insert/save/delete`, а не проверяют кнопки Desk.

Отдельно сохраняется архитектурная граница:

```text
автоматический test существующего контракта
≠
создание нового контракта
```

Поэтому S07 не добавляет browser automation, CI, coverage target или фиктивный concurrency test для гарантии, которой S06 не реализует.

Следующий этап — S08:

```text
каждый обязательный элемент CORE
        ↓
кто владелец?
где source of truth?
как попадёт на чистый Site?
нужен ли migrate / fixture / patch?
```

После S08 останется финальное доказательство S09 на новом чистом Site.
