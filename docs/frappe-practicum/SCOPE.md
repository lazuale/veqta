# Что входит в базовые практикумы

Цель программы — изучить Frappe Framework 16 нативно, через сборку рабочих проектов.

Мы не делим Frappe на «можно непрограммисту» и «нельзя непрограммисту». Если механизм является штатной частью Frappe и естественно решает задачу практикума, его можно использовать.

При этом базовые практикумы не превращаются в курс разработки собственной бизнес-логики. App, Developer Mode, Module и стандартные DocType — нормальная часть Frappe. Ручное написание Python-контроллеров, JavaScript и интеграционного кода — уже следующая ступень.

## Базовая среда

Все практикумы выполняются на:

- Frappe Framework v16;
- проверенной базовой версии v16.32.0;
- отдельном учебном site;
- отдельном учебном Frappe app;
- Developer Mode;
- стандартном Desk и Website;
- штатных scheduler/background workers.

ERPNext и другие приложения не являются обязательной зависимостью программы.

## Что изучаем нативно

### Среда и структура приложения

- Bench на пользовательском уровне;
- site;
- app;
- `bench new-app`;
- `install-app`;
- Developer Mode;
- Module;
- структура app;
- Git;
- JSON-метаданные DocType и других объектов на уровне понимания, без ручного редактирования.

### Модель данных

- стандартный DocType приложения;
- Custom DocType как отдельный штатный механизм и отличие от стандартного DocType;
- Child DocType;
- Single DocType;
- основные и дополнительные Field Types;
- Link;
- Dynamic Link;
- Table;
- Table MultiSelect;
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
- Tree и Calendar/Gantt support как отдельные штатные возможности, если для них есть естественный сценарий.

### Изменение существующих DocType

- Customize Form;
- Custom Field;
- Property Setter;
- site-specific изменение полей и свойств;
- отличие Customize Form от редактирования стандартного DocType своего app в Developer Mode.

### Работа с данными

- Form View;
- List View;
- фильтры;
- сортировка;
- saved filters;
- массовые операции;
- импорт;
- экспорт;
- вложения;
- комментарии;
- Timeline;
- Tags;
- Kanban;
- Calendar;
- другие штатные представления, если их поддерживает конкретный DocType.

### Пользователи и права

- User;
- Role;
- Role Permission Manager;
- Create / Read / Write / Delete;
- Submit / Cancel;
- Print / Export / Import permissions;
- If Owner;
- Permission Level;
- User Permission;
- Share;
- ограничения Workspace.

### Совместная работа

- Assign To;
- ToDo;
- Due Date;
- Priority;
- Comments;
- Timeline;
- персональная очередь работы.

### Жизненный цикл и Workflow

- Status как обычное поле предметной модели;
- Is Submittable;
- Draft / Submit / Cancel / Amend;
- DocStatus;
- Workflow;
- Workflow State;
- Workflow Action Master;
- Workflow Transition;
- роли переходов;
- Workflow Action как рабочая запись ожидающего/выполненного действия;
- простые условия переходов штатным способом.

### Аналитика и рабочие экраны

- Report Builder;
- фильтры;
- Group By;
- Count / Sum / Average;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcuts;
- Quick Lists.

### Печать

- Print View;
- Print Format Builder;
- Letter Head;
- PDF;
- выбор полей и штатные параметры печати.

### Автоматизация

- Notification;
- System Notification;
- Filters-условия Notification;
- Auto Repeat;
- Assignee в Auto Repeat;
- Assignment Rule;
- Round Robin;
- Load Balancing;
- Based on Field;
- Weighted Distribution;
- встроенные простые выражения механизма Assignment Rule;
- scheduler/background jobs на уровне понимания их роли.

### Web

- Web Form;
- Route;
- Anonymous responses;
- Login Required;
- Apply document permissions;
- Allow editing after submit;
- Allow multiple responses;
- Allow delete;
- Show list;
- Attachments;
- Comments;
- Print;
- Web Form Request / Key required как дополнительный сценарий.

## Что не является запретом, но не входит в обязательную базу

Следующие вещи существуют в Frappe и могут изучаться позже, когда без них появится реальная задача:

- ручное написание Python-контроллеров;
- редактирование `hooks.py`;
- собственный JavaScript;
- Client Script;
- Server Script;
- собственные whitelisted methods;
- REST API и Webhooks;
- Query Report;
- Script Report;
- ручные Jinja-шаблоны;
- собственные Website/Portal Pages;
- Virtual DocType;
- внешние библиотеки;
- сторонние приложения.

Они не «запрещены во Frappe». Просто базовые проекты не должны требовать их для работы.

## Как относимся к выражениям внутри штатных механизмов

Если Frappe сам предоставляет поле для простого выражения, его можно использовать.

Пример: `Assignment Rule` в v16 требует `Assign Condition` с типом `PythonExpression`. Это часть самого штатного механизма, а не отдельный Python-модуль.

В таких местах практикум:

1. объясняет, зачем нужно выражение;
2. использует минимальный понятный пример;
3. не превращается в урок языка Python;
4. не скрывает от ученика реальное устройство механизма.

## Стандартный DocType и Custom DocType

В курсе важно увидеть оба сценария.

### Стандартный DocType приложения

Создаётся в Developer Mode и принадлежит учебному app. Его метаданные попадают в репозиторий приложения.

Это основной способ создания предметной модели курса.

### Custom DocType

Создаётся как site-specific объект и может существовать без Developer Mode.

Он изучается, чтобы понимать возможности платформы, но не используется как единственный способ построения курса.

### Customize Form

Используется, когда нужно штатно изменить уже существующий DocType на конкретном site без правки его исходного определения.

Ученик должен чётко различать все три сценария.

## Правило отбора тем

Тема входит в обязательную программу, если:

1. это штатный механизм Frappe v16;
2. для него есть понятная практическая задача;
3. он помогает понять архитектуру или повседневную работу Frappe;
4. его можно воспроизвести на учебном стенде.

Не нужно использовать каждую настройку в основном сценарии. Редкие, но базовые возможности можно вынести в короткие дополнительные упражнения.

## На что опираемся при проверке

При споре приоритет такой:

1. фактическое поведение проверенной версии Frappe v16;
2. исходники ветки `version-16` в `frappe/frappe`;
3. официальная документация Frappe;
4. только после этого — сторонние статьи и примеры.

Ключевые исходники для этой программы находятся, в частности, в:

- `frappe/core/doctype/doctype/`;
- `frappe/custom/doctype/customize_form/`;
- `frappe/workflow/doctype/`;
- `frappe/automation/doctype/`;
- `frappe/email/doctype/notification/`;
- `frappe/desk/doctype/workspace/`;
- `frappe/desk/doctype/number_card/`;
- `frappe/desk/doctype/dashboard_chart/`;
- `frappe/website/doctype/web_form/`.

Главный критерий простой: практикум должен показывать Frappe таким, какой он есть, а не искусственно урезанную версию платформы.