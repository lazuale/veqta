# Лабораторная 01. Bench → Site → App → Module → DocType → Document

## Что должно быть готово

Пройдена глава 0. Запущен стенд `frappe16-course-bench`, Site `learn.localhost`, установлены Apps `frappe` и `training`.

## Что увидим

Не определения на схеме, а реальные объекты на диске и в Site.

## Сделай руками

В Debian:

```bash
cd ~/frappe/frappe16-course-bench
pwd
ls -la
ls -la apps
ls -la sites
bench --site learn.localhost list-apps
```

Затем:

```bash
find apps/training -maxdepth 2 -type d | sort
```

Открой Desk: `http://learn.localhost:8000`.

Через Awesome Bar найди `DocType`, затем открой любой системный DocType, например `User`.

## Что должно получиться

Ты физически видишь:

```text
Bench        → каталог frappe16-course-bench
Site         → sites/learn.localhost
App          → apps/frappe и apps/training
Module       → логическая область внутри App
DocType      → описание типа данных
Document     → конкретная запись DocType
```

## Эксперимент

Выполни:

```bash
bench --site learn.localhost list-apps
bench version
```

Сравни вывод. Первый показывает Apps конкретного Site, второй — версии Apps в Bench.

## Намеренная ошибка

Выполни команду с несуществующим Site:

```bash
bench --site no-such-site.localhost list-apps
```

Прочитай ошибку и объясни, почему наличие Bench не означает наличие любого Site.

## Проверка себя

Ответь без подсказки:

1. Может ли один Bench содержать несколько Sites?
2. Может ли App лежать в `apps/`, но не быть установленным на конкретный Site?
3. Чем DocType отличается от Document?

## Состояние после лабораторной

Ничего не меняем. Стенд остаётся чистым для следующей главы.
