# 10. Decision Standard — обязательный архитектурный review любого Frappe-решения

## 1. Зачем нужен этот файл

Предыдущие разделы объясняют устройство Framework. Этот файл превращает исследование в повторяемую процедуру.

Его цель — не заставить все приложения выглядеть одинаково, а заставить каждое отклонение от native primitive иметь понятную причину.

Главный вопрос:

> **Какую ответственность решает требование, кто уже владеет этой ответственностью во Frappe и почему стандартной семантики недостаточно?**

---

## 2. Матрица ответственности

| Responsibility | Native owner Frappe | First extension choice | Red flag |
|---|---|---|---|
| Структурированная модель | DocType / Meta | Custom Field, Child, Virtual | параллельная entity model без новой ответственности |
| Свойство Document | DocField | computed/server logic | отдельный DocType ради одного значения |
| Ссылка на master | Link | Dynamic Link | копия текста вместо живой связи без snapshot-смысла |
| Состав Document | Child DocType | отдельный relation DocType | самостоятельный CRUD для обычных строк |
| Один набор settings | Single DocType | — | обычный DocType + ручной запрет второй записи |
| Persistence/lifecycle | Document | Controller/service | raw SQL/direct DB для обычного business CRUD |
| Invariants | server-side Document path | service/domain validation | только Client Script |
| Business state | field/domain model | Workflow | docstatus как Kanban status |
| Approval transitions | Workflow | domain service | десятки role/status `if` на клиенте |
| Transaction finality | docstatus / submit | Workflow + docstatus | custom `Approved` + ручная блокировка всех полей |
| Access | permission engine | permission hooks | отдельный ACL до проверки штатных primitives |
| Field access | permlevel | custom response shaping | скрытие только в UI |
| Work assignment | Assignment / ToDo | domain field при другой семантике | дублирование assignee в нескольких источниках истины |
| User notification | Notification | custom notification service | собственный notification engine для одного письма |
| Outgoing Document HTTP event | Webhook | integration job/service | custom polling без причины |
| Async execution | Background Jobs | custom worker configuration | отдельный daemon для обычной site job |
| Periodic site task | Scheduler events | external orchestrator при иной ответственности | `while True` внутри App |
| Generic CRUD API | Document REST API | dedicated API contract | четыре endpoints, просто дублирующие CRUD |
| Document command | document method | service method | изменение state только клиентской кнопкой |
| App command | whitelisted method/service | dedicated API | generic CRUD, скрытый под «service endpoint» |
| Extension чужого DocType | Custom Field / hooks | `extend_doctype_class` | patch installed source |
| Full controller replacement | `override_doctype_class` | fork при осознанной стратегии | override без анализа совместимости |
| Simple admin UI | Desk Form/List | custom JS | отдельный SPA ради обычного CRUD |
| Simple report | Report Builder | Query/Script Report | отдельная BI-система ради простого списка |
| Public/simple web input | Web Form | Portal/custom frontend | отдельный frontend ради одной формы |
| Schema delivery | DocType JSON / migrate | patches | ручные изменения production DB |
| Config delivery | fixtures / exported customization | install hooks | ручное накликивание после каждой установки |
| Critical custom behaviour | Frappe tests | integration/e2e | «проверили руками один раз» |

Матрица не означает, что первый механизм всегда выигрывает. Она определяет **первую точку проверки**.

---

## 3. Decision track A — ownership

```text
Кому принадлежит изменяемый объект?

Нашему App
  → меняем Standard DocType/Controller в нашем source

Другому App
  → ищем extension/customization seam

Конкретному Site
  → runtime customization допустима

Внешней системе
  → проектируем integration boundary
```

### PASS

Owner явно назван.

### FAIL

«Просто изменим Customer в базе, потом разберёмся».

---

## 4. Decision track B — data model

```text
Это самостоятельная запись?
  ├─ нет → Field
  └─ да
      ↓
Это состав одного parent Document?
  ├─ да → Child DocType
  └─ нет → обычный DocType

Нужна ссылка на существующий Document?
  → Link

Тип target определяется динамически?
  → Dynamic Link

Нужен ровно один settings record?
  → Single

External data должны вести себя как Documents?
  → рассмотреть Virtual DocType
```

### Дополнительный вопрос

Link хранит **текущую связь** или бизнесу нужен **исторический snapshot**?

---

## 5. Decision track C — state/lifecycle

```text
Нужно просто хранить рабочее состояние?
  → business status field

Нужно контролировать переходы по ролям/условиям?
  → Workflow candidate

Нужно транзакционно зафиксировать Document?
  → Is Submittable / docstatus candidate
```

Нельзя использовать `docstatus` только потому, что status имеет финальное значение.

---

## 6. Decision track D — logic placement

```text
Это только UX формы?
  → Client Script / client JS

Это инвариант данных?
  → server-side Document/service path

Это lifecycle собственного DocType?
  → Controller

Это реакция на lifecycle чужого DocType?
  → doc_events / extension hook

Это сложная ответственность нескольких Documents?
  → service/domain module candidate
```

---

## 7. Decision track E — permissions

Это **design escalation**, а не runtime order:

```text
Role + DocPerm
   ↓
permlevel / If Owner
   ↓
User Permission
   ↓
Share для ad-hoc grants
   ↓
permission_query_conditions + has_permission
   ↓
complex policy abstraction
```

При custom row policy обязательно проверять и query/list, и direct Document access.

---

## 8. Decision track F — transaction/async

```text
Операция быстрая и атомарная?
  → обычный request transaction

Есть тяжёлая работа?
  → Background Job candidate

Job должна стартовать только после успешного save/submit?
  → enqueue_after_commit

Есть periodic site task?
  → scheduler_events

Есть external side effect?
  → определить commit boundary + idempotency/retry
```

---

## 9. Decision track G — API/integration

```text
Обычный CRUD Frappe-aware клиента?
  → Document REST API

Command одного Document?
  → document method

Command приложения?
  → whitelisted service/module method

Outgoing HTTP callback по Document Event?
  → Webhook

Нужен stable/versioned external contract?
  → dedicated API

Нужны retries/reconciliation/mapping?
  → integration service + jobs
```

---

## 10. Decision track H — customization/extension

```text
Добавляем field/property чужому DocType?
  → Custom Field / Property Setter

Нужно переносить изменение вместе с App?
  → fixtures / export customizations

Реагируем на событие чужого Document?
  → doc_events

Добавляем class behaviour? [v16+]
  → extend_doctype_class

Полностью заменяем controller?
  → override_doctype_class + отдельное обоснование
```

Patch core/fork рассматривается только как осознанная стратегия с upgrade cost.

---

## 11. Decision track I — UI/reporting

```text
Обычная карточка?
  → Form

Реестр?
  → List

Status/category board?
  → Kanban

Простой operational report?
  → Report Builder

SQL dataset?
  → Query Report

Programmatic report?
  → Script Report

Простая внешняя форма?
  → Web Form

Специализированный UX?
  → custom frontend candidate
```

Presentation не должна подменять server-side rules.

---

## 12. Decision track J — delivery

```text
Standard schema?
  → DocType JSON

Обязательные configuration records?
  → fixtures/export customization

Existing data нужно преобразовать?
  → patch

Site обновляется?
  → bench migrate

Критическая custom logic?
  → tests
```

---

## 13. Обязательная карточка архитектурного решения

Для любого нетривиального решения заполняется короткий блок:

```text
REQUIREMENT
Что нужно бизнесу?

OWNERSHIP
Framework / наше App / другое App / Site / external system?

NATIVE PRIMITIVE
Какой Frappe mechanism ближе всего по смыслу?

PROOF
Ссылка на docs/upstream.

SEMANTIC GAP
Что именно штатный механизм не умеет или почему его смысл не совпадает?

DECISION
Что делаем?

COST
Coupling, security, migration, testing, upgrade consequences.

EXCEPTION / EXIT
При каком условии решение нужно пересмотреть?
```

Если `SEMANTIC GAP` пуст — custom mechanism не считается обоснованным.

---

## 14. Классы риска

### R0 — обычная native configuration

Примеры:

```text
поле
Link
Child Table
Role permission
List/Report
```

Требует обычного review.

### R1 — native programmable extension

```text
Controller
Client JS
Script Report
whitelisted method
background job
Webhook
```

Проверяются tests/security/transactions.

### R2 — extension чужого App

```text
Custom Field
export customizations
doc_events
extend_doctype_class
```

Дополнительно проверяется upgrade/dependency ownership.

### R3 — strong override/bypass

```text
override_doctype_class
override_whitelisted_method
ignore_permissions
direct DB lifecycle bypass
manual commit
```

Требуется письменное обоснование и тесты.

### R4 — platform divergence

```text
fork core
parallel ACL
parallel lifecycle engine
own persistence layer over ordinary DocTypes
```

Не запрещено, но требует доказательства, что Framework semantics принципиально недостаточны и стоимость divergence принята сознательно.

---

## 15. Красные флаги design review

Следующие фразы не означают автоматический отказ, но требуют остановить review и получить доказательство:

```text
«Так принято в Clean Architecture».

«Сделаем Repository для каждого DocType».

«Проще дать ignore_permissions=True».

«Workflow слишком сложный, напишем статусы в JS».

«Сделаем свой scheduler».

«Сделаем четыре API endpoint поверх CRUD».

«После установки админ руками добавит поля».

«Поменяем файл ERPNext напрямую».

«Validation только на форме — этого хватит».

«Сделаем docstatus нашими статусами Kanban».

«Закоммитим посередине, чтобы точно сохранилось».
```

---

## 16. Что не является красным флагом само по себе

Не следует демонизировать:

```text
Service
Repository
custom API
custom frontend
SQL
background job
custom permission hook
Virtual DocType
external scheduler
fork
```

Каждый из них может быть правильным.

Критерий:

> решает ли он новую ответственность или просто строит второй экземпляр уже существующей Frappe responsibility?

---

## 17. Definition of Frappe-native

Решение можно считать Frappe-native, если одновременно выполняется следующее:

```text
1. Семантика выбранного primitive совпадает с требованием.
2. Framework responsibility не дублируется без причины.
3. Custom behaviour подключено через public/official seam, если он существует.
4. Security не держится только на UI.
5. Document lifecycle не обходится случайно.
6. Transaction boundary понятна.
7. Обязательное состояние воспроизводимо на новом site.
8. Upgrade/dependency ownership понятен.
9. Критичные собственные правила тестируются.
10. Исключения документированы как исключения, а не превращены в скрытую платформу.
```

---

## 18. Минимальный финальный review перед merge

```text
[ ] Ownership определён.
[ ] Data model прошла проверку DocType/Field/Child/Link.
[ ] Naming выбран осознанно.
[ ] Business status / Workflow / docstatus не смешаны.
[ ] Инварианты server-side.
[ ] Permissions проверены не только визуально.
[ ] Bypass permissions отсутствует или обоснован.
[ ] Transaction/rollback semantics понятны.
[ ] External side effects согласованы с commit.
[ ] Async jobs имеют retry/idempotency reasoning.
[ ] API не дублирует generic CRUD без причины.
[ ] Чужой App расширяется официальным seam.
[ ] Нет ручной обязательной post-install настройки.
[ ] Schema/data migration предусмотрена.
[ ] Critical custom logic покрыта tests.
[ ] Version-specific assumptions зафиксированы.
```

Если хотя бы один критичный пункт неизвестен, решение считается **не готовым к архитектурному утверждению**, даже если prototype технически работает.
