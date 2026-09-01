# Lab F. Специальные Field Types и представления

Lab F завершает набор лабораторий практикума.

Задача лаборатории — руками проверить редкие штатные возможности Frappe, которым не нужно постоянное место в основном `facility_ops`.

Постоянное ядро приложения не меняем:

```text
Facility Location
Equipment
Service Request
```

Для эксперимента создадим временные Standard DocType:

```text
Lab Feature Settings   — Single DocType
Lab Equipment Link     — Child DocType
Lab Feature Record     — обычный DocType-полигон
```

После лаборатории они удаляются штатно.

Для Calendar и Gantt используем встроенный `Event` Frappe, а не пишем свой calendar JavaScript.

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Что изучаем

В лаборатории нужны только штатные механизмы Frappe:

```text
Single DocType
Dynamic Link
Table MultiSelect
Percent
Time
Duration
Barcode
Signature
Geolocation
Attachment Gallery
Markdown Editor
Mask / Data Masking
Calendar
Gantt
Event
```

Главная граница лаборатории:

```text
редкая возможность платформы
≠
обязательная сущность бизнес-модели
```

Не добавляем эти поля в `Equipment` или `Service Request` только ради покрытия матрицы.

---

# 2. Проверить стенд

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

Developer Mode должен быть включён.

---

# 3. Сначала понять структуру лаборатории

Используем три временных Standard DocType.

## Lab Feature Settings

Нужен только для изучения:

```text
Single DocType
```

## Lab Equipment Link

Нужен только как служебный Child DocType для:

```text
Table MultiSelect
```

## Lab Feature Record

На нём соберём остальные специальные Field Types.

Это полигон, а не новая предметная модель.

---

# 4. Создать Single DocType Lab Feature Settings

Через Awesomebar открыть:

```text
DocType
→ New
```

Создать:

```text
Name:        Lab Feature Settings
Module:      Facility Operations
Is Single:   Yes
Custom:      No
```

Добавить поля:

| Label | Fieldname | Type |
|---|---|---|
| Lab Enabled | `lab_enabled` | Check |
| Default Label | `default_label` | Data |
| Default Duration | `default_duration` | Duration |

Сохранить.

---

# 5. Открыть Single DocType

Через Awesomebar открыть:

```text
Lab Feature Settings
```

У Single DocType нет обычного списка независимых Documents.

Заполнить:

```text
Lab Enabled:       Yes
Default Label:     Feature laboratory
Default Duration:  30 minutes
```

Сохранить.

Закрыть форму и открыть её снова.

Значения должны сохраниться.

---

# 6. Понять Single DocType

Обычный DocType:

```text
Equipment
→ EQ-0001
→ EQ-0002
→ EQ-0003
```

Single DocType:

```text
Lab Feature Settings
→ одна запись настроек
```

Для Single не создаём несколько Documents с разными `name`.

Frappe хранит значения Single через механизм `tabSingles`, а не как обычный набор строк `Lab Feature Settings`.

Поэтому Single подходит для:

```text
Settings
глобальных параметров site/app
одного набора настроек
```

а не для реестров и журналов.

---

# 7. Проверить ограничения Single

Вернуться в DocType `Lab Feature Settings`.

Обратить внимание:

```text
Allow Import = недоступен / выключен
Is Submittable = выключен
Is Child Table = выключен
```

Frappe сам ограничивает эти режимы для Single.

Не пытаться превращать Single в реестр.

---

# 8. Создать Child DocType для Table MultiSelect

Создать второй Standard DocType:

```text
Name:           Lab Equipment Link
Module:         Facility Operations
Is Child Table: Yes
Custom:         No
```

Добавить ровно одно рабочее поле:

| Label | Fieldname | Type | Options |
|---|---|---|---|
| Equipment | `equipment` | Link | Equipment |

Сохранить.

Отдельные permissions для Child DocType не настраиваем.

---

# 9. Почему Table MultiSelect требует Child DocType

`Table MultiSelect` визуально похож на набор выбранных значений:

```text
[EQ-0001] [EQ-0004] [EQ-0010]
```

Но внутри Frappe это не строка с перечислением ID.

Механизм использует Child Table.

Для нашего поля структура будет:

```text
Lab Feature Record
        │
        └── equipment_selection
                │
                ├── Lab Equipment Link → EQ-0001
                ├── Lab Equipment Link → EQ-0004
                └── Lab Equipment Link → EQ-0010
```

В `v16.32.0` Table MultiSelect требует, чтобы указанный Child DocType содержал хотя бы одно поле типа `Link`.

Именно таким полем является:

```text
Lab Equipment Link.equipment
```

---

# 10. Создать Lab Feature Record

Создать третий Standard DocType:

```text
Name:    Lab Feature Record
Module:  Facility Operations
Custom:  No
```

Naming:

```text
Naming Rule: Expression
Auto Name:   LABF-.####
```

Title Field:

```text
label
```

Track Changes:

```text
Yes
```

---

# 11. Добавить специальные поля

Добавить поля в `Lab Feature Record`:

| Label | Fieldname | Type | Options / настройка |
|---|---|---|---|
| Label | `label` | Data | Mandatory |
| Completion | `completion` | Percent | — |
| Visit Time | `visit_time` | Time | — |
| Expected Duration | `expected_duration` | Duration | — |
| Barcode | `barcode` | Barcode | — |
| Signature | `signature` | Signature | — |
| Location | `location` | Geolocation | — |
| Attachments Gallery | `attachments_gallery` | Attachment Gallery | — |
| Notes | `notes` | Markdown Editor | — |
| Sensitive Note | `sensitive_note` | Data | Mask = Yes |
| Reference Type | `reference_type` | Select | Equipment\nService Request |
| Reference Document | `reference_document` | Dynamic Link | `reference_type` |
| Equipment Selection | `equipment_selection` | Table MultiSelect | Lab Equipment Link |

Разложить форму по Section Break / Column Break так, чтобы она оставалась читаемой.

Не добавлять Python или JavaScript.

---

# 12. Настроить permissions полигона

В permissions `Lab Feature Record` добавить учебные роли.

Минимально:

### Facility Technician

```text
Read   = Yes
Write  = Yes
Create = Yes
Delete = No
Mask   = No
```

### Facility Supervisor

```text
Read   = Yes
Write  = Yes
Create = Yes
Delete = Yes
Mask   = Yes
```

Если permission grid показывает дополнительные стандартные действия, они для этой лаборатории не нужны.

Смысл теста:

```text
оба пользователя читают Document
но только роль с Mask permission видит реальное masked value
```

---

# 13. Создать первый Lab Feature Record

Войти как Supervisor или Administrator.

Создать:

```text
Label:              Feature demo 1
Completion:         65
Visit Time:         14:30
Expected Duration:  1 hour 30 minutes
Sensitive Note:     INTERNAL-12345
Reference Type:     Equipment
Reference Document: <существующее Equipment>
```

Остальные поля заполним последовательно.

Сохранить.

Получится имя примерно:

```text
LABF-0001
```

---

# 14. Percent

Открыть поле:

```text
Completion
```

Проверить значение:

```text
65
```

Поле `Percent` семантически предназначено для процентных величин.

Не создавать ради процента:

```text
Data
Select 0..100
отдельный справочник
```

Используем штатный тип, когда смысл действительно процентный.

---

# 15. Time

Поле:

```text
Visit Time
```

заполнить:

```text
14:30
```

`Time` хранит время суток.

Не путать:

```text
Date      = календарная дата
Time      = время суток
Datetime  = дата + время
Duration  = длительность
```

---

# 16. Duration

Открыть:

```text
Expected Duration
```

Через штатный picker выставить:

```text
Hours:   1
Minutes: 30
```

Сохранить.

После повторного открытия Frappe должен показать ту же длительность.

Внутри `Duration` работает как количество секунд, а UI переводит его в дни / часы / минуты / секунды.

То есть:

```text
Duration
≠
Time
```

`01:30` как время суток и `1 hour 30 minutes` как длительность — разные вещи.

---

# 17. Barcode

В поле:

```text
Barcode
```

ввести:

```text
LABF-2026-0001
```

После ввода должен появиться визуальный штрихкод.

В `v16.32.0` Barcode control генерирует SVG штатной библиотекой Frappe.

Никакого собственного barcode renderer не нужен.

Если ввести значение, которое выбранный barcode format не может отрисовать, control покажет ошибку.

Для базовой проверки дополнительные JSON options Barcode не задаём.

---

# 18. Signature

В поле:

```text
Signature
```

мышью нарисовать тестовую подпись.

Сохранить документ.

Обновить страницу.

Подпись должна восстановиться.

Затем проверить штатную кнопку reset и снова поставить подпись.

Frappe хранит результат Signature как данные изображения, которые control умеет снова загрузить в signature pad.

Не путать этот механизм с квалифицированной электронной подписью.

Здесь изучается только визуальное поле `Signature` Frappe.

---

# 19. Geolocation

В поле:

```text
Location
```

должна появиться карта.

Поставить один marker в произвольной точке.

Сохранить.

Обновить страницу.

Marker должен восстановиться.

Frappe хранит значение Geolocation как GeoJSON и отображает его через встроенную карту.

При желании проверить line / polygon, но для приёмки достаточно одной точки.

---

# 20. Attachment Gallery

Сначала документ должен быть сохранён.

В блоке:

```text
Attachments Gallery
```

добавить два файла:

```text
одну картинку
один обычный файл, например PDF или TXT
```

Проверить:

- картинка отображается thumbnail;
- обычный файл отображается как файл;
- файл можно открыть;
- при наличии write permission файл можно удалить.

Главное:

```text
Attachment Gallery
не создаёт отдельное хранилище файлов
```

Она показывает обычные `File`, прикреплённые к текущему Document.

То же вложение должно быть видно и через стандартный механизм attachments формы.

---

# 21. Markdown Editor

В поле:

```text
Notes
```

ввести:

```markdown
## Проверка

- первый пункт
- второй пункт

**важное примечание**
```

Сохранить.

Проверить работу штатного Markdown Editor.

Не использовать HTML/Jinja ради форматированного пользовательского текста, если Markdown достаточно.

---

# 22. Dynamic Link

У нас есть пара:

```text
Reference Type
Reference Document
```

Сначала установить:

```text
Reference Type = Equipment
```

В `Reference Document` выбрать существующий Equipment.

Сохранить.

Теперь очистить `Reference Document` и изменить:

```text
Reference Type = Service Request
```

В том же поле `Reference Document` теперь выбрать существующий Service Request.

Сохранить.

Главная идея:

```text
обычный Link
→ заранее знает один DocType

Dynamic Link
→ целевой DocType берётся из другого поля
```

У `Reference Document`:

```text
Options = reference_type
```

то есть `options` указывает **не на DocType**, а на fieldname, содержащий имя DocType.

---

# 23. Когда Dynamic Link уместен

Dynamic Link полезен для универсальной ссылки вида:

```text
Reference Type = Equipment
Reference Name = EQ-0001
```

или:

```text
Reference Type = Service Request
Reference Name = SR-00012
```

Но если поле всегда должно ссылаться только на Equipment, обычный:

```text
Link → Equipment
```

лучше и проще.

Не использовать Dynamic Link ради «гибкости на всякий случай».

---

# 24. Table MultiSelect

В поле:

```text
Equipment Selection
```

выбрать минимум три Equipment.

В форме должны появиться pills примерно вида:

```text
[EQ-0001] [EQ-0004] [EQ-0006]
```

Сохранить.

Обновить страницу.

Выбор должен сохраниться.

Удалить один элемент через крестик и сохранить снова.

---

# 25. Проверить duplicate в Table MultiSelect

Попробовать повторно добавить уже выбранный Equipment.

Frappe не должен оставлять второй одинаковый элемент в текущем Table MultiSelect.

Это поведение control, а не наш скрипт.

После проверки оставить три разных Equipment.

---

# 26. Посмотреть, что хранит Table MultiSelect

Открыть форму `Lab Feature Record` и мысленно сравнить:

```text
UI:
[EQ-0001] [EQ-0004] [EQ-0006]
```

с моделью:

```text
Lab Feature Record LABF-0001
        │
        └── equipment_selection
             ├── child row → EQ-0001
             ├── child row → EQ-0004
             └── child row → EQ-0006
```

Это Child Table с компактным UI, а не отдельный строковый формат хранения.

---

# 27. Проверить Mask / Data Masking

У Supervisor в документе должно быть реальное значение:

```text
Sensitive Note = INTERNAL-12345
```

Выйти и войти как пользователь с ролью:

```text
Facility Technician
```

Открыть тот же `LABF-0001`.

Поскольку поле имеет:

```text
Mask = Yes
```

а роль Technician не имеет permission:

```text
Mask
```

значение должно отображаться замаскированным, например:

```text
XXXXXXXX
```

При этом остальные обычные поля остаются читаемыми.

---

# 28. Проверить Mask permission

Вернуться под Supervisor.

У Supervisor в permissions `Lab Feature Record` установлено:

```text
Mask = Yes
```

Поэтому он должен видеть реальное:

```text
INTERNAL-12345
```

Administrator также видит исходное значение.

Главная модель:

```text
Read permission
= можно читать Document

Mask field flag
= поле считается чувствительным

Mask permission
= можно видеть его реальное значение
```

Это отдельный механизм от Permission Level.

---

# 29. Не путать Mask и Permission Level

В L5 уже изучен:

```text
Permission Level
```

Он решает вопрос:

```text
может ли роль читать/писать поле этого уровня
```

Mask решает другой вопрос:

```text
поле доступно в Document,
но чувствительное значение скрывается без отдельного Mask permission
```

То есть:

```text
Permission Level
≠
Mask
```

---

# 30. Проверить Git временного полигона

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Standard DocType лаборатории должны создать source metadata в app:

```text
Lab Feature Settings
Lab Equipment Link
Lab Feature Record
```

Рабочий Document:

```text
LABF-0001
```

его подпись, координаты, selected Equipment и attachments как рабочие данные сами по себе в Git не входят.

---

# 31. Зафиксировать временный эксперимент

Проверить diff:

```bash
git diff
```

Затем:

```bash
git add facility_ops/facility_operations/doctype

git diff --cached

git commit -m "Experiment with special Frappe fields"
```

Commit нужен для учебной истории.

Эти DocType не обязаны остаться в финальной модели.

---

# 32. Calendar и Gantt: важная граница v16.32.0

В старой формулировке курса можно было ошибочно решить, что для нового DocType достаточно включить:

```text
Is Calendar and Gantt
```

Для точного `Frappe v16.32.0` это неверная модель.

В этой версии переключатели Calendar/Gantt в List View появляются, когда для DocType загружена конфигурация:

```text
frappe.views.calendar["DocType"]
```

Для своего DocType такая конфигурация означает calendar JavaScript.

В базовом курсе собственный JS не пишем.

Поэтому Calendar/Gantt изучаем на штатном `Event`, где Frappe уже поставляет готовую конфигурацию.

---

# 33. Открыть штатный Event

Через Awesomebar открыть:

```text
Event
```

Это системный DocType Frappe.

Для лаборатории создать три тестовых Event, например:

```text
Lab F — Inspection A
Lab F — Inspection B
Lab F — Inspection C
```

Задать им разные:

```text
Starts On
Ends On
```

в пределах одной недели.

Не использовать реальные рабочие встречи.

---

# 34. Calendar View

Открыть список `Event`.

Через переключатель представления выбрать:

```text
Calendar
```

Найти три события Lab F.

Проверить:

```text
subject  → заголовок события
starts_on → начало
ends_on   → конец
all_day   → признак all-day
```

Именно эти поля штатная конфигурация Event связывает с Calendar.

---

# 35. Изменить Event через Calendar

Выбрать одно тестовое событие.

Если интерфейс стенда позволяет drag/reschedule, перенести его на другую дату или время.

Затем открыть Event Form и проверить:

```text
Starts On / Ends On
```

Если drag недоступен в конкретном режиме Calendar, изменить событие через форму и убедиться, что Calendar показывает новое положение.

Цель — увидеть, что Calendar является представлением тех же Documents.

---

# 36. Gantt View

Из списка Event переключиться в:

```text
Gantt
```

Должны появиться те же события как интервалы времени.

Проверить минимум:

```text
Lab F — Inspection A
Lab F — Inspection B
Lab F — Inspection C
```

Calendar и Gantt не создают копии Event.

Это разные представления тех же записей.

---

# 37. Почему не создаём свой Calendar JS в Lab F

Для своего `Lab Schedule Item` можно было бы написать конфигурацию примерно такого класса:

```text
start field
end field
title field
```

Но это уже собственный JavaScript source приложения.

В базовой программе действует граница:

```text
штатная конфигурация без собственного бизнес-кода
```

Поэтому сейчас достаточно понять:

```text
Calendar/Gantt engine есть в Frappe
но custom mapping своего DocType — следующий уровень
```

Не создавать `Lab Schedule Item` только ради этой демонстрации.

---

# 38. Удалить тестовые Event

После проверки Calendar/Gantt удалить только созданные лабораторные Event:

```text
Lab F — Inspection A
Lab F — Inspection B
Lab F — Inspection C
```

Не удалять системный DocType `Event`.

Event Documents — working data текущего site и к `facility_ops` не относятся.

---

# 39. Очистить Lab Feature Record data

Вернуться под Administrator.

Удалить созданные:

```text
LABF-....
```

Если к ним были прикреплены файлы, убедиться, что лабораторные attachments больше не нужны.

Не использовать эти записи как постоянные рабочие данные.

---

# 40. Удалить временные Standard DocType

Через `DocType` штатно удалить в таком порядке:

```text
1. Lab Feature Record
2. Lab Equipment Link
3. Lab Feature Settings
```

Почему сначала parent:

```text
Lab Feature Record
→ ссылается через Table MultiSelect на Lab Equipment Link
```

После удаления parent можно удалить служебный child.

Не удалять generated файлы вручную до штатного удаления DocType.

---

# 41. Проверить Git после удаления

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

После ранее сделанного experiment commit Git должен показать удаление файлов временных DocType.

Проверить, что не затронуты:

```text
Facility Location
Equipment
Service Request
```

---

# 42. Commit очистки

```bash
git add -A

git diff --cached

git commit -m "Remove Lab F temporary doctypes"

git status
```

Ожидается:

```text
working tree clean
```

Git history показывает:

```text
baseline
→ special fields experiment
→ clean rollback
```

---

# 43. Что должно остаться после Lab F

В app нет:

```text
Lab Feature Settings
Lab Equipment Link
Lab Feature Record
```

На site нет лабораторных:

```text
LABF-...
Lab F — Inspection A/B/C
```

Постоянная бизнес-модель по-прежнему:

```text
Facility Location
Equipment
Service Request
```

---

# 44. Что должен уметь объяснить студент

После Lab F без подсказки объяснить:

```text
что такое Single DocType;
чем Single отличается от обычного DocType;
зачем Dynamic Link содержит поле с именем целевого DocType;
чем Dynamic Link отличается от обычного Link;
почему Table MultiSelect использует Child DocType;
почему Table MultiSelect требует Link field в child table;
чем Time отличается от Duration;
что делает Percent;
что делает Barcode;
что хранит Signature;
что хранит Geolocation;
что показывает Attachment Gallery;
когда уместен Markdown Editor;
чем Mask отличается от Permission Level;
как связаны Mask field и Mask permission;
что Calendar и Gantt являются views тех же Documents;
почему в v16.32.0 свой Calendar/Gantt mapping уже выходит за no-JS границу базового курса.
```

---

# 45. Финальная приёмка Lab F

Лаборатория пройдена, если выполнено всё:

```text
[ ] создан и проверен Single DocType Lab Feature Settings
[ ] подтверждено, что Single не является обычным реестром Documents
[ ] создан Child DocType Lab Equipment Link
[ ] создан временный Lab Feature Record
[ ] проверен Percent
[ ] проверен Time
[ ] проверен Duration и его отличие от Time
[ ] проверен Barcode
[ ] проверена Signature и reset
[ ] проверена Geolocation
[ ] проверена Attachment Gallery минимум с двумя файлами
[ ] проверен Markdown Editor
[ ] Dynamic Link переключён между Equipment и Service Request
[ ] Table MultiSelect содержит несколько Equipment
[ ] duplicate в Table MultiSelect не сохраняется как второй элемент
[ ] Technician видит masked Sensitive Note
[ ] Supervisor с Mask permission видит исходное значение
[ ] объяснена разница Mask и Permission Level
[ ] создано три временных Event
[ ] проверен Calendar
[ ] проверен Gantt
[ ] не написан собственный calendar JavaScript
[ ] лабораторные Event удалены
[ ] Lab Feature Record data удалены
[ ] все три временных DocType удалены штатно
[ ] Git содержит experiment commit и cleanup commit
[ ] working tree clean
[ ] постоянное ядро приложения осталось из трёх DocType
```

---

# 46. Итог лабораторий A–F

После всех лабораторий студент отдельно попробовал механизмы, которые не требовались ядру приложения:

```text
Lab A → Child Table
Lab B → DocStatus / Submit / Cancel / Amend
Lab C → Auto Repeat
Lab D → Customize Form / Custom Field / Property Setter
Lab E → Print / Letter Head / PDF
Lab F → специальные Field Types / Single / Dynamic Link / Table MultiSelect / Calendar / Gantt
```

При этом основное приложение не превратилось в каталог демонстрационных сущностей.

Это и есть цель лабораторий.