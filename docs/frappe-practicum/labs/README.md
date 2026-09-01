# Лаборатории практикума

Лаборатории изучают штатные механизмы Frappe, которым не нужно постоянное место в основной модели `facility_ops`.

- [Lab A — Child Table](a-child-table/README.md)
- [Lab B — Draft / Submit / Cancel / Amend / DocStatus](b-docstatus/README.md)
- [Lab C — Auto Repeat](c-auto-repeat/README.md)
- [Lab D — Customize Form / Custom Field / Property Setter / Export Customizations](d-customize-form/README.md)
- [Lab E — Print / Print Format / Letter Head / PDF](e-print-pdf/README.md)
- [Lab F — специальные Field Types и представления](f-special-features/README.md)

Лаборатория может временно менять metadata/configuration, но после cleanup постоянное ядро остаётся:

```text
Facility Location
Equipment
Service Request
```

## Обязательный security baseline после L11

Лаборатории не имеют права незаметно ослаблять финальную модель `Service Request`.

После любой Lab, затрагивающей `Service Request`, должны сохраниться:

```text
Level 0
Requester   → Create + Read own; Write/Delete No
Technician  → Read/Write; Create/Delete No
Supervisor  → Read/Write/Create; Delete No

Level 1 content
Requester   → Read/Write
Technician  → Read only
Supervisor  → Read/Write

status      → Level 0
```

На Level 1 остаются core content fields:

```text
subject
location
equipment
description
priority
target_date
attachment
```

Если лаборатория временно добавляет новый business-content field/table в `Service Request`, она должна:

```text
1. явно выбрать подходящий Permission Level;
2. проверить реального пользователя;
3. описать Temporary Mutation;
4. выполнить Rollback;
5. вернуть исходную Level 0/1 model.
```

`Administrator` можно использовать для изменения metadata, но нельзя использовать как доказательство пользовательской permission model.

## State contract каждой Lab

```text
PRECONDITIONS
→ какой baseline обязателен

TEMPORARY MUTATION
→ что лаборатория временно добавляет/меняет

ROLLBACK
→ что обязано быть удалено/возвращено

FINAL STATE
→ core domain + permissions после лаборатории

GIT STATE
→ ожидаемый source после cleanup
```

Лаборатория считается незавершённой, если механизм изучен, но hardened baseline не восстановлен.
