# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WizardRegisterAuditChecklist(models.TransientModel):
    _name = 'register.audit.checklist.wizard'
    _description = _('WizardRegisterAuditChecklist')

    employee_id = fields.Many2one('hr.employee',string="Empleado")
    audit_user_id = fields.Many2one('res.users', string="Auditado por")
    audit_date = fields.Date(string="Fecha de auditoría")
    audit_notes = fields.Html(string="Observaciones")

    def confirm_audit(self):
        for record in self:
            record.employee_id.audit_user_id=record.audit_user_id.id
            record.employee_id.audit_date=record.audit_date
            record.employee_id.audit_notes=record.audit_notes
            record.employee_id.has_audit=True
