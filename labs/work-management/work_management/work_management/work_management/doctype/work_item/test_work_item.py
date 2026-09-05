from __future__ import annotations

import frappe
from frappe.tests import IntegrationTestCase


class TestWorkItem(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.root = self.make_work_unit("WM Test Root", is_group=1)
		self.unit_a = self.make_work_unit("WM Test Unit A", parent=self.root.name)
		self.unit_b = self.make_work_unit("WM Test Unit B", parent=self.root.name)
		self.work_type = self.make_work_type("WM Test Type", default_priority="High")

	def tearDown(self):
		frappe.set_user("Administrator")

	def make_work_unit(self, unit_name, *, parent=None, is_group=0, active=1):
		return frappe.get_doc(
			{
				"doctype": "Work Unit",
				"unit_name": unit_name,
				"parent_work_unit": parent,
				"is_group": is_group,
				"active": active,
			}
		).insert()

	def make_work_type(self, type_name, *, default_priority=None, active=1):
		return frappe.get_doc(
			{
				"doctype": "Work Type",
				"type_name": type_name,
				"active": active,
				"default_priority": default_priority,
			}
		).insert()

	def make_work_item(self, **values):
		values.setdefault("subject", "Synthetic Work Item")
		values.setdefault("work_type", self.work_type.name)
		values.setdefault("responsible_unit", self.unit_a.name)
		return frappe.get_doc({"doctype": "Work Item", **values}).insert()

	def make_user(self, email, *roles):
		if frappe.db.exists("User", email):
			user = frappe.get_doc("User", email)
			user.enabled = 1
			user.save(ignore_permissions=True)
		else:
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": "WM Test",
					"enabled": 1,
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

		if roles:
			user.add_roles(*roles)
		return user

	def allow_work_unit(self, user, work_unit, *, hide_descendants=0):
		return frappe.get_doc(
			{
				"doctype": "User Permission",
				"user": user.name,
				"allow": "Work Unit",
				"for_value": work_unit,
				"apply_to_all_doctypes": 1,
				"hide_descendants": hide_descendants,
			}
		).insert(ignore_permissions=True)

	def test_due_at_cannot_precede_planned_start(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(
				planned_start="2026-09-05 12:00:00",
				due_at="2026-09-05 11:59:59",
			)

	def test_waiting_requires_reason(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(status="Waiting")

	def test_duplicate_source_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(
				sources=[
					{"source_doctype": "Work Type", "source_name": self.work_type.name},
					{"source_doctype": "Work Type", "source_name": self.work_type.name},
				]
			)

	def test_duplicate_reference_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(
				references=[
					{"reference_doctype": "Work Type", "reference_name": self.work_type.name},
					{"reference_doctype": "Work Type", "reference_name": self.work_type.name},
				]
			)

	def test_inactive_work_type_cannot_be_newly_assigned(self):
		inactive = self.make_work_type("WM Inactive Type", active=0)
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(work_type=inactive.name)

	def test_existing_inactive_work_type_does_not_invalidate_unrelated_edit(self):
		item = self.make_work_item()
		self.work_type.active = 0
		self.work_type.save()
		item.subject = "Edited after type deactivation"
		item.save()

	def test_inactive_work_unit_cannot_be_newly_assigned(self):
		inactive = self.make_work_unit("WM Inactive Unit", active=0)
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(responsible_unit=inactive.name)

	def test_existing_inactive_work_unit_does_not_invalidate_unrelated_edit(self):
		item = self.make_work_item()
		self.unit_a.active = 0
		self.unit_a.save()
		item.subject = "Edited after unit deactivation"
		item.save()

	def test_disabled_user_cannot_be_newly_assigned(self):
		user = self.make_user("wm-disabled@example.com", "Work User")
		user.enabled = 0
		user.save(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(assignee=user.name)

	def test_work_type_priority_default_is_copied(self):
		item = self.make_work_item()
		self.assertEqual(item.priority, "High")

		self.work_type.default_priority = "Urgent"
		self.work_type.save()

		item.subject = "Priority remains historical"
		item.save()
		self.assertEqual(item.priority, "High")

	def test_explicit_priority_wins_over_work_type_default(self):
		item = self.make_work_item(priority="Low")
		self.assertEqual(item.priority, "Low")

	def test_medium_is_fallback_priority(self):
		plain_type = self.make_work_type("WM Type Without Priority")
		item = self.make_work_item(work_type=plain_type.name)
		self.assertEqual(item.priority, "Medium")

	def test_started_at_is_first_start_only(self):
		item = self.make_work_item()
		item.status = "In Progress"
		item.save()
		first_started_at = item.started_at
		self.assertTrue(first_started_at)

		item.status = "Open"
		item.save()
		item.status = "In Progress"
		item.save()
		self.assertEqual(item.started_at, first_started_at)

	def test_waiting_since_and_reason_are_current_state(self):
		item = self.make_work_item()
		item.status = "Waiting"
		item.waiting_reason = "Synthetic external dependency"
		item.save()
		self.assertTrue(item.waiting_since)

		item.status = "In Progress"
		item.save()
		self.assertIsNone(item.waiting_since)
		self.assertFalse(item.waiting_reason)

	def test_terminal_status_sets_closed_at_and_reopen_clears_it(self):
		item = self.make_work_item()
		item.status = "Done"
		item.save()
		self.assertTrue(item.closed_at)

		item.status = "Open"
		item.save()
		self.assertIsNone(item.closed_at)

		item.status = "Cancelled"
		item.save()
		self.assertTrue(item.closed_at)

	def test_dynamic_reference_requires_read_permission_on_new_target(self):
		hidden_item = self.make_work_item(responsible_unit=self.unit_b.name)
		user = self.make_user("wm-reference@example.com", "Work User")
		self.allow_work_unit(user, self.unit_a.name)

		frappe.set_user(user.name)
		with self.assertRaises(frappe.PermissionError):
			self.make_work_item(
				references=[
					{
						"reference_doctype": "Work Item",
						"reference_name": hidden_item.name,
					}
				]
			)

	def test_dynamic_source_requires_read_permission_on_new_target(self):
		hidden_item = self.make_work_item(responsible_unit=self.unit_b.name)
		user = self.make_user("wm-source@example.com", "Work User")
		self.allow_work_unit(user, self.unit_a.name)

		frappe.set_user(user.name)
		with self.assertRaises(frappe.PermissionError):
			self.make_work_item(
				sources=[
					{
						"source_doctype": "Work Item",
						"source_name": hidden_item.name,
					}
				]
			)

	def test_existing_dynamic_link_is_not_revalidated_on_unrelated_edit(self):
		hidden_item = self.make_work_item(responsible_unit=self.unit_b.name)
		item = self.make_work_item(
			references=[
				{
					"reference_doctype": "Work Item",
					"reference_name": hidden_item.name,
				}
			]
		)
		user = self.make_user("wm-existing-link@example.com", "Work User")
		self.allow_work_unit(user, self.unit_a.name)

		frappe.set_user(user.name)
		item = frappe.get_doc("Work Item", item.name)
		item.subject = "Unrelated permitted edit"
		item.save()

	def test_work_unit_user_permission_restricts_work_item_read_create_and_move(self):
		item_a = self.make_work_item(responsible_unit=self.unit_a.name)
		item_b = self.make_work_item(responsible_unit=self.unit_b.name)
		user = self.make_user("wm-unit-permission@example.com", "Work User")
		self.allow_work_unit(user, self.unit_a.name)

		frappe.set_user(user.name)
		visible = frappe.get_list("Work Item", pluck="name")
		self.assertIn(item_a.name, visible)
		self.assertNotIn(item_b.name, visible)

		self.make_work_item(subject="Allowed in A", responsible_unit=self.unit_a.name)

		with self.assertRaises(frappe.PermissionError):
			self.make_work_item(subject="Denied in B", responsible_unit=self.unit_b.name)

		item_a = frappe.get_doc("Work Item", item_a.name)
		item_a.responsible_unit = self.unit_b.name
		with self.assertRaises(frappe.PermissionError):
			item_a.save()

	def test_parent_work_unit_permission_covers_descendants(self):
		item_a = self.make_work_item(responsible_unit=self.unit_a.name)
		item_b = self.make_work_item(responsible_unit=self.unit_b.name)
		user = self.make_user("wm-parent-permission@example.com", "Work User")
		self.allow_work_unit(user, self.root.name)

		frappe.set_user(user.name)
		visible = frappe.get_list("Work Item", pluck="name")
		self.assertIn(item_a.name, visible)
		self.assertIn(item_b.name, visible)

	def test_assignee_is_not_an_acl_boundary(self):
		assignee = self.make_user("wm-assignee@example.com", "Work User")
		other = self.make_user("wm-other@example.com", "Work User")
		self.allow_work_unit(assignee, self.unit_a.name)
		self.allow_work_unit(other, self.unit_a.name)
		item = self.make_work_item(assignee=assignee.name)

		frappe.set_user(other.name)
		item = frappe.get_doc("Work Item", item.name)
		item.subject = "Edited by another member of the permitted queue"
		item.save()
