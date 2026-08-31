# 01. Bench → Site → App → Module → DocType → Document

После главы 0 у тебя уже есть работающий Frappe, но пока это набор имён и каталогов:

```text
~/frappe/frappe16-course-bench
learn.localhost
frappe
training
Training
```

Прежде чем создавать первый собственный DocType, нужно понять, **что из этого является окружением, что кодом, что экземпляром системы, а что данными**.

В этой главе ничего нового на стенде не создаём. Мы разбираем уже существующую лабораторию и связываем термины Frappe с реальными объектами, которые можно увидеть руками.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

После главы 0 должно существовать:

```text
Windows 11
└── WSL2 / Debian 13
    └── ~/frappe/frappe16-course-bench/
        ├── apps/
        │   ├── frappe/
        │   └── training/
        └── sites/
            └── learn.localhost/
```

На Site `learn.localhost` установлены Apps:

```text
frappe
training
```

В App `training` уже создан стандартный Module:

```text
Training
```

Собственного DocType `Request` пока нет. Он появится только в главе 4.

---

## Почему схема `Bench → Site → App` вводит в заблуждение

Эти понятия связаны, но они не вложены друг в друга одной цепочкой.

Реальная картина ближе к такой:

```text
frappe16-course-bench/
├── apps/
│   ├── frappe/        ← код Framework
│   └── training/      ← код нашего учебного App
│
└── sites/
    └── learn.localhost/
        ├── своя конфигурация
        ├── свои файлы
        └── своя база данных
```

А связь между ними выглядит так:

```text
App training
        │
        │ установлен на
        ▼
Site learn.localhost
```

Один App может использоваться несколькими Sites одного Bench. При этом каждый Site хранит собственные данные.

Поэтому лучше держать в голове не лестницу владения, а две части Bench:

```text
код Apps
+
экземпляры Sites
```

---

## Bench

`Bench` — это рабочее окружение Frappe и набор команд для управления этим окружением.

Наш Bench:

```text
~/frappe/frappe16-course-bench
```

В нём находятся, среди прочего:

```text
apps/    → код Frappe Apps
sites/   → Sites и общая конфигурация Sites
config/  → конфигурация процессов Bench
logs/    → логи
```

Команда `bench` работает с этим окружением: запускает development processes, создаёт Sites, устанавливает Apps на Site, делает backup и выполняет другие административные действия.

Пока достаточно одного правила:

> Если речь о каталоге `frappe16-course-bench` и командах `bench`, мы на уровне окружения, а не одной конкретной заявки или другого Document.

---

## Site

`Site` — отдельный экземпляр Frappe со своей базой данных, пользователями, настройками и файлами.

Наш Site:

```text
learn.localhost
```

Его каталог находится здесь:

```text
~/frappe/frappe16-course-bench/sites/learn.localhost
```

Но сами Documents Site хранятся не только в этом каталоге: основная структурированная информация находится в отдельной базе данных Site.

Один Bench может обслуживать несколько Sites. Например, технически можно иметь:

```text
learn.localhost
second.localhost
```

Оба Site могут использовать один и тот же код `training`, но их Documents будут независимы.

В этом курсе второй Site сейчас не нужен, поэтому мы его не создаём.

---

## App

`App` — пакет кода и metadata для Frappe.

В нашем Bench есть:

```text
apps/frappe
apps/training
```

`frappe` — App, в котором находится сам Framework.

`training` — наше учебное App. В главе 0 оно было создано командой `bench new-app training`, а затем установлено на `learn.localhost`.

Важно различать два факта:

```text
App находится в Bench
```

и

```text
App установлен на конкретный Site
```

Это не одно и то же.

Код App может находиться в `apps/`, но Site начнёт использовать это App только после установки на этот Site.

На нашем стенде проверяется команда:

```bash
bench --site learn.localhost list-apps
```

Она должна показывать как минимум:

```text
frappe
training
```

---

## Module

`Module` — логическая область внутри App, к которой относятся DocTypes и другие объекты приложения.

Когда в главе 0 мы создали App `training`, Frappe подготовил для него Module:

```text
Training
```

Список модулей App можно увидеть в файле:

```text
apps/training/training/modules.txt
```

В нашем случае там есть:

```text
Training
```

Module помогает организовать объекты App и их файлы. Это не отдельный Site и не отдельная база данных.

Позже, когда мы создадим DocType `Request`, он будет относиться именно к Module `Training`.

---

## DocType

`DocType` описывает тип документов: какие у них есть поля, как они называются и какое поведение Frappe должен для них предоставить.

Собственного `Request` у нас пока нет, поэтому для первого наблюдения используем системный DocType:

```text
User
```

`User` уже существует, потому что входит в Framework.

Через Desk можно открыть список `User` и увидеть его Documents.

В главе 4 мы создадим собственный DocType:

```text
Request
```

И с этого момента будем постепенно расширять именно его.

---

## Document

`Document` — одна конкретная запись DocType.

На текущем чистом стенде хороший пример:

```text
DocType: User
Document: Administrator
```

`User` отвечает на вопрос:

> какие данные и правила есть у пользователя вообще?

`Administrator` — конкретная запись этого типа.

После главы 4 аналогично будет:

```text
DocType: Request
Document: одна конкретная созданная заявка
```

Главное различие:

```text
DocType  → описание типа
Document → одна запись этого типа
```

---

## Как всё связано на нашем стенде

Теперь можно собрать реальную картину курса:

```text
Bench: ~/frappe/frappe16-course-bench
│
├── App: frappe
│   └── даёт Framework и системные DocTypes
│
├── App: training
│   └── Module: Training
│       └── позже здесь появится DocType Request
│
└── Site: learn.localhost
    ├── установлены frappe и training
    ├── есть собственная база данных
    └── в этой базе живут Documents данного Site
```

Когда позже появится `Request`, связь станет такой:

```text
training
└── Training
    └── Request              ← описание DocType в App

learn.localhost
└── Documents Request       ← конкретные данные этого Site
```

Вот эта модель понадобится почти в каждой следующей части курса.

---

## Что мы пока намеренно не изучаем

В этой главе не разбираем:

```text
поля DocType
naming
permissions
Python controller
hooks
migrations
REST API
```

Они появятся тогда, когда станут нужны практике.

Сейчас задача только одна: перестать путать уровни системы.

---

## Что произойдёт в лабораторной

Ты руками проверишь на существующем стенде:

```text
где находится Bench
где находятся Apps
где находится каталог Site
какие Apps установлены на learn.localhost
где зафиксирован Module Training
как открыть системный DocType User
как открыть конкретный Document Administrator
```

Затем намеренно укажешь несуществующий Site и увидишь, что Bench не превращает любое имя Site в реальную систему.

Лабораторная ничего не изменит. После неё стенд должен остаться ровно в состоянии главы 0.

---

## Что запомнить

1. `Bench` — рабочее окружение, в котором лежат код Apps и каталоги Sites.
2. `Site` — отдельный экземпляр Frappe со своей базой данных и настройками.
3. `App` — пакет кода и metadata, который можно установить на Site.
4. `Module` — логическая область внутри App.
5. `DocType` — описание типа документов.
6. `Document` — одна конкретная запись DocType.
7. `apps/` и `sites/` — соседние части Bench; App не является подкаталогом конкретного Site.
8. На нашем стенде используются только имена `learn.localhost`, `training` и `Training`.

---

## Официальные источники

- [Directory structure](https://docs.frappe.io/framework/user/en/basics/directory-structure)
- [Sites](https://docs.frappe.io/framework/user/en/basics/sites)
- [Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Module](https://docs.frappe.io/framework/user/en/basics/doctypes/modules)
- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Document API](https://docs.frappe.io/framework/user/en/api/document)

Теперь выполни [**лабораторную 01**](labs/01_FOUNDATIONS_LAB.md).

После неё переходи к [**02. Desk, Desktop, Sidebar, Workspace и навигация Frappe 16**](02_DESK_NAVIGATION.md).