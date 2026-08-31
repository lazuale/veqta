# Лабораторная 40. Website / Portal

## Цель

Увидеть, что Website/Portal — это не Desk и не просто Web Form.

## Сделай руками

Создай простую web-страницу или website route средствами Framework, доступными на чистом v16.

Минимальная страница должна содержать:

```text
заголовок Training Portal
ссылку на Web Form Request
ссылку на страницу входа/Desk только как навигационный пример
```

Если глава описывает Portal Menu/Portal Settings — добавь один пункт для учебного пользователя.

## Проверь

Открой страницу:

1. как Guest;
2. как Website User, если создавался;
3. сравни с Desk под System User.

## Эксперимент

Создай отдельный route и посмотри URL mapping. Измени route и проверь старый/новый URL.

## Намеренная ошибка

Попробуй использовать Website Page как замену сложному Desk workspace с permissions/actions. Зафиксируй, где подход перестаёт соответствовать задаче.

## Проверка себя

Соотнеси:

```text
Desk       → внутренний рабочий интерфейс
Web Form   → форма над DocType
Website    → публичная/веб-страница
Portal     → authenticated website experience
```

## Состояние после лабораторной

Оставь простую страницу `Training Portal`.
