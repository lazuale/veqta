# Инженерный практикум Frappe Framework 16

Практикум учит собирать реальные Frappe-приложения и понимать, **какой слой Framework
должен владеть конкретной ответственностью**.

Он рассчитан на взрослого новичка. До начала не требуется знать Linux, Git, Python,
JavaScript, SQL, HTTP или внутреннее устройство Frappe. Термины вводятся до первого
применения, а программный слой появляется только после того, как ученик уже умеет
решать задачу metadata и понимает границу штатной конфигурации.

## Главный принцип

```text
задача
→ ответственность
→ минимальная модель
→ штатный primitive Frappe
→ проверка гарантии
→ только затем extension/code, если primitive уже недостаточен
```

`Frappe-native` не означает «без Python». Это означает не забирать у Framework
ответственность, которую он уже умеет выполнять, и писать код только для новой
ответственности приложения.

## Два уровня курса

### Уровень A — Metadata & Configuration

Три независимых продукта собираются без собственной Python/JavaScript business logic:

1. `equipment_register` — модель данных и рабочий реестр;
2. `purchase_requests` — lifecycle, permissions, Workflow и docstatus;
3. `service_intake` — внешний Web Form, trust boundary, внутренний Case и REST.

Ученик трижды проходит полный цикл:

```text
задача
→ модель данных
→ lifecycle
→ permissions
→ рабочий интерфейс
→ collaboration / automation
→ reporting
→ source / site boundary
→ clean install
```

### Уровень B — Frappe Engineering Bridge

После принятого P3 продолжается **тот же `service_intake`**, а не создаётся четвёртый
учебный продукт.

Появляется реальное требование, которое metadata уже не выражает целиком:

```text
Accepted Service Intake
→ одной серверной командой создать Service Case
→ зафиксировать время конвертации
→ не допустить частично выполненную операцию
```

На этом требовании изучаются:

```text
Controller / validate
Document lifecycle
whitelisted Document method
permission-aware Document API
request transaction / rollback
patches + bench migrate
integration tests
Background Jobs / after_commit / Webhook как decision boundary
```

Маршрут: [engineering/LABS.md](engineering/LABS.md).

## Техническая база

| Компонент | Принято |
|---|---|
| Frappe Framework | `v16.32.0` |
| Python | `>=3.14,<3.15` |
| Node.js | `>=24` |
| Bench | один общий bench |
| Business apps | три независимых app |
| ERPNext и другие business apps | не используются |
| Собственная Python/JavaScript logic | отсутствует в P1–P3; минимальный Python появляется в Engineering Bridge |

Frappe app — полноценный пакет приложения. Он может содержать metadata, controllers,
hooks, API, jobs, patches и tests. Поэтому P1–P3 не объявляют код «ненативным»: они
сначала дают ученику нормальную metadata-модель, чтобы программный слой не превратился в
обход непонятных настроек.

## Три проекта

| № | Продукт | Главный инженерный вопрос | App |
|---:|---|---|---|
| 1 | [Реестр оборудования](projects/01-equipment-register/LABS.md) | Как представить предметную область средствами Frappe? | `equipment_register` |
| 2 | [Заявки на закупку](projects/02-purchase-requests/LABS.md) | Как построить управляемый lifecycle документа? | `purchase_requests` |
| 3 | [Внешняя приёмная](projects/03-service-intake/LABS.md) | Как разделить внешний и внутренний trust boundary? | `service_intake` |

Проекты независимы по данным и исходникам. Знания накапливаются, но P2 не зависит от
`equipment_register`, а P3 — от `purchase_requests`.

Engineering Bridge расширяет P3 **после** его clean-site acceptance, потому что именно в
этом продукте появляется естественная программная ответственность.

## Общий стенд

```text
frappe-practicum-bench/
├── apps/
│   ├── frappe/
│   ├── equipment_register/
│   ├── purchase_requests/
│   └── service_intake/
└── sites/
    ├── equipment.localhost/
    ├── purchase.localhost/
    └── intake.localhost/
```

Для приёмки каждого app создаётся отдельный чистый site. Clean site доказывает, что
продукт существует в исходниках и переносимой конфигурации, а не только в базе
разработчика.

Engineering Bridge добавляет вторую проверку поставки:

```text
clean install
≠ upgrade existing site
```

Patch должен корректно обработать старый `intake.localhost`, а новая установка должна
работать и без исторических данных.

## Как устроен проектный шаг

Новый механизм появляется только после требования:

```text
проблема
→ кто должен владеть ответственностью
→ минимальный Frappe mechanism
→ действие
→ положительная проверка
→ отрицательная проверка
→ source/site boundary
```

Примеры:

```text
иерархия мест
→ Tree DocType

строки без самостоятельного lifecycle
→ Child Table

допустимые переходы согласования
→ Workflow

конкретный исполнитель
→ Assign To / ToDo

инвариант между двумя Documents
→ Controller validation

предметное действие поверх одного Document
→ whitelisted Document method
```

Функция Framework не добавляется в продукт только ради процента покрытия.

## Что считается освоением

Для существенного механизма ученик показывает:

| Проверка | Что доказывает |
|---|---|
| рабочий сценарий | задача продукта решена |
| отрицательный сценарий | запрет обеспечивается реальным enforcement layer |
| source check | понятно, что принадлежит app |
| clean-site / upgrade check | результат воспроизводим и обновляем |
| объяснение границы | понятно, чего механизм **не** гарантирует |

Фраза «кнопки нет» не доказывает server-side запрет. Фраза «код работает» не доказывает,
что код находится в правильном архитектурном слое.

## Где начинать

1. [START_HERE.md](START_HERE.md)
2. [SETUP_WSL2.md](SETUP_WSL2.md)
3. [FOUNDATIONS.md](FOUNDATIONS.md)
4. P1 → P2 → P3
5. [Engineering Bridge](engineering/LABS.md)

Справочные документы:

- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура курса и ownership решений;
- [SCOPE.md](SCOPE.md) — границы Core и Engineering Bridge;
- [ROADMAP.md](ROADMAP.md) — последовательность;
- [MATRIX.md](MATRIX.md) — фактическое покрытие;
- [ACCEPTANCE.md](ACCEPTANCE.md) — инженерная приёмка;
- [REFERENCES.md](REFERENCES.md) — official docs и exact `v16.32.0` source;
- [GLOSSARY.md](GLOSSARY.md) — термины;
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — диагностика.

Начало работы: **[START_HERE.md](START_HERE.md)**.
