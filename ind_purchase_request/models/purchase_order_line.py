from odoo import models, api
import json
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    @api.onchange('company_id') 
    def _onchange_company_id(self):
        # Aplicar un dominio al campo account_analytic_id basado en la compañía seleccionada
        domain = [('company_id', '=', self.company_id.id)]
        return {'domain': {'account_analytic_id': domain}}
            
    @api.model
    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        vals = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        
        # Verificar si super() devolvió un valor antes de intentar actualizar
        if vals:
            for record in self:
                # Extraer el primer valor del diccionario analytic_distribution
                analytic_distribution = record.analytic_distribution
                if analytic_distribution:
                    # Supongamos que analytic_distribution ya es un diccionario
                    first_value = list(analytic_distribution.values())[0] if analytic_distribution else None
                    vals.update({
                        'account_analytic_id': first_value,
                    })

        return vals