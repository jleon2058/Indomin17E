from odoo.exceptions import UserError
from odoo import models, fields, api,_
from odoo.tools import float_compare
from odoo.tools import formatLang
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    is_analytic_account_required = fields.Boolean(string='Centro de costo requerido')

    invoice_line_ids = fields.One2many(
        'account.move.line',
        'move_id',
        string='Invoice lines',
        copy=False,
        domain=[('display_type', 'in', ('product', 'line_section', 'line_note')),('is_target_move_line', '=', False)],
    )

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

    def has_target_move_lines(self):
        return any(line.is_target_move_line for line in self.line_ids)             

    def _post(self, soft=True):

        self.is_post = True

        #res = super()._post(soft=soft)  # Primero posteamos

        for move in self:
            if move.has_target_move_lines():
                continue
            for line in move.line_ids:
                line.validate_analytic_account()
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
            
        
        for move in self:
            if move.manual_amount_tax>0: 
                move.amount_tax = move.manual_amount_tax 
                # Actualizar IGV dentro del JSON tax_totals 
                tax_totals = move.tax_totals 
                if tax_totals and 'groups_by_subtotal' in tax_totals: 
                    for subtotal, groups in tax_totals['groups_by_subtotal'].items(): 
                        for group in groups: 
                            if group.get('tax_group_name') == 'IGV': 
                                group['tax_group_amount'] = move.manual_amount_tax 
                                group['formatted_tax_group_amount'] = formatLang( self.env, move.manual_amount_tax, currency_obj=move.currency_id, ) 
                    # Recalcular amount_total con el nuevo IGV
                    untaxed = tax_totals.get('amount_untaxed', 0.0)
                    total = untaxed + move.manual_amount_tax
                    tax_totals['amount_total'] = total
                    tax_totals['formatted_amount_total'] = formatLang( self.env, total, currency_obj=move.currency_id, )
                    move.tax_totals = tax_totals# Reasignamos el diccionario actualizado

        res = super()._post(soft=soft)  # Primero posteamos

        for move in self:
            lineas_originales = move.line_ids.filtered(lambda l: not l.is_target_move_line and l.account_target_move_type in ('analytic', 'entry')) 

            if lineas_originales:

                target_lines = move.line_ids.filtered(lambda l: l.is_target_move_line)

                dest_index = 0

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

                    for line in current_target_lines:
                        _logger.info(line)
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

    def button_draft(self):
        super(AccountMove, self).button_draft()
        self.is_post=False
        self.line_ids.filtered(lambda l: l.is_target_move_line).unlink()

    @api.depends('line_ids.balance')
    def _compute_depreciation_value(self):
        
        for move in self:
            asset = move.asset_id or move.reversed_entry_id.asset_id
            if asset:
                # Excluir las líneas de destino del cálculo
                depreciation_lines = move._get_asset_depreciation_line().filtered(lambda l: not l.is_target_move_line)
                asset_depreciation = sum(depreciation_lines.mapped('balance'))
                
                # Tu código existente para el caso de closing entry...
                if any(
                    line.account_id == asset.account_asset_id
                    and float_compare(-line.balance, asset.original_value, precision_rounding=asset.currency_id.rounding) == 0
                    for line in move.line_ids
                ) and len(move.line_ids) > 2:
                    asset_depreciation = (
                        asset.original_value
                        - asset.salvage_value
                        - (
                            move.line_ids.filtered(lambda l: not l.is_target_move_line)[1].debit 
                            if asset.original_value > 0 else 
                            move.line_ids.filtered(lambda l: not l.is_target_move_line)[1].credit
                        ) * (-1 if asset.original_value < 0 else 1)
                    )
            else:
                asset_depreciation = 0
            move.depreciation_value = asset_depreciation