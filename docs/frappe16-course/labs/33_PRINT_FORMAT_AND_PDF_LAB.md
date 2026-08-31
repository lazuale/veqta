# Лабораторная 33. Print Format и PDF

## Цель

Создать печатное представление Request, а затем получить настоящий PDF на Frappe 16.

В v16 `Print Format` имеет выбор PDF generator:

```text
wkhtmltopdf
chrome
```

Для учебного Debian 13 используем `chrome`, чтобы получить воспроизводимый renderer из штатного Debian package.

## Шаг 1. Установи Chromium Headless

Во втором терминале:

```bash
sudo apt update
sudo apt install -y chromium-headless-shell
```

Проверь:

```bash
command -v chromium-headless-shell
chromium-headless-shell --version
```

Должен существовать исполняемый файл, обычно:

```text
/usr/bin/chromium-headless-shell
```

## Шаг 2. Скажи Frappe, где Chromium

```bash
cd ~/frappe/frappe16-course-bench
bench set-config -g chromium_path "$(command -v chromium-headless-shell)"
```

Проверь:

```bash
grep -n 'chromium_path' sites/common_site_config.json
```

После изменения общей конфигурации останови `bench start` в первом терминале через `Ctrl+C` и снова запусти:

```bash
cd ~/frappe/frappe16-course-bench
bench start
```

## Шаг 3. Создай Print Format

Создай Print Format:

```text
Name: Request Training
DocType: Request
PDF Generator: chrome
```

Через штатный builder выведи минимум:

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

## Эксперимент 1 — metadata builder

Измени порядок полей, подписи и margins. Обновляй Preview и наблюдай результат.

## Эксперимент 2 — Jinja

Создай второй Custom Print Format с минимальным шаблоном:

```html
<h1>{{ doc.subject }}</h1>
<p>Status: {{ doc.status }}</p>
<p>Priority: {{ doc.priority }}</p>
```

Для него также выбери:

```text
PDF Generator = chrome
```

Сравни builder и ручной Jinja template.

## Шаг 4. Получи PDF

Открой Request → Print → выбери `Request Training` → PDF.

Ожидаемый результат:

```text
браузерный Print Preview
и
реальный PDF-файл
```

## Намеренная ошибка

Временно укажи неправильный путь:

```bash
bench set-config -g chromium_path /no/such/chromium
```

Перезапусти `bench start` и попробуй PDF.

Прочитай реальную server error.

Затем восстанови:

```bash
bench set-config -g chromium_path "$(command -v chromium-headless-shell)"
```

и снова перезапусти `bench start`.

## Что насчёт wkhtmltopdf

Он остаётся штатным generator и default для обычного Print Format. Официальная документация Frappe требует `wkhtmltopdf 0.12.6 with patched Qt` для этого пути.

Мы не подменяем его случайным Debian package. В этой лабораторной цель — понять механизм Print/PDF и получить воспроизводимый PDF через поддерживаемый в v16 `chrome` generator.

## Проверка себя

Объясни цепочку:

```text
Document
→ Print Format
→ rendered HTML
→ выбранный PDF Generator
→ PDF
```

## Состояние после лабораторной

Оставь:

```text
Request Training
PDF Generator = chrome
chromium_path = реальный executable
```
