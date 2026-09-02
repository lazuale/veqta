# Инженерная приёмка

## 1. Правило доказательства

Настройка или код считаются рабочими не после Save и не после успешного запуска метода,
а после проверки поведения.

Для существенной гарантии фиксируются:

```text
предусловие
→ действие
→ ожидаемый результат
→ фактический результат
→ enforcement layer
```

Фраза «кнопка не видна» не доказывает server-side запрет.

Фраза «метод отработал» не доказывает transaction safety, permissions или правильный
архитектурный owner.

Короткой таблицы достаточно:

| Проверка | Ожидалось | Получено | Слой |
|---|---|---|---|
| Viewer изменяет Equipment | запрет | запрет | DocPerm |
| Guest создаёт Service Intake | разрешено | создан | Web Form create path |
| Case из New Intake | запрет | ValidationError | ServiceCase.validate |
| exception после Case insert | Case отсутствует | rollback | request transaction |

---

# 2. Общие проверки каждого app

## Product scenario

Положительный пользовательский сценарий проходит от начала до конца на реалистичных
данных.

## Permissions

Минимум один разрешённый и один запрещённый сценарий проверены для каждой рабочей роли.
Administrator не является доказательством permissions.

## Source

Ученик показывает, какие файлы app изменились и какие данные остались только в site DB.

## Clean install

App устанавливается на новый site без копирования исходной базы.

## Engineering extension

Если app содержит собственный code, дополнительно проверяются:

```text
server invariant
semantic command permissions
transaction rollback
migration existing data
automated tests
upgrade existing site
```

---

# 3. Общий source checklist

Из каталога app:

```bash
git status --short
git diff --check
git diff --stat
git diff
```

Проверить:

- нет passwords/tokens/API secrets/SMTP credentials;
- нет working attachments/data dumps;
- DocType находятся в правильном Module;
- Standard Report/Workspace/Web Form/Notification находятся в source, когда заявлены;
- fixtures содержат только portable configuration;
- нет случайных Users/test documents;
- нет несвязанных изменений;
- commit описывает законченное состояние.

Для Engineering Bridge дополнительно:

- нет временного transaction probe;
- нет `ignore_permissions=True` в public business command;
- нет manual `frappe.db.commit()` в request action;
- patch находится в `patches.txt`;
- tests находятся в source;
- не создан fake service/repository/job без самостоятельной ответственности.

---

# 4. Site checklist

Рабочий site:

```bash
bench --site <site> list-apps
bench --site <site> migrate
bench --site <site> clear-cache
```

Clean acceptance:

```bash
bench new-site <clean-site>
bench --site <clean-site> install-app <app>
bench --site <clean-site> migrate
bench --site <clean-site> clear-cache
bench --site <clean-site> list-apps
```

Clean site не получает database restore исходного site.

Engineering Bridge дополнительно проверяет **upgrade исходного `intake.localhost`**, потому
что fresh install не доказывает migration старых данных.

---

# 5. P1 — Equipment Register

## Positive

- Manager создаёт Location, Category и Equipment.
- Equipment сохраняется с несколькими Identifier rows.
- Operator меняет разрешённые поля.
- Viewer читает List/Report, но не меняет Document.
- корректный Data Import создаёт records.
- Kanban меняет обычный `status`.
- global search по child identifier открывает Equipment.

## Negative

- mandatory field блокирует save;
- duplicate `asset_code` конфликтует с system `name`;
- Link не принимает отсутствующий Category;
- Viewer не create/write;
- Operator не delete в final matrix;
- User Permission сужает видимость и после эксперимента возвращается к заявленной policy.

## Clean site

После install существуют DocType, roles, Report, Number Card, Workspace, Kanban Board.
Working Equipment отсутствуют.

---

# 6. P2 — Purchase Requests

## Positive

- Requester создаёт Draft с items.
- request проходит Department Approval и Procurement Review.
- Approved получает `docstatus = 1`.
- Procurement Officer cancel → `docstatus = 2`.
- Reject допускает исправление/Resubmit.
- Assign To создаёт ToDo.
- Notification срабатывает по выбранному каналу.
- Approved печатается Print Format.
- Calendar показывает `required_by`.

## Negative

- Requester не выполняет approval actions.
- Department Approver не выполняет Procurement action.
- Auditor не меняет document.
- обычный Write не даёт Submit authority.
- assignment не выдаёт скрытое полное право.
- workflow state не меняется обходным drag/direct path.
- submitted document не принимает запрещённые updates.

## Clean site

Workflow, roles, Calendar, reports/cards/chart/workspace/notifications/print существуют.
Новые Users повторяют Draft → Approved.

---

# 7. P3 — Service Intake

## Positive

- Guest отправляет только разрешённые Web Form fields.
- пустое Contact Consent блокирует submission.
- Desk получает `Service Intake`, а не внутренний Case.
- Triage принимает Intake и вручную создаёт Case.
- Agent работает с назначенным Case.
- Manager закрывает Case.
- API User читает только разрешённый reference DocType.

## Negative

- Guest не видит Desk/List и не редактирует submission.
- Guest не задаёт triage/internal/workflow fields.
- Guest не создаёт Service Case.
- public form не раскрывает internal Link catalog.
- второй Case для одного Intake блокируется Unique.
- `source_intake` нельзя перепривязать после создания.
- API User не читает Intake/Case без Read.
- secrets отсутствуют в Git/protocol.

## Clean site

Web Form route, Workflow, reporting, workspace и notifications присутствуют. Guest
создаёт только Intake; Case появляется только после Triage action.

**P3 acceptance закрывает Metadata & Configuration level.**

---

# 8. Engineering Bridge

## E1 — Controller invariant

Предусловие: существует `Service Intake` со статусом `New`.

Проверка:

```text
create Service Case linked to New Intake
→ forbidden
→ ServiceCase.validate
```

После `Accepted` тот же Link должен быть допустим.

Отдельно объяснить: Link/Unique/Set Only Once продолжают обеспечиваться metadata, а
Controller не дублирует их.

## E2/E3 — Semantic command

Для Accepted Intake:

```text
POST create_case
→ exactly one Service Case
→ source_intake correct
→ converted_at filled
→ Timeline comment created
```

Повторный POST:

```text
→ error
→ no second Case
```

Для New Intake:

```text
→ error
→ no Case
```

Проверка выполняется permission-aware User, не Administrator/ignore-permissions path.

## E4 — API boundary

Ученик должен показать разницу:

```text
built-in Document REST
→ CRUD resource

whitelisted document method
→ semantic application command
```

API secret после проверки удалён из shell variables и отсутствует в Git.

## E5 — Transaction rollback

Временный probe после `case.insert()` бросает uncaught exception.

Ожидается:

```text
HTTP action failed
Service Case absent
converted_at empty
```

После удаления probe нормальный вызов создаёт Case.

Проверить:

```bash
grep -R "Transaction rollback probe" -n service_intake || true
```

Результат должен быть пустым перед commit.

Отдельно проверить отсутствие `frappe.db.commit()` в command.

## E6 — Patch / upgrade

На старом P3 site должен существовать Case, созданный до `converted_at`.

До migrate:

```text
old Intake.converted_at = empty
```

После:

```bash
bench --site intake.localhost migrate
```

ожидается:

```text
old Intake.converted_at = old Service Case.creation
```

Повторный migrate не должен повторно менять data как новый patch.

Ученик объясняет, почему patch использует deliberate DB update, а controller обычной
business operation — Document lifecycle.

## E7 — Automated tests

Команда:

```bash
bench --site intake.localhost run-tests --app service_intake
```

Обязательные проверки app-owned behavior:

- non-Accepted source rejected;
- accepted conversion works;
- duplicate conversion rejected;
- `converted_at` заполнен.

Не принимается suite, состоящий только из тестов, что Frappe Mandatory/Link вообще
работают.

## E8 — Async/integration decision

Ученик получает три требования и выбирает owner:

| Требование | Правильная первая проверка |
|---|---|
| простой HTTP callback по Case event | Webhook |
| тяжёлая работа только после успешного commit | Background Job + `enqueue_after_commit` |
| synchronous Document invariant | Controller lifecycle |

Custom job отсутствует в source, потому что текущий product requirement его не требует.
Это **положительный** результат архитектурного аудита.

## E9 — Clean install + upgrade

Оба сценария обязательны:

```text
existing intake.localhost
→ migrate + tests + old-data check

new intake-engineering-clean.localhost
→ install-app + migrate + tests
```

На clean site patch должен быть безопасен при отсутствии historical Case data.

---

# 9. Протокол ошибки

Если clean site или upgrade не воспроизводит ожидаемое состояние:

1. не копировать базу и не «дочинивать» объект молча;
2. определить layer: Standard source / fixture / local config / working data / patch / code;
3. определить owner гарантии;
4. исправить source/evolution path;
5. повторить migrate/install;
6. повторить positive/negative permission/behavior checks;
7. зафиксировать причину, а не только команду, которая «помогла».

Сбой переносимости или migration — часть практикума: он показывает, понял ли ученик
архитектуру Frappe, а не только Desk UI.
