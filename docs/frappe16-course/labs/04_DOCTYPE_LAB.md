# Лабораторная 04. Создаём первый DocType `Request`

## Что должно быть готово

App `training` установлен на `learn.localhost`. Developer Mode включён в стенде главы 0.

## Цель

Создать реальный Standard DocType и несколько Documents.

## Сделай руками

В Desk открой `DocType` → `New`.

Создай:

```text
Name: Request
Module: Training

Fields:
Subject      Data        Mandatory
Description Small Text
Status       Select      Open\nIn Progress\nDone
Due Date     Date

Title Field: subject
Track Changes: enabled
```

Сохрани DocType.

Через Awesome Bar открой `Request` и создай три записи с разными `Status`.

## Проверь на диске

```bash
cd ~/frappe/frappe16-course-bench
find apps/training -type f | grep -i '/request/' | sort
```

Открой созданный JSON:

```bash
sed -n '1,220p' apps/training/training/training/doctype/request/request.json
```

Путь может отличаться на один уровень в зависимости от package layout; если команда не нашла файл, используй результат `find`.

## Что должно получиться

Ты видишь один объект сразу в трёх представлениях:

```text
DocType в Desk
→ metadata

Request Documents
→ реальные записи

request.json в App
→ Standard metadata в Git-friendly файле
```

## Эксперимент

Добавь четвёртое поле `Priority` типа `Select` с вариантами `Low`, `Medium`, `High`. Сохрани DocType, обнови Form Request и посмотри изменение. Затем снова открой `request.json` и найди новое поле.

## Намеренная ошибка

Попробуй создать Request без `Subject`.

Ожидаемый результат: Frappe не должен позволить сохранить Document, потому что поле Mandatory.

## Проверка себя

Объясни, что именно было создано один раз (`DocType`) и что создавалось три раза (`Document`).

## Состояние после лабораторной

Должны существовать `Request` и минимум три его Documents. Поле `Priority` оставить — оно понадобится дальше.
