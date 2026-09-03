# 13. Provisioning ролей Standard DocType

Статус: **нормативное уточнение для Frappe v16.33.0**.

Этот документ уточняет delivery-модель базовых `Role + DocType Permissions` и дополняет [`04_SECURITY.md`](04_SECURITY.md) и [`09_DEPLOYMENT_TESTING.md`](09_DEPLOYMENT_TESTING.md).

## 1. Что является source of truth

Для собственного **Standard DocType** базовые права приложения находятся в его metadata:

```text
Standard DocType JSON
└── permissions[]
    ├── role
    ├── read
    ├── create
    ├── write
    ├── delete
    ├── submit
    ├── cancel
    └── amend
```

Если App требует роль только потому, что она используется в этих `DocPerm`, отдельный `Role` fixture не нужен.

## 2. Почему Role fixture не нужен в базовом случае

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** `DocType.validate()` вызывает `make_amendable()` и другие проверки, а при install/sync Standard DocType Frappe вызывает `make_module_and_roles()`.

`make_module_and_roles()`:

1. собирает имена ролей из `doc.permissions`;
2. проверяет существование `Role`;
3. создаёт отсутствующую `Role`;
4. задаёт `role_name`;
5. задаёт `desk_access = 1`.

Источник:

- `frappe/core/doctype/doctype/doctype.py`, функция `make_module_and_roles()`.

**[ИСХОДНЫЙ КОД FRAPPE v16.33.0]** установка App выполняет:

```text
sync_for(app)
→ Standard DocTypes и их permissions
→ make_module_and_roles()

затем

sync_fixtures(app)
```

Источник:

- `frappe/installer.py`, функция `install_app()`.

Следовательно, для роли, которая не несёт собственной дополнительной конфигурации:

```text
Standard DocPerm
→ source of truth role name
→ Framework создаёт missing Role при sync
```

а схема:

```text
Standard DocPerm
+
Role fixture с тем же role_name
```

создаёт два механизма доставки одной ответственности.

## 3. Когда Role fixture всё-таки оправдан

Fixture нужен не из-за самого факта существования имени роли, а когда App обязан поставлять **самостоятельное состояние Role**, которое не выражается Standard DocPerm.

Примеры:

```text
роль вообще не фигурирует ни в одном Standard DocPerm;
роль должна поставляться до/вне sync собственного Standard DocType;
App требует дополнительные свойства Role, отличающиеся от штатно создаваемого baseline;
роль является отдельной конфигурационной записью продукта по собственной семантике.
```

Тогда сначала формулируется дополнительная ответственность, и только после этого выбирается filtered fixture.

## 4. Практическое правило

Перед добавлением `Role` в `fixtures` ответить:

```text
1. Есть ли эта роль в permissions нашего Standard DocType?
2. Достаточно ли обычного Role, которое Frappe создаст из DocPerm?
3. Есть ли у Role дополнительное App-owned состояние?
```

Если ответы:

```text
да
да
нет
```

то baseline:

```text
Role fixture НЕ нужен.
```

## 5. Clean-install проверка

Для собственного Standard DocType с ролями в metadata новый Site должен доказать:

```text
до install-app
→ Role отсутствует

install-app
→ sync Standard DocType
→ Role появляется
→ default DocPerm присутствуют
```

Без:

```text
ручного создания Role
export-fixtures Role
fixtures/role.json
Role Permission Manager как обязательного шага
```

## 6. Что остаётся Site-owned

Конкретные Users и их пароли остаются данными Site:

```text
User
→ Site

Role name / базовый DocPerm собственного Standard DocType
→ App metadata + штатный sync Frappe
```

## 7. Архитектурный вывод

Правило архитектурного стандарта:

> Не экспортировать `Role` fixture только для того, чтобы воспроизвести имя роли, которое уже является частью Standard DocPerm собственного App и штатно создаётся Frappe при sync.

Это частный случай общего принципа:

> Не вводить второй механизм доставки, если штатный механизм Frappe уже полностью владеет этой ответственностью.
