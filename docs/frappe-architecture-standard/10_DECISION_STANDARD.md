# 10. Frappe-native Decision Standard

## 1. Назначение

Этот документ — не список технологий, а обязательный protocol design review для любого Frappe-приложения.

Он отвечает на вопрос:

> **Как доказать, что архитектурное решение использует Frappe по назначению и не дублирует Framework без причины?**

---

## 2. Основной критерий

Frappe-native решение:

1. правильно определяет ответственность;
2. находит Frappe primitive, которому эта ответственность уже принадлежит;
3. проверяет совпадение semantics;
4. использует официальный extension seam, если стандартного поведения недостаточно;
5. вводит собственную abstraction только для новой ответственности.

Не является критерием:

```text
мало кода
много кода
есть Service
нет Service
всё low-code
всё Python
```

---

## 3. Responsibility matrix

| Ответственность | Нативный владелец | Нормальное расширение | Красный флаг |
|---|---|---|---|
| Structured model | DocType/Meta | Custom Field, Virtual DocType | параллельная entity model без причины |
| Свойство | DocField | custom metadata | отдельный DocType без самостоятельной semantics |
| Живая связь | Link/Dynamic Link | relation DocType | текст вместо relation без причины |
| Составные строки | Child Table | standalone DocType при собственной semantics | самостоятельный CRUD для обычных строк |
| Persistence/lifecycle | Document | Controller/services | raw DB для обычного business CRUD |
| Business invariant | server validation | domain service | только Client Script |
| Business state | field | domain logic | docstatus как универсальный status |
| Governed transitions | Workflow | custom domain state machine | десятки UI-only `if` |
| Transaction state | docstatus | Workflow integration | самодельный submit/cancel lifecycle |
| Access | Permission engine | permission hooks | параллельный ACL |
| Field access | permlevel | custom security design | JS hiding как security |
| Assignment | Assignment/ToDo | custom allocation service | своё назначение без новой semantics |
| Notification | Notification | custom messaging service | свой notification engine для простого письма |
| Async work | Background Jobs | specialized worker design | long HTTP request без причины |
| Periodic work | Scheduler | external orchestrator | свой daemon для обычной site task |
| CRUD integration | REST API | dedicated domain API | дубль CRUD endpoints |
| Document event outbound | Webhook | integration job/outbox | polling собственного Document event |
| Extension чужого DocType | hooks / extend | override/fork | patch upstream core |
| UI | Desk/Web primitives | custom frontend | UI диктует domain schema |
| Report | standard report mechanisms | BI/external analytics | report как единственный business engine |
| Schema deployment | migrate/DocType JSON | patches | ручной production SQL |
| Product configuration | fixtures/export/source | install hooks | инструкция «накликать вручную» |
| Verification | Frappe tests | integration/e2e | critical rules без проверки |

---

## 4. Decision track A: ownership

Перед техническим решением:

```text
Кому принадлежит объект/поведение?

Framework?
Другое App?
Наше App?
Конкретный Site?
External system?
```

Пока ownership не определён, нельзя правильно выбрать extension strategy.

---

## 5. Decision track B: data model

```text
Нужно хранить понятие
        ↓
Самостоятельный record?
   │             │
  нет           да
   │             │
Field         DocType
   │
   ├── living reference → Link
   ├── polymorphic reference → Dynamic Link
   ├── fixed values → Select
   └── composed repeating rows → Child Table

Один settings record на site?
        → Single

External storage должен вести себя как Documents?
        → Virtual DocType

Relation имеет собственные свойства/lifecycle?
        → relation DocType
```

Обязательно отдельно определить Naming.

---

## 6. Decision track C: state

```text
Просто состояние бизнеса?
        → status field

Нужны transitions + roles + conditions?
        → Workflow

Нужна transaction fixation?
        → Is Submittable / docstatus
```

Workflow и docstatus могут быть интегрированы, но их semantics различны.

---

## 7. Decision track D: logic placement

```text
UX формы?
        → Client Script / JS

Нельзя позволить неправильный Document?
        → Controller/server validation

Lifecycle собственного DocType?
        → Controller

Реакция на чужой DocType?
        → doc_events / extension hook

Сложная reusable orchestration?
        → service/domain module

Site-only runtime automation?
        → Server Script, если допустим инфраструктурой
```

---

## 8. Decision track E: security

```text
Права на DocType?
        → Role / DocPerm

Права на поля?
        → Permission Level

Только owner?
        → If Owner

Scope по linked master?
        → User Permission

Точечный grant?
        → Share

Сложная row policy?
        → query + document permission hooks
```

Любой bypass (`get_all`, `ignore_permissions`) требует явной причины.

---

## 9. Decision track F: transaction

```text
Обычная request operation?
        → Framework transaction

Нужен lifecycle?
        → Document API

Намеренно нужен bypass?
        → DB API с объяснением

External side effect после успешного save?
        → after_commit / enqueue_after_commit

Несколько действий должны быть atomic?
        → не разрывать ручным commit
```

---

## 10. Decision track G: async/events

```text
Долгая работа?
        → Background Job

Периодическая?
        → Scheduler

Простое пользовательское уведомление?
        → Notification

Назначение работы?
        → Assignment

Outbound HTTP на Document event?
        → Webhook
```

Если нужны reliability/retries/stateful orchestration — это новая integration responsibility.

---

## 11. Decision track H: API

```text
Обычный Document CRUD?
        → built-in REST

Команда Document?
        → document method

Application command?
        → whitelisted service method

Публичный стабильный contract?
        → dedicated API boundary
```

Custom CRUD допустим, если он реально отделяет внешний contract от внутренней model.

---

## 12. Decision track I: extension

```text
Изменение только site?
        → customization

Product change?
        → source-controlled/exported artifact

Добавить behavior чужому DocType [v16+]?
        → extend_doctype_class

Реакция на event?
        → doc_events

Полностью заменить Controller?
        → override только с доказанной необходимостью

Нельзя выразить официальным seam?
        → upstream contribution / controlled fork / custom boundary
```

---

## 13. Decision track J: UI/reporting

```text
Обычный Document UI?
        → Form/List/standard view

Desk navigation?
        → Workspace

Простой внешний ввод?
        → Web Form

Простой report?
        → Report Builder

SQL dataset?
        → Query Report

Programmatic dataset?
        → Script Report

Специализированный product UX?
        → custom frontend
```

---

## 14. Decision track K: deployment

```text
Standard model?
        → DocType source

Existing data migration?
        → Patch

Product configuration records?
        → fixtures/export/source

Site-owned customization?
        → site state

Fresh install требует ручных обязательных действий?
        → deployment design incomplete
```

---

## 15. Decision track L: testing

Критичное собственное правило должно иметь проверяемый contract.

Обязательно рассмотреть тесты для:

- invariants;
- permissions;
- workflow/state transitions;
- custom API;
- migrations;
- services;
- background jobs;
- integration idempotency.

---

## 16. Четыре обязательных вопроса design review

Для каждой новой конструкции:

```text
1. Какую конкретную ответственность она берёт?

2. Какой Frappe primitive уже ближе всего
   к этой ответственности?

3. Почему semantics этого primitive недостаточна?

4. Почему предлагаемое решение — минимальное
   достаточное расширение, а не параллельный subsystem?
```

Без ответа №3 решение не считается доказанным.

---

## 17. Дополнительные вопросы для новой abstraction

Если создаётся Service/Repository/Engine/Manager:

```text
Что исчезнет, если удалить этот слой?

Есть ли у него самостоятельная responsibility?

Или он только вызывает frappe.get_doc/doc.save?

Используется ли он несколькими owners/use cases?

Снижает ли coupling или только добавляет переходы?
```

---

## 18. Красные флаги

Фразы, требующие review:

```text
«сделаем свой ACL»
«сделаем свой workflow engine»
«обернём все DocTypes в repositories»
«напишем CRUD API на каждый DocType»
«будем обновлять через SQL, так проще»
«спрячем кнопку — значит доступа нет»
«поставим commit после каждого save»
«запустим отдельный daemon раз в минуту»
«поправим файл Frappe напрямую»
«после установки руками создадим поля»
```

Ни одно не запрещено абсолютно. Каждое требует доказательства необходимости.

---

## 19. Критерии принятия Frappe-native решения

Решение принимается, если:

- responsibility ясна;
- native primitive проверен;
- semantic fit подтверждён или недостаток описан;
- extension использует public/official seam, если он есть;
- lifecycle/security/transaction boundaries не обходятся случайно;
- deployment воспроизводим;
- critical behavior проверяем;
- исключения документированы.

---

## 20. Критерий допустимого custom mechanism

Custom mechanism оправдан, когда выполняется хотя бы одно:

- Framework вообще не владеет этой responsibility;
- штатный primitive имеет несовместимую semantics;
- нужен стабильный внешний contract;
- нужна reliability/performance model, отсутствующая в standard mechanism;
- сложность domain logic требует отдельного owner;
- extension boundary другого App требует собственного adapter/service.

---

## 21. Что не является достаточным обоснованием

```text
«так привычнее»
«так делает Clean Architecture»
«в Django мы делали repositories»
«так проще сейчас»
«так предложила LLM»
«хочу, чтобы все проекты были одинаковыми»
```

Внешняя архитектурная методология может быть полезна, но не должна автоматически отменять semantics Frappe.

---

## 22. Итоговая формула

> **Используй primitive Frappe там, где его semantics совпадает с задачей. Расширяй через официальный seam, когда стандартного поведения недостаточно. Вводи собственный subsystem только тогда, когда появляется самостоятельная ответственность.**
