from odoo import api, fields, models, _
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_date_currency_rate = fields.Char(
        string='Tipo de cambio', compute='_compute_invoice_date_currency_rate')

    def _compute_invoice_date_currency_rate(self):
        for record in self:
            currency_rate = self.env['res.currency.rate'].search(
                [('currency_id', '=', record.currency_id.id),
                 ('name', '=', record.invoice_date)], limit=1)
            rate = round(1.0 / currency_rate.rate,
                         3) if currency_rate.rate else 1.0
            rate_char = format(rate, ".3f")
            record.invoice_date_currency_rate = rate_char