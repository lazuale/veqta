from __future__ import annotations

import json

import frappe
from frappe.desk.form.assign_to import add as add_assignment
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today


class TestWorkItem(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.root = self.make_work_unit("WM Test Root", is_group=1)
		self.unit_a = self.make_work_unit("WM Test Unit A", parent=self.root.name)
		self.unit_b = self.make_work_unit("WM Test Unit B", parent=self.root.name)
		self.work_type = self.make_work_type("WM Test Type")

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

	def make_work_type(self, type_name, *, active=1):
		return frappe.get_doc(
			{
				"doctype": "Work Type",
				"type_name": type_name,
				"active": active,
			}
		).insert()

	def make_work_item(self, **values):
		values.setdefault("subject", "Synthetic Work Item")
		values.setdefault("work_type", self.work_type.name)
		values.setdefault("responsible_unit", self.unit_a.name)
		values.setdefault("priority", "Medium")
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

	def allow_work_type(self, user, work_type):
		return frappe.get_doc(
			{
				"doctype": "User Permission",
				"user": user.name,
				"allow": "Work Type",
				"for_value": work_type,
				"apply_to_all_doctypes": 1,
			}
		).insert(ignore_permissions=True)

	def ensure_named_document(self, doctype, fieldname, value):
		if frappe.db.exists(doctype, value):
			return frappe.get_doc(doctype, value)
		return frappe.get_doc({"doctype": doctype, fieldname: value}).insert(ignore_permissions=True)

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

	def test_parent_work_item_supports_decomposition(self):
		parent = self.make_work_item(subject="Parent Work")
		child = self.make_work_item(subject="Child Work", parent_work_item=parent.name)
		self.assertEqual(child.parent_work_item, parent.name)

	def test_parent_work_item_rejects_self_reference(self):
		item = self.make_work_item()
		item.parent_work_item = item.name
		with self.assertRaises(frappe.ValidationError):
			item.save()

	def test_parent_work_item_rejects_cycle(self):
		parent = self.make_work_item(subject="Parent")
		child = self.make_work_item(subject="Child", parent_work_item=parent.name)
		parent.parent_work_item = child.name
		with self.assertRaises(frappe.ValidationError):
			parent.save()

	def test_dependencies_reject_duplicate_and_self_reference(self):
		prerequisite = self.make_work_item(subject="Prerequisite")
		with self.assertRaises(frappe.ValidationError):
			self.make_work_item(
				dependencies=[{"depends_on": prerequisite.name}, {"depends_on": prerequisite.name}]
			)

		item = self.make_work_item(subject="Self dependent")
		item.append("dependencies", {"depends_on": item.name})
		with self.assertRaises(frappe.ValidationError):
			item.save()

	def test_dependencies_reject_cycle(self):
		first = self.make_work_item(subject="First")
		second = self.make_work_item(subject="Second", dependencies=[{"depends_on": first.name}])
		first.append("dependencies", {"depends_on": second.name})
		with self.assertRaises(frappe.ValidationError):
			first.save()

	def test_new_parent_and_dependency_require_read_permission(self):
		hidden_item = self.make_work_item(responsible_unit=self.unit_b.name)
		item = self.make_work_item(responsible_unit=self.unit_a.name)
		user = self.make_user("wm-structure-permission@example.com", "Work User")
		self.allow_work_unit(user, self.unit_a.name)

		frappe.set_user(user.name)
		item = frappe.get_doc("Work Item", item.name)
		item.parent_work_item = hidden_item.name
		with self.assertRaises(frappe.PermissionError):
			item.save()

		item = frappe.get_doc("Work Item", item.name)
		item.append("dependencies", {"depends_on": hidden_item.name})
		with self.assertRaises(frappe.PermissionError):
			item.save()

	def test_existing_parent_and_dependency_do_not_revalidate_read_permission(self):
		hidden_parent = self.make_work_item(responsible_unit=self.unit_b.name)
		hidden_dependency = self.make_work_item(responsible_unit=self.unit_b.name)
		item = self.make_work_item(
			responsible_unit=self.unit_a.name,
			parent_work_item=hidden_parent.name,
			dependencies=[{"depends_on": hidden_dependency.name}],
		)
		user = self.make_user("wm-existing-structure@example.com", "Work User")
		self.allow_work_unit(user, self.unit_a.name)

		frappe.set_user(user.name)
		item = frappe.get_doc("Work Item", item.name)
		item.subject = "Unrelated structure edit"
		item.save()

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

	def test_responsible_unit_is_queue_not_default_acl_boundary(self):
		item_a = self.make_work_item(responsible_unit=self.unit_a.name)
		item_b = self.make_work_item(responsible_unit=self.unit_b.name)
		user = self.make_user("wm-queue-user@example.com", "Work User")

		frappe.set_user(user.name)
		visible = frappe.get_list("Work Item", pluck="name")
		self.assertIn(item_a.name, visible)
		self.assertIn(item_b.name, visible)

		item_a = frappe.get_doc("Work Item", item_a.name)
		item_a.responsible_unit = self.unit_b.name
		item_a.save()
		self.assertEqual(item_a.responsible_unit, self.unit_b.name)

	def test_work_type_is_classification_not_user_permission_boundary(self):
		other_type = self.make_work_type("WM Other Type")
		item_a = self.make_work_item(work_type=self.work_type.name)
		item_b = self.make_work_item(work_type=other_type.name)
		user = self.make_user("wm-type-permission@example.com", "Work User")
		self.allow_work_type(user, self.work_type.name)

		frappe.set_user(user.name)
		visible = frappe.get_list("Work Item", pluck="name")
		self.assertIn(item_a.name, visible)
		self.assertIn(item_b.name, visible)

	def test_work_item_uses_native_frappe_assignments(self):
		item = self.make_work_item()
		user_a = self.make_user("wm-assignment-a@example.com", "Work User")
		user_b = self.make_user("wm-assignment-b@example.com", "Work User")

		add_assignment(
			{
				"doctype": "Work Item",
				"name": item.name,
				"assign_to": json.dumps([user_a.name, user_b.name]),
			}
		)

		assigned_users = set(
			frappe.get_all(
				"ToDo",
				filters={
					"reference_type": "Work Item",
					"reference_name": item.name,
					"status": "Open",
				},
				pluck="allocated_to",
			)
		)
		self.assertEqual(assigned_users, {user_a.name, user_b.name})

	def test_auto_repeat_resets_instance_state_but_keeps_template_context(self):
		parent = self.make_work_item(subject="Recurring Parent")
		prerequisite = self.make_work_item(subject="Recurring Prerequisite")
		template = self.make_work_item(
			subject="Recurring Work",
			status="Waiting",
			waiting_reason="Waiting in template instance",
			planned_start="2026-09-06 08:00:00",
			due_at="2026-09-06 18:00:00",
			parent_work_item=parent.name,
			dependencies=[{"depends_on": prerequisite.name}],
			sources=[{"source_doctype": "Work Type", "source_name": self.work_type.name}],
			references=[{"reference_doctype": "Work Type", "reference_name": self.work_type.name}],
		)

		auto_repeat = frappe.get_doc(
			{
				"doctype": "Auto Repeat",
				"reference_doctype": "Work Item",
				"reference_document": template.name,
				"frequency": "Daily",
				"start_date": add_days(today(), 1),
			}
		).insert(ignore_permissions=True)
		repeated = auto_repeat.make_new_document()

		self.assertEqual(repeated.status, "Open")
		self.assertIsNone(repeated.waiting_reason)
		self.assertIsNone(repeated.waiting_since)
		self.assertIsNone(repeated.started_at)
		self.assertIsNone(repeated.closed_at)
		self.assertIsNone(repeated.planned_start)
		self.assertIsNone(repeated.due_at)
		self.assertIsNone(repeated.parent_work_item)
		self.assertFalse(repeated.dependencies)
		self.assertFalse(repeated.sources)
		self.assertEqual(len(repeated.references), 1)
		self.assertEqual(repeated.references[0].reference_name, self.work_type.name)
		self.assertEqual(repeated.work_type, template.work_type)
		self.assertEqual(repeated.responsible_unit, template.responsible_unit)
		self.assertEqual(repeated.priority, template.priority)

	def test_site_workflow_can_update_canonical_status(self):
		for state in ["WM Open", "WM Working", "WM Complete"]:
			self.ensure_named_document("Workflow State", "workflow_state_name", state)
		for action in ["WM Start", "WM Complete"]:
			self.ensure_named_document("Workflow Action Master", "workflow_action_name", action)

		workflow = frappe.get_doc(
			{
				"doctype": "Workflow",
				"workflow_name": "WM Test Work Item Workflow",
				"document_type": "Work Item",
				"workflow_state_field": "workflow_state",
				"is_active": 1,
				"states": [
					{"state": "WM Open", "doc_status": "0", "allow_edit": "System Manager"},
					{
						"state": "WM Working",
						"doc_status": "0",
						"allow_edit": "System Manager",
						"update_field": "status",
						"update_value": "In Progress",
					},
					{
						"state": "WM Complete",
						"doc_status": "0",
						"allow_edit": "System Manager",
						"update_field": "status",
						"update_value": "Done",
					},
				],
				"transitions": [
					{
						"state": "WM Open",
						"action": "WM Start",
						"next_state": "WM Working",
						"allowed": "System Manager",
						"allow_self_approval": 1,
					},
					{
						"state": "WM Working",
						"action": "WM Complete",
						"next_state": "WM Complete",
						"allowed": "System Manager",
						"allow_self_approval": 1,
					},
				],
			}
		).insert(ignore_permissions=True)
		self.assertTrue(workflow.is_active)

		item = self.make_work_item(subject="Workflow Work")
		self.assertEqual(item.status, "Open")
		self.assertEqual(item.workflow_state, "WM Open")

		item = apply_workflow(item, "WM Start")
		self.assertEqual(item.status, "In Progress")
		self.assertTrue(item.started_at)

		item = apply_workflow(item, "WM Complete")
		self.assertEqual(item.status, "Done")
		self.assertTrue(item.closed_at)
