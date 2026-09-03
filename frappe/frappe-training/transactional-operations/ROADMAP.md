# Маршрут практикума

Практикум продолжает `rental_training` и показывает, где проходит граница одной бизнес-операции.

```text
готовый rental_training
  ↓
Equipment Movement
  ↓
явная команда issue()
  ↓
Rental + несколько Movement
  ↓
необработанная ошибка
  ↓
rollback
  ↓
ручной commit как антипример
  ↓
пойманное исключение как антипример
  ↓
return_equipment()
  ↓
Document API vs set_value
  ↓
автоматические тесты
  ↓
поставка App
  ↓
чистая установка
```

## Этапы

### S00 — исходное состояние и контрольные Rentals

Начать с актуального `rental_training` после предыдущих практикумов.

Проверить:

```text
Frappe v16.33.0
rental_training установлен
Equipment / Customer / Rental / Rental Item существуют
Rental Controller содержит предыдущие validations
текущие permissions воспроизводятся из App
```

Создать отдельные Site-owned Rentals для экспериментов S02–S07. Они не становятся fixtures и не используются автоматическими тестами.

### S01 — добавить Equipment Movement

Создать Standard DocType:

```text
Equipment Movement
├── equipment     → Link → Equipment
├── rental        → Link → Rental
├── movement_type → Select: Issue / Return
└── movement_at   → Datetime
```

`Equipment Movement` — самостоятельный журнал.

Permissions:

```text
Rental Manager  → Read
Rental Operator → без прямого доступа
```

Прикладные роли не получают `Create`, `Write` и `Delete`.

### S02 — собрать атомарную команду Issue

Требование:

> Выдать Rental и зарегистрировать Issue Movement для каждого Equipment одной бизнес-операцией.

На `Rental` появляется whitelisted controller method:

```python
issue()
```

С этого же этапа серверный контракт становится таким:

```text
новый Rental → только Planned
Planned → Active → только issue()
```

Команда:

```text
проверяет write permission текущего пользователя
перечитывает persisted Rental
проверяет status = Planned
разрешает внутренний переход Planned → Active
сохраняет Rental через Document API
создаёт Issue Movement для каждого Rental Item
не вызывает frappe.db.commit()
```

Movement создаётся внутренне через `insert(ignore_permissions=True)` только после `self.check_permission("write")` на Rental.

`status` становится read-only в обычной Form, а Controller защищает и начальное состояние, и прямой переход на сервере.

В `rental.js` появляется тонкая кнопка **Issue**, вызывающая:

```javascript
frm.call("issue")
```

### S03 — увидеть автоматический rollback

После создания первого Issue Movement временно добавить контролируемое исключение.

Ожидаемый результат неуспешного request:

```text
Rental.status = Planned
Issue Movement = 0
```

Ученик видит, что уже выполненные `save()` / `insert()` не означают отдельный commit.

В конце этапа временная ошибка удаляется.

### S04 — сломать атомарность ручным commit

На отдельном контрольном Rental временно добавить:

```python
frappe.db.commit()
```

после части записей, а затем вызвать исключение.

Теперь rollback request уже не отменяет ранее зафиксированную часть.

Наблюдаемое состояние:

```text
Rental = Active
Issue Movement = 1 из N
```

После эксперимента ручной commit и временная ошибка удаляются, а повреждённые Site-owned данные восстанавливаются.

### S05 — увидеть границу пойманного исключения

Временно превратить внутреннее исключение в обычный return:

```python
try:
    ...
except Exception:
    frappe.log_error()
    return {"ok": False}
```

Request завершается без необработанного исключения, поэтому Framework не может автоматически понять, что бизнес-операцию нужно отменить.

После наблюдения код возвращается к правильной форме: ошибка, отменяющая всю операцию, выходит наружу.

### S06 — добавить атомарную команду Return

Добавляется:

```python
return_equipment()
```

Итоговый серверный контракт status:

```text
новый Rental → только Planned
Planned → Active → только issue()
Active → Returned → только return_equipment()
```

Return снова использует Document API, создаёт Movement и не делает ручной commit.

В `rental.js` появляется кнопка **Return** только для `Active`.

### S07 — сравнить Document API и прямое изменение БД

Обычный:

```python
rental.status = "Active"
rental.save()
```

проходит Controller и отклоняет прямой переход.

Технический:

```python
frappe.db.set_value(
    "Rental",
    rental.name,
    "status",
    "Active",
)
```

не запускает обычные ORM triggers и способен создать `Active` без Movement.

После эксперимента контрольная запись восстанавливается.

### S08 — закрепить собственные контракты тестами

Integration tests защищают:

- новый Rental не создаётся сразу как `Active`/`Returned`;
- прямой `Planned → Active` через `save()` запрещён;
- прямой `Active → Returned` через `save()` запрещён;
- `issue()` соблюдает `write` permission Rental;
- чужой оператор не может issue Rental после `If Owner`;
- успешный Issue создаёт один Issue Movement на каждый Equipment;
- успешный Return создаёт полный набор Return Movement;
- повторные команды отклоняются;
- прикладные роли не имеют прямого `Create` на Movement;
- `Rental Manager` имеет `Read` на журнал.

Старые test helpers, которые создавали `Active`/`Returned` напрямую, переводятся на реальные `issue()` / `return_equipment()`.

Штатный rollback POST request отдельно не тестируется как собственный механизм App: его S03 проверяет на живом Site.

### S09 — проверить границу App-owned / Site-owned

App-owned:

```text
Equipment Movement metadata
его permissions
Rental.status metadata
Rental Controller
Rental Form Script
автоматические тесты
```

Site-owned:

```text
Users
Equipment
Customer
Rental
Rental Item
Equipment Movement как рабочие записи
контрольные данные экспериментов
```

Movement не экспортируются как fixtures.

### S10 — проверить чистую установку

Установить итоговый `rental_training` на новый Site той же совместимой версии Frappe.

Из App должны восстановиться:

```text
Equipment Movement
его default permissions
Rental с защищённым status
controller methods issue / return_equipment
Form Script
tests source
```

Рабочие Rental и Movement автоматически не появляются.

После создания минимальных данных выполняется успешный Issue и Return.

## Почему порядок именно такой

Сначала появляется бизнес-факт `Equipment Movement`, затем команда, которая обязана его создавать.

Успешная Issue-команда строится до транзакционных экспериментов.

Rollback проверяется до ручного commit: сначала ученик видит штатное поведение Framework, затем намеренно его ломает.

Пойманное исключение вынесено отдельно, потому что нарушает автоматический rollback по другой причине, чем `commit()`.

Return добавляется после понимания базовой транзакционной границы.

`frappe.db.set_value` появляется только после того, как уже понятно, какой lifecycle он способен обойти.

Background jobs не входят в маршрут, потому что локальная выдача и возврат не требуют асинхронности.

Модель: [`APPLICATION_MODEL.md`](APPLICATION_MODEL.md). Требования: [`REQUIREMENTS.md`](REQUIREMENTS.md).