# Коррекция принятого CORE: provisioning ролей

Статус: **обязательная коррекция baseline CORE**.

Этот документ не меняет permission matrix первого практикума. Он исправляет только один ранее принятый delivery-contract: способ воспроизведения `Rental Operator` и `Rental Manager` на новом Site.

Нормативное основание:

- [`../frappe-architecture-standard/13_ROLE_PROVISIONING.md`](../frappe-architecture-standard/13_ROLE_PROVISIONING.md);
- Frappe v16.33.0 `frappe/core/doctype/doctype/doctype.py::make_module_and_roles()`;
- Frappe v16.33.0 `frappe/installer.py::install_app()`.

## Что было принято раньше

В ряде документов CORE было записано:

```text
Rental Operator / Rental Manager
→ Role fixtures
→ hooks.py + fixtures/role.json
→ export-fixtures
```

Для текущего собственного Standard DocType это оказалось избыточно.

## Исправленный contract

Роли используются в default `DocPerm` Standard DocTypes нашего App.

Frappe при sync Standard DocType создаёт отсутствующие `Role` из `permissions` metadata.

Поэтому для первого CORE source of truth:

```text
Equipment / Customer / Rental JSON
└── permissions[]
    ├── Rental Operator
    └── Rental Manager

↓ Standard DocType sync

missing Role records создаются Framework
```

Отдельные:

```text
hooks.py fixture Role
fixtures/role.json
export-fixtures Role
```

для этих двух ролей **не требуются**.

## Что именно считается отменённым

Если в принятых документах встречаются формулировки:

```text
Role → filtered fixture
Role → hooks.py + fixtures/role.json
Role records → fixtures
Role fixtures обязательны для clean install
повторный export-fixtures Role является acceptance-проверкой
```

они считаются заменёнными этим contract:

```text
role names
→ Standard DocPerm metadata
→ make_module_and_roles() при sync
```

Все остальные части принятого CORE сохраняются.

## Что остаётся App-owned

```text
permission matrix
→ Standard DocType JSON

role names, необходимые этой permission matrix
→ те же DocPerm rows

Controller
→ Python source

tests
→ App source
```

## Что остаётся Site-owned

```text
operator@example.test
manager@example.test
пароли
назначение ролей конкретным Users
runtime Equipment / Customer / Rental
local config
```

## Clean-install acceptance

Новый Site должен доказать:

```text
до install-app
Rental Operator / Rental Manager отсутствуют

install-app rental_training
→ Standard DocType sync
→ Role records появляются
→ default DocPerm присутствуют
```

Без ручного Role creation и без Role fixtures.

## Когда Role fixture снова станет допустим

Только если появится отдельное требование к самой записи Role, которое не выражается Standard DocPerm и не воспроизводится штатным baseline `make_module_and_roles()`.

До такого требования fixture не возвращается.
