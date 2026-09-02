# 04. Security

## 1. Почему permissions нужно проектировать отдельно

Frappe имеет много механизмов доступа:

- Roles;
- DocType Permissions;
- Permission Level;
- If Owner;
- User Permissions;
- Sharing;
- query-time restrictions;
- controller permission hooks;
- explicit bypass mechanisms.

Если воспринимать их как случайный набор «танцев», очень легко построить параллельный ACL.

Правильнее разделить:

```text
runtime permission model
```

и

```text
design escalation
```

Это не одно и то же.

---

## 2. Role и DocType Permission

Role отвечает на базовый вопрос:

> **Что пользователь этой роли вообще может делать с этим DocType?**

Типовые rights:

```text
read
write
create
delete
submit
cancel
amend
print
email
report
import
export
share
```

Это основа permission design обычного приложения.

---

## 3. Permission Level

Доступ может различаться не только на уровне всего Document, но и отдельных полей.

Например:

```text
Employee
    public fields      permlevel 0
    salary             permlevel 1
```

Роль может иметь read access к Employee, но не к полям более высокого permission level.

### Архитектурный вывод

Не нужно автоматически создавать отдельный DocType только ради ограничения пары чувствительных полей.

Сначала нужно проверить field-level permissions.

### Граница

Если чувствительная часть имеет самостоятельный lifecycle или самостоятельную security boundary, отдельный DocType всё-таки может быть лучше.

---

## 4. If Owner

`If Owner` позволяет ограничить часть прав документами, которыми пользователь владеет.

Пример:

```text
Employee Request User
    read   if owner
    write  if owner
```

Это естественный механизм для сценария:

> пользователь работает только со своими Documents.

### Но owner имеет конкретную semantics

Owner — системное поле создания/владения Document.

Не следует автоматически приравнивать его к:

```text
responsible_user
manager
assignee
account_owner
```

Это могут быть другие бизнес-понятия.

---

## 5. User Permission

User Permission ограничивает пользователя определёнными связанными Documents.

Пример:

```text
User = ivan@example.com
Allow = Company
For Value = ACME
```

Если бизнес-документы содержат Link на Company, Framework может учитывать это ограничение.

Это полезно для organizational/data scope.

---

## 6. User Permission не является обычной Role

Role:

> что можно делать?

User Permission:

> с какими связанными данными можно это делать?

Это разные измерения access control.

Попытка выразить оба вопроса сотнями Roles часто приводит к explosion ролей.

---

## 7. Sharing

Sharing — ad-hoc document-level grant.

То есть конкретный Document можно поделиться конкретному пользователю.

Хорошая бытовая аналогия:

```text
общие правила офиса
    → Roles

тебе разрешили доступ
к конкретной папке
    → Share
```

### Следствие

Share хорошо подходит для исключений.

Плохо строить на нём основную predictable organizational permission model, если она должна вычисляться системно.

---

## 8. Runtime permission pipeline

Важно не путать рекомендуемый порядок проектирования с реальным алгоритмом Framework.

В упрощённом виде document-level permission evaluation включает:

```text
controller permission veto
        ↓
role permissions
        ↓
owner rules
        ↓
User Permissions
        ↓
sharing / document-level grants
```

Плюс отдельные query/filter и field-level механизмы.

Это упрощённая схема для понимания, а не полный псевдокод `permissions.py`.

---

## 9. Controller permission hooks

Custom `has_permission` logic может дополнительно ограничить доступ.

Критически важно: upstream Framework прямо задаёт semantics, при которой controller permission checks могут **запретить** доступ, но не должны использоваться как независимый механизм выдачи прав, отсутствующих в базовой permission model.

### Архитектурное следствие

Custom permission code — не замена DocPerm.

Это extension point для дополнительной domain policy.

---

## 10. Design escalation

Это уже рекомендация стандарта, а не runtime algorithm.

Начинать проектирование стоит так:

```text
Role + DocPerm
        ↓
Permission Level / If Owner
        ↓
User Permission
        ↓
Share для точечных исключений
        ↓
custom query/document policy
```

Причина проста:

первые механизмы declarative и встроены во всю Framework permission model.

Custom logic вводится тогда, когда policy действительно нельзя естественно выразить ими.

---

## 11. Почему ранний custom ACL опасен

Допустим, приложение создаёт:

```text
Our Role
Our Permission Rule
Our Department Access
Our User Scope
```

и проверяет всё собственными SQL-фильтрами.

Теперь существуют две системы:

```text
Frappe permissions
+
Our permissions
```

При debugging нужно одновременно отвечать:

> Кто разрешил?
> Кто запретил?
> Где фильтруется list?
> Где проверяется direct read?

Это резко повышает сложность безопасности.

---

## 12. Когда custom permission policy действительно нужна

Например:

```text
доступ разрешён,
если user связан с contract party,
security level <= clearance,
document не находится под legal hold,
и временное окно ещё действует
```

Такая policy уже выходит за простой Role/User Permission model.

Custom permission hook оправдан.

Но он должен **интегрироваться** с Frappe permission system, а не создавать параллельную auth platform.

---

## 13. List permission и direct document permission

Один из самых опасных классов ошибок:

```text
в списке запись скрыта
но по прямому URL доступна
```

Это происходит, когда разработчик ограничил только query/list surface.

### Design requirement

Custom row-level policy должна быть проверена минимум в двух направлениях:

```text
collection/list query
single-document access
```

Если используется query condition hook, нужно проверить соответствующую document-level permission semantics.

---

## 14. permission_query_conditions

Этот extension point предназначен для добавления query restrictions.

Он полезен, когда пользователь должен видеть только subset records.

Пример:

```text
Project Member видит только Projects,
где он участник
```

### Красный флаг

Не считать query condition полноценной security policy без проверки direct document access.

---

## 15. has_permission

`has_permission` решает document-level policy.

Его естественно использовать вместе с query restrictions, когда одна и та же domain policy должна действовать и для списков, и для конкретного Document.

### Требование

Логика двух механизмов не должна расходиться.

---

## 16. `get_list` и permission-aware queries

При обычной пользовательской выборке следует использовать APIs, которые применяют permissions.

Если код получает Documents для пользовательского интерфейса, query должен уважать security model.

Это часть application boundary.

---

## 17. `get_all` и permission bypass

`get_all` и аналогичные bypass capabilities полезны во внутреннем системном коде.

Но их использование должно быть осознанным.

Плохой мотив:

> «get_list ничего не возвращал из-за прав, поэтому заменил на get_all».

Это не исправление query.

Это отключение security boundary.

---

## 18. `ignore_permissions=True`

То же правило.

Иногда system process действительно должен работать с правами системы.

Например:

- scheduled maintenance;
- migration;
- controlled internal service;
- administrative process.

Но permission bypass должен иметь явный reason.

### Review question

> Кто является security principal этой операции и почему обычные permissions здесь неприменимы?

---

## 19. Administrator

Administrator имеет специальный системный статус и не является нормальной пользовательской role model.

Нельзя тестировать безопасность только под Administrator.

Иначе значительная часть реальных permission paths вообще не проверяется.

---

## 20. API не отменяет permissions

Встроенный Document API выполняет permission checks.

Но custom whitelisted method может сам сделать:

```python
frappe.get_all(...)
```

или

```python
doc.save(ignore_permissions=True)
```

Поэтому наличие authentication на endpoint ещё не означает корректную authorization.

### Design question

> Как именно custom endpoint применяет permissions к business action?

---

## 21. Assignment не является permission

Пользователь может быть назначен на Document через Assignment/ToDo, но это не нужно автоматически воспринимать как универсальный access rule.

Если бизнес требует:

> assignee получает read/write

это отдельная domain permission policy, которую нужно выразить и проверить.

Не предполагать, что assignment semantics автоматически равны authorization semantics.

---

## 22. Workflow role не заменяет DocPerm

Workflow может определять, кто способен выполнить transition.

Но пользователь всё ещё должен иметь базовый доступ к Document согласно permission model.

То есть:

```text
Workflow permission
```

и

```text
Document permission
```

решают связанные, но разные задачи.

---

## 23. Field visibility не равна security

Скрыть поле JavaScript'ом:

```text
frm.set_df_property(..., "hidden", 1)
```

не означает защитить данные.

Security должна обеспечиваться server-side permission model.

UI hiding — presentation.

---

## 24. Sensitive data

Для чувствительных данных нужно отдельно рассмотреть:

- field permlevel;
- masking capabilities;
- API serialization;
- reports;
- exports;
- print formats;
- logs;
- attachments.

Security модели Document недостаточно, если данные затем случайно раскрываются в отчёте или custom API.

---

## 25. Child permissions

Child records входят в permission context parent Document.

Не следует считать Child Table независимой security boundary.

Если каждой строке нужен отдельный access control, это ещё один сигнал, что Child DocType может быть неправильной data model.

---

## 26. Permission tests

Сложная permission model обязательно должна тестироваться не только под Administrator.

Минимальная матрица:

```text
Role A
Role B
Owner
Non-owner
Allowed User Permission
Disallowed User Permission
Shared document
Direct URL
List query
API access
```

---

## 27. Бытовой пример

Требование:

> Обычный сотрудник видит свои заявки. Руководитель видит заявки своего подразделения. Директор видит всё.

### Не начинать с

```text
Custom ACL table
```

### Начать с анализа

```text
Employee:
    Role + If Owner?

Manager:
    Role + User Permission by Department?

Director:
    broad Role permission?
```

И только если реальная модель отдела не выражается стандартными relations, добавлять custom policy.

---

## 28. Другой пример

Требование:

> Пользователь может открыть Contract только если он является участником хотя бы одного Project, связанного с Contract.

Это уже relational rule, которая может плохо выражаться простыми User Permissions.

Custom query/document policy здесь может быть совершенно оправданной.

---

## 29. Security decision track

```text
Нужно право на весь DocType?
        → Role / DocPerm

Нужно ограничить поля?
        → Permission Level

Только собственные Documents?
        → If Owner

Ограничение по связанным masters?
        → User Permission

Точечный доступ к конкретному Document?
        → Share

Сложная domain row policy?
        → permission_query_conditions
          + document-level permission logic

Системная операция должна обходить user ACL?
        → explicit controlled bypass
```

---

## 30. Design review checklist

- [ ] Role/DocPerm определены до custom ACL.
- [ ] Permission Level рассмотрен для sensitive fields.
- [ ] Owner не перепутан с assignee/responsible.
- [ ] User Permission используется только там, где relation semantics совпадает.
- [ ] Share используется для точечных grants, а не как основная organizational model.
- [ ] Runtime pipeline не перепутан с design escalation.
- [ ] Query restrictions проверены вместе с direct access.
- [ ] `get_all`/`ignore_permissions` имеют явное обоснование.
- [ ] Workflow role не считается заменой Document permission.
- [ ] UI hiding не считается security.
- [ ] Custom API применяет authorization явно.
- [ ] Permission matrix покрыта тестами обычных пользователей.
