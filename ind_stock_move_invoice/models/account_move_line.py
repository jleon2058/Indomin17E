from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    stock_move_id = fields.Many2one("stock.move","Id movimiento",ondelete='cascade')

    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        tracking=True,
    )