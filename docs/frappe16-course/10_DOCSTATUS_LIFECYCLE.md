# 10. `docstatus`, Submit, Cancel и Amendment

Эта глава разбирает системный lifecycle документов во **Frappe Framework 16**.

Цель — понять:

- что такое `docstatus`;
- почему это не обычное поле `status`;
- какие переходы разрешает Framework;
- что реально делает `Submit`;
- что происходит при `Cancel`;
- какие поля можно менять после Submit;
- как работает Amendment;
- какие controller events вызываются на каждом этапе;
- чем `Cancel`, `Amend`, `Delete` и `Discard` отличаются друг от друга.

Проверено: **2026-08-30**.

---

## 1. `docstatus` — системное состояние документа

У каждого обычного Document во Frappe есть системное поле:

```text
docstatus
```

В Frappe 16 используются три значения:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

В исходном коде это оформлено через класс `DocStatus`:

```python
DocStatus.DRAFT = DocStatus(0)
DocStatus.SUBMITTED = DocStatus(1)
DocStatus.CANCELLED = DocStatus(2)
```

Важно:

> `docstatus` — системное состояние жизненного цикла Document, а не произвольный бизнес-статус.

---

## 2. `status` и `docstatus` — разные вещи

Представим документ:

```text
Request
├── status = In Progress
└── docstatus = 0
```

`status` может означать что угодно в предметной модели:

```text
New
In Progress
Waiting
Done
Rejected
```

А `docstatus` имеет фиксированную семантику Framework:

```text
Draft
Submitted
Cancelled
```

То есть:

```text
status
= бизнес-состояние

 docstatus
= системный lifecycle документа
```

Они могут существовать одновременно.

---

## 3. Когда `docstatus` реально начинает играть роль

Наиболее важен `docstatus` для DocType с включённым:

```text
Is Submittable
```

Обычный несабмиттабельный DocType обычно живёт как редактируемый документ.

Submittable DocType получает формальный lifecycle:

```text
Draft
  │
  │ Submit
  ▼
Submitted
  │
  │ Cancel
  ▼
Cancelled
```

Это уже не просто UI.

Framework проверяет эти переходы на сервере.

---

## 4. Разрешённые переходы в Frappe 16

В `Document.check_docstatus_transition()` явно разрешены следующие переходы:

```text
0 → 0    Save Draft
0 → 1    Submit
1 → 1    Update after Submit
1 → 2    Cancel
```

То есть:

| Было | Стало | Действие |
|---|---:|---|
| Draft | Draft | Save |
| Draft | Submitted | Submit |
| Submitted | Submitted | Update after Submit |
| Submitted | Cancelled | Cancel |

Запрещены обычным save-потоком:

```text
0 → 2
1 → 0
2 → любое изменение
```

Например, Framework прямо выбрасывает ошибку при попытке вернуть Submitted документ обратно в Draft.

---

## 5. Почему нельзя просто изменить `docstatus` руками

Наивная идея:

```python
doc.docstatus = 1
doc.save()
```

может выглядеть как обычное изменение поля.

Но во время сохранения Frappe:

1. загружает предыдущую версию документа;
2. сравнивает старый и новый `docstatus`;
3. определяет действие;
4. проверяет допустимость перехода;
5. проверяет permission;
6. вызывает соответствующие lifecycle hooks.

Поэтому `docstatus` нельзя воспринимать как обычный Integer.

---

## 6. Что делает `doc.submit()`

Публичный метод:

```python
doc.submit()
```

внутри вызывает:

```text
_submit()
   ↓
set docstatus = 1
   ↓
save()
```

Но основная логика происходит уже внутри обычного Document save lifecycle.

При переходе:

```text
0 → 1
```

Frappe определяет действие:

```text
submit
```

и проверяет право:

```text
Submit
```

---

## 7. Server-side последовательность Submit

Для Submit в Frappe 16 controller lifecycle выглядит концептуально так:

```text
before_validate
      ↓
validate
      ↓
before_submit
      ↓
DB update
(docstatus = 1)
      ↓
on_update
      ↓
on_submit
      ↓
on_change
```

Это важный момент.

`before_submit` и `on_submit` — не одно и то же.

### `before_submit`

Запускается **до фиксации Submit**.

Здесь удобно:

```text
проверять обязательные бизнес-условия
останавливать Submit через frappe.throw()
досчитывать значения
```

Пример:

```python
class Contract(Document):
    def before_submit(self):
        if not self.approved_by:
            frappe.throw("Approval is required")
```

### `on_submit`

Запускается после успешного изменения состояния на Submitted.

Обычно используется для действий, которые должны происходить вследствие подтверждения документа.

---

## 8. Почему `validate` выполняется при Submit

В Frappe 16 при действии `submit` выполняются:

```text
before_validate
validate
before_submit
```

То есть обычная validation не исчезает только потому, что документ уже был сохранён как Draft.

Это логично:

```text
Draft мог существовать долго
        ↓
перед окончательным подтверждением
условия должны быть проверены ещё раз
```

---

## 9. Submitted документ больше не является обычным редактируемым документом

После Submit:

```text
docstatus = 1
```

и Framework защищает документ от обычного изменения.

Идея:

```text
Draft
= рабочая версия

Submitted
= подтверждённая версия
```

Поэтому нельзя просто открыть Submitted документ и свободно поменять любое поле.

---

## 10. `Allow on Submit`

Некоторые поля иногда действительно должны оставаться изменяемыми после Submit.

Для этого у DocField существует свойство:

```text
Allow on Submit
```

Если оно включено, такое поле может изменяться при:

```text
Update after Submit
```

Без этой настройки Framework сравнивает текущее значение с сохранённым и выбрасывает:

```text
UpdateAfterSubmitError
```

если поле изменилось.

---

## 11. Как Frappe проверяет Update after Submit

При сохранении документа:

```text
previous docstatus = 1
current docstatus  = 1
```

Framework определяет действие:

```text
update_after_submit
```

После этого вызывается специальная проверка:

```text
validate_update_after_submit()
```

Она сравнивает сохранённые значения с новыми.

Для каждого изменившегося поля проверяется:

```text
allow_on_submit == 1 ?
```

Если нет — изменение запрещается.

---

## 12. Child Table после Submit

Проверка распространяется и на дочерние документы.

То есть недостаточно поставить `Allow on Submit` только на отдельное поле child row и ожидать, что таблица станет полностью свободно редактируемой.

Frappe проверяет:

```text
parent Table field
+
поля child rows
```

Если само Table-поле разрешено для изменения после Submit, Framework допускает, в том числе, добавление новых child rows и затем проверяет допустимость конкретных полей.

---

## 13. Lifecycle Update after Submit

Для сохранения Submitted документа используется отдельная пара hooks:

```text
before_update_after_submit
        ↓
DB update
        ↓
on_update_after_submit
        ↓
on_change
```

То есть это **не обычный Save lifecycle**.

Например:

```python
class Contract(Document):
    def before_update_after_submit(self):
        pass

    def on_update_after_submit(self):
        pass
```

---

## 14. Когда `Allow on Submit` использовать нормально

Хорошие кандидаты:

```text
служебная заметка после подтверждения
внешний reference number
дата получения оригинала
технический комментарий
```

То есть поля, которые:

```text
не меняют смысл подтверждённого документа
```

Плохой кандидат:

```text
сумма
контрагент
предмет документа
ключевые позиции
```

Если изменение превращает подтверждённый документ фактически в другой документ, обычно нужен Cancel + Amend, а не `Allow on Submit`.

---

## 15. Что делает Cancel

Для Submitted документа:

```python
doc.cancel()
```

внутри выполняется:

```text
set docstatus = 2
      ↓
save()
```

Разрешённый переход:

```text
1 → 2
```

Framework определяет действие:

```text
cancel
```

и проверяет право:

```text
Cancel
```

---

## 16. Server-side последовательность Cancel

В Frappe 16 Cancel идёт по отдельному lifecycle:

```text
before_cancel
     ↓
DB update
(docstatus = 2)
     ↓
on_cancel
     ↓
проверка back links
     ↓
on_change
```

Обрати внимание:

```text
validate
```

не является обычным этапом Cancel lifecycle.

Для специальных проверок отмены существует:

```python
before_cancel(self)
```

---

## 17. Зачем нужен `before_cancel`

Например, можно запретить отмену при определённом условии:

```python
class Contract(Document):
    def before_cancel(self):
        if self.locked:
            frappe.throw("Locked document cannot be cancelled")
```

Это правильнее, чем пытаться засовывать cancel-specific логику в обычный `validate()`.

---

## 18. Cancel не равен Delete

Это принципиально разные операции.

### Cancel

```text
Document остаётся в базе
name сохраняется
docstatus становится 2
история сохраняется
его можно использовать как источник Amendment
```

### Delete

```text
Document удаляется
```

Поэтому для формальных документов обычно важно различать:

```text
"документ признан недействительным"
```

и:

```text
"запись физически удалена"
```

---

## 19. Cancelled документ нельзя редактировать

Если документ уже имеет:

```text
docstatus = 2
```

обычная попытка редактирования отклоняется.

В исходном коде transition validation прямо возвращает ошибку:

```text
Cannot edit cancelled document
```

Идея очень простая:

```text
Cancelled
= исторически существовавший, но отменённый документ
```

Он уже не является рабочей версией.

---

## 20. Что такое Amendment

Если Submitted документ оказался неправильным, правильный lifecycle часто выглядит так:

```text
Submitted
    ↓
 Cancel
    ↓
Cancelled
    ↓
 Amend
    ↓
New Draft
```

То есть Framework не возвращает старую запись обратно в Draft.

Вместо этого создаётся **новый документ**.

---

## 21. Поле `amended_from`

Когда DocType помечается как Submittable, Frappe автоматически добавляет поле:

```text
amended_from
```

Тип:

```text
Link → тот же DocType
```

Настройки поля в v16 включают:

```text
Read Only
Print Hide
No Copy
Search Index
```

Пример:

```text
CONTRACT-0001
    docstatus = 2

CONTRACT-0001-1
    docstatus = 0
    amended_from = CONTRACT-0001
```

Конкретный `name` новой версии зависит от Naming механизма DocType.

---

## 22. Amendment — это новая запись

Это очень важная модель:

```text
не:
старый документ снова стал Draft
```

а:

```text
старый документ остаётся Cancelled
+
создаётся новый Draft
```

Связь сохраняется через:

```text
amended_from
```

Поэтому история не теряется.

---

## 23. Почему Amendment лучше прямого редактирования

Допустим подтверждён договор:

```text
Contract A
amount = 100000
Submitted
```

Потом выяснилось:

```text
amount должен быть 120000
```

Если просто изменить исходный документ:

```text
история фактически переписывается
```

При Amendment остаётся цепочка:

```text
Contract A
Cancelled
amount = 100000

        ↓ amended_from

Contract B
Draft / затем Submitted
amount = 120000
```

То есть видно:

```text
что было подтверждено раньше
что отменили
какая версия заменила её
```

---

## 24. Право `Amend`

В Role Permission Manager для Submittable DocType существуют отдельные права:

```text
Submit
Cancel
Amend
```

Это значит, что пользователь может, например:

```text
читать документ
но не Submit
```

или:

```text
Submit
но не Cancel
```

или:

```text
Cancel
но не создавать Amendment
```

Это независимые permission capabilities.

---

## 25. `Discard` в Frappe 16

В v16 есть ещё одно действие:

```text
Discard
```

Оно применимо только к Draft.

Метод:

```python
doc.discard()
```

проверяет:

```text
document is Draft
+
Write permission
```

после чего устанавливает:

```text
docstatus = 2
```

через `db_set()` и запускает:

```text
before_discard
on_discard
```

То есть появляется отдельный путь:

```text
Draft
  │
  │ Discard
  ▼
Cancelled
```

Но это **не обычный `0 → 2` Save transition**.

Это специальная операция Framework.

---

## 26. Cancel и Discard — не одно и то же

### Cancel

Исходное состояние:

```text
Submitted
```

Переход:

```text
1 → 2
```

Hooks:

```text
before_cancel
on_cancel
```

Permission:

```text
Cancel
```

### Discard

Исходное состояние:

```text
Draft
```

Результат:

```text
0 → 2
```

Hooks:

```text
before_discard
on_discard
```

Permission:

```text
Write
```

Это разные операции и разные семантики.

---

## 27. Delete и lifecycle

`Delete` вообще находится за пределами обычной цепочки:

```text
Draft → Submitted → Cancelled
```

Delete означает физическое удаление Document через механизмы Frappe.

Для него существуют отдельные lifecycle hooks, например:

```text
on_trash
after_delete
```

Поэтому нельзя использовать понятия:

```text
Cancel
Discard
Delete
```

как взаимозаменяемые.

---

## 28. Зависимости могут блокировать Cancel

После `on_cancel` Frappe выполняет проверку back links.

Практический смысл:

```text
если на Submitted документ зависят другие активные документы,
его отмена может быть запрещена
```

Это защищает связанную цепочку документов от неконсистентного состояния.

Поэтому Cancel — не просто:

```sql
UPDATE ... SET docstatus = 2
```

---

## 29. Links на Cancelled документы

При обычной link validation Frappe умеет отдельно различать:

```text
несуществующая ссылка
```

и:

```text
ссылка на Cancelled документ
```

Для submittable-контекста попытка связать активный документ с отменённым может привести к:

```text
CancelledLinkError
```

Это ещё одна причина не использовать `docstatus` как декоративный флаг.

---

## 30. Submit / Cancel через Desk

На форме пользователь видит действия Framework, но браузер не является источником истины.

Например, Client Form умеет вызывать:

```javascript
frm.save('Submit')
frm.save('Cancel')
frm.save('Update')
```

Но сервер всё равно повторно проверяет:

```text
transition
permissions
validation
update-after-submit restrictions
```

Поэтому скрытие кнопки в браузере не является системой безопасности.

---

## 31. Submit / Cancel через Python

Основной API Document:

```python
doc = frappe.get_doc("Contract", "CONTRACT-0001")

doc.submit()
```

Отмена:

```python
doc.cancel()
```

Update after Submit выполняется через обычный save после изменения разрешённого поля:

```python
doc.reference_number = "EXT-42"
doc.save()
```

если поле разрешено через:

```text
Allow on Submit
```

---

## 32. Submit / Cancel через REST API

Frappe REST API v2 предоставляет Document methods, включая:

```text
submit
cancel
```

Концептуально:

```text
POST /api/v2/document/<doctype>/<name>/method/submit
POST /api/v2/document/<doctype>/<name>/method/cancel
```

Это означает:

> lifecycle является частью серверной модели документа и доступен не только через Desk.

---

## 33. Controller hooks: итоговая таблица

| Операция | До записи | После записи |
|---|---|---|
| Save Draft | `before_validate`, `validate`, `before_save` | `on_update`, `on_change` |
| Submit | `before_validate`, `validate`, `before_submit` | `on_update`, `on_submit`, `on_change` |
| Update after Submit | `before_update_after_submit` | `on_update_after_submit`, `on_change` |
| Cancel | `before_cancel` | `on_cancel`, `on_change` |
| Discard | `before_discard` | `on_discard` |

Эту таблицу важно запомнить хотя бы концептуально.

---

## 34. Где размещать бизнес-логику

Если условие должно проверяться всегда при обычном сохранении:

```python
validate()
```

Если только перед подтверждением:

```python
before_submit()
```

Если действие должно произойти после успешного Submit:

```python
on_submit()
```

Если нужно запретить Cancel:

```python
before_cancel()
```

Если нужно выполнить действие после Cancel:

```python
on_cancel()
```

Если разрешённые post-submit поля требуют специальной проверки:

```python
before_update_after_submit()
```

---

## 35. Не использовать Client Script как единственную защиту lifecycle

Плохой вариант:

```javascript
if (frm.doc.amount > 100000) {
    frappe.throw("Cannot submit")
}
```

Это может улучшать UX, но API или другой server-side путь не обязан проходить через этот браузерный код.

Если правило действительно обязательно:

```python
class Contract(Document):
    def before_submit(self):
        if self.amount > 100000:
            frappe.throw("Cannot submit")
```

Server-side lifecycle — источник истины.

---

## 36. Workflow и `docstatus`

Workflow может управлять переходами и при необходимости использовать состояния, связанные с Draft / Submitted / Cancelled.

Но это не делает Workflow и `docstatus` одним механизмом.

Концептуально:

```text
Workflow
= кто и через какие бизнес-переходы может менять состояние

 docstatus
= фундаментальный lifecycle Document
```

Workflow подробнее будет разобран отдельно.

---

## 37. Когда Submittable вообще нужен

Хороший кандидат:

```text
документ после подтверждения должен стать исторически фиксированным
его нельзя тихо переписать
ошибка исправляется через Cancel + Amendment
```

Например, концептуально:

```text
акт
заявление
утверждаемая запись
расчёт
официальный реестр операции
```

Плохой кандидат:

```text
обычная задача
черновая заметка
живой профиль
настройка
карточка, которую должны постоянно редактировать
```

Не нужно делать DocType Submittable только потому, что хочется кнопку «Закрыть».

---

## 38. Submittable против Workflow

Очень распространённая ошибка:

```text
"есть статусы → нужен Submittable"
```

Нет.

Если объект проходит:

```text
New → In Progress → Review → Done
```

это может быть обычный `status` или Workflow.

Submittable нужен, когда требуется другая семантика:

```text
Draft
→ подтверждён и зафиксирован
→ отменён, но история сохранена
→ при исправлении создаётся новая версия
```

---

## 39. Полная схема lifecycle

Для Submittable DocType полезно держать в голове такую модель:

```text
                     Save
              ┌───────────────┐
              │               │
              ▼               │
          ┌────────┐          │
          │ Draft  │──────────┘
          │   0    │
          └───┬────┘
              │
              │ Submit
              ▼
        ┌─────────────┐
        │ Submitted   │
        │      1      │
        └─────┬───────┘
              │ ▲
              │ │ Update after Submit
              │ │ only allowed fields
              │
              │ Cancel
              ▼
        ┌─────────────┐
        │ Cancelled   │
        │      2      │
        └─────┬───────┘
              │
              │ Amend
              ▼
        new Draft document
        amended_from = old document
```

Дополнительный специальный путь v16:

```text
Draft
  ↓ Discard
Cancelled
```

---

## 40. Контрольные вопросы

После этой главы нужно уметь ответить:

1. Какие значения имеет `docstatus`?
2. Чем `status` отличается от `docstatus`?
3. Какие обычные переходы `docstatus` разрешены?
4. Почему нельзя просто вернуть Submitted документ в Draft?
5. Какие hooks вызываются при Submit?
6. Какие hooks вызываются при Cancel?
7. Что такое Update after Submit?
8. Для чего нужен `Allow on Submit`?
9. Почему Amendment создаёт новую запись?
10. Для чего используется `amended_from`?
11. Чем Cancel отличается от Delete?
12. Чем Discard отличается от Cancel?
13. Почему Client Script не должен быть единственным enforcement lifecycle?
14. Когда DocType действительно стоит делать Submittable?

Если ответы ясны, базовая модель данных Frappe уже собрана целиком.

---

## Официальные источники

- [Types of DocType — Submittable](https://docs.frappe.io/framework/user/en/tutorial/types-of-doctype)
- [Controllers and lifecycle hooks](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [Form API](https://docs.frappe.io/framework/user/en/api/form)
- [REST API](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [Frappe v16 source: `frappe/model/docstatus.py`](https://github.com/frappe/frappe/blob/version-16/frappe/model/docstatus.py)
- [Frappe v16 source: `frappe/model/document.py`](https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py)
- [Frappe v16 source: `frappe/model/base_document.py`](https://github.com/frappe/frappe/blob/version-16/frappe/model/base_document.py)
- [Frappe v16 source: `DocType.make_amendable()`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/doctype/doctype.py)

---

Следующая глава: **Form View — как metadata DocType превращается в рабочую форму Desk**.