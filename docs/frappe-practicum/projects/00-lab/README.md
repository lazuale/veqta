# L0. Основа приложения

L0 нужен для одного: разобраться, **из чего реально состоит Frappe-приложение**, и создать app, который будет развиваться весь курс.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

`facility_ops` не является временным лабораторным app. L1–L11 будут развивать именно его.

Временным объектом L0 будет только `Lab Note`: он нужен, чтобы руками увидеть связь между Standard DocType, generated files, database и Git. В конце L0 `Lab Note` удаляется.

## К концу L0 ученик может показать

- точную версию Frappe;
- `facility_ops`, установленный на site;
- Developer Mode;
- default Module;
- структуру app и основные файлы;
- Desk v16;
- scheduler и workers;
- Standard DocType и его generated metadata;
- обычный Document в базе site;
- Git diff изменения metadata;
- штатное удаление Standard DocType и его файлов.

PDF в L0 не проверяем. Он изучается отдельно в Lab E.

---

# 1. Поднять стенд

Если стенда ещё нет, пройти:

[SETUP_WSL2.md](SETUP_WSL2.md)

После установки ожидается:

```text
~/frappe/facility-ops-bench/
├── apps/
│   ├── frappe/
│   └── facility_ops/
└── sites/
    └── facility-ops.localhost/
```

Проверить:

```bash
cd ~/frappe/facility-ops-bench

bench version
bench --site facility-ops.localhost list-apps

cd apps/frappe
git describe --tags --exact-match
cd ../..
```

Нужно увидеть Frappe `16.32.0`, приложения `frappe` и `facility_ops`, а `git describe` должен вернуть:

```text
v16.32.0
```

Если версия другая — L0 не начинаем.

---

# 2. Разделить Bench, app и site

```bash
cd ~/frappe/facility-ops-bench
ls -la
ls -la apps
ls -la sites
```

Для начала достаточно:

```text
apps/    код приложений
sites/   отдельные экземпляры Frappe и их данные
logs/    журналы процессов Bench
```

Главное различие:

```text
facility_ops
= app

facility-ops.localhost
= site, на который app установлен
```

Один app можно устанавливать на несколько sites. В L11 это будет проверено на чистом site.

---

# 3. Посмотреть структуру `facility_ops`

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
pwd
git status
find . -maxdepth 2 -type f | sort
```

Найти:

```text
pyproject.toml
facility_ops/hooks.py
facility_ops/modules.txt
facility_ops/patches.txt
```

Проверить Module:

```bash
cat facility_ops/modules.txt
```

Ожидается:

```text
Facility Operations
```

Этот Module уже создал `bench new-app`. Второй раз создавать его не нужно.

Посмотреть начало `hooks.py`:

```bash
sed -n '1,120p' facility_ops/hooks.py
```

Пока ничего не менять.

На этом этапе достаточно понимать:

- `pyproject.toml` описывает Python package app;
- `hooks.py` — штатная точка конфигурации приложения;
- `modules.txt` перечисляет Module приложения;
- `patches.txt` используется для migrations/patches;
- Module — логическая часть app, а не отдельное приложение.

---

# 4. Проверить Developer Mode

```bash
cd ~/frappe/facility-ops-bench
grep '"developer_mode"' sites/common_site_config.json
```

Ожидается:

```text
"developer_mode": 1
```

Если Developer Mode выключен:

```bash
bench set-config -g developer_mode 1
bench --site facility-ops.localhost clear-cache
```

В Developer Mode Standard objects своего app могут сохраняться как version-controlled metadata внутри приложения.

---

# 5. Запустить Desk и пройти базовую навигацию

В первом терминале:

```bash
cd ~/frappe/facility-ops-bench
bench start
```

В браузере открыть:

```text
http://facility-ops.localhost:8000
```

Войти как `Administrator`.

Найти:

- Apps Page;
- Workspace Sidebar;
- Public Workspaces;
- My Workspaces;
- Awesomebar / command palette;
- List View;
- Form View;
- меню пользователя и Settings.

L0 не собирает Workspace. Здесь нужна только ориентация в Desk.

---

# 6. Проверить scheduler и workers

Оставить `bench start` работающим.

Во втором терминале:

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost scheduler status
```

Если scheduler выключен:

```bash
bench --site facility-ops.localhost scheduler enable
```

Повторить:

```bash
bench --site facility-ops.localhost scheduler status
bench --site facility-ops.localhost doctor
bench --site facility-ops.localhost show-pending-jobs
```

Пустая очередь на новом стенде нормальна. Точное количество workers не фиксируем.

---

# 7. Создать временный Standard DocType

В Desk через Awesomebar открыть `DocType` и создать:

```text
Name:   Lab Note
Module: Facility Operations
Custom: выключено
```

Поля:

| Label | Type | Mandatory | Default |
|---|---|---:|---|
| Title | Data | Yes | |
| Note | Small Text | No | |
| Is Active | Check | No | 1 |

Naming, полноценная модель данных и расширенные свойства начинаются в L1–L2.

Сохранить DocType.

---

# 8. Найти generated files

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status --short
```

Найти каталог:

```bash
find facility_ops/facility_operations/doctype/lab_note \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидается boilerplate примерно такого состава:

```text
__init__.py
lab_note.js
lab_note.json
lab_note.py
test_lab_note.py
```

Посмотреть JSON:

```bash
sed -n '1,240p' \
  facility_ops/facility_operations/doctype/lab_note/lab_note.json
```

Найти:

- `name`;
- `module`;
- `fields`;
- `fieldname`;
- типы полей;
- mandatory;
- default.

JSON вручную не редактировать.

Сейчас важно увидеть цепочку:

```text
DocType в Desk
    ↓ Save
metadata
    ↓
JSON + boilerplate в app
    ↓
Git
```

`.py` и `.js` созданы Frappe как boilerplate. В L0 их не редактируем.

---

# 9. Создать обычный Document

Открыть список `Lab Note` и создать запись:

```text
Title:     Первая запись
Note:      Это обычный Document
Is Active: включено
```

Сохранить.

Снова:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops
git status --short
```

Создание ещё одного `Lab Note` Document не должно создавать новый исходный файл app.

Главное различие:

```text
DocType
= описание типа документов
= Standard metadata своего app хранится в файлах app

Document
= конкретная запись DocType
= данные конкретного site
= хранится в базе данных
```

Git не является backup рабочих данных site.

---

# 10. Увидеть Git diff metadata

Вернуться в `DocType: Lab Note`.

Изменить label:

```text
Note → Comment
```

Сохранить.

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git diff -- \
  facility_ops/facility_operations/doctype/lab_note/lab_note.json
```

Убедиться, что изменилась metadata.

Вернуть label обратно в `Note`, снова сохранить и повторить diff.

---

# 11. Зафиксировать создание DocType

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git diff
git add .
git diff --cached
git commit -m "Add Lab Note doctype"
git status
```

Удалённый GitHub repository для учебного app на этом этапе не обязателен. Важно понять локальную version-control модель Frappe app.

---

# 12. Что сознательно не входит в L0

Пока не нужно:

- строить Facility Location и Equipment;
- писать Python controller;
- писать JavaScript;
- Client Script;
- Server Script;
- Workflow;
- роли и permissions;
- Customize Form;
- fixtures;
- Reports;
- Workspace;
- Web Form;
- REST API;
- PDF.

Каждый механизм появится позже только по задаче основного маршрута или отдельной Lab.

---

# 13. Приёмка L0

До cleanup ученик может выполнить и объяснить:

```bash
cd ~/frappe/facility-ops-bench
bench version
bench --site facility-ops.localhost list-apps
bench --site facility-ops.localhost scheduler status
bench --site facility-ops.localhost doctor

cd apps/facility_ops
git status
cat facility_ops/modules.txt
```

И показать:

- Frappe `v16.32.0`;
- app `facility_ops`;
- site `facility-ops.localhost`;
- Module `Facility Operations`;
- Developer Mode;
- каталог `Lab Note`;
- `lab_note.json`;
- обычный Document `Lab Note`;
- объяснение metadata против рабочих данных;
- разницу Bench / app / site / Module.

---

# 14. Удалить `Lab Note` и оставить чистый `facility_ops`

`Lab Note` нужен только как диагностический объект L0.

1. Удалить созданный Document `Lab Note`.
2. Под `Administrator` открыть `DocType: Lab Note`.
3. Выполнить стандартное действие `Delete`.

В Developer Mode Frappe v16.32.0 позволяет удалить Standard DocType и удаляет его controller/metadata directory из app.

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
find facility_ops/facility_operations/doctype/lab_note \
  -maxdepth 1 -type f -printf '%f\n' 2>/dev/null || true
```

Каталога `lab_note` больше быть не должно.

Зафиксировать cleanup:

```bash
git add -A
git diff --cached
git commit -m "Remove Lab Note training doctype"
git status
```

Финальное состояние перед L1:

- `facility_ops` установлен и работает;
- Module `Facility Operations` существует;
- Developer Mode включён;
- scheduler/workers проверены;
- lifecycle Standard metadata `create → change → delete` пройден;
- временного DocType больше нет;
- Git working tree чистый.

После этого L1 создаёт `Facility Location`.
