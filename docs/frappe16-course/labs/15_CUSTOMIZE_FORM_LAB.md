# Лабораторная 15. Customize Form и site-level metadata

## Что уже должно быть готово

Лабораторная 14 завершена.

Существуют:

```text
Standard DocType: Request
Workspace: Training
Number Card: Open Requests
Dashboard Chart: Requests by Status
```

Standard metadata `Request` находится в:

```text
apps/training/training/training/doctype/request/request.json
```

---

## Что сейчас получим

На Site `learn.localhost` оставим:

```text
Custom Field:
Request-custom_local_note

Property Setter:
Request-estimate_hours-description
```

При этом содержимое:

```text
request.json
```

не должно измениться ни на байт в результате Customize Form.

---

# Часть 1. Зафиксируй конкретный Standard-файл

## 1. Сними checksum до customization

Во втором терминале Debian:

```bash
cd ~/frappe/frappe16-course-bench

REQ_JSON="apps/training/training/training/doctype/request/request.json"
sha256sum "$REQ_JSON" | tee /tmp/request-json-before.sha256
```

Ты увидишь строку вида:

```text
<64 hex characters>  apps/training/training/training/doctype/request/request.json
```

Само значение хэша у разных проходов курса может отличаться. Важно сохранить именно текущее значение в `/tmp/request-json-before.sha256`.

---

# Часть 2. Добавь постоянный Custom Field

## 2. Открой Customize Form

В Desk:

```text
поиск → Customize Form
```

В поле выбора DocType укажи:

```text
Request
```

Не открывай Standard `DocType → Request`: в этой лабораторной работаем именно через `Customize Form`.

---

## 3. Добавь `Local Note`

Добавь новое поле:

```text
Label:        Local Note
Fieldname:    custom_local_note
Field Type:   Small Text
Insert After: reference_file
```

Сохрани customization.

---

## 4. Проверь Form View

Открой любой существующий Request серии:

```text
REQ-2026-.....
```

На вкладке `Details` найди новое поле:

```text
Local Note
```

Введи:

```text
Local value from chapter 15
```

Сохрани Request.

Закрой и снова открой этот Document.

Значение должно сохраниться.

---

## 5. Найди точный `Custom Field`

Через поиск Desk открой:

```text
Custom Field
```

Найди Document:

```text
Request-custom_local_note
```

Проверь:

```text
DocType:    Request
Fieldname:  custom_local_note
Field Type: Small Text
```

Теперь видно, где именно Site хранит новое поле.

---

# Часть 3. Создай Property Setter

## 6. Вернись в Customize Form → Request

Найди существующее Standard field:

```text
Estimate Hours
fieldname = estimate_hours
```

Измени только его свойство Description:

```text
Local customization from chapter 15
```

Ни Label, ни Field Type, ни fieldname не меняй.

Сохрани Customize Form.

---

## 7. Проверь подсказку на форме

Открой Request.

У `Estimate Hours` должна отображаться локальная Description:

```text
Local customization from chapter 15
```

Само поле остаётся:

```text
estimate_hours
Int
```

---

## 8. Найди точный Property Setter

Через поиск Desk открой:

```text
Property Setter
```

Найди:

```text
Request-estimate_hours-description
```

Проверь:

```text
Doc Type:   Request
Field Name: estimate_hours
Property:   description
Value:      Local customization from chapter 15
```

Это локальное переопределение свойства Standard DocField.

---

# Часть 4. Намеренная ошибка — Mandatory Custom Field

## 9. Добавь временное поле

Снова открой:

```text
Customize Form → Request
```

Добавь:

```text
Label:        Chapter 15 Required Test
Fieldname:    custom_ch15_required_test
Field Type:   Data
Mandatory:    ✓
Insert After: custom_local_note
```

Сохрани.

---

## 10. Создай новый Request без тестового поля

Открой новый Request.

Заполни:

```text
Subject:  C15 mandatory customization test
Status:   Open
Priority: Medium
```

Поле:

```text
Chapter 15 Required Test
```

оставь пустым.

Нажми Save.

Ожидаемый результат:

```text
Frappe отказывает в сохранении
→ custom_ch15_required_test является Mandatory
```

Таким образом site customization влияет не только на внешний вид формы, но и на validation Document.

---

# Часть 5. Восстановление

## 11. Удали временный Custom Field

Вернись в:

```text
Customize Form → Request
```

Удалить строку:

```text
Chapter 15 Required Test
custom_ch15_required_test
```

Сохрани Customize Form.

Не удаляй:

```text
Local Note
custom_local_note
```

---

## 12. Докажи восстановление

Вернись к несохранённому Request:

```text
Subject: C15 mandatory customization test
```

Обнови форму, чтобы получить актуальную metadata.

Проверь, что поля:

```text
Chapter 15 Required Test
```

больше нет.

Сохрани Request.

Ожидаемый результат:

```text
Document сохраняется
```

---

## 13. Проверь, что временный Custom Field исчез

Через `Custom Field` попробуй найти:

```text
Request-custom_ch15_required_test
```

Такой активной Custom Field записи после удаления быть не должно.

При этом должен оставаться:

```text
Request-custom_local_note
```

---

# Часть 6. Докажи, что `request.json` не менялся

## 14. Сними checksum после customization

В том же терминале:

```bash
cd ~/frappe/frappe16-course-bench

REQ_JSON="apps/training/training/training/doctype/request/request.json"
sha256sum "$REQ_JSON" | tee /tmp/request-json-after.sha256
```

Сравни:

```bash
diff -u /tmp/request-json-before.sha256 /tmp/request-json-after.sha256
```

Ожидаемый результат:

```text
команда diff ничего не выводит
```

Это означает:

```text
SHA-256 до = SHA-256 после
→ request.json не изменился
```

При этом на форме появились Local Note и новая Description у Estimate Hours.

Следовательно, изменения пришли из site customization.

---

## Проверка себя

Ответь без подсказки.

1. Где лежит Standard metadata `Request`?
2. Как называется Document нового поля `Local Note`?
3. Почему его нет как новой строки Standard DocField в `request.json`?
4. Как называется Property Setter для Description `estimate_hours`?
5. Что доказала временная Mandatory customization?
6. Почему `git status` был бы слабее проверки конкретного SHA-256?
7. Какие две site customizations должны остаться после восстановления?

---

## Состояние стенда после лабораторной

Standard `request.json` имеет тот же SHA-256, что до лабораторной.

На Site остаётся Custom Field:

```text
Name:       Request-custom_local_note
DocType:    Request
Fieldname:  custom_local_note
Field Type: Small Text
```

Минимум один Request содержит:

```text
custom_local_note = Local value from chapter 15
```

На Site остаётся Property Setter:

```text
Name:       Request-estimate_hours-description
Doc Type:   Request
Field Name: estimate_hours
Property:   description
Value:      Local customization from chapter 15
```

Временный объект полностью удалён:

```text
Request-custom_ch15_required_test
```

Workspace и Views предыдущих лабораторных не изменены.

Это точное входное состояние [**главы 16**](../16_DESK_PAGE_AND_UI_BOUNDARIES.md).
