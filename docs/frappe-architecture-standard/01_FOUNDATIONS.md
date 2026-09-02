# 01. Foundations

## 1. Что мы называем Frappe-native архитектурой

Frappe-native архитектура — это не отдельный стиль программирования и не запрет собственного кода.

Это способ проектирования, при котором приложение сначала использует **семантически подходящие primitives самого Framework**, затем его официальные точки расширения и только после этого вводит собственные конструкции там, где появляется действительно новая ответственность.

Главный вопрос design review:

> **Какой механизм Frappe уже владеет этой ответственностью и почему его семантика недостаточна для нашей задачи?**

Если ответа на вторую часть нет, новая abstraction, скорее всего, преждевременна.

---

## 2. Что Frappe говорит о себе сам

### Факт Frappe

Frappe позиционирует себя как metadata-driven, full-stack low-code framework.

### Архитектурное следствие

Приложение не должно воспринимать Frappe как пустой Python web-framework, поверх которого обязательна отдельная application platform.

Framework уже предоставляет значительную часть application infrastructure:

- DocType / Meta;
- Document lifecycle;
- permissions;
- generated Desk UI;
- REST API;
- reports;
- notifications;
- assignments;
- background jobs;
- scheduler;
- hooks;
- website/web forms;
- files/comments/versioning.

### Граница

Это не означает, что приложение обязано пользоваться всеми механизмами Framework или что custom implementation запрещён.

Критерий один: **совпадает ли семантика штатного механизма с требованием**.

---

## 3. Configuration over code

### Факт Frappe

Официальная философия Frappe формулируется как preference for configuration over code и минимизация кода там, где задача уже выражается средствами Framework.

### Архитектурное следствие

Если требование полностью выражается через metadata или стандартный subsystem, не следует программировать параллельный механизм только потому, что разработчик привык делать так в другом стеке.

Пример:

```text
нужно отправить письмо при изменении статуса
```

Сначала проверяется `Notification`.

Не потому, что Python плохой, а потому, что Notification уже специально отвечает за такой класс задач.

### Граница

Если Notification не выражает нужную orchestration, retries, external contract или другую сложную семантику, custom code является нормальным следующим решением.

---

## 4. Batteries included и монолитная модель

Frappe проектируется как интегрированная application platform, а не набор микробиблиотек.

Это важно понимать до проектирования архитектуры приложения.

### Неправильная стартовая модель

```text
Frappe = ORM + HTTP

наша платформа:
    domain entities
    repositories
    ACL
    workflow engine
    notification engine
    scheduler
    REST framework
    UI metadata
```

### Более естественная модель

```text
Frappe
    ├── application infrastructure
    └── extension points

Our App
    ├── domain model
    ├── domain rules
    ├── domain services where needed
    └── integrations specific to our product
```

### Архитектурное следствие

Не следует автоматически создавать второй generic framework поверх Frappe.

### Граница

«Монолит» не означает:

- один файл;
- один Controller;
- отсутствие modules;
- отсутствие services;
- отсутствие custom frontend;
- отсутствие интеграционных компонентов.

ERPNext сам использует services для сложной предметной логики.

---

## 5. Metadata — не просто описание формы

DocType metadata влияет одновременно на несколько частей Framework:

```text
fields
schema
relationships
form
list
permissions
naming
API surface
reports
workflow integration
```

Поэтому изменение metadata является архитектурным изменением модели приложения, а не только UI-настройкой.

Например, добавление `Link` вместо `Data` меняет не только вид поля, но и семантику связи между Documents.

---

## 6. DocType как основной structural primitive

DocType — главный структурированный тип данных во Frappe.

Но его не следует узко называть только «бизнес-сущностью».

DocTypes используются для:

- бизнес-документов;
- master data;
- settings;
- logs;
- integration configuration;
- workflow definitions;
- system metadata.

Правильнее думать так:

> **DocType — основной metadata-defined Document type Framework.**

---

## 7. Document как runtime model

DocType отвечает на вопрос:

> Как устроен этот тип документа?

`Document` отвечает:

> Как ведёт себя конкретный экземпляр этого типа во время выполнения?

Controller является Python-классом Document и участвует в lifecycle документа.

Это делает Document значительно более богатой abstraction, чем обычная database row.

---

## 8. Не путать Framework responsibility и domain responsibility

Очень важное разделение.

### Framework responsibility

Например:

```text
как сохранить Document
как проверить Role permissions
как выполнить background job
как вызвать REST CRUD
как синхронизировать schema
```

### App responsibility

Например:

```text
что такое Inspection
когда Claim считается допустимым
как рассчитать Stock Reservation
какие документы создаёт business operation
```

Плохая архитектура часто появляется именно при смешивании этих уровней.

---

## 9. Ownership matrix

Перед изменением любого элемента нужно определить, кто им владеет.

| Владелец | Что это означает |
|---|---|
| Frappe Framework | системный primitive Framework |
| другое App | модель принадлежит установленному приложению |
| наше App | мы владеем моделью и её lifecycle |
| Site | локальная customization конкретного сайта |
| external system | Frappe только интегрируется с данными/процессом |

### Пример

`User` принадлежит Framework.

Если нашему приложению нужно добавить поле к User, это не означает, что нужно копировать User в `Our User`.

Сначала рассматриваются штатные customization/extension mechanisms.

---

## 10. App

Frappe App — source/deployment/package boundary.

Это Python package, устанавливаемый на site.

### Хорошие причины для отдельного App

- независимая установка;
- самостоятельный release cycle;
- отдельная зависимость;
- возможность использовать функциональность на разных sites;
- логически самостоятельная функция продукта.

### Плохая причина

> «У нас появилась ещё одна таблица».

Каждый DocType не требует отдельного App.

---

## 11. Module

Module группирует связанные модели и код внутри App.

Не нужно превращать Module в строгий DDD bounded context, если предметная область этого не требует.

Но и бессистемная свалка всех DocTypes в одном Module ухудшает навигацию и ownership.

Принцип:

> Module должен давать понятную логическую группировку, но не обязан соответствовать чужой архитектурной методологии.

---

## 12. Site customization и product source — разные вещи

Один из важнейших design boundaries Frappe.

### Site customization

Изменение делается для конкретного site:

- Customize Form;
- Custom Field;
- Property Setter;
- Workflow;
- Notification;
- Client Script;
- Server Script.

### Product source

Изменение является обязательной частью нашего App и должно воспроизводиться из repository.

### Design question

> Если поставить App на чистый совместимый site, должно ли это изменение появиться автоматически?

Если да — оно должно быть представлено source-controlled artifacts, fixtures, exported customization, hooks, patches или другим штатным механизмом доставки.

---

## 13. Packages

Современный Frappe также имеет Packages как более лёгкий механизм packaging части configuration artifacts.

Их наличие важно учитывать, чтобы не делать ложный вывод:

> любая переносимая low-code configuration обязательно требует отдельного Python App.

Но Package и App имеют разные capabilities и lifecycle, поэтому выбирать нужно по реальной deployment задаче.

---

## 14. Extension first, replacement second

Если приложение расширяет поведение другого App, сначала ищется предусмотренная точка расширения.

Примеры:

- `doc_events`;
- `extend_doctype_class`;
- `doctype_js`;
- permission hooks;
- scheduler hooks;
- fixtures/customizations;
- whitelisted-method overrides там, где это действительно требуется.

Полная замена объекта или core patch — более сильное вмешательство и требует более сильного обоснования.

---

## 15. Core patching

По умолчанию нельзя строить App на ручном изменении файлов Frappe или другого upstream App.

Причина не идеологическая, а эксплуатационная:

```text
upstream update
    +
local untracked modification
    =
merge/upgrade risk
```

Если Framework предоставляет extension seam, он и является нормальной точкой интеграции.

---

## 16. Public API против internal implementation

Даже код самого Frappe различает public surface и internal implementation.

Следовательно, приложение должно по возможности зависеть от документированных/public APIs Framework, а не от внутренних функций только потому, что их удалось импортировать.

Внутренняя функция может измениться без гарантии compatibility.

---

## 17. Собственная abstraction: правильный критерий

Вопрос не:

> «Разрешены ли services/repositories?»

Правильный вопрос:

> **Какую новую ответственность создаёт этот слой?**

### Плохой wrapper

```python
class TaskRepository:
    def get(self, name):
        return frappe.get_doc("Task", name)

    def save(self, task):
        task.save()
```

Здесь слой просто переименовал Frappe API.

### Нормальный отдельный компонент

```text
StockLedgerService
```

который координирует сложную логику между несколькими Documents и расчётами.

---

## 18. Один универсальный escalation ladder — ошибка

Нельзя строить архитектуру в виде:

```text
metadata
↓
controller
↓
hook
↓
custom API
↓
custom UI
```

Эти механизмы решают разные классы задач.

В стандарте используются независимые decision tracks:

```text
Data Model
Lifecycle
State
Security
Transactions
Async
Integration
Extension
Presentation
Deployment
Testing
```

Внутри каждого действует общий принцип:

```text
native primitive
    ↓
official extension
    ↓
custom implementation
```

---

## 19. Что является реальным анти-паттерном

Не название класса и не количество Python-кода.

Анти-паттерн — **необоснованное параллельное владение той же ответственностью**.

Например:

```text
Frappe Permission Engine
+
Our Permission Engine
```

или:

```text
Frappe Document lifecycle
+
Our Generic Document lifecycle
```

или:

```text
Frappe Scheduler
+
собственный daemon для обычной site-задачи
```

---

## 20. Главное правило стандарта

Перед любой собственной архитектурной конструкцией должны существовать четыре ответа:

```text
1. Какую проблему решаем?

2. Какой Frappe primitive уже отвечает
   за ближайшую ответственность?

3. Почему его семантика недостаточна?

4. Почему выбранный extension/custom mechanism
   является минимально достаточным?
```

Если на вопрос №3 нет конкретного ответа, custom mechanism не доказан.
