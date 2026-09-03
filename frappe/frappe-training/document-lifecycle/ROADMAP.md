# Маршрут практикума

Практикум начинается с обычного `Document` и добавляет следующий механизм только после появления требования, которое предыдущий механизм уже не закрывает.

```text
отдельный App и Site
  ↓
обычный Purchase Request
  ↓
обычный status
  ↓
права на DocType
  ↓
доказанная граница plain status
  ↓
Workflow
  ↓
запрет self approval
  ↓
условный второй уровень согласования
  ↓
Submit / docstatus
  ↓
Cancel
  ↓
Amend
  ↓
поставка конфигурации
  ↓
автоматические тесты
  ↓
чистая установка
```

## Этапы

1. **[S00 — отдельный App и Site](stages/S00_APP_AND_SITE.md)**  
   Создать `purchase_lifecycle_training` в совместимом Bench и установить его на отдельный `purchase-lifecycle.localhost`.

2. **[S01 — обычный Purchase Request](stages/S01_PURCHASE_REQUEST.md)**  
   Создать минимальный Standard DocType, naming, связь заявителя с `owner` и обычный `status : Select` без Workflow.

3. **[S02 — доступ и граница plain status](stages/S02_PERMISSIONS_AND_STATUS_LIMIT.md)**  
   Добавить `PLT Requester` и `PLT Approver`, настроить DocPerm и проверить, почему обычный `Write` не выражает допустимость конкретного перехода состояния.

4. **[S03 — базовый Workflow](stages/S03_BASIC_WORKFLOW.md)**  
   Сделать существующий `status` полем состояния Workflow, добавить отправку на согласование, Approve, Reject, повторную отправку и наблюдение `Workflow Action`.

5. **[S04 — запрет self approval](stages/S04_SELF_APPROVAL.md)**  
   Использовать штатную настройку `Allow Self Approval`, чтобы пользователь с двумя ролями не мог одобрить собственную заявку.

6. **[S05 — условный второй уровень согласования](stages/S05_CONDITIONAL_APPROVAL.md)**  
   Для суммы больше `1000` добавить `PLT Senior Approver` и второй уровень Workflow через условия переходов.

7. **[S06 — окончательное согласование через Submit](stages/S06_SUBMITTABLE.md)**  
   Включить `Is Submittable`, перевести `PLT Approved` в `docstatus = 1` и выдать минимальные Submit permissions.

8. **[S07A — Cancel](stages/S07A_CANCEL.md)**  
   Добавить штатную отмену согласованной заявки с переходом `docstatus 1 → 2` и отдельным Cancel permission.

9. **[S07B — новая версия отменённой заявки через Amend](stages/S07B_AMEND.md)**  
   Разрешить заявителю создавать новую версию отменённой заявки через штатный Amend.

10. **[S08 — поставка конфигурации](stages/S08_APP_STATE_DELIVERY.md)**  
    Разобрать, что уже поставляется Standard metadata, а что нужно экспортировать через filtered fixtures.

11. **[S09 — автоматические тесты](stages/S09_AUTOMATED_TESTS.md)**  
    Закрепить маршруты согласования, permissions, self approval, Submit, Cancel и обязательную конфигурацию Workflow автоматическими проверками.

12. **[S10 — чистая установка](stages/S10_CLEAN_INSTALL.md)**  
    Установить App на новый Site и пройти процесс без ручного создания обязательных Role, Workflow State или Workflow.

## Почему порядок именно такой

`Workflow` не появляется в S01, потому что хранить текущее состояние может обычный `Select`.

`Workflow` появляется в S03 только после практического опыта S02:

```text
пользователь имеет Write
→ может изменить обычный status
→ DocPerm отвечает за доступ к Document вообще
→ но не описывает разрешённый маршрут переходов
```

`Is Submittable` не появляется вместе с Workflow, потому что процессное состояние `Approved` и системный `docstatus = 1` — разные вещи. Submit добавляется только в S06, когда появляется требование зафиксировать окончательное решение через системный жизненный цикл Document.

`Cancel` и `Amend` разделены, потому что это разные операции и разные права. Наличие `amended_from` после включения Submittable ещё не означает, что бизнес уже разрешил кому-либо Amend.

Описание модели находится в [`APPLICATION_MODEL.md`](APPLICATION_MODEL.md), а исходные требования — в [`REQUIREMENTS.md`](REQUIREMENTS.md).
