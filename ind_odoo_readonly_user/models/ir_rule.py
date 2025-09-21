from odoo import api, models
from odoo.osv import expression

class IrRule(models.Model):
    """Inherits the ir rule for restricting the user from accessing data."""
    _inherit = 'ir.rule'

    @api.model
    def _compute_domain(self, model_name, mode):
        # LLAMAR AL MÉTODO BASE CORRECTO - usar super() pero de la clase base de ir.rule
        # Importar la clase base correcta
        from odoo.addons.base.models.ir_rule import IrRule as BaseIrRule
        res = BaseIrRule._compute_domain(self, model_name, mode)
        
        # Verificar primero las condiciones más probables para optimizar
        if (not self.env.user.has_group('odoo_readonly_user.group_users_readonly') or
            mode not in ('write', 'create', 'unlink')):
            return res
        
        # Detectar modelos transitorios dinámicamente
        try:
            model_obj = self.env['ir.model'].sudo().search([('model', '=', model_name)], limit=1)
            es_transient = model_obj and model_obj.transient
        except:
            es_transient = False
        
        # Patrones comunes para identificar wizards
        es_wizard = es_transient or (
            model_name.startswith(('report.', 'wizard.', 'choose.')) or
            model_name.endswith('.wizard') or
            '.wizard.' in model_name or
            'wizard' in model_name.lower() or
            model_name.startswith('ir.')  # Modelos del sistema
        )
        
        # Si es un wizard, permitir todas las operaciones
        if es_wizard:
            return res
        
        # Lista de modelos que tienen permisos especiales de lectura
        readonly_models = ['res.users.log', 'res.users', 'mail.channel',
                           'mail.alias', 'bus.presence', 'res.lang',
                           'mail.channel.member']
        
        # Aplicar restricción si NO está en la lista de excepciones
        if model_name not in readonly_models:
            return expression.AND([res, expression.FALSE_DOMAIN])
        
        return res