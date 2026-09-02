# Инженерный мост: когда metadata уже недостаточно

Этот блок начинается только после принятого P3.

P1–P3 показывают, сколько реального продукта можно собрать штатной моделью, permissions,
Workflow, Web Form, reports и другими декларативными механизмами Frappe. Затем появляется
следующая граница:

```text
требование всё ещё принадлежит приложению
но metadata больше не выражает нужную гарантию
→ используем штатную программную точку расширения Frappe
```

Это не переход «от Frappe к программированию вокруг Frappe». Controller, Document
lifecycle, whitelisted methods, transaction boundary, patches, Background Jobs и tests —
часть обычной архитектуры Frappe app.

## Почему продолжаем именно `service_intake`

В конце P3 сотрудник вручную:

1. принимает `Service Intake`;
2. создаёт `Service Case`;
3. переносит проверенные данные;
4. связывает Case с Intake.

Появляется реальное новое требование:

> Case можно создавать только из принятого Intake, операция должна быть одной серверной
> командой, а дата конвертации должна фиксироваться автоматически.

Link, Unique, Set Only Once, permissions и Workflow решают только части задачи. Значит,
у приложения появилась собственная программная ответственность.

## Маршрут E1–E9

| Блок | Что появляется | Зачем |
|---|---|---|
| E1 | Controller `before_insert` | creation invariant между двумя DocType без поломки последующих Agent-save |
| E2 | Standard field `converted_at` | эволюция source-модели app |
| E3 | whitelisted Document method | семантическая команда вместо клона CRUD API |
| E4 | REST API v2 document method | проверить command через реальный permission-aware HTTP path |
| E5 | request transaction / rollback | доказать атомарность операции без manual commit |
| E6 | patch + `bench migrate` | обновить существующие данные после изменения схемы |
| E7 | `IntegrationTestCase` на отдельном test site | защитить собственные invariants/commands и permission boundary |
| E8 | Background Jobs / `after_commit` / Webhook | выбрать async/integration owner без искусственной job |
| E9 | upgrade + test + clean-install acceptance | проверить три разные эксплуатационные ситуации |

Пошаговая работа: [LABS.md](LABS.md).

## Почему `before_insert`, а не общий `validate`

Правило E1 звучит так:

```text
Case можно СОЗДАТЬ только из Accepted Intake
```

После создания Agent работает с Case, но по модели P3 не читает исходный Intake с
контактными данными.

Если проверять Intake на каждом `validate()`, Agent-save начнёт требовать лишний Read на
Intake. Значит, lifecycle выбран неверно.

```text
creation invariant
→ before_insert

invariant каждого save
→ validate / другой подходящий lifecycle event
```

Курс должен учить выбирать не просто Controller, а правильную фазу Document lifecycle.

## Что принципиально не создаём

Не вводятся:

- `Repository` вокруг `frappe.get_doc`;
- `Service` только ради вызова `doc.save()`;
- собственный transaction manager;
- собственная queue/daemon;
- отдельный CRUD endpoint поверх Document REST;
- Client Script как единственная server guarantee;
- `frappe.db.commit()` внутри обычной request-команды;
- `ignore_permissions=True` в public business command.

Отдельный service/module становится нормальным решением, если позже появится настоящая
cross-document orchestration, reusable algorithm или внешний protocol. В текущей задаче
команда относится к одному `Service Intake`, поэтому естественный владелец — его
controller.

## Что дополнительно доказывает E7

Automated tests запускаются не на рабочем `intake.localhost`, а на отдельном
`intake-test.localhost`.

Причина практическая: test runner подготавливает test dependencies и не должен загрязнять
рабочий учебный site.

Отдельный regression-test проверяет:

```text
Agent
→ не имеет Read на Service Intake
→ имеет Write на существующий Service Case
→ save Case проходит
```

Так тест защищает не только результат, но и правильный lifecycle ownership E1.

## Async и Webhook

Current product не имеет тяжёлой работы, поэтому custom Background Job не добавляется.

При этом ученик должен знать:

```text
heavy internal work after commit
→ Background Job + enqueue_after_commit

simple configurable outbound DocType event
→ штатный Webhook
```

В exact v16.32 обычный Webhook сам накапливается до commit и после успешного commit
ставится Framework в background queue. Второй custom job вокруг него только ради
«асинхронности» не нужен.

## Результат

После инженерного моста ученик должен различать:

```text
metadata invariant
creation invariant
save-time invariant
Workflow transition
permission check
semantic command
request transaction
post-commit side effect
patch/data migration
automated test
```

И уметь объяснить, почему код появился именно в этой точке и именно в этой фазе Frappe
lifecycle.
