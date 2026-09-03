# S00. Подготовить отдельный App и Site

Первый практикум уже показал, как устроены Bench, App и Site. Здесь мы не повторяем установку Frappe с нуля, а создаём отдельную учебную границу для практикума по жизненному циклу Document.

Новый App:

```text
purchase_lifecycle_training
```

Новый dev Site:

```text
purchase-lifecycle.localhost
```

## 1. Проверить исходную среду

Перейдите в Bench первого практикума:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте версию:

```bash
bench version
```

Практикум рассчитан на Frappe v16. Версионно-зависимые решения этого маршрута проверены на v16.33.0.

Проверьте Apps, доступные Bench:

```bash
ls -1 apps
```

Наличие `rental_training` в `apps/` не означает, что он будет установлен на новом Site.

```text
App доступен Bench
≠
App установлен на Site
```

Эту границу мы используем намеренно: второй практикум не зависит от модели Rental.

## 2. Создать новый App

Из корня Bench:

```bash
bench new-app purchase_lifecycle_training
```

Для учебного App используйте:

```text
App Title       : Purchase Lifecycle Training
App Description : Учебное приложение для практикума по жизненному циклу Document
App Publisher   : ваше имя или организация
App Email       : ваш email
App License     : MIT
```

После создания должен существовать каталог:

```text
apps/purchase_lifecycle_training
```

Проверьте:

```bash
test -d apps/purchase_lifecycle_training && echo 'App: OK'
```

## 3. Создать отдельный Site

```bash
bench new-site purchase-lifecycle.localhost
```

Введите пароль MariaDB root, если Bench его запрашивает, и задайте пароль `Administrator` для нового Site.

После создания проверьте, что Site существует:

```bash
ls -1 sites
```

## 4. Установить только новый учебный App

```bash
bench --site purchase-lifecycle.localhost install-app purchase_lifecycle_training
```

Проверьте:

```bash
bench --site purchase-lifecycle.localhost list-apps -f text
```

Ожидается:

```text
frappe
purchase_lifecycle_training
```

`rental_training` на этот Site устанавливать не нужно.

## 5. Включить developer mode только на dev Site

Для создания Standard metadata через Desk:

```bash
bench --site purchase-lifecycle.localhost set-config developer_mode 1
bench --site purchase-lifecycle.localhost clear-cache
```

Проверьте эффективную конфигурацию:

```bash
bench --site purchase-lifecycle.localhost show-config
```

Должно присутствовать:

```text
developer_mode  1
```

Это настройка конкретного Site, а не свойство всего Bench.

## 6. Запустить Desk

Если Bench ещё не запущен:

```bash
bench start
```

Откройте:

```text
http://purchase-lifecycle.localhost:8000/app
```

Войдите как `Administrator`.

## 7. Проверить границу исходников App

Новый App уже является отдельным Git-репозиторием внутри Bench. Проверьте:

```bash
git -C apps/purchase_lifecycle_training status --short
```

На следующих этапах Standard DocType и его код будут появляться именно здесь.

## Результат

После S00 должно быть одновременно верно:

```text
Bench        = существующая совместимая среда
App          = purchase_lifecycle_training
Dev Site     = purchase-lifecycle.localhost
Module       = Purchase Lifecycle Training
Developer Mode на dev Site = 1
rental_training на новом Site = не установлен
```

Следующий этап: [`S01_PURCHASE_REQUEST.md`](S01_PURCHASE_REQUEST.md).
