# 40. Website / portal-возможности Framework

В главе 39 мы разобрали `Web Form` — готовый внешний интерфейс вокруг одного DocType.

Но внешняя часть Frappe этим не заканчивается.

Framework умеет отдавать обычные web-страницы, строить server-rendered portal, показывать документы по красивым URL, собирать navbar/sidebar/footer, рендерить Jinja templates и защищать отдельные страницы авторизацией.

Главный вопрос этой главы:

```text
что Frappe умеет как Website / Portal
без отдельного React/Vue frontend
```

Проверено: **2026-08-31**.

---

# Часть I. Сначала разделим четыре интерфейсных слоя

## 1. Desk

`Desk` — внутренний рабочий интерфейс Frappe для System Users.

Типичный URL:

```text
/desk
```

Там находятся:

```text
Workspace
List View
Form View
Report
Kanban
Calendar
настройки
администрирование
```

Desk — SPA и основной back-office UI Framework.

---

## 2. Website

`Website` — server-rendered web-слой Frappe.

Он отвечает за обычные URL вида:

```text
/about
/help
/catalog
/article/some-name
/customer-area
```

Такие страницы рендерятся website router-ом, а не Desk router-ом.

Упрощённо:

```text
Browser
   ↓
Website Router
   ↓
page / template / document web view
   ↓
HTML
```

---

## 3. Portal

`Portal` во Frappe — не отдельное приложение и не второй frontend engine.

Это, по сути:

> **Website-страницы, рассчитанные на вошедшего пользователя и его ограниченный набор функций.**

Например:

```text
/login
   ↓
/my-requests
/my-profile
/my-documents
/support
```

Portal может использовать:

```text
Website pages
Web Forms
DocType Web Views
Portal Settings
roles
permissions
Jinja
Python controllers
```

Поэтому правильнее думать:

```text
Website = внешний web-слой
Portal  = авторизованная часть этого web-слоя
```

а не:

```text
Website и Portal = две разные системы
```

---

## 4. Web Form

`Web Form` — специализированный готовый интерфейс:

```text
один DocType
→ create / view / edit response
```

Он является частью website-слоя, но не равен всему Website/Portal.

Например:

```text
/customer
```

может быть Portal Page,

а внутри неё ссылка:

```text
/new-request
```

может вести на Web Form.

---

## 5. Главная карта

```text
Frappe UI
│
├── Desk
│   └── внутренний back-office
│
└── Website layer
    │
    ├── обычные публичные страницы
    ├── Portal pages после login
    ├── Web Form
    ├── Web Page
    └── DocType Web View
```

Эту карту стоит держать в голове всю главу.

---

# Часть II. Откуда вообще берётся website-страница

## 6. В v16 есть несколько штатных источников web pages

Основные варианты:

```text
1. файл в app/www
2. Web Page DocType
3. Web View обычного DocType
4. Web Form
```

Кроме этого App может добавлять:

```text
website route rules
redirects
custom page renderer
```

Но это уже более разработческий уровень.

---

## 7. Когда использовать какой вариант

| Нужно | Базовый механизм |
|---|---|
| Простая страница, хранимая в App | `www/` page |
| Страница, редактируемая из Desk | `Web Page` |
| Один Document = одна web-страница | `Has Web View` |
| Ввод/редактирование одного DocType | `Web Form` |
| Несколько собственных страниц личного кабинета | Portal pages |
| Полностью собственный application UI | custom frontend |

---

# Часть III. Website routing

## 8. `/api` и Website — разные ветки request lifecycle

Когда приходит HTTP request, Frappe сначала понимает, что это за запрос.

Например:

```text
/api/...
→ API handler

/files/...
→ file handling

/about
→ website router
```

Поэтому обычная portal page не является REST endpoint только потому, что работает через HTTP.

---

## 9. Website Path Resolver

Для обычного website request Framework проходит примерно такую цепочку:

```text
URL
↓
redirect resolution
↓
route resolution
↓
renderer selection
↓
context
↓
template rendering
↓
HTML response
```

Это уже полноценный routing subsystem.

---

## 10. Redirect resolution

До отрисовки страницы Frappe проверяет redirect rules.

Redirect можно задать:

```text
Website Settings
→ Route Redirects
```

или программно через hook:

```python
website_redirects = [
    {"source": "/old", "target": "/new"}
]
```

То есть для простого переноса URL отдельный nginx rule обычно не обязателен.

---

## 11. Route resolution

После redirects Frappe пытается понять, что должно обслуживать route.

В числе штатных источников:

```text
www page
Web Page
WebsiteGenerator / Has Web View
Web Form
website_route_rules
```

Точное решение принимает website path resolver и page renderers Framework.

---

# Часть IV. Файловые страницы `www/`

## 12. Что такое `www/`

Каждое Frappe App может содержать каталог:

```text
my_app/www
```

Файлы в нём напрямую соответствуют website routes.

Например:

```text
my_app/www/about.html
```

даёт route:

```text
/about
```

---

## 13. Самая простая страница

Файл:

```text
my_app/www/hello.html
```

может содержать:

```html
<h1>Hello</h1>
<p>This is my first portal page.</p>
```

После установки App страница будет доступна как:

```text
/hello
```

Никакого отдельного router registration для такого простого route не требуется.

---

## 14. `.html` и `.md`

TemplatePage v16 ищет в website folders в том числе:

```text
.html
.md
/index.html
/index.md
```

То есть можно писать страницу как HTML:

```text
help.html
```

или как Markdown:

```text
help.md
```

Markdown Framework преобразует в HTML перед rendering.

---

## 15. Папка и `index.html`

Например:

```text
www/help/index.html
```

может обслуживать:

```text
/help
```

А:

```text
www/help/faq.html
```

соответствует:

```text
/help/faq
```

Так можно естественно организовывать разделы сайта по каталогам.

---

## 16. HTML обычно не обязан содержать весь `<html>` документ

Frappe website page обычно рендерится внутри базового шаблона.

Например page template может выглядеть так:

```html
{% extends "templates/web.html" %}

{% block page_content %}
<h1>{{ title }}</h1>
<p>{{ message }}</p>
{% endblock %}
```

`templates/web.html` даёт общую оболочку website.

---

## 17. Jinja

Frappe использует Jinja для server-side templates.

Простейший пример:

```html
<h1>Hello, {{ fullname }}</h1>
```

или:

```html
{% if user != "Guest" %}
<p>You are logged in.</p>
{% endif %}
```

Jinja выполняется на сервере до отправки HTML в browser.

---

# Часть V. Python controller страницы

## 18. `.html` можно дополнить одноимённым `.py`

Структура:

```text
www/customer.html
www/customer.py
```

Framework автоматически связывает их.

`customer.py` может содержать:

```python
def get_context(context):
    context.message = "Hello from Python"
```

А `customer.html`:

```html
<h1>{{ message }}</h1>
```

---

## 19. Что такое `context`

`context` — словарь данных, передаваемых в template.

Схема:

```text
Python
context.customer = ...
context.orders = ...
context.title = ...
        ↓
Jinja template
        ↓
HTML
```

Например:

```python
import frappe


def get_context(context):
    context.user = frappe.session.user
```

И в HTML:

```html
<p>{{ user }}</p>
```

---

## 20. `get_context()` — главный controller entry point

Для обычной website page это базовый паттерн:

```python
def get_context(context):
    ...
```

Здесь обычно:

```text
проверяют session
проверяют permissions
получают Documents
строят списки
вычисляют presentation data
добавляют title/breadcrumbs/sidebar flags
```

---

## 21. Защищаем страницу Login requirement

Для `www/` page нет необходимости создавать отдельный auth framework.

Можно явно проверить session:

```python
import frappe
from frappe import _


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(
            _("You need to be logged in to access this page"),
            frappe.PermissionError,
        )
```

Сам Framework использует такой pattern, например на `/me`.

---

## 22. Login — ещё не permission на данные

Очень важное правило:

```text
user != Guest
```

означает только:

```text
пользователь аутентифицирован
```

Это не означает:

```text
ему можно читать любой Document
```

Например так делать опасно:

```python
context.doc = frappe.get_doc("Request", frappe.form_dict.name)
```

если `name` пришёл из URL и вы не проверили доступ.

---

## 23. Правильная portal-модель

Для user-specific страницы логика должна быть примерно такой:

```text
кто пользователь?
↓
имеет ли он доступ к объекту?
↓
только после этого получить данные
↓
передать их в template
```

Например при списке можно использовать permission-aware query:

```python
context.requests = frappe.get_list(
    "Request",
    fields=["name", "subject", "status"],
    filters={"owner": frappe.session.user},
)
```

Точная модель фильтрации зависит от вашей предметной области, но security rule должен жить на server side.

---

# Часть VI. Page properties и caching

## 24. `no_cache`

Для user-specific portal page обычно не нужен общий HTML cache.

В controller можно задать:

```python
no_cache = 1
```

Например стандартная `/me` page Frappe именно так и делает.

Это особенно важно, если HTML зависит от:

```text
frappe.session.user
roles
permissions
персональных данных
```

---

## 25. Почему cache требует внимания

Если страница содержит персональные данные:

```text
Александр → его заявки
Пётр      → его заявки
```

неправильный shared cache был бы критической ошибкой.

Поэтому правило:

```text
статическая публичная страница
→ cache может быть полезен

персональный portal
→ no_cache обычно безопаснее
```

пока вы осознанно не спроектировали другую cache strategy.

---

## 26. Другие page properties

Website template layer знает свойства вроде:

```text
show_sidebar
no_header
no_breadcrumbs
sitemap
base_template
```

То есть для простых различий layout не требуется переписывать весь HTML shell.

---

# Часть VII. CSS и JavaScript рядом со страницей

## 27. Colocated files

Для страницы:

```text
custom_page.html
```

можно положить рядом:

```text
custom_page.css
custom_page.js
custom_page.py
```

Текущий TemplatePage v16 автоматически ищет одноимённые CSS/JS files.

Структура:

```text
www/
├── custom_page.html
├── custom_page.py
├── custom_page.css
└── custom_page.js
```

---

## 28. Когда это удобно

Если JS нужен только одной странице:

```text
customer-dashboard.js
```

логичнее держать его рядом с этой page, чем грузить глобально на всём website.

То же касается CSS.

---

# Часть VIII. `Web Page` — страница без файлов вручную

## 29. Что такое Web Page

`Web Page` — штатный DocType Framework для создания website-страниц из Desk.

То есть вместо:

```text
создать my_app/www/info.html
commit
установить app
```

можно:

```text
Desk
→ Web Page
→ New
```

и создать страницу как Document.

---

## 30. Web Page и `www/` — два разных способа

### `www/`

Хорошо подходит, когда страница:

```text
часть приложения
должна храниться в Git
имеет Python controller
имеет сложную логику
```

### Web Page

Хорошо подходит, когда страницу нужно:

```text
быстро сделать из Desk
редактировать контент без изменения App
собрать из page blocks
публиковать как CMS-like content
```

---

## 31. Основные поля Web Page v16

В текущей metadata есть, среди прочего:

```text
Title
Route
Published
Content Type
Main Section
Page Building Blocks
Dynamic Route
Context Script
Javascript
CSS
Start Date
End Date
Meta Title
Meta Description
Meta Image
Show Sidebar
Website Sidebar
Enable Comments
Breadcrumbs
```

Это уже маленький встроенный CMS-like механизм.

---

# Часть IX. Content Type Web Page

## 32. Rich Text

Можно выбрать:

```text
Content Type = Rich Text
```

и редактировать страницу через Text Editor.

Подходит для:

```text
инструкции
контакты
описание услуги
простая информационная страница
```

---

## 33. Markdown

Можно выбрать:

```text
Content Type = Markdown
```

и писать:

```markdown
# Заголовок

Текст страницы.

- пункт 1
- пункт 2
```

Framework преобразует Markdown в HTML.

---

## 34. HTML

Режим:

```text
Content Type = HTML
```

даёт больше контроля над markup.

Но вместе со свободой растёт ответственность за:

```text
HTML structure
XSS/security
maintainability
```

---

## 35. Page Builder

В v16 `Web Page` по умолчанию поддерживает:

```text
Content Type = Page Builder
```

Страница собирается из:

```text
Web Page Blocks
```

каждый из которых использует:

```text
Web Template
+
values
```

Это low-code слой между простым Rich Text и ручным HTML/template coding.

---

## 36. Web Template

`Web Template` v16 поддерживает типы:

```text
Component
Section
Navbar
Footer
```

Внутри используется Jinja template и набор configurable fields.

То есть можно создать повторяемый website component и использовать его в Page Builder.

---

## 37. Slideshow

`Web Page` также поддерживает:

```text
Content Type = Slideshow
```

связанный с `Website Slideshow`.

Это специализированный content type, а не универсальный layout engine.

---

# Часть X. Publishing Web Page

## 38. Route

Например:

```text
Title = Help
Route = help
```

страница доступна как:

```text
/help
```

Route должен быть уникальным в рамках соответствующего website routing context.

---

## 39. Published

Если:

```text
Published = 0
```

страница не должна считаться опубликованной website page.

Это основной lifecycle switch для Web Page.

---

## 40. Start Date / End Date

У Web Page есть scheduling publication через:

```text
Start Date
End Date
```

Controller содержит daily logic, которая может публиковать/снимать публикацию по указанному диапазону.

Это удобно для:

```text
временной акции
объявления
регламента на период
страницы события
```

Но работа schedule-dependent поведения требует нормально работающего scheduler.

---

# Часть XI. Dynamic Web Page

## 41. `Dynamic Route`

Web Page v16 умеет dynamic route.

Пример:

```text
/project/<name>
```

Тогда один Web Page template может обслуживать:

```text
/project/PROJ-0001
/project/PROJ-0002
/project/PROJ-0003
```

---

## 42. Route parameter

Dynamic часть попадает в request data и может использоваться при построении context.

По смыслу:

```python
context.project = frappe.get_doc(
    "Project",
    frappe.form_dict.name,
)
```

Но этот пример требует обязательного security комментария.

---

## 43. Dynamic route parameter нельзя считать доверенным

URL контролирует пользователь.

Если страница:

```text
/project/<name>
```

пользователь может попробовать:

```text
/project/любой-другой-name
```

Поэтому dynamic route сам по себе не является permission system.

Нужно отдельно проверять:

```text
существование Document
permission пользователя
website visibility
owner/customer binding
```

---

# Часть XII. `Context Script` Web Page

## 44. Server-side context прямо из Web Page

В Web Page есть:

```text
Context Script
```

Это Python code, выполняемый через safe execution mechanism и дополняющий page context.

Например по смыслу:

```python
context.message = "Hello"
```

После этого HTML/Jinja content может использовать:

```jinja2
{{ message }}
```

---

## 45. Где Context Script полезен

Для небольшой динамической страницы:

```text
получить несколько значений
показать текущую дату
выбрать публичные записи
подготовить небольшую структуру данных
```

можно обойтись без отдельного `.py` файла App.

---

## 46. Где Context Script уже плохая граница

Если внутри получается:

```text
150 строк Python
10 разных DocTypes
сложные permission checks
бизнес-операции
API integrations
дублирование controller logic
```

это уже application code.

Такой код лучше переносить в собственное App, где есть:

```text
Git
tests
modules
review
normal Python files
```

---

# Часть XIII. JavaScript и CSS Web Page

## 47. Javascript

Web Page имеет поле:

```text
Javascript
```

для page-specific client code.

Например можно добавить простую интерактивность после rendering.

Но JavaScript страницы по-прежнему работает в browser и не является security layer.

---

## 48. CSS

Через:

```text
Insert Style
CSS
```

можно задать page-level стили.

Для небольшой визуальной правки это нормально.

Для всей design system лучше использовать:

```text
Website Theme
Web Template
App assets
```

а не копировать CSS в каждую страницу.

---

# Часть XIV. Website Theme

## 49. Что такое Website Theme

`Website Theme` управляет общим визуальным стилем website layer.

В v16 есть настройки вроде:

```text
font
font size
primary color
text color
background color
button styles
custom SCSS
custom overrides
JavaScript
```

То есть внешний website не обязан выглядеть как стандартный Frappe без возможности кастомизации.

---

## 50. Theme относится к Website, а не к Desk

Это важно.

```text
Website Theme
→ public/portal website pages

Desk theme / Desk UI
→ другой слой
```

Изменение Website Theme не означает автоматический redesign Desk.

---

# Часть XV. Website Settings

## 51. Website Settings — глобальная конфигурация website

`Website Settings` — Single DocType с глобальными настройками website layer конкретного Site.

Текущая v16 metadata содержит большие группы:

```text
Home
Navbar
Footer
Integrations
Header / Robots
Redirects
```

---

## 52. Home Page

Поле:

```text
Home Page
```

задаёт route, который будет использоваться как landing page сайта.

Например:

```text
home
portal
about
```

Framework валидирует, что route реально существует.

---

## 53. Title Prefix

Можно задать:

```text
Title Prefix
```

чтобы browser title выглядел по схеме:

```text
Company - Page Title
```

---

## 54. Brand

Website Settings позволяет настроить:

```text
Brand Image
Brand HTML
FavIcon
App Name
App Logo
Splash Image
```

То есть базовый branding можно сделать без переписывания base template.

---

## 55. Navbar

Есть:

```text
Top Bar Items
Navbar Search
Show Language Picker
Call To Action
Navbar Template
```

Можно собрать обычную верхнюю навигацию website.

---

## 56. Footer

Есть:

```text
Footer Items
Copyright
Footer Logo
Address
Footer Template
Powered By text
```

Таким образом общий footer централизован, а не копируется на каждую страницу.

---

## 57. Signup / Login options

Website Settings содержит:

```text
Disable signups
Hide Login
Show footer on login
```

По умолчанию в metadata v16 `Disable signups` включён.

То есть self-registration не нужно считать автоматически доступной на любом новом Site.

---

## 58. `<head>` и robots.txt

Есть настройки:

```text
<head> HTML
Robots.txt
```

Они относятся ко всему website и полезны для:

```text
verification tags
SEO metadata infrastructure
crawler rules
```

Но вставлять произвольный глобальный JS через `<head>` только потому, что так быстрее, — плохая привычка, если есть нормальный asset mechanism.

---

## 59. Route Redirects

Website Settings поддерживает таблицу:

```text
Route Redirects
```

Это удобно при изменении routes:

```text
/old-help
→ /help
```

или более сложных regex mappings.

---

# Часть XVI. Website Sidebar

## 60. Website Sidebar

Для Web Page и Web Form можно выбрать:

```text
Website Sidebar
```

Сам `Website Sidebar` содержит набор:

```text
Title
Route
Group
```

Это простой способ собрать боковую навигацию раздела.

---

## 61. Пример

```text
Customer Area
├── Home      /customer
├── Requests  /request/list
├── Help      /help
└── Profile   /me
```

Один Website Sidebar можно использовать на нескольких страницах, чтобы раздел выглядел единообразно.

---

# Часть XVII. Что именно значит Portal

## 62. Portal — это композиция механизмов

В Frappe нет необходимости искать один объект:

```text
"Portal"
```

который magically создаёт личный кабинет.

Portal обычно складывается из:

```text
Website User
+
login/session
+
portal pages
+
Portal Settings
+
roles
+
permissions
+
Web Forms
+
website navigation
```

---

## 63. Website User и System User

На концептуальном уровне:

```text
System User
→ имеет Desk access

Website User
→ предназначен для website/portal access без полноценного Desk
```

Website User всё равно является Frappe `User` и может иметь Roles.

Но сам факт наличия account не превращает его в System User.

---

## 64. Portal roles

Website Users можно назначать Roles.

Например:

```text
Customer
Supplier
Partner
Student
```

Такие roles могут использоваться для:

```text
portal menu visibility
data permissions
home page selection
custom controller checks
```

---

# Часть XVIII. Portal Settings

## 65. Что содержит Portal Settings v16

Текущий Single DocType содержит:

```text
Default Role at Time of Signup
Default Portal Home
Hide Standard Menu
Portal Menu
Custom Menu Items
```

Это именно настройки portal navigation/account flow, а не глобального public website shell.

---

## 66. Default Role at Time of Signup

Поле:

```text
Default Role at Time of Signup
```

может назначать роль новым portal users.

Но реальная registration policy всё равно зависит от Website Settings и custom app logic.

---

## 67. Default Portal Home

Можно задать route вроде:

```text
/customer
```

который будет использоваться как portal home для logged-in flow.

Это отличается от общего:

```text
Website Settings → Home Page
```

потому что public homepage и portal homepage — не обязательно одна страница.

---

## 68. Portal Menu Item

Элемент portal menu содержит:

```text
Title
Enabled
Route
Reference Document Type
Role
```

Например:

```text
Title = My Requests
Route = /request/list
Role  = Customer
```

---

## 69. Role в Portal Menu Item фильтрует видимость меню

Если menu item назначен role:

```text
Customer
```

его можно показать только пользователям с этой role.

Это полезно для UX.

Но теперь самый важный security нюанс.

---

## 70. Скрытое меню не равно защищённому route

Нельзя делать так:

```text
ссылка скрыта от Supplier
→ значит Supplier не сможет открыть URL вручную
```

Menu visibility — интерфейсное правило.

Настоящая защита должна находиться в:

```text
controller
Document permissions
permission-aware query
server method
```

Пользователь всегда может вручную ввести известный URL.

---

# Часть XIX. Portal menu через App hooks

## 71. `portal_menu_items`

App может добавлять sidebar items программно:

```python
portal_menu_items = [
    {
        "title": "Dashboard",
        "route": "/dashboard",
        "role": "Customer",
    },
    {
        "title": "Requests",
        "route": "/requests",
        "role": "Customer",
    },
]
```

Это удобно, когда menu — часть App architecture.

---

## 72. `standard_portal_menu_items`

Есть также:

```python
standard_portal_menu_items
```

Эти items синхронизируются в `Portal Settings` database record.

Это позволяет App поставить стандартный набор portal links, который затем участвует в общих portal settings.

---

# Часть XX. Home Page selection

## 73. Homepage может зависеть от пользователя

Для portal нет требования отправлять всех на один `/home`.

Можно иметь:

```text
Customer → /orders
Supplier → /bills
Manager  → /dashboard
```

---

## 74. Hooks для homepage

Framework поддерживает:

```python
homepage = "homepage"
```

и role-based:

```python
role_home_page = {
    "Customer": "orders",
    "Supplier": "bills",
}
```

А для более сложной логики:

```python
get_website_user_home_page = "app.website.get_home_page"
```

---

## 75. Приоритет hook-based homepage

Официальная hooks documentation указывает:

```text
get_website_user_home_page
→ выше role_home_page
→ выше homepage
```

Если используется более динамическая логика, она имеет приоритет над простым static homepage hook.

---

# Часть XXI. Jinja в website

## 76. Jinja — presentation layer

В template можно писать:

```jinja2
{% for request in requests %}
    <a href="/request/{{ request.name }}">
        {{ request.subject }}
    </a>
{% endfor %}
```

Это server-side rendering.

Browser получает уже итоговый HTML.

---

## 77. Jinja имеет Frappe API

Framework предоставляет whitelisted Jinja helpers, например:

```text
frappe.format
frappe.format_date
frappe.get_url
frappe.get_doc
```

и другие documented methods.

Но доступность helper-а не означает, что любой data access автоматически безопасен для portal.

---

## 78. Не тащи сложную data logic в template

Плохой template:

```text
20 запросов к базе
permission logic
business calculations
сложные ветвления
```

Лучше:

```text
Python get_context()
→ подготовил данные

Jinja
→ красиво показал
```

То есть Jinja — прежде всего presentation layer.

---

# Часть XXII. Global website context

## 79. `website_context`

App может глобально добавить значения в website context:

```python
website_context = {
    "support_email": "support@example.com"
}
```

После этого значение может быть доступно website templates.

---

## 80. `update_website_context`

Для динамической логики есть hook:

```python
update_website_context = "app.website.update_context"
```

Например:

```python
def update_context(context):
    context.my_value = "..."
```

Этот код может менять общий context множества страниц.

Использовать его стоит для действительно глобальных вещей, а не для логики одной конкретной page.

---

# Часть XXIII. Global website assets

## 81. `web_include_css`

App может подключить CSS ко всему website layer:

```python
web_include_css = [
    "/assets/my_app/css/website.css"
]
```

---

## 82. `web_include_js`

Аналогично JS:

```python
web_include_js = [
    "/assets/my_app/js/website.js"
]
```

В `Website Settings.get_website_settings()` текущий v16 добавляет эти hooks в общий website context.

---

## 83. Desk assets и Website assets — разные hooks

Не путай:

```text
app_include_js
app_include_css
→ Desk

web_include_js
web_include_css
→ Website / Portal
```

Это два разных frontend contexts.

---

# Часть XXIV. `Has Web View` у обычного DocType

## 84. Зачем это нужно

Представим DocType:

```text
Article
```

У него сотни Documents:

```text
ARTICLE-001
ARTICLE-002
ARTICLE-003
```

Создавать вручную сотни Web Pages бессмысленно.

Вместо этого можно сделать:

```text
Article
→ Has Web View
```

и каждый Document сможет иметь свою website page.

---

## 85. Модель

```text
один DocType
+
один web template
+
много Documents
=
много web routes
```

Например:

```text
/articles/article-one
/articles/article-two
/articles/article-three
```

---

## 86. `Has Web View`

В DocType можно включить website view capability.

В учебном tutorial Frappe для этого используются настройки вроде:

```text
Has Web View
Allow Guest to View
Route
Published field
```

Точные доступные поля зависят от metadata DocType и режима разработки, но архитектурная идея стабильна:

> Document становится website generator object.

---

## 87. `WebsiteGenerator`

Под капотом Framework использует модель `WebsiteGenerator`.

Она занимается, среди прочего:

```text
route generation
published condition
cache invalidation
website search index
page information
```

То есть это не просто Jinja trick.

---

## 88. Web Page и Has Web View — важное различие

### Web Page

```text
один Web Page Document
→ одна website page
```

### Has Web View

```text
каждый Document бизнес-DocType
→ собственная website page
```

Например:

```text
О компании
→ Web Page

Каталог из 500 Articles
→ Has Web View
```

---

## 89. Detail template и list row template

Для website-enabled DocType обычно используются templates по смыслу:

```text
article.html
article_row.html
```

Первый отображает один Document.

Второй — один элемент в списке web views.

Это позволяет строить:

```text
/articles
→ список

/articles/some-article
→ detail page
```

---

# Часть XXV. `website_route_rules`

## 90. Когда прямого `www/` route мало

Допустим есть:

```text
/projects
```

и нужен dynamic URL:

```text
/project/<name>
```

App может задать:

```python
website_route_rules = [
    {
        "from_route": "/project/<name>",
        "to_route": "app/projects/project",
    },
]
```

---

## 91. Controller получает dynamic parameter

Например:

```python
import frappe


def get_context(context):
    project_name = frappe.form_dict.name
    context.project = frappe.get_doc("Project", project_name)
```

Но снова:

> route mapping не является permission check.

Если Document приватный, access нужно проверить отдельно.

---

# Часть XXVI. Custom Page Renderer

## 92. Frappe позволяет добавить собственный renderer

Для совсем нестандартного website response есть hook:

```python
page_renderer = "path.to.CustomPage"
```

Custom renderer должен реализовать по смыслу:

```text
can_render()
render()
```

---

## 93. Это уже advanced boundary

Если задача закрывается через:

```text
www page
Web Page
Web Form
Has Web View
```

писать custom renderer обычно не нужно.

Custom Page Renderer — низкоуровневое extension point Framework, а не первый инструмент для обычного portal.

---

# Часть XXVII. Public Website против Portal

## 94. Публичная страница

Например:

```text
/about
/help
/contacts
/articles
```

может работать под:

```text
Guest
```

и быть доступной без session.

---

## 95. Portal page

Например:

```text
/my-orders
/my-requests
/my-documents
```

обычно требует:

```text
user != Guest
```

и затем data-level permission checks.

---

## 96. Web Page v16 не имеет отдельного `Login Required` checkbox

В metadata `Web Page` есть publication/content/sidebar/scripts и другие настройки, но нет такого же отдельного поля:

```text
Login Required
```

как у Web Form.

Поэтому `Web Page` естественнее воспринимать как website content mechanism.

Если нужна настоящая защищённая portal page, обычно яснее использовать:

```text
www page + Python controller
```

или другой application-level route с явной permission logic.

---

# Часть XXVIII. Безопасность portal

## 97. Самая опасная ошибка — фильтровать только интерфейс

Например:

```text
скрыли чужие документы из HTML
```

но backend endpoint всё равно позволяет запросить их по `name`.

Это не security.

Правильная граница:

```text
backend определяет, что доступно
frontend только показывает уже разрешённое
```

---

## 98. URL parameter всегда недоверенный

Это относится ко всему:

```text
/project/<name>
/request?id=...
/customer/<customer>
```

Пользователь может изменить параметр вручную.

Нельзя считать:

```text
он получил ссылку на CUST-001
→ значит никогда не попробует CUST-002
```

---

## 99. Menu role — не data permission

Ещё раз:

```text
Role в Portal Menu
```

решает:

```text
показывать ли ссылку
```

а не:

```text
можно ли читать Document
```

Это разные уровни.

---

## 100. `frappe.get_all()` требует особой осторожности

В application code `get_all` используется как более прямой data query и не является заменой permission-aware retrieval.

Для portal нужно сознательно выбирать:

```text
get_list с permissions
явный permission check
собственный безопасный query
```

в зависимости от задачи.

Не превращай website controller в обход permission model только ради удобства.

---

## 101. Jinja тоже может утечь данные

То, что query написан внутри template, не делает его безопаснее.

Если template получает слишком много данных, browser увидит их в итоговом HTML.

Правило:

> В context должны попадать только те данные, которые пользователь действительно имеет право увидеть.

---

# Часть XXIX. Website search и SEO

## 102. WebsiteGenerator умеет участвовать в search index

`WebsiteGenerator` содержит механизм обновления website search index при изменении опубликованного Document.

Это ещё одно отличие web views от произвольной custom HTML page.

---

## 103. Meta data

Web Page поддерживает:

```text
Meta Title
Meta Description
Meta Image
```

Website Settings также участвует в глобальном branding/title/head configuration.

Это позволяет делать нормальные public website pages без отдельной CMS только ради basic metadata.

---

## 104. Portal pages обычно не должны индексировать персональные данные

Если route содержит:

```text
my-orders
profile
private-request
```

не нужно рассчитывать на SEO-механику как на access control.

Private page должна быть защищена authorization logic независимо от robots/sitemap.

`robots.txt` — инструкция crawler-у, а не security barrier.

---

# Часть XXX. Website comments

## 105. Web Page умеет comments

У Web Page есть:

```text
Enable Comments
```

Controller v16 загружает comment list и допускает guest comment context для этого режима.

Это может быть полезно для публичного discussion/content scenario.

---

## 106. Но comments требуют anti-abuse мышления

Если публичная страница допускает guest interaction, нужно учитывать:

```text
spam
moderation
rate limiting
notifications
personal data
```

Наличие штатной кнопки не означает, что конкретному сайту всегда нужны публичные comments.

---

# Часть XXXI. Типовой простой portal

## 107. Как может выглядеть минимальный portal без custom frontend

```text
/login
  ↓
/customer
  ├── /request/list
  ├── /request/new
  ├── /help
  └── /me
```

Где:

```text
/customer
→ собственная portal page

/request/*
→ Web Form

/help
→ Web Page

/me
→ стандартная account page
```

Навигацию можно собрать через Portal Settings / Website Sidebar.

---

## 108. Уже получается полезный личный кабинет

Без React/Vue можно получить:

```text
login
role-based navigation
несколько страниц
список своих records
форму создания
форму редактирования
comments
attachments
print
profile/account page
```

Для многих B2B/self-service процессов этого действительно достаточно.

---

# Часть XXXII. Где Portal начинает упираться в потолок

## 109. Server-rendered portal хорош, если UX относительно обычный

Например:

```text
открыть страницу
посмотреть список
открыть документ
заполнить форму
перейти на следующую страницу
```

Это естественная модель Website/Portal.

---

## 110. Первый признак выхода за границу

Если интерфейс требует:

```text
постоянно живого client state
```

например:

```text
много панелей на одном экране
instant filters без reload
complex drag-and-drop
realtime board
rich data grid
многоступенчатый app-like navigation
```

server-rendered page начинает требовать слишком много custom JS.

---

## 111. Второй признак — Web Pages становятся shell для огромного JS

Если `.html` фактически содержит только:

```html
<div id="app"></div>
```

а дальше 5000 строк custom JavaScript вручную строят SPA,

то вы уже по сути пишете custom frontend, только неудобным способом.

Лучше признать архитектурную границу явно.

---

# Часть XXXIII. Web Form vs Web Page vs Has Web View vs Portal Page

## 112. Web Form

Выбираем, когда задача:

```text
ввести / показать / изменить один Document
```

Например:

```text
создать обращение
отредактировать анкету
посмотреть свой response
```

---

## 113. Web Page

Выбираем, когда задача:

```text
показать одну content page
```

Например:

```text
FAQ
правила
контакты
landing page
```

---

## 114. Has Web View

Выбираем, когда:

```text
много Documents одного DocType
должны иметь собственные public/web pages
```

Например:

```text
Article
Product-like catalog object
Job opening
Public project
```

---

## 115. `www/` Portal Page

Выбираем, когда:

```text
нужен свой layout
несколько источников данных
Python context
явная auth/permission logic
```

Например:

```text
Customer Dashboard
```

где одновременно показаны:

```text
profile
open requests
last invoices
notifications
```

---

# Часть XXXIV. Portal против Desk

## 116. Не нужно делать Portal для внутренних power users без причины

Внутреннему сотруднику часто уже нужны:

```text
List View
filters
bulk actions
reports
workflow actions
assignments
comments
timeline
permissions
```

Desk всё это уже умеет.

Строить второй внутренний интерфейс поверх Portal имеет смысл только если есть конкретная UX-причина.

---

## 117. Portal особенно полезен для ограниченного пользователя

Например:

```text
клиент
подрядчик
поставщик
соискатель
партнёр
сотрудник self-service сценария
```

которому не нужен весь Desk.

---

# Часть XXXV. Portal против custom frontend

## 118. Portal использует HTML, которое рендерит Frappe

Схема:

```text
Frappe server
→ Jinja
→ HTML
→ browser
```

Client JavaScript можно добавлять, но основа остаётся server-rendered.

---

## 119. Custom frontend переворачивает модель

Например:

```text
React / Vue / Svelte / mobile app
```

Тогда:

```text
frontend application
→ REST/RPC
→ Frappe backend
```

Именно поэтому следующие главы курса посвящены:

```text
REST API
RPC
Authentication
```

---

## 120. Не нужно уходить в custom frontend слишком рано

Если задача закрывается так:

```text
Web Page
+
Web Form
+
Portal Menu
```

создание отдельного SPA добавит:

```text
frontend build stack
routing
state management
API layer
auth handling
error handling
deployment
CORS/CSRF considerations
```

без обязательной пользы.

---

## 121. Но не нужно и мучить Portal бесконечным JS

Обратная ошибка:

```text
нам нужен настоящий application UX,
но мы принципиально не хотим отдельный frontend
```

и в итоге Web Page превращается в самодельный framework.

Нормальная граница:

```text
стандартный website flow
→ Portal

application-like client UX
→ custom frontend
```

---

# Часть XXXVI. Практика без собственного App

На этом этапе курса мы ещё не дошли до главы про создание собственного App, поэтому сначала проверим то, что можно сделать штатно из Desk.

## 122. Создай Web Page

Открой:

```text
Web Page
→ New
```

Задай:

```text
Title     = Portal Demo
Route     = portal-demo
Published = on
```

---

## 123. Выбери Content Type

Для первого упражнения удобно:

```text
Markdown
```

Добавь:

```markdown
# Portal Demo

Это тестовая website-страница Frappe Framework 16.

- Web Page работает вне Desk
- Route контролирует URL
- Контент хранится как Document
```

Сохрани.

---

## 124. Открой route

Открой:

```text
/portal-demo
```

Проверь:

```text
страница открывается без Desk
общая website navbar/footer применяются
URL соответствует Route
```

---

## 125. Проверь Published

Выключи:

```text
Published
```

и снова попробуй открыть страницу.

После проверки включи обратно.

Цель:

> увидеть, что Web Page — website generator Document, а не просто запись текста в базе.

---

## 126. Добавь Meta fields

Заполни:

```text
Meta Title       = Portal Demo
Meta Description = Test Frappe website page
```

Открой HTML страницы через browser dev tools и посмотри итоговый `<head>`.

---

## 127. Создай Website Sidebar

Создай:

```text
Website Sidebar = Demo Sidebar
```

Добавь:

```text
Portal Demo  → /portal-demo
Request      → /request/new
My Account   → /me
```

Вернись в Web Page и включи:

```text
Show Sidebar
Website Sidebar = Demo Sidebar
```

---

## 128. Свяжи Web Page с Web Form из главы 39

На странице добавь ссылку:

```markdown
[Создать заявку](/request/new)
```

Теперь у тебя уже есть простейший внешний flow:

```text
информационная page
→ Web Form
→ Document
```

без собственного frontend.

---

# Часть XXXVII. Практика, которую сделаем позже после главы App

## 129. Файловая portal page

После главы 48 про собственное App вернёмся к конструкции:

```text
my_app/www/customer.html
my_app/www/customer.py
my_app/www/customer.css
my_app/www/customer.js
```

и создадим настоящий authenticated portal page.

---

## 130. Минимальный будущий controller

Он будет выглядеть примерно так:

```python
import frappe
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(
            _("You need to be logged in"),
            frappe.PermissionError,
        )

    context.requests = frappe.get_list(
        "Request",
        fields=["name", "subject", "status"],
        filters={"owner": frappe.session.user},
        order_by="creation desc",
    )
```

А template:

```html
{% extends "templates/web.html" %}

{% block page_content %}
<h1>My Requests</h1>

{% for request in requests %}
    <div>
        {{ request.subject }} — {{ request.status }}
    </div>
{% endfor %}
{% endblock %}
```

Пока этот код нужно понять концептуально, а не обязательно повторять руками до главы собственного App.

---

# Часть XXXVIII. Типичные ошибки

## 131. Ошибка: считать Portal отдельным продуктом внутри Frappe

Нет.

Portal — это архитектурный сценарий поверх website layer.

Не нужно искать кнопку:

```text
Create Portal Application
```

как обязательную точку входа.

---

## 132. Ошибка: использовать Web Page для ввода business Document

Если пользователь должен:

```text
заполнить поля
создать Document
редактировать response
```

обычно сначала нужно смотреть на:

```text
Web Form
```

а не писать HTML form вручную внутри Web Page.

---

## 133. Ошибка: делать 500 Web Pages вместо Has Web View

Если есть:

```text
500 Articles
```

не нужно создавать:

```text
500 Web Page Documents
```

если сама модель `Article` должна иметь website representation.

Для этого существует:

```text
Has Web View
```

---

## 134. Ошибка: скрыть ссылку и считать route защищённым

```text
Portal Menu Role
```

не заменяет permission check.

Это одна из самых важных мыслей всей главы.

---

## 135. Ошибка: использовать robots.txt как security

```text
Disallow: /private
```

не запрещает человеку открыть:

```text
/private
```

Robots — crawler policy, не authentication.

---

## 136. Ошибка: отдавать весь Document в context «на всякий случай»

Например:

```python
context.customer = frappe.get_doc("Customer", name)
```

а template использует только два поля.

Это повышает риск случайно вывести чувствительные данные позже.

Лучше заранее проектировать минимальный presentation data set.

---

## 137. Ошибка: весь website JS подключать глобально

Если code нужен одной странице, не обязательно грузить его через:

```text
web_include_js
```

на каждой website page.

Используй colocated JS или page-specific mechanism.

---

## 138. Ошибка: делать всю бизнес-логику в `get_context()`

`get_context()` должен в первую очередь:

```text
проверить доступ
подготовить presentation data
```

Если он начинает выполнять:

```text
сложные транзакции
массовые изменения
integration workflows
```

архитектуру пора разделять.

Для операций дальше будут:

```text
RPC methods
Document methods
services
controllers
```

---

## 139. Ошибка: использовать GET page rendering для изменения данных

Открытие:

```text
/customer
```

не должно само по себе выполнять опасную business command вроде:

```text
approve order
delete document
pay invoice
```

Page rendering должен быть в основном read-oriented.

Изменяющие операции должны иметь отдельный контролируемый endpoint / method с подходящим HTTP/auth/permission flow.

---

# Часть XXXIX. Decision table

## 140. Что выбирать

| Задача | Инструмент |
|---|---|
| Простая информационная page из Desk | `Web Page` |
| Landing page из блоков | `Web Page + Page Builder` |
| Страница как часть App | `www/*.html` / `.md` |
| Нужен Python context | `www page + .py` |
| Нужна user-specific protected page | Portal page + server-side checks |
| Один Document должен иметь website URL | `Has Web View` |
| Публичная/portal форма над DocType | `Web Form` |
| Общий navbar/footer/home | `Website Settings` |
| Portal sidebar/default role/home | `Portal Settings` |
| Повторяемые website sections | `Web Template` |
| Общая визуальная тема | `Website Theme` |
| Clean dynamic route | `Dynamic Web Page` / `website_route_rules` |
| Полностью application-like UX | custom frontend |

---

# Часть XL. Архитектурная лестница

## 141. От самого простого к самому сложному

```text
Text page
→ Web Page

нужны повторяемые blocks
→ Page Builder / Web Template

нужна форма
→ Web Form

нужно отображать множество Documents
→ Has Web View

нужна своя server-rendered page
→ www + Jinja + get_context

нужен полноценный portal
→ несколько таких pages + permissions + Portal Settings

нужен SPA-like UX
→ custom frontend
```

Это хороший порядок выбора решения.

---

# Что нужно запомнить

1. Website — отдельный server-rendered UI layer Frappe, не Desk.
2. Portal — не отдельный frontend engine, а авторизованный сценарий поверх Website layer.
3. Самые важные sources web pages: `www/`, `Web Page`, `Has Web View`, `Web Form`.
4. Файл `app/www/page.html` автоматически соответствует route `/page`.
5. Рядом с page можно иметь `.py`, `.css` и `.js` того же имени.
6. `get_context(context)` подготавливает server-side данные для Jinja template.
7. Для персональных страниц обычно нужен `no_cache = 1`.
8. Login check и Document permission — разные проверки.
9. URL parameters всегда недоверенные и не дают permission сами по себе.
10. `Web Page` — встроенный CMS-like DocType с Rich Text, Markdown, HTML, Page Builder и Slideshow.
11. Web Page поддерживает route, publication, dynamic route, Context Script, JS/CSS, metadata, sidebar и comments.
12. `Page Builder` строится из Web Page Blocks и Web Templates.
13. `Website Settings` управляет глобальным website shell: home, theme, branding, navbar, footer, signup, head/robots и redirects.
14. `Portal Settings` управляет portal home, default role и portal menu.
15. Role у Portal Menu Item управляет видимостью ссылки, но не заменяет server-side permissions.
16. `Website Sidebar` — простой reusable sidebar для Web Pages/Web Forms.
17. `Has Web View` нужен, когда каждый Document одного DocType должен стать website page.
18. `WebsiteGenerator` обеспечивает routes/publication/cache/search mechanics для document web views.
19. `website_route_rules` позволяет Apps делать clean dynamic routes.
20. `web_include_css/js` относятся к Website, а `app_include_css/js` — к Desk.
21. Jinja — presentation layer; сложную data/security logic лучше готовить в Python.
22. Public website, portal и custom frontend — разные уровни, их не нужно смешивать без необходимости.
23. Пока UX остаётся обычным server-rendered flow, штатный Portal может закрыть очень много задач без SPA.
24. Когда interface превращается в rich client application, честная граница — custom frontend + API.

---

# Источники

Официальная документация Frappe Framework:

- [Portal Pages](https://docs.frappe.io/framework/user/en/portal-pages)
- [Adding Pages](https://docs.frappe.io/framework/user/en/guides/portal-development/adding-pages)
- [Portal Roles](https://docs.frappe.io/framework/user/en/guides/portal-development/portal-roles)
- [Web View Pages](https://docs.frappe.io/framework/user/en/tutorial/portal-pages)
- [Request Lifecycle / Routing and Rendering](https://docs.frappe.io/framework/user/en/python-api/routing-and-rendering)
- [Jinja API](https://docs.frappe.io/framework/user/en/api/jinja)
- [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)

Для поведения v16 дополнительно сверено с исходным кодом ветки `version-16`:

- [`frappe/website/page_renderers/template_page.py`](https://github.com/frappe/frappe/blob/version-16/frappe/website/page_renderers/template_page.py)
- [`frappe/website/website_generator.py`](https://github.com/frappe/frappe/blob/version-16/frappe/website/website_generator.py)
- [`frappe/website/doctype/web_page/web_page.py`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/web_page/web_page.py)
- [`frappe/website/doctype/web_page/web_page.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/web_page/web_page.json)
- [`frappe/website/doctype/website_settings/website_settings.py`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/website_settings/website_settings.py)
- [`frappe/website/doctype/website_settings/website_settings.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/website_settings/website_settings.json)
- [`frappe/website/doctype/portal_settings/portal_settings.py`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/portal_settings/portal_settings.py)
- [`frappe/website/doctype/portal_settings/portal_settings.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/portal_settings/portal_settings.json)
- [`frappe/website/doctype/portal_menu_item/portal_menu_item.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/portal_menu_item/portal_menu_item.json)
- [`frappe/website/doctype/website_sidebar/website_sidebar.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/website_sidebar/website_sidebar.json)
- [`frappe/website/doctype/web_template/web_template.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/web_template/web_template.json)
- [`frappe/website/doctype/website_theme/website_theme.json`](https://github.com/frappe/frappe/blob/version-16/frappe/website/doctype/website_theme/website_theme.json)
- [`frappe/www/me.py`](https://github.com/frappe/frappe/blob/version-16/frappe/www/me.py)

---

Следующая глава: **41. REST API**.
