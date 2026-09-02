# Основы перед первым проектом

Этот блок выполняется после [SETUP_WSL2.md](SETUP_WSL2.md). На стенде уже существуют
Bench и `platform-check.localhost`, но ещё нет учебных business app.

## F0.1. Проверить, где выполняются команды

Открыть Debian в WSL2:

```bash
whoami
pwd
cd ~/frappe/frappe-practicum-bench
pwd
bench version
```

`pwd` должен закончиться на `/frappe/frappe-practicum-bench`. Это корень Bench. В нём
находятся общие каталоги `apps`, `sites`, `env` и служебные файлы процессов.

Посмотреть верхний уровень без изменения файлов:

```bash
find . -maxdepth 1 -mindepth 1 -printf '%f\n' | sort
```

Не добавлять весь Bench в Git. Каждый созданный через `bench new-app` app получит
собственный репозиторий внутри `apps/`.

### Состояние после F0.1

- понятен каталог Bench;
- `bench version` показывает Frappe `16.32.0`;
- команды выполняются в Debian, а не в PowerShell.

## F0.2. Разобрать Bench, site и app

Проверить установленные app:

```bash
bench --site platform-check.localhost list-apps
```

Ожидается только `frappe`.

Связь объектов:

```text
Bench
├── apps/frappe/                 исходники framework
└── sites/platform-check.localhost/  конфигурация одного site
```

Bench может содержать несколько app и несколько site. App лежит в файловой системе и
может устанавливаться на разные site. Site хранит свою базу, пользователей, настройки и
список установленных app.

Команда `bench new-app` создаёт пакет исходников. Команда `bench --site ... install-app`
устанавливает этот пакет на выбранный site. Это разные действия.

### Проверка понимания

Ответить без подсказки:

1. Почему создание app не устанавливает его на site?
2. Почему два site в одном Bench не обязаны иметь одинаковый список app?
3. Почему рабочие Equipment не должны появляться в Git после установки app?

## F0.3. Познакомиться с Desk

Из корня Bench запустить процессы разработки:

```bash
bench start
```

Терминал останется занят журналом процессов. Пока `bench start` работает, открыть в
Windows:

```text
http://platform-check.localhost:8000
```

Войти как `Administrator` с паролем, заданным при `bench new-site`.

Найти в интерфейсе:

- верхнюю строку поиска — Awesomebar;
- Apps Page;
- список Workspace;
- меню пользователя;
- переключатель языка и темы;
- список User;
- список DocType.

Ничего не создавать. Цель — научиться открывать объекты через Awesomebar, не запоминать
расположение пунктов меню. В Frappe v16 навигация может меняться между Workspace, а
поиск остаётся надёжной точкой входа.

Открыть DocType `User` только для просмотра. Найти:

- системный `name`;
- Module;
- список полей;
- таблицу Permissions;
- настройки naming и поведения.

Закрыть форму без сохранения.

Остановить процессы в терминале сочетанием `Ctrl+C`.

### Состояние после F0.3

- Desk открывается;
- ученик умеет находить DocType и User через Awesomebar;
- `platform-check.localhost` не содержит учебных изменений.

## F0.4. Отличить DocType от Document

DocType описывает вид документов. Например, будущий DocType `Equipment` задаст поля
Asset Code, Category и Status. Конкретные записи `EQ-0001` и `EQ-0002` будут Document
этого DocType.

```text
DocType Equipment
├── Document EQ-0001
├── Document EQ-0002
└── Document EQ-0003
```

Изменение DocType меняет модель всех Equipment. Изменение Document меняет одну единицу
оборудования.

Standard DocType создаётся в Developer Mode, принадлежит Module app и записывается в
JSON внутри репозитория. Custom DocType остаётся конфигурацией site. В практикуме
постоянная модель создаётся Standard, потому что app должен устанавливаться на чистый
site.

### Проверка понимания

Определить тип каждого объекта:

| Объект | DocType или Document |
|---|---|
| описание полей Equipment | DocType |
| карточка `EQ-0001` | Document |
| описание полей User | DocType |
| пользователь `operator@example.com` | Document |

## F0.5. Минимум Git до первого commit

Git фиксирует изменения исходников app. Он не заменяет базу site.

Команды, которые используются в каждом проекте:

```bash
git status --short --branch
git diff --check
git diff --stat
git diff
git add .
git commit -m "Краткое описание законченного изменения"
git log --oneline --decorate -5
```

Смысл команд:

| Команда | Что показывает или делает |
|---|---|
| `git status` | изменённые, новые и подготовленные файлы |
| `git diff` | ещё не подготовленные изменения |
| `git diff --check` | ошибки пробелов и конфликтные маркеры |
| `git add .` | подготавливает изменения текущего app к commit |
| `git commit` | создаёт локальную точку истории |
| `git log` | показывает созданные commits |

Перед `git add .` всегда выполнять `pwd`. Команда должна запускаться из репозитория
конкретного app, а не из домашнего каталога или корня Bench.

Remote и `git push` не требуются для прохождения локальной лабораторной. Их настраивают
после первого проверенного commit конкретного app.

## Gate основ

Перед P1 ученик должен уметь:

- открыть Debian и перейти в Bench;
- запустить и остановить `bench start`;
- открыть `platform-check.localhost`;
- найти DocType через Awesomebar;
- объяснить различие Bench, site, app, Module, DocType и Document;
- объяснить, почему Git содержит metadata app, но не рабочую базу site.

Если любой пункт непонятен, вернуться к соответствующему разделу. Следующий шаг:
[P1 — пошаговые лабораторные](projects/01-equipment-register/LABS.md).
