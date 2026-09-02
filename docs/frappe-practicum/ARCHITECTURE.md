# Архитектура учебного приложения `facility_ops`

Базовая версия: **Frappe Framework v16.32.0**.

Этот документ описывает архитектуру именно учебного приложения. Он не объявляет выбранную модель универсальным шаблоном для всех Frappe-приложений.

Методическая основа курса: [архитектурный стандарт Frappe](../frappe-architecture-standard/README.md).

Технические гарантии и точные ограничения вынесены в [INVARIANTS.md](INVARIANTS.md).

---

# 1. Как выбирается механизм

Для каждого требования курс задаёт один вопрос:

```text
какая ответственность нужна
→ кто должен ею владеть
→ какой штатный механизм Frappe совпадает по смыслу
→ что он гарантирует
→ где заканчивается его ответственность
```

Если стандартный механизм решает задачу, собственный параллельный механизм не создаётся.

Поэтому в `facility_ops`:

```text
иерархия мест        → Tree DocType
оборудование         → обычный DocType + Link
заявка               → обычный DocType
исполнитель          → Assignment / ToDo
состояние процесса   → status + Workflow
комментарии          → Comment / Timeline
история изменений    → Track Changes / Version
вложения             → File / Attach
контроль             → Report / Number Card / Chart / Workspace
приём через веб      → Web Form
```

---

# 2. Предметное ядро

```text
Facility Location (Tree)
        │
        ├────────────► Equipment
        │                 │
        └─────────────────┴────────────► Service Request
```

Постоянных предметных `DocType` всего три:

```text
Facility Location
Equipment
Service Request
```

Новый `DocType` не добавляется только ради демонстрации функции Framework.

---

# 3. Почему модель минимальна

Не создаём без отдельной необходимости:

```text
Equipment Type
Department
Technician
Requester
Status
Priority
Assigned Technician
Task History
Task Comment
Attachment Registry
```

Причины различаются:

- часть значений достаточно выразить полями;
- пользователи уже существуют как `User`;
- рабочее назначение уже существует как `Assignment / ToDo`;
- история и комментарии уже имеют штатные механизмы;
- вложения уже принадлежат `File`.

Это не запрет таких сущностей вообще. Они появятся в реальном приложении, если получат самостоятельную идентичность, жизненный цикл или другую отдельную ответственность.

---

# 4. Service Request

Обязательные поля:

```text
Subject
Location
Description
Priority
```

Необязательные:

```text
Equipment
Target Date
Attachment
```

Состояния:

```text
New
Accepted
In Progress
Resolved
Closed
```

Семантика Location:

```text
Service Request.location
= место события в момент создания заявки

Equipment.location
= текущее место оборудования
```

Поэтому между ними нет вечного равенства.

---

# 5. Независимые ответственности

В курсе сознательно не смешиваются:

```text
DOCUMENT ACCESS
CONTENT FIELD ACCESS
PROCESS STATE
ASSIGNMENT
PRESENTATION
```

На человеческом языке:

```text
Role Permission
→ можно ли работать с Document вообще

Permission Level 1
→ какие содержательные поля можно менять

Workflow
→ какой переход состояния разрешён

Assignment / ToDo
→ кому поручена работа

Form / List / Kanban / Workspace
→ как те же данные представлены пользователю
```

Ни одна из этих осей автоматически не заменяет другую.

---

# 6. Права на Document — Level 0

Для `Service Request` учебное требование такое:

```text
Requester
→ Create Yes
→ Read own Yes
→ Write/Delete No

Technician
→ Read/Write Yes
→ Create/Delete No

Supervisor
→ Read/Write/Create Yes
→ Delete No
→ Report/Export Yes
```

Почему Requester после создания не редактирует заявку — это решение **данного сценария**, а не рекомендация для всех Frappe-систем.

---

# 7. Содержательные поля — Permission Level 1

На Level 1 находятся:

```text
subject
location
equipment
description
priority
target_date
attachment
```

Матрица:

```text
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write
```

Зачем это нужно именно здесь:

```text
Technician должен вести рабочий процесс
но не должен переписывать исходную заявку
```

Следовательно, одного `Document Write` недостаточно для выражения требования. `Permission Level` добавляет отдельную семантику доступа к полям.

---

# 8. Status до Workflow

До L7:

```text
Service Request.status
→ обычный Select
→ Permission Level 0
```

Technician и Supervisor с `Document Write` могут менять его как обычное поле.

Это намеренный учебный этап. Он позволяет доказать:

```text
Select
= набор допустимых значений

Select
≠ допустимые переходы
```

Отдельный Permission Level для `status` в курсе не вводится: до Workflow нам специально нужно увидеть обычное поле состояния, а после Workflow допустимость перехода становится ответственностью самого Workflow.

---

# 9. Workflow после L7

```text
New
 │ Accept / Supervisor
 ▼
Accepted
 │ Start Work / Technician
 ▼
In Progress
 │ Resolve / Technician
 ▼
Resolved
 │ Close / Supervisor
 ▼
Closed
```

Все состояния имеют:

```text
docstatus = 0
```

`Workflow State Field`:

```text
status
```

После включения Workflow:

```text
Workflow
→ серверно проверяет допустимость перехода

status Read Only
→ не даёт вручную редактировать поле в обычной Form

Only Allow Edit For
→ управляет редактируемостью формы в Desk
```

`Read Only` и `Only Allow Edit For` — интерфейсные ограничения, а не отдельная ACL.

---

# 10. Assignment

```text
Service Request
→ Assign To / Assignment Rule
→ ToDo
→ User
```

Ментальная модель:

```text
Assignment = ответственность
Assignment ≠ authorization
Assignment ≠ Workflow state
```

Поэтому в `Service Request` нет отдельного поля `Assigned Technician` только ради повторения уже существующего механизма.

---

# 11. Accepted

```text
Accepted
= Supervisor принял заявку в рабочий процесс
```

Это не означает автоматически:

```text
существует ToDo
назначен конкретный Technician
```

Так состояние процесса не становится скрытым дубликатом Assignment.

---

# 12. DocStatus изучается отдельно

`Service Request` не является Submittable только потому, что имеет конечное состояние `Closed`.

В Lab B отдельно сравниваются:

```text
бизнес-статус
Workflow
DocStatus Draft / Submitted / Cancelled
```

Это позволяет выбирать `Is Submittable` по транзакционному смыслу, а не по наличию слова «закрыт».

---

# 13. Автоматизация

L9 использует штатные декларативные механизмы:

```text
Notification
Assignment Rule
scheduler-triggered automation
```

Они не меняют модель прав и Workflow автоматически.

```text
Assignment Rule
→ создаёт ToDo
→ не выдаёт Permission Level 1 Write
→ не меняет Workflow state
```

Собственные `Background Jobs` и `frappe.enqueue` относятся к следующему уровню курса: в Core ученик ещё не пишет собственный Python-код.

---

# 14. Desk и Web Form — разные входы

## Desk

```text
Requester
→ Role Permission Create
→ Permission Level 1 для содержательных полей
→ обычный Document insert
```

## Web Form

В exact `v16.32.0` новый целевой `Document` создаётся отдельным Web Form path с `ignore_permissions=True`.

Поэтому:

```text
Web Form create
≠ доказательство Desk Role Permission
```

Финальная форма курса:

```text
Published = Yes
Login Required = Yes
Show List = Yes
Allow Editing After Submit = No
```

`Login Required` — аутентификация, не специальное право роли на бизнес-действие.

---

# 15. Владение конфигурацией

Курс различает четыре слоя:

```text
Standard source
universal app configuration
site-specific configuration
working data
```

## Standard source

```text
DocTypes
DocFields и permlevel
Standard Report / Number Card / Chart / Workspace
Notifications
Web Form
```

## Universal app configuration

То, что должно появиться на любом Site с приложением:

```text
Roles
Workflow
Custom DocPerm
```

поставляется через штатные fixtures/exported customizations.

## Site-specific

```text
Users
User Permission
Share
Assignment Rule с конкретными Users
```

## Working data

```text
Facility Location Documents
Equipment Documents
Service Request Documents
ToDo
Comments
Files
```

не являются исходным кодом приложения.

---

# 16. Clean-site proof

L11 проверяет не «файлы вроде закоммичены», а реальную воспроизводимость:

```text
чистый совместимый Site
+ facility_ops
+ install-app / migrate
→ обязательная модель и конфигурация приложения
```

После установки отдельно проверяются:

```text
Requester Desk create/read-own/no-write
Technician content read-only + Workflow transitions
Supervisor content/process authority + no Delete
Website User Web Form intake
```

Это ручная приёмка Core. Автоматизированные Frappe tests относятся к следующему уровню, когда появится собственная программная логика, которую действительно нужно защищать тестами.

---

# 17. Лаборатории

Labs изучают механизмы, которые не должны искусственно становиться частью предметного ядра:

```text
Child Table
DocStatus
Auto Repeat
Customize Form
Print/PDF
Single / Dynamic Link / Table MultiSelect / специальные поля и представления
```

Правило:

```text
механизм изучен
≠
сущность обязана остаться в модели
```

Если Lab затрагивает `Service Request`, после неё должны сохраниться исходные права Level 0/1 и Workflow.

---

# 18. Что сознательно остаётся на следующий уровень

```text
custom Controller
Server Script
Client Script / custom JS
custom permission hooks
Permission Types для собственных программных действий
Background Jobs / frappe.enqueue / enqueue_after_commit
Realtime API
собственный REST/RPC контракт
Query / Script Reports
автоматизированные Frappe tests
сложные интеграции
```

Они не «хуже» и не «менее Frappe-native». Просто Core сначала учит использовать возможности платформы без собственного программного слоя.

---

# 19. Итоговая архитектурная формула

```text
Facility Location
      │
      ├── Equipment
      │
      └── Service Request
              │
              ├── Role Permission → Document authority
              ├── Permission Level 1 → content authority
              ├── Workflow → transition authority
              ├── Assignment / ToDo → responsibility
              ├── File / Comment / Version → platform companions
              ├── Notification / Assignment Rule → standard automation
              └── Web Form → separate intake channel
```

Цель курса — не запомнить эту схему как шаблон.

Цель — научиться для следующего приложения заново ответить:

> **какой механизм Frappe уже владеет нужной ответственностью и действительно ли его семантика совпадает с задачей?**
