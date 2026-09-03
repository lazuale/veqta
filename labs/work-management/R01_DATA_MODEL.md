# R01. Модель данных Work Item

## Что проверяем

Нужно выбрать способ хранения типа работы в Frappe:

```text
A. Work Item
   └── work_type: Select

B. Work Type
   └── Work Item
       └── work_type: Link → Work Type
```

Проверяем, где должен жить набор типов работы:

- в metadata `Work Item`;
- или как отдельные данные `Work Type`.

Дополнительно проверяем разделение технического идентификатора `name` и пользовательского названия `title`.

Контрольная версия: **Frappe Framework v16.33.0**.

## Стенд

Нужен рабочий Frappe Bench, браузер с доступом в Desk и отдельный App/Site.

```text
App  : work_management_lab
Site : work-management.localhost
```

Проверить версию:

```bash
bench version
```

Создать App и Site, если их ещё нет:

```bash
bench new-app work_management_lab
bench new-site work-management.localhost
bench --site work-management.localhost install-app work_management_lab
```

Включить Developer Mode:

```bash
bench set-config -g developer_mode true
bench --site work-management.localhost clear-cache
```

Открыть Site и войти в Desk как `Administrator`.

Перед началом проверить состояние App:

```bash
git -C apps/work_management_lab status --short
```

Изменения этого эксперимента не должны смешиваться с другими изменениями App.

## Общие данные

В обоих вариантах используются одинаковые типы и работы.

Типы:

| Код | Название |
| --- | --- |
| `TASK` | Задача |
| `CHECK` | Проверка |
| `REQUEST` | Запрос |

Работы:

| Название | Тип |
| --- | --- |
| Подготовить недельный отчёт | `TASK` |
| Проверить исходные данные | `CHECK` |
| Запросить исходные документы | `REQUEST` |

`REQUEST` добавляется позже — это часть проверки.

Для Work Item используется:

```text
Autoname    : WORK-.#####
Title Field : title
```

---

# A. Тип как Select

## A1. Создать DocType

В Desk создать Standard DocType `Work Item Select` в module приложения `work_management_lab`.

Поля:

| Label | Fieldname | Type | Mandatory | Options |
| --- | --- | --- | --- | --- |
| Title | `title` | Data | yes | — |
| Work Type | `work_type` | Select | yes | `TASK` / `CHECK` |

Настройки:

```text
Autoname    : WORK-.#####
Title Field : title
```

Сохранить DocType.

Проверить Git:

```bash
git -C apps/work_management_lab status --short
```

Записать путь к JSON DocType и убедиться, что Options поля `work_type` содержат `TASK` и `CHECK`.

## A2. Создать две работы

Создать:

```text
Подготовить недельный отчёт → TASK
Проверить исходные данные   → CHECK
```

Записать фактические `name` обеих записей.

## A3. Проверить `name` и `title`

У первой работы изменить `title`:

```text
Подготовить недельный отчёт
→
Подготовить отчёт за неделю
```

Сохранить и перезагрузить Document.

Записать:

| Проверка | Значение |
| --- | --- |
| `name` до изменения | |
| `name` после изменения | |
| `title` после изменения | |

## A4. Добавить новый тип

В Options поля `work_type` добавить:

```text
REQUEST
```

Сохранить DocType и выполнить:

```bash
git -C apps/work_management_lab diff
```

Записать:

- какой файл изменился;
- где появилось `REQUEST`;
- потребовался ли отдельный Document для нового типа.

После этого создать:

```text
Запросить исходные документы → REQUEST
```

## A5. Удалить используемое значение из Options

Временно удалить `CHECK` из Options, не меняя существующую работу:

```text
Проверить исходные данные → CHECK
```

После reload проверить:

1. открывается ли Document;
2. что отображается в `work_type`;
3. можно ли сохранить Document без изменения `work_type`;
4. если возникает ошибка — записать её текст;
5. можно ли выбрать `CHECK` в новой записи.

После проверки вернуть `CHECK` в Options.

### Результат A

| Проверка | Наблюдение |
| --- | --- |
| Где хранится набор типов | |
| Что изменилось в Git при добавлении `REQUEST` | |
| Нужен ли отдельный Document для нового типа | |
| Что произошло с сохранённым `CHECK` после удаления из Options | |
| Изменился ли `name` при смене `title` | |

---

# B. Тип как Link на Work Type

## B1. Создать Work Type

В Desk создать Standard DocType `Work Type` в module приложения `work_management_lab`.

Поля:

| Label | Fieldname | Type | Mandatory | Дополнительно |
| --- | --- | --- | --- | --- |
| Code | `code` | Data | yes | Unique |
| Title | `title` | Data | yes | — |

Настройки:

```text
Autoname                  : field:code
Title Field               : title
Show Title in Link Fields : yes
```

## B2. Создать Work Item

Создать Standard DocType `Work Item Link`.

Поля:

| Label | Fieldname | Type | Mandatory | Options |
| --- | --- | --- | --- | --- |
| Title | `title` | Data | yes | — |
| Work Type | `work_type` | Link | yes | `Work Type` |

Настройки:

```text
Autoname    : WORK-.#####
Title Field : title
```

После сохранения обоих DocTypes проверить:

```bash
git -C apps/work_management_lab status --short
```

## B3. Создать два Work Type

Создать обычные записи:

```text
code=TASK   title=Задача
code=CHECK  title=Проверка
```

После создания снова выполнить:

```bash
git -C apps/work_management_lab status --short
```

Записать, изменились ли файлы App от создания этих записей.

## B4. Создать две работы

Создать:

```text
Подготовить недельный отчёт → TASK
Проверить исходные данные   → CHECK
```

Записать `name` обеих работ.

## B5. Изменить название типа

У `Work Type = TASK` изменить:

```text
Задача
→
Работа
```

Сохранить запись и перезагрузить Work Item, который ссылается на `TASK`.

Записать:

| Проверка | Значение |
| --- | --- |
| `name` Work Type | |
| значение `work_type` у Work Item | |
| что показывает Link field | |

## B6. Добавить новый тип

Создать обычный `Work Type`:

```text
code=REQUEST
 title=Запрос
```

Проверить:

```bash
git -C apps/work_management_lab status --short
```

После этого создать:

```text
Запросить исходные документы → REQUEST
```

Записать, потребовалось ли менять metadata `Work Item Link`.

## B7. Попытаться удалить используемый Work Type

Пока существует Work Item со ссылкой на `TASK`, попытаться удалить `Work Type = TASK` обычной командой Delete в Desk.

Не использовать `force`, raw SQL или другие обходы.

Записать фактический результат и текст сообщения Frappe.

### Результат B

| Проверка | Наблюдение |
| --- | --- |
| Где хранится набор типов | |
| Изменился ли Git после создания `Work Type` records | |
| Нужно ли менять metadata для добавления `REQUEST` | |
| Можно ли менять title типа без смены его `name` | |
| Что произошло при удалении используемого типа | |

---

# Сравнение

После выполнения обоих вариантов заполнить итоговую таблицу.

| Вопрос | Select | Link → Work Type |
| --- | --- | --- |
| Где хранится набор типов | | |
| Требуется ли изменение metadata для нового типа | | |
| Есть ли у типа собственный `name` | | |
| Можно ли отдельно менять отображаемое название типа | | |
| Что происходит при удалении/исключении используемого типа | | |
| Что меняется в Git | | |

## Вывод

Выбрать `Select`, если тип работы по результатам проверки является частью схемы приложения: набор небольшой, стабильный и изменяется вместе с metadata.

Выбрать `Link → Work Type`, если тип работы должен существовать как самостоятельные данные: иметь собственный идентификатор, отображаемое название и изменяться без изменения metadata `Work Item`.

Итоговая модель фиксируется только после заполнения таблиц фактическими наблюдениями.

## Источники Frappe

- https://docs.frappe.io/framework/user/en/basics/doctypes
- https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes
- https://docs.frappe.io/framework/user/en/basics/doctypes/naming
- https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype
