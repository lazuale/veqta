# VEQTA — Prototype v0.1 on WSL2

Статус: **поддерживаемый dev-вариант prototype v0.1**.

## 1. Назначение

VEQTA prototype v0.1 можно разрабатывать локально на Windows через **WSL2**.

Для текущей задачи это предпочтительный вариант, если разработка идёт с ноутбука:

- Linux-среда для Bench/Frappe;
- Windows-браузер и редактор остаются доступными;
- dev server Frappe доступен с Windows через localhost;
- не требуется отдельный VPS только ради раннего prototype;
- не требуется Docker Desktop для самого dev-цикла.

WSL1 не является целевой средой. Используется WSL2.

## 2. Дистрибутив

Предпочтительно использовать **Ubuntu 24.04 LTS в WSL2**.

Причина: актуальная документация Frappe v16 официально указывает Ubuntu 24.04+ и Debian 13+ как поддерживаемые Linux-среды и отдельно допускает Ubuntu в WSL для Windows-пользователей.

## 3. Проверка WSL

В PowerShell:

```powershell
wsl --status
wsl -l -v
```

У выбранного дистрибутива VERSION должна быть `2`.

Если Ubuntu 24.04 ещё нет:

```powershell
wsl --install -d Ubuntu-24.04
```

После установки перезагрузить Windows, если WSL этого потребует, и завершить первичное создание Linux-пользователя.

## 4. systemd

Современный WSL поддерживает systemd. Для prototype желательно использовать его, чтобы MariaDB и Redis работали как обычные Linux services.

Проверить внутри WSL:

```bash
ps -p 1 -o comm=
systemctl status
```

Если systemd не активен, в `/etc/wsl.conf`:

```ini
[boot]
systemd=true
```

Затем из PowerShell:

```powershell
wsl --shutdown
```

и снова открыть Ubuntu.

## 5. Где хранить bench и исходники

Bench, Frappe и VEQTA хранить **в Linux filesystem WSL**, например:

```text
/home/<user>/frappe/veqta-bench
```

Не размещать bench в `/mnt/c/...`.

Причина: Linux toolchain, Python virtualenv, Node modules и большое число мелких файлов работают надёжнее и быстрее в Linux filesystem WSL.

Windows-редактор можно подключать к этой папке через WSL integration.

## 6. Установка Frappe

После подготовки WSL использовать основной runbook:

`docs/PROTOTYPE_RUNBOOK.md`

Системные пакеты, MariaDB, Redis, Node, Python, Bench и Frappe устанавливаются **внутри Ubuntu WSL**, не в Windows.

Для prototype отдельный Linux-пользователь `frappe` не обязателен, если текущий WSL-пользователь является обычным непривилегированным пользователем. Bench нельзя вести от root.

## 7. Доступ из Windows

После запуска:

```bash
cd ~/frappe/veqta-bench
bench start
```

Frappe обычно доступен в Windows-браузере по адресу:

```text
http://localhost:8000
```

или:

```text
http://127.0.0.1:8000
```

Отдельный SSH tunnel для локального WSL-стенда не нужен.

## 8. Что не делаем

Для prototype v0.1 на WSL2 не требуется:

- Docker Desktop;
- отдельная VM;
- отдельный VPS;
- nginx;
- production supervisor/system configuration;
- HTTPS;
- публикация dev server в локальную сеть или интернет.

Это локальная среда разработки и проверки Frappe primitives.

## 9. Ограничение

WSL2 является dev-средой VEQTA, а не автоматически принятой production-платформой.

Production deployment будет рассматриваться отдельно после подтверждения модели prototype v0.1.
