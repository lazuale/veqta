# 04. DocType от А до Я

DocType — центральный механизм Frappe Framework. Если понять его глубоко, становится понятно, почему Frappe называют metadata-driven framework.

Эта глава разбирает **сам DocType как объект конфигурации**: что он описывает, как устроен его экран в Frappe 16, какие группы настроек существуют и что каждая из них меняет.

> Поля DocType (`DocField`) будут подробно разобраны в следующей главе. Здесь фокус именно на настройках уровня DocType.

Проверено: **2026-08-30**.

---

## 1. Что такое DocType

Официальная документация определяет DocType как основной building block приложения Frappe. Он описывает одновременно **модель данных и представление этих данных**.

Упрощённо:

```text
DocType
├── структура данных
├── naming
├── layout
├── permissions
├── view settings
├── lifecycle options
├── web settings
├── email settings
├── links/actions
└── metadata для Framework
```

Для обычного DocType Framework создаёт JSON metadata и соответствующую таблицу в базе данных.

Например:

```text
DocType: Request
```

обычно соответствует таблице:

```text
tabRequest
```

Но DocType нельзя сводить к SQL-таблице: одна и та же metadata используется Desk, ORM, REST API, permissions, reports и другими механизмами.

---

## 2. DocType и Document

Нужно окончательно разделить два понятия.

```text
DocType
= описание типа данных

Document
= один экземпляр этого типа
```

Например:

```text
DocType: Request

Document:
REQ-00001
```

В Python каждый обычный Document является объектом, основанным на `frappe.model.document.Document`.

---

## 3. Где открыть DocType

В Desk открой Awesomebar и найди:

```text
DocType
```

Ты попадёшь в список DocTypes, куда входят:

```text
DocTypes самого Framework
DocTypes установленных Apps
собственные Standard DocTypes
Custom DocTypes конкретного Site
```

Важно: наличие DocType в этом списке ещё не означает, что он относится к чистому Framework. Он может быть установлен отдельным App.

---

## 4. Standard DocType и Custom DocType

Это одно из самых важных различий.

### Standard DocType

Является частью App.

Обычно его metadata хранится в файлах приложения и попадает в Git.

Пример:

```text
training_app/
└── training_app/
    └── training/
        └── doctype/
            └── request/
                ├── request.json
                ├── request.py
                └── request.js
```

### Custom DocType

Создан как site-specific customization.

Он хранится в данных Site и не является автоматически частью исходного кода App.

### Практический смысл

Для обучения и прототипирования Custom DocType удобен.

Для полноценного приложения обычно нужен Standard DocType в Developer Mode, чтобы metadata воспроизводилась из репозитория.

---

## 5. Developer Mode

Официальный tutorial по созданию DocType рекомендует включать Developer Mode, если создаваемые DocTypes должны генерировать boilerplate и попадать в version control.

Команда:

```bash
bench set-config -g developer_mode true
```

После этого Standard DocType становится частью разработки App, а не только конфигурацией одного Site.

Developer Mode не делает DocType «другим типом сущности». Он меняет способ разработки и хранения metadata.

---

# Часть I. Экран DocType в Frappe 16

## 6. Основные вкладки и группы

В текущем Frappe 16 metadata самого `DocType` содержит отдельные области:

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

Не все поля видны одновременно: часть настроек появляется только при включении других флагов.

Это важно: интерфейс DocType динамический.

---

# Часть II. Naming

## 7. Поле `name`

Каждый обычный Document во Frappe имеет уникальный primary key:

```text
name
```

Например:

```text
REQ-00001
```

или:

```text
customer@example.com
```

или UUID.

`name` используется ORM и API для однозначного обращения к записи.

Например:

```python
frappe.get_doc("Request", "REQ-00001")
```

Поэтому naming — не просто визуальная настройка.

---

## 8. Naming Rule

В Frappe 16 у DocType есть девять штатных вариантов naming:

```text
Set by user
Autoincrement
By fieldname
By "Naming Series" field
Expression
Expression (old style)
Random
UUID
By script
```

Не надо писать собственный генератор ID, пока один из этих способов подходит.

---

## 9. Set by user

Пользователь сам вводит `name` при создании документа.

Подходит для естественных кодов вроде:

```text
ISO
EUR
WAREHOUSE-01
```

Не подходит, если пользователь вообще не должен думать об ID.

---

## 10. Autoincrement

Frappe выдаёт последовательные числовые имена:

```text
1
2
3
4
```

Это не gap-safe numbering: удалённые номера не используются повторно.

---

## 11. By fieldname

`name` берётся из значения одного поля.

Например:

```text
Department Name = Analytics
name = Analytics
```

Это удобно для справочников, где естественный ключ действительно уникален и стабилен.

Но если пользовательское название может часто меняться, использовать его как primary key надо осторожно.

---

## 12. Naming Series

Используется series field и последовательная нумерация.

Концептуально:

```text
REQ-.YYYY.-.#####
```

может давать:

```text
REQ-2026-00001
REQ-2026-00002
```

Детально naming будет отдельной главой.

---

## 13. Expression, Random, UUID, Script

Frappe также позволяет:

```text
строить имя выражением
генерировать random name
использовать UUID
передать naming пользовательскому Python-коду
```

`By script` нужен только тогда, когда штатных декларативных схем недостаточно.

---

## 14. Allow Rename

Настройка:

```text
Allow Rename
```

разрешает переименование существующего Document.

Это важнее, чем кажется, потому что `name` является идентификатором записи.

Если ID должен быть неизменяемым бизнес-идентификатором, разрешать rename без причины не стоит.

---

# Часть III. Title и отображение

## 15. `name` и Title Field — разные вещи

Допустим:

```text
name = REQ-00042
subject = Проверить отчёт за август
```

Пользователю полезнее видеть `subject`, но системе нужен стабильный ID.

Для этого существует:

```text
Title Field
```

Можно указать:

```text
subject
```

И тогда Frappe будет использовать это значение как человеческий заголовок документа.

---

## 16. Show Title Field in Link

Настройка:

```text
Show Title Field in Link
```

позволяет Link-полям показывать title вместо технического `name`.

Например вместо:

```text
REQ-00042
```

пользователь может видеть:

```text
Проверить отчёт за август
```

при этом фактически Link по-прежнему ссылается на `name`.

---

## 17. Image Field

Можно указать поле, которое будет использоваться как основное изображение документа.

Подходит, например, для:

```text
профиля человека
товара
оборудования
объекта каталога
```

Для обычной бизнес-записи изображение не требуется автоматически.

---

# Часть IV. Основные типы DocType

## 18. Обычный DocType

Это стандартный вариант:

```text
много Documents
+ отдельная таблица
+ List View
+ Form View
```

Примеры:

```text
Request
Customer
Vehicle
Asset
```

---

## 19. Is Child Table

Флаг:

```text
Is Child Table
```

превращает DocType в дочерний тип.

Такой DocType существует только внутри родительского документа через поле типа `Table`.

У child row есть специальные свойства:

```text
parent
parenttype
parentfield
idx
```

Child Table используется для данных, которые логически являются частью родителя.

Пример:

```text
Order
└── Order Item[]
```

Child Table не получает обычный самостоятельный List View.

---

## 20. Editable Grid

Для Child Table можно включить:

```text
Editable Grid
```

Тогда часть полей можно редактировать прямо в grid родительской формы.

Если выключить, строки чаще редактируются через отдельный row form/dialog.

---

## 21. Is Single

Флаг:

```text
Is Single
```

означает, что существует только один Document данного типа.

Идеальный пример:

```text
Application Settings
```

У Single DocType нет собственной обычной таблицы `tab<DocType>`.

Значения хранятся в:

```text
tabSingles
```

с колонками:

```text
doctype
field
value
```

Single подходит для глобальных настроек, а не для справочника из одной строки «потому что сейчас запись одна».

---

## 22. Is Tree

Флаг:

```text
Is Tree
```

включает иерархическую модель на базе Nested Set.

Пример:

```text
Category
├── Hardware
│   ├── Servers
│   └── Laptops
└── Software
```

Для Tree DocType Frappe автоматически предоставляет Tree View.

Дополнительно используется настройка:

```text
Parent Field (Tree)
```

или `nsm_parent_field` в metadata.

Tree нужен только там, где сама предметная структура действительно иерархическая.

---

## 23. Is Virtual

Флаг:

```text
Is Virtual
```

создаёт Virtual DocType.

Для него Frappe не создаёт обычную таблицу данных.

Источник данных реализуется controller-кодом и может быть:

```text
REST API
внешняя база данных
JSON
CSV
другой backend
```

При этом для пользователя Virtual DocType может выглядеть как обычный DocType и использовать стандартный frontend, resource API и permissions.

Это developer-функция: необходимо реализовать методы чтения/записи в controller.

---

# Часть V. Lifecycle

## 24. Is Submittable

Флаг:

```text
Is Submittable
```

включает формальный lifecycle документа:

```text
Draft
  docstatus = 0

Submitted
  docstatus = 1

Cancelled
  docstatus = 2
```

После Submit документ нельзя свободно редактировать как обычный Draft.

Официальное описание самого поля подчёркивает: submitted document можно Cancel и Amend.

---

## 25. Когда нужен Submittable

Подходит для документов, которые после фиксации должны иметь особый статус достоверности:

```text
акт
заявление
утверждённая операция
проводка
официальная регистрационная запись
```

Не надо делать обычную задачу Submittable только потому, что у неё есть состояние `Done`.

Операционный status и `docstatus` — разные понятия.

---

## 26. Queue in Background

Для Submittable DocType в текущем Frappe существует beta-настройка:

```text
Queue in Background
```

Она позволяет выполнять submit в фоне.

Это специализированная настройка и не нужна обычному документу автоматически.

---

# Часть VI. Settings

## 27. Module

Каждый Standard DocType относится к Module приложения.

Например:

```text
App: training_app
Module: Training
DocType: Request
```

Module влияет на организацию metadata и приложения, но сам по себе не является таблицей данных.

---

## 28. Quick Entry

Флаг:

```text
Quick Entry
```

позволяет создавать Document через небольшой dialog вместо полной формы.

Официальное metadata уточняет: для Quick Entry должен существовать хотя бы один mandatory field, который можно показать в диалоге.

Подходит для простых справочников и быстрых операций.

Не подходит для сложной карточки, где пользователь должен заполнить много связанных данных.

---

## 29. Allow Bulk Edit

Разрешает массовое изменение записей из List View.

Полезно для справочных/операционных полей.

Но если изменения должны проходить строгую бизнес-валидацию или отдельный процесс, массовое редактирование надо оценивать осторожно.

---

## 30. Track Changes

Флаг:

```text
Track Changes
```

включает регистрацию изменений документа через системный механизм Version и отображение истории в timeline.

Это позволяет видеть изменения вроде:

```text
Status
Open → Closed
```

Не надо создавать собственный audit table только ради обычной истории полей, пока штатного Version достаточно.

---

## 31. Track Seen

Флаг:

```text
Track Seen
```

позволяет Framework учитывать пользователей, просмотревших документ.

Это не полноценный механизм юридического подтверждения ознакомления.

---

## 32. Track Views

Отдельная настройка позволяет учитывать просмотры документа.

Её смысл отличается от Track Seen: первое относится к просмотрам как событию/счётчику, второе — к пользователям, видевшим запись.

---

## 33. Allow Copy

Разрешает пользователю создавать новый Document путём копирования существующего.

Полезно для повторяющихся документов.

Но поля с `No Copy` на уровне DocField в новую запись переноситься не должны — это разберём в следующей главе.

---

## 34. Allow Import

Разрешает использовать штатный Data Import для DocType.

Если сущность должна массово загружаться из CSV/XLSX, сначала проверяем этот механизм, а не пишем собственный importer.

---

## 35. Allow Auto Repeat

Флаг:

```text
Allow Auto Repeat
```

разрешает использовать системный механизм Auto Repeat для создания повторяющихся документов.

Это не означает, что каждый новый документ автоматически повторяется — пользователь/администратор должен настроить соответствующий Auto Repeat.

---

## 36. Max Attachments

Можно ограничить максимальное число attachments для документа.

Это относится к встроенным attachments документа, а не к полям `Attach` внутри модели.

---

## 37. Make Attachments Public by Default

Определяет, будут ли новые вложения данного DocType по умолчанию public.

Это security-настройка, поэтому включать её автоматически не стоит.

---

## 38. Protect Attached Files

В текущем metadata DocType существует отдельная настройка защиты attached files.

Её нужно рассматривать вместе с общей моделью file permissions, а не как декоративный флаг.

---

# Часть VII. View Settings

## 39. Search Fields

Позволяет определить дополнительные поля, по которым удобно искать Documents.

Например:

```text
name
subject
external_number
```

Не надо добавлять десятки полей: search fields должны помогать реальному поиску.

---

## 40. Sort Field и Sort Order

Можно задать стандартную сортировку List View.

Например:

```text
Sort Field = modified
Sort Order = DESC
```

или:

```text
Sort Field = priority
```

если это действительно разумно для модели.

---

## 41. Default View

DocType может иметь default view.

В зависимости от доступных views это может быть не только List.

В metadata также существует:

```text
Force Re-route to Default View
```

чтобы направлять пользователя именно в выбранное представление.

---

## 42. Calendar and Gantt

Флаг:

```text
Is Calendar and Gantt
```

включает соответствующие views для DocType.

Но сами календарные поля должны быть корректно определены и настроены.

Наличие даты в сущности ещё не означает, что Calendar View обязательно полезен.

---

## 43. Show Preview Popup

Может включать preview документа в интерфейсе без полного перехода на Form View.

Полезно для быстрой навигации по спискам, но относится только к UX.

---

## 44. Show Name in Global Search

Определяет, показывать ли `name` документа в глобальном поиске.

Если `name` технический и непонятный пользователю, Title Field часто важнее.

---

## 45. Default Print Format

Можно указать стандартный Print Format для документа.

Это не создаёт печатную форму автоматически заново — Framework просто знает, какой существующий формат использовать по умолчанию.

---

# Часть VIII. Form settings

## 46. Timeline Field

В текущем metadata DocType присутствует настройка `timeline_field`.

Она относится к поведению timeline/отображения событий документа.

Это уже более специализированная настройка и обычно не нужна при создании простого DocType.

---

## 47. Hide Toolbar

Позволяет скрыть стандартную toolbar формы.

Использовать надо осторожно: стандартная toolbar содержит важные действия пользователя.

Скрывать её только ради «чистого дизайна» обычно плохая идея.

---

## 48. Description

DocType может иметь описание.

Это полезно для разработчиков и администраторов, чтобы понимать назначение сущности.

Описание не является пользовательским полем Document.

---

## 49. Documentation Link

Можно указать URL документации/справки для DocType.

Это удобный способ связать сложную сущность с внешней инструкцией.

---

# Часть IX. Permissions

## 50. Permissions внутри DocType

DocType содержит таблицу permission rules.

Для каждой Role можно определить права вроде:

```text
Read
Write
Create
Delete
Submit
Cancel
Amend
Report
Import
Export
Print
Email
Share
```

Permissions будут отдельным большим блоком курса.

Здесь достаточно понимать:

> permission model является частью metadata DocType, а не внешним отдельным ACL-модулем.

---

## 51. Permission Level

Конкретные поля DocType могут иметь разные permission levels.

Permission rule Role может разрешать доступ к определённому уровню.

Это позволяет скрывать/защищать часть полей без создания отдельной формы для каждой роли.

---

## 52. Restrict to Domain

В metadata существует ограничение DocType по Domain.

Это более специализированный механизм Framework и обычно используется там, где функциональность должна быть доступна только при активном domain-наборе.

Для обычного собственного App чаще всего он не нужен на старте.

---

# Часть X. Actions, Links и Connections

## 53. Actions

DocType имеет встроенную таблицу:

```text
Document Actions
```

Она позволяет добавлять действия к форме без создания отдельной сущности навигации.

Actions могут вести на route или серверное действие в зависимости от конфигурации.

---

## 54. Links

DocType может описывать связанные Documents через `DocType Link`.

Это используется для Connections/dashboard формы.

Например:

```text
Customer
Connections:
Orders      12
Invoices     8
```

Сами Links не обязательно означают наличие физического поля в текущем DocType: они описывают связь для интерфейса.

---

## 55. Connections

Вкладка Connections показывает связанные объекты и позволяет пользователю быстро переходить между ними.

Не стоит создавать отдельный «Related Objects» DocType только ради отображения таких связей.

---

# Часть XI. Email settings

## 56. Email Append To

DocType может быть настроен так, чтобы входящая email-коммуникация прикреплялась к документам.

Для этого существуют email-related metadata поля вроде:

```text
Email Append To
Sender Field
Sender Name Field
Recipient Account Field
Subject Field
Default Email Template
```

Это не превращает любой DocType в helpdesk автоматически, но даёт базовую email-интеграцию на уровне Framework.

---

# Часть XII. Web View

## 57. Has Web View

Флаг:

```text
Has Web View
```

позволяет документам DocType иметь web-route и отображаться как web pages.

Это отличается от Web Form:

```text
Web Form
= интерфейс ввода/редактирования

Web View
= web-представление Document
```

---

## 58. Route

Для web-enabled DocType можно задать route.

Например документ может быть доступен по URL, построенному на данных записи.

---

## 59. Allow Guest to View

Разрешает гостевой просмотр web view.

Это прямое изменение модели доступа к публичной части, поэтому включать его нужно осознанно.

---

## 60. Published Field

Можно указать поле, определяющее, опубликован ли конкретный Document.

Например:

```text
published = 1
```

Тогда только опубликованные записи должны появляться в web surface.

---

## 61. Index Web Pages for Search

Включает индексацию web pages для website search.

Это уже website-функциональность Framework, а не Desk.

---

# Часть XIII. Advanced

## 62. Database Engine

Для обычных non-Single DocTypes в metadata существует настройка database engine.

По умолчанию используется:

```text
InnoDB
```

Обычному разработчику почти никогда не требуется менять это поле.

---

## 63. Row Format

В текущем DocType metadata существует настройка:

```text
Row Format
```

с вариантами вроде Dynamic/Compressed.

Это низкоуровневая настройка хранения и не является частью обычного проектирования сущности.

---

## 64. Migration Hash

Системное metadata-поле, используемое Framework для внутренней синхронизации/миграций.

Его не нужно проектировать как прикладную настройку.

---

# Часть XIV. Что происходит после Save DocType

## 65. Metadata сохраняется

При создании Standard DocType его metadata представляется JSON-файлом приложения.

Упрощённо:

```json
{
  "doctype": "DocType",
  "name": "Request",
  "module": "Training",
  "fields": [...],
  "permissions": [...]
}
```

---

## 66. Для обычного DocType синхронизируется таблица

Framework создаёт/изменяет таблицу:

```text
tabRequest
```

и колонки, соответствующие persistent DocFields.

При дальнейших изменениях Standard DocType schema синхронизируется через migrate.

---

## 67. Системные поля появляются автоматически

Обычные Documents имеют системные свойства вроде:

```text
name
creation
modified
modified_by
owner
docstatus
idx
```

Их не надо создавать как обычные DocFields.

---

## 68. UI строится автоматически

После создания обычного DocType Framework уже может дать:

```text
Form View
List View
Report View
REST resource
permissions integration
import/export infrastructure
attachments/timeline infrastructure
```

Некоторые дополнительные views требуют соответствующих настроек.

---

# Часть XV. Что DocType НЕ делает автоматически

## 69. Он не придумывает бизнес-модель

Frappe не знает сам:

```text
что означает Status
какие статусы допустимы
кому разрешён переход
когда считать запись просроченной
что считать корректным результатом
```

Это определяет приложение через metadata, Workflow, rules и код.

---

## 70. Он не создаёт сложную бизнес-логику из названия поля

Если создать:

```text
Due Date
```

Frappe не начинает автоматически:

```text
вычислять SLA
эскалировать
уведомлять
переназначать
```

Для этого используются отдельные механизмы.

---

## 71. Он не заменяет продуманную модель данных

Технически можно создать 50 DocTypes за час.

Это не означает, что архитектура хорошая.

Перед созданием DocType надо спросить:

```text
Это самостоятельная сущность?
Она имеет собственный жизненный цикл?
Она должна существовать отдельно?
У неё свои permissions/reporting/API?
Или это просто поле/Link/Child Table?
```

---

# Часть XVI. Как выбирать тип DocType

## 72. Быстрая схема

```text
Нужно много самостоятельных записей?
        │
        ├── да → обычный DocType
        │
        └── нет
             │
             ├── одна глобальная запись?
             │      └── Single
             │
             ├── строки внутри родителя?
             │      └── Child Table
             │
             ├── иерархия?
             │      └── Tree
             │
             └── данные живут не в основной БД Frappe?
                    └── Virtual
```

`Submittable` при этом не отдельная модель хранения, а дополнительный lifecycle-флаг обычного DocType.

---

# Часть XVII. Типичные ошибки новичка

## 73. Делать `name` равным пользовательскому названию всегда

Плохо, если название часто меняется.

Лучше разделять:

```text
name
= стабильный идентификатор

title field
= удобное человеку название
```

---

## 74. Создавать отдельный DocType для каждого списка значений

Если значения:

```text
Low
Normal
High
```

никогда не имеют собственных атрибутов и lifecycle, возможно достаточно `Select`.

Но если элемент должен иметь:

```text
описание
цвет
порядок
активность
права
дополнительные свойства
```

тогда отдельный DocType может быть оправдан.

---

## 75. Использовать Child Table для самостоятельной сущности

Если строка должна иметь собственные:

```text
permissions
workflow
assignments
reports
API lifecycle
```

она, скорее всего, должна быть обычным DocType.

---

## 76. Использовать Single просто потому, что «запись сейчас одна»

Single означает:

> по смыслу системы экземпляр должен быть ровно один.

Это подходит Settings, но не справочнику, который пока содержит один элемент.

---

## 77. Включать Submittable для любого status flow

`Open → Done` не означает `Draft → Submitted`.

Submittable предназначен для фиксации документа, а Workflow/Status — для бизнес-состояния.

---

## 78. Использовать Virtual DocType как способ избежать нормальной модели

Virtual нужен, когда реальный источник данных внешний или нестандартный.

Для обычных данных приложения стандартный DocType проще и надёжнее.

---

# Часть XVIII. Минимальный пример

## 79. Нейтральный `Request`

Представим DocType:

```text
Request
```

Базовые настройки:

```text
Module: Training
Naming: Expression / series-like ID
Title Field: subject
Track Changes: ✓
Allow Import: ✓
Quick Entry: ✗
Is Submittable: ✗
Is Single: ✗
Is Child Table: ✗
Is Tree: ✗
Is Virtual: ✗
```

Fields:

```text
subject
status
priority
due_date
description
```

Это уже нормальная самостоятельная модель для изучения обычного DocType.

---

## 80. Что Framework даст вокруг неё

После создания:

```text
Request metadata
      │
      ├── tabRequest
      ├── Form View
      ├── List View
      ├── REST resource
      ├── permissions
      ├── Report Builder
      ├── attachments
      └── timeline/version при настройке
```

Именно поэтому DocType является главным центром приложения Frappe.

---

# Контрольные вопросы

После этой главы нужно уметь ответить:

1. Чем DocType отличается от Document?
2. Чем Standard DocType отличается от Custom DocType?
3. Зачем Developer Mode?
4. Что такое `name`?
5. Чем `name` отличается от Title Field?
6. Какие naming methods есть в Frappe 16?
7. Когда использовать Child Table?
8. Когда использовать Single?
9. Когда использовать Tree?
10. Когда использовать Virtual DocType?
11. Что включает Is Submittable?
12. Чем `docstatus` отличается от обычного status?
13. Что делает Track Changes?
14. Для чего Allow Import?
15. Что такое Quick Entry?
16. Для чего нужен Default View?
17. Чем Web View отличается от Web Form?
18. Что хранят Actions и Links?
19. Какие вещи Frappe создаёт вокруг обычного DocType автоматически?
20. Почему создание нового DocType должно быть архитектурным решением, а не реакцией на каждое новое поле?

Если эти ответы понятны — можно переходить к самой большой прикладной части metadata: **DocField и свойства полей**.

---

## Официальные источники

- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Naming](https://docs.frappe.io/framework/user/en/basics/doctypes/naming)
- [Types of DocType](https://docs.frappe.io/framework/user/en/tutorial/types-of-doctype)
- [Child / Table DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype)
- [Single DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype)
- [Virtual DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype)
- [Tree View](https://docs.frappe.io/framework/user/en/api/tree)
- [Form & View Settings](https://docs.frappe.io/framework/user/en/basics/doctypes/form_%26_view_settings)
- [Document API](https://docs.frappe.io/framework/user/en/api/document)
- [DocType source metadata](https://github.com/frappe/frappe/blob/develop/frappe/core/doctype/doctype/doctype.json)

---

Следующая глава: **05. DocField и свойства полей — все основные типы, флаги, зависимости и поведение**.
