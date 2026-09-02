# 11. Практические примеры

## Как читать этот раздел

Каждый пример разбирается одинаково:

```text
задача
→ что новичок обычно делает
→ почему это кажется логичным
→ Frappe-native решение
→ почему оно соответствует Framework
→ когда исключение оправдано
```

Это не каталог «запрещённых решений». Цель — научиться распознавать ответственность.

---

# Пример 1. Заявка с несколькими позициями

## Задача

Нужно хранить заявку:

```text
Заявитель
Дата
Подразделение

Позиции:
- Бумага, 10 пачек
- Ручки, 30 штук
- Картридж, 2 штуки
```

## Интуитивное решение новичка

Создать два обычных DocType:

```text
Purchase Request
Purchase Request Item
```

и вручную связывать их полем `request`.

## Почему это кажется логичным

Если человек мыслит только таблицами базы данных, он видит две таблицы и делает две самостоятельные сущности.

## Frappe-native решение

```text
Purchase Request
    └── items → Child Table → Purchase Request Item
```

## Почему

Строки являются составной частью одного Document. Child DocType специально имеет parent semantics и порядок строк.

## Что усложнит отдельный обычный DocType

Придётся отдельно думать о:

- permissions;
- удалении orphan rows;
- связи с parent;
- порядке;
- UI;
- lifecycle.

## Когда отдельный DocType правильнее

Если строка получает собственный lifecycle, permissions, ссылки из других Documents или должна жить независимо от заявки.

---

# Пример 2. Автомобиль и его цвет

## Задача

Есть карточка автомобиля.

## Ошибка

Создать:

```text
Vehicle
Vehicle Color
Vehicle Model Name
Vehicle Registration Number
```

как отдельные DocTypes просто потому, что это отдельные понятия.

## Frappe-native решение

```text
Vehicle
    registration_number → Data
    color               → Select/Data/Link по реальной семантике
    model               → field или Link, если Model — самостоятельный master
```

## Почему

DocType имеет стоимость и должен иметь самостоятельный смысл.

## Исключение

Если `Vehicle Model` — управляемый справочник с производителем, характеристиками, нормативами и множеством ссылок, отдельный DocType совершенно оправдан.

---

# Пример 3. Рабочий статус задачи

## Задача

```text
New
In Progress
Waiting
Done
```

## Ошибка

Сделать DocType `Is Submittable` и использовать `docstatus` как эти четыре состояния.

## Почему кажется логичным

Новичок видит слово status и предполагает, что системный `docstatus` предназначен для любых статусов.

## Frappe-native решение

Обычное business field:

```text
status
```

## Почему

`docstatus` имеет другую системную semantics:

```text
Draft
Submitted
Cancelled
```

Он описывает transaction state Document.

## Исключение

Если документ после подтверждения должен действительно перейти в фиксированное transaction state, `Is Submittable` может быть именно тем, что нужно.

---

# Пример 4. Согласование руководителем

## Задача

```text
Draft
  ↓ сотрудник отправляет
Manager Review
  ↓ руководитель утверждает
Approved
```

## Ошибка

Обычный Select `status` плюс Client Script:

```text
если user имеет роль Manager
покажи кнопку Approve
```

## Почему кажется логичным

На форме всё работает, и процесс выглядит контролируемым.

## Проблема

Кнопка — только UI. Другой API path может изменить поле напрямую.

## Frappe-native решение

Сначала рассмотреть Workflow:

```text
states
transitions
roles
conditions
```

## Исключение

Если согласование строится на сложной динамической матрице, которую Workflow выражает только огромными непрозрачными conditions, отдельная domain logic может быть лучше.

---

# Пример 5. Проверка дат

## Задача

Дата окончания не может быть раньше даты начала.

## Ошибка

Проверить только Client Script.

## Почему кажется достаточным

Пользователь получает сообщение сразу на форме.

## Проблема

Документ можно сохранить через API/background Python path без этой формы.

## Frappe-native решение

```text
Client Script
    → ранняя UX-подсказка

Controller.validate
    → server guarantee
```

## Исключение

Если правило относится только к поведению конкретного UI и не является invariant данных, server validation может быть не нужна.

---

# Пример 6. Права обычного сотрудника

## Задача

Сотрудник видит свои заявки, руководитель — заявки подразделения, директор — все.

## Ошибка

Сразу создать:

```text
Custom Access Rule
Custom Department ACL
Custom User Scope
```

и фильтровать SQL вручную.

## Почему кажется логичным

Организационная структура выглядит специфичной для компании.

## Frappe-native начало

Проверить:

```text
Role / DocPerm
If Owner
User Permission по Department
```

и только затем custom policy.

## Почему

Framework уже централизует access model.

## Исключение

Сложная relational/attribute-based policy вполне может требовать permission hooks.

---

# Пример 7. Скрыли поле — значит защитили

## Задача

Обычный сотрудник не должен видеть зарплату.

## Ошибка

Скрыть поле JavaScript'ом.

## Почему кажется логичным

На экране поля нет.

## Проблема

UI visibility не равна server-side security.

## Frappe-native решение

Рассмотреть field Permission Level и server permission model.

## Исключение

UI hiding может дополнительно улучшать UX, но не заменяет access control.

---

# Пример 8. Собственный CRUD API

## Задача

Мобильное приложение должно создавать и изменять `Request`.

## Ошибка

Сразу написать:

```text
/create_request
/get_request
/update_request
/delete_request
```

## Почему кажется логичным

В обычной backend-разработке API проектируется вручную.

## Frappe-native default

Для внутреннего Frappe-aware клиента сначала проверить standard Document REST API.

## Почему

Он уже предоставляет CRUD и использует Document lifecycle/permissions.

## Когда custom API правильный

Если мобильному приложению обещан стабильный domain contract, который не должен зависеть от внутренней DocType schema.

---

# Пример 9. Бизнес-команда через API

## Задача

Нужно выполнить:

```text
dispatch_shipment
```

Команда:

- проверяет Shipment;
- создаёт несколько Documents;
- вызывает внешний сервис;
- меняет status.

## Ошибка

Пытаться выразить это четырьмя generic PATCH requests с клиента.

## Frappe-native решение

Создать серверную business command / whitelisted method, которая владеет operation boundary.

## Почему

Это уже не CRUD одного Document.

---

# Пример 10. Уведомление по сроку

## Задача

За три дня до срока отправить ответственному письмо.

## Ошибка

Создать собственный scheduler + mail service для одного простого правила.

## Frappe-native default

Проверить Notification/date-event capabilities.

## Исключение

Если нужен сложный multi-channel notification engine с retries/provider routing, отдельный subsystem может быть оправдан.

---

# Пример 11. Тяжёлый пересчёт

## Задача

Пользователь запускает перерасчёт 200 000 строк.

## Ошибка

Выполнить всё внутри HTTP request и заставить browser ждать.

## Frappe-native решение

Background Job.

## Дополнительные вопросы

- idempotency;
- deduplication;
- timeout;
- очередь;
- что делать после failure;
- должен ли job стартовать только после commit.

---

# Пример 12. Ночной пересчёт

## Задача

Раз в ночь пересчитывать технический показатель.

## Ошибка

Отдельный Python daemon:

```python
while True:
    sleep(...)
```

## Frappe-native default

Scheduler event.

## Исключение

Если job является частью внешней enterprise orchestration и управляет несколькими системами, внешний scheduler может быть правильным.

---

# Пример 13. Отправить Document во внешнюю систему

## Задача

После submit нужно сообщить внешнему сервису.

## Ошибка

В `on_submit` сразу выполнить HTTP request, не учитывая transaction.

## Риск

Внешняя система получит событие, а локальная transaction позже rollback.

## Frappe-native решение

Рассмотреть:

```text
Webhook
```

для простого event и/или

```text
after_commit / enqueue_after_commit
```

для контролируемой integration operation.

---

# Пример 14. Изменить стандартный DocType

## Задача

Добавить поведение существующему DocType другого App.

## Ошибка

Отредактировать его Python-файл напрямую.

## Frappe-native решение

Проверить:

```text
Custom Field
Property Setter
doc_events
extend_doctype_class [v16+]
doctype JS
```

в зависимости от responsibility.

## Когда fork оправдан

Когда требуемая semantics принципиально не может быть расширена официальными seams, а команда сознательно принимает стоимость поддержки fork.

---

# Пример 15. Service class

## Ошибка формулировки

> «Services во Frappe запрещены».

Это неверно.

ERPNext сам использует service modules для сложной domain logic.

## Плохой Service

```text
RequestService.save()
    → request.save()
```

Просто переименование API.

## Хороший Service

Компонент, который координирует несколько Documents, сложный расчёт или integration responsibility.

---

# Пример 16. Repository

## Плохой вариант

```text
TaskRepository.get()
    → frappe.get_doc()

TaskRepository.save()
    → doc.save()
```

Если это весь смысл слоя, он не добавляет ответственности.

## Нормальный вариант

Repository/adapter, который действительно скрывает несколько storage backends или сложную aggregate persistence.

---

# Пример 17. Ручная production-настройка

## Задача

App требует:

- 6 Custom Fields;
- Workflow;
- 2 Notifications.

## Ошибка

README:

```text
после установки создайте всё вручную
```

## Правильное решение

Если это часть продукта — configuration должна доставляться source-controlled штатным механизмом.

Контроль:

```text
clean site
+ install-app
+ migrate
=
required state
```

---

# Пример 18. Migration данных

## Задача

Переименовали модель status и нужно преобразовать существующие values.

## Ошибка

После deploy вручную выполнить SQL.

## Frappe-native решение

Versioned patch/migration вместе с App.

## Почему

Upgrade должен быть воспроизводим.

---

# Пример 19. `get_all`, потому что permissions мешают

## Задача

В custom page список оказался пустым.

## Ошибка

Заменить permission-aware query на `get_all`.

## Почему кажется рабочим

Данные появились.

## Что реально произошло

Security boundary была выключена.

## Правильный вопрос

Почему пользователь не имеет access и какая permission semantics нужна page?

---

# Пример 20. Snapshot vs Link

## Задача

Invoice должен сохранить адрес клиента таким, каким он был при выставлении.

## Ошибка

Считать любое копирование значения «денормализацией-костылём» и хранить только Link на текущий Address.

## Правильная модель

Живая ссылка и historical snapshot могут существовать одновременно, потому что отвечают на разные вопросы.

---

# Короткая памятка новичку

Если не понимаешь, с чего начать, задавай вопросы в таком порядке:

```text
1. Что это за реальный объект/процесс?
2. Кто владеет этой ответственностью?
3. Есть ли для неё прямой primitive Frappe?
4. Совпадает ли его смысл с задачей?
5. Если нет — какой официальный extension point ближе всего?
6. Что именно наша собственная конструкция добавляет нового?
```

Главная ошибка — не custom code.

Главная ошибка — **не заметить, что Framework уже решает ту же самую задачу, и построить рядом второй механизм**.
