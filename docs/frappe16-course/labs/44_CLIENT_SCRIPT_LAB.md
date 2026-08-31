# Лабораторная 44. Client Script

## Цель

Своими руками увидеть: Client Script делает UI удобнее, но не является server-side rule.

## Подготовка

В `Request` должны быть:

```text
Priority
Due Date
Status
Result или создай поле Result Small Text
Responsible
Items
```

## Эксперимент 1 — conditional mandatory

Создай Client Script для Request:

```javascript
frappe.ui.form.on('Request', {
    refresh(frm) {
        frm.toggle_reqd('due_date', frm.doc.priority === 'High');
    },
    priority(frm) {
        frm.toggle_reqd('due_date', frm.doc.priority === 'High');
    }
});
```

Проверь Low и High.

## Эксперимент 2 — show/hide

Показывай `Result` только при `Status = Done`.

## Эксперимент 3 — custom button

Добавь кнопку, которая показывает `frappe.msgprint` или меняет UI-only поле.

## Эксперимент 4 — Child Table calculation

На `Request Item` пересчитывай `amount = qty * rate` через client event.

## Главный обязательный опыт

Через REST API создай High Priority Request без Due Date.

Если server metadata не делает Due Date mandatory постоянно, REST не выполнит этот Client Script. Зафиксируй разницу.

## Намеренная ошибка

Спрячь `Internal Cost` через Client Script и под пользователем без permission попробуй запросить данные server-side. Это должно показать: скрытие UI не заменяет Permission Level.

## Проверка себя

Назови минимум три вещи, для которых Client Script хорош, и три вещи, которые нельзя доверять только Client Script.

## Состояние после лабораторной

Оставь Client Script с понятной UI-логикой; критические правила будут продублированы server-side в следующей главе.
