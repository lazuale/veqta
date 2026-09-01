# Границы базового практикума

## Цель

Базовый курс показывает Frappe Framework 16 как платформу приложений.

Весь курс развивается вокруг одного app `facility_ops` и одной минимальной модели:

```text
Facility Location
      │
      ├────────► Equipment
      │             │
      └─────────────┴────────► Service Request
```

Собственная бизнес-логика на Python или JavaScript в базовом курсе не требуется.

## Проверенная версия

Основная версия — **Frappe Framework v16.32.0**.

Приоритет проверки:

1. фактический стенд v16.32.0;
2. исходники тега `v16.32.0`;
3. официальная документация Frappe;
4. `version-16` только для будущих изменений.

## Учебный стенд

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

## Ядро приложения

Только три обязательных DocType:

```text
Facility Location
Equipment
Service Request
```

Новая бизнес-сущность не создаётся только ради изучения отдельной функции Frappe.

## Что входит в основной маршрут

### Среда

- Bench;
- Site;
- App;
- Module;
- Developer Mode;
- структура app;
- `hooks.py`;
- Git;
- Desk;
- scheduler / workers.

### Модель данных

- DocType;
- DocField;
- Document;
- `name`;
- Standard DocType;
- Tree DocType;
- основные Field Types;
- Link;
- Naming;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Form / List / Tree View;
- Data Import / Export.

### Работа с данными

- Filters;
- Sorting;
- Saved Filters;
- Search;
- Mass actions;
- Attachments;
- Timeline.

### Пользователи и права

- User;
- System User;
- Website User;
- Guest;
- Role;
- Role Permission Manager;
- основные permission flags;
- If Owner;
- Permission Level;
- User Permission;
- Share.

Права проверяются входом под обычными учебными пользователями, а не под Administrator.

### Совместная работа

- Assign To;
- ToDo;
- Due Date;
- Comments;
- Timeline;
- Tags;
- Kanban.

### Workflow

- обычный Status;
- Workflow;
- Workflow State;
- Workflow Transition;
- Allowed Role;
- Workflow Action;
- простые transition conditions.

Workflow изучается после ручного изменения Status.

### Аналитика и рабочий интерфейс

- Report Builder;
- filters;
- Group By;
- Count / Sum / Average;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcut;
- Quick List;
- Workspace access.

### Автоматизация

- Notification;
- System Notification;
- Notification Filters;
- date-based Notification;
- Assignment Rule;
- один основной алгоритм распределения;
- сравнение остальных алгоритмов;
- минимальный PythonExpression только там, где его предоставляет сам штатный механизм;
- scheduler/background jobs.

### Web

- Web Form;
- Route;
- Anonymous;
- Login Required;
- Guest;
- Website User;
- document permissions;
- attachments;
- Show List / editing там, где это подходит сценарию;
- Standard Web Form.

### Поставка приложения

- Standard metadata;
- configuration records;
- fixtures;
- `bench export-fixtures`;
- Export Customizations;
- `install-app`;
- `bench migrate`;
- clean site.

Главный результат — ученик понимает, что рабочие Documents и конфигурация приложения являются разными вещами.

## Что изучается лабораториями

Специальные механизмы не расширяют ядро приложения.

### Lab A

Child DocType / Table.

### Lab B

- Is Submittable;
- Draft / Submit / Cancel / Amend;
- DocStatus;
- Allow on Submit;
- Audit Trail.

### Lab C

- Allow Auto Repeat;
- Auto Repeat;
- Auto Repeat Assignee.

### Lab D

- Customize Form;
- Custom Field;
- Property Setter;
- DocType Layout;
- Export Customizations.

### Lab E

- Print View;
- Print Format Builder;
- Letter Head;
- PDF.

### Lab F

- Single DocType;
- Dynamic Link;
- Table MultiSelect;
- дополнительные Field Types;
- Calendar;
- Gantt;
- Barcode;
- Signature;
- Geolocation;
- Attachment Gallery;
- Data Masking и другие специальные возможности базового уровня.

Лабораторный объект может быть удалён после упражнения.

## Что остаётся на следующем уровне

- собственные Python controllers с бизнес-логикой;
- собственные server-side hooks с бизнес-логикой;
- JavaScript / Client Script;
- Server Script;
- whitelisted methods;
- REST API / Webhooks;
- Query Report / Script Report;
- ручные Jinja templates;
- собственные Website / Portal Pages;
- Virtual DocType;
- сторонние библиотеки и apps;
- Custom Permission Types, требующие собственного кода.

## Что считается частью app

### Standard metadata

Создано в Developer Mode внутри Module приложения и хранится в файлах `facility_ops`.

### Site-specific customization

Custom Field, Property Setter и другие изменения конкретного site.

Они не считаются поставляемой частью app, пока не экспортированы штатным способом.

### Configuration record

Например Role, Workflow, Notification или Assignment Rule.

Fixture используется только если запись действительно нужна для воспроизводимости приложения.

### Working data

Конкретные Facility Location, Equipment и Service Request — рабочие Documents.

Они не превращаются в fixtures ради переноса тестового содержимого.

## Проверка переносимости

Финальный основной урок создаёт новый чистый site.

```text
clean Frappe site
+ facility_ops
+ install-app
+ migrate
= рабочая конфигурация приложения
```

На новом site должна восстановиться конфигурация приложения, но не тестовые рабочие данные.

## Правило отбора тем

Тема входит в основной маршрут, если одновременно:

1. это штатная возможность Frappe v16.32.0;
2. она нужна трём основным DocType или основному процессу;
3. её можно воспроизвести и проверить;
4. ради неё не приходится создавать лишнюю бизнес-сущность.

В остальных случаях тема идёт в Lab или на следующий уровень.

Список источников находится в [REFERENCES.md](REFERENCES.md).
