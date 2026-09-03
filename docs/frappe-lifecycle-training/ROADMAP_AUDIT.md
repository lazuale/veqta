# Злой аудит roadmap второго практикума Frappe

Статус: **roadmap прошёл архитектурный аудит с обязательными коррекциями перед executable specification**.

Этот документ проверяет [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md) по фактической семантике Frappe v16.33.0.

До финальной консолидации он имеет приоритет там, где явно корректирует roadmap, matrix или ранний architecture layer.

Нормативная база:

- [`ARCHITECTURE_CORRECTIONS.md`](ARCHITECTURE_CORRECTIONS.md);
- [`docs/frappe-architecture-standard`](../frappe-architecture-standard/README.md);
- [`13_ROLE_PROVISIONING.md`](../frappe-architecture-standard/13_ROLE_PROVISIONING.md).

Первичные source checks Frappe v16.33.0:

- `frappe/model/workflow.py`;
- `frappe/workflow/doctype/workflow_transition/workflow_transition.json`;
- `frappe/workflow/doctype/workflow_action/workflow_action.py`;
- `frappe/public/js/frappe/model/workflow.js`;
- `frappe/public/js/frappe/form/workflow.js`;
- `frappe/public/js/frappe/form/form.js`;
- `frappe/public/js/frappe/model/create_new.js`;
- `frappe/utils/fixtures.py`.

---

# 1. Итог аудита

Stage structure сохраняется:

```text
S00
S01
S02
S03
S04
S05
S06
S07A
S07B
S08
S09
S10
```

Ни один этап не удаляется и новый обязательный этап не добавляется.

Но executable specification обязана учесть найденные ниже коррекции.

---

# 2. CORRECTION R-A01 — `allow_self_approval` является свойством каждого transition

Ранее self-approval policy была слишком легко читаема как одноразовая настройка этапа S04.

В текущем Frappe `apply_workflow()` вызывает:

```text
has_approval_access(user, doc, transition)
```

для **каждого** Workflow transition.

При этом `Workflow Transition.allow_self_approval` имеет default:

```text
1
```

Следовательно, policy нужно принимать **на каждой новой transition row**, а не один раз «для Workflow вообще».

## CORE policy

Пока `requester = owner`, owner обязан сам выполнять свои пользовательские transitions:

```text
PR Draft
→ Submit for Review
→ PR Pending Manager

PR Rejected
→ Submit for Review
→ PR Pending Manager
```

Для них:

```text
allow_self_approval = yes
```

Иначе Requester не сможет отправлять собственную заявку.

Для approval transitions действует separation of duties:

```text
Pending Manager → Approved
Pending Manager → Pending Senior
Pending Senior  → Approved
```

Для них:

```text
allow_self_approval = no
```

То есть после S05 новая Senior branch **обязана унаследовать policy S04**. Нельзя оставить новый Senior approval transition с default `yes`.

Для non-approval transition `Approved → Cancelled` текущий CORE не выводит запрет из self-approval requirement автоматически. Его значение задаётся осознанно в executable specification вместе с Cancel responsibility; оно не наследуется случайно от approval transitions.

## Обязательные tests

```text
owner + Purchase Approver
→ не может final approve собственную маленькую заявку

owner + Purchase Approver
→ не может выполнить first-level approval собственной большой заявки

owner + Senior Purchase Approver
→ не может final approve собственную большую заявку

owner + Purchase Requester
→ может Submit for Review
→ может resubmit после Rejected
```

Архитектурный вывод:

```text
Allow Self Approval
→ transition-level policy

не
→ глобальный ACL-флаг Workflow
```

---

# 3. CORRECTION R-A02 — `status.No Copy = yes` должен появиться вместе с Workflow

`REQUIREMENTS_MATRIX` уже содержит правильное решение, но roadmap S03 его потерял.

Когда Standard:

```text
status : Select
```

становится:

```text
Workflow State Field = status
```

в S03 одновременно фиксируется:

```text
No Copy = yes
```

Это соответствует семантике process-state field и универсальному fallback Workflow field Frappe.

Не создавать второе поле `workflow_state`.

`No Copy` не используется как объяснение Amend: `copy_doc(..., from_amend=true)` намеренно не применяет обычный `no_copy` filter.

---

# 4. CORRECTION R-A03 — Senior получает минимальный базовый DocPerm до Submit

S05 не должен оставлять permission flags Senior на усмотрение ученика.

При появлении `Senior Purchase Approver` baseline до Submittable:

| Right | Value |
|---|---:|
| Read | yes |
| Create | no |
| Write | yes |
| Delete | no |
| Submit | no |
| Cancel | no |
| Amend | no |

Почему нужен `Write`:

пока final states ещё имеют `docstatus 0`, `apply_workflow()` для draft→draft transition сохраняет Document обычным `save()` path.

Только в S06 появляется:

```text
Submit = yes
```

для final approvers.

Не выдавать Senior Create/Delete/Cancel/Amend без отдельного требования.

---

# 5. CORRECTION R-A04 — S06 обязан очистить несовместимые disposable dev records

До S06 существовало учебное состояние:

```text
PR Approved
→ docstatus 0
```

В S06 contract меняется:

```text
PR Approved
→ docstatus 1
```

Если на dev-site оставить старые `PR Approved` Documents с `docstatus 0`, data перестаёт соответствовать новой state mapping.

Поэтому **до изменения mapping** executable S06 обязан:

1. найти учебные Purchase Requests, созданные в предыдущих этапах;
2. убедиться, что это disposable training data;
3. удалить/пересоздать несовместимые контрольные записи обычным Document path;
4. затем включить `Is Submittable` и изменить mapping;
5. создать новые контрольные Documents уже через новый lifecycle.

Запрещено делать ради учебных записей:

```text
ручной SQL UPDATE docstatus
фиктивный production patch
ignore workflow consistency
```

Если существовала бы поддерживаемая предыдущая production-версия с реальными данными, это уже была бы настоящая migration responsibility из GATE.

---

# 6. CORRECTION R-A05 — `Only Allow Edit For` не является server immutability

Source audit подтверждает:

```text
frappe.workflow.is_read_only()
```

использует `Workflow Document State.allow_edit` в Desk.

Но обычный server permission engine остаётся основан на DocPerm, а `validate_workflow()` проверяет допустимость смены state; он не превращает `allow_edit` в самостоятельный server-side запрет изменения любых полей при сохранении в том же state.

Следовательно, текущий CORE обещает только:

```text
Only Allow Edit For
→ Desk/state edit policy
```

а не:

```text
Requester физически не может изменить Pending Manager через любой server path
```

Это важно потому, что Requester baseline имеет `Write = yes`.

## Новый GATE, но не новый CORE stage

Если появляется требование:

> После Submit for Review Requester не может менять сумму/назначение до Reject независимо от Desk/API/server path.

то возникает отдельная ответственность:

```text
server-side state-dependent immutability
```

и проводится новый fit analysis. Нельзя считать, что `Only Allow Edit For` уже решил эту задачу.

Текущий roadmap не расширяется этим механизмом без требования.

---

# 7. CORRECTION R-A06 — Workflow Action подтверждён как runtime queue без email prerequisite

S03 оставляется как есть по структуре.

В v16.33.0 `process_workflow_actions()`:

1. получает следующие допустимые transitions;
2. собирает их allowed roles;
3. создаёт `Workflow Action` с `permitted_roles`;
4. email отправляет только дополнительной веткой, если включены email settings.

Следовательно:

```text
Workflow Action
→ естественный runtime result Workflow
```

и для его появления CORE не обязан включать email alerts.

Граница сохраняется:

```text
Workflow Action permitted_roles
≠ окончательная user-level transition authorization
```

потому что фактический `apply_workflow()` отдельно проверяет self policy.

---

# 8. CORRECTION R-A07 — Amend path теперь имеет source-backed ожидание

Ранее roadmap правильно требовал наблюдать native Amend, не выдумывая workaround.

Source audit уточнил ожидаемый Desk path.

`copy_doc(..., from_amend=true)`:

```text
копирует business fields,
не применяет обычный no_copy filter,
ставит docstatus = 0,
ставит нового owner
```

поэтому скопированный `status` сначала действительно может содержать `PR Cancelled`.

Но новый Document является `__islocal`, а `frappe.ui.form.States.refresh()` для local Document вызывает:

```text
set_default_state()
```

и устанавливает первый Workflow State с соответствующим:

```text
docstatus = 0
```

В нашей модели это должен быть:

```text
PR Draft
```

Поэтому ожидаемый Desk Amend path:

```text
Cancelled original
→ Amend
→ local new Document docstatus 0
→ Workflow default state PR Draft
→ amended_from = original
```

Acceptance всё равно остаётся обязательной: практикум проверяет реальный результат на pinned Frappe v16.33.0.

---

# 9. CORRECTION R-A08 — `Cancelled.allow_edit` нужен только как Desk prerequisite Amend

`Only Allow Edit For` не становится server ACL, но в Desk он влияет на `frappe.workflow.is_read_only()`.

Toolbar `can_amend()` требует одновременно:

```text
docstatus == 2
Amend permission
form not read_only
```

Поэтому после появления S07B текущая Desk policy должна позволить Requester открыть native Amend action на Cancelled Document.

Это объясняет эволюцию:

```text
S07A
Cancelled edit role → Purchase Approver

S07B
Cancelled edit role → Purchase Requester
```

не как server-security rule, а как часть ожидаемого Desk Amend scenario.

---

# 10. CORRECTION R-A09 — naming второго DocType не должен стать случайным

Второй практикум не переучивает naming заново, но новый самостоятельный `Purchase Request` всё равно имеет Document identity.

Executable specification S01 обязана **переиспользовать** решение первого CORE:

```text
осознанно выбрать naming strategy
+
при необходимости Title Field
```

Это checkpoint применения уже изученного принципа, а не новый учебный модуль.

Точную naming expression фиксирует executable specification.

---

# 11. CORRECTION R-A10 — `PR-*` пока является provisional namespace

Ранние документы называют:

```text
PR Draft
PR Pending Manager
...
```

App-scoped Workflow State names.

Но второй App ещё не получил окончательное имя.

Поэтому до executable specification `PR-*` считается **provisional domain prefix**, а не доказанной глобально безопасной App namespace.

Executable specification сначала фиксирует App identifier, затем принимает окончательные persisted Workflow State names.

Требование сохраняется:

```text
Workflow State names
→ не должны случайно конфликтовать с чужим App на одном Site
```

Короткие `Draft / Approved / ...` остаются только diagram aliases.

---

# 12. Подтверждённые решения без изменений

Аудит подтвердил:

```text
✓ один Standard status остаётся Workflow State Field
✓ второй mandatory workflow_state Custom Field не нужен
✓ Role fixtures не нужны базовым ролям из Standard DocPerm
✓ Workflow State fixtures должны импортироваться раньше Workflow fixture
✓ fixture_auto_order действительно добавляет sortable numeric prefixes
✓ Approved 1 → Cancelled 2 не требует status.Allow on Submit
✓ Submit / Cancel / Amend являются разными permission responsibilities
✓ amended_from создаёт Framework при Is Submittable
✓ S04 и S05 остаются параллельными архитектурными ветками; их порядок методический
✓ NEXT не является prerequisite CORE
```

---

# 13. Roadmap после аудита

Stage map не меняется:

```text
S00  second App/Site
S01  Purchase Request + owner + plain status + inherited naming checkpoint
S02  base DocPerm + negative plain-status proof
S03  base Workflow + No Copy + Workflow Action + Reject/Resubmit
S04  transition-level self-approval policy for existing approval path
S05  Senior branch + minimal Senior DocPerm + self-policy on every new approval transition
S06  disposable-data reset + Is Submittable + Submit
S07A Cancel
S07B Amend + Cancelled Desk edit policy for Requester
S08  App-owned delivery
S09  server contracts + observed/UI checks
S10  clean Site acceptance
```

---

# 14. Дополнение к test contract S09

Кроме уже перечисленных tests обязательны:

```text
Requester owner can Submit for Review
Requester owner can resubmit after Rejected

Requester + Approver owner cannot self approve small request
Requester + Approver owner cannot first-level approve own large request
Requester + Senior owner cannot final approve own large request

Senior before S06 has Read+Write but no Create/Delete/Submit/Cancel/Amend
Senior after S06 gets Submit and still no Create/Delete/Cancel/Amend

status.no_copy == 1 after S03

old dev Approved/docstatus0 records are not carried through S06 as valid control data
```

Observed checks additionally prove:

```text
Workflow Action exists without enabling email
Cancelled + Requester Amend permission + Cancelled allow_edit
→ native Amend action is available in Desk

native Amend
→ new docstatus 0
→ initial workflow state
→ amended_from original
```

---

# 15. Gate result

После этих corrections roadmap считается **пригодным основанием для `CORE_STAGE_SPECIFICATION`**.

Запрещено начинать executable specification по одному `PRACTICUM_ROADMAP.md`, игнорируя этот audit.

Правильный вход следующего слоя:

```text
ARCHITECTURE_CORRECTIONS
+
ARCHITECTURE_PASSPORT
+
REQUIREMENTS_MATRIX
+
STAGE_DEPENDENCY_GRAPH
+
PRACTICUM_ROADMAP
+
ROADMAP_AUDIT
↓
CORE_STAGE_SPECIFICATION
```
