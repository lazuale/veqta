# 30. Version и Track Changes

В прошлой главе мы разобрали Timeline и увидели, что часть его записей появляется из `Version`.

Теперь разберём сам механизм версионирования.

Он отвечает на простой вопрос:

> что именно изменилось в уже существующем Document между двумя сохранениями?

Проверено: **2026-08-31**.

---

## 1. Самый простой пример

Есть документ:

```text
Request REQ-0001

Subject: Replace printer
Priority: Medium
Status: Open
```

Пользователь открывает его и меняет:

```text
Priority: Medium → High
```

После Save Frappe может сохранить отдельную запись примерно такого смысла:

```text
Request REQ-0001
Priority changed:
Medium → High
```

Эта запись называется:

```text
Version
```

А свойство DocType, которое включает такое поведение, называется:

```text
Track Changes
```

Удобно запомнить:

```text
Track Changes
      ↓
сравнить старый Document с новым
      ↓
если есть полезные изменения
      ↓
создать Version
      ↓
показать изменение в Timeline
```

---

## 2. `Track Changes` — свойство DocType

У DocType есть штатный флаг:

```text
Track Changes
```

В metadata v16 его описание буквально сводится к тому, что при включении изменения документа отслеживаются и показываются в Timeline.

Для обычного пользовательского DocType его можно включить через **Customize Form**.

Для собственного standard DocType это также обычное свойство metadata DocType.

Пример:

```text
Request

Track Changes: ✓
```

После этого обычные сохранения существующих `Request` начинают участвовать в механизме Version.

Важно:

```text
Track Changes
≠ Track Views
≠ Track Seen
```

Это три разных свойства DocType.

`Track Changes` следит за изменениями значений документа.

---

# Что такое Version

## 3. `Version` — отдельный DocType Framework

Frappe не складывает историю изменений прямо внутрь `Request`.

Он создаёт отдельные Documents типа:

```text
Version
```

У Version в текущем v16 есть основные поля:

```text
ref_doctype
→ какой DocType изменяли

docname
→ какой конкретный Document изменяли

data
→ JSON с diff
```

Плюс у Version есть обычные системные поля Document:

```text
owner
creation
modified
...
```

Поэтому концептуально история выглядит так:

```text
Request REQ-0001
        │
        ├── Version A
        ├── Version B
        └── Version C
```

Каждый Version хранит не полную копию Request, а информацию о конкретной разнице.

---

## 4. Version — это diff, а не снимок всего документа

Допустим, было:

```text
Priority: Medium
Status: Open
Description: Replace printer
```

Стало:

```text
Priority: High
Status: Open
Description: Replace printer
```

Version не обязан сохранять ещё одну полную копию всех трёх полей.

Ему достаточно сохранить смысл:

```text
changed:
Priority
Medium → High
```

То есть модель примерно такая:

```text
старый Document
        ↓ compare
новый Document
        ↓
только разница
        ↓
Version.data
```

Именно поэтому Version лучше воспринимать как **журнал diff**, а не как backup документа.

---

# Что попадает в diff

## 5. Обычное изменение поля

Для простых полей Version хранит:

```text
fieldname
старое значение
новое значение
```

Например:

```text
priority
Medium
High
```

Во внутреннем `data` это относится к группе:

```text
changed
```

Упрощённо:

```json
{
  "changed": [
    ["priority", "Medium", "High"]
  ]
}
```

Точный JSON знать наизусть не нужно.

Нам важна модель:

```text
changed
→ значение поля изменилось
```

---

## 6. Frappe отслеживает и `docstatus`

Кроме обычных DocField движок v16 отдельно сравнивает:

```text
name
docstatus
```

Поэтому для Submittable DocType переход:

```text
docstatus 0 → 1
```

может попасть в Version.

Timeline умеет превратить это в понятное человеку сообщение вроде:

```text
User submitted this document
```

А переход:

```text
1 → 2
```

может отображаться как Cancel.

Это ещё раз показывает связь механизмов:

```text
Submit
  ↓
docstatus изменился
  ↓
Version зафиксировал diff
  ↓
Timeline показал понятное событие
```

Но сам Submit всё равно является lifecycle-операцией Document, а не функцией Version.

---

# Child Table

## 7. Изменения Child Table тоже входят в Version родителя

Представим:

```text
Request
└── Items
    ├── Printer
    └── Cable
```

`Items` — Child Table.

Если у родительского `Request` включён `Track Changes`, Version умеет различать несколько типов изменений таблицы.

В текущем v16 используются четыре группы:

```text
changed
added
removed
row_changed
```

Для обычных полей в основном используется `changed`.

Для Child Table появляются ещё три важных случая.

---

## 8. `added`

Было:

```text
Items
└── Printer
```

Стало:

```text
Items
├── Printer
└── Cable
```

Frappe видит новую строку Child Table.

В Version это относится к:

```text
added
```

Timeline может показать смысл:

```text
User added 1 row to Items
```

---

## 9. `removed`

Было:

```text
Items
├── Printer
└── Cable
```

Стало:

```text
Items
└── Printer
```

Удалённая строка попадает в:

```text
removed
```

---

## 10. `row_changed`

Было:

```text
Cable
Quantity: 1
```

Стало:

```text
Cable
Quantity: 3
```

Строка не новая и не удалённая.

Изменилось поле внутри уже существующей строки.

Это относится к:

```text
row_changed
```

То есть Version умеет отличить:

```text
новую строку
удалённую строку
изменение существующей строки
```

Это одна из причин не делать самодельный журнал Child Table, пока штатного Version достаточно.

---

## 11. `Track Changes` включается на родительском DocType

В metadata v16 флаг `Track Changes` предназначен для обычного DocType и не показывается как самостоятельная настройка Child Table.

Модель такая:

```text
Request
Track Changes = 1
        ↓
Frappe сравнивает Request целиком
        ↓
в том числе его Child Tables
```

Не нужно пытаться включать отдельный version history на каждом Child DocType.

---

# Когда создаётся Version

## 12. Save без изменений не обязан создавать Version

Version создаётся только если сравнение нашло полезную разницу.

Например пользователь открыл Request и нажал Save, но значения фактически не изменились.

Тогда:

```text
old == new
   ↓
полезного diff нет
   ↓
новый Version не нужен
```

В source v16 `Version.update_version_info()` возвращает `False`, если diff отсутствует.

---

## 13. Обычное создание Document — отдельный случай

Новичок может ожидать:

```text
создали REQ-0001
→ обязательно создался Version №1
```

Но это не основная модель v16.

Для нового документа предыдущего состояния ещё нет:

```text
old Document отсутствует
```

Обычное создание и так видно в Timeline через системные данные документа.

Version при insert создаётся только в специальном случае, когда Framework передал `updater_reference` — то есть есть информация, что Document был создан через другой механизм, который стоит зафиксировать как источник создания.

Примеры подобных внутренних механизмов мы уже встречали в Auto Repeat и других автоматизациях.

Поэтому правильно думать так:

```text
Version
→ прежде всего история изменений существующего Document
```

а не «обязательный снимок при каждом Insert».

---

# Как Frappe понимает, что изменилось

## 14. Старое состояние хранится в памяти во время save-flow

Во время обычного сохранения Framework загружает состояние документа до записи в базу и хранит его как:

```text
_doc_before_save
```

Для application code есть публичный метод:

```python
doc.get_doc_before_save()
```

Простой пример:

```python
old_doc = self.get_doc_before_save()

if old_doc and old_doc.priority != self.priority:
    # priority действительно изменился
    pass
```

Официальный Document API прямо рекомендует этот метод для сравнения документа до и после изменения.

---

## 15. Для одного поля есть `has_value_changed()`

Если нужно проверить одно поле, есть более удобный метод:

```python
if self.has_value_changed("priority"):
    # priority изменился
    pass
```

Это не чтение исторических Version.

Это проверка внутри текущего save-flow:

```text
значение до Save
        ↕
значение сейчас
```

После завершения операции `get_doc_before_save()` не превращается в постоянный архив старых документов.

Для постоянной истории нужен Version или собственная модель хранения.

---

# Какие поля сравниваются

## 16. Не всё, что есть на форме, является данными для Version

Version проходит по metadata полей документа.

Поля без собственного сохраняемого значения — например элементы структуры формы — не являются обычными изменяемыми бизнес-данными.

Virtual fields также пропускаются текущим diff-движком v16.

Поэтому ожидание:

```text
любой визуальный элемент формы
→ обязательно попадёт в Version
```

неверно.

Version сравнивает состояние данных Document.

---

## 17. Большие текстовые значения тоже сравниваются

В v16 для длинных или многострочных изменений Version умеет строить дополнительный HTML diff.

То есть вместо неудобного:

```text
огромный старый текст
→ огромный новый текст
```

интерфейс Version может показать более наглядную разницу между строками.

Это относится именно к представлению diff.

Сам принцип остаётся тем же:

```text
old value
vs
new value
```

---

# Где пользователь видит Version

## 18. Основное место — Timeline документа

Когда форма загружается, backend v16 добавляет в `docinfo` последние Version этого документа.

Для Timeline стандартная загрузка сейчас берёт:

```text
до 10 последних Version
```

и сортирует их от новых к старым.

Frontend затем превращает технический diff в человеческие сообщения.

Например:

```text
Anna changed Priority from Medium to High
```

или:

```text
Anna added 2 rows to Items
```

Поэтому пользователь обычно работает не с JSON `Version.data`, а с Timeline.

---

## 19. Timeline показывает краткое представление, а Version содержит технический diff

Это разные уровни:

```text
Version.data
→ техническая структура изменений

Timeline
→ удобное краткое отображение этих изменений
```

Не нужно пытаться понять внутреннюю модель Version только по одной строке Timeline.

Например Timeline специально ограничивает количество деталей, которые выводит в одной короткой фразе.

Сам Version может содержать больше информации.

---

# Кто изменил документ

## 20. У Version есть свой `owner`

Version — обычный Document, поэтому его системный `owner` показывает пользователя, под которым была создана запись Version.

В типичном пользовательском Save это и позволяет Timeline написать:

```text
Anna changed ...
```

Текущий v16 также умеет сохранить в `Version.data` информацию об impersonation/audit user, если такая информация присутствует в session.

Это особенно полезно, когда Administrator временно работает от имени другого пользователя.

---

# Track Changes — не абсолютный audit log

## 21. Это очень полезный журнал, но у него есть границы

Самая опасная ошибка:

```text
Track Changes включён
→ значит вообще любое изменение базы гарантированно и неизменно записано
```

Нет.

Version — часть штатного Document save-flow Frappe.

Он отлично подходит для обычной истории изменений документов, но это не обещание перехватить абсолютно любую запись в базе любым возможным способом.

---

## 22. `db_set()` обходит обычный Save

В application code существует:

```python
doc.db_set("status", "Closed")
```

Этот метод специально обновляет значение непосредственно в базе и не запускает полный набор обычных controller validation.

Version создаётся методом `save_version()` обычного save-flow.

`db_set()` этот normal save/version flow не выполняет.

Поэтому:

```text
doc.save()
```

и:

```text
doc.db_set(...)
```

нельзя считать одинаковыми с точки зрения Version history.

Это одна из причин использовать прямые DB-обновления осознанно.

---

## 23. Прямые database updates тоже не становятся Version автоматически

То же относится к операциям вроде прямого SQL или низкоуровневого изменения значения в базе.

Если код сделал:

```text
UPDATE tabRequest ...
```

механизм `Version.get_diff(old, new)` сам по себе об этом не узнает.

Version не является database trigger.

Он является механизмом уровня Document.

Это принципиально разные архитектуры.

---

## 24. Version можно намеренно отключить для конкретной операции

В `Document.save_version()` текущего v16 есть несколько условий, при которых tracking пропускается.

Среди них:

```text
Track Changes выключен
Document сам является Version
flags.ignore_version установлен
идёт install
некоторые patch-сценарии
```

То есть application code технически может выполнить изменение без создания Version.

Ещё одна причина не называть Version «неотключаемым нормативным аудитом».

---

## 25. Удаление Document — отдельная операция

Version в первую очередь описывает diff между:

```text
old Document
и
new Document
```

Удаление документа не стоит автоматически трактовать как ещё одну обычную Version с полной копией удалённой записи.

Если бизнес-требование звучит так:

> нельзя потерять ни одно удалённое значение и нужно юридически значимое неизменяемое доказательство всех операций

одного `Track Changes` недостаточно как архитектурной гарантии.

Нужно отдельно проектировать audit requirements.

---

# Version и Amendment

## 26. У Submittable документов появляется ещё одна проблема

Напомним lifecycle:

```text
Draft
  ↓ Submit
Submitted
  ↓ Cancel
Cancelled
  ↓ Amend
новый Document
```

После Amend появляется другой Document, обычно с другим `name`, связанный через:

```text
amended_from
```

А Version привязан к паре:

```text
ref_doctype + docname
```

Поэтому история одной конкретной записи Version и цепочка нескольких amended документов — не одно и то же.

---

## 27. Для цепочки Amendments во Framework есть Audit Trail

В Frappe v16 есть отдельный штатный инструмент:

```text
Audit Trail
```

Его задача — сравнивать несколько последовательных amended версий Submittable Document.

Он использует тот же механизм `get_diff()`, но проходит по цепочке:

```text
amended_from
```

В текущем v16 он берёт максимум **5 документов** из этой цепочки.

То есть:

```text
Version
→ изменения внутри одного Document

Audit Trail
→ сравнение нескольких amended Documents
```

Название `Audit Trail` здесь не означает «универсальный аудит всей базы».

Это конкретный инструмент сравнения amendment chain.

---

# Сводная карта

## 28. Не путай четыре разных механизма

| Механизм | Что отвечает |
|---|---|
| `modified / modified_by` | когда и кем Document изменён последним |
| `Version` | что изменилось между сохранениями |
| Timeline | показывает Version и другие события в одной ленте |
| Audit Trail | сравнивает цепочку amended Submittable документов |

Например:

```text
modified_by
```

не расскажет, **какое** поле поменяли.

`Version` расскажет.

Но Version не покажет весь контекст вокруг документа — письма, комментарии, назначения и файлы.

Для этого есть Timeline.

---

# Когда Track Changes подходит

## 29. Хорошие случаи

`Track Changes` обычно отлично подходит, когда нужно:

```text
видеть, кто менял обычные поля
видеть старое и новое значение
видеть изменения Child Table
понимать Submit / Cancel в истории
показывать историю прямо в Timeline
разбирать обычные пользовательские исправления
```

В большинстве прикладных DocType это полезная штатная функция, которую стоит рассмотреть раньше собственного журнала изменений.

---

## 30. Когда одного Track Changes уже мало

Нужна отдельная модель, если требование примерно такое:

```text
аудит абсолютно всех DB-операций
неизменяемый журнал
обязательная фиксация прямых SQL/db_set изменений
хранение специальных бизнес-событий, а не только diff
долгосрочный регламентированный архив
сложные подписи или доказательство неизменности
отдельные retention rules
```

Тогда вопрос уже не:

```text
как включить Track Changes?
```

а:

```text
какую audit model требует система?
```

И это может потребовать собственного DocType, controller logic, hooks, внешнего хранилища или инфраструктурного аудита.

---

# Мини-практика

## 31. Включаем Track Changes

Возьми учебный DocType:

```text
Request
```

Пусть у него есть:

```text
subject
priority
status
```

Открой **Customize Form** для `Request`.

Включи:

```text
Track Changes
```

Сохрани Customize Form.

---

## 32. Создай Request

Создай:

```text
Subject: Check printer
Priority: Medium
Status: Open
```

Сохрани.

Не жди обязательной обычной Version только из-за самого Insert.

Проверь Timeline: там уже будет информация о создании документа.

---

## 33. Измени одно поле

Поменяй:

```text
Priority
Medium → High
```

Нажми Save.

В Timeline должна появиться запись об изменении Priority.

---

## 34. Измени два поля одновременно

Поменяй:

```text
Priority: High → Low
Status: Open → Closed
```

Сохрани.

Посмотри, как Timeline сворачивает несколько изменений в одну activity-запись.

---

## 35. Добавь Child Table

Если у `Request` уже есть учебная Child Table, добавь новую строку.

Например:

```text
Items
└── Cable
```

Сохрани.

Затем:

1. измени поле в этой строке;
2. сохрани;
3. удали строку;
4. снова сохрани.

Проверь три разных случая:

```text
added
row_changed
removed
```

---

## 36. Сравни с `modified_by`

После нескольких изменений посмотри системное:

```text
modified_by
```

Оно показывает только последнего изменившего пользователя.

Timeline + Version показывают историю нескольких изменений.

Это хороший способ почувствовать разницу между:

```text
последнее состояние
```

и:

```text
история diff
```

---

# Что запомнить

1. **`Track Changes` — свойство DocType.**
2. При обычном Save Frappe сравнивает Document с состоянием до сохранения.
3. Если есть полезный diff, создаётся отдельный `Version`.
4. Version хранит **разницу**, а не полную резервную копию документа.
5. Основные группы diff v16: `changed`, `added`, `removed`, `row_changed`.
6. Изменения Child Table входят в Version родительского документа.
7. `name` и `docstatus` тоже отдельно сравниваются.
8. Save без фактических изменений не требует нового Version.
9. Обычный Insert не обязан создавать стандартную Version изменения.
10. `get_doc_before_save()` и `has_value_changed()` позволяют application code работать с текущим old/new состоянием.
11. `db_set`, прямые DB updates и `ignore_version` показывают, почему Version нельзя считать абсолютным database audit log.
12. Timeline — представление истории; Version — один из источников этой истории.
13. Для сравнения цепочки amended Submittable документов во Framework есть отдельный `Audit Trail`.

---

## Официальные источники

- [Document API — `get_doc_before_save()` и `has_value_changed()`](https://docs.frappe.io/framework/user/en/api/document)
- [Audit Trail](https://docs.frappe.io/framework/user/en/audit-trail)
- [DocType metadata v16 — `Track Changes`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/doctype/doctype.json)
- [Version metadata v16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/version/version.json)
- [Version controller v16 — `get_diff()`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/version/version.py)
- [Document controller v16 — `save_version()`, `db_set()`, `get_doc_before_save()`](https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py)
- [Form load v16 — загрузка Version в Timeline](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/load.py)
- [Version Timeline renderer v16](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/footer/version_timeline_content_builder.js)
- [Audit Trail controller v16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/audit_trail/audit_trail.py)

Следующая глава: **31. Attachments и File**.
