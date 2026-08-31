# Лабораторная 43. Authentication для интеграций

## Цель

Выполнить API request без browser session от отдельного учебного integration user.

## Создай User

Например:

```text
training.api@example.test
```

Выдай только минимальные роли/permissions для Request.

## API key/secret

Сгенерируй credentials штатным способом Frappe v16.

Секрет:

```text
не записывать в README
не коммитить в Git
не вставлять в скриншоты
```

Храни только локально на время лабораторной, например в shell переменных:

```bash
export FRAPPE_API_KEY='...'
export FRAPPE_API_SECRET='...'
```

## Вызов

```bash
curl -s \
  -H "Authorization: token ${FRAPPE_API_KEY}:${FRAPPE_API_SECRET}" \
  'http://learn.localhost:8000/api/resource/Request?limit_page_length=5'
```

## Эксперимент

1. Сними у API User Read permission на Request и повтори.
2. Верни Read.
3. Попробуй Create без Create permission.
4. Верни минимально необходимую матрицу.

## Намеренная ошибка

Используй неправильный secret и сравни `401/403` с permission error авторизованного пользователя. Это разные классы проблем.

## Проверка себя

Раздели:

```text
authentication → кто ты
permissions    → что тебе можно
```

## Состояние после лабораторной

API User оставить, secret хранить только локально; после курса credentials можно отозвать.
