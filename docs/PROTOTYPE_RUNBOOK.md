# VEQTA — Prototype v0.1 Runbook

Статус: **пошаговая инструкция тестового стенда**.

Цель — проверить Issue #1 на чистом Frappe v16, не проектируя новые подсистемы VEQTA заранее.

## 1. Baseline

На дату подготовки runbook: 2026-08-29.

Проверенный stable Frappe v16: `v16.32.0`.

Перед фактическим запуском повторно проверить latest stable v16. Если версия изменилась, зафиксировать новый tag в Issue #1 и использовать его вместо указанного ниже.

Для prototype используется native Bench на Debian 13+, а не production Docker deployment. Причина: задача стенда — Developer Mode, `bench new-app`, создание стандартных DocType из Desk и получение их файлов в app repository.

## 2. Установка системных зависимостей

Под root:

```bash
apt update
apt install -y git redis-server libmariadb-dev mariadb-server mariadb-client pkg-config curl
systemctl enable --now redis-server mariadb
```

Проверить:

```bash
mariadb --version
redis-server --version
```

Выполнить первичную настройку MariaDB при необходимости:

```bash
mariadb-secure-installation
```

## 3. Отдельный пользователь разработки

Bench не вести от root.

```bash
adduser --disabled-password --gecos "" frappe
su - frappe
```

Дальнейшие команды этого runbook выполняются от пользователя `frappe`, если отдельно не указано обратное.

## 4. Node 24, Python 3.14 и Bench

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 24
npm install -g yarn

curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.14 --default
uv tool install frappe-bench
```

Проверить:

```bash
node -v
python --version
bench --version
yarn --version
```

## 5. Создание bench с точным stable tag

```bash
mkdir -p ~/frappe
cd ~/frappe
bench init --frappe-branch v16.32.0 veqta-bench
cd veqta-bench
bench version
```

Ожидаем, что `frappe` соответствует `v16.32.0`.

Точный вывод `bench version` зафиксировать в Issue #1.

## 6. Создание site

```bash
cd ~/frappe/veqta-bench
bench new-site veqta.localhost --db-type mariadb
bench use veqta.localhost
```

Команда попросит данные MariaDB и пароль пользователя `Administrator`.

## 7. Developer Mode

```bash
bench set-config -g developer_mode 1
bench --site veqta.localhost clear-cache
```

Developer Mode нужен, чтобы стандартные DocType, созданные для модуля VEQTA, сохранялись как файлы приложения, а не оставались только локальной кастомизацией site.

## 8. Создание app

```bash
cd ~/frappe/veqta-bench
bench new-app veqta
bench --site veqta.localhost install-app veqta
bench --site veqta.localhost list-apps
```

Проверить наличие:

```text
frappe
veqta
```

Метаданные app вводятся интерактивно. Лицензия продукта не должна считаться архитектурно утверждённой только из-за значения, выбранного при scaffold; окончательная лицензия VEQTA фиксируется отдельным решением до публичного релиза.

## 9. Запуск dev server

```bash
cd ~/frappe/veqta-bench
bench start
```

Для удалённого сервера предпочтительно открыть dev site через SSH tunnel, а не публиковать dev server напрямую:

```bash
ssh -L 8000:127.0.0.1:8000 USER@SERVER
```

После `bench use veqta.localhost` открыть локально:

```text
http://127.0.0.1:8000
```

Войти как `Administrator`.

## 10. Создать `Work Type` через Desk

Через поиск Desk открыть `DocType` и создать стандартный DocType приложения, не Custom DocType.

Базовые параметры:

```text
Name: Work Type
Module: VEQTA
Track Changes: yes
Autoname: field:code
Title Field: title
```

Поля prototype:

| fieldname | type | required | примечание |
|---|---|---:|---|
| `code` | Data | yes | unique, машинный идентификатор |
| `title` | Data | yes | пользовательское название |
| `description` | Small Text | no | описание типа |
| `disabled` | Check | no | default 0 |

После сохранения убедиться, что файлы появились внутри `apps/veqta/.../doctype/work_type/`.

Создать две записи:

```text
code = TASK
title = Task
```

```text
code = CHECK
title = Check
```

## 11. Создать `Work Item` через Desk

Базовые параметры:

```text
Name: Work Item
Module: VEQTA
Track Changes: yes
Title Field: title
```

Поля prototype:

| fieldname | type | required |
|---|---|---:|
| `title` | Data | yes |
| `work_type` | Link -> Work Type | yes |
| `description` | Text Editor | no |
| `due_at` | Datetime | no |

**Не добавлять пока:** `responsible`, `assigned_to`, `Workstream`, `Outcome`, `Priority`, `SLA`, `Handoff`.

Причина: prototype должен сначала проверить штатные primitives Frappe.

## 12. Workflow prototype

Через Desk создать один штатный `Workflow` для `Work Item`.

```text
Document Type: Work Item
Workflow State Field: workflow_state
Active: yes
```

States (все с `Doc Status = 0` для prototype):

```text
New
In Progress
Review
Done
```

Минимальные transitions:

```text
New -> In Progress
```

для обоих типов.

Для `TASK`:

```text
In Progress -> Done
Condition: doc.work_type == "TASK"
```

Для `CHECK`:

```text
In Progress -> Review
Condition: doc.work_type == "CHECK"

Review -> Done
Condition: doc.work_type == "CHECK"
```

Для первого теста можно использовать административную роль, чтобы не смешивать проверку lifecycle с проектированием RBAC.

Проверить, что Frappe создал workflow-state field как Link на стандартный `Workflow State`.

## 13. Assignment test

Не добавлять отдельное поле ответственного.

Для сохранённого `Work Item` использовать штатное `Assign To`.

Проверить:

1. одно назначение;
2. два назначения;
3. снятие одного из двух;
4. записи `ToDo`;
5. фильтрацию назначений.

Основным техническим источником проверки являются записи `ToDo` с полями:

```text
allocated_to
reference_type
reference_name
status
assigned_by
```

`_assign` не использовать как аналитический источник.

## 14. State history test

Сначала не писать никакой `Work State Change`.

Выполнить реальные workflow transitions и проверить:

- Timeline;
- Workflow comments;
- Version;
- возможность получить `from_state`, `to_state`, `user`, `timestamp` структурированно;
- возможность корректно рассчитать время между State.

Только если штатной истории недостаточно — переходить к этапу B Issue #1 и проверять минимальный структурированный `Work State Change`.

## 15. Kanban — отдельный compatibility test

Не считать Kanban заранее решённой частью архитектуры.

В `version-16` Kanban Board хранит собственные названия колонок и при drag-and-drop напрямую меняет выбранное поле документа. Quick Kanban получает колонки из `options` поля.

Workflow при этом создаёт поле типа `Link -> Workflow State`, а не обычный `Select` со списком состояний.

Поэтому prototype обязан отдельно проверить:

1. можно ли корректно создать Kanban по workflow-state field;
2. нужно ли вручную создавать колонки;
3. проходит ли drag-and-drop через Workflow validation;
4. не позволяет ли Kanban выполнить transition, запрещённый Workflow;
5. остаётся ли история transitions корректной после drag-and-drop.

Если хотя бы одно из этих свойств нарушается, не исправлять это новым framework до отдельного решения.

## 16. После prototype

Зафиксировать в Issue #1 фактические результаты и только затем обновить `docs/DECISIONS.md`.

Должны получить ответы на Q-001, Q-002, Q-003, Q-006, Q-007.

До этого не проектировать новые Core-сущности.
