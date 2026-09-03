# S09. Проверить, что транзакционная модель принадлежит App

К S09 бизнес-операции работают и покрыты автоматическими тестами.

Теперь нужно убедиться, что обязательное состояние не осталось скрытой настройкой исходного Site.

---

## 1. Что появилось в App

За практикум добавлены или изменены:

```text
Equipment Movement Standard DocType
Rental.status metadata
Rental Controller
Rental Form Script
Rental tests
```

Это обязательные части поведения `rental_training`.

Они должны восстанавливаться из исходников App.

---

## 2. Что не принадлежит App

Рабочие записи остаются данными Site:

```text
Users
Customer
Equipment
Rental
Rental Item
Equipment Movement
```

Даже несмотря на то, что Movement создаётся только системной командой, конкретные Movement являются рабочими бизнес-данными.

Их нельзя экспортировать как fixtures только потому, что они были нужны для демонстрации.

---

## 3. Проверить Equipment Movement metadata

```bash
cd ~/frappe/rental-training-bench

sed -n '1,340p' \
  apps/rental_training/rental_training/rental_training/doctype/equipment_movement/equipment_movement.json
```

Проверьте:

```text
Standard DocType
Module = Rental Training
fields = equipment / rental / movement_type / movement_at
Rental Manager → Read
нет прикладного Create/Write/Delete
```

---

## 4. Проверить изменение Rental metadata

```bash
sed -n '1,340p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.json
```

Найдите поле `status`.

Ожидается:

```text
fieldname = status
read_only = 1
```

Это UI-состояние должно поставляться с Standard DocType metadata.

Серверная validation при этом находится не в JSON, а в Controller.

---

## 5. Проверить Controller

```bash
sed -n '1,420p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.py
```

Итоговый Controller должен содержать:

```text
старые data invariants
validate_status_transition()
create_equipment_movements()
issue()
return_equipment()
```

И не должен содержать учебных антипримеров:

```text
Rollback experiment
Manual commit experiment
Caught exception experiment
```

Проверьте также отсутствие ручного commit в бизнес-командах:

```bash
grep -n 'frappe\.db\.commit' \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.py \
  || true
```

Для итогового Controller ожидается отсутствие совпадений.

---

## 6. Проверить Form Script

```bash
sed -n '1,260p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.js
```

Ожидается тонкий UI:

```text
Planned → кнопка Issue → frm.call("issue")
Active → кнопка Return → frm.call("return_equipment")
```

В JS не должно быть:

```text
прямого изменения status как бизнес-команды
создания Equipment Movement
permission bypass
commit / rollback logic
```

---

## 7. Проверить tests

```bash
sed -n '1,520p' \
  apps/rental_training/rental_training/rental_training/doctype/rental/test_rental.py
```

Проверьте наличие transaction-контрактов из S08 и сохранение предыдущих data/reporting tests.

Отдельного нового testing framework не требуется.

---

## 8. Проверить, что Movement не стал fixture

Откройте hooks приложения:

```bash
sed -n '1,320p' \
  apps/rental_training/rental_training/hooks.py
```

Не должно появиться fixture вроде:

```python
{"dt": "Equipment Movement"}
```

Рабочие движения не являются обязательной конфигурацией App.

Если предыдущие практикумы уже используют fixtures для другого обязательного состояния, не удаляйте их. Проверяем только отсутствие экспорта рабочих Movement.

---

## 9. Выполнить migrate исходного Site

```bash
bench --site rental.localhost migrate
```

После migrate проверьте:

```bash
bench --site rental.localhost console
```

```python
print(bool(frappe.db.exists("DocType", "Equipment Movement")))

status_field = frappe.get_meta("Rental").get_field("status")
print("status.read_only =", status_field.read_only)

movement_meta = frappe.get_meta("Equipment Movement")
for permission in movement_meta.permissions:
    print(permission.role, permission.read, permission.create, permission.write, permission.delete)
```

Ожидается:

```text
Equipment Movement exists
status.read_only = 1
Rental Manager read = 1
```

---

## 10. Проверить Git App целиком

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status --short
```

Должно быть чисто.

Посмотрите историю последних изменений:

```bash
git log --oneline -8
```

К этому моменту в истории должны быть зафиксированы как минимум смысловые изменения:

```text
Equipment Movement
Issue operation
Return operation
transaction tests
```

Экспериментальные ошибки S03–S05 в историю App не попадали.

---

## 11. Почему отдельный fixture для permissions не нужен

Permissions `Equipment Movement` находятся в metadata Standard DocType.

Изменённая metadata Rental также находится в `rental.json`.

Поэтому для этих настроек сначала используется штатная поставка Standard DocType metadata.

Не создавайте `Custom DocPerm` fixture поверх уже принадлежащего App Standard DocType без отдельной причины.

---

## 12. Что будет проверять чистый Site

На S10 новый Site должен получить из App:

```text
Equipment Movement DocType
его permissions
Rental.status read_only
Rental Controller
Rental Form Script
automated tests source
```

Но не должен получить:

```text
контрольного Customer
Transaction Equipment 01...09
контрольные Rentals
их Equipment Movement
учебных Users
```

Это и есть граница App-owned / Site-owned для текущего маршрута.

---

## 13. Контрольная точка S09

Готово, если:

```text
все обязательные изменения находятся в исходниках rental_training
рабочие Movement не экспортируются
экспериментальный код отсутствует
migrate проходит
Git App чист
```

Следующий этап: [`S10_CLEAN_INSTALL.md`](S10_CLEAN_INSTALL.md).