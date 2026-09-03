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
self-approval policy
  ↓
условный второй уровень
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
   Создать минимальный Standard DocType, naming, owner-semantics и обычный `status : Select` без Workflow.

3. **[S02 — доступ и граница plain status](stages/S02_PERMISSIONS_AND_STATUS_LIMIT.md)**  
   Добавить `PLT Requester` и `PLT Approver`, настроить DocPerm и руками доказать, что обычный `Write` не выражает допустимость конкретного перехода состояния.

4. **[S03 — базовый Workflow](stages/S03_BASIC_WORKFLOW.md)**  
   Сделать существующий `status` Workflow State Field, добавить отправку на согласование, Approve, Reject, повторную отправку и наблюдение `Workflow Action`.

5. **[S04 — запрет self approval](stages/S04_SELF_APPROVAL.md)**  
   Использовать штатный `Allow Self Approval` для запрета одобрения собственной заявки dual-role пользователем.

6. **[S05 — условный Senior approval](stages/S05_CONDITIONAL_APPROVAL.md)**  
   Для суммы больше `1000` добавить `PLT Senior Approver` и второй уровень Workflow через transition conditions.

7. **[S06 — окончательное согласование как Submitted fact](stages/S06_SUBMITTABLE.md)**  
   Включить `Is Submittable`, перевести `PLT Approved` в `docstatus = 1` и выдать минимальные Submit permissions.

8. **[S07A — Cancel](stages/S07A_CANCEL.md)**  
   Добавить официальный путь `Approved → Cancelled` с `docstatus = 2` и отдельным Cancel permission.

9. **[S07B — Amend](stages/S07B_AMEND.md)**  
   Разрешить заявителю создавать исправленную draft-версию отменённого документа через штатный Amend path.

10. **[S08 — поставка lifecycle-конфигурации](stages/S08_APP_STATE_DELIVERY.md)**  
    Разобрать, что уже поставляется Standard metadata, а что нужно экспортировать filtered fixtures.

11. **[S09 — автоматические контракты](stages/S09_AUTOMATED_TESTS.md)**  
    Закрепить маршруты согласования, permissions, self approval, Submit, Cancel и конфигурацию Workflow автоматическими tests.

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

`Is Submittable` не появляется вместе с Workflow, потому что процессное состояние `Approved` и системный `docstatus = 1` — разные вещи. Submit добавляется только в S06, когда появляется требование зафиксировать окончательное решение как транзакционный факт.

`Cancel` и `Amend` разделены, потому что это разные операции и разные права. Наличие `amended_from` после включения Submittable ещё не означает, что бизнес уже разрешил кому-либо Amend.

Описание итоговой модели находится в [`APPLICATION_MODEL.md`](APPLICATION_MODEL.md), а исходные требования — в [`REQUIREMENTS.md`](REQUIREMENTS.md).
