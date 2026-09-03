# S05. Построить Equipment Rental History через Query Report

До S05 простая отчётность решалась Report Builder. Теперь появляется требование, которое удобнее выразить одним связанным запросом:

> Менеджеру нужен обязательный отчёт App по использованию Equipment в Rentals за выбранный период. Каждая строка должна показывать конкретную связь Equipment ↔ Rental.

Нужные данные уже находятся в существующей модели:

```text
Equipment
← Rental Item
← Rental
→ Customer
```

Для этой задачи используется Standard `Query Report`.

Связанные материалы:

- [`S03_REPORT_BUILDER.md`](S03_REPORT_BUILDER.md);
- [`S04_DATA_ACCESS_BOUNDARY.md`](S04_DATA_ACCESS_BOUNDARY.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md`](../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md);
- [`../../../frappe-architecture-standard/09_UI_REPORTING.md`](../../../frappe-architecture-standard/09_UI_REPORTING.md).

Первичный источник:

- https://docs.frappe.io/framework/user/en/desk/reports/query-report

---

## 1. Зафиксировать контракт отчёта

Название:

```text
Equipment Rental History
```

Аудитория:

```text
Rental Manager
```

Обязательные filters:

```text
from_date : Date
to_date   : Date
```

Строки отчёта:

```text
equipment
rental
customer
status
start_date
end_date
owner
```

Rental попадает в отчёт, если его период пересекает выбранный диапазон:

```text
rental.start_date <= to_date
AND
rental.end_date >= from_date
```

В этом отчёте показываются все статусы. Он отвечает на вопрос «где и когда фигурировало Equipment», а не рассчитывает фактическую загрузку.

---

## 2. Почему это Standard Report

В отличие от сохранённого Report Builder из S03, новый отчёт является обязательной функцией приложения:

> После установки `rental_training` на новый Site менеджер должен получить этот тип отчёта без ручного создания заново.

Следовательно:

```text
Equipment Rental History
→ Standard Report
→ состояние App
→ должен появиться в исходниках
```

Это самостоятельная причина сделать Report Standard. Не потому, что «стандартные отчёты лучше custom».

---

## 3. Почему отчёт manager-only

На S01 оператор был ограничен собственными Rentals через `If Owner`.

SQL Query Report выполняет собственный запрос. Сам SQL не получает автоматически document-level фильтр `If Owner` только из-за того, что Reference DocType = `Rental`.

Поэтому текущая бизнес-граница выражается так:

```text
Report permission на Rental
+
allowed Role у Standard Report
→ Rental Manager
```

У менеджера есть право видеть весь набор Rentals, поэтому полный запрос соответствует его аудитории.

Не выдавайте этот отчёт `Rental Operator`, пока запрос сам возвращает данные всех владельцев.

---

## 4. Создать Standard Query Report

Войдите как `Administrator`.

Убедитесь, что developer mode включён для учебного Site.

Через Awesomebar откройте:

```text
Report
```

Создайте новый Report:

```text
Report Name       : Equipment Rental History
Ref DocType       : Rental
Report Type       : Query Report
Is Standard       : Yes
Module            : Rental Training
```

В разрешённых ролях оставьте:

```text
Rental Manager
```

Не добавляйте `Rental Operator`.

---

## 5. Добавить filters

В конфигурации Report добавьте два обязательных filter.

### From Date

```text
Label     : From Date
Fieldname : from_date
Fieldtype : Date
Mandatory : yes
```

### To Date

```text
Label     : To Date
Fieldname : to_date
Fieldtype : Date
Mandatory : yes
```

Frappe позволяет использовать значения filters как параметры SQL вида:

```text
%(from_date)s
%(to_date)s
```

Не собирайте SQL через конкатенацию строк с пользовательскими датами.

---

## 6. Добавить запрос

Используйте запрос:

```sql
SELECT
    ri.equipment AS equipment,
    r.name AS rental,
    r.customer AS customer,
    r.status AS status,
    r.start_date AS start_date,
    r.end_date AS end_date,
    r.owner AS owner
FROM `tabRental Item` ri
INNER JOIN `tabRental` r
    ON r.name = ri.parent
    AND ri.parenttype = 'Rental'
    AND ri.parentfield = 'items'
WHERE
    r.start_date <= %(to_date)s
    AND r.end_date >= %(from_date)s
ORDER BY
    ri.equipment,
    r.start_date,
    r.name
```

### Почему нужны `parenttype` и `parentfield`

`Rental Item` — Child DocType.

Связь с родителем хранится не только через `parent`, но и через:

```text
parenttype
parentfield
```

Мы явно фиксируем, что используем строки:

```text
Rental.items
```

а не предполагаем, что одинаковый `parent` сам по себе полностью описывает контекст child row.

---

## 7. Настроить колонки

В Report document настройте колонки с теми же fieldname, которые возвращает SQL.

Минимальная схема:

| Fieldname | Label | Fieldtype | Options |
|---|---|---|---|
| equipment | Equipment | Link | Equipment |
| rental | Rental | Link | Rental |
| customer | Customer | Link | Customer |
| status | Status | Data | |
| start_date | Start Date | Date | |
| end_date | End Date | Date | |
| owner | Owner | Link | User |

Так SQL отвечает за строки, а metadata Report — за представление колонок.

Не нужно кодировать labels и widths в SQL, если они уже описаны в Report document.

---

## 8. Сохранить и проверить исходники

Сохраните Report.

В терминале:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Должен появиться новый Standard Report внутри Module `Rental Training`, обычно в каталоге вида:

```text
rental_training/rental_training/report/equipment_rental_history/
```

Проверьте дерево:

```bash
find rental_training/rental_training/report/equipment_rental_history \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Конкретный набор файлов зависит от типа Report и patch-release. Контракт этапа:

```text
Standard Report экспортирован в исходники App
```

Откройте exported metadata и убедитесь, что там присутствуют:

```text
Equipment Rental History
Query Report
Rental
Rental Manager
from_date
to_date
query
```

---

## 9. Проверить отчёт под менеджером

Войдите под:

```text
manager@example.test
```

Откройте:

```text
Equipment Rental History
```

Укажите:

```text
From Date : 2026-09-01
To Date   : 2026-09-10
```

В контрольном наборе S00 должны появиться строки для Rentals, которые пересекают этот период, включая:

- A2, начавшийся до `from_date`;
- B3, заканчивающийся после `to_date`;
- Planned Rental A3, потому что history-report не фильтрует status.

Каждый Equipment внутри Rental даёт отдельную строку связи.

---

## 10. Проверить запрет для оператора

Войдите под:

```text
operator-a@example.test
```

Оператор не должен получить доступ к manager-only `Equipment Rental History`.

Если отчёт доступен оператору, не добавляйте в SQL условие:

```sql
r.owner = current_user
```

как случайную заплатку, пока предметное требование отчёта остаётся manager-only.

Сначала исправьте конфигурацию ролей/permissions самого Report.

Это разные задачи:

```text
кто вообще может запускать отчёт
→ Report permission + Report roles

какие строки выбирает SQL
→ query semantics
```

---

## 11. Посмотреть diff до коммита

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git diff
git status --short
```

Проверьте, что не появились:

```text
Users
рабочие Rentals
пароли
случайные fixtures
```

В diff должен быть только Standard Report и связанные с ним App-owned файлы.

После проверки зафиксируйте результат, например:

```bash
git add rental_training/rental_training/report/equipment_rental_history
git commit -m "feat: add equipment rental history report"
```

---

## 12. Граница Query Report

`Equipment Rental History` хорошо выражается одним запросом:

```text
выбрать строки
соединить parent/child данные
ограничить периодом
отсортировать
```

Но следующее требование другое:

> Для каждого Equipment посчитать уникальные занятые календарные дни, объединяя пересекающиеся интервалы, а затем вычислить процент загрузки.

SQL способен выразить многое, но текущая задача содержит самостоятельную программную обработку интервалов. Для учебного маршрута это естественная граница, после которой появляется `Script Report`, а не всё более сложный Query Report.

---

## Результат этапа

К концу S05:

```text
создан первый обязательный Standard Report App
filters передаются в SQL параметрами
запрос корректно учитывает пересечение периода
Query Report доступен только Rental Manager
If Owner не ошибочно считается автоматическим фильтром SQL
Report воспроизводимо находится в исходниках rental_training
```

На S06 появится вычислительная ответственность, которую мы вынесем в Python Script Report.
