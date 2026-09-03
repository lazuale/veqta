# S02. Добавить permissions и доказать границу обычного status

После S01 `Purchase Request` уже хранит состояние в обычном `status : Select`.

Теперь появляется новое требование доступа:

```text
заявитель создаёт и редактирует заявку
согласующий работает с существующей заявкой
```

Это ещё не Workflow. Сначала используем штатные Role и DocType Permissions, а затем проверяем, чего они не умеют выразить.

## 1. Создать две роли на dev Site

Через Desk откройте `Role` и создайте:

```text
PLT Requester
PLT Approver
```

Роли нужны на dev Site, чтобы настроить permissions Standard DocType.

На этом этапе не экспортируйте их как fixtures.

## 2. Настроить Standard DocType Permissions

Откройте `Purchase Request` → Permissions.

Для `PLT Requester`:

```text
Read    yes
Create  yes
Write   yes
Delete  no
Submit  no
Cancel  no
Amend   no
```

Для `PLT Approver`:

```text
Read    yes
Create  no
Write   yes
Delete  no
Submit  no
Cancel  no
Amend   no
```

Сохраните DocType.

Пока не включайте `If Owner`: текущие требования не говорят, что Requester должен видеть только собственные заявки. Не добавляйте ограничение, которого пока нет в требованиях.

Официальное описание модели пользователей, ролей и DocType Permissions: https://docs.frappe.io/framework/user/en/basics/users-and-permissions

## 3. Проверить permissions в исходниках App

```bash
cd ~/frappe/rental-training-bench

git -C apps/purchase_lifecycle_training diff -- \
  purchase_lifecycle_training/purchase_lifecycle_training/doctype/purchase_request/purchase_request.json
```

В metadata `Purchase Request` должны появиться строки permissions с именами:

```text
PLT Requester
PLT Approver
```

Это важно для дальнейшей поставки App: default DocPerm собственного Standard DocType хранятся в его metadata.

## 4. Создать пользователей Site

Через Desk создайте двух пользователей, например:

```text
requester@example.test
approver@example.test
```

Назначьте роли:

```text
requester@example.test → PLT Requester
approver@example.test  → PLT Approver
```

Пароли и сами User records — данные конкретного Site. В Git их не экспортируем.

## 5. Проверить обычный доступ

Под `requester@example.test`:

1. создайте `Purchase Request`;
2. заполните обязательные поля;
3. сохраните его с `PLT Draft`;
4. откройте повторно и измените `subject`.

Под `approver@example.test`:

1. откройте существующую заявку;
2. убедитесь, что она читается;
3. измените обычное поле и сохраните.

Мы проверяем базовый смысл DocPerm:

```text
может ли роль работать с Document вообще?
```

## 6. Провести главный отрицательный опыт

Вернитесь под `requester@example.test`.

Откройте свою заявку и вручную измените:

```text
Status:
PLT Draft
→
PLT Approved
```

Нажмите Save.

На этом этапе сохранение должно пройти, потому что:

```text
Requester имеет Write
status — обычный Select
Workflow отсутствует
```

То же можно проверить через Bench Console:

```bash
bench --site purchase-lifecycle.localhost console
```

```python
frappe.set_user("requester@example.test")
name = frappe.get_all("Purchase Request", pluck="name", limit=1)[0]
doc = frappe.get_doc("Purchase Request", name)
doc.status = "PLT Approved"
doc.save()
print(doc.status)
```

Верните пользователя:

```python
frappe.set_user("Administrator")
exit()
```

## 7. Что именно доказал опыт

DocPerm решает задачу:

```text
PLT Requester имеет Write
→ может сохранять Purchase Request
```

Но из него нельзя выразить процессное правило:

```text
Requester:
PLT Draft → PLT Pending Approval

Approver:
PLT Pending Approval → PLT Approved / PLT Rejected

Requester:
не может PLT Pending Approval → PLT Approved
```

Это уже другая ответственность — допустимые переходы между состояниями.

Именно теперь появляется основание использовать `Workflow`.

## 8. Вернуть контрольные данные в понятное состояние

Запись, на которой вручную ставили `PLT Approved`, является временной учебной записью. Удалите её или верните в `PLT Draft` до следующего этапа.

Нам важно не сохранить искусственный «одобренный» Document как будто он прошёл настоящий процесс.

## Результат

После S02:

```text
PLT Requester / PLT Approver существуют
Standard DocPerm находятся в metadata Purchase Request
пользователи Site созданы отдельно
обычного status недостаточно для правил переходов
Workflow всё ещё отсутствует
```

Следующий этап: [`S03_BASIC_WORKFLOW.md`](S03_BASIC_WORKFLOW.md).
