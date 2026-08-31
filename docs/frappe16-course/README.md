# Frappe Framework 16 — учебник с нуля

Этот учебник рассчитан на человека, который впервые открыл Frappe и пока не обязан знать, что такое ORM, metadata, controller или lifecycle.

Задача курса — не заставить запомнить сотню терминов, а постепенно собрать понятную картину: **что Frappe умеет штатно, где это находится в интерфейсе и когда действительно нужен код**.

Целевая версия — **Frappe Framework 16**. ERPNext, CRM, Helpdesk, HRMS и другие приложения не считаются частью Framework: они упоминаются только там, где это помогает понять границу платформы.

Проверено: **2026-08-31**.

## Как читать

Иди по порядку. Первые главы специально объясняют базовые слова, которые дальше будут использоваться без длинных отступлений.

В каждой главе используется один и тот же принцип:

1. **Сначала простыми словами** — что это и зачем.
2. **Потом маленький пример** — чтобы термин за что-то зацепился.
3. **Затем детали Frappe** — названия полей, флаги, методы и ограничения.
4. **В конце — мини-практика и несколько вещей, которые стоит запомнить.**

Если технический блок пока тяжёлый, его можно прочитать по диагонали и вернуться позже. На первом проходе важнее понять общую механику.

## Шесть слов, которые встретятся сразу

| Термин | Простое объяснение |
|---|---|
| **Bench** | окружение Frappe и инструмент для управления им |
| **Site** | один работающий экземпляр Frappe со своими данными |
| **App** | устанавливаемый пакет функциональности |
| **DocType** | описание типа данных и его поведения |
| **Document** | одна конкретная запись DocType |
| **Desk** | встроенный рабочий интерфейс для системных пользователей |

Пока этого достаточно. Точные детали разбираются дальше.

## Программа

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
40. Website / portal-возможности Framework
41. REST API
42. RPC и whitelisted methods
43. Authentication для интеграций

### Блок I. Low-code и разработка

44. Client Script
45. Server Script
46. Standard vs Custom
47. Developer Mode
48. Собственное App
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

67. Создаём учебное приложение с нуля
68. Проверяем штатные механизмы руками
69. Добавляем scripting там, где настроек уже не хватает
70. Переводим стабильную реализацию в App и Git
71. Устанавливаем App на чистый Site и воспроизводим состояние
72. Собираем итоговую карту: **штатно / low-code / application code / custom frontend**

## Как выбирать уровень решения

Не начинай с Python только потому, что умеешь писать код. Во Frappe многие задачи закрываются раньше:

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

Эта последовательность — не запрет на код. Она просто помогает сначала увидеть, что уже умеет Framework.

## Про точность курса

Для поведения именно v16 приоритет такой:

1. документация Frappe;
2. исходный код ветки `version-16`, если документация отстаёт или формулирует неоднозначно;
3. материалы старых версий — только когда поведение подтверждено для v16.

Поэтому в некоторых главах встречаются короткие технические примечания со ссылкой на исходный код. Их не нужно заучивать.

## Основные источники

- [Frappe Framework — Introduction](https://docs.frappe.io/framework/user/en/introduction)
- [Bench](https://docs.frappe.io/framework/user/en/bench)
- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [REST API](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [Migrating to Version 16](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)

Каждая глава дополнительно содержит источники по своей теме.