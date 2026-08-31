# Лабораторная 25. `Status` против `Workflow State`

## Цель

Перестать смешивать обычное бизнес-поле и состояние Workflow engine.

## Подготовка

В `Request` уже есть обычное поле:

```text
Status = Open / In Progress / Done
```

## Сделай руками

Создай новое Select-поле только для временного опыта:

```text
Review State
Draft
Review
Approved
Rejected
```

Поменяй его значения вручную в нескольких Request.

Зафиксируй: это пока просто обычное поле. Никаких transition permissions, кнопок Workflow и engine нет.

## Затем

Открой DocType `Workflow State` и `Workflow`. Посмотри структуру, но не создавай финальный Workflow до следующей главы.

## Эксперимент

Под Training User вручную поменяй `Review State` с Draft сразу на Approved. Если обычные field permissions разрешают запись, Frappe это позволит — потому что это всего лишь Select.

## Намеренная ошибка

Попытайся считать список options Select полноценным Workflow. Запиши, чего не хватает:

```text
transition graph
allowed roles
conditions
state field management
workflow actions
```

## Проверка себя

Объясни три разных вещи:

```text
Status        → обычное бизнес-поле
Workflow State→ поле, управляемое Workflow
Docstatus     → системный lifecycle 0/1/2
```

## Состояние после лабораторной

`Review State` можно удалить перед следующей главой, чтобы не путать с настоящим Workflow State.
