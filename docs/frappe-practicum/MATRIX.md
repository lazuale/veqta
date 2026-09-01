# Матрица практикумов

Матрица контролирует полноту курса. Она не заменяет дорожную карту и не требует вставлять функцию в модель только ради покрытия.

Обозначения:

- **Основное** — механизм обязателен для прохождения этапа;
- **Доп.** — короткая лаборатория или обзор;
- **Позже** — сознательно вынесено за пределы базовой программы.

## Этапы одного приложения

| Код | Стадия `facility_ops` | Главная тема |
|---|---|---|
| P0 | Основа | Bench, app, site, Developer Mode, Git |
| P1 | Реестр эксплуатации | модель данных, Equipment и Movement |
| P2 | Формы и customization | site-specific изменения и Export Customizations |
| P3 | Обращения | пользователи, permissions, Assignment, Kanban |
| P4 | Управляемый процесс | DocStatus, Workflow, fixtures, первый clean-site test |
| P5 | Контроль и аналитика | Inspection, Calendar, Reports, Workspace, Print |
| P6 | Автоматизация | Maintenance Work, Auto Repeat, Assignment Rule, Notification |
| P7 | Внешний вход | Web Form для Service Request |
| P8 | Выпуск | чистая установка и сквозная приёмка |

## Среда и приложение

| Механизм | Впервые | Статус | Зачем |
|---|---:|---|---|
| Bench | P0 | Основное | понять рабочее окружение |
| App | P0 | Основное | единица поставки функциональности |
| Site | P0 | Основное | отдельный экземпляр Frappe |
| `bench new-app` | P0 | Основное | создать настоящий `facility_ops` |
| `install-app` / `list-apps` | P0 | Основное | связать app и site |
| Developer Mode | P0 | Основное | создавать Standard metadata app |
| Module, созданный вместе с app | P0 | Основное | организация объектов внутри app |
| структура app | P0 | Основное | видеть связь Desk и файлов |
| `hooks.py` | P0/P4 | Основное | сначала понять файл, затем добавить реальные fixtures |
| Git diff / commit | P0 | Основное | видеть, что реально попало в app |
| Desk v16 / Workspace Sidebar | P0 | Основное | освоить актуальную навигацию |
| Awesomebar / command palette | P0 | Основное | находить объекты и команды |
| scheduler / workers | P0/P6 | Основное | проверить среду, затем использовать автоматизацию |
| Apps Page / `add_to_apps_screen` | P0/P5 | Доп. | понимать место app в Desk; отдельный hook только при необходимости |

## Модель данных

| Механизм | Впервые | Статус | Где используется |
|---|---:|---|---|
| DocType / DocField / Document / `name` | P0/P1 | Основное | P0 — увидеть устройство, P1 — построить модель |
| Standard DocType своего app | P0/P1 | Основное | Lab Note, затем модель эксплуатации |
| Child DocType / Table | P1 | Основное | Equipment Movement Item |
| Tree DocType | P1 | Основное | Facility Location |
| Single DocType | P1 | Доп. | отдельная лаборатория |
| Custom DocType | P2 | Доп. | сравнение с Standard и Customized |
| Form Builder | P1 | Основное | формы модели эксплуатации |
| Naming | P1 | Основное | справочники и документы |
| By fieldname | P1 | Основное | подходящий справочник |
| Expression / Naming Series | P1 | Основное | рабочий документ |
| Random / UUID / другие способы | P1 | Доп. | обзор палитры Naming |
| Title Field | P1 | Основное | понятное отображение документов |
| Search Fields | P1 | Основное | поиск Equipment и других документов |
| Quick Entry | P1 | Основное | простой справочник |
| Track Changes | P1 | Основное | история Equipment / Movement |
| Track Seen / Track Views | P1 | Доп. | дополнительный tracking |
| Allow Import | P1 | Основное | массовая загрузка Equipment |
| Default Sort | P1 | Основное | порядок списков |
| Preview | P2 | Доп. | быстрый просмотр |
| DocType Links / Actions | P2/P5 | Доп. | только при естественной связи |

## Field Types

| Группа | Впервые | Статус | Основной сценарий |
|---|---:|---|---|
| Data / Small Text / Text | P1 | Основное | Equipment, Movement, Request |
| Select / Check | P1 | Основное | Equipment Status и настройки |
| Int / Float / Currency | P1 | Основное | стоимость и числовые характеристики |
| Percent | P1 | Доп. | лаборатория |
| Date / Datetime | P1 | Основное | эксплуатационные даты |
| Time / Duration | P1 | Доп. | лаборатория |
| Link | P1 | Основное | связи модели |
| Table | P1 | Основное | Equipment Movement Item |
| Attach / Attach Image | P1 | Основное | Equipment и документы |
| Section / Column / Tab Break | P1 | Основное | компоновка форм |
| Text Editor / Markdown Editor | P1/P3 | Доп. | расширенное описание при необходимости |
| Table MultiSelect | P1 | Доп. | лаборатория |
| Dynamic Link | P1/P8 | Доп. | только при доказанной задаче |
| Attachment Gallery | P1/P5 | Доп. | Equipment / Inspection |
| Barcode | P1 | Доп. | Equipment |
| Signature | P5 | Доп. | Inspection |
| Geolocation | P1/P5 | Доп. | Facility Location |

## Кастомизация и переносимость

| Механизм | Впервые | Статус | Проверка |
|---|---:|---|---|
| Customize Form | P2 | Основное | локальное изменение Equipment |
| Custom Field | P2 | Основное | `Local Asset Code` |
| Property Setter | P2 | Основное | изменить свойство Standard field |
| DocType Layout | P2 | Основное | альтернативный layout Equipment |
| Export Customizations | P2 | Основное | включить принятое изменение в app |
| Standard / Custom / Customized | P2 | Основное | различать модели изменений |
| `bench migrate` | P2 | Основное | применить metadata/configuration |
| fixtures | P4 | Основное | Roles / Workflow после появления реальной необходимости |
| `bench export-fixtures` | P4 | Основное | выгрузить минимальную конфигурацию |
| первый второй чистый site | P4 | Основное | доказать переносимость ядра конфигурации |
| финальный чистый site | P8 | Основное | принять всё приложение |

## Работа с данными и представления

| Механизм | Впервые | Статус | Где используется |
|---|---:|---|---|
| Form View | P0/P1 | Основное | P0 знакомство, P1 рабочие формы |
| List View | P0/P1 | Основное | списки Equipment и документов |
| Filters / Sorting | P1 | Основное | Equipment |
| Saved Filters | P2 | Доп. | рабочая выборка |
| Mass actions | P1 | Доп. | безопасная операция в списке |
| Data Import | P1 | Основное | Equipment |
| Export | P1 | Основное | выборка Equipment |
| Comments / Timeline | P3 | Основное | Service Request |
| Tags | P3 | Основное | Service Request |
| Kanban | P3 | Основное | Request State |
| Calendar | P5 | Основное | Inspection |
| Gantt | P5/P6 | Доп. | только если даты модели подходят |

## Пользователи и права

| Механизм | Впервые | Статус | Основной сценарий |
|---|---:|---|---|
| User | P3 | Основное | реальные учебные пользователи |
| System User / Website User | P3/P7 | Основное | Desk в P3, website в P7 |
| Guest / All / Administrator / Desk User | P3/P7 | Основное | автоматические роли и внешний доступ |
| Role | P3 | Основное | Requester / Technician / Facility Supervisor |
| Role Permission Manager | P3 | Основное | Service Request и модель эксплуатации |
| Select permission | P3 | Основное | базовые permission flags |
| Read / Write / Create / Delete | P3 | Основное | реальные проверки входом под User |
| Submit / Cancel / Amend permission | P3/P4 | Основное | флаги в P3, поведение Movement в P4 |
| Report / Export / Import | P3 | Основное | права на работу с данными |
| Share / Print / Email | P3 | Основное | дополнительные действия |
| If Owner | P3 | Основное | Requester |
| Permission Level | P3 | Основное | ограничение полей |
| User Permission | P3 | Основное | ограничение по Facility Location |
| Mask / Data Masking | P3 | Доп. | экспериментальная возможность |
| ограничения Page / Report / Workspace | P3/P5 | Доп. | роли и рабочий стол |
| Assign To | P3 | Основное | Service Request |
| ToDo | P3 | Основное | результат Assignment |
| Due Date / Priority | P3 | Основное | назначенная работа |

`Mask` присутствует в `DocPerm` v16.32.0. Data Masking остаётся дополнительной темой, потому что официальная документация помечает функцию как экспериментальную.

## Жизненный цикл и Workflow

| Механизм | Впервые | Статус | Где используется |
|---|---:|---|---|
| обычный Status / Select state | P1/P3 | Основное | Equipment Status, затем Request State до Workflow |
| Is Submittable | P4 | Основное | Equipment Movement |
| Draft / Submit / Cancel / Amend | P4 | Основное | Equipment Movement |
| DocStatus | P4 | Основное | Equipment Movement |
| Allow on Submit | P4 | Основное | безопасное поле Movement |
| Audit Trail | P4 | Основное | amended Movement |
| Workflow | P4 | Основное | Service Request |
| Workflow State | P4 | Основное | Request State под управлением Workflow |
| Workflow Action Master | P4 | Основное | Service Request |
| Workflow Transition | P4 | Основное | Service Request |
| Workflow Action record | P4 | Основное | история действий |
| transition condition | P4 | Доп. | простая проверяемая задача |

## Аналитика, Workspace и печать

| Механизм | Впервые | Статус | Основной сценарий |
|---|---:|---|---|
| Report Builder | P5 | Основное | Service Request / Inspection |
| Group By | P5 | Основное | состояние, приоритет, результат |
| Count / Sum / Average | P5 | Основное | обращения и стоимость Inspection |
| Number Card | P5 | Основное | открытые Service Request |
| Dashboard Chart | P5 | Основное | Request State / Inspection Result |
| Workspace | P5 | Основное | Facility Operations workspace |
| Shortcut / Quick List | P5 | Основное | рабочая навигация |
| Workspace roles/access | P5 | Основное | Facility Supervisor / Technician |
| Print View | P5 | Основное | Inspection / Movement |
| Print Format Builder | P5 | Основное | печатный документ |
| Letter Head | P5 | Основное | печать |
| PDF | P5 | Основное | итог печатного сценария |

PDF впервые требуется в P5. P0–P4 не требуют установки PDF-зависимости заранее.

## Автоматизация

| Механизм | Впервые | Статус | Где используется |
|---|---:|---|---|
| Allow Auto Repeat | P6 | Основное | Maintenance Work |
| Auto Repeat | P6 | Основное | регулярная Maintenance Work |
| Auto Repeat Assignee | P6 | Основное | назначение регулярной работы |
| Assignment Rule | P6 | Основное | новые Service Request |
| Round Robin или Load Balancing | P6 | Основное | основной алгоритм распределения |
| остальные алгоритмы Assignment Rule | P6 | Доп. | сравнение |
| PythonExpression в Assignment Rule | P6 | Основное | минимальное штатное условие |
| Notification | P6 | Основное | Service Request / Maintenance Work |
| System Notification | P6 | Основное | без зависимости от SMTP |
| Notification Filters | P6 | Основное | ограничить событие |
| date-based Notification | P6 | Основное | плановая работа / Inspection |
| Email Notification | P6 | Доп. | только при настроенном SMTP |
| scheduler/background jobs | P0/P6 | Основное | инфраструктура и фактическая автоматизация |

## Web

| Механизм | Впервые | Статус | Где используется |
|---|---:|---|---|
| Web Form | P7 | Основное | Service Request |
| Route | P7 | Основное | публичный адрес формы |
| Anonymous responses | P7 | Основное | Guest сценарий |
| Login Required | P7 | Основное | Website User сценарий |
| Apply document permissions | P7 | Основное | Website User |
| Allow editing after submit | P7 | Основное | изучить именно настройку Web Form |
| Allow multiple responses | P7 | Основное | повторные обращения |
| Show list | P7 | Основное | Website User |
| Attachments | P7 | Основное | фото проблемы |
| Comments / Print | P7 | Доп. | внешний интерфейс |
| Web Form Request / Key required | P7 | Доп. | приватная ссылка |
| Standard Web Form | P7 | Основное | переносимый web interface |
| файлы Standard Web Form в app | P7 | Основное | увидеть поставку вместе с app |

`Allow editing after submit` здесь — название настройки Web Form, а не `Allow on Submit` свойства DocField.

## Финальная приёмка

| Проверка | Этап | Статус |
|---|---:|---|
| классификация Standard / customization / fixture / data | P8 | Основное |
| install app на новом чистом site | P8 | Основное |
| migrate без ручного восстановления конфигурации | P8 | Основное |
| сквозной сценарий Equipment → Request → Workflow → Inspection → Automation → Web Form | P8 | Основное |
| самостоятельное изменение требования | P8 | Основное |

## За пределами базовой программы

| Механизм | Статус |
|---|---|
| Python controller с собственной бизнес-логикой | Позже |
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

1. есть в Frappe v16.32.0;
2. решает реальную задачу `facility_ops`;
3. воспроизводится на стенде;
4. не требует искажать предметную модель;
5. не дублирует уже изученный механизм без причины.

Если функция нужна только ради формального покрытия, она остаётся дополнительной лабораторией.
