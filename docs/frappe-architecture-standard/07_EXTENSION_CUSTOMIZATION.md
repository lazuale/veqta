# 07. Extension и Customization — как изменять Frappe и чужие Apps без форка

## 1. Сначала определить ownership

Перед изменением существующего DocType нужно ответить:

```text
Кто владеет моделью?

наше App?
Frappe?
ERPNext?
другое installed App?
конкретный Site?
```

Это важнее выбора конкретного hook.

### Если DocType наш

Обычно мы свободно меняем Standard DocType, Controller и metadata в source tree App.

### Если DocType чужой

Нужно расширять его через предусмотренные Framework mechanisms, а не копировать/форкать модель без необходимости.

---

## 2. Hooks — официальный extension mechanism

**[FRAPPE DOCS]** Hooks определяются как места в core, позволяющие App override или extend standard implementation.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks

Это прямое архитектурное намерение Frappe.

Следовательно, поиск решения для расширения чужого App должен начинаться с официальных seams.

---

## 3. Custom Field

Custom Field позволяет добавить поле существующему DocType без изменения его исходного JSON.

Официальные материалы по export/customization:

- https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations
- https://docs.frappe.io/framework/user/en/guides/app-development/how-to-create-custom-fields-during-app-installation

### Подходящий сценарий

Наш App требует, чтобы стандартный `Customer` имел дополнительный field:

```text
external_customer_id
```

Создавать копию `My Customer` только ради одного поля обычно гораздо хуже, чем расширить существующую модель.

---

## 4. Property Setter

Frappe customization model позволяет изменять свойства стандартных fields/DocType без прямого редактирования исходного JSON чужого App.

`frappe.get_meta()` объединяет standard metadata с Custom Fields и Property Setters.

Источник:

- https://docs.frappe.io/framework/user/en/api/document

Это важный пруф: customization не является внешним костылём, она встроена в Meta model.

---

## 5. Site customization vs App-owned customization

Главное различие:

### Site-owned

Изменение специфично для одного site:

```text
локальное поле;
локальная форма;
локальная Notification;
локальный Workflow.
```

Оно может жить как runtime customization.

### App-owned

Изменение является обязательной частью продукта и должно появляться на каждом site после install/update.

Тогда состояние должно быть воспроизводимо из App.

**[FRAPPE DOCS]** Frappe позволяет экспортировать Custom Fields и Property Setters в App; при `bench update`/`bench migrate` они синхронизируются.

Источник:

- https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

---

## 6. Важное предупреждение при export customizations

**[FRAPPE DOCS]** Export Customizations имеет сильную семантику: при sync Property Setters и Custom Permissions на target site могут быть заменены тем, что указано в коде.

Источник:

- https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations

### Архитектурный вывод

Нельзя бездумно одновременно считать один и тот же customization:

```text
частью продукта
и
свободно редактируемой локальной настройкой каждого site
```

Нужно определить владельца конфигурации.

---

## 7. Fixtures

**[FRAPPE DOCS]** Fixtures — database records, которые экспортируются в JSON и синхронизируются при install/update.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks#fixtures

Подходят для records, являющихся частью App configuration.

Пример:

```text
обязательные Role;
набор категорий продукта;
Custom Fields;
определённая configuration metadata.
```

Не использовать fixtures как способ положить в Git обычные пользовательские transactions.

---

## 8. Client Script как customization seam

Client Script может быть site-specific customization для UI behaviour.

Источник:

- https://docs.frappe.io/framework/user/en/desk/scripting/client-script

Но если JavaScript является обязательной частью source-controlled App, standard JS files/hooks обычно дают лучше управляемый deployment path.

### Критическая граница

Client Script не заменяет server validation/security.

---

## 9. Server Script как runtime extension

**[FRAPPE DOCS]** Server Script поддерживает Document Event и API modes, но с v15 disabled by default на shared benches.

Источник:

- https://docs.frappe.io/framework/user/en/desk/scripting/server-script

Следовательно, runtime Server Script хорошо подходит не для любой application logic, а для ограниченного класса site/custom low-code extensions.

Если логика является ядром App, Python source обычно лучше переносится и тестируется.

---

## 10. `doc_events`

**[FRAPPE DOCS]** Hook `doc_events` позволяет App подписываться на lifecycle events DocTypes.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks

Это естественный seam, когда наше App **не владеет Controller**, но хочет реагировать на чужой Document.

Пример:

```text
ERPNext Sales Invoice submitted
        ↓
наше App создаёт Integration Record
```

Нет необходимости редактировать `sales_invoice.py` ERPNext.

---

## 11. `extend_doctype_class` — v16+

**[FRAPPE DOCS]** В v16 `extend_doctype_class` позволяет добавлять методы/свойства к существующему DocType через mixin-like extension.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks#extend-doctype-class

Документация рекомендует prefer extension вместо полного override, когда требуется добавить functionality.

### Подходящий случай

Наше App хочет добавить reusable behaviour существующему `Address`, не заменяя весь Controller.

```text
extend_doctype_class
```

обычно имеет меньший конфликтный surface.

---

## 12. `override_doctype_class`

**[FRAPPE DOCS]** Этот hook полностью заменяет controller class DocType.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks#override-doctype-class

Это более сильное вмешательство.

Риски:

```text
несколько Apps хотят override один class;
upstream меняет original Controller;
нужно самостоятельно наследовать/сохранять нужное поведение;
повышается coupling к implementation другого App.
```

### Правило

**[ARCHITECTURAL INFERENCE]** В v16 extension предпочтительнее replacement, если задача действительно состоит только в добавлении поведения.

---

## 13. Override whitelisted method

Frappe также имеет hook `override_whitelisted_methods`.

Источник:

- https://docs.frappe.io/framework/user/en/python-api/hooks

Полная замена API method — сильный extension. Перед ней нужно убедиться, что:

- обычное событие/extension hook не решает задачу;
- изменение действительно должно заменить semantics метода;
- учтены другие Apps, также способные override method.

---

## 14. Hook order и несколько Apps

Hooks живут не в вакууме. На site установлено несколько Apps.

Следовательно, extension design должен учитывать:

```text
какой App зависит от какого;
может ли несколько Apps подписаться на событие;
может ли несколько Apps пытаться override одно место;
какой порядок выполнения критичен.
```

Это особенно важно для полного override, меньше — для composable event hooks.

---

## 15. Patch core — крайний red flag

Плохой default:

```text
открыть frappe/.../document.py
и изменить Framework под своё приложение
```

или аналогично модифицировать installed ERPNext file.

Почему:

- update перезапишет/конфликтует с изменением;
- репозиторий App больше не содержит полной правды;
- другой site не воспроизводится обычной установкой;
- upgrade analysis резко усложняется.

### Правильный порядок

```text
1. Проверить configuration/customization.
2. Проверить hooks/doc_events.
3. Проверить extend_doctype_class.
4. Проверить override mechanism.
5. Только после доказанной невозможности — обсуждать fork/core patch.
```

Это **[ARCHITECTURAL INFERENCE]**, основанный на наличии официальных extension seams.

---

## 16. Fork может быть оправдан

Стандарт не объявляет fork запрещённым.

Fork Framework/ERPNext может быть осознанным выбором, если организация:

- намеренно поддерживает собственную distribution;
- принимает постоянную стоимость merge/upgrades;
- изменение невозможно выразить extension API;
- изменение настолько глубоко, что upstream contract не подходит.

Но тогда это уже отдельная продуктовая стратегия, а не незаметная «правка одного файла».

---

## 17. Packages

**[FRAPPE DOCS]** Packages — lightweight apps, собираемые из UI-created custom modules и переносимые между sites.

Источник:

- https://docs.frappe.io/framework/user/en/guides/deployment/packages

Они показывают, что Frappe официально поддерживает не только Python-first development, но и переносимую metadata/configuration development model.

Однако Package не обязан заменять App. Выбор зависит от требуемого кода, dependencies и deployment model.

---

## 18. Extension decision track

```text
Изменяем собственный DocType?
    → Standard metadata + Controller

Добавляем field/property чужому DocType?
    → Custom Field / Property Setter

Нужно поставлять customization вместе с App?
    → export customization / fixtures

Нужно реагировать на lifecycle чужого DocType?
    → doc_events

Нужно добавить behaviour чужому class? [v16+]
    → extend_doctype_class

Нужно полностью заменить Controller?
    → override_doctype_class, с отдельным обоснованием

Ничего из этого не выражает требование?
    → custom extension/fork decision
```

---

## 19. Design review extension

```text
1. Кто владеет исходным DocType?
2. Изменение site-specific или app-owned?
3. Нужен Custom Field/Property Setter или новый DocType?
4. Как customization попадёт на новый site?
5. Нет ли конфликта с локальными customizations target site?
6. Есть ли официальный hook?
7. Можно ли extension вместо override?
8. Какие другие Apps могут затронуть тот же seam?
9. Что произойдёт после upstream update?
10. Можно ли воспроизвести систему без ручной правки core?
```
