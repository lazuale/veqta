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
| S05D | Roles / DocType Permissions | следующий |
| S06 | правило пересекающихся Active Rentals | запланирован |
| S07 | автоматические тесты контрактов | запланирован |
| S08 | аудит App-owned состояния и миграций | запланирован |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После S05C центральная модель впервые защищает себя на серверном Document path:

```text
Rental
├── customer
├── start_date
├── end_date
├── status
└── items
      ↓
Controller.validate()
├── validate_date_range()
└── validate_duplicate_equipment()
```

Зафиксированы два локальных инварианта:

```text
V01  end_date >= start_date
V02  Equipment не повторяется внутри одного Rental
```

Они проверяются не только через Form, но и через обычный серверный:

```python
Document.insert()
```

Это принципиальная граница:

```text
Client Script
= удобство конкретного UI

Controller.validate()
= обязательное поведение собственного Rental на обычном Document path
```

S05C не меняет DocType schema: меняется только App-owned `rental.py`. Поэтому этап специально не приучает выполнять `bench migrate` после любого Python-изменения.

В Controller нет:

```text
frappe.db.commit()
ignore_permissions=True
ручного SQL
Rule Engine
Server Script
проверки других Rentals
```

Последний пункт оставлен S06: междокументный конфликт — отдельная ответственность.

После P04 ветки UI, status, локальные инварианты и permissions архитектурно независимы. Следующая исполняемая ветка — S05D:

```text
Rental Operator
Rental Manager
      ↓
Role + DocType Permissions
```

Она должна доказать уже другой контракт:

```text
S05C → какие Documents допустимы
S05D → кто какие операции может выполнять
```
