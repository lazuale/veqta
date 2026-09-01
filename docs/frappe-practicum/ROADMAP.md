# Дорожная карта практикумов

Курс проходит последовательно: **P0 → P8**.

Все этапы развивают один app — `facility_ops`. Новый этап начинается только после того, как предыдущий работает на фактическом стенде Frappe v16.32.0 и его изменения понятны в Desk, базе и Git.

---

# P0. Основа приложения

## Рабочая задача

Получить отдельный Bench с Frappe v16.32.0, создать настоящий app `facility_ops`, установить его на `facility-ops.localhost` и понять связь между Bench, app, site, Module, Desk и Git.

## Результат

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

## Практика

1. Подготовить системное окружение по `projects/00-lab/SETUP_WSL2.md`.
2. Зафиксировать `bench version` и точный tag Frappe.
3. Создать `facility_ops` через `bench new-app`.
4. Создать `facility-ops.localhost`.
5. Установить app и проверить `list-apps`.
6. Включить Developer Mode.
7. Найти default Module и `modules.txt`.
8. Просмотреть структуру app, `hooks.py`, `public`, `templates`, `patches.txt`.
9. Пройти Apps Page, Workspace Sidebar, Awesomebar, List View и Form View.
10. Проверить scheduler и workers.
11. Создать временный Standard DocType `Lab Note`.
12. Найти generated metadata и boilerplate в app.
13. Создать обычный Document и увидеть, что его рабочие данные не становятся исходниками app.
14. Посмотреть Git diff изменения metadata.
15. Удалить `Lab Note` штатно и увидеть удаление его файлов.
16. Зафиксировать чистый Git перед P1.

## Перед P1

Ученик может объяснить:

- Bench против site;
- site против app;
- app против Module;
- DocType против Document;
- metadata против рабочих данных;
- зачем нужен Developer Mode;
- что именно Git хранит в приложении.

---

# P1. Реестр эксплуатации

## Рабочая задача

Создать фундаментальную модель мест и оборудования, а также документ перемещения оборудования.

## Модель

```text
Facility Location (Tree)
        │
        └────────► Equipment
                      ▲
                      │
Equipment Type ───────┘

Equipment Movement
└── Equipment Movement Item (Child)
        └────────► Equipment
```

## DocType

### Facility Location

Иерархия мест эксплуатации.

Пример данных:

```text
Main Site
├── Building A
│   ├── Floor 1
│   └── Floor 2
└── Warehouse
```

### Equipment Type

Минимально:

- Type Name — Data;
- Description — Small Text.

Для справочника сравнить варианты Naming и использовать понятное имя документа.

### Equipment

Основные поля:

- Equipment Code — Data;
- Equipment Name — Data;
- Equipment Type — Link;
- Facility Location — Link;
- Status — Select: `Active`, `Out of Service`, `Retired`;
- Serial Number — Data;
- Commissioning Date — Date;
- Purchase Cost — Currency;
- Warranty End Date — Date;
- Photo — Attach Image;
- Notes — Small Text.

### Equipment Movement Item

Child DocType:

- Equipment — Link;
- Note — Data или Small Text.

### Equipment Movement

- Movement Date — Date;
- From Location — Link;
- To Location — Link;
- Reason — Small Text;
- Items — Table → Equipment Movement Item.

В P1 документ ещё не делаем submittable. Системный DocStatus изучается в P4.

## Что изучаем

- Standard DocType;
- DocField и Document;
- Form Builder;
- основные Field Types;
- Link;
- Tree DocType;
- Child DocType / Table;
- Section / Column / Tab Break;
- Naming;
- By fieldname;
- Expression / Naming Series;
- Title Field;
- Search Fields;
- Quick Entry;
- Track Changes;
- Default Sort;
- Form View и List View;
- filters и sorting;
- Allow Import;
- Data Import;
- Export;
- Git diff Standard metadata.

## Практика

1. Нарисовать модель до открытия DocType editor.
2. Создать `Facility Location` как Tree DocType.
3. Заполнить небольшую иерархию.
4. Создать `Equipment Type`.
5. Создать `Equipment` и разложить поля по секциям формы.
6. Настроить Naming, Title Field и Search Fields.
7. Включить Track Changes там, где история действительно полезна.
8. Проверить Quick Entry на простом справочнике.
9. Создать `Equipment Movement Item` как Child DocType.
10. Создать `Equipment Movement` с Table.
11. Создать несколько документов вручную.
12. Подготовить тестовый CSV оборудования.
13. Импортировать оборудование через Data Import.
14. Найти импортированные записи, отфильтровать их и экспортировать выборку.
15. Посмотреть generated JSON и Git diff каждого Standard DocType.
16. Сделать отдельный commit P1.

## Дополнительная лаборатория

Без изменения основной модели коротко проверить подходящие дополнительные Field Types:

- Percent;
- Time / Duration;
- Table MultiSelect;
- Attachment Gallery;
- Barcode;
- Geolocation;
- Single DocType;
- Dynamic Link.

Если механизм не имеет естественного применения, его не оставляем в основной модели.

## Самостоятельная работа

Добавить к Equipment новую характеристику так, чтобы существующие документы продолжили работать без пересоздания.

## Перед P2

Ученик различает:

- Link и Select;
- Tree и обычный справочник;
- Child Table и отдельный связанный DocType;
- Naming и Title Field;
- metadata Standard DocType и рабочие записи;
- импорт данных и поставку конфигурации app.

---

# P2. Формы и site-specific customization

## Рабочая задача

Понять, что изменение формы на конкретном site и изменение Standard DocType приложения — не одно и то же.

## Базовый сценарий

На `Equipment` появляется локальное требование конкретного site:

- дополнительное поле `Local Asset Code`;
- одно изменение свойства существующего поля;
- альтернативный layout формы.

## Часть A. Customize Form

1. Открыть `Equipment` через Customize Form.
2. Добавить `Local Asset Code` как Custom Field.
3. Изменить одно безопасное свойство существующего поля через Customize Form.
4. Найти созданные Custom Field и Property Setter.
5. Сравнить их со Standard metadata `Equipment`.
6. Убедиться, что исходный JSON Standard DocType не переписан как обычное редактирование DocType.
7. Посмотреть Git до Export Customizations.

## Часть B. Export Customizations

1. Решить, что локальное изменение теперь должно поставляться вместе с app.
2. Выполнить Export Customizations для `Equipment`.
3. Найти экспортированные файлы в `facility_ops`.
4. Посмотреть Git diff.
5. Выполнить `bench migrate` и проверить результат.

## Часть C. DocType Layout

1. Создать альтернативный layout `Equipment`.
2. Изменить порядок и видимость нескольких полей.
3. Проверить применение layout.
4. Убедиться, что назначение Layout отличается от изменения базовой metadata.

## Что изучаем

- Standard / Custom / Customized;
- Customize Form;
- Custom Field;
- Property Setter;
- Export Customizations;
- DocType Layout;
- Preview как дополнительную функцию;
- Saved Filters как дополнительную функцию;
- `bench migrate`;
- Git diff переносимой кастомизации.

## Что пока не изучаем

Fixtures откладываются до P4, когда в приложении появятся реальные конфигурационные записи — Roles и Workflow. Не создаём искусственную fixture только ради упражнения.

## Самостоятельная работа

Добавить ещё одно локальное требование к `Equipment` и самостоятельно решить:

- оставить его только на site;
- или включить в поставку app через Export Customizations.

Решение нужно объяснить.

## Перед P3

Ученик может показать на реальных файлах разницу между:

```text
Standard DocType
Custom Field / Property Setter на site
Export Customizations в app
DocType Layout
```

---

# P3. Обращения и совместная работа

## Рабочая задача

Добавить основной рабочий процесс службы эксплуатации: пользователь создаёт обращение, оно доступно нужным ролям и назначается конкретному технику.

## Новый DocType: Service Request

Основные поля:

- Subject — Data;
- Description — Text;
- Facility Location — Link;
- Equipment — Link, optional;
- Priority — Select: `Low`, `Medium`, `High`, `Critical`;
- Request State — Select: `New`, `Assigned`, `In Progress`, `Awaiting Review`, `Closed`;
- Requested On — Datetime;
- Attachment — Attach.

`Request State` сначала работает как обычное Select. В P4 этим полем начнёт управлять Workflow.

## Учебные роли

```text
Requester
Technician
Facility Supervisor
```

Создать несколько реальных учебных System User и проверять права через вход под ними.

## Что изучаем

- User;
- System User;
- автоматические роли Guest / All / Desk User / Administrator;
- Role;
- Role Permission Manager;
- Select / Read / Write / Create / Delete;
- Report / Export / Import;
- Share / Print / Email;
- If Owner;
- Permission Level;
- User Permission;
- Assign To;
- ToDo;
- Due Date;
- Priority;
- Comments;
- Timeline;
- Tags;
- Kanban.

## Практика

1. Создать `Service Request`.
2. Создать три собственные Role.
3. Создать минимум три учебных System User.
4. Настроить базовые Role Permissions.
5. Проверить права реальным входом под каждым пользователем.
6. Настроить сценарий If Owner там, где он естественен.
7. Ограничить одного пользователя через User Permission по `Facility Location` и проверить результат.
8. Создать несколько Service Request от разных пользователей.
9. Назначить запрос технику через Assign To.
10. Найти соответствующий ToDo.
11. Поставить Due Date и Priority.
12. Снять назначение и проверить изменение ToDo.
13. Добавить Comments и Tags.
14. Посмотреть Timeline.
15. Создать Kanban по `Request State`.
16. Проверить ручное перемещение карточек между состояниями до Workflow.
17. Зафиксировать Git и конфигурационные записи, появившиеся в P3.

## Отрицательные проверки

- Requester не получает административные права только потому, что создал документ.
- Technician без нужного Read не получает доступ только из-за назначения.
- User Permission реально ограничивает документы по Link-полю.
- Проверка под Administrator не считается проверкой Role Permission.

## Самостоятельная работа

Добавить нового Technician и добиться того, чтобы он видел только разрешённые ему Locations, но мог работать с назначенными ему обращениями в этих границах.

## Перед P4

Ученик объясняет:

```text
Permission != Assignment
Role != User Permission
Assign To -> ToDo
Owner != Assignee
```

---

# P4. DocStatus, Workflow и первая переносимость

## Рабочая задача

Разделить два разных вида жизненного цикла:

1. подтверждение факта перемещения оборудования;
2. управляемое прохождение обращения между ролями.

## Часть A. Equipment Movement как submittable document

Включить `Is Submittable` для `Equipment Movement`.

Проверить:

```text
Draft → Submit → Cancel
          │
          └── Cancel → Amend → новый Draft
```

Изучить:

- DocStatus;
- Submit;
- Cancel;
- Amend;
- Allow on Submit на одном безопасном поле;
- Audit Trail.

Отдельно увидеть, что submitted-документ не является просто записью со значением `Status = Done`.

## Часть B. Workflow для Service Request

До Workflow `Request State` менялся вручную.

Теперь создать Workflow:

```text
New
 ↓ Supervisor / Technician assignment
Assigned
 ↓ Technician
In Progress
 ↓ Technician
Awaiting Review
 ↓ Facility Supervisor
Closed
```

Проверить:

- Workflow;
- Workflow State;
- Workflow Action Master;
- Workflow Transition;
- allowed role;
- Workflow Action records;
- простой transition condition как дополнительную тему.

После включения Workflow пользователь не должен обходить маршрут простым ручным изменением поля.

## Часть C. Fixtures

Теперь в приложении появились реальные конфигурационные записи, которые должны воспроизводиться:

- собственные Roles;
- Workflow и связанные необходимые записи.

1. Определить минимальный набор fixtures.
2. Добавить fixtures в `hooks.py`.
3. Выполнить `bench export-fixtures`.
4. Посмотреть JSON fixtures и Git diff.
5. Не включать User и рабочие Service Request в fixtures.

## Часть D. Первый clean-site test

Создать второй чистый site.

Проверить цепочку:

```text
facility_ops source
+ Export Customizations
+ fixtures
+ install-app
+ migrate
= воспроизводимая базовая конфигурация
```

На втором site должны появиться:

- Standard DocType P1–P3;
- экспортированная кастомизация Equipment;
- нужные Role;
- Workflow;
- структура app без повторного ручного накликивания.

Рабочие Equipment и Service Request переносить не требуется.

## Самостоятельная работа

Добавить ещё один допустимый переход Workflow и самостоятельно определить, какие изменения должны попасть в Git, а какие останутся данными site.

## Перед P5

Ученик различает:

- обычное поле состояния;
- Workflow State;
- DocStatus;
- Export Customizations;
- fixtures;
- рабочие данные.

---

# P5. Проверки, аналитика, Workspace и печать

## Рабочая задача

Добавить контроль эксплуатации и собрать из накопленных данных рабочий интерфейс службы.

## Новый DocType: Inspection

Основные поля:

- Inspection Date — Date;
- Equipment — Link;
- Facility Location — Link;
- Inspector — Link → User;
- Result — Select: `Pass`, `Needs Service`, `Failed`;
- Notes — Text;
- Next Inspection Date — Date;
- Cost — Currency;
- Attachment — Attach.

Дополнительно Signature можно проверить короткой лабораторией.

## Что изучаем

- Calendar;
- Report Builder;
- filters;
- Group By;
- Count / Sum / Average;
- Number Card;
- Dashboard Chart;
- Workspace;
- Shortcut;
- Quick List;
- Workspace roles/access;
- Print View;
- Print Format Builder;
- Letter Head;
- PDF;
- Gantt как дополнительное представление, если даты модели подходят.

## Практика

1. Создать `Inspection`.
2. Создать набор проверок по разным Equipment и Locations.
3. Открыть проверки через Calendar.
4. Построить Report Builder по Service Request.
5. Сделать Group By по состоянию или приоритету.
6. Проверить Count.
7. Построить второй отчёт, где естественен Sum или Average, например по стоимости Inspection.
8. Создать Number Card открытых Service Request.
9. Создать Dashboard Chart по Request State или Result Inspection.
10. Создать Workspace `Facility Operations`.
11. Добавить только полезные Shortcuts и Quick Lists.
12. Ограничить Workspace нужными ролями.
13. Настроить печать Inspection или Equipment Movement.
14. Создать Letter Head.
15. Проверить Print View.
16. Подготовить и проверить поддерживаемую PDF-зависимость учебного стенда.
17. Получить PDF.
18. Определить, какие объекты аналитики и Workspace требуют поставки вместе с app, и проверить их переносимость.

## Самостоятельная работа

Добавить один новый показатель на Workspace только в том случае, если он отвечает на конкретный операционный вопрос. Объяснить, зачем он нужен.

## Перед P6

Ученик умеет превратить накопленные Documents в рабочий интерфейс без собственного frontend.

---

# P6. Регламентная работа и автоматизация

## Рабочая задача

Сначала выполнить процесс вручную, затем убрать повторяющуюся ручную работу штатными механизмами Frappe.

## Новый DocType: Maintenance Work

Основные поля:

- Equipment — Link;
- Facility Location — Link;
- Planned Date — Date;
- Work Type — Select;
- Priority — Select;
- Status — Select;
- Description — Text;
- Completed On — Datetime.

Включить `Allow Auto Repeat`.

## Часть A. Auto Repeat

1. Создать обычную Maintenance Work вручную.
2. Проверить её жизненный цикл как обычного Document.
3. Включить Auto Repeat.
4. Создать ежемесячный повтор.
5. Проверить Auto Repeat Assignee.
6. Убедиться, что scheduler работает.

## Часть B. Assignment Rule

До P6 Service Request назначались вручную через Assign To.

Теперь:

1. Создать Assignment Rule для Service Request.
2. Использовать один понятный основной алгоритм — Round Robin или Load Balancing.
3. Проверить автоматическое создание назначения.
4. Сравнить остальные алгоритмы короткой лабораторией.
5. Разобрать минимальный PythonExpression только в рамках штатного поля условия.

## Часть C. Notification

1. Создать System Notification на событие Service Request.
2. Добавить Filters.
3. Проверить date-based Notification на Maintenance Work или Inspection.
4. Email Notification оставить дополнительной проверкой, если SMTP действительно настроен.

## Отрицательные проверки

- Auto Repeat не считается рабочим, пока новый документ реально не создаётся.
- Assignment Rule не должен выдавать пользователю права, которых у него нет.
- Notification не заменяет Workflow и не меняет состояние сама по себе.

## Самостоятельная работа

Выбрать ещё один ручной повторяющийся шаг приложения и обосновать, подходит ли для него Auto Repeat, Assignment Rule, Notification или вообще не нужна автоматизация.

---

# P7. Web Form обращений

## Рабочая задача

Открыть внешний вход в уже существующий `Service Request`, не создавая отдельную параллельную модель заявок.

## Основная цепочка

```text
Guest / Website User
        ↓
    Web Form
        ↓
 Service Request
        ↓
 Desk / Assignment / Workflow
```

## Что изучаем

- Web Form;
- Route;
- Anonymous responses;
- Login Required;
- Website User;
- Apply document permissions;
- Allow editing after submit — как настройку Web Form;
- Allow multiple responses;
- Show list;
- attachments;
- Comments / Print как дополнительные настройки;
- Web Form Request / Key required как дополнительный сценарий;
- Standard Web Form;
- файлы Standard Web Form в app.

## Практика

1. Создать Web Form для Service Request.
2. Опубликовать понятный Route.
3. Оставить только поля, которые действительно должен вводить внешний пользователь.
4. Проверить anonymous submit.
5. Проверить появление обычного Service Request в Desk.
6. Проверить attachment.
7. Затем включить Login Required и сравнить поведение.
8. Создать Website User.
9. Проверить Apply document permissions.
10. Проверить Show List и редактирование там, где это безопасно.
11. Создать Standard Web Form в Developer Mode.
12. Найти его файлы внутри Module app.
13. Убедиться, что Web Form использует существующую модель Service Request, а не отдельный дублирующий DocType.

## Самостоятельная работа

Создать второй вариант внешнего сценария с другой моделью доступа и объяснить различие Guest, Website User и document permissions.

---

# P8. Выпуск и приёмка приложения

## Рабочая задача

Доказать, что `facility_ops` — воспроизводимое приложение, а не результат ручной настройки одного site.

## Перед финальной установкой

Проверить Git и классифицировать всё созданное:

```text
Standard metadata
Export Customizations
fixtures
site-only settings
рабочие данные
```

В поставку app не должны случайно попасть:

- тестовые User;
- реальные Equipment;
- Service Request;
- Inspection;
- Maintenance Work;
- прочие рабочие записи только потому, что они использовались в практикуме.

## Чистый site

На новом совместимом Frappe v16.32.0 site:

1. установить `facility_ops`;
2. выполнить migrate;
3. проверить Standard DocType;
4. проверить exported customizations;
5. проверить Role и Workflow fixtures;
6. проверить Workspace и нужную конфигурацию аналитики;
7. проверить Standard Web Form;
8. создать новые тестовые данные уже на чистом site.

## Финальный сквозной сценарий

На чистом site выполнить без подсказки:

```text
создать Location
↓
создать Equipment Type
↓
создать Equipment
↓
создать и Submit Equipment Movement
↓
создать Service Request
↓
назначить / получить Assignment
↓
провести Request через Workflow
↓
создать Inspection
↓
увидеть данные в Report / Workspace
↓
создать Maintenance Work / Auto Repeat
↓
создать Service Request через Web Form
```

## Самостоятельное изменение

Получить новое небольшое требование к системе и реализовать его без пошагового рецепта, используя уже изученные строительные блоки.

Изменение считается правильным только если ученик может объяснить:

- почему выбран именно этот тип DocType или настройки;
- где изменение хранится;
- нужны ли Export Customizations или fixtures;
- какие permissions затронуты;
- как проверить его на чистом site.

## Критерий завершения курса

```text
чистый Frappe v16.32.0
+ facility_ops
+ install-app
+ migrate
+ новые тестовые данные
= полностью работоспособный учебный продукт
```

Если для восстановления принятой конфигурации приходится вспоминать, что нужно ещё вручную накликать на исходном site, курс не пройден.
