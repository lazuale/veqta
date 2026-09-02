# 11. Практические примеры — правильные и неправильные решения

Этот раздел написан для человека без технического бэкграунда.

Здесь не приводится выдуманная статистика «90% проектов». Выбраны наиболее повторяющиеся классы задач обычных business applications: карточки, строки документа, статусы, согласование, права, проверки, API, уведомления, фоновые задачи и расширение чужих DocType.

Для каждого примера используется одна схема:

```text
Задача
Интуитивная ошибка
Почему она кажется логичной
Frappe-native решение
Почему именно так
Что ухудшится при обходе Framework
Когда исключение оправдано
```

---

# Правильный пример 1. Заявка с несколькими позициями

## Задача

Есть заявка на закупку:

```text
Заявитель: Иван
Дата: 02.09.2026

Позиции:
- Бумага, 10 пачек
- Ручки, 50 шт.
- Картридж, 2 шт.
```

## Интуитивная ошибка

Создать две полностью самостоятельные системы карточек:

```text
Purchase Request
Purchase Request Item
```

и потом программировать связь между ними вручную.

## Почему кажется логичной

Если смотреть на обычную базу данных, видны две таблицы: заявка и строки.

## Frappe-native

```text
Purchase Request
  └─ items: Table → Purchase Request Item (Child DocType)
```

## Почему

**[FRAPPE DOCS]** Child DocType специально предназначен для records, являющихся частью parent Document.

Пруф:

- https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype

Framework сам хранит parent, parenttype, parentfield и порядок `idx`.

## Что ухудшится при обходе

Придётся самостоятельно решать:

- кому принадлежит строка;
- как удалять её вместе с parent;
- как хранить порядок;
- как показывать её в форме;
- как не оставить «осиротевшую» строку.

## Когда исключение оправдано

Если «позиция» должна жить самостоятельно, иметь свои права, использоваться несколькими documents и открываться отдельно — это уже может быть обычный DocType.

---

# Правильный пример 2. Простая задача с четырьмя состояниями

## Задача

```text
New → In Progress → Waiting → Done
```

Пользователь имеет право самостоятельно менять состояние.

## Интуитивная ошибка

Сразу строить Workflow и пытаться использовать `docstatus`.

## Почему кажется логичной

Workflow и docstatus тоже связаны со «статусами», поэтому кажется, что это более серьёзный способ.

## Frappe-native

Обычный business field `status`.

## Почему

`docstatus` имеет специальную transaction semantics:

```text
Draft / Submitted / Cancelled
```

**[FRAPPE DOCS]** Пруф:

- https://docs.frappe.io/framework/doctypes/docstatus

Workflow нужен, когда важны контролируемые transitions/roles/conditions, а не просто список значений.

## Что ухудшится при обходе

Модель станет сложнее, а системный Submitted будет ошибочно означать обычное «Done».

## Когда исключение оправдано

Если переходы зависят от роли или approval — появляется основание для Workflow.

---

# Правильный пример 3. Заявку должен одобрить руководитель

## Задача

```text
Draft
  ↓ сотрудник
Manager Review
  ↓ руководитель
Approved
```

## Интуитивная ошибка

Сделать Select `status`, а в Client Script написать:

```text
если пользователь manager — покажи Approve
если employee — спрячь
```

## Почему кажется логичной

На экране всё выглядит правильно: сотрудник не видит кнопку.

## Frappe-native

Рассмотреть Workflow.

## Почему

Workflow описывает states, transitions, roles и conditions — именно то, что требуется задаче.

Пруф:

- https://docs.frappe.io/erpnext/user/manual/en/workflows

## Что ухудшится при обходе

UI может скрывать кнопку, но другой API/client способен поменять status. Правила оказываются привязаны к форме, а не к процессу.

## Когда исключение оправдано

Если схема согласования динамическая и существенно сложнее штатных states/transitions/conditions, отдельная domain orchestration может быть лучше.

---

# Правильный пример 4. Нельзя сохранить неправильную дату

## Задача

```text
end_date >= start_date
```

## Интуитивная ошибка

Проверить только Client Script.

## Почему кажется логичной

Пользователь получает ошибку сразу, и при ручном тесте всё работает.

## Frappe-native

Server-side validation в Document/controller path. Client Script можно оставить как дополнительную подсказку.

## Почему

**[FRAPPE DOCS]** Client Script validation работает только в standard browser form.

Пруфы:

- https://docs.frappe.io/framework/user/en/desk/scripting/client-script
- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers

## Что ухудшится при обходе

Неправильная запись может прийти через API/import/server process.

## Когда исключение оправдано

Если правило действительно только визуальное и неправильное значение на сервере допустимо — server validation не нужна.

---

# Правильный пример 5. Сотрудник видит только свою Company

## Задача

Пользователь работает только с `Company = ACME`.

## Интуитивная ошибка

Сразу писать собственный SQL-фильтр во всех списках.

## Frappe-native

Сначала проверить Role/DocPerm + User Permission.

## Почему

**[FRAPPE DOCS]** User Permission предназначен для ограничения пользователя по связанным records.

Пруф:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions

## Что ухудшится при обходе

Custom фильтр нужно будет поддерживать отдельно в list, report, API и direct document access.

## Когда исключение оправдано

Если политика зависит не от обычных linked records, а от сложного динамического набора правил — custom permission logic может быть оправдана.

---

# Правильный пример 6. Внешняя программа должна создать обычную заявку

## Задача

Внутренняя программа отправляет поля нового `Request` во Frappe.

## Интуитивная ошибка

Написать новый endpoint `/api/request/create`, который просто делает `doc.insert()`.

## Frappe-native

Использовать стандартный Document REST API.

## Почему

**[FRAPPE DOCS + UPSTREAM]** Frappe автоматически предоставляет CRUD API DocTypes; v16 REST path создаёт Document через `insert()`.

Пруфы:

- https://docs.frappe.io/framework/user/en/api/rest
- https://github.com/frappe/frappe/blob/version-16/frappe/api/v2.py

## Что ухудшится при обходе

Появится второй endpoint с собственной документацией, permission handling и tests, хотя он не добавляет нового смысла.

## Когда исключение оправдано

Если нужен стабильный public contract, скрывающий внутренний DocType, — dedicated API нормален.

---

# Правильный пример 7. Нужно сообщить внешней системе об обновлении документа

## Задача

После `Quotation.on_update` отправить HTTP callback в другую систему.

## Интуитивная ошибка

Написать scheduler, который каждые 5 минут ищет изменённые Quotations.

## Frappe-native

Сначала проверить Webhook.

## Почему

**[FRAPPE DOCS]** Webhook именно связывает Document Event и HTTP callback.

Пруф:

- https://docs.frappe.io/framework/user/en/guides/integration/webhooks

## Что ухудшится при обходе

Polling создаёт задержку, лишние запросы и собственную логику поиска изменений.

## Когда исключение оправдано

Если нужны delivery guarantees, replay, сложные retries и reconciliation, отдельная integration pipeline может быть необходима.

---

# Правильный пример 8. Тяжёлый расчёт после сохранения

## Задача

После создания документа нужно обработать 50 000 строк.

## Интуитивная ошибка

Выполнять весь цикл прямо в кнопке Save.

## Frappe-native

Сохранить Document и поставить работу в Background Job; если job должна видеть только committed data — использовать `enqueue_after_commit`.

## Почему

**[FRAPPE DOCS + UPSTREAM]** Frappe имеет background job system и transaction-aware enqueue.

Пруфы:

- https://docs.frappe.io/framework/user/en/api/background_jobs
- https://github.com/frappe/frappe/blob/version-16/frappe/utils/background_jobs.py

## Что ухудшится при обходе

Долгий HTTP request, timeout, длинные locks, плохой UX.

## Когда исключение оправдано

Если операция короткая и пользователю нужен синхронный результат, background job может только усложнить flow.

---

# Неправильный пример 1. «Сделаем свой ACL сразу»

## Задача

Сотрудник видит свои документы, менеджер — отдел, директор — все.

## Решение

Создаются:

```text
Our Permission Rule
Our Permission Role
Our Permission Department
```

и собственные SQL conditions.

## Почему это опасно

Frappe уже имеет Role/DocPerm, owner, User Permission, Share и permission hooks.

Появляются две системы доступа:

```text
Frappe permissions
+
Our permissions
```

Теперь нужно объяснить итог каждого запроса как пересечение двух моделей.

## Правильный подход

Сначала выразить максимум штатными mechanisms, а custom code использовать только для недостающей row policy.

Пруфы:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py

---

# Неправильный пример 2. «Спрячем поле JavaScript — значит доступа нет»

## Задача

Поле `salary` должен видеть только HR.

## Решение

Client Script скрывает field для остальных.

## Почему неправильно

UI visibility не является permission boundary.

Frappe имеет Permission Level/field-level security.

Пруф:

- https://docs.frappe.io/framework/user/en/basics/users-and-permissions

## Правильный подход

Настроить server-side permission model; UI может дополнительно отражать её.

---

# Неправильный пример 3. `get_all`, потому что `get_list` «ничего не возвращает»

## Задача

Разработчик ожидает увидеть records, но `get_list` их фильтрует.

## Решение

Заменить на `get_all`.

## Почему неправильно

Причина может быть именно в permissions. Обход проблемы превращается в bypass access control.

Пруфы:

- https://docs.frappe.io/framework/user/en/api/database
- https://docs.frappe.io/framework/user/en/python-api/hooks

## Правильный подход

Сначала понять permission model. `get_all` использовать только в осознанном internal/system context.

---

# Неправильный пример 4. `frappe.db.set_value()` вместо Document save

## Задача

Нужно изменить бизнес-поле.

## Решение

Direct DB update, потому что короче.

## Почему неправильно

**[FRAPPE DOCS]** `set_value` не запускает ORM triggers вроде `validate` и `on_update`.

Пруф:

- https://docs.frappe.io/framework/user/en/api/database

## Последствие

Business invariants могут быть обойдены.

## Когда нормально

Технический field или намеренный migration/internal update, где bypass осознан.

---

# Неправильный пример 5. Ручной `commit()` после каждого шага

## Задача

Операция создаёт три связанных документа.

## Решение

После каждого `insert()` делается `frappe.db.commit()` «для надёжности».

## Почему неправильно

Frappe уже имеет request transaction. Если третий шаг упадёт, первые два изменения могут остаться committed.

Пруф:

- https://docs.frappe.io/framework/user/en/api/database

## Правильный подход

Позволить Framework завершить атомарную transaction, если нет отдельной причины дробить её.

---

# Неправильный пример 6. Правка core-файла

## Задача

Нужно добавить одну проверку к стандартному DocType другого App.

## Решение

Изменить его `.py` файл прямо в `apps/frappe` или `apps/erpnext`.

## Почему неправильно как default

Frappe предоставляет hooks, `doc_events`, `extend_doctype_class` и override mechanisms.

Пруф:

- https://docs.frappe.io/framework/user/en/python-api/hooks

## Последствие

Upgrade conflict, потеря воспроизводимости и зависимость от локально изменённого installed source.

## Когда fork оправдан

Когда организация сознательно поддерживает собственную distribution и принимает постоянный merge cost.

---

# Неправильный пример 7. Обязательные настройки остаются только на dev-site

## Задача

Для работы App нужны 12 Custom Fields, Workflow и Role.

## Решение

Инструкция после установки:

```text
зайдите в Customize Form
создайте поля
потом создайте Workflow
потом настройте права
```

## Почему неправильно для app-owned состояния

Новый site не воспроизводится из repository.

Frappe имеет fixtures, export customizations, DocType JSON и migrations.

Пруфы:

- https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- https://docs.frappe.io/framework/user/en/python-api/hooks#fixtures
- https://docs.frappe.io/framework/user/en/guides/deployment/migrations

## Когда ручная настройка нормальна

Когда это сознательно site-owned configuration, которую каждый заказчик должен выбирать самостоятельно.

---

# Неправильный пример 8. Service ради названия Service

## Задача

Нужно сохранять Task.

## Решение

```text
TaskService
  save(task) → task.save()

TaskRepository
  get(name) → frappe.get_doc("Task", name)
```

## Почему подозрительно

Document уже предоставляет persistence/lifecycle abstraction. Новые слои пока не добавляют ответственности.

## Правильный подход

Не создавать слой до появления реальной причины.

## Когда Service становится правильным

Если появляется сложная операция нескольких Documents. First-party ERPNext сам использует service classes для таких задач:

- https://github.com/frappe/erpnext/blob/develop/erpnext/stock/services/stock_ledger_service.py

---

# Итог для новичка

Перед новым механизмом не спрашивай:

> «Как программисты обычно это делают?»

Сначала спроси:

> **«Есть ли во Frappe механизм именно с таким смыслом?»**

Если есть — используй его как starting point.

Если не хватает — выясни, что именно не хватает.

Только после этого появляется основание писать собственную конструкцию.
