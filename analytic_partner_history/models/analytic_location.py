from odoo import fields, models, api


class LocationMining(models.Model):
    _name = 'analytic.location'
    _description = 'Ubicación analítica'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [
        ('unique_location_code', 'UNIQUE(code)', 'El campo Código debe ser único.'),
    ]

    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True
    )
    code = fields.Char(
        string='Código',
        required=True,
        tracking=True,
        size=3,
    )
    active = fields.Boolean(
        string='¿Activo?',
        default=True,
        tracking=True
    )

    @api.model_create_multi
    def create(self, vals):
        for record in vals:
            if 'name' in record:
                record['name'] = record['name'].upper()
            if 'code' in record:
                record['code']= record['code'].upper()
        return super(LocationMining, self).create(vals)

    def write(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper()
        if 'code' in values:
            values['code'] = values['code'].upper()
        return super(LocationMining, self).write(values)
