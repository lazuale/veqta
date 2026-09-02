# CORE — спецификация практических этапов Frappe

Статус: **черновик для архитектурной проверки**.

Этот документ фиксирует точный контракт CORE до написания пошаговых инструкций ученика.

Он продолжает:

- [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md);
- [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md);
- [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md);
- [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md).

Задача спецификации — убрать двусмысленность из практикума. После неё автор инструкции не должен заново придумывать поля, naming, роли, контрольные данные или смысл проверки.

---

# 1. Глобальные фиксированные решения CORE

```text
App        : rental_training
Module     : Rental Training
Site       : rental.localhost
Frappe     : version 16
```

Предметная модель:

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

CORE намеренно не содержит других самостоятельных предметных DocTypes.

---

# 2. Naming — обязательное решение D00

У каждого самостоятельного Document системный `name` отделён от человекочитаемого title.

```text
Equipment → EQ-.#####
Customer  → CUST-.#####
Rental    → RENT-.#####
```

Почему:

- `name` является стабильной identity для Links;
- отображаемое название может измениться;
- бизнес-поле не делается вечным ID только ради краткости;
- собственный Python `autoname()` не нужен, пока Expression naming выражает требование.

Для Equipment и Customer используется штатный `Title Field` + `Show Title in Link Fields`, чтобы пользователь работал с понятными названиями, а ссылки сохраняли стабильный `name`.

Не требуется доказывать, что эта naming strategy универсальна для любых приложений. Практикум должен показать, что naming выбирается осознанно при создании DocType.

---

# 3. Что намеренно не входит в модель

Без нового требования не добавляются:

```text
Equipment Type DocType
Rental Settings
Rental Status DocType
Priority
Rental History
Rental Comment
Rental Assignee
Approval
Notification Log
Rental Request
```

Также в CORE нет полей «на всякий случай», например `active`, если ни один текущий контракт не определяет их поведение.

---

# 4. Equipment

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

# 5. Customer

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

# 6. Rental Item

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

# 7. Rental

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

# 8. Контрольный набор Rentals

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

# 9. Серверные инварианты

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

При редактировании текущий Rental исключается из поиска по `name`.

### Точный путь чтения V03

Проверка выполняется в `Rental.validate()` двумя штатными чтениями:

```text
current Equipment
→ frappe.get_all("Rental Item", ...)
→ candidate parent Rentals
→ frappe.get_all("Rental", status/date filters)
→ conflict / no conflict
```

`get_all()` выбран здесь намеренно: это внутренний инвариант целостности, и он не должен пропускать реальный конфликт из-за permission-filtering пользовательского List. Пользовательские выборки при этом остаются permission-aware (`get_list`/обычный Desk).

Внутренний validator не должен без необходимости раскрывать пользователю данные конфликтующего Rental, если будущая модель доступа может их скрывать.

### Проверка V03

Минимум:

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

# 10. Базовая permission model

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

# 11. CORE-тесты

Тестируются только наши контракты.

Минимальный набор:

```text
test_valid_rental_can_be_saved
test_end_date_before_start_date_is_rejected
test_duplicate_equipment_in_same_rental_is_rejected
test_overlapping_active_rental_is_rejected
test_non_overlapping_active_rental_is_allowed
test_operator_cannot_create_equipment
test_operator_can_create_rental
```

Названия можно изменить, если смысл сохраняется.

## Не тестировать ради количества

```text
Frappe вообще умеет сохранять Document
Link вообще работает
Form вообще существует
```

## Запуск

Финальная проверка использует штатный Bench test runner для учебного Site/App.

---

# 12. Delivery ownership

Обязательное состояние CORE должно иметь явного владельца.

```text
Standard DocType JSON → App source
Controller Python     → App source
Role records          → filtered fixtures
Default DocPerm       → Standard DocType metadata
training Users        → Site-only data
runtime Equipment/Customer/Rental → Site data
```

Изменение Python Controller само по себе не является schema migration и не требует ритуального `bench migrate`.

Изменение metadata/schema синхронизируется штатным `migrate`.

`patch` появляется только когда существующие данные действительно надо преобразовать.

---

# 13. CORE-этапы и критерии готовности

## S00 — среда

### ГОТОВО

- Frappe v16 работает;
- отдельный учебный Site открывается;
- до установки App на Site установлен только `frappe`;
- developer mode применим;
- Git доступен.

### НЕ ГОТОВО

Если практикум зависит от ERPNext, ручной правки Frappe core или неизвестной локальной настройки.

## S01 — App

### ГОТОВО

- `rental_training` существует как отдельный App;
- App установлен на учебный Site;
- `list-apps` показывает `frappe` + `rental_training`;
- Module существует внутри App;
- исходники находятся в Git.

## S02 — Equipment

### ГОТОВО

- схема соответствует разделу 4;
- naming и Title Field разделены;
- контрольные записи создаются;
- `equipment_type` остаётся Select.

## S03 — Customer

### ГОТОВО

- схема соответствует разделу 5;
- naming и Title Field разделены;
- Data Email/Phone используют штатную типизацию;
- Customer существует независимо от Rental.

## S04 — Rental composition

### ГОТОВО

- `Rental Item` — Child DocType;
- `equipment` — Link + In List View;
- `Rental.items` — Table MultiSelect;
- `Rental.customer` — Link;
- child ownership подтверждён;
- обычный Table не введён без атрибутов строки.

## S05A — status

### ГОТОВО

- status = Planned/Active/Returned;
- Workflow отсутствует;
- Is Submittable отсутствует;
- Returned Document остаётся docstatus 0.

## S05B — Desk

### ГОТОВО

Полный сценарий Equipment → Customer → Rental проходит через Desk Form/List без собственного frontend, а runtime Documents не меняют Git App.

## S05C — локальные инварианты

### ГОТОВО

V01/V02 блокируются и через Desk, и обычным `Document.insert()`; Controller не содержит ручного `commit`.

## S05D — permissions

### ГОТОВО

Operator/Manager имеют ожидаемую CRUD-матрицу при реальных server-side операциях; обязательные Role/DocPerm воспроизводимы из App, а Users остаются Site-local.

## S06 — cross-document invariant

### ГОТОВО

V03 соответствует включительной формуле дат, учитывает только Active, исключает self, не зависит от permission-filtered List и блокируется обычным `Document.insert()`. Граница с concurrency названа явно.

## S07 — tests

### ГОТОВО

Автоматически проверяются три инварианта и обязательные permission-контракты.

## S08 — delivery audit

### ГОТОВО

Для каждого обязательного элемента известно: владелец, source of truth и механизм доставки на другой Site.

## S09 — clean install

### ГОТОВО

```text
clean compatible Frappe Site
+ rental_training from Git
+ install-app
+ migrate
+ tests
+ main Desk scenario
```

работают без скрытой ручной реконструкции App state.

---

# 14. Явные исключения CORE

CORE не расширяется ради покрытия возможностей Framework.

Без отдельного требования не вводятся:

```text
Single DocType
Permission Level
Permission Type
If Owner
User Permission
Share
Workspace
Calendar
Print Format
Report Builder
Workflow
Is Submittable
Web Form
Notification
REST integration
Background Jobs
Scheduler
custom frontend
custom ACL
reservation service
manual SQL locks
```

---

# 15. Финальный контракт CORE

```text
clean compatible Frappe Site
+ training App from Git
+ install-app
+ migrate
+ tests
+ main user scenario
= CORE practicum passed
```

До S07 этот критерий ещё не доказан: ручные проверки должны стать автоматическими контрактами.