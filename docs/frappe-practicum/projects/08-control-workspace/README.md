# L8. Контроль работы и Workspace

L8 превращает накопленные `Service Request` в один рабочий экран контроля без новой аналитической модели данных.

Новых предметных DocType нет.

Базовая версия: **Frappe Framework v16.32.0**.

## Что создаём

```text
Report Builder:   Service Requests Overview
Number Card:      Open Requests
Number Card:      High Priority Requests
Number Card:      Closed Requests
Dashboard Chart:  Service Requests by Status
Workspace:        Facility Operations Control
```

Название Workspace специально **не совпадает** с Module:

```text
Module    = Facility Operations
Workspace = Facility Operations Control
```

Так новичок не путает технический Module приложения с отдельным рабочим экраном Desk.

---

# 1. Проверить состояние после L7

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

На site уже должны работать:

```text
Service Request Workflow
Facility Requester
Facility Technician
Facility Supervisor
```

Kanban `Service Request Status Board` после L7 удалён.

---

# 2. Зафиксировать границу аналитики

Рабочие данные уже находятся в:

```text
Service Request
```

L8 не создаёт:

```text
Analytics Request
Request Summary Table
Dashboard Data
BI Mart
```

Штатные Report/Card/Chart/Workspace читают существующие Documents с учётом permissions.

---

# 3. Создать Report Builder

Под Administrator открыть `Report` и создать:

```text
Report Name:        Service Requests Overview
Report Type:        Report Builder
Reference DocType:  Service Request
Module:             Facility Operations
Is Standard:        Yes
```

Сохранить.

Настроить отображаемые поля так, чтобы отчёт оставался рабочим и коротким, например:

```text
Subject
Location
Equipment
Priority
Status
Target Date
Modified
```

Не включать технические поля без необходимости.

---

# 4. Group By Status

В Report Builder сгруппировать по:

```text
Status
```

и использовать Count.

Цель — увидеть распределение текущих Service Request по состояниям без SQL/Python.

Пример смысла:

```text
New          4
Assigned     2
In Progress  3
Resolved     1
Closed       5
```

Точные числа зависят от данных site.

---

# 5. Создать Number Card Open Requests

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

Percentage stats не нужны.

---

# 6. Создать High Priority Requests

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

# 7. Создать Closed Requests

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

Не создавать отдельную карточку для каждого Status.

---

# 8. Проверить permissions Number Card

Под Supervisor проверить карточки.

Под `requester.one@example.com` открыть ту же Number Card напрямую и убедиться, что результат учитывает доступные ему `Service Request`.

Number Card не выдаёт доступ к данным самостоятельно: в `v16.32.0` Document Type Number Card получает данные штатным list-query с permissions.

---

# 9. Создать Dashboard Chart

Создать:

```text
Chart Name:         Service Requests by Status
Chart Type:         Group By
Document Type:      Service Request
Group By Based On:  Status
Group By Type:      Count
Type:               Bar
Is Public:          Yes
Is Standard:        Yes
Module:             Facility Operations
```

Filters оставить пустыми.

В Roles добавить:

```text
Facility Supervisor
```

Chart отвечает на вопрос распределения заявок по Status и не является Kanban.

---

# 10. Проверить Chart permissions

Под Supervisor график должен быть доступен.

Под Technician он не должен использоваться как его рабочий dashboard, если доступ к Chart ограничен Role `Facility Supervisor`.

Role на Chart ограничивает сам объект Chart и не заменяет permissions `Service Request`.

---

# 11. Создать Workspace

Под Administrator создать новый Workspace:

```text
Title:  Facility Operations Control
Public: Yes
Module: Facility Operations
Type:   Workspace
```

В Roles оставить:

```text
Facility Supervisor
```

Различать:

```text
Facility Operations
= Module app

Facility Operations Control
= рабочий Workspace руководителя
```

---

# 12. Добавить Number Cards

В верхнюю часть Workspace добавить:

```text
Open Requests
High Priority Requests
Closed Requests
```

Не заполнять экран карточками ради количества.

---

# 13. Добавить Dashboard Chart

Ниже добавить:

```text
Service Requests by Status
```

Проверить, что он отображает данные `Service Request` текущего site.

---

# 14. Добавить Shortcuts

Добавить Shortcuts:

```text
Service Request
Equipment
Facility Location
Service Requests Overview
```

Workspace должен быть входной точкой контроля, а не копией всего Desk.

---

# 15. Добавить Quick List

Добавить один Quick List:

```text
Document Type: Service Request
```

Проверить несколько последних/доступных заявок.

Один Quick List достаточен для изучения механизма.

---

# 16. Проверить Workspace под Supervisor

Войти как:

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
Dashboard Chart
Shortcuts
Quick List
```

и переход в `Service Requests Overview`.

---

# 17. Проверить границу Workspace

Workspace не хранит копию Service Request.

Изменить или создать рабочую заявку штатным способом, затем обновить Card/Chart/Report.

Результат должен строиться по актуальным Documents.

```text
Service Request
= данные

Report / Card / Chart / Workspace
= app-owned способы чтения и навигации
```

---

# 18. Проверить source и Git

Report, Number Cards, Dashboard Chart и Workspace создаются как Standard objects с Module `Facility Operations`.

В Developer Mode они должны появиться в source app.

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -E 'report|number_card|dashboard_chart|workspace'
```

Не редактировать exported JSON вручную.

---

# 19. Commit L8

Добавить только app-owned Standard configuration и проверить staged diff.

Пример commit:

```bash
git commit -m "Add service request control workspace"
```

Рабочие `Service Request` в Git не добавляются.

---

# 20. Приёмка L8

L8 принят, если:

- существует `Service Requests Overview` как Report Builder;
- существуют ровно три учебные Number Cards;
- существует `Service Requests by Status` как Group By Count Chart;
- Chart ограничен Facility Supervisor;
- существует Workspace `Facility Operations Control`;
- Module и Workspace больше не имеют одинаковое имя;
- Workspace содержит Cards, Chart, Shortcuts и один Quick List;
- показатели отражают актуальные Service Request и permissions;
- Standard configuration находится в app source/Git;
- никакой SQL/Python/отдельной аналитической таблицы не создано.

После L8 переходим к **L9 — автоматизация**.