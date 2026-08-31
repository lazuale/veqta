# Frappe Framework 16 — практический учебник с нуля

Этот учебник рассчитан на человека, который впервые открыл Frappe и пока не обязан знать, что такое ORM, metadata, controller, lifecycle, worker или migration.

Но это **не справочник для чтения**.

Курс строится вокруг живого учебного стенда:

```text
прочитал минимум теории
        ↓
сделал руками на Frappe
        ↓
увидел результат
        ↓
изменил условие
        ↓
увидел другое поведение
        ↓
понял границу механизма
```

Цель — к концу курса не просто знать названия возможностей Frappe, а уметь самостоятельно открыть чистый Site и воспроизвести нужное поведение.

Целевая версия — **Frappe Framework 16**. Базовый стенд курса фиксируется на **Frappe v16.32.0**. ERPNext, CRM, Helpdesk, HRMS и другие приложения не считаются частью Framework: они упоминаются только там, где это помогает понять границу платформы.

Проверено: **2026-08-31**.

---

# Сначала стенд, потом книга

До главы 1 обязательно выполнить:

**[0. Учебный стенд Frappe 16](00_LAB_SETUP.md)**

После него должно быть:

```text
Windows 11
└── WSL2 / Debian 13
    └── frappe16-course-bench
        ├── Frappe v16.32.0
        ├── Site learn.localhost
        └── учебное App training
```

Desk:

```text
http://learn.localhost:8000
```

Без работающего стенда дальнейший курс теряет смысл.

Отдельно смотри:

**[Практический трек всего курса](PRACTICE_TRACK.md)**

Там зафиксировано, что именно ученик должен сделать руками по мере прохождения блоков.

---

# Сквозная лабораторная работа

Начиная с блока модели данных мы создаём один основной учебный DocType:

```text
Request
```

Он постепенно получит:

```text
поля
naming
Link
Child Table
permissions
assignment
workflow
notifications
comments
versions
attachments
reports
charts
Web Form
REST API
Client Script
Server Script
controller
background jobs
tests
```

То есть следующая глава обычно не начинает пример с нуля, а **изменяет уже существующий учебный стенд**.

Так ученик видит, как отдельные механизмы Frappe складываются в одну систему.

---

# Как устроена каждая глава

Основной порядок теперь такой:

1. **Что должно быть готово** — состояние стенда до начала.
2. **Что сегодня увидим** — конкретный результат, который должен появиться.
3. **Минимальная теория** — только то, что нужно для осмысленного действия.
4. **Практика** — точные шаги в Desk / terminal / API.
5. **Ожидаемый результат** — что именно должно измениться и где это увидеть.
6. **Эксперимент** — меняем одно условие и смотрим разницу.
7. **Типичная ошибка** — намеренно встречаем или разбираем реальный failure mode.
8. **Проверка себя** — ученик должен объяснить, почему результат получился именно таким.
9. **Состояние стенда после главы** — что должно остаться для следующей темы.
10. **Что запомнить** — короткая итоговая модель.

Глава не считается законченной только потому, что в ней перечислены все поля интерфейса.

---

# Что считается практикой

Плохо:

```text
«Попробуйте создать несколько записей»
```

Хорошо:

```text
1. Создай Request A со Status = Open.
2. Создай Request B со Status = Closed.
3. Открой List View.
4. Поставь фильтр Status = Open.
5. Должен остаться только Request A.
6. Удали фильтр.
7. Оба документа снова должны быть видны.
```

Ученик всегда должен понимать:

```text
что сделать
что увидеть
как проверить
что изменить для контраста
```

---

# Можно и нужно ломать учебный стенд

Это лаборатория, а не production.

В упражнениях мы намеренно будем получать:

```text
Permission Error
validation error
неправильный Client Script
неудачный API request
сломанный Workflow transition
ошибку migration/test
```

После этого ошибка исправляется и повторяется правильный сценарий.

Именно так становятся понятны реальные границы Frappe.

На стенде не должно быть рабочих данных, которые нельзя потерять.

---

# Шесть слов, которые встретятся сразу

| Термин | Простое объяснение |
|---|---|
| **Bench** | окружение Frappe и инструмент для управления им |
| **Site** | один работающий экземпляр Frappe со своими данными |
| **App** | устанавливаемый пакет функциональности |
| **Module** | логическая область внутри App |
| **DocType** | описание типа данных и его поведения |
| **Document** | одна конкретная запись DocType |
| **Desk** | встроенный рабочий интерфейс для системных пользователей |

Сейчас определения можно не заучивать. В первых главах мы найдём каждый из этих объектов на живом стенде.

---

# Программа

## Перед началом

0. [Учебный стенд Frappe 16](00_LAB_SETUP.md)

Дополнительно: [сквозной практический трек](PRACTICE_TRACK.md).

### Блок A. Карта Frappe

1. [Bench → Site → App → Module → DocType → Document](01_FOUNDATIONS.md)
2. [Desk, Desktop, Sidebar, Workspace и навигация v16](02_DESK_NAVIGATION.md)
3. [Что входит в Framework, а что является отдельным App](03_FRAMEWORK_VS_APPS.md)

### Блок B. Модель данных

4. [DocType от А до Я](04_DOCTYPE.md)
5. [DocField и свойства полей](05_DOCFIELD.md)
6. [Naming и системное поле `name`](06_NAMING.md)
7. [Link, Dynamic Link и Fetch From](07_LINKS_AND_FETCH.md)
8. [Child Table и Table MultiSelect](08_CHILD_TABLES.md)
9. [Single, Tree, Submittable и Virtual DocType](09_SPECIAL_DOCTYPES.md)
10. [`docstatus`, Submit, Cancel и Amendment](10_DOCSTATUS_LIFECYCLE.md)

### Блок C. Интерфейс

11. [Form View](11_FORM_VIEW.md)
12. [List View и фильтры](12_LIST_VIEW_AND_FILTERS.md)
13. [Kanban, Calendar, Gantt и Tree View](13_KANBAN_CALENDAR_GANTT_TREE.md)
14. [Workspace, Shortcut, Quick List, Number Card и Chart](14_WORKSPACE_AND_DASHBOARD_BLOCKS.md)
15. [Customize Form](15_CUSTOMIZE_FORM.md)
16. [Desk Page и границы штатного интерфейса](16_DESK_PAGE_AND_UI_BOUNDARIES.md)

### Блок D. Пользователи и права

17. [User и Role](17_USER_AND_ROLE.md)
18. [Role Permission Manager](18_ROLE_PERMISSION_MANAGER.md)
19. [Permission Level](19_PERMISSION_LEVEL.md)
20. [User Permission](20_USER_PERMISSION.md)
21. [Owner и Sharing](21_OWNER_AND_SHARING.md)
22. [Где заканчиваются штатные permissions](22_PERMISSION_BOUNDARIES.md)

### Блок E. Работа и процессы

23. [Assignment и ToDo](23_ASSIGNMENT_AND_TODO.md)
24. [Assignment Rule](24_ASSIGNMENT_RULE.md)
25. [Status против Workflow State](25_STATUS_VS_WORKFLOW_STATE.md)
26. [Workflow и переходы](26_WORKFLOW_AND_TRANSITIONS.md)
27. [Notification](27_NOTIFICATION.md)
28. [Auto Repeat](28_AUTO_REPEAT.md)

### Блок F. Возможности документа

29. [Timeline и Comments](29_TIMELINE_AND_COMMENTS.md)
30. [Version и Track Changes](30_VERSION_AND_TRACK_CHANGES.md)
31. [Attachments и File](31_ATTACHMENTS_AND_FILE.md)
32. [Email / Communication](32_EMAIL_AND_COMMUNICATION.md)
33. [Print Format и PDF](33_PRINT_FORMAT_AND_PDF.md)

### Блок G. Данные и аналитика

34. [Report Builder](34_REPORT_BUILDER.md)
35. [Query Report](35_QUERY_REPORT.md)
36. [Script Report](36_SCRIPT_REPORT.md)
37. [Dashboard Chart и Number Card](37_DASHBOARD_CHART_AND_NUMBER_CARD.md)
38. [Data Import / Export](38_DATA_IMPORT_EXPORT.md)

### Блок H. Внешние интерфейсы

39. [Web Form](39_WEB_FORM.md)
40. [Website / portal-возможности Framework](40_WEBSITE_AND_PORTAL.md)
41. [REST API](41_REST_API.md)
42. [RPC и whitelisted methods](42_RPC_AND_WHITELISTED_METHODS.md)
43. [Authentication для интеграций](43_AUTHENTICATION_FOR_INTEGRATIONS.md)

### Блок I. Low-code и разработка

44. [Client Script](44_CLIENT_SCRIPT.md)
45. [Server Script](45_SERVER_SCRIPT.md)
46. Standard vs Custom
47. Developer Mode — что мы включили в учебном стенде и зачем
48. Собственное App — теперь разбираем `training` осознанно
49. Standard DocType и файлы приложения
50. Python controller и lifecycle документа
51. Hooks

### Блок J. Серверная инфраструктура

52. ORM и Database API
53. Background Jobs и очереди
54. Scheduler
55. Realtime
56. Fixtures
57. Patches и migrations
58. Tests

### Блок K. Bench и эксплуатация

59. Bench и Bench CLI
60. Site configuration
61. Установка и обновление Apps
62. `bench migrate`
63. Workers, scheduler, Redis/Valkey и web processes
64. Logs и диагностика
65. Backup и restore
66. Production deployment — необходимый минимум

### Блок L. Итоговая практика

67. Создаём новое учебное приложение с нуля уже без пошаговой подсказки
68. Проверяем штатные механизмы руками
69. Добавляем scripting там, где настроек уже не хватает
70. Переводим стабильную реализацию в App и Git
71. Устанавливаем App на чистый Site и воспроизводим состояние
72. Собираем итоговую карту: **штатно / low-code / application code / custom frontend**

---

# Как выбирать уровень решения

В практических заданиях постоянно используется одна и та же лестница:

```text
можно решить свойством поля / DocType?
        ↓ нет
есть готовый штатный механизм Framework?
        ↓ нет
хватает Client Script / Server Script / Jinja?
        ↓ нет
нужен код собственного App?
        ↓ нет
нужен отдельный frontend / внешняя подсистема?
```

Ученик должен не только сделать работающий вариант, но и увидеть, **почему предыдущего уровня уже не хватило**.

---

# Про Developer Mode в стенде

В главе 0 Developer Mode включается заранее, потому что уже в ранних главах мы создаём Standard DocType внутри учебного App `training` и хотим видеть реальные файлы на диске.

Это не означает, что ученик уже обязан понимать Developer Mode.

В главе 47 мы специально:

```text
выключим его
попробуем создать Standard DocType
увидим ограничение
включим обратно
посмотрим, что он меняет
```

То есть установка инструмента и изучение его устройства намеренно разделены.

---

# Про точность курса

Для поведения именно v16 приоритет такой:

1. актуальная документация Frappe;
2. исходный код ветки `version-16`, если документация отстаёт или формулирует неоднозначно;
3. конкретный релиз `v16.32.0`, если поведение зависит от patch/minor состояния;
4. материалы старых версий — только когда поведение подтверждено для v16.

В технических местах курс может давать ссылку на исходный код, но ученик не обязан заучивать internals, если глава посвящена пользовательскому механизму.

---

# Основные источники

- [Frappe Framework — Introduction](https://docs.frappe.io/framework/user/en/introduction)
- [Installation](https://docs.frappe.io/framework/user/en/installation)
- [Bench](https://docs.frappe.io/framework/user/en/bench)
- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [REST API](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [Migrating to Version 16](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)
- [Frappe v16.32.0](https://github.com/frappe/frappe/releases/tag/v16.32.0)

Каждая глава дополнительно содержит источники по своей теме.
