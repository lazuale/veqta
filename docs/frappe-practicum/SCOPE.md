# Границы базовых практикумов

## Цель

Базовая программа показывает Frappe Framework 16 как настоящую платформу приложений, а не как набор форм и не как искусственно урезанный no-code конструктор.

Мы создаём собственный app, работаем в Developer Mode и используем штатные механизмы Frappe. Собственная бизнес-логика на Python или JavaScript начинается позже, когда появляется задача, которую штатная конфигурация уже не решает.

## Проверенная версия

Основная версия курса — **Frappe Framework v16.32.0**.

Порядок проверки спорных мест:

1. стенд на v16.32.0;
2. исходники тега `v16.32.0`;
3. официальная документация Frappe;
4. ветка `version-16` — только для проверки будущих изменений.

Курс не должен ссылаться на поведение, которое есть только в более свежей ветке и отсутствует в v16.32.0.

## Что входит в базовую программу

### Среда и приложение

- Bench на уровне, необходимом для работы с приложением;
- site;
- `bench new-app`;
- установка app на site;
- Developer Mode;
- default Module, созданный вместе с app;
- структура app;
- `hooks.py` как штатная точка конфигурации приложения;
- Git;
- Desk v16, Workspace Sidebar, Apps Page, Awesomebar/command palette;
- scheduler и background workers на уровне понимания и проверки;
- установка app на второй чистый site.

`hooks.py` не изучается как Python-программирование. В базовой программе он нужен для простых штатных настроек, прежде всего fixtures. Дополнительные hooks показываются только при реальной необходимости.

### Модель данных

- DocType, DocField, Document и `name`;
- стандартный DocType своего app;
- Child DocType;
- Tree DocType;
- Single DocType — как дополнительный сценарий, если основной проект не требует глобальных настроек;
- Custom DocType — как отдельный site-specific сценарий;
- основные Field Types;
- дополнительные Field Types короткими лабораторными упражнениями;
- Link;
- Dynamic Link — только там, где одна ссылка действительно может вести на разные DocType;
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
- DocType Links / Actions, когда они нужны модели.

### Кастомизация и переносимость

- Customize Form;
- Custom Field;
- Property Setter;
- DocType Layout;
- отличие Standard DocType / Custom DocType / Customize Form;
- Export Customizations;
- fixtures;
- `bench export-fixtures`;
- `bench migrate`;
- проверка файлов app через Git diff;
- установка app на второй site и проверка, что нужная конфигурация приехала.

Главное правило: ученик должен понимать, что не всё созданное в Desk автоматически становится частью app.

### Работа с данными и интерфейсом

- Form View;
- List View;
- фильтры и сортировка;
- Saved Filters;
- массовые действия;
- import/export;
- attachments;
- comments;
- Timeline;
- Tags;
- Kanban;
- Calendar;
- Workspace;
- Shortcuts;
- Quick Lists;
- Gantt как дополнительное представление там, где модель дат действительно подходит.

### Пользователи и права

- User;
- System User и Website User;
- автоматические роли Guest, All, Administrator, Desk User;
- Role;
- Role Permission Manager;
- Read / Write / Create / Delete;
- Submit / Cancel / Amend;
- Report / Export / Import;
- Set User Permissions;
- Share / Print / Email;
- If Owner;
- Permission Level;
- User Permission;
- ограничения страниц, отчётов и Workspace на уровне базовой практики.

Не каждая галка должна получить отдельный сценарий, но ученик должен увидеть полную строку стандартных прав и понимать назначение основных флагов.

### Совместная работа

- Assign To;
- ToDo;
- Due Date;
- Priority;
- Comments;
- Timeline;
- персональная очередь задач.

### Жизненный цикл и Workflow

- обычное поле Status;
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
- Workflow Action как фактическая запись действия;
- простые штатные условия переходов.

### Аналитика и печать

- Report Builder;
- фильтры;
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
- Filters в Notification;
- Auto Repeat;
- Assignment Rule;
- один основной алгоритм распределения в рабочем сценарии;
- сравнение Round Robin, Load Balancing, Based on Field и Weighted Distribution;
- простые встроенные PythonExpression там, где их требует сам механизм;
- scheduler/background jobs на уровне пользователя.

### Web

- Web Form;
- Route;
- Anonymous responses;
- Login Required;
- Apply document permissions;
- Allow editing after submit;
- Allow multiple responses;
- Show list;
- attachments;
- comments и print как дополнительные настройки;
- Web Form Request / Key required как дополнительный сценарий;
- Standard Web Form в Developer Mode и его файлы в app.

## Что не требуется для завершения базовой программы

Эти механизмы существуют во Frappe, но базовые проекты не должны зависеть от них:

- собственные Python controllers;
- собственные server-side hooks с бизнес-логикой;
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

Это не запрет. Это следующий уровень обучения.

## Как работаем со штатными выражениями

Если сам Frappe предлагает поле для выражения, его можно использовать.

Пример: `Assignment Rule` v16.32.0 требует `Assign Condition` с типом `PythonExpression`.

В таком случае практикум:

1. объясняет назначение поля;
2. использует минимальное понятное выражение;
3. показывает результат;
4. не превращается в урок Python.

## Что считается частью app

Перед каждым коммитом ученик должен уметь ответить, к какому типу относится созданный объект:

### Стандартный объект приложения

Создан в Developer Mode, относится к Module приложения и хранится в файлах app штатным способом.

### Site-specific customization

Например, Custom Field и Property Setter. Для переноса используется Export Customizations.

### Запись базы данных, нужная приложению

Например, выбранные роли или другие конфигурационные записи. Для таких случаев используются fixtures, если они действительно должны поставляться вместе с app.

Не следует экспортировать в fixtures всё подряд. В app попадает только та конфигурация, без которой приложение не воспроизводится на новом site.

## Проверка переносимости

Базовая программа не считается пройденной, если приложение работает только на исходном учебном site.

Минимальная проверка:

1. сохранить изменения app в Git;
2. создать второй чистый site;
3. установить app;
4. выполнить migrate;
5. проверить модель данных, кастомизации, необходимые роли/настройки, Workspace, Workflow и Web Form;
6. исправить всё, что осталось только на первом site.

## Правило отбора тем

Тема входит в обязательную программу, если одновременно выполняются три условия:

1. это штатная возможность Frappe v16.32.0;
2. она решает понятную задачу проекта;
3. её можно воспроизвести и проверить на учебном стенде.

Если функция нужна только ради строки в матрице, она переносится в дополнительное упражнение.

Список официальных источников и проверяемых исходников находится в [REFERENCES.md](REFERENCES.md).