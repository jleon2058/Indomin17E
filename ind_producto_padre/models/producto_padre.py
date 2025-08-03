from odoo import fields, models, api


class ParentProduct(models.Model):
    _name = 'producto.padre'
    _description = 'Parent Product'
    _rec_name = 'product_name'
    _sql_constraints = [('unique_original_product', 'UNIQUE(name)', 'El producto original ya existe.')]

    name = fields.Many2one(
        comodel_name='product.template',
        string='Producto Original',
        required=True,
        index=True,
    )
    product_alternativos = fields.Many2many(
        comodel_name='product.product',
        relation="producto_padre_product_alternativos_rel",
        column1="producto_padre_id",
        column2="product_product_id",
        string='Productos alternativos',
        domain="[('id', '!=', name)]"
    )
    product_name = fields.Char(
        string='Nombre de producto',
        related='name.name'
    )
    product_reference = fields.Char(
        string='Referencia',
        related='name.default_code'
    )
