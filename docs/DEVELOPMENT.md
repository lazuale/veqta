# VEQTA — разработка

## Frappe baseline

VEQTA разрабатывается на актуальной stable-линии Frappe v16. На 2026-08-29 проверена версия `v16.32.0`.

Перед новым стендом, обновлением Framework или решением, зависящим от его поведения, актуальная версия проверяется повторно.

Порядок источников:

1. официальная документация Frappe;
2. исходники `frappe/frappe` используемой версии;
3. release / migration notes;
4. официальные issues и PR при необходимости.

Код из `develop` не считается доступным, пока он не вошёл в используемую stable-линию.

## Frappe first

Перед собственным кодом проверяем, решается ли задача штатным Frappe. Если решается корректно — второй механизм в VEQTA не создаётся.

## Site → Git

Локальный site — среда разработки. Repository — состояние продукта.

```text
Desk / код
    ↓
файлы app или штатный экспорт конфигурации
    ↓
git diff
    ↓
commit
    ↓
push
```

Для стандартных DocType используется Developer Mode. DB-backed конфигурация переносится в app штатными fixtures, export customizations или другим официальным механизмом Frappe.

Контрольный критерий:

```text
чистый совместимый Frappe site
+ lazuale/veqta
+ install-app / migrate
= согласованное состояние VEQTA
```

Если принятую продуктовую конфигурацию приходится накликивать повторно, она ещё не зафиксирована как часть продукта.

## Git hygiene

Коммитим:

- исходники app `veqta`;
- app metadata и DocType;
- продуктовые fixtures / exported customizations;
- migrations / patches;
- тесты;
- документацию.

Не коммитим:

- весь Bench и исходники Frappe;
- локальные БД и рабочие dumps;
- `site_config.json` и секреты;
- пароли и private SSH keys;
- пользовательские данные стенда, если они не являются тестовыми fixtures.

Рабочий цикл:

```bash
cd ~/frappe/veqta-bench/apps/veqta
git status
git pull --ff-only origin main
```

После изменения:

```bash
git status
git diff
git add .
git diff --cached
git commit -m "Описание изменения"
git push origin main
```

## Лицензия

VEQTA — `AGPL-3.0-or-later`.

- полный текст хранится в корневом `LICENSE`;
- `veqta/hooks.py` должен содержать `app_license = "AGPL-3.0-or-later"`;
- дублирующий `license.txt` от boilerplate не сохраняется;
- upstream license headers не переписываются без причины.
