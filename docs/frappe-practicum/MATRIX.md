# Матрица практикумов

Матрица нужна для контроля полноты. Она не заменяет дорожную карту и не пересказывает проекты.

Обозначения:

- **Основное** — механизм обязателен для прохождения проекта;
- **Доп.** — короткое упражнение или обзор;
- **Позже** — сознательно вынесено за пределы базовой программы.

## Проекты

| Код | Проект | Главная тема |
|---|---|---|
| P0 | Учебное приложение | устройство Frappe и app |
| P1 | Реестр оборудования | модель данных |
| P2 | Кастомизация и переносимость | site-specific изменения и упаковка app |
| P3 | Внутренние заявки | пользователи, права, назначения |
| P4 | Согласование закупки | жизненный цикл и Workflow |
| P5 | Журнал проверок | отчёты, Workspace, печать |
| P6 | Регламентные работы | автоматизация |
| P7 | Web Form обращений | внешний интерфейс |
| P8 | Операционный центр | самостоятельная сборка и перенос |

## Среда и приложение

| Механизм | Впервые | Статус | Зачем |
|---|---:|---|---|
| Bench | P0 | Основное | понять рабочее окружение |
| App | P0 | Основное | основная единица поставки функциональности |
| Site | P0 | Основное | понять отдельный экземпляр Frappe |
| `bench new-app` | P0 | Основное | создать настоящий app |
| `install-app` / `list-apps` | P0 | Основное | связать app и site |
| Developer Mode | P0 | Основное | создавать стандартные объекты app |
| модуль, созданный вместе с app | P0 | Основное | понять организацию объектов внутри app |
| структура app | P0 | Основное | видеть связь Desk и файлов |
| `hooks.py` | P0/P2 | Основное | понять штатную конфигурацию; в P2 добавить fixtures |
| Git diff / commit | P0 | Основное | видеть, что реально попало в app |
| Desk v16 / Workspace Sidebar | P0 | Основное | освоить актуальную навигацию |
| Awesomebar / command palette | P0 | Основное | быстро находить объекты и команды |
| scheduler / workers | P0 | Основное | проверить среду для будущей автоматизации |
| Apps Page / `add_to_apps_screen` | P0/P2 | Доп. | показать место app в интерфейсе и hook при необходимости |

## Модель данных

| Механизм | Впервые | Статус | Зачем |
|---|---:|---|---|
| DocType / DocField / Document / `name` | P1 | Основное | понять фундаментальную модель Frappe |
| Standard DocType своего app | P1 | Основное | строить предметную модель в app |
| Child DocType / Table | P1 | Основное | повторяющиеся строки документа |
| Tree DocType | P1 | Основное | иерархия мест размещения |
| Single DocType | P1 | Доп. | увидеть модель одной глобальной записи |
| Custom DocType | P2 | Доп. | понять site-specific DocType |
| Form Builder | P1 | Основное | собирать форму нативно |
| Naming | P1 | Основное | управлять `name` документов |
| By fieldname | P1 | Основное | именовать справочник |
| Expression / Naming Series | P1 | Основное | именовать рабочий документ |
| Random / UUID / другие способы | P1 | Доп. | понимать доступную палитру Naming |
| Title Field | P1 | Основное | отображать понятное название документа |
| Search Fields | P1 | Основное | улучшить поиск документов |
| Quick Entry | P1 | Основное | быстрый ввод простых записей |
| Track Changes | P1 | Основное | видеть изменения в Timeline |
| Track Seen / Track Views | P1 | Доп. | познакомиться с дополнительным трекингом |
| Allow Import | P1 | Основное | разрешить Data Import для подходящего DocType |
| Default Sort | P1 | Основное | управлять стандартным порядком списка |
| Preview | P2 | Доп. | быстрый просмотр документа |
| DocType Links / Actions | P2 | Доп. | использовать только при естественной связи/действии |

## Field Types

| Группа | Впервые | Статус |
|---|---:|---|
| Data / Small Text / Text | P1 | Основное |
| Select / Check | P1 | Основное |
| Int / Float / Currency | P1 | Основное |
| Percent | P1 | Доп. |
| Date / Datetime | P1 | Основное |
| Time / Duration | P1 | Доп. |
| Link | P1 | Основное |
| Table | P1 | Основное |
| Attach / Attach Image | P1 | Основное |
| Section / Column / Tab Break | P1 | Основное |
| Text Editor / Markdown Editor | P1 | Доп. |
| Table MultiSelect | P1 | Доп. |
| Dynamic Link | P1/P8 | Доп. |
| Attachment Gallery | P1/P5 | Доп. |
| Barcode / Signature / Geolocation | P1/P5 | Доп. |

Dynamic Link становится обязательным только если в конкретном проекте одна ссылка действительно должна указывать на документы разных DocType.

## Кастомизация и переносимость

| Механизм | Впервые | Статус | Проверка |
|---|---:|---|---|
| Customize Form | P2 | Основное | изменить существующий DocType |
| Custom Field | P2 | Основное | увидеть созданную site-specific кастомизацию |
| Property Setter | P2 | Основное | изменить свойство стандартного поля |
| DocType Layout | P2 | Основное | создать альтернативную форму без изменения базового DocType |
| Export Customizations | P2 | Основное | получить файлы кастомизации в app |
| fixtures | P2 | Основное | положить нужные записи БД в app |
| `bench export-fixtures` | P2 | Основное | экспортировать fixtures |
| `bench migrate` | P2 | Основное | применить файлы app на site |
| второй чистый site | P2 | Основное | доказать переносимость |
| Standard / Custom / Customized | P2 | Основное | различать три модели изменений |

## Работа с данными и представления

| Механизм | Впервые | Статус |
|---|---:|---|
| Form View | P1 | Основное |
| List View | P1 | Основное |
| Filters / Sorting | P1 | Основное |
| Saved Filters | P2 | Доп. |
| Mass actions | P1 | Доп. |
| Data Import | P1 | Основное |
| Export | P1 | Основное |
| Comments / Timeline | P3 | Основное |
| Tags | P3 | Основное |
| Kanban | P3 | Основное |
| Calendar | P5 | Основное |
| Gantt | P5/P6 | Доп. |

## Пользователи и права

| Механизм | Впервые | Статус |
|---|---:|---|
| User | P3 | Основное |
| System User / Website User | P3/P7 | Основное |
| Guest / All / Administrator / Desk User | P3 | Основное |
| Role | P3 | Основное |
| Role Permission Manager | P3 | Основное |
| Select | P3 | Основное |
| Read / Write / Create / Delete | P3 | Основное |
| Submit / Cancel / Amend | P3/P4 | Основное |
| Report / Export / Import | P3 | Основное |
| Share / Print / Email | P3 | Основное |
| If Owner | P3 | Основное |
| Permission Level | P3 | Основное |
| User Permission | P3 | Основное |
| Mask / Data Masking | P3 | Доп. |
| ограничения Page / Report / Workspace | P3/P5 | Доп. |
| Assign To | P3 | Основное |
| ToDo | P3 | Основное |
| Due Date / Priority | P3 | Основное |

`Mask` присутствует в `DocPerm` v16.32.0. Data Masking рассматривается только как дополнительная тема, потому что официальная документация помечает её как экспериментальную.

## Жизненный цикл и Workflow

| Механизм | Впервые | Статус |
|---|---:|---|
| обычный Status | P3 | Основное |
| Is Submittable | P4 | Основное |
| Draft / Submit / Cancel / Amend | P4 | Основное |
| DocStatus | P4 | Основное |
| Allow on Submit | P4 | Основное |
| Audit Trail | P4 | Основное |
| Workflow | P4 | Основное |
| Workflow State | P4 | Основное |
| Workflow Action Master | P4 | Основное |
| Workflow Transition | P4 | Основное |
| Workflow Action record | P4 | Основное |
| transition condition | P4 | Доп. |

## Аналитика, Workspace и печать

| Механизм | Впервые | Статус |
|---|---:|---|
| Report Builder | P5 | Основное |
| Group By | P5 | Основное |
| Count / Sum / Average | P5 | Основное |
| Number Card | P5 | Основное |
| Dashboard Chart | P5 | Основное |
| Workspace | P5 | Основное |
| Shortcut / Quick List | P5 | Основное |
| Workspace roles/access | P5 | Основное |
| Print View | P5 | Основное |
| Print Format Builder | P5 | Основное |
| Letter Head | P5 | Основное |
| PDF | P5 | Основное |

PDF впервые требуется в P5. P0 проверяет Frappe, app, Desk и фоновые процессы, но не требует установки PDF-зависимости заранее.

## Автоматизация

| Механизм | Впервые | Статус |
|---|---:|---|
| Allow Auto Repeat | P6 | Основное |
| Auto Repeat | P6 | Основное |
| Auto Repeat Assignee | P6 | Основное |
| Assignment Rule | P6 | Основное |
| Round Robin или Load Balancing | P6 | Основное |
| остальные алгоритмы Assignment Rule | P6 | Доп. |
| PythonExpression в Assignment Rule | P6 | Основное |
| Notification | P6 | Основное |
| System Notification | P6 | Основное |
| Notification Filters | P6 | Основное |
| date-based Notification | P6 | Основное |
| Email Notification | P6 | Доп. |
| scheduler/background jobs | P6 | Основное |

## Web

| Механизм | Впервые | Статус |
|---|---:|---|
| Web Form | P7 | Основное |
| Route | P7 | Основное |
| Anonymous responses | P7 | Основное |
| Login Required | P7 | Основное |
| Apply document permissions | P7 | Основное |
| Allow editing after submit | P7 | Основное |
| Allow multiple responses | P7 | Основное |
| Show list | P7 | Основное |
| Attachments | P7 | Основное |
| Comments / Print | P7 | Доп. |
| Web Form Request / Key required | P7 | Доп. |
| Standard Web Form | P7 | Основное |
| файлы Standard Web Form в app | P7 | Основное |

`Allow editing after submit` здесь — название настройки Web Form. Это не `Allow on Submit` свойства DocField из P4.

## За пределами базовой программы

| Механизм | Статус |
|---|---|
| Python controller | Позже |
| собственная логика в hooks | Позже |
| JavaScript / Client Script | Позже |
| Server Script | Позже |
| Custom Permission Types | Позже |
| REST API / Webhooks | Позже |
| Query Report / Script Report | Позже |
| собственные Jinja-шаблоны | Позже |
| собственные Portal/Website Pages | Позже |
| Virtual DocType | Позже |
| сторонние библиотеки и приложения | Позже |

## Правило изменения матрицы

Новая обязательная тема добавляется только если она:

1. есть в v16.32.0;
2. решает реальную задачу конкретного проекта;
3. воспроизводится на стенде;
4. не дублирует уже изученный механизм без причины.

Если функция нужна только для формального «покрытия», она остаётся дополнительной.