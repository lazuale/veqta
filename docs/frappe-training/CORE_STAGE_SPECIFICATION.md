# Исполняемая спецификация CORE-практикума Frappe

Статус: **черновик для финальной методической и инженерной проверки**.

Продолжает:

- [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md);
- [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md);
- [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md);
- [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md).

Этот документ фиксирует **что именно должен построить ученик в CORE**. Здесь впервые задаются конкретные поля, контрольные данные, проверки и критерий `ГОТОВО / НЕ ГОТОВО`.

Документ не является пошаговой инструкцией «куда нажать». Подробные практические задания пишутся только после согласования этой спецификации.

Нормативная база — [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md).

---

# 1. Правило спецификации

Каждое решение должно отвечать на реальное требование.

```text
требование
→ модель
→ штатный механизм Frappe
→ конкретная конфигурация
→ контрольные данные
→ наблюдаемая проверка
```

Запрещено добавлять поле, DocType, Script, Workflow, Report или другой механизм только потому, что он существует во Framework.

---

# 2. Имена учебных объектов

Чтобы документация, исходники и интерфейс не расходились, в CORE используются следующие технические имена:

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

Название предметной области учебное и нейтральное. Оно не связано с VEQTA.

---

# 3. Naming — обязательное решение

У каждого самостоятельного Document существует системный `name`. В CORE он не строится из изменяемого отображаемого названия.

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

`Rental Item` — Child DocType, отдельная naming-стратегия для него не проектируется.

## Почему так

CORE должен показать разницу между:

```text
name                 = стабильная идентичность Document
equipment_name       = отображаемое предметное название
customer_name        = имя клиента
display fields       = человекочитаемое представление
```

Изменение `equipment_name` или `customer_name` не должно менять identity Document и ломать существующие Link.

## Что специально не используем

- серийный номер Equipment как `name`;
- имя Customer как `name`;
- собственный Python `autoname()`;
- UUID только ради демонстрации UUID;
- отдельный Naming Series DocType/процесс, если фиксированного Expression достаточно.

---

# 4. CORE-модель данных

```text
Equipment
Customer

Rental
├── customer        → Link → Customer
├── start_date      → Date
├── end_date        → Date
├── status          → Select
└── items           → Table → Rental Item

Rental Item
└── equipment       → Link → Equipment
```

Никаких дополнительных самостоятельных DocTypes в CORE нет.

---

# 5. Equipment — точная спецификация

## DocType

```text
Name      : Equipment
Module    : Rental Training
Standard  : yes
Child     : no
Single    : no
Submittable: no
```

## Fields

| Label | Fieldname | Type | Required | Unique | Назначение |
|---|---|---|---:|---:|---|
| Equipment Name | `equipment_name` | Data | yes | no | человекочитаемое название |
| Equipment Type | `equipment_type` | Select | yes | no | небольшой стабильный классификатор |
| Serial Number | `serial_number` | Data | no | no | предметный атрибут, не identity |
| Active | `active` | Check | yes | no | можно ли использовать запись в текущей работе |

## Select `equipment_type`

```text
Tool
Camera
Computer
```

Это намеренно маленький стабильный список. В CORE отдельного `Equipment Type` нет.

## Default

```text
active = 1
```

## Naming

```text
EQ-.#####
```

## Контрольные записи

```text
EQ-00001
Equipment Name : Bosch GBH 2-26
Equipment Type : Tool
Serial Number  : BH-10001
Active         : yes

EQ-00002
Equipment Name : Canon EOS R50
Equipment Type : Camera
Serial Number  : CR50-20001
Active         : yes

EQ-00003
Equipment Name : Lenovo ThinkPad E14
Equipment Type : Computer
Serial Number  : LTP-30001
Active         : yes
```

## Проверка

1. Создаются все три записи.
2. Они находятся через List.
3. List фильтруется по `equipment_type`.
4. `Equipment Name` у первой записи меняется.
5. `name = EQ-00001` остаётся прежним.

## ГОТОВО

Если ученик может объяснить:

```text
почему Equipment = DocType
почему equipment_type = Select
почему serial_number ≠ name
почему изменение названия не должно менять identity
```

## НЕ ГОТОВО

Если создан отдельный `Equipment Type` без новых требований, название/серийный номер необоснованно сделаны identity либо Equipment существует только как текстовая строка внутри Rental.

---

# 6. Customer — точная спецификация

## DocType

```text
Name      : Customer
Module    : Rental Training
Standard  : yes
Child     : no
Single    : no
Submittable: no
```

## Fields

| Label | Fieldname | Type | Required | Unique | Назначение |
|---|---|---|---:|---:|---|
| Customer Name | `customer_name` | Data | yes | no | человекочитаемое имя |
| Phone | `phone` | Data | no | no | контакт |
| Email | `email` | Data | no | no | контакт |
| Active | `active` | Check | yes | no | актуальность записи |

## Default

```text
active = 1
```

## Naming

```text
CUST-.#####
```

## Контрольные записи

```text
CUST-00001
Customer Name : Anna Petrova
Phone         : +31 6 10000001
Email         : anna@example.test
Active        : yes

CUST-00002
Customer Name : Mark de Vries
Phone         : +31 6 10000002
Email         : mark@example.test
Active        : yes
```

`example.test` используется как заведомо учебный домен.

## Проверка

1. Создаются два Customer.
2. Один Customer позже используется в нескольких Rentals.
3. Имя `Anna Petrova` меняется, но `CUST-00001` и ссылки на него сохраняются.

## ГОТОВО

Ученик объясняет, почему Customer — самостоятельный Document и почему копирование имени клиента в Rental не заменяет `Link`.

---

# 7. Rental Item — точная спецификация

## DocType

```text
Name      : Rental Item
Module    : Rental Training
Standard  : yes
Child     : yes
Single    : no
Submittable: no
```

## Fields

| Label | Fieldname | Type | Required | Options |
|---|---|---|---:|---|
| Equipment | `equipment` | Link | yes | `Equipment` |

На старте в строке **нет**:

```text
quantity
price
status
responsible
return_date
comment
```

Причина простая: одна строка означает одну конкретную единицу Equipment. Эти поля появятся только после новых требований.

## ГОТОВО

Если Rental Item существует только как часть Rental и ученик понимает смысл `parent`, `parenttype`, `parentfield`, а не пытается превратить строку в отдельный бизнес-объект.

---

# 8. Rental — точная спецификация

## DocType

```text
Name      : Rental
Module    : Rental Training
Standard  : yes
Child     : no
Single    : no
Submittable: no
Track Changes: не требуется для CORE
```

## Fields

| Label | Fieldname | Type | Required | Options |
|---|---|---|---:|---|
| Customer | `customer` | Link | yes | `Customer` |
| Start Date | `start_date` | Date | yes | — |
| End Date | `end_date` | Date | yes | — |
| Status | `status` | Select | yes | `Planned\nActive\nReturned` |
| Equipment | `items` | Table | yes | `Rental Item` |

## Default

```text
status = Planned
```

## Naming

```text
RENT-.#####
```

## Почему Rental не Submittable

CORE пока описывает рабочий объект со статусом. Требования необратимо фиксировать операцию как транзакционный факт ещё нет.

Поэтому:

```text
status = Returned
```

не превращается автоматически в:

```text
docstatus = Submitted
```

---

# 9. Контрольный набор Rentals

Для всех следующих этапов используется один и тот же минимальный набор.

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

## Rental B — валидный плановый

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

Ожидание: отвергается сервером.

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

Ожидание: отвергается сервером.

## Rental E — конфликт по периоду

Создаётся после Rental A:

```text
Customer   : CUST-00002
Start Date : 2026-09-11
End Date   : 2026-09-13
Status     : Active
Items:
- EQ-00001
```

Ожидание: отвергается как пересекающийся активный прокат того же Equipment.

## Rental F — тот же Equipment без конфликта

```text
Customer   : CUST-00002
Start Date : 2026-09-13
End Date   : 2026-09-14
Status     : Active
Items:
- EQ-00001
```

Ожидание: сохраняется при принятой семантике закрытых интервалов, где Rental A заканчивается 12 сентября, а новый начинается 13 сентября.

---

# 10. Серверные инварианты Rental

CORE содержит ровно три собственных бизнес-правила.

## V01. Корректный период

```text
end_date >= start_date
```

Владелец: `Rental` Controller.

Естественная точка: `validate()`.

Ошибка должна быть понятна пользователю и блокировать сохранение.

## V02. Нет одного Equipment дважды внутри Rental

Для одного `Rental.items` значения `equipment` должны быть уникальны.

Владелец: `Rental` Controller.

Не создаётся отдельный Rule Engine.

## V03. Нет пересекающихся активных Rentals

Проверка применяется только к Rentals, чьё предметное состояние участвует в фактической занятости Equipment.

Для CORE занятость создаёт:

```text
status = Active
```

`Planned` и `Returned` в этой базовой модели не блокируют Equipment.

Два периода конфликтуют, если:

```text
existing.start_date <= current.end_date
AND
existing.end_date >= current.start_date
```

и существует совпадающее Equipment.

Текущий Document при редактировании должен исключаться из поиска конфликта по `name`.

## Граница V03

Это учебная последовательная проверка. Она **не является доказанной защитой от race condition** при двух параллельных транзакциях.

Никакие ручные lock/commit в CORE ради этого не добавляются.

---

# 11. Базовая permission model

В CORE используются только:

```text
User
Role
DocType Permissions
```

Без `User Permission`, `Share`, `Permission Level`, custom permission hooks и собственного ACL.

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

`Submit`, `Cancel`, `Amend` в CORE не используются, потому что `Rental` не Submittable.

## Учебные пользователи

Создаются два обычных пользователя:

```text
operator@example.test → Rental Operator
manager@example.test  → Rental Manager
```

Пароли в репозиторий не записываются.

## Проверка

Под Operator:

- Equipment можно читать, но нельзя создавать/изменять/удалять;
- Customer можно создавать и изменять, но нельзя удалять;
- Rental можно создавать и изменять, но нельзя удалять.

Под Manager разрешены все четыре CRUD-действия CORE.

## НЕ ГОТОВО

Если права проверены только под Administrator либо ограничения существуют только в UI.

---

# 12. CORE-тесты

Тестируются только наши контракты.

Минимальный обязательный набор:

```text
test_valid_rental_can_be_saved
test_end_date_before_start_date_is_rejected
test_duplicate_equipment_in_same_rental_is_rejected
test_overlapping_active_rental_is_rejected
test_non_overlapping_active_rental_is_allowed
test_operator_cannot_create_equipment
test_operator_can_create_rental
```

Допустимо объединять/переименовывать тесты, если смысл набора сохраняется.

## Не тестировать

```text
Frappe умеет сохранять любой Document
Link field вообще работает
Form вообще существует
```

## Запуск

Финальная проверка должна уметь запускать тесты через штатный Bench test runner для учебного App/Site.

---

# 13. Этапы CORE и критерии готовности

## S00 — среда

### ГОТОВО

- совместимый Frappe v16 работает;
- учебный Site открывается;
- developer mode применим;
- Git доступен.

### НЕ ГОТОВО

Если дальнейшая работа зависит от ручной правки Frappe core или неизвестной локальной магии.

---

## S01 — App

### ГОТОВО

- `rental_training` существует как отдельный App;
- App установлен на учебный Site;
- Module существует внутри App;
- исходники находятся под Git.

---

## S02 — Equipment

### ГОТОВО

- схема соответствует разделу 5;
- naming стабилен;
- контрольные записи создаются;
- тип остаётся Select.

---

## S03 — Customer

### ГОТОВО

- схема соответствует разделу 6;
- naming стабилен;
- Link позже использует реальный Customer Document.

---

## S04 — Rental composition

### ГОТОВО

- Rental соответствует разделу 8;
- Rental Item — Child DocType;
- связи работают через Link;
- один Rental содержит минимум два Equipment.

---

## S05A — status

### ГОТОВО

- `Planned / Active / Returned` являются обычным предметным status;
- нет Workflow;
- Rental не Submittable.

---

## S05B — Desk

### ГОТОВО

Полный сценарий Equipment → Customer → Rental выполняется стандартными Form/List без собственного frontend.

---

## S05C — local invariants

### ГОТОВО

Rental C и Rental D отвергаются сервером, а корректные Documents сохраняются.

---

## S05D — permissions

### ГОТОВО

Operator и Manager реально получают разные серверные права согласно разделу 11.

---

## S06 — cross-document invariant

### ГОТОВО

Rental E блокируется, Rental F сохраняется, граница concurrency явно понимается и не маскируется.

---

## S07 — tests

### ГОТОВО

- обязательный тестовый набор проходит;
- намеренная поломка собственного правила приводит к падению соответствующего теста.

---

## S08 — delivery audit

### ГОТОВО

Для каждого обязательного элемента можно ответить, откуда он восстановится:

```text
DocType schema → App JSON/source
Controller     → App source
обязательные переносимые настройки → штатный механизм App
Site-local данные → не выдаются за часть исходников
```

Нет обязательного ручного SQL.

---

## S09 — clean install

### ГОТОВО

На новом совместимом Site:

1. App устанавливается;
2. migrate проходит;
3. обязательная схема появляется;
4. тесты проходят;
5. создаются контрольные Equipment/Customer;
6. валидный Rental сохраняется;
7. невалидные сценарии блокируются;
8. permissions соответствуют спецификации.

---

# 14. Что специально остаётся вне CORE

Даже после этой спецификации CORE **не получает** автоматически:

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

Они остаются NEXT/GATE/EXT и требуют отдельного принятого требования.

---

# 15. Запрещённые упрощения в будущих инструкциях

Пошаговый практикум не должен:

- предлагать ручной SQL вместо обычного Document/migrate-пути;
- создавать Custom DocType вместо Standard DocType учебного App;
- делать бизнес-инвариант только Client Script;
- использовать Administrator вместо реальной проверки permissions;
- добавлять `ignore_permissions=True` для обхода неправильно настроенных прав;
- создавать отдельные DocTypes для статуса, комментариев, истории или вложений без требования;
- превращать `Returned` в Submitted без появления транзакционной семантики;
- создавать собственный CRUD API в CORE;
- менять Frappe core;
- требовать скрытых ручных действий, без которых clean install не работает.

---

# 16. Контроль перед написанием пошаговых заданий

Спецификация может быть превращена в подробные инструкции только если на все вопросы ответ `да`:

```text
1. Поля минимальны и имеют предметный смысл?
2. Naming стабилен и не зависит от изменяемого display value?
3. Child DocType действительно является составом Rental?
4. status не перепутан с Workflow/docstatus?
5. Три собственных инварианта имеют серверного владельца?
6. Permission model остаётся штатной и минимальной?
7. Контрольные данные однозначно проверяют happy path и ошибки?
8. Тесты проверяют наши контракты, а не Frappe ради coverage?
9. CORE не содержит NEXT/GATE/EXT ради знакомства?
10. Финальный критерий — clean install, а не «работает на моём dev-site»?
```

Если хотя бы один ответ отрицательный, сначала исправляется спецификация.