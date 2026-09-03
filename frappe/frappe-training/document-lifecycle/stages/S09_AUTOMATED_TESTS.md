# S09. Закрепить правила процесса автоматическими тестами

К этому этапу процесс уже работает через Desk, а его обязательная конфигурация поставляется вместе с App.

Новое требование:

> Критические правила приложения должны проверяться повторяемо одной командой и явно падать, если Workflow или permissions сломаны.

Тестируем не стандартную способность Frappe выполнять Workflow, а нашу конкретную конфигурацию и ожидаемые переходы `Purchase Request`.

---

# 1. Использовать IntegrationTestCase

Тесты создают Documents, переключают пользователей, читают БД и выполняют реальные переходы Workflow. Это интеграционные тесты.

Для Frappe v16 используйте:

```python
from frappe.tests import IntegrationTestCase
```

Официальная документация: https://docs.frappe.io/framework/user/en/testing

Сам Frappe тестирует Workflow через `IntegrationTestCase` и `apply_workflow()`; см. [`test_workflow.py` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/workflow/doctype/workflow/test_workflow.py).

---

# 2. Разрешить запуск тестов на dev Site

```bash
cd ~/frappe/rental-training-bench

bench --site purchase-lifecycle.localhost set-config allow_tests 1 --parse
bench --site purchase-lifecycle.localhost show-config | grep allow_tests
```

`allow_tests` принадлежит Site и не должен попадать в исходники App.

---

# 3. Открыть файл тестов Purchase Request

При создании Standard `Purchase Request` Frappe уже создал:

```text
apps/purchase_lifecycle_training/
└── purchase_lifecycle_training/
    └── purchase_lifecycle_training/
        └── doctype/
            └── purchase_request/
                └── test_purchase_request.py
```

Сохраните существующий copyright/license header и замените содержательную часть следующим минимальным набором.

```python
import frappe
from frappe.model.workflow import apply_workflow
from frappe.permissions import has_permission
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
                    "user_type": "System User",
                }
            ).insert()

        user.add_roles(*roles)
        frappe.clear_cache(user=user.name)
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

    def test_required_permissions(self):
        expected = {
            self.requester: {
                "read": True,
                "create": True,
                "write": True,
                "delete": False,
                "submit": False,
                "cancel": False,
                "amend": True,
            },
            self.approver: {
                "read": True,
                "create": False,
                "write": True,
                "delete": False,
                "submit": True,
                "cancel": True,
                "amend": False,
            },
            self.senior: {
                "read": True,
                "create": False,
                "write": True,
                "delete": False,
                "submit": True,
                "cancel": False,
                "amend": False,
            },
        }

        for user, permissions in expected.items():
            for ptype, allowed in permissions.items():
                self.assertEqual(
                    bool(
                        has_permission(
                            "Purchase Request",
                            ptype=ptype,
                            user=user,
                            print_logs=False,
                        )
                    ),
                    allowed,
                    msg=f"{user}: expected {ptype}={allowed}",
                )

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

Проверка `test_required_permissions()` закрепляет именно итоговую модель прав нашего App. Она должна падать не только при потере нужного права, но и если роль случайно получает лишний `Submit`, `Cancel`, `Amend`, `Create` или `Delete`.

Для проверки используется штатный `frappe.permissions.has_permission()`. В v16.33.0 он принимает `doctype`, тип права и пользователя и проверяет Role Permission System для указанного DocType.

Источник: [`frappe/permissions.py` v16.33.0](https://github.com/frappe/frappe/blob/v16.33.0/frappe/permissions.py).

---

# 4. Тесты не должны восстанавливать обязательную конфигурацию

Тесты создают только тестовых Users и рабочие Documents, которые нужны конкретной проверке.

Они **не должны** делать:

```text
если Workflow отсутствует → создать его
если PLT Role отсутствует → создать её
если Workflow State отсутствует → создать его
```

Это обязательная конфигурация App. Если поставка состояния из S08 сломана, тест должен упасть, а не тайно восстановить недостающую настройку внутри `setUp()`.

---

# 5. Запустить тесты

```bash
cd ~/frappe/rental-training-bench

bench --site purchase-lifecycle.localhost run-tests \
  --app purchase_lifecycle_training
```

Исправляйте причину падения, а не ослабляйте проверку ради зелёного результата.

---

# 6. Что проверить отдельно через Desk

Не каждое поведение интерфейса нужно превращать в интеграционный тест.

Отдельно проверьте через Desk:

```text
Only Allow Edit For даёт ожидаемое состояние Form
Workflow Action появляется у роли ожидающего действия
Requester видит штатный Amend для Cancelled Document
Amend создаёт новый Draft
amended_from указывает на исходную заявку
```

`Only Allow Edit For` не является самостоятельной универсальной серверной защитой полей. Критические переходы Workflow проверяются через `apply_workflow()`.

---

# 7. Дополнительные проверки

После базового набора полезно добавить отдельные тесты для точных границ процесса:

```text
1000     → PLT Approved
1000.01  → PLT Pending Senior
Requester не может Approve
owner не может одобрить собственную большую заявку на первом уровне
owner не может одобрить собственную большую заявку на втором уровне
```

Права `Create / Write / Submit / Cancel / Amend / Delete` уже входят в обязательный `test_required_permissions()` и не должны оставаться только дополнительными проверками.

Каждый дополнительный test method должен проверять одно понятное правило приложения.

---

# Результат

После S09 критические правила процесса можно проверить одной командой:

```text
сломали обязательный Workflow или permissions
→ автоматические тесты падают
```

Следующий этап: [`S10_CLEAN_INSTALL.md`](S10_CLEAN_INSTALL.md).
