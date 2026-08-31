# 25. Status против Workflow State

В Frappe слово **status** встречается слишком часто.

Из-за этого новичок легко начинает считать, что всё это одно и то же:

```text
status
workflow_state
docstatus
ToDo.status
```

Но это **четыре разные вещи**.

Если их смешать, Workflow быстро превращается в путаницу.

Проверено: **2026-08-31**.

---

## 1. Сначала вся картина на одном примере

Представим обычный DocType:

```text
Request
```

У одной заявки одновременно могут быть такие значения:

```text
status         = In Progress
workflow_state = Manager Review
docstatus      = 0
```

И параллельно у Бориса может существовать связанный `ToDo`:

```text
ToDo.status = Open
```

Никакого противоречия здесь нет.

Каждое поле отвечает на свой вопрос.

| Значение | Вопрос |
|---|---|
| `status` | в каком прикладном состоянии находится Request? |
| `workflow_state` | на каком шаге Workflow находится Request? |
| `docstatus` | Draft, Submitted или Cancelled сам Document? |
| `ToDo.status` | открыто ли конкретное назначение пользователя? |

Это и есть главная мысль главы.

---

# Обычный `status`

## 2. `status` — обычное поле DocType

Во Frappe нет требования, что каждый DocType обязан иметь поле:

```text
status
```

Если оно существует, это обычный DocField, который разработчик или администратор добавил в модель.

Например:

```text
Label: Status
Fieldname: status
Field Type: Select
Options:
New
In Progress
Waiting
Closed
```

Тогда документ хранит обычное значение:

```text
status = "In Progress"
```

По смыслу это часть **бизнес-модели конкретного DocType**.

---

## 3. `status` можно назвать вообще иначе

Например, вместо:

```text
status
```

можно сделать:

```text
stage
phase
state
condition
processing_status
```

Для Framework это просто поля.

Название `status` удобно и привычно, но само по себе не включает никакого специального Workflow engine.

---

## 4. Изменение `status` само по себе не является Workflow

Допустим, у `Request` есть:

```text
status:
New
In Progress
Done
```

Пользователь вручную изменил:

```text
New → Done
```

Если других правил нет, Frappe просто сохранит новое значение.

Он не начнёт автоматически проверять:

```text
кто имеет право сделать переход
какой предыдущий статус допустим
нужно ли согласование
кто должен подтвердить действие
```

Чтобы управлять переходами между состояниями, нужен уже отдельный механизм — **Workflow** или собственная серверная логика.

---

# `docstatus`

## 5. `docstatus` — системное поле каждого Document

В отличие от обычного `status`, `docstatus` добавлять не нужно.

Это системное поле Framework.

У него только три значения:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Это не произвольный бизнес-список.

Нельзя штатно придумать:

```text
3 = Approved
4 = Archived
5 = Waiting
```

Для таких состояний используются обычные поля или Workflow State.

---

## 6. `docstatus` отвечает за технический lifecycle документа

Простейшая схема Submittable DocType:

```text
Draft
  ↓ Submit
Submitted
  ↓ Cancel
Cancelled
```

То есть:

```text
docstatus = 0
        ↓ submit()
docstatus = 1
        ↓ cancel()
docstatus = 2
```

Эту механику мы подробно разбирали в главе 10.

---

## 7. Несубмиттабельный DocType обычно остаётся `docstatus = 0`

Например, обычный справочник или рабочая карточка может жить так:

```text
status = New
status = In Progress
status = Closed
```

но всё время иметь:

```text
docstatus = 0
```

Это нормально.

Бизнес-состояние документа и технический Submit lifecycle — разные оси.

---

# Workflow State

## 8. Workflow State появляется только когда нужен Workflow

Представим процесс согласования:

```text
Draft
  ↓ Send for Review
Manager Review
  ↓ Approve
Approved
```

Здесь нам уже важно не только хранить красивую надпись.

Нужно знать:

```text
из какого состояния можно перейти
в какое состояние
какая Role имеет право выполнить действие
какое условие должно выполниться
что произойдёт с docstatus
```

Это задача **Workflow**.

Текущее положение документа в таком процессе хранится в поле Workflow State.

---

## 9. По умолчанию поле называется `workflow_state`

В DocType `Workflow` есть настройка:

```text
Workflow State Field
```

Значение по умолчанию:

```text
workflow_state
```

Но это имя можно изменить.

Например:

```text
approval_state
```

Поэтому технически правильнее говорить:

> поле состояния активного Workflow

а не считать, что оно всегда обязано называться `workflow_state`.

---

## 10. Если поля нет, Frappe создаёт его сам

Это важная механика текущего v16.

При сохранении Workflow Framework проверяет целевой DocType.

Если поля из `Workflow State Field` нет, создаётся `Custom Field` примерно такого типа:

```text
Field Type: Link
Options: Workflow State
Hidden: Yes
Allow on Submit: Yes
No Copy: Yes
```

Поэтому для простого Workflow обычно не нужно заранее вручную создавать поле `workflow_state`.

---

## 11. Workflow State — это не обычный Select

По умолчанию создаваемое поле является:

```text
Link → Workflow State
```

А сами названия состояний являются отдельными записями DocType:

```text
Workflow State
```

Например:

```text
New
Manager Review
Approved
Rejected
```

У Workflow State можно также задавать визуальный Style.

---

# Workflow State и docstatus

## 12. У каждого Workflow State отдельно задаётся Doc Status

Вот здесь обычно и возникает главная путаница.

В таблице состояний Workflow есть колонка:

```text
Doc Status
```

В ней указывается:

```text
0
1
2
```

То есть Workflow State и `docstatus` связаны, но **не являются одним полем**.

Например:

| Workflow State | Doc Status |
|---|---:|
| New | 0 |
| Manager Review | 0 |
| Approved | 1 |
| Cancelled | 2 |

Тогда документ может последовательно пройти:

```text
New
workflow_state = New
docstatus = 0

        ↓

Manager Review
workflow_state = Manager Review
docstatus = 0

        ↓

Approved
workflow_state = Approved
docstatus = 1
```

То есть несколько Workflow States спокойно могут соответствовать одному `docstatus`.

---

## 13. Переход в состояние с Doc Status 1 делает настоящий Submit

В текущем v16 Workflow не просто записывает цифру в `docstatus`.

При переходе:

```text
Draft-state → state with Doc Status 1
```

Framework вызывает обычный механизм:

```python
doc.submit()
```

А если Submitted Document переходит в состояние с:

```text
Doc Status = 2
```

Framework вызывает:

```python
doc.cancel()
```

Поэтому Workflow встроен в обычный lifecycle Document, а не существует параллельно ему.

---

## 14. Нельзя нарушить базовые правила docstatus через Workflow

Например, текущий v16 не разрешает настроить переход:

```text
Submitted → Draft
```

то есть:

```text
Doc Status 1 → 0
```

Также нельзя перейти прямо:

```text
Draft → Cancelled
```

то есть:

```text
0 → 2
```

без Submit.

И из уже Cancelled состояния дальнейшие Workflow transitions не допускаются.

Workflow расширяет lifecycle, но не отменяет фундаментальные правила `docstatus`.

---

# `status` и Workflow State вместе

## 15. Обычный `status` не исчезает при включении Workflow

Допустим, у `Request` уже было поле:

```text
status
```

со значениями:

```text
Open
In Progress
Closed
```

Позже добавили Workflow:

```text
New
Manager Review
Approved
Rejected
```

Тогда у документа существуют **два отдельных поля**:

```text
status
workflow_state
```

Frappe не обязан автоматически делать их одинаковыми.

Например:

```text
status         = In Progress
workflow_state = Manager Review
```

Это допустимо, если именно так спроектирована модель.

---

## 16. Workflow может специально обновлять обычное поле

В строке Workflow State есть параметры:

```text
Update Field
Update Value
```

Например:

```text
Workflow State: Approved
Update Field: status
Update Value: Closed
```

После перехода можно получить:

```text
workflow_state = Approved
status         = Closed
```

Но это уже **явно настроенное действие Workflow**.

Не следует считать, что `status` синхронизируется с Workflow State автоматически просто из-за одинаковых слов.

---

## 17. Не дублируй две одинаковые машины состояний без причины

Плохая модель:

```text
status:
New
Review
Approved
Rejected

workflow_state:
New
Review
Approved
Rejected
```

и оба поля пытаются обозначать абсолютно одно и то же.

Тогда почти неизбежно появятся ситуации:

```text
status = Review
workflow_state = Approved
```

и никто уже не понимает, какое поле истинное.

Если Workflow полностью управляет процессом, спроси:

> нужен ли мне отдельный `status` вообще?

Иногда нужен.

Но причина должна быть понятной.

---

## 18. Когда отдельный `status` всё-таки полезен

Допустим, Workflow отвечает за согласование:

```text
Draft
Manager Review
Approved
```

А обычный `status` отвечает уже за исполнение после согласования:

```text
Not Started
In Progress
Done
```

Тогда оси разные:

```text
workflow_state
→ согласование

status
→ фактическое выполнение
```

Например:

```text
workflow_state = Approved
status         = In Progress
```

Такая модель уже имеет смысл.

---

# Что пользователь видит в List View

## 19. Workflow State может визуально перекрывать обычный Status

Активный Workflow влияет на индикатор документа в List View.

По умолчанию Frappe может показывать именно Workflow State как основной статусный индикатор.

Например вместо:

```text
In Progress
```

пользователь увидит:

```text
Manager Review
```

Хотя обычное поле `status` никуда не исчезло.

---

## 20. `Don't Override Status` влияет на отображение, а не объединяет поля

У Workflow есть настройка:

```text
Don't Override Status
```

Она говорит интерфейсу не подменять обычный status-индикатор Workflow State в List View.

Это **не означает**:

```text
workflow_state перестал существовать
```

и не означает:

```text
status теперь автоматически синхронизирован с workflow_state
```

Это прежде всего поведение отображения.

В v16 аналогичная настройка существует и на уровне отдельных Workflow States:

```text
Don't Override Status
```

поэтому отдельные состояния тоже могут не подменять стандартный индикатор.

---

# ToDo Status

## 21. `ToDo.status` относится к назначению, а не к исходному документу

Вернёмся к примеру:

```text
Request REQ-0001
```

Борису назначено проверить его.

У связанного `ToDo` может быть:

```text
status = Open
```

Это означает:

> назначение Бориса ещё открыто.

Но сам `Request` может иметь:

```text
status = In Progress
workflow_state = Manager Review
docstatus = 0
```

Это независимые значения.

---

## 22. Закрытие ToDo не обязано менять Request

Если Борис нажал Done на своём Assignment:

```text
ToDo.status:
Open → Closed
```

это не означает автоматически:

```text
Request.status = Closed
```

или:

```text
Request.workflow_state = Approved
```

или:

```text
Request.docstatus = 1
```

Assignment отвечает на вопрос:

```text
кто должен сделать работу?
```

Workflow — на вопрос:

```text
какие контролируемые переходы проходит Document?
```

Это разные механизмы.

---

# Четыре состояния рядом

## 23. Один документ может выглядеть так

```text
Request REQ-0001

status         = In Progress
workflow_state = Manager Review
docstatus      = 0
```

Связанный Assignment:

```text
ToDo
allocated_to = boris@example.com
status       = Open
```

После проверки Борис закрывает Assignment:

```text
ToDo.status = Closed
```

Но `Request` пока остаётся:

```text
status         = In Progress
workflow_state = Manager Review
docstatus      = 0
```

После отдельного Workflow action `Approve`:

```text
workflow_state = Approved
docstatus      = 1
```

А `status` изменится только если это предусмотрено моделью или настройкой `Update Field`.

---

## 24. Сводная таблица

| Механизм | Где хранится | Значения | Что означает |
|---|---|---|---|
| `status` | обычный DocField бизнес-DocType | любые заданные моделью | прикладное состояние |
| Workflow State | поле, обычно `workflow_state` | записи `Workflow State` | шаг управляемого Workflow |
| `docstatus` | системное поле Document | 0 / 1 / 2 | Draft / Submitted / Cancelled |
| `ToDo.status` | отдельный `ToDo` | Open / Closed / Cancelled | состояние Assignment / ToDo |

Если эта таблица понятна, следующая глава про Workflow будет значительно проще.

---

# Как выбирать механизм

## 25. Нужен просто рабочий статус

Требование:

> пользователь выбирает New / In Progress / Done.

Обычно достаточно:

```text
Select status
```

Workflow не нужен только потому, что в системе есть несколько состояний.

---

## 26. Нужны контролируемые переходы и роли

Требование:

```text
оператор создаёт
руководитель согласует
только после согласования документ можно Submit
```

Это уже нормальный кандидат на:

```text
Workflow
```

Потому что важно не просто текущее значение, а разрешённые **переходы**.

---

## 27. Нужен официальный Submit lifecycle

Если важно различать:

```text
Draft
Submitted
Cancelled
```

то это:

```text
docstatus
```

и Submittable DocType.

Workflow может управлять этим переходом, но сам механизм Submit остаётся системным `docstatus`.

---

## 28. Нужно назначить человеку работу

Если задача звучит:

> Борис должен проверить этот Request до пятницы.

это прежде всего:

```text
Assignment / ToDo
```

а не новый Workflow State `Assigned to Boris`.

---

# Типичные ошибки

## 29. Ошибка: считать `status` системным lifecycle

```text
status = Submitted
```

не делает документ действительно Submitted.

Если:

```text
docstatus = 0
```

то для Framework документ всё ещё Draft.

---

## 30. Ошибка: вручную менять `workflow_state`

Если Workflow активен, не стоит относиться к его state field как к обычному свободному Select.

Frappe проверяет допустимые transitions.

Правильная модель:

```text
Workflow Action
→ проверка перехода
→ новое Workflow State
```

а не:

```text
пользователь просто написал другое значение в workflow_state
```

---

## 31. Ошибка: считать Workflow заменой любого `status`

Workflow нужен не для красоты и не для любого поля со стадиями.

Если нет:

```text
разных ролей
ограниченных переходов
approval logic
условий перехода
```

обычного Select часто достаточно.

---

## 32. Ошибка: связывать Assignment и Workflow только по названию

Например:

```text
workflow_state = Review
```

не означает автоматически:

```text
создать ToDo ревьюеру
```

А:

```text
ToDo.status = Closed
```

не означает автоматически:

```text
workflow_state = Approved
```

Если процессы нужно связать, это должно быть сделано явно подходящим механизмом.

---

## 33. Мини-практика

Возьми учебный `Request`.

### Шаг 1. Обычный status

Добавь поле:

```text
Status
status
Select
```

со значениями:

```text
New
In Progress
Done
```

Создай документ и установи:

```text
status = In Progress
```

Проверь, что:

```text
docstatus = 0
```

при этом никак не обязан меняться.

### Шаг 2. Посмотри системный docstatus

Если `Request` не Submittable, запомни:

```text
status может меняться много раз
но docstatus остаётся 0
```

### Шаг 3. Создай простой Workflow

Состояния:

| State | Doc Status |
|---|---:|
| New | 0 |
| Review | 0 |
| Approved | 0 |

Для первой практики не нужен Submit.

Проверь, что появляется отдельное поле состояния Workflow.

### Шаг 4. Сравни два поля

Добейся состояния:

```text
status         = In Progress
workflow_state = Review
```

И убедись, что это два разных значения.

### Шаг 5. Добавь Assignment

Назначь этот Request другому пользователю.

Теперь мысленно выпиши:

```text
Request.status
Request.workflow_state
Request.docstatus
ToDo.status
```

Если понятно, почему все четыре могут иметь разные значения, цель главы достигнута.

---

## 34. Что запомнить

1. **`status` — обычное прикладное поле.**
2. **`docstatus` — системный lifecycle 0 / 1 / 2.**
3. **Workflow State — текущее состояние управляемого Workflow.**
4. **Workflow State и `docstatus` связаны через настройку каждого Workflow State, но это разные поля.**
5. **Несколько Workflow States могут иметь один и тот же `docstatus`.**
6. **`ToDo.status` относится к Assignment, а не к бизнес-документу.**
7. **Не создавай две одинаковые машины состояний через `status` и Workflow State без явной причины.**

---

## Источники

- Frappe Framework — Docstatus: https://docs.frappe.io/framework/doctypes/docstatus
- Workflows: https://docs.frappe.io/erpnext/workflows
- Workflow State: https://docs.frappe.io/erpnext/workflow-state
- Frappe v16 — `Workflow` metadata: https://github.com/frappe/frappe/blob/version-16/frappe/workflow/doctype/workflow/workflow.json
- Frappe v16 — `Workflow` controller: https://github.com/frappe/frappe/blob/version-16/frappe/workflow/doctype/workflow/workflow.py
- Frappe v16 — workflow engine: https://github.com/frappe/frappe/blob/version-16/frappe/model/workflow.py
- Frappe v16 — Workflow Document State metadata: https://github.com/frappe/frappe/blob/version-16/frappe/workflow/doctype/workflow_document_state/workflow_document_state.json
- Frappe v16 — status indicator logic: https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/model/indicator.js

---

Предыдущая глава: [24. Assignment Rule](24_ASSIGNMENT_RULE.md)

Следующая глава: **26. Workflow и переходы**.
