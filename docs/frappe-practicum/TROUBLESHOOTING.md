# Диагностика типовых ошибок

Сначала записать последнюю выполненную команду или настройку. Не переустанавливать app и
не копировать базу, пока причина неизвестна.

## Команда выполняется не в том каталоге

Проверка:

```bash
pwd
```

Для команд Bench перейти:

```bash
cd ~/frappe/frappe-practicum-bench
```

Для Git-команд перейти в `apps/<app_name>`.

## `bench` не найден

```bash
uv tool update-shell
source ~/.bashrc
command -v bench
bench --version
```

Не устанавливать второй Bench через `pip` поверх варианта, установленного `uv tool`.

## Site не открывается

Проверить, что `bench start` продолжает работать и не завершился с ошибкой. В другом
терминале:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site platform-check.localhost list-apps
```

Для другого site заменить имя. Открывать адрес с портом разработки:

```text
http://<site-name>:8000
```

После изменения WSL или сетевых настроек остановить `bench start`, выполнить в
PowerShell `wsl --shutdown`, снова открыть Debian и запустить Bench.

## `bench new-site` не подключается к MariaDB

Проверить сервис и отдельного администратора:

```bash
systemctl is-active mariadb
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

Если второй тест не проходит, исправить пользователя MariaDB. Не передавать пароль в
командной строке.

## DocType сохранился, но файла в app нет

Проверить три условия:

1. Developer Mode включён для правильного site.
2. DocType не отмечен как Custom.
3. выбран Module текущего app.

Команды:

```bash
bench --site <site> show-config | rg developer_mode
find apps/<app>/<app> -type f -iname '*doctype*' | sort
```

После исправления:

```bash
bench --site <site> migrate
bench --site <site> clear-cache
```

## Изменение формы не видно

Сохранить DocType, затем:

```bash
bench --site <site> clear-cache
```

Обновить браузер с очисткой текущей страницы. Если проблема остаётся, открыть DocType и
проверить Module, fieldname и тип поля.

## Link не находит значение

Проверить:

- существует ли целевой Document;
- совпадает ли Options с точным именем DocType;
- не отключена ли запись;
- не скрывает ли её User Permission;
- есть ли Read на целевой DocType.

Link хранит системный `name`, а не произвольный текст.

## Пользователь видит лишнее или не видит разрешённое

Проверять под отдельным тестовым пользователем, а не через Administrator.

Последовательно проверить:

1. роли User;
2. базовые строки Permissions Standard DocType;
3. If Owner;
4. User Permission;
5. Share;
6. Permission Level нужного поля;
7. Workflow state и Allowed Role.

Assignment и Read Only не являются заменой этим проверкам.

## Workflow Action не появилась

Проверить:

- Workflow включён;
- текущий state документа совпадает с Current State transition;
- у пользователя есть Allowed Role;
- state field совпадает с `workflow_state`/настроенным полем;
- базовые permissions разрешают действие;
- переход в `docstatus = 1` выполняет роль с Submit;
- документ сохранён после последнего изменения.

## Fixture не появилась после export

Проверить фильтр и имя записи в `hooks.py`, затем выполнить:

```bash
bench --site <site> export-fixtures --app <app>
cd apps/<app>
git status --short
find <app>/fixtures -maxdepth 1 -type f -print | sort
```

Если экспортировалось слишком много записей, не коммитить файл. Сузить фильтр и
повторить экспорт.

## Объект есть на рабочем site, но исчез на чистом site

Классифицировать объект:

| Тип | Правильный способ поставки |
|---|---|
| Standard DocType/Report/Card/Chart/Web Form/Notification | исходники app и правильный Module |
| Public Workspace | исходники app, Public и Module |
| Role/Workflow/Calendar View/Kanban Board | fixture с точным фильтром |
| User/User Permission/Share/API key/SMTP | создать заново как local site configuration |
| Equipment/Request/Intake/Case | рабочие данные, не поставлять в app |

Не создавать пропавший переносимый объект вручную на чистом site. Исправить app и
повторить проверку.

## `git diff` показывает секрет

Не выполнять `git add` и `git commit`. Удалить секрет из файла, сменить его на site, если
он уже был сохранён, затем повторить:

```bash
git diff --check
git diff
```

Удаление строки из нового commit не делает уже опубликованный секрет безопасным.

---

# Engineering Bridge

## Agent не может сохранить существующий Service Case

Симптом:

```text
Agent открывает Case
→ меняет разрешённое поле
→ save падает на permission/read Service Intake
```

Сначала открыть `service_case.py`. Если Accepted-source rule находится в общем
`validate()`, причина архитектурная: creation-only invariant выполняется при каждом save.

Правильный вопрос:

```text
это правило создания?
→ before_insert

это правило любого сохранения?
→ validate / другая подходящая lifecycle phase
```

Не исправлять проблему выдачей Agent лишнего Read на Intake. Это расширит доступ ради
компенсации неправильного controller lifecycle.

## `create_case` работает только под Administrator

Проверить:

1. Triage User имеет Write на `Service Intake`.
2. Triage имеет Read на выбранный Intake.
3. Triage имеет Create на `Service Case`.
4. command не использует `ignore_permissions=True`.
5. вызов идёт POST по whitelisted Document method.

Не копировать Role names в Python как второй ACL.

## После ошибки REST остался частично созданный Case

Ожидаемая модель write request:

```text
uncaught exception
→ rollback current request transaction
```

Проверить код на:

- `frappe.db.commit()` внутри business command;
- пойманное exception, после которого request продолжает считаться успешным;
- внешнее действие, выполненное до transaction finality.

Не добавлять дополнительный rollback вслепую, пока не найдена причина нарушения штатной
transaction boundary.

## Patch не заполнил `converted_at`

Проверить:

```bash
bench --site intake.localhost migrate
```

Затем:

- есть ли новый field в `Service Intake`;
- path patch указан в `patches.txt`;
- patch находится в `[post_model_sync]`, если зависит от нового field;
- есть ли запись patch в `Patch Log`;
- source Case действительно имеет `source_intake` и ожидаемую `creation`.

Не запускать patch вручную повторно как обычную repair-команду, пока не понятно, почему
migration path не сработал.

## Automated tests создают неожиданные записи на рабочем site

Не запускать suite на `intake.localhost`.

Engineering Track использует:

```text
intake.localhost
→ working/upgrade

intake-test.localhost
→ automated tests

intake-engineering-clean.localhost
→ fresh install acceptance
```

Если tests уже запускались на рабочем site, сначала определить созданные test records и
не маскировать проблему database restore.

## Webhook не отправился после save

Для ordinary DocType event exact v16.32 webhook execution зависит от успешного commit и
background worker.

Проверить:

- Webhook enabled;
- правильный DocType event/condition;
- request действительно завершился успешно;
- worker/queue запущены;
- Webhook Request Log;
- URL/timeout/headers.

Не оборачивать Webhook во второй custom job только потому, что первая отправка не
сработала: сначала диагностировать штатный post-commit/background path.

---

## Когда пересоздавать чистый site

Чистый site можно пересоздать после исправления поставки app. Рабочий site с созданной
моделью не пересоздаётся для маскировки ошибки. Test site можно пересоздать как отдельное
тестовое окружение.

Если причина всё ещё непонятна, сохранить `git diff`, вывод команды и точный текст ошибки
до следующих действий.
