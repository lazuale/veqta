# L6. Совместная работа

L6 не добавляет новые предметные DocType и не добавляет поле исполнителя в `Service Request`.

Цель урока: организовать реальную работу с уже существующими заявками штатными средствами Frappe — назначение через `Assign To`, личные задачи через `ToDo`, обсуждение через Comments/Timeline, метки через Tags и визуальную очередь через Kanban.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

После урока рабочая схема выглядит так:

```text
Service Request
      │
      ├── Assign To ─────► ToDo ─────► Technician
      │
      ├── Comments / Timeline
      │
      ├── Tags
      │
      └── Kanban по Status
```

Ключевое разделение:

```text
Permission
= может ли пользователь работать с документом

Assignment
= кому поручена конкретная работа

Status
= в каком состоянии находится сама заявка
```

`Assign To` не заменяет `Status` и не требует собственного поля `Assigned Technician`.

---

# 1. Проверить состояние после L5

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

Должны существовать роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

и пользователи минимум:

```text
technician.one@example.com
supervisor.one@example.com
```

У `technician.one@example.com` после L5 действует `User Permission` на:

```text
Facility Location = Room 101
```

Поэтому для первого назначения используем заявку из `Room 101`, чтобы не смешивать назначение с новым Share.

---

# 2. Выбрать рабочую заявку

Под `supervisor.one@example.com` открыть `Service Request`.

Найти заявку с условиями:

```text
Location = Room 101
Status = New
```

Подойдёт, например, заявка:

```text
Subject: Не охлаждает кондиционер
Location: Room 101
Equipment: EQ-0001
```

Точный номер `SR-.....` зависит от данных site.

Перед назначением зафиксировать:

```text
Status = New
Assigned To = пусто
```

---

# 3. Назначить заявку через Assign To

В форме `Service Request` использовать штатное действие:

```text
Assign To
```

Выбрать:

```text
technician.one@example.com
```

Добавить короткое описание задания, например:

```text
Проверить работу кондиционера и зафиксировать результат.
```

Если интерфейс предлагает дату выполнения — указать ближайшую будущую дату.

Подтвердить назначение.

После назначения на форме должен появиться назначенный пользователь.

Не добавлять в `Service Request` поле:

```text
Assigned Technician
```

Frappe уже хранит назначение штатно.

---

# 4. Проверить, что появился ToDo

Через Awesomebar открыть:

```text
ToDo
```

Найти созданную запись.

Проверить связь:

```text
Allocated To / Assigned To
= technician.one@example.com

Reference Type
= Service Request

Reference Name
= выбранный SR-.....

Status
= Open
```

В исходниках Frappe `Assign To` создаёт обычный `ToDo`, где сохраняются:

```text
allocated_to
reference_type
reference_name
description
priority
status
date
assigned_by
```

Главный вывод:

```text
Assign To
не хранит исполнителя в новом поле нашей заявки

Assign To
создаёт связанную штатную запись ToDo
```

---

# 5. Проверить Status после назначения

Вернуться в исходный `Service Request`.

Проверить поле:

```text
Status
```

После обычного `Assign To` оно не обязано автоматически стать `Assigned`.

У нашего DocType нет специального поля `assigned_to`, и собственную автоматизацию мы не писали.

Поэтому разделяем два действия:

```text
назначить человеку
= Assign To

изменить бизнес-состояние заявки
= Status
```

Теперь вручную изменить:

```text
Status: New → Assigned
```

Сохранить.

Это намеренно ручной шаг. В L7 правила переходов будет контролировать Workflow.

---

# 6. Проверить работу глазами Technician

Выйти из Supervisor.

Войти как:

```text
technician.one@example.com
```

Открыть свою рабочую очередь через штатные элементы Desk / ToDo.

Найти назначенную заявку.

Проверить:

- ссылка ведёт на нужный `Service Request`;
- заявка доступна;
- видно назначение;
- ToDo относится именно к этому документу.

Открыть заявку и изменить:

```text
Status: Assigned → In Progress
```

Сохранить.

Пока это обычное изменение Select-поля.

Workflow появится только в L7.

---

# 7. Добавить комментарий

Оставаясь под Technician, в `Service Request` добавить обычный комментарий через штатную область Timeline/Comments.

Например:

```text
Проверка начата. Внутренний блок работает, требуется осмотр наружного блока.
```

Сохранить/отправить комментарий.

Проверить, что он появился в Timeline.

Не создавать:

```text
Service Request Comment
Work Note
Comment History
```

как собственные DocType.

Комментарий — штатная возможность Frappe.

---

# 8. Отличить Timeline от Track Changes

В той же заявке должны существовать разные виды активности.

Например:

```text
изменение Status
→ изменение Document / Version

назначение
→ Assignment activity

комментарий
→ Comment
```

Все они могут отображаться в общей Timeline, но это не одно и то же.

Ученик должен объяснить:

```text
Timeline
= интерфейс общей истории активности

Track Changes / Version
= история изменения полей Document

Comment
= отдельная пользовательская запись обсуждения
```

---

# 9. Завершить ToDo

Под `technician.one@example.com` открыть своё назначение.

Использовать штатное действие завершения assignment / ToDo.

Проверить, что активный ToDo больше не остаётся `Open`.

После этого снова открыть `Service Request`.

Важно:

```text
закрыть ToDo
≠ автоматически закрыть Service Request
```

Если Status заявки всё ещё `In Progress`, это нормальное поведение нашей текущей модели.

Для завершения учебного сценария вручную изменить:

```text
In Progress → Resolved
```

Сохранить.

---

# 10. Проверить повторное назначение

Под Supervisor взять другую заявку из `Room 101`.

Назначить её тому же Technician.

После этого проверить ToDo пользователя.

У него должно быть несколько отдельных заданий, каждое связано со своим:

```text
reference_type = Service Request
reference_name = конкретный SR-.....
```

То есть:

```text
один Technician
может иметь много ToDo

один ToDo
ссылается на конкретный рабочий документ
```

---

# 11. Проверить дублирующее назначение

На уже назначенной заявке ещё раз попытаться назначить того же пользователя, не закрывая первое активное назначение.

Frappe не должен создавать бессмысленный второй активный ToDo для той же пары:

```text
Service Request + Technician
```

На фактическом стенде проверить сообщение интерфейса.

Главное — понять, что assignment является отдельным управляемым объектом, а не строкой текста.

---

# 12. Добавить Tags

Выбрать несколько `Service Request` и добавить простые рабочие Tags.

Использовать, например:

```text
hvac
urgent-check
network
```

Пример:

```text
Не охлаждает кондиционер
→ hvac

Нет сети у коммутатора
→ network
```

Не превращать Tags в замену нормальным полям.

У нас уже есть структурированные поля:

```text
Priority
Status
Location
Equipment
```

Поэтому неверно создавать теги:

```text
High
New
Room 101
```

только для дублирования существующих данных.

Tags нужны для лёгкой дополнительной классификации, которой нет смысла давать отдельное поле.

---

# 13. Отфильтровать по Tag

Открыть `Service Request` List View.

Найти штатную фильтрацию/группировку по Tags и вывести, например:

```text
hvac
```

Проверить, что отображаются только соответствующие заявки.

После упражнения ученик должен различать:

```text
Select / Link
= структурированное поле модели

Tag
= дополнительная гибкая метка
```

---

# 14. Создать Kanban Board

Открыть `Service Request` List View.

Через переключатель представлений выбрать:

```text
Kanban
```

Если доски ещё нет, использовать:

```text
Create New Kanban Board
```

Создать доску:

```text
Board Name: Service Requests by Status
Reference DocType: Service Request
Field: Status
```

Колонки должны соответствовать значениям `Status`:

```text
New
Assigned
In Progress
Resolved
Closed
```

Не создавать отдельный DocType для колонки Kanban.

Frappe использует существующее поле `Status` как источник колонок.

---

# 15. Проверить Kanban как представление тех же Documents

Открыть доску.

Карточки должны представлять те же `Service Request`, которые уже существуют в List View.

Проверить одну заявку:

```text
List View
→ SR-..... / Status = Assigned

Kanban
→ та же заявка в колонке Assigned
```

Это не копия документа.

```text
List
Kanban
Form
```

— разные представления над теми же Documents.

---

# 16. Переместить карточку

Под пользователем с `Write` на `Service Request` переместить одну карточку:

```text
Assigned → In Progress
```

После этого открыть эту же заявку в Form View.

Проверить:

```text
Status = In Progress
```

На `v16.32.0` Kanban при переносе карточки записывает новое значение в поле, выбранное как `field_name` доски.

Главный вывод:

```text
перенос карточки Kanban
= изменение Status у существующего Service Request
```

Это не отдельная сущность процесса.

---

# 17. Проверить ограничения прав в Kanban

Войти под пользователем, у которого нет `Write` на все заявки, и проверить фактическое поведение доски.

Минимально:

- пользователь должен видеть только доступные ему Documents;
- пользователь без права изменения конкретной заявки не должен успешно менять её Status через обходной интерфейс;
- Kanban не должен отменять Role Permission / User Permission.

Не считать Kanban отдельной системой прав.

---

# 18. Проверить влияние L5 User Permission

Под `technician.one@example.com` открыть Kanban/List `Service Request`.

Из-за User Permission из L5 пользователь должен видеть только разрешённый ему набор, связанный с `Room 101`, плюс документы, которые были явно открыты ему через `Share`.

Проверить это на реальном стенде.

Главное:

```text
Kanban
использует те же permission rules,
что и остальные представления
```

---

# 19. Не смешивать Assignment и Kanban

Выбрать одну заявку и сравнить:

```text
Status = In Progress
Assigned To = technician.one@example.com
```

Это два независимых измерения.

Возможны ситуации:

```text
Status = New
но уже назначен Technician
```

или:

```text
Status = In Progress
но assignment снят
```

В текущем учебном приложении мы специально не пишем автоматизацию, которая насильно синхронизирует эти вещи.

Сначала нужно понять штатные механизмы по отдельности.

---

# 20. Проверить Git

После всех действий выполнить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

Ожидаем:

```text
working tree clean
```

Почему:

```text
ToDo
Comments
Tags
Kanban Board
изменённые Status
```

— это записи и конфигурация конкретного site, а не новый Standard DocType нашего app.

В L11 отдельно решим, какие конфигурационные записи нужно переносить вместе с приложением.

Не добавлять их вручную в Git сейчас.

---

# 21. Самостоятельная практика

Без пошаговой подсказки выполнить сценарий:

1. Supervisor выбирает новую заявку из `Room 101`.
2. Назначает её `technician.one@example.com`.
3. Technician находит её через свой ToDo.
4. Переводит заявку в `In Progress`.
5. Добавляет комментарий о ходе работы.
6. Добавляет уместный Tag.
7. Перемещает заявку на Kanban в `Resolved`.
8. Завершает своё ToDo.
9. Проверяет итоговую Timeline.

После этого ответить:

1. Где хранится исполнитель?
2. Что именно создаёт `Assign To`?
3. Почему ToDo и Status — разные вещи?
4. Что меняет перенос карточки Kanban?
5. Чем Comment отличается от Version?
6. Когда Tag полезнее отдельного поля, а когда нет?
7. Почему эти действия не изменили Git?

---

# 22. Приёмка L6

L6 принят, если ученик может показать следующее.

## Assign To / ToDo

- Supervisor назначил Service Request Technician;
- появился связанный ToDo;
- Technician видит свою работу;
- ToDo можно завершить;
- повторное активное назначение того же пользователя не создаёт бессмысленный дубль.

## Status

Ученик объясняет:

```text
Assign To
≠ Status
```

и понимает, почему назначение само по себе не обязано менять `Service Request.status`.

## Comments / Timeline

- комментарий добавлен;
- изменение Status видно в истории;
- assignment activity видна в Timeline;
- ученик различает Comment, Version и Timeline.

## Tags

- добавлен минимум один осмысленный Tag;
- выполнена фильтрация по Tag;
- Tags не дублируют Priority/Status/Location.

## Kanban

Создана доска:

```text
Service Requests by Status
```

с колонками:

```text
New
Assigned
In Progress
Resolved
Closed
```

Перенос карточки реально меняет поле `Status` у того же `Service Request`.

## Permissions

Под разными пользователями проверено, что Kanban и ToDo не отменяют ограничения L5.

## Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое.

## Итог L6

Теперь приложение умеет не только хранить заявки, но и поддерживать нормальную совместную работу без собственного поля исполнителя и без собственного модуля задач.

Следующий урок — **L7. Workflow**. Там свободное изменение `Status` будет заменено управляемыми переходами между состояниями.