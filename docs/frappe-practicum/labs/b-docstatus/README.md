# Lab B. Draft / Submit / Cancel / Amend / DocStatus

Lab B изучает системный lifecycle Submittable Document отдельно от рабочего Workflow `Service Request`.

Для эксперимента временно создаём:

```text
Service Report
```

После лаборатории `Service Report` и его test Documents удаляются штатно.

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Главная граница

В курсе существуют три разных понятия:

```text
Service Request.status
= бизнес-состояние процесса

Workflow
= допустимые переходы между бизнес-состояниями

DocStatus
= системное состояние Submittable Document
```

Для `Service Request`:

```text
New
Accepted
In Progress
Resolved
Closed
```

Для Submittable `Service Report`:

```text
0 Draft
1 Submitted
2 Cancelled
```

Эти модели не смешиваются.

---

# 2. Preconditions

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
Developer Mode включён
working tree clean
```

---

# 3. Создать временный Service Report

Через `DocType → New`:

```text
Name:           Service Report
Module:         Facility Operations
Is Submittable: Yes
Track Changes:  Yes
```

Naming:

```text
Naming Rule: Expression
Auto Name:   SRPT-.#####
```

Frappe добавит служебный `amended_from`; вручную его не создаём.

---

# 4. Поля

| Label | Fieldname | Type | Mandatory | Allow on Submit |
|---|---|---|---:|---:|
| Service Request | `service_request` | Link → Service Request | Yes | No |
| Report Date | `report_date` | Date | Yes | No |
| Summary | `summary` | Small Text | Yes | No |
| Work Performed | `work_performed` | Text | No | No |
| Final Note | `final_note` | Small Text | No | Yes |

`Final Note` специально используется для проверки исключения `Allow on Submit`.

---

# 5. Создать Draft

Создать:

```text
Service Request: <существующий SR>
Report Date:     сегодня
Summary:         Initial service report
Work Performed:  Inspected equipment and restored operation.
```

Нажать только:

```text
Save
```

Проверить:

```text
DocStatus = 0
Draft
```

В Draft обычные поля можно редактировать.

Главный вывод:

```text
Save ≠ Submit
```

---

# 6. Submit

Нажать:

```text
Submit
```

После подтверждения:

```text
DocStatus = 1
Submitted
```

`docstatus` — системное поле Frappe, а не наш Select.

---

# 7. Submitted data зафиксированы

Попробовать изменить:

```text
Summary
Work Performed
Report Date
```

Обычное изменение полей без `Allow on Submit` должно быть запрещено для Submitted Document.

Это сильнее, чем `Service Request.status = Closed`: Submittable lifecycle имеет отдельную серверную семантику `docstatus`.

---

# 8. Allow on Submit

Изменить только:

```text
Final Note
```

Например:

```text
Customer informed after completion.
```

Сохранить.

Изменение должно пройти, потому что:

```text
final_note.allow_on_submit = Yes
```

Не раздавать `Allow on Submit` всем полям — иначе смысл Submit размывается.

---

# 9. Audit Trail

Посмотреть Timeline / Audit Trail.

Нужно различать:

```text
Track Changes
= аудит изменений

DocStatus
= lifecycle документа

Allow on Submit
= точечное исключение после Submit
```

---

# 10. Cancel

Нажать:

```text
Cancel
```

Получить:

```text
DocStatus = 2
Cancelled
```

`Cancel ≠ Delete`.

Cancelled Document остаётся частью истории.

---

# 11. Amend

На Cancelled документе выполнить:

```text
Amend
```

Frappe создаёт новый Draft:

```text
DocStatus = 0
Amended From = <cancelled Service Report>
```

Исправить `Summary`, сохранить и Submit новую версию.

Итоговая цепочка:

```text
old Service Report
→ Cancelled / docstatus 2
        │
        └── amended_from
                ↓
new Service Report
→ Draft 0
→ Submitted 1
```

История старой версии не переписывается.

---

# 12. Workflow vs DocStatus

## Service Request

```text
New
→ Accepted
→ In Progress
→ Resolved
→ Closed
```

Это бизнес-процесс. Все states курса имеют:

```text
docstatus = 0
```

## Service Report

```text
Draft 0
Submitted 1
Cancelled 2
```

Это системный lifecycle фиксации документа.

Не делаем `Service Request` Submittable только потому, что такая возможность существует.

---

# 13. Почему Service Request остаётся обычным Document

Для заявки нужен живой рабочий процесс и отдельный Workflow.

```text
New → Accepted → In Progress → Resolved → Closed
```

не является заменой:

```text
Draft → Submitted → Cancelled
```

и наоборот.

Lab B нужен именно для того, чтобы не применять `Is Submittable` механически ко всем рабочим документам.

---

# 14. Metadata vs working data

```text
Service Report DocType
→ Standard metadata
→ app source / Git

SRPT-... Documents
→ working data site
→ не Git
```

При желании сделать отдельный experiment commit:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git add .
git commit -m "Add temporary Service Report DocStatus lab"
```

---

# 15. Rollback

Перед удалением DocType удалить лабораторные Service Report Documents штатно, с учётом связей Cancelled/Amended.

Затем удалить:

```text
DocType → Service Report
```

штатным Delete.

Не использовать SQL или `rm -rf` как замену lifecycle.

После удаления:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status --short
git add -A
git commit -m "Remove temporary Service Report DocStatus lab"
git status
```

Если experiment commit не делался, достаточно убедиться, что финальный source снова соответствует baseline core.

---

# 16. Final state

В постоянном domain остаются:

```text
Facility Location
Equipment
Service Request
```

Не остаётся:

```text
Service Report
```

Workflow Service Request по-прежнему:

```text
New
Accepted
In Progress
Resolved
Closed
```

---

# 17. Приёмка

Ученик должен показать и объяснить:

```text
Save → Draft 0
Submit → Submitted 1
Cancel → Cancelled 2
Amend → новый Draft с amended_from
Allow on Submit → точечное поле, разрешённое после Submit
```

и ответить:

1. почему `DocStatus` не является `Service Request.status`;
2. почему Workflow и DocStatus решают разные задачи;
3. почему Submitted Document сильнее фиксирует данные, чем просто terminal Workflow State;
4. почему `Allow on Submit` нужно применять точечно;
5. почему `Service Request` в базовой архитектуре не Submittable.

После rollback лаборатория не оставляет новую постоянную domain entity.
