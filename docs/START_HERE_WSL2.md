# VEQTA — первый стенд на WSL2

Эта инструкция поднимает **локальный стенд разработки VEQTA на Windows через WSL2**.

После неё должно получиться:

```text
Windows
└── WSL2 / Ubuntu
    └── ~/frappe/veqta-bench/
        ├── apps/frappe/   # Framework, на котором работает стенд
        ├── apps/veqta/    # наш Git repository и Frappe app
        └── sites/veqta.localhost/
```

Что происходит по крупным этапам:

1. готовим Linux-среду внутри Windows;
2. ставим БД и зависимости Frappe;
3. подключаем GitHub;
4. создаём Bench с конкретной версией Frappe;
5. превращаем существующий `lazuale/veqta` в реальный Frappe app;
6. создаём локальный site и запускаем Desk;
7. после изменений со стенда отправляем реальный код VEQTA обратно в Git.

Выполнять по порядку. При ошибке не переходить к следующему шагу.

## 1. WSL2

**Зачем:** получить нормальную Linux-среду разработки Frappe внутри Windows. Сам Frappe и его зависимости будут жить здесь, а браузер и VS Code можно использовать из Windows.

В PowerShell от администратора:

```powershell
wsl --status
wsl -l -v
```

Нужен `Ubuntu-24.04` с `VERSION 2`.

Если его нет:

```powershell
wsl --install -d Ubuntu-24.04
```

В Ubuntu проверить:

```bash
cat /etc/os-release
ps -p 1 -o comm=
```

Если PID 1 не `systemd`:

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

Снова открыть Ubuntu.

После этого все Linux-команды ниже выполняются **в Ubuntu WSL**, а не в PowerShell.

## 2. Базовые пакеты

**Зачем:** поставить Git, Redis и системные библиотеки, которые нужны Bench/Frappe.

В Ubuntu:

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

## 3. MariaDB 11.8

**Зачем:** это база данных локального Frappe site. Для текущего стенда используем проверенную линию MariaDB 11.8, а не случайную версию из стандартного Ubuntu repository.

```bash
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup \
  | sudo bash -s -- --mariadb-server-version="mariadb-11.8"

sudo apt update
sudo apt install -y mariadb-server mariadb-client libmariadb-dev
sudo systemctl enable --now mariadb
mariadb --version
```

Вывод должен содержать `11.8`.

Затем:

```bash
sudo mariadb-secure-installation
```

Запомнить реквизиты администратора MariaDB — они понадобятся при создании site. В Git их не сохранять.

## 4. GitHub SSH

**Зачем:** чтобы WSL мог клонировать `lazuale/veqta` и отправлять изменения обратно в GitHub без ручного копирования файлов.

```bash
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
```

Содержимое `id_ed25519.pub` добавить в GitHub:

```text
Settings → SSH and GPG keys → New SSH key
```

Проверить:

```bash
ssh -T git@github.com
```

Настроить автора:

```bash
git config --global user.name "lazuale"
git config --global user.email "ВАШ_GITHUB_EMAIL"
git config --global init.defaultBranch main
```

## 5. Node, Python, Bench

**Зачем:** это runtime и инструменты сборки/управления Frappe. Bench создаёт окружение Frappe, приложения и sites.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 24
npm install -g yarn

curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.14 --default
uv tool install frappe-bench
```

Проверить:

```bash
node -v
python --version
yarn --version
bench --version
mariadb --version
redis-server --version
```

Целевые линии:

```text
Node      24.x
Python    3.14.x
MariaDB   11.8.x
```

## 6. Frappe Bench

**Зачем:** создать саму рабочую среду Frappe. В `apps/frappe` будет точный Framework, на котором мы реально проверяем VEQTA.

Актуальный baseline указан в `DEVELOPMENT.md`. Для текущего первого стенда:

```bash
mkdir -p ~/frappe
cd ~/frappe
bench init --frappe-branch v16.32.0 veqta-bench
cd ~/frappe/veqta-bench
bench version
```

Зафиксировать версию и commit:

```bash
cd ~/frappe/veqta-bench/apps/frappe
git describe --tags --always
git rev-parse HEAD
```

Результат записать в Issue #2. Это связывает наши выводы с конкретным кодом Frappe.

## 7. Создать app `veqta`

**Зачем:** именно здесь текущий repository перестаёт быть только документацией и становится настоящим устанавливаемым Frappe app.

Сначала клонировать текущий repository:

```bash
cd ~
git clone git@github.com:lazuale/veqta.git veqta-existing
```

Создать штатный scaffold Frappe:

```bash
cd ~/frappe/veqta-bench
bench new-app --no-git veqta
```

Ответы:

```text
App Title: VEQTA
App Description: VEQTA prototype on Frappe Framework
App Publisher: lazuale
App Email: ваш GitHub email
App License: agpl-3.0
Create GitHub Workflow action for unittests: No
Branch Name: main
```

Теперь объединить сгенерированный app с уже существующей Git history проекта:

```bash
rsync -a ~/veqta-existing/ ~/frappe/veqta-bench/apps/veqta/
cd ~/frappe/veqta-bench/apps/veqta
rm -f license.txt
sed -i 's/^app_license = .*/app_license = "AGPL-3.0-or-later"/' veqta/hooks.py
rm -rf ~/veqta-existing
```

Проверить:

```bash
grep '^app_license' veqta/hooks.py
git status
git remote -v
git diff
```

Должно быть:

```text
app_license = "AGPL-3.0-or-later"
```

Перед commit убедиться, что сохранены `README.md`, `LICENSE`, `.gitignore`, `docs/` и нет секретов или файлов всего Bench.

Первый commit реального приложения:

```bash
git add .
git diff --cached
git commit -m "Bootstrap VEQTA as Frappe app"
git push origin main
```

После этого GitHub уже должен содержать настоящий Frappe scaffold VEQTA.

## 8. Site

**Зачем:** app сам по себе — код. Site — локальный экземпляр Frappe с БД, в который этот app устанавливается и где мы будем работать через Desk.

```bash
cd ~/frappe/veqta-bench
bench new-site veqta.localhost --db-type mariadb
bench use veqta.localhost
bench --site veqta.localhost install-app veqta
bench --site veqta.localhost list-apps
```

В списке должны быть как минимум:

```text
frappe
veqta
```

Включить Developer Mode:

```bash
bench set-config -g developer_mode 1
bench --site veqta.localhost clear-cache
```

**Зачем Developer Mode:** когда мы создаём стандартные DocType приложения через Desk, Frappe должен записывать их metadata в исходное дерево `apps/veqta`, чтобы изменения можно было увидеть в Git.

## 9. Запуск

**Зачем:** поднять процессы dev-среды и открыть Desk в браузере.

```bash
cd ~/frappe/veqta-bench
bench start
```

В Windows открыть:

```text
http://veqta.localhost:8000
```

Войти пользователем `Administrator`.

Остановка: `Ctrl+C`.

## 10. VS Code

**Зачем:** видеть рядом код используемого Frappe и реальный код VEQTA, не смешивая их.

В Windows установить VS Code и расширение Microsoft `WSL`.

В Ubuntu:

```bash
cd ~/frappe/veqta-bench
code .
```

Рабочие каталоги:

```text
apps/frappe/   # Frappe текущего стенда; для проверки поведения Framework
apps/veqta/    # наш код; только он отправляется в lazuale/veqta
```

## 11. После изменений через Desk

**Зачем:** убедиться, что результат работы существует не только в локальной БД стенда.

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git diff
```

Если принятая конфигурация не появилась в app, определить штатный механизм Frappe для её экспорта до commit.

Рабочая цепочка:

```text
накликали / изменили
        ↓
проверили файлы app
        ↓
git diff
        ↓
commit + push
```

После рабочего запуска стенда переходить к `PROTOTYPE_V0_1.md` и Issue #2.
