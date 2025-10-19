from odoo.exceptions import UserError
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    is_analytic_account_required = fields.Boolean(string='Centro de costo requerido')
    
    def _post(self, soft=True):
        for move in self: #.filtered(lambda m: m.move_type not in ['out_invoice', 'out_receipt'])
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
                elif line.account_target_move_type == 'analytic' and line.analytic_distribution and (line.debit + line.credit) != 0:
                    for account_id, proportion in line.analytic_distribution.items():
                        debit_target_account_id = self.env['account.analytic.account'].browse(int(account_id)).debit_target_account_id
                        credit_target_account_id = self.env['account.analytic.account'].browse(int(account_id)).credit_target_account_id
                        if debit_target_account_id and credit_target_account_id:
                            line._create_target_move_lines(
                                debit_target_account_id, credit_target_account_id)
        for line in move.line_ids:
            _logger.info("id: %s | account_id: %s | debit: %s | credit: %s | balance: %s", 
                line.id, line.account_id.id, line.debit, line.credit, line.balance)
        _logger.info("-----ANTES DE IR AL PADRE-----")
        res = super(AccountMove, self)._post(soft=soft)
        return res



    # def _post(self, soft=True):
    #     _logger.info("------DV Analytic Target Move _post START-------")

    #     for move in self:
    #         candidatas = move.line_ids.filtered(lambda l: not l.is_target_move_line and l.account_target_move_type == 'analytic' and (l.debit + l.credit) != 0)
    #         _logger.info(f"Target lines candidates for move {move.id}: {[l.id for l in candidatas]}")

    #         for line in candidatas:
    #             _logger.info("------for_target------")
    #             debit_target_account_id = line.account_id.debit_target_account_id
    #             credit_target_account_id = line.account_id.credit_target_account_id
    #             if debit_target_account_id and credit_target_account_id:
    #                 _logger.info("------if target------")
    #                 debit_exists = move.line_ids.filtered(lambda l: l.is_target_move_line and l.account_id == debit_target_account_id)
    #                 credit_exists = move.line_ids.filtered(lambda l: l.is_target_move_line and l.account_id == credit_target_account_id)

    #                 if not (debit_exists and credit_exists):
    #                     _logger.info("------exite------")
    #                     _logger.info(f"Creating target lines for line {line.id} in move {move.id}")
    #                     line._create_target_move_lines(debit_target_account_id, credit_target_account_id)
    #                 else:
    #                     _logger.info(f"Target lines already exist for line {line.id} in move {move.id}")

    #     _logger.info("-----antes-----")                
    #     for line in move.line_ids:
    #         _logger.info("id: %s | account_id: %s | debit: %s | credit: %s | balance: %s", 
    #             line.id, line.account_id.id, line.debit, line.credit, line.balance)
    #     _logger.info("-----ANTES DE IR AL PADRE-----")
    #     res = super(AccountMove, self)._post(soft=soft)

    #     # Opcional: examinar líneas después
    #     _logger.info("-------despues de res--------")
    #     for move in self:
    #         for line in move.line_ids.filtered(lambda l: l.is_target_move_line):
    #             _logger.info(f"Post _post check line: id={line.id} debit={line.debit} credit={line.credit}")

    #     return res




    def button_draft(self):
        super(AccountMove, self).button_draft()
        self.line_ids.filtered(lambda l: l.is_target_move_line).unlink()




