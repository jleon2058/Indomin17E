from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # def get_partner_bank_accounts(self):
    #     """Obtener cuentas bancarias del partner para mostrar en reportes"""
    #     # Buscar el partner con ID 10340 o usar el partner de la orden
    #     #partner_id = self.partner_id
    #     # Si quieres forzar el partner 10340, descomenta la siguiente línea:
    #     partner_id = self.env['res.partner'].browse(10340)
        
    #     bank_accounts = self.env['res.partner.bank'].search([
    #         ('partner_id', '=', partner_id.id),
    #         ('allow_out_payment', '=', True)
    #     ])
        
    #     return bank_accounts
    
    def get_company_bank_accounts(self):
        """Obtener cuentas bancarias de la compañía actual"""
        bank_accounts = self.env['res.partner.bank'].search([
            ('partner_id', '=', self.company_id.partner_id.id),
            ('allow_out_payment', '=', True)
        ])
        return bank_accounts