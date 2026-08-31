# 28. Auto Repeat

В прошлой главе Notification реагировал на событие и отправлял сообщение.

Теперь разберём другой тип автоматизации:

```text
Auto Repeat
```

Он нужен, когда один и тот же тип документа должен **создаваться снова по расписанию**.

Например:

```text
каждый месяц
→ создать новый Request
→ на основе уже подготовленного образца
```

Проверено: **2026-08-31**.

---

## 1. Самая простая картина

Есть документ:

```text
Request REQ-0001
```

Он уже заполнен так, как нам нужно:

```text
Subject: Monthly Check
Department: Operations
Priority: Medium
```

Хотим получать такой же новый Request каждый месяц.

Для этого создаём:

```text
Auto Repeat
├── Reference Document Type = Request
├── Reference Document      = REQ-0001
├── Frequency               = Monthly
└── Start Date              = 01.09.2026
```

Дальше Frappe по расписанию создаёт **новый Document** на основе `REQ-0001`.

Удобно запомнить так:

```text
Reference Document
        ↓
    Auto Repeat
        ↓
    расписание
        ↓
новый Document
```

Auto Repeat не «переоткрывает» старый документ.

Он создаёт новый.

---

## 2. Reference Document — это образец

Главные поля Auto Repeat:

```text
Reference Document Type
Reference Document
```

Например:

```text
Reference Document Type: Request
Reference Document: REQ-0001
```

Исходный `REQ-0001` остаётся существовать как обычный документ.

Когда приходит следующая дата расписания, Framework берёт его текущее содержимое и делает копию.

Поэтому Reference Document удобно воспринимать как:

> живой шаблон для будущих повторений

Если до следующего запуска изменить исходный документ, новая копия будет строиться уже из его актуального состояния.

---

# Подготовка DocType

## 3. Сначала нужно разрешить Auto Repeat для DocType

Не каждый DocType автоматически появляется в Auto Repeat.

У целевого DocType должна быть включена настройка:

```text
Allow Auto Repeat
```

Для стандартного DocType это обычно делается через:

```text
Customize Form
```

После этого Framework разрешит выбрать такой DocType как `Reference Document Type`.

Если флаг не включён, backend v16 прямо отклоняет создание Auto Repeat с сообщением о необходимости включить `Allow Auto Repeat`.

---

## 4. На одном Reference Document нельзя повесить несколько Auto Repeat

Frappe связывает исходный документ с конкретным Auto Repeat.

Если документ уже участвует в другом активном Auto Repeat, второй создать не получится.

То есть модель примерно такая:

```text
REQ-0001
   ↓
AUT-AR-00001
```

а не:

```text
REQ-0001
├── Monthly rule
├── Weekly rule
└── Yearly rule
```

Если нужно несколько независимых расписаний, обычно нужны разные reference documents либо уже собственная автоматизация.

---

# Расписание

## 5. Frequency в текущем v16

В актуальном Frappe v16 доступны:

```text
Daily
Weekly
Fortnightly
Monthly
Quarterly
Half-yearly
Yearly
```

`Fortnightly` означает повтор примерно каждые 14 дней.

Это важно: старые описания Auto Repeat часто перечисляют не весь текущий набор.

---

## 6. Start Date

`Start Date` задаёт начало расписания.

Пример:

```text
Start Date: 01.09.2026
Frequency: Monthly
```

Дальше Framework рассчитывает `Next Schedule Date`.

Если при создании Auto Repeat указать дату в прошлом, текущий v16 при обычной работе корректирует её до сегодняшней даты.

Поэтому Auto Repeat не предназначен для автоматического «догоняющего» создания всех пропущенных документов за прошлый год.

---

## 7. End Date

`End Date` необязателен.

Если его нет:

```text
Auto Repeat
→ работает дальше, пока его не отключат
```

Если есть:

```text
Start Date: 01.09.2026
End Date:   31.12.2026
```

после окончания периода правило становится завершённым.

Статусы Auto Repeat в v16:

```text
Active
Disabled
Completed
```

---

## 8. Next Schedule Date

Framework сам хранит:

```text
Next Schedule Date
```

Это ближайшая дата, когда должен быть создан новый документ.

В форме Auto Repeat v16 также показывает рассчитанное расписание.

Поэтому не нужно самому вычислять:

```text
какой следующий понедельник?
какое следующее первое число?
через сколько месяцев квартал?
```

Это делает Auto Repeat.

---

# Weekly

## 9. Weekly можно настроить по дням недели

При:

```text
Frequency = Weekly
```

появляется таблица:

```text
Repeat on Days
```

Например:

```text
Monday
Wednesday
Friday
```

Тогда повторение может происходить по этим дням недели.

Если конкретные дни не заданы, backend v16 использует обычный недельный шаг от текущей schedule date.

---

# Monthly и более длинные периоды

## 10. Repeat on Day

Для частот:

```text
Monthly
Quarterly
Half-yearly
Yearly
```

можно задать:

```text
Repeat on Day
```

Например:

```text
Frequency: Monthly
Repeat on Day: 10
```

означает идею:

```text
10 сентября
10 октября
10 ноября
...
```

---

## 11. Repeat on Last Day of the Month

Для `Monthly` есть отдельная настройка:

```text
Repeat on Last Day of the Month
```

Это удобнее, чем пытаться писать:

```text
Repeat on Day = 31
```

потому что месяцы имеют разную длину.

Например:

```text
31 января
28 февраля
31 марта
30 апреля
```

Framework сам рассчитывает последний день соответствующего месяца.

---

# Что именно происходит при повторении

## 12. Frappe создаёт копию Reference Document

Текущий v16 использует внутри:

```python
frappe.copy_doc(reference_doc, ignore_no_copy=False)
```

То есть новый документ строится как копия исходного.

Но это не побайтовый клон строки в базе.

Framework создаёт новый Document и прогоняет его через обычный процесс вставки.

Схематично:

```text
Reference Document
        ↓ copy_doc
new Document в памяти
        ↓ подготовка Auto Repeat
insert()
        ↓
новая запись в базе
```

---

## 13. Поля `No Copy` учитываются

Поскольку используется обычный механизм копирования, свойства полей продолжают иметь значение.

Если поле отмечено:

```text
No Copy
```

не нужно рассчитывать, что Auto Repeat обязан переносить его как обычное поле.

Это ещё одна причина правильно настраивать metadata DocType, а не пытаться потом чинить результат скриптами.

---

## 14. Новый документ снова начинается как Draft

Перед созданием Framework устанавливает:

```text
docstatus = 0
```

То есть даже если Reference Document был Submitted, новая копия сначала является новым Draft.

Это логично:

```text
старый документ
≠
новый экземпляр документа
```

---

## 15. Mandatory Date-поля получают дату расписания

В текущем backend v16 есть важное специальное поведение.

Для обязательных полей типа:

```text
Date
```

Auto Repeat устанавливает:

```text
Next Schedule Date
```

Например исходный документ имел:

```text
work_date = 01.08.2026
```

а новая scheduled date:

```text
01.09.2026
```

тогда обязательное Date-поле может получить новую дату расписания.

Это нужно помнить, если в DocType несколько обязательных дат с разным бизнес-смыслом.

---

## 16. `from_date` и `to_date` имеют специальную поддержку

Если DocType содержит поля:

```text
from_date
to_date
```

то для месячных/квартальных/полугодовых/годовых повторений v16 умеет сдвигать период вперёд.

Например:

```text
01.08.2026 → 31.08.2026
```

может стать следующим периодом:

```text
01.09.2026 → 30.09.2026
```

Это специальное соглашение Auto Repeat, а не универсальная система расчёта любых пользовательских периодов.

---

# Submit on Creation

## 17. Новый документ можно автоматически Submit

Есть настройка:

```text
Submit on Creation
```

Если она включена, после `insert()` Framework вызывает:

```python
new_doc.submit()
```

Но это разрешено только для:

```text
Is Submittable = Yes
```

Если DocType не Submittable, v16 не даст включить `Submit on Creation`.

---

## 18. Не включай Submit on Creation просто ради удобства

Автоматический Submit означает, что новый документ сразу проходит настоящий lifecycle:

```text
Draft
  ↓
Submitted
```

После этого обычное редактирование уже ограничено правилами Submitted Document.

Поэтому сначала спроси:

> новый повтор действительно должен сразу стать юридически/логически зафиксированным документом?

Если нет — оставь Draft.

---

# Assignee

## 19. Auto Repeat v16 умеет назначать созданный документ

В текущем Auto Repeat есть:

```text
Assignee
```

Можно выбрать пользователей, которым новый Document будет назначен через стандартный Assignment.

То есть после создания происходит обычная знакомая нам схема:

```text
new Document
    ↓ Assign
   ToDo
    ↓
  User
```

Auto Repeat не изобретает второй механизм исполнителей.

Он использует штатный Assignment.

---

## 20. Один документ можно назначить нескольким людям

Если указать несколько assignees и оставить обычный режим:

```text
Anna
Boris
```

Auto Repeat создаёт один новый документ и назначает его выбранным пользователям.

Концептуально:

```text
REQ-0002
├── ToDo → Anna
└── ToDo → Boris
```

---

## 21. Можно создавать отдельный документ на каждого assignee

В v16 есть настройка:

```text
Generate Separate Documents For Each Assignee
```

Тогда при двух пользователях:

```text
Anna
Boris
```

можно получить:

```text
REQ-0002 → Anna
REQ-0003 → Boris
```

а не один общий документ на двоих.

Это полезно, когда повторяемая работа должна физически существовать как отдельная запись для каждого исполнителя.

---

# Email

## 22. Auto Repeat может отправить email после создания

У него есть собственная секция Notification:

```text
Notify by Email
Recipients
Template
Subject
Message
Print Format
```

То есть можно:

```text
создать новый документ
        ↓
отправить письмо
        ↓
приложить Print Format
```

Subject и Message поддерживают Jinja.

Например:

```text
New {{ doc.doctype }} #{{ doc.name }}
```

---

## 23. Это не тот же самый DocType Notification

Важно не смешивать два механизма.

```text
Notification
→ отдельное универсальное правило реакции на события

Auto Repeat email
→ встроенное уведомление конкретного Auto Repeat
```

Если задача простая:

> после создания повторяемого документа отправить конкретным адресатам письмо

встроенной секции Auto Repeat может быть достаточно.

Если нужна сложная общая система уведомлений по разным событиям — используем отдельный `Notification`.

---

# Scheduler

## 24. Auto Repeat зависит от scheduler

Новый документ не создаётся браузером пользователя.

В v16 Auto Repeat запускается системным scheduler через задачу:

```text
frappe.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry
```

Она зарегистрирована в:

```text
daily_maintenance
```

То есть Auto Repeat требует нормально работающий scheduler и workers.

Если scheduler выключен, расписание может быть настроено идеально, но документы сами не появятся.

Подробно scheduler и workers разберём позже в инфраструктурном блоке.

---

## 25. Auto Repeat не является точным cron-конструктором

Auto Repeat отвечает за бизнес-повторение документов:

```text
каждый день
каждую неделю
каждые две недели
каждый месяц
каждый квартал
...
```

Он не предназначен для требований вроде:

```text
каждые 37 минут

в 08:15 первого рабочего дня после третьего четверга

после получения внешнего API-события

только если сложный набор данных в других DocType удовлетворяет алгоритму
```

Для такого уровня нужны уже:

```text
Scheduler
background job
Server Script
App code
```

в зависимости от задачи.

---

# Ошибки при создании

## 26. Ошибка не должна бесконечно ломать scheduler

Допустим Reference Document раньше был валидным.

Потом изменилась модель DocType:

```text
появилось новое Mandatory поле
```

и следующая копия не может сохраниться.

Текущий v16 ловит ошибку создания Auto Repeat, пишет Error Log и отключает проблемный Auto Repeat.

Это лучше, чем ежедневно снова создавать одну и ту же аварийную попытку.

После исправления причины правило нужно снова включить.

---

# Расширение через код

## 27. После подготовки копии вызывается `on_recurring`

Перед вставкой нового документа Auto Repeat вызывает метод целевого документа:

```python
on_recurring(reference_doc=reference_doc, auto_repeat_doc=auto_repeat_doc)
```

Это уже точка расширения для собственного App.

Например, если стандартного копирования почти хватает, но для конкретного DocType нужно перед созданием пересчитать одно поле, можно реализовать `on_recurring` в controller.

Но не начинай с этого без необходимости.

Сначала проверь штатный Auto Repeat.

---

# Auto Repeat и обычное копирование

## 28. Duplicate и Auto Repeat решают разные задачи

Ручное Duplicate:

```text
пользователь нажал Duplicate
→ копия появилась сейчас
```

Auto Repeat:

```text
настроили один раз
→ scheduler создаёт копии дальше сам
```

То есть Auto Repeat — это не новый тип Document.

Это автоматизация обычного создания документов.

---

# Auto Repeat и Assignment Rule

## 29. Эти механизмы можно сочетать

Auto Repeat может создать новый `Request`.

После его `insert()` на этот же Request могут сработать другие штатные механизмы Framework.

Например:

```text
Auto Repeat
    ↓
создал Request
    ↓
Assignment Rule
    ↓
назначил исполнителя
    ↓
Notification
    ↓
отправил сообщение
```

Не обязательно пытаться собрать весь процесс внутри одной настройки.

У разных механизмов разные обязанности.

---

# Когда Auto Repeat подходит

## 30. Хорошие задачи для Auto Repeat

Например:

```text
ежемесячная проверка

еженедельный повторяющийся Request

квартальный документ

ежегодная карточка продления

повторяющийся Submittable Document

одинаковая регулярная работа для нескольких пользователей
```

Главный признак:

> нужно регулярно создавать новый документ на основе известного образца

---

## 31. Когда Auto Repeat не подходит

Не стоит тянуть его на задачу, если требуется:

```text
изменять существующий Document вместо создания нового

сложный плавающий календарь

очень точное время запуска

реакция на внешнее событие

сложный алгоритм формирования данных

массовая генерация документов из произвольного набора источников
```

Тогда правильнее сразу рассматривать automation code или Scheduler.

---

# Мини-практика

## 32. Создай простой повторяемый DocType

Возьми учебный DocType:

```text
Request
```

с полями:

```text
subject     Data
work_date   Date / Mandatory
priority    Select
```

Включи:

```text
Allow Auto Repeat
```

---

## 33. Создай Reference Document

Например:

```text
Subject: Weekly Review
Work Date: 01.09.2026
Priority: Medium
```

Сохрани документ.

---

## 34. Создай Auto Repeat

Настрой:

```text
Reference Document Type: Request
Reference Document: <твой Request>
Frequency: Weekly
Start Date: ближайшая подходящая дата
```

Выбери один день недели.

Сохрани.

Посмотри:

```text
Next Schedule Date
Auto Repeat Schedule
```

---

## 35. Проверь назначение

Добавь одного пользователя в:

```text
Assignee
```

После генерации нового документа проверь, что у него появился обычный Assignment / ToDo.

Если есть два тестовых пользователя, попробуй отдельно:

```text
Generate Separate Documents For Each Assignee
```

и сравни результат.

---

# Что запомнить

1. **Auto Repeat создаёт новый Document, а не меняет старый.**
2. **Reference Document является образцом для будущих копий.**
3. Для DocType нужно включить `Allow Auto Repeat`.
4. В v16 доступны `Daily / Weekly / Fortnightly / Monthly / Quarterly / Half-yearly / Yearly`.
5. Новый документ сначала создаётся как Draft; `Submit on Creation` отдельно вызывает настоящий Submit.
6. Auto Repeat умеет использовать штатный Assignment и создавать отдельные документы для каждого assignee.
7. `No Copy`, обязательные Date-поля и `on_recurring` влияют на итоговую копию.
8. Auto Repeat зависит от работающего scheduler.
9. Для сложного нестандартного расписания или алгоритма нужен уже Scheduler/App code.

---

## Источники

- Frappe/ERPNext Docs — Auto Repeat: https://docs.frappe.io/erpnext/auto-repeat
- Frappe v16 source — `auto_repeat.json`: https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.json
- Frappe v16 source — `auto_repeat.py`: https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.py
- Frappe v16 source — `auto_repeat.js`: https://github.com/frappe/frappe/blob/version-16/frappe/automation/doctype/auto_repeat/auto_repeat.js
- Frappe v16 source — scheduler hooks: https://github.com/frappe/frappe/blob/version-16/frappe/hooks.py

---

Предыдущая глава: **27. Notification**.

Следующая глава: **29. Timeline и Comments**.
