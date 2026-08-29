# VEQTA — старт разработки на Windows + WSL2

Статус: **главная пошаговая инструкция для локальной разработки**.

Цель: с нуля получить рабочую среду, где рядом находятся:

```text
veqta-bench/
└── apps/
    ├── frappe/   # официальный исходный код Frappe той версии, на которой запущен стенд
    └── veqta/    # наш репозиторий lazuale/veqta
```

Такой стенд позволяет одновременно:

- запускать Frappe/VEQTA локально;
- накликивать DocType в Developer Mode;
- видеть сгенерированные исходники VEQTA;
- коммитить и отправлять их в GitHub;
- открывать рядом официальный код Frappe и проверять реальное поведение Framework.

---

## 0. Что будет где

### Windows

Используется только для:

- браузера;
- PowerShell;
- VS Code;
- запуска WSL.

### Ubuntu в WSL2

Внутри Ubuntu находятся:

- Git;
- SSH-ключ GitHub;
- MariaDB;
- Redis;
- Node;
- Python;
- Bench;
- официальный Frappe;
- VEQTA.

Не устанавливать Python/Node/MariaDB для этого проекта отдельно в Windows.

---

## 1. Установить WSL2

### Что открыть

В Windows нажать:

```text
Пуск → PowerShell → Запуск от имени администратора
```

Ввести:

```powershell
wsl --status
wsl -l -v
```

Если `Ubuntu-24.04` уже есть и VERSION = `2`, перейти к разделу 2.

Если Ubuntu ещё нет:

```powershell
wsl --install -d Ubuntu-24.04
```

Если Windows попросит перезагрузку — перезагрузить компьютер.

После установки открыть:

```text
Пуск → Ubuntu 24.04 LTS
```

При первом запуске Ubuntu попросит создать Linux username и password.

Это отдельный локальный пользователь WSL. Пароль запомнить: он нужен для `sudo`.

Проверить:

```bash
cat /etc/os-release
ps -p 1 -o comm=
```

Ожидается Ubuntu 24.04 и `systemd`.

---

## 2. Поставить базовые пакеты

Все дальнейшие Linux-команды выполняются в окне **Ubuntu**, не PowerShell.

Вставить целиком:

```bash
sudo apt update
sudo apt install -y \
  git \
  openssh-client \
  redis-server \
  mariadb-server \
  mariadb-client \
  libmariadb-dev \
  pkg-config \
  curl \
  rsync

sudo systemctl enable --now redis-server mariadb
```

Проверить:

```bash
git --version
mariadb --version
redis-server --version
```

---

## 3. Настроить MariaDB

Запустить:

```bash
sudo mariadb-secure-installation
```

Если мастер спрашивает про root password — задать и записать его в безопасное место.

Этот пароль понадобится при `bench new-site`.

Не публиковать пароль в GitHub.

---

## 4. Подключить WSL к GitHub по SSH

### 4.1. Создать SSH-ключ

В Ubuntu:

```bash
ssh-keygen -t ed25519
```

Когда будет:

```text
Enter file in which to save the key (.../.ssh/id_ed25519):
```

нажать **Enter**.

Для первого локального стенда passphrase можно задать либо оставить пустой. Если оставляется пустой — два раза нажать Enter.

Показать публичный ключ:

```bash
cat ~/.ssh/id_ed25519.pub
```

Скопировать всю строку, начинающуюся с:

```text
ssh-ed25519 ...
```

**Не копировать и никому не показывать файл `~/.ssh/id_ed25519` без `.pub` — это приватный ключ.**

### 4.2. Добавить ключ на GitHub

В браузере Windows открыть GitHub.

Нажать:

```text
аватар справа сверху
→ Settings
→ SSH and GPG keys
→ New SSH key
```

Заполнить:

```text
Title: VEQTA WSL Laptop
Key type: Authentication Key
Key: вставить строку из id_ed25519.pub
```

Нажать:

```text
Add SSH key
```

### 4.3. Проверить подключение

В Ubuntu:

```bash
ssh -T git@github.com
```

При первом подключении может появиться вопрос:

```text
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

ввести:

```text
yes
```

Нормальный результат содержит:

```text
Hi lazuale! You've successfully authenticated...
```

---

## 5. Настроить имя автора Git

На GitHub открыть:

```text
Settings → Emails
```

Если включено скрытие email, GitHub показывает адрес вида `...@users.noreply.github.com`. Скопировать его.

В Ubuntu выполнить, подставив свой адрес:

```bash
git config --global user.name "lazuale"
git config --global user.email "ВАШ_EMAIL_ИЗ_GITHUB"
git config --global init.defaultBranch main
```

Проверить:

```bash
git config --global --list
```

---

## 6. Установить Node, Python и Bench

### Node 24

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 24
npm install -g yarn
```

### Python 3.14 через uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.14 --default
```

### Bench

```bash
uv tool install frappe-bench
```

Проверить:

```bash
node -v
python --version
yarn --version
bench --version
```

---

## 7. Создать Bench с актуальным стабильным Frappe

На дату подготовки инструкции проверенная стабильная версия Frappe v16 — `v16.32.0`.

Перед новым развёртыванием актуальная stable-версия должна быть повторно проверена по официальному `frappe/frappe`.

Создать bench:

```bash
mkdir -p ~/frappe
cd ~/frappe
bench init --frappe-branch v16.32.0 veqta-bench
cd ~/frappe/veqta-bench
```

Проверить:

```bash
bench version
```

И отдельно зафиксировать точный исходник Frappe:

```bash
cd ~/frappe/veqta-bench/apps/frappe
git status
git remote -v
git rev-parse HEAD
git describe --tags --always
```

`apps/frappe` — это **живой официальный исходный код Frappe**, который использует данный стенд.

Не редактировать его для VEQTA.

Вернуться:

```bash
cd ~/frappe/veqta-bench
```

---

## 8. Забрать существующий репозиторий VEQTA

Пока наш GitHub-репозиторий уже содержит документацию, но ещё должен получить Frappe app scaffold.

Клонировать его временно:

```bash
cd ~
git clone git@github.com:lazuale/veqta.git veqta-existing
```

Проверить:

```bash
cd ~/veqta-existing
git status
git remote -v
```

Должно быть чистое состояние и `origin` на `lazuale/veqta`.

---

## 9. Один раз превратить существующий репозиторий в Frappe app

Вернуться в bench:

```bash
cd ~/frappe/veqta-bench
```

Создать штатный scaffold **без отдельного Git repository**:

```bash
bench new-app --no-git veqta
```

Bench задаст несколько вопросов. Для prototype:

```text
App Title: VEQTA
App Description: Configurable work management on Frappe Framework
App Publisher: lazuale
App Email: можно указать GitHub email
App License: MIT
```

Лицензия здесь пока техническое значение scaffold; окончательное продуктовое решение фиксируется отдельно.

После команды появится:

```text
~/frappe/veqta-bench/apps/veqta
```

Теперь наложить на этот scaffold историю и документацию существующего GitHub repository:

```bash
rsync -a ~/veqta-existing/ ~/frappe/veqta-bench/apps/veqta/
```

Эта команда копирует в generated app папку `.git` существующего repository и его документацию, но не удаляет сгенерированные Frappe-файлы.

Проверить:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git remote -v
```

Теперь `apps/veqta` одновременно является:

- Frappe app;
- локальным Git repository `lazuale/veqta`;
- единственным рабочим каталогом исходников VEQTA.

Временный clone больше не нужен:

```bash
rm -rf ~/veqta-existing
```

---

## 10. Первый commit Frappe scaffold VEQTA

Находясь в:

```text
~/frappe/veqta-bench/apps/veqta
```

посмотреть изменения:

```bash
git status
```

Добавить их:

```bash
git add .
```

Посмотреть, что именно попадёт в commit:

```bash
git status
```

Создать commit:

```bash
git commit -m "Bootstrap VEQTA as Frappe app"
```

Отправить в GitHub:

```bash
git push origin main
```

После этого открыть в браузере:

```text
https://github.com/lazuale/veqta
```

и убедиться, что появились исходники Frappe app рядом с `docs/`.

---

## 11. Создать локальный site

```bash
cd ~/frappe/veqta-bench
bench new-site veqta.localhost --db-type mariadb
```

Будет запрошено:

1. MariaDB root password;
2. новый пароль пользователя `Administrator` для Frappe.

Записать Administrator password локально и **не коммитить его**.

Сделать site текущим:

```bash
bench use veqta.localhost
```

Установить VEQTA:

```bash
bench --site veqta.localhost install-app veqta
```

Проверить:

```bash
bench --site veqta.localhost list-apps
```

Ожидается:

```text
frappe
veqta
```

---

## 12. Включить Developer Mode

```bash
cd ~/frappe/veqta-bench
bench set-config -g developer_mode 1
bench --site veqta.localhost clear-cache
```

Developer Mode нужен, чтобы стандартные DocType VEQTA, созданные через Desk, сохранялись в исходники app и могли попасть в Git.

---

## 13. Запустить Frappe

В Ubuntu:

```bash
cd ~/frappe/veqta-bench
bench start
```

Это окно терминала **оставить открытым**. Пока `bench start` работает — работает dev-стенд.

В Windows открыть браузер:

```text
http://localhost:8000
```

Если site не определяется автоматически, попробовать:

```text
http://veqta.localhost:8000
```

Войти:

```text
User: Administrator
Password: пароль, заданный при bench new-site
```

### Как остановить стенд

Вернуться в окно Ubuntu, где работает `bench start`, и нажать:

```text
Ctrl + C
```

### Как запустить завтра

Открыть:

```text
Пуск → Ubuntu 24.04 LTS
```

и выполнить:

```bash
cd ~/frappe/veqta-bench
bench start
```

После этого открыть `http://localhost:8000`.

---

## 14. Поставить VS Code для удобной работы

В Windows установить **Visual Studio Code**.

В VS Code открыть Extensions (`Ctrl+Shift+X`) и установить расширение Microsoft:

```text
WSL
```

Затем в Ubuntu, из bench:

```bash
cd ~/frappe/veqta-bench
code .
```

Если команда `code` ещё не доступна, открыть VS Code → `Ctrl+Shift+P` → выбрать:

```text
WSL: Connect to WSL
```

а затем:

```text
File → Open Folder
```

и открыть:

```text
/home/<ВАШ_WSL_USER>/frappe/veqta-bench
```

В Explorer VS Code будет:

```text
apps/
├── frappe/
└── veqta/
```

### Где смотреть Frappe

Официальный код:

```text
apps/frappe/frappe/
```

Например:

```text
apps/frappe/frappe/model/workflow.py
apps/frappe/frappe/workflow/
apps/frappe/frappe/desk/form/assign_to.py
apps/frappe/frappe/desk/doctype/kanban_board/
```

### Где писать VEQTA

Только:

```text
apps/veqta/
```

Не изменять `apps/frappe` ради реализации функций VEQTA.

---

## 15. Как сверять VEQTA с исходником Frappe

Перед техническим решением:

### 1. Узнать точный Frappe стенда

```bash
cd ~/frappe/veqta-bench/apps/frappe
git rev-parse HEAD
git describe --tags --always
```

### 2. Найти функцию в исходниках

Пример поиска Assignment:

```bash
cd ~/frappe/veqta-bench/apps/frappe
grep -R "def add" frappe/desk/form/assign_to.py
```

Или глобальный поиск через VS Code:

```text
Ctrl + Shift + F
```

например искать:

```text
apply_workflow
```

### 3. Смотреть конкретный файл рядом с VEQTA

Не копировать Frappe-код в VEQTA без необходимости. Сначала понять публичный механизм/hook/API, который предоставляет Framework.

### 4. Если документация и код расходятся

Зафиксировать:

- версию/tag;
- commit SHA;
- путь исходного файла;
- наблюдаемое поведение.

После этого обновить соответствующий документ/Issue VEQTA.

---

## 16. Ежедневный Git workflow VEQTA

Исходники VEQTA находятся здесь:

```bash
cd ~/frappe/veqta-bench/apps/veqta
```

### Перед началом работы

```bash
git status
git pull --ff-only origin main
```

### После изменения/накликивания

Сначала посмотреть:

```bash
git status
```

Затем:

```bash
git diff
```

Добавить изменения:

```bash
git add .
```

Проверить staged diff:

```bash
git diff --cached
```

Создать commit:

```bash
git commit -m "КРАТКОЕ ОПИСАНИЕ ИЗМЕНЕНИЯ"
```

Отправить:

```bash
git push origin main
```

Для prototype допускается прямой `main`. Когда начнётся полноценная разработка несколькими независимыми изменениями, можно перейти на feature branches + Pull Requests.

---

## 17. Что значит «накликал → попало в Git»

Если Developer Mode включён и создаётся **стандартный DocType приложения VEQTA**, Frappe создаёт/изменяет файлы внутри:

```text
apps/veqta/veqta/...
```

После изменения через Desk выполнить:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
```

Новые/изменённые JSON/Python/JS-файлы должны быть видны Git.

Не считать изменение зафиксированным, пока оно не прошло:

```text
Desk
→ files in apps/veqta
→ git diff
→ commit
→ push
```

---

## 18. Не коммитить

Никогда не добавлять в VEQTA repository:

- MariaDB passwords;
- Administrator password;
- private SSH key;
- `site_config.json` с секретами;
- database dumps с реальными данными;
- `.env` с секретами;
- содержимое `sites/veqta.localhost/private`;
- весь bench целиком.

В Git идёт **только app VEQTA и документация проекта**.

Frappe не копируется в repository VEQTA: его официальный repository уже находится отдельно в `apps/frappe`.

---

## 19. Минимальная карта каталогов

```text
/home/<user>/frappe/veqta-bench/
│
├── apps/
│   ├── frappe/             <- официальный git repo Frappe
│   │   └── frappe/
│   │
│   └── veqta/              <- git repo lazuale/veqta
│       ├── .git/
│       ├── docs/
│       ├── pyproject.toml
│       ├── veqta/
│       └── ...
│
├── sites/                  <- локальные данные стенда, НЕ наш source repo
├── env/                    <- Python env Bench
├── logs/
└── Procfile
```

---

## 20. Главные команды, которые нужны каждый день

### Запустить VEQTA

```bash
cd ~/frappe/veqta-bench
bench start
```

### Открыть код

```bash
cd ~/frappe/veqta-bench
code .
```

### Посмотреть изменения VEQTA

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

### Отправить изменения

```bash
git add .
git commit -m "Описание"
git push origin main
```

### Узнать точную версию Frappe

```bash
cd ~/frappe/veqta-bench/apps/frappe
git describe --tags --always
git rev-parse HEAD
```

### Вернуться в VEQTA

```bash
cd ~/frappe/veqta-bench/apps/veqta
```

---

## 21. Правило разработки VEQTA

Перед написанием собственной реализации:

1. проверить официальную документацию текущего Frappe;
2. открыть соответствующий код в `apps/frappe`;
3. проверить фактическое поведение на локальном site;
4. только затем решать, нужен ли код VEQTA;
5. согласованное решение зафиксировать в `docs/` и Git.

Коротко:

> **Документация → исходники Frappe → живой тест → решение VEQTA → commit.**
