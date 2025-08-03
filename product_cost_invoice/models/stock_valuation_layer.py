from odoo import models, fields, api

class StockValuationLayerInherited(models.Model):
    _inherit = 'stock.valuation.layer'

    my_custom_create_date = fields.Datetime(string="Fecha de creación almacenada", store=True)
