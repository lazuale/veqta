# Лабораторная 41. REST API

## Цель

Сделать CRUD над тем же `Request` без Desk и увидеть, что server rules остаются теми же.

## Подготовка

Используй authenticated session/cookie или безопасные API credentials из следующей главы только если уже созданы. Не публикуй секреты в history/Git.

Для первого опыта можно использовать `curl` с session login в локальном стенде либо token пользователя, подготовленный безопасно.

## GET list

```bash
curl -s 'http://learn.localhost:8000/api/resource/Request?fields=["name","subject","status"]'
```

Добавь authentication согласно главе 43, если endpoint не доступен анонимно.

## GET document

```bash
curl -s 'http://learn.localhost:8000/api/resource/Request/REQ-...'
```

## POST create

Отправь JSON с `subject`, `status`, `priority`.

## PUT update

Измени `Priority` созданного API-document.

## DELETE

Удаляй только специально созданный API test Request.

## Эксперимент

Создай через REST Request, который нарушает Mandatory/permissions. Сравни server error с Desk.

## Намеренная ошибка

Используй неразрешённый HTTP method для операции и посмотри response v16.

## Проверка себя

Объясни, почему REST resource API работает с теми же Documents, а не с отдельной «API-базой».

## Состояние после лабораторной

Оставь один Request с Subject `Created via REST`.
