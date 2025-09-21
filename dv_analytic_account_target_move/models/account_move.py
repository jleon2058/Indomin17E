from odoo.exceptions import UserError
from odoo import models, fields, api,_
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    is_analytic_account_required = fields.Boolean(string='Centro de costo requerido')

    manual_amount_tax = fields.Monetary(
        string="manual amount_tax",
        currency_field="company_currency_id",store=True
    )

    manual_amount_total = fields.Monetary(
        string="manual amount_total",
        currency_field="company_currency_id",store=True
    )

    manual_amount_residual = fields.Monetary(
        string="manual amount_residual",
        currency_field="company_currency_id",store=True
    )

    manual_amount_tax_signed = fields.Monetary(
        string="manual amount_tax_signed",
        currency_field="company_currency_id",store=True
    )

    manual_amount_total_signed = fields.Monetary(
        string="manual amount_total_signed",
        currency_field="company_currency_id",store=True
    )

    manual_amount_residual_signed = fields.Monetary(
        string="manual amount_residual_signed",
        currency_field="company_currency_id",store=True
    )

    manual_amount_total_in_currency_signed = fields.Monetary(
        string="manual amount_residual_signed",
        currency_field="company_currency_id",store=True
    )

    is_post = fields.Boolean(string='confirmado',default=False)


    def _post(self, soft=True):

        self.is_post = True

        #res = super()._post(soft=soft)  # Primero posteamos

        for move in self:
            for line in move.line_ids:
                line.validate_analytic_account()
                _logger.info(line)
                if line.account_target_move_type == 'entry' and (line.debit + line.credit) != 0:
                    debit_target_account_id = line.account_id.debit_target_account_id
                    credit_target_account_id = line.account_id.credit_target_account_id
                    if not debit_target_account_id or not credit_target_account_id:
                        raise UserError(
                            _('Target accounts not found for: %s') % line.account_id.name)
                    line._create_target_move_lines(
                        debit_target_account_id, credit_target_account_id)

                elif (
                    line.account_target_move_type == 'analytic'
                    and line.analytic_distribution
                    and (line.debit + line.credit) != 0
                    and (
                        not line.move_id.stock_move_id          # si no hay stock_move_id
                        or not line.move_id.stock_move_id.group_id  # o si hay, que su group_id sea nulo
                    )
                ):
                    for account_id, proportion in line.analytic_distribution.items():
                        debit_target_account_id = self.env['account.analytic.account'].browse(int(account_id)).debit_target_account_id
                        credit_target_account_id = self.env['account.analytic.account'].browse(int(account_id)).credit_target_account_id
                        if debit_target_account_id and credit_target_account_id:
                            line._create_target_move_lines(
                                debit_target_account_id, credit_target_account_id)
            
        res = super()._post(soft=soft)  # Primero posteamos


        for move in self:
            if move.journal_id.type=='purchase':

                self.env.cr.execute("""
                    UPDATE account_move
                    SET amount_tax = %s, amount_total = %s, amount_residual = %s, amount_tax_signed = %s,
                        amount_total_signed = %s, amount_residual_signed = %s, amount_total_in_currency_signed = %s
                    WHERE id = %s
                """, (move.manual_amount_tax , move.manual_amount_total , move.manual_amount_residual , move.manual_amount_tax_signed , move.manual_amount_total_signed , move.manual_amount_residual_signed , move.manual_amount_total_in_currency_signed ,move.id))

                for line in move.line_ids.filtered(lambda l: not l.is_target_move_line):

                    self.env.cr.execute("""
                        UPDATE account_move_line
                        SET debit = %s, credit = %s, balance = %s, amount_currency = %s
                        WHERE id = %s
                    """, (line.manual_debit,line.manual_credit,line.manual_balance,line.manual_amount_currency,line.id))

        for move in self:
            #lineas_originales = move.line_ids.filtered(lambda l: not l.is_target_move_line and l.account_target_move_type == 'analytic')
            lineas_originales = move.line_ids.filtered(lambda l: not l.is_target_move_line and l.account_target_move_type in ('analytic', 'entry') and l.move_id.move_type == 'in_invoice') 

            if lineas_originales:

                _logger.info(lineas_originales)
                target_lines = move.line_ids.filtered(lambda l: l.is_target_move_line)

                _logger.info(target_lines)
                dest_index = 0  # índice para recorrer las líneas destino

                for original_line in lineas_originales:
                    analytic_distribution = original_line.analytic_distribution or {}
                    analytic_id_str = next(iter(analytic_distribution), None)
                    if not analytic_id_str:
                        continue


                    analytic = self.env['account.analytic.account'].browse(int(analytic_id_str))
                    if original_line.account_target_move_type=='entry':
                        debit_target_account = original_line.account_id.debit_target_account_id 
                        credit_target_account = original_line.account_id.credit_target_account_id
                    elif original_line.account_target_move_type=='analytic':
                        debit_target_account = analytic.debit_target_account_id
                        credit_target_account = analytic.credit_target_account_id

                    # Tomamos 2 líneas desde donde nos quedamos
                    current_target_lines = target_lines[dest_index:dest_index+2]
                    dest_index += 2  # avanzamos para la siguiente vuelta

                    _logger.info(current_target_lines)
                    for line in current_target_lines:
                        if line.price_unit==0:

                            debit = original_line.debit
                            credit = original_line.credit
                            balance = original_line.balance
                            amount_currency = original_line.amount_currency
                            price_unit = amount_currency
                            price_subtotal = original_line.price_subtotal
                            price_total = original_line.price_total

                            if debit > 0:
                                if line.account_id == debit_target_account:

                                    self.env.cr.execute("""
                                        UPDATE account_move_line
                                        SET debit = %s, credit = %s, balance = %s, amount_currency = %s,
                                            price_unit = %s, price_subtotal = %s, price_total = %s
                                        WHERE id = %s
                                    """, (debit, 0.0, balance, amount_currency, price_subtotal, price_subtotal, price_total, line.id))
                                else:

                                    self.env.cr.execute("""
                                        UPDATE account_move_line
                                        SET debit = %s, credit = %s, balance = %s, amount_currency = %s,
                                            price_unit = %s, price_subtotal = %s, price_total = %s
                                        WHERE id = %s
                                    """, (0.0, debit, -balance, -amount_currency, -price_subtotal, -price_subtotal, -price_total, line.id))
                            
                            elif credit > 0:
                                if line.account_id == debit_target_account:

                                    self.env.cr.execute("""
                                        UPDATE account_move_line
                                        SET debit = %s, credit = %s, balance = %s, amount_currency = %s,
                                            price_unit = %s, price_subtotal = %s, price_total = %s
                                        WHERE id = %s
                                    """, (0.0, credit, -balance, -amount_currency, -price_subtotal, -price_subtotal, -price_total, line.id))
                                else:

                                    self.env.cr.execute("""
                                        UPDATE account_move_line
                                        SET debit = %s, credit = %s, balance = %s, amount_currency = %s,
                                            price_unit = %s, price_subtotal = %s, price_total = %s
                                        WHERE id = %s
                                    """, (credit, 0.0, balance, amount_currency, price_subtotal, price_subtotal, price_total, line.id))

        return res
    
    @api.depends(
        'line_ids.display_type',
        'line_ids.balance',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        # si is_target_move_line es campo de línea y puede influir:
        'line_ids.is_target_move_line',
    )
    def _compute_amount(self):

        _logger.info(self.mapped('amount_total'))
        for move in self:
            total_untaxed = total_untaxed_currency = 0.0
            total_tax = total_tax_currency = 0.0
            total_residual = total_residual_currency = 0.0
            total = total_currency = 0.0

            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    is_target = getattr(line, 'is_target_move_line', False)
                    if ( (line.display_type == 'tax' or 
                         (line.display_type == 'rounding' and line.tax_repartition_line_id))
                         and line.is_target_move_line is False ):
                        _logger.info(line.amount_currency)
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding') and line.is_target_move_line is False:
                        _logger.info(line.amount_currency)
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term' and line.is_target_move_line is False:
                        _logger.info(line.amount_residual)
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            sign = move.direction_sign
            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_residual = -sign * total_residual_currency
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = (
                abs(move.amount_total) if move.move_type == 'entry' 
                else -(sign * move.amount_total)
            )

            if move.is_post is not True:
                move.manual_amount_tax=move.amount_tax
                move.manual_amount_total=move.amount_total
                move.manual_amount_residual=move.amount_total
                move.manual_amount_tax_signed=move.amount_tax_signed
                move.manual_amount_total_signed=move.amount_total_signed
                move.manual_amount_residual_signed=move.amount_total_signed
                move.manual_amount_total_in_currency_signed=move.amount_total_in_currency_signed

        for line in self.line_ids:

            if move.is_post is not True:

                line.manual_credit=line.credit
                line.manual_debit=line.debit
                line.manual_balance=line.balance
                line.manual_amount_currency=line.amount_currency


    def button_draft(self):
        super(AccountMove, self).button_draft()
        self.is_post=False
        self.line_ids.filtered(lambda l: l.is_target_move_line).unlink()


