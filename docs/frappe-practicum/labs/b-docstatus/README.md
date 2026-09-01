# Lab B. Draft / Submit / Cancel / Amend / DocStatus

Lab B — отдельная лаборатория по жизненному циклу submittable-документа.

Она **не меняет жизненный цикл `Service Request`**.

Для эксперимента создаём временный Standard DocType:

```text
Service Report
```

После лаборатории `Service Report` удаляется штатно, чтобы постоянное ядро курса снова состояло только из:

```text
Facility Location
Equipment
Service Request
```

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Что изучаем

В этой лаборатории нужны штатные механизмы:

```text
Is Submittable
DocStatus
Draft
Submit
Update After Submit
Allow on Submit
Cancel
Amend
Amended From
Audit Trail
```

Никакого Workflow для `Service Report` не создаём.

Задача лаборатории — увидеть разницу между:

```text
бизнес-статусом
Workflow State
DocStatus
```

---

# 2. Базовая модель DocStatus

В Frappe `DocStatus` имеет три значения:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Это системное состояние документа, а не наше поле `Status`.

Для обычного `Service Request` из основного курса мы оставили обычный lifecycle и Workflow.

В Lab B специально создаём другой документ, которому естественно подходит фиксация факта:

```text
черновик отчёта
→ подтверждённый отчёт
→ отменённый отчёт
→ исправленная версия
```

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
Developer Mode включён
Git working tree clean
```

---

# 4. Создать временный Standard DocType

Войти под:

```text
Administrator
```

Через Awesomebar открыть:

```text
DocType
```

Нажать:

```text
New
```

Создать:

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

Сохранить.

После включения `Is Submittable` Frappe добавляет системное поле:

```text
amended_from
```

Его вручную создавать не нужно.

---

# 5. Добавить поля Service Report

Добавить поля в таком порядке:

| Label | Fieldname | Type | Mandatory | Allow on Submit |
|---|---|---|---|---|
| Service Request | service_request | Link → Service Request | Yes | No |
| Report Date | report_date | Date | Yes | No |
| Summary | summary | Small Text | Yes | No |
| Work Performed | work_performed | Text | No | No |
| Final Note | final_note | Small Text | No | Yes |

Для `Service Request`:

```text
Options = Service Request
```

Для `Final Note` включить:

```text
Allow on Submit = Yes
```

Остальные поля после Submit должны стать фактически зафиксированными.

Сохранить DocType.

---

# 6. Проверить generated metadata

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

find facility_ops/facility_operations/doctype/service_report -maxdepth 1 -type f -print

git status --short
```

Должны появиться файлы Standard DocType.

Рабочих `Service Report` в Git пока нет.

---

# 7. Создать первый Draft

Через Awesomebar открыть:

```text
Service Report
```

Создать документ:

```text
Service Request: <любая существующая заявка>
Report Date:     <сегодня>
Summary:         Initial service report
Work Performed:  Inspected equipment and restored operation.
Final Note:      <пусто>
```

Нажать:

```text
Save
```

Не нажимать Submit.

---

# 8. Проверить Draft

После обычного Save документ остаётся:

```text
DocStatus = 0
Draft
```

В Draft изменить:

```text
Summary
Work Performed
Report Date
```

Сохранить.

Все обычные поля должны редактироваться.

Главный вывод:

```text
Save
≠
Submit
```

`Save` сохраняет текущий черновик, но не фиксирует его как подтверждённый документ.

---

# 9. Проверить Timeline до Submit

Открыть Timeline документа.

Так как включён:

```text
Track Changes = Yes
```

изменения Draft должны быть видны в истории.

Не создаём собственный журнал изменений.

---

# 10. Выполнить Submit

На форме `Service Report` нажать:

```text
Submit
```

Подтвердить действие.

После Submit:

```text
DocStatus = 1
Submitted
```

Это не значение отдельного пользовательского поля.

Frappe меняет системный `docstatus` документа.

---

# 11. Проверить, что обычные поля зафиксированы

После Submit попробовать изменить:

```text
Summary
```

или:

```text
Work Performed
```

Попытка сохранения не должна разрешить обычное изменение этих полей после Submit.

Это принцип submittable-документа:

```text
Submitted
→ подтверждённые данные больше нельзя тихо переписать
```

---

# 12. Проверить Allow on Submit

Теперь изменить только:

```text
Final Note
```

Например:

```text
Customer informed after completion.
```

Сохранить.

Изменение должно пройти, потому что для `final_note` явно включено:

```text
Allow on Submit = Yes
```

Именно это поле разрешено менять после Submit.

Не включать `Allow on Submit` на все поля подряд.

Иначе смысл фиксации документа исчезает.

---

# 13. Проверить Audit Trail

После изменения `Final Note` открыть Timeline / Audit Trail.

Нужно увидеть:

```text
создание Draft
изменения Draft
Submit
изменение разрешённого поля после Submit
```

Главный вывод:

```text
Track Changes
+
DocStatus
+
Allow on Submit
```

дают штатный контролируемый lifecycle без собственного audit-модуля.

---

# 14. Выполнить Cancel

На Submitted документе нажать:

```text
Cancel
```

Подтвердить.

После этого:

```text
DocStatus = 2
Cancelled
```

Cancelled — не удалённый документ.

Он остаётся в системе как отменённая версия.

---

# 15. Не путать Cancel и Delete

Зафиксировать различие:

```text
Cancel
→ документ остаётся
→ docstatus = 2
→ история сохраняется

Delete
→ удаление документа
```

Для подтверждённых учётных документов Cancel обычно важнее удаления, потому что сохраняет факт существования исходной версии.

---

# 16. Выполнить Amend

На Cancelled документе нажать:

```text
Amend
```

Frappe создаст новый Draft на основе отменённого документа.

В новом документе проверить:

```text
DocStatus = 0
Amended From = <номер отменённого Service Report>
```

Поле `amended_from` было добавлено Frappe автоматически из-за:

```text
Is Submittable = Yes
```

---

# 17. Исправить amended document

В новой версии изменить, например:

```text
Summary:
Corrected service report
```

и при необходимости:

```text
Work Performed
```

Сохранить.

Получаем цепочку:

```text
старый документ
DocStatus = 2 Cancelled
        │
        └── amended_from
                ↓
новый документ
DocStatus = 0 Draft
```

---

# 18. Submit исправленную версию

Нажать:

```text
Submit
```

Новая версия должна перейти:

```text
Draft 0
→ Submitted 1
```

Старая версия при этом остаётся:

```text
Cancelled 2
```

Frappe не переписывает историю старого подтверждённого документа.

---

# 19. Сравнить Workflow и DocStatus

Теперь сравнить два уже изученных механизма.

## Service Request

```text
Status:
New
Assigned
In Progress
Resolved
Closed

Workflow управляет бизнес-процессом.
```

## Service Report

```text
DocStatus:
0 Draft
1 Submitted
2 Cancelled

DocStatus управляет фиксацией документа.
```

Это разные оси.

Не нужно автоматически делать любой рабочий документ `Is Submittable` только потому, что Frappe умеет Submit.

---

# 20. Почему Service Request не делаем Submittable

Для `Service Request` нужен живой процесс:

```text
New
→ Assigned
→ In Progress
→ Resolved
→ Closed
```

Заявку нормально редактировать по мере работы.

Принудительный lifecycle:

```text
Draft
→ Submitted
→ Cancelled
```

не даёт нам полезной предметной модели для заявки.

Поэтому `Is Submittable` изучается отдельно на `Service Report`.

---

# 21. Проверить системный docstatus из List View

Открыть список `Service Report`.

Должны существовать как минимум:

```text
Cancelled исходная версия
Submitted amended версия
```

Использовать стандартный фильтр `DocStatus`, если он доступен в List View.

Проверить отдельно:

```text
Draft
Submitted
Cancelled
```

---

# 22. Проверить metadata и data

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Нужно понимать:

```text
Service Report DocType
→ Standard metadata
→ source app
→ Git

Service Report Documents
→ working data текущего site
→ не Git
```

`Submit`, `Cancel` и `Amend` не создают source-файлы для каждого документа.

---

# 23. Зафиксировать эксперимент отдельным commit

Пока `Service Report` существует, сделать commit:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git add .
git commit -m "Add temporary Service Report DocStatus lab"
```

Так в истории Git останется полноценный пример submittable DocType.

---

# 24. Удалить тестовые Service Report Documents

Перед удалением DocType удалить рабочие тестовые документы штатно через Desk.

Если есть связанная цепочка Cancelled → Amended, удалять в порядке, который разрешает Frappe с учётом ссылочной целостности.

Не удалять строки напрямую SQL-командами.

Цель — использовать штатный lifecycle и штатное удаление Documents.

---

# 25. Удалить временный Service Report

Через Awesomebar открыть:

```text
DocType
```

Открыть:

```text
Service Report
```

Удалить DocType штатно.

Проверить, что файлы:

```text
facility_ops/facility_operations/doctype/service_report/
```

удалились из source app.

---

# 26. Commit очистки

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git add -A
git commit -m "Remove temporary Service Report DocStatus lab"
```

Теперь Git history хранит эксперимент, но текущее приложение снова не содержит `Service Report`.

---

# 27. Финальная проверка ядра

В Desk должны оставаться постоянными предметными DocType:

```text
Facility Location
Equipment
Service Request
```

Не должны оставаться:

```text
Service Report
```

Lab B закончена только после этой очистки.

---

# 28. Что нужно уметь объяснить после лаборатории

Без подсказки объяснить:

```text
что такое DocStatus
чем Save отличается от Submit
что означает 0 / 1 / 2
зачем нужен Is Submittable
почему Submitted document нельзя свободно переписывать
что делает Allow on Submit
чем Cancel отличается от Delete
что делает Amend
зачем нужен amended_from
чем DocStatus отличается от Workflow State
почему не каждый DocType должен быть Submittable
```

---

# 29. Приёмка Lab B

Лаборатория принята, если ученик реально проделал цепочку:

```text
создал Service Report
      ↓
Save
      ↓
Draft / docstatus 0
      ↓
Submit
      ↓
Submitted / docstatus 1
      ↓
попытался изменить обычное поле
      ↓
получил запрет
      ↓
изменил Final Note с Allow on Submit
      ↓
Cancel
      ↓
Cancelled / docstatus 2
      ↓
Amend
      ↓
новый Draft + amended_from
      ↓
Submit исправленной версии
      ↓
удалил тестовые Documents
      ↓
удалил временный Service Report
      ↓
ядро снова состоит из трёх DocType
```

И ученик понимает главный принцип:

```text
Workflow
= управление бизнес-состоянием

DocStatus
= фиксация жизненного цикла документа
```
