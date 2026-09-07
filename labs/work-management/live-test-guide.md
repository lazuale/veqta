# Управление работой v1: проверка на живом Frappe Site

Этот сценарий проверяет Work Management Lab на реальном Frappe v16 Site после сборки по [Руководству по настройке](setup-guide.md).

Проверяются два типа вещей:

- собственные контракты `Work Item`;
- фактическая воспроизводимая поставка App.

Стандартные возможности Frappe не тестируются повторно без причины.

## Стенд

Нужен отдельный development Site с App:

```text
veqta_work_management
```

Тестовые пользователи:

```text
work-a@example.test  — VEQTA Work User
work-b@example.test  — VEQTA Work User
plain@example.test   — System User без VEQTA Work User и административных ролей
```

Интерфейс рабочих пользователей — `Russian (ru)`.

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
Naming: VWM-WI-.#####
Is Calendar and Gantt: No
```

Создайте один документ и убедитесь, что имя имеет вид:

```text
VWM-WI-00001
```

После сохранения standard metadata выполните в каталоге App:

```bash
git status
git diff
```

`Work Item` должен находиться в App, а не существовать только в DB development Site.

## 2. Русская локализация

После Gettext build/compile под `work-a@example.test` проверьте уникальные строки App:

```text
Work Item             → Работа
VEQTA Work Management → Управление работой
VEQTA Work User       → Участник управления работой
VEQTA Work Items      → Работы
```

Стандартные `Open / Waiting / Closed / Cancelled`, `Low / Medium / High` должны отображаться через доступные русские переводы Frappe.

Технические значения в данных не меняются.

## 3. Общая очередь

Под `work-a@example.test` создайте:

```text
Subject: Проверка общей очереди
Status: Open
Priority: Medium
Due Date: пусто
```

Под `work-b@example.test` проверьте:

- документ виден;
- его можно открыть и изменить;
- `status = Open`;
- `plain@example.test` документ не видит.

Это подтверждает доверенную общую очередь Role/DocPerm.

## 4. Самоназначение

Под `work-b@example.test`:

```text
Assign To
→ Assign to me
```

Проверьте:

- создаётся отдельный `ToDo`;
- `reference_type = Work Item`;
- `reference_name` равен имени Work Item;
- Work Item остаётся `Open`;
- Priority в Assign To dialog по умолчанию соответствует `Work Item.priority`;
- Work Item находится через стандартный `Assigned To → Me`.

`Work Item.due_date` и `ToDo.date` проверяйте отдельно: они не обязаны совпадать.

## 5. Waiting

На назначенной работе добавьте комментарий с контекстом и переведите:

```text
Open → Waiting
```

Проверьте:

- Work Item остаётся назначенным;
- активный ToDo не закрывается;
- Timeline сохраняет комментарий.

Верните `Waiting → Open`: назначение не должно потеряться.

## 6. Closed завершает активные назначения

Создайте Work Item и назначьте одновременно:

```text
work-a@example.test
work-b@example.test
```

Переведите Work Item:

```text
Open → Closed
```

Проверьте:

- `Work Item.status = Closed`;
- оба активных ToDo стали `Closed`;
- активных назначений больше нет.

Это собственный lifecycle-контракт App.

## 7. Cancelled отменяет только активные назначения

Создайте Work Item с двумя назначениями.

Сначала закройте ToDo `work-a@example.test` штатной кнопкой Done. ToDo `work-b@example.test` оставьте `Open`.

Затем:

```text
Work Item → Cancelled
```

Проверьте:

```text
ToDo A: Closed    → остаётся Closed
ToDo B: Open      → становится Cancelled
```

Work Item остаётся `Cancelled`.

Если уже Closed ToDo переписывается в Cancelled, реализация terminal lifecycle неверна.

## 8. Нельзя назначать terminal Work Item

На Work Item со статусом `Closed` попробуйте создать новое назначение.

Ожидается server-side ошибка App и отсутствие нового Open ToDo.

Повторите для `Cancelled`.

Отдельно попробуйте изменить ранее закрытый связанный ToDo обратно в `Open`, если текущие права/UI позволяют это сделать. Серверный `ToDo.validate` hook должен отвергнуть такую операцию, пока Work Item terminal.

После перевода Work Item обратно в `Open` новое назначение снова допустимо. Старые Closed/Cancelled ToDo автоматически не переоткрываются.

## 9. Закрытие одного ToDo не закрывает Work Item

Создайте Work Item с двумя исполнителями и закройте только своё назначение.

Проверьте:

- второй ToDo остаётся активным;
- `Work Item.status` не меняется автоматически.

Это подтверждает направление lifecycle:

```text
Work Item terminal → assignments
```

но не:

```text
one assignment Closed → Work Item Closed
```

## 10. Пользователь без доступа

Под `plain@example.test` попробуйте:

- открыть List Work Item;
- открыть Work Item по прямой ссылке.

Ожидается отсутствие прикладного доступа.

Затем под `work-a@example.test` попробуйте назначить Work Item на `plain@example.test` через стандартный Assign To picker.

Поскольку `VEQTA Work User` не имеет `Share`, назначение пользователя без доступа не должно превращаться в способ обхода Role/DocPerm. Зафиксируйте фактическую permission error и убедитесь, что Open ToDo не остался после отката запроса.

## 11. Снятие чужого назначения

Создайте Work Item, назначенный `work-a@example.test`.

Под `work-b@example.test` попробуйте снять это назначение.

Текущая модель доверенной общей очереди допускает, что пользователь с Write на Work Item сможет это сделать штатным путём Frappe.

Если эксплуатация потребует запретить действие, это отдельное server-side требование; UI-запрет сам по себе не является решением.

## 12. List View

Проверьте:

- Subject, Status, Priority, Due Date;
- штатное отображение назначений;
- сортировку `creation DESC`;
- цветовые indicators из `work_item_list.js`;
- `Assigned To → Me`.

Проверьте обычные фильтры:

```text
status in Open, Waiting
status = Open
status = Waiting
```

Не требуется наличие заранее созданных global Saved Filters.

## 13. Kanban

Откройте `VEQTA Work Items` (`Работы`).

Проверьте колонки:

```text
Open
Waiting
Closed
Cancelled
```

Карточка должна показывать как минимум:

```text
subject
priority
due_date
```

Перетащите:

```text
Open → Waiting → Open
```

и проверьте сохранённый `status`.

Затем на Work Item с активным назначением перетащите:

```text
Open → Closed
```

Связанный ToDo должен закрыться тем же server lifecycle, что и при изменении статуса из формы. Отдельного Kanban-кода для этого быть не должно.

## 14. Number Cards

Проверьте четыре standard cards:

```text
Активные работы
Ожидание
Высокий приоритет
Срок сегодня
```

Для каждой сравните число с обычным permission-aware List View по тем же фильтрам.

### Отдельный experiment: «Без исполнителя»

Попробуйте на exact patch-release создать временную Number Card с фильтром:

```text
status = Open
Assigned To Is Not Set
```

Проверьте реальный SQL/UI результат на назначенных и неназначенных Work Item.

Этот experiment не является обязательным App state. Только подтверждённый результат может стать основанием добавить standard card позже.

## 15. Dashboard Chart

`VEQTA New Work Items` должен:

- открываться без ошибки;
- считать Work Item по `creation`;
- показывать последний месяц по дням;
- не трактоваться как производительность пользователя.

## 16. Auto Repeat

Создайте Work Item:

```text
Subject: Проверка Auto Repeat
Description: Повторяющаяся работа
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
назначение   → отсутствует
```

Относительный due date без отдельного правила не ожидается.

## 17. Workspace и визуальная структура

Откройте `VEQTA Work Management` / `Управление работой`.

Проверьте shortcuts:

- Новая работа;
- Список работ;
- Доска.

Проверьте четыре Number Cards и chart `Новые работы`.

Визуально:

- есть ясные секции `Действия`, `Текущее состояние`, `Поступление`;
- Number Cards визуально различимы;
- интерфейс читается как рабочий экран, а не непрерывное белое полотно;
- нет Custom HTML/CSS только ради декора.

Calendar/Gantt shortcut отсутствует.

## 18. Проверка metadata и fixture

В каталоге App:

```bash
git status
git diff
```

Разделите состояние:

```text
standard metadata / code:
- Work Item
- controller
- list.js
- Workspace
- Number Cards
- Dashboard Chart
- hooks.py
- locale/main.pot
- locale/ru.po

fixture:
- Kanban Board VEQTA Work Items

не должно поставляться:
- пользовательские Saved Filters
- Work Item data
- ToDo data
```

Проверьте fixture: в нём не должно быть чужих Kanban Boards Site.

## 19. Автоматические тесты App

Запустите:

```bash
bench --site <site> run-tests --app veqta_work_management
```

Обязательные App contracts:

- Closed закрывает активные назначения;
- Cancelled отменяет только активные назначения;
- terminal Work Item блокирует Open ToDo;
- один Closed ToDo не закрывает Work Item;
- Auto Repeat не переносит No Copy fields.

## 20. Reinstall test на втором чистом Site

Установите App без ручного повторения конфигурации:

```bash
bench --site <second-site> install-app veqta_work_management
bench --site <second-site> migrate
bench --site <second-site> clear-cache
```

Проверьте:

- standard Work Item;
- naming `VWM-WI-.#####`;
- роль и DocPerm;
- controller/hooks;
- List indicator;
- Kanban fixture;
- Number Cards;
- Dashboard Chart;
- Workspace;
- Gettext Russian translation.

Не должны появиться пользовательские Work Item/ToDo/Saved Filters первого Site.

Каждый отсутствующий обязательный объект сначала разбирается по его штатному delivery mechanism. Patch не добавляется автоматически.

## 21. Runtime без Developer Mode

Выключите Developer Mode только на тестовом Site:

```bash
bench --site <site> set-config developer_mode 0
bench --site <site> clear-cache
```

Под `VEQTA Work User` повторите:

- создание Work Item;
- Assign To;
- Closed / Cancelled lifecycle;
- List;
- Kanban;
- Number Cards;
- Chart;
- Workspace.

Обычная эксплуатация не должна зависеть от Developer Mode.

## Что переносить в публичную документацию после проверки

Фиксируются только наблюдаемые технические факты, которые меняют модель, настройку или понимание Framework.

Внутренний PASS/FAIL-отчёт ради самого отчёта не нужен.

## Источники

- [Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Frappe Commands](https://docs.frappe.io/framework/user/en/bench/frappe-commands)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Assign To dialog`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/public/js/frappe/form/sidebar/assign_to.js)
- [`Document hooks`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/model/document.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Number Card`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/number_card/number_card.py)
- [`Fixtures`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py)
- [`Gettext commands`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/commands/gettext.py)