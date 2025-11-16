# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_employee_docs = fields.Boolean(
        string="Activar documentos de empleados en OneDrive",
        config_parameter='hr_checklist.enable_employee_docs',
        help="Habilita el uso de una carpeta de OneDrive para almacenar documentos relacionados con los empleados."
    )

    employee_docs_path = fields.Char(
        string="Ruta de carpeta en OneDrive",
        config_parameter='hr_checklist.employee_docs_path',
        help="Especifica la ruta completa de la carpeta en OneDrive donde se almacenarán los documentos de los empleados."
    )

    include_company_employee_docs_path = fields.Boolean(
        string="Incluir nombre de la compañía en la ruta",
        config_parameter='hr_checklist.include_company_employee_docs_path',
        help="Si se activa, se añadirá automáticamente el nombre de la compañía del empleado como subcarpeta en la ruta configurada."
    )

    def set_values(self):
        group_employee = self.env.ref('ind_hr_checklist.group_hr_employee_docs')

        if not self.enable_employee_docs:
            self.employee_docs_path = False
            self.include_company_employee_docs_path = False
            group_employee.write({'users': [(5, 0, 0)]})
        else:
            if not self.employee_docs_path:
                raise ValidationError(_("Debe especificar la ruta completa de la carpeta en OneDrive donde se almacenarán los documentos de los empleados."))
            users = self.env.ref('hr.group_hr_manager').users
            group_employee.write({'users': [(6, 0, users.ids)]})
        
        super().set_values()
            