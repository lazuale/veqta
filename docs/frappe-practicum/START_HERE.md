# Начало практикума

Это основной маршрут ученика. Остальные документы не нужно читать подряд до начала
работы.

## Для кого курс

Курс рассчитан на человека, который уверенно пользуется Windows и браузером, но может
не знать Linux, Git, Python, JavaScript, SQL, HTTP и устройство Frappe.

P1–P3 не требуют писать собственную Python/JavaScript business logic. Небольшие правки
`hooks.py` там относятся к поставке metadata/fixtures.

После принятого P3 начинается [Engineering Bridge](engineering/LABS.md). В нём впервые
пишется небольшой Python-код, но только после того, как ученик уже понимает DocType,
Document, permissions, Workflow, Web Form и source/site boundary. Знать Python заранее
не требуется: используются только конструкции, необходимые конкретной задаче Frappe.

## Что понадобится

- Windows 11 с WSL2;
- не менее 8 GB RAM на компьютере;
- интернет во время установки;
- обычный редактор текста, например Visual Studio Code;
- отдельный учебный стенд, не рабочий сервер.

Все команды выполняются в Debian внутри WSL2, если рядом не написано `PowerShell`.

## Порядок прохождения

| Шаг | Материал | Результат |
|---:|---|---|
| 1 | [SETUP_WSL2.md](SETUP_WSL2.md) | Frappe-only Bench и работающий Desk |
| 2 | [FOUNDATIONS.md](FOUNDATIONS.md) | понятны Bench, site, app, Module, DocType и Document |
| 3 | [P1](projects/01-equipment-register/LABS.md) | самостоятельный реестр оборудования |
| 4 | [ACCEPTANCE.md](ACCEPTANCE.md), P1 | P1 принят на чистом site |
| 5 | [P2](projects/02-purchase-requests/LABS.md) | приложение согласования заявок |
| 6 | [ACCEPTANCE.md](ACCEPTANCE.md), P2 | P2 принят на чистом site |
| 7 | [P3](projects/03-service-intake/LABS.md) | внешний intake и внутренняя очередь |
| 8 | [ACCEPTANCE.md](ACCEPTANCE.md), P3 | P3 принят на чистом site |
| 9 | [Engineering Bridge](engineering/LABS.md) | Controller, semantic command, transactions, patch, tests |
| 10 | [ACCEPTANCE.md](ACCEPTANCE.md), Engineering | проверены upgrade и clean install программного слоя |
| 11 | [ROADMAP.md](ROADMAP.md), финальный аудит | ученик объясняет архитектурные решения без подсказки |

После шага 8 закрыт **базовый metadata/configuration уровень**. После шага 10 закрыт
полный инженерный маршрут этого практикума.

[ARCHITECTURE.md](ARCHITECTURE.md), [SCOPE.md](SCOPE.md) и [MATRIX.md](MATRIX.md) —
справочные документы. Их не нужно заучивать перед P1.

## Как выполняется лабораторная

Каждая лабораторная должна закрывать пять видов работы:

1. **Исходное состояние** — понятно, что уже существует.
2. **Действие** — меняется продукт или site.
3. **Проверка** — виден положительный результат и, где нужна гарантия, отрицательный сценарий.
4. **Source check** — понятно, что попало в app, а что осталось в базе site.
5. **Состояние после** — можно однозначно перейти дальше.

В Engineering Bridge добавляется шестой вопрос:

> Почему эта ответственность не могла остаться в уже изученном metadata-механизме?

Если ответа нет, код добавлять нельзя.

Не переходить дальше, если итоговое состояние не совпало. Сначала открыть
[TROUBLESHOOTING.md](TROUBLESHOOTING.md), затем посмотреть последнее изменение через
`git diff`.

## Как читать команды

Знак приглашения терминала не копируется. В записи:

```text
dev@first:~/frappe/frappe-practicum-bench$
```

команда начинается после `$`.

Перед командой с `cd` проверить текущий каталог:

```bash
pwd
```

Из Bench ожидается:

```text
~/frappe/frappe-practicum-bench
```

Из репозитория app:

```text
~/frappe/frappe-practicum-bench/apps/equipment_register
~/frappe/frappe-practicum-bench/apps/purchase_requests
~/frappe/frappe-practicum-bench/apps/service_intake
```

## Что записывать

Для каждой лабораторной достаточно короткого протокола:

```text
Лабораторная:
Дата:
Рабочий site:
Проверка прошла:
Отрицательная проверка прошла:
Enforcement layer:
Commit:
Замечания:
```

Для Engineering Bridge дополнительно записать:

```text
Почему metadata недостаточно:
Почему выбран именно этот extension point:
```

Пароли, API keys, API secrets и SMTP credentials в протокол не записываются.

## Что можно исправлять

Можно:

- повторить последнюю настройку;
- удалить собственный тестовый Document;
- исправить поле до следующей лабораторной;
- пересоздать чистый acceptance site;
- откатить учебный Share/User Permission experiment;
- удалить временный transaction probe сразу после проверки.

Нельзя молча:

- переустанавливать рабочий app;
- копировать базу рабочего site на чистый site;
- создавать недостающий Workflow вручную после `install-app`;
- выполнять permission acceptance только Administrator;
- добавлять Python/JavaScript, чтобы обойти непонятную настройку;
- использовать `ignore_permissions=True` в business command ради удобства;
- добавлять `frappe.db.commit()` внутрь обычного request action без отдельной причины;
- создавать service/repository/queue только потому, что такой pattern знаком из другого стека.

## Критерий окончания

Базовый уровень закончен, когда три app устанавливаются на новые site, working data не
попадает в исходники, permissions проверены отдельными Users, а ученик объясняет выбор
каждого metadata-механизма.

Полный маршрут закончен, когда `service_intake` дополнительно:

- содержит минимальную server business logic в controller;
- предоставляет semantic command вместо дублирующего CRUD endpoint;
- использует штатную request transaction без manual commit;
- обновляет старые данные через patch;
- проходит integration tests;
- работает и как clean install, и как upgrade существующего site;
- не содержит искусственного Background Job только ради coverage.

Следующий шаг: **[SETUP_WSL2.md](SETUP_WSL2.md)**.
