# CORE-практикум Frappe — исполняемые этапы

Статус: **принятый исполняемый baseline CORE**.

Эта папка содержит уже не архитектурные документы, а **пошаговые практические задания**.

CORE учит фундаменту архитектуры собственного Frappe App. Он не объявляется полным курсом Framework: extension чужих Apps, сложные транзакции, background jobs/scheduler, интеграции, публичный web-layer, расширенная отчётность и production operations должны рассматриваться отдельными последующими практикумами из реальных требований.

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
| [`S09`](S09_CLEAN_INSTALL_ACCEPTANCE.md) | clean Site install + tests + Desk/permission acceptance | написан |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.
