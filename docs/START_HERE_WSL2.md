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

### Как читать интерактивные шаги

Если команда задаёт вопросы, ниже в инструкции указано, **что именно отвечать**. Не выбирать варианты наугад.

Пароли при вводе в Linux обычно **никак не отображаются**: нет ни `*`, ни точек. Это нормально — ввести пароль и нажать `Enter`.

В ходе установки появятся три разных учётных секрета:

```text
Linux / WSL user frappe   пароль пользователя Ubuntu
MariaDB root              пароль администратора базы данных
Frappe Administrator      пароль входа в Desk
```

Их не записывать в Git, README, Issue или исходный код. Хранить в менеджере паролей.

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

После установки открыть `Ubuntu 24.04` из меню Пуск. При первом запуске Ubuntu создаёт Linux-пользователя.

Если появятся вопросы:

```text
Enter new UNIX username: frappe
New password:             придумать пароль Linux-пользователя
Retype new password:      повторить тот же пароль
```

Дальше в этой инструкции предполагается, что Linux-пользователь называется `frappe`.

В Ubuntu проверить:

```bash
whoami
cat /etc/os-release
ps -p 1 -o comm=
```

Ожидается:

```text
whoami        -> frappe
Ubuntu        -> 24.04
PID 1         -> systemd
```

Если PID 1 не `systemd`:

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

При первом `sudo` Ubuntu может спросить:

```text
[sudo] password for frappe:
```

Ввести **пароль Linux-пользователя `frappe`**, созданный выше.

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

Ключ `-y` автоматически подтверждает установку пакетов. Если `sudo` снова спросит пароль — это пароль Linux-пользователя `frappe`.

Проверить Redis:

```bash
systemctl is-active redis-server
redis-cli ping
```

Ожидается:

```text
active
PONG
```

## 3. MariaDB 11.8

**Зачем:** это база данных локального Frappe site. Для текущего стенда используем поддерживаемую Frappe линию MariaDB 11.8, а не случайную версию из стандартного Ubuntu repository.

Подключить официальный repository MariaDB и установить сервер:

```bash
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup \
  | sudo bash -s -- --mariadb-server-version="mariadb-11.8"

sudo apt update
sudo apt install -y mariadb-server mariadb-client libmariadb-dev
sudo systemctl enable --now mariadb
```

Проверить, что сервис запущен и установлена именно линия `11.8`:

```bash
systemctl is-active mariadb
mariadb --version
```

Ожидается:

```text
active
mariadb ... 11.8.x ...
```

Если версия не `11.8.x`, дальше не идти.

### Первичная настройка безопасности MariaDB

Запустить:

```bash
sudo mariadb-secure-installation
```

Для **этого локального стенда VEQTA** отвечать так:

```text
Enter current password for root (enter for none):
-> просто Enter

Switch to unix_socket authentication [Y/n]
или Enable unix_socket authentication [Y/n]
-> n

Change the root password? [Y/n]
-> Y

New password:
-> придумать отдельный пароль MariaDB root

Re-enter new password:
-> повторить тот же пароль

Remove anonymous users? [Y/n]
-> Y

Disallow root login remotely? [Y/n]
-> Y

Remove test database and access to it? [Y/n]
-> Y

Reload privilege tables now? [Y/n]
-> Y
```

То есть логика такая:

```text
unix_socket для root       -> нет
root password              -> задать
anonymous users            -> удалить
disallow remote root       -> да
test database              -> удалить
reload privilege tables    -> да
```

Почему `unix_socket -> n`: позже `bench new-site` должен иметь возможность войти в MariaDB администратором базы по паролю. При этом удалённый вход `root` запрещаем — пароль используется только локально внутри WSL.

В конце должен появиться текст о завершении настройки (`All done` / установка защищена).

### Проверка пароля MariaDB root

Сразу проверить, что пароль действительно работает:

```bash
mariadb -u root -p
```

Появится:

```text
Enter password:
```

Ввести **пароль MariaDB root**, который только что задали. Если вход успешен, появится приглашение вида:

```text
MariaDB [(none)]>
```

Внутри MariaDB выполнить:

```sql
SELECT VERSION();
SELECT USER(), CURRENT_USER();
EXIT;
```

`SELECT VERSION()` должен вернуть `11.8.x`, после `EXIT;` вернёмся в обычную Linux-консоль.

**Запомнить пароль MariaDB root.** Он понадобится в разделе **8. Site**, когда `bench new-site` спросит `MariaDB root password`. В Git его не сохранять.

## 4. GitHub SSH

**Зачем:** чтобы WSL мог клонировать `lazuale/veqta` и отправлять изменения обратно в GitHub без ручного копирования файлов.

Создать SSH-ключ:

```bash
ssh-keygen -t ed25519
```

Для локального стенда отвечать:

```text
Enter file in which to save the key (.../.ssh/id_ed25519):
-> Enter

Enter passphrase (empty for no passphrase):
-> Enter

Enter same passphrase again:
-> Enter
```

То есть используем стандартный путь `~/.ssh/id_ed25519` без passphrase. Это допустимо для локального dev-стенда; доступ к самому Windows/WSL-профилю должен быть защищён.

Показать публичный ключ:

```bash
cat ~/.ssh/id_ed25519.pub
```

Скопировать **всю одну строку**, начинающуюся с `ssh-ed25519`.

В GitHub открыть:

```text
Avatar -> Settings -> SSH and GPG keys -> New SSH key
```

Заполнить:

```text
Title:    VEQTA WSL2
Key type: Authentication Key
Key:      вставить строку из id_ed25519.pub
```

Нажать `Add SSH key`.

Проверить из Ubuntu:

```bash
ssh -T git@github.com
```

При первом подключении может появиться:

```text
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Ответить:

```text
yes
```

Ожидаемый результат содержит:

```text
Hi lazuale! You've successfully authenticated...
```

GitHub shell-доступ не предоставляет — соответствующее сообщение после успешной аутентификации нормально.

Настроить автора Git-коммитов:

```bash
git config --global user.name "lazuale"
git config --global user.email "ВАШ_GITHUB_EMAIL"
git config --global init.defaultBranch main
```

Вместо `ВАШ_GITHUB_EMAIL` указать email, который должен отображаться в Git-коммитах.

Проверить:

```bash
git config --global user.name
git config --global user.email
git config --global init.defaultBranch
```

## 5. Node, Python, Bench

**Зачем:** это runtime и инструменты сборки/управления Frappe. Bench создаёт окружение Frappe, приложения и sites.

Для первого стенда VEQTA используем **фиксированные версии**, чтобы повторная установка давала тот же runtime и тот же набор управляющих инструментов. Не заменять их на плавающие `24`, `3.14` или `latest` без отдельного обновления этой инструкции.

Зафиксированный стек:

```text
NVM           0.40.3
Node.js       24.20.0
npm           11.19.0
Yarn          1.22.22
uv            0.12.7
Python        3.14.7
Frappe Bench  5.31.0
```

`npm 11.19.0` уже входит в Node.js `24.20.0`; отдельно обновлять npm не нужно.

Установить Node.js и Yarn:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc

nvm install 24.20.0
nvm use 24.20.0
nvm alias default 24.20.0

npm install -g --allow-scripts=yarn yarn@1.22.22
```

Установить фиксированную версию `uv`, Python и Bench:

```bash
curl -LsSf https://astral.sh/uv/0.12.7/install.sh | sh
source ~/.bashrc

uv python install 3.14.7 --default
uv tool install 'frappe-bench==5.31.0'
```

Эти команды не должны требовать выбора вариантов. Сообщения об успешной загрузке и установке — нормальны; при `error` дальше не идти.

Проверить:

```bash
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

echo "=== MARIADB ==="
mariadb --version

echo "=== REDIS ==="
redis-server --version
```

Для runtime/toolchain должны получиться именно:

```text
NVM           0.40.3
Node.js       v24.20.0
npm           11.19.0
Yarn          1.22.22
uv            0.12.7
Python        3.14.7
Frappe Bench  5.31.0
```

Если версия отличается, не переходить к следующему шагу, пока причина не выяснена.

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

`bench init` скачивает Frappe, создаёт Python virtual environment, устанавливает зависимости и собирает assets. Вывод будет длинным — это нормально. На этом шаге ничего выбирать не требуется.

Команда должна завершиться без `ERROR`/`Traceback` и вернуть обычное приглашение Linux-консоли.

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

Команда интерактивная. Отвечать:

```text
App Title: VEQTA
App Description: VEQTA prototype on Frappe Framework
App Publisher: lazuale
App Email: ваш GitHub email
App License: agpl-3.0
Create GitHub Workflow action for unittests: No
Branch Name: main
```

Если формулировка вопроса немного отличается, смысл значений сохранять. Пароли здесь не вводятся.

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

Создать site:

```bash
cd ~/frappe/veqta-bench
bench new-site veqta.localhost --db-type mariadb
```

Команда спросит как минимум два пароля.

```text
MariaDB root password:
-> ввести пароль MariaDB root из раздела 3

Set Administrator password:
-> придумать пароль пользователя Frappe Administrator
```

Если попросит повторить пароль Administrator — ввести тот же пароль ещё раз.

Это **разные пароли**:

```text
MariaDB root          -> нужен Bench для создания базы и DB user
Frappe Administrator  -> нужен человеку для входа в Desk
```

После успешного создания site продолжить:

```bash
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

`bench start` остаётся работать в текущем окне терминала и выводит логи процессов. Это нормально; приглашение shell не вернётся, пока Bench работает.

В Windows открыть:

```text
http://veqta.localhost:8000
```

На странице входа:

```text
User / Email: Administrator
Password:     пароль Frappe Administrator из раздела 8
```

Если открылась Desk — стенд запущен.

Остановка Bench в Ubuntu: `Ctrl+C`.

## 10. VS Code

**Зачем:** видеть рядом код используемого Frappe и реальный код VEQTA, не смешивая их.

В Windows установить VS Code. Затем открыть Extensions (`Ctrl+Shift+X`), найти расширение Microsoft **WSL** и нажать `Install`.

В Ubuntu:

```bash
cd ~/frappe/veqta-bench
code .
```

При первом запуске VS Code может несколько секунд устанавливать `VS Code Server` внутрь WSL. Это нормально; дождаться открытия окна VS Code, подключённого к WSL.

В левом нижнем углу VS Code должно быть видно, что окно работает через WSL/Ubuntu.

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
