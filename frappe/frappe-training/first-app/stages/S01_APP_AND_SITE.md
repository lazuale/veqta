# S01. Создать учебный App и установить его на Site

S00 дал нам чистый Frappe Site:

```text
Bench
├── apps/
│   └── frappe/
└── sites/
    └── rental.localhost/
```

На S01 появляется **первая часть, принадлежащая нам** — Frappe App `rental_training`.

На этом этапе мы ещё не создаём `Equipment`, `Customer`, `Rental`, роли, Workspace или Scripts.

Цель S01 — руками увидеть границы:

```text
Bench ≠ Site ≠ App ≠ Module
```

Связанные документы:

- [`S00_ENVIRONMENT.md`](S00_ENVIRONMENT.md) — обязательное входное состояние;
- [`../APPLICATION_MODEL.md`](../APPLICATION_MODEL.md) — модель учебного приложения;
- [`../ROADMAP.md`](../ROADMAP.md) — место этапа в практикуме.

---

# 1. Входная проверка

Откройте терминал Debian:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте, что находитесь именно внутри Bench:

```bash
bench find .
```

Проверьте Site:

```bash
bench --site rental.localhost list-apps -f text
```

Перед S01 ожидается ровно:

```text
frappe
```

Если `rental_training` уже существует или на Site установлено другое прикладное App, сначала разберитесь, откуда оно взялось. S01 должен начинаться от результата S00.

---

# 2. Что такое App в этом практикуме

Frappe App — это Python-пакет, использующий Framework. Apps живут в каталоге `apps` Bench и должны быть установлены на конкретный Site, прежде чем их модели станут частью этого Site.

Официальная документация:

- https://docs.frappe.io/framework/user/en/basics/apps
- https://docs.frappe.io/framework/user/en/tutorial/create-an-app

В нашей модели:

```text
frappe
  = Framework App

rental_training
  = наш учебный App
```

Это два разных Apps в одном Bench.

---

# 3. Создать `rental_training`

Убедитесь, что вы в корне Bench:

```bash
cd ~/frappe/rental-training-bench
bench find .
```

Запустите штатное создание App:

```bash
bench new-app rental_training
```

Bench задаст несколько вопросов.

Используйте:

```text
App Title       : Rental Training
App Description : Учебное приложение для практикума Frappe Framework
App Publisher   : ваше имя или название организации
App Email       : ваш email
App License     : MIT
```

Для остальных необязательных вопросов можно принять значения по умолчанию, если Bench их показывает.

### Важно

Не копируйте из инструкции чужое имя или email. Эти значения являются метаданными вашего App.

Не используйте:

```text
--no-git
```

В обычном учебном сценарии нам нужен собственный Git-репозиторий App, потому что далее мы будем проверять, какие изменения действительно принадлежат устанавливаемому приложению.

---

# 4. Проверить, что создал Bench

После завершения:

```bash
ls -la apps/rental_training
```

Проверьте Git:

```bash
git -C apps/rental_training status
```

Команда должна работать внутри самостоятельного Git-репозитория.

Посмотрите верхний уровень:

```bash
find apps/rental_training -maxdepth 2 -type f | sort
```

Точный список вспомогательных файлов может меняться между версиями `bench new-app`. Для архитектуры нам важны следующие элементы:

```text
apps/rental_training/
├── pyproject.toml
├── README.md
└── rental_training/
    ├── hooks.py
    ├── modules.txt
    ├── patches.txt
    └── ...
```

Не нужно сейчас подробно изучать каждый файл. Достаточно понять их владельца и назначение.

---

# 5. Проверить Module

Откройте список модулей App:

```bash
cat apps/rental_training/rental_training/modules.txt
```

Ожидается Module, созданный по умолчанию для App:

```text
Rental Training
```

Если вы ввели `App Title = Rental Training`, именно это имя должно использоваться дальше в практикуме.

## Что означает Module

Module — штатная группировка объектов **внутри App**.

Позже:

```text
rental_training [App]
└── Rental Training [Module]
    ├── Equipment
    ├── Customer
    ├── Rental
    └── Rental Item
```

Но сейчас этих DocTypes ещё нет.

### Чего Module не означает

`Rental Training` Module:

- не является отдельным Python-пакетом верхнего уровня;
- не устанавливается на Site отдельно от App;
- не является вторым приложением;
- не обязан автоматически становиться отдельной предметной областью.

---

# 6. Разобрать минимальную структуру App

Ученик должен знать назначение только тех файлов, которые уже имеют архитектурный смысл.

## `pyproject.toml`

Описание Python-пакета и его зависимостей.

Не добавляйте сторонние библиотеки «на будущее».

## `rental_training/hooks.py`

Штатные точки конфигурации и расширения Frappe App.

На S01 мы ничего туда не добавляем просто ради знакомства с hooks.

## `rental_training/modules.txt`

Перечень Modules, принадлежащих App.

На старте у нас один:

```text
Rental Training
```

## `rental_training/patches.txt`

Список одноразовых patches для миграций данных.

На S01 patches не нужны.

### Главный вывод

Файлы существуют не потому, что ученик обязан немедленно использовать каждую возможность, созданную `bench new-app`.

Они показывают предусмотренные Frappe места для ответственностей, которые могут появиться позже.

---

# 7. Что изменилось в Bench

До `bench new-app`:

```text
apps/
└── frappe/
```

После:

```text
apps/
├── frappe/
└── rental_training/
```

Проверьте:

```bash
ls -1 apps
```

Но наличие App в Bench **ещё не означает**, что он установлен на `rental.localhost`.

Это принципиально.

---

# 8. До установки проверить Site ещё раз

```bash
bench --site rental.localhost list-apps -f text
```

На этом промежуточном шаге ожидается всё ещё:

```text
frappe
```

То есть:

```text
App доступен Bench
≠
App установлен на Site
```

Это одна из главных контрольных точек S01.

---

# 9. Установить App на Site

Теперь выполняем штатную установку:

```bash
bench --site rental.localhost install-app rental_training
```

Frappe применит состояние App к базе данного Site.

Проверьте:

```bash
bench --site rental.localhost list-apps -f text
```

Теперь ожидается:

```text
frappe
rental_training
```

Официальная документация прямо разделяет создание или получение App и его установку на Site:

- https://docs.frappe.io/framework/user/en/basics/apps
- https://docs.frappe.io/framework/user/en/bench/reference/list-apps

---

# 10. Проверить итоговую структуру

Теперь архитектурная картина выглядит так:

```text
~/frappe/rental-training-bench/
│
├── apps/
│   ├── frappe/
│   └── rental_training/
│       └── rental_training/
│           ├── hooks.py
│           ├── modules.txt
│           └── ...
│
└── sites/
    └── rental.localhost/
```

И логически:

```text
Bench: rental-training-bench
│
├── доступные Apps
│   ├── frappe
│   └── rental_training
│
└── Site: rental.localhost
    ├── установлен frappe
    └── установлен rental_training
```

Внутри `rental_training`:

```text
Module: Rental Training
```

---

# 11. Открыть Desk и убедиться, что пустой App — это нормально

Если `bench start` не запущен, откройте отдельный терминал:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте:

```text
http://rental.localhost:8000/app
```

После установки `rental_training` не ожидайте готовой системы проката.

Мы создали **границу приложения**, но ещё не создали предметную модель.

Это правильное состояние:

```text
App есть
Module есть
DocTypes предметной области пока нет
```

Не пытайтесь «исправить пустоту» созданием случайного Workspace или Custom HTML.

---

# 12. Проверить границу Git-репозитория App

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git status
git log --oneline -5
```

Убедитесь, что это Git-репозиторий именно учебного App.

Вернитесь в Bench:

```bash
cd ~/frappe/rental-training-bench
```

## Зачем App имеет собственный Git

Финальная проверка практикума требует:

```text
чистый Site
+ App из Git
+ install-app
+ migrate
= воспроизводимое состояние
```

Значит предметная модель не может жить только в базе текущего `rental.localhost`.

### Пока не нужен удалённый репозиторий

На S01 достаточно локального Git-репозитория App.

Создание отдельного GitHub-репозитория и remote — вопрос хранения исходников, а не условие понимания Frappe App. Это можно сделать отдельно, когда потребуется переносить App между машинами.

---

# 13. Контрольная команда S01

Выполните:

```bash
cd ~/frappe/rental-training-bench

printf '\n=== BENCH ===\n'
bench find .

printf '\n=== AVAILABLE APP DIRECTORIES ===\n'
ls -1 apps

printf '\n=== SITE APPS ===\n'
bench --site rental.localhost list-apps -f text

printf '\n=== MODULES ===\n'
cat apps/rental_training/rental_training/modules.txt

printf '\n=== APP GIT ===\n'
git -C apps/rental_training status --short --branch
```

Ожидаемый смысл:

```text
apps/
  frappe
  rental_training

Site rental.localhost:
  frappe
  rental_training

Module:
  Rental Training

rental_training:
  Git-репозиторий работает
```

---

# 14. Проверка перед S02

Переход к созданию `Equipment` возможен, если одновременно верно:

```text
[ ] App называется rental_training
[ ] App находится в apps/rental_training
[ ] App имеет собственный Git-репозиторий
[ ] внутри App существует Module Rental Training
[ ] rental_training установлен на rental.localhost
[ ] list-apps показывает frappe + rental_training
[ ] ERPNext не установлен
[ ] предметных DocType ещё нет
[ ] ученик различает Bench, Site, App и Module
```

---

# 15. Когда не переходить к S02

Сначала исправьте проблему, если:

- `rental_training` создан вне Bench и Bench его не видит;
- App есть в `apps/`, но не установлен на Site;
- Module воспринимается как отдельное App;
- предметные DocTypes созданы как случайные локальные настройки Site;
- для «красоты» уже добавлен Workspace, frontend или отдельный UI;
- ERPNext установлен только ради готовых сущностей;
- исходники предметного App начали складывать в `apps/frappe`;
- вы редактируете исходники Frappe вместо собственного App.

---

# 16. Типовые ошибки новичка

## «`bench new-app` уже создал папку. Зачем `install-app`?»

Потому что это две разные ответственности:

```text
bench new-app
→ делает App доступным в Bench и создаёт его исходники

bench --site ... install-app
→ устанавливает App в конкретный Site
```

Один Bench может содержать несколько Sites, и набор установленных Apps у них может отличаться.

## «Почему не создаём Module отдельной командой?»

`bench new-app` уже создаёт Module по умолчанию. Для текущей модели нам достаточно одного Module `Rental Training`.

Новый Module появится только если возникнет реальная организационная причина.

## «Может сразу создать Equipment Type, Rental Status и Settings?»

Нет. Для текущих требований они не нужны.

## «Почему не пишем hooks.py?»

Потому что пока нет новой ответственности, для которой нужен hook.

## «Почему не создаём роли сейчас?»

Права имеют смысл относительно уже существующих DocTypes и операций. Они появятся после предметной модели на соответствующем этапе практикума.

---

# 17. Что ученик должен объяснить без шпаргалки

После S01 задайте себе четыре вопроса.

### Что такое Bench?

Среда, содержащая Apps, Sites и процессы разработки.

### Что такое Site?

Конкретный экземпляр Frappe со своей БД и конфигурацией.

### Что такое App?

Устанавливаемый Python-пакет с исходным кодом и метаданными, использующий Frappe.

### Что такое Module?

Штатная группировка объектов внутри App.

Если ответы превращаются в схему:

```text
Bench
├── Apps
│   ├── frappe
│   └── rental_training
└── Sites
    └── rental.localhost
         └── установлены: frappe + rental_training

rental_training App
└── Rental Training Module
```

этап выполнен правильно.

---

# 18. Следующий этап

Теперь впервые можно создавать предметную модель, потому что у неё появился правильный владелец:

```text
Equipment
→ Standard DocType
→ Module: Rental Training
→ App: rental_training
```

Следующий этап — **S02: Equipment как самостоятельный Document**.