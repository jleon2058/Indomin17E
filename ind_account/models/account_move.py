from odoo import models,fields,api,_
from itertools import chain
from odoo.tools import groupby
from collections import defaultdict
from odoo.exceptions import UserError
from lxml import etree
import logging
logger = logging.getLogger(__name__)

class AccountMoveCustom(models.Model):
    _inherit = "account.move"

    hide_button_draft = fields.Boolean(compute='_compute_hide_button_draft')

    @api.depends("state")
    def _compute_hide_button_draft(self):
        for record in self:
            record.hide_button_draft = record.state == "draft"

    def button_draft(self):
        """Sobreescribe el método para eliminar registros de stock_valuation_layer y cancelar asientos contables"""
        stock_valuation_layer = self.env["stock.valuation.layer"]
        account_move = self.env["account.move"]

        for move in self:
            # Buscar los stock valuation layers asociados a las líneas de la factura
            valuation_layers = stock_valuation_layer.search([
                ('account_move_line_id', 'in', move.line_ids.ids)
            ])
            logger.warning("-----------svl-----------")
            logger.warning(valuation_layers)

            # Obtener los asientos contables asociados
            account_moves = account_move.search([
                ('id', 'in', valuation_layers.mapped('account_move_id').ids)
            ])

            logger.warning("--------am----------")
            logger.warning(account_moves)

            # Cancelar los asientos contables
            for account_move in account_moves:
                if account_move.state != 'cancel':  # Evita volver a cancelar si ya está cancelado
                    account_move.button_cancel()

            # Eliminar los registros de stock_valuation_layer
            valuation_layers.sudo().unlink()

            # Verificar si la factura está vinculada a un stock.picking
            stock_moves=self.invoice_line_ids.mapped('stock_move_id')
            logger.warning("------movimientoss-------")
            logger.warning(stock_moves)
            if stock_moves:
                logger.warning("--------am----------")
                for sm in stock_moves:
                    sm.calcular_monto_asigned()

        # Llamar al método original para continuar con el flujo de Odoo
        return super().button_draft()
    
    def action_post(self):
        logger.warning("-------action_post---------")
        moves_with_payments = self.filtered('payment_id')
        other_moves = self - moves_with_payments
        if moves_with_payments:
            moves_with_payments.with_context(skip_product_cost_invoice=True).payment_id.action_post()

        if other_moves:
            other_moves.with_context(skip_product_cost_invoice=True)._post(soft=False)

        logger.warning("------contexto-------")
        logger.warning(f"Contexto en ind_account: {self.env.context}")
        # Modificar create_date de stock valuation layers después de confirmar la factura
        stock_valuation_layer = self.env["stock.valuation.layer"]
        for move in self:
            valuation_layers = stock_valuation_layer.search([
                ('account_move_line_id', 'in', move.line_ids.ids)
            ])
            logger.warning("-----------svl a modificar-----------")
            logger.warning(valuation_layers)

            for svl in valuation_layers:
                if svl.stock_valuation_layer_id:
                    logger.warning("----------fecha----------")
                    logger.warning(svl.stock_valuation_layer_id.stock_move_id.date)
                    #svl.create_date = svl.stock_valuation_layer_id.stock_move_id.date
                    #svl.sudo().write({'create_date': svl.stock_valuation_layer_id.stock_move_id.date})
                    self.env.cr.execute("""
                        UPDATE stock_valuation_layer 
                        SET create_date = %s 
                        WHERE id = %s
                    """, (svl.stock_valuation_layer_id.stock_move_id.date, svl.id))
                    self.env.cr.commit()
                    logger.warning(f"Actualizando create_date de SVL {svl.id} a {svl.create_date}")

        return False
    
    def action_reverse(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_view_account_move_reversal")

        if self.is_invoice():
            action['name'] = _('Credit Note')
        return action
    
    def action_update_exchange_rate_nc(self):
        """ Método ejecutado al presionar el botón en la vista """
        
        for move in self:

            if move.reversed_entry_id:

                exchange_rate_nc = move.reversed_entry_id.exchange_rate
                self.exchange_rate=exchange_rate_nc
            
            for line in move.line_ids:
                if line.amount_currency:

                    if line.debit > 0:
                        new_debit = abs(float(line.amount_currency)) * float(self.exchange_rate)
                        new_credit = 0
                    else:
                        new_credit = abs(float(line.amount_currency)) * float(self.exchange_rate)
                        new_debit = 0

                    new_balance = new_debit - new_credit

                    # Ejecutar la actualización con SQL
                    self.env.cr.execute("""
                        UPDATE account_move_line 
                        SET debit = %s, credit = %s, balance = %s 
                        WHERE id = %s
                    """, (new_debit, new_credit, new_balance, line.id))

                    logger.info(f"Updated line {line.id}: debit={new_debit}, credit={new_credit}, balance={new_balance}")

        # Confirmar y limpiar caché
        self.env.cr.commit()
        #self.env.registry.clear_caches()
        return True