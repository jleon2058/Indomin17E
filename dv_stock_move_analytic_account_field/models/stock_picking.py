from odoo import models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def stock_move_validate_analytic_distribution(self):
        stock_move_ids = self.move_ids_without_package
        if (self.location_id.usage == 'internal' and self.location_dest_id.usage == 'production') and \
            any(not move.analytic_distribution for move in stock_move_ids):
            raise ValidationError("No se ha seleccionado centro de costo para los movimientos")

    def button_validate(self):
        self.stock_move_validate_analytic_distribution()
        res = super(StockPicking, self).button_validate()
        return res
