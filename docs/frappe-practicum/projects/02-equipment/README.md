# L2. Реестр оборудования

L2 добавляет второй постоянный DocType приложения — `Equipment`.

Цель урока: собрать обычный рабочий DocType, связать его с `Facility Location` и на одном объекте пройти основные типы полей, Naming, Title Field, Search Fields, Quick Entry, Track Changes, форму и список.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

После урока модель приложения выглядит так:

```text
Facility Location
        │
        │ Link
        ▼
    Equipment
```

В `Equipment` будут поля:

| Label | Fieldname | Type | Mandatory | Default |
|---|---|---|---:|---|
| Equipment Code | `equipment_code` | Data | Yes | |
| Equipment Name | `equipment_name` | Data | Yes | |
| Location | `location` | Link → Facility Location | Yes | |
| Category | `category` | Select | Yes | |
| Status | `status` | Select | Yes | Active |
| Serial Number | `serial_number` | Data | No | |
| Commissioning Date | `commissioning_date` | Date | No | |
| Photo | `photo` | Attach Image | No | |
| Notes | `notes` | Small Text | No | |

Naming:

```text
By fieldname
Auto Name: field:equipment_code
```

Title Field:

```text
equipment_name
```

Search Fields:

```text
equipment_name,serial_number,location
```

Статусы:

```text
Active
Out of Service
Retired
```

Категории для учебных данных:

```text
HVAC
Electrical
IT
Other
```

---

# 1. Проверить состояние после L1

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

В Desk должен существовать `Facility Location` с рабочим деревом минимум:

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

Если `Facility Location` не принят — L2 не начинаем.

---

# 2. Зафиксировать модель до кликов

`Equipment` — обычный DocType.

Он не является:

- Tree;
- Child Table;
- Single;
- Submittable.

Каждая запись — отдельная единица оборудования.

Пример:

```text
Equipment Code: EQ-0001
Equipment Name: Кондиционер Daikin 01
Location:       Room 101
Category:       HVAC
Status:         Active
```

Главная связь урока:

```text
Equipment.location
        │
        └── Link → Facility Location
```

`Category` пока оставляем `Select`.

Отдельный DocType `Equipment Type` не создаём.

---

# 3. Создать Standard DocType Equipment

В Desk через Awesomebar открыть:

```text
DocType
```

Создать новый DocType:

```text
Name:   Equipment
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

Это обычный Standard DocType своего app.

---

# 4. Добавить поля

Добавить поля в указанном порядке.

## Основные данные

### Equipment Code

```text
Label:      Equipment Code
Fieldname:  equipment_code
Type:       Data
Mandatory:  Yes
```

### Equipment Name

```text
Label:      Equipment Name
Fieldname:  equipment_name
Type:       Data
Mandatory:  Yes
```

### Column Break

Добавить `Column Break`.

### Location

```text
Label:      Location
Fieldname:  location
Type:       Link
Options:    Facility Location
Mandatory:  Yes
```

### Category

```text
Label:      Category
Fieldname:  category
Type:       Select
Mandatory:  Yes
Options:
HVAC
Electrical
IT
Other
```

### Status

```text
Label:      Status
Fieldname:  status
Type:       Select
Mandatory:  Yes
Default:    Active
Options:
Active
Out of Service
Retired
```

---

# 5. Добавить секцию Additional Information

Добавить `Section Break`:

```text
Label: Additional Information
```

После него добавить:

### Serial Number

```text
Label:      Serial Number
Fieldname:  serial_number
Type:       Data
Mandatory:  No
```

### Commissioning Date

```text
Label:      Commissioning Date
Fieldname:  commissioning_date
Type:       Date
Mandatory:  No
```

### Column Break

Добавить `Column Break`.

### Photo

```text
Label:      Photo
Fieldname:  photo
Type:       Attach Image
Mandatory:  No
```

### Notes

```text
Label:      Notes
Fieldname:  notes
Type:       Small Text
Mandatory:  No
```

В результате форма должна быть компактной:

```text
[ Equipment Code ]   [ Location ]
[ Equipment Name ]   [ Category ]
                     [ Status ]

Additional Information

[ Serial Number ]    [ Photo ]
[ Commissioning ]    [ Notes ]
```

Не добавлять поля только ради демонстрации Field Types.

---

# 6. Настроить Naming

Открыть настройки Naming DocType `Equipment`.

Выбрать:

```text
Naming Rule: By fieldname
Auto Name:   field:equipment_code
```

Смысл:

```text
Equipment Code
= технический идентификатор Document
= name
```

Например:

```text
Equipment Code = EQ-0001
name           = EQ-0001
```

`Equipment Name` при этом может быть человекочитаемым названием и не обязан быть уникальным.

---

# 7. Настроить Title Field

Указать:

```text
Title Field: equipment_name
```

После этого Frappe сможет показывать человеку название оборудования, сохраняя `name` равным коду.

Нужно различать:

```text
name
= EQ-0001

Title
= Кондиционер Daikin 01
```

Не менять Naming на `equipment_name`.

---

# 8. Настроить Search Fields

Указать:

```text
Search Fields:
equipment_name,serial_number,location
```

Задача — находить Equipment не только по `name`, но и по полезным рабочим данным.

После сохранения позже проверим поиск по:

```text
Daikin
SN-AC-001
Room 101
```

---

# 9. Включить Track Changes

В настройках DocType включить:

```text
Track Changes = Yes
```

Это нужно, чтобы изменение важных данных Equipment появлялось в Timeline/Version.

Не включать дополнительные tracking-флаги только ради урока.

---

# 10. Включить Quick Entry

В настройках DocType включить:

```text
Quick Entry = Yes
```

Quick Entry нужен только для проверки штатного механизма быстрого создания записи.

Обязательные поля Equipment:

```text
equipment_code
equipment_name
location
category
status
```

`Status` имеет default `Active`.

Если Quick Entry в фактическом v16.32.0 показывает обязательные поля и позволяет корректно создать Equipment — механизм принят.

Не подгонять модель специально под Quick Entry.

---

# 11. Сохранить DocType

Сохранить `Equipment`.

После сохранения открыть созданный DocType ещё раз и проверить:

```text
Module = Facility Operations
Custom = No
Is Tree = No
Track Changes = Yes
Quick Entry = Yes
Naming Rule = By fieldname
Auto Name = field:equipment_code
Title Field = equipment_name
```

---

# 12. Проверить generated metadata

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations/doctype/equipment \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидается boilerplate примерно:

```text
__init__.py
equipment.js
equipment.json
equipment.py
test_equipment.py
```

Открыть metadata:

```bash
sed -n '1,320p' \
  facility_ops/facility_operations/doctype/equipment/equipment.json
```

Найти и проверить:

```text
"name": "Equipment"
"module": "Facility Operations"
"naming_rule": "By fieldname"
"autoname": "field:equipment_code"
"title_field": "equipment_name"
"search_fields"
"track_changes": 1
"quick_entry": 1
```

Также найти поля:

```text
equipment_code
equipment_name
location
category
status
serial_number
commissioning_date
photo
notes
```

JSON вручную не редактировать.

---

# 13. Создать первую запись через обычную Form View

Открыть `Equipment` → New.

Создать:

```text
Equipment Code:     EQ-0001
Equipment Name:     Кондиционер Daikin 01
Location:           Room 101
Category:           HVAC
Status:             Active
Serial Number:      SN-AC-001
Commissioning Date: 2026-01-15
Notes:              Основной кондиционер помещения
```

Фото можно прикрепить любым тестовым изображением.

Сохранить.

Проверить:

```text
name = EQ-0001
```

а заголовок формы должен использовать `Equipment Name` как Title Field.

---

# 14. Проверить Link на Facility Location

В новой записи открыть поле `Location`.

В Link должны выбираться существующие документы `Facility Location`.

Использовать:

```text
Room 101
Room 102
Warehouse
```

Не вводить местоположение второй строкой вручную в Equipment.

Смысл Link:

```text
Location
не копия текста

Location
= ссылка на существующий Document Facility Location
```

---

# 15. Создать набор тестовых Equipment

Создать минимум 8 записей.

| Code | Name | Location | Category | Status | Serial |
|---|---|---|---|---|---|
| EQ-0001 | Кондиционер Daikin 01 | Room 101 | HVAC | Active | SN-AC-001 |
| EQ-0002 | Кондиционер Daikin 02 | Room 102 | HVAC | Active | SN-AC-002 |
| EQ-0003 | Щит распределительный 01 | Floor 1 | Electrical | Active | SN-EL-001 |
| EQ-0004 | Коммутатор 24-port 01 | Room 101 | IT | Active | SN-IT-001 |
| EQ-0005 | Точка доступа Wi-Fi 01 | Room 102 | IT | Active | SN-IT-002 |
| EQ-0006 | ИБП 01 | Warehouse | Electrical | Out of Service | SN-EL-002 |
| EQ-0007 | Ноутбук сервисный 01 | Warehouse | IT | Active | SN-IT-003 |
| EQ-0008 | Старый кондиционер 01 | Floor 2 | HVAC | Retired | SN-AC-008 |

Все записи создаются вручную.

Data Import будет отдельным L3.

---

# 16. Проверить Naming отрицательным сценарием

Попробовать создать ещё один Equipment:

```text
Equipment Code: EQ-0001
Equipment Name: Тестовый дубликат
Location:       Warehouse
Category:       Other
```

Сохранение не должно создать второй Document с тем же `name`.

После проверки отменить создание дубликата.

Главное:

```text
Equipment Code
= уникальный name

Equipment Name
= отображаемое название
= не идентификатор Document
```

---

# 17. Проверить Mandatory

Попробовать создать Equipment без `Location`.

Например:

```text
Equipment Code: EQ-TEST-01
Equipment Name: Без места
Category:       Other
Status:         Active
Location:       пусто
```

Сохранение должно быть остановлено обязательностью поля `Location`.

После проверки запись не сохранять.

---

# 18. Проверить Quick Entry

Из списка Equipment использовать стандартное создание новой записи при включённом `Quick Entry`.

Создать:

```text
Equipment Code: EQ-0009
Equipment Name: Принтер 01
Location:       Room 101
Category:       IT
Status:         Active
```

Сохранить через Quick Entry.

После создания открыть полную форму `EQ-0009` и убедиться, что это обычный Document `Equipment`, а не отдельный тип записи.

Quick Entry:

```text
= другой интерфейс создания того же Document
```

---

# 19. Проверить Title и поиск

Открыть список Equipment.

Проверить поиск минимум по трём значениям:

```text
Daikin
SN-IT-001
Room 101
```

Проверить, что пользователь видит понятные названия Equipment, но `name` остаётся кодом `EQ-....`.

Ученик должен уметь объяснить:

```text
name
≠
Title Field
```

---

# 20. Проверить Track Changes

Открыть:

```text
EQ-0006
```

Изменить:

```text
Status:
Out of Service → Active
```

Сохранить.

Проверить Timeline / историю изменений.

Затем вернуть:

```text
Status = Out of Service
```

и снова сохранить.

Нужно увидеть, что изменение рабочего Document отражается в Timeline/Version благодаря `Track Changes`.

Это изменение данных site, а не metadata DocType.

---

# 21. Проверить Form View и List View

## Form View

Открыть несколько Equipment и убедиться, что:

- основные данные сгруппированы отдельно от дополнительных;
- `Location` работает как Link;
- `Photo` принимает изображение;
- `Status` и `Category` работают как Select;
- `Commissioning Date` работает как Date.

## List View

Открыть список Equipment.

Проверить:

- открытие документа из списка;
- стандартную сортировку;
- отображение `name`/Title;
- стандартный фильтр по `Status`;
- стандартный фильтр по `Location`.

Глубокая работа с фильтрами, сохранёнными выборками, импортом и экспортом начинается в L3.

---

# 22. Отличить Select от Link

На одной форме теперь есть оба механизма.

## Category / Status

```text
Select
```

Значения заданы непосредственно в metadata поля.

Например:

```text
HVAC
Electrical
IT
Other
```

## Location

```text
Link → Facility Location
```

Значения являются отдельными Documents другого DocType.

Критерий выбора:

```text
простая фиксированная палитра значений
→ Select

самостоятельные записи со своим lifecycle / данными
→ Link
```

---

# 23. Проверить Git после создания рабочих данных

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

В Git должны находиться изменения Standard metadata `Equipment`.

Созданные записи:

```text
EQ-0001
EQ-0002
...
```

не должны создавать отдельные source-файлы app.

Модель остаётся той же:

```text
equipment.json
= metadata
= app / Git

EQ-0001
= Document
= database site
```

---

# 24. Зафиксировать L2 в Git

Проверить изменения:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

Добавить:

```bash
git add .
git diff --cached
```

Убедиться, что в commit входят только файлы приложения.

Commit:

```bash
git commit -m "Add equipment registry"
git status
```

Ожидается:

```text
working tree clean
```

---

# 25. Самостоятельное изменение

Без готовой последовательности добавить к `Equipment` поле:

```text
Manufacturer
```

Требования:

```text
Type: Data
Mandatory: No
```

Разместить его в основной части формы рядом с `Equipment Name`.

После изменения:

1. открыть существующий `EQ-0001`;
2. заполнить `Manufacturer = Daikin`;
3. сохранить;
4. убедиться, что старые Documents не пришлось пересоздавать;
5. посмотреть Git diff metadata;
6. сделать commit:

```bash
git add .
git diff --cached
git commit -m "Add equipment manufacturer"
git status
```

Ученик должен увидеть:

```text
изменили schema / metadata DocType
→ существующие Documents продолжили жить
```

---

# 26. Приёмка L2

L2 принят, если ученик может показать следующее.

## В Desk

- `Equipment` существует как Standard DocType;
- Module = `Facility Operations`;
- `Equipment Code` формирует `name`;
- `Equipment Name` используется как Title Field;
- `Location` связан с `Facility Location` через Link;
- `Category` и `Status` являются Select;
- Status по умолчанию = `Active`;
- Quick Entry работает;
- Track Changes работает;
- создано минимум 8 рабочих Equipment.

## В app

Существует каталог:

```text
facility_ops/
└── facility_operations/
    └── doctype/
        └── equipment/
```

и Standard metadata находится в Git.

## В объяснении

Ученик без подсказки отвечает:

1. Почему `Equipment` — обычный DocType, а не Tree?
2. Чем `Link` отличается от `Select`?
3. Что является `name` Equipment?
4. Зачем нужен Title Field, если уже есть `name`?
5. Что дают Search Fields?
6. Что делает Quick Entry?
7. Где хранится изменение `Status` конкретного `EQ-0006`?
8. Где хранится добавление поля `Manufacturer` в DocType?
9. Почему создание восьми Equipment не создаёт восемь файлов в app?

## В Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое.

После принятия L2 переходим к **L3 — Работа с данными**, где уже существующий `Equipment` будет использоваться для Filters, Sorting, Data Import, Export и массовой работы.
