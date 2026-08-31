# 28. Auto Repeat

Assignment Rule автоматизировал назначение уже существующего Request. Notification реагировал на событие уже существующего документа.

`Auto Repeat` решает другую задачу:

```text
по расписанию создать новый Document
на основе заранее выбранного Document-образца
```

Для этого не нужен собственный scheduler-код.

Проверено для **Frappe Framework v16.32.0**.

---

## Почему не используем Request

На `Request` уже действует Workflow, permissions и другие учебные механизмы.

Чтобы не смешивать повторение с согласованием, для этой главы создадим отдельный простой Standard DocType:

```text
Recurring Note
```

Он нужен только для понятного опыта Auto Repeat.

---

# 1. Что будет в Recurring Note

Минимальная модель:

```text
Title
  title
  Data
  Mandatory

Run Date
  run_date
  Date
  Mandatory
```

Naming:

```text
Auto Name = RN-.YYYY.-.#####
Title Field = title
```

И главное свойство DocType:

```text
Allow Auto Repeat = ✓
```

Без него Auto Repeat не разрешит использовать этот DocType как Reference Document Type.

---

# 2. Reference Document — образец для копирования

Создадим исходный:

```text
Title: Monthly Check Template
Run Date: 2026-08-30
```

Затем Auto Repeat будет ссылаться на него:

```text
Reference Document Type = Recurring Note
Reference Document      = RN-...
```

Исходный документ не превращается в расписание и не исчезает.

Он остаётся обычным Document и служит образцом для будущих копий.

---

# 3. Основные поля Auto Repeat

Для первого опыта нужны:

```text
Reference Document Type
Reference Document
Start Date
Frequency
Next Schedule Date
Disabled
Status
```

Auto Repeat сам хранит ближайшую рассчитанную дату:

```text
Next Schedule Date
```

---

# 4. Частоты v16

В `v16.32.0` доступны:

```text
Daily
Weekly
Fortnightly
Monthly
Quarterly
Half-yearly
Yearly
```

В обязательной лабораторной используем:

```text
Daily
```

Так проще увидеть расчёт следующей даты без дополнительных правил месяца или недели.

---

# 5. Что происходит при запуске

Когда наступает `Next Schedule Date`, Frappe:

```text
берёт Reference Document
→ делает новый Document-копию
→ готовит поля для нового повторения
→ insert нового Document
→ рассчитывает следующую дату
```

Это именно новый Document с новым `name`.

Например:

```text
RN-2026-00001   ← reference
RN-2026-00002   ← создан Auto Repeat
```

---

# 6. Mandatory Date-поля получают дату расписания

В текущем backend v16 для обязательных полей типа `Date` Auto Repeat устанавливает:

```text
Next Schedule Date
```

У нашего `Recurring Note` поле:

```text
Run Date
```

обязательное.

Поэтому в лабораторной reference будет иметь:

```text
Run Date = 2026-08-30
```

а созданная сегодня копия получит:

```text
Run Date = 2026-08-31
```

Это даст видимый результат без чтения базы или Python.

---

# 7. Почему в учебнике не ждём до завтра

Обычная работа Auto Repeat зависит от scheduler.

Но учебная лаборатория не должна требовать:

```text
создать правило сегодня
→ закрыть учебник
→ вернуться завтра
```

Поэтому мы сделаем расписание так, чтобы:

```text
Next Schedule Date = 2026-08-31
```

а затем один раз вызовем штатную функцию v16 через уже установленный Bench.

Команда вида:

```bash
bench --site learn.localhost execute <функция>
```

не является нашим пользовательским скриптом. Bench просто вызывает функцию Frappe, которую тот же механизм scheduler использует для создания повторяющихся документов.

Внутреннее устройство Bench CLI будем изучать позже. Здесь команда нужна только как воспроизводимая кнопка «выполнить сегодняшнее scheduled действие сейчас».

---

# 8. Как получим Next Schedule Date = сегодня

Сегодня на учебном стенде:

```text
2026-08-31
```

Сначала создадим Auto Repeat:

```text
Start Date = 2026-08-31
Frequency  = Daily
```

После сохранения ожидается:

```text
Next Schedule Date = 2026-09-01
```

Затем у уже существующего Auto Repeat временно изменим:

```text
Start Date = 2026-08-30
```

и сохраним.

Для Daily расписания ближайшая дата станет:

```text
2026-08-31
```

Теперь штатная функция создания повторений имеет точное условие для сегодняшнего запуска.

---

# 9. После запуска

Если Auto Repeat имеет имя:

```text
AUT-AR-00001
```

и `Next Schedule Date = 2026-08-31`, вызов scheduled backend создаст новую `Recurring Note`.

После этого:

```text
новый Document создан
Next Schedule Date → 2026-09-01
```

Так мы проверим и создание, и продвижение расписания.

---

# 10. Эксперимент с Frequency

После успешного запуска временно переключим:

```text
Frequency = Weekly
Start Date = 2026-08-30
```

Без выбранных отдельных weekdays обычный недельный шаг равен семи дням.

Ожидается:

```text
Next Schedule Date = 2026-09-06
```

Затем вернём:

```text
Frequency = Daily
Start Date = 2026-08-31
```

и снова получим:

```text
Next Schedule Date = 2026-09-01
```

---

# 11. Гарантированная ошибка с End Date

На активном Auto Repeat попробуем указать:

```text
Start Date = 2026-08-31
End Date   = 2026-08-31
```

Для текущей даты v16 отклоняет такую настройку:

```text
End Date cannot be today.
```

Это удобная безопасная ошибка: ни reference document, ни уже созданная копия не повреждаются.

После неё `End Date` очищаем и сохраняем рабочую настройку.

---

# 12. Почему в конце Auto Repeat будет Disabled

Активное ежедневное правило продолжило бы создавать новые документы после лабораторной.

Поэтому финально оставим:

```text
Disabled = ✓
```

Тогда:

```text
Status = Disabled
Next Schedule Date = пусто
```

Сам Auto Repeat и созданные `Recurring Note` останутся на стенде как доказательство опыта.

---

# 13. Что остаётся отдельным от Auto Repeat

Auto Repeat не заменяет:

```text
Assignment Rule
Workflow
Notification
```

Каждый механизм отвечает на свой вопрос:

```text
Auto Repeat
→ когда создать новый Document

Assignment Rule
→ кому назначить Document

Workflow
→ какие переходы разрешены

Notification
→ кого проинформировать
```

Именно такое разделение штатных механизмов нужно видеть до того, как писать собственную автоматизацию.

---

## Что запомнить

1. Auto Repeat создаёт новый Document по расписанию.
2. Reference Document остаётся обычным Document-образцом.
3. Целевой DocType должен иметь `Allow Auto Repeat = ✓`.
4. `Next Schedule Date` рассчитывает Framework.
5. Mandatory Date-поле новой копии может получить дату расписания.
6. Для учебной проверки не нужно ждать следующего дня: используем точный Bench-вызов штатной функции v16.
7. После опыта ежедневное правило оставляем Disabled.

Теперь выполни [**лабораторную 28**](labs/28_AUTO_REPEAT_LAB.md).