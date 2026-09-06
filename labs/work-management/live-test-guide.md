# Work Management v1: проверка на живом Frappe Site

Этот сценарий нужен для проверки native-first конфигурации Work Management на реальном Frappe v16 Site. Он не заменяет [Setup Guide](setup-guide.md): сначала Site настраивается по нему, затем выполняются проверки ниже.

Цель — отделить поведение, подтверждённое исходным кодом Frappe, от поведения, которое важно увидеть в реальном Desk и на реальных документах.

## Стенд

Используйте отдельный чистый Site без пользовательских Client Script, Server Script, hooks и изменений стандартного `ToDo`.

Нужны три тестовых пользователя:

```text
work-a@example.test  — Work User
work-b@example.test  — Work User
plain@example.test   — обычный System User без Work User и без административных ролей
```

Административную настройку выполняет `Administrator` или пользователь с необходимыми штатными административными ролями.

Перед началом настройте Site полностью по [Setup Guide](setup-guide.md).

## 1. Общая очередь

Под `work-a@example.test` создайте:

```text
Subject: Проверка общей очереди
Status: Open
Priority: Medium
Due Date: пусто
```

Под `work-b@example.test` откройте `Work Item List`.

Проверьте:

- документ виден второму `Work User`;
- документ попадает в `Open`;
- документ попадает в `Active`;
- документ попадает в `Unassigned`.

## 2. Self-assignment

Под `work-b@example.test` откройте созданный Work Item и выполните:

```text
Assign To
→ Assign to me
```

Проверьте:

- `Work Item.status` остаётся `Open`;
- создаётся связанный `ToDo`;
- Work Item исчезает из `Unassigned`;
- Work Item находится через `Assigned To → Me` под `work-b@example.test`.

## 3. Waiting

Под `work-b@example.test` добавьте комментарий:

```text
Ожидаем внешний ответ.
```

Переведите:

```text
Open → Waiting
```

Проверьте:

- Work Item появляется в `Waiting`;
- assignment остаётся активным;
- комментарий остаётся в Timeline;
- Work Item больше не считается `Open`.

Затем верните:

```text
Waiting → Open
```

Проверьте, что существующий assignment сохраняется.

## 4. Завершение

Под `work-b@example.test` закройте собственный assignment.

Проверьте, что Work Item сам не становится `Closed`.

Затем вручную переведите Work Item в:

```text
Closed
```

Проверьте:

- Work Item исчезает из `Active`;
- Work Item не появляется в `Open` и `Waiting`;
- закрытие Work Item не создаёт новой автоматической операции над уже закрытым ToDo.

## 5. Отмена

Создайте новый Work Item и назначьте его `work-a@example.test`.

Снимите assignment, затем установите:

```text
Cancelled
```

Проверьте:

- документ сохраняется;
- документ не входит в `Active`;
- удаление Work Item для обычного `Work User` недоступно.

## 6. Несколько исполнителей

Создайте новый Work Item и назначьте одновременно:

```text
work-a@example.test
work-b@example.test
```

Проверьте:

- создаются два отдельных `ToDo`;
- каждый пользователь видит своё назначение;
- закрытие assignment одного пользователя не закрывает assignment другого;
- `Work Item.status` от этого автоматически не меняется.

## 7. Граница прав

Под `plain@example.test` попробуйте открыть `Work Item List` и прямой URL существующего Work Item.

Проверьте, что обычный System User без `Work User` и без административной роли не получает прикладной доступ к Work Item.

Отдельно убедитесь, что штатный административный доступ `Administrator` / `System Manager` не был удалён при настройке DocType.

## 8. Снятие чужого assignment

Создайте Work Item, назначенный `work-a@example.test`.

Под `work-b@example.test`, который также имеет `Work User`, попробуйте снять assignment `work-a@example.test`.

Проверьте фактическое поведение Desk и документа. Текущий native-first security contract допускает, что пользователь с `Write` на общей очереди может снять чужой assignment; этот сценарий важно подтвердить на живом Site.

## 9. Сроки

Создайте Work Item со сроком на текущую дату.

Проверьте:

- он попадает в Number Card `Due Today`;
- он отображается в `Work Items by Due Date`;
- URL shortcut Workspace открывает именно именованный Calendar View;
- Work Item без `due_date` не отображается как календарное событие.

Не используйте `ToDo.date` как критерий этой проверки.

## 10. Kanban

Откройте `Work Items` Kanban.

Перетащите тестовый Work Item:

```text
Open → Waiting
Waiting → Open
```

Проверьте, что изменяется реальное поле `Work Item.status` и изменение видно после повторного открытия документа.

Дополнительно подтвердите, что перенос в `Closed` сам по себе не закрывает активный `ToDo`.

## 11. Auto Repeat

Создайте отдельный тестовый Work Item:

```text
Subject: Проверка Auto Repeat
Description: Повторяющаяся тестовая работа
Status: Open
Priority: High
Due Date: любая дата
Links: добавьте одну тестовую связь
```

Создайте для него Auto Repeat без Assignee.

После появления нового экземпляра проверьте:

```text
subject      → скопирован
description  → скопирован
priority     → High
status       → Open
due_date     → пусто
links        → пусто
assignment   → отсутствует
```

Если для проверки пришлось ждать расписание, не меняйте модель ради ускорения теста: используйте минимальную штатную частоту или отдельный временный тестовый документ.

## 12. Workspace и аналитика

Под `work-a@example.test` откройте Workspace `Work Management`.

Проверьте:

- `New Work Item` открывает создание документа;
- `Work List` открывает List View;
- `Board` открывает `Work Items` Kanban;
- `Calendar` открывает `Work Items by Due Date`;
- Number Cards показывают значения, совпадающие с текущими тестовыми документами;
- клик по Number Card открывает отфильтрованный список;
- графики `Active Work by Status`, `Active Work by Priority` и `New Work Items` отображаются без ошибок.

## Что фиксировать как результат Lab

После фактического прогона в документацию переносятся только наблюдаемые отклонения от описанной модели или подтверждённые важные особенности Frappe.

Для каждого отклонения достаточно четырёх фактов:

```text
сценарий
что ожидалось по текущей модели
что фактически произошло
влияет ли это на архитектуру или только на инструкцию
```

Если фактическое поведение совпадает с текущей моделью, отдельный отчёт ради самого факта прохождения не нужен. Если выявлено расхождение, сначала исправляется соответствующая документация или конфигурация; собственный код рассматривается только если штатный Frappe действительно не закрывает требуемую ответственность.
