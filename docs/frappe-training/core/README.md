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
| S06 | правило пересекающихся Active Rentals | следующий |
| S07 | автоматические тесты контрактов | запланирован |
| S08 | аудит App-owned состояния и миграций | запланирован |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После S05D CORE уже имеет две независимые серверные гарантии.

### Допустимость данных

```text
Rental
      ↓
Controller.validate()
├── V01 end_date >= start_date
└── V02 Equipment не повторяется внутри одного Rental
```

### Авторизация

```text
User
  ↓ roles
Rental Operator / Rental Manager
  ↓ DocType Permissions
Equipment / Customer / Rental
```

S05D специально доказывает права не только через кнопки Desk, но и настоящими server-side операциями под `operator@example.test` и `manager@example.test`.

Базовая матрица:

```text
Rental Operator
Equipment → Read
Customer  → Read/Create/Write
Rental    → Read/Create/Write

Rental Manager
Equipment → CRUD
Customer  → CRUD
Rental    → CRUD
```

Обязательная permission model разделена по ownership:

```text
Role records
→ fixtures App

DocType default permissions
→ Standard DocType JSON

конкретные учебные Users
→ Site only
```

Именно поэтому после S05D чистая установка не должна требовать вручную создавать `Rental Operator` / `Rental Manager` или заново накликивать default CRUD matrix.

Без требования не добавлены:

```text
Permission Level
Permission Type
If Owner
User Permission
Share
permission_query_conditions
has_permission hook
custom ACL
ignore_permissions=True
```

Следующий этап — S06. Он соединит две уже готовые части модели:

```text
status = Active
+
локально корректный Rental
+
поиск других Rentals
        ↓
V03: один Equipment не может находиться
     в двух пересекающихся Active Rentals
```

Это будет первый междокументный инвариант CORE.