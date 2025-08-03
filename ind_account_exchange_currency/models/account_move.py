from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    exchange_rate = fields.Float(
        string='Tipo de Cambio',
        digits=0,
        compute='_compute_currency_rate',
        store=True
    )

    @api.depends('currency_id', 'company_id', 'date', 'invoice_date')
    def _compute_currency_rate(self):
        for move in self:
            move.exchange_rate = move._get_actual_currency_rate()

    def _get_actual_currency_rate(self):
        if not self.currency_id:
            return 1.0

        inverse_exchange_rate = self.env['res.currency']._get_conversion_rate(
            from_currency=self.company_currency_id,
            to_currency=self.currency_id,
            company=self.company_id,
            date=self.invoice_date or self.date or fields.Date.context_today(self),
        )
        return 1 / inverse_exchange_rate

    def currency_rate_move_date_domain(self):
        self.ensure_one()
        move_currency_id = self.currency_id.id

        if self.move_type == 'entry' or not self.invoice_date:
            move_date = self.date
        else:
            move_date = self.invoice_date

        domain = [
            ('currency_id', '=', move_currency_id),
            ('name', '=', move_date)
        ]

        return domain

    def validate_currency_date(self):
        for record in self:
            if record.currency_id.id != record.company_id.currency_id.id:
                currency_rate_obj = self.env['res.currency.rate']

                domain = record.currency_rate_move_date_domain()
                currency_rate_move_date = currency_rate_obj.search(domain)

                if not currency_rate_move_date:
                    raise ValidationError(f"No se ha encontrado tipo de cambio a la fecha para el asiento: {record.name}")

    def _post(self, soft=True):
        self.validate_currency_date()
        return super()._post(soft)
