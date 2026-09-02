# Граф зависимостей этапов нового практикума Frappe

Статус: **черновик для архитектурной проверки**.

Продолжает:

- [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md);
- [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md).

Следующий слой — [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md).

Граф показывает **не темы занятий**, а минимальные законченные результаты и реальные зависимости между ними.

Главное правило:

> `A → B` означает только то, что результат B нельзя корректно получить или проверить без результата A.

Педагогический порядок сам по себе зависимостью не считается.

---

# 1. CORE-граф

```text
P00  готовая среда Frappe v16
 ↓
P01  учебный App установлен на Site
 ├───────────────┐
 ↓               ↓
P02 Equipment    P03 Customer
 └───────┬───────┘
         ↓
P04 Rental + Rental Item + Links
 ├────────────┬────────────┬────────────┐
 ↓            ↓            ↓            ↓
P05 status    P06 Desk     P07 rules    P09 permissions
 └──────┬─────┘            │            │
        └──────────────┬────┘            │
                       ↓                 │
                  P08 conflict           │
                       └─────────┬────────┘
                                 ↓
                         ┌───────┴───────┐
                         ↓               ↓
                     P10 tests       P11 delivery audit
                         └───────┬───────┘
                                 ↓
                           P12 clean install
```

Точные зависимости:

```text
P00 → P01

P01 → P02
P01 → P03

P02 + P03 → P04

P04 → P05
P04 → P06
P04 → P07
P04 → P09

P05 + P07 → P08

P08 + P09 → P10
P08 + P09 → P11

P06 + P10 + P11 → P12
```

---

# 2. P00 — совместимая учебная среда

Техническая предпосылка:

```text
Bench
Frappe v16
Site
developer mode
Git
```

Это не production-курс по администрированию сервера.

---

# 3. P01 — граница App

Создаётся нейтральный учебный App и устанавливается на Site.

Ученик должен различать:

```text
Bench ≠ Site ≠ App ≠ Module
```

---

# 4. P02 — Equipment

**Покрывает:** `R01`, `R06`, часть `D00`.

**Зависит от:** `P01`.

Создаётся Standard `Equipment`, простой тип остаётся `Select`, naming выбирается осознанно.

---

# 5. P03 — Customer

**Покрывает:** `R02`, часть `D00`.

**Зависит от:** `P01`.

Создаётся Standard `Customer` и выбирается naming.

`P02` и `P03` независимы друг от друга.

---

# 6. P04 — Rental-композиция

**Покрывает:** `R03`, `R04`, `R05`, часть `D00`.

**Зависит от:** `P02` + `P03`.

```text
Rental
└── Rental Item [Child DocType]

Rental.customer       → Link → Customer
Rental.items          → Table MultiSelect → Rental Item
Rental Item.equipment → Link → Equipment
```

Текущее требование — выбрать несколько существующих Equipment, а child row содержит только Link. Поэтому `Table MultiSelect` точнее обычного `Table`; если у строки появятся собственные данные отношения, выбор пересматривается.

---

# 7. P05 — business status

**Покрывает:** `R08`.

**Зависит от:** `P04`.

```text
Planned
Active
Returned
```

Пока требуется только хранить состояние, не появляются `Workflow`, `Is Submittable` или отдельный status-справочник.

---

# 8. P06 — стандартный Desk

**Покрывает:** `R16`.

**Зависит от:** `P04`.

Проверяются `Form`, `List`, Link controls, Table MultiSelect и фильтры.

Результат: основной сценарий работает без собственного frontend.

---

# 9. P07 — серверные инварианты одного Rental

**Покрывает:** `R09`, `R10`.

**Зависит от:** `P04`.

В Controller:

```text
end_date >= start_date
одно Equipment не повторяется дважды в Rental
```

Оба правила доказываются через обычный серверный `Document.insert()`, а не только через Form.

Ключ:

```text
Client Script       = UX
Controller.validate = гарантия модели на обычном Document path
```

---

# 10. P08 — правило между Rentals

**Покрывает:** `R11`.

**Зависит от:** `P05` + `P07`.

Проверяется пересечение периодов одного Equipment только для `status = Active`.

CORE использует включительные границы дат:

```text
10–12 + 12–14 → конфликт
10–12 + 13–14 → допустимо
```

Это первый инвариант Rental, который читает другие Documents. Внутреннее чтение не должно пропустить конфликт только из-за permission-filtering пользовательского List, а текущий Rental должен исключаться из self-conflict при редактировании.

Граница фиксируется явно:

```text
последовательная validate-проверка
≠
полная concurrency/locking strategy
```

---

# 11. P09 — Roles/Permissions

**Покрывает:** `R13`.

**Зависит от:** `P04`.

Используются штатные `Role` + `DocType Permissions`.

`P09` не зависит от P07/P08: после появления реальных DocTypes права можно проектировать независимо от бизнес-проверок.

---

# 12. P10 — tests

**Покрывает:** `R23`.

**Зависит от:** `P08` + `P09`.

Тестируются наши контракты:

```text
даты
дубли Equipment
конфликт Rentals
permissions
```

Не тестируется Framework ради coverage.

---

# 13. P11 — delivery audit

**Покрывает:** `R21`, `R22`.

**Зависит от:** `P08` + `P09` и завершённой CORE-модели.

Проверяется:

```text
обязательные Standard DocTypes находятся в App
метаданные под Git
Controller под Git
обязательные Role/config доставляются штатным механизмом
migrate не заменяется ручным SQL
patch появляется только для реальной трансформации существующих данных
```

---

# 14. P12 — clean install

**Покрывает:** `R24`.

**Зависит от:** `P06` + `P10` + `P11`.

Финальная проверка:

```text
clean compatible Frappe Site
+ App from Git
+ install-app
+ migrate
+ tests
+ main user scenario
```

---

# 15. NEXT-зависимости

```text
N01 R07 Site setting       P04          → Single DocType
N02 R12 history/comments   P04          → Version/Comment/File
N03 R14 manager-only field P09          → Permission Level
N04 R15 assignment         P04 + users  → Assignment/ToDo
N05 R17 navigation         P04          → Workspace
N06 R18 calendar           P04          → Calendar view
N07 R19 print              P04          → Print Format
N08 R20 simple report      P05 + data   → Report Builder
```

NEXT не является продолжением CORE по умолчанию.

---

# 16. Архитектурные развилки

## D00 naming

Naming выбирается при создании каждого самостоятельного DocType, а не выносится в поздний необязательный урок.

## D01 Workflow

```text
P05 + P09 + реальное требование переходов по ролям
→ Workflow?
```

## D02 docstatus

```text
P04 + реальное требование фиксированного транзакционного факта
→ Is Submittable/docstatus?
```

D01 и D02 независимы.

## D03 Equipment Type

```text
P02 Select
→ у типа появляются собственные атрибуты/управление
→ Equipment Type DocType + Link
→ проверка миграции существующих данных
```

## D04 Web Form

Сначала определяется, является ли внешняя заявка тем же `Rental` или отдельным `Rental Request`, и только затем выбирается Web Form.

## D05 Notification

Появляется только при реальном требовании напоминания; scheduler/job добавляется лишь если Notification недостаточно.

---

# 17. EXT

```text
X01 E01 CRUD     P07 + P09       → Document REST API
X02 E02 command  P05 + P07 + P09 → Document/whitelisted method
X03 E03 event    lifecycle event → Webhook
```

---

# 18. Контрольные состояния

```text
C1 after P04 → связанная модель существует
C2 after P06 → модель полезна через Desk
C3 after P10 → модель защищает себя и имеет автоматические контракты
C4 after P12 → App воспроизводим на чистом Site
```

---

# 19. Что граф не означает

Граф **не означает**, что:

- каждый `Pxx` обязан быть одним уроком;
- все NEXT обязательны;
- все GATE должны сработать;
- Workflow обязателен;
- Is Submittable обязателен;
- API обязателен;
- количество занятий известно заранее.

Он фиксирует только реальные зависимости результатов.