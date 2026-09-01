# L3. Работа с данными

L3 не добавляет новые DocType.

Цель урока: научиться нормально работать с уже существующим `Equipment` как с реестром данных — фильтровать, сортировать, сохранять фильтры, импортировать новые записи, экспортировать выборку и выполнять безопасную массовую операцию.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

После урока:

- `Equipment` разрешён для Data Import;
- в реестре есть исходные записи L2 и импортированный набор;
- создан персональный Saved Filter;
- выполнен успешный импорт;
- выполнен один отрицательный импорт;
- выполнен экспорт отфильтрованной выборки;
- выполнен Bulk Edit нескольких записей;
- ученик понимает, какие изменения затрагивают metadata app, а какие являются только рабочими данными site.

Основная идея урока:

```text
DocType metadata
      ↓
определяет структуру и возможности
      ↓
Documents
      ↓
фильтры / импорт / экспорт / массовая работа
```

---

# 1. Проверить состояние после L2

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

В Desk должны существовать:

```text
Facility Location
Equipment
```

а в `Equipment` — записи из L2.

Минимально должны быть доступны статусы:

```text
Active
Out of Service
Retired
```

и категории:

```text
HVAC
Electrical
IT
Other
```

---

# 2. Включить Allow Import у Equipment

В Desk открыть:

```text
DocType → Equipment
```

В настройках DocType включить:

```text
Allow Import = Yes
```

Сохранить DocType.

Это первое изменение L3, которое действительно меняет metadata приложения.

Сразу проверить Git:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/equipment/equipment.json
```

Найти изменение:

```text
"allow_import": 1
```

Зафиксировать смысл:

```text
Allow Import
= свойство DocType
= metadata
= изменение app
= Git diff
```

Пока commit не делать.

---

# 3. Открыть List View Equipment

Через Awesomebar открыть:

```text
Equipment
```

Перейти в обычный List View.

Не открывая отдельные формы, найти в списке:

- код оборудования;
- название;
- Location;
- Category;
- Status.

Если часть полезных полей не видна в текущем List View, использовать штатные настройки списка, а не менять предметную модель только ради внешнего вида.

Цель этого шага — перейти от работы с одной формой к работе с набором Documents.

---

# 4. Фильтры

Сначала применить один фильтр:

```text
Status = Active
```

Убедиться, что записи `Out of Service` и `Retired` исчезли из текущей выборки.

Затем добавить второй фильтр:

```text
Category = IT
```

Получить выборку:

```text
Status = Active
AND
Category = IT
```

Проверить, что в неё входят только активные IT-устройства.

После этого очистить фильтры и проверить другой сценарий:

```text
Location = Warehouse
```

Главное:

```text
Filter
не меняет Document
не меняет DocType
не меняет Git

Filter
меняет только текущую выборку
```

---

# 5. Сохранить фильтр

Снова установить:

```text
Status = Active
Category = IT
```

Открыть меню:

```text
Saved Filters
```

выбрать:

```text
Save Current Filter
```

Название:

```text
Active IT Equipment
```

`Is Global` не включать.

После сохранения:

1. очистить текущие фильтры;
2. выбрать `Active IT Equipment` из Saved Filters;
3. убедиться, что оба условия применились снова.

В Frappe v16.32.0 Saved Filter является записью `List Filter`, а не Standard metadata `Equipment`.

Проверить Git:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status --short
```

Создание Saved Filter само по себе не должно создавать новый source-файл `facility_ops`.

Главное различие:

```text
Equipment.allow_import
= metadata app

Active IT Equipment
= пользовательская/системная запись Saved Filter на site
```

---

# 6. Сортировка

Очистить фильтры.

В List View проверить сортировку минимум двумя способами.

## Вариант 1

```text
Equipment Name
Ascending
```

## Вариант 2

```text
Modified
Descending
```

После переключения убедиться, что меняется порядок строк, но сами Documents не изменяются.

Зафиксировать:

```text
Sorting
= представление выборки
≠ изменение данных
```

---

# 7. Открыть Data Import

Через Awesomebar открыть:

```text
Data Import
```

Создать новый Data Import:

```text
Reference DocType: Equipment
Import Type:       Insert New Records
```

Если `Equipment` нельзя выбрать или Frappe сообщает, что импорт запрещён, вернуться к шагу 2 и проверить `Allow Import`.

Frappe v16.32.0 проверяет `allow_import` у целевого DocType перед импортом.

---

# 8. Скачать штатный шаблон

В Data Import скачать шаблон для `Equipment`.

Не создавать CSV вручную с придуманными заголовками.

Использовать шаблон, сформированный самим Frappe для текущего DocType.

В шаблоне оставить нужные поля и заполнить новые строки.

Для импорта достаточно следующих данных:

| Equipment Code | Equipment Name | Location | Category | Status | Serial Number |
|---|---|---|---|---|---|
| EQ-0010 | Вентилятор вытяжной 01 | Warehouse | HVAC | Active | SN-HV-010 |
| EQ-0011 | Вентилятор вытяжной 02 | Warehouse | HVAC | Active | SN-HV-011 |
| EQ-0012 | Автомат защиты 01 | Floor 1 | Electrical | Active | SN-EL-012 |
| EQ-0013 | Автомат защиты 02 | Floor 2 | Electrical | Active | SN-EL-013 |
| EQ-0014 | Коммутатор 8-port 01 | Room 102 | IT | Active | SN-IT-014 |
| EQ-0015 | Коммутатор 8-port 02 | Room 101 | IT | Active | SN-IT-015 |
| EQ-0016 | Точка доступа Wi-Fi 02 | Room 101 | IT | Active | SN-IT-016 |
| EQ-0017 | Точка доступа Wi-Fi 03 | Room 102 | IT | Active | SN-IT-017 |
| EQ-0018 | Резервный ИБП 01 | Warehouse | Electrical | Out of Service | SN-EL-018 |
| EQ-0019 | Тестовое устройство 01 | Warehouse | Other | Active | SN-OT-019 |

Не изменять названия колонок, созданные Frappe.

Если шаблон содержит служебные или дополнительные колонки, не удалять их без необходимости; достаточно корректно заполнить используемые поля.

---

# 9. Импортировать записи

Загрузить заполненный файл обратно в Data Import.

До запуска проверить Preview.

Убедиться, что значения распознаны в правильных колонках.

Запустить импорт.

Ожидаемый итог:

```text
10 новых Equipment Documents
```

После завершения открыть `Equipment` List View и найти:

```text
EQ-0010
...
EQ-0019
```

Проверить минимум три записи вручную через Form View.

Например:

```text
EQ-0014
EQ-0018
EQ-0019
```

---

# 10. Проверить, что импорт не является изменением app

После успешного импорта:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

Git должен показывать только metadata-изменение `Allow Import`, сделанное в шаге 2.

Он не должен содержать отдельные файлы:

```text
EQ-0010
EQ-0011
...
EQ-0019
```

Зафиксировать:

```text
Data Import
= массовое создание Documents
= рабочие данные site

Allow Import
= изменение Standard DocType
= metadata app
```

---

# 11. Отрицательный тест Data Import

Скачать или использовать новый чистый шаблон `Equipment`.

Создать одну тестовую строку:

```text
Equipment Code: EQ-BAD-01
Equipment Name: Некорректное оборудование
Location:       Unknown Room
Category:       IT
Status:         Active
Serial Number:  SN-BAD-01
```

`Unknown Room` не существует в `Facility Location`.

Запустить импорт отдельно от нормального набора.

Ожидаем:

- запись не должна корректно импортироваться как валидный `Equipment`;
- Data Import должен показать ошибку/failed row;
- существующие нормальные Equipment не должны пострадать.

После проверки убедиться, что `EQ-BAD-01` отсутствует в реестре.

Не создавать `Unknown Room` только для того, чтобы заставить плохой импорт пройти.

---

# 12. Экспортировать отфильтрованную выборку

В `Equipment` List View применить:

```text
Category = IT
Status = Active
```

Открыть штатный Export для `Equipment`.

Экспортировать рабочие поля минимум:

```text
ID / name
Equipment Name
Location
Category
Status
Serial Number
```

Использовать текущую отфильтрованную выборку, если Export dialog предлагает фильтры текущего списка.

Проверить выгруженный CSV/XLSX:

- нет HVAC;
- нет Electrical;
- нет Retired;
- нет Out of Service;
- присутствуют активные IT Equipment.

Главное:

```text
Export
= чтение рабочих данных
≠ перенос приложения
```

Экспорт Equipment не заменяет Git, fixtures или backup site.

---

# 13. Выполнить безопасный Bulk Edit

В List View очистить фильтры и найти:

```text
EQ-0015
EQ-0016
```

Выделить обе записи чекбоксами.

В Actions использовать:

```text
Edit
```

или стандартный Bulk Edit, если интерфейс показывает это название.

Изменить поле:

```text
Status = Out of Service
```

Подтвердить массовое изменение.

Проверить обе записи:

```text
EQ-0015 → Out of Service
EQ-0016 → Out of Service
```

Затем тем же способом вернуть обе записи:

```text
Status = Active
```

Цель упражнения — пройти сам штатный Bulk Edit и оставить итоговые данные в ожидаемом состоянии.

Не использовать массовое удаление в базовом упражнении.

---

# 14. Сравнить одиночное и массовое изменение

Открыть Timeline одной из записей, участвовавших в Bulk Edit.

Поскольку `Track Changes` включён у `Equipment`, проверить, отражаются ли изменения в истории документа на фактическом стенде v16.32.0.

Не делать вывод по памяти или документации, если стенд показывает другое поведение.

Главное различие:

```text
Form Save
= изменение одного Document

Bulk Edit
= штатное массовое изменение нескольких Documents
```

Оба работают с данными, а не создают новый DocType.

---

# 15. Проверить поиск после увеличения реестра

Теперь `Equipment` содержит заметно больше записей.

Проверить поиск по:

```text
EQ-0014
Коммутатор
SN-IT-017
Room 101
```

`Equipment Code` является `name`.

`Equipment Name`, `Serial Number` и `Location` указаны как Search Fields.

Особенно важно проверить поиск, когда `Equipment` позже будет использоваться как Link в `Service Request`.

---

# 16. Зафиксировать metadata L3 в Git

До commit:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
```

В diff должен быть только осознанный metadata-шаг:

```text
Equipment.allow_import = 1
```

Добавить:

```bash
git add \
  facility_ops/facility_operations/doctype/equipment/equipment.json

git diff --cached
```

Commit:

```bash
git commit -m "Enable equipment data import"
git status
```

Ожидается:

```text
working tree clean
```

Импортированные Documents не добавляем в Git.

---

# 17. Самостоятельная работа

Без готовой последовательности выполнить задачу:

> Получить список всего действующего HVAC-оборудования, сохранить фильтр `Active HVAC Equipment`, экспортировать эту выборку и убедиться, что Git после этого остаётся чистым.

Условия:

- новый DocType создавать нельзя;
- поля Equipment менять нельзя;
- рабочие Documents удалять нельзя;
- Saved Filter должен быть персональным;
- экспорт должен содержать только подходящие записи.

---

# 18. Приёмка L3

L3 принят, если ученик может показать следующее.

## List View

- фильтр по одному полю;
- фильтр по нескольким условиям;
- сортировку;
- Saved Filter `Active IT Equipment`;
- выбор нескольких Documents;
- Bulk Edit.

## Data Import

- `Allow Import` включён у `Equipment`;
- штатный шаблон скачан из Frappe;
- 10 записей импортированы;
- отрицательный импорт с несуществующим Link отклонён;
- Import Log / failed row понятен.

## Export

- отфильтрованная выборка выгружена;
- ученик понимает, что это экспорт данных, а не приложение.

## Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Рабочее дерево чистое после commit.

## Объяснение

Ученик без подсказки отвечает:

1. Почему `Allow Import` попал в Git, а 10 импортированных Equipment — нет?
2. Чем Filter отличается от изменения Document?
3. Где живёт Saved Filter?
4. Зачем скачивать import template из Frappe, а не угадывать формат CSV?
5. Почему неправильный `Location` должен ломать импорт конкретной строки?
6. Чем Bulk Edit отличается от изменения metadata DocType?
7. Почему Export Equipment не является способом перенести `facility_ops` на другой site?

После принятия L3 переходим к **L4 — Service Request**, где появляется третий и последний основной DocType приложения.