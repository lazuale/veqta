# Лабораторная 01. Bench, Site, App, Module, DocType и Document

## Что уже должно быть готово

Эта лабораторная начинается ровно из состояния после главы 0.

Должно существовать:

```text
Bench:  ~/frappe/frappe16-course-bench
Site:   learn.localhost
Frappe: v16.32.0
Apps:   frappe, training
Module: Training
```

Дополнительно:

```text
Developer Mode: включён
User:           Administrator
Desk:           http://learn.localhost:8000
Request:        ещё не создан
```

В первом терминале должен работать:

```bash
cd ~/frappe/frappe16-course-bench
bench start
```

Все команды ниже выполняй **во втором терминале Debian**.

---

## Что сейчас получим

Ты увидишь один и тот же стенд с трёх сторон:

```text
файловая структура Bench
→ Apps и Site на диске

команда bench
→ Apps, установленные на конкретный Site

Desk
→ DocType и конкретный Document
```

После лабораторной никаких новых объектов или данных остаться не должно.

---

## Сделай руками

### 1. Убедись, что находишься в нужном Bench

```bash
cd ~/frappe/frappe16-course-bench
pwd
```

Ожидаемый конец пути:

```text
/frappe/frappe16-course-bench
```

Точный префикс домашнего каталога зависит от имени твоего Linux-пользователя.

---

### 2. Посмотри верхний уровень Bench

```bash
ls -la
```

Найди глазами как минимум:

```text
apps
sites
config
logs
env
```

Сейчас важно только увидеть, что `apps/` и `sites/` находятся рядом внутри одного Bench.

---

### 3. Посмотри Apps на диске

```bash
ls -1 apps
```

Должны быть как минимум:

```text
frappe
training
```

Это код Apps, доступный этому Bench.

---

### 4. Посмотри каталог Site

```bash
ls -la sites/learn.localhost
```

Найди:

```text
site_config.json
private
public
```

Не публикуй содержимое `site_config.json`: там могут быть чувствительные настройки Site.

---

### 5. Проверь, какие Apps установлены именно на `learn.localhost`

```bash
bench --site learn.localhost list-apps
```

Ожидаются как минимум:

```text
frappe 16.32.0
training
```

Формат строки и dev-версия `training` могут отличаться, но оба App должны присутствовать.

Здесь важно различие:

```text
ls apps
→ что есть в Bench как код

bench --site learn.localhost list-apps
→ что установлено на конкретный Site
```

---

### 6. Найди Module учебного App

Выполни:

```bash
cat apps/training/training/modules.txt
```

Должна быть строка:

```text
Training
```

Пока не разбирай внутреннее устройство App. Сейчас достаточно увидеть, что Module — не выдуманное название из текста: он реально зафиксирован в учебном App.

---

### 7. Открой системный DocType в Desk

В браузере открой:

```text
http://learn.localhost:8000
```

Если нужно, войди как:

```text
Administrator
```

Через поиск Desk найди:

```text
User
```

Открой список `User`.

То, что сейчас показано, — **List View Documents DocType `User`**.

---

### 8. Открой один Document

В списке `User` открой:

```text
Administrator
```

Теперь перед тобой один конкретный Document:

```text
DocType:  User
Document: Administrator
```

Вернись назад в список `User` и ещё раз проговори разницу:

```text
список User
→ много Documents одного DocType

форма Administrator
→ один Document этого DocType
```

---

## Проверь результат

К концу этого шага ты должен уметь показать на живом стенде:

```text
Bench     → ~/frappe/frappe16-course-bench
Site      → sites/learn.localhost
App       → apps/training
Module    → Training в modules.txt
DocType   → User
Document  → Administrator
```

И отдельно понимать связь:

```text
training находится в Bench как App
+
training установлен на learn.localhost
```

Это два разных факта.

---

## Эксперимент

Сравни две команды подряд:

```bash
cd ~/frappe/frappe16-course-bench
ls -1 apps
bench --site learn.localhost list-apps
```

Ответь себе:

1. Какая команда показывает каталоги App в Bench?
2. Какая команда спрашивает конкретный Site?
3. Почему эти два списка описывают разные уровни системы?

Ничего не меняй.

---

## Намеренная ошибка

Теперь укажи Site, которого на стенде нет:

```bash
bench --site no-such-site.localhost list-apps
```

Команда должна завершиться ошибкой: Bench не может получить установленные Apps у несуществующего Site.

Точный текст исключения может зависеть от CLI, но смысл один:

```text
no-such-site.localhost
→ не является существующим Site этого Bench
```

Это безопасная ошибка: мы ничего не создаём и не удаляем.

---

## Восстановление

Ничего чинить в данных не требуется — намеренная ошибка ничего не изменила.

Сразу повтори правильную команду:

```bash
bench --site learn.localhost list-apps
```

Снова должны быть видны:

```text
frappe
training
```

Так ты проверяешь, что рабочий Site остался в исходном состоянии.

---

## Проверка себя

Ответь без подсказки.

1. Почему `apps/training` и `sites/learn.localhost` находятся рядом, а не один внутри другого?
2. Чем отличается «App есть в Bench» от «App установлен на Site»?
3. Где зафиксировано имя Module `Training`?
4. Что в примере `User → Administrator` является DocType, а что Document?
5. Создали ли мы в этой лабораторной хоть один новый объект Frappe?

Если на последний вопрос ответ не «нет», вернись и проверь, что именно было изменено.

---

## Состояние стенда после лабораторной

Стенд не изменён.

Сохраняется:

```text
Bench:          ~/frappe/frappe16-course-bench
Site:           learn.localhost
Apps installed: frappe, training
Module:         Training
Developer Mode: включён
User:           Administrator
Request:        не существует
```

Новых Documents, DocTypes, ролей, настроек и файлов эта лабораторная не создаёт.

Это состояние является входом [**главы 02**](../02_DESK_NAVIGATION.md).