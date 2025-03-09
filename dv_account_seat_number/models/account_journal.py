from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    journal_group_id = fields.Many2one(
        'account.journal.group', string="Journal's Group")
