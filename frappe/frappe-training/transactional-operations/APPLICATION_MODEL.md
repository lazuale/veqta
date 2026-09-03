# Модель и учебный сценарий

Практикум продолжает `rental_training`. Предыдущая предметная модель сохраняется:

```text
Equipment
Customer
Rental
└── Rental Item
```

Новое требование появляется не из-за нехватки полей, а из-за нехватки самостоятельного бизнес-факта:

> После фактической выдачи или возврата нужно сохранить журнал движения каждого Equipment и согласованно изменить состояние Rental.

## Equipment Movement

Добавляется Standard DocType:

```text
Equipment Movement
├── equipment     → Link → Equipment
├── rental        → Link → Rental
├── movement_type → Select: Issue / Return
└── movement_at   → Datetime
```

Naming:

```text
MOVE-.#####
```

### Почему это отдельный Document

`Equipment Movement` имеет самостоятельный смысл:

- представляет отдельный факт выдачи или возврата конкретного Equipment;
- имеет собственное время;
- относится одновременно к Rental и Equipment;
- должен оставаться доступным как история конкретного Equipment;
- не является просто временной строкой формы Rental.

Поэтому он не становится дополнительным полем `Rental` и не превращается в Child DocType только потому, что один Rental создаёт несколько движений.

## Кто создаёт Movement

`Equipment Movement` — системно сформированный журнал.

Пользователь не должен вручную создавать, переписывать или удалять записи движения через обычный Desk.

В учебной модели:

```text
Rental Manager
→ Read Equipment Movement

Rental Operator
→ без прямого доступа к Equipment Movement
```

На `Create`, `Write` и `Delete` прикладным ролям permission не выдаётся.

Movement создаётся только внутри уже авторизованной команды Rental.

Это даёт важную границу:

```text
пользователь имеет write на конкретный Rental
        ↓
серверная команда проверяет это право
        ↓
после проверки команда внутренне создаёт Movement
```

Для внутренней вставки используется:

```python
doc.insert(ignore_permissions=True)
```

Здесь `ignore_permissions=True` не является способом «починить» отказ в доступе. Авторизация уже выполнена на границе бизнес-команды через:

```python
self.check_permission("write")
```

Если такой предварительной проверки нет, внутренний bypass превращается в уязвимость.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/document

## Явные команды Rental

До этого `status` Rental можно было менять как обычное предметное поле:

```text
Planned
Active
Returned
```

После появления журнала простой переход статуса уже недостаточен.

Теперь изменение:

```text
Planned → Active
```

означает бизнес-операцию:

```text
Issue Rental
```

а:

```text
Active → Returned
```

означает:

```text
Return Rental
```

Поэтому на Controller появляются две явные команды:

```python
@frappe.whitelist()
def issue(self):
    ...

@frappe.whitelist()
def return_equipment(self):
    ...
```

Form вызывает их через `frm.call()`.

Первичный источник для `frm.call`:

- https://docs.frappe.io/framework/user/en/api/form

## Почему не on_update

Можно было бы спрятать создание Movement в `on_update` и проверять, изменился ли `status`.

Но тогда самостоятельная операция «выдать Rental» растворяется внутри общего события сохранения.

Для текущей задачи яснее разделить:

```text
обычное редактирование Rental
≠
выдача Rental
≠
возврат Rental
```

Поэтому `issue()` и `return_equipment()` являются явными серверными командами.

Это архитектурный выбор VEQTA для конкретного требования, а не утверждение, что Frappe всегда требует отдельный controller method для любого перехода состояния.

## Защита от прямого изменения status

После появления Movement состояние Rental становится частью транзакционного контракта.

Если пользователь просто сохранит:

```text
status = Active
```

без Issue Movement, приложение окажется в противоречивом состоянии.

Поэтому поле `status` становится read-only в обычной Form, а Controller дополнительно защищает переход на сервере.

Смысл проверки:

```text
новый Rental со status = Planned
→ допустим

Planned → Active
→ только внутри issue()

Active → Returned
→ только внутри return_equipment()

прочие прямые переходы
→ ошибка
```

UI здесь только помогает пользователю. Реальная защита остаётся серверной.

Для внутренней команды можно использовать transient flag Document, например:

```python
self.flags.rental_operation = "issue"
```

и проверять его в `validate()` при изменении `status`.

Флаг не является новым persisted state. Он только связывает текущий вызов команды с разрешённым переходом внутри одного выполнения.

## Операция Issue

Условия:

```text
Rental.status = Planned
текущий пользователь имеет write на Rental
Rental содержит Equipment
```

Команда выполняет:

```text
1. проверить write permission
2. проверить текущее состояние
3. status = Active
4. сохранить Rental через Document API
5. для каждого Rental Item создать Equipment Movement / Issue
6. вернуть успешный результат
```

Ключевой момент:

```text
frappe.db.commit()
```

внутри операции не вызывается.

В обычном успешном `POST` Frappe фиксирует записи в конце request. При необработанном исключении request откатывается.

Первичные источники:

- https://docs.frappe.io/framework/user/en/api/database
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/app.py

## Атомарный контракт Issue

После успешной команды должно выполняться:

```text
Rental.status = Active
```

и число Issue Movement для Rental должно совпадать с числом Equipment в Rental.

Если создание хотя бы одного Movement завершается ошибкой:

```text
Rental.status остаётся Planned
Issue Movement не остаются в БД
```

Не допускается состояние:

```text
Rental = Active
Movement создан только для части Equipment
```

## Почему исключение должно выйти наружу

Frappe может автоматически сделать rollback только когда request завершился ошибкой.

Если код делает:

```python
try:
    ...
except Exception:
    frappe.log_error()
    return {"ok": False}
```

то для request исключение уже обработано.

Framework не может догадаться, что промежуточные DB writes нужно отменить.

Официальная Database API прямо отмечает, что при самостоятельно пойманном исключении ответственность за корректный rollback переходит к коду приложения.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#database-transaction-model

## Операция Return

Условия:

```text
Rental.status = Active
текущий пользователь имеет write на Rental
```

Команда выполняет:

```text
1. проверить write permission
2. проверить состояние Active
3. status = Returned
4. сохранить Rental через Document API
5. создать Return Movement для каждого Equipment
```

Транзакционный контракт тот же:

```text
всё сохранено
или
ничего не сохранено
```

Повторный вызов `issue()` после успешной выдачи отклоняется текущим состоянием `Active`.

Повторный вызов `return_equipment()` после успешного возврата отклоняется состоянием `Returned`.

Для текущей модели отдельная система deduplication не нужна.

## Document API и прямой Database API

В практикуме отдельно сравниваются два пути.

Обычный бизнес-путь:

```python
rental.status = "Active"
rental.save()
```

проходит `Document` lifecycle, permissions и validations.

Прямое изменение:

```python
frappe.db.set_value("Rental", rental.name, "status", "Active")
```

не вызывает обычные ORM triggers, включая `validate` и `on_update`.

Поэтому `set_value` способен технически создать состояние, которое серверный контракт Rental запрещает.

Это не означает, что `set_value` «плохой API». Он имеет другую ответственность и подходит для технических изменений, когда обход lifecycle является намеренным.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#frappedbset_value

## Что принадлежит App

К концу практикума `rental_training` воспроизводимо содержит:

- Standard DocType `Equipment Movement`;
- его permissions;
- изменение metadata `Rental.status` для обычной Form;
- серверную защиту переходов состояния;
- controller methods `issue()` и `return_equipment()`;
- Form buttons, которые вызывают серверные методы;
- автоматические тесты собственных контрактов.

## Что остаётся Site-owned

На Site остаются:

- Users;
- Equipment;
- Customer;
- Rental;
- Rental Item;
- Equipment Movement, созданные во время реальной работы;
- контрольные записи для экспериментов.

Movement — рабочие данные, а не fixture приложения.

## Что сознательно не решается

Текущая операция не требует:

```text
Background Job
Scheduler
Webhook
after_commit callback
внешнюю систему
retry
очередь доставки
```

Все её записи находятся в одной локальной БД Frappe и выполняются быстро в одном request.

Следующий класс задач появится, когда после успешного commit потребуется внешний или долгий эффект. Тогда транзакция БД уже не сможет сама обеспечить согласованность двух систем.