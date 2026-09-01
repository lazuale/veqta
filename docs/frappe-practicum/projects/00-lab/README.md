# P0. Учебное приложение

P0 нужен не для изучения бизнес-модели. Здесь мы разбираемся, **из чего реально состоит Frappe-приложение**, как связаны Bench, app, site, Module, Desk и файлы в Git.

После P0 должно исчезнуть главное непонимание новичка: «я что-то накликал в браузере — а где это вообще живёт?»

Базовая версия практикума: **Frappe Framework v16.32.0**.

## Что должно получиться

К концу P0 у вас есть:

- рабочий Bench с Frappe v16.32.0;
- app `veqta`;
- site `veqta.localhost`;
- app установлен на site;
- включён Developer Mode;
- понятна структура app и его default Module;
- открыт и пройден основной интерфейс Desk v16;
- scheduler не отключён;
- background workers запускаются вместе с dev-стендом;
- создан первый стандартный DocType приложения;
- видно, какие файлы Frappe создал в app;
- создан обычный Document этого DocType;
- понятно, почему запись Document не появляется в Git, а изменение DocType появляется.

PDF в P0 не проверяем. Печатный сценарий начинается в P5.

---

# 1. Поднять учебный стенд

Если стенд ещё не развёрнут, пройти инструкцию:

[START_HERE_WSL2.md](../../../START_HERE_WSL2.md)

Она должна закончиться рабочим состоянием:

```text
~/frappe/veqta-bench/
├── apps/
│   ├── frappe/
│   └── veqta/
└── sites/
    └── veqta.localhost/
```

В `apps/frappe` должен быть точный Frappe `v16.32.0`, а `apps/veqta` должен быть Git-репозиторием VEQTA.

Если стенд уже был развёрнут раньше, установку повторять не нужно. Сразу переходите к проверке.

## Проверка

В Debian/WSL:

```bash
cd ~/frappe/veqta-bench

bench version
bench --site veqta.localhost list-apps

cd apps/frappe
git describe --tags --exact-match
cd ../..
```

Нужно увидеть:

```text
frappe 16.32.0 ...
```

В списке приложений site должны быть минимум:

```text
frappe
veqta
```

А `git describe` для `apps/frappe` должен вернуть:

```text
v16.32.0
```

Если tag другой — практикум пока не начинать. Сначала привести стенд к базовой версии курса.

---

# 2. Разделить в голове Bench, app и site

Откройте корень Bench:

```bash
cd ~/frappe/veqta-bench
ls -la
```

Посмотрите только три каталога:

```text
apps/
sites/
logs/
```

Для P0 достаточно понимать их так:

```text
Bench
├── apps/      код установленных приложений
├── sites/     отдельные экземпляры Frappe и их данные/настройки
└── logs/      журналы процессов Bench
```

Теперь:

```bash
ls -la apps
ls -la sites
```

Главная мысль:

```text
app != site
```

`veqta` — приложение.

`veqta.localhost` — конкретный site, на который это приложение установлено.

Один app в дальнейшем можно поставить на другой site. Именно это мы отдельно докажем в P2.

---

# 3. Посмотреть структуру app

Перейдите в репозиторий приложения:

```bash
cd ~/frappe/veqta-bench/apps/veqta
pwd
git status
```

Посмотрите верхний уровень:

```bash
find . -maxdepth 2 -type f | sort
```

Нас сейчас интересуют:

```text
pyproject.toml
veqta/hooks.py
veqta/modules.txt
veqta/patches.txt
```

Посмотрите `modules.txt`:

```bash
cat veqta/modules.txt
```

Там должен быть default Module, который Frappe создал вместе с app.

Отдельно создавать первый Module после `bench new-app` не нужно.

Посмотрите начало `hooks.py`:

```bash
sed -n '1,120p' veqta/hooks.py
```

Пока ничего в нём не меняем.

На этом этапе нужно только понять:

- `pyproject.toml` описывает Python package приложения;
- `hooks.py` — штатная точка конфигурации app;
- `modules.txt` перечисляет Module приложения;
- `patches.txt` понадобится для миграций, когда появятся patches;
- Module — это не отдельное приложение, а логическая часть app.

---

# 4. Проверить Developer Mode

В P0 и следующих проектах мы создаём **стандартные объекты своего app**, поэтому Developer Mode должен быть включён.

Проверить текущую конфигурацию:

```bash
cd ~/frappe/veqta-bench

grep '"developer_mode"' sites/common_site_config.json
```

Ожидается:

```text
"developer_mode": 1
```

Если строки нет или значение не `1`:

```bash
bench set-config -g developer_mode 1
bench --site veqta.localhost clear-cache
```

Почему это важно: в Developer Mode Frappe при сохранении стандартного DocType создаёт его boilerplate и metadata-файлы в app, чтобы их можно было хранить в Git.

---

# 5. Запустить Desk

В первом терминале:

```bash
cd ~/frappe/veqta-bench
bench start
```

Этот терминал пока не закрывайте.

В браузере Windows откройте:

```text
http://veqta.localhost:8000
```

Войдите как `Administrator`.

## Что нужно найти в Desk v16

Не настраивайте ничего. Просто пройдите интерфейс и найдите:

- Apps Page;
- Workspace Sidebar;
- Public Workspaces;
- My Workspaces;
- Awesomebar / command palette;
- обычный List View;
- обычный Form View;
- меню пользователя и Settings.

Важно: установка app на site **не обязана автоматически создавать красивую плитку VEQTA на Apps Page**. Это отдельная настройка приложения и сейчас нам не нужна.

Цель шага — понять, как искать сущности Frappe, а не собирать рабочий Workspace. Workspace полноценно появится в P5.

---

# 6. Проверить scheduler и workers

Оставьте `bench start` работающим.

Откройте второй терминал Debian/WSL:

```bash
cd ~/frappe/veqta-bench
```

Проверьте scheduler:

```bash
bench --site veqta.localhost scheduler status
```

Нормальное состояние:

```text
Scheduler is enabled for site veqta.localhost
```

Затем:

```bash
bench --site veqta.localhost doctor
```

`doctor` показывает состояние scheduler, workers и очередей. Точное количество workers не фиксируем: оно зависит от конфигурации Bench. Здесь важно, чтобы команда выполнялась без ошибки соединения с Redis/queues и не показывала, что scheduler отключён.

Посмотреть очередь можно отдельно:

```bash
bench --site veqta.localhost show-pending-jobs
```

Пустая очередь на новом стенде — нормальное состояние.

В P6 мы вернёмся к scheduler уже как к рабочему механизму автоматизации. Сейчас достаточно доказать, что инфраструктура для фоновых задач жива.

---

# 7. Создать первый стандартный DocType

Теперь делаем первое изменение, которое должно попасть из Desk в файлы app.

В Desk откройте Awesomebar и найдите:

```text
DocType
```

Откройте список DocType и нажмите `New`.

Создайте:

```text
Name:   P0 Lab Note
Module: VEQTA
```

Не включайте `Custom?`.

Добавьте только три поля:

| Label | Type | Mandatory | Default |
|---|---|---:|---|
| Title | Data | Yes | |
| Note | Small Text | No | |
| Is Active | Check | No | 1 |

Ничего больше пока не настраиваем. Naming, Title Field, Search Fields, permissions и остальные свойства DocType будут разбираться в следующих проектах.

Нажмите `Save`.

Frappe должен сохранить стандартный DocType в Module приложения.

---

# 8. Найти файлы, которые создал Frappe

Вернитесь во второй терминал:

```bash
cd ~/frappe/veqta-bench/apps/veqta
```

Посмотрите состояние Git:

```bash
git status --short
```

Теперь найдите каталог DocType:

```bash
find veqta/veqta/doctype/p0_lab_note -maxdepth 1 -type f -printf '%f\n' | sort
```

Для стандартного DocType Frappe создаёт boilerplate. В каталоге должны появиться файлы вроде:

```text
__init__.py
p0_lab_note.js
p0_lab_note.json
p0_lab_note.py
test_p0_lab_note.py
```

Самый важный сейчас файл:

```text
p0_lab_note.json
```

Посмотрите его:

```bash
sed -n '1,240p' veqta/veqta/doctype/p0_lab_note/p0_lab_note.json
```

Найдите в JSON:

- `name`;
- `module`;
- `fields`;
- созданные `fieldname`;
- типы полей;
- обязательность `Title`;
- default для `Is Active`.

Не редактируйте JSON вручную.

Сейчас задача — увидеть связь:

```text
DocType в Desk
        ↓ Save
metadata
        ↓
JSON + boilerplate в app
        ↓
Git
```

Наличие `.py` и `.js` рядом с DocType **не означает, что мы уже начали программировать**. Это штатный boilerplate стандартного DocType. В базовом практикуме эти файлы пока не редактируем.

---

# 9. Создать обычный Document

В Desk после сохранения DocType перейдите в список `P0 Lab Note`.

Если кнопка перехода не появилась, найдите `P0 Lab Note` через Awesomebar.

Создайте запись:

```text
Title:     Первая запись P0
Note:      Это обычный Document, а не новый DocType
Is Active: включено
```

Сохраните.

Теперь снова выполните:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status --short
```

Создание ещё одного Document **не должно создавать новый каталог в app**.

Это ключевое различие P0:

```text
DocType
= описание типа документов
= metadata приложения
= для стандартного объекта хранится в app

Document
= конкретная запись этого типа
= хранится в базе site
= сам по себе не является исходным кодом app
```

На этом примере также видно, почему Git не является резервной копией рабочих данных site.

---

# 10. Сделать одно изменение DocType и увидеть diff

Вернитесь в сам `DocType: P0 Lab Note`.

Измените label поля:

```text
Note
```

на:

```text
Comment
```

Сохраните DocType.

В терминале:

```bash
cd ~/frappe/veqta-bench/apps/veqta

git diff -- veqta/veqta/doctype/p0_lab_note/p0_lab_note.json
```

Нужно увидеть изменение metadata в JSON.

Верните label обратно в `Note`, снова сохраните и ещё раз выполните `git diff`.

Смысл упражнения не в самом label. Нужно руками увидеть цикл:

```text
Desk → Save DocType → файл app → Git diff
```

---

# 11. Понять, что мы пока сознательно не делаем

На P0 не нужно:

- писать Python controller;
- редактировать `p0_lab_note.py`;
- писать JavaScript;
- добавлять Client Script или Server Script;
- настраивать Workflow;
- создавать роли и permissions;
- делать Workspace VEQTA;
- настраивать fixtures;
- делать Export Customizations;
- подключать REST API;
- ставить PDF-зависимость.

Не потому, что Frappe этого «не позволяет», а потому что эти механизмы пока не нужны задаче P0.

---

# 12. Контрольная проверка P0

В терминале:

```bash
cd ~/frappe/veqta-bench

echo '=== VERSION ==='
bench version

echo '=== APPS ON SITE ==='
bench --site veqta.localhost list-apps

echo '=== SCHEDULER ==='
bench --site veqta.localhost scheduler status

echo '=== FRAPPE TAG ==='
cd apps/frappe
git describe --tags --exact-match
cd ../..

echo '=== VEQTA MODULES ==='
cat apps/veqta/veqta/modules.txt

echo '=== P0 DOCTYPE FILES ==='
find apps/veqta/veqta/veqta/doctype/p0_lab_note -maxdepth 1 -type f -printf '%f\n' | sort

echo '=== GIT ==='
cd apps/veqta
git status --short
```

После этого в Desk проверьте руками:

1. `P0 Lab Note` существует как DocType.
2. В его Module указано `VEQTA`.
3. В списке `P0 Lab Note` есть созданная запись.
4. Запись открывается как обычный Form.
5. Awesomebar находит DocType и список документов.

---

# 13. Что нужно уметь объяснить перед P1

Не переходите дальше, пока своими словами не можете ответить на вопросы.

### Что такое Bench?

Рабочее окружение, в котором находятся приложения, sites и процессы Frappe.

### Что такое app?

Устанавливаемый пакет функциональности. Для нас сейчас это `veqta`.

### Что такое site?

Конкретный экземпляр Frappe со своей базой данных и конфигурацией. Сейчас это `veqta.localhost`.

### Что такое Module?

Логическая группа объектов внутри app. Это не второй app и не второй site.

### Зачем Developer Mode?

Чтобы стандартные объекты приложения создавались как version-controlled metadata/boilerplate внутри app.

### Чем DocType отличается от Document?

DocType описывает структуру и поведение типа документов. Document — конкретная запись этого типа.

### Что после создания `P0 Lab Note` появилось в Git?

Metadata и boilerplate стандартного DocType.

### Что после создания записи «Первая запись P0» появилось в Git?

Ничего нового. Сама запись находится в базе данных site.

### Почему наличие `.py` и `.js` рядом с DocType ещё не означает, что мы пишем собственную бизнес-логику?

Потому что Frappe создаёт эти файлы как стандартный boilerplate DocType. Мы пока их не редактируем.

---

# 14. Результат P0

P0 принят, если одновременно выполняется всё:

- Frappe — `v16.32.0`;
- `veqta` установлен на `veqta.localhost`;
- Developer Mode включён;
- default Module приложения найден в `modules.txt`;
- Desk v16 открыт и базовая навигация понятна;
- scheduler включён;
- `bench doctor` выполняется без инфраструктурной ошибки;
- создан стандартный `P0 Lab Note`;
- его JSON и boilerplate найдены в `apps/veqta`;
- Git показывает изменения DocType;
- создан обычный Document `P0 Lab Note`;
- понятно, почему его данные не появились в Git.

`P0 Lab Note` пока оставляем как диагностический учебный объект. В начале P1 он больше не нужен для объяснения устройства платформы; перед созданием реальной модели P1 его можно удалить штатным способом после проверки фактического поведения удаления на стенде.

Следующий проект: **P1 — Реестр оборудования**.

---

# Источники проверки

Общий список источников курса: [REFERENCES.md](../../REFERENCES.md).

Для P0 особенно важны официальные разделы:

- Create an App;
- Create a Site;
- Create a DocType;
- Developer Mode;
- Apps;
- Diagnosing The Scheduler;
- исходники тега `v16.32.0`.

Если фактический стенд v16.32.0 ведёт себя не так, как описано здесь, не обходите проблему костылём: зафиксируйте расхождение и исправьте практикум.