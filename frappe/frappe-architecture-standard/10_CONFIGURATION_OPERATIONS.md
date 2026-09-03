# 10. Конфигурация и эксплуатация Site

У Frappe-приложения есть состояние, которое не сводится к Python-коду и `DocType` в Git. Реальный `Site` состоит из установленного App, базы данных, файлов, runtime-конфигурации и работающих процессов Framework.

Поэтому здесь рассматриваются четыре границы:

```text
что принадлежит App
что принадлежит конкретному Site
что принадлежит окружению
что является пользовательскими данными
```

Механизмы расширения `DocType`, `fixtures` и `Export Customizations` подробно разобраны в [главе 08](08_EXTENSION_CUSTOMIZATION.md). Миграции и доставка этих изменений — в [главе 11](11_DEPLOYMENT_TESTING.md).

---

## 1. App и Site хранят разное состояние

**[ДОКУМЕНТАЦИЯ FRAPPE]** `App` — Python package, который устанавливается на `Site`. Каждый Site имеет собственную базу данных и конфигурацию.

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

## 2. Site Config — runtime-конфигурация, а не предметный справочник

**[ДОКУМЕНТАЦИЯ FRAPPE]** `site_config.json` хранит параметры конкретного Site. `common_site_config.json` позволяет задавать конфигурацию, общую для Sites одного Bench.

Источники:

- https://docs.frappe.io/framework/user/en/basics/site_config
- https://docs.frappe.io/framework/user/en/basics/sites

Типичные параметры этого уровня:

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

Это другой класс данных, чем управляемые бизнес-настройки приложения, например:

```text
My App Settings
  default_warehouse
  approval_limit
  notification_days
```

которые естественно выражаются через `Single DocType` или другую модель данных.

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Site Config отвечает за запуск и окружение Site; бизнес-конфигурация — за поведение предметной системы.

---

## 3. Секреты принадлежат окружению

Site Config может содержать database credentials и `encryption_key`.

**[ДОКУМЕНТАЦИЯ FRAPPE]** `encryption_key` используется для шифрования значений Password и нужен после восстановления Site для чтения уже сохранённых зашифрованных данных.

Источник:

- https://docs.frappe.io/framework/user/en/basics/site_config

Отсюда граница:

```text
структура настройки
→ может принадлежать App

секрет конкретного окружения
→ принадлежит Site / deployment environment
```

Пароли внешних API, database credentials и encryption keys не становятся частью открытого репозитория только потому, что приложению они нужны для работы.

---

## 4. Зависимости App должны быть видимы из поставляемого приложения

**[ДОКУМЕНТАЦИЯ FRAPPE]** Если App строится поверх другого App, hook `required_apps` позволяет указать обязательную зависимость.

Пример:

```python
required_apps = ["erpnext"]
```

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks#required-apps

Python-зависимости package описываются в `pyproject.toml`.

Источник:

- https://docs.frappe.io/framework/user/en/tutorial/create-an-app

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Обязательная зависимость не должна существовать только как ручной шаг в инструкции. Совместимость конкретных версий проверяется при разработке и поставке App.

---

## 5. Static assets имеют штатный путь поставки

**[ДОКУМЕНТАЦИЯ FRAPPE]** App хранит статические файлы в `public`. В Bench они доступны через `sites/assets/[appname]`, а bundled assets формируются в `assets/[appname]/dist`.

Источник:

- https://docs.frappe.io/framework/user/en/basics/static-assets

```text
App source
  public/
      ↓
Bench assets/build
      ↓
/assets/<app>/...
```

Если пользовательский интерфейс является частью App, его исходные assets и build относятся к поставке приложения так же, как Python-код.

Связанный раздел: [`09_UI_REPORTING.md`](09_UI_REPORTING.md).

---

## 6. Переводы принадлежат App

**[ДОКУМЕНТАЦИЯ FRAPPE]** Frappe имеет встроенную систему переводов. Строки metadata и помеченные строки кода могут поставляться в `translations/<lang>.csv` приложения.

Источники:

- https://docs.frappe.io/framework/user/en/translations
- https://docs.frappe.io/framework/user/en/guides/basics/translations

Перевод относится к представлению. Бизнес-идентификаторы, `fieldname` и API contracts не нужно переводить вместе с интерфейсом.

---

## 7. Logging уже является частью платформы

**[ДОКУМЕНТАЦИЯ FRAPPE]** Frappe имеет Desk Logs и server logs. Среди штатных журналов есть `Error Log`, `Activity Log`, `Scheduled Job Log`; процессы Bench и Site также пишут серверные логи.

Источники:

- https://docs.frappe.io/framework/user/en/logging
- https://docs.frappe.io/framework/user/en/api/logging

Для обычной технической диагностики не нужен отдельный параллельный `Error Journal`, который только сохраняет traceback или факт падения background job.

Предметный audit log может быть отдельной бизнес-сущностью, если его смысл отличается от технических журналов Framework.

---

## 8. Эксплуатационная диагностика и performance-профилирование — разные задачи

Для состояния фоновых задач и общего здоровья Site Frappe предоставляет `RQ Job`, worker/server logs и `System Health Report`.

Для анализа медленных запросов и SQL используется `Recorder` и profiling — это уже подробно разобрано в [главе 05](05_DATA_ACCESS_PERFORMANCE.md), поэтому здесь этот материал не повторяется.

Практическая граница:

```text
почему медленно?
→ глава 05: Recorder / profiling / SQL

что произошло с background job?
→ RQ Job / worker logs

работают ли основные сервисы Site?
→ System Health Report
```

Внешняя observability-платформа становится отдельной ответственностью, когда нужно объединять несколько систем, хранить централизованные метрики и строить инфраструктурные alerts.

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

Database dump без файлов теряет вложения. Восстановленные Password fields без исходного `encryption_key` могут стать нечитаемыми.

**[АРХИТЕКТУРНЫЙ ВЫВОД]** Backup считается рабочим после проверки восстановления, а не только после появления `.sql.gz`.

---

## 10. App update и Site restore — разные операции

```text
обновить App
→ новый code + migrate

восстановить Site
→ вернуть database / files / config
```

Попытка откатить релиз случайным восстановлением базы и попытка вернуть потерянные пользовательские данные через `git checkout` смешивают разные слои системы.

Версия App и версия данных Site связаны миграциями, но не являются одним и тем же состоянием.

---

## 11. Карта ответственности

| Вопрос | Естественный владелец |
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
| технические ошибки | Frappe logging / server logs |
| состояние background jobs | RQ Job / worker logs |
| резервная копия Site | database + files + необходимая config |

---

## 12. Главная граница

```text
исходный код App
≠ runtime-конфигурация Site
≠ пользовательские данные
≠ резервная копия
```

Frappe уже задаёт механизмы для каждого слоя. Архитектурная задача — положить каждую ответственность в подходящее место и не строить параллельную систему конфигурации, логирования или восстановления без отдельной причины.