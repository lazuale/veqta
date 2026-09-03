# S01. Ограничить Rental Operator своими Documents

На S00 два оператора создали Rentals под собственными учётными записями. Пока модель permissions остаётся такой же, как в первом практикуме: оба `Rental Operator` имеют `Read/Create/Write` на весь DocType `Rental`.

Появляется новое требование:

> Оператор должен работать только с Rental, которые создал сам. Менеджер должен по-прежнему видеть все Rentals.

Это требование уже выражается штатным `If Owner` в DocType Permissions. Собственный permission hook или ACL-таблица здесь не нужны.

Связанные материалы:

- [`S00_BASELINE_AND_DATA.md`](S00_BASELINE_AND_DATA.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../../../frappe-architecture-standard/04_SECURITY.md`](../../../frappe-architecture-standard/04_SECURITY.md).

---

## 1. Сначала зафиксировать требуемую матрицу

После этапа должна получиться такая модель для `Rental`:

| Role | Read | Create | Write | Delete | If Owner |
|---|---:|---:|---:|---:|---:|
| Rental Operator | yes | yes | yes | no | yes |
| Rental Manager | yes | yes | yes | yes | no |

`If Owner` здесь относится только к строке `Rental Operator`.

Смысл:

```text
operator-a
→ работает с A1/A2/A3
→ не получает доступ к B1/B2/B3

operator-b
→ работает с B1/B2/B3
→ не получает доступ к A1/A2/A3

manager
→ видит все шесть Rentals
```

`owner` используется потому, что требование буквально говорит о создателе Document. Если бы бизнес-понятие было «ответственный сотрудник», это уже могло бы потребовать отдельного Link-поля и другой модели доступа.

---

## 2. Проверить исходное поведение

До изменения войдите под:

```text
operator-a@example.test
```

Откройте List `Rental`.

На исходном состоянии первого практикума оператор может увидеть Rentals другого оператора. Это и есть наблюдаемая проблема, которую мы исправляем.

Повторите под:

```text
operator-b@example.test
```

После проверки вернитесь под `Administrator`.

---

## 3. Изменить Standard DocType Permissions

Откройте через Desk:

```text
DocType → Rental
```

Найдите таблицу `Permissions`.

Для строки:

```text
Role: Rental Operator
```

оставьте текущие:

```text
Read   : yes
Create : yes
Write  : yes
Delete : no
```

и включите:

```text
If Owner : yes
```

Строку `Rental Manager` не ограничивайте владельцем.

Сохраните Standard DocType `Rental`.

---

## 4. Проверить изменение в исходниках App

Перейдите в App:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
```

Проверьте Git:

```bash
git status --short
```

Ожидается изменение metadata `Rental`, например:

```text
rental_training/rental_training/doctype/rental/rental.json
```

Посмотрите diff:

```bash
git diff -- rental_training/rental_training/doctype/rental/rental.json
```

В permission row `Rental Operator` должно появиться значение `if_owner`.

Точный порядок JSON-ключей не является контрактом. Важно, что обязательная модель permissions находится в Standard DocType metadata и поэтому принадлежит App.

---

## 5. Проверить List View под двумя операторами

Войдите под:

```text
operator-a@example.test
```

Откройте List `Rental`.

Ожидается, что доступны A1/A2/A3 и не доступны B1/B2/B3.

Затем войдите под:

```text
operator-b@example.test
```

Ожидается обратная картина.

Наконец войдите под:

```text
manager@example.test
```

Менеджер должен видеть все контрольные Rentals.

---

## 6. Проверить прямое открытие чужого Document

Одного списка недостаточно для доказательства безопасности.

Под `operator-a@example.test` попробуйте открыть URL или перейти по известному `name` одного Rental, принадлежащего `operator-b@example.test`.

Ожидается отказ в доступе.

Это важная проверка:

```text
не видно в List
+
нельзя открыть напрямую
```

Обе части должны соответствовать одной политике доступа.

---

## 7. Проверить права через Bench console

Откройте console:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Установите пользователя:

```python
frappe.set_user("operator-a@example.test")
```

Получите разрешённый список:

```python
frappe.get_list(
    "Rental",
    fields=["name", "owner"],
    order_by="creation asc",
)
```

В результате не должно быть Rentals `operator-b@example.test`.

Проверьте permission конкретного чужого Rental, подставив его реальный `name`:

```python
frappe.has_permission("Rental", "read", doc="RENT-.....")
```

Ожидается:

```text
False
```

Верните пользователя:

```python
frappe.set_user("Administrator")
```

и закройте console:

```python
exit()
```

На этом этапе `get_list` используется только как дополнительная проверка результата. Разницу между `get_list`, `get_all` и `get_doc` мы разберём отдельно на S04.

---

## 8. Зафиксировать изменение App

Проверьте diff ещё раз:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
git diff
```

Если изменение соответствует требованию, зафиксируйте его в Git вашего учебного App обычным коммитом.

Например:

```bash
git add rental_training/rental_training/doctype/rental/rental.json
git commit -m "feat: restrict rental operator to owned rentals"
```

---

## Результат этапа

К концу S01 доказано:

```text
If Owner выражает текущее требование без собственного ACL
Rental Operator видит только свои Rental
прямое чтение чужого Rental запрещено
Rental Manager по-прежнему видит все Rental
обязательная permission-модель находится в App metadata
```

На S02 никакой новый серверный код не понадобится: следующая задача — обычный рабочий реестр, и сначала нужно проверить стандартный `List View`.
