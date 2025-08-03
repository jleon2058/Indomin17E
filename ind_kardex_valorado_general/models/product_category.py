from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    products_ids=fields.One2many(
        comodel_name='product.template',
        inverse_name='categ_id',
        string='Producto'
    )
