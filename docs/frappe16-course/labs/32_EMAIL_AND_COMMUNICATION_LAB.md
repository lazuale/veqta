# Лабораторная 32. Email / Communication

## Цель

Отправить настоящее SMTP-сообщение из Frappe, но не во внешний интернет, а в локальный отладочный SMTP server.

Мы увидим всю цепочку:

```text
Request
→ Send Email
→ Email Queue
→ SMTP
→ локальный aiosmtpd
→ Communication / Timeline
```

## Шаг 1. Запусти локальный SMTP sink

Открой **третий терминал Debian** и выполни:

```bash
uvx --from aiosmtpd aiosmtpd -n -l localhost:1025
```

Процесс останется запущенным и будет печатать принятые письма прямо в терминал.

Не закрывай его до конца лабораторной.

Порт `1025` слушает только локальный учебный компьютер.

## Шаг 2. Создай Email Account

В Desk открой `Email Account` → `New`.

Настрой учебный исходящий аккаунт примерно так:

```text
Email Address: training@example.test
Email Account Name: Training Local SMTP
Enable Incoming: off
Enable Outgoing: on
Default Outgoing: on

Outgoing Server: localhost
Port: 1025
Use TLS: off
Use SSL for Outgoing: off
Disable SMTP server authentication: on
```

Если UI показывает дополнительные поля authentication, смысл конфигурации остаётся один:

```text
локальный SMTP
без TLS
без login/password
```

Сохрани.

## Шаг 3. Отправь письмо из Request

Открой любой Request и используй штатное действие Email.

Получатель:

```text
student@example.test
```

Subject:

```text
Training Request {{ request name }}
```

Отправь.

## Что должно произойти

Проверь четыре места:

1. терминал `aiosmtpd` — там должно появиться содержимое письма;
2. `Email Queue` — запись должна пройти очередь;
3. `Communication` — должна появиться коммуникация;
4. Timeline Request — должно появиться связанное событие.

Если сообщение висит в очереди, открой запись `Email Queue`, прочитай status/error и при необходимости используй штатное `Send Now`.

## Эксперимент

Отправь второе письмо и приложи один учебный Attachment из Request.

Сравни:

```text
Communication
Email Queue
вывод aiosmtpd
```

## Намеренная ошибка

В Email Account временно поставь:

```text
Port = 1026
```

Отправь ещё одно письмо.

Ожидается ошибка подключения в Email Queue/logs.

Верни:

```text
Port = 1025
```

и повтори отправку успешно.

## Проверка себя

Объясни:

```text
Email Account → конфигурация транспорта
Email Queue   → очередь отправки
SMTP server   → фактическая доставка
Communication → история коммуникации Frappe
```

## Состояние после лабораторной

Оставь `Training Local SMTP` только как учебный аккаунт.

`aiosmtpd` после лабораторной останови `Ctrl+C`.

Никаких реальных SMTP passwords на стенде не требуется.
