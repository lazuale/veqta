# 09. Single, Tree, Submittable и граница Virtual DocType

До этого мы создавали обычный `Request` и два Child DocType. Теперь нужны три другие модели данных, которые обычный DocType выражает плохо:

```text
одна общая настройка Site
иерархический справочник
документ, который можно официально Submit
```

Во Frappe для этого есть специальные режимы `Single`, `Tree` и `Submittable`.

`Virtual` тоже относится к специальным DocType, но его нельзя честно пройти как полноценную лабораторию без controller-кода. Поэтому в этой главе мы не будем изображать работу внешнего источника данных: вместо этого точно зафиксируем границу механизма и увидим одно реальное ограничение v16.

Проверено для **Frappe Framework v16.32.0** и исходного кода тега `v16.32.0`.

---

## Что уже есть на стенде

Главный объект:

```text
Request
```

Дополнительные Child DocTypes:

```text
Request Item
Request Watcher
```

В `Request` уже есть:

```text
Items     → Table → Request Item
Watchers  → Table MultiSelect → Request Watcher
```

Теперь новые объекты вводятся только потому, что специальные режимы невозможно нормально показать на обычном `Request`, не ломая его смысл.

---

# Single

## Какую задачу решает Single

Представим общую настройку учебного App:

```text
Default Priority
Course Note
```

Нам не нужны записи:

```text
Training Settings 1
Training Settings 2
Training Settings 3
```

На всём Site должна быть одна форма текущих настроек.

Для этого создадим:

```text
Training Settings
Is Single = включено
```

---

## Чем Single отличается от обычного DocType

Обычный `Request` имеет много Documents:

```text
REQ-2026-00001
REQ-2026-00002
REQ-2026-00003
```

Single имеет один экземпляр по смыслу самого DocType:

```text
Training Settings
```

У него нет обычной рабочей модели «список → открыть одну из многих записей».

В Frappe значения Single хранятся иначе, через общую таблицу `tabSingles`.

Ученик пока не работает с SQL; важно только наблюдаемое следствие:

```text
Single
→ одна форма настроек на Site
```

---

## Что создадим в `Training Settings`

```text
Default Priority
  fieldname: default_priority
  type: Select
  options: Low / Medium / High

Course Note
  fieldname: course_note
  type: Small Text
```

Эти настройки пока ни на что автоматически не влияют. Мы не будем добавлять скрытую автоматизацию только ради того, чтобы поле выглядело «полезнее».

Задача главы — понять модель Single.

---

# Tree

## Когда нужен Tree

Некоторые Documents образуют настоящую иерархию:

```text
Operations
├── Internal
└── External

Analytics
```

Для такого справочника создадим:

```text
Training Category
Is Tree = включено
```

Каждая категория остаётся самостоятельным Document, но может иметь родителя.

---

## Tree — не просто картинка

В `v16.32.0` при включённом `Is Tree` Frappe использует Nested Set model и добавляет служебные поля, включая:

```text
lft
rgt
is_group
old_parent
parent_training_category
```

`parent_training_category` становится Parent Field для нашего `Training Category`.

Эти поля нужны Framework для поддержания иерархии.

Вручную считать `lft` и `rgt` не нужно.

Практически ученик увидит другое:

```text
создали корневые категории
→ добавили дочерние
→ изменили Parent Training Category
→ узел переместился в дереве
```

---

## `Is Group`

В Tree один узел может быть группой, внутри которой создаются дочерние элементы.

Для нашей структуры:

```text
Operations  → Is Group
Analytics   → Is Group
Internal    → обычный дочерний узел
External    → обычный дочерний узел
```

Это позволит реально увидеть родительскую иерархию, а не только флаг `Is Tree` в metadata.

---

## Naming для `Training Category`

Категории будут иметь короткие уникальные названия:

```text
Operations
Analytics
Internal
External
```

Поэтому здесь разумно использовать:

```text
Auto Name = field:category_name
Title Field = category_name
```

Это другой реальный способ naming, который мы уже можем понять после главы 06.

Frappe будет использовать значение поля `category_name` как `name` Category Document.

---

# Submittable

## Когда обычного Save недостаточно

`Request` — рабочий объект: его статус меняется по ходу работы, но он не обязан проходить системный Submit.

Для другого типа документа может быть нужен смысл:

> черновик подготовлен и официально подтверждён; после этого его нельзя свободно переписывать.

Для этого существует:

```text
Is Submittable
```

Создадим отдельный DocType:

```text
Approval Record
```

и в следующей главе полностью пройдём его lifecycle.

---

## Что меняет Submittable

У такого Document появляется системное поле состояния:

```text
docstatus
```

Основная последовательность:

```text
Draft
  ↓ Submit
Submitted
  ↓ Cancel
Cancelled
```

В этой главе мы пока создадим только Draft и убедимся, что действие Submit действительно появилось.

Полный смысл `docstatus`, Cancel, Amend и `Allow on Submit` — ответственность главы 10.

---

## `amended_from`

В исходном коде `v16.32.0` при включённом `Is Submittable` Frappe автоматически добавляет поле:

```text
Amended From
fieldname: amended_from
Link → этот же DocType
```

В главе 10 это поле станет наблюдаемой связью между отменённым документом и его исправленной версией.

Сейчас вручную его не создаём.

---

# Virtual DocType

## Что меняет Virtual

Обычный DocType хранит свои данные обычным способом Frappe.

Virtual DocType используется, когда Document-интерфейс нужен, но источник данных должен быть реализован кодом, например поверх другого хранилища.

Схема:

```text
Frappe Document interface
        ↓
Virtual DocType controller
        ↓
нестандартный источник данных
```

Framework не может сам угадать, как читать и сохранять такие записи. Нужны методы controller.

---

## Почему не создаём рабочий Virtual сейчас

Код App, controller и Python ещё не изучены.

Если сейчас вставить готовый controller, ученик просто скопирует неизвестный код ради галочки. Это нарушит последовательность курса.

Поэтому полноценный Virtual DocType будет иметь смысл только после знакомства с application code.

Но одну важную границу мы можем проверить уже сейчас.

В `v16.32.0` исходный код прямо запрещает:

```text
Custom Virtual DocType
```

То есть Virtual — не site-only low-code объект, для которого достаточно поставить `Custom?`.

В лабораторной мы намеренно попробуем сохранить такой неправильный вариант и получим гарантированный отказ Framework. После этого форма будет закрыта без создания DocType.

---

## Четыре режима в одной таблице

| Режим | Что меняется | Объект курса |
|---|---|---|
| `Single` | экземпляр один на Site | `Training Settings` |
| `Tree` | Documents образуют иерархию | `Training Category` |
| `Submittable` | появляется системный lifecycle Submit/Cancel | `Approval Record` |
| `Virtual` | обычное хранение заменяет controller-defined источник | только граница механизма сейчас |

Они не являются «улучшенными версиями» обычного DocType. Каждый решает отдельную задачу.

---

## Что произойдёт в лабораторной

Ты:

1. создашь `Training Settings` как Single и убедишься, что это одна форма;
2. сохранишь в ней значения и снова откроешь их;
3. создашь `Training Category` как Tree;
4. построишь иерархию `Operations / Analytics / Internal / External`;
5. изменишь родителя `External` и увидишь перемещение узла;
6. создашь `Approval Record` как Submittable;
7. сохранишь один Draft, но не Submit его;
8. увидишь доступное действие Submit;
9. намеренно попробуешь сохранить `Custom Virtual DocType` и получишь штатный отказ;
10. не оставишь после этой ошибки никакого временного Virtual DocType.

---

## Что запомнить

1. `Single` — одна конфигурация на Site, а не список множества Documents.
2. `Tree` — настоящая иерархия с поддержкой Nested Set, а не просто красивый View.
3. `Submittable` добавляет системный lifecycle `docstatus`.
4. `Virtual` меняет способ получения/хранения данных и требует controller-кода.
5. В `v16.32.0` Custom Virtual DocType запрещён.
6. Специальный режим выбирается по смыслу данных; `Request` не переделываем в Single/Tree/Submittable только ради демонстрации флага.

---

## Официальные источники

- [Single DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype)
- [Tree View](https://docs.frappe.io/framework/user/en/api/tree)
- [Virtual DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype)
- [DocType validation — Single, Virtual, Tree, Submittable; v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py)

Теперь выполни [**лабораторную 09**](labs/09_SPECIAL_DOCTYPES_LAB.md).

После неё переходи к [**10. `docstatus`, Submit, Cancel и Amendment**](10_DOCSTATUS_LIFECYCLE.md).