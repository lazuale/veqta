# 0. Учебный стенд Frappe 16

Эта глава выполняется **до главы 1**.

Курс дальше предполагает, что у ученика есть живой локальный Frappe 16, где можно:

```text
создавать DocType
создавать Documents
менять permissions
строить Workflow
создавать отчёты
проверять Web Form
вызывать REST API
писать Client Script
писать Server Script
смотреть файлы App
запускать bench-команды
ломать учебные данные и восстанавливать стенд
```

Это не production deployment. Это специально **учебная лаборатория**, которую не жалко сломать.

Проверено: **2026-08-31**.

---

# Часть I. Что мы сейчас построим

## 1. Итоговая схема

Основной путь курса:

```text
Windows 11
└── WSL2
    └── Debian 13
        └── ~/frappe/frappe16-course-bench/
            ├── env/
            ├── apps/
            │   ├── frappe/      ← Frappe Framework v16.32.0
            │   └── training/    ← наше учебное App
            └── sites/
                └── learn.localhost/
```

В браузере:

```text
http://learn.localhost:8000
```

Пользователь:

```text
Administrator
```

---

## 2. Почему используется отдельный учебный App

В следующих главах мы будем создавать собственные учебные DocType.

Им нужен нормальный Module, принадлежащий приложению.

Поэтому стенд заранее получает App:

```text
training
```

и Module:

```text
Training
```

Пока не нужно понимать внутреннее устройство App.

На этом этапе достаточно модели:

```text
Frappe
→ Framework

training
→ пустой контейнер для наших учебных объектов

learn.localhost
→ Site, где мы всё запускаем
```

В главах про App, Developer Mode и файлы приложения мы вернёмся к этому же `training` и разберём уже осознанно, что Bench создал на диске.

---

## 3. Почему не Docker

Docker отлично подходит для многих deployment-задач, но этот курс позже требует руками увидеть:

```text
apps/training/
hooks.py
DocType JSON
Python controller
JavaScript files
patches
fixtures
tests
logs
bench commands
```

Для обучения разработке Frappe обычный Bench внутри Linux-среды даёт более прямую картину.

Контейнеризацию можно изучать отдельно после понимания самой платформы.

---

## 4. Почему WSL2 + Debian 13

Frappe официально ориентируется на Unix-like окружение; для Windows документация прямо предлагает WSL.

Для v16 актуальные системные требования включают:

```text
Debian / Ubuntu
MariaDB 11.8
Python 3.14
Node.js 24
Redis / Valkey 6+
Yarn 1.22+
```

Debian 13 удобен для учебного стенда тем, что MariaDB 11.8 доступна из штатных репозиториев дистрибутива.

---

# Часть II. Правила учебного стенда

## 5. Не используем его для реальных данных

На стенде будут намеренно выполняться действия вроде:

```text
Delete
Cancel
reinstall Site
ошибочные permissions
сломанные Scripts
неудачные migrations
```

Поэтому:

> никаких рабочих и единственных экземпляров данных здесь быть не должно.

---

## 6. Не работаем под Linux root

Bench запускаем от обычного пользователя Linux.

`sudo` используем только для системных операций:

```text
apt
systemctl
настройка MariaDB
```

Не запускай:

```bash
sudo bench ...
```

без специальной причины.

---

## 7. Не ставим ERPNext

Курс посвящён именно:

```text
Frappe Framework 16
```

Поэтому на учебном Site сначала будут установлены только:

```text
frappe
training
```

ERPNext, HRMS, CRM, Helpdesk и другие Apps здесь не нужны.

---

# Часть III. Установка WSL2 и Debian 13

## 8. Проверяем WSL

Открой PowerShell **от имени администратора**:

```powershell
wsl --update
wsl --status
wsl --list --online
```

В списке должен быть Debian.

---

## 9. Устанавливаем Debian

```powershell
wsl --install -d Debian
```

После установки проверь:

```powershell
wsl -l -v
```

Нужно увидеть примерно:

```text
NAME      STATE      VERSION
Debian    Stopped    2
```

Критично:

```text
VERSION = 2
```

Если почему-то `1`:

```powershell
wsl --set-version Debian 2
```

---

## 10. Первый запуск Debian

Открой `Debian` из меню Пуск.

Создай обычного Linux-пользователя.

Например:

```text
username: dev
```

Имя пользователя в курсе не принципиально.

Пароль Linux при вводе в терминале обычно не отображается вообще — даже звёздочками. Это нормально.

---

## 11. Проверяем систему

В Debian:

```bash
cd ~
. /etc/os-release

echo "USER=$(whoami)"
echo "VERSION=$VERSION_ID"
echo "CODENAME=$VERSION_CODENAME"
echo "INIT=$(ps -p 1 -o comm=)"
echo "HOME=$HOME"
```

Ожидаем:

```text
VERSION=13
CODENAME=trixie
INIT=systemd
```

Если `systemd` не используется, включи его:

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

Снова открой Debian и повтори проверку.

---

# Часть IV. Системные зависимости

## 12. Обновляем Debian

```bash
sudo apt update
sudo apt full-upgrade -y
```

---

## 13. Ставим необходимые пакеты

```bash
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
  cron \
  xvfb \
  libfontconfig
```

`xvfb` и `libfontconfig` понадобятся при работе с печатью/PDF.

Сам `wkhtmltopdf 0.12.6 patched Qt`, требуемый документацией Frappe для соответствующего PDF-механизма, мы установим и проверим непосредственно в главе про Print/PDF: так ученик увидит, зачем эта зависимость вообще существует.

---

## 14. Запускаем сервисы

```bash
sudo systemctl enable --now mariadb
sudo systemctl enable --now redis-server
sudo systemctl enable --now cron
```

---

## 15. Проверяем сервисы

```bash
mariadb --version
redis-cli ping
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

Если MariaDB не линии `11.8`, дальше не иди, пока не разберёшься с системой пакетов.

---

# Часть V. Локальный администратор MariaDB для Bench

## 16. Зачем отдельный пользователь

На Debian системный MariaDB `root` удобно оставить с его штатной локальной авторизацией.

Для Bench создадим отдельного локального администратора:

```text
frappe_admin
```

Он нужен только нашему учебному компьютеру для создания и удаления учебных баз.

---

## 17. Открываем MariaDB

```bash
sudo mariadb
```

Увидишь приглашение вида:

```text
MariaDB [(none)]>
```

---

## 18. Создаём пользователя

Придумай отдельный пароль MariaDB и выполни:

```sql
CREATE USER 'frappe_admin'@'localhost' IDENTIFIED BY 'ВАШ_ПАРОЛЬ_MARIADB';
GRANT ALL PRIVILEGES ON *.* TO 'frappe_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

Не используй буквальный текст `ВАШ_ПАРОЛЬ_MARIADB`.

---

## 19. Проверяем вход

```bash
mariadb -u frappe_admin -p -e "SELECT VERSION();"
```

Введи пароль.

Должна отобразиться MariaDB 11.8.x.

---

# Часть VI. Node.js и Yarn

## 20. Устанавливаем NVM

Frappe рекомендует ставить Node через NVM.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
```

Проверь:

```bash
nvm --version
```

---

## 21. Устанавливаем Node.js 24

```bash
nvm install 24
nvm use 24
nvm alias default 24
```

Проверяем:

```bash
node --version
npm --version
```

Критично:

```text
Node major = 24
```

Отдельно обновлять npm ради курса не нужно.

---

## 22. Устанавливаем Yarn Classic

```bash
npm install -g yarn@1.22.22
```

Проверяем:

```bash
yarn --version
```

Ожидаем:

```text
1.22.22
```

---

# Часть VII. Python, uv и Bench

## 23. Устанавливаем uv

Frappe рекомендует `uv` для установки Python и Bench.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

Проверяем:

```bash
uv --version
```

---

## 24. Устанавливаем Python 3.14

```bash
uv python install 3.14 --default
```

Проверяем:

```bash
python --version
python3.14 --version
```

Критично:

```text
Python 3.14.x
```

---

## 25. Устанавливаем Bench CLI

Для воспроизводимого стенда курса фиксируем Bench:

```bash
uv tool install 'frappe-bench==5.31.0'
```

Если shell ещё не видит команду:

```bash
uv tool update-shell
source ~/.bashrc
```

Проверяем:

```bash
bench --version
```

Ожидаем:

```text
5.31.0
```

---

# Часть VIII. Контроль окружения перед Frappe

## 26. Выполняем одну проверку

```bash
. /etc/os-release

echo "DEBIAN=$VERSION_ID/$VERSION_CODENAME"
echo "MARIADB=$(mariadb --version)"
echo "REDIS=$(redis-cli ping)"
echo "NODE=$(node --version)"
echo "NPM=$(npm --version)"
echo "YARN=$(yarn --version)"
echo "UV=$(uv --version)"
echo "PYTHON=$(python --version)"
echo "BENCH=$(bench --version)"
```

Минимальный смысл результата:

```text
Debian 13 / trixie
MariaDB 11.8.x
Redis PONG
Node 24.x
Yarn 1.22.22
Python 3.14.x
Bench 5.31.0
```

Если базовая версия не совпадает, лучше исправить её сейчас, а не искать странные ошибки после `bench init`.

---

# Часть IX. Создаём Bench с Frappe 16.32.0

## 27. Создаём рабочую папку

```bash
mkdir -p ~/frappe
cd ~/frappe
```

---

## 28. Создаём Bench

Курс фиксируется на официальном релизе:

```text
Frappe Framework v16.32.0
```

Команда:

```bash
bench init \
  --frappe-branch v16.32.0 \
  --python "$(command -v python3.14)" \
  frappe16-course-bench
```

Команда делает много работы:

```text
создаёт Python virtual environment
скачивает Frappe
устанавливает Python dependencies
устанавливает Node dependencies
собирает assets
создаёт структуру Bench
```

Не нужно пока запоминать детали — мы разберём Bench отдельно.

---

## 29. Заходим в Bench

```bash
cd ~/frappe/frappe16-course-bench
```

Проверяем:

```bash
bench version
./env/bin/python --version
```

Должно быть:

```text
frappe 16.32.0
Python 3.14.x
```

---

## 30. Проверяем точный tag

```bash
cd apps/frappe
git describe --tags --exact-match
cd ../..
```

Ожидаем:

```text
v16.32.0
```

---

# Часть X. Создаём учебный Site

## 31. Создаём `learn.localhost`

Из каталога Bench:

```bash
cd ~/frappe/frappe16-course-bench
bench new-site learn.localhost --db-root-username frappe_admin
```

Bench спросит:

```text
пароль frappe_admin в MariaDB
пароль Frappe Administrator
```

Это **два разных пароля**.

Запомни пароль Frappe `Administrator`: им будем входить в Desk.

---

## 32. Что сейчас произошло

Bench создал:

```text
sites/learn.localhost/
```

и отдельную базу данных этого Site.

Кроме того, Frappe Framework автоматически установлен на Site.

---

## 33. Проверяем Site

```bash
bench --site learn.localhost list-apps
```

Пока ожидаем:

```text
frappe 16.32.0
```

---

# Часть XI. Создаём учебное App `training`

## 34. Создаём App

Убедись, что находишься в Bench:

```bash
cd ~/frappe/frappe16-course-bench
bench find .
```

Затем:

```bash
bench new-app training
```

Bench задаст несколько вопросов.

Для учебного стенда можно заполнить примерно так:

```text
App Title: Training
App Description: Frappe 16 course laboratory
App Publisher: своё имя или Student
App Email: свой email
App License: MIT
```

Остальные значения можно оставить по умолчанию.

---

## 35. Что появилось на диске

```bash
ls -la apps/training
```

Ты увидишь реальное Python/Frappe приложение.

Пока ничего в нём руками не меняй.

---

## 36. Устанавливаем App на Site

```bash
bench --site learn.localhost install-app training
```

Проверяем:

```bash
bench --site learn.localhost list-apps
```

Теперь ожидаем:

```text
frappe 16.32.0
training 0.0.1
```

Точная dev-версия `training` может отображаться немного иначе — важно само наличие приложения.

---

# Часть XII. Developer Mode для учебного курса

## 37. Почему включаем его сразу

В учебнике мы будем создавать **Standard DocType внутри `training`**, чтобы ученик мог одновременно увидеть:

```text
что появилось в Desk
и
какие файлы Frappe создал в App
```

Для этого нужен Developer Mode.

Команда:

```bash
bench set-config -g developer_mode true
```

---

## 38. Почему теория Developer Mode будет позже

Сейчас мы только включаем инструмент лаборатории.

Позже отдельно разберём:

```text
что именно меняет Developer Mode
Standard vs Custom
что сохраняется в БД
что появляется в Git
почему production Site обычно устроен иначе
```

Это тот же принцип, что в автошколе: сначала можно научиться пользоваться педалью, а устройство привода разобрать позже.

---

# Часть XIII. Первый запуск

## 39. Запускаем development processes

Из Bench:

```bash
cd ~/frappe/frappe16-course-bench
bench start
```

Терминал останется занят процессами Frappe.

Не закрывай его во время работы со стендом.

---

## 40. Открываем браузер

Открой:

```text
http://learn.localhost:8000
```

Войди:

```text
User: Administrator
Password: пароль, заданный при bench new-site
```

---

## 41. Если браузер не открывает `learn.localhost`

Сначала из второго окна Debian проверь:

```bash
curl -I http://learn.localhost:8000
```

Если здесь есть HTTP response, Frappe работает, а проблема находится между Windows/browser и именем хоста.

Для `.localhost` современные браузеры обычно направляют запрос на loopback автоматически.

Если не работает и `curl`, смотри терминал с `bench start`: там почти всегда уже видна причина.

---

# Часть XIV. Второй терминал

## 42. Для курса удобно держать два окна Debian

### Терминал 1

```bash
cd ~/frappe/frappe16-course-bench
bench start
```

Он показывает живые процессы и логи.

### Терминал 2

Используется для:

```text
bench commands
git status
просмотра файлов
curl
console
миграций
backup
```

Каждый раз начинай с:

```bash
cd ~/frappe/frappe16-course-bench
```

---

# Часть XV. Первый осмотр — ничего не меняем

## 43. Посмотри структуру Bench

Во втором терминале:

```bash
cd ~/frappe/frappe16-course-bench
find . -maxdepth 2 -type d | sort | head -80
```

Не надо запоминать вывод.

Найди глазами:

```text
env
apps
apps/frappe
apps/training
sites
sites/learn.localhost
logs
config
```

В главе 1 мы уже разберём, что из этого что означает.

---

## 44. Посмотри установленные Apps

```bash
bench --site learn.localhost list-apps
```

---

## 45. Посмотри версии

```bash
bench version
```

---

## 46. Посмотри Site config

```bash
cat sites/learn.localhost/site_config.json
```

Не публикуй содержимое этого файла бездумно: там могут находиться чувствительные настройки и credentials БД.

Сейчас достаточно увидеть, что Site — это не абстракция, а реальная конфигурация внутри Bench.

---

# Часть XVI. Первый checkpoint

## 47. Стенд готов только если выполняются все условия

Проверь:

```text
[ ] Debian 13 запущен в WSL2
[ ] MariaDB работает
[ ] Redis отвечает PONG
[ ] Python = 3.14.x
[ ] Node = 24.x
[ ] Yarn = 1.22.22
[ ] Bench работает
[ ] Frappe = 16.32.0
[ ] Site learn.localhost существует
[ ] App training установлен на Site
[ ] bench start запускается без фатальной ошибки
[ ] http://learn.localhost:8000 открывает Frappe
[ ] вход Administrator работает
```

Если хотя бы один базовый пункт не работает, дальше по книге идти рано.

---

# Часть XVII. Как будет устроена практика курса

## 48. Один Site на весь основной курс

Мы не будем создавать новый Site в каждой главе.

Будет один накопительный стенд:

```text
learn.localhost
```

Он будет постепенно усложняться.

---

## 49. Один сквозной учебный объект

Начиная с главы про DocType мы создадим:

```text
Request
```

И будем постепенно превращать его из простой формы в полноценный объект Frappe.

Он получит:

```text
поля
Link
Child Table
naming
permissions
assignment
workflow
notification
attachments
versions
reports
Web Form
REST API
Client Script
Server Script
```

То есть каждая следующая глава будет менять **реально существующую систему**, а не показывать оторванный пример.

---

## 50. Дополнительные учебные объекты будут появляться только когда нужны

Например:

```text
Request Item
Training Settings
Training User / роли
Approval Record
```

Курс не должен заранее создавать десятки сущностей, смысл которых ученик ещё не понимает.

---

# Часть XVIII. Новый стандарт каждой главы

## 51. Теория больше не является основной частью главы

Каждая практическая глава должна строиться так:

```text
1. Что сегодня увидим
2. Что уже должно быть на стенде
3. Минимальная теория
4. Сделай руками
5. Что именно должно появиться
6. Проверь результат
7. Измени условие и посмотри разницу
8. Намеренно вызови одну типичную ошибку
9. Исправь её
10. Что сохранилось в БД / metadata / файлах
11. Контрольные вопросы
12. Состояние стенда после главы
```

---

## 52. Главное правило курса

Недостаточно прочитать:

```text
Frappe умеет Workflow
```

Ученик должен:

```text
создать Workflow
увидеть кнопки переходов
перейти между состояниями
попробовать сделать это пользователем без нужной роли
увидеть отказ
исправить permission
```

Только после этого механизм считается изученным.

---

## 53. Мы будем не только делать правильный вариант

Очень многое во Frappe лучше понимается через контраст.

Например:

```text
Mandatory в DocField
vs
Mandatory только через Client Script
```

Поэтому практика иногда специально попросит:

```text
сделать неправильно
увидеть последствия
вернуть правильную настройку
```

---

# Часть XIX. Как не бояться сломать стенд

## 54. Создай первый backup

Остановить `bench start` не обязательно, но для начала проще выполнить во втором терминале:

```bash
cd ~/frappe/frappe16-course-bench
bench --site learn.localhost backup
```

Посмотри:

```bash
ls -lah sites/learn.localhost/private/backups
```

Backup/restore подробно будет разобран позже.

Сейчас важно только увидеть: учебный Site можно копировать и восстанавливать.

---

## 55. Если учебный Site безнадёжно сломан

Так как реальных данных в нём нет, крайний вариант:

```bash
bench --site learn.localhost --force reinstall
```

Команда уничтожает данные Site и создаёт БД заново.

После этого учебные изменения придётся повторить или восстановить из backup.

Поэтому не применяй `reinstall` к реальному production Site.

---

## 56. Если сломан только один эксперимент

Не переустанавливай всё автоматически.

Сначала учись находить локальную причину:

```text
неверное поле
permission
Script
Workflow
cache
migration
```

Диагностика — тоже часть курса.

---

# Часть XX. Контрольный эксперимент перед главой 1

## 57. Открой Desk

После входа через `Administrator`:

1. открой Awesome Bar;
2. найди `User`;
3. открой список пользователей;
4. вернись назад;
5. найди `DocType`;
6. открой список DocType;
7. ничего пока не создавай.

Задача — просто убедиться, что Desk живой и поиском можно находить системные объекты.

---

## 58. Одновременно посмотри Terminal 1

Во время переходов по Desk в окне с:

```bash
bench start
```

будут появляться HTTP requests и служебный вывод.

Это первый важный момент курса:

```text
ты нажимаешь что-то в браузере
→ на сервере реально происходит работа
```

Frappe — не набор статичных экранов.

---

# Что нужно запомнить

1. Курс проходит на живом `learn.localhost`, а не только по тексту.
2. Стенд находится внутри WSL2 / Debian 13.
3. `frappe16-course-bench` — наш Bench.
4. `learn.localhost` — наш Site.
5. `frappe` — Framework App.
6. `training` — пустое учебное App, куда будут попадать наши Standard-объекты.
7. Developer Mode включён специально для лаборатории; подробно он будет разобран позже.
8. Frappe Framework зафиксирован на `v16.32.0`, чтобы книга и стенд говорили об одной версии.
9. `bench start` должен работать всё время, пока мы используем development Site.
10. Второй терминал нужен для bench-команд, curl, Git и диагностики.
11. Учебный Site можно и нужно ломать — но только понимая, что именно проверяется.
12. Начиная со следующей главы теория всегда должна связываться с действием на этом стенде.

---

# Официальные источники

- [Installation](https://docs.frappe.io/framework/user/en/installation)
- [Install and Setup Bench](https://docs.frappe.io/framework/user/en/tutorial/install-and-setup-bench)
- [Create a Site](https://docs.frappe.io/framework/user/en/tutorial/create-a-site)
- [Create an App](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [Create a DocType / Developer Mode](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Frappe v16.32.0 release](https://github.com/frappe/frappe/releases/tag/v16.32.0)

Следующая глава: [**01. Bench → Site → App → Module → DocType → Document**](01_FOUNDATIONS.md).
