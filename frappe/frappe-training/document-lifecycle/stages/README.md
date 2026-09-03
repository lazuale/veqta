# Этапы практикума

Этапы выполняются последовательно. Каждый следующий шаг использует состояние App, полученное на предыдущем.

| Этап | Результат |
|---|---|
| [S00](S00_APP_AND_SITE.md) | создан отдельный `purchase_lifecycle_training` и dev Site |
| [S01](S01_PURCHASE_REQUEST.md) | создан обычный `Purchase Request` с обычным `status` |
| [S02](S02_PERMISSIONS_AND_STATUS_LIMIT.md) | настроены базовые роли и DocPerm, доказана граница обычного `status` |
| [S03](S03_BASIC_WORKFLOW.md) | настроен базовый Workflow с Reject, повторной отправкой и Workflow Action |
| [S04](S04_SELF_APPROVAL.md) | запрещено одобрение собственной заявки через `Allow Self Approval` |
| [S05](S05_CONDITIONAL_APPROVAL.md) | добавлен второй уровень согласования для суммы больше `1000` |
| [S06](S06_SUBMITTABLE.md) | окончательное согласование переводит Document в `docstatus = 1` |
| [S07A](S07A_CANCEL.md) | добавлена штатная отмена согласованной заявки |
| [S07B](S07B_AMEND.md) | создаётся новая версия отменённой заявки через Amend |
| [S08](S08_APP_STATE_DELIVERY.md) | обязательная Workflow-конфигурация поставляется вместе с App |
| [S09](S09_AUTOMATED_TESTS.md) | критические правила процесса закреплены автоматическими тестами |
| [S10](S10_CLEAN_INSTALL.md) | процесс воспроизводится на новом чистом Site |

Практикум предполагает, что первое приложение уже пройдено. Если непонятны Bench, Site, App, Module, Standard DocType, developer mode, controller, permissions или `migrate`, сначала вернитесь к [`../../first-app/`](../../first-app/README.md).
