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

Останется:

```text
AUT-AR-00001
Disabled = ✓
```

если это первый Auto Repeat на чистом стенде курса.

---

# Часть 1. Создай Recurring Note

Работай под `Administrator`.

Открой `DocType` и создай Standard DocType:

```text
Name:   Recurring Note
Module: Training
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

# Часть 2. Создай reference document

Открой новый `Recurring Note`.

Заполни:

```text
Title:    Monthly Check Template
Run Date: 2026-08-30
```

Сохрани.

На чистом стенде курса ожидается имя вида:

```text
RN-2026-00001
```

Запомни фактический системный `name` — он будет выбран в Auto Repeat.

---

# Часть 3. Создай Auto Repeat

Открой:

```text
http://learn.localhost:8000/app/auto-repeat
```

Создай новый Auto Repeat:

```text
Reference Document Type: Recurring Note
Reference Document:      <name Monthly Check Template>
Start Date:              2026-08-31
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
Next Schedule Date = 2026-09-01
```

Причина:

```text
Start Date 2026-08-31
+
Daily
→ следующий запуск 2026-09-01
```

---

# Часть 4. Подготовь запуск на сегодня

У уже сохранённого Auto Repeat измени только:

```text
Start Date = 2026-08-30
```

Сохрани.

Ожидается:

```text
Next Schedule Date = 2026-08-31
```

Это сегодняшняя дата учебного прохода.

---

# Часть 5. Выполни сегодняшнее повторение сейчас

Открой терминал WSL2.

Перейди в Bench:

```bash
cd ~/frappe/frappe16-course-bench
```

Сначала зафиксируй фактическое имя Auto Repeat из формы. Для чистого стенда:

```bash
AR_NAME="AUT-AR-00001"
```

Если на форме другое имя, замени значение переменной на него.

Теперь выполни:

```bash
bench --site learn.localhost execute \
  frappe.automation.doctype.auto_repeat.auto_repeat.create_repeated_entries \
  --kwargs "{'data': [{'name': '$AR_NAME'}]}"
```

Команда может завершиться без отдельного текстового результата. Это нормально: проверяем не stdout, а состояние Frappe.

---

# Часть 6. Проверь созданный Document

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
Run Date = 2026-08-30
```

### Новая копия

```text
Run Date = 2026-08-31
```

У новой копии другой системный `name`, например:

```text
RN-2026-00002
```

Это реальный новый Document, а не изменение reference document.

---

## Проверь продвижение расписания

Снова открой Auto Repeat.

После сегодняшнего создания ожидается:

```text
Next Schedule Date = 2026-09-01
Status = Active
```

То есть Framework не только создал копию, но и сдвинул расписание дальше.

---

# Эксперимент — Daily против Weekly

На Auto Repeat установи:

```text
Start Date = 2026-08-30
Frequency  = Weekly
```

Таблицу `Repeat on Days` оставь пустой.

Сохрани.

Ожидается:

```text
Next Schedule Date = 2026-09-06
```

Обычный недельный шаг без выбранных weekdays равен семи дням.

---

# Восстанови рабочее Daily расписание

Верни:

```text
Start Date = 2026-08-31
Frequency  = Daily
```

Сохрани.

Ожидается:

```text
Next Schedule Date = 2026-09-01
```

---

# Намеренная ошибка — недопустимый End Date

На том же активном Auto Repeat установи:

```text
End Date = 2026-08-31
```

Нажми `Save`.

Ожидается отказ:

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
Next Schedule Date = 2026-09-01
```

---

# Часть 7. Отключи Auto Repeat

Чтобы завтра лаборатория не начала создавать новые документы сама, установи:

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

# Часть 8. Финальная проверка блока E

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
Monthly Check Template / 2026-08-30
Monthly Check Template / 2026-08-31
```

---

## Проверка себя

1. Зачем Recurring Note получил `Allow Auto Repeat`?
2. Что является Reference Document?
3. Создался ли новый system name у повторения?
4. Почему у новой копии `Run Date = 2026-08-31`?
5. Что произошло с `Next Schedule Date` после запуска?
6. Какой результат дал Weekly от 2026-08-30?
7. Почему End Date = 2026-08-31 был отвергнут?
8. Зачем Auto Repeat в конце Disabled?
9. Чем Auto Repeat отличается от Assignment Rule?
10. Писали ли мы собственный scheduler code?

---

## Состояние стенда после лабораторной

Standard DocType:

```text
Recurring Note
  Module: Training
  Allow Auto Repeat: ✓
  Auto Name: RN-.YYYY.-.#####
  Title Field: title

  title    Data  Mandatory
  run_date Date  Mandatory
```

Существуют два Documents с Title:

```text
Monthly Check Template
```

и Run Date:

```text
2026-08-30
2026-08-31
```

Существует один проверенный Auto Repeat:

```text
Reference Document Type: Recurring Note
Reference Document:      <reference Monthly Check Template>
Start Date:              2026-08-31
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