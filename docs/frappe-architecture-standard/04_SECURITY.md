# 04. Security — как реально устроены permissions Frappe

## 1. Почему permissions нельзя проектировать как одну таблицу ролей

Frappe имеет несколько механизмов доступа, потому что они отвечают на разные вопросы:

```text
Role / DocPerm        → что роль может делать с DocType
Permission Level      → какие поля доступны на разных уровнях
If Owner              → меняются ли права для владельца Document
User Permission       → с какими конкретными связанными records можно работать
Share                 → ad-hoc доступ к конкретному Document
permission_query_conditions → дополнительная фильтрация list/query
has_permission        → custom document-level veto/check
```

Ошибка — включить все механизмы сразу.

Но также ошибка — считать, что они являются одной простой последовательностью runtime checks.

---

## 2. Role и DocType Permission — базовая модель

**[FRAPPE DOCS]** Role описывает, какие действия User может выполнять на DocType. DocType Permissions включают права вроде Read, Write, Create, Delete, Submit, Cancel, Amend, Report и другие.

Источник:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions

Для обычного DocType проектирование должно начинаться с вопроса:

```text
Какие роли существуют?
Что каждая роль вообще может делать с этим типом документа?
```

Пример:

```text
Request User
  Read   ✓
  Create ✓
  Write  ✓
  Delete —

Request Manager
  Read   ✓
  Create ✓
  Write  ✓
  Delete ✓
```

Это декларативная основа permission model.

---

## 3. Permission Level — доступ может отличаться по полям

**[FRAPPE DOCS]** Fields могут иметь `permlevel`, а role permissions — разрешения на соответствующем permission level.

Источник:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions

На бытовом языке:

> Пользователь может открыть карточку, но это не означает, что он имеет право читать или менять каждое поле.

Пример:

```text
Employee Request
  title       permlevel 0
  description permlevel 0
  salary      permlevel 1
```

Если salary должен быть доступен только отдельной роли, field-level permission — штатный механизм.

### Red flag

Скрыть чувствительное поле только через JavaScript.

Скрытие интерфейса не заменяет server-side permission model.

---

## 4. If Owner

**[FRAPPE DOCS]** DocPerm имеет режим `If Owner`.

Источник:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions

Он полезен для правил вида:

```text
пользователь может редактировать только свои Documents
```

### Важно

`owner` во Frappe — системный creator/owner Document. Он не обязательно совпадает с бизнес-понятием:

```text
Responsible Employee
Account Manager
Department Owner
```

Если бизнес говорит «исполнитель задачи», не нужно автоматически пытаться выразить это через `owner`.

---

## 5. User Permission

**[FRAPPE DOCS]** User Permission ограничивает пользователя по связанным Documents, обычно через Link fields.

Источник:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions

Пример:

```text
User = ivan@example.com
Allow = Company
For Value = ACME
```

После этого Company и связанные через Link данные могут ограничиваться соответствующим набором.

### Подходящий класс задач

```text
пользователь работает только с одной Company;
только с определённым Department;
только с выбранными Warehouses.
```

### Неподходящий класс задач

Сложная динамическая политика:

```text
доступ разрешён, если сумма < лимита,
проект совпадает,
договор активен,
а пользователь состоит в временной комиссии.
```

Это уже может требовать custom policy.

---

## 6. Share — точечное исключение, а не иерархическая ступень

Frappe поддерживает document sharing.

Правильная ментальная модель:

```text
Share = ad-hoc grant на конкретный Document
```

Например:

> Пользователь обычно не видит Contract, но ему временно открыли именно CONTRACT-0007.

Не нужно проектировать основную организационную модель доступа через тысячи Share records, если правило на самом деле систематическое.

---

## 7. Реальный runtime pipeline сложнее design-порядка

**[UPSTREAM]** В `version-16/frappe/permissions.py` `get_doc_permissions()`:

1. выполняет controller-level permission check;
2. получает role permissions;
3. учитывает ownership;
4. применяет User Permissions.

Top-level `has_permission()` также умеет рассмотреть explicitly shared Documents.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py

Это важно, потому что **runtime order** и **наш design escalation** — разные вещи.

---

## 8. Custom controller permission не является независимым ACL

**[UPSTREAM]** В `frappe/permissions.py` прямо записано:

> Controllers can only deny permission, they can not explicitly grant any permission that wasn't already present.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py

Это сильный архитектурный сигнал.

Custom `has_permission` — extension point существующей permission model, а не параллельный движок, который должен полностью заменить Role/DocPerm.

---

## 9. `permission_query_conditions`

**[FRAPPE DOCS]** Hook `permission_query_conditions` добавляет custom conditions к list query.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks

Документация отдельно предупреждает:

> hook влияет на `frappe.db.get_list`, но не на `frappe.db.get_all`.

Это критично.

### Типовой риск

Разработчик пишет только list filter:

```text
в списке секретный документ скрыт
```

но забывает полноценный document-level check.

Результат может выглядеть так:

```text
в List записи нет
но прямой доступ к Document проверяется другой логикой
```

**[ARCHITECTURAL INFERENCE]** Если custom row policy является security boundary, list/query filtering и document-level authorization должны проектироваться согласованно.

---

## 10. `get_list` и `get_all` — не взаимозаменяемые удобства

**[FRAPPE DOCS]** `frappe.db.get_list` применяет user permissions. `permission_query_conditions` также участвует в соответствующем query path.

Источники:

- https://docs.frappe.io/framework/user/en/api/database
- https://docs.frappe.io/framework/get_query

`get_all` используется для получения records без обычной permission filtering.

### Правило

```text
user-facing/application query
    → permission-aware path по умолчанию

system/internal operation
    → bypass допускается намеренно
```

### Red flag

Заменить `get_list` на `get_all`, потому что «не показывает нужные записи», не разобрав причину permissions.

---

## 11. `ignore_permissions=True`

Frappe позволяет внутреннему коду обходить permission checks в определённых API paths.

Это не «режим починки проблем с правами».

**[ARCHITECTURAL INFERENCE]** Bypass допустим, когда операция является системной и авторизация уже обеспечена на другой границе.

Пример:

```text
background system process создаёт технический record
после уже выполненной и проверенной business command
```

Но пользовательский endpoint:

```text
@frappe.whitelist()
def update_secret_document(...):
    doc.save(ignore_permissions=True)
```

без отдельной security проверки — серьёзный red flag.

---

## 12. Field-level security применяется и к query

**[FRAPPE DOCS]** Документация `frappe.qb.get_query` описывает permission-aware query: inaccessible fields ограничиваются в selected fields и могут запрещаться в filters/group/order.

Источник:

- https://docs.frappe.io/framework/get_query

Это ещё один аргумент не строить собственную query infrastructure без понимания permission semantics Framework.

---

## 13. Design escalation permissions

Следующая последовательность — **не runtime algorithm Frappe**.

Это **[ARCHITECTURAL INFERENCE]** для проектирования от простого штатного механизма к custom policy:

```text
1. Role + DocPerm
       ↓
2. Permission Level / If Owner
       ↓
3. User Permission
       ↓
4. Share для точечных исключений
       ↓
5. permission_query_conditions + has_permission
   для нестандартной row/document policy
       ↓
6. отдельная policy abstraction,
   только если сложность действительно требует её
```

Почему так:

- первые уровни декларативны и видимы администраторам;
- они интегрированы с Framework;
- custom code добавляется, когда стандартная модель не выражает политику.

---

## 14. Когда custom ACL/policy оправдан

Собственная policy abstraction может быть нормальной, если доступ зависит от сложной модели:

```text
роль
+ отношения между организациями
+ классификация документа
+ контракт
+ временной интервал
+ динамическая policy
```

Тогда проблема действительно шире стандартного Role/User Permission.

Но желательно подключать такую policy через официальные permission seams, чтобы Desk, API и Document access оставались согласованными с Framework.

---

## 15. Типовой неправильный сценарий

Задача:

```text
Сотрудник видит свои заявки.
Менеджер — заявки отдела.
Директор — все.
```

Новичок сразу создаёт:

```text
Custom ACL Rule
Custom ACL Department
Custom ACL User
```

и затем фильтрует SQL вручную.

Почему это плохо:

- появляется второй источник истины;
- стандартные permissions остаются активны;
- List, Report, API и direct Document access могут расходиться;
- администратору трудно объяснить итоговый доступ.

Правильный путь — сначала проверить Role/Owner/User Permission semantics, и только недостающую часть выразить custom policy.

---

## 16. Security design review

Для каждого DocType ответить:

```text
1. Какие роли имеют Read/Create/Write/Delete/Submit/Cancel?
2. Есть ли поля с отдельным permlevel?
3. Имеет ли значение системный owner?
4. Нужны ли ограничения по Link values через User Permission?
5. Нужны ли точечные Share grants?
6. Есть ли custom row-level policy?
7. Если есть permission_query_conditions — есть ли согласованный document check?
8. Какие queries permission-aware, а какие намеренно обходят permissions?
9. Где используется ignore_permissions и почему это безопасно?
10. Совпадает ли поведение Desk, REST API, Reports и background processes?
```

Security считается спроектированной только тогда, когда эти ответы известны, а не когда «форма вроде не показывает лишнее».
