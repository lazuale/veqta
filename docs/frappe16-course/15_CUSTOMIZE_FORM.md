# 15. Customize Form: site customization поверх Standard DocType

До этой главы мы меняли `Request` как Standard DocType нашего App `training`. При Developer Mode такие изменения попадали в metadata-файл приложения.

Теперь проверим **другой механизм**: изменение формы только на конкретном Site через `Customize Form`.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

`Request` — Standard DocType приложения `training`.

Его основной metadata-файл:

```text
apps/training/training/training/doctype/request/request.json
```

Он уже содержит изменения предыдущих глав:

```text
поля
layout
Start Date / End Date
Is Calendar and Gantt
```

В этой главе мы **не редактируем этот файл** через Standard DocType.

---

## Зачем нужен Customize Form

Представь один App, установленный на двух Sites:

```text
training App
└── Standard Request

Site A
→ нужно дополнительное локальное поле

Site B
→ это поле не нужно
```

Если менять `request.json`, изменение становится частью самого App.

Если использовать `Customize Form`, Frappe хранит переопределение отдельно на Site.

Модель:

```text
Standard Request metadata из App
            +
site customization
            ↓
итоговая metadata Request на этом Site
```

---

## Два главных объекта customization

Для первого прохода достаточно двух механизмов:

```text
Custom Field
Property Setter
```

### Custom Field

Используется, когда на Site добавляется **новое поле**.

Например:

```text
Local Note
custom_local_note
Small Text
```

Это поле не добавляется как строка `DocField` в `request.json`.

Frappe создаёт отдельный Document `Custom Field`.

В `v16.32.0` его `name` формируется так:

```text
<DocType>-<fieldname>
```

Поэтому наш объект будет:

```text
Request-custom_local_note
```

---

## Почему у Custom Field появляется `custom_`

Если fieldname не задан вручную, `Custom Field` v16 формирует его из Label и добавляет префикс:

```text
custom_
```

В курсе задаём fieldname явно:

```text
custom_local_note
```

Так на всех стендах получается одно и то же техническое имя.

---

## Property Setter

Если поле уже существует в Standard DocType, но на Site нужно изменить одно его свойство, Frappe создаёт `Property Setter`.

Например, у существующего поля:

```text
Estimate Hours
fieldname = estimate_hours
```

мы изменим только Description:

```text
Local customization from chapter 15
```

Исходный `DocField` остаётся в `request.json`.

Отдельный Property Setter говорит Site:

```text
для Request.estimate_hours
property = description
использовать локальное значение
```

В v16 его имя строится как:

```text
<DocType>-<field>-<property>
```

В нашем опыте:

```text
Request-estimate_hours-description
```

---

## Почему меняем именно Description

Можно было локально поменять Label, Mandatory или расположение поля.

Но нам важно сохранить стабильную учебную модель для следующих глав.

Поэтому выбираем безобидное свойство:

```text
Description
```

Пользователь увидит локальную подсказку, но:

```text
fieldname не меняется
тип поля не меняется
данные не меняются
layout не ломается
```

---

## Как доказать, что `request.json` не изменился

Старый вариант курса предлагал:

```bash
git status
```

Это слабая проверка: App уже менялся во многих предыдущих лабораторных, поэтому `git status` может показывать другие файлы и ничего не доказывает про конкретный `request.json`.

Правильная проверка в нашей лаборатории:

```bash
sha256sum apps/training/training/training/doctype/request/request.json
```

Делаем checksum **до** Customize Form и **после**.

Если хэши одинаковы, содержимое конкретного файла не изменилось.

При этом Form View изменился — значит слой customization пришёл не из `request.json`.

---

## Что происходит с базой данных

`Custom Field` — не только декоративный элемент формы.

Для обычного сохраняемого поля Frappe обновляет схему DocType так, чтобы новое значение можно было хранить у `Request` Documents.

То есть:

```text
Custom Field metadata
→ входит в итоговую metadata Request
→ поле появляется на форме
→ значение сохраняется для Request
```

Но источник этой настройки остаётся site-level customization.

---

## Customize Form и Standard DocType — два разных маршрута

Для нашего курса:

```text
нужно изменить базовую модель App training
→ редактируем Standard DocType Request
→ request.json меняется

нужно локальное отличие learn.localhost
→ Customize Form
→ Custom Field / Property Setter
```

Это различие станет особенно важным позже, когда дойдём до переноса настроек между Sites.

Пока перенос не изучаем.

---

## Что не делаем в этой главе

Не используем:

```text
Fixtures
Export Customizations
migrations
patches
Python
Client Script
```

Сначала нужно увидеть сам факт существования двух слоёв metadata.

---

## Намеренная ошибка

В лабораторной временно добавим ещё один Custom Field:

```text
Chapter 15 Required Test
custom_ch15_required_test
Data
Mandatory
```

После этого новый Request без этого поля гарантированно не сохранится.

Затем поле полностью удалим через `Customize Form` и проверим, что обычное создание Request восстановилось.

Это показывает: site customization реально участвует в validation, а не только рисует поле.

---

## Каноническое состояние после главы

Оставляем только два постоянных локальных изменения:

```text
Custom Field:
Request-custom_local_note

Property Setter:
Request-estimate_hours-description
```

Временный Mandatory Custom Field удаляется.

`request.json` должен иметь тот же SHA-256 до и после лабораторной.

---

## Что произойдёт в лабораторной

Ты:

1. снимешь SHA-256 `request.json`;
2. через Customize Form добавишь `custom_local_note`;
3. сохранишь значение этого поля в реальном Request;
4. найдёшь точный Document `Custom Field`;
5. изменишь Description `estimate_hours`;
6. найдёшь точный `Property Setter`;
7. создашь временный Mandatory Custom Field и получишь отказ Save;
8. удалишь его и проверишь восстановление;
9. снова снимешь SHA-256 и сравнишь с первым.

---

## Что запомнить

1. Standard metadata App и site customization — разные слои.
2. Новое локальное поле создаётся как `Custom Field`.
3. Изменение свойства Standard field хранится через `Property Setter`.
4. Customize Form может реально менять поведение сохранения Document.
5. `git status` не доказывает неизменность конкретного файла; checksum конкретного `request.json` — доказывает.
6. Перенос customizations — отдельная тема и сейчас не нужен.

---

## Официальные источники и исходный код v16.32.0

- [Customize Form](https://docs.frappe.io/framework/user/en/customize-form)
- [Custom Field source](https://github.com/frappe/frappe/blob/v16.32.0/frappe/custom/doctype/custom_field/custom_field.py)
- [Property Setter source](https://github.com/frappe/frappe/blob/v16.32.0/frappe/custom/doctype/property_setter/property_setter.py)
- [Customize Form source](https://github.com/frappe/frappe/blob/v16.32.0/frappe/custom/doctype/customize_form/customize_form.py)

Теперь выполни [**лабораторную 15**](labs/15_CUSTOMIZE_FORM_LAB.md).

После неё переходи к [**16. Desk Page и границы штатного интерфейса**](16_DESK_PAGE_AND_UI_BOUNDARIES.md).
