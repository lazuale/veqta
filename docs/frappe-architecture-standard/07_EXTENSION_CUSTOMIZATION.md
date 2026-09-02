# 07. Extension and Customization

## 1. Два разных вопроса

Во Frappe важно различать:

```text
как изменить конкретный site?
```

и

```text
как расширить устанавливаемое App/другое App?
```

Первое — customization.
Второе — application extension/deployment design.

---

## 2. Site customization

Для локального изменения site Frappe предоставляет:

- Customize Form;
- Custom Field;
- Property Setter;
- Client Script;
- Server Script;
- Workflow;
- Notification;
- другие metadata/configuration records.

Это нормальный native layer.

### Когда подходит

Когда изменение действительно принадлежит конкретному site и не обязано автоматически появляться во всех установках App.

---

## 3. Product-owned change

Если изменение является частью продукта, должно существовать воспроизводимое source/deployment представление.

Контрольный вопрос:

> После установки App на чистый совместимый site это изменение должно существовать?

Если да, ручное «накликать после установки» недостаточно.

---

## 4. Custom Field

Custom Field естественен, когда нужно добавить поле к DocType, которым наше App не владеет, либо сделать site-level customization.

Пример:

```text
ERPNext Customer
+
our_external_customer_id
```

Копировать `Customer` в собственный `Our Customer` только ради одного поля не нужно.

---

## 5. Property Setter

Property Setter позволяет изменить свойства стандартной metadata без модификации upstream DocType JSON.

Это важный extension mechanism для чужих DocTypes.

### Красный флаг

Не редактировать JSON/исходник чужого App вручную, если изменение должно жить как customization/extension.

---

## 6. Exported customizations

Если Custom Fields/Property Setters должны ехать вместе с App, их можно экспортировать штатными средствами.

Но нужно понимать ownership:

экспортированная customization уже становится частью delivery contract App.

### Review question

> Может ли этот App безопасно применять такую customization на каждом target site?

---

## 7. Fixtures

Fixtures подходят для конфигурационных records, являющихся частью App.

Примеры возможных candidates:

- custom configuration;
- roles/records, если это действительно часть продукта;
- определённые metadata-related records.

### Не использовать fixtures как backup бизнес-данных

Пользовательские transactions не должны случайно становиться source-controlled fixtures.

---

## 8. hooks.py

Hooks — официальный механизм подключения App к Framework lifecycle и extension points.

Это нормальная часть Frappe architecture, а не workaround.

Через hooks подключаются:

- document events;
- scheduler events;
- fixtures;
- overrides/extensions;
- JS/CSS assets;
- permission logic;
- install/migrate-related behavior;
- другие framework seams.

---

## 9. doc_events

Если наше App должно реагировать на lifecycle Document другого App:

```text
Sales Invoice on_submit
```

`doc_events` является естественной точкой расширения.

Это лучше, чем изменять controller Sales Invoice в upstream repository.

---

## 10. extend_doctype_class [v16+]

В Frappe v16 `extend_doctype_class` позволяет добавлять поведение существующему Controller без полной замены класса.

Это особенно полезно для composable extensions.

### Архитектурный принцип

```text
нужно добавить поведение
    → extension

нужно полностью заменить semantics
    → только тогда override
```

---

## 11. override_doctype_class

Полная замена Controller — сильное вмешательство.

Риски:

- другой App тоже хочет override;
- upstream добавляет новое поведение;
- dependency order становится важным;
- compatibility сложнее проверять.

Поэтому override оправдан, когда extension действительно недостаточно.

---

## 12. doctype_js / client extension

Если нужно расширить UI чужого DocType, использовать соответствующие client-side extension mechanisms вместо редактирования upstream JS-файла.

UI extension должен оставаться отделён от server security/invariants.

---

## 13. Permission hooks

Custom permission hooks являются официальной точкой расширения security model.

Но они должны дополнять permission engine, а не подменять его параллельным ACL.

Подробно — `04_SECURITY.md`.

---

## 14. Scheduler hooks

Периодические application tasks подключаются через scheduler events.

Не нужно создавать отдельный daemon для обычной site-level периодической работы, если штатный scheduler подходит по семантике.

---

## 15. Override whitelisted methods

Framework поддерживает override некоторых whitelisted methods.

Это сильный integration seam и должен использоваться осторожно:

- понимать внешний contract;
- учитывать другие Apps;
- тестировать upgrade compatibility.

Если можно добавить новый method вместо замены существующего — обычно это безопаснее.

---

## 16. Core patching

Изменение файлов `frappe/` или другого installed App напрямую — не нормальный default extension method.

Почему:

```text
local modification
+
upstream update
=
upgrade conflict
```

Если официальный seam существует, он предпочтительнее.

### Исключение

Если Framework имеет bug/ограничение, правильный долгосрочный путь может включать upstream contribution или временный fork.

Но это должно быть явным решением, а не скрытой локальной правкой.

---

## 17. Fork

Fork не является автоматически неправильным.

Он оправдан, если продукт сознательно принимает ответственность за поддержание diverged upstream.

Но цена включает:

- merges;
- security updates;
- migration conflicts;
- long-term maintenance.

Поэтому fork — отдельная архитектурная стратегия, а не способ быстро изменить одну кнопку.

---

## 18. Server Script

Server Script — site/runtime extension surface.

Он удобен для ограниченной automation, но имеет инфраструктурные ограничения и может быть отключён.

Для core logic source-controlled App normal Python часто предпочтительнее.

### Правило

Не делать Server Script скрытой обязательной частью продукта, если App должен воспроизводимо устанавливаться в разных средах.

---

## 19. Client Script

Client Script — site-level UI customization.

Если behavior является частью product App, его нужно либо экспортировать/доставлять штатно, либо реализовать в source JS App.

Главный вопрос снова ownership, а не «low-code vs code».

---

## 20. Workflow и Notification как deployable configuration

Если Workflow/Notification являются обязательной частью продукта, нужно определить, как они поставляются:

- fixtures;
- exported customization;
- install setup;
- другое воспроизводимое средство.

Нельзя надеяться на ручное создание в production после каждого fresh install.

---

## 21. App dependencies

Если наше App расширяет DocType другого App, эта dependency должна быть явной.

Пример:

```text
our_app требует ERPNext
```

Иначе App может устанавливаться на site, где target DocType отсутствует.

Extension architecture должна учитывать install order и dependency management.

---

## 22. Hook ordering

При нескольких installed Apps один и тот же extension point может использоваться несколькими участниками.

Нельзя проектировать hook как будто наше App единственное в bench.

Особенно опасны:

- full overrides;
- shared global events;
- monkey patches;
- assumptions о порядке выполнения.

---

## 23. Extension ownership matrix

| Ситуация | Первый кандидат |
|---|---|
| поле только для одного site | Custom Field |
| изменить свойство стандартного поля | Property Setter |
| поставлять customization с App | export/fixtures |
| реагировать на чужой Document event | doc_events |
| добавить server behavior чужому DocType | extend_doctype_class [v16+] |
| полностью заменить Controller | override_doctype_class |
| добавить client behavior | doctype JS/client extension |
| периодическая работа | scheduler hook |
| custom security policy | permission hooks |
| upstream bug/невозможный extension | contribution/fork как отдельное решение |

---

## 24. Что такое «технический хвост» customization

Плохой deployment оставляет знания вне repository:

```text
после install-app вручную:
1. добавить поле
2. изменить permission
3. создать Workflow
4. настроить Notification
```

Если это обязательная product configuration — это technical tail.

Правильный target:

```text
clean site
+ install app
+ migrate
=
required product state
```

---

## 25. Decision track

```text
Изменение принадлежит только site?
        → site customization

Изменение — часть продукта?
        → source/export/fixture

Расширяем чужой DocType?
        → официальный hook/extension

Нужно добавить поведение Controller?
        → extend_doctype_class [v16+]

Нужно полностью заменить behavior?
        → override только с обоснованием

Официального seam нет?
        → проверить upstream contribution/fork/custom boundary
```

---

## 26. Design review checklist

- [ ] Определён владелец изменения: Framework/App/Site.
- [ ] Product-required customization воспроизводима из repository.
- [ ] Custom Fields/Property Setters не требуют ручного production setup.
- [ ] Fixtures не содержат пользовательские transactions.
- [ ] Чужой Controller не изменён напрямую.
- [ ] `extend_doctype_class` рассмотрен до full override на v16+.
- [ ] Full overrides проверены на conflicts/dependencies.
- [ ] Server Script не является случайной infrastructure dependency.
- [ ] Hook ordering/multiple Apps учтены.
- [ ] Fork/core patch имеет явное долгосрочное обоснование.
