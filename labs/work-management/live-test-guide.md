# Управление работой v1: проверка на живом Frappe Site

Этот сценарий проверяет Work Management Lab на реальном Frappe v16 development Site.

Цель — проверить не только пользовательское поведение, но и developer path Framework:

1. standard `Work Item` действительно принадлежит App;
2. Developer Mode не требуется обычному пользователю после сборки;
3. обязательное состояние можно воспроизводимо перенести на второй чистый Site;
4. config-only ограничения не ошибочно принимаются за пределы Frappe.

Перед началом соберите стенд по [Руководству по настройке](setup-guide.md).

## Стенд

Нужен отдельный development bench с Frappe v16 и App:

```text
work_management
```

Developer Mode включён на этапе проектирования.

Нужны три тестовых пользователя:

```text
work-a@example.test  — Work User
work-b@example.test  — Work User
plain@example.test   — обычный System User без Work User и административных ролей
```

Административную настройку выполняет `Administrator` или пользователь с необходимыми штатными административными ролями.

Интерфейс тестовых пользователей переключён на `Russian (ru)`.

## 1. Developer baseline

Проверьте:

```bash
bench --site <site> list-apps
```

Ожидается наличие:

```text
frappe
work_management
```

В Desk откройте `Work Item` как DocType и проверьте:

```text
Module: Work Management
Custom: No
```

После сохранения DocType проверьте каталог App через:

```bash
git status
```

Должны появиться изменения metadata/controller, созданные самим Frappe для standard DocType.

Если `Work Item` остался только database-state Site и не появился в App, live-test считается не пройденным: нужно сначала выяснить причину, а не продолжать строить конфигурацию поверх Custom DocType.

## 2. Русский интерфейс

Под `work-a@example.test` проверьте:

```text
Work Item → Работа
Open      → Открыто
Waiting   → Ожидание
Closed    → Закрыто
Cancelled → Отменено
Low       → Низкий
Medium    → Средний
High      → Высокий
```

Поля:

```text
Название
Описание
Статус
Приоритет
Срок
Связи
```

При этом technical values остаются:

```text
status: Open, Waiting, Closed, Cancelled
priority: Low, Medium, High
```

Если отдельная строка не переведена текущим словарём, фиксируйте это как локализационный результат, не меняя данные модели.

## 3. Общая очередь

Под `work-a@example.test` создайте:

```text
Название: Проверка общей очереди
Статус: Open
Приоритет: Medium
Срок: пусто
```

Под `work-b@example.test` проверьте:

- документ виден;
- входит в `Открытые`;
- входит в `Активные`;
- входит в `Без исполнителя`;
- фактический `status = Open`.

## 4. Самоназначение

Под `work-b@example.test` выполните:

```text
Assign To
→ Assign to me
```

Проверьте:

- создаётся отдельный `ToDo`;
- `Work Item.status` остаётся `Open`;
- Work Item исчезает из `Без исполнителя`;
- находится через `Assigned To → Me`.

## 5. Ожидание

Добавьте комментарий:

```text
Ожидаем внешний ответ.
```

Переведите:

```text
Open → Waiting
```

Проверьте:

- работа появляется в `Ожидание`;
- назначение остаётся активным;
- комментарий остаётся в Timeline.

Верните `Waiting → Open` и убедитесь, что назначение не потеряно.

## 6. Завершение

Закройте собственное назначение.

Проверьте, что Work Item сам не становится `Closed`.

Затем вручную установите `Closed` и проверьте:

- работа исчезает из активных фильтров;
- `status = Closed`;
- никакой дополнительной автоматической операции над ToDo не происходит.

## 7. Отмена

Создайте новый Work Item, назначьте пользователя, снимите назначение и установите `Cancelled`.

Проверьте:

- документ сохраняется;
- не входит в `Активные`;
- обычный `Work User` не может удалить Work Item.

## 8. Несколько исполнителей

Назначьте одновременно:

```text
work-a@example.test
work-b@example.test
```

Проверьте:

- создаются два отдельных `ToDo`;
- каждый пользователь видит своё назначение;
- закрытие одного ToDo не закрывает другой;
- `Work Item.status` автоматически не меняется.

## 9. Граница прав

Под `plain@example.test` попробуйте открыть List и прямой URL Work Item.

Ожидается отсутствие прикладного доступа.

Отдельно убедитесь, что административный доступ `Administrator` / `System Manager` сохранился.

## 10. Снятие чужого назначения

Создайте Work Item, назначенный `work-a@example.test`.

Под `work-b@example.test` попробуйте снять это назначение.

Зафиксируйте фактическое поведение. Текущая security-модель допускает, что в общей доверенной очереди пользователь с `Read` на Work Item сможет снять чужое назначение через штатный путь Frappe.

Если это подтвердится, результат не исправляется UI-запретом. При появлении реального требования на более строгую границу отдельно анализируется официальный permission/assignment extension path App.

## 11. Сроки и Calendar

Создайте Work Item со сроком сегодня.

Проверьте:

- Number Card `Срок сегодня`;
- `Работы по сроку`;
- shortcut `Календарь`;
- документ без `due_date` не появляется как календарное событие.

`ToDo.date` не используйте как критерий.

## 12. Kanban

Проверьте русские заголовки колонок при technical values:

```text
Open
Waiting
Closed
Cancelled
```

Перетащите:

```text
Open → Waiting → Open
```

Проверьте реальное изменение поля после повторного открытия документа.

Дополнительно подтвердите, что перенос в `Closed` сам по себе не закрывает активный `ToDo`.

## 13. Auto Repeat

Создайте тестовый Work Item:

```text
Название: Проверка Auto Repeat
Описание: Повторяющаяся тестовая работа
Статус: Open
Приоритет: High
Срок: любая дата
Связи: одна тестовая связь
```

Создайте Auto Repeat без Assignee.

После появления экземпляра проверьте:

```text
subject      → скопирован
description  → скопирован
priority     → High
status       → Open
due_date     → пусто
links        → пусто
назначение   → отсутствует
```

На текущем этапе `Work Item.on_recurring` не содержит прикладной логики. Поэтому относительный `due_date` не ожидается.

Отдельно зафиксируйте как факт Framework, что Auto Repeat вызывает controller method `on_recurring`. Не реализуйте его до появления реального правила относительного срока.

## 14. Workspace и визуальная структура

Под `work-a@example.test` откройте Workspace `Управление работой`.

Проверьте:

- `Новая работа` открывает создание;
- `Список работ` открывает List View;
- `Доска` открывает Kanban `Работы`;
- `Календарь` открывает `Работы по сроку`;
- пять Number Cards дают корректные значения;
- клик по карточке открывает ожидаемый filtered list;
- `Новые работы` отображается без ошибки.

Визуальная проверка:

- экран разделён на `Действия`, `Текущее состояние`, `Поступление`;
- Number Cards имеют спокойные различимые фоны;
- текст и числа читаются;
- Workspace не выглядит непрерывным белым полотном;
- используются доступные developer settings Workspace/shortcuts, если они улучшают штатный интерфейс;
- нет декоративного Custom HTML/CSS только ради имитации собственного frontend.

## 15. Проверка standard metadata

После настройки public Workspace и других объектов проверьте изменения в каталоге App:

```bash
git status
git diff
```

Разделите объекты на три группы:

```text
A. Frappe сам экспортировал в App
B. остались database records и требуют штатного fixture/delivery механизма
C. являются пользовательским состоянием Site и не должны поставляться App
```

Не объявляйте fixtures заранее для всего подряд. Для каждого обязательного объекта сначала наблюдайте фактическое поведение Frappe v16.

## 16. Reinstall test на втором чистом Site

Это основная проверка воспроизводимой поставки.

После фиксации экспортированного состояния App создайте второй чистый test Site в том же bench и установите App штатным способом:

```bash
bench --site <second-site> install-app work_management
bench --site <second-site> migrate
bench --site <second-site> clear-cache
```

На втором Site проверьте без ручного повторения всей настройки:

- появился ли `Work Item`;
- правильны ли поля и DocPerm;
- присутствует ли Workspace;
- присутствуют ли обязательные Number Cards/Charts;
- присутствуют ли Kanban/Calendar/переводы/роль `Work User`, если они должны быть частью App;
- не появились ли лишние данные, относящиеся только к первому Site.

Каждый отсутствующий обязательный объект — не повод немедленно писать patch. Сначала определить его штатный delivery mechanism: standard metadata, fixture или другой официальный механизм Frappe.

Reinstall test считается пройденным только когда второй Site можно привести в рабочее состояние без повторного ручного конструирования обязательной конфигурации.

## 17. Проверка без Developer Mode

После завершения developer/export проверки выключите Developer Mode на тестовом окружении и очистите cache.

Под обычным `Work User` повторно проверьте:

- Workspace;
- создание Work Item;
- List View;
- Assign To;
- Kanban;
- Calendar;
- Number Cards/Chart.

Ожидается, что пользовательский runtime не зависит от Developer Mode.

Если после выключения режима ломается обычная эксплуатация, нужно определить, случайно ли мы сделали developer-only UI частью runtime-контракта.

## Что фиксировать как результат лаборатории

В публичную документацию переносятся только наблюдаемые технические факты, которые меняют понимание Framework или конфигурацию.

Для отклонения достаточно:

```text
сценарий
что ожидалось
что произошло
это граница конкретной конфигурации или всего Framework
какой штатный механизм нужно проверить следующим
```

Внутренний PASS/FAIL-отчёт ради самого отчёта не нужен.

## Источники

- [Frappe Apps](https://docs.frappe.io/framework/user/en/guides/basics/apps)
- [Developer Mode](https://docs.frappe.io/framework/user/en/guides/app-development/how-enable-developer-mode-in-frappe)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Site Config](https://docs.frappe.io/framework/user/en/basics/site_config)
- [`DocType` controller, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py)
- [`Workspace`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/workspace/workspace.py)
- [`Assign To`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/form/assign_to.py)
- [`Auto Repeat`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/automation/doctype/auto_repeat/auto_repeat.py)
- [`Dashboard Chart Source`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/desk/doctype/dashboard_chart_source/dashboard_chart_source.py)
- [`Report`, v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/report/report.py)
