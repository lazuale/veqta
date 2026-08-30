# 04. DocType от А до Я

Если во Frappe нужно понять один объект по-настоящему хорошо, это `DocType`.

DocType отвечает на вопрос: **что это за тип записей и как Frappe должен с ними работать?**

Проверено: **2026-08-30**.

## 1. Самая простая аналогия

Представь бумажный бланк «Заявка».

На нём есть поля:

```text
Тема
Описание
Статус
Срок
```

Есть правила:

```text
тема обязательна
статус выбирается из списка
номер заявки создаётся автоматически
обычный пользователь может читать и изменять
```

Во Frappe описание такого «бланка и правил» — это DocType.

А одна заполненная заявка `REQ-0001` — Document.

## 2. Что DocType описывает

DocType хранит не только список полей. На его уровне задаются, среди прочего:

- название и Module;
- способ формирования `name`;
- заголовок документа (`Title Field`);
- специальные режимы: Child, Single, Tree, Submittable, Virtual;
- права;
- поведение формы и списка;
- импорт, копирование, отслеживание изменений;
- web/email-настройки;
- Actions, Links и Connections.

Не нужно заучивать весь экран. Важно понять, что **DocType — центральная metadata-модель документа**.

## 3. Что происходит с обычным DocType

Создали:

```text
DocType: Request
```

Для обычного не-Virtual DocType Frappe создаёт таблицу вида:

```text
tabRequest
```

Но этим дело не заканчивается. Та же metadata используется для:

- Form View;
- List View;
- ORM / Document API;
- REST API;
- permissions;
- поиска и фильтров;
- Reports;
- импорта и экспорта;
- Workflow и других механизмов.

Поэтому DocType — больше, чем SQL-таблица.

## 4. Где его найти

В Desk через Awesomebar найди:

```text
DocType
```

Откроется список типов документов, которые доступны на Site.

Там могут быть одновременно:

- DocTypes самого Framework;
- DocTypes установленных Apps;
- свои Standard DocTypes;
- Custom DocTypes текущего Site.

Сам факт наличия в списке не говорит, какому App принадлежит объект.

## 5. Standard и Custom DocType

Эта разница важна уже на старте.

### Custom DocType

Удобен для быстрых экспериментов и site-specific настройки.

Он живёт как конфигурация Site.

### Standard DocType

Является частью App. Его metadata хранится в файлах приложения и может идти в Git.

Пример структуры:

```text
training_app/
└── training_app/
    └── requests/
        └── doctype/
            └── request/
                ├── request.json
                ├── request.py
                └── request.js
```

На пальцах:

```text
Custom   → «сделал прямо на этом Site»
Standard → «это часть устанавливаемого приложения»
```

## 6. Developer Mode

Чтобы нормально разрабатывать Standard DocTypes и получать файлы приложения, используют Developer Mode.

Один из способов включить его:

```bash
bench set-config -g developer_mode true
```

После изменения конфигурации обычно нужно перезапустить dev-процессы/Bench в соответствии с окружением.

Developer Mode не меняет смысл DocType. Он нужен для разработки и экспорта standard metadata в код App.

## 7. Экран DocType: как не утонуть

В v16 настройки DocType сгруппированы по областям вроде:

```text
Form
Permissions
Naming
Settings
View Settings
Email
Fields
Actions
Links
Web View
Advanced
Connections
```

Вместо запоминания вкладок удобнее делить настройки по смыслу.

### «Кто я?»

```text
Name
Module
Custom / Standard
Is Child Table
Is Single
Is Tree
Is Submittable
Is Virtual
```

### «Как меня называют?»

```text
Naming Rule
autoname
Title Field
```

### «Как меня показывают?»

```text
Quick Entry
Default View
Search Fields
Sort Field / Sort Order
Calendar / Gantt settings
```

### «Кто может со мной работать?»

```text
Permissions
```

### «Какие дополнительные возможности включены?»

```text
Track Changes
Allow Import
Allow Copy
Allow Auto Repeat
attachments settings
web/email settings
```

Этого деления достаточно, чтобы ориентироваться в форме DocType без зубрёжки.

## 8. Fields — сердце структуры документа

В секции `Fields` добавляются `DocField`.

Для учебного `Request` можно начать так:

| Label | Fieldname | Type |
|---|---|---|
| Subject | `subject` | Data |
| Description | `description` | Text |
| Status | `status` | Select |
| Due Date | `due_date` | Date |

После сохранения базовая Form View уже будет построена из этих полей.

Подробно свойства полей разберём в следующей главе.

## 9. Naming — как получить `REQ-0001`

Каждый обычный Document имеет уникальное системное поле `name`.

Например:

```text
REQ-0001
```

Frappe 16 поддерживает несколько штатных способов naming: ручное имя, autoincrement, поле документа, Naming Series, expression, random, UUID и script.

Пока достаточно знать одно:

> `name` — не просто красивый номер на форме. Это техническая идентичность Document.

Вся тема naming будет в главе 06.

## 10. Title Field — имя для человека

Допустим:

```text
name = REQ-0001
subject = Проверить отчёт
```

Можно назначить:

```text
Title Field = subject
```

Тогда человеку удобнее видеть «Проверить отчёт», а Frappe продолжит использовать `REQ-0001` как системный ID.

Это хороший способ не превращать `name` в длинный изменяемый заголовок.

## 11. Специальные режимы DocType

У DocType есть несколько флагов, которые сильно меняют его поведение.

| Режим | Для чего |
|---|---|
| **Is Child Table** | строки, принадлежащие родительскому документу |
| **Is Single** | одна запись-настройка на весь Site |
| **Is Tree** | иерархия parent → child |
| **Is Submittable** | Draft → Submitted → Cancelled |
| **Is Virtual** | данные приходят не из обычной таблицы DocType |

Примеры:

```text
Order Item      → Child Table
App Settings    → Single
Category        → Tree
Approval Record → Submittable
External Record → Virtual
```

Не ставь такие галочки «на всякий случай». У каждой есть конкретная семантика. Подробно они разбираются в главах 08–10.

## 12. Permissions

В DocType можно определить, что разные роли могут делать с документами.

Например:

```text
Employee
- Read
- Create
- Write

Manager
- Read
- Create
- Write
- Delete
```

У Submittable DocType появляются ещё действия `Submit`, `Cancel`, `Amend`.

Но сами права лучше разбирать отдельно — в блоке пользователей и permissions.

## 13. Несколько полезных флагов

### Quick Entry

Позволяет создавать документ через небольшое быстрое окно, если для этого достаточно нескольких полей.

Подходит, например, для короткого справочника. Для большой формы с 30 полями Quick Entry обычно не спасает.

### Track Changes

Включает сохранение изменений документа в `Version`.

Полезно, если важно видеть, кто и что изменил.

### Allow Import

Разрешает использовать Data Import для этого DocType.

### Allow Copy

Разрешает создавать новый документ копированием существующего.

### Allow Auto Repeat

Подключает штатный механизм периодического создания документов.

Эти флаги включают готовые механизмы Framework. Для них не требуется сразу писать собственный код.

## 14. View Settings

DocType может подсказывать Desk, как удобнее показывать записи.

Часто здесь важны:

- `Search Fields`;
- `Sort Field`;
- `Sort Order`;
- Default View;
- настройки Calendar/Gantt, если соответствующее представление используется.

Пример:

```text
Request
Sort Field = modified
Sort Order = DESC
```

Тогда свежие изменения будут выше в списке.

## 15. Actions, Links и Connections

DocType может содержать metadata для дополнительных действий и связей в интерфейсе.

Простой смысл:

- **Action** — пользовательское действие;
- **Link / Connection** — показать связанные документы или переходы.

Не нужно путать их с обычным `Link`-полем. `Link` — это значение внутри конкретного Document; Connections — часть навигации вокруг формы.

## 16. Web View и Email

У DocType есть настройки, связанные с web-представлением и email-поведением.

Это не значит, что любой DocType автоматически становится красивым публичным сайтом. Здесь Framework даёт строительные блоки, которые при необходимости настраиваются отдельно.

Для первого знакомства эти секции можно оставить в покое и вернуться к ним в соответствующих главах.

## 17. Advanced — раздел, куда не нужно лезть первым делом

В `Advanced` лежат настройки, которые полезны в специальных случаях.

Правило для новичка простое:

> Если ты пока не понимаешь, зачем конкретная опция нужна, не включай её «для улучшения».

Сначала собери обычный DocType и посмотри, чего реально не хватает.

## 18. Мини-пример: создаём простую `Request`

Для первого учебного DocType достаточно:

```text
Name: Request
Module: Training

Fields:
Subject      Data      Mandatory
Description Text
Status       Select    Open / In Progress / Done
Due Date     Date

Title Field: subject
Track Changes: enabled
```

После сохранения попробуй:

1. открыть List View;
2. создать две записи;
3. открыть одну запись;
4. изменить `Status`;
5. посмотреть, как выглядит заголовок и Timeline.

Даже такой маленький DocType уже показывает большую часть философии Frappe.

## Что запомнить

- DocType описывает **тип документов и правила работы с ним**.
- Document — одна запись этого типа.
- Standard DocType живёт в App; Custom — прежде всего в конфигурации Site.
- Поля — только одна часть DocType. Есть ещё naming, permissions, views и специальные режимы.
- Большинство настроек не нужно трогать сразу. Начинай с минимальной модели.

## Официальные источники

- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [DocType source, version-16](https://github.com/frappe/frappe/tree/version-16/frappe/core/doctype/doctype)

Следующая глава: [**05. DocField и свойства полей**](05_DOCFIELD.md).