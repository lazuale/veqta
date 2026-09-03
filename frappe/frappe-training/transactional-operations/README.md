# Транзакционная операция на Frappe

Практикум продолжает учебное приложение `rental_training` и разбирает одну новую ответственность: как выполнить бизнес-операцию, которая должна согласованно изменить несколько `Document`.

Здесь не создаётся отдельный App и не добавляются background jobs «для полноты». Задача остаётся синхронной и короткой: при выдаче Rental нужно изменить его состояние и создать журнал движения по каждому Equipment так, чтобы либо сохранилось всё, либо не сохранилось ничего.

## Что будет построено

К существующей модели добавляется один самостоятельный DocType:

```text
Equipment Movement
├── equipment
├── rental
├── movement_type
└── movement_at
```

`Equipment Movement` — журнал фактических операций `Issue` и `Return` по конкретному Equipment.

На `Rental` появляются две явные серверные команды:

```text
issue()
return_equipment()
```

Их вызывают тонкие кнопки стандартной Form. Сервер остаётся владельцем бизнес-правила и проверки permissions.

Основная цепочка практикума:

```text
готовый rental_training
        ↓
Equipment Movement
        ↓
явная команда выдачи
        ↓
Rental + несколько Movement в одной транзакции
        ↓
ошибка внутри операции
        ↓
автоматический rollback
        ↓
эксперимент с ручным commit
        ↓
частично сохранённое состояние
        ↓
эксперимент с пойманным исключением
        ↓
явная команда возврата
        ↓
Document API vs прямое изменение БД
        ↓
автоматические проверки
        ↓
поставка состояния App
        ↓
чистая установка
```

## Главная идея

В обычном записывающем web-request Frappe сам управляет транзакцией: успешный `POST`/`PUT` фиксирует изменения в конце запроса, а необработанное исключение приводит к rollback.

Поэтому корректная бизнес-операция не должна делать `frappe.db.commit()` после каждого промежуточного шага.

В практикуме это проверяется не на абстрактных примерах, а на реальном состоянии приложения:

```text
Rental = Active
и
Issue Movement создан для каждого Equipment
```

либо:

```text
Rental остаётся Planned
и
не остаётся ни одного частичного Issue Movement
```

Первичные источники:

- https://docs.frappe.io/framework/user/en/api/database
- https://docs.frappe.io/framework/user/en/api/document
- https://docs.frappe.io/framework/user/en/api/form
- https://github.com/frappe/frappe/blob/v16.33.0/frappe/app.py

## Что не входит

В маршрут не входят без отдельной задачи:

- `frappe.enqueue`;
- `enqueue_after_commit`;
- worker queues;
- scheduler;
- Webhook;
- внешнее API;
- retries и idempotency внешних эффектов;
- собственный frontend;
- ручные savepoint как основной путь бизнес-операции.

Эти механизмы относятся к другим ответственностям. В частности, background job понадобится тогда, когда после успешного commit появится реально долгая или независимая работа.

## Что нужно знать до начала

Нужно пройти предыдущие практикумы VEQTA Learn или иметь эквивалентное понимание:

- Bench / App / Site;
- Standard DocType и Child DocType;
- `Document Controller`;
- Role и DocType Permissions;
- серверные validations;
- `get_list` / `get_all` и permission boundary;
- автоматические тесты;
- установка App на чистый Site.

Практикум использует уже существующие `Equipment`, `Customer`, `Rental` и `Rental Item`.

## Версия

Маршрут проверяется на **Frappe Framework v16.33.0** — той же контрольной версии, на которой собран `rental_training` в предыдущих практикумах.

## Материалы

- [модель и учебный сценарий](APPLICATION_MODEL.md);
- [требования практикума](REQUIREMENTS.md);
- [маршрут практикума](ROADMAP.md).

Практические этапы будут находиться в [`stages/`](stages/README.md).

Архитектурный контекст: [Transactions & Async](../../frappe-architecture-standard/06_TRANSACTIONS_ASYNC.md).