from odoo import fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    picking_type_code = fields.Char(string="Picking Type Code")

    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        tracking=True,
    )

    account_move_line_ids = fields.One2many(
                    comodel_name = "account.move.line",
                    inverse_name = "stock_move_id",
                    string = "lineas de asiento",
                    ondelete='cascade'
                    )
