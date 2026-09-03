# S09. Закрепить lifecycle автоматическими tests

К этому этапу процесс уже работает через Desk и его конфигурация принадлежит App.

Новое требование:

> Критические контракты приложения должны проверяться повторяемо одной командой и падать, если Workflow или его permissions сломаны.

Тестируем не «умеет ли Frappe делать Workflow вообще», а нашу конкретную конфигурацию и process semantics.

## 1. Использовать IntegrationTestCase

Тесты создают Documents, переключают пользователей, читают БД и вызывают реальный Workflow path. Это интеграционные тесты.

Для Frappe v16 используйте:

```python
from frappe.tests import IntegrationTestCase
```

Официальная документация: https://docs.frappe.io/framework/user/en/testing

Сам Frappe тестирует Workflow через `IntegrationTestCase` и `apply_workflow()`; см. [`test_workflow.py` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/test_workflow.py).

## 2. Разрешить tests на dev Site

```bash
cd ~/frappe/rental-training-bench

bench --site purchase-lifecycle.localhost set-config allow_tests 1 --parse
bench --site purchase-lifecycle.localhost show-config | grep allow_tests
```

`allow_tests` принадлежит Site и не должен попадать в исходники App.

## 3. Открыть generated test file

При создании Standard `Purchase Request` Frappe уже создал:

```text
apps/purchase_lifecycle_training/
└── purchase_lifecycle_training/
    └── purchase_lifecycle_training/
        └── doctype/
            └── purchase_request/
                └── test_purchase_request.py
```

Сохраните generated copyright/license header и замените содержательную часть следующим минимальным набором.

```python
import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase


class IntegrationTestPurchaseRequest(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        frappe.set_user("Administrator")

        self.requester = self.ensure_user(
            "plt-requester@example.test",
            ["PLT Requester"],
        )
        self.approver = self.ensure_user(
            "plt-approver@example.test",
            ["PLT Approver"],
        )
        self.senior = self.ensure_user(
            "plt-senior@example.test",
            ["PLT Senior Approver"],
        )
        self.dual = self.ensure_user(
            "plt-dual@example.test",
            ["PLT Requester", "PLT Approver", "PLT Senior Approver"],
        )

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()

    def ensure_user(self, email, roles):
        frappe.set_user("Administrator")

        if frappe.db.exists("User", email):
            user = frappe.get_doc("User", email)
        else:
            user = frappe.get_doc(
                {
                    "doctype": "User",
                    "email": email,
                    "first_name": email.split("@", 1)[0],
                    "enabled": 1,
                    "send_welcome_email": 0,
                }
            ).insert()

        user.add_roles(*roles)
        return user.name

    def make_request(self, *, owner=None, amount=500, subject="Test request"):
        owner = owner or self.requester
        frappe.set_user(owner)

        return frappe.get_doc(
            {
                "doctype": "Purchase Request",
                "subject": subject,
                "description": "Automated lifecycle test",
                "requested_amount": amount,
                "needed_by": "2026-12-31",
            }
        ).insert()

    def transition(self, doc, *, user, action):
        frappe.set_user(user)
        return apply_workflow(doc, action)

    def test_small_request_reaches_submitted_approved(self):
        doc = self.make_request(amount=500)

        self.transition(doc, user=self.requester, action="PLT Submit for Review")
        self.assertEqual(doc.status, "PLT Pending Approval")
        self.assertEqual(doc.docstatus, 0)

        self.transition(doc, user=self.approver, action="Approve")
        self.assertEqual(doc.status, "PLT Approved")
        self.assertEqual(doc.docstatus, 1)

    def test_large_request_requires_senior(self):
        doc = self.make_request(amount=1500)

        self.transition(doc, user=self.requester, action="PLT Submit for Review")
        self.transition(doc, user=self.approver, action="Approve")

        self.assertEqual(doc.status, "PLT Pending Senior")
        self.assertEqual(doc.docstatus, 0)

        self.transition(doc, user=self.senior, action="Approve")
        self.assertEqual(doc.status, "PLT Approved")
        self.assertEqual(doc.docstatus, 1)

    def test_owner_cannot_self_approve(self):
        doc = self.make_request(owner=self.dual, amount=500, subject="Self approval")

        self.transition(doc, user=self.dual, action="PLT Submit for Review")

        with self.assertRaises(frappe.ValidationError):
            self.transition(doc, user=self.dual, action="Approve")

        self.assertEqual(doc.status, "PLT Pending Approval")
        self.assertEqual(doc.docstatus, 0)

    def test_reject_can_be_resubmitted(self):
        doc = self.make_request(amount=300, subject="Reject and resubmit")

        self.transition(doc, user=self.requester, action="PLT Submit for Review")
        self.transition(doc, user=self.approver, action="Reject")

        self.assertEqual(doc.status, "PLT Rejected")
        self.assertEqual(doc.docstatus, 0)

        self.transition(doc, user=self.requester, action="PLT Submit for Review")
        self.assertEqual(doc.status, "PLT Pending Approval")

    def test_approved_request_can_be_cancelled_by_approver(self):
        doc = self.make_request(amount=500, subject="Cancel request")

        self.transition(doc, user=self.requester, action="PLT Submit for Review")
        self.transition(doc, user=self.approver, action="Approve")
        self.transition(doc, user=self.approver, action="PLT Cancel Request")

        self.assertEqual(doc.status, "PLT Cancelled")
        self.assertEqual(doc.docstatus, 2)

    def test_required_configuration_exists(self):
        self.assertTrue(frappe.db.exists("Role", "PLT Requester"))
        self.assertTrue(frappe.db.exists("Role", "PLT Approver"))
        self.assertTrue(frappe.db.exists("Role", "PLT Senior Approver"))

        self.assertTrue(
            frappe.db.exists("Workflow", "PLT Purchase Request Approval")
        )

        for state in (
            "PLT Draft",
            "PLT Pending Approval",
            "PLT Rejected",
            "PLT Pending Senior",
            "PLT Approved",
            "PLT Cancelled",
        ):
            self.assertTrue(frappe.db.exists("Workflow State", state))

        for action in ("PLT Submit for Review", "PLT Cancel Request"):
            self.assertTrue(frappe.db.exists("Workflow Action Master", action))

        status = frappe.get_meta("Purchase Request").get_field("status")
        self.assertEqual(status.fieldtype, "Select")
        self.assertTrue(status.no_copy)
        self.assertFalse(status.allow_on_submit)
```

## 4. Почему tests не создают Workflow как fallback

Тесты создают только Site-local test Users и business Documents.

Они **не должны** делать:

```text
если Workflow отсутствует → создать его
если PLT Role отсутствует → создать её
если Workflow State отсутствует → создать его
```

Это обязательная конфигурация App. Если S08 delivery сломан, suite должен упасть, а не тайно восстановить приложение внутри test setup.

## 5. Запустить tests

```bash
cd ~/frappe/rental-training-bench

bench --site purchase-lifecycle.localhost run-tests \
  --app purchase_lifecycle_training
```

Исправляйте причину падения, а не ослабляйте test ради зелёного результата.

## 6. Что проверить отдельно через Desk

Не всё полезно превращать в server integration test.

Отдельно наблюдаем через Desk:

```text
Only Allow Edit For даёт ожидаемое состояние Form
Workflow Action появляется у роли ожидающего действия
Requester видит native Amend для cancelled document
Amend создаёт новый Draft
amended_from указывает на original
```

Особенно важно не выдавать `Only Allow Edit For` за самостоятельную универсальную server immutability. Критические server transitions тестируются через `apply_workflow()`.

## 7. Дополнительные контракты

После базового набора полезно добавить отдельные tests для точных границ:

```text
1000     → direct Approved
1000.01  → Pending Senior
Requester не может Approve
owner не может first-level approve собственной большой заявки
owner не может Senior-approve собственной большой заявки
PLT Requester не получает Cancel
PLT Senior Approver не получает Cancel
PLT Requester имеет Amend
Approver/Senior не получают Amend
```

Добавляйте их как самостоятельные методы с одним понятным контрактом на test.

## Результат

После S09 критический lifecycle можно проверить одной командой:

```text
изменили обязательный Workflow или permissions неправильно
→ tests красные
```

Следующий этап: [`S10_CLEAN_INSTALL.md`](S10_CLEAN_INSTALL.md).
