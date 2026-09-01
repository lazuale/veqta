# L1. Места эксплуатации

L1 — первый рабочий урок `facility_ops`.

Задача простая: создать иерархию мест эксплуатации и на ней понять, чем настоящий Standard DocType отличается от обычной записи данных.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

После урока в приложении существует один постоянный предметный DocType:

```text
Facility Location
```

и дерево данных:

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

Ученик должен увидеть одновременно четыре вещи:

```text
DocType
→ generated metadata в app

Document
→ конкретный узел дерева в базе site

Tree
→ штатная nested-set структура Frappe

Git
→ изменения Standard metadata приложения
```

---

# 1. Проверить исходное состояние

L1 начинается после принятого L0.

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

Если `Lab Note` из L0 ещё существует, L1 не начинаем: сначала закончить cleanup L0.

---

# 2. Сначала определить модель

До открытия DocType editor фиксируем модель:

```text
Facility Location

данные пользователя:
- Location Name

структура дерева:
- parent
- is_group
- lft
- rgt
```

Технические поля дерева вручную не создаём.

При `Is Tree` Frappe добавляет необходимые nested-set поля сам.

Для L1 собственного поля достаточно одного:

| Label | Fieldname | Type | Mandatory |
|---|---|---|---:|
| Location Name | `location_name` | Data | Yes |

Почему пока только одно поле: задача L1 — понять Tree DocType. Остальные свойства места появятся только если они реально понадобятся приложению.

---

# 3. Создать Standard DocType

В Desk через Awesomebar открыть:

```text
DocType
```

Нажать **New**.

Основные настройки:

```text
Name:   Facility Location
Module: Facility Operations
Custom?: выключено
Is Tree: включено
```

Не включать:

```text
Is Single
Is Child Table
Is Submittable
```

В Form Builder добавить поле:

```text
Label:       Location Name
Fieldname:   location_name
Type:        Data
Mandatory:   Yes
```

Сохранить DocType.

---

# 4. Настроить Naming

Открыть вкладку **Naming**.

Установить:

```text
Naming Rule: By fieldname
Auto Name:   field:location_name
```

Сохранить.

Теперь значение `Location Name` становится системным `name` документа.

Пример:

```text
Location Name = Building A
name          = Building A
```

Это удобно для учебного справочника: в Link и Tree пользователь видит понятное имя без отдельного кода.

Важно понимать ограничение: `name` уникален во всём DocType. Поэтому два узла с одинаковым `Location Name` создать нельзя, даже если они находятся в разных ветках дерева.

---

# 5. Посмотреть, что Frappe добавил сам

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations/doctype/facility_location \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидается каталог Standard DocType с boilerplate примерно такого состава:

```text
__init__.py
facility_location.js
facility_location.json
facility_location.py
test_facility_location.py
```

Посмотреть metadata:

```bash
sed -n '1,280p' \
  facility_ops/facility_operations/doctype/facility_location/facility_location.json
```

Найти:

```text
"is_tree": 1
"nsm_parent_field"
"location_name"
"is_group"
"lft"
"rgt"
```

Также должен существовать parent field дерева для `Facility Location`, например:

```text
parent_facility_location
```

Зафиксировать вывод:

```text
Мы создали только Location Name.

Tree infrastructure
Frappe добавил сам.
```

`lft`, `rgt`, parent field и `is_group` вручную не редактировать.

---

# 6. Открыть Tree View

Через Awesomebar открыть:

```text
Facility Location
```

Работаем с Tree View этого DocType.

Первым создаём корневой узел:

```text
Location Name: Main Site
Parent:        пусто
Is Group:      включено
```

`Is Group` означает, что под узлом могут находиться дочерние элементы.

Сохранить.

---

# 7. Построить иерархию

Создать следующие узлы.

## Building A

```text
Location Name: Building A
Parent:        Main Site
Is Group:      включено
```

## Floor 1

```text
Location Name: Floor 1
Parent:        Building A
Is Group:      включено
```

## Room 101

```text
Location Name: Room 101
Parent:        Floor 1
Is Group:      выключено
```

## Room 102

```text
Location Name: Room 102
Parent:        Floor 1
Is Group:      выключено
```

## Floor 2

```text
Location Name: Floor 2
Parent:        Building A
Is Group:      включено
```

## Warehouse

```text
Location Name: Warehouse
Parent:        Main Site
Is Group:      выключено
```

Итог:

```text
Main Site
├── Building A
│   ├── Floor 1
│   │   ├── Room 101
│   │   └── Room 102
│   └── Floor 2
└── Warehouse
```

---

# 8. Понять Group и Leaf

В дереве теперь есть два типа узлов.

Группы:

```text
Main Site
Building A
Floor 1
Floor 2
```

Конечные узлы:

```text
Room 101
Room 102
Warehouse
```

Главное различие:

```text
Is Group = 1
→ узел может содержать дочерние узлы

Is Group = 0
→ конечный рабочий узел
```

Не создаём отдельный DocType для здания, этажа, комнаты и склада.

Именно иерархия является причиной выбора Tree DocType.

---

# 9. Проверить Naming отрицательным сценарием

Попробовать создать ещё один узел:

```text
Location Name: Room 101
Parent:        Floor 2
```

Сохранение не должно создать второй Document с тем же `name`.

После проверки отменить создание дубликата.

Что нужно понять:

```text
Parent
не является частью name.

By fieldname
делает location_name глобально уникальным идентификатором Document.
```

Для учебного приложения это принимаем сознательно.

Если в реальном проекте понадобятся одинаковые названия помещений в разных зданиях, Naming придётся спроектировать иначе.

---

# 10. Отличить metadata от данных

После создания всех узлов выполнить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

В Git должны быть изменения Standard DocType.

Создание:

```text
Main Site
Building A
Floor 1
Room 101
...
```

не должно создавать отдельные source-файлы для каждого узла.

Итоговая модель:

```text
Facility Location.json
= metadata приложения
= Git

Room 101
= Document
= database конкретного site
```

---

# 11. Посмотреть metadata осознанно

Открыть:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

sed -n '1,280p' \
  facility_ops/facility_operations/doctype/facility_location/facility_location.json
```

Ученик должен самостоятельно найти и объяснить:

- имя DocType;
- Module;
- `is_tree`;
- `nsm_parent_field`;
- `location_name`;
- `naming_rule`;
- `autoname`;
- автоматически добавленные nested-set поля.

JSON вручную не менять.

---

# 12. Зафиксировать L1 в Git

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

Добавить изменения:

```bash
git add .
git diff --cached
```

Перед commit убедиться, что фиксируется только metadata приложения, а не какие-либо пароли, site config или рабочие данные.

Commit:

```bash
git commit -m "Add facility location tree"
git status
```

Ожидается:

```text
working tree clean
```

---

# 13. Самостоятельное изменение

Без готовой последовательности добавить в дерево:

```text
Building B
└── Floor 1 B
    └── Room 201
```

Условия:

- существующую ветку `Building A` не менять;
- `Building B` и `Floor 1 B` должны быть группами;
- `Room 201` должен быть конечным узлом;
- новый DocType создавать нельзя;
- metadata DocType из-за добавления обычных Documents меняться не должна.

После выполнения проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Если после предыдущего commit менялись только Documents, Git должен остаться чистым.

---

# 14. Приёмка L1

L1 принят, если ученик может показать:

## В Desk

- `Facility Location` существует как Standard DocType;
- Module = `Facility Operations`;
- `Is Tree` включён;
- дерево построено;
- group и leaf nodes различаются;
- `Location Name` используется для Naming.

## В app

```text
facility_ops/
└── facility_operations/
    └── doctype/
        └── facility_location/
```

и generated metadata DocType находится в Git.

## В объяснении

Ученик без подсказки отвечает:

1. Почему `Facility Location` — Tree DocType, а не обычный DocType?
2. Что такое `Document` в этом уроке?
3. Почему `Room 101` не является отдельным файлом app?
4. Что делает `By fieldname`?
5. Зачем нужен `Is Group`?
6. Кто создал `lft`, `rgt` и parent field?
7. Почему не нужны отдельные DocType `Building`, `Floor` и `Room`?

## В Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое.

После принятия L1 переходим к **L2 — Equipment**, где `Facility Location` впервые будет использоваться как настоящий `Link` из другого DocType.
