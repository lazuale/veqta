# S05B. Пройти полный сценарий Rental через стандартный Desk

К S05B модель уже собрана:

```text
Equipment
Customer

Rental
├── customer   → Link → Customer
├── start_date → Date
├── end_date   → Date
├── status     → Select
│                ├── Planned
│                ├── Active
│                └── Returned
└── items      → Table MultiSelect → Rental Item
                                     └── equipment → Link → Equipment
```

До этого мы проверяли части модели по отдельности.

Теперь нужен другой вопрос:

> Можно ли уже выполнить нормальную рабочую операцию от начала до конца, используя только штатный интерфейс Frappe?

S05B ничего нового не добавляет в предметную модель.

Мы проверяем уже существующую модель через:

```text
Desk
Form View
List View
Awesomebar / поиск
Link controls
Table MultiSelect
filters
```

На этом этапе **не создаются**:

```text
custom frontend
SPA
Workspace ради красивой стартовой страницы
Client Script
custom List JS
custom Form JS
Web Form
Portal
Report
```

Если обычный внутренний CRUD-сценарий уже нормально выражается стандартным Desk, собственного UI пока не требуется.

Связанные документы:

- [`S04_RENTAL_COMPOSITION.md`](S04_RENTAL_COMPOSITION.md);
- [`S05A_RENTAL_STATUS.md`](S05A_RENTAL_STATUS.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/09_UI_REPORTING.md`](../../frappe-architecture-standard/09_UI_REPORTING.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/desk
- https://docs.frappe.io/framework/user/en/api/list
- https://docs.frappe.io/framework/user/en/basics/doctypes

---

# 1. Что именно доказывает S05B

Frappe Desk читает metadata DocType и предоставляет стандартные представления для работы с Documents.

Нас интересует не факт существования экранов, а законченный пользовательский результат:

```text
создать Equipment
→ найти его в Equipment List
→ создать Customer
→ найти его в Customer List
→ создать Rental
→ выбрать созданные/существующие Documents через Links
→ сохранить Rental
→ найти его в List
→ отфильтровать список
→ открыть Rental повторно
→ изменить и снова сохранить
```

Если всё это работает, для текущего внутреннего сценария уже есть полноценный UI.

Архитектурная формула:

```text
DocType metadata
      ↓
стандартный Desk
      ↓
рабочая операция пользователя
```

---

# 2. Запустить dev-среду

Из корня Bench:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте:

```text
http://rental.localhost:8000/app
```

Войдите как `Administrator`.

---

# 3. Проверить Equipment

Через Awesomebar найдите:

```text
Equipment List
```

Создайте несколько записей, если их ещё нет.

Пример:

```text
Excavator CAT 320
Loader Volvo L120
Generator Atlas 50
```

Проверьте:

- записи сохраняются;
- `equipment_name` используется как Title Field;
- записи находятся через список и поиск;
- открытие из списка ведёт к той же записи.

---

# 4. Проверить Customer

Откройте:

```text
Customer List
```

Создайте несколько клиентов.

Пример:

```text
North Construction
Delta Service
```

Проверьте создание, поиск и повторное открытие записи.

---

# 5. Создать Rental

Откройте:

```text
Rental List
```

Создайте Rental:

```text
customer   = North Construction
start_date = 2026-09-10
end_date   = 2026-09-12
status     = Planned
```

В `items` добавьте несколько Equipment.

Проверьте, что Link/Table MultiSelect выбирает существующие Documents, а не хранит произвольный текст вместо связи.

Сохраните Rental.

---

# 6. Найти Rental повторно

Вернитесь в `Rental List`.

Проверьте:

```text
поиск
filters
сортировку
повторное открытие записи
```

Измените один из обычных атрибутов, сохраните и снова откройте запись.

---

# 7. Проверить status в рабочем сценарии

Измените:

```text
Planned → Active
```

Сохраните.

Затем:

```text
Active → Returned
```

На этом этапе мы не проверяем переходы Workflow. S05A определил `status` как обычное состояние предметной модели.

---

# 8. Что здесь важно увидеть

Весь сценарий выполнен без собственного интерфейса:

```text
создание
редактирование
поиск
списки
Links
состав Rental
статус
```

Это не означает, что Desk подходит любому будущему продукту. Это означает только, что **для текущего требования** Framework уже предоставляет достаточный пользовательский интерфейс.

---

# 9. Когда собственный UI появится позже

Он станет оправдан, если появится реальное требование, например:

```text
оператор обрабатывает сотни Rentals в час;
нужен специализированный drag-and-drop планировщик;
требуется мобильный интерфейс;
нужна отдельная клиентская навигация;
Desk создаёт измеримое препятствие рабочему процессу.
```

Тогда собственный интерфейс будет решать новую UX-ответственность, а не создаваться заранее.

---

# 10. Результат S05B

После этапа ученик должен уметь объяснить:

```text
DocType задаёт модель
Desk предоставляет стандартные представления
Form/List не являются предметной моделью
интерфейс выбирается после модели
собственный frontend нужен только при отдельном UX-требовании
```

Следующий этап: [`S05C_RENTAL_LOCAL_INVARIANTS.md`](S05C_RENTAL_LOCAL_INVARIANTS.md).