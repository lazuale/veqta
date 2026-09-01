# P0 — стенд Facility Operations в WSL2

Эта инструкция поднимает самостоятельный учебный стенд Frappe Framework 16 для всего курса.

Итоговая структура:

```text
WSL2 / Debian 13
└── ~/frappe/facility-ops-bench/
    ├── apps/
    │   ├── frappe/            # Frappe Framework v16.32.0
    │   └── facility_ops/      # учебный app всего курса
    └── sites/
        └── facility-ops.localhost/
```

Desk:

```text
http://facility-ops.localhost:8000
```

## 0. Базовые версии

Для воспроизводимости используем проверенный стек курса:

```text
Debian                  13 / Trixie
MariaDB                 11.8.x
NVM                     0.40.3
Node.js                 24.20.0 LTS
Yarn Classic            1.22.22
uv                      0.12.7
Python                  3.14.7
Frappe Bench            5.31.0
Frappe Framework        v16.32.0
```

Системные пакеты Debian до patch-версий не фиксируются и получают обычные обновления безопасности.

PDF-зависимость в P0 не ставится. Она впервые понадобится в P5.

---

# 1. Debian 13 в WSL2

Если Debian 13 уже установлен и работает через WSL2 с `systemd`, этот раздел пропустить.

В PowerShell от имени администратора:

```powershell
wsl --update
wsl --list --online
wsl --install -d Debian
```

Проверить:

```powershell
wsl -l -v
```

Для Debian нужен `VERSION 2`.

Если получился WSL1:

```powershell
wsl --set-version Debian 2
```

После первого запуска Debian создать обычного пользователя.

Проверить:

```bash
cd ~
. /etc/os-release

echo "USER=$(whoami)"
echo "DEBIAN=$VERSION_ID"
echo "CODENAME=$VERSION_CODENAME"
echo "INIT=$(ps -p 1 -o comm=)"
```

Ожидается:

```text
DEBIAN=13
CODENAME=trixie
INIT=systemd
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

Снова открыть Debian и повторить проверку.

---

# 2. Системные зависимости

```bash
sudo apt update
sudo apt full-upgrade -y

sudo apt install -y \
  build-essential \
  git \
  curl \
  ca-certificates \
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

Нужно получить MariaDB `11.8.x`, `PONG` и три состояния `active`.

Если MariaDB не 11.8.x, дальше не идти.

---

# 3. Локальный администратор MariaDB для Bench

Системного MariaDB `root` не перенастраиваем.

Открыть MariaDB:

```bash
sudo mariadb
```

Создать отдельного локального администратора:

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

Пароль не сохранять в Git.

---

# 4. Node.js и Yarn

Установить NVM 0.40.3:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm --version
```

Установить Node.js 24.20.0:

```bash
nvm install 24.20.0
nvm use 24.20.0
nvm alias default 24.20.0
node --version
```

Ожидается:

```text
v24.20.0
```

Установить Yarn Classic:

```bash
npm install -g yarn@1.22.22
yarn --version
```

Ожидается:

```text
1.22.22
```

Отдельно обновлять зависимости самого Frappe вручную не нужно.

---

# 5. uv, Python и Bench

Установить uv 0.12.7:

```bash
curl -LsSf https://astral.sh/uv/0.12.7/install.sh | sh
source ~/.bashrc
uv --version
```

Установить Python 3.14.7:

```bash
uv python install 3.14.7 --default
python3.14 --version
```

Установить Frappe Bench 5.31.0:

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

# 6. Создать Bench

```bash
mkdir -p ~/frappe
cd ~/frappe
```

Каталога `facility-ops-bench` на чистом стенде ещё быть не должно.

Создать Bench на точном tag Frappe:

```bash
bench init \
  --frappe-branch v16.32.0 \
  --python "$(command -v python3.14)" \
  facility-ops-bench
```

После завершения:

```bash
cd ~/frappe/facility-ops-bench
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

# 7. Создать app всего курса

```bash
cd ~/frappe/facility-ops-bench
bench new-app facility_ops
```

Ответы:

```text
App Title [Facility Ops]:
Facility Operations

App Description:
Training application for facility operations on Frappe Framework 16

App Publisher:
Student

App Email:
<ваш действующий email>

App License [mit]:
<Enter>

Create GitHub Workflow action for unittests [y/N]:
N

Branch Name [HEAD]:
main
```

На Bench, созданном непосредственно на tag `v16.32.0`, репозиторий Frappe находится в detached HEAD, поэтому `bench new-app` может предложить `HEAD` как default branch. Ввести `main` явно.

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status
git branch --show-current
cat facility_ops/modules.txt
```

Ожидается:

```text
main
```

и default Module:

```text
Facility Operations
```

Отдельно создавать первый Module не нужно.

---

# 8. Создать учебный site

```bash
cd ~/frappe/facility-ops-bench

bench new-site facility-ops.localhost \
  --db-type mariadb \
  --db-root-username frappe_admin
```

Bench попросит:

1. пароль `frappe_admin`;
2. отдельный пароль пользователя Frappe `Administrator`.

После создания:

```bash
bench use facility-ops.localhost
bench --site facility-ops.localhost install-app facility_ops
bench --site facility-ops.localhost list-apps
```

В списке должны быть:

```text
frappe
facility_ops
```

---

# 9. Включить Developer Mode

```bash
cd ~/frappe/facility-ops-bench
bench set-config -g developer_mode 1
bench --site facility-ops.localhost clear-cache
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

# 10. Первый запуск

```bash
cd ~/frappe/facility-ops-bench
bench start
```

В Windows открыть:

```text
http://facility-ops.localhost:8000
```

Войти:

```text
User: Administrator
Password: пароль из шага 8
```

После проверки остановить Bench можно `Ctrl+C`.

---

# 11. Проверить scheduler и workers

Снова запустить `bench start` в первом терминале.

Во втором терминале:

```bash
cd ~/frappe/facility-ops-bench
bench --site facility-ops.localhost scheduler status
```

Если scheduler сообщает `disabled`:

```bash
bench --site facility-ops.localhost scheduler enable
```

Повторить:

```bash
bench --site facility-ops.localhost scheduler status
bench --site facility-ops.localhost doctor
bench --site facility-ops.localhost show-pending-jobs
```

Пустая очередь на новом стенде нормальна. Важно, чтобы Redis, scheduler и workers были доступны без ошибок соединения.

---

# 12. Финальная проверка стенда

```bash
cd ~/frappe/facility-ops-bench

echo "=== BENCH ==="
bench --version
bench version

echo "=== APPS ==="
bench --site facility-ops.localhost list-apps

echo "=== SCHEDULER ==="
bench --site facility-ops.localhost scheduler status

echo "=== APP GIT ==="
cd apps/facility_ops
git status
git branch --show-current
cat facility_ops/modules.txt
```

P0 можно продолжать, если одновременно:

- Frappe = `16.32.0`;
- site открывается;
- установлены `frappe` и `facility_ops`;
- Developer Mode = `1`;
- scheduler enabled;
- `bench doctor` работает;
- `facility_ops` имеет собственный Git repository;
- branch app = `main`;
- default Module = `Facility Operations`.
