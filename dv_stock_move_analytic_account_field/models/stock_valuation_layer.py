from odoo import fields, models, _


class StockValuationLayer(models.Model):
	_inherit = 'stock.valuation.layer'

	analytic_distribution = fields.Json(
		string='Distribución analítica'
    )
	analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env["decimal.precision"].precision_get(
            "Percentage Analytic"
        ),
    )
