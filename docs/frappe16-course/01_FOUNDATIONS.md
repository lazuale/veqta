# 01. Основа Frappe: Bench → Site → App → Module → DocType → Document

Это первая глава курса. Здесь не создаём бизнес-логику и не пишем код. Цель — понять, **из каких уровней состоит Frappe и что именно мы называем приложением**.

Проверено: **2026-08-30**.

## 1. Что такое Frappe Framework

Frappe Framework — full-stack web framework на Python и JavaScript для приложений, работающих с данными.

Его ключевая особенность — **metadata-driven architecture**: описание сущностей и их полей используется Framework не только для хранения данных, но и для построения значительной части интерфейса и поведения системы.

Практическое следствие:

```text
описали сущность
        ↓
Frappe уже знает значительную часть того,
как её хранить, показывать и обслуживать
```

Поэтому Frappe нельзя воспринимать ни как обычную Python-библиотеку, ни как готовую ERP-систему.

---

## 2. Frappe Framework не равен ERPNext

Нужно сразу разделить платформу и приложения:

```text
Frappe Framework
      │
      ├── ERPNext
      ├── Frappe CRM
      ├── Helpdesk
      ├── HRMS
      └── собственные Apps
```

Framework предоставляет техническую платформу. Отдельные Apps добавляют конкретные предметные модели и пользовательские сценарии.

Если определённая сущность или экран есть в ERPNext, CRM или другом приложении, это ещё не означает, что они входят в чистый Frappe Framework.

---

## 3. Главная иерархия

Для старта достаточно держать в голове такую схему:

```text
Bench
└── Site
    └── App
        └── Module
            └── DocType
                └── Document
```

Каждый уровень отвечает за разную часть системы.

---

## 4. Bench

Слово `bench` во Frappe используется в двух близких смыслах:

1. **Bench CLI** — командный инструмент управления Frappe-окружением.
2. **Bench directory** — каталог окружения, содержащий Apps, Sites, config и logs.

Упрощённо:

```text
frappe-bench/
├── apps/
├── sites/
├── config/
├── logs/
└── ...
```

Через Bench выполняются операции вроде:

```text
создать Site
получить App
создать App
установить App
выполнить migrate
запустить dev-среду
сделать backup
управлять процессами
```

### Что важно новичку

На старте не нужно заучивать весь Bench CLI.

Достаточно понимать:

> **Bench — уровень окружения и управления им.**

Предметные сущности приложения находятся ниже.

---

## 5. Site

`Site` — конкретный экземпляр Frappe-системы со своими данными и настройками.

Например:

```text
example.localhost
```

или:

```text
dev.example.internal
```

Один Bench может содержать несколько Sites:

```text
frappe-bench
├── dev.localhost
├── test.localhost
└── demo.localhost
```

Они могут использовать один и тот же код Apps, но иметь разные данные.

### Пример

```text
training_app
     │
     ├── установлен на dev.localhost
     └── установлен на test.localhost
```

Код приложения одинаковый. Базы, пользователи и записи сайтов разные.

### Что относится к конкретному Site

Концептуально:

```text
данные Documents
Users
site-specific settings
Customizations
Files
установленные Apps
site config
```

### Важный вывод

Site — **экземпляр системы**, а не исходный код приложения.

Если приложение должно воспроизводиться на другом Site, его стабильное состояние должно находиться в App или в штатно переносимой конфигурации, а не зависеть исключительно от ручных изменений одного Site.

---

## 6. App

`App` — устанавливаемый пакет функциональности Frappe.

Примеры:

```text
frappe
erpnext
helpdesk
training_app
```

Сам Framework поставляется как приложение `frappe`.

Собственный App создаётся Bench CLI и затем устанавливается на нужный Site.

Концептуально:

```text
Site
├── frappe
└── training_app
```

### Зачем нужен App

App является естественным местом для функциональности, которая должна:

```text
храниться в Git
переезжать между Sites
тестироваться
обновляться
иметь версии
воспроизводиться после установки
```

### App не обязан быть большим

Собственный App может состоять всего из нескольких DocTypes и небольшого количества кода, используя остальную инфраструктуру Framework.

Поэтому не следует считать, что «создать App» означает «написать второй Framework».

---

## 7. Module

Module — логическая группировка объектов внутри App.

Например:

```text
Training App
├── Operations
├── Directory
└── Settings
```

Module помогает организовать:

```text
DocTypes
Reports
Pages
код
metadata
```

Сам по себе Module обычно не является бизнес-сущностью и не хранит пользовательские записи.

---

## 8. DocType

`DocType` — центральный building block Frappe.

Допустим, нужно хранить сущность:

```text
Request
```

Описываем DocType:

```text
Request
├── Subject
├── Description
├── Status
└── Due Date
```

Frappe использует это описание как metadata модели.

Обычный DocType определяет, среди прочего:

```text
поля
типы данных
layout формы
naming
permissions
связи
часть поведения
```

Для обычного DocType Framework создаёт соответствующее хранение в базе данных и предоставляет Document API/ORM для работы с записями.

Главное:

```text
DocType
≠ просто SQL-таблица
```

Это описание **типа документа и значительной части того, как Framework с ним работает**.

---

## 9. Document

Если DocType — тип сущности, то Document — одна конкретная запись этого типа.

Например:

```text
DocType: Request

Documents:
REQ-0001
REQ-0002
REQ-0003
```

Упрощённая аналогия:

```text
DocType ≈ model + schema metadata + UI metadata
Document ≈ один объект / одна запись
```

Но Document нельзя сводить только к строке таблицы.

Вокруг него работают механизмы Frappe:

```text
permissions
validation
lifecycle
comments
attachments
versions
workflow
REST API
printing
и другие
```

---

## 10. Почему эта иерархия важна

Типичная ошибка новичка — смешивать уровни.

Например:

```text
"Нужно новое поле"
```

не означает:

```text
"нужно новое App"
```

А:

```text
"нужен отдельный тестовый экземпляр"
```

не означает:

```text
"нужно копировать исходный код приложения"
```

Правильная карта:

| Задача | Уровень |
|---|---|
| управлять окружением | Bench |
| отдельный экземпляр с собственными данными | Site |
| поставляемая функциональность | App |
| логическая группировка объектов | Module |
| тип данных / сущность | DocType |
| конкретная запись | Document |

---

## 11. Что Frappe даёт вокруг DocType

Подробно это разберём в следующих главах, но уже сейчас важно увидеть масштаб.

После определения DocType Framework может использовать одну metadata-модель для:

```text
хранения данных
Document API / ORM
Form View
List View
permissions
REST API
reports
import/export
attachments
printing
workflow и автоматизации
```

Именно поэтому изучение Frappe удобно строить вокруг DocType: большинство возможностей Framework сходятся вокруг Document-модели.

---

## 12. Что изменилось в v16 и почему старые материалы нужно проверять

Frappe v16 отличается от предыдущих веток не только внутренним кодом.

Среди заметных изменений:

- обновлены требования к зависимостям;
- изменена навигация Desk;
- введена постоянная sidebar-навигация на базе `Workspace Sidebar`;
- используется Desktop для публичных Workspaces;
- некоторые ранее встроенные возможности вынесены из `frappe` в отдельные Apps.

Поэтому материал по v14/v15 нельзя автоматически считать точной инструкцией по интерфейсу, установке или составу чистого Framework v16.

---

## 13. Контрольные вопросы

После этой главы нужно уметь без подсказки ответить:

1. Чем Bench отличается от Site?
2. Может ли один Bench содержать несколько Sites?
3. Может ли один App быть установлен на несколько Sites?
4. Что является поставляемой единицей функциональности: Site или App?
5. Для чего нужен Module?
6. Чем DocType отличается от Document?
7. Почему DocType нельзя считать просто SQL-таблицей?
8. Почему изменения только на одном Site ещё не равны воспроизводимому приложению?
9. Почему наличие функции в отдельном Frappe-приложении не доказывает наличие этой функции в чистом Framework?

Если ответы ясны — можно переходить к интерфейсу Desk и навигации v16.

## Официальные источники

- [Frappe Framework — Introduction](https://docs.frappe.io/framework/user/en/introduction)
- [Bench](https://docs.frappe.io/framework/user/en/bench)
- [Create a Site](https://docs.frappe.io/framework/user/en/tutorial/create-a-site)
- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Migrating to Version 16](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)

---

Следующая глава: [**02. Desk, Desktop, Sidebar, Workspace и навигация Frappe 16**](02_DESK_NAVIGATION.md).