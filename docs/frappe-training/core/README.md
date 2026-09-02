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
| S05C | серверные инварианты одного Rental | следующий |
| S05D | Roles / DocType Permissions | запланирован |
| S06 | правило пересекающихся Active Rentals | запланирован |
| S07 | автоматические тесты контрактов | запланирован |
| S08 | аудит App-owned состояния и миграций | запланирован |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После S05B центральная модель уже доказала не только структуру, но и пригодность для реальной внутренней работы через штатный Desk:

```text
Equipment List / Form
        ↓
Customer List / Form
        ↓
Rental Form
├── Customer Link
├── Date fields
├── status
└── Equipment Table MultiSelect
        ↓
Save
        ↓
Rental List
├── filters
├── reopen
└── edit
```

При этом никакой новый UI-слой не появился:

```text
Workspace        → не требуется текущему сценарию
Client Script    → не требуется
custom List JS   → не требуется
custom Page      → не требуется
SPA              → не требуется
```

Ключевая проверка S05B — после обычной работы с бизнес-записями:

```bash
git -C apps/rental_training status --short
```

остаётся пустым.

Ученик должен объяснить границу:

```text
DocType metadata / controller / обязательная config
= App-owned state
= source + Git

конкретные Equipment / Customer / Rental
= runtime data конкретного Site
= не source App
```

S05B выполняется под Administrator только для проверки UI-сценария. Это **не** считается доказательством корректных permissions — роли и реальные серверные ограничения проверяются отдельно на S05D.

После P04 ветки UI, status, серверные инварианты и permissions архитектурно независимы. В исполняемом маршруте следующей пишется S05C: два настоящих инварианта одного Rental должны впервые привести нас к серверному Python Controller:

```text
end_date >= start_date
Equipment не повторяется внутри одного Rental
```

Собственный код появляется не как очередная ступень курса, а потому что возникла новая ответственность, которую metadata сама по себе не гарантирует.
