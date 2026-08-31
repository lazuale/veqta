# Лабораторная 10. `docstatus`, Submit, Cancel и Amendment

## Цель

Пройти lifecycle Submittable Document руками.

## Сделай руками

Используй `Approval Record` из предыдущей лабораторной. Добавь поля:

```text
Subject   Data Mandatory
Comment   Small Text
```

Создай новый документ.

## Шаг 1 — Draft

Сохрани, но не Submit.

В bench console:

```bash
bench --site learn.localhost console
```

```python
d = frappe.get_last_doc("Approval Record")
(d.name, d.docstatus)
```

Ожидается `0`.

## Шаг 2 — Submit

В форме нажми Submit. Снова проверь `docstatus` — ожидается `1`.

Попробуй изменить обычное поле `Subject` после Submit.

## Шаг 3 — Cancel

Нажми Cancel. Проверь `docstatus` — ожидается `2`.

## Шаг 4 — Amend

Используй Amend. Посмотри, какой новый Document создаётся и как он связан с отменённым.

## Эксперимент

Добавь поле, которое разрешено изменять после Submit (`Allow on Submit`), и сравни с обычным полем.

## Намеренная ошибка

После Submit попробуй изменить поле, для которого `Allow on Submit` выключен. Не обходи ограничение кодом — именно увидь штатный отказ.

## Проверка себя

Назови значения:

```text
Draft      → ?
Submitted  → ?
Cancelled  → ?
```

И объясни, почему бизнес-поле `Status` не равно `docstatus`.

## Состояние после лабораторной

Оставь минимум один Draft, один Submitted и один Cancelled/Amended пример для сравнения в следующих главах.
