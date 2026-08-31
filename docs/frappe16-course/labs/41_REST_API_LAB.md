# Лабораторная 41. REST API

## Цель

Сделать CRUD над тем же `Request` без Desk и увидеть, что REST работает с обычными Frappe Documents.

В этой главе используем **временную authenticated session Administrator через cookie jar**. Постоянную token authentication для интеграций разберём отдельно в главе 43.

## Шаг 1. Авторизуй curl без записи пароля в файл

Во втором терминале:

```bash
read -s -p "Frappe Administrator password: " FRAPPE_PASSWORD
echo
```

Выполни login:

```bash
curl -sS \
  -c /tmp/frappe-course.cookies \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'usr=Administrator' \
  --data-urlencode "pwd=${FRAPPE_PASSWORD}" \
  http://learn.localhost:8000/api/method/login
```

Сразу очисти shell variable:

```bash
unset FRAPPE_PASSWORD
```

Cookie лежит только во временном файле:

```text
/tmp/frappe-course.cookies
```

## Шаг 2. GET list

```bash
curl -sS \
  -b /tmp/frappe-course.cookies \
  -G \
  --data-urlencode 'fields=["name","subject","status","priority"]' \
  --data-urlencode 'limit_page_length=5' \
  http://learn.localhost:8000/api/resource/Request
```

## Шаг 3. GET один Document

Подставь реальный `name`:

```bash
curl -sS \
  -b /tmp/frappe-course.cookies \
  http://learn.localhost:8000/api/resource/Request/REQ-2026-00001
```

## Шаг 4. POST create

```bash
curl -sS \
  -b /tmp/frappe-course.cookies \
  -X POST \
  -H 'Content-Type: application/json' \
  --data '{
    "subject": "Created via REST",
    "status": "Open",
    "priority": "Medium"
  }' \
  http://learn.localhost:8000/api/resource/Request
```

Скопируй `name` созданного Document из JSON response.

## Шаг 5. PUT update

Подставь этот `name`:

```bash
curl -sS \
  -b /tmp/frappe-course.cookies \
  -X PUT \
  -H 'Content-Type: application/json' \
  --data '{"priority":"High"}' \
  http://learn.localhost:8000/api/resource/Request/ИМЯ_ДОКУМЕНТА
```

Открой тот же Request в Desk и проверь изменение.

## Шаг 6. DELETE

Создай ещё один специальный Request только для удаления и выполни:

```bash
curl -sS \
  -b /tmp/frappe-course.cookies \
  -X DELETE \
  http://learn.localhost:8000/api/resource/Request/ИМЯ_ТЕСТОВОГО_ДОКУМЕНТА
```

Не удаляй основной набор учебных данных.

## Эксперимент — server validation

Попробуй POST без Mandatory `subject`.

Ожидается server-side validation error.

Если к этому моменту Workflow/другие server rules ограничивают `Request`, учитывай их: REST не обходит lifecycle и permissions только потому, что запрос пришёл не из Desk.

## Намеренная ошибка — HTTP method

Попробуй вызвать resource operation неподходящим HTTP method и прочитай status/response.

## Проверка себя

Объясни:

```text
Desk Form
REST API
Python code
```

могут работать с одним и тем же Document `Request`.

## Состояние после лабораторной

Оставь один документ:

```text
Subject = Created via REST
```

Cookie jar можно оставить до лабораторной 42, затем удалить:

```bash
rm -f /tmp/frappe-course.cookies
```
