# Лабораторная 08. Child Table

## Цель

Создать строки, которые принадлежат родительскому Request, и увидеть их реальную модель хранения.

## Сделай руками

Создай DocType:

```text
Name: Request Item
Module: Training
Is Child Table: enabled
```

Поля:

```text
Title   Data
Qty     Float
Rate    Currency
Amount  Currency
```

В `Request` добавь поле:

```text
Items  Table → Request Item
```

Создай Request с тремя строками.

## Ожидаемый результат

Строки редактируются внутри родительского Document и не ведут себя как независимый master-справочник.

## Проверь через Console

Открой bench console:

```bash
cd ~/frappe/frappe16-course-bench
bench --site learn.localhost console
```

В Python:

```python
r = frappe.get_last_doc("Request")
r.name
[(x.name, x.parent, x.parenttype, x.parentfield, x.idx) for x in r.items]
```

Выйди:

```python
exit()
```

## Эксперимент

Поменяй порядок строк в форме, сохрани и снова посмотри `idx`.

## Намеренная ошибка

Попробуй найти `Request Item` как обычный независимый список и создать строку без parent через обычный пользовательский сценарий. Смысл — увидеть, что Child DocType предназначен для принадлежности parent-документу.

## Проверка себя

Объясни поля child row:

```text
parent
parenttype
parentfield
idx
```

## Состояние после лабораторной

`Request Item` и поле `Items` оставить.
