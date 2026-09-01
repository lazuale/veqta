# Lab E. Print / Print Format / Letter Head / PDF

Lab E изучает штатную печать Frappe на существующем `Service Request`.

Новых domain DocType не создаём.

Создаём:

```text
Service Request Summary
→ Standard Print Format приложения
```

и временно:

```text
Facility Operations Training
→ Letter Head текущего site
```

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Что изучаем

```text
Print View
Print Format
Print Format Builder
Letter Head
Print Settings
browser Print
PDF
Chrome PDF generator
Standard source vs site configuration
```

Архитектура:

```text
Service Request
      ↓
Print Format
      ↓
Print View
      ├── browser Print
      └── PDF

Letter Head
      ↓
выбирается отдельно
```

---

# 2. Preconditions

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
Developer Mode включён
working tree clean
```

Активным должен быть основной site, возвращённый L11:

```text
facility-ops.localhost
```

---

# 3. Выбрать валидную Service Request

Нужен существующий Document, например:

```text
Subject:     Air conditioner inspection
Location:    Room 101
Equipment:   <логично подходящий Equipment или пусто>
Description: Check noise and temperature
Priority:    High
Status:      In Progress
Target Date: заполнено или пусто
```

Важно: даже лабораторная печать не ослабляет H-01 — `Description` остаётся обязательным полем Service Request.

---

# 4. Посмотреть штатный Print View

Открыть Service Request → `Print`.

Посмотреть существующий вывод и элементы:

```text
Print Format
Language
Letter Head
Print
PDF
Refresh
```

Print View не создаёт копию бизнес-документа.

Он строится из:

```text
Service Request
+ Print Format
+ Letter Head
+ Print Settings
```

---

# 5. Создать Standard Print Format

Через `Print Format → New`:

```text
Name:             Service Request Summary
Print Format For: DocType
DocType:          Service Request
Module:           Facility Operations
Standard:         Yes
Custom Format:    No
Disabled:         No
PDF Generator:    chrome
```

Используем штатный Builder, не HTML/Jinja.

`Standard = Yes + Module` делает формат app-owned source configuration.

---

# 6. Собрать макет через Print Format Builder

Оставить полезные поля:

```text
Subject
Location
Equipment
Priority
Status
Target Date
Description
Attachment
```

Рекомендуемая компоновка:

```text
Subject

Location | Equipment
Priority | Status
Target Date

Description
Attachment
```

Не тащить без необходимости:

```text
owner
creation
modified
modified_by
_assign
_comments
```

Не создавать отдельное поле `Request Number`: системный `name` уже существует.

---

# 7. Проверить optional Equipment и Target Date

Сделать Preview минимум двух валидных Service Request:

```text
с Equipment
без Equipment
```

и при возможности:

```text
с Target Date
без Target Date
```

Print Format не должен ломаться из-за optional полей.

---

# 8. Базовые print settings формата

Оставить разумные настройки, например:

```text
Margin Top:    15
Margin Bottom: 15
Margin Left:   15
Margin Right:  15
Page Number:   Bottom Center
PDF Generator: chrome
```

Не добавлять Custom CSS без доказанной необходимости.

---

# 9. Chrome PDF generator

`v16.32.0` поддерживает штатный Chromium PDF generator.

Если Chromium ещё не подготовлен на bench, использовать штатную команду:

```bash
cd ~/frappe/facility-ops-bench
bench setup-chrome
```

Не подменять лабораторию самодельным PDF pipeline.

---

# 10. Проверить source Print Format

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short

find facility_ops/facility_operations/print_format \
  -maxdepth 3 -type f -print | sort
```

Ожидается source `service_request_summary`.

Посмотреть JSON только для чтения.

Не редактировать exported source вручную вместо UI.

---

# 11. Не нажимать Set as Default

`Set as Default` может создать изменение `default_print_format` через Property Setter.

Лаборатории не нужна скрытая глобальная настройка.

Формат выбираем явно в Print View.

---

# 12. Создать временный Letter Head

Создать:

```text
Letter Head Name: Facility Operations Training
Letter Head Based On: HTML
Footer Based On: HTML
Default Letter Head: No
Disabled: No
```

Header:

```text
FACILITY OPERATIONS
Training Site
```

Footer:

```text
Training document — facility-ops.localhost
```

Не использовать Header/Footer Script.

---

# 13. Почему Letter Head site-specific

Этот Letter Head содержит локальное оформление учебного deployment.

Поэтому:

```text
Service Request Summary
→ app-owned source

Facility Operations Training
→ site-specific Setup Document
```

Letter Head не включаем fixtures и не делаем Default.

---

# 14. Preview с Letter Head и без него

В Print View выбрать:

```text
Print Format = Service Request Summary
Letter Head  = Facility Operations Training
```

Refresh и проверить результат.

Затем убрать Letter Head и обновить снова.

Формат содержимого должен остаться тем же.

```text
Print Format
≠ Letter Head
```

---

# 15. Browser Print и PDF

Проверить:

```text
Print
```

как browser/system print path.

Затем:

```text
PDF
```

Проверить PDF минимум по:

```text
Subject
Location
Priority
Status
Description
Letter Head
Page Number
```

Footer проверить **именно в PDF**, а не только в preview.

---

# 16. Workflow state в печати

Сравнить Preview двух Documents, например:

```text
Status = New
Status = Closed
```

Print Format показывает текущее `Service Request.status`.

Он не хранит отдельную копию process state.

`Closed` здесь означает terminal Workflow state курса, а не отдельный DocStatus.

---

# 17. Attachment

Если `Service Request.attachment` заполнен, проверить его представление.

Не путать:

```text
Attach field в Document
```

с:

```text
отправкой PDF как email attachment
```

Email automation в Lab E не добавляется.

---

# 18. Print permission

Lab E не перестраивает permission architecture, но ученик должен понимать:

```text
Print
```

— отдельный permission type Frappe.

Если обычный пользователь не может печатать, проверять Role Permission Manager, а не создавать обходной механизм.

Administrator используется для создания Standard Print Format, но не как доказательство пользовательского доступа.

---

# 19. Не переходить на Custom HTML/Jinja без необходимости

Custom Format/Jinja — штатная возможность Frappe, но в базовой лаборатории не нужна.

Правило:

```text
Builder решает задачу
→ используем Builder

Builder объективно недостаточен
→ custom template становится отдельным advanced decision
```

---

# 20. Commit Standard Print Format

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff

git add facility_ops/facility_operations/print_format/service_request_summary

git diff --cached
git commit -m "Add Service Request print format"
git status
```

В Git не добавляются:

```text
PDF output
Letter Head site record
working Service Request
```

---

# 21. Проверить переносимость на clean site

Если `facility-ops-clean.localhost` существует:

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

На clean site должен появиться:

```text
Service Request Summary
```

без ручного пересоздания.

Letter Head:

```text
Facility Operations Training
```

не должен появиться автоматически.

---

# 22. Создать корректный clean-site print document

На clean site создать **валидную** заявку:

```text
Subject:     Clean site print test
Location:    существующая clean Location
Equipment:   существующий clean Equipment или пусто
Description: Проверка Standard Print Format на clean site
Priority:    Medium
```

`Status` получит:

```text
New
```

из default DocType/Workflow модели.

Не пропускать `Description` ради сокращённого примера.

Открыть Print и выбрать `Service Request Summary`.

Формат должен работать без учебного Letter Head.

---

# 23. Удалить временный Letter Head

На основном site открыть:

```text
Facility Operations Training
```

и удалить штатно.

Standard Print Format оставить.

После удаления Letter Head печать через `Service Request Summary` должна продолжить работать.

---

# 24. Final state

После Lab E:

```text
Core domain:
Facility Location
Equipment
Service Request
```

Постоянно добавлено только:

```text
Service Request Summary
→ presentation configuration
```

Не осталось:

```text
Facility Operations Training Letter Head
PDF files в Git
новых domain entities
```

Это важное различие:

```text
domain rollback
≠ обязательный byte-identical source rollback
```

Lab E сознательно оставляет полезный Standard Print Format.

---

# 25. Приёмка

Лаборатория принята, если:

- открыт штатный Print View;
- создан `Service Request Summary` как Standard app-owned Print Format;
- используется Print Format Builder;
- Custom HTML/Jinja не нужен;
- проверены optional Equipment/Target Date;
- `PDF Generator = chrome`;
- при необходимости использован штатный `bench setup-chrome`;
- создан временный non-default Letter Head;
- Preview проверен с Letter Head и без него;
- browser Print проверен;
- PDF сформирован;
- Footer проверен в PDF;
- `Set as Default` не использован;
- Standard Print Format попал в source/Git;
- Letter Head остался site-specific;
- clean-site тестовая заявка содержит обязательный Description;
- Print Format приехал на clean site через app sync/migrate;
- Letter Head не приехал;
- временный Letter Head удалён;
- `Service Request Summary` оставлен как presentation configuration;
- Git clean.

После Lab E переходим к **Lab F — специальные Field Types и представления**.
