# VEQTA — старт локальной разработки на WSL2

Статус: **единственная актуальная инструкция локального dev-стенда**.

Эта инструкция нужна для первого bootstrap реального Frappe app VEQTA на Windows + WSL2.

> Выполнять разделы по порядку. Если команда завершилась ошибкой — не переходить дальше, пока ошибка не разобрана.

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

Нужен `Ubuntu-24.04` с `VERSION 2`.

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

Ожидается Ubuntu 24.04 и:

```text
systemd
```

Если `systemd` не используется, выполнить в Ubuntu:

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

и снова открыть Ubuntu.

## 2. Поставить базовые пакеты

Все следующие Linux-команды выполняются **в Ubuntu WSL**, а не в PowerShell.

```bash
sudo apt update
sudo apt install -y \
  git \
  openssh-client \
  redis-server \
  pkg-config \
  curl \
  rsync \
  ca-certificates \
  apt-transport-https

sudo systemctl enable --now redis-server
```

Проверить:

```bash
git --version
redis-server --version
```

## 3. Поставить MariaDB 11.8

Для Frappe v16 целевая версия MariaDB — **11.8**. Не полагаемся на версию `mariadb-server` из стандартного Ubuntu repository.

Подключить официальный MariaDB repository, зафиксированный на линии 11.8:

```bash
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup \
  | sudo bash -s -- --mariadb-server-version="mariadb-11.8"

sudo apt update
sudo apt install -y \
  mariadb-server \
  mariadb-client \
  libmariadb-dev

sudo systemctl enable --now mariadb
```

Проверить:

```bash
mariadb --version
```

**Не продолжать**, если вывод не содержит `11.8`.

Если установка не попросила задать пароль администратора MariaDB:

```bash
sudo mariadb-secure-installation
```

Запомнить выбранные реквизиты администратора MariaDB. Они понадобятся при создании site.

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

Проверить всё до продолжения:

```bash
node -v
python --version
yarn --version
bench --version
mariadb --version
redis-server --version
```

Ожидаемые основные линии:

```text
Node      24.x
Python    3.14.x
MariaDB   11.8.x
```

## 7. Создать Bench с проверенной stable-версией Frappe

Перед фактическим выполнением проверить текущую stable-версию согласно `DEVELOPMENT.md`.

На дату последнего аудита (2026-08-29) последняя проверенная stable-версия линии v16 — `v16.32.0`.

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

Сохранить этот вывод в Issue #1.

`apps/frappe` не редактируется ради VEQTA.

## 8. Превратить существующий repository в Frappe app

Repository уже существует и содержит документацию, `LICENSE` и `.gitignore`, поэтому нельзя создавать второй независимый Git repository тем же именем.

### 8.1. Временно клонировать существующий repository

```bash
cd ~
git clone git@github.com:lazuale/veqta.git veqta-existing
cd ~/veqta-existing
git status
```

Рабочее дерево должно быть чистым.

### 8.2. Создать штатный Frappe scaffold без нового Git

```bash
cd ~/frappe/veqta-bench
bench new-app --no-git veqta
```

На вопросы первого bootstrap отвечать:

```text
App Title: VEQTA
App Description: Configurable work management on Frappe Framework
App Publisher: lazuale
App Email: ваш GitHub email
App License: agpl-3.0
Create GitHub Workflow action for unittests: No
Branch Name: main
```

Почему в prompt выбирается `agpl-3.0`: это штатный вариант генератора Frappe v16. Продуктовое решение VEQTA при этом — **`AGPL-3.0-or-later`**; после объединения metadata приводится к нему явно.

### 8.3. Соединить scaffold с существующей Git history

```bash
rsync -a ~/veqta-existing/ ~/frappe/veqta-bench/apps/veqta/
cd ~/frappe/veqta-bench/apps/veqta
```

Удалить дублирующий license-файл, который создал boilerplate:

```bash
rm -f license.txt
```

Привести metadata приложения к принятой лицензии:

```bash
sed -i 's/^app_license = .*/app_license = "AGPL-3.0-or-later"/' veqta/hooks.py
grep '^app_license' veqta/hooks.py
```

Ожидается:

```text
app_license = "AGPL-3.0-or-later"
```

Проверить Git:

```bash
git status
git remote -v
```

`origin` должен указывать на `lazuale/veqta`.

После проверки:

```bash
rm -rf ~/veqta-existing
```

Теперь `apps/veqta` одновременно является Frappe app и рабочим Git repository проекта.

## 9. Проверить первый diff и сделать commit scaffold

Сначала **не коммитить вслепую**:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

Проверить минимум:

- существующие `README.md`, `LICENSE`, `.gitignore` и `docs/` не потерялись;
- появился реальный Frappe app scaffold;
- нет `license.txt`;
- в `veqta/hooks.py` стоит `AGPL-3.0-or-later`;
- нет паролей, site config или файлов всего Bench.

Только затем:

```bash
git add .
git diff --cached
git commit -m "Bootstrap VEQTA as Frappe app"
git push origin main
```

После push repository должен содержать настоящий Frappe app scaffold.

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
