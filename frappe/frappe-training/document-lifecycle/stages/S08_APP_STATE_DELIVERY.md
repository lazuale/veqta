# S08. Поставить lifecycle-конфигурацию вместе с App

К S08 процесс уже работает на dev Site. Но пока часть конфигурации была создана через Desk.

Новое требование:

> Новый Site после установки App должен получить обязательный lifecycle без повторного ручного создания Workflow.

Здесь нужно не экспортировать всё подряд, а определить владельца каждого элемента.

Связанный архитектурный раздел: [`../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md`](../../../frappe-architecture-standard/11_DEPLOYMENT_TESTING.md).

## 1. Составить карту владения

Финальный lifecycle состоит из разных типов состояния.

| Элемент | Основной источник | Поставка |
|---|---|---|
| `Purchase Request` schema | Standard DocType JSON | sync при install/migrate |
| default DocPerm | Standard DocType JSON | sync при install/migrate |
| `PLT Requester` | имя Role в Standard DocPerm | Frappe создаёт missing Role при sync |
| `PLT Approver` | имя Role в Standard DocPerm | Frappe создаёт missing Role при sync |
| `PLT Senior Approver` | имя Role в Standard DocPerm | Frappe создаёт missing Role при sync |
| `PLT Submit for Review` | App-owned setup record | filtered fixture |
| `PLT Cancel Request` | App-owned setup record | filtered fixture |
| `PLT ...` Workflow States | App-owned setup records | filtered fixture |
| `PLT Purchase Request Approval` | App-owned setup record | filtered fixture |
| runtime Workflow Actions | данные Site | не fixture |
| Users / passwords | данные Site | не fixture |
| Purchase Request records | данные Site | не fixture |

Главный принцип:

```text
обязательная конфигурация App
→ должна воспроизводиться из App

операционные данные конкретного Site
→ не становятся fixtures
```

## 2. Почему Role fixture не нужен

Имена трёх ролей уже находятся в permission rows Standard `Purchase Request`.

При sync Standard DocType Frappe вызывает `make_module_and_roles()` и создаёт отсутствующие Role, используемые в permissions.

Источник:

- [`frappe/core/doctype/doctype/doctype.py` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/core/doctype/doctype/doctype.py).

Поэтому схема:

```text
Standard DocPerm
+
Role fixture с тем же именем
```

дублировала бы один и тот же delivery responsibility.

Отдельный Role fixture понадобился бы только при отдельном App-owned состоянии Role, которое не выражается Standard DocPerm.

## 3. Настроить fixtures в hooks.py

Откройте:

```text
apps/purchase_lifecycle_training/purchase_lifecycle_training/hooks.py
```

Добавьте:

```python
fixture_auto_order = True

fixtures = [
    {
        "dt": "Workflow Action Master",
        "filters": [
            [
                "workflow_action_name",
                "in",
                ["PLT Submit for Review", "PLT Cancel Request"],
            ]
        ],
    },
    {
        "dt": "Workflow State",
        "filters": [
            [
                "workflow_state_name",
                "in",
                [
                    "PLT Draft",
                    "PLT Pending Approval",
                    "PLT Rejected",
                    "PLT Pending Senior",
                    "PLT Approved",
                    "PLT Cancelled",
                ],
            ]
        ],
    },
    {
        "dt": "Workflow",
        "filters": [["workflow_name", "=", "PLT Purchase Request Approval"]],
    },
]
```

Порядок выбран по зависимостям:

```text
Workflow Action Master
→ Workflow State
→ Workflow
```

`Workflow` ссылается на Action Masters и Workflow States через свои child rows, поэтому базовые records должны импортироваться раньше самого Workflow.

В v16.33.0 `fixture_auto_order` добавляет числовые префиксы к export-файлам, а import читает fixture files в отсортированном порядке.

Источник: [`frappe/utils/fixtures.py`](https://github.com/frappe/frappe/blob/v16.33.0/frappe/utils/fixtures.py).

## 4. Экспортировать fixtures

Из Bench:

```bash
cd ~/frappe/rental-training-bench

bench --site purchase-lifecycle.localhost export-fixtures --app purchase_lifecycle_training
```

Проверьте каталог:

```bash
find apps/purchase_lifecycle_training/purchase_lifecycle_training/fixtures \
  -maxdepth 1 -type f -printf '%f\n' | sort
```

Ожидаемый смысл порядка:

```text
1_workflow_action_master.json
2_workflow_state.json
3_workflow.json
```

Точное количество цифр префикса зависит от количества fixtures; при трёх элементах это одна цифра.

## 5. Проверить, что экспорт не захватил лишнее

В fixtures должны быть только:

```text
2 собственных Workflow Action Master
6 собственных Workflow State
1 собственный Workflow
```

Не должно быть:

```text
Role
User
Workflow Action runtime rows
Purchase Request business records
Framework-owned Approve / Reject / Review Action Masters
```

Проверьте Git:

```bash
git -C apps/purchase_lifecycle_training status --short
```

Затем повторите export:

```bash
bench --site purchase-lifecycle.localhost export-fixtures --app purchase_lifecycle_training
```

Повторный export при неизменной конфигурации должен давать объяснимый стабильный diff, а не случайно захватывать новые записи Site.

## 6. Проверить source manifest

К этому моменту App должен содержать по смыслу:

```text
purchase_lifecycle_training/
├── hooks.py
├── modules.txt
├── fixtures/
│   ├── 1_workflow_action_master.json
│   ├── 2_workflow_state.json
│   └── 3_workflow.json
└── purchase_lifecycle_training/
    └── doctype/
        └── purchase_request/
            ├── purchase_request.json
            ├── purchase_request.py
            └── test_purchase_request.py
```

`purchase_request.py` может оставаться без собственной бизнес-логики. В текущем практикуме процесс уже выражается штатными `Workflow`, `docstatus` и permissions, поэтому Python не нужно добавлять просто ради наличия Controller.

## Результат

После S08:

```text
Standard metadata владеет Purchase Request и default DocPerm
Role fixture отсутствует
App-owned Action Masters / States / Workflow экспортированы filtered fixtures
runtime данные Site не попали в Git
порядок fixture import выражает реальные зависимости
```

Следующий этап: [`S09_AUTOMATED_TESTS.md`](S09_AUTOMATED_TESTS.md).
