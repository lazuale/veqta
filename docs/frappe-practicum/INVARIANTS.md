# Инварианты учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Этот документ задаёт не список пожеланий, а формальную модель того, **что именно считается гарантией**, кто эту гарантию обеспечивает и с какого момента курса она действует.

Главное правило:

```text
не называть security invariant то,
что Frappe обеспечивает только интерфейсом или дисциплиной пользователя
```

---

# 1. Уровни силы

Каждый инвариант относится к одному из уровней.

## H — hard / server-enforced

Проверяется сервером Frappe при штатной операции.

Примеры:

```text
Mandatory field
Link на существующий Document
Role Permission
Workflow transition Allowed Role / Condition
Web Form Allow Edit = No
```

Нарушение должно привести к отказу операции.

## S — structural

Следует из структуры приложения и его metadata/source.

Примеры:

```text
ровно три core DocType
status — единственное поле состояния
Assignment не хранится собственным полем
```

## U — UI/process guard

Помогает пользователю работать правильно, но **не считается серверной границей безопасности**.

Примеры:

```text
Status Read Only
Workflow Only Allow Edit For
отсутствие поля Status в Web Form
```

## P — deployment/process policy

Верно только при соблюдении настройки конкретного site или обязательного cleanup шага.

Примеры:

```text
Assignment Rule включён на основном site
временный User Permission удалён после L5
после L11 active site снова facility-ops.localhost
```

---

# 2. Фазы жизни

Инвариант может быть не глобальным, а фазовым.

```text
L0–L3  → модель справочников
L4–L6  → ручной процесс
L7+     → Workflow-процесс
L9+     → automation на основном site
L10+    → authenticated external intake
L11     → portable app + site-specific deployment
Labs    → временные отклонения с обязательным rollback
```

Поэтому фраза вроде:

```text
Status можно менять вручную
```

верна в L4–L6 и неверна после L7.

---

# 3. Структурные инварианты

## S-01. Постоянное предметное ядро

**Уровень:** S  
**Действует:** L4+  

Постоянное ядро состоит из:

```text
Facility Location
Equipment
Service Request
```

Лабораторные Child/Single/Submittable DocType не становятся core автоматически.

## S-02. Один источник состояния заявки

**Уровень:** S  
**Действует:** L4+  

Единственное бизнес-поле состояния:

```text
Service Request.status
```

После L7 это же поле используется как `Workflow State Field`.

Запрещено создавать параллельные:

```text
workflow_state
request_state
processing_status
```

## S-03. Assignment не дублируется бизнес-полем

**Уровень:** S  
**Действует:** L6+  

Конкретное поручение хранится штатно:

```text
Service Request
→ Assign To
→ ToDo
→ User
```

Не создаются:

```text
Assigned Technician
Assignee
Technician User
```

в `Service Request` только ради повторения `_assign` / ToDo.

## S-04. Assignment не является авторизацией

**Уровень:** S  
**Действует:** L6+  

`Assign To` отвечает за ответственность и очередь работы, а не за security boundary.

```text
Permission
≠ Assignment
```

Facility Technician получает доступ через Role Permission. Наличие или отсутствие ToDo не считается доказательством права читать/писать Document.

Если продукту в будущем понадобится модель:

```text
редактировать может только конкретный assignee
```

она требует отдельной server-side permission/validation архитектуры и находится за границей базового no-own-code курса.

---

# 4. Инварианты данных

## H-01. Обязательные поля Service Request

**Уровень:** H  
**Действует:** L4+  

```text
Subject
Location
Description
Priority
```

обязательны на уровне DocType.

Любой канал создания должен выдавать валидный Document:

```text
Desk
Web Form
Auto Repeat
тестовые данные automation
clean-site acceptance
```

## H-02. Equipment необязателен

**Уровень:** H/S  
**Действует:** L4+  

```text
Service Request.equipment
```

не Mandatory.

Проблема может относиться к месту без отдельной единицы Equipment.

## H-03. Допустимые Priority

**Уровень:** H  
**Действует:** L4+  

```text
Low
Medium
High
```

Default:

```text
Medium
```

## H-04. Допустимые Status

**Уровень:** H  
**Действует:** L4+  

```text
New
Accepted
In Progress
Resolved
Closed
```

Состояние `Accepted` означает:

```text
Supervisor принял заявку в рабочий процесс
```

и **не означает**, что существует конкретный ToDo или конкретный assignee.

Это сознательно устраняет ложную связь старого состояния `Assigned` с механизмом Assign To.

## H-05. Equipment Category

**Уровень:** H  
**Действует:** L2+  

```text
HVAC
Electrical
IT
Other
```

Нельзя подставлять новое значение вроде `Pump` без изменения metadata.

## S-05. Семантика Location

**Уровень:** S  
**Действует:** L4+  

```text
Service Request.location
= место события / проблемы, зафиксированное заявкой

Equipment.location
= текущее размещение Equipment
```

Курс **не вводит hard invariant**:

```text
Service Request.location == Equipment.location
```

Причина: Equipment может быть позже перемещён, а историческое место события не должно переписываться вслед за карточкой оборудования.

При создании учебных заявок с Equipment используем логично совпадающую текущую Location, но это контроль качества данных, а не серверное ограничение.

---

# 5. Инварианты permissions

## H-06. Role Permission — базовая security boundary

**Уровень:** H  
**Действует:** L5+  

Основной серверный доступ задаёт Role Permission Manager.

```text
Requester
→ Read/Create/Write own Service Request в учебной модели L5+

Technician
→ Read/Write Service Request

Supervisor
→ Read/Write/Create/Delete + Report/Export
```

`If Owner`, Permission Level, User Permission и Share считаются отдельными механизмами, а не заменой Role Permission.

## P-01. User Permission/Share L5 временные

**Уровень:** P  
**Действует:** только внутри L5  

Эксперимент выполняется на:

```text
technician.restricted@example.com
```

До выхода из L5:

```text
Share удалён
User Permission удалён
Restricted Technician отключён
```

Основные Technician не наследуют Location restrictions.

## H-07. Assignment Rule не должен менять access model скрытым Share

**Уровень:** H/P  
**Действует:** L9+ на основном site  

В `v16.32.0` `Assign To` при отсутствии доступа у assignee способен автоматически создать `DocShare`; при отключённом document sharing операция может завершиться Missing Permission.

Поэтому основной deployment курса даёт обоим Technician одинаковый базовый доступ к `Service Request` до включения глобального Round Robin.

Цель:

```text
Assignment
не создаёт неожиданные permission exceptions
```

## U-01. Only Allow Edit For — не security boundary

**Уровень:** U  
**Действует:** L7+  

`Workflow State.only_allow_edit_for` используется как state-dependent Desk guard.

Он **не заменяет** Role Permission и не считается достаточным серверным запретом изменения полей через любой возможный канал.

Правильная модель:

```text
Role Permission
= security permission

Workflow Allowed Role / Condition
= server-side transition permission

Only Allow Edit For
= state-dependent editability в стандартном Desk UX
```

## U-02. Read Only Status — защита интерфейса, не отдельная ACL

**Уровень:** U  
**Действует:** L7+  

```text
status → Read Only = Yes
```

нужен, чтобы пользователь не обходил Workflow обычным Select в Desk.

Серверную допустимость смены state обеспечивает Workflow validation.

---

# 6. Инварианты процесса

## H-08. Workflow states

**Уровень:** H/S  
**Действует:** L7+  

```text
New
 ↓ Accept / Facility Supervisor
Accepted
 ↓ Start Work / Facility Technician
In Progress
 ↓ Resolve / Facility Technician
Resolved
 ↓ Close / Facility Supervisor
Closed
```

Все:

```text
docstatus = 0
```

## H-09. Allowed Role управляет переходом

**Уровень:** H  
**Действует:** L7+  

Workflow transition доступен только роли, указанной в `Allowed`.

Это серверно проверяется через `get_transitions()` / `validate_workflow()`.

## S-06. Accepted не означает Assigned To

**Уровень:** S  
**Действует:** L7+  

Допустимо:

```text
Status = New
Assigned To = Technician One
```

и технически возможно:

```text
Status = Accepted
Assigned To = пусто
```

потому что процесс и поручение — ортогональные механизмы.

Курс рекомендует рабочую последовательность:

```text
Assign To
→ Accept
```

но не выдаёт эту последовательность за hard server invariant.

## S-07. Technician role ≠ конкретный assignee

**Уровень:** S  
**Действует:** L7+  

Transition:

```text
Accepted → In Progress
In Progress → Resolved
```

разрешён роли `Facility Technician`.

В базовой архитектуре Frappe assignment не используется как authorization predicate для Workflow.

Следовательно assignment показывает ответственность, а Workflow Allowed Role — полномочие роли.

## S-08. Closed — terminal workflow state, но не immutable record

**Уровень:** H/S  
**Действует:** L7+  

У `Closed` нет исходящих Workflow transitions.

Это гарантирует:

```text
Closed
→ нельзя штатным Workflow Action вернуть назад
```

Но это **не равно**:

```text
все поля Document навсегда физически неизменяемы
```

Для серверно-неизменяемого closed record потребовалась бы отдельная validation policy, которая в базовом курсе не пишется.

Track Changes остаётся обязательным аудитом допустимых исправлений.

---

# 7. Инварианты automation

## P-02. Assignment Rule site-specific

**Уровень:** P  
**Действует:** L9+ на основном site  

```text
Service Request Auto Assignment
```

содержит конкретных Users:

```text
technician.one@example.com
technician.two@example.com
```

Поэтому он не является universal fixture приложения.

## H-10. Assignment Rule не меняет Workflow state

**Уровень:** H/S  
**Действует:** L9+  

После автоматического назначения нормальное состояние:

```text
Assigned To = Technician
Status = New
```

Переход `New → Accepted` выполняется отдельно через Workflow.

## C-01. Target Date задаёт условную автоматизацию

**Тип:** conditional invariant  
**Уровень:** H/S  
**Действует:** L9+  

Если:

```text
Target Date заполнен
```

то:

```text
Assignment Rule ToDo.date
→ следует Target Date

Service Request One Day Overdue
→ может сработать через 1 день после Target Date
```

Если `Target Date` пуст:

```text
нет обещания Due Date
нет date-based overdue trigger
```

`Target Date` остаётся Optional именно поэтому.

## P-03. Load Balancing не остаётся финальной конфигурацией

**Уровень:** P  
**Действует:** optional часть L9  

После эксперимента:

```text
Rule = Round Robin
```

---

# 8. Инварианты Web Form

## H-11. Финальная форма требует login

**Уровень:** H  
**Действует:** финал L10+  

```text
Login Required = Yes
Anonymous Responses = No
```

Guest mode существует только как временная лабораторная проверка внутри L10.

## H-12. Финальная Web Form create/read-only

**Уровень:** H  
**Действует:** финал L10+  

```text
Allow Editing After Submit = No
```

Причина: при owner-based Web Form access с `Apply Document Permissions = No` Frappe сохраняет разрешённое Web Form update через `doc.save(ignore_permissions=True)`.

Такой update нельзя использовать как безопасный state-aware editor поверх Workflow.

Поэтому механизм `Allow Edit` изучается временно, после чего обязательно отключается до приёмки.

Финальная модель:

```text
Website User
→ создать заявку
→ видеть свои ответы в Show List
→ не редактировать созданный Service Request через Web Form
```

## H-13. Web Form не управляет Workflow

**Уровень:** H/S  
**Действует:** L10+  

В пользовательском наборе полей отсутствует:

```text
Status
```

После insert:

```text
Status = New
```

за счёт DocType default.

## P-04. Link catalog disclosure является осознанным trust decision

**Уровень:** P  
**Действует:** финал L10+  

`Allow Read On All Link Options = Yes` для Location/Equipment позволяет authenticated Website User выбирать общие справочные значения через Web Form.

Это означает осознанное раскрытие имён/названий этих Link options авторизованным Website Users.

Threat model курса:

```text
Website User = доверенный внутренний заявитель
```

Для публичного/недоверенного internet intake такая модель не считается безопасной; нужен отдельный внешний каталог/permission design и это Later.

---

# 9. Инварианты поставки

## S-09. Четыре слоя поставки

**Уровень:** S  
**Действует:** L11  

```text
Standard source
app configuration
site-specific configuration
working data
```

не смешиваются.

## S-10. Universal app configuration

Через source/fixtures/customizations поставляются:

```text
3 core DocType
Reports/Cards/Chart/Workspace
Notifications
Web Form
Roles
Workflow States
Workflow Action Masters
Workflow
Custom DocPerm
```

## P-05. Неуниверсальная конфигурация не fixture

Не экспортируются как universal fixtures:

```text
Users
User Permission
Share
Assignment Rule tied to local Users
```

## H-14. install-app — первоначальная установка

В `v16.32.0` install flow выполняет синхронизацию source, fixtures, customizations и dashboards.

`migrate` после установки в L11 проверяет обычный повторный update/convergence path, а не «доделывает неполную установку».

## S-11. Portability scope

L11 доказывает:

```text
clean-site portability
```

то есть установка `facility_ops` на новый чистый Frappe site.

L11 **не доказывает** автоматическую совместимость с произвольным набором сторонних apps и глобальных имён на уже насыщенном site.

## P-06. После L11 возвращается основной site

```text
bench use facility-ops.localhost
```

обязателен перед Labs.

---

# 10. Инварианты лабораторий

## P-07. Lab rollback contract

Каждая лаборатория явно указывает:

```text
Temporary Mutation
Persistent Mutation
Rollback
Final State
```

## S-12. Domain rollback ≠ source rollback

Лаборатории не должны незаметно расширять доменную модель.

Но это не означает, что после каждой Lab Git обязан вернуться к идентичному baseline.

Пример:

```text
Lab E
→ Standard Print Format остаётся app-owned presentation configuration
→ Letter Head удаляется
→ новых core business entities нет
```

---

# 11. Compatibility matrix

| Механизмы | Совместимость | Условие |
|---|---|---|
| DocType Mandatory ↔ Web Form | жёсткая | Web Form не ослабляет Mandatory |
| Role Permission ↔ Workflow | совместимы | Role Permission = access, Workflow = transitions |
| Only Allow Edit For ↔ security | не эквивалентны | Only Allow Edit For не считать ACL |
| Assignment ↔ Workflow | ортогональны | assignment не кодирует status |
| Assignment ↔ authorization | не эквивалентны | assignee не является permission predicate |
| User Permission ↔ Round Robin | опасная без cleanup | main Technician без Location restriction |
| Assignment Rule ↔ permissions | совместимы | не допускать неожиданный auto-Share |
| Target Date ↔ Due Date | условная | только если Target Date задан |
| Workflow ↔ Web Form edit | небезопасная | финальный Allow Edit = No |
| Workflow ↔ Kanban | допустима для демонстрации | после L7 Kanban удаляется |
| Standard source ↔ fixtures | совместимы | fixtures не дублируют Standard DocType |
| Main site ↔ clean site | намеренно различаются | Assignment Rule site-specific |
| Labs ↔ core domain | совместимы | обязательный rollback domain changes |

---

# 12. State contract урока

Каждый урок при execution-аудите должен проверяться по одному шаблону:

```text
PRECONDITIONS
→ что обязано существовать перед уроком

TEMPORARY MUTATIONS
→ что разрешено изменить только внутри эксперимента

PERSISTENT MUTATIONS
→ что должно остаться

ROLLBACK
→ что обязательно вернуть

OUTPUT STATE
→ точное состояние site после приёмки

GIT STATE
→ ожидаемые изменения source
```

Формальный критерий последовательности:

```text
OUTPUT(Ln)
должен удовлетворять
PRECONDITIONS(Ln+1)
```

Если это не выполняется без ручного угадывания — ошибка находится в курсе, а не в ученике.

---

# 13. Что сознательно нельзя назвать hard invariant без следующего уровня

В базовом no-own-code маршруте **не обещаем**:

```text
редактировать Service Request может только конкретный assignee

Closed физически неизменяем на уровне любого API

Equipment.location всегда равен исторической Service Request.location

Website User может безопасно редактировать заявку на любой стадии Workflow

facility_ops бесконфликтно co-installable с любым сторонним app
```

Для таких гарантий нужен следующий слой: Server Script/custom controller/custom permission logic или иная специально спроектированная серверная валидация.

В текущем курсе эти механизмы находятся в `Later`, поэтому базовая архитектура должна быть **честно ограниченной, а не псевдобезопасной**.
