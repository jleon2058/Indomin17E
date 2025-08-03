import base64

from odoo import models, fields
from odoo.exceptions import UserError

from ..reports.report_consumption import ReportConsumptionXlsx


class ConsumptionAnalysisWizard(models.TransientModel):
    _name = 'consumption.analysis.wizard'
    _description = 'Wizard para reporte de consumos'

    date_start = fields.Date(
        string='Fecha de inicio',
        required=True
    )
    date_end = fields.Date(
        string='Fecha de fin',
        required=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    file_data = fields.Binary(string='Archivo Excel', readonly=True)

    def action_generate_report(self):
        moves = self.env['stock.move'].sudo().search([
            '|',
            '&',
            ('location_id.usage', '=', 'internal'),
            ('location_dest_id.usage', '=', 'production'),
            '&',
            ('location_id.usage', '=', 'production'),
            ('location_dest_id.usage', '=', 'internal'),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'done')
        ])

        if not moves:
            raise UserError('No se encontraron movimientos en el rango de fechas especificado.')

        records = moves.with_context(active_test=False)
        excel_file = ReportConsumptionXlsx(records, self.env)
        file_data = base64.b64encode(excel_file.get_content())
        self.write({'file_data': file_data})
        date_range = f"{self.date_start.strftime('%d-%m-%Y')}{self.date_end.strftime('%d-%m-%Y')}"
        url = '/web/content/?model=consumption.analysis.wizard&id={}&field=file_data&filename=COMPRAS_APROBADAS_{}&download=true'.format(self.id, date_range)

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }
