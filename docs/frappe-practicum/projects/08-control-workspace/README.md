# L8. Контроль работы и Workspace

L8 строит контрольный экран над уже существующими `Service Request` без новой аналитической модели данных.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

## Создаём

```text
Report Builder:   Service Requests Overview
Number Card:      Open Requests
Number Card:      High Priority Requests
Number Card:      Closed Requests
Dashboard Chart:  Service Requests by Status
Workspace:        Facility Operations Control
```

Различать:

```text
Module    = Facility Operations
Workspace = Facility Operations Control
```

---

# 1. Preconditions

После L7:

```text
Service Request Workflow активен
Status values:
New
Accepted
In Progress
Resolved
Closed
```

Kanban `Service Request Status Board` удалён.

Проверить:

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Ожидается clean working tree.

---

# 2. Граница аналитики

Рабочие данные остаются в:

```text
Service Request
```

Не создаём:

```text
Analytics Request
Summary Table
Dashboard Data
BI Mart
```

Report/Card/Chart/Workspace — способы чтения и навигации.

Они **не выдают permission сами** и не заменяют Role Permission.

---

# 3. Report Builder

Создать:

```text
Report Name:       Service Requests Overview
Report Type:       Report Builder
Reference DocType: Service Request
Module:            Facility Operations
Is Standard:       Yes
```

Показать минимум:

```text
Subject
Location
Equipment
Priority
Status
Target Date
Modified
```

---

# 4. Group By Status

Сгруппировать по:

```text
Status
```

с Count.

Допустимые группы соответствуют реальной модели:

```text
New
Accepted
In Progress
Resolved
Closed
```

Пример результата:

```text
New          4
Accepted     2
In Progress  3
Resolved     1
Closed       5
```

Точные counts зависят от working data текущего site.

---

# 5. Open Requests

Создать Standard Number Card:

```text
Name:          Open Requests
Type:          Document Type
Document Type: Service Request
Function:      Count
Is Public:     Yes
Is Standard:   Yes
Module:        Facility Operations
```

Filter:

```text
Status != Closed
```

Здесь `Open` — аналитическое имя группы всех незакрытых заявок, а не отдельный Workflow state.

---

# 6. High Priority Requests

```text
Name:          High Priority Requests
Type:          Document Type
Document Type: Service Request
Function:      Count
Is Public:     Yes
Is Standard:   Yes
Module:        Facility Operations
```

Filters:

```text
Priority = High
Status != Closed
```

---

# 7. Closed Requests

```text
Name:          Closed Requests
Type:          Document Type
Document Type: Service Request
Function:      Count
Is Public:     Yes
Is Standard:   Yes
Module:        Facility Operations
```

Filter:

```text
Status = Closed
```

---

# 8. Permission-aware counts

Под Supervisor посмотреть Cards.

Под `requester.one@example.com` открыть доступную Number Card напрямую и сравнить count.

В `v16.32.0` Document Type Number Card использует штатный list-query с permissions.

Фиксируем:

```text
Card
→ считает только доступные query results

Card
≠ permission grant
```

---

# 9. Dashboard Chart

Создать:

```text
Chart Name:        Service Requests by Status
Chart Type:        Group By
Document Type:     Service Request
Group By Based On: Status
Group By Type:     Count
Type:              Bar
Is Public:         Yes
Is Standard:       Yes
Module:            Facility Operations
```

В Roles:

```text
Facility Supervisor
```

Chart показывает те же Status values:

```text
New / Accepted / In Progress / Resolved / Closed
```

---

# 10. Chart role vs data permission

Role `Facility Supervisor` ограничивает доступ к самому Chart object.

Это не означает, что Chart role заменяет permissions underlying `Service Request`.

Различать:

```text
доступ к визуализации
≠
доступ к исходным Documents
```

---

# 11. Workspace

Создать:

```text
Title:  Facility Operations Control
Public: Yes
Module: Facility Operations
Type:   Workspace
Roles:  Facility Supervisor
```

Не называть Workspace просто `Facility Operations`, чтобы не смешивать его с Module.

---

# 12. Наполнить Workspace

Добавить Number Cards:

```text
Open Requests
High Priority Requests
Closed Requests
```

Добавить Chart:

```text
Service Requests by Status
```

Shortcuts:

```text
Service Request
Equipment
Facility Location
Service Requests Overview
```

Quick List:

```text
Service Request
```

Не превращать Workspace в копию всего Desk.

---

# 13. Проверить под Supervisor

Войти:

```text
supervisor.one@example.com
```

Открыть:

```text
Facility Operations Control
```

Проверить:

```text
3 Number Cards
1 Dashboard Chart
Shortcuts
Quick List
Report link
```

---

# 14. Доказать отсутствие аналитической копии

Создать или изменить обычный `Service Request`, затем обновить Report/Card/Chart.

Показатели должны отражить актуальные working Documents.

```text
Service Request
= source operational data

Report/Card/Chart/Workspace
= read model / presentation
```

В базовом курсе отдельный OLAP/BI слой не создаётся.

---

# 15. Source и Git

Standard Report, Cards, Chart и Workspace при Developer Mode должны появиться в source app.

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations \
  -type f | sort \
  | grep -E 'report|number_card|dashboard_chart|workspace'
```

Не редактировать generated JSON вручную.

---

# 16. Commit

Добавить только app-owned Standard configuration.

Пример:

```bash
git commit -m "Add service request control workspace"
```

Working `Service Request` Documents в Git не попадают.

---

# 17. State contract L8

## Preconditions

```text
Workflow L7 active
Status set = New / Accepted / In Progress / Resolved / Closed
```

## Persistent mutations

```text
Service Requests Overview
Open Requests
High Priority Requests
Closed Requests
Service Requests by Status
Facility Operations Control
```

## Temporary mutations

```text
нет обязательных
```

## Output state

```text
один рабочий control Workspace
никаких новых domain DocType
```

## Git state

```text
Standard analytics/workspace source committed
working tree clean
```

---

# 18. Приёмка L8

L8 принят, если:

- Report Builder существует;
- Group By показывает только актуальные Status values, включая `Accepted`, не старый `Assigned`;
- существуют ровно три учебные Number Cards;
- Number Card counts permission-aware;
- существует `Service Requests by Status` Chart;
- существует `Facility Operations Control` Workspace;
- Module и Workspace различаются;
- визуализации не трактуются как permission boundary;
- никаких SQL/Python reports и аналитических копий data не создано;
- Standard configuration находится в source/Git;
- Git clean.

После L8 переходим к **L9 — автоматизация**.
