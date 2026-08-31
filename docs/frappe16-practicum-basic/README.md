# Frappe Framework 16 — базовый практикум

## Статус

Согласованная базовая траектория обучения Frappe Framework 16.

Этот каталог заменяет концепцию «книги/справочника» отдельным последовательным практикумом. Старый каталог `docs/frappe16-course` сохраняется как предыдущая версия материала и не является источником структуры нового практикума.

## Цель

Провести человека без опыта работы с Frappe от чистого стенда до законченной рабочей системы, построенной штатными средствами Frappe 16 без программирования.

Практикум строится вокруг одного сквозного учебного проекта — системы управления работой. Каждая следующая работа расширяет уже существующую систему и использует только знания предыдущих этапов.

## Главный принцип

> Не изучаем возможности Frappe по отдельности. Строим одну систему и вводим новую возможность только тогда, когда она становится нужна проекту.

Последовательность:

```text
чистая система
    ↓
Frappe Site
    ↓
Custom DocType
    ↓
связанная модель данных
    ↓
представления и Workspace
    ↓
пользователи и права
    ↓
совместная работа
    ↓
Workflow и автоматизация
    ↓
импорт, отчёты и Dashboard
    ↓
печать и Email
    ↓
Web Form
    ↓
штатный REST API
    ↓
backup / restore
    ↓
законченная рабочая система
```

## Граница базового уровня

### Входит

- установка и базовое администрирование учебного Frappe 16;
- Bench и Site на уровне, необходимом пользователю практикума;
- Desk и системные настройки;
- Custom DocType и Document;
- DocField и штатные типы полей;
- naming, title и search;
- Link, Fetch From, Dynamic Link;
- Child DocType и Table;
- Single DocType;
- Tree DocType;
- Attachments / File;
- Submit / Cancel / Amend;
- Track Changes / Version / Timeline;
- List, Report, Kanban, Calendar, Gantt и Tree views там, где они применимы;
- Workspace;
- Users, Roles и Role Profile;
- Role Permissions, Permission Level, If Owner, User Permission и Share;
- Assign и ToDo;
- Assignment Rule;
- Workflow и Workflow Actions;
- Notification;
- Auto Repeat;
- Customize Form, Custom Field, Property Setter, Custom DocPerm и Custom Link;
- Data Import / Data Export;
- Report Builder;
- Number Card, Dashboard Chart и Dashboard/Workspace analytics;
- стандартная печать и Print Format Builder;
- Email Account, Communication и Email Queue;
- Web Form и Website User;
- автоматически предоставляемый REST API;
- backup и restore.

### Не входит

Базовый уровень сознательно не содержит программирования и developer-level расширений:

- Python controllers;
- Python Document API;
- Database API и Query Builder;
- raw SQL;
- hooks;
- Server Script;
- Client Script;
- JavaScript Form Script;
- Query Report;
- Script Report;
- собственные API methods;
- собственные background jobs и scheduler handlers;
- Custom Desk Page;
- ручной Jinja/HTML-код как способ разработки;
- Virtual DocType / Virtual DocField;
- Document Queue;
- Packages;
- Data Migration Tool;
- разработка собственного Frappe App.

Это отдельный следующий уровень: **Frappe 16 Development**.

## Сквозной учебный проект

К концу базового практикума формируется примерно такая модель:

```text
Project
│
├── Work Item
│   ├── Project
│   ├── Category
│   ├── Status
│   ├── Priority
│   ├── Responsible
│   ├── Due Date
│   ├── Description
│   ├── Checklist
│   └── Files
│
├── Category
│
├── Work Item Step
│   └── Child DocType
│
└── Practicum Settings
    └── Single DocType
```

Поверх модели последовательно появляются пользователи, права, назначения, Workflow, уведомления, отчётность, Dashboard, печать, Email, Web Form и REST API.

## Структура каталога

- [`MATRIX.md`](MATRIX.md) — финальная матрица практических работ и покрытия возможностей Frappe 16.
- [`ROADMAP.md`](ROADMAP.md) — последовательность развития проекта по фазам.
- [`labs/`](labs/) — будущие пошаговые практические работы.

## Формат каждой практической работы

Каждая работа должна иметь один и тот же каркас:

1. Где мы сейчас.
2. Что хотим получить.
3. Минимальное объяснение нового механизма.
4. Пошаговые действия.
5. Реальные тестовые данные.
6. Проверка штатного поведения.
7. Намеренное изменение или ошибка.
8. Объяснение причины полученного результата.
9. Возврат правильной конфигурации.
10. Контрольный сценарий.
11. Состояние проекта после работы.

Теория добавляется только там, где без неё невозможно понять следующий практический шаг.

## Критерий завершения базового уровня

После практикума ученик на чистом Frappe Site без Python, JavaScript и SQL должен самостоятельно уметь:

1. создать модель из нескольких связанных DocTypes;
2. построить формы и представления;
3. собрать Workspace;
4. создать пользователей и роли;
5. разграничить права;
6. организовать назначения и совместную работу;
7. построить Workflow;
8. настроить штатные уведомления и повторяемую работу;
9. импортировать и экспортировать данные;
10. сделать отчёты и Dashboard;
11. подготовить печатный документ;
12. работать с Email;
13. открыть внешний сценарий через Web Form;
14. работать с теми же документами через штатный REST API;
15. сделать backup и восстановить Site;
16. пройти полный сквозной сценарий после восстановления.

Если это выполнено, базовый уровень Frappe 16 считается завершённым.
