# 10. `docstatus`, Submit, Cancel и Amendment

В лабораторной 09 появился первый `Approval Record`, сохранённый как Draft. Он специально остался неподтверждённым.

Теперь пройдём полный системный lifecycle Submittable Document руками:

```text
Draft
→ Submit
→ Submitted
→ Cancel
→ Cancelled
→ Amend
→ новый Draft
```

Без Python, REST API и controller hooks: сейчас важно сначала увидеть само поведение Framework.

Проверено для **Frappe Framework v16.32.0**.

---

## Что уже есть на стенде

`Approval Record`:

```text
Is Submittable: 1
Auto Name:      APR-.YYYY.-.#####
Title Field:    subject
```

Поля:

```text
subject       Data   Mandatory
amended_from  Link → Approval Record   добавлено Framework
```

Есть минимум один сохранённый Draft:

```text
APR-2026-00001
Subject = Первый черновик Approval Record
```

Submit у него ещё не выполнялся.

---

## `docstatus` — системное состояние документа

У Submittable Document Frappe использует системное поле:

```text
docstatus
```

В `v16.32.0` значения зафиксированы так:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Это не обычный `Select`, который мы сами добавили в DocType.

Framework использует `docstatus`, чтобы контролировать допустимые действия над подтверждаемым документом.

---

## `Request.status` и `Approval Record.docstatus` — не одно и то же

У нашего основного `Request` есть обычное поле:

```text
status
→ Open / In Progress / Done
```

Мы сами создали его как `Select`.

У `Approval Record` есть системный lifecycle:

```text
docstatus
→ Draft / Submitted / Cancelled
```

Они отвечают на разные вопросы.

```text
status
→ предметное состояние, определённое моделью приложения

docstatus
→ системное состояние Submittable Document во Frappe
```

Поэтому нельзя воспринимать Submit как ещё одно значение обычного поля `Status`.

---

# Draft

## Что означает Draft

Новый сохранённый `Approval Record` начинается как:

```text
docstatus = 0
Draft
```

Это рабочий черновик.

Его можно редактировать обычным Save, пока документ не подтверждён.

На этом состоянии остановилась лабораторная 09.

---

# Submit

## Чем Submit отличается от Save

Save сохраняет Draft и оставляет:

```text
docstatus = 0
```

Submit переводит документ в:

```text
docstatus = 1
```

То есть Submit означает не просто «ещё раз сохранить», а изменить системное состояние документа.

После этого Framework применяет ограничения Submitted Document.

---

## Почему после Submit обычные поля блокируются

Если подтверждённый документ можно свободно переписывать, Submit теряет смысл.

Поэтому обычные поля после Submit нельзя менять обычным редактированием.

Для нашего `Approval Record` поле:

```text
Subject
```

после Submit должно быть защищено от обычного изменения.

Это не просто визуальная договорённость формы. В `v16.32.0` Document lifecycle отдельно проверяет update after submit и разрешает изменения только там, где metadata явно это допускает.

---

# `Allow on Submit`

Иногда после подтверждения нужно оставить редактируемым отдельное служебное поле.

В лабораторной добавим:

```text
Internal Note
fieldname: internal_note
Field Type: Small Text
Allow on Submit: включено
```

И рядом обычное поле:

```text
Comment
fieldname: comment
Field Type: Small Text
Allow on Submit: выключено
```

После Submit получится наглядный контраст:

```text
Comment
→ обычное поле
→ менять после Submit нельзя

Internal Note
→ Allow on Submit
→ допускается Update после Submit
```

Так ученик увидит назначение свойства, которое в главе 05 мы специально не изучали заранее.

---

# Cancel

Submitted Document можно отменить штатным действием:

```text
Cancel
```

После него:

```text
docstatus = 2
Cancelled
```

Cancel не удаляет запись.

Отменённый `Approval Record` остаётся в системе как часть истории.

Это принципиально отличается от физического удаления Document.

---

## Почему Cancelled не возвращаем обратно в Draft

Обычный lifecycle не разрешает превращать уже отменённую запись назад в прежний черновик простым Save.

Если документ был подтверждён, затем отменён из-за ошибки, Framework предлагает другой путь:

```text
Amend
```

Так история старой версии не переписывается.

---

# Amendment

## Что делает Amend

После Cancel можно создать исправленную версию через:

```text
Amend
```

Frappe создаёт **новый Document** в состоянии Draft.

Старый остаётся:

```text
Cancelled
```

Новый получает связь:

```text
amended_from = name отменённого Approval Record
```

Именно эта связь, а не внешний вид нового номера, является главным доказательством Amendment.

При стандартных настройках amended document часто получает суффикс вроде `-1`, но naming Amendment может настраиваться. В лабораторной мы не полагаемся на конкретный суффикс: проверяем `Amended From` и новый Draft.

---

## Почему Amendment лучше переписывания истории

Получается цепочка:

```text
старый Document
Submitted
→ Cancelled

новый Document
Draft
amended_from → старый Document
```

Можно увидеть:

```text
какая версия была подтверждена
почему она отменена
какая новая версия создана на её основе
```

Вместо того чтобы незаметно изменить уже подтверждённую запись.

---

# Что сейчас не изучаем

У lifecycle есть server-side события и методы, например проверки перед Submit/Cancel и код после этих действий.

Они относятся к controller и application code, которые будут позже.

Также пока не соединяем Submit с Workflow. Workflow появится в отдельном блоке процессов.

Сейчас ответственность главы ограничена наблюдаемой моделью:

```text
Draft
Submit
Allow on Submit
Cancel
Amend
```

---

## Что произойдёт в лабораторной

Ты:

1. добавишь `Comment` и `Internal Note` к существующему `Approval Record`;
2. у `Internal Note` включишь `Allow on Submit`;
3. сохранишь новый Draft;
4. нажмёшь Submit и увидишь Submitted;
5. изменишь `Internal Note` после Submit штатным Update;
6. намеренно попробуешь изменить обычный `Comment` и увидишь блокировку;
7. нажмёшь Cancel;
8. убедишься, что Document остался, но стал Cancelled;
9. нажмёшь Amend;
10. увидишь новый Draft и заполненное `Amended From`;
11. оставишь на стенде примеры Draft, Submitted, Cancelled и Amended Draft для следующих глав.

---

## Что запомнить

1. `docstatus` — системное состояние Submittable Document.
2. `0 / 1 / 2` означают Draft / Submitted / Cancelled.
3. Save и Submit — разные действия.
4. После Submit обычные поля защищены от свободного изменения.
5. `Allow on Submit` разрешает ограниченное обновление конкретного поля после Submit.
6. Cancel не удаляет Document.
7. Amend создаёт новый Draft и связывает его с отменённым через `amended_from`.
8. `Request.status` и `Approval Record.docstatus` — разные механизмы.

---

## Официальные источники

- [Document API](https://docs.frappe.io/framework/user/en/api/document)
- [DocStatus — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/docstatus.py)
- [Document lifecycle — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/document.py)
- [Submittable `amended_from` generation — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/core/doctype/doctype/doctype.py)
- [Amended naming — v16.32.0](https://github.com/frappe/frappe/blob/v16.32.0/frappe/model/naming.py)

Теперь выполни [**лабораторную 10**](labs/10_DOCSTATUS_LIFECYCLE_LAB.md).

После неё блок B завершён. Следующий блок начинается с [**11. Form View**](11_FORM_VIEW.md).