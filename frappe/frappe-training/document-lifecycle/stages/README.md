# Этапы практикума

Этапы выполняются последовательно. Каждый следующий шаг использует состояние App, полученное на предыдущем.

| Этап | Результат |
|---|---|
| [S00](S00_APP_AND_SITE.md) | отдельный `purchase_lifecycle_training` и dev Site |
| [S01](S01_PURCHASE_REQUEST.md) | обычный `Purchase Request` и plain `status` |
| [S02](S02_PERMISSIONS_AND_STATUS_LIMIT.md) | базовые роли/DocPerm и доказанная граница plain status |
| [S03](S03_BASIC_WORKFLOW.md) | базовый Workflow, Reject/Resubmit и Workflow Action |
| [S04](S04_SELF_APPROVAL.md) | запрет self approval штатной transition policy |
| [S05](S05_CONDITIONAL_APPROVAL.md) | условный второй уровень для суммы больше `1000` |
| [S06](S06_SUBMITTABLE.md) | final approval становится `docstatus = 1` |
| [S07A](S07A_CANCEL.md) | официальный Cancel path |
| [S07B](S07B_AMEND.md) | исправленная версия через Amend |
| [S08](S08_APP_STATE_DELIVERY.md) | Workflow-конфигурация поставляется вместе с App |
| [S09](S09_AUTOMATED_TESTS.md) | критические lifecycle-контракты закреплены tests |
| [S10](S10_CLEAN_INSTALL.md) | процесс воспроизводится на новом чистом Site |

Практикум предполагает, что первое приложение уже пройдено. Если непонятны Bench, Site, App, Module, Standard DocType, developer mode, controller, permissions или `migrate`, сначала вернитесь к [`../../first-app/`](../../first-app/README.md).
