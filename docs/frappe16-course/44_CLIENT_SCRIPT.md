# 44. Client Script

В предыдущем блоке мы разобрали внешние интерфейсы Frappe:

```text
Web Form
Website / Portal
REST API
RPC
Authentication
```

Теперь начинается блок **Low-code и разработка**.

Первый инструмент здесь — `Client Script`.

Главный вопрос этой главы:

```text
как изменить поведение Desk Form или List View
не создавая полноценный App
```

Проверено: **2026-08-31**.

---

# Часть I. Что такое Client Script простыми словами

## 1. Form View уже умеет очень много

Обычный DocType автоматически получает:

```text
поля
Save
Submit / Cancel
permissions
attachments
comments
timeline
links
```

Но иногда хочется изменить именно поведение интерфейса.

Например:

```text
если Priority = High
→ сделать Due Date обязательным

если документ уже сохранён
→ показать кнопку "Закрыть"

при выборе Customer
→ ограничить список доступных Contract
```

Для этого можно использовать Client Script.

---

## 2. Client Script — JavaScript, который выполняется в браузере

Упрощённо:

```text
User opens Form
      ↓
Frappe loads metadata
      ↓
Client Script arrives in browser
      ↓
JavaScript subscribes to Form events
      ↓
UI reacts to user actions
```

То есть Client Script работает не на Python server, а внутри браузера пользователя.

---

## 3. Аналогия

Представь стандартную Form View как готовый автомобиль.

DocType определяет:

```text
кузов
двигатель
основные органы управления
```

Client Script — это дополнительная электронная логика:

```text
если включили режим X
→ показать предупреждение

если нажали кнопку Y
→ выполнить действие
```

Он меняет поведение интерфейса, но не заменяет серверную бизнес-логику.

---

# Часть II. Где находится Client Script

## 4. Client Script — отдельный DocType Framework

В Desk можно создать документ:

```text
Client Script
```

В v16 у него есть ключевые поля:

```text
DocType
Apply To
Module (for export)
Enabled
Script
```

---

## 5. `DocType`

Определяет, к какому DocType относится скрипт.

Например:

```text
Request
```

---

## 6. `Apply To`

В текущем v16 доступны два значения:

```text
Form
List
```

Это важная деталь.

Client Script — не только Form Script.

Он может кастомизировать:

```text
Form View
или
List View
```

---

## 7. `Enabled`

Если выключить:

```text
Enabled = 0
```

скрипт не попадёт в активные custom scripts этого DocType.

---

## 8. `Module (for export)`

Это поле связано с переносом custom logic в управляемую структуру приложения.

Сам механизм экспорта и разница:

```text
Custom
vs
Standard
vs
fixtures / exported customization
```

будут отдельно разобраны в следующих главах.

---

## 9. Кто может создавать Client Script

Штатные permissions v16 на DocType `Client Script` выданы:

```text
System Manager
Administrator
```

Документация также прямо указывает, что для создания Client Script нужен System Manager.

Это правильно: Client Script фактически позволяет запускать произвольный JavaScript в Desk пользователей данного DocType.

---

# Часть III. Client Script против standard JS файла

## 10. Есть два способа написать Form Script

### Вариант A — Client Script в базе

```text
Desk
→ Client Script
→ Script field
```

### Вариант B — standard JavaScript в App

```text
my_app/
  module/
    doctype/
      request/
        request.js
```

---

## 11. Client Script подходит для site-specific логики

Официальная документация формулирует границу так:

```text
логика нужна только этому Site
→ Client Script
```

---

## 12. JS файл App подходит для переносимой логики

Если поведение должно одинаково работать:

```text
на нескольких Sites
в dev/test/prod
после установки App
из Git
```

то его естественнее хранить в App.

---

## 13. Это не два разных Form API

И Client Script, и standard `{doctype}.js` используют тот же основной API:

```javascript
frappe.ui.form.on(...)
```

Поэтому прототип можно сделать как Client Script, а стабильную реализацию позже перенести в App.

---

# Часть IV. Самый простой Form Client Script

## 14. Базовый шаблон

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        // код
    }
});
```

---

## 15. Что здесь происходит

```text
frappe.ui.form.on
```

регистрирует обработчики событий Form для указанного DocType.

```text
Request
```

— имя DocType.

```text
refresh
```

— событие.

```text
frm
```

— текущая Form.

---

# Часть V. Объект `frm`

## 16. `frm` — главный объект Form Script

Через него можно обращаться к:

```text
текущему Document
полям формы
кнопкам
save / reload
Link queries
Child Tables
server methods
```

---

## 17. Текущий Document находится в `frm.doc`

Например:

```javascript
frm.doc.status
```

```javascript
frm.doc.priority
```

```javascript
frm.doc.name
```

---

## 18. Пример чтения значения

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        console.log(frm.doc.status);
    }
});
```

---

## 19. `frm.doc` — клиентская копия Document

Важно понимать архитектуру:

```text
Database Document
      ↓ load
Browser copy → frm.doc
      ↓ save
Server validates and writes
```

Изменение объекта в браузере ещё не означает, что значение уже сохранено в БД.

---

# Часть VI. События Form

## 20. Client Script обычно строится вокруг событий

Frappe сам сообщает:

```text
форма создаётся
загружается
рендерится
поле изменилось
пользователь сохраняет
документ сохранён
submit
cancel
```

А Script подписывается только на нужные события.

---

## 21. `setup`

```javascript
setup(frm) {
}
```

Срабатывает один раз при создании Form.

Хорошее место для ранней конфигурации, например Link query.

---

## 22. `before_load`

```javascript
before_load(frm) {
}
```

Срабатывает перед загрузкой Form.

---

## 23. `onload`

```javascript
onload(frm) {
}
```

Form загружена и собирается рендериться.

---

## 24. `refresh`

```javascript
refresh(frm) {
}
```

Одно из самых часто используемых событий.

Оно подходит для:

```text
кнопок
intro messages
динамических UI properties
проверки текущего состояния
```

---

## 25. Почему `refresh` может выполняться много раз

`refresh` — не событие «открыли страницу один раз».

Оно может срабатывать после:

```text
load
save
submit
reload
других refresh операций
```

Поэтому код в `refresh` должен быть безопасным для повторного запуска.

---

## 26. Типичная ошибка — бесконечно добавлять кнопки

Если логика плохо организована, каждый refresh может пытаться повторно построить UI.

Frappe многие стандартные методы обрабатывает корректно, но всё равно нужно мыслить так:

```text
refresh может повториться
```

---

## 27. `onload_post_render`

```javascript
onload_post_render(frm) {
}
```

Срабатывает после загрузки и рендера Form.

Используется реже, когда действительно нужен уже отрисованный UI.

---

## 28. `validate`

```javascript
validate(frm) {
}
```

Срабатывает перед `before_save`.

Подходит для клиентской проверки перед сохранением через стандартную Form View.

---

## 29. `before_save`

```javascript
before_save(frm) {
}
```

Срабатывает непосредственно перед вызовом Save.

---

## 30. `after_save`

```javascript
after_save(frm) {
}
```

Срабатывает после успешного сохранения Form.

---

## 31. Submit events

Для Submittable DocType есть:

```text
before_submit
on_submit
```

---

## 32. Cancel events

Есть:

```text
before_cancel
after_cancel
```

---

## 33. Discard events

В v16 Form API также документирует:

```text
before_discard
after_discard
```

---

## 34. `timeline_refresh`

Срабатывает после рендера timeline.

Это уже более узкая UI-задача.

---

# Часть VII. События конкретного поля

## 35. Имя fieldname само является событием

Допустим есть поле:

```text
priority
```

Можно написать:

```javascript
frappe.ui.form.on('Request', {
    priority(frm) {
        console.log(frm.doc.priority);
    }
});
```

---

## 36. Событие сработает при изменении значения

Например пользователь выбрал:

```text
Priority = High
```

и код сразу отреагировал.

---

## 37. Пример

```javascript
frappe.ui.form.on('Request', {
    priority(frm) {
        frm.toggle_reqd('due_date', frm.doc.priority === 'High');
    }
});
```

---

# Часть VIII. `frm.set_value()`

## 38. Не обязательно писать прямо в `frm.doc`

Для обычного изменения поля лучше использовать:

```javascript
frm.set_value('status', 'Open');
```

---

## 39. `set_value` запускает field change event

Это важное отличие.

Если сделать:

```javascript
frm.set_value('priority', 'High');
```

Frappe также вызовет обработчик:

```javascript
priority(frm) {
}
```

---

## 40. Можно установить несколько значений

```javascript
frm.set_value({
    status: 'Open',
    priority: 'High'
});
```

---

## 41. `frm.set_value()` возвращает Promise

```javascript
frm.set_value('status', 'Open').then(() => {
    // значение установлено
});
```

Или:

```javascript
await frm.set_value('status', 'Open');
```

в `async` handler.

---

# Часть IX. Async handlers

## 42. Form handlers могут возвращать Promise

Текущий ScriptManager v16 проверяет результат handler.

Если он Promise, Form event chain ждёт его завершения.

Поэтому можно писать:

```javascript
frappe.ui.form.on('Request', {
    async customer(frm) {
        await frm.set_value('priority', 'Medium');
    }
});
```

---

## 43. Это полезно при server calls

Например:

```javascript
async refresh(frm) {
    let r = await frappe.call({
        method: 'my_app.api.get_info'
    });
}
```

Но тяжёлые server calls в `refresh` без необходимости делать не стоит.

---

# Часть X. Dirty state

## 44. Изменённая Form становится dirty

То есть:

```text
есть несохранённые изменения
```

---

## 45. Проверить можно через

```javascript
frm.is_dirty()
```

---

## 46. `frm.dirty()`

Если вы вручную изменили данные способом, который Frappe не отследил:

```javascript
frm.doc.some_value = 'X';
frm.dirty();
```

тогда Form покажет состояние:

```text
Not Saved
```

---

## 47. Но лучше не превращать прямое изменение `frm.doc` в основной стиль

Для обычных полей:

```javascript
frm.set_value(...)
```

обычно понятнее и безопаснее для event flow.

---

# Часть XI. `frm.save()`

## 48. Сохранить Form программно

```javascript
frm.save();
```

---

## 49. Для Submittable документа

```javascript
frm.save('Submit');
```

---

## 50. Cancel

```javascript
frm.save('Cancel');
```

---

## 51. Update submitted document

```javascript
frm.save('Update');
```

если серверные правила позволяют изменение соответствующих полей после Submit.

---

## 52. Client Script не обходит серверный lifecycle

Даже если JS вызвал:

```javascript
frm.save('Submit')
```

сервер всё равно выполняет обычные проверки Document lifecycle и permissions.

---

# Часть XII. Изменение свойств полей

## 53. `frm.set_df_property()`

Можно динамически изменить property DocField в текущей Form.

Например:

```javascript
frm.set_df_property('status', 'read_only', 1);
```

---

## 54. Сделать поле mandatory

```javascript
frm.set_df_property('due_date', 'reqd', 1);
```

---

## 55. Изменить options Select

```javascript
frm.set_df_property('status', 'options', ['Open', 'Closed']);
```

---

## 56. Это runtime UI change

Не нужно путать его с постоянным изменением DocField metadata.

```text
Customize Form / DocType
→ постоянная metadata

frm.set_df_property
→ поведение текущей Form в браузере
```

---

# Часть XIII. Удобные toggle methods

## 57. `frm.toggle_display()`

```javascript
frm.toggle_display('due_date', frm.doc.status === 'Open');
```

Показывает или скрывает поле.

---

## 58. `frm.toggle_reqd()`

```javascript
frm.toggle_reqd('due_date', frm.doc.priority === 'High');
```

Делает поле обязательным в UI.

---

## 59. `frm.toggle_enable()`

```javascript
frm.toggle_enable('priority', frm.doc.status === 'Draft');
```

Управляет read-only состоянием.

---

## 60. UI mandatory ≠ server mandatory

Критически важно.

Если обязательность существует только так:

```javascript
frm.toggle_reqd(...)
```

REST API клиент этот JavaScript не выполняет.

Поэтому критическая бизнес-проверка должна существовать на server side.

---

# Часть XIV. Intro и сообщения

## 61. Intro message

```javascript
frm.set_intro('Заполните обязательные реквизиты', 'orange');
```

---

## 62. Alert

```javascript
frappe.show_alert({
    message: 'Готово',
    indicator: 'green'
});
```

---

## 63. Message dialog

```javascript
frappe.msgprint('Проверьте данные');
```

---

## 64. Confirm

Для подтверждения действия можно использовать стандартные Dialog APIs Frappe.

Но UI confirm никогда не должен быть единственной защитой опасной server operation.

---

# Часть XV. Custom Buttons

## 65. Добавить кнопку

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        frm.add_custom_button('Закрыть', () => {
            frappe.msgprint('Clicked');
        });
    }
});
```

---

## 66. Кнопка может быть условной

```javascript
refresh(frm) {
    if (!frm.is_new() && frm.doc.status === 'Open') {
        frm.add_custom_button('Закрыть', () => {
            // action
        });
    }
}
```

---

## 67. Кнопки можно группировать

```javascript
frm.add_custom_button(
    'Закрыть',
    () => {},
    'Действия'
);
```

---

## 68. Можно менять тип кнопки

```javascript
frm.change_custom_button_type(
    'Закрыть',
    'Действия',
    'danger'
);
```

---

## 69. Можно удалить кнопку

```javascript
frm.remove_custom_button('Закрыть', 'Действия');
```

---

## 70. Кнопка — только UI entry point

Если она выполняет серьёзную бизнес-команду:

```text
Approve
Close Period
Delete external object
Recalculate
```

сама операция должна жить на server side.

Client Script лишь вызывает её.

---

# Часть XVI. Link field filters

## 71. Типичная задача

Есть Link:

```text
Contract
```

Но пользователь должен выбирать только Contract нужной Company.

---

## 72. `frm.set_query()`

```javascript
frappe.ui.form.on('Request', {
    setup(frm) {
        frm.set_query('contract', () => {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
    }
});
```

---

## 73. `set_query` лучше назначать рано

Официальная документация рекомендует:

```text
setup
или
onload
```

---

## 74. Link filter — не permission rule

Даже если UI показывает только:

```text
Company A contracts
```

это не означает, что пользователь технически не может запросить другой Document через иной интерфейс.

Настоящие permissions остаются server-side.

---

## 75. `set_query` для Link внутри Child Table

```javascript
frm.set_query('item_code', 'items', () => {
    return {
        filters: {
            disabled: 0
        }
    };
});
```

---

## 76. Можно использовать custom query method

```javascript
frm.set_query('contract', () => {
    return {
        query: 'my_app.api.contract_query',
        filters: {
            company: frm.doc.company
        }
    };
});
```

Серверный query method уже должен безопасно формировать разрешённый результат.

---

# Часть XVII. Child Tables

## 77. Child row тоже имеет события

Допустим parent DocType:

```text
Request
```

а Child DocType:

```text
Request Item
```

---

## 78. Handler пишется на Child DocType

```javascript
frappe.ui.form.on('Request Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        console.log(row.qty);
    }
});
```

---

## 79. Что такое `cdt`

```text
Child DocType
```

Например:

```text
Request Item
```

---

## 80. Что такое `cdn`

Это имя конкретной child row в клиентской модели.

Например:

```text
a6dfk76...
```

---

## 81. Получить строку

```javascript
let row = frappe.get_doc(cdt, cdn);
```

---

## 82. Установить значение child row

```javascript
frappe.model.set_value(
    cdt,
    cdn,
    'amount',
    row.qty * row.rate
);
```

---

## 83. Добавление row event

Если Table field parent называется:

```text
items
```

то event:

```javascript
items_add(frm, cdt, cdn) {
}
```

---

## 84. Удаление row

Есть:

```text
before_items_remove
items_remove
```

---

## 85. Перемещение row

```text
items_move
```

---

## 86. Открытие row как формы

```text
form_render
```

---

## 87. Особенность v16

Официальная Form API отдельно отмечает, что начиная с v16 события:

```text
before_{fieldname}_remove
{fieldname}_add
{fieldname}_remove
```

также работают для `Table MultiSelect`.

---

# Часть XVIII. Добавление строки из Client Script

## 88. `frm.add_child()`

```javascript
let row = frm.add_child('items', {
    item_code: 'ITEM-001',
    qty: 1
});
```

---

## 89. После изменения Table обычно нужен refresh field

```javascript
frm.refresh_field('items');
```

---

# Часть XIX. `frm.refresh_field()` и reload

## 90. Refresh конкретного поля

```javascript
frm.refresh_field('priority');
```

---

## 91. Reload Document с сервера

```javascript
frm.reload_doc();
```

---

## 92. `frm.refresh()`

Заново обновляет Form и запускает соответствующий event flow.

Не используй полный refresh как универсальное решение каждой UI-проблемы.

---

# Часть XX. Вызов серверного кода

## 93. Client Script не обязан делать всё сам

Правильная архитектура часто выглядит так:

```text
Client Script
→ UI logic
→ server call
→ business logic / permission checks
→ result
→ Client Script обновляет UI
```

---

## 94. `frappe.call()`

Для module-level whitelisted method:

```javascript
let r = await frappe.call({
    method: 'my_app.api.close_request',
    args: {
        name: frm.doc.name
    }
});
```

---

## 95. Серверный method должен быть whitelisted

```python
@frappe.whitelist(methods=['POST'])
def close_request(name):
    ...
```

Тема подробно разобрана в главе 42.

---

## 96. `frm.call()`

Если method находится в controller текущего Document:

```javascript
let r = await frm.call('get_linked_doc', {
    throw_if_missing: true
});
```

---

## 97. `frm.call()` не делает private Python method публичным автоматически

Controller method всё равно требует:

```python
@frappe.whitelist()
```

---

## 98. Не делай прямой server call на каждое нажатие клавиши

Например field event может срабатывать очень часто.

Плохой UX:

```text
каждое изменение
→ request на server
→ latency
→ ещё request
```

Нужно понимать частоту события и стоимость операции.

---

# Часть XXI. Client validation

## 99. Простая client validation

```javascript
frappe.ui.form.on('Request', {
    validate(frm) {
        if (frm.doc.priority === 'High' && !frm.doc.due_date) {
            frappe.throw('Укажите Due Date');
        }
    }
});
```

---

## 100. Это хороший UX

Пользователь получает ошибку ещё в форме.

Но это не надёжная business constraint.

---

## 101. Почему Client validation можно обойти

Она работает только там, где выполняется этот JavaScript.

Например:

```text
REST API
Python code
System Console
background job
другая форма
```

не обязаны запускать Client Script.

Официальная документация прямо предупреждает об этом.

---

## 102. Поэтому важное правило должно существовать на сервере

Например:

```text
High Priority всегда требует Due Date
```

Если это реальное правило данных, проверка должна жить в:

```text
DocType metadata
или
server validation
или
controller
```

Client Script может только продублировать её ради удобного UX.

---

# Часть XXII. Security boundary

## 103. Client Script не является security layer

Никогда не делай так:

```javascript
if (!frappe.user_roles.includes('Manager')) {
    frm.toggle_display('secret_field', false);
}
```

и не считай после этого поле защищённым.

---

## 104. Скрытое поле всё ещё может существовать в данных

UI visibility и permission — разные вещи.

Настоящая защита строится через:

```text
Role Permissions
Permission Level
User Permissions
server-side checks
```

---

## 105. Нельзя доверять значению из browser

Пользователь контролирует browser.

Он может:

```text
изменить JS
вызвать endpoint вручную
подменить request
изменить локальный объект
```

Поэтому сервер проверяет всё важное заново.

---

# Часть XXIII. Секреты

## 106. Никогда не помещай API Secret в Client Script

Например запрещено делать:

```javascript
const SECRET = 'abc123';
```

---

## 107. Почему

Client Script отправляется в browser.

Пользователь может увидеть его через:

```text
Developer Tools
Network
Sources
runtime objects
```

---

## 108. Правильная схема внешнего API

```text
Browser Client Script
→ Frappe whitelisted method
→ secret хранится server-side
→ внешний API
```

Если вообще нужен такой вызов.

---

# Часть XXIV. Roles в Client Script

## 109. Можно менять UX по ролям

Например:

```javascript
if (frappe.user_roles.includes('System Manager')) {
    // показать дополнительную кнопку
}
```

---

## 110. Но это только UX

Это не должно быть единственной проверкой permission.

```text
button visibility
≠
authorization
```

---

# Часть XXV. `frm.trigger()`

## 111. Можно создавать собственные Form events

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        frm.trigger('update_ui');
    },

    update_ui(frm) {
        frm.toggle_display(
            'resolution',
            frm.doc.status === 'Closed'
        );
    }
});
```

---

## 112. Это помогает не копировать код

Вместо:

```text
один и тот же блок в refresh
тот же блок в status
тот же блок в after_save
```

можно иметь один helper event.

---

# Часть XXVI. Хорошая организация Client Script

## 113. Плохой вариант

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        // 300 строк всего подряд
    }
});
```

---

## 114. Лучше разделить события

```javascript
frappe.ui.form.on('Request', {
    setup(frm) {
        frm.trigger('setup_queries');
    },

    refresh(frm) {
        frm.trigger('update_buttons');
        frm.trigger('update_visibility');
    },

    status(frm) {
        frm.trigger('update_visibility');
    },

    setup_queries(frm) {
        // ...
    },

    update_buttons(frm) {
        // ...
    },

    update_visibility(frm) {
        // ...
    }
});
```

---

## 115. Но не строй второй framework внутри Client Script

Если появились:

```text
десятки helper layers
огромные state machines
сложные shared modules
много API endpoints
500–1000+ строк логики
```

это сигнал переводить реализацию в App.

---

# Часть XXVII. Несколько Client Scripts на один DocType

## 116. Это возможно

Текущий v16 собирает все включённые `Client Script` для DocType.

Для Form и List они разделяются по `Apply To`.

---

## 117. В текущей реализации v16 scripts собираются по creation ascending

То есть более ранние записи добавляются раньше.

Но не стоит строить архитектуру, где правильность системы зависит от скрытого порядка десятка Client Scripts.

---

## 118. Лучше один логически цельный Client Script на одну область поведения

Например:

```text
Request — Form behavior
```

чем пять скриптов, которые взаимно меняют одни и те же поля.

---

# Часть XXVIII. Как Frappe загружает Client Script

## 119. Client Scripts попадают в Form metadata

В v16 `FormMeta.add_custom_script()` читает:

```text
Client Script
where dt = текущий DocType
and enabled = 1
```

---

## 120. Form scripts складываются в `__custom_js`

List scripts — в:

```text
__custom_list_js
```

---

## 121. Browser выполняет JavaScript

Form ScriptManager запускает custom JS через JavaScript runtime браузера.

То есть Client Script — не sandbox для бизнес-секретов.

---

## 122. При изменении Client Script Frappe очищает cache DocType

Controller `ClientScript` вызывает cache clear при:

```text
on_update
on_trash
```

Это нужно, чтобы обновлённая metadata дошла до клиента.

---

# Часть XXIX. Standard Form JS + Client Script

## 123. Они могут работать одновременно

Для standard DocType App может иметь:

```text
request.js
```

и Site дополнительно может иметь:

```text
Client Script
```

---

## 124. Form ScriptManager сначала получает standard code

В текущем v16 Form metadata содержит:

```text
__js
__custom_js
```

и standard form JS выполняется до custom Client Script.

---

## 125. `frappe.ui.form.on()` допускает несколько handlers одного event

ScriptManager хранит список обработчиков.

Поэтому standard и custom handlers могут оба слушать:

```text
refresh
validate
field change
```

---

## 126. Не рассчитывай, что Client Script автоматически «заменяет» standard handler

По умолчанию несколько handlers добавляются в цепочку.

Если задача требует глубокого override standard behavior, нужно очень внимательно проверить extension point — иногда это уже граница App code.

---

# Часть XXX. Нюанс DocType Layout в v16

## 127. Техническая деталь

Текущий `ScriptManager` v16 умеет добавлять `client_script` активного `DocType Layout` к standard JS.

При активном `doctype_layout` обычный `__custom_js` Client Script в этом участке загрузки не исполняется.

---

## 128. Что из этого запомнить новичку

Если на форме используется отдельный `DocType Layout` и Client Script внезапно не ведёт себя как обычная Form, нужно проверять именно layout-specific client script и текущую логику загрузки v16.

Для обычной Form без DocType Layout этот нюанс можно пока забыть.

---

# Часть XXXI. Client Script для List View

## 129. `Apply To = List`

Client Script может кастомизировать List View.

Синтаксис уже другой:

```javascript
frappe.listview_settings['Request'] = {
};
```

---

## 130. Пример

```javascript
frappe.listview_settings['Request'] = {
    add_fields: ['status', 'priority'],

    filters: [
        ['status', '=', 'Open']
    ],

    get_indicator(doc) {
        if (doc.priority === 'High') {
            return ['High', 'red', 'priority,=,High'];
        }
    }
};
```

---

## 131. `add_fields`

Просит List View дополнительно получить поля, которые нужны вашему JS.

Не считай, что arbitrary field автоматически присутствует в каждом list row object.

---

## 132. `filters`

Можно задать default List filters.

Например:

```javascript
filters: [
    ['status', '=', 'Open']
]
```

---

## 133. `get_indicator(doc)`

Позволяет динамически определить indicator List row.

---

## 134. `onload(listview)`

Срабатывает один раз перед загрузкой List.

---

## 135. `before_render()`

Вызывается перед рендером records.

---

## 136. Можно добавить row button

List API v16 документирует:

```text
button.show
button.get_label
button.get_description
button.action
```

---

## 137. Осторожно со страницей документации про multiple dropdown buttons

Текущая документация помечает отдельный пример multiple buttons как feature из `develop`.

Поэтому в курсе v16 не считаем этот конкретный расширенный dropdown API гарантированным stable-v16 контрактом без проверки исходного кода конкретной версии.

---

# Часть XXXII. Client Script Form против List Script

## 138. Form

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {}
});
```

---

## 139. List

```javascript
frappe.listview_settings['Request'] = {
    onload(listview) {}
};
```

---

## 140. Не смешивай API

`frm` относится к Form View.

В List Script основной объект другой:

```text
listview
```

---

# Часть XXXIII. Client Script и permissions

## 141. Client Script получает интерфейс пользователя

Если пользователь не имеет доступа к Document, Client Script не должен использоваться как способ этот доступ получить.

---

## 142. `frappe.call()` всё равно проходит server authentication/authorization

Browser может вызвать whitelisted method, но серверная сторона должна проверить:

```text
кто пользователь
есть ли нужная Role
есть ли permission на Document
допустимо ли состояние
```

---

## 143. Нельзя считать Form permission достаточным для произвольного RPC

Если кнопка вызывает:

```text
close_period()
```

серверный метод должен сам определять допустимость операции.

---

# Часть XXXIV. Что Client Script делает хорошо

## 144. Динамическая видимость

```text
show/hide
read only
mandatory
options
```

---

## 145. Реакция на поля

```text
если A изменилось
→ пересчитать B
```

---

## 146. Link filters

```text
ограничить варианты выбора
```

как UX-механизм.

---

## 147. Контекстные кнопки

```text
показать действие только в нужном состоянии
```

---

## 148. Простые клиентские расчёты

Например:

```text
qty × rate
```

для немедленного UI feedback.

Но authoritative result при необходимости должен подтверждаться сервером.

---

## 149. Небольшие автоматические заполнения

Например:

```text
выбрали тип
→ выставили default поля
```

---

# Часть XXXV. Что Client Script делает плохо

## 150. Security rules

Нельзя оставлять только здесь.

---

## 151. Сложная бизнес-логика

Например:

```text
расчёт финансового результата
закрытие периода
проведение документов
сложные state transitions
```

лучше держать на сервере.

---

## 152. Интеграционные secrets

Категорически не здесь.

---

## 153. Большая reusable codebase

Для этого App лучше.

---

## 154. Background processing

Browser не должен выполнять долгую надёжную задачу.

Используй server method + background job.

---

## 155. Cross-client rule

Если правило должно одинаково работать через:

```text
Desk
REST
import
scheduler
background job
Python code
```

оно должно быть server-side.

---

# Часть XXXVI. Частая ошибка: бизнес-статус через UI

## 156. Плохой вариант

```javascript
frm.add_custom_button('Approve', () => {
    frm.set_value('status', 'Approved');
    frm.save();
});
```

Если `Approved` — реальное бизнес-действие.

---

## 157. Почему плохо

Весь смысл операции сводится к тому, что Browser сам решил:

```text
status = Approved
```

---

## 158. Лучше

```javascript
frm.add_custom_button('Approve', async () => {
    await frappe.call({
        method: 'my_app.api.approve_request',
        args: {
            name: frm.doc.name
        }
    });

    await frm.reload_doc();
});
```

---

## 159. На сервере

```python
@frappe.whitelist(methods=['POST'])
def approve_request(name):
    doc = frappe.get_doc('Request', name)
    doc.check_permission('write')
    doc.approve()
```

Теперь Browser только инициирует команду.

---

# Часть XXXVII. Частая ошибка: hidden field как защита

## 160. Плохой вариант

```javascript
if (!frappe.user_roles.includes('Manager')) {
    frm.toggle_display('cost_price', false);
}
```

и считать цену защищённой.

---

## 161. Правильный механизм

Если поле действительно секретно:

```text
Permission Level
Role Permission
Data Masking
server-side response filtering
```

в зависимости от задачи.

Client Script может дополнительно улучшить UI, но не заменить permission model.

---

# Часть XXXVIII. Частая ошибка: слишком много server calls

## 162. Плохой вариант

```javascript
description(frm) {
    frappe.call(...);
}
```

если поле меняется часто и server response не нужен на каждое изменение.

---

## 163. Последствия

```text
лишняя latency
лишняя server load
race conditions
responses приходят не в том порядке
дёргающийся UI
```

---

## 164. Решение

Использовать:

```text
client calculation
явную кнопку
debounce
server validation при Save
```

в зависимости от задачи.

---

# Часть XXXIX. Race conditions

## 165. Async response может прийти позже нового значения

Представим:

```text
User выбрал Customer A
→ request A

сразу выбрал Customer B
→ request B
```

Если A ответит после B, старый response может перезаписать новый UI state.

---

## 166. Для сложных async interactions нужно проектировать stale-response protection

Например сравнивать значение, для которого отправлялся request, с текущим `frm.doc` перед применением результата.

Это уже сигнал, что UI перестаёт быть совсем простым.

---

# Часть XL. Browser debugging

## 167. Client Script отлаживается как JavaScript

Основные инструменты:

```text
Browser DevTools
Console
Network
Sources
```

---

## 168. `console.log`

```javascript
console.log(frm.doc);
```

нормален на этапе разработки.

В чистовой реализации бессмысленный debug noise лучше убрать.

---

## 169. Ошибки Client Script видны в browser console

Текущий ScriptManager v16 также показывает сообщение:

```text
Error in Client Script
```

если custom Form Script падает при setup execution.

---

## 170. Network tab особенно важен для `frappe.call()`

Там видно:

```text
URL
HTTP method
payload
status code
response
```

---

# Часть XLI. Перезагрузка после изменения Client Script

## 171. После Save Frappe очищает DocType cache

Но browser всё равно может держать уже загруженную Form metadata.

Если изменение не видно:

```text
перезагрузи Form / List
при необходимости hard refresh
```

и проверь, что Script:

```text
Enabled = 1
правильный DocType
правильный Apply To
```

---

# Часть XLII. Мини-практика 1 — mandatory по условию

## 172. Задача

Для `Request`:

```text
если Priority = High
→ Due Date обязательна
```

---

## 173. Script

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        frm.trigger('set_due_date_rules');
    },

    priority(frm) {
        frm.trigger('set_due_date_rules');
    },

    set_due_date_rules(frm) {
        frm.toggle_reqd(
            'due_date',
            frm.doc.priority === 'High'
        );
    }
});
```

---

## 174. Что здесь хорошо

Одна логика вызывается из двух мест:

```text
refresh
priority change
```

без копирования.

---

## 175. Чего здесь не хватает для строгого business rule

Server-side validation.

Client Script делает форму удобной, но API всё ещё может попытаться сохранить High без Due Date.

---

# Часть XLIII. Мини-практика 2 — Link query

## 176. Задача

Выбирать Contract только текущей Company.

---

## 177. Script

```javascript
frappe.ui.form.on('Request', {
    setup(frm) {
        frm.set_query('contract', () => {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
    }
});
```

---

## 178. Если Company меняется

Сам callback читает текущее:

```javascript
frm.doc.company
```

поэтому при открытии Link query получит актуальное значение.

Но если логика сложнее, нужно отдельно продумать очистку уже выбранного несовместимого Contract.

---

# Часть XLIV. Мини-практика 3 — Child Table amount

## 179. Поля child row

```text
qty
rate
amount
```

---

## 180. Script

```javascript
frappe.ui.form.on('Request Item', {
    qty(frm, cdt, cdn) {
        update_amount(cdt, cdn);
    },

    rate(frm, cdt, cdn) {
        update_amount(cdt, cdn);
    }
});

function update_amount(cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);

    frappe.model.set_value(
        cdt,
        cdn,
        'amount',
        (row.qty || 0) * (row.rate || 0)
    );
}
```

---

## 181. Для критического финансового расчёта

Такой client calculation может давать мгновенный preview.

Но authoritative calculation должен быть проверен сервером.

---

# Часть XLV. Мини-практика 4 — context action

## 182. Задача

Для сохранённого Open Request показать кнопку Close.

---

## 183. Client Script

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        if (frm.is_new() || frm.doc.status !== 'Open') {
            return;
        }

        frm.add_custom_button('Close', async () => {
            await frappe.call({
                method: 'my_app.api.close_request',
                args: {
                    name: frm.doc.name
                }
            });

            await frm.reload_doc();
        });
    }
});
```

---

## 184. Почему это хороший шаблон

```text
Client
→ решает, показывать ли кнопку

Server
→ решает, можно ли реально Close
```

---

# Часть XLVI. Мини-практика 5 — List indicator

## 185. List Client Script

```javascript
frappe.listview_settings['Request'] = {
    add_fields: ['priority'],

    get_indicator(doc) {
        if (doc.priority === 'High') {
            return ['High', 'red', 'priority,=,High'];
        }

        return ['Normal', 'blue'];
    }
};
```

---

## 186. Здесь нет `frm`

Потому что это List View, а не Form View.

---

# Часть XLVII. Когда Client Script уже пора переносить в App

## 187. Первый сигнал — логика нужна на нескольких Sites

```text
Site A
Site B
Site C
```

Если приходится копировать Script вручную, App становится естественнее.

---

## 188. Второй сигнал — нужен Git workflow

```text
branch
review
commit
test
release
rollback
```

Client Script в базе хуже подходит как основной source of truth большой codebase.

---

## 189. Третий сигнал — много server code

Если Client Script вызывает набор связанных Python methods, уже появляется полноценная application feature.

---

## 190. Четвёртый сигнал — нужны automated tests

Прототип:

```text
Client Script
```

Production feature:

```text
App code
+
tests
```

часто устойчивее.

---

## 191. Пятый сигнал — несколько Client Scripts начинают конфликтовать

Если становится непонятно:

```text
кто изменил поле
кто добавил кнопку
кто перезаписал query
в каком порядке всё запускается
```

это уже технический долг.

---

# Часть XLVIII. Client Script против Customize Form

## 192. Если настройка статическая — сначала Customize Form

Например:

```text
поле всегда hidden
поле всегда read-only
label всегда другой
section всегда collapsible
```

не обязательно писать JavaScript.

---

## 193. Client Script нужен для динамики

Например:

```text
если условие A
→ hidden
иначе visible
```

---

# Часть XLIX. Client Script против Fetch From

## 194. Если поле всегда можно получить из Link обычным Fetch From

Используй штатное:

```text
Fetch From
```

а не Client Script.

---

## 195. Client Script нужен, когда логика сложнее

Например:

```text
несколько условий
несколько источников
динамическая реакция
UI-only вычисление
```

---

# Часть L. Client Script против Workflow

## 196. Не программируй Workflow кнопками вручную без необходимости

Если задача:

```text
Draft → Review → Approved
```

и нужны роли/переходы,

сначала смотри штатный `Workflow`.

Client Script можно использовать для дополнительного UX вокруг Workflow, но не обязательно заменять его своей state machine.

---

# Часть LI. Client Script против Server Script

## 197. Client Script

```text
Browser
JavaScript
UI events
Form / List
```

---

## 198. Server Script

```text
Server
restricted Python environment
Document / API / scheduler events в зависимости от типа
```

---

## 199. Главное различие

```text
Client Script
→ удобство интерфейса

Server Script
→ server-side logic
```

Следующая глава целиком посвящена Server Script.

---

# Часть LII. Client Script против controller App

## 200. Controller

Это полноценный Python class DocType в App.

Он выполняется независимо от того, кто изменяет Document:

```text
Desk
REST
background job
Python code
```

---

## 201. Client Script

Работает только там, где реально загружен соответствующий browser UI.

Поэтому controller — место для authoritative Document behavior.

---

# Часть LIII. Decision table

## 202. Что выбирать

| Задача | Инструмент |
|---|---|
| Поле всегда hidden/read-only | Customize Form / DocField |
| Простая связанная подстановка | Fetch From |
| Динамически show/hide field | Client Script |
| Mandatory только в UI по условию | Client Script |
| Mandatory как правило данных | server-side validation / metadata |
| Ограничить Link choices в UI | `frm.set_query()` |
| Ограничить реальный доступ к данным | Permissions / server checks |
| Добавить Form button | Client Script / standard form JS |
| Кнопка запускает business command | Client Script → whitelisted server method |
| Рассчитать UI preview | Client Script |
| Authoritative расчёт | server code |
| Child Table UI reaction | Client Script |
| Customize List indicator | List Client Script |
| Логика только одного Site | Client Script подходит |
| Логика должна устанавливаться на много Sites | App JS |
| Большая feature с тестами | App code |
| Долгая задача | server method → background job |

---

# Часть LIV. Архитектурная лестница

## 203. Хороший порядок выбора

```text
можно решить свойством DocField?
→ DocType / Customize Form

можно решить Fetch From / Depends On?
→ штатная metadata

нужна небольшая динамика UI?
→ Client Script

нужна server validation / command?
→ Server Script или App code

нужно переносить между Sites и тестировать?
→ App
```

---

# Что нужно запомнить

1. `Client Script` — JavaScript, который выполняется в браузере пользователя.
2. В v16 Client Script имеет `Apply To = Form` или `List`.
3. Для Form используется `frappe.ui.form.on()`.
4. Для List используется `frappe.listview_settings[...]`.
5. `frm` — основной объект текущей Form.
6. Текущий клиентский Document находится в `frm.doc`.
7. Поле DocType можно слушать как event по его `fieldname`.
8. Основные Form events: `setup`, `onload`, `refresh`, `validate`, save/submit/cancel events.
9. `refresh` может выполняться многократно, поэтому handler должен быть безопасен для повторного запуска.
10. `frm.set_value()` меняет поле и запускает field change event.
11. `frm.set_value()` возвращает Promise.
12. Form ScriptManager v16 умеет ждать Promise из event handler.
13. `frm.set_df_property`, `toggle_display`, `toggle_reqd`, `toggle_enable` меняют runtime UI behavior.
14. Runtime UI property не является постоянной metadata DocField.
15. `frm.set_query()` ограничивает варианты Link в UI, но не заменяет permissions.
16. Child Table handlers получают `frm`, `cdt`, `cdn`.
17. Для child row можно использовать `frappe.get_doc(cdt, cdn)` и `frappe.model.set_value()`.
18. В v16 add/remove events также документированы для Table MultiSelect.
19. `frm.add_child()` добавляет Child row.
20. `frm.add_custom_button()` добавляет context action в Form.
21. Серьёзная бизнес-команда должна жить на сервере; Client Script только инициирует её.
22. `frappe.call()` вызывает whitelisted module method.
23. `frm.call()` вызывает whitelisted controller method текущего Document.
24. Client validation работает только в browser Form flow и может быть обойдена через другие interfaces.
25. Поэтому Client Script нельзя использовать как единственный источник критических business validations.
26. Client Script не является security layer.
27. Hidden/read-only UI не заменяет Role Permission, Permission Level и server checks.
28. Никогда не храни API Secret, пароль или другой секрет в Client Script.
29. В браузере код Client Script доступен пользователю.
30. Несколько enabled Client Scripts одного DocType могут выполняться одновременно.
31. Текущий v16 собирает их в порядке `creation asc`, но архитектуру лучше не строить вокруг скрытых взаимозависимостей между скриптами.
32. Standard `{doctype}.js` и site Client Script используют один и тот же Form API.
33. Standard JS нужен для переносимой App logic, Client Script — для site-specific customization.
34. Client Script может кастомизировать List View через `frappe.listview_settings`.
35. Поля, используемые List Script, при необходимости нужно добавить через `add_fields`.
36. Отдельный пример multiple dropdown buttons в текущей документации помечен как develop feature, поэтому не считаем его гарантированным API stable v16 без дополнительной проверки.
37. При активном DocType Layout текущая v16 логика загрузки имеет отдельный layout client script path; это важно при диагностике необычного поведения Client Script.
38. Если Client Script становится большим, shared, сложным и плохо тестируемым — его пора переносить в App.
39. Сначала используй штатную metadata, затем Client Script, затем server/app code — по мере необходимости.
40. Следующая глава — `Server Script`, то есть low-code логика уже на стороне сервера.

---

# Источники

Официальная документация Frappe Framework:

- [Client Script](https://docs.frappe.io/framework/user/en/desk/scripting/client-script)
- [Form Scripts / Form API](https://docs.frappe.io/framework/user/en/api/form)
- [List API](https://docs.frappe.io/framework/user/en/api/list)
- [Server Calls](https://docs.frappe.io/framework/user/en/api/server-calls)
- [REST API](https://docs.frappe.io/framework/user/en/api/rest)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)

Для поведения именно v16 дополнительно сверено с исходным кодом ветки `version-16`:

- [`frappe/custom/doctype/client_script/client_script.json`](https://github.com/frappe/frappe/blob/version-16/frappe/custom/doctype/client_script/client_script.json)
- [`frappe/custom/doctype/client_script/client_script.py`](https://github.com/frappe/frappe/blob/version-16/frappe/custom/doctype/client_script/client_script.py)
- [`frappe/desk/form/meta.py`](https://github.com/frappe/frappe/blob/version-16/frappe/desk/form/meta.py)
- [`frappe/public/js/frappe/form/script_manager.js`](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/script_manager.js)
- [`frappe/public/js/frappe/model/model.js`](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/model/model.js)

---

Следующая глава: **45. Server Script**.
