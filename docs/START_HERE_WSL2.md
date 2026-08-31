# VEQTA — чистовая установка dev-стенда на WSL2

Эта инструкция поднимает **локальный стенд разработки VEQTA с нуля на Windows через WSL2 / Ubuntu 24.04**.

Это эталонный сценарий. Команды выполняются **строго сверху вниз**. Если контрольная проверка шага не совпала с ожидаемым результатом — следующий шаг не выполнять.

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

Desk будет доступен из Windows:

```text
http://veqta.localhost:8000
```

## 0. Зафиксированный baseline

```text
WSL distro              Ubuntu 24.04 LTS
MariaDB                 11.8.9
wkhtmltopdf             0.12.6.1-2, patched Qt
NVM                     0.40.6
Node.js                 24.20.0 LTS
npm                     11.19.0
Yarn Classic            1.22.22
uv                      0.12.7
Python                  3.14.7
Frappe Bench            5.31.0
Frappe Framework        v16.32.0
```

Ubuntu system libraries и Redis берём из актуальных security/update repositories Ubuntu 24.04. Их patch-версии отдельно не фиксируем.

Не заменять версии выше на `latest`, `24`, `3.14`, `develop` и другие плавающие значения без отдельного обновления baseline.

Пароли при вводе в Linux обычно **вообще не отображаются** — это нормально.

В процессе появятся три разных секрета:

```text
Linux user password       пароль пользователя Ubuntu
MariaDB frappe_admin      пароль администратора БД для Bench
Frappe Administrator      пароль входа в Desk
```

Их нельзя сохранять в Git, README, Issue или исходном коде.

---

## 1. WSL2 / Ubuntu 24.04

### 1.1. Установка

Открыть **PowerShell от имени администратора**:

```powershell
wsl --update
wsl --install -d Ubuntu-24.04
```

После установки открыть `Ubuntu 24.04` из меню Пуск.

При первом запуске создать Linux-пользователя. Имя может быть любым, например:

```text
Enter new UNIX username: dev
New password:             придумать пароль Linux-пользователя
Retype new password:      повторить пароль
```

### 1.2. Если нужно полностью начать заново

**Внимание: следующая команда полностью удаляет выбранный WSL-дистрибутив со всеми его файлами.**

Сначала посмотреть точное имя:

```powershell
wsl -l -v
```

Если дистрибутив называется `Ubuntu-24.04` и его действительно нужно уничтожить:

```powershell
wsl --terminate Ubuntu-24.04
wsl --unregister Ubuntu-24.04
wsl --install -d Ubuntu-24.04
```

После этого снова открыть Ubuntu и создать Linux-пользователя.

### 1.3. Контроль Ubuntu, systemd и рабочего каталога

Уже **в Ubuntu**, не в PowerShell:

```bash
cd ~
. /etc/os-release

echo "USER=$(whoami)"
echo "UBUNTU=$VERSION_ID"
echo "INIT=$(ps -p 1 -o comm=)"
echo "HOME=$HOME"
echo "PWD=$PWD"
```

Для пользователя `dev` контрольный вывод должен быть таким:

```text
USER=dev
UBUNTU=24.04
INIT=systemd
HOME=/home/dev
PWD=/home/dev
```

Имя пользователя может быть другим. Важно:

```text
UBUNTU=24.04
INIT=systemd
PWD совпадает с HOME
```

`cd ~` обязателен. Если WSL был открыт из PowerShell в `C:\Windows\System32`, без него стартовый каталог может оказаться `/mnt/c/WINDOWS/System32`.

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

Снова открыть Ubuntu и повторить контроль пункта 1.3.

---

## 2. Проверка сети и DNS

Проверка выполняется **в отдельном subshell**. Если что-то недоступно, проверка завершится ошибкой, но сам Ubuntu-shell не закроется.

```bash
cd ~

(
  set -e

  for host in \
    github.com \
    raw.githubusercontent.com \
    mariadb.org \
    deb.mariadb.org \
    nodejs.org \
    astral.sh
  do
    getent ahosts "$host" >/dev/null
    echo "OK  $host"
  done

  curl -fsSL https://mariadb.org/mariadb_release_signing_key.pgp -o /dev/null
  curl -fsSL https://deb.mariadb.org/11.8/ubuntu/dists/noble/InRelease -o /dev/null

  echo "NETWORK OK"
)
```

Должно закончиться:

```text
OK  github.com
OK  raw.githubusercontent.com
OK  mariadb.org
OK  deb.mariadb.org
OK  nodejs.org
OK  astral.sh
NETWORK OK
```

Если какой-то хост не резолвится или `curl` возвращает ошибку — следующий шаг не выполнять.

**`dlm.mariadb.com` в этом сценарии не используется.** Репозиторий MariaDB подключается напрямую через официальный MariaDB Foundation APT endpoint.

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

Если `sudo` спросит пароль — ввести пароль Linux-пользователя.

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

Frappe v16 использует MariaDB 11.8. Стандартный repository Ubuntu 24.04 содержит MariaDB 10.11, поэтому сначала подключаем официальный MariaDB Foundation repository и **до установки проверяем Candidate**.

### 4.1. Добавить ключ MariaDB

```bash
sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL \
  https://mariadb.org/mariadb_release_signing_key.pgp \
  -o /etc/apt/keyrings/mariadb-keyring.asc
```

Проверить:

```bash
test -s /etc/apt/keyrings/mariadb-keyring.asc && echo "MARIADB KEY OK"
```

Ожидается:

```text
MARIADB KEY OK
```

### 4.2. Добавить repository MariaDB 11.8 для Ubuntu Noble

```bash
sudo tee /etc/apt/sources.list.d/mariadb.sources >/dev/null <<'EOF'
X-Repolib-Name: MariaDB
Types: deb
URIs: https://deb.mariadb.org/11.8/ubuntu
Suites: noble
Components: main
Signed-By: /etc/apt/keyrings/mariadb-keyring.asc
EOF

sudo apt update
```

Показать политику пакета:

```bash
apt-cache policy mariadb-server
```

Затем выполнить контроль, который **не закрывает shell**:

```bash
MARIADB_CANDIDATE="$(apt-cache policy mariadb-server | awk '/Candidate:/ {print $2}')"

echo "MARIADB_CANDIDATE=$MARIADB_CANDIDATE"

if [[ "$MARIADB_CANDIDATE" == *11.8.9* ]]; then
  echo "MARIADB REPOSITORY OK"
else
  echo "ERROR: expected MariaDB 11.8.9; DO NOT CONTINUE"
fi
```

На текущем baseline нужно получить примерно:

```text
MARIADB_CANDIDATE=1:11.8.9+maria~ubu2404
MARIADB REPOSITORY OK
```

Если Candidate содержит `10.11` или другую версию — **MariaDB не устанавливать**.

### 4.3. Установить MariaDB

Только после `MARIADB REPOSITORY OK`:

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

### 4.4. Настроить charset для Frappe

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

Ожидается:

```text
11.8.9-MariaDB...
character_set_server    utf8mb4
collation_server        utf8mb4_unicode_ci
```

### 4.5. Создать администратора БД для Bench

Системный MariaDB `root` не меняем. Для Bench создаём отдельного локального администратора `frappe_admin`.

```bash
sudo mariadb
```

Появится:

```text
MariaDB [(none)]>
```

Выполнить, заменив пароль на свой:

```sql
CREATE USER 'frappe_admin'@'localhost' IDENTIFIED BY 'ВАШ_ПАРОЛЬ_MARIADB';
GRANT ALL PRIVILEGES ON *.* TO 'frappe_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

Сохранить пароль `frappe_admin` в менеджере паролей.

Проверить:

```bash
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

Ввести пароль `frappe_admin`.

Результат должен содержать:

```text
11.8.9-MariaDB
```

`mariadb-secure-installation` в этом dev-сценарии не используется.

---

## 5. wkhtmltopdf с patched Qt

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

Ожидается:

```text
wkhtmltopdf 0.12.6.1 (with patched qt)
```

Если `with patched qt` отсутствует — следующий шаг не выполнять.

---

## 6. GitHub SSH

### 6.1. Настроить автора Git

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

### 6.2. Создать SSH-ключ

```bash
ssh-keygen -t ed25519 -C "ВАШ_GITHUB_EMAIL"
```

На вопрос о пути:

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

В GitHub:

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

### 7.1. NVM 0.40.6

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.6/install.sh | bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
```

Проверить:

```bash
nvm --version
```

Строго:

```text
0.40.6
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

**npm отдельно не обновлять.**

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

Если `bench` не найден:

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

## 9. Полный контроль runtime до Bench

```bash
cd ~
. /etc/os-release

printf 'UBUNTU=%s\n' "$VERSION_ID"
printf 'MARIADB='
mariadb --version
printf 'REDIS='
redis-cli ping
printf 'WKHTMLTOPDF='
wkhtmltopdf --version
printf 'NVM='
nvm --version
printf 'NODE='
node --version
printf 'NPM='
npm --version
printf 'YARN='
yarn --version
printf 'UV='
uv --version
printf 'PYTHON='
python --version
printf 'BENCH='
bench --version
```

Baseline:

```text
Ubuntu                  24.04
MariaDB                 11.8.9
Redis                   PONG
wkhtmltopdf             0.12.6.1 (with patched qt)
NVM                     0.40.6
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

Проверить, что каталога ещё нет:

```bash
if [ -e ~/frappe/veqta-bench ]; then
  echo "ERROR: ~/frappe/veqta-bench already exists"
else
  echo "BENCH PATH OK"
fi
```

Нужно увидеть:

```text
BENCH PATH OK
```

Создать Bench:

```bash
bench init \
  --frappe-branch v16.32.0 \
  --python "$(command -v python3.14)" \
  veqta-bench
```

Вывод будет длинным. Команда должна завершиться без `ERROR` и `Traceback`.

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

Нужно увидеть Frappe `16.32.0`, Python `3.14.7` и tag `v16.32.0`.

---

## 11. Превратить repository VEQTA в Frappe app

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

Нужен чистый `main` и remote `git@github.com:lazuale/veqta.git`.

### 11.2. Создать штатный scaffold Frappe app

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

Проверить:

```bash
test -f ~/frappe/veqta-bench/apps/veqta/pyproject.toml && \
test -f ~/frappe/veqta-bench/apps/veqta/veqta/hooks.py && \
echo "VEQTA SCAFFOLD OK"
```

Нужно увидеть:

```text
VEQTA SCAFFOLD OK
```

### 11.3. Совместить scaffold с существующей Git history

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

test -f pyproject.toml && \
test -f veqta/hooks.py && \
test -f veqta/__init__.py && \
echo "VEQTA REPOSITORY + SCAFFOLD OK"
```

Remote должен быть `git@github.com:lazuale/veqta.git`, branch — `main`.

Удалить временный clone:

```bash
rm -rf ~/veqta-existing
```

Проверить лицензию app:

```bash
grep -n "app_license" veqta/hooks.py
grep -n "license" pyproject.toml
```

Ожидается `agpl-3.0`. Корневой `LICENSE` проекта не заменять.

---

## 12. Создать site `veqta.localhost`

```bash
cd ~/frappe/veqta-bench

bench new-site veqta.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Bench попросит пароль суперпользователя БД. Ввести **пароль MariaDB пользователя `frappe_admin` из шага 4.5**.

Затем:

```text
Set Administrator password:
```

Задать отдельный пароль пользователя Frappe `Administrator`.

После успешного создания site:

```bash
bench use veqta.localhost
bench --site veqta.localhost install-app veqta
bench --site veqta.localhost list-apps
```

Должно быть как минимум:

```text
frappe
veqta
```

---

## 13. Developer Mode

```bash
cd ~/frappe/veqta-bench

bench set-config -g -p developer_mode 1
bench --site veqta.localhost clear-cache
```

Проверить:

```bash
grep -n '"developer_mode"' sites/common_site_config.json
```

Ожидается значение `1`.

---

## 14. Финальная проверка site до запуска

```bash
cd ~/frappe/veqta-bench

echo "=== FRAPPE ==="
bench version

echo "=== SITE APPS ==="
bench --site veqta.localhost list-apps

echo "=== SITE DIRECTORY ==="
test -d sites/veqta.localhost && echo "SITE DIRECTORY OK"

echo "=== VEQTA GIT ==="
cd apps/veqta
git remote -v
git branch --show-current
git status
cd ../..
```

Нужно получить:

```text
Frappe        16.32.0
Site apps     frappe + veqta
Site dir      OK
VEQTA remote  lazuale/veqta
Branch        main
```

---

## 15. Первый запуск Desk

```bash
cd ~/frappe/veqta-bench
bench start
```

`bench start` остаётся работать в текущем терминале и выводит логи.

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

Только после успешного запуска Desk:

```bash
cd ~/frappe/veqta-bench/apps/veqta

git status
git diff
```

Перед commit проверить:

- сохранены `README.md`, `LICENSE`, `.gitignore`, `docs/`;
- появились `pyproject.toml`, пакет `veqta/` и штатные файлы Frappe app;
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
apps/frappe/   # Frappe v16.32.0; читаем, но не коммитим в VEQTA
apps/veqta/    # код VEQTA; этот repository отправляется в lazuale/veqta
```

---

## 18. Контрольная карта готового стенда

В новом терминале Ubuntu:

```bash
cd ~
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

. /etc/os-release
echo "UBUNTU=$VERSION_ID"

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
Ubuntu                  24.04
MariaDB                 11.8.9
Redis                   PONG
wkhtmltopdf             0.12.6.1 (with patched qt)
NVM                     0.40.6
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

- не используем `dlm.mariadb.com`;
- не ставим MariaDB из стандартного Ubuntu repository до подключения MariaDB Foundation repo;
- не используем MariaDB 10.11;
- не запускаем `set -e` в основном интерактивном shell;
- не используем `exit` в контрольных блоках, способный закрыть WSL-shell;
- не обновляем npm отдельно до 12;
- не используем Node Current 26;
- не используем Python из Ubuntu для Frappe;
- не устанавливаем Python-пакеты глобально через `sudo pip`;
- не используем `develop` вместо фиксированного Frappe tag;
- не меняем системный MariaDB `root` ради Bench;
- не кладём пароли в Git;
- не коммитим весь Bench в repository VEQTA.

Для обновления baseline сначала проверяются новые версии и совместимость, затем меняются зафиксированные значения в этой инструкции.
