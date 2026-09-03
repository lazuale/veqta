# S03. Создать Customer как второй самостоятельный Document

S02 дал нам первый предметный объект — `Equipment`.

Теперь нужен второй объект, который существует независимо от конкретного проката: **Customer**.

Цель S03 — не повторить создание DocType ещё раз, а закрепить четыре вещи:

```text
самостоятельный бизнес-объект → Standard DocType
стабильный идентификатор      → name
человекочитаемое имя          → Title Field
типизированный текст          → Data + Options
```

На этом этапе мы ещё не связываем Customer с Rental. `Link` появится на S04, когда возникнет сама операция проката.

Связанные документы:

- [`S02_EQUIPMENT_DOCTYPE.md`](S02_EQUIPMENT_DOCTYPE.md) — обязательное предыдущее практическое состояние;
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md) — модель Customer;
- [`../ROADMAP.md`](../ROADMAP.md) — место этапа в практикуме.

---

# 1. Входная проверка

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Apps на Site:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте, что `Equipment` уже существует как Standard DocType, принадлежащий App:

```bash
test -f \
  apps/rental_training/rental_training/rental_training/doctype/equipment/equipment.json \
  && echo 'Equipment metadata: OK'
```

Если файл не найден, S02 не закончен.

---

# 2. Почему Customer — отдельный DocType

Требование:

> Один и тот же клиент может брать оборудование много раз. Его данные должны храниться один раз и переиспользоваться в разных Rentals.

Задайте тот же вопрос, что на S02:

```text
имеет ли Customer собственный идентификатор?
→ да

существует ли Customer без конкретного Rental?
→ да

будет ли на него ссылаться много Rentals?
→ да
```

Следовательно:

```text
Customer = самостоятельный Document
         = обычный Standard DocType
```

## Неправильная модель

Не делаем так:

```text
Rental
├── customer_name
├── customer_phone
└── customer_email
```

Если один человек сделает пять Rentals, его данные будут скопированы пять раз.

Появятся очевидные проблемы:

- исправили телефон только в одном Rental;
- одинаковый клиент превращается в несколько несвязанных текстовых наборов;
- невозможно однозначно сослаться на клиента;
- история операций клиента становится результатом поиска по строке, а не связью Documents.

На S04 именно эта самостоятельность позволит использовать штатный `Link → Customer`.

---

# 3. Что нового относительно Equipment

Структурно Customer похож на Equipment:

```text
оба самостоятельные Documents
оба принадлежат rental_training
оба получают стабильный name
оба имеют человекочитаемый Title Field
```

Но S03 добавляет новую штатную возможность DocField:

```text
Data
├── Options = Phone
└── Options = Email
```

Frappe документирует `Data` как обычное текстовое поле и позволяет включить штатную валидацию значений через `Options = Name | Email | Phone | URL`.

Поэтому для телефона и email **не нужны**:

```text
собственное регулярное выражение
Client Script
Server Script
отдельный Python validator
```

Пока стандартная семантика Frappe подходит требованию, собственного механизма не создаём.

Первичный источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes

---

# 4. Создать DocType Customer

Запустите сервер разработки, если он ещё не работает:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте Desk:

```text
http://rental.localhost:8000/app
```

Через поиск Desk откройте:

```text
DocType
```

Нажмите **New**.

Заполните:

```text
Name   : Customer
Module : Rental Training
```

Проверьте основные признаки:

```text
Custom?        : OFF
Is Child Table : OFF
Is Single      : OFF
Is Submittable : OFF
```

Почему:

- `Custom? = OFF` — модель принадлежит App и должна попасть в исходники;
- Customer — самостоятельный объект, поэтому не Child Table;
- клиентов много, поэтому не Single;
- у Customer нет транзакционного жизненного цикла submit/cancel.

---

# 5. Добавить только три поля

Создайте поля в таком порядке.

## 5.1. Customer Name

```text
Label     : Customer Name
Fieldname : customer_name
Type      : Data
Mandatory : yes
```

Это отображаемое имя клиента, но не системный `name` Document.

## 5.2. Phone

```text
Label     : Phone
Fieldname : phone
Type      : Data
Options   : Phone
Mandatory : no
```

## 5.3. Email

```text
Label     : Email
Fieldname : email
Type      : Data
Options   : Email
Mandatory : no
```

Не делайте Phone или Email системным идентификатором.

Причины простые:

- у человека может не быть заполненного телефона или email;
- контакт может измениться;
- два человека могут использовать общий контакт;
- требования практикума не говорят, что эти значения глобально уникальны.

---

# 6. Настроить naming

В секции Naming выберите штатный Expression naming:

```text
CUST-.#####
```

Ожидаемые новые `name`:

```text
CUST-00001
CUST-00002
...
```

Идея та же, что у Equipment:

```text
name          = стабильный идентификатор
customer_name = изменяемое отображаемое значение
```

Мы намеренно не используем:

```text
field:customer_name
field:email
Python autoname()
UUID ради UUID
```

Для практикума достаточно одного фиксированного штатного Expression.

Первичные источники:

- https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- https://docs.frappe.io/framework/user/en/tutorial/doctype-features

---

# 7. Настроить отображаемый title

В View Settings задайте:

```text
Title Field               : customer_name
Show Title in Link Fields : yes
```

Это станет особенно заметно на S04.

Тогда будущий `Link → Customer` сможет показывать человеку:

```text
Anna Petrova
```

а внутри Document сохранять стабильную ссылку:

```text
CUST-00001
```

То есть:

```text
что видит пользователь ≠ системный идентификатор связанного Document
```

Первичный источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/form_%26_view_settings

---

# 8. Чего не добавлять

На S03 не нужны:

```text
Address DocType
Contact DocType
Customer Type
status
active
company
birth_date
notes
attachments
Workspace
Role
Workflow
Client Script
Server Script
Python controller logic
```

Это не запрет на такие решения вообще.

Для них просто нет требований текущего практикума.

---

# 9. Сохранить Customer и проверить исходники

Нажмите **Save**.

Вернитесь в терминал:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Должен появиться каталог Customer внутри Module:

```bash
find apps/rental_training/rental_training/rental_training/doctype/customer \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидайте метаданные Standard DocType и стандартные места для Controller и тестов, например:

```text
__init__.py
customer.json
customer.py
customer.js
test_customer.py
```

Точный набор служебных файлов может меняться, поэтому важен контракт:

```text
метаданные Customer находятся в исходниках rental_training
```

Откройте JSON:

```bash
sed -n '1,260p' \
  apps/rental_training/rental_training/rental_training/doctype/customer/customer.json
```

Найдите:

```text
"module": "Rental Training"
customer_name
phone
email
title_field
show_title_field_in_link
autoname / naming metadata
```

Для `phone` и `email` найдите также `options`.

---

# 10. Проверить созданные файлы через Git

Новые файлы сначала являются `untracked`, поэтому одного `git diff` недостаточно.

Проверьте:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Добавьте исходники Equipment и Customer в индекс:

```bash
git add \
  rental_training/rental_training/doctype/equipment \
  rental_training/rental_training/doctype/customer
```

Теперь посмотрите подготовленный diff:

```bash
git diff --cached -- \
  rental_training/rental_training/doctype/equipment \
  rental_training/rental_training/doctype/customer
```

Ученик должен увидеть связь:

```text
настроил Standard DocTypes в Desk
↓
Frappe сформировал метаданные в App
↓
Git видит изменение исходного состояния App
```

Не нужно вручную переписывать созданный JSON после сохранения только ради того, чтобы «сделать всё кодом».

---

# 11. Зафиксировать первую предметную версию в Git

До перехода к операции Rental зафиксируйте обе независимые сущности в истории App:

```bash
git commit -m "feat: add equipment and customer doctypes"
```

Проверьте:

```bash
git status --short
git log --oneline -3
```

После commit `git status --short` должен быть пустым, если вы не делали других изменений.

Это не урок Git ради Git. Здесь commit подтверждает архитектурную границу:

```text
метаданные Equipment + Customer
принадлежат App
и восстанавливаются из его истории Git
```

Если Git просит настроить `user.name`/`user.email`, настройте свои локальные данные Git и повторите commit. Не используйте вымышленные авторские данные из инструкции.

---

# 12. Создать контрольных Customers

Через стандартную Form создайте две записи.

## Customer 1

```text
Customer Name : Anna Petrova
Phone         : +31 6 10000001
Email         : anna@example.test
```

На чистом прохождении ожидается:

```text
name = CUST-00001
```

## Customer 2

```text
Customer Name : Mark de Vries
Phone         : +31 6 10000002
Email         : mark@example.test
```

Ожидается:

```text
name = CUST-00002
```

`example.test` — зарезервированный учебный домен. Реальные адреса для практикума не нужны.

Если счётчик уже использовался во время экспериментов, фактический номер может быть другим. Проверяется формат `CUST-#####`, а не искусственный сброс счётчика.

---

# 13. Проверить штатную валидацию Email

Попробуйте создать временную запись:

```text
Customer Name : Invalid Email Test
Email         : not-an-email
```

Сохранение должно показать, что значение не соответствует Email-формату.

После проверки временную запись не оставляйте в контрольном наборе.

Смысл проверки не в тексте конкретной ошибки, а в архитектурном наблюдении:

```text
требование: email должен иметь формат email
↓
владелец ответственности уже есть
↓
Data + Options = Email
↓
собственное регулярное выражение не нужно
```

Не пытайтесь в этом этапе исследовать все допустимые международные форматы Phone. Нам достаточно понять сам механизм типизации Data.

---

# 14. Проверить List и title

Откройте Customer List.

Убедитесь, что обе контрольные записи доступны через стандартные List/Form без собственного UI.

Откройте `Anna Petrova` и запомните две разные величины:

```text
Document name : CUST-00001
Title         : Anna Petrova
```

Измените:

```text
Customer Name : Anna Petrova-Test
```

Сохраните.

Проверьте:

```text
name остался CUST-00001
```

Верните имя обратно:

```text
Anna Petrova
```

Так ученик второй раз подтверждает правило:

```text
изменяемое отображаемое значение
не должно случайно становиться системным идентификатором Document
```

---

# 15. Почему Customer не копируется в Rental текстом

До S04 у нас теперь существуют две независимые сущности:

```text
Equipment
Customer
```

Они пока вообще не связаны.

Это правильно.

Будущий Rental будет третьим самостоятельным Document и свяжет их штатными механизмами:

```text
Rental
├── customer → Link → Customer
└── items    → Table MultiSelect → Rental Item
                                 └── equipment → Link → Equipment
```

Именно реальное требование «Rental использует существующего Customer» создаёт причину для `Link`.

Мы не создавали Link на S02/S03 заранее ради знакомства с полем.

---

# 16. Типовые неправильные решения

## Ошибка 1. `customer_name` используется как `name`

Почему плохо в нашем требовании:

```text
имя может измениться
имена людей не обязаны быть уникальными
системный идентификатор начинает зависеть от отображаемого значения
```

Штатный Expression лучше соответствует выбранному контракту.

## Ошибка 2. Email используется как `name`

Email — контактное свойство, а не гарантированно неизменный идентификатор Customer.

## Ошибка 3. Email проверяется своим регулярным выражением

Если нужна обычная email-валидация, Frappe уже предоставляет `Data + Options = Email`.

Собственная проверка без дополнительного требования дублирует ответственность Framework.

## Ошибка 4. Customer вообще не создаётся как Document

Копирование имени, телефона и email в каждый Rental создаёт дубли там, где предметная модель требует живой самостоятельной сущности.

## Ошибка 5. Создаются Address/Contact/Customer Type «потому что так бывает в CRM»

Практикум не строит CRM. Пока у этих сущностей нет собственной ответственности, они являются преждевременной моделью.

---

# 17. Проверка перед S04

Перед переходом дальше одновременно должно быть верно следующее.

## Модель

```text
Customer = Standard DocType
Module   = Rental Training
Custom?  = OFF
Child    = OFF
Single   = OFF
Submit   = OFF
```

## Поля

```text
customer_name : Data, mandatory
phone         : Data, Options=Phone
email         : Data, Options=Email
```

Лишних полей нет.

## Naming / title

```text
Expression                = CUST-.#####
Title Field               = customer_name
Show Title in Link Fields = yes
```

## Контрольные данные

Существуют:

```text
Anna Petrova
Mark de Vries
```

## Поведение

Проверено:

- Customer List/Form работают без собственного frontend;
- неверный email ловится штатным механизмом Data/Email;
- изменение `customer_name` не меняет системный `name`;
- метаданные Customer находятся в исходниках App;
- метаданные Equipment + Customer зафиксированы commit в Git.

## Ученик может объяснить

```text
почему Customer = самостоятельный DocType
почему телефон и email = свойства Customer
почему Email validation не требует своей проверки
почему name ≠ customer_name
почему Customer пока не связан с Equipment
```

---

# 18. Когда не переходить к S04

Сначала исправьте проблему, если:

- Customer создан как `Custom` DocType, локальный для Site;
- `customer_name` или email без требования используется как системный `name`;
- email validation реализована собственным Script вместо штатного Options;
- контактные данные копируются в ещё не существующий Rental вместо самостоятельного Customer;
- созданы дополнительные CRM-сущности без требования;
- метаданные не находятся в Git и исходниках App;
- репозиторий App после этапа содержит незакоммиченные изменения Equipment/Customer.

---

# 19. Что теперь существует

После S03 предметная модель впервые содержит **две независимые сущности**:

```text
Equipment
Customer
```

Они имеют собственный системный `name`, Form/List и метаданные в App, но пока не связаны друг с другом.

Следующее требование уже нельзя решить ещё одним изолированным справочником:

> Нужно зарегистрировать сам факт проката: кто взял, на какой период и какое оборудование.

Именно это приведёт на **S04** к центральной композиции практикума:

```text
Rental
├── Link → Customer
└── Table MultiSelect → Rental Item
                          └── Link → Equipment
```

На S04 впервые вместе появятся `Link`, `Child DocType` и `Table MultiSelect` — не как набор функций, а как прямое следствие модели операции проката.