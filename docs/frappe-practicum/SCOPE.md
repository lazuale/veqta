# Границы базовых практикумов

## Цель

Базовая программа показывает Frappe Framework 16 как платформу приложений, а не как набор форм и не как искусственно урезанный no-code конструктор.

Весь курс развивается вокруг **одного app `facility_ops`**. Мы работаем в Developer Mode, используем штатные механизмы Frappe и постепенно собираем небольшую систему службы эксплуатации.

Собственная бизнес-логика на Python или JavaScript начинается только на следующем уровне обучения, когда появляется задача, которую штатная конфигурация уже не решает.

## Проверенная версия

Основная версия курса — **Frappe Framework v16.32.0**.

Порядок проверки спорных мест:

1. фактический стенд на v16.32.0;
2. исходники тега `v16.32.0`;
3. официальная документация Frappe;
4. ветка `version-16` — только для будущих изменений.

Курс не должен ссылаться на поведение, отсутствующее в v16.32.0.

## Учебный продукт

Техническая база:

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Основные DocType:

```text
Facility Location (Tree)
Equipment Type
Equipment
Equipment Movement
Equipment Movement Item (Child)
Service Request
Inspection
Maintenance Work
```

Этого достаточно для базового курса. Новая сущность не добавляется только потому, что во Frappe существует ещё одна функция.

## Что входит в базовую программу

### Среда и приложение

- Bench на уровне, необходимом для работы с приложением;
- site;
- `bench new-app`;
- установка app на site;
- Developer Mode;
- default Module;
- структура app;
- `hooks.py` как штатная точка конфигурации;
- Git;
- Desk v16, Workspace Sidebar, Apps Page, Awesomebar / command palette;
- scheduler и background workers;
- установка app на чистые sites.

`hooks.py` не изучается как Python-программирование. В базовой программе он нужен для штатной конфигурации, прежде всего fixtures.

### Модель данных

- DocType, DocField, Document и `name`;
- Standard DocType своего app;
- Child DocType;
- Tree DocType;
- Single DocType — дополнительной лабораторией;
- Custom DocType — дополнительным site-specific сценарием;
- основные Field Types;
- дополнительные Field Types короткими лабораториями;
- Link;
- Dynamic Link только при реальной необходимости;
- Table и Table MultiSelect;
- Section / Column / Tab Break;
- Naming;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Track Seen / Track Views как дополнительные настройки;
- Allow Import;
- Allow Auto Repeat;
- Default Sort;
- Preview;
- DocType Links / Actions при естественной задаче.

### Кастомизация и переносимость

- Customize Form;
- Custom Field;
- Property Setter;
- DocType Layout;
- Standard / Custom / Customized;
- Export Customizations;
- fixtures только после появления реальной конфигурации;
- `bench export-fixtures`;
- `bench migrate`;
- Git diff;
- первый clean-site test в P4;
- финальный clean-site test в P8.

Главное правило: не всё, что создано в Desk, автоматически является частью app.

### Работа с данными и интерфейсом

- Form View;
- List View;
- filters и sorting;
- Saved Filters;
- mass actions;
- Data Import и Export;
- attachments;
- comments;
- Timeline;
- Tags;
- Kanban;
- Calendar;
- Workspace;
- Shortcuts;
- Quick Lists;
- Gantt как дополнительное представление, если модель дат действительно подходит.

### Пользователи и права

- User;
- System User и Website User;
- Guest, All, Administrator, Desk User;
- Role;
- Role Permission Manager;
- Select;
- Read / Write / Create / Delete;
- Submit / Cancel / Amend;
- Report / Export / Import;
- Share / Print / Email;
- If Owner;
- Permission Level;
- User Permission;
- Mask / Data Masking как дополнительная экспериментальная возможность;
- ограничения Page / Report / Workspace на базовом уровне.

Права проверяются реальным входом под учебными пользователями. Проверка под `Administrator` не считается.

### Совместная работа

- Assign To;
- ToDo;
- Due Date;
- Priority;
- Comments;
- Timeline;
- персональная очередь работы.

### Жизненный цикл и Workflow

- обычное предметное состояние;
- Is Submittable;
- Draft / Submit / Cancel / Amend;
- DocStatus;
- Allow on Submit;
- Audit Trail;
- Workflow;
- Workflow State;
- Workflow Action Master;
- Workflow Transition;
- allowed role;
- Workflow Action record;
- простые transition conditions.

Курс обязан разводить `Status`, `Workflow State` и `DocStatus` как разные понятия.

### Аналитика и печать

- Report Builder;
- filters;
- Group By;
- Count / Sum / Average;
- Number Card;
- Dashboard Chart;
- Workspace;
- Print View;
- Print Format Builder;
- Letter Head;
- PDF.

### Автоматизация

- Notification;
- System Notification;
- Notification Filters;
- date-based Notification;
- Auto Repeat;
- Assignment Rule;
- один основной алгоритм распределения;
- сравнение остальных алгоритмов;
- простые встроенные PythonExpression там, где их требует штатный механизм;
- scheduler/background jobs на уровне пользователя.

### Web

- Web Form;
- Route;
- Anonymous responses;
- Login Required;
- Website User;
- Apply document permissions;
- Allow editing after submit;
- Allow multiple responses;
- Show list;
- attachments;
- comments и print как дополнительные настройки;
- Web Form Request / Key required как дополнительный сценарий;
- Standard Web Form в Developer Mode и его файлы в app.

## Что не требуется для завершения базовой программы

- собственные Python controllers с бизнес-логикой;
- собственные server-side hooks с бизнес-логикой;
- собственный JavaScript;
- Client Script;
- Server Script;
- собственные whitelisted methods;
- Custom Permission Types;
- REST API и Webhooks;
- Query Report;
- Script Report;
- ручные Jinja-шаблоны;
- собственные Website / Portal Pages;
- Virtual DocType;
- внешние библиотеки;
- сторонние приложения.

Это не запрет на Frappe. Это граница базового уровня.

## Как работаем со штатными выражениями

Если сам Frappe предлагает expression field, его можно использовать.

Например `Assignment Rule` v16.32.0 использует `PythonExpression` для условия.

Практикум в таком случае:

1. объясняет назначение поля;
2. использует минимальное понятное выражение;
3. показывает результат;
4. не превращается в урок Python.

## Что считается частью app

Перед каждым commit ученик должен определить тип изменения.

### Standard metadata

Создано в Developer Mode внутри Module `Facility Operations` и штатно хранится в файлах `facility_ops`.

### Site-specific customization

Custom Field, Property Setter и подобные изменения конкретного site. Для включения принятой кастомизации в app используется Export Customizations.

### Конфигурационная запись базы данных

Например Role или Workflow. Fixture используется только если запись действительно необходима для воспроизводимости приложения.

### Рабочие данные

Equipment, Service Request, Inspection, Maintenance Work и другие конкретные рабочие документы не превращаются в fixtures ради переноса тестовых данных.

## Проверка переносимости

Переносимость проверяется дважды.

### P4

Первый технический контроль после появления Standard metadata, Export Customizations, Roles, Workflow и fixtures.

### P8

Полная установка приложения на новый чистый site и сквозная приёмка.

Минимальный принцип:

```text
clean compatible Frappe site
+ facility_ops
+ install-app
+ migrate
= принятая конфигурация без повторного ручного накликивания
```

## Правило отбора тем

Тема входит в обязательную программу, если одновременно:

1. это штатная возможность Frappe v16.32.0;
2. она решает понятную задачу `facility_ops`;
3. её можно воспроизвести и проверить;
4. ради неё не приходится портить предметную модель.

Если функция нужна только для строки в матрице, она остаётся дополнительной лабораторией.

Список официальных источников и проверяемых исходников находится в [REFERENCES.md](REFERENCES.md).
