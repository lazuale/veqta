# S03. Построить простую сводку через Report Builder

После S02 менеджер умеет находить нужные Rentals в стандартном List. Теперь появляется новое требование:

> Менеджеру нужна сохраняемая сводка по Rental: сгруппировать записи по Status и увидеть количество Rentals в каждой группе.

Это уже отчётная задача, но для неё пока не нужны Python или SQL. Frappe предоставляет `Report Builder` для отчётов по одному DocType и его Child Tables.

Одновременно впервые появляется необходимость в стандартном permission `Report` на `Rental`.

Связанные материалы:

- [`S02_LIST_VIEW.md`](S02_LIST_VIEW.md);
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md);
- [`../../../frappe-architecture-standard/04_SECURITY.md`](../../../frappe-architecture-standard/04_SECURITY.md);
- [`../../../frappe-architecture-standard/09_UI_REPORTING.md`](../../../frappe-architecture-standard/09_UI_REPORTING.md).

Первичный источник:

- https://docs.frappe.io/framework/user/en/desk/reports/report-builder

---

## 1. Почему `Report` permission появляется только сейчас

В первом практикуме `Rental Manager` получил CRUD-права на `Rental`, но отдельного требования к отчётам ещё не было.

Теперь оно появилось.

Требуемая строка Standard DocType Permissions становится такой:

```text
Rental Manager
Read   : yes
Create : yes
Write  : yes
Delete : yes
Report : yes
```

`Rental Operator` на этом этапе `Report` не получает: текущая отчётная задача поставлена для менеджера.

Не включайте дополнительные permission-флаги просто потому, что они существуют в таблице DocPerm.

---

## 2. Добавить `Report` permission в Standard DocType

Войдите как `Administrator`.

Откройте:

```text
DocType → Rental
```

В таблице `Permissions` найдите строку:

```text
Rental Manager
```

Включите:

```text
Report : yes
```

Остальные значения оставьте как после S01.

Сохраните `Rental`.

---

## 3. Проверить изменение App

В терминале:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
git status --short
```

Ожидается изменение:

```text
rental_training/rental_training/doctype/rental/rental.json
```

Посмотрите diff:

```bash
git diff -- rental_training/rental_training/doctype/rental/rental.json
```

В строке `Rental Manager` должен появиться `report`.

Это обязательное состояние приложения, поэтому оно находится в Standard metadata.

---

## 4. Открыть Report View для Rental

Войдите под:

```text
manager@example.test
```

Откройте `Rental` и переключитесь в стандартное отчётное представление / Report Builder текущего Frappe v16.

Нужная задача:

```text
показать Status
сгруппировать по Status
посчитать количество Rentals
```

Не добавляйте числовое поле в `Rental` только ради демонстрации `Sum` или `Average`.

Текущая предметная модель не содержит такого показателя, поэтому для этого практикума достаточно агрегата:

```text
Count
```

---

## 5. Построить первую сводку

Настройте отчёт так, чтобы он показывал количество Rentals по каждому `status`.

Ожидаемый смысл результата:

```text
Planned  → N
Active   → N
Returned → N
```

Точные числа зависят от того, остались ли на Site дополнительные Rentals из первого практикума.

Если нужен строго контрольный результат, добавьте фильтр по периоду:

```text
Start Date <= 2026-09-10
End Date   >= 2026-09-01
```

Тогда выборка будет ограничена тем же диапазоном, который используется в S00.

---

## 6. Построить вторую рабочую группировку

Переключите группировку на:

```text
Customer
```

и снова используйте:

```text
Count
```

Цель — увидеть, что Report Builder решает обычные задачи:

```text
выбрать колонки
применить filters
задать ordering
сгруппировать
посчитать записи
```

без собственного серверного кода.

---

## 7. Сохранить пользовательский отчёт

Сохраните один удобный вариант Report Builder, например:

```text
Rental Count by Status
```

Это **Custom Report на текущем Site**, а не обязательный Standard Report приложения.

Поэтому его смысловая принадлежность:

```text
удобное сохранённое представление пользователя/Site
→ Site-owned
```

а не:

```text
обязательная часть работы rental_training
→ App-owned
```

На S05 появится другой класс требования: отчёт будет обязательной функциональностью App, и тогда он станет Standard Report в исходниках приложения.

---

## 8. Проверить, что Custom Report не стал файлом App

Вернитесь в терминал:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training
git status --short
```

После S03 в Git должно быть только осознанное изменение Standard DocType Permissions, если вы его ещё не закоммитили.

Сохранение пользовательского Report Builder само по себе не должно создавать обязательные файлы App.

Это полезное различие:

```text
Rental Manager → Report permission
→ обязательная модель App

Rental Count by Status
→ пользовательский Custom Report
→ состояние Site
```

---

## 9. Зафиксировать permission в Git

Если diff содержит только ожидаемое изменение `Rental` metadata:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git add rental_training/rental_training/doctype/rental/rental.json
git commit -m "feat: allow rental manager reports"
```

Custom Report из Report Builder не добавляйте в fixtures только ради того, чтобы всё созданное на Site оказалось в Git.

---

## 10. Увидеть границу Report Builder

Теперь появляется следующее требование:

> Нужно программно читать Rental в пользовательском контексте и быть уверенным, что оператор не получает чужие Documents.

Это уже не вопрос представления таблицы.

Также позже понадобится обязательный отчёт, который связывает:

```text
Rental
Rental Item
Equipment
Customer
```

Report Builder остаётся правильным решением текущей простой сводки, но не обязан закрывать все будущие запросы.

---

## Результат этапа

К концу S03:

```text
Report permission появился только после отчётного требования
Rental Manager может использовать отчётное представление Rental
простая сводка решена Report Builder без кода
текущему Rental достаточно Group By + Count
Custom Report остался Site-owned
обязательная permission-модель осталась App-owned
```

На S04 мы отойдём от UI и проверим фундаментальную границу чтения: почему `get_list`, `get_all` и `get_doc` нельзя считать взаимозаменяемыми способами получить те же данные.
