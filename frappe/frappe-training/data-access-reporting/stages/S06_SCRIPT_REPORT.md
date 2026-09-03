# S06. Рассчитать Equipment Utilization через Script Report

Query Report из S05 умеет показать строки использования Equipment. Теперь появляется другая ответственность:

> Для каждого Equipment нужно посчитать, сколько уникальных календарных дней оно было занято в выбранном периоде, объединить пересекающиеся интервалы и вычислить процент загрузки.

Это уже не только выборка строк. Нужна программная обработка интервалов, поэтому появляется Standard `Script Report`.

Связанные материалы:

- [`S05_QUERY_REPORT.md`](S05_QUERY_REPORT.md);
- [`S00_BASELINE_AND_DATA.md`](S00_BASELINE_AND_DATA.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md`](../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md);
- [`../../../frappe-architecture-standard/09_UI_REPORTING.md`](../../../frappe-architecture-standard/09_UI_REPORTING.md).

Первичный источник:

- https://docs.frappe.io/framework/user/en/desk/reports/script-report

---

## 1. Зафиксировать расчёт до кода

Report filters:

```text
from_date : Date, required
to_date   : Date, required
```

Условия:

```text
from_date <= to_date
```

Диапазон считается включительно:

```text
2026-09-01 → 2026-09-10
= 10 календарных дней
```

В загрузку входят только Rentals со статусом:

```text
Active
Returned
```

`Planned` не считается фактической занятостью.

Для каждого Rental:

```text
start = max(rental.start_date, from_date)
end   = min(rental.end_date, to_date)
```

Если:

```text
start > end
```

интервал не пересекает отчётный период и не учитывается.

Пересекающиеся интервалы одного Equipment объединяются до подсчёта дней.

Итог:

```text
period_days
occupied_days
utilization_percent = occupied_days / period_days * 100
```

---

## 2. Проверить ожидаемый результат S00

Для периода:

```text
2026-09-01 → 2026-09-10
```

контрольные значения:

| Equipment | Occupied Days | Period Days | Utilization |
|---|---:|---:|---:|
| A | 5 | 10 | 50% |
| B | 5 | 10 | 50% |
| C | 1 | 10 | 10% |

Если позже код выдаёт другое значение, сначала проверяется расчёт и данные, а не подгоняется ожидаемый результат.

---

## 3. Почему Script Report тоже manager-only

Отчёт рассчитывает загрузку по Rentals всех владельцев.

Его аудитория остаётся:

```text
Rental Manager
```

`Rental Operator` не получает доступ к этому Report.

Python внутри Script Report не является отдельной системой авторизации. Граница доступа задаётся штатно:

```text
Report permission на Rental
+
Role у Standard Report
```

На первой реализации мы сознательно читаем полный набор данных как доверенную внутреннюю часть manager-only отчёта.

---

## 4. Создать Standard Script Report

Войдите как `Administrator`.

Через `Report` создайте:

```text
Report Name  : Equipment Utilization
Ref DocType  : Rental
Report Type  : Script Report
Is Standard  : Yes
Module       : Rental Training
```

Разрешённая роль:

```text
Rental Manager
```

Сохраните Report.

Для Standard Script Report Frappe создаёт каталог Report в Module и шаблоны Python/JavaScript исходников.

---

## 5. Найти созданные файлы

В терминале:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

find rental_training/rental_training/report/equipment_utilization \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидайте как минимум metadata Report и исходники вида:

```text
equipment_utilization.py
equipment_utilization.js
```

Точный дополнительный набор файлов зависит от patch-release.

---

## 6. Настроить filters в JavaScript

Откройте:

```text
rental_training/rental_training/report/equipment_utilization/equipment_utilization.js
```

Задайте:

```javascript
frappe.query_reports["Equipment Utilization"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
        },
    ],
};
```

Filters относятся к интерфейсу отчёта. Проверку их смысла всё равно нужно сделать на сервере в Python.

Нельзя полагаться только на `reqd: 1`, потому что серверный `execute()` остаётся настоящей границей расчёта.

---

## 7. Реализовать первую корректную Python-версию

Откройте:

```text
rental_training/rental_training/report/equipment_utilization/equipment_utilization.py
```

Используйте первую прямолинейную реализацию:

```python
from __future__ import annotations

from datetime import date

import frappe
from frappe import _
from frappe.utils import date_diff, getdate


COUNTED_STATUSES = ("Active", "Returned")


def execute(filters=None):
    filters = frappe._dict(filters or {})
    from_date, to_date = _validate_period(filters)
    period_days = date_diff(to_date, from_date) + 1

    columns = [
        {
            "fieldname": "equipment",
            "label": _("Equipment"),
            "fieldtype": "Link",
            "options": "Equipment",
            "width": 160,
        },
        {
            "fieldname": "equipment_name",
            "label": _("Equipment Name"),
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "fieldname": "occupied_days",
            "label": _("Occupied Days"),
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "period_days",
            "label": _("Period Days"),
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "fieldname": "utilization_percent",
            "label": _("Utilization %"),
            "fieldtype": "Percent",
            "width": 120,
        },
    ]

    data = []

    equipment_rows = frappe.get_all(
        "Equipment",
        fields=["name", "equipment_name"],
        order_by="name asc",
    )

    for equipment in equipment_rows:
        intervals = _get_equipment_intervals_naive(
            equipment.name,
            from_date,
            to_date,
        )
        occupied_days = _count_occupied_days(intervals)

        data.append(
            {
                "equipment": equipment.name,
                "equipment_name": equipment.equipment_name,
                "occupied_days": occupied_days,
                "period_days": period_days,
                "utilization_percent": round(
                    occupied_days / period_days * 100,
                    2,
                ),
            }
        )

    return columns, data


def _validate_period(filters) -> tuple[date, date]:
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("From Date and To Date are required"))

    from_date = getdate(filters.from_date)
    to_date = getdate(filters.to_date)

    if from_date > to_date:
        frappe.throw(_("From Date cannot be after To Date"))

    return from_date, to_date


def _get_equipment_intervals_naive(
    equipment: str,
    from_date: date,
    to_date: date,
) -> list[tuple[date, date]]:
    item_rows = frappe.get_all(
        "Rental Item",
        filters={
            "equipment": equipment,
            "parenttype": "Rental",
            "parentfield": "items",
        },
        fields=["parent"],
    )

    intervals = []

    for item in item_rows:
        rental = frappe.get_doc("Rental", item.parent)

        if rental.status not in COUNTED_STATUSES:
            continue

        rental_start = getdate(rental.start_date)
        rental_end = getdate(rental.end_date)

        start = max(rental_start, from_date)
        end = min(rental_end, to_date)

        if start <= end:
            intervals.append((start, end))

    return intervals


def _count_occupied_days(intervals: list[tuple[date, date]]) -> int:
    merged = _merge_intervals(intervals)
    return sum(date_diff(end, start) + 1 for start, end in merged)


def _merge_intervals(
    intervals: list[tuple[date, date]],
) -> list[tuple[date, date]]:
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda interval: interval[0])
    merged = [ordered[0]]

    for start, end in ordered[1:]:
        previous_start, previous_end = merged[-1]

        if start <= previous_end:
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))

    return merged
```

---

## 8. Почему первая версия намеренно прямолинейная

Она делает:

```text
1 query → список Equipment

для каждого Equipment:
  1 query → Rental Item

для каждой найденной строки:
  ещё 1 query → get_doc Rental
```

Это корректно по результату, но форма доступа к данным подозрительна:

```text
цикл
→ запрос
→ ещё один цикл
→ ещё один запрос
```

На S06 мы **не объявляем это проблемой только по внешнему виду кода**.

Сначала нужно получить работающий результат. На S07 `Recorder` покажет фактическое число запросов и позволит доказать N+1 измерением.

---

## 9. Почему здесь допустим `get_all` и `get_doc` без read-check

На S04 мы видели, что это было бы опасно для произвольного user-facing метода.

Но текущая операция имеет другую границу:

```text
Equipment Utilization
→ Standard Report
→ разрешён только Rental Manager
→ менеджер по предметному требованию имеет Read всех Rentals
```

Следовательно, код отчёта выполняет доверенную внутреннюю выборку полного набора.

Это не универсальное разрешение писать так везде.

Если аудитория отчёта изменится, модель чтения нужно пересмотреть вместе с новым требованием.

---

## 10. Проверить отчёт

Запустите dev server, если он не работает:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Войдите под:

```text
manager@example.test
```

Откройте:

```text
Equipment Utilization
```

Filters:

```text
From Date : 2026-09-01
To Date   : 2026-09-10
```

Для контрольных Equipment A/B/C ожидается:

```text
A → 5 / 10 → 50%
B → 5 / 10 → 50%
C → 1 / 10 → 10%
```

Дополнительные Equipment на Site могут появиться в отчёте с `0%`.

---

## 11. Проверить граничные случаи вручную

### Один день

```text
From Date = 2026-09-10
To Date   = 2026-09-10
```

Ожидается:

```text
Period Days = 1
```

### Неверный диапазон

```text
From Date = 2026-09-11
To Date   = 2026-09-10
```

Сервер должен отклонить расчёт.

### Пересечение границы

Для B3:

```text
Rental = 2026-09-10 → 2026-09-12
Report = 2026-09-01 → 2026-09-10
```

учитывается ровно один день:

```text
2026-09-10
```

---

## 12. Проверить аудиторию

Под `operator-a@example.test` Script Report не должен быть доступен.

Под `manager@example.test` должен открываться и выполняться.

Это тот же manager-only контракт, что у Query Report.

---

## 13. Проверить Git

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
git status --short
git diff
```

В App должны появиться только файлы Standard Script Report.

После проверки:

```bash
git add rental_training/rental_training/report/equipment_utilization
git commit -m "feat: add equipment utilization report"
```

---

## Результат этапа

К концу S06:

```text
Script Report появился только из-за программного расчёта интервалов
период имеет однозначную включительную семантику
пересечения не удваивают календарные дни
контрольный результат совпадает с S00
Report доступен только Rental Manager
первая реализация корректна, но её стоимость запросов ещё не оценена
```

На S07 мы не будем переписывать код «на глаз». Сначала измерим работающий отчёт через Frappe Recorder.
