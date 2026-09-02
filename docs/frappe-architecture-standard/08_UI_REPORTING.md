# 08. UI и Reporting — представление модели, а не замена модели

## 1. Frappe уже предоставляет application UI

**[FRAPPE DOCS]** Frappe Desk — встроенный administrative UI. Framework автоматически предоставляет standard Form/List experience для DocTypes и дополнительные views.

Источники:

- https://docs.frappe.io/framework/user/en/introduction
- https://docs.frappe.io/framework/user/en/api/list

Это одна из причин, по которой Frappe называет себя batteries-included.

### Архитектурное следствие

**[ARCHITECTURAL INFERENCE]** Для обычного back-office CRUD стандартный Desk — сильный default. Custom frontend не нужен только ради того, чтобы получить форму, список и фильтры, которые Framework уже генерирует.

---

## 2. Но Desk не определяет предметную модель

Очень типичная ошибка:

> «Нам нужна Kanban-доска, значит главная сущность приложения — Board Column».

Это проектирование базы из экрана.

Правильный порядок:

```text
business object
    ↓
DocType + fields + lifecycle
    ↓
подходящие представления
```

Например:

```text
Work Item
  status = New / In Progress / Done
```

может отображаться:

- Form;
- List;
- Kanban;
- Report;
- custom page.

Один и тот же Document не обязан менять свою сущность из-за выбранного view.

---

## 3. Form View

Form — естественное представление одного Document.

Уместен, когда пользователь:

- просматривает карточку;
- редактирует fields;
- работает с child tables;
- выполняет Document actions.

### Red flag

Создавать custom page только потому, что standard Form кажется «слишком обычной», ещё до проверки её capabilities.

Custom UI оправдан функциональным требованием, а не желанием отличаться визуально.

---

## 4. List View

List естественен для поиска, фильтрации и массового просмотра records.

Источник:

- https://docs.frappe.io/framework/user/en/api/list

List можно расширять JS-конфигурацией, indicators и custom actions.

### Архитектурное правило

Если пользователю нужен обычный реестр документов, сначала проверить List View, а не строить отдельный SPA registry.

---

## 5. Kanban, Calendar, Gantt и другие views

Разные representations подходят разным семантикам данных.

Пример:

```text
status/category → Kanban
start/end date  → Calendar/Gantt
hierarchy       → Tree
```

Но view должен соответствовать уже существующему field meaning.

### Неправильно

Добавить artificial field только потому, что конкретный UI требует колонку, хотя бизнес-смысла у поля нет.

Если field существует только для layout и не выражает состояние модели, нужно проверить, не смешались ли domain и presentation.

---

## 6. Workspace

**[FRAPPE DOCS]** Workspace предназначен для организации рабочей области Desk: shortcuts, links, charts и sections.

Источник:

- https://docs.frappe.io/framework/user/en/desk/workspace

Workspace отвечает на вопрос:

> Как пользователю собрать доступ к рабочим объектам и информации?

Он не должен становиться скрытым источником бизнес-логики.

---

## 7. Report Builder

**[FRAPPE DOCS]** Report Builder позволяет построить простой report без программирования на основе DocType и связанных данных.

Источник:

- https://docs.frappe.io/framework/user/en/desk/reports/report-builder

Подходящий класс задач:

```text
выбрать поля;
отфильтровать;
сгруппировать;
получить простой operational report.
```

---

## 8. Query Report

**[FRAPPE DOCS]** Query Report предназначен для SQL-based dataset/report.

Источник:

- https://docs.frappe.io/framework/user/en/guides/reports-and-printing/how-to-make-query-report

Он уместен, когда требование естественно выражается query и не нуждается в сложном procedural calculation.

### Security warning

Report должен учитывать, какие данные реально разрешено показывать пользователю. SQL сам по себе не делает query permission-aware автоматически в том же смысле, что Document API.

При чувствительных данных security нужно проверять отдельно.

---

## 9. Script Report

**[FRAPPE DOCS]** Script Report использует Python для сложной report logic.

Источник:

- https://docs.frappe.io/framework/user/en/guides/reports-and-printing/how-to-make-script-reports

Подходит, если report требует:

- сложных расчётов;
- нескольких queries;
- нестандартного формирования columns/data;
- charts/message/summary.

### Не считать Script Report «хуже» Query Report

Это не лестница качества.

Выбор зависит от природы задачи:

```text
простая настройка      → Report Builder
естественный SQL       → Query Report
programmatic logic     → Script Report
```

---

## 10. Prepared Report

Для тяжёлых reports Framework поддерживает prepared/background execution.

Источник:

- https://docs.frappe.io/framework/user/en/guides/reports-and-printing/how-to-make-script-reports

Это связывает reporting с background processing, а не требует держать пользователя в долгом request.

---

## 11. Web Form

**[FRAPPE DOCS]** Web Form позволяет создать web-facing форму поверх DocType, включая создание/редактирование Documents и login/public scenarios.

Источник:

- https://docs.frappe.io/framework/user/en/web-form

Подходящий сценарий:

> Внешний пользователь должен отправить простую заявку через web.

### Red flag

Сразу строить отдельный frontend + API только ради одной формы, не проверив Web Form.

---

## 12. Portal / web pages

Frappe имеет web/portal mechanisms для server-rendered pages и пользовательских web-сценариев.

Источник:

- https://docs.frappe.io/framework/user/en/portal-pages

Они подходят, когда Web Form уже слишком ограничен, но полноценный отдельный frontend ещё не требуется.

---

## 13. Custom frontend совершенно допустим

Стандарт не утверждает:

```text
всё приложение обязано работать только через Desk
```

Custom frontend оправдан, если требование действительно специализированное:

```text
массовая высокочастотная работа;
сложные gestures/interactions;
consumer-facing UX;
mobile-first product;
визуальный редактор;
реaltime dashboard;
нестандартная навигационная модель.
```

Frappe при этом может оставаться backend/application platform.

### Главная граница

**[ARCHITECTURAL INFERENCE]** Custom frontend не должен вынуждать нас без причины строить параллельную business/data platform.

---

## 14. Не хранить бизнес-правила только в UI

Если custom frontend запрещает кнопку, но server API позволяет операцию, запрет является только UX.

Security и invariants должны оставаться на server side.

Связанные разделы:

- `03_DOCUMENT_LIFECYCLE.md`;
- `04_SECURITY.md`.

---

## 15. Print и document output

Frappe имеет встроенные printing/document output capabilities как часть batteries-included platform.

Перед созданием отдельного PDF service для обычного печатного Document нужно проверить стандартные Print Format/printing возможности Framework.

Но специализированный генератор оправдан, если требования к layout, rendering pipeline или downstream format выходят за стандартные capabilities.

---

## 16. UI design review

```text
1. Это обычная карточка Document?
2. Подходит ли стандартный Form?
3. Это обычный реестр — подходит ли List?
4. Представление Kanban/Calendar/Gantt отражает реальное поле модели?
5. Нужен ли Workspace или это бизнес-логика, спрятанная в навигации?
6. Какой report type соответствует природе расчёта?
7. Можно ли Web Form/Portal вместо отдельного frontend?
8. Если custom frontend нужен — почему?
9. Где находятся реальные server-side rules?
10. Не диктует ли конкретный экран структуру domain model?
```
