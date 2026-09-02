# 03. Document Lifecycle — где должна жить логика

## 1. Controller — владелец поведения своего DocType

**[FRAPPE DOCS]** Controller — Python class DocType, наследующий `frappe.model.document.Document`.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers

**[UPSTREAM]** `frappe/model/document.py` показывает, что `Document.save()` и `insert()` выполняют permission checks, validation и lifecycle methods.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py

Это означает: Controller — не случайное место, куда «удобно положить код», а часть официальной Document model.

---

## 2. Главное разделение: UX и гарантия данных

### Client Script

**[FRAPPE DOCS]** Client Script выполняется в браузере и влияет на standard form view.

Источник:

- https://docs.frappe.io/framework/user/en/desk/scripting/client-script

Подходящие задачи:

```text
показать предупреждение;
скрыть/показать поле;
автоматически заполнить удобное значение;
изменить filter Link;
добавить кнопку;
немедленно подсказать ошибку пользователю.
```

### Server-side Document logic

Подходящие задачи:

```text
данные никогда не должны нарушать правило;
неправильный Document нельзя сохранить через API;
правило должно работать при импорте и background processing;
бизнес-инвариант не зависит от UI.
```

### Ключевое правило

**[ARCHITECTURAL INFERENCE]**

```text
Client Script = удобство интерфейса
Server-side validation = гарантия модели
```

Это следует из прямого предупреждения документации: Client Script validation применяется только в standard browser form.

---

## 3. Типовой пример

Правило:

```text
end_date не может быть раньше start_date
```

Неполное решение:

```text
Client Script запрещает выбрать неправильную дату
```

Проблема: Document может быть создан через REST API, import или серверный код.

Надёжное решение:

```text
Controller.validate()
```

и, при желании, тот же check на форме для ранней обратной связи.

---

## 4. Основные lifecycle hooks

**[FRAPPE DOCS]** Controller API перечисляет hooks жизненного цикла Document.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers

Для архитектурного мышления полезна следующая семантика.

### `before_validate`

Подготовить данные перед проверкой.

Пример:

```text
нормализовать введённое значение;
заполнить производное поле, необходимое validation.
```

### `validate`

Проверить инварианты Document.

Пример:

```text
quantity > 0
end_date >= start_date
parent != self
```

### `before_save`

Последняя подготовка перед обычным save.

### `on_update`

Реакция после update Document.

Нельзя автоматически превращать `on_update` в место для любой тяжёлой интеграции. Side effects требуют учёта transactions — см. `05_TRANSACTIONS_ASYNC.md`.

### `before_submit`

Последняя проверка перед переходом в Submitted.

### `on_submit`

Реакция на успешный submit.

### `before_cancel`

Проверить, допустима ли отмена.

### `on_cancel`

Реакция на cancel.

### `before_update_after_submit` / `on_update_after_submit`

Отдельные hooks для разрешённых изменений Submitted Document.

---

## 5. Инвариант должен находиться там, где его нельзя обойти

Инвариант — правило, которое должно быть истинно всегда.

Пример:

```text
Inspection нельзя завершить без result.
```

Если правило реализовано только:

- кнопкой;
- client validation;
- скрытием поля;
- фильтром формы,

оно не является гарантией данных.

**[ARCHITECTURAL INFERENCE]** Критические инварианты должны проверяться на server-side path, через который проходят обычные изменения Document.

---

## 6. Server Script — официальный, но особый механизм

**[FRAPPE DOCS]** Server Script позволяет выполнять Python logic на Document Event или как API.

Источник:

- https://docs.frappe.io/framework/user/en/desk/scripting/server-script

Но начиная с v15 Server Scripts **disabled by default** на shared benches из соображений безопасности; public shared Frappe Cloud bench их не разрешает.

Отсюда важный вывод.

**[ARCHITECTURAL INFERENCE]** Server Script не является обязательной промежуточной ступенью между configuration и Python App code.

### Когда Server Script уместен

- site-specific automation;
- ограниченная low-code настройка;
- логика действительно должна жить как runtime configuration;
- deployment environment разрешает Server Scripts.

### Когда Controller лучше

- логика является обязательной частью устанавливаемого App;
- нужен Git history;
- нужны обычные code review и tests;
- логика должна одинаково разворачиваться на нескольких sites.

---

## 7. Business status, Workflow и docstatus

Это три разных понятия, которые могут взаимодействовать.

### Business status

Отвечает:

> Что сейчас происходит с объектом?

Пример:

```text
New
In Progress
Waiting
Done
```

Обычно выражается обычным field.

### Workflow

Отвечает:

> Какие переходы между состояниями разрешены, кому и при каких условиях?

Workflow имеет states, transitions, roles и conditions.

Официальная документация Workflow:

- https://docs.frappe.io/erpnext/user/manual/en/workflows

### `docstatus`

**[FRAPPE DOCS]** Системный транзакционный lifecycle:

```text
0 Draft
1 Submitted
2 Cancelled
```

Источник:

- https://docs.frappe.io/framework/doctypes/docstatus

`docstatus` отвечает не на вопрос «в какой колонке Kanban находится задача», а на вопрос о системном состоянии transactional Document.

---

## 8. Они различны, но не изолированы

Нельзя рисовать их как три независимых мира.

Workflow может управлять состояниями и участвовать в переходах, связанных с `docstatus`.

Поэтому правильная формулировка:

```text
business status = предметный смысл состояния
Workflow        = политика переходов
DocStatus       = системный transaction lifecycle
```

Один Document может использовать более одного из этих механизмов.

---

## 9. Когда достаточно обычного status

Пример:

```text
Task
New → In Progress → Waiting → Done
```

Если уполномоченный пользователь может менять состояние без отдельного approval route, обычное поле может быть достаточно.

### Red flag

Создавать Workflow только потому, что у поля есть четыре значения.

Workflow имеет смысл, когда действительно нужны управляемые переходы, роли и условия.

---

## 10. Когда рассматривать Workflow

Пример:

```text
Draft
  ↓ Employee: Submit for Review
Manager Review
  ↓ Manager: Approve
Approved
```

Здесь присутствуют:

```text
states
transitions
roles
conditions
```

и Workflow естественно выражает процесс.

### Исключение

Если approval является сложной динамической orchestration:

```text
стоимость × риск × договор × организация × внешний API
```

стандартный Workflow может перестать быть достаточным. Тогда сложная domain logic может быть оправдана.

Наличие слова «approval» не является автоматическим требованием использовать Workflow.

---

## 11. Когда нужен `Is Submittable`

**[FRAPPE DOCS]** Submittable Documents используют Draft → Submitted → Cancelled semantics и получают ограничения после submit.

Источник:

- https://docs.frappe.io/framework/doctypes/docstatus

Это естественно для документа, где submit означает совершённый/зафиксированный факт.

Примеры:

```text
финансовая операция;
акт;
складская транзакция;
официально подтверждённый документ.
```

### Неправильный мотив

> «У нас задача может быть Done, значит сделаем её Submitted».

Done и Submitted имеют разную семантику.

---

## 12. Allow on Submit — не способ бесконтрольно редактировать Submitted Document

Некоторые поля могут быть разрешены для изменения после submit.

Архитектурно это следует рассматривать как исключение для конкретных полей, а не как обход транзакционной фиксации.

Перед `Allow on Submit` нужно спросить:

> Это действительно атрибут, изменение которого не меняет смысл уже подтверждённой операции?

---

## 13. Service layer — не запрещён

Аудит first-party ERPNext показывает реальные service classes:

- `StockLedgerService`;
- `TaxService`;
- `QualityInspectionService`;
- `AssetService`;
- `SerialBatchBundleService`.

Примеры:

- https://github.com/frappe/erpnext/blob/develop/erpnext/stock/services/stock_ledger_service.py
- https://github.com/frappe/erpnext/blob/develop/erpnext/accounts/services/taxes.py

`StockLedgerService` даже прямо описывает логику, вынесенную из большого `StockController`.

### Следствие

Нельзя утверждать:

```text
вся бизнес-логика обязана жить только в Controller
```

Правильнее:

```text
Controller
  владеет Document lifecycle и поведением своего Document

Service/domain module
  выделяет сложную отдельную ответственность,
  особенно если она координирует несколько Documents
```

---

## 14. Плохой и хороший Service

### Пустая обёртка

```text
TaskService.save(task):
    task.save()
```

Она ничего не добавляет к Document API.

### Реальная ответственность

```text
MonthlySettlementService
```

может:

- собрать данные из нескольких DocType;
- выполнить расчёты;
- создать несколько Documents;
- вызвать integration;
- работать как background job.

Тогда выделение service снижает coupling и размер Controllers.

---

## 15. Repository — такой же критерий

Framework не запрещает Repository pattern.

Но обёртка:

```text
TaskRepository.get(name):
    return frappe.get_doc("Task", name)
```

лишь дублирует API Framework.

Repository приобретает смысл, если действительно абстрагирует:

```text
несколько backends;
специализированный aggregate storage;
внешний источник;
сложную query/persistence responsibility.
```

Статус этого правила: **[ARCHITECTURAL INFERENCE]**.

---

## 16. Свой DocType vs расширение чужого

Если App владеет DocType, его Controller — естественное место для lifecycle logic.

Если другое App лишь реагирует на чужой DocType, часто естественнее официальный extension seam:

```text
doc_events
extend_doctype_class
```

Это позволяет не захватывать ownership чужой модели.

Подробно: `07_EXTENSION_CUSTOMIZATION.md`.

---

## 17. Lifecycle design review

Перед реализацией правила спросить:

```text
1. Это UX или гарантия данных?
2. Правило относится к одному Document или координирует несколько?
3. Какой lifecycle event соответствует семантике?
4. Может ли логика быть вызвана повторно?
5. Есть ли внешние side effects?
6. Что произойдёт при rollback?
7. Это business status, Workflow policy или docstatus?
8. Нужна ли transaction finality через submit?
9. Logic site-specific или является частью App?
10. Нужен ли service, или Controller остаётся понятным и локальным?
```

Если эти ответы известны, место для логики обычно становится очевидным без искусственных архитектурных слоёв.
