# S06. Зафиксировать окончательное согласование через Submit

До S06 `PLT Approved` означал только состояние процесса:

```text
status    = PLT Approved
docstatus = 0
```

Теперь появляется новое требование:

> После окончательного согласования заявка считается зафиксированным разрешением и не должна переписываться обычным Draft Save как будто решения ещё не было.

Для этого используется системный жизненный цикл Document во Frappe.

## 1. Сначала очистить несовместимые учебные записи

До этого этапа на dev Site уже есть заявки:

```text
status = PLT Approved
docstatus = 0
```

После изменения Workflow то же состояние будет означать:

```text
status = PLT Approved
docstatus = 1
```

Старые контрольные записи не нужно «чинить» SQL. Это временные данные dev Site, созданные только для предыдущих упражнений.

Посмотрите существующие заявки:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
for row in frappe.get_all(
    "Purchase Request",
    fields=["name", "status", "docstatus", "owner"],
    order_by="creation asc",
):
    print(row)
```

Если Site используется только для этого практикума, удалите контрольные Purchase Requests штатным способом через Frappe:

```python
frappe.set_user("Administrator")
for name in frappe.get_all("Purchase Request", pluck="name"):
    frappe.delete_doc("Purchase Request", name)
frappe.db.commit()
exit()
```

Не используйте:

```text
UPDATE tabPurchase Request SET docstatus = ...
ручное изменение docstatus в БД
patch только ради временных учебных данных
```

В рабочей системе с реальными данными такое изменение потребовало бы отдельной миграции данных. В учебном dev Site сохранять контрольные записи предыдущих этапов не требуется.

## 2. Включить Is Submittable

Откройте Standard DocType `Purchase Request` и включите:

```text
Is Submittable : yes
```

Сохраните DocType.

Frappe добавляет Standard field `amended_from` для submittable DocType. Его не нужно создавать вручную.

Проверьте metadata в Git:

```bash
cd ~/frappe/rental-training-bench

git -C apps/purchase_lifecycle_training diff -- \
  purchase_lifecycle_training/purchase_lifecycle_training/doctype/purchase_request/purchase_request.json
```

## 3. Выдать Submit только согласующим

В Permissions `Purchase Request` измените только `Submit`:

```text
PLT Requester        Submit no
PLT Approver         Submit yes
PLT Senior Approver  Submit yes
```

Почему Submit нужен обеим ролям согласования:

```text
маленькая заявка → окончательное решение принимает PLT Approver
большая заявка   → окончательное решение принимает PLT Senior Approver
```

Requester не получает Submit, потому что он не выполняет окончательное согласование.

## 4. Изменить docstatus только у Approved

Откройте Workflow `PLT Purchase Request Approval`.

Измените строку состояния:

```text
PLT Approved
Doc Status: 0 → 1
```

Остальные текущие состояния остаются:

```text
PLT Draft             0
PLT Pending Approval  0
PLT Rejected          0
PLT Pending Senior    0
PLT Approved          1
```

Сохраните Workflow.

В v16.33.0 `apply_workflow()` смотрит `docstatus` следующего Workflow State и для перехода:

```text
Draft 0 → Submitted 1
```

вызывает штатный `doc.submit()`.

Источник: [`frappe/model/workflow.py`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/workflow.py).

## 5. Не включать status.Allow on Submit

Поле `status` должно остаться:

```text
No Copy         : yes
Allow on Submit : no
```

На этом этапе состояние меняется одновременно с переходом Draft → Submitted через `doc.submit()`.

`Allow on Submit` нужен, когда поле должно изменяться уже после Submit у существующего Submitted Document. Такого требования у нас нет.

## 6. Проверить малую заявку

Создайте новый Document под Requester:

```text
Subject          : Office chair
Requested Amount : 500
Needed By        : будущая дата
```

Пройдите:

```text
Requester:
PLT Draft → PLT Pending Approval

Approver:
Approve
```

Ожидается:

```text
status    = PLT Approved
docstatus = 1
```

Проверьте через console:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
row = frappe.get_all(
    "Purchase Request",
    filters={"subject": "Office chair"},
    fields=["name", "status", "docstatus"],
    limit=1,
)[0]
print(row)
exit()
```

## 7. Проверить большую заявку

Создайте:

```text
Subject          : Team laptop
Requested Amount : 1500
```

Маршрут:

```text
Requester
→ PLT Pending Approval

PLT Approver
→ PLT Pending Senior

PLT Senior Approver
→ PLT Approved
```

Финальный результат снова:

```text
docstatus = 1
```

Оба маршрута согласования заканчиваются одинаково: окончательно согласованный Document становится Submitted.

## 8. Проверить права, а не только кнопки

Под Requester убедитесь, что у него нет права Submit.

Approver и Senior должны получать Submit только потому, что именно их переходы завершают согласование.

Не выдавайте сейчас:

```text
Cancel
Amend
```

Техническая возможность Submittable Document поддерживать Cancel и Amend ещё не означает, что эти операции уже разрешены текущими бизнес-требованиями.

## Результат

После S06:

```text
Purchase Request = Is Submittable
PLT Approved      = docstatus 1
маленькая заявка  = Submit через PLT Approver
большая заявка    = Submit через PLT Senior Approver
Requester         = no Submit
amended_from      = Standard field Framework
status Allow on Submit = no
```

Следующий этап: [`S07A_CANCEL.md`](S07A_CANCEL.md).
