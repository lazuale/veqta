# VEQTA — чистовая установка dev-стенда на WSL2

Эта инструкция поднимает **локальный стенд разработки VEQTA с нуля на Windows через WSL2 / Ubuntu 24.04**.

Это эталонный сценарий первого стенда. Команды выполняются **строго сверху вниз**. Если проверка шага не совпала с ожидаемым результатом — следующий шаг не выполнять.

После завершения получится:

```text
Windows
└── WSL2 / Ubuntu 24.04
    └── ~/frappe/veqta-bench/
        ├── env/                       # Python environment Bench
        ├── apps/
        │   ├── frappe/                # Frappe Framework v16.32.0
        │   └── veqta/                 # lazuale/veqta + Frappe app
        └── sites/
            └── veqta.localhost/       # локальный Frappe site
```

Desk будет доступен в Windows:

```text
http://veqta.localhost:8000
```

Вход:

```text
User: Administrator
Password: пароль, заданный при создании site
```

## 0. Зафиксированный baseline

```text
WSL distro              Ubuntu 24.04 LTS
MariaDB                 11.8.9
wkhtmltopdf             0.12.6.1-2, patched Qt
NVM                     0.40.7
Node.js                 24.20.0 LTS
npm                     11.19.0
Yarn Classic            1.22.22
uv                      0.12.7
Python                  3.14.7
Frappe Bench            5.31.0
Frappe Framework        v16.32.0
```

Ubuntu system libraries и Redis берём из актуальных security/update repositories Ubuntu 24.04. Их patch-версии отдельно не фиксируем.

Не заменять версии выше на `latest`, `24`, `3.14`, `develop` или другую ветку без отдельного обновления baseline.

Пароли при вводе в Linux обычно **не отображаются вообще** — это нормально.

В ходе установки будут разные секреты:

```text
Linux user password       пароль пользователя Ubuntu
MariaDB frappe_admin      пароль администратора БД для Bench
Frappe Administrator      пароль входа в Desk
```

Не сохранять их в Git, README, Issue или исходном коде.

---

## 1. WSL2 / Ubuntu 24.04

### 1.1. Новая установка

Открыть **PowerShell от имени администратора**:

```powershell
wsl --update
wsl --install -d Ubuntu-24.04
```

После установки открыть `Ubuntu 24.04` из меню Пуск.

При первом запуске создать Linux-пользователя. Имя может быть любым, например `dev`:

```text
Enter new UNIX username: dev
New password:             придумать пароль Linux-пользователя
Retype new password:      повторить пароль
```

### 1.2. Если нужен действительно чистый WSL вместо уже сломанного

**Внимание: `wsl --unregister` полностью удаляет выбранный Linux-дистрибутив и все его файлы.**

В PowerShell:

```powershell
wsl -l -v
```

Если сознательно начинаем заново и дистрибутив называется `Ubuntu-24.04`:

```powershell
wsl --terminate Ubuntu-24.04
wsl --unregister Ubuntu-24.04
wsl --install -d Ubuntu-24.04
```

После этого снова открыть Ubuntu и создать Linux-пользователя.

### 1.3. Проверить Ubuntu, systemd и рабочий каталог

Уже **в Ubuntu**, не в PowerShell, выполнить именно этот блок:

```bash
cd ~
. /etc/os-release

echo "USER=$(whoami)"
echo "UBUNTU=$VERSION_ID"
echo "INIT=$(ps -p 1 -o comm=)"
echo "HOME=$HOME"
echo "PWD=$PWD"
```

`cd ~` обязателен: если WSL был открыт из PowerShell, запущенного в `C:\Windows\System32`, начальный каталог может быть `/mnt/c/WINDOWS/System32`. Для стенда работаем из домашнего Linux-каталога.

Если Linux-пользователь создан как `dev`, контрольный вывод должен быть **ровно по смыслу таким**:

```text
USER=dev
UBUNTU=24.04
INIT=systemd
HOME=/home/dev
PWD=/home/dev
```

Если имя пользователя другое, оно должно одинаково отображаться в `USER`, `HOME` и `PWD`. Критические значения:

```text
UBUNTU=24.04
INIT=systemd
HOME=/home/<ваш_пользователь>
PWD=/home/<ваш_пользователь>
```

Если `INIT` не `systemd`:

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Затем в PowerShell:

```powershell
wsl --shutdown
```

Снова открыть Ubuntu и **повторить весь контрольный блок из начала пункта 1.3**. Следующий шаг выполнять только когда `UBUNTU=24.04`, `INIT=systemd`, а `PWD` совпадает с `HOME`.

Все Linux-команды ниже выполняются **в Ubuntu WSL**.

---

## 2. Проверка сети и DNS

До установки пакетов проверяем все основные хосты, откуда дальше будут скачиваться компоненты:

```bash
set -e

for host in \
  github.com \
  raw.githubusercontent.com \
  dlm.mariadb.com \
  nodejs.org \
  astral.sh
do
  if getent ahosts "$host" >/dev/null; then
    echo "OK  $host"
  else
    echo "DNS ERROR: $host"
    exit 1
  fi
done

curl -fsSL https://dlm.mariadb.com/3/MariaDB/mariadb_repo_setup -o /dev/null

echo "NETWORK OK"
```

Должно закончиться:

```text
NETWORK OK
```

Если есть `DNS ERROR`, `Could not resolve host` или ошибка `curl` — **дальше не идти**.

---

## 3. Базовые системные пакеты

```bash
sudo apt update

sudo apt install -y \
  build-essential \
  git \
  openssh-client \
  curl \
  ca-certificates \
  rsync \
  pkg-config \
  cron \
  redis-server \
  xvfb \
  libfontconfig1 \
  xfonts-75dpi \
  xfonts-base

sudo systemctl enable --now redis-server
sudo systemctl enable --now cron
```

При запросе:

```text
[sudo] password for <ваш_пользователь>:
```

ввести пароль Linux-пользователя.

Проверить:

```bash
systemctl is-active redis-server
redis-cli ping
systemctl is-active cron
```

Ожидается:

```text
active
PONG
active
```

---

## 4. MariaDB 11.8.9

Frappe v16 требует MariaDB 11.8. В Ubuntu 24.04 стандартный repository содержит MariaDB 10.11, поэтому **нельзя сначала выполнять обычный `apt install mariadb-server`**.

Сначала подключаем официальный MariaDB repository, проверяем Candidate и только после этого устанавливаем сервер.

### 4.1. Скачать официальный repository setup

```bash
curl -fL --retry 3 \
  https://dlm.mariadb.com/3/MariaDB/mariadb_repo_setup \
  -o /tmp/mariadb_repo_setup

chmod +x /tmp/mariadb_repo_setup
```

Проверить:

```bash
test -s /tmp/mariadb_repo_setup && echo "repo setup downloaded"
```

Ожидается:

```text
repo setup downloaded
```

### 4.2. Подключить именно MariaDB 11.8.9

```bash
sudo /tmp/mariadb_repo_setup \
  --mariadb-server-version="mariadb-11.8.9" \
  --skip-maxscale

sudo apt update
```

До установки проверить:

```bash
apt-cache policy mariadb-server
```

В `Candidate` должна быть версия `11.8.9`, например:

```text
Candidate: 1:11.8.9+maria~ubu2404
```

Автоматическая стоп-проверка:

```bash
MARIADB_CANDIDATE="$(apt-cache policy mariadb-server | awk '/Candidate:/ {print $2}')"

echo "MariaDB candidate: $MARIADB_CANDIDATE"

case "$MARIADB_CANDIDATE" in
  *11.8.9*)
    echo "MARIADB REPOSITORY OK"
    ;;
  *)
    echo "ERROR: expected MariaDB 11.8.9"
    exit 1
    ;;
esac
```

Должно закончиться:

```text
MARIADB REPOSITORY OK
```

Если Candidate `10.11.x` — **MariaDB не устанавливать**.

### 4.3. Установить MariaDB

```bash
sudo apt install -y \
  mariadb-server \
  mariadb-client \
  libmariadb-dev

sudo systemctl enable --now mariadb
```

Проверить:

```bash
systemctl is-active mariadb
mariadb --version
```

Ожидается:

```text
active
... Distrib 11.8.9-MariaDB ...
```

### 4.4. Настроить MariaDB для Frappe

```bash
sudo tee /etc/mysql/mariadb.conf.d/99-frappe.cnf >/dev/null <<'EOF'
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
EOF

sudo systemctl restart mariadb
```

Проверить:

```bash
sudo mariadb -NBe "
SELECT VERSION();
SHOW VARIABLES LIKE 'character_set_server';
SHOW VARIABLES LIKE 'collation_server';
"
```

Должно быть:

```text
11.8.9-MariaDB...
character_set_server    utf8mb4
collation_server        utf8mb4_unicode_ci
```

### 4.5. Создать отдельного администратора БД для Bench

Системный MariaDB `root` оставляем работать штатно через `sudo mariadb`. Для Bench создаём отдельного локального администратора `frappe_admin`.

Открыть MariaDB:

```bash
sudo mariadb
```

Появится:

```text
MariaDB [(none)]>
```

Выполнить по одной строке:

```sql
CREATE USER 'frappe_admin'@'localhost' IDENTIFIED BY 'ВАШ_ОТДЕЛЬНЫЙ_ПАРОЛЬ_MARIADB';
GRANT ALL PRIVILEGES ON *.* TO 'frappe_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

Вместо `ВАШ_ОТДЕЛЬНЫЙ_ПАРОЛЬ_MARIADB` указать свой пароль и сохранить его в менеджере паролей.

Проверить:

```bash
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

После:

```text
Enter password:
```

ввести пароль `frappe_admin`.

Результат должен содержать:

```text
11.8.9-MariaDB
```

`mariadb-secure-installation` в этом сценарии **не используется**.

---

## 5. wkhtmltopdf с patched Qt

Frappe требует wkhtmltopdf 0.12.6 с patched Qt. Используем пакет, который применяется в текущем Frappe CI:

```bash
curl -fL --retry 3 \
  https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb \
  -o /tmp/wkhtmltox_0.12.6.1-2.jammy_amd64.deb

sudo apt install -y /tmp/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
```

Проверить:

```bash
wkhtmltopdf --version
```

Строго ожидается:

```text
wkhtmltopdf 0.12.6.1 (with patched qt)
```

Если `with patched qt` отсутствует — дальше не идти.

---

## 6. GitHub SSH

### 6.1. Автор Git

Подставить свой GitHub email:

```bash
git config --global user.name "lazuale"
git config --global user.email "ВАШ_GITHUB_EMAIL"
git config --global init.defaultBranch main
```

Проверить:

```bash
git config --global user.name
git config --global user.email
git config --global init.defaultBranch
```

### 6.2. SSH-ключ

```bash
ssh-keygen -t ed25519 -C "ВАШ_GITHUB_EMAIL"
```

На:

```text
Enter file in which to save the key (.../.ssh/id_ed25519):
```

нажать `Enter`.

Passphrase можно задать. Для простого локального стенда можно дважды нажать `Enter` и оставить её пустой.

Показать публичный ключ:

```bash
cat ~/.ssh/id_ed25519.pub
```

Скопировать всю строку `ssh-ed25519 ...`.

В GitHub открыть:

```text
Avatar
→ Settings
→ SSH and GPG keys
→ New SSH key
```

Заполнить:

```text
Title:    VEQTA WSL2
Key type: Authentication Key
Key:      строка из ~/.ssh/id_ed25519.pub
```

Нажать `Add SSH key`.

Проверить:

```bash
ssh -T git@github.com
```

При первом подключении ответить:

```text
yes
```

Ожидаемый ответ содержит:

```text
Hi lazuale! You've successfully authenticated
```

---

## 7. Node.js 24.20.0 LTS + npm 11.19.0 + Yarn 1.22.22

### 7.1. NVM 0.40.7

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
```

Проверить:

```bash
nvm --version
```

Строго:

```text
0.40.7
```

### 7.2. Node.js и npm

```bash
nvm install 24.20.0
nvm use 24.20.0
nvm alias default 24.20.0
```

Проверить:

```bash
node --version
npm --version
```

Строго:

```text
v24.20.0
11.19.0
```

**npm отдельно не обновлять.** `npm 11.19.0` входит в Node.js 24.20.0.

### 7.3. Yarn Classic

```bash
npm install -g --allow-scripts=yarn yarn@1.22.22
```

Проверить:

```bash
yarn --version
```

Строго:

```text
1.22.22
```

---

## 8. uv 0.12.7 + Python 3.14.7 + Bench 5.31.0

### 8.1. uv

```bash
curl -LsSf https://astral.sh/uv/0.12.7/install.sh | sh
source ~/.bashrc
```

Проверить:

```bash
uv --version
```

Строго:

```text
uv 0.12.7
```

### 8.2. Python

```bash
uv python install 3.14.7 --default
```

Проверить:

```bash
python --version
python3.14 --version
```

Строго:

```text
Python 3.14.7
Python 3.14.7
```

### 8.3. Frappe Bench

```bash
uv tool install --python 3.14.7 'frappe-bench==5.31.0'
```

Если shell после установки не видит `bench`:

```bash
uv tool update-shell
source ~/.bashrc
```

Проверить:

```bash
bench --version
```

Строго:

```text
5.31.0
```

---

## 9. Контроль runtime перед созданием Bench

```bash
echo "=== OS ==="
. /etc/os-release
echo "$PRETTY_NAME"

echo "=== MARIADB ==="
mariadb --version

echo "=== REDIS ==="
redis-cli ping

echo "=== WKHTMLTOPDF ==="
wkhtmltopdf --version

echo "=== NVM ==="
nvm --version

echo "=== NODE ==="
node --version

echo "=== NPM ==="
npm --version

echo "=== YARN ==="
yarn --version

echo "=== UV ==="
uv --version

echo "=== PYTHON ==="
python --version

echo "=== BENCH ==="
bench --version
```

Контрольный baseline:

```text
Ubuntu                  24.04.x LTS
MariaDB                 11.8.9
Redis                   PONG
wkhtmltopdf             0.12.6.1 (with patched qt)
NVM                     0.40.7
Node.js                 v24.20.0
npm                     11.19.0
Yarn                    1.22.22
uv                      0.12.7
Python                  3.14.7
Bench                   5.31.0
```

Если что-то не совпало — Bench пока не создавать.

---

## 10. Создать Bench с Frappe v16.32.0

```bash
mkdir -p ~/frappe
cd ~/frappe
```

Убедиться, что каталог стенда отсутствует:

```bash
test ! -e ~/frappe/veqta-bench && echo "bench path is clean"
```

Ожидается:

```text
bench path is clean
```

Создать Bench на точном Frappe tag и точном Python:

```bash
bench init \
  --frappe-branch v16.32.0 \
  --python "$(command -v python3.14)" \
  veqta-bench
```

`bench init` создаёт virtual environment, скачивает Frappe, ставит зависимости и собирает assets. Вывод длинный — это нормально. Команда должна завершиться без `ERROR` и `Traceback`.

Проверить:

```bash
cd ~/frappe/veqta-bench
bench version
./env/bin/python --version

cd apps/frappe
git describe --tags --exact-match
git rev-parse HEAD
cd ../..
```

Нужно увидеть:

```text
frappe 16.32.0 ...
Python 3.14.7
v16.32.0
```

Последняя команда `git rev-parse HEAD` выведет точный commit SHA Frappe.

---

## 11. Превратить repository VEQTA в Frappe app

Сейчас repository `lazuale/veqta` содержит проектную документацию. На этом шаге создаём штатный scaffold Frappe app и сохраняем существующую Git history.

### 11.1. Клонировать существующий repository

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

Ожидается чистый `main` и remote `git@github.com:lazuale/veqta.git`.

### 11.2. Создать scaffold

```bash
cd ~/frappe/veqta-bench
bench new-app --no-git veqta
```

Отвечать:

```text
App Title [Veqta]:
VEQTA

App Description:
VEQTA prototype on Frappe Framework

App Publisher:
lazuale

App Email:
ВАШ_GITHUB_EMAIL

App License [mit]:
agpl-3.0

Create GitHub Workflow action for unittests [y/N]:
N

Branch Name [version-16]:
main
```

Проверить scaffold:

```bash
test -f ~/frappe/veqta-bench/apps/veqta/pyproject.toml
test -f ~/frappe/veqta-bench/apps/veqta/veqta/hooks.py
echo "VEQTA scaffold OK"
```

Ожидается:

```text
VEQTA scaffold OK
```

### 11.3. Объединить scaffold с существующей Git history

```bash
rsync -a ~/veqta-existing/ ~/frappe/veqta-bench/apps/veqta/

cd ~/frappe/veqta-bench/apps/veqta
```

Проверить:

```bash
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git status
```

Корень должен быть:

```text
.../frappe/veqta-bench/apps/veqta
```

Remote:

```text
git@github.com:lazuale/veqta.git
```

Branch:

```text
main
```

Проверить, что scaffold сохранился:

```bash
test -f pyproject.toml
test -f veqta/hooks.py
test -f veqta/__init__.py
echo "VEQTA repository + scaffold OK"
```

Ожидается:

```text
VEQTA repository + scaffold OK
```

Удалить временный clone:

```bash
rm -rf ~/veqta-existing
```

Проверить лицензию app:

```bash
grep -n "app_license" veqta/hooks.py
grep -n "license" pyproject.toml
```

Ожидаем `agpl-3.0`. Корневой `LICENSE` проекта не заменять.

---

## 12. Создать site `veqta.localhost`

```bash
cd ~/frappe/veqta-bench

bench new-site veqta.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Bench попросит пароль суперпользователя БД. Несмотря на слово `root` в prompt, ввести **пароль MariaDB пользователя `frappe_admin`**, потому что мы передали `--db-root-username frappe_admin`.

Затем появится:

```text
Set Administrator password:
```

Задать новый отдельный пароль **Frappe Administrator**.

После успешного создания site:

```bash
bench use veqta.localhost
bench --site veqta.localhost install-app veqta
bench --site veqta.localhost list-apps
```

Должны быть как минимум:

```text
frappe
veqta
```

---

## 13. Developer Mode

```bash
cd ~/frappe/veqta-bench

bench set-config -g developer_mode 1
bench --site veqta.localhost clear-cache
```

Проверить:

```bash
grep -n '"developer_mode"' sites/common_site_config.json
```

Должно быть:

```text
"developer_mode": 1
```

Developer Mode нужен, чтобы metadata стандартных объектов приложения, создаваемых через Desk, могли попадать в исходное дерево `apps/veqta` и затем в Git.

---

## 14. Финальная проверка site до запуска

```bash
cd ~/frappe/veqta-bench

echo "=== FRAPPE ==="
bench version

echo "=== SITE APPS ==="
bench --site veqta.localhost list-apps

echo "=== SITE DIRECTORY ==="
test -d sites/veqta.localhost && echo "site directory OK"

echo "=== VEQTA GIT ==="
cd apps/veqta
git remote -v
git branch --show-current
git status
cd ../..
```

Нужно получить:
- Frappe `16.32.0`;
- apps `frappe` и `veqta`;
- `site directory OK`;
- remote `lazuale/veqta`;
- branch `main`;
- новые scaffold-файлы VEQTA видны в `git status` как изменения.

---

## 15. Первый запуск Desk

```bash
cd ~/frappe/veqta-bench
bench start
```

`bench start` остаётся работать в текущем окне и выводит логи процессов.

В Windows открыть:

```text
http://veqta.localhost:8000
```

Войти:

```text
User: Administrator
Password: пароль Frappe Administrator из шага 12
```

Если открылся Desk — стенд поднят.

Остановить dev-сервер:

```text
Ctrl+C
```

---

## 16. Первый commit Frappe scaffold VEQTA

Только после успешного создания site, установки `veqta` и открытия Desk:

```bash
cd ~/frappe/veqta-bench/apps/veqta

git status
git diff
```

Перед commit проверить:
- сохранены `README.md`, `LICENSE`, `.gitignore`, `docs/`;
- появились `pyproject.toml`, пакет `veqta/` и остальные штатные файлы Frappe app;
- нет паролей;
- нет `sites/`, `env/`, `logs/` и всего `veqta-bench`.

Затем:

```bash
git add .
git diff --cached
git commit -m "Bootstrap VEQTA as Frappe app"
git push origin main
```

Проверить:

```bash
git status
```

Ожидается:

```text
nothing to commit, working tree clean
```

---

## 17. VS Code

В Windows установить:
- Visual Studio Code;
- расширение Microsoft **WSL**.

В Ubuntu:

```bash
cd ~/frappe/veqta-bench
code .
```

Рабочие каталоги:

```text
apps/frappe/   # исходники точного Frappe v16.32.0; читаем, но не коммитим в VEQTA
apps/veqta/    # код VEQTA; именно этот Git repository отправляется в lazuale/veqta
```

---

## 18. Контрольная карта готового стенда

В новом терминале Ubuntu:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

echo "=== OS ==="
. /etc/os-release
echo "$PRETTY_NAME"

echo "=== DB ==="
mariadb --version

echo "=== REDIS ==="
redis-cli ping

echo "=== PDF ==="
wkhtmltopdf --version

echo "=== NODE STACK ==="
nvm --version
node --version
npm --version
yarn --version

echo "=== PYTHON STACK ==="
uv --version
python --version
bench --version

echo "=== FRAPPE / VEQTA ==="
cd ~/frappe/veqta-bench
bench version
bench --site veqta.localhost list-apps

echo "=== SERVICES ==="
systemctl is-active mariadb
systemctl is-active redis-server
systemctl is-active cron
```

Эталон:

```text
Ubuntu                  24.04.x LTS
MariaDB                 11.8.9
Redis                   PONG
wkhtmltopdf             0.12.6.1 (with patched qt)
NVM                     0.40.7
Node.js                 v24.20.0
npm                     11.19.0
Yarn                    1.22.22
uv                      0.12.7
Python                  3.14.7
Bench                   5.31.0
Frappe                  16.32.0
Site apps               frappe, veqta
MariaDB service         active
Redis service           active
cron service            active
```

После этого стенд считается готовым.

---

## Что в этом baseline специально не делаем

- не ставим MariaDB из стандартного Ubuntu repository до подключения MariaDB repo;
- не используем MariaDB 10.11;
- не обновляем npm отдельно до 12;
- не используем Node Current 26;
- не используем Python из Ubuntu для Frappe;
- не устанавливаем Python-пакеты глобально через `sudo pip`;
- не используем `develop` вместо фиксированного Frappe tag;
- не меняем системный MariaDB `root` ради Bench;
- не кладём пароли в Git;
- не коммитим весь Bench в repository VEQTA.

Для обновления baseline сначала отдельно проверяются новые версии, затем меняются зафиксированные значения в этой инструкции.