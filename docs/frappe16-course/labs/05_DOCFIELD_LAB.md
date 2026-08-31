# Лабораторная 05. DocField и свойства полей

## Цель

Не заучивать типы полей, а увидеть, как metadata меняет живую форму.

## Сделай руками

В `Request` добавь учебные поля:

```text
Is Urgent       Check
Estimate Hours  Int
Notes           Text Editor
Reference File  Attach
```

Для существующих полей последовательно попробуй свойства:

```text
Mandatory
Read Only
Hidden
In List View
Default
Description
```

Меняй только одно свойство за раз, сохраняй DocType и обновляй Form/List.

## Ожидаемый результат

Ты должен увидеть причинную связь:

```text
DocField metadata
→ Form/List renderer
→ другое поведение UI
```

## Эксперимент 1 — Default

Для `Priority` поставь Default = `Medium`. Создай новый Request и проверь значение. Затем открой уже существующий Request и убедись, что изменение default не переписало старые данные автоматически.

## Эксперимент 2 — In List View

Включи `In List View` для `Priority` и `Due Date`. Перейди в список Request и сравни.

## Намеренная ошибка

Сделай `Due Date` одновременно `Hidden` и `Mandatory`, затем попробуй создать новый Request.

Посмотри, какой UX получается. После эксперимента верни разумные свойства.

## Проверка себя

Для каждого утверждения скажи, metadata это или значение Document:

- `Priority` имеет тип Select;
- у REQ-X Priority = High;
- `Due Date` Mandatory;
- у REQ-Y Due Date = 2026-09-10.

## Состояние после лабораторной

Оставь `Priority`, `Due Date`, `Is Urgent`, `Estimate Hours`, `Notes`, `Reference File`. Не оставляй намеренно конфликтные Hidden/Mandatory настройки.
