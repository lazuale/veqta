# S08. Убрать N+1 через `frappe.qb.get_query`

S07 показал измеримую причину: первая версия `Equipment Utilization` выполняет запросы внутри циклов.

Новое требование:

> Получить исходные строки для расчёта set-based, не меняя календарную логику и не обходя без необходимости permission-модель Frappe.

В Frappe v16 для этого подходит `frappe.qb.get_query`: API строит Query Builder expression поверх DocType metadata и умеет применять permissions.

Связанные материалы:

- [`S07_RECORDER.md`](S07_RECORDER.md);
- [`S06_SCRIPT_REPORT.md`](S06_SCRIPT_REPORT.md);
- [`../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md`](../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md);
- [`../../../frappe-architecture-standard/04_SECURITY.md`](../../../frappe-architecture-standard/04_SECURITY.md).

Первичный источник:

- https://docs.frappe.io/framework/get_query

---

## 1. Что именно меняется

На S06 было:

```text
получить Equipment
↓
для каждого Equipment запросить Rental Item
↓
для каждого item загрузить Rental
```

После S08 должно стать:

```text
1 set-based query → доступные Equipment
1 set-based query → нужные Rental + child Equipment за период
↓
Python группирует уже полученные строки в памяти
↓
тот же расчёт интервалов
```

Мы не переписываем:

```text
_validate_period()
_merge_intervals()
_count_occupied_days()
```

Их ответственность не связана с БД.

---

## 2. Почему используется `frappe.qb.get_query`, а не bare SQL

Текущая задача находится внутри Python Script Report.

Нужны:

```text
DocType fields
Child Table field items.equipment
filters
permissions текущего пользователя
```

`frappe.qb.get_query` уже умеет работать с этой моделью.

Поэтому нет отдельной причины переходить на:

```text
frappe.db.sql()
ручной JOIN через строку SQL
новый repository/service layer
```

Query Report на S05 использовал SQL потому, что SQL является самим механизмом Query Report. В Script Report такой причины нет.

---

## 3. Permission boundary остаётся явной

`Equipment Utilization` по-прежнему manager-only Standard Report.

Дополнительно `frappe.qb.get_query` вызывается с:

```python
ignore_permissions=False
user=frappe.session.user
```

То есть set-based запрос не требует обходить permissions ради производительности.

В текущем сценарии `Rental Manager` имеет Read всех Rentals, поэтому результат остаётся полным и соответствует предметному требованию.

Важно различать:

```text
Report roles + Report permission
→ кто имеет право запустить функциональность

frappe.qb.get_query(ignore_permissions=False)
→ какие Documents/fields доступны этому user context при запросе
```

Они не заменяют друг друга.

---

## 4. Изменить imports

В:

```text
rental_training/rental_training/report/equipment_utilization/equipment_utilization.py
```

добавьте:

```python
from collections import defaultdict
```

Остальные imports первого варианта сохраняются.

---

## 5. Получать Equipment одним query

В `execute()` замените:

```python
equipment_rows = frappe.get_all(
    "Equipment",
    fields=["name", "equipment_name"],
    order_by="name asc",
)
```

на:

```python
equipment_rows = frappe.qb.get_query(
    "Equipment",
    fields=["name", "equipment_name"],
    order_by="name asc",
    ignore_permissions=False,
    user=frappe.session.user,
).run(as_dict=True)
```

---

## 6. Получить все нужные Rental rows одним query

Добавьте helper:

```python
def _get_intervals_by_equipment(
    from_date: date,
    to_date: date,
) -> dict[str, list[tuple[date, date]]]:
    rows = frappe.qb.get_query(
        "Rental",
        fields=[
            "items.equipment as equipment",
            "start_date",
            "end_date",
        ],
        filters=[
            ["status", "in", list(COUNTED_STATUSES)],
            ["start_date", "<=", to_date],
            ["end_date", ">=", from_date],
        ],
        ignore_permissions=False,
        user=frappe.session.user,
    ).run(as_dict=True)

    intervals_by_equipment = defaultdict(list)

    for row in rows:
        start = max(getdate(row.start_date), from_date)
        end = min(getdate(row.end_date), to_date)

        if start <= end:
            intervals_by_equipment[row.equipment].append((start, end))

    return intervals_by_equipment
```

Здесь поле:

```text
items.equipment
```

обращается к `equipment` внутри Child Table `Rental.items`.

Frappe строит нужную связанную выборку по metadata DocType вместо нашего цикла по `Rental Item`.

---

## 7. Убрать naive DB access из цикла

Перед циклом Equipment в `execute()` вызовите:

```python
intervals_by_equipment = _get_intervals_by_equipment(
    from_date,
    to_date,
)
```

Цикл должен использовать уже готовый словарь:

```python
for equipment in equipment_rows:
    intervals = intervals_by_equipment.get(equipment.name, [])
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
```

Удалите больше не нужную функцию:

```text
_get_equipment_intervals_naive()
```

---

## 8. Что получилось архитектурно

До:

```text
Python loop
→ Database API
→ Python loop
→ Document load
```

После:

```text
Database query
→ набор необходимых строк
→ Python
→ предметный расчёт интервалов
```

Ответственности разделились естественно:

```text
frappe.qb.get_query
→ получить набор данных

Python helpers
→ обработать календарные интервалы
```

Мы не создавали новый слой только ради того, чтобы назвать его repository или service.

---

## 9. Сначала проверить результат

Запустите Report:

```text
From Date : 2026-09-01
To Date   : 2026-09-10
```

Контрольные A/B/C должны остаться:

```text
50%
50%
10%
```

Если результат изменился, оптимизация не принята.

Правило:

```text
быстрее
но считает другое
=
ошибка
```

---

## 10. Повторить Recorder

Повторите процедуру S07:

1. войдите как `Administrator`;
2. запустите Recorder;
3. один раз выполните `Equipment Utilization` за контрольный период;
4. остановите Recorder;
5. сравните SQL capture с baseline S07.

Теперь количество запросов, связанных с подготовкой Equipment/Rental rows, не должно расти по схеме:

```text
1 + Equipment + Rental Items
```

Вместо этого подготовка данных должна состоять из небольшого постоянного числа set-based запросов.

Точное общее количество SQL Framework не является контрактом.

---

## 11. Почему индекс по-прежнему не добавляется автоматически

После устранения N+1 посмотрите SQL и `EXPLAIN` ещё раз.

Если на учебном наборе нет отдельной измеримой проблемы плана запроса, этап заканчивается здесь.

Не добавляйте индекс:

```text
по status
по start_date
по end_date
```

только потому, что эти поля участвуют в filters.

Индекс — отдельное решение с собственной стоимостью записи и хранения. Для него нужна отдельная наблюдаемая причина.

---

## 12. Cache тоже не нужен

Мы исправили саму форму доступа к данным.

Нет нового требования:

```text
результат очень дорогой
+
часто повторяется
+
имеет понятную стратегию invalidation/TTL
```

Поэтому `frappe.cache` здесь не появляется.

---

## 13. Проверить diff

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git diff -- \
  rental_training/rental_training/report/equipment_utilization/equipment_utilization.py
```

В diff должна быть только осмысленная замена способа получения данных.

JS filters, Report metadata и календарный алгоритм не должны случайно переписаться.

После проверки:

```bash
git add rental_training/rental_training/report/equipment_utilization/equipment_utilization.py
git commit -m "perf: remove utilization report n plus one queries"
```

---

## Результат этапа

К концу S08 доказано:

```text
N+1 устранён после измерения, а не заранее
frappe.qb.get_query получает данные set-based
permissions не обходятся ради производительности
календарный алгоритм не изменился
контрольный результат сохранился
повторный Recorder показывает устранение причины
индекс и cache не добавлены без отдельного требования
```

На S09 собственные контракты практикума будут закреплены автоматическими тестами.
