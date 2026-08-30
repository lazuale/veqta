# 23. Assignment и ToDo

В прошлых главах мы разбирали доступ: кто может открыть документ, изменить его или получить исключение через Sharing.

Теперь начинается другая тема:

> кто должен что-то сделать с документом?

Во Frappe для этого уже есть штатный механизм **Assignment**.

И под ним работает системный DocType:

```text
ToDo
```

Проверено: **2026-08-31**.

---

## 1. Самая простая картина

Есть документ:

```text
Request REQ-0001
```

Его создала Анна, но проверить заявку должен Борис.

На форме Анна нажимает:

```text
Assign
```

и выбирает:

```text
boris@example.com
```

После этого не происходит магического добавления поля в `Request`.

Frappe создаёт отдельный `ToDo`, связанный с этим документом:

```text
ToDo
├── allocated_to   = boris@example.com
├── reference_type = Request
├── reference_name = REQ-0001
├── status         = Open
├── priority       = Medium
└── assigned_by    = anna@example.com
```

Удобно запомнить так:

```text
Document
   ↓ Assign
ToDo
   ↓
конкретному User нужно что-то сделать
```

---

## 2. Assignment — не поле `assigned_to`

Для обычной работы Frappe не требует добавлять в каждый DocType поле:

```text
assigned_to
```

Штатное назначение строится вокруг отдельного `ToDo`.

Например:

```text
Request REQ-0001
   │
   ├── ToDo → Boris
   └── ToDo → Anna
```

У одного документа поэтому может быть больше одного активного назначения.

Если бы мы сделали одно обычное поле:

```text
assigned_to = User
```

оно смогло бы хранить только одного пользователя.

`ToDo` такой проблемы не имеет.

---

## 3. Где пользователь видит Assignment

В стандартном Form View назначения находятся в sidebar формы вместе с другими штатными механизмами документа.

Упрощённо:

```text
Request REQ-0001

[поля документа]

Sidebar
├── Assignments
├── Attachments
├── Sharing
└── Tags
```

То есть для обычного внутреннего DocType не нужно рисовать свой блок исполнителей.

Framework уже умеет показать активные назначения и дать действия над ними.

---

## 4. Сначала документ нужно сохранить

Новый ещё не сохранённый Document назначить нельзя.

Логика понятна: чтобы создать связанный `ToDo`, Frappe уже должен знать точный адрес документа:

```text
reference_type = Request
reference_name = REQ-0001
```

Поэтому последовательность такая:

```text
New Request
↓
Save
↓
у документа появился name
↓
Assign
```

В текущем интерфейсе v16 попытка назначить несохранённый документ останавливается сообщением о необходимости сначала сохранить его.

---

## 5. Что есть в окне Assign

Стандартный диалог назначения в v16 позволяет выбрать:

```text
Assign To
Complete By
Priority
Comment
```

Также есть:

```text
Assign to me
Assign To User Group
```

`Assign To` поддерживает несколько пользователей.

Например:

```text
Assign To:
- anna@example.com
- boris@example.com
```

Для каждого пользователя создаётся своё назначение.

---

## 6. Назначаются именно активные System Users

Стандартный Assign dialog ищет пользователей с условиями:

```text
User Type = System User
Enabled = 1
```

То есть механизм ориентирован на пользователей Desk, которые реально работают внутри системы.

Это ещё одна причина не превращать Assignment в универсальное поле для любых внешних контактов.

---

# ToDo

## 7. Что такое `ToDo`

`ToDo` — обычный системный DocType Frappe для небольших рабочих задач.

В v16 у него есть основные поля:

| Поле | Смысл |
|---|---|
| `status` | Open / Closed / Cancelled |
| `priority` | High / Medium / Low |
| `date` | Due Date |
| `description` | что нужно сделать |
| `allocated_to` | кому назначено |
| `assigned_by` | кто назначил |
| `reference_type` | тип связанного документа |
| `reference_name` | конкретный связанный документ |
| `assignment_rule` | правило, если назначение создано автоматикой |

`description` обязательна.

По умолчанию:

```text
status   = Open
priority = Medium
```

---

## 8. ToDo может существовать без другого документа

`ToDo` не обязан быть Assignment для `Request`, `Order` или другого DocType.

Можно создать обычный самостоятельный ToDo:

```text
Позвонить поставщику
```

без:

```text
reference_type
reference_name
```

То есть есть два нормальных сценария.

### Самостоятельный ToDo

```text
ToDo
└── Проверить резервную копию
```

### Assignment на Document

```text
Request REQ-0001
        ↓
      ToDo
        ↓
      Boris
```

Не нужно смешивать их в одну концепцию.

---

## 9. Как ToDo связывается с любым Document

Для этого используется знакомая пара:

```text
reference_type
reference_name
```

`reference_type` — Link на `DocType`.

`reference_name` — Dynamic Link, который использует значение `reference_type`.

Например:

```text
reference_type = Request
reference_name = REQ-0001
```

или:

```text
reference_type = Order
reference_name = ORD-0032
```

Поэтому Framework не нужен отдельный тип назначения для каждого бизнес-DocType.

---

## 10. Что именно делает стандартный Assign

Если очень упростить текущий backend v16:

```text
пользователь нажал Assign
        ↓
проверка доступа к исходному Document
        ↓
для каждого выбранного User
        ↓
создать Open ToDo
        ↓
записать reference_type / reference_name
        ↓
обновить список активных назначений документа
        ↓
создать notification
```

То есть Assignment — не декоративная отметка формы.

За ним стоят реальные записи `ToDo`.

---

## 11. Одному пользователю не создаётся второй такой же Open Assignment

Допустим, уже существует:

```text
Request REQ-0001
→ Boris
→ Open
```

Если снова назначить тот же документ Борису, стандартный backend проверяет существующий `ToDo` по комбинации:

```text
reference_type
reference_name
allocated_to
status = Open
```

И второй одинаковый Open ToDo не создаётся.

Это защищает обычный интерфейс от случайного удвоения одного и того же назначения.

---

## 12. Что такое `_assign`

Кроме самих `ToDo`, Framework поддерживает в документе специальное служебное поле:

```text
_assign
```

В модели Frappe оно относится к optional system fields и имеет смысл:

```text
Assigned To
```

Когда назначения меняются, контроллер `ToDo` собирает активных пользователей и синхронизирует `_assign` у связанного документа.

Условно:

```text
REQ-0001
_assign = [
    "anna@example.com",
    "boris@example.com"
]
```

Это служебное представление текущих назначений.

Источником отдельных assignment-записей всё равно остаются связанные `ToDo`.

---

## 13. Почему не стоит создавать своё поле `_assign`

Не нужно добавлять `_assign` в DocType вручную.

Это имя уже используется самим Framework как служебное поле.

Так же как не нужно заново моделировать:

```text
owner
creation
modified
```

не нужно строить собственную бизнес-логику вокруг ручного заполнения `_assign`.

Framework синхронизирует его сам.

---

## 14. А что с полем `assigned_to`?

Здесь есть важная деталь именно текущего v16.

Если в исходном DocType уже существует поле с точным fieldname:

```text
assigned_to
```

стандартный backend Assignment дополнительно записывает туда назначаемого пользователя.

А при закрытии или отмене назначения очищает это поле.

Это не меняет основную архитектуру:

```text
Assignment → ToDo
```

и не делает `assigned_to` обязательным полем Framework.

Более того, для нескольких одновременно назначенных пользователей одно такое поле принципиально не может полноценно представить состояние.

Поэтому создавать `assigned_to` только ради того, чтобы «Assignment заработал», не нужно.

Если приложению действительно нужен отдельный бизнес-смысл вроде:

```text
Primary Responsible
Case Owner
Coordinator
```

лучше так его и назвать и определить его правила отдельно.

---

## 15. Assignment и `owner` — разные вещи

Вернёмся к примеру:

```text
Request REQ-0001
owner = anna@example.com
```

Анна назначила документ Борису.

После Assign:

```text
owner       = anna@example.com
assigned    = boris@example.com
```

`owner` не меняется.

Потому что вопросы разные:

```text
owner
→ кто создал Document

Assignment
→ кто должен выполнить работу
```

Поэтому `Only if Creator` не начинает считать Бориса owner только потому, что заявка ему назначена.

---

## 16. Assignment и Sharing — тоже разные механизмы

Концептуально:

```text
Assignment
→ рабочая ответственность

Sharing
→ доступ к документу
```

Но в стандартном Assign между ними есть полезная связка.

Представим:

```text
Boris не имеет Read на REQ-0001
```

Анна пытается назначить ему этот документ.

Если обычный Document Sharing разрешён, v16 автоматически делает Boris Share с `Read`, чтобы назначенный пользователь вообще смог открыть документ.

Упрощённо:

```text
Assign Boris
↓
Boris пока не может Read
↓
автоматический Share
↓
Boris получает Read на этот Document
```

То есть Assignment и Sharing остаются разными механизмами, но стандартный Assign умеет использовать Sharing как вспомогательный шаг.

---

## 17. Что если Sharing отключён

В `System Settings` можно включить:

```text
Disable Document Sharing
```

Тогда ситуация:

```text
назначаемый пользователь
не имеет доступа к документу
+
Sharing отключён
```

не обходится молча.

Стандартный backend v16 выдаёт ошибку `Missing Permission` и требует сначала дать пользователю необходимые права.

Это хорошее поведение: Assignment не должен превращаться в скрытый обход централизованной security model.

---

## 18. Assignment создаёт уведомление

При обычном назначении Framework формирует Notification Log типа:

```text
Assignment
```

для назначенного пользователя.

Уведомление связывается с исходным документом.

То есть для базового сценария:

```text
Анна назначила Request Борису
```

не нужно писать свою систему оповещений только ради факта назначения.

В отдельной главе 27 разберём более общий механизм `Notification`.

---

## 19. Assignment попадает в Timeline исходного документа

Когда связанный `ToDo` создаётся или его assignment-запись меняет состояние, controller добавляет комментарий в связанный Document.

Например, в Timeline можно получить событие о назначении пользователя или завершении назначения.

Это ещё одна причина использовать штатный механизм вместо поля:

```text
assigned_to
```

Простое поле само по себе не даёт:

```text
историю назначения
ToDo
уведомление
срок
priority
completion
```

---

## 20. `Open`, `Closed` и `Cancelled`

У `ToDo` в v16 три состояния:

```text
Open
Closed
Cancelled
```

Для Assignment удобно понимать их так.

### Open

Назначение активно.

```text
Boris ещё должен выполнить работу
```

### Closed

Назначение выполнено.

В стандартном sidebar кнопка `Done` относится именно к назначению текущего пользователя.

Backend отдельно проверяет, что завершить assignment через этот путь может сам assignee.

### Cancelled

Назначение снято.

Например:

```text
Boris больше не должен выполнять эту работу
```

Это отличается от выполненного задания.

---

## 21. Done на Assignment не закрывает бизнес-документ

Это очень важная граница.

Допустим:

```text
Request.status = In Progress
```

Борис завершил свой ToDo:

```text
ToDo.status = Closed
```

Это **не означает автоматически**:

```text
Request.status = Closed
```

Assignment отвечает за рабочее поручение.

Бизнес-состояние `Request` — отдельная модель.

Если приложение требует:

> когда последний исполнитель завершил Assignment, перевести Request в Done

это уже дополнительное бизнес-правило, которое нужно проектировать отдельно.

---

## 22. Cancel Assignment тоже не равен Cancel Document

Точно так же:

```text
ToDo.status = Cancelled
```

и:

```text
docstatus = 2
```

вообще не одно и то же.

Первое означает:

```text
рабочее назначение сняли
```

Второе относится к lifecycle Submittable Document:

```text
Submitted → Cancelled
```

Не смешивай эти два `Cancel` только потому, что слово одинаковое.

---

## 23. Несколько исполнителей

Стандартный Assign dialog поддерживает выбор нескольких пользователей.

Например:

```text
REQ-0001
├── Anna  → Open ToDo
├── Boris → Open ToDo
└── Carol → Open ToDo
```

Каждый Assignment живёт отдельно.

Поэтому Boris может завершить свой ToDo, пока у Anna и Carol назначения остаются активными.

Это значительно гибче, чем:

```text
assigned_to = Boris
```

---

## 24. User Group в Assign dialog

В v16 можно выбрать:

```text
Assign To User Group
```

Интерфейс получает участников `User Group` и подставляет их в список назначаемых пользователей.

Важно понимать механику:

```text
User Group
↓
разворачивается в Users
↓
создаются обычные назначения пользователям
```

Это не один абстрактный ToDo, владельцем которого является группа.

---

## 25. Due Date и Priority относятся к ToDo

В Assign dialog можно указать:

```text
Complete By
Priority
```

Эти значения записываются в Assignment `ToDo`:

```text
date
priority
```

Они не обязаны совпадать с бизнес-полями исходного Document.

Например:

```text
Request.due_date = 2026-09-10

Assignment ToDo.date = 2026-09-05
```

Это может быть абсолютно нормальной моделью:

```text
весь Request должен завершиться 10 сентября,
а конкретная проверка Бориса — 5 сентября
```

---

## 26. Priority исходного документа и Assignment Priority — не одно поле

Текущий Assign dialog v16 делает удобную вещь: если у исходного документа есть `priority` со значением:

```text
Low
Medium
High
```

оно может использоваться как начальное значение Priority в диалоге.

Но после создания это всё равно `ToDo.priority`.

Не стоит считать два поля автоматически синхронизированными навсегда.

---

## 27. Кто видит ToDo

У `ToDo` есть собственная permission-логика.

В обычной ситуации пользователь видит ToDo, если он связан с записью как один из участников:

```text
allocated_to
assigned_by
owner
```

Либо пользователь имеет дополнительную подходящую роль с доступом к `ToDo`.

То есть список ToDo не должен автоматически превращаться для каждого пользователя в глобальный список всех чужих поручений.

---

## 28. Assignment не заменяет бизнес-сущность

`ToDo` хорош для вопроса:

> кому нужно выполнить действие?

Но не нужно пытаться хранить в нём всю предметную область.

Например, если бизнес-объект должен иметь:

```text
номер
категорию
контрагента
стоимость
этап процесса
проверки
документы
историю предметных изменений
```

это нормальный отдельный DocType.

А Assignment лишь добавляет к нему:

```text
кто сейчас должен что-то сделать
```

Правильная композиция:

```text
Business Document
      +
Assignment / ToDo
```

а не:

```text
всё превратить в ToDo
```

---

## 29. Когда отдельное поле ответственного всё-таки нужно

Иногда в самой предметной модели действительно существует один устойчивый владелец.

Например:

```text
Account Manager
Case Owner
Coordinator
```

Тогда отдельный Link на `User` или другую сущность может быть оправдан.

Но вопрос надо задавать так:

> это реальное свойство бизнес-объекта или я просто пытаюсь повторить Assignment?

Если задача только:

```text
назначить работу
показать исполнителю
дать срок
уведомить
завершить поручение
```

сначала используй штатный Assignment.

---

## 30. Assignment Rule — следующий уровень

До сих пор мы назначали пользователя руками:

```text
открыли Document
↓
Assign
↓
выбрали Boris
```

Но Frappe умеет автоматизировать этот шаг.

Например:

```text
новый Request
↓
условие подходит
↓
Framework сам выбирает исполнителя
↓
создаётся Assignment
```

Для этого существует:

```text
Assignment Rule
```

Его разберём в следующей главе.

---

# Мини-практика

Возьми учебный DocType:

```text
Request
```

Создай два System User:

```text
anna@example.com
boris@example.com
```

Затем выполни по порядку.

### Шаг 1

Создай и сохрани:

```text
Request REQ-0001
```

### Шаг 2

В sidebar нажми Assign и назначь:

```text
boris@example.com
```

Укажи:

```text
Complete By = через несколько дней
Priority    = High
Comment     = Проверить данные заявки
```

### Шаг 3

Открой список `ToDo` под пользователем Boris.

Найди созданное назначение и посмотри:

```text
allocated_to
assigned_by
reference_type
reference_name
status
priority
date
```

### Шаг 4

Вернись в `REQ-0001` и проверь:

```text
Assignments в sidebar
Timeline
```

### Шаг 5

Заверши Assignment под Boris через `Done`.

Проверь, что:

```text
ToDo → Closed
```

но бизнес-поле `Request.status`, если оно есть, само по себе не обязано измениться.

### Шаг 6

Назначь `REQ-0001` одновременно двум пользователям и убедись, что это два отдельных назначения, а не одно поле с одним значением.

---

# Что запомнить

1. **Assignment во Frappe строится на `ToDo`.**
2. **У Assignment есть исполнитель, срок, priority, описание и ссылка на исходный Document.**
3. **Один Document может иметь несколько активных назначений.**
4. **`owner` и Assignment — разные вещи.**
5. **Assignment и Sharing — разные механизмы, хотя стандартный Assign может автоматически Share документ пользователю без доступа.**
6. **`_assign` — служебное поле Framework с текущими назначениями; не нужно моделировать его вручную.**
7. **Поле `assigned_to` не требуется для стандартного Assignment и плохо представляет несколько исполнителей.**
8. **Closed ToDo не означает автоматически Closed бизнес-документ.**
9. **Cancelled Assignment не равен Cancelled Submittable Document.**
10. **Сначала используй штатный Assignment, а отдельного «ответственного» добавляй только если это действительно свойство предметной модели.**

---

## Официальные источники

- [Assignments and Todos](https://docs.frappe.io/framework/assignments-and-todos)
- [Form Scripts / Form API](https://docs.frappe.io/framework/user/en/api/form)
- [ToDo controller — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/todo/todo.py)
- [ToDo metadata — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/todo/todo.json)
- [Assignment backend — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/assign_to.py)
- [Assignment UI — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [Model optional fields — `version-16`](https://github.com/frappe/frappe/blob/version-16/frappe/model/__init__.py)

---

← [22. Где заканчиваются штатные permissions](22_PERMISSION_BOUNDARIES.md)

→ **24. Assignment Rule**
