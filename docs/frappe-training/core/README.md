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
| [`S09`](S09_CLEAN_INSTALL_ACCEPTANCE.md) | clean Site install + tests + Desk/permission acceptance | написан |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## CORE завершён как маршрут

S09 закрывает обязательную цепочку CORE:

```text
совместимый Frappe Bench
        ↓
App boundary
        ↓
Standard metadata
        ↓
Document relations
        ↓
status
        ↓
Desk
        ↓
server invariants
        ↓
permissions
        ↓
cross-document invariant
        ↓
automated contracts
        ↓
delivery audit
        ↓
clean Site acceptance
```

Финальная проверка выполняется не на старом dev-site, а на новом:

```text
rental-acceptance.localhost
```

До установки на нём должен быть только:

```text
frappe
```

После установки текущего committed `rental_training` без `developer_mode` должны штатно появиться:

```text
Rental Training Module
Equipment
Customer
Rental Item
Rental
Rental Operator
Rental Manager
default DocType Permissions
Rental Controller behavior
```

Затем:

```text
bench migrate
→ success

bench run-tests
→ green

Manager
→ Equipment → Customer → Rental

Operator
→ permission limits работают

Active overlap
→ блокируется

App Git
→ clean
```

## Что является App-owned

После S08/S09 граница должна быть понятна без догадок:

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

Экземплярное состояние остаётся у Site:

```text
Users
Equipment/Customer/Rental records
developer_mode на dev-site
allow_tests на test-site
runtime naming state
```

## Важная поправка среды

`developer_mode` включается **только на `rental.localhost`**, а не глобально на Bench.

Это нужно, чтобы второй acceptance-site мог доказать:

```text
установка и работа App
≠
зависимость от developer mode
```

Если практикум проходился по старой версии с глобальным `developer_mode`, S00 и S09 содержат точную команду очистки `common_site_config.json` через штатный `bench set-config`.

## Что дальше

CORE закончен не потому, что «мы прошли все возможности Frappe».

Наоборот, следующие механизмы остаются вне CORE до появления реального требования:

```text
Single DocType
Notification
Report
Print Format
Web Form
REST integration
Webhook
Background Jobs
Workflow
Is Submittable / docstatus
Permission Level / User Permission / Share
Server Script
custom frontend
```

Следующий учебный блок должен начинаться не с выбора очередной функции Frappe, а с нового требования и повторять тот же принцип:

```text
требование
→ ответственность
→ штатный механизм
→ проверяемый результат
```
