# Lab E. Print / Print Format / Letter Head / PDF

Lab E — отдельная лаборатория по штатной печати Frappe.

Работаем на уже существующем:

```text
Service Request
```

Новых предметных DocType не создаём.

В лаборатории создадим один полезный Standard Print Format приложения и один временный Letter Head текущего site.

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Что изучаем

В лаборатории нужны только штатные механизмы:

```text
Print View
Print Format
Print Format Builder
Letter Head
Print Settings
Print
PDF
Chrome PDF generator
Standard configuration
Git
```

Главная схема:

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
выбирается отдельно в Print View
```

Важно сразу разделить:

```text
Print Format
= как выглядит содержимое документа

Letter Head
= фирменная шапка / подвал конкретного site

PDF
= итоговый файл, а не metadata приложения
```

---

# 2. Проверить стенд

В терминале:

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
Developer Mode включён
```

Для Standard Print Format Developer Mode обязателен.

---

# 3. Выбрать тестовую Service Request

Нужна обычная существующая заявка, у которой заполнено большинство полей.

Например:

```text
Subject:     Air conditioner inspection
Location:    Room 101
Equipment:   <любое Equipment>
Description: Check noise and temperature
Priority:    High
Status:      In Progress
Target Date: <заполнено>
```

Точный номер заявки не важен.

Она нужна только как живой Document для preview.

---

# 4. Сначала посмотреть штатную печать без нашего формата

Открыть выбранную `Service Request`.

Через меню формы открыть:

```text
Print
```

Откроется штатный Print View.

Слева должны быть настройки, включая:

```text
Print Format
Language
Letter Head
```

Сверху доступны действия:

```text
Print
Full Page
PDF
Refresh
```

Пока ничего не настраивать.

Посмотреть текущий стандартный вывод.

Цель шага — увидеть, что Frappe умеет печатать Document ещё до создания собственного Print Format.

---

# 5. Зафиксировать границу Print View

Print View не является отдельным документом процесса.

Он читает:

```text
Service Request Document
+
Print Format
+
Letter Head
+
Print Settings
```

и строит представление для печати.

Не создаём:

```text
Printable Service Request
PDF Request
Service Request Print
```

---

# 6. Создать Standard Print Format

Войти как:

```text
Administrator
```

Через Awesomebar открыть:

```text
Print Format
```

Создать новый:

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

Оставить:

```text
Print Format Builder Beta = No
```

если поле доступно.

Сохранить.

Почему `Custom Format = No`:

в базовой лаборатории используем штатный Print Format Builder и не пишем собственный HTML/Jinja.

---

# 7. Почему Standard = Yes

`Service Request Summary` — не локальная настройка одного пользователя.

Это часть приложения:

```text
facility_ops
```

При:

```text
Standard = Yes
Module   = Facility Operations
```

Frappe в Developer Mode экспортирует Print Format в source app.

То есть здесь сознательно строим переносимую конфигурацию.

Letter Head позже сделаем иначе.

---

# 8. Открыть Print Format Builder

После сохранения Print Format нажать:

```text
Edit Format
```

Frappe откроет штатный:

```text
Print Format Builder
```

Не включать `Custom Format`.

Не открывать HTML/Jinja редактор для основной практики.

---

# 9. Собрать компактный макет

В Print Format Builder оставить только данные, полезные для печатной заявки.

Итоговый состав:

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

Логика расположения:

```text
Subject

Location | Equipment
Priority | Status
Target Date

Description
Attachment
```

Не пытаться повторить Desk Form один в один.

Печатная форма — отдельное представление тех же данных.

---

# 10. Не тащить технические поля

В итоговом макете не нужны:

```text
owner
creation
modified
modified_by
_doc_tags
_assign
_comments
```

Если нужен номер документа, его можно оставить как стандартный заголовок/идентификатор Print View.

Не создаём специальное поле `Request Number` только ради печати.

---

# 11. Проверить пустой Equipment

В нашей модели:

```text
Location = mandatory
Equipment = optional
```

Открыть ещё одну Service Request без Equipment и посмотреть Preview.

Печатный формат не должен становиться непригодным только потому, что Equipment пустой.

Это важная проверка самого макета, а не бизнес-логики.

---

# 12. Настроить базовые параметры Print Format

Вернуться в `Print Format → Service Request Summary`.

Оставить разумные базовые настройки:

```text
Margin Top:    15
Margin Bottom: 15
Margin Left:   15
Margin Right:  15
Page Number:   Bottom Center
PDF Generator: chrome
```

Не добавлять Custom CSS в базовой лаборатории.

Задача — сначала получить нормальный результат штатными средствами.

---

# 13. Почему используем chrome

В `v16.32.0` Print Format поддерживает выбор:

```text
wkhtmltopdf
chrome
```

Сам Frappe регистрирует штатный Chromium PDF generator.

Для учебного стенда используем:

```text
chrome
```

Не устанавливаем отдельный PDF-движок только ради лаборатории, если штатный Chromium уже работает на стенде.

---

# 14. Проверить Git после сохранения Standard Print Format

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Должен появиться source Standard Print Format.

Ожидаемый путь имеет вид:

```text
facility_ops/facility_operations/print_format/
  service_request_summary/
    service_request_summary.json
```

Посмотреть:

```bash
find facility_ops/facility_operations/print_format \
  -maxdepth 3 \
  -type f \
  -print \
  | sort
```

Затем:

```bash
sed -n '1,320p' \
  facility_ops/facility_operations/print_format/service_request_summary/service_request_summary.json
```

Не редактировать JSON вручную.

---

# 15. Что должно быть видно в JSON

Найти признаки:

```text
Service Request
Facility Operations
Standard = Yes
print_format_builder / format_data
pdf_generator = chrome
```

Точные служебные поля могут отличаться по наполнению Builder.

Главное:

```text
Print Format существует как Standard source object приложения
```

---

# 16. Не делать формат Default

На форме Print Format может быть кнопка:

```text
Set as Default
```

В этой лаборатории **не нажимать** её.

Для Standard DocType Frappe реализует это через изменение:

```text
default_print_format
```

поверх DocType с помощью `Property Setter`.

Нам не нужна скрытая глобальная настройка только ради лаборатории.

Формат будем выбирать явно в Print View.

---

# 17. Создать временный Letter Head

Через Awesomebar открыть:

```text
Letter Head
```

Создать:

```text
Letter Head Name: Facility Operations Training
Letter Head Based On: HTML
Footer Based On: HTML
Default Letter Head: No
Disabled: No
```

В Header HTML через штатный визуальный редактор набрать простой текст:

```text
FACILITY OPERATIONS
Training Site
```

В Footer HTML:

```text
Training document — facility-ops.localhost
```

Не писать JavaScript в Header Script / Footer Script.

---

# 18. Почему Letter Head не делаем Default

На site уже может существовать свой Default Letter Head.

Лаборатория не должна менять глобальную печать всех документов.

Поэтому:

```text
Facility Operations Training
Default Letter Head = No
```

и выбираем его вручную только в нужном Print View.

---

# 19. Почему Letter Head не кладём в app source

`Letter Head` — Setup Document текущего site.

В нашем сценарии он содержит локальное оформление учебного развёртывания:

```text
Training Site
facility-ops.localhost
```

Это не универсальная часть `facility_ops`.

Поэтому:

```text
Print Format
→ app configuration
→ source / Git

Letter Head
→ site-specific configuration
→ DB текущего site
```

В fixtures его не добавляем.

---

# 20. Проверить Git после создания Letter Head

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

Создание `Letter Head` само по себе не должно породить новый source-файл нашего app.

Изменение Git относится к Standard Print Format, а не к локальному Letter Head.

---

# 21. Проверить Print View с нашим форматом

Открыть тестовую `Service Request`.

Перейти:

```text
Print
```

В левом меню выбрать:

```text
Print Format = Service Request Summary
Letter Head  = Facility Operations Training
```

Нажать:

```text
Refresh
```

Проверить Preview.

Должны одновременно работать:

```text
наш макет полей
+
локальный Letter Head
```

---

# 22. Проверить Print без Letter Head

В Print View очистить:

```text
Letter Head
```

Обновить Preview.

Основная форма должна остаться той же:

```text
Service Request Summary
```

а шапка/подвал исчезнуть.

Главный вывод:

```text
Print Format
и
Letter Head
независимы друг от друга
```

---

# 23. Проверить обычный Print

Вернуть Letter Head.

Нажать:

```text
Print
```

Должен открыться обычный browser print flow.

Не сохранять этот результат в репозиторий.

`Print` — вывод представления на браузерный/системный механизм печати.

---

# 24. Сформировать PDF

Вернуться в Print View.

Нажать:

```text
PDF
```

Frappe должен сформировать PDF через выбранный штатный generator.

Открыть полученный PDF.

Проверить минимум:

```text
Subject читается
Location читается
Priority и Status на месте
Description не обрезан
Letter Head есть
номер страницы расположен ожидаемо
```

---

# 25. Отдельно проверить Footer

У `Letter Head.footer` в `v16.32.0` прямо указано, что footer корректно отображается именно в PDF.

Поэтому этот тест делаем не только по экранному Preview.

В сформированном PDF найти:

```text
Training document — facility-ops.localhost
```

Если footer отсутствует, открыть:

```text
Print Settings
```

и проверить связанные настройки header/footer.

Не исправлять проблему собственным HTML-шаблоном до проверки штатных Print Settings.

---

# 26. Проверить разные состояния Workflow

Сформировать Preview минимум для двух заявок:

```text
Status = New
Status = Closed
```

Print Format должен показывать текущее значение поля `status`.

Он не хранит копию Workflow state отдельно.

Если статус заявки изменился:

```text
Document
→ изменился
→ следующий Preview/PDF показывает новое значение
```

---

# 27. Проверить Attachment как обычное поле

Если в выбранной заявке есть Attachment, посмотреть его вывод в Print Format.

Не путать:

```text
Attachment field
```

с:

```text
вложением PDF в письмо
```

В этой лаборатории мы только печатаем значение Document.

Отправку PDF по email отдельно не автоматизируем.

---

# 28. Проверить права без изменения модели

Lab E не является вторым уроком по Role Permission Manager.

Но важно помнить:

```text
Print
```

— отдельное право Frappe.

Если под обычным пользователем Print недоступен, не добавлять обходные поля и не использовать Share как замену разрешения.

Правильное место проверки:

```text
Role Permission Manager
→ Service Request
→ Print
```

Для самой сборки Standard Print Format используем Administrator, потому что это setup/developer действие.

Для доказательства пользовательского доступа при необходимости проверять под реальным System User с соответствующим Print permission.

---

# 29. Не переходить на Custom HTML без причины

На Print Format существует:

```text
Custom Format = Yes
Print Format Type = Jinja / JS
HTML
Custom CSS
```

Это штатные возможности Frappe.

Но в базовой части Lab E их не используем.

Причина простая:

```text
Print Format Builder уже решает задачу
```

Собственный HTML/Jinja нужен только когда Builder объективно не может дать требуемый документ.

---

# 30. Что хранится где

После лаборатории различать:

```text
Service Request
→ working Document

Service Request Summary
→ Standard Print Format
→ app source / Git

Facility Operations Training
→ Letter Head
→ site-specific Setup Document

Print Settings
→ site configuration

PDF
→ итоговый файл вывода
```

Это пять разных вещей.

---

# 31. Проверить переносимость Print Format

Если clean site из L11 существует:

```text
facility-ops-clean.localhost
```

сначала commit Standard Print Format в app.

На исходном app:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
git diff

git add facility_ops/facility_operations/print_format/service_request_summary

git diff --cached

git commit -m "Add Service Request print format"
```

Затем на том же bench выполнить для clean site:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

На clean site должен появиться:

```text
Print Format: Service Request Summary
```

без ручного пересоздания.

---

# 32. Что не должно перенестись на clean site

После migrate не ожидаем автоматического появления:

```text
Facility Operations Training Letter Head
```

Потому что его не включали:

```text
в Standard source
в fixtures
```

Это правильный результат.

На другом развёртывании организация может использовать свой Letter Head.

---

# 33. Проверить Print Format на clean site

На clean site создать одну минимальную заявку:

```text
Subject:     Clean site print test
Location:    Main Site или существующий leaf
Priority:    Medium
Status:      New
```

Открыть:

```text
Print
```

Выбрать:

```text
Service Request Summary
```

Проверить Preview.

Даже без учебного Letter Head формат должен работать.

Это доказывает, что он не зависит от site-specific branding.

---

# 34. Очистить временный Letter Head

На исходном site открыть:

```text
Letter Head → Facility Operations Training
```

Удалить его штатно.

Поскольку:

```text
Default Letter Head = No
```

мы не должны оставлять глобальную настройку.

Проверить, что Print View продолжает работать с:

```text
Service Request Summary
```

без этого Letter Head.

---

# 35. Print Format оставляем в приложении

В отличие от Letter Head, `Service Request Summary` после лаборатории не удаляем.

Причина:

```text
это полезное переносимое представление
и оно не расширяет предметную модель
```

Постоянное ядро всё ещё состоит из:

```text
Facility Location
Equipment
Service Request
```

Print Format — configuration, а не четвёртый business DocType.

---

# 36. Проверить финальный Git

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
```

Ожидается:

```text
working tree clean
```

В Git остаётся:

```text
Service Request Summary Print Format
```

Не остаются:

```text
PDF-файлы
Letter Head текущего site
рабочие Service Request
```

---

# 37. Самостоятельная задача

Без подсказки изменить `Service Request Summary` через Print Format Builder так, чтобы:

```text
Subject был первым;
Location и Equipment находились рядом;
Priority и Status находились рядом;
Description находился отдельным широким блоком;
Target Date оставался видимым;
форма нормально выглядела и с пустым Equipment.
```

После изменения:

```text
Preview
PDF
Git diff
```

должны показать ожидаемый результат.

Не использовать Custom HTML/Jinja.

---

# 38. Что должен уметь объяснить студент

После Lab E без подсказки объяснить:

```text
что такое Print View;
что такое Print Format;
что делает Print Format Builder;
чем Print Format отличается от Letter Head;
почему Letter Head может быть site-specific;
почему Standard Print Format попадает в Git;
что делает Standard = Yes;
зачем Print Format нужен Module;
чем browser Print отличается от PDF;
какой PDF generator используется в лаборатории;
почему PDF-файл не является source приложения;
почему Set as Default может создать Property Setter;
почему в базовой форме не нужен собственный HTML/Jinja;
почему Print Format не является новым business DocType.
```

---

# 39. Финальная приёмка Lab E

Лаборатория пройдена, если выполнено всё:

```text
[ ] открыт штатный Print View Service Request
[ ] создан Service Request Summary
[ ] Print Format создан как Standard в Facility Operations
[ ] Custom Format не использован
[ ] макет собран через Print Format Builder
[ ] проверена заявка с Equipment
[ ] проверена заявка без Equipment
[ ] PDF Generator = chrome
[ ] создан временный Facility Operations Training Letter Head
[ ] Letter Head не сделан Default
[ ] Preview проверен с Letter Head
[ ] Preview проверен без Letter Head
[ ] browser Print проверен
[ ] PDF сформирован
[ ] footer проверен именно в PDF
[ ] Set as Default не использован
[ ] Standard Print Format найден в app source
[ ] Letter Head не появился в app source
[ ] Print Format перенесён на clean site через migrate
[ ] Letter Head не перенёсся автоматически
[ ] временный Letter Head удалён
[ ] Service Request Summary оставлен как полезная app configuration
[ ] рабочие Documents и PDF не попали в Git
[ ] git status clean
```

После Lab E постоянная предметная модель остаётся:

```text
Facility Location
Equipment
Service Request
```

Следующая лаборатория:

```text
Lab F — специальные Field Types и представления
```
