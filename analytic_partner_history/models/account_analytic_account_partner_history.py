from odoo import models, fields, api

_LOCATION = [
    ('uchucchacua', 'Uchucchacua'),
    ('tambomayo', 'Tambomayo'),
    ('orcopampa', 'Orcopampa'),
    ('taller', 'Taller'),
    ('yumpag', 'Yumpag')
]


class AnalyticAccountPartnerHistory(models.Model):
    _name = 'account.analytic.account.partner.history'
    _description = 'Historial de ubicaciones asignadas a centros de costo'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Centro de Costo',
        required=True,
        ondelete='cascade'
    )
    location_id = fields.Selection( # DELETE IN FUTURE VERSIONS
        selection=_LOCATION,
        string='Ubicación (Deprecado)',
    )
    ubication_id = fields.Many2one(
        string='Ubicación',
        comodel_name='analytic.location'
    )
    start_datetime = fields.Datetime(
        string='Inicio de Asignación',
        required=True,
        default=fields.Datetime.now
    )
    end_datetime = fields.Datetime(string='Fin de Asignación')
