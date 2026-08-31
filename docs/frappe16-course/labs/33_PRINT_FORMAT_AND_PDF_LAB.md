# Лабораторная 33. Print Format и PDF

## Цель

Создать собственное печатное представление Request и увидеть границу HTML/Jinja/PDF renderer.

## Сделай руками

Создай Print Format для `Request` через штатный builder.

Выведи минимум:

```text
Subject
Status
Priority
Due Date
Responsible Name
Description
Items
```

Открой Print Preview.

## Эксперимент 1

Измени порядок блоков и подписи. Обнови preview.

## Эксперимент 2

Создай отдельный Custom HTML/Jinja Print Format с минимальным шаблоном, например:

```html
<h1>{{ doc.subject }}</h1>
<p>Status: {{ doc.status }}</p>
```

Сравни builder и ручной template.

## PDF

Нажми PDF/Download PDF и посмотри, работает ли renderer на текущем стенде.

Если PDF не строится, не «чинить наугад»: прочитай сообщение, проверь установленный PDF renderer/зависимости согласно текущей v16 документации и логам.

## Намеренная ошибка

Добавь в Jinja ссылку на несуществующее поле и посмотри результат. Затем исправь.

## Проверка себя

Объясни:

```text
Document data
→ Print Format/Jinja
→ HTML print view
→ PDF renderer
→ PDF
```

## Состояние после лабораторной

Оставь один рабочий Print Format `Request Training`.
