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

`Equipment Movement` представляет самостоятельный факт:

- конкретное Equipment было выдано или возвращено;
- событие относится к конкретному Rental;
- у события есть собственное время;
- история нужна со стороны Equipment, а не только внутри одной формы Rental.

Поэтому Movement не становится полем Rental или Child DocType только потому, что одна операция создаёт несколько записей.

## Кто создаёт Movement

`Equipment Movement` — system-generated журнал.

Прикладные permissions:

```text
Rental Manager
→ Read

Rental Operator
→ без прямого доступа
```

`Create`, `Write` и `Delete` прикладным ролям не выдаются.

Movement создаётся внутри уже авторизованной команды Rental:

```text
пользователь имеет write на конкретный Rental
        ↓
серверная команда проверяет право
        ↓
команда внутренне создаёт Movement
```

Для внутренней вставки используется:

```python
doc.insert(ignore_permissions=True)
```

`ignore_permissions=True` здесь не исправляет ошибку модели прав. Авторизация уже выполнена на границе команды через:

```python
self.check_permission("write")
```

Без этой предварительной проверки внутренний bypass был бы неправильной границей безопасности.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/document

## Явные команды Rental

До этого `status` был обычным предметным полем:

```text
Planned
Active
Returned
```

После появления журнала переходы получают дополнительный смысл:

```text
Planned → Active
= Issue Rental

Active → Returned
= Return Rental
```

Поэтому Controller получает две явные команды:

```python
@frappe.whitelist()
def issue(self):
    ...

@frappe.whitelist()
def return_equipment(self):
    ...
```

Form вызывает их через `frm.call()`.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/form#frmcall

## Почему не on_update

Можно было бы создавать Movement в `on_update`, проверяя изменение `status`.

Для текущего требования яснее различить:

```text
обычное редактирование Rental
≠
Issue Rental
≠
Return Rental
```

Поэтому операция остаётся явным controller method.

Это архитектурный выбор VEQTA для конкретной задачи, а не универсальное правило Frappe.

## Серверный контракт status

После появления Movement состояние Rental больше нельзя менять независимо от операции.

Итоговый контракт:

```text
новый Rental
→ только Planned

Planned → Active
→ только внутри issue()

Active → Returned
→ только внутри return_equipment()

прочие прямые переходы
→ ошибка
```

Правило `new Rental → Planned` важно отдельно. Иначе новый Document можно было бы вставить сразу как `Active` и получить состояние без Issue Movement.

Поле `status` становится read-only в обычной Form, но UI не является единственной защитой. Controller проверяет начальное состояние и переходы на сервере.

Для связи разрешённого перехода с текущим вызовом команды используется transient flag, например:

```python
self.flags.rental_operation = "issue"
```

Флаг не хранится в БД и не становится дополнительным состоянием модели.

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
2. перечитать persisted Rental
3. проверить status = Planned
4. разрешить внутренний переход Planned → Active
5. сохранить Rental через Document API
6. создать Issue Movement для каждого Rental Item
7. вернуть успешный результат
```

Внутри операции нет:

```python
frappe.db.commit()
```

В обычном успешном POST Frappe фиксирует DB writes в конце request. При необработанном исключении request откатывается.

Первичные источники:

- https://docs.frappe.io/framework/user/en/api/database#database-transaction-model
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/app.py

### Атомарный контракт Issue

После успеха:

```text
Rental.status = Active
Issue Movement = по одному на каждый Equipment
```

Если создание хотя бы одного Movement завершается ошибкой:

```text
Rental.status остаётся Planned
Issue Movement не остаются в БД
```

Не допускается:

```text
Rental = Active
Movement создан только для части Equipment
```

## Почему исключение должно выйти наружу

Если код делает:

```python
try:
    ...
except Exception:
    frappe.log_error()
    return {"ok": False}
```

то request больше не содержит необработанного исключения.

Framework не может автоматически определить, что промежуточные DB writes нужно отменить. В таком случае решение о rollback становится ответственностью приложения.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#database-transaction-model

Для текущего Issue такого требования нет, поэтому ошибка, отменяющая всю операцию, должна выйти наружу.

## Операция Return

Условия:

```text
Rental.status = Active
текущий пользователь имеет write на Rental
```

Команда выполняет:

```text
1. проверить write permission
2. перечитать persisted Rental
3. проверить status = Active
4. разрешить Active → Returned
5. сохранить Rental через Document API
6. создать Return Movement для каждого Equipment
```

Транзакционный контракт тот же:

```text
всё сохранено
или
ничего не сохранено
```

Повторный `issue()` после успешной выдачи отклоняется состоянием `Active`.

Повторный `return_equipment()` после возврата отклоняется состоянием `Returned`.

Отдельная deduplication infrastructure текущей локальной операции не нужна.

## Document API и прямой Database API

Обычный бизнес-путь:

```python
rental.status = "Active"
rental.save()
```

проходит `Document` lifecycle и validations.

Прямое изменение:

```python
frappe.db.set_value("Rental", rental.name, "status", "Active")
```

не вызывает обычные ORM triggers вроде `validate` и `on_update`.

Поэтому `set_value` способен технически создать состояние, которое Controller Rental запрещает.

Это не делает `set_value` плохим API. У него другая ответственность: техническое изменение БД, когда обход Document lifecycle является намеренным.

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database#frappedbset_value

## Что принадлежит App

К концу практикума `rental_training` воспроизводимо содержит:

- Standard DocType `Equipment Movement`;
- его permissions;
- metadata `Rental.status`;
- серверное правило `new Rental → Planned`;
- защиту переходов состояния;
- controller methods `issue()` и `return_equipment()`;
- Form buttons для вызова серверных методов;
- автоматические тесты собственных контрактов.

## Что остаётся Site-owned

На конкретном Site остаются:

- Users;
- Equipment;
- Customer;
- Rental;
- Rental Item;
- Equipment Movement как рабочие записи;
- контрольные записи экспериментов.

Movement не является fixture приложения.

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

Все изменения находятся в одной локальной БД Frappe и выполняются быстро внутри одного request.

Следующий класс задач появится, когда после успешного локального commit потребуется долгая или внешняя работа.