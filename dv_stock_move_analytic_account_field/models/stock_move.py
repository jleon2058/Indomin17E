from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_distribution_key = fields.Char(
        compute='_compute_analytic_distribution_key',
        store=True
    )

    def _prepare_common_svl_vals(self):
        """Este método sirve para propagar el valor de la distribución analitica a la capa de valoración"""
        res = super(StockMove, self)._prepare_common_svl_vals()
        res['analytic_distribution'] = self.analytic_distribution if self.analytic_distribution else False
        return res
    
    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields_list = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        fields_list.append('analytic_distribution_key')
        return fields_list

    @api.depends('analytic_distribution')
    def _compute_analytic_distribution_key(self):
         for move in self:
            # Convierte el JSON en string ordenado para evitar errores de orden
            move.analytic_distribution_key = str(sorted(move.analytic_distribution.items())) if move.analytic_distribution else ''
