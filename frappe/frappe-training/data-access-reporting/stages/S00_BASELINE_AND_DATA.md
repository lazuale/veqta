# S00. Подготовить исходное состояние и контрольные данные

Этот практикум не создаёт новый App. Он продолжает `rental_training`, поэтому сначала нужно доказать, что исходная модель первого маршрута действительно готова, а затем подготовить данные, на которых следующие этапы можно проверить фактически.

Новое требование этого этапа:

> Для проверки permissions, отчётов и запросов нужны Rentals нескольких пользователей с заранее понятными датами, статусами и Equipment.

Контрольные Users и Documents остаются данными учебного Site. Они не становятся fixtures и не коммитятся в App.

Связанные документы:

- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../REQUIREMENTS.md`](../REQUIREMENTS.md);
- [`../ROADMAP.md`](../ROADMAP.md);
- [`../../first-app/README.md`](../../first-app/README.md).

---

## 1. Проверить готовый App и Site

Перейдите в Bench первого практикума:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте установленные Apps:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается как минимум:

```text
frappe
rental_training
```

Проверьте рабочее дерево App:

```bash
git -C apps/rental_training status --short
```

Перед началом нового маршрута оно должно быть чистым.

Если остались незакоммиченные изменения первого практикума, сначала разберите их. Третий маршрут не должен начинаться поверх неизвестного локального состояния.

---

## 2. Проверить исходную модель

В Desk должны существовать:

```text
Equipment
Customer
Rental
Rental Item
```

У `Rental` должны быть поля:

```text
customer
start_date
end_date
status
items
```

и состояния:

```text
Planned
Active
Returned
```

Роли первого практикума:

```text
Rental Operator
Rental Manager
```

На S00 мы ещё **не меняем permissions**. Это произойдёт на S01 после отдельного требования.

---

## 3. Создать трёх учебных пользователей

Через Desk → `User` создайте три System User:

```text
operator-a@example.test
operator-b@example.test
manager@example.test
```

Назначьте роли:

```text
operator-a@example.test → Rental Operator
operator-b@example.test → Rental Operator
manager@example.test    → Rental Manager
```

Пароли задайте локально для учебного Site.

Не добавляйте реальные пароли:

```text
в документацию
в Git
в fixtures
в исходный код App
```

Эти Users существуют только для прохождения практикума.

---

## 4. Подготовить минимум три Equipment и два Customer

Можно использовать Documents, созданные в первом практикуме.

Нужно минимум:

```text
Equipment A
Equipment B
Equipment C

Customer 1
Customer 2
```

Если данных не хватает, создайте недостающие записи через стандартные формы.

Важно не конкретное название, а то, чтобы в дальнейшем вы однозначно понимали, какой Equipment соответствует A, B и C.

Для примеров удобно использовать:

```text
Equipment A → Bosch GBH 2-26
Equipment B → Canon EOS R50
Equipment C → Leica Lino L2
```

Имена `EQ-.....` могут отличаться в зависимости от уже созданных записей. Контрактом являются сами Documents, а не конкретный номер sequence.

---

## 5. Создать контрольные Rentals

Дальнейшие примеры используют отчётный период:

```text
2026-09-01 → 2026-09-10
```

Создайте шесть Rentals по следующей схеме.

| Кто создаёт | Rental | Период | Status | Equipment |
|---|---|---|---|---|
| operator-a | A1 | 2026-09-01 → 2026-09-03 | Active | Equipment A |
| operator-a | A2 | 2026-08-30 → 2026-09-02 | Returned | Equipment B |
| operator-a | A3 | 2026-09-04 → 2026-09-06 | Planned | Equipment C |
| operator-b | B1 | 2026-09-03 → 2026-09-05 | Returned | Equipment A |
| operator-b | B2 | 2026-09-06 → 2026-09-08 | Active | Equipment B |
| operator-b | B3 | 2026-09-10 → 2026-09-12 | Returned | Equipment C |

Customer можно чередовать между двумя подготовленными Customers.

### Почему создавать нужно именно под соответствующим пользователем

Поле `owner` — системный владелец Document.

На следующем этапе правило будет буквально таким:

```text
Rental Operator
→ работает только с Rental, где owner = текущий User
```

Поэтому нельзя создать все шесть Rentals под `Administrator`, а затем считать их данными двух операторов.

Войдите под `operator-a@example.test` и создайте A1–A3 обычной Form `Rental`.

Затем войдите под `operator-b@example.test` и создайте B1–B3.

Не меняйте `owner` напрямую через SQL или служебными обходами.

---

## 6. Почему набор данных выглядит именно так

Он нужен не для реалистичной симуляции бизнеса, а для однозначных проверок последующих требований.

### Equipment A

```text
A1 Active   : 2026-09-01 → 2026-09-03
B1 Returned : 2026-09-03 → 2026-09-05
```

В выбранном периоде занятые календарные дни:

```text
01, 02, 03, 04, 05 сентября
```

День `03` встречается в двух интервалах, но должен считаться один раз.

Ожидается:

```text
occupied_days = 5
```

### Equipment B

```text
A2 Returned : 2026-08-30 → 2026-09-02
B2 Active   : 2026-09-06 → 2026-09-08
```

Первый интервал выходит за левую границу отчёта и должен быть обрезан до:

```text
2026-09-01 → 2026-09-02
```

Итого:

```text
occupied_days = 2 + 3 = 5
```

### Equipment C

```text
A3 Planned  : 2026-09-04 → 2026-09-06
B3 Returned : 2026-09-10 → 2026-09-12
```

`Planned` не участвует в учебном показателе загрузки.

B3 пересекает правую границу отчёта только одним днём:

```text
2026-09-10
```

Ожидается:

```text
occupied_days = 1
```

### Итоговые контрольные значения

Период `2026-09-01 → 2026-09-10` содержит 10 календарных дней включительно.

Ожидаемый результат будущего Script Report:

| Equipment | Occupied Days | Period Days | Utilization |
|---|---:|---:|---:|
| A | 5 | 10 | 50% |
| B | 5 | 10 | 50% |
| C | 1 | 10 | 10% |

Эти значения понадобятся на S06–S09.

---

## 7. Проверить владельцев без изменения данных

Под `Administrator` можно открыть List `Rental` и добавить колонку `Owner`, если она доступна в текущем представлении.

Либо проверить через Bench console:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

В console:

```python
frappe.get_all(
    "Rental",
    fields=["name", "owner", "start_date", "end_date", "status"],
    order_by="creation asc",
)
```

В результате должны присутствовать записи обоих операторов.

Здесь `get_all` используется намеренно под `Administrator` только как техническая проверка подготовленных данных. Семантику `get_all` относительно пользовательских permissions мы отдельно разберём на S04.

Закройте console:

```python
exit()
```

---

## 8. Проверить, что Site-данные не попали в Git

После создания Users, Equipment, Customer и Rental:

```bash
cd ~/frappe/rental-training-bench
git -C apps/rental_training status --short
```

Ожидается чистое рабочее дерево.

Создание обычных рабочих Documents на Site не должно превращать их в исходники App.

Это важная граница:

```text
App
→ DocType metadata, controllers, обязательная конфигурация

Site
→ Users и рабочие Documents
```

---

## Результат этапа

К концу S00:

```text
готовый rental_training подтверждён
два Rental Operator созданы
один Rental Manager создан
есть Rentals двух разных owner
есть контролируемый период и ожидаемые расчётные значения
рабочие данные не появились в Git
```

На S01 появится первое новое требование к самому App: `Rental Operator` больше не должен видеть Rentals другого оператора.
