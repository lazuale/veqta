# Lab A. Child Table

Lab A — отдельная лаборатория по вложенным строкам документа.

Она **не расширяет постоянное ядро приложения**.

Временный эксперимент:

```text
Service Request
    │
    └── Work Logs
          ├── Description
          ├── Hours
          └── Cost
```

После лаборатории `Work Log` и поле `Work Logs` удаляются штатно, чтобы итоговая модель курса снова состояла только из:

```text
Facility Location
Equipment
Service Request
```

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Что изучаем

В лаборатории нужны только штатные механизмы:

```text
Child DocType
Table field
Editable Grid
строки внутри parent Document
idx
parent / parentfield / parenttype
metadata / working data / Git
```

Собственный Python или JavaScript не пишем.

---

# 2. Что такое Child Table

Обычный DocType представляет самостоятельный Document:

```text
Equipment
Service Request
```

Child DocType предназначен для строк, которые существуют **в составе другого Document**.

В нашем примере:

```text
Service Request SR-00042

Work Logs
┌──────────────────────┬───────┬────────┐
│ Description          │ Hours │ Cost   │
├──────────────────────┼───────┼────────┤
│ Inspect equipment    │ 0.5   │ 0      │
│ Replace bearing      │ 2.0   │ 120.00 │
│ Test after repair    │ 0.5   │ 0      │
└──────────────────────┴───────┴────────┘
```

Строка `Replace bearing` не является отдельной заявкой и не должна жить как самостоятельный рабочий объект.

---

# 3. Проверить стенд

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
working tree clean
```

В приложении должны существовать только основные предметные DocType:

```text
Facility Location
Equipment
Service Request
```

---

# 4. Создать временный Child DocType

Войти под:

```text
Administrator
```

Developer Mode должен быть включён.

Через Awesomebar открыть:

```text
DocType
```

Создать новый Standard DocType:

```text
Name:       Work Log
Module:     Facility Operations
Is Child Table: Yes
```

Если интерфейс показывает `Editable Grid`, оставить его включённым.

Не включать:

```text
Is Single
Is Tree
Is Submittable
Allow Import
```

Для Child DocType отдельная permission matrix не нужна.

---

# 5. Добавить поля Work Log

Создать три поля:

| Label | Fieldname | Type | Mandatory | In List View |
|---|---|---|---:|---:|
| Description | `description` | Data | Yes | Yes |
| Hours | `hours` | Float | Yes | Yes |
| Cost | `cost` | Currency | No | Yes |

Для `Hours` можно задать:

```text
Precision = 2
```

Для `Cost` отдельную валютную модель не создаём.

Это просто поле Currency внутри строки лаборатории.

Сохранить DocType.

---

# 6. Посмотреть, что Frappe сделал с Child DocType

После сохранения открыть `Work Log` ещё раз.

Проверить:

```text
Is Child Table = Yes
```

У него нет самостоятельной пользовательской модели permissions как у обычного бизнес-DocType.

В исходниках Frappe v16.32.0 при `istable = 1`:

```text
Allow Import → выключается
Permissions  → очищаются
```

То есть Child DocType не проектируется как самостоятельный реестр.

---

# 7. Добавить Table в Service Request

Открыть Standard DocType:

```text
Service Request
```

В нижней части формы добавить Section Break:

```text
Work
```

После него добавить поле:

```text
Label:     Work Logs
Fieldname: work_logs
Field Type: Table
Options:   Work Log
```

Сохранить `Service Request`.

Связь теперь выглядит так:

```text
Service Request.work_logs
          │
          └── Table → Work Log
```

---

# 8. Не путать Table и Link

Сравнить два механизма.

## Link

```text
Service Request.location
→ ссылка на самостоятельный Facility Location
```

`Facility Location` существует отдельно и может использоваться многими Documents.

## Table

```text
Service Request.work_logs
→ набор вложенных Work Log rows
```

Эти строки принадлежат конкретному `Service Request`.

Главное:

```text
Link
= ссылка на другой самостоятельный Document

Table
= дочерние строки текущего Document
```

---

# 9. Создать тестовую заявку

Под Administrator создать отдельную заявку только для лаборатории:

```text
Subject:     Child table lab
Location:    Room 101
Description: Temporary document for Lab A
Priority:    Medium
Target Date: <любая будущая дата>
```

Сохранить.

Не использовать рабочую заявку, которую жалко испортить.

---

# 10. Добавить первую строку

В секции:

```text
Work Logs
```

добавить строку:

```text
Description: Inspect equipment
Hours:       0.50
Cost:        0
```

Сохранить `Service Request`.

Обратить внимание:

```text
Save выполняется у Service Request
```

Мы не открываем отдельную форму `Work Log` и не нажимаем там отдельный Save как для самостоятельного рабочего документа.

---

# 11. Добавить несколько строк

Добавить ещё две строки:

```text
Description: Replace bearing
Hours:       2.00
Cost:        120
```

```text
Description: Test after repair
Hours:       0.50
Cost:        0
```

Сохранить.

Итог:

```text
3 Work Log rows
1 Service Request
```

Не три самостоятельных Service Request и не три самостоятельных бизнес-объекта.

---

# 12. Проверить Editable Grid

В таблице изменить прямо в строке:

```text
Replace bearing
Hours: 2.00 → 2.50
```

Сохранить parent Document.

Затем открыть строку через row form/grid-row editor и изменить:

```text
Cost: 120 → 135
```

Сохранить.

Нужно увидеть два способа работы:

```text
inline grid
row form
```

Оба изменяют одну и ту же child row.

---

# 13. Проверить порядок строк

Переставить строки, если фактический Grid v16.32.0 позволяет это штатным drag/reorder.

Например:

```text
1. Inspect equipment
2. Test after repair
3. Replace bearing
```

Сохранить и обновить страницу.

Порядок должен сохраниться.

Frappe хранит позицию child row через системное поле:

```text
idx
```

Если на конкретной форме drag/reorder недоступен, не искать обходной скрипт — достаточно увидеть `idx` как часть штатной модели Child Table.

---

# 14. Удалить одну строку

Удалить:

```text
Test after repair
```

из Grid.

Сохранить `Service Request`.

После обновления страницы строка не должна возвращаться.

Важно:

```text
удаление child row
≠ удаление parent Service Request
```

---

# 15. Проверить Mandatory внутри строки

Добавить новую пустую строку и попробовать сохранить при пустом:

```text
Description
```

или:

```text
Hours
```

Сохранение корректной строки должно потребовать обязательные значения.

После проверки заполнить строку нормально либо удалить её.

Не отключать Mandatory ради прохождения теста.

---

# 16. Понять техническую связь строк

Для Child Table Frappe хранит системную привязку:

```text
parent
parenttype
parentfield
idx
```

В нашем примере смысл такой:

```text
parent
= SR-00042

parenttype
= Service Request

parentfield
= work_logs

idx
= положение строки в таблице
```

Эти поля не нужно добавлять вручную в `Work Log`.

MariaDB schema Frappe v16.32.0 добавляет `parent`, `parentfield` и `parenttype` автоматически для `istable` DocType; `idx` входит в системные поля документа.

---

# 17. Посмотреть metadata в Git

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Ожидаются изменения примерно двух типов:

```text
новый Standard DocType Work Log
изменённый Standard DocType Service Request
```

Найти файлы:

```bash
find facility_ops/facility_operations \
  -type f \
  | sort \
  | grep -E 'work_log|service_request'
```

Посмотреть diff:

```bash
git diff -- \
  facility_ops/facility_operations/doctype/service_request/service_request.json
```

В `Service Request` найти поле примерно такого смысла:

```text
fieldtype = Table
fieldname = work_logs
options   = Work Log
```

В JSON `Work Log` найти:

```text
istable = 1
```

---

# 18. Что не попало в Git

Строки:

```text
Inspect equipment
Replace bearing
```

не должны появиться в source app.

Они являются рабочими данными конкретного site.

Получаем:

```text
Work Log DocType definition
→ metadata
→ Git

Service Request.work_logs field
→ metadata
→ Git

конкретные Work Log rows
→ database site
→ не Git
```

---

# 19. Зафиксировать лабораторное состояние

Перед очисткой полезно сделать отдельный commit, чтобы эксперимент остался в истории Git.

```bash
git add .
git diff --cached
git commit -m "Add temporary work log child table lab"
git status
```

Ожидается:

```text
working tree clean
```

Этот commit фиксирует изученный механизм, но не означает, что `Work Log` обязан остаться в конечной модели приложения.

---

# 20. Почему Work Log не оставляем в ядре

В базовой модели курса Service Request уже решает поставленную учебную задачу без детализации работ по строкам.

`Work Log` был создан только чтобы понять Child Table.

Правило проектирования:

```text
механизм Frappe изучили
≠
обязаны навсегда добавить сущность в продукт
```

Поэтому лабораторию завершаем очисткой.

---

# 21. Очистить тестовые child rows

Открыть тестовую заявку:

```text
Child table lab
```

Удалить из неё все строки `Work Logs`.

Сохранить.

После этого удалить саму временную заявку, если она больше не нужна.

Не трогать другие учебные Service Request.

---

# 22. Удалить Table field штатно

Открыть Standard DocType:

```text
Service Request
```

Удалить поле:

```text
Work Logs
fieldname: work_logs
```

Если Section Break `Work` после этого больше ничего не содержит, удалить и его.

Сохранить DocType.

Не удалять JSON вручную из файловой системы.

---

# 23. Удалить временный Child DocType

Через список DocType открыть:

```text
Work Log
```

Удалить его штатным действием Delete.

Если Frappe сообщает о существующей ссылке на Child DocType, значит поле `Service Request.work_logs` удалено не полностью — сначала исправить metadata parent DocType.

Не использовать `rm -rf` как способ удаления DocType.

---

# 24. Проверить возврат модели

После очистки в приложении снова должно быть только три предметных DocType:

```text
Facility Location
Equipment
Service Request
```

В `Service Request` больше нет:

```text
work_logs
```

В списке DocType больше нет:

```text
Work Log
```

---

# 25. Проверить Git после очистки

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

Git должен показать обратные изменения относительно лабораторного commit:

```text
удаление Work Log source
возврат Service Request metadata
```

Проверить diff и выполнить:

```bash
git add .
git diff --cached
git commit -m "Remove temporary work log child table lab"
git status
```

Ожидается:

```text
working tree clean
```

Итоговое состояние app снова соответствует основной архитектуре, а Git history сохраняет лабораторный эксперимент.

---

# 26. Самостоятельная практика

Без готового пошагового описания временно создать второй Child DocType:

```text
Checklist Item
```

Поля:

```text
Item        Data
Completed   Check
```

Добавить его как Table в тестовый Service Request, создать 3 строки и проверить Grid.

После проверки полностью удалить эксперимент штатно.

Никаких новых постоянных сущностей после упражнения остаться не должно.

---

# 27. Приёмка Lab A

Лаборатория принята, если ученик может объяснить и показать:

```text
Child DocType
Table field
Editable Grid
parent
parenttype
parentfield
idx
```

и ответить на вопросы.

## Чем Table отличается от Link?

```text
Link → другой самостоятельный Document
Table → дочерние строки текущего Document
```

## Имеет ли Child DocType собственную обычную permission matrix?

```text
Нет.
Доступ к строкам определяется контекстом parent Document.
```

## Нужно ли вручную создавать parent / parenttype / parentfield?

```text
Нет.
Это системная структура Frappe для Child Table.
```

## Попадают ли конкретные строки Work Log в Git?

```text
Нет.
В Git попадает metadata, а строки остаются working data site.
```

## Остался ли Work Log в итоговой архитектуре?

```text
Нет.
Лаборатория должна закончиться возвратом к трём core DocType.
```

---

# Результат

Ученик на практике увидел:

```text
самостоятельный Document
        ≠
вложенная строка Child Table
```

и умеет использовать Child DocType только там, где данные действительно принадлежат одному parent Document, а не создавать отдельные сущности ради демонстрации механизма Frappe.
