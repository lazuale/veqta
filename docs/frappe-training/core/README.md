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
| [`S08`](S08_APP_STATE_DELIVERY_AUDIT.md) | audit manifest App-owned/Site-owned состояния и migrate/fixture delivery | написан |
| S09 | чистая установка и финальная приёмка | следующий |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После S08 для каждого обязательного элемента CORE должен быть известен владелец и source of truth.

```text
Rental Training Module
→ modules.txt

Equipment / Customer / Rental Item / Rental
→ Standard DocType JSON

naming / fields / default DocPerm
→ Standard DocType metadata

V01 / V02 / V03
→ rental.py

Rental Operator / Rental Manager
→ hooks.py + fixtures/role.json

automated contracts
→ test_rental.py
```

При этом экземплярное состояние остаётся у Site:

```text
Users
Equipment/Customer/Rental records
developer_mode
allow_tests
runtime naming state
```

S08 отдельно проверяет отсутствие скрытой обязательной конфигурации в:

```text
Custom Field
Property Setter
Custom DocPerm
```

и выполняет два round-trip:

```text
Site Role config
→ export-fixtures
→ committed fixture
→ Git clean

App source
→ bench migrate
→ current Site
→ tests green
→ Git clean
```

Patch в CORE не создаётся ради демонстрации: пока строится первый baseline и нет поддерживаемой старой версии данных, отсутствует реальная одноразовая data migration.

Следующий и последний CORE-этап — S09:

```text
новый clean Frappe Site
+ текущий rental_training из Git
+ install-app
+ migrate
+ tests
+ основной Desk/permission scenario
=
доказательство воспроизводимости CORE
```
