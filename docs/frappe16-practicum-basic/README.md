# Frappe Framework 16 — базовый практикум

Этот практикум рассчитан на человека, который раньше не работал с Frappe и не является программистом.

Цель простая: пройти путь от чистого стенда до рабочего приложения и своими руками увидеть, что Frappe умеет штатно.

Мы не будем изучать Frappe как справочник функций. На протяжении всего курса будем развивать одно приложение для управления работой. Каждая новая возможность появится тогда, когда она действительно понадобится проекту.

## Как будем работать

Сначала всегда используем готовый механизм Frappe. Если задачу можно решить настройкой DocType, правами, Workflow, Notification, Assignment Rule, Report Builder или другим штатным инструментом, так и делаем.

Встроенные скрипты тоже входят в практикум, но только как следующий шаг. Client Script, Server Script, простые условия, Query Report, Jinja и Webhook нужны, чтобы увидеть реальный потолок платформы, а не чтобы превратить курс в обучение программированию.

Мы не пишем собственную бизнес-логику в Python-файлах приложения, не меняем core Frappe и не строим свой frontend.

## Что будем строить

В начале создадим обычное приложение Frappe:

```text
Bench
  ↓
Site
  ↓
bench new-app
  ↓
frappe_practicum
  ↓
Module: Practicum
```

После этого внутри него постепенно появятся:

```text
Project
Work Item
Category
Work Item Step
Practicum Settings
Work Approval
```

Основной документ курса — `Work Item`. На нём будем изучать формы, связи, представления, пользователей, права, назначения, Workflow, уведомления, отчёты, Web Form и API.

Для Submit / Cancel / Amend будет отдельный `Work Approval`. Обычную рабочую задачу не будем искусственно делать подтверждаемым документом только ради демонстрации функции.

## Что входит в практикум

Мы пройдём:

- установку Frappe 16 и базовую работу с Bench и Site;
- `bench new-app`, установку App на Site и Git;
- Developer Mode и создание объектов, которые должны попасть в исходники App;
- DocType, поля, naming, связи, Child Table, Single и Tree DocType;
- файлы, Geolocation, Connections и Actions;
- Submit, Cancel, Amend, Version, Timeline и Audit Trail;
- List, Kanban, Calendar, Gantt, Tree и Map View там, где они штатно доступны;
- Workspace и навигацию Frappe 16;
- Users, Roles, Role Profile и всю базовую систему permissions;
- Assign, ToDo, Comments, Mentions, Tags, Following и Share;
- Assignment Rule, Workflow, Notification и Auto Repeat;
- Customize Form, Custom Field, Property Setter, Custom DocPerm, DocType Layout;
- Client Script и Server Script как встроенные инструменты Frappe;
- Scheduler Event и Permission Query;
- Data Import / Export;
- Report Builder, Query Report и Custom Script Report;
- Number Card, Dashboard Chart и Dashboard;
- Standard Print, Print Format Builder и Jinja Print Format;
- Email Account, Communication, Email Queue и Email Notification;
- Website Settings, Web Page и Web Form;
- штатный REST API, Server Script API и Webhook;
- Workflow Transition Tasks v16;
- Package как отдельную штатную возможность Frappe;
- перенос App на второй Site через Git и Bench;
- backup и restore.

## Что не входит

На этом уровне мы не пишем полноценное приложение вручную.

Не входят:

- собственные Python controllers в DocType;
- бизнес-логика в Python-модулях App;
- hooks как способ расширять поведение Framework;
- override и extend стандартных классов;
- собственные файловые API methods;
- собственные background jobs и scheduler handlers в Python;
- файловые Form/List/Page JavaScript-скрипты;
- Vue, TypeScript, asset bundling и собственный frontend;
- patches и собственные data migrations;
- Standard Script Report с отдельными `.py` / `.js` файлами;
- Virtual DocType, если для него нужен controller;
- полноценные automated tests собственного кода;
- production hardening и отдельный DevOps-контур.

При этом `hooks.py` не является полностью запретной темой: если Frappe штатно использует его как конфигурацию приложения, например для fixtures, мы можем показать такую запись. Но писать туда собственную бизнес-логику на базовом уровне не будем.

## Важная часть курса: что хранится в App, а что только в Site

Frappe позволяет многое настроить через Desk, но не каждая такая настройка автоматически оказывается в Git.

Поэтому по ходу практикума мы отдельно разберём:

- какие DocType и другие стандартные объекты записываются в App при включённом Developer Mode;
- что остаётся только в базе Site;
- как работает Export Customizations;
- зачем нужны fixtures;
- почему второй Site не должен зависеть от ручного повторения настроек.

К финалу приложение должно устанавливаться на чистый второй Site штатным способом и воспроизводить всю конфигурацию, которую мы считаем частью продукта.

## Как выглядит путь курса

```text
ставим Frappe
    ↓
создаём App и включаем Developer Mode
    ↓
строим модель данных
    ↓
настраиваем формы и представления
    ↓
добавляем пользователей и права
    ↓
организуем рабочий процесс
    ↓
пробуем встроенные скрипты
    ↓
учимся переносить настройки в App
    ↓
работаем с импортом, отчётами и Dashboard
    ↓
настраиваем печать и почту
    ↓
выходим в Website / Web Form
    ↓
пробуем API и Webhook
    ↓
ставим App на второй Site
    ↓
делаем backup / restore
    ↓
проходим весь сценарий заново
```

## Что ученик должен уметь после курса

После практикума человек должен без посторонней разработки суметь:

1. развернуть учебный Frappe 16;
2. создать и установить собственный App;
3. включить Developer Mode и понимать, зачем он нужен;
4. собрать связанную модель DocTypes;
5. настроить формы, представления и Workspace;
6. создать пользователей и правильно разграничить доступ;
7. организовать назначения, Workflow и уведомления;
8. использовать Client Script и Server Script только там, где штатной настройки уже недостаточно;
9. импортировать данные и строить отчёты разной сложности;
10. собрать Dashboard;
11. подготовить печатный документ и отправить его по Email;
12. сделать внешнюю страницу и Web Form;
13. работать с документами через REST API и Webhook;
14. понимать, какие настройки живут только в Site и как включить нужные в App;
15. установить тот же App на второй Site из Git;
16. сделать backup и восстановить Site;
17. понять, где заканчиваются штатные возможности Frappe и действительно начинается разработка.

## Файлы практикума

- [`MATRIX.md`](MATRIX.md) — список практических работ и результат каждой из них;
- [`ROADMAP.md`](ROADMAP.md) — общий маршрут курса;
- [`labs/`](labs/) — сами пошаговые работы.

Все команды и особенности интерфейса должны проверяться именно на Frappe Framework 16. Основные источники — официальная документация Frappe, ветка `version-16` репозитория `frappe/frappe` и официальные заметки по версии 16.