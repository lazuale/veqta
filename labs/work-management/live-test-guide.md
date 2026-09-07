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

Технические значения данных не меняются.

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
- Priority в Assign To соответствует `Work Item.priority`, если это подтверждается текущим patch-release;
- стандартный фильтр `Assigned To → Me` находит документ.

`Work Item.due_date` и `ToDo.date` проверяются отдельно и не обязаны совпадать.

## 5. Независимость `Work Item.status` и `ToDo.status`

Создайте назначенный Work Item и последовательно проверьте:

```text
Work Item Open → Waiting
Work Item Waiting → Open
Work Item Open → Closed
Work Item Closed → Cancelled
```

Зафиксируйте фактическое состояние связанного ToDo после каждого изменения.

Baseline не ожидает автоматической синхронизации. Если Frappe сам меняет ToDo каким-либо штатным механизмом, это фиксируется как факт версии.

Затем отдельно закройте ToDo и убедитесь, что Work Item не меняет `status` автоматически.

Это ключевой эксперимент: только его результат и реальная потребность могут стать основанием для будущего lifecycle-кода.

## 6. Waiting

На назначенной работе добавьте комментарий и переведите `Open → Waiting`.

Проверьте:

- назначение не теряется;
- Timeline сохраняет контекст;
- возврат `Waiting → Open` не требует отдельной сущности ожидания.

## 7. Пользователь без доступа

Под `plain@example.test` попробуйте открыть List и прямую ссылку Work Item.

Затем под `work-a@example.test` попробуйте назначить Work Item на `plain@example.test`.

Зафиксируйте фактическое поведение `Assign To` / `DocShare`. Назначение не должно становиться обходом authorization model только из-за того, что пользователь выбран в picker.

## 8. Снятие чужого назначения

Назначьте Work Item на `work-a@example.test`.

Под `work-b@example.test` попробуйте снять назначение.

Зафиксируйте штатное поведение Frappe. Если реальная эксплуатация потребует более строгого правила, это станет отдельным server-side требованием.

## 9. List View

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

## 10. Kanban

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

## 11. Number Cards

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

## 12. Dashboard Chart

`VEQTA New Work Items` должен:

- считать Work Item по `creation`;
- показывать последний месяц по дням;
- не трактоваться как производительность пользователя.

## 13. Auto Repeat

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

## 14. Workspace

Откройте `VEQTA Work Management` / `Управление работой`.

Проверьте:

- Новая работа;
- Список работ;
- Доска;
- четыре Number Cards;
- chart `Новые работы`;
- секции `Действия`, `Текущее состояние`, `Поступление`.

Интерфейс должен быть читаемым без Custom HTML/CSS. Calendar/Gantt shortcut отсутствует.

## 15. Metadata и fixture

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
- Kanban Board VEQTA Work Items

не должно быть:
- Work Item / ToDo user data
- global Saved Filters
- custom List JS
- ToDo hooks
- lifecycle-кода Work Item
```

Проверьте, что fixture не захватил посторонние Kanban Boards.

## 16. Reinstall test

На втором чистом Site:

```bash
bench --site <second-site> install-app veqta_work_management
bench --site <second-site> migrate
bench --site <second-site> clear-cache
```

Без ручной пересборки должны появиться:

- standard Work Item;
- naming `WI-.#####`;
- Role и DocPerm;
- Kanban fixture;
- Number Cards;
- Dashboard Chart;
- Workspace;
- Gettext localization.

Пользовательские данные первого Site переноситься не должны.

## 17. Runtime без Developer Mode

```bash
bench --site <site> set-config developer_mode 0
bench --site <site> clear-cache
```

Под обычным `VEQTA Work User` повторите создание Work Item, Assign To, изменение status, List, Kanban, Number Cards, Chart и Workspace.

Обычная эксплуатация не должна зависеть от Developer Mode.

## Что фиксировать после проверки

В публичную документацию переносятся только наблюдаемые факты, которые меняют модель, настройку или понимание Frappe.

Внутренний PASS/FAIL-отчёт ради самого отчёта не нужен.

## Источники

- [Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`ToDo`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/todo/todo.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Workspace`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
