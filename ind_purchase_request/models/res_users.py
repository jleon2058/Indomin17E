from odoo import fields, models

class Users(models.Model):
    _inherit = 'res.users'
    
    planning = fields.Boolean(string="Área de Planeamiento", default=False)