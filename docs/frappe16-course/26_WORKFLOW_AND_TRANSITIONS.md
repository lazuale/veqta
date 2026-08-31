# 26. Workflow и переходы

В прошлой главе мы развели четыре разные вещи:

```text
status
workflow_state
docstatus
ToDo.status
```

Теперь можно спокойно собрать настоящий **Workflow**.

Workflow нужен не для красивого цветного статуса.

Он отвечает на более строгий вопрос:

> кто, из какого состояния, каким действием и при каких условиях может перевести Document в следующее состояние?

Проверено: **2026-08-31**.

---

## 1. Самая простая картина

Представим DocType:

```text
Request
```

И процесс:

```text
New
  ↓ Send for Review
Review
  ↓ Approve
Approved

Review
  ↓ Reject
Rejected
```

Но одного списка состояний мало.

Нужно ещё определить:

```text
кто может нажать Send for Review?

кто может Approve?

кто может Reject?

можно ли Approve только при заполненном поле?

что произойдёт с docstatus?
```

Именно это и описывает Workflow.

---

# Из чего состоит Workflow

## 2. У Workflow есть четыре главных элемента

Для первого прохода достаточно запомнить:

```text
Workflow State
→ состояние

Workflow Action Master
→ название действия

Workflow Transition
→ правило перехода

Workflow
→ собирает всё вместе для конкретного DocType
```

Например:

```text
State: New
Action: Send for Review
Next State: Review
Allowed: Request User
```

Это означает:

> пользователь с ролью `Request User`, находясь в состоянии `New`, может выполнить действие `Send for Review`, после чего документ перейдёт в `Review`.

---

## 3. Workflow State — просто справочник названий состояний

Отдельный DocType:

```text
Workflow State
```

может содержать записи:

```text
New
Review
Approved
Rejected
```

У состояния также есть визуальный `Style`.

Например:

```text
Approved → Success
Rejected → Danger
Review   → Warning
```

Это влияет на визуальное представление состояния.

Но сам Workflow State ещё не знает:

```text
из какого состояния сюда можно попасть
кто может сделать переход
какое действие нужно нажать
```

Это задаётся позже в Workflow.

---

## 4. Workflow Action Master — название команды пользователя

Отдельный DocType:

```text
Workflow Action Master
```

хранит названия действий.

Например:

```text
Send for Review
Approve
Reject
Return
```

Здесь важно не путать две вещи:

```text
Workflow Action Master
→ справочник названий действий

Workflow Action
→ конкретное ожидающее действие по конкретному документу
```

Вторая сущность появится автоматически во время работы Workflow.

К ней вернёмся ниже.

---

# Собираем первый Workflow

## 5. Сначала сделаем Workflow без Submit

Чтобы не смешивать сразу две механики, первый пример оставим обычным.

Пусть все состояния имеют:

```text
Doc Status = 0
```

То есть Document всё время остаётся Draft с точки зрения системного `docstatus`.

Нам сейчас важна именно логика переходов.

Состояния:

| State | Doc Status | Only Allow Edit For |
|---|---:|---|
| New | 0 | Request User |
| Review | 0 | Request Manager |
| Approved | 0 | Request Manager |
| Rejected | 0 | Request Manager |

Получаем:

```text
New       docstatus=0
Review    docstatus=0
Approved  docstatus=0
Rejected  docstatus=0
```

Это абсолютно допустимый Workflow.

---

## 6. `Only Allow Edit For` относится к состоянию

В строке состояния есть поле:

```text
Only Allow Edit For
```

Например:

```text
State: Review
Only Allow Edit For: Request Manager
```

Смысл:

> пока документ находится в `Review`, редактирование через Workflow разрешено указанной Role.

Это не то же самое, что Role Permission Manager.

Базовые permissions DocType по-прежнему существуют.

Workflow добавляет ещё один слой правил поверх них.

---

## 7. Теперь добавляем Transitions

Для нашего примера нужны три перехода.

### Переход 1

```text
State: New
Action: Send for Review
Next State: Review
Allowed: Request User
```

### Переход 2

```text
State: Review
Action: Approve
Next State: Approved
Allowed: Request Manager
```

### Переход 3

```text
State: Review
Action: Reject
Next State: Rejected
Allowed: Request Manager
```

Получается уже настоящий граф:

```text
                 Approve
              ┌──────────→ Approved
              │
New ──Send──→ Review
              │
              └──────────→ Rejected
                 Reject
```

---

## 8. Transition — это не просто стрелка

У каждой строки `Workflow Transition` в текущем v16 есть основные поля:

```text
State
Action
Next State
Allowed
Allow Self Approval
Send Email To Creator
Condition
Transition Tasks
```

То есть переход одновременно определяет:

```text
откуда
↓
какой командой
↓
куда
↓
какой Role
↓
при каком условии
↓
с какими дополнительными действиями
```

Именно поэтому Workflow намного строже обычного поля `status`.

---

# Как пользователь видит Workflow

## 9. Пользователь не редактирует `workflow_state` как обычный Select

Допустим:

```text
workflow_state = Review
```

и пользователь имеет роль:

```text
Request Manager
```

Для него Framework вычислит допустимые переходы из `Review`.

В нашем примере:

```text
Approve
Reject
```

Пользователь выбирает **Action**.

Он не должен вручную делать:

```text
workflow_state = Approved
```

иначе вся идея контролируемого перехода потеряла бы смысл.

---

## 10. Frappe проверяет текущий State, Role и Condition

Упрощённо перед показом или выполнением действия Framework проверяет:

```text
текущий workflow_state
        ↓
есть ли Transition из этого State
        ↓
есть ли у User нужная Role
        ↓
выполнен ли Condition
        ↓
можно показать Action
```

Если хотя бы одно условие не выполняется, этот переход пользователю недоступен.

---

# Condition

## 11. У Transition может быть условие

Допустим, Request нельзя отправить на согласование без суммы.

Можно задать:

```python
doc.amount > 0
```

Тогда переход:

```text
New → Send for Review → Review
```

будет доступен только если:

```text
amount > 0
```

---

## 12. Condition — это серверная проверка, а не скрытие кнопки ради красоты

В текущем v16 условие проверяется через безопасное вычисление выражения.

Доступен сам документ как:

```python
doc
```

Например:

```python
doc.priority == "High"
```

или:

```python
doc.amount >= 100000
```

или:

```python
doc.owner != frappe.session.user
```

В expression также доступны ограниченные серверные функции, в том числе:

```text
frappe.db.get_value
frappe.db.get_list
frappe.session
frappe.utils.now_datetime
frappe.utils.get_datetime
frappe.utils.add_to_date
frappe.utils.now
```

Не нужно превращать Condition в большой Python-скрипт.

Если правило стало сложной бизнес-логикой, ему уже лучше жить в коде приложения.

---

## 13. Один State может иметь несколько разных переходов

Например:

```text
Review
├── Approve → Approved
├── Reject  → Rejected
└── Return  → New
```

Это обычная схема.

Причём разные переходы могут иметь разные Roles и Conditions.

Например:

```text
Approve
Allowed: Manager

Reject
Allowed: Manager

Escalate
Allowed: Senior Manager
Condition: doc.amount > 1000000
```

---

# Allow Self Approval

## 14. Self Approval означает согласование собственного документа

Представим:

```text
owner = anna@example.com
```

Анна создала Request и одновременно имеет роль:

```text
Request Manager
```

По Role она подходит для перехода:

```text
Review → Approve → Approved
```

Но нужно решить:

> может ли создатель сам согласовать собственный документ?

Для этого в Transition есть:

```text
Allow Self Approval
```

---

## 15. Если Self Approval выключен, проверяется `owner`

В текущем v16 логика фактически такая:

```text
Administrator
→ может

или

Allow Self Approval = Yes
→ может

или

current_user != doc.owner
→ может
```

Поэтому здесь под «создателем» понимается именно системный:

```text
owner
```

а не Assignment, не поле `requested_by` и не произвольный `employee`.

---

## 16. Self Approval не заменяет Roles

Если пользователь вообще не имеет Role из `Allowed`, то включённый:

```text
Allow Self Approval
```

не создаёт ему право Approve из воздуха.

Сначала пользователь должен подходить под Transition.

А уже затем проверяется ограничение собственного документа.

---

# Workflow State и изменение полей

## 17. State может обновить обычное поле Document

В строке Workflow State есть:

```text
Update Field
Update Value
```

Например:

```text
State: Approved
Update Field: status
Update Value: Closed
```

Когда документ перейдёт в `Approved`, Workflow дополнительно сделает:

```text
status = Closed
```

То есть:

```text
workflow_state = Approved
status = Closed
```

---

## 18. В v16 `Update Value` может быть выражением

Для состояния также есть:

```text
Evaluate as Expression
```

Если он выключен:

```text
Update Value = Approved
```

будет воспринят как обычный текст.

Если включён, значение вычисляется как expression.

Например концептуально:

```python
doc.amount * 2
```

Не стоит использовать это как замену полноценной серверной бизнес-логике, но для небольшого вычисляемого обновления механизм существует.

---

# Workflow и `docstatus`

## 19. Теперь добавим настоящий Submit

Предположим, `Request` является:

```text
Is Submittable = Yes
```

Теперь можно сделать:

| Workflow State | Doc Status |
|---|---:|
| New | 0 |
| Review | 0 |
| Approved | 1 |
| Cancelled | 2 |

Тогда схема будет:

```text
New
0
 ↓
Review
0
 ↓ Approve
Approved
1
 ↓ Cancel
Cancelled
2
```

---

## 20. Переход в State с Doc Status 1 вызывает настоящий `submit()`

Workflow не делает грубое:

```text
docstatus = 1
```

При переходе из Draft-state в состояние с:

```text
Doc Status = 1
```

текущий v16 вызывает:

```python
doc.submit()
```

То есть выполняется обычный lifecycle Submit со всеми его проверками и hooks.

---

## 21. Переход из Submitted в State с Doc Status 2 вызывает `cancel()`

Аналогично:

```text
Submitted State
        ↓
Transition
        ↓
Cancelled State
Doc Status = 2
```

приводит к:

```python
doc.cancel()
```

Поэтому Workflow встроен в lifecycle Document, а не существует рядом с ним отдельной параллельной системой.

---

## 22. Workflow не позволяет сломать базовую логику `docstatus`

Текущий v16 запрещает такие маршруты:

```text
Submitted → Draft
1 → 0
```

и:

```text
Draft → Cancelled
0 → 2
```

Также из уже Cancelled Document нельзя продолжать обычные Workflow transitions.

Workflow может усложнить жизненный цикл, но фундаментальные правила Submit/Cancel сохраняются.

---

# Workflow Action

## 23. `Workflow Action` — это ожидающая работа по конкретному Document

Это уже не `Workflow Action Master`.

Например у Request:

```text
REQ-0001
workflow_state = Review
```

есть два допустимых перехода для роли Manager:

```text
Approve
Reject
```

Framework может создать запись:

```text
Workflow Action
```

для пользователей/ролей, которым сейчас нужно принять решение.

Поэтому можно открыть отдельный список Workflow Actions и увидеть ожидающие согласования.

---

## 24. Workflow Action создаётся из следующих возможных переходов

Упрощённо логика такая:

```text
Document сохранился
        ↓
Workflow смотрит текущий State
        ↓
ищет следующие допустимые Transitions
        ↓
собирает их Allowed Roles
        ↓
создаёт открытые Workflow Actions
```

Когда переход выполнен, соответствующая запись Workflow Action помечается выполненной.

---

## 25. Optional State отличается от обычного состояния

В строке состояния есть:

```text
Is Optional State
```

Документация Frappe отдельно указывает:

> Workflow Actions не создаются для optional states.

Такой режим полезен для состояний, которые не являются обязательной очередной стадией согласования.

Например:

```text
Rejected
Cancelled
```

Но использовать optional state нужно по смыслу процесса, а не просто чтобы убрать уведомление.

---

# Email по Workflow

## 26. Workflow умеет отправлять уведомления о следующих действиях

У Workflow есть:

```text
Send Email Alert
```

А у строки состояния текущего v16 есть настройка:

```text
Send Email On State
```

Workflow Action также поддерживает уведомления для пользователей, которым доступны следующие действия.

Это удобно для простых approval-процессов.

Но Workflow email и обычный системный `Notification` — не одно и то же.

Notification подробно разберём в следующей главе.

---

# Transition Tasks — важное дополнение v16

## 27. В v16 Transition может запускать дополнительные задачи

У `Workflow Transition` теперь есть поле:

```text
Transition Tasks
```

Оно ссылается на:

```text
Workflow Transition Tasks
```

То есть при переходе можно выполнить дополнительное действие.

Например:

```text
Review
  ↓ Approve
Approved
  ↓
запустить Webhook
```

или:

```text
Approve
  ↓
Server Script
```

или действие, которое зарегистрировало собственное App.

---

## 28. В текущем v16 есть три типа Transition Task

Штатная модель поддерживает:

```text
App-defined action
Server Script
Webhook
```

Для App-defined action приложение регистрирует метод через hook:

```python
workflow_methods = [
    {
        "name": "Create Related Record",
        "method": "training_app.workflow.create_related_record",
    }
]
```

А метод получает текущий Document:

```python
def create_related_record(doc):
    ...
```

Это уже application code.

Для новичка важнее понять саму границу:

```text
Transition
→ меняет состояние

Transition Task
→ делает дополнительную работу во время этого перехода
```

---

## 29. Synchronous Transition Task может остановить переход

По умолчанию задача выполняется синхронно.

Смысл:

```text
начали Workflow transition
        ↓
выполнили synchronous task
        ↓
задача успешна
        ↓
переход продолжается
```

Если synchronous task падает с ошибкой, переход откатывается вместе с транзакцией.

Это подходит для действий, без которых переход нельзя считать завершённым.

Например:

```text
проверить обязательное внешнее условие
создать критичную связанную запись
```

---

## 30. Asynchronous Task уже не является частью атомарного перехода

Для задачи можно включить:

```text
Asynchronous
```

Тогда она запускается отдельным background job после commit.

Схема:

```text
Workflow transition завершён
        ↓ commit
        ↓
background job
        ↓
async task
```

Если такая задача потом завершится ошибкой, сам Workflow State назад автоматически не откатится.

Поэтому asynchronous вариант хорош для вещей вроде:

```text
необязательная интеграция
тяжёлая фоновая обработка
внешнее уведомление
```

а не для проверки, от которой зависит законность самого перехода.

---

# Что происходит при одном Workflow Action

## 31. Полная упрощённая цепочка

Пусть документ находится здесь:

```text
workflow_state = Review
```

Пользователь нажимает:

```text
Approve
```

Дальше текущий v16 делает примерно следующее:

```text
1. загрузить Document

2. получить активный Workflow

3. найти допустимые Transitions

4. проверить текущий State

5. проверить Role

6. проверить Condition

7. проверить Self Approval

8. установить Next State

9. применить Update Field / Update Value

10. выполнить synchronous Transition Tasks

11. привести docstatus к значению Next State
    через save / submit / cancel

12. записать Workflow comment в Timeline

13. после commit запустить asynchronous Transition Tasks

14. пересчитать следующие Workflow Actions
```

Это уже полноценный процесс, а не смена одного Select-поля.

---

# Один активный Workflow на DocType

## 32. Для одного DocType активным остаётся один Workflow

У Workflow есть флаг:

```text
Is Active
```

Если активировать Workflow для определённого `Document Type`, текущий v16 деактивирует другие Workflow этого же DocType.

То есть не надо рассчитывать на схему:

```text
один и тот же Request
одновременно управляется двумя активными Workflow
```

Если процесс сильно различается, чаще надо либо выразить ветвление внутри одного Workflow, либо пересмотреть модель.

---

# Workflow и обычные permissions

## 33. Workflow не отменяет Role Permission Manager

Допустим Transition говорит:

```text
Allowed: Request Manager
```

Это ещё не значит:

> любой пользователь с Request Manager теперь получает полный доступ к Request.

Обычные permissions DocType продолжают действовать.

Упрощённая логика:

```text
Role Permission
→ базовый доступ к Document

Workflow
→ какие действия и переходы допустимы в текущем состоянии
```

Не надо использовать Workflow как замену всей permission model.

---

## 34. `Allowed` у Transition и `Only Allow Edit For` у State — разные вещи

Например:

```text
State: Review
Only Allow Edit For: Request Manager
```

и переход:

```text
State: Review
Action: Escalate
Allowed: Senior Manager
```

Это две отдельные настройки.

Первая отвечает за редактирование документа в состоянии.

Вторая — за право выполнить конкретный переход.

---

# Workflow и Assignment

## 35. Workflow не назначает исполнителя автоматически

Схема:

```text
workflow_state = Review
```

не означает автоматически:

```text
assigned_to = manager
```

Workflow отвечает за:

```text
state + allowed transitions
```

Assignment отвечает за:

```text
кому конкретно нужно что-то сделать
```

Если нужно автоматическое назначение, для этого есть:

```text
Assignment Rule
```

или отдельная бизнес-логика.

---

## 36. Workflow Action и Assignment тоже не одно и то же

Похожи они только внешне: оба механизма могут означать «у пользователя есть ожидающее действие».

Но модели разные.

### Assignment

```text
ToDo
allocated_to = конкретный User
```

### Workflow Action

```text
ожидающее решение по Workflow
доступное подходящей Role
```

Не надо заменять одно другим без причины.

---

# Можно ли просто изменить `workflow_state` программно

## 37. Прямое изменение поля не является правильным Workflow transition

Плохая идея:

```python
doc.workflow_state = "Approved"
doc.save()
```

если этим пытаются обойти настоящий переход.

В текущем v16 серверная валидация проверяет изменение Workflow State и убеждается, что такой Transition действительно разрешён.

То есть Workflow — не только кнопки Desk.

Проверка существует на сервере.

---

## 38. Даже Data Import не должен перепрыгивать состояния

Текущий код v16 отдельно защищает от ситуации, когда новый документ пытаются сразу записать в произвольный Workflow State, минуя первый state и разрешённый transition.

Это правильный принцип:

```text
Workflow State
не должен становиться дырой для обхода Workflow
```

---

# Когда Workflow действительно нужен

## 39. Хорошие задачи для Workflow

Workflow хорошо подходит для правил вида:

```text
сотрудник создаёт
↓
руководитель проверяет
↓
директор согласует
```

или:

```text
Draft
↓ Send for Review
Review
├── Approve
└── Reject
```

или:

```text
обычный пользователь может сделать A
руководитель может сделать B
только при условии X
```

То есть когда важны **разрешённые переходы и роли**.

---

## 40. Когда обычного `status` достаточно

Если правило выглядит так:

```text
New
In Progress
Done
```

и любой пользователь с Write может свободно менять значение, Workflow может быть лишним.

Обычный:

```text
Select status
```

проще и прозрачнее.

Не нужно включать Workflow только потому, что у объекта есть несколько состояний.

---

## 41. Когда Workflow уже недостаточно

Workflow не должен превращаться в универсальный конструктор всего приложения.

Если процесс требует:

```text
сложных вычислений
массового создания связанных документов
длинных транзакций
сложной маршрутизации между командами
нетривиальных внешних интеграций
```

часть поведения уже разумнее вынести в:

```text
server-side application code
```

При этом сам Workflow может остаться верхним слоем управления переходами.

---

# Частые ошибки

## 42. Ошибка: сделать Workflow ради цветных статусов

Если нужно только:

```text
New
In Progress
Done
```

без ограниченных переходов и approval logic, начни с обычного поля.

---

## 43. Ошибка: дублировать `status` и `workflow_state` один в один

Плохо:

```text
status         = Review
workflow_state = Review
```

если оба поля обозначают абсолютно одно и то же.

Нужно выбрать один источник истины или чётко развести смысл двух осей.

---

## 44. Ошибка: считать Role в Transition полноценной permission model

```text
Allowed = Manager
```

не означает:

```text
Manager автоматически видит все документы
```

Права DocType настраиваются отдельно.

---

## 45. Ошибка: смешивать Assignment и Workflow

Workflow отвечает:

```text
какой переход можно выполнить?
```

Assignment отвечает:

```text
кто конкретно должен заняться документом?
```

Это связанные, но разные задачи.

---

## 46. Ошибка: писать огромные Conditions

Если Condition превращается в нечто вроде:

```text
20 строк логики
несколько запросов
сложные ветвления
```

это уже плохое место для бизнес-правила.

Сделай понятный серверный метод или controller validation.

---

## 47. Ошибка: запускать критичную операцию асинхронно

Если без операции переход не должен состояться, не делай её asynchronous Transition Task.

Иначе получится:

```text
Approved уже сохранён
↓
background task упал
```

а Workflow назад сам не откатится.

---

# Мини-практика

## 48. Практика 1. Подготовь состояния и действия

Создай Workflow States:

```text
New
Review
Approved
Rejected
```

Создай Workflow Actions:

```text
Send for Review
Approve
Reject
```

---

## 49. Практика 2. Создай простой Workflow

Для учебного `Request` создай Workflow:

```text
Workflow Name: Request Review
Document Type: Request
Is Active: Yes
Workflow State Field: workflow_state
```

Для первого опыта оставь все состояния:

```text
Doc Status = 0
```

---

## 50. Практика 3. Добавь States

Например:

```text
New       → Request User
Review    → Request Manager
Approved  → Request Manager
Rejected  → Request Manager
```

Если таких Roles ещё нет, создай учебные роли заранее.

---

## 51. Практика 4. Добавь Transitions

```text
New
Send for Review
Review
Request User
```

```text
Review
Approve
Approved
Request Manager
```

```text
Review
Reject
Rejected
Request Manager
```

---

## 52. Практика 5. Проверь двумя пользователями

Не тестируй всё Administrator.

Создай или используй двух учебных пользователей:

```text
user@example.com
→ Request User

manager@example.com
→ Request Manager
```

Проверь:

```text
user видит Send for Review
manager видит Approve / Reject
user не получает manager actions
```

---

## 53. Практика 6. Добавь Condition

На `Approve` добавь простое условие.

Например если у Request есть поле:

```text
amount
```

то:

```python
doc.amount > 0
```

Проверь документ с:

```text
amount = 0
```

и:

```text
amount = 100
```

Сравни доступные Actions.

---

## 54. Практика 7. Проверь Self Approval

Создай Request пользователем, у которого одновременно есть manager Role.

Сначала оставь:

```text
Allow Self Approval = Yes
```

Затем выключи.

Посмотри, сможет ли создатель сам выполнить Approval transition.

---

## 55. Практика 8. Только после этого добавь Submit

Если учебный `Request` сделан Submittable, поменяй:

```text
Approved → Doc Status 1
```

и добавь Cancelled State:

```text
Cancelled → Doc Status 2
```

Проверь, что переход в `Approved` теперь приводит к настоящему:

```text
docstatus = 1
```

а не только к красивому Workflow State.

---

# Что запомнить

## 56. Семь основных мыслей

### 1

Workflow — это не список статусов.

Это правила допустимых переходов.

### 2

```text
State + Action + Next State + Role + Condition
```

— основа одного Transition.

### 3

`workflow_state` и `docstatus` связаны, но это разные поля.

### 4

Переход в Workflow State с `Doc Status = 1` может вызвать настоящий Submit.

### 5

Workflow не заменяет Role Permission, Assignment и обычную серверную бизнес-логику.

### 6

`Workflow Action Master` — название команды, а `Workflow Action` — конкретное ожидающее решение по документу.

### 7

В v16 Transition Tasks позволяют запускать App action, Server Script или Webhook; synchronous task участвует в транзакции перехода, asynchronous — выполняется после commit.

---

# Источники

Официальная документация:

- Workflows: https://docs.frappe.io/erpnext/workflows
- Workflow State: https://docs.frappe.io/erpnext/workflow-state
- Workflow Actions: https://docs.frappe.io/erpnext/workflow-actions
- Workflow Transition Tasks: https://docs.frappe.io/erpnext/workflow-transition-tasks

Исходный код Frappe `version-16`:

- `frappe/model/workflow.py`
- `frappe/workflow/doctype/workflow/workflow.py`
- `frappe/workflow/doctype/workflow/workflow.json`
- `frappe/workflow/doctype/workflow_state/workflow_state.json`
- `frappe/workflow/doctype/workflow_document_state/workflow_document_state.json`
- `frappe/workflow/doctype/workflow_transition/workflow_transition.json`
- `frappe/workflow/doctype/workflow_action_master/workflow_action_master.json`
- `frappe/workflow/doctype/workflow_action/workflow_action.py`
- `frappe/workflow/doctype/workflow_transition_tasks/workflow_transition_tasks.json`
- `frappe/workflow/doctype/workflow_transition_task/workflow_transition_task.json`

---

Предыдущая глава: [25. Status против Workflow State](25_STATUS_VS_WORKFLOW_STATE.md)

Следующая глава: **27. Notification**
