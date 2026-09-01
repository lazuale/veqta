# P0. Учебное приложение

P0 нужен для одного: разобраться, **из чего реально состоит Frappe-приложение**, как связаны Bench, app, site, Module, Desk, база данных и файлы в Git.

Базовая версия: **Frappe Framework v16.32.0**.

## Что должно получиться

К концу P0 есть отдельный учебный стенд:

```text
Bench: frappe-practicum-bench
App:   frappe_practicum
Site:  frappe-practicum.localhost
Module: Frappe Practicum
```

И ученик может показать:

- точную версию Frappe;
- app, установленный на site;
- включённый Developer Mode;
- default Module, созданный вместе с app;
- структуру app и основные файлы;
- работающий Desk v16;
- scheduler и workers;
- первый стандартный DocType;
- файлы этого DocType в app;
- обычный Document в базе site;
- разницу между изменением metadata приложения и созданием рабочих данных;
- штатное удаление стандартного DocType и соответствующее удаление его файлов из app.

PDF в P0 не проверяем. Он впервые понадобится в P5.

---

# 1. Поднять отдельный стенд

Если учебного стенда ещё нет, пройти:

[SETUP_WSL2.md](SETUP_WSL2.md)

После установки ожидается:

```text
~/frappe/frappe-practicum-bench/
├── apps/
│   ├── frappe/
│   └── frappe_practicum/
└── sites/
    └── frappe-practicum.localhost/
```

Проверить:

```bash
cd ~/frappe/frappe-practicum-bench

bench version
bench --site frappe-practicum.localhost list-apps

cd apps/frappe
git describe --tags --exact-match
cd ../..
```

Нужно увидеть Frappe `16.32.0`, приложения `frappe` и `frappe_practicum`, а `git describe` должен вернуть:

```text
v16.32.0
```

Если версия другая — P0 не начинаем.

---

# 2. Bench, app и site — это разные вещи

Открыть корень Bench:

```bash
cd ~/frappe/frappe-practicum-bench
ls -la
```

Для начала достаточно трёх каталогов:

```text
apps/    код приложений
sites/   отдельные экземпляры Frappe и их данные
logs/    журналы процессов Bench
```

Посмотреть:

```bash
ls -la apps
ls -la sites
```

Зафиксировать главное:

```text
frappe_practicum
= app

frappe-practicum.localhost
= site, на который app установлен
```

Один app можно устанавливать на разные sites. Это будет отдельно проверено в P2.

---

# 3. Посмотреть структуру учебного app

```bash
cd ~/frappe/frappe-practicum-bench/apps/frappe_practicum
pwd
git status
find . -maxdepth 2 -type f | sort
```

Найти:

```text
pyproject.toml
frappe_practicum/hooks.py
frappe_practicum/modules.txt
frappe_practicum/patches.txt
```

Проверить Module:

```bash
cat frappe_practicum/modules.txt
```

Ожидается:

```text
Frappe Practicum
```

Этот Module уже создал `bench new-app`. Второй раз создавать его не нужно.

Посмотреть начало `hooks.py`:

```bash
sed -n '1,120p' frappe_practicum/hooks.py
```

Пока ничего не менять.

На этом этапе достаточно понимать:

- `pyproject.toml` описывает Python package app;
- `hooks.py` — штатная точка конфигурации приложения;
- `modules.txt` перечисляет Module приложения;
- `patches.txt` используется для patches/migrations;
- Module — логическая часть app, а не отдельное приложение.

---

# 4. Проверить Developer Mode

```bash
cd ~/frappe/frappe-practicum-bench
grep '"developer_mode"' sites/common_site_config.json
```

Ожидается:

```text
"developer_mode": 1
```

Если Developer Mode выключен:

```bash
bench set-config -g developer_mode 1
bench --site frappe-practicum.localhost clear-cache
```

В Developer Mode стандартные объекты своего app могут сохраняться как файлы приложения и попадать в Git.

---

# 5. Запустить Desk и пройти базовую навигацию v16

В первом терминале:

```bash
cd ~/frappe/frappe-practicum-bench
bench start
```

В браузере открыть:

```text
http://frappe-practicum.localhost:8000
```

Войти как `Administrator`.

Найти в интерфейсе:

- Apps Page;
- Workspace Sidebar;
- Public Workspaces;
- My Workspaces;
- Awesomebar / command palette;
- List View;
- Form View;
- меню пользователя и Settings.

Ничего специально не настраивать. P0 нужен только для ориентации в Desk.

---

# 6. Проверить scheduler и workers

Оставить `bench start` работающим.

Во втором терминале:

```bash
cd ~/frappe/frappe-practicum-bench
bench --site frappe-practicum.localhost scheduler status
```

Если scheduler выключен:

```bash
bench --site frappe-practicum.localhost scheduler enable
```

Повторить проверку:

```bash
bench --site frappe-practicum.localhost scheduler status
bench --site frappe-practicum.localhost doctor
bench --site frappe-practicum.localhost show-pending-jobs
```

Пустая очередь на новом стенде нормальна.

Точное количество workers не фиксируем. Важно, чтобы команды выполнялись без ошибок Redis/queues и scheduler был enabled.

---

# 7. Создать первый стандартный DocType

В Desk через Awesomebar открыть:

```text
DocType
```

Создать новый DocType:

```text
Name:   Lab Note
Module: Frappe Practicum
Custom: выключено
```

Добавить три поля:

| Label | Type | Mandatory | Default |
|---|---|---:|---|
| Title | Data | Yes | |
| Note | Small Text | No | |
| Is Active | Check | No | 1 |

Никакие другие свойства пока не настраивать.

Naming, Title Field, Search Fields, permissions и расширенная модель данных начинаются в следующих проектах.

Сохранить DocType.

---

# 8. Найти созданные файлы

В терминале:

```bash
cd ~/frappe/frappe-practicum-bench/apps/frappe_practicum
git status --short
```

Найти каталог DocType:

```bash
find frappe_practicum/frappe_practicum/doctype/lab_note \
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

Главный файл сейчас:

```text
lab_note.json
```

Посмотреть:

```bash
sed -n '1,240p' \
  frappe_practicum/frappe_practicum/doctype/lab_note/lab_note.json
```

Найти в JSON:

- `name`;
- `module`;
- `fields`;
- `fieldname`;
- типы полей;
- mandatory для `Title`;
- default для `Is Active`.

JSON вручную не редактировать.

Сейчас нужно увидеть цепочку:

```text
DocType в Desk
    ↓ Save
metadata
    ↓
JSON + boilerplate в app
    ↓
Git
```

`.py` и `.js` рядом с DocType — штатный boilerplate. В P0 их не редактируем.

---

# 9. Создать обычный Document

Открыть список `Lab Note` и создать запись:

```text
Title:     Первая запись
Note:      Это обычный Document
Is Active: включено
```

Сохранить.

Снова выполнить:

```bash
cd ~/frappe/frappe-practicum-bench/apps/frappe_practicum
git status --short
```

Создание ещё одной записи `Lab Note` не должно создавать новый исходный файл app.

Главная разница:

```text
DocType
= описание типа документов
= metadata
= стандартный DocType своего app хранится в файлах app

Document
= конкретная запись DocType
= данные конкретного site
= хранится в базе данных
```

Git не является резервной копией рабочих данных site.

---

# 10. Увидеть реальный Git diff

Вернуться в `DocType: Lab Note`.

Изменить label поля:

```text
Note → Comment
```

Сохранить.

В терминале:

```bash
cd ~/frappe/frappe-practicum-bench/apps/frappe_practicum

git diff -- \
  frappe_practicum/frappe_practicum/doctype/lab_note/lab_note.json
```

Убедиться, что metadata изменилась в JSON.

Вернуть label обратно в `Note`, снова сохранить и повторить `git diff`.

Нужно руками увидеть цикл:

```text
Desk → Save DocType → файл app → Git diff
```

---

# 11. Зафиксировать создание DocType в локальном Git

Проверить изменения:

```bash
cd ~/frappe/frappe-practicum-bench/apps/frappe_practicum

git status
git diff
```

Затем:

```bash
git add .
git diff --cached
git commit -m "Add Lab Note doctype"
```

Проверить:

```bash
git status
```

Ожидается чистое рабочее дерево.

Удалённый GitHub-репозиторий для P0 не требуется. Здесь важно понять локальную version-control модель Frappe app.

---

# 12. Что сознательно не входит в P0

Пока не нужно:

- писать Python controller;
- писать JavaScript;
- Client Script;
- Server Script;
- Workflow;
- роли и permissions;
- Customize Form;
- Export Customizations;
- fixtures;
- Reports;
- Workspace;
- Web Form;
- REST API;
- PDF.

Эти вещи не запрещены. Просто у каждой будет свой практический сценарий дальше.

---

# 13. Приёмка P0

До удаления учебного DocType ученик должен без подсказки выполнить и объяснить:

```bash
cd ~/frappe/frappe-practicum-bench
bench version
bench --site frappe-practicum.localhost list-apps
bench --site frappe-practicum.localhost scheduler status
bench --site frappe-practicum.localhost doctor

cd apps/frappe_practicum
git status
cat frappe_practicum/modules.txt
```

И показать:

- Frappe `v16.32.0`;
- app `frappe_practicum`;
- site `frappe-practicum.localhost`;
- Module `Frappe Practicum`;
- Developer Mode;
- каталог `Lab Note` в app;
- `lab_note.json`;
- обычную запись `Lab Note` в Desk;
- объяснение, почему metadata DocType попадает в Git, а Document — в базу site;
- разницу между Bench, app, site и Module.

---

# 14. Удалить учебный DocType и оставить чистый app

`Lab Note` нужен только для P0. Перед P1 его удаляем штатно и заодно смотрим обратную сторону lifecycle metadata.

Сначала удалить созданную запись `Lab Note` через обычный List/Form View.

Затем под `Administrator` открыть сам `DocType: Lab Note` и выполнить стандартное действие `Delete`.

Для стандартного DocType это разрешено в Developer Mode. Frappe v16.32.0 при таком удалении удаляет каталог controller/metadata этого DocType из Module приложения.

Проверить:

```bash
cd ~/frappe/frappe-practicum-bench/apps/frappe_practicum

git status --short
find frappe_practicum/frappe_practicum/doctype/lab_note \
  -maxdepth 1 -type f -printf '%f\n' 2>/dev/null || true
```

Каталога `lab_note` в app больше быть не должно, а Git должен показывать удаление ранее закоммиченных файлов.

Зафиксировать cleanup:

```bash
git add -A
git diff --cached
git commit -m "Remove Lab Note training doctype"
git status
```

Финальное состояние перед P1:

- учебный app установлен и работает;
- Developer Mode включён;
- scheduler/workers проверены;
- устройство standard DocType и Document понятно;
- цикл `create → change → delete` standard metadata пройден;
- одноразового `Lab Note` в app больше нет;
- Git working tree чистый.

После этого можно переходить к P1.