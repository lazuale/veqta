# S00. Подготовить чистую учебную среду Frappe v16

На первом этапе создаётся отдельная локальная среда для практикума. В ней пока нет учебного приложения, собственных `DocType`, ролей и предметной логики — только Frappe Framework и чистый `Site`.

После S00 структура будет выглядеть так:

```text
~/frappe/
└── rental-training-bench/
    ├── apps/
    │   └── frappe/
    └── sites/
        └── rental.localhost/
```

Маршрут всего практикума описан в [`../ROADMAP.md`](../ROADMAP.md), а модель будущего приложения — в [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md).

---

## 1. Контрольные версии

Практикум использует конкретные версии Framework и Bench, чтобы команды и ожидаемое поведение оставались воспроизводимыми на протяжении всего курса.

```text
Frappe Framework : v16.33.0
Bench CLI         : 5.31.0
Python            : 3.14.x
Node.js           : 24.x
Yarn               : 1.22.x
MariaDB            : 11.8.x
Redis              : 6+
```

Frappe v16 требует Python 3.14 и Node 24; официальная страница установки указывает MariaDB 11.8 и Yarn 1.22+. Для практикума выбраны Frappe `v16.33.0` и Bench `5.31.0`.

Первичные источники:

- https://docs.frappe.io/framework/user/en/installation
- https://github.com/frappe/frappe/releases/tag/v16.33.0
- https://github.com/frappe/frappe/blob/v16.33.0/pyproject.toml
- https://github.com/frappe/frappe/blob/v16.33.0/package.json
- https://github.com/frappe/bench/releases/tag/v5.31.0

Исправляющие версии системных пакетов отдельно не замораживаются: они остаются внутри совместимой линии и могут получать обычные исправления безопасности и ошибок.

---

## 2. Операционная система

Основной маршрут практикума:

```text
Windows
└── WSL2
    └── Debian 13
```

Официальная инструкция Frappe поддерживает Debian/Ubuntu; для текущей линии v16 указаны Debian 13+ и Ubuntu 24.04+.

Если подходящий Linux уже установлен, переходите к разделу 4.

---

## 3. Установить Debian 13 в WSL2

Откройте PowerShell от имени администратора:

```powershell
wsl --update
wsl --list --online
wsl --install -d Debian
```

После установки проверьте версию WSL:

```powershell
wsl -l -v
```

Для Debian должно быть:

```text
VERSION 2
```

Если указано `1`:

```powershell
wsl --set-version Debian 2
```

При первом запуске Debian создайте обычного Linux-пользователя.

Проверьте систему:

```bash
. /etc/os-release
printf 'USER=%s\nDEBIAN=%s\nCODENAME=%s\nINIT=%s\n' \
  "$(whoami)" "$VERSION_ID" "$VERSION_CODENAME" "$(ps -p 1 -o comm=)"
```

Для Debian 13 ожидаются:

```text
DEBIAN=13
CODENAME=trixie
INIT=systemd
```

Если PID 1 не `systemd`, сначала исправьте конфигурацию WSL. Дальнейшие команды предполагают работающий systemd.

---

## 4. Установить системные зависимости

Обновите систему:

```bash
sudo apt update
sudo apt full-upgrade -y
```

Установите зависимости, которые используются в этом практикуме:

```bash
sudo apt install -y \
  git \
  curl \
  ca-certificates \
  redis-server \
  libmariadb-dev \
  mariadb-server \
  mariadb-client \
  pkg-config
```

Запустите MariaDB и Redis:

```bash
sudo systemctl enable --now mariadb
sudo systemctl enable --now redis-server
```

Проверьте:

```bash
mariadb --version
redis-cli ping
systemctl is-active mariadb
systemctl is-active redis-server
```

Ожидается MariaDB `11.8.x`, ответ Redis `PONG` и состояние `active` для обоих сервисов.

### Почему здесь нет wkhtmltopdf

В этом практикуме нет задания на PDF и Print Format, поэтому соответствующая зависимость сейчас не используется. Она понадобится только в учебном сценарии, где появится печатный документ.

---

## 5. Подготовить пользователя MariaDB для Bench

При создании `Site` Bench нужен пользователь БД с правами на создание базы и пользователя Site.

Откройте MariaDB:

```bash
sudo mariadb
```

Создайте отдельного локального администратора для учебной среды, заменив `ВАШ_ПАРОЛЬ` своим паролем:

```sql
CREATE USER 'frappe_admin'@'localhost' IDENTIFIED BY 'ВАШ_ПАРОЛЬ';
GRANT ALL PRIVILEGES ON *.* TO 'frappe_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

Проверьте вход:

```bash
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

Пароль этой учётной записи не хранится в Git.

Bench v16 поддерживает `--db-root-username`, поэтому системную модель пользователя `root` MariaDB для практикума менять не требуется.

Источник:

- https://docs.frappe.io/framework/user/en/bench/reference/new-site

---

## 6. Установить Node.js 24 и Yarn Classic

### NVM

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
```

### Node.js

```bash
nvm install 24
nvm use 24
nvm alias default 24
node --version
```

Версия должна начинаться с:

```text
v24.
```

### Yarn

```bash
npm install -g yarn@1.22.22
yarn --version
```

Ожидается:

```text
1.22.22
```

Версии JavaScript-зависимостей самого Frappe отдельно не обновляются: они принадлежат выбранной версии Framework.

---

## 7. Установить uv, Python 3.14 и Bench

### uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version
```

### Python 3.14

```bash
uv python install 3.14 --default
python --version
python3.14 --version
```

Ожидается Python `3.14.x`.

### Bench 5.31.0

```bash
uv tool install 'frappe-bench==5.31.0'
```

Если команда `bench` ещё не появилась в `PATH`:

```bash
uv tool update-shell
source ~/.bashrc
```

Проверьте:

```bash
bench --version
```

Ожидается:

```text
5.31.0
```

Bench устанавливается в пользовательское окружение; `sudo pip install frappe-bench` для этого стенда не используется.

---

## 8. Проверить зависимости

Перед созданием Bench выполните:

```bash
printf 'MARIADB=%s\n' "$(mariadb --version)"
printf 'REDIS=%s\n' "$(redis-cli ping)"
printf 'NODE=%s\n' "$(node --version)"
printf 'YARN=%s\n' "$(yarn --version)"
printf 'PYTHON=%s\n' "$(python --version)"
printf 'BENCH=%s\n' "$(bench --version)"
```

Ожидаемая совместимая среда:

```text
MariaDB 11.8.x
Redis PONG
Node v24.x
Yarn 1.22.22
Python 3.14.x
Bench 5.31.0
```

Если одна из основных версий отличается, сначала исправьте среду. Следующие этапы практикума рассчитаны именно на этот набор.

---

## 9. Создать Bench с Frappe v16.33.0

```bash
mkdir -p ~/frappe
cd ~/frappe

bench init \
  --frappe-branch v16.33.0 \
  --python "$(command -v python3.14)" \
  rental-training-bench
```

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте:

```bash
bench find .
bench --version
bench version --format plain
./env/bin/python --version
node --version
yarn --version
```

Для Framework ожидается `16.33.0`.

Точную Git-точку можно проверить так:

```bash
cd apps/frappe
git describe --tags --exact-match
cd ../..
```

Ожидается:

```text
v16.33.0
```

На этом шаге `Bench` — только рабочая среда с Framework. Учебного приложения и учебного `Site` ещё нет.

---

## 10. Создать чистый Site

Из корня `rental-training-bench` выполните:

```bash
bench new-site rental.localhost \
  --db-root-username frappe_admin \
  --set-default
```

Bench запросит пароль пользователя MariaDB `frappe_admin`, а затем пароль Frappe-пользователя `Administrator`.

Проверьте установленные Apps:

```bash
bench --site rental.localhost list-apps -f text
```

На чистом Site ожидается только:

```text
frappe
```

Источники:

- https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- https://docs.frappe.io/framework/user/en/bench/reference/new-site

---

## 11. Включить developer mode на Site разработки

На следующих этапах создаются Standard DocTypes, принадлежащие учебному App. Их метаданные должны сохраняться в исходниках приложения, поэтому для `rental.localhost` включается developer mode.

```bash
bench --site rental.localhost set-config developer_mode 1
bench --site rental.localhost clear-cache
```

Проверьте:

```bash
bench --site rental.localhost show-config | grep developer_mode
```

Ожидается значение `1` или `true`.

Настройка задаётся для `rental.localhost`, а не глобально для Bench. На S09 появится второй чистый Site, на котором установка приложения будет проверяться без зависимости от developer mode.

---

## 12. Запустить сервер разработки

Из корня Bench:

```bash
bench start
```

Откройте:

```text
http://rental.localhost:8000/app
```

Войдите как `Administrator` с паролем, заданным при `bench new-site`.

---

## 13. Проверить результат S00

Во втором терминале выполните:

```bash
cd ~/frappe/rental-training-bench

printf '\n=== BENCH ===\n'
bench find .
bench --version

printf '\n=== FRAMEWORK ===\n'
bench version --format plain

printf '\n=== SITE APPS ===\n'
bench --site rental.localhost list-apps -f text

printf '\n=== DEVELOPER MODE ===\n'
bench --site rental.localhost show-config | grep developer_mode
```

Перед переходом к S01 проверьте:

```text
[ ] Bench находится в ~/frappe/rental-training-bench
[ ] Bench CLI = 5.31.0
[ ] Frappe Framework = 16.33.0
[ ] Python = 3.14.x
[ ] Node = 24.x
[ ] MariaDB = 11.8.x
[ ] Redis отвечает PONG
[ ] rental.localhost существует
[ ] на Site установлен только frappe
[ ] developer mode включён для rental.localhost
[ ] Desk открывается
[ ] вход Administrator работает
```

После этого среда готова к созданию собственного App.

---

## Что важно понять после S00

```text
Bench
= среда, в которой находятся Apps и Sites

frappe
= Framework как App внутри Bench

Site
= отдельный экземпляр Frappe со своей БД и конфигурацией

rental.localhost
= учебный Site для разработки
```

На S00 предметного приложения ещё нет.

Следующий этап: [`S01_APP_AND_SITE.md`](S01_APP_AND_SITE.md) — создать `rental_training` и установить его на `rental.localhost`.