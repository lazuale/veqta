# 14. Конфигурация и эксплуатация Site

У Frappe-приложения есть состояние, которое не сводится к Python-коду и `DocType` в Git. Реальный Site состоит из установленного App, базы данных, файлов, runtime-конфигурации и работающих процессов Framework.

Поэтому важно различать:

```text
что принадлежит App
что принадлежит конкретному Site
что принадлежит окружению
что является пользовательскими данными
```

---

## 1. App и Site хранят разное состояние

**[ДОКУМЕНТАЦИЯ FRAPPE]** `App` — Python package, который устанавливается на `Site`. Каждый Site имеет собственную базу данных и собственную конфигурацию.

Источники:

- https://docs.frappe.io/framework/user/en/basics/apps
- https://docs.frappe.io/framework/user/en/basics/sites

Типичное разделение:

```text
App в Git
├── Python / JavaScript
├── Standard DocType metadata
├── hooks.py
├── patches.txt
├── fixtures
├── public assets
└── translations

Site
├── database
├── site_config.json
├── public files
├── private files
├── installed apps
└── пользовательские Documents
```

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Репозиторий App не является резервной копией Site, а резервная копия Site не заменяет исходный код App.

---

## 2. Site Config — конфигурация окружения, а не предметный справочник

**[ДОКУМЕНТАЦИЯ FRAPPE]** `site_config.json` хранит параметры конкретного Site. `common_site_config.json` позволяет задавать конфигурацию, общую для Sites одного Bench.

Источники:

- https://docs.frappe.io/framework/user/en/basics/site_config
- https://docs.frappe.io/framework/user/en/basics/sites

В Site Config находятся параметры уровня runtime и инфраструктуры, например:

```text
db_type
db_name
db_password
host_name
developer_mode
disable_scheduler
allow_cors
encryption_key
```

Это другой тип данных, чем, например:

```text
My App Settings
  default_warehouse
  approval_limit
  notification_days
```

которые могут естественно жить в `Single DocType` и управляться пользователем через Desk.

**[АРХИТЕКТУРНЫЙ ВЫВОД]** В Site Config стоит хранить то, что относится к запуску и окружению Site. Управляемая бизнес-конфигурация приложения обычно лучше выражается через модель данных Frappe.

---

## 3. Секреты не являются fixtures

Site Config может содержать чувствительные значения, включая database credentials и `encryption_key`.

**[ДОКУМЕНТАЦИЯ FRAPPE]** `encryption_key` используется для шифрования значений Password; при восстановлении Site этот ключ также нужен для чтения уже сохранённых зашифрованных данных.

Источник:

- https://docs.frappe.io/framework/user/en/basics/site_config

Из этого следует простое разделение:

```text
структура настройки
→ может принадлежать App

секрет конкретного окружения
→ принадлежит Site / deployment environment
```

Пароли внешних API, database credentials и encryption keys не становятся частью открытого App только потому, что приложению они нужны для работы.

---

## 4. Зависимость от другого App выражается средствами Frappe

**[ДОКУМЕНТАЦИЯ FRAPPE]** Если App строится поверх другого App, hook `required_apps` позволяет указать обязательную зависимость.

Пример:

```python
required_apps = ["erpnext"]
```

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks#required-apps

Python-зависимости самого package описываются в `pyproject.toml` приложения.

Источник:

- https://docs.frappe.io/framework/user/en/tutorial/create-an-app

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Зависимость, без которой App не имеет смысла, должна быть видна из поставляемого приложения, а не существовать только в инструкции «сначала руками установите ещё вот это».

Совместимость версий при этом остаётся отдельной ответственностью разработчика продукта.

---

## 5. Static assets имеют штатный путь поставки

**[ДОКУМЕНТАЦИЯ FRAPPE]** App хранит собственные статические файлы в `public`. В Bench они доступны через `sites/assets/[appname]`, а bundled assets формируются в `assets/[appname]/dist`.

Источник:

- https://docs.frappe.io/framework/user/en/basics/static-assets

Это означает, что CSS, JavaScript и изображения App не нужно раскладывать вручную по директории веб-сервера.

```text
App source
  public/
      ↓
Bench assets/build
      ↓
/assets/<app>/...
```

Если пользовательский интерфейс является частью App, его исходные assets и процесс build относятся к поставке приложения так же, как Python-код.

Связанный раздел: [`08_UI_REPORTING.md`](08_UI_REPORTING.md).

---

## 6. Переводы тоже принадлежат App

**[ДОКУМЕНТАЦИЯ FRAPPE]** Frappe имеет встроенную систему переводов. Строки из metadata и помеченные строки кода извлекаются и могут поставляться в `translations/<lang>.csv` приложения.

Источники:

- https://docs.frappe.io/framework/user/en/translations
- https://docs.frappe.io/framework/user/en/guides/basics/translations

Для приложения с несколькими языками перевод не является копией `DocType` или отдельной веткой продукта. Это штатный слой представления поверх одной модели.

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Бизнес-идентификаторы, fieldnames и API contracts не нужно переводить вместе с интерфейсом. Перевод относится к пользовательскому представлению и текстам.

---

## 7. Logging уже является частью платформы

**[ДОКУМЕНТАЦИЯ FRAPPE]** Frappe имеет Desk Logs и server logs. Среди штатных журналов есть `Error Log`, `Activity Log`, `Scheduled Job Log`; серверные процессы также пишут логи Bench и Site.

Источник:

- https://docs.frappe.io/framework/user/en/logging

Для собственного приложения доступен стандартный logging API.

Источник:

- https://docs.frappe.io/framework/user/en/api/logging

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Для обычной диагностики App не нужен собственный параллельный «журнал ошибок» только ради сохранения traceback или факта падения background job. Сначала нужно проверить штатные журналы и logger Framework.

Предметный audit log при этом может быть отдельной бизнес-сущностью, если его смысл отличается от технического журнала Frappe.

---

## 8. Наблюдаемость начинается со штатных инструментов

**[ДОКУМЕНТАЦИЯ FRAPPE]** Framework предоставляет:

- `Recorder` для анализа requests/jobs и SQL;
- `Monitor` для метаданных запросов и задач;
- `RQ Job` для состояния background jobs;
- `System Health Report` для общей проверки сервисов, database, cache, scheduler, email и storage.

Источник:

- https://docs.frappe.io/framework/user/en/profiling

Эти инструменты не заменяют внешний monitoring в крупной инфраструктуре, но задают первую точку диагностики самого Frappe.

```text
непонятно, почему медленно
→ Recorder

непонятно, что происходит с jobs
→ RQ Job / worker logs

нужно проверить состояние Site
→ System Health Report
```

Внешняя observability-платформа оправдана, когда нужно объединять несколько систем, хранить метрики централизованно, строить alerts или выполнять инфраструктурный мониторинг за пределами одного Bench.

---

## 9. Backup Site состоит не только из SQL

**[ДОКУМЕНТАЦИЯ FRAPPE]** `bench backup` создаёт database backup и может включать public/private files. `bench restore` умеет восстанавливать database и переданные архивы файлов.

Источники:

- https://docs.frappe.io/framework/user/en/bench/reference/backup
- https://docs.frappe.io/framework/user/en/bench/reference/restore

Для полноценного восстановления нужно помнить о трёх типах состояния:

```text
database
public/private files
Site configuration / encryption material
```

Database dump без файлов теряет пользовательские вложения. Восстановленный Password field без исходного `encryption_key` может оказаться нечитаемым.

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Backup считается рабочим только после проверки восстановления. Наличие `.sql.gz` само по себе ещё не доказывает возможность вернуть Site в рабочее состояние.

---

## 10. App update и Site restore — разные операции

```text
обновить App
→ новый code + migrate

восстановить Site
→ вернуть состояние database/files/config
```

Смешивание этих задач создаёт опасные сценарии, например попытку «откатить релиз» восстановлением случайной базы или попытку восстановить потерянные пользовательские данные обычным `git checkout`.

Версия App и версия данных Site связаны миграциями, но принадлежат разным слоям системы.

---

## 11. Эксплуатационная карта ответственности

| Вопрос | Где искать естественного владельца |
|---|---|
| обязательный код и metadata продукта | App / Git |
| бизнес-настройка, которую меняет пользователь | DocType / Single DocType |
| runtime-параметр конкретного Site | `site_config.json` |
| общий параметр Sites одного Bench | `common_site_config.json` |
| секрет окружения | Site / deployment secret management |
| обязательное другое Frappe App | `required_apps` |
| Python package dependency | `pyproject.toml` |
| JS/CSS/images App | `public` + assets/build |
| перевод интерфейса | translations |
| технические ошибки и процессные логи | Frappe logging / Desk Logs / server logs |
| диагностика медленного запроса | Recorder / profiling |
| состояние background jobs | RQ Job / worker logs |
| резервная копия Site | database + files + необходимая config |

---

## 12. Главный принцип

Эксплуатационная архитектура Frappe становится проще, если не смешивать четыре разных слоя:

```text
исходный код App
≠ runtime-конфигурация Site
≠ пользовательские данные
≠ резервная копия
```

Frappe уже задаёт механизмы для каждого из этих слоёв. Задача приложения — положить каждую ответственность в подходящее место, а не строить собственную систему конфигурации, cache, логирования или восстановления раньше, чем обнаружено реальное ограничение Framework.