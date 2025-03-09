from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class AccountJournalGroup(models.Model):
    _inherit = 'account.journal.group'

    code = fields.Char(string='Code', required=True)
    child_journal_ids = fields.One2many('account.journal', inverse_name='journal_group_id', string="Journals", domain="[('company_id', '=', company_id)]",
                                        check_company=True)

    sequence_id = fields.Many2one('ir.sequence', string='Group sequence',
                                  help="This field contains the information related to the numbering of the"
                                       " journal entries of this journal.",
                                  required=True, copy=False)
    sequence_number_next = fields.Integer(string='Next number',
                                          help='The next sequence number will be used for the next invoice.',
                                          compute='_compute_seq_number_next',
                                          inverse='_inverse_seq_number_next')

    @api.model
    def _create_sequence(self, vals, refund=False):
        prefix = self._get_sequence_prefix(vals['code'], refund)
        date_range = self._get_date_range()
        seq_name = refund and vals['code'] + _(': Refund') or vals['code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'suffix': False,
            'padding': 5,
            'number_increment': 1,
            'use_date_range': True,
            'date_range_ids': date_range,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = vals.get('sequence_number_next', 1)
        return seq

    def _get_date_range(self):
        return [(5, 0, 0), (0, 0, {
                    'date_from': '2021-01-01',
                    'date_to': '2021-01-31',
                }), (0, 0, {
                    'date_from': '2021-02-01',
                    'date_to': '2021-02-28',
                }), (0, 0, {
                    'date_from': '2021-03-01',
                    'date_to': '2021-03-31',
                }), (0, 0, {
                    'date_from': '2021-04-01',
                    'date_to': '2021-04-30',
                }), (0, 0, {
                    'date_from': '2021-05-01',
                    'date_to': '2021-05-31',
                }), (0, 0, {
                    'date_from': '2021-06-01',
                    'date_to': '2021-06-30',
                }), (0, 0, {
                    'date_from': '2021-07-01',
                    'date_to': '2021-07-31',
                }), (0, 0, {
                    'date_from': '2021-08-01',
                    'date_to': '2021-08-31',
                }), (0, 0, {
                    'date_from': '2021-09-01',
                    'date_to': '2021-09-30',
                }), (0, 0, {
                    'date_from': '2021-10-01',
                    'date_to': '2021-10-31',
                }), (0, 0, {
                    'date_from': '2021-11-01',
                    'date_to': '2021-11-30',
                }), (0, 0, {
                    'date_from': '2021-12-01',
                    'date_to': '2021-12-31',
                })]

    def create_sequence(self, refund):
        prefix = self._get_sequence_prefix(self.code, refund)
        date_range = self._get_date_range()
        seq_name = refund and self.code + _(': Refund') or self.code
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'suffix': False,
            'padding': 5,
            'number_increment': 1,
            'use_date_range': True,
            'date_range_ids': date_range,
        }
        _logger.info(seq)
        if self.company_id:
            seq['company_id'] = self.company_id.id
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = self.sequence_number_next or 1
        return seq

    def create_journal_sequence(self):
        if not self.sequence_id:
            seq = self.create_sequence(refund=False)
            self.sequence_id = seq.id

    @api.depends('sequence_id.use_date_range', 'sequence_id.number_next_actual')
    def _compute_seq_number_next(self):
        for journal in self:
            if journal.sequence_id:
                sequence = journal.sequence_id._get_current_sequence()
                journal.sequence_number_next = sequence.number_next_actual
            else:
                journal.sequence_number_next = 1

    def _inverse_seq_number_next(self):
        for journal in self:
            if journal.sequence_id and journal.sequence_number_next:
                sequence = journal.sequence_id._get_current_sequence()
                sequence.sudo().number_next = journal.sequence_number_next

    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code.upper()
        if refund:
            prefix = 'R' + prefix
        return f"%(range_year)s-%(range_month)s-{prefix}-"

    @api.model
    def create(self, vals):
        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        journal = super(AccountJournalGroup, self.with_context(
            mail_create_nolog=True)).create(vals)
        return journal

    def write(self, vals):
        for journal in self:
            if ('code' in vals and journal.code != vals['code']):
                new_prefix = self._get_sequence_prefix(
                    vals['code'], refund=False)
                journal.sequence_id.write({'prefix': new_prefix})
        return super(AccountJournalGroup, self).write(vals)

    def button_open_form(self):
        rec_id = self.id
        form_id = self.env.ref(
            'dv_account_seat_number.account_journal_group_view_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'title',
            'res_model': 'account.journal.group',
            'res_id': rec_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_id.id,
            'context': {},
            # if you want to open the form in edit mode direclty
            'flags': {'initial_mode': 'edit'},
            'target': 'current',
        }
