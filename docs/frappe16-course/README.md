# Frappe Framework 16 — учебный курс для VEQTA

Этот каталог — учебник по **Frappe Framework 16 с нуля**. Его задача — дать системное понимание штатных возможностей Framework до того, как мы начнём добавлять собственные механизмы в VEQTA.

> Главный вопрос курса: **это действительно нужно реализовать в VEQTA или Frappe уже умеет это штатно?**

## Статус и границы

- Целевая версия: **Frappe Framework 16**.
- Актуальность курса проверяется по официальной документации и исходному коду Frappe.
- ERPNext, Frappe CRM, Helpdesk, HRMS и другие приложения **не считаются частью Framework** и рассматриваются только если это явно указано.
- Старые материалы по v14/v15 используются только для общих концепций, если они подтверждены для v16.
- Этот каталог — **учебный материал**, а не спецификация VEQTA. Продуктовые решения остаются в `docs/DECISIONS.md`, `docs/MODEL_V0_1.md` и других документах проекта.

Проверено: **2026-08-30**.

## Как проходить курс

Курс идёт от устройства платформы к практике и только затем к коду. Не перескакиваем сразу в Python: сначала проверяем, что можно решить штатной конфигурацией Frappe.

Для каждого механизма фиксируем четыре вещи:

1. **Что это такое.**
2. **Что Frappe делает сам.**
3. **Где граница штатной возможности.**
4. **Когда действительно нужен код VEQTA.**

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
   только если штатного Desk действительно недостаточно
```

## Программа

### Блок A. Карта Frappe

1. [Архитектура: Bench → Site → App → Module → DocType → Document](01_FOUNDATIONS.md)
2. Desk, Desktop, Sidebar, Workspace и навигация v16
3. Что входит в чистый Framework, а что является отдельным приложением

### Блок B. Модель данных

4. DocType от А до Я
5. DocField и свойства полей
6. Naming и `name`
7. Link, Dynamic Link и Fetch From
8. Child Table и Table MultiSelect
9. Single, Tree, Submittable и Virtual DocType
10. `docstatus`, Submit, Cancel и Amendment

### Блок C. Интерфейс без собственного frontend

11. Form View
12. List View и фильтры
13. Kanban, Calendar, Gantt и Tree View
14. Workspace, Shortcut, Quick List, Number Card и Chart
15. Customize Form

### Блок D. Пользователи и права

16. User и Role
17. Role Permission Manager
18. Permission Level
19. User Permission
20. Owner и Sharing
21. Где заканчиваются штатные permissions

### Блок E. Работа и процессы

22. Assignment и ToDo
23. Assignment Rule
24. Status против Workflow State
25. Workflow и переходы
26. Notification
27. Auto Repeat

### Блок F. Системные сервисы документа

28. Timeline и Comments
29. Version и Track Changes
30. Attachments и File
31. Email / Communication
32. Print Format и PDF

### Блок G. Данные и аналитика

33. Report Builder
34. Query Report
35. Script Report
36. Dashboard Chart и Number Card
37. Data Import / Export

### Блок H. Внешние интерфейсы

38. Web Form
39. Portal / website-возможности Framework
40. REST API
41. RPC и whitelisted methods
42. Authentication для интеграций

### Блок I. Low-code и разработка

43. Client Script
44. Server Script
45. Standard vs Custom
46. Developer Mode
47. Собственное App
48. Standard DocType и файлы приложения
49. Python controller и lifecycle документа
50. Hooks

### Блок J. Фоновая и серверная инфраструктура

51. ORM и Database API
52. Background Jobs и очереди
53. Scheduler
54. Realtime
55. Fixtures
56. Patches и migrations
57. Tests

### Блок K. Bench и эксплуатация

58. Bench и Bench CLI
59. Site configuration
60. Установка и обновление Apps
61. `bench migrate`
62. Workers, scheduler, Redis/Valkey и web processes
63. Logs и диагностика
64. Backup и restore
65. Production deployment — что обязан понимать разработчик приложения

### Блок L. Итоговая практика

66. Создаём учебное приложение с нуля
67. Проверяем каждый штатный механизм руками
68. Выносим принятую конфигурацию в Git
69. Устанавливаем приложение на чистый Site и воспроизводим состояние
70. Составляем карту: **Frappe штатно / VEQTA должна реализовать**

## Правило курса для VEQTA

Перед созданием любой общей сущности или инфраструктурного механизма задаём вопросы по порядку:

```text
1. Frappe уже хранит этот факт?
2. Frappe уже предоставляет такой UI?
3. Frappe уже имеет permission/automation/reporting механизм?
4. Можно ли закрыть задачу настройкой Framework?
5. Если нет — чего конкретно не хватает?
6. Только этот подтверждённый недостаток становится кандидатом на код VEQTA.
```

Это не запрет на разработку. Это защита от создания второго framework поверх Frappe.

## Основные официальные источники

- [Frappe Framework — Introduction](https://docs.frappe.io/framework/user/en/introduction)
- [Bench](https://docs.frappe.io/framework/user/en/bench)
- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [REST API](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [Migration guide for Version 16](https://github.com/frappe/frappe/wiki/Migrating-to-version-16)

По мере прохождения курса конкретные главы будут содержать свои ссылки на официальную документацию и исходный код.