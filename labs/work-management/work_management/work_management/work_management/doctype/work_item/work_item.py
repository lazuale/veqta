from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.permissions import has_permission
from frappe.utils import get_datetime, now_datetime


TERMINAL_STATUSES = {"Done", "Cancelled"}


class WorkItem(Document):
	def before_validate(self):
		self.set_priority_default()
		self.update_lifecycle_state()

	def validate(self):
		self.validate_dates()
		self.validate_waiting_state()
		self.validate_unique_links("sources", "source_doctype", "source_name")
		self.validate_unique_links("references", "reference_doctype", "reference_name")
		self.validate_active_link("work_type", "Work Type")
		self.validate_active_link("responsible_unit", "Work Unit")
		self.validate_new_dynamic_links("sources", "source_doctype", "source_name")
		self.validate_new_dynamic_links("references", "reference_doctype", "reference_name")

	def set_priority_default(self):
		if self.priority:
			return

		default_priority = None
		if self.work_type:
			default_priority = frappe.db.get_value("Work Type", self.work_type, "default_priority")

		self.priority = default_priority or "Medium"

	def update_lifecycle_state(self):
		previous = self.get_doc_before_save()
		previous_status = previous.status if previous else None

		if previous and previous.started_at:
			self.started_at = previous.started_at
		elif self.status == "In Progress":
			self.started_at = now_datetime()
		else:
			self.started_at = None

		if self.status == "Waiting":
			if previous_status == "Waiting" and previous and previous.waiting_since:
				self.waiting_since = previous.waiting_since
			else:
				self.waiting_since = now_datetime()
		else:
			self.waiting_since = None
			self.waiting_reason = None

		if self.status in TERMINAL_STATUSES:
			if previous_status in TERMINAL_STATUSES and previous and previous.closed_at:
				self.closed_at = previous.closed_at
			else:
				self.closed_at = now_datetime()
		else:
			self.closed_at = None

	def validate_dates(self):
		if (
			self.planned_start
			and self.due_at
			and get_datetime(self.due_at) < get_datetime(self.planned_start)
		):
			frappe.throw(_("Due At cannot be earlier than Planned Start."))

	def validate_waiting_state(self):
		if self.status == "Waiting" and not (self.waiting_reason or "").strip():
			frappe.throw(_("Waiting Reason is required while Work Item is Waiting."))

	def validate_unique_links(self, table_field, doctype_field, name_field):
		seen = set()
		for row in self.get(table_field) or []:
			if not row.get(doctype_field) or not row.get(name_field):
				continue

			key = (row.get(doctype_field), row.get(name_field))
			if key in seen:
				frappe.throw(
					_("Duplicate {0}: {1} {2}.").format(
						_(table_field), frappe.bold(key[0]), frappe.bold(key[1])
					)
				)
			seen.add(key)

	def validate_active_link(self, fieldname, doctype):
		value = self.get(fieldname)
		if not value or not self.has_value_changed(fieldname):
			return

		active = frappe.db.get_value(doctype, value, "active")
		if active is None:
			return
		if not active:
			frappe.throw(_("{0} {1} is inactive.").format(_(doctype), frappe.bold(value)))

	def validate_new_dynamic_links(self, table_field, doctype_field, name_field):
		if self.flags.ignore_permissions:
			return

		previous = self.get_doc_before_save()
		previous_pairs = {
			(row.get(doctype_field), row.get(name_field))
			for row in (previous.get(table_field) if previous else [])
			if row.get(doctype_field) and row.get(name_field)
		}

		for row in self.get(table_field) or []:
			target_doctype = row.get(doctype_field)
			target_name = row.get(name_field)
			if not target_doctype or not target_name:
				continue

			key = (target_doctype, target_name)
			if key in previous_pairs:
				continue

			# Link/Dynamic Link existence is validated by Frappe itself. Only enforce
			# the additional Work Management contract when a real target exists.
			if not frappe.db.exists(target_doctype, target_name):
				continue

			if not has_permission(target_doctype, "read", doc=target_name, print_logs=False):
				frappe.throw(
					_("You need read permission on {0} {1} to link it to this Work Item.").format(
						_(target_doctype), frappe.bold(target_name)
					),
					frappe.PermissionError,
				)
