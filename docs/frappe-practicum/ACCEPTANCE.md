# Инженерная приёмка

## 1. Правило доказательства

Настройка считается рабочей не после нажатия Save, а после проверки поведения.

Для каждой гарантии фиксируются:

```text
предусловие
→ действие
→ ожидаемый результат
→ фактический результат
→ слой, который обеспечивает гарантию
```

Фраза «кнопка не видна» не доказывает server-side запрет. Permission test выполняется штатным действием под целевой ролью и, где уместно, через стандартный API.

## 2. Четыре gate каждого проекта

### Functional gate

Положительный пользовательский сценарий проходит от начала до конца на реалистичных данных.

### Permission gate

Минимум один разрешённый и один запрещённый сценарий проверены для каждой роли. Administrator не используется как доказательство прав рабочей роли.

### Source gate

Ученик может показать, какой файл app изменился после сохранения Standard metadata, и объяснить, какие настройки остались только в базе site.

### Clean-site gate

App устанавливается на новый site без копирования исходной базы. На нём повторяются ключевой сценарий и permission tests.

## 3. Общий source checklist

Из каталога конкретного app:

```bash
git status --short
git diff --check
git diff --stat
git diff
```

Проверить:

- нет паролей, token, API secret и SMTP credentials;
- нет файлов рабочих вложений;
- нет случайных Users и тестовых документов;
- DocType находятся в правильном Module;
- standard Report, Workspace, Web Form и Notification действительно экспортированы;
- fixtures содержат только заявленную переносимую конфигурацию;
- нет несвязанных изменений;
- commit описывает законченное состояние продукта.

## 4. Общий site checklist

Для рабочего site:

```bash
bench --site <site> list-apps
bench --site <site> migrate
bench --site <site> clear-cache
```

Для чистой приёмки:

```bash
bench new-site <clean-site>
bench --site <clean-site> install-app <app>
bench --site <clean-site> migrate
bench --site <clean-site> clear-cache
bench --site <clean-site> list-apps
```

Clean site не получает database restore исходного site. Тестовых Users и master data создают заново как входные данные приёмки.

## 5. P1 — реестр оборудования

### Положительные проверки

- Manager создаёт Location, Category и Equipment.
- Equipment сохраняется с несколькими Identifier rows.
- Operator меняет разрешённые рабочие поля.
- Viewer читает List и Report, но не меняет документ.
- импорт корректного файла создаёт записи.
- Kanban меняет обычный `status`.

### Отрицательные проверки

- отсутствующий mandatory field блокирует сохранение;
- дублирующий `asset_code` блокируется Unique;
- Link не принимает несуществующую Category;
- Viewer не создаёт и не изменяет Equipment;
- Operator не удаляет Equipment в финальной матрице;
- User Permission действительно сужает видимые Location и связанные документы, затем опыт откатывается или фиксируется как осознанная политика.

### Clean-site proof

После установки существуют DocType, роли, Report и Workspace. Рабочих Equipment нет до ручного создания или импорта.

## 6. P2 — заявки на закупку

### Положительные проверки

- Requester создаёт Draft со строками items.
- заявка проходит Department Approval и Procurement Review;
- Approved получает `docstatus = 1`;
- Procurement Officer отменяет Approved документ, получая `docstatus = 2`;
- возврат в Rejected допускает исправление и повторную подачу;
- Assign To создаёт ToDo нужному пользователю;
- Notification приходит по выбранному каналу;
- Approved печатается утверждённым Print Format.

### Отрицательные проверки

- Requester не выполняет Department/Procurement action;
- Department Approver не выполняет финальное действие Procurement;
- Auditor не меняет документ;
- обычный Write без Submit не даёт права утвердить документ;
- assignee без базового Read не получает неявную полную власть над документом;
- state не меняется прямой правкой поля или Kanban drag;
- после submit запрещённые поля не редактируются обычным save.

### Clean-site proof

Workflow, roles и permission matrix присутствуют после установки app. Полный переход Draft → Approved повторяется новыми тестовыми Users.

## 7. P3 — внешняя приёмная

### Положительные проверки

- Guest отправляет разрешённые поля Web Form;
- в Desk появляется `Service Intake` со значениями только из публичного allow-list;
- Triage принимает обращение и создаёт связанный `Service Case`;
- Agent работает с назначенным Case;
- Manager видит общую очередь и отчётность;
- API user выполняет только разрешённую операцию стандартного REST API.

### Отрицательные проверки

- Guest не видит Desk;
- Guest не получает список Intake;
- Guest не редактирует отправленный Intake;
- Guest не задаёт triage status, internal notes, assignee или workflow state;
- Guest не создаёт `Service Case`;
- публичная форма не раскрывает закрытый Link-каталог;
- API user не читает DocType без выданного Read;
- API secret отсутствует в Git и протоколе приёмки.

### Clean-site proof

После установки доступен заданный route Standard Web Form. Guest submission создаёт только `Service Intake`; внутренний Case появляется только после действия Triage user.

## 8. Протокол ошибки

Если clean site не воспроизводит рабочий site:

1. не копировать базу и не создавать недостающий объект вручную молча;
2. определить его тип: standard metadata, fixture, customization, local config или working data;
3. исправить слой поставки;
4. обновить app source и commit;
5. пересоздать чистую проверку;
6. повторить permission и functional gates.

Такой сбой — не помеха курсу, а основная проверка понимания архитектуры Frappe.
