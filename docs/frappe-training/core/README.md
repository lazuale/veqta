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
| S05B | полный сценарий через Desk | следующий |
| S05C | серверные инварианты одного Rental | запланирован |
| S05D | Roles / DocType Permissions | запланирован |
| S06 | правило пересекающихся Active Rentals | запланирован |
| S07 | автоматические тесты контрактов | запланирован |
| S08 | аудит App-owned состояния и миграций | запланирован |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После S05A центральная модель уже содержит предметное состояние:

```text
Rental
├── customer   → Link → Customer
├── start_date → Date
├── end_date   → Date
├── status     → Select
│                ├── Planned
│                ├── Active
│                └── Returned
└── items      → Table MultiSelect → Rental Item
                                     └── equipment → Link → Equipment
```

При этом S05A специально доказывает три разные ответственности:

```text
business status
= что сейчас происходит с Rental
= Planned / Active / Returned

Workflow
= политика разрешённых переходов
= пока отсутствует

docstatus
= системный Draft / Submitted / Cancelled lifecycle
= для Rental остаётся 0 Draft
```

Ученик должен руками увидеть через серверный API/console, что возможна запись:

```text
status    = Returned
docstatus = 0
```

и объяснить, почему это не противоречие.

Также S05A впервые изменяет уже существующий tracked Standard DocType: `rental.json` виден обычным `git diff`, после чего изменение фиксируется отдельным Git checkpoint.

После P04 ветки UI, status, серверные инварианты и permissions архитектурно независимы. В исполняемом маршруте следующей пишется S05B — проверка полного вертикального сценария через стандартный Desk, без собственного frontend.