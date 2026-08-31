# Лабораторная 03. Framework против Apps

## Что уже должно быть готово

Лабораторная 02 завершена и восстановлена.

Стенд:

```text
Bench:          ~/frappe/frappe16-course-bench
Site:           learn.localhost
Apps installed: frappe, training
Module:         Training
Developer Mode: включён
User:           Administrator
Request:        ещё не создан
```

В первом терминале работает:

```bash
cd ~/frappe/frappe16-course-bench
bench start
```

Все команды ниже выполняй во втором терминале Debian из каталога Bench.

---

## Что сейчас получим

Ты проверишь руками три разных факта:

```text
какой код Apps лежит в Bench
→ apps/

какие Apps установлены на Site
→ bench --site ... list-apps

какие системные объекты доступны без ERPNext
→ Desk
```

После лабораторной стенд должен остаться без изменений.

---

## Сделай руками

### 1. Перейди в Bench

```bash
cd ~/frappe/frappe16-course-bench
pwd
```

---

### 2. Посмотри Apps на диске

```bash
ls -1 apps
```

Ожидаются как минимум:

```text
frappe
training
```

Проверь отдельно, что каталога ERPNext нет:

```bash
test -d apps/erpnext && echo "ERPNext code exists" || echo "ERPNext code is absent"
```

На нашем учебном стенде ожидается:

```text
ERPNext code is absent
```

---

### 3. Посмотри Apps конкретного Site

```bash
bench --site learn.localhost list-apps
```

Ожидаются:

```text
frappe
training
```

ERPNext в этом списке быть не должен.

Теперь у тебя есть два наблюдения:

```text
apps/erpnext отсутствует
+
erpnext не установлен на learn.localhost
```

---

### 4. Убедись, что сам Framework уже даёт рабочие системные объекты

В браузере открой:

```text
http://learn.localhost:8000/app
```

Через поиск Desk последовательно найди и открой:

```text
User
Role
DocType
Workspace
```

Не редактируй их.

Цель этого шага — увидеть, что эти объекты и экраны уже работают на Site, где установлены только:

```text
frappe
training
```

Причём `training` пока не содержит наших собственных DocTypes.

---

### 5. Проверь отсутствие предметного ERPNext DocType

В поиске Desk введи:

```text
Sales Invoice
```

На чистом стенде курса этот ERPNext DocType не должен быть доступен как установленный рабочий DocType.

Это не проблема установки Frappe.

Это ожидаемая граница:

```text
DocType как механизм
→ Framework

Sales Invoice как конкретная ERP-сущность
→ ERPNext App
```

---

### 6. Сравни `frappe` и наше App только на уровне структуры

В терминале выполни:

```bash
find apps/training -maxdepth 3 -type d | sort
```

Затем:

```bash
find apps/frappe/frappe -maxdepth 1 -mindepth 1 -type d | sort | head -30
```

Не разбирай сейчас внутренности каталогов Framework.

Нужно увидеть только разницу масштаба:

```text
frappe
→ большой Framework App

training
→ небольшой учебный App, который мы будем наполнять сами
```

---

## Проверь результат

К этому моменту должно быть доказано руками:

```text
1. В Bench есть frappe и training.
2. На learn.localhost установлены frappe и training.
3. ERPNext code в apps/ отсутствует.
4. ERPNext не установлен на Site.
5. User, Role, DocType и Workspace работают без ERPNext.
6. Sales Invoice на этом чистом стенде отсутствует.
```

---

## Эксперимент

Сравни два объекта в Desk:

```text
User
Sales Invoice
```

Для `User` ты можешь открыть реальный List View.

Для `Sales Invoice` на нашем стенде такого рабочего DocType нет.

Изменилось только одно условие — принадлежность объекта:

```text
User
→ поставляется Framework

Sales Invoice
→ поставляется отдельным ERPNext App
```

Ничего не устанавливай и не создавай.

---

## Намеренная ошибка

Теперь намеренно попроси Site установить App, которого нет в Bench:

```bash
cd ~/frappe/frappe16-course-bench
bench --site learn.localhost install-app erpnext
```

Ожидаемый результат:

```text
команда завершается ошибкой
→ ERPNext не устанавливается
→ причина связана с тем, что App erpnext отсутствует среди доступного кода Bench
```

Точный текст исключения может различаться, но команда **не должна успешно установить ERPNext**, потому что `install-app` не скачивает отсутствующий App автоматически.

Это контролируемая ошибка. Не выполняй `bench get-app erpnext`: загрузка ERPNext не является задачей этого курса.

---

## Восстановление

Ошибка установки не должна была изменить рабочий состав Site.

Проверь это:

```bash
bench --site learn.localhost list-apps
```

Должны остаться:

```text
frappe
training
```

Дополнительно проверь:

```bash
test -d apps/erpnext && echo "UNEXPECTED: ERPNext code exists" || echo "OK: ERPNext code is still absent"
```

Ожидается:

```text
OK: ERPNext code is still absent
```

Если это так, стенд восстановлен в исходное состояние — фактически не было чего восстанавливать в данных, мы только убедились, что ошибочная установка не состоялась.

---

## Проверка себя

Ответь без подсказки.

1. Почему `User` доступен без ERPNext?
2. Почему `Sales Invoice` не обязан существовать в чистом Framework?
3. Чем отличается `apps/erpnext` от `bench --site learn.localhost list-apps`?
4. Почему `install-app erpnext` не должен сам скачать ERPNext?
5. Что будет содержать наше `training` после следующего блока?
6. Появился ли `Request` в блоке A?

---

## Состояние стенда после лабораторной

Блок A закончен.

Фактическое состояние стенда:

```text
Bench:          ~/frappe/frappe16-course-bench
Frappe:         v16.32.0
Site:           learn.localhost
Apps in Bench:  frappe, training
Apps installed: frappe, training
Module:         Training
Developer Mode: включён
User:           Administrator
ERPNext:        отсутствует
Request:        ещё не создан
```

Новых бизнес-DocTypes, Documents, ролей, Workspaces или настроек в блоке A не создано.

Это состояние является входом следующего блока: [**04. DocType от А до Я**](../04_DOCTYPE.md).