from odoo import models, fields, api


_LOCATION = [
    ('uchucchacua', 'Uchucchacua'),
    ('tambomayo', 'Tambomayo'),
    ('orcopampa', 'Orcopampa'),
    ('taller', 'Taller'),
    ('yumpag', 'Yumpag')
]


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    location_id = fields.Selection(
        selection=_LOCATION,
        string='Ubicación (Deprecado)',
    )
    ubication_id = fields.Many2one(
        comodel_name='analytic.location',
        string='Ubicación ',
        domain="[('active', '=', True)]",
        tracking=True
    )
    partner_history_count = fields.Integer(
        string='Historial de Ubicaciones',
        compute='_compute_partner_history_count'
    )

    @api.model_create_multi
    def create(self, vals):
        record = super(AccountAnalyticAccount, self).create(vals)
        if 'ubication_id' in vals:
            self.env['account.analytic.account.partner.history'].create({
                'analytic_account_id': record.id,
                # 'location_id': vals['location_id'],
                'ubication_id': vals['ubication_id'],
                'start_datetime': fields.Datetime.now(),
            })
        return record

    @api.depends('ubication_id') # AQUI DEBERIA COLOCAR LUEGO LA UBICATION_ID
    def _compute_partner_history_count(self):
        for record in self:
            record.partner_history_count = self.env['account.analytic.account.partner.history'].search_count([
                ('analytic_account_id', '=', record.id)
            ])

    def write(self, vals):
        for record in self:
            if 'ubication_id' in vals:
                new_ubication_id = vals['ubication_id']
                current_location_id = record.ubication_id or False
                
                if current_location_id != new_ubication_id:
                    # Cerrar el historial activo
                    last_history = self.env['account.analytic.account.partner.history'].search([
                        ('analytic_account_id', '=', record.id),
                        ('end_datetime', '=', False)
                    ], limit=1)
                    if last_history:
                        last_history.end_datetime = fields.Datetime.now()
                    
                    # Crear un nuevo historial
                    self.env['account.analytic.account.partner.history'].create({
                        'analytic_account_id': record.id,
                        # 'location_id': vals['location_id'],
                        'ubication_id': vals['ubication_id'],
                        'start_datetime': fields.Datetime.now(),
                    })
        return super(AccountAnalyticAccount, self).write(vals)

    def action_open_partner_history(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Historial de Ubicaciones',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.account.partner.history',
            'domain': [('analytic_account_id', '=', self.id)],
            'context': {'default_analytic_account_id': self.id},
        }
