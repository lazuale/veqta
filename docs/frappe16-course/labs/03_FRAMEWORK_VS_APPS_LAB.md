# Лабораторная 03. Framework против Apps

## Цель

Увидеть, что Frappe Framework уже работает как платформа без ERPNext.

## Сделай руками

В терминале:

```bash
cd ~/frappe/frappe16-course-bench
bench --site learn.localhost list-apps
ls -1 apps
```

Ожидаются как минимум:

```text
frappe
training
```

Проверь отсутствие ERPNext:

```bash
test -d apps/erpnext && echo "ERPNext есть" || echo "ERPNext не установлен"
```

В Desk открой:

- `User`;
- `Role`;
- `DocType`;
- `Workspace`;
- `Report`.

## Что увидим

Все эти возможности существуют уже в Framework.

`training` пока почти пустое App, но оно установлено на Site и может содержать наши объекты.

## Эксперимент

Выполни:

```bash
find apps/frappe/frappe -maxdepth 2 -type d | head -40
find apps/training -maxdepth 3 -type d | sort
```

Сравни масштаб Framework и пустого учебного App.

## Намеренная ошибка мышления

Проверь, есть ли в Awesome Bar `Sales Invoice`. На чистом Framework такого ERPNext DocType быть не должно.

Это демонстрирует границу:

```text
Frappe Framework ≠ ERPNext
```

## Проверка себя

Объясни: если установить CRM или ERPNext, станет ли сам Frappe другим Framework, или это будут дополнительные Apps поверх него?

## Состояние после лабораторной

Без изменений.
