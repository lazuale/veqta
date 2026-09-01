# L4. Заявка на обслуживание

L4 добавляет третий и последний основной DocType приложения — `Service Request`.

Цель урока: собрать первый настоящий рабочий документ `facility_ops`, связать его одновременно с местом и оборудованием и получить простую очередь заявок, которая пока работает без ролей, назначений и Workflow.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

После урока ядро приложения полностью собрано:

```text
Facility Location
      │
      ├────────► Equipment
      │              │
      └──────────────┴────────► Service Request
```

`Service Request` всегда связан с `Facility Location`.

Связь с `Equipment` необязательна:

```text
сломался кондиционер
→ Location + Equipment

протекает потолок
→ только Location
```

Поля `Service Request`:

| Label | Fieldname | Type | Mandatory | Default |
|---|---|---|---:|---|
| Subject | `subject` | Data | Yes | |
| Location | `location` | Link → Facility Location | Yes | |
| Equipment | `equipment` | Link → Equipment | No | |
| Description | `description` | Text | Yes | |
| Priority | `priority` | Select | Yes | Medium |
| Status | `status` | Select | Yes | New |
| Target Date | `target_date` | Date | No | |
| Attachment | `attachment` | Attach | No | |

Priority:

```text
Low
Medium
High
```

Status:

```text
New
Assigned
In Progress
Resolved
Closed
```

Naming:

```text
Naming Rule: Expression
Auto Name:   SR-.#####
```

Примеры:

```text
SR-00001
SR-00002
SR-00003
```

Title Field:

```text
subject
```

Track Changes:

```text
Yes
```

---

# 1. Проверить состояние после L3

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
```

и рабочие данные из предыдущих уроков.

Минимально должны существовать Locations:

```text
Room 101
Room 102
Floor 1
Floor 2
Warehouse
```

и Equipment:

```text
EQ-0001
EQ-0004
EQ-0006
```

Если L3 не принят — L4 не начинаем.

---

# 2. Зафиксировать модель до кликов

`Service Request` — обычный Standard DocType.

Он не является:

- Tree;
- Child Table;
- Single;
- Submittable.

Каждый Document — отдельная заявка.

Пример:

```text
name:        SR-00001
Subject:     Не охлаждает кондиционер
Location:    Room 101
Equipment:   EQ-0001
Priority:    High
Status:      New
```

Главное отличие от Equipment:

```text
Equipment
= относительно постоянная карточка объекта

Service Request
= рабочий документ, который меняется по ходу процесса
```

---

# 3. Создать Standard DocType Service Request

В Desk через Awesomebar открыть:

```text
DocType
```

Создать новый DocType:

```text
Name:   Service Request
Module: Facility Operations
Custom: выключено
```

Не включать:

```text
Is Tree
Is Child Table
Is Single
Is Submittable
```

Сейчас заявка специально остаётся обычным Document.

`Draft / Submit / Cancel / Amend` изучаются отдельно в лаборатории, а не навязываются заявке.

---

# 4. Добавить основные поля

Добавить поля в следующем порядке.

## Subject

```text
Label:      Subject
Fieldname:  subject
Type:       Data
Mandatory:  Yes
```

Это короткая суть проблемы.

Пример:

```text
Не охлаждает кондиционер
```

## Location

```text
Label:      Location
Fieldname:  location
Type:       Link
Options:    Facility Location
Mandatory:  Yes
```

Любая заявка должна относиться к месту.

## Equipment

```text
Label:      Equipment
Fieldname:  equipment
Type:       Link
Options:    Equipment
Mandatory:  No
```

Оборудование указывается только если проблема относится к конкретной единице.

---

# 5. Добавить описание

Добавить `Section Break`:

```text
Label: Details
```

После него добавить:

## Description

```text
Label:      Description
Fieldname:  description
Type:       Text
Mandatory:  Yes
```

`Subject` отвечает на вопрос «что случилось кратко».

`Description` — «что именно наблюдаем».

Не дублировать одно и то же содержание в обоих полях.

---

# 6. Добавить управление очередью

Добавить `Section Break`:

```text
Label: Processing
```

Добавить поля:

## Priority

```text
Label:      Priority
Fieldname:  priority
Type:       Select
Mandatory:  Yes
Default:    Medium
Options:
Low
Medium
High
```

## Status

```text
Label:      Status
Fieldname:  status
Type:       Select
Mandatory:  Yes
Default:    New
Options:
New
Assigned
In Progress
Resolved
Closed
```

## Column Break

Добавить `Column Break`.

## Target Date

```text
Label:      Target Date
Fieldname:  target_date
Type:       Date
Mandatory:  No
```

## Attachment

```text
Label:      Attachment
Fieldname:  attachment
Type:       Attach
Mandatory:  No
```

В результате форма должна оставаться короткой:

```text
[ Subject ]      [ Location ]
                 [ Equipment ]

Details
[ Description                         ]

Processing
[ Priority ]     [ Target Date ]
[ Status   ]     [ Attachment  ]
```

Не добавлять пока:

- исполнителя;
- подразделение;
- отдельный справочник Priority;
- отдельный справочник Status;
- даты каждого перехода;
- собственные комментарии;
- собственную историю.

---

# 7. Настроить Naming

В Naming DocType `Service Request` выбрать:

```text
Naming Rule: Expression
Auto Name:   SR-.#####
```

Смысл:

```text
Subject
= бизнес-заголовок

name
= системный уникальный номер заявки
```

Например:

```text
name    = SR-00001
Subject = Не охлаждает кондиционер
```

Следующая заявка с тем же Subject всё равно получит новый `name`.

Это сознательно отличается от `Equipment`, где `name` задаётся полем `Equipment Code`.

---

# 8. Настроить Title Field и поиск

Указать:

```text
Title Field: subject
```

Search Fields:

```text
location,equipment,priority,status
```

Нужно различать:

```text
name
= SR-00001

Title Field
= Не охлаждает кондиционер
```

Позже `Service Request` будет удобнее искать по связанному месту, Equipment и состоянию.

---

# 9. Включить Track Changes

В настройках DocType включить:

```text
Track Changes = Yes
```

Это важно для рабочего документа, потому что его Status, Priority и другие данные будут меняться.

Не создаём собственный журнал изменений.

---

# 10. Сохранить DocType

После сохранения ещё раз открыть `Service Request` и проверить:

```text
Module = Facility Operations
Custom = No
Is Tree = No
Is Submittable = No
Naming Rule = Expression
Auto Name = SR-.#####
Title Field = subject
Track Changes = Yes
```

---

# 11. Проверить generated metadata

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations/doctype/service_request \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидается boilerplate примерно:

```text
__init__.py
service_request.js
service_request.json
service_request.py
test_service_request.py
```

Открыть metadata:

```bash
sed -n '1,360p' \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

Найти:

```text
"name": "Service Request"
"module": "Facility Operations"
"naming_rule": "Expression"
"autoname": "SR-.#####"
"title_field": "subject"
"track_changes": 1
```

и поля:

```text
subject
location
equipment
description
priority
status
target_date
attachment
```

JSON вручную не редактировать.

---

# 12. Создать первую заявку с Equipment

Открыть:

```text
Service Request → New
```

Создать:

```text
Subject:     Не охлаждает кондиционер
Location:    Room 101
Equipment:   EQ-0001
Description: Кондиционер включается, но температура в помещении не снижается.
Priority:    High
Status:      New
Target Date: выбрать ближайшую будущую дату
```

Сохранить.

Проверить, что Frappe присвоил имя вида:

```text
SR-00001
```

Точное число зависит от состояния site.

Главное — формат:

```text
SR- + 5 цифр
```

---

# 13. Создать заявку без Equipment

Создать вторую заявку:

```text
Subject:     Не работает освещение
Location:    Floor 1
Equipment:   пусто
Description: В коридоре первого этажа не работает часть светильников.
Priority:    Medium
Status:      New
```

Сохранить.

Заявка должна успешно создаться.

Главное правило модели:

```text
Location
= обязательно

Equipment
= только когда существует конкретный объект Equipment
```

Не создавать фиктивный Equipment вроде `General` или `Building` ради заполнения Link.

---

# 14. Проверить обязательный Location

Попробовать создать:

```text
Subject:     Тест без места
Location:    пусто
Description: Проверка обязательности Location
Priority:    Low
Status:      New
```

Сохранение должно быть остановлено обязательностью `Location`.

После проверки запись не сохранять.

---

# 15. Проверить Link на несуществующий Equipment

В новой заявке попробовать указать в поле Equipment значение, которого нет в реестре, например:

```text
EQ-NOT-EXISTS
```

Обычный Link должен ссылаться на существующий Document `Equipment`.

Не создаём Equipment из текста заявки автоматически.

После проверки отменить тестовую запись.

---

# 16. Создать рабочий набор заявок

Создать минимум 8 заявок.

Использовать разные места, оборудование, Priority и Status.

Пример набора:

| Subject | Location | Equipment | Priority | Status |
|---|---|---|---|---|
| Не охлаждает кондиционер | Room 101 | EQ-0001 | High | New |
| Не работает освещение | Floor 1 | — | Medium | New |
| Нет сети у коммутатора | Room 101 | EQ-0004 | High | In Progress |
| Проверить ИБП | Warehouse | EQ-0006 | Low | Assigned |
| Шум от кондиционера | Room 102 | EQ-0002 | Medium | New |
| Повреждена розетка | Room 102 | — | High | Resolved |
| Убрать старое оборудование | Floor 2 | EQ-0008 | Low | Closed |
| Слабый сигнал Wi-Fi | Room 102 | EQ-0005 | Medium | In Progress |

Не стремиться воспроизвести номера `SR-...` из примера.

Frappe назначает их сам.

---

# 17. Проверить обычный Status до Workflow

Открыть одну заявку со Status:

```text
New
```

Вручную изменить:

```text
New → Closed
```

Сохранить.

На этом этапе Frappe должен позволить изменение, потому что `Status` пока обычный `Select`.

После проверки вернуть заявке логичное состояние.

Что нужно понять:

```text
Select Status
= хранит состояние

но сам по себе
не описывает допустимые переходы
```

Это сознательная подготовка к L7 Workflow.

---

# 18. Проверить Track Changes

Открыть одну рабочую заявку.

Например изменить:

```text
Priority: Medium → High
```

и:

```text
Status: New → In Progress
```

Сохранить.

В Timeline проверить историю изменений.

Затем вернуть данные в состояние, подходящее тестовому сценарию.

Вывод:

```text
Track Changes
= штатная история изменения Document
```

Отдельный `Service Request History` DocType не нужен.

---

# 19. Проверить Attachment

К одной заявке прикрепить небольшой тестовый файл через поле:

```text
Attachment
```

Например фотографию или простой документ.

После сохранения убедиться, что файл доступен из заявки.

Не хранить путь к файлу вручную в Data field.

---

# 20. Поработать со списком

Открыть List View `Service Request`.

Проверить фильтры:

```text
Status = New
Priority = High
Location = Room 101
Equipment = EQ-0001
```

Затем комбинированный фильтр:

```text
Status != Closed
Priority = High
```

Сейчас Saved Filters повторно подробно не изучаем — механизм уже пройден в L3.

Главная задача — увидеть, что рабочий Document естественно образует очередь.

---

# 21. Отличить три основных DocType

После L4 ученик должен уже видеть разницу между всеми тремя сущностями ядра.

```text
Facility Location
= иерархический справочник мест

Equipment
= карточка относительно постоянного объекта

Service Request
= изменяемый рабочий документ
```

Их не объединяем в один универсальный DocType.

И не делим на десяток сущностей без необходимости.

---

# 22. Проверить Git после создания рабочих данных

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

Git должен видеть metadata нового Standard DocType `Service Request`.

Созданные заявки:

```text
SR-.....
SR-.....
SR-.....
```

не должны превращаться в source-файлы app.

Итог:

```text
service_request.json
= metadata app
= Git

конкретный SR-00001
= рабочий Document
= database site
```

---

# 23. Зафиксировать L4 в Git

Проверить:

```bash
git status
git diff
```

Добавить metadata:

```bash
git add .
git diff --cached
```

Commit:

```bash
git commit -m "Add service request doctype"
git status
```

Ожидается:

```text
working tree clean
```

Рабочие Service Request остаются в database site и в commit не попадают.

---

# 24. Самостоятельная практика

Без готовой пошаговой инструкции выполнить три действия.

## Сценарий A

Создать заявку на конкретное Equipment со Status `New` и Priority `High`.

## Сценарий B

Создать заявку на помещение без Equipment.

## Сценарий C

Вывести List View только с незакрытыми заявками высокого приоритета.

После выполнения ответить:

1. Почему Equipment необязателен?
2. Почему Location обязателен?
3. Почему Subject не используется как `name`?
4. Почему Status пока можно менять свободно?
5. Где хранится Attachment?
6. Какие из выполненных действий должны изменить Git?

---

# 25. Приёмка L4

L4 принят, если ученик может показать следующее.

## В Desk

- существует Standard DocType `Service Request`;
- Module = `Facility Operations`;
- Naming создаёт `SR-.....`;
- Subject используется как Title Field;
- Location — обязательный Link на `Facility Location`;
- Equipment — необязательный Link на `Equipment`;
- Priority и Status работают как Select;
- Target Date работает как Date;
- Attachment принимает файл;
- Track Changes показывает историю;
- создано минимум 8 рабочих заявок.

## В модели

Ученик без подсказки объясняет:

```text
Facility Location
→ где

Equipment
→ что эксплуатируем

Service Request
→ что произошло и что нужно обработать
```

## В процессе

Ученик понимает:

```text
Status
= значение текущего состояния

Workflow
= будущие правила переходов
```

Workflow в L4 ещё не создаётся.

## В Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое после commit.

## Итог L4

Основная предметная модель `facility_ops` закончена:

```text
3 DocType
1 рабочий процесс
0 лишних сущностей
```

Дальше новые основные DocType для курса не нужны.

Следующий урок — **L5. Пользователи и права**. В нём впервые перестаём работать только под `Administrator` и проверяем приложение глазами разных пользователей.