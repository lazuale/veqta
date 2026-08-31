# 23. Assignment и ToDo

Блок D отвечал на вопрос:

```text
кто имеет доступ к Request?
```

Теперь начинается работа с процессом. Первый вопрос другой:

```text
кто должен заняться конкретным Request?
```

Во Frappe для этого есть штатное действие **Assign**. Оно не меняет `owner` и не записывает исполнителя в наше поле `Responsible`. Вместо этого Framework создаёт отдельный системный Document типа `ToDo`.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

После блока D у нас есть два реальных System User:

```text
student.user@example.test
student.manager@example.test
```

и рабочая permission model `Request`.

Обычный User ограничен:

```text
Training Area = North
```

Менеджер такого ограничения не имеет.

Sharing включён:

```text
Disable Document Sharing = ☐
```

Assignment до этой главы ещё не был частью обязательного состояния курса.

---

# 1. Assignment — это связь с отдельным ToDo

Представим сохранённый Request:

```text
Subject: E23-Assignment-Manual
```

Менеджер открывает его и назначает:

```text
student.user@example.test
```

Framework создаёт `ToDo` примерно с такими значениями:

```text
Allocated To:    student.user@example.test
Reference Type:  Request
Reference Name:  <system name Request>
Status:          Open
Priority:        Medium
Assigned By:     student.manager@example.test
```

Связь выглядит так:

```text
Request
   │
   └── ToDo
       ├── allocated_to
       ├── reference_type
       ├── reference_name
       └── status
```

Поэтому Assignment — не декоративная метка формы. За ним остаётся отдельная запись данных.

---

# 2. Почему это не поле `Responsible`

У нашего `Request` уже есть:

```text
Responsible
fieldname: responsible
Link → User
```

Это обычное поле нашей модели данных.

Если записать в него:

```text
student.manager@example.test
```

Framework сохранит Link на User, но сам по себе не создаст `ToDo`.

Сравнение:

| Механизм | Что хранит |
|---|---|
| `Responsible` | значение внутри `Request` |
| Assignment | отдельный `ToDo`, связанный с `Request` |

Поле может понадобиться, если у бизнеса есть отдельное понятие вроде «ответственный», «координатор» или «владелец процесса». Но оно не заменяет штатный механизм Assign.

---

# 3. Один документ может иметь несколько Assignment

Один `Request` можно назначить нескольким пользователям.

Тогда Framework создаёт несколько `ToDo`:

```text
Request
├── ToDo → student.user@example.test
└── ToDo → student.manager@example.test
```

У каждого ToDo собственные:

```text
Allocated To
Status
Priority
Due Date
```

Поэтому модель не ограничена одним исполнителем.

---

# 4. Какие поля ToDo важны в первом проходе

В `v16.32.0` системный DocType `ToDo` имеет, среди прочего:

```text
Status
  Open / Closed / Cancelled

Priority
  High / Medium / Low

Due Date
  fieldname: date

Allocated To
  Link → User

Description
  обязательное поле

Reference Type
  Link → DocType

Reference Name
  Dynamic Link

Assigned By
  Link → User

Assignment Rule
  ссылка на правило автоматического назначения
```

Для нашей лабораторной главные четыре поля:

```text
allocated_to
reference_type
reference_name
status
```

По ним легко доказать, какой пользователь назначен на какой Document.

---

# 5. Почему сначала нужно сохранить Request

Assignment должен ссылаться на конкретный Document.

Для этого нужны:

```text
reference_type = Request
reference_name = <name>
```

У нового несохранённого Request ещё нет окончательного `name`.

Поэтому практическая последовательность такая:

```text
создать Request
→ Save
→ Assign
```

---

# 6. Что делает окно Assign

В штатном диалоге Assign можно указать:

```text
Assign To
Complete By
Priority
Comment
```

Для лабораторной мы зададим все основные значения явно, чтобы результат можно было проверить в ToDo.

Назначаемый пользователь должен быть активным System User. Наши два учебных User этому условию соответствуют.

---

# 7. Open, Closed и Cancelled

После обычного назначения ToDo создаётся как:

```text
Status = Open
```

Дальше Assignment может закончиться двумя разными способами.

### Complete

Работа выполнена:

```text
Open → Closed
```

### Remove / Unassign

Назначение снято:

```text
Open → Cancelled
```

История при этом не обязана исчезать. Мы меняем состояние связанного ToDo.

---

# 8. Дубликат одного и того же Open Assignment не создаётся

Backend v16 перед созданием проверяет комбинацию:

```text
Reference Type
Reference Name
Allocated To
Status = Open
```

Если такой Open ToDo уже существует, второй такой же Open Assignment для того же User и документа не создаётся.

Это не мешает назначить тот же документ другому пользователю.

---

# 9. Assignment не меняет owner

Например:

```text
owner = student.manager@example.test
```

После назначения обычному User:

```text
owner = student.manager@example.test
Allocated To = student.user@example.test
```

`owner` продолжает означать создателя Document.

Assignment отвечает только за текущую работу.

Поэтому:

```text
owner
Responsible
Assignment
```

— три разных понятия.

---

# 10. Assignment и Sharing

Assignment и Sharing тоже не одно и то же:

```text
Assignment
→ кому поручена работа

Sharing
→ кому явно дан доступ к Document
```

Но Frappe умеет связать эти механизмы.

Если выбранный assignee не имеет Read на документ, а document sharing разрешён, стандартный Assign может автоматически выдать ему Read Share.

Если же включено:

```text
Disable Document Sharing = ✓
```

и assignee не имеет обычного доступа, Assignment завершается ошибкой `Missing Permission`.

Эту границу мы специально проверим в следующей главе на автоматическом Assignment Rule.

---

# 11. Assignment создаёт системное уведомление

При назначении другому активному User Framework создаёт уведомление типа:

```text
Assignment
```

То есть для простого сценария «тебе назначили документ» не нужно сразу создавать собственный Notification rule.

Общий механизм Notification будем изучать отдельно в главе 27.

---

# 12. Где смотреть результат

У Assignment есть два удобных представления.

### На исходном Request

В Form View видны активные назначения.

### В системном ToDo

Можно открыть:

```text
http://learn.localhost:8000/app/todo
```

и отфильтровать по:

```text
Reference Type = Request
Reference Name = <name>
```

Именно этот второй путь позволяет увидеть серверную запись, стоящую за кнопкой Assign.

---

# 13. Что мы сделаем в лабораторной

На отдельном Request:

```text
E23-Assignment-Manual
```

мы:

1. создадим ручной Assignment на `student.user@example.test`;
2. найдём связанный ToDo;
3. временно добавим второй Assignment на менеджера;
4. снимем только второй Assignment;
5. изменим обычное поле `Responsible` и убедимся, что новый ToDo не появился;
6. вернём `Responsible` в исходное состояние;
7. оставим ровно один активный Assignment на обычного User.

Так следующий блок будет продолжаться с реальным рабочим назначением, а не с абстрактной схемой.

---

## Что запомнить

1. `Assign` создаёт отдельный `ToDo`.
2. `Responsible` — обычный Link и не является Assignment.
3. `owner` не меняется из-за назначения.
4. Один Request может иметь несколько ToDo для разных Users.
5. Open Assignment можно завершить или снять.
6. Assignment может использовать Sharing, если assignee не имеет обычного доступа.
7. Для проверки Assignment полезно смотреть и Form View, и системный `ToDo`.

Теперь выполни [**лабораторную 23**](labs/23_ASSIGNMENT_AND_TODO_LAB.md).