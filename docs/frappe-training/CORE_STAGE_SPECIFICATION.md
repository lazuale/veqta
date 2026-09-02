# Исполняемая спецификация CORE-практикума Frappe

Статус: **черновик для финальной методической и инженерной проверки**.

Продолжает:

- [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md);
- [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md);
- [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md);
- [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md).

Этот документ фиксирует **что именно должен построить ученик в CORE**: точную модель, поля, naming, контрольные данные, права, тесты и критерий `ГОТОВО / НЕ ГОТОВО`.

Это ещё не инструкция «куда нажать». Подробные практические задания пишутся только после согласования спецификации.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md).

---

# 1. Правило спецификации

Каждый элемент обязан отвечать на требование:

```text
требование
→ ответственность
→ штатный механизм Frappe
→ конкретная конфигурация
→ контрольные данные
→ наблюдаемая проверка
```

Запрещено добавлять поле, DocType, Script, Workflow, Report или иной механизм только ради знакомства с функцией.

---

# 2. Граница учебной среды

CORE проходит на **отдельном чистом Site Frappe v16**.

До установки учебного App:

```text
installed apps:
frappe
```

После установки:

```text
installed apps:
frappe
rental_training
```

ERPNext и другие прикладные Apps для CORE не требуются.

Это не ограничение Frappe как Framework. Это граница практикума: ученик должен видеть, что именно предоставляет Frappe и что добавляет его собственный App, без случайных зависимостей от чужих моделей.

---

# 3. Имена учебных объектов

```text
App       : rental_training
Module    : Rental Training

DocTypes:
Equipment
Customer
Rental
Rental Item

Roles:
Rental Operator
Rental Manager
```

Предметная область учебная и нейтральная, не связана с VEQTA.

---

# 4. Naming и отображаемый title

У каждого самостоятельного Document есть системный `name`. В CORE он не строится из изменяемого отображаемого названия.

Используем штатный Expression naming:

```text
Equipment → EQ-.#####
Customer  → CUST-.#####
Rental    → RENT-.#####
```

Ожидаемый вид:

```text
EQ-00001
CUST-00001
RENT-00001
```

Для человекочитаемой работы Desk отдельно используются штатные title-настройки:

```text
Equipment
  Title Field               = equipment_name
  Show Title in Link Fields = yes

Customer
  Title Field               = customer_name
  Show Title in Link Fields = yes
```

Ученик должен увидеть разницу:

```text
name            = стабильная identity Document
Title Field     = человекочитаемое представление
equipment_name  = изменяемое название Equipment
customer_name   = изменяемое имя Customer
```

Изменение title-поля не должно менять `name` и ломать Link.

`Rental Item` — Child DocType, отдельная naming-стратегия для него не проектируется.

## Не используем

- серийный номер Equipment как `name`;
- имя Customer как `name`;
- Python `autoname()` без отдельного требования;
- UUID только ради демонстрации UUID;
- отдельный `naming_series` field, когда одного фиксированного Expression достаточно.

---

# 5. CORE-модель

```text
Equipment
Customer

Rental
├── customer        → Link → Customer
├── start_date      → Date
├── end_date        → Date
├── status          → Select
└── items           → Table MultiSelect → Rental Item

Rental Item
└── equipment       → Link → Equipment
```

В CORE нет дополнительных самостоятельных DocTypes.

`Rental Item` остаётся Child DocType, потому что `Table MultiSelect` во Frappe хранит выбранные ссылки через child-table модель. Обычный `Table` в CORE не нужен: у строки пока нет ни одного собственного бизнес-атрибута кроме ссылки на Equipment.

---

# 6. Equipment

## DocType

```text
Name       : Equipment
Module     : Rental Training
Standard   : yes
Child      : no
Single     : no
Submittable: no
```

## Fields

| Label | Fieldname | Type | Required | Unique | Дополнительно |
|---|---|---|---:|---:|---|
| Equipment Name | `equipment_name` | Data | yes | no | Title Field |
| Equipment Type | `equipment_type` | Select | yes | no | In List View |
| Serial Number | `serial_number` | Data | no | no | In List View |

`equipment_type`:

```text
Tool
Camera
Computer
```

Отдельного `Equipment Type` в CORE нет: у типа пока нет собственных атрибутов, lifecycle или управления.

`serial_number` — предметный атрибут, но не системная identity. Он намеренно не объявляется `Unique`, потому что CORE не предъявляет требования гарантировать его наличие и глобальную уникальность.

## Naming / view

```text
Expression                : EQ-.#####
Title Field               : equipment_name
Show Title in Link Fields : yes
```

## Контрольные записи

```text
EQ-00001
Equipment Name : Bosch GBH 2-26
Equipment Type : Tool
Serial Number  : BH-10001

EQ-00002
Equipment Name : Canon EOS R50
Equipment Type : Camera
Serial Number  : CR50-20001

EQ-00003
Equipment Name : Lenovo ThinkPad E14
Equipment Type : Computer
Serial Number  : LTP-30001
```

## Проверка

1. Создать все три записи.
2. Найти их через List.
3. Отфильтровать List по `equipment_type`.
4. В Link-поле убедиться, что пользователь видит человекочитаемый title, а запись сохраняет стабильный `name`.
5. Переименовать `Equipment Name` у `EQ-00001`.
6. Убедиться, что системный `name` и существующие Link не изменились.

## ГОТОВО

Ученик объясняет:

```text
почему Equipment = DocType
почему equipment_type = Select
почему serial_number ≠ name
почему name ≠ Title Field
```

## НЕ ГОТОВО

Если создан лишний `Equipment Type`, название/серийный номер необоснованно сделаны identity либо Equipment хранится только текстом внутри Rental.

---

# 7. Customer

## DocType

```text
Name       : Customer
Module     : Rental Training
Standard   : yes
Child      : no
Single     : no
Submittable: no
```

## Fields

| Label | Fieldname | Type | Required | Unique | Options |
|---|---|---|---:|---:|---|
| Customer Name | `customer_name` | Data | yes | no | — |
| Phone | `phone` | Data | no | no | `Phone` |
| Email | `email` | Data | no | no | `Email` |

Phone и Email остаются обычными свойствами Customer. Для них используется штатная типизация `Data`, а не собственная регулярка или Client Script.

## Naming / view

```text
Expression                : CUST-.#####
Title Field               : customer_name
Show Title in Link Fields : yes
```

## Контрольные записи

```text
CUST-00001
Customer Name : Anna Petrova
Phone         : +31 6 10000001
Email         : anna@example.test

CUST-00002
Customer Name : Mark de Vries
Phone         : +31 6 10000002
Email         : mark@example.test
```

`example.test` — учебный домен; реальные адреса не используются.

## Проверка

1. Создать двух Customer.
2. Использовать одного Customer в нескольких Rentals.
3. Изменить `customer_name` у `CUST-00001`.
4. Убедиться, что `name` и Link остаются прежними, а UI показывает новый title.

## ГОТОВО

Ученик объясняет, почему Customer является отдельным Document и почему текстовая копия имени в Rental не заменяет Link.

---

# 8. Rental Item

## DocType

```text
Name       : Rental Item
Module     : Rental Training
Standard   : yes
Child      : yes
Single     : no
Submittable: no
```

## Fields

| Label | Fieldname | Type | Required | Options | Дополнительно |
|---|---|---|---:|---|---|
| Equipment | `equipment` | Link | yes | `Equipment` | In List View = yes |

`In List View` для `equipment` обязателен в этой модели: `Table MultiSelect` определяет целевой Link через Link-поле Child DocType, отмеченное для list view.

В строке намеренно нет:

```text
quantity
price
status
responsible
return_date
comment
```

Одна строка означает одну выбранную конкретную единицу Equipment. Новые поля появятся только после новых требований.

Почему `Table MultiSelect`, а не обычный `Table`:

```text
текущее требование = выбрать несколько существующих Equipment
строка отношения   = только Link → Equipment
```

У обычного `Table` появится основание, если строка начнёт хранить собственные данные отношения, например состояние при выдаче или цену на момент проката.

## ГОТОВО

Rental Item существует только как часть Rental, а ученик может объяснить смысл `parent`, `parenttype`, `parentfield`, `idx`, почему строке не нужен самостоятельный CRUD и почему текущему требованию точнее соответствует `Table MultiSelect`.

---

# 9. Rental

## DocType

```text
Name         : Rental
Module       : Rental Training
Standard     : yes
Child        : no
Single       : no
Submittable  : no
Track Changes: не требуется для CORE
```

## Fields

| Label | Fieldname | Type | Required | Options | View |
|---|---|---|---:|---|---|
| Customer | `customer` | Link | yes | `Customer` | In List View |
| Start Date | `start_date` | Date | yes | — | In List View |
| End Date | `end_date` | Date | yes | — | In List View |
| Status | `status` | Select | yes | `Planned\nActive\nReturned` | In List View |
| Equipment | `items` | Table MultiSelect | yes | `Rental Item` | — |

## Default

```text
status = Planned
```

## Naming

```text
RENT-.#####
```

## Почему не Submittable

CORE пока моделирует рабочий объект со статусом. Требования фиксировать Rental как необратимый транзакционный факт нет.

```text
status = Returned
```

не означает:

```text
docstatus = Submitted
```

---

# 10. Контрольный набор Rentals

Один набор используется в Desk, серверных проверках и тестах.

## Rental A — валидный активный

```text
Customer   : CUST-00001
Start Date : 2026-09-10
End Date   : 2026-09-12
Status     : Active
Items:
- EQ-00001
- EQ-00002
```

Ожидание: сохраняется.

## Rental B — валидный Planned

```text
Customer   : CUST-00002
Start Date : 2026-09-15
End Date   : 2026-09-17
Status     : Planned
Items:
- EQ-00001
```

Ожидание: сохраняется.

## Rental C — неправильный период

```text
Customer   : CUST-00001
Start Date : 2026-09-20
End Date   : 2026-09-18
Status     : Planned
Items:
- EQ-00003
```

Ожидание: сервер отклоняет.

## Rental D — дубль строки

```text
Customer   : CUST-00001
Start Date : 2026-09-20
End Date   : 2026-09-22
Status     : Planned
Items:
- EQ-00003
- EQ-00003
```

Ожидание: сервер отклоняет.

## Rental E — конфликт активного периода

Создаётся после Rental A:

```text
Customer   : CUST-00002
Start Date : 2026-09-11
End Date   : 2026-09-13
Status     : Active
Items:
- EQ-00001
```

Ожидание: сервер отклоняет.

## Rental F — тот же Equipment без конфликта

```text
Customer   : CUST-00002
Start Date : 2026-09-13
End Date   : 2026-09-14
Status     : Active
Items:
- EQ-00001
```

Ожидание: сохраняется. Rental A заканчивается 12 сентября, новый начинается 13 сентября.

---

# 11. Серверные инварианты

CORE содержит ровно три собственных бизнес-правила.

## V01. Корректный период

```text
end_date >= start_date
```

Владелец: `Rental` Controller.

Естественная точка: `validate()`.

Client Script не является единственной гарантией.

## V02. Нет дубля Equipment внутри Rental

Для одного `Rental.items` значения `equipment` должны быть уникальны.

Владелец: `Rental` Controller.

`Table MultiSelect` является подходящим UI/control для выбора набора, но серверный инвариант не делегируется клиентскому поведению.

Оба локальных правила S05C должны быть доказаны не только через Desk Form, но и через обычный серверный `Document.insert()` без Client Script. Это подтверждает, что правило действительно принадлежит Document path.

Отдельный Rule Engine не создаётся.

## V03. Нет пересекающихся Active Rentals

В CORE Equipment считается занятым только при:

```text
status = Active
```

`Planned` и `Returned` Equipment не блокируют.

Периоды включительны и конфликтуют, если:

```text
existing.start_date <= current.end_date
AND
existing.end_date >= current.start_date
```

и найдено совпадающее Equipment.

При редактировании текущий Rental исключается из поиска конфликта по `name`.

Путь чтения V03:

```text
current Equipment
→ frappe.get_all("Rental Item", ...)
→ candidate parent Rentals
→ frappe.get_all("Rental", status/date filters)
→ conflict / no conflict
```

`get_all()` здесь выбран намеренно: V03 является внутренним инвариантом целостности и не должен пропустить конфликт только из-за permission-filtering пользовательского List. Это не отменяет правило использовать permission-aware путь (`get_list`, Desk) для пользовательских выборок.

Внутренний validator не должен без необходимости раскрывать пользователю имя/Customer/owner конфликтующего Rental, если будущая модель доступа может скрывать эту запись.

Минимальная проверка:

```text
Active 10–12 + Active 11–13 → запрещено
Active 10–12 + Active 12–14 → запрещено
Active 10–12 + Active 13–14 → разрешено
Planned overlap              → разрешено
Planned → Active при конфликте → запрещено
повторный save самого Active Rental → разрешено
```

V03 также должна блокироваться обычным `Document.insert()` без Form.

## Граница V03

Это последовательная учебная проверка, а не доказанная race-condition защита для двух параллельных транзакций.

В CORE не добавляются ручные `commit`, SQL-lock или отдельный reservation service ради имитации production-concurrency.

---

# 12. Базовая permission model

В CORE используются только:

```text
User
Role
DocType Permissions
```

Без `Permission Level`, `User Permission`, `Share`, permission hooks и собственного ACL.

## Rental Operator

| DocType | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Equipment | yes | no | no | no |
| Customer | yes | yes | yes | no |
| Rental | yes | yes | yes | no |

## Rental Manager

| DocType | Read | Create | Write | Delete |
|---|---:|---:|---:|---:|
| Equipment | yes | yes | yes | yes |
| Customer | yes | yes | yes | yes |
| Rental | yes | yes | yes | yes |

`Submit`, `Cancel`, `Amend` не используются: Rental не Submittable.

## Что принадлежит App

Роли обязательны для permission model приложения, поэтому экспортируются как fixtures.

`hooks.py` должен ограничивать fixture только этими ролями, например по `role_name`:

```text
Rental Operator
Rental Manager
```

После изменения обязательных Role выполняется штатный `export-fixtures`, а полученный fixture хранится в Git.

Permission rules Standard DocTypes находятся в метаданных самих DocTypes.

## Что принадлежит Site

Учебные Users являются тестовыми данными Site и в App не поставляются:

```text
operator@example.test → Rental Operator
manager@example.test  → Rental Manager
```

Пароли и реальные пользовательские аккаунты в репозиторий не записываются.

## Проверка

Под Operator:

- Equipment можно читать, нельзя создавать/изменять/удалять;
- Customer можно читать/создавать/изменять, нельзя удалять;
- Rental можно читать/создавать/изменять, нельзя удалять.

Под Manager разрешены все четыре CRUD-действия CORE.

## НЕ ГОТОВО

Если права проверены только под Administrator, ограничение существует только в UI либо обязательные Role после clean install приходится создавать вручную.

---

# 13. CORE-тесты

Тестируются только наши контракты.

Для DB/Document/permission сценариев Frappe v16 используется актуальный Frappe-aware integration test API:

```python
from frappe.tests import IntegrationTestCase
```

Минимальный набор:

```text
test_valid_rental_can_be_saved
test_end_date_before_start_date_is_rejected
test_duplicate_equipment_in_same_rental_is_rejected
test_overlapping_active_rental_is_rejected
test_touching_active_periods_are_rejected
test_non_overlapping_active_rental_is_allowed
test_planned_overlap_is_allowed
test_active_rental_does_not_conflict_with_itself
test_operator_cannot_create_equipment
test_operator_can_create_and_update_rental_but_cannot_delete_it
test_manager_can_manage_equipment
```

Тестовые Customer, Equipment и Users создаются самим test case. Он не должен зависеть от вручную созданных `EQ-00001`, `CUST-00001` или паролей dev-site.

## Не тестировать ради количества

```text
Frappe вообще умеет сохранять Document
Link вообще работает
Form вообще существует
```

## Запуск

Финальная проверка использует штатный Bench test runner для учебного Site/App.

---

# 14. CORE-этапы и критерии готовности

## S00 — среда

### ГОТОВО

- Frappe v16 работает;
- отдельный учебный Site открывается;
- до установки App на Site установлен только `frappe`;
- developer mode применим;
- Git доступен.

### НЕ ГОТОВО

Если практикум зависит от ERPNext, ручной правки Frappe core или неизвестной локальной настройки.

---

## S01 — App

### ГОТОВО

- `rental_training` существует как отдельный App;
- App установлен на учебный Site;
- `list-apps` показывает `frappe` + `rental_training`;
- Module существует внутри App;
- исходники находятся в Git.

---

## S02 — Equipment

### ГОТОВО

- схема соответствует разделу 6;
- naming и Title Field разделены;
- контрольные записи создаются;
- `equipment_type` остаётся Select.

---

## S03 — Customer

### ГОТОВО

- схема соответствует разделу 7;
- naming и Title Field разделены;
- Link позже использует настоящий Customer Document.

---

## S04 — Rental composition

### ГОТОВО

- Rental соответствует разделу 9;
- Rental Item — Child DocType;
- связи реализованы Link;
- набор Equipment реализован Table MultiSelect;
- один Rental содержит минимум два Equipment.

---

## S05A — status

### ГОТОВО

- `Planned / Active / Returned` — обычный предметный status;
- Workflow отсутствует;
- Rental не Submittable.

---

## S05B — Desk

### ГОТОВО

Equipment → Customer → Rental полностью проходит стандартными Form/List; человек видит title связанных Documents, а Link хранит их `name`.

---

## S05C — local invariants

### ГОТОВО

- Rental C и D отвергаются серверным `Document` path;
- корректные Documents сохраняются;
- V01 и V02 проверены через обычный `Document.insert()` без зависимости от Form/Client Script;
- Controller не выполняет ручной `commit`.

---

## S05D — permissions

### ГОТОВО

- Operator и Manager имеют разные реальные серверные права;
- Role входят в переносимое состояние App;
- Users остаются Site-local.

---

## S06 — cross-document invariant

### ГОТОВО

- пересекающийся Active Rental блокируется;
- общая граничная дата считается конфликтом;
- следующий день разрешён;
- Planned overlap разрешён;
- self-save текущего Active Rental разрешён;
- правило доказано обычным `Document.insert()`;
- системное чтение не зависит случайно от permission-filtering List;
- concurrency boundary сформулирована явно.

---

## S07 — tests

### ГОТОВО

- используется актуальный `IntegrationTestCase`, а не deprecated `FrappeTestCase`;
- test data создаются самим test case;
- инварианты V01/V02/V03 и permission contracts проходят через Bench test runner;
- намеренная поломка собственного правила валит соответствующий test;
- после восстановления полный suite снова зелёный.

---

## S08 — delivery audit

### ГОТОВО

Для каждого обязательного элемента указан владелец и источник восстановления:

```text
Module                        → App / modules.txt
DocType schema + permissions  → App / Standard DocType JSON
Controller V01/V02/V03        → App / rental.py
Role                          → App / hooks.py + fixtures/role.json
automated contracts           → App / test_rental.py
Users                         → Site-local data
business Documents            → Site-local data
developer_mode / allow_tests  → Site-local config
```

Дополнительно доказано:

- у CORE DocTypes нет скрытой обязательной зависимости от `Custom Field`, `Property Setter` или `Custom DocPerm`;
- повторный `export-fixtures` не оставляет необъяснённый Git diff;
- Users и runtime business data не поставляются fixtures;
- `bench migrate` проходит без ручного SQL и повторного накликивания модели;
- после migrate автоматические tests зелёные;
- App Git остаётся clean;
- patch не создаётся без реальной миграции существующих данных поддерживаемой предыдущей версии.

---

## S09 — clean install

### ГОТОВО

На новом чистом совместимом Site:

1. до установки есть только `frappe`;
2. `rental_training` устанавливается;
3. migrate проходит;
4. Standard DocTypes появляются из App;
5. обязательные Role появляются из fixture;
6. тесты проходят;
7. создаются Site-local учебные Users и контрольные business data;
8. валидный Rental сохраняется;
9. невалидные сценарии блокируются;
10. permissions соответствуют спецификации.

---

# 15. Что остаётся вне CORE

CORE **не получает автоматически**:

```text
Single DocType / Rental Settings
Track Changes / Comment / Attach
Permission Level
Assignment / ToDo
Workspace
Calendar
Print Format
Report Builder
Workflow
docstatus / Is Submittable
Equipment Type DocType
Web Form
Notification
REST integration
Webhook
Background Jobs
Server Script
custom frontend
```

Это NEXT/GATE/EXT и требует отдельного принятого требования.

---

# 16. Запрещённые упрощения будущих инструкций

Пошаговый практикум не должен:

- создавать обязательные модели через Customize Form вместо Standard DocType учебного App;
- предлагать ручной SQL вместо обычного Document/migrate-пути;
- делать бизнес-инвариант только Client Script;
- проверять permissions только под Administrator;
- использовать `ignore_permissions=True` как способ обойти неправильные права;
- создавать отдельные DocTypes для статуса, комментариев, истории или вложений без требования;
- превращать `Returned` в Submitted без транзакционной семантики;
- создавать собственный CRUD API в CORE;
- менять Frappe core;
- поставлять реальные Users/пароли как fixtures;
- требовать скрытых ручных действий после clean install.

---

# 17. Контроль перед написанием пошаговых заданий

На все вопросы должен быть ответ `да`:

```text
1. Поля минимальны и имеют предметный смысл?
2. Не осталось ли поля, семантика которого нигде не используется?
3. Naming отделён от изменяемого title?
4. Child DocType действительно является составом Rental?
5. status не перепутан с Workflow/docstatus?
6. Три собственных инварианта имеют серверного владельца?
7. Permission model остаётся штатной и минимальной?
8. Обязательные Role воспроизводятся из App, а Users остаются Site-local?
9. Контрольные данные однозначно проверяют happy path и ошибки?
10. Тесты проверяют наши контракты, а не Frappe ради coverage?
11. CORE не содержит NEXT/GATE/EXT ради знакомства?
12. Финальный критерий — clean install, а не «работает на моём dev-site»?
```

Если хотя бы один ответ отрицательный, сначала исправляется спецификация.