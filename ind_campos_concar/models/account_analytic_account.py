from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.analytic.account'

    concar_id = fields.Char(string='Codigo Concar')
    