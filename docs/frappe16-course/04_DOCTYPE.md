# 04. DocType: создаём первый объект курса

Блок A закончился без новых бизнес-объектов. На стенде есть Bench, Site `learn.localhost`, App `training` и Module `Training`, но собственного типа данных курса пока нет.

В этой главе это меняется: мы создадим первый Standard DocType — `Request`. С этого момента он останется на стенде до конца курса и будет постепенно расширяться.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

```text
Bench:          ~/frappe/frappe16-course-bench
Site:           learn.localhost
Apps installed: frappe, training
Module:         Training
Developer Mode: включён
User:           Administrator
Request:        ещё не существует
```

`training` уже установлен на `learn.localhost`, поэтому новый Standard DocType можно отнести к Module `Training` и сохранить как часть этого App.

---

## Какую проблему решаем

До сих пор мы работали только с системными объектами Framework, например `User`.

Теперь нужен собственный тип записей:

```text
Request
```

У одной заявки будут поля:

```text
Subject
Description
Status
Due Date
```

А конкретные записи будут выглядеть примерно так:

```text
Заявка: Проверить отчёт
Status: In Progress
Due Date: 2026-09-03
```

Во Frappe описание такого типа записей задаётся через `DocType`.

---

## DocType и Document

Разницу мы уже видели на системном `User`:

```text
DocType:  User
Document: Administrator
```

С `Request` будет то же самое:

```text
DocType: Request
Document: одна конкретная заявка
```

DocType создаётся один раз и описывает структуру типа.

Documents создаются много раз и содержат реальные значения полей.

---

## Что хранит DocType

DocType — не только список полей. В его metadata находятся настройки, которые определяют, как Frappe работает с документом.

В дальнейшем на том же `Request` мы постепенно изучим:

```text
поля и их свойства
naming
ссылки на другие Documents
Child Table
представления Desk
permissions
Workflow
reports
API
scripting
```

Сейчас нам нужен только минимальный каркас. Остальные настройки не трогаем раньше времени.

---

## Standard и Custom: что используем в курсе

У Frappe есть Standard и Custom DocTypes.

В нашем учебном проекте `Request` будет **Standard DocType** внутри App `training`.

Это означает две вещи одновременно:

```text
на learn.localhost появится рабочий DocType
+
его metadata будет экспортирована в файлы App training
```

Developer Mode для этого уже включён в главе 0.

Custom DocType сейчас не нужен: курс должен позже показать реальное приложение и его файлы, а не только настройки одного Site.

Глубокую разницу `Standard vs Custom` разберём позже. Сейчас достаточно знать, почему для `Request` поле `Custom?` оставляем выключенным.

---

## Где окажется Standard DocType на диске

Для нашего App и Module путь детерминирован:

```text
apps/training/
└── training/
    └── training/
        └── doctype/
            └── request/
                └── request.json
```

Полный путь из Bench:

```text
~/frappe/frappe16-course-bench/apps/training/training/training/doctype/request/request.json
```

Почему три похожих уровня:

```text
apps/training                 → каталог App
training/                     → Python package App
training/                     → package Module Training
```

Подробно структуру Python App изучим позже. В лабораторной файл открывается только для одного наблюдения:

> сохранили Standard DocType в Desk → Frappe создал его metadata-файл в App.

JSON пока разбирать не нужно.

---

## Первый состав `Request`

В лабораторной создаём только четыре поля.

| Label | Fieldname | Field Type | Что означает |
|---|---|---|---|
| Subject | `subject` | Data | короткая тема заявки |
| Description | `description` | Small Text | пояснение |
| Status | `status` | Select | текущее простое состояние |
| Due Date | `due_date` | Date | срок |

Для `Status` используем ровно три значения:

```text
Open
In Progress
Done
```

`Subject` будет Mandatory: пустую заявку сохранить нельзя.

Остальные свойства полей подробно разберём в следующей главе.

---

## Title Field

У Document есть системный `name`, но для человека удобнее видеть понятный заголовок.

Поэтому для `Request` зададим:

```text
Title Field = subject
```

На этом этапе не пытаемся настраивать красивую нумерацию `REQ-...`.

Системное именование — тема главы 06. Первые Requests специально позволят увидеть поведение до настройки naming.

---

## Что произойдёт после Save DocType

После сохранения `Request` Frappe сможет дать нам стандартные экраны без написания frontend-кода:

```text
Request List
Request Form
```

А внутри App появится Standard metadata.

Связь будет такой:

```text
DocType Request
        ↓
metadata
        ↓
Frappe строит Form/List
        ↓
Documents Request хранят реальные данные Site
```

Это первая практическая демонстрация metadata-driven подхода во Frappe.

---

## Что пока не включаем

Не настраиваем заранее:

```text
Naming Series
Links
Child Tables
Single / Tree / Submittable / Virtual
permissions для учебных ролей
Workflow
Track Changes
Client Script
Server Script
```

Каждый механизм появится в своей главе и будет добавлен к уже существующему стенду.

---

## Что произойдёт в лабораторной

Ты:

1. создашь Standard DocType `Request` в Module `Training`;
2. добавишь четыре базовых поля;
3. сохранишь DocType;
4. откроешь реальный `Request` List;
5. создашь несколько Documents;
6. увидишь обязательность `Subject`;
7. откроешь `request.json` на диске и убедишься, что Standard metadata действительно экспортирована в `training`.

После лабораторной `Request` уже не удаляется и не создаётся заново в следующих главах.

---

## Что запомнить

1. `DocType` описывает тип документов; `Document` — одна запись этого типа.
2. `Request` — первый собственный DocType сквозного учебного проекта.
3. Он относится к App `training` и Module `Training`.
4. В курсе создаём его как Standard DocType.
5. Базовая форма и список появляются из metadata без собственного frontend-кода.
6. В этой главе модель намеренно минимальна; следующие главы будут расширять её, а не заменять.

---

## Официальные источники

- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Create an App — directory structure](https://docs.frappe.io/framework/user/en/tutorial/create-an-app)
- [DocType controller source — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py)

Теперь выполни [**лабораторную 04**](labs/04_DOCTYPE_LAB.md).

После неё переходи к [**05. DocField и свойства полей**](05_DOCFIELD.md).