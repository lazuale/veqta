# Дорожная карта базового практикума Frappe Framework 16

Дорожная карта показывает эволюцию одного продукта от чистого стенда до воспроизводимого рабочего приложения, собранного максимально нативно средствами Frappe 16.

Она не дублирует подробный состав работ из `MATRIX.md`. Здесь фиксируются только фазы, зависимости и логика порядка.

## Фаза I. Поднять платформу

**Работы:** `00–01`

Цель:

> Понимать, где работает Frappe 16, уметь поднять Site и ориентироваться в его штатной среде.

```text
чистая Linux-система
        ↓
      Bench
        ↓
       Site
        ↓
Desk / Desktop / Sidebar / Awesome Bar
```

Следующая фаза начинается только после того, как стенд можно самостоятельно остановить, запустить и проверить.

---

## Фаза II. Создать нормальный Frappe App

**Работа:** `02`

Цель:

> Создать нативный контейнер продукта штатным Bench-процессом, не начиная преждевременно писать собственную бизнес-логику.

```text
Bench
  ↓
bench new-app
  ↓
frappe_practicum
  ↓
Module: Practicum
  ↓
install-app
  ↓
Git
```

На выходе есть обычный Frappe App, куда естественно будут относиться все дальнейшие стандартные объекты проекта.

---

## Фаза III. Построить модель данных

**Работы:** `03–08`

Цель:

> Освоить ядро Frappe: DocType, Document, поля, связи, специальные типы DocType и lifecycle.

```text
Work Item
   ↓
поля / layout / naming
   ↓
Project / Child / Single
   ↓
Category [Tree]
   ↓
Work Approval [Submittable]
   ↓
lifecycle / audit
```

Ключевое решение: `Work Item` остаётся обычным рабочим Document; `Work Approval` используется для Submit/Cancel/Amend.

---

## Фаза IV. Освоить интерфейс, который Frappe строит из metadata

**Работы:** `09–10`

Цель:

> Показать, насколько далеко можно зайти без собственного frontend.

```text
Documents
   ↓
List / Report View / Kanban
   ↓
Calendar / Gantt / Map / Tree
   ↓
Workspace
```

Number Card и Dashboard Chart пока не появляются: аналитика вводится только после отчётности.

---

## Фаза V. Добавить людей и доступ

**Работы:** `11–12`

Цель:

> Сделать продукт многопользовательским и построить права сначала полностью штатными декларативными механизмами.

```text
User
 ↓
Role / Role Profile
 ↓
Role Permissions
 ↓
Permission Level
 ↓
If Owner / User Permission / Share
```

Server Script Permission Query здесь пока не используется: сначала ученик обязан понять стандартную модель permissions.

---

## Фаза VI. Превратить Documents в рабочий процесс

**Работы:** `13–18`

Цель:

> Получить полноценный рабочий процесс средствами готовых Frappe-механизмов до перехода к scripting.

```text
Assign / ToDo / Collaboration
        ↓
Assignment Rule + condition
        ↓
Workflow + condition
        ↓
Notification + condition
        ↓
Auto Repeat
        ↓
Customize Form / Layout / Actions / Links
```

Это принципиальная точка курса: всё, что можно разумно решить декларативно, решается здесь без Client Script и Server Script.

---

## Фаза VII. Освоить встроенный low-code слой

**Работы:** `19–21`

Цель:

> Научиться расширять штатное поведение внутри самого Frappe, не переходя к файловой разработке собственного backend/frontend.

```text
декларативная форма
      ↓
Client Script
      ↓
Server Script: DocType Event
      ↓
Server Script: Scheduler Event / Permission Query
```

Порядок важен:

- Client Script используется только для реального клиентского поведения;
- server-side validation не дублируется бессмысленно на клиенте;
- Permission Query вводится только после обычных permissions;
- Scheduler Event вводится как штатная low-code автоматизация, а не как повод писать hooks.

---

## Фаза VIII. Работать с массивом данных и аналитикой

**Работы:** `22–24`

Цель:

> Освоить нативную лестницу от массовых данных к сложной отчётности.

```text
Data Import / Export
       ↓
Report Builder
       ↓
Query Report
       ↓
Custom Script Report
       ↓
Number Card / Dashboard Chart
       ↓
Workspace analytics
```

Главный принцип этой фазы:

> Не писать SQL или script, если задачу нормально решает Report Builder.

---

## Фаза IX. Вывод документов и Email

**Работы:** `25–26`

Цель:

> Пройти штатную лестницу от визуального конструктора к встроенному шаблонному low-code.

```text
Standard Print
     ↓
Print Format Builder
     ↓
Jinja Print Format
     ↓
PDF
     ↓
Email / Communication / Email Queue
     ↓
Email Notification
```

Jinja используется как штатная система шаблонов Frappe, а не как отдельный курс web-разработки.

---

## Фаза X. Выйти за пределы Desk

**Работы:** `27–28`

Цель:

> Использовать штатный website-layer Frappe до создания собственного frontend.

```text
Website Settings
      ↓
Web Page
      ↓
Web Form
      ↓
Website User
      ↓
Web Form layout / CSS / Client Script
```

Web Form scripting вводится только после базового Web Form, а не вместо его штатных настроек.

---

## Фаза XI. Интеграции

**Работы:** `29–31`

Цель:

> Освоить три естественных интеграционных слоя Frappe: готовый REST, low-code API и исходящие события.

```text
автоматический REST CRUD
        ↓
Server Script API
        ↓
Webhook
        ↓
Workflow Transition Tasks v16
```

Сначала используется автоматически предоставляемый REST API. Server Script API создаётся только для сценария, который нельзя выразить обычным CRUD.

Workflow Transition Tasks вводятся последними, потому что к этому моменту уже понятны Workflow, Server Script и Webhook.

---

## Фаза XII. Понять альтернативный stock-механизм Package

**Работа:** `32`

Цель:

> Понять, зачем Frappe имеет Package и чем lightweight/UI-created package отличается от обычного Frappe App.

Package изучается как штатная возможность платформы, но не подменяет основной App учебного проекта.

---

## Фаза XIII. Доказать воспроизводимость App

**Работа:** `33`

Цель:

> Установить тот же App на второй чистый Site штатным Git/Bench-процессом.

```text
Git repository
     ↓
второй Bench/Site
     ↓
get-app / install-app
     ↓
bench migrate
     ↓
тот же Practicum App
```

Это проверяет переносимость продукта как App, а не восстановление пользовательских данных.

---

## Фаза XIV. Доказать восстановимость Site

**Работы:** `34–35`

Цель:

> Отдельно доказать восстановление полного состояния Site и затем пройти весь сквозной сценарий.

```text
Site с данными
    ↓
backup
    ↓
restore
    ↓
финальная проверка
```

Финальный сценарий объединяет Desk, Web Form, Workflow, Notifications, scripts, reports, print/email, REST/Webhook и восстановление.

---

# Итоговая траектория

```text
01. ПЛАТФОРМА                     00–01
02. APP                           02
03. МОДЕЛЬ И LIFECYCLE            03–08
04. VIEWS И WORKSPACE             09–10
05. USERS И PERMISSIONS           11–12
06. РАБОЧИЙ ПРОЦЕСС               13–18
07. ВСТРОЕННЫЙ LOW-CODE           19–21
08. ДАННЫЕ И АНАЛИТИКА            22–24
09. PRINT И EMAIL                 25–26
10. WEBSITE / WEB FORM            27–28
11. API / INTEGRATIONS            29–31
12. PACKAGE                       32
13. ВОСПРОИЗВОДИМОСТЬ APP         33
14. BACKUP / RESTORE / FINAL      34–35
```

# Правило перехода между фазами

Следующая фаза начинается только после прохождения контрольного результата предыдущей.

Ключевые зависимости:

- App создаётся раньше стандартных объектов проекта;
- scripting не используется до освоения декларативных возможностей;
- Client Script не считается серверной бизнес-валидацией;
- Permission Query не используется до обычной permissions-модели;
- Query Report не используется, пока задачу решает Report Builder;
- custom Script Report не используется, пока хватает Query Report;
- Jinja не используется вместо Print Format Builder без причины;
- Server Script API не используется вместо автоматически предоставляемого REST CRUD;
- Workflow Transition Tasks не изучаются раньше Workflow, Server Script и Webhook;
- Package не подменяет обычный App;
- Git-based App deployment и backup/restore рассматриваются как разные навыки.

Так сохраняется принцип **«максимально нативно: сначала Frappe, потом low-code, и только затем — Development»**.