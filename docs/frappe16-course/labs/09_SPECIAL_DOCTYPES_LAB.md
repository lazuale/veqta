# Лабораторная 09. Single, Tree, Submittable и граница Virtual DocType

## Что уже должно быть готово

Лабораторная 08 завершена.

Главный DocType:

```text
Request
```

Child DocTypes:

```text
Request Item
Request Watcher
```

В `Request` есть:

```text
Items     Table → Request Item
Watchers  Table MultiSelect → Request Watcher
```

Есть рабочие Request Documents. Ничего из предыдущего состояния не удаляем.

---

## Что сейчас получим

После лабораторной останутся три новых Standard DocType:

```text
Training Settings   → Single
Training Category   → Tree
Approval Record     → Submittable
```

Также будет проверена граница Virtual DocType без создания постоянного Virtual-объекта.

---

# Часть A. Single — `Training Settings`

## 1. Создай Single DocType

Открой:

```text
DocType
→ New
```

Создай:

```text
Name:      Training Settings
Module:    Training
Is Single: включено
Custom?:   выключено
```

Добавь поля.

### Default Priority

```text
Label:      Default Priority
Fieldname:  default_priority
Field Type: Select
Options:
Low
Medium
High
Default:    Medium
```

### Course Note

```text
Label:      Course Note
Fieldname:  course_note
Field Type: Small Text
```

Сохрани DocType.

---

## 2. Открой `Training Settings`

Через поиск Desk найди:

```text
Training Settings
```

Открой форму.

Обрати внимание: это не обычный List View с кнопкой создания множества Documents.

Перед тобой одна форма настроек.

Заполни:

```text
Default Priority: Medium
Course Note: Block B settings
```

Нажми Save.

---

## 3. Проверь постоянство Single

Перейди на другой экран Desk, затем снова открой:

```text
Training Settings
```

Ожидается:

```text
Default Priority = Medium
Course Note = Block B settings
```

Но второй отдельный `Training Settings` Document создавать не нужно и обычного списка множества настроек нет.

Наблюдение:

```text
Single
→ один экземпляр настроек на Site
```

---

# Часть B. Tree — `Training Category`

## 4. Создай Tree DocType

Открой:

```text
DocType
→ New
```

Создай:

```text
Name:    Training Category
Module:  Training
Is Tree: включено
Custom?: выключено
```

Добавь поле:

```text
Label:      Category Name
Fieldname:  category_name
Field Type: Data
Mandatory:  включено
```

В Naming укажи:

```text
Auto Name:   field:category_name
Title Field: category_name
```

Сохрани DocType.

Frappe должен автоматически подготовить служебные поля Tree, включая:

```text
Parent Training Category
Is Group
```

Не создавай их вручную второй раз.

---

## 5. Создай корневую группу `Operations`

Открой `Training Category` и создай:

```text
Category Name: Operations
Is Group:      включено
Parent Training Category: пусто
```

Сохрани.

Так как Auto Name берётся из `category_name`, системный `name` будет:

```text
Operations
```

---

## 6. Создай корневую группу `Analytics`

Создай:

```text
Category Name: Analytics
Is Group:      включено
Parent Training Category: пусто
```

Сохрани.

---

## 7. Создай дочернюю категорию `Internal`

Создай:

```text
Category Name: Internal
Is Group:      выключено
Parent Training Category: Operations
```

Сохрани.

---

## 8. Создай дочернюю категорию `External`

Создай:

```text
Category Name: External
Is Group:      выключено
Parent Training Category: Operations
```

Сохрани.

---

## 9. Посмотри Tree View

Открой Tree View `Training Category`.

Должна получиться структура:

```text
Operations
├── Internal
└── External

Analytics
```

Если узлы свернуты, раскрой `Operations`.

---

## Эксперимент — перенеси узел

Открой Document:

```text
External
```

Измени только:

```text
Parent Training Category:
Operations → Analytics
```

Сохрани.

Вернись в Tree View.

Ожидается:

```text
Operations
└── Internal

Analytics
└── External
```

Мы изменили родителя одного Document, а Framework перестроил иерархию Tree.

---

# Часть C. Submittable — `Approval Record`

## 10. Создай Submittable DocType

Открой:

```text
DocType
→ New
```

Создай:

```text
Name:           Approval Record
Module:         Training
Is Submittable: включено
Custom?:        выключено
```

Добавь поле:

```text
Label:      Subject
Fieldname:  subject
Field Type: Data
Mandatory:  включено
```

В Naming укажи:

```text
Auto Name:   APR-.YYYY.-.#####
Title Field: subject
```

Сохрани DocType.

После сохранения Frappe должен автоматически иметь служебное поле:

```text
Amended From
fieldname: amended_from
```

Его вручную не добавляй.

---

## 11. Создай первый Draft

Открой `Approval Record` и создай:

```text
Subject: Первый черновик Approval Record
```

Нажми Save.

На свежем стенде имя будет вида:

```text
APR-2026-00001
```

Но **Submit пока не нажимай**.

Убедись, что у сохранённого документа доступно действие:

```text
Submit
```

Это всё, что сейчас нужно от Submittable. Полный lifecycle будет в следующей лабораторной.

---

# Часть D. Намеренная ошибка — Custom Virtual DocType

Теперь проверим реальное ограничение `v16.32.0`.

## 12. Начни создавать временный DocType

Открой:

```text
DocType
→ New
```

Введи:

```text
Name:       Temporary Virtual Test
Module:     Training
Custom?:    включено
Is Virtual: включено
```

Добавь простое поле:

```text
Label:      Title
Fieldname:  title
Field Type: Data
```

Нажми Save.

---

## Ожидаемая ошибка

Frappe `v16.32.0` должен отказать в создании такого DocType.

Смысл сообщения:

```text
Custom Virtual DocType создавать нельзя
```

Это не случайная ошибка формы.

Исходный код Framework явно проверяет сочетание:

```text
is_virtual + custom
```

и запрещает его.

Причина учебной границы:

```text
Virtual DocType
→ требует developer-level реализации controller
→ не является обычной site-only Custom metadata
```

---

## Восстановление

После ошибки **не исправляй** временный DocType и не создавай Standard Virtual «в обход».

Закрой несохранённую форму.

Через список `DocType` убедись, что:

```text
Temporary Virtual Test
```

не создан.

Постоянное состояние стенда должно содержать только три специальных объекта этой лабораторной:

```text
Training Settings
Training Category
Approval Record
```

---

## Проверь результат

Должно быть доказано руками:

```text
Training Settings
→ одна форма, значения сохранились

Training Category
→ иерархия с родителями реально работает

Approval Record
→ сохранённый Draft имеет действие Submit

Temporary Virtual Test
→ не создан, потому что Custom Virtual запрещён
```

---

## Проверка себя

Ответь без подсказки.

1. Почему `Training Settings` сделан Single?
2. Можно ли создать второй независимый экземпляр тех же Single-настроек обычным способом?
3. Какое поле связывает `External` с его текущим родителем в Tree?
4. Что произошло после изменения родителя `External`?
5. Почему `Approval Record` сделан Submittable, а основной `Request` пока нет?
6. Что означает появившееся действие Submit?
7. Почему мы не написали Virtual controller прямо сейчас?
8. Какое сочетание настроек намеренно вызвало ошибку Virtual?

---

## Состояние стенда после лабораторной

Оставляем:

### `Training Settings`

```text
Is Single: 1
Default Priority = Medium
Course Note = Block B settings
```

### `Training Category`

```text
Is Tree: 1
Auto Name: field:category_name
Title Field: category_name
```

Documents:

```text
Operations  Is Group = 1
└── Internal

Analytics   Is Group = 1
└── External
```

То есть после эксперимента:

```text
Internal.parent_training_category = Operations
External.parent_training_category = Analytics
```

### `Approval Record`

```text
Is Submittable: 1
Auto Name: APR-.YYYY.-.#####
Title Field: subject
Subject field: Mandatory
amended_from: добавлено Framework
```

Есть минимум один сохранённый Draft:

```text
APR-2026-00001
Subject = Первый черновик Approval Record
```

Он **не Submitted**.

### Virtual

```text
Temporary Virtual Test отсутствует
```

Это точное входное состояние [**главы 10**](../10_DOCSTATUS_LIFECYCLE.md).