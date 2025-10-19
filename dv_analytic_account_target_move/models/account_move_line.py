from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    is_analytic_account_required = fields.Boolean(
        related='account_id.is_analytic_account_required',
        store=True
    )
    account_target_move_type = fields.Selection(
        related='account_id.account_target_move_type',
        store=True
    )
    is_target_move_line = fields.Boolean(
        string='Es linea de destino',
        default=False,
        required=True
    )

    def validate_analytic_account(self):
        for line in self:    
            if line.is_analytic_account_required and not line.analytic_distribution:
                raise UserError(f'La cuenta contable {line.account_id.name} requiere un centro de costo.')

    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        res.validate_analytic_account()
        return res
    
    def _create_target_move_lines(self, debit_target_account_id, credit_target_account_id):
        self.ensure_one()
        line_data = {
            'name': self.name,
            'ref': self.name,
            'partner_id': self.partner_id and self.partner_id.id or False,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'is_target_move_line': True,
            'move_id': self.move_id.id,
        }

        if self.debit > 0:
            debit_data = dict(line_data, account_id=debit_target_account_id.id, debit=self.debit, credit=0.0, amount_currency=self.amount_currency)
            credit_data = dict(line_data, account_id=credit_target_account_id.id, debit=0.0, credit=self.debit, amount_currency=-self.amount_currency if self.amount_currency else 0.0)
        elif self.credit > 0:
            debit_data = dict(line_data, account_id=debit_target_account_id.id, debit=0.0, credit=self.credit, amount_currency=self.amount_currency)
            credit_data = dict(line_data, account_id=credit_target_account_id.id, debit=self.credit, credit=0.0, amount_currency=-self.amount_currency if self.amount_currency else 0.0)
        else:
            # No hay valores, no crear líneas
            return

        logger.info("----------valores------------")
        logger.info("Creating target lines with these values:")
        logger.info(f"Debit data: {debit_data}")
        logger.info(f"Credit data: {credit_data}")

        # Crear las líneas directamente:
        created_lines = self.env['account.move.line'].create([debit_data, credit_data])
        self.env.cr.flush()  # forzar escritura en bd

        for line in created_lines:
            logger.info(f"Created line {line.id}: debit={line.debit} credit={line.credit}")
