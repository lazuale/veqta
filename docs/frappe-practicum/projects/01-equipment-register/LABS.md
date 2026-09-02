# P1. Реестр оборудования: лабораторные

Перед началом выполнить [FOUNDATIONS.md](../../FOUNDATIONS.md). Архитектура и границы
продукта описаны в [README.md](README.md).

## P1.1. Создать app и рабочий site

### До начала

- Bench находится в `~/frappe/frappe-practicum-bench`;
- `platform-check.localhost` открывается;
- business app ещё не создан.

### Действия

Из корня Bench:

```bash
cd ~/frappe/frappe-practicum-bench
bench new-app equipment_register
```

Ответы Bench:

| Вопрос | Значение |
|---|---|
| App Title | Equipment Register |
| App Description | Training equipment register |
| App Publisher | своё имя |
| App Email | свой email |
| App License | MIT |
| GitHub Workflow | No |

Создать site и установить app:

```bash
bench new-site equipment.localhost --db-root-username frappe_admin
bench --site equipment.localhost install-app equipment_register
bench --site equipment.localhost set-config developer_mode 1
bench --site equipment.localhost clear-cache
bench --site equipment.localhost list-apps
```

В списке должны быть `frappe` и `equipment_register`.

Открыть `apps/equipment_register/equipment_register/hooks.py` в текстовом редакторе и
добавить после метаданных app:

```python
add_to_apps_screen = [
	{
		"name": "equipment_register",
		"title": "Equipment Register",
		"route": "/desk/equipment-register",
	}
]
```

Это настройка навигации Frappe v16. Здесь нет собственного метода проверки прав или
business logic.

Запустить `bench start`, открыть `http://equipment.localhost:8000` и войти как
Administrator. Через Awesomebar открыть `Module Def` и убедиться, что существует Module
`Equipment Register` с App Name `equipment_register`. Новый Module не создавать.

### Source check

В отдельном терминале:

```bash
cd ~/frappe/frappe-practicum-bench/apps/equipment_register
git status --short --branch
git diff -- equipment_register/hooks.py
```

### Состояние после P1.1

- app установлен только на `equipment.localhost`;
- Developer Mode включён;
- используется созданный Bench Module;
- `hooks.py` содержит `add_to_apps_screen`;
- commit пока не создавался.

## P1.2. Создать модель данных

### Перед созданием DocType

В Awesomebar открыть `Role List` и создать:

- `Equipment Operator`;
- `Equipment Manager`;
- `Equipment Viewer`.

Роли нужны до заполнения Permissions Standard DocType.

### Общий порядок создания Standard DocType

Для каждого DocType:

1. В Awesomebar открыть `DocType List`.
2. Нажать `Add DocType`.
3. Указать Name и Module `Equipment Register`.
4. Не включать `Custom`.
5. Добавить поля в указанном порядке.
6. Задать naming и остальные свойства.
7. Сохранить.
8. Проверить появившийся файл в app.

Подписи в UI могут быть переведены, но технические имена DocType и fieldname вводятся
точно как в таблицах.

### Equipment Location

Создать Standard DocType `Equipment Location`:

- Is Tree: Yes;
- Naming: `field:location_code`;
- Title Field: `location_name`.

Поля:

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Location Code | `location_code` | Data | Mandatory, Set Only Once |
| Location Name | `location_name` | Data | Mandatory, In List View |
| Is Group | `is_group` | Check | системное поле дерева |
| Parent Equipment Location | `parent_equipment_location` | Link | Options `Equipment Location` |

Если Frappe добавил `is_group`, parent, `lft`, `rgt` или `old_parent` автоматически, не
создавать второй экземпляр поля.

### Equipment Category

Создать `Equipment Category`:

- Naming: `field:category_name`;
- Title Field: `category_name`.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Category Name | `category_name` | Data | Mandatory, Set Only Once, In List View |
| Description | `description` | Small Text | без дополнительных флагов |
| Disabled | `disabled` | Check | Default 0 |

### Equipment Identifier

Создать `Equipment Identifier` с `Is Child Table = Yes`:

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Identifier Type | `identifier_type` | Select | Mandatory; `Serial Number`, `Inventory Number`, `Network Address`, `Other` |
| Identifier Value | `identifier_value` | Data | Mandatory, In List View, In Global Search |
| Note | `note` | Small Text | без дополнительных флагов |

Child DocType не получает Permissions и отдельное рабочее место.

### Equipment

Создать `Equipment`:

- Track Changes: Yes;
- Naming: `field:asset_code`;
- Title Field: `equipment_name`.

| Label | Fieldname | Type | Настройки |
|---|---|---|---|
| Asset Code | `asset_code` | Data | Mandatory, Set Only Once, In List View, In Global Search |
| Equipment Name | `equipment_name` | Data | Mandatory, In List View, In Global Search |
| Category | `category` | Link | Mandatory, Options `Equipment Category`, In List View |
| Location | `location` | Link | Mandatory, Options `Equipment Location`, In List View |
| Status | `status` | Select | Mandatory; `In Service`, `In Storage`, `Under Repair`, `Retired`; Default `In Storage` |
| Commissioned On | `commissioned_on` | Date | без дополнительных флагов |
| Identifiers | `identifiers` | Table | Options `Equipment Identifier` |
| Notes | `notes` | Small Text | без дополнительных флагов |

В таблице Permissions каждого самостоятельного DocType задать финальные роли. Для
`Equipment`:

| Role | Read | Write | Create | Delete | Report | Import | Export |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Equipment Operator | Yes | Yes | Yes | No | Yes | No | No |
| Equipment Manager | Yes | Yes | Yes | No | Yes | Yes | Yes |
| Equipment Viewer | Yes | No | No | No | Yes | No | No |

Для Location и Category Manager получает Read/Write/Create, Operator и Viewer — Read.
Права редактировать в DocType, а не сохранять через Role Permission Manager.

### Source check

```bash
cd ~/frappe/frappe-practicum-bench/apps/equipment_register
find equipment_register -type f -path '*doctype*' | sort
git diff --stat
git diff
```

Нужно найти каталоги четырёх DocType. В JSON `Equipment` должны присутствовать поля и
permission rows.

### Состояние после P1.2

- существуют четыре Standard DocType;
- Equipment связан с Category, Location и Identifier;
- коды с naming по полю нельзя менять после первого сохранения;
- permissions находятся в source JSON.

## P1.3. Создать и проверить данные

### Справочники

Создать Location:

| Code | Name | Is Group | Parent |
|---|---|:---:|---|
| HQ | Headquarters | Yes | пусто |
| HQ-STORE | Main Store | No | HQ |

Создать Category:

| Category Name | Description |
|---|---|
| Laptop | Portable computers |
| Printer | Office printers |

Создать Equipment:

| Asset Code | Name | Category | Location | Status | Identifier Type | Identifier Value |
|---|---|---|---|---|---|---|
| EQ-0001 | Office Laptop | Laptop | HQ-STORE | In Service | Serial Number | SN-1001 |
| EQ-0002 | Reserve Laptop | Laptop | HQ-STORE | In Storage | Serial Number | SN-1002 |
| EQ-0003 | Office Printer | Printer | HQ | In Service | Inventory Number | INV-300 |

### Отрицательные проверки

По очереди попытаться сохранить:

1. Equipment без Category.
2. второй Equipment с Asset Code `EQ-0001`.
3. Equipment с несуществующей Category.

Каждую ошибочную запись закрыть без сохранения.

Изменить `equipment_name` у `EQ-0001`: системный `name` должен остаться `EQ-0001`.
Попытка изменить `asset_code` после сохранения должна быть запрещена Set Only Once.

Через глобальный поиск найти `SN-1001`. Результат должен открыть `EQ-0001`. Если запись
не находится, проверить In Global Search у child-поля и пересохранить Equipment.

### Data Import

Открыть `Data Import`, выбрать Equipment и скачать template. Не создавать заголовки
вручную. В копии template добавить ещё две корректные записи, затем отдельно проверить
файл с пустой Category и отсутствующим Link.

После импорта открыть Data Export и выгрузить Equipment. Экспорт документов не должен
создавать новые файлы в репозитории app.

### Состояние после P1.3

- есть минимум пять Equipment;
- обязательность, naming и Link проверены ошибками;
- поиск по child identifier работает;
- ученик различает Data Export и исходники app.

## P1.4. Проверить права

Для каждого пользователя открыть `User List` через Awesomebar, нажать `Add User`,
указать Email и имя, выбрать User Type `System User`, включить нужную Role в таблице
ролей и сохранить. Так как исходящая почта не настроена, пароль задать через поле
`New Password` в карточке User. Не использовать один User с тремя ролями: тогда
проверка не покажет, какая роль выдала право.

Через `User List` создать три System User:

| Email | Role |
|---|---|
| `equipment.operator@example.com` | Equipment Operator |
| `equipment.manager@example.com` | Equipment Manager |
| `equipment.viewer@example.com` | Equipment Viewer |

Задать локальные учебные пароли. Пароли не записывать в app или Git.

Войти по очереди каждым пользователем и заполнить таблицу фактических результатов:

| Проверка | Operator | Manager | Viewer |
|---|---|---|---|
| открыть Equipment List | должно работать | должно работать | должно работать |
| создать Equipment | должно работать | должно работать | запрещено |
| изменить Equipment | должно работать | должно работать | запрещено |
| удалить Equipment | запрещено | запрещено | запрещено |
| экспортировать | запрещено | должно работать | запрещено |

Затем провести три временных опыта:

1. If Owner для Operator.
2. User Permission на Location `HQ-STORE`.
3. Share одного Equipment пользователю без расширения роли.

После каждого опыта записать наблюдение. Затем удалить временные User Permission и
Share, вернуть финальный DocPerm. Role Permission Manager открыть только для просмотра
эффективной матрицы; не сохранять через него Custom DocPerm.

### Состояние после P1.4

- финальная матрица восстановлена;
- временные ограничения удалены;
- Viewer не изменяет документы;
- Assign To и Workflow ещё не используются.

## P1.5. Собрать рабочее место

Настроить List View полями Asset Code, Equipment Name, Category, Location и Status.

Создать общий Kanban Board `Equipment by Status`:

- Reference DocType: Equipment;
- Field: status;
- Private: No.

Переместить `EQ-0002` из `In Storage` в `In Service` и проверить Timeline.

Создать Report Builder report `Equipment Register`:

- Reference DocType: Equipment;
- Is Standard: Yes;
- Module: Equipment Register;
- колонки: Asset Code, Equipment Name, Category, Location, Status.

Создать Number Card `Active Equipment`:

- Document Type: Equipment;
- Function: Count;
- Filter: Status = In Service;
- Is Standard: Yes;
- Module: Equipment Register.

Создать Public Workspace `Equipment Register`, выбрать Module app и добавить shortcut на
Equipment, report и Number Card. После сохранения открыть Apps Page и Workspace Sidebar.

### Проверка

- Card показывает число Equipment со статусом In Service;
- фильтр Report изменяет результат;
- Viewer видит Workspace и Report, но не получает Write;
- Kanban изменяет обычный status, потому что Workflow отсутствует.

## P1.6. Зафиксировать и проверить app на чистом site

В `hooks.py` добавить fixtures:

```python
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", [
			"Equipment Operator",
			"Equipment Manager",
			"Equipment Viewer",
		]]],
	},
	{
		"dt": "Kanban Board",
		"filters": [["name", "=", "Equipment by Status"]],
	},
]
```

Экспортировать и проверить:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site equipment.localhost export-fixtures --app equipment_register
bench --site equipment.localhost migrate

cd apps/equipment_register
git status --short
git diff --check
git diff --stat
git diff
```

В diff не должно быть Users, паролей, User Permission, Share и рабочих Equipment.

Создать commit:

```bash
git add .
git commit -m "Build equipment register practicum app"
git log --oneline -1
```

Создать чистый site:

```bash
cd ~/frappe/frappe-practicum-bench
bench new-site equipment-clean.localhost --db-root-username frappe_admin
bench --site equipment-clean.localhost install-app equipment_register
bench --site equipment-clean.localhost migrate
bench --site equipment-clean.localhost clear-cache
```

На чистом site должны существовать DocType, роли, Workspace, Report, Number Card и Kanban Board,
но не Equipment. Создать заново одного Manager и одного Viewer, затем выполнить P1 из
[ACCEPTANCE.md](../../ACCEPTANCE.md).

P1 закончен только после проверки на чистом site. Следующий проект:
[P2 — лабораторные](../02-purchase-requests/LABS.md).
