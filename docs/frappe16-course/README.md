# Frappe Framework 16 — практический учебник с нуля

Этот курс рассчитан на человека, который впервые открыл Frappe и пока не обязан знать, что такое ORM, metadata, controller, lifecycle, worker или migration.

Это **не справочник для пассивного чтения**. Каждая тема должна быть проверена на живом локальном стенде.

Целевая версия курса — **Frappe Framework 16**, базовый стенд зафиксирован на **Frappe v16.32.0**.

ERPNext, CRM, Helpdesk, HRMS и другие приложения не считаются частью Framework и появляются только там, где помогают понять границу платформы.

Проверено: **2026-08-31**.

---

# Как проходить курс

До главы 1 обязательно выполнить:

**[0. Учебный стенд Frappe 16](00_LAB_SETUP.md)**

После главы 0 должно быть:

```text
Windows 11
└── WSL2 / Debian 13
    └── ~/frappe/frappe16-course-bench/
        ├── Frappe v16.32.0
        ├── Site learn.localhost
        └── App training / Module Training
```

Desk:

```text
http://learn.localhost:8000
```

Дальше каждая тема состоит из двух обязательных частей:

```text
Глава
→ понять механизм

Лабораторная
→ сделать руками
→ увидеть результат
→ изменить условие
→ увидеть другое поведение
→ намеренно встретить ошибку
→ восстановить рабочее состояние
```

**Глава без лабораторной не считается пройденной.**

Все лабораторные собраны также в [отдельном индексе](labs/README.md), а сквозное состояние учебного стенда описано в [PRACTICE_TRACK.md](PRACTICE_TRACK.md).

---

# Сквозная учебная система

Основной объект курса — DocType:

```text
Request
```

Он не выбрасывается после каждой темы, а постепенно развивается:

```text
DocType
→ DocField
→ Naming
→ Links
→ Child Tables
→ Form/List/Kanban/Calendar
→ Workspace
→ Permissions
→ Assignment
→ Workflow
→ Notification
→ Timeline/Version/File/Email
→ Reports/Dashboard/Import
→ Web Form/Website
→ REST/RPC/Auth
→ Client Script
→ Server Script
→ App code
→ Jobs/Scheduler/Migrations/Tests
```

За счёт этого ученик видит не набор несвязанных функций Frappe, а одну систему, которая постепенно усложняется.

---

# Стандарт лабораторной

Каждая лабораторная 1–45 содержит:

1. **Что должно быть готово**.
2. **Конкретную цель**.
3. **Точные действия** в Desk, terminal или API.
4. **Ожидаемый результат**.
5. **Эксперимент** с изменением одного условия.
6. **Намеренную ошибку / поломку**.
7. **Проверку себя**.
8. **Состояние стенда после главы**.

Если результат отличается, не переходи дальше, пока не понял причину.

---

# Программа

## Блок A. Карта Frappe

1. [Bench → Site → App → Module → DocType → Document](01_FOUNDATIONS.md) · [лабораторная](labs/01_FOUNDATIONS_LAB.md)
2. [Desk, Desktop, Sidebar, Workspace и навигация v16](02_DESK_NAVIGATION.md) · [лабораторная](labs/02_DESK_NAVIGATION_LAB.md)
3. [Что входит в Framework, а что является отдельным App](03_FRAMEWORK_VS_APPS.md) · [лабораторная](labs/03_FRAMEWORK_VS_APPS_LAB.md)

## Блок B. Модель данных

4. [DocType от А до Я](04_DOCTYPE.md) · [лабораторная](labs/04_DOCTYPE_LAB.md)
5. [DocField и свойства полей](05_DOCFIELD.md) · [лабораторная](labs/05_DOCFIELD_LAB.md)
6. [Naming и системное поле `name`](06_NAMING.md) · [лабораторная](labs/06_NAMING_LAB.md)
7. [Link, Dynamic Link и Fetch From](07_LINKS_AND_FETCH.md) · [лабораторная](labs/07_LINKS_AND_FETCH_LAB.md)
8. [Child Table и Table MultiSelect](08_CHILD_TABLES.md) · [лабораторная](labs/08_CHILD_TABLES_LAB.md)
9. [Single, Tree, Submittable и Virtual DocType](09_SPECIAL_DOCTYPES.md) · [лабораторная](labs/09_SPECIAL_DOCTYPES_LAB.md)
10. [`docstatus`, Submit, Cancel и Amendment](10_DOCSTATUS_LIFECYCLE.md) · [лабораторная](labs/10_DOCSTATUS_LIFECYCLE_LAB.md)

## Блок C. Интерфейс

11. [Form View](11_FORM_VIEW.md) · [лабораторная](labs/11_FORM_VIEW_LAB.md)
12. [List View и фильтры](12_LIST_VIEW_AND_FILTERS.md) · [лабораторная](labs/12_LIST_VIEW_AND_FILTERS_LAB.md)
13. [Kanban, Calendar, Gantt и Tree View](13_KANBAN_CALENDAR_GANTT_TREE.md) · [лабораторная](labs/13_KANBAN_CALENDAR_GANTT_TREE_LAB.md)
14. [Workspace, Shortcut, Quick List, Number Card и Chart](14_WORKSPACE_AND_DASHBOARD_BLOCKS.md) · [лабораторная](labs/14_WORKSPACE_AND_DASHBOARD_BLOCKS_LAB.md)
15. [Customize Form](15_CUSTOMIZE_FORM.md) · [лабораторная](labs/15_CUSTOMIZE_FORM_LAB.md)
16. [Desk Page и границы штатного интерфейса](16_DESK_PAGE_AND_UI_BOUNDARIES.md) · [лабораторная](labs/16_DESK_PAGE_AND_UI_BOUNDARIES_LAB.md)

## Блок D. Пользователи и права

17. [User и Role](17_USER_AND_ROLE.md) · [лабораторная](labs/17_USER_AND_ROLE_LAB.md)
18. [Role Permission Manager](18_ROLE_PERMISSION_MANAGER.md) · [лабораторная](labs/18_ROLE_PERMISSION_MANAGER_LAB.md)
19. [Permission Level](19_PERMISSION_LEVEL.md) · [лабораторная](labs/19_PERMISSION_LEVEL_LAB.md)
20. [User Permission](20_USER_PERMISSION.md) · [лабораторная](labs/20_USER_PERMISSION_LAB.md)
21. [Owner и Sharing](21_OWNER_AND_SHARING.md) · [лабораторная](labs/21_OWNER_AND_SHARING_LAB.md)
22. [Где заканчиваются штатные permissions](22_PERMISSION_BOUNDARIES.md) · [лабораторная](labs/22_PERMISSION_BOUNDARIES_LAB.md)

## Блок E. Работа и процессы

23. [Assignment и ToDo](23_ASSIGNMENT_AND_TODO.md) · [лабораторная](labs/23_ASSIGNMENT_AND_TODO_LAB.md)
24. [Assignment Rule](24_ASSIGNMENT_RULE.md) · [лабораторная](labs/24_ASSIGNMENT_RULE_LAB.md)
25. [Status против Workflow State](25_STATUS_VS_WORKFLOW_STATE.md) · [лабораторная](labs/25_STATUS_VS_WORKFLOW_STATE_LAB.md)
26. [Workflow и переходы](26_WORKFLOW_AND_TRANSITIONS.md) · [лабораторная](labs/26_WORKFLOW_AND_TRANSITIONS_LAB.md)
27. [Notification](27_NOTIFICATION.md) · [лабораторная](labs/27_NOTIFICATION_LAB.md)
28. [Auto Repeat](28_AUTO_REPEAT.md) · [лабораторная](labs/28_AUTO_REPEAT_LAB.md)

## Блок F. Возможности документа

29. [Timeline и Comments](29_TIMELINE_AND_COMMENTS.md) · [лабораторная](labs/29_TIMELINE_AND_COMMENTS_LAB.md)
30. [Version и Track Changes](30_VERSION_AND_TRACK_CHANGES.md) · [лабораторная](labs/30_VERSION_AND_TRACK_CHANGES_LAB.md)
31. [Attachments и File](31_ATTACHMENTS_AND_FILE.md) · [лабораторная](labs/31_ATTACHMENTS_AND_FILE_LAB.md)
32. [Email / Communication](32_EMAIL_AND_COMMUNICATION.md) · [лабораторная](labs/32_EMAIL_AND_COMMUNICATION_LAB.md)
33. [Print Format и PDF](33_PRINT_FORMAT_AND_PDF.md) · [лабораторная](labs/33_PRINT_FORMAT_AND_PDF_LAB.md)

## Блок G. Данные и аналитика

34. [Report Builder](34_REPORT_BUILDER.md) · [лабораторная](labs/34_REPORT_BUILDER_LAB.md)
35. [Query Report](35_QUERY_REPORT.md) · [лабораторная](labs/35_QUERY_REPORT_LAB.md)
36. [Script Report](36_SCRIPT_REPORT.md) · [лабораторная](labs/36_SCRIPT_REPORT_LAB.md)
37. [Dashboard Chart и Number Card](37_DASHBOARD_CHART_AND_NUMBER_CARD.md) · [лабораторная](labs/37_DASHBOARD_CHART_AND_NUMBER_CARD_LAB.md)
38. [Data Import / Export](38_DATA_IMPORT_EXPORT.md) · [лабораторная](labs/38_DATA_IMPORT_EXPORT_LAB.md)

## Блок H. Внешние интерфейсы

39. [Web Form](39_WEB_FORM.md) · [лабораторная](labs/39_WEB_FORM_LAB.md)
40. [Website / portal-возможности Framework](40_WEBSITE_AND_PORTAL.md) · [лабораторная](labs/40_WEBSITE_AND_PORTAL_LAB.md)
41. [REST API](41_REST_API.md) · [лабораторная](labs/41_REST_API_LAB.md)
42. [RPC и whitelisted methods](42_RPC_AND_WHITELISTED_METHODS.md) · [лабораторная](labs/42_RPC_AND_WHITELISTED_METHODS_LAB.md)
43. [Authentication для интеграций](43_AUTHENTICATION_FOR_INTEGRATIONS.md) · [лабораторная](labs/43_AUTHENTICATION_FOR_INTEGRATIONS_LAB.md)

## Блок I. Low-code и разработка

44. [Client Script](44_CLIENT_SCRIPT.md) · [лабораторная](labs/44_CLIENT_SCRIPT_LAB.md)
45. [Server Script](45_SERVER_SCRIPT.md) · [лабораторная](labs/45_SERVER_SCRIPT_LAB.md)
46. Standard vs Custom
47. Developer Mode
48. Собственное App
49. Standard DocType и файлы приложения
50. Python controller и lifecycle документа
51. Hooks

## Блок J. Серверная инфраструктура

52. ORM и Database API
53. Background Jobs и очереди
54. Scheduler
55. Realtime
56. Fixtures
57. Patches и migrations
58. Tests

## Блок K. Bench и эксплуатация

59. Bench и Bench CLI
60. Site configuration
61. Установка и обновление Apps
62. `bench migrate`
63. Workers, scheduler, Redis/Valkey и web processes
64. Logs и диагностика
65. Backup и restore
66. Production deployment — необходимый минимум

## Блок L. Итоговая практика

67. Создаём учебное приложение с нуля
68. Проверяем штатные механизмы руками
69. Добавляем scripting там, где настроек уже не хватает
70. Переводим стабильную реализацию в App и Git
71. Устанавливаем App на чистый Site и воспроизводим состояние
72. Собираем итоговую карту: **штатно / low-code / application code / custom frontend**

---

# Как выбирать уровень решения

Во время лабораторных постоянно проверяй лестницу:

```text
поле или свойство DocType
        ↓ не хватает
штатная настройка Framework
        ↓ не хватает
Client Script / Server Script / Jinja
        ↓ не хватает
код собственного App
        ↓ не хватает
отдельный frontend или внешняя подсистема
```

Не начинай с Python только потому, что Python позволяет решить задачу. Цель курса — сначала научиться видеть возможности самой платформы.

---

# Правило безопасности учебного стенда

Стенд `learn.localhost` предназначен для экспериментов.

В нём можно:

```text
создавать и удалять тестовые данные
намеренно ломать настройки
проверять permission errors
делать неудачные imports
проверять API failures
перезапускать bench
восстанавливать состояние
```

Но нельзя использовать в учебнике:

```text
реальные рабочие пароли
реальные API secrets
корпоративную SMTP-почту без необходимости
production database
production Site
```

---

# Про точность курса

Для поведения именно Frappe 16 приоритет источников такой:

1. официальная документация Frappe;
2. исходный код ветки `version-16`, если документация отстаёт или неоднозначна;
3. материалы старых версий — только после подтверждения поведения в v16.

Если лабораторная расходится с живым `v16.32.0`, фактическое поведение стенда является сигналом перепроверить документацию и исходный код, а не придумывать обходной «магический» шаг.
