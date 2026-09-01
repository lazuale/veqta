# L6. Совместная работа

L6 не добавляет новые предметные DocType и не добавляет поле исполнителя в `Service Request`.

Цель: организовать работу с уже существующими заявками штатными средствами Frappe — `Assign To`, `ToDo`, Comments, Timeline, Tags и Kanban.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

```text
Service Request
      │
      ├── Assign To ─────► ToDo ─────► Technician
      ├── Comments / Timeline
      ├── Tags
      └── Kanban по Status
```

Ключевое разделение:

```text
Permission
= может ли пользователь работать с документом

Assignment
= кому поручена конкретная работа

Status
= состояние самой заявки
```

После L5 основные Technician не имеют постоянного User Permission по Location. Временный Restricted Technician из L5 отключён и в L6 не используется.

---

# 1. Проверить состояние после L5

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

Должны существовать роли:

```text
Facility Requester
Facility Technician
Facility Supervisor
```

и основные пользователи:

```text
requester.one@example.com
requester.two@example.com
technician.one@example.com
supervisor.one@example.com
```

Проверить отдельно:

```text
technician.one@example.com
→ нет постоянного User Permission на Facility Location
```

Если такой User Permission остался после L5, удалить его до продолжения.

---

# 2. Выбрать заявку для назначения

Под `supervisor.one@example.com` открыть любую незакрытую `Service Request`, например:

```text
Status = New
```

Зафиксировать до назначения:

```text
Assigned To = пусто
Status = New
```

Location теперь не обязана быть `Room 101`: Technician имеет обычную область доступа, заданную Role Permission.

---

# 3. Назначить через Assign To

Использовать штатное действие:

```text
Assign To
```

Выбрать:

```text
technician.one@example.com
```

Описание:

```text
Проверить заявку и зафиксировать результат.
```

Если интерфейс предлагает Due Date, указать ближайшую будущую дату.

Не добавлять поле:

```text
Assigned Technician
```

в `Service Request`.

---

# 4. Проверить созданный ToDo

Через Awesomebar открыть `ToDo` и найти назначение.

Проверить:

```text
Allocated To   = technician.one@example.com
Reference Type = Service Request
Reference Name = выбранный SR-.....
Status         = Open
```

Главный вывод:

```text
Assign To
→ создаёт штатный ToDo
→ не записывает исполнителя в наше собственное поле
```

---

# 5. Проверить Status после Assign To

Вернуться в `Service Request`.

После обычного Assign To статус остаётся отдельным понятием.

Вручную изменить:

```text
New → Assigned
```

Сохранить.

Пока Workflow ещё не создан, `Status` остаётся обычным Select.

---

# 6. Проверить работу Technician

Войти как:

```text
technician.one@example.com
```

Открыть свою очередь / ToDo и перейти к назначенной заявке.

Проверить:

- заявка открывается;
- назначение видно;
- ToDo ссылается на нужный документ.

Изменить:

```text
Assigned → In Progress
```

Сохранить.

---

# 7. Comments и Timeline

В той же заявке добавить Comment:

```text
Проверка начата. Требуется дополнительный осмотр оборудования.
```

Проверить Timeline.

Различать:

```text
Timeline
= общий интерфейс истории активности

Track Changes / Version
= изменение полей Document

Comment
= пользовательская запись обсуждения

Assignment
= отдельная активность назначения
```

Не создавать собственные `Comment History` или `Work Note` DocType.

---

# 8. Закрыть ToDo и сравнить с Status

Завершить назначение штатным действием ToDo / Assignment.

Проверить:

```text
ToDo Status = Closed
```

При этом `Service Request` не обязан автоматически стать `Closed`.

Если заявка всё ещё `In Progress`, вручную перевести:

```text
In Progress → Resolved
```

Сохранить.

Фиксируем:

```text
закрыть ToDo
≠ закрыть Service Request
```

---

# 9. Повторное назначение

Под Supervisor взять другую незакрытую заявку и назначить её тому же Technician.

Проверить, что у пользователя существуют отдельные ToDo для разных:

```text
reference_name
```

Один Technician может иметь много заданий.

---

# 10. Дублирующее назначение

На уже назначенной заявке попробовать снова назначить того же пользователя, пока первое назначение активно.

На фактическом стенде зафиксировать штатное поведение Frappe.

Не писать обходной код и не создавать собственный assignment registry.

---

# 11. Tags

Добавить к нескольким Service Request лёгкие дополнительные метки, например:

```text
hvac
urgent-check
network
```

Не дублировать Tags уже существующие структурированные данные:

```text
Priority
Status
Location
Equipment
```

То есть не использовать `High`, `New`, `Room 101` как теги только ради копирования значений полей.

Проверить фильтрацию по одному Tag.

---

# 12. Создать Kanban

Открыть `Service Request` List View → `Kanban` → создать доску:

```text
Board Name: Service Request Status Board
Reference DocType: Service Request
Field: Status
```

Колонки:

```text
New
Assigned
In Progress
Resolved
Closed
```

Название специально отличается от Dashboard Chart, который появится позже в L8.

---

# 13. Kanban — представление тех же Documents

Сравнить одну заявку:

```text
List View
Form View
Kanban
```

Во всех трёх местах это один и тот же `Service Request`.

Переместить карточку:

```text
Assigned → In Progress
```

Открыть Form View и проверить:

```text
Status = In Progress
```

В `v16.32.0` перенос карточки меняет значение поля, выбранного как field доски.

---

# 14. Проверить permissions через Kanban

Войти под Requester.

Он должен видеть только свои `Service Request`, потому что L5 использует `If Owner`.

Kanban не создаёт отдельную систему прав:

```text
List / Form / Kanban
→ работают над теми же Documents
→ подчиняются тем же permissions
```

Затем под Technician проверить обычный доступ к заявкам независимо от Location. Если Technician внезапно видит только одно помещение, значит после L5 остался лишний User Permission — исправить состояние стенда, а не подстраивать L6.

---

# 15. Не смешивать Assignment и Kanban

На одной заявке проверить ситуацию:

```text
Assigned To = technician.one@example.com
Status = In Progress
```

Это нормально.

Kanban отвечает на вопрос:

```text
в каком состоянии заявка
```

Assign To отвечает:

```text
кому поручена работа
```

---

# 16. Проверить Git

L6 работает только с site data / штатными служебными Documents:

```text
ToDo
Comment
Tag
Kanban Board
```

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status
```

Если Standard metadata приложения не менялась, working tree должен оставаться чистым.

Kanban Board в этом курсе рассматриваем как site configuration учебного стенда и не экспортируем вручную.

---

# 17. Приёмка L6

L6 принят, если ученик может показать:

- назначение через `Assign To`;
- соответствующий `ToDo`;
- отдельность Assignment и Status;
- Comment и Timeline;
- Tags без дублирования полей;
- Kanban `Service Request Status Board`;
- drag меняет Status того же Service Request;
- permissions одинаково действуют в List/Form/Kanban;
- `technician.one@example.com` не ограничен постоянным Location User Permission;
- Git не содержит рабочих ToDo/Comments/Tags.

Ученик без подсказки объясняет:

1. почему не нужно поле `Assigned Technician`;
2. чем ToDo отличается от Service Request;
3. почему закрытие ToDo не закрывает заявку;
4. чем Tag отличается от Select/Link;
5. почему Kanban не является отдельной базой задач.

После L6 переходим к **L7 — Workflow**. Kanban пока оставляем для сравнения, а в L7 после проверки удалим, чтобы процесс управлялся одним понятным способом — Workflow Actions.