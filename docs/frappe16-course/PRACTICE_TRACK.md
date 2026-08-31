# Практический трек курса Frappe 16

Этот файл задаёт **сквозную лабораторную работу** для всего учебника.

Он нужен, чтобы главы не превращались в энциклопедию возможностей Frappe.

Главная идея курса:

```text
прочитал
→ сделал руками
→ увидел результат
→ изменил условие
→ увидел другое поведение
→ понял границу механизма
```

Основной стенд описан в [00_LAB_SETUP.md](00_LAB_SETUP.md).

---

# 1. Сквозной объект курса

Главный учебный DocType:

```text
Request
```

Он специально начинается очень простым и постепенно получает новые возможности.

К концу курса через один и тот же объект ученик должен руками увидеть:

```text
metadata
Document lifecycle
Form
List
Kanban
Calendar
permissions
sharing
assignment
workflow
notifications
versions
attachments
reports
import/export
Web Form
REST API
RPC
Client Script
Server Script
controller
hooks
background jobs
scheduler
fixtures
migrations
tests
```

Это лучше, чем создавать новый бессвязный пример в каждой главе.

---

# 2. Исходное состояние

После главы 0 есть:

```text
Bench:  frappe16-course-bench
Site:   learn.localhost
Apps:   frappe, training
Module: Training
```

И больше ничего специально создавать не нужно.

---

# 3. Блок A — карта Frappe

## Глава 1

Практика:

```text
открыть каталог Bench
найти apps/
найти sites/
найти apps/frappe/
найти apps/training/
выполнить bench --site learn.localhost list-apps
```

Результат:

> ученик физически видит разницу Bench / Site / App, а не только читает определения.

## Глава 2

Практика:

```text
открыть Desk
найти через Awesome Bar User
найти DocType
найти Workspace
перейти между Desktop / Sidebar / Workspace
```

Проверка:

> ученик должен уметь найти системный объект без инструкции «нажми третью кнопку слева».

## Глава 3

Практика:

```text
bench --site learn.localhost list-apps
ls apps
открыть Installed Applications / Apps в Desk, если применимо
сравнить frappe и training
```

Эксперимент:

> убедиться, что ERPNext отсутствует, но Framework при этом полностью работает.

---

# 4. Блок B — модель данных

## Глава 4 — DocType

Создать Standard DocType:

```text
Name: Request
Module: Training
```

Минимальные поля:

```text
Subject      Data
Description  Small Text
Status       Select
Due Date     Date
```

Создать 2–3 Documents.

После Save открыть:

```bash
find apps/training -iname '*request*' -o -iname 'request*'
```

Ученик должен увидеть одновременно:

```text
DocType в Desk
таблицу/records в Frappe
файлы Standard DocType в App
```

## Глава 5 — DocField

На `Request` последовательно попробовать:

```text
Data
Select
Date
Check
Int
Text Editor
Attach
Link
```

Для нескольких полей изменить:

```text
Mandatory
Read Only
Hidden
In List View
Default
Depends On
```

Главный эксперимент:

> менять ровно одно свойство, обновлять Form и наблюдать разницу.

## Глава 6 — Naming

Сначала создать Request с обычным naming.

Затем настроить отдельную naming scheme и создать ещё несколько записей.

Нужно увидеть:

```text
name
Title Field
человеческий заголовок
системный идентификатор
```

## Глава 7 — Link / Fetch From

Добавить в `Request`:

```text
Responsible   Link → User
Responsible Name  Data / Fetch From
```

Выбрать разных Users и увидеть автоматическую подстановку.

Потом временно сломать `Fetch From`, убедиться, что значение перестало приходить, и исправить.

## Глава 8 — Child Table

Создать:

```text
Request Item
```

как Child Table.

Поля:

```text
Title
Qty
Rate
Amount
```

Добавить Table в `Request`.

Создать Document с несколькими rows.

Проверить:

```text
child row не существует как обычный независимый master Document
parent хранит набор rows
```

## Глава 9 — специальные DocType

Создать маленькие экспериментальные объекты:

```text
Training Settings → Single
Training Category → Tree
```

Не пытаться делать их полноценной бизнес-моделью.

Цель — руками почувствовать отличие режимов.

## Глава 10 — docstatus lifecycle

Создать отдельный учебный Submittable DocType, например:

```text
Approval Record
```

Выполнить:

```text
Draft
→ Submit
→ попробовать изменить обычное поле
→ Cancel
→ Amend
```

Ученик должен увидеть `docstatus` не как теорию, а как реальный lifecycle.

---

# 5. Блок C — интерфейс

## Глава 11 — Form View

На `Request`:

```text
Section Break
Column Break
Tab Break
описания полей
read-only
mandatory
attachments/timeline area
```

Цель — построить форму и сразу посмотреть, как metadata влияет на UI.

## Глава 12 — List View

Создать 10–15 Request с разными Status и Due Date.

Практика:

```text
filters
saved filters
sort
page length
list columns
bulk actions
```

## Глава 13 — Kanban / Calendar / Gantt / Tree

Не просто открыть экраны.

Нужно подготовить подходящие данные и проверить:

```text
Kanban → изменить колонку и увидеть изменение Document
Calendar → увидеть записи по Date
Gantt → проверить требуемые поля и границы
Tree → использовать Training Category
```

## Глава 14 — Workspace

Создать учебный Workspace:

```text
Training
```

Добавить:

```text
Shortcut → Request
Quick List
Number Card
Chart
```

К концу главы ученик должен иметь собственную маленькую рабочую область.

## Глава 15 — Customize Form

Изменить существующий DocType через Customize Form.

Сравнить:

```text
Standard metadata файла App
vs
Custom Field / Property Setter на Site
```

Пока без глубокого Git-разбора.

## Глава 16 — Desk Page и границы UI

Открыть несколько штатных Page/Workspace экранов и определить:

```text
что можно собрать metadata
что требует Client Script
что уже требует Page/App code
```

Практический результат — не написание большого frontend, а умение увидеть границу.

---

# 6. Блок D — пользователи и права

Создать учебных пользователей, например:

```text
student.user@example.test
student.manager@example.test
```

и роли:

```text
Training User
Training Manager
```

Не использовать реальные email для учебной модели доступа.

## Глава 17

Назначить разные роли двум пользователям и войти в отдельном private/incognito окне.

## Глава 18

Настроить Role Permission Manager для `Request`.

Проверить реальные действия:

```text
Read
Create
Write
Delete
```

под обоими пользователями.

## Глава 19

Добавить поле с другим Permission Level.

Проверить:

```text
один пользователь видит
другой не видит / не может менять
```

## Глава 20

Настроить User Permission через подходящий Link-объект и проверить фильтрацию записей.

## Глава 21

Создать два Request разными owners.

Проверить:

```text
owner restriction
Share
Unshare
```

## Глава 22

Сделать несколько намеренно конфликтующих permission-настроек и научиться определять, какой слой доступа реально сработал.

---

# 7. Блок E — работа и процессы

## Глава 23

Назначить Request другому пользователю через Assignment.

Проверить созданный `ToDo` и снять назначение.

## Глава 24

Создать Assignment Rule и несколько новых Request.

Проверить автоматическое распределение.

## Глава 25

На живом объекте сравнить:

```text
обычный field Status
Workflow State
```

## Глава 26

Создать Workflow:

```text
Draft
→ Review
→ Approved
→ Rejected
```

Проверить transition разными ролями.

Обязательно попытаться сделать запрещённый transition.

## Глава 27

Создать Notification на изменение Request.

Если реальный SMTP ещё не настроен, сначала проверить создание Email Queue/Communication и сам trigger; локальный SMTP-синк подключается в практической части email-главы.

## Глава 28

Создать простой повторяемый учебный документ и увидеть, что делает Auto Repeat без собственного scheduler code.

---

# 8. Блок F — возможности документа

## Глава 29

На одном Request:

```text
добавить comments
mention пользователя
посмотреть Timeline
```

## Глава 30

Включить/использовать Track Changes.

Несколько раз изменить разные поля и сравнить Version.

## Глава 31

Прикрепить:

```text
текстовый файл
картинку
```

Проверить public/private поведение File.

## Глава 32

Настроить безопасный локальный тест отправки почты либо отдельный учебный SMTP account.

Отправить письмо из Frappe и найти созданный `Communication`.

Никаких реальных массовых рассылок.

## Глава 33

Создать Print Format для `Request`.

Распечатать HTML, затем проверить PDF-механизм и системную зависимость PDF renderer.

---

# 9. Блок G — данные и аналитика

К этому моменту в `Request` должно быть хотя бы 30–50 учебных записей.

Их можно быстро создать импортом.

## Глава 34

Собрать Report Builder:

```text
Status
Responsible
Due Date
filters
grouping
```

## Глава 35

Создать безопасный Query Report и увидеть, какие данные реально возвращает SQL.

## Глава 36

Создать Script Report и сравнить его с Query Report.

## Глава 37

На базе данных Request сделать:

```text
Number Card
Dashboard Chart
```

и разместить их на Training Workspace.

## Глава 38

Экспортировать Requests, изменить CSV/XLSX и импортировать обратно.

Обязательно сделать один файл с ошибкой и разобрать import feedback.

---

# 10. Блок H — внешние интерфейсы

## Глава 39

Создать Web Form для `Request`.

Проверить:

```text
создание как Guest / authenticated user
поля формы
созданный Document в Desk
```

## Глава 40

Создать простейшую website/portal поверхность и увидеть отличие от Desk и Web Form.

## Глава 41

Через `curl` выполнить REST операции над `Request`:

```text
GET list
GET document
POST create
PUT update
DELETE test document
```

## Глава 42

Вызвать whitelisted method и сравнить RPC с resource REST API.

## Глава 43

Создать отдельного учебного API User / credentials и выполнить authenticated запрос без браузерной session.

---

# 11. Блок I — low-code и разработка

## Глава 44 — Client Script

На `Request` сделать руками:

```text
условный mandatory
show/hide
Link filter
custom button
client calculation
```

Потом вызвать тот же Save через REST и увидеть, какие client-only правила не работают на сервере.

Это обязательный эксперимент.

## Глава 45 — Server Script

На `Request` сделать минимум три эксперимента:

```text
DocType Event validation
API Server Script
Scheduler Event
```

Для validation:

```text
Status = Closed
→ Result обязательно
```

Проверить одинаковый отказ через:

```text
Desk
REST API
```

Именно здесь ученик должен руками увидеть разницу Client Script и Server Script.

## Глава 46 — Standard vs Custom

Сравнить реальные объекты, которые уже накопились на Site:

```text
Standard Request в apps/training
Custom Field / Property Setter
Client Script в БД
Server Script в БД
```

## Глава 47 — Developer Mode

Мы уже включили его в главе 0.

Теперь:

```text
выключить
попробовать создать Standard DocType
увидеть отказ
включить обратно
повторить
```

## Глава 48 — App

Разобрать уже существующий `training`:

```text
pyproject.toml
hooks.py
modules.txt
public/
templates/
training/training/
```

Затем создать второй маленький App с нуля и удалить его после эксперимента либо оставить для итоговой практики.

## Глава 49

Открыть реальные файлы `Request` и связать:

```text
JSON metadata
Python file
JS file
Desk behavior
```

## Глава 50

Добавить простую server validation в Python controller.

Проверить через Desk и REST.

## Глава 51

Добавить один безопасный hook и увидеть, когда он вызывается.

---

# 12. Блок J — серверная инфраструктура

## Глава 52

Открыть:

```bash
bench --site learn.localhost console
```

и руками выполнить несколько `frappe.get_doc`, `frappe.get_list`, `frappe.db.get_value`.

## Глава 53

Поставить маленькую задачу в background queue и увидеть worker execution.

## Глава 54

Создать scheduled job и вручную проверить его регистрацию/выполнение.

## Глава 55

Сделать минимальный realtime event и увидеть сообщение в browser UI.

## Глава 56

Экспортировать одну безопасную конфигурационную сущность как fixture и увидеть файл в App.

## Глава 57

Создать маленький patch, выполнить migrate и проверить идемпотентность.

## Глава 58

Написать первый automated test для `Request` и намеренно заставить его упасть, затем исправить.

---

# 13. Блок K — Bench и эксплуатация

## Глава 59

Через реальный стенд разобрать основные команды Bench.

## Глава 60

Сравнить:

```text
common_site_config.json
site_config.json
```

и изменить одну безопасную настройку.

## Глава 61

Установить/удалить дополнительный учебный App либо локальную копию собственного экспериментального App.

## Глава 62

Сделать изменение metadata, выполнить `bench migrate`, увидеть результат.

## Глава 63

Во время `bench start` сопоставить процессы:

```text
web
socketio
scheduler
workers
redis
```

с тем, что происходит в браузере и очередях.

## Глава 64

Создать контролируемую ошибку и найти её в правильном логе.

## Глава 65

Сделать backup учебного Site, изменить данные, восстановить backup и проверить возврат состояния.

## Глава 66

Разобрать production topology на отдельном тестовом контексте, не превращая WSL dev-стенд в якобы production.

---

# 14. Блок L — итоговая практика

Здесь ученик перестаёт следовать пошаговому рецепту и воспроизводит механику сам.

## Главы 67–71

Нужно создать **новое маленькое приложение с чистого листа**:

```text
новый App
новый Site или чистый test Site
несколько DocType
permissions
workflow
report
Client Script
server logic
API
test
migration
```

После этого приложение устанавливается на чистый Site.

Главный экзамен:

> система должна воспроизводиться не потому, что «на старом Site что-то настроено руками», а потому что ученик понимает, что относится к App, что к Site и что нужно перенести.

## Глава 72

Ученик для нескольких требований должен самостоятельно выбрать уровень:

```text
metadata
штатный low-code механизм
Client Script
Server Script
App code
custom frontend
```

и объяснить выбор.

---

# 15. Формат практики внутри главы

Каждая глава должна содержать явные секции:

```text
## Что должно быть готово
## Что сегодня делаем
## Практика
## Ожидаемый результат
## Эксперимент
## Типичная ошибка
## Проверка себя
## Состояние стенда после главы
```

Не каждая глава обязана использовать именно эти заголовки дословно, но все эти функции должны присутствовать.

---

# 16. Запрет на «практику понарошку»

Не считается практикой формулировка:

```text
«попробуйте создать несколько документов»
```

без указания:

```text
какие именно
с какими значениями
что должно измениться
где это увидеть
как понять, что механизм сработал
```

Хорошая практика выглядит так:

```text
1. Создай Request A со Status = Open.
2. Создай Request B со Status = Closed.
3. Открой List View.
4. Поставь фильтр Status = Open.
5. Должен остаться только Request A.
6. Удали фильтр.
7. Оба документа снова должны быть видны.
```

---

# 17. Главный критерий качества курса

После каждой главы ученик должен уметь ответить не только:

```text
«что такое механизм X?»
```

но и:

```text
где его найти
как создать минимальный пример
как проверить, что он сработал
какое изменение сломает/изменит поведение
где заканчиваются его возможности
```

Если этого нет — глава ещё не закончена.
