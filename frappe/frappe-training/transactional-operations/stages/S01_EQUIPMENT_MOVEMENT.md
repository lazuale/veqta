# S01. Добавить Equipment Movement как самостоятельный журнал

S00 подготовил Rental, которые можно использовать для транзакционных экспериментов.

Теперь появляется новая предметная ответственность:

> После фактической выдачи или возврата нужно хранить отдельный факт движения каждого Equipment.

Для этого создаётся новый Standard DocType `Equipment Movement`.

---

## 1. Почему Movement — отдельный DocType

Одна строка движения отвечает на самостоятельный вопрос:

```text
какое Equipment
по какому Rental
какое действие произошло
когда оно произошло
```

Этот факт нужен независимо от конкретной формы Rental и позже может использоваться как история Equipment.

Поэтому:

```text
Equipment Movement
→ самостоятельный Standard DocType
```

а не:

```text
поле в Rental
Child Table только ради хранения нескольких строк
текстовый log
JSON в одном поле
```

---

## 2. Кто имеет право работать с журналом

Movement должен создаваться системой внутри уже авторизованной бизнес-операции.

Прикладной пользователь не должен вручную создавать или переписывать записи журнала.

Модель permissions:

```text
Rental Manager
→ Read = yes

Rental Operator
→ прямых permissions нет
```

Ни одна прикладная роль не получает:

```text
Create
Write
Delete
```

На следующем этапе команда Rental будет внутренне создавать Movement после проверки права на сам Rental.

---

## 3. Создать Equipment Movement

Запустите dev server, если он ещё не работает:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте Desk:

```text
http://rental.localhost:8000/app
```

Через поиск откройте:

```text
DocType
```

Создайте:

```text
Name   : Equipment Movement
Module : Rental Training
```

Проверьте:

```text
Custom?        : OFF
Is Child Table : OFF
Is Single      : OFF
Is Submittable : OFF
```

Почему `Is Submittable = OFF`:

Movement уже представляет зафиксированный факт, который создаётся программно внутри команды Rental. В текущем требовании нет отдельного пользовательского lifecycle Draft → Submit → Cancel для самого Movement.

Это не универсальное правило для всех журналов.

---

## 4. Добавить поля

### Equipment

```text
Label        : Equipment
Fieldname    : equipment
Type         : Link
Options      : Equipment
Mandatory    : yes
In List View : yes
```

### Rental

```text
Label        : Rental
Fieldname    : rental
Type         : Link
Options      : Rental
Mandatory    : yes
In List View : yes
```

### Movement Type

```text
Label        : Movement Type
Fieldname    : movement_type
Type         : Select
Options      :
Issue
Return
Mandatory    : yes
In List View : yes
```

### Movement At

```text
Label        : Movement At
Fieldname    : movement_at
Type         : Datetime
Mandatory    : yes
In List View : yes
```

Не добавляйте сейчас:

```text
status
retry_count
external_id
job_id
queue_name
processed
error
```

Для них нет требований текущей локальной операции.

---

## 5. Настроить naming

Используйте штатный Expression:

```text
MOVE-.#####
```

Movement имеет собственный стабильный идентификатор:

```text
MOVE-00001
MOVE-00002
...
```

Не используйте комбинацию `rental + equipment + type` как `name`: эти значения являются бизнес-данными, а не обязанностью системного идентификатора.

---

## 6. Настроить permissions

В Permissions добавьте только:

```text
Role           : Rental Manager
Read           : yes
Create         : no
Write          : no
Delete         : no
```

Не добавляйте `Rental Operator`.

Сохраните DocType.

---

## 7. Проверить metadata в App

В терминале:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Должен появиться новый каталог:

```text
rental_training/rental_training/doctype/equipment_movement/
```

Проверьте:

```bash
find \
  apps/rental_training/rental_training/rental_training/doctype/equipment_movement \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Откройте JSON:

```bash
sed -n '1,320p' \
  apps/rental_training/rental_training/rental_training/doctype/equipment_movement/equipment_movement.json
```

Найдите смысловые признаки:

```text
module = Rental Training
custom = 0
istable = 0
is_submittable = 0

equipment → Link → Equipment
rental → Link → Rental
movement_type → Select
movement_at → Datetime

Rental Manager → read = 1
create/write/delete = 0
```

---

## 8. Проверить permissions на Site

Откройте console:

```bash
bench --site rental.localhost console
```

Выполните:

```python
meta = frappe.get_meta("Equipment Movement")

for permission in meta.permissions:
    print(
        permission.role,
        "read=", permission.read,
        "create=", permission.create,
        "write=", permission.write,
        "delete=", permission.delete,
    )
```

Ожидается только manager read.

Проверьте прикладные роли:

```python
for role in ["Rental Operator", "Rental Manager"]:
    print(
        role,
        "read=", frappe.has_permission("Equipment Movement", "read", user=(
            "manager@example.test" if role == "Rental Manager" else "operator-a@example.test"
        )),
        "create=", frappe.has_permission("Equipment Movement", "create", user=(
            "manager@example.test" if role == "Rental Manager" else "operator-a@example.test"
        )),
    )
```

Смысл результата:

```text
operator → read false / create false
manager  → read true / create false
```

Завершите console.

---

## 9. Почему пока не создаём Movement вручную

Если открыть обычную Form под менеджером, журнал должен быть доступен для чтения, но не для ручного формирования.

Это важная граница:

```text
Equipment Movement
→ не пользовательская команда
→ результат другой бизнес-операции
```

На S02 серверная команда `Rental.issue()` сначала проверит право пользователя на Rental, а затем внутренне создаст Movement.

---

## 10. Зафиксировать DocType в Git

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git add \
  rental_training/rental_training/doctype/equipment_movement

git diff --cached -- \
  rental_training/rental_training/doctype/equipment_movement
```

Если metadata соответствует этапу:

```bash
git commit -m "feat: add equipment movement journal"
```

Проверьте:

```bash
git status --short
```

Рабочее дерево должно быть чистым.

---

## 11. Контрольная точка S01

Готово, если:

```text
Equipment Movement существует как Standard DocType
Movement принадлежит rental_training
Rental Manager имеет только Read
Rental Operator не имеет прямого доступа
прикладные роли не имеют Create/Write/Delete
рабочих Movement пока нет
Git App чист
```

Следующий этап: [`S02_ISSUE_COMMAND.md`](S02_ISSUE_COMMAND.md).