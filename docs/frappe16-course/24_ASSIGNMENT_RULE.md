# 24. Assignment Rule

В главе 23 пользователь выбирал assignee вручную через `Assign`.

Теперь автоматизируем тот же механизм штатным `Assignment Rule`.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть

Есть два System User:

```text
student.user@example.test
student.manager@example.test
```

и ручной Assignment на `E23-Assignment-Manual`.

Assignment Rule пока не создан.

---

# 1. Что делает Assignment Rule

Правило не создаёт новую систему задач.

Оно решает:

```text
подходит ли Document
→ кому назначить
→ создать обычный ToDo
```

После автоматического назначения результат тот же, что после ручного Assign:

```text
ToDo
  allocated_to
  reference_type
  reference_name
  status
  assignment_rule
```

---

# 2. Наше правило

В лабораторной создадим:

```text
Training Request Round Robin
```

для:

```text
Document Type = Request
```

с условием:

```python
status == "Open"
```

и стратегией:

```text
Round Robin
```

Порядок Users будет фиксирован:

```text
1. student.user@example.test
2. student.manager@example.test
```

По исходному коду v16 Round Robin хранит `last_user` и выбирает следующего пользователя в этом списке.

При пустом `last_user` первый подходящий Request получит первый User.

Поэтому последовательность для четырёх новых документов детерминирована:

```text
E24-RR-1 → student.user@example.test
E24-RR-2 → student.manager@example.test
E24-RR-3 → student.user@example.test
E24-RR-4 → student.manager@example.test
```

---

# 3. Assign Condition

Поле `Assign Condition` принимает простое Python-выражение.

Для нашего Request достаточно:

```python
status == "Open"
```

Это не отдельный скрипт и не программа из нескольких строк.

Если Request имеет:

```text
Status = Done
```

правило не создаёт Assignment.

---

# 4. Assignment Days

В v16 таблица `Assignment Days` обязательна.

В форме есть готовая кнопка:

```text
All Days
```

Она заполняет:

```text
Monday
Tuesday
Wednesday
Thursday
Friday
Saturday
Sunday
```

В лабораторной используем именно её, чтобы результат не зависел от дня недели.

---

# 5. Round Robin

Алгоритм v16 прост:

```text
last_user пуст
→ первый User

последним был первый
→ второй User

последним был второй и он последний в списке
→ снова первый User
```

Поэтому здесь не нужно гадать, кого выберет Framework.

---

# 6. Другие стратегии

В v16 доступны ещё:

```text
Load Balancing
Based on Field
Weighted Distribution
```

Их полезно знать, но в обязательной лабораторной мы не смешиваем несколько алгоритмов.

### Load Balancing

Выбирает User с наименьшим числом Open ToDo для этого `Document Type`.

### Based on Field

Берёт пользователя из выбранного поля документа, например из `responsible`.

### Weighted Distribution

Распределяет задания по относительным весам.

Для первого воспроизводимого опыта достаточно Round Robin.

---

# 7. Assignment Rule не заменяет permissions

Правило отвечает:

```text
кому назначить работу
```

Permissions отвечают:

```text
может ли User открыть Document
```

В обычном Assign v16 умеет автоматически сделать Read Share, если assignee не имеет обычного доступа и Sharing разрешён.

Assignment Rule использует тот же backend назначения.

Поэтому при разрешённом Sharing отсутствие обычного Read не обязательно приводит к отказу: Framework может создать Share.

---

# 8. Как получить гарантированный permission failure

После четырёх Round Robin назначений `last_user` будет:

```text
student.manager@example.test
```

Значит следующий подходящий Request должен достаться:

```text
student.user@example.test
```

Мы временно включим:

```text
Disable Document Sharing = ✓
```

и попробуем создать:

```text
Area = South
Status = Open
```

Обычный User ограничен `Training Area = North`, а автоматический Share запрещён.

Backend v16 в этой комбинации выдаёт:

```text
Missing Permission
```

с объяснением, что document sharing отключён и сначала нужно выдать необходимые permissions.

Это гарантированная поломка, а не эксперимент «посмотрим, что случится».

После неё Sharing сразу возвращаем в исходное состояние.

---

# 9. Почему правило отключим после лабораторной

Активный Assignment Rule проверяется при сохранении подходящих документов.

В следующих главах мы будем много сохранять `Request`, настраивая Workflow и Notification.

Чтобы автоматическое назначение не меняло картину незаметно, после проверки оставим правило существовать, но установим:

```text
Disabled = ✓
```

Так ученик сможет открыть готовую настройку позже, но она не будет вмешиваться в следующие опыты.

---

## Что запомнить

1. Assignment Rule автоматизирует обычный Assignment и создаёт ToDo.
2. `Assign Condition` определяет, подходит ли Document.
3. Round Robin в нашем опыте даёт точный порядок 1 → 2 → 1 → 2.
4. Assignment Days определяют, в какие дни правило применяется.
5. Assignment Rule не заменяет permissions.
6. Sharing может дать assignee Read на конкретный документ.
7. Если Sharing отключён и assignee не имеет доступа, назначение получает `Missing Permission`.
8. После учебного опыта правило лучше Disabled, чтобы оно не влияло на следующие главы.

Теперь выполни [**лабораторную 24**](labs/24_ASSIGNMENT_RULE_LAB.md).