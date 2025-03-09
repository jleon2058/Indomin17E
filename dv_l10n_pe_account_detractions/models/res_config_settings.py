from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    detraction_account_id = fields.Many2one('account.account', string="Cuenta de detracción",
                                            domain=lambda self: [('deprecated', '=', False)],
                                            help="Cuenta que será utilizada para registrar la deuda de detracciones.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    detraction_account_id = fields.Many2one(
        'account.account', string='Cuenta de detracción',
        related='company_id.detraction_account_id', readonly=False,
        domain=lambda self: [('deprecated', '=', False)],
        help="Cuenta que será utilizada para registrar la deuda de detracciones.")
