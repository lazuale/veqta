# S02. Создать Equipment как первый Standard DocType

На S00 мы получили чистую среду Frappe. На S01 создали и установили собственный App `rental_training`.

На S02 впервые появляется **предметная модель приложения**.

Мы не будем сначала изучать список типов полей, писать Python-класс или проектировать таблицу SQL. Есть конкретное требование:

> Система должна хранить оборудование, которое существует независимо от отдельной операции проката и может использоваться во многих Rentals.

Из этого требования нужно выбрать штатный механизм Frappe.

Связанные документы:

- [`S01_APP_AND_SITE.md`](S01_APP_AND_SITE.md) — обязательное входное состояние;
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md) — точная спецификация `Equipment`;
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md) — место этапа в CORE;
- [`../../frappe-architecture-standard/02_DATA_MODEL.md`](../../frappe-architecture-standard/02_DATA_MODEL.md) — правило выбора DocType и поля.

---

# 1. Что должно получиться

После S02 в приложении существует самостоятельный Standard DocType:

```text
Equipment
├── Equipment Name : Data
├── Equipment Type : Select
└── Serial Number  : Data
```

У записей стабильный системный `name`:

```text
EQ-00001
EQ-00002
EQ-00003
```

При этом пользователь в интерфейсе работает с понятным названием оборудования:

```text
Bosch GBH 2-26
Canon EOS R50
Lenovo ThinkPad E14
```

Главное, что нужно увидеть руками:

```text
DocType metadata
      ↓
Frappe создаёт модель Document
      ↓
таблицу хранения
      ↓
Form
      ↓
List
      ↓
исходники Standard DocType внутри App
```

Мы не создаём эти части отдельно.

---

# 2. Входная проверка

Откройте Debian и перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте установленные Apps:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте developer mode:

```bash
bench --site rental.localhost show-config
```

В эффективной конфигурации должно быть:

```text
developer_mode  1
```

Если developer mode выключен, вернитесь к S00. Не создавайте Standard DocType до исправления среды.

Проверьте состояние Git учебного App:

```bash
git -C apps/rental_training status --short
```

Перед началом этапа желательно иметь понятное чистое состояние. Если там уже есть неизвестные изменения, сначала разберитесь с ними.

---

# 3. Почему Equipment — отдельный DocType

Перед созданием задаём архитектурный вопрос:

```text
Equipment имеет собственную идентичность?
→ да

Equipment существует без конкретного Rental?
→ да

Одно Equipment может участвовать в разных Rentals со временем?
→ да

На Equipment будут ссылаться другие Documents?
→ да
```

Следовательно:

```text
Equipment = самостоятельный Document
          = обычный DocType
```

Это не правило «каждое существительное = DocType».

Например `Equipment Type` пока не получает собственного DocType, потому что текущее требование говорит только о небольшом фиксированном наборе значений:

```text
Tool
Camera
Computer
```

У типа пока нет:

- собственных атрибутов;
- собственного lifecycle;
- отдельных прав;
- необходимости ссылаться на него как на самостоятельный Document.

Поэтому сейчас штатная модель проще:

```text
Equipment Type = Select
```

Если позже требования изменятся, решение можно пересмотреть. Но отдельный справочник «на будущее» сейчас был бы лишней сущностью.

---

# 4. Открыть DocType в Desk

Если `bench start` ещё не работает, откройте отдельный терминал:

```bash
cd ~/frappe/rental-training-bench
bench start
```

В браузере откройте:

```text
http://rental.localhost:8000/app
```

Войдите как `Administrator`.

Через строку поиска Desk найдите:

```text
DocType
```

Откройте список DocType и нажмите создание нового.

Почему именно через штатный DocType editor: Frappe рассматривает DocType как основной metadata-объект модели. Нам не нужно вручную создавать SQL-таблицу и затем отдельно описывать ORM и форму.

Официальные источники:

- https://docs.frappe.io/framework/user/en/basics/doctypes
- https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype

---

# 5. Создать каркас Equipment

Заполните основные параметры:

```text
Name            : Equipment
Module          : Rental Training
Custom?         : выключено
Is Child Table  : выключено
Is Single       : выключено
Is Submittable  : выключено
```

## Почему `Custom?` обязательно выключено

Мы создаём модель, принадлежащую устанавливаемому App `rental_training`.

При включённом developer mode Standard DocType сохраняется в исходники App. Именно это состояние потом можно перенести на чистый Site через Git и migration.

Если включить `Custom?`, получится site-local DocType. Это другая ответственность и другой способ владения конфигурацией.

На S02 нужен именно:

```text
App-owned Standard DocType
```

а не:

```text
локальная модель только этого Site
```

Официальный tutorial Frappe отдельно предупреждает, что для генерации файлов DocType `Custom?` должен быть выключен.

---

# 6. Добавить только необходимые поля

Создайте три поля в указанном порядке.

## Поле 1 — Equipment Name

```text
Label      : Equipment Name
Fieldname  : equipment_name
Type       : Data
Mandatory  : yes
Unique     : no
```

Это человекочитаемое название оборудования.

Примеры:

```text
Bosch GBH 2-26
Canon EOS R50
```

Название может измениться, поэтому мы не используем его как системную identity Document.

## Поле 2 — Equipment Type

```text
Label        : Equipment Type
Fieldname    : equipment_type
Type         : Select
Mandatory    : yes
In List View : yes
```

Options, каждая с новой строки:

```text
Tool
Camera
Computer
```

Почему `Select`, а не отдельный DocType, разобрано в разделе 3.

## Поле 3 — Serial Number

```text
Label        : Serial Number
Fieldname    : serial_number
Type         : Data
Mandatory    : no
Unique       : no
In List View : yes
```

Почему `Unique = no`:

CORE пока не содержит бизнес-требования:

```text
каждое Equipment обязано иметь серийный номер
и серийный номер обязан быть глобально уникален
```

Мы не усиливаем предметные правила собственной фантазией.

Если реальный заказчик позже предъявит такое требование, модель изменится тогда.

---

# 7. Настроить системное имя Document

У любого обычного DocType Frappe есть системное поле `name`. Это primary key и стабильный идентификатор Document.

В секции **Naming** установите:

```text
Naming Rule : Expression
Auto Name   : EQ-.#####
```

Ожидаемый результат:

```text
EQ-00001
EQ-00002
EQ-00003
```

Это штатный `Expression` naming Frappe.

Не выбирайте:

```text
By fieldname → equipment_name
By fieldname → serial_number
By script
UUID
```

не потому, что эти варианты плохие, а потому что для текущего требования они не нужны.

### Почему не `equipment_name`

Пользователь может исправить название:

```text
Bosch GBH 2-26
→
Bosch GBH 2-26 DRE
```

Идентичность Equipment при этом не должна меняться.

### Почему не `serial_number`

Серийный номер у нас необязателен и не объявлен глобально уникальным.

Следовательно он не может выполнять роль обязательной identity.

Официальный Frappe naming guide прямо определяет `name` как уникальный ID Document и поддерживает `Expression` как штатную схему именования.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/naming

---

# 8. Настроить человекочитаемый title

В **View Settings** установите:

```text
Title Field               : equipment_name
Show Title in Link Fields : yes
```

Получаем две разные вещи:

```text
name
= EQ-00001
= стабильная identity

Title Field
= Bosch GBH 2-26
= человекочитаемое представление
```

Это принципиально разные обязанности.

Когда позже `Rental Item` будет ссылаться на Equipment через `Link`, Frappe сможет показывать человеку `equipment_name`, сохраняя ссылку на стабильный `name`.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/form_%26_view_settings

---

# 9. Перед сохранением сверить модель

Должно быть:

```text
Equipment

Module          = Rental Training
Custom?         = no
Is Child Table  = no
Is Single       = no
Is Submittable  = no

Naming Rule     = Expression
Auto Name       = EQ-.#####

Title Field               = equipment_name
Show Title in Link Fields = yes

Fields
1. equipment_name  Data    mandatory
2. equipment_type  Select  mandatory, in list view
3. serial_number   Data    optional, in list view
```

Не добавляйте сейчас:

```text
status
available
owner
location
price
purchase_date
notes
Equipment Type DocType
Workspace
Workflow
Role
Client Script
Server Script
Python validation
```

Для них пока нет требования CORE.

---

# 10. Сохранить DocType

Нажмите **Save**.

После сохранения Frappe должен создать Standard DocType `Equipment`.

Теперь откройте через Desk список:

```text
Equipment
```

Вы должны получить обычный List View, хотя мы отдельно List View не программировали.

Создание новой записи должно открыть обычную Form.

Это первая важная практическая демонстрация metadata-driven архитектуры:

```text
мы описали DocType
↓
Frappe дал хранение + Document + Form + List
```

Официальная документация описывает DocType как core building block приложения и указывает, что после его создания Frappe предоставляет стандартные List и Form views.

---

# 11. Проверить, что Frappe создал исходники App

Вернитесь в терминал Bench:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Должны появиться новые файлы внутри Module `Rental Training`.

Посмотрите только каталог Equipment:

```bash
find apps/rental_training/rental_training/rental_training/doctype/equipment \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидайте файлы примерно такого назначения:

```text
__init__.py
equipment.json    metadata DocType
equipment.py      Python controller
equipment.js      client-side controller
test_equipment.py test boilerplate
```

Точный набор служебных boilerplate-файлов определяется текущим scaffold Frappe, поэтому критерием является не буквальное количество файлов, а наличие App-owned metadata и controller/test locations.

### Главное

Мы **не создавали вручную** `equipment.json`, `equipment.py`, `equipment.js` и test boilerplate.

Их создал штатный механизм Frappe для Standard DocType.

Официальный tutorial показывает тот же принцип: JSON описывает DocType, Python-файл является controller, JS-файл — client controller, а test-файл создаётся как заготовка тестов.

---

# 12. Открыть `equipment.json`

Посмотрите файл:

```bash
cd ~/frappe/rental-training-bench

sed -n '1,260p' \
  apps/rental_training/rental_training/rental_training/doctype/equipment/equipment.json
```

Не редактируйте его сейчас руками.

Найдите глазами:

```text
module
fields
fieldname
fieldtype
reqd
in_list_view
naming_rule / autoname
title_field
show_title_field_in_link
```

Формат JSON может содержать больше технических metadata-полей, чем мы вводили в форме. Это нормально.

Нужно понять связь:

```text
DocType editor в Desk
        ↓ сохраняет
metadata Standard DocType
        ↓ находится в
App source
```

То есть UI здесь не создаёт «магическую настройку отдельно от кода». Для Standard DocType metadata является частью исходного состояния App.

---

# 13. Создать три контрольные записи

Через стандартную Form создайте:

## Equipment 1

```text
Equipment Name : Bosch GBH 2-26
Equipment Type : Tool
Serial Number  : BH-10001
```

После сохранения ожидается:

```text
name = EQ-00001
```

## Equipment 2

```text
Equipment Name : Canon EOS R50
Equipment Type : Camera
Serial Number  : CR50-20001
```

Ожидается:

```text
name = EQ-00002
```

## Equipment 3

```text
Equipment Name : Lenovo ThinkPad E14
Equipment Type : Computer
Serial Number  : LTP-30001
```

Ожидается:

```text
name = EQ-00003
```

Если номера отличаются потому, что вы уже создавали и удаляли тестовые Documents, не пытайтесь вручную «открутить счётчик» ради красивого результата. Важен формат `EQ-#####`, а не искусственное совпадение номера после экспериментов.

На чистом прохождении ожидаются значения из спецификации.

---

# 14. Проверить List без собственного UI

Откройте Equipment List.

Убедитесь, что записи находятся через стандартный интерфейс.

Проверьте фильтр:

```text
Equipment Type = Camera
```

В результате должна остаться запись Canon.

Затем фильтр:

```text
Equipment Type = Tool
```

Должна остаться Bosch.

Никакой отдельный экран каталога оборудования мы не создавали.

Текущее требование нормально выражается стандартным Desk List.

---

# 15. Проверить разницу между `name` и Title Field

Откройте:

```text
EQ-00001
```

Измените:

```text
Equipment Name
Bosch GBH 2-26
```

на:

```text
Bosch GBH 2-26 DRE
```

Сохраните.

Проверьте:

```text
Title изменился
name остался EQ-00001
```

Это и есть требуемая модель:

```text
отображаемое название можно исправлять
≠
идентичность Document должна измениться
```

Позже Link на `EQ-00001` продолжит ссылаться на тот же Equipment, даже если пользовательское название поменялось.

---

# 16. Что мы намеренно НЕ проверяем через Link на S02

В спецификации есть проверка отображения Title в Link Fields.

Но отдельного предметного `Link → Equipment` в приложении пока ещё нет. Он появится естественно на S04 внутри `Rental Item`.

Поэтому сейчас мы **не создаём искусственный тестовый DocType или лишнее Link-поле** только ради демонстрации настройки.

На S02 достаточно проверить:

```text
Title Field настроен
Show Title in Link Fields включён
name и title различаются
```

Фактическое поведение Link проверим тогда, когда бизнес-модель действительно потребует Link.

Это важнее формального «покрытия функции».

---

# 17. Не изменять модель прямым SQL

Для приёмки S02 прямой доступ к MariaDB не требуется.

Не выполняйте ручные `INSERT`, `UPDATE`, `ALTER TABLE` или другие изменения `tabEquipment` через MariaDB.

Причина простая: приложение должно работать через модель Frappe, а не обходить Document lifecycle и metadata вручную.

Прямой SQL может быть полезен для диагностики и чтения, но он не является способом построения этой модели.

---

# 18. Проверить Git после создания DocType

Сначала посмотрите, какие файлы появились:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Новые файлы на этом шаге могут быть `untracked`, поэтому обычный `git diff` их ещё не покажет. Это нормально.

Добавьте generated source в индекс Git:

```bash
git add rental_training/rental_training/doctype
```

Теперь посмотрите staged diff:

```bash
git diff --cached -- rental_training/rental_training/doctype
```

Проверьте:

```bash
git status
```

Новые файлы Equipment должны принадлежать repository `rental_training`.

Создайте commit:

```bash
git commit -m "feat: add Equipment doctype"
```

Это не декоративный Git-шаг.

Теперь metadata модели хранится в исходниках App и может участвовать в дальнейшем clean-install тесте.

---

# 19. Архитектурный разбор результата

После S02 ученик должен уметь восстановить решение от требования, а не от меню Frappe.

## Требование 1

```text
Оборудование существует самостоятельно
```

Решение:

```text
normal DocType Equipment
```

## Требование 2

```text
У оборудования есть простое название
```

Решение:

```text
DocField Data
```

## Требование 3

```text
Тип выбирается из маленького стабильного списка
```

Решение:

```text
Select
```

а не новый справочник без собственной ответственности.

## Требование 4

```text
Нужна стабильная identity
```

Решение:

```text
name через штатный Expression
EQ-.#####
```

## Требование 5

```text
Пользователь должен видеть нормальное название
```

Решение:

```text
Title Field = equipment_name
Show Title in Link Fields = yes
```

## Требование 6

```text
Модель принадлежит устанавливаемому App
```

Решение:

```text
developer mode
+ Standard DocType
+ Custom? = no
+ generated metadata в Git
```

---

# 20. Почему здесь пока нет Python-кода

Frappe создал `equipment.py`, но на S02 у нас нет бизнес-требования, для которого нужен controller behavior.

Поэтому правильный Python controller сейчас может быть почти пустым.

Мы не добавляем искусственную функцию только для того, чтобы «попробовать Python».

Код появится в CORE тогда, когда появится ответственность, которую metadata сама не гарантирует — например серверные инварианты Rental.

Правило не такое:

```text
сначала no-code
потом low-code
потом code
```

Правило такое:

```text
требование
↓
ответственность
↓
штатный механизм Frappe
↓
код только если для требования действительно нужна новая логика
```

---

# 21. Типичные неправильные решения

## Ошибка 1 — создать `Equipment Type` DocType заранее

Получается:

```text
Equipment
  ↓ Link
Equipment Type
```

Хотя у `Equipment Type` нет собственной модели.

Почему плохо: добавлена сущность и управление связями без требования.

Правильное решение сейчас:

```text
Select
```

## Ошибка 2 — сделать `equipment_name` системным `name`

Почему плохо: человекочитаемое название может исправляться и не обязано быть подходящей стабильной identity.

Правильное решение:

```text
name = EQ-00001
Title = Bosch GBH 2-26
```

## Ошибка 3 — создать Custom DocType

Почему плохо: обязательная модель учебного App останется site-local вместо App-owned source.

Правильное решение:

```text
Standard DocType
Custom? = no
```

## Ошибка 4 — сначала создать SQL-таблицу вручную

Почему плохо: мы обходим владельца ответственности — DocType/Document engine Frappe.

Правильное решение:

```text
DocType metadata → Frappe создаёт schema
```

## Ошибка 5 — писать Python для генерации Form/List

Почему плохо: стандартные представления уже следуют из DocType.

Правильное решение:

```text
использовать Desk Form/List
```

---

# 22. Контрольная проверка S02

В терминале:

```bash
cd ~/frappe/rental-training-bench

bench --site rental.localhost list-apps -f text

git -C apps/rental_training status
```

На Site по-прежнему:

```text
frappe
rental_training
```

В Desk существует DocType:

```text
Equipment
```

Он принадлежит:

```text
Module = Rental Training
Custom? = no
```

Модель:

```text
Equipment Name  Data    mandatory
Equipment Type  Select  mandatory
Serial Number   Data    optional
```

Naming:

```text
Expression
EQ-.#####
```

View:

```text
Title Field = equipment_name
Show Title in Link Fields = yes
```

Есть контрольные Documents трёх типов, List фильтруется по `equipment_type`, а изменение `equipment_name` не меняет системный `name`.

В Git присутствуют generated source files Standard DocType.

---

# 23. ГОТОВО

S02 считается пройденным, если ученик без подсказки может объяснить:

```text
1. Почему Equipment является самостоятельным DocType?
2. Почему Equipment Type пока Select, а не DocType?
3. Что такое системный name?
4. Чем name отличается от Title Field?
5. Почему serial_number не используется как name?
6. Почему Custom? должен быть выключен?
7. Что именно Frappe создал автоматически после сохранения DocType?
8. Почему Form и List не потребовали отдельной разработки?
9. Где в repository лежит metadata Equipment?
10. Почему equipment.py пока не нужно наполнять кодом?
```

И руками показать:

```text
Equipment List
→ три записи
→ фильтр Equipment Type
→ EQ-00001
→ изменение Equipment Name
→ name остаётся тем же
→ equipment.json находится внутри rental_training
→ Git содержит изменение модели
```

---

# 24. НЕ ГОТОВО

Не переходите дальше, если:

- `Equipment` создан как `Custom`;
- DocType попал не в Module `Rental Training`;
- создан отдельный `Equipment Type` без нового требования;
- `equipment_name` или `serial_number` необоснованно сделали identity;
- naming не соответствует выбранной Expression-схеме;
- title и `name` воспринимаются как одно и то же;
- обязательные App-owned metadata отсутствуют в Git;
- модель работает только из-за ручных изменений базы;
- ученик не может объяснить, почему Frappe сам дал Form/List;
- в controller добавлен код без предметной ответственности.

Исправьте причину, а не маскируйте её следующим этапом.

---

# 25. Что будет дальше

После S02 у нас есть первый самостоятельный объект:

```text
Equipment
```

Следующий этап S03 добавит второй независимый Document:

```text
Customer
```

Только после этого S04 сможет естественно поставить новый вопрос:

```text
как один Rental связать с существующим Customer
и несколькими существующими Equipment?
```

И именно это требование приведёт нас к штатным механизмам:

```text
Link
Child DocType
Table
```

а не к изучению этих функций ради самих функций.
