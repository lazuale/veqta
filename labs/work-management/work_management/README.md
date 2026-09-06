# Work Management Lab App

Минимальный Frappe App, реализующий только универсальный Core Work Management:

- `Work Unit`
- `Work Type`
- `Work Item`
- `Work Dependency`
- `Work Source`
- `Work Reference`

Схема и семантика определены в соседнем документе [`../data-model-v1.md`](../data-model-v1.md).
Правила допустимой настройки Site — в [`../compatibility.md`](../compatibility.md).

App не содержит дополнительные first-party capabilities. Intake, membership, documentary records,
tracked assets, projects, shift operations, time tracking и другие модели могут появляться отдельно
только после подтверждения самостоятельной ответственности и проверки, что её не закрывают Core,
штатная настройка Frappe или совместимый App.

## Требования

Текущая реализация ориентирована на Frappe Framework v16 и Python 3.14.

`Work User` и `Work Manager` доставляются как fixtures. `System Manager` получает явные setup-права
на Core DocType через их DocPerm; приложение не полагается на несуществующий автоматический bypass этой роли.

## Проверка на Bench

После подключения этого каталога к Bench как приложения `work_management`:

```bash
bench --site <site> install-app work_management
bench --site <site> run-tests --app work_management
```

Репозиторий VEQTA сам по себе не является Bench, поэтому наличие тестов в этом каталоге не означает,
что они были выполнены без отдельного Frappe Site.
