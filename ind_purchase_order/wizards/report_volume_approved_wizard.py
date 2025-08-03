import base64
from datetime import datetime, timedelta, time
from odoo import models, fields, api
from odoo.exceptions import UserError
from ..reports.report_volume_approved_excel import ReportVolumeApprovedExcel
from zoneinfo import ZoneInfo


class ReportVolumeApprovedWizard(models.TransientModel):
    _name = 'report.volume.approved.wizard'
    _description = 'Reporte ordenes de compra aprobadas en un lapso de tiempo'

    @api.model
    def _get_week_start(self):
        today = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return today - timedelta(days=today.weekday())
        

    @api.model
    def _get_week_end(self):
        today = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return today + timedelta(days=(6 - today.weekday()))

    date_start = fields.Date(
        string='Fecha de inicio',
        required=True,
        default=_get_week_start
    )
    date_end = fields.Date(
        string='Fecha de fin',
        required=True,
        default=_get_week_end
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


        purchase_orders = self.env['purchase.order'].search([
            ('state', '=', 'purchase'),
            ('date_approve', '>=', start_utc),
            ('date_approve', '<=', end_utc),
            ('company_id', '=', self.company_id.id)
        ], order='date_approve asc')

        if not purchase_orders:
            raise UserError('No se encontraron órdenes de compra aprobadas en el rango de fechas especificado.')
    
        excel_file = ReportVolumeApprovedExcel(purchase_orders)
        file_data = base64.b64encode(excel_file.get_content())
        self.write({'file_data': file_data})
        date_range = f"{self.date_start.strftime('%d-%m-%Y')}{self.date_end.strftime('%d-%m-%Y')}"
        url = '/web/content/?model=report.volume.approved.wizard&id={}&field=file_data&filename=COMPRAS_APROBADAS_{}&download=true'.format(self.id, date_range)

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }
