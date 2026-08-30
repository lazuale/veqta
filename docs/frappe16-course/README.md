# Frappe Framework 16 — полный учебный курс

Этот каталог — самостоятельный учебник по **Frappe Framework 16 с нуля**.

Его цель — последовательно изучить:

- устройство Frappe Framework;
- штатный интерфейс и навигацию;
- модель данных и DocType;
- пользователей и права;
- Workflow, Assignment и автоматизацию;
- отчёты, печать, импорт и экспорт;
- Web Forms и API;
- low-code возможности;
- разработку собственных Apps;
- фоновые процессы и эксплуатацию.

Место хранения этого учебника не относится к его предметной области. Материал должен оставаться самостоятельным и переносимым в другой репозиторий без смысловых изменений.

## Цель курса

После прохождения курса читатель должен понимать не только **как выполнить действие во Frappe**, но и:

1. что именно делает Framework;
2. какие возможности существуют штатно;
3. где они находятся в интерфейсе;
4. какие metadata и настройки стоят за интерфейсом;
5. где заканчивается конфигурация и начинается код;
6. когда нужен Client Script, Server Script или Python App;
7. как устроено приложение от DocType до production-процессов.

## Статус и границы

- Целевая версия: **Frappe Framework 16**.
- Актуальность проверяется по официальной документации и исходному коду Frappe.
- Основной предмет курса — **чистый Frappe Framework**.
- ERPNext, Frappe CRM, Helpdesk, HRMS и другие приложения не считаются частью Framework и упоминаются только для объяснения границы между платформой и отдельными Apps.
- Материалы по старым версиям используются только тогда, когда соответствующая возможность подтверждена для v16.

Проверено: **2026-08-30**.

## Как проходить курс

Курс идёт от общей карты платформы к интерфейсу, затем к данным и настройкам, после этого — к scripting и полноценной разработке.

Для каждого механизма фиксируем четыре вещи:

1. **Что это такое.**
2. **Где это находится и как выглядит.**
3. **Что Frappe делает штатно.**
4. **Где заканчивается штатная возможность и требуется код.**

Уровни решения задачи:

```text
1. Metadata
   DocType / DocField / Link / Child Table

2. Configuration
   Permissions / Workflow / Assignment / Notification / Reports

3. Low-code
   Client Script / Server Script / Jinja / Script Report

4. Application code
   Python controllers / hooks / API / jobs / tests

5. Custom frontend
   используется, когда штатного Desk или web-интерфейсов недостаточно
```

## Программа

### Блок A. Карта Frappe

1. [Архитектура: Bench → Site → App → Module → DocType → Document](01_FOUNDATIONS.md)
2. [Desk, Desktop, Sidebar, Workspace и навигация v16](02_DESK_NAVIGATION.md)
3. [Что входит в чистый Frappe Framework 16, а что является отдельным App](03_FRAMEWORK_VS_APPS.md)

### Блок B. Модель данных

4. [DocType от А до Я](04_DOCTYPE.md)
5. [DocField и свойства полей](05_DOCFIELD.md)
6. [Naming и `name`](06_NAMING.md)
7. [Link, Dynamic Link и Fetch From](07_LINKS_AND_FETCH.md)
8. [Child Table и Table MultiSelect](08_CHILD_TABLES.md)
9. [Single, Tree, Submittable и Virtual DocType](09_SPECIAL_DOCTYPES.md)
10. `docstatus`, Submit, Cancel и Amendment

### Блок C. Интерфейс

11. Form View
12. List View и фильтры
13. Kanban, Calendar, Gantt и Tree View
14. Workspace, Shortcut, Quick List, Number Card и Chart
15. Customize Form
16. Desk Page и границы штатного интерфейса

### Блок D. Пользователи и права

17. User и Role
18. Role Permission Manager
19. Permission Level
20. User Permission
21. Owner и Sharing
22. Где заканчиваются штатные permissions

### Блок E. Работа и процессы

23. Assignment и ToDo
24. Assignment Rule
25. Status против Workflow State
26. Workflow и переходы
27. Notification
28. Auto Repeat

### Блок F. Системные возможности документа

29. Timeline и Comments
30. Version и Track Changes
31. Attachments и File
32. Email / Communication
33. Print Format и PDF

### Блок G. Данные и аналитика

34. Report Builder
35. Query Report
36. Script Report
37. Dashboard Chart и Number Card
38. Data Import / Export

### Блок H. Внешние интерфейсы

39. Web Form
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
66. Production deployment — что должен понимать разработчик Frappe

### Блок L. Итоговая практика

67. Создаём нейтральное учебное приложение с нуля
68. Проверяем штатные механизмы руками
69. Добавляем scripting только там, где configuration недостаточно
70. Переводим стабильную реализацию в App и Git
71. Устанавливаем App на чистый Site и воспроизводим состояние
72. Составляем итоговую карту возможностей: **штатно / low-code / application code / custom frontend**

## Главный принцип обучения

Для любой задачи сначала определяем минимальный уровень решения:

```text
Можно решить свойством DocType/DocField?
        ↓ нет
Есть штатная настройка Framework?
        ↓ нет
Достаточно low-code механизма?
        ↓ нет
Нужен код собственного App?
        ↓ нет
Только тогда рассматриваем отдельный frontend или внешнюю подсистему.
```

Это позволяет понять реальную мощность Frappe, а не изучать его как набор случайных экранов и API.

## Основные официальные источники

- [Frappe Framework — Introduction](https://docs.frappe.io/framework/user/en/introduction)
- [Bench](https://docs.frappe.io/framework/user/en/bench)
- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [REST API](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [Migration guide for Version 16](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)

Каждая глава курса должна содержать собственные ссылки на официальную документацию и, когда это полезно, на исходный код Framework.