# Лабораторная 28. Auto Repeat

## Что уже должно быть готово

Лабораторная 27 завершена.

Активен:

```text
Training Request Workflow
```

Отключены:

```text
Training Request Round Robin
Training Review Notification
```

Auto Repeat ещё не является частью учебного состояния.

---

## Что сейчас получим

Появится Standard DocType:

```text
Recurring Note
```

с двумя Documents:

```text
reference document
+
одна реально созданная Auto Repeat копия
```

Останется один проверенный Auto Repeat в состоянии:

```text
Disabled = ✓
```

---

# Часть 1. Получи даты именно из учебного Site

Открой терминал WSL2.

Перейди в Bench:

```bash
cd ~/frappe/frappe16-course-bench
```

Получим текущую дату Frappe Site:

```bash
TODAY=$(bench --site learn.localhost execute frappe.utils.nowdate)
```

Посчитаем соседние даты средствами Debian:

```bash
YESTERDAY=$(date -d "$TODAY -1 day" +%F)
TOMORROW=$(date -d "$TODAY +1 day" +%F)
WEEKLY_NEXT=$(date -d "$YESTERDAY +7 days" +%F)
```

Выведи их:

```bash
printf 'YESTERDAY=%s\nTODAY=%s\nTOMORROW=%s\nWEEKLY_NEXT=%s\n' \
  "$YESTERDAY" "$TODAY" "$TOMORROW" "$WEEKLY_NEXT"
```

Ты получишь четыре реальные даты вида:

```text
YESTERDAY=YYYY-MM-DD
TODAY=YYYY-MM-DD
TOMORROW=YYYY-MM-DD
WEEKLY_NEXT=YYYY-MM-DD
```

**Дальше в поля Desk вводи именно значения, которые напечатал твой терминал.**

---

# Часть 2. Создай Recurring Note

Работай под `Administrator`.

Открой `DocType` и создай Standard DocType:

```text
Name:    Recurring Note
Module:  Training
Custom?: ☐
```

Включи:

```text
Allow Auto Repeat = ✓
```

Настрой naming:

```text
Auto Name:   RN-.YYYY.-.#####
Title Field: title
```

Добавь поля:

| Label | Fieldname | Type | Mandatory |
|---|---|---|---|
| Title | `title` | Data | ✓ |
| Run Date | `run_date` | Date | ✓ |

Сохрани DocType.

---

## Проверь, что Framework добавил служебную связь сам

Открой `Customize Form` для:

```text
Recurring Note
```

Найди поле:

```text
Auto Repeat
fieldname: auto_repeat
```

Это служебный Custom Field, созданный из-за:

```text
Allow Auto Repeat = ✓
```

Ничего в нём не меняй.

Закрой Customize Form без изменений.

---

# Часть 3. Создай reference document

Открой новый `Recurring Note`.

Заполни:

```text
Title:    Monthly Check Template
Run Date: <значение YESTERDAY>
```

Сохрани.

На чистом стенде курса ожидается имя вида:

```text
RN-<current-year>-00001
```

Запомни фактический системный `name` — он будет выбран в Auto Repeat.

---

# Часть 4. Создай Auto Repeat

Открой:

```text
http://learn.localhost:8000/app/auto-repeat
```

Создай новый Auto Repeat:

```text
Reference Document Type: Recurring Note
Reference Document:      <name Monthly Check Template>
Start Date:              <значение TODAY>
Frequency:               Daily
Disabled:                ☐
```

Не включай email и assignees.

Сохрани.

На чистом стенде курса это первый Auto Repeat, поэтому ожидается:

```text
AUT-AR-00001
```

Если фактический system name отличается, дальше используй именно имя из своей формы.

---

## Проверь первое рассчитанное расписание

После Save ожидается:

```text
Status = Active
Next Schedule Date = <значение TOMORROW>
```

Причина:

```text
Start Date = TODAY
+
Daily
→ Next Schedule Date = TOMORROW
```

---

# Часть 5. Подготовь запуск на TODAY

У уже сохранённого Auto Repeat измени только:

```text
Start Date = <значение YESTERDAY>
```

Сохрани.

Ожидается:

```text
Next Schedule Date = <значение TODAY>
```

Теперь scheduled backend имеет запись, которую нужно выполнить именно сегодня.

---

# Часть 6. Выполни сегодняшнее повторение сейчас

Вернись в терминал:

```bash
cd ~/frappe/frappe16-course-bench
```

Зафиксируй фактическое имя Auto Repeat из формы. Для чистого стенда:

```bash
AR_NAME="AUT-AR-00001"
```

Если на форме другое имя, замени значение переменной на него.

Выполни:

```bash
bench --site learn.localhost execute \
  frappe.automation.doctype.auto_repeat.auto_repeat.create_repeated_entries \
  --kwargs "{'data': [{'name': '$AR_NAME'}]}"
```

Команда может завершиться без отдельного текстового результата. Это нормально: проверяем не stdout, а состояние Frappe.

---

# Часть 7. Проверь созданный Document

Вернись в Desk и открой:

```text
http://learn.localhost:8000/app/recurring-note
```

Для Title:

```text
Monthly Check Template
```

теперь должны существовать **два** Documents.

Открой оба и сравни.

### Reference

```text
Run Date = <значение YESTERDAY>
```

### Новая копия

```text
Run Date = <значение TODAY>
```

У новой копии другой системный `name`, например следующий `RN-...` в series.

Это реальный новый Document, а не изменение reference document.

---

## Проверь продвижение расписания

Снова открой Auto Repeat.

После сегодняшнего создания ожидается:

```text
Next Schedule Date = <значение TOMORROW>
Status = Active
```

То есть Framework не только создал копию, но и сдвинул расписание дальше.

---

# Эксперимент — Daily против Weekly

На Auto Repeat установи:

```text
Start Date = <значение YESTERDAY>
Frequency  = Weekly
```

Таблицу `Repeat on Days` оставь пустой.

Сохрани.

Ожидается:

```text
Next Schedule Date = <значение WEEKLY_NEXT>
```

То есть обычный недельный шаг без выбранных weekdays равен семи дням.

---

# Восстанови рабочее Daily расписание

Верни:

```text
Start Date = <значение TODAY>
Frequency  = Daily
```

Сохрани.

Ожидается:

```text
Next Schedule Date = <значение TOMORROW>
```

---

# Намеренная ошибка — недопустимый End Date

На том же активном Auto Repeat установи:

```text
End Date = <значение TODAY>
```

Нажми `Save`.

Ожидается точный отказ:

```text
End Date cannot be today.
```

Рабочая запись не должна сохраниться с этим End Date.

---

# Восстановление

Очисти:

```text
End Date
```

Сохрани.

Проверь снова:

```text
Status = Active
Next Schedule Date = <значение TOMORROW>
```

---

# Часть 8. Отключи Auto Repeat

Чтобы после лабораторной правило не создавало новые документы само, установи:

```text
Disabled = ✓
```

Сохрани.

Ожидается:

```text
Status = Disabled
Next Schedule Date = пусто
```

Auto Repeat не удаляй.

---

# Часть 9. Финальная проверка блока E

Проверь, что существуют:

```text
Training Request Round Robin
→ Disabled = ✓

Training Request Workflow
→ Is Active = ✓

Training Review Notification
→ Enabled = ☐

Auto Repeat <AUT-AR-name>
→ Disabled = ✓
```

Проверь два `Recurring Note`:

```text
Monthly Check Template / <YESTERDAY>
Monthly Check Template / <TODAY>
```

---

## Проверка себя

1. Откуда в лабораторной взято значение TODAY?
2. Зачем Recurring Note получил `Allow Auto Repeat`?
3. Какое служебное поле Framework добавил сам?
4. Что является Reference Document?
5. Создался ли новый system name у повторения?
6. Почему у новой копии `Run Date = TODAY`?
7. Что произошло с `Next Schedule Date` после запуска?
8. Какой результат дал Weekly от YESTERDAY?
9. Почему End Date = TODAY был отвергнут?
10. Зачем Auto Repeat в конце Disabled?
11. Писали ли мы собственный scheduler code?

---

## Состояние стенда после лабораторной

Standard DocType:

```text
Recurring Note
  Module: Training
  Allow Auto Repeat: ✓
  Auto Name: RN-.YYYY.-.#####
  Title Field: title

  title       Data  Mandatory
  run_date    Date  Mandatory
  auto_repeat служебный Custom Field, создан Framework
```

Существуют два Documents с Title:

```text
Monthly Check Template
```

и Run Date:

```text
reference = YESTERDAY текущего прохода
generated = TODAY текущего прохода
```

Существует один проверенный Auto Repeat:

```text
Reference Document Type: Recurring Note
Reference Document:      <reference Monthly Check Template>
Start Date:              TODAY текущего прохода
Frequency:               Daily
End Date:                пусто
Disabled:                ✓
Status:                  Disabled
Next Schedule Date:      пусто
```

Также после блока E:

```text
Training Request Round Robin → Disabled
Training Request Workflow    → Active
Training Review Notification → Disabled
```

Permissions и Sharing блока D восстановлены и не изменены.

Это точное входное состояние следующего блока: [**29. Timeline и Comments**](../29_TIMELINE_AND_COMMENTS.md).