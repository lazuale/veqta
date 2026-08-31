# Лабораторная 35. Query Report

## Цель

Создать SQL-отчёт и увидеть, как SQL напрямую формирует набор строк.

## Подготовка

Используй только учебный Site и read-only SELECT.

## Сделай руками

Создай Query Report для `Request`.

Пример базового запроса адаптируй к фактическим fieldnames:

```sql
SELECT
    name,
    subject,
    status,
    priority,
    due_date
FROM `tabRequest`
WHERE docstatus < 2
ORDER BY modified DESC
```

Добавь Report columns/metadata так, как требует текущий v16.

## Эксперимент

Добавь фильтр `status` и используй его в query через безопасный report-filter синтаксис Frappe текущей версии.

Сравни:

```text
без фильтра
с Open
с Done
```

## Намеренная ошибка

Сделай опечатку в имени таблицы или поля. Посмотри SQL error и исправь её по тексту ошибки, а не случайными изменениями.

Не выполняй `UPDATE`, `DELETE`, `DROP` в учебном Query Report.

## Проверка себя

Почему Query Report мощнее Report Builder, но требует понимания структуры БД и ответственности за SQL?

## Состояние после лабораторной

Оставь рабочий read-only Query Report.
