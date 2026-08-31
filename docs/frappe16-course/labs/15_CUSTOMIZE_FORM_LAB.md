# Лабораторная 15. Customize Form

## Цель

Увидеть разницу между Standard metadata App и site-specific customization.

## Сделай руками

1. Зафиксируй текущее состояние файла Request:

```bash
cd ~/frappe/frappe16-course-bench
git -C apps/training status --short
```

2. В Desk открой `Customize Form`.
3. Выбери `Request`.
4. Добавь Custom Field, например:

```text
Label: Local Note
Type: Small Text
Fieldname: custom_local_note
```

5. Сохрани и открой Request Form.

## Наблюдение

Поле появилось на Site, но это не то же самое, что вручную добавить Standard DocField в исходный `request.json`.

## Проверь данные customization

Через Awesome Bar найди `Custom Field` и найди запись для `Request-custom_local_note`.

Также найди `Property Setter`, если в Customize Form менял свойства стандартного поля.

## Эксперимент

Через Customize Form измени Label существующего поля `Description`, затем найди созданный Property Setter. После наблюдения верни исходный Label или оставь осмысленное учебное изменение.

## Намеренная ошибка

Попробуй относиться к Customize Form как к редактору исходного `request.json`. Сравни `git status` и реальные Custom Field/Property Setter Records — это разные механизмы.

## Проверка себя

Ответь:

- где живёт Standard DocField;
- где живёт Custom Field;
- что делает Property Setter;
- почему site customization удобно, но требует отдельной стратегии переноса.

## Состояние после лабораторной

Оставь `custom_local_note`: позже он пригодится в главах Standard vs Custom и Fixtures.
