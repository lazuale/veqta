# S00. Подготовить чистую учебную среду Frappe v16

Этот этап поднимает **отдельный локальный dev-стенд для практикума**.

На нём пока нет учебного App, DocType, ролей и предметной логики. Результат S00 — только работающий Frappe Framework и чистый Site.

Связанные документы:

- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md) — что в итоге строится в CORE;
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md) — место этого этапа в общем маршруте.

---

## 1. Что должно получиться

После S00 структура выглядит так:

```text
~/frappe/
└── rental-training-bench/
    ├── apps/
    │   └── frappe/
    └── sites/
        └── rental.localhost/
```

На `rental.localhost` установлен только Framework:

```text
frappe
```

Учебного `rental_training` ещё нет. Он появится только на S01.

---

## 2. Зафиксированный baseline

Практикум использует конкретную контрольную точку Frappe, чтобы инструкция не менялась посреди обучения:

```text
Frappe Framework : v16.33.0
Bench CLI         : 5.31.0
Python            : 3.14.x
Node.js           : 24.x
Yarn               : 1.22.x
MariaDB            : 11.8.x
Redis              : 6+
```

Почему именно так:

- Frappe v16 требует Python 3.14;
- Frappe v16 требует Node 24;
- официальная installation page для v16 указывает MariaDB 11.8 и Yarn 1.22+;
- `v16.33.0` — зафиксированный release Framework для этого практикума;
- `5.31.0` — зафиксированный Bench CLI для этого практикума.

Первичные источники:

- https://docs.frappe.io/framework/user/en/installation
- https://github.com/frappe/frappe/releases/tag/v16.33.0
- https://github.com/frappe/frappe/blob/v16.33.0/pyproject.toml
- https://github.com/frappe/frappe/blob/v16.33.0/package.json
- https://github.com/frappe/bench/releases/tag/v5.31.0

### Почему не фиксируем каждую patch-версию системных пакетов

Debian, MariaDB, Node и Python должны оставаться внутри указанной совместимой линии и получать штатные исправления. Нам важно воспроизвести **контракт среды**, а не заморозить весь Linux до последнего пакета.

---

## 3. Какая ОС используется в инструкции

Основной путь практикума:

```text
Windows
└── WSL2
    └── Debian 13
```

Frappe официально поддерживает Debian/Ubuntu; для v16 installation page требует Debian 13+ или Ubuntu 24.04+.

Если у вас уже есть отдельный Linux/WSL со всеми версиями из раздела 2, установку ОС можно пропустить и начать с раздела 5 «Проверить системные зависимости».

Практикум **не использует существующий VEQTA bench**. Смысл S00 — получить отдельную чистую учебную среду.

---

# 4. Установить Debian 13 в WSL2

Если Debian 13 уже установлен и работает через WSL2, переходите к разделу 5.

## 4.1. PowerShell

Откройте PowerShell от имени администратора:

```powershell
wsl --update
wsl --list --online
wsl --install -d Debian
```

После установки:

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

## 4.2. Первый запуск

Откройте Debian и создайте обычного Linux-пользователя.

Дальше все команды выполняются **от обычного пользователя**, а `sudo` используется только там, где нужны системные права.

Проверка:

```bash
. /etc/os-release
printf 'USER=%s\nDEBIAN=%s\nCODENAME=%s\nINIT=%s\n' \
  "$(whoami)" "$VERSION_ID" "$VERSION_CODENAME" "$(ps -p 1 -o comm=)"
```

Ожидаем:

```text
DEBIAN=13
CODENAME=trixie
INIT=systemd
```

Если PID 1 не `systemd`, включите systemd для WSL и перезапустите WSL. Это вопрос окружения, не Frappe.

---

# 5. Установить системные зависимости

Обновите индекс пакетов:

```bash
sudo apt update
sudo apt full-upgrade -y
```

Установите зависимости, которые нужны текущему CORE-практикуму:

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

Запустите сервисы:

```bash
sudo systemctl enable --now mariadb
sudo systemctl enable --now redis-server
```

Проверка:

```bash
mariadb --version
redis-cli ping
systemctl is-active mariadb
systemctl is-active redis-server
```

Нужно получить:

```text
MariaDB ... 11.8.x ...
PONG
active
active
```

Если MariaDB не `11.8.x`, **не продолжайте**: сначала исправьте системную установку.

### Почему здесь нет wkhtmltopdf

PDF/Print Format не входит в CORE. Не ставим компонент заранее только потому, что он существует в полном production-стеке Frappe.

Когда в NEXT появится реальное требование печатного документа, вернёмся к зависимости для PDF.

---

# 6. Подготовить локального администратора MariaDB для Bench

Bench при создании Site должен иметь право создать базу данных и пользователя Site.

На Debian системный `root` MariaDB может быть настроен через Unix socket. Чтобы не менять системную модель `root`, для учебного Bench создаём отдельного локального администратора БД.

Откройте MariaDB:

```bash
sudo mariadb
```

В консоли MariaDB выполните, подставив свой пароль вместо `ВАШ_ПАРОЛЬ`:

```sql
CREATE USER 'frappe_admin'@'localhost' IDENTIFIED BY 'ВАШ_ПАРОЛЬ';
GRANT ALL PRIVILEGES ON *.* TO 'frappe_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

Проверьте:

```bash
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

Введите тот же пароль.

Это не специальная подсистема практикума. Bench штатно поддерживает параметр `--db-root-username`; мы лишь не используем системного `root` как учётную запись учебного инструмента.

Пароль нигде не записывайте в Git.

---

# 7. Установить Node.js и Yarn

## 7.1. NVM

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
```

Проверка:

```bash
nvm --version
```

## 7.2. Node 24

```bash
nvm install 24
nvm use 24
nvm alias default 24
```

Проверка:

```bash
node --version
```

Первая часть версии должна быть:

```text
v24.
```

## 7.3. Yarn Classic

```bash
npm install -g yarn@1.22.22
```

Проверка:

```bash
yarn --version
```

Ожидается:

```text
1.22.22
```

Не обновляйте JavaScript-зависимости самого Frappe вручную. Их версии принадлежат выбранному release Framework.

---

# 8. Установить uv, Python 3.14 и Bench

## 8.1. uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

Проверка:

```bash
uv --version
```

## 8.2. Python 3.14

```bash
uv python install 3.14 --default
```

Проверка:

```bash
python --version
python3.14 --version
```

Обе команды должны показывать Python `3.14.x`.

## 8.3. Bench 5.31.0

```bash
uv tool install 'frappe-bench==5.31.0'
```

Если shell ещё не видит `bench`:

```bash
uv tool update-shell
source ~/.bashrc
```

Проверка:

```bash
bench --version
```

Ожидается:

```text
5.31.0
```

Не используйте `sudo pip install frappe-bench`: Bench ставится в пользовательское окружение, а не в системный Python.

---

# 9. Контроль перед созданием Bench

Выполните одним блоком:

```bash
printf 'MARIADB=%s\n' "$(mariadb --version)"
printf 'REDIS=%s\n' "$(redis-cli ping)"
printf 'NODE=%s\n' "$(node --version)"
printf 'YARN=%s\n' "$(yarn --version)"
printf 'PYTHON=%s\n' "$(python --version)"
printf 'BENCH=%s\n' "$(bench --version)"
```

Контракт S00:

```text
MariaDB 11.8.x
Redis PONG
Node v24.x
Yarn 1.22.22
Python 3.14.x
Bench 5.31.0
```

Если один пункт не совпадает, не маскируйте проблему следующими командами.

---

# 10. Создать отдельный Bench на Frappe v16.33.0

```bash
mkdir -p ~/frappe
cd ~/frappe
```

Создайте Bench:

```bash
bench init \
  --frappe-branch v16.33.0 \
  --python "$(command -v python3.14)" \
  rental-training-bench
```

Перейдите в него:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте, что это Bench:

```bash
bench find .
```

Проверьте версии:

```bash
bench --version
bench version --format plain
./env/bin/python --version
node --version
yarn --version
```

Для Framework должно быть `16.33.0`.

Дополнительная строгая проверка tag:

```bash
cd apps/frappe
git describe --tags --exact-match
cd ../..
```

Ожидается:

```text
v16.33.0
```

### Что мы получили

```text
rental-training-bench/
├── env/
├── apps/
│   └── frappe/
└── sites/
```

`Bench` — это рабочая среда. Это ещё не Site и не наше приложение.

---

# 11. Создать чистый Site

Находясь в:

```text
~/frappe/rental-training-bench
```

выполните:

```bash
bench new-site rental.localhost \
  --db-root-username frappe_admin \
  --set-default
```

Bench запросит пароль `frappe_admin`, затем пароль пользователя Frappe `Administrator`.

Пароль `Administrator` нужен для входа в Desk. Это **другой пароль**, не пароль MariaDB.

После создания проверьте:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается ровно:

```text
frappe
```

Если здесь уже есть ERPNext или другое прикладное App, это не чистый Site для CORE.

Первичный источник по Site:

- https://docs.frappe.io/framework/user/en/tutorial/create-a-site
- https://docs.frappe.io/framework/user/en/bench/reference/new-site

---

# 12. Включить developer mode только для dev-site

На следующих этапах мы будем создавать **Standard DocType, принадлежащие App**, и их metadata должны сохраняться в исходниках. Для этого developer mode нужен именно разработческому Site `rental.localhost`.

Включите его как Site-local настройку:

```bash
bench --site rental.localhost set-config developer_mode 1
bench --site rental.localhost clear-cache
```

Проверьте:

```bash
bench --site rental.localhost show-config | grep developer_mode
```

Должно быть значение `1`/`true`.

### Почему здесь нет `-g`

```text
bench set-config -g ...
→ common_site_config.json
→ настройка наследуется другими Sites этого Bench
```

Для режима разработки это слишком широкая область. В S09 появится второй чистый acceptance-site, который должен доказать установку App **без developer mode**.

Поэтому граница такая:

```text
rental.localhost
→ developer_mode = 1

новый clean Site
→ developer_mode не требуется
```

Если вы проходили более раннюю версию практикума, где developer mode уже был включён глобально, исправьте это один раз:

```bash
bench set-config -g developer_mode None
bench --site rental.localhost set-config developer_mode 1
bench --site rental.localhost clear-cache
```

Это изменение окружения Bench, а не migration App.

Developer mode — не способ сделать Site production-ready. Это режим разработки.

---

# 13. Запустить dev-сервер

Из корня Bench:

```bash
bench start
```

Не закрывайте этот терминал: он показывает процессы dev-среды и их ошибки.

Откройте в браузере:

```text
http://rental.localhost:8000/app
```

Войдите:

```text
User: Administrator
Password: пароль, заданный при bench new-site
```

Официальный development flow использует `bench start` для запуска процессов Bench.

---

# 14. Контрольная точка S00

Откройте второй терминал Debian и выполните:

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

## S00 — ГОТОВО

Переход к S01 разрешён только если одновременно верно:

```text
[ ] Bench находится в ~/frappe/rental-training-bench
[ ] Bench CLI = 5.31.0
[ ] Frappe Framework = 16.33.0
[ ] Python = 3.14.x
[ ] Node = 24.x
[ ] MariaDB = 11.8.x
[ ] Redis отвечает PONG
[ ] Site rental.localhost существует
[ ] на Site установлен только frappe
[ ] developer mode включён только для rental.localhost
[ ] Desk открывается
[ ] вход Administrator работает
```

---

# 15. S00 — НЕ ГОТОВО

Не переходите дальше, если:

- `bench version` показывает другую major/minor линию Framework;
- Python не `3.14.x`;
- Node не `24.x`;
- MariaDB не `11.8.x`;
- Site не открывается;
- на Site уже установлен ERPNext или другое прикладное App;
- вы работаете внутри существующего VEQTA Bench;
- developer mode не включён на `rental.localhost`;
- developer mode включён глобально без причины;
- вы начали создавать DocType до появления собственного App.

---

# 16. Типовые ошибки новичка

### «Я нахожусь где-то в Linux и `bench` ругается»

Команды Site/App выполняются из корня нужного Bench:

```bash
cd ~/frappe/rental-training-bench
bench find .
```

### «Давайте сразу установим ERPNext — там больше готового»

Нет. Цель CORE — увидеть границу:

```text
что даёт Frappe
vs
что создаёт наше App
```

ERPNext эту границу размоет.

### «Давайте сразу создадим Equipment через Customize Form»

Нет. Собственного App ещё нет. Standard модель должна сразу иметь правильного владельца.

### «Можно поставить всё через sudo pip/npm?»

Не нужно. Node управляется через NVM, Python — через uv, Bench — через uv tool. Системный Python не превращаем в свалку проектных пакетов.

### «Почему мы не ставим всё, что умеет Frappe?»

Потому что практикум не каталог функций. Компонент появляется тогда, когда его требует следующий реальный сценарий.

---

# 17. Что ученик должен понять после S00

Без терминов «наизусть» ученик должен уметь объяснить:

```text
Bench
  = среда, в которой живут Apps и Sites

frappe App
  = сам Framework внутри Bench

Site
  = отдельный экземпляр Frappe со своей БД и конфигурацией

rental.localhost
  = наш чистый учебный Site
```

На S00 **ещё нет нашего предметного App**.

Следующий этап: [`S01_APP_AND_SITE.md`](S01_APP_AND_SITE.md) — создать `rental_training` и установить его на `rental.localhost`.