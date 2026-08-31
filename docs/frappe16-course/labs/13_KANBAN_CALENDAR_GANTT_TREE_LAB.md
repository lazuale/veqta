# Лабораторная 13. Kanban, Calendar, Gantt и Tree

## Что уже должно быть готово

Лабораторная 12 завершена.

Есть шесть учебных Requests:

```text
C12-Open-High-1
C12-Open-High-2
C12-Open-Medium
C12-Progress-High
C12-Progress-Low
C12-Done-High
```

`Request.status` содержит:

```text
Open
In Progress
Done
```

Также существует Tree DocType `Training Category`.

---

## Что сейчас получим

Постоянно добавим в `Request`:

```text
Start Date  start_date  Date
End Date    end_date    Date
```

Включим:

```text
Is Calendar and Gantt = ✓
```

Оставим:

```text
Kanban Board: Request Status
Calendar View: Request Course Calendar
apps/training/training/training/doctype/request/request_calendar.js
```

---

# Часть 1. Kanban по `Status`

## 1. Открой Request List

Через поиск Desk открой:

```text
Request
```

Перейди в List View.

Через переключатель View выбери:

```text
Kanban
```

Если доски для Request ещё нет, Frappe предложит создать Kanban Board.

Создай:

```text
Kanban Board Name:       Request Status
Reference Document Type: Request
Field Name:              status
```

Для поля `Status` Frappe использует варианты:

```text
Open
In Progress
Done
```

как колонки доски.

---

## 2. Проверь, что карточка меняет Document

Найди карточку:

```text
C12-Open-Medium
```

Она должна находиться в колонке:

```text
Open
```

Перетащи её в:

```text
In Progress
```

Открой этот Request в Form View.

Проверь:

```text
Status = In Progress
```

Верни его обратно:

```text
Status = Open
```

через Kanban или Form View и сохрани.

Итоговые данные лабораторной 12 восстановлены.

---

# Часть 2. Подготовь даты для Calendar и Gantt

## 3. Создай `Start Date`

Открой:

```text
DocType → Request
```

Добавь поле в `Main / General` после `Due Date` или рядом с ним:

```text
Label:      Start Date
Fieldname:  start_date
Field Type: Date
```

---

## 4. Намеренно создай `End Date` неправильного типа

Добавь:

```text
Label:      End Date
Fieldname:  end_date
Field Type: Data
```

Да, сейчас тип специально неправильный.

Сохрани DocType.

---

## 5. Докажи ограничение Calendar View

Через поиск Desk открой:

```text
Calendar View
```

Создай новый Calendar View.

Задай имя:

```text
Request Course Calendar
```

Выбери:

```text
Reference Document Type: Request
Subject Field:            subject
Start Date Field:         start_date
```

Теперь открой список вариантов:

```text
End Date Field
```

Ожидаемый результат:

```text
end_date отсутствует среди доступных Date/Datetime fields
```

Причина точная: мы создали `end_date` как `Data`, а форма Calendar View v16.32.0 предлагает для Start/End только `Date` и `Datetime`.

Не пытайся сохранять Calendar View без обязательного End Date Field.

---

## Восстановление ошибки

Вернись в:

```text
DocType → Request
```

У `End Date` измени:

```text
Field Type: Data
```

на:

```text
Field Type: Date
```

Поле ещё не содержит данных, поэтому учебное изменение выполняется до заполнения Documents.

Сохрани DocType.

---

# Часть 3. Создай точный Calendar View

## 6. Закончи `Request Course Calendar`

Снова открой новый Calendar View и задай:

```text
Name:                    Request Course Calendar
Reference Document Type: Request
Subject Field:           subject
Start Date Field:        start_date
End Date Field:          end_date
All Day:                 ✓
```

Сохрани.

После Save на форме Calendar View нажми:

```text
Show Calendar
```

Пока часть Requests ещё может не отображаться: мы не заполнили интервалы.

---

# Часть 4. Заполни фиксированные интервалы

## 7. Заполни `Start Date` и `End Date`

У шести C12 Requests задай:

```text
C12-Open-High-1
Start Date: 2026-08-31
End Date:   2026-09-01

C12-Open-High-2
Start Date: 2026-09-03
End Date:   2026-09-05

C12-Open-Medium
Start Date: 2026-09-02
End Date:   2026-09-03

C12-Progress-High
Start Date: 2026-09-01
End Date:   2026-09-02

C12-Progress-Low
Start Date: 2026-09-03
End Date:   2026-09-04

C12-Done-High
Start Date: 2026-09-05
End Date:   2026-09-06
```

Сохрани каждый Document.

---

## 8. Проверь named Calendar

Открой:

```text
Calendar View → Request Course Calendar
→ Show Calendar
```

Перейди к августу/сентябрю 2026.

Ты должен увидеть C12 Requests на временных интервалах, заданных через:

```text
start_date
end_date
```

Открой событие кликом и убедись, что открывается тот же Request Document.

---

# Часть 5. Включи Standard Calendar/Gantt для Request

## 9. Включи флаг DocType

В `DocType → Request` включи:

```text
Is Calendar and Gantt = ✓
```

Сохрани DocType.

---

## 10. Создай точный standard mapping-файл

Сейчас мы **не изучаем JavaScript**. Выполняем один точный конфигурационный шаг, потому что Gantt v16.32.0 берёт mapping именно из Standard calendar config DocType.

Во втором терминале Debian выполни:

```bash
cd ~/frappe/frappe16-course-bench

cat > apps/training/training/training/doctype/request/request_calendar.js <<'EOF'
frappe.views.calendar["Request"] = {
    field_map: {
        start: "start_date",
        end: "end_date",
        id: "name",
        title: "subject",
        allDay: 1,
    },
};
EOF
```

Проверь файл:

```bash
cat apps/training/training/training/doctype/request/request_calendar.js
```

Ты должен увидеть ровно этот mapping.

Очисти cache Site:

```bash
bench --site learn.localhost clear-cache
```

Вернись в браузер и обнови Desk.

---

## 11. Проверь Standard Calendar

Открой Request List и через переключатель View выбери:

```text
Calendar
```

Если Frappe предлагает несколько календарей, выбери default/standard Calendar, использующий конфигурацию `Request`.

C12 Requests должны использовать те же поля:

```text
start_date
end_date
subject
```

---

## 12. Проверь Gantt

В том же переключателе View выбери:

```text
Gantt
```

Ожидаемый результат:

```text
C12 Requests отображаются как полосы
начало полосы = Start Date
конец полосы  = End Date
```

Открой одну полосу кликом — должен открыться соответствующий Request.

Мы не изменяем полосы drag/resize в обязательном опыте, чтобы итоговые даты оставались ровно заданными выше.

---

# Часть 6. Tree View

## 13. Открой `Training Category`

Через поиск Desk открой:

```text
Training Category
```

Перейди в Tree View.

Исходная структура после блока B:

```text
Operations
└── Internal

Analytics
└── External
```

Перемести:

```text
External
```

из `Analytics` под `Operations`.

Убедись, что дерево изменилось.

Затем **верни `External` обратно под `Analytics`**.

Итоговая структура должна снова быть:

```text
Operations
└── Internal

Analytics
└── External
```

Это показывает отличие Tree: меняется реальная parent-child структура Documents, а не только сортировка экрана.

---

## Проверка себя

Ответь без подсказки.

1. Какое поле использует `Request Status` Kanban Board?
2. Что изменилось в Document при переносе Kanban-карточки?
3. Почему `end_date` типа `Data` не появился в End Date Field Calendar View?
4. Какие поля использует `Request Course Calendar`?
5. Зачем понадобился `request_calendar.js`, если named Calendar View уже существует?
6. Какие два поля Gantt использует как границы полосы?
7. Почему Tree проверяем на `Training Category`, а не включаем `Is Tree` у `Request`?

---

## Состояние стенда после лабораторной

`Request` сохраняет все предыдущие поля и получает:

```text
Start Date  start_date  Date
End Date    end_date    Date
```

DocType setting:

```text
Is Calendar and Gantt = ✓
```

Существуют:

```text
Kanban Board: Request Status
  Reference Document Type: Request
  Field Name: status

Calendar View: Request Course Calendar
  Reference Document Type: Request
  Subject Field: subject
  Start Date Field: start_date
  End Date Field: end_date
  All Day: ✓
```

Standard calendar config существует по точному пути:

```text
apps/training/training/training/doctype/request/request_calendar.js
```

Шесть C12 Requests имеют фиксированные `start_date/end_date` из шага 7.

`C12-Open-Medium` восстановлен в:

```text
Status = Open
```

`Training Category` восстановлен в:

```text
Operations
└── Internal

Analytics
└── External
```

Это точное входное состояние [**главы 14**](../14_WORKSPACE_AND_DASHBOARD_BLOCKS.md).
