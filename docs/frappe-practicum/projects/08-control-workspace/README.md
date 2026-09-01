# L8. Контроль работы

L8 собирает рабочий экран руководителя на уже существующих данных `Service Request`.

Новых предметных DocType нет.

Цель урока: получить один сохранённый Report Builder, три Number Card, один Dashboard Chart и один Workspace без SQL, Python и отдельной BI-системы.

Базовая версия: **Frappe Framework v16.32.0**.

## Результат

```text
Facility Operations Workspace

[ Open Requests ] [ High Priority ] [ Closed Requests ]

Service Requests by Status

Shortcuts:
- Service Request
- Equipment
- Facility Location
- Service Requests Overview
```

Основной источник данных один:

```text
Service Request
```

Мы не создаём отдельные таблицы статистики и не дублируем данные заявки.

---

# 1. Проверить состояние после L7

В терминале:

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
Git working tree clean
```

В Desk должны существовать:

```text
Facility Location
Equipment
Service Request
```

Workflow `Service Request Workflow` должен быть активен.

Для нормальной проверки нужны заявки минимум в трёх состояниях, например:

```text
New
In Progress
Closed
```

Если все учебные заявки оказались в одном Status, сначала распределить несколько записей штатными Workflow Actions.

---

# 2. Зафиксировать границу урока

L8 не строит отдельную аналитику.

Используем только штатные объекты Frappe:

```text
Report
Number Card
Dashboard Chart
Workspace
```

Они являются конфигурацией интерфейса над существующими Documents.

```text
Service Request
= рабочие данные

Report / Card / Chart / Workspace
= представление и контроль этих данных
```

---

# 3. Создать Report Builder

Войти под:

```text
Administrator
```

Developer Mode должен оставаться включённым.

Открыть:

```text
Service Request → List
```

Переключить представление:

```text
List → Report
```

Оставить в отчёте полезные поля:

```text
Name
Subject
Location
Equipment
Priority
Status
Target Date
Owner
Modified
```

Проверить фильтры, например:

```text
Status != Closed
```

Затем убрать временный фильтр, чтобы сохранённый отчёт показывал все заявки.

Сохранить Report Builder с именем:

```text
Service Requests Overview
```

Проверить созданный `Report` через Awesomebar:

```text
Report
```

Ожидается:

```text
Report Name:   Service Requests Overview
Report Type:   Report Builder
Reference DocType: Service Request
Module:        Facility Operations
Is Standard:   Yes
```

При создании Standard Report под Administrator в Developer Mode Frappe экспортирует его в app.

---

# 4. Проверить Group By

Открыть сохранённый:

```text
Service Requests Overview
```

В Report Builder включить группировку:

```text
Group By: Status
Aggregate: Count
```

Проверить, что результат показывает количество заявок по состояниям.

Например:

```text
New          3
Assigned     2
In Progress  2
Resolved     1
Closed       4
```

Конкретные числа зависят от учебных данных.

После проверки сохранить отчёт в таком виде.

Что нужно понять:

```text
Group By
= группировка Documents

Count
= агрегат над группой
```

SQL для этого не нужен.

---

# 5. Создать Number Card: Open Requests

Через Awesomebar открыть:

```text
Number Card
```

Создать:

```text
Label:         Open Requests
Type:          Document Type
Document Type: Service Request
Function:      Count
Is Public:     Yes
Is Standard:   Yes
Module:        Facility Operations
```

Filters:

```text
Status != Closed
```

Percentage Stats для базового урока отключить:

```text
Show Percentage Stats = No
```

Сохранить.

Проверить, что число совпадает с количеством незакрытых заявок.

---

# 6. Создать Number Card: High Priority

Создать вторую карточку:

```text
Label:         High Priority Requests
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

Сохранить.

Карточка должна считать только незакрытые заявки высокого приоритета.

---

# 7. Создать Number Card: Closed Requests

Создать третью карточку:

```text
Label:         Closed Requests
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

Сохранить.

На этом Number Card достаточно.

Не создавать отдельную карточку для каждого Status.

---

# 8. Проверить права Number Card

Войти под:

```text
supervisor.one@example.com
```

Проверить, что Supervisor может читать данные карточек.

Затем войти под:

```text
requester.one@example.com
```

Если открыть ту же Number Card напрямую, результат должен учитывать фактические права пользователя на `Service Request`.

Это важно:

```text
Number Card
не выдаёт доступ к данным сама по себе
```

Она использует разрешённые пользователю Documents.

---

# 9. Создать Dashboard Chart

Вернуться под:

```text
Administrator
```

Через Awesomebar открыть:

```text
Dashboard Chart
```

Создать:

```text
Chart Name:     Service Requests by Status
Chart Type:     Group By
Document Type:  Service Request
Group By Based On: Status
Group By Type:  Count
Type:           Bar
Is Public:      Yes
Is Standard:    Yes
Module:         Facility Operations
```

Filters оставить пустыми.

Сохранить.

Ожидаемый смысл графика:

```text
New          ███
Assigned     ██
In Progress  ██
Resolved     █
Closed       ████
```

Не важен внешний вид.

Важно, что график строится напрямую по `Service Request.status`.

---

# 10. Ограничить Chart ролью Supervisor

В `Dashboard Chart` в таблице Roles добавить:

```text
Facility Supervisor
```

Сохранить.

Проверить:

```text
supervisor.one@example.com
→ график доступен

technician.one@example.com
→ график не должен использоваться как его рабочий dashboard
```

Здесь роль ограничивает доступ к самому Chart.

Она не заменяет permissions исходного DocType.

---

# 11. Создать Workspace

Войти под Administrator.

Создать новый Workspace через штатный интерфейс Workspace:

```text
Title:  Facility Operations
Public: Yes
```

Для публичного Workspace требуется возможность управлять общими Workspace; Administrator подходит для настройки учебного стенда.

После создания открыть настройки Workspace и проверить:

```text
Title:  Facility Operations
Module: Facility Operations
Public: Yes
Type:   Workspace
```

В Roles оставить:

```text
Facility Supervisor
```

Рабочий Workspace предназначен руководителю, а не всем ролям приложения.

---

# 12. Добавить Number Cards в Workspace

Перевести Workspace в режим редактирования.

Добавить три Number Card:

```text
Open Requests
High Priority Requests
Closed Requests
```

Разместить их рядом в верхней части Workspace.

Не добавлять больше карточек только ради заполнения экрана.

---

# 13. Добавить Dashboard Chart

Ниже Number Cards добавить:

```text
Service Requests by Status
```

Проверить, что график отображает реальные данные.

Изменить Status одной тестовой заявки штатным Workflow Action.

Обновить Workspace.

Количество и график должны отражать новое состояние.

Никакого ручного обновления отдельной таблицы статистики быть не должно.

---

# 14. Добавить Shortcuts

Добавить в Workspace Shortcuts:

```text
Service Request
Equipment
Facility Location
Service Requests Overview
```

Для первых трёх использовать тип:

```text
DocType
```

Для последнего:

```text
Report
```

После сохранения проверить каждый Shortcut кликом.

---

# 15. Добавить один Quick List

Добавить в Workspace одну Quick List:

```text
Service Request
```

Цель — увидеть механизм Quick List.

Не пытаться превращать Workspace в полный альтернативный List View.

Если Quick List оказывается визуально лишней, после практики её можно удалить.

---

# 16. Проверить Workspace под Supervisor

Войти:

```text
supervisor.one@example.com
```

Открыть Workspace:

```text
Facility Operations
```

Проверить:

- видны три Number Card;
- виден Dashboard Chart;
- работают Shortcuts;
- открывается Report Builder;
- числа соответствуют доступным заявкам;
- можно перейти из Workspace к рабочим Documents.

Workspace должен быть рабочей точкой входа, а не декоративной страницей.

---

# 17. Проверить другую роль

Войти:

```text
technician.one@example.com
```

Публичный Workspace с Roles только:

```text
Facility Supervisor
```

не должен становиться основным Workspace Technician.

Не добавлять Technician в Roles только ради того, чтобы тест прошёл.

Смысл настройки — показать, что Workspace тоже имеет аудиторию.

---

# 18. Проверить source-файлы

Вернуться в терминал:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

После создания Standard объектов Git должен увидеть новые app-owned файлы для:

```text
Report
Number Card
Dashboard Chart
Workspace
```

Посмотреть их:

```bash
find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -E 'report|number_card|dashboard_chart|workspace'
```

Не редактировать эти JSON вручную.

---

# 19. Отличить app-owned configuration от рабочих данных

После L8 должно быть видно следующее:

```text
Service Request SR-00001
→ database site
→ не Git

Service Requests Overview
→ Standard Report
→ app source
→ Git

Open Requests
→ Standard Number Card
→ app source
→ Git

Service Requests by Status
→ Standard Dashboard Chart
→ app source
→ Git

Facility Operations Workspace
→ public app-owned Workspace
→ app source
→ Git
```

Это один из главных результатов L8.

---

# 20. Проверить отсутствие лишней аналитической модели

В приложении по-прежнему только три предметных DocType:

```text
Facility Location
Equipment
Service Request
```

Не должно появиться:

```text
Service Request Statistics
Dashboard Data
Request Summary
Status Counter
Analytics Record
```

Report/Card/Chart читают исходные Documents напрямую.

---

# 21. Commit L8

Проверить diff:

```bash
git status
git diff
```

Добавить только осознанно созданную Standard-конфигурацию:

```bash
git add .
git diff --cached
```

Проверить, что в staged diff нет рабочих Service Request или случайных файлов.

Commit:

```bash
git commit -m "Add facility operations workspace and dashboard"
git status
```

Ожидается:

```text
working tree clean
```

---

# 22. Самостоятельная практика

Без готовых кликов выполнить три задачи.

## A

Создать временную Number Card:

```text
New Requests
```

с фильтром:

```text
Status = New
```

Проверить результат и удалить карточку после практики.

## B

В `Service Requests Overview` сгруппировать заявки по Priority и сравнить результат с группировкой по Status.

После проверки вернуть Group By на Status.

## C

Добавить в Workspace Shortcut на сохранённый Report и убедиться, что он открывается под Supervisor.

---

# 23. Приёмка L8

L8 принят, если ученик может показать следующее.

## Report

```text
Service Requests Overview
Report Type = Report Builder
Reference DocType = Service Request
Group By = Status
Aggregate = Count
```

## Number Cards

```text
Open Requests
High Priority Requests
Closed Requests
```

и объяснить их Filters.

## Dashboard Chart

```text
Service Requests by Status
Chart Type = Group By
Group By Based On = Status
Group By Type = Count
```

## Workspace

```text
Facility Operations
```

с:

- тремя Number Card;
- одним Chart;
- Shortcuts;
- ролью `Facility Supervisor`.

## Архитектура

Ученик объясняет:

```text
Document
= данные

Report
= табличное представление/агрегация

Number Card
= одно вычисляемое число

Dashboard Chart
= визуальная агрегация

Workspace
= рабочая композиция этих элементов
```

## Git

Standard Report, Number Card, Dashboard Chart и публичный Workspace присутствуют в source app.

Рабочие Service Request в Git не попадают.

---

# Итог L8

После урока `facility_ops` уже выглядит как небольшое рабочее приложение:

```text
данные
→ процесс
→ права
→ совместная работа
→ Workflow
→ контроль и Workspace
```

Следующий урок — **L9. Автоматизация**: Notification, Assignment Rule и scheduler поверх уже работающего ручного процесса.
