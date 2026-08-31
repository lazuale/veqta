# 38. Data Import / Export

В предыдущих главах мы научились получать данные из Frappe через:

```text
Report Builder
Query Report
Script Report
Dashboard Chart
Number Card
```

Теперь разберём обратную сторону работы с данными:

```text
как массово загрузить записи в Frappe
и
как массово выгрузить их обратно
```

Для этого во Framework есть два штатных инструмента:

```text
Data Import
Data Export
```

Проверено: **2026-08-31**.

---

## 1. Что такое Data Import простыми словами

`Data Import` берёт таблицу:

```text
CSV / XLS / XLSX
```

и превращает её строки в обычные Frappe Documents.

Например есть DocType:

```text
Request
```

с полями:

```text
subject
department
priority
status
```

В файле:

```text
Subject           | Department | Priority | Status
Printer broken    | Support    | High     | Open
New account       | IT         | Medium   | Open
Replace keyboard  | Support    | Low      | Closed
```

после импорта появляются обычные Documents:

```text
Request REQ-0001
Request REQ-0002
Request REQ-0003
```

Важно:

> Data Import не вставляет строки напрямую в SQL-таблицу.

В нормальном import-flow Frappe создаёт или загружает Document и проводит его через обычные `insert()` / `save()`.

Поэтому продолжают работать:

```text
валидации
mandatory fields
Link checks
controller lifecycle
permissions
naming
hooks
Version / Track Changes
```

в той мере, в какой они участвуют в обычном Document lifecycle.

---

## 2. Data Import — не ETL-система

Очень важно сразу провести границу.

Data Import хорош, когда данные уже **почти соответствуют модели Frappe**.

Например:

```text
CSV column       → Request field
Subject          → subject
Department       → department
Priority         → priority
```

Но если исходник требует:

```text
объединить 12 CSV
нормализовать ФИО
сопоставить справочники
устранить дубли
пересчитать единицы измерения
провести сложную сверку
загрузить данные из API
вести incremental sync
```

то это уже не просто Data Import.

Удобная граница:

```text
готовая таблица почти формы DocType
→ Data Import

данные сначала нужно серьёзно преобразовать
→ ETL / integration code / Data Migration / отдельный pipeline
```

---

## 3. Два режима импорта

В текущем v16 у `Data Import.import_type` два основных варианта:

```text
Insert New Records
Update Existing Records
```

Это принципиально разные операции.

### Insert New Records

Создаёт новые Documents.

```text
файл
→ new_doc
→ insert()
```

### Update Existing Records

Находит уже существующий Document и обновляет его.

```text
ID
→ get_doc(existing)
→ update(values)
→ save()
```

Нельзя воспринимать Update как «Insert, если записи ещё нет».

Для Update существующая запись должна быть однозначно найдена.

---

## 4. Самый безопасный способ начать — скачать шаблон

Не нужно угадывать названия колонок руками.

В `Data Import` сначала выбираем:

```text
Document Type = Request
Import Type    = Insert New Records
```

затем:

```text
Download Template
```

Текущий интерфейс v16 позволяет выбрать:

```text
File Type
- Excel
- CSV

Export Type
- All Records
- Filtered Records
- 5 Records
- Blank Template
```

Для нового импорта стандартный выбор — обычно:

```text
Blank Template
```

Для обновления удобно выгрузить уже существующие records и менять именно их.

---

## 5. Почему шаблон лучше самодельного Excel

Шаблон знает метаданные DocType.

Он помогает показать:

```text
ID
mandatory fields
типы полей
Link targets
Select options
Date format
Child Table columns
```

Например для поля:

```text
priority
fieldtype = Select
```

template metadata может подсказать допустимые значения.

Для:

```text
department
fieldtype = Link
options = Department
```

он показывает, что значение должно соответствовать существующему `Department`.

То есть шаблон — это не просто пустая таблица.

Это отражение metadata вашего DocType.

---

## 6. Выбирай только нужные поля

При скачивании шаблона необязательно брать весь DocType.

Для Insert можно выбрать, например:

```text
subject
department
priority
```

а не 60 колонок, из которых используются три.

Для Update это ещё важнее.

Если нужно массово поменять только:

```text
priority
```

логичнее выгрузить:

```text
ID
Priority
```

а не весь документ.

Чем меньше лишних колонок, тем меньше риск случайно затереть или изменить данные.

---

## 7. Mandatory fields

При Insert новый Document всё равно должен пройти обычную валидацию.

Если `subject` обязателен:

```text
subject.reqd = 1
```

то строка без Subject не превращается магически в корректный Document.

Импорт должен передать достаточный набор данных, чтобы Document можно было создать.

Поэтому в диалоге шаблона есть удобная команда:

```text
Select Mandatory
```

Она помогает быстро выбрать обязательные поля.

Но помни: обязательность может зависеть не только от `reqd = 1`.

Ваш controller или server logic тоже может содержать проверки.

---

## 8. `Allow Import` у DocType

Не каждый DocType должен разрешать массовый импорт.

У DocType есть свойство:

```text
Allow Import
```

Текущий backend v16 перед запуском Data Import проверяет его.

Если:

```text
Allow Import = 0
```

получим ошибку по смыслу:

```text
Data Import is not allowed for this DocType
```

То есть массовый импорт должен быть **явно разрешён моделью**.

---

## 9. Permission `Import`

Одного `Allow Import` недостаточно.

У пользователя также должно быть permission:

```text
Import
```

на целевой DocType.

Упрощённо:

```text
DocType.Allow Import = 1
+
User has Import permission
→ target может участвовать в Data Import
```

Это тот самый `Import`, который мы видели в Role Permission Manager.

Он не равен:

```text
Create
Write
```

и существует отдельно.

---

## 10. Доступ к самому системному инструменту — отдельная вещь

Не путай два вопроса:

```text
можно ли импортировать Request?
```

и:

```text
можно ли работать с системным DocType Data Import?
```

В стандартной metadata текущего v16 полный доступ к самому `Data Import` выдан роли:

```text
System Manager
```

А backend дополнительно проверяет `Import` permission целевого DocType.

То есть permission target Document и permission административного инструмента — два разных слоя.

---

## 11. Не все системные DocTypes разрешено импортировать

Текущий v16 также содержит отдельный список заблокированных Core DocTypes.

То есть даже если пытаться включить всё подряд, Framework не рассматривает Data Import как универсальный способ переписывать внутренние системные таблицы.

Главная мысль:

> Data Import предназначен прежде всего для нормальных бизнес-DocTypes, а не для бесконтрольного изменения внутренностей Framework.

---

## 12. Поддерживаемые файлы в UI v16

Текущий Data Import frontend разрешает:

```text
.csv
.xls
.xlsx
```

То есть можно использовать и Excel, и CSV.

Для повторяемых интеграций CSV часто проще контролировать технически.

Для ручной работы пользователя Excel может быть удобнее.

Сам формат файла не меняет модель импорта:

```text
file
→ parse rows
→ map columns
→ build Documents
→ insert/save
```

---

## 13. Импорт из Google Sheets

В текущем v16 `Data Import` имеет ещё поле:

```text
Import from Google Sheets
```

URL должен быть публично доступным для чтения в той форме, которую ожидает Framework.

Это удобно для одноразовой совместной подготовки таблицы.

Но Google Sheet не превращает Data Import в полноценную синхронизацию.

Схема всё равно остаётся:

```text
прочитать Sheet
→ импортировать текущее содержимое
```

а не:

```text
постоянно синхронизировать изменения туда и обратно
```

Для настоящей интеграции нужен другой механизм.

---

## 14. CSV delimiter в текущем v16

CSV в разных странах часто выглядит по-разному.

Например:

```text
comma:
name,department,status

semicolon:
name;department;status

tab:
name<TAB>department<TAB>status
```

В текущем v16 у `Data Import` есть:

```text
Detect CSV type
Custom Delimiters
Delimiter Options
```

Стандартный набор delimiter options сейчас включает по смыслу:

```text
,
;
tab
|
```

Поэтому файл с `;` не обязательно предварительно переделывать вручную.

---

## 15. Preview — это проверка до запуска

После загрузки файла Frappe показывает:

```text
Import Preview
```

В текущем backend preview ограничен первыми:

```text
10 rows
```

если файл больше.

Это не означает, что импортируются только десять строк.

Preview — просто небольшое окно проверки:

```text
правильно ли распознаны колонки?
правильно ли распарсились значения?
есть ли warnings?
```

Перед большим импортом обязательно смотри preview.

---

## 16. Column mapping

Если заголовок файла не совпал с полем автоматически, текущий интерфейс позволяет переназначить колонку.

Упрощённо:

```text
CSV: Dept
        ↓ remap
Frappe: department
```

Такое сопоставление сохраняется во внутреннем:

```text
template_options.column_to_field_map
```

Это полезно для разового несовпадения названий.

Но если каждый импорт требует десятков нестабильных mappings, это уже сигнал, что исходные данные лучше нормализовать до Data Import.

---

## 17. Link-поля требуют существующих связанных Documents

Пусть есть:

```text
Request.department
→ Link / Department
```

и в CSV:

```text
Department = Support
```

Чтобы импорт прошёл нормально, `Department` с подходящим `name` должен существовать.

Data Import не должен рассматриваться как магический механизм:

```text
встретил неизвестный Link
→ автоматически создал справочник
```

Если справочники ещё не загружены, обычно сначала импортируют их.

Например:

```text
1. Department
2. Request
```

а не наоборот.

---

## 18. Select — это не произвольный текст

Если поле:

```text
priority = Select
```

с options:

```text
Low
Medium
High
```

значение:

```text
Very High
```

не становится новым Select option автоматически.

Импорт должен соблюдать модель поля.

Поэтому хороший процесс:

```text
сначала привести источник к допустимым значениям
→ потом импортировать
```

---

## 19. Даты тоже должны соответствовать ожидаемому формату

Template metadata показывает формат Date/Datetime согласно настройкам Frappe.

Это важнее, чем кажется.

Например строка:

```text
01/02/2026
```

без контекста может означать:

```text
1 февраля
или
2 января
```

Для массового импорта лучше не полагаться на догадки.

Используй формат, который ожидает конкретный Site/template.

---

## 20. Check-поле

Для `Check` template подсказка текущего exporter по смыслу:

```text
0 or 1
```

То есть надёжный массовый вариант:

```text
0
1
```

а не набор человеческих вариантов:

```text
Да
Нет
YES
FALSE
x
```

если вы не убедились, как именно они будут разобраны.

---

# Часть II. Insert New Records

## 21. Что происходит при Insert

Текущий Importer v16 делает по смыслу:

```python
new_doc = frappe.new_doc(doctype)
new_doc.update(imported_values)
new_doc.insert()
```

То есть создаётся настоящий новый Document.

Это означает, что продолжает работать обычная логика:

```text
before_insert
before_validate
validate
autoname
before_save
after_insert
on_update
```

в рамках обычного Document lifecycle.

Подробно controller events будут в главе 50.

---

## 22. Naming при Insert

Если DocType использует автоматический naming, обычно не нужно руками придумывать `name` для каждой строки.

Например:

```text
REQ-00001
REQ-00002
REQ-00003
```

может создавать naming mechanism самого DocType.

Если naming основан на:

```text
autoname = field:request_code
```

то именно это поле становится особенно важным идентификатором для import/update механики.

Не смешивай:

```text
человеческий бизнес-код
```

и

```text
случайно введённый Excel ID
```

без ясной naming-модели.

---

## 23. Когда `ID` нужен

Для новых записей `ID/name` часто оставляют пустым, если naming создаётся Framework автоматически.

Для обновления существующих records идентификатор уже критичен.

Поэтому базовое правило:

```text
Insert
→ чаще ID создаёт Frappe

Update
→ Frappe должен понять, какой существующий Document менять
```

---

## 24. `Submit After Import`

Если целевой DocType:

```text
Is Submittable = 1
```

текущий Data Import показывает опцию:

```text
Submit After Import
```

При включении после `insert()` Framework вызывает:

```python
doc.submit()
```

То есть создаётся не просто Draft.

Он проходит настоящий Submit lifecycle.

Не включай этот флаг автоматически для любого массового импорта.

Сначала проверь, что данные действительно готовы к необратимому business-state `Submitted`.

---

## 25. `Don't Send Emails`

В текущем `Data Import` есть флаг:

```text
Don't Send Emails
```

и по стандартной metadata v16 он включён по умолчанию.

При импорте устанавливается внутренний:

```text
mute_emails
```

Это полезно, потому что массовая загрузка 20 000 records не должна неожиданно породить 20 000 уведомлений только из-за обычных hooks/Notification-процессов.

Но не предполагай, что этот флаг отключает **любое возможное внешнее действие любого custom code**.

Свой App всё равно нужно проектировать осознанно.

---

# Часть III. Update Existing Records

## 26. Update начинается с идентификации существующего Document

В текущем v16 Importer выбирает ID field так:

```text
если autoname = field:some_field
→ ID field = some_field

иначе
→ ID field = name
```

Упрощённо для обычного DocType:

```text
ID = REQ-0001
```

означает:

```python
frappe.get_doc("Request", "REQ-0001")
```

После этого значения из файла накладываются на Document и вызывается:

```python
save()
```

---

## 27. Самый надёжный Update — сначала экспортировать существующие записи

Не набирай ID вручную, если можно избежать этого.

Безопасный цикл:

```text
1. Download Template
2. Export existing records
3. Оставить ID
4. Изменить только нужные columns
5. Upload
6. Preview
7. Update Existing Records
```

Так значительно меньше риска:

```text
ошибиться в ID
обновить не тот Document
создать несогласованный файл
```

---

## 28. Для Update можно выбирать только изменяемые колонки

Это одна из главных сильных сторон штатного инструмента.

Например нужно поменять priority у 300 Requests.

Файл может быть минимальным:

```text
ID       | Priority
REQ-0001 | High
REQ-0002 | Low
REQ-0003 | Medium
```

Не нужно тащить:

```text
subject
description
department
owner
creation
и ещё 40 полей
```

если они не меняются.

---

## 29. `No changes to update` в текущем v16

Есть неочевидный нюанс реализации.

Перед save текущий Importer сравнивает:

```text
existing_doc
updated_doc
```

через diff.

Если изменений нет, он вызывает ошибку:

```text
No changes to update
```

То есть строка Update, которая фактически ничего не меняет, может попасть в import log как проблема.

Это полезно знать при массовом повторном прогоне уже обновлённого файла.

---

# Часть IV. Child Table

## 30. Child Table тоже можно импортировать вместе с Parent

Представим:

```text
Request
├── subject
├── department
└── items → Table / Request Item
```

`Request Item`:

```text
item
qty
```

Шаблон может содержать parent и child columns вместе.

Например по смыслу:

```text
Request Subject | Department | Item     | Qty
Printer setup   | IT         | Monitor  | 2
                              | Keyboard | 2
                              | Mouse    | 2
```

---

## 31. Как v16 понимает, что следующая строка — Child Row

Текущий Importer использует простое правило.

Первая строка начинает Parent Document.

Если далее есть Child Table columns и следующая строка имеет пустые значения во всех parent columns:

```text
parent columns = blank
```

она считается продолжением предыдущего документа — child row.

Схема:

```text
Parent values present
→ новый Parent Document

Parent values blank
→ child row предыдущего Parent
```

Поэтому в сложных шаблонах нельзя хаотично заполнять parent columns в каждой строке и ожидать, что importer сам угадает структуру.

---

## 32. Child Table — часть Parent Document

При разборе файла текущий Importer собирает структуру примерно так:

```python
parent_doc = {
    "subject": "Printer setup",
    "items": [
        {"item": "Monitor", "qty": 2},
        {"item": "Keyboard", "qty": 2},
    ],
}
```

а затем сохраняет весь Parent Document.

Это соответствует модели Frappe:

```text
Child row
не является самостоятельным бизнес-документом
```

который пользователь обычно импортирует независимо от parent context.

---

## 33. При обновлении Child Table будь особенно осторожен

Массовый update parent + child rows уже сложнее простого изменения одного поля.

Нужно понимать:

```text
какие child rows уже существуют
какие ID у child rows
что именно должно добавиться
что должно измениться
что должно исчезнуть
```

Поэтому для Update Child Table особенно правильно:

```text
сначала выгрузить существующие данные
→ изменить template минимально
→ проверить на 1–2 Documents
→ только потом запускать массово
```

Если требуется сложное reconcile/merge дочерних строк, Data Import быстро перестаёт быть удобным решением.

---

# Часть V. Как реально выполняется импорт

## 34. Data Import в UI v16 работает через background job

При `Start Import` текущий backend ставит задачу в очередь:

```text
queue = default
```

с отдельным job id для конкретного Data Import.

Упрощённо:

```text
browser
→ Start Import
→ enqueue job
→ worker
→ Importer.import_data()
```

Поэтому долгий импорт не обязан жить внутри одного обычного browser request.

---

## 35. Scheduler должен быть активен

Перед запуском текущий backend проверяет scheduler.

Если scheduler inactive и это не test/developer synchronous path, импорт останавливается с ошибкой по смыслу:

```text
Scheduler is inactive. Cannot import data.
```

Это полезный диагностический факт.

Если Data Import «не стартует», проблема может быть не в CSV, а в инфраструктуре worker/scheduler.

---

## 36. В Developer Mode импорт может выполняться сразу

В текущем source:

```text
run_now = in_test OR developer_mode
```

То есть в Developer Mode Data Import может выполняться синхронно в текущем процессе вместо обычного enqueue behavior.

Это удобно для разработки, но не надо переносить ощущения от dev-site на production без проверки.

---

## 37. Batch size v16

Importer разбивает payloads на batches.

Размер берётся из конфигурации:

```text
data_import_batch_size
```

если она не задана, текущий fallback:

```text
1000
```

Важно:

> batch здесь не означает одну общую транзакцию на 1000 Documents.

Текущая реализация коммитит успешные records значительно чаще.

---

## 38. Импорт не является атомарным целиком

Это одна из самых важных вещей главы.

Текущий v16 после каждого успешно обработанного payload делает:

```python
frappe.db.commit()
```

При ошибке текущего payload:

```python
frappe.db.rollback()
```

но предыдущие успешно закоммиченные Documents уже остаются в базе.

Например импортируем 1000 Requests:

```text
1–724  → Success
725    → Error
726–1000 → продолжают обрабатываться
```

Результат может быть:

```text
Success: 999
Failure: 1
Status: Partial Success
```

Это **не all-or-nothing transaction**.

---

## 39. Почему существует `Partial Success`

У `Data Import.status` в текущем v16 есть:

```text
Pending
Success
Partial Success
Error
Timed Out
```

`Partial Success` означает именно то, что название говорит:

```text
часть Documents уже сохранена
часть не прошла
```

Поэтому после ошибки нельзя автоматически считать:

> ничего не импортировалось.

Всегда смотри Import Log.

---

## 40. Retry не повторяет всё вслепую

Текущий Importer хранит `Data Import Log` и при retry умеет определить уже успешно импортированные строки.

Такие row indexes пропускаются.

Схема:

```text
первый запуск
1 success
2 success
3 fail
4 success

Retry
1 skip
2 skip
3 retry
4 skip
```

Это значительно безопаснее полного повторного Insert по тому же файлу.

---

## 41. Data Import Log

Для каждого результата создаётся отдельный системный record:

```text
Data Import Log
```

Текущий DocType хранит:

```text
data_import
row_indexes
success
docname
messages
exception
log_index
```

То есть можно понять:

```text
какая строка файла
→ какой Document
→ успех или ошибка
→ какое сообщение/exception
```

---

## 42. Export Errored Rows

При `Partial Success` текущий UI предлагает:

```text
Export Errored Rows
```

Это очень полезный рабочий цикл:

```text
1000 rows
↓
990 success
10 failed
↓
Export Errored Rows
↓
исправить только 10
↓
Retry / новый корректный импорт
```

Не нужно вручную вырезать ошибки из исходного файла по номерам строк.

---

## 43. Import Log тоже можно выгрузить

Текущий backend умеет сформировать CSV-log с данными по смыслу:

```text
Row Numbers
Status
Message
Exception
```

Это полезно, когда ошибок много и разбирать их в интерфейсе неудобно.

---

## 44. Cancel Import — не Undo

В текущем UI есть:

```text
Cancel Import
```

Но сама кнопка предупреждает, что немедленная остановка job может быть опасной.

Главное:

> **Cancel background job не откатывает уже закоммиченные Documents.**

Мы уже видели, что успешные payloads коммитятся по ходу работы.

Поэтому Cancel означает:

```text
остановить дальнейшую обработку
```

а не:

```text
вернуть базу в состояние до Start Import
```

---

# Часть VI. Большие объёмы

## 45. Web UI — не лучший путь для огромных файлов

Официальная документация Framework для больших импортов рекомендует CLI.

Ориентир в документации:

```text
более 5000 Documents
→ bench data-import
```

Причина простая:

```text
меньше зависимости от browser/web request
проще выполнять большой batch
проще видеть console output
```

Это не значит, что строка 5001 технически всегда невозможна в UI.

Это практическая граница, после которой CLI считается более надёжным инструментом.

---

## 46. `bench data-import`

Текущий Framework поддерживает команду:

```bash
bench --site site.local data-import /path/to/request.xlsx \
  --doctype Request \
  --type Insert
```

Для update:

```bash
bench --site site.local data-import /path/to/request.csv \
  --doctype Request \
  --type Update
```

Официальная команда также поддерживает:

```text
--submit-after-import
--mute-emails
```

То есть CLI использует тот же общий Data Import механизм, а не отдельный самодельный SQL loader.

---

## 47. CLI не делает плохую модель данных хорошей

Если импорт из 500 000 строк медленный, причина может быть не только в UI.

Например каждый Document при `validate()` делает:

```text
5 SQL queries
3 remote API calls
2 expensive calculations
```

Тогда:

```text
500 000 Documents × дорогой lifecycle
```

останется дорогим и через CLI.

Нужно различать:

```text
ограничение способа запуска
```

и

```text
дорогая бизнес-логика каждого Document
```

---

# Часть VII. Data Export

## 48. Что такое Data Export

`Data Export` делает обратную операцию:

```text
Documents
→ CSV / Excel
```

Например:

```text
Request
↓
ID | Subject | Department | Priority
```

Это полезно для:

```text
анализа
массового редактирования
переноса данных
подготовки Update template
ручной сверки
```

---

## 49. Data Export и Download Template связаны, но не идентичны

Есть два близких сценария.

### Из Data Import

```text
Download Template
```

ориентирован на:

```text
последующий Import
```

### Data Export

отдельный инструмент:

```text
выбрать DocType
выбрать fields
задать filters
выбрать CSV/Excel
выгрузить данные
```

Под капотом механика пересекается, но пользовательский сценарий разный.

---

## 50. CSV и Excel

Текущий `Data Export` поддерживает:

```text
Excel
CSV
```

Также есть флаг:

```text
Export without main header
```

Он убирает дополнительные template notes/column descriptions и делает выгрузку более похожей на обычную плоскую таблицу.

Если файл должен потом вернуться в Data Import, metadata/header information может быть полезна.

Если файл нужен для анализа — чистый export часто удобнее.

---

## 51. Выбор полей

Data Export позволяет выбрать конкретные fields Parent и Child DocTypes.

Например:

```text
Request
- name
- subject
- department

Request Item
- item
- qty
```

Это лучше, чем автоматически выгружать весь документ целиком.

Правило то же:

> выгружай только те данные, которые реально нужны задаче.

---

## 52. Filters

Перед экспортом можно задать filters.

Например:

```text
status = Open
department = Support
```

Тогда выгрузка строится только по подходящим Documents.

Это позволяет не выгружать миллион строк, если нужен один Department за один период.

---

## 53. Export permission

Для массовой выгрузки существует отдельное permission:

```text
Export
```

Текущий exporter явно вызывает permission-check перед выдачей данных.

Кроме того, получение Parent Documents идёт через:

```python
frappe.get_list(...)
```

то есть обычные row-level permissions пользователя продолжают участвовать в выборке.

Поэтому нормальный Data Export не должен рассматриваться как:

```text
скачать всю таблицу независимо от access model
```

---

## 54. Permission Level учитывается при выборе exportable fields

Текущий exporter Data Import template использует:

```text
get_permitted_fields()
```

и разрешённые Permission Levels для чтения.

То есть пользователь не должен автоматически получить в шаблоне поле, которое его role/permlevel не позволяет читать.

Это важное продолжение главы 19:

```text
Permission Level
работает не только как визуальное скрытие Form
```

---

## 55. Export создаёт Access Log

Текущий v16 при Data Export вызывает:

```text
make_access_log(...)
```

и сохраняет информацию вроде:

```text
user
export_from
file_type
filters
columns
```

То есть массовая выгрузка не обязана быть полностью невидимым действием без следа.

При этом стандартный `Access Log` автоматически очищает старые записи по своей maintenance-логике; текущий helper имеет default cleanup window 30 дней.

Не путай такой operational log с вечным юридическим audit archive.

---

## 56. Data Export тоже не заменяет backup

Экспорт CSV/Excel — это данные выбранных полей.

Backup Site — это совсем другая задача.

```text
Data Export
→ человекочитаемые табличные данные

Backup
→ восстановление Site/database/files
```

Нельзя считать:

```text
я выгрузил CSV
→ у меня полноценный backup Frappe
```

Backup/restore разберём отдельно в главе 65.

---

# Часть VIII. Безопасный рабочий процесс

## 57. Перед большим Insert сначала импортируй 3–5 записей

Не начинай с 50 000 строк.

Правильнее:

```text
1. сделать template
2. заполнить 3–5 rows
3. Import
4. открыть Documents руками
5. проверить Links
6. проверить Child Tables
7. проверить lifecycle side effects
8. только потом массовый файл
```

Это намного дешевле, чем потом разбираться, почему 50 000 Documents создались неправильно.

---

## 58. Перед массовым Update сделай экспорт

Минимальная страховка:

```text
Export текущих данных
↓
сохранить исходный файл
↓
делать Update
```

Это не полноценный database backup, но хотя бы даёт вам исходное состояние затрагиваемых полей для ручной сверки.

Для действительно критичного массового изменения нужен нормальный backup Site.

---

## 59. Не редактируй одновременно лишние колонки

Плохой update-файл:

```text
ID
Subject
Description
Department
Priority
Status
Owner
... ещё 40 колонок
```

когда нужно изменить только Priority.

Хороший:

```text
ID
Priority
```

Чем меньше поверхность изменения, тем проще контролировать результат.

---

## 60. Проверяй side effects

Обычный Document lifecycle означает, что при импорте могут срабатывать:

```text
validate
hooks
Workflow-related checks
Assignment logic
Notifications
custom controller code
```

Поэтому вопрос перед массовым импортом:

> что произойдёт кроме записи полей в базу?

особенно важен.

Если import изменяет 100 000 Documents, даже маленький side effect становится большим.

---

## 61. Не импортируй грязные справочники «как есть»

Например источник содержит Department:

```text
IT
It
I.T.
Information Technology
ИТ
```

а в Frappe должен быть один справочник:

```text
IT
```

Data Import не обязан быть местом, где решается вся нормализация мира.

Лучше:

```text
source
→ normalize
→ validate
→ clean import file
→ Data Import
```

---

## 62. Не используй Data Import как постоянную интеграцию

Если каждое утро человек должен:

```text
скачать CSV из системы A
почистить три колонки
открыть Data Import
загрузить файл
проверить ошибки
```

то это уже не разовая загрузка.

Это интеграционный процесс.

Следующий уровень решения:

```text
REST API
scheduled job
integration App
Data Migration mechanism
ETL pipeline
```

в зависимости от задачи.

---

## 63. Когда нужен собственный import script

Data Import уже тесен, если нужно:

```text
сложное преобразование каждой строки
lookup по нескольким внешним ключам
upsert по собственному business key
merge нескольких источников
сложная дедупликация
reconciliation
предварительная staging table
массовая обработка миллионов records
частичное обновление Child Table по custom правилам
```

Тогда нормальнее написать отдельный контролируемый pipeline.

Но даже в собственном коде не нужно автоматически прыгать к raw SQL.

Часто правильный слой остаётся:

```text
frappe.get_doc / new_doc / db API / Query Builder
```

с чётко определёнными транзакциями и validation strategy.

---

## 64. Data Import против `frappe.get_doc().insert()` в цикле

Иногда начинающий пишет:

```python
for row in csv:
    frappe.get_doc({...}).insert()
```

хотя штатный Data Import уже умеет:

```text
template
preview
column mapping
warnings
background job
progress
partial success
retry
error rows
import log
```

Поэтому сначала спроси:

> действительно ли нам нужен собственный importer?

Если нет — штатный инструмент дешевле поддерживать.

---

## 65. Data Import против прямого SQL INSERT

Для обычных бизнес-DocTypes прямой SQL массово обходит слишком многое:

```text
Document validation
naming
controller hooks
permissions
child handling
versioning
link checks
business invariants
```

Поэтому идея:

```text
CSV
→ INSERT INTO tabRequest
```

не является «быстрым вариантом Data Import».

Это другой уровень ответственности.

Он уместен только там, где разработчик полностью контролирует последствия и сознательно работает ниже Document layer.

---

## 66. Простая карта выбора

```text
нужно разово загрузить подготовленный CSV/XLSX?
        │
        ├── да → Data Import
        │
        └── нет
             ↓
нужно массово обновить существующие Documents?
        │
        ├── да → Export existing + Update Existing Records
        │
        └── нет
             ↓
нужна постоянная синхронизация / сложный transform?
        │
        ├── да → integration / ETL / App code
        │
        └── нет → уточнить задачу
```

Для выгрузки:

```text
нужен CSV/Excel существующих Documents?
→ Data Export

нужен backup Site?
→ Backup

нужен программный API consumer?
→ REST / RPC
```

---

## 67. Полный маленький пример Insert

Есть `Request`:

```text
subject     Data, Required
department  Link → Department
priority    Select: Low / Medium / High
status      Select: Open / Closed
```

Сначала создаём Departments:

```text
IT
Support
```

Затем:

```text
Data Import
Document Type = Request
Import Type = Insert New Records
```

Download Template.

Файл:

```text
Subject          | Department | Priority | Status
Printer broken   | Support    | High     | Open
Create user      | IT         | Medium   | Open
```

Upload.

Preview.

Start Import.

Ожидаем:

```text
2 Success
Status = Success
```

После этого открываем оба Request и проверяем, что реальные Documents выглядят так, как ожидалось.

---

## 68. Полный маленький пример Update

Теперь хотим изменить Priority первого Request.

Скачиваем существующие records для Update и оставляем:

```text
ID       | Priority
REQ-0001 | Low
```

В `Data Import`:

```text
Import Type = Update Existing Records
```

Upload → Preview → Start Import.

Текущий backend:

```text
находит REQ-0001
→ загружает Document
→ меняет priority
→ save()
```

После чего в системе:

```text
REQ-0001.priority = Low
```

---

## 69. Мини-практика

Создай учебный DocType:

```text
Request
```

с полями:

```text
subject       Data / Required
department    Link → Department
priority      Select
status        Select
amount        Currency
```

Подготовь Departments:

```text
Support
IT
```

### Шаг 1

Через `Insert New Records` загрузи 5 Requests.

Проверь:

```text
name
Links
amount
status
```

### Шаг 2

Экспортируй эти 5 Documents.

Оставь только:

```text
ID
Priority
Amount
```

### Шаг 3

Измени три строки и сделай:

```text
Update Existing Records
```

### Шаг 4

Одну строку намеренно сломай:

```text
Department = DOES-NOT-EXIST
```

Посмотри:

```text
Partial Success
Data Import Log
Export Errored Rows
```

### Шаг 5

Исправь только ошибочную строку и повтори импорт.

Убедись, что уже успешные rows не создаются повторно в рамках retry того же Data Import.

---

## 70. Практика на выбор инструмента

### A

Нужно один раз загрузить 300 Departments из подготовленного XLSX.

Ответ:

```text
Data Import
```

### B

Нужно изменить Priority у 200 существующих Requests.

Ответ:

```text
Export existing records
+
Update Existing Records
```

### C

Каждый час нужно синхронизировать 50 000 записей из внешнего API.

Ответ:

```text
не ручной Data Import
→ integration / background jobs / App code
```

### D

Нужно выгрузить список Open Requests в Excel.

Ответ:

```text
Data Export
```

### E

Нужно иметь возможность восстановить весь Site после аварии.

Ответ:

```text
Backup
```

### F

Нужно объединить пять исходных файлов, убрать дубли, нормализовать справочник и только потом загрузить результат.

Ответ:

```text
ETL / preprocessing
↓
чистый файл
↓
Data Import
```

---

## 71. Типичные ошибки

### Ошибка 1. Делать самодельный CSV без template

Работает, пока не столкнётесь с:

```text
неверным fieldname
не тем Date format
Child Table
Link
mandatory field
```

Сначала скачай template.

---

### Ошибка 2. Update без ID

Framework должен понимать, какой существующий Document менять.

---

### Ошибка 3. Импортировать неизвестные Link values

Сначала загрузите/создайте справочники.

---

### Ошибка 4. Считать import одной транзакцией

В текущем v16 успешные payloads коммитятся по ходу обработки.

`Partial Success` — реальное сохранённое состояние.

---

### Ошибка 5. Нажать Cancel и ожидать Undo

Cancel останавливает job, а не откатывает уже закоммиченные Documents.

---

### Ошибка 6. Обновлять весь DocType ради одного поля

Выбирай минимальный набор columns.

---

### Ошибка 7. Использовать Data Import как ежедневную интеграцию

Повторяемый ручной обмен файлами — сигнал автоматизировать integration flow.

---

### Ошибка 8. Делать raw SQL ради скорости без понимания lifecycle

Data Import работает через Document layer не случайно.

---

### Ошибка 9. Считать Data Export backup-ом

CSV не заменяет database + files backup.

---

### Ошибка 10. Не проверять import под реальными permissions

Import/Export связаны с отдельными permissions и row/field access model.

---

## 72. Что запомнить

1. **Data Import превращает CSV/XLS/XLSX rows в обычные Frappe Documents.**
2. **Два основных режима — Insert New Records и Update Existing Records.**
3. **Сначала скачивай template, а не угадывай колонки.**
4. **Для DocType должен быть включён `Allow Import`.**
5. **На целевой DocType отдельно проверяется permission `Import`.**
6. **Link values должны соответствовать существующим связанным Documents.**
7. **Для Update нужен стабильный идентификатор существующего Document.**
8. **При `autoname = field:...` текущий importer использует это поле как ID field; иначе — `name`.**
9. **Child rows определяются как продолжение Parent, когда parent columns в следующих строках пусты.**
10. **UI Data Import v16 запускает импорт через background job.**
11. **Preview показывает максимум первые 10 rows, а не весь файл.**
12. **`data_import_batch_size` имеет текущий fallback 1000.**
13. **Импорт целиком не атомарен: успешные Documents коммитятся по одному payload.**
14. **Поэтому возможен настоящий `Partial Success`.**
15. **Retry умеет пропускать уже успешные rows того же Data Import.**
16. **Data Import Log связывает row indexes, result и exception.**
17. **Cancel Import не является Undo.**
18. **Для крупных импортов официально рекомендуется `bench data-import`; ориентир документации — более 5000 Documents.**
19. **Data Export поддерживает CSV/Excel, filters и выбор fields.**
20. **Export использует permission-aware data access и отдельный `Export` permission.**
21. **Permission Level участвует в выборе доступных для экспорта полей.**
22. **Массовый Data Export создаёт Access Log.**
23. **Data Import / Export не заменяют ETL, integration и backup.**
24. **Если данные требуют сложной трансформации, сначала приведи их к чистой модели, потом импортируй.**

---

## Источники

- [Frappe Framework — Bulk Data Import Guide](https://docs.frappe.io/framework/user/en/guides/data/import-large-csv-file)
- [Frappe Framework — Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [Frappe Framework — Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [Frappe Framework — Configuration](https://docs.frappe.io/framework/user/en/basics/site_config)
- [Frappe Framework v16 — `Data Import` controller](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_import/data_import.py)
- [Frappe Framework v16 — `Data Import` DocType](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_import/data_import.json)
- [Frappe Framework v16 — `Data Import` frontend](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_import/data_import.js)
- [Frappe Framework v16 — Importer](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_import/importer.py)
- [Frappe Framework v16 — Data Import template exporter](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_import/exporter.py)
- [Frappe Framework v16 — Data Import template UI](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/data_import/data_exporter.js)
- [Frappe Framework v16 — `Data Import Log`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_import_log/data_import_log.json)
- [Frappe Framework v16 — `Data Export`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_export/data_export.js)
- [Frappe Framework v16 — Data Export backend](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/data_export/exporter.py)
- [Frappe Framework v16 — Access Log](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/access_log/access_log.py)

---

Дальше: **39. Web Form**.