# 03. Document Lifecycle

## 1. Главная идея

Во Frappe Document — не пассивная строка таблицы.

Он имеет:

- metadata;
- permissions;
- lifecycle;
- validation;
- persistence semantics;
- events;
- submit/cancel state;
- integration points.

Поэтому правила, которые принадлежат самому Document, должны проектироваться с учётом его lifecycle, а не как произвольный набор обработчиков.

---

## 2. Controller

Controller — Python-класс конкретного DocType, наследующий `frappe.model.document.Document`.

Он является естественным владельцем поведения самого Document.

Пример:

```python
class Inspection(Document):
    def validate(self):
        ...
```

Это нативно.

Нативность не определяется количеством Python-кода. Она определяется тем, что логика находится в механизме, специально предназначенном для lifecycle Document.

---

## 3. Document lifecycle как server-side boundary

`doc.save()` — не просто SQL UPDATE.

Framework выполняет permission checks, validation hooks и post-save events.

Поэтому обычное изменение business Document через `Document` API имеет другую семантику, чем direct DB update.

### Архитектурное следствие

Если операция должна соблюдать правила документа, используем Document lifecycle.

Если lifecycle намеренно обходится — это отдельное архитектурное решение, которое должно быть явно обосновано.

---

## 4. Основные lifecycle hooks

Упрощённая последовательность обычного сохранения:

```text
before_validate
    ↓
validate
    ↓
before_save
    ↓
DB write
    ↓
on_update
```

Для insert дополнительно существуют:

```text
before_insert
after_insert
```

Для submittable Documents:

```text
before_submit
on_submit

before_cancel
on_cancel
```

Для изменения разрешённых полей после submit:

```text
before_update_after_submit
on_update_after_submit
```

---

## 5. before_validate

Хорошее место для подготовки данных, необходимых самой validation.

Пример:

```text
нормализовать значение;
заполнить производное поле;
подготовить child rows.
```

### Не следует

Превращать `before_validate` в универсальный event bus с внешними side effects.

---

## 6. validate

`validate` — основное место для business invariants конкретного Document.

Инвариант — правило, которое никогда не должно быть нарушено независимо от интерфейса.

Примеры:

```text
finish_date >= start_date
quantity > 0
parent != self
closed document cannot contain active child operation
```

### Почему server-side

Документ может быть изменён:

- Desk form;
- REST API;
- import;
- Python;
- background job;
- integration.

Правило должно работать во всех обычных путях сохранения.

---

## 7. before_save

Используется для изменений непосредственно перед persistence, когда validation уже пройдена.

Но если вычисление нужно самой validation, его следует выполнять раньше.

Главный вопрос:

> Нужны ли эти данные для проверки корректности Document или только для финальной записи?

---

## 8. on_update

`on_update` выполняется после изменения Document.

Это естественное место для реакций на успешное обновление в рамках Document lifecycle.

Но side effects должны учитывать transaction semantics: окончательный commit request ещё может не произойти.

Поэтому внешнюю систему нельзя бездумно уведомлять из любого `on_update`.

Эта тема подробно рассматривается в `05_TRANSACTIONS_ASYNC.md`.

---

## 9. submit/cancel

Если DocType `Is Submittable`, у него появляется системный transaction lifecycle:

```text
Draft      docstatus = 0
Submitted  docstatus = 1
Cancelled  docstatus = 2
```

### before_submit

Последняя проверка возможности подтвердить документ.

### on_submit

Последствия успешно выполненного submit.

### before_cancel

Проверка, можно ли отменить документ.

### on_cancel

Компенсационные последствия отмены.

---

## 10. Submit не является обычным status change

Это критическая граница.

`Submitted` во Frappe имеет системную semantics: документ переходит в более фиксированное состояние и обычное редактирование ограничивается.

Поэтому бизнес-статусы:

```text
New
In Progress
Waiting
Done
```

не должны автоматически превращаться в `docstatus`.

---

## 11. Business status

Обычный status отвечает:

> **В каком бизнес-состоянии находится объект?**

Пример:

```text
Work Item
    status = New / In Progress / Done
```

Это просто часть предметной модели.

---

## 12. Workflow

Workflow отвечает на другой вопрос:

> **Какие переходы разрешены и кто может их выполнять?**

Пример:

```text
Draft
  ↓ Employee submits
Manager Review
  ↓ Manager approves
Approved
```

Здесь имеются:

- states;
- transitions;
- roles;
- conditions.

Workflow является естественным первым кандидатом.

---

## 13. docstatus

`docstatus` отвечает:

> **Каково системное транзакционное состояние Document?**

Его нельзя использовать как универсальный Kanban status.

---

## 14. Workflow и docstatus могут взаимодействовать

Business status, Workflow и docstatus семантически различны, но не полностью независимы.

Workflow может управлять системным `docstatus`.

Поэтому правильная модель:

```text
business state       → предметная семантика
workflow transition  → governance переходов
docstatus            → системный transaction state
```

а не три полностью изолированных механизма.

---

## 15. Когда Workflow не нужен

Если любой уполномоченный пользователь может просто менять:

```text
Open → In Progress → Done
```

обычного `status` может быть достаточно.

Workflow не нужен только потому, что значений несколько.

---

## 16. Когда Workflow может быть недостаточен

Если approval зависит от сложной динамической логики:

```text
amount
× risk level
× external scoring
× contract type
× organization hierarchy
```

стандартная States/Transitions/Roles модель может перестать быть достаточной.

Тогда custom domain logic оправдана.

Критерий:

> Может ли процесс естественно выражаться моделью Workflow без превращения условий в нечитаемую программу внутри configuration?

---

## 17. Client Script

Client Script выполняется в браузере и предназначен прежде всего для form UX.

Хорошие задачи:

```text
показать/скрыть поле;
изменить фильтр Link;
сразу предупредить пользователя;
заполнить вспомогательное значение;
добавить button;
изменить presentation формы.
```

---

## 18. Client Script не является гарантией данных

Критическое правило нельзя защищать только Client Script.

Почему?

Потому что Document можно изменить без этой browser form.

Пример плохого решения:

```text
finish_date >= start_date
```

проверяется только JavaScript.

Через API неправильный Document может быть сохранён.

### Правильная модель

```text
Client Script
    → удобное раннее предупреждение

server validate
    → окончательная гарантия
```

---

## 19. Server Script

Server Script — штатный runtime customization mechanism.

Он полезен для site-level automation, когда полноценное изменение App source не требуется или недоступно.

Но Server Script нельзя автоматически считать обязательной промежуточной ступенью перед Python Controller.

### В source-controlled App

Python Controller или normal Python module часто:

- проще тестировать;
- проще version-control;
- проще review;
- проще переносить между sites.

### Важная граница

Server Script имеет security/deployment restrictions и может быть отключён в конкретной инфраструктуре.

Поэтому architecture продукта не должна неосознанно зависеть от него.

---

## 20. Controller или doc_events

Хорошая граница ownership:

```text
мы владеем DocType
    → Controller — естественный owner lifecycle logic

мы хотим реагировать на DocType другого App
    → doc_events — естественный extension seam
```

Это рекомендация, а не технический запрет.

---

## 21. Service layer

Service не противоречит Frappe.

Он оправдан, если действительно выделяет отдельную ответственность.

Примеры:

- координация нескольких Documents;
- сложный расчёт;
- интеграционная orchestration;
- общий алгоритм для нескольких Controllers;
- разгрузка слишком большого Controller.

ERPNext сам использует подобные service modules.

---

## 22. Когда Service является пустым слоем

Плохой пример:

```python
class RequestService:
    def save(self, request):
        request.save()
```

Это не новая ответственность.

Код лишь переименовал Document API.

### Design question

> Если удалить Service, потеряется ли понятная отдельная business/technical responsibility?

Если нет — слой, вероятно, ничего не добавляет.

---

## 23. Repository

Repository также не запрещён.

Но обычный Frappe Document уже скрывает большую часть persistence lifecycle.

Поэтому wrapper:

```text
get → frappe.get_doc
save → doc.save
```

обычно не создаёт ценности.

Repository становится осмысленным, если действительно абстрагирует:

- несколько storage mechanisms;
- специализированную aggregate persistence;
- внешний источник;
- сложную query abstraction с самостоятельной ценностью.

---

## 24. Side effects

Document lifecycle и external side effects — разные вопросы.

Например:

```text
on_submit
    → call external API
```

кажется естественным.

Но если request transaction затем rollback, внешний API уже мог выполнить операцию.

Поэтому такие действия должны проектироваться вместе с transaction boundary.

---

## 25. Idempotency

Некоторые lifecycle events или background operations могут быть повторены.

Side effect должен отвечать на вопрос:

> Что произойдёт, если этот код выполнится второй раз?

Особенно важно для:

- внешних API calls;
- создания derived Documents;
- background jobs;
- cancellation/compensation;
- integration retries.

---

## 26. Direct DB update обходит lifecycle

Операция вида:

```python
frappe.db.set_value(...)
```

не эквивалентна:

```python
doc.save()
```

Если business rules живут в validation/events, direct DB write может их обойти.

Это не делает DB API плохим.

Оно означает:

> bypass должен быть намеренным.

---

## 27. Derived fields

Если поле полностью вычисляется из других данных, нужно определить ownership вычисления.

Варианты:

```text
не хранить вообще;
вычислять перед сохранением;
хранить как snapshot;
пересчитывать background job;
```

Не нужно автоматически хранить каждое удобное UI-значение в DB.

Но performance/reporting может оправдывать денормализацию.

---

## 28. Validation vs mutation

Хорошая validation отвечает:

> допустим ли Document?

Если `validate` неожиданно создаёт множество других Documents, отправляет API calls и выполняет тяжёлую orchestration, lifecycle становится трудно понимать.

Такую логику часто полезнее вынести в понятную command/service operation.

---

## 29. Большой Controller

«Вся бизнес-логика должна жить в Controller» — неправильное правило.

Controller должен оставаться владельцем Document lifecycle, но сложные алгоритмы можно выносить в:

- domain/service modules;
- pure functions;
- integration services;
- background operations.

Controller может координировать их в соответствующем lifecycle hook.

---

## 30. Маленький Controller тоже не самоцель

Обратная крайность:

```text
Controller
  → Service
      → Manager
          → Handler
              → Repository
```

для проверки двух дат.

Это добавляет переходы, но не ответственность.

Архитектурная ценность определяется не количеством слоёв, а ясностью ownership.

---

## 31. Decision track: где должна жить логика

```text
Нужно изменить UX формы?
        → Client Script / form JS

Нужно гарантировать корректность Document?
        → server-side Controller validation

Нужно обработать lifecycle собственного DocType?
        → Controller

Нужно реагировать на lifecycle чужого DocType?
        → doc_events / extension hook

Нужна сложная reusable domain orchestration?
        → service/domain module

Нужна долгая операция?
        → Background Job

Нужно выполнить периодически?
        → Scheduler

Нужна runtime site-only автоматизация?
        → рассмотреть Server Script
```

---

## 32. State decision track

```text
Просто рабочее состояние объекта?
        → status field

Нужны управляемые переходы/roles/approval?
        → Workflow

Нужна системная фиксация transaction?
        → Is Submittable / docstatus

Workflow должен управлять submit/cancel?
        → интегрировать Workflow и docstatus
```

---

## 33. Design review checklist

- [ ] Определены invariants Document.
- [ ] Критические invariants проверяются server-side.
- [ ] Client Script не является единственной защитой данных.
- [ ] `status`, Workflow и `docstatus` не смешаны семантически.
- [ ] `Is Submittable` используется из-за transaction semantics, а не просто наличия статусов.
- [ ] Controller владеет lifecycle собственного DocType.
- [ ] Service имеет самостоятельную ответственность.
- [ ] Direct DB writes используются намеренно.
- [ ] External side effects согласованы с transaction boundary.
- [ ] Повторное выполнение side effects рассмотрено.
- [ ] Server Script не стал скрытой обязательной production dependency.
