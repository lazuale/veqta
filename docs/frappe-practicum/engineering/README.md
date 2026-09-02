# Инженерный мост: когда metadata уже недостаточно

Этот блок начинается **только после принятого P3**.

P1–P3 сознательно показывают, сколько реального продукта можно собрать штатной моделью,
permissions, Workflow, Web Form, reports и другими декларативными механизмами Frappe.
Здесь появляется следующая граница:

```text
требование всё ещё принадлежит приложению
но metadata больше не выражает нужную гарантию
→ используем штатную программную точку расширения Frappe
```

Это не «переход от Frappe к программированию вокруг Frappe». Controller, Document
lifecycle, whitelisted methods, transaction handling, patches и tests — часть обычной
архитектуры Frappe app.

## Почему продолжаем именно `service_intake`

В конце P3 сотрудник вручную:

1. принимает `Service Intake`;
2. создаёт `Service Case`;
3. переносит проверенные данные;
4. связывает Case с Intake.

Такой процесс правильный для no-code уровня, но появляется реальное новое требование:

> Case можно создавать только из принятого Intake, операция должна быть одной
> серверной командой, а дата конвертации должна фиксироваться автоматически.

Обычные Link, Unique, Read Only и Workflow решают только части задачи. Значит, у
приложения появилась собственная программная ответственность.

## Что изучается

| Блок | Что появляется | Зачем |
|---|---|---|
| E1 | Controller и `validate` | серверный инвариант между двумя DocType |
| E2 | whitelisted Document method | семантическая команда вместо клона CRUD API |
| E3 | transaction boundary | одна операция либо завершается целиком, либо откатывается |
| E4 | patch + `bench migrate` | эволюция уже установленного app и существующих данных |
| E5 | integration tests | проверка собственного поведения, а не Framework вообще |
| E6 | async/integration decision lab | понять `enqueue_after_commit`, Background Jobs и Webhook без искусственного внедрения в продукт |
| E7 | clean install + upgrade acceptance | проверить и новую установку, и обновление существующего site |

Пошаговая работа: [LABS.md](LABS.md).

## Что здесь принципиально не делаем

Не создаём:

- `Repository` вокруг `frappe.get_doc`;
- `Service` только ради вызова `doc.save()`;
- собственный transaction manager;
- собственную очередь;
- отдельный CRUD endpoint для того, что уже даёт Document REST API;
- Client Script как единственную защиту бизнес-правила;
- `frappe.db.commit()` внутри обычной команды;
- `ignore_permissions=True` ради удобства.

Если позже появится настоящая cross-document orchestration или внешняя интеграция,
отдельный service/module может быть нормальным владельцем этой сложности. В текущей
задаче команда относится к одному `Service Intake`, поэтому естественный владелец — его
controller.

## Результат

После инженерного моста ученик должен различать:

```text
metadata invariant
controller invariant
Workflow transition
permission check
semantic command
request transaction
post-commit side effect
patch/data migration
automated test
```

И главное — уметь объяснить, **почему код появился именно в этой точке, а не раньше**.
