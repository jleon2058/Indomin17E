from odoo import models, fields
from odoo.exceptions import UserError
from zoneinfo import ZoneInfo
from datetime import datetime, time


class ReportRFQApprovedWizard(models.TransientModel):
    _name = 'report.rfq.approved.wizard'
    _description = ''


    date_start = fields.Date(
        string='Fecha de inicio',
        required=True,
    )
    date_end = fields.Date(
        string='Fecha de fin',
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    file_data = fields.Binary(string='Archivo Excel', readonly=True)

    def action_generate_report(self):
        user_tz = self.env.user.tz or 'UTC'

        start_datetime = datetime.combine(self.date_start, time.min)
        end_datetime = datetime.combine(self.date_end, time.max)

        start_utc = fields.Datetime.context_timestamp(self.with_context(tz=user_tz), start_datetime).astimezone(ZoneInfo('UTC'))
        end_utc = fields.Datetime.context_timestamp(self.with_context(tz=user_tz), end_datetime).astimezone(ZoneInfo('UTC'))

        domain = [
            ('date_approve', '>=', start_utc),
            ('date_approve', '<=', end_utc),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'purchase')
        ]
        purchase_orders = self.env['purchase.order'].search(domain, order='create_date asc')

        if not purchase_orders:
            raise UserError('No se encontraron órdenes de compra aprobadas en el rango de fechas especificado.')

        return self.env.ref('ind_purchase_order.report_oc_xlsx').report_action(purchase_orders)
