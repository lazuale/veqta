# Управление работой v1: проверка на живом Frappe Site

Этот сценарий проверяет Work Management Lab на реальном Frappe v16 Site после сборки по [Руководству по настройке](setup-guide.md).

Цель — проверить фактическую семантику выбранных штатных механизмов и воспроизводимость App. Не нужно повторно тестировать весь Frappe.

## Стенд

App:

```text
veqta_work_management
```

Пользователи:

```text
work-a@example.test  — VEQTA Work User
work-b@example.test  — VEQTA Work User
plain@example.test   — System User без VEQTA Work User
```

Рабочий интерфейс — `Russian (ru)`.

## 1. Developer baseline

```bash
bench --site <site> list-apps
bench --site <site> show-config
```

Проверьте:

```text
App: veqta_work_management
Module: VEQTA Work Management
DocType: Work Item
Custom: No
Naming: WI-.#####
Is Calendar and Gantt: No
```

Первый документ должен получить имя вида:

```text
WI-00001
```

В каталоге App проверьте, что standard metadata реально появилась в файлах App, а не осталась только в DB development Site.

## 2. Русская локализация

После Gettext compile проверьте уникальные строки App:

```text
Work Item             → Работа
VEQTA Work Management → Управление работой
VEQTA Work User       → Участник управления работой
VEQTA Work Items      → Работы
```

Общие строки Frappe, включая `Due Date`, не должны переопределяться только ради Lab, если core translation уже подходит. Технические значения данных не меняются.

## 3. Общая очередь

Под `work-a@example.test` создайте Work Item.

Под `work-b@example.test` проверьте:

- документ виден;
- его можно открыть и изменить;
- `plain@example.test` документ не видит.

Это проверяет Role/DocPerm общей очереди.

## 4. Assign To

Под `work-b@example.test` выполните:

```text
Assign To
→ Assign to me
```

Проверьте:

- создаётся связанный `ToDo`;
- `reference_type = Work Item`;
- `reference_name = WI-...`;
- Work Item остаётся `Open`;
- `priority` в Assign To dialog по умолчанию соответствует `Work Item.priority` для `Low / Medium / High`;
- после назначения `ToDo.priority` соответствует выбранному в dialog значению;
- стандартный фильтр `Assigned To → Me` находит документ.

Активный ToDo фиксирует персональную ответственность. Он не должен интерпретироваться как отдельное сохранённое состояние `In Progress` Work Item.

## 5. Общий срок и Complete By

Создайте Work Item с `due_date`, отличным от текущей даты.

Сделайте два назначения последовательно.

### Вариант A: Complete By не задан

Оставьте `Complete By` пустым.

Стандартный FieldGroup не включает null-поле `date` в результат dialog `get_values()`. Поэтому Assign To получает args без `date`, и для Frappe v16.33.0 ожидается текущая дата из backend default `nowdate()`.

Проверьте фактический `ToDo.date` и убедитесь, что:

```text
Work Item.due_date не копируется в ToDo.date
```

### Вариант B: Complete By задан явно

Укажите дату, отличную от `Work Item.due_date`.

Проверьте, что ToDo хранит именно явно выбранный `Complete By`, а Work Item не меняется.

Это подтверждает две независимые ответственности:

```text
Work Item.due_date = общий срок работы
ToDo.date          = срок конкретного назначения
```

## 6. Независимость `Work Item.status` и `ToDo.status`

Создайте назначенный Work Item и последовательно проверьте:

```text
Work Item Open → Waiting
Work Item Waiting → Open
Work Item Open → Closed
Work Item Closed → Cancelled
```

Зафиксируйте фактическое состояние связанного ToDo после каждого изменения.

Baseline не ожидает автоматической синхронизации. Если Frappe сам меняет ToDo каким-либо штатным механизмом, это фиксируется как факт версии.

Затем отдельно завершите своё ToDo и убедитесь, что Work Item не меняет `status` автоматически.

Это ключевой эксперимент: только его результат и реальная потребность могут стать основанием для будущего lifecycle-кода.

## 7. Waiting

На назначенной работе добавьте комментарий и переведите `Open → Waiting`.

Проверьте:

- назначение не теряется;
- Timeline сохраняет контекст;
- возврат `Waiting → Open` не требует отдельной сущности ожидания.

## 8. Пользователь без доступа

Под `plain@example.test` попробуйте открыть List и прямую ссылку Work Item.

Затем под `work-a@example.test` попробуйте назначить Work Item на `plain@example.test`.

Зафиксируйте фактическое поведение `Assign To` / `DocShare` текущего Site, включая влияние System Settings на document sharing.

Baseline не считает назначение пользователя без прикладного доступа штатным способом выдачи роли `VEQTA Work User`. Если назначение не проходит — это не основание расширять DocPerm. Если Frappe выдаёт document share, отдельно проверьте, какой доступ фактически получил пользователь и соответствует ли это выбранной security boundary.

## 9. Complete и Remove assignment

Назначьте Work Item на `work-a@example.test`.

### Завершение чужого назначения

Под `work-b@example.test` попробуйте завершить ToDo `work-a@example.test` через действие Complete.

Для v16.33.0 ожидается отказ: `frappe.desk.form.assign_to.close` разрешает завершить assignment только самому assignee.

### Снятие чужого назначения

Снова создайте назначение на `work-a@example.test`.

Под `work-b@example.test` снимите его через стандартное Remove/Cancel assignment.

Для baseline ожидается, что операция доступна, потому что `work-b@example.test` имеет Write на исходный Work Item. После операции связанный ToDo должен перейти в `Cancelled`.

Это ожидаемая семантика доверенной общей очереди. Если реальный процесс требует запретить снятие чужих назначений, это отдельное server-side требование, а не повод менять общий DocPerm без формулировки правила.

## 10. List View

Проверьте стандартный List View без custom `work_item_list.js`:

- Subject;
- Status;
- Priority;
- Due Date;
- отображение назначений;
- сортировку `creation DESC`;
- `Assigned To → Me`.

Проверьте обычные фильтры:

```text
status in Open, Waiting
status = Open
status = Waiting
```

Отдельно оцените, действительно ли стандартного List View недостаточно визуально. Только подтверждённый UX-пробел является основанием для `<doctype>_list.js`.

Внутренний `_assign` не используется как собственное поле App или authorization boundary.

## 11. Kanban

Откройте `VEQTA Work Items` (`Работы`).

Проверьте колонки:

```text
Open
Waiting
Closed
Cancelled
```

Карточка должна показывать `priority` и `due_date` через штатные Kanban Settings.

Перетаскивание должно менять только `Work Item.status`. Никакого собственного Kanban/lifecycle-кода нет.

Под обычным `VEQTA Work User` проверьте, что shared board открывается и перемещение Work Item опирается на Write к исходному DocType, а не на отдельное прикладное право доски.

## 12. Number Cards

Проверьте четыре standard cards:

```text
Активные работы
Ожидание
Высокий приоритет
Срок сегодня
```

Сравните каждое число с обычным permission-aware List View по тем же фильтрам.

### Эксперимент «Без исполнителя»

На текущем patch-release отдельно проверьте временную Number Card:

```text
status = Open
Assigned To Is Not Set
```

Она не входит в обязательное состояние App. Добавлять собственное поле `assignee` ради неё нельзя.

## 13. Dashboard Chart

`VEQTA New Work Items` должен:

- считать Work Item по `creation`;
- показывать последний месяц по дням;
- не трактоваться как производительность пользователя.

Сравните данные с permission-aware List/Report по Work Item.

## 14. Auto Repeat без assignee

Создайте Work Item:

```text
Status: Waiting
Priority: High
Due Date: любая дата
Links: одна тестовая связь
```

Создайте Auto Repeat без Assignee.

Новый экземпляр должен иметь:

```text
subject      → скопирован
description  → скопирован
priority     → High
status       → Open
due_date     → пусто
links        → пусто
```

Если фактическое поведение отличается, сначала проверяется metadata `No Copy` и exact v16 source.

## 15. Auto Repeat с assignee

Если на стенде проверяется повторяющаяся работа с фиксированным исполнителем, используйте встроенный `Auto Repeat.assignee`, а не собственный hook.

Проверьте:

- новый Work Item создаётся штатным Auto Repeat;
- для нового документа создаётся ToDo выбранного assignee;
- назначение относится к новому Work Item, а не копируется как поле исходного документа;
- `Work Item.status` остаётся независимым от ToDo.

Если нужен не фиксированный пользователь, а автоматический выбор, этот сценарий должен проверяться через `Assignment Rule`, а не через собственный scheduler.

## 16. Assignment Rule как нативная альтернатива

Assignment Rule не входит в обязательный baseline, поэтому этот тест выполняется только при соответствующем требовании.

Если требуется автоматически передавать срок Work Item в назначение, временно создайте Assignment Rule для `Work Item` с:

```text
due_date_based_on = due_date
```

Проверьте, что штатная механика:

- создаёт ToDo с датой из `Work Item.due_date`;
- обновляет дату открытого ToDo при изменении поля, если assignment создан этим Rule.

Если это закрывает требование, собственная Work Item → ToDo синхронизация не нужна.

Для автоматического выбора исполнителя отдельно проверяются только нужные стратегии Frappe:

```text
Round Robin
Load Balancing
Based on Field
Weighted Distribution
```

## 17. Workspace

Откройте `VEQTA Work Management` / `Управление работой`.

Проверьте:

- Новая работа;
- Список работ;
- Доска;
- четыре Number Cards;
- chart `Новые работы`;
- секции `Действия`, `Текущее состояние`, `Поступление`.

Интерфейс должен быть читаемым без Custom HTML/CSS. Calendar/Gantt shortcut отсутствует.

Отдельный Workspace Sidebar не требуется для прохождения baseline. Проверьте, что штатная module navigation Frappe делает Workspace и основные сущности доступными без ручной site-only настройки.

## 18. Communication

Добавьте комментарий и, если на Site уже существует связанный `Communication`, проверьте его отображение в Timeline.

Не меняйте permissions только ради теста. Под `VEQTA Work User` убедитесь, что отсутствие permission `Email` не мешает обычной работе Work Item и что документация не обещает отдельный почтовый workflow.

## 19. Metadata и fixture

В каталоге App:

```bash
git status
git diff
```

Ожидается:

```text
standard metadata:
- Work Item
- Workspace
- Number Cards
- Dashboard Chart
- locale/main.pot
- locale/ru.po

fixture:
- Work Management Kanban Board

не должно быть:
- отдельного fixture Role только ради VEQTA Work User
- Work Item / ToDo user data
- global Saved Filters
- custom List JS
- ToDo hooks
- lifecycle-кода Work Item
- Workspace Sidebar без отдельного требования
```

Проверьте, что fixture не захватил посторонние Kanban Boards.

## 20. Reinstall test

На втором чистом Site:

```bash
bench --site <second-site> install-app veqta_work_management
bench --site <second-site> migrate
bench --site <second-site> clear-cache
```

Без ручной пересборки должны появиться:

- standard Work Item;
- naming `WI-.#####`;
- Role `VEQTA Work User` и DocPerm;
- Kanban fixture;
- Number Cards;
- Dashboard Chart;
- Workspace;
- Gettext localization.

Пользовательские данные первого Site переноситься не должны.

Отдельно подтвердите, что Role появилась из standard metadata/permissions, а не потому, что случайно осталась в DB второго Site.

## 21. Runtime без Developer Mode

```bash
bench --site <site> set-config developer_mode 0
bench --site <site> clear-cache
```

Под обычным `VEQTA Work User` повторите создание Work Item, Assign To, изменение status, List, Kanban, Number Cards, Chart и Workspace.

Обычная эксплуатация не должна зависеть от Developer Mode.

## Что фиксировать после проверки

В публичную документацию переносятся только наблюдаемые факты, которые меняют модель, настройку или понимание Frappe.

Внутренний PASS/FAIL-отчёт ради самого отчёта не нужен.

Если live-test подтверждает уже проверенную по исходникам семантику, отдельный audit-документ не создаётся. Если поведение конкретного patch-release расходится с исходным ожиданием или меняет архитектурное решение, исправляется соответствующий публичный документ Lab.

## Источники

- [Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`DocType`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Assign To dialog`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [`FieldGroup.get_values`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/ui/field_group.js)
- [`ToDo`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Assignment Rule`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/assignment_rule/assignment_rule.py)
- [`Kanban Board`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/kanban_board/kanban_board.py)
- [`Workspace`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [`Workspace Sidebar`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace_sidebar/workspace_sidebar.py)
