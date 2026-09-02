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
| S05A | предметный status | следующий |
| S05B | полный сценарий через Desk | запланирован |
| S05C | серверные инварианты одного Rental | запланирован |
| S05D | Roles / DocType Permissions | запланирован |
| S06 | правило пересекающихся Active Rentals | запланирован |
| S07 | автоматические тесты контрактов | запланирован |
| S08 | аудит App-owned состояния и миграций | запланирован |
| S09 | чистая установка и финальная приёмка | запланирован |

`NEXT`, `GATE` и `EXT` не смешиваются с этим маршрутом автоматически. Они подключаются только после соответствующего требования, как определено в архитектурных документах.

## Текущая точка

После успешного S04 приложение впервые содержит саму операцию проката:

```text
rental_training [App]
└── Rental Training [Module]
    ├── Equipment [DocType]
    ├── Customer [DocType]
    ├── Rental [DocType]
    └── Rental Item [Child DocType]
```

Связи:

```text
Rental
├── customer → Link → Customer
├── start_date
├── end_date
└── items → Table MultiSelect → Rental Item
                              └── equipment → Link → Equipment
```

S04 специально использует `Table MultiSelect`, а не обычный `Table`.

Причина архитектурная, а не учебная:

```text
текущее требование
= выбрать несколько существующих Equipment

Rental Item
= только Link → Equipment
```

Обычный `Table` появится только если у строки появятся собственные бизнес-атрибуты отношения. Мы не добавляем такие поля заранее ради знакомства с grid.

Через `bench console` ученик уже должен увидеть, что компактный Table MultiSelect всё равно хранится как дочерние Documents с:

```text
parent
parenttype
parentfield
idx
```

И уметь объяснить:

```text
Rental = самостоятельный Document
Rental Item = часть одного Rental
Customer = живая Link-ссылка
Equipment = живая Link-ссылка
Table MultiSelect = набор Links через child-table модель
обычный Table = пока не требуется текущей семантикой
```

После S04 в `Rental` **ещё нет status**.

Следующее реальное требование:

> отличать запланированный прокат от активного и возвращённого.

Оно приводит к S05A и обычному предметному полю:

```text
status → Select
Planned
Active
Returned
```

без автоматического Workflow и без `Is Submittable`.