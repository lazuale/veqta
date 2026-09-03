# S04. Разделить пользовательское и системное чтение

До этого момента permissions проверялись через Desk. Теперь нужно увидеть ту же границу непосредственно в серверном коде.

Новое требование:

> Код, который читает данные от имени пользователя, не должен случайно вернуть Rental, который этому пользователю запрещён.

Для этого нужно различать три ситуации:

```text
список в пользовательском контексте
→ get_list

доверенная системная выборка
→ get_all

один конкретный Document для пользователя
→ get_doc + явная проверка read
```

Связанные материалы:

- [`S01_OWNER_PERMISSIONS.md`](S01_OWNER_PERMISSIONS.md);
- [`S03_REPORT_BUILDER.md`](S03_REPORT_BUILDER.md);
- [`../../../frappe-architecture-standard/04_SECURITY.md`](../../../frappe-architecture-standard/04_SECURITY.md);
- [`../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md`](../../../frappe-architecture-standard/05_DATA_ACCESS_PERFORMANCE.md).

Первичный источник:

- https://docs.frappe.io/framework/user/en/api/database
- https://docs.frappe.io/framework/user/en/api/document

---

## 1. Найти имена контрольных Rentals

Откройте Bench console под Site:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Пока session user — `Administrator`, найдите по одному Rental каждого оператора:

```python
rental_a = frappe.db.get_value(
    "Rental",
    {"owner": "operator-a@example.test"},
    "name",
)

rental_b = frappe.db.get_value(
    "Rental",
    {"owner": "operator-b@example.test"},
    "name",
)

rental_a, rental_b
```

Оба значения должны быть непустыми.

`rental_b` дальше будет заведомо чужим Document для operator A.

---

## 2. Переключить контекст пользователя

В той же console:

```python
frappe.set_user("operator-a@example.test")
frappe.session.user
```

Ожидается:

```text
operator-a@example.test
```

Теперь последующие permission-aware операции выполняются в контексте этого пользователя.

---

## 3. Проверить `get_list`

Выполните:

```python
rows = frappe.get_list(
    "Rental",
    fields=["name", "owner", "status"],
    order_by="creation asc",
)
rows
```

В результате должны быть только Rentals, разрешённые `operator-a@example.test`.

Проверьте явно:

```python
[row.owner for row in rows]
```

Ожидается, что среди owner нет:

```text
operator-b@example.test
```

Это нормальная ответственность `get_list`: пользовательская выборка учитывает permission-модель текущего пользователя.

---

## 4. Выполнить тот же запрос через `get_all`

Теперь:

```python
all_rows = frappe.get_all(
    "Rental",
    fields=["name", "owner", "status"],
    order_by="creation asc",
)
all_rows
```

В контрольном наборе должны появиться Rentals обоих операторов.

Проверьте:

```python
sorted({row.owner for row in all_rows})
```

Смысл наблюдения:

```text
get_list
→ применяет пользовательскую permission boundary

get_all
→ выполняет выборку без обычного permission filtering
```

`get_all` не является «улучшенной версией get_list» и не должен использоваться только потому, что первая функция «не вернула нужные строки».

---

## 5. Когда `get_all` допустим

У `get_all` есть нормальные сценарии.

Например:

```text
миграция
системная сверка
внутренняя фоновая операция
доверенный manager-only отчёт
```

Общий смысл:

> Авторизация уже определена другой границей, а самой операции действительно нужен полный набор данных.

Опасный сценарий выглядит иначе:

```python
@frappe.whitelist()
def my_rentals():
    return frappe.get_all("Rental", fields=["name", "customer"])
```

Если этот метод вызывается обычным оператором и не имеет отдельной проверки, он способен вернуть данные за пределами его обычного доступа.

На S04 такой endpoint создавать не нужно. Достаточно понять саму границу.

---

## 6. Проверить обычный `get_doc`

Оставаясь под `operator-a@example.test`, загрузите чужой Rental B:

```python
doc = frappe.get_doc("Rental", rental_b)
doc.name, doc.owner
```

Сам факт загрузки объекта не является доказательством права пользователя его читать.

Теперь выполните явную проверку:

```python
doc.check_permission("read")
```

Ожидается `frappe.PermissionError`.

Если exception прервал выражение в console, это и есть ожидаемый результат проверки.

---

## 7. Использовать загрузку с явной permission check

Ту же границу можно выразить сразу при загрузке:

```python
frappe.get_doc("Rental", rental_b, check_permission="read")
```

Для чужого Rental должен возникнуть отказ.

Для собственного:

```python
own_doc = frappe.get_doc("Rental", rental_a, check_permission="read")
own_doc.name
```

загрузка должна пройти.

Главное правило:

```text
Document найден в базе
≠
пользователь имеет право его видеть
```

---

## 8. Проверить manager context

Переключитесь:

```python
frappe.set_user("manager@example.test")
```

Проверьте:

```python
frappe.get_list(
    "Rental",
    fields=["name", "owner"],
    order_by="creation asc",
)
```

Менеджер должен увидеть Rentals обоих операторов, потому что его Standard DocType Permissions не ограничены `If Owner`.

Таким образом одна и та же функция `get_list` возвращает разный допустимый набор в зависимости от permission context.

---

## 9. Вернуть Administrator

Перед выходом обязательно верните пользователя:

```python
frappe.set_user("Administrator")
```

Закройте console:

```python
exit()
```

Это особенно полезная привычка в интерактивных экспериментах: не оставлять дальнейшие команды в неожиданном user context.

---

## 10. Что не нужно делать после этого наблюдения

Не создавайте wrapper вида:

```python
def safe_get_list(...):
    ...
```

только чтобы спрятать штатный Frappe API за собственной абстракцией.

Также не нужно запрещать `get_all` во всём приложении.

Нужно различать ответственность:

```text
user-facing data access
→ permission-aware путь

trusted system operation
→ осознанный полный доступ
```

---

## 11. Проверить Git

S04 — эксперимент с runtime-семантикой чтения. Нового состояния App он не создаёт.

```bash
cd ~/frappe/rental-training-bench
git -C apps/rental_training status --short
```

Рабочее дерево должно оставаться чистым после коммита S03.

---

## Результат этапа

К концу S04 на одних и тех же Rentals доказано:

```text
get_list учитывает permission boundary
get_all получает доверенный полный набор
get_doc сам по себе не доказывает право read
чтение одного пользовательского Document требует явной permission check
```

На S05 появится первый обязательный собственный отчёт App. Он сознательно будет manager-only, потому что его SQL должен видеть весь набор Rentals.
