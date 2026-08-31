# 19. Permission Level

В главе 18 мы настроили доступ к `Request` целиком:

```text
Training User
→ Read + Create + Write

Training Manager
→ Read + Create + Write + Delete + Share
```

Теперь нужен другой уровень вопроса:

> может ли пользователь открыть Request, но не видеть отдельное внутреннее поле?

Для этого во Frappe есть **Permission Level**, или `Perm Level`.

Проверено для **Frappe Framework v16.32.0**.

---

## Главная идея

У обычного DocField есть свойство:

```text
Perm Level
```

По умолчанию:

```text
0
```

Большинство полей `Request` сейчас находятся на Level 0.

В этой главе добавим:

```text
Internal Cost
fieldname = internal_cost
Currency
Perm Level = 1
```

И получим:

```text
Training User
→ Request доступен
→ Level 1 не разрешён
→ Internal Cost не доступен

Training Manager
→ Request доступен
→ Level 1 Read + Write
→ Internal Cost виден и редактируется
```

---

# Level 0 и Level 1 — не разные документы

Это всё тот же:

```text
Request
```

Permission Level не создаёт второй DocType и не делит запись на две физические части.

Он группирует поля по уровню доступа.

Пример:

```text
Request
├── subject        Level 0
├── status         Level 0
├── priority       Level 0
├── notes          Level 0
└── internal_cost  Level 1
```

---

## Level 0 остаётся базой

Пользователь сначала должен иметь базовый доступ к самому `Request`.

То есть Level 1 не работает как самостоятельный «пропуск к одному полю при отсутствии документа».

Практическая модель курса:

```text
Level 0
→ можно ли нормально работать с Request

Level 1
→ доступно ли поле internal_cost внутри уже доступного Request
```

---

# Где задаётся Perm Level поля

Наш `Request` — собственный Standard DocType App `training`.

Поэтому постоянное поле этой главы добавляем **прямо в Standard metadata `Request`**, а не через Customize Form.

Получится изменение файла:

```text
apps/training/training/training/doctype/request/request.json
```

Это принципиально отличается от главы 15:

```text
Customize Form
→ site customization

редактирование собственного Standard DocType в Developer Mode
→ metadata App
```

---

# Где задаются права Level 1

В том же:

```text
Role Permissions Manager
```

можно добавить rule:

```text
Document Type: Request
Role: Training Manager
Permission Level: 1
```

В UI `v16.32.0` для уровней выше 0 показываются только field-level права:

```text
Read
Write
Mask
```

Там нет смысла выдавать:

```text
Create
Delete
Share
Import
Export
```

потому что эти действия относятся к Document целиком, а не к отдельному полю.

---

# Три состояния поля

Для пользователя поле высокого уровня практически может оказаться в одном из трёх состояний.

## 1. Read + Write

```text
Level 1
Read  ✓
Write ✓
```

Поле доступно и может редактироваться, если другие свойства документа не накладывают дополнительное ограничение.

Так будет у `Training Manager`.

---

## 2. Только Read

```text
Level 1
Read  ✓
Write ☐
```

Поле видно, но редактировать его нельзя.

Это временно проверим на `Training User`.

---

## 3. Нет Level 1 rule

```text
Read  нет
Write нет
```

Пользователь не получает обычного доступа к полю этого уровня.

Это будет финальным состоянием `Training User`.

---

# Permission Level — не `Hidden`

Эти механизмы нельзя путать.

```text
Hidden
→ metadata интерфейса

Perm Level
→ permission model
```

Если сделать чувствительное поле:

```text
Hidden = 1
Perm Level = 0
```

это не превращает его в защищённое поле для одной роли.

`Hidden` говорит форме не показывать control обычным способом.

А `Perm Level` участвует в permission-aware обработке полей Framework.

---

# Permission Level — не только CSS

В текущем `v16.32.0` permission-aware query engine получает список разрешённых полей и фильтрует выбираемые fields по Perm Level пользователя.

То есть идея не сводится к:

```text
браузер просто спрятал input
```

Framework учитывает доступ к полям и на серверной стороне стандартных permission-aware путей.

Это именно security boundary Framework, а не косметика формы.

---

## Но custom server code всё равно должен уважать permissions

Frappe — framework.

Разработчик может написать доверенный серверный код, который сознательно обходит обычные permission checks.

Поэтому нельзя делать ложный вывод:

> Perm Level физически шифрует данные и любой Python-код никогда их не увидит.

Правильнее:

```text
штатные permission-aware механизмы
→ учитывают Perm Level

код, сознательно обходящий permission engine
→ ответственность разработчика
```

Server-side код подробно будет позже.

---

# Read Only тоже не заменяет Perm Level

Поле:

```text
Read Only = 1
```

говорит, что его нельзя редактировать через обычное поведение поля.

Но это не модель:

```text
Manager видит
User не видит
```

Для разного доступа разных Roles используем permission levels.

---

# Несколько ограничений работают вместе

Даже если Role имеет:

```text
Level 1 Read + Write
```

поле ещё может быть ограничено свойствами и состоянием документа:

```text
Read Only
Set Only Once
docstatus
Allow on Submit
Workflow
Depends On
```

Permission отвечает на вопрос:

```text
какой максимум разрешён пользователю?
```

Другие правила могут дополнительно этот максимум уменьшить.

---

# Почему экспериментируем на известном Document

Из главы 18 у нас уже есть:

```text
D18-Manager-Record
owner = student.manager@example.test
```

На нём менеджер запишет:

```text
Internal Cost = 1250
```

После этого обычный User откроет **тот же Document**.

Так сравнение не зависит от разных данных.

---

# Контролируемая утечка доступа

Лаборатория сначала даст `Training User` временно только:

```text
Level 1 Read
```

и мы увидим read-only поле.

Затем намеренно включим ему:

```text
Level 1 Write
```

Обычный User получит право изменить Internal Cost.

Это будет неправильная для нашей модели настройка — и наглядное доказательство, что permission row действительно влияет на доступ.

После опыта:

```text
Training User Level 1 rule
→ полностью удаляется

Internal Cost
→ возвращается к 1250
```

---

# Что произойдёт в лабораторной

Ты:

1. добавишь Standard field `internal_cost` в `Request`;
2. задашь ему `Perm Level = 1`;
3. создашь Level 1 rule `Training Manager: Read + Write`;
4. запишешь `1250` в известный Request;
5. увидишь, что Training User этого поля не получает;
6. временно добавишь Training User Level 1 Read;
7. увидишь поле только для чтения;
8. намеренно добавишь Write и изменишь значение;
9. восстановишь `1250`;
10. полностью удалишь Training User Level 1 rule.

---

# Что запомнить

1. Level 0 — базовые document permissions.
2. Level 1+ используются для групп полей с другой политикой доступа.
3. На Level 1+ Role Permissions Manager показывает Read/Write/Mask.
4. `Hidden` и `Read Only` не заменяют permission model.
5. Permission Level учитывается permission-aware серверными механизмами.
6. Для собственного Standard DocType постоянный `Perm Level` хранится в metadata App.
7. В финале `Internal Cost` доступен только `Training Manager`.

---

## Проверенные исходники v16.32.0

- [Role Permissions Manager UI](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/page/permission_manager/permission_manager.js)
- [Custom DocPerm metadata](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/custom_docperm/custom_docperm.json)
- [Query permission handling](https://github.com/frappe/frappe/blob/v16.32.0/frappe/database/query.py)
- [Permission engine](https://github.com/frappe/frappe/blob/v16.32.0/frappe/permissions.py)

Теперь выполни [**лабораторную 19**](labs/19_PERMISSION_LEVEL_LAB.md).

После неё переходи к [**20. User Permission**](20_USER_PERMISSION.md).
