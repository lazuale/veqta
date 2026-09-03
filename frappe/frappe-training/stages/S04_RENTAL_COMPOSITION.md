# S04. Собрать Rental из независимых Documents и принадлежащего ему набора Equipment

После S02 и S03 у нас уже есть две самостоятельные сущности:

```text
Equipment
Customer
```

Они существуют независимо друг от друга и пока никак не описывают сам факт проката.

Теперь появляется новое требование:

> Нужно зафиксировать, **кто**, **на какой период** и **какое оборудование** берёт в прокат.

Это требование создаёт третий самостоятельный Document — `Rental` — и две разные связи:

```text
Rental.customer
    → один существующий Customer
    → Link

Rental.items
    → несколько существующих Equipment
    → Table MultiSelect
    → Rental Item [Child DocType]
    → Link → Equipment
```

На S04 мы впервые собираем несколько Documents в одну предметную модель.

Связанные документы:

- [`S02_EQUIPMENT_DOCTYPE.md`](S02_EQUIPMENT_DOCTYPE.md);
- [`S03_CUSTOMER_DOCTYPE.md`](S03_CUSTOMER_DOCTYPE.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md);
- [`../REQUIREMENTS_MATRIX.md`](../REQUIREMENTS_MATRIX.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md).

---

# 1. Входная проверка

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Apps:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте, что metadata Equipment и Customer уже принадлежат App:

```bash
test -f \
  apps/rental_training/rental_training/rental_training/doctype/equipment/equipment.json \
  && echo 'Equipment: OK'

test -f \
  apps/rental_training/rental_training/rental_training/doctype/customer/customer.json \
  && echo 'Customer: OK'
```

Ожидается:

```text
Equipment: OK
Customer: OK
```

Проверьте Git App:

```bash
git -C apps/rental_training status --short
```

После принятого S03 рабочее дерево должно быть чистым.

Если там остались незакоммиченные изменения S02/S03, сначала закончите предыдущую контрольную точку.

---

# 2. Разобрать требование до создания полей

Нам нужны четыре факта:

```text
Rental имеет собственную identity
Rental ссылается на одного Customer
Rental хранит период
Rental выбирает несколько Equipment
```

Разложим их по ответственности.

## 2.1. Почему Rental — обычный DocType

Rental:

- существует как отдельная операция;
- должен иметь собственный `name`;
- его нужно находить и открывать отдельно;
- позже у него появятся собственные status, permissions и бизнес-правила.

Следовательно:

```text
Rental = самостоятельный Standard DocType
```

Это не Child DocType Customer и не Child DocType Equipment.

## 2.2. Почему Customer — Link

Customer уже существует как самостоятельный Document.

В Rental не нужно копировать:

```text
customer_name
phone
email
```

Нужно сохранить настоящую связь:

```text
customer → Link → Customer
```

## 2.3. Почему Equipment не копируется текстом

То же правило:

```text
"Bosch GBH 2-26"
```

как обычная строка не заменяет связь с:

```text
EQ-00001
```

Rental должен ссылаться на существующий Equipment Document.

Но Equipment несколько, поэтому одного обычного Link недостаточно.

---

# 3. Выбрать механизм для нескольких Equipment

На этом месте легко автоматически выбрать обычный `Table` только потому, что «несколько строк = таблица».

Но сначала смотрим на семантику строки.

Текущее требование к одной позиции Rental:

```text
Rental Item
└── equipment → Link → Equipment
```

И всё.

У строки **нет**:

```text
quantity
price
daily_rate
condition_on_issue
status
returned_at
comment
```

То есть бизнес-смысл сейчас:

> выбрать несколько существующих Equipment.

Frappe предоставляет для этого `Table MultiSelect` — fieldtype, объединяющий Link-выбор с child-table хранением.

Поэтому CORE использует:

```text
Rental.items
    → Table MultiSelect
    → Rental Item [Child DocType]
    → equipment [Link → Equipment]
```

Первичные источники:

- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/docfield/docfield.py

---

# 4. Почему Child DocType всё равно нужен

Название `Table MultiSelect` может создать ложное впечатление, что Frappe хранит просто массив строк внутри одного поля.

Нет.

Штатный механизм использует Child DocType.

Для нашего случая:

```text
Rental Item
└── equipment → Link → Equipment
```

Child rows получают служебную связь с родителем:

```text
parent
parenttype
parentfield
idx
```

Официальная документация Child DocType определяет их так:

```text
parent     = name родительского Document
parenttype = DocType родителя
parentfield= поле родителя, которому принадлежит строка
idx        = порядок строки
```

То есть `Rental Item` — не самостоятельная карточка проката оборудования.

Это часть конкретного Rental.

---

# 5. Сначала создать Rental Item

`Rental` ещё не создан.

Сначала создаём тип дочерней строки, потому что позже поле `Table MultiSelect` должно ссылаться на уже определённый Child DocType.

Запустите dev server, если он ещё не работает:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте Desk:

```text
http://rental.localhost:8000/app
```

Через поиск откройте:

```text
DocType
```

Создайте новый DocType:

```text
Name   : Rental Item
Module : Rental Training
```

Проверьте:

```text
Custom?        : OFF
Is Child Table : ON
```

Для Child DocType отдельный пользовательский lifecycle не проектируется.

---

# 6. Добавить единственное поле Rental Item

Добавьте:

```text
Label        : Equipment
Fieldname    : equipment
Type         : Link
Options      : Equipment
Mandatory    : yes
In List View : yes
```

Последняя настройка здесь не косметическая.

В Frappe v16 `Table MultiSelect` определяет целевой DocType по `Link`-полю Child DocType, у которого включён `in_list_view`.

В актуальном исходном коде `DocField.get_link_doctype()` для `Table MultiSelect` ищет именно:

```text
fieldtype    = Link
parent       = Rental Item
in_list_view = 1
```

Поэтому:

```text
In List View = yes
```

является частью контракта этой конфигурации.

Сохраните `Rental Item`.

---

# 7. Проверить generated source Rental Item

В терминале:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Проверьте каталог:

```bash
find \
  apps/rental_training/rental_training/rental_training/doctype/rental_item \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Откройте metadata:

```bash
sed -n '1,240p' \
  apps/rental_training/rental_training/rental_training/doctype/rental_item/rental_item.json
```

Найдите смысловые признаки:

```text
"istable": 1
"fieldname": "equipment"
"fieldtype": "Link"
"options": "Equipment"
"in_list_view": 1
```

Точный порядок JSON не важен.

Важно увидеть:

```text
Child DocType создан через Desk
↓
его metadata принадлежит rental_training
```

---

# 8. Создать Rental

Вернитесь в Desk → `DocType` → **New**.

Создайте:

```text
Name   : Rental
Module : Rental Training
```

Проверьте:

```text
Custom?        : OFF
Is Child Table : OFF
Is Single      : OFF
Is Submittable : OFF
```

Почему `Is Submittable = OFF`:

На текущем этапе Rental — обычный рабочий Document.

У нас ещё нет требования:

> после подтверждения операция становится фиксированным транзакционным фактом, который можно только Cancel/Amend.

Значит `docstatus` пока не нужен как бизнес-механизм.

---

# 9. Добавить поля Rental

На S04 создаём только структуру операции.

## 9.1. Customer

```text
Label        : Customer
Fieldname    : customer
Type         : Link
Options      : Customer
Mandatory    : yes
In List View : yes
```

## 9.2. Start Date

```text
Label        : Start Date
Fieldname    : start_date
Type         : Date
Mandatory    : yes
In List View : yes
```

## 9.3. End Date

```text
Label        : End Date
Fieldname    : end_date
Type         : Date
Mandatory    : yes
In List View : yes
```

## 9.4. Equipment

```text
Label     : Equipment
Fieldname : items
Type      : Table MultiSelect
Options   : Rental Item
Mandatory : yes
```

### Важно

На S04 **не добавляйте** поле `status`.

Оно появится на S05A, когда отдельное требование заставит различать:

```text
Planned
Active
Returned
```

Так мы не подсовываем механизм раньше требования.

---

# 10. Настроить naming Rental

Используйте штатный Expression:

```text
RENT-.#####
```

Ожидаемый формат:

```text
RENT-00001
RENT-00002
...
```

Rental — самостоятельный Document, поэтому у него есть собственная стабильная identity.

Мы не строим `name` из:

```text
customer
start_date
```

Потому что эти значения являются бизнес-данными и могут изменяться.

Сохраните DocType `Rental`.

---

# 11. Проверить generated source Rental

В терминале:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Посмотрите каталог Rental:

```bash
find \
  apps/rental_training/rental_training/rental_training/doctype/rental \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Откройте metadata:

```bash
sed -n '1,300p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.json
```

Найдите:

```text
customer
Link
Customer

start_date
Date

end_date
Date

items
Table MultiSelect
Rental Item

RENT-.#####
```

Пока в `rental.py` не нужно добавлять собственную бизнес-логику.

Серверные инварианты появятся на S05C и S06, когда сформулируются соответствующие требования.

---

# 12. Создать первый Rental

Теперь у нас достаточно модели для первой операции.

Создайте через стандартную Form:

```text
Customer   : Anna Petrova
Start Date : 2026-09-10
End Date   : 2026-09-12
Equipment  :
- Bosch GBH 2-26
- Canon EOS R50
```

За человекочитаемыми названиями должны стоять Documents:

```text
Customer:
CUST-00001

Equipment:
EQ-00001
EQ-00002
```

Сохраните.

На чистом прохождении ожидается:

```text
name = RENT-00001
```

Если sequence уже использовалась во время экспериментов, номер может отличаться. Проверяем формат `RENT-#####`, а не искусственный сброс sequence.

### Что произошло

Пользователь работал с одной Form:

```text
Rental
```

но модель уже связывает три типа Documents:

```text
Rental
├── Customer
└── Equipment × N
```

Без собственного frontend и без ручного SQL.

---

# 13. Увидеть Link identity и title

В Form пользователь должен видеть человекочитаемые значения, например:

```text
Anna Petrova
Bosch GBH 2-26
Canon EOS R50
```

Но ссылки должны хранить стабильные `name`:

```text
CUST-00001
EQ-00001
EQ-00002
```

Именно ради этого на S02/S03 мы заранее разделили:

```text
name
≠
Title Field
```

На S04 становится видно, зачем это было нужно.

---

# 14. Посмотреть Document через bench console

Теперь впервые полезно посмотреть на модель не только через Desk.

Откройте отдельный терминал:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

В Python console:

```python
rental = frappe.get_doc("Rental", "RENT-00001")
```

Если ваш фактический номер другой, подставьте его.

Проверьте Customer:

```python
rental.customer
```

Ожидается системный `name`, например:

```text
'CUST-00001'
```

Проверьте Equipment:

```python
[row.equipment for row in rental.items]
```

Ожидается примерно:

```text
['EQ-00001', 'EQ-00002']
```

То есть `Table MultiSelect` в UI не превратил данные в одну строку.

Frappe загрузил дочерние Documents.

---

# 15. Увидеть ownership Child Documents

В той же console:

```python
[
    (
        row.equipment,
        row.parent,
        row.parenttype,
        row.parentfield,
        row.idx,
    )
    for row in rental.items
]
```

Ожидаемый смысл результата:

```text
EQ-00001 | RENT-00001 | Rental | items | 1
EQ-00002 | RENT-00001 | Rental | items | 2
```

Точные кавычки/формат Python не важны.

Важно увидеть четыре свойства:

```text
parent      = конкретный Rental
parenttype  = Rental
parentfield = items
idx         = порядок строки
```

Теперь определение Child DocType становится физически наблюдаемым, а не теоретическим.

Выйдите из console:

```python
exit()
```

---

# 16. Почему Rental Item не самостоятельный DocType бизнеса

Да, технически `Rental Item` является DocType Frappe.

Но по бизнес-смыслу текущая строка не живёт сама по себе.

Нельзя осмысленно спросить:

```text
«открой Rental Item № X как отдельную операцию»
```

без его Rental.

У строки нет:

```text
собственного пользователя-владельца процесса
отдельного lifecycle
собственных permissions
собственной ссылки из других бизнес-документов
самостоятельного смысла вне Rental
```

Поэтому:

```text
Rental Item = Child DocType
```

а не отдельный master/transaction DocType.

---

# 17. Почему обычный Table пока не нужен

Обычный `Table` тоже использует Child DocType и является штатным механизмом Frappe.

Он просто выражает другой пользовательский и модельный акцент: **строка как состав с собственными полями**.

Например, если появится требование:

> При выдаче для каждой единицы нужно зафиксировать состояние и дневную цену именно на момент этой выдачи.

Тогда строка станет:

```text
Rental Item
├── equipment
├── daily_rate
└── condition_on_issue
```

И обычный:

```text
Table → Rental Item
```

станет естественнее `Table MultiSelect`.

Но такого требования сейчас нет.

Не добавляем поля «на будущее», чтобы оправдать выбранный механизм задним числом.

---

# 18. Почему не Table MultiSelect без Child DocType

Во Frappe это не отдельный массив ссылок без модели.

Актуальный `DocField.get_link_doctype()` для `Table MultiSelect`:

1. берёт `options` поля;
2. рассматривает его как Child DocType;
3. внутри Child DocType ищет `Link` с `in_list_view = 1`;
4. через `options` этого Link определяет конечный linked DocType.

Для нашей модели:

```text
Rental.items.options
= Rental Item

Rental Item.equipment
= Link → Equipment
```

Именно поэтому оба уровня нужны.

---

# 19. Типовые неправильные решения

## Ошибка 1. Customer копируется текстом

```text
Rental.customer_name : Data
Rental.phone          : Data
```

когда Rental должен ссылаться на существующего Customer.

### Почему плохо

Теряется identity и связь с Customer Document.

---

## Ошибка 2. Equipment хранится одной строкой

```text
items : Data
"EQ-00001, EQ-00002"
```

### Почему плохо

Framework больше не видит отдельные Links и child rows.

---

## Ошибка 3. Фиксированные поля

```text
equipment_1
equipment_2
equipment_3
```

### Почему плохо

Количество позиций искусственно зашито в схему.

---

## Ошибка 4. Dynamic Link

```text
equipment_doctype
equipment_name : Dynamic Link
```

при том что целевой тип всегда `Equipment`.

### Почему плохо

Добавлена универсальность, которой нет в требовании.

---

## Ошибка 5. Обычный Table только ради изучения Table

```text
Rental Item
└── equipment
```

и поле:

```text
Table
```

хотя строка не несёт других данных.

### Почему плохо

Более тяжёлый grid UI выбран не из семантики модели, а ради прохождения функции курса.

---

## Ошибка 6. Выдумать поля строки, чтобы оправдать Table

```text
quantity = 1
comment
status
```

хотя бизнес-требование их не предъявляло.

### Почему плохо

Архитектура начинает создавать требования сама для себя.

---

## Ошибка 7. Rental Item сделан самостоятельной карточкой

Отдельный CRUD/lifecycle/permissions для строки, которая существует только внутри Rental.

### Почему плохо

Ответственность строки искусственно раздута.

---

# 20. Зафиксировать generated source в Git

Проверьте изменения:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Добавьте два новых DocType:

```bash
git add \
  rental_training/rental_training/doctype/rental \
  rental_training/rental_training/doctype/rental_item
```

Посмотрите staged diff:

```bash
git diff --cached -- \
  rental_training/rental_training/doctype/rental \
  rental_training/rental_training/doctype/rental_item
```

Проверьте, что в diff нет случайных изменений Equipment/Customer или чужих настроек.

Зафиксируйте checkpoint:

```bash
git commit -m "feat: add rental composition"
```

Проверьте:

```bash
git status --short
```

Ожидается чистое рабочее дерево.

---

# 21. Что должно существовать после S04

Модель App:

```text
Rental Training
├── Equipment
├── Customer
├── Rental
└── Rental Item [Child]
```

Связи:

```text
Rental
├── customer → Link → Customer
├── start_date
├── end_date
└── items → Table MultiSelect → Rental Item
                              └── equipment → Link → Equipment
```

Пока **нет**:

```text
status
Workflow
docstatus / Is Submittable
server validation
permissions практикума
Workspace
Print Format
Report
```

Каждая следующая вещь должна появиться из следующего требования.

---

# 22. Контрольные вопросы

Ученик должен ответить своими словами.

## 1

Почему `Rental` — самостоятельный DocType?

Правильный смысл:

> операция имеет собственную identity и существует как отдельный Document.

## 2

Почему `customer` — `Link`, а не `Data`?

Правильный смысл:

> Rental ссылается на уже существующий Customer Document.

## 3

Почему Equipment тоже хранится через Link?

Правильный смысл:

> Rental должен ссылаться на конкретные Equipment Documents, а не копировать их названия.

## 4

Почему `Rental Item` — Child DocType?

Правильный смысл:

> строка является частью одного Rental и сейчас не имеет самостоятельного бизнес-lifecycle.

## 5

Почему выбран `Table MultiSelect`, а не обычный `Table`?

Правильный смысл:

> текущее требование — только выбрать несколько существующих Equipment; строка пока содержит одну Link-ссылку и не имеет собственных атрибутов отношения.

## 6

Когда обычный `Table` станет лучше?

Правильный смысл:

> когда у позиции появятся собственные данные отношения, которые нужно видеть и редактировать как строку: цена, состояние при выдаче, фактический возврат и т. п.

## 7

Что хранит `Table MultiSelect` физически с точки зрения Document model?

Правильный смысл:

> child rows с `parent`, `parenttype`, `parentfield`, `idx` и Link на Equipment.

---

# 23. ГОТОВО

S04 принят, если одновременно выполняется всё:

```text
[ ] Rental Item = Standard Child DocType rental_training
[ ] Rental Item.equipment = Link → Equipment
[ ] Rental Item.equipment имеет In List View = yes
[ ] Rental = Standard самостоятельный DocType
[ ] Rental.customer = Link → Customer
[ ] Rental.start_date = Date
[ ] Rental.end_date = Date
[ ] Rental.items = Table MultiSelect → Rental Item
[ ] Rental naming = RENT-.#####
[ ] status ещё не добавлен
[ ] один Rental сохранён минимум с двумя Equipment
[ ] через console видны реальные customer/equipment name
[ ] через console видны parent/parenttype/parentfield/idx child rows
[ ] generated metadata находится в App source
[ ] изменения зафиксированы Git commit
[ ] рабочее дерево App чистое
```

Ученик может без подсказки объяснить:

```text
Document vs Child Document
Link vs копирование текста
Table MultiSelect vs обычный Table
name vs title связанного Document
```

---

# 24. НЕ ГОТОВО

Этап не принят, если:

- Customer или Equipment копируются текстовыми полями вместо Link;
- Equipment записаны CSV/JSON-строкой;
- используются `equipment_1`, `equipment_2`, ...;
- Dynamic Link введён без переменного целевого DocType;
- обычный `Table` выбран только ради знакомства с ним;
- в Rental Item добавлены выдуманные поля ради оправдания Table;
- Rental Item сделан самостоятельной бизнес-карточкой без соответствующего требования;
- `status`, Workflow или Is Submittable добавлены раньше соответствующих этапов;
- обязательная metadata осталась только локальной настройкой Site;
- S04 заканчивается незакоммиченным App-owned состоянием.

---

# 25. Что дальше

После S04 у нас впервые существует полноценная операция проката.

Но система пока не различает состояние этой операции.

Возникает следующее реальное требование:

> Нужно отличать запланированный прокат от активного и возвращённого.

Только это требование приводит к S05A:

```text
Rental.status
→ Select
→ Planned / Active / Returned
```

И именно на S05A отдельно проверяется, почему:

```text
business status
≠ Workflow
≠ docstatus
```
