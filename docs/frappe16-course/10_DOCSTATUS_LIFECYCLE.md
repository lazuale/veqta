# 10. `docstatus`, Submit, Cancel и Amendment

`docstatus` — это системное состояние документа во Frappe. Оно нужно не каждому DocType, но для `Submittable` документов определяет очень важный lifecycle.

В этой главе разберём его на простом примере и только потом посмотрим на controller events.

Проверено: **2026-08-30**.

## 1. Три значения `docstatus`

Во Frappe 16 используются три состояния:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Их можно представить так:

```text
Draft
  ↓ Submit
Submitted
  ↓ Cancel
Cancelled
```

`docstatus` — системное поле Framework, а не обычный `Select`.

## 2. `status` и `docstatus` — не одно и то же

Пусть у документа есть обычное поле:

```text
status = Approved
```

и одновременно:

```text
docstatus = 0
```

Это возможно.

Почему? Потому что они отвечают на разные вопросы.

### `status`

Бизнес-состояние, которое придумало приложение:

```text
New
In Review
Approved
Rejected
Closed
```

### `docstatus`

Системное состояние Frappe:

```text
Draft
Submitted
Cancelled
```

Пример:

```text
status = Approved

docstatus = 1  # Submitted
```

То есть документ и по бизнес-логике Approved, и технически подтверждён через Submit.

## 3. Пример целиком

Представим DocType `Approval Record`.

Пока его готовят:

```text
APR-0001
Subject: Проверка оборудования
Result: Approved
docstatus: Draft
```

Пользователь может исправлять поля и нажимать Save.

Когда запись окончательно подтверждена:

```text
Submit
```

Frappe переводит её в:

```text
docstatus = 1
```

После этого документ уже не считается обычным редактируемым черновиком.

## 4. Какие переходы разрешены

В обычном lifecycle Framework разрешает такие переходы:

| Было | Стало | Что происходит |
|---|---|---|
| Draft `0` | Draft `0` | обычный Save |
| Draft `0` | Submitted `1` | Submit |
| Submitted `1` | Submitted `1` | ограниченное Update after Submit |
| Submitted `1` | Cancelled `2` | Cancel |

А вот такие переходы обычным Save не допускаются:

```text
Draft → Cancelled
Submitted → Draft
Cancelled → Submitted
```

То есть нельзя просто поменять число `docstatus` как обычное поле и считать задачу решённой.

## 5. Save и Submit — разные действия

### Save

Сохраняет Draft:

```text
docstatus = 0
```

Документ остаётся рабочим черновиком.

### Submit

Переводит его в:

```text
docstatus = 1
```

и запускает отдельный lifecycle подтверждения.

Поэтому Submit стоит использовать только там, где предметный смысл действительно требует фиксации документа.

## 6. Что вызывает Submit в controller

Для Submit важные server-side hooks идут примерно так:

```text
before_validate
validate
before_submit
        ↓
сохранение документа с docstatus = 1
        ↓
on_update
on_submit
on_change
```

Для первого знакомства достаточно помнить три основных события:

```text
validate
before_submit
on_submit
```

Например:

```python
class ApprovalRecord(Document):
    def before_submit(self):
        # последняя проверка перед подтверждением
        pass

    def on_submit(self):
        # действия после успешного Submit
        pass
```

Подробно controller lifecycle будет отдельной главой.

## 7. После Submit документ становится почти read-only

Обычные поля подтверждённого документа менять нельзя.

Это защищает смысл Submit: если после подтверждения всё можно свободно переписать, само подтверждение мало что означает.

Пример:

```text
Amount = 1000
```

после Submit не должно тихо превратиться в:

```text
Amount = 5000
```

обычным Save.

## 8. Allow on Submit

Иногда после Submit всё же нужно разрешить менять отдельное служебное поле.

Например:

```text
Internal Note
```

Для такого DocField можно включить:

```text
Allow on Submit = ✓
```

Тогда Frappe разрешит Update after Submit именно для таких полей.

При этом ключевые реквизиты без этого флага останутся защищены.

## 9. Что проверяет Frappe при Update after Submit

Framework сравнивает текущие значения с сохранённым документом.

Если изменилось поле без `Allow on Submit`, Frappe выбросит ошибку `UpdateAfterSubmitError`.

Это server-side проверка, а не просто «серое поле в браузере».

То же относится к child rows: возможность изменять дочернюю таблицу после Submit зависит от соответствующих `allow_on_submit` настроек.

## 10. Cancel

`Cancel` переводит Submitted документ в:

```text
docstatus = 2
```

Это не удаление записи.

Документ остаётся в системе, но отмечен как отменённый.

Пример:

```text
APR-0001
Submitted
```

после Cancel:

```text
APR-0001
Cancelled
```

История существования документа сохраняется.

## 11. Hooks при Cancel

Основные controller events:

```text
before_cancel
        ↓
сохранение docstatus = 2
        ↓
on_cancel
on_change
```

Пример:

```python
class ApprovalRecord(Document):
    def before_cancel(self):
        # проверить, можно ли отменять
        pass

    def on_cancel(self):
        # откатить последствия Submit, если они были
        pass
```

## 12. Почему Cancel иногда не проходит

Документ может быть связан с другими записями так, что его отмена нарушит целостность процесса.

Framework проверяет связанные документы и back links.

Простой сценарий:

```text
Document A был Submitted
Document B уже ссылается на него как на действующий подтверждённый документ
```

Cancel A может потребовать сначала разобраться с B.

Именно поэтому Cancel — бизнес-операция, а не просто установка `docstatus = 2`.

## 13. Cancelled документ нельзя нормально редактировать

После:

```text
docstatus = 2
```

обычный save запрещён.

Если в отменённом документе была ошибка и нужен исправленный вариант, штатный путь — **Amendment**, а не возврат старого документа обратно в Draft.

## 14. Amendment — новая исправленная версия

Представим:

```text
APR-0001
Submitted
```

Выяснилось, что в нём ошибка.

Штатная логика:

```text
APR-0001
Submit
   ↓
Cancel
   ↓
Amend
   ↓
новый Draft
```

Новый документ получает ссылку на исходный через поле:

```text
amended_from
```

Например:

```text
APR-0001-1
amended_from = APR-0001
```

Точный naming amended document зависит от naming поведения DocType, но принцип один: **создаётся новый Document**.

## 15. Откуда берётся `amended_from`

Для Submittable DocType Frappe сам добавляет поле `amended_from`, если его ещё нет.

Оно является Link на тот же DocType и показывает, какой отменённый документ послужил основой новой версии.

Это полезнее, чем «стереть прошлое и переписать старую запись».

## 16. Amend — не Undo

После Amend исходный документ остаётся:

```text
Cancelled
```

Новый документ начинается как:

```text
Draft
```

И его нужно снова проверить и Submit, если он должен стать действующим.

То есть:

```text
старый документ → история
новый документ  → исправленная версия
```

## 17. Permissions для Submittable DocType

У ролей могут быть отдельные права:

```text
Read
Write
Create
Submit
Cancel
Amend
```

Например:

```text
Operator
- Create
- Read
- Write

Manager
- Read
- Submit
- Cancel
- Amend
```

Так можно отделить подготовку документа от его подтверждения.

## 18. Workflow и Submit

Workflow может управлять бизнес-переходами и в определённых состояниях использовать системные действия Submit/Cancel.

Например:

```text
Draft
  ↓ Send for Review
Review
  ↓ Approve
Approved + Submit
```

Но Workflow не отменяет смысл `docstatus`. Это дополнительный слой процесса.

## 19. Cancel, Discard и Delete — три разных действия

Их легко перепутать.

### Cancel

Для Submitted документа:

```text
Submitted → Cancelled
```

Запись остаётся в системе.

### Discard

В v16 есть отдельное действие `Discard` для Draft: оно переводит черновик в cancelled-like состояние через специальный lifecycle `before_discard` / `on_discard`.

Смысл — отказаться от Draft, не делая обычный Submit → Cancel.

### Delete

Физически удаляет Document через штатный delete lifecycle, если это разрешено permissions и связями.

На пальцах:

```text
Cancel  → «этот подтверждённый документ отменён»
Discard → «этот черновик больше не нужен»
Delete  → «удалить запись»
```

Это разные семантики.

## 20. Submit в Python

Document API даёт методы:

```python
doc.submit()
```

и:

```python
doc.cancel()
```

Они запускают штатный lifecycle.

Не нужно заменять их прямым SQL UPDATE `docstatus`, иначе будут пропущены permissions, validations, hooks и связанные проверки.

## 21. Submit через REST

REST API работает поверх Document-модели Frappe, а whitelisted методы позволяют выполнять серверные действия.

Конкретные способы вызова API разберём в отдельном блоке. Здесь нужно запомнить принцип:

> Каким бы интерфейсом ты ни работал — Desk, Python или API — системный lifecycle документа должен оставаться одним и тем же.

## 22. Когда Submittable вообще нужен

Не каждый документ надо Submit-ить.

Хороший кандидат:

```text
документ проходит этап подготовки,
после подтверждения должен считаться зафиксированным,
а исправление требует явной отмены/новой версии
```

Плохой кандидат:

```text
обычная задача, заметка или справочник,
которые просто меняются по ходу работы
```

Для них обычного Save и бизнес-статуса часто достаточно.

## Мини-практика

Представь `Approval Record`.

1. Создали и заполняем → `docstatus = 0` **Draft**.
2. Руководитель подтвердил → `Submit`, `docstatus = 1`.
3. Нужно добавить только служебную заметку → поле должно иметь **Allow on Submit**.
4. Нашли серьёзную ошибку → **Cancel → Amend → новый Draft**.
5. Хотим вернуть старый Cancelled Document в Draft простым Save → **так делать нельзя**.

## Что запомнить

- `docstatus` — системное состояние, `status` — обычное бизнес-поле.
- `Submit` переводит `0 → 1` и запускает отдельный lifecycle.
- После Submit можно менять только специально разрешённые поля.
- `Cancel` переводит `1 → 2`, но не удаляет документ.
- `Amend` создаёт новый Draft, связанный с отменённым документом через `amended_from`.
- `Cancel`, `Discard` и `Delete` имеют разный смысл.

## Официальные источники

- [Document API](https://docs.frappe.io/framework/user/en/api/document)
- [DocStatus source, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/model/docstatus.py)
- [Document lifecycle implementation, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py)
- [DocType `amended_from` creation, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/doctype/doctype.py)

Следующая глава: **11. Form View**.