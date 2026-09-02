# 08. UI and Reporting

## 1. UI — представление модели, а не сама модель

Frappe генерирует значительную часть Desk UI из DocType metadata.

Это означает, что модель должна проектироваться прежде экрана.

Плохой порядок:

```text
хочу Kanban
    ↓
придумываю сущности Board / Column
```

Хороший порядок:

```text
что является business object?
    ↓
какое поле выражает состояние?
    ↓
можно ли показать это Kanban view?
```

---

## 2. Form

Standard Form — default UI для работы с Document.

Он уже знает:

- fields;
- child tables;
- permissions;
- attachments;
- comments/timeline;
- actions;
- workflow state;
- links.

Для обычного административного CRUD это сильный default.

### Когда custom form оправдан

Когда interaction существенно отличается от обычной карточки Document:

- специализированный массовый ввод;
- высокоинтерактивный интерфейс;
- consumer UX;
- visual editor;
- сложная multi-document operation.

---

## 3. List View

List View — стандартное collection representation DocType.

Перед созданием собственной таблицы нужно проверить:

- fields;
- filters;
- indicators;
- list actions;
- custom list JS;
- saved filters.

Custom list нужен, если стандартная collection semantics действительно недостаточна.

---

## 4. Kanban

Kanban — представление Documents по состоянию/категории.

Он не должен автоматически становиться источником domain model.

Пример:

```text
Work Item.status
    ↓
Kanban columns
```

а не обязательно:

```text
Board Column = отдельный business DocType
```

если у Column нет самостоятельной семантики.

---

## 5. Calendar/Gantt и другие views

Если Documents естественно имеют даты/периоды, стандартные views могут покрыть задачу без отдельного frontend.

Но view не должен заставлять искажать data model только ради совместимости.

---

## 6. Workspace

Workspace организует пользовательскую навигацию и рабочую область.

Он отвечает за presentation/navigation, а не domain ownership.

Не хранить business state только потому, что его удобно показать в Workspace.

---

## 7. Client Script и UI behavior

Client Script хорош для:

- UX;
- dynamic visibility;
- quick validation feedback;
- filtering;
- form buttons.

Но он не должен быть единственным местом critical business rule/security.

Подробно — `03_DOCUMENT_LIFECYCLE.md` и `04_SECURITY.md`.

---

## 8. Custom frontend

Custom frontend не является «не-Frappe».

Он оправдан, если стандартный Desk не соответствует product UX.

Примеры:

- мобильный operational interface;
- public customer application;
- visual planning board;
- high-frequency dispatch console.

### Главное условие

Не создавать вместе с custom frontend второй business backend без необходимости.

Frontend может продолжать использовать Frappe Document/API/domain services.

---

## 9. Web Form

Если внешний пользователь должен просто создать/редактировать Document через web, Web Form — естественный первый кандидат.

Не нужно автоматически строить отдельный SPA ради формы из десяти полей.

### Граница

Если нужен сложный multi-step product UX, custom web frontend может быть правильнее.

---

## 10. Portal/Web pages

Frappe предоставляет website/portal mechanisms для server-rendered pages и внешнего взаимодействия.

Их стоит проверить до отдельного frontend stack, если требования достаточно просты.

Но framework-native не означает обязанность использовать portal для любого публичного продукта.

---

## 11. Report Builder

Report Builder подходит для относительно простой выборки/группировки данных без custom code.

Хороший кандидат, когда пользователь хочет:

```text
показать поля
отфильтровать
сгруппировать
отсортировать
```

---

## 12. Query Report

Query Report естественен, когда dataset хорошо выражается SQL/query logic.

Он не является «следующей ступенью сложности» в обязательной лестнице.

Это другой инструмент для другого типа задачи.

---

## 13. Script Report

Script Report подходит, когда отчёт требует программной логики, вычислений или нескольких источников.

Если report становится тяжёлым, нужно учитывать prepared/background execution.

---

## 14. Prepared Report

Долгий report не должен обязательно выполняться синхронно в web request.

Prepared report/background processing позволяет отделить тяжёлый расчёт от UI response.

---

## 15. Report не должен становиться скрытым business engine

Плохой паттерн:

```text
критические business calculations
живут только внутри Script Report
```

а другие части системы повторяют расчёт отдельно.

Если расчёт является доменной функцией, его лучше вынести в reusable domain/service logic, которую Report использует.

---

## 16. Dashboard/Number Card/Chart

Для стандартной аналитической presentation сначала проверить встроенные компоненты.

Но если аналитика требует полноценного BI/data warehouse, Frappe Desk не обязан заменять специализированную BI platform.

Нативность = использовать Framework там, где его responsibility подходит.

---

## 17. Print Format

Print Format — нативный механизм представления Document для печати/PDF.

Не создавать отдельный document-generation service для обычной печатной формы, если Print Format покрывает задачу.

### Когда custom generation оправдана

- сложная пакетная генерация;
- regulatory format;
- external rendering service;
- специализированный binary output.

---

## 18. UI permissions

То, что кнопка скрыта, не означает, что операция запрещена.

UI должен отражать server permissions, а не заменять их.

Пример:

```text
button hidden for Employee
```

без server authorization — не security.

---

## 19. UX и workflow

Workflow должен оставаться server-governed process.

Kanban drag/drop, custom button или API не должны обходить разрешённые transitions.

Если UI может изменить state напрямую, это нужно протестировать.

---

## 20. Presentation-specific denormalization

Иногда для UI/reporting полезно хранить derived field.

Это допустимо, если определены:

- source of truth;
- момент пересчёта;
- consistency strategy.

Не хранить одно и то же значение в пяти местах без ownership.

---

## 21. Search

Перед собственной search subsystem проверить стандартные search/global search/link search capabilities.

Но специализированный полнотекстовый/semantic search может требовать внешнего engine.

Это новая ответственность и нормальная интеграция.

---

## 22. Realtime

Если UI нужно получать realtime updates, Frappe имеет realtime/socket capabilities.

Не обязательно строить собственный polling loop для внутренних events.

Но external/event-stream architecture может требовать отдельной infrastructure.

---

## 23. UI decision track

```text
Обычная карточка Document?
        → Form

Нужен список/filtering?
        → List View

Нужно состояние колонками?
        → Kanban

Простой внешний ввод?
        → Web Form

Навигация Desk?
        → Workspace

Простой аналитический отчёт?
        → Report Builder

SQL dataset?
        → Query Report

Programmable report?
        → Script Report

Специализированный product UX?
        → custom frontend
```

---

## 24. Design review checklist

- [ ] Data model не выведена из конкретного экрана.
- [ ] Standard Form/List/View capabilities проверены до custom UI.
- [ ] Kanban не породил лишние domain entities без причины.
- [ ] Web Form рассмотрен для простого external CRUD.
- [ ] UI hiding не используется как security.
- [ ] Workflow нельзя обойти альтернативным UI.
- [ ] Report type выбран по nature задачи, а не по «лестнице сложности».
- [ ] Domain calculations не спрятаны только в report.
- [ ] Heavy reports/jobs не блокируют request без причины.
- [ ] Custom frontend сохраняет ясную backend ownership model.
