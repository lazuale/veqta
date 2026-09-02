# Учебный Frappe Bench в WSL2

Инструкция поднимает общий стенд трёх практикумов:

```text
Windows
└── WSL2 / Debian 13
    └── ~/frappe/frappe-practicum-bench/
        ├── env/
        ├── apps/
        │   └── frappe/
        └── sites/
```

На этом шаге не создаётся business app. `equipment_register`, `purchase_requests` и `service_intake` будут созданы внутри своих проектов.

## 1. Зафиксированные версии

```text
Debian                  13 / Trixie
MariaDB                 11.8.x из Debian 13
NVM                     0.40.3
Node.js                 24.20.0 LTS
npm                     12.0.2
Yarn Classic            1.22.22
uv                      0.12.7
Python                  3.14.7
Frappe Bench            5.31.0
Frappe Framework        v16.32.0
```

Python и Node соответствуют exact tag Frappe. Системные Debian packages получают обычные security updates и не фиксируются до patch-версии.

## 2. Установить Debian в WSL2

Открыть PowerShell от имени администратора:

```powershell
wsl --update
wsl --list --online
wsl --install -d Debian
wsl -l -v
```

Для `Debian` нужен `VERSION 2`. Если установлен WSL1:

```powershell
wsl --set-version Debian 2
wsl --set-default Debian
```

При первом запуске Debian создать обычного Linux user, например `dev`.

Проверить в Debian:

```bash
cd ~
. /etc/os-release

echo "USER=$(whoami)"
echo "DEBIAN=$VERSION_ID"
echo "CODENAME=$VERSION_CODENAME"
echo "INIT=$(ps -p 1 -o comm=)"
echo "PWD=$PWD"
```

Ожидается Debian 13, codename `trixie`, PID 1 `systemd`, а текущий каталог совпадает с домашним.

Если systemd не включён:

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Затем выполнить в PowerShell:

```powershell
wsl --shutdown
```

Снова открыть Debian и повторить проверку.

## 3. Установить системные зависимости

```bash
cd ~
sudo apt update
sudo apt full-upgrade -y

sudo apt install -y \
  build-essential \
  git \
  openssh-client \
  curl \
  ca-certificates \
  rsync \
  ripgrep \
  pkg-config \
  redis-server \
  mariadb-server \
  mariadb-client \
  libmariadb-dev \
  cron
```

Запустить сервисы:

```bash
sudo systemctl enable --now mariadb
sudo systemctl enable --now redis-server
sudo systemctl enable --now cron
```

Проверить:

```bash
mariadb --version
redis-cli ping
systemctl is-active mariadb
systemctl is-active redis-server
systemctl is-active cron
```

MariaDB должна быть `11.8.x`, Redis отвечает `PONG`, сервисы — `active`. Сторонний MariaDB repository не добавляется.

## 4. Создать локального администратора БД для Bench

Системный MariaDB root не перенастраивать. Открыть штатную консоль:

```bash
sudo mariadb
```

Выполнить, заменив пароль своим:

```sql
CREATE USER 'frappe_admin'@'localhost' IDENTIFIED BY 'ВАШ_ПАРОЛЬ_MARIADB';
GRANT ALL PRIVILEGES ON *.* TO 'frappe_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

Проверить:

```bash
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

Пароль вводится интерактивно и не сохраняется в Git. В этой схеме `mariadb-secure-installation` не нужен: системный root остаётся локальным, Bench работает через отдельного локального администратора.

## 5. Установить Node.js, npm и Yarn

NVM:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm --version
```

Node.js:

```bash
nvm install 24.20.0
nvm use 24.20.0
nvm alias default 24.20.0
node --version
```

npm и Yarn Classic:

```bash
npm install -g npm@12.0.2
npm install -g yarn@1.22.22

npm --version
yarn --version
```

Ожидается:

```text
NVM   0.40.3
Node  v24.20.0
npm   12.0.2
Yarn  1.22.22
```

## 6. Установить uv, Python и Bench

```bash
curl -LsSf https://astral.sh/uv/0.12.7/install.sh | sh
source ~/.bashrc
uv --version

uv python install 3.14.7 --default
python --version
python3.14 --version

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

## 7. Настроить автора Git

```bash
git config --global user.name "ВАШЕ_ИМЯ"
git config --global user.email "ВАШ_EMAIL"
git config --global init.defaultBranch main
```

Проверить:

```bash
git config --global user.name
git config --global user.email
git config --global init.defaultBranch
```

SSH remote для учебных app настраивается перед первым push. Сам Bench в Git не помещается.

## 8. Создать общий Bench

```bash
mkdir -p ~/frappe
cd ~/frappe

bench init \
  --frappe-branch v16.32.0 \
  --python "$(command -v python3.14)" \
  frappe-practicum-bench
```

После завершения:

```bash
cd ~/frappe/frappe-practicum-bench
bench version
./env/bin/python --version

cd apps/frappe
git describe --tags --exact-match
git rev-parse HEAD
cd ../..
```

Нужно увидеть Frappe `16.32.0`, Python `3.14.7` и tag `v16.32.0`.

## 9. Smoke test платформы

Создать Frappe-only site:

```bash
cd ~/frappe/frappe-practicum-bench
bench new-site platform-check.localhost --db-root-username frappe_admin
bench use platform-check.localhost
bench --site platform-check.localhost list-apps
```

Bench запросит пароль `frappe_admin`, затем пароль Frappe Administrator. В `list-apps` пока должен быть только `frappe`.

Запустить development process:

```bash
bench start
```

Открыть в Windows:

```text
http://platform-check.localhost:8000
```

Войти как `Administrator`. После проверки остановить `bench start` сочетанием `Ctrl+C`.

## 10. PDF для проекта 2

До проекта 2 Chromium не нужен. Перед проверкой PDF выполнить из bench:

```bash
bench setup-chrome
```

Команда использует штатный генератор PDF через Chromium в Frappe v16. Если она
завершилась ошибкой, Print View можно проверить отдельно, но проверка PDF не пройдена.

## 11. Финальная проверка стенда

```bash
cd ~/frappe/frappe-practicum-bench
. /etc/os-release

echo "DEBIAN=$VERSION_ID/$VERSION_CODENAME"
mariadb --version
redis-cli ping
nvm --version
node --version
npm --version
yarn --version
uv --version
python --version
bench --version
bench version
bench --site platform-check.localhost list-apps
```

Стенд принят, если:

- Debian 13 / Trixie и systemd работают;
- MariaDB 11.8.x и Redis active;
- Node 24, Python 3.14 и Bench соответствуют baseline;
- Frappe установлен из exact tag `v16.32.0`;
- Desk открывается;
- в Bench ещё нет business app практикума;
- каталог `sites/` и весь Bench не добавлены в какой-либо app repository.

Дальше: [проект 1 — «Реестр оборудования»](projects/01-equipment-register/README.md).
