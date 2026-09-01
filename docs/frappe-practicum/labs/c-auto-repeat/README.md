# Lab C. Auto Repeat

Lab C — отдельная лаборатория по штатному созданию повторяющихся Documents.

Новых постоянных предметных DocType не создаём.

Для эксперимента используем уже существующий:

```text
Service Request
```

и временно разрешаем для него штатный механизм:

```text
Allow Auto Repeat
```

После лаборатории Auto Repeat удаляется, настройка отключается, служебный Custom Field очищается, а ядро приложения снова остаётся прежним.

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Что изучаем

В лаборатории нужны только штатные механизмы Frappe:

```text
Allow Auto Repeat
Auto Repeat
Reference Document
Frequency
Start Date
End Date
Next Schedule Date
Assignee
Assign To / ToDo
scheduler
background job
```

Главная идея:

```text
исходный Document
      ↓
Auto Repeat
      ↓
scheduler
      ↓
новый Document-копия
      ↓
Assign To / ToDo
```

Auto Repeat не является Workflow и не является Assignment Rule.

---

# 2. Проверить стенд

В терминале:

```bash
cd ~/frappe/facility-ops-bench

bench version
bench --site facility-ops.localhost list-apps
bench --site facility-ops.localhost scheduler status
bench --site facility-ops.localhost doctor

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
scheduler активен
workers доступны
```

Во время практики `bench start` должен быть запущен в отдельном терминале.

---

# 3. Зафиксировать границу механизма

Auto Repeat нужен, когда новый Document должен появляться по расписанию на основе существующего Document.

Например:

```text
ежедневный осмотр
еженедельная проверка
ежемесячное обслуживание
```

Для лаборатории используем сценарий:

```text
Periodic inspection
→ новый Service Request каждый день
```

Не создаём:

```text
Maintenance Schedule
Recurring Request
Inspection Plan
Schedule Item
```

Сейчас задача — изучить именно штатный `Auto Repeat`.

---

# 4. Временно отключить Assignment Rule L9

На основном учебном site уже может работать:

```text
Service Request Auto Assignment
```

Для чистого эксперимента временно открыть `Assignment Rule` и установить:

```text
Disabled = Yes
```

Почему:

```text
Auto Repeat Assignee
и
Assignment Rule
```

оба могут создавать назначения.

В этой лаборатории нужно увидеть действие только Auto Repeat.

После лаборатории Assignment Rule вернём обратно.

---

# 5. Разрешить Auto Repeat для Service Request

Войти как:

```text
Administrator
```

Developer Mode должен быть включён.

Через Awesomebar открыть:

```text
DocType
→ Service Request
```

Включить:

```text
Allow Auto Repeat = Yes
```

Сохранить DocType.

Frappe автоматически добавляет служебное поле:

```text
auto_repeat
```

Это Link на `Auto Repeat`, который связывает исходный Document с его расписанием.

Не создаём такое поле вручную.

---

# 6. Найти автоматически созданный Custom Field

Через Awesomebar открыть:

```text
Custom Field
```

Отфильтровать:

```text
Document Type = Service Request
Fieldname     = auto_repeat
```

Должен существовать служебный Custom Field.

Зафиксировать:

```text
Allow Auto Repeat
→ не просто флаг интерфейса
→ Frappe добавляет техническую связь с Auto Repeat
```

Не менять этот Custom Field вручную.

---

# 7. Создать исходную Service Request

Создать отдельную заявку-шаблон эксперимента:

```text
Subject:     Periodic inspection template
Location:    Room 101
Equipment:   <любое Equipment из Room 101 или пусто>
Description: Template for Auto Repeat laboratory
Priority:    Medium
Target Date: <пусто>
Status:      New
```

Сохранить.

Запомнить номер, например:

```text
SR-00042
```

`Target Date` оставляем пустым намеренно.

В текущей модели это необязательное Date-поле, а Auto Repeat автоматически переносит `Next Schedule Date` только в обязательные Date-поля повторяемого DocType.

Не ожидаем, что необязательный `Target Date` станет датой расписания сам по себе.

---

# 8. Создать Auto Repeat

Через Awesomebar открыть:

```text
Auto Repeat
```

Создать:

```text
Reference Document Type: Service Request
Reference Document:      <номер Periodic inspection template>
Start Date:              сегодня
Frequency:               Daily
Disabled:                No
Submit on Creation:      No
Notify by Email:         No
```

End Date пока оставить пустым.

Сохранить.

Имя будет штатным, примерно:

```text
AUT-AR-00001
```

---

# 9. Проверить связь с исходной заявкой

Вернуться в исходный `Service Request`.

Поле `auto_repeat` должно ссылаться на созданный Auto Repeat.

Получаем:

```text
Service Request SR-...
        │
        └── auto_repeat → AUT-AR-00001
```

Один Reference Document не должен одновременно иметь два разных Auto Repeat.

Попробовать создать второй Auto Repeat на ту же исходную заявку.

Frappe должен запретить это.

После проверки второй документ не сохранять.

---

# 10. Посмотреть рассчитанную дату

Открыть созданный `Auto Repeat`.

Проверить:

```text
Status             = Active
Frequency          = Daily
Next Schedule Date = завтра
```

При Daily расписании первая новая копия создаётся на следующую рассчитанную дату.

`Next Schedule Date` — read-only результат расчёта Frappe.

Не вводим его вручную.

---

# 11. Добавить Assignee

В секции Assignee добавить:

```text
technician.one@example.com
```

Оставить:

```text
Generate Separate Documents For Each Assignee = No
```

Сохранить.

При создании повторного Document Frappe после insert использует штатный Assign To-механизм.

То есть результат будет:

```text
новый Service Request
        ↓
Assign To
        ↓
ToDo
```

Отдельного поля `Assigned Technician` по-прежнему не нужно.

---

# 12. Негативный тест Submit on Creation

На Auto Repeat временно попробовать включить:

```text
Submit on Creation = Yes
```

Сохранить.

`Service Request` в нашем приложении не является Submittable DocType.

Frappe должен запретить такую настройку.

Вернуть:

```text
Submit on Creation = No
```

Главный вывод:

```text
Auto Repeat может автоматически Submit-ить
только submittable DocType
```

`Service Request` ради этой функции submittable не делаем.

---

# 13. Подготовить немедленную проверку scheduler

Ждать календарные сутки для лаборатории не нужно.

Открыть существующий Auto Repeat и изменить:

```text
Start Date = вчера
```

Сохранить.

Это уже не первоначальный insert Auto Repeat, поэтому Frappe пересчитает расписание от указанной даты.

Проверить:

```text
Next Schedule Date = сегодня
```

Теперь запись подходит для текущего запуска Auto Repeat scheduler-job.

---

# 14. Запустить штатный Auto Repeat job вручную

В терминале:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost execute \
  frappe.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry
```

Это тот же штатный метод, который Frappe запускает через scheduler.

Он не содержит нашей бизнес-логики.

Метод находит Auto Repeat, у которых:

```text
Next Schedule Date <= сегодня
Status = Active
Disabled = No
```

и ставит создание Documents в long queue.

---

# 15. Проверить background job

Сразу проверить:

```bash
bench --site facility-ops.localhost show-pending-jobs
bench --site facility-ops.localhost doctor
```

В `bench start` должны быть доступны workers, включая long queue.

Не писать собственный scheduler event.

Frappe уже регистрирует Auto Repeat как штатную daily maintenance задачу.

---

# 16. Проверить новую Service Request

В Desk открыть:

```text
Service Request
```

Найти новую заявку с Subject:

```text
Periodic inspection template
```

Она должна иметь **другой `name`**, чем исходная заявка.

Сравнить:

```text
Reference Document
SR-00042

Generated Document
SR-00043
```

Номера примерные.

Проверить скопированные значения:

```text
Subject
Location
Equipment
Description
Priority
Status = New
```

Это новый обычный `Service Request`, а не строка внутри Auto Repeat.

---

# 17. Проверить назначение

Открыть созданную повтором заявку.

Проверить:

```text
Assigned To = technician.one@example.com
```

Открыть связанный `ToDo`.

Проверить:

```text
Reference Type = Service Request
Reference Name = новый номер заявки
Allocated To   = technician.one@example.com
```

Assignment Rule сейчас отключён.

Следовательно это назначение создал именно:

```text
Auto Repeat Assignee
→ Assign To
→ ToDo
```

---

# 18. Проверить Workflow отдельно

Новая повторная заявка должна оставаться:

```text
Status = New
```

Сам Auto Repeat не выполняет:

```text
New → Assigned
```

Под Supervisor отдельно выполнить Workflow Action:

```text
Mark Assigned
```

После этого:

```text
Status = Assigned
```

Фиксируем:

```text
Auto Repeat
= когда создать новый Document

Assignment
= кому его назначить

Workflow
= в каком состоянии находится процесс
```

---

# 19. Проверить Next Schedule Date после запуска

Открыть Auto Repeat снова.

После успешной обработки сегодняшнего расписания `Next Schedule Date` должна перейти на следующую дату.

Для Daily:

```text
сегодня
→ создан новый Document
→ Next Schedule Date = завтра
```

То есть Auto Repeat хранит состояние собственного расписания.

Не создаём свой счётчик повторов.

---

# 20. Проверить End Date

На Auto Repeat задать будущую `End Date`, например через несколько дней.

Сохранить.

Проверить рассчитанное расписание штатным просмотром Auto Repeat, если кнопка Schedule доступна на стенде.

Затем попробовать некорректное значение:

```text
End Date = Start Date
```

Frappe должен отклонить его.

После теста вернуть корректную будущую End Date или очистить её.

---

# 21. Проверить Disabled

Установить:

```text
Disabled = Yes
```

Сохранить.

Проверить:

```text
Status             = Disabled
Next Schedule Date = пусто
```

Исходный `Service Request` больше не должен считаться активным участником расписания.

Вернуть:

```text
Disabled = No
```

только если нужен следующий тест.

---

# 22. Что реально хранится где

После лаборатории различать:

```text
Service Request template
→ обычный working Document

Auto Repeat
→ configuration Document с расписанием

Generated Service Request
→ новый working Document

ToDo
→ assignment Document

Allow Auto Repeat
→ metadata DocType

auto_repeat
→ служебный Custom Field / ссылка
```

Auto Repeat не является копией данных «на будущее».

Он хранит правило, по которому Frappe создаёт новые Documents.

---

# 23. Проверить Git во время эксперимента

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Изменение:

```text
Allow Auto Repeat = Yes
```

относится к Standard metadata `Service Request`, поэтому изменение DocType должно быть видно в source app.

Рабочие записи:

```text
Auto Repeat
Service Request template
Generated Service Request
ToDo
```

сами по себе в Git не попадают.

Служебный `auto_repeat` создан как Custom Field текущего site и отдельно в source app автоматически не превращается.

---

# 24. Зафиксировать эксперимент

Проверить diff:

```bash
git diff
```

Можно сделать учебный commit состояния лаборатории:

```bash
git add .
git commit -m "Lab C: enable Service Request auto repeat"
```

Это не означает, что Auto Repeat должен остаться в финальном приложении.

Следующий шаг — штатная очистка.

---

# 25. Удалить Auto Repeat

Сначала открыть созданный:

```text
AUT-AR-xxxxx
```

и удалить его штатным `Delete`.

Удаление Auto Repeat очищает ссылку `auto_repeat` у Reference Document.

Проверить исходный `Service Request`:

```text
auto_repeat = пусто
```

Тестовые Service Request, созданные во время лаборатории, можно удалить отдельно, если они больше не нужны.

---

# 26. Отключить Allow Auto Repeat

Открыть:

```text
DocType → Service Request
```

Вернуть:

```text
Allow Auto Repeat = No
```

Сохранить.

Важно:

выключение флага само по себе не является гарантией удаления уже созданного служебного Custom Field.

Поэтому проверяем его отдельно.

---

# 27. Удалить оставшийся Custom Field

Открыть:

```text
Custom Field
```

Найти:

```text
Document Type = Service Request
Fieldname     = auto_repeat
```

Если запись осталась — удалить её штатно.

После этого выполнить:

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost clear-cache
```

Открыть `Service Request` заново и проверить, что служебного поля Auto Repeat больше нет.

---

# 28. Вернуть Assignment Rule

Открыть:

```text
Service Request Auto Assignment
```

Вернуть:

```text
Disabled = No
```

Сохранить.

Основной процесс L9 снова работает как до лаборатории.

---

# 29. Проверить финальный Git

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff
```

После возврата `Allow Auto Repeat = No` предметная модель должна снова соответствовать основной архитектуре.

Если во время сохранения Standard DocType изменился только технический `modified` timestamp, это видно в diff и должно быть осознанно зафиксировано или возвращено через Git после проверки.

Не использовать `git restore` вслепую, если в том же файле есть реальные изменения курса.

Если эксперимент был отдельным commit, сделать второй commit очистки:

```bash
git add .
git commit -m "Lab C: remove auto repeat experiment"
```

---

# 30. Финальное состояние

После Lab C должно остаться:

```text
Service Request.allow_auto_repeat = No
нет активного Auto Repeat лаборатории
нет Custom Field Service Request.auto_repeat
Assignment Rule снова включён
основные Workflow / Permissions не изменены
```

Постоянное ядро:

```text
Facility Location
Equipment
Service Request
```

---

# 31. Что нужно уметь объяснить

После лаборатории ученик должен своими словами объяснить:

1. Зачем DocType должен разрешить `Allow Auto Repeat`.
2. Что хранит `Auto Repeat`.
3. Чем Reference Document отличается от generated Document.
4. Что означает `Next Schedule Date`.
5. Что делает scheduler.
6. Зачем Auto Repeat использует background queue.
7. Как Assignee превращается в обычный `ToDo`.
8. Почему Auto Repeat не заменяет Workflow.
9. Почему `Submit on Creation` неприменим к нашему `Service Request`.
10. Почему необязательный `Target Date` не обязан автоматически стать датой расписания.
11. Чем metadata `Allow Auto Repeat` отличается от configuration Document `Auto Repeat`.
12. Как полностью убрать эксперимент после лаборатории.

---

# 32. Приёмка Lab C

Лаборатория пройдена, если ученик без подсказки может выполнить цепочку:

```text
включить Allow Auto Repeat
→ увидеть служебный auto_repeat
→ создать reference Service Request
→ создать Auto Repeat
→ настроить Daily
→ добавить Assignee
→ получить Next Schedule Date
→ подготовить запуск на сегодня
→ запустить штатный scheduler method
→ получить новый Service Request
→ увидеть ToDo назначенного Technician
→ доказать, что Workflow остался отдельным
→ удалить Auto Repeat
→ отключить Allow Auto Repeat
→ удалить служебный Custom Field
→ вернуть Assignment Rule
```

И объяснить итоговую архитектуру:

```text
Auto Repeat
= расписание создания Documents

Assign To / ToDo
= назначение созданной работы

Workflow
= управление состоянием работы
```

После очистки лаборатория не оставляет нового постоянного предметного DocType.