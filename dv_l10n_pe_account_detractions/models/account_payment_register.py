# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    detraction_number = fields.Char(string="Nro detracción")
    detraction_date = fields.Date(string="Fecha detracción")
    is_detraction_pay = fields.Boolean(string="Pago detracción?")
    has_detraction_lines = fields.Boolean(string='Existe apuntes de detracción', compute='_compute_has_detraction_lines')

    @api.depends(
        'can_edit_wizard', 'source_amount', 'source_amount_currency',
        'company_id', 'currency_id',
        'payment_date', 'is_detraction_pay'
    )
    def _compute_amount(self):
        for wizard in self:
            if not wizard.journal_id or not wizard.currency_id or not wizard.payment_date:
                wizard.amount = wizard.amount
            batches = wizard._get_batches()
            detraction_batches = [batch for batch in batches if all(line.l10n_pe_is_detraction_line for line in batch['lines'])]
            if detraction_batches and len(batches) == 1:
                self.is_detraction_pay = True
            elif len(batches) == 1:
                self.is_detraction_pay = False
            batch_to_use = wizard._get_batch_to_use_for_amount(batches)
            if batch_to_use:
                amount = wizard._get_total_amount_in_wizard_currency_to_full_reconcile(batch_to_use)[0]
                wizard.amount = amount
            else:
                wizard.amount = None

    @api.depends('amount')
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.payment_date:
                batches = wizard._get_batches()
                batch_to_use = wizard._get_batch_to_use_for_amount(batches)
                if batch_to_use:
                    if not wizard.source_currency_id:
                        payment_values = batch_to_use['payment_values']
                        wizard.source_currency_id = payment_values['currency_id']

                    total_amount_residual_in_wizard_currency = wizard._get_total_amount_in_wizard_currency_to_full_reconcile(batch_to_use)[0]
                    wizard.payment_difference = total_amount_residual_in_wizard_currency - wizard.amount
                else:
                    wizard.payment_difference = 0.0
            else:
                wizard.payment_difference = 0.0

    def _get_batch_to_use_for_amount(self, batches):
        self.ensure_one()
        lines = self.line_ids._origin
        has_detraction_lines = any(line.l10n_pe_is_detraction_line for line in lines)
        if has_detraction_lines and self.is_detraction_pay:
            if len(batches) > 1:
                return batches[1]
        return batches[0] if batches else None

    @api.depends('line_ids.l10n_pe_is_detraction_line')
    def _compute_has_detraction_lines(self):
        for wizard in self:
            lines = wizard.line_ids._origin
            wizard.has_detraction_lines = any(
                line.l10n_pe_is_detraction_line for line in lines
            )
    
    @api.depends('early_payment_discount_mode')
    def _compute_payment_difference_handling(self):
        for wizard in self:
            wizard.payment_difference_handling = 'reconcile' if wizard.early_payment_discount_mode else 'open'

    @api.depends('can_edit_wizard')
    def _compute_group_payment(self):
        for wizard in self:
            batches = wizard._get_batches()
            wizard.group_payment = len(batches[0]['lines'].move_id) == 1