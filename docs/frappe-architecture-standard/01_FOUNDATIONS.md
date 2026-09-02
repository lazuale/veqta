# 01. Foundations — как Frappe предполагает строить приложения

## 1. Frappe — не пустой web-framework

**[FRAPPE DOCS]** Frappe официально описывает себя как **metadata-driven, full-stack, batteries-included framework**. В Introduction отдельно сказано, что metadata рассматривается как data, а архитектура Framework сознательно монолитна: Frappe поставляется почти со всем, что требуется современному web-приложению.

Источники:

- https://docs.frappe.io/framework/user/en/introduction
- https://docs.frappe.io/framework/user/en/basics
- https://github.com/frappe/frappe/blob/version-16/pyproject.toml

На бытовом языке это значит: Frappe похож не на пустую строительную площадку, а на уже оборудованное здание. Пользователи, роли, документы, формы, списки, файлы, комментарии, API, scheduler и фоновые workers уже существуют.

**[ARCHITECTURAL INFERENCE]** Поэтому обычное приложение должно в первую очередь добавлять предметную модель и правила, а не заново реализовывать инфраструктуру приложения.

---

## 2. Configuration over code — прямой принцип Frappe

**[FRAPPE DOCS]** Страница *Why Frappe Framework?* прямо говорит:

- core philosophy — писать как можно меньше кода;
- предпочитать configuration over code;
- generic capability, нужную многим приложениям, помещать непосредственно во Framework.

Источник:

- https://docs.frappe.io/framework/user/en/basics/why

Это один из самых сильных первичных пруфов для всего стандарта.

Но его нельзя толковать как запрет программирования.

Неправильное прочтение:

```text
metadata хорошо
Python плохо
```

Правильное прочтение:

```text
если Framework уже выражает задачу штатно,
не переписывай тот же механизм кодом без причины
```

Python Controller, hooks, services, background jobs и custom API — штатные части экосистемы Frappe.

---

## 3. Monolith — не «всё в одном файле»

**[FRAPPE DOCS]** Introduction прямо говорит: Frappe придерживается monolithic architecture и поэтому предоставляет integrated application capabilities из коробки.

Источник:

- https://docs.frappe.io/framework/user/en/introduction

Под «монолитом» здесь нельзя понимать плохой код или отсутствие модулей. Речь о другом: основные application concerns работают в одной согласованной платформе.

Например:

```text
DocType
  ├─ metadata
  ├─ persistence
  ├─ permissions
  ├─ form/list UI
  ├─ REST resource
  └─ lifecycle
```

**[ARCHITECTURAL INFERENCE]** Поэтому механическое добавление параллельных Entity/Repository/ACL/API layers может разрушить именно ту интеграцию, ради которой используется Frappe.

Исключение: слой решает отдельную реальную ответственность. Например, сложный integration service или shared stock-calculation service не дублирует Document model, а организует сложную предметную логику.

---

## 4. Основная единица приложения — DocType

**[FRAPPE DOCS]** Документация называет `DocType` **core building block** приложений на Frappe.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes

DocType задаёт metadata модели. Обычный DocType приводит к schema в database и получает стандартные представления Framework.

Поэтому архитектура Frappe начинается не с таблиц SQL и не с REST endpoints, а с вопроса:

> Какие устойчивые документы и записи существуют в предметной области?

При этом не каждое существительное бизнеса обязано стать отдельным DocType. Решение разбирается отдельно в `02_DATA_MODEL.md`.

---

## 5. Document — не просто ORM row

**[FRAPPE DOCS]** Каждый controller DocType наследуется от `frappe.model.document.Document`. Document управляет загрузкой, сохранением и lifecycle документа.

Источник:

- https://docs.frappe.io/framework/user/en/basics/doctypes/controllers

**[UPSTREAM]** В `frappe/model/document.py` `save()` проверяет permissions, выполняет validation и lifecycle hooks.

Источник:

- https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py

Следовательно, Frappe Document — более богатая abstraction, чем обычная database row.

Он находится на пересечении:

```text
metadata
persistence
permissions
lifecycle
relations
versioning hooks
framework events
```

**[ARCHITECTURAL INFERENCE]** Repository, который только переназывает `frappe.get_doc()` и `doc.save()`, обычно не добавляет ценности. Но repository/service не запрещён, если действительно изолирует новую ответственность.

---

## 6. Границы ответственности: Framework, App, Site, External System

Для любого решения сначала нужно понять, **кто им владеет**.

### Framework

Общие инфраструктурные возможности:

```text
DocType/Document model
permissions engine
REST resources
scheduler/background jobs
hooks
Desk foundations
migrate
files/comments/assignments/notifications
```

### App

Устанавливаемый source-controlled пакет:

```text
свои Standard DocType
Controllers
hooks.py
reports
public assets
patches
fixtures
integration code
```

**[FRAPPE DOCS]** App является Python package; `hooks.py` содержит integration points, `modules.txt` — modules, `patches.txt` — migrations.

Источники:

- https://docs.frappe.io/framework/user/en/basics/apps
- https://docs.frappe.io/framework/user/en/tutorial/create-an-app

### Site

Конкретный экземпляр системы. На нём могут существовать runtime/custom configuration:

```text
Custom Field
Property Setter
Client Script
Server Script
Workflow
Notification
site-specific settings
```

Часть таких изменений можно экспортировать в App.

### External System

Система за границей Frappe: ERP, API provider, identity provider, data warehouse и т.д.

**[ARCHITECTURAL INFERENCE]** Ошибка ownership часто и создаёт костыль. Например, если App требует конкретное поле в чужом DocType, это нельзя оставлять только ручным изменением одного dev-site: изменение должно стать воспроизводимой частью App.

---

## 7. App, Module и Package — не одно и то же

### App

**[FRAPPE DOCS]** Source/dependency/install boundary. App имеет Python package, hooks, modules, patches и другие файлы.

Источник:

- https://docs.frappe.io/framework/user/en/basics/apps

### Module

**[FRAPPE DOCS]** Frappe app организуется в modules. Это способ группировки связанных DocType и кода.

Источник:

- https://docs.frappe.io/framework/user/en/basics/apps

Нельзя автоматически приравнивать Module к DDD bounded context. Это может быть удобным проектным решением, но Framework этого не требует.

### Package

**[FRAPPE DOCS]** Начиная с v14 Frappe поддерживает Packages — lightweight app-like packaging custom Module Defs, созданных через UI. Package можно release/import и хранить в Git.

Источник:

- https://docs.frappe.io/framework/user/en/guides/deployment/packages

**[ARCHITECTURAL INFERENCE]** Для серьёзного source-controlled приложения обычный App остаётся основным инструментом. Package полезен, когда задача действительно относится к переносимой low-code/custom конфигурации.

---

## 8. Extensibility — часть замысла, а не обход Framework

**[FRAPPE DOCS]** Страница Why Frappe прямо говорит об extensible architecture: собственные apps могут приносить модели и изменять существующие модели Frappe.

Источник:

- https://docs.frappe.io/framework/user/en/basics/why

Hooks официально определены как места, где App может extend или override standard implementation.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks

Это означает:

```text
не менять core-файлы
        ↓
найти предусмотренный extension seam
        ↓
если seam недостаточен — обосновать custom solution
```

В v16 особенно важен `extend_doctype_class`, позволяющий добавлять поведение существующему DocType без полной замены controller.

---

## 9. Почему стандарт не навязывает Clean Architecture или DDD

Frappe не запрещает применять идеи DDD, services или decomposition.

Но стандарт не позволяет использовать их как самостоятельное доказательство решения.

Плохое обоснование:

> «У каждой Entity должен быть Repository, потому что так принято».

Хорошее обоснование:

> «Эта предметная операция координирует пять DocType и внешний API, не принадлежит lifecycle одного Document, поэтому выделяем отдельный service».

Первое — перенос чужого шаблона.

Второе — объяснение ответственности.

---

## 10. Минимальный тест Frappe-native решения

Решение проходит базовый фильтр, если на пять вопросов есть ясный ответ:

```text
1. Что является бизнес-требованием?
2. Какой native primitive Frappe ближе всего по семантике?
3. Совпадает ли его семантика с требованием?
4. Если нет — какой официальный extension seam существует?
5. Какую новую ответственность добавляет custom code?
```

Ключевой критерий — **совпадение семантики**, а не просто наличие похожей функции в интерфейсе.
