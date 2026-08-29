# VEQTA — старт локальной разработки на WSL2

Статус: **единственная актуальная инструкция локального dev-стенда**.

Эта инструкция нужна для первого bootstrap реального Frappe app VEQTA на Windows + WSL2.

> Выполнять разделы по порядку. Если команда завершилась ошибкой — не продолжать следующий раздел, пока ошибка не разобрана.

## Что получится

```text
Windows
├── браузер
├── VS Code
└── WSL2 / Ubuntu 24.04
    └── ~/frappe/veqta-bench/
        ├── apps/
        │   ├── frappe/   # официальный Frappe текущего стенда
        │   └── veqta/    # git repository lazuale/veqta
        ├── sites/
        └── ...
```

Bench и app хранятся в Linux filesystem WSL, **не в `/mnt/c/...`**.

## 1. Проверить WSL2

Открыть PowerShell от администратора:

```powershell
wsl --status
wsl -l -v
```

Нужен дистрибутив Ubuntu с `VERSION 2`.

Если его нет:

```powershell
wsl --install -d Ubuntu-24.04
```

После установки открыть `Ubuntu 24.04 LTS` из меню Пуск и создать обычного Linux-пользователя.

Проверить внутри Ubuntu:

```bash
cat /etc/os-release
ps -p 1 -o comm=
```

Ожидается Ubuntu 24.04 и `systemd`.

## 2. Поставить системные пакеты

Все следующие команды выполняются **в Ubuntu WSL**, а не в PowerShell.

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

Проверка:

```bash
git --version
mariadb --version
redis-server --version
```

## 3. Настроить MariaDB

```bash
sudo mariadb-secure-installation
```

Запомнить выбранные реквизиты администратора MariaDB. Они могут понадобиться при `bench new-site`.

Не хранить пароли в repository.

## 4. Подключить WSL к GitHub

Создать SSH key:

```bash
ssh-keygen -t ed25519
```

Для стандартного пути нажать Enter. Публичный ключ показать командой:

```bash
cat ~/.ssh/id_ed25519.pub
```

В GitHub открыть:

```text
Settings → SSH and GPG keys → New SSH key
```

Добавить **только** содержимое `id_ed25519.pub`.

Проверить:

```bash
ssh -T git@github.com
```

Ожидается успешная аутентификация пользователя `lazuale`.

Приватный `~/.ssh/id_ed25519` никому не передавать и в Git не коммитить.

## 5. Настроить автора Git

```bash
git config --global user.name "lazuale"
git config --global user.email "ВАШ_GITHUB_EMAIL"
git config --global init.defaultBranch main
```

Проверить:

```bash
git config --global --list
```

## 6. Поставить Node, Python и Bench

### Node 24

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 24
npm install -g yarn
```

### Python 3.14

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

## 7. Создать Bench с проверенной stable-версией Frappe

Перед фактическим выполнением проверить текущую stable-версию согласно `DEVELOPMENT.md`.

На дату этой инструкции проверена `v16.32.0`:

```bash
mkdir -p ~/frappe
cd ~/frappe
bench init --frappe-branch v16.32.0 veqta-bench
cd ~/frappe/veqta-bench
bench version
```

Зафиксировать точный Frappe стенда:

```bash
cd ~/frappe/veqta-bench/apps/frappe
git describe --tags --always
git rev-parse HEAD
```

`apps/frappe` не редактируется ради VEQTA.

## 8. Превратить существующий repository в Frappe app

Repository уже существует и содержит документацию, поэтому нельзя просто создать новый независимый Git repository тем же именем.

### 8.1. Временно клонировать существующий repository

```bash
cd ~
git clone git@github.com:lazuale/veqta.git veqta-existing
```

### 8.2. Создать штатный Frappe scaffold без нового Git

```bash
cd ~/frappe/veqta-bench
bench new-app --no-git veqta
```

Интерактивные значения prototype:

```text
App Title: VEQTA
App Description: Configurable work management on Frappe Framework
App Publisher: lazuale
App Email: ваш GitHub email
```

Поле license при scaffold **не считается продуктовым решением**; актуальный статус лицензии см. `DECISIONS.md`.

### 8.3. Соединить scaffold с существующей Git history

```bash
rsync -a ~/veqta-existing/ ~/frappe/veqta-bench/apps/veqta/
cd ~/frappe/veqta-bench/apps/veqta
git status
git remote -v
```

`origin` должен указывать на `lazuale/veqta`.

После проверки:

```bash
rm -rf ~/veqta-existing
```

Теперь `apps/veqta` одновременно является Frappe app и рабочим Git repository проекта.

## 9. Сделать первый commit scaffold

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git add .
git diff --cached
git commit -m "Bootstrap VEQTA as Frappe app"
git push origin main
```

После push repository должен содержать не только `docs/`, но и настоящий Frappe app scaffold.

## 10. Создать локальный site

```bash
cd ~/frappe/veqta-bench
bench new-site veqta.localhost --db-type mariadb
bench use veqta.localhost
bench --site veqta.localhost install-app veqta
bench --site veqta.localhost list-apps
```

Ожидаются как минимум:

```text
frappe
veqta
```

Пароль Frappe `Administrator`, задаваемый при `new-site`, не коммитить.

## 11. Включить Developer Mode

```bash
cd ~/frappe/veqta-bench
bench set-config -g developer_mode 1
bench --site veqta.localhost clear-cache
```

Developer Mode нужен для разработки стандартных DocType приложения и записи их metadata в исходное дерево app.

## 12. Запустить стенд

```bash
cd ~/frappe/veqta-bench
bench start
```

Окно оставить открытым.

В браузере Windows открыть:

```text
http://localhost:8000
```

Если site не определяется автоматически:

```text
http://veqta.localhost:8000
```

Войти как `Administrator`.

Остановить стенд: `Ctrl+C` в терминале с `bench start`.

Следующий запуск обычно сводится к:

```bash
cd ~/frappe/veqta-bench
bench start
```

## 13. VS Code

В Windows установить VS Code и расширение Microsoft `WSL`.

Из Ubuntu:

```bash
cd ~/frappe/veqta-bench
code .
```

В workspace будут рядом:

```text
apps/frappe/   # код Framework
apps/veqta/    # наш код
```

VEQTA редактируется только в `apps/veqta`.

## 14. После любого накликивания VEQTA

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

Если согласованная конфигурация не появилась в файлах app, работа не закончена: определить штатный механизм Frappe для её экспорта и только после этого commit/push.

Полное правило: `DEVELOPMENT.md`.

## 15. Следующий практический документ

После рабочего запуска стенда выполнять испытания только по:

`PROTOTYPE_V0_1.md`.
