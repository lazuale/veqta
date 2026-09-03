# S01. Создать обычный Purchase Request без Workflow

На этом этапе системе нужно только хранить внутреннюю заявку и её текущее предметное состояние.

Требование пока звучит так:

> Пользователь создаёт заявку на закупку, указывает сумму и требуемую дату и видит, в каком состоянии находится заявка.

В этом требовании ещё нет правил вида «кто имеет право перевести заявку из одного состояния в другое». Поэтому начинаем не с Workflow, а с обычного Standard DocType и обычного `Select`.

Связанные материалы:

- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../REQUIREMENTS.md`](../REQUIREMENTS.md);
- [`../../../frappe-architecture-standard/02_DATA_MODEL.md`](../../../frappe-architecture-standard/02_DATA_MODEL.md);
- [`../../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md`](../../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md).

## 1. Проверить входное состояние

```bash
cd ~/frappe/rental-training-bench

bench --site purchase-lifecycle.localhost list-apps -f text
bench --site purchase-lifecycle.localhost show-config
```

Ожидается:

```text
frappe
purchase_lifecycle_training
```

и:

```text
developer_mode  1
```

## 2. Создать Standard DocType

Откройте Desk:

```text
http://purchase-lifecycle.localhost:8000/app
```

Найдите `DocType` и создайте новый.

Основные параметры:

```text
Name            : Purchase Request
Module          : Purchase Lifecycle Training
Custom?         : выключено
Is Child Table  : выключено
Is Single       : выключено
Is Submittable  : выключено
```

`Is Submittable` сейчас выключен намеренно. Пока нет требования фиксировать окончательное согласование через Submit, системный `docstatus` не нужен как часть процесса.

## 3. Добавить поля

### Subject

```text
Label        : Subject
Fieldname    : subject
Type         : Data
Mandatory    : yes
In List View : yes
```

### Description

```text
Label      : Description
Fieldname  : description
Type       : Small Text
Mandatory  : no
```

### Requested Amount

```text
Label        : Requested Amount
Fieldname    : requested_amount
Type         : Currency
Mandatory    : yes
In List View : yes
```

### Needed By

```text
Label        : Needed By
Fieldname    : needed_by
Type         : Date
Mandatory    : yes
In List View : yes
```

### Status

```text
Label        : Status
Fieldname    : status
Type         : Select
Mandatory    : yes
In List View : yes
Default      : PLT Draft
```

Options:

```text
PLT Draft
PLT Pending Approval
PLT Approved
PLT Rejected
```

Пока это обычные значения обычного `Select`.

Не создавайте:

```text
workflow_state
Workflow
Workflow State
Approval Log
requester
```

## 4. Почему requester не нужен

Каждый Frappe Document уже имеет системное поле `owner`.

В учебной модели заявка всегда создаётся самим заявителем, поэтому принимаем:

```text
requester = owner
```

Отдельный `Link → User` сейчас дублировал бы один и тот же смысл.

Если позднее понадобится создавать заявки от имени другого сотрудника, это будет новое требование и модель придётся пересмотреть.

## 5. Настроить naming

В секции Naming:

```text
Naming Rule : Expression
Auto Name   : PLT-PR-.#####
```

Ожидаемый вид:

```text
PLT-PR-00001
PLT-PR-00002
```

`name` остаётся стабильным идентификатором, а человекочитаемое название берём из `subject`.

В View Settings:

```text
Title Field               : subject
Show Title in Link Fields : yes
```

Официальное описание naming: https://docs.frappe.io/framework/user/en/basics/doctypes/naming

## 6. Сохранить DocType и проверить исходники App

После Save вернитесь в терминал:

```bash
cd ~/frappe/rental-training-bench

git -C apps/purchase_lifecycle_training status --short
```

Проверьте metadata:

```bash
test -f \
  apps/purchase_lifecycle_training/purchase_lifecycle_training/purchase_lifecycle_training/doctype/purchase_request/purchase_request.json \
  && echo 'Purchase Request metadata: OK'
```

Standard DocType должен появиться в исходниках App, а не существовать только в базе dev Site.

## 7. Создать контрольную заявку

Через Desk создайте:

```text
Subject          : Office chair
Description      : Ergonomic chair for workstation
Requested Amount : 500
Needed By        : любая будущая дата
Status           : PLT Draft
```

Сохраните документ.

Проверьте его `name` и `owner` через Bench Console:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
name = frappe.get_all("Purchase Request", pluck="name", limit=1)[0]
doc = frappe.get_doc("Purchase Request", name)
print(doc.name)
print(doc.owner)
print(doc.status)
print(doc.docstatus)
```

Ожидаемый смысл результата:

```text
name      = PLT-PR-00001 или следующий номер
owner     = пользователь, создавший Document
status    = PLT Draft
docstatus = 0
```

Выйдите из console:

```python
exit()
```

## 8. Увидеть важную границу

Сейчас у нас есть несколько значений состояния, но это ещё не основание для Workflow.

```text
нужно хранить состояние
→ status : Select
```

Workflow понадобится только тогда, когда возникнет отдельная ответственность:

```text
кто
из какого состояния
каким действием
в какое состояние
имеет право перейти
```

Поэтому результат S01 намеренно простой:

```text
Purchase Request = обычный Document
status           = обычное предметное состояние
docstatus        = 0
Workflow         = отсутствует
```

Следующий этап: [`S02_PERMISSIONS_AND_STATUS_LIMIT.md`](S02_PERMISSIONS_AND_STATUS_LIMIT.md).
