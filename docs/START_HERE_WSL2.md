# VEQTA — чистовая установка dev-стенда на WSL2

Эта инструкция поднимает **локальный dev-стенд VEQTA с нуля на Windows через WSL2 / Debian 13**.

Цель — получить рабочий Frappe Desk без сторонних репозиториев MariaDB, самодельных install-скриптов и лишней настройки системы.

После завершения:

```text
Windows
└── WSL2 / Debian 13
    └── ~/frappe/veqta-bench/
        ├── env/
        ├── apps/
        │   ├── frappe/        # Frappe Framework v16.32.0
        │   └── veqta/         # repository lazuale/veqta + Frappe app
        └── sites/
            └── veqta.localhost/
```

Desk:

```text
http://veqta.localhost:8000
```

## 0. Принцип установки

Для этого стенда используем **Debian 13 (Trixie)**.

Почему Debian, а не Ubuntu 24.04:

- Frappe v16 официально поддерживает Debian 13+;
- Frappe v16 требует MariaDB 11.8;
- Debian 13 поставляет MariaDB 11.8 штатно через обычный `apt`;
- поэтому не нужен отдельный repository MariaDB и не возникает конфликт с MariaDB 10.11 из Ubuntu 24.04.

Системные пакеты Debian не фиксируем до patch-версии: они должны получать штатные security updates Debian 13.

Фиксируем только runtime и код, от которых зависит воспроизводимость разработки:

```text
Debian                  13 / Trixie
MariaDB                 11.8.x из Debian 13
NVM                     0.40.3
Node.js                 24.20.0
npm                     11.19.0 (идёт вместе с Node 24.20.0)
Yarn Classic            1.22.22
uv                      0.12.7
Python                  3.14.7
Frappe Bench            5.31.0
Frappe Framework        v16.32.0
```

`wkhtmltopdf` не входит в основной сценарий: он нужен для PDF-печати, но не для запуска Desk. Его добавляем отдельно, когда понадобится PDF.

---

# 1. Установить Debian в WSL2

## 1.1. PowerShell

Открыть **PowerShell от имени администратора**.

Обновить WSL и посмотреть доступные дистрибутивы:

```powershell
wsl --update
wsl --list --online
```

В списке должен быть:

```text
Debian    Debian GNU/Linux
```

Установить Debian:

```powershell
wsl --install -d Debian
```

Проверить:

```powershell
wsl -l -v
```

Для `Debian` должно быть:

```text
VERSION 2
```

Если Debian почему-то создан как WSL1:

```powershell
wsl --set-version Debian 2
```

Сделать Debian дистрибутивом по умолчанию:

```powershell
wsl --set-default Debian
```

Старый Ubuntu пока **не удалять**. Удалить его можно после того, как новый стенд полностью заработает.

## 1.2. Первый запуск Debian

Открыть `Debian` из меню Пуск.

При первом запуске создать обычного Linux-пользователя. Например:

```text
Enter new UNIX username: dev
New password:             придумать пароль
Retype new password:      повторить пароль
```

Имя пользователя может быть любым. Дальше инструкция не зависит от имени `dev`.

## 1.3. Проверить систему

В Debian:

```bash
cd ~
. /etc/os-release

echo "USER=$(whoami)"
echo "DEBIAN=$VERSION_ID"
echo "CODENAME=$VERSION_CODENAME"
echo "INIT=$(ps -p 1 -o comm=)"
echo "HOME=$HOME"
echo "PWD=$PWD"
```

Ожидается по смыслу:

```text
USER=dev
DEBIAN=13
CODENAME=trixie
INIT=systemd
HOME=/home/dev
PWD=/home/dev
```

Критично:

```text
DEBIAN=13
CODENAME=trixie
INIT=systemd
PWD совпадает с HOME
```

Если `INIT` не `systemd`, выполнить:

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

Снова открыть Debian и повторить проверку пункта 1.3.

---

# 2. Обновить Debian и поставить системные зависимости

В Debian:

```bash
cd ~
sudo apt update
sudo apt full-upgrade -y
```

Установить системные зависимости стенда:

```bash
sudo apt install -y \
  build-essential \
  git \
  openssh-client \
  curl \
  ca-certificates \
  rsync \
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
echo "=== MARIADB ==="
mariadb --version

echo "=== REDIS ==="
redis-cli ping

echo "=== SERVICES ==="
systemctl is-active mariadb
systemctl is-active redis-server
systemctl is-active cron
```

Нормальный результат:

```text
MariaDB ... 11.8.x ...
PONG
active
active
active
```

Если MariaDB не `11.8.x`, дальше не идти.

Никакой сторонний MariaDB repository в этой инструкции не используется.

---

# 3. Создать администратора MariaDB для Bench

Системного MariaDB-пользователя `root` не перенастраиваем. Он остаётся штатным системным администратором MariaDB.

Для Bench создаём отдельного локального администратора `frappe_admin`.

Открыть MariaDB от системного root:

```bash
sudo mariadb
```

Появится приглашение:

```text
MariaDB [(none)]>
```

Выполнить:

```sql
CREATE USER 'frappe_admin'@'localhost' IDENTIFIED BY 'ВАШ_ПАРОЛЬ_MARIADB';
GRANT ALL PRIVILEGES ON *.* TO 'frappe_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

`ВАШ_ПАРОЛЬ_MARIADB` заменить на отдельный пароль и сохранить в менеджере паролей.

Проверить вход:

```bash
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

На:

```text
Enter password:
```

ввести пароль `frappe_admin`.

Версия должна начинаться с `11.8`.

`mariadb-secure-installation` для этого локального dev-стенда не требуется: системный `root` не меняем, а Bench работает через отдельного локального администратора.

---

# 4. Git и GitHub SSH

## 4.1. Настроить автора Git

Подставить email GitHub:

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

## 4.2. Создать SSH-ключ

```bash
ssh-keygen -t ed25519 -C "ВАШ_GITHUB_EMAIL"
```

На вопрос о пути:

```text
Enter file in which to save the key (.../.ssh/id_ed25519):
```

нажать `Enter`.

Passphrase можно задать или оставить пустой для локального dev-стенда.

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

Проверить:

```bash
ssh -T git@github.com
```

При первом подключении подтвердить fingerprint словом:

```text
yes
```

Ожидаемый ответ содержит:

```text
Hi lazuale! You've successfully authenticated
```

---

# 5. Node.js, npm и Yarn

## 5.1. NVM 0.40.3

Установить NVM тем же способом, который рекомендует документация Frappe:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
```

Проверить:

```bash
nvm --version
```

Ожидается:

```text
0.40.3
```

## 5.2. Node.js 24.20.0

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

Ожидается:

```text
v24.20.0
11.19.0
```

`npm` отдельно не обновлять.

## 5.3. Yarn 1.22.22

```bash
npm install -g --allow-scripts=yarn yarn@1.22.22
```

Проверить:

```bash
yarn --version
```

Ожидается:

```text
1.22.22
```

---

# 6. uv, Python и Bench

## 6.1. uv 0.12.7

```bash
curl -LsSf https://astral.sh/uv/0.12.7/install.sh | sh
source ~/.bashrc
```

Проверить:

```bash
uv --version
```

Ожидается:

```text
uv 0.12.7
```

## 6.2. Python 3.14.7

```bash
uv python install 3.14.7 --default
```

Проверить:

```bash
python --version
python3.14 --version
```

Ожидается:

```text
Python 3.14.7
Python 3.14.7
```

## 6.3. Frappe Bench 5.31.0

```bash
uv tool install --python 3.14.7 'frappe-bench==5.31.0'
```

Если `bench` сразу не найден:

```bash
uv tool update-shell
source ~/.bashrc
```

Проверить:

```bash
bench --version
```

Ожидается:

```text
5.31.0
```

---

# 7. Контроль окружения

Перед созданием Bench выполнить:

```bash
cd ~
. /etc/os-release

echo "DEBIAN=$VERSION_ID/$VERSION_CODENAME"
echo "MARIADB=$(mariadb --version)"
echo "REDIS=$(redis-cli ping)"
echo "NVM=$(nvm --version)"
echo "NODE=$(node --version)"
echo "NPM=$(npm --version)"
echo "YARN=$(yarn --version)"
echo "UV=$(uv --version)"
echo "PYTHON=$(python --version)"
echo "BENCH=$(bench --version)"
```

Контроль:

```text
DEBIAN=13/trixie
MARIADB=... 11.8.x ...
REDIS=PONG
NVM=0.40.3
NODE=v24.20.0
NPM=11.19.0
YARN=1.22.22
UV=uv 0.12.7
PYTHON=Python 3.14.7
BENCH=5.31.0
```

Если всё совпадает — переходить дальше.

---

# 8. Создать Bench с Frappe v16.32.0

```bash
mkdir -p ~/frappe
cd ~/frappe
```

Убедиться, что каталог ещё не существует:

```bash
ls -la
```

`veqta-bench` на чистой установке здесь быть не должно.

Создать Bench:

```bash
bench init \
  --frappe-branch v16.32.0 \
  --python "$(command -v python3.14)" \
  veqta-bench
```

Команда скачает Frappe, создаст Python environment, установит зависимости и соберёт assets. Вывод будет длинным.

После завершения:

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

---

# 9. Превратить repository VEQTA в Frappe app

Это единственный проектный bootstrap-шаг: repository `lazuale/veqta` уже существует и содержит документацию, поэтому нужно добавить в него штатный scaffold Frappe app, сохранив Git history.

## 9.1. Клонировать существующий repository

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

Должны быть branch `main`, чистый working tree и remote `git@github.com:lazuale/veqta.git`.

## 9.2. Создать штатный scaffold Frappe

```bash
cd ~/frappe/veqta-bench
bench new-app --no-git veqta
```

Ответы:

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
test -f ~/frappe/veqta-bench/apps/veqta/pyproject.toml && echo OK
test -f ~/frappe/veqta-bench/apps/veqta/veqta/hooks.py && echo OK
```

Должно быть два `OK`.

## 9.3. Добавить существующую Git history

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

Корень Git должен быть:

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

Scaffold должен существовать:

```bash
test -f pyproject.toml && echo "pyproject OK"
test -f veqta/hooks.py && echo "hooks OK"
test -f veqta/__init__.py && echo "package OK"
```

Удалить временную копию:

```bash
rm -rf ~/veqta-existing
```

---

# 10. Создать site

Перейти в Bench:

```bash
cd ~/frappe/veqta-bench
```

Создать site:

```bash
bench new-site veqta.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Bench спросит пароль администратора MariaDB. Ввести пароль пользователя `frappe_admin` из шага 3.

Затем:

```text
Set Administrator password:
```

задать **другой** пароль — это пароль пользователя `Administrator` в Frappe Desk.

После создания site:

```bash
bench use veqta.localhost
bench --site veqta.localhost install-app veqta
bench --site veqta.localhost list-apps
```

Должны присутствовать:

```text
frappe
veqta
```

---

# 11. Включить Developer Mode

```bash
cd ~/frappe/veqta-bench
bench set-config -g developer_mode 1
bench --site veqta.localhost clear-cache
```

Проверить:

```bash
grep '"developer_mode"' sites/common_site_config.json
```

Ожидается:

```text
"developer_mode": 1
```

---

# 12. Первый запуск Desk

```bash
cd ~/frappe/veqta-bench
bench start
```

Команда остаётся работать и выводит логи — это нормально.

В Windows открыть:

```text
http://veqta.localhost:8000
```

Войти:

```text
User: Administrator
Password: пароль Frappe Administrator из шага 10
```

Если Desk открылся — основной dev-стенд готов.

Остановить Bench:

```text
Ctrl+C
```

---

# 13. Зафиксировать Frappe scaffold VEQTA в Git

После успешного запуска Desk:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

Проверить, что:

- существующие `README.md`, `LICENSE`, `.gitignore`, `docs/` сохранены;
- появились штатные файлы Frappe app: `pyproject.toml`, пакет `veqta/` и т. п.;
- паролей в изменениях нет;
- в repository не попали `env/`, `sites/`, `logs/` или весь `veqta-bench`.

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

# 14. VS Code

В Windows установить:

- Visual Studio Code;
- расширение Microsoft **WSL**.

В Debian:

```bash
cd ~/frappe/veqta-bench
code .
```

Рабочие каталоги:

```text
apps/frappe/   # точный Frappe v16.32.0; читаем как Framework
apps/veqta/    # код VEQTA; именно этот repository коммитим
```

---

# 15. Финальная проверка стенда

В новом терминале Debian:

```bash
cd ~
source ~/.bashrc
. /etc/os-release

echo "=== SYSTEM ==="
echo "$PRETTY_NAME"

echo "=== SERVICES ==="
systemctl is-active mariadb
systemctl is-active redis-server
systemctl is-active cron

echo "=== DATABASE ==="
mariadb --version

echo "=== NODE ==="
nvm --version
node --version
npm --version
yarn --version

echo "=== PYTHON ==="
uv --version
python --version
bench --version

echo "=== FRAPPE ==="
cd ~/frappe/veqta-bench
bench version
bench --site veqta.localhost list-apps
```

Стенд готов, если:

```text
Debian                  13 / Trixie
MariaDB                 11.8.x
MariaDB service         active
Redis                   active / PONG
cron                    active
NVM                     0.40.3
Node.js                 v24.20.0
npm                     11.19.0
Yarn                    1.22.22
uv                      0.12.7
Python                  3.14.7
Bench                   5.31.0
Frappe                  16.32.0
Site apps               frappe, veqta
Desk                    открывается на veqta.localhost:8000
```

---

# Что намеренно не входит в основной сценарий

- Ubuntu 24.04 — для нового стенда используем Debian 13, чтобы MariaDB 11.8 ставилась штатно;
- сторонние MariaDB repositories;
- `mariadb_repo_setup`;
- ручная настройка `character-set-server` и `collation-server` — Frappe создаёт свою БД с `utf8mb4` и `utf8mb4_unicode_ci`;
- отдельное обновление npm;
- Node Current;
- Python из системного Debian для Frappe;
- `sudo pip`;
- Frappe `develop`;
- Docker внутри WSL;
- production nginx/supervisor/systemd-конфигурация — это отдельный production-сценарий;
- wkhtmltopdf — добавляется отдельно, когда потребуется PDF-печать.
