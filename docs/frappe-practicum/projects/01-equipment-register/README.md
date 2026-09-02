# Проект 1. Реестр оборудования

## Результат

В конце проекта существует самостоятельный app `equipment_register`, в котором сотрудники ведут оборудование, категории, места и идентификаторы. Реестр устанавливается на чистый site и начинает работу без ERPNext и собственной business logic.

## 1. Сценарий продукта

Пользователь должен уметь:

- зарегистрировать оборудование с устойчивым кодом;
- указать категорию и текущее место;
- сохранить несколько идентификаторов в составе карточки;
- изменить текущее состояние;
- найти и отфильтровать записи;
- загрузить исходный реестр из файла;
- увидеть сводку по состояниям и местам.

Не входят: заявки, ремонты, согласования, история перемещений, амортизация и складской учёт.

## 2. Создать app и site

Из каталога общего bench:

```bash
bench new-app equipment_register
bench new-site equipment.localhost --db-root-username frappe_admin
bench --site equipment.localhost install-app equipment_register
bench --site equipment.localhost set-config developer_mode 1
bench --site equipment.localhost clear-cache
bench --site equipment.localhost list-apps
```

В `list-apps` должны присутствовать `frappe` и `equipment_register`.

Проверить app как отдельный Git repository:

```bash
cd apps/equipment_register
git status --short --branch
find equipment_register -maxdepth 2 -type f | sort
```

Созданный `bench new-app` Module используется как основной. Дополнительный Module без предметной причины не создаётся.

## 3. Спроектировать модель

```text
Equipment Location (Tree) ◄──── Equipment ────► Equipment Category
                                      │
                                      └──── Equipment Identifier (Child)
```

### `Equipment Location`

Standard DocType, `Is Tree = Yes`.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Location Code | `location_code` | Data | Mandatory, Set Only Once |
| Location Name | `location_name` | Data | Mandatory, In List View |
| Is Group | `is_group` | Check | служебная семантика Tree |
| Parent Equipment Location | `parent_equipment_location` | Link | Options: Equipment Location; штатное parent-поле Tree |

Naming: `field:location_code`. Title Field: `location_name`. Отдельный Unique для кода не
нужен, потому что код становится системным `name`.

После включения Tree сверить фактически созданные tree-поля с формой DocType. Не добавлять вручную второй parent или `lft/rgt`.

### `Equipment Category`

Standard DocType.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Category Name | `category_name` | Data | Mandatory, Set Only Once, In List View |
| Description | `description` | Small Text | Optional |
| Disabled | `disabled` | Check | Default 0 |

Naming: `field:category_name`. Title Field: `category_name`.

### `Equipment Identifier`

Standard DocType, `Is Child Table = Yes`.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Identifier Type | `identifier_type` | Select | Mandatory; `Serial Number`, `Inventory Number`, `Network Address`, `Other` |
| Identifier Value | `identifier_value` | Data | Mandatory, In List View, In Global Search |
| Note | `note` | Small Text | Optional |

Строка Identifier не получает собственную роль, naming или отдельный Workspace: её жизненный цикл полностью принадлежит Equipment.

### `Equipment`

Standard DocType, Track Changes включён.

| Label | Fieldname | Type | Правила |
|---|---|---|---|
| Asset Code | `asset_code` | Data | Mandatory, Set Only Once, In List View, In Global Search |
| Equipment Name | `equipment_name` | Data | Mandatory, In List View |
| Category | `category` | Link | Mandatory, Options: Equipment Category, In List View |
| Location | `location` | Link | Mandatory, Options: Equipment Location, In List View |
| Status | `status` | Select | Mandatory; `In Service`, `In Storage`, `Under Repair`, `Retired` |
| Commissioned On | `commissioned_on` | Date | Optional |
| Identifiers | `identifiers` | Table | Options: Equipment Identifier |
| Notes | `notes` | Small Text | Optional |

Naming: `field:asset_code`. Title Field: `equipment_name`. Default Status: `In Storage`.

Не добавлять `assigned_to`, `current_user`, `department`, `workflow_state` и универсальный JSON. Они не нужны принятому сценарию.

## 4. Проверить ядро на малых данных

Вручную создать:

- корневое место `HQ` и дочернее `HQ-STORE`;
- категории `Laptop` и `Printer`;
- минимум три Equipment в разных состояниях;
- два Identifier у одного Equipment.

Обязательные опыты:

1. Сохранить Equipment без Category — сохранение должно быть заблокировано.
2. Создать второй Equipment с тем же `asset_code` — конфликт системного `name` должен
   заблокировать сохранение.
3. Ввести в Link несуществующую Category — должна потребоваться существующая запись.
4. Переименовать отображаемое имя Equipment — `name` остаётся равен устойчивому `asset_code`.
5. Изменить Location и посмотреть Timeline при включённом Track Changes.
6. Найти Equipment через глобальный поиск по `identifier_value` из дочерней строки.

## 5. Импорт и экспорт данных

Порядок импорта важен:

```text
Equipment Location
→ Equipment Category
→ Equipment с child rows
```

Сначала выгрузить template средствами Data Import, затем заполнить его. Не угадывать технические колонки вручную.

Провести два запуска:

- намеренно ошибочный файл: отсутствующий Link, повторный Asset Code, пустое обязательное поле;
- исправленный файл: все строки приняты.

После Data Export объяснить различие:

```text
Data Export = документы
Git source  = модель и переносимые метаданные app
```

## 6. Роли и права

Создать роли:

- `Equipment Operator`;
- `Equipment Manager`;
- `Equipment Viewer`.

Финальная матрица для `Equipment`:

| Роль | Read | Write | Create | Delete | Report | Import | Export |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Operator | Yes | Yes | Yes | No | Yes | No | No |
| Manager | Yes | Yes | Yes | No | Yes | Yes | Yes |
| Viewer | Yes | No | No | No | Yes | No | No |

Для Location и Category Manager управляет справочниками; Operator и Viewer читают их. Удаление используемого справочника не является рабочей операцией.

Создать по одному System User на роль и проверить матрицу входом под каждым пользователем.

Отдельный опыт:

- временно включить `If Owner` для Operator и увидеть строковое ограничение;
- создать User Permission на конкретную ветку Location;
- проверить, как Link-ограничение влияет на видимость;
- точечно Share одну запись пользователю без расширения его роли и затем удалить временный Share;
- затем либо откатить опыт, либо записать его как явную финальную политику.

## 7. Рабочий интерфейс

### List и Form

В List должны быть видны Asset Code, Equipment Name, Category, Location и Status. Проверить стандартный поиск, фильтры и сортировку.

### Kanban

Создать Kanban Board по `status` и переместить Equipment между `In Storage` и `In Service`.

Это допустимо, потому что `status` — обычное поле без Workflow. Этот результат нельзя автоматически переносить на workflow-controlled state проекта 2.

### Аналитика

Создать Standard Report Builder report `Equipment Register` с фильтрами Category, Location и Status.

Создать:

- Number Card `Active Equipment`;
- public Workspace `Equipment Register` с shortcut на Equipment, report и card.

В Frappe v16 проверить не только Workspace, но и его место в Apps Page/Workspace Sidebar.

## 8. Проверка исходников

Из app repository:

```bash
git status --short
find equipment_register -type f | sort
git diff --check
git diff
```

Нужно найти файлы четырёх DocType и standard-объектов интерфейса. Рабочие Equipment не
входят в исходники app.

Три учебные Role и общий Kanban Board зафиксировать fixtures с фильтром по точным
именам. Не экспортировать весь `Role` или `Kanban Board`. Финальные permission rows
настроить в Standard DocType и проверить в его JSON. Не создавать Custom DocPerm для
DocType этого app.

Number Card должен иметь `Is Standard = Yes` и Module app. Workspace должен быть Public
и принадлежать Module app. В `hooks.py` добавить штатный `add_to_apps_screen`, чтобы app
появлялся в навигации Frappe v16.

Выполнить:

```bash
cd ../..
bench --site equipment.localhost migrate
bench --site equipment.localhost clear-cache
cd apps/equipment_register
git add .
git commit -m "Build equipment register practicum app"
```

Перед `git add .` ещё раз убедиться, что в app нет secrets или файлов рабочих вложений.

## 9. Проверка на чистом site

Из bench:

```bash
bench new-site equipment-clean.localhost --db-root-username frappe_admin
bench --site equipment-clean.localhost install-app equipment_register
bench --site equipment-clean.localhost migrate
bench --site equipment-clean.localhost clear-cache
bench --site equipment-clean.localhost list-apps
```

На чистом site проверить:

- четыре DocType существуют;
- Workspace/Report/Card существуют;
- роли и права восстановлены выбранным способом поставки;
- рабочих Equipment нет;
- Manager может создать полный объект;
- Viewer не может его изменить.

Если роли или права исчезли, не создавать их молча вручную. Определить их слой,
исправить поставку app и повторить проверку на чистом site.

## 10. Готовность проекта

Проект принят, когда выполнены все проверки P1 из [ACCEPTANCE.md](../../ACCEPTANCE.md) и ученик может объяснить:

- почему Category — Link, а Identifier — Child Table;
- почему Location — Tree;
- чем `name` отличается от Title Field;
- что хранится в исходниках app, а что остаётся рабочими данными site;
- почему Workflow в этом реестре не нужен.

Дальше: [проект 2 — «Заявки на закупку»](../02-purchase-requests/README.md).

Пошаговое выполнение: [LABS.md](LABS.md).
